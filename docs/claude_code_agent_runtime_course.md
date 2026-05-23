# Claude Code 风格 Code Agent Runtime 课程设计

> 面向网络安全工程师的现代 code agent runtime 实战课程。课程目标不是复刻某个商业产品，而是把 Claude Code 官方文档和 `pengchengneo/Claude-Code` 源码还原材料中暴露出的核心工程能力拆成可运行实验。

---

## 1. 课程定位

本课程是阶段三的专项深化模块，放在 Function Calling、ReAct、MCP、Skill、LangGraph 之后学习。

核心问题：

> Claude Code / Codex / OpenCode 这类 code agent，除了“模型调用工具”之外，还需要哪些 runtime 能力才能稳定完成真实代码任务？

课程不重点讲模型原理，也不继续增加扫描、分析、报告类角色示例，而是围绕 code agent runtime 的核心能力展开：

- Agent loop
- Reasoning trace / effort control
- Tool permission
- Subagent delegation
- Coordinator / Worker
- Agent Team
- Hook control plane
- Instruction loading
- Context compaction
- Persistent memory
- Long-running session

---

## 2. 资料基准

课程采用双资料源：

- 官方功能边界：Claude Code 官方文档，包括 Agent loop、Model configuration、Subagents、Agent Teams、Hooks、Memory、Settings / Permissions。
- 工程实现线索：[pengchengneo/Claude-Code](https://github.com/pengchengneo/Claude-Code)，重点参考 query、thinking、effort、messages、AgentTool、Coordinator、agent teams、hooks、context、memory、permission、session 等目录和说明。

使用原则：

- 官方文档定义“能力应该是什么”。
- 源码还原材料帮助理解“工程上可能怎样组织”。
- 本项目实验只实现可教学、可验证的最小子集。
- 不把 prompt 约束当成权限系统，不把上下文摘要当成长期记忆。

---

## 3. 课程结构

### 模块 0：Reasoning Trace 与 ReAct Scratchpad

对应章节：

- [D:\Code\BeginningWithAI\docs\phase3_agent.md](D:/Code/BeginningWithAI/docs/phase3_agent.md)
- [D:\Code\BeginningWithAI\experiments\phase3\exp3_2_react_agent.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_2_react_agent.py)
- [D:\Code\BeginningWithAI\experiments\phase3\exp3_11b_multi_agent_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11b_multi_agent_openai.py)

学习目标：

- 区分隐藏思维链、provider `reasoning_content`、ReAct Scratchpad、用户可见 reasoning summary。
- 理解 Claude Code 的 `effort / extended thinking / ultrathink` 是 runtime 配置，不是简单提示词模板。
- 理解为什么真实 code agent 应输出计划、行动、证据、风险和结论，而不是完整 thinking trace。

验收问题：

- ReAct `Thought` 和模型 hidden reasoning 是不是同一个东西？
- 为什么 `reasoning_content` 需要协议级回填，但不应该当作用户输出？
- subagent 为什么需要单独控制 thinking budget？

### 模块 1：固定 Team 与单 Agent Tool Loop

对应实验：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_11b_multi_agent_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11b_multi_agent_openai.py)

学习目标：

- 看懂 OpenAI Function Calling 的 message/tool 回填闭环。
- 看懂固定角色 Team：`scanner -> analyzer -> reporter`。
- 区分单 Agent runtime 和多 Agent 编排层。

验收问题：

- `OpenAIToolAgent` 为什么不是 OpenAI SDK 内置类？
- `tool_call_id` 为什么必须回填？
- `choose_next_agent(state)` 为什么可以不是 LLM？

### 模块 2：Subagent Delegation Runtime

对应实验：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_11c_subagent_runtime_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11c_subagent_runtime_openai.py)

学习目标：

- 理解 primary agent 和 subagent 的上下文隔离。
- 理解 `Task` 委派原语。
- 理解 subagent 工具权限和父子 session。

验收问题：

- subagent 和 Agent Team 的边界是什么？
- 子 session 的 tool results 为什么不应该全部灌回父上下文？
- `@explore` 和自动 delegation 的区别是什么？

### 模块 3：Coordinator / Worker Runtime

对应实验：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_11d_coordinator_runtime_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11d_coordinator_runtime_openai.py)

学习目标：

- 理解 Coordinator 只做派活、通信、停工。
- 理解 Worker 才执行代码库读写或验证工具。
- 理解 shared task list 和 task-notification 的作用。

验收问题：

