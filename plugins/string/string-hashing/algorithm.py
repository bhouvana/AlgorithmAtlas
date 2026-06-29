"""String Hashing (Polynomial Rolling Hash) plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_BASE = 31
_MOD = 10**9 + 7
_EXAMPLES = ["hello", "abracadabra", "algorithm", "banana", "mississippi"]


def _char_val(c: str) -> int:
    return ord(c.lower()) - ord('a') + 1  # 1..26


class StringHashingSimulation(AlgorithmPlugin):
    """Polynomial rolling hash prefix computation."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="string-hashing",
            name="String Hashing (Polynomial Rolling Hash)",
            category="string",
            visualization_type="ARRAY_BARS",
            description=f"H[i] = H[i-1]*{_BASE} + char_val(s[i]) mod {_MOD}. Visualize prefix hashes.",
            intuition=(
                f"Each prefix hash = previous_hash × {_BASE} + char_value. "
                "Equal substrings have equal hashes (with high probability). "
                "Used for O(1) substring comparison after O(n) preprocessing."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("string", "hashing", "rolling-hash", "polynomial"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        s = _EXAMPLES[params.seed % len(_EXAMPLES)]
        # array = char values (1-26 scaled to 1-99)
        arr = tuple(max(1, min(99, _char_val(c) * 4)) for c in s)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"StrHash input='{s}' base={_BASE} mod={_MOD}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        s = re.search(r"input='([^']+)'", initial_state.description).group(1)
        n = len(s)
        arr = initial_state.array

        h = 0
        hashes = []

        for i, c in enumerate(s):
            h = (h * _BASE + _char_val(c)) % _MOD
            hashes.append(h)
            # Scale hash to 1-99 for bar: use h % 100 (modular visual)
            display = max(1, min(99, (h % 100) or 1))

            # Rebuild display array: done positions show scaled hash mod 100
            bars = list(arr)
            for j, hj in enumerate(hashes):
                bars[j] = max(1, min(99, (hj % 100) or 1))

            yield SortState(
                array=tuple(bars),
                comparing=(i, i),
                last_swap=(i - 1, i) if i > 0 else (0, 0),
                sorted_indices=frozenset(range(i + 1)),
                comparisons=i + 1,
                swaps=h % 10000,  # last 4 digits of hash for display
                description=(
                    f"H[{i}]=H[{i-1}]×{_BASE}+'{c}'={h} "
                    f"(mod {_MOD})"
                ),
            )

        return SortState(
            array=tuple(max(1, min(99, (hj % 100) or 1)) for hj in hashes),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=n,
            swaps=h % 10000,
            description=f"Done: {n} prefix hashes computed. H[{n-1}]={h}",
        )
