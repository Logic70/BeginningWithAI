#!/usr/bin/env python3
"""
回显测试脚本 - Echo Test Skill 的脚本组件

功能：
    展示 Skill 变量如何传递给脚本

用法：
    python echo.py "$0" "$ARGUMENTS"

参数：
    argv[1]: Skill 名称（$0）
    argv[2]: 参数字符串（$ARGUMENTS）
"""
import sys


def main():
    skill_name = sys.argv[1] if len(sys.argv) > 1 else "未提供"
    arguments = sys.argv[2] if len(sys.argv) > 2 else "未提供"

    print(f"变量 $0 (Skill 名称): {skill_name}")
    print(f"变量 $ARGUMENTS (参数字符串): {arguments}")


if __name__ == "__main__":
    main()
