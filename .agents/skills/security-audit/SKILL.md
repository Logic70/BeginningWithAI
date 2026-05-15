---
name: security-audit
description: 对 C 语言代码进行安全审计，结合自动化代码检查（模式匹配）和 AI 深度分析（上下文理解）两种手段，识别内存安全、并发安全、输入验证等漏洞。**务必在以下场景使用此 Skill**：用户要求检查 C/C++ 代码安全、审计项目安全性、查找漏洞、分析缓冲区溢出、检查内存管理问题，或任何涉及 C 代码安全性的任务。即使只提到"安全检查"、"漏洞"、"不安全"等关键词，只要涉及 C 代码就应该使用此 Skill。
---

# C 语言安全审计 Skill

针对 C 语言代码的双重安全审计方案：
- **Level 1 代码检查**：使用正则模式匹配明确的安全问题（如危险函数调用）
- **Level 2 AI 检查**：分析需要上下文理解的复杂漏洞（如内存管理、状态机）

## 工作流程

1. **明确目标** - 用户指定要审计的 C 文件或目录
2. **Level 1 扫描** - 运行 `scripts/audit.py --mode code` 进行快速模式匹配
3. **Level 2 分析** - 对复杂问题使用 AI 进行深度上下文分析
4. **综合报告** - 合并两类检查结果，给出修复建议

## 审计分类

### Level 1: 代码检查（文本可明确识别）

适合正则表达式直接检测的问题：

| 漏洞类型 | 严重程度 | 检测模式 | 示例 |
|---------|---------|---------|------|
| 危险字符串函数 | HIGH | `strcpy`, `strcat`, `sprintf` | 无长度检查的字符串操作 |
| 未检查输入函数 | CRITICAL | `gets`, `scanf("%s")` | 无边界输入读取 |
| 内存操作风险 | HIGH | `memcpy` 无长度验证 | 潜在的缓冲区溢出 |
| 整数溢出 | MEDIUM | 无符号/有符号混用 | `int` 与 `size_t` 比较 |
| 格式化字符串 | HIGH | `printf(var)` | 用户可控的格式化字符串 |
| 硬编码凭证 | CRITICAL | `password = "xxx"` | 明文密钥/密码 |

### Level 2: AI 检查（需要上下文理解）

需要理解代码逻辑和状态才能发现的问题：

| 漏洞类型 | 严重程度 | 分析要点 | 说明 |
|---------|---------|---------|------|
| Use-After-Free | CRITICAL | 释放后使用指针 | 需要追踪指针生命周期 |
| Double Free | CRITICAL | 重复释放内存 | 需要分析控制流分支 |
| 内存泄漏 | MEDIUM | malloc 无对应 free | 需要理解函数退出路径 |
| 竞争条件 | HIGH | 并发访问共享资源 | 需要分析线程交互 |
| 逻辑错误 | MEDIUM | 错误的状态机转换 | 需要理解程序意图 |
| TOCTOU | HIGH | 检查与使用时序 | 需要分析时间窗口 |

## 使用脚本

### audit.py - 双重审计引擎

```bash
# Level 1: 代码检查（快速扫描）
python scripts/audit.py --target ./src --mode code

# Level 2: AI 检查（深度分析，由 AI 驱动）
python scripts/audit.py --target ./src --mode ai

# 完整审计（先代码检查，输出适合 AI 分析的格式）
python scripts/audit.py --target ./src --mode code --format ai

# 扫描单个文件
python scripts/audit.py --target ./main.c --mode code

# JSON 输出（便于程序化使用）
python scripts/audit.py --target ./src --mode code --format json
```

参数说明：
- `--target`: 要扫描的目录或 C 文件（必需）
- `--mode`: 审计模式，`code`（代码检查）或 `ai`（AI 检查）
- `--format`: 输出格式，`markdown`（人类可读）、`json`（结构化）、`ai`（供 AI 分析的简洁格式）

## 输出示例

### Level 1 代码检查报告

```markdown
# C 语言安全审计报告 - Level 1 代码检查

目标: ./src
扫描文件: 12 个
发现 Level 1 问题: 8 个

## 危险函数使用

### strcpy (HIGH)
- **文件**: `./src/utils.c:45`
- **描述**: 使用 strcpy 可能导致缓冲区溢出
- **代码**: `strcpy(buffer, input);`
- **修复建议**: 使用 strncpy(buffer, input, sizeof(buffer)-1);

### gets (CRITICAL)
- **文件**: `./src/main.c:23`
- **描述**: gets 函数无法限制输入长度，极度危险
- **代码**: `gets(user_input);`
- **修复建议**: 使用 fgets(user_input, sizeof(user_input), stdin);

### printf 格式化字符串 (HIGH)
- **文件**: `./src/log.c:78`
- **描述**: printf 第一个参数可能包含用户输入
- **代码**: `printf(user_msg);`
- **修复建议**: 使用 printf("%s", user_msg);

## 建议转 Level 2 分析的位置

以下位置需要 AI 进行深度上下文分析：
- `./src/memory.c:120-150` - 复杂的内存管理逻辑
- `./src/thread.c:45-80` - 并发访问代码块
```

### Level 2 AI 检查报告

由 AI 分析生成，包含：
- 内存生命周期分析图
- 竞争条件检测说明
- 状态机逻辑验证
- 修复建议及代码示例

## 修复建议

### Level 1 问题修复

**strcpy → strncpy**
```c
// 问题代码
char buffer[100];
strcpy(buffer, user_input);

// 修复代码
char buffer[100];
if (strlen(user_input) < sizeof(buffer)) {
    strncpy(buffer, user_input, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
}
```

**gets → fgets**
```c
// 问题代码
char input[256];
gets(input);

// 修复代码
char input[256];
if (fgets(input, sizeof(input), stdin) != NULL) {
    input[strcspn(input, "\n")] = 0; // 移除换行符
}
```

**printf 格式化字符串**
```c
// 问题代码
printf(user_message);

// 修复代码
printf("%s", user_message);
```

### Level 2 问题修复

需要 AI 根据具体上下文提供针对性修复方案，通常涉及：
- 引用计数管理
- 锁的使用顺序
- 状态机边界条件

## 使用建议

1. **CI/CD 集成**：Level 1 代码检查可集成到提交前钩子
2. **代码审查**：Level 2 AI 检查作为人工审查的辅助
3. **优先级**：先修复 Level 1 的 CRITICAL 和 HIGH 问题
4. **组合使用**：Level 1 快速定位可疑代码，Level 2 深度验证
