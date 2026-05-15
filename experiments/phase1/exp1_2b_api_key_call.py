"""
实验 1.2b: API Key 模式 - OpenAI 兼容格式调用
对比 Ollama 原生调用，理解 API 差异

适用场景：
  - 使用云服务 API（OpenAI、DeepSeek、通义千问等）
  - 使用自建 API 服务（vLLM、TGI、Ollama OpenAI 模式）
  - 需要跨平台兼容的场景

架构图：
  ┌─────────────┐     HTTPS API     ┌─────────────┐
  │ Python 代码  │ ───────────────► │  API 服务   │
  │  (本文件)    │    + API Key     │ (OpenAI/    │
  │             │ ◄─────────────── │  DeepSeek/  │
  │  openai SDK │    JSON 响应      │  自建服务等) │
  └─────────────┘                   └─────────────┘

与 Ollama 原生 API 的区别：
  ┌────────────────┬─────────────────┬─────────────────┐
  │     特性        │   Ollama SDK    │   OpenAI SDK    │
  ├────────────────┼─────────────────┼─────────────────┤
  │ 认证方式        │ 无（本地服务）   │ API Key         │
  │ 默认地址        │ localhost:11434 │ api.openai.com  │
  │ 消息格式        │ 相同             │ 相同            │
  │ 流式支持        │ stream=True     │ stream=True     │
  │ 模型列表        │ ollama list     │ 自行管理        │
  └────────────────┴─────────────────┴─────────────────┘
"""

# ==================== 导入 ====================
import os
from openai import OpenAI
# OpenAI: 官方 Python SDK，支持 OpenAI API 和兼容服务

from dotenv import load_dotenv
# python-dotenv: 从 .env 文件加载环境变量
# 避免在代码中硬编码 API Key

# ==================== 配置加载 ====================
load_dotenv()
# 读取项目根目录的 .env 文件
# .env 文件格式：
#   OPENAI_API_KEY=sk-xxx
#   OPENAI_BASE_URL=https://opencode.ai/zen/go/v1
#   OPENAI_MODEL=deepseek-v4-pro

# ==================== 客户端初始化 ====================
# OpenAI 客户端是线程安全的，可以全局初始化后复用
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    # API Key：从云服务商获取
    # 格式通常是 sk-xxx 或类似

    base_url=os.getenv("OPENAI_BASE_URL"),
    # API 地址：
    # - OpenCode Go: https://opencode.ai/zen/go/v1
    # - DeepSeek: https://api.deepseek.com/v1
    # - 通义千问: https://dashscope.aliyuncs.com/compatible-mode/v1
    # - Ollama OpenAI 模式: http://localhost:11434/v1
    # - 自建服务: 根据实际情况配置
)

# 默认模型配置
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "deepseek-v4-pro")
# 从环境变量读取，不存在则使用默认值

# 待测试的提示词
prompt = "你是一个网络安全专家，请解释什么是 SQL 注入？"


# ============================================================
# 函数 1：非流式对话
# ============================================================

def simple_chat(prompt, model=DEFAULT_MODEL):
    """
    非流式对话函数

    调用流程：
    1. 构建请求（model + messages + 参数）
    2. 发送 POST 请求到 {base_url}/chat/completions
    3. 等待模型生成完毕
    4. 返回完整响应

    Args:
        prompt: 用户输入
        model: 模型名称（不同服务商支持的模型不同）

    响应结构：
    {
        "id": "chatcmpl-xxx",
        "object": "chat.completion",
        "model": "deepseek-v4-pro",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "模型生成的文本..."
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 100,
            "total_tokens": 110
        }
    }
    """
    print(f"使用模型: {model}")
    print("-" * 60)

    # client.chat.completions.create() 是核心调用方法
    response = client.chat.completions.create(
        model=model,
        # messages 是对话历史，按顺序排列
        messages=[
            {"role": "system", "content": "你是一个安全助手"},
            # system: 系统提示词，定义 AI 的角色和行为
            {"role": "user", "content": prompt},
            # user: 用户消息
        ],
        temperature=0.7,
        # temperature: 控制随机性，0-2
        # - 0: 确定性输出，每次相同
        # - 0.7: 平衡创造性和一致性
        # - 2: 高度随机，可能不稳定

        max_tokens=500,
        # max_tokens: 限制生成的最大 token 数
        # 用于控制成本和响应长度
    )

    # 从响应中提取回复文本
    # response.choices[0] 是第一个（通常也是唯一一个）选择
    reply = response.choices[0].message.content

    print(f"\n用户: {prompt}")
    print(f"\n模型: {reply}")
    print("\n" + "-" * 60)
    print(f"API 调用成功！模型: {model}")


# ============================================================
# 函数 2：流式对话
# ============================================================

def stream_chat(prompt, model=DEFAULT_MODEL):
    """
    流式对话函数

    与非流式的区别：
    - 设置 stream=True
    - 返回一个迭代器而非完整响应
    - 每个 chunk 包含一小段文本

    流式响应结构（每个 chunk）：
    {
        "id": "chatcmpl-xxx",
        "choices": [{
            "delta": {
                "content": "一个字"  # 注意是 delta 而非 message
            }
        }]
    }
    """
    print(f"使用模型: {model}")
    print("-" * 60)

    # 启用流式模式
    stream_response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个安全助手"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=500,
        stream=True,  # 关键参数：启用流式输出
    )

    print(f"\n用户: {prompt}")
    print(f"\n模型: ", end="")

    # 遍历流中的每个 chunk
    for chunk in stream_response:
        # chunk.choices[0].delta.content 是当前片段
        # delta 可能只有 content，也可能有 role（第一个 chunk）
        content = chunk.choices[0].delta.content
        if content:
            # 只有 content 非空时才输出
            # 第一个 chunk 可能只有 role 没有 content
            print(content, end="", flush=True)

    print("\n" + "-" * 60)
    print(f"API 流式调用成功！模型: {model}")


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    # 非流式调用示例
    # simple_chat(prompt)                       # 使用 .env 中的默认模型
    # simple_chat(prompt, model="deepseek-v4-pro") # 或手动指定模型

    # 流式调用示例
    stream_chat(prompt)
    # stream_chat(prompt, model="deepseek-v4-pro")