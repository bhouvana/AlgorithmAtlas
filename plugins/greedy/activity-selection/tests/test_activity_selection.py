"""Tests for Activity Selection plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "activity_selection",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ActivitySelectionSimulation = _mod.ActivitySelectionSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 8, seed: int = 42):
    sim = ActivitySelectionSimulation()
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


class TestActivitySelectionMetadata:
    def test_slug(self):
        assert ActivitySelectionSimulation().metadata().slug == "activity-selection"

    def test_category(self):
        assert ActivitySelectionSimulation().metadata().category == "greedy"

    def test_visualization_type(self):
        assert ActivitySelectionSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestActivitySelectionInitialize:
    def test_array_size(self):
        initial, _, _ = run(8)
        assert len(initial.array) == 8

    def test_array_sorted_finish_times(self):
        initial, _, _ = run(8)
        arr = list(initial.array)
        assert arr == sorted(arr), "Finish times should be sorted"

    def test_description_has_starts(self):
        initial, _, _ = run(8)
        assert "starts=" in initial.description


class TestActivitySelectionCorrectness:
    def test_at_least_one_selected(self):
        _, _, final = run(8)
        assert len(final.sorted_indices) >= 1

    def test_selected_at_most_n(self):
        _, _, final = run(8)
        assert len(final.sorted_indices) <= 8

    def test_no_overlaps_in_selection(self):
        initial, _, final = run(8)
        finish_times = list(initial.array)
        starts_str = initial.description.split("starts=")[1]
        start_times = [int(x) for x in starts_str.split(",")]
        activities = list(zip(start_times, finish_times))

        selected_indices = sorted(final.sorted_indices)
        for i in range(len(selected_indices) - 1):
            a_idx = selected_indices[i]
            b_idx = selected_indices[i + 1]
            a_finish = activities[a_idx][1]
            b_start = activities[b_idx][0]
            assert b_start >= a_finish, f"Overlap between activities {a_idx} and {b_idx}"

    @pytest.mark.parametrize("seed", range(10))
    def test_consistent_selection(self, seed: int):
        initial, _, final = run(8, seed=seed)
        assert len(final.sorted_indices) >= 1

    def test_comparisons_equals_n_minus_1(self):
        _, _, final = run(8)
        assert final.comparisons == 7  # check all n-1 remaining activities

    def test_done_message(self):
        _, _, final = run(8)
        assert "Done" in final.description or "selected" in final.description.lower()


class TestActivitySelectionFrames:
    def test_has_frames(self):
        _, frames, _ = run(8)
        assert len(frames) > 0

    def test_serializable(self):
        import json
        initial, frames, final = run(8)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_selected_count_monotonically_increasing(self):
        _, frames, final = run(8)
        select_frames = [f for f in frames if f.last_swap is not None]
        counts = [len(f.sorted_indices) for f in select_frames]
        for i in range(1, len(counts)):
            assert counts[i] >= counts[i - 1]
