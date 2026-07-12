"""Scales Function Mode coverage for the 21 uniform `mutates_argument`
sort-family problems across the 6 newly-confirmed languages this session:
go, kotlin, ruby, php, r, scala (all genuinely working via
`source scripts/toolchain_path.sh` -- confirmed with real compile+run
tests, not just version checks; see docs/atlascode-resume.md).

Same "one contract shape, native sort is a valid reference solution"
precedent as scale_sort_family_all_languages.py (the 8-language version),
but each of these 6 languages needed its OWN mutation-convention research
first (confirmed by reading adapters.py/compiled_adapters.py directly,
not guessed):
  - go/kotlin/scala: mutates_argument means the generated starter has NO
    return type (void/Unit/()) -- the harness re-reads the mutated
    argument after the call. Go slices, Kotlin MutableList, and Scala
    ListBuffer are reference types, so an in-place algorithm (no
    reassignment of the parameter itself) is naturally observed.
  - ruby: same re-read-the-argument convention, but Ruby method params are
    local bindings -- `arr.sort!` (bang, in-place) works, `arr = arr.sort`
    (reassignment) would NOT be observed by the caller.
  - php: same re-read convention, but PHP arrays are copy-on-value by
    default -- the parameter MUST be declared `&$arr` (by-reference) or
    the mutation is invisible to the caller (a real bug PhpFunctionAdapter's
    own docstring documents having hit and fixed).
  - r: R has NO mutable-reference call semantics at all -- RFunctionAdapter
    explicitly uses the function's RETURN VALUE for mutates_argument
    contracts, not a re-read of the argument. R's sort function must
    actually `return(sort(arr))`.
"""
from __future__ import annotations

import asyncio
import json
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))
sys.path.insert(0, str(Path(__file__).parent))
import logging
logging.disable(logging.CRITICAL)

from algorithm_atlas.atlascode.function_mode.contracts import FunctionContract
from algorithm_atlas.atlascode.function_mode.runner import FunctionCase, evaluate_function
import atlascode_ledger as ledger

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"

_SORT_PROBLEMS = [
    "bubble-sort", "bitonic-sort", "bucket-sort", "cocktail-sort", "comb-sort",
    "counting-sort", "cycle-sort", "gnome-sort", "heap-sort", "insertion-sort",
    "merge-sort", "odd-even-sort", "pancake-sort", "patience-sort", "quick-sort",
    "radix-sort", "selection-sort", "shell-sort", "stooge-sort", "strand-sort", "tim-sort",
]

_TARGET_LANGUAGES = ["go", "kotlin", "ruby", "php", "r", "scala"]


def _go_wrapper(fn, wrong):
    cmp = "<" if wrong else ">"
    return (
        f"func {fn}(arr []int) {{\n"
        f"\tn := len(arr)\n"
        f"\tfor i := 0; i < n-1; i++ {{\n"
        f"\t\tfor j := 0; j < n-1-i; j++ {{\n"
        f"\t\t\tif arr[j] {cmp} arr[j+1] {{\n"
        f"\t\t\t\tarr[j], arr[j+1] = arr[j+1], arr[j]\n"
        f"\t\t\t}}\n"
        f"\t\t}}\n"
        f"\t}}\n"
        f"}}\n"
    )


def _kotlin_wrapper(fn, wrong):
    cmp = "<" if wrong else ">"
    return (
        f"fun {fn}(arr: MutableList<Int>) {{\n"
        f"    val n = arr.size\n"
        f"    for (i in 0 until n-1) {{\n"
        f"        for (j in 0 until n-1-i) {{\n"
        f"            if (arr[j] {cmp} arr[j+1]) {{\n"
        f"                val t = arr[j]; arr[j] = arr[j+1]; arr[j+1] = t\n"
        f"            }}\n"
        f"        }}\n"
        f"    }}\n"
        f"}}\n"
    )


def _scala_wrapper(fn, wrong):
    cmp = "<" if wrong else ">"
    return (
        f"def {fn}(arr: scala.collection.mutable.ListBuffer[Int]): Unit = {{\n"
        f"  val n = arr.length\n"
        f"  for (i <- 0 until n-1) {{\n"
        f"    for (j <- 0 until n-1-i) {{\n"
        f"      if (arr(j) {cmp} arr(j+1)) {{\n"
        f"        val t = arr(j); arr(j) = arr(j+1); arr(j+1) = t\n"
        f"      }}\n"
        f"    }}\n"
        f"  }}\n"
        f"}}\n"
    )


