"""Naive Bayes (Gaussian 1D) plugin for Algorithm Atlas."""
from __future__ import annotations

import math
import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


def _gaussian_pdf(x: float, mean: float, var: float) -> float:
    if var < 1e-9:
        return 1.0 if abs(x - mean) < 1e-6 else 0.0
    return math.exp(-((x - mean) ** 2) / (2 * var)) / math.sqrt(2 * math.pi * var)


def _generate_data(rng: random.Random, n: int):
    xs, ys = [], []
    for _ in range(n):
        label = rng.randint(0, 1)
        x = rng.randint(10, 45) if label == 0 else rng.randint(55, 90)
        xs.append(x)
        ys.append(label)
    return xs, ys


class NaiveBayesSimulation(AlgorithmPlugin):
    """Gaussian Naive Bayes binary classifier on 1D features."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="naive-bayes",
            name="Naive Bayes (Gaussian 1D)",
            category="machine-learning",
            visualization_type="ARRAY_BARS",
            description="Binary classification using Gaussian Naive Bayes on 1D features.",
            intuition=(
                "Model each class as a Gaussian (mean, variance). "
                "For a query x: pick class that maximises P(class) × P(x|class)."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(1)",
            tags=("machine-learning", "naive-bayes", "classification", "probability"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("n_samples", 20))
        xs, ys = _generate_data(rng, n)
        q = rng.randint(1, 99)
        class1_idx = frozenset(i for i, y in enumerate(ys) if y == 1)
        return SortState(
            array=tuple(xs),
            comparing=None,
            last_swap=None,
            sorted_indices=class1_idx,
            comparisons=0,
            swaps=0,
            description=f"Naive Bayes: n={n} q={q} seed={params.seed}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        desc = initial_state.description
        n = int(re.search(r"n=(\d+)", desc).group(1))
        q = int(re.search(r"q=(\d+)", desc).group(1))
        seed_val = int(re.search(r"seed=(\d+)", desc).group(1))

        rng = random.Random(seed_val)
        xs, ys = _generate_data(rng, n)
        _ = rng.randint(1, 99)  # consume q draw

        # Separate by class
        xs0 = [x for x, y in zip(xs, ys) if y == 0]
        xs1 = [x for x, y in zip(xs, ys) if y == 1]
        n0, n1 = len(xs0), len(xs1)

        class1_idx = frozenset(i for i, y in enumerate(ys) if y == 1)

        # Step 1: show training data
        yield SortState(
            array=tuple(xs),
            comparing=None,
            last_swap=None,
            sorted_indices=class1_idx,
            comparisons=0,
            swaps=0,
            description=(
                f"Training data: {n0} class-0 points, {n1} class-1 points. "
                f"Query x={q}"
            ),
        )

        # Step 2: compute class-0 stats
        mean0 = sum(xs0) / n0 if n0 else 0.0
        var0 = sum((x - mean0) ** 2 for x in xs0) / n0 if n0 > 1 else 1.0

        yield SortState(
            array=tuple(xs),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(i for i, y in enumerate(ys) if y == 0),
            comparisons=n0,
            swaps=0,
            description=(
                f"Class 0: mean={mean0:.1f} var={var0:.1f} "
                f"prior={n0}/{n}"
            ),
        )

        # Step 3: compute class-1 stats
        mean1 = sum(xs1) / n1 if n1 else 0.0
        var1 = sum((x - mean1) ** 2 for x in xs1) / n1 if n1 > 1 else 1.0

        yield SortState(
            array=tuple(xs),
            comparing=None,
            last_swap=None,
            sorted_indices=class1_idx,
            comparisons=n0 + n1,
            swaps=0,
            description=(
                f"Class 1: mean={mean1:.1f} var={var1:.1f} "
                f"prior={n1}/{n}"
            ),
        )

        # Step 4: compute likelihoods for query
        p0 = (n0 / n) * _gaussian_pdf(q, mean0, var0)
        p1 = (n1 / n) * _gaussian_pdf(q, mean1, var1)
        pred = 1 if p1 > p0 else 0

        yield SortState(
            array=tuple(xs),
            comparing=None,
            last_swap=None,
            sorted_indices=class1_idx,
            comparisons=n,
            swaps=pred,
            description=(
                f"P(0|x={q})∝{p0:.4f}  P(1|x={q})∝{p1:.4f} "
                f"→ predicted class {pred}"
            ),
        )

        return SortState(
            array=tuple(xs),
            comparing=None,
            last_swap=None,
            sorted_indices=class1_idx,
            comparisons=n,
            swaps=pred,
            description=(
                f"Naive Bayes done: q={q} → class {pred} "
                f"(score0={p0:.4f}, score1={p1:.4f})"
            ),
        )
