"""
实验 3.4c: MCP 工具发现 + LangChain Agent 集成
展示 MCP Client 如何动态发现工具并让 LangChain Agent 使用

运行环境：WSL (推荐) 或 Windows
运行方式：
  python exp3_4c_mcp_langchain_agent.py --mode discover  # 测试工具发现
  python exp3_4c_mcp_langchain_agent.py --mode agent     # 运行 Agent

核心流程：
  1. MCP Client 连接 Server (initialize)
  2. 动态发现可用工具 (tools/list)
  3. 转换为 LangChain Tool 格式 (JSON Schema → Pydantic)
  4. LangChain Agent 自动决策和调用 (tools/call)

架构图：
  ┌─────────────────┐     stdio/JSON-RPC     ┌─────────────────┐
  │  MCP Client     │◄──────────────────────►│  MCP Server     │
  │  (本文件)        │                        │  (exp3_4)       │
  │  ┌───────────┐  │                        │  ┌───────────┐  │
  │  │ Agent     │  │                        │  │ nmap_scan │  │
  │  │ LLM       │  │                        │  │ whois     │  │
  │  └───────────┘  │                        │  │ dns_enum  │  │
  └─────────────────┘                        │  └───────────┘  │
                                             └─────────────────┘
"""

# ==================== 标准库导入 ====================
import asyncio      # 异步编程：支持 async/await 语法
import json         # JSON 解析：处理 MCP 消息格式
import os           # 环境变量：读取 API Key 等配置
import sys          # 系统信息：检测运行平台
from pathlib import Path        # 路径处理：跨平台路径操作
from typing import Any, Optional, Type  # 类型注解：提升代码可读性

# ==================== Windows 编码修复 ====================
# 问题：Windows CMD 默认使用 GBK 编码，无法正确显示中文
# 解决：强制将标准输出/错误流设置为 UTF-8 编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ==================== 环境变量加载 ====================
from dotenv import load_dotenv
# Path(__file__) 获取当前文件路径
# .parent.parent.parent 向上三级到达项目根目录
# 这样可以在任意位置运行脚本都能正确找到 .env 文件
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# ==================== MCP SDK 导入 ====================
# MCP 官方 Python SDK，提供 Client 端核心功能
from mcp import ClientSession, StdioServerParameters

# ClientSession: MCP 协议会话管理
# StdioServerParameters: 配置如何启动 Server 进程

from mcp.client.stdio import stdio_client
# stdio_client: 通过 stdin/stdout 与 Server 进程通信

# ==================== LangChain 导入 ====================
from langchain_core.tools import BaseTool
# BaseTool: LangChain 工具基类，所有自定义工具都需要继承它
# 要求实现 _run() 同步方法或 _arun() 异步方法

from langchain_core.callbacks import CallbackManagerForToolRun
# 回调管理器：用于追踪工具执行过程（本文件未使用）

from langchain_ollama import ChatOllama
# ChatOllama: LangChain 对 Ollama 本地模型的封装

from langchain_openai import ChatOpenAI
# ChatOpenAI: LangChain 对 OpenAI 兼容 API 的封装
# 可连接 OpenAI 官方或任何兼容 API（如 vLLM、Ollama OpenAI 模式）

from langchain.agents import create_agent
# create_agent: LangChain 1.2+ 新 API，创建工具调用 Agent
# 底层基于 LangGraph 实现，但提供了更简洁的接口

from pydantic import BaseModel, Field
# BaseModel: Pydantic 数据模型基类，用于参数验证
# Field: 字段定义，支持默认值、描述、验证规则


# ============================================================
# 核心类 1：MCP 工具发现器
# ============================================================
# 职责：管理 MCP Server 连接生命周期，提供工具发现和调用能力
# 设计模式：封装 MCP SDK 的复杂性，提供简洁的异步接口

