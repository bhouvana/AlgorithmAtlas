"""Longest Palindromic Subsequence plugin for Algorithm Atlas."""
from __future__ import annotations

import random
import string
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)


def _make_string(rng: random.Random, n: int) -> str:
    """Generate a string with some repeated chars to ensure non-trivial LPS."""
    alphabet = "abcde"
    return "".join(rng.choice(alphabet) for _ in range(n))


class PalindromeSubsequenceSimulation(AlgorithmPlugin):
    """
    Longest Palindromic Subsequence — O(n²) DP.

    DPState table: n×n where dp[i][j] = LPS length for s[i..j].
    Encodes "LPS('string')" in description.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="palindrome-subsequence",
            name="Longest Palindromic Subsequence",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description=(
                "Find the longest subsequence of a string that reads the same "
                "forwards and backwards."
            ),
            intuition=(
                "dp[i][j] = LPS length in s[i..j]. "
                "Base: dp[i][i]=1. "
                "If s[i]==s[j]: dp[i][j]=dp[i+1][j-1]+2. "
                "Else: max(dp[i+1][j], dp[i][j-1])."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n²)",
            tags=("dynamic-programming", "palindrome", "subsequence", "string"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n: int = max(5, min(params.inputs.get("array_size", 6), 8))
        s = _make_string(rng, n)
        # Initial table: diagonal = 1, rest = 0
        dp = [[0] * n for _ in range(n)]
        for i in range(n):
            dp[i][i] = 1
        computed = frozenset((i, i) for i in range(n))
        return DPState(
            table=tuple(tuple(row) for row in dp),
            current_cell=None,
            computed_cells=computed,
            description=f"LPS('{s}'): base dp[i][i]=1",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        s = initial_state.description.split("'")[1]
        n = len(s)
        dp = [list(row) for row in initial_state.table]
        computed: set = set((i, i) for i in range(n))

        # Fill by increasing substring length
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                if s[i] == s[j]:
                    inner = dp[i + 1][j - 1] if length > 2 else 0
                    dp[i][j] = inner + 2
                    desc = f"s[{i}]=s[{j}]='{s[i]}': dp[{i}][{j}] = {dp[i][j]}"
                else:
                    dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
                    desc = (
                        f"s[{i}]='{s[i]}' ≠ s[{j}]='{s[j]}': "
                        f"dp[{i}][{j}] = max({dp[i+1][j]},{dp[i][j-1]}) = {dp[i][j]}"
                    )
                computed.add((i, j))
                yield DPState(
                    table=tuple(tuple(row) for row in dp),
                    current_cell=(i, j),
                    computed_cells=frozenset(computed),
                    description=desc,
                )

        return DPState(
            table=tuple(tuple(row) for row in dp),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"LPS('{s}') = {dp[0][n-1]}",
        )
