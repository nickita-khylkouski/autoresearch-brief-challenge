from __future__ import annotations

import chess

from . import config
from .evaluate import evaluate
from .move_ordering import ordered_moves


def _search(board: chess.Board, depth: int, alpha: int, beta: int) -> int:
    if depth <= 0 or board.is_game_over():
        return evaluate(board)

    if board.turn == chess.WHITE:
        value = -10**9
        for move in ordered_moves(board):
            board.push(move)
            value = max(value, _search(board, depth - 1, alpha, beta))
            board.pop()
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value

    value = 10**9
    for move in ordered_moves(board):
        board.push(move)
        value = min(value, _search(board, depth - 1, alpha, beta))
        board.pop()
        beta = min(beta, value)
        if alpha >= beta:
            break
    return value


def choose_move(board: chess.Board, depth_limit: int | None = None) -> chess.Move:
    moves = ordered_moves(board)
    if not moves:
        raise ValueError("No legal moves")
    depth = max(1, min(depth_limit or config.SEARCH_DEPTH, config.SEARCH_DEPTH))

    best_move = moves[0]
    if board.turn == chess.WHITE:
        best_score = -10**9
        for move in moves:
            board.push(move)
            score = _search(board, depth - 1, -10**9, 10**9)
            board.pop()
            if score > best_score:
                best_score = score
                best_move = move
    else:
        best_score = 10**9
        for move in moves:
            board.push(move)
            score = _search(board, depth - 1, -10**9, 10**9)
            board.pop()
            if score < best_score:
                best_score = score
                best_move = move
    return best_move
