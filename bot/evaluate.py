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


def _is_passed_pawn(board: chess.Board, square: int, color: chess.Color) -> bool:
    """Check if a pawn at square is passed (no enemy pawns ahead of it)."""
    file_idx = chess.square_file(square)
    rank_idx = chess.square_rank(square)
    
    # Direction the pawn moves (up or down the board)
    direction = 1 if color == chess.WHITE else -1
    
    # Check squares ahead of the pawn
    for check_rank in range(rank_idx + direction, 8 if color == chess.WHITE else -1, direction):
        for check_file in range(max(0, file_idx - 1), min(8, file_idx + 2)):
            check_sq = chess.square(check_file, check_rank)
            if board.piece_at(check_sq) == chess.Piece(chess.PAWN, not color):
                return False
    return True


def passed_pawn_score(board: chess.Board) -> int:
    """Bonus for passed pawns, scales with how close to promotion."""
    score = 0
    for square in board.pieces(chess.PAWN, chess.WHITE):
        if _is_passed_pawn(board, square, chess.WHITE):
            rank = chess.square_rank(square)
            # Scale: closer to promotion = more valuable
            advancement = rank - 1  # rank 1 pawn = 0, rank 7 pawn = 6
            score += 30 + advancement * 25
    for square in board.pieces(chess.PAWN, chess.BLACK):
        if _is_passed_pawn(board, square, chess.BLACK):
            rank = chess.square_rank(square)
            advancement = 6 - rank  # rank 7 pawn = 0, rank 2 pawn = 5
            score -= 30 + advancement * 25
    return score


def king_endgame_activity(board: chess.Board) -> int:
    """Bonus for king centralization in endgame (few pieces remaining)."""
    total_pieces = len(board.piece_map())
    
    # Only meaningful when few pieces remain (12 or fewer, roughly Q+R or less)
    if total_pieces > 12:
        return 0
    
    score = 0
    for color, sign in ((chess.WHITE, 1), (chess.BLACK, -1)):
        king_sq = board.king(color)
        if king_sq is not None:
            # King centralization bonus (king at d4/e4/d5/e5 = max bonus)
            file_dist = abs(chess.square_file(king_sq) - 3.5)
            rank_dist = abs(chess.square_rank(king_sq) - 3.5)
            centrality = 10 - (file_dist + rank_dist) * 2
            score += sign * max(0, centrality) * (12 - total_pieces) // 3
    return score


def _has_king_opposition(white_king_sq: int, black_king_sq: int) -> bool:
    """Check if kings are in direct opposition (one square apart on same line)."""
    file_diff = abs(chess.square_file(white_king_sq) - chess.square_file(black_king_sq))
    rank_diff = abs(chess.square_rank(white_king_sq) - chess.square_rank(black_king_sq))
    
    # Kings are close (within 2 squares)
    if max(file_diff, rank_diff) <= 2:
        # In opposition if aligned on same file or rank with exactly 1 square between
        if file_diff == 0 and rank_diff == 2:
            return True
        if rank_diff == 0 and file_diff == 2:
            return True
        if file_diff == 2 and rank_diff == 2:  # diagonal opposition
            return True
    return False


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
    
    # Endgame-specific evaluations
    score += passed_pawn_score(board)
    score += king_endgame_activity(board)
    
    return score
