"""
实验 3.14: 综合项目 — 安全评估平台
整合全部所学：LangGraph 工作流 + 多 Agent + 安全工具 + Human-in-the-loop

这是 Phase 3 的毕业设计，综合运用：
  ✓ 3.1 Function Calling — 工具调用基础
  ✓ 3.2 ReAct Agent — 推理与行动循环
  ✓ 3.4 MCP — 工具服务化（可选集成）
  ✓ 3.7-3.9 Skills — 领域知识注入（可选集成）
  ✓ 3.10 LangGraph 工作流 — 条件路由、循环、检查点
  ✓ 3.11 多 Agent 编排 — Supervisor 模式
  ✓ 3.12 A2A 协议 — Agent 互操作（可选集成）

系统架构：
  ┌─────────────────────────────────────────────────────────┐
  │                  Security Platform                      │
  │  ┌───────────────────────────────────────────────────┐  │
  │  │  Supervisor Agent (协调器)                        │  │
  │  │  - 任务分解                                        │  │
  │  │  - Agent 调度                                      │  │
  │  │  - 风险评估                                        │  │
  │  └───────────────────────────────────────────────────┘  │
  │           ↓                ↓                ↓            │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
  │  │   Recon     │  │  Analyzer   │  │  Reporter   │     │
  │  │   Agent     │  │   Agent     │  │   Agent     │     │
  │  └─────────────┘  └─────────────┘  └─────────────┘     │
  │           ↓                ↓                ↓            │
  │  ┌──────────────────────────────────────────────────┐   │
  │  │  Security Tools (MCP 可选)                       │   │
  │  │  - Port Scanner                                  │   │
  │  │  - HTTP Fingerprint                              │   │
  │  │  - Vulnerability Check                           │   │
  │  │  - WHOIS / DNS Enum                              │   │
  │  └──────────────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────────────┘
                          ↕
                  Human-in-the-loop
                  (高危操作审批)

工作流程：
  1. 用户输入目标 → Supervisor 分解任务
  2. Recon Agent 执行信息收集（端口扫描、HTTP 指纹）
  3. Analyzer Agent 分析风险等级
  4. 如果发现 HIGH/CRITICAL 风险 → 暂停等待人工确认
  5. Reporter Agent 生成结构化报告
  6. 支持检查点恢复（长任务中断后可继续）

与前面实验的区别：
  - 3.10：单一工作流 → 本实验：多 Agent 协作工作流
  - 3.11：简单 Supervisor → 本实验：带风险评估和人工审批的 Supervisor
  - 3.12：A2A 协议演示 → 本实验：实际安全场景应用
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
from langgraph.types import interrupt

# LangChain
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, AIMessage

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
# 安全工具集（整合前面实验的工具）
# ============================================================

@tool
def scan_ports(host: str, ports: str = "21,22,80,443,3306,3389,5432,6379,8080,8443,27017") -> str:
    """扫描目标主机的常见端口

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

    open_ports = [p for p, s in results.items() if s == "open"]
    return json.dumps({
        "host": host,
        "total_scanned": len(port_list),
        "open_ports": open_ports,
        "details": results
    }, ensure_ascii=False)


@tool
def check_http_security(url: str) -> str:
    """检查 HTTP 安全响应头

    Args:
        url: 目标 URL（如 http://example.com）
    """
    import urllib.request
    try:
        if not url.startswith("http"):
            url = f"http://{url}"
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "SecurityAudit/1.0")

        with urllib.request.urlopen(req, timeout=5) as resp:
            headers = dict(resp.headers)

            # 检查安全响应头
            security_headers = {
                "X-Frame-Options": headers.get("X-Frame-Options"),
                "X-Content-Type-Options": headers.get("X-Content-Type-Options"),
                "Strict-Transport-Security": headers.get("Strict-Transport-Security"),
                "Content-Security-Policy": headers.get("Content-Security-Policy"),
                "X-XSS-Protection": headers.get("X-XSS-Protection"),
            }

            missing = [k for k, v in security_headers.items() if v is None]

            return json.dumps({
                "url": url,
                "status": resp.status,
                "server": headers.get("Server", "unknown"),
                "security_headers": security_headers,
                "missing_headers": missing,
                "risk": "HIGH" if len(missing) >= 4 else "MEDIUM" if len(missing) >= 2 else "LOW"
            }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e), "url": url})