class MCPToolDiscovery:
    """
    MCP 工具发现器

    职责：
    1. 启动并连接 MCP Server 进程
    2. 发送 initialize 消息完成协议握手
    3. 发送 tools/list 消息发现可用工具
    4. 发送 tools/call 消息调用工具
    5. 管理连接生命周期（连接/断开）
    """

    def __init__(self, command: str, args: list[str]):
        """
        初始化发现器

        Args:
            command: 启动 MCP Server 的命令，如 "python"、"node"
            args: 命令行参数列表，如 ["server.py"]

        示例：
            discovery = MCPToolDiscovery("python", ["exp3_4_mcp_server.py"])
            # 等效于运行: python exp3_4_mcp_server.py
        """
        self.command = command
        self.args = args
        # MCP 会话对象，初始化为 None，connect() 后才有效
        self.session: Optional[ClientSession] = None
        # 内部使用的上下文管理器引用（用于正确释放资源）
        self._context = None
        # 工具缓存（避免重复请求）
        self._tools_cache: list = []

    async def connect(self):
        """
        连接到 MCP Server 并完成初始化握手

        执行流程：
        1. 配置 Server 启动参数
        2. 启动子进程，建立 stdin/stdout 通信管道
        3. 创建 MCP 协议会话
        4. 发送 initialize 消息，获取 Server 信息

        Returns:
            InitResult: 包含 serverInfo 和 capabilities

        MCP 协议层面的消息：
        Client → Server: {"method": "initialize", "params": {...}}
        Server → Client: {"result": {"serverInfo": {...}, "capabilities": {...}}}
        """
        # 步骤 1：配置如何启动 Server 进程
        server_params = StdioServerParameters(
            command=self.command,    # 如 "python"
            args=self.args,          # 如 ["server.py"]
        )

        # 步骤 2：启动 Server 子进程，建立 stdio 连接
        # stdio_client 返回一个异步上下文管理器
        # __aenter__ 返回 (read_stream, write_stream) 用于通信
        self._stdio_context = stdio_client(server_params)
        read, write = await self._stdio_context.__aenter__()
        # read: 从 Server 的 stdout 读取响应
        # write: 向 Server 的 stdin 写入请求

        # 步骤 3：创建 MCP 协议会话
        # ClientSession 负责处理 JSON-RPC 协议细节
        # 包括消息序列化、请求ID管理、响应解析等
        self._session_context = ClientSession(read, write)
        self.session = await self._session_context.__aenter__()

        # 步骤 4：发送 initialize 消息，完成 MCP 协议握手
        # 这是 MCP 协议要求的第一步，必须在其他操作之前执行
        init_result = await self.session.initialize()
        # init_result 包含：
        # - serverInfo: {name: "security-tools", version: "0.1.0"}
        # - capabilities: {tools: {...}, resources: {...}, ...}

        return init_result

    async def disconnect(self):
        """
        断开与 MCP Server 的连接

        注意：必须按创建的逆序关闭上下文管理器
        1. 先关闭 session（协议层）
        2. 再关闭 stdio（传输层）

        否则可能导致资源泄漏或进程残留
        """
        # 关闭协议会话
        if self._session_context:
            # __aexit__ 的三个参数是 (exc_type, exc_val, exc_tb)
            # 传入 None 表示正常退出，不传播异常
            await self._session_context.__aexit__(None, None, None)
        # 关闭 stdio 连接（这会终止 Server 子进程）
        if self._stdio_context:
            await self._stdio_context.__aexit__(None, None, None)

    async def discover_tools(self) -> list:
        """
        发现 MCP Server 提供的所有工具

        Returns:
            list[Tool]: 工具列表，每个 Tool 对象包含：
                - name: 工具名称，如 "nmap_scan"
                - description: 工具描述
                - inputSchema: 参数的 JSON Schema 定义

        MCP 协议层面的消息：
        Client → Server: {"method": "tools/list"}
        Server → Client: {"result": {"tools": [{...}, {...}]}}

        示例返回值结构：
        [
            Tool(
                name="dns_enum",
                description="DNS 枚举工具",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string", "description": "域名"}
                    },
                    "required": ["domain"]
                }
            ),
            ...
        ]
        """
        if not self.session:
            raise RuntimeError("未连接到 MCP Server，请先调用 connect()")

        # 调用 MCP SDK 的 list_tools 方法
        result = await self.session.list_tools()
        # 缓存工具列表（供后续使用）
        self._tools_cache = result.tools
        return self._tools_cache

    async def call_tool(self, name: str, arguments: dict) -> str:
        """
        调用 MCP Server 的工具并返回结果

        Args:
            name: 工具名称，如 "dns_enum"
            arguments: 工具参数，如 {"domain": "baidu.com"}

        Returns:
            str: 工具执行结果（文本格式）

        MCP 协议层面的消息：
        Client → Server: {
            "method": "tools/call",
            "params": {
                "name": "dns_enum",
                "arguments": {"domain": "baidu.com"}
            }
        }
        Server → Client: {
            "result": {
                "content": [{"type": "text", "text": "{...}"}]
            }
        }
        """
        if not self.session:
            raise RuntimeError("未连接到 MCP Server")

        # 调用 MCP SDK 的 call_tool 方法
        result = await self.session.call_tool(name, arguments=arguments)

        # MCP 返回的是 content 列表，需要提取文本内容
        # content 可能包含多种类型：text、image、resource 等
        # 对于我们的安全工具，通常只有 text 类型
        for content in result.content:
            if content.type == "text":
                return content.text

        # 如果没有文本内容，返回原始内容的字符串表示
        return str(result.content)

    def get_server_info(self, init_result) -> dict:
        """
        从初始化结果中提取 Server 信息

        Args:
            init_result: connect() 返回的初始化结果

        Returns:
            dict: {
                "name": "security-tools",
                "version": "0.1.0",
                "capabilities": {...}
            }
        """
        return {
            "name": init_result.serverInfo.name,
            "version": init_result.serverInfo.version,
            "capabilities": init_result.capabilities
        }


