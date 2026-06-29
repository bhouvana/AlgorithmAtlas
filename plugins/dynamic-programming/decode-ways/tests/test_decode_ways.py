"""Tests for Decode Ways plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "decode_ways",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
DecodeWaysSimulation = _mod.DecodeWaysSimulation
_INSTANCES = _mod._INSTANCES

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = DecodeWaysSimulation()
    params = SimulationParams(seed=seed, inputs={}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestDecodeWaysMetadata:
    def test_slug(self):
        assert DecodeWaysSimulation().metadata().slug == "decode-ways"

    def test_category(self):
        assert DecodeWaysSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert DecodeWaysSimulation().metadata().visualization_type == "MATRIX"


class TestDecodeWaysCorrectness:
    @pytest.mark.parametrize("seed", range(len(_INSTANCES)))
    def test_correct_count(self, seed: int):
        s, expected = _INSTANCES[seed]
        initial, _, final = run(seed)
        result = int(final.description.split(" = ")[1])
        assert result == expected, f"seed={seed}: '{s}' expected {expected}, got {result}"

    def test_has_frames(self):
        _, frames, _ = run(0)
        assert len(frames) >= 2

    def test_table_has_2_rows(self):
        initial, _, _ = run(0)
        assert len(initial.table) == 2


class TestDecodeWaysFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_frame_count_equals_n_plus_1(self):
        seed = 1  # "226" → n=3
        _, frames, _ = run(seed)
        s = _INSTANCES[seed][0]
        # 1 base frame + n-1 fill frames = n frames
        assert len(frames) == len(s)
