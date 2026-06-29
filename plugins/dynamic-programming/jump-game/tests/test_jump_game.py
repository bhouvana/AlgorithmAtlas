"""Tests for Jump Game plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import List

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "jump_game",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
JumpGameSimulation = _mod.JumpGameSimulation

from algorithm_atlas_sdk import SimulationParams

_INF = 999999


def run(n: int = 8, seed: int = 42):
    sim = JumpGameSimulation()
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


def brute_force_min_jumps(arr: List[int]) -> int:
    """BFS to find minimum jumps."""
    from collections import deque
    n = len(arr)
    if n == 1:
        return 0
    dist = [_INF] * n
    dist[0] = 0
    q = deque([0])
    while q:
        i = q.popleft()
        for j in range(i + 1, min(i + arr[i] + 1, n)):
            if dist[j] == _INF:
                dist[j] = dist[i] + 1
                q.append(j)
    return dist[n - 1]


class TestJumpGameMetadata:
    def test_slug(self):
        assert JumpGameSimulation().metadata().slug == "jump-game"

    def test_category(self):
        assert JumpGameSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert JumpGameSimulation().metadata().visualization_type == "MATRIX"


class TestJumpGameCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_min_jumps(self, seed: int):
        initial, _, final = run(8, seed=seed)
        arr = list(initial.table[0])
        expected = brute_force_min_jumps(arr)
        actual = int(final.description.split("= ")[1])
        assert actual == expected, f"seed={seed}: arr={arr}, expected={expected}, got={actual}"

    def test_table_has_2_rows(self):
        initial, _, _ = run(8)
        assert len(initial.table) == 2

    def test_initial_dp0_is_zero(self):
        initial, _, _ = run(8)
        assert initial.table[1][0] == 0

    def test_has_frames(self):
        _, frames, _ = run(8)
        assert len(frames) > 0


class TestJumpGameFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(8)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_dp_monotone(self):
        """dp[i] non-decreasing as i increases."""
        _, _, final = run(8)
        dp = [x for x in final.table[1] if x < _INF]
        for a, b in zip(dp, dp[1:]):
            assert b >= a
