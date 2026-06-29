"""Tests for Maximum Subarray (Kadane's) plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "maximum_subarray",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
MaxSubarraySimulation = _mod.MaxSubarraySimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 10, seed: int = 42):
    sim = MaxSubarraySimulation()
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


def brute_force_max_subarray(arr):
    n = len(arr)
    best = arr[0]
    for i in range(n):
        cur = 0
        for j in range(i, n):
            cur += arr[j]
            if cur > best:
                best = cur
    return best


class TestMaxSubarrayMetadata:
    def test_slug(self):
        assert MaxSubarraySimulation().metadata().slug == "maximum-subarray"

    def test_category(self):
        assert MaxSubarraySimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert MaxSubarraySimulation().metadata().visualization_type == "MATRIX"


class TestMaxSubarrayCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_max_sum(self, seed: int):
        initial, _, final = run(10, seed=seed)
        arr = list(initial.table[0])
        expected = brute_force_max_subarray(arr)
        actual = int(final.description.split("= ")[-1])
        assert actual == expected, (
            f"seed={seed}: arr={arr}, expected={expected}, got={actual}"
        )

    def test_table_has_2_rows(self):
        initial, _, _ = run(10)
        assert len(initial.table) == 2

    def test_dp_row_correct_length(self):
        initial, _, final = run(10)
        assert len(final.table[1]) == len(initial.table[0])

    def test_all_cells_computed(self):
        initial, _, final = run(10)
        n = len(initial.table[0])
        assert len(final.computed_cells) == n

    def test_has_positive_in_array(self):
        """Array must always have at least one positive number."""
        for seed in range(10):
            initial, _, _ = run(10, seed=seed)
            arr = list(initial.table[0])
            assert any(v > 0 for v in arr)


class TestMaxSubarrayFrames:
    def test_has_frames(self):
        _, frames, _ = run(10)
        assert len(frames) > 0

    def test_frame_count_equals_n(self):
        n = 10
        _, frames, _ = run(n)
        assert len(frames) == n

    def test_serializable(self):
        import json
        initial, frames, final = run(10)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_extend_or_restart_in_descriptions(self):
        _, frames, _ = run(10)
        decision_frames = [f for f in frames if "extend" in f.description or "restart" in f.description]
        assert len(decision_frames) >= 1
