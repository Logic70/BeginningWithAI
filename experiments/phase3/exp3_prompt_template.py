"""
实验 3.Prompt: ChatPromptTemplate 核心价值演示
展示 Prompt 模板的两大能力：变量替换 和 LCEL 链式组装
"""
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

load_dotenv()


def get_llm(backend: str = "openai"):
    """获取 LLM 实例"""
    if backend == "ollama":
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        return ChatOllama(model="qwen2.5:7b", base_url=ollama_host)
    elif backend == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "qwen3.5-plus"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    raise ValueError(f"未知后端: {backend}")


# ===== 演示 1: 变量替换 — 替代手动 f-string =====

def demo_variable_substitution():
    """
    对比手动拼接 vs PromptTemplate：
    
    手动拼接：prompt = f"你是{role}，请分析{target}的{vuln_type}漏洞"
    模板方式：用 {变量名} 占位，invoke 时自动填充
    """
    print("=" * 60)
    print("演示 1: 变量替换")
    print("=" * 60)

    template = ChatPromptTemplate.from_messages([
        ("system", "你是{role}，精通各类安全技术，请用简洁专业的语言回答"),
        ("user", "请简要分析 {target} 可能存在的 {vuln_type} 风险"),
    ])

    # 渲染模板 — 传入变量字典，得到标准 Message 列表
    messages = template.invoke({
        "role": "网络安全专家",
        "target": "example.com",
        "vuln_type": "SQL注入",
    })

    print(f"\n📝 渲染后的消息列表：")
    for msg in messages.messages:
        print(f"  [{msg.type}] {msg.content}")

    # 同一模板，不同参数 — 复用的价值
    messages2 = template.stream({
        "role": "渗透测试工程师",
        "target": "192.168.1.1",
        "vuln_type": "SSRF",
    })

    print(f"\n📝 同一模板不同参数：")
    for msg in messages2.messages:
        print(f"  [{msg.type}] {msg.content}")


# ===== 演示 2: LCEL 链式组装 — Prompt | LLM | Parser =====

def demo_chain_assembly(backend: str = "openai"):
    """
    用管道操作符 | 将 Prompt + LLM + Parser 组装为调用链
    一行 invoke 即可完成「模板渲染 → 模型调用 → 输出解析」全流程
    """
    print("\n" + "=" * 60)
    print(f"演示 2: LCEL 链式组装（后端: {backend}）")
    print("=" * 60)

    llm = get_llm(backend)

    # 构建 Chain: Prompt → LLM → StrOutputParser
    chain = (
        ChatPromptTemplate.from_messages([
            ("system", "你是{role}，请用不超过3句话回答"),
            ("user", "什么是 {concept}？在安全领域有什么应用？"),
        ])
        | llm
        | StrOutputParser()
    )

    # invoke: 一次性全量返回
    print("\n🔹 invoke 模式（全量返回）：")
    result = chain.invoke({"role": "安全专家", "concept": "零信任架构"})
    print(result)

    # stream: 流式逐字返回
    print("\n🔹 stream 模式（流式返回）：")
    for chunk in chain.stream({"role": "安全专家", "concept": "蜜罐技术"}):
        print(chunk, end="", flush=True)
    print()

    # batch: 批量执行
    print("\n🔹 batch 模式（批量执行）：")
    results = chain.batch([
        {"role": "安全专家", "concept": "WAF"},
        {"role": "安全专家", "concept": "IDS"},
    ])
    for i, r in enumerate(results):
        print(f"  [{i+1}] {r[:80]}...")


# ===== 演示 3: 替换组件不影响其他部分 =====

def demo_component_swap():
    """
    展示链式组装的灵活性：替换 LLM 组件，其余代码不变
    """
    print("\n" + "=" * 60)
    print("演示 3: 组件替换的灵活性")
    print("=" * 60)

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


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PromptTemplate 核心价值演示")
    parser.add_argument("--backend", choices=["ollama", "openai"], default="openai")
    parser.add_argument("--demo", choices=["1", "2", "3", "all"], default="all",
                        help="1=变量替换, 2=链式组装, 3=组件替换, all=全部")
    args = parser.parse_args()

    if args.demo in ["1", "all"]:
        demo_variable_substitution()

    if args.demo in ["2", "all"]:
        demo_chain_assembly(args.backend)

    if args.demo in ["3", "all"]:
        demo_component_swap()
