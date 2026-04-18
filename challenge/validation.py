from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_submission_bundle(path_like: str | Path) -> dict[str, Any]:
    path = Path(path_like).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return {"ok": False, "errors": [f"missing submission path: {path}"], "warnings": []}

    config_path = path / "config.json"
    if not config_path.exists():
        errors.append("missing config.json")
        return {"ok": False, "errors": errors, "warnings": warnings}

    try:
        config = _read_json(config_path)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid config.json: {exc}")
        return {"ok": False, "errors": errors, "warnings": warnings}

    metadata = config.get("metadata")
    retrieval = config.get("retrieval")
    prompt_files = config.get("prompt_files", {})

    if not isinstance(metadata, dict):
        errors.append("config.metadata must be an object")
    else:
        for key in ("name", "version", "expected_token_budget"):
            if key not in metadata:
                errors.append(f"config.metadata missing {key}")

    if not isinstance(retrieval, dict):
        errors.append("config.retrieval must be an object")
    else:
        for key in ("top_k", "rerank_top_n"):
            if key not in retrieval:
                errors.append(f"config.retrieval missing {key}")

    if not isinstance(prompt_files, dict):
        errors.append("config.prompt_files must be an object")
    else:
        for label, relative_path in prompt_files.items():
            prompt_path = path / relative_path
            if not prompt_path.exists():
                errors.append(f"prompt file listed in config is missing: {label} -> {relative_path}")

    optional_files = {
        "research.md": "recommended: document the objective and constraints",
        "memory.md": "recommended: include iteration notes or scaffold memory",
        "results.jsonl": "recommended: include local run history",
        "writeup.md": "recommended: include a short approach summary for leaderboard review",
    }
    for filename, message in optional_files.items():
        if not (path / filename).exists():
            warnings.append(f"{filename}: {message}")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
    }
