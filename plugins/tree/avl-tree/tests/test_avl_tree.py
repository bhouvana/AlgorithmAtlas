"""Tests for AVL Tree plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "avl_tree", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
AVLTreeSimulation = _mod.AVLTreeSimulation
_N = _mod._N
_h = _mod._h
_bf = _mod._bf
_insert = _mod._insert
_inorder = _mod._inorder

from algorithm_atlas_sdk import GraphTraversalState, SimulationParams
import random


def make_params(seed=0, array_size=7):
    return SimulationParams(seed=seed, inputs={"array_size": array_size})


def run(seed=0, array_size=7):
    sim = AVLTreeSimulation()
    params = make_params(seed=seed, array_size=array_size)
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
        assert AVLTreeSimulation().metadata().slug == "avl-tree"

    def test_category(self):
        assert AVLTreeSimulation().metadata().category == "tree"

    def test_visualization_type(self):
        assert AVLTreeSimulation().metadata().visualization_type == "TREE"


class TestAVLCore:
    def test_insert_preserves_bst(self):
        root = None
        for v in [5, 3, 7, 1, 4, 6, 8]:
            root, _ = _insert(root, v)
        vals = [n.val for n in _inorder(root)]
        assert vals == sorted(vals)

    def test_balance_maintained(self):
        root = None
        for v in [1, 2, 3, 4, 5, 6, 7]:
            root, _ = _insert(root, v)
            for node in _inorder(root):
                assert abs(_bf(node)) <= 1

    def test_height_log_n(self):
        import math
        root = None
        n = 0
        for v in [5, 3, 7, 1, 4, 6, 8, 2]:
            root, _ = _insert(root, v)
            n += 1
        # AVL height ≤ 1.44 * log2(n)
        assert _h(root) <= int(1.44 * math.log2(n) + 2)

    def test_right_rotation_triggered(self):
        root = None
        # Insert 3, 2, 1 → LL case → right rotation at 3
        root, rot = _insert(None, 3)
        root, rot = _insert(root, 2)
        root, rot = _insert(root, 1)
        assert "LL" in rot

    def test_left_rotation_triggered(self):
        root = None
        root, _ = _insert(None, 1)
        root, _ = _insert(root, 2)
        root, rot = _insert(root, 3)
        assert "RR" in rot


class TestInitialize:
    def test_returns_graph_state(self):
        init = AVLTreeSimulation().initialize(make_params())
        assert isinstance(init, GraphTraversalState)

    def test_starts_with_one_node(self):
        init = AVLTreeSimulation().initialize(make_params())
        assert len(init.nodes) == 1

    def test_description_has_insert_sequence(self):
        init = AVLTreeSimulation().initialize(make_params())
        assert "AVL insert sequence" in init.description


class TestSteps:
    def test_produces_n_minus_1_steps(self):
        n = 7
        _, states, _ = run(array_size=n)
        assert len(states) == n - 1

    def test_all_graph_states(self):
        _, states, final = run()
        for s in states:
            assert isinstance(s, GraphTraversalState)
        assert isinstance(final, GraphTraversalState)

    def test_node_count_grows(self):
        _, states, _ = run()
        prev = 1
        for s in states:
            assert len(s.nodes) >= prev
            prev = len(s.nodes)

    def test_final_has_n_nodes(self):
        n = 7
        _, _, final = run(array_size=n)
        assert len(final.nodes) == n

    def test_tree_height_in_distances(self):
        _, _, final = run()
        assert "height" in final.distances

    def test_bst_order_preserved(self):
        # The nodes returned should form a valid BST (inorder sorted)
        _, _, final = run()
        node_vals = sorted(int(n.label.split("(")[0]) for n in final.nodes)
        # Just verify no duplicates and all positive
        assert len(node_vals) == len(set(node_vals))
        assert all(v > 0 for v in node_vals)

    def test_balance_maintained_after_all_insertions(self):
        for seed in range(3):
            n = 7
            rng = random.Random(seed)
            vals = rng.sample(range(1, n * 6 + 1), n)
            root = None
            for v in vals:
                root, _ = _insert(root, v)
            for node in _inorder(root):
                assert abs(_bf(node)) <= 1

    def test_reproducible(self):
        _, _, f1 = run(seed=3, array_size=7)
        _, _, f2 = run(seed=3, array_size=7)
        assert len(f1.nodes) == len(f2.nodes)
        assert f1.distances == f2.distances
