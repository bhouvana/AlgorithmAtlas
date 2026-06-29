"""Tests for Line Segment Intersection plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "line_segment_intersection", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
LineSegmentIntersectionSimulation = _mod.LineSegmentIntersectionSimulation
_intersects = _mod._intersects
_SEGMENT_PAIRS = _mod._SEGMENT_PAIRS

from algorithm_atlas_sdk import SimulationParams


def run(seed=0):
    sim = LineSegmentIntersectionSimulation()
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


class TestLineSegmentIntersectionMetadata:
    def test_slug(self):
        assert LineSegmentIntersectionSimulation().metadata().slug == "line-segment-intersection"

    def test_category(self):
        assert LineSegmentIntersectionSimulation().metadata().category == "computational-geometry"


class TestLineSegmentIntersectionCorrectness:
    def test_all_cases_correct(self):
        for a, b, c, d, expected in _SEGMENT_PAIRS:
            result = _intersects(a, b, c, d)
            assert result == expected, f"Failed for {a},{b},{c},{d}: expected {expected}"

    @pytest.mark.parametrize("seed", range(len(_SEGMENT_PAIRS)))
    def test_result_matches_expected(self, seed: int):
        initial, _, final = run(seed % len(_SEGMENT_PAIRS))
        expected_str = "YES" if "YES" in initial.description else "NO"
        result_str = "DO" if "DO intersect" in final.description else "do NOT"
        if expected_str == "YES":
            assert "DO intersect" in final.description
        else:
            assert "do NOT" in final.description

    def test_has_frames(self):
        _, frames, _ = run(0)
        assert len(frames) == 4


class TestLineSegmentIntersectionFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
