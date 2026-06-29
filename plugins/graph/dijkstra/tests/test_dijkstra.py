"""Tests for Dijkstra's shortest path plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "dijkstra_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
DijkstraSimulation = _mod.DijkstraSimulation
_build_adj = _mod._build_adj

from algorithm_atlas_sdk import SimulationParams


def run(node_count: int = 7, seed: int = 42):
    sim = DijkstraSimulation()
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


def naive_dijkstra(nodes, edges, start):
    """Reference Dijkstra implementation."""
    import heapq
    INF = float("inf")
    adj = {}
    for e in edges:
        w = e.weight or 1.0
        adj.setdefault(e.source, []).append((e.target, w))
        adj.setdefault(e.target, []).append((e.source, w))
    dist = {n.node_id: INF for n in nodes}
    dist[start] = 0.0
    heap = [(0.0, start)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj.get(u, []):
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))
    return {k: v for k, v in dist.items() if v != INF}


class TestDijkstraMetadata:
    def test_slug(self):
        assert DijkstraSimulation().metadata().slug == "dijkstra"

    def test_category(self):
        assert DijkstraSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert DijkstraSimulation().metadata().visualization_type == "GRAPH"


class TestDijkstraInitialization:
    def test_start_has_distance_zero(self):
        initial, _, _ = run(7)
        start = initial.frontier[0]
        assert initial.distances[start] == 0.0

    def test_edges_have_weights(self):
        initial, _, _ = run(7)
        for e in initial.edges:
            assert e.weight is not None
            assert e.weight > 0

    def test_graph_is_connected(self):
        initial, _, final = run(7)
        assert len(final.distances) == len(initial.nodes)


class TestDijkstraCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_distances_match_naive(self, seed: int):
        initial, _, final = run(7, seed=seed)
        start = initial.frontier[0]
        expected = naive_dijkstra(initial.nodes, initial.edges, start)
        for node, dist in expected.items():
            assert abs(final.distances.get(node, -1) - dist) < 1e-9, (
                f"seed={seed} node={node}: got {final.distances.get(node)}, expected {dist}"
            )

    def test_source_distance_is_zero(self):
        initial, _, final = run(7)
        start = initial.frontier[0]
        assert final.distances[start] == 0.0

    def test_triangle_inequality(self):
        """For every edge (u,v,w): dist[v] <= dist[u] + w."""
        initial, _, final = run(8, seed=3)
        for e in initial.edges:
            du = final.distances.get(e.source)
            dv = final.distances.get(e.target)
            if du is not None and dv is not None:
                w = e.weight or 1.0
                assert dv <= du + w + 1e-9
                assert du <= dv + w + 1e-9  # undirected

    def test_all_nodes_reachable(self):
        for seed in range(5):
            initial, _, final = run(7, seed=seed)
            assert len(final.distances) == len(initial.nodes)

    def test_distances_non_negative(self):
        _, _, final = run(7)
        for v in final.distances.values():
            assert v >= 0.0


class TestDijkstraFrames:
    def test_settlement_order(self):
        """Nodes should be settled in non-decreasing distance order."""
        initial, frames, final = run(7)
        settle_frames = [f for f in frames if f.current is not None and f.current not in f.visited]
        prev_dist = 0.0
        for f in settle_frames:
            cur_dist = f.distances.get(f.current, 0.0)
            assert cur_dist >= prev_dist - 1e-9
            prev_dist = cur_dist

    def test_no_current_at_end(self):
        _, _, final = run(7)
        assert final.current is None

    def test_frontier_empty_at_end(self):
        _, _, final = run(7)
        assert final.frontier == ()

    def test_all_nodes_settled(self):
        initial, _, final = run(7)
        assert len(final.visited) == len(initial.nodes)

    def test_serializable(self):
        import json
        initial, frames, final = run(7)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_clamp_min(self):
        sim = DijkstraSimulation()
        p = SimulationParams(seed=0, inputs={"node_count": 1}, config={})
        s = sim.initialize(p)
        assert len(s.nodes) == 4  # min=4

    def test_clamp_max(self):
        sim = DijkstraSimulation()
        p = SimulationParams(seed=0, inputs={"node_count": 99}, config={})
        s = sim.initialize(p)
        assert len(s.nodes) == 10  # max=10
