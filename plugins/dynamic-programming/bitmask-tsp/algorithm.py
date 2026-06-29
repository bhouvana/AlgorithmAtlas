"""Bitmask DP — Traveling Salesman Problem plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

# Fixed 5-city TSP instance
_N = 5
_DIST = [
    [0,  10, 15, 20, 25],
    [10,  0, 35, 25, 20],
    [15, 35,  0, 30, 10],
    [20, 25, 30,  0, 15],
    [25, 20, 10, 15,  0],
]
_INF = float('inf')


class BitmaskTSPSimulation(AlgorithmPlugin):
    """Exact TSP via bitmask DP on a 5-city graph."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="bitmask-tsp",
            name="Bitmask DP — Traveling Salesman",
            category="dynamic-programming",
            visualization_type="ARRAY_BARS",
            description=f"Solve TSP exactly for {_N} cities using dp[mask][i] bitmask DP.",
            intuition=(
                "dp[mask][i] = min cost to visit all cities in mask ending at i. "
                "Extend each state by adding an unvisited city. "
                "Final answer: min(dp[all_visited][i] + dist[i][0]) for each i."
            ),
            complexity_time_best="O(2^n · n²)",
            complexity_time_average="O(2^n · n²)",
            complexity_time_worst="O(2^n · n²)",
            complexity_space="O(2^n · n)",
            tags=("dynamic-programming", "tsp", "bitmask", "combinatorial", "exact"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        # Show distance matrix as flat array (first row scaled)
        flat = [_DIST[0][j] for j in range(_N)]
        mx = max(flat[1:])
        scaled = tuple(max(1, min(99, int(v * 99 // mx))) if v > 0 else 1 for v in flat)
        return SortState(
            array=scaled,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"TSP n={_N}: dp bitmask initialization",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        size = 1 << _N
        dp = [[_INF] * _N for _ in range(size)]
        parent = [[-1] * _N for _ in range(size)]
        dp[1][0] = 0  # start at city 0, only city 0 visited

        states_to_yield = []

        # Fill DP table layer by layer (by popcount of mask)
        for mask in range(1, size):
            popcount = bin(mask).count('1')
            for i in range(_N):
                if not (mask >> i & 1):
                    continue
                if dp[mask][i] == _INF:
                    continue
                for j in range(_N):
                    if mask >> j & 1:
                        continue
                    new_mask = mask | (1 << j)
                    new_cost = dp[mask][i] + _DIST[i][j]
                    if new_cost < dp[new_mask][j]:
                        dp[new_mask][j] = new_cost
                        parent[new_mask][j] = i
                        states_to_yield.append((new_mask, j, new_cost, popcount + 1))

        # Yield states grouped by number of cities visited
        for i, (new_mask, j, cost, level) in enumerate(states_to_yield):
            # Show current best dp values for this mask
            best_vals = [min(dp[new_mask][k] for k in range(_N) if dp[new_mask][k] < _INF)]
            best_val = best_vals[0] if best_vals else 0
            mx = max(cost, 1)
            scaled = tuple(
                max(1, min(99, int(dp[new_mask][k] * 99 // (best_val * 2 or 1))))
                if dp[new_mask][k] < _INF else 1
                for k in range(_N)
            )
            yield SortState(
                array=scaled,
                comparing=(j, j),
                last_swap=None,
                sorted_indices=frozenset(k for k in range(_N) if new_mask >> k & 1),
                comparisons=i + 1,
                swaps=cost,
                description=(
                    f"Extend to city {j}: mask={bin(new_mask)} "
                    f"cost={cost} (visited {level}/{_N})"
                ),
            )

        # Find optimal tour
        full_mask = size - 1
        min_cost = _INF
        last_city = -1
        for i in range(1, _N):
            total = dp[full_mask][i] + _DIST[i][0] if dp[full_mask][i] < _INF else _INF
            if total < min_cost:
                min_cost = total
                last_city = i

        # Reconstruct path
        path = []
        mask = full_mask
        curr = last_city
        while curr != -1:
            path.append(curr)
            prev = parent[mask][curr]
            mask ^= (1 << curr)
            curr = prev
        path.reverse()
        path.append(0)

        path_str = " → ".join(map(str, path))
        mx = max(dp[full_mask][i] for i in range(_N) if dp[full_mask][i] < _INF)
        scaled_final = tuple(
            max(1, min(99, int(dp[full_mask][i] * 99 // mx)))
            if dp[full_mask][i] < _INF else 1
            for i in range(_N)
        )
        return SortState(
            array=scaled_final,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(_N)),
            comparisons=len(states_to_yield),
            swaps=int(min_cost),
            description=(
                f"Optimal TSP tour: {path_str} "
                f"cost={int(min_cost)}"
            ),
        )
