"""
Birthday Paradox — Algorithm Atlas Plugin

Simulates the birthday problem: in a group of n people, what is the probability
that at least two share a birthday? Famously, only 23 people are needed for
a >50% chance.

The simulation runs many trials at the configured group size, and also computes
empirical collision probability for group sizes 1..50 to build the histogram.
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


def _true_collision_prob(group_size: int) -> float:
    """Analytical P(at least one collision) for given group size."""
    if group_size >= 365:
        return 1.0
    prob_no_collision = 1.0
    for i in range(group_size):
        prob_no_collision *= (365 - i) / 365
    return 1.0 - prob_no_collision


class BirthdayParadox:
    """Birthday paradox simulation."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="birthday-paradox",
            name="Birthday Paradox",
            category="probability",
            visualization_type="PROBABILITY_SPACE",
            description=(
                "Simulates the birthday problem across many trials. For a group of "
                "23 people, there is already a >50% chance that two share a birthday — "
                "far higher than most people intuit. The histogram shows collision "
                "probability across group sizes 1 to 50."
            ),
            intuition=(
                "With 23 people in a room there are 253 possible pairs of birthdays "
                "to compare — not 23. Each pair has a small chance of matching, and "
                "collectively they push the collision probability past 50%."
            ),
            complexity_time_best="O(trials × group_size)",
            complexity_time_average="O(trials × group_size)",
            complexity_time_worst="O(trials × group_size)",
            complexity_space="O(group_size)",
            tags=("probability", "birthday-paradox", "simulation", "combinatorics", "collision"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> ProbabilityState:
        trials = int(params.inputs.get("trials", 1000))
        group_size = int(params.inputs.get("group_size", 23))
        seed = int(params.inputs.get("seed", 42))
        true_val = _true_collision_prob(group_size)
        # histogram_bins: group sizes 1..50 (50 bins)
        bins = tuple(float(i) for i in range(1, 51))
        return ProbabilityState(
            samples=(float(seed), float(group_size)),
            histogram_bins=bins,
            histogram_counts=tuple(0 for _ in range(50)),
            trial=0,
            total_trials=trials,
            estimate=0.0,
            true_value=round(true_val, 6),
            path_x=(),
            path_y=(),
            description=(
                f"Simulating {trials} groups of size {group_size}. "
                f"True P(collision)={true_val:.4f}"
            ),
        )

    def steps(
        self,
        initial_state: ProbabilityState,
    ) -> Generator[ProbabilityState, None, ProbabilityState]:
        trials = initial_state.total_trials
        group_size = int(initial_state.samples[1]) if len(initial_state.samples) > 1 else 23
        seed = int(initial_state.samples[0]) if initial_state.samples else 42
        rng = random.Random(seed)

        true_val = _true_collision_prob(group_size)

        # Pre-compute empirical collision probs for group sizes 1..50
        # We'll use the rng to simulate 200 mini-trials per group size once
        mini_trials = 200
        empirical_by_size: list[float] = []
        for gs in range(1, 51):
            hits = 0
            for _ in range(mini_trials):
                birthdays = [rng.randint(1, 365) for _ in range(gs)]
                if len(set(birthdays)) < gs:
                    hits += 1
            empirical_by_size.append(hits / mini_trials)

        # histogram_counts = empirical collision rate * 1000 (scaled to int counts)
        hist_counts = tuple(int(round(p * 1000)) for p in empirical_by_size)
        bins = tuple(float(i) for i in range(1, 51))

        # Now run the main trials at the configured group_size
        collisions = 0
        for trial in range(1, trials + 1):
            birthdays = [rng.randint(1, 365) for _ in range(group_size)]
            if len(set(birthdays)) < group_size:
                collisions += 1

            estimate = collisions / trial

            if trial % 20 == 0 or trial == trials:
                yield ProbabilityState(
                    samples=(),
                    histogram_bins=bins,
                    histogram_counts=hist_counts,
                    trial=trial,
                    total_trials=trials,
                    estimate=estimate,
                    true_value=round(true_val, 6),
                    path_x=(),
                    path_y=(),
                    description=(
                        f"Trial {trial}: {collisions} collisions in group_size={group_size}. "
                        f"P̂={estimate:.4f}, true={true_val:.4f}"
                    ),
                )

        estimate = collisions / trials
        return ProbabilityState(
            samples=(),
            histogram_bins=bins,
            histogram_counts=hist_counts,
            trial=trials,
            total_trials=trials,
            estimate=estimate,
            true_value=round(true_val, 6),
            path_x=(),
            path_y=(),
            description=(
                f"Done — {collisions}/{trials} groups had a collision. "
                f"P̂={estimate:.4f}, analytical={true_val:.4f}"
            ),
        )
