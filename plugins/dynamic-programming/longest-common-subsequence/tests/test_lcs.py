"""Tests for Longest Common Subsequence DP plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "lcs_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
LCSSimulation = _mod.LCSSimulation

from algorithm_atlas_sdk import SimulationParams


def run(string_length: int = 6, seed: int = 42):
    sim = LCSSimulation()
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


def naive_lcs(s1: str, s2: str) -> int:
    """Reference implementation."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


def parse_strings(description: str):
    """Extract s1 and s2 from LCS("S1", "S2") description."""
    inner = description[5:-2]  # strip 'LCS("' prefix and '")' suffix
    parts = inner.split('", "')
    return parts[0], parts[1]


class TestLCSMetadata:
    def test_slug(self):
        assert LCSSimulation().metadata().slug == "longest-common-subsequence"

    def test_category(self):
        assert LCSSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert LCSSimulation().metadata().visualization_type == "MATRIX"


class TestLCSTableShape:
    def test_table_dimensions(self):
        initial, _, _ = run(6)
        # (m+1) rows × (n+1) cols; strings are length 6 by default
        rows = len(initial.table)
        cols = len(initial.table[0])
        assert rows == 7  # m+1
        assert cols == 7  # n+1

    def test_all_zeros_initially(self):
        initial, _, _ = run(6)
        for row in initial.table:
            for cell in row:
                assert cell == 0

    @pytest.mark.parametrize("length", [4, 5, 7, 10])
    def test_table_size_matches_input(self, length: int):
        initial, _, _ = run(length)
        assert len(initial.table) == length + 1
        assert len(initial.table[0]) == length + 1


class TestLCSCorrectness:
    def test_final_value_matches_naive(self):
        for seed in range(10):
            initial, _, final = run(6, seed=seed)
            s1, s2 = parse_strings(initial.description)
            expected = naive_lcs(s1, s2)
            m, n = len(s1), len(s2)
            assert final.table[m][n] == expected, (
                f"seed={seed} s1={s1} s2={s2}: got {final.table[m][n]}, expected {expected}"
            )

    def test_known_case_same_strings(self):
        # If s1 == s2, LCS length == len(s1)
        # We can't force this without mocking, so verify invariant:
        # LCS length <= min(len(s1), len(s2))
        for seed in range(20):
            initial, _, final = run(6, seed=seed)
            s1, s2 = parse_strings(initial.description)
            m, n = len(s1), len(s2)
            assert 0 <= final.table[m][n] <= min(m, n)

    def test_base_row_is_zero(self):
        _, _, final = run(6)
        assert all(final.table[0][j] == 0 for j in range(len(final.table[0])))

    def test_base_col_is_zero(self):
        _, _, final = run(6)
        assert all(final.table[i][0] == 0 for i in range(len(final.table)))

    def test_monotone_rows(self):
        """dp[i][j] >= dp[i][j-1] — adding more chars can only help."""
        _, _, final = run(8, seed=7)
        for row in final.table:
            for j in range(1, len(row)):
                assert row[j] >= row[j - 1]

    def test_monotone_cols(self):
        """dp[i][j] >= dp[i-1][j]."""
        _, _, final = run(8, seed=7)
        for i in range(1, len(final.table)):
            for j in range(len(final.table[0])):
                assert final.table[i][j] >= final.table[i - 1][j]


class TestLCSFrames:
    def test_frame_count(self):
        # Expect: 1 base-case frame + m*n fill frames
        initial, frames, _ = run(6)
        m = len(initial.table) - 1
        n = len(initial.table[0]) - 1
        assert len(frames) == 1 + m * n  # base frame + one per (i,j) cell

    def test_all_cells_computed_at_end(self):
        initial, _, final = run(6)
        m = len(initial.table) - 1
        n = len(initial.table[0]) - 1
        expected_cells = (m + 1) * (n + 1)
        assert len(final.computed_cells) == expected_cells

    def test_no_current_cell_at_end(self):
        _, _, final = run(6)
        assert final.current_cell is None

    def test_current_cell_advances(self):
        _, frames, _ = run(5)
        fill_frames = frames[1:]  # skip base-case frame
        prev = None
        for f in fill_frames:
            if f.current_cell is not None:
                if prev is not None:
                    # Should fill row-by-row, col-by-col
                    r, c = f.current_cell
                    pr, pc = prev
                    assert (r, c) > (pr, pc)
                prev = f.current_cell

    def test_serializable(self):
        import json
        initial, frames, final = run(5)
        for state in [initial, frames[0], frames[-1], final]:
            json.dumps(state.to_dict())

    def test_clamp_min(self):
        sim = LCSSimulation()
        p = SimulationParams(seed=0, inputs={"string_length": 1}, config={})
        s = sim.initialize(p)
        assert len(s.table) == 5  # min=4 → m+1=5

    def test_clamp_max(self):
        sim = LCSSimulation()
        p = SimulationParams(seed=0, inputs={"string_length": 99}, config={})
        s = sim.initialize(p)
        assert len(s.table) == 11  # max=10 → m+1=11
