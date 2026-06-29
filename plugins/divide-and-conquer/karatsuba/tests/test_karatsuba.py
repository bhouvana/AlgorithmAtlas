"""Tests for Karatsuba Multiplication plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "karatsuba",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
KaratsubaSimulation = _mod.KaratsubaSimulation
_PAIRS = _mod._PAIRS

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = KaratsubaSimulation()
    params = SimulationParams(seed=seed, inputs={}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestKaratsubaMetadata:
    def test_slug(self):
        assert KaratsubaSimulation().metadata().slug == "karatsuba"

    def test_category(self):
        assert KaratsubaSimulation().metadata().category == "divide-and-conquer"

    def test_visualization_type(self):
        assert KaratsubaSimulation().metadata().visualization_type == "MATRIX"


class TestKaratsubaCorrectness:
    @pytest.mark.parametrize("seed", range(len(_PAIRS)))
    def test_correct_product(self, seed: int):
        x, y = _PAIRS[seed]
        _, _, final = run(seed)
        result = int(final.description.split("= ")[1])
        assert result == x * y, f"seed={seed}: {x}×{y} expected {x*y}, got {result}"

    def test_has_frames(self):
        _, frames, _ = run(0)
        assert len(frames) > 0


class TestKaratsubaFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
