"""Tests for Perceptron plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "perceptron", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PerceptronSimulation = _mod.PerceptronSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n=10, seed=0):
    sim = PerceptronSimulation()
    params = SimulationParams(seed=seed, inputs={"sample_count": n}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestPerceptronMetadata:
    def test_slug(self):
        assert PerceptronSimulation().metadata().slug == "perceptron"

    def test_category(self):
        assert PerceptronSimulation().metadata().category == "machine-learning"


class TestPerceptronCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_converges(self, seed: int):
        _, _, final = run(10, seed)
        assert "Converged" in final.description

    def test_has_frames(self):
        _, frames, _ = run(10)
        assert len(frames) > 0

    def test_frame_descriptions_have_prediction(self):
        _, frames, _ = run(10)
        for f in frames[:3]:
            assert "pred" in f.description


class TestPerceptronFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run()
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
