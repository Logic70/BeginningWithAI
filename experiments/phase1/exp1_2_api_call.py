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
    import time

    # 测试简单对话：会等全部生成完毕后才输出（注意等待时间）
    print("=== 简单对话测试 ===")
    print("⏳ 等待模型生成完整响应...")
    start = time.time()
    response = simple_chat("用一句话解释什么是缓冲区溢出。")
    elapsed = time.time() - start
    print(f"💬 {response}")
    print(f"⏱️ 等待 {elapsed:.1f} 秒后一次性输出\n")

    # 测试流式对话：逐字实时输出（注意文字是逐渐出现的）
    print("=== 流式对话测试 ===")
    print("⏳ 实时逐字输出中...")
    start = time.time()
    stream_chat("用一句话解释什么是 SQL 注入。")
    elapsed = time.time() - start
    print(f"⏱️ 共耗时 {elapsed:.1f} 秒，但首字几乎立刻显示")