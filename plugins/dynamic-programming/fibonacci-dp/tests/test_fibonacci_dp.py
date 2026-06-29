"""Tests for Fibonacci DP plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "fib_dp_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
FibonacciDPSimulation = _mod.FibonacciDPSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 10, seed: int = 0):
    sim = FibonacciDPSimulation()
    params = SimulationParams(seed=seed, inputs={"n": n}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


KNOWN = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765]


class TestFibonacciDPBasics:
    def test_slug(self):
        assert FibonacciDPSimulation().metadata().slug == "fibonacci-dp"

    def test_category(self):
        assert FibonacciDPSimulation().metadata().category == "dynamic-programming"

    def test_table_size(self):
        initial, _, _ = run(10)
        assert len(initial.table) == 1
        assert len(initial.table[0]) == 11  # n+1 cells

    def test_final_value_correct(self):
        for n in range(5, 16):
            _, _, final = run(n)
            assert final.table[0][n] == KNOWN[n], f"fib({n}) expected {KNOWN[n]}"

    def test_all_cells_computed(self):
        _, _, final = run(10)
        assert len(final.computed_cells) == 11

    def test_no_current_cell_at_end(self):
        _, _, final = run(10)
        assert final.current_cell is None

    def test_frames_count(self):
        _, frames, _ = run(10)
        assert len(frames) == 11  # 2 base + 9 fill

    def test_values_match_fibonacci(self):
        _, _, final = run(15)
        for i, v in enumerate(final.table[0]):
            assert v == KNOWN[i], f"dp[{i}] = {v} != {KNOWN[i]}"

    def test_serializable(self):
        import json
        initial, frames, final = run(8)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_clamp_min(self):
        sim = FibonacciDPSimulation()
        p = SimulationParams(seed=0, inputs={"n": 1}, config={})
        s = sim.initialize(p)
        assert len(s.table[0]) == 6  # min=5, so n=5 → 6 cells

    def test_clamp_max(self):
        sim = FibonacciDPSimulation()
        p = SimulationParams(seed=0, inputs={"n": 99}, config={})
        s = sim.initialize(p)
        assert len(s.table[0]) == 21  # max=20 → 21 cells


class TestFibonacciDPIncremental:
    def test_cells_filled_in_order(self):
        _, frames, _ = run(10)
        for i, frame in enumerate(frames):
            expected_filled = i + 1
            assert len(frame.computed_cells) == expected_filled

    @pytest.mark.parametrize("n", range(5, 15))
    def test_correct_values(self, n: int):
        _, _, final = run(n)
        assert final.table[0][n] == KNOWN[n]
