"""
实验 3.2: ReAct Agent
推理与行动交替进行
支持 Ollama 本地模型和 OpenAI 兼容 API 两种后端
"""
import os
import ollama
import json
import re
from typing import Dict, Callable, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ReActAgent:

    def __init__(self, model: str = "qwen2.5:7b", max_iterations: int = 5, backend: str = "ollama"):
        self.model = model
        self.max_iterations = max_iterations
        self.backend = backend
        self.tools: Dict[str, Callable] = {}
        self.tool_descriptions: List[str] = []
        self.messages = []

        # OpenAI 后端初始化
        if self.backend == "openai":
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),
            )
        else:
            self.client = ollama.Client(
                host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            )

    def add_tool(self, name: str, func: Callable, description: str):
        """添加工具"""
        self.tools[name] = func
        self.tool_descriptions.append(f"- {name}: {description}")

    def _get_tools_prompt(self)->str:
        """获取工具描述"""
        return "\n".join(self.tool_descriptions)

    def _parse_response(self,response:str)->Dict[str,str]:
        """解析模型响应"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"action":"final_answer","answer":response}

    def _create_prompt(self, task: str, history: str = "") -> str:
        """创建提示词"""
        tools_str = "\n".join(self.tool_descriptions)
        
        return f"""你是一个安全分析助手。你需要通过推理和使用工具来完成任务。

可用工具:
{tools_str}

使用格式:
Thought: [你的思考过程]
Action: [工具名称]
Action Input: [JSON格式的参数]

当你得到结果后，继续思考。如果任务完成，使用:
Thought: [最终总结]
Final Answer: [最终答案]

{history}
任务: {task}

开始:"""
    
    def _parse_response(self, response: str) -> dict:
        """解析响应"""
        result = {
            "thought": "",
            "action": None,
            "action_input": None,
            "final_answer": None
        }
        
        # 提取 Thought
        thought_match = re.search(r"Thought:\s*(.+?)(?=Action:|Final Answer:|$)", response, re.DOTALL)
        if thought_match:
            result["thought"] = thought_match.group(1).strip()
        
        # 提取 Final Answer
        final_match = re.search(r"Final Answer:\s*(.+)", response, re.DOTALL)
        if final_match:
            result["final_answer"] = final_match.group(1).strip()
            return result
        
        # 提取 Action
        action_match = re.search(r"Action:\s*(\w+)", response)
        if action_match:
            result["action"] = action_match.group(1)
        
        # 提取 Action Input
        input_match = re.search(r"Action Input:\s*(\{.+?\})", response, re.DOTALL)
        if input_match:
            try:
                result["action_input"] = json.loads(input_match.group(1))
            except json.JSONDecodeError:
                pass
        
        return result
    
    def run(self, task: str) -> str:
        """运行 Agent"""
        history = ""
        
        for i in range(self.max_iterations):
            print(f"\n--- 迭代 {i+1} ---")
            
            # 生成响应
            prompt = self._create_prompt(task, history)

            if self.backend == "ollama":
                response = self.client.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                    
                )
                response_text = response["message"]["content"]
            else:
                # OpenAI 兼容 API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = response.choices[0].message.content
            parsed = self._parse_response(response_text)
            
            print(f"Thought: {parsed['thought']}")
            
            # 检查是否结束
            if parsed["final_answer"]:
                print(f"Final Answer: {parsed['final_answer']}")
                return parsed["final_answer"]
            
            # 执行工具
            if parsed["action"] and parsed["action"] in self.tools:
                print(f"Action: {parsed['action']}")
                print(f"Action Input: {parsed['action_input']}")
                
                try:
                    result = self.tools[parsed["action"]](**parsed["action_input"])
                    observation = json.dumps(result, ensure_ascii=False)
                except Exception as e:
                    observation = f"Error: {str(e)}"
                
                print(f"Observation: {observation}")
                
                # 更新历史
                history += f"""
Thought: {parsed['thought']}
Action: {parsed['action']}
Action Input: {json.dumps(parsed['action_input'], ensure_ascii=False)}
Observation: {observation}
"""
            else:
                print("无有效行动，继续思考...")
                history += f"\nThought: {parsed['thought']}\n"
        
        return "达到最大迭代次数，任务未完成。"


# 工具函数
def port_scan(host: str, ports: list) -> dict:
    """端口扫描"""
    import socket
    results = {}
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            results[port] = "open" if result == 0 else "closed"
            sock.close()
        except:
            results[port] = "error"
    return {"host": host, "ports": results}


def web_fingerprint(url: str) -> dict:
    """Web 指纹识别（模拟）"""
    return {
        "url": url,
        "server": "nginx/1.18.0",
        "technologies": ["PHP", "MySQL"],
        "cms": "unknown"
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ReAct Agent")
    parser.add_argument("--backend", choices=["ollama", "openai"], default="ollama")
    args = parser.parse_args()

    # 根据后端选择模型
    if args.backend == "openai":
        model = os.getenv("OPENAI_MODEL", "qwen3.5-plus")
    else:
        model = "qwen2.5:7b"

    # 创建 Agent
    agent = ReActAgent(model=model, backend=args.backend)
    print(f"后端: {args.backend}，模型: {model}\n")

    # 注册工具
    agent.add_tool(
        "port_scan",
        port_scan,
        "扫描目标主机的端口。参数: host(str), ports(list[int])"
    )
    agent.add_tool(
        "web_fingerprint",
        web_fingerprint,
        "识别Web服务的技术栈。参数: url(str)"
    )
    
    # 运行任务
    task = "分析 localhost 的安全状况，扫描常用端口(80, 443, 22, 3306)并识别Web技术栈"
    result = agent.run(task)
    
    print(f"\n{'='*60}")
    print(f"最终结果: {result}")
