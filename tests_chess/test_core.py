from __future__ import annotations

import json
import os
from pathlib import Path

import chess

from autoresearch_chess.config import EvalConfig, LoopConfig, ROOT
from autoresearch_chess.elo import OpponentScore, estimate_elo
from autoresearch_chess.evaluator import evaluate_repo
from autoresearch_chess.evaluator import evaluate_repo_subprocess
from autoresearch_chess.guardrails import validate_patch_text
from autoresearch_chess.loop import run_loop
from autoresearch_chess.minimax_client import MiniMaxClient, MiniMaxSettings, mask_secret
from autoresearch_chess.opponents import greedy_move
from autoresearch_chess.replay import replay_run
from bot.search import choose_move


BASELINE_CONFIG = """SEARCH_DEPTH = 1
MATERIAL_WEIGHT = 1.0
MOBILITY_WEIGHT = 0.0
KING_SAFETY_WEIGHT = 0.0
USE_PIECE_SQUARES = False
CAPTURE_FIRST = True
"""


def test_estimated_elo_orders_better_scores() -> None:
    weak = estimate_elo([OpponentScore("anchor", 900, wins=1, draws=0, losses=3)])
    strong = estimate_elo([OpponentScore("anchor", 900, wins=3, draws=0, losses=1)])
    assert strong > weak


def test_baseline_bot_returns_legal_move() -> None:
    board = chess.Board()
    move = choose_move(board)
    assert move in board.legal_moves


def test_evaluator_rejects_illegal_move(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "bot").mkdir()
    for source in (ROOT / "bot").glob("*.py"):
        (repo / "bot" / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    (repo / "bot" / "search.py").write_text(
        "import chess\n\ndef choose_move(board, depth_limit=None):\n    return chess.Move.from_uci('a2a5')\n",
        encoding="utf-8",
    )
    result = evaluate_repo(repo, EvalConfig(games_per_opponent=1, max_plies=4))
    assert not result["ok"]
    assert "illegal_move" in json.dumps(result)


def test_guardrails_detect_forbidden_file_and_dependency() -> None:
    patch = """diff --git a/eval/score.py b/eval/score.py
--- a/eval/score.py
+++ b/eval/score.py
@@ -1,1 +1,2 @@
 value = 1
+import requests
"""
    result = validate_patch_text(patch)
    assert not result.ok
    assert any("illegal_file_edit" in reason for reason in result.reasons)
    assert any("forbidden_dependency" in reason for reason in result.reasons)


def test_secret_masking() -> None:
    text = "Authorization: Bearer sk_1234567890abcdef and sk-test-secret"
    masked = mask_secret(text)
    assert "1234567890abcdef" not in masked
    assert "***MASKED" in masked


def test_rate_limit_marks_key_cooldown(tmp_path: Path) -> None:
    env_file = tmp_path / "minimax.env"
    env_file.write_text("MINIMAX_API_KEY=sk_test_123456789\n", encoding="utf-8")
    client = MiniMaxClient(MiniMaxSettings(keys=["sk_test_123456789"], env_file=env_file))
    client.mark_key_cooldown(0, "rate limit for sk_test_123456789", seconds=5)
    health = json.loads((tmp_path / "minimax_key_health.json").read_text(encoding="utf-8"))
    assert "0" in health["keys"]
    assert "sk_test_123456789" not in json.dumps(health)


def test_env_file_loading_and_exact_key_redaction(tmp_path: Path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "MINIMAX_API_KEY=plain-minimax-secret-value\nMINIMAX_API_HOST=https://example.test\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("MINIMAX_ENV_FILE", str(env_file))
    client = MiniMaxClient.from_environment()
    assert client.settings.keys == ["plain-minimax-secret-value"]
    assert "plain-minimax-secret-value" not in client.redactor.redact("plain-minimax-secret-value leaked")


def test_opponents_do_not_depend_on_editable_bot_move_ordering(monkeypatch) -> None:
    import bot.move_ordering

    def explode(*args, **kwargs):
        raise AssertionError("editable bot move ordering should not be used by opponents")

    monkeypatch.setattr(bot.move_ordering, "move_score", explode)
    board = chess.Board()
    move = greedy_move(board, __import__("random").Random(1))
    assert move in board.legal_moves


def test_candidate_eval_timeout_rejects_hanging_bot(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "bot").mkdir()
    (repo / "autoresearch_chess").mkdir()
    for source in (ROOT / "bot").glob("*.py"):
        (repo / "bot" / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    for source in (ROOT / "autoresearch_chess").glob("*.py"):
        (repo / "autoresearch_chess" / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    (repo / "bot" / "search.py").write_text(
        "def choose_move(board, depth_limit=None):\n    while True:\n        pass\n",
        encoding="utf-8",
    )
    result = evaluate_repo_subprocess(repo, EvalConfig(games_per_opponent=1), timeout_seconds=1)
    assert not result["ok"]
    assert "timeout" in json.dumps(result)


def test_replay_runs_without_key(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "progress.jsonl").write_text(
        '{"best_elo": 500, "candidate_elo": 500}\n{"best_elo": 700, "candidate_elo": 700}\n',
        encoding="utf-8",
    )
    target = replay_run(source, target_name="pytest_replay", force=True)
    assert (target / "progress.jsonl").exists()
    assert (target / "progress.png").exists()
    assert replay_run(source).name.startswith("replay_")


def test_mock_loop_accepts_improving_patch() -> None:
    config_path = ROOT / "bot" / "config.py"
    original = config_path.read_text(encoding="utf-8")
    try:
        config_path.write_text(BASELINE_CONFIG, encoding="utf-8")
        summary = run_loop(
            LoopConfig(
                iterations=1,
                accept_threshold_elo=1.0,
                mock_minimax=True,
                run_id="pytest_mock_loop",
                eval_config=EvalConfig(games_per_opponent=1, max_plies=60),
            )
        )
        assert summary["accepted"] >= 1
        assert summary["best_eval"]["estimated_elo"] > summary["baseline_eval"]["estimated_elo"]
    finally:
        config_path.write_text(original, encoding="utf-8")
        assert config_path.read_text(encoding="utf-8") == original
        import shutil

        shutil.rmtree(ROOT / "artifacts" / "runs" / "pytest_mock_loop", ignore_errors=True)
        shutil.rmtree(ROOT / "artifacts" / "runs" / "pytest_replay", ignore_errors=True)
