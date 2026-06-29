"""Tests for Coin Change Ways plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "coin_change_ways",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CoinChangeWaysSimulation = _mod.CoinChangeWaysSimulation
_INSTANCES = _mod._INSTANCES

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = CoinChangeWaysSimulation()
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


class TestCoinChangeWaysMetadata:
    def test_slug(self):
        assert CoinChangeWaysSimulation().metadata().slug == "coin-change-ways"

    def test_category(self):
        assert CoinChangeWaysSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert CoinChangeWaysSimulation().metadata().visualization_type == "MATRIX"


class TestCoinChangeWaysCorrectness:
    @pytest.mark.parametrize("seed", range(len(_INSTANCES)))
    def test_correct_count(self, seed: int):
        coins, amount, expected = _INSTANCES[seed]
        _, _, final = run(seed)
        result = int(final.description.split(" = ")[1])
        assert result == expected, f"seed={seed}: coins={coins} amount={amount} expected {expected}, got {result}"

    def test_has_frames(self):
        _, frames, _ = run(0)
        assert len(frames) > 0


class TestCoinChangeWaysFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
