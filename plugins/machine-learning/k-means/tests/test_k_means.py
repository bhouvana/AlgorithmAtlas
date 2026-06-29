"""Tests for K-Means plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "k_means", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
KMeansSimulation = _mod.KMeansSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n=12, k=3, seed=0):
    sim = KMeansSimulation()
    params = SimulationParams(seed=seed, inputs={"point_count": n, "k": k}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestKMeansMetadata:
    def test_slug(self):
        assert KMeansSimulation().metadata().slug == "k-means"

    def test_category(self):
        assert KMeansSimulation().metadata().category == "machine-learning"


class TestKMeansCorrectness:
    @pytest.mark.parametrize("seed", range(6))
    def test_converges(self, seed: int):
        _, _, final = run(12, 3, seed)
        assert "Converged" in final.description

    @pytest.mark.parametrize("k", [2, 3, 4])
    def test_k_clusters(self, k: int):
        _, _, final = run(12, k, seed=0)
        assert f"centroids=" in final.description

    def test_has_frames(self):
        _, frames, _ = run()
        assert len(frames) > 0


class TestKMeansFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run()
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
