"""
实验 3.7b：支持 Skills 的 ReAct Agent（双模式）
集成 SkillLoader 到既有 ReAct Agent，支持 Ollama/API 切换

学习目标：
1. 理解如何在 Agent 中集成 SkillLoader
2. 掌握 load_skill 和 bash 工具的实现
3. 学会双模式（Ollama + OpenAI API）切换

架构：
- SkillsAgent: 支持 Skills 的 ReAct Agent
- load_skill_tool: Level 2 加载 - 按需加载 Skill 指令
- bash_tool: Level 3 执行 - 运行脚本，代码不进入上下文
"""

import os
import json
import re
import subprocess
import sys
from typing import Dict, Callable, Optional
from dotenv import load_dotenv
from pathlib import Path

# 导入实验 3.7 的 SkillLoader
from exp3_7_skill_loader import SkillLoader, SkillContent

# 支持双模式
import ollama
from openai import OpenAI

# 加载项目根目录的 .env 文件
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


def safe_print(text: str, **kwargs):
    """安全打印，处理编码问题"""
    try:
        print(text, **kwargs)
    except UnicodeEncodeError:
        # 使用 sys.stdout.buffer 直接写入 UTF-8 字节
        encoded = text.encode('utf-8', errors='ignore')
        sys.stdout.buffer.write(encoded)
        if kwargs.get('end') != '':
            sys.stdout.buffer.write(b'\n')
        sys.stdout.buffer.flush()


# ==================== Level 3: 工具实现 ====================


def load_skill_tool(skill_name: str, skill_loader: SkillLoader) -> str:
    """
    工具：加载 Skill 详细指令（Level 2）

    当用户请求匹配某个 skill 的 description 时调用。
    这是三层加载机制的第二层。

    Args:
        skill_name: Skill 名称
        skill_loader: SkillLoader 实例

    Returns:
        Skill 的完整指令，包含路径信息
    """
    skill_content = skill_loader.load_skill(skill_name)

    if not skill_content:
        skills = skill_loader.scan_skills()
        available = [s.name for s in skills]
        return f"Skill '{skill_name}' not found. Available skills: {', '.join(available)}"

    # 获取 skill 路径信息
    skill_path = skill_content.metadata.skill_path
    scripts_dir = skill_path / "scripts"

    # 构建路径信息
    path_info = f"""
## Skill Path Info

- **Skill Directory**: `{skill_path}`
- **Scripts Directory**: `{scripts_dir}`

**Important**: When running scripts, use absolute paths like:
```bash
python {scripts_dir}/script_name.py [args]
```
"""

    # 返回 instructions 和路径信息
    return f"""# Skill: {skill_name}

## Instructions

{skill_content.instructions}
{path_info}
"""


def bash_tool(command: str, cwd: str = ".") -> str:
    """
    工具：执行 shell 命令（Level 3）

    重要设计：脚本代码不进入上下文，只有输出进入。
    这是三层加载机制的第三层。

    Args:
        command: 要执行的 shell 命令
        cwd: 工作目录

    Returns:
        格式化的输出，带 [OK] 或 [FAILED] 前缀
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 分钟超时
        )

        parts = []

        # 状态标记
        if result.returncode == 0:
            parts.append("[OK]")
        else:
            parts.append(f"[FAILED] Exit code: {result.returncode}")

        parts.append("")  # 空行分隔

        if result.stdout:
            parts.append(result.stdout.rstrip())

        if result.stderr:
            if result.stdout:
                parts.append("")
            parts.append("--- stderr ---")
            parts.append(result.stderr.rstrip())

        if not result.stdout and not result.stderr:
            parts.append("(no output)")

        return "\n".join(parts)

    except subprocess.TimeoutExpired:
        return "[FAILED] Command timed out after 300 seconds."
    except Exception as e:
        return f"[FAILED] {str(e)}"


# ==================== Skills Agent ====================


class SkillsAgent:
    """
    支持 Skills 的 ReAct Agent

    与既有 exp3_2_react_agent.py 的主要区别：
    1. 集成 SkillLoader 在 system prompt 中注入可用 Skills
    2. 增加 load_skill 工具供模型按需加载 Skill 指令
    3. bash 工具执行 Skill 脚本（Level 3）

    支持双模式：
    - Ollama: 本地模型，使用 ollama Python SDK
    - OpenAI: 远程 API，使用 openai Python SDK
    """

    def __init__(
        self,
        model: str = "qwen2.5:7b",
        max_iterations: int = 10,
        backend: str = "ollama"
    ):
        """
        初始化 Skills Agent

        Args:
            model: 模型名称
            max_iterations: 最大迭代次数
            backend: 后端类型，"ollama" 或 "openai"
        """
        self.model = model
        self.max_iterations = max_iterations
        self.backend = backend

        # Skills 支持
        self.skill_loader = SkillLoader()

        # 工具注册
        self.tools: Dict[str, Callable] = {
            "load_skill": self._wrap_load_skill,
            "bash": bash_tool,
        }
        self.tool_descriptions = self._build_tool_descriptions()

        # 根据后端初始化客户端
        if backend == "openai":
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),
            )
        else:
            self.client = ollama.Client(
                host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            )

    def _wrap_load_skill(self, skill_name: str) -> str:
        """包装 load_skill_tool，注入 skill_loader"""
        return load_skill_tool(skill_name, self.skill_loader)

    def _build_tool_descriptions(self) -> str:
        """构建工具描述"""
        return """- load_skill: Load a skill's detailed instructions. Parameters: skill_name (str)
