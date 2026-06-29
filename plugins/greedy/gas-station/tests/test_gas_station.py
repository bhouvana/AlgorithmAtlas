"""Tests for Gas Station plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import List

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "gas_station",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
GasStationSimulation = _mod.GasStationSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 6, seed: int = 42):
    sim = GasStationSimulation()
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


def brute_force_start(gas: List[int], cost: List[int]) -> int:
    """Try each station as the starting point."""
    n = len(gas)
    for start in range(n):
        tank = 0
        ok = True
        for step in range(n):
            i = (start + step) % n
            tank += gas[i] - cost[i]
            if tank < 0:
                ok = False
                break
        if ok:
            return start
    return -1


def parse_instance(state):
    desc = state.description
    gas_str, cost_str = desc.split("|")
    gas = [int(x) for x in gas_str.split("=")[1].split(",")]
    cost = [int(x) for x in cost_str.split("=")[1].split(",")]
    return gas, cost


class TestGasStationMetadata:
    def test_slug(self):
        assert GasStationSimulation().metadata().slug == "gas-station"

    def test_category(self):
        assert GasStationSimulation().metadata().category == "greedy"

    def test_visualization_type(self):
        assert GasStationSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestGasStationCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_start(self, seed: int):
        initial, _, final = run(6, seed=seed)
        gas, cost = parse_instance(initial)
        expected = brute_force_start(gas, cost)
        actual = int(final.description.split("= ")[1])
        assert actual == expected, (
            f"seed={seed}: gas={gas}, cost={cost}, expected={expected}, got={actual}"
        )

    @pytest.mark.parametrize("seed", range(10))
    def test_can_complete_circuit(self, seed: int):
        initial, _, final = run(6, seed=seed)
        gas, cost = parse_instance(initial)
        start = int(final.description.split("= ")[1])
        n = len(gas)
        tank = 0
        for step in range(n):
            i = (start + step) % n
            tank += gas[i] - cost[i]
            assert tank >= 0, f"Tank depleted at step {step} (station {i})"

    def test_has_frames(self):
        _, frames, _ = run(6)
        assert len(frames) == 6


class TestGasStationFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
