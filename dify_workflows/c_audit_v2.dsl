{
  "app": {
    "name": "C Code Security Auditor",
    "mode": "workflow",
    "icon": "🔒",
    "icon_background": "#FFE4E1",
    "description": "两级C代码安全审计工作流"
  },
  "version": "0.1.0",
  "graph": {
    "nodes": [
      {
        "id": "start",
        "type": "start",
        "position": {
          "x": 200,
          "y": 100
        },
        "data": {
          "type": "start",
          "title": "开始",
          "variables": [
            {
              "variable": "code_content",
              "type": "paragraph",
              "required": true,
              "label": "C代码内容"
            }
          ]
        }
      },
      {
        "id": "llm_1",
        "type": "llm",
        "position": {
          "x": 200,
          "y": 300
        },
        "data": {
          "type": "llm",
          "title": "Level 1 模式扫描",
          "model": {
            "provider": "openai",
            "name": "gpt-4",
            "mode": "chat",
            "temperature": 0.1
          },
          "prompt": "分析以下C代码的危险函数：\n{{#start.code_content#}}\n\n检查：strcpy, strcat, sprintf, gets, system等\n输出JSON格式发现的问题。"
        }
      },
      {
        "id": "llm_2",
        "type": "llm",
        "position": {
          "x": 500,
          "y": 300
        },
        "data": {
          "type": "llm",
          "title": "Level 2 深度分析",
          "model": {
            "provider": "openai",
            "name": "gpt-4",
            "mode": "chat",
            "temperature": 0.2
          },
          "prompt": "深度安全分析：\n{{#start.code_content#}}\n\n检查：命令注入、路径遍历、内存安全、逻辑错误\n输出详细的JSON格式报告。"
        }
      },
      {
        "id": "code_1",
        "type": "code",
        "position": {
          "x": 350,
          "y": 500
        },
        "data": {
          "type": "code",
          "title": "合并结果",
          "language": "python3",
          "code": "import json\n\nresult = {\n    'level1': '{{#llm_1.text#}}',\n    'level2': '{{#llm_2.text#}}',\n    'status': 'completed'\n}\n\nprint(json.dumps(result, ensure_ascii=False))"
        }
      },
      {
        "id": "llm_3",
        "type": "llm",
        "position": {
          "x": 350,
          "y": 700
        },
        "data": {
          "type": "llm",
          "title": "生成报告",
          "model": {
            "provider": "openai",
            "name": "gpt-4",
            "mode": "chat",
            "temperature": 0.3
          },
          "prompt": "基于以下结果生成审计报告：\n{{#code_1.result#}}\n\n格式：## C代码安全审计报告\n### 摘要\n### 发现问题\n### 修复建议"
        }
      },
      {
        "id": "end",
        "type": "end",
        "position": {
          "x": 350,
          "y": 900
        },
        "data": {
          "type": "end",
          "title": "结束",
          "outputs": [
            {
              "variable": "report",
              "type": "string",
              "value": "{{#llm_3.text#}}"
            }
          ]
        }
      }
    ],
    "edges": [
      {
        "source": "start",
        "target": "llm_1"
      },
      {
        "source": "start",
        "target": "llm_2"
      },
      {
        "source": "llm_1",
        "target": "code_1"
      },
      {
        "source": "llm_2",
        "target": "code_1"
      },
      {
        "source": "code_1",
        "target": "llm_3"
      },
      {
        "source": "llm_3",
        "target": "end"
      }
    ]
  }
}