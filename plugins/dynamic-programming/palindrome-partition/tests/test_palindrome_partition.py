"""Tests for Palindrome Partitioning plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "palindrome_partition",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PalindromePartitionSimulation = _mod.PalindromePartitionSimulation
_min_cuts = _mod._min_cuts

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 6, seed: int = 0):
    sim = PalindromePartitionSimulation()
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


class TestPalindromePartitionMetadata:
    def test_slug(self):
        assert PalindromePartitionSimulation().metadata().slug == "palindrome-partition"

    def test_category(self):
        assert PalindromePartitionSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert PalindromePartitionSimulation().metadata().visualization_type == "MATRIX"


class TestPalindromePartitionCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_min_cuts(self, seed: int):
        initial, _, final = run(6, seed)
        s = initial.description.split("'")[1]
        expected = _min_cuts(s)
        result = int(final.description.split("= ")[1])
        assert result == expected, f"seed={seed}: '{s}' expected {expected}, got {result}"

    def test_has_n_minus_1_frames(self):
        initial, frames, _ = run(6)
        n = len(initial.description.split("'")[1])
        assert len(frames) == n - 1


class TestPalindromePartitionFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_known_cases(self):
        assert _min_cuts("a") == 0
        assert _min_cuts("aa") == 0
        assert _min_cuts("aab") == 1
        assert _min_cuts("abcba") == 0
        assert _min_cuts("abcd") == 3
