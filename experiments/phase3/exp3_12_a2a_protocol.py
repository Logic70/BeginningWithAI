"""
实验 3.12: A2A 协议与 Agent 互操作
理解 A2A 作为跨框架 Agent 通信标准的定位

核心问题：为什么需要 A2A？
  场景 1：跨团队协作
    - 你的团队用 LangChain 开发了扫描 Agent
    - 另一个团队用 AutoGen 开发了分析 Agent
    - 如何让两个 Agent 协作？

  场景 2：第三方 Agent 集成
    - 你想调用 Google 提供的翻译 Agent
    - 你想调用 Salesforce 提供的 CRM Agent
    - 如何发现和调用这些 Agent？

  A2A 的解法：
    - 标准化的 Agent Card（描述 Agent 能力）
    - 标准化的任务发送/结果返回协议（JSON-RPC over HTTP）
    - 跨框架、跨语言、跨组织的互操作

A2A 协议现状（2026.3）：
  - Linux Foundation 治理（2025.8 从 Google 捐赠）
  - 150+ 组织支持（Google, Microsoft, IBM, Anthropic, SAP...）
  - v0.3 版本（2025.7）：gRPC 支持、签名安全卡、Python SDK

A2A vs MCP 的互补关系：
  ┌─────────────────────────────────────────────────┐
  │                  Your Agent                     │
  │  ┌──────────────────────────────────────────┐   │
  │  │  使用 MCP 调用垂直工具                    │   │
  │  │  ├─ Database (MCP Server)                │   │
  │  │  ├─ File System (MCP Server)             │   │
  │  │  └─ API Gateway (MCP Server)             │   │
  │  └──────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────┘
                      ↕ A2A 协议
  ┌─────────────────────────────────────────────────┐
  │              External Agent (第三方)             │
  │  ┌──────────────────────────────────────────┐   │
  │  │  使用 MCP 调用它自己的工具                │   │
  │  │  ├─ Inventory DB (MCP Server)            │   │
  │  │  └─ Shipping API (MCP Server)            │   │
  │  └──────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────┘

  MCP：Agent 内部的工具调用（垂直）
  A2A：Agent 之间的任务协作（水平）

与前面实验的关系：
  - 3.4 MCP：工具服务化 → 本实验：Agent 服务化
  - 3.11 多 Agent：同一进程内协作 → 本实验：跨进程/跨网络协作
"""

# ==================== 导入 ====================
import os
import json
import socket
import asyncio
from pathlib import Path
from typing import TypedDict, Optional
from dotenv import load_dotenv
from datetime import datetime

# HTTP 服务
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import requests

# LangChain（用于 Agent 实现）
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage

# ==================== 配置 ====================
load_dotenv(Path(__file__).parent.parent.parent / ".env")


