"""
实验 3.10: LangGraph 工作流编排
从线性流水线进化到真正的条件路由、循环和人工审批

核心概念：
  - 线性图：A → B → C（前面实验已学过）
  - 条件路由：根据状态动态选择下一个节点
  - 循环：ReAct 模式的图表达
  - Human-in-the-loop：高危操作前暂停等待人工确认
  - 检查点：保存图执行状态，支持中断恢复

工作流示意：
  ┌──────────┐     ┌───────────┐     ┌──────────────────┐
  │  recon   │────→│  router   │────→│ web_analysis     │──┐
  │(信息收集) │     │ (条件路由) │  ├→│ port_analysis    │  ├→ report
  └──────────┘     └───────────┘  ├→│ comprehensive    │  │
                                  │  └──────────────────┘  │
                                  │                        │
                                  │  ┌──────────────────┐  │
                                  └→│ human_review     │──┘
                                     │ (高危时人工确认)  │
                                     └──────────────────┘

与前面实验的关系：
  - 3.1 Function Calling：模型调用单个工具 → 本实验：多步骤工具编排
  - 3.2 ReAct Agent：手写循环 → 本实验：LangGraph 声明式图
  - 3.4 MCP：工具服务化 → 本实验：工作流级别的编排
"""

# ==================== 导入 ====================
import os
import json
import socket
from pathlib import Path
from typing import TypedDict, Literal, Annotated
from dotenv import load_dotenv

# LangGraph 核心
from langgraph.graph import StateGraph, END
# StateGraph: 有状态图，节点共享可变状态
# END: 特殊节点，标记图的终点

from langgraph.checkpoint.memory import InMemorySaver
# InMemorySaver: 内存检查点，支持 interrupt 和状态恢复
# 生产环境可替换为 SqliteSaver / PostgresSaver

from langgraph.types import interrupt, Command
# interrupt: 暂停图执行，等待外部输入（Human-in-the-loop 核心）
# Command: 从 interrupt 恢复时，可以指定跳转到哪个节点

# LangChain LLM 封装
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# ==================== 配置 ====================
load_dotenv(Path(__file__).parent.parent.parent / ".env")


# ============================================================
# 状态定义
# ============================================================
# LangGraph 的核心：所有节点共享一个 TypedDict 状态
# 每个节点读取状态、返回部分更新，框架自动合并

class SecurityState(TypedDict):
    """安全评估工作流状态"""
    target: str               # 评估目标
    analysis_type: str         # 分析类型: web / port / comprehensive
    recon_result: str          # 信息收集结果
    analysis_result: str       # 分析结果
    risk_level: str            # 风险等级: LOW / MEDIUM / HIGH / CRITICAL
    human_approved: bool       # 人工审批结果
    report: str                # 最终报告


# ============================================================
# LLM 工厂
# ============================================================

def get_llm(backend: str = "ollama"):
    """获取 LLM 实例，与项目其他实验保持一致的双后端模式"""
    if backend == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "deepseek-v4-pro"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    return ChatOllama(model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"))


# ============================================================
# 安全工具函数（复用项目已有模式）
# ============================================================

def scan_ports(host: str, ports: list[int] = None) -> dict:
    """端口扫描 — 与 exp3_1/exp3_2 中的工具逻辑一致"""
    if ports is None:
        ports = [22, 80, 443, 3306, 8080, 8443]
    results = {}
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            status = "open" if sock.connect_ex((host, port)) == 0 else "closed"
            results[port] = status
            sock.close()
        except Exception:
            results[port] = "error"
    return {"host": host, "ports": results}


def check_http_headers(host: str) -> dict:
    """检查 HTTP 响应头（简化版 Web 指纹）"""
    import urllib.request
    try:
        url = f"http://{host}" if not host.startswith("http") else host
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "SecurityAudit/1.0")
        with urllib.request.urlopen(req, timeout=5) as resp:
            headers = dict(resp.headers)
            return {
                "status": resp.status,
                "server": headers.get("Server", "unknown"),
                "headers": {k: v for k, v in headers.items()
                            if k.lower() in ("server", "x-powered-by",
                                              "content-type", "x-frame-options",
                                              "strict-transport-security")}
            }
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# 工作流节点
# ============================================================
# 每个节点是一个函数：接收 State → 返回 State 的部分更新（dict）

