from __future__ import annotations

import difflib
import re
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


_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@")
_FILE_RE = re.compile(r"^\+\+\+ (?:b/)?(.+?)\s*$")


def _strip_phantom_leading_context(patch_text: str, candidate_root: Path) -> str:
    """Drop blank leading context lines from each hunk when the target file's
    line at that position is not actually blank.

    MiniMax M2.7 (and other LLMs that emit unified diffs) frequently prepend
    a blank context line to a hunk that starts at line 1, even when the file
    doesn't have a leading blank. git apply rejects such hunks. This pass
    removes only that specific defect; other context mismatches still fail.
    """
    lines = patch_text.splitlines(keepends=True)
    out: list[str] = []
    target: Path | None = None
    i = 0
    while i < len(lines):
        line = lines[i]
        m_file = _FILE_RE.match(line.rstrip("\n"))
        if m_file:
            rel = m_file.group(1)
            cand = candidate_root / rel
            target = cand if cand.is_file() else None
            out.append(line)
            i += 1
            continue
        m_hunk = _HUNK_RE.match(line)
        if not m_hunk or target is None:
            out.append(line)
            i += 1
            continue
        out.append(line)
        i += 1
        start = int(m_hunk.group(1))
        src_lines = target.read_text(encoding="utf-8").splitlines()
        file_at_start = src_lines[start - 1] if 1 <= start <= len(src_lines) else None
        while i < len(lines):
            body = lines[i]
            if body.startswith(("@@", "--- ", "+++ ", "diff ")):
                break
            is_blank_context = body in (" \n", " \r\n", "\n", "\r\n")
            if is_blank_context and file_at_start not in (None, ""):
                i += 1
                continue
            break
    return "".join(out)


def apply_unified_patch(root: Path, patch_text: str) -> PatchResult:
    candidate = make_candidate_copy(root)
    normalized = _strip_phantom_leading_context(patch_text, candidate)
    try:
        proc = subprocess.run(
            ["git", "apply", "--whitespace=nowarn", "--recount", "-"],
            cwd=candidate,
            input=normalized,
            text=True,
            capture_output=True,
            timeout=10,
        )
    except Exception as exc:
        return PatchResult(False, candidate, f"patch_exception:{exc}")
    if proc.returncode != 0:
        return PatchResult(False, candidate, (proc.stderr or proc.stdout).strip())
    return PatchResult(True, candidate)


def compute_edit_diff(
    root: Path, rel_path: str, old_str: str, new_str: str
) -> tuple[str | None, str | None]:
    """Synthesize a unified diff for replacing one occurrence of old_str.

    Returns (diff_text, None) on success or (None, error_code) on failure.
    Error codes: file_not_found, string_not_found, not_unique, no_change.
    """
    target = root / rel_path
    if not target.is_file():
        return None, "file_not_found"
    content = target.read_text(encoding="utf-8")
    count = content.count(old_str)
    if count == 0:
        return None, "string_not_found"
    if count > 1:
        return None, f"not_unique:{count}_matches"
    if old_str == new_str:
        return None, "no_change"
    new_content = content.replace(old_str, new_str, 1)
    diff_body = "".join(
        difflib.unified_diff(
            content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{rel_path}",
            tofile=f"b/{rel_path}",
            n=3,
        )
    )
    if not diff_body:
        return None, "no_change"
    diff_text = f"diff --git a/{rel_path} b/{rel_path}\n{diff_body}"
    if not diff_text.endswith("\n"):
        diff_text += "\n"
    return diff_text, None


def copy_editable_files(src_root: Path, dest_root: Path, changed_files: list[str]) -> None:
    for rel in changed_files:
        src = src_root / rel
        dest = dest_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