# ============================================================
# 核心类 2：MCP → LangChain 工具适配器
# ============================================================
# 职责：将 MCP 工具适配为 LangChain 可用的 Tool 对象
# 设计模式：适配器模式（Adapter Pattern）
#   - MCP 工具有自己的格式（JSON Schema）
#   - LangChain 要求工具继承 BaseTool 并提供 Pydantic 参数模型
#   - 本类负责格式转换

class MCPToolAdapter(BaseTool):
    """
    将 MCP 工具适配为 LangChain Tool

    设计思路：
    1. 继承 LangChain 的 BaseTool 基类
    2. 持有 MCPToolDiscovery 引用（复用已有的 MCP 连接）
    3. 将 MCP 的 JSON Schema 转换为 LangChain 需要的 Pydantic 模型
    4. 实现 _arun() 方法，调用 MCP Server

    为什么需要这个适配器？
    - MCP Server 返回的工具定义是 JSON Schema 格式
    - LangChain Agent 要求工具是 BaseTool 子类
    - 这个类在两者之间建立桥梁
    """

    # ==================== 类属性 ====================
    # Pydantic 会自动验证这些属性的类型

    # MCP 连接管理器引用（用于实际调用 MCP Server）
    mcp_discovery: MCPToolDiscovery = None
    # MCP 工具名称（与 Server 端注册的名称一致）
    mcp_tool_name: str = ""
    # 参数模型（Pydantic BaseModel，用于参数验证）
    args_schema: Type[BaseModel] = None

    def __init__(
        self,
        name: str,
        description: str,
        mcp_discovery: MCPToolDiscovery,
        input_schema: dict
    ):
        """
        初始化适配器

        Args:
            name: 工具名称（传递给 LangChain）
            description: 工具描述（LLM 会看到这个描述）
            mcp_discovery: MCP 连接管理器（用于调用 Server）
            input_schema: MCP 工具的 inputSchema（JSON Schema 格式）
        """
        # 动态创建 Pydantic 参数模型
        # 这样 LangChain Agent 就能知道工具需要什么参数
        args_model = self._create_args_model(name, input_schema)

        # 调用父类初始化
        super().__init__(
            name=name,                           # LangChain 使用的工具名
            description=description,             # LLM 看到的工具描述
            mcp_discovery=mcp_discovery,         # MCP 连接引用
            mcp_tool_name=name,                  # 用于调用 MCP Server
            args_schema=args_model               # 参数验证模型
        )

    @staticmethod
    def _create_args_model(tool_name: str, schema: dict) -> Type[BaseModel]:
        """
        根据 JSON Schema 动态创建 Pydantic 模型

        这是本类的核心方法，实现了格式转换：
        MCP inputSchema (JSON Schema) → LangChain args_schema (Pydantic Model)

        为什么需要动态创建？
        - 不同工具有不同的参数结构
        - 我们在编写代码时不知道 MCP Server 有哪些工具
        - 需要根据运行时获取的 schema 动态生成模型

        Args:
            tool_name: 工具名称（用于生成模型类名）
            schema: MCP 工具的 inputSchema

        Returns:
            Type[BaseModel]: 动态创建的 Pydantic 模型类

        示例转换：
            输入 schema:
            {
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "description": "域名"},
                    "record_types": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["domain"]
            }

            输出 Pydantic 模型:
            class DnsEnumArgs(BaseModel):
                domain: str = Field(..., description="域名")
                record_types: list = Field(None, description="")
        """
        fields = {}  # 存储字段定义
        properties = schema.get("properties", {})  # 获取属性定义
        required = set(schema.get("required", []))  # 获取必填字段列表

        # 遍历每个属性，转换为 Pydantic Field
        for prop_name, prop_def in properties.items():
            # 获取属性类型（默认 string）
            prop_type = prop_def.get("type", "string")
            # 获取属性描述
            description = prop_def.get("description", "")
            # 设置默认值：必填字段用 ...（Ellipsis），可选字段用 None
            # ... 在 Pydantic 中表示"必须提供，无默认值"
            default = ... if prop_name in required else None

            # JSON Schema 类型 → Python 类型映射
            type_map = {
                "string": str,
                "integer": int,
                "number": float,    # JSON 的 number 包括整数和浮点数
                "boolean": bool,
                "array": list,
                "object": dict
            }
            python_type = type_map.get(prop_type, str)  # 未知类型默认为 str

            # 创建字段定义：(类型, Field对象)
            fields[prop_name] = (python_type, Field(default=default, description=description))

        # 动态创建 Pydantic 模型类
        # type() 函数可以动态创建类：
        # type(类名, 父类元组, 属性字典)
        return type(
            f"{tool_name.title().replace('_', '')}Args",  # 类名，如 "DnsEnumArgs"
            (BaseModel,),                                  # 父类
            {
                "__annotations__": {k: v[0] for k, v in fields.items()},  # 类型注解
                **{k: v[1] for k, v in fields.items()}  # Field 定义
            }
        )

    def _run(self, **kwargs) -> str:
        """
        同步执行方法（LangChain 默认调用）

        LangChain 的 Agent 默认使用同步方式调用工具
        但 MCP 操作是异步的，所以这里用 asyncio.run() 包装

        Args:
            **kwargs: 工具参数，由 Agent 根据用户输入填充

        Returns:
            str: 工具执行结果
        """
        # asyncio.run() 创建新的事件循环并运行异步函数
        print(f"\n[DEBUG-1] _run 被调用，参数: {kwargs}")
        print(f"[DEBUG-2] 工具名: {self.mcp_tool_name}")
        result = asyncio.run(self._arun(**kwargs))
        print(f"[DEBUG-3] _run 返回结果: {result[:100]}...")
        return result
        

    async def _arun(self, **kwargs) -> str:
        """
        异步执行方法 - 真正调用 MCP Server 的地方

        这是工具执行的入口点：
        1. Agent 决定调用这个工具
        2. LangChain 调用 tool._arun(domain="baidu.com")
        3. 本方法通过 mcp_discovery 发送 MCP 请求
        4. MCP Server 执行实际工具并返回结果

        Args:
            **kwargs: 工具参数，如 {"domain": "baidu.com"}

        Returns:
            str: MCP Server 返回的结果文本
        """
        # 通过 MCP 连接调用 Server 端的工具
        print(f"[DEBUG-4] _arun 被调用")
        result = await self.mcp_discovery.call_tool(self.mcp_tool_name, kwargs)
        print(f"[DEBUG-5] MCP Server 返回: {result[:100]}...")
        return result


