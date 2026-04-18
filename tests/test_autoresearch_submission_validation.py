from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from challenge.repository import ROOT
from challenge.validation import validate_submission_bundle


class AutoResearchSubmissionValidationTests(unittest.TestCase):
    def test_template_submission_is_valid(self) -> None:
        result = validate_submission_bundle(ROOT / "submissions" / "template")
        self.assertTrue(result["ok"])

    def test_cli_returns_nonzero_for_invalid_submission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            submission_dir = Path(tmp_dir) / "bad"
            submission_dir.mkdir()
            (submission_dir / "config.json").write_text(json.dumps({"metadata": {}}), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "validate_submission.py"),
                    "--submission",
                    str(submission_dir),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc.returncode, 0)
            payload = json.loads(proc.stdout)
            self.assertFalse(payload["ok"])


if __name__ == "__main__":
    unittest.main()