@tool
def check_common_vulns(host: str, open_ports: str) -> str:
    """根据开放端口检查常见漏洞风险

    Args:
        host: 目标主机
        open_ports: JSON 格式的开放端口列表
    """
    try:
        ports = json.loads(open_ports) if isinstance(open_ports, str) else open_ports
    except:
        ports = []

    vulns = []

    # 高危端口映射
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
        port_num = int(port) if isinstance(port, (str, int)) else port
        if port_num in high_risk:
            vulns.append({**high_risk[port_num], "port": port_num})
        elif port_num in medium_risk:
            vulns.append({**medium_risk[port_num], "port": port_num})

    overall_risk = "CRITICAL" if any(v["risk"] == "CRITICAL" for v in vulns) else \
                   "HIGH" if any(v["risk"] == "HIGH" for v in vulns) else \
                   "MEDIUM" if vulns else "LOW"

    return json.dumps({
        "host": host,
        "overall_risk": overall_risk,
        "vulnerabilities": vulns,
        "total_issues": len(vulns)
    }, ensure_ascii=False)


# ============================================================
# 平台状态定义
# ============================================================

class SecurityPlatformState(TypedDict):
    """安全评估平台的全局状态"""
    messages: Annotated[list[BaseMessage], operator.add]  # 对话历史
    target: str                    # 评估目标
    scan_result: str               # 扫描结果
    http_result: str               # HTTP 检查结果
    vuln_result: str               # 漏洞分析结果
    overall_risk: str              # 总体风险等级
    human_approved: bool           # 人工审批结果
    report: str                    # 最终报告
    next_agent: str                # 下一个要调用的 Agent


# ============================================================
# 专业 Agent 定义
# ============================================================

def create_recon_agent(backend: str = "ollama"):
    """
    Recon Agent：信息收集专家
    职责：端口扫描、HTTP 指纹识别
    """
    llm = get_llm(backend)
    tools = [scan_ports, check_http_security]

    system_prompt = """你是一个信息收集专家。你的任务是：
1. 扫描目标的常见端口
2. 如果发现 Web 服务（80/443/8080/8443），检查 HTTP 安全头
3. 将结果以 JSON 格式返回

重要：只执行信息收集，不做风险分析。"""

    def recon_node(state: SecurityPlatformState) -> dict:
        target = state["target"]
        messages = [SystemMessage(content=system_prompt),
                    HumanMessage(content=f"扫描目标: {target}")]

        # 使用 LLM + Tools 执行扫描
        response = llm.bind_tools(tools).invoke(messages)

        # 执行工具调用
        scan_data = {}
        http_data = {}

        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call["name"] == "scan_ports":
                    result = scan_ports.invoke(tool_call["args"])
                    scan_data = json.loads(result)
                elif tool_call["name"] == "check_http_security":
                    result = check_http_security.invoke(tool_call["args"])
                    http_data = json.loads(result)

        return {
            "scan_result": json.dumps(scan_data, ensure_ascii=False),
            "http_result": json.dumps(http_data, ensure_ascii=False),
            "messages": [AIMessage(content=f"[Recon Agent] 完成扫描: {target}")]
        }

    return recon_node


