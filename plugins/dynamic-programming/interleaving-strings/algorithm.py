"""Interleaving Strings plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

# (s1, s2, s3, expected)
_INSTANCES = [
    ("aab", "axy", "aaxaby", True),
    ("aab", "axy", "abaaxy", False),
    ("abc", "def", "adbecf", True),
    ("abc", "def", "abcdef", True),
    ("ab", "bc", "babc", True),
    ("ab", "bc", "abbc", True),
    ("aaa", "aaa", "aaaaaa", True),
    ("abc", "xyz", "abcxyz", True),
    ("db", "b", "cbb", False),
    ("a", "b", "ab", True),
]


def _is_interleaving(s1: str, s2: str, s3: str) -> bool:
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for i in range(1, m + 1):
        dp[i][0] = dp[i-1][0] and s1[i-1] == s3[i-1]
    for j in range(1, n + 1):
        dp[0][j] = dp[0][j-1] and s2[j-1] == s3[j-1]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = (
                (dp[i-1][j] and s1[i-1] == s3[i+j-1]) or
                (dp[i][j-1] and s2[j-1] == s3[i+j-1])
            )
    return dp[m][n]


class InterleavingStringsSimulation(AlgorithmPlugin):
    """Interleaving Strings DP."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="interleaving-strings",
            name="Interleaving Strings",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Check if s3 can be formed by interleaving characters of s1 and s2 in order.",
            intuition=(
                "dp[i][j] = can s3[0..i+j-1] be formed from s1[0..i-1] and s2[0..j-1]. "
                "True if we can take next char from s1 or s2 and match s3's next char."
            ),
            complexity_time_best="O(m·n)",
            complexity_time_average="O(m·n)",
            complexity_time_worst="O(m·n)",
            complexity_space="O(m·n)",
            tags=("dynamic-programming", "interleaving", "string"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        s1, s2, s3, expected = _INSTANCES[params.seed % len(_INSTANCES)]
        m, n = len(s1), len(s2)
        table = tuple(tuple([0] * (n + 1)) for _ in range(m + 1))
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"Interleave s1='{s1}' s2='{s2}' s3='{s3}' expected={expected}",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        desc = initial_state.description
        parts = desc.split("'")
        s1, s2, s3 = parts[1], parts[3], parts[5]
        m, n = len(s1), len(s2)
        dp = [[False] * (n + 1) for _ in range(m + 1)]
        dp[0][0] = True
        for i in range(1, m + 1):
            dp[i][0] = dp[i-1][0] and s1[i-1] == s3[i-1]
        for j in range(1, n + 1):
            dp[0][j] = dp[0][j-1] and s2[j-1] == s3[j-1]

        computed = {(0, 0)} | {(i, 0) for i in range(m+1)} | {(0, j) for j in range(n+1)}

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                dp[i][j] = (
                    (dp[i-1][j] and s1[i-1] == s3[i+j-1]) or
                    (dp[i][j-1] and s2[j-1] == s3[i+j-1])
                )
                computed.add((i, j))
                yield DPState(
                    table=tuple(tuple(int(v) for v in row) for row in dp),
                    current_cell=(i, j),
                    computed_cells=frozenset(computed),
                    description=(
                        f"dp[{i}][{j}]: s1[{i-1}]='{s1[i-1]}' s2[{j-1}]='{s2[j-1]}' "
                        f"s3[{i+j-1}]='{s3[i+j-1]}' → {int(dp[i][j])}"
                    ),
                )

        return DPState(
            table=tuple(tuple(int(v) for v in row) for row in dp),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Is interleaving: {dp[m][n]}",
        )
