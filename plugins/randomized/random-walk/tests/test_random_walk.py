"""Tests for Random Walk (2D) plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "random_walk", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
RandomWalkSimulation = _mod.RandomWalkSimulation

from algorithm_atlas_sdk import GridState, SimulationParams

GRID_SIZE = 20


def make_params(seed=0, steps=50):
    return SimulationParams(seed=seed, inputs={"steps": steps})


def run(seed=0, steps=50):
    sim = RandomWalkSimulation()
    params = make_params(seed=seed, steps=steps)
    init = sim.initialize(params)
    gen = sim.steps(init)
    states = []
    try:
        while True:
            states.append(next(gen))
    except StopIteration as e:
        final = e.value
    return init, states, final


class TestMetadata:
    def test_slug(self):
        assert RandomWalkSimulation().metadata().slug == "random-walk"

    def test_category(self):
        assert RandomWalkSimulation().metadata().category == "randomized"

    def test_visualization_type(self):
        assert RandomWalkSimulation().metadata().visualization_type == "GRID"


class TestInitialize:
    def test_returns_grid_state(self):
        init = RandomWalkSimulation().initialize(make_params())
        assert isinstance(init, GridState)

    def test_starts_at_centre(self):
        init = RandomWalkSimulation().initialize(make_params())
        assert init.current == (GRID_SIZE // 2, GRID_SIZE // 2)

    def test_grid_dimensions(self):
        init = RandomWalkSimulation().initialize(make_params())
        assert len(init.grid) == GRID_SIZE
        assert all(len(row) == GRID_SIZE for row in init.grid)

    def test_description_contains_steps_and_seed(self):
        init = RandomWalkSimulation().initialize(make_params(seed=7, steps=30))
        assert "steps=30" in init.description
        assert "seed=7" in init.description


class TestSteps:
    def test_produces_states(self):
        _, states, _ = run()
        assert len(states) >= 1

    def test_all_grid_states(self):
        _, states, final = run()
        for s in states:
            assert isinstance(s, GridState)
        assert isinstance(final, GridState)

    def test_grid_stays_bounded(self):
        _, states, _ = run(steps=100)
        for s in states:
            if s.current is not None:
                r, c = s.current
                assert 0 <= r < GRID_SIZE
                assert 0 <= c < GRID_SIZE

    def test_path_grows(self):
        _, states, _ = run(steps=50)
        prev = 0
        for s in states:
            assert len(s.path) >= prev
            prev = len(s.path)

    def test_path_ends_at_current(self):
        _, states, _ = run()
        for s in states:
            if s.current is not None and len(s.path) > 0:
                assert s.path[-1] == s.current

    def test_reproducible(self):
        _, _, f1 = run(seed=5, steps=40)
        _, _, f2 = run(seed=5, steps=40)
        assert f1.description == f2.description

    def test_final_has_done_keyword(self):
        _, _, final = run()
        assert "Done" in final.description

    def test_unique_cell_count_positive(self):
        _, _, final = run()
        assert "unique" in final.description

    def test_step_count_matches_param(self):
        _, _, final = run(steps=30)
        assert "30 steps" in final.description
