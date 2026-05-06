You are MiniMax running inside a constrained AutoResearch loop.

Objective: improve the chess bot's estimated Elo.

Rules:
- Return exactly one unified diff patch.
- You may edit only these files: bot/config.py, bot/evaluate.py, bot/move_ordering.py, bot/search.py.
- Do not edit forbidden files: .env, .env.example, README.md, notebooks/workshop.ipynb, pyproject.toml, requirements.txt, setup.py, workshop.ipynb.
- Do not edit paths under these prefixes: eval/, tournament/, autoresearch_loop/, autoresearch_chess/evaluator.py, autoresearch_chess/tournament.py, autoresearch_chess/elo.py, autoresearch_chess/minimax_client.py, artifacts/, tests/.
- Do not add dependencies.
- Do not use network, subprocess, filesystem tricks, or opponent/seed special cases.
- Keep the bot legal and fast.
- Optimize general chess strength through evaluation/search heuristics.

Scoring:
- The evaluator reports estimated Elo from fixed local matches.
- Current best estimated Elo: 1163.4.
- Baseline estimated Elo: 629.6.

Recent history:
```json
[
  {
    "iteration": 1,
    "accepted": true,
    "candidate_elo": 1163.4,
    "best_elo": 1163.4,
    "reasons": []
  }
]
```

Editable files:
### bot/config.py
```python
SEARCH_DEPTH = 2
MATERIAL_WEIGHT = 1.0
MOBILITY_WEIGHT = 2.0
KING_SAFETY_WEIGHT = 0.0
USE_PIECE_SQUARES = True
CAPTURE_FIRST = True

```

### bot/evaluate.py
```python
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


```

### bot/move_ordering.py
```python
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


```

### bot/search.py
```python
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


```

Return only the unified diff patch.
