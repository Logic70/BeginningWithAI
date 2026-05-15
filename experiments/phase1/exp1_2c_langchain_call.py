"""
实验 1.2c: LangChain 统一接口
用相同的代码调用 Ollama 和 OpenAI，理解框架的抽象价值

核心价值：
  - 一套代码，多种后端
  - 统一的消息格式（HumanMessage、SystemMessage）
  - 统一的调用方式（invoke、stream）
  - 易于切换模型、构建复杂应用

架构图：
  ┌─────────────────────────────────────────────────────┐
  │                     用户代码                          │
  │              model.invoke(messages)                  │
  └─────────────────────────────────────────────────────┘
                            ↓
  ┌─────────────────────────────────────────────────────┐
  │                   LangChain 层                       │
  │  ┌─────────────┐              ┌─────────────┐       │
  │  │ ChatOllama  │              │ ChatOpenAI  │       │
  │  │ (本地模型)   │              │ (云服务API) │       │
  │  └──────┬──────┘              └──────┬──────┘       │
  └─────────┼─────────────────────────────┼─────────────┘
            ↓                             ↓
  ┌─────────────────┐           ┌─────────────────┐
  │  Ollama Server  │           │  OpenAI API     │
  │  localhost:11434│           │  或兼容服务      │
  └─────────────────┘           └─────────────────┘

对比三种调用方式：
  ┌──────────────┬─────────────────┬─────────────────┬─────────────────┐
  │     特性      │    Ollama SDK   │    OpenAI SDK   │    LangChain    │
  ├──────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 本地模型      │       ✓         │       ✗         │       ✓         │
  │ 云服务 API    │       ✗         │       ✓         │       ✓         │
  │ 统一接口      │       ✗         │       ✗         │       ✓         │
  │ 工具调用      │       ✓         │       ✓         │       ✓         │
  │ 链式组合      │       ✗         │       ✗         │       ✓         │
  └──────────────┴─────────────────┴─────────────────┴─────────────────┘
"""

# ==================== 导入 ====================
import os
from dotenv import load_dotenv

# LangChain 核心组件
from langchain_openai import ChatOpenAI
# ChatOpenAI: LangChain 对 OpenAI API 的封装
# 支持所有 OpenAI 兼容的服务（DeepSeek、通义千问等）

from langchain_ollama import ChatOllama
# ChatOllama: LangChain 对 Ollama 的封装
# 底层仍调用 Ollama API，但使用统一的 LangChain 接口

from langchain_core.messages import HumanMessage, SystemMessage
# LangChain 的消息类型：
# - SystemMessage: 系统提示词，定义 AI 角色
# - HumanMessage: 用户消息
# - AIMessage: AI 回复（模型返回）

# ==================== 配置加载 ====================
load_dotenv()

# 待测试的提示词
prompt = "你是一个网络安全专家，请解释什么是 SQL 注入？"


# ============================================================
# 函数 1：统一调用接口
# ============================================================

def simple_chat(model_instance, model_name):
    """
    使用 LangChain 统一接口调用模型

    这是 LangChain 的核心价值：无论底层是 Ollama 还是 OpenAI，
    调用方式完全相同！

    Args:
        model_instance: LangChain 模型实例（ChatOllama 或 ChatOpenAI）
        model_name: 模型名称（用于打印）

    LangChain 调用流程：
    1. 构建消息列表（使用 HumanMessage、SystemMessage）
    2. 调用 model.invoke(messages)
    3. 从响应中提取 content

    invoke() 返回的 AIMessage 结构：
    {
        "content": "模型生成的文本...",
        "response_metadata": {...},
        "type": "ai"
    }
    """
    print(f"使用 LangChain 调用模型: {model_name}")
    print("-" * 60)

    # 构建消息列表
    # LangChain 使用类型化的消息对象，而非字典
    messages = [
        SystemMessage(content="你是一个安全助手"),
        # SystemMessage: 设置 AI 的角色和行为
        HumanMessage(content=prompt),
        # HumanMessage: 用户输入
    ]

    # invoke() 是 LangChain 的统一调用方法
    # 无论 ChatOllama 还是 ChatOpenAI，用法完全相同
    response = model_instance.invoke(messages)

    # 从响应中提取文本
    # response 是 AIMessage 对象
    # response.content 是生成的文本
    reply = response.content

    print(f"\n用户: {prompt}")
    print(f"\n模型: {reply}")
    print("\n" + "-" * 60)
    print(f"LangChain 调用成功！模型: {model_name}")


