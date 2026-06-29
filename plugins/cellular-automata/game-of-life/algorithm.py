"""
Conway's Game of Life — Algorithm Atlas Plugin

Classic 2D cellular automaton with four simple rules:
1. A live cell with <2 live neighbors dies (underpopulation).
2. A live cell with 2-3 live neighbors survives.
3. A live cell with >3 live neighbors dies (overpopulation).
4. A dead cell with exactly 3 live neighbors becomes alive (reproduction).
"""
from __future__ import annotations

import random
from typing import Generator, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    CellularAutomataState,
    SimulationParams,
)


class GameOfLife:
    """Conway's Game of Life simulation."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="game-of-life",
            name="Conway's Game of Life",
            category="cellular-automata",
            visualization_type="PARTICLE_FIELD",
            description=(
                "Conway's Game of Life is a zero-player cellular automaton devised by "
                "mathematician John Conway in 1970. Starting from an initial seed "
                "configuration, the grid evolves through discrete generations according "
                "to four simple rules based on each cell's eight neighbors."
            ),
            intuition=(
                "Complex, lifelike patterns emerge from four deceptively simple rules. "
                "Stable structures, oscillators, and 'gliders' that move across the grid "
                "all arise spontaneously from random initial conditions."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n²)",
            tags=("cellular-automata", "simulation", "emergent", "2d", "classic"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CellularAutomataState:
        n = int(params.inputs.get("n", 30))
        density = float(params.inputs.get("density", 0.3))
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
            description=f"Initial state — {alive} live cells ({density:.0%} density)",
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
                    neighbors = 0
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = (r + dr) % n, (c + dc) % n
                            neighbors += grid[nr][nc]
                    cell = grid[r][c]
                    if cell == 1 and neighbors in (2, 3):
                        new_grid[r][c] = 1
                    elif cell == 0 and neighbors == 3:
                        new_grid[r][c] = 1
                    else:
                        new_grid[r][c] = 0
            grid = new_grid
            alive = sum(cell for row in grid for cell in row)
            yield CellularAutomataState(
                grid=tuple(tuple(row) for row in grid),
                width=n,
                height=n,
                generation=gen,
                alive_count=alive,
                description=f"Generation {gen} — {alive} live cells",
            )
