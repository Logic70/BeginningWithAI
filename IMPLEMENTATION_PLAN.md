# Skills 学习实施计划（修订版）

> 创建时间：2026-03-15 | 目标文档：`docs/phase3_agent.md` 实验 3.7-3.8 章节

---

## 背景与目标

基于 `docs/phase3_agent.md` 现有 Skill 章节（实验 3.7-3.8）进行内容增强，引入 **Agent Skills 三层渐进式加载机制** 的完整实现。

**核心改进**：
- 从"Skill = 文档说明"升级到"Skill = 三层渐进式加载机制"
- 结合 `NanmiCoder/skills-agent-proto` 参考实现
- 支持项目既有技术栈：Ollama 本地模型 + OpenAI-compatible 远程 API

**重要区分**（与文档保持一致）：

| 模式 | 本质 | 知识来源 | 适用场景 |
|------|------|----------|----------|
| **Function Calling** | API 协议特性 | JSON Schema（显式） | 生产环境 |
| **MCP** | 工具服务协议 | Server 自动发现 | 工具服务化 |
| **Shell Tool** | 通用 CLI 执行 | 训练数据 + Prompt | 开发探索 |
| **Skill** | 提示词模板 + 渐进式加载 | SKILL.md 指令 | 复杂流程、领域知识 |

---

## 阶段 1：Skill 编写规范学习

**目标**：掌握 SKILL.md 文件结构，理解三层加载机制的设计哲学
**成功标准**：能独立创建符合 Agent Skills 标准的 Skill，并在 Claude Code 中正确触发
**状态**：已完成

### 任务清单

- [x] 阅读 Agent Skills 官方规范（agentskills.io）
- [x] 阅读 `NanmiCoder/skills-agent-proto` 中的 `news-extractor` Skill 示例
- [x] 创建 `.claude/skills/hello-world/SKILL.md`（Hello World 示例）
- [x] 创建 `.claude/skills/port-scanner/SKILL.md`（端口扫描示例）
- [x] 创建 `.claude/skills/security-audit/SKILL.md`（安全审计示例）

### 关键知识点：SKILL.md 格式规范

```yaml
---
name: skill-name                    # 必需：1-64字符，小写/数字/连字符
description: 描述技能和触发条件       # 必需：最多1024字符，说明何时使用
---

# Markdown 格式的指令内容
## 工作流程
...

## 可用脚本
...
```

**目录结构**（与文档一致）：

```
skill-name/
├── SKILL.md          # 必需：YAML frontmatter + Markdown 指令
├── scripts/          # 可选：可执行脚本（Shell Tool 执行）
├── references/       # 可选：参考文档
└── assets/           # 可选：模板和资源
```

### 核心设计哲学：渐进式披露

区别于文档中原有的"Skill = 说明书"理解，引入三层加载机制：

| 层级 | 内容 | 加载时机 | Token 消耗 | 类比 |
|------|------|----------|------------|------|
| **Level 1** | name + description（YAML frontmatter） | 启动时 | ~100 tokens/Skill | 书籍目录 |
| **Level 2** | SKILL.md 完整指令（Markdown body） | Skill 触发时 | <5000 tokens | 章节内容 |
| **Level 3** | 脚本执行结果（scripts/ 输出） | 运行时 | 仅输出入上下文 | 代码运行结果 |

> **设计原则**：让大模型成为真正的"智能体"，自己阅读指令、发现脚本、决定执行。代码层面不需要特殊处理脚本发现/执行逻辑。

---

## 阶段 2：Agent Skills 支持实现

**目标**：在既有 Agent 框架中实现 Skill 发现、加载和激活机制
**成功标准**：Agent 能自动发现 Skills，按三层机制加载，支持 Ollama 和远程 API 切换
**状态**：已完成

### 技术栈适配说明

本项目既有代码已实现双模式支持（参见 `exp3_1_function_calling.py` 和 `exp3_1b_function_calling_api.py`）：

```bash
# 模式 1：Ollama 本地模型
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# 模式 2：OpenAI-compatible 远程 API
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.example.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

Skills Agent 实现将参考 `NanmiCoder/skills-agent-proto`，保持相同的多 Provider 支持能力。

### 任务清单

#### 2.1 SkillLoader 实现（Level 1）

参考 `skill_loader.py` 实现：

- [x] `scan_skills()` - 扫描 `.claude/skills/` 目录（项目级 + 用户级）
- [x] `_parse_skill_metadata()` - 解析 YAML frontmatter 提取 name/description
- [x] `build_system_prompt()` - 将 Skills 元数据注入 System Prompt

**输出示例**：
```
## Available Skills

