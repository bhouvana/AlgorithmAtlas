"""Tests for Two Sum plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "two_sum",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
TwoSumSimulation = _mod.TwoSumSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 8, seed: int = 0):
    sim = TwoSumSimulation()
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


class TestTwoSumMetadata:
    def test_slug(self):
        assert TwoSumSimulation().metadata().slug == "two-sum"

    def test_category(self):
        assert TwoSumSimulation().metadata().category == "searching"

    def test_visualization_type(self):
        assert TwoSumSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestTwoSumCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_sum(self, seed: int):
        initial, _, final = run(8, seed)
        target = int(initial.description.split("target=")[1])
        arr = list(initial.array)
        desc = final.description
        if "indices" in desc:
            parts = desc.split("indices ")[1].split(",")
            i, j = int(parts[0]), int(parts[1])
            assert arr[i] + arr[j] == target

    def test_has_frames(self):
        _, frames, _ = run(8)
        assert len(frames) > 0


class TestTwoSumFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(8)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
