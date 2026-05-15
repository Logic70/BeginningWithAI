"""
实验 3.11: 多 Agent 编排模式
理解 Supervisor 和 Swarm 两种主流多 Agent 架构

核心问题：为什么需要多 Agent？
  单 Agent 的天花板：
  1. 上下文窗口有限 — 工具太多时描述占满 context
  2. 职责模糊 — 一个 Agent 又要扫描又要分析，容易混乱
  3. 错误传播 — 一步出错影响全局

  多 Agent 的解法：
  1. 分而治之 — 每个 Agent 专注一个领域
  2. 独立上下文 — 各 Agent 有自己的 system prompt 和工具集
  3. 故障隔离 — 一个 Agent 出错不影响其他

两种架构模式：

  Supervisor（中心调度）:
  ┌─────────────┐
  │  Supervisor  │ ← 决定调用哪个 Agent
  │  (协调器)    │
  └──────┬──────┘
         ├─────────────┬──────────────┐
    ┌────▼────┐  ┌─────▼─────┐  ┌────▼────┐
    │ Scanner │  │ Analyzer  │  │ Reporter│
    │  Agent  │  │  Agent    │  │  Agent  │
    └─────────┘  └───────────┘  └─────────┘

  Swarm（去中心化）:
  ┌─────────┐  handoff  ┌───────────┐  handoff  ┌─────────┐
  │ Scanner │ ────────→ │ Analyzer  │ ────────→ │ Reporter│
  │  Agent  │ ←──────── │  Agent    │ ←──────── │  Agent  │
  └─────────┘           └───────────┘           └─────────┘
  每个 Agent 自主决定"下一步交给谁"

与前面实验的关系：
  - 3.2 ReAct Agent：单 Agent 循环 → 本实验：多 Agent 协作
  - 3.10 LangGraph 工作流：固定节点图 → 本实验：Agent 作为节点，动态调度
"""

# ==================== 导入 ====================
import os
import json
import socket
from pathlib import Path
from typing import TypedDict, Literal, Annotated
from dotenv import load_dotenv
import operator

# LangGraph
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

# LangChain
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage

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
# 安全工具定义（@tool 装饰器，与 exp3_1c/exp3_2c 一致）
# ============================================================

