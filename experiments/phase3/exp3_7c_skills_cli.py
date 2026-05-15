"""
实验 3.7c：Skills Agent CLI 交互
支持 --list-skills 查看可用 Skills，交互式对话，验证三层加载机制

学习目标：
1. 学会验证 Level 1：Skills 元数据扫描
2. 学会验证 Level 2：Skill 指令加载
3. 学会验证 Level 3：脚本执行

使用方式：
    # 列出所有 Skills（Level 1 验证）
    python exp3_7c_skills_cli.py --list-skills

    # 显示 System Prompt（Level 1 验证）
    python exp3_7c_skills_cli.py --show-prompt

    # 执行单次任务
    python exp3_7c_skills_cli.py "帮我扫描 localhost 的端口"

    # 交互模式
    python exp3_7c_skills_cli.py

    # 使用 OpenAI API
    python exp3_7c_skills_cli.py --backend openai "你好"
"""

import argparse
import os
import sys
from pathlib import Path

# 确保能导入同级目录的模块
sys.path.insert(0, str(Path(__file__).parent))

from exp3_7_skill_loader import SkillLoader
from exp3_7b_skills_agent import SkillsAgent


def list_skills():
    """列出所有可用的 Skills（Level 1 验证）"""
    loader = SkillLoader()
    skills = loader.scan_skills()

    print("=" * 60)
    print("Level 1 验证：Skills 元数据列表")
    print("=" * 60)

    if not skills:
        print("\n[警告] 未找到任何 Skills")
        print(f"搜索路径:")
        for path in loader.DEFAULT_SKILL_PATHS:
            print(f"  - {path}")
        print("\n请确保上述路径中存在有效的 Skill 目录（包含 SKILL.md）")
        return

    print(f"\n[OK] 发现 {len(skills)} 个 Skills:\n")
    for skill in skills:
        print(f"[Skill] {skill.name}")
        print(f"   描述: {skill.description}")
        print(f"   路径: {skill.skill_path}")
        print()

    print(f"总计: {len(skills)} 个 Skills")


def show_system_prompt():
    """显示 System Prompt（Level 1 验证）"""
    loader = SkillLoader()
    prompt = loader.build_system_prompt()

    print("=" * 60)
    print("Level 1 验证：System Prompt（Skills 部分）")
    print("=" * 60)
    print()
    print(prompt)
    print()
    print("=" * 60)
    print(f"总长度: {len(prompt)} 字符")


def show_skill_detail(skill_name: str):
    """显示 Skill 详细内容（Level 2 验证）"""
    loader = SkillLoader()
    content = loader.load_skill(skill_name)

    print("=" * 60)
    print(f"Level 2 验证：Skill '{skill_name}' 详细内容")
    print("=" * 60)

    if not content:
        print(f"\n⚠️ Skill '{skill_name}' 未找到")
        skills = loader.scan_skills()
        if skills:
            print(f"可用 Skills: {', '.join(s.name for s in skills)}")
        return

    print(f"\n元数据:")
    print(f"  名称: {content.metadata.name}")
    print(f"  描述: {content.metadata.description}")
    print(f"  路径: {content.metadata.skill_path}")
    print()
    print("Instructions:")
    print("-" * 60)
    print(content.instructions[:1500])
    if len(content.instructions) > 1500:
        print("\n... (截断)")
    print("-" * 60)
    print(f"总长度: {len(content.instructions)} 字符")


def interactive_mode(agent: SkillsAgent):
    """交互式对话模式"""
    print("=" * 60)
    print("Skills Agent 交互模式")
    print("输入 'quit' 或 'exit' 退出")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n用户: ").strip()

            if user_input.lower() in ("quit", "exit", "q"):
                print("\n再见！")
                break

            if not user_input:
                continue

            print("\nAgent 思考中...")
            print("-" * 60)
            result = agent.run(user_input)
            print("-" * 60)
            print(f"\nAgent: {result}")

        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except EOFError:
            break


def main():
    parser = argparse.ArgumentParser(
        description="Skills Agent CLI - 验证三层加载机制",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # Level 1 验证
  python %(prog)s --list-skills
  python %(prog)s --show-prompt

  # Level 2 验证
  python %(prog)s --show-skill hello-world

  # Level 3 验证（执行 Skill）
  python %(prog)s "帮我扫描 localhost 的 80 端口"

  # 交互模式
  python %(prog)s

  # 使用 OpenAI API
  python %(prog)s --backend openai "你好"
        """
    )

    parser.add_argument(
        "--list-skills",
        action="store_true",
        help="Level 1: 列出所有可用的 Skills"
    )
    parser.add_argument(
        "--show-prompt",
        action="store_true",
        help="Level 1: 显示 System Prompt"
    )
    parser.add_argument(
        "--show-skill",
        metavar="NAME",
        help="Level 2: 显示指定 Skill 的详细内容"
    )
    parser.add_argument(
        "--backend",
        choices=["ollama", "openai"],
        default="openai",
        help="选择后端 (默认: openai)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="指定模型名称"
    )
    parser.add_argument(
        "task",
        nargs="?",
        help="要执行的任务（可选，不提供则进入交互模式）"
    )

    args = parser.parse_args()

    # 模式 1: 列出 Skills
    if args.list_skills:
        list_skills()
        return

    # 模式 2: 显示 Prompt
    if args.show_prompt:
        show_system_prompt()
        return

    # 模式 3: 显示 Skill 详情
    if args.show_skill:
        show_skill_detail(args.show_skill)
        return

    # 确定模型：优先级 1) 命令行参数 2) 环境变量 3) 默认值
    model = args.model
    if not model:
        if args.backend == "ollama":
            model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        else:
            model = os.getenv("OPENAI_MODEL", "deepseek-v4-pro")

    # 创建 Agent
    agent = SkillsAgent(model=model, backend=args.backend)

    # 模式 4: 单次任务
    if args.task:
        print("=" * 60)
        print("Skills Agent - 单次任务")
        print("=" * 60)
        print(f"后端: {args.backend}")
        print(f"模型: {model}")
        print(f"任务: {args.task}\n")
        result = agent.run(args.task)
        print(f"\n结果: {result}")
        return

    # 模式 5: 交互模式
    print(f"后端: {args.backend}")
    print(f"模型: {model}")
    interactive_mode(agent)


if __name__ == "__main__":
    main()
