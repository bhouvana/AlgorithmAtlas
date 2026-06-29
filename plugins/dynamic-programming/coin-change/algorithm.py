"""Coin Change (minimum coins) DP plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator, List, Optional, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

_INF = 10_000  # sentinel for "unreachable"
_COINS = [1, 2, 5]  # fixed denominations for clear visualization


class CoinChangeDPSimulation(AlgorithmPlugin):
    """
    Minimum coin count via 1D bottom-up DP.

    Coins: [1, 2, 5] (fixed for visual clarity)
    dp[0] = 0
    dp[a] = min(dp[a - c] + 1) for each coin c <= a
    dp[a] = INF if unreachable

    1-row table of size (amount + 1).
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="coin-change",
            name="Coin Change (Min Coins)",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Minimum number of coins to make a target amount. Coins: 1, 2, 5.",
            intuition="dp[a] = min coins for amount a. For each amount, try subtracting each coin and take the minimum. Fills left to right — each cell depends only on previously computed cells.",
            complexity_time_best="O(amount · coins)",
            complexity_time_average="O(amount · coins)",
            complexity_time_worst="O(amount · coins)",
            complexity_space="O(amount)",
            tags=("dynamic-programming", "coins", "optimization", "bottom-up"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        amount: int = max(8, min(params.inputs.get("target_amount", 12), 20))
        row: Tuple[Optional[int], ...] = tuple(None if a > 0 else 0 for a in range(amount + 1))
        return DPState(
            table=(row,),
            current_cell=None,
            computed_cells=frozenset({(0, 0)}),
            description=f"Coin change: amount={amount}, coins={_COINS}. dp[0]=0",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        amount = len(initial_state.table[0]) - 1
        dp: List[Optional[int]] = [None] * (amount + 1)
        dp[0] = 0
        computed: set = {(0, 0)}

        for a in range(1, amount + 1):
            best: Optional[int] = None
            used_coin: Optional[int] = None
            for c in _COINS:
                if c <= a and dp[a - c] is not None:
                    candidate = dp[a - c] + 1  # type: ignore[operator]
                    if best is None or candidate < best:
                        best = candidate
                        used_coin = c
            dp[a] = best
            computed.add((0, a))

            if best is not None:
                desc = f"dp[{a}] = dp[{a}-{used_coin}]({dp[a-used_coin]})+1 = {best}"  # type: ignore[operator]
            else:
                desc = f"dp[{a}] = ∞ (unreachable with coins {_COINS})"

            yield DPState(
                table=(tuple(dp),),
                current_cell=(0, a),
                computed_cells=frozenset(computed),
                description=desc,
            )

        result = dp[amount]
        return DPState(
            table=(tuple(dp),),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=(
                f"Min coins for {amount}: {result}"
                if result is not None
                else f"Amount {amount} is unreachable with coins {_COINS}"
            ),
        )
