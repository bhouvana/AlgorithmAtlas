"""
Buffon's Needle — Algorithm Atlas Plugin

Estimates π by simulating Buffon's needle experiment. A needle of length l=1
is dropped onto a floor with parallel lines spaced d=2 apart. The probability
that the needle crosses a line is P = 2l / (πd) = 1/π (when l ≤ d).

Thus π ≈ 2 × n_needles / crossings.
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

NEEDLE_LEN = 1.0
LINE_SPACING = 2.0


class BuffonNeedle:
    """Buffon's needle π estimation."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="buffon-needle",
            name="Buffon's Needle",
            category="probability",
            visualization_type="PROBABILITY_SPACE",
            description=(
                "Estimates π by simulating Buffon's 18th-century needle experiment. "
                "A needle of length 1 is dropped randomly on a floor with parallel "
                "lines spaced 2 apart. The crossing probability is 1/π, so "
                "π ≈ 2 × n_needles / crossings."
            ),
            intuition=(
                "Drop a toothpick on a hardwood floor. If the gaps are twice as long "
                "as the toothpick, the fraction of times it crosses a crack encodes π. "
                "Geometry and probability conspire to give you the most famous constant."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(1)",
            tags=("probability", "monte-carlo", "simulation", "pi", "buffon"),
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
            description=f"Ready to drop {n} needles. Estimating π via Buffon.",
        )

    def steps(
        self,
        initial_state: ProbabilityState,
    ) -> Generator[ProbabilityState, None, ProbabilityState]:
        n = initial_state.total_trials
        seed = int(initial_state.samples[0]) if initial_state.samples else 42
        rng = random.Random(seed)

        crossings = 0
        needle_left_x: list[float] = []
        needle_right_x: list[float] = []
        WINDOW = 50

        for trial in range(1, n + 1):
            # y_center: distance from needle center to nearest line (0 .. d/2)
            y_center = rng.uniform(0, LINE_SPACING / 2)
            # angle: needle orientation (0 .. π/2 by symmetry)
            theta = rng.uniform(0, math.pi / 2)
            half_proj = (NEEDLE_LEN / 2) * math.sin(theta)

            crosses = y_center <= half_proj
            if crosses:
                crossings += 1

            # Store left/right x positions of needle for path
            x_center = rng.uniform(0, LINE_SPACING)
            half_x = (NEEDLE_LEN / 2) * math.cos(theta)
            needle_left_x.append(x_center - half_x)
            needle_right_x.append(x_center + half_x)
            if len(needle_left_x) > WINDOW:
                needle_left_x.pop(0)
                needle_right_x.pop(0)

            if trial % 20 == 0 or trial == n:
                estimate = (2.0 * trial / crossings) if crossings > 0 else 0.0
                yield ProbabilityState(
                    samples=(),
                    histogram_bins=(0.0, 1.0),
                    histogram_counts=(crossings, trial - crossings),
                    trial=trial,
                    total_trials=n,
                    estimate=estimate,
                    true_value=math.pi,
                    path_x=tuple(needle_left_x),
                    path_y=tuple(needle_right_x),
                    description=(
                        f"Trial {trial}: {crossings} crossings → "
                        f"π ≈ {estimate:.5f} (error {abs(estimate - math.pi):.5f})"
                    ),
                )

        estimate = (2.0 * n / crossings) if crossings > 0 else 0.0
        return ProbabilityState(
            samples=(),
            histogram_bins=(0.0, 1.0),
            histogram_counts=(crossings, n - crossings),
            trial=n,
            total_trials=n,
            estimate=estimate,
            true_value=math.pi,
            path_x=tuple(needle_left_x),
            path_y=tuple(needle_right_x),
            description=(
                f"Done — {crossings}/{n} crossings. "
                f"π ≈ {estimate:.6f} (true {math.pi:.6f}, "
                f"error {abs(estimate - math.pi):.6f})"
            ),
        )
