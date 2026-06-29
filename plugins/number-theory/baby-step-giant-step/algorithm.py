"""Baby-Step Giant-Step (discrete log) plugin for Algorithm Atlas."""
from __future__ import annotations

import math
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

# Problems: find x such that g^x ≡ h (mod p) — all verified to have solutions
# g is a primitive root in each case
_PROBLEMS = [
    (22, 7, 41),   # 7^x ≡ 22 (mod 41): x=11  (ord(7)=40)
    (15, 2, 53),   # 2^x ≡ 15 (mod 53): x=12  (ord(2)=52)
    (9, 5, 23),    # 5^x ≡ 9  (mod 23): x=10  (ord(5)=22)
    (24, 2, 37),   # 2^x ≡ 24 (mod 37): x=29  (ord(2)=36)
    (10, 3, 31),   # 3^x ≡ 10 (mod 31): x=14  (ord(3)=30)
]


def _bsgs(h, g, p):
    """Returns (x, baby_steps, giant_steps, m) where g^x ≡ h (mod p)."""
    m = math.ceil(math.sqrt(p))
    # Baby steps: table[h * g^j mod p] = j
    table = {}
    val = h % p
    baby_steps = [(val, 0)]
    table[val] = 0
    gj = 1
    for j in range(1, m + 1):
        gj = (gj * g) % p
        val = (h * gj) % p
        baby_steps.append((val, j))
        if val not in table:
            table[val] = j

    # Giant steps: compute g^(im) for i=1..m
    gm = pow(g, m, p)
    gim = gm
    giant_steps = []
    for i in range(1, m + 1):
        giant_steps.append((gim, i))
        if gim in table:
            j = table[gim]
            x = i * m - j
            return x, baby_steps, giant_steps, m
        gim = (gim * gm) % p

    return None, baby_steps, giant_steps, m


class BabyStepGiantStepSimulation(AlgorithmPlugin):
    """Baby-step Giant-step discrete log visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="baby-step-giant-step",
            name="Baby-Step Giant-Step",
            category="number-theory",
            visualization_type="ARRAY_BARS",
            description="Solve discrete log g^x ≡ h (mod p) in O(√p).",
            intuition=(
                "Baby steps: build table of h·g^j mod p for j=0..√p. "
                "Giant steps: compute g^(i·√p) mod p, look up in table. "
                "Match means x = i·√p - j."
            ),
            complexity_time_best="O(√p)",
            complexity_time_average="O(√p)",
            complexity_time_worst="O(√p)",
            complexity_space="O(√p)",
            tags=("number-theory", "discrete-logarithm", "baby-step-giant-step"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        h, g, p = _PROBLEMS[params.seed % len(_PROBLEMS)]
        m = math.ceil(math.sqrt(p))
        arr = tuple(1 for _ in range(m))
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"BSGS h={h} g={g} p={p}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        h = int(re.search(r"h=(\d+)", initial_state.description).group(1))
        g = int(re.search(r"g=(\d+)", initial_state.description).group(1))
        p = int(re.search(r"p=(\d+)", initial_state.description).group(1))

        x, baby_steps, giant_steps, m = _bsgs(h, g, p)

        # Show baby steps phase
        table_vals = []
        for j, (val, idx) in enumerate(baby_steps[:m]):
            table_vals.append(val)
            mx = max(table_vals) or 1
            arr = tuple(max(1, min(99, v * 99 // mx)) for v in table_vals) + \
                  tuple(1 for _ in range(m - len(table_vals)))
            yield SortState(
                array=arr,
                comparing=(j, j),
                last_swap=None,
                sorted_indices=frozenset(range(j + 1)),
                comparisons=j + 1,
                swaps=val,
                description=f"Baby step {j}: h·g^{j} mod {p} = {val}",
            )

        # Show giant steps phase
        for idx, (gim, i) in enumerate(giant_steps):
            mx = max(gim, max(table_vals)) or 1
            arr_vals = table_vals[:]
            matched = gim in {v for v, _ in baby_steps}
            arr = tuple(max(1, min(99, v * 99 // mx)) for v in arr_vals)
            found = i * m - baby_steps[0][1]  # placeholder

            yield SortState(
                array=arr,
                comparing=(idx % m, idx % m),
                last_swap=(idx % m, idx % m) if matched else None,
                sorted_indices=frozenset(range(m)) if matched else frozenset(range(len(table_vals))),
                comparisons=m + idx + 1,
                swaps=x if (matched and x is not None) else gim,
                description=f"Giant step {i}: g^({i}·{m}) mod {p} = {gim}" + (" → MATCH!" if matched else ""),
            )
            if matched:
                break

        if x is not None:
            verify = pow(g, x, p)
            return SortState(
                array=initial_state.array,
                comparing=None,
                last_swap=None,
                sorted_indices=frozenset(range(m)),
                comparisons=m + len(giant_steps),
                swaps=x,
                description=f"Solution: {g}^{x} ≡ {h} (mod {p}). Verify: {g}^{x} mod {p} = {verify}",
            )
        return SortState(
            array=initial_state.array,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=m + len(giant_steps),
            swaps=-1,
            description=f"No solution found for {g}^x ≡ {h} (mod {p})",
        )
