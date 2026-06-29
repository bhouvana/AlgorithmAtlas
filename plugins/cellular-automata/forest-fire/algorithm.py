"""
Forest Fire Model — Algorithm Atlas Plugin

A stochastic cellular automaton modeling wildfire spread.

Cell states:
  0 = empty ground
  1 = tree (healthy)
  2 = burning tree (fire)

Rules applied simultaneously each step:
  - Burning cell → becomes empty (ash)
  - Tree with at least one burning neighbor → catches fire
  - Empty cell → grows a tree with probability p
  - Tree with no burning neighbors → spontaneously ignites with probability f (lightning)

Determinism: seed is passed via SimulationParams and forwarded through initialize
so that steps() re-seeds from it consistently.
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

EMPTY = 0
TREE = 1
BURNING = 2


class ForestFire:
    """Forest Fire stochastic cellular automaton."""

    # Store seed so steps() can reproduce deterministically
    _seed: int = 0

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="forest-fire",
            name="Forest Fire Model",
            category="cellular-automata",
            visualization_type="PARTICLE_FIELD",
            description=(
                "The Forest Fire model is a stochastic cellular automaton simulating "
                "the cycle of forest growth and wildfire. Trees grow on empty ground "
                "with probability p, spread fire to neighbors when burning, and can be "
                "spontaneously ignited by lightning with probability f."
            ),
            intuition=(
                "The model reaches a self-organized critical state where forest density "
                "and fire frequency balance. Small p and tiny f produce lush forests with "
                "rare but large fires; large f produces frequent small fires."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n²)",
            tags=("cellular-automata", "stochastic", "simulation", "fire", "ecology"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CellularAutomataState:
        n = int(params.inputs.get("n", 30))
        self._seed = params.seed
        rng = random.Random(params.seed)

        # Start with a dense forest
        grid = tuple(
            tuple(TREE if rng.random() < 0.6 else EMPTY for _ in range(n))
            for _ in range(n)
        )
        trees = sum(cell == TREE for row in grid for cell in row)

        return CellularAutomataState(
            grid=grid,
            width=n,
            height=n,
            generation=0,
            alive_count=trees,
            description=f"Initial forest — {trees} trees",
        )

    def steps(
        self,
        state: CellularAutomataState,
    ) -> Generator[CellularAutomataState, None, None]:
        n = state.width
        params_p = 0.05   # probability of new tree growth
        params_f = 0.001  # probability of lightning strike

        # Re-seed from the stored seed offset by n² to skip initialization draws
        rng = random.Random(self._seed ^ 0xDEADBEEF)

        grid = [list(row) for row in state.grid]
        max_steps = 200

        for step in range(1, max_steps + 1):
            new_grid = [[EMPTY] * n for _ in range(n)]
            for r in range(n):
                for c in range(n):
                    cell = grid[r][c]
                    if cell == BURNING:
                        new_grid[r][c] = EMPTY
                    elif cell == TREE:
                        # Check 4-connected neighbors for fire
                        on_fire = False
                        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == BURNING:
                                on_fire = True
                                break
                        if on_fire or rng.random() < params_f:
                            new_grid[r][c] = BURNING
                        else:
                            new_grid[r][c] = TREE
                    else:  # EMPTY
                        new_grid[r][c] = TREE if rng.random() < params_p else EMPTY

            grid = new_grid
            trees = sum(cell == TREE for row in grid for cell in row)
            burning = sum(cell == BURNING for row in grid for cell in row)

            yield CellularAutomataState(
                grid=tuple(tuple(row) for row in grid),
                width=n,
                height=n,
                generation=step,
                alive_count=trees,
                description=f"Step {step} — {trees} trees, {burning} burning",
            )
