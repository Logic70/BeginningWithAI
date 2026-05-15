"""
实验 3.1：Function Calling 基础（Ollama 版）
展示 LLM 如何"调用"外部工具

核心概念：
  - Function Calling：让 LLM 能够"使用工具"
  - 工具定义：告诉 LLM 有哪些工具可用（JSON Schema 格式）
  - 两阶段调用：模型决策 → 执行工具 → 模型生成回答

执行流程：
  ┌─────────────────────────────────────────────────────────────┐
  │ 用户: "帮我扫描 localhost 的 80 端口"                        │
  └─────────────────────────────────────────────────────────────┘
                              ↓
  ┌─────────────────────────────────────────────────────────────┐
  │ 第一次调用: ollama.chat(model, messages, tools)             │
  │ LLM 分析用户意图，决定调用 scan_port 工具                     │
  │ 返回: tool_calls = [{name: "scan_port", arguments: {...}}]  │
  └─────────────────────────────────────────────────────────────┘
                              ↓
  ┌─────────────────────────────────────────────────────────────┐
  │ 执行工具: scan_port(host="localhost", port=80)              │
  │ 返回: {"host": "localhost", "port": 80, "status": "open"}   │
  └─────────────────────────────────────────────────────────────┘
                              ↓
  ┌─────────────────────────────────────────────────────────────┐
  │ 第二次调用: 将工具结果加入 messages，再次调用模型             │
  │ LLM 根据工具结果生成自然语言回答                              │
  │ 返回: "localhost 的 80 端口是开放的..."                       │
  └─────────────────────────────────────────────────────────────┘
"""

# ==================== 导入 ====================
import ollama
# ollama: Ollama 官方 Python SDK

import json
# json: 处理工具参数和结果的序列化

import socket
# socket: 端口扫描的底层实现

import ipaddress
# ipaddress: 解析 IP 网络段

import subprocess
# subprocess: 执行系统命令（ping 扫描）


# ============================================================
# 工具定义（JSON Schema 格式）
# ============================================================
# 工具定义告诉 LLM：
# 1. 有哪些工具可用
# 2. 每个工具的名称和用途
# 3. 每个工具需要什么参数

tools = [
    # 工具 1：端口扫描
    {
        "type": "function",  # 固定值，表示这是一个函数工具
        "function": {
            "name": "scan_port",  # 工具名称，调用时使用
            "description": "扫描目标主机的指定端口是否开放",
            # description 非常重要！LLM 根据这个描述决定何时调用
            "parameters": {
                "type": "object",  # 参数是一个对象
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "目标主机IP或域名"
                        # 描述帮助 LLM 理解参数含义
                    },
                    "port": {
                        "type": "integer",
                        "description": "要扫描的端口号"
                    }
                },
                "required": ["host", "port"]
                # required: 必须提供的参数列表
            }
        }
    },

    # 工具 2：漏洞检查
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
                        # enum: 限制可选值，防止 LLM 生成无效参数
                        "description": "漏洞类型"
                    }
                },
                "required": ["target", "vuln_type"]
            }
        }
    },

    # 工具 3：IP 段扫描
    {
        "type": "function",
        "function": {
            "name": "scan_ip",
            "description": "扫描目标网络所有存活的主机",
            "parameters": {
                "type": "object",
                "properties": {
                    "network": {
                        "type": "string",
                        "description": "目标网络IP段"
                    },
                    "mask": {
                        "type": "string",
                        "description": "子网掩码"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "超时时间,默认5秒"
                    }
                },
                "required": ["network", "mask"]
            }
        }
    }
]


# ============================================================
# 工具实现函数
# ============================================================

def scan_port(host: str, port: int) -> dict:
    """
    扫描指定主机的端口

    实现原理：
    1. 创建 TCP socket
    2. 尝试连接目标端口
    3. connect_ex() 返回 0 表示成功（端口开放）

    Args:
        host: 目标主机 IP 或域名
        port: 端口号

    Returns:
        dict: {"host": ..., "port": ..., "status": "open/closed/error"}
    """
    try:
        # 创建 TCP socket
        # AF_INET: IPv4
        # SOCK_STREAM: TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)  # 设置超时时间
            result = s.connect_ex((host, port))
            # connect_ex() 返回 0 表示连接成功
            # 非 0 表示连接失败（端口关闭或不可达）

            if result == 0:
                return {"host": host, "port": port, "status": "open"}
            else:
                return {"host": host, "port": port, "status": "closed"}
    except Exception as e:
        return {"host": host, "port": port, "status": "error", "message": str(e)}


def check_vulnerability(target: str, vuln_type: str) -> dict:
    """
    检查目标是否存在指定漏洞

    注意：这是模拟实现，实际应用需要调用真实扫描工具
    如 sqlmap、Nuclei 等

    Args:
        target: 目标 URL 或 IP
        vuln_type: 漏洞类型

    Returns:
        dict: 扫描结果
    """
    try:
        # 模拟实现 - 实际应用中应调用真实扫描工具
        if vuln_type == "sql_injection":
            return {"target": target, "vuln_type": vuln_type, "status": "open"}
        elif vuln_type == "xss":
            return {"target": target, "vuln_type": vuln_type, "status": "open"}
        elif vuln_type == "ssrf":
            return {"target": target, "vuln_type": vuln_type, "status": "open"}
        elif vuln_type == "lfi":
            return {"target": target, "vuln_type": vuln_type, "status": "open"}
    except Exception as e:
        return {"target": target, "vuln_type": vuln_type, "status": "error", "message": str(e)}


