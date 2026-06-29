"""Boyer-Moore (Bad Character) string search plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SearchState,
    SimulationParams,
)

_CHARS = "AABCDE"


def _random_text(rng: random.Random, n: int) -> str:
    return "".join(rng.choices(_CHARS, k=n))


def _bad_char_table(pattern: str) -> dict:
    """Rightmost occurrence of each char in pattern (excluding last position)."""
    table: dict = {}
    for i, c in enumerate(pattern):
        table[c] = i
    return table


class BoyerMooreSimulation(AlgorithmPlugin):
    """
    Boyer-Moore (Bad Character heuristic) — compare right-to-left, shift on mismatch.

    Encodes text as ASCII in array. Pattern stored in description.
    current: text index currently being compared.
    low/high: window [shift, shift + m - 1] in text.
    found_at: match start index.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="boyer-moore",
            name="Boyer-Moore String Search",
            category="string",
            visualization_type="ARRAY_BARS_SEARCH",
            description=(
                "Pattern search using the bad-character heuristic: "
                "compare right-to-left and skip ahead on mismatch."
            ),
            intuition=(
                "Compare pattern to text from right to left within the current window. "
                "On mismatch, shift so that the mismatched text character aligns with "
                "its rightmost occurrence in the pattern (or skip past it)."
            ),
            complexity_time_best="O(n/m)",
            complexity_time_average="O(n+m)",
            complexity_time_worst="O(nm)",
            complexity_space="O(alphabet)",
            tags=("string", "pattern-matching", "boyer-moore", "bad-character"),
        )

    def initialize(self, params: SimulationParams) -> SearchState:
        rng = random.Random(params.seed)
        n: int = max(16, min(params.inputs.get("text_length", 20), 32))
        pattern_len = 3
        text = _random_text(rng, n)
        pattern = _random_text(rng, pattern_len)
        return SearchState(
            array=tuple(ord(c) for c in text),
            target=ord(pattern[0]),
            current=None,
            low=0,
            high=pattern_len - 1,
            eliminated=frozenset(),
            found_at=None,
            comparisons=0,
            description=f'BoyerMoore: text[{n}] pattern="{pattern}"',
        )

    def steps(
        self, initial_state: SearchState
    ) -> Generator[SearchState, None, SearchState]:
        text = "".join(chr(c) for c in initial_state.array)
        n = len(text)
        desc0 = initial_state.description
        pattern = desc0.split('pattern="')[1].rstrip('"')
        m = len(pattern)

        bad_char = _bad_char_table(pattern)
        comparisons = 0
        shift = 0
        no_match_starts: set = set()

        while shift <= n - m:
            j = m - 1  # start from rightmost char

            while j >= 0:
                comparisons += 1
                ti = shift + j
                yield SearchState(
                    array=initial_state.array,
                    target=ord(pattern[j]),
                    current=ti,
                    low=shift,
                    high=shift + m - 1,
                    eliminated=frozenset(no_match_starts),
                    found_at=None,
                    comparisons=comparisons,
                    description=(
                        f"Compare text[{ti}]='{text[ti]}' with pattern[{j}]='{pattern[j]}'"
                    ),
                )
                if text[ti] != pattern[j]:
                    break
                j -= 1

            if j < 0:
                # Full match
                return SearchState(
                    array=initial_state.array,
                    target=ord(pattern[0]),
                    current=None,
                    low=shift,
                    high=shift + m - 1,
                    eliminated=frozenset(no_match_starts),
                    found_at=shift,
                    comparisons=comparisons,
                    description=f'Found "{pattern}" at index {shift}! {comparisons} comparisons',
                )
            else:
                # Bad character: shift so mismatched char aligns
                bad_c = text[shift + j]
                bc_shift = max(1, j - bad_char.get(bad_c, -1))
                no_match_starts.add(shift)
                yield SearchState(
                    array=initial_state.array,
                    target=ord(pattern[0]),
                    current=shift + j,
                    low=shift,
                    high=shift + m - 1,
                    eliminated=frozenset(no_match_starts),
                    found_at=None,
                    comparisons=comparisons,
                    description=(
                        f"Mismatch on '{bad_c}': bad-char shift = {bc_shift}"
                    ),
                )
                shift += bc_shift

        return SearchState(
            array=initial_state.array,
            target=ord(pattern[0]),
            current=None,
            low=None,
            high=None,
            eliminated=frozenset(range(n)),
            found_at=None,
            comparisons=comparisons,
            description=f'"{pattern}" not found. {comparisons} comparisons',
        )
