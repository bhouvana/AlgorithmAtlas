"""Tests for Knight's Tour plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "knight_tour",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
KnightTourSimulation = _mod.KnightTourSimulation
MOVES = _mod.MOVES

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = KnightTourSimulation()
    params = SimulationParams(seed=seed, inputs={}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestKnightTourMetadata:
    def test_slug(self):
        assert KnightTourSimulation().metadata().slug == "knight-tour"

    def test_category(self):
        assert KnightTourSimulation().metadata().category == "backtracking"

    def test_visualization_type(self):
        assert KnightTourSimulation().metadata().visualization_type == "GRID"


class TestKnightTourCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_complete_tour(self, seed: int):
        _, _, final = run(seed)
        n = 5
        assert len(final.path) == n * n, f"seed={seed}: only {len(final.path)} moves"

    @pytest.mark.parametrize("seed", range(5))
    def test_valid_knight_moves(self, seed: int):
        _, _, final = run(seed)
        path = final.path
        for i in range(1, len(path)):
            r1, c1 = path[i-1]
            r2, c2 = path[i]
            dr, dc = abs(r2 - r1), abs(c2 - c1)
            assert (dr, dc) in [(1, 2), (2, 1)], f"Invalid move {path[i-1]} → {path[i]}"

    @pytest.mark.parametrize("seed", range(5))
    def test_no_square_visited_twice(self, seed: int):
        _, _, final = run(seed)
        assert len(set(final.path)) == len(final.path)

    def test_has_n2_frames(self):
        _, frames, _ = run(0)
        assert len(frames) == 25


class TestKnightTourFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
