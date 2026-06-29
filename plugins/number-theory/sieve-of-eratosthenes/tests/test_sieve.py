"""Tests for Sieve of Eratosthenes plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "sieve_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
SieveSimulation = _mod.SieveSimulation

from algorithm_atlas_sdk import SimulationParams


def run(limit: int = 30):
    sim = SieveSimulation()
    params = SimulationParams(seed=0, inputs={"limit": limit}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


def naive_primes(n: int):
    from sympy import isprime
    return [i for i in range(2, n + 1) if isprime(i)]


def simple_primes(n: int):
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(2, n+1) if sieve[i]]


class TestSieveMetadata:
    def test_slug(self):
        assert SieveSimulation().metadata().slug == "sieve-of-eratosthenes"

    def test_category(self):
        assert SieveSimulation().metadata().category == "number-theory"

    def test_visualization_type(self):
        assert SieveSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestSieveCorrectness:
    @pytest.mark.parametrize("limit", [20, 25, 30, 40, 50])
    def test_primes_match_naive(self, limit: int):
        _, _, final = run(limit)
        expected_primes = set(simple_primes(limit))
        # sorted_indices are the prime positions; array[i] = i + 2
        found_primes = {final.array[k] for k in final.sorted_indices}
        assert found_primes == expected_primes, (
            f"limit={limit}: got {sorted(found_primes)}, expected {sorted(expected_primes)}"
        )

    def test_known_primes_up_to_30(self):
        _, _, final = run(30)
        expected = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29}
        found = {final.array[k] for k in final.sorted_indices}
        assert found == expected

    def test_prime_count(self):
        # π(30) = 10, π(50) = 15
        _, _, final30 = run(30)
        _, _, final50 = run(50)
        assert len(final30.sorted_indices) == 10
        assert len(final50.sorted_indices) == 15

    def test_2_is_prime(self):
        _, _, final = run(20)
        assert final.array[0] == 2  # first element is 2
        assert 0 in final.sorted_indices


class TestSieveFrames:
    def test_has_frames(self):
        _, frames, _ = run(30)
        assert len(frames) > 0

    def test_array_is_range(self):
        initial, _, _ = run(30)
        assert initial.array == tuple(range(2, 31))

    def test_no_current_cell_at_end(self):
        _, _, final = run(30)
        assert final.comparing is None

    def test_serializable(self):
        import json
        initial, frames, final = run(30)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_clamp_min(self):
        sim = SieveSimulation()
        p = SimulationParams(seed=0, inputs={"limit": 5}, config={})
        s = sim.initialize(p)
        assert s.array[0] == 2  # starts at 2
        assert len(s.array) == 19  # min=20, so 2..20 = 19 elements

    def test_clamp_max(self):
        sim = SieveSimulation()
        p = SimulationParams(seed=0, inputs={"limit": 999}, config={})
        s = sim.initialize(p)
        assert len(s.array) == 49  # max=50, so 2..50 = 49 elements
