"""Tests for Bridge Finding plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import List, Set, Tuple

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "bridges",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BridgesSimulation = _mod.BridgesSimulation

from algorithm_atlas_sdk import GraphTraversalState, SimulationParams
from algorithm_atlas_sdk.testing import AlgorithmTestHarness


def run(node_count: int = 7, extra_edges: int = 1, seed: int = 42):
    sim = BridgesSimulation()
    params = SimulationParams(
        seed=seed,
        inputs={"node_count": node_count, "extra_edges": extra_edges},
        config={},
    )
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames: List[GraphTraversalState] = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


def brute_force_bridges(nodes: List[str], edges: List[Tuple[str, str]]) -> Set[Tuple[str, str]]:
    """Find bridges by removing each edge and checking connectivity."""
    def is_connected(remaining_edges: list) -> bool:
        adj: dict = {n: [] for n in nodes}
        for u, v in remaining_edges:
            adj[u].append(v)
            adj[v].append(u)
        start = nodes[0]
        visited = {start}
        stack = [start]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v not in visited:
                    visited.add(v)
                    stack.append(v)
        return visited == set(nodes)

    bridges = set()
    for i, (u, v) in enumerate(edges):
        remaining = edges[:i] + edges[i + 1:]
        if not is_connected(remaining):
            a, b = min(u, v), max(u, v)
            bridges.add((a, b))
    return bridges


def parse_bridges_from_path(path: tuple) -> Set[Tuple[str, str]]:
    """Parse bridge strings like 'A-B' from path field."""
    result = set()
    for s in path:
        parts = s.split("-")
        if len(parts) == 2:
            result.add((parts[0], parts[1]))
    return result


class TestBridgesMetadata:
    def test_slug(self):
        assert BridgesSimulation().metadata().slug == "bridges"

    def test_category(self):
        assert BridgesSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert BridgesSimulation().metadata().visualization_type == "GRAPH"


class TestBridgesCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_correct_bridges_found(self, seed: int):
        """Verify against brute-force edge removal check."""
        initial, _, final = run(7, extra_edges=1, seed=seed)

        edge_pairs = [(e.source, e.target) for e in initial.edges]
        node_ids = [n.node_id for n in initial.nodes]
        expected = brute_force_bridges(node_ids, edge_pairs)
        actual = parse_bridges_from_path(final.path)
        assert actual == expected, (
            f"seed={seed}: expected bridges={sorted(expected)}, got={sorted(actual)}"
        )

    def test_bridges_are_valid_edges(self):
        initial, _, final = run(7)
        edge_keys = {
            (min(e.source, e.target), max(e.source, e.target))
            for e in initial.edges
        }
        for bridge_str in final.path:
            parts = bridge_str.split("-")
            key = (parts[0], parts[1])
            assert key in edge_keys, f"Bridge {bridge_str} is not in the edge list"

    def test_path_sorted(self):
        _, _, final = run(7)
        assert list(final.path) == sorted(final.path)

    def test_all_nodes_discovered(self):
        initial, _, final = run(7)
        node_ids = {n.node_id for n in initial.nodes}
        assert final.visited == node_ids

    def test_disc_times_sequential(self):
        initial, _, final = run(7)
        n = len(initial.nodes)
        disc_vals = sorted(int(v) for v in final.distances.values())
        assert disc_vals == list(range(n))

    @pytest.mark.parametrize("seed", range(5))
    def test_larger_graph_correct(self, seed: int):
        initial, _, final = run(9, extra_edges=2, seed=seed)
        edge_pairs = [(e.source, e.target) for e in initial.edges]
        node_ids = [n.node_id for n in initial.nodes]
        expected = brute_force_bridges(node_ids, edge_pairs)
        actual = parse_bridges_from_path(final.path)
        assert actual == expected

    def test_spanning_tree_all_edges_are_bridges(self):
        """A pure spanning tree (extra_edges=0) has n-1 bridges."""
        initial, _, final = run(5, extra_edges=0, seed=42)
        n = len(initial.nodes)
        assert len(final.path) == n - 1

    def test_complete_cycle_has_no_bridges(self):
        """Adding enough edges to close all cycles should yield 0 bridges."""
        initial, _, final = run(5, extra_edges=10, seed=42)
        edge_pairs = [(e.source, e.target) for e in initial.edges]
        node_ids = [n.node_id for n in initial.nodes]
        expected = brute_force_bridges(node_ids, edge_pairs)
        actual = parse_bridges_from_path(final.path)
        assert actual == expected


class TestBridgesFrames:
    def test_has_frames(self):
        _, frames, _ = run(7)
        assert len(frames) > 0

    def test_frontier_empty_at_terminal(self):
        _, _, final = run(7)
        assert final.frontier == ()

    def test_current_none_at_terminal(self):
        _, _, final = run(7)
        assert final.current is None

    def test_visited_grows_monotonically(self):
        _, frames, _ = run(7)
        prev = frozenset()
        for f in frames:
            assert f.visited >= prev
            prev = f.visited

    def test_graph_structure_unchanged(self):
        initial, frames, final = run(7)
        for f in frames + [final]:
            assert f.nodes == initial.nodes
            assert f.edges == initial.edges

    def test_path_grows_monotonically(self):
        _, frames, final = run(7)
        prev = frozenset()
        for f in frames + [final]:
            bridge_set = frozenset(f.path)
            assert bridge_set >= prev
            prev = bridge_set

    def test_bridge_frames_present_when_bridges_exist(self):
        initial, frames, final = run(7, extra_edges=0, seed=42)
        bridge_frames = [f for f in frames if "BRIDGE" in f.description]
        assert len(bridge_frames) >= 1

    def test_back_edge_frames_mention_low(self):
        _, frames, _ = run(7)
        back_frames = [f for f in frames if "Back edge" in f.description]
        for f in back_frames:
            assert "low[" in f.description

    def test_descriptions_nonempty(self):
        _, frames, _ = run(7)
        for f in frames:
            assert isinstance(f.description, str) and len(f.description) > 0

    def test_serializable(self):
        import json
        initial, frames, final = run(7)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_deterministic(self):
        harness = AlgorithmTestHarness(BridgesSimulation())
        params = SimulationParams(seed=42, inputs={"node_count": 7, "extra_edges": 1}, config={})
        harness.assert_deterministic(params)

    def test_final_description_mentions_count(self):
        _, _, final = run(7)
        assert "bridge" in final.description.lower()

    def test_node_positions_in_unit_square(self):
        initial, _, _ = run(7)
        for node in initial.nodes:
            assert 0.0 <= node.x <= 1.0
            assert 0.0 <= node.y <= 1.0
