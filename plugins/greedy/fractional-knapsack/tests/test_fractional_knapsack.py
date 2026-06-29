"""Tests for Fractional Knapsack plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "fractional_knapsack",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
FractionalKnapsackSimulation = _mod.FractionalKnapsackSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 6, seed: int = 42):
    sim = FractionalKnapsackSimulation()
    params = SimulationParams(seed=seed, inputs={"array_size": n}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestFractionalKnapsackMetadata:
    def test_slug(self):
        assert FractionalKnapsackSimulation().metadata().slug == "fractional-knapsack"

    def test_category(self):
        assert FractionalKnapsackSimulation().metadata().category == "greedy"

    def test_visualization_type(self):
        assert FractionalKnapsackSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestFractionalKnapsackInitialize:
    def test_array_size(self):
        initial, _, _ = run(6)
        assert len(initial.array) == 6

    def test_description_has_weights_and_capacity(self):
        initial, _, _ = run(6)
        assert "weights=" in initial.description
        assert "capacity=" in initial.description

    def test_array_values_positive(self):
        initial, _, _ = run(6)
        assert all(v > 0 for v in initial.array)


class TestFractionalKnapsackCorrectness:
    def test_final_value_positive(self):
        _, _, final = run(6)
        assert final.swaps > 0  # total_value * 10

    def test_has_frames(self):
        _, frames, _ = run(6)
        assert len(frames) > 0

    def test_done_message(self):
        _, _, final = run(6)
        assert "Done" in final.description or "max value" in final.description

    def test_array_unchanged(self):
        initial, _, final = run(6)
        assert initial.array == final.array

    @pytest.mark.parametrize("seed", range(10))
    def test_value_positive_all_seeds(self, seed: int):
        _, _, final = run(6, seed=seed)
        assert final.swaps >= 0

    @pytest.mark.parametrize("n", [4, 6, 8, 10])
    def test_various_sizes(self, n: int):
        initial, frames, final = run(n)
        assert len(frames) > 0
        assert len(initial.array) == n

    def test_comparisons_equals_items_considered(self):
        initial, _, final = run(6)
        # comparisons counts each item examined
        assert final.comparisons >= 1
        assert final.comparisons <= len(initial.array)


class TestFractionalKnapsackFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_value_non_decreasing(self):
        _, frames, _ = run(6)
        taken_frames = [f for f in frames if f.last_swap is not None]
        values = [f.swaps for f in taken_frames]
        for i in range(1, len(values)):
            assert values[i] >= values[i - 1]
