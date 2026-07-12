"""Targeted fix for edit-distance's 39/40 Function Mode test-case gap
(mission Phase 17's "40-test-corpus invariant").

Root cause, found via evidence (not guessed): the problem's own declared
constraint is `0 <= word1.length, word2.length <= 500` -- an EMPTY word is
explicitly valid input -- but the shipped Python starter code parses stdin
with bare `sys.stdin.read().split()`, which (whitespace-split) SILENTLY
DROPS empty tokens. For the one hidden case exercising an empty word
(`input_data = '\\na'`, i.e. word1="", word2="a"), `.split()` returns
`["a"]`, so `lines[1]` raises IndexError -- a REAL user's correct solution,
written against this exact starter code, would crash on this valid hidden
test case. This is why scripts/migrate_atlascode_function_mode.py's
argument-capture step silently produced no row for this case (the capture
harness's `except BaseException: pass` swallowed the same IndexError) --
not a Function Mode-only gap, a genuine pre-existing Program Mode bug.

Fix: split on '\\n' instead of whitespace (input_data is always exactly
`word1 + "\\n" + word2` with no trailing newline -- confirmed against all
40 stored input_data rows), which preserves empty tokens and still parses
every other case identically. Then backfill the one missing test row's
function_args/function_expected from its already-committed
input_data/expected_output (never re-derived).

No family Python source module generates this legacy problem's starter
code (confirmed via repo-wide search) -- the DB is the only place this
lives, so this script edits it directly, the same pattern already used for
the fractional-knapsack/remove-k-digits contract fixes.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    row = con.execute("SELECT starter_code FROM problems WHERE id='edit-distance'").fetchone()
    starter = json.loads(row[0])
    old_py = starter["python"]
    if "sys.stdin.read().split()" not in old_py:
        raise SystemExit(f"expected pattern not found -- starter code changed since this script was written:\n{old_py}")
    new_py = old_py.replace("sys.stdin.read().split()", "sys.stdin.read().split('\\n')")
    starter["python"] = new_py
    con.execute("UPDATE problems SET starter_code=? WHERE id='edit-distance'", (json.dumps(starter),))

    rows = con.execute(
        "SELECT id, input_data, expected_output FROM test_cases "
        "WHERE problem_id='edit-distance' AND function_args IS NULL"
    ).fetchall()
    for tid, input_data, expected_output in rows:
        w1, w2 = input_data.split("\n")
        con.execute(
            "UPDATE test_cases SET function_args=?, function_expected=? WHERE id=?",
            (json.dumps({"w1": w1, "w2": w2}), json.dumps(int(expected_output)), tid),
        )
    con.commit()
    n = con.execute(
        "SELECT COUNT(*) FROM test_cases WHERE problem_id='edit-distance' AND function_args IS NOT NULL"
    ).fetchone()[0]
    con.close()
    print(f"starter code fixed (split() -> split('\\n')); backfilled {len(rows)} row(s)")
    print(f"edit-distance function-mode test rows now: {n}/40")


if __name__ == "__main__":
    main()
