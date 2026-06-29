"""Gas Station greedy plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


def _make_instance(rng: random.Random, n: int):
    """Generate a solvable gas station instance: total_gas >= total_cost."""
    cost = [rng.randint(1, 5) for _ in range(n)]
    # Gas slightly exceeds cost on average to guarantee a solution
    gas = [c + rng.randint(0, 2) for c in cost]
    # Ensure total gas > total cost
    gas[rng.randint(0, n - 1)] += max(0, sum(cost) - sum(gas) + 1)
    return gas, cost


class GasStationSimulation(AlgorithmPlugin):
    """
    Gas Station — O(n) greedy.

    SortState encoding:
      array:          gas[i] - cost[i] (net gain at each station)
      comparisons:    current running tank
      swaps:          total net (gas - cost) across all stations
      sorted_indices: stations that have been processed
      description:    "gas=g1,g2,...|cost=c1,c2,..."
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="gas-station",
            name="Gas Station",
            category="greedy",
            visualization_type="ARRAY_BARS",
            description=(
                "Find the starting gas station index from which a car can "
                "complete a circular route without running out of fuel."
            ),
            intuition=(
                "If total gas ≥ total cost, a solution always exists. "
                "Track running tank; when it goes negative, the start candidate "
                "must be after the current station."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(1)",
            tags=("greedy", "gas-station", "circular", "array"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("array_size", 6), 10))
        gas, cost = _make_instance(rng, n)
        net = [g - c for g, c in zip(gas, cost)]
        return SortState(
            array=tuple(net),
            comparisons=0,
            swaps=sum(net),
            sorted_indices=frozenset(),
            comparing=None,
            last_swap=None,
            description=f"gas={','.join(map(str,gas))}|cost={','.join(map(str,cost))}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        net = list(initial_state.array)
        n = len(net)
        total_net = sum(net)

        if total_net < 0:
            return SortState(
                array=tuple(net),
                comparisons=0,
                swaps=total_net,
                sorted_indices=frozenset(),
                comparing=None,
                last_swap=None,
                description="No solution: total gas < total cost",
            )

        start = 0
        tank = 0
        processed: set = set()

        for i in range(n):
            tank += net[i]
            processed.add(i)
            if tank < 0:
                # Can't start from current `start` through `i`; try i+1
                start = i + 1
                tank = 0
                yield SortState(
                    array=tuple(net),
                    comparisons=tank,
                    swaps=start,
                    sorted_indices=frozenset(processed),
                    comparing=(i, i),
                    last_swap=None,
                    description=f"Tank depleted at station {i}: try start={start}",
                )
            else:
                yield SortState(
                    array=tuple(net),
                    comparisons=tank,
                    swaps=start,
                    sorted_indices=frozenset(processed),
                    comparing=(i, i),
                    last_swap=None,
                    description=f"Station {i}: net={net[i]:+d}, tank={tank}, start candidate={start}",
                )

        return SortState(
            array=tuple(net),
            comparisons=tank,
            swaps=start,
            sorted_indices=frozenset(range(n)),
            comparing=None,
            last_swap=None,
            description=f"Start station = {start}",
        )
