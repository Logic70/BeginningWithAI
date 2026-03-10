# 阶段三：Agent、Dify 与 A2A 开发

> 预计时间：6-8 周 | 核心问题：如何让模型调用工具、编排工作流、实现多 Agent 协作？

---

## 🎯 阶段目标

完成本阶段后，你将能够：
- ✅ 理解 Agent 架构与工作原理
- ✅ 实现 Function Calling 工具调用
- ✅ 开发 MCP Server 扩展模型能力
- ✅ 使用 Dify 可视化编排 Agent 工作流
- ✅ 掌握 A2A 协议实现多 Agent 协作
- ✅ 构建自动化安全测试 Agent

---

## 📦 环境准备

```powershell
# 激活虚拟环境
cd d:\Security\AILearningwithAI
.\venv\Scripts\activate

# 安装 Agent 核心依赖
pip install langchain langgraph langchain-community
pip install langchain-openai langchain-ollama python-dotenv
pip install mcp  # MCP Python SDK
pip install python-nmap shodan requests

# 安装 A2A 依赖
pip install a2a-sdk httpx
```

### Dify 部署（Docker）

```powershell
# 克隆并启动 Dify
git clone https://github.com/langgenius/dify.git
cd dify/docker
cp .env.example .env
docker compose up -d
```

启动后访问 `http://localhost` 即可使用 Dify 平台。

---

## 📋 Agent 底层逻辑概览

> 在进入具体实验之前，先理解 Agent 工具调用的底层原理。各技术（MCP、Skill 等）的详细说明见对应实验章节，全景对比见末尾「工具调用模式总结」。

### Function Calling 的 5 步生命周期

这是理解所有 Agent 框架的基石：

```
步骤 1: 初始化 Client/LLM
         │
步骤 2: 定义 Tools List（函数说明书）
         │
步骤 3: 第一次调用（问题 + Tools → 模型）
         │  模型不直接回答，返回: "我要调 scan_port，参数是 {...}"
         │
步骤 4: 本地执行工具
         │  运行 TOOL_MAP["scan_port"](**args)，拿到真实结果
         │
步骤 5: 第二次调用（原问题 + 调用指令 + 工具结果 → 模型）
            模型看完结果，生成最终自然语言回答
```

> **本质**：模型只做决策不执行，代码只做执行不思考。二者通过消息传递协作。

### 从 Function Calling 到 ReAct Agent

以上 5 步是**单次工具调用**的闭环。真正的 Agent 只是加了 `while True`：

```python
while True:
    response = llm.invoke(messages)    # 问模型
    if response.tool_calls:            # 模型要调工具？
        执行工具 → 将结果追加到 messages → continue
    else:
        break  # 模型直接回答了 → 退出循环
```

这就是 ReAct Agent 的中心引擎。无论手写还是 `create_react_agent()`，底层都是这个循环。

---

## 🧪 实验 3.1：Function Calling 基础

### 目标
理解并实现 LLM 的工具调用能力。

### 📖 核心概念：Agent 与工具调用

#### 什么是 Agent？

Agent 是一种能够自主决策和执行任务的 AI 系统。

```
用户目标 → Agent 规划 → 工具调用 → 观察结果 → 继续/完成
```

#### Agent 核心能力

| 能力 | 描述 |
|------|------|
| 规划 | 将复杂任务分解为可执行步骤 |
| 记忆 | 保持对话历史和任务状态 |
| 工具使用 | 调用外部 API 和工具 |
| 反思 | 根据结果调整策略 |

### 📘 API 参考：`ollama.chat()` 的 `tools` 扩展

在基础 `ollama.chat()` 调用（参见阶段一 API 参考）之上新增 `tools` 参数，使模型具备工具调用能力。

#### 新增入参：`tools`

```python
response = ollama.chat(
    model="qwen2.5:7b",
    messages=[...],
    tools=[...]      # 新增：工具定义列表
)
```

##### `tools` 工具定义结构

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "scan_port",                    # 工具名称
            "description": "扫描目标主机的指定端口",   # 工具描述（模型据此判断何时调用）
            "parameters": {                          # 参数定义（JSON Schema 格式）
                "type": "object",
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "目标主机IP"
                    },
                    "port": {
                        "type": "integer",
                        "description": "端口号"
                    }
                },
                "required": ["host", "port"]         # 必填参数
            }
        }
    }
]
```

#### 返回值变化：`message.tool_calls`

当模型判断需要调用工具时，`response.message.content` 为空，转而在 `tool_calls` 中返回调用请求：

```python
# response.message.tool_calls 结构：
[
    ToolCall(
        function=Function(
            name="scan_port",                # 模型决定调用的工具名
            arguments={"host": "localhost", "port": 80}  # 已解析为 dict
        )
    )
]
```

两种等效的访问方式：
```python
# 属性访问
name = tool_call.function.name
args = tool_call.function.arguments

# 字典访问
name = tool_call["function"]["name"]
args = tool_call["function"]["arguments"]
```

#### 两阶段调用流程

```
第一阶段                          第二阶段
┌─────────────┐               ┌─────────────┐
│ ollama.chat │               │ ollama.chat │
│  + tools    │               │  + tools    │
└──────┬──────┘               └──────┬──────┘
       │                             │
       ▼                             ▼
  response.message              final.message
  .tool_calls ≠ None            .content = "最终回答"
       │
       ▼
  你的代码执行工具
  TOOL_MAP[name](**args)
       │
       ▼
  将结果追加到 messages：
  ┌────────────────────────────┐
  │ messages.append(           │
  │   response.message         │ ← assistant 的工具调用消息
  │ )                          │
  │ messages.append({          │
  │   "role": "tool",          │ ← 工具执行结果
  │   "content": json.dumps(), │
  │   "tool_name": func_name   │ ← 必须指定
  │ })                         │
  └────────────────────────────┘
```

> **注意**：`tool_calls` 在 `response.message` 下面，不在 `response` 顶层。这是最常见的踩坑点。

### 代码示例

创建文件 `experiments/phase3/exp3_1_function_calling.py`：

```python
"""
实验 3.1: Function Calling 基础
使用 Ollama 实现工具调用
"""
import ollama
import json

# 定义工具
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


