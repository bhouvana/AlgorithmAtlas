"""Tests for Suffix Array plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "suffix_array",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
SuffixArraySimulation = _mod.SuffixArraySimulation
_build_suffix_array = _mod._build_suffix_array

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 7, seed: int = 0):
    sim = SuffixArraySimulation()
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


class TestSuffixArrayMetadata:
    def test_slug(self):
        assert SuffixArraySimulation().metadata().slug == "suffix-array"

    def test_category(self):
        assert SuffixArraySimulation().metadata().category == "string"

    def test_visualization_type(self):
        assert SuffixArraySimulation().metadata().visualization_type == "MATRIX"


class TestSuffixArrayCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_suffix_array(self, seed: int):
        initial, _, final = run(7, seed)
        s = initial.description.split("'")[1]
        expected_sa = _build_suffix_array(s)
        result_sa = list(map(int, final.description.split("= [")[1].rstrip("]").split(", ")))
        assert result_sa == expected_sa, f"seed={seed}: '{s}' expected {expected_sa}, got {result_sa}"

    def test_has_n_frames(self):
        initial, frames, _ = run(7)
        n = len(initial.table)
        assert len(frames) == n

    @pytest.mark.parametrize("seed", range(10))
    def test_sorted_suffixes_order(self, seed: int):
        initial, _, final = run(7, seed)
        s = initial.description.split("'")[1]
        sa = list(map(int, final.description.split("= [")[1].rstrip("]").split(", ")))
        suffixes = [s[i:] for i in sa]
        assert suffixes == sorted(suffixes)


class TestSuffixArrayFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(7)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_table_is_n_by_n(self):
        initial, _, _ = run(7)
        n = len(initial.table)
        assert n == 7
        for row in initial.table:
            assert len(row) == 7
