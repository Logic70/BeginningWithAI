"""
实验 3.1c: LangChain Tool Calling
用 @tool 装饰器和 bind_tools() 统一工具调用接口

核心价值：
  - 一套代码，两种后端（Ollama / OpenAI）
  - @tool 装饰器自动生成 JSON Schema
  - 统一的 tool_calls 访问方式
  - 自动处理 arguments 格式差异

三种实现方式对比：
  ┌──────────────────┬─────────────────┬─────────────────┬─────────────────┐
  │      特性         │   Ollama SDK    │   OpenAI SDK    │   LangChain     │
  ├──────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 工具定义          │ 手写 JSON Schema│ 手写 JSON Schema│ @tool 装饰器    │
  │ arguments 类型    │ dict            │ JSON 字符串     │ 统一为 dict     │
  │ tool_call 关联    │ tool_name       │ tool_call_id    │ 统一用 id       │
  │ 切换后端          │ 改所有代码      │ 改所有代码      │ 改一处配置      │
  │ 学习曲线          │ 低              │ 低              │ 中              │
  │ 灵活性            │ 高              │ 高              │ 最高            │
  └──────────────────┴─────────────────┴─────────────────┴─────────────────┘
"""

# ==================== 导入 ====================
import os
import json
from dotenv import load_dotenv

# LangChain 核心组件
from langchain_core.tools import tool
# @tool 装饰器：自动从函数签名生成 JSON Schema

from langchain_core.messages import HumanMessage, ToolMessage
# HumanMessage: 用户消息
# ToolMessage: 工具结果消息

from langchain_ollama import ChatOllama
# ChatOllama: LangChain 对 Ollama 的封装

from langchain_openai import ChatOpenAI
# ChatOpenAI: LangChain 对 OpenAI API 的封装

# ==================== 配置 ====================
load_dotenv()


# ============================================================
# 工具定义（使用 @tool 装饰器）
# ============================================================
# @tool 装饰器的作用：
# 1. 自动从函数签名提取参数类型
# 2. 自动从 docstring 提取描述
# 3. 自动生成 JSON Schema
# 4. 将函数包装为 LangChain Tool 对象

@tool
def scan_port(host: str, port: int) -> dict:
    """
    扫描目标主机的指定端口是否开放

    注意：函数的 docstring 会成为工具的 description
    参数的类型注解会自动转换为 JSON Schema 类型
    """
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return {"host": host, "port": port, "open": result == 0}
    except Exception as e:
        return {"host": host, "port": port, "error": str(e)}


@tool
def check_vulnerability(target: str, vuln_type: str) -> dict:
    """
    检查目标是否存在指定漏洞。vuln_type 可选: sql_injection, xss, ssrf, lfi
    """
    return {"target": target, "vuln_type": vuln_type, "status": "scan_completed", "findings": []}


# ============================================================
# LLM 工厂函数
# ============================================================

def get_llm(backend: str = "ollama"):
    """
    获取 LLM 实例

    这是 LangChain 的核心优势：
    无论选择哪个后端，后续代码完全相同！

    Args:
        backend: "ollama" 或 "openai"
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
# 工具列表和映射
# ============================================================

# 工具列表：包含所有可用工具
tools = [scan_port, check_vulnerability]

# 工具映射：通过名称快速查找
tool_map = {t.name: t for t in tools}


# ============================================================
# 核心函数：统一的工具调用流程
# ============================================================

def chat_with_tools(user_message: str, backend: str = "ollama"):
    """
    LangChain 统一的工具调用流程

    无论后端是 Ollama 还是 OpenAI，代码完全一样！

    LangChain 自动处理的差异：
    1. arguments 格式：统一解析为 dict
    2. tool_call_id：统一使用 id 字段
    3. 消息格式：统一使用 HumanMessage / ToolMessage

    Args:
        user_message: 用户输入
        backend: 后端类型
    """
    # 获取 LLM 并绑定工具
    llm = get_llm(backend)

    # bind_tools() 是关键方法：
    # 将工具绑定到 LLM，后续调用会自动包含工具定义
    llm_with_tools = llm.bind_tools(tools)

    # 构建消息
    messages = [HumanMessage(content=user_message)]

    # ==================== 第一次调用 ====================
    response = llm_with_tools.invoke(messages)
    # 将响应加入历史
    messages.append(response)

    # 检查工具调用
    # LangChain 统一了访问方式：response.tool_calls
    # 无论底层是 Ollama 还是 OpenAI，都是这个属性
    if response.tool_calls:
        for tc in response.tool_calls:
            # tc 结构：{"name": "...", "args": {...}, "id": "..."}
            print(f"\n调用工具: {tc['name']}")
            print(f"   参数: {json.dumps(tc['args'], ensure_ascii=False)}")

            # 执行工具
            # tool_map[tc["name"]] 获取工具函数
            # .invoke() 执行工具
            result = tool_map[tc["name"]].invoke(tc["args"])
            print(f"   结果: {result}")

            # 追加工具结果
            # LangChain 使用 ToolMessage 类型
            # tool_call_id 用于关联工具调用和结果
            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tc["id"]
                )
            )

        # ==================== 第二次调用 ====================
        final = llm_with_tools.invoke(messages)
        return final.content

    return response.content


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backend",
        choices=["ollama", "openai"],
        default="ollama"
    )
    args = parser.parse_args()

    print(f"后端: {args.backend}\n")

    test_queries = [
        "帮我扫描一下 localhost 的 80 端口是否开放",
        "检查 example.com 是否存在 SQL 注入漏洞",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"问题: {query}")
        print("="*60)
        result = chat_with_tools(query, args.backend)
        print(f"\n回答: {result}")