"""
实验 3.Prompt: ChatPromptTemplate 核心价值演示
展示 Prompt 模板的两大能力：变量替换 和 LCEL 链式组装

ChatPromptTemplate 核心价值：
  1. 变量替换：替代手动 f-string，支持复用
  2. LCEL 链式组装：用管道符 | 组装 Prompt → LLM → Parser

架构图：
  ┌─────────────────────────────────────────────────────────────┐
  │                    LCEL 链式组装                            │
  │                                                             │
  │   Prompt          LLM           Parser                     │
  │ ┌──────────┐   ┌──────────┐   ┌──────────┐                │
  │ │ 模板+变量 │──►│ 模型推理 │──►│ 输出解析 │──► 最终结果    │
  │ └──────────┘   └──────────┘   └──────────┘                │
  │                                                             │
  │ chain = prompt | llm | parser                              │
  │ chain.invoke({"变量": "值"})                               │
  └─────────────────────────────────────────────────────────────┘

对比手动实现：
  ┌──────────────────┬─────────────────────┬─────────────────────┐
  │      操作         │      手动实现        │     LangChain       │
  ├──────────────────┼─────────────────────┼─────────────────────┤
  │ 变量替换          │ f"你是{role}..."    │ template.invoke()   │
  │ 消息构建          │ 手动拼接列表        │ 自动生成 Message    │
  │ 调用模型          │ 单独调用            │ 链式调用            │
  │ 输出解析          │ 手动提取 content    │ StrOutputParser     │
  │ 组件替换          │ 改多处代码          │ 改一处配置          │
  └──────────────────┴─────────────────────┴─────────────────────┘
"""

# ==================== 导入 ====================
import os
from dotenv import load_dotenv

# LangChain 核心组件
from langchain_core.prompts import ChatPromptTemplate
# ChatPromptTemplate: 提示词模板类
# - from_messages(): 从消息列表创建模板
# - invoke(): 渲染模板（填充变量）
# - stream(): 流式渲染

from langchain_core.output_parsers import StrOutputParser
# StrOutputParser: 字符串输出解析器
# - 从 AIMessage 中提取 content 字段
# - 将复杂响应转为简单字符串

from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
# LLM 封装类

# ==================== 配置 ====================
load_dotenv()


# ============================================================
# LLM 工厂函数
# ============================================================

def get_llm(backend: str = "openai"):
    """
    获取 LLM 实例

    Args:
        backend: "ollama" 或 "openai"
    """
    if backend == "ollama":
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        return ChatOllama(model="qwen2.5:7b", base_url=ollama_host)
    elif backend == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "deepseek-v4-pro"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    raise ValueError(f"未知后端: {backend}")


# ============================================================
# 演示 1：变量替换
# ============================================================

def demo_variable_substitution():
    """
    演示 ChatPromptTemplate 的变量替换能力

    对比：
    - 手动拼接：prompt = f"你是{role}，请分析{target}的{vuln_type}漏洞"
    - 模板方式：用 {变量名} 占位，invoke 时自动填充

    模板的优势：
    1. 分离模板和数据
    2. 可复用（同一模板不同参数）
    3. 类型安全（LangChain 会验证变量）
    """
    print("=" * 60)
    print("演示 1: 变量替换")
    print("=" * 60)

    # 创建模板
    # from_messages() 接收消息列表
    # 每条消息是 (role, content) 元组
    # content 中的 {变量名} 会被替换
    template = ChatPromptTemplate.from_messages([
        ("system", "你是{role}，精通各类安全技术，请用简洁专业的语言回答"),
        ("user", "请简要分析 {target} 可能存在的 {vuln_type} 风险"),
    ])

    # 渲染模板 — 传入变量字典
    # invoke() 返回 ChatPromptValue 对象
    # .messages 属性包含渲染后的消息列表
    messages = template.invoke({
        "role": "网络安全专家",
        "target": "example.com",
        "vuln_type": "SQL注入",
    })

    print(f"\n渲染后的消息列表：")
    for msg in messages.messages:
        print(f"  [{msg.type}] {msg.content}")

    # 同一模板，不同参数 — 复用的价值
    messages2 = template.invoke({
        "role": "渗透测试工程师",
        "target": "192.168.1.1",
        "vuln_type": "SSRF",
    })

    print(f"\n同一模板不同参数：")
    for msg in messages2.messages:
        print(f"  [{msg.type}] {msg.content}")


