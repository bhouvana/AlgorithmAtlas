"""Tests for Lowest Common Ancestor plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "lca",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
LCASimulation = _mod.LCASimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 7, seed: int = 42):
    sim = LCASimulation()
    params = SimulationParams(seed=seed, inputs={"array_size": n}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


def is_ancestor(children, ancestor, node) -> bool:
    """Check if ancestor is on the path from node to root using DFS from ancestor."""
    visited = set()
    stack = [ancestor]
    while stack:
        cur = stack.pop()
        if cur == node:
            return True
        if cur in visited:
            continue
        visited.add(cur)
        for child in children.get(cur, []):
            stack.append(child)
    return False


class TestLCAMetadata:
    def test_slug(self):
        assert LCASimulation().metadata().slug == "lca"

    def test_category(self):
        assert LCASimulation().metadata().category == "tree"

    def test_visualization_type(self):
        assert LCASimulation().metadata().visualization_type == "TREE"


class TestLCACorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_lca_is_ancestor_of_both(self, seed: int):
        initial, _, final = run(7, seed=seed)
        lca_val = int(final.distances["lca_value"])
        lca_node = next(n for n in initial.nodes if int(n.label) == lca_val)

        # Build children map from edges
        children = {n.node_id: [] for n in initial.nodes}
        for e in initial.edges:
            children[e.source].append(e.target)

        p = initial.frontier[1]
        q = initial.frontier[2]
        assert is_ancestor(children, lca_node.node_id, p), f"LCA not ancestor of p"
        assert is_ancestor(children, lca_node.node_id, q), f"LCA not ancestor of q"

    def test_has_frames(self):
        _, frames, _ = run(7)
        assert len(frames) > 0

    def test_all_nodes_visited(self):
        initial, _, final = run(7)
        assert len(final.visited) == len(initial.nodes)

    def test_lca_in_description(self):
        _, _, final = run(7)
        assert "LCA" in final.description


class TestLCAFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(7)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
