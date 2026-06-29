"""
WireWorld — Algorithm Atlas Plugin

WireWorld is a cellular automaton designed to simulate digital logic circuits.
There are four cell states:

  0 = empty    (never changes)
  1 = conductor (wire)
  2 = electron head (front of signal — blue)
  3 = electron tail (back of signal — red)

Transition rules (applied simultaneously):
  empty      → empty
  head       → tail
  tail       → conductor
  conductor  → head  if exactly 1 or 2 of the 8 neighbors are electron heads
             → conductor  otherwise

A simple loop circuit is initialized with a rectangle of conductors
and two electron head/tail pairs placed to create a moving pulse.
"""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    CellularAutomataState,
    SimulationParams,
)

EMPTY = 0
CONDUCTOR = 1
HEAD = 2
TAIL = 3


class WireWorld:
    """WireWorld digital-circuit cellular automaton."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="wireworld",
            name="WireWorld",
            category="cellular-automata",
            visualization_type="PARTICLE_FIELD",
            description=(
                "WireWorld is a cellular automaton designed by Brian Silverman in 1987 "
                "to simulate digital electronic circuits. Electron signals (head/tail pairs) "
                "travel along conductor wires, and wire junctions can function as AND/OR "
                "gates, enabling construction of Turing-complete logic circuits."
            ),
            intuition=(
                "Just four cell states and three simple rules produce a system powerful "
                "enough to build logic gates, memory, and even a working computer. "
                "Watch electron signals loop endlessly around the circuit."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n²)",
            tags=("cellular-automata", "circuit", "simulation", "logic", "digital"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CellularAutomataState:
        n = int(params.inputs.get("n", 30))

        grid = [[EMPTY] * n for _ in range(n)]

        # Draw a rectangular loop of conductors
        # Outer rectangle: rows 5..24, cols 5..24 on a 30×30 grid
        # Scale to fit any n (min n=15 to be safe)
        margin = max(3, n // 6)
        top    = margin
        bottom = n - margin - 1
        left   = margin
        right  = n - margin - 1

        for r in range(n):
            for c in range(n):
                on_top    = (r == top    and left  <= c <= right)
                on_bottom = (r == bottom and left  <= c <= right)
                on_left   = (c == left   and top   <= r <= bottom)
                on_right  = (c == right  and top   <= r <= bottom)
                if on_top or on_bottom or on_left or on_right:
                    grid[r][c] = CONDUCTOR

        # Place an electron head and tail on the top wire to start a signal
        # Head moves rightward along the top row
        grid[top][left + 2] = HEAD
        grid[top][left + 1] = TAIL

        # Place a second signal on the bottom wire moving leftward
        grid[bottom][right - 2] = HEAD
        grid[bottom][right - 1] = TAIL

        g = tuple(tuple(row) for row in grid)
        conductors = sum(cell == CONDUCTOR for row in g for cell in row)
        heads = sum(cell == HEAD for row in g for cell in row)

        return CellularAutomataState(
            grid=g,
            width=n,
            height=n,
            generation=0,
            alive_count=heads,
            description=f"WireWorld — {conductors} wire cells, {heads} electron head(s)",
        )

    def steps(
        self,
        state: CellularAutomataState,
    ) -> Generator[CellularAutomataState, None, None]:
        n = state.width
        grid = [list(row) for row in state.grid]
        max_steps = 100

        for step in range(1, max_steps + 1):
            new_grid = [[EMPTY] * n for _ in range(n)]
            for r in range(n):
                for c in range(n):
                    cell = grid[r][c]
                    if cell == EMPTY:
                        new_grid[r][c] = EMPTY
                    elif cell == HEAD:
                        new_grid[r][c] = TAIL
                    elif cell == TAIL:
                        new_grid[r][c] = CONDUCTOR
                    else:  # CONDUCTOR
                        # Count neighboring electron heads
                        head_count = 0
                        for dr in (-1, 0, 1):
                            for dc in (-1, 0, 1):
                                if dr == 0 and dc == 0:
                                    continue
                                nr, nc = r + dr, c + dc
                                if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == HEAD:
                                    head_count += 1
                        if head_count in (1, 2):
                            new_grid[r][c] = HEAD
                        else:
                            new_grid[r][c] = CONDUCTOR

            grid = new_grid
            heads = sum(cell == HEAD for row in grid for cell in row)
            yield CellularAutomataState(
                grid=tuple(tuple(row) for row in grid),
                width=n,
                height=n,
                generation=step,
                alive_count=heads,
                description=f"WireWorld step {step} — {heads} electron head(s) active",
            )
