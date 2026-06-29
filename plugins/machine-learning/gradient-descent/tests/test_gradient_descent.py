"""Tests for Gradient Descent plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "gradient_descent", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
GradientDescentSimulation = _mod.GradientDescentSimulation

from algorithm_atlas_sdk import SimulationParams


def run(lr_x10=2, seed=0):
    sim = GradientDescentSimulation()
    params = SimulationParams(seed=seed, inputs={"learning_rate_x10": lr_x10}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestGradientDescentMetadata:
    def test_slug(self):
        assert GradientDescentSimulation().metadata().slug == "gradient-descent"

    def test_category(self):
        assert GradientDescentSimulation().metadata().category == "machine-learning"


class TestGradientDescentCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_converges_near_minimum(self, seed: int):
        """Final x should be close to the true minimum b."""
        import re
        _, _, final = run(2, seed)
        desc = final.description
        x_val = float(re.search(r"x=([\d.\-]+)", desc).group(1))
        b_val = float(re.search(r"b=([\d.\-]+)", desc).group(1))
        assert abs(x_val - b_val) < 0.5, f"x={x_val} not near minimum b={b_val}"

    def test_has_frames(self):
        _, frames, _ = run(2, 0)
        assert len(frames) > 0

    def test_final_contains_converged(self):
        _, _, final = run(2, 0)
        assert "Converged" in final.description


class TestGradientDescentFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run()
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
