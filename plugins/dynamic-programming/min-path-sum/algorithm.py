"""Minimum Path Sum plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

_INF = 999999


def _make_grid(rng: random.Random, n: int) -> list[list[int]]:
    return [[rng.randint(1, 9) for _ in range(n)] for _ in range(n)]


def _min_path(grid: list[list[int]]) -> int:
    n = len(grid)
    dp = [[0] * n for _ in range(n)]
    dp[0][0] = grid[0][0]
    for j in range(1, n):
        dp[0][j] = dp[0][j-1] + grid[0][j]
    for i in range(1, n):
        dp[i][0] = dp[i-1][0] + grid[i][0]
    for i in range(1, n):
        for j in range(1, n):
            dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])
    return dp[n-1][n-1]


class MinPathSumSimulation(AlgorithmPlugin):
    """Minimum Path Sum in a Grid."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="min-path-sum",
            name="Minimum Path Sum",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Find minimum cost path from top-left to bottom-right moving only right or down.",
            intuition=(
                "dp[i][j] = grid[i][j] + min(from above, from left). "
                "Fill first row/column as prefix sums."
            ),
            complexity_time_best="O(m·n)",
            complexity_time_average="O(m·n)",
            complexity_time_worst="O(m·n)",
            complexity_space="O(m·n)",
            tags=("dynamic-programming", "grid", "min-path"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 4))
        grid = _make_grid(rng, n)
        expected = _min_path(grid)
        return DPState(
            table=tuple(tuple(row) for row in grid),
            current_cell=None,
            computed_cells=frozenset(),
            description=f"Min path sum {n}x{n} grid expected={expected}",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        grid = [list(row) for row in initial_state.table]
        n = len(grid)
        dp = [[0] * n for _ in range(n)]
        computed: set = set()

        dp[0][0] = grid[0][0]
        computed.add((0, 0))
        yield DPState(
            table=tuple(tuple(row) for row in dp),
            current_cell=(0, 0),
            computed_cells=frozenset(computed),
            description=f"Base dp[0][0]={dp[0][0]}",
        )

        for j in range(1, n):
            dp[0][j] = dp[0][j-1] + grid[0][j]
            computed.add((0, j))
            yield DPState(
                table=tuple(tuple(row) for row in dp),
                current_cell=(0, j),
                computed_cells=frozenset(computed),
                description=f"Top row: dp[0][{j}]={dp[0][j]}",
            )

        for i in range(1, n):
            dp[i][0] = dp[i-1][0] + grid[i][0]
            computed.add((i, 0))
            yield DPState(
                table=tuple(tuple(row) for row in dp),
                current_cell=(i, 0),
                computed_cells=frozenset(computed),
                description=f"Left col: dp[{i}][0]={dp[i][0]}",
            )

        for i in range(1, n):
            for j in range(1, n):
                dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])
                computed.add((i, j))
                yield DPState(
                    table=tuple(tuple(row) for row in dp),
                    current_cell=(i, j),
                    computed_cells=frozenset(computed),
                    description=f"dp[{i}][{j}]={dp[i][j]} (grid={grid[i][j]} + min({dp[i-1][j]},{dp[i][j-1]}))",
                )

        return DPState(
            table=tuple(tuple(row) for row in dp),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Min path sum = {dp[n-1][n-1]}",
        )
