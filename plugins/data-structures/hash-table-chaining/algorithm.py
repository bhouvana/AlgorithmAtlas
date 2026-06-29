"""
Hash Table with Separate Chaining — Algorithm Atlas Plugin

Array visualization: bucket index → chain length (bar height).
Inserts 12 keys into a table of M=7 buckets; shows collisions resolved
via chaining. comparing=(bucket, bucket) highlights the target bucket.
"""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import AlgorithmMetadata, AlgorithmPlugin, SimulationParams, SortState


class HashTableChaining(AlgorithmPlugin):

    M = 7  # number of buckets

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="hash-table-chaining",
            name="Hash Table (Separate Chaining)",
            category="data-structures",
            visualization_type="ARRAY_BARS",
            description=(
                "Hash table that resolves collisions via separate chaining. "
                "Each bucket holds a linked list of entries that hashed to that slot. "
                "Insert: O(1) amortised; Lookup: O(1) average, O(n) worst case."
            ),
            complexity_time_best="O(1)",
            complexity_time_average="O(1)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("data-structures", "hash-table", "chaining", "collision-resolution"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> SortState:
        n = max(5, min(int(params.inputs.get("n", 12)), 20))
        rng = random.Random(params.seed)
        keys = [rng.randint(1, 99) for _ in range(n)]
        return SortState(
            array=tuple([0] * self.M),   # chain lengths per bucket
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Empty hash table: {self.M} buckets, 0 chains. "
                        f"About to insert {n} keys: {keys}",
        )

    def _h(self, k: int) -> int:
        return k % self.M

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        rng = random.Random(42)
        n = 12
        keys: List[int] = [rng.randint(1, 99) for _ in range(n)]
        buckets: List[int] = [0] * self.M  # chain lengths
        chains: List[List[int]] = [[] for _ in range(self.M)]
        comparisons = 0
        swaps = 0

        for key in keys:
            b = self._h(key)
            comparisons += 1

            # Highlight target bucket
            yield SortState(
                array=tuple(buckets),
                comparing=(b, b),
                last_swap=None,
                sorted_indices=frozenset(i for i in range(self.M) if chains[i]),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Insert {key}: hash({key}) = {key} % {self.M} = {b}  →  bucket[{b}]",
            )

            # Check for collision
            if chains[b]:
                comparisons += len(chains[b])
                yield SortState(
                    array=tuple(buckets),
                    comparing=(b, b),
                    last_swap=(b, b),
                    sorted_indices=frozenset(i for i in range(self.M) if chains[i]),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=(
                        f"Collision at bucket[{b}] (chain length {len(chains[b])})! "
                        f"Appending {key} to chain: {chains[b]} → {chains[b] + [key]}"
                    ),
                )
            else:
                yield SortState(
                    array=tuple(buckets),
                    comparing=(b, b),
                    last_swap=None,
                    sorted_indices=frozenset(i for i in range(self.M) if chains[i]),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"bucket[{b}] is empty → insert {key} as first element.",
                )

            chains[b].append(key)
            buckets[b] += 1
            swaps += 1

            yield SortState(
                array=tuple(buckets),
                comparing=None,
                last_swap=(b, b),
                sorted_indices=frozenset(i for i in range(self.M) if chains[i]),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Inserted {key} → bucket[{b}] chain: {chains[b]}. "
                            f"Load factor: {sum(buckets)}/{self.M} = {sum(buckets)/self.M:.2f}",
            )

        # Final lookup demonstration
        target = keys[len(keys) // 2]
        b = self._h(target)
        comparisons += 1
        for i, v in enumerate(chains[b]):
            comparisons += 1
            yield SortState(
                array=tuple(buckets),
                comparing=(b, b),
                last_swap=None,
                sorted_indices=frozenset(idx for idx in range(self.M) if buckets[idx] == max(buckets)),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Lookup {target}: bucket[{b}], checking chain[{i}]={v}",
            )
            if v == target:
                break

        final = SortState(
            array=tuple(buckets),
            comparing=(b, b),
            last_swap=None,
            sorted_indices=frozenset(range(self.M)),
            comparisons=comparisons,
            swaps=swaps,
            description=(
                f"Found {target} in bucket[{b}]. Final bucket chain lengths: "
                + ", ".join(f"[{i}]={buckets[i]}" for i in range(self.M))
            ),
        )
        yield final
        return final
