"""
实验 3.11c: OpenAI SDK 版主 Agent + Subagent Runtime

目标：
  - 不修改现有 3.11b，而是新增一个更贴近现代 coding agent 的实验文件
  - 参考公开可验证的工程模式，而不是自创一套“看起来像多 Agent”的逻辑
  - 用 OpenAI SDK 演示：主 agent、subagent、独立上下文、工具权限、Task 委派原语

严格参考的公开实现模式：
  1. Claude Code subagents
     - subagent 有独立 context window
     - subagent 有自己的 system prompt 和工具限制
     - 主会话可以把侧任务委派给 subagent，再收回结果摘要
  2. OpenCode agents
     - primary agent 和 subagent 是两类不同角色
     - 内置 primary: Build / Plan
     - 内置 subagent: General / Explore（公开文档中如此）
     - primary agent 通过 Task 原语调用 subagent
     - permission.task 控制能调用哪些 subagent
  3. OpenClaw routing / sessions
     - 每个 agent / subagent 运行在隔离 session 里
     - 父子 session 关系是显式可追踪的

这份实验不会声称自己复刻这些项目的私有内部实现。
它只实现上述公开文档中可以验证的运行时特征。

运行方式：
  python experiments/phase3/exp3_11c_subagent_runtime_openai.py --task "找出 exp3_11b 里调度多 Agent 的核心函数"
  python experiments/phase3/exp3_11c_subagent_runtime_openai.py --agent plan --task "分析 exp3_11b 的结构，不要修改文件"
  python experiments/phase3/exp3_11c_subagent_runtime_openai.py --task "@explore 查找 phase3 里所有出现 tool_call_id 的地方"
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(Path(__file__).parent.parent.parent / ".env")


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "deepseek-v4-pro")
WORKSPACE_ROOT = Path(__file__).parent.parent.parent.resolve()
IGNORED_PATH_PARTS = {
    "__pycache__",
    ".git",
    "node_modules",
    "logs",
    "checkpoints",
    "platform_checkpoints",
}


def create_client() -> OpenAI:
    """统一创建 OpenAI-compatible client。"""
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )


def normalize_path(path: str) -> Path:
    """
    把用户输入路径规范到工作区内。

    真实 coding agent 通常都会有 workspace 边界。
    这里不做逃逸路径支持，保证实验行为简单且可控。
    """
    candidate = (WORKSPACE_ROOT / path).resolve()
    if WORKSPACE_ROOT not in candidate.parents and candidate != WORKSPACE_ROOT:
        raise ValueError(f"path escapes workspace: {path}")
    return candidate


def is_noise_path(path: Path) -> bool:
    """过滤生成物和仓库噪音目录，避免结果污染。"""
    return any(part in IGNORED_PATH_PARTS for part in path.parts)


# ============================================================
# 工具实现：参考实际 coding agent 常见内置工具面
# ============================================================

def tool_glob(pattern: str, root: str = ".", limit: int = 200) -> str:
    """
    近似 OpenCode / coding agent 常见的 glob 工具。

    作用：
      - 按模式发现文件
      - 给 Explore 类 subagent 用来快速摸清代码结构
    """
    base = normalize_path(root)
    results = [
        str(path.relative_to(WORKSPACE_ROOT))
        for path in base.rglob(pattern)
        if path.is_file() and not is_noise_path(path)
    ]
    return json.dumps({"root": str(base.relative_to(WORKSPACE_ROOT)), "matches": results[:limit]}, ensure_ascii=False)


def tool_read(path: str, start_line: int = 1, end_line: int = 200) -> str:
    """
    近似 coding agent 的 read 工具。

    真实系统会做更多分页、截断和编码处理。
    这里保留最关键的行为：按行读取，并返回带行号的片段。
    """
    target = normalize_path(path)
    text = target.read_text(encoding="utf-8", errors="ignore").splitlines()

    start = max(start_line, 1)
    end = max(end_line, start)
    snippet = []
    for index in range(start - 1, min(end, len(text))):
        snippet.append(f"{index + 1}: {text[index]}")

    return json.dumps(
        {
            "path": str(target.relative_to(WORKSPACE_ROOT)),
            "start_line": start,
            "end_line": end,
            "content": "\n".join(snippet),
        },
        ensure_ascii=False,
    )


def tool_grep(query: str, root: str = ".", glob: str = "*.py", limit: int = 50) -> str:
    """
    近似 coding agent 的 grep 工具。

    优先使用 rg。
    如果 rg 不存在，再退回 Python 扫描。
    """
    base = normalize_path(root)

    rg_command = [
        "rg",
        "-n",
        "--glob",
        glob,
        query,
        str(base),
    ]
    try:
        completed = subprocess.run(rg_command, capture_output=True, text=True, check=False)
        if completed.returncode in (0, 1):
            lines = completed.stdout.splitlines()[:limit]
            return json.dumps(
                {"root": str(base.relative_to(WORKSPACE_ROOT)), "query": query, "matches": lines},
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


TOOLS = {
    "glob": {
        "schema": {
            "type": "function",
            "function": {
                "name": "glob",
                "description": "Find files in the workspace by glob pattern.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Glob pattern, for example '*.py' or '**/*.md'"},
                        "root": {"type": "string", "description": "Workspace-relative root directory"},
                        "limit": {"type": "integer", "description": "Maximum number of matches to return"},
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
                        "path": {"type": "string", "description": "Workspace-relative file path"},
                        "start_line": {"type": "integer", "description": "First line to include"},
                        "end_line": {"type": "integer", "description": "Last line to include"},
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
                "description": "Search the workspace for a query string.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "String or pattern to search"},
                        "root": {"type": "string", "description": "Workspace-relative root directory"},
                        "glob": {"type": "string", "description": "File glob filter, for example '*.py'"},
                        "limit": {"type": "integer", "description": "Maximum number of matches to return"},
                    },
                    "required": ["query"],
                },
            },
        },
        "function": tool_grep,
    },
}


# ============================================================
# Agent / Session 规格：参考 OpenCode primary + subagent，Claude subagent 分离上下文
# ============================================================

@dataclass
class AgentSpec:
    """
    Agent 规格。

    这里对应公开文档里的“agent configuration”概念：
      - name
      - mode（primary / subagent）
      - description
      - prompt
      - tools / permissions
    """

    name: str
    mode: str
    description: str
    system_prompt: str
    allowed_tools: List[str]
    allowed_subagents: List[str] = field(default_factory=list)
    hidden: bool = False
    model: str = DEFAULT_MODEL


@dataclass
class SessionRecord:
    """
    Session 记录。

    参考 OpenCode child session 和 OpenClaw isolated sessions 的公开概念：
      - session 是隔离的上下文单元
      - child session 有显式 parent session
    """

    session_id: str
    agent_name: str
    parent_session_id: Optional[str]
    task: str
    messages: List[Dict[str, Any]] = field(default_factory=list)
    child_session_ids: List[str] = field(default_factory=list)


@dataclass
class AgentRunResult:
    session_id: str
    agent_name: str
    output: str
    tool_results: Dict[str, str] = field(default_factory=dict)
    child_session_ids: List[str] = field(default_factory=list)


class SubagentRuntime:
    """
    教学用 subagent runtime。

    设计目标：
      - 保留真实工程里公开可验证的几个关键运行时特征
      - 不伪装成任何项目的精确私有实现

    保留的特征：
      - primary agent 和 subagent 分层
      - subagent 独立 context
      - per-agent tool permissions
      - Task delegation primitive
      - child session tracking
      - explicit @subagent invocation

    有意简化的部分：
      - 不实现完整 UI / session navigation
      - 不实现 edit / patch / bash 全量权限面
      - 不实现规则文件、hooks、sandbox、MCP 注入等控制面
    """

    def __init__(self, client: OpenAI, workspace_root: Path, model: str = DEFAULT_MODEL):
        self.client = client
        self.workspace_root = workspace_root
        self.model = model
        self.specs = self._build_specs()
        self.sessions: Dict[str, SessionRecord] = {}
        self._session_counter = 0

    def _build_specs(self) -> Dict[str, AgentSpec]:
        """
        构建内置 agent 规格。

        参考公开文档的角色划分：
          - primary: build, plan
          - subagent: general, explore

        这里不加入 Scout，因为不同公开页面对内置集合有版本差异。
        为了避免文档漂移，实验只使用可以稳定验证的最小集合。
        """
        return {
            "build": AgentSpec(
                name="build",
                mode="primary",
                description="Primary development agent with broad task handling.",
                system_prompt=(
                    "You are the Build primary agent. "
                    "You handle the main coding conversation. "
                    "Use Task delegation when a side task should run in a separate context. "
                    "Prefer Explore for read-only codebase discovery. "
                    "Prefer General for complex multi-step side work. "
                    "Once you have enough evidence, stop using tools and answer directly. "
                    "Avoid rereading the same file range unless new evidence is needed."
                ),
                allowed_tools=["glob", "read", "grep"],
                allowed_subagents=["general", "explore"],
                model=self.model,
            ),
            "plan": AgentSpec(
                name="plan",
                mode="primary",
                description="Read-only planning and analysis agent.",
                system_prompt=(
                    "You are the Plan primary agent. "
                    "You analyze and explain without making changes. "
                    "Use Explore when you need focused codebase discovery in a child session. "
                    "After gathering enough evidence, produce a direct structured answer. "
                    "Do not keep calling tools if the answer can already be written."
                ),
                allowed_tools=["glob", "read", "grep"],
                allowed_subagents=["explore"],
                model=self.model,
            ),
            "general": AgentSpec(
                name="general",
                mode="subagent",
                description="General-purpose subagent for complex searches and multi-step side tasks.",
                system_prompt=(
                    "You are the General subagent. "
                    "Work independently in your own context and return only the result summary needed by the parent. "
                    "Prefer concise evidence-backed findings over long narrative."
                ),
                allowed_tools=["glob", "read", "grep"],
                allowed_subagents=[],
                model=self.model,
            ),
            "explore": AgentSpec(
                name="explore",
                mode="subagent",
                description="Fast read-only subagent for searching and understanding the codebase.",
                system_prompt=(
                    "You are the Explore subagent. "
                    "Focus on search, file discovery, and code understanding. "
                    "Do not attempt edits. Return concise findings. "
                    "Ignore generated files, caches, and build artifacts."
                ),
                allowed_tools=["glob", "read", "grep"],
                allowed_subagents=[],
                model=self.model,
            ),
        }

    def _new_session(self, agent_name: str, task: str, parent_session_id: Optional[str]) -> SessionRecord:
        self._session_counter += 1
        session_id = f"session-{self._session_counter:03d}"
        record = SessionRecord(
            session_id=session_id,
            agent_name=agent_name,
            parent_session_id=parent_session_id,
            task=task,
        )
        self.sessions[session_id] = record
        if parent_session_id:
            self.sessions[parent_session_id].child_session_ids.append(session_id)
        return record

    def run(self, agent_name: str, task: str, parent_session_id: Optional[str] = None, context_note: str = "") -> AgentRunResult:
        """
        运行一个 agent session。

        如果是 primary agent：
          - 它可以拥有 Task delegation primitive
        如果是 subagent：
          - 它运行在独立上下文里
          - 默认不再继续嵌套 subagent
        """
        spec = self.specs[agent_name]
        session = self._new_session(agent_name, task, parent_session_id)

        user_message = task
        if context_note:
            user_message += f"\n\nContext from parent session:\n{context_note}"

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": spec.system_prompt},
            {"role": "user", "content": user_message},
        ]
        session.messages = list(messages)

        tool_schemas = self._tool_schemas_for_agent(spec)
        tool_results: Dict[str, str] = {}

        for _ in range(6):
            response = self.client.chat.completions.create(
                model=spec.model,
                messages=messages,
                tools=tool_schemas,
                tool_choice="auto",
            )
            message = response.choices[0].message

            if not getattr(message, "tool_calls", None):
                output = message.content or ""
                session.messages.append({"role": "assistant", "content": output})
                return AgentRunResult(
                    session_id=session.session_id,
                    agent_name=agent_name,
                    output=output,
                    tool_results=tool_results,
                    child_session_ids=list(session.child_session_ids),
                )

            messages.append(self._assistant_message_for_history(message))

            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments or "{}")
                tool_output = self._execute_tool(spec, session, function_name, function_args)
                tool_results[function_name] = tool_output
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_output,
                    }
                )

        return AgentRunResult(
            session_id=session.session_id,
            agent_name=agent_name,
            output="Agent exceeded max rounds before final answer.",
            tool_results=tool_results,
            child_session_ids=list(session.child_session_ids),
        )

    def _tool_schemas_for_agent(self, spec: AgentSpec) -> List[Dict[str, Any]]:
        """
        构建当前 agent 可见的工具面。

        参考 OpenCode 的核心点：
          - permission 决定工具是否可见 / 可调用
          - permission.task 决定哪些 subagent 会出现在 Task 原语描述里
        """
        schemas = [TOOLS[name]["schema"] for name in spec.allowed_tools]

        if spec.allowed_subagents:
            descriptions = []
            for subagent_name in spec.allowed_subagents:
                child = self.specs[subagent_name]
                descriptions.append(f"{child.name}: {child.description}")

            schemas.append(
                {
                    "type": "function",
                    "function": {
                        "name": "task",
                        "description": (
                            "Delegate a side task to a subagent running in a separate child session. "
                            "Available subagents: " + " | ".join(descriptions)
                        ),
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "agent": {
                                    "type": "string",
                                    "enum": spec.allowed_subagents,
                                    "description": "Subagent to invoke",
                                },
                                "task": {
                                    "type": "string",
                                    "description": "Concrete side task for the subagent",
                                },
                                "context_note": {
                                    "type": "string",
                                    "description": "Short context summary for the child session",
                                },
                            },
                            "required": ["agent", "task"],
                        },
                    },
                }
            )

        return schemas

    def _execute_tool(self, spec: AgentSpec, session: SessionRecord, function_name: str, function_args: Dict[str, Any]) -> str:
        """
        执行工具或 delegation primitive。

        注意区分两类原语：
          1. 普通工具：glob / read / grep
          2. Task 原语：启动子 session，运行 subagent，再把结果摘要返回父 session
        """
        if function_name == "task":
            child_name = function_args["agent"]
            if child_name not in spec.allowed_subagents:
                return json.dumps({"error": f"{spec.name} cannot invoke subagent {child_name}"}, ensure_ascii=False)

            child_result = self.run(
                agent_name=child_name,
                task=function_args["task"],
                parent_session_id=session.session_id,
                context_note=function_args.get("context_note", ""),
            )
            return json.dumps(
                {
                    "delegated_to": child_name,
                    "child_session_id": child_result.session_id,
                    "child_output": child_result.output,
                },
                ensure_ascii=False,
            )

        if function_name not in spec.allowed_tools:
            return json.dumps({"error": f"tool not allowed for {spec.name}: {function_name}"}, ensure_ascii=False)

        tool_function = TOOLS[function_name]["function"]
        try:
            return tool_function(**function_args)
        except Exception as exc:
            return json.dumps({"error": str(exc)}, ensure_ascii=False)

    def _assistant_message_for_history(self, message: Any) -> Dict[str, Any]:
        """
        把 assistant tool call message 回填到历史里。

        这和 exp3_11b 是同一个闭环要求：
          - 先保留 assistant 的工具请求
          - 再追加 tool 结果
          - 下一轮模型才能理解“刚才发生了什么”
        """
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


def parse_explicit_subagent(task: str) -> tuple[Optional[str], str]:
    """
    支持类似 @explore 的显式 subagent 调用。

    这对应公开文档中“手动 @mention subagent”的使用方式。
    """
    task = task.strip()
    if not task.startswith("@"):
        return None, task
    parts = task.split(maxsplit=1)
    agent = parts[0][1:]
    remaining = parts[1] if len(parts) > 1 else ""
    return agent, remaining


def decode_tool_results(tool_results: Dict[str, str]) -> Dict[str, Any]:
    """
    把工具返回的 JSON 字符串尽量还原成结构化对象，方便终端阅读。

    当前工具全部返回字符串，这是为了兼容 tool message 的 content 字段。
    展示层不应该再把这些字符串原封不动嵌套打印。
    """
    decoded: Dict[str, Any] = {}
    for name, value in tool_results.items():
        try:
            decoded[name] = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            decoded[name] = value
    return decoded


def print_session_tree(runtime: SubagentRuntime, root_session_id: str, indent: int = 0) -> None:
    """输出父子 session 树，帮助理解 child session 结构。"""
    record = runtime.sessions[root_session_id]
    prefix = " " * indent
    print(f"{prefix}- {record.session_id} [{record.agent_name}] task={record.task}")
    for child_id in record.child_session_ids:
        print_session_tree(runtime, child_id, indent + 2)


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenAI SDK 版主 Agent + Subagent Runtime 实验")
    parser.add_argument("--agent", choices=["build", "plan"], default="build", help="Primary agent to start from")
    parser.add_argument(
        "--task",
        default="找出 exp3_11b 里负责多 Agent 调度的核心函数，并总结它们的关系。",
        help="Task for the primary agent. Supports explicit subagent invocation like @explore ...",
    )
    args = parser.parse_args()

    client = create_client()
    runtime = SubagentRuntime(client=client, workspace_root=WORKSPACE_ROOT, model=DEFAULT_MODEL)

    explicit_subagent, normalized_task = parse_explicit_subagent(args.task)
    if explicit_subagent:
        if explicit_subagent not in runtime.specs or runtime.specs[explicit_subagent].mode != "subagent":
            raise ValueError(f"Unknown subagent in @mention: {explicit_subagent}")
        result = runtime.run(explicit_subagent, normalized_task)
    else:
        result = runtime.run(args.agent, normalized_task)

    print("\n" + "=" * 60)
    print("Final Output")
    print("=" * 60)
    print(result.output)

    print("\n" + "=" * 60)
    print("Session Tree")
    print("=" * 60)
    print_session_tree(runtime, result.session_id)

    print("\n" + "=" * 60)
    print("Tool Results")
    print("=" * 60)
    print(json.dumps(decode_tool_results(result.tool_results), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