def scan_port(host: str, port: int) -> dict:
    """模拟端口扫描"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        is_open = result == 0
        return {"host": host, "port": port, "open": is_open}
    except Exception as e:
        return {"host": host, "port": port, "error": str(e)}


def check_vulnerability(target: str, vuln_type: str) -> dict:
    """模拟漏洞检查（演示用）"""
    # 实际应用中应调用真实的漏洞扫描器
    return {
        "target": target,
        "vuln_type": vuln_type,
        "status": "scan_completed",
        "findings": []  # 演示用，无发现
    }


# 工具映射
TOOL_MAP = {
    "scan_port": scan_port,
    "check_vulnerability": check_vulnerability
}


def chat_with_tools(user_message: str, model: str = "qwen2.5:7b"):
    """带工具调用的对话"""
    messages = [{"role": "user", "content": user_message}]
    
    # 第一次调用：让模型决定是否使用工具
    response = ollama.chat(
        model=model,
        messages=messages,
        tools=tools
    )
    
    # 检查是否有工具调用（注意：用属性访问，不是字典）
    if response.message.tool_calls:
        for tool_call in response.message.tool_calls:
            func_name = tool_call.function.name
            func_args = tool_call.function.arguments  # 已经是 dict，无需 json.loads
            
            print(f"\n🔧 调用工具: {func_name}")
            print(f"   参数: {json.dumps(func_args, ensure_ascii=False)}")
            
            # 执行工具
            if func_name in TOOL_MAP:
                result = TOOL_MAP[func_name](**func_args)
                print(f"   结果: {json.dumps(result, ensure_ascii=False)}")
                
                # 将 assistant 消息和工具结果追加到对话历史
                messages.append(response.message)
                messages.append({
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False),
                    "tool_name": func_name
                })
        
        # 第二次调用：根据工具结果生成最终回答
        final_response = ollama.chat(
            model=model,
            messages=messages,
            tools=tools
        )
        return final_response.message.content
    
    return response.message.content


if __name__ == "__main__":
    # 测试用例
    test_queries = [
        "帮我扫描一下 localhost 的 80 端口是否开放",
        "检查 example.com 是否存在 SQL 注入漏洞",
        "分析一下常见的 Web 安全漏洞"  # 不需要工具的问题
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"问题: {query}")
        print("="*60)
        result = chat_with_tools(query)
        print(f"\n💬 回答: {result}")
```

### 验证标准
- [x] 模型能识别何时需要工具
- [x] 工具参数提取正确
- [x] 工具执行结果正确返回
- [x] 最终回答整合了工具结果

### 常见问题与踩坑记录

#### 1. Ollama SDK 的两种访问方式

`ChatResponse` 对象**同时支持属性访问和字典访问**，两种方式等效：

```python
# 方式一：属性访问
response.message.content
response.message.tool_calls
tool_call.function.name
tool_call.function.arguments

# 方式二：字典访问（与 exp1_2 中的用法一致）
response["message"]["content"]
response["message"]["tool_calls"]
tool_call["function"]["name"]
tool_call["function"]["arguments"]
```

| 模式 | 返回类型 | 两种访问方式 |
|------|----------|----------|
| `stream=True` | 迭代器，每个 chunk 是 `dict` | 仅字典访问 `chunk["message"]["content"]` |
| `stream=False`（默认） | `ChatResponse` 对象 | 属性 `response.message.content` 或字典 `response["message"]["content"]` 均可 |

#### 2. `tool_calls` 的查找路径（踩坑重点）

**真正的 bug 不是访问方式（属性 vs 字典），而是查找路径写错了：**

```python
# ❌ 错误：在 response 顶层找 tool_calls，永远找不到
if "tool_calls" in response:  

# ✅ 正确：tool_calls 在 response.message 下面
if response.message.tool_calls:          # 属性方式
if response["message"].get("tool_calls"):  # 字典方式（也行）
```

`tool_calls` 不是你的代码生成的，而是 **LLM 在响应中返回的**。完整流程：

```
你定义 tools → 传给 ollama.chat() → LLM 分析用户意图
→ LLM 返回 tool_calls（"我要调这个工具，参数是这些"）
→ 你的代码执行工具 → 把结果传回 LLM → LLM 给出最终回答
```

#### 3. `arguments` 无需 `json.loads`

Ollama SDK 已自动将参数解析为 `dict`，直接使用即可，无需再调用 `json.loads()`：
```python
func_args = tool_call.function.arguments       # 属性方式，已是 dict
func_args = tool_call["function"]["arguments"]  # 字典方式，同样是 dict
```

#### 4. 工具结果消息格式

返回工具结果时需包含 `tool_name` 字段：
```python
messages.append({
    "role": "tool",
    "content": json.dumps(result),
    "tool_name": func_name  # 必须指定
})
```

#### 5. Python 参数默认值 vs 类型注解

```python
# ❌ 错误：这是类型注解，"qwen2.5:7b" 被当作类型，model 仍是必填参数
def chat_with_tools(model: "qwen2.5:7b"): ...

# ✅ 正确：这是默认参数值
def chat_with_tools(model: str = "qwen2.5:7b"): ...
```

#### 6. Windows 下 ping 命令差异

```python
# ❌ Linux 参数：-c (count), -W (timeout)
subprocess.run(["ping", "-c", "1", "-W", "5", ip])

# ✅ Windows 参数：-n (count), -w (timeout in ms)
subprocess.run(["ping", "-n", "1", "-w", "1000", ip])
```

### 场景 B：API Key 模式的 Function Calling

> Ollama 和 OpenAI 的 Function Calling 核心概念一致（tools 定义 → 模型返回 tool_calls → 执行 → 回传结果），但响应格式有差异。掌握这些差异后，你能灵活切换后端。

创建文件 `experiments/phase3/exp3_1b_function_calling_api.py`：

```python
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
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
)
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


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
```

#### Ollama vs OpenAI Function Calling 差异

| | Ollama | OpenAI |
|---|---|---|
| **tool_calls 路径** | `response.message.tool_calls` | `response.choices[0].message.tool_calls` |
| **arguments 类型** | `dict`（已解析，直接使用） | JSON 字符串（需 `json.loads()`） |
| **工具结果关联** | `"tool_name": func_name` | `"tool_call_id": tool_call.id` |
| **消息追加** | `messages.append(response.message)` | `messages.append(message)`（完整 message 对象） |

### 场景 C：LangChain 的 Tool Calling

> 手写 Function Calling 需要处理很多格式差异。LangChain 用 `@tool` 装饰器 + `bind_tools()` 统一了不同模型的工具调用接口，代码更简洁，切换模型也更方便。

创建文件 `experiments/phase3/exp3_1c_function_calling_langchain.py`：

```python
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
    
    # bind_tools: 将工具绑定到模型，一行搞定
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
```

#### 三种 Function Calling 实现对比

| | 原生 Ollama | 原生 OpenAI | LangChain |
|---|---|---|---|
| **工具定义** | 手写 JSON Schema | 手写 JSON Schema | `@tool` 装饰器自动生成 |
| **绑定工具** | `tools=tools` 参数 | `tools=tools` 参数 | `llm.bind_tools(tools)` |
| **解析参数** | 直接是 `dict` | 需 `json.loads()` | 自动解析 |
| **结果回传** | `tool_name` | `tool_call_id` | `ToolMessage` 统一处理 |
| **切换模型** | 改代码 | 改代码 | 改一行配置 |
| **代码量** | 中 | 中 | 少 |

### 📋 LangChain 框架进阶认知

> 在完成三种 Function Calling 实现对比后，以下是对 LangChain 框架设计哲学的进阶总结。

#### Message vs History：数据与容器的解耦

LangChain 将"消息"和"装消息的容器"分成了两个独立层：

```
Message 类（数据对象 — 只存数据）
├── HumanMessage(content="...")    → 用户消息
├── AIMessage(content="...")       → AI 回复
└── SystemMessage(content="...")   → 系统提示词

InMemoryChatMessageHistory（历史管理器 — 装消息的容器）
├── .add_user_message("...")   → 内部创建 HumanMessage 并追加
├── .add_ai_message("...")     → 内部创建 AIMessage 并追加
├── .add_message(msg)          → 直接追加任意 Message 对象
├── .messages                  → 返回消息列表
└── .clear()                   → 清空列表
```

`add_user_message` 是容器方法（语法糖），两者等价：

```python
history.add_user_message("什么是XSS？")              # 语法糖
history.add_message(HumanMessage(content="什么是XSS？"))  # 底层实现
```

> **扩展性**：`InMemoryChatMessageHistory` 只是内存实现。LangChain 还提供 `RedisChatMessageHistory`、`SQLChatMessageHistory` 等，切换存储只需换一个类，其余代码不变。

#### `langchain_core` vs `langchain`：底层与上层

```
langchain_core    ← 核心包（最底层，无多余依赖）
    └── tools, messages, chat_history 等定义在这里

langchain         ← 主包（依赖 langchain_core）
    └── 从 langchain_core 重新导出，加上社区工具
```

```python
from langchain_core.tools import tool    # ✅ 推荐：依赖更少，导入更快
from langchain.tools import tool         # 也行，但多了一层间接依赖
```

> **建议**：优先从 `langchain_core` 导入，这是官方推荐的面向未来的写法。

#### LCEL 统一接口哲学：万物皆可 invoke / stream

LangChain v0.1 后所有组件都实现了统一的 `Runnable` 接口：

| 方法 | 作用 | 返回类型 |
|------|------|----------|
| `.invoke(input)` | 一次性全量返回 | 完整结果 |
| `.stream(input)` | 逐字流式返回 | 生成器 |
| `.batch(inputs)` | 批量执行 | 结果列表 |
| `.ainvoke(input)` | 异步版 invoke | Awaitable |

**不论主体是 Chat 模型、Tool 工具、还是组合 Chain，一次性输出统一叫 `invoke`，流式输出统一叫 `stream`。**

#### @tool 装饰器：自动生成 JSON Schema

`@tool` 利用 Python 反射机制，从函数签名中自动提取工具描述：

```python
@tool
def scan_port(host: str, port: int) -> dict:
    """扫描目标主机的指定端口是否开放"""
    ...

# 自动提取：函数名 → name，docstring → description，类型标注 → parameters
```

**tool_map 字典调度模式**：

```python
tools = [scan_port, check_vulnerability]
tool_map = {t.name: t for t in tools}  # O(1) 查找

func = tool_map["scan_port"]
result = func.invoke({"host": "localhost", "port": 80})
```

> `if func_name in TOOL_MAP` 的检查是**防御性编程**：防止模型幻觉返回不存在的函数名导致 `KeyError` 崩溃。

---

## 🧪 实验 3.2：Prompt 核心价值与 LCEL

### 目标
理解 `ChatPromptTemplate` 的核心价值：变量替换和 LCEL 链式组装。

### 为什么需要 PromptTemplate？

```python
# ❌ 手动拼接（容易出错、难维护、无法复用）
prompt = f"你是{role}，请分析{target}的{vuln_type}漏洞"

# ✅ LangChain 模板（变量替换 + 类型安全 + 可复用）
from langchain_core.prompts import ChatPromptTemplate

template = ChatPromptTemplate.from_messages([
    ("system", "你是{role}，精通各类安全技术"),
    ("user", "请分析{target}的{vuln_type}漏洞"),
])

messages = template.invoke({"role": "安全专家", "target": "example.com", "vuln_type": "XSS"})
```

### LCEL 管道组装：Prompt | LLM | Parser

PromptTemplate 的终极价值在于**通过管道操作符 `|` 组装成调用链**：

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

chain = (
    ChatPromptTemplate.from_messages([
        ("system", "你是{role}"),
        ("user", "分析{target}的{vuln_type}漏洞风险"),
    ])
    | ChatOpenAI(model="qwen3.5-plus")
    | StrOutputParser()
)

# 一行调用
result = chain.invoke({"role": "安全专家", "target": "example.com", "vuln_type": "SQL注入"})

# 流式输出同样支持
for chunk in chain.stream({"role": "安全专家", "target": "example.com", "vuln_type": "XSS"}):
    print(chunk, end="", flush=True)
```

**链式组装的价值**：
- 每个组件只负责一件事（单一职责）
- 替换任一环节不影响其他部分（如换模型只改 `ChatOpenAI` → `ChatOllama`）
- 同一个 Chain 可以 `invoke`、`stream`、`batch`，接口完全统一

### 代码示例

完整代码见 `experiments/phase3/exp3_prompt_template.py`，包含 3 个演示：
1. **变量替换**：同一模板不同参数的复用
2. **链式组装**：`invoke` / `stream` / `batch` 三种调用方式
3. **组件替换**：同一 Prompt+Parser，切换不同 LLM 后端

### 运行方式

```bash
# 运行全部演示
python3 experiments/phase3/exp3_prompt_template.py --demo all

# 仅运行链式组装演示
python3 experiments/phase3/exp3_prompt_template.py --demo 2 --backend openai
```

---

## 🧪 实验 3.3：ReAct Agent 实现

### 目标
构建一个能够推理和行动交替进行的 Agent。

### ReAct 模式
```
Thought: 我需要先了解目标的开放端口...
Action: scan_port
Action Input: {"host": "target.com", "port": 80}
Observation: {"open": true}
Thought: 80端口开放，我应该检查Web漏洞...
...
Final Answer: 扫描完成，发现以下安全问题...
```

### 代码示例

创建文件 `experiments/phase3/exp3_2_react_agent.py`：

```python
"""
实验 3.3: ReAct Agent
推理与行动交替进行
支持 Ollama 本地模型和 OpenAI 兼容 API 两种后端
"""
import os
import ollama
import json
import re
from typing import Dict, Callable, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ReActAgent:
    """ReAct 模式 Agent"""
    
    def __init__(self, model: str = "qwen2.5:7b", max_iterations: int = 5, backend: str = "ollama"):
        self.model = model
        self.max_iterations = max_iterations
        self.backend = backend
        self.tools: Dict[str, Callable] = {}
        self.tool_descriptions: List[str] = []

        # OpenAI 后端初始化
        if self.backend == "openai":
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),
            )
    
    def register_tool(self, name: str, func: Callable, description: str):
        """注册工具"""
        self.tools[name] = func
        self.tool_descriptions.append(f"- {name}: {description}")
    
    def _create_prompt(self, task: str, history: str = "") -> str:
        """创建提示词"""
        tools_str = "\n".join(self.tool_descriptions)
        
        return f"""你是一个安全分析助手。你需要通过推理和使用工具来完成任务。

