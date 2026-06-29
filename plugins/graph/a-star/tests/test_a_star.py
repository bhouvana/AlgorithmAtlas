"""Tests for A* pathfinding plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "a_star_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
AStarSimulation = _mod.AStarSimulation
_manhattan = _mod._manhattan

from algorithm_atlas_sdk import SimulationParams, CELL_EMPTY, CELL_WALL, CELL_START, CELL_GOAL, CELL_PATH


def run(grid_size: int = 9, wall_density: int = 20, seed: int = 42):
    sim = AStarSimulation()
    params = SimulationParams(seed=seed, inputs={"grid_size": grid_size, "wall_density": wall_density}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestAStarMetadata:
    def test_slug(self):
        assert AStarSimulation().metadata().slug == "a-star"

    def test_category(self):
        assert AStarSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert AStarSimulation().metadata().visualization_type == "GRID"


class TestAStarGrid:
    def test_grid_is_square(self):
        initial, _, _ = run(9)
        rows = len(initial.grid)
        cols = len(initial.grid[0])
        assert rows == 9
        assert cols == 9

    def test_start_at_top_left(self):
        initial, _, _ = run(9)
        assert initial.grid[0][0] == CELL_START

    def test_goal_at_bottom_right(self):
        initial, _, _ = run(9)
        n = len(initial.grid) - 1
        assert initial.grid[n][n] == CELL_GOAL

    @pytest.mark.parametrize("size", [6, 8, 10, 12])
    def test_grid_size_matches_param(self, size: int):
        initial, _, _ = run(size)
        assert len(initial.grid) == size
        assert len(initial.grid[0]) == size


class TestAStarCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_path_is_valid_when_found(self, seed: int):
        initial, _, final = run(9, wall_density=15, seed=seed)
        if len(final.path) == 0:
            return  # unreachable — that's fine
        path = final.path
        rows = len(initial.grid)
        cols = len(initial.grid[0])
        # Check each step is adjacent
        for i in range(1, len(path)):
            r0, c0 = path[i - 1]
            r1, c1 = path[i]
            assert abs(r0 - r1) + abs(c0 - c1) == 1, f"Non-adjacent path step: {path[i-1]} → {path[i]}"
        # Check start and end
        assert path[0] == (0, 0)
        assert path[-1] == (rows - 1, cols - 1)

    def test_no_path_through_walls(self):
        initial, _, final = run(9, wall_density=15)
        if not final.path:
            return
        for r, c in final.path:
            assert initial.grid[r][c] != CELL_WALL

    def test_path_length_optimal_on_no_walls(self):
        # With no walls, path length = 2*(n-1) (Manhattan distance)
        sim = AStarSimulation()
        params = SimulationParams(seed=42, inputs={"grid_size": 6, "wall_density": 0}, config={})
        initial = sim.initialize(params)
        gen = sim.steps(initial)
        final = None
        try:
            while True:
                next(gen)
        except StopIteration as e:
            final = e.value
        n = 6
        expected_len = 2 * (n - 1) + 1  # n-1 right + n-1 down + 1 for start cell
        if final and final.path:
            assert len(final.path) == expected_len


class TestAStarManhattan:
    def test_same_cell(self):
        assert _manhattan((3, 4), (3, 4)) == 0

    def test_adjacent_cells(self):
        assert _manhattan((0, 0), (0, 1)) == 1
        assert _manhattan((0, 0), (1, 0)) == 1

    def test_diagonal(self):
        assert _manhattan((0, 0), (3, 4)) == 7


class TestAStarFrames:
    def test_has_frames(self):
        _, frames, _ = run(9, wall_density=15)
        assert len(frames) > 0

    def test_serializable(self):
        import json
        initial, frames, final = run(9)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_clamp_min(self):
        sim = AStarSimulation()
        p = SimulationParams(seed=0, inputs={"grid_size": 1}, config={})
        s = sim.initialize(p)
        assert len(s.grid) == 6

    def test_clamp_max(self):
        sim = AStarSimulation()
        p = SimulationParams(seed=0, inputs={"grid_size": 99}, config={})
        s = sim.initialize(p)
        assert len(s.grid) == 12
