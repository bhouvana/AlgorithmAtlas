"""Manacher's Algorithm plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SearchState,
    SimulationParams,
)

_CHARS = "AABBC"


class ManacherSimulation(AlgorithmPlugin):
    """
    Manacher's Algorithm — O(n) longest palindromic substring.

    Works on the transformed string T = '#A#B#A#...' to handle even/odd lengths.
    p[i] = radius of palindrome centred at T[i].

    State encoding (SearchState):
      array:    ASCII values of the ORIGINAL string s (for display)
      target:   radius of best palindrome found so far
      current:  current centre being processed (in original indices)
      low:      best palindrome start in original string
      high:     best palindrome end in original string
      comparisons: total character comparisons made
      description: "Manacher: n=... bestLen=..."
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="manacher",
            name="Manacher's Algorithm",
            category="string",
            visualization_type="ARRAY_BARS_SEARCH",
            description=(
                "Find the longest palindromic substring in O(n) time "
                "using palindrome radii and the mirror property."
            ),
            intuition=(
                "Insert '#' between every character. For each centre, "
                "reuse the mirror palindrome's radius as a starting point. "
                "Expand only where the known boundary ends."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("string", "palindrome", "manacher"),
        )

    def initialize(self, params: SimulationParams) -> SearchState:
        rng = random.Random(params.seed)
        n: int = max(8, min(params.inputs.get("text_length", 12), 20))
        # Inject a known palindrome to keep the demo interesting
        s = list(rng.choices(_CHARS, k=n))
        pal_len = rng.randint(3, min(6, n))
        start = rng.randint(0, n - pal_len)
        half = pal_len // 2
        for i in range(half):
            s[start + pal_len - 1 - i] = s[start + i]
        text = "".join(s)

        return SearchState(
            array=tuple(ord(c) for c in text),
            target=0,
            current=None,
            low=0,
            high=0,
            eliminated=frozenset(),
            found_at=None,
            comparisons=0,
            description=f'Manacher: text="{text}"',
        )

    def steps(
        self, initial_state: SearchState
    ) -> Generator[SearchState, None, SearchState]:
        text = "".join(chr(c) for c in initial_state.array)
        n = len(text)

        # Transform: insert '#' between characters and at boundaries
        T = "#" + "#".join(text) + "#"
        N = len(T)
        p = [0] * N
        c, r = 0, 0  # current centre and right boundary

        comparisons = 0
        best_len = 1
        best_orig_centre = 0

        for i in range(N):
            mirror = 2 * c - i
            if i < r:
                p[i] = min(r - i, p[mirror])

            # Expand
            while i - p[i] - 1 >= 0 and i + p[i] + 1 < N and T[i - p[i] - 1] == T[i + p[i] + 1]:
                comparisons += 1
                p[i] += 1

            # Update rightmost palindrome
            if i + p[i] > r:
                c, r = i, i + p[i]

            # Convert to original string coordinates
            orig_len = p[i]  # radius in transformed string = radius in original chars (incl. #)
            # p[i] in T corresponds to palindrome of length p[i] in original string
            if orig_len > best_len:
                best_len = orig_len
                best_orig_centre = i

            # Map current centre to original index for visualization
            orig_i = (i - 1) // 2 if i % 2 == 1 else -1  # '#' positions map to -1

            yield SearchState(
                array=initial_state.array,
                target=best_len,
                current=orig_i if orig_i >= 0 else None,
                low=max(0, (best_orig_centre - best_len) // 2),
                high=min(n - 1, (best_orig_centre + best_len) // 2 - (0 if best_len % 2 == 0 else 0)),
                eliminated=frozenset(),
                found_at=None,
                comparisons=comparisons,
                description=(
                    f"Centre T[{i}]='{T[i]}', radius={p[i]}, "
                    f"bestLen={best_len}"
                ),
            )

        # Compute best palindrome bounds in original string
        pal_start = (best_orig_centre - best_len) // 2
        pal_end = pal_start + best_len - 1
        best_substr = text[pal_start:pal_end + 1]

        return SearchState(
            array=initial_state.array,
            target=best_len,
            current=None,
            low=pal_start,
            high=pal_end,
            eliminated=frozenset(),
            found_at=pal_start,
            comparisons=comparisons,
            description=(
                f'Done: longest palindrome = "{best_substr}" '
                f'(len={best_len}, [{pal_start},{pal_end}])'
            ),
        )
