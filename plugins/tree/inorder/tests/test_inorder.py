"""Tests for the inorder tree traversal plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "inorder_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
InorderTraversalSimulation = _mod.InorderTraversalSimulation
_label = _mod._label

from algorithm_atlas_sdk import SimulationParams


def run(node_count: int = 9, seed: int = 42):
    sim = InorderTraversalSimulation()
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


class TestInorderBasics:
    def test_metadata_slug(self):
        assert InorderTraversalSimulation().metadata().slug == "inorder-traversal"

    def test_metadata_category(self):
        assert InorderTraversalSimulation().metadata().category == "tree"

    def test_initialize_produces_nodes_and_edges(self):
        initial, _, _ = run(9, 42)
        assert len(initial.nodes) == 9
        assert len(initial.edges) == 8  # BST with n nodes has n-1 edges

    def test_all_nodes_visited_at_end(self):
        initial, _, final = run(9, 42)
        node_ids = {n.node_id for n in initial.nodes}
        assert final.visited == node_ids

    def test_result_length_equals_node_count(self):
        initial, _, final = run(9, 42)
        assert len(final.path) == len(initial.nodes)

    def test_result_visits_each_node_once(self):
        initial, _, final = run(9, 42)
        assert len(set(final.path)) == len(initial.nodes)

    def test_result_is_sorted_ascending(self):
        _, _, final = run(9, 42)
        values = [int(_label(final.nodes, nid)) for nid in final.path]
        assert values == sorted(values), f"Expected sorted but got {values}"

    def test_empty_frontier_at_end(self):
        _, _, final = run(9, 42)
        assert final.frontier == ()

    def test_no_current_at_end(self):
        _, _, final = run(9, 42)
        assert final.current is None

    def test_sorted_for_various_sizes(self):
        for n in [5, 7, 10, 13, 15]:
            _, _, final = run(n, n * 7)
            values = [int(_label(final.nodes, nid)) for nid in final.path]
            assert values == sorted(values), f"n={n}: expected sorted but got {values}"

    def test_different_seeds_give_different_trees(self):
        _, _, final1 = run(9, 1)
        _, _, final2 = run(9, 2)
        vals1 = sorted(n.label for n in final1.nodes)
        vals2 = sorted(n.label for n in final2.nodes)
        assert vals1 != vals2

    def test_frames_have_non_decreasing_path_length(self):
        _, frames, _ = run(7, 42)
        path_lens = [len(f.path) for f in frames]
        for i in range(1, len(path_lens)):
            assert path_lens[i] >= path_lens[i - 1]

    def test_state_serializable(self):
        import json
        initial, frames, final = run(7, 42)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())


class TestInorderEdgeCases:
    def test_min_node_count_clamps(self):
        sim = InorderTraversalSimulation()
        params = SimulationParams(seed=1, inputs={"node_count": 1}, config={})
        initial = sim.initialize(params)
        assert len(initial.nodes) == 5

    def test_max_node_count_clamps(self):
        sim = InorderTraversalSimulation()
        params = SimulationParams(seed=1, inputs={"node_count": 99}, config={})
        initial = sim.initialize(params)
        assert len(initial.nodes) == 15

    def test_missing_node_count_uses_default(self):
        sim = InorderTraversalSimulation()
        params = SimulationParams(seed=42, inputs={}, config={})
        initial = sim.initialize(params)
        assert len(initial.nodes) == 9

    def test_every_frame_has_nodes(self):
        initial, frames, final = run(7, 42)
        for f in [initial] + frames + [final]:
            assert len(f.nodes) > 0

    def test_nodes_have_x_and_y_in_range(self):
        initial, _, _ = run(9, 42)
        for n in initial.nodes:
            assert 0.0 <= n.x <= 1.0, f"x={n.x} out of range"
            assert 0.0 <= n.y <= 1.0, f"y={n.y} out of range"

    def test_edges_are_directed(self):
        initial, _, _ = run(9, 42)
        for e in initial.edges:
            assert e.directed is True

    def test_exactly_one_root(self):
        initial, _, _ = run(9, 42)
        targets = {e.target for e in initial.edges}
        node_ids = {n.node_id for n in initial.nodes}
        roots = node_ids - targets
        assert len(roots) == 1


class TestInorderSorted:
    @pytest.mark.parametrize("seed", range(10))
    def test_always_sorted(self, seed: int):
        _, _, final = run(9, seed + 100)
        values = [int(_label(final.nodes, nid)) for nid in final.path]
        assert values == sorted(values), f"seed={seed}: {values}"
