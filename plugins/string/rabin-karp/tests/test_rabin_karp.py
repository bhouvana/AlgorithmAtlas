"""Tests for Rabin-Karp rolling-hash string search plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "rabin_karp_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
RabinKarpSimulation = _mod.RabinKarpSimulation
_hash = _mod._hash
_roll = _mod._roll
_BASE = _mod._BASE
_MOD = _mod._MOD

from algorithm_atlas_sdk import SimulationParams


def run(text_length: int = 20, seed: int = 42):
    sim = RabinKarpSimulation()
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


class TestRabinKarpMetadata:
    def test_slug(self):
        assert RabinKarpSimulation().metadata().slug == "rabin-karp"

    def test_category(self):
        assert RabinKarpSimulation().metadata().category == "string"

    def test_visualization_type(self):
        assert RabinKarpSimulation().metadata().visualization_type == "ARRAY_BARS_SEARCH"


class TestRollingHash:
    def test_hash_deterministic(self):
        assert _hash("ABC") == _hash("ABC")

    def test_different_strings_different_hashes(self):
        # Not guaranteed, but very likely for short strings
        assert _hash("ABC") != _hash("ABD")

    def test_roll_consistent(self):
        # rolling "ABCD"[1:4] should equal _hash("BCD")
        text = "ABCDE"
        m = 3
        h = _hash(text[:m])
        high_power = pow(_BASE, m - 1, _MOD)
        h2 = _roll(h, text[0], text[m], high_power)
        assert h2 == _hash(text[1:m + 1])


class TestRabinKarpCorrectness:
    def test_found_result_correct(self):
        for seed in range(20):
            initial, _, final = run(20, seed=seed)
            text = "".join(chr(c) for c in initial.array)
            pattern = get_pattern(initial)
            if final.found_at is not None:
                assert text[final.found_at:final.found_at + len(pattern)] == pattern

    def test_not_found_means_absent(self):
        for seed in range(20):
            initial, _, final = run(20, seed=seed)
            if final.found_at is None:
                text = "".join(chr(c) for c in initial.array)
                pattern = get_pattern(initial)
                assert pattern not in text

    def test_found_at_matches_naive(self):
        for seed in range(30):
            initial, _, final = run(20, seed=seed)
            text = "".join(chr(c) for c in initial.array)
            pattern = get_pattern(initial)
            naive = text.find(pattern)
            if naive == -1:
                assert final.found_at is None
            else:
                assert final.found_at == naive


class TestRabinKarpFrames:
    def test_has_frames(self):
        _, frames, _ = run(20)
        assert len(frames) > 0

    def test_frame_count_bounded(self):
        initial, frames, _ = run(20)
        n = len(initial.array)
        pattern = get_pattern(initial)
        m = len(pattern)
        # At most n-m+1 window frames
        assert len(frames) <= n - m + 2

    def test_serializable(self):
        import json
        initial, frames, final = run(20)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_clamp_min(self):
        sim = RabinKarpSimulation()
        p = SimulationParams(seed=0, inputs={"text_length": 1}, config={})
        s = sim.initialize(p)
        assert len(s.array) == 16

    def test_clamp_max(self):
        sim = RabinKarpSimulation()
        p = SimulationParams(seed=0, inputs={"text_length": 99}, config={})
        s = sim.initialize(p)
        assert len(s.array) == 32
