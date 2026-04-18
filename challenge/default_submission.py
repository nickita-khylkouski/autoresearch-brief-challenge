from __future__ import annotations

from collections import defaultdict
from typing import Any


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "best",
    "for",
    "from",
    "how",
    "in",
    "is",
    "of",
    "on",
    "or",
    "should",
    "the",
    "to",
    "under",
    "what",
    "which",
    "with",
}


def _keyword_query(question: str) -> str:
    words = [word.strip(" ,.?").lower() for word in question.split()]
    keywords = [word for word in words if word and word not in STOPWORDS]
    return " ".join(keywords[:10]) or question


def _first_sentence(text: str) -> str:
    sentence = text.split(". ")[0].strip()
    if not sentence.endswith("."):
        sentence += "."
    return sentence


def run_task(*, task: dict[str, Any], tools: Any, config: dict[str, Any]) -> dict[str, Any]:
    retrieval = config.get("retrieval", {})
    top_k = int(retrieval.get("top_k", 6))
    rerank_top_n = int(retrieval.get("rerank_top_n", 4))
    citation_count = int(config.get("citation_count", 3))

    queries = [
        task["question"],
        _keyword_query(task["question"]),
    ]
    if task.get("task_type") == "comparison":
        queries.append(f"{task['question']} method evidence limitation")
    elif task.get("task_type") == "constraint_selection":
        queries.append(f"{task['question']} budget latency tradeoff")
    elif task.get("task_type") == "verification":
        queries.append(f"{task['question']} citation evidence support")

    seen_chunks: dict[str, dict[str, Any]] = {}
    source_votes: dict[str, float] = defaultdict(float)
    for query in queries[:3]:
        for hit in tools.search(query, top_k=top_k):
            seen_chunks.setdefault(hit["chunk_id"], hit)
            source_votes[hit["source_id"]] += hit["score"]

    ranked_hits = tools.rerank(task["question"], list(seen_chunks))
    selected_hits = []
    used_sources: set[str] = set()
    for hit in ranked_hits[: max(rerank_top_n, citation_count + 1)]:
        if hit["source_id"] in used_sources and len(selected_hits) >= citation_count:
            continue
        selected_hits.append(hit)
        used_sources.add(hit["source_id"])
        if len(selected_hits) >= citation_count:
            break

    chunk_ids = [hit["chunk_id"] for hit in selected_hits]
    chunks = tools.batch_get_chunks(chunk_ids)
    sentences = [_first_sentence(chunk["text"]) for chunk in chunks]
    answer = " ".join(sentences[:citation_count]).strip()
    if not answer:
        answer = "Insufficient evidence retrieved from the frozen corpus."
    notes = {
        "queries": queries[:3],
        "sources_considered": sorted(source_votes, key=source_votes.get, reverse=True)[:4],
    }
    return {
        "answer": answer,
        "citations": chunk_ids[:citation_count],
        "notes": notes,
    }
