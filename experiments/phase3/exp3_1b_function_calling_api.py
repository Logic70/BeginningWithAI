"""
实验 3.1b: API Key 模式的 Function Calling
对比 Ollama 版本，理解 OpenAI 格式的工具调用差异
"""
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)
MODEL = os.getenv("OPENAI_MODEL",'qwen3.5-plus')


# 工具定义格式与 Ollama 完全一致（都遵循 JSON Schema）
tools = [
    {
        "type": "function",
        "function": {
            "name": "scan_port",
            "description": "扫描目标主机的指定端口是否开放",
            "parameters": {
                "type": "object",
                "properties": {
                    "host": {"type": "string", "description": "目标主机IP或域名"},
                    "port": {"type": "integer", "description": "要扫描的端口号"}
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
                    "target": {"type": "string", "description": "目标URL或IP"},
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


def scan_port(host: str, port: int) -> dict:
    """模拟端口扫描"""
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
    """模拟漏洞检查"""
    return {"target": target, "vuln_type": vuln_type, "status": "scan_completed", "findings": []}


TOOL_MAP = {"scan_port": scan_port, "check_vulnerability": check_vulnerability}


def chat_with_tools(user_message: str):
    """
    OpenAI 格式的工具调用 — 与 Ollama 的关键差异：
    
    1. 调用方式: client.chat.completions.create() vs ollama.chat()
    2. tool_calls 路径: response.choices[0].message.tool_calls vs response.message.tool_calls
    3. arguments 类型: JSON 字符串（需 json.loads）vs dict（已解析）
    4. 工具结果角色: "tool" + tool_call_id vs "tool" + tool_name
    """
    messages = [{"role": "user", "content": user_message}]
    
    # 第一次调用
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools
    )
    
    message = response.choices[0].message
    
    if message.tool_calls:
        # 将 assistant 消息加入历史
        messages.append(message)
        
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            # ⚠️ 关键差异：OpenAI 返回的 arguments 是 JSON 字符串，需手动解析
            func_args = json.loads(tool_call.function.arguments)
            
            print(f"\n🔧 调用工具: {func_name}")
            print(f"   参数: {json.dumps(func_args, ensure_ascii=False)}")
            
            if func_name in TOOL_MAP:
                result = TOOL_MAP[func_name](**func_args)
                print(f"   结果: {json.dumps(result, ensure_ascii=False)}")
                
                # ⚠️ 关键差异：OpenAI 用 tool_call_id 关联结果，而非 tool_name
                messages.append({
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False),
                    "tool_call_id": tool_call.id  # Ollama 用 tool_name
                })
            else:
                result = {"error": f"未知工具: {func_name}"}
        
        # 第二次调用
        final = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools
        )
        return final.choices[0].message.content
    
    return message.content


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
        print(f"\n💬 回答: {result}")