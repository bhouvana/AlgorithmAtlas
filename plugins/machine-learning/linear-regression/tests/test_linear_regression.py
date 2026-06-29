"""Tests for Linear Regression plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "linear_regression", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
LinearRegressionSimulation = _mod.LinearRegressionSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n=10, seed=0):
    sim = LinearRegressionSimulation()
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


class TestLinearRegressionMetadata:
    def test_slug(self):
        assert LinearRegressionSimulation().metadata().slug == "linear-regression"

    def test_category(self):
        assert LinearRegressionSimulation().metadata().category == "machine-learning"


class TestLinearRegressionCorrectness:
    @pytest.mark.parametrize("seed", range(6))
    def test_produces_frames(self, seed: int):
        _, frames, _ = run(10, seed)
        assert len(frames) == _mod.MAX_ITERS

    def test_final_contains_fitted(self):
        _, _, final = run(10)
        assert "Fitted" in final.description

    def test_w_close_to_true(self):
        import re
        _, _, final = run(10, 0)
        w_fit = float(re.search(r"w=([\d.\-]+)", final.description).group(1))
        true_w = float(re.search(r"true w=([\d.\-]+)", final.description).group(1))
        assert abs(w_fit - true_w) < 1.0


class TestLinearRegressionFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run()
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
