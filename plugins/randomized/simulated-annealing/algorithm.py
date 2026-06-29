"""Simulated Annealing plugin for Algorithm Atlas."""
from __future__ import annotations

import math
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

# Multi-modal energy landscape: E(x) = sin(x/3)*40 + sin(x/7)*20 + x/2, x in [0,99]
# Has global min near x=70-80 range (varies with seed, so we use a fixed landscape)
_N = 50          # landscape width
_T0 = 100.0      # initial temperature
_ALPHA = 0.85    # cooling factor
_STEPS = 30      # total steps to yield


def _energy(x: int) -> float:
    """Multi-modal landscape with global minimum near x=40."""
    return math.sin(x * 0.3) * 35 + math.sin(x * 0.7 + 1) * 20 + (x - 25) ** 2 * 0.03


def _build_landscape() -> tuple:
    vals = [_energy(x) for x in range(_N)]
    mn, mx = min(vals), max(vals)
    scaled = tuple(max(1, min(99, int((v - mn) / (mx - mn + 1e-9) * 98) + 1)) for v in vals)
    return scaled


_LANDSCAPE = _build_landscape()


class SimulatedAnnealingSimulation(AlgorithmPlugin):
    """Simulated annealing for 1D multi-modal function minimization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="simulated-annealing",
            name="Simulated Annealing",
            category="randomized",
            visualization_type="ARRAY_BARS",
            description="Minimize a multi-modal 1D energy landscape using simulated annealing.",
            intuition=(
                "Start at random position with high temperature. "
                "Accept uphill moves with probability e^(-ΔE/T). "
                "As T decreases, only downhill moves accepted — finds global minimum."
            ),
            complexity_time_best="O(iters)",
            complexity_time_average="O(iters)",
            complexity_time_worst="O(iters)",
            complexity_space="O(n)",
            tags=("randomized", "simulated-annealing", "optimization", "metaheuristic"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        import random
        rng = random.Random(params.seed)
        x0 = rng.randint(0, _N - 1)
        return SortState(
            array=_LANDSCAPE,
            comparing=(x0, x0),
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"SA: x={x0} E={_energy(x0):.2f} T={_T0:.1f} seed={params.seed}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        import random
        desc = initial_state.description
        x = int(re.search(r"x=(\d+)", desc).group(1))
        seed = int(re.search(r"seed=(\d+)", desc).group(1))

        rng = random.Random(seed + 99)
        T = _T0
        best_x = x
        best_E = _energy(x)
        accepted = 0

        for step in range(_STEPS):
            # Propose neighbor: step size shrinks with temperature
            step_size = max(1, int(T / 10))
            delta = rng.randint(-step_size, step_size)
            x_new = max(0, min(_N - 1, x + delta))
            E_cur = _energy(x)
            E_new = _energy(x_new)
            dE = E_new - E_cur

            accepted_move = False
            if dE < 0 or rng.random() < math.exp(-dE / max(T, 0.01)):
                x = x_new
                accepted_move = True
                accepted += 1

            if _energy(x) < best_E:
                best_E = _energy(x)
                best_x = x

            T *= _ALPHA

            yield SortState(
                array=_LANDSCAPE,
                comparing=(x, x),
                last_swap=(best_x, best_x) if accepted_move else None,
                sorted_indices=frozenset([best_x]),
                comparisons=step + 1,
                swaps=accepted,
                description=(
                    f"Step {step + 1}: x={x} E={_energy(x):.2f} "
                    f"T={T:.2f} best={best_x}(E={best_E:.2f}) "
                    f"{'accepted' if accepted_move else 'rejected'}"
                ),
            )

        return SortState(
            array=_LANDSCAPE,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset([best_x]),
            comparisons=_STEPS,
            swaps=accepted,
            description=(
                f"Done: best x={best_x} E={best_E:.2f} (T={T:.3f}) "
                f"{accepted}/{_STEPS} accepted"
            ),
        )
