"""Tests for Cocktail Shaker Sort plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "cocktail_sort",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CocktailSortSimulation = _mod.CocktailSortSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 10, seed: int = 42):
    sim = CocktailSortSimulation()
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


class TestCocktailSortMetadata:
    def test_slug(self):
        assert CocktailSortSimulation().metadata().slug == "cocktail-sort"

    def test_category(self):
        assert CocktailSortSimulation().metadata().category == "sorting"

    def test_visualization_type(self):
        assert CocktailSortSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestCocktailSortCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_sorted_output(self, seed: int):
        initial, _, final = run(10, seed=seed)
        assert final.array == tuple(sorted(initial.array))

    def test_all_indices_sorted(self):
        _, _, final = run(10)
        assert final.sorted_indices == frozenset(range(10))

    def test_same_elements(self):
        initial, _, final = run(10)
        assert sorted(initial.array) == sorted(final.array)


class TestCocktailSortFrames:
    def test_has_frames(self):
        _, frames, _ = run(10)
        assert len(frames) > 0

    def test_comparisons_positive(self):
        _, _, final = run(10)
        assert final.comparisons > 0

    def test_serializable(self):
        import json
        initial, frames, final = run(10)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
