from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from challenge.corpus import CorpusPack
from challenge.evaluator import evaluate_split
from challenge.repository import ROOT, load_tasks


class AutoResearchBriefChallengeTests(unittest.TestCase):
    def test_corpus_pack_search_is_deterministic(self) -> None:
        corpus = CorpusPack("frozen_autoresearch_v1")
        self.assertEqual(len(corpus.chunks), 108)
        hits_a = [hit.to_dict() for hit in corpus.search("hybrid retrieval reranker tool budget", top_k=3)]
        hits_b = [hit.to_dict() for hit in corpus.search("hybrid retrieval reranker tool budget", top_k=3)]
        self.assertEqual(hits_a, hits_b)
        self.assertEqual(hits_a[0]["chunk_id"], "src_001_c03")

    def test_baseline_single_task_emits_run_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            summary = evaluate_split(
                split="dev",
                submission_path=ROOT / "submissions" / "baseline",
                task_id="dev_001",
                output_dir=tmp_dir,
            )
            self.assertEqual(summary["task_count"], 1)
            self.assertGreaterEqual(summary["final_score"], 0.3)
            self.assertTrue((Path(tmp_dir) / "summary.json").exists())
            self.assertTrue((Path(tmp_dir) / "raw_outputs.json").exists())
            self.assertTrue((Path(tmp_dir) / "scores.json").exists())

    def test_invalid_submission_output_scores_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            submission_dir = Path(tmp_dir) / "invalid_submission"
            submission_dir.mkdir()
            (submission_dir / "config.json").write_text(
                json.dumps({"metadata": {"name": "invalid"}, "citation_count": 1}),
                encoding="utf-8",
            )
            (submission_dir / "submission_impl.py").write_text(
                textwrap.dedent(
                    """
                    def run_task(*, task, tools, config):
                        return {"answer": 123, "citations": "bad"}
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            summary = evaluate_split(
                split="dev",
                submission_path=submission_dir,
                task_id="dev_001",
                output_dir=Path(tmp_dir) / "run",
            )
            result = summary["task_results"][0]
            self.assertEqual(result["status"], "invalid_output")
            self.assertEqual(result["task_score"], 0.0)

    def test_budget_violation_applies_quarter_penalty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            submission_dir = Path(tmp_dir) / "budget_submission"
            submission_dir.mkdir()
            (submission_dir / "config.json").write_text(
                json.dumps({"metadata": {"name": "budget-violation"}}),
                encoding="utf-8",
            )
            (submission_dir / "submission_impl.py").write_text(
                textwrap.dedent(
                    """
                    def run_task(*, task, tools, config):
                        for idx in range(11):
                            tools.mark_note(f"note-{idx}")
                        return {
                            "answer": "Hybrid lexical dense retrieval with a reranker cut candidate pool and kept a small candidate pool to preserve latency budget.",
                            "citations": ["src_001_c03", "src_001_c04", "src_011_c03"],
                            "notes": "budget test",
                        }
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            summary = evaluate_split(
                split="dev",
                submission_path=submission_dir,
                task_id="dev_001",
                output_dir=Path(tmp_dir) / "run",
            )
            result = summary["task_results"][0]
            self.assertEqual(result["status"], "scored")
            self.assertIn("budget_violation", result["penalties"])
            self.assertAlmostEqual(result["task_score"], 0.25, places=6)

    def test_leaderboard_cli_reads_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            summary = evaluate_split(
                split="dev",
                submission_path=ROOT / "submissions" / "baseline",
                task_id="dev_001",
                output_dir=tmp_dir,
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "leaderboard.py"),
                    "--score-file",
                    str(Path(summary["run_dir"]) / "summary.json"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            rows = json.loads(result.stdout)
            self.assertEqual(rows[0]["submission"], "baseline")
            self.assertEqual(rows[0]["split"], "dev")

    def test_all_splits_are_present(self) -> None:
        self.assertEqual(len(load_tasks("dev")), 20)

    def test_only_dev_split_is_public(self) -> None:
        with self.assertRaises(ValueError):
            load_tasks("public_leaderboard")

    def test_network_is_blocked_during_evaluation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            submission_dir = Path(tmp_dir) / "network_submission"
            submission_dir.mkdir()
            (submission_dir / "config.json").write_text(
                json.dumps(
                    {
                        "metadata": {"name": "network", "version": "0.1.0", "expected_token_budget": 2200},
                        "retrieval": {"top_k": 6, "rerank_top_n": 4},
                        "prompt_files": {},
                    }
                ),
                encoding="utf-8",
            )
            (submission_dir / "submission_impl.py").write_text(
                textwrap.dedent(
                    """
                    import socket

                    def run_task(*, task, tools, config):
                        sock = socket.socket()
                        sock.connect(("example.com", 80))
                        return {"answer": "x", "citations": ["src_001_c03"]}
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            summary = evaluate_split(
                split="dev",
                submission_path=submission_dir,
                task_id="dev_001",
                output_dir=Path(tmp_dir) / "run",
            )
            result = summary["task_results"][0]
            self.assertEqual(result["status"], "execution_error")
            self.assertIn("NetworkAccessError", result["error"])


if __name__ == "__main__":
    unittest.main()
