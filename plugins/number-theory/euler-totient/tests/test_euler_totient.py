"""Tests for Euler's Totient Function plugin."""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "euler_totient",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
EulerTotientSimulation = _mod.EulerTotientSimulation
_NUMBERS = _mod._NUMBERS

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = EulerTotientSimulation()
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


def brute_force_phi(n: int) -> int:
    return sum(1 for k in range(1, n + 1) if math.gcd(k, n) == 1)


class TestEulerTotientMetadata:
    def test_slug(self):
        assert EulerTotientSimulation().metadata().slug == "euler-totient"

    def test_category(self):
        assert EulerTotientSimulation().metadata().category == "number-theory"

    def test_visualization_type(self):
        assert EulerTotientSimulation().metadata().visualization_type == "MATRIX"


class TestEulerTotientCorrectness:
    @pytest.mark.parametrize("seed", range(len(_NUMBERS)))
    def test_correct_totient(self, seed: int):
        n = _NUMBERS[seed]
        _, _, final = run(seed)
        result = int(final.description.split("= ")[1])
        expected = brute_force_phi(n)
        assert result == expected, f"φ({n}): expected {expected}, got {result}"

    def test_table_has_3_rows(self):
        initial, _, _ = run(0)
        assert len(initial.table) == 3

    def test_has_frames(self):
        _, frames, _ = run(0)
        assert len(frames) >= 1


class TestEulerTotientFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_phi_monotonically_applied(self):
        _, frames, final = run(0)
        # Each frame's phi value should be <= previous (phi decreases or stays)
        phi_values = [int(f.description.split("= ")[1]) for f in frames]
        for a, b in zip(phi_values, phi_values[1:]):
            assert b <= a
