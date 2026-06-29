"""Tests for Patience Sort plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "patience_sort", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PatienceSortSimulation = _mod.PatienceSortSimulation

from algorithm_atlas_sdk import SimulationParams, SortState


def make_params(seed=0, array_size=12):
    return SimulationParams(seed=seed, inputs={"array_size": array_size})


def run(seed=0, array_size=12):
    sim = PatienceSortSimulation()
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
        assert PatienceSortSimulation().metadata().slug == "patience-sort"

    def test_category(self):
        assert PatienceSortSimulation().metadata().category == "sorting"

    def test_visualization_type(self):
        assert PatienceSortSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestInitialize:
    def test_returns_sort_state(self):
        init = PatienceSortSimulation().initialize(make_params())
        assert isinstance(init, SortState)

    def test_array_length(self):
        init = PatienceSortSimulation().initialize(make_params(array_size=8))
        assert len(init.array) == 8

    def test_values_in_range(self):
        init = PatienceSortSimulation().initialize(make_params())
        assert all(1 <= v <= 99 for v in init.array)


class TestCorrectness:
    def test_final_array_sorted(self):
        init, _, final = run()
        assert list(final.array) == sorted(init.array)

    def test_all_sorted_indices_in_final(self):
        n = 10
        _, _, final = run(array_size=n)
        assert final.sorted_indices == frozenset(range(n))

    def test_preserves_multiset(self):
        init, _, final = run(seed=5, array_size=15)
        assert sorted(final.array) == sorted(init.array)

    def test_various_seeds(self):
        for seed in range(5):
            init, _, final = run(seed=seed, array_size=10)
            assert list(final.array) == sorted(init.array)


class TestSteps:
    def test_produces_steps(self):
        n = 12
        _, states, _ = run(array_size=n)
        assert len(states) == n  # one per card in pile-building phase

    def test_all_sort_state(self):
        _, states, final = run()
        for s in states:
            assert isinstance(s, SortState)
        assert isinstance(final, SortState)

    def test_pile_count_in_swaps(self):
        _, states, final = run()
        assert final.swaps >= 1

    def test_lis_property(self):
        # Number of piles = LIS length. Verify for known case.
        import random
        # [1,2,3,4,5] is strictly increasing → 1 pile per element... wait
        # patience sort: place on leftmost pile with top >= card
        # For [1,2,3,4,5]: 1 goes on pile 0, 2: no pile with top>=2 (pile 0 top=1<2) → new pile
        # So [1,2,3,...,n] creates n piles. LIS = n. ✓
        rng = random.Random(0)
        n = 8
        xs = list(range(1, n+1))  # strictly increasing
        # Run patience sort on this
        sim = PatienceSortSimulation()
        init = SortState(
            array=tuple(xs), comparing=None, last_swap=None,
            sorted_indices=frozenset(), comparisons=0, swaps=0,
            description=f"Patience sort n={n}: input={xs}",
        )
        gen = sim.steps(init)
        states = []
        try:
            while True:
                states.append(next(gen))
        except StopIteration as e:
            final = e.value
        assert final.swaps == n  # n piles for strictly increasing = LIS = n

    def test_reproducible(self):
        _, _, f1 = run(seed=3, array_size=10)
        _, _, f2 = run(seed=3, array_size=10)
        assert f1.array == f2.array
        assert f1.swaps == f2.swaps
