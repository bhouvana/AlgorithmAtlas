"""Longest Common Substring plugin for Algorithm Atlas."""
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


def _make_strings(rng: random.Random, n: int):
    """Make two strings with a guaranteed common substring of length ~n//2."""
    common_len = max(2, n // 2)
    common = "".join(rng.choice(_ALPHA) for _ in range(common_len))
    s1_prefix = "".join(rng.choice(_ALPHA) for _ in range(rng.randint(0, n - common_len)))
    s2_prefix = "".join(rng.choice(_ALPHA) for _ in range(rng.randint(0, n - common_len)))
    s1_suffix = "".join(rng.choice(_ALPHA) for _ in range(max(0, n - len(s1_prefix) - common_len)))
    s2_suffix = "".join(rng.choice(_ALPHA) for _ in range(max(0, n - len(s2_prefix) - common_len)))
    s1 = (s1_prefix + common + s1_suffix)[:n]
    s2 = (s2_prefix + common + s2_suffix)[:n]
    return s1, s2


def _lcs_dp(s1: str, s2: str):
    """Returns (length, dp_table)."""
    m, n2 = len(s1), len(s2)
    dp = [[0] * (n2 + 1) for _ in range(m + 1)]
    best = 0
    for i in range(1, m + 1):
        for j in range(1, n2 + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
                best = max(best, dp[i][j])
            else:
                dp[i][j] = 0
    return best, dp


class LongestCommonSubstringSimulation(AlgorithmPlugin):
    """Longest Common Substring."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="longest-common-substring",
            name="Longest Common Substring",
            category="string",
            visualization_type="MATRIX",
            description="Find the longest contiguous substring shared by two strings using DP.",
            intuition=(
                "dp[i][j] = common suffix length ending at s1[i-1] and s2[j-1]. "
                "dp[i][j] = dp[i-1][j-1]+1 if chars match, else 0. Track global max."
            ),
            complexity_time_best="O(m·n)",
            complexity_time_average="O(m·n)",
            complexity_time_worst="O(m·n)",
            complexity_space="O(m·n)",
            tags=("string", "longest-common-substring", "dynamic-programming"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 6))
        s1, s2 = _make_strings(rng, n)
        best, _ = _lcs_dp(s1, s2)
        # Table: (m+1) rows x (n+1) cols, initialized to 0
        m2, n2 = len(s1), len(s2)
        table = tuple(tuple([0] * (n2 + 1)) for _ in range(m2 + 1))
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"LCS-substring '{s1}' vs '{s2}' expected={best}",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        desc = initial_state.description
        parts = desc.split("'")
        s1, s2 = parts[1], parts[3]
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        best = 0
        computed: set = set()

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                    if dp[i][j] > best:
                        best = dp[i][j]
                computed.add((i, j))
                yield DPState(
                    table=tuple(tuple(row) for row in dp),
                    current_cell=(i, j),
                    computed_cells=frozenset(computed),
                    description=(
                        f"dp[{i}][{j}]: '{s1[i-1]}' vs '{s2[j-1]}' → {dp[i][j]} (best={best})"
                    ),
                )

        return DPState(
            table=tuple(tuple(row) for row in dp),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Longest common substring length = {best}",
        )
