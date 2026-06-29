"""Word Break DP plugin for Algorithm Atlas.

The DP array dp[0..n] is shown as a 1-row table.
dp[i] = 1 (True) or 0 (False): can s[0..i-1] be segmented?
"""
from __future__ import annotations

import random
from typing import Generator, List, Set

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

# Fixed word bank — short words for clear visualization
_WORD_BANK = [
    "cat", "cats", "and", "sand", "dog", "leetcode", "leet",
    "code", "apple", "pen", "pine", "pineapple", "ap",
    "i", "like", "sam", "sung", "samsung", "mobile",
]

_STRINGS = [
    "leetcode",
    "applepenapple",
    "catsanddog",
    "pineapple",
    "ilikesamsung",
]


class WordBreakSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="word-break",
            name="Word Break",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Determine if a string can be segmented into words from a dictionary using DP.",
            intuition="dp[i] = True if s[0..i-1] can be segmented. For each i, check if dp[j] is True and s[j..i-1] is in the dictionary.",
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n)",
            tags=("dynamic-programming", "word-break", "string", "dictionary"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        idx = params.seed % len(_STRINGS)
        s = _STRINGS[idx]
        n = len(s)
        dp = [0] * (n + 1)
        dp[0] = 1  # empty prefix is always segmentable
        # Encode string as ASCII values in first row, dp in second row
        char_codes = [ord(c) for c in s]
        # Pad char_codes to length n+1 with 0 for index 0 slot
        row0 = tuple([0] + char_codes)  # row0[i] = ord(s[i-1]) for i >= 1
        return DPState(
            table=(row0, tuple(dp)),
            current_cell=None,
            computed_cells=frozenset({(1, 0)}),
            description=f'WordBreak("{s}")',
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        desc = initial_state.description
        s = desc[11:-2]  # strip 'WordBreak("' and '")'
        n = len(s)
        word_set: Set[str] = set(_WORD_BANK)

        dp = [False] * (n + 1)
        dp[0] = True
        computed: set = {(1, 0)}

        row0 = initial_state.table[0]

        def make_table():
            return (row0, tuple(1 if v else 0 for v in dp))

        for i in range(1, n + 1):
            for j in range(i):
                if dp[j]:
                    word = s[j:i]
                    in_dict = word in word_set
                    yield DPState(
                        table=make_table(),
                        current_cell=(1, i),
                        computed_cells=frozenset(computed),
                        description=f"dp[{j}]=T, s[{j}:{i}]='{word}' {'∈' if in_dict else '∉'} dict",
                    )
                    if in_dict:
                        dp[i] = True
                        break
            computed.add((1, i))
            yield DPState(
                table=make_table(),
                current_cell=(1, i),
                computed_cells=frozenset(computed),
                description=f"dp[{i}] = {'True' if dp[i] else 'False'} (s[0:{i}]='{s[:i]}')",
            )

        result = dp[n]
        return DPState(
            table=make_table(),
            current_cell=None,
            computed_cells=frozenset((1, i) for i in range(n + 1)),
            description=f'"{s}" {"CAN" if result else "CANNOT"} be segmented',
        )
