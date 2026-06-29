"""Tests for Quickselect (Randomized) plugin."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

from algorithm_atlas_sdk import SimulationParams, SortState
from plugins.randomized.quickselect.algorithm import QuickselectSimulation


def make_params(seed=0, array_size=12):
    return SimulationParams(seed=seed, inputs={"array_size": array_size})


def run(seed=0, array_size=12):
    sim = QuickselectSimulation()
    params = make_params(seed=seed, array_size=array_size)
    init = sim.initialize(params)
    gen = sim.steps(init)
    states = []
    try:
        while True:
            states.append(next(gen))
    except StopIteration as e:
        final = e.value
    return init, states, final


class TestMetadata:
    def test_slug(self):
        m = QuickselectSimulation().metadata()
        assert m.slug == "quickselect"

    def test_category(self):
        m = QuickselectSimulation().metadata()
        assert m.category == "randomized"

    def test_visualization_type(self):
        m = QuickselectSimulation().metadata()
        assert m.visualization_type == "ARRAY_BARS"

    def test_complexity_average(self):
        m = QuickselectSimulation().metadata()
        assert m.complexity_time_average == "O(n)"

    def test_complexity_worst(self):
        m = QuickselectSimulation().metadata()
        assert m.complexity_time_worst == "O(n²)"


class TestInitialize:
    def test_returns_sort_state(self):
        sim = QuickselectSimulation()
        init = sim.initialize(make_params())
        assert isinstance(init, SortState)

    def test_array_length(self):
        sim = QuickselectSimulation()
        init = sim.initialize(make_params(array_size=10))
        assert len(init.array) == 10

    def test_k_is_median(self):
        sim = QuickselectSimulation()
        init = sim.initialize(make_params(array_size=12))
        assert init.swaps == 6  # n//2 = 6

    def test_k_for_odd_size(self):
        sim = QuickselectSimulation()
        init = sim.initialize(make_params(array_size=9))
        assert init.swaps == 4  # 9//2 = 4

    def test_values_in_range(self):
        sim = QuickselectSimulation()
        init = sim.initialize(make_params(seed=42, array_size=15))
        assert all(1 <= v <= 99 for v in init.array)

    def test_no_sorted_indices_initially(self):
        sim = QuickselectSimulation()
        init = sim.initialize(make_params())
        assert init.sorted_indices == frozenset()


class TestCorrectness:
    def test_finds_correct_kth_element(self):
        _, _, final = run(seed=0, array_size=12)
        # final.swaps holds the found value
        found_val = final.swaps
        k = 6
        _, _, _ = run(seed=0, array_size=12)
        import random
        rng = random.Random(0)
        original = [rng.randint(1, 99) for _ in range(12)]
        expected = sorted(original)[k]
        assert found_val == expected

    def test_finds_correct_kth_various_seeds(self):
        import random
        for seed in range(5):
            n = 10
            k = n // 2
            _, _, final = run(seed=seed, array_size=n)
            rng = random.Random(seed)
            original = [rng.randint(1, 99) for _ in range(n)]
            expected = sorted(original)[k]
            assert final.swaps == expected, f"seed={seed}: got {final.swaps}, expected {expected}"

    def test_final_sorted_indices_contains_k(self):
        k = 6
        _, _, final = run(seed=7, array_size=12)
        assert k in final.sorted_indices

    def test_array_preserves_all_elements(self):
        init, _, final = run(seed=3, array_size=12)
        assert sorted(init.array) == sorted(final.array)

    def test_small_array(self):
        import random
        n = 6
        k = n // 2
        _, _, final = run(seed=99, array_size=n)
        rng = random.Random(99)
        original = [rng.randint(1, 99) for _ in range(n)]
        expected = sorted(original)[k]
        assert final.swaps == expected


class TestSteps:
    def test_produces_steps(self):
        _, states, _ = run()
        assert len(states) >= 1

    def test_all_states_are_sort_state(self):
        _, states, final = run()
        for s in states:
            assert isinstance(s, SortState)
        assert isinstance(final, SortState)

    def test_comparisons_increase(self):
        _, states, final = run()
        prev = 0
        for s in states:
            assert s.comparisons >= prev
            prev = s.comparisons
        assert final.comparisons >= prev

    def test_array_length_constant(self):
        init, states, final = run()
        n = len(init.array)
        for s in states:
            assert len(s.array) == n
        assert len(final.array) == n

    def test_pivot_states_have_last_swap(self):
        # Every other state (partition step) should have last_swap set
        _, states, _ = run()
        # At least some states should have last_swap
        has_last_swap = any(s.last_swap is not None for s in states)
        assert has_last_swap

    def test_final_description_mentions_found(self):
        _, _, final = run()
        desc = final.description.lower()
        assert "done" in desc or "found" in desc or "smallest" in desc

    def test_reproducible(self):
        _, s1, f1 = run(seed=5, array_size=10)
        _, s2, f2 = run(seed=5, array_size=10)
        assert f1.swaps == f2.swaps
        assert len(s1) == len(s2)

    def test_different_seeds_may_differ(self):
        _, _, f1 = run(seed=0, array_size=10)
        _, _, f2 = run(seed=1, array_size=10)
        # Different seeds produce different arrays, so kth elements may differ
        # (not guaranteed, but tests that seeds are used)
        import random
        rng0 = random.Random(0)
        arr0 = sorted([rng0.randint(1, 99) for _ in range(10)])
        rng1 = random.Random(1)
        arr1 = sorted([rng1.randint(1, 99) for _ in range(10)])
        k = 5
        assert f1.swaps == arr0[k]
        assert f2.swaps == arr1[k]
