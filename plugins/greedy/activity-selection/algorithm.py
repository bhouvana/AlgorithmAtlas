"""Activity Selection greedy plugin for Algorithm Atlas.

Array encodes finish times of activities (sorted).
Bar heights = finish time, sorted_indices = selected activities.
comparisons tracks how many activities were considered.
"""
from __future__ import annotations

import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class ActivitySelectionSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="activity-selection",
            name="Activity Selection",
            category="greedy",
            visualization_type="ARRAY_BARS",
            description="Select the maximum number of non-overlapping activities sorted by finish time.",
            intuition="Sort activities by finish time. Greedily pick each activity if its start ≥ finish of last selected. This locally optimal choice is globally optimal.",
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n)",
            tags=("greedy", "activity-selection", "interval-scheduling", "optimization"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n: int = max(5, min(params.inputs.get("array_size", 8), 15))

        # Generate non-trivial activities with random start/finish times
        activities: List[Tuple[int, int]] = []
        t = 0
        for _ in range(n):
            start = t + rng.randint(0, 3)
            duration = rng.randint(2, 6)
            activities.append((start, start + duration))
            t = start + rng.randint(1, 3)

        # Sort by finish time
        activities.sort(key=lambda x: x[1])
        finish_times = [f for _, f in activities]

        # Store start times packed in description as comma-separated
        starts_str = ",".join(str(s) for s, _ in activities)
        return SortState(
            array=tuple(finish_times),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"starts={starts_str}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        finish_times = list(initial_state.array)
        n = len(finish_times)
        starts_str = initial_state.description.split("starts=")[1]
        start_times = [int(x) for x in starts_str.split(",")]
        activities = list(zip(start_times, finish_times))

        selected: List[int] = [0]  # always select first activity
        last_finish = finish_times[0]
        comparisons = 0

        yield SortState(
            array=tuple(finish_times),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(selected),
            comparisons=comparisons,
            swaps=len(selected),
            description=f"Select first activity [s={activities[0][0]}, f={activities[0][1]}]",
        )

        for i in range(1, n):
            comparisons += 1
            s, f = activities[i]
            yield SortState(
                array=tuple(finish_times),
                comparing=(i, i),
                last_swap=None,
                sorted_indices=frozenset(selected),
                comparisons=comparisons,
                swaps=len(selected),
                description=f"Check activity {i}: [s={s}, f={f}] vs last_finish={last_finish}",
            )
            if s >= last_finish:
                selected.append(i)
                last_finish = f
                yield SortState(
                    array=tuple(finish_times),
                    comparing=None,
                    last_swap=(i, i),
                    sorted_indices=frozenset(selected),
                    comparisons=comparisons,
                    swaps=len(selected),
                    description=f"Selected activity {i}: [s={s}, f={f}] — {len(selected)} selected so far",
                )
            else:
                yield SortState(
                    array=tuple(finish_times),
                    comparing=None,
                    last_swap=None,
                    sorted_indices=frozenset(selected),
                    comparisons=comparisons,
                    swaps=len(selected),
                    description=f"Skip activity {i}: [s={s}, f={f}] overlaps (s < {last_finish})",
                )

        return SortState(
            array=tuple(finish_times),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(selected),
            comparisons=comparisons,
            swaps=len(selected),
            description=f"Done — selected {len(selected)} of {n} activities",
        )
