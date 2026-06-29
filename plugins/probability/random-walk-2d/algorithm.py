"""
2D Random Walk — Algorithm Atlas Plugin

A particle starts at the origin and takes unit steps in one of four cardinal
directions (N, E, S, W) chosen uniformly at random. Shows how diffusion
emerges from simple random choices.
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


class RandomWalk2d:
    """2D random walk on the integer lattice."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="random-walk-2d",
            name="2D Random Walk",
            category="probability",
            visualization_type="PROBABILITY_SPACE",
            description=(
                "A particle starts at the origin and steps randomly in one of four "
                "cardinal directions at each tick. Demonstrates diffusion: after n "
                "steps the expected distance from the origin is √n."
            ),
            intuition=(
                "Imagine a drunk person wandering a city grid, turning randomly at "
                "every intersection. On average they drift √n blocks from home after "
                "n steps — surprisingly far, but never purposeful."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("probability", "random-walk", "simulation", "diffusion", "stochastic"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> ProbabilityState:
        steps = int(params.inputs.get("steps", 500))
        seed = int(params.inputs.get("seed", 42))
        # Encode seed in samples as a sentinel so steps() can recover it
        return ProbabilityState(
            samples=(float(seed),),
            histogram_bins=(0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0),
            histogram_counts=(0, 0, 0, 0, 0, 0),
            trial=0,
            total_trials=steps,
            estimate=0.0,
            true_value=0.0,   # updated each step: sqrt(step)
            path_x=(0.0,),
            path_y=(0.0,),
            description=f"Starting 2D random walk for {steps} steps.",
        )

    def steps(
        self,
        initial_state: ProbabilityState,
    ) -> Generator[ProbabilityState, None, ProbabilityState]:
        steps = initial_state.total_trials
        seed = int(initial_state.samples[0]) if initial_state.samples else 42
        rng = random.Random(seed)

        DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # N, S, E, W
        WINDOW = 200

        # Histogram: distance buckets 0-5, 5-10, 10-15, 15-20, 20-25, 25-30, 30+
        BIN_EDGES = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
        n_bins = len(BIN_EDGES)  # 7 edges → 7 bins (last is open-ended)
        dist_counts = [0] * n_bins

        x, y = 0, 0
        path_x: list[float] = [0.0]
        path_y: list[float] = [0.0]

        for step in range(1, steps + 1):
            dx, dy = rng.choice(DIRS)
            x += dx
            y += dy

            path_x.append(float(x))
            path_y.append(float(y))
            if len(path_x) > WINDOW:
                path_x.pop(0)
                path_y.pop(0)

            dist = math.sqrt(x * x + y * y)
            # Bin this distance
            bin_idx = min(int(dist // 5), n_bins - 1)
            dist_counts[bin_idx] += 1

            true_val = math.sqrt(step)
            yield ProbabilityState(
                samples=(float(x), float(y)),
                histogram_bins=tuple(BIN_EDGES),
                histogram_counts=tuple(dist_counts),
                trial=step,
                total_trials=steps,
                estimate=dist,
                true_value=true_val,
                path_x=tuple(path_x),
                path_y=tuple(path_y),
                description=(
                    f"Step {step}: pos=({x},{y}), dist={dist:.2f}, "
                    f"expected √{step}={true_val:.2f}"
                ),
            )

        dist = math.sqrt(x * x + y * y)
        return ProbabilityState(
            samples=(float(x), float(y)),
            histogram_bins=tuple(BIN_EDGES),
            histogram_counts=tuple(dist_counts),
            trial=steps,
            total_trials=steps,
            estimate=dist,
            true_value=math.sqrt(steps),
            path_x=tuple(path_x),
            path_y=tuple(path_y),
            description=(
                f"Walk complete — final pos ({x},{y}), "
                f"distance {dist:.2f}, expected {math.sqrt(steps):.2f}"
            ),
        )
