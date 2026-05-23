# 阶段二：RAG、模型微调与后训练

> 预计时间：3-4 周 | 核心问题：如何让模型利用外部知识，并在特定任务上表现得更专业？

---

## 🎯 阶段目标

完成本阶段后，你将能够：
- ✅ 理解 RAG 的基本链路：切块、检索、上下文组装、生成
- ✅ 构建一个面向安全知识库的最小 RAG 问答原型
- ✅ 判断 RAG、微调、Agent 工具调用分别适合解决什么问题
- ✅ 理解 LoRA/QLoRA 微调原理
- ✅ 准备和格式化训练数据集
- ✅ 使用 Unsloth 进行高效微调
- ✅ 评估和部署微调后的模型

---

## 📖 RAG 与微调核心概念

### 为什么阶段二要同时学习 RAG 和微调？

阶段二的核心不是“只会训练模型”，而是学会让模型在安全领域更可靠。常见有两条路线：

- **RAG**：不改模型参数，把外部知识检索出来放进上下文，让模型基于资料回答。
- **微调**：改模型的部分参数，让模型学会更稳定的输出风格、任务格式和领域表达。

两者不是替代关系，而是互补关系。

| 场景 | 优先选择 | 原因 |
|------|----------|------|
| 知识频繁更新，例如 CVE、厂商公告、内部规范 | RAG | 更新知识库比重新训练模型更快 |
| 需要引用来源、保留证据链 | RAG | 可以把检索到的文档片段作为回答依据 |
| 模型回答格式不稳定 | 微调 | 让模型学习固定输出结构 |
| 需要领域语气、术语、分类标准 | 微调 | 让模型形成稳定表达习惯 |
| 需要调用扫描器、读文件、执行命令 | Agent / Tool | 这是执行能力，不是 RAG 或微调本身 |

一句话判断：

> 知识问题先用 RAG，行为和格式问题再考虑微调，需要执行外部动作时进入 Agent。

### RAG 最小链路

```text
原始文档
  -> 文档切块 chunking
  -> 向量化 embedding
  -> 相似度检索 retrieval
  -> 组装上下文 context
  -> 模型基于上下文回答 generation
```

RAG 的关键不是“把文档全部塞给模型”，而是只把和问题最相关的片段放进上下文。

本项目先用一个最小可运行版本理解链路：

- 用公开安全知识学习材料作为文档源。
- 用本地词袋向量模拟 embedding，避免一开始依赖向量数据库。
- 用余弦相似度做 Top-K 检索。
- 默认只输出检索上下文和本地摘要，避免消耗 API 额度。
- 可选 `--backend openai` 再调用 OpenAI 兼容接口生成答案。

### 阶段二 RAG 学习路线

RAG 重新加入阶段二，但不和微调混在一起讲。推荐顺序是：

```text
2.0a 公开数据 RAG 练习
  -> 2.0b WorkflowProgram 项目知识 RAG for Claude Code
  -> 2.1 LoRA 原理
  -> 2.2 Unsloth 环境
  -> 2.3-2.9 微调、评估、部署
```

### 实践边界说明

下面这些内容是当前仓库里可以直接实践的：

| 内容 | 当前状态 | 说明 |
|------|----------|------|
| 2.0a 公开数据本地 RAG 检索 | 已验证可运行 | 不依赖 GPU，不调用模型 |
| 2.0a OpenAI 兼容模型生成 | 已验证可运行 | 需要使用项目虚拟环境和 `.env` |
| 2.0b 本地目录 RAG 上下文包生成 | 已验证可运行 | 已用 `docs` 目录模拟 WorkflowProgram 源路径 |
| 2.0b 真实 WorkflowProgram RAG | 需要外部路径 | 当前仓库没有 WorkflowProgram 源码，拿到路径后用 `--source-root` 接入 |
| 生产级向量库 / Embedding 模型 | 暂不包含 | 本阶段先学 RAG 机制，后续可替换为 Chroma、FAISS 或 pgvector |

所以这部分是可实践的，但要明确：当前实现是**教学级最小 RAG**，不是生产级知识库系统。

#### 2.0a：公开数据 RAG 练习

对应文件：

- 代码：[D:\Code\BeginningWithAI\experiments\phase2\exp2_0_public_rag_practice.py](D:/Code/BeginningWithAI/experiments/phase2/exp2_0_public_rag_practice.py)
- 数据：[D:\Code\BeginningWithAI\data\rag\public_security_corpus.jsonl](D:/Code/BeginningWithAI/data/rag/public_security_corpus.jsonl)

