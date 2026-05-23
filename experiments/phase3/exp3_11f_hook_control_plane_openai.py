"""
实验 3.11f: Hook Control Plane Runtime

目标：
  - 学习 Claude Code Hooks 官方文档中的核心思想：
      Hook 是 runtime 控制面，不是模型推理能力。
  - 演示 Hook 如何在 session、prompt、tool、task、subagent、compact 生命周期中触发。
  - 用确定性脚本完成验证，避免教学实验依赖模型是否主动收口。

参考边界：
  - Claude Code Hooks reference:
    SessionStart / UserPromptSubmit / PreToolUse / PostToolUse /
    TaskCreated / TaskCompleted / SubagentStart / SubagentStop /
    PreCompact / PostCompact / SessionEnd。
  - pengchengneo/Claude-Code:
    关注 hook、permission、context collapse、task lifecycle 的工程线索。

运行方式：
  ./venv/bin/python experiments/phase3/exp3_11f_hook_control_plane_openai.py --help
  ./venv/bin/python experiments/phase3/exp3_11f_hook_control_plane_openai.py --scripted
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from exp3_11d_coordinator_runtime_openai import WORKSPACE_ROOT, tool_read, tool_shell


DEFAULT_STATE_DIR = Path(tempfile.gettempdir()) / "beginningwithai-exp3-11f"


@dataclass
class HookContext:
    """传给 hook handler 的事件上下文。"""

    event: str
    session_id: str
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HookDecision:
    """hook 返回的控制结果。"""

    allow: bool = True
    reason: str = ""
    add_context: str = ""


HookHandler = Callable[[HookContext], HookDecision]


class HookRegistry:
    """
    最小 hook registry。

    官方 Hook 配置里有 event、matcher、handler 三层。
    这里保留核心语义：按事件注册 handler，触发时收集 allow / deny / context。
    """

    def __init__(self):
        self.handlers: Dict[str, List[HookHandler]] = {}

    def register(self, event: str, handler: HookHandler) -> None:
        self.handlers.setdefault(event, []).append(handler)

    def fire(self, context: HookContext) -> HookDecision:
        final = HookDecision()
        for handler in self.handlers.get(context.event, []):
            decision = handler(context)
            if decision.add_context:
                final.add_context += decision.add_context + "\n"
            if not decision.allow:
                return decision
        return final


class HookedRuntime:
    """
    教学用 Hook 控制面 runtime。

    重点不是实现完整 agent loop，而是展示：
      - PreToolUse 可以阻断工具
      - PostToolUse 可以审计结果
      - TaskCompleted 可以阻断不合格完成
      - PreCompact / PostCompact 是上下文生命周期事件
    """

    def __init__(self, state_dir: Path = DEFAULT_STATE_DIR):
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.audit_log = self.state_dir / "audit.jsonl"
        self.compact_log = self.state_dir / "compact.jsonl"
        self.registry = HookRegistry()
        self.session_id = "hook-session-001"
        self.messages: List[Dict[str, str]] = []
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self._register_default_hooks()

    def _register_default_hooks(self) -> None:
        self.registry.register("SessionStart", self._audit_hook)
        self.registry.register("UserPromptSubmit", self._prompt_context_hook)
        self.registry.register("PreToolUse", self._deny_sensitive_read_hook)
        self.registry.register("PreToolUse", self._deny_destructive_shell_hook)
        self.registry.register("PostToolUse", self._audit_hook)
        self.registry.register("TaskCreated", self._audit_hook)
        self.registry.register("TaskCompleted", self._task_completion_gate_hook)
        self.registry.register("SubagentStart", self._audit_hook)
        self.registry.register("SubagentStop", self._audit_hook)
        self.registry.register("PreCompact", self._compact_audit_hook)
        self.registry.register("PostCompact", self._compact_audit_hook)
        self.registry.register("SessionEnd", self._audit_hook)

    def start_session(self) -> None:
        self._fire("SessionStart", {"started_by": "scripted"})

    def submit_prompt(self, prompt: str) -> str:
        decision = self._fire("UserPromptSubmit", {"prompt": prompt})
        self.messages.append({"role": "user", "content": prompt})
        if decision.add_context:
            self.messages.append({"role": "system", "content": decision.add_context.strip()})
        return decision.add_context

    def create_task(self, title: str) -> str:
        task_id = f"hook-task-{len(self.tasks) + 1:03d}"
        self.tasks[task_id] = {"task_id": task_id, "title": title, "status": "pending", "verification_passed": False}
        self._fire("TaskCreated", {"task_id": task_id, "title": title})
        return task_id

    def start_subagent(self, agent_type: str, task_id: str) -> None:
        self._fire("SubagentStart", {"agent_type": agent_type, "task_id": task_id})

    def stop_subagent(self, agent_type: str, task_id: str, result: str) -> None:
        self._fire("SubagentStop", {"agent_type": agent_type, "task_id": task_id, "result": result})

    def run_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        pre = self._fire("PreToolUse", {"tool_name": tool_name, "tool_input": tool_input})
        if not pre.allow:
            denied = {"status": "denied", "reason": pre.reason, "tool_name": tool_name, "tool_input": tool_input}
            self._write_jsonl(self.audit_log, {"event": "PermissionDenied", **denied})
            return denied

        if tool_name == "read":
            output = tool_read(**tool_input)
        elif tool_name == "shell":
            output = tool_shell(**tool_input)
        else:
            output = json.dumps({"error": f"unknown tool: {tool_name}"}, ensure_ascii=False)

        result = {"status": "ok", "tool_name": tool_name, "tool_input": tool_input, "output": output}
        self._fire("PostToolUse", result)
        return result

    def complete_task(self, task_id: str) -> Dict[str, Any]:
        decision = self._fire("TaskCompleted", self.tasks[task_id])
        if not decision.allow:
            return {"status": "blocked", "task_id": task_id, "reason": decision.reason}
        self.tasks[task_id]["status"] = "completed"
        return {"status": "completed", "task_id": task_id}

    def mark_verification_passed(self, task_id: str) -> None:
        self.tasks[task_id]["verification_passed"] = True

    def compact(self) -> Dict[str, Any]:
        self._fire("PreCompact", {"message_count": len(self.messages)})
        summary = " | ".join(message["content"][:80] for message in self.messages[-4:])
        self.messages = [{"role": "system", "content": f"Compacted summary: {summary}"}]
        self._fire("PostCompact", {"message_count": len(self.messages), "summary": summary})
        return {"message_count": len(self.messages), "summary": summary}

    def end_session(self) -> None:
        self._fire("SessionEnd", {"task_count": len(self.tasks)})

    def run_scripted_demo(self) -> Dict[str, Any]:
        self.start_session()
        injected_context = self.submit_prompt("分析 Hook 为什么属于控制面，而不是 prompt 技巧。")
        task_id = self.create_task("Verify hook-controlled task completion")
        self.start_subagent("explore", task_id)
        denied_read = self.run_tool("read", {"path": ".env", "start_line": 1, "end_line": 5})
        allowed_read = self.run_tool(
            "read",
            {"path": "experiments/phase3/exp3_11d_coordinator_runtime_openai.py", "start_line": 399, "end_line": 430},
        )
        denied_shell = self.run_tool("shell", {"command": "rm -rf /tmp/build", "cwd": "."})
        verification = self.run_tool(
            "shell",
            {"command": "./venv/bin/python experiments/phase3/exp3_11f_hook_control_plane_openai.py --help", "cwd": ".", "timeout": 90},
        )
        blocked_completion = self.complete_task(task_id)
        self.mark_verification_passed(task_id)
        completed = self.complete_task(task_id)
        self.stop_subagent("explore", task_id, "verification evidence collected")
        compact_result = self.compact()
        self.end_session()
        return {
            "injected_context": injected_context.strip(),
            "denied_read": denied_read,
            "allowed_read_status": allowed_read["status"],
            "denied_shell": denied_shell,
            "verification": self._decode_tool_output(verification),
            "blocked_completion": blocked_completion,
            "completed": completed,
            "compact_result": compact_result,
            "audit_log": str(self.audit_log),
            "compact_log": str(self.compact_log),
        }

    def _fire(self, event: str, payload: Dict[str, Any]) -> HookDecision:
        return self.registry.fire(HookContext(event=event, session_id=self.session_id, payload=payload))

    def _audit_hook(self, context: HookContext) -> HookDecision:
        self._write_jsonl(self.audit_log, {"event": context.event, "session_id": context.session_id, "payload": context.payload})
        return HookDecision()

    def _prompt_context_hook(self, context: HookContext) -> HookDecision:
        return HookDecision(add_context="Runtime note: Hooks can add context, but enforcement belongs to PreToolUse/TaskCompleted.")

    def _deny_sensitive_read_hook(self, context: HookContext) -> HookDecision:
        if context.payload.get("tool_name") != "read":
            return HookDecision()
        path = context.payload.get("tool_input", {}).get("path", "")
        denied_patterns = [".env", ".env.*", "secrets/**", "config/credentials.json"]
        if any(fnmatch.fnmatch(path, pattern) for pattern in denied_patterns):
            return HookDecision(allow=False, reason=f"PreToolUse blocked sensitive read: {path}")
        return HookDecision()

    def _deny_destructive_shell_hook(self, context: HookContext) -> HookDecision:
        if context.payload.get("tool_name") != "shell":
            return HookDecision()
        command = context.payload.get("tool_input", {}).get("command", "")
        if "rm -rf" in command or "del /s" in command.lower():
            return HookDecision(allow=False, reason=f"PreToolUse blocked destructive shell command: {command}")
        return HookDecision()

    def _task_completion_gate_hook(self, context: HookContext) -> HookDecision:
        if not context.payload.get("verification_passed"):
            return HookDecision(allow=False, reason="TaskCompleted blocked: verification_passed is false")
        self._audit_hook(context)
        return HookDecision()

    def _compact_audit_hook(self, context: HookContext) -> HookDecision:
        self._write_jsonl(self.compact_log, {"event": context.event, "payload": context.payload})
        return HookDecision()

    def _write_jsonl(self, path: Path, payload: Dict[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def _decode_tool_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        decoded = dict(result)
        if isinstance(decoded.get("output"), str):
            try:
                decoded["output"] = json.loads(decoded["output"])
            except json.JSONDecodeError:
                pass
        return decoded


def main() -> None:
    parser = argparse.ArgumentParser(description="Hook 控制面教学实验")
    parser.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR), help="Directory for audit and compact logs")
    parser.add_argument("--scripted", action="store_true", help="Run deterministic hook lifecycle demo")
    args = parser.parse_args()

    runtime = HookedRuntime(state_dir=Path(args.state_dir))
    result = runtime.run_scripted_demo()

    print("\n" + "=" * 60)
    print("Hook Control Plane Result")
    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
