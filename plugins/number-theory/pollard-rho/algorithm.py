"""Pollard's Rho Factorization plugin for Algorithm Atlas."""
from __future__ import annotations

import math
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

# Good composite numbers for demonstration (not prime, not too large)
_COMPOSITES = [77, 91, 57, 85, 51, 65, 69, 87, 93, 95]


def _f(x, n, c=1):
    return (x * x + c) % n


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _pollard_steps(n, c=1):
    """Returns list of (tortoise, hare, gcd_val) steps until non-trivial factor found."""
    for c_try in range(1, 10):
        steps = []
        x = 2
        y = 2
        d = 1
        for _ in range(200):  # limit iterations
            x = _f(x, n, c_try)
            y = _f(_f(y, n, c_try), n, c_try)
            d = _gcd(abs(x - y), n)
            steps.append((x, y, d))
            if d != 1:
                break
        if 1 < d < n:
            return steps, d
    # Fallback: trial division
    for i in range(2, n):
        if n % i == 0:
            return [(i, i, i)], i
    return [(n, n, n)], n


class PollardRhoSimulation(AlgorithmPlugin):
    """Pollard's rho factorization visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="pollard-rho",
            name="Pollard's Rho Factorization",
            category="number-theory",
            visualization_type="ARRAY_BARS",
            description="Factor composite n using Pollard's rho + Floyd cycle detection.",
            intuition=(
                "x = f(x), y = f(f(y)) (tortoise and hare). "
                "gcd(|x-y|, n) reveals a factor when they cycle "
                "in the same residue class mod a prime factor of n."
            ),
            complexity_time_best="O(n^(1/4))",
            complexity_time_average="O(n^(1/4))",
            complexity_time_worst="O(n^(1/2))",
            complexity_space="O(1)",
            tags=("number-theory", "factorization", "pollard-rho", "gcd", "cycle-detection"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        n = int(params.inputs.get("size", 77))
        # Ensure n is composite and in valid range
        if n < 10 or n > 99:
            n = 77
        # Prefer from our curated list
        if n not in _COMPOSITES:
            n = _COMPOSITES[params.seed % len(_COMPOSITES)]
        steps, _ = _pollard_steps(n)
        arr = tuple(1 for _ in steps)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=n,
            description=f"PollardRho n={n}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        n = int(re.search(r"n=(\d+)", initial_state.description).group(1))
        steps_log, factor = _pollard_steps(n)

        for idx, (x, y, d) in enumerate(steps_log):
            # Array: [x mod n, y mod n, d] scaled to bars
            arr_vals = [x, y, d if d > 1 else 1]
            # Pad to fixed length
            while len(arr_vals) < max(3, idx + 1):
                arr_vals.append(1)
            arr_vals = arr_vals[:max(3, len(steps_log))]
            arr_vals[idx % len(arr_vals)] = x
            mx = max(arr_vals) or 1
            arr = tuple(max(1, min(99, v * 99 // mx)) for v in arr_vals)

            yield SortState(
                array=arr,
                comparing=(idx % len(arr), idx % len(arr)),
                last_swap=(idx % len(arr), idx % len(arr)) if d > 1 else None,
                sorted_indices=frozenset(range(idx + 1)) if d > 1 else frozenset(range(idx)),
                comparisons=idx + 1,
                swaps=d if d > 1 else 0,
                description=f"Step {idx+1}: x={x} y={y} gcd={d}",
            )

        other = n // factor
        return SortState(
            array=initial_state.array,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(len(steps_log))),
            comparisons=len(steps_log),
            swaps=factor,
            description=f"{n} = {factor} × {other} (found in {len(steps_log)} steps)",
        )