def get_llm(backend: str = "ollama"):
    """获取 LLM 实例"""
    if backend == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "deepseek-v4-pro"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    return ChatOllama(model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"))


# ============================================================
# A2A 协议核心数据结构
# ============================================================

class AgentCard(TypedDict):
    """
    Agent Card：Agent 的"名片"
    类似 OpenAPI Spec，描述 Agent 的能力和接口

    A2A v0.3 标准字段：
      - id: Agent 唯一标识
      - name: 人类可读名称
      - description: 能力描述
      - capabilities: 支持的任务类型
      - endpoint: 任务提交地址
      - version: Agent 版本
    """
    id: str
    name: str
    description: str
    capabilities: list[str]
    endpoint: str
    version: str


class A2ATask(TypedDict):
    """
    A2A 任务请求
    遵循 JSON-RPC 2.0 格式
    """
    jsonrpc: str              # 固定 "2.0"
    method: str               # 固定 "agent.execute"
    params: dict              # 任务参数 {"task": "...", "context": {...}}
    id: str                   # 请求 ID


class A2AResponse(TypedDict):
    """
    A2A 任务响应
    """
    jsonrpc: str
    result: Optional[dict]    # 成功时返回结果
    error: Optional[dict]     # 失败时返回错误
    id: str


# ============================================================
# 安全工具（复用前面实验的逻辑）
# ============================================================

@tool
def scan_ports(host: str, ports: str = "22,80,443,3306,8080") -> str:
    """扫描目标主机的指定端口"""
    port_list = [int(p.strip()) for p in ports.split(",")]
    results = {}
    for port in port_list:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            status = "open" if sock.connect_ex((host, port)) == 0 else "closed"
            results[port] = status
            sock.close()
        except Exception:
            results[port] = "error"
    return json.dumps({"host": host, "ports": results}, ensure_ascii=False)


@tool
def analyze_risk(scan_data: str) -> str:
    """分析扫描数据的安全风险"""
    try:
        data = json.loads(scan_data)
    except json.JSONDecodeError:
        data = {"raw": scan_data}

    risks = []
    high_risk_ports = {3306: "MySQL", 6379: "Redis", 27017: "MongoDB"}
    medium_risk_ports = {22: "SSH", 8080: "HTTP-Alt"}

    if "ports" in data:
        for port_str, status in data["ports"].items():
            port = int(port_str)
            if status == "open":
                if port in high_risk_ports:
                    risks.append(f"HIGH: 端口 {port} ({high_risk_ports[port]}) 对外开放")
                elif port in medium_risk_ports:
                    risks.append(f"MEDIUM: 端口 {port} ({medium_risk_ports[port]}) 开放")

    overall = "HIGH" if any("HIGH" in r for r in risks) else "MEDIUM" if risks else "LOW"
    return json.dumps({
        "overall_risk": overall,
        "findings": risks if risks else ["未发现明显风险"],
    }, ensure_ascii=False)


# ============================================================
# A2A Agent 实现
# ============================================================

class A2AAgent:
    """
    A2A 兼容的 Agent 基类
    实现 Agent Card 发布和任务执行接口
    """

    def __init__(self, agent_id: str, name: str, description: str,
                 capabilities: list[str], port: int, backend: str = "ollama"):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.port = port
        self.backend = backend
        self.llm = get_llm(backend)
        self.tools = []

    def get_agent_card(self) -> AgentCard:
        """返回 Agent Card"""
        return {
            "id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "endpoint": f"http://localhost:{self.port}/execute",
            "version": "1.0.0"
        }

    def execute_task(self, task: str, context: dict = None) -> dict:
        """
        执行任务的核心逻辑
        子类需要实现具体的任务处理
        """
        raise NotImplementedError

    def start_server(self):
        """启动 HTTP 服务器，监听 A2A 请求"""
        agent = self

        class A2AHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # 禁用默认日志

            def do_GET(self):
                """GET /card - 返回 Agent Card"""
                if self.path == "/card":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    card = agent.get_agent_card()
                    self.wfile.write(json.dumps(card, ensure_ascii=False).encode())
                else:
                    self.send_response(404)
                    self.end_headers()

            def do_POST(self):
                """POST /execute - 执行任务"""
                if self.path == "/execute":
                    content_length = int(self.headers['Content-Length'])
                    body = self.rfile.read(content_length).decode()
                    try:
                        request: A2ATask = json.loads(body)
                        task = request["params"]["task"]
                        context = request["params"].get("context", {})

                        # 执行任务
                        result = agent.execute_task(task, context)

                        # 返回 A2A 响应
                        response: A2AResponse = {
                            "jsonrpc": "2.0",
                            "result": result,
                            "error": None,
                            "id": request["id"]
                        }
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
                    except Exception as e:
                        error_response: A2AResponse = {
                            "jsonrpc": "2.0",
                            "result": None,
                            "error": {"code": -32603, "message": str(e)},
                            "id": request.get("id", "unknown")
                        }
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode())
                else:
                    self.send_response(404)
                    self.end_headers()

        server = HTTPServer(("localhost", self.port), A2AHandler)
        print(f"  [{self.name}] A2A Agent 启动在 http://localhost:{self.port}")
        print(f"  [{self.name}] Agent Card: http://localhost:{self.port}/card")
        server.serve_forever()


