"""Tests for Cycle Sort plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "cycle_sort",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CycleSortSimulation = _mod.CycleSortSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 8, seed: int = 42):
    sim = CycleSortSimulation()
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


class TestCycleSortMetadata:
    def test_slug(self):
        assert CycleSortSimulation().metadata().slug == "cycle-sort"

    def test_category(self):
        assert CycleSortSimulation().metadata().category == "sorting"

    def test_visualization_type(self):
        assert CycleSortSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestCycleSortCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_sorted_output(self, seed: int):
        initial, _, final = run(8, seed=seed)
        assert final.array == tuple(sorted(initial.array))

    def test_all_indices_sorted(self):
        _, _, final = run(8)
        assert final.sorted_indices == frozenset(range(8))

    def test_same_elements(self):
        initial, _, final = run(8)
        assert sorted(initial.array) == sorted(final.array)

    def test_minimal_writes(self):
        """Cycle sort uses at most n writes for n distinct elements (each write places one element)."""
        _, _, final = run(8)
        n = len(final.array)
        assert final.swaps <= n


class TestCycleSortFrames:
    def test_has_frames(self):
        _, frames, _ = run(8)
        assert len(frames) > 0

    def test_serializable(self):
        import json
        initial, frames, final = run(8)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
