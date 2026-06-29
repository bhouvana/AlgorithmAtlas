"""Job Scheduling (Deadline) greedy plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class JobSchedulingSimulation(AlgorithmPlugin):
    """
    Job Scheduling with Deadlines — O(n²) greedy.

    Jobs: each has (profit, deadline). Sort by profit desc.
    Greedily place each job in the latest free slot ≤ deadline.

    SortState encoding:
      array:        profits (sorted descending)
      sorted_indices: slots filled so far (job indices placed)
      comparisons:  total profit collected
      swaps:        number of jobs scheduled
      description:  "deadlines=d1,d2,..."
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="job-scheduling",
            name="Job Scheduling (Deadline)",
            category="greedy",
            visualization_type="ARRAY_BARS",
            description=(
                "Schedule jobs with deadlines and profits greedily "
                "to maximize total profit."
            ),
            intuition=(
                "Sort jobs by profit (highest first). "
                "Try to assign each job to the latest free slot before its deadline. "
                "If no slot is free, skip the job."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n)",
            tags=("greedy", "scheduling", "jobs", "deadline"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("array_size", 6), 10))
        max_deadline = n

        profits = [rng.randint(10, 50) for _ in range(n)]
        deadlines = [rng.randint(1, max_deadline) for _ in range(n)]

        # Sort by profit descending
        order = sorted(range(n), key=lambda i: profits[i], reverse=True)
        sorted_profits = [profits[i] for i in order]
        sorted_deadlines = [deadlines[i] for i in order]

        dl_str = ",".join(str(d) for d in sorted_deadlines)
        return SortState(
            array=tuple(sorted_profits),
            comparisons=0,
            swaps=0,
            sorted_indices=frozenset(),
            comparing=None,
            last_swap=None,
            description=f"deadlines={dl_str}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        profits = list(initial_state.array)
        dl_str = initial_state.description.split("deadlines=")[1]
        deadlines = [int(x) for x in dl_str.split(",")]
        n = len(profits)
        max_deadline = max(deadlines)

        # Slot array: -1 = free
        slots: List[int] = [-1] * (max_deadline + 1)  # 1-indexed
        scheduled: set = set()
        total_profit = 0
        jobs_done = 0

        for i in range(n):
            profit = profits[i]
            deadline = deadlines[i]

            # Find latest free slot ≤ deadline
            placed = False
            for t in range(min(deadline, max_deadline), 0, -1):
                if slots[t] == -1:
                    slots[t] = i
                    scheduled.add(i)
                    total_profit += profit
                    jobs_done += 1
                    placed = True
                    break

            placed_slot = slots.index(i) if placed else None
            yield SortState(
                array=tuple(profits),
                comparisons=total_profit,
                swaps=jobs_done,
                sorted_indices=frozenset(scheduled),
                comparing=(i, deadlines[i] - 1) if placed else None,
                last_swap=(i, placed_slot - 1) if placed and placed_slot else None,
                description=(
                    f"Job {i}: profit={profit}, deadline={deadline} → "
                    + (f"placed at slot {placed_slot} ✓" if placed else "no slot, skipped")
                ),
            )

        return SortState(
            array=tuple(profits),
            comparisons=total_profit,
            swaps=jobs_done,
            sorted_indices=frozenset(scheduled),
            comparing=None,
            last_swap=None,
            description=f"Done: {jobs_done} jobs scheduled, total profit = {total_profit}",
        )
