"""Optimal BST (Knuth's Algorithm) plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

_KEYS = ["k1", "k2", "k3", "k4"]
_FREQ = [3, 2, 4, 2]   # search frequencies for each key
_N = len(_KEYS)
_INF = 10 ** 9


class OptimalBSTSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="optimal-bst",
            name="Optimal BST (Knuth's Algorithm)",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Find the BST with minimum expected search cost given key frequencies.",
            intuition=(
                "dp[i][j] = min cost BST for keys i..j. "
                "Try each key k as root: dp[i][j] = dp[i][k-1] + dp[k+1][j] + w[i][j]. "
                "w[i][j] = cumulative weight added each time we descend through this subtree."
            ),
            complexity_time_best="O(n³)",
            complexity_time_average="O(n³)",
            complexity_time_worst="O(n³)",
            complexity_space="O(n²)",
            tags=("dynamic-programming", "optimal-bst", "knuth", "binary-search-tree", "classic"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        dp = [[0] * _N for _ in range(_N)]
        for i in range(_N):
            dp[i][i] = _FREQ[i]
        return DPState(
            table=tuple(tuple(row) for row in dp),
            current_cell=None,
            computed_cells=frozenset((i, i) for i in range(_N)),
            description=f"keys={_KEYS} freq={_FREQ}",
        )

    def steps(self, initial_state: DPState) -> Generator[DPState, None, DPState]:
        dp = [[0] * _N for _ in range(_N)]
        root = [[0] * _N for _ in range(_N)]
        # prefix sums for w[i][j] = sum(freq[i..j])
        prefix = [0] * (_N + 1)
        for i, f in enumerate(_FREQ):
            prefix[i + 1] = prefix[i] + f

        def w(i, j):
            return prefix[j + 1] - prefix[i]

        computed: set = set()

        # Length-1 subproblems
        for i in range(_N):
            dp[i][i] = _FREQ[i]
            root[i][i] = i
            computed.add((i, i))
            yield DPState(
                table=tuple(tuple(row) for row in dp),
                current_cell=(i, i),
                computed_cells=frozenset(computed),
                description=f"dp[{i}][{i}] = freq[{i}] = {_FREQ[i]} (root={_KEYS[i]})",
            )

        for length in range(2, _N + 1):
            for i in range(_N - length + 1):
                j = i + length - 1
                dp[i][j] = _INF
                weight = w(i, j)
                for k in range(i, j + 1):
                    left = dp[i][k - 1] if k > i else 0
                    right = dp[k + 1][j] if k < j else 0
                    cost = left + right + weight
                    yield DPState(
                        table=tuple(tuple(row) for row in dp),
                        current_cell=(i, j),
                        computed_cells=frozenset(computed),
                        description=(
                            f"dp[{i}][{j}] try root={_KEYS[k]}: "
                            f"{left}+{right}+{weight}={cost}"
                        ),
                    )
                    if cost < dp[i][j]:
                        dp[i][j] = cost
                        root[i][j] = k
                computed.add((i, j))
                yield DPState(
                    table=tuple(tuple(row) for row in dp),
                    current_cell=(i, j),
                    computed_cells=frozenset(computed),
                    description=(
                        f"dp[{i}][{j}] = {dp[i][j]}, optimal root = {_KEYS[root[i][j]]}"
                    ),
                )

        final = DPState(
            table=tuple(tuple(row) for row in dp),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Optimal BST cost = {dp[0][_N - 1]}, root = {_KEYS[root[0][_N - 1]]}",
        )
        yield final
        return final