可用工具:
{tools_str}

使用格式:
Thought: [你的思考过程]
Action: [工具名称]
Action Input: [JSON格式的参数]

当你得到结果后，继续思考。如果任务完成，使用:
Thought: [最终总结]
Final Answer: [最终答案]

{history}
任务: {task}

开始:"""
    
    def _parse_response(self, response: str) -> dict:
        """解析响应"""
        result = {
            "thought": "",
            "action": None,
            "action_input": None,
            "final_answer": None
        }
        
        # 提取 Thought
        thought_match = re.search(r"Thought:\s*(.+?)(?=Action:|Final Answer:|$)", response, re.DOTALL)
        if thought_match:
            result["thought"] = thought_match.group(1).strip()
        
        # 提取 Final Answer
        final_match = re.search(r"Final Answer:\s*(.+)", response, re.DOTALL)
        if final_match:
            result["final_answer"] = final_match.group(1).strip()
            return result
        
        # 提取 Action
        action_match = re.search(r"Action:\s*(\w+)", response)
        if action_match:
            result["action"] = action_match.group(1)
        
        # 提取 Action Input
        input_match = re.search(r"Action Input:\s*(\{.+?\})", response, re.DOTALL)
        if input_match:
            try:
                result["action_input"] = json.loads(input_match.group(1))
            except json.JSONDecodeError:
                pass
        
        return result
    
    def run(self, task: str) -> str:
        """运行 Agent"""
        history = ""
        
        for i in range(self.max_iterations):
            print(f"\n--- 迭代 {i+1} ---")
            
            # 生成响应
            prompt = self._create_prompt(task, history)

            if self.backend == "ollama":
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = response["message"]["content"]
            else:
                # OpenAI 兼容 API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = response.choices[0].message.content
            parsed = self._parse_response(response_text)
            
            print(f"Thought: {parsed['thought']}")
            
            # 检查是否结束
            if parsed["final_answer"]:
                print(f"Final Answer: {parsed['final_answer']}")
                return parsed["final_answer"]
            
            # 执行工具
            if parsed["action"] and parsed["action"] in self.tools:
                print(f"Action: {parsed['action']}")
                print(f"Action Input: {parsed['action_input']}")
                
                try:
                    result = self.tools[parsed["action"]](**parsed["action_input"])
                    observation = json.dumps(result, ensure_ascii=False)
                except Exception as e:
                    observation = f"Error: {str(e)}"
                
                print(f"Observation: {observation}")
                
                # 更新历史
                history += f"""
