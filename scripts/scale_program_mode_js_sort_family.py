"""First real Program Mode scaling slice (mission Phase 21-25), proven
end-to-end before attempting the full 16-language x 216-problem build-out.

Program Mode's I/O contract is per-problem free-form stdin/stdout text (not
the uniform typed contract Function Mode has) -- confirmed by reading all 21
sort problems' EXISTING Python starter_code directly: every one uses the
identical convention "first token n, then n whitespace-separated ints,
mutate in place, print space-joined result" (verified by inspection, not
assumed from one example). This script:

  1. Generates a REAL JavaScript Program Mode starter for each of the 21
     sort problems, matching that exact convention (same stdin tokenization,
     same output join), and saves it into problems.starter_code["javascript"]
     (additive JSON merge -- never touches the existing "python" key).
  2. Builds a correct + a genuinely-wrong (descending sort) full JS PROGRAM
     for each problem.
  3. Runs both through the REAL Program Mode judge
     (submission.evaluator.evaluate), against the REAL persisted
     test_cases.input_data/expected_output text corpus -- never function_args
     (that's Function Mode's separate typed corpus).
  4. Records mode="program" Level 6 in the ledger only for genuine
     all-pass + wrong-rejected results.

This is deliberately scoped to ONE language x ONE well-understood problem
family, not all 16 languages x 216 problems -- Program Mode's per-problem
I/O format needs to be confirmed uniform (or handled per-shape) before any
broader generator is built; forcing this to all 216 problems now would risk
generating starters for I/O shapes never actually inspected.
"""
from __future__ import annotations

import asyncio
import json
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))
sys.path.insert(0, str(Path(__file__).parent))
import logging
logging.disable(logging.CRITICAL)

from algorithm_atlas.submission.evaluator import evaluate

import atlascode_ledger as ledger

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"

_SORT_PROBLEMS = [
    "bubble-sort", "bitonic-sort", "bucket-sort", "cocktail-sort", "comb-sort",
    "counting-sort", "cycle-sort", "gnome-sort", "heap-sort", "insertion-sort",
    "merge-sort", "odd-even-sort", "pancake-sort", "patience-sort", "quick-sort",
    "radix-sort", "selection-sort", "shell-sort", "stooge-sort", "strand-sort", "tim-sort",
]


@dataclass
class SimpleCase:
    id: str
    input_data: str
    expected_output: str
    is_hidden: bool
    order: int


def _js_starter(fn: str) -> str:
    return (
        "const data = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0];\n"
        "const arr = data.slice(1, 1 + n);\n\n"
        f"function {fn}(arr) {{\n\n}}\n\n"
        f"{fn}(arr);\n"
        "console.log(arr.join(' '));\n"
    )


def _js_program(fn: str, wrong: bool) -> str:
    cmp = "b-a" if wrong else "a-b"
    return (
        "const data = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0];\n"
        "const arr = data.slice(1, 1 + n);\n\n"
        f"function {fn}(arr) {{ arr.sort((a,b)=>{cmp}); }}\n\n"
        f"{fn}(arr);\n"
        "console.log(arr.join(' '));\n"
    )


def load_cases(con: sqlite3.Connection, pid: str) -> tuple[list[SimpleCase], str]:
    cur = con.execute(
        "SELECT id, input_data, expected_output, is_hidden, \"order\" FROM test_cases "
        "WHERE problem_id=? ORDER BY \"order\"", (pid,)
    )
    cases = [SimpleCase(id=r["id"], input_data=r["input_data"], expected_output=r["expected_output"],
                         is_hidden=bool(r["is_hidden"]), order=r["order"]) for r in cur.fetchall()]
    row = con.execute("SELECT test_suite_version FROM problems WHERE id=?", (pid,)).fetchone()
    return cases, row["test_suite_version"]


def function_name_for(con: sqlite3.Connection, pid: str) -> str:
    row = con.execute("SELECT function_contract FROM problems WHERE id=?", (pid,)).fetchone()
    return json.loads(row["function_contract"])["function_name"]


async def verify_one(pid: str, fn: str, cases: list[SimpleCase]) -> dict:
    t0 = time.monotonic()
    correct_result = await evaluate(_js_program(fn, False), "javascript", cases)
    if correct_result.tests_passed != correct_result.tests_total:
        sample_fail = next((r for r in correct_result.test_results if not r.passed), None)
        return {"pid": pid, "outcome": "reference_failed",
                "detail": f"{correct_result.tests_passed}/{correct_result.tests_total} verdict={correct_result.verdict} "
                          f"sample={(sample_fail.stderr if sample_fail else '')[:200]}",
                "duration_ms": (time.monotonic() - t0) * 1000}

    wrong_result = await evaluate(_js_program(fn, True), "javascript", cases)
    if wrong_result.tests_passed >= wrong_result.tests_total:
        return {"pid": pid, "outcome": "corpus_weakness",
                "detail": f"corrupted solution still passed all {wrong_result.tests_total}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    return {"pid": pid, "outcome": "verified",
            "detail": f"{correct_result.tests_passed}/{correct_result.tests_total} correct, "
                      f"wrong rejected on {wrong_result.tests_total - wrong_result.tests_passed}/{wrong_result.tests_total}",
            "duration_ms": (time.monotonic() - t0) * 1000}


async def main() -> int:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ledger.ensure_schema(con)

    results = []
    for pid in _SORT_PROBLEMS:
        fn = function_name_for(con, pid)
        cases, tsv = load_cases(con, pid)
        r = await verify_one(pid, fn, cases)
        results.append(r)
        status = "PASS" if r["outcome"] == "verified" else "FAIL"
        print(f"[{status}] javascript(program) {pid:16s} {r['outcome']:18s} {r['detail'][:100]}", flush=True)

        if r["outcome"] == "verified":
            # Save the real starter code (additive merge, python untouched)
            row = con.execute("SELECT starter_code FROM problems WHERE id=?", (pid,)).fetchone()
            sc = json.loads(row["starter_code"])
            sc["javascript"] = _js_starter(fn)
            con.execute("UPDATE problems SET starter_code=? WHERE id=?", (json.dumps(sc), pid))
            con.commit()

            ledger.record_cell(
                con, problem_id=pid, language="javascript", mode="program",
                verification_level=ledger.LEVEL_VERIFIED, status="pass",
                adapter_version="js-program-sort-family-v1",
                test_suite_version=tsv,
                duration_ms=r["duration_ms"],
            )

    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")

    (REPO_ROOT / "docs" / "atlascode-program-mode-js-sort-family.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
