"""K-Means Clustering plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

MAX_ITERS = 15


def _assign(points: List[int], centroids: List[float]) -> List[int]:
    return [min(range(len(centroids)), key=lambda j: abs(points[i] - centroids[j]))
            for i in range(len(points))]


def _recompute(points: List[int], assignments: List[int], k: int) -> List[float]:
    centroids = []
    for j in range(k):
        cluster = [points[i] for i in range(len(points)) if assignments[i] == j]
        centroids.append(sum(cluster) / len(cluster) if cluster else 0.0)
    return centroids


class KMeansSimulation(AlgorithmPlugin):
    """K-Means clustering on 1D data."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="k-means",
            name="K-Means Clustering",
            category="machine-learning",
            visualization_type="ARRAY_BARS",
            description="Partition 1D points into k clusters by iterating assignments and centroid updates.",
            intuition=(
                "Randomly initialize k centroids. "
                "Assign each point to its nearest centroid. "
                "Recompute centroids as cluster means. "
                "Repeat until stable."
            ),
            complexity_time_best="O(nkT)",
            complexity_time_average="O(nkT)",
            complexity_time_worst="O(nkT)",
            complexity_space="O(n + k)",
            tags=("machine-learning", "k-means", "clustering", "unsupervised"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("point_count", 12))
        k = int(params.inputs.get("k", 3))

        # Generate k clusters
        centers = sorted(rng.sample(range(10, 90), k))
        points = []
        for c in centers:
            for _ in range(n // k):
                points.append(max(1, min(99, c + rng.randint(-8, 8))))
        while len(points) < n:
            c = rng.choice(centers)
            points.append(max(1, min(99, c + rng.randint(-8, 8))))
        points = points[:n]
        rng.shuffle(points)

        # Initial centroids = first k points
        centroids = [float(points[i]) for i in range(k)]
        assignments = _assign(points, centroids)

        return SortState(
            array=tuple(sorted(points)),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(i for i, a in enumerate(assignments) if a == 0),
            comparisons=0,
            swaps=k,
            description=f"K-Means k={k} n={n} centroids={[round(c) for c in centroids]}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        desc = initial_state.description
        k = initial_state.swaps
        points = sorted(initial_state.array)
        n = len(points)

        import re
        m = re.search(r"centroids=\[([^\]]+)\]", desc)
        centroids = list(map(float, m.group(1).split(", "))) if m else [float(points[i * n // k]) for i in range(k)]

        assignments = _assign(points, centroids)

        for it in range(MAX_ITERS):
            # Show assignment step
            yield SortState(
                array=tuple(points),
                comparing=None,
                last_swap=None,
                sorted_indices=frozenset(i for i, a in enumerate(assignments) if a == 0),
                comparisons=it * 2,
                swaps=k,
                description=(
                    f"Iter {it}: assigned — centroids={[round(c, 1) for c in centroids]}"
                ),
            )

            new_centroids = _recompute(points, assignments, k)
            moved = any(abs(new_centroids[j] - centroids[j]) > 0.01 for j in range(k))
            centroids = new_centroids
            new_assignments = _assign(points, centroids)

            yield SortState(
                array=tuple(points),
                comparing=None,
                last_swap=None,
                sorted_indices=frozenset(i for i, a in enumerate(new_assignments) if a == 0),
                comparisons=it * 2 + 1,
                swaps=k,
                description=(
                    f"Iter {it}: updated centroids={[round(c, 1) for c in centroids]}"
                ),
            )

            if not moved and new_assignments == assignments:
                assignments = new_assignments
                break
            assignments = new_assignments

        return SortState(
            array=tuple(points),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(i for i, a in enumerate(assignments) if a == 0),
            comparisons=MAX_ITERS * 2,
            swaps=k,
            description=f"Converged: {k} clusters centroids={[round(c, 1) for c in centroids]}",
        )
