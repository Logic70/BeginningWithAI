"""
实验 3.11g: Instruction / Permission Runtime

目标：
  - 学习 Claude Code 中 CLAUDE.md、rules、settings / permissions 的分层。
  - 明确区分：
      instruction loading: 告诉 Agent 应该怎么做。
      permission enforcement: 决定工具是否真的允许执行。
  - 用确定性 demo 验证：即使 CLAUDE.md 里写了“不要读 .env”，真正阻断仍来自 permissions.deny。

参考边界：
  - Claude Code Memory 文档：CLAUDE.md、imports、project/local memory。
  - Claude Code Settings 文档：permissions.deny 等配置。
  - Claude Code Subagents 文档：不同 agent/subagent 可以有不同上下文和工具权限。
  - pengchengneo/Claude-Code：prompt assembly、rules、permission mode 的工程线索。

运行方式：
  ./venv/bin/python experiments/phase3/exp3_11g_instruction_permission_runtime_openai.py --help
  ./venv/bin/python experiments/phase3/exp3_11g_instruction_permission_runtime_openai.py --scripted
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_DEMO_ROOT = Path(tempfile.gettempdir()) / "beginningwithai-exp3-11g-workspace"


@dataclass
class LoadedInstructions:
    """一次 instruction assembly 的结果。"""

    cwd: Path
    target_path: Optional[str]
    files_loaded: List[str] = field(default_factory=list)
    sections: List[str] = field(default_factory=list)
    rules_loaded: List[str] = field(default_factory=list)
    settings_loaded: List[str] = field(default_factory=list)

    @property
    def prompt_context(self) -> str:
        return "\n\n".join(self.sections)


class PermissionDenied(Exception):
    pass


class DemoWorkspace:
    """创建最小 CLAUDE.md / rules / settings fixture。"""

    def __init__(self, root: Path):
        self.root = root

    def create(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "experiments/phase3").mkdir(parents=True, exist_ok=True)
        (self.root / ".claude/rules").mkdir(parents=True, exist_ok=True)
        (self.root / "secrets").mkdir(parents=True, exist_ok=True)

        (self.root / "AGENTS.md").write_text(
            "# AGENTS.md\n\n"
            "- Use project conventions.\n"
            "- Prefer ./venv/bin/python in WSL.\n",
            encoding="utf-8",
        )
        (self.root / "CLAUDE.md").write_text(
            "# Project instructions\n\n"
            "@AGENTS.md\n\n"
            "- Never intentionally read `.env` or `secrets/**`.\n"
            "- Explain code with file paths and line numbers.\n",
            encoding="utf-8",
        )
        (self.root / "CLAUDE.local.md").write_text(
            "# Local instructions\n\n"
            "- This machine uses OpenCode Go compatible OpenAI API.\n",
            encoding="utf-8",
        )
        (self.root / ".claude/rules/python.md").write_text(
            "---\n"
            "paths: [\"experiments/**/*.py\"]\n"
            "---\n\n"
            "# Python rule\n\n"
            "- Use py_compile before claiming Python code is valid.\n"
            "- Keep runnable teaching scripts deterministic by default.\n",
            encoding="utf-8",
        )
        (self.root / ".claude/rules/docs.md").write_text(
            "---\n"
            "paths: [\"docs/**/*.md\"]\n"
            "---\n\n"
            "# Docs rule\n\n"
            "- Keep Chinese teaching docs aligned with actual experiment files.\n",
            encoding="utf-8",
        )
        (self.root / ".claude/settings.json").write_text(
            json.dumps(
                {
                    "permissions": {
                        "deny": [
                            "Read(.env)",
                            "Read(.env.*)",
                            "Read(secrets/**)",
                            "Read(**/credentials.json)",
                        ]
                    }
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (self.root / ".env").write_text("OPENAI_API_KEY=should-not-be-read\n", encoding="utf-8")
        (self.root / "secrets/token.txt").write_text("secret-token\n", encoding="utf-8")
        (self.root / "experiments/phase3/demo_agent.py").write_text(
            "def run_agent():\n"
            "    return 'ok'\n",
            encoding="utf-8",
        )
        (self.root / "docs_demo.md").write_text("# Demo docs\n", encoding="utf-8")


class InstructionPermissionRuntime:
    """
    教学用 instruction / permission runtime。

    这里有意不调用模型，因为本实验的重点是 prompt assembly 和 permission gate。
    """

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()
        self.events: List[Dict[str, Any]] = []
        self.settings = self._load_settings()

    def assemble(self, cwd: str = ".", target_path: Optional[str] = None, include_local: bool = True) -> LoadedInstructions:
        cwd_path = self._normalize(cwd)
        loaded = LoadedInstructions(cwd=cwd_path, target_path=target_path)

        for name in ("CLAUDE.md", "CLAUDE.local.md"):
            if name == "CLAUDE.local.md" and not include_local:
                continue
            path = self.workspace_root / name
            if path.exists():
                loaded.files_loaded.append(self._rel(path))
                loaded.sections.append(self._read_with_imports(path, seen=[]))

        if target_path:
            for rule_path in sorted((self.workspace_root / ".claude/rules").glob("*.md")):
                if self._rule_matches(rule_path, target_path):
                    loaded.rules_loaded.append(self._rel(rule_path))
                    loaded.sections.append(rule_path.read_text(encoding="utf-8"))

        settings_path = self.workspace_root / ".claude/settings.json"
        if settings_path.exists():
            loaded.settings_loaded.append(self._rel(settings_path))

        self.events.append(
            {
                "event": "InstructionsLoaded",
                "files_loaded": loaded.files_loaded,
                "rules_loaded": loaded.rules_loaded,
                "settings_loaded": loaded.settings_loaded,
            }
        )
        return loaded

    def read_file(self, path: str, agent_name: str = "build") -> Dict[str, Any]:
        self._enforce_read_permission(path, agent_name)
        target = self._normalize(path)
        return {"path": self._rel(target), "content": target.read_text(encoding="utf-8", errors="ignore")}

    def demo(self) -> Dict[str, Any]:
        python_context = self.assemble(target_path="experiments/phase3/demo_agent.py")
        allowed_read = self.read_file("experiments/phase3/demo_agent.py")
        denied_env = self._attempt_read(".env")
        denied_secret = self._attempt_read("secrets/token.txt")

        explore_context = self.assemble(target_path="experiments/phase3/demo_agent.py", include_local=False)
        return {
            "workspace": str(self.workspace_root),
            "prompt_context_preview": python_context.prompt_context[:1200],
            "files_loaded": python_context.files_loaded,
            "rules_loaded": python_context.rules_loaded,
            "settings_loaded": python_context.settings_loaded,
            "allowed_read": {"path": allowed_read["path"], "content": allowed_read["content"]},
            "denied_env": denied_env,
            "denied_secret": denied_secret,
            "explore_context_files_loaded": explore_context.files_loaded,
            "explore_context_includes_local": any(path.endswith("CLAUDE.local.md") for path in explore_context.files_loaded),
            "events": self.events,
        }

    def _load_settings(self) -> Dict[str, Any]:
        path = self.workspace_root / ".claude/settings.json"
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _read_with_imports(self, path: Path, seen: List[Path]) -> str:
        path = path.resolve()
        if path in seen:
            return f"\n<!-- skipped recursive import: {self._rel(path)} -->\n"
        seen.append(path)
        lines = []
        for line in path.read_text(encoding="utf-8").splitlines():
            match = re.fullmatch(r"@(.+)", line.strip())
            if match:
                imported = (path.parent / match.group(1)).resolve()
                if imported.exists() and self._is_inside_workspace(imported):
                    lines.append(self._read_with_imports(imported, seen))
                else:
                    lines.append(f"<!-- missing import: {match.group(1)} -->")
            else:
                lines.append(line)
        return "\n".join(lines)

    def _rule_matches(self, rule_path: Path, target_path: str) -> bool:
        text = rule_path.read_text(encoding="utf-8")
        match = re.search(r"paths:\s*\[(.*?)\]", text)
        if not match:
            return False
        patterns = [item.strip().strip("\"'") for item in match.group(1).split(",") if item.strip()]
        return any(fnmatch.fnmatch(target_path, pattern) for pattern in patterns)

    def _enforce_read_permission(self, path: str, agent_name: str) -> None:
        relative = self._rel(self._normalize(path))
        for rule in self.settings.get("permissions", {}).get("deny", []):
            parsed = re.fullmatch(r"Read\((.+)\)", rule)
            if parsed and fnmatch.fnmatch(relative, parsed.group(1)):
                raise PermissionDenied(f"{agent_name} denied by permissions.deny: {rule}")

    def _attempt_read(self, path: str) -> Dict[str, Any]:
        try:
            return {"status": "allowed", "result": self.read_file(path)}
        except PermissionDenied as exc:
            return {"status": "denied", "reason": str(exc)}

    def _normalize(self, path: str) -> Path:
        candidate = (self.workspace_root / path).resolve()
        if not self._is_inside_workspace(candidate):
            raise ValueError(f"path escapes workspace: {path}")
        return candidate

    def _is_inside_workspace(self, path: Path) -> bool:
        return path == self.workspace_root or self.workspace_root in path.parents

    def _rel(self, path: Path) -> str:
        return str(path.resolve().relative_to(self.workspace_root))


def main() -> None:
    parser = argparse.ArgumentParser(description="Instruction / Permission Runtime 教学实验")
    parser.add_argument("--workspace", default=str(DEFAULT_DEMO_ROOT), help="Demo workspace root")
    parser.add_argument("--scripted", action="store_true", help="Create fixture and run deterministic demo")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    if args.scripted:
        DemoWorkspace(workspace).create()

    runtime = InstructionPermissionRuntime(workspace)
    result = runtime.demo()

    print("\n" + "=" * 60)
    print("Instruction / Permission Result")
    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
