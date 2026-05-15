{
  "app": {
    "name": "C Code Security Auditor",
    "mode": "workflow",
    "icon": "🔒",
    "icon_background": "#FFE4E1",
    "description": "两级C代码安全审计 - 支持文件上传、三分析器并行、SARIF导出"
  },
  "version": "0.1.0",
  "environment_variables": [],
  "conversation_variables": [],
  "workflow": {
    "nodes": [
      {
        "id": "start",
        "type": "start",
        "position": {
          "x": 100,
          "y": 100
        },
        "data": {
          "type": "start",
          "title": "开始",
          "variables": [
            {
              "variable": "input_type",
              "type": "select",
              "options": ["file", "code"],
              "default": "file",
              "label": "输入类型",
              "required": true
            },
            {
              "variable": "audit_level",
              "type": "select",
              "options": ["full", "level1", "level2"],
              "default": "full",
              "label": "审计级别",
              "required": true
            },
            {
              "variable": "code_text",
              "type": "paragraph",
              "label": "C代码（如选择粘贴代码）",
              "required": false
            }
          ]
        }
      },
      {
        "id": "file_upload",
        "type": "file-upload",
        "position": {
          "x": 100,
          "y": 250
        },
        "data": {
          "type": "file-upload",
          "title": "上传C代码文件",
          "allowed_file_types": ".c,.h",
          "max_file_size": 5,
          "multiple": true
        }
      },
      {
        "id": "input_merge",
        "type": "code",
        "position": {
          "x": 400,
          "y": 200
        },
        "data": {
          "type": "code",
          "title": "合并输入数据",
          "language": "python3",
          "code": "import json\n\nfiles = []\n\n# 处理文件上传\nfile_data = context.get('file_upload', {}).get('files', [])\nif file_data:\n    for f in file_data[:10]:  # 最多10个文件\n        files.append({\n            'name': f.get('name', 'unknown.c'),\n            'content': f.get('content', '')\n        })\n\n# 处理直接输入\ncode_text = context.get('start', {}).get('code_text', '')\nif code_text and not files:\n    files.append({\n        'name': 'input.c',\n        'content': code_text\n    })\n\noutput = {\n    'total_files': len(files),\n    'files': files\n}\n\nprint(json.dumps(output, ensure_ascii=False))"
        }
      },
      {
        "id": "pattern_scanner",
        "type": "llm",
        "position": {
          "x": 700,
          "y": 100
        },
        "data": {
          "type": "llm",
          "title": "Level 1 - 危险函数模式扫描",
          "model": {
            "provider": "openai",
            "name": "gpt-4",
            "mode": "chat",
            "temperature": 0.1
          },
          "prompt": "你是Level 1 C代码安全扫描器。使用模式匹配检测常见漏洞。\n\n## 分析文件\n{{#input_merge.result#}}\n\n## 检测模式\n- strcpy, strcat, sprintf → CWE-120\n- gets() → CWE-242 (Critical)\n- printf(user_input) → CWE-134\n- system(cmd) → CWE-78\n- scanf(\"%s\") without bounds → CWE-120\n- malloc without NULL check → CWE-252\n- printf with password/token keywords → CWE-532\n\n## 严重度\n- critical: gets(), unchecked strcpy with user input\n- high: strcpy/strcat/sprintf without size check, system()\n- medium: scanf(\"%s\"), fopen with user input\n- low: Information leak via debug print\n\n## 输出格式 (JSON数组)\n{\"level\":1,\"severity\":\"critical|high|medium|low\",\"file\":\"...\",\"line\":N,\"cwe\":\"CWE-XXX\",\"pattern\":\"...\",\"description\":\"...\",\"code_snippet\":\"...\",\"fix_suggestion\":\"...\"}\n\n如无问题输出: {\"level\":1,\"status\":\"no_issues\",\"message\":\"No Level 1 patterns detected.\"}"
        }
      },
      {
        "id": "security_analyzer",
        "type": "llm",
        "position": {
          "x": 700,
          "y": 300
        },
        "data": {
          "type": "llm",
          "title": "Level 2 - 安全分析器",
          "model": {
            "provider": "openai",
            "name": "gpt-4",
            "mode": "chat",
            "temperature": 0.2
          },
          "prompt": "你是C代码安全分析专家。\n\n## 分析文件\n{{#input_merge.result#}}\n\n## 分析焦点\n1. 污点分析: source→sink跟踪\n2. 命令注入: system/popen使用未净化输入\n3. 路径遍历: fopen/remove使用用户输入\n4. 硬编码凭证\n5. 弱加密\n6. 竞争条件\n\n## 输出格式 (JSON)\n{\"level\":2,\"severity\":\"critical|high|medium|low\",\"file\":\"...\",\"line\":N,\"cwe\":\"CWE-XXX\",\"category\":\"taint|injection|crypto|race|auth\",\"description\":\"...\",\"attack_scenario\":\"...\",\"suggestion\":\"...\"}\n\n如无问题: {\"level\":2,\"status\":\"no_issues\",\"agent\":\"security\"}"
        }
      },
      {
        "id": "memory_analyzer",
        "type": "llm",
        "position": {
          "x": 700,
          "y": 500
        },
        "data": {
          "type": "llm",
          "title": "Level 2 - 内存安全分析器",
          "model": {
            "provider": "openai",
            "name": "gpt-4",
            "mode": "chat",
            "temperature": 0.2
          },
          "prompt": "你是C代码内存安全专家。\n\n## 分析文件\n{{#input_merge.result#}}\n\n## 分析焦点\n1. Use-After-Free\n2. Double-Free\n3. 内存泄漏\n4. 缓冲区溢出\n5. 未初始化内存\n6. NULL指针解引用\n7. 整数溢出\n\n## 输出格式 (JSON)\n{\"level\":2,\"severity\":\"critical|high|medium|low\",\"file\":\"...\",\"line\":N,\"cwe\":\"CWE-XXX\",\"type\":\"uaf|double-free|leak|overflow\",\"description\":\"...\",\"suggestion\":\"...\"}\n\n如无问题: {\"level\":2,\"status\":\"no_issues\",\"agent\":\"memory\"}"
        }
      },
      {
        "id": "logic_analyzer",
        "type": "llm",
        "position": {
          "x": 700,
          "y": 700
        },
        "data": {
          "type": "llm",
          "title": "Level 2 - 逻辑分析器",
          "model": {
            "provider": "openai",
            "name": "gpt-4",
            "mode": "chat",
            "temperature": 0.2
          },
          "prompt": "你是C代码逻辑分析专家。\n\n## 分析文件\n{{#input_merge.result#}}\n\n## 分析焦点\n1. 竞争条件 (TOCTOU)\n2. Off-by-one错误\n3. 整数溢出\n4. API误用\n5. 死代码\n6. Switch缺少break\n7. 控制流问题\n\n## 输出格式 (JSON)\n{\"level\":2,\"severity\":\"high|medium|low\",\"file\":\"...\",\"line\":N,\"cwe\":\"CWE-XXX\",\"category\":\"logic|race|api-misuse|dead-code\",\"description\":\"...\",\"impact\":\"...\",\"suggestion\":\"...\"}\n\n如无问题: {\"level\":2,\"status\":\"no_issues\",\"agent\":\"logic\"}"
        }
      },
      {
        "id": "merge_results",
        "type": "code",
        "position": {
          "x": 1000,
          "y": 400
        },
        "data": {
          "type": "code",
          "title": "合并分析结果",
          "language": "python3",
          "code": "import json\nimport re\n\nall_findings = []\nseverity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}\n\ndef parse_findings(text):\n    findings = []\n    if not text:\n        return findings\n    # 提取JSON对象\n    matches = re.findall(r'{[^{}]+}', text)\n    for m in matches:\n        try:\n            obj = json.loads(m)\n            if 'status' in obj:\n                continue\n            if 'severity' in obj:\n                findings.append(obj)\n        except:\n            pass\n    return findings\n\n# 解析各分析器\nfor key in ['pattern_scanner', 'security_analyzer', 'memory_analyzer', 'logic_analyzer']:\n    text = context.get(key, {}).get('text', '')\n    all_findings.extend(parse_findings(text))\n\n# 去重\nseen = set()\nunique = []\nfor f in all_findings:\n    key = (f.get('file', ''), f.get('line', 0), f.get('description', '')[:30])\n    if key not in seen:\n        seen.add(key)\n        unique.append(f)\n\n# 排序\nunique.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 4))\n\n# 统计\nsummary = {\n    'total': len(unique),\n    'critical': sum(1 for f in unique if f.get('severity') == 'critical'),\n    'high': sum(1 for f in unique if f.get('severity') == 'high'),\n    'medium': sum(1 for f in unique if f.get('severity') == 'medium'),\n    'low': sum(1 for f in unique if f.get('severity') == 'low')\n}\n\n# 判决\nif summary['critical'] > 0:\n    verdict = 'CRITICAL_ISSUES'\nelif summary['high'] > 0:\n    verdict = 'NEEDS_WORK'\nelif summary['total'] == 0:\n    verdict = 'PASS'\nelse:\n    verdict = 'ACCEPTABLE'\n\noutput = {\n    'summary': summary,\n    'verdict': verdict,\n    'findings': unique[:50]  # 限制数量\n}\nprint(json.dumps(output, ensure_ascii=False))"
        }
      },
      {
        "id": "generate_report",
        "type": "llm",
        "position": {
          "x": 1300,
          "y": 300
        },
        "data": {
          "type": "llm",
          "title": "生成审计报告",
          "model": {
            "provider": "openai",
            "name": "gpt-4",
            "mode": "chat",
            "temperature": 0.3
          },
          "prompt": "生成C代码安全审计报告。\n\n## 数据\n{{#merge_results.result#}}\n\n## 报告格式\n# C代码安全审计报告\n\n## 摘要\n- 发现问题: {{summary.total}}\n- 严重: {{summary.critical}} | 高: {{summary.high}} | 中: {{summary.medium}} | 低: {{summary.low}}\n\n## 关键问题\n{{#findings}}{{#if severity == 'critical' or severity == 'high'}}\n### {{file}}:{{line}} ({{severity}}) - {{cwe}}\n- {{description}}\n- 修复: {{fix_suggestion}}\n{{/if}}{{/findings}}\n\n## 最终判决: {{verdict}}\n- CRITICAL_ISSUES: 必须立即修复\n- NEEDS_WORK: 发布前需修复\n- ACCEPTABLE: 可后续修复\n- PASS: 无问题"
        }
      },
      {
        "id": "end",
        "type": "end",
        "position": {
          "x": 1600,
          "y": 300
        },
        "data": {
          "type": "end",
          "title": "结束",
          "outputs": [
            {
              "variable": "report",
              "type": "string",
              "value": "{{#generate_report.text#}}"
            },
            {
              "variable": "summary",
              "type": "object",
              "value": "{{#merge_results.result.summary#}}"
            },
            {
              "variable": "verdict",
              "type": "string",
              "value": "{{#merge_results.result.verdict#}}"
            }
          ]
        }
      }
    ],
    "edges": [
      {
        "source": "start",
        "target": "file_upload"
      },
      {
        "source": "file_upload",
        "target": "input_merge"
      },
      {
        "source": "start",
        "target": "input_merge"
      },
      {
        "source": "input_merge",
        "target": "pattern_scanner"
      },
      {
        "source": "input_merge",
        "target": "security_analyzer"
      },
      {
        "source": "input_merge",
        "target": "memory_analyzer"
      },
      {
        "source": "input_merge",
        "target": "logic_analyzer"
      },
      {
        "source": "pattern_scanner",
        "target": "merge_results"
      },
      {
        "source": "security_analyzer",
        "target": "merge_results"
      },
      {
        "source": "memory_analyzer",
        "target": "merge_results"
      },
      {
        "source": "logic_analyzer",
        "target": "merge_results"
      },
      {
        "source": "merge_results",
        "target": "generate_report"
      },
      {
        "source": "generate_report",
        "target": "end"
      }
    ]
  },
  "environment_variables": [],
  "conversation_variables": [],
  "version": "0.1.0"
}