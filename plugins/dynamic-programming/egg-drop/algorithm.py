"""Egg Drop Problem plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

# (k_eggs, n_floors) instances
_INSTANCES = [
    (2, 10), (2, 14), (2, 20), (3, 14), (3, 20),
    (2, 36), (4, 20), (3, 36), (2, 100), (4, 50),
]


class EggDropSimulation(AlgorithmPlugin):
    """
    Egg Drop Problem — dual DP formulation O(k*n).

    Instead of dp[k][n] = min trials for k eggs, n floors (which requires O(n²) binary search),
    use: dp[k][t] = max floors testable with k eggs and t trials.

    dp[1][t] = t (1 egg: must go linearly)
    dp[k][t] = dp[k-1][t-1] + dp[k][t-1] + 1

    Find min t such that dp[k][t] >= n.

    DPState table: (k+1) rows × T columns where T = answer
      row 0: trial counts [1, 2, ..., T]
      rows 1..k: dp[eggs][trials] values
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="egg-drop",
            name="Egg Drop Problem",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description=(
                "Minimum trials to find the critical floor with k eggs and n floors, "
                "in the worst case."
            ),
            intuition=(
                "dp[k][t] = max floors testable with k eggs and t trials. "
                "dp[k][t] = dp[k-1][t-1] + dp[k][t-1] + 1. "
                "Find the smallest t where dp[k][t] ≥ n."
            ),
            complexity_time_best="O(kn)",
            complexity_time_average="O(kn)",
            complexity_time_worst="O(kn)",
            complexity_space="O(kn)",
            tags=("dynamic-programming", "egg-drop", "decision-theory", "puzzle"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        k, n = _INSTANCES[params.seed % len(_INSTANCES)]
        # Find answer T
        T = 1
        while True:
            # Compute dp[k][T]
            dp = [0] * (k + 1)
            for t in range(1, T + 1):
                dp2 = [0] * (k + 1)
                for e in range(1, k + 1):
                    dp2[e] = dp[e - 1] + dp[e] + 1
                dp = dp2
            if dp[k] >= n:
                break
            T += 1

        # Build full table: (k+1) rows x T cols
        # row 0 = trial indices, rows 1..k = dp values
        full_dp = [[0] * (k + 1) for _ in range(T + 1)]  # full_dp[t][e]
        for t in range(1, T + 1):
            for e in range(1, k + 1):
                full_dp[t][e] = full_dp[t - 1][e - 1] + full_dp[t - 1][e] + 1

        table_rows = [tuple(range(T + 1))]  # row 0: trial indices 0..T
        for e in range(1, k + 1):
            table_rows.append(tuple(full_dp[t][e] for t in range(T + 1)))

        return DPState(
            table=tuple(table_rows),
            current_cell=None,
            computed_cells=frozenset([(0, t) for t in range(T + 1)]),
            description=f"EggDrop(k={k}, n={n}): find min trials T",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        desc = initial_state.description
        k = int(desc.split("k=")[1].split(",")[0])
        n = int(desc.split("n=")[1].split(")")[0])
        T = len(initial_state.table[0]) - 1  # T = number of trials

        table = [list(row) for row in initial_state.table]
        computed: set = set((0, t) for t in range(T + 1))

        # Fill row by row (egg count 1..k), col by col (trial 1..T)
        for e in range(1, k + 1):
            for t in range(1, T + 1):
                val = table[e][t]  # precomputed during initialize
                computed.add((e, t))
                yield DPState(
                    table=tuple(tuple(row) for row in table),
                    current_cell=(e, t),
                    computed_cells=frozenset(computed),
                    description=(
                        f"dp[{e} eggs][{t} trials] = "
                        f"dp[{e-1}][{t-1}]+dp[{e}][{t-1}]+1 = {val}"
                    ),
                )

        # Find answer
        answer_t = next(t for t in range(1, T + 1) if table[k][t] >= n)
        return DPState(
            table=tuple(tuple(row) for row in table),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"EggDrop(k={k}, n={n}) = {answer_t} trials",
        )
