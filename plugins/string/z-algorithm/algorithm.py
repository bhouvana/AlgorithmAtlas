"""Z-Algorithm string search plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SearchState,
    SimulationParams,
)

_CHARS = "AABCDE"


def _random_text(rng: random.Random, n: int) -> str:
    return "".join(rng.choices(_CHARS, k=n))


def _compute_z(s: str) -> List[int]:
    """Compute Z-array in O(n)."""
    n = len(s)
    z = [0] * n
    z[0] = n
    l, r = 0, 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z


class ZAlgorithmSimulation(AlgorithmPlugin):
    """
    Z-Algorithm — O(n + m).

    Builds Z-array for (pattern + '$' + text).
    SearchState.array: ASCII codes of text only.
    current: index in text being examined.
    low/high: current match window.
    found_at: first position where Z[i] == len(pattern).
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="z-algorithm",
            name="Z-Algorithm String Search",
            category="string",
            visualization_type="ARRAY_BARS_SEARCH",
            description="Finds pattern in text using Z-array (longest prefix match starting at each position).",
            intuition="Concatenate pattern + '$' + text. Z[i] = pattern length means pattern matches at text position i - (m+1).",
            complexity_time_best="O(n + m)",
            complexity_time_average="O(n + m)",
            complexity_time_worst="O(n + m)",
            complexity_space="O(n + m)",
            tags=("string", "pattern-matching", "z-array", "prefix-matching"),
        )

    def initialize(self, params: SimulationParams) -> SearchState:
        rng = random.Random(params.seed)
        n: int = max(16, min(params.inputs.get("text_length", 20), 32))
        text = _random_text(rng, n)
        pattern = _random_text(rng, 3)
        return SearchState(
            array=tuple(ord(c) for c in text),
            target=len(pattern),  # use target field to store pattern length
            current=None,
            low=0,
            high=len(pattern) - 1,
            eliminated=frozenset(),
            found_at=None,
            comparisons=0,
            description=f'Z-Algorithm: text[{n}] pattern="{pattern}"',
        )

    def steps(
        self, initial_state: SearchState
    ) -> Generator[SearchState, None, SearchState]:
        text = "".join(chr(c) for c in initial_state.array)
        n = len(text)
        desc = initial_state.description
        pattern = desc.split('pattern="')[1].rstrip('"')
        m = len(pattern)

        combined = pattern + "$" + text
        z = _compute_z(combined)

        matches: list = []
        processed: set = set()

        for i in range(m + 1, len(combined)):
            text_pos = i - (m + 1)
            processed.add(text_pos)

            yield SearchState(
                array=initial_state.array,
                target=m,
                current=text_pos,
                low=text_pos,
                high=min(text_pos + m - 1, n - 1),
                eliminated=frozenset(j for j in processed if j not in matches),
                found_at=matches[0] if matches else None,
                comparisons=len(processed),
                description=f"Z[{i}]={z[i]} at text[{text_pos}]=\"{text[text_pos:text_pos+m]}\""
                + (" ← MATCH!" if z[i] == m else ""),
            )

            if z[i] == m:
                matches.append(text_pos)

        if matches:
            return SearchState(
                array=initial_state.array,
                target=m,
                current=None,
                low=matches[0],
                high=matches[0] + m - 1,
                eliminated=frozenset(j for j in processed if j not in matches),
                found_at=matches[0],
                comparisons=len(processed),
                description=f'Found "{pattern}" at index {matches[0]} ({len(matches)} occurrence(s))',
            )

        return SearchState(
            array=initial_state.array,
            target=m,
            current=None,
            low=None,
            high=None,
            eliminated=frozenset(range(n)),
            found_at=None,
            comparisons=len(processed),
            description=f'"{pattern}" not found in text',
        )
