"""Tests for Lucas' Theorem plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "lucas_theorem",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
LucasTheoremSimulation = _mod.LucasTheoremSimulation
_INSTANCES = _mod._INSTANCES
_lucas = _mod._lucas
_c = _mod._c

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = LucasTheoremSimulation()
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


class TestLucasMetadata:
    def test_slug(self):
        assert LucasTheoremSimulation().metadata().slug == "lucas-theorem"

    def test_category(self):
        assert LucasTheoremSimulation().metadata().category == "number-theory"

    def test_visualization_type(self):
        assert LucasTheoremSimulation().metadata().visualization_type == "MATRIX"


class TestLucasCorrectness:
    @pytest.mark.parametrize("seed", range(len(_INSTANCES)))
    def test_correct_result(self, seed: int):
        n, k, p, expected = _INSTANCES[seed]
        _, _, final = run(seed)
        result = int(final.description.split("= ")[1])
        assert result == expected, f"seed={seed}: C({n},{k}) mod {p} expected {expected}, got {result}"

    @pytest.mark.parametrize("seed", range(len(_INSTANCES)))
    def test_matches_brute_force(self, seed: int):
        n, k, p, _ = _INSTANCES[seed]
        expected = _c(n, k) % p
        _, _, final = run(seed)
        result = int(final.description.split("= ")[1])
        assert result == expected

    def test_has_frames(self):
        _, frames, _ = run(0)
        assert len(frames) > 0


class TestLucasFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_table_is_p_by_p(self):
        for seed in range(3):
            _, k, p, _ = _INSTANCES[seed]
            initial, _, _ = run(seed)
            assert len(initial.table) == p
            for row in initial.table:
                assert len(row) == p
