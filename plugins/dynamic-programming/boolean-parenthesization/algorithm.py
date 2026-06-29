"""Boolean Parenthesization DP plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

# Boolean expression: T & F | T ^ F  (4 operands, 3 operators)
_SYMS = [True, False, True, False]   # operand values
_OPS  = ["&",  "|",  "^"]           # operators between operands
_N    = len(_SYMS)


def _combine(lt, lf, op, rt, rf):
    """Return (true_ways, false_ways) when combining left and right with op."""
    if op == "&":
        t = lt * rt
    elif op == "|":
        t = lt * rt + lt * rf + lf * rt
    else:  # "^"
        t = lt * rf + lf * rt
    total = (lt + lf) * (rt + rf)
    return t, total - t


class BooleanParenthesizationSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="boolean-parenthesization",
            name="Boolean Parenthesization",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Count parenthesizations of a boolean expression that evaluate to True.",
            intuition=(
                "dp_true[i][j] = ways to make operands i..j evaluate to True. "
                "For each split k, combine dp_true[i][k] and dp_true[k+1][j] "
                "according to operator ops[k]."
            ),
            complexity_time_best="O(n³)",
            complexity_time_average="O(n³)",
            complexity_time_worst="O(n³)",
            complexity_space="O(n²)",
            tags=("dynamic-programming", "boolean", "parenthesization", "counting", "classic"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        t = [[0] * _N for _ in range(_N)]
        f = [[0] * _N for _ in range(_N)]
        for i in range(_N):
            t[i][i] = 1 if _SYMS[i] else 0
            f[i][i] = 0 if _SYMS[i] else 1
        sym_str = " ".join(("T" if s else "F") for s in _SYMS)
        op_str = " ".join(_OPS)
        return DPState(
            table=tuple(tuple(row) for row in t),
            current_cell=None,
            computed_cells=frozenset((i, i) for i in range(_N)),
            description=f"expr: {sym_str}  ops: {op_str}",
        )

    def steps(self, initial_state: DPState) -> Generator[DPState, None, DPState]:
        t = [[0] * _N for _ in range(_N)]
        f = [[0] * _N for _ in range(_N)]
        for i in range(_N):
            t[i][i] = 1 if _SYMS[i] else 0
            f[i][i] = 0 if _SYMS[i] else 1

        computed: set = {(i, i) for i in range(_N)}

        for i in range(_N):
            yield DPState(
                table=tuple(tuple(row) for row in t),
                current_cell=(i, i),
                computed_cells=frozenset(computed),
                description=f"Base: operand {i} = {'T' if _SYMS[i] else 'F'} → true={t[i][i]}",
            )

        for length in range(2, _N + 1):
            for i in range(_N - length + 1):
                j = i + length - 1
                for k in range(i, j):
                    op = _OPS[k]
                    add_t, add_f = _combine(t[i][k], f[i][k], op, t[k + 1][j], f[k + 1][j])
                    t[i][j] += add_t
                    f[i][j] += add_f
                    yield DPState(
                        table=tuple(tuple(row) for row in t),
                        current_cell=(i, j),
                        computed_cells=frozenset(computed),
                        description=(
                            f"dp[{i}][{j}] split at {k} (op='{op}'): "
                            f"+{add_t} true ways → total true={t[i][j]}"
                        ),
                    )
                computed.add((i, j))
                yield DPState(
                    table=tuple(tuple(row) for row in t),
                    current_cell=(i, j),
                    computed_cells=frozenset(computed),
                    description=f"dp_true[{i}][{j}] = {t[i][j]}  dp_false[{i}][{j}] = {f[i][j]}",
                )

        final = DPState(
            table=tuple(tuple(row) for row in t),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Total ways to evaluate True = {t[0][_N - 1]}",
        )
        yield final
        return final
