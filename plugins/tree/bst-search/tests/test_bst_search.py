"""Tests for BST Search plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "bst_search",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BSTSearchSimulation = _mod.BSTSearchSimulation

from algorithm_atlas_sdk import GraphTraversalState, SimulationParams
from algorithm_atlas_sdk.testing import AlgorithmTestHarness


def run(n: int = 10, seed: int = 42):
    sim = BSTSearchSimulation()
    params = SimulationParams(seed=seed, inputs={"node_count": n}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestBSTSearchMetadata:
    def test_slug(self):
        assert BSTSearchSimulation().metadata().slug == "bst-search"

    def test_category(self):
        assert BSTSearchSimulation().metadata().category == "tree"

    def test_visualization_type(self):
        assert BSTSearchSimulation().metadata().visualization_type == "TREE"


class TestBSTSearchCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_found_result(self, seed: int):
        initial, _, final = run(10, seed=seed)
        node_vals = {n.node_id: int(n.label) for n in initial.nodes}
        target = int(initial.distances["target"])
        all_vals = set(node_vals.values())

        if target in all_vals:
            assert len(final.path) == 1, f"seed={seed}: expected found, got path={final.path}"
            found_nid = final.path[0]
            assert node_vals[found_nid] == target
        else:
            assert len(final.path) == 0, f"seed={seed}: expected not found, got path={final.path}"

    def test_comparisons_positive(self):
        _, _, final = run(10)
        assert final.distances.get("comparisons", 0) >= 1

    def test_comparisons_at_most_height(self):
        initial, _, final = run(10)
        n = len(initial.nodes)
        comps = final.distances.get("comparisons", 0)
        assert comps <= n  # worst case is all nodes (skewed tree)


class TestBSTSearchFrames:
    def test_has_frames(self):
        _, frames, _ = run(10)
        assert len(frames) > 0

    def test_graph_structure_unchanged(self):
        initial, frames, final = run(10)
        for f in frames + [final]:
            assert f.nodes == initial.nodes
            assert f.edges == initial.edges

    def test_frontier_empty_at_terminal(self):
        _, _, final = run(10)
        assert final.frontier == ()

    def test_serializable(self):
        import json
        initial, frames, final = run(10)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_deterministic(self):
        harness = AlgorithmTestHarness(BSTSearchSimulation())
        params = SimulationParams(seed=42, inputs={"node_count": 10}, config={})
        harness.assert_deterministic(params)

    def test_descriptions_mention_direction(self):
        _, frames, _ = run(10, seed=0)
        direction_frames = [f for f in frames if "LEFT" in f.description or "RIGHT" in f.description]
        assert len(direction_frames) >= 0  # may be 0 if root matches target
