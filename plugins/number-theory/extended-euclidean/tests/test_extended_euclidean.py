"""Tests for Extended Euclidean Algorithm plugin."""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "extended_euclidean",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ExtendedEuclideanSimulation = _mod.ExtendedEuclideanSimulation

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 42):
    sim = ExtendedEuclideanSimulation()
    params = SimulationParams(seed=seed, inputs={"array_size": 5}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestExtGCDMetadata:
    def test_slug(self):
        assert ExtendedEuclideanSimulation().metadata().slug == "extended-euclidean"

    def test_category(self):
        assert ExtendedEuclideanSimulation().metadata().category == "number-theory"

    def test_visualization_type(self):
        assert ExtendedEuclideanSimulation().metadata().visualization_type == "MATRIX"


class TestExtGCDCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_gcd(self, seed: int):
        initial, _, final = run(seed)
        inner = initial.description[7:-1]
        a, b = [int(x) for x in inner.split(",")]
        expected_gcd = math.gcd(a, b)
        actual_gcd = int(final.description.split("=")[1].split(";")[0])
        assert actual_gcd == expected_gcd

    @pytest.mark.parametrize("seed", range(10))
    def test_bezout_identity(self, seed: int):
        """Verify ax + by = gcd(a,b)."""
        initial, _, final = run(seed)
        inner = initial.description[7:-1]
        a, b = [int(x) for x in inner.split(",")]
        # Parse: "Done: GCD(a,b)=g; a×(x) + b×(y) = g"
        gcd_part = final.description.split(";")[0]
        gcd = int(gcd_part.split("=")[-1])
        coeff_part = final.description.split(";")[1]
        # Extract x from "a×(x)"
        x_str = coeff_part.split("×(")[1].split(")")[0]
        y_str = coeff_part.split("×(")[2].split(")")[0]
        x, y = int(x_str), int(y_str)
        assert a * x + b * y == gcd, (
            f"seed={seed}: {a}×({x}) + {b}×({y}) = {a*x+b*y} ≠ {gcd}"
        )

    def test_table_has_4_rows(self):
        initial, _, _ = run(42)
        assert len(initial.table) == 4

    def test_has_frames(self):
        _, frames, _ = run(42)
        assert len(frames) > 0


class TestExtGCDFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(42)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_descriptions_mention_step(self):
        _, frames, _ = run(42)
        for f in frames:
            assert "Step" in f.description
