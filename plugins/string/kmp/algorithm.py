"""KMP (Knuth-Morris-Pratt) string search plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List, Optional, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SearchState,
    SimulationParams,
)

_CHARS = "AABCDE"  # limited alphabet → increases match/mismatch variety


def _random_text(rng: random.Random, n: int) -> str:
    return "".join(rng.choices(_CHARS, k=n))


def _build_failure(pattern: str) -> List[int]:
    """KMP failure (partial match) table."""
    m = len(pattern)
    f = [0] * m
    k = 0
    for i in range(1, m):
        while k > 0 and pattern[k] != pattern[i]:
            k = f[k - 1]
        if pattern[k] == pattern[i]:
            k += 1
        f[i] = k
    return f


class KMPSimulation(AlgorithmPlugin):
    """
    KMP string search — O(n + m).

    Encodes text as ASCII values in SearchState.array.
    current: text index being compared.
    low/high: current active match window [i-j, i-1].
    eliminated: confirmed non-match starting positions.
    found_at: index where pattern was found (first occurrence).
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="kmp",
            name="KMP String Search",
            category="string",
            visualization_type="ARRAY_BARS_SEARCH",
            description="Finds a pattern in text using the KMP failure function to avoid redundant comparisons.",
            intuition="Precompute how far to shift on mismatch — never re-examine a character that already matched a prefix of the pattern.",
            complexity_time_best="O(n)",
            complexity_time_average="O(n + m)",
            complexity_time_worst="O(n + m)",
            complexity_space="O(m)",
            tags=("string", "pattern-matching", "kmp", "failure-function"),
        )

    def initialize(self, params: SimulationParams) -> SearchState:
        rng = random.Random(params.seed)
        n: int = max(16, min(params.inputs.get("text_length", 20), 32))
        pattern_len = 3
        text = _random_text(rng, n)
        pattern = _random_text(rng, pattern_len)
        # Store pattern in description for step reconstruction
        return SearchState(
            array=tuple(ord(c) for c in text),
            target=ord(pattern[0]),
            current=None,
            low=0,
            high=pattern_len - 1,
            eliminated=frozenset(),
            found_at=None,
            comparisons=0,
            description=f'KMP: text[{n}] pattern="{pattern}"',
        )

    def steps(
        self, initial_state: SearchState
    ) -> Generator[SearchState, None, SearchState]:
        text = "".join(chr(c) for c in initial_state.array)
        n = len(text)
        desc0 = initial_state.description
        # Parse pattern from description: pattern="XXX"
        pattern = desc0.split('pattern="')[1].rstrip('"')
        m = len(pattern)
        failure = _build_failure(pattern)
        comparisons = 0
        j = 0  # match length so far
        no_match_starts: set = set()

        for i in range(n):
            comparisons += 1
            yield SearchState(
                array=initial_state.array,
                target=ord(pattern[j]),
                current=i,
                low=i - j,
                high=i - j + m - 1,
                eliminated=frozenset(no_match_starts),
                found_at=None,
                comparisons=comparisons,
                description=f"Compare text[{i}]='{text[i]}' with pattern[{j}]='{pattern[j]}'",
            )

            while j > 0 and text[i] != pattern[j]:
                no_match_starts.add(i - j)
                j = failure[j - 1]
                yield SearchState(
                    array=initial_state.array,
                    target=ord(pattern[j]),
                    current=i,
                    low=i - j,
                    high=i - j + m - 1,
                    eliminated=frozenset(no_match_starts),
                    found_at=None,
                    comparisons=comparisons,
                    description=f"Mismatch — shift to j={j} via failure table",
                )

            if text[i] == pattern[j]:
                j += 1

            if j == m:
                match_start = i - m + 1
                return SearchState(
                    array=initial_state.array,
                    target=ord(pattern[0]),
                    current=None,
                    low=match_start,
                    high=match_start + m - 1,
                    eliminated=frozenset(no_match_starts),
                    found_at=match_start,
                    comparisons=comparisons,
                    description=f'Found "{pattern}" at index {match_start}! {comparisons} comparisons',
                )
                j = failure[j - 1]

        return SearchState(
            array=initial_state.array,
            target=ord(pattern[0]),
            current=None,
            low=None,
            high=None,
            eliminated=frozenset(range(n)),
            found_at=None,
            comparisons=comparisons,
            description=f'"{pattern}" not found in text. {comparisons} comparisons',
        )
