"""
实验 1.3c: LangChain 对话程序
用 LangChain 管理对话历史，体验框架的便利性

核心价值：
  - 统一接口：一套代码支持 Ollama 和 OpenAI
  - 类型安全：使用 HumanMessage、AIMessage 等类型
  - 内置历史管理：InMemoryChatMessageHistory 自动管理消息
  - 易于扩展：可快速接入数据库持久化、工具调用等

三种对话管理方式对比：
  ┌──────────────────┬─────────────────┬─────────────────┬─────────────────┐
  │      特性         │   Ollama SDK    │   OpenAI SDK    │   LangChain     │
  ├──────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 消息存储          │ 手动管理 list   │ 手动管理 list   │ 内置管理器       │
  │ 消息类型          │ 字典            │ 字典            │ 类型化对象       │
  │ 切换后端          │ 改所有调用代码   │ 改所有调用代码   │ 改一处配置       │
  │ 流式访问          │ chunk["message"]│ chunk.choices[] │ chunk.content   │
  │ 工具调用支持       │ 手动实现        │ 手动实现        │ 内置支持        │
  │ 链式组合          │ 不支持          │ 不支持          │ 支持（LCEL）    │
  └──────────────────┴─────────────────┴─────────────────┴─────────────────┘
"""

# ==================== 导入 ====================
import os
from dotenv import load_dotenv

# LangChain 模型组件
from langchain_ollama import ChatOllama
# ChatOllama: LangChain 对 Ollama 的封装

from langchain_openai import ChatOpenAI
# ChatOpenAI: LangChain 对 OpenAI API 的封装

# LangChain 消息类型
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
# HumanMessage: 用户消息
# SystemMessage: 系统提示词
# AIMessage: AI 回复

# LangChain 历史管理
from langchain_core.chat_history import InMemoryChatMessageHistory
# InMemoryChatMessageHistory: 内存中的对话历史管理器
# 自动处理消息的添加、获取、清空

# ==================== 配置加载 ====================
load_dotenv()

# ==================== 系统提示词 ====================
SYSTEM_PROMPT = """你是一个专业的网络安全助手。
你精通各类安全技术，包括渗透测试、漏洞分析、安全开发等。
请用简洁专业的语言回答问题。"""


# ============================================================
# LLM 工厂函数
# ============================================================

def get_llm(backend: str = "ollama"):
    """
    获取 LLM 实例 — 切换模型只需改这一处

    这是 LangChain 的核心优势：
    - 场景 A (Ollama): 写死用 ollama.chat()，换模型要改整个类
    - 场景 B (OpenAI): 写死用 client.chat.completions.create()，换模型也要改
    - 场景 C (LangChain): 改这一行就能切换，其他代码完全不变

    Args:
        backend: 后端类型，"ollama" 或 "openai"

    Returns:
        LLM 实例（统一接口）
    """
    if backend == "ollama":
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        return ChatOllama(model="qwen2.5:7b", base_url=ollama_host)
    elif backend == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "deepseek-v4-pro"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    raise ValueError(f"未知后端: {backend}")


# ============================================================
# 核心类：ChatClient
# ============================================================

class ChatClient:
    """
    LangChain 对话客户端

    核心组件：
    1. llm: 语言模型实例（ChatOllama 或 ChatOpenAI）
    2. history: 对话历史管理器（InMemoryChatMessageHistory）

    与前两个版本的差异：
    - 使用类型化消息对象（HumanMessage、AIMessage）
    - 使用 InMemoryChatMessageHistory 管理历史
    - 切换后端只需改 get_llm() 的参数
    """

    def __init__(self, backend: str = "openai"):
        """
        初始化对话客户端

        Args:
            backend: 后端类型，"ollama" 或 "openai"
        """
        # 获取 LLM 实例
        self.llm = get_llm(backend)

        # 创建对话历史管理器
        # InMemoryChatMessageHistory 内部维护一个消息列表
        self.history = InMemoryChatMessageHistory()

        # 添加系统提示词
        # 这是第一条消息，定义 AI 的角色
        self.history.add_message(SystemMessage(content=SYSTEM_PROMPT))

    def chat(self, user_input: str):
        """
        发送消息并获取响应

        流程：
        1. 添加用户消息到历史
        2. 调用模型（传入完整历史）
        3. 流式输出响应
        4. 添加响应到历史

        Args:
            user_input: 用户输入
        """
        # 步骤 1：添加用户消息
        self.history.add_message(HumanMessage(content=user_input))
        # HumanMessage: 表示用户消息的类型

        # 步骤 2-3：调用模型并流式输出
        print(f"\n ({self.llm.model}) 助手: ", end="", flush=True)

        response_content = ""
        # self.history.messages 获取完整的消息列表
        # LangChain 会自动处理消息格式转换
        for chunk in self.llm.stream(self.history.messages):
            # LangChain 流式访问最简洁：chunk.content
            # 无需 chunk["message"]["content"] 或 chunk.choices[0].delta.content
            print(chunk.content, end="", flush=True)
            response_content += chunk.content
        print()

        # 步骤 4：添加 AI 回复到历史
        self.history.add_message(AIMessage(content=response_content))
        # AIMessage: 表示 AI 回复的类型

        return response_content

    def run(self):
        """
        运行对话循环

        支持的命令：
        - exit / quit: 退出程序
        - clear: 清空对话历史
        """
        print("""
        LangChain 对话助手
        输入 'exit' 或 'quit' 退出
        输入 'clear' 清空对话历史
        """)

        while True:
            try:
                user_input = input("\n你: ")
            except (EOFError, KeyboardInterrupt):
                print("\n再见！")
                break
            except UnicodeDecodeError:
                # 处理编码异常
                print("输入编码异常，请重新输入")
                continue

            # 清理输入
            user_input = user_input.strip()
            user_input = user_input.encode('utf-8', errors='ignore').decode('utf-8')

            if not user_input:
                continue

            # 退出命令
            if user_input.lower() in ["exit", "quit"]:
                print("再见！")
                break

            # 清空历史命令
            elif user_input.lower() == "clear":
                self.history.clear()
                # 清空后需要重新添加系统提示词
                self.history.add_message(SystemMessage(content=SYSTEM_PROMPT))
                print("对话历史已清空")
                continue

            # 正常对话
            self.chat(user_input)


# ============================================================
# 主程序入口
# ============================================================

if __name__ == "__main__":
    import argparse

    # 命令行参数解析
    parser = argparse.ArgumentParser(description="LangChain 对话助手")
    parser.add_argument(
        "--backend",
        type=str,
        default="openai",
        choices=["ollama", "openai"],
        help="后端类型"
    )
    args = parser.parse_args()

    # 创建客户端并运行
    chat_client = ChatClient(backend=args.backend)
    chat_client.run()