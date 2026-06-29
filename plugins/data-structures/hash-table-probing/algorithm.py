"""
Hash Table with Linear Probing — Algorithm Atlas Plugin

Array visualization: slot index → stored value (0 = empty).
Inserts 8 keys into a table of M=11 slots using linear probing.
comparing=(slot, slot) highlights the slot being examined.
last_swap=(slot, slot) marks where a key was just placed.
sorted_indices = occupied slots.
"""
from __future__ import annotations

import random
from typing import Generator, List, Optional

from algorithm_atlas_sdk import AlgorithmMetadata, AlgorithmPlugin, SimulationParams, SortState


class HashTableLinearProbing(AlgorithmPlugin):

    M = 11  # prime table size

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="hash-table-probing",
            name="Hash Table (Linear Probing)",
            category="data-structures",
            visualization_type="ARRAY_BARS",
            description=(
                "Open-addressing hash table with linear probing. "
                "On collision, scan slots (i+1) % M until empty. "
                "Shows primary clustering effect. "
                "Lookup: O(1) amortised, O(n) worst case."
            ),
            complexity_time_best="O(1)",
            complexity_time_average="O(1)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("data-structures", "hash-table", "linear-probing", "open-addressing"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> SortState:
        n = max(4, min(int(params.inputs.get("n", 8)), 10))
        rng = random.Random(params.seed)
        keys = [rng.randint(1, 50) for _ in range(n)]
        return SortState(
            array=tuple([0] * self.M),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Empty table, {self.M} slots. Linear probing: h(k)=k%{self.M}. "
                        f"Keys to insert: {keys}",
        )

    def _h(self, k: int) -> int:
        return k % self.M

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        rng = random.Random(42)
        n = 8
        keys: List[int] = [rng.randint(1, 50) for _ in range(n)]
        table: List[int] = [0] * self.M
        comparisons = 0
        swaps = 0
        occupied: set[int] = set()

        for key in keys:
            slot = self._h(key)
            comparisons += 1

            # Show initial hash position
            yield SortState(
                array=tuple(table),
                comparing=(slot, slot),
                last_swap=None,
                sorted_indices=frozenset(occupied),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Insert {key}: h({key}) = {key} % {self.M} = {slot} → slot[{slot}]={table[slot] or 'empty'}",
            )

            probes = 0
            while table[slot] != 0:
                comparisons += 1
                probes += 1
                yield SortState(
                    array=tuple(table),
                    comparing=(slot, slot),
                    last_swap=None,
                    sorted_indices=frozenset(occupied),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"slot[{slot}]={table[slot]} occupied! Linear probe → slot[{(slot+1)%self.M}]",
                )
                slot = (slot + 1) % self.M

            table[slot] = key
            occupied.add(slot)
            swaps += 1

            yield SortState(
                array=tuple(table),
                comparing=None,
                last_swap=(slot, slot),
                sorted_indices=frozenset(occupied),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Placed {key} at slot[{slot}] after {probes} probe(s). "
                            f"Load factor: {len(occupied)}/{self.M} = {len(occupied)/self.M:.2f}",
            )

        # Search demo: find a key that had probing
        target = keys[-1]
        slot = self._h(target)
        comparisons += 1
        probe_slots = []
        while table[slot] != target and table[slot] != 0:
            probe_slots.append(slot)
            comparisons += 1
            yield SortState(
                array=tuple(table),
                comparing=(slot, slot),
                last_swap=None,
                sorted_indices=frozenset(occupied),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Search {target}: slot[{slot}]={table[slot]} ≠ {target}, probing next...",
            )
            slot = (slot + 1) % self.M

        comparisons += 1
        final = SortState(
            array=tuple(table),
            comparing=(slot, slot),
            last_swap=(slot, slot),
            sorted_indices=frozenset(occupied),
            comparisons=comparisons,
            swaps=swaps,
            description=(
                f"Found {target} at slot[{slot}]! "
                f"{len(probe_slots)} extra probe(s) needed due to clustering. "
                f"Table: {[f'{v}' if v else '_' for v in table]}"
            ),
        )
        yield final
        return final
