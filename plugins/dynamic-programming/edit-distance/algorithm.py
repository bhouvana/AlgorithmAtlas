"""Edit Distance (Levenshtein) DP plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

_CHARS = "ABCDE"


def _random_string(rng: random.Random, n: int) -> str:
    return "".join(rng.choices(_CHARS, k=n))


class EditDistanceSimulation(AlgorithmPlugin):
    """
    Levenshtein Edit Distance — O(m·n).

    dp[i][j] = min edits to convert s1[:i] to s2[:j].
    Base cases: dp[0][j]=j (delete j chars), dp[i][0]=i (insert i chars).
    Row/col labels: [ε, s1[0], ...] / [ε, s2[0], ...]
    Encodes strings in description: EditDist("S1","S2")
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="edit-distance",
            name="Edit Distance (Levenshtein)",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Minimum insertions, deletions, and substitutions to transform one string into another.",
            intuition="dp[i][j]: cost to convert s1[:i] to s2[:j]. Match = free; mismatch = +1 to the cheapest of delete, insert, or substitute.",
            complexity_time_best="O(m·n)",
            complexity_time_average="O(m·n)",
            complexity_time_worst="O(m·n)",
            complexity_space="O(m·n)",
            tags=("dynamic-programming", "string", "edit-distance", "levenshtein"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        length: int = max(4, min(params.inputs.get("string_length", 5), 8))
        s1 = _random_string(rng, length)
        s2 = _random_string(rng, length)
        m, n = len(s1), len(s2)
        # Initialize base cases
        table = tuple(
            tuple(j if i == 0 else (i if j == 0 else 0) for j in range(n + 1))
            for i in range(m + 1)
        )
        base = frozenset(
            [(0, j) for j in range(n + 1)] + [(i, 0) for i in range(m + 1)]
        )
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=base,
            description=f'EditDist("{s1}","{s2}")',
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        desc = initial_state.description  # EditDist("S1","S2")
        inner = desc[10:-2]  # strip EditDist(" prefix and ")
        parts = inner.split('","')
        s1, s2 = parts[0], parts[1]
        m, n = len(s1), len(s2)

        dp: List[List[int]] = [list(row) for row in initial_state.table]
        computed: set = set(initial_state.computed_cells)

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                    op = f"match '{s1[i-1]}' → dp[{i}][{j}] = dp[{i-1}][{j-1}] = {dp[i][j]}"
                else:
                    best = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
                    dp[i][j] = best + 1
                    ops = ["del", "ins", "sub"]
                    costs = [dp[i-1][j], dp[i][j-1], dp[i-1][j-1]]
                    which = ops[costs.index(best)]
                    op = f"'{s1[i-1]}'≠'{s2[j-1]}' → {which}: dp[{i}][{j}]={dp[i][j]}"
                computed.add((i, j))
                yield DPState(
                    table=tuple(tuple(r) for r in dp),
                    current_cell=(i, j),
                    computed_cells=frozenset(computed),
                    description=op,
                )

        return DPState(
            table=tuple(tuple(r) for r in dp),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f'EditDist("{s1}","{s2}") = {dp[m][n]}',
        )
