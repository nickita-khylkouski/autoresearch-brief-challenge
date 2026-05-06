from __future__ import annotations

import argparse
from pathlib import Path

from .artifacts import write_json
from .config import ROOT
from .evaluator import evaluate_repo


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate current chess bot and write estimated Elo JSON.")
    parser.add_argument("--bot", default="bot/current.py", help="Compatibility placeholder; bot package is loaded from repo root.")
    parser.add_argument("--out", default="artifacts/eval.json")
    parser.add_argument("--games-per-opponent", type=int, default=4)
    args = parser.parse_args(argv)

    from .config import EvalConfig

    result = evaluate_repo(ROOT, EvalConfig(games_per_opponent=args.games_per_opponent))
    write_json(ROOT / args.out, result)
    print(f"estimated Elo: {result['estimated_elo']} ok={result['ok']} wrote={args.out}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
