from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


EDITABLE_FILES = {
    "bot/evaluate.py",
    "bot/search.py",
    "bot/move_ordering.py",
    "bot/config.py",
}

FORBIDDEN_PREFIXES = (
    "eval/",
    "tournament/",
    "autoresearch_loop/",
    "autoresearch_chess/evaluator.py",
    "autoresearch_chess/tournament.py",
    "autoresearch_chess/elo.py",
    "autoresearch_chess/minimax_client.py",
    "artifacts/",
    "tests/",
)

FORBIDDEN_FILES = {
    ".env",
    ".env.example",
    "README.md",
    "workshop.ipynb",
    "notebooks/workshop.ipynb",
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
}

FORBIDDEN_DEPENDENCY_PATTERNS = (
    re.compile(r"^\s*(import|from)\s+(requests|urllib|httpx|aiohttp|socket|subprocess|os)\b"),
    re.compile(r"pip\s+install"),
)


@dataclass(frozen=True)
class GuardrailResult:
    ok: bool
    reasons: list[str]
    changed_files: list[str]


def file_sha256(path: Path) -> str:
    if not path.exists():
        return "<missing>"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hash_forbidden_files(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("artifacts/"):
            continue
        if is_forbidden(rel):
            out[rel] = file_sha256(path)
    return out


def is_forbidden(rel_path: str) -> bool:
    if rel_path in FORBIDDEN_FILES:
        return True
    return any(rel_path.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)


def _extract_diff_paths(patch_text: str) -> list[str]:
    paths: list[str] = []
    for line in patch_text.splitlines():
        if line.startswith("+++ b/"):
            paths.append(line.removeprefix("+++ b/").strip())
        elif line.startswith("--- b/"):
            paths.append(line.removeprefix("--- b/").strip())
    return sorted(set(path for path in paths if path != "/dev/null"))


def validate_patch_text(patch_text: str) -> GuardrailResult:
    reasons: list[str] = []
    changed_files = _extract_diff_paths(patch_text)
    if not changed_files:
        reasons.append("patch_does_not_declare_changed_files")
    for rel in changed_files:
        if rel not in EDITABLE_FILES:
            reasons.append(f"illegal_file_edit:{rel}")
        if is_forbidden(rel):
            reasons.append(f"forbidden_file_edit:{rel}")
    for line in patch_text.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        body = line[1:]
        for pattern in FORBIDDEN_DEPENDENCY_PATTERNS:
            if pattern.search(body):
                reasons.append(f"forbidden_dependency_or_runtime:{body.strip()[:80]}")
    return GuardrailResult(ok=not reasons, reasons=reasons, changed_files=changed_files)


def validate_candidate_tree(root: Path, before_hashes: dict[str, str]) -> GuardrailResult:
    reasons: list[str] = []
    changed_files: list[str] = []
    after_hashes = hash_forbidden_files(root)
    for rel, before in before_hashes.items():
        after = after_hashes.get(rel, "<missing>")
        if after == "<missing>":
            continue
        if before != after:
            reasons.append(f"forbidden_file_changed:{rel}")
            changed_files.append(rel)
    for rel, after in after_hashes.items():
        if rel not in before_hashes:
            reasons.append(f"new_forbidden_file:{rel}")
            changed_files.append(rel)
    return GuardrailResult(ok=not reasons, reasons=reasons, changed_files=sorted(set(changed_files)))