这个实验使用公开安全知识主题作为练习材料，包括 OWASP、NIST、MITRE ATT&CK、CISA KEV 等公开资料对应的原创摘要。这样做的目的不是训练安全专家模型，而是先把 RAG 链路跑通。

运行方式：

```bash
./venv/bin/python experiments/phase2/exp2_0_public_rag_practice.py --query SQL注入
./venv/bin/python experiments/phase2/exp2_0_public_rag_practice.py --query 零信任
./venv/bin/python experiments/phase2/exp2_0_public_rag_practice.py --query 已知被利用漏洞 --backend openai
```

学习重点：

- `load_corpus()`：读取 JSONL 文档。
- `chunk_documents()`：把文档切成 chunk。
- `tokenize()` / `vectorize()`：把文本转换成可检索表示。
- `retrieve()`：计算相似度并选 Top-K。
- `build_context()`：把检索结果组装成模型上下文。

#### 2.0b：WorkflowProgram 项目知识 RAG for Claude Code

对应文件：

- [D:\Code\BeginningWithAI\experiments\phase2\exp2_0b_workflowprogram_rag_for_claudecode.py](D:/Code/BeginningWithAI/experiments/phase2/exp2_0b_workflowprogram_rag_for_claudecode.py)

这个实验是阶段二 RAG 的最终目标：把 WorkflowProgram 的体系知识变成 Claude Code 可引用的 RAG 上下文包。

它不假设 WorkflowProgram 在当前仓库里。等你有 WorkflowProgram 的本地路径后，传入 `--source-root` 即可：

```bash
./venv/bin/python experiments/phase2/exp2_0b_workflowprogram_rag_for_claudecode.py \
  --source-root D:/Code/WorkflowProgram \
  --query "WorkflowProgram 的核心对象模型是什么？" \
  --export data/rag/workflowprogram_claude_context.md
```

生成的文件可以在 Claude Code 里作为上下文引用：

```text
请基于 @data/rag/workflowprogram_claude_context.md 中的证据回答：
WorkflowProgram 的核心对象模型是什么？
如果证据不足，请明确说明缺少哪类文件，不要编造实现。
```

生成的 `data/rag/*_claude_context.md` 已加入 `.gitignore`。原因是 WorkflowProgram 的检索上下文未来可能包含私有项目知识，不应该默认提交到公开仓库。

在 WorkflowProgram 路径还没有接入前，可以先用本项目文档验证机制：

```bash
./venv/bin/python experiments/phase2/exp2_0b_workflowprogram_rag_for_claudecode.py \
  --source-root docs \
  --query "Subagent Runtime 和 Agent Team 有什么区别？" \
  --export data/rag/workflowprogram_claude_context.md
```

学习重点：

- 面向 code agent 的 RAG 不只是“回答知识问题”，还要保留文件路径、行号和证据片段。
- Claude Code 侧不需要先实现复杂向量数据库；第一版可以通过 `@file` 引入检索后的上下文包。
- 最终目标是让 Claude Code 基于 WorkflowProgram 的真实体系知识回答，而不是凭模型记忆编造。

### 为什么需要微调？

| 场景 | RAG | 微调 |
|------|-----|------|
| 知识更新频繁 | ✅ 适合 | ❌ 不适合 |
| 特定输出风格 | ❌ 不适合 | ✅ 适合 |
| 领域术语理解 | 一般 | ✅ 优秀 |
| 复杂推理任务 | 一般 | ✅ 优秀 |

补充说明：

- 表里的“RAG 一般”不是说 RAG 没价值，而是说 RAG 主要负责提供事实依据，不负责改变模型能力边界。
- 如果模型本身不会做某类推理，单纯检索资料不一定能解决。
- 如果只是知识缺失，不应该优先微调。

### LoRA 原理

**LoRA (Low-Rank Adaptation)** 是一种参数高效微调技术。

核心思想：不修改原始模型权重，而是添加小型可训练矩阵。

```
原始权重: W (4096 × 4096)
LoRA: W + ΔW = W + A × B
其中: A (4096 × r), B (r × 4096), r << 4096 (如 r=8)
```

优势：
- 只需训练约 0.1%-1% 的参数
- 显存占用低（16GB GPU 可微调 7B 模型）
- 可快速切换不同微调版本

