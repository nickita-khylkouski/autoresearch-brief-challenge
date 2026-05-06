from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class OpponentScore:
    opponent: str
    anchor_elo: float
    wins: int
    draws: int
    losses: int

    @property
    def games(self) -> int:
        return self.wins + self.draws + self.losses

    @property
    def score(self) -> float:
        if self.games == 0:
            return 0.0
        return (self.wins + 0.5 * self.draws) / self.games


def performance_elo(anchor_elo: float, score: float) -> float:
    bounded = min(0.98, max(0.02, score))
    return anchor_elo + 400.0 * math.log10(bounded / (1.0 - bounded))


def estimate_elo(scores: list[OpponentScore]) -> float:
    weighted_total = 0.0
    total_games = 0
    for item in scores:
        if item.games == 0:
            continue
        weighted_total += performance_elo(item.anchor_elo, item.score) * item.games
        total_games += item.games
    if total_games == 0:
        return 0.0
    return round(weighted_total / total_games, 1)
