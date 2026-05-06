from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PatchResult:
    ok: bool
    candidate_root: Path | None
    error: str = ""


def make_candidate_copy(root: Path) -> Path:
    temp_root = Path(tempfile.mkdtemp(prefix="autoresearch_candidate_"))
    candidate = temp_root / "repo"
    candidate.mkdir()
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")
    for rel in ("autoresearch_chess", "bot"):
        shutil.copytree(root / rel, candidate / rel, ignore=ignore)
    for rel in ("requirements.txt",):
        if (root / rel).exists():
            shutil.copy2(root / rel, candidate / rel)
    return candidate


def apply_unified_patch(root: Path, patch_text: str) -> PatchResult:
    candidate = make_candidate_copy(root)
    try:
        proc = subprocess.run(
            ["git", "apply", "--whitespace=nowarn", "-"],
            cwd=candidate,
            input=patch_text,
            text=True,
            capture_output=True,
            timeout=10,
        )
    except Exception as exc:
        return PatchResult(False, candidate, f"patch_exception:{exc}")
    if proc.returncode != 0:
        return PatchResult(False, candidate, (proc.stderr or proc.stdout).strip())
    return PatchResult(True, candidate)


def copy_editable_files(src_root: Path, dest_root: Path, changed_files: list[str]) -> None:
    for rel in changed_files:
        src = src_root / rel
        dest = dest_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
