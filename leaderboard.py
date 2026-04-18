from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render leaderboard rows from evaluation summaries.")
    parser.add_argument("--score-file", action="append", required=True)
    args = parser.parse_args()
    rows = []
    for score_file in args.score_file:
        payload = json.loads(Path(score_file).read_text(encoding="utf-8"))
        rows.append(
            {
                "submission": payload["submission"]["name"],
                "split": payload["split"],
                "final_score": payload["final_score"],
                "avg_latency_s": payload["average_latency_seconds"],
                "avg_tool_calls": payload["average_tool_calls"],
                "avg_tokens": payload["average_tokens_used"],
            }
        )
    rows.sort(key=lambda row: (-row["final_score"], row["submission"]))
    print(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
