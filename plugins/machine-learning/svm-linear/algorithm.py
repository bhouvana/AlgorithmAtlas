"""Linear SVM via subgradient descent plugin for Algorithm Atlas."""
from __future__ import annotations

import math
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_LAMBDA = 0.01   # regularization
_LR = 0.1        # learning rate
_ITERS = 25


def _generate_data(seed):
    """Two linearly separable classes."""
    rng = seed * 1103515245 + 12345
    points = []
    labels = []
    for i in range(12):
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        x1 = (rng % 30) + (40 if i < 6 else 5)   # class +1: x in [40,70], class -1: x in [5,35]
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        x2 = (rng % 25) + 30
        label = 1 if i < 6 else -1
        points.append((x1 / 100.0, x2 / 100.0))
        labels.append(label)
    return points, labels


def _hinge_loss(points, labels, w, b):
    total = 0.0
    for (x1, x2), y in zip(points, labels):
        margin = y * (w[0] * x1 + w[1] * x2 + b)
        total += max(0.0, 1.0 - margin)
    return total / len(points)


def _classify(points, w, b):
    return [1 if (w[0] * x1 + w[1] * x2 + b) >= 0 else -1 for (x1, x2) in points]


class SVMLinearSimulation(AlgorithmPlugin):
    """Linear SVM training via subgradient descent."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="svm-linear",
            name="Linear SVM",
            category="machine-learning",
            visualization_type="ARRAY_BARS",
            description="Train linear SVM with subgradient descent.",
            intuition=(
                "Hinge loss + L2 regularization. "
                "Update: w -= lr*(lambda*w - y*x) if violated, else w -= lr*lambda*w. "
                "Bar heights show per-sample margin at each iteration."
            ),
            complexity_time_best="O(n·iter)",
            complexity_time_average="O(n·iter)",
            complexity_time_worst="O(n·iter)",
            complexity_space="O(n)",
            tags=("machine-learning", "svm", "classification", "margin", "gradient-descent"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        points, labels = _generate_data(params.seed)
        n = len(points)
        return SortState(
            array=tuple(50 for _ in range(n)),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"SVMLinear seed={params.seed}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        seed = int(re.search(r"seed=(\d+)", initial_state.description).group(1))
        points, labels = _generate_data(seed)
        n = len(points)

        w = [0.0, 0.0]
        b = 0.0

        for it in range(_ITERS):
            for (x1, x2), y in zip(points, labels):
                margin = y * (w[0] * x1 + w[1] * x2 + b)
                if margin < 1.0:  # hinge active
                    w[0] = w[0] - _LR * (_LAMBDA * w[0] - y * x1)
                    w[1] = w[1] - _LR * (_LAMBDA * w[1] - y * x2)
                    b = b + _LR * y
                else:
                    w[0] = w[0] - _LR * _LAMBDA * w[0]
                    w[1] = w[1] - _LR * _LAMBDA * w[1]

            # Compute margins for visualization
            margins = [
                (labels[i] * (w[0] * points[i][0] + w[1] * points[i][1] + b))
                for i in range(n)
            ]
            mx = max(abs(m) for m in margins) or 1.0
            arr = tuple(
                max(1, min(99, int((m / mx) * 49 + 50)))  # center at 50
                for m in margins
            )
            loss = _hinge_loss(points, labels, w, b)
            correct = sum(
                1 for i in range(n) if margins[i] > 0
            )
            yield SortState(
                array=arr,
                comparing=(it % n, it % n),
                last_swap=None,
                sorted_indices=frozenset(i for i in range(n) if margins[i] >= 1.0),
                comparisons=it + 1,
                swaps=correct,
                description=f"Iter {it+1}: loss={loss:.3f} correct={correct}/{n}",
            )

        margins = [
            (labels[i] * (w[0] * points[i][0] + w[1] * points[i][1] + b))
            for i in range(n)
        ]
        mx = max(abs(m) for m in margins) or 1.0
        arr = tuple(
            max(1, min(99, int((m / mx) * 49 + 50)))
            for m in margins
        )
        correct = sum(1 for m in margins if m > 0)
        loss = _hinge_loss(points, labels, w, b)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=_ITERS,
            swaps=correct,
            description=f"SVM trained. Accuracy={correct}/{n}. Loss={loss:.3f}",
        )
