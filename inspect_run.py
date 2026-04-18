from __future__ import annotations

import argparse
import json

from challenge.inspection import inspect_run


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a stored challenge run summary.")
    parser.add_argument("--run", required=True)
    args = parser.parse_args()
    print(json.dumps(inspect_run(args.run), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
