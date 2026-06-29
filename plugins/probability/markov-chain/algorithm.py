"""
Markov Chain Weather Model — Algorithm Atlas Plugin

A simple 3-state Markov chain: Sunny (0), Cloudy (1), Rainy (2).
The simulation runs the chain and tracks state frequencies, converging
to the stationary distribution of the transition matrix.
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

# Transition matrix: T[i][j] = P(next=j | current=i)
# Rows: Sunny, Cloudy, Rainy
TRANSITION = [
    [0.7, 0.2, 0.1],   # from Sunny
    [0.3, 0.4, 0.3],   # from Cloudy
    [0.2, 0.3, 0.5],   # from Rainy
]

STATE_NAMES = ["Sunny", "Cloudy", "Rainy"]

# Stationary distribution (solved analytically via balance equations)
# π = π × T  →  πS=0.4828..., πC=0.2931..., πR=0.2241...
# Exact: solve the linear system
def _stationary() -> tuple[float, float, float]:
    """Compute stationary distribution by power iteration."""
    pi = [1 / 3, 1 / 3, 1 / 3]
    for _ in range(1000):
        new_pi = [0.0, 0.0, 0.0]
        for j in range(3):
            for i in range(3):
                new_pi[j] += pi[i] * TRANSITION[i][j]
        pi = new_pi
    return tuple(pi)  # type: ignore[return-value]


_STATIONARY = _stationary()


class MarkovChain:
    """Simple weather Markov chain simulation."""

    def metadata(self) -> AlgorithmMetadata:
        stat_sunny = _STATIONARY[0]
        return AlgorithmMetadata(
            slug="markov-chain",
            name="Markov Chain Weather Model",
            category="probability",
            visualization_type="PROBABILITY_SPACE",
            description=(
                "Simulates a 3-state Markov chain (Sunny/Cloudy/Rainy) with a fixed "
                "transition matrix. Tracks empirical state frequencies and shows them "
                "converging to the stationary distribution."
            ),
            intuition=(
                "A Markov chain has no memory: tomorrow's weather depends only on "
                "today's. After many steps, the fraction of time in each state "
                "converges to a fixed stationary distribution regardless of starting state."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(1)",
            tags=("probability", "markov-chain", "simulation", "stationary-distribution", "stochastic"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> ProbabilityState:
        steps = int(params.inputs.get("steps", 200))
        seed = int(params.inputs.get("seed", 42))
        stat_sunny = _STATIONARY[0]
        return ProbabilityState(
            samples=(float(seed),),
            histogram_bins=(0.0, 1.0, 2.0),
            histogram_counts=(0, 0, 0),
            trial=0,
            total_trials=steps,
            estimate=0.0,
            true_value=round(stat_sunny, 6),
            path_x=(),
            path_y=(),
            description=(
                f"Starting in Sunny state. Stationary P(Sunny)={stat_sunny:.4f}. "
                f"Running {steps} steps."
            ),
        )

    def steps(
        self,
        initial_state: ProbabilityState,
    ) -> Generator[ProbabilityState, None, ProbabilityState]:
        steps = initial_state.total_trials
        seed = int(initial_state.samples[0]) if initial_state.samples else 42
        rng = random.Random(seed)

        counts = [0, 0, 0]  # Sunny, Cloudy, Rainy
        state = 0  # start Sunny
        stat_sunny = _STATIONARY[0]

        for step in range(1, steps + 1):
            counts[state] += 1
            freq_sunny = counts[0] / step

            yield ProbabilityState(
                samples=(float(state),),
                histogram_bins=(0.0, 1.0, 2.0),
                histogram_counts=tuple(counts),
                trial=step,
                total_trials=steps,
                estimate=freq_sunny,
                true_value=round(stat_sunny, 6),
                path_x=(),
                path_y=(),
                description=(
                    f"Step {step}: {STATE_NAMES[state]}. "
                    f"Freq Sunny={freq_sunny:.3f} (target {stat_sunny:.3f})"
                ),
            )

            # Transition
            row = TRANSITION[state]
            r = rng.random()
            cumul = 0.0
            next_state = 2
            for j, p in enumerate(row):
                cumul += p
                if r < cumul:
                    next_state = j
                    break
            state = next_state

        counts[state] += 1
        freq_sunny = counts[0] / steps
        return ProbabilityState(
            samples=(float(state),),
            histogram_bins=(0.0, 1.0, 2.0),
            histogram_counts=tuple(counts),
            trial=steps,
            total_trials=steps,
            estimate=freq_sunny,
            true_value=round(stat_sunny, 6),
            path_x=(),
            path_y=(),
            description=(
                f"Chain complete. Empirical P(Sunny)={freq_sunny:.4f}, "
                f"theoretical={stat_sunny:.4f}"
            ),
        )
