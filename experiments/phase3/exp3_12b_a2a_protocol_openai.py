"""
实验 3.12b: A2A 协议与 Agent 互操作（OpenAI SDK 版）

教学目标：
  1. 不依赖 LangChain / LangGraph，只使用 OpenAI Python SDK
  2. 把 3.11b 的本地 Multi-Agent 思路扩展成“跨进程/跨网络”的 Agent 协作
  3. 理解 A2A 的本质不是“新的推理能力”，而是“Agent 之间的标准通信层”

学习主线：
  - 3.11b 解决：同一进程里的多个 Agent 怎么协作
  - 3.12b 解决：不同进程里的 Agent 怎么发现彼此并发送任务

运行方式：
  python experiments/phase3/exp3_12b_a2a_protocol_openai.py scanner
  python experiments/phase3/exp3_12b_a2a_protocol_openai.py analyzer
  python experiments/phase3/exp3_12b_a2a_protocol_openai.py orchestrator localhost

推荐开三个终端：
  终端 1: 启动 Scanner Agent
  终端 2: 启动 Analyzer Agent
  终端 3: 运行 Orchestrator
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import time
from dataclasses import dataclass, field
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypedDict

import requests
from dotenv import load_dotenv
from openai import OpenAI


# 显式从项目根目录读取 .env。
# 这样即使你从 experiments/phase3 目录运行脚本，也能拿到统一的模型配置。
load_dotenv(Path(__file__).parent.parent.parent / ".env")


# ============================================================
# 基础配置
# ============================================================

DEFAULT_MODEL = "deepseek-v4-pro"


def create_client() -> OpenAI:
    """
    创建 OpenAI SDK Client。

    这里使用的是“OpenAI 兼容接口”的统一入口。
    只要服务商遵循 chat/completions 协议，这里就不用改代码。
    """
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )


def get_model() -> str:
    """优先使用 .env 中配置的模型名。"""
    return os.getenv("OPENAI_MODEL", DEFAULT_MODEL)


# ============================================================
# 本地安全工具
# ============================================================

def scan_ports(host: str, ports: str = "22,80,443,3306,8080") -> str:
    """
    端口扫描工具。

    这一层仍然是普通 Python 函数。
    Tool 的本质从来都不是“Agent 魔法”，而是“可被 Agent 调用的代码”。
    """
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
    """
    风险分析工具。

    输入是扫描结果 JSON 字符串，输出也是结构化 JSON。
    这样后面的 Agent 之间传上下文时，格式会更稳定。
    """
    try:
        data = json.loads(scan_data)
    except json.JSONDecodeError:
        data = {"raw": scan_data}

    risks: List[str] = []
    high_risk_ports = {3306: "MySQL", 6379: "Redis", 27017: "MongoDB"}
    medium_risk_ports = {22: "SSH", 8080: "HTTP-Alt"}

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


# ============================================================
# OpenAI Function Calling 元数据
# ============================================================

# 这一节做的事情很机械，但非常重要：
# 我们需要把“本地 Python 函数”翻译成“模型能读懂的 JSON Schema”。
# 只有这样，模型才知道：
#   - 有哪些工具可用
#   - 工具叫什么
#   - 参数应该长什么样
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
}


# ============================================================
# 单个专家 Agent 的最小运行时
# ============================================================

@dataclass
class AgentRunResult:
    """
    保存一次 Agent 运行的结果。

    这里故意同时保留：
      - output: 模型最终自然语言输出
      - tool_results: 本轮执行过的工具输出

    教学上这么做是为了让你能看清楚：
      - 模型总结文本是什么
      - 工具真实结果是什么
    """

    name: str
    output: str
    tool_results: Dict[str, str] = field(default_factory=dict)


class OpenAIToolAgent:
    """
    一个最小的 OpenAI SDK 专家 Agent。

    它只做一件事：
      “接收任务 -> 调模型 -> 如果模型要工具，就执行工具 -> 回填结果 -> 继续”

    所以这个类不是“多 Agent”本身，
    而是“单个会使用工具的 Agent 模板”。
    """

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

    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentRunResult:
        """
        执行单个专家 Agent 的完整 tool loop。

        这个方法是整个脚本里最值得反复看的部分之一。
        你后面学习 Subagent、A2A、Supervisor、Workflow，
        里面的“单个 Agent 内核”本质上都还是这一套。
        """
        print(f"  [{self.name}] 收到任务: {task}")

        # 初始化对话历史。
        # 每次 run() 都是一个新的子任务，所以我们不复用旧历史。
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self._build_user_message(task, context or {})},
        ]

        # 把当前 Agent 允许使用的工具 schema 取出来。
        tool_schemas = [OPENAI_TOOLS[name]["schema"] for name in self.tool_names]
        tool_results: Dict[str, str] = {}

        for _ in range(self.max_rounds):
            # 第 1 步：问模型当前该怎么做。
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tool_schemas,
                tool_choice="auto",
            )
            message = response.choices[0].message

            # 如果模型没有再请求工具，说明它已经准备给出最终回答。
            if not getattr(message, "tool_calls", None):
                return AgentRunResult(self.name, message.content or "", tool_results)

            # 重要：
            # 我们必须把 assistant 的完整 tool_calls 消息回填到历史里，
            # 否则后面的 tool 结果就“找不到对应的调用”。
            messages.append(self._assistant_message_for_history(message))

            # 第 2 步：逐个执行模型要求调用的工具。
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments or "{}")
                tool_output = self._execute_tool(function_name, function_args)
                tool_results[function_name] = tool_output

                print(f"  [{self.name}] 调用工具: {function_name}({function_args})")

                # 第 3 步：把工具结果以 role=tool 的消息形式回填给模型。
                # 这里必须带 tool_call_id，才能和上一个 assistant 的请求对应上。
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_output,
                    }
                )

        # 如果循环次数耗尽，说明这个 Agent 陷入了反复工具调用或没有收敛。
        return AgentRunResult(self.name, "Agent exceeded max_rounds before final answer.", tool_results)

    def _build_user_message(self, task: str, context: Dict[str, Any]) -> str:
        """
        把任务和上游上下文组装成用户消息。

        在 A2A 场景里，这个 context 往往来自另一个远程 Agent。
        所以这里相当于“把远程协作结果注入到当前 Agent 的工作上下文中”。
        """
        if not context:
            return task
        return f"{task}\n\n上下文:\n{json.dumps(context, ensure_ascii=False, indent=2)}"

    def _execute_tool(self, function_name: str, function_args: Dict[str, Any]) -> str:
        """
        真正执行本地工具。

        模型只会“提建议”说它想调哪个工具。
        真正有权限执行工具的，永远是本地 Python 代码。
        """
        if function_name not in self.tool_names:
            return json.dumps({"error": f"Tool not allowed for {self.name}: {function_name}"}, ensure_ascii=False)

        tool_function: Callable[..., str] = OPENAI_TOOLS[function_name]["function"]
        try:
            return tool_function(**function_args)
        except Exception as exc:
            return json.dumps({"error": str(exc)}, ensure_ascii=False)

    def _assistant_message_for_history(self, message: Any) -> Dict[str, Any]:
        """
        把 SDK 返回的 assistant message 转成下一轮请求可复用的历史消息。

        这里专门保留 reasoning_content，是因为 deepseek-v4-pro 在 reasoning 模式下，
        第二轮继续请求时需要把 reasoning_content 一起回传。
        否则 provider 会报 400。
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
# A2A 协议数据结构
# ============================================================

