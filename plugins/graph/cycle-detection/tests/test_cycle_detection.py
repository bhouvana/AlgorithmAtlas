"""Tests for Cycle Detection plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import List

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "cycle_detection",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CycleDetectionSimulation = _mod.CycleDetectionSimulation

from algorithm_atlas_sdk import GraphTraversalState, SimulationParams
from algorithm_atlas_sdk.testing import AlgorithmTestHarness


def run(node_count: int = 6, seed: int = 42):
    sim = CycleDetectionSimulation()
    params = SimulationParams(seed=seed, inputs={"node_count": node_count}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames: List[GraphTraversalState] = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


def brute_force_has_cycle(nodes: List[str], adj: dict) -> bool:
    """DFS-based cycle detection reference."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in nodes}

    def dfs(u):
        color[u] = GRAY
        for v in adj.get(u, []):
            if color[v] == GRAY:
                return True
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False

    for n in nodes:
        if color[n] == WHITE:
            if dfs(n):
                return True
    return False


class TestCycleDetectionMetadata:
    def test_slug(self):
        assert CycleDetectionSimulation().metadata().slug == "cycle-detection"

    def test_category(self):
        assert CycleDetectionSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert CycleDetectionSimulation().metadata().visualization_type == "GRAPH"


class TestCycleDetectionCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_result(self, seed: int):
        initial, _, final = run(6, seed=seed)

        adj: dict = {n.node_id: [] for n in initial.nodes}
        for e in initial.edges:
            adj[e.source].append(e.target)

        node_ids = [n.node_id for n in initial.nodes]
        expected = brute_force_has_cycle(node_ids, adj)
        actual = "CYCLE" in final.path
        assert actual == expected, (
            f"seed={seed}: expected cycle={expected}, got path={final.path}"
        )

    def test_even_seed_no_cycle(self):
        """Even seeds generate DAGs by construction."""
        initial, _, final = run(6, seed=0)
        adj: dict = {n.node_id: [] for n in initial.nodes}
        for e in initial.edges:
            adj[e.source].append(e.target)
        node_ids = [n.node_id for n in initial.nodes]
        assert not brute_force_has_cycle(node_ids, adj)
        assert "NO_CYCLE" in final.path

    def test_odd_seed_has_cycle(self):
        """Odd seeds generate graphs with back edges by construction."""
        initial, _, final = run(6, seed=1)
        adj: dict = {n.node_id: [] for n in initial.nodes}
        for e in initial.edges:
            adj[e.source].append(e.target)
        node_ids = [n.node_id for n in initial.nodes]
        assert brute_force_has_cycle(node_ids, adj)
        assert "CYCLE" in final.path

    def test_colors_are_valid(self):
        """All nodes should be BLACK or detected as GRAY at end."""
        initial, _, final = run(6, seed=0)
        for v in final.distances.values():
            assert v in (0.0, 1.0, 2.0)

    def test_edges_directed(self):
        initial, _, _ = run(6)
        for e in initial.edges:
            assert e.directed is True

    def test_all_nodes_have_color(self):
        initial, _, final = run(6)
        node_ids = {n.node_id for n in initial.nodes}
        assert set(final.distances.keys()) == node_ids


class TestCycleDetectionFrames:
    def test_has_frames(self):
        _, frames, _ = run(6)
        assert len(frames) > 0

    def test_frontier_empty_at_terminal(self):
        _, _, final = run(6)
        assert final.frontier == ()

    def test_graph_structure_unchanged(self):
        initial, frames, final = run(6)
        for f in frames + [final]:
            assert f.nodes == initial.nodes
            assert f.edges == initial.edges

    def test_cycle_frame_mentions_back_edge(self):
        _, frames, final = run(6, seed=1)
        if "CYCLE" in final.path:
            back_edge_frames = [f for f in frames if "Back edge" in f.description]
            assert len(back_edge_frames) >= 1

    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_deterministic(self):
        harness = AlgorithmTestHarness(CycleDetectionSimulation())
        params = SimulationParams(seed=42, inputs={"node_count": 6}, config={})
        harness.assert_deterministic(params)
