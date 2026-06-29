"""Patience Sort plugin for Algorithm Atlas."""
from __future__ import annotations

import heapq
import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class PatienceSortSimulation(AlgorithmPlugin):
    """Patience sort: pile-building + heap-merge."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="patience-sort",
            name="Patience Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description="Sort by dealing cards into piles, then merging with a min-heap.",
            intuition=(
                "Place each card on the leftmost pile whose top ≥ it, or start a new pile. "
                "Pile tops stay sorted. #piles = LIS length. "
                "Merge all piles with a min-heap in O(n log n)."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n)",
            tags=("sorting", "patience", "lis", "heap", "merge"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 12))
        arr = [rng.randint(1, 99) for _ in range(n)]
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Patience sort n={n}: input={arr}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        n = len(arr)

        piles: list[list[int]] = []  # each pile is a stack

        # Phase 1: pile building
        for i, card in enumerate(arr):
            # Binary search for leftmost pile top >= card
            lo, hi = 0, len(piles)
            while lo < hi:
                mid = (lo + hi) // 2
                if piles[mid][-1] < card:
                    lo = mid + 1
                else:
                    hi = mid

            if lo == len(piles):
                piles.append([card])
            else:
                piles[lo].append(card)

            # Show pile tops as array (padded to n)
            tops = [p[-1] for p in piles]
            padded = tops + [0] * (n - len(tops))

            yield SortState(
                array=tuple(padded[:n]),
                comparing=(i, lo),
                last_swap=None,
                sorted_indices=frozenset(range(len(tops))),
                comparisons=i + 1,
                swaps=len(piles),
                description=(
                    f"Card[{i}]={card} → pile {lo}. "
                    f"Pile tops: {tops}"
                ),
            )

        # Phase 2: heap merge
        heap = [(pile[-1], j, len(pile) - 1) for j, pile in enumerate(piles)]
        heapq.heapify(heap)
        sorted_arr = []

        while heap:
            val, j, k = heapq.heappop(heap)
            sorted_arr.append(val)
            if k > 0:
                heapq.heappush(heap, (piles[j][k - 1], j, k - 1))

        return SortState(
            array=tuple(sorted_arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=n,
            swaps=len(piles),
            description=f"Sorted. #piles={len(piles)} = LIS length.",
        )
