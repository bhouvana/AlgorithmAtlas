"""Rabin-Karp rolling-hash string search plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List, Optional

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SearchState,
    SimulationParams,
)

_CHARS = "AABCDE"
_BASE = 31
_MOD = 10_007


def _random_text(rng: random.Random, n: int) -> str:
    return "".join(rng.choices(_CHARS, k=n))


def _hash(s: str) -> int:
    h = 0
    for c in s:
        h = (h * _BASE + ord(c)) % _MOD
    return h


def _roll(old_hash: int, out_char: str, in_char: str, high_power: int) -> int:
    """Remove out_char from front, add in_char to back."""
    h = (old_hash - ord(out_char) * high_power % _MOD + _MOD) % _MOD
    h = (h * _BASE + ord(in_char)) % _MOD
    return h


class RabinKarpSimulation(AlgorithmPlugin):
    """
    Rabin-Karp — O(n+m) average, O(n·m) worst.

    Encodes text as ASCII values in SearchState.array.
    current: right edge of rolling window.
    low/high: rolling window [left, right].
    eliminated: confirmed non-match windows.
    found_at: first match position.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="rabin-karp",
            name="Rabin-Karp String Search",
            category="string",
            visualization_type="ARRAY_BARS_SEARCH",
            description="Rolling-hash string search: slide a hash window over the text in O(1) per step.",
            intuition="Hash the pattern. Slide a same-length window across text updating the hash in O(1). Only verify character-by-character on a hash collision (spurious hit).",
            complexity_time_best="O(n + m)",
            complexity_time_average="O(n + m)",
            complexity_time_worst="O(n·m)",
            complexity_space="O(1)",
            tags=("string", "pattern-matching", "rolling-hash", "rabin-karp"),
        )

    def initialize(self, params: SimulationParams) -> SearchState:
        rng = random.Random(params.seed)
        n: int = max(16, min(params.inputs.get("text_length", 20), 32))
        text = _random_text(rng, n)
        pattern = _random_text(rng, 3)
        return SearchState(
            array=tuple(ord(c) for c in text),
            target=_hash(pattern) % 256,  # hash as the "target" value for display
            current=None,
            low=0,
            high=len(pattern) - 1,
            eliminated=frozenset(),
            found_at=None,
            comparisons=0,
            description=f'Rabin-Karp: text[{n}] pattern="{pattern}"',
        )

    def steps(
        self, initial_state: SearchState
    ) -> Generator[SearchState, None, SearchState]:
        text = "".join(chr(c) for c in initial_state.array)
        n = len(text)
        desc0 = initial_state.description
        pattern = desc0.split('pattern="')[1].rstrip('"')
        m = len(pattern)
        comparisons = 0
        no_match_windows: set = set()

        if m > n:
            return SearchState(
                array=initial_state.array,
                target=initial_state.target,
                current=None,
                low=None,
                high=None,
                eliminated=frozenset(),
                found_at=None,
                comparisons=0,
                description=f'Pattern longer than text — not found',
            )

        pattern_hash = _hash(pattern)
        # high_power = BASE^(m-1) mod MOD
        high_power = 1
        for _ in range(m - 1):
            high_power = (high_power * _BASE) % _MOD

        window_hash = _hash(text[:m])

        for i in range(n - m + 1):
            comparisons += 1
            is_match = (window_hash == pattern_hash)
            if is_match:
                # Verify character by character
                is_match = text[i:i + m] == pattern

            yield SearchState(
                array=initial_state.array,
                target=initial_state.target,
                current=i + m - 1,
                low=i,
                high=i + m - 1,
                eliminated=frozenset(no_match_windows),
                found_at=None,
                comparisons=comparisons,
                description=(
                    f"Window [{i},{i+m-1}]=\"{text[i:i+m]}\" hash={window_hash} "
                    + ("== pattern_hash ✓" if window_hash == pattern_hash else "≠ pattern_hash")
                ),
            )

            if is_match:
                return SearchState(
                    array=initial_state.array,
                    target=initial_state.target,
                    current=None,
                    low=i,
                    high=i + m - 1,
                    eliminated=frozenset(no_match_windows),
                    found_at=i,
                    comparisons=comparisons,
                    description=f'Found "{pattern}" at index {i}! {comparisons} windows checked',
                )

            no_match_windows.add(i)
            if i + m < n:
                window_hash = _roll(window_hash, text[i], text[i + m], high_power)

        return SearchState(
            array=initial_state.array,
            target=initial_state.target,
            current=None,
            low=None,
            high=None,
            eliminated=frozenset(range(n - m + 1)),
            found_at=None,
            comparisons=comparisons,
            description=f'"{pattern}" not found. {comparisons} windows checked',
        )
