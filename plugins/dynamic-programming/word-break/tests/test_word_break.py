"""Tests for Word Break plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "word_break",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
WordBreakSimulation = _mod.WordBreakSimulation

from algorithm_atlas_sdk import SimulationParams

_STRINGS = ["leetcode", "applepenapple", "catsanddog", "pineapple", "ilikesamsung"]


def run(seed: int = 0):
    sim = WordBreakSimulation()
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


class TestWordBreakMetadata:
    def test_slug(self):
        assert WordBreakSimulation().metadata().slug == "word-break"

    def test_category(self):
        assert WordBreakSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert WordBreakSimulation().metadata().visualization_type == "MATRIX"


class TestWordBreakCorrectness:
    def test_leetcode_can_be_segmented(self):
        # seed 0 → "leetcode" (leet + code)
        _, _, final = run(0)
        assert "CAN" in final.description

    def test_table_has_2_rows(self):
        initial, _, _ = run(0)
        assert len(initial.table) == 2

    def test_dp_row_starts_with_1(self):
        initial, _, _ = run(0)
        dp = list(initial.table[1])
        assert dp[0] == 1  # empty prefix always True

    def test_has_frames(self):
        _, frames, _ = run(0)
        assert len(frames) > 0

    @pytest.mark.parametrize("seed", range(5))
    def test_final_is_definitive(self, seed: int):
        _, _, final = run(seed)
        assert "CAN" in final.description or "CANNOT" in final.description

    def test_dp_values_are_0_or_1(self):
        _, _, final = run(0)
        for val in final.table[1]:
            assert val in (0, 1)


class TestWordBreakFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_descriptions_mention_dictionary(self):
        _, frames, _ = run(0)
        dict_frames = [f for f in frames if "∈" in f.description or "∉" in f.description]
        assert len(dict_frames) > 0