# ============================================================
# 演示 2：LCEL 链式组装
# ============================================================

def demo_chain_assembly(backend: str = "openai"):
    """
    演示 LCEL (LangChain Expression Language) 链式组装

    LCEL 核心概念：
    - 所有组件都实现统一的 Runnable 接口
    - 可以用管道操作符 | 串联组件
    - 自动传递数据，无需手动处理

    链式组装的优势：
    1. 代码简洁：一行定义完整流程
    2. 统一接口：invoke / stream / batch
    3. 易于测试：每个组件可独立测试
    4. 灵活组合：随时替换组件

    Args:
        backend: LLM 后端
    """
    print("\n" + "=" * 60)
    print(f"演示 2: LCEL 链式组装（后端: {backend}）")
    print("=" * 60)

    llm = get_llm(backend)

    # 构建 Chain: Prompt → LLM → StrOutputParser
    # 管道操作符 | 会自动传递数据
    # 等效于：parser.invoke(llm.invoke(prompt.invoke(input)))
    chain = (
        ChatPromptTemplate.from_messages([
            ("system", "你是{role}，请用不超过3句话回答"),
            ("user", "什么是 {concept}？在安全领域有什么应用？"),
        ])
        | llm
        | StrOutputParser()
    )

    # ========== invoke 模式：全量返回 ==========
    # invoke() 会等待模型生成完整响应后返回
    print("\ninvoke 模式（全量返回）：")
    result = chain.invoke({"role": "安全专家", "concept": "零信任架构"})
    print(result)

    # ========== stream 模式：流式返回 ==========
    # stream() 返回迭代器，逐 token 获取
    # 用户体验更好（首字延迟低）
    print("\nstream 模式（流式返回）：")
    for chunk in chain.stream({"role": "安全专家", "concept": "蜜罐技术"}):
        print(chunk, end="", flush=True)
    print()

    # ========== batch 模式：批量执行 ==========
    # batch() 一次性执行多个输入
    # 比循环调用 invoke 更高效（可能并行）
    print("\nbatch 模式（批量执行）：")
    results = chain.batch([
        {"role": "安全专家", "concept": "WAF"},
        {"role": "安全专家", "concept": "IDS"},
    ])
    for i, r in enumerate(results):
        print(f"  [{i+1}] {r[:80]}...")


# ============================================================
# 演示 3：组件替换
# ============================================================

def demo_component_swap():
    """
    演示链式组装的灵活性：替换组件不影响其他部分

    核心价值：
    - 同一个 Prompt + Parser，可以随意切换 LLM
    - 切换模型只需改一行代码
    - 这就是"依赖注入"的思想
    """
    print("\n" + "=" * 60)
    print("演示 3: 组件替换的灵活性")
    print("=" * 60)

    # 定义 Prompt 和 Parser（与 LLM 无关）
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是{role}，用一句话回答"),
        ("user", "{question}"),
    ])
    parser = StrOutputParser()

    # 同一个 Prompt + Parser，可以随意切换 LLM
    for backend in ["openai", "ollama"]:
        try:
            llm = get_llm(backend)
            chain = prompt | llm | parser
            result = chain.invoke({"role": "安全顾问", "question": "什么是CVE？"})
            print(f"\n  [{backend}] {result}")
        except Exception as e:
            print(f"\n  [{backend}] 跳过：{e}")


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PromptTemplate 核心价值演示")
    parser.add_argument(
        "--backend",
        choices=["ollama", "openai"],
        default="openai"
    )
    parser.add_argument(
        "--demo",
        choices=["1", "2", "3", "all"],
        default="all",
        help="1=变量替换, 2=链式组装, 3=组件替换, all=全部"
    )
    args = parser.parse_args()

    if args.demo in ["1", "all"]:
        demo_variable_substitution()

    if args.demo in ["2", "all"]:
        demo_chain_assembly(args.backend)

    if args.demo in ["3", "all"]:
        demo_component_swap()