- bash: Execute shell commands. Parameters: command (str), cwd (str, optional)"""

    def _create_system_prompt(self) -> str:
        """创建包含 Skills 列表的 system prompt"""
        base_prompt = """You are a helpful assistant with access to specialized skills.

When a user request matches a skill's description:
1. Call `load_skill(skill_name)` to get detailed instructions
2. Follow the instructions carefully
3. Use `bash` tool to run scripts when needed

Always think step by step."""

        return self.skill_loader.build_system_prompt(base_prompt)

    def _create_react_prompt(self, task: str, history: str = "") -> str:
        """创建 ReAct 格式提示词"""
        system_prompt = self._create_system_prompt()

        return f"""{system_prompt}

Available Tools:
{self.tool_descriptions}

You must follow this exact format (use English keywords):
Thought: [your reasoning about what to do]
Action: [tool_name]
Action Input: [JSON parameters]

Or when finished:
Thought: [final reasoning]
Final Answer: [your answer to the user]

{history}
Task: {task}
Begin:"""

    def _parse_response(self, response: str) -> dict:
        """解析 ReAct 格式响应（支持中英文）"""
        result = {
            "thought": "",
            "action": None,
            "action_input": None,
            "final_answer": None
        }

        # 支持中英文格式
        # Thought / 思考 / Thought:
        thought_patterns = [
            r"(?:Thought|思考)[:：]\s*(.+?)(?=(?:Action|行动|Final Answer|最终答案|$))",
        ]

        for pattern in thought_patterns:
            thought_match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if thought_match:
                result["thought"] = thought_match.group(1).strip()
                break

        # Final Answer / 最终答案
        final_patterns = [
            r"(?:Final Answer|最终答案)[:：]\s*(.+)",
        ]

        for pattern in final_patterns:
            final_match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if final_match:
                result["final_answer"] = final_match.group(1).strip()
                return result

        # Action / 行动
        action_patterns = [
            r"(?:Action|行动)[:：]\s*(\w+)",
        ]

        for pattern in action_patterns:
            action_match = re.search(pattern, response, re.IGNORECASE)
            if action_match:
                result["action"] = action_match.group(1)
                break

        # Action Input / 行动输入 / 输入
        input_patterns = [
            r"(?:Action Input|行动输入|输入)[:：]\s*(\{.+?\})",
            r"(?:Action Input|行动输入|输入)[:：]\s*(.+?)(?=\n\w+|$)",
        ]

        for pattern in input_patterns:
            input_match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if input_match:
                try:
                    content = input_match.group(1).strip()
                    # 尝试解析 JSON
                    result["action_input"] = json.loads(content)
                except json.JSONDecodeError:
                    # 如果不是 JSON，作为字符串参数处理
                    result["action_input"] = {"command": content} if result["action"] == "bash" else {"skill_name": content}
                break

        return result

    def _build_tools_for_api(self) -> list:
        """构建 OpenAI API 格式的 tools 定义"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "load_skill",
                    "description": "Load a skill's detailed instructions when user request matches a skill's description",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "skill_name": {
                                "type": "string",
                                "description": "Name of the skill to load"
                            }
                        },
                        "required": ["skill_name"]
                    }
                }
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
                                "description": "Shell command to execute"
                            },
                            "cwd": {
                                "type": "string",
                                "description": "Working directory",
                                "default": "."
                            }
                        },
                        "required": ["command"]
                    }
                }
            }
        ]

    def run(self, task: str) -> str:
        """
        运行 Agent 执行任务

        Args:
            task: 用户任务

        Returns:
            最终答案
        """
        history = ""
        messages = [
            {"role": "system", "content": self._create_system_prompt()},
            {"role": "user", "content": task}
        ]

        for i in range(self.max_iterations):
            safe_print(f"\n--- 迭代 {i+1} ---")

            # 调用模型
            if self.backend == "ollama":
                # Ollama 使用 ReAct 格式
                prompt = self._create_react_prompt(task, history)
                response = self.client.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = response["message"]["content"]

                # 解析响应
                parsed = self._parse_response(response_text)
                safe_print(f"Thought: {parsed['thought'][:100] if parsed['thought'] else '(empty)'}...")

                # 检查是否结束
                if parsed["final_answer"]:
                    safe_print(f"Final Answer: {parsed['final_answer']}")
                    return parsed["final_answer"]

                # 执行工具
                if parsed["action"] and parsed["action"] in self.tools:
                    safe_print(f"Action: {parsed['action']}")
                    safe_print(f"Action Input: {parsed['action_input']}")

                    try:
                        result = self.tools[parsed["action"]](**parsed["action_input"])
                    except Exception as e:
                        result = f"Error: {str(e)}"

                    safe_print(f"Observation: {result[:200]}...")

                    # 更新历史
                    history += f"""
Thought: {parsed['thought']}
Action: {parsed['action']}
Action Input: {json.dumps(parsed['action_input'], ensure_ascii=False)}
Observation: {result}
"""
                else:
                    history += f"\nThought: {parsed['thought']}\n"

            else:
                # OpenAI 兼容 API 使用 Function Calling
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self._build_tools_for_api(),
                    tool_choice="auto"
                )

                message = response.choices[0].message

                # 检查是否有工具调用
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)

                        safe_print(f"Function Call: {function_name}({function_args})")

                        # 执行工具
                        if function_name in self.tools:
                            try:
                                result = self.tools[function_name](**function_args)
                            except Exception as e:
                                result = f"Error: {str(e)}"

                            safe_print(f"Result: {result[:200]}...")

                            # 添加 assistant 的消息
                            messages.append({
                                "role": "assistant",
                                "content": message.content or "",
                                "tool_calls": [
                                    {
                                        "id": tool_call.id,
                                        "type": "function",
                                        "function": {
                                            "name": function_name,
                                            "arguments": tool_call.function.arguments
                                        }
                                    }
                                ]
                            })

                            # 添加 tool 结果
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": str(result)
                            })
                        else:
                            safe_print(f"Unknown function: {function_name}")
                            return f"Error: Unknown function {function_name}"
                else:
                    # 直接返回回答
                    final_answer = message.content
                    safe_print(f"Final Answer: {final_answer}")
                    return final_answer

        return "达到最大迭代次数，任务未完成。"


