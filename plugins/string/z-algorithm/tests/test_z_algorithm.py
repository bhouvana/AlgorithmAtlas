"""Tests for Z-Algorithm string search plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "z_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ZAlgorithmSimulation = _mod.ZAlgorithmSimulation
_compute_z = _mod._compute_z

from algorithm_atlas_sdk import SimulationParams


def run(text_length: int = 20, seed: int = 42):
    sim = ZAlgorithmSimulation()
    params = SimulationParams(seed=seed, inputs={"text_length": text_length}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


def get_pattern(initial):
    return initial.description.split('pattern="')[1].rstrip('"')


class TestZAlgorithmMetadata:
    def test_slug(self):
        assert ZAlgorithmSimulation().metadata().slug == "z-algorithm"

    def test_category(self):
        assert ZAlgorithmSimulation().metadata().category == "string"

    def test_visualization_type(self):
        assert ZAlgorithmSimulation().metadata().visualization_type == "ARRAY_BARS_SEARCH"


class TestZArray:
    def test_first_element_equals_length(self):
        z = _compute_z("AABAA")
        assert z[0] == 5

    def test_no_prefix_suffix(self):
        z = _compute_z("ABCD")
        assert z[1] == 0
        assert z[2] == 0

    def test_repeated_chars(self):
        z = _compute_z("AAAA")
        assert z[1] == 3
        assert z[2] == 2

    def test_z_function_via_pattern_search(self):
        # "AAA$XAAAY": Z[4]=0, Z[5]=3 → match of length 3 = "AAA" at position 5
        z = _compute_z("AAA$XAAAY")
        assert z[5] == 3  # position 5 is first 'A' of "AAA" in text


class TestZAlgorithmCorrectness:
    @pytest.mark.parametrize("seed", range(20))
    def test_found_at_matches_naive(self, seed: int):
        initial, _, final = run(20, seed=seed)
        text = "".join(chr(c) for c in initial.array)
        pattern = get_pattern(initial)
        naive = text.find(pattern)
        if naive == -1:
            assert final.found_at is None
        else:
            assert final.found_at == naive

    def test_found_at_is_valid(self):
        for seed in range(20):
            initial, _, final = run(20, seed=seed)
            if final.found_at is not None:
                text = "".join(chr(c) for c in initial.array)
                pattern = get_pattern(initial)
                assert text[final.found_at:final.found_at + len(pattern)] == pattern


class TestZAlgorithmFrames:
    def test_has_frames(self):
        _, frames, _ = run(20)
        assert len(frames) > 0

    def test_serializable(self):
        import json
        initial, frames, final = run(20)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_clamp_min(self):
        sim = ZAlgorithmSimulation()
        p = SimulationParams(seed=0, inputs={"text_length": 1}, config={})
        s = sim.initialize(p)
        assert len(s.array) == 16

    def test_clamp_max(self):
        sim = ZAlgorithmSimulation()
        p = SimulationParams(seed=0, inputs={"text_length": 99}, config={})
        s = sim.initialize(p)
        assert len(s.array) == 32
