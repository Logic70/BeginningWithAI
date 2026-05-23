"""
Experiment 2.0a: public-data RAG practice.

Goal:
  Learn the minimal RAG loop before fine-tuning:
    documents -> chunks -> retrieval -> context -> answer.

This script intentionally has a dependency-free retrieval backend. It uses a
simple bag-of-words vectorizer so the RAG mechanics are visible and runnable
without a vector database.

Run:
  ./venv/bin/python experiments/phase2/exp2_0_public_rag_practice.py --query SQL注入
  ./venv/bin/python experiments/phase2/exp2_0_public_rag_practice.py --query 零信任 --backend openai
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CORPUS = PROJECT_ROOT / "data" / "rag" / "public_security_corpus.jsonl"


@dataclass
class Document:
    doc_id: str
    title: str
    source: str
    url: str
    text: str


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    source: str
    url: str
    text: str


@dataclass
class ScoredChunk:
    chunk: Chunk
    score: float


def load_env_file(path: Path) -> None:
    """Load .env values without requiring python-dotenv."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_corpus(path: Path) -> list[Document]:
    documents: list[Document] = []
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            item = json.loads(line)
            documents.append(
                Document(
                    doc_id=item.get("id", f"line-{line_number}"),
                    title=item.get("title", ""),
                    source=item.get("source", ""),
                    url=item.get("url", ""),
                    text=item["text"],
                )
            )
    return documents


def chunk_documents(documents: Iterable[Document], chunk_size: int, overlap: int) -> list[Chunk]:
    chunks: list[Chunk] = []
    for document in documents:
        text = document.text.strip()
        start = 0
        chunk_index = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    Chunk(
                        chunk_id=f"{document.doc_id}#{chunk_index}",
                        doc_id=document.doc_id,
                        title=document.title,
                        source=document.source,
                        url=document.url,
                        text=chunk_text,
                    )
                )
            if end == len(text):
                break
            start = max(0, end - overlap)
            chunk_index += 1
    return chunks


def tokenize(text: str) -> list[str]:
    """Tokenize English words and Chinese characters for a tiny local retriever."""
    return [token.lower() for token in re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9_+-]+", text)]


def vectorize(text: str) -> Counter[str]:
    return Counter(tokenize(text))


def cosine_similarity(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    dot = sum(value * right.get(key, 0) for key, value in left.items())
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def retrieve(query: str, chunks: list[Chunk], top_k: int) -> list[ScoredChunk]:
    query_vector = vectorize(query)
    scored = [
        ScoredChunk(chunk=chunk, score=cosine_similarity(query_vector, vectorize(chunk.text)))
        for chunk in chunks
    ]
    scored.sort(key=lambda item: item.score, reverse=True)
    return [item for item in scored[:top_k] if item.score > 0]


def build_context(results: list[ScoredChunk]) -> str:
    parts = []
    for index, result in enumerate(results, start=1):
        chunk = result.chunk
        parts.append(
            "\n".join(
                [
                    f"[{index}] title: {chunk.title}",
                    f"source: {chunk.source}",
                    f"url: {chunk.url}",
                    f"score: {result.score:.4f}",
                    f"content: {chunk.text}",
                ]
            )
        )
    return "\n\n".join(parts)


def local_answer(query: str, results: list[ScoredChunk]) -> str:
    if not results:
        return "没有检索到足够相关的资料。请换一个更具体的问题。"
    best = results[0].chunk
    return (
        f"基于检索结果，最相关资料是《{best.title}》。\n"
        f"简要回答：{best.text}\n\n"
        "注意：这是本地检索摘要，不是模型生成答案。"
    )


def openai_answer(query: str, context: str) -> str:
    load_env_file(PROJECT_ROOT / ".env")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("OpenAI backend requires the openai package.") from exc

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )
    model = os.getenv("OPENAI_MODEL", "deepseek-v4-pro")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "你是安全知识库问答助手。只能基于给定 RAG 上下文回答；如果证据不足，要明确说明。",
            },
            {
                "role": "user",
                "content": f"问题：{query}\n\nRAG 上下文：\n{context}",
            },
        ],
    )
    return response.choices[0].message.content or ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Public corpus RAG practice")
    parser.add_argument("--query", default="How to defend against SQL injection?")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--chunk-size", type=int, default=420)
    parser.add_argument("--overlap", type=int, default=60)
    parser.add_argument("--backend", choices=["none", "openai"], default="none")
    args = parser.parse_args()

    documents = load_corpus(args.corpus)
    chunks = chunk_documents(documents, chunk_size=args.chunk_size, overlap=args.overlap)
    results = retrieve(args.query, chunks, top_k=args.top_k)
    context = build_context(results)

    print("=" * 60)
    print("Retrieved Context")
    print("=" * 60)
    print(context or "No relevant chunks found.")

    print("\n" + "=" * 60)
    print("Answer")
    print("=" * 60)
    if args.backend == "openai":
        print(openai_answer(args.query, context))
    else:
        print(local_answer(args.query, results))


if __name__ == "__main__":
    main()
