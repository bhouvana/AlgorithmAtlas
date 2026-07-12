"""Scales Function Mode coverage for the 21 uniform `mutates_argument`
sort-family problems (bubble-sort, quick-sort, heap-sort, ... -- see
docs/atlascode-complete-matrix.json for the full list) across every
CURRENTLY-REPRODUCIBLE compiled/interpreted language in this environment
(javascript, typescript, java, cpp, csharp, perl, c, rust -- the 8 NOT
affected by the PATH-staleness/toolchain-availability finding from this
session's audit; see docs/atlascode-ledger-staleness.json).

Why this is a legitimate, non-porting scaling strategy (mission Phase 6/18):
every one of these 21 problems has the IDENTICAL function_contract shape --
one `arr: array<int>` parameter, `mutates_argument="arr"`, no other
parameters -- regardless of which named sorting algorithm the problem
teaches. A language's OWN native/standard-library sort is therefore a
correct reference solution for "sort this array" independent of the
algorithm name, exactly the same precedent
`verify_python_function_mode_bulk.py`'s `build_sort_wrapper` already
established for Python (`list.sort()`). This is NOT solving each problem by
name; it's recognizing 21 problems share one real contract.

Wrong solution: a genuine defect (descending sort instead of ascending) --
not a syntactic no-op, a real semantic bug matching the mission's preferred
wrong-solution taxonomy (Phase 10).

Every (problem, language) pair not already Level-6 in the ledger is composed,
compiled/run via the REAL per-language runner (compile-once for the 5
compiled languages here: java/cpp/csharp/c/rust, interpreted per-case for
javascript/typescript/perl), and only recorded Level 6 on genuine
all-pass + wrong-rejected.
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

_TARGET_LANGUAGES = ["javascript", "typescript", "java", "cpp", "csharp", "perl", "c", "rust"]


def _js_wrapper(fn: str, wrong: bool) -> str:
    cmp = "b-a" if wrong else "a-b"
    return f"function {fn}(arr) {{ arr.sort((a,b)=>{cmp}); }}\n"


def _ts_wrapper(fn: str, wrong: bool) -> str:
    cmp = "b-a" if wrong else "a-b"
    return f"function {fn}(arr: number[]): number[] {{ arr.sort((a,b)=>{cmp}); return arr; }}\n"


def _java_wrapper(fn: str, wrong: bool) -> str:
    body = "java.util.Arrays.sort(arr);"
    if wrong:
        body += " int i=0,j=arr.length-1; while(i<j){int t=arr[i];arr[i]=arr[j];arr[j]=t;i++;j--;}"
    return f"class Solution {{ public void {fn}(int[] arr) {{ {body} }} }}\n"


def _cpp_wrapper(fn: str, wrong: bool) -> str:
    body = "std::sort(arr.rbegin(), arr.rend());" if wrong else "std::sort(arr.begin(), arr.end());"
    return f"class Solution {{ public: void {fn}(std::vector<int>& arr) {{ {body} }} }};\n"


def _csharp_wrapper(fn: str, wrong: bool) -> str:
    body = "System.Array.Sort(arr);"
    if wrong:
        body += " System.Array.Reverse(arr);"
    return f"class Solution {{ public static void {fn}(ref int[] arr) {{ {body} }} }}\n"


def _perl_wrapper(fn: str, wrong: bool) -> str:
    cmp = "$b <=> $a" if wrong else "$a <=> $b"
    return f"sub {fn} {{ my ($arr) = @_; @$arr = sort {{ {cmp} }} @$arr; }}\n"


def _c_wrapper(fn: str, wrong: bool) -> str:
    cmp = "<" if wrong else ">"
    return (
        f"void {fn}(AtlasIntArray* arr) {{\n"
        f"    int n = arr->size;\n"
        f"    for (int i = 0; i < n - 1; i++) {{\n"
        f"        for (int j = 0; j < n - 1 - i; j++) {{\n"
        f"            if (arr->data[j] {cmp} arr->data[j+1]) {{\n"
        f"                int t = arr->data[j]; arr->data[j] = arr->data[j+1]; arr->data[j+1] = t;\n"
        f"            }}\n"
        f"        }}\n"
        f"    }}\n"
        f"}}\n"
    )


def _rust_wrapper(fn: str, wrong: bool) -> str:
    body = "arr.sort(); arr.reverse();" if wrong else "arr.sort();"
    return f"fn {fn}(arr: &mut Vec<i32>) -> () {{ {body} }}\n"


_WRAPPERS = {
    "javascript": _js_wrapper, "typescript": _ts_wrapper, "java": _java_wrapper,
    "cpp": _cpp_wrapper, "csharp": _csharp_wrapper, "perl": _perl_wrapper,
    "c": _c_wrapper, "rust": _rust_wrapper,
}

_ADAPTER_VERSION = {
    "javascript": "js-sort-family-v1", "typescript": "ts-sort-family-v1",
    "java": "java-sort-family-v1", "cpp": "cpp-sort-family-v1",
    "csharp": "csharp-sort-family-v1", "perl": "perl-sort-family-v1",
    "c": "c-sort-family-v1", "rust": "rust-sort-family-v1",
}


def _maybe_json(v):
    return json.loads(v) if isinstance(v, str) else v


def load_problem(con: sqlite3.Connection, pid: str) -> tuple[FunctionContract, list[FunctionCase], str, str]:
    row = con.execute(
        "SELECT function_contract, test_suite_version FROM problems WHERE id=?", (pid,)
    ).fetchone()
    contract = FunctionContract.from_dict(json.loads(row[0]))
    cur = con.execute(
        "SELECT id, function_args, function_expected, \"order\" FROM test_cases "
        "WHERE problem_id=? AND function_args IS NOT NULL ORDER BY \"order\"",
        (pid,),
    )
    cases = [
        FunctionCase(id=r[0], arguments=_maybe_json(r[1]), expected=_maybe_json(r[2]),
                     has_expected=True, is_hidden=False, order=r[3])
        for r in cur.fetchall()
    ]
    return contract, cases, row[0], row[1]


async def verify_one(pid: str, lang: str, contract: FunctionContract, cases: list[FunctionCase]) -> dict:
    t0 = time.monotonic()
    build = _WRAPPERS[lang]
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
    con.row_factory = sqlite3.Row  # required by ledger.already_verified()/get_cell() -- a prior
    # run without this crashed with TypeError the instant it hit a pre-existing cell (csharp+
    # bubble-sort, already in C#'s ladder), losing 84 already-computed genuine passes because
    # persistence used to happen only in a single batch at the very end. Fixed two ways: this
    # line, and writing to the ledger immediately after each verified result below instead of
    # batching, so a future crash can never lose already-completed, already-judged work again.
    ledger.ensure_schema(con)

    results = []
    skipped_already_verified = 0
    for lang in _TARGET_LANGUAGES:
        for pid in _SORT_PROBLEMS:
            contract, cases, raw_contract, tsv = load_problem(con, pid)
            cv = ledger.contract_hash(raw_contract)
            if ledger.already_verified(con, pid, lang, "function", contract_version=cv, test_suite_version=tsv):
                skipped_already_verified += 1
                continue
            r = await verify_one(pid, lang, contract, cases)
            results.append(r)
            status = "PASS" if r["outcome"] == "verified" else "FAIL"
            print(f"[{status}] {lang:10s} {pid:16s} {r['outcome']:18s} {r['detail'][:100]}", flush=True)
            if r["outcome"] == "verified":
                ledger.record_cell(
                    con, problem_id=pid, language=lang, mode="function",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=_ADAPTER_VERSION[lang],
                    contract_version=cv, test_suite_version=tsv,
                    duration_ms=r["duration_ms"],
                )

    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL attempted: {len(results)}  skipped (already verified): {skipped_already_verified}")
    print(f"verified={len(verified)}  reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")

    (REPO_ROOT / "docs" / "atlascode-sort-family-scaling.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
