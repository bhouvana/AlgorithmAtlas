"""Tests for Prime Factorization plugin."""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "prime_factorization",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PrimeFactorizationSimulation = _mod.PrimeFactorizationSimulation
_NUMBERS = _mod._NUMBERS

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = PrimeFactorizationSimulation()
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


class TestPrimeFactorizationMetadata:
    def test_slug(self):
        assert PrimeFactorizationSimulation().metadata().slug == "prime-factorization"

    def test_category(self):
        assert PrimeFactorizationSimulation().metadata().category == "number-theory"

    def test_visualization_type(self):
        assert PrimeFactorizationSimulation().metadata().visualization_type == "MATRIX"


class TestPrimeFactorizationCorrectness:
    @pytest.mark.parametrize("seed", range(len(_NUMBERS)))
    def test_product_equals_n(self, seed: int):
        n = _NUMBERS[seed]
        initial, _, _ = run(seed)
        primes = [x for x in initial.table[0] if x > 0]
        exponents = [x for x in initial.table[1] if x > 0]
        product = 1
        for p, e in zip(primes, exponents):
            product *= p ** e
        assert product == n, f"n={n}: product={product}"

    @pytest.mark.parametrize("seed", range(len(_NUMBERS)))
    def test_all_factors_prime(self, seed: int):
        initial, _, _ = run(seed)
        primes = [x for x in initial.table[0] if x > 0]
        for p in primes:
            # Check primality via trial division
            if p < 2:
                assert False, f"{p} is not prime"
            for d in range(2, int(p**0.5) + 1):
                assert p % d != 0, f"{p} is not prime (divisible by {d})"

    def test_has_frames(self):
        _, frames, _ = run(0)
        assert len(frames) >= 1

    def test_table_has_3_rows(self):
        initial, _, _ = run(0)
        assert len(initial.table) == 3


class TestPrimeFactorizationFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_quotient_decreases(self):
        _, frames, _ = run(0)
        quotients = [f.table[2][-1] for f in frames]
        for a, b in zip(quotients, quotients[1:]):
            assert b <= a
