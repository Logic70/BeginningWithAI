"""
实验 3.13b: Runtime Reliability for Code Agents

目标：
  - 把 retry、fallback、checkpoint、trace、eval 从生产化章节里单独拆成可运行实验。
  - 说明可靠性不是“模型更聪明”，而是 runtime 对失败、恢复和验收有明确机制。
  - 用确定性脚本模拟一次长任务：扫描 -> 分析 -> 报告 -> 评估。

运行方式：
  ./venv/bin/python experiments/phase3/exp3_13b_runtime_reliability_openai.py --help
  ./venv/bin/python experiments/phase3/exp3_13b_runtime_reliability_openai.py --scripted
  ./venv/bin/python experiments/phase3/exp3_13b_runtime_reliability_openai.py --scripted --resume

说明：
  这个实验不调用模型。它关注 code agent runtime 的可靠性控制面：
  失败要能重试，重试失败要能 fallback，中间状态要 checkpoint，最终结果要 eval。
"""

from __future__ import annotations

import argparse
import json
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List


DEFAULT_STATE_DIR = Path(tempfile.gettempdir()) / "beginningwithai-exp3-13b"


class TransientToolError(RuntimeError):
    """可重试的瞬时错误。"""


class PermanentToolError(RuntimeError):
    """不可通过重试解决的错误，需要 fallback 或人工处理。"""


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    backoff_seconds: float = 0.0


@dataclass
class StepResult:
    name: str
    status: str
    output: Dict[str, Any]
    attempts: int
    fallback_used: bool = False


@dataclass
class EvalCase:
    name: str
    required_state_keys: List[str]
    required_report_terms: List[str] = field(default_factory=list)


class TraceStore:
    """JSONL trace，记录 agent runtime 的关键事件。"""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: str, payload: Dict[str, Any]) -> None:
        record = {
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "event": event,
            "payload": payload,
        }
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    def read_all(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]


class CheckpointStore:
    """最小 checkpoint store，用 JSON 保存每个阶段的运行状态。"""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, state: Dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(state, file, ensure_ascii=False, indent=2)

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))


