"""Tests for the postorder tree traversal plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "postorder_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PostorderTraversalSimulation = _mod.PostorderTraversalSimulation
_label = _mod._label

from algorithm_atlas_sdk import SimulationParams


def run(node_count: int = 9, seed: int = 42):
    sim = PostorderTraversalSimulation()
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


class TestPostorderBasics:
    def test_slug(self):
        assert PostorderTraversalSimulation().metadata().slug == "postorder-traversal"

    def test_category(self):
        assert PostorderTraversalSimulation().metadata().category == "tree"

    def test_node_count(self):
        initial, _, _ = run(9, 42)
        assert len(initial.nodes) == 9

    def test_edge_count(self):
        initial, _, _ = run(9, 42)
        assert len(initial.edges) == 8

    def test_all_nodes_in_path(self):
        initial, _, final = run(9, 42)
        assert len(final.path) == 9
        assert set(final.path) == {n.node_id for n in initial.nodes}

    def test_all_nodes_visited_at_end(self):
        initial, _, final = run(9, 42)
        assert final.visited == {n.node_id for n in initial.nodes}

    def test_empty_frontier_at_end(self):
        _, _, final = run(9, 42)
        assert final.frontier == ()

    def test_root_is_last(self):
        initial, _, final = run(9, 42)
        targets = {e.target for e in initial.edges}
        root = next(n.node_id for n in initial.nodes if n.node_id not in targets)
        assert final.path[-1] == root, f"Expected root {root} at end, got {final.path[-1]}"

    def test_various_sizes(self):
        for n in [5, 7, 11, 13, 15]:
            initial, _, final = run(n, n + 1)
            assert len(set(final.path)) == n

    def test_frames_not_empty(self):
        _, frames, _ = run(9, 42)
        assert len(frames) > 0

    def test_state_serializable(self):
        import json
        initial, frames, final = run(7, 42)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_nodes_x_y_in_range(self):
        initial, _, _ = run(9, 42)
        for n in initial.nodes:
            assert 0.0 <= n.x <= 1.0
            assert 0.0 <= n.y <= 1.0

    def test_edges_directed(self):
        initial, _, _ = run(9, 42)
        for e in initial.edges:
            assert e.directed is True

    def test_exactly_one_root(self):
        initial, _, _ = run(9, 42)
        targets = {e.target for e in initial.edges}
        roots = {n.node_id for n in initial.nodes} - targets
        assert len(roots) == 1


class TestPostorderStructural:
    def test_children_before_parent(self):
        """In postorder, both children must appear before their parent."""
        initial, _, final = run(9, 42)
        node_x = {n.node_id: n.x for n in initial.nodes}
        children: dict = {n.node_id: [] for n in initial.nodes}
        for e in initial.edges:
            children[e.source].append(e.target)
        for nid in children:
            children[nid].sort(key=lambda c: node_x[c])

        path = list(final.path)
        for nid, kids in children.items():
            parent_pos = path.index(nid)
            for child in kids:
                child_pos = path.index(child)
                assert child_pos < parent_pos, (
                    f"Child {child} should appear before parent {nid} in postorder"
                )

    @pytest.mark.parametrize("seed", range(8))
    def test_root_always_last(self, seed: int):
        initial, _, final = run(9, seed + 300)
        targets = {e.target for e in initial.edges}
        root = next(n.node_id for n in initial.nodes if n.node_id not in targets)
        assert final.path[-1] == root

    @pytest.mark.parametrize("seed", range(8))
    def test_covers_all_nodes(self, seed: int):
        initial, _, final = run(9, seed + 400)
        assert set(final.path) == {n.node_id for n in initial.nodes}
