"""Tests for Collatz Sequence plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "collatz_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CollatzSimulation = mod.CollatzSimulation
_collatz_seq = mod._collatz_seq


def _make_plugin(n=27, seed=0):
    plugin = CollatzSimulation()

    class P:
        pass

    P.inputs = {"size": n}
    P.seed = seed
    return plugin, P()


def _collect(plugin, params):
    state = plugin.initialize(params)
    states = [state]
    gen = plugin.steps(state)
    try:
        while True:
            states.append(next(gen))
    except StopIteration as e:
        states.append(e.value)
    return states


def test_metadata_slug():
    p = CollatzSimulation()
    assert p.metadata().slug == "collatz"


def test_metadata_category():
    p = CollatzSimulation()
    assert p.metadata().category == "number-theory"


def test_initial_state_comparisons_zero():
    plugin, params = _make_plugin(n=6)
    state = plugin.initialize(params)
    assert state.comparisons == 0


def test_initial_swaps_is_n():
    plugin, params = _make_plugin(n=6)
    state = plugin.initialize(params)
    assert state.swaps == 6


def test_sequence_n6():
    seq = _collatz_seq(6)
    # 6 → 3 → 10 → 5 → 16 → 8 → 4 → 2 → 1
    assert seq[0] == 6
    assert 1 in seq
    assert seq[-1] == 1


def test_sequence_n4():
    seq = _collatz_seq(4)
    # 4 → 2 → 1
    assert seq == [4, 2, 1]


def test_sequence_n27_long():
    seq = _collatz_seq(27)
    assert len(seq) > 10  # 27 has a long sequence


def test_step_count_matches_sequence():
    plugin, params = _make_plugin(n=4)
    states = _collect(plugin, params)
    seq = _collatz_seq(4)
    # initial + len(seq)-1 steps + final
    assert len(states) == len(seq) + 1


def test_all_array_values_in_range():
    plugin, params = _make_plugin(n=27)
    states = _collect(plugin, params)
    for s in states:
        for v in s.array:
            assert 1 <= v <= 99


def test_comparisons_increment():
    plugin, params = _make_plugin(n=6)
    states = _collect(plugin, params)
    # step states have comparisons 1, 2, 3, ...
    step_states = states[1:-1]
    for i, s in enumerate(step_states):
        assert s.comparisons == i + 1


def test_description_contains_n():
    plugin, params = _make_plugin(n=12)
    state = plugin.initialize(params)
    assert "n=12" in state.description


def test_final_state_reached_1():
    plugin, params = _make_plugin(n=6)
    states = _collect(plugin, params)
    final = states[-1]
    assert "1" in final.description or "reached 1" in final.description


def test_final_sorted_indices_full():
    plugin, params = _make_plugin(n=4)
    states = _collect(plugin, params)
    final = states[-1]
    seq = _collatz_seq(4)
    assert final.sorted_indices == frozenset(range(len(seq)))