class AgentCard(TypedDict):
    """
    Agent 的“名片”。

    对外暴露的不是内部 prompt，也不是内部工具细节，
    而是一个稳定的能力描述和入口地址。
    """

    id: str
    name: str
    description: str
    capabilities: List[str]
    endpoint: str
    version: str


class A2ATask(TypedDict):
    """
    A2A 请求体。

    这里借用 JSON-RPC 2.0 的通用结构，
    好处是：请求/响应格式统一，错误码和请求 ID 都容易追踪。
    """

    jsonrpc: str
    method: str
    params: Dict[str, Any]
    id: str


class A2AResponse(TypedDict):
    """A2A 响应体。"""

    jsonrpc: str
    result: Optional[Dict[str, Any]]
    error: Optional[Dict[str, Any]]
    id: str


# ============================================================
# A2A Agent 基类
# ============================================================

class A2AOpenAIAgent:
    """
    A2A 兼容 Agent 基类。

    这个类解决的是“对外暴露协议接口”的问题，而不是“内部怎么思考”的问题。
    所以它关心的重点是：
      - GET /card
      - POST /execute

    真正的任务执行逻辑仍然交给子类自己的 execute_task()。
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        capabilities: List[str],
        port: int,
        model: str,
    ):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.port = port
        self.model = model
        self.client = create_client()

    def get_agent_card(self) -> AgentCard:
        """返回标准化 Agent Card。"""
        return {
            "id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "endpoint": f"http://localhost:{self.port}/execute",
            "version": "1.0.0",
        }

    def execute_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        子类必须实现。

        为什么这里不直接写死逻辑？
        因为 Scanner 和 Analyzer 虽然都叫 Agent，
        但职责、工具集、prompt、输入上下文都不同。
        """
        raise NotImplementedError

    def start_server(self) -> None:
        """
        启动 HTTP 服务。

        这是 A2A 最关键的“跨边界”变化：
        在 3.11b 里，Agent 只是本地 Python 对象；
        在 3.12b 里，Agent 变成了别人可以通过 HTTP 调用的服务。
        """
        parent = self

        class A2AHandler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: Any) -> None:
                # 教学演示时关闭 http.server 默认日志，避免输出太乱。
                return

            def do_GET(self) -> None:
                """GET /card -> 暴露 Agent Card。"""
                if self.path != "/card":
                    self.send_response(404)
                    self.end_headers()
                    return

                card = parent.get_agent_card()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(card, ensure_ascii=False).encode("utf-8"))

            def do_POST(self) -> None:
                """POST /execute -> 执行远程任务。"""
                if self.path != "/execute":
                    self.send_response(404)
                    self.end_headers()
                    return

                content_length = int(self.headers["Content-Length"])
                body = self.rfile.read(content_length).decode("utf-8")
                request_id = "unknown"

                try:
                    request: A2ATask = json.loads(body)
                    request_id = request["id"]
                    task = request["params"]["task"]
                    context = request["params"].get("context", {})

                    result = parent.execute_task(task, context)
                    response: A2AResponse = {
                        "jsonrpc": "2.0",
                        "result": result,
                        "error": None,
                        "id": request_id,
                    }
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
                except Exception as exc:
                    error_response: A2AResponse = {
                        "jsonrpc": "2.0",
                        "result": None,
                        "error": {"code": -32603, "message": str(exc)},
                        "id": request_id,
                    }
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode("utf-8"))

        server = HTTPServer(("localhost", self.port), A2AHandler)
        print(f"[{self.name}] A2A Agent 启动在 http://localhost:{self.port}")
        print(f"[{self.name}] Agent Card 地址: http://localhost:{self.port}/card")
        server.serve_forever()


