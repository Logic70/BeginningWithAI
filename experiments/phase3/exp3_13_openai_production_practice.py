"""
实验 3.13: 生产化实践（OpenAI SDK 版）

这份代码的定位不是“再造一个新 Agent 框架”，
而是站在 3.11b 的 OpenAI SDK Multi-Agent 之上，
补齐生产环境真正关心的几件事：

  1. 输入校验：不要什么目标都直接拿去跑
  2. 可观测性：每次运行发生了什么，要能追踪
  3. 错误恢复：失败时要有重试和留痕
  4. 检查点：运行结果要能落盘，方便复盘
  5. 评估：你要知道这个 Agent 到底有没有达到预期

运行方式：
  python experiments/phase3/exp3_13_openai_production_practice.py run localhost
  python experiments/phase3/exp3_13_openai_production_practice.py eval
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# 这里直接复用 3.11b 已经跑通的 OpenAI SDK Multi-Agent 运行时。
# 教学上这么做是刻意的：
# 3.13 不是重写“怎么做多 Agent”，而是强调“怎么把已有 Agent 做得更像生产系统”。
from exp3_11b_multi_agent_openai import create_client, get_model, run_supervisor


load_dotenv(Path(__file__).parent.parent.parent / ".env")


# ============================================================
# 结构化日志
# ============================================================

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
TRACE_LOG = LOG_DIR / "exp3_13_openai_trace.jsonl"


def build_logger() -> logging.Logger:
    """
    构建日志器。

    这里故意不搞很复杂的 logging 配置，
    目标是让你一眼能看懂：生产里的“可观测性”至少要把什么写下来。
    """
    logger = logging.getLogger("exp3_13_openai")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(handler)
    return logger


LOGGER = build_logger()


def append_trace(event: str, payload: Dict[str, Any]) -> None:
    """
    把关键事件落成 JSON Lines。

    这么做的好处：
      - 机器容易分析
      - 人也容易 grep / jq
      - 一条记录一个事件，不需要把整次运行硬塞到一份大 JSON 里
    """
    record = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "event": event,
        "payload": payload,
    }
    with TRACE_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


# ============================================================
# 输入校验与检查点
# ============================================================

CHECKPOINT_DIR = Path(__file__).parent / "checkpoints"
CHECKPOINT_DIR.mkdir(exist_ok=True)


def validate_target(target: str) -> bool:
    """
    只允许最常见的域名 / IPv4 / localhost。

    生产环境里，最危险的事情之一就是“把原始用户输入直接喂给工具”。
    所以即使这里只是学习项目，也要养成先做基本校验的习惯。
    """
    if target == "localhost":
        return True

    ip_pattern = r"^\d{1,3}(?:\.\d{1,3}){3}$"
    domain_pattern = r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(ip_pattern, target) or re.match(domain_pattern, target))


def checkpoint_path(target: str) -> Path:
    """
    为每个 target 生成一个检查点文件名。

    文件名里只保留安全字符，避免把奇怪的输入直接拼到路径上。
    """
    safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", target)
    return CHECKPOINT_DIR / f"{safe_name}.json"


def save_checkpoint(target: str, state: Dict[str, Any]) -> Path:
    """
    保存最终状态。

    这里保存的是“运行结果快照”，
    不是 LangGraph 那种细粒度中间执行现场。
    但对学习生产实践来说，已经足够让你体会检查点的价值。
    """
    path = checkpoint_path(target)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)
    return path


# ============================================================
# 评估用例
# ============================================================

@dataclass
class EvalCase:
    """
    一条最小评估用例。

    这里不追求“学术级评测框架”，
    而是强调一个非常务实的问题：
      你准备如何判断这套 Agent 是不是基本可用？
    """

    name: str
    target: str
    expected_report_contains: List[str] = field(default_factory=list)
    expected_scan_keys: List[str] = field(default_factory=list)


DEFAULT_EVAL_CASES = [
    EvalCase(
        name="localhost_basic",
        target="localhost",
        expected_report_contains=["安全评估报告", "风险等级"],
        expected_scan_keys=["host", "ports"],
    )
]


def evaluate_state(case: EvalCase, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    对一次运行结果做最小评估。

    评估思路非常朴素：
      - 报告有没有生成
      - 报告里是否包含关键字段
      - 扫描结果是不是结构化 JSON
    """
    report = state.get("report", "")
    scan_result = state.get("scan_result", "")

    issues: List[str] = []

    for token in case.expected_report_contains:
        if token not in report:
            issues.append(f"report missing token: {token}")

    try:
        scan_data = json.loads(scan_result)
    except json.JSONDecodeError as exc:
        issues.append(f"scan_result is not valid JSON: {exc}")
        scan_data = {}

    for key in case.expected_scan_keys:
        if key not in scan_data:
            issues.append(f"scan_result missing key: {key}")

    return {
        "case": case.name,
        "target": case.target,
        "passed": not issues,
        "issues": issues,
    }


