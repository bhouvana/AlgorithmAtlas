"""Tests for Point-in-Polygon plugin."""
from __future__ import annotations

import importlib.util
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "point_in_polygon", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PointInPolygonSimulation = _mod.PointInPolygonSimulation
_ray_crosses_edge = _mod._ray_crosses_edge
_make_convex_polygon = _mod._make_convex_polygon

from algorithm_atlas_sdk import GridState, SimulationParams

GRID_SIZE = 20


def make_params(seed=0):
    return SimulationParams(seed=seed, inputs={})


def run(seed=0):
    sim = PointInPolygonSimulation()
    params = make_params(seed=seed)
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
        assert PointInPolygonSimulation().metadata().slug == "point-in-polygon"

    def test_category(self):
        assert PointInPolygonSimulation().metadata().category == "computational-geometry"

    def test_visualization_type(self):
        assert PointInPolygonSimulation().metadata().visualization_type == "GRID"


class TestInitialize:
    def test_returns_grid_state(self):
        init = PointInPolygonSimulation().initialize(make_params())
        assert isinstance(init, GridState)

    def test_grid_dimensions(self):
        init = PointInPolygonSimulation().initialize(make_params())
        assert len(init.grid) == GRID_SIZE
        assert all(len(row) == GRID_SIZE for row in init.grid)

    def test_description_has_query(self):
        init = PointInPolygonSimulation().initialize(make_params())
        assert "query=" in init.description

    def test_description_has_verts(self):
        init = PointInPolygonSimulation().initialize(make_params())
        assert "verts=" in init.description


class TestRayCrossing:
    def test_horizontal_edge_not_crossed(self):
        assert not _ray_crosses_edge(5, 5, 5, 3, 5, 10)

    def test_edge_above_query_not_crossed(self):
        assert not _ray_crosses_edge(10, 5, 3, 8, 7, 8)

    def test_simple_cross(self):
        # Edge from (2,10) to (12,10), ray from (7,5) rightward → crosses at col=10
        assert _ray_crosses_edge(7, 5, 2, 10, 12, 10)

    def test_edge_left_of_query_not_crossed(self):
        assert not _ray_crosses_edge(7, 15, 2, 5, 12, 5)


class TestSteps:
    def test_produces_steps(self):
        _, states, _ = run()
        assert len(states) >= 1

    def test_all_grid_states(self):
        _, states, final = run()
        for s in states:
            assert isinstance(s, GridState)
        assert isinstance(final, GridState)

    def test_final_has_result(self):
        _, _, final = run()
        desc = final.description.upper()
        assert "INSIDE" in desc or "OUTSIDE" in desc

    def test_grid_bounded(self):
        _, states, _ = run()
        for s in states:
            assert len(s.grid) == GRID_SIZE
            for row in s.grid:
                assert len(row) == GRID_SIZE

    def test_reproducible(self):
        _, _, f1 = run(seed=3)
        _, _, f2 = run(seed=3)
        assert f1.description == f2.description

    def test_various_seeds_run_cleanly(self):
        for seed in range(5):
            _, _, final = run(seed=seed)
            assert "INSIDE" in final.description or "OUTSIDE" in final.description


class TestConvexPolygon:
    def test_polygon_has_n_verts(self):
        verts = _make_convex_polygon(random.Random(0), 6)
        assert len(verts) == 6

    def test_polygon_in_bounds(self):
        verts = _make_convex_polygon(random.Random(0), 8)
        for r, c in verts:
            assert 0 <= r < GRID_SIZE
            assert 0 <= c < GRID_SIZE
