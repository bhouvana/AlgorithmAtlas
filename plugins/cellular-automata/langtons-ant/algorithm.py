"""
Langton's Ant — Algorithm Atlas Plugin

A 2D Turing machine with a very simple rule:
  - On a white (0) cell: turn right 90°, flip cell to black (1), move forward.
  - On a black (1) cell: turn left 90°, flip cell to white (0), move forward.

Despite the simplicity, after ~10,000 steps the ant builds an emergent
"highway" — a diagonal corridor that repeats indefinitely.

Direction encoding:
  0 = North (up,    row--)
  1 = East  (right, col++)
  2 = South (down,  row++)
  3 = West  (left,  col--)
"""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    CellularAutomataState,
    SimulationParams,
)

# Direction → (row_delta, col_delta)
_DR = (-1, 0, 1, 0)
_DC = (0, 1, 0, -1)
_DIR_NAMES = ("N", "E", "S", "W")


class LangtonsAnt:
    """Langton's Ant cellular automaton."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="langtons-ant",
            name="Langton's Ant",
            category="cellular-automata",
            visualization_type="PARTICLE_FIELD",
            description=(
                "Langton's Ant is a 2D Turing machine where an ant moves on a grid of "
                "black and white cells following two rules: turn right and flip on white, "
                "turn left and flip on black. After ~10,000 chaotic steps, the ant "
                "spontaneously constructs a diagonal highway pattern that repeats forever."
            ),
            intuition=(
                "The first ~10,000 steps look random and chaotic, then without warning "
                "the ant locks into a perfectly regular 'highway'. This sudden emergence "
                "of order from chaos is a famous example of self-organization."
            ),
            complexity_time_best="O(steps)",
            complexity_time_average="O(steps)",
            complexity_time_worst="O(steps)",
            complexity_space="O(n²)",
            tags=("cellular-automata", "turing-machine", "emergent", "simulation"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CellularAutomataState:
        n = int(params.inputs.get("n", 60))

        grid = tuple(tuple(0 for _ in range(n)) for _ in range(n))

        return CellularAutomataState(
            grid=grid,
            width=n,
            height=n,
            generation=0,
            alive_count=0,
            description=f"Step 0 — ant at ({n//2},{n//2}) facing N",
        )

    def steps(
        self,
        state: CellularAutomataState,
    ) -> Generator[CellularAutomataState, None, None]:
        n = state.width
        grid = [list(row) for row in state.grid]

        ant_r = n // 2
        ant_c = n // 2
        direction = 0  # North

        total_steps = 12000
        yield_every = 50

        for step in range(1, total_steps + 1):
            # Read current cell
            cell = grid[ant_r][ant_c]

            if cell == 0:  # White: turn right, flip to black
                direction = (direction + 1) % 4
                grid[ant_r][ant_c] = 1
            else:          # Black: turn left, flip to white
                direction = (direction - 1) % 4
                grid[ant_r][ant_c] = 0

            # Move forward (wrap at boundaries)
            ant_r = (ant_r + _DR[direction]) % n
            ant_c = (ant_c + _DC[direction]) % n

            if step % yield_every == 0:
                # Mark ant position as value 2 for visualization
                vis_grid = [list(row) for row in grid]
                ant_was = vis_grid[ant_r][ant_c]
                vis_grid[ant_r][ant_c] = 2

                black_cells = sum(cell == 1 for row in grid for cell in row)
                yield CellularAutomataState(
                    grid=tuple(tuple(row) for row in vis_grid),
                    width=n,
                    height=n,
                    generation=step,
                    alive_count=black_cells,
                    description=(
                        f"Step {step} — ant at ({ant_r},{ant_c}) "
                        f"facing {_DIR_NAMES[direction]}, {black_cells} black cells"
                    ),
                )
                # Restore ant cell to actual value
                vis_grid[ant_r][ant_c] = ant_was
