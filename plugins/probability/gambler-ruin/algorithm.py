"""
Gambler's Ruin — Algorithm Atlas Plugin

Simulates the classic gambler's ruin problem. A gambler starts with $10 and
plays a sequence of fair coin flips (probability p of winning each flip),
betting $1 each time. The game ends when they either go broke ($0) or reach
the target ($20).

The theoretical probability of reaching the target starting at wealth k is:
  - If p == 0.5: P(win) = k / target = 10/20 = 0.5
  - If p != 0.5: P(win) = (1 - (q/p)^k) / (1 - (q/p)^target)

Yields one frame per completed game (trial), showing wealth trajectory of
the most recently completed game.
"""
from __future__ import annotations

import math
import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    ProbabilityState,
    SimulationParams,
)

INITIAL_WEALTH = 10
TARGET_WEALTH = 20


def _true_win_prob(p: float, k: int = INITIAL_WEALTH, n: int = TARGET_WEALTH) -> float:
    """Analytical probability of reaching target n starting at k."""
    if abs(p - 0.5) < 1e-10:
        return k / n
    q = 1.0 - p
    ratio = q / p
    return (1.0 - ratio ** k) / (1.0 - ratio ** n)


class GamblerRuin:
    """Gambler's ruin simulation."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="gambler-ruin",
            name="Gambler's Ruin",
            category="probability",
            visualization_type="PROBABILITY_SPACE",
            description=(
                "Simulates the gambler's ruin problem: a gambler starts with $10 "
                "and plays coin flips (winning or losing $1) until reaching $20 "
                "(win) or $0 (bust). Tracks empirical win rate vs. the analytical "
                "probability of ruin."
            ),
            intuition=(
                "Even with a 50/50 coin, a gambler with finite wealth playing "
                "against an infinitely rich house (or a fixed target) is guaranteed "
                "to eventually go broke. Finite targets make the game fair, but any "
                "slight disadvantage is ruinous in the long run."
            ),
            complexity_time_best="O(trials)",
            complexity_time_average="O(trials × n²)",
            complexity_time_worst="O(∞)",
            complexity_space="O(n)",
            tags=("probability", "gambler-ruin", "simulation", "random-walk", "martingale"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> ProbabilityState:
        trials = int(params.inputs.get("trials", 500))
        p = float(params.inputs.get("p", 0.5))
        seed = int(params.inputs.get("seed", 42))
        true_val = _true_win_prob(p)
        return ProbabilityState(
            samples=(float(seed), p),
            histogram_bins=(0.0, 20.0),
            histogram_counts=(0, 0),
            trial=0,
            total_trials=trials,
            estimate=0.0,
            true_value=round(true_val, 6),
            path_x=(),
            path_y=(),
            description=(
                f"Gambler starts with ${INITIAL_WEALTH}, target ${TARGET_WEALTH}, "
                f"p={p:.2f}. True P(win)={true_val:.4f}. Running {trials} games."
            ),
        )

    def steps(
        self,
        initial_state: ProbabilityState,
    ) -> Generator[ProbabilityState, None, ProbabilityState]:
        trials = initial_state.total_trials
        seed = int(initial_state.samples[0]) if initial_state.samples else 42
        p = float(initial_state.samples[1]) if len(initial_state.samples) > 1 else 0.5
        rng = random.Random(seed)

        true_val = _true_win_prob(p)
        wins = 0
        busts = 0
        last_path: list[float] = []

        for trial in range(1, trials + 1):
            wealth = INITIAL_WEALTH
            path: list[float] = [float(wealth)]

            while 0 < wealth < TARGET_WEALTH:
                if rng.random() < p:
                    wealth += 1
                else:
                    wealth -= 1
                path.append(float(wealth))

            won = wealth == TARGET_WEALTH
            if won:
                wins += 1
            else:
                busts += 1

            last_path = path
            estimate = wins / trial

            yield ProbabilityState(
                samples=(),
                histogram_bins=(0.0, 20.0),
                histogram_counts=(wins, busts),
                trial=trial,
                total_trials=trials,
                estimate=estimate,
                true_value=round(true_val, 6),
                path_x=tuple(float(i) for i in range(len(last_path))),
                path_y=tuple(last_path),
                description=(
                    f"Game {trial}: {'WON' if won else 'BUST'} "
                    f"after {len(path)-1} flips. "
                    f"Win rate={estimate:.4f} (true={true_val:.4f})"
                ),
            )

        estimate = wins / trials
        return ProbabilityState(
            samples=(),
            histogram_bins=(0.0, 20.0),
            histogram_counts=(wins, busts),
            trial=trials,
            total_trials=trials,
            estimate=estimate,
            true_value=round(true_val, 6),
            path_x=tuple(float(i) for i in range(len(last_path))),
            path_y=tuple(last_path),
            description=(
                f"Simulation complete. {wins}/{trials} games won. "
                f"Empirical P(win)={estimate:.4f}, analytical={true_val:.4f}"
            ),
        )
