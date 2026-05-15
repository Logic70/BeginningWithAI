"""
测试 MCP Server 连接
验证 security-tools MCP 服务是否正常工作

这是一个简单的测试脚本，不使用 MCP SDK
直接通过 subprocess 和 JSON-RPC 与 Server 通信

用途：
  - 验证 MCP Server 是否能正常启动
  - 验证 initialize 和 tools/list 请求是否正常
  - 快速调试，不需要完整的 Client 实现

架构图：
  ┌─────────────────────────────────────────────────────────────┐
  │              test_mcp_client.py (本文件)                    │
  │  ┌─────────────────────────────────────────────────────┐   │
  │  │ 1. 启动 subprocess: python exp3_4_mcp_server.py     │   │
  │  │ 2. 向 stdin 写入 JSON-RPC 请求                       │   │
  │  │ 3. 从 stdout 读取 JSON-RPC 响应                      │   │
  │  └─────────────────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────────────────┘
                              ↓ subprocess + stdin/stdout
  ┌─────────────────────────────────────────────────────────────┐
  │                     exp3_4_mcp_server.py                    │
  │                     (MCP Server 进程)                       │
  └─────────────────────────────────────────────────────────────┘
"""

import asyncio
import json
from contextlib import asynccontextmanager


# ============================================================
# MCP Server 连接管理
# ============================================================

@asynccontextmanager
async def connect_mcp_server():
    """
    启动并连接到 MCP Server

    使用 subprocess 启动 Server 进程
    通过 stdin/stdout 进行通信

    Yields:
        proc: subprocess 进程对象
            - proc.stdin: 写入请求
            - proc.stdout: 读取响应

    使用方式：
        async with connect_mcp_server() as proc:
            proc.stdin.write(...)
            response = await proc.stdout.readline()
    """
    # 启动 MCP Server 作为子进程
    # stdin=PIPE: 允许向进程写入
    # stdout=PIPE: 允许从进程读取
    # stderr=PIPE: 捕获错误输出
    proc = await asyncio.create_subprocess_exec(
        "python",
        "experiments/phase3/exp3_4_mcp_server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    try:
        yield proc
    finally:
        # 确保进程被正确终止
        proc.terminate()
        await proc.wait()


# ============================================================
# 测试函数
# ============================================================

async def test_mcp_server():
    """
    测试 MCP Server 的基本功能

    测试流程：
    1. 发送 initialize 请求
    2. 验证初始化响应
    3. 发送 tools/list 请求
    4. 验证工具列表

    Returns:
        bool: 测试是否通过
    """
    print("=== MCP Server 测试 ===\n")

    async with connect_mcp_server() as proc:
        # ========== 步骤 1：发送初始化请求 ==========
        # initialize 是 MCP 协议的第一步
        # Client 必须先初始化才能发送其他请求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                # MCP 协议版本
                "capabilities": {},
                # Client 的能力（空表示无特殊能力）
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
                # Client 信息
            }
        }

        print("发送初始化请求...")

        # 写入请求到 stdin
        # 每个请求是一行 JSON，以换行符结束
        proc.stdin.write((json.dumps(init_request) + "\n").encode())
        await proc.stdin.drain()
        # drain() 确保数据被写入

        # 读取响应
        response = await asyncio.wait_for(
            proc.stdout.readline(),
            timeout=10
        )
        result = json.loads(response.decode())
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}\n")

        # ========== 步骤 2：发送工具列表请求 ==========
        # tools/list 获取 Server 提供的所有工具
        # 必须在 initialize 之后调用
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
            # tools/list 不需要参数
        }

        print("请求工具列表...")
        proc.stdin.write((json.dumps(list_tools_request) + "\n").encode())
        await proc.stdin.drain()

        # 读取响应
        response = await asyncio.wait_for(
            proc.stdout.readline(),
            timeout=10
        )
        result = json.loads(response.decode())

        # 验证结果
        if "result" in result and "tools" in result["result"]:
            tools = result["result"]["tools"]
            print(f"发现 {len(tools)} 个工具:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
            return True

        return False


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    if success:
        print("\nMCP Server 测试通过！")
    else:
        print("\nMCP Server 测试失败")