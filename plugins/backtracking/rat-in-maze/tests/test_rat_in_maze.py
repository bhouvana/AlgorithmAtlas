"""Tests for Rat in a Maze plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import List, Tuple

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "rat_in_maze",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
RatInMazeSimulation = _mod.RatInMazeSimulation

from algorithm_atlas_sdk import SimulationParams, CELL_WALL, CELL_PATH, CELL_START, CELL_GOAL


def run(n: int = 6, seed: int = 42):
    sim = RatInMazeSimulation()
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


def is_adjacent(a: Tuple[int, int], b: Tuple[int, int]) -> bool:
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1


class TestRatInMazeMetadata:
    def test_slug(self):
        assert RatInMazeSimulation().metadata().slug == "rat-in-maze"

    def test_category(self):
        assert RatInMazeSimulation().metadata().category == "backtracking"

    def test_visualization_type(self):
        assert RatInMazeSimulation().metadata().visualization_type == "GRID"


class TestRatInMazeCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_path_found(self, seed: int):
        """The DFS carving guarantees a solvable maze."""
        _, _, final = run(6, seed=seed)
        assert "Path found" in final.description

    @pytest.mark.parametrize("seed", range(8))
    def test_path_starts_at_origin(self, seed: int):
        _, _, final = run(6, seed=seed)
        assert final.path[0] == (0, 0)

    @pytest.mark.parametrize("seed", range(8))
    def test_path_ends_at_goal(self, seed: int):
        initial, _, final = run(6, seed=seed)
        n = len(initial.grid)
        assert final.path[-1] == (n - 1, n - 1)

    @pytest.mark.parametrize("seed", range(8))
    def test_path_is_contiguous(self, seed: int):
        _, _, final = run(6, seed=seed)
        for a, b in zip(final.path, final.path[1:]):
            assert is_adjacent(a, b), f"Non-adjacent cells in path: {a} → {b}"

    @pytest.mark.parametrize("seed", range(8))
    def test_path_avoids_walls(self, seed: int):
        initial, _, final = run(6, seed=seed)
        for r, c in final.path:
            assert initial.grid[r][c] != CELL_WALL


class TestRatInMazeFrames:
    def test_has_frames(self):
        _, frames, _ = run(6)
        assert len(frames) > 0

    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_initial_current_is_origin(self):
        initial, _, _ = run(6)
        assert initial.current == (0, 0)

    def test_grid_dimensions(self):
        initial, _, _ = run(6)
        n = len(initial.grid)
        for row in initial.grid:
            assert len(row) == n
