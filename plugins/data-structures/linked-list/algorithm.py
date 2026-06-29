"""
Linked List — Algorithm Atlas Plugin

Simulates a singly linked list of 10 integers.
Operations shown in sequence:
  1. Traverse  — highlight each node one at a time (left → right)
  2. Insert    — insert a new value at position 3 (0-indexed)
  3. Delete    — delete the node at position 5 after insertion
  4. Search    — highlight every node visited while searching for a target

Encoding (SortState):
  array       = current list values in order
  comparing   = (current_index, current_index)  ← single highlighted node
  last_swap   = (insert_pos, insert_pos) during insert, (del_pos, del_pos) during delete
  sorted_indices = indices that have been "visited/settled"
  auxiliary_indices = search-target index when found
  description = human-readable event
"""
from __future__ import annotations

import random
from typing import Generator, List, Optional, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class LinkedList(AlgorithmPlugin):
    """Singly linked list simulator: traverse, insert, delete, search."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="linked-list",
            name="Linked List",
            category="data-structures",
            visualization_type="ARRAY_BARS",
            description=(
                "A singly linked list where each node holds a value and a pointer to "
                "the next node. Demonstrates O(n) traversal, O(1) insertion/deletion "
                "given a pointer, and O(n) search."
            ),
            intuition=(
                "Think of a chain of train cars: you must walk from the engine to reach "
                "any car. Inserting or removing a car in the middle only requires "
                "re-linking neighbours — no shifting like in an array."
            ),
            complexity_time_best="O(1)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("data-structures", "linked-list", "pointer", "linear"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> SortState:
        n: int = max(5, min(int(params.inputs.get("n", 10)), 16))
        rng = random.Random(params.seed)
        values: List[int] = [rng.randint(1, 20) for _ in range(n)]
        return SortState(
            array=tuple(values),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Initial linked list of {n} nodes",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        lst: List[int] = list(initial_state.array)
        rng = random.Random(42)

        # ── Phase 1: Traverse ──────────────────────────────────────────────────
        visited: set[int] = set()
        for i in range(len(lst)):
            yield SortState(
                array=tuple(lst),
                comparing=(i, i),
                last_swap=None,
                sorted_indices=frozenset(visited),
                comparisons=i + 1,
                swaps=0,
                description=f"Traverse: visiting node[{i}] = {lst[i]}  →  next",
            )
            visited.add(i)

        yield SortState(
            array=tuple(lst),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(len(lst))),
            comparisons=len(lst),
            swaps=0,
            description="Traversal complete — all nodes visited",
        )

        # ── Phase 2: Insert at position 3 ─────────────────────────────────────
        insert_pos = min(3, len(lst))
        new_val = rng.randint(1, 20)

        # Walk to predecessor
        for i in range(insert_pos):
            yield SortState(
                array=tuple(lst),
                comparing=(i, i),
                last_swap=None,
                sorted_indices=frozenset(),
                comparisons=len(lst) + i + 1,
                swaps=0,
                description=f"Insert {new_val} @ pos {insert_pos}: walking to node[{i}]",
            )

        # Perform insert
        lst.insert(insert_pos, new_val)
        yield SortState(
            array=tuple(lst),
            comparing=None,
            last_swap=(insert_pos, insert_pos),
            sorted_indices=frozenset({insert_pos}),
            comparisons=len(lst) - 1 + insert_pos,
            swaps=1,
            description=(
                f"Inserted {new_val} at position {insert_pos} "
                f"— list now has {len(lst)} nodes"
            ),
        )

        # Show settled list briefly
        yield SortState(
            array=tuple(lst),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=len(lst) - 1 + insert_pos,
            swaps=1,
            description=f"List after insertion: {lst}",
        )

        # ── Phase 3: Delete at position 5 ─────────────────────────────────────
        del_pos = min(5, len(lst) - 1)

        # Walk to predecessor
        for i in range(del_pos):
            yield SortState(
                array=tuple(lst),
                comparing=(i, i),
                last_swap=None,
                sorted_indices=frozenset(),
                comparisons=len(lst) + del_pos + i,
                swaps=1,
                description=f"Delete @ pos {del_pos}: walking to node[{i}] (value={lst[i]})",
            )

        # Highlight target node before deletion
        yield SortState(
            array=tuple(lst),
            comparing=(del_pos, del_pos),
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=len(lst) + del_pos * 2,
            swaps=1,
            description=f"Found node[{del_pos}] = {lst[del_pos]} — will unlink and remove",
        )

        removed_val = lst[del_pos]
        lst.pop(del_pos)

        yield SortState(
            array=tuple(lst),
            comparing=None,
            last_swap=(del_pos - 1, del_pos - 1) if del_pos > 0 else None,
            sorted_indices=frozenset(),
            comparisons=len(lst) + del_pos * 2 + 1,
            swaps=2,
            description=(
                f"Deleted {removed_val} from position {del_pos} "
                f"— list now has {len(lst)} nodes"
            ),
        )

        yield SortState(
            array=tuple(lst),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=len(lst) + del_pos * 2 + 1,
            swaps=2,
            description=f"List after deletion: {lst}",
        )

        # ── Phase 4: Search ───────────────────────────────────────────────────
        target = lst[len(lst) // 2] if lst else 1
        search_steps = 0
        found_idx: Optional[int] = None

        for i, val in enumerate(lst):
            search_steps += 1
            yield SortState(
                array=tuple(lst),
                comparing=(i, i),
                last_swap=None,
                sorted_indices=frozenset(range(i)),
                comparisons=len(lst) * 3 + search_steps,
                swaps=2,
                description=f"Search {target}: checking node[{i}] = {val}",
            )
            if val == target:
                found_idx = i
                break

        final_desc = (
            f"Found {target} at node[{found_idx}] after {search_steps} step(s)"
            if found_idx is not None
            else f"{target} not found after {search_steps} step(s)"
        )

        final_highlight = frozenset({found_idx}) if found_idx is not None else frozenset()

        yield SortState(
            array=tuple(lst),
            comparing=(found_idx, found_idx) if found_idx is not None else None,
            last_swap=None,
            sorted_indices=final_highlight,
            comparisons=len(lst) * 3 + search_steps,
            swaps=2,
            description=final_desc,
        )

        return SortState(
            array=tuple(lst),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(len(lst))),
            comparisons=len(lst) * 3 + search_steps,
            swaps=2,
            description="Linked list simulation complete",
        )
