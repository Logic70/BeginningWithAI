# 阶段三：现代 Agent Runtime、Workflow 与系统集成

> 预计时间：6-8 周 | 核心问题：当前主流 Agent 工具如何通过软编排、能力调用、多 Agent 协作与系统集成完成真实任务？

---

## 🎯 阶段目标

完成本阶段后，你将能够：

- ✅ 拆解 Claude Code / OpenCode / OpenClaw 一类现代 Agent 工具的运行链路
- ✅ 理解能力实现、软编排、显式 Workflow 与系统集成之间的边界
- ✅ 实现最小单 Agent，并把工具接入、任务约束、结果验收串起来
- ✅ 设计和实现多 Agent Workflow，明确角色拆分、handoff 与聚合方式
- ✅ 在必要时使用 LangGraph 进行显式状态管理、路由与中断恢复
- ✅ 理解 MCP、A2A、Dify / 业务流程骨架在系统集成中的位置
- ✅ 构建一个面向安全分析场景的综合 Agent 系统

---

## 📘 专项课程

- [Claude Code 风格 Code Agent Runtime 课程设计](D:/Code/BeginningWithAI/docs/claude_code_agent_runtime_course.md)

这门专项课程补齐现代 code agent 的核心运行时能力：Subagent、Coordinator / Worker、Agent Team、Hook、Instruction / Permission、Context / Memory、Internal/System Agent、Runtime Reliability。它是 3.11 多 Agent 章节的深化，不替代 Function Calling、MCP、Skill 和 LangGraph 的基础实验。

---

## 🧭 如何使用本章

- 本章正文继续保留原实验编号，便于与你现有代码文件一一对应。
- 推荐学习顺序**不按实验编号线性推进**，而按下面的 5 个阶段执行。
- 每个阶段都要求同时完成两件事：**拆结构** 和 **写代码 / 跑实验**。
- 每个阶段都要明确 4 件事：任务输入、可用能力、输出格式、完成条件。

### 五阶段学习主线

#### 阶段 1：看懂现有 Agent 工具（代码 + 结构）

**核心问题**：Claude Code / OpenCode / OpenClaw 这类工具，到底是怎么把自然语言任务变成可执行循环的？

**学习重点**：
- Agent loop：上下文组装、模型决策、工具执行、结果回填
- Function Calling / MCP / Skill 在运行时中的角色
- rules / commands / skills / subagents 这些软编排资产分别解决什么问题

**推荐先读 / 先跑**：
- 「Agent 底层逻辑概览」
- 实验 3.1：Function Calling 基础
- 实验 3.4-3.6：MCP Server 开发
- 实验 3.7：Skill 编写基础
- 实验 3.8：Skills Agent 实现

**阶段产出**：
- 画出一张现代 coding agent 的运行链路图
- 跑通一个最小“模型决策 -> 工具执行 -> 结果回填”的示例

#### 阶段 2：自己实现最小单 Agent

**核心问题**：如果不依赖完整平台，怎样自己做出一个能工作的单 Agent？

**学习重点**：
- 单 Agent loop
- 任务约束：输入、输出、完成条件
- 结果验收：格式检查、必要测试、复核步骤
- 把 Function Calling、Skill、MCP 组合进单 Agent

**推荐先读 / 先跑**：
- 实验 3.2：Prompt 核心价值与 LCEL
- 实验 3.3：ReAct Agent 实现
- 专题 3.3x：Reasoning Trace、思维链与 ReAct Scratchpad
- 实验 3.2b：最小 Guarded Single Agent（任务契约 + 结果校验 + 修复重试）
- 实验 3.8：Skills Agent 实现
- 实验 3.9：高级 Skill 编写（Security Audit）
- 实验 3.13：生产化实践（重点读 Eval / 可观测性 / 错误恢复）

**阶段产出**：
- 一个能完成“扫描 -> 分析 -> 报告”的单 Agent 原型
- 明确这个 Agent 的输入、能力边界、输出格式和验收方式

#### 阶段 3：多 Agent Workflow

**核心问题**：什么时候单 Agent 不够？多 Agent 应该怎么拆才合理？

**学习重点**：
- planner / worker / reviewer
- supervisor / specialists
- context 隔离、handoff、结果聚合
- 多 Agent 失败模式：重复劳动、上下文丢失、循环委派、职责重叠

**推荐先读 / 先跑**：
- 实验 3.11：多 Agent 编排模式
- 实验 3.11c：OpenAI SDK 版主 Agent + Subagent Runtime
- 实验 3.11d：OpenAI SDK 版 Coordinator / Worker Runtime
- 实验 3.11e：OpenAI SDK 版 Agent Team Runtime
- 实验 3.11f：OpenAI SDK 版 Hook Control Plane Runtime
- 实验 3.11g：OpenAI SDK 版 Instruction / Permission Runtime
- 实验 3.11h：OpenAI SDK 版 Context / Memory Runtime
- 实验 3.11i：OpenAI SDK 风格 Internal / System Agent Runtime
- 实验 3.13b：OpenAI SDK 风格 Runtime Reliability
- 实验 3.13：生产化实践（重点读评估与可观测性）

**阶段产出**：
- 一个多 Agent 安全分析 workflow
- 一份单 Agent 与多 Agent 的选型说明

#### 阶段 4：显式 Workflow

**核心问题**：软编排什么时候不够？什么时候值得把流程显式写成状态图？

**学习重点**：
- 显式状态
- 条件路由
- interrupt / checkpoint / resume
- 用显式 Workflow 解决人工确认、恢复执行、复杂分支

**推荐先读 / 先跑**：
- 实验 3.10：LangGraph 工作流编排

**阶段产出**：
- 把一个已有软编排任务改写成显式 Workflow
- 能清楚说明为什么这里需要 LangGraph，而不是继续只靠自然语言编排

#### 阶段 5：跨系统协议与业务集成

**核心问题**：Agent 怎么接入更大的系统，而不是只停留在本地对话？

**学习重点**：
- MCP：能力协议
- A2A：跨 Agent / 跨 Runtime 协议
- Dify / 业务流程骨架：外层业务流程集成
- 综合项目中的系统分层：外层流程、中层 Agent、内层能力

**推荐先读 / 先跑**：
- 实验 3.12：A2A 协议与 Agent 互操作
- 实验 3.14：综合项目 — 安全评估平台
- 附录 A：Dify 可视化编排

**阶段产出**：
- 一个“外层流程 + 中层 Agent + 内层能力”的系统原型
- 说明 MCP、A2A、Dify / 业务流程骨架分别适合放在哪一层

### 贯穿要求

- 不把“能力实现”和“编排逻辑”混为一谈
- 不把“软编排”和“权限 / hook / sandbox”等控制面混为一谈
- 每个实验都要写清楚：输入是什么、能调用什么、输出必须长什么样、怎样算完成
- 每个阶段至少产出一份能运行的代码和一份结构理解说明

---

## 🧭 Claude Code 核心能力补充学习线

本节补充的是“现代 code agent 的核心能力层”，资料来源分成两类：

- **官方功能边界**：以 Claude Code 官方文档为准，包括 Subagents、Agent Teams、Hooks、Memory、Settings / Permissions、Skills。
- **工程实现线索**：以 [pengchengneo/Claude-Code](https://github.com/pengchengneo/Claude-Code) 的源码还原文档为主要参考，重点只取 code agent 核心能力，不展开宠物、语音、贴纸等旁支功能。

### 为什么要补这一节

前面的 3.11 主要讲了两个教学模型：

- `exp3_11b_multi_agent_openai.py`：固定角色 Team，重点是 `scanner -> analyzer -> reporter` 这种共享 state 调度。
- `exp3_11c_subagent_runtime_openai.py`：主 Agent 临时委派子任务，重点是 `primary -> subagent -> result` 这种父子 session。

但 Claude Code 这类真实 code agent 的核心能力不止这两层。官方文档和源码还原材料显示，完整能力至少还包括：

- 权限与隔离：工具能不能调用、文件能不能读写、危险操作如何拦截。
- 指令加载：`CLAUDE.md`、`.claude/rules/`、skills、subagent prompt 分别进入上下文的时机不同。
- Hook 生命周期：不是简单“执行脚本”，而是贯穿 session、tool use、compact、task、subagent、worktree 的控制面。
- Agent Team：不是普通 subagent，而是有 shared task list、mailbox、teammate、team config 的协作运行时。
- 记忆与持久化：不只是当前 messages，还包括 project memory、agent memory、session transcript、后台整合与长期任务。

### 资料对照表

| 能力层 | 官方文档锚点 | `pengchengneo/Claude-Code` 线索 | 本项目学习落点 |
|--------|--------------|----------------------------------|----------------|
| Subagent | [Claude Code Subagents](https://code.claude.com/docs/en/subagents) | `/fork`、`FORK_SUBAGENT`、独立上下文 | `exp3_11c_subagent_runtime_openai.py` |
| Agent Team | [Claude Code Agent Teams](https://code.claude.com/docs/en/agent-teams) | `--agent-teams`、team/task 本地状态 | `exp3_11e_agent_team_runtime_openai.py` |
| Coordinator / Worker | 官方 Agent Team 与 Subagent 共同提供边界 | `src/coordinator/`、`COORDINATOR_MODE` | `exp3_11d_coordinator_runtime_openai.py` |
| Hooks | [Claude Code Hooks](https://code.claude.com/docs/en/hooks) | `src/hooks/`、生命周期事件 | `exp3_11f_hook_control_plane_openai.py` |
| 指令加载 | [Claude Code Memory](https://code.claude.com/docs/en/memory) | `CLAUDE.md`、rules、skills、prompt assembly | `exp3_11g_instruction_permission_runtime_openai.py` |
| 权限控制 | [Claude Code Settings](https://code.claude.com/docs/en/settings) 与 [Agent SDK Permissions](https://code.claude.com/docs/en/agent-sdk/permissions) | permission mode、Bash classifier、transcript classifier | `exp3_11f / exp3_11g` |
| 上下文压缩 | [Claude Code Hooks - PreCompact/PostCompact](https://code.claude.com/docs/en/hooks) | `CONTEXT_COLLAPSE`、`REACTIVE_COMPACT`、`HISTORY_SNIP`、`TOKEN_BUDGET` | `exp3_11h_context_memory_runtime_openai.py` |
| 记忆系统 | [Claude Code Memory](https://code.claude.com/docs/en/memory) | `EXTRACT_MEMORIES`、`TEAMMEM`、`KAIROS / Dream` | `exp3_11h` |
| 长生命周期 | [Claude Code Hooks - SessionEnd/WorktreeCreate](https://code.claude.com/docs/en/hooks) | `KAIROS`、cron、background tasks、lock | 待补 `3.13 / 3.14` 生产化章节 |

### 核心概念边界

这几组概念必须分开：

| 概念 | 解决的问题 | 不要混淆成 |
|------|------------|------------|
| **Subagent** | 父 Agent 把一个局部任务委派出去，子 Agent 独立上下文执行后返回摘要 | Agent Team |
| **Agent Team** | 多个独立 teammate 通过 shared task list / mailbox / lead 协作 | 普通工具调用 |
| **Coordinator** | 主 Agent 只负责拆解、派活、综合，不直接改代码 | 会写代码的万能 Supervisor |
| **Hook** | 在生命周期事件上注入控制、校验、阻断或上下文 | Prompt 技巧 |
| **CLAUDE.md / rules** | 长期项目指令和路径规则加载 | 记忆数据库 |
| **Memory** | 跨会话或跨任务保留有价值事实 | 当前上下文 |
| **Permission** | 决定工具调用是否允许执行 | Tool schema |
| **Worktree / Session** | 隔离并持久化一次执行环境 | 普通消息历史 |

### 后续学习任务拆分

接下来不继续堆更多“扫描 / 分析 / 报告”示例，而是按 Claude Code 的核心能力层补实验。

#### 任务 1：补齐 Subagent Runtime 讲解

对应代码：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_11c_subagent_runtime_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11c_subagent_runtime_openai.py)

学习目标：

- 看懂 `primary agent` 和 `subagent` 为什么不是同一个上下文。
- 看懂 `Task` 委派原语如何启动 child session。
- 看懂 `@explore` 这种显式 subagent 入口与自动委派的区别。
- 看懂为什么 subagent 的工具权限必须独立配置。

验收问题：

- 为什么 `explore` 适合读代码但不应该写文件？
- 为什么子 Agent 的 tool results 不应该全部灌回父 Agent 上下文？
- `subagent` 和 `fork` 的最大区别是什么？

#### 任务 2：新增 Coordinator / Worker Runtime

对应代码：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_11d_coordinator_runtime_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11d_coordinator_runtime_openai.py)

参考能力：

- `pengchengneo/Claude-Code` 的 `Coordinator` 文档把 Coordinator 限制为派活、通信、停工三类能力。
- Worker 独立执行，并把结果以结构化通知形式交回 Coordinator。
- 标准流程是 `Research -> Synthesis -> Implementation -> Verification`。

本项目实现目标：

- [CoordinatorRuntime](D:/Code/BeginningWithAI/experiments/phase3/exp3_11d_coordinator_runtime_openai.py:349) 不直接读写代码，只能调用 `agent`、`send_message`、`task_stop` 三个控制工具。
- [WorkerSpec](D:/Code/BeginningWithAI/experiments/phase3/exp3_11d_coordinator_runtime_openai.py:274) 定义 `research / implementation / verification` 三类 Worker。
- [TaskStore](D:/Code/BeginningWithAI/experiments/phase3/exp3_11d_coordinator_runtime_openai.py:309) 用本地 JSON 文件模拟 shared task list。
- [run_coordinator()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11d_coordinator_runtime_openai.py:399) 演示 Coordinator 通过 LLM 自主派发 Worker。
- [run_scripted_demo()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11d_coordinator_runtime_openai.py:438) 用固定计划验证 runtime 行为，避免调试时被模型规划不稳定干扰。
- [_coordinator_tool_schemas()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11d_coordinator_runtime_openai.py:619) 是 Coordinator 的工具权限边界，里面只有 `agent / send_message / task_stop`。

运行方式：

```bash
./venv/bin/python experiments/phase3/exp3_11d_coordinator_runtime_openai.py --help
./venv/bin/python experiments/phase3/exp3_11d_coordinator_runtime_openai.py --scripted --max-rounds 5
./venv/bin/python experiments/phase3/exp3_11d_coordinator_runtime_openai.py --max-rounds 4 --task "只派一个 research worker 分析 experiments/phase3/exp3_11b_multi_agent_openai.py 中 create_agents、choose_next_agent、run_supervisor 的关系。worker 完成后你直接总结。"
```

验证结论：

- `py_compile` 通过。
- `--help` 通过。
- `--scripted --max-rounds 5` 通过：Research Worker 完成代码结构分析，Verification Worker 使用 `./venv/bin/python` 验证 `exp3_11b --help` 成功。
- 非 scripted 模式通过：Coordinator 成功通过 `agent` 控制工具派出 `research` Worker，并综合 Worker 结果。

验收问题：

- 为什么 Coordinator 工具越少，反而越容易形成稳定分工？
- 为什么 Worker prompt 必须自包含？
- 什么时候应该继续已有 Worker，什么时候应该 spawn 新 Worker？

#### 任务 3：新增 Agent Team Runtime

对应代码：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_11e_agent_team_runtime_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11e_agent_team_runtime_openai.py)

参考能力：

- 官方 Agent Teams 文档把 Team 拆成 `team lead`、`teammates`、`task list`、`mailbox`。
- Team 和 Subagent 的官方区别是：Subagent 只把结果回给主 Agent；Team 允许 teammate 之间直接通信，并通过共享任务列表协作。

本项目实现目标：

- [TeamMember](D:/Code/BeginningWithAI/experiments/phase3/exp3_11e_agent_team_runtime_openai.py:59) 定义 teammate 的 agent type、system prompt、工具权限和模型。
- [TeamTask](D:/Code/BeginningWithAI/experiments/phase3/exp3_11e_agent_team_runtime_openai.py:70) 是 shared task list 的任务记录，包含 `pending / in_progress / blocked / completed`。
- [MailboxMessage](D:/Code/BeginningWithAI/experiments/phase3/exp3_11e_agent_team_runtime_openai.py:83) 是 teammate 之间的直接消息。
- [TeamStore](D:/Code/BeginningWithAI/experiments/phase3/exp3_11e_agent_team_runtime_openai.py:101) 把 team config、tasks、mailbox 落到本地 JSON 文件。
- [AgentTeamRuntime](D:/Code/BeginningWithAI/experiments/phase3/exp3_11e_agent_team_runtime_openai.py:210) 负责运行 teammates，并维护共享任务和邮箱。
- [run_scripted_demo()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11e_agent_team_runtime_openai.py:276) 用固定 lead 计划稳定演示 team runtime。
- [run_teammate()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11e_agent_team_runtime_openai.py:317) 每次启动一个独立 teammate session。
- [_tool_schemas_for_member()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11e_agent_team_runtime_openai.py:428) 根据 teammate 权限暴露工具。

运行方式：

```bash
./venv/bin/python experiments/phase3/exp3_11e_agent_team_runtime_openai.py --help
./venv/bin/python experiments/phase3/exp3_11e_agent_team_runtime_openai.py --scripted --max-rounds 3
```

验证结论：

- `py_compile` 通过。
- `--help` 通过。
- clean-state `--scripted --max-rounds 3` 通过：三个 task 都进入 `completed`，task list 和 mailbox 都写入本地 JSON。
- mailbox 验证通过：`architect -> critic` 的消息存在，critic 读取自己的 inbox 时能看到这条消息。
- verification task 通过：verifier 使用 `shell` 工具运行 `./venv/bin/python experiments/phase3/exp3_11e_agent_team_runtime_openai.py --help`，returncode 为 0。

验收问题：

- Agent Team 为什么比 Subagent 更贵？
- Team 的 shared task list 和 3.11b 的共享 `state` 有什么区别？
- teammate 之间直接通信会引入什么新的失败模式？

#### 任务 4：新增 Hook 控制面

对应代码：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_11f_hook_control_plane_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11f_hook_control_plane_openai.py)

参考能力：

- 官方 Hooks 文档把事件放在完整生命周期里：`SessionStart`、`UserPromptSubmit`、`PreToolUse`、`PostToolUse`、`TaskCreated`、`TaskCompleted`、`SubagentStart`、`SubagentStop`、`PreCompact`、`PostCompact`、`SessionEnd`、`WorktreeCreate`、`WorktreeRemove`。
- Hook 不是模型能力，而是 runtime 在关键事件上执行的控制逻辑。

本项目实现目标：

- 实现 `HookRegistry` 和 `HookDecision`。
- 在工具执行前触发 `PreToolUse`，允许 block / allow。
- 在工具执行后触发 `PostToolUse`，记录审计日志。
- 在任务完成前触发 `TaskCompleted`，如果验证未通过则阻断完成。
- 在压缩前后触发 `PreCompact / PostCompact`，演示上下文压缩生命周期。

运行方式：

```bash
./venv/bin/python experiments/phase3/exp3_11f_hook_control_plane_openai.py --scripted
```

验证结论：

- `py_compile` 通过。
- `--help` 通过。
- `--scripted` 通过：`.env` 读取被 `PreToolUse` 阻断，破坏性 shell 被阻断，`TaskCompleted` 在验证前被阻断，验证通过后允许完成，`PreCompact / PostCompact` 写入 compact log。

验收问题：

- 为什么权限控制不能只写进 prompt？
- `PreToolUse` 和 `PostToolUse` 的根本差异是什么？
- 为什么 `TaskCompleted` hook 比“让模型自觉跑测试”更可靠？

#### 任务 5：新增 Instruction / Permission Runtime

对应代码：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_11g_instruction_permission_runtime_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11g_instruction_permission_runtime_openai.py)

参考能力：

- 官方 Memory 文档中，`CLAUDE.md` 有 managed、user、project、local 多级加载。
- `.claude/rules/` 可以按路径加载规则。
- 官方 Settings 文档用 `permissions.deny` 阻止读取 `.env`、`secrets/**` 等敏感路径。

本项目实现目标：

- 模拟加载 `CLAUDE.md`、`.claude/rules/*.md` 和 `.claude/settings.json`。
- 区分“指令加载”和“权限强制”：前者告诉 Agent 应该怎么做，后者决定工具是否允许执行。
- 实现 `permissions.deny` 对 `read / grep / glob` 的统一过滤。
- 演示 subagent 如何继承或覆盖工具权限。

运行方式：

```bash
./venv/bin/python experiments/phase3/exp3_11g_instruction_permission_runtime_openai.py --scripted
```

验证结论：

- `py_compile` 通过。
- `--help` 通过。
- `--scripted` 通过：`CLAUDE.md` import 了 `AGENTS.md`，Python rule 按路径加载，`.claude/settings.json` 被加载，`.env` 和 `secrets/token.txt` 被 `permissions.deny` 阻断。

验收问题：

- 为什么 `CLAUDE.md` 不能替代权限系统？
- 为什么 rules 要支持路径匹配？
- 为什么 settings 是 JSON，而 instructions 是 Markdown？

#### 任务 6：新增 Context / Memory Runtime

对应代码：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_11h_context_memory_runtime_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11h_context_memory_runtime_openai.py)

参考能力：

- 官方文档把项目指令、规则、skills、subagent memory 分开处理。
- `pengchengneo/Claude-Code` 的 KAIROS / Dream 文档提供了长期记忆整合线索：每日日志、后台整合、锁、索引文件、过期事实清理。

本项目实现目标：

- 实现 `transcript.jsonl` 保存每轮消息。
- 实现 token budget 近似估算。
- 实现 `compact()`：把长历史压缩成摘要，并触发 `PreCompact / PostCompact`。
- 实现 `MEMORY.md` 索引和 topic memory 文件。
- 实现 `extract_memory()`：从完成的任务中抽取稳定事实，而不是把所有对话都存成记忆。

运行方式：

```bash
./venv/bin/python experiments/phase3/exp3_11h_context_memory_runtime_openai.py --scripted
```

验证结论：

- `py_compile` 通过。
- `--help` 通过。
- `--scripted` 通过：长上下文触发 compact，`transcript.jsonl` 保存完整会话，`MEMORY.md` 只保存 topic 索引，稳定事实被写入 topic memory 文件。

验收问题：

- 上下文压缩和记忆抽取有什么区别？
- 为什么 memory 需要索引文件？
- 为什么长期记忆必须有删除和修正机制？

#### 任务 7：新增 Internal / System Agent Runtime

对应代码：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_11i_internal_system_agent_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11i_internal_system_agent_openai.py)

本项目实现目标：

- 实现 `AgentSpec.hidden`，区分用户可见 Agent 和 runtime 内部 Agent。
- 实现 permission classifier，在工具执行前阻断敏感路径和破坏性命令。
- 实现 completion judge，用 `TaskContract` 判断候选结果是否达到交付条件。
- 实现 context compactor 和 memory curator，分别处理上下文预算和长期稳定事实。

运行方式：

```bash
./venv/bin/python experiments/phase3/exp3_11i_internal_system_agent_openai.py --scripted
```

验收问题：

- Internal/System Agent 和普通 subagent 的边界是什么？
- 为什么 completion judge 应该读取测试结果和证据，而不是只读模型最终回答？
- 为什么 internal agent 不应该输出隐藏思维链？

#### 任务 8：新增 Runtime Reliability

对应代码：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_13b_runtime_reliability_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_13b_runtime_reliability_openai.py)

本项目实现目标：

- 实现 retry，用于处理瞬时失败。
- 实现 fallback，用于处理主路径不可用。
- 实现 checkpoint，用于长任务恢复和复盘。
- 实现 trace 和 eval，用于回答“发生了什么”和“算不算合格”。

运行方式：

```bash
./venv/bin/python experiments/phase3/exp3_13b_runtime_reliability_openai.py --scripted
./venv/bin/python experiments/phase3/exp3_13b_runtime_reliability_openai.py --scripted --resume
```

验收问题：

- retry 和 fallback 的边界是什么？
- checkpoint、memory、transcript 分别保存什么？
- trace 和 eval 为什么要同时存在？

### 推荐学习顺序

```text
3.11b 固定 Team
  -> 3.11c 主 Agent + Subagent
  -> 3.11d Coordinator / Worker
  -> 3.11e Agent Team
  -> 3.11f Hook 控制面
  -> 3.11g Instruction / Permission
  -> 3.11h Context / Memory
  -> 3.11i Internal / System Agent
  -> 3.13b Runtime Reliability
  -> 3.13/3.14 生产化与综合平台
```

这条线的核心不是“多写几个 Agent”，而是逐步补齐真实 code agent 的运行时能力：

```text
agent loop
  -> tool permission
  -> delegated subtask
  -> team coordination
  -> lifecycle hooks
  -> instruction loading
  -> context compaction
  -> persistent memory
  -> internal completion and memory governance
  -> retry / fallback / checkpoint / trace / eval
  -> long-running session
```

---

## 📦 环境准备

```powershell
# 激活虚拟环境
cd D:\Code\BeginningWithAI
.\venv\Scripts\activate

# 安装核心依赖（阶段 1-4）
pip install langchain langgraph langchain-community
pip install langchain-openai langchain-ollama python-dotenv
pip install mcp  # MCP Python SDK
pip install python-nmap shodan requests

# 阶段 5 再安装
pip install a2a-sdk httpx
```

### Dify 部署（Docker，可放到阶段 5 再执行）

```powershell
# 克隆并启动 Dify
git clone https://github.com/langgenius/dify.git
cd dify/docker
cp .env.example .env
docker compose up -d
```

启动后访问 `http://localhost` 即可使用 Dify 平台。

---

## 📋 Agent 底层逻辑概览

> 在进入具体实验之前，先理解 Agent 工具调用的底层原理。各技术（MCP、Skill 等）的详细说明见对应实验章节，全景对比见末尾「工具调用模式总结」。

### Function Calling 的 5 步生命周期

这是理解所有 Agent 框架的基石：

```
步骤 1: 初始化 Client/LLM
         │
步骤 2: 定义 Tools List（函数说明书）
         │
步骤 3: 第一次调用（问题 + Tools → 模型）
         │  模型不直接回答，返回: "我要调 scan_port，参数是 {...}"
         │
步骤 4: 本地执行工具
         │  运行 TOOL_MAP["scan_port"](**args)，拿到真实结果
         │
步骤 5: 第二次调用（原问题 + 调用指令 + 工具结果 → 模型）
            模型看完结果，生成最终自然语言回答
```

> **本质**：模型只做决策不执行，代码只做执行不思考。二者通过消息传递协作。

### 从 Function Calling 到 ReAct Agent

以上 5 步是**单次工具调用**的闭环。真正的 Agent 只是加了 `while True`：

```python
while True:
    response = llm.invoke(messages)    # 问模型
    if response.tool_calls:            # 模型要调工具？
        执行工具 → 将结果追加到 messages → continue
    else:
        break  # 模型直接回答了 → 退出循环
```

这就是 ReAct Agent 的中心引擎。无论手写还是 `create_react_agent()`，底层都是这个循环。

---

## 🧪 实验 3.1：Function Calling 基础

### 目标

理解并实现 LLM 的工具调用能力。

### 对应代码文件与逐行阅读入口

- Ollama 主文件：[D:\Code\BeginningWithAI\experiments\phase3\exp3_1_function_calling.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_1_function_calling.py)
- OpenAI SDK 对照：[D:\Code\BeginningWithAI\experiments\phase3\exp3_1b_function_calling_api.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_1b_function_calling_api.py)
- LangChain 对照：[D:\Code\BeginningWithAI\experiments\phase3\exp3_1c_function_calling_langchain.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_1c_function_calling_langchain.py)
- 建议逐行顺序： [scan_port()](D:/Code/BeginningWithAI/experiments/phase3/exp3_1_function_calling.py:143) → [check_vulnerability()](D:/Code/BeginningWithAI/experiments/phase3/exp3_1_function_calling.py:177) → [scan_ip()](D:/Code/BeginningWithAI/experiments/phase3/exp3_1_function_calling.py:205) → [chat_with_tools()](D:/Code/BeginningWithAI/experiments/phase3/exp3_1_function_calling.py:273)
- OpenAI 版逐行重点： [chat_with_tools()](D:/Code/BeginningWithAI/experiments/phase3/exp3_1b_function_calling_api.py:142) 里要重点对照 `tool_calls` 路径、`arguments` 的 JSON 解析、`tool_call_id` 的结果回填。

### 📖 核心概念：Agent 与工具调用

#### 什么是 Agent？

Agent 是一种能够自主决策和执行任务的 AI 系统。

```
用户目标 → Agent 规划 → 工具调用 → 观察结果 → 继续/完成
```

#### Agent 核心能力

| 能力   | 描述            |
| ---- | ------------- |
| 规划   | 将复杂任务分解为可执行步骤 |
| 记忆   | 保持对话历史和任务状态   |
| 工具使用 | 调用外部 API 和工具  |
| 反思   | 根据结果调整策略      |

### 📘 API 参考：`ollama.chat()` 的 `tools` 扩展

在基础 `ollama.chat()` 调用（参见阶段一 API 参考）之上新增 `tools` 参数，使模型具备工具调用能力。

#### 新增入参：`tools`

```python
response = ollama.chat(
    model="qwen2.5:7b",
    messages=[...],
    tools=[...]      # 新增：工具定义列表
)
```

##### `tools` 工具定义结构

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "scan_port",                    # 工具名称
            "description": "扫描目标主机的指定端口",   # 工具描述（模型据此判断何时调用）
            "parameters": {                          # 参数定义（JSON Schema 格式）
                "type": "object",
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "目标主机IP"
                    },
                    "port": {
                        "type": "integer",
                        "description": "端口号"
                    }
                },
                "required": ["host", "port"]         # 必填参数
            }
        }
    }
]
```

#### 返回值变化：`message.tool_calls`

当模型判断需要调用工具时，`response.message.content` 为空，转而在 `tool_calls` 中返回调用请求：

```python
# response.message.tool_calls 结构：
[
    ToolCall(
        function=Function(
            name="scan_port",                # 模型决定调用的工具名
            arguments={"host": "localhost", "port": 80}  # 已解析为 dict
        )
    )
]
```

两种等效的访问方式：

```python
# 属性访问
name = tool_call.function.name
args = tool_call.function.arguments

