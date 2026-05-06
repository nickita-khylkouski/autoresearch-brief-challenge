from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOT_DIR = ROOT / "bot"
ARTIFACT_DIR = ROOT / "artifacts"
RUNS_DIR = ARTIFACT_DIR / "runs"
DEMO_REPLAY_DIR = ARTIFACT_DIR / "demo_replay"


@dataclass(frozen=True)
class EvalConfig:
    games_per_opponent: int = 4
    max_plies: int = 120
    candidate_depth_limit: int = 3
    opponent_names: tuple[str, ...] = ("random", "greedy", "baseline")


@dataclass(frozen=True)
class LoopConfig:
    iterations: int = 5
    accept_threshold_elo: float = 5.0
    mock_minimax: bool = False
    run_id: str | None = None
    eval_config: EvalConfig = EvalConfig()


STAGE_EVAL_CONFIG = EvalConfig(games_per_opponent=2, max_plies=90)
STAGE_LOOP_CONFIG = LoopConfig(
    iterations=3,
    accept_threshold_elo=1.0,
    mock_minimax=True,
    eval_config=STAGE_EVAL_CONFIG,
)
