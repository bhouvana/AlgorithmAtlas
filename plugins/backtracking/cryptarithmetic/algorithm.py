"""Cryptarithmetic (SEND+MORE=MONEY) plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

# SEND + MORE = MONEY
# Letters: S E N D M O R Y
_LETTERS = list("SENDMORY")  # 8 unique letters
_LEADING = {"S", "M"}        # cannot be 0

# Solution: S=9 E=5 N=6 D=7 M=1 O=0 R=8 Y=2
_SOLUTION = {"S": 9, "E": 5, "N": 6, "D": 7, "M": 1, "O": 0, "R": 8, "Y": 2}


def _check(assign):
    """True if SEND + MORE = MONEY under assignment."""
    S, E, N, D = assign["S"], assign["E"], assign["N"], assign["D"]
    M, O, R, Y = assign["M"], assign["O"], assign["R"], assign["Y"]
    SEND = 1000*S + 100*E + 10*N + D
    MORE = 1000*M + 100*O + 10*R + E
    MONEY = 10000*M + 1000*O + 100*N + 10*E + Y
    return SEND + MORE == MONEY


def _solve_steps():
    """Backtracking solver that logs assignment states."""
    steps = []
    letters = _LETTERS
    assign = {}
    used = set()

    def backtrack(idx):
        if idx == len(letters):
            if _check(assign):
                steps.append((dict(assign), True))
                return True
            return False

        letter = letters[idx]
        for digit in range(10):
            if digit in used:
                continue
            if digit == 0 and letter in _LEADING:
                continue
            assign[letter] = digit
            used.add(digit)
            steps.append((dict(assign), False))
            if backtrack(idx + 1):
                return True
            used.remove(digit)
            del assign[letter]
        return False

    backtrack(0)
    return steps


# Pre-compute steps at import time to avoid recomputing each call
_STEPS_CACHE = None


def _get_steps():
    global _STEPS_CACHE
    if _STEPS_CACHE is None:
        _STEPS_CACHE = _solve_steps()
    return _STEPS_CACHE


class CryptarithmeticSimulation(AlgorithmPlugin):
    """SEND + MORE = MONEY cryptarithmetic solver."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="cryptarithmetic",
            name="Cryptarithmetic",
            category="backtracking",
            visualization_type="ARRAY_BARS",
            description="Solve SEND + MORE = MONEY by assigning digits to letters.",
            intuition=(
                "Assign digits 0-9 to letters S,E,N,D,M,O,R,Y (all unique). "
                "Backtrack when constraint violated. "
                "Solution: S=9 E=5 N=6 D=7 M=1 O=0 R=8 Y=2."
            ),
            complexity_time_best="O(10!)",
            complexity_time_average="O(10!)",
            complexity_time_worst="O(10!)",
            complexity_space="O(letters)",
            tags=("backtracking", "cryptarithmetic", "constraint-satisfaction", "search"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        # Array = 8 bars, one per letter, value = assigned digit (or 0 if unassigned)
        arr = tuple(0 for _ in _LETTERS)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description="Cryptarithmetic: SEND+MORE=MONEY",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        all_steps = _get_steps()
        # Subsample to at most 30 representative steps to keep visualization manageable
        total = len(all_steps)
        if total > 30:
            indices = [int(i * (total - 1) / 29) for i in range(29)] + [total - 1]
        else:
            indices = list(range(total))

        for step_idx in indices:
            assign, is_solution = all_steps[step_idx]
            arr = tuple(assign.get(L, 0) * 10 for L in _LETTERS)
            arr = tuple(max(1, min(99, v)) if v > 0 else 1 for v in arr)
            assigned_count = len(assign)
            yield SortState(
                array=arr,
                comparing=(assigned_count - 1, assigned_count - 1) if assign else None,
                last_swap=(assigned_count - 1, assigned_count - 1) if is_solution else None,
                sorted_indices=frozenset(range(assigned_count)) if is_solution else frozenset(),
                comparisons=step_idx + 1,
                swaps=assigned_count,
                description=(
                    "SOLUTION FOUND! " + " ".join(f"{L}={assign[L]}" for L in _LETTERS if L in assign)
                    if is_solution else
                    " ".join(f"{L}={assign[L]}" for L in _LETTERS if L in assign) or "Searching..."
                ),
            )

        # Final: solution
        sol = _SOLUTION
        arr = tuple(sol[L] * 10 for L in _LETTERS)
        arr = tuple(max(1, min(99, v)) for v in arr)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(len(_LETTERS))),
            comparisons=total,
            swaps=len(_LETTERS),
            description="SEND=9567 MORE=1085 MONEY=10652",
        )
