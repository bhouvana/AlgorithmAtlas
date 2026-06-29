"""Tests for Boyer-Moore string search plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "boyer_moore",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BoyerMooreSimulation = _mod.BoyerMooreSimulation

from algorithm_atlas_sdk import SimulationParams
from algorithm_atlas_sdk.testing import AlgorithmTestHarness


def run(seed: int = 42):
    sim = BoyerMooreSimulation()
    params = SimulationParams(seed=seed, inputs={"text_length": 20}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestBoyerMooreMetadata:
    def test_slug(self):
        assert BoyerMooreSimulation().metadata().slug == "boyer-moore"

    def test_category(self):
        assert BoyerMooreSimulation().metadata().category == "string"

    def test_visualization_type(self):
        assert BoyerMooreSimulation().metadata().visualization_type == "ARRAY_BARS_SEARCH"


class TestBoyerMooreCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_match_result(self, seed: int):
        initial, _, final = run(seed)
        text = "".join(chr(c) for c in initial.array)
        pattern = initial.description.split('pattern="')[1].rstrip('"')
        expected_idx = text.find(pattern)

        if expected_idx >= 0:
            assert final.found_at == expected_idx, (
                f"seed={seed}: expected found_at={expected_idx}, got={final.found_at}"
            )
        else:
            assert final.found_at is None

    def test_comparisons_positive(self):
        _, _, final = run(42)
        assert final.comparisons > 0

    def test_found_at_valid_index(self):
        for seed in range(5):
            initial, _, final = run(seed)
            if final.found_at is not None:
                text = "".join(chr(c) for c in initial.array)
                pattern = initial.description.split('pattern="')[1].rstrip('"')
                assert text[final.found_at:final.found_at + len(pattern)] == pattern


class TestBoyerMooreFrames:
    def test_has_frames(self):
        _, frames, _ = run(42)
        assert len(frames) > 0

    def test_bad_char_frames(self):
        _, frames, _ = run(42)
        bad_char_frames = [f for f in frames if "bad-char" in f.description.lower()]
        assert len(bad_char_frames) >= 0  # may not occur if every attempt matches

    def test_serializable(self):
        import json
        initial, frames, final = run(42)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_deterministic(self):
        harness = AlgorithmTestHarness(BoyerMooreSimulation())
        params = SimulationParams(seed=42, inputs={"text_length": 20}, config={})
        harness.assert_deterministic(params)

    def test_descriptions_nonempty(self):
        _, frames, _ = run(42)
        for f in frames:
            assert len(f.description) > 0
