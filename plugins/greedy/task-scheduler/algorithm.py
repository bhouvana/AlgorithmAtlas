"""Task Scheduler (EDF) plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


def _make_tasks(rng: random.Random, n: int):
    """Generate tasks with (processing_time=1, deadline) pairs."""
    deadlines = sorted(rng.sample(range(1, 2 * n + 1), n))
    return deadlines


def _max_lateness(deadlines: list) -> int:
    """Compute max lateness under EDF order (sorted by deadline)."""
    time = 0
    max_late = 0
    for d in sorted(deadlines):
        time += 1
        lateness = time - d
        max_late = max(max_late, lateness)
    return max_late


class TaskSchedulerSimulation(AlgorithmPlugin):
    """Earliest Deadline First (EDF) Task Scheduler."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="task-scheduler",
            name="Task Scheduler (Earliest Deadline First)",
            category="greedy",
            visualization_type="ARRAY_BARS",
            description="Schedule unit-time tasks to minimize maximum lateness by sorting on deadline.",
            intuition=(
                "EDF: sort tasks ascending by deadline. If any task is going to be late, "
                "swapping with an earlier-deadline task can only reduce or maintain max lateness."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n)",
            tags=("greedy", "scheduling", "deadline", "earliest-deadline-first"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 6))
        deadlines = _make_tasks(rng, n)
        max_late = _max_lateness(deadlines)
        return SortState(
            array=tuple(deadlines),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=max_late,
            description=f"EDF schedule deadlines={deadlines} max_lateness={max_late}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        deadlines = list(initial_state.array)
        n = len(deadlines)

        # Sort by deadline (insertion sort for visualization)
        arr = deadlines[:]
        comparisons = 0
        swaps = 0
        sorted_set: set[int] = set()

        for i in range(1, n):
            key = arr[i]
            j = i - 1
            while j >= 0 and arr[j] > key:
                comparisons += 1
                arr[j + 1] = arr[j]
                swaps += 1
                j -= 1
                yield SortState(
                    array=tuple(arr),
                    comparing=(j + 1, i),
                    last_swap=(j + 1, j + 2),
                    sorted_indices=frozenset(sorted_set),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"Move task (deadline={key}) left",
                )
            arr[j + 1] = key
            sorted_set.add(i)

        # Show schedule execution
        time = 0
        max_late = 0
        for i, d in enumerate(arr):
            time += 1
            lateness = max(0, time - d)
            max_late = max(max_late, lateness)
            yield SortState(
                array=tuple(arr),
                comparing=(i, i),
                last_swap=None,
                sorted_indices=frozenset(range(i + 1)),
                comparisons=comparisons,
                swaps=max_late,
                description=f"Task {i+1}: deadline={d} finish={time} lateness={lateness}",
            )

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=comparisons,
            swaps=max_late,
            description=f"EDF: max lateness = {max_late}",
        )