# 字典访问
name = tool_call["function"]["name"]
args = tool_call["function"]["arguments"]
```

#### 两阶段调用流程

```
第一阶段                          第二阶段
┌─────────────┐               ┌─────────────┐
│ ollama.chat │               │ ollama.chat │
│  + tools    │               │  + tools    │
└──────┬──────┘               └──────┬──────┘
       │                             │
       ▼                             ▼
  response.message              final.message
  .tool_calls ≠ None            .content = "最终回答"
       │
       ▼
  你的代码执行工具
  TOOL_MAP[name](**args)
       │
       ▼
  将结果追加到 messages：
  ┌────────────────────────────┐
  │ messages.append(           │
  │   response.message         │ ← assistant 的工具调用消息
  │ )                          │
  │ messages.append({          │
  │   "role": "tool",          │ ← 工具执行结果
  │   "content": json.dumps(), │
  │   "tool_name": func_name   │ ← 必须指定
  │ })                         │
  └────────────────────────────┘
```

> **注意**：`tool_calls` 在 `response.message` 下面，不在 `response` 顶层。这是最常见的踩坑点。

### 代码示例

创建文件 `experiments/phase3/exp3_1_function_calling.py`：

```python
"""
实验 3.1: Function Calling 基础
使用 Ollama 实现工具调用
"""
import ollama
import json

# 定义工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "scan_port",
            "description": "扫描目标主机的指定端口是否开放",
            "parameters": {
                "type": "object",
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "目标主机IP或域名"
                    },
                    "port": {
                        "type": "integer",
                        "description": "要扫描的端口号"
                    }
                },
                "required": ["host", "port"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_vulnerability",
            "description": "检查目标是否存在指定漏洞",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "目标URL或IP"
                    },
                    "vuln_type": {
                        "type": "string",
                        "enum": ["sql_injection", "xss", "ssrf", "lfi"],
                        "description": "漏洞类型"
                    }
                },
                "required": ["target", "vuln_type"]
            }
        }
    }
]


def scan_port(host: str, port: int) -> dict:
    """模拟端口扫描"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        is_open = result == 0
        return {"host": host, "port": port, "open": is_open}
    except Exception as e:
        return {"host": host, "port": port, "error": str(e)}


def check_vulnerability(target: str, vuln_type: str) -> dict:
    """模拟漏洞检查（演示用）"""
    # 实际应用中应调用真实的漏洞扫描器
    return {
        "target": target,
        "vuln_type": vuln_type,
        "status": "scan_completed",
        "findings": []  # 演示用，无发现
    }


# 工具映射
TOOL_MAP = {
    "scan_port": scan_port,
    "check_vulnerability": check_vulnerability
}


def chat_with_tools(user_message: str, model: str = "qwen2.5:7b"):
    """带工具调用的对话"""
    messages = [{"role": "user", "content": user_message}]

    # 第一次调用：让模型决定是否使用工具
    response = ollama.chat(
        model=model,
        messages=messages,
        tools=tools
    )

    # 检查是否有工具调用（注意：用属性访问，不是字典）
    if response.message.tool_calls:
        for tool_call in response.message.tool_calls:
            func_name = tool_call.function.name
            func_args = tool_call.function.arguments  # 已经是 dict，无需 json.loads

            print(f"\n🔧 调用工具: {func_name}")
            print(f"   参数: {json.dumps(func_args, ensure_ascii=False)}")

            # 执行工具
            if func_name in TOOL_MAP:
                result = TOOL_MAP[func_name](**func_args)
                print(f"   结果: {json.dumps(result, ensure_ascii=False)}")

                # 将 assistant 消息和工具结果追加到对话历史
                messages.append(response.message)
                messages.append({
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False),
                    "tool_name": func_name
                })

        # 第二次调用：根据工具结果生成最终回答
        final_response = ollama.chat(
            model=model,
            messages=messages,
            tools=tools
        )
        return final_response.message.content

    return response.message.content


if __name__ == "__main__":
    # 测试用例
    test_queries = [
        "帮我扫描一下 localhost 的 80 端口是否开放",
        "检查 example.com 是否存在 SQL 注入漏洞",
        "分析一下常见的 Web 安全漏洞"  # 不需要工具的问题
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"问题: {query}")
        print("="*60)
        result = chat_with_tools(query)
        print(f"\n💬 回答: {result}")
```

### 验证标准

- [x] 模型能识别何时需要工具
- [x] 工具参数提取正确
- [x] 工具执行结果正确返回
- [x] 最终回答整合了工具结果

### 常见问题与踩坑记录

#### 1. Ollama SDK 的两种访问方式

`ChatResponse` 对象**同时支持属性访问和字典访问**，两种方式等效：

```python
# 方式一：属性访问
response.message.content
response.message.tool_calls
tool_call.function.name
tool_call.function.arguments

# 方式二：字典访问（与 exp1_2 中的用法一致）
response["message"]["content"]
response["message"]["tool_calls"]
tool_call["function"]["name"]
tool_call["function"]["arguments"]
```

| 模式                 | 返回类型                  | 两种访问方式                                                                |
| ------------------ | --------------------- | --------------------------------------------------------------------- |
| `stream=True`      | 迭代器，每个 chunk 是 `dict` | 仅字典访问 `chunk["message"]["content"]`                                   |
| `stream=False`（默认） | `ChatResponse` 对象     | 属性 `response.message.content` 或字典 `response["message"]["content"]` 均可 |

#### 2. `tool_calls` 的查找路径（踩坑重点）

**真正的 bug 不是访问方式（属性 vs 字典），而是查找路径写错了：**

```python
# ❌ 错误：在 response 顶层找 tool_calls，永远找不到
if "tool_calls" in response:  

# ✅ 正确：tool_calls 在 response.message 下面
if response.message.tool_calls:          # 属性方式
if response["message"].get("tool_calls"):  # 字典方式（也行）
```

`tool_calls` 不是你的代码生成的，而是 **LLM 在响应中返回的**。完整流程：

```
你定义 tools → 传给 ollama.chat() → LLM 分析用户意图
→ LLM 返回 tool_calls（"我要调这个工具，参数是这些"）
→ 你的代码执行工具 → 把结果传回 LLM → LLM 给出最终回答
```

#### 3. `arguments` 无需 `json.loads`

Ollama SDK 已自动将参数解析为 `dict`，直接使用即可，无需再调用 `json.loads()`：

```python
func_args = tool_call.function.arguments       # 属性方式，已是 dict
func_args = tool_call["function"]["arguments"]  # 字典方式，同样是 dict
```

#### 4. 工具结果消息格式

返回工具结果时需包含 `tool_name` 字段：

```python
messages.append({
    "role": "tool",
    "content": json.dumps(result),
    "tool_name": func_name  # 必须指定
})
```

#### 5. Python 参数默认值 vs 类型注解

```python
# ❌ 错误：这是类型注解，"qwen2.5:7b" 被当作类型，model 仍是必填参数
def chat_with_tools(model: "qwen2.5:7b"): ...

# ✅ 正确：这是默认参数值
def chat_with_tools(model: str = "qwen2.5:7b"): ...
```

#### 6. Windows 下 ping 命令差异

```python
# ❌ Linux 参数：-c (count), -W (timeout)
subprocess.run(["ping", "-c", "1", "-W", "5", ip])

# ✅ Windows 参数：-n (count), -w (timeout in ms)
subprocess.run(["ping", "-n", "1", "-w", "1000", ip])
```

### 场景 B：API Key 模式的 Function Calling

> Ollama 和 OpenAI 的 Function Calling 核心概念一致（tools 定义 → 模型返回 tool_calls → 执行 → 回传结果），但响应格式有差异。掌握这些差异后，你能灵活切换后端。

创建文件 `experiments/phase3/exp3_1b_function_calling_api.py`：

```python
"""
实验 3.1b: API Key 模式的 Function Calling
对比 Ollama 版本，理解 OpenAI 格式的工具调用差异
"""
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://opencode.ai/zen/go/v1"),
)
MODEL = os.getenv("OPENAI_MODEL", "deepseek-v4-pro")


# 工具定义格式与 Ollama 完全一致（都遵循 JSON Schema）
tools = [
    {
        "type": "function",
        "function": {
            "name": "scan_port",
            "description": "扫描目标主机的指定端口是否开放",
            "parameters": {
                "type": "object",
                "properties": {
                    "host": {"type": "string", "description": "目标主机IP或域名"},
                    "port": {"type": "integer", "description": "要扫描的端口号"}
                },
                "required": ["host", "port"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_vulnerability",
            "description": "检查目标是否存在指定漏洞",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "目标URL或IP"},
                    "vuln_type": {
                        "type": "string",
                        "enum": ["sql_injection", "xss", "ssrf", "lfi"],
                        "description": "漏洞类型"
                    }
                },
                "required": ["target", "vuln_type"]
            }
        }
    }
]


def scan_port(host: str, port: int) -> dict:
    """模拟端口扫描"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return {"host": host, "port": port, "open": result == 0}
    except Exception as e:
        return {"host": host, "port": port, "error": str(e)}


def check_vulnerability(target: str, vuln_type: str) -> dict:
    """模拟漏洞检查"""
    return {"target": target, "vuln_type": vuln_type, "status": "scan_completed", "findings": []}


TOOL_MAP = {"scan_port": scan_port, "check_vulnerability": check_vulnerability}


def chat_with_tools(user_message: str):
    """
    OpenAI 格式的工具调用 — 与 Ollama 的关键差异：

    1. 调用方式: client.chat.completions.create() vs ollama.chat()
    2. tool_calls 路径: response.choices[0].message.tool_calls vs response.message.tool_calls
    3. arguments 类型: JSON 字符串（需 json.loads）vs dict（已解析）
    4. 工具结果角色: "tool" + tool_call_id vs "tool" + tool_name
    """
    messages = [{"role": "user", "content": user_message}]

    # 第一次调用
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools
    )

    message = response.choices[0].message

    if message.tool_calls:
        # 将 assistant 消息加入历史
        messages.append(message)

        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            # ⚠️ 关键差异：OpenAI 返回的 arguments 是 JSON 字符串，需手动解析
            func_args = json.loads(tool_call.function.arguments)

            print(f"\n🔧 调用工具: {func_name}")
            print(f"   参数: {json.dumps(func_args, ensure_ascii=False)}")

            if func_name in TOOL_MAP:
                result = TOOL_MAP[func_name](**func_args)
                print(f"   结果: {json.dumps(result, ensure_ascii=False)}")

                # ⚠️ 关键差异：OpenAI 用 tool_call_id 关联结果，而非 tool_name
                messages.append({
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False),
                    "tool_call_id": tool_call.id  # Ollama 用 tool_name
                })

        # 第二次调用
        final = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools
        )
        return final.choices[0].message.content

    return message.content


if __name__ == "__main__":
    test_queries = [
        "帮我扫描一下 localhost 的 80 端口是否开放",
        "检查 example.com 是否存在 SQL 注入漏洞",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"问题: {query}")
        print("="*60)
        result = chat_with_tools(query)
        print(f"\n💬 回答: {result}")
```

#### Ollama vs OpenAI Function Calling 差异

|                   | Ollama                              | OpenAI                                    |
| ----------------- | ----------------------------------- | ----------------------------------------- |
| **tool_calls 路径** | `response.message.tool_calls`       | `response.choices[0].message.tool_calls`  |
| **arguments 类型**  | `dict`（已解析，直接使用）                    | JSON 字符串（需 `json.loads()`）                |
| **工具结果关联**        | `"tool_name": func_name`            | `"tool_call_id": tool_call.id`            |
| **消息追加**          | `messages.append(response.message)` | `messages.append(message)`（完整 message 对象） |

### 场景 C：LangChain 的 Tool Calling

> 手写 Function Calling 需要处理很多格式差异。LangChain 用 `@tool` 装饰器 + `bind_tools()` 统一了不同模型的工具调用接口，代码更简洁，切换模型也更方便。

创建文件 `experiments/phase3/exp3_1c_function_calling_langchain.py`：

```python
"""
实验 3.1c: LangChain Tool Calling
用 @tool 装饰器和 bind_tools() 统一工具调用接口
"""
import os
import json
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

load_dotenv()


# ===== 用 @tool 装饰器定义工具（比手写 JSON Schema 简洁得多）=====

