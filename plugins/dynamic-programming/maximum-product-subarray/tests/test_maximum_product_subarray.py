"""Tests for Maximum Product Subarray plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "maximum_product_subarray",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
MaxProductSubarraySimulation = _mod.MaxProductSubarraySimulation
_max_product = _mod._max_product

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 8, seed: int = 0):
    sim = MaxProductSubarraySimulation()
    params = SimulationParams(seed=seed, inputs={"array_size": n}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestMaxProdMetadata:
    def test_slug(self):
        assert MaxProductSubarraySimulation().metadata().slug == "maximum-product-subarray"

    def test_category(self):
        assert MaxProductSubarraySimulation().metadata().category == "dynamic-programming"


class TestMaxProdCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_max(self, seed: int):
        initial, _, final = run(8, seed)
        expected = _max_product(list(initial.array))
        result = int(final.description.split("= ")[1])
        assert result == expected

    def test_has_n_frames(self):
        initial, frames, _ = run(8)
        assert len(frames) == len(initial.array)


class TestMaxProdFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(8)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