You have access to the following specialized skills:

- **security-audit**: 对代码进行安全审计，检查 SQL 注入、XSS 等漏洞
- **port-scanner**: 扫描目标主机端口开放情况

### How to Use Skills
1. **Discover**: Review the skills list above
2. **Load**: When a user request matches a skill's description, use `load_skill(skill_name)`
3. **Execute**: Follow the skill's instructions, which may include running scripts via `bash`
```

#### 2.2 load_skill Tool 实现（Level 2）

- [x] 实现 `load_skill(skill_name: str)` 工具函数
- [x] 读取 SKILL.md 完整内容（去除 frontmatter，返回 Markdown body）
- [x] 附加脚本路径信息，供模型后续调用

**关键设计**：只返回 instructions，让大模型从指令中自己发现脚本和文档（Anthropic Skills 核心设计理念）。

#### 2.3 bash Tool 实现（Level 3）

- [x] 实现 `bash(command: str)` 工具函数
- [x] 支持脚本执行（如 `python scripts/audit.py --target ./src`）
- [x] 输出格式：`[OK]` / `[FAILED]` 前缀标识执行状态
- [x] 脚本代码不进入上下文，仅输出入上下文

#### 2.4 AgentWithSkills 集成

- [x] 实现 `SkillsAgent` 类（基于既有 ReAct Agent 扩展）
- [x] 集成 SkillLoader 到 System Prompt 构建流程
- [x] 注册 `load_skill` 和 `bash` 工具到 Tool Map
- [x] 支持 Ollama 本地模型模式
- [x] 支持 OpenAI-compatible 远程 API 模式
- [x] 编写 CLI 测试脚本验证三层加载机制

### 参考实现

| 源文件 | 功能 | 本项目适配点 |
|--------|------|--------------|
| `skill_loader.py` | Skills 发现、解析、加载 | 直接使用，适配 Ollama System Prompt 格式 |
| `tools.py` | `load_skill`, `bash` 等工具 | 保持工具定义，适配项目既有 Tool Map 机制 |
| `agent.py` | LangChain Agent 集成 | 参考多 Provider 配置逻辑，整合到既有 Agent |

---

## 阶段 3：文档更新（`docs/phase3_agent.md`）

**目标**：更新实验 3.7-3.8 章节，引入三层加载机制内容
**成功标准**：文档清晰说明 Skill 概念、实现方法和与既有技术的对比
**状态**：已完成

### 文档结构规划

#### 实验 3.7：Skill 编写与三层加载机制

**新增/修改内容**：

1. **什么是 Skill**（更新）
   - 保留原有"Skill = 领域知识 + 工作流程 + 工具脚本的封装"
   - 补充：Skill 的核心理念是**渐进式披露**（Progressive Disclosure）
   - 补充三层加载表格（Level 1/2/3）

2. **Skill 工作原理**（更新）
   - 保留原有流程图
   - 补充三层加载的详细说明：
     - Level 1：启动时 `scan_skills()` 扫描，元数据注入 System Prompt
     - Level 2：触发时 `load_skill` 工具读取 SKILL.md 完整指令
     - Level 3：执行时 `bash` 工具运行脚本，代码不进上下文

3. **SKILL.md 格式规范**（保留并补充）
   - 保留原有结构说明
   - 补充 frontmatter 字段规范（name, description, argument-hint 等）
   - 补充变量替换机制（`$ARGUMENTS`, `$0`, `${CLAUDE_SKILL_DIR}`）

4. **三层加载演示**（新增）
   - Level 1 验证：`--list-skills` 查看发现的 Skills
   - Level 2 验证：观察 `load_skill` 工具调用
   - Level 3 验证：观察 `bash` 工具执行脚本

#### 实验 3.8：Agent Skills 支持实现

**新增/修改内容**：

1. **实现 SkillLoader**（新增）
   - 代码示例：`SkillMetadata`, `SkillContent` dataclass
   - 代码示例：`scan_skills()`, `load_skill()`, `build_system_prompt()`

2. **实现 load_skill 和 bash 工具**（新增）
   - 工具函数代码示例
   - 与既有 Tool Map 集成方式

3. **集成到 Agent**（新增）
   - 参考 `NanmiCoder/skills-agent-proto` 的 `agent.py`
   - 适配既有双模式（Ollama/API）配置

4. **与既有技术对比**（保留并更新）
   - 保留原有对比表格
   - 补充：Skill 的三层加载 vs MCP 的自动发现 vs Function Calling 的显式定义

### 工具调用模式总结（文档末尾章节）更新

更新对比表格，补充 Skill 的三层加载特性：

| | Function Calling | MCP | Shell Tool | **Skill** |
|---|------------------|-----|------------|-----------|
| **是什么** | API 协议特性 | 工具服务协议 | 通用 CLI 执行 | **渐进式指令加载** |
| **知识来源** | JSON Schema（显式）| Server 自动发现 | 预训练知识 + Prompt | **SKILL.md 三层披露** |
| **新增工具成本** | 写代码封装 | 写 MCP Server | 零（CLI 已存在） | **写文档** |
| **Token 效率** | ⭐⭐⭐ 高 | ⭐⭐⭐ 高 | ⭐⭐⭐ 高 | **⭐⭐⭐ 高（按需加载）** |
| **适用场景** | 生产环境 | 工具服务化 | 开发探索 | **复杂流程、领域知识** |

---

## 文件清单

| 文件 | 用途 | 状态 | 参考来源 |
|------|------|------|----------|
| `.claude/skills/hello-world/SKILL.md` | Hello World Skill 示例 | 已完成 | 原创 |
| `.claude/skills/port-scanner/SKILL.md` | 端口扫描 Skill 示例 | 已完成 | 原创 |
| `.claude/skills/security-audit/SKILL.md` | 安全审计 Skill 示例 | 已完成 | 原创 |
| `experiments/phase3/exp3_7_skill_loader.py` | Skill 加载器（Level 1/2） | 已完成 | 参考 skill-agent-proto |
| `experiments/phase3/exp3_7b_skills_agent.py` | 支持 Skills 的 Agent（双模式） | 已完成 | 参考 skill-agent-proto |
| `experiments/phase3/exp3_7c_skills_cli.py` | Skills Agent CLI 交互 | 已完成 | 原创 |
| `docs/phase3_agent.md` | 更新实验 3.7-3.8 章节 | 已完成 | 原创 |

---

## 验证方法

### 阶段 1 验证（Claude Code 环境）

```bash
# 在 Claude Code 中测试 Skill 自动触发
/security-audit experiments/phase1/exp1_2_api_call.py
```

### 阶段 2 验证（既有双模式）

```bash
# 模式 1：Ollama 本地模型
python experiments/phase3/exp3_7b_skills_agent.py

