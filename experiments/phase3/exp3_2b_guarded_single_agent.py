"""
实验 3.2b：最小单 Agent（Guarded Loop）

在既有 ReAct / Skills Agent 基础上，补齐阶段 2 需要的三个能力：
1. 任务契约：明确输入、可用能力、输出格式、完成条件
2. 结果校验：对最终答案做结构化校验
3. 失败修复：校验失败后，把反馈回送给模型进行一次或多次修复

设计目标：
- 保持单 Agent，不引入 LangGraph
- 继续沿用 Skill + load_skill + bash 的组合
- 让“扫描 -> 分析 -> 报告”具备最小的工程闭环
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import ollama
from dotenv import load_dotenv
from openai import OpenAI

from exp3_7_skill_loader import SkillLoader
from exp3_7b_skills_agent import bash_tool, load_skill_tool, safe_print

load_dotenv()


@dataclass
class TaskContract:
    """单 Agent 的任务契约。"""

    name: str
    goal: str
    allowed_tools: List[str]
    allowed_skills: List[str]
    required_fields: List[str]
    risk_levels: List[str] = field(default_factory=lambda: ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
    max_iterations: int = 8
    max_repairs: int = 2

    def render(self) -> str:
        required = "\n".join(f"- {field}" for field in self.required_fields)
        tools = "\n".join(f"- {tool}" for tool in self.allowed_tools)
        skills = "\n".join(f"- {skill}" for skill in self.allowed_skills)
        risks = ", ".join(self.risk_levels)
        return f"""## Task Contract

Name: {self.name}
Goal: {self.goal}

Allowed Tools:
{tools}

Allowed Skills:
{skills}

Output Rules:
- Final Answer must be valid JSON
- JSON must include these fields:
{required}
- risk_level must be one of: {risks}
- evidence must be a non-empty list
- recommendations must be a non-empty list
"""


class FinalAnswerValidator:
    """对最终答案做最小但明确的结构化校验。"""

    def __init__(self, contract: TaskContract):
        self.contract = contract

    def validate(self, final_answer: str) -> tuple[bool, str, Optional[Dict[str, Any]]]:
        try:
            data = json.loads(final_answer)
        except json.JSONDecodeError as exc:
            return False, f"Final Answer is not valid JSON: {exc}", None

        missing = [field for field in self.contract.required_fields if field not in data]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}", None

        risk_level = data.get("risk_level")
        if risk_level not in self.contract.risk_levels:
            return False, f"risk_level must be one of: {', '.join(self.contract.risk_levels)}", None

        evidence = data.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            return False, "evidence must be a non-empty list", None

        recommendations = data.get("recommendations")
        if not isinstance(recommendations, list) or not recommendations:
            return False, "recommendations must be a non-empty list", None

        return True, "ok", data


class GuardedSingleAgent:
    """
    阶段 2 的最小单 Agent。

    两种运行模式：
    - ollama: 文本 ReAct + 正则解析 + history 回填
    - openai: function calling + messages 回填
    """

    def __init__(
        self,
        contract: TaskContract,
        model: str,
        backend: str = "openai",
    ):
        self.contract = contract
        self.model = model
        self.backend = backend
        self.skill_loader = SkillLoader()
        self.validator = FinalAnswerValidator(contract)

        self.tools: Dict[str, Callable[..., str]] = {
            "load_skill": self._guarded_load_skill,
            "bash": bash_tool,
        }

        if backend == "openai":
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),
            )
        else:
            self.client = ollama.Client(
                host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            )

    def _guarded_load_skill(self, skill_name: str) -> str:
        if skill_name not in self.contract.allowed_skills:
            return (
                f"Skill '{skill_name}' is not allowed by the current task contract. "
                f"Allowed skills: {', '.join(self.contract.allowed_skills)}"
            )
        return load_skill_tool(skill_name, self.skill_loader)

    def _tool_descriptions(self) -> str:
        return """- load_skill: Load a skill's detailed instructions. Parameters: skill_name (str)
- bash: Execute shell commands. Parameters: command (str), cwd (str, optional)"""

    def _create_system_prompt(self) -> str:
        base_prompt = f"""You are a single security analysis agent.

You must obey the task contract below.
Use tools only when they are necessary.
Do not invent tools, skills, or file paths.

{self.contract.render()}

