"""
Wolfram Rule 110 — Algorithm Atlas Plugin

A 1D elementary cellular automaton proven to be Turing complete.
Rule 110 exhibits complex behavior at the boundary between order and chaos,
producing structured glider-like patterns rather than pure randomness.

Rule 110 in binary: 01101110
Pattern:  111 110 101 100 011 010 001 000
Output:     0   1   1   0   1   1   1   0
"""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    CellularAutomataState,
    SimulationParams,
)

RULE_NUMBER = 110
_RULE_TABLE = {
    ((i >> 2) & 1, (i >> 1) & 1, i & 1): (RULE_NUMBER >> i) & 1
    for i in range(8)
}


class Rule110:
    """Wolfram Rule 110 — Turing-complete 1D cellular automaton."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="rule-110",
            name="Wolfram Rule 110",
            category="cellular-automata",
            visualization_type="PARTICLE_FIELD",
            description=(
                "Wolfram Rule 110 is an elementary 1D cellular automaton proven to be "
                "Turing complete by Matthew Cook in 1994. It produces complex, structured "
                "patterns with glider-like structures that interact in non-trivial ways. "
                "Each row represents one generation computed from the row above."
            ),
            intuition=(
                "Rule 110 sits at the edge of chaos — more structured than Rule 30 yet "
                "complex enough for universal computation. Repeating triangular structures "
                "and moving patterns emerge that interact like particles."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n²)",
            tags=("cellular-automata", "wolfram", "1d", "turing-complete", "simulation"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CellularAutomataState:
        n = int(params.inputs.get("n", 50))

        first_row = [0] * n
        first_row[n // 2] = 1

        grid = tuple(tuple(first_row if r == 0 else (0,) * n) for r in range(n))

        return CellularAutomataState(
            grid=grid,
            width=n,
            height=n,
            generation=0,
            alive_count=1,
            description="Rule 110 — generation 0, single center cell",
        )

    def steps(
        self,
        state: CellularAutomataState,
    ) -> Generator[CellularAutomataState, None, None]:
        n = state.width
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

            grid_rows = [tuple(rows[r]) for r in range(gen + 1)]
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
                description=f"Rule 110 — generation {gen}, row alive cells: {alive}",
            )