@tool
def scan_port(host: str, port: int) -> dict:
    """扫描目标主机的指定端口是否开放"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return {"host": host, "port": port, "open": result == 0}
    except Exception as e:
        return {"host": host, "port": port, "error": str(e)}


@tool
def check_vulnerability(target: str, vuln_type: str) -> dict:
    """检查目标是否存在指定漏洞。vuln_type 可选: sql_injection, xss, ssrf, lfi"""
    return {"target": target, "vuln_type": vuln_type, "status": "scan_completed", "findings": []}


def get_llm(backend: str = "ollama"):
    """获取 LLM 实例"""
    if backend == "ollama":
        return ChatOllama(model="qwen2.5:7b")
    elif backend == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "deepseek-v4-pro"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    raise ValueError(f"未知后端: {backend}")


# 工具列表
tools = [scan_port, check_vulnerability]
tool_map = {t.name: t for t in tools}


def chat_with_tools(user_message: str, backend: str = "ollama"):
    """
    LangChain 统一的工具调用流程 — 无论后端是什么，代码完全一样！

    对比手写版本：
    - 无需手写 JSON Schema（@tool 装饰器自动生成）
    - 无需处理 arguments 格式差异（LangChain 统一解析）
    - 无需关心 tool_call_id vs tool_name（LangChain 自动处理）
    """
    llm = get_llm(backend)

    # bind_tools: 将工具绑定到模型，一行搞定
    llm_with_tools = llm.bind_tools(tools)

    messages = [HumanMessage(content=user_message)]

    # 第一次调用
    response = llm_with_tools.invoke(messages)
    messages.append(response)

    # 检查工具调用（统一的 .tool_calls 属性）
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"\n🔧 调用工具: {tc['name']}")
            print(f"   参数: {json.dumps(tc['args'], ensure_ascii=False)}")

            # 执行工具
            result = tool_map[tc["name"]].invoke(tc["args"])
            print(f"   结果: {result}")

            # 追加工具结果（LangChain 统一用 ToolMessage）
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

        # 第二次调用
        final = llm_with_tools.invoke(messages)
        return final.content

    return response.content


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["ollama", "openai"], default="ollama")
    args = parser.parse_args()

    print(f"后端: {args.backend}\n")

    test_queries = [
        "帮我扫描一下 localhost 的 80 端口是否开放",
        "检查 example.com 是否存在 SQL 注入漏洞",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"问题: {query}")
        print("="*60)
        result = chat_with_tools(query, args.backend)
        print(f"\n💬 回答: {result}")
```

#### 三种 Function Calling 实现对比

|          | 原生 Ollama        | 原生 OpenAI        | LangChain               |
| -------- | ---------------- | ---------------- | ----------------------- |
| **工具定义** | 手写 JSON Schema   | 手写 JSON Schema   | `@tool` 装饰器自动生成         |
| **绑定工具** | `tools=tools` 参数 | `tools=tools` 参数 | `llm.bind_tools(tools)` |
| **解析参数** | 直接是 `dict`       | 需 `json.loads()` | 自动解析                    |
| **结果回传** | `tool_name`      | `tool_call_id`   | `ToolMessage` 统一处理      |
| **切换模型** | 改代码              | 改代码              | 改一行配置                   |
| **代码量**  | 中                | 中                | 少                       |

### 📋 LangChain 框架进阶认知

> 在完成三种 Function Calling 实现对比后，以下是对 LangChain 框架设计哲学的进阶总结。

#### Message vs History：数据与容器的解耦

LangChain 将"消息"和"装消息的容器"分成了两个独立层：

```
Message 类（数据对象 — 只存数据）
├── HumanMessage(content="...")    → 用户消息
├── AIMessage(content="...")       → AI 回复
└── SystemMessage(content="...")   → 系统提示词

InMemoryChatMessageHistory（历史管理器 — 装消息的容器）
├── .add_user_message("...")   → 内部创建 HumanMessage 并追加
├── .add_ai_message("...")     → 内部创建 AIMessage 并追加
├── .add_message(msg)          → 直接追加任意 Message 对象
├── .messages                  → 返回消息列表
└── .clear()                   → 清空列表
```

`add_user_message` 是容器方法（语法糖），两者等价：

```python
history.add_user_message("什么是XSS？")              # 语法糖
history.add_message(HumanMessage(content="什么是XSS？"))  # 底层实现
```

> **扩展性**：`InMemoryChatMessageHistory` 只是内存实现。LangChain 还提供 `RedisChatMessageHistory`、`SQLChatMessageHistory` 等，切换存储只需换一个类，其余代码不变。

#### `langchain_core` vs `langchain`：底层与上层

```
langchain_core    ← 核心包（最底层，无多余依赖）
    └── tools, messages, chat_history 等定义在这里

langchain         ← 主包（依赖 langchain_core）
    └── 从 langchain_core 重新导出，加上社区工具
```

```python
from langchain_core.tools import tool    # ✅ 推荐：依赖更少，导入更快
from langchain.tools import tool         # 也行，但多了一层间接依赖
```

> **建议**：优先从 `langchain_core` 导入，这是官方推荐的面向未来的写法。

#### LCEL 统一接口哲学：万物皆可 invoke / stream

LangChain v0.1 后所有组件都实现了统一的 `Runnable` 接口：

| 方法                | 作用         | 返回类型      |
| ----------------- | ---------- | --------- |
| `.invoke(input)`  | 一次性全量返回    | 完整结果      |
| `.stream(input)`  | 逐字流式返回     | 生成器       |
| `.batch(inputs)`  | 批量执行       | 结果列表      |
| `.ainvoke(input)` | 异步版 invoke | Awaitable |

**不论主体是 Chat 模型、Tool 工具、还是组合 Chain，一次性输出统一叫 `invoke`，流式输出统一叫 `stream`。**

#### @tool 装饰器：自动生成 JSON Schema

`@tool` 利用 Python 反射机制，从函数签名中自动提取工具描述：

```python
@tool
def scan_port(host: str, port: int) -> dict:
    """扫描目标主机的指定端口是否开放"""
    ...

# 自动提取：函数名 → name，docstring → description，类型标注 → parameters
```

**tool_map 字典调度模式**：

```python
tools = [scan_port, check_vulnerability]
tool_map = {t.name: t for t in tools}  # O(1) 查找

func = tool_map["scan_port"]
result = func.invoke({"host": "localhost", "port": 80})
```

> `if func_name in TOOL_MAP` 的检查是**防御性编程**：防止模型幻觉返回不存在的函数名导致 `KeyError` 崩溃。

---

## 🧪 实验 3.2：Prompt 核心价值与 LCEL

### 目标

理解 `ChatPromptTemplate` 的核心价值：变量替换和 LCEL 链式组装。

### 对应代码文件与逐行阅读入口

- 主文件：[D:\Code\BeginningWithAI\experiments\phase3\exp3_prompt_template.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_prompt_template.py)
- 建议逐行顺序： [get_llm()](D:/Code/BeginningWithAI/experiments/phase3/exp3_prompt_template.py:62) → [demo_variable_substitution()](D:/Code/BeginningWithAI/experiments/phase3/exp3_prompt_template.py:85) → [demo_chain_assembly()](D:/Code/BeginningWithAI/experiments/phase3/exp3_prompt_template.py:140) → [demo_component_swap()](D:/Code/BeginningWithAI/experiments/phase3/exp3_prompt_template.py:206)
- 这一章逐行阅读的重点不是 Agent loop，而是 Prompt 如何组装、变量什么时候替换、LCEL 的 `|` 管道怎么把 Prompt / LLM / Parser 串起来。

### 为什么需要 PromptTemplate？

```python
# ❌ 手动拼接（容易出错、难维护、无法复用）
prompt = f"你是{role}，请分析{target}的{vuln_type}漏洞"

# ✅ LangChain 模板（变量替换 + 类型安全 + 可复用）
from langchain_core.prompts import ChatPromptTemplate

template = ChatPromptTemplate.from_messages([
    ("system", "你是{role}，精通各类安全技术"),
    ("user", "请分析{target}的{vuln_type}漏洞"),
])

messages = template.invoke({"role": "安全专家", "target": "example.com", "vuln_type": "XSS"})
```

### LCEL 管道组装：Prompt | LLM | Parser

PromptTemplate 的终极价值在于**通过管道操作符 `|` 组装成调用链**：

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

chain = (
    ChatPromptTemplate.from_messages([
        ("system", "你是{role}"),
        ("user", "分析{target}的{vuln_type}漏洞风险"),
    ])
    | ChatOpenAI(model="deepseek-v4-pro")
    | StrOutputParser()
)

# 一行调用
result = chain.invoke({"role": "安全专家", "target": "example.com", "vuln_type": "SQL注入"})

# 流式输出同样支持
for chunk in chain.stream({"role": "安全专家", "target": "example.com", "vuln_type": "XSS"}):
    print(chunk, end="", flush=True)
```

**链式组装的价值**：

- 每个组件只负责一件事（单一职责）
- 替换任一环节不影响其他部分（如换模型只改 `ChatOpenAI` → `ChatOllama`）
- 同一个 Chain 可以 `invoke`、`stream`、`batch`，接口完全统一

### 代码示例

完整代码见 `experiments/phase3/exp3_prompt_template.py`，包含 3 个演示：

1. **变量替换**：同一模板不同参数的复用
2. **链式组装**：`invoke` / `stream` / `batch` 三种调用方式
3. **组件替换**：同一 Prompt+Parser，切换不同 LLM 后端

### 运行方式

```bash
# 运行全部演示
python3 experiments/phase3/exp3_prompt_template.py --demo all

# 仅运行链式组装演示
python3 experiments/phase3/exp3_prompt_template.py --demo 2 --backend openai
```

---

## 🧪 实验 3.3：ReAct Agent 实现

### 目标

构建一个能够推理和行动交替进行的 Agent。

### 对应代码文件与逐行阅读入口

- 手写 ReAct 主文件：[D:\Code\BeginningWithAI\experiments\phase3\exp3_2_react_agent.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_2_react_agent.py)
- Guarded Single Agent 扩展版：[D:\Code\BeginningWithAI\experiments\phase3\exp3_2b_guarded_single_agent.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_2b_guarded_single_agent.py)
- LangChain 封装版：[D:\Code\BeginningWithAI\experiments\phase3\exp3_2c_react_agent_langchain.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_2c_react_agent_langchain.py)
- 建议逐行顺序： [ReActAgent.__init__()](D:/Code/BeginningWithAI/experiments/phase3/exp3_2_react_agent.py:85) → [add_tool()](D:/Code/BeginningWithAI/experiments/phase3/exp3_2_react_agent.py:124) → [_create_prompt()](D:/Code/BeginningWithAI/experiments/phase3/exp3_2_react_agent.py:140) → [_parse_response()](D:/Code/BeginningWithAI/experiments/phase3/exp3_2_react_agent.py:176) → [run()](D:/Code/BeginningWithAI/experiments/phase3/exp3_2_react_agent.py:238)
- 如果你想看“更工程化”的单 Agent，再继续读： [TaskContract](D:/Code/BeginningWithAI/experiments/phase3/exp3_2b_guarded_single_agent.py:35) → [FinalAnswerValidator](D:/Code/BeginningWithAI/experiments/phase3/exp3_2b_guarded_single_agent.py:73) → [GuardedSingleAgent._run_openai()](D:/Code/BeginningWithAI/experiments/phase3/exp3_2b_guarded_single_agent.py:358)

### ReAct 模式

```
Thought: 我需要先了解目标的开放端口...
Action: scan_port
Action Input: {"host": "target.com", "port": 80}
Observation: {"open": true}
Thought: 80端口开放，我应该检查Web漏洞...
...
Final Answer: 扫描完成，发现以下安全问题...
```

### 代码示例

创建文件 `experiments/phase3/exp3_2_react_agent.py`：

```python
"""
实验 3.3: ReAct Agent
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
    """ReAct 模式 Agent"""

    def __init__(self, model: str = "qwen2.5:7b", max_iterations: int = 5, backend: str = "ollama"):
        self.model = model
        self.max_iterations = max_iterations
        self.backend = backend
        self.tools: Dict[str, Callable] = {}
        self.tool_descriptions: List[str] = []

        # OpenAI 后端初始化
        if self.backend == "openai":
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),
            )

    def register_tool(self, name: str, func: Callable, description: str):
        """注册工具"""
        self.tools[name] = func
        self.tool_descriptions.append(f"- {name}: {description}")

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
                response = ollama.chat(
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
```

### 运行方式

```bash
# Ollama 本地模型（默认）
python3 experiments/phase3/exp3_2_react_agent.py

# OpenAI 兼容 API
python3 experiments/phase3/exp3_2_react_agent.py --backend openai
```

> **核心差异**：相比实验 3.1 的 Function Calling（模型通过 `tool_calls` 结构化返回工具调用），ReAct Agent 使用**纯文本提示词**引导模型输出 `Thought/Action/Action Input` 格式，再用正则表达式解析。这是两种完全不同的工具调用范式。

### 专题 3.3x：Reasoning Trace、思维链与 ReAct Scratchpad

这一节补充一个容易混淆但很关键的点：

> 真实 code agent 需要可观察的“推理轨迹”，但这不等于要求模型把隐藏思维链完整暴露给用户或日志系统。

结合 Claude Code 官方文档和 `pengchengneo/Claude-Code` 源码还原材料，可以把相关概念拆成 5 层：

| 层次 | 含义 | 本项目中对应位置 |
|------|------|------------------|
| Hidden reasoning | 模型内部推理或 provider 的受保护 thinking block | 不作为教学输出，不要求模型泄露 |
| `reasoning_content` / `thinking` block | provider/API 需要在多轮工具调用中保留的推理字段 | [D:\Code\BeginningWithAI\experiments\phase3\exp3_11b_multi_agent_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11b_multi_agent_openai.py:248) |
| ReAct Scratchpad | 人为设计的 `Thought/Action/Observation` 工作区 | [D:\Code\BeginningWithAI\experiments\phase3\exp3_2_react_agent.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_2_react_agent.py:157) |
| Reasoning summary | 面向用户的简短计划、证据、风险和结论 | 后续所有 code agent 输出都应该采用这种形式 |
| Audit trace | runtime 记录的工具调用、权限判断、上下文压缩、任务完成状态 | [D:\Code\BeginningWithAI\experiments\phase3\exp3_11f_hook_control_plane_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11f_hook_control_plane_openai.py) |

#### 1. Claude Code 官方文档中的边界

Claude Code 官方文档把 code agent 的底层循环描述为：

```text
gather context -> take action -> verify results -> repeat
```

也就是：

- 模型负责理解代码、拆解任务、决定下一步。
- runtime 提供文件、搜索、执行、Web、子代理等工具。
- 每次工具结果都会回到上下文，影响下一步决策。
- 复杂任务可以先进入 plan mode，先研究和计划，再执行修改。

这和本项目的 ReAct / Function Calling / Multi-Agent 实验是一条主线：

```text
模型决策
  -> 工具调用
  -> 工具结果回填
  -> 模型继续决策
  -> 直到最终回答或达到限制
```

Claude Code 官方文档还单独说明了 reasoning effort 和 extended thinking：

- `/effort`、`--effort`、`CLAUDE_CODE_EFFORT_LEVEL` 可以控制推理投入。
- `ultrathink` 是一次性深度推理触发词，官方文档说明它会添加上下文指令，但不改变发送到 API 的 effort level。
- extended thinking 默认折叠显示；在交互界面中可能是 redacted thinking block。
- 用户需要为 thinking token 付费，即使这些内容被折叠或被 redacted。
- Skill 和 subagent frontmatter 也可以设置 `effort`，说明推理预算是 runtime 配置的一部分，不只是 prompt 文案。

所以，工程上要学的不是“让模型多写几段思考”，而是：

> 在不同任务复杂度下，如何分配 reasoning effort，并把行动、证据、验证结果以可审计方式暴露出来。

参考资料：

- [Claude Code: How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works)
- [Claude Code: Model configuration](https://code.claude.com/docs/en/model-config)
- [Claude Code Agent SDK: How the agent loop works](https://code.claude.com/docs/en/agent-sdk/agent-loop)

#### 2. GitHub 源码还原材料中的工程线索

`pengchengneo/Claude-Code` 是非官方源码还原仓库，但它提供了很有价值的工程观察。结合源码路径可以看到，Claude Code 风格 runtime 并不是简单地“打印思维链”，而是围绕 thinking block 做了很多工程控制：

> 注意：官方文档代表当前公开能力边界；源码还原材料代表某个还原版本里的工程实现线索。若两者在模型名、effort 枚举或开关名称上出现差异，课程以官方文档为准，用源码理解机制。

| 源码位置 | 观察点 | 对本项目的启发 |
|----------|--------|----------------|
| [`src/utils/thinking.ts`](https://github.com/pengchengneo/Claude-Code/blob/main/src/utils/thinking.ts) | 定义 `ThinkingConfig`：`adaptive / enabled / disabled`，并检测 `ultrathink` 关键词 | thinking 是 runtime 配置，不是普通输出文本 |
| [`src/utils/effort.ts`](https://github.com/pengchengneo/Claude-Code/blob/main/src/utils/effort.ts) | 定义 effort levels，并按 env、session、模型默认值解析最终 effort | reasoning budget 应有明确优先级 |
| [`src/query.ts`](https://github.com/pengchengneo/Claude-Code/blob/main/src/query.ts) | 在主 agent loop 中把 `thinkingConfig` 连同 messages/tools 一起传给模型调用 | 推理配置属于每轮模型请求的一部分 |
| [`src/utils/messages.ts`](https://github.com/pengchengneo/Claude-Code/blob/main/src/utils/messages.ts) | 流式处理中区分 `thinking / redacted_thinking / text / tool_use`，并过滤尾部或孤立 thinking block | thinking block 有 API 格式约束，不能随便改写 |
| [`src/tools/AgentTool/runAgent.ts`](https://github.com/pengchengneo/Claude-Code/blob/main/src/tools/AgentTool/runAgent.ts) | 普通 subagent 默认禁用 thinking 来控制输出 token 成本，fork child 可继承 thinkingConfig 以利用 prompt cache | subagent 的推理预算要按任务类型单独控制 |
| [`src/tools/AgentTool/forkSubagent.ts`](https://github.com/pengchengneo/Claude-Code/blob/main/src/tools/AgentTool/forkSubagent.ts) | fork 子任务保留父 assistant message 的 thinking/text/tool_use，但 worker 输出规则要求“不 thinking-out-loud” | 内部轨迹可用于继续执行，但最终报告要结构化、简洁 |

这和我们在 OpenAI 兼容实现里保留 `reasoning_content` 的原因一致：

```python
reasoning_content = getattr(message, "reasoning_content", None)
if reasoning_content:
    assistant_message["reasoning_content"] = reasoning_content
```

这段代码不是“展示思维链”，而是为了让 provider 在工具调用后的下一轮请求中看到它要求保留的推理字段。对 deepseek-v4-pro 这类 OpenAI 兼容 provider，如果上一轮 assistant tool call 带了 reasoning 内容，后续 tool result 回填时丢掉该字段，可能触发格式错误。

#### 3. ReAct Scratchpad 不是隐藏思维链

本项目手写 ReAct 实验里的提示词是：

```text
Thought: [你的思考过程]
Action: [工具名称]
Action Input: [JSON格式的参数]
Observation: [工具结果]
```

这里的 `Thought` 是我们显式设计出来的 scratchpad 字段。它的作用是教学和调试：

- 让你看到模型为什么选择某个工具。
- 让下一轮 prompt 能带上前面的行动历史。
- 让你理解 ReAct 与 Function Calling 的差异。

但它不等于模型的隐藏内部思维。真实生产系统通常不应该把完整 `Thought` 当作最终用户输出或长期日志。更稳妥的做法是保留下面这些可审计字段：

```json
{
  "plan": ["准备做什么"],
  "actions": ["实际调用了哪些工具"],
  "evidence": ["关键工具结果或文件证据"],
  "risks": ["仍不确定或需要人工确认的点"],
  "final_answer": "给用户的结论"
}
```

这也是后续 code agent runtime 课程要统一采用的输出风格：用户看到计划、行动、证据和结论；runtime 保存工具调用和权限日志；provider 特有的 hidden thinking 字段只做协议级传递。

#### 4. 与本项目代码逐行学习的对应关系

推荐按这个顺序阅读：

1. [D:\Code\BeginningWithAI\experiments\phase3\exp3_2_react_agent.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_2_react_agent.py:157)：先看 `_create_prompt()` 如何把 `Thought/Action/Observation` 写成文本协议。
2. [D:\Code\BeginningWithAI\experiments\phase3\exp3_2_react_agent.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_2_react_agent.py:200)：再看 `_parse_response()` 如何用正则从模型文本里拆出 `thought/action/final_answer`。
3. [D:\Code\BeginningWithAI\experiments\phase3\exp3_2_react_agent.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_2_react_agent.py:238)：继续看 `run()` 如何把 Observation 拼回 history，形成 ReAct 循环。
4. [D:\Code\BeginningWithAI\experiments\phase3\exp3_2b_guarded_single_agent.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_2b_guarded_single_agent.py:176)：对比工程化版本如何增加任务契约、最终答案校验和修复重试。
5. [D:\Code\BeginningWithAI\experiments\phase3\exp3_11b_multi_agent_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11b_multi_agent_openai.py:248)：最后看 OpenAI 兼容工具调用里为什么要把 `tool_calls` 和 `reasoning_content` 放回 assistant history。

#### 5. 学习验收问题

- ReAct 的 `Thought` 是模型隐藏思维链，还是 prompt 设计出来的可解析字段？
- 为什么生产环境更应该输出 `plan/actions/evidence/risks/final_answer`，而不是完整 `Thought`？
- 为什么 `reasoning_content` 要回填到下一轮请求，但不应该直接展示给用户？
- Claude Code 源码还原材料里，为什么普通 subagent 会默认禁用 thinking？
- `effort`、`extended thinking`、`ultrathink` 分别属于模型能力、runtime 配置，还是普通 prompt 文本？

### 验证标准

- [x] Agent 能够自主规划步骤
- [x] 正确调用工具并处理结果
- [x] 根据观察结果调整策略
- [x] 最终给出完整答案

### 场景 C：LangChain ReAct Agent

> 前面手写了完整的 ReAct 循环（提示词构造 → 响应解析 → 工具执行 → 历史拼接），代码量大且容易出错。LangChain 的 `create_react_agent()` 将这些步骤封装为几行代码，让你专注于工具定义和业务逻辑。

创建文件 `experiments/phase3/exp3_2c_react_agent_langchain.py`：

```python
"""
实验 3.3c: LangChain ReAct Agent
对比手写 ReAct 循环，体验框架的封装价值
"""
import os
import json
import socket
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

load_dotenv()


# ===== 工具定义（与手写版相同的功能，但用 @tool 装饰器更简洁）=====

@tool
def port_scan(host: str, ports: list[int]) -> dict:
    """扫描目标主机的多个端口。参数: host(str)-目标主机, ports(list[int])-端口列表"""
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


@tool
def web_fingerprint(url: str) -> dict:
    """识别Web服务的技术栈。参数: url(str)-目标URL"""
    return {
        "url": url,
        "server": "nginx/1.18.0",
        "technologies": ["PHP", "MySQL"],
        "cms": "unknown"
    }


def get_llm(backend: str = "ollama"):
    """获取 LLM 实例"""
    if backend == "ollama":
        return ChatOllama(model="qwen2.5:7b")
    elif backend == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "deepseek-v4-pro"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    raise ValueError(f"未知后端: {backend}")


def run_react_agent(task: str, backend: str = "ollama"):
    """
    用 LangChain 创建 ReAct Agent — 对比手写版本：

    手写版: ~100 行（提示词模板 + 正则解析 + 迭代循环 + 历史管理）
    LangChain: ~3 行（create_react_agent + invoke）
    """
    llm = get_llm(backend)
    tools = [port_scan, web_fingerprint]

    # 核心：一行创建 ReAct Agent
    agent = create_react_agent(llm, tools)

    # 运行（内部自动处理 ReAct 循环：思考 → 工具调用 → 观察 → 继续）
    result = agent.invoke({"messages": [("user", task)]})

    # 打印执行过程
    print("\n--- 执行过程 ---")
    for msg in result["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"🔧 调用: {tc['name']}({json.dumps(tc['args'], ensure_ascii=False)})")
        elif msg.type == "tool":
            print(f"📋 结果: {msg.content[:100]}...")
        elif msg.type == "ai" and msg.content:
            print(f"💬 回答: {msg.content[:200]}...")

    # 返回最终回答
    final_msg = result["messages"][-1]
    return final_msg.content


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["ollama", "openai"], default="ollama")
    args = parser.parse_args()

    print(f"后端: {args.backend}")

    task = "分析 localhost 的安全状况，扫描常用端口(80, 443, 22, 3306)并识别Web技术栈"
    print(f"\n任务: {task}")

    result = run_react_agent(task, args.backend)
    print(f"\n{'='*60}")
    print(f"最终结果: {result}")
```

#### 手写 ReAct vs LangChain ReAct 对比

|           | 手写 ReAct（实验 3.3）                   | LangChain ReAct（实验 3.3c） |
| --------- | ---------------------------------- | ------------------------ |
| **代码量**   | ~100 行                             | ~10 行核心代码                |
| **提示词管理** | 手动构造 Thought/Action/Observation 模板 | 框架内置，自动管理                |
| **响应解析**  | 正则匹配 Thought/Action/Final Answer   | 框架自动解析                   |
| **工具执行**  | 手动查找和调用                            | 框架自动执行                   |
| **迭代控制**  | 手动循环 + max_iterations              | 框架自动管理                   |
| **学习价值**  | ⭐⭐⭐ 深入理解 ReAct 原理                  | ⭐ 了解最佳实践                 |
| **生产可用**  | ⭐ 需要大量完善                           | ⭐⭐⭐ 开箱即用                 |

> **建议**：先完成手写版（3.3），确保理解 ReAct 的每个步骤，再用 LangChain 版（3.3c）体会框架的封装价值。

---

## 🧪 实验 3.4-3.6：MCP Server 开发

### 目标

开发符合 MCP 协议的安全工具服务。

### 对应代码文件与逐行阅读入口

- MCP Server 主文件：[D:\Code\BeginningWithAI\experiments\phase3\exp3_4_mcp_server.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_4_mcp_server.py)
- LangChain Agent 集成版：[D:\Code\BeginningWithAI\experiments\phase3\exp3_4c_mcp_langchain_agent.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_4c_mcp_langchain_agent.py)
- 手工客户端测试：[D:\Code\BeginningWithAI\experiments\phase3\test_mcp_client.py](D:/Code/BeginningWithAI/experiments/phase3/test_mcp_client.py)
- 建议逐行顺序： [server = Server(...)](D:/Code/BeginningWithAI/experiments/phase3/exp3_4_mcp_server.py:76) → [list_tools()](D:/Code/BeginningWithAI/experiments/phase3/exp3_4_mcp_server.py:88) → [call_tool()](D:/Code/BeginningWithAI/experiments/phase3/exp3_4_mcp_server.py:175)
- 如果你想看 Agent 侧如何把 MCP 工具转成可调用对象，再继续读： [MCPToolDiscovery](D:/Code/BeginningWithAI/experiments/phase3/exp3_4c_mcp_langchain_agent.py:90) → [MCPToolAdapter](D:/Code/BeginningWithAI/experiments/phase3/exp3_4c_mcp_langchain_agent.py:298)

### 📖 核心概念：MCP (Model Context Protocol)

Anthropic 提出的开放协议，用于标准化 AI 模型与外部工具的交互。

```
AI 模型 ←→ MCP Client ←→ MCP Server ←→ 外部工具/数据
```

### MCP 基础结构

```
MCP Server
├── Resources  # 暴露数据资源
├── Tools      # 提供可调用函数
├── Prompts    # 预定义提示词模板
└── Transport  # 通信层 (stdio/HTTP)
```

### 代码示例

创建文件 `experiments/phase3/exp3_4_mcp_server.py`：

```python
"""
实验 3.5: MCP Server - 安全工具集成
将 Nmap 等安全工具封装为 MCP 服务
"""
import asyncio
import json
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# 创建 MCP Server
server = Server("security-tools")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """列出可用工具"""
    return [
        types.Tool(
            name="nmap_scan",
            description="使用 Nmap 扫描目标主机",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "目标 IP 或主机名"
                    },
                    "scan_type": {
                        "type": "string",
                        "enum": ["quick", "full", "vuln"],
                        "description": "扫描类型: quick(快速), full(全端口), vuln(漏洞)"
                    }
                },
                "required": ["target"]
            }
        ),
        types.Tool(
            name="whois_lookup",
            description="查询域名 WHOIS 信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "要查询的域名"
                    }
                },
                "required": ["domain"]
            }
        ),
        types.Tool(
            name="dns_enum",
            description="DNS 枚举，获取域名解析记录",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "目标域名"
                    },
                    "record_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "记录类型: A, AAAA, MX, NS, TXT 等"
                    }
                },
                "required": ["domain"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """执行工具"""

    if name == "nmap_scan":
        result = await run_nmap_scan(
            arguments["target"],
            arguments.get("scan_type", "quick")
        )
    elif name == "whois_lookup":
        result = await run_whois(arguments["domain"])
    elif name == "dns_enum":
        result = await run_dns_enum(
            arguments["domain"],
            arguments.get("record_types", ["A", "MX", "NS"])
        )
    else:
        result = {"error": f"Unknown tool: {name}"}

    return [types.TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False, indent=2)
    )]


async def run_nmap_scan(target: str, scan_type: str) -> dict:
    """执行 Nmap 扫描"""
    try:
        import nmap
        nm = nmap.PortScanner()

        if scan_type == "quick":
            nm.scan(target, arguments="-F -T4")
        elif scan_type == "full":
            nm.scan(target, arguments="-p- -T4")
        elif scan_type == "vuln":
            nm.scan(target, arguments="--script vuln -T4")

        results = {
            "target": target,
            "scan_type": scan_type,
            "hosts": []
        }

        for host in nm.all_hosts():
            host_info = {
                "ip": host,
                "state": nm[host].state(),
                "ports": []
            }
            for proto in nm[host].all_protocols():
                for port in nm[host][proto].keys():
                    port_info = nm[host][proto][port]
                    host_info["ports"].append({
                        "port": port,
                        "state": port_info["state"],
                        "service": port_info.get("name", "unknown")
                    })
            results["hosts"].append(host_info)

        return results

    except ImportError:
        return {"error": "python-nmap not installed"}
    except Exception as e:
        return {"error": str(e)}


async def run_whois(domain: str) -> dict:
    """WHOIS 查询"""
    try:
        import whois
        w = whois.whois(domain)
        return {
            "domain": domain,
            "registrar": w.registrar,
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "name_servers": w.name_servers
        }
    except ImportError:
        return {"error": "python-whois not installed"}
    except Exception as e:
        return {"error": str(e)}


async def run_dns_enum(domain: str, record_types: list) -> dict:
    """DNS 枚举"""
    import socket
    results = {"domain": domain, "records": {}}

    for rtype in record_types:
        try:
            if rtype == "A":
                ip = socket.gethostbyname(domain)
                results["records"]["A"] = [ip]
            # 其他记录类型可添加 dnspython 支持
        except Exception as e:
            results["records"][rtype] = [f"Error: {str(e)}"]

    return results


