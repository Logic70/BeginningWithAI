"""
实验 1.2c: LangChain 统一接口
用相同的代码调用 Ollama 和 OpenAI，理解框架的抽象价值
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

# 加载 .env 配置
load_dotenv()

# 待测试的提示词
prompt = "你是一个网络安全专家，请解释什么是 SQL 注入？"


def simple_chat(model_instance, model_name):
    """使用 LangChain 统一接口调用模型"""
    print(f"🚀 使用 LangChain 调用模型: {model_name}")
    print("-" * 60)

    # 构建消息列表
    messages = [
        SystemMessage(content="你是一个安全助手"),
        HumanMessage(content=prompt),
    ]

    # 调用模型
    response = model_instance.invoke(messages)

    # 提取回复
    reply = response.content

    print(f"\n👤 用户: {prompt}")
    print(f"\n🤖 模型: {reply}")
    print("\n" + "-" * 60)
    print(f"✅ LangChain 调用成功！模型: {model_name}")


def simple_test_ollama():
    '''
    1. 测试 Ollama 模型
    WSL 中 localhost 指向 WSL 自身，需用宿主机 IP 访问 Ollama
    可在 .env 中配置 OLLAMA_HOST=http://host.docker.internal:11434
    或用宿主机实际 IP，如 http://172.x.x.1:11434
    '''
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model = ChatOllama(model="qwen2.5:7b", base_url=ollama_host)
    print(f"📡 Ollama 地址: {ollama_host}")
    try:
        simple_chat(ollama_model, "qwen2.5:7b (Ollama)")
    except Exception as e:
        print(f"❌ Ollama 调用失败: {e}")

def simple_test_openai():
    '''
    2. 测试 OpenAI 兼容模型（API Key 模式）
    确保 .env 中配置了 OPENAI_API_KEY 和 OPENAI_BASE_URL
    '''
    openai_model = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "qwen3.5-plus"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    try:
        simple_chat(openai_model, "qwen3.5-plus (OpenAI API)")
    except Exception as e:
        print(f"❌ OpenAI 调用失败: {e}")


def stream_chat(model_instance, model_name):
    """使用 LangChain 统一接口调用模型"""
    print(f"🚀 使用 LangChain 调用模型: {model_name}")
    print("-" * 60)

    # 构建消息列表
    messages = [
        SystemMessage(content="你是一个安全助手"),
        HumanMessage(content=prompt),
    ]
    
    # 调用模型
    response = model_instance.stream(messages)
    print(f"\n👤 用户: {prompt}")
    print(f"\n🤖 模型: ", end="")
    # 提取回复
    for chunk in response:
        print(chunk.content, end="", flush=True)

    print("\n" + "-" * 60)
    print(f"✅ LangChain 调用成功！模型: {model_name}")

def stream_test_ollama():
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model = ChatOllama(model="qwen2.5:7b", base_url=ollama_host)
    print(f"📡 Ollama 地址: {ollama_host}")
    try:
        stream_chat(ollama_model, "qwen2.5:7b (Ollama)")
    except Exception as e:
        print(f"❌ Ollama 调用失败: {e}")

def stream_test_openai():
    openai_model = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "qwen3.5-plus"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    try:
        stream_chat(openai_model, "qwen3.5-plus (OpenAI API)")
    except Exception as e:
        print(f"❌ OpenAI 调用失败: {e}")

if __name__ == "__main__":
    # simple_test_ollama()
    # simple_test_openai()
    #stream_test_ollama()
    stream_test_openai()