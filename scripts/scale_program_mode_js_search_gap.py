"""Closes a real gap found while auditing coverage: JavaScript's Program
Mode search-family (binary-search + the 5 searching-family variants +
linear-search) was never actually run -- the JS proof-of-concept script
only covered the sort-family, and the later 7-language batch deliberately
excluded javascript (assuming, incorrectly, that it was already done).
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

_BINARY_SEARCH_PROBLEMS = [
    "binary-search", "exponential-search", "fibonacci-search",
    "interpolation-search", "jump-search", "ternary-search",
]
_LINEAR_SEARCH_PROBLEMS = ["linear-search"]


@dataclass
class SimpleCase:
    id: str
    input_data: str
    expected_output: str
    is_hidden: bool
    order: int


def _js_bsearch(fn, wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "const data = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0];\n"
        "const nums = data.slice(1, 1 + n);\n"
        "const target = data[1 + n];\n"
        f"function {fn}(nums, target) {{\n"
        "    let lo = 0, hi = nums.length - 1;\n"
        "    while (lo <= hi) {\n"
        "        const mid = (lo + hi) >> 1;\n"
        f"        if (nums[mid] === target) return {ret};\n"
        "        if (nums[mid] < target) lo = mid + 1; else hi = mid - 1;\n"
        "    }\n"
        "    return -1;\n"
        "}\n"
        f"console.log({fn}(nums, target));\n"
    )


def _js_linear(fn, wrong):
    ret = "i + 1" if wrong else "i"
    return (
        "const data = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0];\n"
        "const nums = data.slice(1, 1 + n);\n"
        "const target = data[1 + n];\n"
        f"function {fn}(nums, target) {{\n"
        f"    for (let i = 0; i < nums.length; i++) {{ if (nums[i] === target) return {ret}; }}\n"
        "    return -1;\n"
        "}\n"
        f"console.log({fn}(nums, target));\n"
    )


def function_name_for(con, pid):
    row = con.execute("SELECT function_contract FROM problems WHERE id=?", (pid,)).fetchone()
    return json.loads(row["function_contract"])["function_name"]


def load_cases(con, pid):
    cur = con.execute(
        "SELECT id, input_data, expected_output, is_hidden, \"order\" FROM test_cases "
        "WHERE problem_id=? ORDER BY \"order\"", (pid,)
    )
    cases = [SimpleCase(id=r["id"], input_data=r["input_data"], expected_output=r["expected_output"],
                         is_hidden=bool(r["is_hidden"]), order=r["order"]) for r in cur.fetchall()]
    row = con.execute("SELECT test_suite_version FROM problems WHERE id=?", (pid,)).fetchone()
    return cases, row["test_suite_version"]


async def verify_one(pid, fn, cases, build):
    t0 = time.monotonic()
    correct_result = await evaluate(build(fn, False), "javascript", cases)
    if correct_result.tests_passed != correct_result.tests_total:
        return {"pid": pid, "outcome": "reference_failed",
                "detail": f"{correct_result.tests_passed}/{correct_result.tests_total} verdict={correct_result.verdict}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    wrong_result = await evaluate(build(fn, True), "javascript", cases)
    if wrong_result.tests_passed >= wrong_result.tests_total:
        return {"pid": pid, "outcome": "corpus_weakness", "detail": "wrong solution still passed all cases",
                "duration_ms": (time.monotonic() - t0) * 1000}
    return {"pid": pid, "outcome": "verified",
            "detail": f"{correct_result.tests_passed}/{correct_result.tests_total} correct, "
                      f"wrong rejected on {wrong_result.tests_total - wrong_result.tests_passed}/{wrong_result.tests_total}",
            "duration_ms": (time.monotonic() - t0) * 1000}


async def main():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ledger.ensure_schema(con)

    groups = [(p, _js_bsearch) for p in _BINARY_SEARCH_PROBLEMS] + [(p, _js_linear) for p in _LINEAR_SEARCH_PROBLEMS]
    results = []
    for pid, build in groups:
        cases, tsv = load_cases(con, pid)
        if ledger.already_verified(con, pid, "javascript", "program", test_suite_version=tsv):
            print(f"[SKIP] {pid} already verified")
            continue
        fn = function_name_for(con, pid)
        r = await verify_one(pid, fn, cases, build)
        results.append(r)
        status = "PASS" if r["outcome"] == "verified" else "FAIL"
        print(f"[{status}] javascript(program) {pid:22s} {r['outcome']:18s} {r['detail'][:100]}", flush=True)
        if r["outcome"] == "verified":
            row = con.execute("SELECT starter_code FROM problems WHERE id=?", (pid,)).fetchone()
            sc = json.loads(row["starter_code"])
            sc["javascript"] = build(fn, False)
            con.execute("UPDATE problems SET starter_code=? WHERE id=?", (json.dumps(sc), pid))
            con.commit()
            ledger.record_cell(
                con, problem_id=pid, language="javascript", mode="program",
                verification_level=ledger.LEVEL_VERIFIED, status="pass",
                adapter_version="js-program-search-gap-v1", test_suite_version=tsv,
                duration_ms=r["duration_ms"],
            )

    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  verified={len(verified)}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
