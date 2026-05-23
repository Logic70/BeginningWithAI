"""
实验 3.11h: Context / Memory Runtime

目标：
  - 学习 Claude Code Memory 与上下文管理的分层。
  - 区分：
      transcript: 完整会话流水账。
      context: 当前发给模型的工作上下文。
      compacted summary: 为了继续任务压缩出来的摘要。
      memory: 跨会话保留的稳定事实。
  - 演示 PreCompact / PostCompact、token budget、MEMORY.md 索引和 topic memory 文件。

参考边界：
  - Claude Code Memory 文档：项目记忆、索引、启动加载预算、按需读取。
  - Claude Code Hooks 文档：PreCompact / PostCompact。
  - pengchengneo/Claude-Code：CONTEXT_COLLAPSE、REACTIVE_COMPACT、HISTORY_SNIP、TOKEN_BUDGET、KAIROS / Dream。

运行方式：
  ./venv/bin/python experiments/phase3/exp3_11h_context_memory_runtime_openai.py --help
  ./venv/bin/python experiments/phase3/exp3_11h_context_memory_runtime_openai.py --scripted
"""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_STATE_DIR = Path(tempfile.gettempdir()) / "beginningwithai-exp3-11h"


def estimate_tokens(text: str) -> int:
    """粗略 token 估算，教学实验不引入 tokenizer 依赖。"""
    return max(1, len(text) // 4)


@dataclass
class Message:
    role: str
    content: str


@dataclass
class CompactResult:
    before_tokens: int
    after_tokens: int
    summary: str


@dataclass
class MemoryFact:
    topic: str
    fact: str
    source: str


class TranscriptStore:
    """完整 transcript 落盘，不等于当前上下文。"""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, message: Message) -> None:
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps({"role": message.role, "content": message.content}, ensure_ascii=False) + "\n")

    def read_all(self) -> List[Dict[str, str]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]


