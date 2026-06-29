"""Tests for Bipartite Matching plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "bipartite_matching", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BipartiteMatchingSimulation = _mod.BipartiteMatchingSimulation

from algorithm_atlas_sdk import GraphTraversalState, SimulationParams


def make_params():
    return SimulationParams(seed=0, inputs={})


def run():
    sim = BipartiteMatchingSimulation()
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
        assert BipartiteMatchingSimulation().metadata().slug == "bipartite-matching"

    def test_category(self):
        assert BipartiteMatchingSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert BipartiteMatchingSimulation().metadata().visualization_type == "GRAPH"


class TestInitialize:
    def test_returns_graph_state(self):
        init = BipartiteMatchingSimulation().initialize(make_params())
        assert isinstance(init, GraphTraversalState)

    def test_has_10_nodes(self):
        init = BipartiteMatchingSimulation().initialize(make_params())
        assert len(init.nodes) == 10  # 5 left + 5 right

    def test_has_edges(self):
        init = BipartiteMatchingSimulation().initialize(make_params())
        assert len(init.edges) > 0

    def test_no_matching_initially(self):
        init = BipartiteMatchingSimulation().initialize(make_params())
        assert len(init.visited) == 0


class TestSteps:
    def test_produces_5_steps(self):
        # One step per left node (5 total)
        _, states, _ = run()
        assert len(states) == 5

    def test_all_graph_states(self):
        _, states, final = run()
        for s in states:
            assert isinstance(s, GraphTraversalState)
        assert isinstance(final, GraphTraversalState)

    def test_matching_grows(self):
        _, states, _ = run()
        prev = 0
        for s in states:
            assert len(s.visited) >= prev
            prev = len(s.visited)

    def test_maximum_matching_size(self):
        # Max matching for this graph: L0-R0,L1-R1,L2-R3,L3-R2,L4-R4 = 5
        # or L0-R1,L1-R2,L2-R0,L3-R4,L4-R3 = 5
        _, _, final = run()
        assert len(final.distances) == 5

    def test_final_description_has_matching(self):
        _, _, final = run()
        assert "↔" in final.description or "matching" in final.description.lower()

    def test_matched_nodes_consistent(self):
        _, _, final = run()
        # Each matched L-node corresponds to a unique R-node
        ml = final.distances
        seen_r = set()
        for l, r in ml.items():
            r_int = int(r)
            assert r_int not in seen_r
            seen_r.add(r_int)

    def test_reproducible(self):
        _, _, f1 = run()
        _, _, f2 = run()
        assert f1.distances == f2.distances
