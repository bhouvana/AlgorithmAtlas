"""Meeting Rooms II plugin for Algorithm Atlas."""
from __future__ import annotations

import heapq
import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


def _make_meetings(rng: random.Random, n: int) -> List[Tuple[int, int]]:
    starts = sorted(rng.randint(0, 20) for _ in range(n))
    meetings = []
    for s in starts:
        dur = rng.randint(1, 6)
        meetings.append((s, s + dur))
    return meetings


def _brute_force_rooms(meetings: List[Tuple[int, int]]) -> int:
    """Count max overlaps at any point."""
    events = []
    for s, e in meetings:
        events.append((s, 1))
        events.append((e, -1))
    events.sort()
    cur = max_rooms = 0
    for _, delta in events:
        cur += delta
        max_rooms = max(max_rooms, cur)
    return max_rooms


class MeetingRoomsSimulation(AlgorithmPlugin):
    """
    Meeting Rooms II — min rooms for n meetings.

    SortState encoding:
      array:          end times of currently allocated rooms (heap representation)
      comparisons:    current number of rooms in use
      swaps:          max rooms needed so far
      sorted_indices: indices of meetings processed so far
      description:    start/end times encoded as "starts=s1,s2,...|ends=e1,e2,..."
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="meeting-rooms",
            name="Meeting Rooms (Min Rooms)",
            category="greedy",
            visualization_type="ARRAY_BARS",
            description=(
                "Find the minimum number of conference rooms to hold all meetings "
                "without conflicts."
            ),
            intuition=(
                "Sort meetings by start time. Use a min-heap of room end times. "
                "If the earliest-finishing room is free before the next meeting, "
                "reuse it. Otherwise allocate a new room."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n)",
            tags=("greedy", "meeting-rooms", "intervals", "heap"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("array_size", 6), 10))
        meetings = _make_meetings(rng, n)
        meetings.sort()
        starts = [s for s, e in meetings]
        ends = [e for s, e in meetings]
        return SortState(
            array=tuple(starts),  # start times (sorted)
            comparisons=0,
            swaps=0,
            sorted_indices=frozenset(),
            comparing=None,
            last_swap=None,
            description=f"starts={','.join(map(str,starts))}|ends={','.join(map(str,ends))}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        desc = initial_state.description
        starts_str, ends_str = desc.split("|")
        starts = [int(x) for x in starts_str.split("=")[1].split(",")]
        ends = [int(x) for x in ends_str.split("=")[1].split(",")]
        n = len(starts)
        meetings = sorted(zip(starts, ends))

        heap: List[int] = []  # min-heap of end times
        processed: set = set()
        max_rooms = 0

        for i, (s, e) in enumerate(meetings):
            if heap and heap[0] <= s:
                heapq.heapreplace(heap, e)
                rooms = len(heap)
            else:
                heapq.heappush(heap, e)
                rooms = len(heap)

            max_rooms = max(max_rooms, rooms)
            processed.add(i)

            yield SortState(
                array=tuple(sorted(heap)),  # show current room end times
                comparisons=rooms,
                swaps=max_rooms,
                sorted_indices=frozenset(range(len(heap))),
                comparing=(i, i),
                last_swap=None,
                description=f"Meeting [{s},{e}]: {rooms} rooms in use, max={max_rooms}",
            )

        return SortState(
            array=tuple(sorted(heap)),
            comparisons=len(heap),
            swaps=max_rooms,
            sorted_indices=frozenset(range(len(heap))),
            comparing=None,
            last_swap=None,
            description=f"Done: {max_rooms} rooms needed",
        )
