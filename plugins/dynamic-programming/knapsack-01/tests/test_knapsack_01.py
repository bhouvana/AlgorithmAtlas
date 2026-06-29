"""Tests for 0/1 Knapsack DP plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import List, Tuple

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "knapsack_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
Knapsack01Simulation = _mod.Knapsack01Simulation

from algorithm_atlas_sdk import SimulationParams


def run(item_count: int = 4, capacity: int = 8, seed: int = 42):
    sim = Knapsack01Simulation()
    params = SimulationParams(seed=seed, inputs={"item_count": item_count, "capacity": capacity}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


def parse_items(description: str) -> Tuple[int, int, List[Tuple[int, int]]]:
    """Parse 'Knapsack: n=N W=W items=w1:v1,...' from description."""
    parts = description.split()
    n = int(parts[1].split("=")[1])
    W = int(parts[2].split("=")[1])
    items_str = parts[3].split("=")[1]
    items = []
    for pair in items_str.split(","):
        wi, vi = pair.split(":")
        items.append((int(wi), int(vi)))
    return n, W, items


def naive_knapsack(items, W):
    n = len(items)
    dp = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        wi, vi = items[i - 1]
        for w in range(W + 1):
            dp[i][w] = dp[i - 1][w]
            if wi <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - wi] + vi)
    return dp[n][W]


class TestKnapsackMetadata:
    def test_slug(self):
        assert Knapsack01Simulation().metadata().slug == "knapsack-01"

    def test_category(self):
        assert Knapsack01Simulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert Knapsack01Simulation().metadata().visualization_type == "MATRIX"


class TestKnapsackTableShape:
    def test_table_dimensions(self):
        initial, _, _ = run(4, 8)
        n = len(initial.table) - 1  # n+1 rows
        W = len(initial.table[0]) - 1  # W+1 cols
        assert n == 4
        assert W == 8

    @pytest.mark.parametrize("n,W", [(3, 6), (4, 8), (5, 10), (6, 12)])
    def test_dimensions_match_params(self, n: int, W: int):
        initial, _, _ = run(n, W)
        assert len(initial.table) == n + 1
        assert len(initial.table[0]) == W + 1


class TestKnapsackCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_max_value_matches_naive(self, seed: int):
        initial, _, final = run(4, 8, seed=seed)
        n, W, items = parse_items(initial.description)
        expected = naive_knapsack(items, W)
        got = final.table[n][W]
        assert got == expected, f"seed={seed}: got {got}, expected {expected}"

    def test_base_row_all_zeros(self):
        _, _, final = run(4, 8)
        assert all(v == 0 for v in final.table[0])

    def test_non_negative_values(self):
        _, _, final = run(4, 8)
        for row in final.table:
            for v in row:
                assert v >= 0

    def test_monotone_along_capacity(self):
        """dp[i][w] >= dp[i][w-1] — more capacity can only help."""
        _, _, final = run(4, 10)
        for row in final.table:
            for j in range(1, len(row)):
                assert row[j] >= row[j - 1]


class TestKnapsackFrames:
    def test_frame_count(self):
        initial, frames, _ = run(4, 8)
        n = len(initial.table) - 1
        W = len(initial.table[0]) - 1
        assert len(frames) == n * (W + 1)

    def test_no_current_cell_at_end(self):
        _, _, final = run(4, 8)
        assert final.current_cell is None

    def test_all_cells_computed_at_end(self):
        initial, _, final = run(4, 8)
        n = len(initial.table) - 1
        W = len(initial.table[0]) - 1
        expected = (n + 1) * (W + 1)
        assert len(final.computed_cells) == expected

    def test_serializable(self):
        import json
        initial, frames, final = run(4, 8)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
