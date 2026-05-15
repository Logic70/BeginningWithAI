"""
实验 3.2c: LangChain ReAct Agent
对比手写 ReAct 循环，体验框架的封装价值

手写 vs LangChain 对比：
  ┌──────────────────┬─────────────────────────┬─────────────────────────┐
  │      特性         │       手写版本          │      LangChain 版本     │
  ├──────────────────┼─────────────────────────┼─────────────────────────┤
  │ 代码行数          │ ~100 行                 │ ~3 行                   │
  │ 提示词管理        │ 手写字符串拼接          │ 自动生成                │
  │ 响应解析          │ 正则表达式              │ 自动解析                │
  │ 迭代循环          │ 手写 while/for          │ 内部自动处理            │
  │ 历史管理          │ 手动追加字符串          │ 自动管理 messages       │
  │ 工具定义          │ 手写描述字符串          │ @tool 装饰器自动生成     │
  │ 错误处理          │ 需要自己实现            │ 内置处理机制            │
  └──────────────────┴─────────────────────────┴─────────────────────────┘

API 演进说明：
  - LangGraph (2024): create_react_agent() - 基于状态图
  - LangChain 1.2+ (2024末): create_agent() - 简化 API，底层仍是 LangGraph
"""

# ==================== 导入 ====================
import os
import json
import socket
# socket: 端口扫描底层实现

from pathlib import Path
from dotenv import load_dotenv

# LangChain 核心组件
from langchain_core.tools import tool
# @tool 装饰器：自动生成工具定义

from langchain_ollama import ChatOllama
# ChatOllama: LangChain 对 Ollama 的封装

from langchain_openai import ChatOpenAI
# ChatOpenAI: LangChain 对 OpenAI API 的封装

from langchain.agents import create_agent
# create_agent: LangChain 1.2+ 新 API，创建 ReAct Agent

# ==================== 配置加载 ====================
# 显式加载项目根目录的 .env（支持 WSL 环境）
load_dotenv(Path(__file__).parent.parent.parent / ".env")


# ============================================================
# 工具定义
# ============================================================
# 使用 @tool 装饰器定义工具
# 优点：
# 1. 自动从函数签名提取参数类型
# 2. 自动从 docstring 提取描述
# 3. 自动生成 JSON Schema

@tool
def port_scan(host: str, ports: list[int]) -> dict:
    """
    扫描目标主机的多个端口，返回每个端口的开放状态。

    Args:
        host: 目标主机 IP 或域名
        ports: 要扫描的端口列表

    Returns:
        包含 host 和 ports 状态的字典
    """
    results = {}
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            results[port] = "open" if result == 0 else "closed"
            sock.close()
        except:
            results[port] = "error"
    return {"host": host, "ports": results}


@tool
def web_fingerprint(url: str) -> dict:
    """
    识别 Web 服务的技术栈，包括服务器、编程语言、数据库等。

    Args:
        url: 目标 Web 服务的 URL

    Returns:
        包含 server、technologies、cms 等信息的字典
    """
    # 模拟实现（实际应用中应调用真实的指纹识别工具）
    return {
        "url": url,
        "server": "nginx/1.18.0",
        "technologies": ["PHP", "MySQL"],
        "cms": "unknown"
    }


# ============================================================
# LLM 工厂函数
# ============================================================

def get_llm(backend: str = "openai"):
    """
    获取 LLM 实例

    支持 Ollama 本地模型和 OpenAI 兼容 API
    无论选择哪个后端，后续代码完全相同！

    Args:
        backend: "ollama" 或 "openai"

    Returns:
        LLM 实例
    """
    if backend == "ollama":
        return ChatOllama(model="qwen2.5:7b")
    elif backend == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "deepseek-v4-pro"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    raise ValueError(f"未知后端: {backend}")


# ============================================================
# 核心：LangChain Agent 创建和执行
# ============================================================

def run_react_agent(task: str, backend: str = "openai"):
    """
    用 LangChain 创建 ReAct Agent

    对比手写版本：
    - 手写版: ~100 行（提示词模板 + 正则解析 + 迭代循环 + 历史管理）
    - LangChain: ~3 行（create_agent + invoke）

    内部自动处理：
    1. 生成 ReAct 格式的提示词
    2. 解析模型响应
    3. 执行工具调用
    4. 管理执行历史
    5. 循环直到得到最终答案

    API 变更说明 (langchain >= 1.2):
    - 旧: langgraph.prebuilt.create_react_agent(llm, tools)
    - 新: langchain.agents.create_agent(llm, tools, system_prompt="...")
    - 新 API 需要显式传递 system_prompt 参数

    Args:
        task: 用户任务
        backend: 后端类型
    """
    # 获取 LLM
    llm = get_llm(backend)
    tools = [port_scan, web_fingerprint]

    # ========== 核心：创建 Agent ==========
    # 这一行替代了手写版本的 ~50 行代码
    agent = create_agent(
        llm,
        tools,
        system_prompt="你是一个网络安全分析助手，帮助用户进行端口扫描、技术栈识别等安全分析任务。"
    )

    # ========== 执行 Agent ==========
    # 内部自动处理 ReAct 循环：思考 → 工具调用 → 观察 → 继续
    result = agent.invoke({"messages": [("user", task)]})

    # ========== 打印执行过程 ==========
    print("\n--- 执行过程 ---")
    for msg in result["messages"]:
        # 检查工具调用
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"调用: {tc['name']}({json.dumps(tc['args'], ensure_ascii=False)})")
        # 检查工具结果
        elif msg.type == "tool":
            content = str(msg.content)[:100] if msg.content else ""
            print(f"结果: {content}...")
        # 检查 AI 回复
        elif msg.type == "ai" and msg.content:
            print(f"回答: {msg.content[:200]}...")

    # 返回最终回答
    final_msg = result["messages"][-1]
    return final_msg.content if hasattr(final_msg, "content") else str(final_msg)


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LangChain ReAct Agent 演示")
    parser.add_argument(
        "--backend",
        choices=["ollama", "openai"],
        default="openai",
        help="LLM 后端 (默认: openai)"
    )
    parser.add_argument(
        "--task",
        type=str,
        default=None,
        help="自定义任务描述"
    )
    args = parser.parse_args()

    print(f"后端: {args.backend}")

    # 默认任务
    task = args.task or "分析 localhost 的安全状况，扫描常用端口(80, 443, 22, 3306)并识别Web技术栈"
    print(f"\n任务: {task}")

    result = run_react_agent(task, args.backend)
    print(f"\n{'='*60}")
    print(f"最终结果: {result}")