"""Tests for Stock Trading with Cooldown plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "stock_cooldown_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

StockCooldownSimulation = mod.StockCooldownSimulation
_PRICES_EXAMPLES = mod._PRICES_EXAMPLES


def _brute_force_cooldown(prices):
    """O(3^n) brute force for small inputs."""
    n = len(prices)

    def rec(i, holding):
        if i >= n:
            return 0
        if holding:
            # sell today or keep
            sell = prices[i] + rec(i + 2, False)
            keep = rec(i + 1, True)
            return max(sell, keep)
        else:
            # buy today or skip
            buy = -prices[i] + rec(i + 1, True)
            skip = rec(i + 1, False)
            return max(buy, skip)

    return rec(0, False)


def _make_plugin(seed=0):
    plugin = StockCooldownSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
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
    p = StockCooldownSimulation()
    assert p.metadata().slug == "stock-cooldown"


def test_metadata_category():
    p = StockCooldownSimulation()
    assert p.metadata().category == "dynamic-programming"


def test_initial_swaps_zero():
    plugin, params = _make_plugin(seed=0)
    state = plugin.initialize(params)
    assert state.swaps == 0


def test_final_profit_seed0():
    # prices = [1, 2, 3, 0, 2] → max profit = 3 (buy@1 sell@3, cooldown, buy@0 sell@2)
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    final = states[-1]
    assert final.swaps == _brute_force_cooldown(_PRICES_EXAMPLES[0])


def test_final_profit_seed1():
    plugin, params = _make_plugin(seed=1)
    states = _collect(plugin, params)
    final = states[-1]
    expected = _brute_force_cooldown(_PRICES_EXAMPLES[1])
    assert final.swaps == expected


def test_final_profit_seed2_decreasing():
    # prices = [5,4,3,2,1] → no profit possible
    plugin, params = _make_plugin(seed=2)
    states = _collect(plugin, params)
    final = states[-1]
    assert final.swaps == 0


def test_final_profit_seed3():
    plugin, params = _make_plugin(seed=3)
    states = _collect(plugin, params)
    final = states[-1]
    expected = _brute_force_cooldown(_PRICES_EXAMPLES[3])
    assert final.swaps == expected


def test_step_count():
    plugin, params = _make_plugin(seed=0)
    prices = _PRICES_EXAMPLES[0]
    states = _collect(plugin, params)
    # initial + (n-1) step states + final = n+1
    assert len(states) == len(prices) + 1


def test_all_array_values_in_range():
    for seed in range(5):
        plugin, params = _make_plugin(seed=seed)
        states = _collect(plugin, params)
        for s in states:
            for v in s.array:
                assert 1 <= v <= 99


def test_description_encodes_prices():
    plugin, params = _make_plugin(seed=0)
    state = plugin.initialize(params)
    assert "prices=" in state.description


def test_final_description_mentions_profit():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    assert "profit" in states[-1].description.lower()
