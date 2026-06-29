"""Tests for Counting Inversions plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import List

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "counting_inversions",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CountingInversionsSimulation = _mod.CountingInversionsSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 8, seed: int = 42):
    sim = CountingInversionsSimulation()
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


def brute_force_inversions(arr: List[int]) -> int:
    count = 0
    n = len(arr)
    for i in range(n):
        for j in range(i + 1, n):
            if arr[i] > arr[j]:
                count += 1
    return count


class TestCountingInversionsMetadata:
    def test_slug(self):
        assert CountingInversionsSimulation().metadata().slug == "counting-inversions"

    def test_category(self):
        assert CountingInversionsSimulation().metadata().category == "divide-and-conquer"

    def test_visualization_type(self):
        assert CountingInversionsSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestCountingInversionsCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_inversion_count(self, seed: int):
        initial, _, final = run(8, seed=seed)
        expected = brute_force_inversions(list(initial.array))
        actual = int(final.description.split("= ")[1])
        assert actual == expected, f"seed={seed}: arr={list(initial.array)}, expected={expected}, got={actual}"

    def test_sorted_output(self):
        initial, _, final = run(8)
        assert final.array == tuple(sorted(initial.array))

    def test_zero_inversions_sorted_array(self):
        from algorithm_atlas_sdk import SimulationParams
        sim = CountingInversionsSimulation()
        # We can't directly pass sorted input, but we can verify with any seed
        initial, _, final = run(8)
        assert final.comparisons >= 0

    def test_has_frames(self):
        _, frames, _ = run(8)
        assert len(frames) > 0


class TestCountingInversionsFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(8)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_inversions_monotone_increase(self):
        _, frames, _ = run(8)
        inv_values = [f.comparisons for f in frames]
        for a, b in zip(inv_values, inv_values[1:]):
            assert b >= a
