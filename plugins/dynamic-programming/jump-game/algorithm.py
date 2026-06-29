"""Jump Game II plugin for Algorithm Atlas."""
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


def _make_array(rng: random.Random, n: int) -> List[int]:
    """Generate a jump array that is always solvable (each element ≥ 1)."""
    return [rng.randint(1, max(1, n // 2)) for _ in range(n)]


class JumpGameSimulation(AlgorithmPlugin):
    """
    Jump Game II — minimum jumps to reach last index.

    DPState table rows:
      row 0: array values (jump lengths)
      row 1: dp[i] = minimum jumps to reach index i (_INF = unreachable)
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="jump-game",
            name="Jump Game (Min Jumps)",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description=(
                "Find minimum jumps to reach the last index. "
                "Each array element is the max jump length from that position."
            ),
            intuition=(
                "dp[i] = min jumps to reach i. "
                "For each i, update all reachable positions j in [i+1, i+arr[i]]: "
                "dp[j] = min(dp[j], dp[i] + 1)."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("dynamic-programming", "greedy", "jump", "array"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n: int = max(5, min(params.inputs.get("array_size", 8), 12))
        arr = _make_array(rng, n)
        dp = [_INF] * n
        dp[0] = 0
        table = (tuple(arr), tuple(dp))
        return DPState(
            table=table,
            current_cell=(0, 0),
            computed_cells=frozenset([(1, 0)]),
            description=f"JumpGame: n={n}, start at index 0 with 0 jumps",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        arr = list(initial_state.table[0])
        n = len(arr)
        dp = [_INF] * n
        dp[0] = 0
        computed: set = {(1, 0)}

        for i in range(n):
            if dp[i] == _INF:
                continue
            max_reach = min(i + arr[i], n - 1)
            for j in range(i + 1, max_reach + 1):
                if dp[i] + 1 < dp[j]:
                    dp[j] = dp[i] + 1
                    computed.add((1, j))
                    yield DPState(
                        table=(tuple(arr), tuple(dp)),
                        current_cell=(1, j),
                        computed_cells=frozenset(computed),
                        description=f"From {i} (jumps={dp[i]}) reach {j}: dp[{j}]={dp[j]}",
                    )

        ans = dp[n - 1]
        return DPState(
            table=(tuple(arr), tuple(dp)),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Done: min jumps = {ans}",
        )
