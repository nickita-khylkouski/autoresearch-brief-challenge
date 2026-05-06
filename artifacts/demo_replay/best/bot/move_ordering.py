from __future__ import annotations

import chess

from . import config
from .evaluate import PIECE_VALUES


def move_score(board: chess.Board, move: chess.Move) -> int:
    score = 0
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        if victim:
            score += PIECE_VALUES.get(victim.piece_type, 0)
        if attacker:
            score -= PIECE_VALUES.get(attacker.piece_type, 0) // 10
        score += 1_000
    if move.promotion:
        score += PIECE_VALUES.get(move.promotion, 0)
    if board.gives_check(move):
        score += 75
    if not config.CAPTURE_FIRST:
        score = -score
    return score


def ordered_moves(board: chess.Board) -> list[chess.Move]:
    moves = list(board.legal_moves)
    return sorted(moves, key=lambda move: move_score(board, move), reverse=True)
