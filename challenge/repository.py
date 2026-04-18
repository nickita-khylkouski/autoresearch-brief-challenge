from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from .utils import read_json


ROOT = Path(__file__).resolve().parent.parent
CORPORA_DIR = ROOT / "corpora"
TASKS_DIR = ROOT / "tasks"
SCHEMAS_DIR = ROOT / "challenge" / "schemas"


def available_splits() -> list[str]:
    return ["dev"]


def split_task_path(split: str) -> Path:
    return TASKS_DIR / f"{split}.json"


def split_hidden_path(split: str) -> Path:
    return TASKS_DIR / "_private" / f"{split}_hidden.json"


def load_schema(name: str) -> dict[str, Any]:
    return read_json(SCHEMAS_DIR / name)


def load_tasks(split: str) -> list[dict[str, Any]]:
    if split not in available_splits():
        raise ValueError(f"Unknown split: {split}")
    return read_json(split_task_path(split))


def load_hidden_specs(split: str) -> dict[str, dict[str, Any]]:
    payload = read_json(split_hidden_path(split))
    return {entry["task_id"]: entry for entry in payload}


@lru_cache(maxsize=None)
def load_corpus_pack(pack_id: str) -> dict[str, Any]:
    base = CORPORA_DIR / pack_id
    if not base.exists():
        raise FileNotFoundError(f"Missing corpus pack: {pack_id}")
    return {
        "pack_id": pack_id,
        "sources": read_json(base / "sources.json"),
        "chunks": read_json(base / "chunks.json"),
        "index": read_json(base / "index.json"),
    }
