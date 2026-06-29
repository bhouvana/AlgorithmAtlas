"""Longest Palindromic Substring plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)


def _make_string(rng: random.Random, n: int) -> str:
    """Generate a string with a guaranteed palindrome of length >= 3."""
    alphabet = "abcde"
    s = list(rng.choice(alphabet) for _ in range(n))
    # Inject a palindrome
    pal_len = rng.randint(3, min(5, n))
    pos = rng.randint(0, n - pal_len)
    half = [rng.choice(alphabet) for _ in range(pal_len // 2)]
    if pal_len % 2 == 0:
        pal = half + half[::-1]
    else:
        mid = rng.choice(alphabet)
        pal = half + [mid] + half[::-1]
    for i, ch in enumerate(pal):
        s[pos + i] = ch
    return "".join(s)


def _expand(s: str, lo: int, hi: int):
    """Expand palindrome outward, return (lo, hi) of the palindrome."""
    while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
        lo -= 1
        hi += 1
    return lo + 1, hi - 1


class LongestPalindromicSubstringSimulation(AlgorithmPlugin):
    """
    Longest Palindromic Substring — expand-around-center O(n²).

    DPState table rows:
      row 0: character codes (ord values)
      row 1: best palindrome length centered here (odd centers)
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="longest-palindromic-substring",
            name="Longest Palindromic Substring",
            category="string",
            visualization_type="MATRIX",
            description=(
                "Find the longest contiguous palindromic substring "
                "by expanding around each possible center."
            ),
            intuition=(
                "For each center (character or gap between characters), "
                "expand outward while s[lo]==s[hi]. "
                "Track the maximum expansion found."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(1)",
            tags=("string", "palindrome", "substring", "expand-around-center"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n: int = max(5, min(params.inputs.get("array_size", 8), 12))
        s = _make_string(rng, n)
        chars = tuple(ord(c) for c in s)
        lengths = tuple(1 for _ in range(n))
        return DPState(
            table=(chars, lengths),
            current_cell=None,
            computed_cells=frozenset(),
            description=f"LPS_sub('{s}'): expand around each center",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        s = initial_state.description.split("'")[1]
        n = len(s)
        chars = tuple(ord(c) for c in s)
        lengths = list(initial_state.table[1])
        computed: set = set()
        best_lo, best_hi = 0, 0

        # Odd-length centers
        for center in range(n):
            lo, hi = _expand(s, center, center)
            plen = hi - lo + 1
            lengths[center] = plen
            computed.add((1, center))
            if plen > best_hi - best_lo + 1:
                best_lo, best_hi = lo, hi
            yield DPState(
                table=(chars, tuple(lengths)),
                current_cell=(0, center),
                computed_cells=frozenset(computed),
                description=(
                    f"Odd center {center} ('{s[center]}'): "
                    f"palindrome='{s[lo:hi+1]}' len={plen}"
                ),
            )

        # Even-length centers
        for center in range(n - 1):
            if s[center] == s[center + 1]:
                lo, hi = _expand(s, center, center + 1)
                plen = hi - lo + 1
                if plen > best_hi - best_lo + 1:
                    best_lo, best_hi = lo, hi
                yield DPState(
                    table=(chars, tuple(lengths)),
                    current_cell=(0, center),
                    computed_cells=frozenset(computed),
                    description=(
                        f"Even center {center}-{center+1}: "
                        f"palindrome='{s[lo:hi+1]}' len={plen}"
                    ),
                )

        best_pal = s[best_lo:best_hi + 1]
        return DPState(
            table=(chars, tuple(lengths)),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Longest palindrome: '{best_pal}' (len={len(best_pal)})",
        )