Thought: {parsed['thought']}
Action: {parsed['action']}
Action Input: {json.dumps(parsed['action_input'], ensure_ascii=False)}
Observation: {observation}
"""
            else:
                print("无有效行动，继续思考...")
                history += f"\nThought: {parsed['thought']}\n"
        
        return "达到最大迭代次数，任务未完成。"


# 工具函数
def port_scan(host: str, ports: list) -> dict:
    """端口扫描"""
    import socket
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


def web_fingerprint(url: str) -> dict:
    """Web 指纹识别（模拟）"""
    return {
        "url": url,
        "server": "nginx/1.18.0",
        "technologies": ["PHP", "MySQL"],
        "cms": "unknown"
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ReAct Agent")
    parser.add_argument("--backend", choices=["ollama", "openai"], default="ollama")
    args = parser.parse_args()

    # 根据后端选择模型
    if args.backend == "openai":
        model = os.getenv("OPENAI_MODEL", "qwen3.5-plus")
    else:
        model = "qwen2.5:7b"

    # 创建 Agent
    agent = ReActAgent(model=model, backend=args.backend)
    print(f"后端: {args.backend}，模型: {model}\n")

    # 注册工具
    agent.add_tool(
        "port_scan",
        port_scan,
        "扫描目标主机的端口。参数: host(str), ports(list[int])"
    )
    agent.add_tool(
        "web_fingerprint",
        web_fingerprint,
        "识别Web服务的技术栈。参数: url(str)"
    )
    
    # 运行任务
    task = "分析 localhost 的安全状况，扫描常用端口(80, 443, 22, 3306)并识别Web技术栈"
    result = agent.run(task)
    
    print(f"\n{'='*60}")
    print(f"最终结果: {result}")
```

### 运行方式

```bash
# Ollama 本地模型（默认）
python3 experiments/phase3/exp3_2_react_agent.py

# OpenAI 兼容 API
python3 experiments/phase3/exp3_2_react_agent.py --backend openai
```

> **核心差异**：相比实验 3.1 的 Function Calling（模型通过 `tool_calls` 结构化返回工具调用），ReAct Agent 使用**纯文本提示词**引导模型输出 `Thought/Action/Action Input` 格式，再用正则表达式解析。这是两种完全不同的工具调用范式。

### 验证标准
- [ ] Agent 能够自主规划步骤
- [ ] 正确调用工具并处理结果
- [ ] 根据观察结果调整策略
- [ ] 最终给出完整答案

### 场景 C：LangChain ReAct Agent

> 前面手写了完整的 ReAct 循环（提示词构造 → 响应解析 → 工具执行 → 历史拼接），代码量大且容易出错。LangChain 的 `create_react_agent()` 将这些步骤封装为几行代码，让你专注于工具定义和业务逻辑。

创建文件 `experiments/phase3/exp3_2c_react_agent_langchain.py`：

```python
"""
实验 3.3c: LangChain ReAct Agent
对比手写 ReAct 循环，体验框架的封装价值
"""
import os
import json
import socket
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

load_dotenv()


# ===== 工具定义（与手写版相同的功能，但用 @tool 装饰器更简洁）=====

@tool
def port_scan(host: str, ports: list[int]) -> dict:
    """扫描目标主机的多个端口。参数: host(str)-目标主机, ports(list[int])-端口列表"""
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
    """识别Web服务的技术栈。参数: url(str)-目标URL"""
    return {
        "url": url,
        "server": "nginx/1.18.0",
        "technologies": ["PHP", "MySQL"],
        "cms": "unknown"
    }


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


def run_react_agent(task: str, backend: str = "ollama"):
    """
    用 LangChain 创建 ReAct Agent — 对比手写版本：
    
    手写版: ~100 行（提示词模板 + 正则解析 + 迭代循环 + 历史管理）
    LangChain: ~3 行（create_react_agent + invoke）
    """
    llm = get_llm(backend)
    tools = [port_scan, web_fingerprint]
    
    # 核心：一行创建 ReAct Agent
    agent = create_react_agent(llm, tools)
    
    # 运行（内部自动处理 ReAct 循环：思考 → 工具调用 → 观察 → 继续）
    result = agent.invoke({"messages": [("user", task)]})
    
    # 打印执行过程
    print("\n--- 执行过程 ---")
    for msg in result["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"🔧 调用: {tc['name']}({json.dumps(tc['args'], ensure_ascii=False)})")
        elif msg.type == "tool":
            print(f"📋 结果: {msg.content[:100]}...")
        elif msg.type == "ai" and msg.content:
            print(f"💬 回答: {msg.content[:200]}...")
    
    # 返回最终回答
    final_msg = result["messages"][-1]
    return final_msg.content


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["ollama", "openai"], default="ollama")
    args = parser.parse_args()
    
    print(f"后端: {args.backend}")
    
    task = "分析 localhost 的安全状况，扫描常用端口(80, 443, 22, 3306)并识别Web技术栈"
    print(f"\n任务: {task}")
    
    result = run_react_agent(task, args.backend)
    print(f"\n{'='*60}")
    print(f"最终结果: {result}")
```

#### 手写 ReAct vs LangChain ReAct 对比

| | 手写 ReAct（实验 3.3） | LangChain ReAct（实验 3.3c） |
|---|---|---|
| **代码量** | ~100 行 | ~10 行核心代码 |
| **提示词管理** | 手动构造 Thought/Action/Observation 模板 | 框架内置，自动管理 |
| **响应解析** | 正则匹配 Thought/Action/Final Answer | 框架自动解析 |
| **工具执行** | 手动查找和调用 | 框架自动执行 |
| **迭代控制** | 手动循环 + max_iterations | 框架自动管理 |
| **学习价值** | ⭐⭐⭐ 深入理解 ReAct 原理 | ⭐ 了解最佳实践 |
| **生产可用** | ⭐ 需要大量完善 | ⭐⭐⭐ 开箱即用 |

> **建议**：先完成手写版（3.3），确保理解 ReAct 的每个步骤，再用 LangChain 版（3.3c）体会框架的封装价值。

---

## 🧪 实验 3.4-3.6：MCP Server 开发

### 目标
开发符合 MCP 协议的安全工具服务。

### 📖 核心概念：MCP (Model Context Protocol)

Anthropic 提出的开放协议，用于标准化 AI 模型与外部工具的交互。

```
AI 模型 ←→ MCP Client ←→ MCP Server ←→ 外部工具/数据
```

### MCP 基础结构

```
MCP Server
├── Resources  # 暴露数据资源
├── Tools      # 提供可调用函数
├── Prompts    # 预定义提示词模板
└── Transport  # 通信层 (stdio/HTTP)
```

### 代码示例

创建文件 `experiments/phase3/exp3_4_mcp_server.py`：

```python
"""
实验 3.5: MCP Server - 安全工具集成
将 Nmap 等安全工具封装为 MCP 服务
"""
import asyncio
import json
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# 创建 MCP Server
server = Server("security-tools")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """列出可用工具"""
    return [
        types.Tool(
            name="nmap_scan",
            description="使用 Nmap 扫描目标主机",
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
                        "description": "扫描类型: quick(快速), full(全端口), vuln(漏洞)"
                    }
                },
                "required": ["target"]
            }
        ),
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


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """执行工具"""
    
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
    
    return [types.TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False, indent=2)
    )]


async def run_nmap_scan(target: str, scan_type: str) -> dict:
    """执行 Nmap 扫描"""
    try:
        import nmap
        nm = nmap.PortScanner()
        
        if scan_type == "quick":
            nm.scan(target, arguments="-F -T4")
        elif scan_type == "full":
            nm.scan(target, arguments="-p- -T4")
        elif scan_type == "vuln":
            nm.scan(target, arguments="--script vuln -T4")
        
        results = {
            "target": target,
            "scan_type": scan_type,
            "hosts": []
        }
        
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
    """WHOIS 查询"""
    try:
        import whois
        w = whois.whois(domain)
        return {
            "domain": domain,
            "registrar": w.registrar,
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "name_servers": w.name_servers
        }
    except ImportError:
        return {"error": "python-whois not installed"}
    except Exception as e:
        return {"error": str(e)}


async def run_dns_enum(domain: str, record_types: list) -> dict:
    """DNS 枚举"""
    import socket
    results = {"domain": domain, "records": {}}
    
    for rtype in record_types:
        try:
            if rtype == "A":
                ip = socket.gethostbyname(domain)
                results["records"]["A"] = [ip]
            # 其他记录类型可添加 dnspython 支持
        except Exception as e:
            results["records"][rtype] = [f"Error: {str(e)}"]
    
    return results


async def main():
    """启动 MCP Server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
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
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
```

### MCP 配置

创建 `experiments/phase3/mcp_config.json`：

```json
{
  "mcpServers": {
    "security-tools": {
      "command": "python",
      "args": ["exp3_4_mcp_server.py"],
      "cwd": "d:/Security/AILearningwithAI/experiments/phase3"
    }
  }
}
```

### 验证标准
- [ ] MCP Server 启动无报错
- [ ] 工具列表正确返回
- [ ] 工具调用返回预期结果
- [ ] 与 Claude Desktop 等客户端集成

### 场景 B：MCP 与模型后端的解耦

> MCP 的核心设计是**协议层与模型层完全解耦**。MCP Server 只负责暴露工具，不关心谁来调用它。这意味着无论你用 Ollama 本地模型还是 OpenAI 云端模型驱动的 Agent，都可以使用同一个 MCP Server。

```
              ┌─── Ollama (本地) ──────┐
              │                        │
用户 → Agent ─┤                        ├──→ MCP Server (安全工具)
              │                        │
              └─── OpenAI (API Key) ───┘
                                        ↑
                                  同一个 MCP Server
                                  无需任何修改
```

#### 在 Claude Desktop 中切换模型后端

MCP 配置文件 (`mcp_config.json`) 只定义工具服务，**不涉及模型选择**。模型由 MCP Client 端（如 Claude Desktop、你的 Python 脚本）自行决定：

```python
# 使用 LangChain + MCP 时，模型和工具是独立配置的
from langchain_openai import ChatOpenAI

# 换模型只需改这一行，MCP Server 无需任何变更
llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

