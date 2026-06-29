"""Tests for Coin Change DP plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Optional

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "coin_change_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CoinChangeDPSimulation = _mod.CoinChangeDPSimulation
_COINS = _mod._COINS

from algorithm_atlas_sdk import SimulationParams


def run(amount: int = 12, seed: int = 0):
    sim = CoinChangeDPSimulation()
    params = SimulationParams(seed=seed, inputs={"target_amount": amount}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


def naive_min_coins(amount: int, coins: list) -> Optional[int]:
    """Reference implementation."""
    INF = float("inf")
    dp = [INF] * (amount + 1)
    dp[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return None if dp[amount] == INF else int(dp[amount])


class TestCoinChangeMetadata:
    def test_slug(self):
        assert CoinChangeDPSimulation().metadata().slug == "coin-change"

    def test_category(self):
        assert CoinChangeDPSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert CoinChangeDPSimulation().metadata().visualization_type == "MATRIX"


class TestCoinChangeTable:
    def test_table_is_1d(self):
        initial, _, _ = run(12)
        assert len(initial.table) == 1

    def test_table_size(self):
        initial, _, _ = run(12)
        assert len(initial.table[0]) == 13  # amount + 1

    def test_base_case_initialized(self):
        initial, _, _ = run(10)
        assert initial.table[0][0] == 0

    def test_rest_is_none(self):
        initial, _, _ = run(10)
        for v in initial.table[0][1:]:
            assert v is None

    @pytest.mark.parametrize("amount", [8, 10, 12, 15, 20])
    def test_table_size_matches_amount(self, amount: int):
        initial, _, _ = run(amount)
        assert len(initial.table[0]) == amount + 1


class TestCoinChangeCorrectness:
    @pytest.mark.parametrize("amount", [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
    def test_final_value_matches_naive(self, amount: int):
        _, _, final = run(amount)
        expected = naive_min_coins(amount, _COINS)
        result = final.table[0][amount]
        assert result == expected, (
            f"amount={amount}: got {result}, expected {expected}"
        )

    def test_base_case_preserved(self):
        _, _, final = run(12)
        assert final.table[0][0] == 0

    def test_known_amounts_with_coins_1_2_5(self):
        # Coins [1,2,5]: known optimal counts
        known = {
            1: 1, 2: 1, 3: 2, 4: 2, 5: 1,
            6: 2, 7: 2, 8: 3, 9: 3, 10: 2,
            11: 3, 12: 3, 13: 4, 14: 4, 15: 3,
        }
        for amount, expected in known.items():
            if 8 <= amount <= 20:
                _, _, final = run(amount)
                assert final.table[0][amount] == expected, (
                    f"amount={amount}: expected {expected}, got {final.table[0][amount]}"
                )

    def test_no_none_in_final_table(self):
        # All amounts [1,2,5] are reachable since coin 1 is included
        _, _, final = run(15)
        for v in final.table[0]:
            assert v is not None


class TestCoinChangeFrames:
    def test_frame_count(self):
        _, frames, _ = run(12)
        assert len(frames) == 12  # one frame per amount 1..12

    def test_current_cell_is_set_per_frame(self):
        _, frames, _ = run(12)
        for i, frame in enumerate(frames):
            assert frame.current_cell == (0, i + 1)

    def test_no_current_cell_at_end(self):
        _, _, final = run(12)
        assert final.current_cell is None

    def test_all_cells_computed_at_end(self):
        _, _, final = run(12)
        assert len(final.computed_cells) == 13  # 0..12

    def test_computed_cells_grow_monotonically(self):
        _, frames, _ = run(10)
        for i, frame in enumerate(frames):
            assert len(frame.computed_cells) == i + 2  # base(0) + 1..i+1

    def test_serializable(self):
        import json
        initial, frames, final = run(10)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_clamp_min(self):
        sim = CoinChangeDPSimulation()
        p = SimulationParams(seed=0, inputs={"target_amount": 1}, config={})
        s = sim.initialize(p)
        assert len(s.table[0]) == 9  # min=8 → 9 cells

    def test_clamp_max(self):
        sim = CoinChangeDPSimulation()
        p = SimulationParams(seed=0, inputs={"target_amount": 99}, config={})
        s = sim.initialize(p)
        assert len(s.table[0]) == 21  # max=20 → 21 cells
