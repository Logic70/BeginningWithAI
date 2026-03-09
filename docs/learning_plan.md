# 📚 AI 技术完整学习计划

> 面向网络安全工程师的问题驱动式 AI 实践学习路径

---

## 🎯 学习目标

通过 10-14 周的系统学习，掌握以下能力：

| 能力领域 | 目标描述 | 对应阶段 |
|----------|----------|----------|
| 本地模型运维 | 能够本地部署、调用、管理开源LLM | 阶段一 |
| 多后端接入 | 掌握 Ollama 本地 + OpenAI API Key 云端双模式 | 阶段一/三 |
| LangChain 实践 | 理解原生实现后，用 LangChain 掌握最佳实践 | 阶段一/三 |
| 模型微调 | 能够针对特定领域进行 LoRA 微调 | 阶段二 |
| Agent 开发 | 能够开发 Agent、MCP Server、Skill | 阶段三 |
| 工作流编排 | 使用 Dify 平台可视化编排 Agent 工作流 | 阶段三 |
| 多 Agent 协作 | 掌握 A2A 协议实现 Agent 间通信与协作 | 阶段三 |

---

## 📅 时间规划

| 阶段 | 内容 | 起止时间 | 周期 |
|------|------|----------|------|
| 阶段一 | 基础认知与环境搭建 | 02/09 - 02/22 | 2 周 |
| 阶段二 | 模型微调与后训练 | 02/23 - 03/22 | 4 周 |
| 阶段三 | Agent / Dify / A2A 开发 | 03/23 - 05/17 | 8 周 |

```
02/09       02/23       03/23                          05/17
  |--阶段一--|---阶段二----|----------阶段三--------------|
  ├ 基础认知  ├ 模型微调    ├ Agent/MCP  ├ Dify   ├ A2A
  └ 环境搭建  └ 后训练      └ Skill      └ 工作流  └ 多Agent协作
```

---

## 阶段一：基础认知与环境搭建（1-2周）

### 🎯 核心问题
> "如何在本地运行一个开源大语言模型？"

### 📋 任务清单
1. **环境搭建**：安装 Ollama、Python 环境
2. **模型运行**：本地运行 Llama 3.2 / Qwen 模型
3. **API 调用**：使用 Python 调用本地模型
4. **项目输出**：完成命令行对话程序

### 📖 理论知识
- Transformer 架构原理
- Token、Embedding、Context Window 概念
- 模型量化基础（GGUF、GGML）

### 📎 实验指导
详见 [阶段一实验指导](phase1_foundation.md)

---

## 阶段二：模型微调与后训练（3-4周）

### 🎯 核心问题
> "如何让模型在特定任务上表现得更专业？"

### 📋 任务清单
1. **原理学习**：LoRA / QLoRA / PEFT 原理
2. **数据准备**：安全领域数据集制作
3. **微调实践**：使用 Unsloth 进行微调
4. **模型评估**：评估指标与对比分析
5. **模型部署**：量化导出与本地部署

### 📖 理论知识
- 参数高效微调（PEFT）原理
- LoRA 数学原理与实现
- 训练数据格式（Alpaca、ShareGPT）
- 模型量化技术

### 📎 实验指导
详见 [阶段二实验指导](phase2_finetuning.md)

---

## 阶段三：Agent、Dify 与 A2A 开发（6-8周）

### 🎯 核心问题
> "如何让模型调用工具、编排工作流、实现多 Agent 协作？"

### 📋 任务清单
1. **Function Calling**：工具调用机制实现
2. **Agent 架构**：ReAct、Plan-and-Execute 模式
3. **MCP 开发**：Model Context Protocol 服务开发
4. **Skill 开发**：AI 编码助手扩展开发
5. **Dify 工作流**：平台部署与可视化 Agent 编排
6. **A2A 协议**：Agent 间通信与多 Agent 协作
7. **综合项目**：自动化安全 Agent

### 📖 理论知识
- Agent 架构设计模式
- MCP 协议规范
- Dify 工作流编排与 Agent 节点
- A2A 协议（Agent Card、JSON-RPC 2.0）
- LangGraph 工作流设计
- 安全工具集成

### 📎 实验指导
详见 [阶段三实验指导](phase3_agent.md)

---

## 🛠️ 开发环境要求

### 硬件要求
| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| GPU | 8GB VRAM（如 RTX 3070） | 16GB+ VRAM（如 RTX 4080） |
| RAM | 16GB | 32GB+ |
| 存储 | 100GB SSD | 500GB NVMe SSD |

### 软件环境
- **操作系统**: Windows 11 / Ubuntu 22.04
- **Python**: 3.10+
- **CUDA**: 11.8+ (用于 GPU 加速)
- **Docker**: 可选，用于服务部署
- **API Key**: 可选，OpenAI 或兼容平台的 API Key（用于云端模型调用）
- **LangChain**: `langchain`, `langchain-openai`, `langchain-ollama`（对比学习用）

---

## 📚 推荐资源

### 视频教程
- [Andrej Karpathy - Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY)
- [3Blue1Brown - 神经网络可视化](https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi)

### 官方文档
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [LangChain 文档](https://python.langchain.com/docs)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Anthropic MCP 规范](https://modelcontextprotocol.io/)
- [Dify 官方文档](https://docs.dify.ai/)
- [Google A2A 协议](https://github.com/google/A2A)

### 实践平台
- [Ollama](https://ollama.com/)
- [LM Studio](https://lmstudio.ai/)
- [Unsloth](https://github.com/unslothai/unsloth)
- [Dify](https://github.com/langgenius/dify)

---

## 📊 学习产出清单

| 阶段 | 产出物 | 描述 |
|------|--------|------|
| 一 | `chat_cli.py` | 命令行对话程序 |
| 二 | `security_qa_model/` | 安全问答微调模型 |
| 三 | `security_agent/` | 自动化安全测试 Agent |
| 三 | `dify_security_workflow` | Dify 安全分析工作流 |
| 三 | `a2a_multi_agent/` | A2A 多 Agent 协作系统 |
