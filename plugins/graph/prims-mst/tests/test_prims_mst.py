"""Tests for Prim's MST plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "prims_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PrimsMSTSimulation = _mod.PrimsMSTSimulation

from algorithm_atlas_sdk import SimulationParams


def run(node_count: int = 7, seed: int = 42):
    sim = PrimsMSTSimulation()
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


def naive_prim_cost(nodes, edges, start):
    """Compute MST total cost with reference Prim's."""
    import heapq
    INF = float("inf")
    adj = {}
    for e in edges:
        w = e.weight or 1.0
        adj.setdefault(e.source, []).append((e.target, w))
        adj.setdefault(e.target, []).append((e.source, w))
    in_mst = set()
    key = {nd.node_id: INF for nd in nodes}
    key[start] = 0.0
    heap = [(0.0, start)]
    total = 0.0
    while heap:
        cost, u = heapq.heappop(heap)
        if u in in_mst:
            continue
        in_mst.add(u)
        total += cost
        for v, w in adj.get(u, []):
            if v not in in_mst and w < key[v]:
                key[v] = w
                heapq.heappush(heap, (w, v))
    return total


class TestPrimsMSTMetadata:
    def test_slug(self):
        assert PrimsMSTSimulation().metadata().slug == "prims-mst"

    def test_category(self):
        assert PrimsMSTSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert PrimsMSTSimulation().metadata().visualization_type == "GRAPH"


class TestPrimsMSTCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_all_nodes_in_mst(self, seed: int):
        initial, _, final = run(7, seed=seed)
        assert len(final.visited) == len(initial.nodes)

    @pytest.mark.parametrize("seed", range(8))
    def test_mst_cost_matches_prim_reference(self, seed: int):
        initial, _, final = run(7, seed=seed)
        start = initial.frontier[0]
        expected = naive_prim_cost(initial.nodes, initial.edges, start)
        # Extract total from description: "total cost = X"
        desc = final.description
        if "total cost =" in desc:
            got = float(desc.split("total cost =")[1].strip().split(",")[0].split()[0])
            assert abs(got - expected) < 1e-9, f"seed={seed}: got {got}, expected {expected}"

    def test_edges_have_weights(self):
        initial, _, _ = run(7)
        for e in initial.edges:
            assert e.weight is not None
            assert e.weight > 0

    def test_source_distance_zero(self):
        initial, _, _ = run(7)
        start = initial.frontier[0]
        assert initial.distances[start] == 0.0


class TestPrimsMSTFrames:
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
        sim = PrimsMSTSimulation()
        p = SimulationParams(seed=0, inputs={"node_count": 1}, config={})
        s = sim.initialize(p)
        assert len(s.nodes) == 4

    def test_clamp_max(self):
        sim = PrimsMSTSimulation()
        p = SimulationParams(seed=0, inputs={"node_count": 99}, config={})
        s = sim.initialize(p)
        assert len(s.nodes) == 10
