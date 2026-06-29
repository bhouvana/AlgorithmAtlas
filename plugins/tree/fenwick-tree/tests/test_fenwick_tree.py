"""Tests for Fenwick Tree plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "fenwick_tree",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
FenwickTreeSimulation = _mod.FenwickTreeSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 8, seed: int = 42):
    sim = FenwickTreeSimulation()
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


class TestFenwickMetadata:
    def test_slug(self):
        assert FenwickTreeSimulation().metadata().slug == "fenwick-tree"

    def test_category(self):
        assert FenwickTreeSimulation().metadata().category == "tree"

    def test_visualization_type(self):
        assert FenwickTreeSimulation().metadata().visualization_type == "MATRIX"


class TestFenwickCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_total_sum_correct(self, seed: int):
        initial, _, final = run(8, seed=seed)
        arr = list(initial.table[0])[1:]  # 1-indexed, skip index 0
        expected_total = sum(arr) + 3  # +3 from the update in steps
        actual_total = int(final.description.split("= ")[1].split(" ")[0])
        assert actual_total == expected_total

    def test_table_has_2_rows(self):
        initial, _, _ = run(8)
        assert len(initial.table) == 2

    def test_has_frames(self):
        _, frames, _ = run(8)
        assert len(frames) > 0

    def test_query_frame_present(self):
        _, frames, _ = run(8)
        query_frames = [f for f in frames if "Query prefix_sum" in f.description]
        assert len(query_frames) == 1

    def test_update_frame_present(self):
        _, frames, _ = run(8)
        update_frames = [f for f in frames if "Update arr[1]" in f.description]
        assert len(update_frames) == 1


class TestFenwickFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(8)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_insert_frames_equal_n(self):
        n = 8
        _, frames, _ = run(n)
        insert_frames = [f for f in frames if f.description.startswith("Insert")]
        assert len(insert_frames) == n
