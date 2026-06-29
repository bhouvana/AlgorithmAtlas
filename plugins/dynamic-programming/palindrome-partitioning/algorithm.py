"""Palindrome Partitioning (min cuts) plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_STRINGS = [
    "aab",
    "abacaba",
    "aababab",
    "nitin",
    "abcde",
]


def _min_cuts(s):
    n = len(s)
    # pal[i][j] = True if s[i..j] is palindrome
    pal = [[False] * n for _ in range(n)]
    for i in range(n):
        pal[i][i] = True
    for i in range(n - 1):
        pal[i][i + 1] = (s[i] == s[i + 1])
    for length in range(3, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            pal[i][j] = (s[i] == s[j]) and pal[i + 1][j - 1]

    dp = [0] * n
    for i in range(n):
        if pal[0][i]:
            dp[i] = 0
        else:
            dp[i] = i  # worst case: cut before each char
            for j in range(1, i + 1):
                if pal[j][i]:
                    dp[i] = min(dp[i], dp[j - 1] + 1)
    return dp, pal


class PalindromePartitioningSimulation(AlgorithmPlugin):
    """Palindrome partitioning min-cuts visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="palindrome-partitioning",
            name="Palindrome Partitioning",
            category="dynamic-programming",
            visualization_type="ARRAY_BARS",
            description="Minimum cuts to partition string into palindromes.",
            intuition=(
                "Precompute pal[i][j] for all substrings. "
                "dp[i] = min cuts for s[0..i]. "
                "dp[i] = min(dp[j-1]+1) where s[j..i] is a palindrome."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n²)",
            tags=("dynamic-programming", "palindrome", "string", "min-cut"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        s = _STRINGS[params.seed % len(_STRINGS)]
        dp, _ = _min_cuts(s)
        n = len(s)
        arr = tuple(1 for _ in range(n))
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"PalPart s='{s}'",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        s = re.search(r"s='([^']+)'", initial_state.description).group(1)
        n = len(s)
        dp, pal = _min_cuts(s)

        for i in range(n):
            # Show DP progress: dp[0..i], rest still 0
            partial = list(dp[:i + 1]) + [0] * (n - i - 1)
            mx = max(max(dp), 1)
            arr = tuple(max(1, min(99, int(v * 99 / mx + 1))) for v in partial)
            yield SortState(
                array=arr,
                comparing=(i, i),
                last_swap=None,
                sorted_indices=frozenset(range(i + 1)),
                comparisons=i + 1,
                swaps=dp[i],
                description=f"dp[{i}]={dp[i]}: s[0..{i}]='{s[:i+1]}' needs {dp[i]} cut(s)",
            )

        mx = max(max(dp), 1)
        arr = tuple(max(1, min(99, int(v * 99 / mx + 1))) for v in dp)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=n,
            swaps=dp[-1],
            description=f"Min cuts for '{s}' = {dp[-1]}",
        )