# MCP 工具照常使用
# agent = create_react_agent(llm, mcp_tools)
```

> **理解要点**：MCP Server 是"工具提供者"，不是"模型使用者"。你可以开发一个 MCP Server，然后在不同的模型后端间自由切换。

### 场景 C：MCP Client 编程实例

> 前面实验只开发了 MCP Server（暴露工具），但实际使用中还需要 **MCP Client** 来连接 Server、发现工具、调用工具。文档中的架构图 `AI 模型 ←→ MCP Client ←→ MCP Server` 中，Client 端才是真正驱动整个流程的核心。

#### MCP Client 的角色

```
MCP Server（你已经开发好了）     MCP Client（本节要学的）
├── 暴露 Tools                   ├── 连接 Server
├── 暴露 Resources               ├── 发现可用工具
└── 等待被调用                   ├── 调用工具并获取结果
                                 └── 将工具结果交给 LLM 处理
```

在之前的实验中，Client 端是由 Claude Desktop 充当的。但在编程场景下，你需要自己用代码创建 MCP Client。

#### 方式一：原生 MCP SDK 客户端

```python
"""
MCP Client - 使用原生 mcp SDK 连接 MCP Server
"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # 定义要连接的 MCP Server
    server_params = StdioServerParameters(
        command="python",
        args=["exp3_4_mcp_server.py"],
    )

    # 通过 stdio 传输建立连接
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 1. 初始化握手
            await session.initialize()

            # 2. 发现可用工具
            tools = await session.list_tools()
            print("可用工具：")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # 3. 调用工具
            result = await session.call_tool(
                "port_scan",
                arguments={"host": "localhost", "ports": [80, 443]}
            )
            print(f"\n工具返回: {result.content}")

asyncio.run(main())
```

> **理解要点**：`ClientSession` 实现了 MCP 协议的握手（`initialize`）→ 发现（`list_tools`）→ 调用（`call_tool`）完整生命周期。这和 Function Calling 的 5 步流程类似，只是通信走的是 MCP 协议而非直接函数调用。

#### 方式二：LangChain MCP 适配器（推荐）

LangChain 官方提供了 `langchain-mcp-adapters` 库，它是 MCP 与 LangChain 之间的桥梁：

```bash
pip install langchain-mcp-adapters
```

核心组件：

| 组件 | 作用 |
|------|------|
| `MultiServerMCPClient` | 连接一个或多个 MCP Server，管理连接生命周期 |
| `client.get_tools()` | 从 Server 自动发现工具，转为 LangChain Tool 格式 |
| 支持 `stdio` 和 `sse` 两种传输 | 本地进程用 stdio，远程服务用 HTTP/SSE |

```python
"""
MCP Client - 使用 LangChain MCP 适配器
自动将 MCP Server 的工具转为 LangChain Tool，无需手写 @tool 或 JSON Schema
"""
import os
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

load_dotenv()

async def main():
    # 1. 连接 MCP Server（支持同时连多个 Server）
    async with MultiServerMCPClient(
        {
            "security-tools": {
                "command": "python",
                "args": ["exp3_4_mcp_server.py"],
                "transport": "stdio",
            }
        }
    ) as client:
        # 2. 自动发现并加载所有 MCP 工具 → 转为 LangChain Tool
        tools = client.get_tools()
        print(f"已加载 {len(tools)} 个工具: {[t.name for t in tools]}")

        # 3. 用 LangChain Agent 直接使用这些工具
        llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "qwen3.5-plus"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
        agent = create_react_agent(llm, tools)

        result = await agent.ainvoke({
            "messages": [("user", "扫描 localhost 的 80 和 443 端口")]
        })
        print(result["messages"][-1].content)

asyncio.run(main())
```

#### 三种 MCP Client 方式对比

| | Claude Desktop | 原生 mcp SDK | langchain-mcp-adapters |
|---|---|---|---|
| **适用场景** | 交互式使用 | 底层编程控制 | 与 LangChain Agent 集成 |
| **工具发现** | 自动 | `session.list_tools()` | `client.get_tools()` 自动转换 |
| **工具调用** | 自动 | `session.call_tool()` | Agent 自动调度 |
| **多 Server** | 支持 | 需手动管理 | `MultiServerMCPClient` 内置支持 |
| **学习价值** | ⭐ 了解概念 | ⭐⭐⭐ 理解协议 | ⭐⭐ 掌握最佳实践 |

> **核心价值**：`langchain-mcp-adapters` 让你写的 MCP Server 工具**不需要再手动定义 `@tool` 或 JSON Schema**，`get_tools()` 会自动从 Server 发现并转换。这意味着你开发的任何 MCP Server，LangChain Agent 都能直接使用。

---

## 🧪 实验 3.7-3.8：Skill 开发

### 目标
为 AI 编码助手开发自定义 Skill。

### Skill 结构

```
skills/
└── security-audit/
    ├── SKILL.md          # 技能说明
    ├── scripts/
    │   ├── audit.py      # 审计脚本
    │   └── report.py     # 报告生成
    └── examples/
        └── sample.md     # 示例用法
```

### 代码示例

创建文件 `experiments/phase3/skills/security-audit/SKILL.md`：

```markdown
---
name: Security Audit
description: 对代码进行安全审计，识别常见漏洞
---

# Security Audit Skill

## 使用方法

当用户请求代码安全审计时，使用此技能。

## 审计流程

1. 分析代码语言和框架
2. 识别潜在安全问题
3. 生成审计报告

## 可用脚本

- `scripts/audit.py`: 执行静态代码分析
- `scripts/report.py`: 生成审计报告

## 检查项

- [ ] SQL 注入
- [ ] XSS 跨站脚本
- [ ] 命令注入
- [ ] 路径遍历
- [ ] 硬编码凭证
- [ ] 不安全的反序列化
```

创建审计脚本 `experiments/phase3/skills/security-audit/scripts/audit.py`：

```python
"""
安全审计脚本
"""
import re
from pathlib import Path
from typing import List, Dict


class SecurityAuditor:
    """代码安全审计器"""
    
    # 漏洞模式定义
    PATTERNS = {
        "sql_injection": [
            (r'execute\s*\(\s*["\'].*%s', "可能的 SQL 注入 (字符串拼接)"),
            (r'execute\s*\(\s*f["\']', "可能的 SQL 注入 (f-string)"),
            (r'\+\s*["\'].*SELECT|INSERT|UPDATE|DELETE', "SQL 语句拼接"),
        ],
        "xss": [
            (r'innerHTML\s*=', "可能的 XSS (innerHTML)"),
            (r'document\.write\s*\(', "可能的 XSS (document.write)"),
            (r'v-html\s*=', "可能的 XSS (Vue v-html)"),
        ],
        "command_injection": [
            (r'os\.system\s*\(', "可能的命令注入 (os.system)"),
            (r'subprocess\.call\s*\([^,]+shell\s*=\s*True', "危险的 shell=True"),
            (r'eval\s*\(', "危险的 eval 调用"),
            (r'exec\s*\(', "危险的 exec 调用"),
        ],
        "hardcoded_secrets": [
            (r'password\s*=\s*["\'][^"\']+["\']', "硬编码密码"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "硬编码 API Key"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "硬编码密钥"),
        ],
        "path_traversal": [
            (r'open\s*\([^)]*\+', "可能的路径遍历"),
            (r'\.\./', "目录遍历模式"),
        ],
    }
    
    def audit_file(self, file_path: str) -> List[Dict]:
        """审计单个文件"""
        findings = []
        path = Path(file_path)
        
        if not path.exists():
            return [{"error": f"文件不存在: {file_path}"}]
        
        content = path.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")
        
        for vuln_type, patterns in self.PATTERNS.items():
            for pattern, description in patterns:
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        findings.append({
                            "file": file_path,
                            "line": i,
                            "type": vuln_type,
                            "severity": self._get_severity(vuln_type),
                            "description": description,
                            "code": line.strip()[:100]
                        })
        
        return findings
    
    def audit_directory(self, dir_path: str, extensions: List[str] = None) -> List[Dict]:
        """审计目录"""
        if extensions is None:
            extensions = [".py", ".js", ".php", ".java", ".go"]
        
        findings = []
        path = Path(dir_path)
        
        for ext in extensions:
            for file in path.rglob(f"*{ext}"):
                findings.extend(self.audit_file(str(file)))
        
        return findings
    
    def _get_severity(self, vuln_type: str) -> str:
        """获取严重程度"""
        severity_map = {
            "sql_injection": "HIGH",
            "command_injection": "CRITICAL",
            "xss": "MEDIUM",
            "hardcoded_secrets": "HIGH",
            "path_traversal": "MEDIUM",
        }
        return severity_map.get(vuln_type, "LOW")
    
    def generate_report(self, findings: List[Dict]) -> str:
        """生成报告"""
        if not findings:
            return "✅ 未发现安全问题"
        
        report = ["# 安全审计报告\n"]
        report.append(f"**发现问题数**: {len(findings)}\n")
        
        # 按严重程度分组
        by_severity = {}
        for f in findings:
            sev = f["severity"]
            if sev not in by_severity:
                by_severity[sev] = []
            by_severity[sev].append(f)
        
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if sev in by_severity:
                report.append(f"\n## {sev} ({len(by_severity[sev])})\n")
                for f in by_severity[sev]:
                    report.append(f"- **{f['type']}** @ `{f['file']}:{f['line']}`")
                    report.append(f"  - {f['description']}")
                    report.append(f"  - `{f['code']}`\n")
        
        return "\n".join(report)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python audit.py <目录或文件路径>")
        sys.exit(1)
    
    auditor = SecurityAuditor()
    target = sys.argv[1]
    
    path = Path(target)
    if path.is_dir():
        findings = auditor.audit_directory(target)
    else:
        findings = auditor.audit_file(target)
    
    report = auditor.generate_report(findings)
    print(report)
```

---

## 🧪 实验 3.9：Dify 平台部署与基础使用

### 目标
部署 Dify 平台，理解工作流和 Agent 节点的基本用法。

### 📖 核心概念：Dify 工作流平台

开源 LLM 应用编排平台，提供可视化工作流、Agent 节点、多模型集成。

```
用户输入 → [工作流编排器] → LLM节点 → 工具节点 → 条件分支 → 输出
```

核心价值：
- 拖拽式构建复杂 AI 工作流
- 内置 Agent 节点（自主决策 + 工具调用）
- 支持 MCP 工具集成
- 提供 API 服务部署

### 部署验证

```powershell
# 确认 Dify 正在运行
docker compose ps

# 访问 http://localhost 完成初始化设置
# 1. 创建管理员账号
# 2. 配置模型供应商（添加 Ollama: http://host.docker.internal:11434）
```

### 实验步骤

1. **创建对话应用**
   - 新建 "安全顾问" 对话应用
   - 配置 System Prompt 为安全领域专家
   - 接入本地 Ollama 模型测试对话

2. **创建工作流应用**
   - 新建工作流，添加 "开始" → "LLM" → "结束" 节点
   - 在 LLM 节点配置安全分析提示词
   - 发布并通过 API 调用测试

3. **探索 Agent 节点**
   - 在工作流中添加 Agent 节点
   - 配置自定义工具（HTTP 请求）
   - 理解 Agent 节点的自主决策流程

### 验证标准
- [ ] Dify 平台部署成功
- [ ] 对话应用接入本地模型
- [ ] 工作流应用正常运行
- [ ] Agent 节点能调用工具

---

## 🧪 实验 3.10：Dify 可视化编排安全分析工作流

### 目标
使用 Dify 的可视化工作流构建安全分析流水线。

### 工作流设计

```
用户输入(IP/URL)
    ↓
[变量提取] → 提取目标地址和分析类型
    ↓
[条件分支] → 根据类型选择分析路径
   ├─ Web安全 → [LLM分析] → [HTTP工具扫描]
   ├─ 端口扫描 → [代码执行节点]
   └─ 综合分析 → [Agent节点(自主决策)]
    ↓
[结果汇总LLM] → 生成结构化报告
    ↓
输出报告
```

### 实验步骤

1. **创建工作流**
   - 按上述设计创建节点和连线
   - 配置变量传递和条件判断
  
2. **集成 MCP 工具**
   - 将之前开发的 MCP Security Tools 接入 Dify
   - 在 Agent 节点中配置工具列表

3. **API 部署**
   - 发布工作流为 API 服务
   - 编写 Python 脚本调用 Dify API

创建文件 `experiments/phase3/exp3_9_dify_api_call.py`：

```python
"""
实验 3.10: 调用 Dify 工作流 API
"""
import requests
import json

DIFY_API_URL = "http://localhost/v1/workflows/run"
DIFY_API_KEY = "your-api-key-here"  # 从 Dify 控制台获取


def run_security_workflow(target: str, analysis_type: str = "comprehensive"):
    """调用 Dify 安全分析工作流"""
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": {
            "target": target,
            "analysis_type": analysis_type
        },
        "response_mode": "blocking",
        "user": "security-engineer"
    }
    
    response = requests.post(DIFY_API_URL, headers=headers, json=payload)
    result = response.json()
    
    if result.get("data", {}).get("outputs"):
        return result["data"]["outputs"]
    return result


if __name__ == "__main__":
    # 测试工作流
    result = run_security_workflow("example.com", "web_security")
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

### 验证标准
- [ ] 工作流节点连线正确
- [ ] 条件分支根据输入正确路由
- [ ] MCP 工具在 Dify 中正常调用
- [ ] API 调用返回预期结果

---

## 🧪 实验 3.11：A2A 协议与 Agent Card

### 目标
理解 A2A 协议原理，实现 Agent Card 能力发现机制。

### 📖 核心概念：A2A (Agent-to-Agent) 协议

Google 提出的开放协议，用于实现 AI Agent 之间的通信与协作。

```
Agent A (扫描) ←→ A2A 协议 (JSON-RPC 2.0) ←→ Agent B (分析)
                          │
                    Agent Card (能力发现)
```

核心机制：
- **Agent Card**：JSON 格式的能力声明，用于 Agent 间相互发现
- **任务管理**：创建、查询、取消任务的标准流程
- **传输层**：基于 HTTP(S)，支持 SSE/WebSocket 流式传输

| 协议 | 定位 | 解决的问题 |
|------|------|------------|
| MCP | 垂直集成 | Agent 如何调用外部工具 |
| A2A | 水平协作 | Agent 之间如何通信协作 |

### A2A 核心流程

```
1. Agent B 发布 Agent Card（声明能力）
2. Agent A 发现并读取 Agent Card
3. Agent A 通过 A2A 协议向 Agent B 发送任务
4. Agent B 执行任务并返回结果
5. Agent A 整合结果继续工作
```

### 代码示例

创建文件 `experiments/phase3/exp3_10_agent_card.py`：

```python
"""
实验 3.11: A2A Agent Card 定义与发现
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading


# ===== Agent Card 定义 =====

SCANNER_AGENT_CARD = {
    "name": "Security Scanner Agent",
    "description": "执行网络安全扫描任务，包括端口扫描、服务识别",
    "url": "http://localhost:8001",
    "version": "1.0.0",
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
    },
    "skills": [
        {
            "id": "port_scan",
            "name": "端口扫描",
            "description": "扫描目标主机的开放端口",
            "inputModes": ["text"],
            "outputModes": ["text"]
        },
        {
            "id": "service_detect",
            "name": "服务识别",
            "description": "识别开放端口上运行的服务",
            "inputModes": ["text"],
            "outputModes": ["text"]
        }
    ]
}

ANALYZER_AGENT_CARD = {
    "name": "Security Analyzer Agent",
    "description": "分析安全扫描结果，评估风险等级，生成报告",
    "url": "http://localhost:8002",
    "version": "1.0.0",
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
    },
    "skills": [
        {
            "id": "risk_analysis",
            "name": "风险分析",
            "description": "分析扫描结果的安全风险",
            "inputModes": ["text"],
            "outputModes": ["text"]
        },
        {
            "id": "report_generation",
            "name": "报告生成",
            "description": "生成结构化安全报告",
            "inputModes": ["text"],
            "outputModes": ["text"]
        }
    ]
}


# ===== Agent Card 服务 =====

class AgentCardHandler(BaseHTTPRequestHandler):
    """提供 Agent Card 的 HTTP 服务"""
    
    agent_card = None
    
    def do_GET(self):
        if self.path == "/.well-known/agent.json":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(self.agent_card, ensure_ascii=False).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # 静默日志


def discover_agent(agent_url: str) -> dict:
    """发现 Agent — 获取 Agent Card"""
    import requests
    response = requests.get(f"{agent_url}/.well-known/agent.json")
    if response.status_code == 200:
        card = response.json()
        print(f"✅ 发现 Agent: {card['name']}")
        print(f"   描述: {card['description']}")
        print(f"   技能: {[s['name'] for s in card['skills']]}")
        return card
    return None