# ============================================================
# 工厂函数：批量创建 LangChain Tools
# ============================================================

async def create_langchain_tools_from_mcp(
    command: str,
    args: list[str]
) -> tuple[MCPToolDiscovery, list[BaseTool]]:
    """
    从 MCP Server 创建 LangChain 工具集

    这是一个便捷函数，封装了完整的工具发现和转换流程：
    1. 创建 MCP 连接
    2. 发现所有工具
    3. 转换为 LangChain 格式

    Args:
        command: 启动 MCP Server 的命令
        args: 命令行参数

    Returns:
        tuple: (discovery, tools)
            - discovery: MCPToolDiscovery 实例（需要保留，用于断开连接）
            - tools: LangChain Tool 列表（直接传给 Agent）

    使用示例：
        discovery, tools = await create_langchain_tools_from_mcp(
            "python", ["exp3_4_mcp_server.py"]
        )
        try:
            agent = create_agent(llm, tools)
            result = await agent.ainvoke({...})
        finally:
            await discovery.disconnect()
    """
    # 步骤 1：创建发现器并连接到 MCP Server
    discovery = MCPToolDiscovery(command, args)
    init_result = await discovery.connect()

    # 打印 Server 信息（帮助调试）
    print(f"[OK] 已连接到 MCP Server: {init_result.serverInfo.name}")
    print(f"   能力: {init_result.capabilities}")

    # 步骤 2：发现所有可用工具
    mcp_tools = await discovery.discover_tools()
    print(f"[Tools] 发现 {len(mcp_tools)} 个工具")

    # 步骤 3：将每个 MCP 工具转换为 LangChain Tool
    langchain_tools = []
    for mcp_tool in mcp_tools:
        # 创建适配器实例
        tool = MCPToolAdapter(
            name=mcp_tool.name,                  # 工具名称
            description=mcp_tool.description,    # 工具描述
            mcp_discovery=discovery,             # MCP 连接引用
            input_schema=mcp_tool.inputSchema    # 参数 Schema
        )
        langchain_tools.append(tool)
        print(f"   - {mcp_tool.name}: {mcp_tool.description[:30]}...")

    # 返回发现器和工具列表
    # 注意：调用者负责在不需要时调用 discovery.disconnect()
    return discovery, langchain_tools


