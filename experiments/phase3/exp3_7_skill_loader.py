"""
实验 3.7：Skills 三层加载机制核心实现
演示 Agent Skills 的 Level 1/2/3 加载流程

学习目标：
1. 理解 SkillLoader 如何实现三层加载机制
2. 掌握 SkillMetadata 和 SkillContent 的数据模型
3. 学会构建包含 Skills 的 system prompt

核心设计：
- Level 1: scan_skills() - 扫描元数据，注入 system prompt (~100 tokens/Skill)
- Level 2: load_skill() - 按需加载 SKILL.md 完整指令 (<5000 tokens)
- Level 3: bash 工具执行 - 脚本代码不进入上下文（由 Agent 实现）
"""

import re
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# ==================== 数据模型 ====================


@dataclass
class SkillMetadata:
    """
    Level 1: Skill 元数据（约 100 tokens）

    启动时从 YAML frontmatter 解析，用于注入 system prompt。
    这是三层加载机制的第一层。
    """
    name: str               # Skill 唯一名称
    description: str        # 何时使用此 skill 的描述
    skill_path: Path        # skill 目录路径

    def to_prompt_line(self) -> str:
        """生成 system prompt 中的单行描述"""
        return f"- **{self.name}**: {self.description}"


@dataclass
class SkillContent:
    """
    Level 2: Skill 完整内容（小于 5000 tokens）

    用户请求匹配时加载，包含 SKILL.md 的完整指令。
    这是三层加载机制的第二层。
    """
    metadata: SkillMetadata
    instructions: str       # SKILL.md body 内容（去除 frontmatter）


# ==================== SkillLoader 核心 ====================


class SkillLoader:
    """
    Skills 加载器 - 实现三层加载机制

    核心职责：
    1. scan_skills(): 发现文件系统中的 Skills，解析元数据（Level 1）
    2. load_skill(): 按需加载 Skill 详细内容（Level 2）
    3. build_system_prompt(): 生成包含 Skills 列表的 system prompt

    使用示例：
        loader = SkillLoader()

        # Level 1: 获取 system prompt
        system_prompt = loader.build_system_prompt()

        # Level 2: 加载具体 skill
        skill = loader.load_skill("port-scanner")
        print(skill.instructions)
    """

    # 默认 Skills 搜索路径（项目级优先，用户级兜底）
    DEFAULT_SKILL_PATHS = [
        Path.cwd() / ".claude" / "skills",      # 项目级 Skills - 优先
        Path.home() / ".claude" / "skills",    # 用户级 Skills - 兜底
    ]

    def __init__(self, skill_paths: list[Path] | None = None, project_root: Path | None = None):
        """
        初始化加载器

        Args:
            skill_paths: 自定义 Skills 搜索路径，默认为项目级 + 用户级
            project_root: 项目根目录，用于定位 .claude/skills
        """
        if skill_paths:
            self.skill_paths = skill_paths
        elif project_root:
            # 使用指定的项目根目录
            self.skill_paths = [
                project_root / ".claude" / "skills",
                Path.home() / ".claude" / "skills",
            ]
        else:
            # 自动查找项目根目录（向上查找直到找到 .claude 或 .git）
            self.skill_paths = self._find_project_skill_paths()

        self._metadata_cache: dict[str, SkillMetadata] = {}

    def _find_project_skill_paths(self) -> list[Path]:
        """自动查找项目级 Skills 路径"""
        # 从当前工作目录向上查找
        current = Path.cwd()

        # 向上查找 5 层目录
        for _ in range(5):
            skill_dir = current / ".claude" / "skills"
            if skill_dir.exists():
                return [skill_dir, Path.home() / ".claude" / "skills"]

            # 检查是否是项目根目录（有 .git 或 README）
            if (current / ".git").exists() or (current / "README.md").exists():
                # 在根目录下检查 .claude/skills
                skill_dir = current / ".claude" / "skills"
                if skill_dir.exists():
                    return [skill_dir, Path.home() / ".claude" / "skills"]
                break

            # 向上移动
            parent = current.parent
            if parent == current:  # 到达根目录
                break
            current = parent

        # 默认使用当前目录
        return self.DEFAULT_SKILL_PATHS

    def scan_skills(self) -> list[SkillMetadata]:
        """
        Level 1: 扫描所有 Skills 元数据

        遍历 skill_paths，查找包含 SKILL.md 的目录，
        解析 YAML frontmatter 提取 name 和 description。

        Returns:
            所有发现的 Skills 元数据列表

        示例输出：
            [
                SkillMetadata(name='hello-world', description='向你问好...'),
                SkillMetadata(name='port-scanner', description='扫描目标主机的端口...'),
            ]
        """
        skills = []
        seen_names = set()

        for base_path in self.skill_paths:
            if not base_path.exists():
                continue

            # 遍历 skills 目录下的每个子目录
            for skill_dir in base_path.iterdir():
                if not skill_dir.is_dir():
                    continue

                # 检查是否存在 SKILL.md
                skill_md = skill_dir / "SKILL.md"
                if not skill_md.exists():
                    continue

                # 解析元数据
                metadata = self._parse_skill_metadata(skill_md)
                if metadata and metadata.name not in seen_names:
                    skills.append(metadata)
                    seen_names.add(metadata.name)
                    self._metadata_cache[metadata.name] = metadata

        return skills

    def _parse_skill_metadata(self, skill_md_path: Path) -> Optional[SkillMetadata]:
        """
        解析 SKILL.md 的 YAML frontmatter

        SKILL.md 格式：
            ---
            name: skill-name
            description: Brief description when to use it
            ---
            # Instructions...

        Args:
            skill_md_path: SKILL.md 文件路径

        Returns:
            解析后的元数据，解析失败返回 None
        """
        try:
            content = skill_md_path.read_text(encoding="utf-8")
        except Exception:
            return None

        # 使用正则提取 YAML frontmatter
        # 格式: ---\n...yaml...\n---
        frontmatter_match = re.match(
            r'^---\s*\n(.*?)\n---\s*\n',
            content,
            re.DOTALL
        )

        if not frontmatter_match:
            return None

        try:
            # 解析 YAML
            frontmatter = yaml.safe_load(frontmatter_match.group(1))

            name = frontmatter.get("name", "")
            description = frontmatter.get("description", "")

            if not name:
                return None

            return SkillMetadata(
                name=name,
                description=description,
                skill_path=skill_md_path.parent,
            )
        except yaml.YAMLError:
            return None

    def load_skill(self, skill_name: str) -> Optional[SkillContent]:
        """
        Level 2: 加载 Skill 完整内容

        读取 SKILL.md 的完整指令（去除 frontmatter）。
        这是 load_skill tool 的核心实现。

        Args:
            skill_name: Skill 名称（如 "hello-world"）

        Returns:
            Skill 完整内容，未找到返回 None

        注意：
            只返回 instructions，让大模型从指令中自己发现脚本和文档。
            这是 Anthropic Skills 的核心设计理念。
        """
        # 先检查缓存
        metadata = self._metadata_cache.get(skill_name)
        if not metadata:
            # 尝试重新扫描
            self.scan_skills()
            metadata = self._metadata_cache.get(skill_name)

        if not metadata:
            return None

        # 读取 SKILL.md 完整内容
        skill_md = metadata.skill_path / "SKILL.md"
        try:
            content = skill_md.read_text(encoding="utf-8")
        except Exception:
            return None

        # 提取 body（去除 frontmatter）
        body_match = re.match(
            r'^---\s*\n.*?\n---\s*\n(.*)$',
            content,
            re.DOTALL
        )
        instructions = body_match.group(1).strip() if body_match else content

        # 只返回 instructions，让大模型从指令中自己发现脚本和文档
        return SkillContent(
            metadata=metadata,
            instructions=instructions,
        )

    def build_system_prompt(self, base_prompt: str = "") -> str:
        """
        构建包含 Skills 列表的 system prompt

        这是 Level 1 的核心输出：将所有 Skills 的元数据
        注入到 system prompt 中。

        Args:
            base_prompt: 基础 system prompt（可选）

        Returns:
            完整的 system prompt
        """
        skills = self.scan_skills()

        # 构建 Skills 部分
        if skills:
            skills_section = "## Available Skills\n\n"
            skills_section += "You have access to the following specialized skills:\n\n"
            for skill in skills:
                skills_section += skill.to_prompt_line() + "\n"
            skills_section += "\n"
            skills_section += "### How to Use Skills\n\n"
            skills_section += "1. **Discover**: Review the skills list above\n"
            skills_section += "2. **Load**: When a user request matches a skill's description, "
            skills_section += "use `load_skill(skill_name)` to get detailed instructions\n"
            skills_section += "3. **Execute**: Follow the skill's instructions, which may include "
            skills_section += "running scripts via `bash`\n\n"
            skills_section += "**Important**: Only load a skill when it's relevant to the user's request. "
            skills_section += "Script code never enters the context - only their output does.\n"
        else:
            skills_section = "## Skills\n\nNo skills currently available.\n"

        # 组合完整 prompt
        if base_prompt:
            return f"{base_prompt}\n\n{skills_section}"
        else:
            return f"You are a helpful assistant.\n\n{skills_section}"