if __name__ == "__main__":
    # 启动 Scanner Agent Card 服务
    class ScannerHandler(AgentCardHandler):
        agent_card = SCANNER_AGENT_CARD
    
    server = HTTPServer(("localhost", 8001), ScannerHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print("Scanner Agent Card 服务已启动 (port 8001)")
    
    # 发现 Agent
    print("\n=== Agent 发现 ===")
    card = discover_agent("http://localhost:8001")
    
    if card:
        print(f"\n已发现 {len(card['skills'])} 个技能:")
        for skill in card["skills"]:
            print(f"  - {skill['id']}: {skill['description']}")
    
    server.shutdown()
```

### 验证标准
- [ ] 理解 Agent Card 的结构和用途
- [ ] Agent Card 服务正常响应
- [ ] 能通过 well-known URL 发现 Agent
- [ ] 理解 MCP 与 A2A 的互补关系

---

## 🧪 实验 3.12：多 Agent 协作（A2A 实践）

### 目标
基于 A2A 协议实现扫描 Agent 和分析 Agent 的协作。

### 架构设计

```
[协调器 Agent]
    ├─ 发现 Agent（读取 Agent Card）
    ├─ 发送扫描任务 → [Scanner Agent] → 返回扫描结果
    ├─ 发送分析任务 → [Analyzer Agent] → 返回分析报告
    └─ 汇总结果 → 最终安全报告
```

### 代码示例

创建文件 `experiments/phase3/exp3_11_multi_agent.py`：

```python
"""
实验 3.12: A2A 多 Agent 协作
扫描Agent + 分析Agent 协作完成安全评估
"""
import json
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import requests
import socket


# ===== Scanner Agent =====

class ScannerAgent:
    """安全扫描 Agent"""
    
    AGENT_CARD = {
        "name": "Scanner Agent",
        "url": "http://localhost:8001",
        "skills": [{"id": "port_scan", "name": "端口扫描"}]
    }
    
    @staticmethod
    def handle_task(task_input: str) -> dict:
        """处理扫描任务"""
        # 解析目标
        target = task_input.strip()
        
        # 执行端口扫描
        open_ports = []
        for port in [22, 80, 443, 3306, 8080, 8443]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                if sock.connect_ex((target, port)) == 0:
                    open_ports.append(port)
                sock.close()
            except:
                pass
        
        return {
            "target": target,
            "open_ports": open_ports,
            "status": "completed"
        }


# ===== Analyzer Agent =====

class AnalyzerAgent:
    """安全分析 Agent"""
    
    AGENT_CARD = {
        "name": "Analyzer Agent",
        "url": "http://localhost:8002",
        "skills": [{"id": "risk_analysis", "name": "风险分析"}]
    }
    
    @staticmethod
    def handle_task(task_input: str) -> dict:
        """分析扫描结果"""
        scan_data = json.loads(task_input)
        
        # 基于端口的风险评估
        risks = []
        risk_rules = {
            22: ("SSH", "MEDIUM", "确保使用密钥认证，禁用密码登录"),
            80: ("HTTP", "LOW", "建议启用 HTTPS 重定向"),
            443: ("HTTPS", "INFO", "检查 SSL/TLS 证书有效性"),
            3306: ("MySQL", "HIGH", "数据库端口不应暴露在公网"),
            8080: ("HTTP-Alt", "MEDIUM", "检查是否为管理后台"),
            8443: ("HTTPS-Alt", "MEDIUM", "检查服务用途"),
        }
        
        for port in scan_data.get("open_ports", []):
            if port in risk_rules:
                service, severity, advice = risk_rules[port]
                risks.append({
                    "port": port,
                    "service": service,
                    "severity": severity,
                    "advice": advice
                })
        
        return {
            "target": scan_data["target"],
            "total_risks": len(risks),
            "risks": risks,
            "overall_risk": "HIGH" if any(r["severity"] == "HIGH" for r in risks) else "MEDIUM"
        }


# ===== A2A 协调器 =====

class Orchestrator:
    """多 Agent 协调器"""
    
    def __init__(self):
        self.agents = {}
    
    def discover_agents(self, agent_urls: list):
        """发现并注册 Agent"""
        for url in agent_urls:
            try:
                resp = requests.get(f"{url}/.well-known/agent.json", timeout=2)
                if resp.status_code == 200:
                    card = resp.json()
                    self.agents[card["name"]] = {
                        "card": card,
                        "url": url
                    }
                    print(f"✅ 发现: {card['name']}")
            except:
                print(f"❌ 无法连接: {url}")
    
    def send_task(self, agent_name: str, task_input: str) -> dict:
        """向 Agent 发送任务"""
        if agent_name not in self.agents:
            return {"error": f"Agent not found: {agent_name}"}
        
        agent_url = self.agents[agent_name]["url"]
        
        task = {
            "jsonrpc": "2.0",
            "method": "tasks/send",
            "params": {
                "id": str(uuid.uuid4()),
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": task_input}]
                }
            }
        }
        
        try:
            resp = requests.post(f"{agent_url}/a2a", json=task, timeout=30)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
    
    def run_security_assessment(self, target: str):
        """执行完整的安全评估流程"""
        print(f"\n{'='*60}")
        print(f"🔍 开始安全评估: {target}")
        print(f"{'='*60}")
        
        # Step 1: 扫描
        print("\n[1/3] 调用 Scanner Agent...")
        scan_result = ScannerAgent.handle_task(target)
        print(f"  扫描完成: 发现 {len(scan_result['open_ports'])} 个开放端口")
        
        # Step 2: 分析
        print("\n[2/3] 调用 Analyzer Agent...")
        analysis = AnalyzerAgent.handle_task(json.dumps(scan_result))
        print(f"  分析完成: 整体风险等级 {analysis['overall_risk']}")
        
        # Step 3: 生成报告
        print("\n[3/3] 生成安全报告...")
        report = self._generate_report(scan_result, analysis)
        print(report)
        
        return report
    
    def _generate_report(self, scan_result: dict, analysis: dict) -> str:
        """生成综合报告"""
        report = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 安全评估报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
目标: {scan_result['target']}
整体风险: {analysis['overall_risk']}
开放端口: {scan_result['open_ports']}

风险详情:
"""
        for risk in analysis["risks"]:
            icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢", "INFO": "🔵"}
            report += f"  {icon.get(risk['severity'], '⚪')} Port {risk['port']} ({risk['service']}) "
            report += f"[{risk['severity']}]\n"
            report += f"    建议: {risk['advice']}\n"
        
        return report


if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run_security_assessment("localhost")
```

### 验证标准
- [ ] 多 Agent 协作流程正确执行
- [ ] 扫描结果正确传递给分析 Agent
- [ ] 风险评估逻辑合理
- [ ] 最终报告包含所有 Agent 的分析结果

---

## 🧪 实验 3.13-3.14：综合项目

### 目标
构建完整的自动化安全测试 Agent。

### 项目：自动化渗透测试 Agent

创建文件 `experiments/phase3/exp3_12_pentest_agent.py`：

```python
"""
实验 3.13: 自动化渗透测试 Agent
整合多个安全工具进行自动化测试
"""
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator


class PentestState(TypedDict):
    """渗透测试状态"""
    target: str
    phase: str
    findings: Annotated[List[dict], operator.add]
    report: str


class PentestAgent:
    """渗透测试 Agent"""
    
    def __init__(self):
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建工作流图"""
        workflow = StateGraph(PentestState)
        
        # 添加节点
        workflow.add_node("recon", self.reconnaissance)
        workflow.add_node("scan", self.vulnerability_scan)
        workflow.add_node("analyze", self.analyze_results)
        workflow.add_node("report", self.generate_report)
        
        # 定义边
        workflow.set_entry_point("recon")
        workflow.add_edge("recon", "scan")
        workflow.add_edge("scan", "analyze")
        workflow.add_edge("analyze", "report")
        workflow.add_edge("report", END)
        
        return workflow.compile()
    
    def reconnaissance(self, state: PentestState) -> dict:
        """信息收集阶段"""
        print(f"[*] 信息收集: {state['target']}")
        # 实现端口扫描、服务识别等
        findings = [
            {"type": "open_port", "data": {"port": 80, "service": "http"}},
            {"type": "open_port", "data": {"port": 443, "service": "https"}},
        ]
        return {"phase": "recon_complete", "findings": findings}
    
    def vulnerability_scan(self, state: PentestState) -> dict:
        """漏洞扫描阶段"""
        print("[*] 漏洞扫描中...")
        # 实现漏洞扫描逻辑
        findings = [
            {"type": "vulnerability", "data": {"name": "Outdated SSL", "severity": "MEDIUM"}}
        ]
        return {"phase": "scan_complete", "findings": findings}
    
    def analyze_results(self, state: PentestState) -> dict:
        """结果分析"""
        print("[*] 分析结果...")
        return {"phase": "analysis_complete"}
    
    def generate_report(self, state: PentestState) -> dict:
        """生成报告"""
        print("[*] 生成报告...")
        report = f"""
# 渗透测试报告

## 目标: {state['target']}

## 发现
"""
        for f in state['findings']:
            report += f"- {f['type']}: {f['data']}\n"
        
        return {"report": report, "phase": "complete"}
    
    def run(self, target: str) -> str:
        """执行渗透测试"""
        initial_state = {
            "target": target,
            "phase": "init",
            "findings": [],
            "report": ""
        }
        
        result = self.graph.invoke(initial_state)
        return result["report"]