def create_analyzer_agent(backend: str = "ollama"):
    """
    Analyzer Agent：风险分析专家
    职责：根据扫描结果分析漏洞和风险等级
    """
    llm = get_llm(backend)
    tools = [check_common_vulns]

    system_prompt = """你是一个安全风险分析专家。你的任务是：
1. 分析扫描结果中的开放端口
2. 识别常见漏洞和风险
3. 评估总体风险等级（CRITICAL/HIGH/MEDIUM/LOW）
4. 返回结构化的分析结果"""

    def analyzer_node(state: SecurityPlatformState) -> dict:
        scan_result = state.get("scan_result", "{}")
        try:
            scan_data = json.loads(scan_result)
            open_ports = scan_data.get("open_ports", [])
        except:
            open_ports = []

        # 调用漏洞检查工具
        vuln_result = check_common_vulns.invoke({
            "host": state["target"],
            "open_ports": json.dumps(open_ports)
        })

        vuln_data = json.loads(vuln_result)
        overall_risk = vuln_data.get("overall_risk", "LOW")

        return {
            "vuln_result": vuln_result,
            "overall_risk": overall_risk,
            "messages": [AIMessage(content=f"[Analyzer Agent] 风险等级: {overall_risk}")]
        }

    return analyzer_node


def create_reporter_agent(backend: str = "ollama"):
    """
    Reporter Agent：报告生成专家
    职责：汇总所有结果，生成结构化报告
    """
    llm = get_llm(backend)

    system_prompt = """你是一个安全报告撰写专家。你的任务是：
1. 汇总扫描、HTTP 检查、漏洞分析的结果
2. 生成清晰的 Markdown 格式报告
3. 包含：目标信息、风险等级、发现详情、修复建议"""

    def reporter_node(state: SecurityPlatformState) -> dict:
        target = state["target"]
        scan_result = state.get("scan_result", "{}")
        http_result = state.get("http_result", "{}")
        vuln_result = state.get("vuln_result", "{}")
        overall_risk = state.get("overall_risk", "UNKNOWN")

        # 解析数据
        try:
            scan_data = json.loads(scan_result)
            http_data = json.loads(http_result)
            vuln_data = json.loads(vuln_result)
        except:
            scan_data = {}
            http_data = {}
            vuln_data = {}

        # 生成报告
        report = f"""# 安全评估报告

## 目标信息
- **目标**: {target}
- **总体风险**: {overall_risk}
- **评估时间**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 端口扫描结果
- **扫描端口数**: {scan_data.get('total_scanned', 0)}
- **开放端口**: {scan_data.get('open_ports', [])}

## HTTP 安全检查
"""
        if http_data and "error" not in http_data:
            report += f"- **服务器**: {http_data.get('server', 'N/A')}\n"
            report += f"- **缺失安全头**: {http_data.get('missing_headers', [])}\n"
            report += f"- **HTTP 风险**: {http_data.get('risk', 'N/A')}\n"
        else:
            report += "- 未检测到 Web 服务或检查失败\n"

        report += "\n## 漏洞发现\n"
        vulns = vuln_data.get('vulnerabilities', [])
        if vulns:
            for vuln in vulns:
                report += f"- **[{vuln['risk']}]** 端口 {vuln['port']} ({vuln['service']}): {vuln['desc']}\n"
        else:
            report += "- 未发现明显漏洞\n"

        report += "\n## 修复建议\n"
        if overall_risk in ["CRITICAL", "HIGH"]:
            report += "- 立即关闭不必要的高危端口\n"
            report += "- 配置防火墙规则限制访问\n"
            report += "- 启用强认证机制\n"
        elif overall_risk == "MEDIUM":
            report += "- 审查开放端口的必要性\n"
            report += "- 加强访问控制\n"
        else:
            report += "- 保持当前安全配置\n"
            report += "- 定期进行安全审计\n"

        return {
            "report": report,
            "messages": [AIMessage(content="[Reporter Agent] 报告生成完成")]
        }

    return reporter_node


# ============================================================
# Supervisor 节点
# ============================================================

def supervisor_node(state: SecurityPlatformState) -> dict:
    """
    Supervisor：协调器
    决定下一步调用哪个 Agent
    """
    # 决策逻辑
    if not state.get("scan_result"):
        return {"next_agent": "recon"}
    elif not state.get("vuln_result"):
        return {"next_agent": "analyzer"}
    elif not state.get("report"):
        return {"next_agent": "reporter"}
    else:
        return {"next_agent": "END"}


