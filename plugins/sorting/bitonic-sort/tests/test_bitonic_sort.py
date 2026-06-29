"""Tests for Bitonic Sort plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "bitonic_sort",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BitonicSortSimulation = _mod.BitonicSortSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 8, seed: int = 0):
    sim = BitonicSortSimulation()
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


class TestBitonicSortMetadata:
    def test_slug(self):
        assert BitonicSortSimulation().metadata().slug == "bitonic-sort"

    def test_category(self):
        assert BitonicSortSimulation().metadata().category == "sorting"

    def test_visualization_type(self):
        assert BitonicSortSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestBitonicSortCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_array_sorted(self, seed: int):
        initial, _, final = run(8, seed)
        assert list(final.array) == sorted(initial.array)

    def test_has_frames(self):
        _, frames, _ = run(8)
        assert len(frames) > 0

    def test_all_indices_sorted(self):
        _, _, final = run(8)
        assert len(final.sorted_indices) == 8


class TestBitonicSortFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(8)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
