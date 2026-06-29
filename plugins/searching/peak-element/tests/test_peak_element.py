"""Tests for Find Peak Element plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "peak_element",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PeakElementSimulation = _mod.PeakElementSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 8, seed: int = 0):
    sim = PeakElementSimulation()
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


class TestPeakMetadata:
    def test_slug(self):
        assert PeakElementSimulation().metadata().slug == "peak-element"

    def test_category(self):
        assert PeakElementSimulation().metadata().category == "searching"

    def test_visualization_type(self):
        assert PeakElementSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestPeakCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_is_peak(self, seed: int):
        initial, _, final = run(8, seed)
        arr = list(initial.array)
        n = len(arr)
        idx = final.swaps  # swaps field stores found peak index
        assert idx >= 0
        if idx > 0:
            assert arr[idx] >= arr[idx - 1]
        if idx < n - 1:
            assert arr[idx] >= arr[idx + 1]

    def test_has_frames(self):
        _, frames, _ = run(8)
        assert len(frames) > 0


class TestPeakFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(8)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
