"""Wildcard Pattern Matching plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

# (string, pattern, expected_match)
_INSTANCES = [
    ("aa", "a", False),
    ("aa", "*", True),
    ("cb", "?a", False),
    ("adceb", "*a*b", True),
    ("acdcb", "a*c?b", False),
    ("abc", "a?c", True),
    ("abcdef", "a*f", True),
    ("abc", "***", True),
    ("abc", "a*d", False),
    ("abcd", "a?c*", True),
]


def _match(s: str, p: str) -> bool:
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for j in range(1, n + 1):
        if p[j-1] == '*':
            dp[0][j] = dp[0][j-1]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j-1] == '*':
                dp[i][j] = dp[i-1][j] or dp[i][j-1]
            elif p[j-1] == '?' or s[i-1] == p[j-1]:
                dp[i][j] = dp[i-1][j-1]
    return dp[m][n]


class WildcardMatchingSimulation(AlgorithmPlugin):
    """Wildcard Pattern Matching DP."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="wildcard-matching",
            name="Wildcard Pattern Matching",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Match string against a pattern with '?' (any char) and '*' (any sequence).",
            intuition=(
                "dp[i][j] = matches(s[0..i-1], p[0..j-1]). "
                "'*' matches empty or any prefix: dp[i][j] = dp[i-1][j] | dp[i][j-1]."
            ),
            complexity_time_best="O(m·n)",
            complexity_time_average="O(m·n)",
            complexity_time_worst="O(m·n)",
            complexity_space="O(m·n)",
            tags=("dynamic-programming", "wildcard", "pattern-matching"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        s, p, expected = _INSTANCES[params.seed % len(_INSTANCES)]
        m, n = len(s), len(p)
        dp = [[False] * (n + 1) for _ in range(m + 1)]
        dp[0][0] = True
        for j in range(1, n + 1):
            if p[j-1] == '*':
                dp[0][j] = dp[0][j-1]
        table = tuple(tuple(int(v) for v in row) for row in dp)
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"Wildcard: s='{s}' p='{p}' expected={expected}",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        desc = initial_state.description
        parts = desc.split("'")
        s, p = parts[1], parts[3]
        m, n = len(s), len(p)
        dp = [[False] * (n + 1) for _ in range(m + 1)]
        dp[0][0] = True
        for j in range(1, n + 1):
            if p[j-1] == '*':
                dp[0][j] = dp[0][j-1]
        computed: set = {(0, j) for j in range(n + 1)}

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if p[j-1] == '*':
                    dp[i][j] = dp[i-1][j] or dp[i][j-1]
                elif p[j-1] == '?' or s[i-1] == p[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                computed.add((i, j))
                yield DPState(
                    table=tuple(tuple(int(v) for v in row) for row in dp),
                    current_cell=(i, j),
                    computed_cells=frozenset(computed),
                    description=(
                        f"dp[{i}][{j}]: s[{i-1}]='{s[i-1]}' p[{j-1}]='{p[j-1]}' → {int(dp[i][j])}"
                    ),
                )

        return DPState(
            table=tuple(tuple(int(v) for v in row) for row in dp),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"'{s}' matches '{p}': {dp[m][n]}",
        )
