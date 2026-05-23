"""
实验 3.11i: Internal / System Agent Runtime

目标：
  - 把实验中已经出现但没有正式收束的 hidden/internal agent 概念做成独立章节。
  - 说明内部 Agent 不是给用户聊天的角色，而是 runtime 用来做判断、压缩、记忆抽取和权限分类的系统组件。
  - 用确定性脚本演示：permission classifier、completion judge、context compactor、memory curator。

运行方式：
  ./venv/bin/python experiments/phase3/exp3_11i_internal_system_agent_openai.py --help
  ./venv/bin/python experiments/phase3/exp3_11i_internal_system_agent_openai.py --scripted

说明：
  这个实验不调用模型。真实 code agent 中这些 internal agent 可以由模型或规则共同实现；
  本实验先保留运行时结构和数据流，避免把“模型说完成了”误当成可靠的完成条件。
"""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_STATE_DIR = Path(tempfile.gettempdir()) / "beginningwithai-exp3-11i"


@dataclass
class AgentSpec:
    """Agent 注册信息。hidden=True 表示这个 Agent 属于 runtime 内部能力。"""

    name: str
    role: str
    tools: List[str] = field(default_factory=list)
    hidden: bool = False


@dataclass
class TaskContract:
    """任务完成契约：系统用它判断候选结果是否真的可交付。"""

    required_sections: List[str]
    required_evidence: List[str]
    required_tests: List[str]
    forbidden_claims: List[str] = field(default_factory=list)


@dataclass
class CandidateResult:
    """用户可见 Agent 产出的候选结果。"""

    summary: str
    sections: List[str]
    evidence: Dict[str, str]
    tests: Dict[str, bool]
    memory_notes: List[str] = field(default_factory=list)


@dataclass
class InternalDecision:
    """内部 Agent 的短结论。这里保存原因，但不保存隐藏思维链。"""

    agent: str
    status: str
    reason: str
    data: Dict[str, Any] = field(default_factory=dict)