---

## 📦 环境准备

### RAG 实验环境

RAG 的 `2.0a / 2.0b` 实验不需要 GPU，也不需要 Unsloth。默认只使用 Python 标准库即可运行。

#### 运行位置

所有阶段二命令都建议从项目根目录运行：

```bash
cd /mnt/d/Code/BeginningWithAI
```

不要从 `experiments/phase2/` 子目录里直接运行。原因是实验代码会按项目根目录查找 `data/rag/`、`.env` 和导出路径。

#### Python 环境

优先使用项目虚拟环境：

```bash
./venv/bin/python --version
./venv/bin/python experiments/phase2/exp2_0_public_rag_practice.py --query SQL注入
```

如果 `./venv/bin/python` 不存在，再使用系统 `python3`。但注意：系统 `python3` 只能运行不调用模型的本地检索模式；`--backend openai` 需要安装 `openai` 包。

#### 实验前检查

运行 RAG 前先执行：

```bash
# 1. 确认公开练习数据存在
test -f data/rag/public_security_corpus.jsonl

# 2. 确认两个 RAG 脚本语法正确
./venv/bin/python -m py_compile \
  experiments/phase2/exp2_0_public_rag_practice.py \
  experiments/phase2/exp2_0b_workflowprogram_rag_for_claudecode.py

# 3. 跑一个不消耗模型额度的本地检索
./venv/bin/python experiments/phase2/exp2_0_public_rag_practice.py --query SQL注入
```

#### OpenAI 兼容模型准备

如果要让 `2.0a` 在检索后调用 OpenAI 兼容模型生成答案，需要已有 `.env`，并使用安装了 `openai` 包的项目虚拟环境：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://opencode.ai/zen/go/v1
OPENAI_MODEL=deepseek-v4-pro
```

验证命令：

```bash
./venv/bin/python experiments/phase2/exp2_0_public_rag_practice.py --query SQL注入 --backend openai
```

不加 `--backend openai` 时不会消耗模型额度。

#### WorkflowProgram 路径准备

`2.0b` 的最终目标是索引 WorkflowProgram 的体系知识，但当前仓库不包含 WorkflowProgram 源码。因此真实实验前需要准备一个本地路径，例如：

```text
D:/Code/WorkflowProgram
```

在 WSL 中对应路径是：

```text
/mnt/d/Code/WorkflowProgram
```

如果暂时没有 WorkflowProgram 路径，可以先用本项目 `docs` 目录模拟：

```bash
./venv/bin/python experiments/phase2/exp2_0b_workflowprogram_rag_for_claudecode.py \
  --source-root docs \
  --query Subagent \
  --export /tmp/workflowprogram_claude_context.md
```

真实 WorkflowProgram 接入后再运行：

```bash
./venv/bin/python experiments/phase2/exp2_0b_workflowprogram_rag_for_claudecode.py \
  --source-root /mnt/d/Code/WorkflowProgram \
  --query "WorkflowProgram 的核心对象模型是什么？" \
  --export data/rag/workflowprogram_claude_context.md
