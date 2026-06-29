"""Tests for Segment Tree plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "segment_tree",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
SegmentTreeSimulation = _mod.SegmentTreeSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 6, seed: int = 42):
    sim = SegmentTreeSimulation()
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


class TestSegmentTreeMetadata:
    def test_slug(self):
        assert SegmentTreeSimulation().metadata().slug == "segment-tree"

    def test_category(self):
        assert SegmentTreeSimulation().metadata().category == "tree"

    def test_visualization_type(self):
        assert SegmentTreeSimulation().metadata().visualization_type == "MATRIX"


class TestSegmentTreeCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_root_equals_total_sum(self, seed: int):
        """tree[1] should equal sum(arr) after build and one update."""
        initial, _, final = run(6, seed=seed)
        # After the update, arr[0] has +5 added
        arr = list(initial.table[0])
        arr[0] += 5  # the update always does arr[0] += 5
        expected_total = sum(arr)
        actual_total = int(final.description.split("= ")[-1])
        assert actual_total == expected_total

    def test_table_has_2_rows(self):
        initial, _, _ = run(6)
        assert len(initial.table) == 2

    def test_has_frames(self):
        _, frames, _ = run(6)
        assert len(frames) > 0

    def test_leaf_assignment_frames(self):
        _, frames, _ = run(6)
        leaf_frames = [f for f in frames if f.description.startswith("Leaf")]
        assert len(leaf_frames) == 6  # one per array element

    def test_query_frame_present(self):
        _, frames, _ = run(6)
        query_frames = [f for f in frames if "Query sum" in f.description]
        assert len(query_frames) == 1


class TestSegmentTreeFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_propagate_frames_present(self):
        _, frames, _ = run(6)
        prop_frames = [f for f in frames if "Propagate" in f.description]
        assert len(prop_frames) >= 1