def scan_ip(network: str, mask: str, timeout: int = 1) -> dict:
    """
    扫描目标网络所有存活的主机

    实现原理：
    1. 解析 IP 网络段（如 192.168.1.0/24）
    2. 遍历所有主机 IP
    3. 使用 ping 检测存活状态

    Args:
        network: 网络地址（如 "192.168.1.0"）
        mask: 子网掩码（如 "24"）
        timeout: ping 超时时间

    Returns:
        list: 每个主机的存活状态
    """
    network_list = []

    # 解析 IP 网络段
    # ip_network("192.168.1.0/24") 返回所有 IP
    ip_list = ipaddress.ip_network(f"{network}/{mask}", strict=False)

    # 获取所有可用的主机 IP
    # hosts() 排除网络地址和广播地址
    for ip in ip_list.hosts():
        network_list.append(str(ip))

    result_list = []

    # 遍历每个 IP 进行 ping 扫描
    for ip in network_list:
        try:
            # 使用系统 ping 命令
            # -w: 超时时间（秒）
            result = subprocess.run(
                ["ping", "-w", str(timeout), ip],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                result_list.append({"host": ip, "status": "open"})
            else:
                result_list.append({"host": ip, "status": "closed"})
        except Exception as e:
            result_list.append({"host": ip, "status": "error", "message": str(e)})

    return result_list


# ============================================================
# 工具映射
# ============================================================
# 将工具名称映射到实际函数
# 当 LLM 决定调用某个工具时，通过这个映射找到对应函数

TOOL_MAP = {
    "scan_port": scan_port,
    "check_vulnerability": check_vulnerability,
    "scan_ip": scan_ip
}


# ============================================================
# 核心函数：带工具调用的对话
# ============================================================

def chat_with_tools(user_message: str, model: str = "qwen2.5:7b"):
    """
    与 Ollama 进行 Function Calling 对话

    执行流程：
    1. 第一次调用：让模型决定是否使用工具
    2. 如果有工具调用，执行工具并将结果加入历史
    3. 第二次调用：模型根据工具结果生成最终回答

    Args:
        user_message: 用户输入
        model: 使用的模型

    Returns:
        str: 模型的最终回答

    Ollama SDK 的访问方式：
      - 属性访问: response.message.tool_calls
      - 字典访问: response["message"]["tool_calls"]
      两种方式等效，本函数演示属性访问
    """
    # 构建消息历史
    messages = [{"role": "user", "content": user_message}]

    # ==================== 第一次调用 ====================
    # 让模型分析用户意图，决定是否调用工具
    response = ollama.chat(
        model=model,
        messages=messages,
        tools=tools  # 传入可用工具列表
    )

    # 检查是否有工具调用
    # 注意：tool_calls 在 response.message 下，不在 response 顶层！
    if response.message.tool_calls:
        for tool_call in response.message.tool_calls:
            # 提取工具名称和参数
            func_name = tool_call.function.name
            func_args = tool_call.function.arguments
            # Ollama 的 arguments 已经是 dict，无需 json.loads
            # 这是 Ollama 与 OpenAI 的一个重要差异

            print(f"\n调用工具: {func_name}")
            print(f"   参数: {json.dumps(func_args, ensure_ascii=False)}")

            # 执行工具
            if func_name in TOOL_MAP:
                result = TOOL_MAP[func_name](**func_args)
                print(f"   结果: {json.dumps(result, ensure_ascii=False)}")

                # 将助手消息和工具结果加入历史
                messages.append(response.message)

                # 工具结果消息格式
                messages.append({
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False),
                    "tool_name": func_name  # Ollama 使用 tool_name
                    # OpenAI 使用 tool_call_id
                })
            else:
                print(f"   错误：未知的工具 {func_name}")
                return f"未知的工具: {func_name}"

        # ==================== 第二次调用 ====================
        # 将完整历史（包含工具结果）发给模型
        # 模型会根据工具结果生成自然语言回答
        final_response = ollama.chat(
            model=model,
            messages=messages,
            tools=tools
        )
        return final_response.message.content

    else:
        # 模型认为不需要调用工具，直接返回文本回答
        return response.message.content


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    test_queries = [
        # "帮我扫描一下 localhost 的 80 端口是否开放",
        # "检查 example.com 是否存在 SQL 注入漏洞",
        "帮我扫描一下我192.168.101.0 24有哪些主机"
        # "分析一下常见的 Web 安全漏洞"  # 不需要工具的问题
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"问题: {query}")
        print("="*60)
        result = chat_with_tools(query)
        print(f"\n回答: {result}")