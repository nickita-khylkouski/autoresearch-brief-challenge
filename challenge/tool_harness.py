from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .corpus import CorpusPack
from .utils import approx_token_count


@dataclass
class ToolMetrics:
    tool_calls: int = 0
    tokens_used: int = 0
    notes: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_calls": self.tool_calls,
            "tokens_used": self.tokens_used,
            "notes": list(self.notes),
            "violations": list(self.violations),
        }


class ToolHarness:
    def __init__(self, corpus: CorpusPack, budget: dict[str, Any]) -> None:
        self.corpus = corpus
        self.budget = budget
        self.metrics = ToolMetrics()

    def _record_call(self, payload_text: str = "") -> None:
        self.metrics.tool_calls += 1
        self.metrics.tokens_used += approx_token_count(payload_text)
        max_tool_calls = int(self.budget.get("max_tool_calls", 0) or 0)
        if max_tool_calls and self.metrics.tool_calls > max_tool_calls:
            self._violate(f"tool_calls>{max_tool_calls}")

    def _record_output(self, payload: Any) -> None:
        self.metrics.tokens_used += approx_token_count(str(payload))
        max_tokens = int(self.budget.get("max_tokens", 0) or 0)
        if max_tokens and self.metrics.tokens_used > max_tokens:
            self._violate(f"tokens>{max_tokens}")

    def _violate(self, code: str) -> None:
        if code not in self.metrics.violations:
            self.metrics.violations.append(code)

    def search(self, query: str, top_k: int) -> list[dict[str, Any]]:
        self._record_call(f"search {query} {top_k}")
        cap = int(self.budget.get("max_search_results", top_k))
        effective_top_k = min(top_k, cap)
        if top_k > cap:
            self._violate(f"top_k>{cap}")
        hits = [hit.to_dict() for hit in self.corpus.search(query, effective_top_k)]
        self._record_output(hits)
        return hits

    def get_chunk(self, chunk_id: str) -> dict[str, Any]:
        self._record_call(f"get_chunk {chunk_id}")
        chunk = self.corpus.get_chunk(chunk_id)
        self._record_output(chunk)
        return chunk

    def batch_get_chunks(self, chunk_ids: list[str]) -> list[dict[str, Any]]:
        self._record_call(f"batch_get_chunks {' '.join(chunk_ids)}")
        chunks = [self.corpus.get_chunk(chunk_id) for chunk_id in chunk_ids if chunk_id in self.corpus.chunks]
        self._record_output(chunks)
        return chunks

    def list_sources(self, source_ids: list[str]) -> list[dict[str, Any]]:
        self._record_call(f"list_sources {' '.join(source_ids)}")
        sources = self.corpus.list_sources(source_ids)
        self._record_output(sources)
        return sources

    def rerank(self, query: str, candidate_chunk_ids: list[str]) -> list[dict[str, Any]]:
        self._record_call(f"rerank {query} {' '.join(candidate_chunk_ids)}")
        hits = [hit.to_dict() for hit in self.corpus.rerank(query, candidate_chunk_ids)]
        self._record_output(hits)
        return hits

    def compare(self, chunk_ids: list[str]) -> dict[str, Any]:
        self._record_call(f"compare {' '.join(chunk_ids)}")
        chunks = [self.corpus.get_chunk(chunk_id) for chunk_id in chunk_ids if chunk_id in self.corpus.chunks]
        comparison = {
            "chunk_ids": chunk_ids,
            "titles": [chunk["title"] for chunk in chunks],
            "sections": [chunk.get("section") for chunk in chunks],
        }
        self._record_output(comparison)
        return comparison

    def mark_note(self, text: str) -> dict[str, Any]:
        self._record_call(f"mark_note {text}")
        self.metrics.notes.append(text)
        payload = {"ok": True, "note_count": len(self.metrics.notes)}
        self._record_output(payload)
        return payload