async def main():
    """启动 MCP Server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="security-tools",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
```

### Claude Code MCP 配置

#### 配置模板

在项目根目录创建 `.mcp.json`：

```json
{
  "mcpServers": {
    "<server-name>": {
      "command": "<执行命令>",
      "args": ["<参数1>", "<参数2>"]
    }
  }
}
```

#### 当前配置示例

```json
// .mcp.json
{
  "mcpServers": {
    "security-tools": {
      "command": "python",
      "args": ["D:\\Code\\BeginningWithAI\\experiments\\phase3\\exp3_4_mcp_server.py"]
    }
  }
}
```

#### 检查 MCP Server

| 命令     | 作用               |
| ------ | ---------------- |
| `/mcp` | 连接/重连 MCP Server |

运行 `/mcp` 后显示 "Reconnected to <server-name>" 表示连接成功。

### 验证标准

- [ ] MCP Server 启动无报错
- [ ] 工具列表正确返回
- [ ] 工具调用返回预期结果
  
  

### MCP 底层原理深入

> 理解 MCP 的通信协议和代码执行流程，才能在出问题时快速定位。

#### MCP 通信本质：stdin/stdout 上的 JSON-RPC

MCP Client 调用本地 MCP Server，本质是启动一个子进程，通过标准输入输出通信：

```
┌─────────────────────────────────────────────────────────────┐
│  MCP Client 进程                    MCP Server 进程         │
│  ┌─────────────────┐    stdin/stdout    ┌─────────────────┐ │
│  │  Python 脚本    │ ◄────────────────► │  python exp3_4  │ │
│  │  (ClientSession)│   JSON-RPC 消息    │  _mcp_server.py │ │
│  └─────────────────┘                    └─────────────────┘ │
│        Shell 启动子进程                                      │
└─────────────────────────────────────────────────────────────┘
```

**`.mcp.json` 配置就是告诉 Client 如何启动子进程：**

```json
{
  "command": "python",                    // 执行器
  "args": ["exp3_4_mcp_server.py"]        // 参数
}
```

等效于 Shell 命令：`python exp3_4_mcp_server.py`

#### MCP 消息格式（JSON-RPC）

**初始化请求：**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "claude-code", "version": "1.0"}
  }
}
```

**获取工具列表：**

```json
{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
```

**调用工具：**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "nmap_scan",
    "arguments": {"target": "39.156.66.10", "scan_type": "quick"}
  }
}
```

| 字段        | 说明                                         |
| --------- | ------------------------------------------ |
| `jsonrpc` | 固定 `"2.0"`，JSON-RPC 版本                     |
| `id`      | 请求 ID，用于匹配响应                               |
| `method`  | 方法名：`initialize`、`tools/list`、`tools/call` |
| `params`  | 参数，不同方法结构不同                                |

#### MCP Server 代码结构

完整代码见 `experiments/phase3/exp3_4_mcp_server.py`，核心结构：

| 组件                         | 作用              | 触发条件               |
| -------------------------- | --------------- | ------------------ |
| `Server("security-tools")` | 创建服务器实例         | 启动时                |
| `@server.list_tools()`     | 注册工具列表函数        | 收到 `tools/list` 请求 |
| `@server.call_tool()`      | 注册工具执行函数        | 收到 `tools/call` 请求 |
| `stdio_server()`           | 监听 stdin/stdout | 启动时                |
| `server.run()`             | 启动事件循环          | 启动时                |

#### 完整执行流程图

```
python exp3_4_mcp_server.py
        │
        ▼
asyncio.run(main())
        │
        ▼
stdio_server() ──── 监听 stdin
        │
        ▼
server.run() ──── 进入事件循环
        │
        │  ◄─── stdin: {"method": "initialize", ...}
        ▼
返回服务器信息 ──── 写入 stdout
        │
        │  ◄─── stdin: {"method": "tools/list"}
        ▼
自动调用 list_tools() ──── 返回工具定义
        │
        │  ◄─── stdin: {"method": "tools/call", "params": {"name": "nmap_scan", ...}}
        ▼
自动调用 call_tool("nmap_scan", {...})
        │
        ▼
run_nmap_scan() ──── 执行实际扫描
        │
        ▼
返回结果 ──── 写入 stdout
```

#### 手动测试 MCP Server

```powershell
# PowerShell / Bash（支持单引号）
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | python exp3_4_mcp_server.py
```

```cmd
# Windows CMD（不支持单引号，JSON 中双引号无需转义）
echo {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{}, "clientInfo":{"name":"test","version":"1.0"}}} | python exp3_4_mcp_server.py
```

**输出：**

```json
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"tools":{"listChanged":false}},"serverInfo":{"name":"security-tools","version":"0.1.0"}}}
```

**测试工具列表（需要先发送初始化消息）：**

```powershell
# PowerShell / Bash（多行消息用反引号或字符串拼接）
# 先发送 initialize，再发送 tools/list
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | python exp3_4_mcp_server.py
```

```cmd
# Windows CMD（创建临时文件方式发送多行消息）
(echo {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{}, "clientInfo":{"name":"test","version":"1.0"}}} && echo {"jsonrpc":"2.0","id":2,"method":"tools/list"}) | python exp3_4_mcp_server.py
```

**输出：**

```json
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05",...}}
{"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"nmap_scan","description":"使用 Nmap 扫描目标主机",...},{"name":"whois_lookup",...},{"name":"dns_enum",...}]}}
```

### 场景 B：MCP Client 编程实例

> 前面实验只开发了 MCP Server（暴露工具），但实际使用中还需要 **MCP Client** 来连接 Server、发现工具、调用工具。MCP在agent端的本质，就是获取mcp server的tools list作为function call的工具列表。

#### MCP Client 的核心职责

```
MCP Server（工具提供者）          MCP Client（驱动者）
├── 暴露 Tools                    ├── 连接 Server（initialize）
├── 暴露 Resources                ├── 发现可用工具（tools/list）
└── 等待被调用                    ├── 调用工具并获取结果（tools/call）
                                  └── 将工具信息转换给 LLM 使用
```

**关键问题：Client 如何让 Agent 知道 Server 有哪些工具？**

答案：MCP Client 通过 session.list_tools() 从 Server 获取工具列表，然后通过 MCPToolAdapter 转换为 LangChain Tool 格式，最后通过 create_agent(llm, tools) 将工具列表传给 Agent。

#### MCP 工具发现流程

```
┌─────────────────────────────────────────────────────────────────┐
│                     MCP Client 工具发现流程                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 连接 Server                                                 │
│     Client ────────stdio_client()──────► Server 进程           │
│                                                                 │
│  2. 初始化 (initialize)                                         │
│     Client ───initialize()───► Server                           │
│     Client ◄───serverInfo + capabilities─── Server             │
│     返回: Server 名称、版本、支持的能力                            │
│                                                                 │
│  3. 发现工具 (tools/list)                                       │
│     Client ───list_tools()───► Server                           │
│     Client ◄───[Tool{name, description, inputSchema}]─── Server│
│     返回: 工具名称、描述、参数 JSON Schema                         │
│                                                                 │
│  4. 转换格式 (MCP → LangChain/OpenAI)                           │
│     MCP Tool.inputSchema ──► OpenAI function.parameters        │
│     MCP Tool.name ─────────► OpenAI function.name              │
│                                                                 │
│  5. 传给 Agent 使用                                              │
│     tools 被传入 Agent，LLM 自动决策何时调用                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### MCP vs Function Calling 架构对比

| 对比项      | Function Calling | MCP                         |
| -------- | ---------------- | --------------------------- |
| **工具位置** | 你的 Python 代码里    | 独立运行的进程                     |
| **谁调用**  | 你的程序             | Claude Desktop / 任何 MCP 客户端 |
| **通信方式** | 直接函数调用           | JSON-RPC（网络协议）              |
| **可复用性** | 仅你的程序            | 任何 MCP 客户端都能用               |
| **类比**   | 你家厨房自己做菜         | 外卖平台连接各餐厅                   |

#### 代码示例：exp3_4c_mcp_langchain_agent.py

完整的 MCP Client 实现，包含三个核心类：

```
exp3_4c_mcp_langchain_agent.py
├── MCPToolDiscovery      # MCP 连接管理器
│   ├── connect()         # 连接 + 初始化
│   ├── discover_tools()  # tools/list 发现工具
│   └── call_tool()       # tools/call 调用工具
│
├── MCPToolAdapter        # MCP → LangChain 适配器
│   └── 动态创建 Pydantic 参数模型
│
├── create_langchain_tools_from_mcp()  # 工厂函数
│
└── run_langchain_agent() # LangChain Agent 示例
```

**核心类 1：MCPToolDiscovery - 连接与发现**

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPToolDiscovery:
    """MCP 工具发现器：连接 Server、发现工具、管理会话"""

    def __init__(self, command: str, args: list[str]):
        self.command = command
        self.args = args
        self.session: Optional[ClientSession] = None

    async def connect(self):
        """连接到 MCP Server 并初始化"""
        server_params = StdioServerParameters(
            command=self.command,
            args=self.args,
        )

        # 建立 stdio 连接
        self._stdio_context = stdio_client(server_params)
        read, write = await self._stdio_context.__aenter__()

        # 创建会话
        self._session_context = ClientSession(read, write)
        self.session = await self._session_context.__aenter__()

        # 初始化协议，获取 Server 信息
        init_result = await self.session.initialize()
        return init_result  # 包含 serverInfo, capabilities

    async def discover_tools(self) -> list:
        """发现 MCP Server 提供的所有工具"""
        result = await self.session.list_tools()
        return result.tools  # 每个 tool 包含 name, description, inputSchema

    async def call_tool(self, name: str, arguments: dict) -> str:
        """调用 MCP 工具并返回结果"""
        result = await self.session.call_tool(name, arguments=arguments)
        for content in result.content:
            if content.type == "text":
                return content.text
        return str(result.content)

    async def disconnect(self):
        """断开连接"""
        await self._session_context.__aexit__(None, None, None)
        await self._stdio_context.__aexit__(None, None, None)
```

**核心类 2：MCPToolAdapter - 格式转换**

```python
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

class MCPToolAdapter(BaseTool):
    """
    将 MCP 工具适配为 LangChain Tool
    核心功能：将 MCP 的 JSON Schema 转换为 LangChain 需要的 Pydantic 模型
    """

    mcp_discovery: MCPToolDiscovery = None
    mcp_tool_name: str = ""

    def __init__(self, name: str, description: str,
                 mcp_discovery: MCPToolDiscovery, input_schema: dict):
        # 动态创建 Pydantic 参数模型
        args_model = self._create_args_model(name, input_schema)

        super().__init__(
            name=name,
            description=description,
            mcp_discovery=mcp_discovery,
            mcp_tool_name=name,
            args_schema=args_model
        )

    @staticmethod
    def _create_args_model(tool_name: str, schema: dict) -> Type[BaseModel]:
        """根据 JSON Schema 动态创建 Pydantic 模型"""
        fields = {}
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))

        type_map = {
            "string": str, "integer": int, "number": float,
            "boolean": bool, "array": list, "object": dict
        }

        for prop_name, prop_def in properties.items():
            prop_type = prop_def.get("type", "string")
            description = prop_def.get("description", "")
            default = ... if prop_name in required else None
            python_type = type_map.get(prop_type, str)
            fields[prop_name] = (python_type, Field(default=default, description=description))

        return type(f"{tool_name.title()}Args", (BaseModel,),
                    {"__annotations__": {k: v[0] for k, v in fields.items()},
                     **{k: v[1] for k, v in fields.items()}})

    async def _arun(self, **kwargs) -> str:
        """异步执行 - 调用 MCP Server"""
        return await self.mcp_discovery.call_tool(self.mcp_tool_name, kwargs)
```

**核心流程 3：工厂函数**

```python
async def create_langchain_tools_from_mcp(
    command: str, args: list[str]
) -> tuple[MCPToolDiscovery, list[BaseTool]]:
    """从 MCP Server 创建 LangChain 工具集"""

    # 1. 创建发现器并连接
    discovery = MCPToolDiscovery(command, args)
    init_result = await discovery.connect()
    print(f"已连接: {init_result.serverInfo.name}")
    print(f"能力: {init_result.capabilities}")

    # 2. 发现工具
    mcp_tools = await discovery.discover_tools()
    print(f"发现 {len(mcp_tools)} 个工具")

    # 3. 转换为 LangChain Tools
    langchain_tools = [
        MCPToolAdapter(t.name, t.description, discovery, t.inputSchema)
        for t in mcp_tools
    ]

    return discovery, langchain_tools
```

**完整 Agent 示例**

```python
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

async def run_langchain_agent(backend: str = "openai"):
    # 1. 连接 MCP Server 并发现工具
    discovery, tools = await create_langchain_tools_from_mcp(
        command="python",
        args=["experiments/phase3/exp3_4_mcp_server.py"]
    )

    try:
        # 2. 创建 LLM（支持 Ollama 和 OpenAI 兼容 API）
        if backend == "ollama":
            llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"))
        else:
            llm = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "deepseek-v4-pro"),
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),
            )

        # 3. 创建 Agent
        agent = create_agent(
            llm, tools,
            system_prompt="你是一个网络安全分析助手，可以使用 DNS 和 WHOIS 工具帮助用户分析域名。"
        )

        # 4. 执行任务
        result = await agent.ainvoke({
            "messages": [("user", "查询 github.com 的 DNS A 记录")]
        })

    finally:
        await discovery.disconnect()
```

#### 运行方式

```bash
# 测试工具发现（不使用 LLM）
python exp3_4c_mcp_langchain_agent.py --mode discover

# 运行 Agent (OpenAI 兼容 API)
python exp3_4c_mcp_langchain_agent.py --backend openai

# 运行 Agent (本地 Ollama)
python exp3_4c_mcp_langchain_agent.py --backend ollama
```

#### 关键 API 速查

| 操作   | MCP SDK 方法                      | 返回值                                                       |
| ---- | ------------------------------- | --------------------------------------------------------- |
| 初始化  | `session.initialize()`          | `serverInfo`, `capabilities`                              |
| 发现工具 | `session.list_tools()`          | `tools: [Tool]`，每个包含 `name`, `description`, `inputSchema` |
| 调用工具 | `session.call_tool(name, args)` | `content: [TextContent]`                                  |
| 发现资源 | `session.list_resources()`      | `resources: [Resource]`                                   |
| 读取资源 | `session.read_resource(uri)`    | `contents`                                                |

#### Server 能力检测

```python
init_result = await session.initialize()

# 获取 Server 基本信息
print(f"Server: {init_result.serverInfo.name} v{init_result.serverInfo.version}")

# 检查 Server 支持的能力
capabilities = init_result.capabilities
# capabilities.tools     - 是否支持工具
# capabilities.resources - 是否支持资源
# capabilities.prompts   - 是否支持提示词模板
```

#### MCP Client 深入理解 Q&A

**Q1: 为什么在代码中看不到 tool.invoke() 调用？**

因为调用在 LangChain 框架内部，不是在你的代码中：

| 层面   | 你写的代码             | 框架做的事                 |
| ---- | ----------------- | --------------------- |
| 调用入口 | `agent.ainvoke()` | 内部自动处理                |
| 工具匹配 | 无                 | 根据 tool_calls.name 匹配 |
| 工具调用 | 无                 | `tool.ainvoke(args)`  |
| 结果处理 | 无                 | 包装为 ToolMessage       |

**理解**：框架封装了完整的调用链，你只需定义工具（继承 BaseTool），框架负责调用。

**Q2: BaseTool 的模板方法模式是什么？**

```
┌─────────────────────────────────────────┐
│ 模板方法模式                              │
├─────────────────────────────────────────┤
│                                         │
│  BaseTool (父类)                         │
│  ├── invoke()     [公开接口，不重写]      │
│  └── _run()       [抽象方法，子类实现]    │
│                                         │
│  MCPToolAdapter (子类)                   │
│  └── _run()       [重写，实现具体逻辑]    │
│                                         │
│  调用链：                                 │
│  invoke() → self._run()                 │
│  [父类方法]  [子类实现]                   │
│                                         │
└─────────────────────────────────────────┘
```

关键理解：

- `invoke()` 是框架调用的入口（父类实现）
- `_run()` / `_arun()` 是你实现的具体逻辑（子类重写）
- 这就是模板方法模式：父类定义骨架，子类填充细节

**Q3: 同步/异步双路径设计是怎样的？**

```
┌─────────────────────────────────────────┐
│ 双路径设计                               │
├─────────────────────────────────────────┤
│                                         │
│  agent.invoke()  ──►  tool.invoke()     │
│       [同步]               ↓             │
│                          _run()         │
│                                         │
│  agent.ainvoke() ──► tool.ainvoke()     │
│       [异步]               ↓             │
│                          _arun()        │
│                                         │
└─────────────────────────────────────────┘
```

| 场景       | 调用方式              | 执行路径      |
| -------- | ----------------- | --------- |
| 异步 Agent | `agent.ainvoke()` | `_arun()` |
| 同步 Agent | `agent.invoke()`  | `_run()`  |

为什么有时只执行 `_arun()` 不执行 `_run()`？因为你用的是 `ainvoke()`，走的是异步路径。`_run()` 内部用 `asyncio.run()` 包装 `_arun()` 作为同步兼容层。

**Q4: Agent 工具调用的完整链路是什么？**

```
┌─────────────────────────────────────────┐
│ 完整调用链                               │
├─────────────────────────────────────────┤
│                                         │
│  1. 用户输入                             │
│        ↓                                │
│  2. LLM 返回 AIMessage                   │
│     (tool_calls=[{name, args}])         │
│        ↓                                │
│  3. Agent 框架匹配工具                   │
│     find_tool(name) → MCPToolAdapter    │
│        ↓                                │
│  4. 框架调用 tool.ainvoke(args)          │
│        ↓                                │
│  5. BaseTool.ainvoke()                   │
│        ↓                                │
│  6. MCPToolAdapter._arun()               │
│        ↓                                │
│  7. mcp_discovery.call_tool()            │
│        ↓                                │
│  8. MCP Server 执行                      │
│        ↓                                │
│  9. 返回 ToolMessage                     │
│        ↓                                │
│  10. LLM 生成最终回答                    │
│                                         │
└─────────────────────────────────────────┘
```

**关键理解**：不是你"启动"工具调用，而是 LLM 决定调用什么，框架负责执行。

**Q5: AI 的回答一定是最终回答吗？**

不一定，需要判断消息类型：

| 消息类型                               | 特征     | 含义   |
| ---------------------------------- | ------ | ---- |
| AIMessage + tool_calls             | 有工具调用  | 中间步骤 |
| AIMessage + content + 无 tool_calls | 有内容无调用 | 最终回答 |
| ToolMessage                        | 工具返回结果 | 中间步骤 |

正确判断方式：

```python
# 检查是否有工具调用
if hasattr(msg, "tool_calls") and msg.tool_calls:
    # 中间步骤：LLM 决定调用工具
    for tc in msg.tool_calls:
        print(f"调用: {tc['name']}({tc['args']})")
elif msg.type == "ai" and msg.content:
    # 可能是最终回答（需确认无 tool_calls）
    print(f"回答: {msg.content}")
```

**Q6: OpenCode 和 OpenClaw 的 MCP 实现有什么不同？**

**OpenCode（直接集成模式）**：

```typescript
// 使用官方 MCP TypeScript SDK + Vercel AI SDK
import { Client } from "@modelcontextprotocol/sdk/client/index.js"
import { dynamicTool, jsonSchema } from "ai"

// 工具转换：MCP Tool → Vercel AI SDK Tool
async function convertMcpTool(mcpTool, client) {
  return dynamicTool({
    description: mcpTool.description,
    inputSchema: jsonSchema(mcpTool.inputSchema),
    execute: async (args) => {
      return client.callTool({
        name: mcpTool.name,
        arguments: args
      })
    }
  })
}
```

**OpenClaw（代理模式）**：

```typescript
// MCP Proxy：拦截 session/new 注入 MCP 配置
function buildMcpProxyAgentCommand(targetCommand, mcpServers) {
  const payload = Buffer.from(JSON.stringify({
    targetCommand,
    mcpServers
  })).toString("base64url")

  return `node mcp-proxy.mjs --payload ${payload}`
}

// Proxy 拦截并重写 JSON-RPC 消息
function rewriteLine(line, mcpServers) {
  const parsed = JSON.parse(line)
  if (parsed.method === "session/new") {
    parsed.params.mcpServers = mcpServers  // 注入配置
  }
  return JSON.stringify(parsed)
}
```

| 对比项          | OpenCode                      | OpenClaw                          |
| ------------ | ----------------------------- | --------------------------------- |
| **架构**       | 直接集成 MCP SDK                  | MCP Proxy 代理模式                    |
| **工具转换**     | MCP Tool → Vercel AI SDK Tool | 注入配置到 Agent session               |
| **Agent 类型** | 单一 Agent                      | 多 Agent 支持（codex, claude, gemini） |
| **通信方式**     | stdin/stdout, SSE, HTTP       | 进程间代理                             |

**共同点**：都需要将 MCP 工具转换为对应框架的工具格式。

## 🧪 实验 3.7：Skill 编写基础

### 目标

掌握 SKILL.md 文件结构，学会编写基础 Skill。

### 对应代码文件与逐行阅读入口

- 主文件：[D:\Code\BeginningWithAI\experiments\phase3\exp3_7_skill_loader.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_7_skill_loader.py)
- 建议逐行顺序： [SkillMetadata](D:/Code/BeginningWithAI/experiments/phase3/exp3_7_skill_loader.py:26) → [SkillLoader.__init__()](D:/Code/BeginningWithAI/experiments/phase3/exp3_7_skill_loader.py:83) → [scan_skills()](D:/Code/BeginningWithAI/experiments/phase3/exp3_7_skill_loader.py:133) → [_parse_skill_metadata()](D:/Code/BeginningWithAI/experiments/phase3/exp3_7_skill_loader.py:175) → [load_skill()](D:/Code/BeginningWithAI/experiments/phase3/exp3_7_skill_loader.py:226) → [build_system_prompt()](D:/Code/BeginningWithAI/experiments/phase3/exp3_7_skill_loader.py:274)
- 这一章逐行阅读的重点不是模型，而是 Skill 元数据如何被发现、完整指令何时加载、系统提示词如何动态拼接。

**核心设计哲学**：Skill = 提示词模板 + 渐进式加载。让大模型成为真正的"智能体"，自己阅读指令、发现脚本、决定执行。

### 📖 核心概念：Skills 三层加载机制

与传统工具调用不同，Skills 采用**渐进式加载**策略，平衡 Token 消耗与功能丰富度：

```
┌─────────────────────────────────────────────────────────────┐
│              Agent Skills 三层渐进式加载机制                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Level 1: 元数据层 (Metadata)                                │
│  ├── 内容: name + description（YAML frontmatter）            │
│  ├── 加载时机: Agent 启动时                                  │
│  ├── Token 消耗: ~100 tokens/Skill                          │
│  └── 用途: 注入 System Prompt，让模型知道有哪些 Skills        │
│                      │                                      │
│                      ▼ (用户请求匹配时)                      │
│                                                             │
│  Level 2: 指令层 (Instructions)                             │
│  ├── 内容: SKILL.md 完整内容（Markdown body）                 │
│  ├── 加载时机: Skill 触发时                                  │
│  ├── Token 消耗: <5000 tokens                               │
│  └── 用途: 通过 load_skill 工具按需加载详细指令              │
│                      │                                      │
│                      ▼ (执行脚本时)                          │
│                                                             │
│  Level 3: 执行层 (Execution)                                 │
│  ├── 内容: scripts/ 目录下的脚本执行输出                     │
│  ├── 加载时机: 运行时                                       │
│  ├── Token 消耗: 仅输出入上下文（代码不进）                  │
│  └── 用途: 通过 bash 工具执行，获取结果                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**类比理解**：

- Level 1 = 书籍目录（知道有什么）
- Level 2 = 章节内容（知道怎么做）
- Level 3 = 代码运行结果（得到实际输出）

### Skill 与其他工具调用模式的区别

| 维度           | Skill       | MCP         | Shell Tool     | Function Calling |
| ------------ | ----------- | ----------- | -------------- | ---------------- |
| **知识来源**     | SKILL.md 文档 | Server 自动发现 | 预训练知识 + Prompt | JSON Schema 显式定义 |
| **Token 效率** | ⭐⭐⭐ 渐进式加载   | ⭐⭐ 中等       | ⭐ 全进上下文        | ⭐⭐⭐ 精确控制         |
| **调用确定性**    | ⭐⭐ 中        | ⭐⭐⭐ 高       | ⭐ 弱            | ⭐⭐⭐ 高            |
| **安全性**      | ⭐⭐ 中        | ⭐⭐⭐ 受控      | ⭐ 高风险          | ⭐⭐⭐ 受控           |
| **适用场景**     | 复杂流程、领域知识   | 工具服务化       | 开发探索           | 生产环境             |

### SKILL.md 文件结构

````markdown
---
name: skill-name                    # Skill 唯一标识
description: 何时使用此 Skill 的描述   # 用于 Level 1 匹配
---

# Skill 标题

## 工作流程

1. 步骤一
2. 步骤二
3. 步骤三

## 可用脚本

### script.py - 脚本说明

```bash
python scripts/script.py <参数>
```

### 参数说明：

* `param1`: 参数1说明
* `param2`: 参数2说明

````

#### 使用示例

**示例场景**：

```bash
python scripts/script.py exampl
```

#### 变量替换机制

Skills 支持以下变量替换：

| 变量                    | 含义           | 示例值                                  |
| --------------------- | ------------ | ------------------------------------ |
| `$ARGUMENTS`          | 用户输入的完整参数    | `arg1 arg2`                          |
| `$0`                  | Skill 名称     | `skill-name`                         |
| `${CLAUDE_SKILL_DIR}` | Skill 目录绝对路径 | `/path/to/.claude/skills/skill-name` |

---

### 步骤 1：创建第一个 Skill（Hello World）

**目标**：掌握 SKILL.md 基本结构，理解三层加载机制。

#### 1.1 创建 Skill 目录结构

在项目根目录执行：

```bash
mkdir -p .claude/skills/hello-world/scripts
```

#### 1.2 编写 SKILL.md

创建 `.claude/skills/hello-world/SKILL.md`：

````markdown
---
name: hello-world
description: 向你问好。当用户说"你好"、"hello"或需要问候时激活。
---

# Hello World Skill

这是一个最简单的 Skill 示例，展示 Skills 的基本结构。

## 工作流程

1. 获取当前时间
2. 根据时间返回不同的问候语
3. 如果提供了名字，使用个性化问候

## 可用脚本

### hello.py - 问候脚本

```bash
python scripts/hello.py [名字]
```

参数：

- 可选的位置参数：名字，默认"朋友"

示例输出：

```
当前时间: 2024-01-15 09:30
问候: 早上好，Alice！
```

## 实现细节

- 使用 Python 的 `datetime` 模块获取当前时间

- 根据小时判断时段：5-12点早上，12-18点下午，其他晚上

- 脚本路径相对于 Skill 目录
````



#### 1.3 创建脚本

创建 `.claude/skills/hello-world/scripts/hello.py`：

```python
#!/usr/bin/env python3
"""问候脚本"""
import sys
from datetime import datetime

name = sys.argv[1] if len(sys.argv) > 1 else "朋友"
hour = datetime.now().hour

if 5 <= hour < 12:
    greeting = "早上好"
elif 12 <= hour < 18:
    greeting = "下午好"
else:
    greeting = "晚上好"

print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"问候: {greeting}，{name}！")
```

#### 1.4 在 Claude Code 中验证 Skill

由于 Skill 文件已创建在项目根目录的 `.claude/skills/` 下，Claude Code 会自动发现并加载这些 Skill。

**验证方式**：在 Claude Code 中直接调用 Skill

```
用户: /hello-world
```

**预期行为**：
1. Claude Code 识别到 `hello-world` Skill 被触发
2. 自动加载 `.claude/skills/hello-world/SKILL.md` 的完整指令
3. 根据指令执行 `python scripts/hello.py`
4. 返回问候结果：

```
当前时间: 2024-01-15 09:30
问候: 早上好，朋友！
```

**验证要点**：
- ✓ Skill 能被正确识别和触发（Level 1 元数据有效）
- ✓ Skill 指令被正确加载和执行（Level 2 指令有效）
- ✓ 脚本被正确执行并返回结果（Level 3 执行有效）

#### 1.5 验证个性化问候

```
用户: /hello-world Alice
```

**预期输出**：

```
当前时间: 2024-01-15 09:30
问候: 早上好，Alice！
```

这验证了 Skill 支持参数传递（`$ARGUMENTS` 变量工作正常）。

---

### 步骤 2：创建带脚本的 Skill（Port Scanner）

**目标**：创建带参数传递的 Skill，理解变量替换。

#### 2.1 创建目录

```bash
mkdir -p .claude/skills/port-scanner/scripts
```

#### 2.2 编写 SKILL.md

创建 `.claude/skills/port-scanner/SKILL.md`：

````markdown
---
name: port-scanner
description: 扫描目标主机的端口开放情况。当用户需要检查端口、扫描主机、检查服务是否运行时激活。
---

# 端口扫描 Skill

使用 TCP 连接扫描目标主机的端口状态。

## 工作流程

1. 解析用户提供的目标主机和端口
2. 执行端口扫描脚本
3. 返回扫描结果

## 可用脚本

### scan.py - 端口扫描器

```bash
python scripts/scan.py <host> <port1,port2,...>
```

参数：

- `host`: 目标主机 IP 或域名
- `ports`: 要扫描的端口列表（逗号分隔）

示例：

```bash
python scripts/scan.py localhost 80,443,22,3306
```

输出格式：

```
扫描目标: localhost
端口 80: open
端口 443: closed
端口 22: open
端口 3306: closed
```
````

#### 2.3 使用示例

**扫描常见 Web 端口**：

```bash
python scripts/scan.py example.com 80,443,8080,8443
```

**扫描数据库端口**：

```bash
python scripts/scan.py db.server.local 3306,5432,27017,6379
```

#### 2.4 创建扫描脚本

创建 `.claude/skills/port-scanner/scripts/scan.py`：

```python
#!/usr/bin/env python3
"""端口扫描脚本"""
import sys
import socket

def scan_port(host: str, port: int) -> str:
    """扫描单个端口"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return "open" if result == 0 else "closed"
    except Exception as e:
        return f"error: {e}"

