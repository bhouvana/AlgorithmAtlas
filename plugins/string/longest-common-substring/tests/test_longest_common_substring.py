"""Tests for Longest Common Substring plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "longest_common_substring",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
LongestCommonSubstringSimulation = _mod.LongestCommonSubstringSimulation
_lcs_dp = _mod._lcs_dp

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 6, seed: int = 0):
    sim = LongestCommonSubstringSimulation()
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


class TestLCSMetadata:
    def test_slug(self):
        assert LongestCommonSubstringSimulation().metadata().slug == "longest-common-substring"

    def test_category(self):
        assert LongestCommonSubstringSimulation().metadata().category == "string"

    def test_visualization_type(self):
        assert LongestCommonSubstringSimulation().metadata().visualization_type == "MATRIX"


class TestLCSCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_length(self, seed: int):
        initial, _, final = run(6, seed)
        desc = initial.description
        parts = desc.split("'")
        s1, s2 = parts[1], parts[3]
        expected, _ = _lcs_dp(s1, s2)
        result = int(final.description.split("= ")[1])
        assert result == expected

    def test_has_frames(self):
        _, frames, _ = run(6)
        assert len(frames) > 0


class TestLCSFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
