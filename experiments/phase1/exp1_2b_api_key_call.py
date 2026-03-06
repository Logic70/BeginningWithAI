"""
实验 1.2b: API Key 模式 - OpenAI 兼容格式调用
对比 Ollama 原生调用，理解 API 差异
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 配置
load_dotenv()

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# 默认模型（来自 .env），不存在则返回 qwen3.5-plus
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "qwen3.5-plus")

# 待测试的提示词
prompt = "你是一个网络安全专家，请解释什么是 SQL 注入？"


def simple_chat(prompt, model=DEFAULT_MODEL):
    """非流式对话"""
    print(f"🚀 使用模型: {model}")
    print("-" * 60)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个安全助手"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=500,
    )

    reply = response.choices[0].message.content

    print(f"\n👤 用户: {prompt}")
    print(f"\n🤖 模型: {reply}")
    print("\n" + "-" * 60)
    print(f"✅ API 调用成功！模型: {model}")


def stream_chat(prompt, model=DEFAULT_MODEL):
    """流式对话"""
    print(f"🚀 使用模型: {model}")
    print("-" * 60)

    stream_response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个安全助手"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=500,
        stream=True,
    )

    print(f"\n👤 用户: {prompt}")
    print(f"\n🤖 模型: ", end="")
    for chunk in stream_response:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
    print("\n" + "-" * 60)
    print(f"✅ API 流式调用成功！模型: {model}")


if __name__ == "__main__":
    # simple_chat(prompt)                      # 使用 .env 中的默认模型
    # simple_chat(prompt, model="qwen3.5-plus") # 或手动指定模型
    # stream_chat(prompt)
    stream_chat(prompt, model="qwen3.5-plus")