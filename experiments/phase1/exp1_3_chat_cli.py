"""
实验 1.3: 命令行对话程序（Ollama 版）
支持多轮对话、历史记录、系统提示词

核心概念：
  - 多轮对话：保持上下文，AI 记住之前的交流
  - 历史记录：存储所有对话消息的列表
  - 系统提示词：定义 AI 的角色和行为

架构图：
  ┌─────────────────────────────────────────────────────┐
  │                    ChatCLI 类                        │
  │  ┌─────────────────────────────────────────────┐   │
  │  │ messages = [                                 │   │
  │  │   {"role": "system", "content": "系统提示"}, │   │
  │  │   {"role": "user", "content": "用户消息"},   │   │
  │  │   {"role": "assistant", "content": "AI回复"},│   │
  │  │   ...                                       │   │
  │  │ ]                                           │   │
  │  └─────────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────────┘
                            ↓
                   ollama.chat(messages)
                            ↓
  ┌─────────────────────────────────────────────────────┐
  │                   Ollama Server                      │
  │         根据完整历史生成下一个回复                    │
  └─────────────────────────────────────────────────────┘

对话历史结构：
  messages = [
      {"role": "system", "content": "你是一个安全助手..."},
      {"role": "user", "content": "什么是 XSS？"},
      {"role": "assistant", "content": "XSS 是跨站脚本攻击..."},
      {"role": "user", "content": "如何防御？"},  # 新问题
      # AI 会基于之前的历史回答
  ]
"""

# ==================== 导入 ====================
import ollama
# ollama: Ollama 官方 Python SDK

from datetime import datetime
# 用于时间戳记录（可选功能）


# ============================================================
# 核心类：ChatCLI
# ============================================================

class ChatCLI:
    """
    命令行对话客户端

    职责：
    1. 管理对话历史（messages 列表）
    2. 处理用户输入
    3. 调用模型生成响应
    4. 流式输出响应
    """

    def __init__(self, model: str = "qwen2.5:7b"):
        """
        初始化对话客户端

        Args:
            model: 使用的模型名称

        初始化流程：
        1. 设置模型名称
        2. 创建空的消息列表
        3. 添加系统提示词
        """
        self.model = model

        # 对话历史：存储所有消息
        # 每条消息是一个字典：{"role": "...", "content": "..."}
        self.messages = []

        # 系统提示词：定义 AI 的角色、行为、回答风格
        # 这是整个对话的"人设"，会影响所有回复
        self.system_prompt = """你是一个专业的网络安全助手。
你精通各类安全技术，包括渗透测试、漏洞分析、安全开发等。
请用简洁专业的语言回答问题。"""

        # 添加系统提示词到历史
        # 系统消息必须放在第一条
        self.messages.append({
            "role": "system",
            "content": self.system_prompt
        })

    def chat(self, user_input: str) -> str:
        """
        发送消息并获取响应

        流程：
        1. 将用户消息添加到历史
        2. 调用模型（传入完整历史）
        3. 流式输出响应
        4. 将响应添加到历史

        Args:
            user_input: 用户输入的文本

        Returns:
            str: AI 的完整响应

        为什么需要传入完整历史？
        - LLM 是无状态的，每次调用都是独立的
        - 需要通过 messages 列表传递上下文
        - 模型会根据历史生成连贯的回复
        """
        # 步骤 1：添加用户消息到历史
        self.messages.append({
            "role": "user",
            "content": user_input
        })

        # 步骤 2：调用模型（流式输出）
        print("\n助手: ", end="", flush=True)
        full_response = ""

        # ollama.chat() 会把整个 messages 列表发给模型
        stream = ollama.chat(
            model=self.model,
            messages=self.messages,  # 传入完整历史
            stream=True              # 启用流式输出
        )

        # 步骤 3：逐 chunk 输出
        for chunk in stream:
            text = chunk["message"]["content"]
            print(text, end="", flush=True)
            full_response += text  # 累积完整响应
        print()

        # 步骤 4：保存助手回复到历史
        # 这一步很重要！否则 AI 不会"记住"自己说过什么
        self.messages.append({
            "role": "assistant",
            "content": full_response
        })

        return full_response

    def run(self):
        """
        运行对话循环

        这是一个无限循环，持续读取用户输入并响应
        直到用户输入 'exit' 或发生中断
        """
        print("=== 安全助手对话程序 ===")
        print(f"模型: {self.model}")
        print("输入 'exit' 退出, 'clear' 清空历史\n")

        while True:
            try:
                # 读取用户输入
                user_input = input("你: ")
            except (EOFError, KeyboardInterrupt):
                # EOFError: Ctrl+D (Unix) 或 Ctrl+Z (Windows)
                # KeyboardInterrupt: Ctrl+C
                print("\n再见!")
                break

            # 处理特殊命令
            if user_input.strip().lower() == "exit":
                print("再见!")
                break

            if user_input.strip().lower() == "clear":
                # 清空历史，但保留系统提示词
                self.messages = [{"role": "system", "content": self.system_prompt}]
                print("对话历史已清空\n")
                continue

            if not user_input.strip():
                # 空输入，跳过
                continue

            # 正常对话
            self.chat(user_input)


# ============================================================
# 主程序入口
# ============================================================

if __name__ == "__main__":
    # 创建客户端实例
    cli = ChatCLI()

    # 运行对话循环
    cli.run()