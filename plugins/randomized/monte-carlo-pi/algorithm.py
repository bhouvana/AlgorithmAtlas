"""Monte Carlo π Estimation plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    GridState,
    SimulationParams,
)

GRID_SIZE = 20
CELL_EMPTY  = 0
CELL_INSIDE = 6   # CELL_PATH — dart inside circle
CELL_OUTSIDE = 1  # CELL_WALL — dart outside circle
CELL_ARC    = 4   # CELL_OPEN — quarter-circle boundary


def _make_grid_state(inside_pts, outside_pts):
    g = [[CELL_EMPTY] * GRID_SIZE for _ in range(GRID_SIZE)]
    # Draw quarter-circle arc (r=GRID_SIZE-1)
    r = GRID_SIZE - 1
    for col in range(GRID_SIZE):
        row_arc = GRID_SIZE - 1 - int((r**2 - col**2) ** 0.5)
        if 0 <= row_arc < GRID_SIZE:
            g[row_arc][col] = CELL_ARC
    for (row, col) in outside_pts:
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            g[row][col] = CELL_OUTSIDE
    for (row, col) in inside_pts:
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            g[row][col] = CELL_INSIDE
    return tuple(tuple(row) for row in g)


class MonteCarloPiSimulation(AlgorithmPlugin):
    """Monte Carlo estimation of π."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="monte-carlo-pi",
            name="Monte Carlo π Estimation",
            category="randomized",
            visualization_type="GRID",
            description="Estimate π by counting random darts that land inside a quarter-circle.",
            intuition=(
                "Throw n darts uniformly at random in [0,1]×[0,1]. "
                "Count how many satisfy x²+y²≤1 (inside quarter-circle). "
                "π ≈ 4 × inside/total."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(1)",
            tags=("randomized", "monte-carlo", "pi", "probability"),
        )

    def initialize(self, params: SimulationParams) -> GridState:
        n = int(params.inputs.get("dart_count", 80))
        grid = _make_grid_state([], [])
        return GridState(
            grid=grid,
            current=None,
            path=tuple(),
            description=f"Monte Carlo π: throwing {n} darts seed={params.seed}",
        )

    def steps(self, initial_state: GridState) -> Generator[GridState, None, GridState]:
        import re
        desc = initial_state.description
        n = int(re.search(r"throwing (\d+)", desc).group(1))
        seed_val = int(re.search(r"seed=(\d+)", desc).group(1))
        rng = random.Random(seed_val)

        inside_pts = []
        outside_pts = []
        inside_count = 0

        step_size = max(1, n // 40)

        for i in range(1, n + 1):
            x = rng.random()
            y = rng.random()
            hit = (x * x + y * y) <= 1.0
            row = GRID_SIZE - 1 - int(y * (GRID_SIZE - 1))
            col = int(x * (GRID_SIZE - 1))
            row = max(0, min(GRID_SIZE - 1, row))
            col = max(0, min(GRID_SIZE - 1, col))

            if hit:
                inside_count += 1
                inside_pts.append((row, col))
            else:
                outside_pts.append((row, col))

            if i % step_size == 0 or i == n:
                pi_est = 4.0 * inside_count / i
                yield GridState(
                    grid=_make_grid_state(inside_pts, outside_pts),
                    current=(row, col),
                    path=tuple(),
                    description=f"Dart {i}/{n}: inside={inside_count} π≈{pi_est:.4f}",
                )

        pi_est = 4.0 * inside_count / n
        return GridState(
            grid=_make_grid_state(inside_pts, outside_pts),
            current=None,
            path=tuple(),
            description=f"π ≈ {pi_est:.4f} (inside={inside_count}/{n}, true π≈3.1416)",
        )
