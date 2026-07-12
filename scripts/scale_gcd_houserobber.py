"""Scales gcd-euclidean and house-robber (Function Mode) across the 8
working languages -- both simple, well-understood, single-pass algorithms,
neither part of the bigint-blocked list (docs/atlascode-bigint-numeric-audit.json).
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
_TARGET_LANGUAGES = ["javascript", "typescript", "java", "cpp", "csharp", "perl", "c", "rust"]


def _js_gcd(wrong):
    a = " + 1" if wrong else ""
    return (
        "function gcd(a, b) {\n"
        "    a = Math.abs(a); b = Math.abs(b);\n"
        "    while (b !== 0) { const t = b; b = a % b; a = t; }\n"
        f"    return a{a};\n"
        "}\n"
    )


def _ts_gcd(wrong):
    a = " + 1" if wrong else ""
    return (
        "function gcd(a: number, b: number): number {\n"
        "    a = Math.abs(a); b = Math.abs(b);\n"
        "    while (b !== 0) { const t = b; b = a % b; a = t; }\n"
        f"    return a{a};\n"
        "}\n"
    )


def _java_gcd(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public int gcd(int a, int b) {\n"
        "        a = Math.abs(a); b = Math.abs(b);\n"
        "        while (b != 0) { int t = b; b = a % b; a = t; }\n"
        f"        return a{a};\n"
        "    }\n"
        "}\n"
    )


def _cpp_gcd(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "public:\n"
        "    int gcd(int a, int b) {\n"
        "        a = std::abs(a); b = std::abs(b);\n"
        "        while (b != 0) { int t = b; b = a % b; a = t; }\n"
        f"        return a{a};\n"
        "    }\n"
        "};\n"
    )


def _csharp_gcd(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public static int gcd(int a, int b) {\n"
        "        a = System.Math.Abs(a); b = System.Math.Abs(b);\n"
        "        while (b != 0) { int t = b; b = a % b; a = t; }\n"
        f"        return a{a};\n"
        "    }\n"
        "}\n"
    )


def _perl_gcd(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub gcd {\n"
        "    my ($a, $b) = @_;\n"
        "    $a = abs($a); $b = abs($b);\n"
        "    while ($b != 0) { my $t = $b; $b = $a % $b; $a = $t; }\n"
        f"    return $a{a};\n"
        "}\n"
    )


def _c_gcd(wrong):
    a = " + 1" if wrong else ""
    return (
        "int gcd(int a, int b) {\n"
        "    a = a < 0 ? -a : a; b = b < 0 ? -b : b;\n"
        "    while (b != 0) { int t = b; b = a % b; a = t; }\n"
        f"    return a{a};\n"
        "}\n"
    )


def _rust_gcd(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn gcd(a: i32, b: i32) -> i32 {\n"
        "    let mut a = a.abs(); let mut b = b.abs();\n"
        "    while b != 0 { let t = b; b = a % b; a = t; }\n"
        f"    a{a}\n"
        "}\n"
    )


def _js_rob(wrong):
    a = " + 1" if wrong else ""
    return (
        "function rob(nums) {\n"
        "    let prev = 0, cur = 0;\n"
        "    for (const x of nums) { const t = Math.max(cur, prev + x); prev = cur; cur = t; }\n"
        f"    return cur{a};\n"
        "}\n"
    )


def _ts_rob(wrong):
    a = " + 1" if wrong else ""
    return (
        "function rob(nums: number[]): number {\n"
        "    let prev = 0, cur = 0;\n"
        "    for (const x of nums) { const t = Math.max(cur, prev + x); prev = cur; cur = t; }\n"
        f"    return cur{a};\n"
        "}\n"
    )


def _java_rob(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public int rob(int[] nums) {\n"
        "        int prev = 0, cur = 0;\n"
        "        for (int x : nums) { int t = Math.max(cur, prev + x); prev = cur; cur = t; }\n"
        f"        return cur{a};\n"
        "    }\n"
        "}\n"
    )


def _cpp_rob(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "public:\n"
        "    int rob(std::vector<int> nums) {\n"
        "        int prev = 0, cur = 0;\n"
        "        for (int x : nums) { int t = std::max(cur, prev + x); prev = cur; cur = t; }\n"
        f"        return cur{a};\n"
        "    }\n"
        "};\n"
    )


def _csharp_rob(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public static int rob(int[] nums) {\n"
        "        int prev = 0, cur = 0;\n"
        "        foreach (int x in nums) { int t = System.Math.Max(cur, prev + x); prev = cur; cur = t; }\n"
        f"        return cur{a};\n"
        "    }\n"
        "}\n"
    )


def _perl_rob(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub rob {\n"
        "    my ($nums) = @_;\n"
        "    my $prev = 0; my $cur = 0;\n"
        "    foreach my $x (@$nums) { my $t = ($cur > $prev + $x) ? $cur : $prev + $x; $prev = $cur; $cur = $t; }\n"
        f"    return $cur{a};\n"
        "}\n"
    )


def _c_rob(wrong):
    a = " + 1" if wrong else ""
    return (
        "int rob(AtlasIntArray nums) {\n"
        "    int prev = 0, cur = 0;\n"
        "    for (int i=0;i<nums.size;i++) {\n"
        "        int withCur = prev + nums.data[i];\n"
        "        int t = cur > withCur ? cur : withCur;\n"
        "        prev = cur; cur = t;\n"
        "    }\n"
        f"    return cur{a};\n"
        "}\n"
    )


def _rust_rob(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn rob(nums: Vec<i32>) -> i32 {\n"
        "    let mut prev = 0; let mut cur = 0;\n"
        "    for x in nums.iter() { let t = cur.max(prev + x); prev = cur; cur = t; }\n"
        f"    cur{a}\n"
        "}\n"
    )


_BUILDERS = {
    "gcd-euclidean": {"javascript": _js_gcd, "typescript": _ts_gcd, "java": _java_gcd, "cpp": _cpp_gcd,
                      "csharp": _csharp_gcd, "perl": _perl_gcd, "c": _c_gcd, "rust": _rust_gcd},
    "house-robber": {"javascript": _js_rob, "typescript": _ts_rob, "java": _java_rob, "cpp": _cpp_rob,
                     "csharp": _csharp_rob, "perl": _perl_rob, "c": _c_rob, "rust": _rust_rob},
}


def _maybe_json(v):
    return json.loads(v) if isinstance(v, str) else v


def load_problem(con, pid):
    row = con.execute("SELECT function_contract, test_suite_version FROM problems WHERE id=?", (pid,)).fetchone()
    contract = FunctionContract.from_dict(json.loads(row["function_contract"]))
    cur = con.execute(
        "SELECT id, function_args, function_expected, \"order\" FROM test_cases "
        "WHERE problem_id=? AND function_args IS NOT NULL ORDER BY \"order\"", (pid,),
    )
    cases = [
        FunctionCase(id=r["id"], arguments=_maybe_json(r["function_args"]), expected=_maybe_json(r["function_expected"]),
                     has_expected=True, is_hidden=False, order=r["order"])
        for r in cur.fetchall()
    ]
    return contract, cases, row["function_contract"], row["test_suite_version"]


async def verify_one(pid, lang, contract, cases, build):
    t0 = time.monotonic()
    correct_result = await evaluate_function(build(False), lang, contract, cases)
    n_pass = sum(1 for r in correct_result.case_results if r.passed)
    if n_pass != len(cases):
        sample_fail = next((r for r in correct_result.case_results if not r.passed), None)
        return {"pid": pid, "lang": lang, "outcome": "reference_failed",
                "detail": f"{n_pass}/{len(cases)} verdict={correct_result.verdict} "
                          f"compile={(correct_result.compile_output or '')[:150]} "
                          f"stderr={(sample_fail.stderr if sample_fail else '')[:150]}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    wrong_result = await evaluate_function(build(True), lang, contract, cases)
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
    for pid, builders in _BUILDERS.items():
        for lang in _TARGET_LANGUAGES:
            contract, cases, raw, tsv = load_problem(con, pid)
            cv = ledger.contract_hash(raw)
            if ledger.already_verified(con, pid, lang, "function", contract_version=cv, test_suite_version=tsv):
                skipped += 1
                continue
            r = await verify_one(pid, lang, contract, cases, builders[lang])
            results.append(r)
            status = "PASS" if r["outcome"] == "verified" else "FAIL"
            print(f"[{status}] {lang:10s} {pid:16s} {r['outcome']:18s} {r['detail'][:100]}", flush=True)
            if r["outcome"] == "verified":
                ledger.record_cell(con, problem_id=pid, language=lang, mode="function",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=f"{lang}-simple-v1", contract_version=cv, test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
