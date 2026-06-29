"""
Monte Carlo Pi Estimation — Algorithm Atlas Plugin

Estimates π by throwing random darts at a unit square and checking
whether they land inside the quarter unit circle. The ratio of hits
to total darts approximates π/4.
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


class MonteCarloPi:
    """Monte Carlo estimation of π using the dart-board method."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="monte-carlo-pi",
            name="Monte Carlo Pi Estimation",
            category="probability",
            visualization_type="PROBABILITY_SPACE",
            description=(
                "Estimates π by randomly throwing darts at a unit square and counting "
                "how many land inside the inscribed quarter circle. The ratio "
                "hits/total ≈ π/4, so π ≈ 4 × hits/total."
            ),
            intuition=(
                "If you throw darts randomly at a square, the fraction that land in "
                "the inscribed circle is proportional to its area (π/4). More darts "
                "means a better estimate of π."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(1)",
            tags=("probability", "monte-carlo", "simulation", "pi", "estimation"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> ProbabilityState:
        n = int(params.inputs.get("n", 2000))
        seed = int(params.inputs.get("seed", 42))
        return ProbabilityState(
            samples=(float(seed),),
            histogram_bins=(0.0, 1.0),
            histogram_counts=(0, 0),
            trial=0,
            total_trials=n,
            estimate=0.0,
            true_value=math.pi,
            path_x=(),
            path_y=(),
            description=f"Ready to throw {n} darts. Estimating π.",
        )

    def steps(
        self,
        initial_state: ProbabilityState,
    ) -> Generator[ProbabilityState, None, ProbabilityState]:
        n = initial_state.total_trials
        seed = int(initial_state.samples[0]) if initial_state.samples else 42
        rng = random.Random(seed)

        hits = 0
        dart_x: list[float] = []
        dart_y: list[float] = []
        WINDOW = 50  # keep last N dart positions

        for trial in range(1, n + 1):
            x = rng.random()
            y = rng.random()
            in_circle = (x * x + y * y) <= 1.0
            if in_circle:
                hits += 1

            dart_x.append(x)
            dart_y.append(y)
            if len(dart_x) > WINDOW:
                dart_x.pop(0)
                dart_y.pop(0)

            if trial % 20 == 0 or trial == n:
                estimate = 4.0 * hits / trial
                yield ProbabilityState(
                    samples=tuple(dart_x),
                    histogram_bins=(0.0, 1.0),
                    histogram_counts=(hits, trial - hits),
                    trial=trial,
                    total_trials=n,
                    estimate=estimate,
                    true_value=math.pi,
                    path_x=tuple(dart_x),
                    path_y=tuple(dart_y),
                    description=(
                        f"Trial {trial}: {hits} hits / {trial} total → "
                        f"π ≈ {estimate:.5f} (error {abs(estimate - math.pi):.5f})"
                    ),
                )

        estimate = 4.0 * hits / n
        return ProbabilityState(
            samples=tuple(dart_x),
            histogram_bins=(0.0, 1.0),
            histogram_counts=(hits, n - hits),
            trial=n,
            total_trials=n,
            estimate=estimate,
            true_value=math.pi,
            path_x=tuple(dart_x),
            path_y=tuple(dart_y),
            description=(
                f"Done — {hits}/{n} darts hit the circle. "
                f"π ≈ {estimate:.6f} (true: {math.pi:.6f}, "
                f"error: {abs(estimate - math.pi):.6f})"
            ),
        )
