"""
实验 3.2: ReAct Agent（手写实现）
推理（Reasoning）与行动（Acting）交替进行的 Agent 模式

ReAct 核心理念：
  - Thought（思考）：LLM 分析当前情况，决定下一步
  - Action（行动）：执行工具调用
  - Observation（观察）：获取工具结果
  - 循环直到得出最终答案

执行流程：
  ┌─────────────────────────────────────────────────────────────┐
  │ 用户任务: "分析 localhost 的安全状况"                         │
  └─────────────────────────────────────────────────────────────┘
                              ↓
  ┌─────────────────────────────────────────────────────────────┐
  │ Thought: 我需要先扫描常用端口来了解开放的服务...              │
  │ Action: port_scan                                           │
  │ Action Input: {"host": "localhost", "ports": [80, 443, 22]} │
  └─────────────────────────────────────────────────────────────┘
                              ↓
  ┌─────────────────────────────────────────────────────────────┐
  │ Observation: {"host": "localhost", "ports": {80: "open"}}   │
  └─────────────────────────────────────────────────────────────┘
                              ↓
  ┌─────────────────────────────────────────────────────────────┐
  │ Thought: 发现 80 端口开放，接下来检查 Web 技术栈...          │
  │ Action: web_fingerprint                                     │
  │ Action Input: {"url": "http://localhost"}                   │
  └─────────────────────────────────────────────────────────────┘
                              ↓
  ┌─────────────────────────────────────────────────────────────┐
  │ Observation: {"server": "nginx", "technologies": ["PHP"]}   │
  └─────────────────────────────────────────────────────────────┘
                              ↓
  ┌─────────────────────────────────────────────────────────────┐
  │ Thought: 已完成分析，可以给出结论...                         │
  │ Final Answer: localhost 运行 nginx + PHP，80 端口开放...    │
  └─────────────────────────────────────────────────────────────┘

与 Function Calling 的区别：
  - Function Calling：模型直接返回结构化的工具调用
  - ReAct：模型输出自然语言格式的思考和行动，需要解析
"""

# ==================== 导入 ====================
import os
import ollama
# ollama: Ollama 官方 SDK

import json
# json: 解析 Action Input 参数

import re
# re: 正则表达式，解析模型输出的 Thought/Action/Final Answer

from typing import Dict, Callable, List
# 类型注解

from openai import OpenAI
# OpenAI: 用于 OpenAI 兼容 API 后端

from dotenv import load_dotenv
# 加载环境变量

# ==================== 配置 ====================
load_dotenv()


# ============================================================
# 核心类：ReActAgent
# ============================================================

class ReActAgent:
    """
    ReAct Agent 实现

    核心组件：
    1. 工具注册表：存储可用工具
    2. 提示词模板：引导模型输出 ReAct 格式
    3. 响应解析器：从模型输出中提取 Thought/Action/Final Answer
    4. 执行循环：迭代执行直到得出最终答案
    """

    def __init__(
        self,
        model: str = "qwen2.5:7b",
        max_iterations: int = 5,
        backend: str = "ollama"
    ):
        """
        初始化 Agent

        Args:
            model: 使用的模型名称
            max_iterations: 最大迭代次数（防止无限循环）
            backend: 后端类型，"ollama" 或 "openai"
        """
        self.model = model
        self.max_iterations = max_iterations
        self.backend = backend

        # 工具存储
        self.tools: Dict[str, Callable] = {}
        # 工具名 → 函数映射

        self.tool_descriptions: List[str] = []
        # 工具描述列表，用于构建提示词

        # 对话历史
        self.messages = []

        # 根据后端初始化客户端
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
        """
        注册工具

        Args:
            name: 工具名称
            func: 工具函数
            description: 工具描述（包含参数说明）
        """
        self.tools[name] = func
        self.tool_descriptions.append(f"- {name}: {description}")

    def _get_tools_prompt(self) -> str:
        """获取工具描述字符串"""
        return "\n".join(self.tool_descriptions)

    def _create_prompt(self, task: str, history: str = "") -> str:
        """
        创建 ReAct 格式的提示词

        提示词结构：
        1. 角色定义
        2. 工具列表
        3. 输出格式说明
        4. 历史记录（之前的 Thought/Action/Observation）
        5. 当前任务

        Args:
            task: 用户任务
            history: 之前的执行历史
        """
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
        """
        解析模型响应

        从自然语言输出中提取结构化信息：
        - thought: 思考过程
        - action: 要执行的工具
        - action_input: 工具参数
        - final_answer: 最终答案

        Args:
            response: 模型的原始输出

        Returns:
            dict: 解析后的结构化数据
        """
        result = {
            "thought": "",
            "action": None,
            "action_input": None,
            "final_answer": None
        }

        # 使用正则表达式提取各部分
        # 提取 Thought（思考过程）
        thought_match = re.search(
            r"Thought:\s*(.+?)(?=Action:|Final Answer:|$)",
            response,
            re.DOTALL
        )
        if thought_match:
            result["thought"] = thought_match.group(1).strip()

        # 提取 Final Answer（最终答案）
        final_match = re.search(
            r"Final Answer:\s*(.+)",
            response,
            re.DOTALL
        )
        if final_match:
            result["final_answer"] = final_match.group(1).strip()
            return result  # 有最终答案，直接返回

        # 提取 Action（工具名称）
        action_match = re.search(r"Action:\s*(\w+)", response)
        if action_match:
            result["action"] = action_match.group(1)

        # 提取 Action Input（工具参数）
        input_match = re.search(
            r"Action Input:\s*(\{.+?\})",
            response,
            re.DOTALL
        )
        if input_match:
            try:
                result["action_input"] = json.loads(input_match.group(1))
            except json.JSONDecodeError:
                pass

        return result

    def run(self, task: str) -> str:
        """
        运行 Agent 执行任务

        执行流程：
        1. 构建提示词
        2. 调用模型获取响应
        3. 解析响应
        4. 如果有 Action，执行工具
        5. 将结果加入历史
        6. 重复直到得到 Final Answer 或达到最大迭代次数

        Args:
            task: 用户任务

        Returns:
            str: 最终答案
        """
        history = ""

        for i in range(self.max_iterations):
            print(f"\n--- 迭代 {i+1} ---")

            # 构建提示词
            prompt = self._create_prompt(task, history)

            # 调用模型
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

            # 解析响应
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
                    # 执行工具函数
                    result = self.tools[parsed["action"]](**parsed["action_input"])
                    observation = json.dumps(result, ensure_ascii=False)
                except Exception as e:
                    observation = f"Error: {str(e)}"

                print(f"Observation: {observation}")

                # 更新历史记录
                # 这一步很重要：让模型知道之前做了什么
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


# ============================================================
# 工具函数
# ============================================================

def port_scan(host: str, ports: list) -> dict:
    """
    端口扫描工具

    Args:
        host: 目标主机
        ports: 端口列表

    Returns:
        dict: 每个端口的状态
    """
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
    """
    Web 指纹识别工具（模拟）

    实际应用中应调用真实工具如 Wappalyzer
    """
    return {
        "url": url,
        "server": "nginx/1.18.0",
        "technologies": ["PHP", "MySQL"],
        "cms": "unknown"
    }


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ReAct Agent")
    parser.add_argument(
        "--backend",
        choices=["ollama", "openai"],
        default="ollama"
    )
    args = parser.parse_args()

    # 根据后端选择模型
    if args.backend == "openai":
        model = os.getenv("OPENAI_MODEL", "deepseek-v4-pro")
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