"""Selection Sort test suite — ≥20 tests required by correctness gate."""
import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "selection_sort_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
SelectionSortSimulation = _mod.SelectionSortSimulation

from algorithm_atlas_sdk import AlgorithmTestHarness, SimulationParams, SortState


def params(size: int = 8, seed: int = 42) -> SimulationParams:
    return SimulationParams(seed=seed, inputs={"array_size": size}, config={})


@pytest.fixture
def harness():
    return AlgorithmTestHarness(SelectionSortSimulation())


def test_random_array_sorted(harness):
    final = harness.get_terminal_state(params(8, seed=1))
    assert list(final.array) == sorted(final.array)

def test_multiple_seeds(harness):
    for seed in range(10):
        final = harness.get_terminal_state(params(10, seed=seed))
        assert list(final.array) == sorted(final.array), f"Failed for seed {seed}"

def test_two_elements(harness):
    final = harness.get_terminal_state(params(2))
    assert final.array[0] <= final.array[1]

def test_single_element(harness):
    final = harness.get_terminal_state(params(1))
    assert len(final.array) == 1

def test_large_array(harness):
    final = harness.get_terminal_state(params(50, seed=7))
    assert list(final.array) == sorted(final.array)

def test_swaps_at_most_n_minus_1(harness):
    final = harness.get_terminal_state(params(8, seed=42))
    assert final.swaps <= 7

def test_comparisons_exactly_n_squared(harness):
    n = 8
    final = harness.get_terminal_state(params(n, seed=42))
    expected = n * (n - 1) // 2
    assert final.comparisons == expected

def test_comparisons_quadratic_invariant(harness):
    for n in [4, 6, 8, 10]:
        final = harness.get_terminal_state(params(n, seed=1))
        expected = n * (n - 1) // 2
        assert final.comparisons == expected, f"n={n}: expected {expected} comparisons"

def test_deterministic(harness):
    harness.assert_deterministic(params(8))

def test_json_serializable(harness):
    harness.assert_json_serializable(params(8))

def test_terminal_state_fully_sorted(harness):
    harness.assert_terminal_state(
        params(8),
        lambda s: isinstance(s, SortState) and s.sorted_indices == frozenset(range(len(s.array)))
    )

def test_sorted_indices_monotonically_grows(harness):
    states = harness.run_to_completion(params(8))
    prev_sorted: frozenset = frozenset()
    for s in states:
        assert isinstance(s, SortState)
        assert prev_sorted <= s.sorted_indices
        prev_sorted = s.sorted_indices

def test_no_comparing_in_terminal_frame(harness):
    final = harness.get_terminal_state(params(8))
    assert final.comparing is None

def test_no_last_swap_in_terminal_frame(harness):
    final = harness.get_terminal_state(params(8))
    assert final.last_swap is None

def test_array_length_constant(harness):
    states = harness.run_to_completion(params(8))
    for s in states:
        assert isinstance(s, SortState)
        assert len(s.array) == 8

def test_comparisons_monotone(harness):
    states = harness.run_to_completion(params(8))
    counts = [s.comparisons for s in states]
    assert counts == sorted(counts)

def test_swaps_monotone(harness):
    states = harness.run_to_completion(params(8))
    counts = [s.swaps for s in states]
    assert counts == sorted(counts)

def test_metadata_correctness(harness):
    meta = SelectionSortSimulation().metadata()
    assert meta.slug == "selection-sort"
    assert meta.complexity_time_best == "O(n²)"
    assert meta.complexity_space == "O(1)"

def test_frame_count_increases_with_size(harness):
    count_small = harness.get_frame_count(params(4))
    count_large = harness.get_frame_count(params(8))
    assert count_large > count_small

def test_auxiliary_indices_tracks_minimum(harness):
    states = harness.run_to_completion(params(6))
    has_auxiliary = any(
        isinstance(s, SortState) and len(s.auxiliary_indices) > 0
        for s in states
    )
    assert has_auxiliary

def test_terminal_array_values_positive(harness):
    final = harness.get_terminal_state(params(8))
    assert all(v > 0 for v in final.array)
