"""
实验 3.1b: API Key 模式的 Function Calling
对比 Ollama 版本，理解 OpenAI 格式的工具调用差异

核心差异对比：
  ┌────────────────────┬─────────────────────┬─────────────────────┐
  │        特性         │      Ollama SDK     │     OpenAI SDK      │
  ├────────────────────┼─────────────────────┼─────────────────────┤
  │ 调用方法           │ ollama.chat()       │ client.chat.        │
  │                    │                     │ completions.create()│
  ├────────────────────┼─────────────────────┼─────────────────────┤
  │ tool_calls 路径    │ response.message.   │ response.choices[0].│
  │                    │ tool_calls          │ message.tool_calls  │
  ├────────────────────┼─────────────────────┼─────────────────────┤
  │ arguments 类型     │ dict（已解析）       │ JSON 字符串         │
  │                    │ 直接使用            │ 需 json.loads()     │
  ├────────────────────┼─────────────────────┼─────────────────────┤
  │ 工具结果关联       │ tool_name           │ tool_call_id        │
  ├────────────────────┼─────────────────────┼─────────────────────┤
  │ 工具定义格式       │ 相同（JSON Schema）  │ 相同（JSON Schema） │
  └────────────────────┴─────────────────────┴─────────────────────┘

为什么需要了解这些差异？
  - 开发跨平台应用时需要兼容不同 API
  - 迁移代码时知道哪些地方需要修改
  - 调试问题时能快速定位
"""

# ==================== 导入 ====================
import os
import json
from openai import OpenAI
# OpenAI: 官方 Python SDK

from dotenv import load_dotenv
# 加载环境变量

# ==================== 配置 ====================
load_dotenv()

# 创建 OpenAI 客户端
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# 模型名称
MODEL = os.getenv("OPENAI_MODEL", "deepseek-v4-pro")


# ============================================================
# 工具定义
# ============================================================
# 工具定义格式与 Ollama 完全一致（都遵循 OpenAI 的 JSON Schema 标准）

tools = [
    {
        "type": "function",
        "function": {
            "name": "scan_port",
            "description": "扫描目标主机的指定端口是否开放",
            "parameters": {
                "type": "object",
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "目标主机IP或域名"
                    },
                    "port": {
                        "type": "integer",
                        "description": "要扫描的端口号"
                    }
                },
                "required": ["host", "port"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_vulnerability",
            "description": "检查目标是否存在指定漏洞",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "目标URL或IP"
                    },
                    "vuln_type": {
                        "type": "string",
                        "enum": ["sql_injection", "xss", "ssrf", "lfi"],
                        "description": "漏洞类型"
                    }
                },
                "required": ["target", "vuln_type"]
            }
        }
    }
]


# ============================================================
# 工具实现函数
# ============================================================

def scan_port(host: str, port: int) -> dict:
    """
    扫描端口

    与 Ollama 版本完全相同
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


def check_vulnerability(target: str, vuln_type: str) -> dict:
    """
    检查漏洞（模拟）
    """
    return {"target": target, "vuln_type": vuln_type, "status": "scan_completed", "findings": []}


# 工具映射
TOOL_MAP = {
    "scan_port": scan_port,
    "check_vulnerability": check_vulnerability
}


# ============================================================
# 核心函数：OpenAI 格式的工具调用
# ============================================================

def chat_with_tools(user_message: str):
    """
    OpenAI 格式的工具调用

    与 Ollama 版本的关键差异：

    1. 调用方式：
       - Ollama: ollama.chat(model, messages, tools)
       - OpenAI: client.chat.completions.create(model, messages, tools)

    2. tool_calls 路径：
       - Ollama: response.message.tool_calls
       - OpenAI: response.choices[0].message.tool_calls

    3. arguments 类型：
       - Ollama: 已解析的 dict
       - OpenAI: JSON 字符串，需 json.loads()

    4. 工具结果关联：
       - Ollama: tool_name
       - OpenAI: tool_call_id

    Args:
        user_message: 用户输入

    Returns:
        str: 模型回答
    """
    messages = [{"role": "user", "content": user_message}]

    # ==================== 第一次调用 ====================
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools
    )

    # 获取消息对象
    # 注意：OpenAI 返回 choices 列表，取第一个
    message = response.choices[0].message

    if message.tool_calls:
        # 将 assistant 消息加入历史
        # 重要：必须加入完整的 message 对象，包含 tool_calls
        messages.append(message)

        for tool_call in message.tool_calls:
            func_name = tool_call.function.name

            # ========== 关键差异 1：arguments 是字符串 ==========
            # OpenAI 返回的 arguments 是 JSON 字符串
            # 必须使用 json.loads() 解析
            # Ollama 直接返回 dict，无需解析
            func_args = json.loads(tool_call.function.arguments)

            print(f"\n调用工具: {func_name}")
            print(f"   参数: {json.dumps(func_args, ensure_ascii=False)}")

            if func_name in TOOL_MAP:
                result = TOOL_MAP[func_name](**func_args)
                print(f"   结果: {json.dumps(result, ensure_ascii=False)}")

                # ========== 关键差异 2：使用 tool_call_id ==========
                # OpenAI 用 tool_call_id 关联工具调用和结果
                # Ollama 用 tool_name
                # 这个 id 是每次调用自动生成的唯一标识
                messages.append({
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False),
                    "tool_call_id": tool_call.id  # 使用 id 而非 name
                })
            else:
                result = {"error": f"未知工具: {func_name}"}

        # ==================== 第二次调用 ====================
        final = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools
        )
        return final.choices[0].message.content

    return message.content


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    test_queries = [
        "帮我扫描一下 localhost 的 80 端口是否开放",
        "检查 example.com 是否存在 SQL 注入漏洞",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"问题: {query}")
        print("="*60)
        result = chat_with_tools(query)
        print(f"\n回答: {result}")