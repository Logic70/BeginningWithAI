---
name: echo-test
description: 回显测试，展示变量替换机制。用于学习 Skill 变量。
---

# Echo Test Skill

展示 Skill 变量如何传递给脚本，用于理解变量替换机制。

## 变量说明

| 变量 | 含义 | 示例 |
|------|------|------|
| `$0` | Skill 名称 | `echo-test` |
| `$ARGUMENTS` | 用户输入的完整参数字符串 | `hello world 123` |
| `${CLAUDE_SKILL_DIR}` | Skill 所在目录的绝对路径 | `/path/to/.Codex/skills/echo-test` |

## 工作流程

1. 显示 Skill 名称（$0）
2. 显示传入参数（$ARGUMENTS）
3. 显示 Skill 目录（${CLAUDE_SKILL_DIR}）

## 可用脚本

```bash
python scripts/echo.py "$0" "$ARGUMENTS"
```

## 测试示例

在 Codex 中输入：
```
/echo-test hello world 123
```

期望输出：
```
变量 $0 (Skill 名称): echo-test
变量 $ARGUMENTS (参数字符串): hello world 123
```
