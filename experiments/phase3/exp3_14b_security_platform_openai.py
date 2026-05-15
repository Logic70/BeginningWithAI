"""
实验 3.14b: 综合项目 — 安全评估平台（OpenAI SDK 版）

这份代码是 Phase 3 的 OpenAI SDK 毕业项目版本。

它把前面几章的主线串在一起：
  - 3.11b：OpenAI SDK 版 Multi-Agent
  - 3.12b：A2A 思维方式（这里先保留本地进程内编排）
  - 3.13：生产化实践（日志、检查点、人工审批）

这个脚本刻意不依赖 LangGraph。
目的不是否定 LangGraph，而是帮助你从“纯 OpenAI SDK + Python 状态机”的视角，
彻底看清一个综合 Agent 系统到底是怎么拼起来的。

运行方式：
  python experiments/phase3/exp3_14b_security_platform_openai.py localhost
  python experiments/phase3/exp3_14b_security_platform_openai.py localhost --auto-approve
  python experiments/phase3/exp3_14b_security_platform_openai.py localhost --resume
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(Path(__file__).parent.parent.parent / ".env")


# ============================================================
# 配置
# ============================================================

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "deepseek-v4-pro")
CHECKPOINT_DIR = Path(__file__).parent / "platform_checkpoints"
CHECKPOINT_DIR.mkdir(exist_ok=True)


def create_client() -> OpenAI:
    """
    创建 OpenAI SDK Client。

    这里沿用项目统一的 OPENAI-compatible 配置。
    所以不管底层是 OpenAI 官方，还是 OpenCode Go 这样的兼容网关，
    这层代码都不需要感知区别。
    """
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )


def checkpoint_path(target: str) -> Path:
    """
    生成检查点文件路径。

    文件名只保留安全字符，防止奇怪输入直接进入文件系统路径。
    """
    safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", target)
    return CHECKPOINT_DIR / f"{safe_name}.json"


# ============================================================
# 本地安全工具
# ============================================================

def scan_ports(host: str, ports: str = "21,22,80,443,3306,3389,5432,6379,8080,8443,27017") -> str:
    """扫描一组常见端口。"""
    results: Dict[int, str] = {}
    port_list = [int(item.strip()) for item in ports.split(",")]

    for port in port_list:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            status = "open" if sock.connect_ex((host, port)) == 0 else "closed"
            results[port] = status
            sock.close()
        except Exception:
            results[port] = "error"

    open_ports = [port for port, status in results.items() if status == "open"]
    return json.dumps(
        {
            "host": host,
            "total_scanned": len(port_list),
            "open_ports": open_ports,
            "details": results,
        },
        ensure_ascii=False,
    )


def check_http_security(url: str) -> str:
    """检查 HTTP 安全头。"""
    import urllib.request

    try:
        if not url.startswith("http"):
            url = f"http://{url}"

        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "SecurityAudit/1.0")

        with urllib.request.urlopen(req, timeout=5) as resp:
            headers = dict(resp.headers)
            security_headers = {
                "X-Frame-Options": headers.get("X-Frame-Options"),
                "X-Content-Type-Options": headers.get("X-Content-Type-Options"),
                "Strict-Transport-Security": headers.get("Strict-Transport-Security"),
                "Content-Security-Policy": headers.get("Content-Security-Policy"),
                "X-XSS-Protection": headers.get("X-XSS-Protection"),
            }
            missing = [key for key, value in security_headers.items() if value is None]

            return json.dumps(
                {
                    "url": url,
                    "status": resp.status,
                    "server": headers.get("Server", "unknown"),
                    "security_headers": security_headers,
                    "missing_headers": missing,
                    "risk": "HIGH" if len(missing) >= 4 else "MEDIUM" if len(missing) >= 2 else "LOW",
                },
                ensure_ascii=False,
            )
    except Exception as exc:
        return json.dumps({"error": str(exc), "url": url}, ensure_ascii=False)


def check_common_vulns(host: str, open_ports: str) -> str:
    """根据开放端口映射常见风险。"""
    try:
        parsed = json.loads(open_ports) if isinstance(open_ports, str) else open_ports
    except json.JSONDecodeError:
        parsed = []

    ports = parsed if isinstance(parsed, list) else parsed.get("open_ports", [])
    vulnerabilities: List[Dict[str, Any]] = []

    high_risk = {
        3306: {"service": "MySQL", "risk": "CRITICAL", "desc": "数据库直接暴露，可能遭受暴力破解"},
        5432: {"service": "PostgreSQL", "risk": "CRITICAL", "desc": "数据库直接暴露"},
        6379: {"service": "Redis", "risk": "CRITICAL", "desc": "Redis 未授权访问风险"},
        27017: {"service": "MongoDB", "risk": "CRITICAL", "desc": "MongoDB 未授权访问风险"},
        3389: {"service": "RDP", "risk": "HIGH", "desc": "远程桌面暴露，易遭受暴力破解"},
        21: {"service": "FTP", "risk": "HIGH", "desc": "FTP 明文传输，可能泄露凭据"},
    }
    medium_risk = {
        22: {"service": "SSH", "risk": "MEDIUM", "desc": "SSH 暴露，建议限制访问 IP"},
        8080: {"service": "HTTP-Alt", "risk": "MEDIUM", "desc": "备用 HTTP 端口，可能是管理后台"},
        8443: {"service": "HTTPS-Alt", "risk": "MEDIUM", "desc": "备用 HTTPS 端口"},
    }

    for port in ports:
        port_num = int(port)
        if port_num in high_risk:
            vulnerabilities.append({**high_risk[port_num], "port": port_num})
        elif port_num in medium_risk:
            vulnerabilities.append({**medium_risk[port_num], "port": port_num})

    overall_risk = (
        "CRITICAL"
        if any(item["risk"] == "CRITICAL" for item in vulnerabilities)
        else "HIGH"
        if any(item["risk"] == "HIGH" for item in vulnerabilities)
        else "MEDIUM"
        if vulnerabilities
        else "LOW"
    )

    return json.dumps(
        {
            "host": host,
            "overall_risk": overall_risk,
            "vulnerabilities": vulnerabilities,
            "total_issues": len(vulnerabilities),
        },
        ensure_ascii=False,
    )


def generate_report(target: str, recon_result: str, http_result: str, vuln_result: str) -> str:
    """把各阶段结果汇总成最终 Markdown 报告。"""
    try:
        recon = json.loads(recon_result)
    except json.JSONDecodeError:
        recon = {"raw": recon_result}

    try:
        http = json.loads(http_result) if http_result else {}
    except json.JSONDecodeError:
        http = {"raw": http_result}

    try:
        vuln = json.loads(vuln_result)
    except json.JSONDecodeError:
        vuln = {"raw": vuln_result}

    lines = [
        "# 安全评估报告",
        "",
        f"**目标**: {target}",
        f"**总体风险**: {vuln.get('overall_risk', 'UNKNOWN')}",
        "",
        "## 信息收集",
        "",
        f"- 开放端口: {recon.get('open_ports', [])}",
        "",
    ]

    if http:
        lines.extend(
            [
                "## HTTP 安全头",
                "",
                f"- 状态码: {http.get('status', 'unknown')}",
                f"- 缺失安全头: {http.get('missing_headers', [])}",
                "",
            ]
        )

    lines.extend(["## 风险发现", ""])
    for item in vuln.get("vulnerabilities", []):
        lines.append(f"- [{item['risk']}] 端口 {item['port']} {item['service']}：{item['desc']}")

    if not vuln.get("vulnerabilities"):
        lines.append("- 未发现明显高危暴露")

    return "\n".join(lines)


# ============================================================
# OpenAI Function Calling 元数据
# ============================================================

OPENAI_TOOLS = {
    "scan_ports": {
        "schema": {
            "type": "function",
            "function": {
                "name": "scan_ports",
                "description": "扫描目标主机的常见端口",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string", "description": "目标主机"},
                        "ports": {"type": "string", "description": "逗号分隔的端口列表"},
                    },
                    "required": ["host"],
                },
            },
        },
        "function": scan_ports,
    },
    "check_http_security": {
        "schema": {
            "type": "function",
            "function": {
                "name": "check_http_security",
                "description": "检查 HTTP 安全响应头",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "目标 URL 或主机名"}
                    },
                    "required": ["url"],
                },
            },
        },
        "function": check_http_security,
    },
    "check_common_vulns": {
        "schema": {
            "type": "function",
            "function": {
                "name": "check_common_vulns",
                "description": "根据开放端口检查常见漏洞风险",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string", "description": "目标主机"},
                        "open_ports": {"type": "string", "description": "开放端口列表或扫描结果 JSON"},
                    },
                    "required": ["host", "open_ports"],
                },
            },
        },
        "function": check_common_vulns,
    },
    "generate_report": {
        "schema": {
            "type": "function",
            "function": {
                "name": "generate_report",
                "description": "根据各阶段结果生成 Markdown 报告",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string"},
                        "recon_result": {"type": "string"},
                        "http_result": {"type": "string"},
                        "vuln_result": {"type": "string"},
                    },
                    "required": ["target", "recon_result", "http_result", "vuln_result"],
                },
            },
        },
        "function": generate_report,
    },
}


# ============================================================
# 单个专家 Agent 运行时
# ============================================================

@dataclass
class AgentRunResult:
    """保存单个专家 Agent 的结果。"""

    name: str
    output: str
    tool_results: Dict[str, str] = field(default_factory=dict)


class OpenAIToolAgent:
    """
    最小专家 Agent 模板。

    这一层解决的是：
      - 单个 Agent 如何使用 OpenAI Function Calling
      - 模型要工具时如何执行
      - 工具结果如何回填

    它还不是平台编排层。
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        tool_names: List[str],
        client: OpenAI,
        model: str,
        max_rounds: int = 5,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.tool_names = tool_names
        self.client = client
        self.model = model
        self.max_rounds = max_rounds

    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentRunResult:
        print(f"  [{self.name}] 任务: {task}")

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self._build_user_message(task, context or {})},
        ]
        tool_schemas = [OPENAI_TOOLS[name]["schema"] for name in self.tool_names]
        tool_results: Dict[str, str] = {}

        for _ in range(self.max_rounds):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tool_schemas,
                tool_choice="auto",
            )
            message = response.choices[0].message

            if not getattr(message, "tool_calls", None):
                return AgentRunResult(self.name, message.content or "", tool_results)

            messages.append(self._assistant_message_for_history(message))

            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments or "{}")
                tool_output = self._execute_tool(function_name, function_args)
                tool_results[function_name] = tool_output
                print(f"  [{self.name}] 调用工具: {function_name}({function_args})")
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_output,
                    }
                )

        return AgentRunResult(self.name, "Agent exceeded max_rounds before final answer.", tool_results)

    def _build_user_message(self, task: str, context: Dict[str, Any]) -> str:
        """
        把任务和共享状态里的必要字段注入当前 Agent。

        这一步就是多 Agent 编排里最常说的 handoff：
        不是把整个世界都塞给下一个 Agent，而是只传它完成职责所需的信息。
        """
        if not context:
            return task
        return f"{task}\n\n上下文:\n{json.dumps(context, ensure_ascii=False, indent=2)}"

    def _execute_tool(self, function_name: str, function_args: Dict[str, Any]) -> str:
        """执行被允许的本地工具。"""
        if function_name not in self.tool_names:
            return json.dumps({"error": f"Tool not allowed for {self.name}: {function_name}"}, ensure_ascii=False)

        tool_function: Callable[..., str] = OPENAI_TOOLS[function_name]["function"]
        try:
            return tool_function(**function_args)
        except Exception as exc:
            return json.dumps({"error": str(exc)}, ensure_ascii=False)

    def _assistant_message_for_history(self, message: Any) -> Dict[str, Any]:
        """
        把 assistant 的 tool_calls 和 reasoning_content 回填到下一轮历史中。

        deepseek-v4-pro 需要 reasoning_content 一起带回去，
        不然继续请求时会报 provider 级别的 400。
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


# ============================================================
# 平台状态
# ============================================================

@dataclass
class SecurityPlatformState:
    """
    整个平台共享的状态。

    这是 OpenAI SDK 版里对 LangGraph state 的一个朴素替代。
    你可以把它理解成“平台级共享上下文”。
    """

    target: str
    scan_result: str = ""
    http_result: str = ""
    vuln_result: str = ""
    overall_risk: str = ""
    human_approved: bool = False
    report: str = ""
    next_agent: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "scan_result": self.scan_result,
            "http_result": self.http_result,
            "vuln_result": self.vuln_result,
            "overall_risk": self.overall_risk,
            "human_approved": self.human_approved,
            "report": self.report,
            "next_agent": self.next_agent,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecurityPlatformState":
        return cls(**data)


# ============================================================
# 平台级 Agent 创建
# ============================================================

def create_platform_agents(client: OpenAI, model: str) -> Dict[str, OpenAIToolAgent]:
    """
    构建三个专业 Agent。

    和 3.11b 的区别在于，这里每个 Agent 的任务粒度更真实：
      - recon: 信息收集
      - analyzer: 风险分析
      - reporter: 报告输出
    """
    return {
        "recon": OpenAIToolAgent(
            name="Recon Agent",
            system_prompt=(
                "你是信息收集专家。"
                "你的目标是：扫描端口；如果存在 Web 端口，再检查 HTTP 安全头。"
                "只做信息收集，不做风险定级。"
            ),
            tool_names=["scan_ports", "check_http_security"],
            client=client,
            model=model,
        ),
        "analyzer": OpenAIToolAgent(
            name="Analyzer Agent",
            system_prompt=(
                "你是安全分析专家。"
                "你的目标是基于扫描结果和 HTTP 结果判断风险，必要时调用 check_common_vulns。"
            ),
            tool_names=["check_common_vulns"],
            client=client,
            model=model,
        ),
        "reporter": OpenAIToolAgent(
            name="Reporter Agent",
            system_prompt=(
                "你是安全报告专家。"
                "你的目标是根据前面阶段的结构化结果生成清晰的 Markdown 报告。"
            ),
            tool_names=["generate_report"],
            client=client,
            model=model,
        ),
    }


# ============================================================
# 平台编排
# ============================================================

def choose_next_agent(state: SecurityPlatformState) -> str:
    """
    平台级 Supervisor。

    这里依然不是另一个 LLM，而是一个规则型调度器。
    这样教学上更容易看清楚：
      多 Agent 的关键不是“再加一个更聪明的模型”，
      而是“把状态流和职责边界设计清楚”。
    """
    if not state.scan_result:
        return "recon"
    if not state.vuln_result:
        return "analyzer"
    if not state.report:
        return "reporter"
    return "done"


def save_checkpoint(state: SecurityPlatformState) -> Path:
    """把当前平台状态落盘。"""
    path = checkpoint_path(state.target)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(state.to_dict(), fh, ensure_ascii=False, indent=2)
    return path


def load_checkpoint(target: str) -> SecurityPlatformState:
    """从磁盘恢复平台状态。"""
    path = checkpoint_path(target)
    with path.open("r", encoding="utf-8") as fh:
        return SecurityPlatformState.from_dict(json.load(fh))


def human_review(state: SecurityPlatformState, auto_approve: bool = False) -> bool:
    """
    人工审批。

    这是 OpenAI SDK 版对 Human-in-the-loop 的最朴素实现：
      - 高危时暂停
      - 交给人来决定是否继续

    LangGraph 可以把这个流程做得更优雅，但工程本质是一样的。
    """
    if state.overall_risk not in {"HIGH", "CRITICAL"}:
        return True

    print("\n" + "=" * 60)
    print(f"需要人工审批：当前风险等级 = {state.overall_risk}")
    print("=" * 60)

    if auto_approve:
        print("auto_approve=True，自动继续。")
        return True

    answer = input("是否继续生成最终报告？输入 yes 继续，其他任意输入终止: ").strip().lower()
    return answer in {"yes", "y"}


def run_platform(target: str, auto_approve: bool = False, resume: bool = False) -> SecurityPlatformState:
    """
    运行整个平台。

    这是整份脚本的顶层入口，负责把：
      - 平台状态
      - 专业 Agent
      - 人工审批
      - 检查点
    真正串成一个可以跑起来的系统。
    """
    client = create_client()
    agents = create_platform_agents(client, DEFAULT_MODEL)

    if resume and checkpoint_path(target).exists():
        state = load_checkpoint(target)
        print(f"从检查点恢复: {checkpoint_path(target)}")
    else:
        state = SecurityPlatformState(target=target)

    while True:
        state.next_agent = choose_next_agent(state)
        print(f"\n[Supervisor] next_agent = {state.next_agent}")

        if state.next_agent == "done":
            break

        if state.next_agent == "recon":
            result = agents["recon"].run(
                task=f"对目标 {target} 做信息收集：扫描常见端口；如果有 Web 服务，检查 HTTP 安全头。",
                context={"target": target},
            )
            state.scan_result = result.tool_results.get("scan_ports", "")
            state.http_result = result.tool_results.get("check_http_security", "")
            save_checkpoint(state)
            continue

        if state.next_agent == "analyzer":
            result = agents["analyzer"].run(
                task="根据已有扫描结果分析风险等级",
                context={
                    "target": target,
                    "scan_result": state.scan_result,
                    "http_result": state.http_result,
                },
            )
            state.vuln_result = result.tool_results.get("check_common_vulns", result.output)

            try:
                state.overall_risk = json.loads(state.vuln_result).get("overall_risk", "LOW")
            except json.JSONDecodeError:
                state.overall_risk = "UNKNOWN"

            state.human_approved = human_review(state, auto_approve=auto_approve)
            save_checkpoint(state)
            if not state.human_approved:
                print("人工审批未通过，流程终止。")
                return state
            continue

        if state.next_agent == "reporter":
            result = agents["reporter"].run(
                task="根据当前平台状态生成最终安全评估报告",
                context={
                    "target": target,
                    "recon_result": state.scan_result,
                    "http_result": state.http_result,
                    "vuln_result": state.vuln_result,
                },
            )
            state.report = result.tool_results.get("generate_report", result.output)
            save_checkpoint(state)
            continue

    return state


# ============================================================
# CLI
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="综合项目 — 安全评估平台（OpenAI SDK 版）")
    parser.add_argument("target", nargs="?", default="localhost", help="评估目标")
    parser.add_argument("--auto-approve", action="store_true", help="高危时自动继续，不等待人工输入")
    parser.add_argument("--resume", action="store_true", help="如果存在检查点，则从检查点恢复")
    args = parser.parse_args()

    start = time.time()
    state = run_platform(args.target, auto_approve=args.auto_approve, resume=args.resume)
    elapsed = round(time.time() - start, 2)

    print("\n" + "=" * 60)
    print("最终平台状态")
    print("=" * 60)
    print(json.dumps(state.to_dict(), ensure_ascii=False, indent=2))
    print("\n" + "=" * 60)
    print("最终报告")
    print("=" * 60)
    print(state.report or "<未生成报告>")
    print(f"\n总耗时: {elapsed}s")


if __name__ == "__main__":
    main()
