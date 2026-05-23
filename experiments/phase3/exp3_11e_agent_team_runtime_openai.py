"""
实验 3.11e: OpenAI SDK 版 Agent Team Runtime

目标：
  - 在 3.11c subagent 和 3.11d coordinator/worker 之后，继续学习 Agent Team。
  - 重点实现 Claude Code Agent Teams 官方文档中的核心结构：
      team lead / teammates / shared task list / mailbox / independent context。
  - 展示 Agent Team 和 Subagent 的区别：
      subagent 只把结果回给调用者；
      team teammate 可以看到共享任务列表，并能直接给其他 teammate 发消息。

参考边界：
  1. Claude Code Agent Teams 官方文档
     - team lead 创建 team、spawn teammates、协调工作
     - teammates 是独立 Claude Code instances，各自有 context window
     - shared task list 有 pending / in progress / completed 状态
     - mailbox 支持 teammate 之间直接通信
     - task claiming 需要避免多人同时领取同一任务
  2. pengchengneo/Claude-Code 源码还原材料
     - 关注 team/task 本地状态、team config、mailbox、teammate lifecycle

这份实验是教学原型，不实现真实并发进程、tmux pane、文件锁和 UI。
它保留核心语义：独立 teammate session + shared task list + mailbox。

运行方式：
  python experiments/phase3/exp3_11e_agent_team_runtime_openai.py --help
  ./venv/bin/python experiments/phase3/exp3_11e_agent_team_runtime_openai.py --scripted --max-rounds 4
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

from exp3_11d_coordinator_runtime_openai import (
    DEFAULT_MODEL,
    WORKER_TOOLS,
    WORKSPACE_ROOT,
    create_client,
    decode_tool_results,
)


load_dotenv(Path(__file__).parent.parent.parent / ".env")


DEFAULT_STATE_DIR = Path(tempfile.gettempdir()) / "beginningwithai-exp3-11e"


@dataclass
class TeamMember:
    """Team teammate 配置。"""

    name: str
    agent_type: str
    system_prompt: str
    allowed_tools: List[str]
    model: str = DEFAULT_MODEL


@dataclass
class TeamTask:
    """共享任务列表中的任务。"""

    task_id: str
    title: str
    description: str
    status: str = "pending"
    assignee: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    result: str = ""


@dataclass
class MailboxMessage:
    """teammate 之间的直接消息。"""

    message_id: str
    sender: str
    recipient: str
    body: str
    task_id: Optional[str] = None


@dataclass
class TeamRunResult:
    member: str
    task_id: str
    output: str
    tool_results: Dict[str, str]


class TeamStore:
    """
    本地 team state。

    对应官方文档里的本地 team config、task list 和 mailbox。
    """

    def __init__(self, team_name: str, state_dir: Path):
        self.team_name = team_name
        self.team_dir = state_dir / team_name
        self.team_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.team_dir / "config.json"
        self.tasks_path = self.team_dir / "tasks.json"
        self.mailbox_path = self.team_dir / "mailbox.json"
        self.members: Dict[str, TeamMember] = {}
        self.tasks: Dict[str, TeamTask] = {}
        self.mailbox: List[MailboxMessage] = []
        self._task_counter = 0
        self._message_counter = 0

    def add_member(self, member: TeamMember) -> None:
        self.members[member.name] = member
        self.save()

    def create_task(
        self,
        title: str,
        description: str,
        assignee: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
    ) -> TeamTask:
        self._task_counter += 1
        task = TeamTask(
            task_id=f"team-task-{self._task_counter:03d}",
            title=title,
            description=description,
            assignee=assignee,
            dependencies=dependencies or [],
        )
        self.tasks[task.task_id] = task
        self.save()
        return task

    def send_message(self, sender: str, recipient: str, body: str, task_id: Optional[str] = None) -> MailboxMessage:
        self._message_counter += 1
        message = MailboxMessage(
            message_id=f"mail-{self._message_counter:03d}",
            sender=sender,
            recipient=recipient,
            body=body,
            task_id=task_id,
        )
        self.mailbox.append(message)
        self.save()
        return message

    def save(self) -> None:
        self.config_path.write_text(
            json.dumps(
                {
                    "team_name": self.team_name,
                    "members": [
                        {"name": member.name, "agent_type": member.agent_type, "model": member.model}
                        for member in self.members.values()
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        self.tasks_path.write_text(
            json.dumps(
                {
                    task_id: {
                        "task_id": task.task_id,
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "assignee": task.assignee,
                        "dependencies": task.dependencies,
                        "result": task.result,
                    }
                    for task_id, task in self.tasks.items()
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        self.mailbox_path.write_text(
            json.dumps(
                [
                    {
                        "message_id": message.message_id,
                        "sender": message.sender,
                        "recipient": message.recipient,
                        "task_id": message.task_id,
                        "body": message.body,
                    }
                    for message in self.mailbox
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )


class AgentTeamRuntime:
    """
    教学用 Agent Team runtime。

    与 3.11c 的区别：
      - 3.11c 是 parent -> subagent -> parent result。
      - 3.11e 是 teammates 共享任务列表，并能直接互相通信。

    与 3.11d 的区别：
      - 3.11d 是 Coordinator 派 Worker，Worker 结果主要回 Coordinator。
      - 3.11e 让 teammate 拥有 team tools：list_tasks / claim_task / send_message / read_mailbox / complete_task。
    """

    def __init__(
        self,
        client: OpenAI,
        team_name: str = "phase3-agent-team",
        state_dir: Path = DEFAULT_STATE_DIR,
        model: str = DEFAULT_MODEL,
        max_rounds: int = 4,
    ):
        self.client = client
        self.model = model
        self.max_rounds = max_rounds
        self.store = TeamStore(team_name=team_name, state_dir=state_dir)
        self._build_default_team()

    def _build_default_team(self) -> None:
        members = [
            TeamMember(
                name="architect",
                agent_type="architecture-reviewer",
                system_prompt=(
                    "You are the Architect teammate. Focus on runtime structure, data flow, "
                    "and architectural tradeoffs. Use the shared task list and mailbox. "
                    "When you finish, call complete_task or return a concise final answer."
                ),
                allowed_tools=["glob", "read", "grep", "list_tasks", "send_message", "read_mailbox", "complete_task"],
                model=self.model,
            ),
            TeamMember(
                name="critic",
                agent_type="design-critic",
                system_prompt=(
                    "You are the Critic teammate. Challenge assumptions, look for failure modes, "
                    "and send concise messages to other teammates when useful. "
                    "When you finish, call complete_task or return a concise final answer."
                ),
                allowed_tools=["glob", "read", "grep", "list_tasks", "send_message", "read_mailbox", "complete_task"],
                model=self.model,
            ),
            TeamMember(
                name="verifier",
                agent_type="verification-runner",
                system_prompt=(
                    "You are the Verifier teammate. Run safe verification commands and report exact results. "
                    "Use shell only for safe read-only or verification commands. "
                    "When you finish, call complete_task or return a concise final answer."
                ),
                allowed_tools=["shell", "read", "grep", "list_tasks", "send_message", "read_mailbox", "complete_task"],
                model=self.model,
            ),
        ]
        for member in members:
            self.store.add_member(member)

    def run_scripted_demo(self, user_task: str) -> str:
        """
        用固定 lead 策略创建任务并运行 teammates。

        这不是为了复刻真实 lead 的智能规划，而是为了稳定演示 team runtime。
        """
        architecture_task = self.store.create_task(
            title="Architecture review",
            description=(
                "只阅读 experiments/phase3/exp3_11d_coordinator_runtime_openai.py。"
                "总结 Agent Team 之前的 Coordinator / Worker 结构：Coordinator 工具有哪些，Worker 工具有哪些，TaskStore 做什么。"
                "完成前给 critic 发一条消息，指出你认为最值得质疑的设计点。"
            ),
            assignee="architect",
        )
        critique_task = self.store.create_task(
            title="Failure-mode review",
            description=(
                "阅读 mailbox 和 tasks，结合 architect 的消息，指出 Agent Team runtime 最容易出问题的 3 个点。"
                "必要时读取 experiments/phase3/exp3_11d_coordinator_runtime_openai.py。"
            ),
            assignee="critic",
            dependencies=[architecture_task.task_id],
        )
        verification_task = self.store.create_task(
            title="CLI verification",
            description=(
                "运行 ./venv/bin/python experiments/phase3/exp3_11e_agent_team_runtime_openai.py --help，"
                "报告 returncode 和关键输出。"
            ),
            assignee="verifier",
        )

        results = [
            self.run_teammate("architect", architecture_task.task_id),
        ]
        self._ensure_architect_message_for_critic(architecture_task.task_id)
        results.append(self.run_teammate("critic", critique_task.task_id))
        results.append(self.run_teammate("verifier", verification_task.task_id))
        return self._lead_synthesis(user_task, results)

    def run_teammate(self, member_name: str, task_id: str) -> TeamRunResult:
        if member_name not in self.store.members:
            raise ValueError(f"unknown teammate: {member_name}")
        if task_id not in self.store.tasks:
            raise ValueError(f"unknown task: {task_id}")

        member = self.store.members[member_name]
        task = self.store.tasks[task_id]
        if task.assignee and task.assignee != member_name:
            raise ValueError(f"task {task_id} is assigned to {task.assignee}, not {member_name}")
        if not self._dependencies_completed(task):
            task.status = "blocked"
            self.store.save()
            return TeamRunResult(member_name, task_id, "Task is blocked by dependencies.", {})

        task.assignee = member_name
        task.status = "in_progress"
        self.store.save()

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": member.system_prompt},
            {"role": "user", "content": self._teammate_user_prompt(member, task)},
        ]
        tool_results: Dict[str, str] = {}
        tool_schemas = self._tool_schemas_for_member(member)

        for _ in range(self.max_rounds):
            response = self.client.chat.completions.create(
                model=member.model,
                messages=messages,
                tools=tool_schemas,
                tool_choice="auto",
            )
            message = response.choices[0].message

            if not getattr(message, "tool_calls", None):
                output = message.content or ""
                if task.status != "completed":
                    self._complete_task(member_name, task_id, output)
                return TeamRunResult(member_name, task_id, output, tool_results)

            messages.append(self._assistant_message_for_history(message))
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments or "{}")
                tool_output = self._execute_tool(member, task, function_name, function_args)
                tool_results[function_name] = tool_output
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_output,
                    }
                )

        fallback = self._fallback_result(member_name, task_id, tool_results)
        if task.status != "completed":
            self._complete_task(member_name, task_id, fallback)
        return TeamRunResult(member_name, task_id, fallback, tool_results)

    def _execute_tool(self, member: TeamMember, task: TeamTask, function_name: str, function_args: Dict[str, Any]) -> str:
        if function_name not in member.allowed_tools:
            return json.dumps({"error": f"tool not allowed for {member.name}: {function_name}"}, ensure_ascii=False)

        if function_name in WORKER_TOOLS:
            if function_name == "shell":
                function_args["cwd"] = "."
            tool_function: Callable[..., str] = WORKER_TOOLS[function_name]["function"]
            try:
                return tool_function(**function_args)
            except Exception as exc:
                return json.dumps({"error": str(exc)}, ensure_ascii=False)

        if function_name == "list_tasks":
            return self._list_tasks()

        if function_name == "send_message":
            message = self.store.send_message(
                sender=member.name,
                recipient=function_args["recipient"],
                body=function_args["body"],
                task_id=function_args.get("task_id", task.task_id),
            )
            return json.dumps({"message_id": message.message_id, "recipient": message.recipient}, ensure_ascii=False)

        if function_name == "read_mailbox":
            recipient = member.name
            messages = [
                {
                    "message_id": message.message_id,
                    "sender": message.sender,
                    "recipient": message.recipient,
                    "task_id": message.task_id,
                    "body": message.body,
                }
                for message in self.store.mailbox
                if message.recipient == recipient
            ]
            return json.dumps({"recipient": recipient, "messages": messages}, ensure_ascii=False)

        if function_name == "claim_task":
            claimed = self._claim_task(member.name, function_args.get("task_id"))
            return json.dumps(claimed, ensure_ascii=False)

        if function_name == "complete_task":
            result = function_args["result"]
            self._complete_task(member.name, function_args.get("task_id", task.task_id), result)
            return json.dumps({"task_id": function_args.get("task_id", task.task_id), "status": "completed"}, ensure_ascii=False)

        return json.dumps({"error": f"unknown team tool: {function_name}"}, ensure_ascii=False)

    def _tool_schemas_for_member(self, member: TeamMember) -> List[Dict[str, Any]]:
        schemas: List[Dict[str, Any]] = []
        for name in member.allowed_tools:
            if name in WORKER_TOOLS:
                schemas.append(WORKER_TOOLS[name]["schema"])

        if "list_tasks" in member.allowed_tools:
            schemas.append(
                {
                    "type": "function",
                    "function": {
                        "name": "list_tasks",
                        "description": "Read the shared team task list.",
                        "parameters": {"type": "object", "properties": {}},
                    },
                }
            )
        if "claim_task" in member.allowed_tools:
            schemas.append(
                {
                    "type": "function",
                    "function": {
                        "name": "claim_task",
                        "description": "Claim an unassigned, unblocked task.",
                        "parameters": {
                            "type": "object",
                            "properties": {"task_id": {"type": "string"}},
                        },
                    },
                }
            )
        if "send_message" in member.allowed_tools:
            schemas.append(
                {
                    "type": "function",
                    "function": {
                        "name": "send_message",
                        "description": "Send a direct mailbox message to another teammate.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "recipient": {"type": "string", "enum": list(self.store.members)},
                                "body": {"type": "string"},
                                "task_id": {"type": "string"},
                            },
                            "required": ["recipient", "body"],
                        },
                    },
                }
            )
        if "read_mailbox" in member.allowed_tools:
            schemas.append(
                {
                    "type": "function",
                    "function": {
                        "name": "read_mailbox",
                        "description": "Read mailbox messages for a teammate.",
                        "parameters": {
                            "type": "object",
                            "properties": {"recipient": {"type": "string"}},
                        },
                    },
                }
            )
        if "complete_task" in member.allowed_tools:
            schemas.append(
                {
                    "type": "function",
                    "function": {
                        "name": "complete_task",
                        "description": "Mark a team task completed with its result.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {"type": "string"},
                                "result": {"type": "string"},
                            },
                            "required": ["result"],
                        },
                    },
                }
            )
        return schemas

    def _claim_task(self, member_name: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        candidates = [self.store.tasks[task_id]] if task_id and task_id in self.store.tasks else self.store.tasks.values()
        for task in candidates:
            if task.status != "pending":
                continue
            if task.assignee not in (None, member_name):
                continue
            if not self._dependencies_completed(task):
                continue
            task.assignee = member_name
            task.status = "in_progress"
            self.store.save()
            return {"claimed": True, "task_id": task.task_id, "title": task.title}
        return {"claimed": False}

    def _complete_task(self, member_name: str, task_id: str, result: str) -> None:
        task = self.store.tasks[task_id]
        task.assignee = member_name
        task.status = "completed"
        task.result = result
        self.store.send_message(
            sender=member_name,
            recipient="lead",
            body=f"Task {task_id} completed by {member_name}: {result[:500]}",
            task_id=task_id,
        )
        self.store.save()

    def _dependencies_completed(self, task: TeamTask) -> bool:
        return all(self.store.tasks[dependency].status == "completed" for dependency in task.dependencies)

    def _list_tasks(self) -> str:
        return json.dumps(
            {
                task_id: {
                    "title": task.title,
                    "status": task.status,
                    "assignee": task.assignee,
                    "dependencies": task.dependencies,
                }
                for task_id, task in self.store.tasks.items()
            },
            ensure_ascii=False,
        )

    def _teammate_user_prompt(self, member: TeamMember, task: TeamTask) -> str:
        return (
            f"Team: {self.store.team_name}\n"
            f"You are teammate: {member.name} ({member.agent_type})\n"
            f"Task id: {task.task_id}\n"
            f"Title: {task.title}\n"
            f"Description: {task.description}\n\n"
            f"Shared tasks:\n{self._list_tasks()}\n\n"
            f"Your mailbox recipient name is {member.name}. "
            f"When reading mailbox, the runtime will read only your own inbox. "
            "When running shell, use workspace root cwd='.'. "
            "Use mailbox tools when direct teammate communication is useful. "
            "Complete the task with complete_task or return a concise final answer."
        )

    def _lead_synthesis(self, user_task: str, results: List[TeamRunResult]) -> str:
        sections = [
            "Agent Team scripted synthesis",
            "",
            f"User task: {user_task}",
            "",
            f"Team config: {self.store.config_path}",
            f"Task list: {self.store.tasks_path}",
            f"Mailbox: {self.store.mailbox_path}",
            "",
            "Completed teammate results:",
        ]
        for result in results:
            task = self.store.tasks[result.task_id]
            sections.append(f"- {result.member} / {task.title} / {task.status}: {task.result[:600]}")
        sections.append("")
        sections.append("Mailbox messages:")
        for message in self.store.mailbox:
            sections.append(f"- {message.message_id}: {message.sender} -> {message.recipient}: {message.body[:300]}")
        return "\n".join(sections)

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

    def _ensure_architect_message_for_critic(self, task_id: str) -> None:
        """
        教学兜底：确保 scripted demo 能稳定展示 teammate -> teammate mailbox。

        模型可能完成了结构分析但忘记调用 send_message。真实系统会通过 hook
        或 lead 提醒处理；这里直接补一条最小消息，保证后续 critic 能读到。
        """
        exists = any(
            message.sender == "architect" and message.recipient == "critic" and message.task_id == task_id
            for message in self.store.mailbox
        )
        if exists:
            return
        task = self.store.tasks[task_id]
        self.store.send_message(
            sender="architect",
            recipient="critic",
            task_id=task_id,
            body=(
                "Architect note for critic: review whether the Team runtime should rely on model-initiated "
                "complete_task/send_message calls, or whether runtime fallbacks and hooks should enforce completion."
                f" Architecture task result starts with: {task.result[:240]}"
            ),
        )

    def _fallback_result(self, member_name: str, task_id: str, tool_results: Dict[str, str]) -> str:
        decoded = decode_tool_results(tool_results)
        return (
            f"{member_name} reached max rounds after collecting evidence for {task_id}.\n"
            f"Evidence:\n{json.dumps(decoded, ensure_ascii=False, indent=2)[:3000]}"
        )


def print_team_state(runtime: AgentTeamRuntime) -> None:
    print("\n" + "=" * 60)
    print("Team State")
    print("=" * 60)
    print(f"config={runtime.store.config_path}")
    print(f"tasks={runtime.store.tasks_path}")
    print(f"mailbox={runtime.store.mailbox_path}")
    print("\nTasks:")
    for task in runtime.store.tasks.values():
        print(f"- {task.task_id} [{task.status}] assignee={task.assignee} title={task.title}")
    print("\nMailbox:")
    for message in runtime.store.mailbox:
        print(f"- {message.message_id}: {message.sender} -> {message.recipient}: {message.body[:180]}")


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenAI SDK 版 Agent Team Runtime 实验")
    parser.add_argument(
        "--task",
        default="演示 Agent Team：多个 teammate 通过 shared task list 和 mailbox 协作分析 3.11d。",
        help="User task for the team lead.",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenAI-compatible model name")
    parser.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR), help="Directory for team state")
    parser.add_argument("--team-name", default="phase3-agent-team", help="Team name for local state")
    parser.add_argument("--max-rounds", type=int, default=4, help="Max model/tool rounds per teammate")
    parser.add_argument("--scripted", action="store_true", help="Run a deterministic team lead plan")
    args = parser.parse_args()

    runtime = AgentTeamRuntime(
        client=create_client(),
        team_name=args.team_name,
        state_dir=Path(args.state_dir),
        model=args.model,
        max_rounds=args.max_rounds,
    )

    if args.scripted:
        output = runtime.run_scripted_demo(args.task)
    else:
        output = runtime.run_scripted_demo(args.task)

    print("\n" + "=" * 60)
    print("Final Output")
    print("=" * 60)
    print(output)
    print_team_state(runtime)


if __name__ == "__main__":
    main()
