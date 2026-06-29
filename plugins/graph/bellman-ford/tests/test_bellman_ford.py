"""Tests for Bellman-Ford shortest path plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "bellman_ford_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BellmanFordSimulation = _mod.BellmanFordSimulation

from algorithm_atlas_sdk import SimulationParams


def run(node_count: int = 6, seed: int = 42):
    sim = BellmanFordSimulation()
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


def naive_bellman_ford(nodes, edges, start):
    """Reference Bellman-Ford implementation."""
    INF = float("inf")
    dist = {n.node_id: INF for n in nodes}
    dist[start] = 0.0
    V = len(nodes)
    for _ in range(V - 1):
        for e in edges:
            w = e.weight or 1.0
            if dist[e.source] + w < dist[e.target]:
                dist[e.target] = dist[e.source] + w
            if dist[e.target] + w < dist[e.source]:
                dist[e.source] = dist[e.target] + w  # undirected
    return {k: v for k, v in dist.items() if v != INF}


class TestBellmanFordMetadata:
    def test_slug(self):
        assert BellmanFordSimulation().metadata().slug == "bellman-ford"

    def test_category(self):
        assert BellmanFordSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert BellmanFordSimulation().metadata().visualization_type == "GRAPH"


class TestBellmanFordInitialization:
    def test_start_has_zero_distance(self):
        initial, _, _ = run(6)
        start = initial.frontier[0]
        assert initial.distances[start] == 0.0

    def test_edges_have_weights(self):
        initial, _, _ = run(6)
        for e in initial.edges:
            assert e.weight is not None
            assert e.weight > 0


class TestBellmanFordCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_distances_match_naive(self, seed: int):
        initial, _, final = run(6, seed=seed)
        start = initial.frontier[0]
        expected = naive_bellman_ford(initial.nodes, initial.edges, start)
        for node, dist in expected.items():
            got = final.distances.get(node)
            assert got is not None, f"seed={seed} node={node} missing from final distances"
            assert abs(got - dist) < 1e-9, (
                f"seed={seed} node={node}: got {got}, expected {dist}"
            )

    def test_source_distance_is_zero(self):
        initial, _, final = run(6)
        start = initial.frontier[0]
        assert final.distances[start] == 0.0

    def test_triangle_inequality(self):
        initial, _, final = run(7, seed=5)
        for e in initial.edges:
            du = final.distances.get(e.source)
            dv = final.distances.get(e.target)
            if du is not None and dv is not None:
                w = e.weight or 1.0
                assert dv <= du + w + 1e-9
                assert du <= dv + w + 1e-9

    def test_all_nodes_reachable(self):
        for seed in range(5):
            initial, _, final = run(6, seed=seed)
            assert len(final.distances) == len(initial.nodes)

    def test_distances_non_negative(self):
        _, _, final = run(6)
        for v in final.distances.values():
            assert v >= 0.0


class TestBellmanFordFrames:
    def test_has_frames(self):
        _, frames, _ = run(6)
        assert len(frames) > 0

    def test_no_current_at_end(self):
        _, _, final = run(6)
        assert final.current is None

    def test_frontier_empty_at_end(self):
        _, _, final = run(6)
        assert final.frontier == ()

    def test_all_nodes_in_visited_at_end(self):
        initial, _, final = run(6)
        assert len(final.visited) == len(initial.nodes)

    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_clamp_min(self):
        sim = BellmanFordSimulation()
        p = SimulationParams(seed=0, inputs={"node_count": 1}, config={})
        s = sim.initialize(p)
        assert len(s.nodes) == 4  # min=4

    def test_clamp_max(self):
        sim = BellmanFordSimulation()
        p = SimulationParams(seed=0, inputs={"node_count": 99}, config={})
        s = sim.initialize(p)
        assert len(s.nodes) == 8  # max=8

    def test_relaxation_frame_descriptions(self):
        """Frames that relax an edge contain 'relax' or 'Round' in description."""
        _, frames, _ = run(6)
        relax_frames = [f for f in frames if "relax" in f.description.lower() or "round" in f.description.lower()]
        assert len(relax_frames) > 0
