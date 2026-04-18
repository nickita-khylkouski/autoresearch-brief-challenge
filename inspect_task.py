from __future__ import annotations

import argparse
import json

from challenge.inspection import inspect_task


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a challenge task and its visible retrieval context.")
    parser.add_argument("--task-id", required=True)
    args = parser.parse_args()
    print(json.dumps(inspect_task(args.task_id), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
