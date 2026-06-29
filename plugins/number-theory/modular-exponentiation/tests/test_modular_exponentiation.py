"""Tests for Modular Exponentiation plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "modular_exp",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ModularExponentiationSimulation = _mod.ModularExponentiationSimulation

from algorithm_atlas_sdk import SimulationParams


def run(bits: int = 8, seed: int = 42):
    sim = ModularExponentiationSimulation()
    params = SimulationParams(seed=seed, inputs={"array_size": bits}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestModExpMetadata:
    def test_slug(self):
        assert ModularExponentiationSimulation().metadata().slug == "modular-exponentiation"

    def test_category(self):
        assert ModularExponentiationSimulation().metadata().category == "number-theory"

    def test_visualization_type(self):
        assert ModularExponentiationSimulation().metadata().visualization_type == "MATRIX"


class TestModExpCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_result(self, seed: int):
        initial, _, final = run(8, seed=seed)
        desc0 = initial.description
        inner = desc0[7:-1]
        parts = inner.split(",")
        base, exp, mod = int(parts[0]), int(parts[1]), int(parts[2])
        expected = pow(base, exp, mod)
        actual = int(final.description.split("= ")[-1])
        assert actual == expected, (
            f"seed={seed}: {base}^{exp} mod {mod}: expected={expected}, got={actual}"
        )

    def test_table_has_2_rows(self):
        initial, _, _ = run(8)
        assert len(initial.table) == 2

    def test_row0_is_decreasing(self):
        initial, _, _ = run(8)
        row0 = list(initial.table[0])
        assert row0 == sorted(row0, reverse=True)

    def test_all_cells_computed(self):
        initial, _, final = run(8)
        k = len(initial.table[0])
        assert len(final.computed_cells) == k

    def test_result_in_range(self):
        for seed in range(5):
            initial, _, final = run(8, seed=seed)
            inner = initial.description[7:-1]
            parts = inner.split(",")
            mod = int(parts[2])
            result = int(final.description.split("= ")[-1])
            assert 0 <= result < mod


class TestModExpFrames:
    def test_has_frames(self):
        _, frames, _ = run(8)
        assert len(frames) > 0

    def test_frame_count_equals_bits(self):
        initial, frames, _ = run(8)
        k = len(initial.table[0])
        assert len(frames) == k

    def test_serializable(self):
        import json
        initial, frames, final = run(8)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_descriptions_mention_bit(self):
        _, frames, _ = run(8)
        for f in frames:
            assert "bit[" in f.description
