"""Tests for Minimum Path Sum plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "min_path_sum",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
MinPathSumSimulation = _mod.MinPathSumSimulation
_min_path = _mod._min_path
_make_grid = _mod._make_grid

from algorithm_atlas_sdk import SimulationParams
import random


def run(n: int = 4, seed: int = 0):
    sim = MinPathSumSimulation()
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


class TestMinPathSumMetadata:
    def test_slug(self):
        assert MinPathSumSimulation().metadata().slug == "min-path-sum"

    def test_category(self):
        assert MinPathSumSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert MinPathSumSimulation().metadata().visualization_type == "MATRIX"


class TestMinPathSumCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_min_sum(self, seed: int):
        initial, _, final = run(4, seed)
        grid = [list(row) for row in initial.table]
        expected = _min_path(grid)
        result = int(final.description.split("= ")[1])
        assert result == expected

    def test_has_n2_frames(self):
        initial, frames, _ = run(4)
        n = len(initial.table)
        assert len(frames) == n * n


class TestMinPathSumFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(4)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_table_is_n_by_n(self):
        initial, _, final = run(4)
        assert len(final.table) == 4
        for row in final.table:
            assert len(row) == 4
