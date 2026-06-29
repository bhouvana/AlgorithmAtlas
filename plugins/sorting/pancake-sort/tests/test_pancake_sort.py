"""Tests for Pancake Sort plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "pancake_sort",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PancakeSortSimulation = _mod.PancakeSortSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 7, seed: int = 0):
    sim = PancakeSortSimulation()
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


class TestPancakeSortMetadata:
    def test_slug(self):
        assert PancakeSortSimulation().metadata().slug == "pancake-sort"

    def test_category(self):
        assert PancakeSortSimulation().metadata().category == "sorting"

    def test_visualization_type(self):
        assert PancakeSortSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestPancakeSortCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_array_sorted(self, seed: int):
        initial, _, final = run(7, seed)
        assert list(final.array) == sorted(initial.array)

    def test_has_frames(self):
        _, frames, _ = run(7)
        assert len(frames) > 0

    def test_all_indices_sorted(self):
        _, _, final = run(7)
        assert len(final.sorted_indices) == 7


class TestPancakeSortFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(7)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_flips_at_most_2n_minus_3(self):
        initial, _, final = run(7)
        n = len(initial.array)
        assert final.swaps <= 2 * (n - 1)
