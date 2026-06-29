"""
Bubble Sort correctness test suite.

Minimum 20 tests required by the algorithm correctness gate.
Tests cover: correctness, edge cases, simulation invariants, complexity bounds.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "bubble_sort_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BubbleSortSimulation = _mod.BubbleSortSimulation

from algorithm_atlas_sdk import AlgorithmTestHarness, SimulationParams, SortState


def make_params(
    array_size: int = 5,
    input_order: str = "random",
    seed: int = 42,
) -> SimulationParams:
    return SimulationParams(
        seed=seed,
        inputs={"array_size": array_size, "input_order": input_order},
        config={},
    )


@pytest.fixture
def harness() -> AlgorithmTestHarness:
    return AlgorithmTestHarness(BubbleSortSimulation())


# ─── Correctness ──────────────────────────────────────────────────────────────

def test_random_array_is_sorted(harness):
    p = make_params(10, "random", seed=1)
    terminal = harness.get_terminal_state(p)
    assert isinstance(terminal, SortState)
    assert list(terminal.array) == sorted(terminal.array)


def test_already_sorted_remains_sorted(harness):
    p = make_params(8, "sorted")
    terminal = harness.get_terminal_state(p)
    assert list(terminal.array) == sorted(terminal.array)


def test_reverse_sorted_is_sorted(harness):
    p = make_params(8, "reverse")
    terminal = harness.get_terminal_state(p)
    assert list(terminal.array) == sorted(terminal.array)


def test_nearly_sorted_is_sorted(harness):
    p = make_params(10, "nearly_sorted", seed=7)
    terminal = harness.get_terminal_state(p)
    assert list(terminal.array) == sorted(terminal.array)


def test_two_elements_unsorted(harness):
    p = make_params(2, "reverse")
    terminal = harness.get_terminal_state(p)
    assert list(terminal.array) == [1, 2]


def test_two_elements_sorted(harness):
    p = make_params(2, "sorted")
    terminal = harness.get_terminal_state(p)
    assert list(terminal.array) == [1, 2]


def test_single_element(harness):
    """Single element — no comparisons, no swaps, immediately sorted."""
    p = make_params(1, "sorted")
    terminal = harness.get_terminal_state(p)
    assert len(terminal.array) == 1
    assert terminal.comparisons == 0
    assert terminal.swaps == 0


def test_elements_are_preserved_not_lost(harness):
    """No element may be lost or duplicated during sorting."""
    p = make_params(15, "random", seed=99)
    initial = BubbleSortSimulation().initialize(p)
    terminal = harness.get_terminal_state(p)
    assert sorted(terminal.array) == sorted(initial.array)
    assert len(terminal.array) == len(initial.array)


def test_large_array_is_sorted(harness):
    p = make_params(100, "random", seed=2024)
    terminal = harness.get_terminal_state(p)
    assert list(terminal.array) == sorted(terminal.array)


def test_different_seeds_produce_different_arrays(harness):
    """Different seeds must produce different initial orderings."""
    s1 = BubbleSortSimulation().initialize(make_params(10, "random", seed=1))
    s2 = BubbleSortSimulation().initialize(make_params(10, "random", seed=2))
    assert s1.array != s2.array


# ─── Swap and comparison invariants ──────────────────────────────────────────

def test_best_case_zero_swaps(harness):
    """Already-sorted array: optimized bubble sort requires 0 swaps."""
    p = make_params(10, "sorted")
    terminal = harness.get_terminal_state(p)
    assert terminal.swaps == 0


def test_best_case_n_minus_one_comparisons(harness):
    """Already-sorted array: exactly n-1 comparisons (one pass, early exit)."""
    n = 10
    p = make_params(n, "sorted")
    terminal = harness.get_terminal_state(p)
    assert terminal.comparisons == n - 1


def test_worst_case_comparison_count(harness):
    """Reverse-sorted array: n*(n-1)/2 comparisons."""
    n = 6
    p = make_params(n, "reverse")
    terminal = harness.get_terminal_state(p)
    expected = n * (n - 1) // 2
    assert terminal.comparisons == expected


def test_comparison_count_is_non_decreasing_across_frames(harness):
    """Comparisons must only increase — they are never decremented."""
    p = make_params(8, "random", seed=5)
    states = harness.run_to_completion(p)
    counts = [s.comparisons for s in states]
    assert counts == sorted(counts)


def test_swap_count_is_non_decreasing_across_frames(harness):
    """Swaps must only increase — they are never decremented."""
    p = make_params(8, "random", seed=5)
    states = harness.run_to_completion(p)
    counts = [s.swaps for s in states]
    assert counts == sorted(counts)


def test_array_length_constant_across_all_frames(harness):
    """Array length must never change during sorting."""
    p = make_params(12, "random", seed=3)
    states = harness.run_to_completion(p)
    lengths = {len(s.array) for s in states}
    assert len(lengths) == 1
    assert 12 in lengths


# ─── Simulation invariants ────────────────────────────────────────────────────

def test_deterministic(harness):
    """Same params → identical frame sequence across two runs."""
    harness.assert_deterministic(make_params(8, "random", seed=42))


def test_all_frames_json_serializable(harness):
    """Every frame must cross the WebSocket boundary without error."""
    harness.assert_json_serializable(make_params(6, "random", seed=10))


def test_produces_multiple_frames(harness):
    """Non-trivial input must produce more than one frame."""
    p = make_params(5, "reverse")
    assert harness.get_frame_count(p) > 1


def test_sorted_indices_only_grow(harness):
    """sorted_indices is append-only — elements are never 'un-confirmed'."""
    p = make_params(8, "random", seed=77)
    states = harness.run_to_completion(p)
    for i in range(1, len(states)):
        prev = states[i - 1].sorted_indices
        curr = states[i].sorted_indices
        assert prev.issubset(curr), (
            f"sorted_indices shrank at frame {i}: {prev} → {curr}"
        )


def test_terminal_state_all_indices_sorted(harness):
    """At termination, every index must be in sorted_indices."""
    n = 8
    p = make_params(n, "random", seed=33)
    terminal = harness.get_terminal_state(p)
    assert terminal.sorted_indices == frozenset(range(n))
