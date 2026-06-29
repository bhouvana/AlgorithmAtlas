"""Tests for Reservoir Sampling plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "reservoir_sampling", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ReservoirSamplingSimulation = _mod.ReservoirSamplingSimulation

from algorithm_atlas_sdk import SimulationParams, SortState


def make_params(seed=0, stream_size=20, reservoir_size=5):
    return SimulationParams(
        seed=seed, inputs={"stream_size": stream_size, "reservoir_size": reservoir_size}
    )


def run(seed=0, stream_size=20, reservoir_size=5):
    sim = ReservoirSamplingSimulation()
    params = make_params(seed=seed, stream_size=stream_size, reservoir_size=reservoir_size)
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
        assert ReservoirSamplingSimulation().metadata().slug == "reservoir-sampling"

    def test_category(self):
        assert ReservoirSamplingSimulation().metadata().category == "randomized"

    def test_visualization_type(self):
        assert ReservoirSamplingSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestInitialize:
    def test_returns_sort_state(self):
        init = ReservoirSamplingSimulation().initialize(make_params())
        assert isinstance(init, SortState)

    def test_array_length_equals_stream_size(self):
        init = ReservoirSamplingSimulation().initialize(make_params(stream_size=15))
        assert len(init.array) == 15

    def test_reservoir_size_in_swaps(self):
        init = ReservoirSamplingSimulation().initialize(make_params(reservoir_size=4))
        assert init.swaps == 4

    def test_all_values_in_range(self):
        init = ReservoirSamplingSimulation().initialize(make_params())
        assert all(1 <= v <= 99 for v in init.array)


class TestSteps:
    def test_produces_steps(self):
        _, states, _ = run()
        assert len(states) >= 1

    def test_all_sort_state(self):
        _, states, final = run()
        for s in states:
            assert isinstance(s, SortState)
        assert isinstance(final, SortState)

    def test_reservoir_size_constant(self):
        k = 5
        _, states, final = run(reservoir_size=k)
        for s in states:
            assert s.swaps == k
        assert final.swaps == k

    def test_reservoir_indices_in_bounds(self):
        _, _, final = run()
        for idx in final.sorted_indices:
            assert 0 <= idx < len(final.array)

    def test_reproducible(self):
        _, _, f1 = run(seed=7)
        _, _, f2 = run(seed=7)
        assert f1.description == f2.description

    def test_final_description_has_reservoir(self):
        _, _, final = run()
        assert "reservoir" in final.description.lower() or "sample" in final.description.lower()

    def test_array_unchanged(self):
        init, _, final = run()
        assert init.array == final.array
