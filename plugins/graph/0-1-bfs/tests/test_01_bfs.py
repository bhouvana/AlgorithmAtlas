"""Tests for 0-1 BFS plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "zero_one_bfs", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ZeroOneBFSSimulation = _mod.ZeroOneBFSSimulation

from algorithm_atlas_sdk import GraphTraversalState, SimulationParams


def make_params():
    return SimulationParams(seed=0, inputs={})


def run():
    sim = ZeroOneBFSSimulation()
    params = make_params()
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
        assert ZeroOneBFSSimulation().metadata().slug == "0-1-bfs"

    def test_category(self):
        assert ZeroOneBFSSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert ZeroOneBFSSimulation().metadata().visualization_type == "GRAPH"


class TestInitialize:
    def test_returns_graph_state(self):
        init = ZeroOneBFSSimulation().initialize(make_params())
        assert isinstance(init, GraphTraversalState)

    def test_has_nodes(self):
        init = ZeroOneBFSSimulation().initialize(make_params())
        assert len(init.nodes) == 7

    def test_has_edges(self):
        init = ZeroOneBFSSimulation().initialize(make_params())
        assert len(init.edges) > 0

    def test_source_in_frontier(self):
        init = ZeroOneBFSSimulation().initialize(make_params())
        assert "0" in init.frontier


class TestSteps:
    def test_produces_steps(self):
        _, states, _ = run()
        assert len(states) >= 1

    def test_all_graph_states(self):
        _, states, final = run()
        for s in states:
            assert isinstance(s, GraphTraversalState)
        assert isinstance(final, GraphTraversalState)

    def test_visited_grows(self):
        _, states, _ = run()
        prev = 0
        for s in states:
            assert len(s.visited) >= prev
            prev = len(s.visited)

    def test_distances_computed(self):
        _, _, final = run()
        assert len(final.distances) == 7

    def test_source_distance_zero(self):
        _, _, final = run()
        assert final.distances["0"] == 0.0

    def test_shortest_path_to_target(self):
        # Source=0, Target=6
        # Optimal path: 0→1(w=0)→3(w=0)... no, 1→3 costs 0 but 3→5 costs 1
        # Let's verify: 0→1→4→5→6: 0+1+0+0=1 or 0→1→3→5→6: 0+0+1+0=1
        # Actually: edges: 0-1:0, 0-2:1, 1-3:0, 1-4:1, 2-4:0, 3-5:1, 4-5:0, 5-6:0
        # 0→1→3: 0+0=0, 3→5: +1=1, 5→6: +0=1
        # 0→1→4: 0+1=1... no wait 1-4 is w=1
        # 0→2→4→5→6: 1+0+0+0=1
        # Minimum = 1
        _, _, final = run()
        assert final.distances["6"] == 1.0

    def test_all_nodes_reached(self):
        _, _, final = run()
        for i in range(7):
            assert str(i) in final.distances
            assert final.distances[str(i)] < float("inf")

    def test_final_description_has_path(self):
        _, _, final = run()
        assert "→" in final.description or "path" in final.description.lower()

    def test_reproducible(self):
        _, _, f1 = run()
        _, _, f2 = run()
        assert f1.distances == f2.distances
