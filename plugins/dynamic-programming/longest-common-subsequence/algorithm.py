"""Longest Common Subsequence (LCS) DP plugin for Algorithm Atlas."""
from __future__ import annotations

import random
import string
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _random_string(rng: random.Random, n: int) -> str:
    return "".join(rng.choices(_CHARS, k=n))


class LCSSimulation(AlgorithmPlugin):
    """
    Longest Common Subsequence via 2D bottom-up DP.

    dp[i][j] = LCS length of s1[:i] and s2[:j].
    - dp[0][j] = 0, dp[i][0] = 0  (base cases)
    - if s1[i-1] == s2[j-1]: dp[i][j] = dp[i-1][j-1] + 1
    - else:                  dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    Row labels = [ε, s1[0], s1[1], ...]  (ε = empty string)
    Col labels = [ε, s2[0], s2[1], ...]
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="longest-common-subsequence",
            name="Longest Common Subsequence",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Finds the LCS of two strings using a 2D DP table.",
            intuition="dp[i][j] = LCS length of first i chars of s1 and first j chars of s2. Match → extend diagonal; else max(left, above).",
            complexity_time_best="O(m·n)",
            complexity_time_average="O(m·n)",
            complexity_time_worst="O(m·n)",
            complexity_space="O(m·n)",
            tags=("dynamic-programming", "string", "subsequence", "lcs"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        length: int = max(4, min(params.inputs.get("string_length", 6), 10))
        s1 = _random_string(rng, length)
        s2 = _random_string(rng, length)

        # Store strings in description for reference
        m, n = len(s1), len(s2)
        table: Tuple[Tuple[int, ...], ...] = tuple(
            tuple(0 for _ in range(n + 1)) for _ in range(m + 1)
        )
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f'LCS("{s1}", "{s2}")',
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        # Reconstruct strings from initial table dimensions
        # We embed the strings in the first frame description — re-parse them
        desc = initial_state.description  # LCS("S1", "S2")
        parts = desc[5:-2].split('", "')
        s1, s2 = parts[0], parts[1]
        m, n = len(s1), len(s2)

        table: List[List[int]] = [[0] * (n + 1) for _ in range(m + 1)]
        computed: set = set()

        # Base cases (row 0 and col 0 are already 0)
        for j in range(n + 1):
            computed.add((0, j))
        for i in range(1, m + 1):
            computed.add((i, 0))

        yield DPState(
            table=tuple(tuple(r) for r in table),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f'Fill base cases (row 0 and col 0 = 0)',
        )

        # Fill table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    table[i][j] = table[i - 1][j - 1] + 1
                    desc = f"s1[{i-1}]='{s1[i-1]}' == s2[{j-1}]='{s2[j-1]}' → dp[{i}][{j}] = dp[{i-1}][{j-1}]+1 = {table[i][j]}"
                else:
                    table[i][j] = max(table[i - 1][j], table[i][j - 1])
                    desc = f"s1[{i-1}]='{s1[i-1]}' ≠ s2[{j-1}]='{s2[j-1]}' → max({table[i-1][j]},{table[i][j-1]}) = {table[i][j]}"
                computed.add((i, j))
                yield DPState(
                    table=tuple(tuple(r) for r in table),
                    current_cell=(i, j),
                    computed_cells=frozenset(computed),
                    description=desc,
                )

        lcs_len = table[m][n]
        return DPState(
            table=tuple(tuple(r) for r in table),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f'LCS("{s1}", "{s2}") = {lcs_len}',
        )