# ============================================================
# 运行时包装
# ============================================================

def run_supervisor_with_retry(target: str, retries: int = 2) -> Dict[str, Any]:
    """
    给 3.11b 的 run_supervisor() 套上一层重试。

    这里的重试粒度是“整次工作流”而不是“单次 LLM 调用”，
    这样实现简单，足够说明生产里“失败后要怎么办”的基本思路。
    """
    client = create_client()
    model = get_model()
    last_error: Optional[Exception] = None

    for attempt in range(1, retries + 2):
        start = time.time()
        append_trace("run_start", {"target": target, "attempt": attempt, "model": model})
        LOGGER.info(f"运行开始 target={target} attempt={attempt}")

        try:
            state = run_supervisor(target, client, model)
            duration = round(time.time() - start, 2)

            checkpoint = save_checkpoint(target, state)
            append_trace(
                "run_success",
                {
                    "target": target,
                    "attempt": attempt,
                    "duration_sec": duration,
                    "checkpoint": str(checkpoint),
                },
            )
            LOGGER.info(f"运行成功 target={target} duration={duration}s checkpoint={checkpoint.name}")
            return state
        except Exception as exc:  # pragma: no cover - 用于真实运行时防御
            duration = round(time.time() - start, 2)
            last_error = exc
            append_trace(
                "run_error",
                {
                    "target": target,
                    "attempt": attempt,
                    "duration_sec": duration,
                    "error": str(exc),
                },
            )
            LOGGER.warning(f"运行失败 target={target} attempt={attempt} error={exc}")

            # 小规模指数退避。
            # 教学重点不是退避算法本身，而是让你意识到“失败后不要立刻疯狂重试”。
            if attempt <= retries:
                time.sleep(min(2 ** attempt, 5))

    raise RuntimeError(f"workflow failed after retries: {last_error}")


def run_once(target: str) -> Dict[str, Any]:
    """
    生产风格的单次运行入口。

    这层做三件事：
      1. 输入校验
      2. 重试包装
      3. 返回最终状态给调用方
    """
    if not validate_target(target):
        raise ValueError(f"非法目标: {target}")

    return run_supervisor_with_retry(target)


def run_eval(cases: List[EvalCase]) -> List[Dict[str, Any]]:
    """
    批量执行评估。

    这里的设计很有意图：
    你不是只“跑通代码”，而是开始习惯性地问：
      - 这次运行算成功吗？
      - 成功的标准是什么？
      - 这些标准能不能自动检查？
    """
    results: List[Dict[str, Any]] = []

    for case in cases:
        LOGGER.info(f"开始评估 case={case.name} target={case.target}")
        try:
            state = run_once(case.target)
            evaluation = evaluate_state(case, state)
        except Exception as exc:  # pragma: no cover - 真实调用防御
            evaluation = {
                "case": case.name,
                "target": case.target,
                "passed": False,
                "issues": [f"exception: {exc}"],
            }

        append_trace("eval_result", evaluation)
        results.append(evaluation)

    return results


# ============================================================
# CLI
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="生产化实践（OpenAI SDK 版）")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    run_parser = subparsers.add_parser("run", help="运行一次生产风格工作流")
    run_parser.add_argument("target", help="扫描目标，例如 localhost")

    subparsers.add_parser("eval", help="运行内置评估用例")

    args = parser.parse_args()

    if args.mode == "run":
        state = run_once(args.target)
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return

    results = run_eval(DEFAULT_EVAL_CASES)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
