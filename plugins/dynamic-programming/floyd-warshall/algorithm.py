"""Floyd-Warshall all-pairs shortest paths plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List, Optional, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

_INF = 999  # sentinel for display (not float("inf") so it's JSON-friendly)


def _build_adj(rng: random.Random, n: int) -> List[List[int]]:
    """Random connected weighted directed graph as adjacency matrix. -1 = no edge."""
    mat = [[_INF] * n for _ in range(n)]
    for i in range(n):
        mat[i][i] = 0
    # Spanning tree edges (both directions, asymmetric weights)
    nodes = list(range(n))
    rng.shuffle(nodes)
    for i in range(1, n):
        j = rng.randint(0, i - 1)
        u, v = nodes[i], nodes[j]
        w = rng.randint(1, 9)
        mat[u][v] = w
        mat[v][u] = rng.randint(1, 9)
    # Extra edges
    for _ in range(n):
        u = rng.randint(0, n - 1)
        v = rng.randint(0, n - 1)
        if u != v and mat[u][v] == _INF:
            mat[u][v] = rng.randint(1, 9)
    return mat


class FloydWarshallSimulation(AlgorithmPlugin):
    """
    Floyd-Warshall — O(V³).

    DPState table: V×V distance matrix.
    current_cell: (i, j) being updated.
    computed_cells: all (i, j) processed in current round k.
    description: current k, i, j and the relaxation result.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="floyd-warshall",
            name="Floyd-Warshall All-Pairs Shortest Paths",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Finds shortest paths between all pairs of nodes in a weighted graph.",
            intuition="For each intermediate node k, try to improve all (i→j) paths by routing through k. Repeat for every k.",
            complexity_time_best="O(V³)",
            complexity_time_average="O(V³)",
            complexity_time_worst="O(V³)",
            complexity_space="O(V²)",
            tags=("dynamic-programming", "graph", "shortest-path", "all-pairs"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("node_count", 5), 6))
        adj = _build_adj(rng, n)
        table = tuple(tuple(row) for row in adj)
        # All main diagonal cells start as computed (dist[i][i]=0)
        computed = frozenset((i, i) for i in range(n))
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=computed,
            description=f"Floyd-Warshall: {n}×{n} distance matrix (999=∞)",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        n = len(initial_state.table)
        dist: List[List[int]] = [list(row) for row in initial_state.table]
        computed: set = set((i, i) for i in range(n))

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if i == j:
                        continue
                    if dist[i][k] < _INF and dist[k][j] < _INF:
                        new_d = dist[i][k] + dist[k][j]
                        if new_d < dist[i][j]:
                            dist[i][j] = new_d
                            computed.add((i, j))
                            yield DPState(
                                table=tuple(tuple(r) for r in dist),
                                current_cell=(i, j),
                                computed_cells=frozenset(computed),
                                description=f"k={k}: dist[{i}][{j}] = min({dist[i][j]}, {dist[i][k]}+{dist[k][j]}) = {new_d}",
                            )
                        else:
                            computed.add((i, j))
                            yield DPState(
                                table=tuple(tuple(r) for r in dist),
                                current_cell=(i, j),
                                computed_cells=frozenset(computed),
                                description=f"k={k}: dist[{i}][{j}]={dist[i][j]} already optimal via k",
                            )

        # Mark all cells computed
        all_cells = frozenset((i, j) for i in range(n) for j in range(n))
        return DPState(
            table=tuple(tuple(r) for r in dist),
            current_cell=None,
            computed_cells=all_cells,
            description=f"Floyd-Warshall complete: all {n}×{n} = {n*n} pairs computed",
        )
