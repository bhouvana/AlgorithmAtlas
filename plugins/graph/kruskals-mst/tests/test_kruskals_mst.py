"""Tests for Kruskal's MST plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "kruskals_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
KruskalsMSTSimulation = _mod.KruskalsMSTSimulation
UnionFind = _mod.UnionFind

from algorithm_atlas_sdk import SimulationParams


def run(node_count: int = 7, seed: int = 42):
    sim = KruskalsMSTSimulation()
    params = SimulationParams(seed=seed, inputs={"node_count": node_count}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


def naive_kruskal_cost(nodes, edges):
    """Reference Kruskal's MST cost."""
    uf = UnionFind([nd.node_id for nd in nodes])
    total = 0.0
    for e in sorted(edges, key=lambda e: e.weight or 0):
        if uf.union(e.source, e.target):
            total += e.weight or 0
    return total


class TestKruskalsMSTMetadata:
    def test_slug(self):
        assert KruskalsMSTSimulation().metadata().slug == "kruskals-mst"

    def test_category(self):
        assert KruskalsMSTSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert KruskalsMSTSimulation().metadata().visualization_type == "GRAPH"


class TestUnionFind:
    def test_initially_separate(self):
        uf = UnionFind(["A", "B", "C"])
        assert uf.find("A") != uf.find("B")

    def test_union_joins(self):
        uf = UnionFind(["A", "B", "C"])
        uf.union("A", "B")
        assert uf.find("A") == uf.find("B")

    def test_same_component_returns_false(self):
        uf = UnionFind(["A", "B"])
        uf.union("A", "B")
        assert uf.union("A", "B") is False

    def test_different_components_returns_true(self):
        uf = UnionFind(["A", "B"])
        assert uf.union("A", "B") is True


class TestKruskalsMSTCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_mst_cost_matches_reference(self, seed: int):
        initial, _, final = run(7, seed=seed)
        expected = naive_kruskal_cost(initial.nodes, initial.edges)
        # Extract cost from description
        desc = final.description
        if "total weight=" in desc:
            got = float(desc.split("total weight=")[1].strip())
            assert abs(got - expected) < 1e-9, f"seed={seed}: got {got}, expected {expected}"

    @pytest.mark.parametrize("seed", range(8))
    def test_mst_has_v_minus_1_edges(self, seed: int):
        initial, _, final = run(7, seed=seed)
        n = len(initial.nodes)
        # description has "N edges"
        desc = final.description
        if "edges," in desc:
            edge_count = int(desc.split("edges,")[0].split()[-1])
            assert edge_count == n - 1

    def test_edges_have_weights(self):
        initial, _, _ = run(7)
        for e in initial.edges:
            assert e.weight is not None
            assert e.weight > 0


class TestKruskalsMSTFrames:
    def test_has_frames(self):
        _, frames, _ = run(7)
        assert len(frames) > 0

    def test_no_current_at_end(self):
        _, _, final = run(7)
        assert final.current is None

    def test_frontier_empty_at_end(self):
        _, _, final = run(7)
        assert final.frontier == ()

    def test_serializable(self):
        import json
        initial, frames, final = run(7)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_clamp_min(self):
        sim = KruskalsMSTSimulation()
        p = SimulationParams(seed=0, inputs={"node_count": 1}, config={})
        s = sim.initialize(p)
        assert len(s.nodes) == 4

    def test_clamp_max(self):
        sim = KruskalsMSTSimulation()
        p = SimulationParams(seed=0, inputs={"node_count": 99}, config={})
        s = sim.initialize(p)
        assert len(s.nodes) == 10
