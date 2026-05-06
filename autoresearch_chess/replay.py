from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

from .chart import write_progress_png
from .config import DEMO_REPLAY_DIR, ROOT, RUNS_DIR


def replay_run(source: Path, target_name: str | None = None, *, force: bool = False) -> Path:
    if not source.exists():
        raise FileNotFoundError(f"Replay source not found: {source}")
    if target_name is None:
        target_name = f"replay_{time.strftime('%Y%m%d_%H%M%S')}"
    target = RUNS_DIR / target_name
    if target.exists():
        if not force:
            raise FileExistsError(f"Replay target already exists: {target}. Use --force to overwrite.")
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    progress = target / "progress.jsonl"
    values: list[float] = []
    if progress.exists():
        for line in progress.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            values.append(float(payload.get("best_elo", 0.0)))
    if values:
        write_progress_png(target / "progress.png", values)
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Replay captured AutoResearch run without API/network.")
    parser.add_argument("--run", default=str(DEMO_REPLAY_DIR))
    parser.add_argument("--target-name", default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    target = replay_run(
        (ROOT / args.run).resolve() if not Path(args.run).is_absolute() else Path(args.run),
        target_name=args.target_name,
        force=args.force,
    )
    print(f"replayed estimated Elo run to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
