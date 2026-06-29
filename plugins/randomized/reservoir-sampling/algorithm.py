"""Reservoir Sampling plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class ReservoirSamplingSimulation(AlgorithmPlugin):
    """Reservoir Sampling (Algorithm R) for uniform stream sampling."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="reservoir-sampling",
            name="Reservoir Sampling",
            category="randomized",
            visualization_type="ARRAY_BARS",
            description="Sample k items uniformly from a stream of n items in O(n) time, O(k) space.",
            intuition=(
                "Accept the first k items unconditionally. "
                "For each subsequent item at position i, replace a uniform random "
                "reservoir slot with probability k/i. Result is a uniform sample."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(k)",
            tags=("randomized", "reservoir-sampling", "streaming", "probability"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("stream_size", 20))
        k = int(params.inputs.get("reservoir_size", 5))
        stream = [rng.randint(1, 99) for _ in range(n)]

        return SortState(
            array=tuple(stream),
            comparing=(0, k - 1),
            last_swap=None,
            sorted_indices=frozenset(range(k)),
            comparisons=0,
            swaps=k,
            description=f"Reservoir k={k} n={n}: stream={stream}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        stream = list(initial_state.array)
        n = len(stream)
        k = initial_state.swaps
        rng = random.Random(hash(tuple(stream)) % (2**31))

        reservoir = list(stream[:k])
        reservoir_set = set(range(k))

        yield SortState(
            array=tuple(stream),
            comparing=(0, k - 1),
            last_swap=None,
            sorted_indices=frozenset(range(k)),
            comparisons=k,
            swaps=k,
            description=f"Filled reservoir with first {k} items: {reservoir}",
        )

        for i in range(k, n):
            j = rng.randint(0, i)
            replaced = j < k

            if replaced:
                old_val = reservoir[j]
                reservoir[j] = stream[i]
                reservoir_set = set(range(k))  # indices 0..k-1 represent reservoir positions

            yield SortState(
                array=tuple(stream),
                comparing=(i, i),
                last_swap=(j, j) if replaced else None,
                sorted_indices=frozenset(range(k)),
                comparisons=i + 1,
                swaps=k,
                description=(
                    f"Item {i} (val={stream[i]}): j={j} "
                    + (f"→ KEEP, replace slot {j} (was {old_val})" if replaced
                       else f"→ DISCARD (j={j} ≥ k={k})")
                ),
            )

        return SortState(
            array=tuple(stream),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(k)),
            comparisons=n,
            swaps=k,
            description=f"Sample complete: reservoir={reservoir}",
        )
