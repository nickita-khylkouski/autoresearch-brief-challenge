from __future__ import annotations

import argparse
import json

from challenge.evaluator import evaluate_split
from challenge.repository import available_splits


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AutoResearch Brief Challenge evaluation.")
    parser.add_argument("--split", required=True, choices=available_splits())
    parser.add_argument("--submission", required=True)
    parser.add_argument("--task-id")
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    summary = evaluate_split(
        split=args.split,
        submission_path=args.submission,
        task_id=args.task_id,
        output_dir=args.output_dir,
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