def _ruby_wrapper(fn, wrong):
    cmp = "b <=> a" if wrong else "a <=> b"
    return f"def {fn}(arr)\n  arr.sort! {{ |a, b| {cmp} }}\nend\n"


def _php_wrapper(fn, wrong):
    body = "rsort($arr);" if wrong else "sort($arr);"
    return f"function {fn}(&$arr) {{\n    {body}\n}}\n"


def _r_wrapper(fn, wrong):
    body = "return(sort(arr, decreasing = TRUE))" if wrong else "return(sort(arr))"
    return f"{fn} <- function(arr) {{\n  {body}\n}}\n"


_WRAPPERS = {
    "go": _go_wrapper, "kotlin": _kotlin_wrapper, "ruby": _ruby_wrapper,
    "php": _php_wrapper, "r": _r_wrapper, "scala": _scala_wrapper,
}


def _maybe_json(v):
    return json.loads(v) if isinstance(v, str) else v


def load_problem(con, pid):
    row = con.execute("SELECT function_contract, test_suite_version FROM problems WHERE id=?", (pid,)).fetchone()
    contract = FunctionContract.from_dict(json.loads(row["function_contract"]))
    cur = con.execute(
        "SELECT id, function_args, function_expected, is_hidden, \"order\" FROM test_cases "
        "WHERE problem_id=? ORDER BY \"order\"", (pid,)
    )
    cases = []
    for r in cur.fetchall():
        args = _maybe_json(r["function_args"])
        expected = _maybe_json(r["function_expected"])
        cases.append(FunctionCase(id=r["id"], arguments=args, expected=expected, has_expected=True,
                                   is_hidden=bool(r["is_hidden"]), order=r["order"]))
    return contract, cases, row["test_suite_version"]


async def verify_one(pid, lang, contract, cases, fn_name, build):
    t0 = time.monotonic()
    correct_result = await evaluate_function(build(fn_name, False), lang, contract, cases)
    n_pass = sum(1 for r in correct_result.case_results if r.passed)
    if n_pass != len(cases):
        sample_fail = next((r for r in correct_result.case_results if not r.passed), None)
        return {"pid": pid, "lang": lang, "outcome": "reference_failed",
                "detail": f"{n_pass}/{len(cases)} verdict={correct_result.verdict} "
                          f"compile={(correct_result.compile_output or '')[:200]} "
                          f"stderr={(sample_fail.stderr if sample_fail else '')[:200]} "
                          f"actual={(sample_fail.actual_return if sample_fail else '')!r} "
                          f"expected={(sample_fail.expected_return if sample_fail else '')!r}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    wrong_result = await evaluate_function(build(fn_name, True), lang, contract, cases)
    n_wrong_pass = sum(1 for r in wrong_result.case_results if r.passed)
    if n_wrong_pass >= len(cases):
        return {"pid": pid, "lang": lang, "outcome": "corpus_weakness",
                "detail": f"corrupted solution still passed all {len(cases)}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    return {"pid": pid, "lang": lang, "outcome": "verified",
            "detail": f"{n_pass}/{len(cases)} correct, wrong rejected on {len(cases) - n_wrong_pass}/{len(cases)}",
            "duration_ms": (time.monotonic() - t0) * 1000}


async def main():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ledger.ensure_schema(con)
    results = []
    skipped = 0
    for pid in _SORT_PROBLEMS:
        contract, cases, tsv = load_problem(con, pid)
        for lang in _TARGET_LANGUAGES:
            if ledger.already_verified(con, pid, lang, "function", test_suite_version=tsv):
                skipped += 1
                continue
            build = _WRAPPERS[lang]
            r = await verify_one(pid, lang, contract, cases, contract.function_name, build)
            results.append(r)
            status = "PASS" if r["outcome"] == "verified" else "FAIL"
            print(f"[{status}] {lang:10s}(function) {pid:20s} {r['outcome']:18s} {r['detail'][:150]}", flush=True)
            if r["outcome"] == "verified":
                ledger.record_cell(con, problem_id=pid, language=lang, mode="function",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=f"{lang}-function-sort-family-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
