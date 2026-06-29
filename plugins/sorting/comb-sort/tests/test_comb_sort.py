"""Tests for Comb Sort plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "comb_sort",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CombSortSimulation = _mod.CombSortSimulation

from algorithm_atlas_sdk import SimulationParams


def run(size: int = 10, seed: int = 42):
    sim = CombSortSimulation()
    params = SimulationParams(seed=seed, inputs={"array_size": size}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestCombSortMetadata:
    def test_slug(self):
        assert CombSortSimulation().metadata().slug == "comb-sort"

    def test_category(self):
        assert CombSortSimulation().metadata().category == "sorting"


class TestCombSortCorrectness:
    @pytest.mark.parametrize("seed", range(15))
    def test_output_sorted(self, seed: int):
        initial, _, final = run(10, seed=seed)
        assert list(final.array) == sorted(final.array)

    def test_permutation_preserved(self):
        initial, _, final = run(10)
        assert sorted(initial.array) == sorted(final.array)

    def test_all_sorted_at_end(self):
        initial, _, final = run(10)
        assert len(final.sorted_indices) == len(initial.array)


class TestCombSortFrames:
    def test_has_frames(self):
        _, frames, _ = run(10)
        assert len(frames) > 0

    def test_serializable(self):
        import json
        initial, frames, final = run(10)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