# ============================================================
# 具体 Agent：Scanner / Analyzer
# ============================================================

class ScannerAgent(A2AOpenAIAgent):
    """
    扫描 Agent。

    职责非常单一：
      - 接收“请扫描某个目标”的任务
      - 用 scan_ports 工具完成扫描
      - 返回扫描结果
    """

    def __init__(self, port: int = 8001, model: Optional[str] = None):
        super().__init__(
            agent_id="scanner-agent-001",
            name="Scanner Agent",
            description="执行网络端口扫描和主机发现",
            capabilities=["port_scan", "host_discovery"],
            port=port,
            model=model or get_model(),
        )
        self.runtime = OpenAIToolAgent(
            name="Scanner Agent Runtime",
            system_prompt=(
                "你是网络扫描专家。"
                "只负责识别目标并调用 scan_ports 工具。"
                "完成后用简洁中文总结扫描结果。"
            ),
            tool_names=["scan_ports"],
            client=self.client,
            model=self.model,
        )

    def execute_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        result = self.runtime.run(task, context)
        return {"status": "completed", "output": result.output, "tool_results": result.tool_results}


class AnalyzerAgent(A2AOpenAIAgent):
    """
    分析 Agent。

    它不重新扫描网络，而是消费上游 Scanner 提供的上下文，
    然后调用 analyze_risk 给出风险判断。
    """

    def __init__(self, port: int = 8002, model: Optional[str] = None):
        super().__init__(
            agent_id="analyzer-agent-001",
            name="Analyzer Agent",
            description="分析扫描结果并评估安全风险",
            capabilities=["risk_analysis", "vulnerability_assessment"],
            port=port,
            model=model or get_model(),
        )
        self.runtime = OpenAIToolAgent(
            name="Analyzer Agent Runtime",
            system_prompt=(
                "你是安全分析专家。"
                "只负责基于扫描结果判断风险，必要时调用 analyze_risk。"
                "最后输出风险等级和关键发现。"
            ),
            tool_names=["analyze_risk"],
            client=self.client,
            model=self.model,
        )

    def execute_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        result = self.runtime.run(task, context)
        return {"status": "completed", "output": result.output, "tool_results": result.tool_results}


# ============================================================
# A2A 协调器
# ============================================================