def main():
    if len(sys.argv) < 3:
        print("用法: python scan.py <host> <port1,port2,...>")
        sys.exit(1)

    host = sys.argv[1]
    ports_str = sys.argv[2]
    ports = [int(p.strip()) for p in ports_str.split(",")]

    print(f"扫描目标: {host}")
    for port in ports:
        status = scan_port(host, port)
        print(f"端口 {port}: {status}")

if __name__ == "__main__":
    main()
```

---

## 🧪 实验 3.8：Skills Agent 实现

### 目标

实现支持 Skills 的 ReAct Agent，验证三层加载机制。

### 对应代码文件与逐行阅读入口

- 主文件：[D:\Code\BeginningWithAI\experiments\phase3\exp3_7b_skills_agent.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_7b_skills_agent.py)
- CLI 验证入口：[D:\Code\BeginningWithAI\experiments\phase3\exp3_7c_skills_cli.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_7c_skills_cli.py)
- 建议逐行顺序： [load_skill_tool()](D:/Code/BeginningWithAI/experiments/phase3/exp3_7b_skills_agent.py:53) → [bash_tool()](D:/Code/BeginningWithAI/experiments/phase3/exp3_7b_skills_agent.py:101) → [SkillsAgent.__init__()](D:/Code/BeginningWithAI/experiments/phase3/exp3_7b_skills_agent.py:172) → [_create_system_prompt()](D:/Code/BeginningWithAI/experiments/phase3/exp3_7b_skills_agent.py:220) → [_build_tools_for_api()](D:/Code/BeginningWithAI/experiments/phase3/exp3_7b_skills_agent.py:318) → [run()](D:/Code/BeginningWithAI/experiments/phase3/exp3_7b_skills_agent.py:362)
- CLI 对照入口： [list_skills()](D:/Code/BeginningWithAI/experiments/phase3/exp3_7c_skills_cli.py:39) → [show_system_prompt()](D:/Code/BeginningWithAI/experiments/phase3/exp3_7c_skills_cli.py:66) → [interactive_mode()](D:/Code/BeginningWithAI/experiments/phase3/exp3_7c_skills_cli.py:111)

### 📖 核心概念：Skills Agent 架构

Skills Agent 在既有 ReAct Agent 基础上增加了：

1. **SkillLoader** - Level 1/2 加载器
   
   - `scan_skills()`：发现 Skills，解析元数据
   - `load_skill()`：按需加载 SKILL.md 完整指令
   - `build_system_prompt()`：生成包含 Skills 列表的 system prompt

2. **Tools 扩展** - Level 3 执行
   
   - `load_skill_tool`：供模型调用，加载 Skill 指令
   - `bash_tool`：执行脚本，代码不进入上下文

三层加载流程：

```
用户请求 → Level 1 (扫描元数据注入 System Prompt)
              ↓
         匹配 Skill → Level 2 (调用 load_skill 获取指令)
                          ↓
                     执行脚本 → Level 3 (调用 bash 获取输出)
```

### 步骤 1：SkillLoader 实现（Level 1/2）

SkillLoader 是 Skills Agent 的核心组件，负责 Level 1 和 Level 2 的加载：

```python
"""
实验 3.7：Skills 三层加载机制核心实现
"""
import re
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class SkillMetadata:
    """Level 1: Skill 元数据（约 100 tokens）"""
    name: str
    description: str
    skill_path: Path

    def to_prompt_line(self) -> str:
        return f"- **{self.name}**: {self.description}"


@dataclass
class SkillContent:
    """Level 2: Skill 完整内容（小于 5000 tokens）"""
    metadata: SkillMetadata
    instructions: str


class SkillLoader:
    """
    Skills 加载器 - 实现三层加载机制

    核心职责：
    1. scan_skills(): 发现 Skills，解析元数据（Level 1）
    2. load_skill(): 按需加载 Skill 详细内容（Level 2）
    3. build_system_prompt(): 生成包含 Skills 列表的 system prompt

    默认搜索路径（项目级优先，用户级兜底）：
    - ./.claude/skills/      # 项目级 Skills
    - ~/.claude/skills/      # 用户级 Skills
    """

    DEFAULT_SKILL_PATHS = [
        Path.cwd() / ".claude" / "skills",
        Path.home() / ".claude" / "skills",
    ]

    def scan_skills(self) -> list[SkillMetadata]:
        """Level 1: 扫描所有 Skills 元数据"""
        skills = []
        seen_names = set()

        for base_path in self.skill_paths:
            if not base_path.exists():
                continue

            for skill_dir in base_path.iterdir():
                if not skill_dir.is_dir():
                    continue

                skill_md = skill_dir / "SKILL.md"
                if not skill_md.exists():
                    continue

                metadata = self._parse_skill_metadata(skill_md)
                if metadata and metadata.name not in seen_names:
                    skills.append(metadata)
                    seen_names.add(metadata.name)

        return skills

    def _parse_skill_metadata(self, skill_md_path: Path) -> Optional[SkillMetadata]:
        """解析 SKILL.md 的 YAML frontmatter"""
        content = skill_md_path.read_text(encoding="utf-8")

        # 提取 frontmatter: ---\n...\n---
        frontmatter_match = re.match(
            r'^---\s*\n(.*?)\n---\s*\n',
            content,
            re.DOTALL
        )

        if not frontmatter_match:
            return None

        frontmatter = yaml.safe_load(frontmatter_match.group(1))
        return SkillMetadata(
            name=frontmatter.get("name", ""),
            description=frontmatter.get("description", ""),
            skill_path=skill_md_path.parent,
        )

    def load_skill(self, skill_name: str) -> Optional[SkillContent]:
        """Level 2: 加载 Skill 完整内容"""
        # 获取缓存的元数据
        metadata = self._metadata_cache.get(skill_name)
        if not metadata:
            self.scan_skills()
            metadata = self._metadata_cache.get(skill_name)

        if not metadata:
            return None

        # 读取 SKILL.md 完整内容
        skill_md = metadata.skill_path / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")

        # 提取 body（去除 frontmatter）
        body_match = re.match(
            r'^---\s*\n.*?\n---\s*\n(.*)$',
            content,
            re.DOTALL
        )
        instructions = body_match.group(1).strip() if body_match else content

        return SkillContent(metadata=metadata, instructions=instructions)

    def build_system_prompt(self, base_prompt: str = "") -> str:
        """构建包含 Skills 列表的 system prompt"""
        skills = self.scan_skills()

        if skills:
            skills_section = "## Available Skills\n\n"
            skills_section += "You have access to the following skills:\n\n"
            for skill in skills:
                skills_section += skill.to_prompt_line() + "\n"
            skills_section += "\n### How to Use Skills\n\n"
            skills_section += "1. **Discover**: Review the skills list above\n"
            skills_section += "2. **Load**: When relevant, use `load_skill(skill_name)`\n"
            skills_section += "3. **Execute**: Follow instructions, run scripts via `bash`\n"
        else:
            skills_section = "## Skills\n\nNo skills available.\n"

        if base_prompt:
            return f"{base_prompt}\n\n{skills_section}"
        return f"You are a helpful assistant.\n\n{skills_section}"
```

**运行测试**：

```bash
# 测试 Level 1 扫描
python experiments/phase3/exp3_7_skill_loader.py
```

---

### 步骤 2：Skills Agent 实现（双模式）

**目标**：整合 SkillLoader 和工具，实现支持 Skills 的 ReAct Agent。

**文件**: `experiments/phase3/exp3_7b_skills_agent.py`

核心设计：

```python
"""
实验 3.7b：支持 Skills 的 ReAct Agent（双模式）
"""
import os
import json
import subprocess
from typing import Dict, Callable
from dotenv import load_dotenv

from exp3_7_skill_loader import SkillLoader, SkillContent
import ollama
from openai import OpenAI

load_dotenv()


def load_skill_tool(skill_name: str, skill_loader: SkillLoader) -> str:
    """
    工具：加载 Skill 详细指令（Level 2）
    当用户请求匹配某个 skill 的 description 时调用
    """
    skill_content = skill_loader.load_skill(skill_name)

    if not skill_content:
        return f"Skill '{skill_name}' not found"

    skill_path = skill_content.metadata.skill_path
    scripts_dir = skill_path / "scripts"

    return f"""# Skill: {skill_name}

## Instructions
{skill_content.instructions}

## Path Info
- Skill Directory: {skill_path}
- Scripts Directory: {scripts_dir}
"""


def bash_tool(command: str, cwd: str = ".") -> str:
    """
    工具：执行 shell 命令（Level 3）
    重要：脚本代码不进入上下文，只有输出进入
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            return f"[OK]\n\n{result.stdout}"
        else:
            return f"[FAILED] Exit code: {result.returncode}\n\n{result.stderr}"

    except Exception as e:
        return f"[FAILED] {str(e)}"


class SkillsAgent:
    """
    支持 Skills 的 ReAct Agent

    与既有 ReAct Agent 的主要区别：
    1. 集成 SkillLoader 在 system prompt 中注入可用 Skills
    2. 增加 load_skill 工具供模型按需加载 Skill 指令
    3. bash 工具执行 Skill 脚本（Level 3）
    """

    def __init__(
        self,
        model: str = "qwen2.5:7b",
        max_iterations: int = 10,
        backend: str = "ollama"
    ):
        self.model = model
        self.max_iterations = max_iterations
        self.backend = backend

        # Skills 支持
        self.skill_loader = SkillLoader()

        # 工具注册
        self.tools: Dict[str, Callable] = {
            "load_skill": lambda name: load_skill_tool(name, self.skill_loader),
            "bash": bash_tool,
        }

        # 后端客户端初始化
        if backend == "openai":
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),
            )
        else:
            self.client = ollama.Client(
                host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            )

    def _create_system_prompt(self) -> str:
        """创建包含 Skills 列表的 system prompt"""
        base_prompt = """You are a helpful assistant with access to skills.

When a user request matches a skill's description:
1. Call `load_skill(skill_name)` to get detailed instructions
2. Follow the instructions carefully
3. Use `bash` tool to run scripts when needed

