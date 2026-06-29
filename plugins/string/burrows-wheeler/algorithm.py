"""Burrows-Wheeler Transform plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

_INPUT = "banana$"   # sentinel '$' must be lexicographically smallest


def _bwt(s):
    n = len(s)
    rotations = sorted(s[i:] + s[:i] for i in range(n))
    bwt_out = "".join(r[-1] for r in rotations)
    orig_idx = rotations.index(s)
    return bwt_out, rotations, orig_idx


def _lf_map(bwt_out):
    first_col = sorted(bwt_out)
    char_start: dict = {}
    idx = 0
    for ch in sorted(set(first_col)):
        char_start[ch] = idx
        idx += first_col.count(ch)
    lf = [0] * len(bwt_out)
    cnt: dict = {}
    for i, ch in enumerate(bwt_out):
        cnt[ch] = cnt.get(ch, 0)
        lf[i] = char_start[ch] + cnt[ch]
        cnt[ch] += 1
    return lf


def _ibwt(bwt_out, orig_idx):
    """Reconstruct original string from BWT and original row index."""
    lf = _lf_map(bwt_out)
    result: List[str] = []
    row = orig_idx
    for _ in range(len(bwt_out)):
        result.append(bwt_out[row])
        row = lf[row]
    result.reverse()
    return "".join(result)


# Pre-compute for use in visualization
_BWT_OUT, _ROTATIONS_SORTED, _ORIG_IDX = _bwt(_INPUT)


class BurrowsWheelerSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="burrows-wheeler",
            name="Burrows-Wheeler Transform",
            category="string",
            visualization_type="MATRIX",
            description="Compute the BWT of a string by sorting cyclic rotations, then recover the original via inverse BWT.",
            intuition=(
                "Sort all n cyclic rotations. The last column is the BWT — "
                "it groups repeated characters for compression. "
                "The inverse uses the LF-mapping to trace characters from the "
                "last column back to the original string in O(n)."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n²)",
            tags=("string", "burrows-wheeler", "bwt", "compression", "transform"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        n = len(_INPUT)
        rotations_unsorted = tuple(_INPUT[i:] + _INPUT[:i] for i in range(n))
        return DPState(
            table=rotations_unsorted,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"Input: \"{_INPUT}\" — {n} rotations to sort",
        )

    def steps(self, initial_state: DPState) -> Generator[DPState, None, DPState]:
        s = _INPUT
        n = len(s)
        computed: set = set()

        rotations_unsorted = [s[i:] + s[:i] for i in range(n)]

        # Phase 1: generate rotations
        for i, rot in enumerate(rotations_unsorted):
            computed.add((i, 0))
            yield DPState(
                table=tuple(rotations_unsorted),
                current_cell=(i, 0),
                computed_cells=frozenset(computed),
                description=f"Rotation {i}: \"{rot}\"",
            )

        # Phase 2: sort rotations
        rotations_sorted = sorted(rotations_unsorted)
        for i in range(n):
            computed.add((i, n - 1))
        yield DPState(
            table=tuple(rotations_sorted),
            current_cell=None,
            computed_cells=frozenset(computed),
            description="Rotations sorted lexicographically",
        )

        # Phase 3: extract BWT (last column)
        bwt_out = "".join(r[-1] for r in rotations_sorted)
        orig_idx = rotations_sorted.index(s)
        for i in range(n):
            yield DPState(
                table=tuple(rotations_sorted),
                current_cell=(i, n - 1),
                computed_cells=frozenset(computed),
                description=f"BWT[{i}] = '{rotations_sorted[i][-1]}' (last char of row {i})",
            )

        yield DPState(
            table=tuple(rotations_sorted),
            current_cell=(orig_idx, n - 1),
            computed_cells=frozenset(computed),
            description=f"Forward BWT = \"{bwt_out}\"  (original at row {orig_idx})",
        )

        # Phase 4: inverse BWT via LF-mapping
        lf = _lf_map(bwt_out)
        result: List[str] = []
        row = orig_idx
        for step in range(n):
            ch = bwt_out[row]
            result.append(ch)
            next_row = lf[row]
            yield DPState(
                table=tuple(rotations_sorted),
                current_cell=(row, n - 1),
                computed_cells=frozenset(computed),
                description=(
                    f"InvBWT step {step+1}: L[{row}]='{ch}' "
                    f"→ next row {next_row}  (collected={len(result)} chars)"
                ),
            )
            row = next_row

        recovered = "".join(reversed(result))

        final = DPState(
            table=tuple(rotations_sorted),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"BWT=\"{bwt_out}\" → inverse → \"{recovered}\"",
        )
        yield final
        return final
