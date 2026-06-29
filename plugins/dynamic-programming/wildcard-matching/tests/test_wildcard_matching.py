"""Tests for Wildcard Pattern Matching plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "wildcard_matching",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
WildcardMatchingSimulation = _mod.WildcardMatchingSimulation
_INSTANCES = _mod._INSTANCES
_match = _mod._match

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = WildcardMatchingSimulation()
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


class TestWildcardMetadata:
    def test_slug(self):
        assert WildcardMatchingSimulation().metadata().slug == "wildcard-matching"

    def test_category(self):
        assert WildcardMatchingSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert WildcardMatchingSimulation().metadata().visualization_type == "MATRIX"


class TestWildcardCorrectness:
    @pytest.mark.parametrize("seed", range(len(_INSTANCES)))
    def test_correct_match(self, seed: int):
        s, p, expected = _INSTANCES[seed]
        _, _, final = run(seed)
        result_str = final.description.split(": ")[1]
        result = result_str == "True"
        assert result == expected, f"seed={seed}: '{s}' vs '{p}' expected {expected}, got {result}"

    def test_has_frames(self):
        _, frames, _ = run(3)
        assert len(frames) > 0


class TestWildcardFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