# ============================================================
# 函数 2：Ollama 测试
# ============================================================

def simple_test_ollama():
    """
    测试 Ollama 本地模型

    环境要求：
    1. 安装并运行 Ollama
    2. 下载模型: ollama pull qwen2.5:7b

    WSL 网络注意事项：
    - WSL 中 localhost 指向 WSL 自身
    - 若 Ollama 运行在宿主机，需使用宿主机 IP
    - 可在 .env 中配置: OLLAMA_HOST=http://host.docker.internal:11434
    - 或使用宿主机实际 IP: http://172.x.x.1:11434
    """
    # 从环境变量获取 Ollama 地址
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    # 创建 ChatOllama 实例
    ollama_model = ChatOllama(
        model="qwen2.5:7b",       # 模型名称
        base_url=ollama_host       # Ollama 服务地址
    )

    print(f"Ollama 地址: {ollama_host}")
    try:
        simple_chat(ollama_model, "qwen2.5:7b (Ollama)")
    except Exception as e:
        print(f"Ollama 调用失败: {e}")


# ============================================================
# 函数 3：OpenAI 测试
# ============================================================

def simple_test_openai():
    """
    测试 OpenAI 兼容 API

    环境要求：
    1. 在 .env 中配置:
       - OPENAI_API_KEY=sk-xxx
       - OPENAI_BASE_URL=https://opencode.ai/zen/go/v1
       - OPENAI_MODEL=deepseek-v4-pro

    支持的服务：
    - OpenAI 官方
    - DeepSeek
    - 通义千问
    - 智谱 AI
    - 自建服务（vLLM、TGI 等）
    """
    # 创建 ChatOpenAI 实例
    openai_model = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "deepseek-v4-pro"),
        # 模型名称（不同服务商支持的模型不同）

        base_url=os.getenv("OPENAI_BASE_URL"),
        # API 地址

        api_key=os.getenv("OPENAI_API_KEY"),
        # API Key
    )

    try:
        simple_chat(openai_model, "deepseek-v4-pro (OpenAI API)")
    except Exception as e:
        print(f"OpenAI 调用失败: {e}")


# ============================================================
# 函数 4：流式调用
# ============================================================

def stream_chat(model_instance, model_name):
    """
    流式对话函数

    LangChain 流式调用：
    - 使用 model.stream(messages) 替代 invoke()
    - 返回一个迭代器
    - 每个 chunk 是一个 AIMessageChunk 对象

    与 OpenAI SDK 的区别：
    - OpenAI: chunk.choices[0].delta.content
    - LangChain: chunk.content（更简洁）
    """
    print(f"使用 LangChain 调用模型: {model_name}")
    print("-" * 60)

    messages = [
        SystemMessage(content="你是一个安全助手"),
        HumanMessage(content=prompt),
    ]

    # stream() 返回一个异步迭代器
    response = model_instance.stream(messages)

    print(f"\n用户: {prompt}")
    print(f"\n模型: ", end="")

    # 遍历流中的每个 chunk
    for chunk in response:
        # chunk 是 AIMessageChunk 对象
        # chunk.content 是当前片段的文本
        print(chunk.content, end="", flush=True)

    print("\n" + "-" * 60)
    print(f"LangChain 调用成功！模型: {model_name}")


def stream_test_ollama():
    """测试 Ollama 流式调用"""
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model = ChatOllama(model="qwen2.5:7b", base_url=ollama_host)
    print(f"Ollama 地址: {ollama_host}")
    try:
        stream_chat(ollama_model, "qwen2.5:7b (Ollama)")
    except Exception as e:
        print(f"Ollama 调用失败: {e}")


def stream_test_openai():
    """测试 OpenAI 流式调用"""
    openai_model = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "deepseek-v4-pro"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    try:
        stream_chat(openai_model, "deepseek-v4-pro (OpenAI API)")
    except Exception as e:
        print(f"OpenAI 调用失败: {e}")


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    # 非流式调用
    # simple_test_ollama()    # 测试 Ollama
    # simple_test_openai()    # 测试 OpenAI API

    # 流式调用
    # stream_test_ollama()    # 测试 Ollama 流式
    stream_test_openai()      # 测试 OpenAI 流式