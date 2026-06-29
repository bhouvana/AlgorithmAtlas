"""Huffman Coding greedy plugin for Algorithm Atlas.

Visualized as ARRAY_BARS: the array holds current node frequencies
sorted ascending, shrinking by 1 each merge step.
sorted_indices shows which slots have already been merged away.
"""
from __future__ import annotations

import heapq
import random
from typing import Generator, List, Optional, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_SYMBOL_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class HuffmanCodingSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="huffman-coding",
            name="Huffman Coding",
            category="greedy",
            visualization_type="ARRAY_BARS",
            description="Build an optimal prefix-free code by greedily merging the two lowest-frequency symbols.",
            intuition="Use a min-heap. Repeatedly merge the two lowest-frequency nodes into a parent with combined frequency. The resulting binary tree assigns shorter codes to higher-frequency symbols.",
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n)",
            tags=("greedy", "huffman", "compression", "prefix-free-code", "min-heap"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("array_size", 6), 8))
        # Frequencies 1..30, distinct and sorted
        freqs = sorted(rng.sample(range(1, 40), n))
        symbols = list(_SYMBOL_CHARS[:n])
        sym_str = ",".join(f"{s}:{f}" for s, f in zip(symbols, freqs))
        return SortState(
            array=tuple(freqs),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"symbols={sym_str}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        freqs = list(initial_state.array)
        n = len(freqs)
        sym_str = initial_state.description.split("symbols=")[1]
        sym_freqs = [(p.split(":")[0], int(p.split(":")[1])) for p in sym_str.split(",")]

        # Build min-heap: (frequency, index, label)
        # index used as tiebreaker for stable ordering
        heap = [(f, i, s) for i, (s, f) in enumerate(sym_freqs)]
        heapq.heapify(heap)

        # Track current "active" frequencies for visualization
        active_freqs = list(freqs)
        removed: List[int] = []
        comparisons = 0
        merge_count = 0

        def current_array() -> Tuple[int, ...]:
            return tuple(active_freqs)

        while len(heap) > 1:
            # Pop two lowest-frequency nodes
            f1, i1, s1 = heapq.heappop(heap)
            f2, i2, s2 = heapq.heappop(heap)
            comparisons += 1
            merged_freq = f1 + f2
            merge_count += 1

            yield SortState(
                array=current_array(),
                comparing=(min(i1, i2), max(i1, i2)),
                last_swap=None,
                sorted_indices=frozenset(removed),
                comparisons=comparisons,
                swaps=merge_count,
                description=f"Merge '{s1}'({f1}) + '{s2}'({f2}) → node({merged_freq})",
            )

            # Update visualization: replace first slot with merged, mark second as removed
            active_freqs[min(i1, i2)] = merged_freq
            removed.append(max(i1, i2))

            new_idx = min(i1, i2)
            new_label = f"({s1}+{s2})"
            heapq.heappush(heap, (merged_freq, new_idx, new_label))

            yield SortState(
                array=current_array(),
                comparing=None,
                last_swap=(min(i1, i2), max(i1, i2)),
                sorted_indices=frozenset(removed),
                comparisons=comparisons,
                swaps=merge_count,
                description=f"Merged node({merged_freq}) placed — {n - merge_count - 1} nodes remain",
            )

        return SortState(
            array=current_array(),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(1, n)),  # only root remains active
            comparisons=comparisons,
            swaps=merge_count,
            description=f"Huffman tree built — {merge_count} merges, root freq={heap[0][0] if heap else freqs[0]}",
        )
