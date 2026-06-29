"""Tests for Bucket Sort plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "bucket_sort_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BucketSortSimulation = mod.BucketSortSimulation
_gen_array = mod._gen_array
_insertion_sort = mod._insertion_sort


def _make_plugin(n=12, seed=0):
    plugin = BucketSortSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {"size": n}
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
    p = BucketSortSimulation()
    assert p.metadata().slug == "bucket-sort"


def test_metadata_category():
    p = BucketSortSimulation()
    assert p.metadata().category == "sorting"


def test_initial_array_length():
    plugin, params = _make_plugin(n=10)
    state = plugin.initialize(params)
    assert len(state.array) == 10


def test_final_array_sorted():
    for seed in range(5):
        plugin, params = _make_plugin(n=12, seed=seed)
        states = _collect(plugin, params)
        final = states[-1]
        arr = list(final.array)
        assert arr == sorted(arr), f"Not sorted for seed={seed}: {arr}"


def test_final_array_same_elements():
    plugin, params = _make_plugin(n=12, seed=0)
    states = _collect(plugin, params)
    original = list(_gen_array(0, 12))
    final = list(states[-1].array)
    assert sorted(original) == sorted(final)


def test_final_sorted_indices_full():
    plugin, params = _make_plugin(n=8, seed=0)
    states = _collect(plugin, params)
    final = states[-1]
    assert final.sorted_indices == frozenset(range(8))


def test_steps_produced():
    plugin, params = _make_plugin(n=8, seed=0)
    states = _collect(plugin, params)
    assert len(states) >= 5


def test_all_array_values_in_range():
    plugin, params = _make_plugin(n=12, seed=0)
    states = _collect(plugin, params)
    for s in states:
        for v in s.array:
            assert 1 <= v <= 99


def test_final_description_mentions_sorted():
    plugin, params = _make_plugin(n=10, seed=0)
    states = _collect(plugin, params)
    final = states[-1]
    assert "sort" in final.description.lower()


def test_insertion_sort_helper():
    lst = [3, 1, 4, 1, 5, 9, 2, 6]
    result = _insertion_sort(list(lst))
    assert result == sorted(lst)
