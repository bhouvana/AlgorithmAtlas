"""Tests for Edit Distance (Levenshtein) DP plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "edit_distance_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
EditDistanceSimulation = _mod.EditDistanceSimulation

from algorithm_atlas_sdk import SimulationParams


def run(string_length: int = 5, seed: int = 42):
    sim = EditDistanceSimulation()
    params = SimulationParams(seed=seed, inputs={"string_length": string_length}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


def parse_strings(description: str):
    inner = description[10:-2]  # strip EditDist(" prefix and ")
    parts = inner.split('","')
    return parts[0], parts[1]


def naive_edit_distance(s1: str, s2: str) -> int:
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[m][n]


class TestEditDistanceMetadata:
    def test_slug(self):
        assert EditDistanceSimulation().metadata().slug == "edit-distance"

    def test_category(self):
        assert EditDistanceSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert EditDistanceSimulation().metadata().visualization_type == "MATRIX"


class TestEditDistanceTable:
    def test_dimensions(self):
        initial, _, _ = run(5)
        assert len(initial.table) == 6  # m+1
        assert len(initial.table[0]) == 6  # n+1

    def test_base_cases_initialized(self):
        initial, _, _ = run(5)
        # Row 0: dp[0][j] = j
        for j, v in enumerate(initial.table[0]):
            assert v == j
        # Col 0: dp[i][0] = i
        for i, row in enumerate(initial.table):
            assert row[0] == i


class TestEditDistanceCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_matches_naive(self, seed: int):
        initial, _, final = run(5, seed=seed)
        s1, s2 = parse_strings(initial.description)
        expected = naive_edit_distance(s1, s2)
        m, n = len(s1), len(s2)
        assert final.table[m][n] == expected, f"seed={seed}: got {final.table[m][n]}, expected {expected}"

    def test_same_strings_distance_zero(self):
        # When s1 == s2 (unlikely with random but can force via seed matching)
        for seed in range(30):
            initial, _, final = run(5, seed=seed)
            s1, s2 = parse_strings(initial.description)
            expected = naive_edit_distance(s1, s2)
            m, n = len(s1), len(s2)
            assert final.table[m][n] == expected

    def test_non_negative_values(self):
        _, _, final = run(5)
        for row in final.table:
            for v in row:
                assert v >= 0

    def test_symmetric_property(self):
        """edit(s1,s2) == edit(s2,s1) — check against naive."""
        initial, _, final = run(5)
        s1, s2 = parse_strings(initial.description)
        m, n = len(s1), len(s2)
        d12 = final.table[m][n]
        d21 = naive_edit_distance(s2, s1)
        assert d12 == d21


class TestEditDistanceFrames:
    def test_frame_count(self):
        initial, frames, _ = run(5)
        m = len(initial.table) - 1
        n = len(initial.table[0]) - 1
        assert len(frames) == m * n

    def test_no_current_cell_at_end(self):
        _, _, final = run(5)
        assert final.current_cell is None

    def test_all_cells_computed_at_end(self):
        initial, _, final = run(5)
        m = len(initial.table) - 1
        n = len(initial.table[0]) - 1
        assert len(final.computed_cells) == (m + 1) * (n + 1)

    def test_serializable(self):
        import json
        initial, frames, final = run(5)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_clamp_min(self):
        sim = EditDistanceSimulation()
        p = SimulationParams(seed=0, inputs={"string_length": 1}, config={})
        s = sim.initialize(p)
        assert len(s.table) == 5  # min=4 → m+1=5

    def test_clamp_max(self):
        sim = EditDistanceSimulation()
        p = SimulationParams(seed=0, inputs={"string_length": 99}, config={})
        s = sim.initialize(p)
        assert len(s.table) == 9  # max=8 → m+1=9