# ==================== 便捷函数 ====================

def discover_skills(skill_paths: list[Path] | None = None) -> list[SkillMetadata]:
    """便捷函数：发现所有 Skills"""
    loader = SkillLoader(skill_paths)
    return loader.scan_skills()


def get_skill_content(skill_name: str, skill_paths: list[Path] | None = None) -> Optional[SkillContent]:
    """便捷函数：获取 Skill 内容"""
    loader = SkillLoader(skill_paths)
    return loader.load_skill(skill_name)


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("实验 3.7：Skills 三层加载机制")
    print("=" * 60)

    loader = SkillLoader()

    # Level 1: 扫描元数据
    print("\n" + "-" * 60)
    print("Level 1: 扫描 Skills 元数据")
    print("-" * 60)
    skills = loader.scan_skills()
    print(f"发现 {len(skills)} 个 Skills:\n")
    for skill in skills:
        print(f"  [Skill] {skill.name}")
        print(f"     描述: {skill.description}")
        print(f"     路径: {skill.skill_path}")
        print()

    # Level 1: 构建 System Prompt
    print("-" * 60)
    print("Level 1: System Prompt 片段")
    print("-" * 60)
    system_prompt = loader.build_system_prompt()
    print(system_prompt[:800] + "\n..." if len(system_prompt) > 800 else system_prompt)

    # Level 2: 加载具体 Skill
    if skills:
        print("\n" + "-" * 60)
        print(f"Level 2: 加载 Skill '{skills[0].name}'")
        print("-" * 60)
        content = loader.load_skill(skills[0].name)
        if content:
            print(f"Instructions 长度: {len(content.instructions)} 字符")
            print("\nInstructions 前 300 字符:")
            print(content.instructions[:300])
            print("\n...")

    print("\n" + "=" * 60)
    print("实验完成！")
    print("=" * 60)