def recon_node(state: SecurityState) -> dict:
    """
    节点 1: 信息收集
    扫描端口 + HTTP 头，汇总为文本报告供后续节点使用
    """
    target = state["target"]
    print(f"  [recon] 正在扫描 {target}...")

    # 执行扫描
    port_result = scan_ports(target)
    http_result = check_http_headers(target)

    # 汇总结果
    open_ports = [p for p, s in port_result["ports"].items() if s == "open"]
    recon_text = f"目标: {target}\n"
    recon_text += f"开放端口: {open_ports if open_ports else '无'}\n"

    if "error" not in http_result:
        recon_text += f"Web 服务器: {http_result.get('server', 'N/A')}\n"
        recon_text += f"响应头: {json.dumps(http_result.get('headers', {}), ensure_ascii=False)}\n"
    else:
        recon_text += f"HTTP 检查: {http_result['error']}\n"

    # 自动判断分析类型（如果用户未指定）
    analysis_type = state.get("analysis_type", "")
    if not analysis_type:
        if 80 in open_ports or 443 in open_ports or 8080 in open_ports:
            analysis_type = "web"
        elif open_ports:
            analysis_type = "port"
        else:
            analysis_type = "comprehensive"

    print(f"  [recon] 完成。分析类型: {analysis_type}")
    return {"recon_result": recon_text, "analysis_type": analysis_type}


# ============================================================
# 条件路由函数
# ============================================================
# 这是 LangGraph 的核心能力：根据状态动态决定下一个节点
# 返回值是节点名称字符串

def route_analysis(state: SecurityState) -> str:
    """
    条件路由：根据 analysis_type 选择分析路径

    与线性图的区别：
      线性图: recon → analysis → report（固定路径）
      条件图: recon → router → {web_analysis | port_analysis | comprehensive}
    """
    analysis_type = state["analysis_type"]
    print(f"  [router] 路由到: {analysis_type}")

    if analysis_type == "web":
        return "web_analysis"
    elif analysis_type == "port":
        return "port_analysis"
    else:
        return "comprehensive_analysis"


def web_analysis_node(state: SecurityState) -> dict:
    """Web 安全分析节点"""
    print("  [web_analysis] 分析 Web 安全...")
    llm = get_llm(BACKEND)
    response = llm.invoke([
        SystemMessage(content="你是 Web 安全专家。根据扫描结果分析 Web 安全风险，用中文简洁回答。"),
        HumanMessage(content=f"请分析以下扫描结果的 Web 安全风险：\n{state['recon_result']}"),
    ])
    # 简单的风险等级判断
    risk = "HIGH" if any(kw in response.content for kw in ["高危", "严重", "critical"]) else "MEDIUM"
    return {"analysis_result": response.content, "risk_level": risk}


def port_analysis_node(state: SecurityState) -> dict:
    """端口安全分析节点"""
    print("  [port_analysis] 分析端口安全...")
    llm = get_llm(BACKEND)
    response = llm.invoke([
        SystemMessage(content="你是网络安全专家。根据端口扫描结果评估安全风险，用中文简洁回答。"),
        HumanMessage(content=f"请分析以下端口扫描结果的安全风险：\n{state['recon_result']}"),
    ])
    risk = "HIGH" if any(kw in response.content for kw in ["高危", "严重", "critical", "3306"]) else "MEDIUM"
    return {"analysis_result": response.content, "risk_level": risk}


def comprehensive_analysis_node(state: SecurityState) -> dict:
    """综合分析节点"""
    print("  [comprehensive] 执行综合分析...")
    llm = get_llm(BACKEND)
    response = llm.invoke([
        SystemMessage(content="你是安全评估专家。对扫描结果进行全面的安全风险评估，用中文简洁回答。"),
        HumanMessage(content=f"请对以下信息进行综合安全评估：\n{state['recon_result']}"),
    ])
    risk = "CRITICAL" if "严重" in response.content else "HIGH" if "高" in response.content else "MEDIUM"
    return {"analysis_result": response.content, "risk_level": risk}


