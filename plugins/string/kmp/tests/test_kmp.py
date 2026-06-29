"""Tests for KMP string search plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "kmp_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
KMPSimulation = _mod.KMPSimulation
_build_failure = _mod._build_failure

from algorithm_atlas_sdk import SimulationParams


def run(text_length: int = 20, seed: int = 42):
    sim = KMPSimulation()
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


class TestKMPMetadata:
    def test_slug(self):
        assert KMPSimulation().metadata().slug == "kmp"

    def test_category(self):
        assert KMPSimulation().metadata().category == "string"

    def test_visualization_type(self):
        assert KMPSimulation().metadata().visualization_type == "ARRAY_BARS_SEARCH"


class TestKMPFailureFunction:
    def test_all_same_chars(self):
        f = _build_failure("AAAA")
        assert f == [0, 1, 2, 3]

    def test_no_prefix_suffix(self):
        f = _build_failure("ABCD")
        assert f == [0, 0, 0, 0]

    def test_partial_repeat(self):
        f = _build_failure("ABABC")
        assert f[2] == 1  # "AB" prefix = "AB" suffix length 1 (only "A" works for pos 2)
        assert f[3] == 2  # "ABAB" — "AB" is both prefix and suffix

    def test_single_char(self):
        f = _build_failure("A")
        assert f == [0]


class TestKMPCorrectness:
    def test_found_result(self):
        # Brute-force verify: if found_at is not None, text[found_at:found_at+m] == pattern
        for seed in range(20):
            initial, _, final = run(20, seed=seed)
            text = "".join(chr(c) for c in initial.array)
            pattern = get_pattern(initial)
            if final.found_at is not None:
                assert text[final.found_at:final.found_at + len(pattern)] == pattern, (
                    f"seed={seed}: found_at={final.found_at} but text[{final.found_at}:{final.found_at+len(pattern)}]={text[final.found_at:final.found_at+len(pattern)]} != pattern={pattern}"
                )

    def test_not_found_result(self):
        # If not found, pattern genuinely not in text
        for seed in range(20):
            initial, _, final = run(20, seed=seed)
            if final.found_at is None:
                text = "".join(chr(c) for c in initial.array)
                pattern = get_pattern(initial)
                assert pattern not in text, f"seed={seed}: found_at=None but '{pattern}' in '{text}'"

    def test_no_frames_when_empty(self):
        # Edge case: very short text
        initial, frames, final = run(16)
        assert len(frames) > 0

    def test_found_at_consistent_with_naive(self):
        for seed in range(30):
            initial, _, final = run(20, seed=seed)
            text = "".join(chr(c) for c in initial.array)
            pattern = get_pattern(initial)
            naive_pos = text.find(pattern)
            if naive_pos == -1:
                assert final.found_at is None
            else:
                assert final.found_at == naive_pos


class TestKMPFrames:
    def test_has_frames(self):
        _, frames, _ = run(20)
        assert len(frames) > 0

    def test_serializable(self):
        import json
        initial, frames, final = run(20)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_clamp_min(self):
        sim = KMPSimulation()
        p = SimulationParams(seed=0, inputs={"text_length": 1}, config={})
        s = sim.initialize(p)
        assert len(s.array) == 16  # min=16

    def test_clamp_max(self):
        sim = KMPSimulation()
        p = SimulationParams(seed=0, inputs={"text_length": 99}, config={})
        s = sim.initialize(p)
        assert len(s.array) == 32  # max=32
