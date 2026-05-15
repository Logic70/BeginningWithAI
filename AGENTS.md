# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

This is a learning project for a network security engineer to acquire AI/LLM development skills. The project follows a problem-driven learning path across 3 phases:

1. **Phase 1**: Foundation - Local LLM deployment and API usage (Ollama)
2. **Phase 2**: Model Fine-tuning - LoRA/QLoRA with Unsloth for security domain
3. **Phase 3**: Agent Development - Function Calling, ReAct Agent, MCP, Dify workflows, A2A protocol

## Directory Structure

```
AILearningwithAI/
├── docs/                        # Learning documentation
│   ├── learning_plan.md         # Complete learning roadmap
│   ├── phase1_foundation.md     # Phase 1: Local LLM setup
│   ├── phase2_finetuning.md     # Phase 2: Model fine-tuning
│   └── phase3_agent.md          # Phase 3: Agent development
├── experiments/                 # Hands-on code examples
│   ├── phase1/                  # Ollama API, chat CLI
│   ├── phase2/                  # LoRA fine-tuning scripts
│   ├── phase3/                  # Function calling, ReAct agents
│   └── phase4/                  # (planned)
├── data/
│   ├── raw/                     # Raw datasets
│   └── processed/               # Formatted training data
├── models/
│   ├── downloaded/              # Downloaded models
│   └── finetuned/               # Fine-tuned models
├── dify/                        # Dify platform submodule
└── venv/                        # Python virtual environment
```

## Key Commands

```bash
# Activate virtual environment
source venv/Scripts/activate

# Run Phase 1 experiments
python experiments/phase1/exp1_2_api_call.py      # Basic Ollama API
python experiments/phase1/exp1_3_chat_cli.py      # Interactive chat CLI

# Run Phase 3 experiments
python experiments/phase3/exp3_1_function_calling.py  # Tool calling
python experiments/phase3/exp3_2_react_agent.py       # ReAct agent
```

## Architecture Notes

### Ollama API Pattern

The project uses Ollama for local LLM inference. Key API patterns:

```python
# Basic chat
response = ollama.chat(model="qwen2.5:7b", messages=[...])
text = response["message"]["content"]

# Streaming
stream = ollama.chat(model="qwen2.5:7b", messages=[...], stream=True)
for chunk in stream:
    print(chunk["message"]["content"], end="")

# Function Calling
response = ollama.chat(model="qwen2.5:7b", messages=[...], tools=[...])
if response.message.tool_calls:
    for tool_call in response.message.tool_calls:
        func_name = tool_call.function.name
        func_args = tool_call.function.arguments  # Already a dict
```

### Agent Architecture (Phase 3)

- **Function Calling**: Model decides when to call tools based on user query
- **ReAct Agent**: Reasoning + Action loop with Thought/Action/Observation cycle
- Tools are security-focused: port scanning, vulnerability checking, web fingerprinting

### Key Dependencies (in venv)

- `ollama` - Local LLM inference
- `openai` - OpenAI-compatible API client
- `langchain`, `langgraph` - Agent orchestration
- `mcp` - Model Context Protocol SDK
- `python-nmap`, `shodan` - Security scanning tools

## Learning Context

The user is a network security engineer learning AI development. Documentation is in Chinese. The project emphasizes:
- Security domain applications (vulnerability scanning, security Q&A)
- Practical hands-on experiments over theory
- Progressive complexity: API calls → Fine-tuning → Agent development

## 回答质量约束

基于实际交互经验，建立以下约束以确保回答质量：

### 概念层次区分
- **Codex Skill**（提示词模板 + 工作流指令）与 **LangChain Tool / MCP / Function Calling**（可执行函数）是不同层次的概念
- Skill 的本质是"教 AI 怎么做事"，Tool/MCP 的本质是"给 Agent 调用的代码"
- 两者不应混淆，Skill 学习不应混入 Function Calling/MCP 的实现内容

### 文档结构规范
- 章节编号要逻辑连贯，避免跳步（如步骤 2 后直接跳到步骤 5）
- 实现细节的子目录要与前文示例对应
- 引用前文工具时要确保前文已介绍过该工具

### 实现一致性
- 实现方案要与项目已有方法保持一致
- 不要脱离项目上下文自创方法（如 LLM 来源判断逻辑应与既有代码一致）

### 代码验证要求
- 提供的代码必须经过实际验证，确保能正常运行
- 按步骤执行命令时如遇报错必须修复
- 实现要与当前项目结构相符（如路径扫描应从项目根目录开始，而非从子目录）

### 验证完整性
- 验证要执行到底，不能只验证一半
- 非实验关注重点的问题不需要记录，但验证时要给出明确结论
