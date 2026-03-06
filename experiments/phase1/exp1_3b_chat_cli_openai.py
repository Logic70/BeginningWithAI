"""
实验 1.3b: OpenAI SDK 对话程序
对比 Ollama 版本，理解 OpenAI 格式的多轮对话管理
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ChatCLI:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
        self.model = os.getenv("OPENAI_MODEL","qwen3.5-plus")
        self.messages = []
        self.system_prompt = """你是一个专业的网络安全助手。""" 

        self.messages.append({
            "role": "system",
            "content": self.system_prompt
        })

    def chat(self, user_input: str) -> str:
        """发送消息并获取响应"""
        # 清理可能的无效 Unicode 字符（WSL 终端中文输入可能产生代理对）
        user_input = user_input.encode('utf-8', errors='ignore').decode('utf-8')
        self.messages.append({
            "role": "user",
            "content": user_input
        })
        
        print("\n助手: ", end="", flush=True)
        full_response = ""
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            stream=True
        )

        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
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
        """运行对话循环"""
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
                print("✅ 对话历史已清空\n")
                continue
            if not user_input.strip():
                continue
            
            self.chat(user_input)

if __name__ == "__main__":
    cli = ChatCLI()
    cli.run()
