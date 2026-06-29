"""Logistic Regression plugin for Algorithm Atlas."""
from __future__ import annotations

import math
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_LR = 3.0
_ITERS = 20
_THRESHOLD = 50  # points below this are class 0, above class 1


def _sigmoid(z):
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


def _generate_data(rng, n):
    xs, ys = [], []
    for _ in range(n // 2):
        xs.append(rng.randint(10, 45))
        ys.append(0)
    for _ in range(n - n // 2):
        xs.append(rng.randint(55, 90))
        ys.append(1)
    return xs, ys


class LogisticRegressionSimulation(AlgorithmPlugin):
    """Logistic regression trained with gradient descent."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="logistic-regression",
            name="Logistic Regression (Gradient Descent)",
            category="machine-learning",
            visualization_type="ARRAY_BARS",
            description="Train a binary logistic classifier on 1D data with gradient descent.",
            intuition=(
                "P(y=1|x) = sigmoid(w·x + b). "
                "Loss = cross-entropy. "
                "Gradient updates push predictions toward correct labels."
            ),
            complexity_time_best="O(n·iters)",
            complexity_time_average="O(n·iters)",
            complexity_time_worst="O(n·iters)",
            complexity_space="O(n)",
            tags=("machine-learning", "logistic-regression", "gradient-descent", "classification"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        import random
        n = int(params.inputs.get("size", 20))
        rng = random.Random(params.seed)
        xs, ys = _generate_data(rng, n)
        xs_str = ",".join(map(str, xs))
        ys_str = ",".join(map(str, ys))
        # Initial predictions: all 0.5 → scaled to 50
        return SortState(
            array=tuple([50] * n),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"LogReg n={n} seed={params.seed} xs={xs_str} ys={ys_str}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        desc = initial_state.description
        n = int(re.search(r"n=(\d+)", desc).group(1))
        xs_str = re.search(r"xs=([0-9,]+)", desc).group(1)
        ys_str = re.search(r"ys=([0-9,]+)", desc).group(1)
        xs = list(map(int, xs_str.split(",")))
        ys = list(map(int, ys_str.split(",")))

        xs_norm = [x / 100.0 for x in xs]  # normalize to [0.1, 0.9] range
        w = 0.0
        b = 0.0

        for iteration in range(_ITERS):
            preds = [_sigmoid(w * x + b) for x in xs_norm]
            loss = -sum(
                y * math.log(max(p, 1e-15)) + (1 - y) * math.log(max(1 - p, 1e-15))
                for y, p in zip(ys, preds)
            ) / n

            dw = sum((p - y) * x for p, y, x in zip(preds, ys, xs_norm)) / n
            db = sum(p - y for p, y in zip(preds, ys)) / n

            w -= _LR * dw
            b -= _LR * db

            # Scaled predictions: 1 (class 0 certain) to 99 (class 1 certain)
            scaled = tuple(max(1, min(99, int(p * 99))) for p in preds)
            correct = frozenset(i for i, (p, y) in enumerate(zip(preds, ys))
                                if round(p) == y)
            yield SortState(
                array=scaled,
                comparing=None,
                last_swap=None,
                sorted_indices=correct,
                comparisons=iteration + 1,
                swaps=len(correct),
                description=(
                    f"Iter {iteration + 1}/{_ITERS}: "
                    f"w={w:.3f} b={b:.2f} loss={loss:.4f} "
                    f"acc={len(correct)}/{n}"
                ),
            )

        preds = [_sigmoid(w * x + b) for x in xs_norm]
        correct = frozenset(i for i, (p, y) in enumerate(zip(preds, ys))
                            if round(p) == y)
        scaled = tuple(max(1, min(99, int(p * 99))) for p in preds)
        return SortState(
            array=scaled,
            comparing=None,
            last_swap=None,
            sorted_indices=correct,
            comparisons=_ITERS,
            swaps=len(correct),
            description=(
                f"Done: w={w:.3f} b={b:.2f} acc={len(correct)}/{n}"
            ),
        )
