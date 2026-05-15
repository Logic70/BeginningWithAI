"""
实验 1.3b: OpenAI SDK 对话程序
对比 Ollama 版本，理解 OpenAI 格式的多轮对话管理

与 Ollama 版本的主要区别：
  ┌────────────────┬─────────────────────┬─────────────────────┐
  │     特性        │      Ollama SDK     │     OpenAI SDK      │
  ├────────────────┼─────────────────────┼─────────────────────┤
  │ 初始化          │ 无需配置             │ 需要 API Key + URL  │
  │ 消息格式        │ 相同（字典）          │ 相同（字典）         │
  │ 流式访问        │ chunk["message"]    │ chunk.choices[0]    │
  │ 费用            │ 免费（本地）          │ 按使用量付费         │
  │ 模型切换        │ 改 model 参数        │ 改 model 参数        │
  └────────────────┴─────────────────────┴─────────────────────┘

适用场景：
  - 使用云服务 API（OpenAI、DeepSeek、通义千问等）
  - 需要远程模型能力的场景
  - 生产环境部署
"""

# ==================== 导入 ====================
import os
from openai import OpenAI
# OpenAI: 官方 Python SDK，支持 OpenAI API 和兼容服务

from dotenv import load_dotenv
# python-dotenv: 从 .env 文件加载环境变量

# ==================== 配置加载 ====================
load_dotenv()
# 读取 .env 文件中的配置：
# - OPENAI_API_KEY=sk-xxx
# - OPENAI_BASE_URL=https://opencode.ai/zen/go/v1
# - OPENAI_MODEL=deepseek-v4-pro


# ============================================================
# 核心类：ChatCLI
# ============================================================

class ChatCLI:
    """
    OpenAI SDK 对话客户端

    与 Ollama 版本的核心差异：
    1. 初始化需要 API Key 和 Base URL
    2. 流式响应的访问路径不同
    3. 需要处理网络异常和编码问题
    """

    def __init__(self):
        """
        初始化 OpenAI 客户端

        初始化流程：
        1. 创建 OpenAI 客户端实例
        2. 设置模型名称
        3. 初始化消息历史
        4. 添加系统提示词
        """
        # 创建 OpenAI 客户端
        # 这是线程安全的，可以全局复用
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            # API Key：从云服务商获取

            base_url=os.getenv("OPENAI_BASE_URL"),
            # API 地址：可以是 OpenAI 官方或兼容服务
        )

        # 模型名称
        self.model = os.getenv("OPENAI_MODEL", "deepseek-v4-pro")

        # 对话历史
        self.messages = []

        # 系统提示词
        self.system_prompt = """你是一个专业的网络安全助手。"""

        # 添加系统提示词
        self.messages.append({
            "role": "system",
            "content": self.system_prompt
        })

    def chat(self, user_input: str) -> str:
        """
        发送消息并获取响应

        流程：
        1. 清理输入中的无效字符
        2. 添加用户消息到历史
        3. 调用 OpenAI API（流式）
        4. 输出响应并保存到历史

        Args:
            user_input: 用户输入

        Returns:
            str: AI 的完整响应

        OpenAI 流式响应结构：
        for chunk in stream:
            chunk.choices[0].delta.content  # 当前片段
            # delta 而非 message！
        """
        # 清理无效 Unicode 字符
        # WSL 终端中文输入可能产生代理对（Surrogate Pair）
        # 这些字符会导致 API 调用失败
        user_input = user_input.encode('utf-8', errors='ignore').decode('utf-8')

        # 添加用户消息到历史
        self.messages.append({
            "role": "user",
            "content": user_input
        })

        print("\n助手: ", end="", flush=True)
        full_response = ""

        # 调用 OpenAI API
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,  # 传入完整历史
            stream=True              # 启用流式输出
        )

        # 遍历流式响应
        for chunk in stream:
            # 注意访问路径与 Ollama 不同
            # OpenAI: chunk.choices[0].delta.content
            # Ollama: chunk["message"]["content"]
            content = chunk.choices[0].delta.content
            if content:  # 可能是 None（第一个 chunk）
                print(content, end="", flush=True)
                full_response += content
        print()

        # 保存助手回复到历史
        self.messages.append({
            "role": "assistant",
            "content": full_response
        })

        return full_response

    def run(self):
        """
        运行对话循环

        与 Ollama 版本完全相同
        """
        print("=== 安全助手对话程序 ===")
        print(f"模型: {self.model}")
        print("输入 'exit' 退出, 'clear' 清空历史\n")

        while True:
            try:
                user_input = input("你: ")
            except (EOFError, KeyboardInterrupt):
                print("\n再见!")
                break

            if user_input.strip().lower() == "exit":
                print("再见!")
                break

            if user_input.strip().lower() == "clear":
                self.messages = [{"role": "system", "content": self.system_prompt}]
                print("对话历史已清空\n")
                continue

            if not user_input.strip():
                continue

            self.chat(user_input)


# ============================================================
# 主程序入口
# ============================================================

if __name__ == "__main__":
    cli = ChatCLI()
    cli.run()