"""Tests for Task Scheduler plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "task_scheduler",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
TaskSchedulerSimulation = _mod.TaskSchedulerSimulation
_max_lateness = _mod._max_lateness

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 6, seed: int = 0):
    sim = TaskSchedulerSimulation()
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


class TestTaskSchedulerMetadata:
    def test_slug(self):
        assert TaskSchedulerSimulation().metadata().slug == "task-scheduler"

    def test_category(self):
        assert TaskSchedulerSimulation().metadata().category == "greedy"

    def test_visualization_type(self):
        assert TaskSchedulerSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestTaskSchedulerCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_max_lateness(self, seed: int):
        initial, _, final = run(6, seed)
        deadlines = list(initial.array)
        expected = _max_lateness(deadlines)
        result = int(final.description.split("= ")[1])
        assert result == expected

    def test_schedule_sorted_by_deadline(self):
        _, _, final = run(6)
        desc = final.description
        # Final array should be sorted
        sim = TaskSchedulerSimulation()
        from algorithm_atlas_sdk import SimulationParams
        params = SimulationParams(seed=0, inputs={"array_size": 6}, config={})
        gen = sim.steps(sim.initialize(params))
        frames = []
        try:
            while True:
                frames.append(next(gen))
        except StopIteration as exc:
            f = exc.value
        assert list(f.array) == sorted(f.array)

    def test_has_frames(self):
        _, frames, _ = run(6)
        assert len(frames) > 0


class TestTaskSchedulerFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
