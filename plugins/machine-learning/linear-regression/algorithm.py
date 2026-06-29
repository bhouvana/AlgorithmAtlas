"""Linear Regression via Batch Gradient Descent plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

MAX_ITERS = 30
LR = 0.01
SCALE = 10


def _mse(xs: List[float], ys: List[float], w: float, b: float) -> float:
    n = len(xs)
    return sum((w * xs[i] + b - ys[i]) ** 2 for i in range(n)) / n


def _grads(xs, ys, w, b):
    n = len(xs)
    dw = 2 * sum((w * xs[i] + b - ys[i]) * xs[i] for i in range(n)) / n
    db = 2 * sum((w * xs[i] + b - ys[i]) for i in range(n)) / n
    return dw, db


class LinearRegressionSimulation(AlgorithmPlugin):
    """Linear Regression y = wx + b via batch gradient descent."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="linear-regression",
            name="Linear Regression (Gradient Descent)",
            category="machine-learning",
            visualization_type="ARRAY_BARS",
            description="Fit a line to noisy data by minimizing mean-squared error with gradient descent.",
            intuition=(
                "MSE loss is convex. Gradients ∂L/∂w and ∂L/∂b point uphill. "
                "Subtract a fraction of each gradient at every iteration."
            ),
            complexity_time_best="O(nT)",
            complexity_time_average="O(nT)",
            complexity_time_worst="O(nT)",
            complexity_space="O(n)",
            tags=("machine-learning", "linear-regression", "gradient-descent"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("sample_count", 10))
        true_w = rng.uniform(0.5, 2.0)
        true_b = rng.uniform(-5.0, 5.0)
        # xs in [0, 1], ys with noise
        xs = [rng.uniform(0, 1) for _ in range(n)]
        ys = [true_w * x + true_b + rng.gauss(0, 0.1) for x in xs]

        # Normalize ys to [1, 50] for display
        y_min, y_max = min(ys), max(ys)
        span = y_max - y_min or 1.0
        display = [max(1, int(1 + 49 * (y - y_min) / span)) for y in ys]

        return SortState(
            array=tuple(display),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=(
                f"LinReg n={n} seed={params.seed} true_w={true_w:.3f} true_b={true_b:.3f} "
                f"w=0.0 b=0.0"
            ),
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        desc = initial_state.description
        n = int(re.search(r"n=(\d+)", desc).group(1))
        seed_val = int(re.search(r"seed=(\d+)", desc).group(1))
        rng = random.Random(seed_val)
        true_w = float(re.search(r"true_w=([\d.\-]+)", desc).group(1))
        true_b = float(re.search(r"true_b=([\d.\-]+)", desc).group(1))
        xs = [rng.uniform(0, 1) for _ in range(n)]
        ys = [true_w * x + true_b + rng.gauss(0, 0.1) for x in xs]

        display = list(initial_state.array)
        w, b = 0.0, 0.0
        prev_loss = _mse(xs, ys, w, b)

        for it in range(MAX_ITERS):
            loss = _mse(xs, ys, w, b)
            dw, db = _grads(xs, ys, w, b)

            # Highlight worst-predicted sample
            errors = [abs(w * xs[i] + b - ys[i]) for i in range(n)]
            worst = errors.index(max(errors))

            yield SortState(
                array=tuple(display),
                comparing=(worst, worst),
                last_swap=None,
                sorted_indices=frozenset(),
                comparisons=it,
                swaps=int(w * SCALE),
                description=f"Iter {it}: w={w:.3f} b={b:.3f} loss={loss:.4f} ∂w={dw:.4f}",
            )

            w -= LR * dw
            b -= LR * db
            prev_loss = loss

        final_loss = _mse(xs, ys, w, b)
        return SortState(
            array=tuple(display),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=MAX_ITERS,
            swaps=int(w * SCALE),
            description=f"Fitted: w={w:.3f} b={b:.3f} loss={final_loss:.4f} (true w={true_w:.3f})",
        )
