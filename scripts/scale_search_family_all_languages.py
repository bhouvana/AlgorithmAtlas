"""Scales Function Mode coverage for the 7 uniform `(nums: array<int>,
target: int) -> integer` SEARCH problems across the same 8 currently-
reproducible languages as scale_sort_family_all_languages.py.

Two genuinely distinct algorithms, not one blindly reused across all 7 --
verified against each problem's real oracle/testdata semantics before
grouping (mission Phase 10/18 -- never assume identical contract shape
means identical correct answer):

  - BINARY SEARCH group (6 problems: binary-search + the 5 searching-family
    variants exponential/fibonacci/interpolation/jump/ternary-search) --
    all confirmed (searching.py's `_search_oracle` docstring, and
    legacy_audit_oracles.py's binary_search_index) to guarantee a SORTED,
    DISTINCT input array, so a real binary search is a correct reference
    for all 6 regardless of which named algorithm the problem teaches.
  - LINEAR SEARCH group (1 problem: linear-search) -- explicitly documented
    (legacy_audit_oracles.py) as an UNSORTED array, first-occurrence
    semantics -- genuinely different from binary search and kept separate,
    not folded into the same group.

Wrong solution for both groups: found-index + 1 (a real off-by-one defect,
matching the mission's preferred wrong-solution taxonomy), leaving -1
(not-found) untouched so the defect only bites on found cases -- always
present in a real 40-case corpus for a search problem.
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

_BINARY_SEARCH_PROBLEMS = [
    "binary-search", "exponential-search", "fibonacci-search",
    "interpolation-search", "jump-search", "ternary-search",
]
_LINEAR_SEARCH_PROBLEMS = ["linear-search"]

_TARGET_LANGUAGES = ["javascript", "typescript", "java", "cpp", "csharp", "perl", "c", "rust"]


def _js_bsearch(fn: str, wrong: bool) -> str:
    ret = "mid + 1" if wrong else "mid"
    return (
        f"function {fn}(nums, target) {{\n"
        f"    let lo = 0, hi = nums.length - 1;\n"
        f"    while (lo <= hi) {{\n"
        f"        const mid = (lo + hi) >> 1;\n"
        f"        if (nums[mid] === target) return {ret};\n"
        f"        if (nums[mid] < target) lo = mid + 1; else hi = mid - 1;\n"
        f"    }}\n"
        f"    return -1;\n"
        f"}}\n"
    )


def _ts_bsearch(fn: str, wrong: bool) -> str:
    ret = "mid + 1" if wrong else "mid"
    return (
        f"function {fn}(nums: number[], target: number): number {{\n"
        f"    let lo = 0, hi = nums.length - 1;\n"
        f"    while (lo <= hi) {{\n"
        f"        const mid = (lo + hi) >> 1;\n"
        f"        if (nums[mid] === target) return {ret};\n"
        f"        if (nums[mid] < target) lo = mid + 1; else hi = mid - 1;\n"
        f"    }}\n"
        f"    return -1;\n"
        f"}}\n"
    )


def _java_bsearch(fn: str, wrong: bool) -> str:
    ret = "mid + 1" if wrong else "mid"
    return (
        f"class Solution {{ public int {fn}(int[] nums, int target) {{\n"
        f"    int lo = 0, hi = nums.length - 1;\n"
        f"    while (lo <= hi) {{\n"
        f"        int mid = (lo + hi) / 2;\n"
        f"        if (nums[mid] == target) return {ret};\n"
        f"        if (nums[mid] < target) lo = mid + 1; else hi = mid - 1;\n"
        f"    }}\n"
        f"    return -1;\n"
        f"}} }}\n"
    )


def _cpp_bsearch(fn: str, wrong: bool) -> str:
    ret = "mid + 1" if wrong else "mid"
    return (
        f"class Solution {{ public: int {fn}(std::vector<int> nums, int target) {{\n"
        f"    int lo = 0, hi = (int)nums.size() - 1;\n"
        f"    while (lo <= hi) {{\n"
        f"        int mid = (lo + hi) / 2;\n"
        f"        if (nums[mid] == target) return {ret};\n"
        f"        if (nums[mid] < target) lo = mid + 1; else hi = mid - 1;\n"
        f"    }}\n"
        f"    return -1;\n"
        f"}} }};\n"
    )


def _csharp_bsearch(fn: str, wrong: bool) -> str:
    ret = "mid + 1" if wrong else "mid"
    return (
        f"class Solution {{ public static int {fn}(int[] nums, int target) {{\n"
        f"    int lo = 0, hi = nums.Length - 1;\n"
        f"    while (lo <= hi) {{\n"
        f"        int mid = (lo + hi) / 2;\n"
        f"        if (nums[mid] == target) return {ret};\n"
        f"        if (nums[mid] < target) lo = mid + 1; else hi = mid - 1;\n"
        f"    }}\n"
        f"    return -1;\n"
        f"}} }}\n"
    )


def _perl_bsearch(fn: str, wrong: bool) -> str:
    ret = "$mid + 1" if wrong else "$mid"
    return (
        f"sub {fn} {{\n"
        f"    my ($nums, $target) = @_;\n"
        f"    my $lo = 0; my $hi = scalar(@$nums) - 1;\n"
        f"    while ($lo <= $hi) {{\n"
        f"        my $mid = int(($lo + $hi) / 2);\n"
        f"        if ($nums->[$mid] == $target) {{ return {ret}; }}\n"
        f"        if ($nums->[$mid] < $target) {{ $lo = $mid + 1; }} else {{ $hi = $mid - 1; }}\n"
        f"    }}\n"
        f"    return -1;\n"
        f"}}\n"
    )


def _c_bsearch(fn: str, wrong: bool) -> str:
    ret = "mid + 1" if wrong else "mid"
    return (
        f"int {fn}(AtlasIntArray nums, int target) {{\n"
        f"    int lo = 0, hi = nums.size - 1;\n"
        f"    while (lo <= hi) {{\n"
        f"        int mid = (lo + hi) / 2;\n"
        f"        if (nums.data[mid] == target) return {ret};\n"
        f"        if (nums.data[mid] < target) lo = mid + 1; else hi = mid - 1;\n"
        f"    }}\n"
        f"    return -1;\n"
        f"}}\n"
    )


def _rust_bsearch(fn: str, wrong: bool) -> str:
    ret = "mid + 1" if wrong else "mid"
    return (
        f"fn {fn}(nums: Vec<i32>, target: i32) -> i32 {{\n"
        f"    let mut lo: i32 = 0;\n"
        f"    let mut hi: i32 = nums.len() as i32 - 1;\n"
        f"    while lo <= hi {{\n"
        f"        let mid = (lo + hi) / 2;\n"
        f"        if nums[mid as usize] == target {{ return {ret}; }}\n"
        f"        if nums[mid as usize] < target {{ lo = mid + 1; }} else {{ hi = mid - 1; }}\n"
        f"    }}\n"
        f"    return -1;\n"
        f"}}\n"
    )


def _js_linear(fn: str, wrong: bool) -> str:
    ret = "i + 1" if wrong else "i"
    return (
        f"function {fn}(nums, target) {{\n"
        f"    for (let i = 0; i < nums.length; i++) {{ if (nums[i] === target) return {ret}; }}\n"
        f"    return -1;\n"
        f"}}\n"
    )


def _ts_linear(fn: str, wrong: bool) -> str:
    ret = "i + 1" if wrong else "i"
    return (
        f"function {fn}(nums: number[], target: number): number {{\n"
        f"    for (let i = 0; i < nums.length; i++) {{ if (nums[i] === target) return {ret}; }}\n"
        f"    return -1;\n"
        f"}}\n"
    )


def _java_linear(fn: str, wrong: bool) -> str:
    ret = "i + 1" if wrong else "i"
    return (
        f"class Solution {{ public int {fn}(int[] nums, int target) {{\n"
        f"    for (int i = 0; i < nums.length; i++) {{ if (nums[i] == target) return {ret}; }}\n"
        f"    return -1;\n"
        f"}} }}\n"
    )


def _cpp_linear(fn: str, wrong: bool) -> str:
    ret = "i + 1" if wrong else "i"
    return (
        f"class Solution {{ public: int {fn}(std::vector<int> nums, int target) {{\n"
        f"    for (int i = 0; i < (int)nums.size(); i++) {{ if (nums[i] == target) return {ret}; }}\n"
        f"    return -1;\n"
        f"}} }};\n"
    )


def _csharp_linear(fn: str, wrong: bool) -> str:
    ret = "i + 1" if wrong else "i"
    return (
        f"class Solution {{ public static int {fn}(int[] nums, int target) {{\n"
        f"    for (int i = 0; i < nums.Length; i++) {{ if (nums[i] == target) return {ret}; }}\n"
        f"    return -1;\n"
        f"}} }}\n"
    )


def _perl_linear(fn: str, wrong: bool) -> str:
    ret = "$i + 1" if wrong else "$i"
    return (
        f"sub {fn} {{\n"
        f"    my ($nums, $target) = @_;\n"
        f"    for (my $i = 0; $i < scalar(@$nums); $i++) {{ if ($nums->[$i] == $target) {{ return {ret}; }} }}\n"
        f"    return -1;\n"
        f"}}\n"
    )


def _c_linear(fn: str, wrong: bool) -> str:
    ret = "i + 1" if wrong else "i"
    return (
        f"int {fn}(AtlasIntArray nums, int target) {{\n"
        f"    for (int i = 0; i < nums.size; i++) {{ if (nums.data[i] == target) return {ret}; }}\n"
        f"    return -1;\n"
        f"}}\n"
    )


def _rust_linear(fn: str, wrong: bool) -> str:
    ret = "i as i32 + 1" if wrong else "i as i32"
    return (
        f"fn {fn}(nums: Vec<i32>, target: i32) -> i32 {{\n"
        f"    for i in 0..nums.len() {{ if nums[i] == target {{ return {ret}; }} }}\n"
        f"    return -1;\n"
        f"}}\n"
    )


_BSEARCH_WRAPPERS = {
    "javascript": _js_bsearch, "typescript": _ts_bsearch, "java": _java_bsearch,
    "cpp": _cpp_bsearch, "csharp": _csharp_bsearch, "perl": _perl_bsearch,
    "c": _c_bsearch, "rust": _rust_bsearch,
}
_LINEAR_WRAPPERS = {
    "javascript": _js_linear, "typescript": _ts_linear, "java": _java_linear,
    "cpp": _cpp_linear, "csharp": _csharp_linear, "perl": _perl_linear,
    "c": _c_linear, "rust": _rust_linear,
}

_ADAPTER_VERSION = {
    "javascript": "js-search-family-v1", "typescript": "ts-search-family-v1",
    "java": "java-search-family-v1", "cpp": "cpp-search-family-v1",
    "csharp": "csharp-search-family-v1", "perl": "perl-search-family-v1",
    "c": "c-search-family-v1", "rust": "rust-search-family-v1",
}


def _maybe_json(v):
    return json.loads(v) if isinstance(v, str) else v


def load_problem(con: sqlite3.Connection, pid: str):
    row = con.execute(
        "SELECT function_contract, test_suite_version FROM problems WHERE id=?", (pid,)
    ).fetchone()
    contract = FunctionContract.from_dict(json.loads(row["function_contract"]))
    cur = con.execute(
        "SELECT id, function_args, function_expected, \"order\" FROM test_cases "
        "WHERE problem_id=? AND function_args IS NOT NULL ORDER BY \"order\"",
        (pid,),
    )
    cases = [
        FunctionCase(id=r["id"], arguments=_maybe_json(r["function_args"]), expected=_maybe_json(r["function_expected"]),
                     has_expected=True, is_hidden=False, order=r["order"])
        for r in cur.fetchall()
    ]
    return contract, cases, row["function_contract"], row["test_suite_version"]


async def verify_one(pid: str, lang: str, contract: FunctionContract, cases: list[FunctionCase], build) -> dict:
    t0 = time.monotonic()
    fn = contract.function_name

    correct_result = await evaluate_function(build(fn, False), lang, contract, cases)
    n_pass = sum(1 for r in correct_result.case_results if r.passed)
    if n_pass != len(cases):
        sample_fail = next((r for r in correct_result.case_results if not r.passed), None)
        return {
            "pid": pid, "lang": lang, "outcome": "reference_failed",
            "detail": f"{n_pass}/{len(cases)} -- verdict={correct_result.verdict} "
                      f"compile_output={(correct_result.compile_output or '')[:200]} "
                      f"sample_stderr={(sample_fail.stderr if sample_fail else '')[:200]}",
            "duration_ms": (time.monotonic() - t0) * 1000,
        }

    wrong_result = await evaluate_function(build(fn, True), lang, contract, cases)
    n_wrong_pass = sum(1 for r in wrong_result.case_results if r.passed)
    if n_wrong_pass >= len(cases):
        return {"pid": pid, "lang": lang, "outcome": "corpus_weakness",
                "detail": f"corrupted solution still passed all {len(cases)}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    return {"pid": pid, "lang": lang, "outcome": "verified",
            "detail": f"{n_pass}/{len(cases)} correct, wrong rejected on {len(cases) - n_wrong_pass}/{len(cases)}",
            "duration_ms": (time.monotonic() - t0) * 1000}


async def main() -> int:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ledger.ensure_schema(con)

    groups = [(p, _BSEARCH_WRAPPERS) for p in _BINARY_SEARCH_PROBLEMS] + \
             [(p, _LINEAR_WRAPPERS) for p in _LINEAR_SEARCH_PROBLEMS]

    results = []
    skipped = 0
    for lang in _TARGET_LANGUAGES:
        for pid, wrappers in groups:
            contract, cases, raw_contract, tsv = load_problem(con, pid)
            cv = ledger.contract_hash(raw_contract)
            if ledger.already_verified(con, pid, lang, "function", contract_version=cv, test_suite_version=tsv):
                skipped += 1
                continue
            r = await verify_one(pid, lang, contract, cases, wrappers[lang])
            results.append(r)
            status = "PASS" if r["outcome"] == "verified" else "FAIL"
            print(f"[{status}] {lang:10s} {pid:22s} {r['outcome']:18s} {r['detail'][:100]}", flush=True)
            if r["outcome"] == "verified":
                ledger.record_cell(
                    con, problem_id=pid, language=lang, mode="function",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=_ADAPTER_VERSION[lang],
                    contract_version=cv, test_suite_version=tsv,
                    duration_ms=r["duration_ms"],
                )

    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL attempted: {len(results)}  skipped (already verified): {skipped}")
    print(f"verified={len(verified)}  reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")

    (REPO_ROOT / "docs" / "atlascode-search-family-scaling.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
