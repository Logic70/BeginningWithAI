# 阶段一：基础认知与环境搭建

> 预计时间：1-2 周 | 核心问题：如何在本地运行一个开源大语言模型？

---

## 🎯 阶段目标

完成本阶段后，你将能够：
- ✅ 在本地安装和运行开源 LLM
- ✅ 使用 Python 调用本地模型 API
- ✅ 理解 Transformer 架构的基本原理
- ✅ 构建一个简单的命令行对话程序

---

## 📦 环境搭建

### 安装 Ollama

Ollama 是本地运行 LLM 最简单的方式。

**Windows 安装：**
1. 访问 [ollama.com](https://ollama.com/)
2. 下载 Windows 安装包
3. 运行安装程序

**验证安装：**
```powershell
ollama --version
```

### 下载首个模型

```powershell
# 下载 Qwen2.5 7B（推荐，中文效果好）
ollama pull qwen2.5:7b

# 或下载 Llama 3.2（英文效果好）
ollama pull llama3.2:latest
```

### Python 环境

```powershell
# 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 安装依赖
pip install ollama openai requests

# API Key 模式依赖（OpenAI 兼容格式）
pip install openai python-dotenv

# LangChain 依赖（对比学习用）
pip install langchain langchain-openai langchain-ollama
```

### API Key 配置（可选）

如果你希望使用云端模型（如 OpenAI、DeepSeek、智谱等 OpenAI 兼容平台），需要配置 API Key：

在项目根目录创建 `.env` 文件：
```
# .env（⚠️ 请确认项目根目录的 .gitignore 中包含 .env，避免 API Key 泄露）
OPENAI_API_KEY=sk-xxx                          # 你的 API Key
OPENAI_BASE_URL=https://api.openai.com/v1      # 可替换为其他平台 URL
OPENAI_MODEL=gpt-4o-mini                       # 云端模型名称
```

常见平台的 `OPENAI_BASE_URL`：
| 平台 | Base URL |
|------|----------|
| OpenAI | `https://api.openai.com/v1` |
| DeepSeek | `https://api.deepseek.com` |
| 智谱 AI | `https://open.bigmodel.cn/api/paas/v4` |
| 硅基流动 | `https://api.siliconflow.cn/v1` |

> **提示**：本教程的所有实验都提供 **Ollama 本地模式**（免费、离线）和 **API Key 云端模式**（需付费、效果更好）两种运行方式。初学者可以先用 Ollama 模式，有 API Key 后再尝试云端模式。

### ⚠️ 常见问题排查

#### 1. PowerShell 激活虚拟环境报错：禁止运行脚本

**报错信息**：
```
无法加载文件 ...\Activate.ps1，因为在此系统上禁止运行脚本
```

**原因**：Windows PowerShell 默认执行策略为 `Restricted`，禁止运行 `.ps1` 脚本。

**解决方法**：
```powershell
# 方法1：仅对当前用户永久生效（推荐）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 方法2：仅对当前会话生效（关闭终端后失效）
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

---

#### 2. 安装 Ollama 后命令仍未找到

**报错信息**：
```
ollama : 无法将"ollama"项识别为 cmdlet、函数、脚本文件或可运行程序的名称
```

**原因**：安装 Ollama 后，已打开的终端 PATH 环境变量未自动刷新。

**解决方法**：
```powershell
# 方法1：关闭终端后重新打开一个新终端

# 方法2：在当前终端手动刷新 PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

---

#### 3. ollama pull 报错 "file does not exist"

**报错信息**：
```
pulling manifest
Error: pull model manifest: file does not exist
```

**原因**：模型名称或标签不正确，Ollama 仓库中不存在该版本。

**解决方法**：
```powershell
# 确认模型名称正确，访问 https://ollama.com/library 查看可用模型
# 示例：拉取 Qwen2.5 7B
ollama pull qwen2.5:7b

# 不确定时，先搜索可用标签
ollama list   # 查看已下载的模型
```

---

## 🧪 实验 1.1：本地运行模型

### 目标
验证 Ollama 安装正确，能够本地对话。

### 步骤

1. **启动 Ollama 服务**（Windows 安装后自动启动）

2. **命令行对话测试**
```powershell
ollama run qwen2.5:7b
```

3. **测试提示词**
```
>>> 你是一个网络安全专家，请解释什么是 SQL 注入？
```

### 验证标准
- [ ] 模型能正常加载
- [ ] 能够进行多轮对话
- [ ] 响应时间在可接受范围内（< 30秒首字）

### 记录
> 在此记录你的测试结果和遇到的问题

---

## 🧪 实验 1.2：Python API 调用

### 目标
使用 Python 代码调用本地 Ollama 模型。

### 📘 API 参考：`ollama.chat()`

在进入代码之前，先了解核心 API 的入参和返回值结构。

#### 入参

```python
response = ollama.chat(
    model="qwen2.5:7b",      # 必填，模型名称
    messages=[...],           # 必填，对话消息列表
    stream=False,             # 可选，是否流式输出（默认 False）
    options={"temperature": 0.7},  # 可选，推理参数
    format="json",            # 可选，指定输出格式
    keep_alive="5m"           # 可选，模型保持加载的时长
)
```

##### `messages` 消息列表

`messages` 是一个字典列表，每条消息包含 `role` 和 `content` 两个字段：

| 角色 | 含义 | 示例 |
|------|------|------|
| `system` | 系统提示词，定义模型的行为和人设 | `"你是一个安全专家"` |
| `user` | 用户的输入 | `"什么是 SQL 注入？"` |
| `assistant` | 模型的历史回复（用于多轮对话） | `"SQL 注入是指..."` |

```python
messages = [
    {"role": "system", "content": "你是一个安全助手"},   # 可选
    {"role": "user", "content": "什么是 XSS？"},
    {"role": "assistant", "content": "XSS 是跨站脚本..."},  # 历史回复
    {"role": "user", "content": "如何防御？"}             # 最新问题
]
```

> **多轮对话的本质**：模型本身没有记忆，每次调用都是独立的。"记住上下文"是通过将历史对话全部放入 `messages` 列表一起发给模型来实现的。

#### 返回值

返回值类型取决于 `stream` 参数：

##### 非流式（`stream=False`，默认）→ `ChatResponse` 对象

```python
response = ollama.chat(model="qwen2.5:7b", messages=[...])

# ChatResponse 结构（同时支持属性访问和字典访问）：
# response.message.role       → "assistant"
# response.message.content    → "SQL 注入是指..."
# response.model              → "qwen2.5:7b"
# response.done               → True
# response.total_duration     → 1234567890  (纳秒)
# response.eval_count         → 42  (生成的 token 数)

# 两种等效的访问方式：
text = response.message.content      # 属性访问
text = response["message"]["content"] # 字典访问（也可以）
```

##### 流式（`stream=True`）→ 迭代器，每个 chunk 是 `dict`

```python
stream = ollama.chat(model="qwen2.5:7b", messages=[...], stream=True)

for chunk in stream:
    # 每个 chunk 是普通字典：
    # chunk["message"]["content"]  → 文本片段（通常 1-2 个字）
    # chunk["done"]               → 是否为最后一个 chunk
    print(chunk["message"]["content"], end="")
```

##### 对比总结

| | 非流式 `stream=False` | 流式 `stream=True` |
|---|---|---|
| **返回类型** | `ChatResponse` 对象 | 迭代器（每个 chunk 是 `dict`） |
| **输出时机** | 等全部生成完一次性返回 | 边生成边返回 |
| **访问内容** | `response.message.content` 或 `response["message"]["content"]` | `chunk["message"]["content"]` |
| **适用场景** | 需要完整结果再处理 | 实时展示、用户体验更好 |

### 代码示例

创建文件 `experiments/phase1/exp1_2_api_call.py`：


```python
"""
实验 1.2: Python 调用 Ollama API
"""
import ollama

def simple_chat(prompt: str, model: str = "qwen2.5:7b") -> str:
    """
    简单对话函数
    
    Args:
        prompt: 用户输入
        model: 模型名称
    
    Returns:
        模型响应文本
    """
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response["message"]["content"]


def stream_chat(prompt: str, model: str = "qwen2.5:7b"):
    """
    流式对话函数（实时输出）
    """
    stream = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    for chunk in stream:
        print(chunk["message"]["content"], end="", flush=True)
    print()


if __name__ == "__main__":
    # 测试简单对话
    print("=== 简单对话测试 ===")
    response = simple_chat("什么是缓冲区溢出？请简要说明。")
    print(response)
    
    print("\n=== 流式对话测试 ===")
    stream_chat("请列出常见的 Web 安全漏洞类型。")
```

### 运行测试
```powershell
cd experiments/phase1
python exp1_2_api_call.py
```

### 验证标准
- [ ] 成功导入 ollama 库
- [ ] simple_chat 函数返回正确响应
- [ ] stream_chat 函数实现流式输出

### 场景 B：API Key 模式（OpenAI 兼容格式）

> 学完 Ollama 原生调用后，接下来用 OpenAI SDK 调用云端模型。你会发现两者的核心概念（`messages`、`role`、流式输出）完全一致，只是初始化方式和返回值格式略有不同。

创建文件 `experiments/phase1/exp1_2b_api_key_call.py`：

```python
"""
实验 1.2b: API Key 模式 - OpenAI 兼容格式调用
对比 Ollama 原生调用，理解 API 差异
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 配置
load_dotenv()

# 初始化客户端（支持任何 OpenAI 兼容平台）
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
)
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def simple_chat(prompt: str) -> str:
    """
    简单对话 — 对比 Ollama 版本的差异：
    
    Ollama:  ollama.chat(model=..., messages=[...])
    OpenAI:  client.chat.completions.create(model=..., messages=[...])
    
    返回值：
    Ollama:  response.message.content  或  response["message"]["content"]
    OpenAI:  response.choices[0].message.content
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def stream_chat(prompt: str):
    """
    流式对话 — 对比 Ollama 版本的差异：
    
    Ollama:  stream=True → chunk["message"]["content"]
    OpenAI:  stream=True → chunk.choices[0].delta.content
    """
    stream = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:  # OpenAI 的 chunk 可能为 None
            print(content, end="", flush=True)
    print()


if __name__ == "__main__":
    print(f"使用模型: {MODEL}")
    print(f"API 地址: {client.base_url}\n")
    
    print("=== 简单对话测试 ===")
    response = simple_chat("什么是缓冲区溢出？请简要说明。")
    print(response)
    
    print("\n=== 流式对话测试 ===")
    stream_chat("请列出常见的 Web 安全漏洞类型。")
```

#### Ollama vs OpenAI 关键差异对比

| | Ollama SDK | OpenAI SDK |
|---|---|---|
| **初始化** | 无需初始化，直接 `import ollama` | 需创建 `OpenAI(api_key=..., base_url=...)` 客户端 |
| **调用方式** | `ollama.chat(model, messages)` | `client.chat.completions.create(model, messages)` |
| **返回值** | `response.message.content` | `response.choices[0].message.content` |
| **流式 chunk** | `chunk["message"]["content"]`（总是有值） | `chunk.choices[0].delta.content`（可能为 `None`） |
| **认证** | 无需（本地运行） | 需要 API Key |
| **费用** | 免费 | 按 Token 计费 |

### 场景 C：LangChain 统一接口

> 前面分别用了 Ollama SDK 和 OpenAI SDK，两套 API 风格不同。LangChain 提供统一抽象层，让你用**相同的代码**切换不同的模型后端。这就是框架的价值：屏蔽底层差异，专注业务逻辑。

创建文件 `experiments/phase1/exp1_2c_langchain_call.py`：

```python
"""
实验 1.2c: LangChain 统一接口
用相同的代码调用 Ollama 和 OpenAI，理解框架的抽象价值
"""
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()


def get_llm(backend: str = "ollama"):
    """
    获取 LLM 实例 — 不同后端，相同接口
    
    这就是 LangChain 的核心价值：无论用哪个模型，
    后续的 invoke()、stream() 调用方式完全一致。
    """
    if backend == "ollama":
        return ChatOllama(model="qwen2.5:7b")
    elif backend == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    else:
        raise ValueError(f"未知后端: {backend}")


def simple_chat(llm, prompt: str) -> str:
    """
    统一的对话接口 — 无论 llm 是 Ollama 还是 OpenAI，代码完全一样
    
    对比之前：
    - Ollama:  ollama.chat(model=..., messages=[...])  → response.message.content
    - OpenAI:  client.chat.completions.create(...)     → response.choices[0].message.content
    - LangChain: llm.invoke([...])                     → response.content  ✨ 统一！
    """
    messages = [
        SystemMessage(content="你是一个安全专家"),
        HumanMessage(content=prompt),
    ]
    response = llm.invoke(messages)
    return response.content


def stream_chat(llm, prompt: str):
    """
    统一的流式输出 — 同样与后端无关
    """
    messages = [HumanMessage(content=prompt)]
    for chunk in llm.stream(messages):
        print(chunk.content, end="", flush=True)
    print()


if __name__ == "__main__":
    # 测试两种后端
    for backend in ["ollama", "openai"]:
        print(f"\n{'='*60}")
        print(f"  后端: {backend}")
        print(f"{'='*60}")
        
        try:
            llm = get_llm(backend)
            
            print("\n--- 简单对话 ---")
            response = simple_chat(llm, "什么是 XSS？一句话回答。")
            print(response)
            
            print("\n--- 流式对话 ---")
            stream_chat(llm, "列出 3 种常见的注入攻击。")
        except Exception as e:
            print(f"  ⚠️ {backend} 不可用: {e}")
            print(f"  提示: 请检查 {'Ollama 是否启动' if backend == 'ollama' else '.env 中的 API Key 配置'}")
```

#### 三种模式总结

| | 原生 Ollama | 原生 OpenAI | LangChain |
|---|---|---|---|
| **学习价值** | 理解底层 API | 理解云端调用 | 掌握最佳实践 |
| **代码量** | 少 | 少 | 稍多（但可复用） |
| **切换模型** | 改代码 | 改代码 | 改一行配置 |
| **适用阶段** | 学习/原型 | 学习/原型 | 生产项目 |

---

## 🧪 实验 1.3：命令行对话程序

### 目标
构建一个完整的命令行对话程序，支持多轮对话和历史记录。

### 代码示例

创建文件 `experiments/phase1/exp1_3_chat_cli.py`：

```python
"""
实验 1.3: 命令行对话程序
支持多轮对话、历史记录、系统提示词
"""
import ollama
from datetime import datetime

class ChatCLI:
    def __init__(self, model: str = "qwen2.5:7b"):
        self.model = model
        self.messages = []
        self.system_prompt = """你是一个专业的网络安全助手。
你精通各类安全技术，包括渗透测试、漏洞分析、安全开发等。
请用简洁专业的语言回答问题。"""
        
        # 添加系统提示词
        self.messages.append({
            "role": "system",
            "content": self.system_prompt
        })
    
    def chat(self, user_input: str) -> str:
        """发送消息并获取响应"""
        # 添加用户消息
        self.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # 调用模型
        response = ollama.chat(
            model=self.model,
            messages=self.messages
        )
        
        assistant_message = response["message"]["content"]
        
        # 保存助手回复到历史
        self.messages.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    
    def stream_chat(self, user_input: str):
        """流式对话"""
        self.messages.append({
            "role": "user",
            "content": user_input
        })
        
        stream = ollama.chat(
            model=self.model,
            messages=self.messages,
            stream=True
        )
        
        full_response = ""
        for chunk in stream:
            content = chunk["message"]["content"]
            print(content, end="", flush=True)
            full_response += content
        
        print()
        
        self.messages.append({
            "role": "assistant",
            "content": full_response
        })
    
    def clear_history(self):
        """清除对话历史"""
        self.messages = [{
            "role": "system",
            "content": self.system_prompt
        }]
        print("对话历史已清除。")
    
    def show_history(self):
        """显示对话历史"""
        print("\n=== 对话历史 ===")
        for i, msg in enumerate(self.messages[1:], 1):  # 跳过系统提示词
            role = "👤 用户" if msg["role"] == "user" else "🤖 助手"
            print(f"{i}. {role}: {msg['content'][:100]}...")
        print("================\n")


def main():
    print("=" * 50)
    print("  🔐 安全助手 - 命令行对话程序")
    print("  输入 /help 查看帮助")
    print("=" * 50)
    
    cli = ChatCLI()
    
    while True:
        try:
            user_input = input("\n👤 你: ").strip()
            
            if not user_input:
                continue
            
            # 命令处理
            if user_input.startswith("/"):
                if user_input == "/help":
                    print("""
命令列表:
  /help    - 显示帮助
  /clear   - 清除对话历史
  /history - 显示对话历史
  /exit    - 退出程序
                    """)
                elif user_input == "/clear":
                    cli.clear_history()
                elif user_input == "/history":
                    cli.show_history()
                elif user_input == "/exit":
                    print("再见！")
                    break
                else:
                    print(f"未知命令: {user_input}")
                continue
            
            # 正常对话
            print("\n🤖 助手: ", end="")
            cli.stream_chat(user_input)
            
        except KeyboardInterrupt:
            print("\n再见！")
            break


if __name__ == "__main__":
    main()
```

### 运行程序
```powershell
python exp1_3_chat_cli.py
```

### 功能验证
- [ ] 程序正常启动
- [ ] 支持多轮对话（记住上下文）
- [ ] `/help` 命令正常工作
- [ ] `/clear` 可清除历史
- [ ] `/history` 可查看历史
- [ ] `/exit` 可正常退出
- [ ] 流式输出效果正常

### 场景 B：OpenAI SDK 对话程序

> 场景 A 用 Ollama SDK 构建了对话程序。接下来用 OpenAI SDK 实现同样的功能，体会两者在多轮对话管理上的异同。核心区别在于客户端初始化和流式 chunk 的处理方式。

创建文件 `experiments/phase1/exp1_3b_chat_cli_openai.py`：

```python
"""
实验 1.3b: OpenAI SDK 对话程序
对比 Ollama 版本，理解 OpenAI 格式的多轮对话管理
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ChatCLI:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.messages = []
        self.system_prompt = """你是一个专业的网络安全助手。
你精通各类安全技术，包括渗透测试、漏洞分析、安全开发等。
请用简洁专业的语言回答问题。"""
        
        self.messages.append({"role": "system", "content": self.system_prompt})
    
    def chat(self, user_input: str) -> str:
        """
        发送消息并获取响应 — 对比 Ollama 版本：
        
        Ollama:  ollama.chat(model, messages, stream=True)
                 → chunk["message"]["content"]（总是有值）
        OpenAI:  client.chat.completions.create(model, messages, stream=True)
                 → chunk.choices[0].delta.content（可能为 None）
        """
        self.messages.append({"role": "user", "content": user_input})
        
        print("\n🤖 助手: ", end="", flush=True)
        full_response = ""
        
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            stream=True
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:  # OpenAI 的 chunk 可能为 None
                print(content, end="", flush=True)
                full_response += content
        print()
        
        self.messages.append({"role": "assistant", "content": full_response})
        return full_response
    
    def run(self):
        """运行对话循环"""
        print("=" * 50)
        print(f"  🔐 安全助手 (OpenAI: {self.model})")
        print("  输入 'exit' 退出, 'clear' 清空历史")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n👤 你: ")
            except (EOFError, KeyboardInterrupt):
                print("\n再见!")
                break
            
            if user_input.strip().lower() == "exit":
                print("再见!")
                break
            if user_input.strip().lower() == "clear":
                self.messages = [{"role": "system", "content": self.system_prompt}]
                print("✅ 对话历史已清空")
                continue
            if not user_input.strip():
                continue
            
            self.chat(user_input)


if __name__ == "__main__":
    cli = ChatCLI()
    cli.run()
```

### 运行方式
```powershell
python exp1_3b_chat_cli_openai.py
```

### 功能验证
- [ ] 多轮对话正常（模型记住上下文）
- [ ] 流式输出逐字显示
- [ ] `clear` 清空历史后模型"忘记"之前的对话

#### Ollama vs OpenAI 对话程序差异

| | Ollama（场景 A） | OpenAI（场景 B） |
|---|---|---|
| **初始化** | 无需，`import ollama` 即可 | 需创建 `OpenAI(api_key, base_url)` 客户端 |
| **调用方式** | `ollama.chat(model, messages)` | `client.chat.completions.create(model, messages)` |
| **流式 chunk** | `chunk["message"]["content"]` | `chunk.choices[0].delta.content`（需判空） |
| **多轮对话** | 手动维护 `messages` 列表 | 手动维护 `messages` 列表（相同） |

### 场景 C：LangChain 对话程序

> 场景 A/B 都需要手动维护 `messages` 列表来实现多轮对话。LangChain 提供了 `ChatMessageHistory` 来自动管理对话历史，而且切换模型只需改一行配置，代码其余部分完全不变。

创建文件 `experiments/phase1/exp1_3c_chat_cli_langchain.py`：

```python
"""
实验 1.3c: LangChain 对话程序
用 LangChain 管理对话历史，体验框架的便利性
"""
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.chat_history import InMemoryChatMessageHistory

load_dotenv()


SYSTEM_PROMPT = """你是一个专业的网络安全助手。
你精通各类安全技术，包括渗透测试、漏洞分析、安全开发等。
请用简洁专业的语言回答问题。"""


def get_llm(backend: str = "ollama"):
    """
    获取 LLM 实例 — 切换模型只需改这一处
    
    对比之前：
    - 场景 A: 写死用 ollama.chat()，换模型要改整个类
    - 场景 B: 写死用 client.chat.completions.create()，换模型也要改整个类
    - 场景 C: 改这一行就能切换，其他代码完全不变 ✨
    """
    if backend == "ollama":
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        return ChatOllama(model="qwen2.5:7b", base_url=ollama_host)
    elif backend == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    raise ValueError(f"未知后端: {backend}")


class ChatCLI:
    def __init__(self, backend: str = "ollama"):
        self.llm = get_llm(backend)
        self.backend = backend
        # LangChain 自动管理对话历史（不再需要手动维护 messages 列表）
        self.history = InMemoryChatMessageHistory()
        self.history.add_message(SystemMessage(content=SYSTEM_PROMPT))
    
    def chat(self, user_input: str) -> str:
        """
        对话 — 对比手动管理 messages 的方式：
        
        场景 A/B:  self.messages.append({"role": "user", ...})
                   response = ollama.chat(messages=self.messages)
                   self.messages.append({"role": "assistant", ...})
        
        场景 C:    self.history.add_user_message(user_input)
                   response = self.llm.stream(self.history.messages)
                   self.history.add_ai_message(full_response)
        """
        self.history.add_user_message(user_input)
        
        print("\n🤖 助手: ", end="", flush=True)
        full_response = ""
        
        for chunk in self.llm.stream(self.history.messages):
            print(chunk.content, end="", flush=True)
            full_response += chunk.content
        print()
        
        self.history.add_ai_message(full_response)
        return full_response
    
    def clear(self):
        """清空历史"""
        self.history.clear()
        self.history.add_message(SystemMessage(content=SYSTEM_PROMPT))
        print("✅ 对话历史已清空")
    
    def run(self):
        """运行对话循环"""
        print("=" * 50)
        print(f"  🔐 安全助手 (LangChain + {self.backend})")
        print("  输入 'exit' 退出, 'clear' 清空历史")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n👤 你: ")
            except (EOFError, KeyboardInterrupt):
                print("\n再见!")
                break
            
            cmd = user_input.strip().lower()
            if cmd == "exit":
                print("再见!")
                break
            if cmd == "clear":
                self.clear()
                continue
            if not user_input.strip():
                continue
            
            self.chat(user_input)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LangChain 安全助手")
    parser.add_argument("--backend", choices=["ollama", "openai"], default="openai")
    args = parser.parse_args()
    
    cli = ChatCLI(backend=args.backend)
    cli.run()
```

### 运行方式
```powershell
# 使用 OpenAI 模型（默认）
python exp1_3c_chat_cli_langchain.py

# 使用 Ollama 本地模型
python exp1_3c_chat_cli_langchain.py --backend ollama
```

### 功能验证
- [ ] `--backend openai` 正常对话
- [ ] `--backend ollama` 正常对话
- [ ] 两种后端的代码逻辑完全一样（只有 `get_llm` 不同）

#### 📖 LangChain 消息系统核心概念

场景 C 中用到了 `InMemoryChatMessageHistory` 和 `HumanMessage` 等类，它们的关系是：

```
InMemoryChatMessageHistory（历史管理器 — 装消息的容器）
├── .add_user_message("...")   → 内部创建 HumanMessage 并追加
├── .add_ai_message("...")     → 内部创建 AIMessage 并追加
├── .add_message(msg)          → 直接追加任意 Message 对象
├── .messages                  → 返回消息列表 [Message, ...]
└── .clear()                   → 清空列表

Message 类（数据对象 — 只存数据，没有"添加"能力）
├── HumanMessage(content="...")    → 用户消息
├── AIMessage(content="...")       → AI 回复
└── SystemMessage(content="...")   → 系统提示词
```

**Message 是"消息"本身，History 是"装消息的容器"。** `add_user_message` 是容器的方法，不是消息的方法：

```python
# 这两行效果完全一样（前者是语法糖）
history.add_user_message("什么是XSS？")
history.add_message(HumanMessage(content="什么是XSS？"))
```

> **扩展**：`InMemoryChatMessageHistory` 只是内存实现。LangChain 还提供 `RedisChatMessageHistory`、`SQLChatMessageHistory` 等，切换存储只需换一个类，代码其余部分不变——这就是接口统一的价值。

#### 三种对话程序总结

| | Ollama 原生（A） | OpenAI SDK（B） | LangChain（C） |
|---|---|---|---|
| **历史管理** | 手动维护 `messages` 列表 | 手动维护 `messages` 列表 | `InMemoryChatMessageHistory` 自动管理 |
| **流式输出** | `chunk["message"]["content"]` | `chunk.choices[0].delta.content` | `chunk.content`（统一） |
| **切换模型** | 改整个调用逻辑 | 改整个调用逻辑 | 改 `get_llm()` 一行 |
| **代码量** | ~80 行 | ~90 行 | ~100 行（但更灵活） |
| **适用场景** | 学习原理 | 学习云端 API | 生产项目 |

---

## 📖 理论学习：Transformer 架构

### 核心概念

#### 1. Token（词元）
文本被分割成的最小单位。例如：
- "Hello World" → ["Hello", " World"]
- "你好世界" → ["你", "好", "世", "界"]

#### 2. Embedding（嵌入）
将 Token 转换为高维向量的过程。每个 Token 对应一个向量（如 768 维或 4096 维）。

#### 3. Context Window（上下文窗口）
模型一次能处理的最大 Token 数量。例如：
- Qwen2.5 7B: 128K tokens
- Llama 3.2: 128K tokens

#### 4. Attention（注意力机制）

Transformer 的核心创新。以下内容参考 [3Blue1Brown - Attention 可视化](https://www.youtube.com/watch?v=eMlx5fFNoYc)。

##### 为什么需要注意力机制？

Embedding 向量在初始阶段只编码了"这个词是什么"的信息，但没有上下文。例如"bank"在"river bank"和"bank account"中含义完全不同。**注意力机制的目标是让每个 Token 的向量能够吸收来自其他 Token 的相关信息，从而获得上下文感知的表示。**

##### 三个核心向量：Query、Key、Value

对于序列中的**每一个 Token**，通过其 Embedding 向量乘以三个不同的权重矩阵，产生三个新向量：

| 向量 | 权重矩阵 | 计算方式 | 直觉含义 |
|------|----------|----------|----------|
| **Query (Q)** | W_Q | Q = Embedding × W_Q | "我在找什么信息？" — 当前 Token 的**提问** |
| **Key (K)** | W_K | K = Embedding × W_K | "我能提供什么信息？" — 当前 Token 的**标签/索引** |
| **Value (V)** | W_V | V = Embedding × W_V | "我实际携带的内容" — 当前 Token 要**传递的信息** |

> W_Q、W_K、W_V 是三个独立的权重矩阵，在训练过程中通过反向传播学习得到。它们的初始值是随机的，训练完成后编码了"什么样的词应该关注什么样的词"的模式。

##### 注意力计算流程

```
步骤 1: 生成 Q、K、V
         每个 Token 的 Embedding → 乘以 W_Q → Query 向量
                                 → 乘以 W_K → Key 向量
                                 → 乘以 W_V → Value 向量

步骤 2: 计算注意力分数（点积）
         Score = Q · K^T
         ┌───────────────────────────────────────────────┐
         │ Token_A 的 Query · Token_B 的 Key = 相关性分数 │
         │ 点积越大 → 两个 Token 越相关                   │
         │ 点积接近零 → 两个 Token 关联性弱                │
         └───────────────────────────────────────────────┘

步骤 3: 缩放（Scale）
         Score = Score / √d_k
         d_k 是 Key 向量的维度。除以 √d_k 防止点积值过大导致
         softmax 输出趋于极端（梯度消失问题）。

步骤 4: Softmax 归一化
         Weights = softmax(Score)
         ┌────────────────────────────────────────────────┐
         │ 将分数转化为概率分布（所有权重之和 = 1）              │
         │ 例: [2.1, 0.3, 5.8, 0.1] → [0.05, 0.01, 0.93, 0.01]│
         │ 含义：当前 Token 应把 93% 的注意力放在第 3 个 Token 上  │
         └────────────────────────────────────────────────┘

步骤 5: 加权求和
         Output = Weights × V
         用注意力权重对所有 Token 的 Value 向量加权求和，
         得到融合了上下文信息的新向量。
```

##### 公式总结

```
Attention(Q, K, V) = softmax(Q·K^T / √d_k) × V
```

##### 一个具体的例子

考虑句子："安全工程师发现了一个严重的漏洞"

```
                    安全  工程师  发现  了  一个  严重的  漏洞
"漏洞" 的 Query ·    ↓     ↓     ↓   ↓    ↓     ↓      ↓
各 Token 的 Key     0.1   0.2   0.3  0.0  0.0   0.3    1.0
                                                  ↑      ↑
                              softmax 后 "严重的" 和 "漏洞" 自身关注度最高

→ "漏洞" 的输出向量 = 0.1×V_安全 + 0.2×V_工程师 + 0.3×V_发现 + ... + 0.3×V_严重的 + 1.0×V_漏洞
→ 这个新向量现在不仅知道"漏洞"是什么，还融入了"严重的"这个修饰信息
```

##### 多头注意力（Multi-Head Attention）

实际的 Transformer 会使用**多个**注意力头并行工作：

```
┌──────────────────────────────────────────────────┐
│  Head 1 (W_Q1, W_K1, W_V1): 可能学习语法关系       │
│  Head 2 (W_Q2, W_K2, W_V2): 可能学习语义关联       │
│  Head 3 (W_Q3, W_K3, W_V3): 可能学习指代关系       │
│  ...                                             │
│  Head N: 可能学习其他模式                           │
│                                                  │
│  最终输出 = Concat(Head1, Head2, ..., HeadN) × W_O │
└──────────────────────────────────────────────────┘
```

每个 Head 拥有独立的 W_Q、W_K、W_V 矩阵，因此能**同时关注不同类型的关系**。例如：
- 一个 Head 学会了"形容词修饰名词"的模式
- 另一个 Head 学会了"主语-谓语"的语法关系
- 还有 Head 可能学会了"远距离指代"的模式

所有 Head 的输出拼接后再通过一个线性变换 W_O，得到最终的上下文感知表示。

### 推荐学习资源
1. **[3Blue1Brown - Attention 可视化](https://www.youtube.com/watch?v=eMlx5fFNoYc)**
2. **[The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)**
3. **[Andrej Karpathy - Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY)**

### 理解验证
完成学习后，你应该能回答以下问题：
- [ ] 什么是 Token？模型如何处理文本？

    Token是模型最小的输入输出单位。从用户角度讲，token就是单词（英语）或者字（中文）。
- [ ] Embedding 的作用是什么？

    Embedding是将token转换为高维向量的过程。一般Embedding vector记录了token的语义信息和其在语句中的位置信息。

- [ ] 为什么需要 Attention 机制？
查询向量
键向量
softmax
    
- [ ] Context Window 对使用有什么影响？

---

## ✅ 阶段检查清单

完成本阶段前，请确保：

| 检查项 | 状态 |
|--------|------|
| Ollama 安装并运行正常 | ⬜ |
| 至少下载一个本地模型 | ⬜ |
| 实验 1.1: 命令行对话成功 | ⬜ |
| 实验 1.2: Python API 调用成功 | ⬜ |
| 实验 1.3: 对话程序功能完整 | ⬜ |
| 理解 Transformer 基础概念 | ⬜ |

---

## 🚀 下一步

完成阶段一后，进入 [阶段二：模型微调与后训练](phase2_finetuning.md)

---

## 📝 学习笔记

> 在此记录本阶段的学习心得和问题

1. 模型的输出方式有simple模式和stream模式，simple是一次性输出所有回答，stream是逐字回答；
2. 模型本身是没有记忆的，实际会把历史的问答以字典的形式发送给模型。上下文的本质就是一次性把所有对话发给模型，然后模型根据上下文输出最新问题的答案。

---

## 📋 避坑指南：环境与 API 常见陷阱

> 以下是实际操作中踩过的坑，记录在此供回顾参考。

### 1. WSL 虚拟环境隔离（PEP 668）

WSL 中的 Python 3.12 遵循 PEP 668，禁止在系统级 Python 中直接 `pip install`，必须先创建虚拟环境。

**关键陷阱**：Windows 创建的 venv（目录结构为 `Scripts/`）和 Linux 创建的 venv（目录结构为 `bin/`）**不可混用**。

```bash
# ❌ 错误：在 WSL 中激活 Windows 创建的 venv
source venv/Scripts/activate   # 看似成功，但 pip 仍指向系统级

# ✅ 正确：在 WSL 中创建 Linux 原生 venv
python3 -m venv venv_wsl
source venv_wsl/bin/activate
pip install ollama openai requests python-dotenv langchain langchain-openai langchain-ollama
```

> **根因**：Windows venv 内置的是 Windows Python 解释器路径，WSL 无法正确识别，导致激活后 `pip` 仍指向系统级。

### 2. WSL 访问宿主机 Ollama

WSL 与 Windows 宿主机并非完全共享 `localhost`。当 Ollama 运行在 Windows 上时，WSL 内的代码可能连不上 `localhost:11434`。

**解决方案**：让 Ollama 监听所有网络接口：

```powershell
# 在 Windows PowerShell 中设置环境变量
[System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', '0.0.0.0', 'User')

# 重启 Ollama 服务后生效
```

然后在 WSL 中通过宿主机 IP 或 `host.docker.internal` 访问。

### 3. 终端中文编码陷阱（Unicode 代理对）

在 WSL 终端中输入中文时，可能产生无效的 UTF-8 字符（surrogate pairs），导致：

```
UnicodeEncodeError: 'utf-8' codec can't encode characters: surrogates not allowed
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe6: invalid continuation byte
```

**双层防御方案**：

```python
# 第一层：try-except 捕获 input() 本身的解码异常
try:
    user_input = input("你: ")
except UnicodeDecodeError:
    print("⚠️ 输入编码异常，请重新输入")
    continue

# 第二层：清洗已读入的字符串中的无效字符
user_input = user_input.encode('utf-8', errors='ignore').decode('utf-8')
```

> **注意**：第一层是必须的，因为 `input()` 函数内部就可能抛异常，此时第二层的 `encode/decode` 根本来不及执行。

### 4. OpenAI SDK 版本升级（v0.x → v1.x）

OpenAI Python SDK 在 v1.0 进行了破坏性升级，旧写法直接报错 `APIRemovedInV1`：

| 项目 | v0.x 旧版 | v1.x 新版 |
|------|-----------|-----------|
| **导入** | `import openai` | `from openai import OpenAI` |
| **配置** | `openai.api_key = "..."` | `client = OpenAI(api_key="...")` |
| **调用** | `openai.ChatCompletion.create(...)` | `client.chat.completions.create(...)` |
| **流式 chunk** | `chunk["choices"][0]["delta"]["content"]` | `chunk.choices[0].delta.content`（需判空） |

```python
# ✅ v1.x 正确写法
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))

response = client.chat.completions.create(
    model="qwen3.5-plus",
    messages=[{"role": "user", "content": "你好"}],
    stream=True
)

for chunk in response:
    content = chunk.choices[0].delta.content
    if content:  # 流式模式下 content 可能为 None
        print(content, end="", flush=True)
```

---

## 📋 核心概念总结：参数与流式机制

### temperature（温度）

控制模型输出的**随机性**，决定概率分布的"平坦程度"：

| 值 | 效果 | 适用场景 |
|---|---|---|
| `0` | 几乎确定性输出，每次回答一致 | 代码生成、事实性问答、安全分析 |
| `0.7` | 适度随机，平衡创意和准确性 | 通用对话（推荐默认值） |
| `1.0+` | 高度随机，回答更有创意但可能跑偏 | 创意写作、头脑风暴 |

**原理**：模型生成每个 token 时会计算所有候选词的概率分布。`temperature` 越低，概率最高的词越容易被选中；值越高，低概率的词也有机会被选中。

### max_tokens（最大令牌数）

限制模型**最多生成多少个 token**：
- `max_tokens=500` → 回答最多约 250-350 个中文字（1 个中文字 ≈ 1.5-2 个 token）
- 到达上限时模型会被**截断**，可能句子没说完就停了
- 不设置则使用模型默认上限（通常 4096 或更多）

> **实用建议**：安全分析场景建议设 1000-2000，避免截断；简单问答设 500 足够。

### 流式输出与 flush 机制

**`stream=True` 改变了什么？**

| 对比项 | stream=False（默认） | stream=True |
|--------|---------------------|-------------|
| 返回类型 | 完整的 Response 对象 | 生成器（Generator），逐 chunk 产出 |
| 获取文本 | `response.choices[0].message.content` | `chunk.choices[0].delta.content` |
| 用户体验 | 等待几秒后一次性显示全部 | 逐字打印，像打字机 |
| 适用场景 | 后台处理、批量调用 | 交互式对话、实时展示 |

**`flush=True` 的关键作用**：

```python
# ❌ 没有 flush：文字被攒在缓冲区，最后一坨全出来（和非流式没区别）
print(chunk.content, end="")

# ✅ 有 flush：每个 chunk 立即输出到屏幕（真正的打字机效果）
print(chunk.content, end="", flush=True)
```

`flush=True` 强制 Python 在每次 `print` 后立即清空输出缓冲区。默认情况下，当 `end=""` 取消了换行符时，输出会被缓存直到缓冲区满或遇到换行。这就是为什么不加 `flush=True`，流式输出就白做了。