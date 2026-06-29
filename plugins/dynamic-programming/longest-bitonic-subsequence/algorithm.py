"""Longest Bitonic Subsequence plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class LongestBitonicSubsequenceSimulation(AlgorithmPlugin):
    """LBS = max LIS[i] + LDS[i] - 1 over all pivot positions i."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="longest-bitonic-subsequence",
            name="Longest Bitonic Subsequence",
            category="dynamic-programming",
            visualization_type="ARRAY_BARS",
            description="LBS: longest subseq increasing then decreasing. Uses LIS + LDS.",
            intuition=(
                "Phase 1: LIS[i] = length of longest increasing subsequence ending at i. "
                "Phase 2: LDS[i] = longest decreasing subsequence starting at i. "
                "Combine: LBS = max(LIS[i] + LDS[i] - 1)."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n)",
            tags=("dynamic-programming", "bitonic", "subsequence", "lis", "lds"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        import random
        n = int(params.inputs.get("size", 10))
        rng = random.Random(params.seed)
        arr = tuple(rng.randint(1, 99) for _ in range(n))
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"LBS n={n} seed={params.seed}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        n = int(re.search(r"n=(\d+)", initial_state.description).group(1))
        arr = list(initial_state.array)

        # Phase 1: compute LIS[i]
        lis = [1] * n
        for i in range(1, n):
            for j in range(i):
                if arr[j] < arr[i]:
                    lis[i] = max(lis[i], lis[j] + 1)
            # Yield current LIS state
            yield SortState(
                array=tuple(lis),
                comparing=(i, i),
                last_swap=None,
                sorted_indices=frozenset(range(i + 1)),
                comparisons=i,
                swaps=max(lis[:i+1]),
                description=f"LIS[{i}]={lis[i]} (phase 1: increasing)",
            )

        # Phase 2: compute LDS[i]
        lds = [1] * n
        for i in range(n - 2, -1, -1):
            for j in range(i + 1, n):
                if arr[j] < arr[i]:
                    lds[i] = max(lds[i], lds[j] + 1)
            # Yield current LDS state
            yield SortState(
                array=tuple(lds),
                comparing=(i, i),
                last_swap=None,
                sorted_indices=frozenset(range(i, n)),
                comparisons=n + (n - 1 - i),
                swaps=max(lds[i:]),
                description=f"LDS[{i}]={lds[i]} (phase 2: decreasing)",
            )

        # Phase 3: compute LBS[i] = LIS[i] + LDS[i] - 1
        lbs = [lis[i] + lds[i] - 1 for i in range(n)]
        best = max(lbs)
        best_i = lbs.index(best)

        # Yield final combined view
        yield SortState(
            array=tuple(lbs),
            comparing=(best_i, best_i),
            last_swap=(best_i, best_i),
            sorted_indices=frozenset(range(n)),
            comparisons=2 * n,
            swaps=best,
            description=f"LBS[{best_i}]=LIS+LDS-1={lis[best_i]}+{lds[best_i]}-1={best}",
        )

        return SortState(
            array=tuple(lbs),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset([best_i]),
            comparisons=2 * n,
            swaps=best,
            description=f"Longest bitonic subsequence length = {best} (pivot at idx {best_i})",
        )
