"""
实验 3.4: MCP Server - 安全工具集成
将 Nmap 等安全工具封装为 MCP 服务

MCP Server 核心概念：
  - Server 暴露工具（Tools）、资源（Resources）、提示词（Prompts）
  - Client 通过 JSON-RPC 2.0 协议调用
  - 通信通过 stdin/stdout 或 HTTP/SSE

架构图：
  ┌─────────────────────────────────────────────────────────────┐
  │                     MCP Client                              │
  │  (Claude Desktop / LangChain Agent / 自定义客户端)          │
  └─────────────────────────────────────────────────────────────┘
                              ↓ JSON-RPC 2.0
  ┌─────────────────────────────────────────────────────────────┐
  │                     MCP Server (本文件)                     │
  │  ┌─────────────────────────────────────────────────────┐   │
  │  │ @server.list_tools()                                │   │
  │  │ 返回: [Tool(name, description, inputSchema), ...]   │   │
  │  └─────────────────────────────────────────────────────┘   │
  │  ┌─────────────────────────────────────────────────────┐   │
  │  │ @server.call_tool()                                 │   │
  │  │ 接收: name, arguments                               │   │
  │  │ 执行: 调用实际工具函数                               │   │
  │  │ 返回: [TextContent(text=result)]                    │   │
  │  └─────────────────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────────────────┘
                              ↓
  ┌─────────────────────────────────────────────────────────────┐
  │                     系统工具层                              │
  │        nmap          whois          socket (DNS)           │
  └─────────────────────────────────────────────────────────────┘

运行方式：
  python exp3_4_mcp_server.py

手动测试：
  # 测试初始化
  echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | python exp3_4_mcp_server.py

  # 测试工具列表（需要先初始化）
  echo -e '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}\n{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | python exp3_4_mcp_server.py
"""

# ==================== 导入 ====================
import asyncio
# asyncio: 异步编程支持

import json
# json: 序列化工具结果

# ==================== MCP SDK 导入 ====================
from mcp.server import Server, NotificationOptions
# Server: MCP Server 核心类
# NotificationOptions: 通知选项配置

from mcp.server.models import InitializationOptions
# InitializationOptions: 初始化选项，包含服务器名称、版本、能力

import mcp.server.stdio
# stdio: stdin/stdout 通信模块

import mcp.types as types
# types: MCP 类型定义（Tool, TextContent 等）


# ============================================================
# 创建 Server 实例
# ============================================================
# Server 是 MCP 的核心类，负责：
# 1. 注册工具（通过装饰器）
# 2. 处理 JSON-RPC 请求
# 3. 路由到对应的处理函数

server = Server("security-tools")
# 参数是服务器名称，会显示在 Client 连接时


# ============================================================
# 注册工具列表函数
# ============================================================
# @server.list_tools() 装饰器：
# - 当 Client 发送 tools/list 请求时自动调用
# - 返回所有可用工具的定义
# - 每个工具包含 name, description, inputSchema

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """
    返回可用工具列表

    Tool 结构：
    - name: 工具名称（调用时使用）
    - description: 工具描述（LLM 根据此描述决定何时调用）
    - inputSchema: 参数的 JSON Schema（定义参数类型和验证规则）

    Returns:
        list[types.Tool]: 工具列表
    """
    return [
        # 工具 1：Nmap 端口扫描
        types.Tool(
            name="nmap_scan",
            description="使用 Nmap 扫描目标主机",
            # inputSchema 使用 JSON Schema 格式
            # 定义参数类型、描述、是否必填、可选值等
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "目标 IP 或主机名"
                    },
                    "scan_type": {
                        "type": "string",
                        "enum": ["quick", "full", "vuln"],
                        # enum 限制可选值，防止 LLM 生成无效参数
                        "description": "扫描类型: quick(快速), full(全端口), vuln(漏洞)"
                    }
                },
                "required": ["target"]
                # required: 必须提供的参数
            }
        ),

        # 工具 2：WHOIS 域名查询
        types.Tool(
            name="whois_lookup",
            description="查询域名 WHOIS 信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "要查询的域名"
                    }
                },
                "required": ["domain"]
            }
        ),

        # 工具 3：DNS 枚举
        types.Tool(
            name="dns_enum",
            description="DNS 枚举，获取域名解析记录",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "目标域名"
                    },
                    "record_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "记录类型: A, AAAA, MX, NS, TXT 等"
                    }
                },
                "required": ["domain"]
            }
        )
    ]


