"""Tests for Chinese Remainder Theorem plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "chinese_remainder",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ChineseRemainderSimulation = _mod.ChineseRemainderSimulation
_INSTANCES = _mod._INSTANCES
_crt = _mod._crt

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = ChineseRemainderSimulation()
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


class TestCRTMetadata:
    def test_slug(self):
        assert ChineseRemainderSimulation().metadata().slug == "chinese-remainder"

    def test_category(self):
        assert ChineseRemainderSimulation().metadata().category == "number-theory"

    def test_visualization_type(self):
        assert ChineseRemainderSimulation().metadata().visualization_type == "MATRIX"


class TestCRTCorrectness:
    @pytest.mark.parametrize("seed", range(len(_INSTANCES)))
    def test_correct_solution(self, seed: int):
        remainders, moduli, expected = _INSTANCES[seed]
        _, _, final = run(seed)
        result = int(final.description.split(" = ")[-1])
        assert result == expected, f"seed={seed}: expected {expected}, got {result}"

    @pytest.mark.parametrize("seed", range(len(_INSTANCES)))
    def test_satisfies_congruences(self, seed: int):
        remainders, moduli, expected = _INSTANCES[seed]
        for r, m in zip(remainders, moduli):
            assert expected % m == r, f"seed={seed}: {expected} mod {m} != {r}"

    def test_has_frames(self):
        _, frames, _ = run(0)
        assert len(frames) > 0


class TestCRTFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_table_has_4_rows(self):
        initial, _, _ = run(0)
        assert len(initial.table) == 4
