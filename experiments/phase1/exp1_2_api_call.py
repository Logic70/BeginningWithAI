"""
实验 1.2: Ollama 本地模型 API 调用
展示两种调用模式：非流式（等待完整响应）vs 流式（实时逐字输出）

运行前提：
  1. 安装 Ollama: https://ollama.ai
  2. 下载模型: ollama pull qwen2.5:7b
  3. 启动服务: ollama serve（或自动启动）

架构图：
  ┌─────────────┐     HTTP API      ┌─────────────┐
  │ Python 代码  │ ───────────────► │   Ollama    │
  │  (本文件)    │                   │   Server    │
  │             │ ◄─────────────── │ (localhost:  │
  │  ollama SDK │    JSON 响应      │  11434)     │
  └─────────────┘                   └─────────────┘

关键概念：
  - 非流式调用：等待模型生成完整响应后一次性返回
  - 流式调用：模型逐 token 生成，实时返回每个片段
"""

# ==================== 导入 ====================
import ollama
# ollama: 官方 Python SDK，封装了与 Ollama Server 的 HTTP 通信
# 自动连接 http://localhost:11434（默认端口）


# ============================================================
# 函数 1：非流式对话
# ============================================================

def simple_chat(prompt: str, model: str = "qwen2.5:7b") -> str:
    """
    简单对话函数（非流式）

    特点：
    - 等待模型生成完整响应后一次性返回
    - 用户需要等待较长时间才能看到输出
    - 适合批量处理、自动化脚本

    Args:
        prompt: 用户输入的提示词
        model: 模型名称（需先用 ollama pull 下载）

    Returns:
        str: 模型的完整响应文本

    API 调用流程：
    1. 构建请求体 {"model": "...", "messages": [...]}
    2. POST 到 http://localhost:11434/api/chat
    3. 等待模型生成完毕
    4. 返回完整响应
    """
    # ollama.chat() 是同步调用，会阻塞直到模型完成生成
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
            # messages 是对话历史列表，每个元素是一个消息字典
            # role: "user"(用户) / "assistant"(助手) / "system"(系统)
            # content: 消息内容
        ]
    )

    # response 结构：
    # {
    #     "model": "qwen2.5:7b",
    #     "created_at": "2024-...",
    #     "message": {
    #         "role": "assistant",
    #         "content": "模型生成的文本..."
    #     },
    #     "done": true
    # }
    return response["message"]["content"]


# ============================================================
# 函数 2：流式对话
# ============================================================

def stream_chat(prompt: str, model: str = "qwen2.5:7b"):
    """
    流式对话函数（实时输出）

    特点：
    - 模型每生成一个 token 就立即返回
    - 用户几乎立刻看到第一个字
    - 适合交互式场景、聊天界面

    Args:
        prompt: 用户输入的提示词
        model: 模型名称

    API 调用流程：
    1. 构建请求体（同非流式）
    2. POST 到 http://localhost:11434/api/chat?stream=true
    3. 收到每个 token 立即触发回调
    4. 持续直到 done=True

    流式响应结构（每个 chunk）：
    {
        "model": "qwen2.5:7b",
        "created_at": "...",
        "message": {"role": "assistant", "content": "一个字"},
        "done": false
    }
    最后一个 chunk: {"done": true, ...}
    """
    # stream=True 启用流式模式
    stream = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True  # 关键参数：启用流式输出
    )

    # 遍历流中的每个 chunk
    # 每个 chunk 包含一小段生成的文本（通常是一个 token）
    for chunk in stream:
        # chunk["message"]["content"] 是当前片段的文本
        # end="" 阻止 print 自动换行
        # flush=True 强制立即输出（否则可能被缓冲）
        print(chunk["message"]["content"], end="", flush=True)
    print()  # 最后换行


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    import time

    # ==================== 测试非流式调用 ====================
    print("=== 简单对话测试（非流式）===")
    print("等待模型生成完整响应...")
    start = time.time()
    response = simple_chat("用一句话解释什么是缓冲区溢出。")
    elapsed = time.time() - start
    print(f"模型回复: {response}")
    print(f"耗时 {elapsed:.1f} 秒，等待完整响应后一次性输出\n")

    # ==================== 测试流式调用 ====================
    print("=== 流式对话测试 ===")
    print("实时逐字输出中...")
    start = time.time()
    stream_chat("用一句话解释什么是 SQL 注入。")
    elapsed = time.time() - start
    print(f"耗时 {elapsed:.1f} 秒，但首字几乎立刻显示")

    # ==================== 对比总结 ====================
    # 非流式：适合后台任务、批量处理
    # 流式：适合聊天界面、交互式应用
    # 流式不会更快，但用户体验更好（首字延迟低）