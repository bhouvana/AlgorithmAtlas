"""
Wolfram Rule 30 — Algorithm Atlas Plugin

A 1D elementary cellular automaton discovered by Stephen Wolfram.
Rule 30 produces chaotic, seemingly random output from a single live cell.
Each row in the n×n grid represents one generation evolving from the row above.
The rule number encodes which 3-cell neighborhood patterns produce a live cell.

Rule 30 in binary: 00011110
Pattern:  111 110 101 100 011 010 001 000
Output:     0   0   0   1   1   1   1   0
"""
from __future__ import annotations

from typing import Generator, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    CellularAutomataState,
    SimulationParams,
)

RULE_NUMBER = 30
RULE_TABLE = {
    (i >> 2) & 1: None  # placeholder; built below
    for i in range(8)
}
# Build rule lookup: maps (left, center, right) -> next state
_RULE_TABLE = {
    ((i >> 2) & 1, (i >> 1) & 1, i & 1): (RULE_NUMBER >> i) & 1
    for i in range(8)
}


class Rule30:
    """Wolfram Rule 30 — 1D elementary cellular automaton."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="rule-30",
            name="Wolfram Rule 30",
            category="cellular-automata",
            visualization_type="PARTICLE_FIELD",
            description=(
                "Wolfram Rule 30 is an elementary 1D cellular automaton that generates "
                "chaotic output from a single live center cell. Each row is a new "
                "generation computed from the row above using a fixed 3-cell neighborhood "
                "rule. The pattern is so unpredictable it has been used as a random "
                "number generator."
            ),
            intuition=(
                "Despite having only one rule table, Rule 30 produces output that passes "
                "randomness tests — illustrating how simple local rules can yield global "
                "complexity. The middle column alone approximates a random bit sequence."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n²)",
            tags=("cellular-automata", "wolfram", "1d", "chaos", "simulation"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CellularAutomataState:
        n = int(params.inputs.get("n", 50))

        # Build the full n×n grid: row 0 = seed, subsequent rows computed on yield
        first_row = [0] * n
        first_row[n // 2] = 1

        grid = tuple(tuple(first_row if r == 0 else (0,) * n) for r in range(n))

        return CellularAutomataState(
            grid=grid,
            width=n,
            height=n,
            generation=0,
            alive_count=1,
            description="Rule 30 — generation 0, single center cell",
        )

    def steps(
        self,
        state: CellularAutomataState,
    ) -> Generator[CellularAutomataState, None, None]:
        n = state.width
        # Reconstruct rows as lists for mutation
        rows: list[list[int]] = [list(state.grid[0])]

        for gen in range(1, n):
            prev = rows[gen - 1]
            new_row = [0] * n
            for c in range(n):
                left = prev[(c - 1) % n]
                center = prev[c]
                right = prev[(c + 1) % n]
                new_row[c] = _RULE_TABLE[(left, center, right)]
            rows.append(new_row)

            # Rebuild full grid showing all rows computed so far (rest remain zero)
            grid_rows = [tuple(rows[r]) for r in range(gen + 1)]
            # Pad remaining rows with zeros
            zero_row = tuple([0] * n)
            while len(grid_rows) < n:
                grid_rows.append(zero_row)

            alive = sum(new_row)
            yield CellularAutomataState(
                grid=tuple(grid_rows),
                width=n,
                height=n,
                generation=gen,
                alive_count=alive,
                description=f"Rule 30 — generation {gen}, row alive cells: {alive}",
            )
