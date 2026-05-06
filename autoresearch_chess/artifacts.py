from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import Any

from .config import BOT_DIR, RUNS_DIR


def new_run_id(prefix: str = "run") -> str:
    return f"{prefix}_{time.strftime('%Y%m%d_%H%M%S')}"


def ensure_run_dir(run_id: str) -> Path:
    run_dir = RUNS_DIR / run_id
    (run_dir / "iterations").mkdir(parents=True, exist_ok=True)
    (run_dir / "best").mkdir(parents=True, exist_ok=True)
    return run_dir


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def snapshot_best_bot(run_dir: Path) -> None:
    target = run_dir / "best" / "bot"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(BOT_DIR, target)
    snapshot = run_dir / "best" / "bot_snapshot.py"
    snapshot.write_text((BOT_DIR / "search.py").read_text(encoding="utf-8"), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