# ============================================================
# 注册工具执行函数
# ============================================================
# @server.call_tool() 装饰器：
# - 当 Client 发送 tools/call 请求时自动调用
# - 接收工具名称和参数
# - 根据名称路由到实际执行函数

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """
    根据工具名路由到对应的实际执行函数

    Args:
        name: 工具名称
        arguments: 工具参数（已验证，符合 inputSchema）

    Returns:
        list[types.TextContent]: 结果必须封装为此类型

    TextContent 结构：
        {"type": "text", "text": "结果字符串"}
    """
    # 根据工具名路由
    if name == "nmap_scan":
        result = await run_nmap_scan(
            arguments["target"],
            arguments.get("scan_type", "quick")
        )
    elif name == "whois_lookup":
        result = await run_whois(arguments["domain"])
    elif name == "dns_enum":
        result = await run_dns_enum(
            arguments["domain"],
            arguments.get("record_types", ["A", "MX", "NS"])
        )
    else:
        result = {"error": f"Unknown tool: {name}"}

    # 返回结果必须封装为 TextContent 列表
    # MCP 协议要求返回 content 列表，支持多种类型（text, image, resource）
    return [types.TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False, indent=2)
    )]


# ============================================================
# 实际工具函数
# ============================================================

async def run_nmap_scan(target: str, scan_type: str) -> dict:
    """
    执行 Nmap 扫描

    Args:
        target: 目标主机
        scan_type: 扫描类型 (quick/full/vuln)

    Returns:
        dict: 扫描结果
    """
    try:
        import nmap
        nm = nmap.PortScanner()

        # 根据扫描类型选择参数
        if scan_type == "quick":
            # 快速扫描：常用端口
            nm.scan(target, arguments="-F -T4")
        elif scan_type == "full":
            # 全端口扫描：1-65535
            nm.scan(target, arguments="-p- -T4")
        elif scan_type == "vuln":
            # 漏洞扫描：使用 vuln 脚本
            nm.scan(target, arguments="--script vuln -T4")

        # 构建结果
        results = {
            "target": target,
            "scan_type": scan_type,
            "hosts": []
        }

        # 解析扫描结果
        for host in nm.all_hosts():
            host_info = {
                "ip": host,
                "state": nm[host].state(),
                "ports": []
            }
            for proto in nm[host].all_protocols():
                for port in nm[host][proto].keys():
                    port_info = nm[host][proto][port]
                    host_info["ports"].append({
                        "port": port,
                        "state": port_info["state"],
                        "service": port_info.get("name", "unknown")
                    })
            results["hosts"].append(host_info)

        return results

    except ImportError:
        return {"error": "python-nmap not installed"}
    except Exception as e:
        return {"error": str(e)}


async def run_whois(domain: str) -> dict:
    """
    WHOIS 查询

    Args:
        domain: 要查询的域名

    Returns:
        dict: WHOIS 信息
    """
    try:
        import whois
        w = whois.whois(domain)
        return {
            "domain": domain,
            "registrar": w.registrar,
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "name_servers": list(w.name_servers) if w.name_servers else []
        }
    except ImportError:
        return {"error": "python-whois not installed"}
    except Exception as e:
        return {"error": str(e)}


async def run_dns_enum(domain: str, record_types: list) -> dict:
    """
    DNS 枚举

    Args:
        domain: 目标域名
        record_types: 记录类型列表

    Returns:
        dict: DNS 记录
    """
    import socket
    results = {"domain": domain, "records": {}}

    for rtype in record_types:
        try:
            if rtype == "A":
                # 使用 socket 解析 A 记录
                ip = socket.gethostbyname(domain)
                results["records"]["A"] = [ip]
            # 其他记录类型可添加 dnspython 支持
        except Exception as e:
            results["records"][rtype] = [f"Error: {str(e)}"]

    return results


# ============================================================
# 启动入口
# ============================================================

async def main():
    """
    启动 MCP Server，监听 stdin/stdout

    执行流程：
    1. stdio_server() 创建 stdin/stdout 通信通道
    2. server.run() 进入事件循环，等待 JSON-RPC 请求
    3. 收到请求后自动路由到对应装饰器函数

    通信模型：
    - 从 stdin 读取 Client 请求
    - 向 stdout 写入响应
    - 每行一个 JSON 消息
    """
    # stdio_server() 创建上下文管理器
    # 返回 (read_stream, write_stream)
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        # read_stream: 从 stdin 读取 Client 请求
        # write_stream: 向 stdout 写入响应

        # server.run() 进入主循环
        # 处理所有传入的 JSON-RPC 请求
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="security-tools",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
                # capabilities 告诉 Client Server 支持什么功能
                # - tools: 工具支持
                # - resources: 资源支持
                # - prompts: 提示词支持
            )
        )


if __name__ == "__main__":
    asyncio.run(main())