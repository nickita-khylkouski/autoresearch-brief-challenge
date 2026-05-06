from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

import chess


MoveChooser = Callable[[chess.Board, random.Random], chess.Move]

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}


@dataclass(frozen=True)
class Opponent:
    name: str
    anchor_elo: int
    choose_move: MoveChooser


def random_move(board: chess.Board, rng: random.Random) -> chess.Move:
    return rng.choice(list(board.legal_moves))


def greedy_move(board: chess.Board, rng: random.Random) -> chess.Move:
    moves = list(board.legal_moves)
    rng.shuffle(moves)
    return max(moves, key=lambda move: opponent_move_score(board, move))


def opponent_move_score(board: chess.Board, move: chess.Move) -> int:
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
    return score


def baseline_move(board: chess.Board, rng: random.Random) -> chess.Move:
    moves = list(board.legal_moves)
    rng.shuffle(moves)
    best = moves[0]
    best_score = -10**9 if board.turn == chess.WHITE else 10**9
    for move in moves:
        board.push(move)
        score = material_only(board)
        board.pop()
        if board.turn == chess.WHITE and score > best_score:
            best_score = score
            best = move
        elif board.turn == chess.BLACK and score < best_score:
            best_score = score
            best = move
    return best


def heuristic_move(board: chess.Board, rng: random.Random) -> chess.Move:
    moves = list(board.legal_moves)
    rng.shuffle(moves)
    best = moves[0]
    best_score = -10**9 if board.turn == chess.WHITE else 10**9
    for move in moves:
        board.push(move)
        score = material_only(board) + 3 * board.legal_moves.count()
        board.pop()
        if board.turn == chess.WHITE and score > best_score:
            best_score = score
            best = move
        elif board.turn == chess.BLACK and score < best_score:
            best_score = score
            best = move
    return best


def material_only(board: chess.Board) -> int:
    score = 0
    for piece_type, value in PIECE_VALUES.items():
        score += len(board.pieces(piece_type, chess.WHITE)) * value
        score -= len(board.pieces(piece_type, chess.BLACK)) * value
    return score


OPPONENTS = {
    "random": Opponent("random", 250, random_move),
    "greedy": Opponent("greedy", 650, greedy_move),
    "baseline": Opponent("baseline", 900, baseline_move),
    "heuristic": Opponent("heuristic", 1200, heuristic_move),
}
