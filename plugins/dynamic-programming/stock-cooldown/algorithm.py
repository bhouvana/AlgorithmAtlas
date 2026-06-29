"""Stock Trading with Cooldown plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_PRICES_EXAMPLES = [
    [1, 2, 3, 0, 2],
    [1, 3, 1, 3, 1, 4],
    [5, 4, 3, 2, 1],
    [1, 2, 4, 2, 5, 7, 2, 4, 9, 0],
    [6, 1, 3, 2, 4, 7],
]


class StockCooldownSimulation(AlgorithmPlugin):
    """Stock trading with 1-day cooldown DP."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="stock-cooldown",
            name="Stock Trading with Cooldown",
            category="dynamic-programming",
            visualization_type="ARRAY_BARS",
            description="Max profit with unlimited trades but 1-day cooldown after each sell.",
            intuition=(
                "States: held, sold (cooldown), rest. "
                "held[i] = max(held[i-1], rest[i-1] - price[i]) [hold or buy]. "
                "sold[i] = held[i-1] + price[i] [sell today]. "
                "rest[i] = max(rest[i-1], sold[i-1]) [wait or finish cooldown]."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(1)",
            tags=("dynamic-programming", "stock", "cooldown", "state-machine"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        prices = _PRICES_EXAMPLES[params.seed % len(_PRICES_EXAMPLES)]
        mx = max(prices)
        arr = tuple(max(1, min(99, p * 99 // mx)) for p in prices)
        prices_str = ",".join(map(str, prices))
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"StockCooldown prices={prices_str}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        prices_str = re.search(r"prices=([0-9,]+)", initial_state.description).group(1)
        prices = list(map(int, prices_str.split(",")))
        n = len(prices)
        mx = max(prices)

        held = -prices[0]
        sold = 0
        rest = 0

        arr = initial_state.array

        for i in range(1, n):
            prev_held, prev_sold, prev_rest = held, sold, rest
            held = max(prev_held, prev_rest - prices[i])
            sold = prev_held + prices[i]
            rest = max(prev_rest, prev_sold)

            # Display prices with profit overlay
            profit = max(held, sold, rest)
            yield SortState(
                array=arr,
                comparing=(i, i),
                last_swap=(i, i) if sold > prev_sold else None,
                sorted_indices=frozenset(range(i + 1)),
                comparisons=i,
                swaps=max(0, profit),
                description=(
                    f"Day {i}: price={prices[i]} "
                    f"held={held} sold={sold} rest={rest} "
                    f"best={max(0, profit)}"
                ),
            )

        final_profit = max(0, sold, rest)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=n,
            swaps=final_profit,
            description=f"Max profit with cooldown = {final_profit}",
        )
