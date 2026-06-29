"""Decision Tree — Information Gain plugin for Algorithm Atlas."""
from __future__ import annotations

import math
import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


def _entropy(labels: List[int]) -> float:
    if not labels:
        return 0.0
    n = len(labels)
    p = sum(labels) / n
    if p == 0 or p == 1:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def _info_gain(xs: List[int], ys: List[int], threshold: int) -> float:
    n = len(xs)
    left_y  = [ys[i] for i in range(n) if xs[i] <= threshold]
    right_y = [ys[i] for i in range(n) if xs[i] > threshold]
    h_parent = _entropy(ys)
    h_weighted = (len(left_y) / n) * _entropy(left_y) + \
                 (len(right_y) / n) * _entropy(right_y)
    return h_parent - h_weighted


class DecisionTreeEntropySimulation(AlgorithmPlugin):
    """Find the best binary split on 1D data using information gain."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="decision-tree-entropy",
            name="Decision Tree — Information Gain",
            category="machine-learning",
            visualization_type="ARRAY_BARS",
            description="Find optimal 1D split threshold by maximizing entropy reduction (information gain).",
            intuition=(
                "Parent entropy = H(all labels). "
                "For each split: IG = H_parent − (n_L/n·H_L + n_R/n·H_R). "
                "The best split maximizes IG."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n)",
            tags=("machine-learning", "decision-tree", "entropy", "information-gain"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("sample_count", 12))

        # Two-class 1D data with a clear split around 50
        neg_xs = [rng.randint(5, 42) for _ in range(n // 2)]
        pos_xs = [rng.randint(58, 95) for _ in range(n - n // 2)]
        xs = neg_xs + pos_xs
        ys = [0] * len(neg_xs) + [1] * len(pos_xs)
        combined = sorted(zip(xs, ys))
        xs = [c[0] for c in combined]
        ys = [c[1] for c in combined]

        pos_set = frozenset(i for i, y in enumerate(ys) if y == 1)
        return SortState(
            array=tuple(xs),
            comparing=None,
            last_swap=None,
            sorted_indices=pos_set,
            comparisons=0,
            swaps=0,
            description=f"DT entropy n={n}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        xs = list(initial_state.array)
        n = len(xs)
        pos_set = set(initial_state.sorted_indices)
        ys = [1 if i in pos_set else 0 for i in range(n)]

        h_parent = _entropy(ys)
        best_ig = -1.0
        best_thresh = xs[0]
        best_split_idx = 0

        thresholds = sorted(set((xs[i] + xs[i+1]) // 2 for i in range(n-1)))

        for t_idx, t in enumerate(thresholds):
            ig = _info_gain(xs, ys, t)
            improved = ig > best_ig
            if improved:
                best_ig = ig
                best_thresh = t
                best_split_idx = next(
                    (i for i in range(n) if xs[i] > t), n - 1
                )

            yield SortState(
                array=tuple(xs),
                comparing=(best_split_idx, best_split_idx),
                last_swap=(t_idx, t_idx),
                sorted_indices=frozenset(pos_set),
                comparisons=t_idx,
                swaps=t,
                description=(
                    f"Split at {t}: IG={ig:.4f}"
                    + (" ← best!" if improved else f", best={best_thresh}")
                ),
            )

        split_idx = next((i for i in range(n) if xs[i] > best_thresh), n - 1)
        return SortState(
            array=tuple(xs),
            comparing=None,
            last_swap=(split_idx, split_idx),
            sorted_indices=frozenset(pos_set),
            comparisons=len(thresholds),
            swaps=best_thresh,
            description=(
                f"Best split: threshold={best_thresh} IG={best_ig:.4f} "
                f"H_parent={h_parent:.4f}"
            ),
        )
