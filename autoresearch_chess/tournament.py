from __future__ import annotations

import importlib
import hashlib
import random
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import chess

from .config import EvalConfig
from .elo import OpponentScore, estimate_elo
from .opponents import OPPONENTS, Opponent


OPENINGS = (
    (),
    ("e2e4",),
    ("d2d4",),
    ("g1f3",),
    ("c2c4",),
)


def load_choose_move(repo_root: Path):
    sys.path.insert(0, str(repo_root))
    for name in list(sys.modules):
        if name == "bot" or name.startswith("bot."):
            del sys.modules[name]
    try:
        module = importlib.import_module("bot.search")
        return module.choose_move
    finally:
        try:
            sys.path.remove(str(repo_root))
        except ValueError:
            pass


def board_from_opening(moves: tuple[str, ...]) -> chess.Board:
    board = chess.Board()
    for move_uci in moves:
        board.push(chess.Move.from_uci(move_uci))
    return board


def play_game(
    choose_move,
    opponent: Opponent,
    *,
    bot_color: bool,
    seed: int,
    max_plies: int,
    depth_limit: int,
) -> float:
    rng = random.Random(seed)
    opening = OPENINGS[seed % len(OPENINGS)]
    board = board_from_opening(opening)
    plies = 0
    while not board.is_game_over(claim_draw=True) and plies < max_plies:
        try:
            if board.turn == bot_color:
                move = choose_move(board.copy(stack=False), depth_limit)
            else:
                move = opponent.choose_move(board.copy(stack=False), rng)
        except Exception as exc:
            raise RuntimeError(f"move_generation_failed:{exc}") from exc
        if move not in board.legal_moves:
            raise RuntimeError(f"illegal_move:{move}")
        board.push(move)
        plies += 1

    outcome = board.outcome(claim_draw=True)
    if outcome is None or outcome.winner is None:
        return 0.5
    if outcome.winner == bot_color:
        return 1.0
    return 0.0


def run_tournament(repo_root: Path, config: EvalConfig) -> dict[str, Any]:
    choose_move = load_choose_move(repo_root)
    opponent_scores: list[OpponentScore] = []
    raw_games: list[dict[str, Any]] = []

    for opponent_name in config.opponent_names:
        opponent = OPPONENTS[opponent_name]
        wins = draws = losses = 0
        for game_index in range(config.games_per_opponent):
            bot_color = chess.WHITE if game_index % 2 == 0 else chess.BLACK
            seed_bytes = hashlib.sha256(f"{opponent_name}:{game_index}".encode("utf-8")).digest()
            seed = int.from_bytes(seed_bytes[:4], "big") % 1_000_000
            score = play_game(
                choose_move,
                opponent,
                bot_color=bot_color,
                seed=seed,
                max_plies=config.max_plies,
                depth_limit=config.candidate_depth_limit,
            )
            if score == 1.0:
                wins += 1
            elif score == 0.5:
                draws += 1
            else:
                losses += 1
            raw_games.append(
                {
                    "opponent": opponent_name,
                    "bot_color": "white" if bot_color == chess.WHITE else "black",
                    "score": score,
                    "seed": seed,
                }
            )
        opponent_scores.append(
            OpponentScore(
                opponent=opponent.name,
                anchor_elo=opponent.anchor_elo,
                wins=wins,
                draws=draws,
                losses=losses,
            )
        )

    return {
        "estimated_elo": estimate_elo(opponent_scores),
        "opponents": [asdict(score) | {"score_rate": score.score} for score in opponent_scores],
        "games": raw_games,
        "config": asdict(config),
        "label": "estimated Elo",
    }
