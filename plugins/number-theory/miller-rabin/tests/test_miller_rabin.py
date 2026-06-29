"""Tests for Miller-Rabin Primality Test plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "miller_rabin",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
MillerRabinSimulation = _mod.MillerRabinSimulation
_CANDIDATES = _mod._CANDIDATES

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = MillerRabinSimulation()
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


def is_prime_trial(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


class TestMillerRabinMetadata:
    def test_slug(self):
        assert MillerRabinSimulation().metadata().slug == "miller-rabin"

    def test_category(self):
        assert MillerRabinSimulation().metadata().category == "number-theory"

    def test_visualization_type(self):
        assert MillerRabinSimulation().metadata().visualization_type == "MATRIX"


class TestMillerRabinCorrectness:
    @pytest.mark.parametrize("seed", range(len(_CANDIDATES)))
    def test_correct_verdict(self, seed: int):
        n, expected_prime = _CANDIDATES[seed]
        _, _, final = run(seed)
        verdict = final.description
        if expected_prime:
            assert "PRIME" in verdict, f"n={n} should be prime, got: {verdict}"
        else:
            assert "COMPOSITE" in verdict, f"n={n} should be composite, got: {verdict}"

    def test_has_frames(self):
        _, frames, _ = run(0)
        assert len(frames) >= 1

    def test_table_has_3_rows(self):
        initial, _, _ = run(0)
        assert len(initial.table) == 3


class TestMillerRabinFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_witnesses_in_table_row0(self):
        initial, _, _ = run(0)
        n = int(initial.description.split("(")[1].split(")")[0])
        witnesses = [a for a in initial.table[0] if a > 0]
        for a in witnesses:
            assert 1 < a < n or a == 2
