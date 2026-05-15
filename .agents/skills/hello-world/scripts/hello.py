#!/usr/bin/env python3
"""
问候脚本 - Hello World Skill 的脚本组件

功能：
1. 获取当前时间
2. 根据时间判断时段
3. 输出个性化问候语

用法：
    python hello.py [名字]

示例：
    python hello.py
    python hello.py 张三
"""
import sys
from datetime import datetime


def get_greeting(hour: int) -> str:
    """根据小时数返回时段问候"""
    if 5 <= hour < 12:
        return "早上好"
    elif 12 <= hour < 18:
        return "下午好"
    else:
        return "晚上好"


def main():
    # 获取名字参数，默认为"朋友"
    name = sys.argv[1] if len(sys.argv) > 1 else "朋友"

    # 获取当前时间
    now = datetime.now()
    hour = now.hour

    # 获取问候语
    greeting = get_greeting(hour)

    # 输出结果
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"问候: {greeting}，{name}！")


if __name__ == "__main__":
    main()
