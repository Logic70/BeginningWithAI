# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
