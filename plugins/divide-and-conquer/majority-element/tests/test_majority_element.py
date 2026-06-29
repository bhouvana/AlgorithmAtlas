"""Tests for Majority Element plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "majority_element",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
MajorityElementSimulation = _mod.MajorityElementSimulation
_make_array = _mod._make_array

from algorithm_atlas_sdk import SimulationParams
import random


def run(n: int = 9, seed: int = 0):
    sim = MajorityElementSimulation()
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


class TestMajorityElementMetadata:
    def test_slug(self):
        assert MajorityElementSimulation().metadata().slug == "majority-element"

    def test_category(self):
        assert MajorityElementSimulation().metadata().category == "divide-and-conquer"

    def test_visualization_type(self):
        assert MajorityElementSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestMajorityElementCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_majority(self, seed: int):
        initial, _, final = run(9, seed)
        arr = list(initial.array)
        n = len(arr)
        # Find true majority
        counts = {}
        for v in arr:
            counts[v] = counts.get(v, 0) + 1
        true_majority = max(counts, key=lambda k: counts[k])
        result = int(final.description.split("Majority element = ")[1].split(" ")[0])
        assert result == true_majority, f"seed={seed}: arr={arr}, expected {true_majority}, got {result}"

    def test_has_frames(self):
        _, frames, _ = run(9)
        assert len(frames) == 8  # n-1 frames

    @pytest.mark.parametrize("seed", range(10))
    def test_majority_appears_more_than_half(self, seed: int):
        initial, _, final = run(9, seed)
        count = int(final.description.split("appears ")[1].split(" ")[0])
        n = len(initial.array)
        assert count > n // 2


class TestMajorityElementFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(9)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
