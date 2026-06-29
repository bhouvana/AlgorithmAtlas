"""Tests for Meeting Rooms plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import List, Tuple

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "meeting_rooms",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
MeetingRoomsSimulation = _mod.MeetingRoomsSimulation
_brute_force_rooms = _mod._brute_force_rooms

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 6, seed: int = 42):
    sim = MeetingRoomsSimulation()
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


def parse_meetings(initial_state) -> List[Tuple[int, int]]:
    desc = initial_state.description
    starts_str, ends_str = desc.split("|")
    starts = [int(x) for x in starts_str.split("=")[1].split(",")]
    ends = [int(x) for x in ends_str.split("=")[1].split(",")]
    return list(zip(starts, ends))


class TestMeetingRoomsMetadata:
    def test_slug(self):
        assert MeetingRoomsSimulation().metadata().slug == "meeting-rooms"

    def test_category(self):
        assert MeetingRoomsSimulation().metadata().category == "greedy"

    def test_visualization_type(self):
        assert MeetingRoomsSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestMeetingRoomsCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_correct_min_rooms(self, seed: int):
        initial, _, final = run(6, seed=seed)
        meetings = parse_meetings(initial)
        expected = _brute_force_rooms(meetings)
        actual = int(final.description.split(": ")[1].split(" rooms")[0])
        assert actual == expected, f"seed={seed}: meetings={meetings}, expected={expected}, got={actual}"

    def test_has_frames(self):
        _, frames, _ = run(6)
        assert len(frames) == 6  # one per meeting

    def test_rooms_geq_1(self):
        _, _, final = run(6)
        assert int(final.description.split(": ")[1].split(" rooms")[0]) >= 1


class TestMeetingRoomsFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_swaps_tracks_max_rooms(self):
        """swaps field tracks max rooms needed so far."""
        _, frames, final = run(6)
        max_from_frames = max(f.swaps for f in frames)
        assert final.swaps == max_from_frames
