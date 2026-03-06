"""
实验 1.3c: LangChain 对话程序
用 LangChain 管理对话历史，体验框架的便利性
"""
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
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
            model=os.getenv("OPENAI_MODEL", "qwen3.5-plus"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    raise ValueError(f"未知后端: {backend}")

class ChatClient:
    def __init__(self, backend: str = "openai"):
        self.llm = get_llm(backend)
        self.history = InMemoryChatMessageHistory()
        self.history.add_message(SystemMessage(content=SYSTEM_PROMPT))
    
    def chat(self, user_input: str):
        self.history.add_message(HumanMessage(content=user_input))

        print(f"\n🤖 ({self.llm.model}) 助手: ", end="", flush=True)
        response_content = ""
        for chunk in self.llm.stream(self.history.messages):
            print(chunk.content, end="", flush=True)
            response_content += chunk.content
        print()
        self.history.add_message(AIMessage(content=response_content))
        return response_content

    
    def run(self):
        print("""
        LangChain 对话助手
        输入 'exit' 或 'quit' 退出
        输入 'clear' 清空对话历史
        """)
        while True:
            try:
                user_input = input("\n👤 你: ")
            except (EOFError, KeyboardInterrupt):
                print("\n再见！")
                break
            except UnicodeDecodeError:
                print("⚠️ 输入编码异常，请重新输入")
                continue
            
            user_input = user_input.strip()
            user_input = user_input.encode('utf-8', errors='ignore').decode('utf-8')
            
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("再见！")
                break
            elif user_input.lower() == "clear":
                self.history.clear()
                self.history.add_message(SystemMessage(content=SYSTEM_PROMPT))
                print("对话历史已清空")
                continue
            self.chat(user_input)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LangChain 对话助手")
    parser.add_argument("--backend", type=str, default="openai", choices=["ollama", "openai"], help="后端类型")
    args = parser.parse_args()
    chat_client = ChatClient(backend=args.backend)
    chat_client.run()