class RuntimeReliabilityDemo:
    """
    教学版可靠性 runtime。

    它不实现新的 Agent 能力，而是在普通任务链外面包一层运行时保障：
      - trace: 发生了什么
      - retry: 瞬时失败怎么重试
      - fallback: 永久失败怎么降级
      - checkpoint: 跑到哪了
      - eval: 最终算不算合格
    """

    def __init__(self, state_dir: Path = DEFAULT_STATE_DIR, retry_policy: RetryPolicy | None = None):
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.trace = TraceStore(self.state_dir / "runtime_trace.jsonl")
        self.checkpoint = CheckpointStore(self.state_dir / "checkpoint.json")
        self.retry_policy = retry_policy or RetryPolicy()
        self._attempt_counters: Dict[str, int] = {}

    def run_scripted_demo(self, resume: bool = False) -> Dict[str, Any]:
        state = self.checkpoint.load() if resume else {"target": "localhost", "steps": []}
        self.trace.append("run_start", {"resume": resume, "existing_keys": sorted(state.keys())})

        if "scan_result" not in state:
            scan = self.run_step("scan", self._scan_with_transient_failure)
            state["scan_result"] = scan.output
            state["steps"].append(scan.__dict__)
            self._checkpoint(state, "scan")

        if "analysis_result" not in state:
            analysis = self.run_step("analysis", self._analysis_with_permanent_failure, fallback=self._analysis_fallback)
            state["analysis_result"] = analysis.output
            state["steps"].append(analysis.__dict__)
            self._checkpoint(state, "analysis")

        if "report" not in state:
            report = self.run_step("report", lambda: self._generate_report(state))
            state["report"] = report.output
            state["steps"].append(report.__dict__)
            self._checkpoint(state, "report")

        evaluation = self.evaluate(
            EvalCase(
                name="runtime_reliability_minimum",
                required_state_keys=["target", "scan_result", "analysis_result", "report"],
                required_report_terms=["localhost", "fallback", "checkpoint"],
            ),
            state,
        )
        state["evaluation"] = evaluation
        self._checkpoint(state, "evaluation")
        self.trace.append("run_end", {"passed": evaluation["passed"]})

        return {
            "state_dir": str(self.state_dir),
            "checkpoint": str(self.checkpoint.path),
            "trace": str(self.trace.path),
            "state": state,
            "trace_event_count": len(self.trace.read_all()),
        }

    def run_step(
        self,
        name: str,
        operation: Callable[[], Dict[str, Any]],
        fallback: Callable[[], Dict[str, Any]] | None = None,
    ) -> StepResult:
        last_error = ""
        for attempt in range(1, self.retry_policy.max_attempts + 1):
            self.trace.append("step_attempt", {"step": name, "attempt": attempt})
            try:
                output = operation()
                self.trace.append("step_success", {"step": name, "attempt": attempt})
                return StepResult(name=name, status="success", output=output, attempts=attempt)
            except TransientToolError as exc:
                last_error = str(exc)
                self.trace.append("step_retryable_error", {"step": name, "attempt": attempt, "error": last_error})
                if self.retry_policy.backoff_seconds:
                    time.sleep(self.retry_policy.backoff_seconds)
            except PermanentToolError as exc:
                last_error = str(exc)
                self.trace.append("step_permanent_error", {"step": name, "attempt": attempt, "error": last_error})
                break

        if fallback is None:
            raise RuntimeError(f"step {name} failed without fallback: {last_error}")

        output = fallback()
        self.trace.append("step_fallback", {"step": name, "error": last_error})
        return StepResult(
            name=name,
            status="fallback",
            output=output,
            attempts=min(self.retry_policy.max_attempts, max(1, self._attempt_counters.get(name, 1))),
            fallback_used=True,
        )

    def evaluate(self, case: EvalCase, state: Dict[str, Any]) -> Dict[str, Any]:
        issues: List[str] = []
        for key in case.required_state_keys:
            if key not in state:
                issues.append(f"missing state key: {key}")

        report_text = json.dumps(state.get("report", {}), ensure_ascii=False).lower()
        for term in case.required_report_terms:
            if term.lower() not in report_text:
                issues.append(f"report missing term: {term}")

        fallback_seen = any(step.get("fallback_used") for step in state.get("steps", []))
        if not fallback_seen:
            issues.append("expected at least one fallback path")

        return {
            "case": case.name,
            "passed": not issues,
            "issues": issues,
            "step_count": len(state.get("steps", [])),
        }

    def _scan_with_transient_failure(self) -> Dict[str, Any]:
        attempt = self._next_attempt("scan")
        if attempt == 1:
            raise TransientToolError("simulated port scanner timeout")
        return {
            "host": "localhost",
            "ports": [{"port": 80, "state": "open"}, {"port": 443, "state": "closed"}],
            "source": "simulated scanner after retry",
        }

    def _analysis_with_permanent_failure(self) -> Dict[str, Any]:
        self._next_attempt("analysis")
        raise PermanentToolError("simulated analyzer model/tool unavailable")

    def _analysis_fallback(self) -> Dict[str, Any]:
        return {
            "risk": "medium",
            "findings": ["fallback analysis used because primary analyzer failed"],
            "fallback": True,
        }

    def _generate_report(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self._next_attempt("report")
        return {
            "title": "Runtime reliability report for localhost",
            "target": state["target"],
            "summary": "scan completed after retry; analysis used fallback; checkpoint saved after every step",
            "checkpoint": str(self.checkpoint.path),
            "fallback": state["analysis_result"].get("fallback", False),
        }

    def _checkpoint(self, state: Dict[str, Any], stage: str) -> None:
        state["last_checkpoint_stage"] = stage
        self.checkpoint.save(state)
        self.trace.append("checkpoint_saved", {"stage": stage, "path": str(self.checkpoint.path)})

    def _next_attempt(self, name: str) -> int:
        self._attempt_counters[name] = self._attempt_counters.get(name, 0) + 1
        return self._attempt_counters[name]


def main() -> None:
    parser = argparse.ArgumentParser(description="Runtime Reliability 教学实验")
    parser.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR), help="Directory for trace and checkpoint files")
    parser.add_argument("--scripted", action="store_true", help="Run deterministic reliability demo")
    parser.add_argument("--resume", action="store_true", help="Resume from existing checkpoint if present")
    args = parser.parse_args()

    runtime = RuntimeReliabilityDemo(state_dir=Path(args.state_dir))
    result = runtime.run_scripted_demo(resume=args.resume)

    print("\n" + "=" * 60)
    print("Runtime Reliability Result")
    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