```

`data/rag/*_claude_context.md` 已加入 `.gitignore`，避免把项目私有知识上下文误提交。

### 硬件要求
- **最低**: 16GB VRAM GPU (RTX 4060 Ti / RTX 3090)
- **推荐**: 24GB+ VRAM GPU (RTX 4090 / A100)

### 安装 Unsloth

```powershell
# 创建新的虚拟环境（推荐）
python -m venv venv_finetune
.\venv_finetune\Scripts\activate

# 安装 PyTorch (CUDA 12.1)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 安装 Unsloth
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps trl peft accelerate bitsandbytes
```

### 验证安装
```python
import torch
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
```

---

## 🧪 实验 2.1：理解 LoRA 原理

### 目标
通过代码理解 LoRA 的工作原理。

### 代码示例

创建文件 `experiments/phase2/exp2_1_lora_principle.py`：

```python
"""
实验 2.1: LoRA 原理可视化
"""
import torch
import torch.nn as nn


class LoRALayer(nn.Module):
    """简化的 LoRA 层实现"""
    
    def __init__(self, in_features: int, out_features: int, rank: int = 8):
        super().__init__()
        
        # 原始权重（冻结）
        self.W = nn.Linear(in_features, out_features, bias=False)
        self.W.weight.requires_grad = False
        
        # LoRA 矩阵（可训练）
        self.lora_A = nn.Linear(in_features, rank, bias=False)
        self.lora_B = nn.Linear(rank, out_features, bias=False)
        
        # 缩放因子
        self.scaling = 0.01
        
        # 初始化
        nn.init.kaiming_uniform_(self.lora_A.weight)
        nn.init.zeros_(self.lora_B.weight)
    
    def forward(self, x):
        # 原始路径 + LoRA 路径
        original = self.W(x)
        lora = self.lora_B(self.lora_A(x)) * self.scaling
        return original + lora


def count_parameters(model):
    """统计可训练参数数量"""
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    return trainable, total


# 演示
print("=== LoRA 参数效率演示 ===\n")

# 模拟 Transformer 层的维度
hidden_size = 4096
rank = 8

# 创建 LoRA 层
lora_layer = LoRALayer(hidden_size, hidden_size, rank=rank)

trainable, total = count_parameters(lora_layer)
print(f"隐藏层维度: {hidden_size}")
print(f"LoRA Rank: {rank}")
print(f"总参数量: {total:,}")
print(f"可训练参数: {trainable:,}")
print(f"参数效率: {trainable/total*100:.2f}%")

# 前向传播测试
x = torch.randn(1, 128, hidden_size)  # [batch, seq_len, hidden]
y = lora_layer(x)
print(f"\n输入形状: {x.shape}")
print(f"输出形状: {y.shape}")
```

### 验证标准
- [ ] 理解 LoRA 矩阵分解原理
- [ ] 理解参数效率的计算方式
- [ ] 理解为什么 LoRA 能减少显存

---

## 🧪 实验 2.2：Unsloth 环境验证

### 目标
验证微调环境配置正确，加载模型成功。

### 代码示例

创建文件 `experiments/phase2/exp2_2_unsloth_setup.py`：

```python
"""
实验 2.2: Unsloth 环境验证
"""
from unsloth import FastLanguageModel
import torch

# 配置
max_seq_length = 2048
dtype = None  # 自动检测
load_in_4bit = True  # 使用 4bit 量化加载

# 加载模型
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen2.5-7B",
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
)

print(f"模型加载成功!")
print(f"模型类型: {type(model)}")
print(f"设备: {next(model.parameters()).device}")

# 添加 LoRA 适配器
model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # LoRA rank
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",  # 节省显存
)

# 统计参数
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
total = sum(p.numel() for p in model.parameters())
print(f"\n可训练参数: {trainable:,} ({trainable/total*100:.2f}%)")

# 简单推理测试
FastLanguageModel.for_inference(model)
inputs = tokenizer("你好，请介绍一下SQL注入漏洞", return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=100)
print(f"\n测试生成:\n{tokenizer.decode(outputs[0], skip_special_tokens=True)}")
```

### 验证标准
- [ ] 模型加载无报错
- [ ] LoRA 适配器添加成功
- [ ] 可训练参数比例约 1%
- [ ] 推理测试成功

---

## 🧪 实验 2.3-2.4：数据集准备

### 目标
创建安全领域的微调数据集。

### 数据格式

**Alpaca 格式**（推荐）:
```json
{
  "instruction": "解释什么是SQL注入漏洞",
  "input": "",
  "output": "SQL注入是一种代码注入技术..."
}
```

**ShareGPT 格式**（多轮对话）:
```json
{
  "conversations": [
    {"from": "human", "value": "什么是SQL注入？"},
    {"from": "gpt", "value": "SQL注入是一种常见的Web安全漏洞..."},
    {"from": "human", "value": "如何防护？"},
    {"from": "gpt", "value": "可以采用以下防护措施..."}
  ]
}
```

### 代码示例

创建文件 `experiments/phase2/exp2_3_data_preparation.py`：

```python
"""
实验 2.3-2.4: 安全领域数据集准备
"""
import json
from pathlib import Path


def create_security_dataset():
    """创建安全问答数据集"""
    
    # 示例数据 - 实际应用中需要更多数据（建议 1000+ 条）
    dataset = [
        {
            "instruction": "请解释什么是SQL注入攻击",
            "input": "",
            "output": """SQL注入（SQL Injection）是一种代码注入攻击技术，攻击者通过在应用程序的输入字段中插入恶意SQL代码，来操纵后端数据库查询。

主要危害：
1. 数据泄露：窃取敏感信息
2. 数据篡改：修改或删除数据  
3. 权限提升：获取管理员权限
4. 系统控制：执行系统命令

防护措施：
1. 使用参数化查询（PreparedStatement）
2. 输入验证和过滤
3. 最小权限原则
4. 使用WAF"""
        },
        {
            "instruction": "分析以下代码是否存在安全漏洞",
            "input": "query = f\"SELECT * FROM users WHERE id = {user_id}\"",
            "output": """这段代码存在严重的SQL注入漏洞。

问题分析：
- 使用 f-string 字符串拼接构建SQL查询
- user_id 直接来自用户输入，未经验证
- 攻击者可输入如 "1 OR 1=1" 来获取所有用户数据

修复建议：
```python
# 使用参数化查询
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```"""
        },
        {
            "instruction": "请解释XSS跨站脚本攻击的类型和防护方法",
            "input": "",
            "output": """XSS（Cross-Site Scripting）跨站脚本攻击是一种注入攻击，攻击者在网页中注入恶意脚本代码。

三种主要类型：

1. 存储型XSS
   - 恶意脚本存储在服务器数据库
   - 每次用户访问时执行
   - 危害最大

2. 反射型XSS
   - 恶意脚本在URL参数中
   - 需要诱导用户点击链接
   - 一次性攻击

3. DOM型XSS
   - 在客户端JavaScript中利用
   - 不经过服务器
   - 难以检测

防护措施：
1. 输出编码（HTML实体转义）
2. 设置 Content-Security-Policy 头
3. 使用 HttpOnly Cookie
4. 输入验证和过滤"""
        },
        # 添加更多数据...
    ]
    
    return dataset


def format_for_training(dataset, output_path: str):
    """格式化为训练格式"""
    
    # Alpaca 格式模板
    template = """### Instruction:
{instruction}

### Input:
{input}

### Response:
{output}"""
    
    formatted = []
    for item in dataset:
        text = template.format(
            instruction=item["instruction"],
            input=item.get("input", ""),
            output=item["output"]
        )
        formatted.append({"text": text})
    
    # 保存数据集
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(formatted, f, ensure_ascii=False, indent=2)
    
    print(f"数据集已保存: {output_path}")
    print(f"样本数量: {len(formatted)}")
    
    return formatted


if __name__ == "__main__":
    # 创建数据集
    dataset = create_security_dataset()
    
    # 格式化并保存
    formatted = format_for_training(
        dataset,
        "../../data/processed/security_qa_dataset.json"
    )
    
    # 显示示例
    print("\n=== 数据样例 ===")
    print(formatted[0]["text"][:500])
```

### 数据收集建议

| 来源 | 数据类型 | 数量建议 |
|------|----------|----------|
| 安全博客 | 技术解释 | 200+ |
| CTF Writeups | 实战分析 | 100+ |
| CVE 描述 | 漏洞说明 | 300+ |
| 安全问答 | 问答对 | 400+ |

### 验证标准
- [ ] 数据集格式正确
- [ ] 至少包含 100 个样本（演示用）
- [ ] 数据覆盖多种安全话题
- [ ] 回答质量符合预期

---

## 🧪 实验 2.5-2.6：LoRA 微调实践

### 目标
使用 Unsloth 进行安全问答模型微调。

### 代码示例

创建文件 `experiments/phase2/exp2_5_finetune.py`：

```python
"""
实验 2.5-2.6: LoRA 微调安全问答模型
"""
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
import torch

# ========== 配置 ==========
MODEL_NAME = "unsloth/Qwen2.5-7B"
DATASET_PATH = "../../data/processed/security_qa_dataset.json"
OUTPUT_DIR = "../../models/finetuned/security-qa-lora"

MAX_SEQ_LENGTH = 2048
BATCH_SIZE = 2
GRADIENT_ACCUMULATION = 4
EPOCHS = 3
LEARNING_RATE = 2e-4

# ========== 加载模型 ==========
print("加载模型...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=None,
    load_in_4bit=True,
)

# ========== 添加 LoRA ==========
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
)

# ========== 加载数据集 ==========
print("加载数据集...")
dataset = load_dataset("json", data_files=DATASET_PATH, split="train")
print(f"数据集大小: {len(dataset)}")

# ========== 训练配置 ==========
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRADIENT_ACCUMULATION,
    warmup_steps=10,
    num_train_epochs=EPOCHS,
    learning_rate=LEARNING_RATE,
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    logging_steps=10,
    save_steps=100,
    save_total_limit=2,
    optim="adamw_8bit",
)

# ========== 训练 ==========
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    args=training_args,
)

print("开始训练...")
trainer.train()

# ========== 保存模型 ==========
print("保存模型...")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"训练完成! 模型保存至: {OUTPUT_DIR}")
```

### 运行训练
```powershell
cd experiments/phase2
python exp2_5_finetune.py
```

### 监控训练
- 观察 loss 是否稳定下降
- 监控 GPU 显存使用
- 检查 checkpoint 保存

---

## 🧪 实验 2.7：模型评估

### 目标
对比微调前后的模型效果。

### 代码示例

创建文件 `experiments/phase2/exp2_7_evaluation.py`：

```python
"""
实验 2.7: 模型评估对比
"""
from unsloth import FastLanguageModel
import torch

def load_model(model_path, is_finetuned=False):
    """加载模型"""
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_path,
        max_seq_length=2048,
        load_in_4bit=True,
    )
    FastLanguageModel.for_inference(model)
    return model, tokenizer


def generate_response(model, tokenizer, prompt):
    """生成回复"""
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.7,
        do_sample=True,
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


# 测试问题
test_questions = [
    "### Instruction:\n请解释什么是缓冲区溢出漏洞\n\n### Response:\n",
    "### Instruction:\n分析SQL注入攻击的防护措施\n\n### Response:\n",
    "### Instruction:\n什么是CSRF攻击？如何防护？\n\n### Response:\n",
]

# 加载原始模型
print("=== 原始模型 ===")
base_model, base_tokenizer = load_model("unsloth/Qwen2.5-7B")

# 加载微调模型
print("\n=== 微调模型 ===")
ft_model, ft_tokenizer = load_model("../../models/finetuned/security-qa-lora")

# 对比测试
for q in test_questions:
    print(f"\n{'='*60}")
    print(f"问题: {q[:50]}...")
    
    print("\n[原始模型回答]")
    print(generate_response(base_model, base_tokenizer, q))
    
    print("\n[微调模型回答]")
    print(generate_response(ft_model, ft_tokenizer, q))
```

### 评估维度
- [ ] 回答的专业程度
- [ ] 安全术语使用准确性
- [ ] 回答的结构化程度
- [ ] 是否存在幻觉

---

## 🧪 实验 2.8-2.9：量化与部署

### 目标
将微调模型量化导出并部署到 Ollama。

### 导出 GGUF 格式

```python
"""
实验 2.8: GGUF 量化导出
"""
from unsloth import FastLanguageModel

# 加载微调后的模型
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="../../models/finetuned/security-qa-lora",
    max_seq_length=2048,
    load_in_4bit=True,
)

# 保存为 GGUF 格式（多种量化等级）
model.save_pretrained_gguf(
    "../../models/finetuned/security-qa-gguf",
    tokenizer,
    quantization_method="q4_k_m"  # 4-bit 量化
)
```

### 部署到 Ollama

1. 创建 Modelfile：
```dockerfile
# Modelfile
FROM ./security-qa-q4_k_m.gguf

PARAMETER temperature 0.7
PARAMETER stop "### Instruction:"

SYSTEM """你是一个专业的网络安全顾问。请用专业、准确的语言回答安全相关问题。"""
```

2. 创建模型：
```powershell
cd models/finetuned/security-qa-gguf
ollama create security-qa -f Modelfile
```

3. 运行测试：
```powershell
ollama run security-qa "什么是SQL注入？"
```

---

## ✅ 阶段检查清单

| 检查项 | 状态 |
|--------|------|
| 理解 RAG 与微调的边界 | ⬜ |
| 公开数据 RAG 检索链路跑通 | ⬜ |
| WorkflowProgram RAG 上下文包能生成 | ⬜ |
| 理解 LoRA 原理 | ⬜ |
| Unsloth 环境配置成功 | ⬜ |
| 数据集准备完成 | ⬜ |
| 微调训练成功运行 | ⬜ |
| 模型评估对比完成 | ⬜ |
| GGUF 量化导出成功 | ⬜ |
| Ollama 部署成功 | ⬜ |

---

## 🚀 下一步

完成阶段二后，进入 [阶段三：Agent/MCP/Skill 开发](phase3_agent.md)
