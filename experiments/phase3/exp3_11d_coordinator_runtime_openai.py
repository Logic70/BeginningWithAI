"""
实验 3.11d: OpenAI SDK 版 Coordinator / Worker Runtime

目标：
  - 在 3.11c 的 subagent runtime 之后，继续学习更接近 code agent 的
    Coordinator / Worker 分层。
  - 重点不是多几个固定角色，而是把“指挥”和“执行”拆成两个运行层。
  - Coordinator 只拥有控制工具：agent / send_message / task_stop。
  - Worker 才拥有代码库工具：glob / read / grep / shell。

参考边界：
  1. Claude Code Agent Teams 官方文档
     - team lead 负责创建队伍、分配任务、综合结果
     - teammates 有独立上下文窗口
     - shared task list / mailbox 是 team 协作核心
  2. pengchengneo/Claude-Code 的 Coordinator 文档
     - Coordinator 只有 Agent / SendMessage / TaskStop 三类工具
     - Worker 在独立执行上下文里运行
     - Worker 结果以 task-notification 回流
     - 禁止“甩锅式委派”：Worker prompt 必须自包含

这份实验仍是教学原型，不复刻任何私有实现。
它只实现 code agent 中可观察、可解释的核心运行时结构。

运行方式：
  python experiments/phase3/exp3_11d_coordinator_runtime_openai.py --help
  python experiments/phase3/exp3_11d_coordinator_runtime_openai.py --scripted
  python experiments/phase3/exp3_11d_coordinator_runtime_openai.py --task "分析 exp3_11b 的多 Agent 调度结构"
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(Path(__file__).parent.parent.parent / ".env")


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "deepseek-v4-pro")
WORKSPACE_ROOT = Path(__file__).parent.parent.parent.resolve()
DEFAULT_STATE_DIR = Path(tempfile.gettempdir()) / "beginningwithai-exp3-11d"
IGNORED_PATH_PARTS = {
    "__pycache__",
    ".git",
    "node_modules",
    "logs",
    "checkpoints",
    "platform_checkpoints",
    ".runtime",
}


def create_client() -> OpenAI:
    """创建 OpenAI-compatible client。"""
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        timeout=float(os.getenv("OPENAI_TIMEOUT", "90")),
    )


def normalize_path(path: str) -> Path:
    """把工作区相对路径规范到仓库内，防止工具读到工作区外。"""
    candidate = (WORKSPACE_ROOT / path).resolve()
    if WORKSPACE_ROOT not in candidate.parents and candidate != WORKSPACE_ROOT:
        raise ValueError(f"path escapes workspace: {path}")
    return candidate


def is_noise_path(path: Path) -> bool:
    """过滤缓存、日志、检查点等生成物。"""
    return any(part in IGNORED_PATH_PARTS for part in path.parts)


def tool_glob(pattern: str, root: str = ".", limit: int = 200) -> str:
    """按 glob pattern 查找文件。"""
    base = normalize_path(root)
    matches = [
        str(path.relative_to(WORKSPACE_ROOT))
        for path in base.rglob(pattern)
        if path.is_file() and not is_noise_path(path)
    ]
    return json.dumps({"root": str(base.relative_to(WORKSPACE_ROOT)), "matches": matches[:limit]}, ensure_ascii=False)


def tool_read(path: str, start_line: int = 1, end_line: int = 200) -> str:
    """读取文件片段，并附带行号。"""
    target = normalize_path(path)
    lines = target.read_text(encoding="utf-8", errors="ignore").splitlines()
    start = max(start_line, 1)
    end = max(end_line, start)
    content = "\n".join(f"{index + 1}: {lines[index]}" for index in range(start - 1, min(end, len(lines))))
    return json.dumps(
        {
            "path": str(target.relative_to(WORKSPACE_ROOT)),
            "start_line": start,
            "end_line": end,
            "content": content,
        },
        ensure_ascii=False,
    )


def tool_grep(query: str, root: str = ".", glob: str = "*.py", limit: int = 80) -> str:
    """优先使用 rg 搜索；rg 不存在时退回 Python 扫描。"""
    base = normalize_path(root)
    rg_command = ["rg", "-n", "--glob", glob, query, str(base)]
    try:
        completed = subprocess.run(rg_command, capture_output=True, text=True, check=False)
        if completed.returncode in (0, 1):
            lines = [
                line
                for line in completed.stdout.splitlines()
                if not is_noise_path(Path(line.split(":", 1)[0]))
            ]
            return json.dumps(
                {"root": str(base.relative_to(WORKSPACE_ROOT)), "query": query, "matches": lines[:limit]},
                ensure_ascii=False,
            )
    except FileNotFoundError:
        pass

    matches: List[str] = []
    for path in base.rglob(glob):
        if not path.is_file() or is_noise_path(path):
            continue
        try:
            for index, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if query in line:
                    matches.append(f"{path.relative_to(WORKSPACE_ROOT)}:{index}:{line}")
                    if len(matches) >= limit:
                        return json.dumps(
                            {"root": str(base.relative_to(WORKSPACE_ROOT)), "query": query, "matches": matches},
                            ensure_ascii=False,
                        )
        except OSError:
            continue
    return json.dumps({"root": str(base.relative_to(WORKSPACE_ROOT)), "query": query, "matches": matches}, ensure_ascii=False)


def tool_shell(command: str, cwd: str = ".", timeout: int = 60) -> str:
    """
    受限 shell 工具。

    这里只允许读分析和验证类命令，避免教学实验变成任意命令执行器。
    """
    blocked_tokens = {";", "&&", "||", "|", ">", "<", "`", "$("}
    if any(token in command for token in blocked_tokens):
        return json.dumps({"error": "compound shell syntax is not allowed in this teaching tool"}, ensure_ascii=False)

    args = shlex.split(command)
    if not args:
        return json.dumps({"error": "empty command"}, ensure_ascii=False)

    executable = Path(args[0]).name
    allowed = {"python", "python3", "rg", "ls", "pwd"}
    if executable not in allowed:
        return json.dumps({"error": f"command not allowed: {args[0]}", "allowed": sorted(allowed)}, ensure_ascii=False)

    working_dir = normalize_path(cwd)
    completed = subprocess.run(
        args,
        cwd=working_dir,
        capture_output=True,
        text=True,
        timeout=max(1, min(timeout, 120)),
        check=False,
    )
    return json.dumps(
        {
            "command": command,
            "cwd": str(working_dir.relative_to(WORKSPACE_ROOT)),
            "returncode": completed.returncode,
            "stdout": completed.stdout[-4000:],
            "stderr": completed.stderr[-4000:],
        },
        ensure_ascii=False,
    )


WORKER_TOOLS: Dict[str, Dict[str, Any]] = {
    "glob": {
        "schema": {
            "type": "function",
            "function": {
                "name": "glob",
                "description": "Find files in the workspace by glob pattern.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "root": {"type": "string"},
                        "limit": {"type": "integer"},
                    },
                    "required": ["pattern"],
                },
            },
        },
        "function": tool_glob,
    },
    "read": {
        "schema": {
            "type": "function",
            "function": {
                "name": "read",
                "description": "Read a file from the workspace with line numbers.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "start_line": {"type": "integer"},
                        "end_line": {"type": "integer"},
                    },
                    "required": ["path"],
                },
            },
        },
        "function": tool_read,
    },
    "grep": {
        "schema": {
            "type": "function",
            "function": {
                "name": "grep",
                "description": "Search files in the workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "root": {"type": "string"},
                        "glob": {"type": "string"},
                        "limit": {"type": "integer"},
                    },
                    "required": ["query"],
                },
            },
        },
        "function": tool_grep,
    },
    "shell": {
        "schema": {
            "type": "function",
            "function": {
                "name": "shell",
                "description": "Run a restricted read-only or verification command in the workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"},
                        "cwd": {"type": "string"},
                        "timeout": {"type": "integer"},
                    },
                    "required": ["command"],
                },
            },
        },
        "function": tool_shell,
    },
}


@dataclass
class WorkerSpec:
    """Worker 规格：Worker 执行具体工作，拥有代码库工具。"""

    name: str
    description: str
    system_prompt: str
    allowed_tools: List[str]


@dataclass
class TaskRecord:
    """文件化 task list 中的一条任务记录。"""

    task_id: str
    worker_type: str
    task_kind: str
    prompt: str
    files: List[str]
    status: str = "pending"
    result: str = ""
    summary: str = ""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: Dict[str, str] = field(default_factory=dict)


@dataclass
class WorkerRunResult:
    task_id: str
    worker_type: str
    status: str
    summary: str
    result: str
    tool_results: Dict[str, str]


class TaskStore:
    """用本地 JSON 文件模拟 Claude Code 文档中的 shared task list。"""

    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.state_dir / "tasks.json"
        self.records: Dict[str, TaskRecord] = {}
        self._counter = 0

    def create(self, worker_type: str, task_kind: str, prompt: str, files: Optional[List[str]] = None) -> TaskRecord:
        self._counter += 1
        record = TaskRecord(
            task_id=f"task-{self._counter:03d}",
            worker_type=worker_type,
            task_kind=task_kind,
            prompt=prompt,
            files=files or [],
        )
        self.records[record.task_id] = record
        self.save()
        return record

    def save(self) -> None:
        payload = {
            task_id: {
                "task_id": record.task_id,
                "worker_type": record.worker_type,
                "task_kind": record.task_kind,
                "prompt": record.prompt,
                "files": record.files,
                "status": record.status,
                "summary": record.summary,
                "result": record.result,
            }
            for task_id, record in self.records.items()
        }
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class CoordinatorRuntime:
    """
    教学用 Coordinator / Worker runtime。

    与 3.11c 的区别：
      - 3.11c 关注 primary 调用 subagent，并把结果返回父 session。
      - 3.11d 关注 Coordinator 只做控制和综合，Worker 才做代码库操作。
    """

    def __init__(self, client: OpenAI, model: str = DEFAULT_MODEL, state_dir: Path = DEFAULT_STATE_DIR, max_rounds: int = 5):
        self.client = client
        self.model = model
        self.max_rounds = max_rounds
        self.task_store = TaskStore(state_dir)
        self.worker_specs = self._build_worker_specs()

    def _build_worker_specs(self) -> Dict[str, WorkerSpec]:
        return {
            "research": WorkerSpec(
                name="research",
                description="Read-only worker for codebase discovery and evidence gathering.",
                system_prompt=(
                    "You are a Research Worker. Use read, grep, and glob to gather evidence. "
                    "Do not modify files. Return concrete file paths, line numbers, and concise conclusions. "
                    "Once you have enough evidence, stop using tools and answer directly."
                ),
                allowed_tools=["glob", "read", "grep"],
            ),
            "implementation": WorkerSpec(
                name="implementation",
                description="Worker for implementation planning in this teaching demo.",
                system_prompt=(
                    "You are an Implementation Worker. In this teaching demo, do not edit files. "
                    "Instead, produce a precise implementation plan with file paths, functions, and acceptance criteria. "
                    "Once you have enough evidence, stop using tools and answer directly."
                ),
                allowed_tools=["glob", "read", "grep"],
            ),
            "verification": WorkerSpec(
                name="verification",
                description="Worker for running safe verification commands and reporting results.",
                system_prompt=(
                    "You are a Verification Worker. Use shell only for safe read-only or verification commands. "
                    "Report the exact command, return code, and important output. "
                    "After running the requested verification command once, stop using tools and answer directly."
                ),
                allowed_tools=["shell", "read", "grep"],
            ),
        }

    def run_coordinator(self, task: str) -> str:
        """
        运行 Coordinator。

        Coordinator 只看见 agent / send_message / task_stop 三个控制工具。
        它不能直接 grep/read/shell，这样才能逼迫它先拆任务、再综合结果。
        """
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self._coordinator_prompt()},
            {"role": "user", "content": task},
        ]

        for _ in range(self.max_rounds):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._coordinator_tool_schemas(),
                tool_choice="auto",
            )
            message = response.choices[0].message

            if not getattr(message, "tool_calls", None):
                return message.content or ""

            messages.append(self._assistant_message_for_history(message))
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments or "{}")
                tool_output = self._execute_coordinator_tool(function_name, function_args)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_output,
                    }
                )

        return "Coordinator exceeded max rounds before final answer."

    def run_scripted_demo(self) -> str:
        """
        固定四阶段演示。

        这个入口用于验证 runtime 行为，不依赖 Coordinator 模型自己决定怎么派工。
        Worker 仍然是真实 OpenAI tool-calling session。
        """
        research = self.spawn_worker(
            worker_type="research",
            task_kind="Research",
            prompt=(
                "只分析 experiments/phase3/exp3_11b_multi_agent_openai.py。"
                "找出 create_agents、choose_next_agent、run_supervisor、run_swarm 的位置和职责。"
                "必要时使用 grep/read，完成后直接总结，不要读取无关文件。"
            ),
            files=["experiments/phase3/exp3_11b_multi_agent_openai.py"],
        )
        verify = self.spawn_worker(
            worker_type="verification",
            task_kind="Verification",
            prompt=(
                "运行 ./venv/bin/python experiments/phase3/exp3_11b_multi_agent_openai.py --help，"
                "报告命令是否成功和关键输出。"
            ),
            files=["experiments/phase3/exp3_11b_multi_agent_openai.py"],
        )
        return self._synthesize(
            user_task="演示 Coordinator / Worker：研究 exp3_11b 的调度结构并验证 CLI 入口。",
            notifications=[self._task_notification(research), self._task_notification(verify)],
        )

    def spawn_worker(self, worker_type: str, task_kind: str, prompt: str, files: Optional[List[str]] = None) -> WorkerRunResult:
        if worker_type not in self.worker_specs:
            return WorkerRunResult(
                task_id="unknown",
                worker_type=worker_type,
                status="failed",
                summary=f"unknown worker type: {worker_type}",
                result="",
                tool_results={},
            )

        record = self.task_store.create(worker_type=worker_type, task_kind=task_kind, prompt=prompt, files=files)
        record.status = "in_progress"
        self.task_store.save()
        result = self._run_worker(record)
        record.status = result.status
        record.summary = result.summary
        record.result = result.result
        record.tool_results = result.tool_results
        self.task_store.save()
        return result

    def send_message(self, task_id: str, message: str) -> WorkerRunResult:
        """
        继续已有 Worker。

        真实系统会把消息送到正在运行的子进程。
        这里用同一条 TaskRecord 的 messages 继续对话，保留上下文。
        """
        if task_id not in self.task_store.records:
            return WorkerRunResult(task_id, "unknown", "failed", f"unknown task: {task_id}", "", {})

        record = self.task_store.records[task_id]
        record.prompt = message
        record.status = "in_progress"
        result = self._run_worker(record, continuation=message)
        record.status = result.status
        record.summary = result.summary
        record.result = result.result
        record.tool_results.update(result.tool_results)
        self.task_store.save()
        return result

    def stop_task(self, task_id: str, reason: str) -> str:
        if task_id not in self.task_store.records:
            return json.dumps({"error": f"unknown task: {task_id}"}, ensure_ascii=False)
        record = self.task_store.records[task_id]
        record.status = "killed"
        record.summary = reason
        self.task_store.save()
        return self._task_notification(
            WorkerRunResult(task_id, record.worker_type, "killed", reason, record.result, record.tool_results)
        )

    def _run_worker(self, record: TaskRecord, continuation: str = "") -> WorkerRunResult:
        spec = self.worker_specs[record.worker_type]
        if not record.messages:
            record.messages = [
                {"role": "system", "content": spec.system_prompt},
                {"role": "user", "content": self._worker_user_prompt(record)},
            ]
        elif continuation:
            record.messages.append({"role": "user", "content": continuation})

        tool_results: Dict[str, str] = {}
        tool_schemas = [WORKER_TOOLS[name]["schema"] for name in spec.allowed_tools]

        for _ in range(self.max_rounds):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=record.messages,
                tools=tool_schemas,
                tool_choice="auto",
            )
            message = response.choices[0].message

            if not getattr(message, "tool_calls", None):
                output = message.content or ""
                record.messages.append({"role": "assistant", "content": output})
                return WorkerRunResult(
                    task_id=record.task_id,
                    worker_type=record.worker_type,
                    status="completed",
                    summary=self._make_summary(output),
                    result=output,
                    tool_results=tool_results,
                )

            record.messages.append(self._assistant_message_for_history(message))
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments or "{}")
                tool_output = self._execute_worker_tool(spec, function_name, function_args)
                tool_results[function_name] = tool_output
                record.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_output,
                    }
                )

        if tool_results:
            result = self._fallback_worker_result(record, tool_results)
            return WorkerRunResult(
                task_id=record.task_id,
                worker_type=record.worker_type,
                status="completed",
                summary=self._make_summary(result),
                result=result,
                tool_results=tool_results,
            )

        return WorkerRunResult(
            task_id=record.task_id,
            worker_type=record.worker_type,
            status="failed",
            summary="Worker exceeded max rounds before final answer.",
            result="Worker exceeded max rounds before final answer.",
            tool_results=tool_results,
        )

    def _execute_worker_tool(self, spec: WorkerSpec, function_name: str, function_args: Dict[str, Any]) -> str:
        if function_name not in spec.allowed_tools:
            return json.dumps({"error": f"tool not allowed for {spec.name}: {function_name}"}, ensure_ascii=False)
        tool_function: Callable[..., str] = WORKER_TOOLS[function_name]["function"]
        try:
            return tool_function(**function_args)
        except Exception as exc:
            return json.dumps({"error": str(exc)}, ensure_ascii=False)

    def _execute_coordinator_tool(self, function_name: str, function_args: Dict[str, Any]) -> str:
        if function_name == "agent":
            result = self.spawn_worker(
                worker_type=function_args["worker_type"],
                task_kind=function_args.get("task_kind", "Research"),
                prompt=function_args["prompt"],
                files=function_args.get("files", []),
            )
            return self._task_notification(result)

        if function_name == "send_message":
            result = self.send_message(function_args["task_id"], function_args["message"])
            return self._task_notification(result)

        if function_name == "task_stop":
            return self.stop_task(function_args["task_id"], function_args["reason"])

        return json.dumps({"error": f"unknown coordinator tool: {function_name}"}, ensure_ascii=False)

    def _coordinator_tool_schemas(self) -> List[Dict[str, Any]]:
        worker_types = list(self.worker_specs)
        return [
            {
                "type": "function",
                "function": {
                    "name": "agent",
                    "description": "Spawn a worker in an independent task context.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "worker_type": {"type": "string", "enum": worker_types},
                            "task_kind": {"type": "string", "enum": ["Research", "Synthesis", "Implementation", "Verification"]},
                            "prompt": {"type": "string", "description": "Self-contained worker instruction"},
                            "files": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Workspace files or directories in scope",
                            },
                        },
                        "required": ["worker_type", "prompt"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "send_message",
                    "description": "Send follow-up instructions to an existing worker task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string"},
                            "message": {"type": "string"},
                        },
                        "required": ["task_id", "message"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "task_stop",
                    "description": "Stop a worker task that is going in the wrong direction.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string"},
                            "reason": {"type": "string"},
                        },
                        "required": ["task_id", "reason"],
                    },
                },
            },
        ]

    def _coordinator_prompt(self) -> str:
        return (
            "You are the Coordinator. You do not directly inspect files or run shell commands. "
            "Your only tools are agent, send_message, and task_stop. "
            "Use research workers for code discovery, implementation workers for precise implementation planning, "
            "and verification workers for safe verification commands. "
            "You must synthesize worker outputs yourself. "
            "Do not delegate vague instructions like 'based on your findings'. "
            "Every worker prompt must include concrete scope, files if known, and completion criteria. "
            "After receiving enough task-notification results, produce a concise final answer."
        )

    def _worker_user_prompt(self, record: TaskRecord) -> str:
        return (
            f"Task id: {record.task_id}\n"
            f"Task kind: {record.task_kind}\n"
            f"Files in scope: {json.dumps(record.files, ensure_ascii=False)}\n\n"
            f"Instruction:\n{record.prompt}\n\n"
            "Completion criteria: return a concise result with evidence. If you used tools, cite paths, lines, or commands."
        )

    def _task_notification(self, result: WorkerRunResult) -> str:
        return (
            "<task-notification>\n"
            f"  <task-id>{result.task_id}</task-id>\n"
            f"  <worker-type>{result.worker_type}</worker-type>\n"
            f"  <status>{result.status}</status>\n"
            f"  <summary>{result.summary}</summary>\n"
            f"  <result>{result.result}</result>\n"
            "</task-notification>"
        )

    def _synthesize(self, user_task: str, notifications: List[str]) -> str:
        return (
            "Coordinator scripted synthesis\n\n"
            f"User task: {user_task}\n\n"
            "Worker notifications:\n\n"
            + "\n\n".join(notifications)
            + f"\n\nTask list stored at: {self.task_store.path}"
        )

    def _assistant_message_for_history(self, message: Any) -> Dict[str, Any]:
        assistant_message = {
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in message.tool_calls
            ],
        }
        reasoning_content = getattr(message, "reasoning_content", None)
        if reasoning_content:
            assistant_message["reasoning_content"] = reasoning_content
        return assistant_message

    def _make_summary(self, output: str, limit: int = 220) -> str:
        compact = " ".join(output.split())
        return compact[:limit] + ("..." if len(compact) > limit else "")

    def _fallback_worker_result(self, record: TaskRecord, tool_results: Dict[str, str]) -> str:
        """
        Worker 已经拿到工具证据但模型没有及时收口时，由 runtime 生成保底摘要。

        真实 code agent 通常会有更复杂的 stop policy / summarizer。
        教学实验里保留这个兜底，避免“证据已足够但模型继续调工具”导致演示失败。
        """
        lines = [
            f"Worker reached max rounds after collecting evidence for {record.task_id}.",
            f"Worker type: {record.worker_type}",
            f"Task kind: {record.task_kind}",
            "Collected tool evidence:",
        ]
        for name, value in tool_results.items():
            try:
                decoded = json.loads(value)
            except (TypeError, json.JSONDecodeError):
                decoded = value
            lines.append(f"- {name}: {json.dumps(decoded, ensure_ascii=False)[:1200]}")
        return "\n".join(lines)


def decode_tool_results(tool_results: Dict[str, str]) -> Dict[str, Any]:
    """展示层解码工具 JSON 字符串，避免终端输出双重转义。"""
    decoded: Dict[str, Any] = {}
    for name, value in tool_results.items():
        try:
            decoded[name] = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            decoded[name] = value
    return decoded


def print_task_list(runtime: CoordinatorRuntime) -> None:
    print("\n" + "=" * 60)
    print("Task List")
    print("=" * 60)
    for record in runtime.task_store.records.values():
        print(f"- {record.task_id} [{record.worker_type}/{record.task_kind}] {record.status}: {record.summary}")
        if record.tool_results:
            print(json.dumps(decode_tool_results(record.tool_results), ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenAI SDK 版 Coordinator / Worker Runtime 实验")
    parser.add_argument(
        "--task",
        default="分析 experiments/phase3/exp3_11b_multi_agent_openai.py 的多 Agent 调度结构，并验证 CLI 入口是否正常。",
        help="Task for the Coordinator.",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenAI-compatible model name")
    parser.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR), help="Directory for the teaching task list")
    parser.add_argument("--max-rounds", type=int, default=5, help="Max model/tool rounds per Coordinator or Worker")
    parser.add_argument("--scripted", action="store_true", help="Run a fixed four-stage-style demo without Coordinator LLM planning")
    args = parser.parse_args()

    runtime = CoordinatorRuntime(
        client=create_client(),
        model=args.model,
        state_dir=Path(args.state_dir),
        max_rounds=args.max_rounds,
    )

    if args.scripted:
        output = runtime.run_scripted_demo()
    else:
        output = runtime.run_coordinator(args.task)

    print("\n" + "=" * 60)
    print("Final Output")
    print("=" * 60)
    print(output)
    print_task_list(runtime)


if __name__ == "__main__":
    main()