# ============================================================
# Human-in-the-loop 节点
# ============================================================
# 这是 LangGraph 区别于简单管道的关键能力：
# 当发现高风险时，暂停执行，等待人工确认后再继续

def risk_check_router(state: SecurityState) -> str:
    """高风险时路由到人工审批，否则直接生成报告"""
    if state["risk_level"] in ("HIGH", "CRITICAL"):
        return "human_review"
    return "report"


def human_review_node(state: SecurityState) -> dict:
    """
    人工审批节点

    使用 LangGraph 的 interrupt() 机制：
    1. 执行到此节点时，图暂停
    2. 返回 interrupt 值给调用方
    3. 调用方（CLI/Web）展示信息给人类
    4. 人类决策后，通过 Command 恢复执行
    """
    print(f"\n  {'='*50}")
    print(f"  ⚠️  发现 {state['risk_level']} 级风险！需要人工确认")
    print(f"  {'='*50}")
    print(f"  分析摘要: {state['analysis_result'][:200]}...")

    # interrupt 暂停图执行
    # 返回值会传递给调用方，调用方通过 graph.invoke(Command(resume=...)) 恢复
    decision = interrupt({
        "question": "是否继续生成详细报告？",
        "risk_level": state["risk_level"],
        "summary": state["analysis_result"][:500],
    })

    # 恢复执行后，decision 是调用方传入的值
    approved = decision.get("approved", False) if isinstance(decision, dict) else bool(decision)
    print(f"  [human_review] 人工决策: {'✅ 批准' if approved else '❌ 拒绝'}")
    return {"human_approved": approved}


def report_node(state: SecurityState) -> dict:
    """生成最终报告"""
    # 如果人工审批被拒绝，生成简化报告
    if state.get("risk_level") in ("HIGH", "CRITICAL") and not state.get("human_approved", True):
        report = f"⚠️ 安全评估已中止（人工拒绝）\n目标: {state['target']}\n风险等级: {state['risk_level']}"
        return {"report": report}

    print("  [report] 生成报告...")
    llm = get_llm(BACKEND)
    response = llm.invoke([
        SystemMessage(content="请生成简洁的安全评估报告，包含发现和建议。使用 Markdown 格式。"),
        HumanMessage(content=(
            f"目标: {state['target']}\n"
            f"风险等级: {state['risk_level']}\n"
            f"分析结果:\n{state['analysis_result']}"
        )),
    ])
    return {"report": response.content}


# ============================================================
# 构建工作流图
# ============================================================

