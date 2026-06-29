"""Distinct Subsequences Count plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_EXAMPLES = [
    ("rabbbit", "rabbit"),
    ("babgbag", "bag"),
    ("aabdbabd", "abd"),
    ("xyzxyz", "xyz"),
    ("aaaaaa", "aaa"),
]


class DistinctSubsequencesSimulation(AlgorithmPlugin):
    """Count distinct subsequences using 1D rolling DP."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="distinct-subsequences",
            name="Distinct Subsequences Count",
            category="dynamic-programming",
            visualization_type="ARRAY_BARS",
            description="Count ways t appears as a subsequence of s using rolling DP.",
            intuition=(
                "dp[j] = ways to form t[0..j-1] from s[0..i-1]. "
                "Process s right-to-left per row to avoid overwriting. "
                "Match at s[i]==t[j]: add ways from dp[j-1]."
            ),
            complexity_time_best="O(m·n)",
            complexity_time_average="O(m·n)",
            complexity_time_worst="O(m·n)",
            complexity_space="O(n)",
            tags=("dynamic-programming", "subsequences", "string-dp", "counting"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        s, t = _EXAMPLES[params.seed % len(_EXAMPLES)]
        return SortState(
            array=tuple([1] + [0] * len(t)),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset([0]),
            comparisons=0,
            swaps=0,
            description=f"DistSubseq s='{s}' t='{t}'",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        s = re.search(r"s='([^']+)'", initial_state.description).group(1)
        t = re.search(r"t='([^']+)'", initial_state.description).group(1)
        m, n = len(s), len(t)
        dp = [0] * (n + 1)
        dp[0] = 1

        for i, cs in enumerate(s):
            # Right-to-left update to avoid using updated values
            for j in range(n, 0, -1):
                if cs == t[j - 1]:
                    dp[j] += dp[j - 1]

            mx = max(dp) or 1
            arr = tuple(max(1, min(99, v * 99 // mx)) for v in dp)
            matches = frozenset(j for j in range(n + 1) if dp[j] > 0)
            yield SortState(
                array=arr,
                comparing=(i % n, i % n),
                last_swap=(i % n, i % n) if cs in t else None,
                sorted_indices=matches,
                comparisons=i + 1,
                swaps=dp[n],
                description=(
                    f"s[{i}]='{cs}': dp[{n}]={dp[n]}"
                ),
            )

        mx = max(dp) or 1
        arr = tuple(max(1, min(99, v * 99 // mx)) for v in dp)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n + 1)),
            comparisons=m,
            swaps=dp[n],
            description=f"'{t}' appears {dp[n]} times as subsequence of '{s}'",
        )
