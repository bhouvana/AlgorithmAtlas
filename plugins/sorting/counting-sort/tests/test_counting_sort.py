"""Counting Sort test suite — ≥20 tests required by correctness gate."""
import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "counting_sort_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CountingSortSimulation = _mod.CountingSortSimulation

from algorithm_atlas_sdk import AlgorithmTestHarness, SimulationParams, SortState


def params(size: int = 10, max_val: int = 20, seed: int = 42) -> SimulationParams:
    return SimulationParams(
        seed=seed,
        inputs={"array_size": size, "max_value": max_val},
        config={},
    )


@pytest.fixture
def harness():
    return AlgorithmTestHarness(CountingSortSimulation())


def test_random_sorted(harness):
    final = harness.get_terminal_state(params(10))
    assert list(final.array) == sorted(final.array)

def test_multiple_seeds(harness):
    for seed in range(12):
        final = harness.get_terminal_state(params(10, seed=seed))
        assert list(final.array) == sorted(final.array)

def test_all_same_value(harness):
    final = harness.get_terminal_state(params(5, max_val=1))
    assert all(v == 1 for v in final.array)

def test_small_range_large_array(harness):
    final = harness.get_terminal_state(params(50, max_val=5))
    assert list(final.array) == sorted(final.array)

def test_single_element(harness):
    final = harness.get_terminal_state(params(1))
    assert len(final.array) == 1

def test_two_elements(harness):
    final = harness.get_terminal_state(params(2))
    assert final.array[0] <= final.array[1]

def test_no_comparisons(harness):
    final = harness.get_terminal_state(params(10))
    assert final.comparisons == 0

def test_writes_equals_n(harness):
    n = 10
    final = harness.get_terminal_state(params(n))
    assert final.swaps == n

def test_deterministic(harness):
    harness.assert_deterministic(params(10))

def test_json_serializable(harness):
    harness.assert_json_serializable(params(10))

def test_terminal_fully_sorted(harness):
    harness.assert_terminal_state(
        params(10),
        lambda s: isinstance(s, SortState) and s.sorted_indices == frozenset(range(len(s.array)))
    )

def test_no_comparing_in_terminal(harness):
    final = harness.get_terminal_state(params(10))
    assert final.comparing is None

def test_array_length_constant(harness):
    states = harness.run_to_completion(params(10))
    for s in states:
        assert len(s.array) == 10

def test_auxiliary_indices_during_count(harness):
    states = harness.run_to_completion(params(8))
    has_aux = any(
        isinstance(s, SortState) and len(s.auxiliary_indices) > 0
        for s in states
    )
    assert has_aux

def test_metadata_slug(harness):
    meta = CountingSortSimulation().metadata()
    assert meta.slug == "counting-sort"

def test_metadata_linear_complexity(harness):
    meta = CountingSortSimulation().metadata()
    assert "k" in meta.complexity_time_best
    assert "n" in meta.complexity_time_best

def test_large_array(harness):
    final = harness.get_terminal_state(params(100, max_val=50))
    assert list(final.array) == sorted(final.array)

def test_various_k_values(harness):
    for k in [5, 10, 20, 50]:
        final = harness.get_terminal_state(params(15, max_val=k))
        assert list(final.array) == sorted(final.array)

def test_writes_exactly_n_for_any_input(harness):
    for seed in [1, 2, 3]:
        final = harness.get_terminal_state(params(8, seed=seed))
        assert final.swaps == 8

def test_comparisons_always_zero(harness):
    for seed in [1, 2, 3, 4, 5]:
        final = harness.get_terminal_state(params(10, seed=seed))
        assert final.comparisons == 0