if __name__ == "__main__":
    agent = PentestAgent()
    report = agent.run("example.com")
    print(report)
```

---

### 场景 B+C：LangGraph + API Key 综合安全工作流

> 前面的 LangGraph 渗透测试 Agent 使用了硬编码的逻辑。在生产环境中，更常见的组合是 **云端模型（API Key）+ LangGraph 工作流 + LangChain 工具集成**。以下示例展示如何将三者结合。

```python
"""
实验 3.13 扩展: LangGraph + API Key 综合安全工作流
生产环境中的典型组合：云端模型 + LangGraph 状态机 + LangChain 工具
"""
import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()


class SecurityState(TypedDict):
    """安全评估状态"""
    target: str
    phase: str
    recon_result: str
    analysis_result: str
    report: str


def get_llm(backend: str = "openai"):
    """获取 LLM — 生产环境推荐使用 API Key 模式"""
    if backend == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    return ChatOllama(model="qwen2.5:7b")


def recon_node(state: SecurityState) -> dict:
    """信息收集节点 — 用 LLM 生成侦查计划"""
    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content="你是安全测试专家，请对目标进行信息收集分析。"),
        HumanMessage(content=f"目标: {state['target']}，请列出关键信息点。"),
    ])
    return {"recon_result": response.content, "phase": "recon_done"}


def analysis_node(state: SecurityState) -> dict:
    """分析节点 — 基于侦查结果进行风险分析"""
    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content="你是安全分析专家，请基于侦查结果分析潜在风险。"),
        HumanMessage(content=f"目标: {state['target']}\n侦查结果:\n{state['recon_result']}"),
    ])
    return {"analysis_result": response.content, "phase": "analysis_done"}


def report_node(state: SecurityState) -> dict:
    """报告节点 — 生成结构化报告"""
    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content="请生成简洁的安全评估报告，包含发现和建议。"),
        HumanMessage(content=f"目标: {state['target']}\n分析:\n{state['analysis_result']}"),
    ])
    return {"report": response.content, "phase": "complete"}


# 构建工作流
workflow = StateGraph(SecurityState)
workflow.add_node("recon", recon_node)
workflow.add_node("analysis", analysis_node)
workflow.add_node("report", report_node)

workflow.set_entry_point("recon")
workflow.add_edge("recon", "analysis")
workflow.add_edge("analysis", "report")
workflow.add_edge("report", END)

app = workflow.compile()


if __name__ == "__main__":
    result = app.invoke({
        "target": "example.com",
        "phase": "init",
        "recon_result": "",
        "analysis_result": "",
        "report": "",
    })
    
    print("\n" + "="*60)
    print("📋 安全评估报告")
    print("="*60)
    print(result["report"])
```

#### 教学总结：何时选择哪种组合

| 场景 | 推荐组合 | 理由 |
|------|----------|------|
| **学习/调试** | Ollama + 原生 Python | 免费、可离线、理解底层原理 |
| **快速原型** | API Key + LangChain | 模型效果好、开发速度快 |
| **复杂工作流** | API Key + LangGraph | 状态管理清晰、流程可控 |
| **工具集成** | 任意模型 + MCP Server | 工具与模型解耦、可复用 |
| **生产部署** | API Key + LangGraph + MCP | 完整技术栈、可维护性好 |

---

---

## 📋 工具调用模式总结

> 完成以上所有实验后，回顾四种工具调用模式的全景对比。

### 四种模式全景对比

| | Function Calling | MCP | Shell Tool | Skill |
|---|---|---|---|---|
| **是什么** | API 协议特性 | 工具服务协议 | 通用 CLI 执行 | IDE 插件指令集 |
| **模型的认知来源** | JSON Schema（显式） | Server 自动发现 | 训练数据 + Prompt | SKILL.md 指令 |
| **新增工具成本** | 写代码封装 | 写 MCP Server | 零（CLI 已存在） | 写文档 |
| **调用确定性** | ⭐⭐⭐ 强 | ⭐⭐⭐ 强 | ⭐⭐ 弱 | ⭐⭐ 中 |
| **安全性** | ⭐⭐⭐ 受控 | ⭐⭐⭐ 受控 | ⭐ 高风险 | ⭐⭐ 中 |
| **适用场景** | 生产环境 | 工具服务化 | 开发探索 | 冷门工具补充 |
| **典型产品** | OpenAI API | Claude Desktop | Cursor/Antigravity | Gemini CLI |

### Shell Tool 模式：把操作系统变成工具箱

当前流行的一种工程方法是**不封装**，直接让 Agent 执行 CLI 命令：

```python
@tool
def run_shell(command: str) -> str:
    """在 shell 中执行命令并返回输出"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout[:4000]

# Agent 收到 "扫描 example.com" → 自主决定执行 nmap -sV example.com
```

**模型如何知道 CLI 工具的用法？** 靠两件事：

1. **预训练知识**：大模型训练时读过 man pages、Stack Overflow、GitHub 脚本，天生知道 `nmap`、`curl`、`dig` 怎么用
2. **System Prompt 引导**：通过提示词告知可用工具列表和使用示例

### Skill + Shell 组合：解决冷门工具问题

对于模型训练数据中覆盖不足的 CLI 工具（如 `nuclei`、`subfinder`、`httpx` 等），可以通过 **Skill 的方式将使用说明注入给模型**：

```markdown
# SKILL.md — 给 Agent 的 nuclei 使用指南
可用命令：
- nuclei -u <url> -t cves/     # 扫描已知 CVE
- nuclei -l urls.txt -t xss/   # 批量 XSS 检测
- nuclei -u <url> -severity critical  # 只报高危
```

Agent 在执行前读取 SKILL.md，就像工程师翻阅工具手册一样，弥补了预训练知识的空白。

### 实践建议

- **核心工具**：用 Function Calling / MCP 封装（确定性强，参数可控）
- **长尾 CLI 工具**：用 Shell Tool + Skill 补充（灵活但需人工确认）
- **安全红线**：Shell Tool 必须配合命令白名单、沙箱执行或人工审批

---

## ✅ 阶段检查清单

| 检查项 | 状态 |
|--------|------|
| Function Calling 实现成功（Ollama） | ⬜ |
| Function Calling - API Key 模式 | ⬜ |
| Function Calling - LangChain 统一接口 | ⬜ |
| ReAct Agent 正常运行（手写版） | ⬜ |
| ReAct Agent - LangChain 版 | ⬜ |
| 理解 MCP 协议及与模型后端的解耦 | ⬜ |
| MCP Server 开发完成 | ⬜ |
| Skill 开发完成 | ⬜ |
| Dify 平台部署与基础使用 | ⬜ |
| Dify 安全分析工作流编排 | ⬜ |
| A2A Agent Card 发现机制 | ⬜ |
| 多 Agent 协作实践 | ⬜ |
| LangGraph + API Key 综合工作流 | ⬜ |
| 渗透测试 Agent 完成 | ⬜ |

---

## 🎉 学习完成

恭喜完成全部三个阶段的学习！

### 下一步建议

1. **深入实践**：在真实项目中应用所学
2. **持续学习**：关注 AI 领域最新发展
3. **开源贡献**：参与开源 Agent 项目
4. **知识分享**：撰写博客或教程

### 推荐进阶方向

- **多模态 Agent**：结合视觉能力的 Agent
- **Agent 评估**：Agent 能力评估框架
- **生产部署**：Agent 系统的可靠性和安全性
- **自主 Agent**：更高自主性的 AI 系统
