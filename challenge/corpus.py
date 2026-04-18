from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any

from .repository import load_corpus_pack
from .utils import safe_log_ratio, tokenize


@dataclass
class SearchHit:
    chunk_id: str
    source_id: str
    title: str
    section: str | None
    score: float
    text_preview: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "source_id": self.source_id,
            "title": self.title,
            "section": self.section,
            "score": round(self.score, 6),
            "text_preview": self.text_preview,
        }


class CorpusPack:
    def __init__(self, pack_id: str) -> None:
        payload = load_corpus_pack(pack_id)
        self.pack_id = pack_id
        self.sources = {item["source_id"]: item for item in payload["sources"]}
        self.chunks = {item["chunk_id"]: item for item in payload["chunks"]}
        self.postings = payload["index"]["postings"]
        self._chunk_tokens = {
            chunk_id: Counter(tokenize(item["text"]))
            for chunk_id, item in self.chunks.items()
        }
        self._title_tokens = {
            chunk_id: set(tokenize(item["title"]))
            for chunk_id, item in self.chunks.items()
        }
        self._section_tokens = {
            chunk_id: set(tokenize(item.get("section") or ""))
            for chunk_id, item in self.chunks.items()
        }

    def get_chunk(self, chunk_id: str) -> dict[str, Any]:
        return self.chunks[chunk_id]

    def list_sources(self, source_ids: list[str]) -> list[dict[str, Any]]:
        return [self.sources[source_id] for source_id in source_ids if source_id in self.sources]

    def search(self, query: str, top_k: int) -> list[SearchHit]:
        terms = tokenize(query)
        if not terms:
            return []
        section_weights = {
            "finding": 1.2,
            "recommendation": 1.12,
            "failure": 1.04,
            "setup": 0.96,
            "overview": 0.94,
        }
        scores: dict[str, float] = defaultdict(float)
        term_counts = Counter(terms)
        total_docs = len(self.chunks)
        for term, query_tf in term_counts.items():
            doc_ids = self.postings.get(term, [])
            if not doc_ids:
                continue
            idf = safe_log_ratio(total_docs, len(doc_ids))
            for chunk_id in doc_ids:
                chunk_tf = self._chunk_tokens[chunk_id].get(term, 0)
                if not chunk_tf:
                    continue
                score = idf * (1 + chunk_tf * 0.3) * (1 + query_tf * 0.05)
                if term in self._title_tokens[chunk_id]:
                    score *= 1.25
                if term in self._section_tokens[chunk_id]:
                    score *= 1.1
                section = self.chunks[chunk_id].get("section")
                score *= section_weights.get(section, 1.0)
                scores[chunk_id] += score
        ranked = sorted(
            scores.items(),
            key=lambda item: (-item[1], item[0]),
        )[:top_k]
        return [
            SearchHit(
                chunk_id=chunk_id,
                source_id=self.chunks[chunk_id]["source_id"],
                title=self.chunks[chunk_id]["title"],
                section=self.chunks[chunk_id].get("section"),
                score=score,
                text_preview=self.chunks[chunk_id]["text"][:220],
            )
            for chunk_id, score in ranked
        ]

    def rerank(self, query: str, candidate_chunk_ids: list[str]) -> list[SearchHit]:
        terms = set(tokenize(query))
        section_weights = {
            "finding": 1.15,
            "recommendation": 1.08,
            "failure": 1.03,
            "setup": 0.97,
            "overview": 0.95,
        }
        scored: list[tuple[float, str]] = []
        for chunk_id in candidate_chunk_ids:
            chunk = self.chunks[chunk_id]
            text_terms = set(tokenize(chunk["text"]))
            title_terms = self._title_tokens[chunk_id]
            section_terms = self._section_tokens[chunk_id]
            overlap = len(terms & text_terms)
            title_overlap = len(terms & title_terms)
            section_overlap = len(terms & section_terms)
            score = overlap + 0.75 * title_overlap + 0.35 * section_overlap
            score *= section_weights.get(chunk.get("section"), 1.0)
            scored.append((score, chunk_id))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [
            SearchHit(
                chunk_id=chunk_id,
                source_id=self.chunks[chunk_id]["source_id"],
                title=self.chunks[chunk_id]["title"],
                section=self.chunks[chunk_id].get("section"),
                score=score,
                text_preview=self.chunks[chunk_id]["text"][:220],
            )
            for score, chunk_id in scored
        ]