# ==================== 主程序 ====================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Skills Agent")
    parser.add_argument(
        "--backend",
        choices=["ollama", "openai"],
        default="openai",
        help="选择后端 (默认: openai)"
    )
    parser.add_argument(
        "--task",
        type=str,
        default=None,
        help="要执行的任务"
    )
    args = parser.parse_args()

    # 选择模型
    if args.backend == "openai":
        model = os.getenv("OPENAI_MODEL", "deepseek-v4-pro")
    else:
        model = "qwen2.5:7b"

    print("=" * 60)
    print("实验 3.7b：Skills Agent（双模式）")
    print("=" * 60)
    safe_print(f"后端: {args.backend}")
    safe_print(f"模型: {model}\n")

    # 显示可用 Skills（Level 1）
    loader = SkillLoader()
    skills = loader.scan_skills()
    if skills:
        print("可用 Skills:")
        for s in skills:
            safe_print(f"  - {s.name}: {s.description}")
        print()
    else:
        print("未找到任何 Skills\n")

    # 创建 Agent
    agent = SkillsAgent(model=model, backend=args.backend)

    # 运行任务
    if args.task:
        task = args.task
    else:
        task = "帮我扫描一下 localhost 的 80 端口"

    safe_print(f"任务: {task}\n")
    print("=" * 60)
    result = agent.run(task)
    print("=" * 60)
    safe_print(f"\n最终结果: {result}")
