"""Tests for Search in Rotated Sorted Array plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "rotated_binary_search",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
RotatedBinarySearchSimulation = _mod.RotatedBinarySearchSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 10, seed: int = 0):
    sim = RotatedBinarySearchSimulation()
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


class TestRotatedBinarySearchMetadata:
    def test_slug(self):
        assert RotatedBinarySearchSimulation().metadata().slug == "rotated-binary-search"

    def test_category(self):
        assert RotatedBinarySearchSimulation().metadata().category == "searching"

    def test_visualization_type(self):
        assert RotatedBinarySearchSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestRotatedBinarySearchCorrectness:
    @pytest.mark.parametrize("seed", range(20))
    def test_result_correct(self, seed: int):
        """If target is in array, swaps=found_idx; otherwise swaps=-1."""
        initial, _, final = run(10, seed)
        arr = list(initial.array)
        target = initial.swaps
        idx = final.swaps
        if idx >= 0:
            assert arr[idx] == target, f"arr[{idx}]={arr[idx]} != target={target}"
        else:
            assert target not in arr, f"target={target} should be in arr but swaps=-1"

    def test_found_target_in_sorted_indices(self):
        """When found, the index appears in sorted_indices."""
        for seed in range(10):
            initial, _, final = run(10, seed)
            arr = list(initial.array)
            target = initial.swaps
            if target in arr:
                assert final.swaps >= 0
                assert final.swaps in final.sorted_indices

    def test_has_frames(self):
        _, frames, _ = run(10)
        assert len(frames) > 0

    def test_comparisons_log_bound(self):
        """Number of comparisons must be ≤ log2(n)+2."""
        import math
        for seed in range(10):
            _, frames, final = run(10, seed)
            assert final.comparisons <= math.log2(10) + 2


class TestRotatedBinarySearchFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(10)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
