"""Matrix Chain Multiplication DP plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

_INF = 999999


class MatrixChainSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="matrix-chain-multiplication",
            name="Matrix Chain Multiplication",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Find optimal parenthesization to minimize scalar multiplications for a chain of matrices.",
            intuition="dp[i][j] = min cost to multiply matrices i..j. Try every split k: dp[i][j] = min(dp[i][k] + dp[k+1][j] + dims[i]*dims[k+1]*dims[j+1]).",
            complexity_time_best="O(n³)",
            complexity_time_average="O(n³)",
            complexity_time_worst="O(n³)",
            complexity_space="O(n²)",
            tags=("dynamic-programming", "matrix-chain", "optimization", "classic"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n: int = max(3, min(params.inputs.get("array_size", 4), 6))
        # n matrices → n+1 dimensions
        dims = [rng.randint(2, 8) for _ in range(n + 1)]
        dp = [[0 if i == j else _INF for j in range(n)] for i in range(n)]
        dims_str = ",".join(str(d) for d in dims)
        return DPState(
            table=tuple(tuple(row) for row in dp),
            current_cell=None,
            computed_cells=frozenset((i, i) for i in range(n)),
            description=f"dims={dims_str}",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        n = len(initial_state.table)
        dims_str = initial_state.description.split("dims=")[1]
        dims = [int(x) for x in dims_str.split(",")]

        dp = [[0 if i == j else _INF for j in range(n)] for i in range(n)]
        computed: set = {(i, i) for i in range(n)}

        # Fill by chain length (diagonal by diagonal)
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                for k in range(i, j):
                    cost = dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                    yield DPState(
                        table=tuple(tuple(row) for row in dp),
                        current_cell=(i, j),
                        computed_cells=frozenset(computed),
                        description=f"dp[{i}][{j}]: split at k={k}, cost={dp[i][k]}+{dp[k+1][j]}+{dims[i]}×{dims[k+1]}×{dims[j+1]}={cost}",
                    )
                    if cost < dp[i][j]:
                        dp[i][j] = cost
                computed.add((i, j))
                yield DPState(
                    table=tuple(tuple(row) for row in dp),
                    current_cell=(i, j),
                    computed_cells=frozenset(computed),
                    description=f"dp[{i}][{j}] = {dp[i][j]}",
                )

        return DPState(
            table=tuple(tuple(row) for row in dp),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Optimal cost = {dp[0][n - 1]} scalar multiplications",
        )
