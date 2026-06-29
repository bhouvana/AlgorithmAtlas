"""Tests for Subset Sum DP plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "subset_sum",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
SubsetSumSimulation = _mod.SubsetSumSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 5, seed: int = 42):
    sim = SubsetSumSimulation()
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


def brute_force_subset_sum(arr, target):
    n = len(arr)
    for mask in range(1 << n):
        total = sum(arr[i] for i in range(n) if mask & (1 << i))
        if total == target:
            return True
    return False


class TestSubsetSumMetadata:
    def test_slug(self):
        assert SubsetSumSimulation().metadata().slug == "subset-sum"

    def test_category(self):
        assert SubsetSumSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert SubsetSumSimulation().metadata().visualization_type == "MATRIX"


class TestSubsetSumCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_answer(self, seed: int):
        initial, _, final = run(5, seed=seed)
        desc = initial.description
        nums_str = desc[desc.index("[") + 1 : desc.index("]")]
        arr = [int(x) for x in nums_str.split(",")]
        target = int(desc.split("target=")[1])

        expected = brute_force_subset_sum(arr, target)
        actual_exists = "EXISTS" in final.description
        assert actual_exists == expected, (
            f"seed={seed}: arr={arr}, target={target}, expected={expected}, "
            f"final desc={final.description}"
        )

    def test_table_shape(self):
        initial, _, final = run(5)
        n_rows = len(final.table)
        assert n_rows >= 2
        for row in final.table:
            assert len(row) == len(final.table[0])

    def test_base_row_has_1_at_col0(self):
        initial, _, final = run(5)
        assert final.table[0][0] == 1

    def test_base_row_zeros_elsewhere(self):
        initial, _, _ = run(5)
        assert all(initial.table[0][j] == 0 for j in range(1, len(initial.table[0])))

    def test_dp_values_are_0_or_1(self):
        _, _, final = run(5)
        for row in final.table:
            for val in row:
                assert val in (0, 1)

    def test_all_cells_computed(self):
        initial, _, final = run(5)
        n = len(initial.table) - 1
        W = len(initial.table[0]) - 1
        assert len(final.computed_cells) == (n + 1) * (W + 1)

    def test_target_leq_sum(self):
        for seed in range(5):
            initial, _, _ = run(5, seed=seed)
            desc = initial.description
            nums_str = desc[desc.index("[") + 1 : desc.index("]")]
            arr = [int(x) for x in nums_str.split(",")]
            target = int(desc.split("target=")[1])
            assert target <= sum(arr)


class TestSubsetSumFrames:
    def test_has_frames(self):
        _, frames, _ = run(5)
        assert len(frames) > 0

    def test_serializable(self):
        import json
        initial, frames, final = run(5)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_current_cell_tracks_progress(self):
        _, frames, _ = run(5)
        for f in frames:
            assert f.current_cell is not None
