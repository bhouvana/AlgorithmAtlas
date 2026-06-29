"""Radix Sort (LSD) test suite — ≥20 tests required by correctness gate."""
import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "radix_sort_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
RadixSortSimulation = _mod.RadixSortSimulation

from algorithm_atlas_sdk import AlgorithmTestHarness, SimulationParams, SortState


def params(size: int = 10, max_val: int = 100, seed: int = 42) -> SimulationParams:
    return SimulationParams(
        seed=seed,
        inputs={"array_size": size, "max_value": max_val},
        config={},
    )


@pytest.fixture
def harness():
    return AlgorithmTestHarness(RadixSortSimulation())


def test_random_sorted(harness):
    final = harness.get_terminal_state(params())
    assert list(final.array) == sorted(final.array)

def test_multiple_seeds(harness):
    for seed in range(12):
        final = harness.get_terminal_state(params(seed=seed))
        assert list(final.array) == sorted(final.array)

def test_single_digit_values(harness):
    final = harness.get_terminal_state(params(10, max_val=9))
    assert list(final.array) == sorted(final.array)

def test_three_digit_values(harness):
    final = harness.get_terminal_state(params(10, max_val=999))
    assert list(final.array) == sorted(final.array)

def test_single_element(harness):
    final = harness.get_terminal_state(params(1))
    assert len(final.array) == 1

def test_two_elements(harness):
    final = harness.get_terminal_state(params(2))
    assert final.array[0] <= final.array[1]

def test_large_array(harness):
    final = harness.get_terminal_state(params(80, max_val=999))
    assert list(final.array) == sorted(final.array)

def test_no_comparisons(harness):
    final = harness.get_terminal_state(params())
    assert final.comparisons == 0

def test_writes_at_least_n(harness):
    n = 10
    final = harness.get_terminal_state(params(n))
    assert final.swaps >= n

def test_deterministic(harness):
    harness.assert_deterministic(params())

def test_json_serializable(harness):
    harness.assert_json_serializable(params())

def test_terminal_fully_sorted(harness):
    harness.assert_terminal_state(
        params(),
        lambda s: isinstance(s, SortState) and s.sorted_indices == frozenset(range(len(s.array)))
    )

def test_no_comparing_in_terminal(harness):
    final = harness.get_terminal_state(params())
    assert final.comparing is None

def test_array_length_constant(harness):
    states = harness.run_to_completion(params())
    for s in states:
        assert len(s.array) == 10

def test_auxiliary_indices_set(harness):
    states = harness.run_to_completion(params())
    has_aux = any(
        isinstance(s, SortState) and len(s.auxiliary_indices) > 0
        for s in states
    )
    assert has_aux

def test_metadata_slug(harness):
    meta = RadixSortSimulation().metadata()
    assert meta.slug == "radix-sort"

def test_metadata_linear_complexity(harness):
    meta = RadixSortSimulation().metadata()
    assert "k" in meta.complexity_time_worst and "n" in meta.complexity_time_worst

def test_comparisons_always_zero(harness):
    for seed in [1, 2, 3, 4, 5]:
        final = harness.get_terminal_state(params(seed=seed))
        assert final.comparisons == 0

def test_various_array_sizes(harness):
    for n in [3, 7, 15, 20]:
        final = harness.get_terminal_state(params(n))
        assert list(final.array) == sorted(final.array)

def test_duplicate_values_sorted(harness):
    final = harness.get_terminal_state(params(15, max_val=5))
    assert list(final.array) == sorted(final.array)