# 模式 2：远程 API 模式
export OPENAI_API_KEY=sk-xxx
export OPENAI_BASE_URL=https://api.example.com/v1
python experiments/phase3/exp3_7b_skills_agent.py
```

### 阶段 3：三层加载机制验证

```bash
# Level 1：启动时元数据加载
python experiments/phase3/exp3_7c_skills_cli.py --list-skills

# Level 2：触发时指令加载
# 观察 agent 是否调用 load_skill 工具获取完整指令

# Level 3：运行时脚本执行
# 观察 bash 工具执行脚本，确认脚本代码不进上下文
```

---

## 参考资源

### Agent Skills 标准
- [Agent Skills 开放标准](https://agentskills.io) - 官方规范
- [Adding Skills Support 指南](https://agentskills.io/client-implementation/adding-skills-support) - 客户端实现指南
- [Claude Code Skills 文档](https://code.claude.com/docs/en/skills) - Claude Code 官方文档

### 参考实现
- [NanmiCoder/skills-agent-proto](https://github.com/NanmiCoder/skills-agent-proto) - LangChain 1.0 实现的三层加载机制演示
  - `src/langchain_skills/skill_loader.py` - Skills 发现与加载（Level 1/2）
  - `src/langchain_skills/tools.py` - `load_skill` / `bash` 工具
  - `src/langchain_skills/agent.py` - Agent 集成与流式输出
  - `.claude/skills/news-extractor/SKILL.md` - 完整 Skill 示例
  - 支持 Anthropic/OpenAI 双 Provider 切换

### 项目既有代码（技术栈确认）
- `experiments/phase3/exp3_1_function_calling.py` - Ollama Function Calling
- `experiments/phase3/exp3_1b_function_calling_api.py` - OpenAI API Function Calling
- `experiments/phase3/exp3_2_react_agent.py` - ReAct Agent 实现
- `experiments/phase3/exp3_4c_mcp_langchain_agent.py` - LangChain Agent 框架

### 文档上下文
- `docs/phase3_agent.md` 实验 3.7-3.8 - 既有 Skill 章节（待更新）
- `docs/phase3_agent.md` 工具调用模式总结 - 既有对比表格（待更新）
