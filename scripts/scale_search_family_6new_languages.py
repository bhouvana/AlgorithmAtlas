"""Scales Function Mode coverage for the 7 uniform search-family problems
(nums: array<int>, target: int -> int, no mutation) across the 6
newly-confirmed languages: go, kotlin, ruby, php, r, scala.

Same "one contract shape, one correct algorithm" precedent as the sort
family -- every one of these named search algorithms is checked purely on
output (found index or -1), so a standard binary search is a valid
reference solution for all 7, matching the already-proven 8-language
search-family pattern from earlier this session.
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

_SEARCH_PROBLEMS = [
    "binary-search", "exponential-search", "fibonacci-search",
    "interpolation-search", "jump-search", "ternary-search", "linear-search",
]

_TARGET_LANGUAGES = ["go", "kotlin", "ruby", "php", "r", "scala"]


def _go_wrapper(fn, wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        f"func {fn}(nums []int, target int) int {{\n"
        f"\tlo, hi := 0, len(nums)-1\n"
        f"\tfor lo <= hi {{\n"
        f"\t\tmid := (lo + hi) / 2\n"
        f"\t\tif nums[mid] == target {{\n"
        f"\t\t\treturn {ret}\n"
        f"\t\t}} else if nums[mid] < target {{\n"
        f"\t\t\tlo = mid + 1\n"
        f"\t\t}} else {{\n"
        f"\t\t\thi = mid - 1\n"
        f"\t\t}}\n"
        f"\t}}\n"
        f"\treturn -1\n"
        f"}}\n"
    )


def _kotlin_wrapper(fn, wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        f"fun {fn}(nums: List<Int>, target: Int): Int {{\n"
        f"    var lo = 0; var hi = nums.size - 1\n"
        f"    while (lo <= hi) {{\n"
        f"        val mid = (lo + hi) / 2\n"
        f"        if (nums[mid] == target) return {ret}\n"
        f"        else if (nums[mid] < target) lo = mid + 1\n"
        f"        else hi = mid - 1\n"
        f"    }}\n"
        f"    return -1\n"
        f"}}\n"
    )


def _scala_wrapper(fn, wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        f"def {fn}(nums: List[Int], target: Int): Int = {{\n"
        f"  var lo = 0; var hi = nums.length - 1\n"
        f"  while (lo <= hi) {{\n"
        f"    val mid = (lo + hi) / 2\n"
        f"    if (nums(mid) == target) return {ret}\n"
        f"    else if (nums(mid) < target) lo = mid + 1\n"
        f"    else hi = mid - 1\n"
        f"  }}\n"
        f"  -1\n"
        f"}}\n"
    )


def _ruby_wrapper(fn, wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        f"def {fn}(nums, target)\n"
        f"  lo = 0; hi = nums.length - 1\n"
        f"  while lo <= hi\n"
        f"    mid = (lo + hi) / 2\n"
        f"    if nums[mid] == target\n"
        f"      return {ret}\n"
        f"    elsif nums[mid] < target\n"
        f"      lo = mid + 1\n"
        f"    else\n"
        f"      hi = mid - 1\n"
        f"    end\n"
        f"  end\n"
        f"  -1\n"
        f"end\n"
    )


def _php_wrapper(fn, wrong):
    ret = "$mid + 1" if wrong else "$mid"
    return (
        f"function {fn}($nums, $target) {{\n"
        f"    $lo = 0; $hi = count($nums) - 1;\n"
        f"    while ($lo <= $hi) {{\n"
        f"        $mid = intdiv($lo + $hi, 2);\n"
        f"        if ($nums[$mid] == $target) return {ret};\n"
        f"        else if ($nums[$mid] < $target) $lo = $mid + 1;\n"
        f"        else $hi = $mid - 1;\n"
        f"    }}\n"
        f"    return -1;\n"
        f"}}\n"
    )


def _r_wrapper(fn, wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        f"{fn} <- function(nums, target) {{\n"
        f"  lo <- 0; hi <- length(nums) - 1\n"
        f"  while (lo <= hi) {{\n"
        f"    mid <- (lo + hi) %/% 2\n"
        f"    if (nums[[mid + 1]] == target) {{\n"
        f"      return({ret})\n"
        f"    }} else if (nums[[mid + 1]] < target) {{\n"
        f"      lo <- mid + 1\n"
        f"    }} else {{\n"
        f"      hi <- mid - 1\n"
        f"    }}\n"
        f"  }}\n"
        f"  return(-1)\n"
        f"}}\n"
    )


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
    for pid in _SEARCH_PROBLEMS:
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
                    adapter_version=f"{lang}-function-search-family-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
