"""Ports Kotlin (Function Mode) solutions for the ~185 problems missing
Kotlin coverage, using existing verified JS/other-language builders in the
scale_*.py scripts as reference algorithms where available, and original
implementations for problems with no existing language coverage.

12 problems are skipped as documented architectural limitations (int32/int64
overflow on real corpus stress cases -- see docs/atlascode-bigint-numeric-audit.json):
fibonacci-dp, karatsuba, catalan-number, fast-power, decode-ways, unique-paths,
combination-sum-iv-count, evaluate-reverse-polish-notation, maximum-product-subarray,
sum-root-to-leaf-numbers, trapping-rain-water, reverse-bits.
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
LANG = "kotlin"

# Problems skipped: documented int-width architectural limitations (see module
# docstring). Not attempted for Kotlin, consistent with java/cpp/csharp/c/rust.
SKIPPED_BIGINT = {
    "fibonacci-dp", "karatsuba", "catalan-number", "fast-power", "decode-ways",
    "unique-paths", "combination-sum-iv-count", "evaluate-reverse-polish-notation",
    "maximum-product-subarray", "sum-root-to-leaf-numbers", "trapping-rain-water",
    "reverse-bits",
}

_BUILDERS = {}


# ══════════════════════════════════════════════════════════════════════════
# Batch 1: binary-search family
# ══════════════════════════════════════════════════════════════════════════

def _kt_binarysearch(wrong):
    a = " + 1" if wrong else ""
    return (f"fun binary_search(nums: List<Int>, target: Int): Int {{\n"
            f"    var lo = 0; var hi = nums.size - 1\n"
            f"    while (lo <= hi) {{\n"
            f"        val mid = (lo + hi) / 2\n"
            f"        if (nums[mid] == target) return mid{a}\n"
            f"        if (nums[mid] < target) lo = mid + 1 else hi = mid - 1\n"
            f"    }}\n"
            f"    return -1\n}}\n")
_BUILDERS["binary-search"] = _kt_binarysearch


def _kt_linearsearch(wrong):
    a = " + 1" if wrong else ""
    return (f"fun linear_search(nums: List<Int>, target: Int): Int {{\n"
            f"    for (i in nums.indices) {{ if (nums[i] == target) return i{a} }}\n"
            f"    return -1\n}}\n")
_BUILDERS["linear-search"] = _kt_linearsearch


def _kt_exponentialsearch(wrong):
    a = " + 1" if wrong else ""
    return (f"fun rangeSearchExp(nums: List<Int>, target: Int, lo0: Int, hi0: Int): Int {{\n"
            f"    var lo = lo0; var hi = hi0\n"
            f"    while (lo <= hi) {{\n"
            f"        val mid = (lo + hi) / 2\n"
            f"        if (nums[mid] == target) return mid\n"
            f"        if (nums[mid] < target) lo = mid + 1 else hi = mid - 1\n"
            f"    }}\n"
            f"    return -1\n}}\n"
            f"fun exponential_search(nums: List<Int>, target: Int): Int {{\n"
            f"    val n = nums.size\n"
            f"    if (n == 0) return -1\n"
            f"    if (nums[0] == target) return 0{a}\n"
            f"    var i = 1\n"
            f"    while (i < n && nums[i] <= target) i *= 2\n"
            f"    return rangeSearchExp(nums, target, i / 2, minOf(i, n - 1))\n}}\n")
_BUILDERS["exponential-search"] = _kt_exponentialsearch


def _kt_fibonaccisearch(wrong):
    a = " + 1" if wrong else ""
    return (f"fun fibonacci_search(nums: List<Int>, target: Int): Int {{\n"
            f"    val n = nums.size\n"
            f"    if (n == 0) return -1\n"
            f"    var fib2 = 0; var fib1 = 1; var fibN = fib2 + fib1\n"
            f"    while (fibN < n) {{ fib2 = fib1; fib1 = fibN; fibN = fib2 + fib1 }}\n"
            f"    var offset = -1\n"
            f"    while (fibN > 1) {{\n"
            f"        val i = minOf(offset + fib2, n - 1)\n"
            f"        if (nums[i] < target) {{ fibN = fib1; fib1 = fib2; fib2 = fibN - fib1; offset = i }}\n"
            f"        else if (nums[i] > target) {{ fibN = fib2; fib1 = fib1 - fib2; fib2 = fibN - fib1 }}\n"
            f"        else return i{a}\n"
            f"    }}\n"
            f"    if (fib1 == 1 && offset + 1 < n && nums[offset + 1] == target) return (offset + 1){a}\n"
            f"    return -1\n}}\n")
_BUILDERS["fibonacci-search"] = _kt_fibonaccisearch


def _kt_interpolationsearch(wrong):
    a = " + 1" if wrong else ""
    return (f"fun interpolation_search(nums: List<Int>, target: Int): Int {{\n"
            f"    var lo = 0; var hi = nums.size - 1\n"
            f"    while (lo <= hi && target >= nums[lo] && target <= nums[hi]) {{\n"
            f"        if (lo == hi) {{ return if (nums[lo] == target) lo{a} else -1 }}\n"
            f"        val pos = lo + (((target - nums[lo]).toLong() * (hi - lo) / (nums[hi] - nums[lo]).toLong()).toInt())\n"
            f"        if (nums[pos] == target) return pos{a}\n"
            f"        if (nums[pos] < target) lo = pos + 1 else hi = pos - 1\n"
            f"    }}\n"
            f"    return -1\n}}\n")
_BUILDERS["interpolation-search"] = _kt_interpolationsearch


def _kt_firstoccurrence(wrong):
    a = " + 1" if wrong else ""
    return (f"fun first_occurrence(nums: List<Int>, target: Int): Int {{\n"
            f"    var lo = 0; var hi = nums.size - 1; var ans = -1\n"
            f"    while (lo <= hi) {{\n"
            f"        val mid = (lo + hi) / 2\n"
            f"        if (nums[mid] == target) {{ ans = mid; hi = mid - 1 }}\n"
            f"        else if (nums[mid] < target) lo = mid + 1 else hi = mid - 1\n"
            f"    }}\n"
            f"    return if (ans == -1) -1 else ans{a}\n}}\n")
_BUILDERS["first-occurrence"] = _kt_firstoccurrence


def _kt_lastoccurrence(wrong):
    a = " + 1" if wrong else ""
    return (f"fun last_occurrence(nums: List<Int>, target: Int): Int {{\n"
            f"    var lo = 0; var hi = nums.size - 1; var ans = -1\n"
            f"    while (lo <= hi) {{\n"
            f"        val mid = (lo + hi) / 2\n"
            f"        if (nums[mid] == target) {{ ans = mid; lo = mid + 1 }}\n"
            f"        else if (nums[mid] < target) lo = mid + 1 else hi = mid - 1\n"
            f"    }}\n"
            f"    return if (ans == -1) -1 else ans{a}\n}}\n")
_BUILDERS["last-occurrence"] = _kt_lastoccurrence


def _kt_countoccurrences(wrong):
    a = " + 1" if wrong else ""
    return (f"fun countFirst(nums: List<Int>, target: Int): Int {{\n"
            f"    var lo = 0; var hi = nums.size - 1; var ans = -1\n"
            f"    while (lo <= hi) {{\n"
            f"        val mid = (lo + hi) / 2\n"
            f"        if (nums[mid] == target) {{ ans = mid; hi = mid - 1 }}\n"
            f"        else if (nums[mid] < target) lo = mid + 1 else hi = mid - 1\n"
            f"    }}\n"
            f"    return ans\n}}\n"
            f"fun countLast(nums: List<Int>, target: Int): Int {{\n"
            f"    var lo = 0; var hi = nums.size - 1; var ans = -1\n"
            f"    while (lo <= hi) {{\n"
            f"        val mid = (lo + hi) / 2\n"
            f"        if (nums[mid] == target) {{ ans = mid; lo = mid + 1 }}\n"
            f"        else if (nums[mid] < target) lo = mid + 1 else hi = mid - 1\n"
            f"    }}\n"
            f"    return ans\n}}\n"
            f"fun count_occurrences(nums: List<Int>, target: Int): Int {{\n"
            f"    val f = countFirst(nums, target)\n"
            f"    if (f == -1) return 0\n"
            f"    val l = countLast(nums, target)\n"
            f"    return (l - f + 1){a}\n}}\n")
_BUILDERS["count-occurrences-sorted"] = _kt_countoccurrences


def _kt_rotatedbinarysearch(wrong):
    a = " + 1" if wrong else ""
    return (f"fun search(nums: List<Int>, target: Int): Int {{\n"
            f"    var lo = 0; var hi = nums.size - 1\n"
            f"    while (lo <= hi) {{\n"
            f"        val mid = (lo + hi) / 2\n"
            f"        if (nums[mid] == target) return mid{a}\n"
            f"        if (nums[lo] <= nums[mid]) {{\n"
            f"            if (target >= nums[lo] && target < nums[mid]) hi = mid - 1 else lo = mid + 1\n"
            f"        }} else {{\n"
            f"            if (target > nums[mid] && target <= nums[hi]) lo = mid + 1 else hi = mid - 1\n"
            f"        }}\n"
            f"    }}\n"
            f"    return -1\n}}\n")
_BUILDERS["rotated-binary-search"] = _kt_rotatedbinarysearch


def _kt_findminrotated(wrong):
    a = " + 1" if wrong else ""
    return (f"fun find_min(nums: List<Int>): Int {{\n"
            f"    var lo = 0; var hi = nums.size - 1\n"
            f"    while (lo < hi) {{\n"
            f"        val mid = (lo + hi) / 2\n"
            f"        if (nums[mid] > nums[hi]) lo = mid + 1 else hi = mid\n"
            f"    }}\n"
            f"    return nums[lo]{a}\n}}\n")
_BUILDERS["find-minimum-rotated-sorted-array"] = _kt_findminrotated


def _kt_searchinsertposition(wrong):
    a = " + 1" if wrong else ""
    return (f"fun search_insert(nums: List<Int>, target: Int): Int {{\n"
            f"    var lo = 0; var hi = nums.size\n"
            f"    while (lo < hi) {{\n"
            f"        val mid = (lo + hi) / 2\n"
            f"        if (nums[mid] < target) lo = mid + 1 else hi = mid\n"
            f"    }}\n"
            f"    return lo{a}\n}}\n")
_BUILDERS["search-insert-position"] = _kt_searchinsertposition


def _kt_search2dmatrix(wrong):
    neg = "!" if wrong else ""
    return (f"fun search_matrix(matrix: List<List<Int>>, target: Int): Boolean {{\n"
            f"    if (matrix.isEmpty() || matrix[0].isEmpty()) return false\n"
            f"    val rows = matrix.size; val cols = matrix[0].size\n"
            f"    var lo = 0; var hi = rows * cols - 1\n"
            f"    while (lo <= hi) {{\n"
            f"        val mid = (lo + hi) / 2\n"
            f"        val v = matrix[mid / cols][mid % cols]\n"
            f"        if (v == target) return {neg}true\n"
            f"        if (v < target) lo = mid + 1 else hi = mid - 1\n"
            f"    }}\n"
            f"    return {neg}false\n}}\n")
_BUILDERS["search-2d-matrix"] = _kt_search2dmatrix



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


async def verify_one(pid, contract, cases, build):
    t0 = time.monotonic()
    correct_result = await evaluate_function(build(False), LANG, contract, cases)
    n_pass = sum(1 for r in correct_result.case_results if r.passed)
    if n_pass != len(cases):
        sample_fail = next((r for r in correct_result.case_results if not r.passed), None)
        return {"pid": pid, "outcome": "reference_failed",
                "detail": f"{n_pass}/{len(cases)} verdict={correct_result.verdict} "
                          f"compile={(correct_result.compile_output or '')[:200]} "
                          f"stderr={(sample_fail.stderr if sample_fail else '')[:200]} "
                          f"actual={(sample_fail.actual_return if sample_fail else '')!r} "
                          f"expected={(sample_fail.expected_return if sample_fail else '')!r}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    wrong_result = await evaluate_function(build(True), LANG, contract, cases)
    n_wrong_pass = sum(1 for r in wrong_result.case_results if r.passed)
    if n_wrong_pass >= len(cases):
        return {"pid": pid, "outcome": "corpus_weakness",
                "detail": f"corrupted solution still passed all {len(cases)}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    return {"pid": pid, "outcome": "verified",
            "detail": f"{n_pass}/{len(cases)} correct, wrong rejected on {len(cases) - n_wrong_pass}/{len(cases)}",
            "duration_ms": (time.monotonic() - t0) * 1000}


async def main():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ledger.ensure_schema(con)
    results = []
    skipped = 0
    for pid, build in _BUILDERS.items():
        contract, cases, tsv = load_problem(con, pid)
        if ledger.already_verified(con, pid, LANG, "function", test_suite_version=tsv):
            skipped += 1
            continue
        r = await verify_one(pid, contract, cases, build)
        results.append(r)
        status = "PASS" if r["outcome"] == "verified" else "FAIL"
        print(f"[{status}] {pid:38s} {r['outcome']:18s} {r['detail'][:160]}", flush=True)
        if r["outcome"] == "verified":
            ledger.record_cell(con, problem_id=pid, language=LANG, mode="function",
                verification_level=ledger.LEVEL_VERIFIED, status="pass",
                adapter_version="kotlin-function-port-v1", test_suite_version=tsv,
                duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL attempted: {len(results)}  skipped(already-verified): {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