# ============================================================
# 具体 Agent 实现
# ============================================================

class ScannerAgent(A2AAgent):
    """扫描 Agent：负责端口扫描"""

    def __init__(self, port: int = 8001, backend: str = "ollama"):
        super().__init__(
            agent_id="scanner-agent-001",
            name="Scanner Agent",
            description="执行网络端口扫描和主机发现",
            capabilities=["port_scan", "host_discovery"],
            port=port,
            backend=backend
        )
        self.tools = [scan_ports]

    def execute_task(self, task: str, context: dict = None) -> dict:
        """执行扫描任务"""
        print(f"  [Scanner] 收到任务: {task}")

        # 使用 LLM + 工具执行任务
        from langchain.agents import create_tool_calling_agent, AgentExecutor
        from langchain_core.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个网络扫描专家。使用 scan_ports 工具完成任务。"),
            ("human", "{input}")
        ])

        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        executor = AgentExecutor(agent=agent, tools=self.tools, verbose=False)

        result = executor.invoke({"input": task})
        return {"status": "completed", "output": result["output"]}


class AnalyzerAgent(A2AAgent):
    """分析 Agent：负责风险分析"""

    def __init__(self, port: int = 8002, backend: str = "ollama"):
        super().__init__(
            agent_id="analyzer-agent-001",
            name="Analyzer Agent",
            description="分析扫描结果并评估安全风险",
            capabilities=["risk_analysis", "vulnerability_assessment"],
            port=port,
            backend=backend
        )
        self.tools = [analyze_risk]

    def execute_task(self, task: str, context: dict = None) -> dict:
        """执行分析任务"""
        print(f"  [Analyzer] 收到任务: {task}")
        print(f"  [Analyzer] 上下文: {context}")

        from langchain.agents import create_tool_calling_agent, AgentExecutor
        from langchain_core.prompts import ChatPromptTemplate

        # 将上下文注入到任务中
        full_task = task
        if context and "scan_result" in context:
            full_task += f"\n\n扫描结果:\n{context['scan_result']}"

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个安全分析专家。使用 analyze_risk 工具分析扫描数据。"),
            ("human", "{input}")
        ])

        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        executor = AgentExecutor(agent=agent, tools=self.tools, verbose=False)

        result = executor.invoke({"input": full_task})
        return {"status": "completed", "output": result["output"]}


# ============================================================
# A2A Orchestrator（协调器）
# ============================================================

