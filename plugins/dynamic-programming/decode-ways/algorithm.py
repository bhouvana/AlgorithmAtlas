"""Decode Ways plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

# Hardcoded digit strings and expected answers
_INSTANCES = [
    ("12",    2),   # "AB" or "L"
    ("226",   3),   # "BZ", "VF", "BBF" → actually "BBF","BZ","VF" = 3
    ("06",    0),   # leading zero → 0 ways
    ("11106", 2),
    ("111",   3),
    ("1234",  3),
    ("2101",  1),
    ("10",    1),
    ("27",    1),
    ("1111",  5),
]


def _decode_count(s: str) -> int:
    n = len(s)
    dp = [0] * (n + 1)
    dp[0] = 1
    dp[1] = 1 if s[0] != "0" else 0
    for i in range(2, n + 1):
        one = int(s[i-1])
        two = int(s[i-2:i])
        if one >= 1:
            dp[i] += dp[i-1]
        if 10 <= two <= 26:
            dp[i] += dp[i-2]
    return dp[n]


class DecodeWaysSimulation(AlgorithmPlugin):
    """Decode Ways DP."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="decode-ways",
            name="Decode Ways",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description=(
                "Count distinct ways to decode a digit string where A=1, B=2, …, Z=26."
            ),
            intuition=(
                "dp[i] = ways to decode first i characters. "
                "Add dp[i-1] for single-digit decode; add dp[i-2] for two-digit (10-26)."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("dynamic-programming", "string", "decode-ways"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        s, expected = _INSTANCES[params.seed % len(_INSTANCES)]
        n = len(s)
        # Row 0: char codes, Row 1: dp values (initially 0s)
        dp = [0] * (n + 1)
        dp[0] = 1
        dp[1] = 1 if s[0] != "0" else 0
        row0 = tuple(ord(c) - ord("0") for c in s) + (0,)  # length n+1
        row1 = tuple(dp)
        return DPState(
            table=(row0, row1),
            current_cell=None,
            computed_cells=frozenset(),
            description=f"Decode '{s}' expected={expected}",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        desc = initial_state.description
        s = desc.split("'")[1]
        n = len(s)

        dp = [0] * (n + 1)
        dp[0] = 1
        dp[1] = 1 if s[0] != "0" else 0
        computed = {(1, 0), (1, 1)}

        row0 = initial_state.table[0]

        yield DPState(
            table=(row0, tuple(dp)),
            current_cell=(1, 1),
            computed_cells=frozenset(computed),
            description=f"Base: dp[0]=1, dp[1]={dp[1]} (s[0]={s[0]})",
        )

        for i in range(2, n + 1):
            one = int(s[i-1])
            two = int(s[i-2:i])
            if one >= 1:
                dp[i] += dp[i-1]
            if 10 <= two <= 26:
                dp[i] += dp[i-2]
            computed.add((1, i))

            yield DPState(
                table=(row0, tuple(dp)),
                current_cell=(1, i),
                computed_cells=frozenset(computed),
                description=(
                    f"i={i}: digit={s[i-1]} two_digit={s[i-2:i]} → dp[{i}]={dp[i]}"
                ),
            )

        return DPState(
            table=(row0, tuple(dp)),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Ways to decode '{s}' = {dp[n]}",
        )