class A2AOrchestrator:
    """
    A2A 协调器。

    这一层在做的事情非常像 3.11b 的 Supervisor，
    但区别是：它调度的不是“本地 Python 对象”，而是“远程 Agent 服务”。
    """

    def __init__(self):
        self.agents: Dict[str, AgentCard] = {}

    def discover_agent(self, endpoint: str) -> AgentCard:
        """
        发现一个远程 Agent。

        endpoint 传的是 /execute 地址，
        我们再推导出 /card 地址去拿名片。
        """
        card_url = endpoint.replace("/execute", "/card")
        resp = requests.get(card_url, timeout=10)
        resp.raise_for_status()
        card: AgentCard = resp.json()
        self.agents[card["id"]] = card
        print(f"[Orchestrator] 发现 Agent: {card['name']} ({card['id']})")
        print(f"[Orchestrator]   能力: {', '.join(card['capabilities'])}")
        return card

    def send_task(self, agent_id: str, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        通过 JSON-RPC over HTTP 给指定 Agent 发送任务。

        这里要特别注意：
        在 A2A 里，调用方不直接碰对方内部的 Python 函数。
        调用方只知道：
          - endpoint
          - request schema
          - response schema
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} 未发现")

        card = self.agents[agent_id]
        request: A2ATask = {
            "jsonrpc": "2.0",
            "method": "agent.execute",
            "params": {"task": task, "context": context or {}},
            "id": f"task-{datetime.now().timestamp()}",
        }

        print(f"[Orchestrator] 发送任务到 {card['name']}: {task}")
        resp = requests.post(card["endpoint"], json=request, timeout=60)
        resp.raise_for_status()
        response: A2AResponse = resp.json()

        if response["error"]:
            raise RuntimeError(f"Agent 返回错误: {response['error']}")

        return response["result"] or {}

    def run_workflow(self, target: str) -> None:
        """
        运行一个最小 A2A 安全评估工作流。

        流程和 3.11b 很像：
          Scanner -> Analyzer

        但现在 Scanner 和 Analyzer 不是本地函数调用，
        而是两个独立 HTTP 服务。
        """
        print("\n" + "=" * 60)
        print(f"A2A 工作流（OpenAI SDK 版）: 安全评估 {target}")
        print("=" * 60)

        print("\n步骤 1: 发现 Scanner Agent")
        scanner_card = self.discover_agent("http://localhost:8001/execute")

        print("\n步骤 2: 发送扫描任务")
        scan_result = self.send_task(
            scanner_card["id"],
            f"扫描 {target} 的常用端口（22, 80, 443, 3306, 8080）",
        )

        print("\n步骤 3: 发现 Analyzer Agent")
        analyzer_card = self.discover_agent("http://localhost:8002/execute")

        # 优先传结构化工具结果，而不是自然语言 output。
        # 这是 A2A / Multi-Agent 场景里很重要的一条经验：
        # 上下游 Agent 之间尽量传结构化数据，减少解析歧义。
        scan_context = {
            "scan_result": scan_result.get("tool_results", {}).get("scan_ports", scan_result.get("output", ""))
        }

        print("\n步骤 4: 发送分析任务")
        analysis_result = self.send_task(
            analyzer_card["id"],
            "分析扫描结果并评估安全风险",
            context=scan_context,
        )

        print("\n" + "=" * 60)
        print("最终汇总")
        print("=" * 60)
        print(f"目标: {target}")
        print(f"\nScanner 输出:\n{scan_result.get('output', '')}")
        print(f"\nAnalyzer 输出:\n{analysis_result.get('output', '')}")


# ============================================================
# 主程序
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="A2A 协议与 Agent 互操作（OpenAI SDK 版）")
    parser.add_argument("mode", choices=["scanner", "analyzer", "orchestrator"], help="运行模式")
    parser.add_argument("target", nargs="?", default="localhost", help="orchestrator 模式下的扫描目标")
    parser.add_argument("--model", default=get_model(), help="OpenAI 模型名称")
    args = parser.parse_args()

    if args.mode == "scanner":
        agent = ScannerAgent(port=8001, model=args.model)
        agent.start_server()
        return

    if args.mode == "analyzer":
        agent = AnalyzerAgent(port=8002, model=args.model)
        agent.start_server()
        return

    # 给前两个终端一点启动时间。
    # 真实系统里通常会用服务发现或健康检查，这里先用最小教学写法。
    time.sleep(1)
    orchestrator = A2AOrchestrator()
    orchestrator.run_workflow(args.target)


if __name__ == "__main__":
    main()
