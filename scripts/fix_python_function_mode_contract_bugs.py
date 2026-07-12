"""Targeted, evidenced fixes for 2 of the 8 real Python Function Mode
failures found by scripts/verify_python_function_mode_bulk.py (mission
Phase 4) -- both are genuine CONTRACT-INFERENCE bugs in the stored DB data,
not verification-harness issues (those are fixed separately in
verify_python_function_mode_bulk.py's build_oracle_wrapper).

1. fractional-knapsack: starter code prints `f'{fn(...):.2f}'` -- a single
   scalar float formatted with an f-string. migrate_atlascode_function_mode's
   classify_return_shape only recognizes a BARE `print(fn(...))` call as
   "scalar"; an f-string wraps the call in a JoinedStr/FormattedValue node,
   which fell through to the generic "contains a call to fn -> array" catch-all.
   Stored contract: return_type=array<float>, test rows: function_expected=[X].
   Correct: return_type=float, function_expected=X (a bare float).

2. remove-k-digits: starter code prints a bare string `print(fn(num, k))`,
   correctly classified as "scalar", but ALL 40 of this problem's committed
   expected_output strings happen to look numeric (digit strings), so
   decide_scalar_kind's int/float/string heuristic (Step 3 in the migration
   script, run purely against output TEXT with no other signal available)
   picked "float" -- losing leading-zero semantics and, for large inputs,
   silently losing precision. The independent oracle
   (independent_oracles.remove_k_digits) returns a real Python `str` by
   design ("Smallest possible number (as a string, no leading zeros)").
   Correct: return_type=string, function_expected=the exact already-stored
   expected_output text (never re-derived -- Phase 18's "the canonical case
   is whatever already produced expected_output").

Both fixes reuse the EXACT already-committed `test_cases.expected_output`
text as the source of truth for the corrected `function_expected` value --
never re-run the oracle to invent a new expected value.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"


def fix_remove_k_digits(con: sqlite3.Connection) -> int:
    contract = json.dumps({
        "function_name": "remove_k_digits",
        "parameters": [
            {"name": "num", "type": {"kind": "string"}},
            {"name": "k", "type": {"kind": "integer"}},
        ],
        "return_type": {"kind": "string"},
    })
    con.execute("UPDATE problems SET function_contract=? WHERE id='remove-k-digits'", (contract,))
    rows = con.execute(
        "SELECT id, expected_output FROM test_cases WHERE problem_id='remove-k-digits'"
    ).fetchall()
    for tid, expected_output in rows:
        con.execute(
            "UPDATE test_cases SET function_expected=? WHERE id=?",
            (json.dumps(expected_output), tid),
        )
    return len(rows)


def fix_fractional_knapsack(con: sqlite3.Connection) -> int:
    contract = json.dumps({
        "function_name": "fractional_knapsack",
        "parameters": [
            {"name": "weights", "type": {"kind": "array", "items": {"kind": "integer"}}},
            {"name": "values", "type": {"kind": "array", "items": {"kind": "integer"}}},
            {"name": "capacity", "type": {"kind": "integer"}},
        ],
        "return_type": {"kind": "float"},
    })
    con.execute("UPDATE problems SET function_contract=? WHERE id='fractional-knapsack'", (contract,))
    rows = con.execute(
        "SELECT id, expected_output FROM test_cases WHERE problem_id='fractional-knapsack'"
    ).fetchall()
    for tid, expected_output in rows:
        con.execute(
            "UPDATE test_cases SET function_expected=? WHERE id=?",
            (json.dumps(float(expected_output)), tid),
        )
    return len(rows)


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    n1 = fix_remove_k_digits(con)
    n2 = fix_fractional_knapsack(con)
    con.commit()
    con.close()
    print(f"remove-k-digits: contract fixed (string), {n1} test rows corrected")
    print(f"fractional-knapsack: contract fixed (float), {n2} test rows corrected")


if __name__ == "__main__":
    main()
