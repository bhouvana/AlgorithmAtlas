"""Unique Paths (Grid DP) plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)


class UniquePathsSimulation(AlgorithmPlugin):
    """
    Unique Paths — count paths from (0,0) to (m-1,n-1) using only right/down moves.

    DPState table: m×n grid where dp[i][j] = paths to reach cell (i,j).
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="unique-paths",
            name="Unique Paths (Grid DP)",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description=(
                "Count distinct paths from top-left to bottom-right of an m×n grid, "
                "moving only right or down."
            ),
            intuition=(
                "dp[i][j] = dp[i-1][j] + dp[i][j-1]. "
                "Base: first row and column all = 1 (single straight path). "
                "Fill left-to-right, top-to-bottom."
            ),
            complexity_time_best="O(m×n)",
            complexity_time_average="O(m×n)",
            complexity_time_worst="O(m×n)",
            complexity_space="O(m×n)",
            tags=("dynamic-programming", "grid", "counting", "paths"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        n: int = max(3, min(params.inputs.get("array_size", 4), 6))
        # Initialize grid: all zeros, base cases set
        dp = [[0] * n for _ in range(n)]
        for i in range(n):
            dp[i][0] = 1
        for j in range(n):
            dp[0][j] = 1
        computed = frozenset((i, 0) for i in range(n)) | frozenset((0, j) for j in range(n))
        return DPState(
            table=tuple(tuple(row) for row in dp),
            current_cell=None,
            computed_cells=computed,
            description=f"UniquePaths({n}×{n}): base row/col = 1",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        dp = [list(row) for row in initial_state.table]
        n = len(dp)
        computed = set(initial_state.computed_cells)

        for i in range(1, n):
            for j in range(1, n):
                dp[i][j] = dp[i - 1][j] + dp[i][j - 1]
                computed.add((i, j))
                yield DPState(
                    table=tuple(tuple(row) for row in dp),
                    current_cell=(i, j),
                    computed_cells=frozenset(computed),
                    description=(
                        f"dp[{i}][{j}] = dp[{i-1}][{j}] + dp[{i}][{j-1}] "
                        f"= {dp[i-1][j]} + {dp[i][j-1]} = {dp[i][j]}"
                    ),
                )

        return DPState(
            table=tuple(tuple(row) for row in dp),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Unique paths in {n}×{n} grid = {dp[n-1][n-1]}",
        )
