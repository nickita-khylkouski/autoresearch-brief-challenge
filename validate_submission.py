from __future__ import annotations

import argparse
import json

from challenge.validation import validate_submission_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an AutoResearch Brief Challenge submission bundle.")
    parser.add_argument("--submission", required=True)
    args = parser.parse_args()
    result = validate_submission_bundle(args.submission)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
