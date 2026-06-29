"""
Brownian Motion — Algorithm Atlas Plugin

Simulates 2D Brownian motion (Wiener process) by accumulating independent
Gaussian increments at each step. Uses Box-Muller transform to generate
normal samples from the stdlib random module (no numpy).

The theoretical variance of each coordinate after n steps is n (assuming
unit step variance), so true_value = step_number.
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


def _box_muller(rng: random.Random) -> tuple[float, float]:
    """Generate two independent standard normal samples via Box-Muller."""
    u1 = rng.random()
    u2 = rng.random()
    # Avoid log(0)
    while u1 == 0.0:
        u1 = rng.random()
    mag = math.sqrt(-2.0 * math.log(u1))
    theta = 2.0 * math.pi * u2
    return mag * math.cos(theta), mag * math.sin(theta)


class BrownianMotion:
    """2D Brownian motion via Box-Muller Gaussian increments."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="brownian-motion",
            name="Brownian Motion",
            category="probability",
            visualization_type="PROBABILITY_SPACE",
            description=(
                "Simulates 2D Brownian motion by accumulating independent Gaussian "
                "increments at each time step. The x-coordinate histogram shows the "
                "normal distribution emerging, and the theoretical variance equals "
                "the number of steps."
            ),
            intuition=(
                "Pollen grains on water jitter randomly due to molecular collisions. "
                "Each tiny push is independent. After n steps, the total displacement "
                "is the sum of n random variables — central limit theorem in action."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("probability", "brownian-motion", "simulation", "gaussian", "stochastic"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> ProbabilityState:
        steps = int(params.inputs.get("steps", 300))
        seed = int(params.inputs.get("seed", 42))
        # Histogram: 10 bins over x-position range [-20, 20]
        BIN_WIDTH = 4.0
        bins = tuple(-20.0 + i * BIN_WIDTH for i in range(10))
        return ProbabilityState(
            samples=(float(seed),),
            histogram_bins=bins,
            histogram_counts=tuple(0 for _ in range(10)),
            trial=0,
            total_trials=steps,
            estimate=0.0,
            true_value=0.0,
            path_x=(0.0,),
            path_y=(0.0,),
            description=f"Starting Brownian motion for {steps} steps.",
        )

    def steps(
        self,
        initial_state: ProbabilityState,
    ) -> Generator[ProbabilityState, None, ProbabilityState]:
        steps = initial_state.total_trials
        seed = int(initial_state.samples[0]) if initial_state.samples else 42
        rng = random.Random(seed)

        BIN_EDGES = list(initial_state.histogram_bins)   # [-20, -16, -12, ..., 16]
        N_BINS = len(BIN_EDGES)
        bin_counts = [0] * N_BINS

        x, y = 0.0, 0.0
        x_positions: list[float] = [0.0]
        y_positions: list[float] = [0.0]
        x_samples: list[float] = []   # for variance tracking

        sum_x_sq = 0.0

        for step in range(1, steps + 1):
            dx, dy = _box_muller(rng)
            x += dx
            y += dy
            x_positions.append(x)
            y_positions.append(y)
            x_samples.append(x)
            sum_x_sq += x * x

            # Update histogram bin for x
            bin_idx = N_BINS - 1
            for i, edge in enumerate(BIN_EDGES):
                if x < edge + 4.0:   # bin width = 4
                    bin_idx = i
                    break
            bin_idx = max(0, min(bin_idx, N_BINS - 1))
            bin_counts[bin_idx] += 1

            empirical_var = sum_x_sq / step
            true_var = float(step)

            yield ProbabilityState(
                samples=tuple(x_samples[-50:]),
                histogram_bins=tuple(BIN_EDGES),
                histogram_counts=tuple(bin_counts),
                trial=step,
                total_trials=steps,
                estimate=empirical_var,
                true_value=true_var,
                path_x=tuple(x_positions[-200:]),
                path_y=tuple(y_positions[-200:]),
                description=(
                    f"Step {step}: pos=({x:.2f},{y:.2f}), "
                    f"empirical var={empirical_var:.2f}, expected={true_var:.1f}"
                ),
            )

        empirical_var = sum_x_sq / steps
        return ProbabilityState(
            samples=tuple(x_samples[-50:]),
            histogram_bins=tuple(BIN_EDGES),
            histogram_counts=tuple(bin_counts),
            trial=steps,
            total_trials=steps,
            estimate=empirical_var,
            true_value=float(steps),
            path_x=tuple(x_positions[-200:]),
            path_y=tuple(y_positions[-200:]),
            description=(
                f"Brownian motion complete. Final pos=({x:.2f},{y:.2f}), "
                f"x-variance={empirical_var:.2f} (theoretical={steps})"
            ),
        )
