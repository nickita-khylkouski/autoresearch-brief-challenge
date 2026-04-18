from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .corpus import CorpusPack
from .repository import load_tasks


def inspect_task(task_id: str) -> dict[str, Any]:
    for split in ("dev",):
        for task in load_tasks(split):
            if task["task_id"] != task_id:
                continue
            corpus = CorpusPack(task["corpus_pack_id"])
            sample_hits = [hit.to_dict() for hit in corpus.search(task["question"], top_k=5)]
            return {
                "split": split,
                "task": task,
                "corpus_stats": {
                    "pack_id": corpus.pack_id,
                    "chunk_count": len(corpus.chunks),
                    "source_count": len(corpus.sources),
                },
                "sample_hits": sample_hits,
            }
    raise ValueError(f"Unknown visible task_id: {task_id}")


def inspect_run(path_like: str | Path) -> dict[str, Any]:
    path = Path(path_like).resolve()
    if path.is_dir():
        path = path / "summary.json"
    return json.loads(path.read_text(encoding="utf-8"))
