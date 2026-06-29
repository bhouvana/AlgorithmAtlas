"""Skip List plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_MAX_LEVEL = 4
_P = 0.5  # probability of promotion


def _random_level(rng):
    level = 1
    while rng.random() < _P and level < _MAX_LEVEL:
        level += 1
    return level


class SkipListSimulation(AlgorithmPlugin):
    """Skip list insertion and search visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="skip-list",
            name="Skip List (Probabilistic Search)",
            category="searching",
            visualization_type="ARRAY_BARS",
            description=f"Build a {_MAX_LEVEL}-level skip list and search for median element.",
            intuition=(
                "Insert each element into a randomly tall tower. "
                "Level 0 = all elements sorted. Higher levels = express lanes. "
                "Search: start top, move right if next < target, else drop down."
            ),
            complexity_time_best="O(log n)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n log n)",
            tags=("searching", "skip-list", "probabilistic", "linked-list"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        import random
        n = int(params.inputs.get("size", 10))
        rng = random.Random(params.seed)
        values = sorted(rng.sample(range(5, 99), n))
        vals_str = ",".join(map(str, values))
        return SortState(
            array=tuple(values),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"SkipList n={n} seed={params.seed} values={vals_str}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        import random
        desc = initial_state.description
        n = int(re.search(r"n=(\d+)", desc).group(1))
        seed = int(re.search(r"seed=(\d+)", desc).group(1))
        values_str = re.search(r"values=([0-9,]+)", desc).group(1)
        values = list(map(int, values_str.split(",")))

        rng = random.Random(seed * 13 + 7)
        # Assign each element a level
        levels = [_random_level(rng) for _ in range(n)]
        max_level_used = max(levels)

        # Insert phase: show each insertion
        inserted = set()
        for i, (v, lv) in enumerate(zip(values, levels)):
            inserted.add(i)
            # Bar height = element value; color shows level
            arr = list(initial_state.array)
            yield SortState(
                array=tuple(arr),
                comparing=(i, i),
                last_swap=(i, i),
                sorted_indices=frozenset(inserted),
                comparisons=i + 1,
                swaps=lv,
                description=(
                    f"Insert {v} at level {lv}/{max_level_used}"
                ),
            )

        # Search phase: search for median
        target = values[n // 2]
        search_path = []
        # Simulate top-down search
        level = max_level_used - 1
        current_idx = -1  # before first element

        while level >= 0:
            # Move right on this level while next element < target
            next_idx = current_idx + 1
            while next_idx < n and values[next_idx] < target:
                # Only advance if current element's level >= current search level
                if levels[next_idx] >= level + 1:
                    current_idx = next_idx
                    search_path.append(current_idx)
                next_idx += 1
            level -= 1

        # Found at current_idx + 1 or not found
        found_idx = current_idx + 1 if current_idx + 1 < n and values[current_idx + 1] == target else -1

        for step_idx, idx in enumerate(search_path):
            arr = list(initial_state.array)
            yield SortState(
                array=tuple(arr),
                comparing=(idx, idx),
                last_swap=None,
                sorted_indices=frozenset([idx]),
                comparisons=n + step_idx + 1,
                swaps=values[idx],
                description=(
                    f"Search {target}: at {values[idx]}, continue right"
                ),
            )

        arr = list(initial_state.array)
        if found_idx >= 0:
            yield SortState(
                array=tuple(arr),
                comparing=(found_idx, found_idx),
                last_swap=(found_idx, found_idx),
                sorted_indices=frozenset([found_idx]),
                comparisons=n + len(search_path) + 1,
                swaps=target,
                description=f"Found {target} at index {found_idx}!",
            )

        return SortState(
            array=tuple(initial_state.array),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=n + len(search_path) + 1,
            swaps=target,
            description=(
                f"Done: {n} elements in {max_level_used}-level skip list. "
                f"Searched for {target}: {'found' if found_idx >= 0 else 'not found'}"
            ),
        )
