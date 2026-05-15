"""
实验 3.11b: OpenAI SDK 版多 Agent 编排

目标：
  - 不依赖 LangGraph / LangChain，只使用 OpenAI Python SDK
  - 对照 exp3_11_multi_agent.py 理解同一个 Multi-Agent 思路如何用普通 Python 实现
  - 继续练习 OpenAI Function Calling 的消息回填格式

运行方式：
  python experiments/phase3/exp3_11b_multi_agent_openai.py localhost --mode supervisor
  python experiments/phase3/exp3_11b_multi_agent_openai.py localhost --mode swarm
  python experiments/phase3/exp3_11b_multi_agent_openai.py localhost --mode compare
"""

from __future__ import annotations

import argparse
import json
import os
import socket
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(Path(__file__).parent.parent.parent / ".env")

DEFAULT_MODEL = "deepseek-v4-pro"


def create_client() -> OpenAI:
    """创建 OpenAI SDK Client，兼容官方 API 和 OpenAI-compatible 网关。"""
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )


def get_model() -> str:
    return os.getenv("OPENAI_MODEL", DEFAULT_MODEL)


# ============================================================
# 本地安全工具
# ============================================================

def scan_ports(host: str, ports: str = "22,80,443,3306,8080") -> str:
    """扫描目标主机的指定端口是否开放。"""
    results: Dict[int, str] = {}
    for raw_port in ports.split(","):
        port = int(raw_port.strip())
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            status = "open" if sock.connect_ex((host, port)) == 0 else "closed"
            results[port] = status
            sock.close()
        except Exception:
            results[port] = "error"
    return json.dumps({"host": host, "ports": results}, ensure_ascii=False)


def analyze_risk(scan_data: str) -> str:
    """根据扫描结果做一个规则化风险分析。"""
    try:
        data = json.loads(scan_data)
    except json.JSONDecodeError:
        data = {"raw": scan_data}

    risks: List[str] = []
    high_risk_ports = {3306: "MySQL", 6379: "Redis", 27017: "MongoDB", 5432: "PostgreSQL"}
    medium_risk_ports = {22: "SSH", 21: "FTP", 8080: "HTTP-Alt", 8443: "HTTPS-Alt"}

    for port_raw, status in data.get("ports", {}).items():
        port = int(port_raw)
        if status != "open":
            continue
        if port in high_risk_ports:
            risks.append(f"HIGH: 端口 {port} ({high_risk_ports[port]}) 对外开放")
        elif port in medium_risk_ports:
            risks.append(f"MEDIUM: 端口 {port} ({medium_risk_ports[port]}) 开放")

    overall = "HIGH" if any("HIGH" in item for item in risks) else "MEDIUM" if risks else "LOW"
    return json.dumps(
        {"overall_risk": overall, "findings": risks if risks else ["未发现明显风险"]},
        ensure_ascii=False,
    )


def generate_report(target: str, findings: str) -> str:
    """生成 Markdown 格式安全评估报告。"""
    try:
        data = json.loads(findings)
    except json.JSONDecodeError:
        data = {"overall_risk": "UNKNOWN", "findings": [findings]}

    lines = [
        "# 安全评估报告",
        "",
        f"**目标**: {target}",
        f"**风险等级**: {data.get('overall_risk', 'UNKNOWN')}",
        "",
        "## 发现",
        "",
    ]
    lines.extend(f"- {finding}" for finding in data.get("findings", []))
    return "\n".join(lines)


OPENAI_TOOLS = {
    "scan_ports": {
        "schema": {
            "type": "function",
            "function": {
                "name": "scan_ports",
                "description": "扫描目标主机的指定端口是否开放",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string", "description": "目标主机 IP 或域名"},
                        "ports": {"type": "string", "description": "逗号分隔的端口列表"},
                    },
                    "required": ["host"],
                },
            },
        },
        "function": scan_ports,
    },
    "analyze_risk": {
        "schema": {
            "type": "function",
            "function": {
                "name": "analyze_risk",
                "description": "分析扫描数据并输出风险等级和发现",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scan_data": {"type": "string", "description": "JSON 格式的扫描结果"}
                    },
                    "required": ["scan_data"],
                },
            },
        },
        "function": analyze_risk,
    },
    "generate_report": {
        "schema": {
            "type": "function",
            "function": {
                "name": "generate_report",
                "description": "根据目标和风险发现生成 Markdown 报告",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string", "description": "评估目标"},
                        "findings": {"type": "string", "description": "JSON 格式的风险发现"},
                    },
                    "required": ["target", "findings"],
                },
            },
        },
        "function": generate_report,
    },
}


@dataclass
class AgentResult:
    name: str
    output: str
    tool_results: Dict[str, str] = field(default_factory=dict)


class OpenAIToolAgent:
    """一个最小专家 Agent：有自己的 system prompt 和可用工具集。"""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        tool_names: List[str],
        client: OpenAI,
        model: str,
        max_rounds: int = 4,
    ): 
        self.name = name
        self.system_prompt = system_prompt
        self.tool_names = tool_names
        self.client = client
        self.model = model
        self.max_rounds = max_rounds

    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
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
                return AgentResult(self.name, message.content or "", tool_results)

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

        return AgentResult(self.name, "Agent exceeded max_rounds before final answer.", tool_results)

    def _build_user_message(self, task: str, context: Dict[str, Any]) -> str:
        if not context:
            return task
        return f"{task}\n\n上下文:\n{json.dumps(context, ensure_ascii=False, indent=2)}"

    def _execute_tool(self, function_name: str, function_args: Dict[str, Any]) -> str:
        if function_name not in self.tool_names:
            return json.dumps({"error": f"Tool not allowed for {self.name}: {function_name}"}, ensure_ascii=False)
        tool_function: Callable[..., str] = OPENAI_TOOLS[function_name]["function"]
        try:
            return tool_function(**function_args)
        except Exception as exc:
            return json.dumps({"error": str(exc)}, ensure_ascii=False)

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