# ============================================================
# LangChain Agent 示例
# ============================================================

def get_llm(backend: str = "openai"):
    """
    获取 LLM 实例

    支持两种后端：
    1. ollama: 本地 Ollama 服务（无需 API Key）
    2. openai: OpenAI 兼容 API（可以是任何兼容服务）

    Args:
        backend: 后端类型，"ollama" 或 "openai"

    Returns:
        LLM 实例

    环境变量配置（.env 文件）：
        OLLAMA_MODEL=qwen2.5:7b
        OPENAI_MODEL=deepseek-v4-pro
        OPENAI_API_KEY=sk-xxx
        OPENAI_BASE_URL=https://opencode.ai/zen/go/v1

    参考：exp3_2c_react_agent_langchain.py
    """
    if backend == "ollama":
        # Ollama 本地模型
        # 前提：已安装 Ollama 并运行 ollama serve
        return ChatOllama(model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"))
    elif backend == "openai":
        # OpenAI 兼容 API
        # 可以连接 OpenAI 官方、DeepSeek、通义千问等
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "deepseek-v4-pro"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    raise ValueError(f"未知后端: {backend}")


async def run_langchain_agent(backend: str = "openai"):
    """
    使用 LangChain Agent 自动调用 MCP 工具

    完整流程演示：
    1. 连接 MCP Server 并发现工具
    2. 创建 LLM 实例
    3. 创建 Agent（LLM + 工具）
    4. 执行用户任务
    5. 打印执行过程
    6. 断开连接

    Agent 执行流程：
    ┌─────────────────────────────────────────────────────┐
    │ 用户: "查询 github.com 的 DNS A 记录"                │
    └─────────────────────────────────────────────────────┘
                            ↓
    ┌─────────────────────────────────────────────────────┐
    │ LLM 思考: 需要调用 dns_enum 工具                     │
    │ 决策: tool_calls = [{name: "dns_enum", args: {...}}]│
    └─────────────────────────────────────────────────────┘
                            ↓
    ┌─────────────────────────────────────────────────────┐
    │ Agent 调用: dns_enum(domain="github.com")           │
    │ MCPToolAdapter._arun() → MCP Server                 │
    └─────────────────────────────────────────────────────┘
                            ↓
    ┌─────────────────────────────────────────────────────┐
    │ MCP Server 返回: {"records": {"A": ["140.82.121.4"]}}│
    └─────────────────────────────────────────────────────┘
                            ↓
    ┌─────────────────────────────────────────────────────┐
    │ LLM 生成最终回答: "github.com 的 A 记录是..."         │
    └─────────────────────────────────────────────────────┘

    更新说明 (2026-03):
    - 使用 langchain.agents.create_agent 替代 langgraph.prebuilt.create_react_agent
    - 支持 ollama 和 openai 两种后端
    """
    print("=" * 60)
    print("MCP + LangChain Agent 集成演示")
    print("=" * 60)
    print(f"后端: {backend}")

    # ==================== 步骤 1：连接 MCP Server 并发现工具 ====================
    discovery, tools = await create_langchain_tools_from_mcp(
        command="python",
        args=["experiments/phase3/exp3_4_mcp_server.py"]
    )

    try:
        # ==================== 步骤 2：创建 LLM 和 Agent ====================
        llm = get_llm(backend)

        # 使用 LangChain 新 API 创建 Agent
        # create_agent 内部会：
        # 1. 创建 ReAct 风格的提示词模板
        # 2. 绑定工具到 LLM（使用 function calling）
        # 3. 设置 Agent 执行循环
        agent = create_agent(
            llm,
            tools,
            system_prompt="你是一个网络安全分析助手，可以使用 DNS 和 WHOIS 工具帮助用户分析域名。"
        )

        # ==================== 步骤 3：执行任务 ====================
        print("\n" + "=" * 60)
        print("开始执行任务: 查询 github.com 的 DNS A 记录")
        print("=" * 60)

        # Agent 的输入是 messages 格式
        # ainvoke 是异步执行方法
        result = await agent.ainvoke({
            "messages": [("user", "查询 github.com 的 DNS A 记录")]
        })
        # result 结构：{"messages": [HumanMessage, AIMessage, ToolMessage, ...]}

        # ==================== 步骤 4：打印执行过程 ====================
        print("\n--- 执行过程 ---")
        for msg in result["messages"]:
            # 检查是否有工具调用（AI 决定调用工具）
            if hasattr(msg, "tool_calls") and msg.tool_calls:# hasattr函数检查msg中是否有tool_call属性
                for tc in msg.tool_calls:
                    print(f"[调用] {tc['name']}({json.dumps(tc['args'], ensure_ascii=False)})")
            # 检查是否是工具返回结果
            elif msg.type == "tool":
                content = str(msg.content)[:100] if msg.content else ""
                print(f"[结果] {content}...")
            # 检查是否是 AI 最终回答
            elif msg.type == "ai" and msg.content:
                print(f"[回答] {msg.content[:200]}...")

    finally:
        # ==================== 步骤 5：清理连接 ====================
        # 重要：必须在 finally 块中断开连接
        # 否则 MCP Server 进程会残留
        await discovery.disconnect()
        print("\n[OK] 已断开 MCP 连接")


# ============================================================
# 测试函数：手动调用工具（不通过 LLM）
# ============================================================

async def test_tool_discovery():
    """
    测试 MCP 工具发现流程

    用途：验证 MCP 连接和工具发现是否正常工作
    场景：调试时不想消耗 LLM API 调用次数

    执行内容：
    1. 连接 MCP Server
    2. 打印所有发现的工具
    3. 手动调用 dns_enum 工具
    4. 打印结果
    """
    print("=" * 60)
    print("测试 MCP 工具发现")
    print("=" * 60)

    # 创建 MCP 连接
    discovery = MCPToolDiscovery(
        command="python",
        args=["experiments/phase3/exp3_4_mcp_server.py"]
    )

    try:
        # 连接到 Server
        init_result = await discovery.connect()
        print(f"[OK] 连接成功: {init_result.serverInfo.name} v{init_result.serverInfo.version}")

        # 发现工具
        tools = await discovery.discover_tools()
        print(f"\n[Tools] 发现 {len(tools)} 个工具:")
        for tool in tools:
            print(f"\n   工具名: {tool.name}")
            print(f"   描述: {tool.description}")
            print(f"   参数: {json.dumps(tool.inputSchema, ensure_ascii=False, indent=6)}")

        # 手动调用工具
        print("\n" + "=" * 60)
        print("手动调用 dns_enum 工具...")
        print("=" * 60)

        result = await discovery.call_tool(
            "dns_enum",
            {"domain": "baidu.com", "record_types": ["A"]}
        )
        print(f"\n结果: {result}")

    finally:
        await discovery.disconnect()


# ============================================================
# 主程序入口
# ============================================================

if __name__ == "__main__":
    import argparse

    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="MCP + LangChain Agent")
    parser.add_argument(
        "--mode", "-m",
        choices=["discover", "agent"],
        default="agent",
        help="discover=测试工具发现, agent=运行 LangChain Agent"
    )
    parser.add_argument(
        "--backend", "-b",
        choices=["ollama", "openai"],
        default="openai",
        help="LLM 后端 (默认: openai)"
    )
    args = parser.parse_args()

    # 根据模式执行不同的函数
    if args.mode == "discover":
        # 测试工具发现（不消耗 LLM API）
        asyncio.run(test_tool_discovery())
    else:
        # 运行完整的 Agent
        asyncio.run(run_langchain_agent(args.backend))