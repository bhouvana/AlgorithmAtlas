"""Sequence Alignment (Needleman-Wunsch) plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_MATCH = 1
_MISMATCH = -1
_GAP = -2

_PAIRS = [
    ("ACGT", "AGCT"),
    ("GATTACA", "GCATGCU"),
    ("AGTACG", "ACATCG"),
    ("ATCG", "TACG"),
    ("GCAG", "GCTA"),
]


def _nw(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i * _GAP
    for j in range(n + 1):
        dp[0][j] = j * _GAP
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = _MATCH if s1[i - 1] == s2[j - 1] else _MISMATCH
            dp[i][j] = max(
                dp[i - 1][j - 1] + match,
                dp[i - 1][j] + _GAP,
                dp[i][j - 1] + _GAP,
            )
    return dp


def _traceback(dp, s1, s2):
    i, j = len(s1), len(s2)
    a1, a2 = [], []
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            match = _MATCH if s1[i - 1] == s2[j - 1] else _MISMATCH
            if dp[i][j] == dp[i - 1][j - 1] + match:
                a1.append(s1[i - 1])
                a2.append(s2[j - 1])
                i -= 1
                j -= 1
                continue
        if i > 0 and dp[i][j] == dp[i - 1][j] + _GAP:
            a1.append(s1[i - 1])
            a2.append("-")
            i -= 1
        else:
            a1.append("-")
            a2.append(s2[j - 1])
            j -= 1
    return "".join(reversed(a1)), "".join(reversed(a2))


class SequenceAlignmentSimulation(AlgorithmPlugin):
    """Needleman-Wunsch sequence alignment."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="sequence-alignment",
            name="Sequence Alignment (Needleman-Wunsch)",
            category="dynamic-programming",
            visualization_type="ARRAY_BARS",
            description="Global sequence alignment: match=+1, mismatch=-1, gap=-2.",
            intuition=(
                "dp[i][j] = score aligning s1[0..i] and s2[0..j]. "
                "Each cell = max(diagonal±score, left-gap, up-gap). "
                "Traceback from bottom-right recovers the optimal alignment."
            ),
            complexity_time_best="O(m·n)",
            complexity_time_average="O(m·n)",
            complexity_time_worst="O(m·n)",
            complexity_space="O(m·n)",
            tags=("dynamic-programming", "sequence-alignment", "needleman-wunsch", "bioinformatics"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        s1, s2 = _PAIRS[params.seed % len(_PAIRS)]
        n = len(s2)
        arr = tuple(j * abs(_GAP) for j in range(n + 1))
        mx = max(arr) or 1
        arr = tuple(max(1, min(99, v * 99 // mx)) for v in arr)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset([0]),
            comparisons=0,
            swaps=0,
            description=f"NW s1='{s1}' s2='{s2}'",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        s1 = re.search(r"s1='([^']+)'", initial_state.description).group(1)
        s2 = re.search(r"s2='([^']+)'", initial_state.description).group(1)
        m, n = len(s1), len(s2)
        dp = _nw(s1, s2)

        for i in range(1, m + 1):
            row = dp[i]
            # Shift row values to be non-negative for display
            mn = min(row)
            shifted = [v - mn for v in row]
            mx = max(shifted) or 1
            arr = tuple(max(1, min(99, v * 99 // mx)) for v in shifted)
            yield SortState(
                array=arr,
                comparing=(i - 1, i - 1),
                last_swap=(i - 1, i - 1) if any(s1[i - 1] == s2[j] for j in range(n)) else None,
                sorted_indices=frozenset(range(i)),
                comparisons=i,
                swaps=dp[i][n],
                description=f"Row {i} (s1[{i-1}]='{s1[i-1]}'): best={dp[i][n]}",
            )

        a1, a2 = _traceback(dp, s1, s2)
        final_score = dp[m][n]
        return SortState(
            array=initial_state.array,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(m)),
            comparisons=m,
            swaps=final_score,
            description=f"Score={final_score} | '{a1}' | '{a2}'",
        )
