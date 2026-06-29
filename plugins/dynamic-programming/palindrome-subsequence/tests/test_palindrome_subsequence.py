"""Tests for Longest Palindromic Subsequence plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "palindrome_subsequence",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PalindromeSubsequenceSimulation = _mod.PalindromeSubsequenceSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 6, seed: int = 42):
    sim = PalindromeSubsequenceSimulation()
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


def brute_force_lps(s: str) -> int:
    """O(2^n) brute-force via LCS with reverse."""
    t = s[::-1]
    n, m = len(s), len(t)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]


class TestPalindromeMetadata:
    def test_slug(self):
        assert PalindromeSubsequenceSimulation().metadata().slug == "palindrome-subsequence"

    def test_category(self):
        assert PalindromeSubsequenceSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert PalindromeSubsequenceSimulation().metadata().visualization_type == "MATRIX"


class TestPalindromeCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_lps(self, seed: int):
        initial, _, final = run(6, seed=seed)
        s = initial.description.split("'")[1]
        expected = brute_force_lps(s)
        actual = int(final.description.split("= ")[1])
        assert actual == expected, f"seed={seed}: s='{s}', expected={expected}, got={actual}"

    def test_table_is_nxn(self):
        initial, _, _ = run(6)
        n = len(initial.table)
        for row in initial.table:
            assert len(row) == n

    def test_diagonal_initialized_to_1(self):
        initial, _, _ = run(6)
        for i in range(len(initial.table)):
            assert initial.table[i][i] == 1

    def test_result_geq_1(self):
        _, _, final = run(6)
        assert int(final.description.split("= ")[1]) >= 1

    @pytest.mark.parametrize("seed", range(5))
    def test_lps_leq_string_length(self, seed: int):
        initial, _, final = run(6, seed=seed)
        s = initial.description.split("'")[1]
        lps = int(final.description.split("= ")[1])
        assert lps <= len(s)


class TestPalindromeFrames:
    def test_has_frames(self):
        _, frames, _ = run(6)
        assert len(frames) > 0

    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_frame_count(self):
        n = 6
        _, frames, _ = run(n)
        # n*(n+1)/2 - n base cells = n*(n-1)/2 frames
        assert len(frames) == n * (n - 1) // 2
