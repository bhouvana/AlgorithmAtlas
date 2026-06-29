"""Tests for Primitive Root Finder plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "prim_root_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

PrimitiveRootSimulation = mod.PrimitiveRootSimulation
_is_primitive_root = mod._is_primitive_root
_find_primitive_root = mod._find_primitive_root
_PRIMES = mod._PRIMES


def _make_plugin(p=41, seed=0):
    plugin = PrimitiveRootSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {"size": p}
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
    p = PrimitiveRootSimulation()
    assert p.metadata().slug == "primitive-root"


def test_metadata_category():
    p = PrimitiveRootSimulation()
    assert p.metadata().category == "number-theory"


def test_primitive_root_7():
    # Primitive roots mod 7: 3, 5
    assert _is_primitive_root(3, 7)
    assert _is_primitive_root(5, 7)
    assert not _is_primitive_root(2, 7)  # ord(2)=3, not 6


def test_primitive_root_11():
    # Primitive roots mod 11: 2, 6, 7, 8
    assert _is_primitive_root(2, 11)
    assert not _is_primitive_root(10, 11)  # ord(10)=2


def test_find_primitive_root_41():
    g = _find_primitive_root(41)
    assert _is_primitive_root(g, 41)
    assert g > 1


def test_find_smallest_prim_root():
    # For each prime, found root should be smallest
    for p in [7, 11, 13, 17]:
        g = _find_primitive_root(p)
        for smaller in range(2, g):
            assert not _is_primitive_root(smaller, p), f"g={smaller} is prim root of {p} but {g} was returned"


def test_prim_root_generates_all():
    g = _find_primitive_root(17)
    powers = set(pow(g, k, 17) for k in range(1, 17))
    assert powers == set(range(1, 17))


def test_final_swaps_is_primitive_root():
    plugin, params = _make_plugin(p=41)
    states = _collect(plugin, params)
    final = states[-1]
    assert _is_primitive_root(final.swaps, 41)


def test_all_array_values_in_range():
    plugin, params = _make_plugin(p=17)
    states = _collect(plugin, params)
    for s in states:
        for v in s.array:
            assert 1 <= v <= 99


def test_final_description_mentions_root():
    plugin, params = _make_plugin(p=41)
    states = _collect(plugin, params)
    final = states[-1]
    assert "primitive root" in final.description.lower() or "g=" in final.description


def test_primes_list_nonempty():
    assert len(_PRIMES) > 5
