"""Tests for Interleaving Strings plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "interleaving_strings",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
InterleavingStringsSimulation = _mod.InterleavingStringsSimulation
_INSTANCES = _mod._INSTANCES
_is_interleaving = _mod._is_interleaving

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = InterleavingStringsSimulation()
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


class TestInterleavingMetadata:
    def test_slug(self):
        assert InterleavingStringsSimulation().metadata().slug == "interleaving-strings"

    def test_category(self):
        assert InterleavingStringsSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert InterleavingStringsSimulation().metadata().visualization_type == "MATRIX"


class TestInterleavingCorrectness:
    @pytest.mark.parametrize("seed", range(len(_INSTANCES)))
    def test_correct_result(self, seed: int):
        s1, s2, s3, expected = _INSTANCES[seed]
        _, _, final = run(seed)
        result = final.description.split(": ")[1] == "True"
        assert result == expected, f"seed={seed}: '{s1}' '{s2}' '{s3}' expected {expected}"

    def test_has_frames(self):
        _, frames, _ = run(0)
        assert len(frames) > 0


class TestInterleavingFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
