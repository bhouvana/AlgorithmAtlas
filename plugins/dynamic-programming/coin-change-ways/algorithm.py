"""Coin Change II (Number of Ways) plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

# (coins, amount, expected_ways)
_INSTANCES = [
    ([1, 2, 5], 5, 4),
    ([2], 3, 0),
    ([1, 2, 3], 4, 4),
    ([1, 2, 5], 10, 10),
    ([1, 2, 3], 5, 5),
    ([2, 3, 7], 6, 2),
    ([1, 5, 10], 10, 4),
    ([2, 5, 10], 20, 6),
    ([1, 3, 4], 6, 4),
    ([1, 2, 5, 10], 12, 15),
]


def _solve(coins: list, amount: int) -> int:
    dp = [0] * (amount + 1)
    dp[0] = 1
    for coin in coins:
        for j in range(coin, amount + 1):
            dp[j] += dp[j - coin]
    return dp[amount]


class CoinChangeWaysSimulation(AlgorithmPlugin):
    """Coin Change II — count distinct coin combinations."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="coin-change-ways",
            name="Coin Change II (Number of Ways)",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Count distinct ways to reach amount using unlimited coins of given denominations.",
            intuition=(
                "For each coin, update dp[j] += dp[j-coin] for all reachable amounts. "
                "Processing coin by coin avoids counting permutations as distinct."
            ),
            complexity_time_best="O(n·amount)",
            complexity_time_average="O(n·amount)",
            complexity_time_worst="O(n·amount)",
            complexity_space="O(amount)",
            tags=("dynamic-programming", "coin-change", "combinations", "unbounded-knapsack"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        coins, amount, expected = _INSTANCES[params.seed % len(_INSTANCES)]
        # Table: (n_coins+1) rows × (amount+1) cols
        # Row i: dp values after processing coins[0..i-1]
        n = len(coins)
        W = amount + 1
        rows = []
        dp = [0] * W
        dp[0] = 1
        rows.append(tuple(dp))
        for coin in coins:
            for j in range(coin, W):
                dp[j] += dp[j - coin]
            rows.append(tuple(dp))
        # Just show initial state
        init_dp = [0] * W
        init_dp[0] = 1
        return DPState(
            table=tuple([tuple(init_dp)]),
            current_cell=None,
            computed_cells=frozenset(),
            description=f"Coins={coins} amount={amount} expected={expected}",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        desc = initial_state.description
        coins_str = desc.split("Coins=")[1].split(" amount=")[0]
        coins = list(map(int, coins_str.strip("[]").split(", ")))
        amount = int(desc.split("amount=")[1].split(" ")[0])
        expected = int(desc.split("expected=")[1])
        W = amount + 1

        dp = [0] * W
        dp[0] = 1
        computed: set = {(0, 0)}
        rows = [tuple(dp)]

        for ci, coin in enumerate(coins):
            for j in range(coin, W):
                dp[j] += dp[j - coin]
                computed.add((ci + 1, j))
                rows = [tuple(dp)]
                yield DPState(
                    table=tuple(rows),
                    current_cell=(0, j),
                    computed_cells=frozenset(computed),
                    description=f"Coin {coin}: dp[{j}]={dp[j]} (using coin {coin} from dp[{j-coin}]={dp[j-coin]-dp[j]+dp[j]})",
                )

        return DPState(
            table=tuple([tuple(dp)]),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Ways to make {amount} = {dp[amount]}",
        )
