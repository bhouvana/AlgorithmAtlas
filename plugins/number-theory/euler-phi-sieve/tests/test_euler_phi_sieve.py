"""Tests for Euler's Totient Sieve plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "euler_phi_sieve", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
EulerPhiSieveSimulation = _mod.EulerPhiSieveSimulation

from algorithm_atlas_sdk import SimulationParams, SortState

KNOWN_PHI = {
    1: 1, 2: 1, 3: 2, 4: 2, 5: 4, 6: 2, 7: 6, 8: 4,
    9: 6, 10: 4, 12: 4, 15: 8, 20: 8, 30: 8,
}


def make_params(n=30):
    return SimulationParams(seed=0, inputs={"n": n})


def run(n=30):
    sim = EulerPhiSieveSimulation()
    params = make_params(n=n)
    init = sim.initialize(params)
    gen = sim.steps(init)
    states = []
    try:
        while True:
            states.append(next(gen))
    except StopIteration as e:
        final = e.value
    return init, states, final


class TestMetadata:
    def test_slug(self):
        assert EulerPhiSieveSimulation().metadata().slug == "euler-phi-sieve"

    def test_category(self):
        assert EulerPhiSieveSimulation().metadata().category == "number-theory"

    def test_visualization_type(self):
        assert EulerPhiSieveSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestInitialize:
    def test_returns_sort_state(self):
        init = EulerPhiSieveSimulation().initialize(make_params(n=20))
        assert isinstance(init, SortState)

    def test_array_length(self):
        init = EulerPhiSieveSimulation().initialize(make_params(n=20))
        assert len(init.array) == 20

    def test_initial_values(self):
        init = EulerPhiSieveSimulation().initialize(make_params(n=10))
        assert list(init.array) == list(range(1, 11))


class TestCorrectness:
    def test_known_phi_values_n30(self):
        _, _, final = run(n=30)
        arr = final.array
        for i, expected in KNOWN_PHI.items():
            if i <= 30:
                assert arr[i - 1] == expected, (
                    f"phi({i}): got {arr[i-1]}, expected {expected}"
                )

    def test_phi_1_equals_1(self):
        _, _, final = run(n=10)
        assert final.array[0] == 1

    def test_prime_phi_is_p_minus_1(self):
        _, _, final = run(n=20)
        for p in [2, 3, 5, 7, 11, 13, 17, 19]:
            if p <= 20:
                assert final.array[p - 1] == p - 1

    def test_prime_count_n30(self):
        _, _, final = run(n=30)
        assert final.swaps == 10  # 2,3,5,7,11,13,17,19,23,29

    def test_prime_count_n10(self):
        _, _, final = run(n=10)
        assert final.swaps == 4  # 2,3,5,7

    def test_all_values_positive(self):
        _, _, final = run(n=50)
        assert all(v >= 1 for v in final.array)

    def test_phi_leq_n(self):
        _, _, final = run(n=30)
        for i, phi_i in enumerate(final.array, start=1):
            assert phi_i <= i


class TestSteps:
    def test_produces_steps(self):
        _, states, _ = run()
        assert len(states) >= 1

    def test_all_sort_state(self):
        _, states, final = run()
        for s in states:
            assert isinstance(s, SortState)
        assert isinstance(final, SortState)

    def test_array_length_constant(self):
        _, states, final = run(n=20)
        for s in states:
            assert len(s.array) == 20
        assert len(final.array) == 20

    def test_prime_indices_are_primes(self):
        _, _, final = run(n=20)
        primes_set = {2, 3, 5, 7, 11, 13, 17, 19}
        for idx in final.sorted_indices:
            val = idx + 1
            assert val in primes_set