Always think step by step."""

        return self.skill_loader.build_system_prompt(base_prompt)

    def run(self, task: str) -> str:
        """运行 Agent 执行任务"""
        history = ""

        for i in range(self.max_iterations):
            # 构建 ReAct 格式提示词
            prompt = self._create_react_prompt(task, history)

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
                    messages=[
                        {"role": "system", "content": self._create_system_prompt()},
                        {"role": "user", "content": task + "\n\n" + history}
                    ]
                )
                response_text = response.choices[0].message.content

            # 解析响应并执行工具...
            # (详见完整代码)
```

**运行测试**：

```bash
# 使用 Ollama 后端（默认）
python experiments/phase3/exp3_7b_skills_agent.py --task "帮我扫描 localhost 的 80 端口"

# 使用 OpenAI 后端
python experiments/phase3/exp3_7b_skills_agent.py --backend openai --task "你好"
```

---

### 步骤 3：Skills CLI 验证工具

**目标**：使用 CLI 工具验证三层加载机制，并与 Claude Code 的 Skill 验证结果相互印证。

**说明**：实验 3.7 中已通过 Claude Code 的 `/hello-world` 命令验证了 Skill 能正常工作。本步骤使用 CLI 工具反向验证 Skill 扫描和加载机制的实现是否正确。

**文件**: `experiments/phase3/exp3_7c_skills_cli.py`

**使用方式**：

```bash
# Level 1 验证：列出所有 Skills
python experiments/phase3/exp3_7c_skills_cli.py --list-skills

# Level 1 验证：显示 System Prompt
python experiments/phase3/exp3_7c_skills_cli.py --show-prompt

# Level 2 验证：显示指定 Skill 详情
python experiments/phase3/exp3_7c_skills_cli.py --show-skill hello-world

# Level 3 验证：执行单次任务
python experiments/phase3/exp3_7c_skills_cli.py "帮我扫描 localhost 的端口"

# 交互模式
python experiments/phase3/exp3_7c_skills_cli.py

# 使用 OpenAI API
python experiments/phase3/exp3_7c_skills_cli.py --backend openai "你好"
```

**验证结果对比**：

| 验证方式 | 验证层级 | 预期结果 | 与 Claude Code 验证的关联 |
|----------|----------|----------|---------------------------|
| `--list-skills` | Level 1 | 列出 hello-world 等 Skills | 应包含实验 3.7 中创建的 Skill |
| `--show-skill hello-world` | Level 2 | 显示完整 SKILL.md 内容 | 与 Claude Code 加载的指令一致 |
| 直接运行任务 | Level 3 | 执行脚本并返回结果 | 与 `/hello-world` 命令输出相同 |

**验证逻辑**：
- 如果 Claude Code 的 `/hello-world` 能正常工作，但 cli.py 的 `--list-skills` 没有列出该 Skill，说明 SkillLoader 的路径扫描逻辑有问题
- 两者验证结果应相互印证，确保 Skill 实现符合 Agent Skills 标准

---

## 🧪 实验 3.9：高级 Skill 编写（Security Audit）

### 目标

创建完整的、带多个检查项的安全审计 Skill。

### 对应代码文件与逐行阅读入口

- Skill 描述文件：[D:\Code\BeginningWithAI\.claude\skills\security-audit\SKILL.md](D:/Code/BeginningWithAI/.claude/skills/security-audit/SKILL.md)
- 执行脚本：[D:\Code\BeginningWithAI\.claude\skills\security-audit\scripts\audit.py](D:/Code/BeginningWithAI/.claude/skills/security-audit/scripts/audit.py)
- 评估配置：[D:\Code\BeginningWithAI\.claude\skills\security-audit\evals\evals.json](D:/Code/BeginningWithAI/.claude/skills/security-audit/evals/evals.json)
- 建议顺序：先读 `SKILL.md`，确认触发条件和用法；再读 `audit.py`，看“安全审计任务”如何落成脚本；最后读 `evals.json`，理解 Skill 的验收方式。

### 步骤 1：创建 Security Audit Skill 目录

```bash
mkdir -p .claude/skills/security-audit/scripts
```

### 步骤 2：编写 Security Audit SKILL.md

`.claude/skills/security-audit/SKILL.md`：

````markdown
---
name: security-audit
description: 对代码进行安全审计，检查 SQL 注入、XSS、命令注入、硬编码密钥等常见漏洞。当用户要求检查代码安全、审计项目、查找漏洞时激活。
---

# 安全审计 Skill

使用 Python 脚本自动扫描代码中的常见安全漏洞。这是一个完整的、带多个检查项的 Skill 示例。

## 工作流程

1. **确定目标** - 用户指定要扫描的文件或目录
2. **运行扫描** - 执行 `scripts/audit.py` 进行漏洞检测
3. **分析结果** - 查看扫描报告，识别高危漏洞
4. **提供建议** - 针对发现的问题给出修复建议

## 可用脚本

### audit.py - 安全扫描器

```bash
python scripts/audit.py --target <路径> [--format json|markdown]
```

参数：

- `--target`: 要扫描的目录或文件（必需）
- `--format`: 输出格式，可选 `json` 或 `markdown`（默认 `markdown`）

示例：

```bash
# 扫描整个项目
python scripts/audit.py --target ./src

# 扫描单个文件
python scripts/audit.py --target ./app.py

# JSON 格式输出
python scripts/audit.py --target ./src --format json
```

## 检查项

| 漏洞类型   | 严重程度     | 检测模式                           | 说明                     |
| ------ | -------- | ------------------------------ | ---------------------- |
| SQL 注入 | CRITICAL | 字符串拼接 SQL                      | 使用 `+` 或 `%` 拼接 SQL 语句 |
| 命令注入   | HIGH     | `os.system`, `subprocess` 调用   | 直接调用系统命令               |
| 硬编码密钥  | HIGH     | `password`, `secret`, `key` 赋值 | 代码中硬编码的敏感信息            |
| XSS    | MEDIUM   | `innerHTML`, `document.write`  | 前端未转义的输出               |
| 路径遍历   | MEDIUM   | 文件操作拼接路径                       | 使用 `../` 或拼接路径         |

## 输出示例

**Markdown 格式**（默认）：

```markdown
# 安全审计报告

目标: ./src
发现漏洞: 3 个

## 详细结果

### sql_injection (CRITICAL)
- **文件**: `./src/db.py:15`
- **描述**: 潜在的 SQL 注入（字符串拼接 SQL）
- **代码**: `query = "SELECT * FROM users WHERE id = " + user_id`

### hardcoded_secret (HIGH)
- **文件**: `./src/config.py:8`
- **描述**: 硬编码密钥/密码
- **代码**: `DB_PASSWORD = "admin123"`
```

## 修复建议

### SQL 注入

**问题代码**：

```python
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)
```

**修复方案**：

```python
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))  # 使用参数化查询
```

### 硬编码密钥

**问题代码**：

```python
API_KEY = "sk-1234567890abcdef"
```

**修复方案**：

```python
import os
API_KEY = os.environ.get("API_KEY")  # 从环境变量读取
```

### 命令注入

**问题代码**：

```python
os.system("ping " + hostname)
```

**修复方案**：

```python
import subprocess
subprocess.run(["ping", hostname], capture_output=True)
```

## 使用建议

1. 定期扫描代码库（建议每次提交前）

2. 优先修复 CRITICAL 和 HIGH 级别漏洞

3. 结合代码审查确认漏洞真实性

4. 建立安全编码规范，预防类似问题
   
````

### 步骤 3：创建安全审计脚本

`.claude/skills/security-audit/scripts/audit.py`：

```python
#!/usr/bin/env python3
"""
安全审计脚本 - Security Audit Skill 的脚本组件
"""
import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Any


class SecurityAuditor:
    """
    安全审计器

    通过正则表达式匹配常见的安全漏洞模式。
    注意：这是一个教学示例，实际生产环境应使用更专业的工具。
    """

    # 漏洞模式定义
    PATTERNS = {
        "sql_injection": {
            "pattern": r"(SELECT|INSERT|UPDATE|DELETE).*\+.*\$|\%s.*%",
            "description": "潜在的 SQL 注入（字符串拼接 SQL）",
            "severity": "CRITICAL"
        },
        "command_injection": {
            "pattern": r"(os\.system|subprocess\.call|eval|exec)\s*\(",
            "description": "命令/代码执行（可能存在注入风险）",
            "severity": "HIGH"
        },
        "hardcoded_secret": {
            "pattern": r"(password|passwd|secret|key|token)\s*=\s*['\"][^'\"]+['\"]",
            "description": "硬编码密钥/密码",
            "severity": "HIGH"
        },
        "xss_vulnerable": {
            "pattern": r"(innerHTML|document\.write|\.html\().*\+",
            "description": "潜在的 XSS（未转义的输出）",
            "severity": "MEDIUM"
        },
        "path_traversal": {
            "pattern": r"open\s*\(.*\+.*\)|\.\./",
            "description": "潜在的路径遍历",
            "severity": "MEDIUM"
        },
    }

    def __init__(self, target: Path):
        self.target = target
        self.findings: List[Dict[str, Any]] = []

    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """扫描单个文件"""
        findings = []

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")

            for vuln_name, vuln_info in self.PATTERNS.items():
                for line_num, line in enumerate(lines, 1):
                    if re.search(vuln_info["pattern"], line, re.IGNORECASE):
                        findings.append({
                            "file": str(file_path),
                            "line": line_num,
                            "type": vuln_name,
                            "description": vuln_info["description"],
                            "severity": vuln_info["severity"],
                            "code": line.strip()[:100]
                        })

        except Exception as e:
            findings.append({"file": str(file_path), "error": str(e)})

        return findings

    def scan(self) -> List[Dict[str, Any]]:
        """执行扫描"""
        if self.target.is_file():
            self.findings = self.scan_file(self.target)
        else:
            extensions = {".py", ".js", ".php", ".java", ".go", ".ts", ".rb"}
            for ext in extensions:
                for file_path in self.target.rglob(f"*{ext}"):
                    if ".venv" in str(file_path) or "node_modules" in str(file_path):
                        continue
                    self.findings.extend(self.scan_file(file_path))

        return self.findings

    def to_markdown(self) -> str:
        """生成 Markdown 报告"""
        lines = [
            "# 安全审计报告",
            "",
            f"目标: `{self.target}`",
            f"发现漏洞: {len(self.findings)} 个",
            "",
            "## 详细结果",
            "",
        ]

        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        sorted_findings = sorted(
            self.findings,
            key=lambda x: severity_order.get(x.get("severity", "LOW"), 4)
        )

        for finding in sorted_findings:
            if "error" in finding:
                lines.append(f"- **Error**: {finding['error']}")
                continue

            lines.append(f"### {finding['type']} ({finding['severity']})")
            lines.append(f"- **文件**: `{finding['file']}:{finding['line']}`")
            lines.append(f"- **描述**: {finding['description']}")
            lines.append(f"- **代码**: `{finding['code']}`")
            lines.append("")

        return "\n".join(lines)

    def to_json(self) -> str:
        """生成 JSON 报告"""
        return json.dumps({
            "target": str(self.target),
            "total_findings": len(self.findings),
            "findings": self.findings
        }, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="安全审计工具")
    parser.add_argument("--target", required=True, help="目标文件或目录")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f"Error: Target not found: {target}")
        return 1

    auditor = SecurityAuditor(target)
    auditor.scan()

    if args.format == "json":
        print(auditor.to_json())
    else:
        print(auditor.to_markdown())

    return 0


if __name__ == "__main__":
    exit(main())
```

### 步骤 4：测试 Security Audit Skill

```bash
# 使用 CLI 工具测试
python experiments/phase3/exp3_7c_skills_cli.py "帮我审计当前项目的安全"

# 或直接运行脚本测试
python .claude/skills/security-audit/scripts/audit.py --target ./experiments --format markdown
```

---

### 三层加载机制验证总结

| 验证级别    | 命令                    | 预期输出                       |
| ------- | --------------------- | -------------------------- |
| Level 1 | `--list-skills`       | 列出所有 Skills 元数据            |
| Level 1 | `--show-prompt`       | System Prompt 包含 Skills 列表 |
| Level 2 | `--show-skill <name>` | 显示 SKILL.md 完整内容           |
| Level 3 | 直接运行任务                | Agent 调用 bash 执行脚本         |

---

## 🧪 实验 3.10：LangGraph 工作流编排

### 目标

从线性图进化到真正的工作流编排：条件路由、Human-in-the-loop、检查点与状态持久化。

### 对应代码文件与逐行阅读入口

- 主文件：[D:\Code\BeginningWithAI\experiments\phase3\exp3_10_langgraph_workflow.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_10_langgraph_workflow.py)
- 建议逐行顺序： [SecurityState](D:/Code/BeginningWithAI/experiments/phase3/exp3_10_langgraph_workflow.py:66) → [get_llm()](D:/Code/BeginningWithAI/experiments/phase3/exp3_10_langgraph_workflow.py:81) → [recon_node()](D:/Code/BeginningWithAI/experiments/phase3/exp3_10_langgraph_workflow.py:139) → [route_analysis()](D:/Code/BeginningWithAI/experiments/phase3/exp3_10_langgraph_workflow.py:182) → [risk_check_router()](D:/Code/BeginningWithAI/experiments/phase3/exp3_10_langgraph_workflow.py:244) → [human_review_node()](D:/Code/BeginningWithAI/experiments/phase3/exp3_10_langgraph_workflow.py:251) → [build_workflow()](D:/Code/BeginningWithAI/experiments/phase3/exp3_10_langgraph_workflow.py:304)
- 这章逐行阅读的重点是：`state` 怎么定义、路由函数怎么决定下一跳、`interrupt`/检查点是怎么插入工作流的。


### 📖 核心概念：从线性图到工作流

前面的实验中，我们学习了：
- 3.1 Function Calling：模型调用单个工具
- 3.2 ReAct Agent：手写的推理-行动循环
- 3.4 MCP：工具服务化

但这些都是**线性执行**的：A → B → C。在实际场景中，我们需要：
- **条件分支**：根据扫描结果选择不同的分析路径
- **人工审批**：高危操作前暂停等待确认
- **状态恢复**：长任务中断后从断点继续

LangGraph 将工作流表达为**有向图**，支持这些高级特性：

```
线性图（前面学过）:
  recon → analyze → report → END

条件路由图（本实验）:
  recon → router → web_analysis ────┐
                 → port_analysis ───┤→ risk_check → human_review → report → END
                 → comprehensive ───┘               (高危暂停)
```

### LangGraph 核心 API

| API | 作用 | 何时用 |
|-----|------|--------|
| `StateGraph(State)` | 创建有状态图 | 所有场景 |
| `add_node(name, fn)` | 添加节点 | 所有场景 |
| `add_edge(a, b)` | 固定边 | 确定的顺序 |
| `add_conditional_edges(src, fn, map)` | 条件路由 | 动态分支 |
| `compile(checkpointer=...)` | 编译为可执行图 | 定义完成后 |
| `invoke(input, config=None)` | 启动或恢复图执行 | 运行时 |
| `interrupt(value)` | 暂停执行 | Human-in-the-loop |
| `InMemorySaver()` | 内存检查点 | 开发/测试 |
| `Command(resume=val)` | 恢复执行 | 从 interrupt 继续 |
| `get_state(config)` | 查看当前快照 | 调试 / 恢复前检查 |
| `get_state_history(config)` | 查看执行历史 | 调试 / 可观测性 |

### 代码示例

创建文件 `experiments/phase3/exp3_10_langgraph_workflow.py`：

```python
# ============================================================
# 状态定义 — LangGraph 的核心
# ============================================================
# 所有节点共享一个 TypedDict 状态
# 每个节点读取状态、返回部分更新，框架自动合并

class SecurityState(TypedDict):
    """安全评估工作流状态"""
    target: str               # 评估目标
    analysis_type: str         # 分析类型: web / port / comprehensive
    recon_result: str          # 信息收集结果
    analysis_result: str       # 分析结果
    risk_level: str            # 风险等级: LOW / MEDIUM / HIGH / CRITICAL
    human_approved: bool       # 人工审批结果
    report: str                # 最终报告


# ============================================================
# 条件路由函数
# ============================================================
# 返回值是节点名称字符串，LangGraph 据此选择下一步

def route_analysis(state: SecurityState) -> str:
    """根据 analysis_type 选择分析路径"""
    analysis_type = state["analysis_type"]
    if analysis_type == "web":
        return "web_analysis"
    elif analysis_type == "port":
        return "port_analysis"
    else:
        return "comprehensive_analysis"


# ============================================================
# Human-in-the-loop 节点
# ============================================================
# interrupt() 暂停图执行，返回值传递给调用方
# 调用方通过 Command(resume=...) 恢复

def human_review_node(state: SecurityState) -> dict:
    """高风险时暂停等待人工确认"""
    decision = interrupt({
        "question": "是否继续生成详细报告？",
        "risk_level": state["risk_level"],
    })
    approved = decision.get("approved", False) if isinstance(decision, dict) else bool(decision)
    return {"human_approved": approved}


# ============================================================
# 构建图
# ============================================================

def build_workflow() -> StateGraph:
    workflow = StateGraph(SecurityState)

    # 添加节点
    workflow.add_node("recon", recon_node)
    workflow.add_node("web_analysis", web_analysis_node)
    workflow.add_node("port_analysis", port_analysis_node)
    workflow.add_node("comprehensive_analysis", comprehensive_analysis_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("report", report_node)

    # 入口
    workflow.set_entry_point("recon")

    # 条件路由：recon 之后根据分析类型分支
    workflow.add_conditional_edges(
        "recon", route_analysis,
        {"web_analysis": "web_analysis", "port_analysis": "port_analysis",
         "comprehensive_analysis": "comprehensive_analysis"}
    )

    # 三个分析节点汇聚后，根据风险等级路由
    for node in ["web_analysis", "port_analysis", "comprehensive_analysis"]:
        workflow.add_conditional_edges(
            node, risk_check_router,
            {"human_review": "human_review", "report": "report"}
        )

    workflow.add_edge("human_review", "report")
    workflow.add_edge("report", END)
    return workflow
```

### 执行模型：State、节点与图结构

先把 LangGraph 的执行模型压缩成一句话：

> 图在运行时维护一份共享 `state`，节点读取它并返回局部更新；边和条件边只负责定义控制流，不直接在 Python 代码里手写函数调用链。

#### 1. `SecurityState` 不是“进度条”，而是共享上下文

`SecurityState` 用 `TypedDict` 定义了整张图里流动的数据结构。运行时真正被传递的是一个 `dict`，例如：

```python
{
    "target": "localhost",
    "analysis_type": "",
    "recon_result": "",
    "analysis_result": "",
    "risk_level": "LOW",
    "human_approved": False,
    "report": "",
}
```

各个节点只返回自己负责更新的字段，LangGraph 自动合并这些局部更新：

- `recon_node()` 更新 `recon_result`、`analysis_type`
- `*_analysis_node()` 更新 `analysis_result`、`risk_level`
- `human_review_node()` 更新 `human_approved`
- `report_node()` 更新 `report`

因此，`state` 更像是**工作流共享上下文**或**黑板**，而不是单独表示“当前执行到第几步”的进度标记。执行进度主要由当前节点、下一跳和是否处于中断状态决定。

#### 2. `build_workflow()` 定义的是“图”，不是“调用顺序代码”

`build_workflow()` 做两件事：

- 定义逻辑单元：`add_node(...)`
- 定义它们之间的关系：`add_edge(...)` 和 `add_conditional_edges(...)`

这和普通 Python 代码中直接写：

```python
if analysis_type == "web":
    web_analysis_node(state)
elif analysis_type == "port":
    port_analysis_node(state)
```

是两种不同思路。上面的写法是“立即执行分支”；而 LangGraph 的写法是先**声明有哪些分支以及如何选择分支**，真正调用哪个节点由框架在运行时调度。

### `add_conditional_edges` 的语义：声明路由，不直接执行节点

看这段代码：

```python
workflow.add_conditional_edges(
    "recon",
    route_analysis,
    {
        "web_analysis": "web_analysis",
        "port_analysis": "port_analysis",
        "comprehensive_analysis": "comprehensive_analysis",
    }
)
```

它的执行顺序是：

1. 先执行 `recon` 节点
2. `recon` 更新 `state`
3. LangGraph 调用 `route_analysis(state)`
4. `route_analysis` 返回一个字符串，例如 `"web_analysis"`
5. 框架根据映射表选择下一节点并执行

所以要区分两个概念：

- **执行分支**：你在 Python 里直接 `if/else` 调用某个函数
- **声明分支**：你只告诉 LangGraph“从这里出去后，按这个路由函数决定下一站”

### Human-in-the-loop 使用方式与执行时序

```python
# 使用检查点：interrupt() 需要 checkpointer
checkpointer = InMemorySaver()
app = workflow.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "assessment-001"}}

# 第一次调用 — 可能在 human_review 暂停
result = app.invoke(initial_state, config=config)

# 检查是否暂停
snapshot = app.get_state(config)
if snapshot.next:  # next 非空表示未执行完
    print(f"图在 {snapshot.next} 处暂停")
    # 恢复执行
    result = app.invoke(Command(resume={"approved": True}), config=config)
```

上面这段代码的关键时序如下：

1. `app.invoke(initial_state, config=config)` 从入口节点开始执行图
2. 图运行到 `human_review_node()` 时调用 `interrupt(...)`
3. 当前这次 `invoke(...)` 提前返回到外部调用方
4. LangGraph 通过 `checkpointer` 保存当前运行现场
5. 外部调用方用 `get_state(config)` 查看暂停状态
6. 外部调用方再执行 `app.invoke(Command(resume=...), config=config)` 恢复
7. 图从 `interrupt()` 之后继续执行，而不是从入口重新开始

#### 为什么需要 `checkpointer` 和 `thread_id`

`interrupt()` 不是简单地“停一下”，而是要支持未来继续执行。为此框架必须保存：

- 当前 `state`
- 当前停在哪个节点
- 恢复执行所需的上下文

`checkpointer` 负责保存这些内容，`thread_id` 用来标识“这是哪一次运行的存档槽位”。这里的 `thread_id` 是**工作流会话 ID**，不是操作系统线程。

#### `initial_state` 的作用

`initial_state` 是图的起始输入，不是“中断点”。  
真正的中断点是在运行过程中到达 `human_review_node()` 并执行 `interrupt(...)` 时才出现。

#### 这份工作流为什么通常只中断一次

不是 LangGraph 只能 `interrupt` 一次，而是这份图的结构只有一个中断节点：

- `human_review_node()` 调用了 `interrupt(...)`
- 图中没有循环再回到 `human_review_node()`
- `human_review -> report -> END` 是单向路径

如果图中有多个审批节点，或者存在循环重新进入审批节点，那么同一个工作流也可以多次中断和恢复。

### `demo_with_checkpoint()` 的简化执行链

```
外部调用 app.invoke(initial_state)
  → recon
  → route_analysis
  → analysis_node
  → risk_check_router
  → human_review
  → interrupt() 暂停并返回外部
  → 外部 app.get_state(...)
  → 外部 app.invoke(Command(resume=...))
  → report
  → END
```

### 运行方式

```bash
# 基础工作流
python experiments/phase3/exp3_10_langgraph_workflow.py localhost --demo basic

# Human-in-the-loop 演示
python experiments/phase3/exp3_10_langgraph_workflow.py localhost --demo hitl

# 状态检查演示
python experiments/phase3/exp3_10_langgraph_workflow.py localhost --demo inspect

# 使用 OpenAI 后端
python experiments/phase3/exp3_10_langgraph_workflow.py example.com --backend openai
```

### 验证标准

- [ ] 条件路由根据扫描结果自动选择分析路径
- [ ] High/Critical 风险触发 Human-in-the-loop
- [ ] 检查点能保存和恢复执行状态
- [ ] 理解 `add_conditional_edges` 与 `add_edge` 的区别

### 📋 方法论提炼：何时用哪种图结构

| 图结构 | 适用场景 | 示例 |
|--------|---------|------|
| **线性图** | 步骤固定、顺序确定 | ETL 管道 |
| **条件路由** | 根据中间结果选择路径 | 安全评估分支 |
| **循环图** | 需要迭代直到满足条件 | ReAct Agent |
| **带审批的图** | 高风险操作需人工确认 | 渗透测试 |

**决策原则**：从最简单的线性图开始，只在需要时才增加复杂度。

---

## 🧪 实验 3.11：多 Agent 编排模式

### 目标

理解 Supervisor 和 Swarm 两种主流多 Agent 架构，学会根据场景选型。

### 对应代码文件与逐行阅读入口

- LangGraph 版：[D:\Code\BeginningWithAI\experiments\phase3\exp3_11_multi_agent.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11_multi_agent.py)
- OpenAI SDK 版：[D:\Code\BeginningWithAI\experiments\phase3\exp3_11b_multi_agent_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11b_multi_agent_openai.py)
- OpenAI SDK Subagent Runtime 版：[D:\Code\BeginningWithAI\experiments\phase3\exp3_11c_subagent_runtime_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11c_subagent_runtime_openai.py)
- OpenAI SDK Coordinator / Worker 版：[D:\Code\BeginningWithAI\experiments\phase3\exp3_11d_coordinator_runtime_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11d_coordinator_runtime_openai.py)
- OpenAI SDK Agent Team 版：[D:\Code\BeginningWithAI\experiments\phase3\exp3_11e_agent_team_runtime_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11e_agent_team_runtime_openai.py)
- OpenAI SDK Hook 控制面版：[D:\Code\BeginningWithAI\experiments\phase3\exp3_11f_hook_control_plane_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11f_hook_control_plane_openai.py)
- OpenAI SDK Instruction / Permission 版：[D:\Code\BeginningWithAI\experiments\phase3\exp3_11g_instruction_permission_runtime_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11g_instruction_permission_runtime_openai.py)
- OpenAI SDK Context / Memory 版：[D:\Code\BeginningWithAI\experiments\phase3\exp3_11h_context_memory_runtime_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11h_context_memory_runtime_openai.py)
- LangGraph 版建议顺序： [SupervisorState](D:/Code/BeginningWithAI/experiments/phase3/exp3_11_multi_agent.py:183) → [build_supervisor_workflow()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11_multi_agent.py:192) → [SwarmState](D:/Code/BeginningWithAI/experiments/phase3/exp3_11_multi_agent.py:296) → [build_swarm_workflow()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11_multi_agent.py:305)
- OpenAI SDK 版建议顺序： [OpenAIToolAgent](D:/Code/BeginningWithAI/experiments/phase3/exp3_11b_multi_agent_openai.py:177) → [create_agents()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11b_multi_agent_openai.py:270) → [choose_next_agent()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11b_multi_agent_openai.py:296) → [run_supervisor()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11b_multi_agent_openai.py:307) → [run_swarm()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11b_multi_agent_openai.py:334)
- Subagent Runtime 版建议顺序： [AgentSpec](D:/Code/BeginningWithAI/experiments/phase3/exp3_11c_subagent_runtime_openai.py:250) → [SessionRecord](D:/Code/BeginningWithAI/experiments/phase3/exp3_11c_subagent_runtime_openai.py:273) → [SubagentRuntime](D:/Code/BeginningWithAI/experiments/phase3/exp3_11c_subagent_runtime_openai.py:299) → [_build_specs()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11c_subagent_runtime_openai.py:329) → [run()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11c_subagent_runtime_openai.py:416) → [_execute_tool()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11c_subagent_runtime_openai.py:535)
- Coordinator / Worker 版建议顺序： [WorkerSpec](D:/Code/BeginningWithAI/experiments/phase3/exp3_11d_coordinator_runtime_openai.py:274) → [TaskStore](D:/Code/BeginningWithAI/experiments/phase3/exp3_11d_coordinator_runtime_openai.py:309) → [CoordinatorRuntime](D:/Code/BeginningWithAI/experiments/phase3/exp3_11d_coordinator_runtime_openai.py:349) → [run_coordinator()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11d_coordinator_runtime_openai.py:399) → [run_scripted_demo()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11d_coordinator_runtime_openai.py:438) → [_coordinator_tool_schemas()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11d_coordinator_runtime_openai.py:619)
- Agent Team 版建议顺序： [TeamMember](D:/Code/BeginningWithAI/experiments/phase3/exp3_11e_agent_team_runtime_openai.py:59) → [TeamTask](D:/Code/BeginningWithAI/experiments/phase3/exp3_11e_agent_team_runtime_openai.py:70) → [MailboxMessage](D:/Code/BeginningWithAI/experiments/phase3/exp3_11e_agent_team_runtime_openai.py:83) → [TeamStore](D:/Code/BeginningWithAI/experiments/phase3/exp3_11e_agent_team_runtime_openai.py:101) → [AgentTeamRuntime](D:/Code/BeginningWithAI/experiments/phase3/exp3_11e_agent_team_runtime_openai.py:210) → [run_teammate()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11e_agent_team_runtime_openai.py:317)
- Hook 控制面版建议顺序： [HookRegistry](D:/Code/BeginningWithAI/experiments/phase3/exp3_11f_hook_control_plane_openai.py:60) → [HookedRuntime](D:/Code/BeginningWithAI/experiments/phase3/exp3_11f_hook_control_plane_openai.py:85) → [run_tool()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11f_hook_control_plane_openai.py:143) → [compact()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11f_hook_control_plane_openai.py:171) → [run_scripted_demo()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11f_hook_control_plane_openai.py:181)
- Instruction / Permission 版建议顺序： [DemoWorkspace](D:/Code/BeginningWithAI/experiments/phase3/exp3_11g_instruction_permission_runtime_openai.py:57) → [InstructionPermissionRuntime](D:/Code/BeginningWithAI/experiments/phase3/exp3_11g_instruction_permission_runtime_openai.py:131) → [assemble()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11g_instruction_permission_runtime_openai.py:143) → [read_file()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11g_instruction_permission_runtime_openai.py:175)
- Context / Memory 版建议顺序： [TranscriptStore](D:/Code/BeginningWithAI/experiments/phase3/exp3_11h_context_memory_runtime_openai.py:62) → [MemoryStore](D:/Code/BeginningWithAI/experiments/phase3/exp3_11h_context_memory_runtime_openai.py:79) → [ContextMemoryRuntime](D:/Code/BeginningWithAI/experiments/phase3/exp3_11h_context_memory_runtime_openai.py:126) → [compact()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11h_context_memory_runtime_openai.py:157) → [extract_memory()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11h_context_memory_runtime_openai.py:170)

### 📖 核心概念：为什么需要多 Agent

单 Agent 的天花板：
1. **上下文溢出** — 工具太多时描述占满 context window
2. **职责模糊** — 一个 Agent 又扫描又分析，容易混乱
3. **错误传播** — 一步出错影响全局

多 Agent 的解法：分而治之 + 独立上下文 + 故障隔离。

### 两种架构模式

```
Supervisor（中心调度）:
┌─────────────┐
│  Supervisor  │ ← 决定调用哪个 Agent
└──────┬──────┘
       ├──────────┬──────────┐
  ┌────▼───┐ ┌───▼────┐ ┌───▼────┐
  │Scanner │ │Analyzer│ │Reporter│
  └────────┘ └────────┘ └────────┘

Swarm（去中心化 handoff）:
┌────────┐ handoff ┌────────┐ handoff ┌────────┐
│Scanner │ ──────→ │Analyzer│ ──────→ │Reporter│
└────────┘         └────────┘         └────────┘
每个 Agent 自主决定"下一步交给谁"
```

### Supervisor vs Swarm 对比

| 特性 | Supervisor | Swarm |
|------|-----------|-------|
| **调度方式** | 中心化 | 去中心化 |
| **Token 消耗** | 较高（经过 Supervisor 翻译） | 较低（直接 handoff） |
| **灵活性** | 高（可动态调整顺序） | 中（handoff 路径相对固定） |
| **错误处理** | Supervisor 统一处理 | 各 Agent 自行处理 |
| **第三方 Agent** | ✅ 支持（不需要互相了解） | ❌ 需要互相了解 |
| **适用场景** | 结构化任务、需要审批 | 流水线任务、灵活协作 |

### 📖 Agent Team 实现原理

先明确一个边界：

- **Agent Team** 是协作架构层，解决"多个 Agent 如何分工、传递上下文、汇总结果"
- **Tool / MCP** 是能力层，解决"Agent 真正能调用什么函数或服务"
- **A2A** 是跨进程 / 跨网络通信层，解决"不同系统里的 Agent 怎么互相调用"

所以，Agent Team 不是一种新的模型能力，也不是某个神秘框架；它在工程上的本质是：

> **一组职责单一的 Agent 节点 + 一份可共享的任务状态 + 一套明确的调度 / handoff 规则。**

### Agent Team 和 Subagent 的区别

这两个词经常被混用，但它们不是一个层次：

- **Agent Team**：系统架构概念，强调"多个角色如何协作完成一个任务"
- **Subagent**：运行时执行概念，强调"某个父 Agent 临时拉起一个子执行单元去做子任务"

可以先用一句话记住：

> **Team 关注组织结构，Subagent 关注委派动作。**

### 直观类比

- **Agent Team** 像一个项目组：组里有扫描、分析、报告三个岗位，流程和职责长期稳定。
- **Subagent** 像项目经理临时派出去的一个人："你去查这个文件夹的风险点，查完回来汇报。"

### 核心差异对比

| 维度 | Agent Team | Subagent |
|------|------------|----------|
| **关注点** | 多角色协作架构 | 单次任务委派机制 |
| **生命周期** | 通常随整个 workflow 持续存在 | 通常是临时创建，任务完成后结束 |
| **控制关系** | 可以是平级协作，也可以有 Supervisor | 明确有父 Agent / 子 Agent 关系 |
| **状态管理** | 依赖共享 state、handoff、聚合 | 常由父 Agent 下发任务，子 Agent 返回结果 |
| **适用场景** | 长链路任务、职责明确分工 | 把一个局部问题外包出去并行或隔离处理 |
| **典型实现** | LangGraph Supervisor / Swarm | coding agent 里的 `spawn/delegate/subagent` |

### 为什么容易混淆

因为在现代 coding agent 工具里，**一个 Team 完全可以用多个 Subagent 来实现**：

- 从架构视角看：这是一个 `planner / worker / reviewer` Team
- 从运行时视角看：父 Agent 先后或并行拉起了几个 Subagent 去执行这些角色

所以关系更准确地说是：

> **Subagent 是一种实现 Team 的手段，但 Team 不等于 Subagent。**

### 在本项目语境里如何理解

结合本章现有实验，推荐这样区分：

- [exp3_11_multi_agent.py](/mnt/d/Code/BeginningWithAI/experiments/phase3/exp3_11_multi_agent.py) 讲的是 **Agent Team 架构**
  因为重点是 `Scanner / Analyzer / Reporter` 这些角色怎么通过 `state` 和路由规则协作。
- `subagent` 更接近 Claude Code / Codex 这类 modern coding agent 里的**委派执行单元**
  父 Agent 把一个子任务交给它，等它返回结果，再决定后续动作。

换句话说：

- 如果你在讨论"系统里有哪些角色、谁和谁协作、怎么 handoff"，你在讨论 **Team**
- 如果你在讨论"父 Agent 如何把一个子任务派出去单独执行"，你在讨论 **Subagent**

### 一个常见误区

不要把 `subagent = 多 Agent`。

更准确的说法应该是：

- 一个系统可能只有 **单 Agent + 若干临时 Subagent**
- 也可能是 **显式 Agent Team**，但底层并没有动态 spawn subagent
- 还可能是 **Agent Team + Subagent 混合**
  例如 Supervisor 负责调度，而某个 Analyzer Agent 内部再拉起两个 subagent 分别看网络面和应用面

### Team 在代码里到底由什么组成

一个最小可运行的 Agent Team，通常只有 5 个核心部件：

1. **共享状态（state）**
   保存任务执行进度，例如目标、扫描结果、分析结果、最终报告、下一跳 Agent。
2. **专家 Agent 节点**
   每个 Agent 只做一类事，例如 `Scanner` 只收集信息，`Analyzer` 只判断风险。
3. **路由机制**
   决定下一步该谁执行。Supervisor 模式靠中心调度，Swarm 模式靠 Agent 自己写入下一跳。
4. **handoff 契约**
   约定 Agent 之间传什么字段、字段名是什么、格式是不是 JSON。
5. **终止条件**
   明确什么情况下结束，例如报告生成完毕，或达到 `END` 状态。

对应到 [exp3_11_multi_agent.py](/mnt/d/Code/BeginningWithAI/experiments/phase3/exp3_11_multi_agent.py)，你会看到：

- `SupervisorState` / `SwarmState`：共享状态
- `scanner_node()` / `analyzer_node()` / `reporter_node()`：专家 Agent
- `next_agent` / `current_agent`：路由字段
- `route_next()` / `route_swarm()`：路由函数
- `END`：终止条件

### 运行链路：Agent Team 并不是"大家一起聊天"

很多初学者会把 Agent Team 想成"多个 LLM 在群聊里互相讨论"。工程实现通常不是这样，而是更接近一个**有状态的调度循环**：

```text
用户任务
  ↓
初始化 state
  ↓
调度器 / 当前 Agent 读取 state
  ↓
选出下一个 Agent
  ↓
该 Agent 执行自己的 prompt + tools
  ↓
把结果写回 state
  ↓
判断是否结束；未结束则继续下一跳
```

这里最关键的一点是：

> **Agent 之间共享的不是"自动同步的记忆"，而是你显式设计出来的 state。**

这也是多 Agent 最容易出 bug 的地方。不是模型不聪明，而是：

- 上一个 Agent 没把关键字段写回 state
- 下一个 Agent 读错字段名
- handoff 传的是自然语言，但下游期待的是结构化 JSON
- 没有终止条件，导致来回循环

### Supervisor 模式的实现本质

Supervisor 可以理解为一个"项目经理节点"。它自己不一定做业务，只负责看当前状态并决定下一步调用谁。

```text
Supervisor 读 state
  ├─ 没有 scan_result     → 调 Scanner
  ├─ 没有 analysis_result → 调 Analyzer
  ├─ 没有 report          → 调 Reporter
  └─ 都有了               → 结束
```

这正是 [exp3_11_multi_agent.py](/mnt/d/Code/BeginningWithAI/experiments/phase3/exp3_11_multi_agent.py) 里 `supervisor_node()` 的工作方式。它不是让 LLM 无限自由发挥，而是把调度权约束在一个可检查的节点里。

这种模式的优点是：

- 中心控制强，容易插入审批、重试、限流、日志
- 新增一个 Agent 时，对其他 Agent 影响小
- 比较适合安全场景，因为高风险步骤常常需要统一治理

代价是：

- 每次都要经过 Supervisor，链路更长
- Token 和延迟通常更高

### Swarm 模式的实现本质

Swarm 没有中心调度器，核心变成：

> **每个 Agent 在完成当前工作后，自己决定把任务 handoff 给谁。**

在 [exp3_11_multi_agent.py](/mnt/d/Code/BeginningWithAI/experiments/phase3/exp3_11_multi_agent.py) 里，这体现在节点返回值中直接写入：

- `{"current_agent": "analyzer"}`
- `{"current_agent": "reporter"}`
- `{"current_agent": "done"}`

然后由 `route_swarm()` 读取 `current_agent` 并跳到下一个节点。

这种模式更像流水线，优点是：

- 不需要每一步都回 Supervisor
- handoff 更直接，链路更短

但代价也很明显：

- 每个 Agent 都要知道团队里还有谁
- handoff 契约一旦变化，多个 Agent 都可能要一起改
- 更容易出现循环委派或上下文不一致

### 设计 Agent Team 时最该先想清楚的 4 件事

1. **按职责拆，不按文件名拆**
   `Scanner / Analyzer / Reporter` 是职责边界；不要把一个 Agent 定义成"会调用 12 个工具的人形脚本"。
2. **先定义 state，再写 prompt**
   多 Agent 的核心不是 prompt，而是状态字段和字段流向。
3. **handoff 尽量传结构化数据**
   能传 JSON 就不要只传自然语言摘要，否则下游解析会不稳定。
4. **结束条件必须显式**
   `done`、`END`、报告已生成，这类条件一定要在图里写出来。

### 与综合实验 3.14 的关系

[exp3_14_security_platform.py](/mnt/d/Code/BeginningWithAI/experiments/phase3/exp3_14_security_platform.py) 可以看作是在 Team 架构上继续加了三层工程能力：

- **风险门控**：高风险时进入 Human-in-the-loop
- **检查点**：任务中断后可恢复
- **流式可观测性**：可以看到每个 Agent 节点何时完成

因此，3.11 学的是"Team 怎么协作"，3.14 学的是"Team 怎么变成可上线的系统"。

### 代码示例

创建文件 `experiments/phase3/exp3_11_multi_agent.py`：

**Supervisor 模式核心逻辑**：

```python
# Supervisor 的核心：一个"调度节点"控制全部流程
def supervisor_node(state: SupervisorState) -> dict:
    """根据当前进度决定下一步"""
    if not state.get("scan_result"):
        return {"next_agent": "scanner"}
    elif not state.get("analysis_result"):
        return {"next_agent": "analyzer"}
    elif not state.get("report"):
        return {"next_agent": "reporter"}
    else:
        return {"next_agent": "done"}

# 构建图：各 Agent 完成后回到 Supervisor
workflow.set_entry_point("supervisor")
workflow.add_conditional_edges("supervisor", route_next,
    {"scanner": "scanner", "analyzer": "analyzer",
     "reporter": "reporter", "done": END})

# 关键区别：Agent → Supervisor → Agent（而非 Agent → Agent）
workflow.add_edge("scanner", "supervisor")
workflow.add_edge("analyzer", "supervisor")
workflow.add_edge("reporter", "supervisor")
```

**Swarm 模式核心逻辑**：

```python
# Swarm 的核心：每个 Agent 自己设置 "下一跳"
def scanner_node(state: SwarmState) -> dict:
    """Scanner 完成后直接 handoff 给 Analyzer"""
    result = scan_ports.invoke({"host": target})
    return {"scan_result": result, "current_agent": "analyzer"}  # ← handoff

def analyzer_node(state: SwarmState) -> dict:
    """Analyzer 完成后直接 handoff 给 Reporter"""
    result = analyze_risk.invoke({"scan_data": state["scan_result"]})
    return {"analysis_result": result, "current_agent": "reporter"}  # ← handoff

# 每个节点都用条件路由实现 handoff
for node in ["scanner", "analyzer", "reporter"]:
    workflow.add_conditional_edges(node, route_swarm, {...})
```

### 运行方式

```bash
# Supervisor 模式
python experiments/phase3/exp3_11_multi_agent.py localhost --mode supervisor

# Swarm 模式
python experiments/phase3/exp3_11_multi_agent.py localhost --mode swarm

# 对比两种模式
python experiments/phase3/exp3_11_multi_agent.py localhost --mode compare
```

### OpenAI SDK 对照版

如果你想先避开 LangGraph / LangChain，只看 OpenAI SDK 如何实现同样的多 Agent 思路，可以运行：

```bash
# Supervisor 模式
python experiments/phase3/exp3_11b_multi_agent_openai.py localhost --mode supervisor

# Swarm 模式
python experiments/phase3/exp3_11b_multi_agent_openai.py localhost --mode swarm

# 对比两种模式
python experiments/phase3/exp3_11b_multi_agent_openai.py localhost --mode compare
```

这个版本的关键点：

- `OpenAIToolAgent`：每个专家 Agent 都有自己的 system prompt 和工具集
- `client.chat.completions.create(..., tools=...)`：用 OpenAI Function Calling 驱动工具调用
- `tool_call_id`：工具结果必须按 OpenAI 格式回填给模型
- `choose_next_agent(state)`：用普通 Python 实现 Supervisor 调度
- `current_agent`：用普通 Python 实现 Swarm handoff

先澄清一个容易混淆的点：

- `OpenAIToolAgent` 是**项目里自定义的普通 Python 类名**
- 它**不是** OpenAI SDK 自带的类
- 它也**不是**重写或继承 `openai` 包内部的对象
- 它只是把“一个会使用 OpenAI Function Calling 的专家 Agent”封装成了一个教学用运行时

### 逐行解读：`OpenAIToolAgent`

以下逐行解读对应文件 `experiments/phase3/exp3_11b_multi_agent_openai.py` 中的核心类。

#### 1. 类定义与初始化

```python
class OpenAIToolAgent:
    """一个最小专家 Agent：有自己的 system prompt 和可用工具集。"""
```

- 这不是框架类，而是我们自己定义的类。
- 它的职责不是“做多 Agent 编排”，而是“让单个专家 Agent 能跑起来”。

```python
def __init__(
    self,
    name: str,
    system_prompt: str,
    tool_names: List[str],
    client: OpenAI,
    model: str,
    max_rounds: int = 4,
):
```

- `name`：这个 Agent 的名字，用于日志和调试。
- `system_prompt`：这个 Agent 的角色说明书，决定它的职责边界。
- `tool_names`：这个 Agent 允许使用哪些工具。
- `client`：OpenAI SDK 客户端，用来真正发起模型请求。
- `model`：底层模型名，例如 `deepseek-v4-pro`。
- `max_rounds`：最多允许工具循环几轮，防止死循环。

```python
self.name = name
self.system_prompt = system_prompt
self.tool_names = tool_names
self.client = client
self.model = model
self.max_rounds = max_rounds
```

- 这里没有额外逻辑，只是把初始化参数挂到对象上。
- 这样后面的 `run()` 就可以直接使用这些配置。

#### 2. `run()`：单个专家 Agent 的核心运行时

```python
def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
    print(f"  [{self.name}] 任务: {task}")
```

- `task` 是当前要执行的子任务。
- `context` 是上游 Agent 传来的上下文。
- 第一行 `print` 只是为了让你在运行时能看到“当前是谁在干什么”。

```python
messages: List[Dict[str, Any]] = [
    {"role": "system", "content": self.system_prompt},
    {"role": "user", "content": self._build_user_message(task, context or {})},
]
```

- `messages` 是 OpenAI `chat.completions` 的标准消息历史。
- 第一条是 `system`，决定当前 Agent 的身份。
- 第二条是 `user`，真正下发任务内容。
- 这里没有直接把 `task` 塞进去，而是先走 `_build_user_message(...)`，因为有时还要附带上游上下文。

```python
tool_schemas = [OPENAI_TOOLS[name]["schema"] for name in self.tool_names]
tool_results: Dict[str, str] = {}
```

- `tool_schemas` 把当前 Agent 允许使用的工具 JSON Schema 取出来。
- 这一步很重要：**不是所有 Agent 都能看到所有工具**。
- `tool_results` 用来保存本轮运行过程中真实执行过的工具结果。

#### 3. tool loop：模型决定是否调用工具

```python
for _ in range(self.max_rounds):
```

- 这里开始一个最小 Agent loop。
- 它的意思是：最多让模型思考和调工具 `max_rounds` 轮。

```python
response = self.client.chat.completions.create(
    model=self.model,
    messages=messages,
    tools=tool_schemas,
    tool_choice="auto",
)
message = response.choices[0].message
```

- `self.client.chat.completions.create(...)` 是真正的模型调用。
- `model=self.model`：指定底层模型。
- `messages=messages`：把当前完整历史发给模型。
- `tools=tool_schemas`：告诉模型它当前有哪些工具可以调用。
- `tool_choice="auto"`：让模型自己判断是直接回答，还是先调工具。
- `response.choices[0].message` 取出这一轮 assistant 的输出。

#### 4. 终止条件：如果没有 `tool_calls`，就返回最终答案

```python
if not getattr(message, "tool_calls", None):
    return AgentResult(self.name, message.content or "", tool_results)
```

- 这里在检查：模型这次有没有要求调用工具。
- 如果没有，说明它已经准备给最终回答。
- 返回值里同时保留：
  - `message.content`：模型最终自然语言输出
  - `tool_results`：这一轮实际调用过哪些工具

这一步说明一个核心事实：

- 模型负责“决定要不要调工具”
- 本地代码负责“真的去执行工具”

#### 5. 如果模型请求工具：先把 assistant message 回填到历史

```python
messages.append(self._assistant_message_for_history(message))
```

- 这一步不能省。
- 因为后面你要把 `tool` 结果回给模型时，模型必须先看到：
  “刚才是我自己请求了这个工具调用”。
- 所以 assistant 的 tool request 消息要先进历史。

#### 6. 遍历并执行每个工具调用

```python
for tool_call in message.tool_calls:
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments or "{}")
```

- `message.tool_calls` 里可能有一个或多个工具调用。
- `function_name` 拿到工具名称。
- `function_args` 把 JSON 字符串参数解析成 Python 字典。

```python
tool_output = self._execute_tool(function_name, function_args)
tool_results[function_name] = tool_output
print(f"  [{self.name}] 调用工具: {function_name}({function_args})")
```

- `_execute_tool(...)` 才是真正执行本地 Python 工具的地方。
- 注意：**模型本身没有权限执行工具**。
- 模型只是返回“我想调用哪个工具”，真正执行的是你的代码。
- 执行结果会保存到 `tool_results`，同时打印一条日志方便调试。

#### 7. 把工具结果回填给模型

```python
messages.append(
    {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": tool_output,
    }
)
```

- 这一步是 OpenAI Function Calling 的关键。
- `role="tool"`：告诉模型这是一条工具执行结果。
- `tool_call_id=tool_call.id`：把这条结果和上一轮 assistant 请求的那个工具调用对应起来。
- `content=tool_output`：工具的真实输出内容。

下一轮模型看到的历史会变成：

1. `system`：你是谁
2. `user`：你要做什么
3. `assistant`：我要调这个工具
4. `tool`：这是工具结果

然后模型再基于这段历史继续思考。

#### 8. 超过最大轮次时返回失败态

```python
return AgentResult(self.name, "Agent exceeded max_rounds before final answer.", tool_results)
```

- 如果循环跑满了 `max_rounds` 还没有最终答案，说明这个 Agent 没有收敛。
- 可能是一直在重复调用工具，也可能是一直不给最终回答。
- 这里返回一个失败态文本，而不是无限循环。

这属于工程防护，不是推理核心，但在真实系统里很重要。

### 逐行解读：三个辅助方法

#### `_build_user_message()`

```python
def _build_user_message(self, task: str, context: Dict[str, Any]) -> str:
    if not context:
        return task
    return f"{task}\n\n上下文:\n{json.dumps(context, ensure_ascii=False, indent=2)}"
```

- 如果没有上游上下文，就只返回当前任务。
- 如果有上下文，就把 `task + context` 组合成一个完整的用户消息。
- 这一步就是 handoff 的最小实现：不是把整个系统状态都塞给下一个 Agent，而是把需要的信息整理后传过去。

#### `_execute_tool()`

```python
def _execute_tool(self, function_name: str, function_args: Dict[str, Any]) -> str:
    if function_name not in self.tool_names:
        return json.dumps({"error": f"Tool not allowed for {self.name}: {function_name}"}, ensure_ascii=False)
```

- 这里先做权限检查。
- 即使模型说它想调某个工具，如果这个工具不在当前 Agent 的白名单里，也不能执行。

```python
tool_function: Callable[..., str] = OPENAI_TOOLS[function_name]["function"]
try:
    return tool_function(**function_args)
except Exception as exc:
    return json.dumps({"error": str(exc)}, ensure_ascii=False)
```

- 从 `OPENAI_TOOLS` 里取出真正的 Python 函数。
- 然后用 `**function_args` 执行。
- 如果执行失败，就把异常转成结构化 JSON 返回。

#### `_assistant_message_for_history()`

```python
assistant_message = {
    "role": "assistant",
    "content": message.content or "",
    "tool_calls": [
        {
            "id": tool_call.id,
            "type": "function",
            "function": {
                "name": tool_call.function.name,
                "arguments": tool_call.function.arguments,
            },
        }
        for tool_call in message.tool_calls
    ],
}
```

- 这里把 SDK 返回的 assistant message 转成下一轮请求能继续使用的历史消息。
- 重点是把 `tool_calls` 原样保留下来。
- 因为下一轮 tool result 必须和这条 assistant 请求严格对应。

```python
reasoning_content = getattr(message, "reasoning_content", None)
if reasoning_content:
    assistant_message["reasoning_content"] = reasoning_content
return assistant_message
```

- 这一步是针对 `deepseek-v4-pro` 的兼容处理。
- reasoning 模式下，它要求第二轮继续请求时把 `reasoning_content` 一起带回去。
- 否则 provider 会报 400。
- 所以这不是装饰代码，而是真实运行中必须保留的字段。

### 小结

`OpenAIToolAgent` 的本质不是“多 Agent 系统”，而是：

> **一个会使用 OpenAI Function Calling 的单专家 Agent 运行时模板。**

Multi-Agent 真正开始发生的地方，是后面的：

- `create_agents(...)`
- `choose_next_agent(state)`
- `run_supervisor(...)`
- `run_swarm(...)`

对照关系：

| 学习目标 | LangGraph 版 | OpenAI SDK 版 |
|----------|--------------|---------------|
| 多 Agent 状态 | `SupervisorState` / `SwarmState` | 普通 `dict` state |
| 节点定义 | `workflow.add_node(...)` | `OpenAIToolAgent.run(...)` |
| Supervisor 调度 | `add_conditional_edges(...)` | `choose_next_agent(state)` |
| Swarm handoff | `route_swarm(state)` | 修改 `state["current_agent"]` |
| 工具调用 | LangChain `@tool` | OpenAI `tools` + `tool_calls` |

### 验证标准

- [ ] Supervisor 模式：Supervisor 正确调度三个 Agent
- [ ] Swarm 模式：Agent 之间直接 handoff
- [ ] 理解两种模式的 token 消耗差异
- [ ] 能根据场景选择合适的模式

### 📋 方法论提炼：多 Agent 选型指南

```
你需要多 Agent 吗？
  ├─ 工具数量 < 5 且职责单一 → 单 Agent 足够
  ├─ 工具数量 > 5 或职责明确分离 → 多 Agent
  │    ├─ 需要动态调度/审批 → Supervisor
  │    ├─ 固定流水线 → Swarm
  │    └─ 混合场景 → Supervisor + Swarm 嵌套
  └─ 跨团队/跨框架 → A2A 协议（见 3.12）
```

**最常见的错误**：过早引入多 Agent。先用单 Agent 验证可行性，只在遇到天花板时才拆分。

**handoff 是多 Agent 最容易出错的地方** — 上下文丢失、格式不匹配、循环调用。测试时重点覆盖 Agent 之间的数据传递。

---

## 🧪 实验 3.12：A2A 协议与 Agent 互操作

### 目标

理解 A2A (Agent-to-Agent) 协议作为跨框架 Agent 通信标准的定位。

### 对应代码文件与逐行阅读入口

- LangChain / HTTP 版：[D:\Code\BeginningWithAI\experiments\phase3\exp3_12_a2a_protocol.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_12_a2a_protocol.py)
- OpenAI SDK 版：[D:\Code\BeginningWithAI\experiments\phase3\exp3_12b_a2a_protocol_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_12b_a2a_protocol_openai.py)
- 建议逐行顺序： [AgentCard](D:/Code/BeginningWithAI/experiments/phase3/exp3_12b_a2a_protocol_openai.py:353) → [A2ATask](D:/Code/BeginningWithAI/experiments/phase3/exp3_12b_a2a_protocol_openai.py:369) → [A2AOpenAIAgent](D:/Code/BeginningWithAI/experiments/phase3/exp3_12b_a2a_protocol_openai.py:396) → [ScannerAgent](D:/Code/BeginningWithAI/experiments/phase3/exp3_12b_a2a_protocol_openai.py:524) → [AnalyzerAgent](D:/Code/BeginningWithAI/experiments/phase3/exp3_12b_a2a_protocol_openai.py:560) → [A2AOrchestrator](D:/Code/BeginningWithAI/experiments/phase3/exp3_12b_a2a_protocol_openai.py:598)
- 这一章逐行阅读的核心是：先分清“内部怎么思考”和“对外怎么通信”是两层不同问题。

### 📖 核心概念：A2A 协议

Google 于 2025.4 提出，2025.8 捐赠给 Linux Foundation。截至 2026 年初，已有 150+ 组织支持（Google, Microsoft, IBM, Anthropic, SAP...），成为事实上的 Agent 互操作标准。

**核心问题**：你用 LangChain 开发了扫描 Agent，同事用 AutoGen 开发了分析 Agent，如何协作？

```
Agent A (你的团队)  ←→  A2A 协议 (JSON-RPC 2.0 over HTTP)  ←→  Agent B (其他团队)
                              │
                        Agent Card (能力发现)
```

### A2A vs MCP：互补关系

```
┌──────────────────────────────────────┐
│            Your Agent                │
│  使用 MCP 调用垂直工具               │
│  ├─ Database (MCP Server)           │
│  └─ File System (MCP Server)        │
└──────────────────────────────────────┘
                ↕ A2A 协议（水平协作）
┌──────────────────────────────────────┐
│         External Agent (第三方)       │
│  使用 MCP 调用它自己的工具            │
│  ├─ Inventory DB (MCP Server)       │
│  └─ Shipping API (MCP Server)       │
└──────────────────────────────────────┘
```

| 协议 | 方向 | 解决的问题 |
|------|------|-----------|
| MCP | 垂直 | Agent 如何调用外部工具 |
| A2A | 水平 | Agent 之间如何通信协作 |

### A2A 核心流程

1. Agent B 发布 Agent Card（声明能力） — `GET /card`
2. Agent A 发现并读取 Agent Card
3. Agent A 通过 JSON-RPC 发送任务 — `POST /execute`
4. Agent B 执行任务并返回结果
5. Agent A 整合结果继续工作

### 代码示例

创建文件 `experiments/phase3/exp3_12_a2a_protocol.py`：

```python
# ============================================================
# A2A Agent Card（Agent 的"名片"）
# ============================================================

class AgentCard(TypedDict):
    id: str               # 唯一标识
    name: str             # 人类可读名称
    description: str      # 能力描述
    capabilities: list    # 支持的任务类型
    endpoint: str         # 任务提交地址
    version: str          # 版本

# ============================================================
# A2A Agent 基类 — 实现标准 HTTP 接口
# ============================================================

class A2AAgent:
    def get_agent_card(self) -> AgentCard: ...
    def execute_task(self, task: str, context: dict) -> dict: ...
    def start_server(self):
        """启动 HTTP 服务器
        GET /card     → 返回 Agent Card
        POST /execute → 执行任务（JSON-RPC 2.0）
        """

# ============================================================
# Orchestrator — 发现和调用 Agent
# ============================================================

class A2AOrchestrator:
    def discover_agent(self, endpoint: str) -> AgentCard:
        """GET /card 获取 Agent Card"""
        resp = requests.get(f"{endpoint}/card")
        return resp.json()

    def send_task(self, agent_id: str, task: str, context: dict) -> dict:
        """POST /execute 发送 JSON-RPC 任务"""
        request = {
            "jsonrpc": "2.0",
            "method": "agent.execute",
            "params": {"task": task, "context": context},
            "id": "task-001"
        }
        resp = requests.post(endpoint, json=request)
        return resp.json()["result"]
```

### 运行方式

需要三个终端：

```bash
# 终端 1: 启动 Scanner Agent
python experiments/phase3/exp3_12_a2a_protocol.py scanner

# 终端 2: 启动 Analyzer Agent
python experiments/phase3/exp3_12_a2a_protocol.py analyzer

# 终端 3: 运行 Orchestrator
python experiments/phase3/exp3_12_a2a_protocol.py orchestrator localhost
```

### OpenAI SDK 对照版

如果你想从 OpenAI SDK 视角理解 A2A，而不是先看 LangChain 版，可以运行：

```bash
# 终端 1: 启动 Scanner Agent
python experiments/phase3/exp3_12b_a2a_protocol_openai.py scanner

# 终端 2: 启动 Analyzer Agent
python experiments/phase3/exp3_12b_a2a_protocol_openai.py analyzer

# 终端 3: 运行 Orchestrator
python experiments/phase3/exp3_12b_a2a_protocol_openai.py orchestrator localhost
```

这个版本的重点：

- `A2AOpenAIAgent`：把本地 OpenAI SDK Agent 包成一个 HTTP 服务
- `GET /card`：暴露 Agent Card
- `POST /execute`：接收 JSON-RPC 任务
- `A2AOrchestrator`：发现远程 Agent 并发送任务
- `OpenAIToolAgent`：每个远程 Agent 内部仍然是 OpenAI Function Calling tool loop

### 验证标准

- [ ] Agent Card 通过 HTTP 正常返回
- [ ] Orchestrator 能发现并调用远程 Agent
- [ ] 任务结果通过 JSON-RPC 正确传递
- [ ] 理解 A2A 与 MCP 的互补关系

### 📋 方法论提炼：何时需要 A2A

A2A 的价值在于**跨边界协作**：

| 场景 | 推荐方案 |
|------|---------|
| 同一代码库内的多 Agent | LangGraph（3.11） |
| 同一团队的微服务 Agent | 内部 API 即可 |
| 跨团队/跨组织的 Agent 协作 | **A2A 协议** |
| 集成第三方 Agent 服务 | **A2A 协议** |

不要为了用 A2A 而用 A2A。如果你的 Agent 都在同一个进程里，LangGraph 更高效。

---

## 🧪 实验 3.13：生产化实践

### 目标

理解从实验代码到生产系统的关键差距：评估、可观测性、错误恢复、安全边界。

### 对应代码文件与逐行阅读入口

- OpenAI SDK 版生产化脚本：[D:\Code\BeginningWithAI\experiments\phase3\exp3_13_openai_production_practice.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_13_openai_production_practice.py)
- 建议逐行顺序： [build_logger()](D:/Code/BeginningWithAI/experiments/phase3/exp3_13_openai_production_practice.py:51) → [append_trace()](D:/Code/BeginningWithAI/experiments/phase3/exp3_13_openai_production_practice.py:70) → [validate_target()](D:/Code/BeginningWithAI/experiments/phase3/exp3_13_openai_production_practice.py:96) → [save_checkpoint()](D:/Code/BeginningWithAI/experiments/phase3/exp3_13_openai_production_practice.py:121) → [evaluate_state()](D:/Code/BeginningWithAI/experiments/phase3/exp3_13_openai_production_practice.py:165) → [run_supervisor_with_retry()](D:/Code/BeginningWithAI/experiments/phase3/exp3_13_openai_production_practice.py:205)
- 这章逐行阅读的重点是：不再问“Agent 能不能跑”，而是问“跑坏了怎么办、怎么观测、怎么评估”。

### 📖 Agent 评估（Eval）

> "如果你不能衡量它，你就不能改进它。" — Lord Kelvin

Agent 的评估比传统软件复杂，因为输出是非确定性的。

```python
# 评估的核心思路：定义 "什么算对"
eval_cases = [
    {
        "input": "扫描 localhost 的常用端口",
        "expected_tools": ["scan_ports"],        # 期望调用的工具
        "expected_contains": ["80", "443"],       # 期望输出包含的关键词
        "max_iterations": 3,                      # 期望的最大迭代次数
    },
    {
        "input": "分析 192.168.1.1 的安全风险",
        "expected_tools": ["scan_ports", "analyze_risk"],
        "expected_contains": ["风险"],
    },
]

# 评估维度
eval_metrics = {
    "工具调用准确率": "Agent 是否调用了正确的工具？",
    "输出质量": "最终输出是否包含期望的信息？",
    "效率": "是否在合理的迭代次数内完成？",
    "鲁棒性": "面对错误输入是否优雅处理？",
}
```

### 📖 可观测性（Observability）

生产环境中，你需要知道 Agent 在做什么、为什么做、花了多长时间。

```python
import logging
import time

# 结构化日志 — Agent 执行的每一步都记录
logger = logging.getLogger("agent")

def traced_node(name: str, fn):
    """给节点添加追踪"""
    def wrapper(state):
        start = time.time()
        logger.info(f"[{name}] 开始执行", extra={
            "node": name,
            "state_keys": list(state.keys()),
        })
        try:
            result = fn(state)
            duration = time.time() - start
            logger.info(f"[{name}] 完成", extra={
                "node": name,
                "duration_ms": int(duration * 1000),
                "output_keys": list(result.keys()),
            })
            return result
        except Exception as e:
            logger.error(f"[{name}] 失败: {e}", extra={"node": name})
            raise
    return wrapper

# LangSmith 集成（如果可用）
# export LANGCHAIN_TRACING_V2=true
# export LANGCHAIN_API_KEY=your_key
# 自动追踪所有 LangChain/LangGraph 调用
```

### 📖 错误恢复

> 生产 Agent 的可靠性核心是"失败时怎么办"

```python
# 策略 1: 重试（适用于瞬时错误）
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
def call_llm_with_retry(llm, messages):
    return llm.invoke(messages)


# 策略 2: 回退（适用于工具不可用）
def scan_with_fallback(host: str) -> str:
    try:
        return nmap_scan(host)          # 首选：nmap
    except Exception:
        return socket_scan(host)         # 回退：socket


# 策略 3: 优雅降级（适用于部分功能失败）
def analyzer_node(state):
    try:
        # 正常路径：LLM 分析
        return llm_analyze(state)
    except Exception:
        # 降级路径：规则引擎分析
        return rule_based_analyze(state)


# 策略 4: 检查点恢复（适用于长任务中断）
# LangGraph 的 checkpointer 天然支持
# 中断后重新调用 app.invoke(state, config=config) 即可从断点继续
```

### 📖 安全边界

Agent 能执行工具 = Agent 能造成损害。必须设置边界。

```python
# 1. 输入验证 — 不信任用户输入
import re
def validate_target(target: str) -> bool:
    """只允许合法的 IP 或域名"""
    ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
    domain_pattern = r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(ip_pattern, target) or re.match(domain_pattern, target))

# 2. 工具权限 — 限制 Agent 能调用的工具
ALLOWED_TOOLS = {"scan_ports", "check_http", "analyze_risk"}
# 不允许: execute_shell, delete_file, send_email

# 3. 输出过滤 — 不泄露敏感信息
SENSITIVE_PATTERNS = [r"\b\d{3}-\d{2}-\d{4}\b", r"password\s*=\s*\S+"]

# 4. 速率限制 — 防止 Agent 失控
MAX_TOOL_CALLS_PER_RUN = 20
MAX_LLM_CALLS_PER_RUN = 10
```

### 📋 生产化检查清单

| 维度 | 检查项 | 优先级 |
|------|--------|--------|
| **评估** | 定义了评估用例和指标 | P0 |
| **评估** | 有自动化评估脚本 | P1 |
| **可观测** | 结构化日志记录每步执行 | P0 |
| **可观测** | 关键指标监控（延迟、错误率） | P0 |
| **错误恢复** | LLM 调用有重试机制 | P0 |
| **错误恢复** | 工具调用有回退方案 | P1 |
| **错误恢复** | 长任务支持检查点恢复 | P1 |
| **安全** | 输入验证 | P0 |
| **安全** | 工具白名单 | P0 |
| **安全** | 输出过滤敏感信息 | P1 |
| **安全** | 速率限制 | P1 |

### OpenAI SDK 对照版

为了让生产化实践也能和前面的 OpenAI SDK Multi-Agent 主线接上，本章增加了一个配套脚本：

```bash
# 运行一次带输入校验 / 重试 / 检查点 / 日志的工作流
python experiments/phase3/exp3_13_openai_production_practice.py run localhost

# 运行内置评估用例
python experiments/phase3/exp3_13_openai_production_practice.py eval
```

对应文件：

- `experiments/phase3/exp3_13_openai_production_practice.py`

这个版本刻意不重新发明 Agent Runtime，而是在 `exp3_11b_multi_agent_openai.py` 之上补齐：

- 输入校验
- 结构化 trace 日志
- 整次工作流重试
- 结果检查点
- 最小评估用例

---

## 🧪 实验 3.14：综合项目 — 安全评估平台

### 目标

整合全部所学，构建一个完整的安全评估平台。

### 对应代码文件与逐行阅读入口

- LangGraph 综合版：[D:\Code\BeginningWithAI\experiments\phase3\exp3_14_security_platform.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_14_security_platform.py)
- OpenAI SDK 综合版：[D:\Code\BeginningWithAI\experiments\phase3\exp3_14b_security_platform_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_14b_security_platform_openai.py)
- OpenAI SDK 版建议顺序： [scan_ports()](D:/Code/BeginningWithAI/experiments/phase3/exp3_14b_security_platform_openai.py:77) → [check_http_security()](D:/Code/BeginningWithAI/experiments/phase3/exp3_14b_security_platform_openai.py:104) → [check_common_vulns()](D:/Code/BeginningWithAI/experiments/phase3/exp3_14b_security_platform_openai.py:141) → [OpenAIToolAgent](D:/Code/BeginningWithAI/experiments/phase3/exp3_14b_security_platform_openai.py:337) → [SecurityPlatformState](D:/Code/BeginningWithAI/experiments/phase3/exp3_14b_security_platform_openai.py:462) → [create_platform_agents()](D:/Code/BeginningWithAI/experiments/phase3/exp3_14b_security_platform_openai.py:500) → [choose_next_agent()](D:/Code/BeginningWithAI/experiments/phase3/exp3_14b_security_platform_openai.py:548) → [human_review()](D:/Code/BeginningWithAI/experiments/phase3/exp3_14b_security_platform_openai.py:581) → [run_platform()](D:/Code/BeginningWithAI/experiments/phase3/exp3_14b_security_platform_openai.py:606)
- 这章逐行阅读的重点是：如何把“单 Agent 内核、Multi-Agent 调度、人工审批、检查点”拼成一个完整平台。

### 架构设计

```
┌──────────────────────────────────────────────────────────┐
│                Security Platform                         │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Supervisor Agent (协调器)                         │  │
│  │  - 任务分解 → Agent 调度 → 风险评估               │  │
│  └────────────────────────────────────────────────────┘  │
│           ↓                ↓                ↓             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │   Recon    │  │  Analyzer  │  │  Reporter  │        │
│  │   Agent    │  │   Agent    │  │   Agent    │        │
│  └────────────┘  └────────────┘  └────────────┘        │
│           ↓                                               │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Security Tools                                    │  │
│  │  - scan_ports · check_http_security                │  │
│  │  - check_common_vulns                              │  │
│  └────────────────────────────────────────────────────┘  │
│                       ↕                                   │
│              Human-in-the-loop                            │
│              (高危操作审批)                                │
└──────────────────────────────────────────────────────────┘
```

### 代码要点

创建文件 `experiments/phase3/exp3_14_security_platform.py`：

**综合运用**：

```python
# 1. 多 Agent 协作（3.11 Supervisor 模式）
def supervisor_node(state) -> dict:
    if not state.get("scan_result"):
        return {"next_agent": "recon"}
    elif not state.get("vuln_result"):
        return {"next_agent": "analyzer"}
    elif not state.get("report"):
        return {"next_agent": "reporter"}
    return {"next_agent": "END"}

# 2. LangGraph 条件路由（3.10）
workflow.add_conditional_edges("supervisor", route_supervisor,
    {"recon": "recon", "analyzer": "analyzer", "reporter": "reporter", END: END})

# 3. Human-in-the-loop（3.10）
def human_review_node(state) -> dict:
    if state["overall_risk"] in ["CRITICAL", "HIGH"]:
        approval = interrupt(f"⚠️ 检测到 {state['overall_risk']} 风险！继续？")
        return {"human_approved": approval.lower() in ["yes", "y"]}
    return {"human_approved": True}

# 4. 检查点支持（长任务恢复）
checkpointer = InMemorySaver()
platform = workflow.compile(checkpointer=checkpointer)

# 5. 流式执行（实时查看进度）
for event in platform.stream(initial_state, config):
    for node_name, output in event.items():
        print(f"[{node_name}] 执行完成")
```

### 运行方式

```bash
# 评估本地主机
python experiments/phase3/exp3_14_security_platform.py localhost

# 评估远程目标（使用 OpenAI 后端）
python experiments/phase3/exp3_14_security_platform.py example.com --backend openai
```

### OpenAI SDK 对照版

如果你想把整个综合项目都放到 OpenAI SDK 主线上理解，可以运行：

```bash
# 默认评估 localhost
python experiments/phase3/exp3_14b_security_platform_openai.py localhost

# 高危时自动继续，不等待人工输入
python experiments/phase3/exp3_14b_security_platform_openai.py localhost --auto-approve

# 从检查点恢复
python experiments/phase3/exp3_14b_security_platform_openai.py localhost --resume
```

对应文件：

- `experiments/phase3/exp3_14b_security_platform_openai.py`

这个版本的设计重点：

- 保留 `Supervisor + Recon/Analyzer/Reporter` 的角色拆分
- 保留 Human-in-the-loop
- 用普通 Python `state` 替代 LangGraph state
- 用 JSON 文件实现最小检查点恢复
- 每个专业 Agent 内部仍然使用 OpenAI Function Calling

### 验证标准

- [ ] Supervisor 正确调度三个 Agent
- [ ] Recon Agent 执行端口扫描和 HTTP 检查
- [ ] Analyzer Agent 基于扫描结果分析漏洞
- [ ] 高风险触发 Human-in-the-loop
- [ ] Reporter Agent 生成 Markdown 格式报告
- [ ] 支持 Ollama 和 OpenAI 双后端

---

## 📌 附录 A：Dify 可视化编排

Dify 是开源 LLM 应用编排平台，提供拖拽式工作流构建。

### 何时使用 Dify

| 场景 | 推荐 |
|------|------|
| 非开发者构建 AI 应用 | ✅ Dify |
| 快速验证工作流原型 | ✅ Dify |
| 需要细粒度控制 | ❌ 用代码（LangGraph） |
| 复杂条件逻辑和循环 | ❌ 用代码 |
| 多 Agent 协作 | ❌ 用代码 |
| 生产级别的可靠性 | ❌ 用代码 |

### 与代码编排的关系

Dify 的可视化编排本质上对应 LangGraph 的子集：
- Dify 的"LLM 节点" ≈ LangGraph 的 `add_node`
- Dify 的"条件分支" ≈ LangGraph 的 `add_conditional_edges`
- Dify 的"工具节点" ≈ LangChain 的 `@tool`

学会了代码编排（LangGraph），你会发现 Dify 的可视化界面非常直观 — 因为你理解了背后的原理。

---

## 🧩 补充实验：Internal/System Agent 与运行时可靠性

前面的实验已经出现了几个重要概念：`hidden` agent、完成判断、fallback、checkpoint、trace、eval。它们不是新的模型能力，而是现代 code agent runtime 的系统层能力。为了避免这些能力只散落在代码里，本节把它们整理成两个正式实验。

### 实验 3.11i：Internal / System Agent Runtime

**目标**

- 理解 Internal/System Agent 和普通用户可见 Agent 的区别。
- 理解 `hidden=True` 不是“神秘 Agent”，而是 runtime 不直接暴露给用户的系统组件。
- 用确定性脚本演示 permission classifier、completion judge、context compactor、memory curator。
- 明确边界：内部 Agent 可以给出短结论和结构化决策，但不应该暴露隐藏思维链。

**对应代码文件与逐行阅读入口**

- Internal/System Agent 版：[D:\Code\BeginningWithAI\experiments\phase3\exp3_11i_internal_system_agent_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11i_internal_system_agent_openai.py)
- 建议逐行顺序： [AgentSpec](D:/Code/BeginningWithAI/experiments/phase3/exp3_11i_internal_system_agent_openai.py:33) → [TaskContract](D:/Code/BeginningWithAI/experiments/phase3/exp3_11i_internal_system_agent_openai.py:43) → [InternalSystemAgentRuntime](D:/Code/BeginningWithAI/experiments/phase3/exp3_11i_internal_system_agent_openai.py:73) → [classify_action()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11i_internal_system_agent_openai.py:122) → [judge_completion()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11i_internal_system_agent_openai.py:152) → [compact_context()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11i_internal_system_agent_openai.py:183) → [curate_memory()](D:/Code/BeginningWithAI/experiments/phase3/exp3_11i_internal_system_agent_openai.py:197)

**运行方式**

```bash
./venv/bin/python experiments/phase3/exp3_11i_internal_system_agent_openai.py --help
./venv/bin/python experiments/phase3/exp3_11i_internal_system_agent_openai.py --scripted
```

**学习重点**

- Public agent 负责产出候选结果，internal agent 负责验收和治理。
- Completion judge 对照 `TaskContract` 判断交付是否合格，不依赖模型自我声明。
- Memory curator 只保存稳定事实，临时观察不能进入长期记忆。
- Context compactor 只解决上下文预算，不等于长期记忆。

### 实验 3.13b：Runtime Reliability

**目标**

- 把 retry、fallback、checkpoint、trace、eval 从生产化章节中拆成独立可运行实验。
- 理解可靠性不是“模型更聪明”，而是 runtime 对失败、恢复和验收有明确机制。
- 用确定性脚本模拟长任务：扫描失败重试、分析失败 fallback、每步 checkpoint、最终 eval。

**对应代码文件与逐行阅读入口**

- Runtime Reliability 版：[D:\Code\BeginningWithAI\experiments\phase3\exp3_13b_runtime_reliability_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_13b_runtime_reliability_openai.py)
- 建议逐行顺序： [RetryPolicy](D:/Code/BeginningWithAI/experiments/phase3/exp3_13b_runtime_reliability_openai.py:42) → [TraceStore](D:/Code/BeginningWithAI/experiments/phase3/exp3_13b_runtime_reliability_openai.py:63) → [CheckpointStore](D:/Code/BeginningWithAI/experiments/phase3/exp3_13b_runtime_reliability_openai.py:85) → [RuntimeReliabilityDemo](D:/Code/BeginningWithAI/experiments/phase3/exp3_13b_runtime_reliability_openai.py:102) → [run_step()](D:/Code/BeginningWithAI/experiments/phase3/exp3_13b_runtime_reliability_openai.py:164) → [evaluate()](D:/Code/BeginningWithAI/experiments/phase3/exp3_13b_runtime_reliability_openai.py:200)

**运行方式**

```bash
./venv/bin/python experiments/phase3/exp3_13b_runtime_reliability_openai.py --help
./venv/bin/python experiments/phase3/exp3_13b_runtime_reliability_openai.py --scripted
./venv/bin/python experiments/phase3/exp3_13b_runtime_reliability_openai.py --scripted --resume
```

**学习重点**

- Retry 处理瞬时错误，例如超时、限流、临时网络失败。
- Fallback 处理主路径不可用，例如工具不可用、模型返回异常、外部服务失败。
- Checkpoint 保存运行现场，支持长任务恢复和事后复盘。
- Trace 是可观测性的基础，Eval 是判断“是否真的完成”的基础。

**验收标准**

- 能解释 internal agent 为什么不是普通 subagent。
- 能说明 completion judge 和 `TaskCompleted` hook 的关系。
- 能指出 compact、memory extraction、checkpoint 三者分别保存什么。
- 能跑通两个实验的 `--scripted`，并在输出里看到 blocked completion、approved completion、retry、fallback、checkpoint、eval。

---

## 📋 工具调用模式总结

> 完成以上所有实验后，回顾从工具调用到工作流编排的完整技术栈。

### 六种模式全景对比

|             | Function Calling | MCP            | Shell Tool         | Skill       | LangGraph 工作流 | 多 Agent |
| ----------- | ---------------- | -------------- | ------------------ | ----------- | --------------- | -------- |
| **是什么**     | API 协议特性         | 工具服务协议         | 通用 CLI 执行          | IDE 插件指令集   | 有状态图编排        | Agent 协作架构 |
| **模型的认知来源** | JSON Schema（显式）  | Server 自动发现    | 训练数据 + Prompt      | SKILL.md 指令 | 代码定义节点/边     | 各 Agent 独立 Prompt |
| **核心能力**   | 单次工具调用          | 工具服务化          | 操作系统即工具          | 冷门工具补充     | 条件路由/循环/中断  | 分而治之/并行 |
| **调用确定性**   | ⭐⭐⭐ 强            | ⭐⭐⭐ 强          | ⭐⭐ 弱               | ⭐⭐ 中        | ⭐⭐⭐ 强（代码控制）| ⭐⭐ 中 |
| **适用场景**    | 生产环境             | 工具服务化          | 开发探索               | 冷门工具补充      | 复杂工作流        | 职责分离 |

### Shell Tool 模式：把操作系统变成工具箱

当前流行的一种工程方法是**不封装**，直接让 Agent 执行 CLI 命令：

```python
@tool
def run_shell(command: str) -> str:
    """在 shell 中执行命令并返回输出"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout[:4000]

