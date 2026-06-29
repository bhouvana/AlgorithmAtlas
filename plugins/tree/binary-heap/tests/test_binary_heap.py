"""Tests for Binary Heap Operations plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "binary_heap",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BinaryHeapSimulation = _mod.BinaryHeapSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 7, seed: int = 0):
    sim = BinaryHeapSimulation()
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


class TestBinaryHeapMetadata:
    def test_slug(self):
        assert BinaryHeapSimulation().metadata().slug == "binary-heap"

    def test_category(self):
        assert BinaryHeapSimulation().metadata().category == "tree"

    def test_visualization_type(self):
        assert BinaryHeapSimulation().metadata().visualization_type == "TREE"


class TestBinaryHeapCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_min_heap_property(self, seed: int):
        """Final state must satisfy min-heap property."""
        _, _, final = run(7, seed)
        nodes = {n.node_id: int(n.label) for n in final.nodes}
        edges = final.edges
        for edge in edges:
            parent_val = nodes[edge.source]
            child_val = nodes[edge.target]
            assert parent_val <= child_val, (
                f"Min-heap violated: parent {edge.source}={parent_val} > child {edge.target}={child_val}"
            )

    @pytest.mark.parametrize("seed", range(5))
    def test_all_values_present(self, seed: int):
        """All inserted values must appear in final heap."""
        initial, _, final = run(7, seed)
        desc = initial.description
        vals_str = desc.split("[")[1].rstrip("]")
        input_vals = sorted(map(int, vals_str.split(", ")))
        heap_vals = sorted(int(n.label) for n in final.nodes)
        assert input_vals == heap_vals

    def test_final_description_contains_min(self):
        _, _, final = run(7, 0)
        assert "min=" in final.description

    def test_has_frames(self):
        _, frames, _ = run(7)
        assert len(frames) > 0

    def test_root_is_minimum(self):
        """Root node (index 0) must have the smallest value."""
        _, _, final = run(7, 42)
        nodes = {n.node_id: int(n.label) for n in final.nodes}
        min_val = min(nodes.values())
        assert nodes["0"] == min_val


class TestBinaryHeapFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(7)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_node_count_matches_size(self):
        _, _, final = run(7, 1)
        size = int(final.distances["size"])
        assert len(final.nodes) == size
