"""
实验 3.1c: LangChain Tool Calling
用 @tool 装饰器和 bind_tools() 统一工具调用接口
"""

import os
import json
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

load_dotenv()

# ===== 用 @tool 装饰器定义工具（比手写 JSON Schema 简洁得多）=====

@tool
def scan_port(host: str, port: int) -> dict:
    """扫描目标主机的指定端口是否开放"""
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
    """检查目标是否存在指定漏洞。vuln_type 可选: sql_injection, xss, ssrf, lfi"""
    return {"target": target, "vuln_type": vuln_type, "status": "scan_completed", "findings": []}

def get_llm(backend: str = "ollama"):
    """获取 LLM 实例"""
    if backend == "ollama":
        return ChatOllama(model="qwen2.5:7b")
    elif backend == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    raise ValueError(f"未知后端: {backend}")

# 工具列表
tools = [scan_port, check_vulnerability]
tool_map = {t.name: t for t in tools}

def chat_with_tools(user_message: str, backend: str = "ollama"):
    """
    LangChain 统一的工具调用流程 — 无论后端是什么，代码完全一样！
    
    对比手写版本：
    - 无需手写 JSON Schema（@tool 装饰器自动生成）
    - 无需处理 arguments 格式差异（LangChain 统一解析）
    - 无需关心 tool_call_id vs tool_name（LangChain 自动处理）
    """
    llm = get_llm(backend)
    llm_with_tools = llm.bind_tools(tools)
    messages = [HumanMessage(content=user_message)]

    # 第一次调用
    response = llm_with_tools.invoke(messages)
    messages.append(response)

    # 检查工具调用（统一的 .tool_calls 属性）
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"\n🔧 调用工具: {tc['name']}")
            print(f"   参数: {json.dumps(tc['args'], ensure_ascii=False)}")

            # 执行工具
            result = tool_map[tc["name"]].invoke(tc["args"])
            print(f"   结果: {result}")

            # 追加工具结果（LangChain 统一用 ToolMessage）
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

        # 第二次调用
        final = llm_with_tools.invoke(messages)
        return final.content
    
    return response.content     

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["ollama", "openai"], default="ollama")
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
        print(f"\n💬 回答: {result}") 