class A2AOrchestrator:
    """
    A2A 协调器：发现和调用 A2A Agent

    核心流程：
      1. 发现 Agent（GET /card）
      2. 发送任务（POST /execute）
      3. 接收结果
      4. 传递上下文给下一个 Agent
    """

    def __init__(self):
        self.agents: dict[str, AgentCard] = {}

    def discover_agent(self, endpoint: str) -> AgentCard:
        """发现 Agent（获取 Agent Card）"""
        card_url = endpoint.replace("/execute", "/card")
        try:
            resp = requests.get(card_url, timeout=5)
            resp.raise_for_status()
            card: AgentCard = resp.json()
            self.agents[card["id"]] = card
            print(f"  [Orchestrator] 发现 Agent: {card['name']} ({card['id']})")
            print(f"  [Orchestrator]   能力: {', '.join(card['capabilities'])}")
            return card
        except Exception as e:
            print(f"  [Orchestrator] 发现失败: {e}")
            raise

    def send_task(self, agent_id: str, task: str, context: dict = None) -> dict:
        """发送任务给指定 Agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} 未发现")

        card = self.agents[agent_id]
        request: A2ATask = {
            "jsonrpc": "2.0",
            "method": "agent.execute",
            "params": {"task": task, "context": context or {}},
            "id": f"task-{datetime.now().timestamp()}"
        }

        print(f"  [Orchestrator] 发送任务到 {card['name']}: {task}")
        try:
            resp = requests.post(card["endpoint"], json=request, timeout=30)
            resp.raise_for_status()
            response: A2AResponse = resp.json()

            if response["error"]:
                raise Exception(f"Agent 返回错误: {response['error']}")

            print(f"  [Orchestrator] 收到结果: {response['result']['status']}")
            return response["result"]
        except Exception as e:
            print(f"  [Orchestrator] 任务执行失败: {e}")
            raise

    def run_workflow(self, target: str):
        """运行完整的安全评估工作流"""
        print(f"\n{'='*60}")
        print(f"A2A 工作流: 安全评估 {target}")
        print(f"{'='*60}\n")

        # 步骤 1: 发现 Scanner Agent
        print("步骤 1: 发现 Scanner Agent")
        scanner_card = self.discover_agent("http://localhost:8001/execute")

        # 步骤 2: 发送扫描任务
        print("\n步骤 2: 发送扫描任务")
        scan_result = self.send_task(
            scanner_card["id"],
            f"扫描 {target} 的常用端口（22, 80, 443, 3306, 8080）"
        )

        # 步骤 3: 发现 Analyzer Agent
        print("\n步骤 3: 发现 Analyzer Agent")
        analyzer_card = self.discover_agent("http://localhost:8002/execute")

        # 步骤 4: 发送分析任务（传递扫描结果作为上下文）
        print("\n步骤 4: 发送分析任务")
        analysis_result = self.send_task(
            analyzer_card["id"],
            "分析扫描结果并评估安全风险",
            context={"scan_result": scan_result["output"]}
        )

        # 步骤 5: 汇总结果
        print(f"\n{'='*60}")
        print("最终报告")
        print(f"{'='*60}\n")
        print(f"目标: {target}")
        print(f"\n扫描结果:\n{scan_result['output']}")
        print(f"\n风险分析:\n{analysis_result['output']}")


# ============================================================
# 主程序
# ============================================================

def main():
    import sys
    import time

    if len(sys.argv) < 2:
        print("用法:")
        print("  # 启动 Scanner Agent")
        print("  python exp3_12_a2a_protocol.py scanner [--backend openai]")
        print()
        print("  # 启动 Analyzer Agent")
        print("  python exp3_12_a2a_protocol.py analyzer [--backend openai]")
        print()
        print("  # 运行 Orchestrator（需要先启动两个 Agent）")
        print("  python exp3_12_a2a_protocol.py orchestrator <target>")
        print()
        print("完整流程:")
        print("  1. 终端 1: python exp3_12_a2a_protocol.py scanner")
        print("  2. 终端 2: python exp3_12_a2a_protocol.py analyzer")
        print("  3. 终端 3: python exp3_12_a2a_protocol.py orchestrator localhost")
        return

    mode = sys.argv[1]
    backend = "openai" if "--backend" in sys.argv and sys.argv[sys.argv.index("--backend") + 1] == "openai" else "ollama"

    if mode == "scanner":
        print(f"启动 Scanner Agent (backend: {backend})...")
        agent = ScannerAgent(port=8001, backend=backend)
        agent.start_server()

    elif mode == "analyzer":
        print(f"启动 Analyzer Agent (backend: {backend})...")
        agent = AnalyzerAgent(port=8002, backend=backend)
        agent.start_server()

    elif mode == "orchestrator":
        if len(sys.argv) < 3:
            print("错误: 需要指定目标")
            print("用法: python exp3_12_a2a_protocol.py orchestrator <target>")
            return

        target = sys.argv[2]
        print("等待 Agent 启动...")
        time.sleep(2)

        orchestrator = A2AOrchestrator()
        orchestrator.run_workflow(target)

    else:
        print(f"未知模式: {mode}")
        print("支持的模式: scanner, analyzer, orchestrator")


if __name__ == "__main__":
    main()