def human_review_node(state: SecurityPlatformState) -> dict:
    """
    Human-in-the-loop 节点
    高危风险时暂停等待人工确认
    """
    overall_risk = state.get("overall_risk", "LOW")

    if overall_risk in ["CRITICAL", "HIGH"]:
        # 使用 interrupt 暂停执行
        approval = interrupt(
            f"⚠️  检测到 {overall_risk} 风险！\n"
            f"目标: {state['target']}\n"
            f"是否继续生成报告？(yes/no)"
        )

        # 用户输入 "yes" 才继续
        approved = approval.lower() in ["yes", "y", "是"]
        return {"human_approved": approved}
    else:
        # 低风险自动通过
        return {"human_approved": True}


# ============================================================
# 路由函数
# ============================================================

def route_supervisor(state: SecurityPlatformState) -> str:
    """根据 Supervisor 决策路由到下一个节点"""
    next_agent = state.get("next_agent", "END")
    if next_agent == "END":
        return END
    return next_agent


def route_human_review(state: SecurityPlatformState) -> str:
    """根据人工审批结果路由"""
    if state.get("human_approved", False):
        return "reporter"
    else:
        return END


# ============================================================
# 构建完整平台
# ============================================================

def build_security_platform(backend: str = "ollama"):
    """
    构建安全评估平台的完整工作流

    流程：
      START → supervisor → recon → supervisor → analyzer → human_review → reporter → END
                  ↑___________|         ↑___________|              |
                                                                   ↓ (拒绝)
                                                                  END
    """
    # 创建各 Agent 节点
    recon_agent = create_recon_agent(backend)
    analyzer_agent = create_analyzer_agent(backend)
    reporter_agent = create_reporter_agent(backend)

    # 构建状态图
    workflow = StateGraph(SecurityPlatformState)

    # 添加节点
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("recon", recon_agent)
    workflow.add_node("analyzer", analyzer_agent)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("reporter", reporter_agent)

    # 设置入口
    workflow.set_entry_point("supervisor")

    # 添加边
    workflow.add_conditional_edges("supervisor", route_supervisor,
                                   {"recon": "recon", "analyzer": "analyzer",
                                    "reporter": "reporter", END: END})
    workflow.add_edge("recon", "supervisor")
    workflow.add_edge("analyzer", "human_review")
    workflow.add_conditional_edges("human_review", route_human_review,
                                   {"reporter": "reporter", END: END})
    workflow.add_edge("reporter", END)

    # 添加检查点（支持中断恢复）
    checkpointer = InMemorySaver()

    return workflow.compile(checkpointer=checkpointer)


# ============================================================
# 主程序
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="安全评估平台")
    parser.add_argument("target", help="评估目标（IP 或域名）")
    parser.add_argument("--backend", choices=["ollama", "openai"], default="ollama",
                        help="LLM 后端")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  安全评估平台 v1.0")
    print(f"  目标: {args.target}")
    print(f"  后端: {args.backend}")
    print(f"{'='*60}\n")

    # 构建平台
    platform = build_security_platform(args.backend)

    # 初始状态
    initial_state = {
        "messages": [],
        "target": args.target,
        "scan_result": "",
        "http_result": "",
        "vuln_result": "",
        "overall_risk": "",
        "human_approved": False,
        "report": "",
        "next_agent": ""
    }

    # 执行工作流（带检查点支持）
    config = {"configurable": {"thread_id": "security-eval-001"}}

    try:
        for event in platform.stream(initial_state, config):
            for node_name, node_output in event.items():
                if node_name != "__end__":
                    print(f"\n[{node_name}] 执行完成")
                    if "messages" in node_output and node_output["messages"]:
                        print(f"  {node_output['messages'][-1].content}")

        # 获取最终状态
        final_state = platform.get_state(config)

        if final_state.values.get("report"):
            print(f"\n{'='*60}")
            print(final_state.values["report"])
            print(f"{'='*60}\n")
        else:
            print("\n⚠️  评估被中止或未完成\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行\n")
    except Exception as e:
        print(f"\n❌ 执行出错: {e}\n")


if __name__ == "__main__":
    main()
