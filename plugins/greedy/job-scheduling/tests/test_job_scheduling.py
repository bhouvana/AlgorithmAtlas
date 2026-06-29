"""Tests for Job Scheduling (Deadline) plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import List, Tuple

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "job_scheduling",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
JobSchedulingSimulation = _mod.JobSchedulingSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 6, seed: int = 42):
    sim = JobSchedulingSimulation()
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


def brute_force_max_profit(profits: List[int], deadlines: List[int]) -> int:
    """Brute-force: try all subsets, find feasible schedule with max profit."""
    n = len(profits)
    max_deadline = max(deadlines)
    best = 0
    for mask in range(1 << n):
        jobs = [(profits[i], deadlines[i]) for i in range(n) if mask & (1 << i)]
        # Check feasibility by greedy slot assignment
        slots = [-1] * (max_deadline + 1)
        total = 0
        for profit, deadline in sorted(jobs, key=lambda x: -x[0]):
            for t in range(min(deadline, max_deadline), 0, -1):
                if slots[t] == -1:
                    slots[t] = 1
                    total += profit
                    break
            else:
                total = -1
                break
        if total > best:
            best = total
    return best


class TestJobSchedulingMetadata:
    def test_slug(self):
        assert JobSchedulingSimulation().metadata().slug == "job-scheduling"

    def test_category(self):
        assert JobSchedulingSimulation().metadata().category == "greedy"

    def test_visualization_type(self):
        assert JobSchedulingSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestJobSchedulingCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_correct_max_profit(self, seed: int):
        initial, _, final = run(6, seed=seed)
        profits = list(initial.array)
        dl_str = initial.description.split("deadlines=")[1]
        deadlines = [int(x) for x in dl_str.split(",")]

        expected = brute_force_max_profit(profits, deadlines)
        actual = int(final.description.split("total profit = ")[1])
        assert actual == expected, (
            f"seed={seed}: profits={profits}, deadlines={deadlines}, "
            f"expected={expected}, got={actual}"
        )

    def test_profits_sorted_descending(self):
        initial, _, _ = run(6)
        profits = list(initial.array)
        assert profits == sorted(profits, reverse=True)

    def test_scheduled_count_leq_n(self):
        initial, _, final = run(6)
        scheduled = int(final.description.split(": ")[1].split(" jobs")[0])
        assert scheduled <= len(initial.array)

    def test_has_frames(self):
        _, frames, _ = run(6)
        assert len(frames) == 6  # one per job


class TestJobSchedulingFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_comparisons_track_profit(self):
        """comparisons field tracks total profit accumulated."""
        _, frames, final = run(6)
        # comparisons in final should equal total profit
        assert final.comparisons == int(final.description.split("total profit = ")[1])