@tool
def scan_ports(host: str, ports: str = "22,80,443,3306,8080") -> str:
    """扫描目标主机的指定端口是否开放

    Args:
        host: 目标主机 IP 或域名
        ports: 逗号分隔的端口号列表
    """
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
def check_http(url: str) -> str:
    """检查目标 URL 的 HTTP 响应头信息

    Args:
        url: 目标 URL（如 http://localhost）
    """
    import urllib.request
    try:
        if not url.startswith("http"):
            url = f"http://{url}"
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "SecurityAudit/1.0")
        with urllib.request.urlopen(req, timeout=5) as resp:
            headers = {k: v for k, v in resp.headers.items()
                        if k.lower() in ("server", "x-powered-by", "content-type")}
            return json.dumps({"status": resp.status, "headers": headers}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def analyze_risk(scan_data: str) -> str:
    """分析扫描数据的安全风险等级

    Args:
        scan_data: JSON 格式的扫描结果数据
    """
    try:
        data = json.loads(scan_data)
    except json.JSONDecodeError:
        data = {"raw": scan_data}

    risks = []
    high_risk_ports = {3306: "MySQL", 6379: "Redis", 27017: "MongoDB", 5432: "PostgreSQL"}
    medium_risk_ports = {22: "SSH", 21: "FTP", 8080: "HTTP-Alt", 8443: "HTTPS-Alt"}

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


@tool
def generate_report(target: str, findings: str) -> str:
    """生成安全评估报告

    Args:
        target: 评估目标
        findings: JSON 格式的分析发现
    """
    try:
        data = json.loads(findings)
    except json.JSONDecodeError:
        data = {"raw": findings}

    report = f"# 安全评估报告\n\n"
    report += f"**目标**: {target}\n"
    report += f"**风险等级**: {data.get('overall_risk', 'UNKNOWN')}\n\n"
    report += "## 发现\n\n"
    for finding in data.get("findings", []):
        report += f"- {finding}\n"
    return report


# ============================================================
# 方案 A: Supervisor 模式
# ============================================================
# Supervisor 是一个"调度 Agent"，它拥有一个特殊的工具集：
# 调用其他 Agent。它决定任务分配顺序。

class SupervisorState(TypedDict):
    """Supervisor 状态 — 追踪整个协作流程"""
    messages: Annotated[list[BaseMessage], operator.add]
    next_agent: str
    scan_result: str
    analysis_result: str
    report: str


def build_supervisor_workflow(backend: str = "ollama"):
    """
    构建 Supervisor 多 Agent 工作流

    架构：
      Supervisor → Scanner Agent → Supervisor → Analyzer Agent → Supervisor → Reporter Agent → END

    Supervisor 的核心逻辑：
      - 读取当前状态
      - 决定下一步调用哪个 Agent（或结束）
      - 将任务分配给对应 Agent
    """
    llm = get_llm(backend)

    # --- 定义各 Agent 的节点函数 ---

    def supervisor_node(state: SupervisorState) -> dict:
        """Supervisor: 根据当前进度决定下一步"""
        # 用 LLM 决策，还是用规则决策？
        # 生产中常用规则（更可控），教学中展示 LLM 决策
        if not state.get("scan_result"):
            print("  [Supervisor] → 分配给 Scanner Agent")
            return {"next_agent": "scanner"}
        elif not state.get("analysis_result"):
            print("  [Supervisor] → 分配给 Analyzer Agent")
            return {"next_agent": "analyzer"}
        elif not state.get("report"):
            print("  [Supervisor] → 分配给 Reporter Agent")
            return {"next_agent": "reporter"}
        else:
            print("  [Supervisor] → 任务完成")
            return {"next_agent": "done"}

    def scanner_node(state: SupervisorState) -> dict:
        """Scanner Agent: 专注于信息收集"""
        print("  [Scanner Agent] 执行扫描...")
        # 从最近的消息中获取目标
        last_msg = state["messages"][-1].content if state["messages"] else "localhost"
        # 提取目标（简单解析）
        target = last_msg.strip().split()[-1] if last_msg else "localhost"

        result = scan_ports.invoke({"host": target, "ports": "22,80,443,3306,8080"})
        print(f"  [Scanner Agent] 扫描完成")
        return {"scan_result": result}

    def analyzer_node(state: SupervisorState) -> dict:
        """Analyzer Agent: 专注于风险分析"""
        print("  [Analyzer Agent] 分析风险...")
        result = analyze_risk.invoke({"scan_data": state["scan_result"]})
        print(f"  [Analyzer Agent] 分析完成")
        return {"analysis_result": result}

    def reporter_node(state: SupervisorState) -> dict:
        """Reporter Agent: 专注于报告生成"""
        print("  [Reporter Agent] 生成报告...")
        last_msg = state["messages"][-1].content if state["messages"] else "unknown"
        target = last_msg.strip().split()[-1] if last_msg else "unknown"
        result = generate_report.invoke({
            "target": target,
            "findings": state["analysis_result"],
        })
        print(f"  [Reporter Agent] 报告完成")
        return {"report": result}

    # --- 路由函数 ---
    def route_next(state: SupervisorState) -> str:
        return state["next_agent"]

    # --- 构建图 ---
    workflow = StateGraph(SupervisorState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("scanner", scanner_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("reporter", reporter_node)

    workflow.set_entry_point("supervisor")

    # Supervisor 根据 next_agent 路由
    workflow.add_conditional_edges(
        "supervisor",
        route_next,
        {
            "scanner": "scanner",
            "analyzer": "analyzer",
            "reporter": "reporter",
            "done": END,
        }
    )

    # 各 Agent 完成后回到 Supervisor
    workflow.add_edge("scanner", "supervisor")
    workflow.add_edge("analyzer", "supervisor")
    workflow.add_edge("reporter", "supervisor")

    return workflow.compile()


# ============================================================
# 方案 B: Swarm 模式（简化版）
# ============================================================
# Swarm 的核心区别：没有中心调度器
# 每个 Agent 自己决定"下一步交给谁"

class SwarmState(TypedDict):
    """Swarm 状态"""
    messages: Annotated[list[BaseMessage], operator.add]
    current_agent: str
    scan_result: str
    analysis_result: str
    report: str


def build_swarm_workflow(backend: str = "ollama"):
    """
    构建 Swarm 多 Agent 工作流

    与 Supervisor 的区别：
      Supervisor: Agent → Supervisor → Agent → Supervisor → ...
      Swarm:      Agent → Agent → Agent → END（直接 handoff）

    优势：减少 Supervisor 的"翻译"开销，更少 token 消耗
    劣势：每个 Agent 需要知道其他 Agent 的存在
    """

    def scanner_node(state: SwarmState) -> dict:
        """Scanner → 完成后直接 handoff 给 Analyzer"""
        print("  [Scanner] 执行扫描...")
        last_msg = state["messages"][-1].content if state["messages"] else "localhost"
        target = last_msg.strip().split()[-1] if last_msg else "localhost"
        result = scan_ports.invoke({"host": target, "ports": "22,80,443,3306,8080"})
        print("  [Scanner] → handoff to Analyzer")
        return {"scan_result": result, "current_agent": "analyzer"}

    def analyzer_node(state: SwarmState) -> dict:
        """Analyzer → 完成后直接 handoff 给 Reporter"""
        print("  [Analyzer] 分析风险...")
        result = analyze_risk.invoke({"scan_data": state["scan_result"]})
        print("  [Analyzer] → handoff to Reporter")
        return {"analysis_result": result, "current_agent": "reporter"}

    def reporter_node(state: SwarmState) -> dict:
        """Reporter → 生成报告后结束"""
        print("  [Reporter] 生成报告...")
        last_msg = state["messages"][-1].content if state["messages"] else "unknown"
        target = last_msg.strip().split()[-1] if last_msg else "unknown"
        result = generate_report.invoke({
            "target": target,
            "findings": state["analysis_result"],
        })
        print("  [Reporter] → 完成")
        return {"report": result, "current_agent": "done"}

    def route_swarm(state: SwarmState) -> str:
        """Swarm 路由：每个 Agent 设置 current_agent 来决定下一跳"""
        return state["current_agent"]

    workflow = StateGraph(SwarmState)

    workflow.add_node("scanner", scanner_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("reporter", reporter_node)

    workflow.set_entry_point("scanner")

    # 每个节点都用条件路由实现 handoff
    for node in ["scanner", "analyzer", "reporter"]:
        workflow.add_conditional_edges(
            node,
            route_swarm,
            {
                "scanner": "scanner",
                "analyzer": "analyzer",
                "reporter": "reporter",
                "done": END,
            }
        )

    return workflow.compile()


# ============================================================
# 演示
# ============================================================

def demo_supervisor(target: str, backend: str = "ollama"):
    """演示 Supervisor 模式"""
    print("\n" + "=" * 60)
    print("演示: Supervisor 模式（中心调度）")
    print("=" * 60)
    print("  流程: Supervisor → Scanner → Supervisor → Analyzer → Supervisor → Reporter → END")

    app = build_supervisor_workflow(backend)
    result = app.invoke({
        "messages": [HumanMessage(content=f"请对 {target} 进行安全评估")],
        "next_agent": "",
        "scan_result": "",
        "analysis_result": "",
        "report": "",
    })

    print(f"\n📋 报告:\n{result['report']}")
    return result


def demo_swarm(target: str, backend: str = "ollama"):
    """演示 Swarm 模式"""
    print("\n" + "=" * 60)
    print("演示: Swarm 模式（去中心化 Handoff）")
    print("=" * 60)
    print("  流程: Scanner → Analyzer → Reporter → END（无中心调度）")

    app = build_swarm_workflow(backend)
    result = app.invoke({
        "messages": [HumanMessage(content=f"请对 {target} 进行安全评估")],
        "current_agent": "scanner",
        "scan_result": "",
        "analysis_result": "",
        "report": "",
    })

    print(f"\n📋 报告:\n{result['report']}")
    return result


def demo_comparison(target: str, backend: str = "ollama"):
    """对比两种模式"""
    print("\n" + "=" * 60)
    print("对比: Supervisor vs Swarm")
    print("=" * 60)

    print("\n--- Supervisor 模式 ---")
    r1 = demo_supervisor(target, backend)

    print("\n--- Swarm 模式 ---")
    r2 = demo_swarm(target, backend)

    print("\n" + "=" * 60)
    print("📊 对比总结")
    print("=" * 60)
    print("""
  | 特性         | Supervisor        | Swarm              |
  |-------------|-------------------|--------------------|
  | 调度方式      | 中心化             | 去中心化            |
  | Token 消耗   | 较高（经过 Supervisor 翻译）| 较低（直接 handoff）|
  | 灵活性       | 高（可动态调整顺序）  | 中（handoff 路径固定）|
  | 错误处理      | Supervisor 统一处理  | 各 Agent 自行处理   |
  | 适用场景      | 结构化任务、需要审批   | 流水线任务、灵活协作  |
  | 第三方 Agent  | ✅ 支持             | ❌ 需要互相了解      |
    """)


# ============================================================
# 主入口
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="多 Agent 编排模式演示")
    parser.add_argument("target", nargs="?", default="localhost",
                        help="评估目标 (默认: localhost)")
    parser.add_argument("--backend", choices=["ollama", "openai"], default="ollama")
    parser.add_argument("--mode", choices=["supervisor", "swarm", "compare"],
                        default="compare", help="演示模式")
    args = parser.parse_args()

    if args.mode == "supervisor":
        demo_supervisor(args.target, args.backend)
    elif args.mode == "swarm":
        demo_swarm(args.target, args.backend)
    else:
        demo_comparison(args.target, args.backend)
