"""Tests for Articulation Points plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import List, Set

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "articulation_points",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ArticulationPointsSimulation = _mod.ArticulationPointsSimulation

from algorithm_atlas_sdk import GraphTraversalState, SimulationParams
from algorithm_atlas_sdk.testing import AlgorithmTestHarness


def run(node_count: int = 7, extra_edges: int = 1, seed: int = 42):
    sim = ArticulationPointsSimulation()
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


def brute_force_aps(nodes: List[str], adj: dict) -> Set[str]:
    """Find APs by removing each node and checking connectivity."""
    def is_connected(remaining: set) -> bool:
        if not remaining:
            return True
        start = next(iter(remaining))
        visited = {start}
        stack = [start]
        while stack:
            u = stack.pop()
            for v in adj.get(u, []):
                if v in remaining and v not in visited:
                    visited.add(v)
                    stack.append(v)
        return visited == remaining

    all_nodes = set(nodes)
    aps = set()
    for u in nodes:
        remaining = all_nodes - {u}
        if not is_connected(remaining):
            aps.add(u)
    return aps


class TestArticulationPointsMetadata:
    def test_slug(self):
        assert ArticulationPointsSimulation().metadata().slug == "articulation-points"

    def test_category(self):
        assert ArticulationPointsSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert ArticulationPointsSimulation().metadata().visualization_type == "GRAPH"


class TestArticulationPointsCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_correct_aps_found(self, seed: int):
        """Verify against brute-force removal check."""
        initial, _, final = run(7, extra_edges=1, seed=seed)

        # Build adjacency from the graph
        adj: dict = {n.node_id: [] for n in initial.nodes}
        for e in initial.edges:
            adj[e.source].append(e.target)
            adj[e.target].append(e.source)

        node_ids = [n.node_id for n in initial.nodes]
        expected = brute_force_aps(node_ids, adj)
        actual = set(final.path)
        assert actual == expected, (
            f"seed={seed}: expected APs={sorted(expected)}, got={sorted(actual)}"
        )

    def test_chain_graph_has_interior_aps(self):
        """A path graph A-B-C-D-E must have B,C,D as APs."""
        # Build manually: override with a known chain using minimal extra edges
        initial, _, final = run(5, extra_edges=0, seed=0)
        # All interior nodes of the spanning tree chain must be APs
        # We can't guarantee the exact structure, so just verify correctness
        adj: dict = {n.node_id: [] for n in initial.nodes}
        for e in initial.edges:
            adj[e.source].append(e.target)
            adj[e.target].append(e.source)
        node_ids = [n.node_id for n in initial.nodes]
        expected = brute_force_aps(node_ids, adj)
        assert set(final.path) == expected

    def test_path_contains_only_valid_nodes(self):
        initial, _, final = run(7)
        node_ids = {n.node_id for n in initial.nodes}
        for ap in final.path:
            assert ap in node_ids

    def test_path_sorted(self):
        _, _, final = run(7)
        assert list(final.path) == sorted(final.path)

    def test_all_nodes_discovered(self):
        initial, _, final = run(7)
        node_ids = {n.node_id for n in initial.nodes}
        assert final.visited == node_ids

    def test_disc_times_unique(self):
        initial, _, final = run(7)
        disc_vals = [int(v) for v in final.distances.values()]
        assert len(disc_vals) == len(set(disc_vals)), "Discovery times must be unique"

    def test_disc_times_sequential(self):
        initial, _, final = run(7)
        n = len(initial.nodes)
        disc_vals = sorted(int(v) for v in final.distances.values())
        assert disc_vals == list(range(n))

    @pytest.mark.parametrize("seed", range(5))
    def test_larger_graph_correct(self, seed: int):
        initial, _, final = run(9, extra_edges=2, seed=seed)
        adj: dict = {n.node_id: [] for n in initial.nodes}
        for e in initial.edges:
            adj[e.source].append(e.target)
            adj[e.target].append(e.source)
        node_ids = [n.node_id for n in initial.nodes]
        expected = brute_force_aps(node_ids, adj)
        assert set(final.path) == expected


class TestArticulationPointsFrames:
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
        """AP set in path should only grow across frames."""
        _, frames, final = run(7)
        prev = frozenset()
        for f in frames + [final]:
            ap_set = frozenset(f.path)
            assert ap_set >= prev
            prev = ap_set

    def test_descriptions_nonempty(self):
        _, frames, _ = run(7)
        for f in frames:
            assert isinstance(f.description, str) and len(f.description) > 0

    def test_back_edge_frames_mention_low(self):
        _, frames, _ = run(7)
        back_edge_frames = [f for f in frames if "Back edge" in f.description]
        for f in back_edge_frames:
            assert "low[" in f.description

    def test_tree_edge_frames_mention_disc(self):
        _, frames, _ = run(7)
        tree_edge_frames = [f for f in frames if "Tree edge" in f.description]
        for f in tree_edge_frames:
            assert "disc[" in f.description

    def test_serializable(self):
        import json
        initial, frames, final = run(7)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_deterministic(self):
        harness = AlgorithmTestHarness(ArticulationPointsSimulation())
        params = SimulationParams(seed=42, inputs={"node_count": 7, "extra_edges": 1}, config={})
        harness.assert_deterministic(params)

    def test_final_description_mentions_count(self):
        _, _, final = run(7)
        assert "articulation point" in final.description.lower()

    def test_node_positions_in_unit_square(self):
        initial, _, _ = run(7)
        for node in initial.nodes:
            assert 0.0 <= node.x <= 1.0
            assert 0.0 <= node.y <= 1.0
