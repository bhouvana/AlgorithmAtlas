"""Tests for Longest Palindromic Substring plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "longest_palindromic_substring",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
LongestPalindromicSubstringSimulation = _mod.LongestPalindromicSubstringSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 8, seed: int = 42):
    sim = LongestPalindromicSubstringSimulation()
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


def brute_force_lps(s: str) -> str:
    """Find longest palindromic substring by brute force."""
    n = len(s)
    best = s[0]
    for i in range(n):
        for j in range(i + 1, n + 1):
            sub = s[i:j]
            if sub == sub[::-1] and len(sub) > len(best):
                best = sub
    return best


class TestLPSMetadata:
    def test_slug(self):
        assert LongestPalindromicSubstringSimulation().metadata().slug == "longest-palindromic-substring"

    def test_category(self):
        assert LongestPalindromicSubstringSimulation().metadata().category == "string"

    def test_visualization_type(self):
        assert LongestPalindromicSubstringSimulation().metadata().visualization_type == "MATRIX"


class TestLPSCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_palindrome_length(self, seed: int):
        initial, _, final = run(8, seed=seed)
        s = initial.description.split("'")[1]
        expected = brute_force_lps(s)
        result_str = final.description.split("'")[1]
        assert len(result_str) == len(expected), (
            f"seed={seed}: s='{s}', expected len={len(expected)} ('{expected}'), "
            f"got len={len(result_str)} ('{result_str}')"
        )

    @pytest.mark.parametrize("seed", range(10))
    def test_result_is_palindrome(self, seed: int):
        _, _, final = run(8, seed=seed)
        result_str = final.description.split("'")[1]
        assert result_str == result_str[::-1], f"'{result_str}' is not a palindrome"

    @pytest.mark.parametrize("seed", range(10))
    def test_result_is_substring(self, seed: int):
        initial, _, final = run(8, seed=seed)
        s = initial.description.split("'")[1]
        result_str = final.description.split("'")[1]
        assert result_str in s

    def test_has_frames(self):
        _, frames, _ = run(8)
        assert len(frames) >= 8  # at least n frames for n centers


class TestLPSFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(8)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_table_has_2_rows(self):
        initial, _, _ = run(8)
        assert len(initial.table) == 2
