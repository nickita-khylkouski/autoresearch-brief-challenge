from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .guardrails import EDITABLE_FILES, FORBIDDEN_FILES, FORBIDDEN_PREFIXES


def read_file(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def build_prompt(
    *,
    root: Path,
    baseline_eval: dict[str, Any],
    best_eval: dict[str, Any],
    history: list[dict[str, Any]],
) -> str:
    editable_listing = "\n\n".join(
        f"### {rel}\n```python\n{read_file(root, rel)}\n```" for rel in sorted(EDITABLE_FILES)
    )
    history_summary = json.dumps(history[-5:], ensure_ascii=True, indent=2)
    return f"""You are MiniMax running inside a constrained AutoResearch loop.

Objective: improve the chess bot's estimated Elo.

Rules:
- Return exactly one unified diff patch.
- Return no Markdown fences and no explanation.
- Keep the patch small; prefer one focused change under 80 diff lines.
- You may edit only these files: {', '.join(sorted(EDITABLE_FILES))}.
- Do not edit forbidden files: {', '.join(sorted(FORBIDDEN_FILES))}.
- Do not edit paths under these prefixes: {', '.join(FORBIDDEN_PREFIXES)}.
- Do not add dependencies.
- Do not use network, subprocess, filesystem tricks, or opponent/seed special cases.
- Keep the bot legal and fast.
- Optimize general chess strength through evaluation/search heuristics.

Scoring:
- The evaluator reports estimated Elo from fixed local matches.
- Current best estimated Elo: {best_eval.get('estimated_elo')}.
- Baseline estimated Elo: {baseline_eval.get('estimated_elo')}.

Recent history:
```json
{history_summary}
```

Editable files:
{editable_listing}

Return only the unified diff patch.
"""
