"""Perceptron Learning Algorithm plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


def _make_linearly_separable(rng: random.Random, n: int) -> Tuple[List, List]:
    """
    Generate 1D linearly separable data.
    Class -1: points in [0, 40]; Class +1: points in [60, 100].
    Returns (features_scaled, labels) where features_scaled are ints [0..100].
    """
    neg = sorted(rng.randint(5, 40) for _ in range(n // 2))
    pos = sorted(rng.randint(60, 95) for _ in range(n - n // 2))
    xs = neg + pos
    ys = [-1] * len(neg) + [1] * len(pos)
    combined = list(zip(xs, ys))
    rng.shuffle(combined)
    return [c[0] for c in combined], [c[1] for c in combined]


class PerceptronSimulation(AlgorithmPlugin):
    """Rosenblatt Perceptron for 1D binary classification."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="perceptron",
            name="Perceptron Learning Algorithm",
            category="machine-learning",
            visualization_type="ARRAY_BARS",
            description="Learn a linear binary classifier by updating weights on misclassified samples.",
            intuition=(
                "Start with w=0, b=0. For each sample: predict sign(w·x + b). "
                "If wrong: w += lr·y·x, b += lr·y. "
                "Repeat until all correctly classified."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n·T)",
            complexity_time_worst="O(n·T)",
            complexity_space="O(d)",
            tags=("machine-learning", "perceptron", "classification"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("sample_count", 10))
        xs, ys = _make_linearly_separable(rng, n)

        # Display: array = sample feature values; color encodes class
        # sorted_indices = positive-class indices (shown green)
        pos_idx = frozenset(i for i, y in enumerate(ys) if y == 1)

        return SortState(
            array=tuple(xs),
            comparing=None,
            last_swap=None,
            sorted_indices=pos_idx,   # green = class +1, rest = class -1
            comparisons=0,
            swaps=0,   # epoch counter
            description=f"Perceptron n={n} w=0.0 b=0.0 sep=50",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        xs = list(initial_state.array)
        n = len(xs)
        pos_idx = set(initial_state.sorted_indices)
        ys = [1 if i in pos_idx else -1 for i in range(n)]

        w = 0.0
        b = 0.0
        lr = 1.0
        max_epochs = 20
        sep = 50  # decision boundary scaled

        for epoch in range(max_epochs):
            errors = 0
            for i, (xi, yi) in enumerate(zip(xs, ys)):
                x_real = xi / 100.0
                pred = 1 if (w * x_real + b) >= 0 else -1
                correct = (pred == yi)

                yield SortState(
                    array=tuple(xs),
                    comparing=(i, i),
                    last_swap=None,
                    sorted_indices=frozenset(pos_idx),
                    comparisons=epoch * n + i,
                    swaps=epoch,
                    description=(
                        f"Epoch {epoch} sample {i}: x={xi} y={yi:+d} "
                        f"pred={pred:+d} {'✓' if correct else '✗'} w={w:.2f} b={b:.2f}"
                    ),
                )

                if not correct:
                    w += lr * yi * x_real
                    b += lr * yi
                    errors += 1
                    sep = max(0, min(100, int((-b / w * 100) if w != 0 else 50)))

            if errors == 0:
                break

        return SortState(
            array=tuple(xs),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(pos_idx),
            comparisons=n * max_epochs,
            swaps=max_epochs,
            description=f"Converged: w={w:.3f} b={b:.3f} boundary≈{sep}",
        )
