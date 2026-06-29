"""Tests for K-Nearest Neighbors (1D) plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "knn", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
KNNSimulation = _mod.KNNSimulation
_generate_data = _mod._generate_data

from algorithm_atlas_sdk import SimulationParams, SortState


def make_params(seed=0, n_samples=20, k=3):
    return SimulationParams(seed=seed, inputs={"n_samples": n_samples, "k": k})


def run(seed=0, n_samples=20, k=3):
    sim = KNNSimulation()
    params = make_params(seed=seed, n_samples=n_samples, k=k)
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
        assert KNNSimulation().metadata().slug == "k-nearest-neighbors"

    def test_category(self):
        assert KNNSimulation().metadata().category == "machine-learning"

    def test_visualization_type(self):
        assert KNNSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestInitialize:
    def test_returns_sort_state(self):
        init = KNNSimulation().initialize(make_params())
        assert isinstance(init, SortState)

    def test_array_length(self):
        init = KNNSimulation().initialize(make_params(n_samples=15))
        assert len(init.array) == 15

    def test_all_bars_positive(self):
        init = KNNSimulation().initialize(make_params())
        assert all(v >= 1 for v in init.array)

    def test_description_has_k_and_q(self):
        init = KNNSimulation().initialize(make_params(k=5))
        assert "k=5" in init.description
        assert "q=" in init.description


class TestSteps:
    def test_produces_n_steps(self):
        _, states, _ = run(n_samples=20)
        assert len(states) == 20

    def test_all_sort_state(self):
        _, states, final = run()
        for s in states:
            assert isinstance(s, SortState)
        assert isinstance(final, SortState)

    def test_array_constant(self):
        init, states, final = run()
        for s in states:
            assert s.array == init.array

    def test_prediction_is_0_or_1(self):
        _, _, final = run()
        assert final.swaps in (0, 1)

    def test_k_neighbors_marked(self):
        k = 3
        _, _, final = run(k=k)
        assert len(final.sorted_indices) == k

    def test_reproducible(self):
        _, _, f1 = run(seed=7, n_samples=15, k=3)
        _, _, f2 = run(seed=7, n_samples=15, k=3)
        assert f1.swaps == f2.swaps
        assert f1.sorted_indices == f2.sorted_indices

    def test_final_description_has_predicted(self):
        _, _, final = run()
        assert "predicted" in final.description

    def test_k_neighbors_are_actual_nearest(self):
        import random
        for seed in range(5):
            n, k = 20, 3
            rng = random.Random(seed)
            xs, _ = _generate_data(rng, n)
            q = rng.randint(1, 99)
            dists = [abs(x - q) for x in xs]
            # k-th smallest distance (allow ties)
            kth_dist = sorted(dists)[k - 1]
            _, _, final = run(seed=seed, n_samples=n, k=k)
            assert len(final.sorted_indices) == k
            for idx in final.sorted_indices:
                assert dists[idx] <= kth_dist, (
                    f"seed={seed}: index {idx} has dist {dists[idx]} > {kth_dist}"
                )
