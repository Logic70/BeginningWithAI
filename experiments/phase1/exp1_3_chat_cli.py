"""
实验 1.3: 命令行对话程序
支持多轮对话、历史记录、系统提示词
"""
import ollama
from datetime import datetime

class ChatCLI:
    def __init__(self, model: str = "qwen2.5:7b"):
        self.model = model
        self.messages = []
        self.system_prompt = """你是一个专业的网络安全助手。
你精通各类安全技术，包括渗透测试、漏洞分析、安全开发等。
请用简洁专业的语言回答问题。"""
        
        # 添加系统提示词
        self.messages.append({
            "role": "system",
            "content": self.system_prompt
        })
    
    def chat(self, user_input: str) -> str:
        """发送消息并获取响应"""
        # 添加用户消息
        self.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # 调用模型（流式输出）
        print("\n助手: ", end="", flush=True)
        full_response = ""
        stream = ollama.chat(
            model=self.model,
            messages=self.messages,
            stream=True
        )
        for chunk in stream:
            text = chunk["message"]["content"]
            print(text, end="", flush=True)
            full_response += text
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