class InternalSystemAgentRuntime:
    """
    教学版 internal/system agent runtime。

    公开 Agent 负责产出候选结果；内部 Agent 负责判断这个结果是否能交付。
    重点是执行边界：
      - permission classifier 在工具执行前工作
      - completion judge 在任务完成前工作
      - context compactor 管理上下文预算
      - memory curator 只保留稳定事实
    """

    def __init__(self, state_dir: Path = DEFAULT_STATE_DIR):
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.events_path = self.state_dir / "internal_events.jsonl"
        self.memory_path = self.state_dir / "INTERNAL_MEMORY.md"
        self.agents = self._build_agents()

    def _build_agents(self) -> Dict[str, AgentSpec]:
        return {
            "builder": AgentSpec(
                name="builder",
                role="public coding agent that produces user-facing work",
                tools=["read", "grep", "shell"],
                hidden=False,
            ),
            "permission_classifier": AgentSpec(
                name="permission_classifier",
                role="internal policy agent that classifies requested actions before tool use",
                hidden=True,
            ),
            "completion_judge": AgentSpec(
                name="completion_judge",
                role="internal system agent that checks task contract before final answer",
                hidden=True,
            ),
            "context_compactor": AgentSpec(
                name="context_compactor",
                role="internal system agent that compresses long working context",
                hidden=True,
            ),
            "memory_curator": AgentSpec(
                name="memory_curator",
                role="internal system agent that extracts stable cross-session facts",
                hidden=True,
            ),
        }

    def classify_action(self, tool_name: str, tool_input: Dict[str, Any]) -> InternalDecision:
        """模拟 PreToolUse 前的权限分类，不依赖模型自觉遵守 prompt。"""
        path = str(tool_input.get("path", ""))
        command = str(tool_input.get("command", ""))

        if tool_name == "read" and self._is_sensitive_path(path):
            decision = InternalDecision(
                agent="permission_classifier",
                status="deny",
                reason=f"sensitive path is blocked: {path}",
                data={"tool_name": tool_name, "tool_input": tool_input},
            )
        elif tool_name == "shell" and self._is_destructive_command(command):
            decision = InternalDecision(
                agent="permission_classifier",
                status="deny",
                reason=f"destructive command is blocked: {command}",
                data={"tool_name": tool_name, "tool_input": tool_input},
            )
        else:
            decision = InternalDecision(
                agent="permission_classifier",
                status="allow",
                reason="action is allowed by the teaching policy",
                data={"tool_name": tool_name, "tool_input": tool_input},
            )

        self._event("internal_decision", decision)
        return decision

    def judge_completion(self, contract: TaskContract, candidate: CandidateResult) -> InternalDecision:
        """
        判断任务是否完成。

        这个函数刻意不用 LLM 来“感觉是否完成”，而是对照契约做结构化检查。
        """
        issues: List[str] = []
        for section in contract.required_sections:
            if section not in candidate.sections:
                issues.append(f"missing section: {section}")
        for evidence_name in contract.required_evidence:
            if not candidate.evidence.get(evidence_name):
                issues.append(f"missing evidence: {evidence_name}")
        for test_name in contract.required_tests:
            if candidate.tests.get(test_name) is not True:
                issues.append(f"test not passed: {test_name}")
        for claim in contract.forbidden_claims:
            if claim.lower() in candidate.summary.lower():
                issues.append(f"forbidden claim found: {claim}")

        status = "approved" if not issues else "blocked"
        reason = "candidate satisfies the task contract" if not issues else "; ".join(issues)
        decision = InternalDecision(
            agent="completion_judge",
            status=status,
            reason=reason,
            data={"issues": issues},
        )
        self._event("internal_decision", decision)
        return decision

    def compact_context(self, messages: List[Dict[str, str]], max_messages: int = 4) -> InternalDecision:
        """把长上下文压缩成可回填给主 Agent 的摘要。"""
        kept = messages[-max_messages:]
        summary_lines = [f"{item['role']}: {item['content'][:120]}" for item in kept]
        summary = "\n".join(summary_lines)
        decision = InternalDecision(
            agent="context_compactor",
            status="compacted",
            reason=f"compressed {len(messages)} messages into {len(kept)} summary lines",
            data={"summary": summary, "original_message_count": len(messages)},
        )
        self._event("internal_decision", decision)
        return decision

    def curate_memory(self, candidate: CandidateResult) -> InternalDecision:
        """
        只抽取显式稳定事实。

        教学规则：
          - "Stable fact:" 开头的内容可以进入长期记忆。
          - "Temporary:" 开头的观察不能进入长期记忆。
        """
        facts: List[str] = []
        ignored: List[str] = []
        for note in candidate.memory_notes:
            if note.startswith("Stable fact:"):
                facts.append(note.removeprefix("Stable fact:").strip())
            elif note.startswith("Temporary:"):
                ignored.append(note)

        if facts:
            existing = self.memory_path.read_text(encoding="utf-8") if self.memory_path.exists() else "# Internal Memory\n\n"
            new_lines = []
            for fact in facts:
                line = f"- {fact}\n"
                if line not in existing:
                    new_lines.append(line)
            if new_lines:
                self.memory_path.write_text(existing + "".join(new_lines), encoding="utf-8")

        decision = InternalDecision(
            agent="memory_curator",
            status="stored" if facts else "no_memory",
            reason=f"stored {len(facts)} stable facts; ignored {len(ignored)} temporary notes",
            data={"facts": facts, "ignored": ignored, "memory_path": str(self.memory_path)},
        )
        self._event("internal_decision", decision)
        return decision

    def run_scripted_demo(self) -> Dict[str, Any]:
        contract = TaskContract(
            required_sections=["course_design", "experiment_design", "verification"],
            required_evidence=["code_paths", "test_output"],
            required_tests=["py_compile", "scripted_run"],
            forbidden_claims=["trust me"],
        )

        requested_actions = [
            ("read", {"path": "docs/phase3_agent.md"}),
            ("read", {"path": ".env"}),
            ("shell", {"command": "rm -rf /tmp/demo"}),
        ]
        permissions = [self.classify_action(tool, payload).__dict__ for tool, payload in requested_actions]

        draft = CandidateResult(
            summary="Draft says the task is done, but test evidence is incomplete.",
            sections=["course_design", "experiment_design"],
            evidence={"code_paths": "experiments/phase3/exp3_11i_internal_system_agent_openai.py"},
            tests={"py_compile": True, "scripted_run": False},
            memory_notes=[
                "Stable fact: WSL commands should use ./venv/bin/python in this project.",
                "Temporary: The current draft is missing one verification section.",
            ],
        )
        blocked = self.judge_completion(contract, draft)

        fixed = CandidateResult(
            summary="Internal agents approved the deliverable after verification evidence was attached.",
            sections=["course_design", "experiment_design", "verification"],
            evidence={
                "code_paths": "experiments/phase3/exp3_11i_internal_system_agent_openai.py",
                "test_output": "py_compile passed; scripted_run passed",
            },
            tests={"py_compile": True, "scripted_run": True},
            memory_notes=[
                "Stable fact: Internal agents should return concise decisions, not hidden chain-of-thought.",
                "Stable fact: Completion should be checked against a task contract.",
                "Temporary: The scripted demo currently uses a synthetic localhost task.",
            ],
        )
        approved = self.judge_completion(contract, fixed)
        memory = self.curate_memory(fixed)

        long_context = [
            {"role": "user", "content": f"Round {index}: explain internal agent boundary in detail."}
            for index in range(8)
        ]
        compacted = self.compact_context(long_context)

        user_visible = {
            "summary": fixed.summary,
            "sections": fixed.sections,
            "evidence": fixed.evidence,
            "tests": fixed.tests,
        }

        return {
            "state_dir": str(self.state_dir),
            "visible_agents": [spec.name for spec in self.agents.values() if not spec.hidden],
            "internal_agents": [spec.name for spec in self.agents.values() if spec.hidden],
            "permissions": permissions,
            "blocked_completion": blocked.__dict__,
            "approved_completion": approved.__dict__,
            "memory_decision": memory.__dict__,
            "compact_decision": compacted.__dict__,
            "user_visible_output": user_visible,
            "internal_event_log": str(self.events_path),
        }

    def _is_sensitive_path(self, path: str) -> bool:
        normalized = path.replace("\\", "/").lower()
        return normalized in {".env", ".env.local"} or "secret" in normalized or "credential" in normalized

    def _is_destructive_command(self, command: str) -> bool:
        lowered = command.lower()
        return "rm -rf" in lowered or "del /s" in lowered or "remove-item -recurse" in lowered

    def _event(self, event: str, decision: InternalDecision) -> None:
        record = {"event": event, **decision.__dict__}
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Internal / System Agent Runtime 教学实验")
    parser.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR), help="Directory for internal event and memory files")
    parser.add_argument("--scripted", action="store_true", help="Run deterministic internal-agent demo")
    args = parser.parse_args()

    runtime = InternalSystemAgentRuntime(state_dir=Path(args.state_dir))
    result = runtime.run_scripted_demo()

    print("\n" + "=" * 60)
    print("Internal / System Agent Runtime Result")
    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
