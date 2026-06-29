"""Tests for Decision Tree Entropy plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "decision_tree_entropy", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
DecisionTreeEntropySimulation = _mod.DecisionTreeEntropySimulation
_entropy = _mod._entropy
_info_gain = _mod._info_gain

from algorithm_atlas_sdk import SimulationParams


def run(n=12, seed=0):
    sim = DecisionTreeEntropySimulation()
    params = SimulationParams(seed=seed, inputs={"sample_count": n}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestDecisionTreeEntropyMetadata:
    def test_slug(self):
        assert DecisionTreeEntropySimulation().metadata().slug == "decision-tree-entropy"

    def test_category(self):
        assert DecisionTreeEntropySimulation().metadata().category == "machine-learning"


class TestEntropyFunction:
    def test_pure_class_zero(self):
        assert _entropy([0, 0, 0]) == 0.0

    def test_pure_class_one(self):
        assert _entropy([1, 1, 1]) == 0.0

    def test_max_entropy_balanced(self):
        assert abs(_entropy([0, 1]) - 1.0) < 1e-9


class TestDecisionTreeEntropyCorrectness:
    @pytest.mark.parametrize("seed", range(6))
    def test_best_split_in_middle(self, seed: int):
        """Best threshold should be between 42 and 58 (the two cluster boundaries)."""
        _, _, final = run(12, seed)
        thresh = final.swaps
        assert 40 <= thresh <= 60, f"Expected split near 50, got {thresh}"

    @pytest.mark.parametrize("seed", range(6))
    def test_ig_positive(self, seed: int):
        import re
        _, _, final = run(12, seed)
        ig = float(re.search(r"IG=([\d.]+)", final.description).group(1))
        assert ig > 0

    def test_has_frames(self):
        _, frames, _ = run(12)
        assert len(frames) > 0


class TestDecisionTreeEntropyFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run()
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
