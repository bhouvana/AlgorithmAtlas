"""Tests for Fibonacci Search plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "fibonacci_search",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
FibonacciSearchSimulation = _mod.FibonacciSearchSimulation

from algorithm_atlas_sdk import SimulationParams


def run(size: int = 20, seed: int = 42):
    sim = FibonacciSearchSimulation()
    params = SimulationParams(seed=seed, inputs={"array_size": size}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestFibonacciSearchMetadata:
    def test_slug(self):
        assert FibonacciSearchSimulation().metadata().slug == "fibonacci-search"

    def test_category(self):
        assert FibonacciSearchSimulation().metadata().category == "searching"


class TestFibonacciSearchCorrectness:
    @pytest.mark.parametrize("seed", range(15))
    def test_result_consistent(self, seed: int):
        initial, _, final = run(20, seed=seed)
        arr = list(initial.array)
        target = initial.target
        if final.found_at is not None:
            assert arr[final.found_at] == target
        else:
            assert target not in arr

    def test_array_is_sorted(self):
        initial, _, _ = run(20)
        arr = list(initial.array)
        assert arr == sorted(arr)

    def test_has_frames(self):
        _, frames, _ = run(20)
        assert len(frames) > 0

    def test_serializable(self):
        import json
        initial, frames, final = run(20)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