# Agent 收到 "扫描 example.com" → 自主决定执行 nmap -sV example.com
```

**模型如何知道 CLI 工具的用法？** 靠两件事：

1. **预训练知识**：大模型训练时读过 man pages、Stack Overflow、GitHub 脚本，天生知道 `nmap`、`curl`、`dig` 怎么用
2. **System Prompt 引导**：通过提示词告知可用工具列表和使用示例

### Skill + Shell 组合：解决冷门工具问题

对于模型训练数据中覆盖不足的 CLI 工具（如 `nuclei`、`subfinder`、`httpx` 等），可以通过 **Skill 的方式将使用说明注入给模型**：

```markdown
# SKILL.md — 给 Agent 的 nuclei 使用指南
可用命令：
- nuclei -u <url> -t cves/     # 扫描已知 CVE
- nuclei -l urls.txt -t xss/   # 批量 XSS 检测
- nuclei -u <url> -severity critical  # 只报高危
```

Agent 在执行前读取 SKILL.md，就像工程师翻阅工具手册一样，弥补了预训练知识的空白。

### 实践建议

- **核心工具**：用 Function Calling / MCP 封装（确定性强，参数可控）
- **长尾 CLI 工具**：用 Shell Tool + Skill 补充（灵活但需人工确认）
- **安全红线**：Shell Tool 必须配合命令白名单、沙箱执行或人工审批
- **复杂流程**：用 LangGraph 工作流编排（条件路由、人工审批、检查点）
- **职责分离**：用多 Agent 架构（Supervisor/Swarm）

### 技术栈选型速查

| 场景 | 推荐组合 | 理由 |
|------|---------|------|
| **学习/调试** | Ollama + 原生 Python | 免费、可离线、理解底层原理 |
| **快速原型** | API Key + LangChain | 模型效果好、开发速度快 |
| **复杂工作流** | API Key + LangGraph | 状态管理清晰、流程可控 |
| **工具集成** | 任意模型 + MCP Server | 工具与模型解耦、可复用 |
| **多 Agent 系统** | LangGraph + Supervisor/Swarm | 职责隔离、独立上下文 |
| **跨组织协作** | A2A 协议 | 标准化互操作 |
| **生产部署** | API Key + LangGraph + MCP | 完整技术栈、可维护性好 |

---

## ✅ 阶段检查清单

| 阶段 | 检查项 | 状态 |
|------|--------|------|
| 阶段 1 | 能画出主流 coding agent 的运行链路，并跑通最小工具调用闭环 | ⬜ |
| 阶段 1 | 能解释 Function Calling、MCP、Skill 在现代 Agent Runtime 中的角色 | ⬜ |
| 阶段 2 | 做出一个最小单 Agent，并明确输入、能力边界、输出格式、完成条件 | ⬜ |
| 阶段 2 | 单 Agent 具备基本结果验收能力（格式检查 / 测试 / 复核） | ⬜ |
| 阶段 3 | 能实现一个 planner / worker / reviewer 或 supervisor / specialists Workflow | ⬜ |
| 阶段 3 | 能清楚说明什么时候该用单 Agent，什么时候该拆成多 Agent | ⬜ |
| 阶段 4 | 能用 LangGraph 实现显式状态、条件路由与 interrupt / resume | ⬜ |
| 阶段 4 | 能说明为什么某个任务需要显式 Workflow，而不是继续只靠软编排 | ⬜ |
| 阶段 4 | 能解释 Internal/System Agent 如何承担权限分类、完成判断、压缩和记忆抽取 | ⬜ |
| 阶段 4 | 能跑通 retry、fallback、checkpoint、trace、eval 的可靠性实验 | ⬜ |
| 阶段 5 | 能说明 MCP、A2A、Dify / 业务流程骨架分别处于系统哪一层 | ⬜ |
| 阶段 5 | 完成一个“外层流程 + 中层 Agent + 内层能力”的安全平台原型 | ⬜ |

---

## 🎉 学习完成

恭喜完成全部三个阶段的学习！

### 下一步建议

1. **深入实践**：在真实项目中应用所学
2. **持续学习**：关注 coding agent runtime、多 Agent 协作与协议层的最新演进
3. **开源贡献**：参与开源 Agent 项目
4. **知识分享**：撰写博客或教程

### 推荐进阶方向

- **多模态 Agent**：结合视觉能力的 Agent（如 Claude 的 computer use）
- **Agent 评估框架**：LangSmith Eval / Braintrust 等专业工具
- **RAG + Agent**：检索增强生成与 Agent 结合
- **Agent 安全**：对抗性提示注入、工具滥用防护
- **自主 Agent**：更高自主性的 AI 系统（如 Devin、OpenHands）