def build_workflow() -> StateGraph:
    """
    构建安全评估工作流

    图结构：
      recon → (条件路由) → {web|port|comprehensive}_analysis
                → (风险检查) → {human_review | report}
                               → report → END
    """
    workflow = StateGraph(SecurityState)

    # 1. 添加节点
    workflow.add_node("recon", recon_node)
    workflow.add_node("web_analysis", web_analysis_node)
    workflow.add_node("port_analysis", port_analysis_node)
    workflow.add_node("comprehensive_analysis", comprehensive_analysis_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("report", report_node)

    # 2. 设置入口
    workflow.set_entry_point("recon")

    # 3. 条件路由：recon 之后根据 analysis_type 选择分支
    #    add_conditional_edges(源节点, 路由函数, {返回值: 目标节点})
    workflow.add_conditional_edges(
        "recon",
        route_analysis,
        {
            "web_analysis": "web_analysis",
            "port_analysis": "port_analysis",
            "comprehensive_analysis": "comprehensive_analysis",
        }
    )

    # 4. 三个分析节点汇聚后，根据风险等级路由
    for node in ["web_analysis", "port_analysis", "comprehensive_analysis"]:
        workflow.add_conditional_edges(
            node,
            risk_check_router,
            {
                "human_review": "human_review",
                "report": "report",
            }
        )

    # 5. human_review → report
    workflow.add_edge("human_review", "report")

    # 6. report → END
    workflow.add_edge("report", END)

    return workflow


# ============================================================
# 演示：三种运行模式
# ============================================================

def demo_basic(target: str):
    """
    演示 1: 基础运行（无检查点）
    适用于低风险目标，不需要 human-in-the-loop
    """
    print("\n" + "=" * 60)
    print("演示 1: 基础工作流（无 Human-in-the-loop）")
    print("=" * 60)

    workflow = build_workflow()
    # compile() 不传 checkpointer → interrupt 会直接抛异常
    # 所以这个演示只能用于不触发 human_review 的场景
    app = workflow.compile()

    result = app.invoke({
        "target": target,
        "analysis_type": "",  # 空 = 自动判断
        "recon_result": "",
        "analysis_result": "",
        "risk_level": "LOW",
        "human_approved": True,
        "report": "",
    })

    print(f"\n📋 报告:\n{result['report']}")
    return result


def demo_with_checkpoint(target: str):
    """
    演示 2: 带检查点的运行（支持 Human-in-the-loop）
    当发现高风险时，图会暂停等待人工确认
    """
    print("\n" + "=" * 60)
    print("演示 2: Human-in-the-loop 工作流")
    print("=" * 60)

    workflow = build_workflow()

    # 使用检查点：interrupt() 需要 checkpointer 来保存暂停时的状态
    checkpointer = InMemorySaver()
    app = workflow.compile(checkpointer=checkpointer)

    # 配置 thread_id — 检查点按 thread 隔离
    config = {"configurable": {"thread_id": "security-assessment-001"}}

    # 第一次调用：可能在 human_review 节点暂停
    initial_state = {
        "target": target,
        "analysis_type": "",
        "recon_result": "",
        "analysis_result": "",
        "risk_level": "LOW",
        "human_approved": False,
        "report": "",
    }

    print(f"\n[启动] 评估目标: {target}")
    result = app.invoke(initial_state, config=config)

    # 检查是否在 interrupt 处暂停
    snapshot = app.get_state(config)
    if snapshot.next:  # next 非空表示图未执行完
        print(f"\n  ⏸️  图在 {snapshot.next} 处暂停")
        print("  模拟人工审批: 批准继续...")

        # 恢复执行：传入 Command(resume=审批结果)
        result = app.invoke(
            Command(resume={"approved": True}),
            config=config,
        )

    print(f"\n📋 报告:\n{result['report']}")
    return result


def demo_state_inspection(target: str):
    """
    演示 3: 状态检查（检查点的另一个用途）
    可以在任何时刻查看图的执行状态，用于调试和可观测性
    """
    print("\n" + "=" * 60)
    print("演示 3: 状态检查与执行历史")
    print("=" * 60)

    workflow = build_workflow()
    checkpointer = InMemorySaver()
    app = workflow.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "inspection-demo"}}

    result = app.invoke({
        "target": target,
        "analysis_type": "port",  # 明确指定分析类型
        "recon_result": "",
        "analysis_result": "",
        "risk_level": "LOW",
        "human_approved": True,
        "report": "",
    }, config=config)

    # 查看最终状态快照
    snapshot = app.get_state(config)
    print("\n📊 状态快照:")
    print(f"  目标: {snapshot.values.get('target')}")
    print(f"  分析类型: {snapshot.values.get('analysis_type')}")
    print(f"  风险等级: {snapshot.values.get('risk_level')}")
    print(f"  下一节点: {snapshot.next if snapshot.next else '(已完成)'}")

    # 查看执行历史
    print("\n📜 执行历史:")
    for i, state in enumerate(app.get_state_history(config)):
        node = state.metadata.get("source", "unknown") if state.metadata else "unknown"
        print(f"  Step {i}: {node}")
        if i > 5:
            print("  ...")
            break

    return result


# ============================================================
# 主入口
# ============================================================

BACKEND = "ollama"  # 改为 "openai" 使用云端模型

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LangGraph 安全评估工作流")
    parser.add_argument("target", nargs="?", default="localhost",
                        help="评估目标 (默认: localhost)")
    parser.add_argument("--backend", choices=["ollama", "openai"], default="ollama",
                        help="LLM 后端")
    parser.add_argument("--demo", choices=["basic", "hitl", "inspect", "all"],
                        default="all", help="运行哪个演示")
    args = parser.parse_args()

    BACKEND = args.backend

    if args.demo in ("basic", "all"):
        demo_basic(args.target)

    if args.demo in ("hitl", "all"):
        demo_with_checkpoint(args.target)

    if args.demo in ("inspect", "all"):
        demo_state_inspection(args.target)