- 为什么 Coordinator 不应该直接拥有 `read / grep / shell`？
- Worker prompt 为什么必须自包含？
- `send_message` 和 spawn 新 Worker 的适用场景有什么区别？

### 模块 4：Agent Team Runtime

对应实验：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_11e_agent_team_runtime_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11e_agent_team_runtime_openai.py)

学习目标：

- 理解 team lead、teammates、shared task list、mailbox。
- 理解 teammate 之间直接通信带来的能力和风险。
- 理解 Agent Team 与 Subagent 的工程区别。

验收问题：

- shared task list 和 `state` 有什么不同？
- mailbox 为什么会引入新失败模式？
- Agent Team 为什么比普通 subagent 更贵？

### 模块 5：Hook Control Plane

对应实验：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_11f_hook_control_plane_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11f_hook_control_plane_openai.py)

学习目标：

- 理解 Hook 是 runtime 控制面。
- 实现 `PreToolUse / PostToolUse / TaskCompleted / PreCompact / PostCompact`。
- 用 Hook 做权限阻断、审计日志、任务完成门禁。

验收问题：

- 为什么权限控制不能只写进 prompt？
- `PreToolUse` 和 `PostToolUse` 的根本差异是什么？
- 为什么 `TaskCompleted` hook 比“让模型自觉跑测试”更可靠？

### 模块 6：Instruction / Permission Runtime

对应实验：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_11g_instruction_permission_runtime_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11g_instruction_permission_runtime_openai.py)

学习目标：

- 理解 `CLAUDE.md`、`CLAUDE.local.md`、imports、rules、settings 的加载关系。
- 区分指令注入和权限强制。
- 实现 `permissions.deny` 对敏感路径的硬阻断。

验收问题：

- 为什么 `CLAUDE.md` 不能替代权限系统？
- 为什么 rules 要按路径匹配？
- 为什么 settings 用 JSON，而 instructions 用 Markdown？

### 模块 7：Context / Memory Runtime

对应实验：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_11h_context_memory_runtime_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11h_context_memory_runtime_openai.py)

学习目标：

- 区分 transcript、current context、compacted summary、persistent memory。
- 实现 token budget 和上下文压缩。
- 实现 `MEMORY.md` 索引和 topic memory 文件。
- 只抽取稳定事实，不把临时对话写入长期记忆。

验收问题：

- compact 和 memory extraction 的区别是什么？
- 为什么 memory 需要索引文件？
- 长期记忆为什么必须支持修正和删除？

### 模块 8：Internal / System Agent Runtime

对应实验：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_11i_internal_system_agent_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_11i_internal_system_agent_openai.py)

学习目标：

- 区分用户可见 Agent、subagent、internal/system agent。
- 理解 `hidden=True` 的工程含义：内部系统组件参与判断，但不直接作为用户对话角色。
- 实现 permission classifier、completion judge、context compactor、memory curator。
- 用 `TaskContract` 约束完成判断，而不是让模型自行宣称任务完成。

验收问题：

- Internal/System Agent 和普通 subagent 的边界是什么？
- 为什么 completion judge 应该读取结构化证据和测试结果？
- 为什么 internal agent 可以输出短决策，但不应该暴露隐藏思维链？

### 模块 9：Runtime Reliability

对应实验：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_13b_runtime_reliability_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_13b_runtime_reliability_openai.py)

学习目标：

- 理解 retry、fallback、checkpoint、trace、eval 是 code agent 的运行时可靠性能力。
- 区分瞬时错误、永久错误和可降级错误。
- 在每个关键阶段保存 checkpoint，并用 trace 支持复盘。
- 用 eval 判断运行结果是否满足最小交付条件。

验收问题：

- retry 和 fallback 的边界是什么？
- checkpoint 保存的是当前运行现场还是长期记忆？
- trace 和 eval 为什么分别解决“发生了什么”和“算不算合格”两个问题？

### 模块 10：生产化整合

对应实验：

- [D:\Code\BeginningWithAI\experiments\phase3\exp3_13_openai_production_practice.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_13_openai_production_practice.py)
- [D:\Code\BeginningWithAI\experiments\phase3\exp3_14b_security_platform_openai.py](D:/Code/BeginningWithAI/experiments/phase3/exp3_14b_security_platform_openai.py)

学习目标：

- 把 hook、permission、context、memory、checkpoint、eval 接入综合平台。
- 区分 demo agent 和可长期运行的 code agent runtime。

验收问题：

- 哪些能力属于 agent loop？
- 哪些能力属于控制面？
- 哪些能力属于持久化和可恢复性？

