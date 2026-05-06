from __future__ import annotations

import chess

from . import config


PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

CENTER_SQUARES = {chess.D4, chess.E4, chess.D5, chess.E5}


def material_score(board: chess.Board) -> int:
    score = 0
    for piece_type, value in PIECE_VALUES.items():
        score += len(board.pieces(piece_type, chess.WHITE)) * value
        score -= len(board.pieces(piece_type, chess.BLACK)) * value
    return score


def piece_square_score(board: chess.Board) -> int:
    score = 0
    for square, piece in board.piece_map().items():
        file_idx = chess.square_file(square)
        rank_idx = chess.square_rank(square)
        center_bonus = 14 - (abs(file_idx - 3.5) + abs(rank_idx - 3.5)) * 4
        if square in CENTER_SQUARES and piece.piece_type in {chess.PAWN, chess.KNIGHT, chess.BISHOP}:
            center_bonus += 12
        score += int(center_bonus) if piece.color == chess.WHITE else -int(center_bonus)
    return score


def mobility_score(board: chess.Board) -> int:
    if board.is_game_over():
        return 0
    turn = board.turn
    board.turn = chess.WHITE
    white_moves = board.legal_moves.count()
    board.turn = chess.BLACK
    black_moves = board.legal_moves.count()
    board.turn = turn
    return white_moves - black_moves


def king_safety_score(board: chess.Board) -> int:
    score = 0
    for color, sign in ((chess.WHITE, 1), (chess.BLACK, -1)):
        king_square = board.king(color)
        if king_square is None:
            continue
        attackers = board.attackers(not color, king_square)
        defenders = board.attackers(color, king_square)
        score += sign * (len(defenders) * 8 - len(attackers) * 20)
    return score


def evaluate(board: chess.Board) -> int:
    if board.is_checkmate():
        return -100_000 if board.turn == chess.WHITE else 100_000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = int(config.MATERIAL_WEIGHT * material_score(board))
    if config.USE_PIECE_SQUARES:
        score += piece_square_score(board)
    score += int(config.MOBILITY_WEIGHT * mobility_score(board))
    score += int(config.KING_SAFETY_WEIGHT * king_safety_score(board))
    return score
