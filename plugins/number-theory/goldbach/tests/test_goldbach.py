"""Tests for Goldbach's Conjecture plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "goldbach_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

GoldbachSimulation = mod.GoldbachSimulation
_sieve = mod._sieve
_goldbach_pairs = mod._goldbach_pairs


def _make_plugin(n=40):
    plugin = GoldbachSimulation()

    class P:
        pass

    P.seed = 0
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
    p = GoldbachSimulation()
    assert p.metadata().slug == "goldbach"


def test_metadata_category():
    p = GoldbachSimulation()
    assert p.metadata().category == "number-theory"


def test_sieve_correctness():
    is_prime = _sieve(20)
    primes = [i for i in range(2, 21) if is_prime[i]]
    assert primes == [2, 3, 5, 7, 11, 13, 17, 19]


def test_goldbach_4():
    is_prime = _sieve(10)
    pairs = _goldbach_pairs(4, is_prime)
    assert (2, 2) in pairs


def test_goldbach_10():
    is_prime = _sieve(20)
    pairs = _goldbach_pairs(10, is_prime)
    for p, q in pairs:
        assert p + q == 10
        assert is_prime[p] and is_prime[q]


def test_all_pairs_sum_to_even():
    plugin, params = _make_plugin(n=40)
    states = _collect(plugin, params)
    # Each step state's description should include valid sum
    is_prime = _sieve(50)
    for state in states[1:-1]:
        # Extract even number from description
        import re
        m = re.search(r"^(\d+) = (\d+)\+(\d+)", state.description)
        if m:
            n_val, p, q = int(m.group(1)), int(m.group(2)), int(m.group(3))
            assert p + q == n_val
            assert is_prime[p] and is_prime[q]


def test_all_even_numbers_have_decomposition():
    plugin, params = _make_plugin(n=60)
    states = _collect(plugin, params)
    # All step states should have swaps >= 1 (at least one pair found)
    for state in states[1:-1]:
        assert state.swaps >= 1


def test_step_count():
    plugin, params = _make_plugin(n=20)
    states = _collect(plugin, params)
    # Even numbers: 4, 6, 8, ..., 20 → (20-4)//2 + 1 = 9 evens
    evens = list(range(4, 21, 2))
    assert len(states) == len(evens) + 2  # initial + steps + final


def test_all_array_values_in_range():
    plugin, params = _make_plugin(n=40)
    states = _collect(plugin, params)
    for s in states:
        for v in s.array:
            assert 1 <= v <= 99


def test_final_description_verified():
    plugin, params = _make_plugin(n=40)
    states = _collect(plugin, params)
    final = states[-1]
    assert "verified" in final.description.lower()


def test_initial_array_length():
    plugin, params = _make_plugin(n=20)
    state = plugin.initialize(params)
    evens = list(range(4, 21, 2))
    assert len(state.array) == len(evens)
