from __future__ import annotations

import py_compile
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from .config import EvalConfig, ROOT
from .tournament import run_tournament


def syntax_check(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for rel in ("bot/config.py", "bot/evaluate.py", "bot/move_ordering.py", "bot/search.py"):
        try:
            py_compile.compile(str(repo_root / rel), doraise=True)
        except Exception as exc:
            errors.append(f"{rel}:{exc}")
    return errors


def evaluate_repo(repo_root: Path | None = None, config: EvalConfig | None = None) -> dict[str, Any]:
    root = repo_root or ROOT
    eval_config = config or EvalConfig()
    errors = syntax_check(root)
    if errors:
        return {"ok": False, "estimated_elo": 0.0, "errors": errors, "label": "estimated Elo"}
    try:
        result = run_tournament(root, eval_config)
    except Exception as exc:
        return {"ok": False, "estimated_elo": 0.0, "errors": [str(exc)], "label": "estimated Elo"}
    result["ok"] = True
    result["errors"] = []
    return result


def evaluate_repo_subprocess(repo_root: Path, config: EvalConfig, *, timeout_seconds: int) -> dict[str, Any]:
    output_path = repo_root / "artifacts" / "candidate_eval.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "autoresearch_chess.eval",
        "--out",
        str(output_path.relative_to(repo_root)),
        "--games-per-opponent",
        str(config.games_per_opponent),
    ]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(repo_root)
    try:
        proc = subprocess.run(
            command,
            cwd=repo_root,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "estimated_elo": 0.0,
            "errors": [f"timeout:excessive_runtime>{timeout_seconds}s"],
            "label": "estimated Elo",
        }
    if output_path.exists():
        try:
            payload = json.loads(output_path.read_text(encoding="utf-8"))
        except Exception as exc:
            payload = {"ok": False, "estimated_elo": 0.0, "errors": [f"invalid_eval_json:{exc}"], "label": "estimated Elo"}
    else:
        payload = {"ok": False, "estimated_elo": 0.0, "errors": ["missing_eval_json"], "label": "estimated Elo"}
    if proc.returncode != 0:
        errors = list(payload.get("errors", []))
        if proc.stderr.strip():
            errors.append(proc.stderr.strip()[:1000])
        payload["ok"] = False
        payload["errors"] = errors
    return payload
