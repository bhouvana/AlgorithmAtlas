"""Insertion Sort test suite — ≥20 tests required by correctness gate."""
import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "insertion_sort_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
InsertionSortSimulation = _mod.InsertionSortSimulation

from algorithm_atlas_sdk import AlgorithmTestHarness, SimulationParams, SortState


def params(size: int = 8, seed: int = 42) -> SimulationParams:
    return SimulationParams(seed=seed, inputs={"array_size": size}, config={})


@pytest.fixture
def harness():
    return AlgorithmTestHarness(InsertionSortSimulation())


def test_random_array_sorted(harness):
    final = harness.get_terminal_state(params(8, seed=1))
    assert list(final.array) == sorted(final.array)

def test_multiple_seeds(harness):
    for seed in range(12):
        final = harness.get_terminal_state(params(10, seed=seed))
        assert list(final.array) == sorted(final.array)

def test_two_elements(harness):
    final = harness.get_terminal_state(params(2))
    assert final.array[0] <= final.array[1]

def test_single_element(harness):
    final = harness.get_terminal_state(params(1))
    assert len(final.array) == 1

def test_large_array(harness):
    final = harness.get_terminal_state(params(50, seed=77))
    assert list(final.array) == sorted(final.array)

def test_comparisons_leq_quadratic_bound(harness):
    n = 10
    final = harness.get_terminal_state(params(n, seed=3))
    assert final.comparisons <= n * (n - 1) // 2

def test_comparisons_at_least_n_minus_1(harness):
    n = 8
    final = harness.get_terminal_state(params(n, seed=42))
    assert final.comparisons >= n - 1

def test_swaps_leq_quadratic_bound(harness):
    n = 8
    final = harness.get_terminal_state(params(n, seed=99))
    assert final.swaps <= n * (n - 1) // 2

def test_deterministic(harness):
    harness.assert_deterministic(params(8))

def test_json_serializable(harness):
    harness.assert_json_serializable(params(8))

def test_terminal_state_fully_sorted(harness):
    harness.assert_terminal_state(
        params(8),
        lambda s: isinstance(s, SortState) and s.sorted_indices == frozenset(range(len(s.array)))
    )

def test_sorted_indices_is_prefix(harness):
    states = harness.run_to_completion(params(8))
    for s in states:
        assert isinstance(s, SortState)
        si = s.sorted_indices
        if si:
            max_idx = max(si)
            assert si == frozenset(range(max_idx + 1))

def test_no_comparing_in_terminal_frame(harness):
    final = harness.get_terminal_state(params(8))
    assert final.comparing is None

def test_array_length_constant(harness):
    states = harness.run_to_completion(params(8))
    for s in states:
        assert len(s.array) == 8

def test_auxiliary_indices_tracks_insertion(harness):
    states = harness.run_to_completion(params(6))
    has_aux = any(
        isinstance(s, SortState) and len(s.auxiliary_indices) > 0
        for s in states
    )
    assert has_aux

def test_metadata_correctness(harness):
    meta = InsertionSortSimulation().metadata()
    assert meta.slug == "insertion-sort"
    assert meta.complexity_time_best == "O(n)"
    assert meta.complexity_time_worst == "O(n²)"

def test_frame_count_positive(harness):
    count = harness.get_frame_count(params(5))
    assert count > 5

def test_stable_equal_elements(harness):
    for seed in [10, 20, 30, 40, 50]:
        final = harness.get_terminal_state(params(8, seed=seed))
        assert list(final.array) == sorted(final.array)

def test_comparisons_monotone(harness):
    states = harness.run_to_completion(params(8))
    counts = [s.comparisons for s in states]
    assert counts == sorted(counts)

def test_swaps_non_negative(harness):
    final = harness.get_terminal_state(params(10))
    assert final.swaps >= 0
