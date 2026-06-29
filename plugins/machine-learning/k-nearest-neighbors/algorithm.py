"""K-Nearest Neighbors (1D) plugin for Algorithm Atlas."""
from __future__ import annotations

import heapq
import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


def _generate_data(rng: random.Random, n: int):
    xs = [rng.randint(1, 99) for _ in range(n)]
    # Two-cluster labels: class 0 = low values, class 1 = high values (with overlap)
    ys = [0 if x < 55 else 1 for x in xs]
    return xs, ys


class KNNSimulation(AlgorithmPlugin):
    """K-Nearest Neighbours (1D binary classification)."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="k-nearest-neighbors",
            name="K-Nearest Neighbors (1D)",
            category="machine-learning",
            visualization_type="ARRAY_BARS",
            description="Classify a query point using the k training points closest to it.",
            intuition=(
                "Bar height = distance from the query. "
                "The k shortest bars are the nearest neighbours; "
                "majority class among them is the prediction."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("machine-learning", "knn", "classification", "distance"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("n_samples", 20))
        k = int(params.inputs.get("k", 3))
        xs, _ = _generate_data(rng, n)
        q = rng.randint(1, 99)
        distances = [abs(x - q) for x in xs]
        max_d = max(distances) if distances else 1
        scaled = [max(1, int(d * 99 // max_d)) for d in distances]
        return SortState(
            array=tuple(scaled),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"k-NN: n={n} k={k} q={q} seed={params.seed}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        desc = initial_state.description
        n = int(re.search(r"n=(\d+)", desc).group(1))
        k = int(re.search(r"k=(\d+)", desc).group(1))
        q = int(re.search(r"q=(\d+)", desc).group(1))
        seed_val = int(re.search(r"seed=(\d+)", desc).group(1))

        rng = random.Random(seed_val)
        xs, ys = _generate_data(rng, n)
        _ = rng.randint(1, 99)  # consume the q draw

        distances = [abs(x - q) for x in xs]
        max_d = max(distances) if distances else 1
        scaled = [max(1, int(d * 99 // max_d)) for d in distances]

        # max-heap: track k smallest distances via (-dist, idx)
        heap: list = []

        for i, (dist, sdist) in enumerate(zip(distances, scaled)):
            if len(heap) < k:
                heapq.heappush(heap, (-dist, i))
            elif dist < -heap[0][0]:
                heapq.heapreplace(heap, (-dist, i))

            current_k = frozenset(idx for _, idx in heap)

            yield SortState(
                array=tuple(scaled),
                comparing=(i, i),
                last_swap=None,
                sorted_indices=current_k,
                comparisons=i + 1,
                swaps=0,
                description=(
                    f"x[{i}]={xs[i]} dist={dist}. "
                    f"Top-{k} so far: {sorted(current_k)}"
                ),
            )

        k_indices = [idx for _, idx in heap]
        k_classes = [ys[idx] for idx in k_indices]
        pred = 1 if sum(k_classes) > k // 2 else 0

        return SortState(
            array=tuple(scaled),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(k_indices),
            comparisons=n,
            swaps=pred,
            description=(
                f"k-NN done: k={k} neighbors={sorted(k_indices)}, "
                f"classes={k_classes}, predicted={pred}"
            ),
        )