def create_agents(client: OpenAI, model: str) -> Dict[str, OpenAIToolAgent]:
    return {
        "scanner": OpenAIToolAgent(
            "Scanner Agent",
            "你是网络扫描专家。需要扫描端口时调用 scan_ports，最后用简洁中文总结扫描结果。",
            ["scan_ports"],
            client,
            model,
        ),
        "analyzer": OpenAIToolAgent(
            "Analyzer Agent",
            "你是安全风险分析专家。需要分析扫描 JSON 时调用 analyze_risk，最后输出风险等级和关键发现。",
            ["analyze_risk"],
            client,
            model,
        ),
        "reporter": OpenAIToolAgent(
            "Reporter Agent",
            "你是安全报告专家。需要生成报告时调用 generate_report，最后返回完整报告。",
            ["generate_report"],
            client,
            model,
        ),
    }


def choose_next_agent(state: Dict[str, Any]) -> str:
    """规则型 Supervisor：读取 state，决定下一个 Agent。"""
    if not state.get("scan_result"):
        return "scanner"
    if not state.get("analysis_result"):
        return "analyzer"
    if not state.get("report"):
        return "reporter"
    return "done"


def run_supervisor(target: str, client: OpenAI, model: str) -> Dict[str, Any]:
    print("\n" + "=" * 60)
    print("OpenAI SDK Supervisor 模式")
    print("=" * 60)
    agents = create_agents(client, model)
    state: Dict[str, Any] = {"target": target, "scan_result": "", "analysis_result": "", "report": ""}

    while True:
        next_agent = choose_next_agent(state)
        print(f"  [Supervisor] next_agent = {next_agent}")
        if next_agent == "done":
            break

        if next_agent == "scanner":
            result = agents["scanner"].run(f"扫描 {target} 的常用端口：22, 80, 443, 3306, 8080")
            state["scan_result"] = result.tool_results.get("scan_ports", result.output)
        elif next_agent == "analyzer":
            result = agents["analyzer"].run("分析扫描结果并评估安全风险", {"scan_result": state["scan_result"]})
            state["analysis_result"] = result.tool_results.get("analyze_risk", result.output)
        elif next_agent == "reporter":
            result = agents["reporter"].run("生成最终安全评估报告", {"target": target, "findings": state["analysis_result"]})
            state["report"] = result.tool_results.get("generate_report", result.output)

    print(f"\n报告:\n{state['report']}")
    return state


def run_swarm(target: str, client: OpenAI, model: str) -> Dict[str, Any]:
    print("\n" + "=" * 60)
    print("OpenAI SDK Swarm 模式")
    print("=" * 60)
    agents = create_agents(client, model)
    state: Dict[str, Any] = {
        "target": target,
        "current_agent": "scanner",
        "scan_result": "",
        "analysis_result": "",
        "report": "",
    }

    while state["current_agent"] != "done":
        current_agent = state["current_agent"]
        print(f"  [Swarm] current_agent = {current_agent}")

        if current_agent == "scanner":
            result = agents["scanner"].run(f"扫描 {target} 的常用端口：22, 80, 443, 3306, 8080")
            state["scan_result"] = result.tool_results.get("scan_ports", result.output)
            state["current_agent"] = "analyzer"
        elif current_agent == "analyzer":
            result = agents["analyzer"].run("分析扫描结果并评估安全风险", {"scan_result": state["scan_result"]})
            state["analysis_result"] = result.tool_results.get("analyze_risk", result.output)
            state["current_agent"] = "reporter"
        elif current_agent == "reporter":
            result = agents["reporter"].run("生成最终安全评估报告", {"target": target, "findings": state["analysis_result"]})
            state["report"] = result.tool_results.get("generate_report", result.output)
            state["current_agent"] = "done"
        else:
            raise ValueError(f"未知 Agent: {current_agent}")

    print(f"\n报告:\n{state['report']}")
    return state


def run_compare(target: str, client: OpenAI, model: str) -> None:
    run_supervisor(target, client, model)
    run_swarm(target, client, model)
    print("\n" + "=" * 60)
    print("对比总结")
    print("=" * 60)
    print("Supervisor 由 choose_next_agent(state) 统一调度；Swarm 由各节点直接修改 current_agent。")


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenAI SDK 版多 Agent 编排演示")
    parser.add_argument("target", nargs="?", default="localhost", help="评估目标")
    parser.add_argument("--mode", choices=["supervisor", "swarm", "compare"], default="compare")
    parser.add_argument("--model", default=get_model(), help="OpenAI 模型名称")
    args = parser.parse_args()

    client = create_client()
    if args.mode == "supervisor":
        run_supervisor(args.target, client, args.model)
    elif args.mode == "swarm":
        run_swarm(args.target, client, args.model)
    else:
        run_compare(args.target, client, args.model)


if __name__ == "__main__":
    main()