---

## 4. 推荐学习顺序

```text
3.3x Reasoning Trace / ReAct Scratchpad
  -> 3.11b 固定 Team / OpenAI Tool Loop
  -> 3.11c Subagent Delegation
  -> 3.11d Coordinator / Worker
  -> 3.11e Agent Team
  -> 3.11f Hook Control Plane
  -> 3.11g Instruction / Permission
  -> 3.11h Context / Memory
  -> 3.11i Internal / System Agent
  -> 3.13b Runtime Reliability
  -> 3.13 / 3.14 生产化整合
```

---

## 5. 实验运行清单

```bash
./venv/bin/python experiments/phase3/exp3_11b_multi_agent_openai.py localhost --mode supervisor
./venv/bin/python experiments/phase3/exp3_11c_subagent_runtime_openai.py --task "@explore 查找 phase3 里所有出现 tool_call_id 的地方"
./venv/bin/python experiments/phase3/exp3_11d_coordinator_runtime_openai.py --scripted --max-rounds 5
./venv/bin/python experiments/phase3/exp3_11e_agent_team_runtime_openai.py --scripted --max-rounds 3
./venv/bin/python experiments/phase3/exp3_11f_hook_control_plane_openai.py --scripted
./venv/bin/python experiments/phase3/exp3_11g_instruction_permission_runtime_openai.py --scripted
./venv/bin/python experiments/phase3/exp3_11h_context_memory_runtime_openai.py --scripted
./venv/bin/python experiments/phase3/exp3_11i_internal_system_agent_openai.py --scripted
./venv/bin/python experiments/phase3/exp3_13b_runtime_reliability_openai.py --scripted
```

说明：

- WSL 下优先使用 `./venv/bin/python`，不要使用裸 `python`。
- `3.11b / 3.11c / 3.11d / 3.11e` 会调用真实模型，可能消耗额度。
- `3.11f / 3.11g / 3.11h / 3.11i / 3.13b` 默认是确定性 runtime demo，不消耗模型额度。
- `3.11d / 3.11e / 3.11f / 3.11g / 3.11h / 3.11i / 3.13b` 会在临时目录写入 state、task、mailbox、audit、memory、trace 或 checkpoint 文件。

---

## 6. 交付物矩阵

| 模块 | 代码 | 文档状态 | 验证方式 |
|------|------|----------|----------|
| Fixed Team | `exp3_11b_multi_agent_openai.py` | 已补逐段解析 | API 实跑 |
| Subagent | `exp3_11c_subagent_runtime_openai.py` | 已有入口，待补逐行解析 | API 实跑 |
| Coordinator / Worker | `exp3_11d_coordinator_runtime_openai.py` | 已有入口，待补逐行解析 | API 实跑 |
| Agent Team | `exp3_11e_agent_team_runtime_openai.py` | 已有入口，待补逐行解析 | API 实跑 |
| Hooks | `exp3_11f_hook_control_plane_openai.py` | 已接入 phase3 正文 | `py_compile` + `--help` + `--scripted` |
| Instruction / Permission | `exp3_11g_instruction_permission_runtime_openai.py` | 已接入 phase3 正文 | `py_compile` + `--help` + `--scripted` |
| Context / Memory | `exp3_11h_context_memory_runtime_openai.py` | 已接入 phase3 正文 | `py_compile` + `--help` + `--scripted` |
| Internal / System Agent | `exp3_11i_internal_system_agent_openai.py` | 已接入 phase3 正文 | `py_compile` + `--help` + `--scripted` |
| Runtime Reliability | `exp3_13b_runtime_reliability_openai.py` | 已接入 phase3 正文 | `py_compile` + `--help` + `--scripted` + `--resume` |
| Production Integration | `exp3_13 / exp3_14b` | 待升级整合 | py_compile + targeted run |

---

## 7. 最终能力验收

完成本课程后，应该能独立回答并实现：

- 一个 code agent 的单次 tool call 为什么必须回填消息历史。
- subagent、Coordinator / Worker、Agent Team 分别解决什么问题。
- Hook 为什么属于控制面。
- `CLAUDE.md` 和 `permissions.deny` 为什么不是一类东西。
- compact、transcript、memory 的边界在哪里。
- Internal/System Agent 为什么适合承担权限分类、完成判断、压缩和记忆抽取。
- retry、fallback、checkpoint、trace、eval 分别解决哪类可靠性问题。
- 真实 code agent 为什么必须有 state、audit、permission、memory 和恢复机制。