class MemoryStore:
    """
    项目 memory store。

    MEMORY.md 是索引，不保存全部事实。
    具体事实按 topic 写到 topics/*.md，模拟按需读取。
    """

    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.topics_dir = self.root / "topics"
        self.topics_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / "MEMORY.md"
        if not self.index_path.exists():
            self.index_path.write_text("# MEMORY.md\n\n## Topics\n", encoding="utf-8")

    def add_fact(self, fact: MemoryFact) -> None:
        topic_slug = self._slug(fact.topic)
        topic_path = self.topics_dir / f"{topic_slug}.md"
        existing = topic_path.read_text(encoding="utf-8") if topic_path.exists() else f"# {fact.topic}\n\n"
        line = f"- {fact.fact} (source: {fact.source})\n"
        if line not in existing:
            topic_path.write_text(existing + line, encoding="utf-8")
        self._ensure_index_entry(fact.topic, topic_path)

    def startup_load(self, max_lines: int = 200, max_chars: int = 25_000) -> str:
        text = self.index_path.read_text(encoding="utf-8")
        lines = text.splitlines()[:max_lines]
        return "\n".join(lines)[:max_chars]

    def read_topic(self, topic: str) -> str:
        path = self.topics_dir / f"{self._slug(topic)}.md"
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def _ensure_index_entry(self, topic: str, topic_path: Path) -> None:
        rel = topic_path.relative_to(self.root)
        entry = f"- [{topic}]({rel})"
        text = self.index_path.read_text(encoding="utf-8")
        if entry not in text:
            self.index_path.write_text(text.rstrip() + "\n" + entry + "\n", encoding="utf-8")

    def _slug(self, topic: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", topic.strip().lower()).strip("-")
        return slug or "general"


class ContextMemoryRuntime:
    """教学用 context / memory runtime。"""

    def __init__(self, state_dir: Path = DEFAULT_STATE_DIR, token_budget: int = 360):
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.transcript = TranscriptStore(self.state_dir / "transcript.jsonl")
        self.memory = MemoryStore(self.state_dir / "memory")
        self.events_path = self.state_dir / "events.jsonl"
        self.context: List[Message] = []
        self.token_budget = token_budget

    def add_message(self, role: str, content: str) -> None:
        message = Message(role=role, content=content)
        self.context.append(message)
        self.transcript.append(message)

    def context_tokens(self) -> int:
        return sum(estimate_tokens(message.content) for message in self.context)

    def maybe_compact(self) -> Dict[str, Any]:
        if self.context_tokens() <= self.token_budget:
            return {"compacted": False, "tokens": self.context_tokens()}
        result = self.compact()
        return {
            "compacted": True,
            "before_tokens": result.before_tokens,
            "after_tokens": result.after_tokens,
            "summary": result.summary,
        }

    def compact(self) -> CompactResult:
        before = self.context_tokens()
        self._event("PreCompact", {"message_count": len(self.context), "tokens": before})
        important = []
        for message in self.context[-8:]:
            if message.role in {"user", "assistant"}:
                important.append(f"{message.role}: {message.content[:220]}")
        summary = "\n".join(important)
        self.context = [Message(role="system", content="Compacted context summary:\n" + summary)]
        after = self.context_tokens()
        self._event("PostCompact", {"message_count": len(self.context), "tokens": after})
        return CompactResult(before_tokens=before, after_tokens=after, summary=summary)

    def extract_memory(self, task_result: str, source: str) -> List[MemoryFact]:
        """
        从任务结果中抽取稳定事实。

        教学规则很保守：只抽取显式前缀，避免把临时对话误写成长期记忆。
        """
        facts: List[MemoryFact] = []
        patterns = [
            (r"模型默认使用\s*`?([\w.-]+)`?", "model-config", "Default model is {value}."),
            (r"WSL\s*下使用\s*`?(\./venv/bin/python)`?", "environment", "Use {value} for Python commands in WSL."),
            (r"Agent Team\s*使用\s*(task list\s*\+\s*mailbox)", "agent-team", "Agent Team uses {value} for collaboration."),
        ]
        for pattern, topic, template in patterns:
            match = re.search(pattern, task_result, re.IGNORECASE)
            if match:
                facts.append(MemoryFact(topic=topic, fact=template.format(value=match.group(1)), source=source))
        for fact in facts:
            self.memory.add_fact(fact)
        return facts

    def run_scripted_demo(self) -> Dict[str, Any]:
        self.add_message("system", "You are a code agent runtime teaching assistant.")
        for index in range(12):
            self.add_message(
                "user",
                (
                    f"Round {index}: 请分析 Claude Code runtime 中 hook、context、memory 的区别。"
                    "这是一段较长的上下文，用来触发 token budget 和 compact 行为。"
                ),
            )
            self.add_message(
                "assistant",
                (
                    f"Round {index}: hook 属于控制面，context 是当前模型输入，memory 是跨会话稳定事实。"
                    "如果上下文超过预算，需要 compact，但 compact 不等于 memory extraction。"
                ),
            )
        compact_result = self.maybe_compact()
        task_result = (
            "模型默认使用 `deepseek-v4-pro`。\n"
            "WSL 下使用 `./venv/bin/python`。\n"
            "Agent Team 使用 task list + mailbox。\n"
            "临时观察：本次输出很长，但这不应该成为长期记忆。"
        )
        facts = self.extract_memory(task_result, source="scripted-demo")
        startup_memory = self.memory.startup_load()
        agent_team_memory = self.memory.read_topic("agent-team")
        return {
            "state_dir": str(self.state_dir),
            "transcript": str(self.transcript.path),
            "events": str(self.events_path),
            "compact": compact_result,
            "facts_extracted": [fact.__dict__ for fact in facts],
            "memory_index": str(self.memory.index_path),
            "startup_memory": startup_memory,
            "agent_team_memory": agent_team_memory,
            "transcript_line_count": len(self.transcript.read_all()),
            "current_context_messages": [message.__dict__ for message in self.context],
        }

    def _event(self, event: str, payload: Dict[str, Any]) -> None:
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps({"event": event, "payload": payload}, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Context / Memory Runtime 教学实验")
    parser.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR), help="Directory for transcript and memory files")
    parser.add_argument("--token-budget", type=int, default=360, help="Approximate context token budget")
    parser.add_argument("--scripted", action="store_true", help="Run deterministic context/memory demo")
    args = parser.parse_args()

    runtime = ContextMemoryRuntime(state_dir=Path(args.state_dir), token_budget=args.token_budget)
    result = runtime.run_scripted_demo()

    print("\n" + "=" * 60)
    print("Context / Memory Result")
    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
