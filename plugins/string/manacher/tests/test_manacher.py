"""Tests for Manacher's Algorithm plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "manacher",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ManacherSimulation = _mod.ManacherSimulation

from algorithm_atlas_sdk import SimulationParams
from algorithm_atlas_sdk.testing import AlgorithmTestHarness


def run(n: int = 12, seed: int = 42):
    sim = ManacherSimulation()
    params = SimulationParams(seed=seed, inputs={"text_length": n}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


def brute_force_longest_palindrome(s: str) -> int:
    n = len(s)
    best = 1
    for i in range(n):
        for j in range(i + 1, n + 1):
            sub = s[i:j]
            if sub == sub[::-1] and len(sub) > best:
                best = len(sub)
    return best


class TestManacherMetadata:
    def test_slug(self):
        assert ManacherSimulation().metadata().slug == "manacher"

    def test_category(self):
        assert ManacherSimulation().metadata().category == "string"

    def test_visualization_type(self):
        assert ManacherSimulation().metadata().visualization_type == "ARRAY_BARS_SEARCH"


class TestManacherCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_palindrome_length(self, seed: int):
        initial, _, final = run(12, seed=seed)
        text = "".join(chr(c) for c in initial.array)
        expected_len = brute_force_longest_palindrome(text)
        actual_len = int(final.description.split("len=")[1].split(",")[0].rstrip(")"))
        assert actual_len == expected_len, (
            f"seed={seed}: text={text!r}, expected={expected_len}, got={actual_len}"
        )

    @pytest.mark.parametrize("seed", range(5))
    def test_result_is_palindrome(self, seed: int):
        initial, _, final = run(12, seed=seed)
        text = "".join(chr(c) for c in initial.array)
        lo, hi = final.low, final.high
        substr = text[lo:hi + 1]
        assert substr == substr[::-1], (
            f"seed={seed}: text={text!r}, substr={substr!r} is not a palindrome"
        )

    def test_has_frames(self):
        _, frames, _ = run(12)
        assert len(frames) > 0

    def test_found_at_valid(self):
        initial, _, final = run(12)
        n = len(initial.array)
        if final.found_at is not None:
            assert 0 <= final.found_at < n

    def test_best_len_at_least_1(self):
        _, _, final = run(12)
        assert final.target >= 1


class TestManacherFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(12)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_deterministic(self):
        harness = AlgorithmTestHarness(ManacherSimulation())
        params = SimulationParams(seed=42, inputs={"text_length": 12}, config={})
        harness.assert_deterministic(params)

    def test_descriptions_mention_best_len(self):
        _, frames, _ = run(12)
        for f in frames:
            assert "bestLen=" in f.description
