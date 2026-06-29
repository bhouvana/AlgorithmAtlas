"""Bloom Filter plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_M = 32    # bit array size
_K = 3     # number of hash functions
_ITEMS = ["cat", "dog", "fish", "bird", "frog", "wolf", "bear", "deer"]
# Query items: some inserted, some not
_QUERIES = ["cat", "wolf", "lion", "dog", "snake"]


def _hash(item: str, seed: int) -> int:
    h = seed * 2654435761
    for c in item:
        h = (h * 31 + ord(c)) & 0xFFFFFFFF
    return h % _M


def _insert_bits(item: str) -> list:
    return [_hash(item, k) for k in range(_K)]


class BloomFilterSimulation(AlgorithmPlugin):
    """Bloom filter insertion and membership query."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="bloom-filter",
            name="Bloom Filter",
            category="searching",
            visualization_type="ARRAY_BARS",
            description=f"Bloom filter with {_M}-bit array, {_K} hash functions.",
            intuition=(
                "Insert: hash item k times, set those bit positions. "
                "Query: hash k times, check if all positions are 1. "
                "False positives possible; false negatives impossible."
            ),
            complexity_time_best="O(k)",
            complexity_time_average="O(k)",
            complexity_time_worst="O(k)",
            complexity_space="O(m)",
            tags=("searching", "bloom-filter", "probabilistic", "hashing", "data-structure"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        n = (params.seed % 5) + 3  # insert 3-7 items
        items_str = ",".join(_ITEMS[:n])
        return SortState(
            array=tuple([1] * _M),  # all bits = 0 → bar height 1
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"BloomFilter m={_M} k={_K} items={items_str}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        items_str = re.search(r"items=(.+)$", initial_state.description).group(1)
        items = items_str.split(",")

        bits = [0] * _M

        for idx, item in enumerate(items):
            positions = _insert_bits(item)
            for pos in positions:
                bits[pos] = 1

            set_bits = frozenset(i for i, b in enumerate(bits) if b)
            arr = tuple(99 if b else 1 for b in bits)

            yield SortState(
                array=arr,
                comparing=(min(positions), max(positions)),
                last_swap=None,
                sorted_indices=set_bits,
                comparisons=idx + 1,
                swaps=sum(bits),
                description=(
                    f"Inserted '{item}': bits {positions} set. "
                    f"{sum(bits)}/{_M} bits used."
                ),
            )

        # Now show queries
        for query in _QUERIES:
            positions = _insert_bits(query)
            hit = all(bits[p] for p in positions)
            result = "MAYBE" if hit else "ABSENT"
            arr = tuple(99 if b else 1 for b in bits)

            yield SortState(
                array=arr,
                comparing=(min(positions), max(positions)),
                last_swap=(min(positions), max(positions)) if hit else None,
                sorted_indices=frozenset(p for p in positions if bits[p]),
                comparisons=len(items) + _QUERIES.index(query) + 1,
                swaps=sum(bits),
                description=(
                    f"Query '{query}': check bits {positions} → {result} "
                    f"({'in set' if query in items else 'NOT in set'})"
                ),
            )

        arr = tuple(99 if b else 1 for b in bits)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(i for i, b in enumerate(bits) if b),
            comparisons=len(items) + len(_QUERIES),
            swaps=sum(bits),
            description=(
                f"Done: {sum(bits)}/{_M} bits set, "
                f"~{(1-sum(bits)/_M)**(_K*_M/sum(bits) if sum(bits) else 1):.3f} false positive rate"
            ),
        )
