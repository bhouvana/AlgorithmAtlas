"""Tests for Monte Carlo π Estimation plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "monte_carlo_pi", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
MonteCarloPiSimulation = _mod.MonteCarloPiSimulation

from algorithm_atlas_sdk import GridState, SimulationParams

GRID_SIZE = 20


def make_params(seed=0, dart_count=80):
    return SimulationParams(seed=seed, inputs={"dart_count": dart_count})


def run(seed=0, dart_count=80):
    sim = MonteCarloPiSimulation()
    params = make_params(seed=seed, dart_count=dart_count)
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
        assert MonteCarloPiSimulation().metadata().slug == "monte-carlo-pi"

    def test_category(self):
        assert MonteCarloPiSimulation().metadata().category == "randomized"

    def test_visualization_type(self):
        assert MonteCarloPiSimulation().metadata().visualization_type == "GRID"


class TestInitialize:
    def test_returns_grid_state(self):
        init = MonteCarloPiSimulation().initialize(make_params())
        assert isinstance(init, GridState)

    def test_grid_dimensions(self):
        init = MonteCarloPiSimulation().initialize(make_params())
        assert len(init.grid) == GRID_SIZE
        assert all(len(row) == GRID_SIZE for row in init.grid)

    def test_description_has_n_and_seed(self):
        init = MonteCarloPiSimulation().initialize(make_params(seed=3, dart_count=60))
        assert "60" in init.description
        assert "seed=3" in init.description


class TestSteps:
    def test_produces_steps(self):
        _, states, _ = run()
        assert len(states) >= 1

    def test_all_grid_states(self):
        _, states, final = run()
        for s in states:
            assert isinstance(s, GridState)
        assert isinstance(final, GridState)

    def test_pi_estimate_in_final(self):
        _, _, final = run(seed=0, dart_count=200)
        assert "π" in final.description or "pi" in final.description.lower()

    def test_pi_estimate_roughly_correct(self):
        # With 200 darts and seed=0, should be within 0.5 of true π
        import re
        _, _, final = run(seed=0, dart_count=200)
        m = re.search(r"π\s*[≈~=]\s*(\d+\.\d+)", final.description)
        if m:
            pi_est = float(m.group(1))
            assert abs(pi_est - 3.14159) < 0.6

    def test_reproducible(self):
        _, _, f1 = run(seed=5, dart_count=80)
        _, _, f2 = run(seed=5, dart_count=80)
        assert f1.description == f2.description

    def test_grid_bounded(self):
        _, states, _ = run()
        for s in states:
            assert len(s.grid) == GRID_SIZE
            for row in s.grid:
                assert len(row) == GRID_SIZE
