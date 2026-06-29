"""Gradient Descent plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

# Minimize f(x) = (x - target)^2 + noise
# Represent x and f(x) as scaled integers for SortState

SCALE = 10          # display units per real unit
N_BARS = 32         # number of x positions to display as the loss landscape
X_MIN, X_MAX = -8.0, 8.0


def _func(x: float, a: float, b: float, c: float) -> float:
    """Quadratic f(x) = a*(x-b)^2 + c."""
    return a * (x - b) ** 2 + c


def _grad(x: float, a: float, b: float) -> float:
    return 2 * a * (x - b)


def _make_landscape(a: float, b: float, c: float) -> list[int]:
    """Sample f(x) at N_BARS equally spaced x values, scaled to [1, 50]."""
    xs = [X_MIN + (X_MAX - X_MIN) * i / (N_BARS - 1) for i in range(N_BARS)]
    vals = [_func(x, a, b, c) for x in xs]
    v_min, v_max = min(vals), max(vals)
    span = v_max - v_min or 1.0
    return [max(1, int(1 + 49 * (v - v_min) / span)) for v in vals]


def _x_to_bar(x: float) -> int:
    frac = (x - X_MIN) / (X_MAX - X_MIN)
    return max(0, min(N_BARS - 1, int(frac * (N_BARS - 1))))


class GradientDescentSimulation(AlgorithmPlugin):
    """1D gradient descent on a quadratic loss landscape."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="gradient-descent",
            name="Gradient Descent",
            category="machine-learning",
            visualization_type="ARRAY_BARS",
            description="Minimize f(x) = a(x−b)² + c by stepping opposite the gradient.",
            intuition=(
                "Compute slope f'(x) at current x. "
                "Update x ← x − α·f'(x). "
                "Repeat until |f'(x)| < ε or max iterations reached."
            ),
            complexity_time_best="O(1/ε)",
            complexity_time_average="O(1/ε)",
            complexity_time_worst="O(1/ε)",
            complexity_space="O(1)",
            tags=("machine-learning", "gradient-descent", "optimization"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        a = rng.uniform(0.5, 2.0)
        b = rng.uniform(-4.0, 4.0)      # true minimum
        c = rng.uniform(0.0, 10.0)
        lr = int(params.inputs.get("learning_rate_x10", 2)) / 10.0
        x0 = rng.uniform(-6.0, 6.0)    # starting point

        landscape = _make_landscape(a, b, c)
        bar = _x_to_bar(x0)

        return SortState(
            array=tuple(landscape),
            comparing=(bar, bar),
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=int(x0 * SCALE),
            description=(
                f"GD: a={a:.2f} b={b:.2f} c={c:.2f} lr={lr} x0={x0:.2f}"
            ),
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        # Parse params from description
        desc = initial_state.description
        parts = desc.split()
        a = float(parts[1].split("=")[1])
        b = float(parts[2].split("=")[1])
        c = float(parts[3].split("=")[1])
        lr = float(parts[4].split("=")[1])
        x = initial_state.swaps / SCALE

        landscape = list(initial_state.array)
        max_iters = 40
        eps = 1e-4

        for it in range(max_iters):
            g = _grad(x, a, b)
            fx = _func(x, a, b, c)
            bar = _x_to_bar(x)

            yield SortState(
                array=tuple(landscape),
                comparing=(bar, bar),
                last_swap=(bar, _x_to_bar(b)),
                sorted_indices=frozenset(),
                comparisons=it,
                swaps=int(x * SCALE),
                description=(
                    f"Iter {it}: x={x:.4f} f(x)={fx:.4f} grad={g:.4f}"
                ),
            )

            if abs(g) < eps:
                break
            x = x - lr * g

        final_fx = _func(x, a, b, c)
        return SortState(
            array=tuple(landscape),
            comparing=None,
            last_swap=(_x_to_bar(x), _x_to_bar(b)),
            sorted_indices=frozenset([_x_to_bar(x)]),
            comparisons=max_iters,
            swaps=int(x * SCALE),
            description=f"Converged: x={x:.4f} f(x)={final_fx:.4f} (min at b={b:.2f})",
        )
