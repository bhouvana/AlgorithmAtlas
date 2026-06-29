"""Suffix Array Construction plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

_ALPHABET = "abcde"


def _make_string(rng: random.Random, n: int) -> str:
    return "".join(rng.choice(_ALPHABET) for _ in range(n))


def _build_suffix_array(s: str) -> list[int]:
    """Returns suffix array: sorted indices of all suffixes."""
    n = len(s)
    return sorted(range(n), key=lambda i: s[i:])


class SuffixArraySimulation(AlgorithmPlugin):
    """Suffix Array (naïve construction)."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="suffix-array",
            name="Suffix Array Construction",
            category="string",
            visualization_type="MATRIX",
            description="Sort all suffixes of a string to build an index enabling fast substring search.",
            intuition=(
                "Generate all n suffixes, sort them lexicographically. "
                "The SA[i] = start index of the i-th smallest suffix."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n² log n)",
            complexity_space="O(n)",
            tags=("string", "suffix-array", "sorting", "pattern-matching"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 7))
        s = _make_string(rng, n)
        sa = _build_suffix_array(s)

        # Table: n rows × n cols
        # Row i: chars of suffix starting at sa[i], padded with -1
        rows = []
        for idx in sa:
            suffix = s[idx:]
            row = tuple(ord(c) - ord('a') + 1 for c in suffix) + (0,) * (n - len(suffix))
            rows.append(row)

        return DPState(
            table=tuple(rows),
            current_cell=None,
            computed_cells=frozenset(),
            description=f"Build suffix array for '{s}'",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        desc = initial_state.description
        s = desc.split("'")[1]
        n = len(s)

        # Show each suffix being placed in sorted order
        suffixes = [(s[i:], i) for i in range(n)]
        # Sort step by step using insertion sort for visualization
        sorted_list: list = []
        computed: set = set()

        for suffix, orig_idx in sorted(suffixes):
            sorted_list.append((suffix, orig_idx))
            rank = sorted_list.index((suffix, orig_idx))
            computed.add((rank, 0))

            # Build current table
            rows = []
            for suf, _ in sorted_list:
                row = tuple(ord(c) - ord('a') + 1 for c in suf) + (0,) * (n - len(suf))
                rows.append(row)
            # Pad to n rows
            while len(rows) < n:
                rows.append((0,) * n)

            yield DPState(
                table=tuple(rows),
                current_cell=(rank, 0),
                computed_cells=frozenset(computed),
                description=f"Placed suffix '{suffix}' (starts at {orig_idx}) at rank {rank}",
            )

        sa = [idx for _, idx in sorted(suffixes)]
        return DPState(
            table=initial_state.table,
            current_cell=None,
            computed_cells=frozenset(range(n) for _ in [None]),
            description=f"Suffix array = {sa}",
        )
