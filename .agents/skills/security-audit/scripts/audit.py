#!/usr/bin/env python3
"""
C 语言安全审计脚本 - 支持代码检查（Level 1）和 AI 检查（Level 2）两种模式

功能：
    - Level 1 (code): 使用正则表达式匹配明确的安全漏洞模式
    - Level 2 (ai):  准备供 AI 深度分析的上下文信息

用法：
    python audit.py --target <路径> --mode <code|ai> [--format json|markdown|ai]

示例：
    # Level 1: 代码检查（快速扫描危险函数）
    python audit.py --target ./src --mode code

    # Level 2: AI 检查准备（输出供 AI 分析的格式）
    python audit.py --target ./src --mode code --format ai

    # JSON 输出（程序化使用）
    python audit.py --target ./src --mode code --format json

输出格式：
    - markdown: 人类可读的完整报告
    - json:     结构化数据
    - ai:       供 AI 分析的简洁格式（仅 Level 1 可疑位置）
"""

import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Finding:
    """安全发现"""
    file: str
    line: int
    type: str
    severity: str
    description: str
    code: str
    category: str  # "code" 或 "ai"
    suggestion: Optional[str] = None


class CSecurityAuditor:
    """
    C 语言安全审计器

    支持两种检查方式：
    1. Level 1 - 代码检查：使用正则匹配明确的危险模式
    2. Level 2 - AI 检查：准备上下文供 AI 分析复杂问题
    """

    # C 文件扩展名
    C_EXTENSIONS = {".c", ".h", ".cpp", ".hpp", ".cc"}

    # Level 1: 代码检查模式 - 文本可明确识别的危险
    CODE_PATTERNS = {
        # 危险字符串操作函数
        "dangerous_strcpy": {
            "pattern": r"\bstrcpy\s*\(",
            "description": "使用 strcpy 可能导致缓冲区溢出",
            "severity": "HIGH",
            "suggestion": "使用 strncpy(dest, src, sizeof(dest)-1) 并确保终止符",
            "category": "code"
        },
        "dangerous_strcat": {
            "pattern": r"\bstrcat\s*\(",
            "description": "使用 strcat 可能导致缓冲区溢出",
            "severity": "HIGH",
            "suggestion": "使用 strncat(dest, src, sizeof(dest)-strlen(dest)-1)",
            "category": "code"
        },
        "dangerous_sprintf": {
            "pattern": r"\bsprintf\s*\(",
            "description": "使用 sprintf 可能导致缓冲区溢出",
            "severity": "HIGH",
            "suggestion": "使用 snprintf(buf, sizeof(buf), fmt, ...)",
            "category": "code"
        },
        "dangerous_gets": {
            "pattern": r"\bgets\s*\(",
            "description": "gets 函数无法限制输入长度，极度危险",
            "severity": "CRITICAL",
            "suggestion": "使用 fgets(buf, sizeof(buf), stdin) 替代",
            "category": "code"
        },
        "dangerous_scanf": {
            "pattern": r'\bscanf\s*\(\s*["\'][^"\']*%s',
            "description": "scanf %s 无长度限制，可能导致溢出",
            "severity": "HIGH",
            "suggestion": '使用 scanf("%255s", buf) 指定最大长度',
            "category": "code"
        },

        # 内存操作风险
        "unchecked_memcpy": {
            "pattern": r"\bmemcpy\s*\([^,]+,\s*[^,]+\)",
            "description": "memcpy 目标/源长度未验证",
            "severity": "MEDIUM",
            "suggestion": "确保目标缓冲区足够大，或改用 memmove",
            "category": "code"
        },
        "unchecked_malloc": {
            "pattern": r"\b(malloc|calloc|realloc)\s*\([^)]+\)\s*;?\s*$",
            "description": "内存分配结果未检查",
            "severity": "MEDIUM",
            "suggestion": "检查返回值: if ((ptr = malloc(size)) == NULL) { handle_error(); }",
            "category": "code"
        },

        # 格式化字符串 - 匹配 printf(var) 而不是 printf("fmt", ...)
        "format_string_vuln": {
            "pattern": r"\b(printf|fprintf|sprintf|snprintf|syslog)\s*\(\s*[^'\"\)]*\)",
            "description": "格式化字符串可能包含用户输入",
            "severity": "HIGH",
            "suggestion": "使用 printf(\"%s\", user_input) 固定格式",
            "category": "code"
        },

        # 命令执行
        "system_call": {
            "pattern": r"\bsystem\s*\(",
            "description": "使用 system() 执行命令，存在命令注入风险",
            "severity": "HIGH",
            "suggestion": "使用 execve() 等 exec 族函数，避免 shell 解释",
            "category": "code"
        },
        "popen_call": {
            "pattern": r"\bpopen\s*\(",
            "description": "使用 popen 执行命令，存在命令注入风险",
            "severity": "HIGH",
            "suggestion": "使用 pipe() + fork() + exec() 组合",
            "category": "code"
        },

        # 整数溢出风险
        "unchecked_multiplication": {
            "pattern": r"malloc\s*\(\s*[^)]*\*\s*[^)]+\)",
            "description": "malloc 中使用乘法可能导致整数溢出",
            "severity": "MEDIUM",
            "suggestion": "检查乘法溢出: if (nmemb && size > SIZE_MAX / nmemb) { handle_error(); }",
            "category": "code"
        },
        "unchecked_addition": {
            "pattern": r"(malloc|calloc|realloc)\s*\(\s*[^)]+\+\s*[^)]+\)",
            "description": "内存分配中使用加法可能导致整数溢出",
            "severity": "MEDIUM",
            "suggestion": "检查加法溢出: if (size1 > SIZE_MAX - size2) { handle_error(); }",
            "category": "code"
        },
        "unchecked_subtraction": {
            "pattern": r"(malloc|calloc|realloc)\s*\(\s*[^)]+\-\s*[^)]+\)",
            "description": "内存分配中使用减法可能导致整数下溢",
            "severity": "MEDIUM",
            "suggestion": "确保减法结果非负: if (size1 < size2) { handle_error(); }",
            "category": "code"
        },
        # 变量赋值中的整数运算溢出（不局限于内存分配）
        "integer_overflow_in_assignment": {
            "pattern": r"int\s+\w+\s*=\s*[^;]+\+\s*[^;]+\s*;",
            "description": "整数加法可能导致溢出",
            "severity": "LOW",
            "suggestion": "检查加法溢出: if (a > INT_MAX - b) { handle_error(); }",
            "category": "code"
        },
        "integer_underflow_in_assignment": {
            "pattern": r"int\s+\w+\s*=\s*[^;]+\-\s*[^;]+\s*;",
            "description": "整数减法可能导致下溢",
            "severity": "LOW",
            "suggestion": "确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }",
            "category": "code"
        },
        "implicit_conversion": {
            "pattern": r"(size_t|unsigned)\s+\w+\s*=\s*-",
            "description": "无符号类型赋负值导致大正数",
            "severity": "MEDIUM",
            "suggestion": "检查赋值范围，避免无符号/有符号混用",
            "category": "code"
        },

        # 除零风险 - 只匹配实际的除法表达式，排除注释
        "divide_by_zero": {
            "pattern": r"\w+\s*/\s*\w+",
            "description": "除法操作未检查除数是否为零",
            "severity": "MEDIUM",
            "suggestion": "检查除数: if (divisor == 0) { handle_error(); }",
            "category": "code"
        },

        # 返回局部变量地址
        "return_local_address": {
            "pattern": r"return\s+&\w+\[?[^\]]*\]?;",
            "description": "返回局部变量地址（悬垂指针）",
            "severity": "HIGH",
            "suggestion": "使用堆分配或传入缓冲区参数",
            "category": "code"
        },

        # 未初始化使用 - 检测声明但没有初始化的变量
        "uninitialized_variable": {
            "pattern": r"\b(int|char|long|short|float|double|size_t)\s+\w+\s*;(?![^\n]*=)",
            "description": "变量声明后未初始化",
            "severity": "LOW",
            "suggestion": "声明时初始化: int x = 0;",
            "category": "code"
        },

        # 缓冲区访问
        "unchecked_array_access": {
            "pattern": r"\w+\[\w+\]\s*=",
            "description": "数组访问可能越界（无边界检查）",
            "severity": "MEDIUM",
            "suggestion": "添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))",
            "category": "code"
        },

        # 字符串处理
        "strncpy_without_null": {
            "pattern": r"strncpy\s*\([^,]+,[^,]+,\s*\w+\)(?!\s*;\s*\w+\[)",
            "description": "strncpy 可能不添加终止符",
            "severity": "MEDIUM",
            "suggestion": "手动添加终止符: dest[n-1] = '\\0';",
            "category": "code"
        },

        # 硬编码凭证 - 改进模式以匹配更多变体
        "hardcoded_password": {
            "pattern": r"\b(password|passwd|secret|key|token|api_key|apikey)\w*\s*(\[\s*\]|\*)?\s*=?\s*['\"][^'\"]+['\"]",
            "description": "硬编码密码或密钥",
            "severity": "CRITICAL",
            "suggestion": "从环境变量或配置文件读取",
            "category": "code"
        },
        "hardcoded_credential_var": {
            "pattern": r"\b(char|wchar_t)\s+\*?\s*\w*(password|passwd|secret|key|token|api_key|apikey)\w*\s*(\[\s*\])?\s*=\s*['\"]",
            "description": "硬编码密码或密钥变量声明",
            "severity": "CRITICAL",
            "suggestion": "从环境变量或配置文件读取",
            "category": "code"
        },

        # 整数溢出
        "signed_unsigned_cmp": {
            "pattern": r"\bsizeof\s*\([^)]+\)\s*[<>]=?\s*-",
            "description": "有符号与无符号数比较可能导致问题",
            "severity": "MEDIUM",
            "suggestion": "确保比较操作符两侧类型一致",
            "category": "code"
        },

        # 不安全的随机数
        "insecure_random": {
            "pattern": r"\brand\s*\(",
            "description": "rand() 不是加密安全的随机数生成器",
            "severity": "MEDIUM",
            "suggestion": "安全敏感场景使用 /dev/urandom 或 OpenSSL RAND_bytes",
            "category": "code"
        },

        # 竞态条件
        "tmpnam_usage": {
            "pattern": r"\btmpnam\s*\(|\btempnam\s*\(",
            "description": "tmpnam/tempnam 存在 TOCTOU 竞态条件",
            "severity": "MEDIUM",
            "suggestion": "使用 mkstemp() 替代",
            "category": "code"
        },
        "access_toctou": {
            "pattern": r"\baccess\s*\(",
            "description": "access() 存在 TOCTOU 竞态条件",
            "severity": "MEDIUM",
            "suggestion": "直接打开文件并使用 fstat 检查权限，而非先 access 后 open",
            "category": "code"
        },

        # 并发操作
        "pthread_mutex_lock": {
            "pattern": r"\bpthread_mutex_lock\s*\(",
            "description": "互斥锁操作，需要检查死锁风险",
            "severity": "MEDIUM",
            "suggestion": "确保锁在异常路径也能释放，考虑使用 pthread_mutex_timedlock",
            "category": "code"
        },

        # 内存管理复杂漏洞（基于代码模式的初步检测）
        "multiple_free_in_scope": {
            "pattern": r"free\s*\([^)]+\)[^;]*;",
            "description": "检测到 free 调用，需检查是否存在双重释放风险",
            "severity": "LOW",
            "suggestion": "确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;",
            "category": "code"
        },
        "pointer_assignment_after_free_risk": {
            "pattern": r"free\s*\(",
            "description": "内存释放操作，需检查后续是否存在释放后使用风险",
            "severity": "LOW",
            "suggestion": "释放后立即将指针置为 NULL，避免释放后使用",
            "category": "code"
        },
        "potential_memory_leak": {
            "pattern": r"\b\w+\s*=\s*0\s*;",
            "description": "指针被覆盖为零，可能导致内存泄漏",
            "severity": "MEDIUM",
            "suggestion": "在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;",
            "category": "code"
        },

        # 递归和栈风险 - 通过代码逻辑检测而非正则
        "infinite_loop_risk": {
            "pattern": r"while\s*\(\s*1\s*\)",
            "description": "无限循环 while(1) 可能导致拒绝服务",
            "severity": "LOW",
            "suggestion": "确保循环内有退出条件: break、return 或 exit",
            "category": "code"
        },
    }

    # Level 2: AI 检查标记 - 需要上下文理解的可疑点
    AI_CHECK_MARKERS = {
        "memory_management": {
            "patterns": [r"\bmalloc\s*\(", r"\bfree\s*\(", r"\bcalloc\s*\(", r"\brealloc\s*\("],
            "description": "内存管理区域（需要 AI 检查 use-after-free, double-free, memory leak）",
            "context_lines": 10
        },
        "pointer_usage": {
            "patterns": [r"\*\s*\w+", r"->\s*\w+"],
            "description": "指针解引用区域（需要 AI 检查空指针、野指针）",
            "context_lines": 5
        },
        "thread_operations": {
            "patterns": [r"\bpthread_", r"\bmutex_", r"\bsem_", r"\bspin_"],
            "description": "并发操作区域（需要 AI 检查 race condition, deadlock）",
            "context_lines": 15
        },
        "file_operations": {
            "patterns": [r"\bfopen\s*\(", r"\bopen\s*\(", r"\bfstat\s*\("],
            "description": "文件操作区域（需要 AI 检查 TOCTOU）",
            "context_lines": 8
        },
        "signal_handling": {
            "patterns": [r"\bsignal\s*\(", r"\bsigaction\s*\("],
            "description": "信号处理区域（需要 AI 检查异步安全）",
            "context_lines": 10
        },
    }

    def __init__(self, target: Path):
        self.target = target
        self.findings: List[Finding] = []
        self.ai_regions: List[Dict[str, Any]] = []

    def scan_file_code(self, file_path: Path) -> List[Finding]:
        """
        Level 1: 代码检查 - 使用正则匹配明确的安全问题
        """
        findings = []

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")

            for vuln_name, vuln_info in self.CODE_PATTERNS.items():
                for line_num, line in enumerate(lines, 1):
                    if re.search(vuln_info["pattern"], line, re.IGNORECASE):
                        findings.append(Finding(
                            file=str(file_path),
                            line=line_num,
                            type=vuln_name,
                            severity=vuln_info["severity"],
                            description=vuln_info["description"],
                            code=line.strip()[:120],
                            category="code",
                            suggestion=vuln_info.get("suggestion")
                        ))

            # 额外检测：递归函数调用（需要多行分析，不能用简单正则）
            findings.extend(self._detect_recursive_calls(file_path, content, lines))

        except Exception as e:
            findings.append(Finding(
                file=str(file_path),
                line=0,
                type="error",
                severity="LOW",
                description=f"扫描错误: {str(e)}",
                code="",
                category="code"
            ))

        return findings

    def scan_file_ai_markers(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        标记需要 AI 检查的区域
        """
        regions = []

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")

            for marker_name, marker_info in self.AI_CHECK_MARKERS.items():
                for line_num, line in enumerate(lines, 1):
                    for pattern in marker_info["patterns"]:
                        if re.search(pattern, line):
                            # 提取上下文
                            start = max(0, line_num - marker_info["context_lines"])
                            end = min(len(lines), line_num + marker_info["context_lines"])
                            context = "\n".join(lines[start:end])

                            regions.append({
                                "file": str(file_path),
                                "line": line_num,
                                "type": marker_name,
                                "description": marker_info["description"],
                                "code": line.strip()[:100],
                                "context": context,
                                "context_lines": f"{start+1}-{end}"
                            })
                            break  # 避免同一行重复匹配同一 marker 的不同 pattern

        except Exception:
            pass

        return regions

    def _detect_recursive_calls(self, file_path: Path, content: str, lines: List[str]) -> List[Finding]:
        """
        检测递归函数调用
        通过分析函数定义和函数体内的调用关系来检测
        """
        findings = []

        # 简单的函数定义匹配: 返回类型 函数名(参数) { ... }
        # 匹配 void func() { ... func(...); ... }
        func_def_pattern = r'(\w+)\s+(\w+)\s*\([^)]*\)\s*\{'

        # 找到所有函数定义
        for line_num, line in enumerate(lines, 1):
            match = re.search(func_def_pattern, line)
            if match:
                func_name = match.group(2)
                # 在接下来的行中查找是否调用了自己
                brace_count = line.count('{') - line.count('}')
                if brace_count <= 0:
                    continue

                # 搜索函数体内是否有对同一函数的调用
                for j in range(line_num, min(line_num + 50, len(lines))):
                    inner_line = lines[j]
                    # 检查是否调用了自己
                    if re.search(rf'\b{func_name}\s*\(', inner_line):
                        findings.append(Finding(
                            file=str(file_path),
                            line=j + 1,
                            type="recursive_function_call",
                            severity="MEDIUM",
                            description="函数内部调用自身可能导致栈溢出",
                            code=inner_line.strip()[:120],
                            category="code",
                            suggestion="添加递归深度限制或使用迭代替代"
                        ))
                        break  # 找到一个就够了

        return findings

    def scan(self, mode: str = "code") -> Dict[str, Any]:
        """
        执行扫描

        Args:
            mode: "code" 进行代码检查，"ai" 准备 AI 分析数据
        """
        result = {
            "target": str(self.target),
            "mode": mode,
            "files_scanned": 0,
            "findings": [],
            "ai_regions": []
        }

        files_to_scan = []

        if self.target.is_file():
            if self.target.suffix in self.C_EXTENSIONS:
                files_to_scan = [self.target]
        else:
            for ext in self.C_EXTENSIONS:
                for file_path in self.target.rglob(f"*{ext}"):
                    # 跳过常见非源码目录
                    if any(skip in str(file_path) for skip in [".git", "node_modules", ".venv", "build", "dist"]):
                        continue
                    files_to_scan.append(file_path)

        for file_path in files_to_scan:
            result["files_scanned"] += 1

            if mode in ("code", "both"):
                findings = self.scan_file_code(file_path)
                self.findings.extend(findings)

            # 总是收集 AI 检查区域（用于 --format ai 输出）
            regions = self.scan_file_ai_markers(file_path)
            self.ai_regions.extend(regions)

        result["findings"] = [asdict(f) for f in self.findings]
        result["ai_regions"] = self.ai_regions
        result["total_findings"] = len(self.findings)
        result["ai_check_count"] = len(self.ai_regions)

        return result

    def to_markdown(self, result: Dict[str, Any]) -> str:
        """生成 Markdown 报告"""
        lines = [
            "# C 语言安全审计报告",
            "",
            f"**目标**: `{result['target']}`",
            f"**模式**: {result['mode']}",
            f"**扫描文件**: {result['files_scanned']} 个",
            f"**Level 1 问题**: {result['total_findings']} 个",
            f"**Level 2 待检区域**: {result['ai_check_count']} 个",
            "",
        ]

        # Level 1 发现
        if result['findings']:
            lines.append("## Level 1 代码检查结果")
            lines.append("")

            # 按严重程度排序
            severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
            sorted_findings = sorted(
                result['findings'],
                key=lambda x: severity_order.get(x.get("severity", "LOW"), 4)
            )

            for finding in sorted_findings:
                if finding['type'] == 'error':
                    lines.append(f"- ⚠️ **Error**: {finding['description']}")
                    continue

                lines.append(f"### {finding['type']} ({finding['severity']})")
                lines.append(f"- **文件**: `{finding['file']}:{finding['line']}`")
                lines.append(f"- **描述**: {finding['description']}")
                lines.append(f"- **代码**: `{finding['code']}`")
                if finding.get('suggestion'):
                    lines.append(f"- **建议**: {finding['suggestion']}")
                lines.append("")
        else:
            lines.append("## Level 1 代码检查结果")
            lines.append("✅ 未发现明确的代码级安全问题")
            lines.append("")

        # Level 2 待检区域
        if result['ai_regions']:
            lines.append("## Level 2 AI 检查建议区域")
            lines.append("")
            lines.append("以下区域需要 AI 进行深度上下文分析：")
            lines.append("")

            for region in result['ai_regions'][:20]:  # 限制数量
                lines.append(f"### {region['type']}")
                lines.append(f"- **文件**: `{region['file']}:{region['line']}`")
                lines.append(f"- **说明**: {region['description']}")
                lines.append(f"- **代码**: `{region['code']}`")
                lines.append("")

        # 修复建议汇总
        lines.append("## 修复建议汇总")
        lines.append("")
        lines.append("### Level 1 快速修复")
        lines.append("")
        lines.append("| 原函数 | 安全替代 | 风险 |")
        lines.append("|--------|----------|------|")
        lines.append("| strcpy | strncpy | 缓冲区溢出 |")
        lines.append("| strcat | strncat | 缓冲区溢出 |")
        lines.append("| sprintf | snprintf | 缓冲区溢出 |")
        lines.append("| gets | fgets | 无限制输入 |")
        lines.append("| scanf | scanf with limit | 格式问题 |")
        lines.append("| system | execve | 命令注入 |")
        lines.append("")
        lines.append("### Level 2 检查要点")
        lines.append("")
        lines.append("- [ ] 检查所有 malloc/free 配对")
        lines.append("- [ ] 验证指针使用前的有效性")
        lines.append("- [ ] 确认并发代码的锁使用")
        lines.append("- [ ] 审查文件操作的 TOCTOU 风险")
        lines.append("")

        return "\n".join(lines)

    def to_ai_format(self, result: Dict[str, Any]) -> str:
        """
        生成供 AI 分析的简洁格式
        """
        lines = [
            "# C Code Security Analysis Input",
            "",
            f"Target: {result['target']}",
            f"Files: {result['files_scanned']}",
            f"Level 1 Issues: {result['total_findings']}",
            f"Level 2 Regions: {result['ai_check_count']}",
            "",
            "## Level 1 Findings (Code Check)",
            "",
        ]

        # 简化的 Level 1 发现
        for finding in result['findings'][:50]:  # 限制数量避免过长
            if finding['type'] == 'error':
                continue
            lines.append(f"[{finding['severity']}] {finding['file']}:{finding['line']}")
            lines.append(f"  Type: {finding['type']}")
            lines.append(f"  Code: {finding['code'][:80]}")
            lines.append("")

        # Level 2 需要 AI 分析的区域
        lines.append("## Level 2 Regions for AI Analysis")
        lines.append("")

        for region in result['ai_regions'][:30]:  # 限制数量
            lines.append(f"### {region['file']}:{region['line']} ({region['type']})")
            lines.append(f"{region['description']}")
            lines.append("")
            lines.append("```c")
            lines.append(region['context'])
            lines.append("```")
            lines.append("")

        return "\n".join(lines)

    def to_json(self, result: Dict[str, Any]) -> str:
        """生成 JSON 报告"""
        return json.dumps(result, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description="C 语言安全审计工具 - 支持代码检查和 AI 检查两种模式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # Level 1: 代码检查（快速扫描）
    python audit.py --target ./src --mode code

    # Level 2: 准备 AI 分析数据
    python audit.py --target ./src --mode code --format ai

    # JSON 输出
    python audit.py --target ./src --mode code --format json

模式说明:
    code - Level 1 代码检查：使用正则匹配明确的安全问题
    ai   - Level 2 AI 检查：输出供 AI 深度分析的上下文
        """
    )
    parser.add_argument(
        "--target",
        required=True,
        help="目标文件或目录"
    )
    parser.add_argument(
        "--mode",
        choices=["code", "ai", "both"],
        default="code",
        help="审计模式（默认: code）"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "ai"],
        default="markdown",
        help="输出格式（默认: markdown）"
    )
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f"Error: Target not found: {target}")
        return 1

    print(f"正在扫描 C 代码: {target} (mode: {args.mode})...")

    auditor = CSecurityAuditor(target)
    result = auditor.scan(mode=args.mode)

    if args.format == "json":
        print(auditor.to_json(result))
    elif args.format == "ai":
        print(auditor.to_ai_format(result))
    else:
        print(auditor.to_markdown(result))

    return 0


if __name__ == "__main__":
    exit(main())
