"""
Seeds Automaton (B2/S) — Algorithm Atlas Plugin

The Seeds automaton has one of the simplest birth/survival rules:
  - Birth (B2): A dead cell with exactly 2 live neighbors becomes alive.
  - Survival (S0 / none): No live cell ever survives — all die every generation.

This means every live cell dies each step and only dead cells with exactly
two live neighbors can become alive. The result is explosive, branching
growth patterns that expand outward and never stabilize.
"""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    CellularAutomataState,
    SimulationParams,
)


class Seeds:
    """Seeds (B2/S) cellular automaton."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="seeds",
            name="Seeds Automaton",
            category="cellular-automata",
            visualization_type="PARTICLE_FIELD",
            description=(
                "The Seeds automaton follows the B2/S rule: a dead cell with exactly "
                "2 live neighbors becomes alive, and all live cells die each generation. "
                "Starting from a sparse random seed, it produces explosive, symmetric, "
                "ever-expanding fractal-like growth patterns."
            ),
            intuition=(
                "Because no cell survives, the automaton constantly reinvents itself. "
                "The expanding wavefront creates beautiful fractal symmetries that grow "
                "outward until they wrap around the grid and collide."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n²)",
            tags=("cellular-automata", "simulation", "fractal", "2d", "explosive"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CellularAutomataState:
        n = int(params.inputs.get("n", 30))
        density = float(params.inputs.get("density", 0.05))
        rng = random.Random(params.seed)

        grid = tuple(
            tuple(1 if rng.random() < density else 0 for _ in range(n))
            for _ in range(n)
        )
        alive = sum(cell for row in grid for cell in row)

        return CellularAutomataState(
            grid=grid,
            width=n,
            height=n,
            generation=0,
            alive_count=alive,
            description=f"Seeds initial state — {alive} live cells ({density:.0%} density)",
        )

    def steps(
        self,
        state: CellularAutomataState,
    ) -> Generator[CellularAutomataState, None, None]:
        n = state.width
        grid = [list(row) for row in state.grid]
        max_generations = 200

        for gen in range(1, max_generations + 1):
            new_grid = [[0] * n for _ in range(n)]
            for r in range(n):
                for c in range(n):
                    # Count 8-connected live neighbors
                    neighbors = 0
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = (r + dr) % n, (c + dc) % n
                            neighbors += grid[nr][nc]
                    # B2: dead cell with exactly 2 neighbors → alive
                    # S (none): all live cells die
                    if grid[r][c] == 0 and neighbors == 2:
                        new_grid[r][c] = 1
                    # else: 0 (dead)

            grid = new_grid
            alive = sum(cell for row in grid for cell in row)
            yield CellularAutomataState(
                grid=tuple(tuple(row) for row in grid),
                width=n,
                height=n,
                generation=gen,
                alive_count=alive,
                description=f"Seeds generation {gen} — {alive} live cells",
            )
