"""Tests for Egg Drop Problem plugin."""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "egg_drop",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
EggDropSimulation = _mod.EggDropSimulation
_INSTANCES = _mod._INSTANCES

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = EggDropSimulation()
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


def brute_force_egg_drop(k: int, n: int) -> int:
    """Classical O(kn²) DP: dp[k][n] = min trials."""
    dp = [[0] * (n + 1) for _ in range(k + 1)]
    for floors in range(1, n + 1):
        dp[1][floors] = floors
    for eggs in range(2, k + 1):
        for floors in range(1, n + 1):
            dp[eggs][floors] = floors  # worst case
            for x in range(1, floors + 1):
                worst = 1 + max(dp[eggs - 1][x - 1], dp[eggs][floors - x])
                dp[eggs][floors] = min(dp[eggs][floors], worst)
    return dp[k][n]


class TestEggDropMetadata:
    def test_slug(self):
        assert EggDropSimulation().metadata().slug == "egg-drop"

    def test_category(self):
        assert EggDropSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert EggDropSimulation().metadata().visualization_type == "MATRIX"


class TestEggDropCorrectness:
    @pytest.mark.parametrize("seed", range(len(_INSTANCES)))
    def test_correct_answer(self, seed: int):
        k, n = _INSTANCES[seed]
        _, _, final = run(seed)
        actual = int(final.description.split("= ")[1].split(" trials")[0])
        expected = brute_force_egg_drop(k, n)
        assert actual == expected, (
            f"k={k}, n={n}: expected {expected}, got {actual}"
        )

    def test_table_has_k_plus_1_rows(self):
        k, n = _INSTANCES[0]
        initial, _, _ = run(0)
        assert len(initial.table) == k + 1

    def test_has_frames(self):
        _, frames, _ = run(0)
        assert len(frames) > 0


class TestEggDropFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_dp_values_increase_with_trials(self):
        k, n = _INSTANCES[0]
        _, _, final = run(0)
        # For each egg row, values should be non-decreasing with trials
        table = final.table
        for e in range(1, len(table)):
            row = table[e]
            for a, b in zip(row, row[1:]):
                assert b >= a, f"Row {e} not non-decreasing: {row}"
