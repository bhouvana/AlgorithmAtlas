"""Palindrome Partitioning (Min Cuts) plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

_ALPHA = "abcde"


def _make_string(rng: random.Random, n: int) -> str:
    return "".join(rng.choice(_ALPHA) for _ in range(n))


def _min_cuts(s: str) -> int:
    n = len(s)
    # pal[i][j] = True if s[i..j] is palindrome
    pal = [[False] * n for _ in range(n)]
    for i in range(n):
        pal[i][i] = True
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if length == 2:
                pal[i][j] = s[i] == s[j]
            else:
                pal[i][j] = s[i] == s[j] and pal[i+1][j-1]
    dp = [0] * n
    for i in range(1, n):
        if pal[0][i]:
            dp[i] = 0
        else:
            dp[i] = i  # worst case: cut after every char
            for j in range(1, i + 1):
                if pal[j][i]:
                    dp[i] = min(dp[i], dp[j-1] + 1)
    return dp[n-1]


class PalindromePartitionSimulation(AlgorithmPlugin):
    """Palindrome Partitioning — Minimum Cuts."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="palindrome-partition",
            name="Palindrome Partitioning (Min Cuts)",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Find minimum cuts to partition a string so every part is a palindrome.",
            intuition=(
                "Build palindrome table first. Then dp[i] = minimum cuts for s[0..i]. "
                "If s[0..i] itself is palindrome, 0 cuts; else try all valid palindrome suffixes."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n²)",
            tags=("dynamic-programming", "palindrome", "partitioning", "min-cuts"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 6))
        s = _make_string(rng, n)
        expected = _min_cuts(s)
        # Table: n rows (palindrome[i][j] for i=0..n-1), n cols
        pal = [[False] * n for _ in range(n)]
        for i in range(n):
            pal[i][i] = True
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                pal[i][j] = (s[i] == s[j]) and (length == 2 or pal[i+1][j-1])
        table = tuple(tuple(int(v) for v in row) for row in pal)
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"Palindrome partition '{s}' expected={expected}",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        desc = initial_state.description
        s = desc.split("'")[1]
        n = len(s)

        pal = [[False] * n for _ in range(n)]
        for i in range(n):
            pal[i][i] = True
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                pal[i][j] = (s[i] == s[j]) and (length == 2 or pal[i+1][j-1])

        dp = [0] * n
        computed: set = set()
        table = tuple(tuple(int(v) for v in row) for row in pal)

        for i in range(1, n):
            if pal[0][i]:
                dp[i] = 0
            else:
                dp[i] = i
                for j in range(1, i + 1):
                    if pal[j][i]:
                        dp[i] = min(dp[i], dp[j-1] + 1)
            computed.add((i, i))
            yield DPState(
                table=table,
                current_cell=(i, i),
                computed_cells=frozenset(computed),
                description=f"dp[{i}]={dp[i]}: s[0..{i}]='{s[:i+1]}' needs {dp[i]} cuts",
            )

        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Min cuts for '{s}' = {dp[n-1]}",
        )