When a user request matches an allowed skill:
1. Call load_skill(skill_name)
2. Follow the skill instructions
3. Use bash to execute scripts

Always prefer precise, verifiable output."""
        return self.skill_loader.build_system_prompt(base_prompt)

    def _create_react_prompt(self, task: str, history: str) -> str:
        return f"""{self._create_system_prompt()}

Available Tools:
{self._tool_descriptions()}

You must follow this exact format:
Thought: [your reasoning]
Action: [tool_name]
Action Input: [JSON parameters]

Or when finished:
Thought: [final reasoning]
Final Answer: [strict JSON only]

{history}
Task: {task}
Begin:"""

    def _parse_react_response(self, response: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "thought": "",
            "action": None,
            "action_input": None,
            "final_answer": None,
        }

        thought_match = re.search(
            r"(?:Thought|思考)[:：]\s*(.+?)(?=(?:Action|行动|Final Answer|最终答案|$))",
            response,
            re.DOTALL | re.IGNORECASE,
        )
        if thought_match:
            result["thought"] = thought_match.group(1).strip()

        final_match = re.search(
            r"(?:Final Answer|最终答案)[:：]\s*(.+)",
            response,
            re.DOTALL | re.IGNORECASE,
        )
        if final_match:
            result["final_answer"] = final_match.group(1).strip()
            return result

        action_match = re.search(r"(?:Action|行动)[:：]\s*(\w+)", response, re.IGNORECASE)
        if action_match:
            result["action"] = action_match.group(1)

        input_match = re.search(
            r"(?:Action Input|行动输入|输入)[:：]\s*(\{.+?\})",
            response,
            re.DOTALL | re.IGNORECASE,
        )
        if input_match:
            try:
                result["action_input"] = json.loads(input_match.group(1))
            except json.JSONDecodeError:
                result["action_input"] = None

        return result

    def _openai_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "load_skill",
                    "description": "Load an allowed skill's detailed instructions",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "skill_name": {
                                "type": "string",
                                "description": "Name of the skill to load",
                            }
                        },
                        "required": ["skill_name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "bash",
                    "description": "Execute shell commands to run scripts",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Shell command to execute",
                            },
                            "cwd": {
                                "type": "string",
                                "description": "Working directory",
                                "default": ".",
                            },
                        },
                        "required": ["command"],
                    },
                },
            },
        ]

    def _build_validation_feedback(self, reason: str) -> str:
        return (
            "Your previous Final Answer did not satisfy the task contract. "
            f"Validation error: {reason}. "
            "Return a corrected Final Answer as strict JSON only."
        )

    def run(self, task: str) -> Dict[str, Any]:
        if self.backend == "openai":
            return self._run_openai(task)
        return self._run_ollama(task)

    def _run_ollama(self, task: str) -> Dict[str, Any]:
        history = ""
        repairs = 0

        for index in range(self.contract.max_iterations):
            safe_print(f"\n--- Iteration {index + 1} ---")
            prompt = self._create_react_prompt(task, history)
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            response_text = response["message"]["content"]
            parsed = self._parse_react_response(response_text)

            safe_print(f"Thought: {parsed['thought'][:120] if parsed['thought'] else '(empty)'}")

            if parsed["final_answer"]:
                valid, reason, data = self.validator.validate(parsed["final_answer"])
                if valid:
                    return {
                        "status": "completed",
                        "backend": self.backend,
                        "iterations": index + 1,
                        "final_answer": data,
                    }

                repairs += 1
                safe_print(f"[Validator] {reason}")
                if repairs > self.contract.max_repairs:
                    return {
                        "status": "failed_validation",
                        "backend": self.backend,
                        "iterations": index + 1,
                        "error": reason,
                        "raw_final_answer": parsed["final_answer"],
                    }

                history += (
                    f"\nThought: {parsed['thought']}\n"
                    f"Observation: Validation failed. {self._build_validation_feedback(reason)}\n"
                )
                continue

            action = parsed["action"]
            action_input = parsed["action_input"]
            if action and action in self.tools and action_input:
                safe_print(f"Action: {action}")
                safe_print(f"Action Input: {action_input}")
                try:
                    result = self.tools[action](**action_input)
                except Exception as exc:  # pragma: no cover - defensive guard
                    result = f"Error: {exc}"

                safe_print(f"Observation: {result[:200]}")
                history += (
                    f"\nThought: {parsed['thought']}\n"
                    f"Action: {action}\n"
                    f"Action Input: {json.dumps(action_input, ensure_ascii=False)}\n"
                    f"Observation: {result}\n"
                )
                continue

            history += (
                f"\nThought: {parsed['thought']}\n"
                "Observation: Invalid or missing action. Either use an allowed tool or return Final Answer as JSON.\n"
            )

        return {
            "status": "max_iterations_exceeded",
            "backend": self.backend,
            "iterations": self.contract.max_iterations,
        }

    def _run_openai(self, task: str) -> Dict[str, Any]:
        repairs = 0
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self._create_system_prompt()},
            {"role": "user", "content": task},
        ]

        for index in range(self.contract.max_iterations):
            safe_print(f"\n--- Iteration {index + 1} ---")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._openai_tools(),
                tool_choice="auto",
            )
            message = response.choices[0].message

            if getattr(message, "tool_calls", None):
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    safe_print(f"Function Call: {function_name}({function_args})")

                    if function_name not in self.tools:
                        return {
                            "status": "tool_error",
                            "backend": self.backend,
                            "iterations": index + 1,
                            "error": f"Unknown function: {function_name}",
                        }

                    try:
                        result = self.tools[function_name](**function_args)
                    except Exception as exc:  # pragma: no cover - defensive guard
                        result = f"Error: {exc}"

                    safe_print(f"Result: {str(result)[:200]}")
                    messages.append(
                        {
                            "role": "assistant",
                            "content": message.content or "",
                            "tool_calls": [
                                {
                                    "id": tool_call.id,
                                    "type": "function",
                                    "function": {
                                        "name": function_name,
                                        "arguments": tool_call.function.arguments,
                                    },
                                }
                            ],
                        }
                    )
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(result),
                        }
                    )
                continue

            final_answer = message.content or ""
            valid, reason, data = self.validator.validate(final_answer)
            if valid:
                return {
                    "status": "completed",
                    "backend": self.backend,
                    "iterations": index + 1,
                    "final_answer": data,
                }

            repairs += 1
            safe_print(f"[Validator] {reason}")
            if repairs > self.contract.max_repairs:
                return {
                    "status": "failed_validation",
                    "backend": self.backend,
                    "iterations": index + 1,
                    "error": reason,
                    "raw_final_answer": final_answer,
                }

            messages.append({"role": "assistant", "content": final_answer})
            messages.append({"role": "user", "content": self._build_validation_feedback(reason)})

        return {
            "status": "max_iterations_exceeded",
            "backend": self.backend,
            "iterations": self.contract.max_iterations,
        }


def default_contract() -> TaskContract:
    return TaskContract(
        name="security-audit-single-agent",
        goal="Use the security-audit skill to inspect a local target and return a structured report.",
        allowed_tools=["load_skill", "bash"],
        allowed_skills=["security-audit"],
        required_fields=[
            "target",
            "summary",
            "risk_level",
            "evidence",
            "recommendations",
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="阶段 2：最小 Guarded Single Agent")
    parser.add_argument(
        "--backend",
        choices=["openai", "ollama"],
        default="openai",
        help="选择模型后端",
    )
    parser.add_argument(
        "--task",
        default=(
            "使用 security-audit skill 审计 "
            ".claude/skills/security-audit/scripts/test_vulnerable.c，"
            "并输出符合任务契约的最终 JSON 报告。"
        ),
        help="要执行的任务",
    )
    parser.add_argument(
        "--show-contract",
        action="store_true",
        help="仅显示任务契约，不执行 agent",
    )
    args = parser.parse_args()

    contract = default_contract()

    if args.show_contract:
        safe_print(contract.render())
        return

    if args.backend == "openai":
        model = os.getenv("OPENAI_MODEL", "deepseek-v4-pro")
    else:
        model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

    safe_print("=" * 60)
    safe_print("实验 3.2b：最小 Guarded Single Agent")
    safe_print("=" * 60)
    safe_print(f"Backend: {args.backend}")
    safe_print(f"Model: {model}")
    safe_print(f"Task: {args.task}\n")

    agent = GuardedSingleAgent(
        contract=contract,
        model=model,
        backend=args.backend,
    )
    result = agent.run(args.task)
    safe_print("\n=== Result ===")
    safe_print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
