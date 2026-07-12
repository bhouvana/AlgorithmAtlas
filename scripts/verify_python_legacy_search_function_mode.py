"""Closes the Python Function Mode gap (mission Phase 8): the 23 problems
`verify_python_function_mode_bulk.py` reports as `skipped_no_reference`.

Root cause (confirmed by reading migrate_atlascode_function_mode.py's
`load_family_oracles()` directly): that function only scans family modules
shaped as a `_SPECS`-keyed dict, and explicitly skips modules named
"searching"/"sorting" by name. Two real oracle sources exist but were never
wired in:
  - `families/legacy_audit_oracles.py` -- 18 independent, plugin-free oracle
    functions for the original curated/canonical problems (not _SPECS-shaped,
    just plain module-level functions).
  - `families/searching.py`'s `_search_oracle` -- a bisect-based ground truth
    shared by all 5 searching-variant problems (exponential/fibonacci/
    interpolation/jump/ternary-search), all of which search a SORTED array
    for the same target, independent of which algorithm name the problem
    teaches.

Every (problem, oracle) pairing below was verified by hand against the
problem's actual function_contract in the DB (parameter names/order,
positional match with the oracle signature) before being added -- not
assumed from naming similarity.

For each of the 23: compose a CORRECT wrapper (calls the oracle directly)
and a WRONG wrapper (a genuine value-level corruption -- integer +1,
boolean negation, or +1 to every element of an integer array), run BOTH
through the real subprocess judge (`evaluate_function`) against the REAL
DB test corpus, and only record Level 6 in `atlascode_matrix_ledger` if the
correct wrapper is all-Accepted AND the wrong wrapper is rejected on at
least one case. Anything else is reported honestly, never silently upgraded.
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
BACKEND_ROOT = REPO_ROOT / "apps" / "backend"

# problem_id -> (module dotted path, oracle function name, needs_tuple_to_list)
_LEGACY_ORACLES: dict[str, tuple[str, str, bool]] = {
    "binary-search": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "binary_search_index", False),
    "linear-search": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "linear_search_first_index", False),
    "fibonacci-dp": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "fibonacci", False),
    "gcd-euclidean": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "gcd_euclidean", False),
    "two-sum": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "two_sum_indices", True),
    "maximum-subarray": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "max_subarray", False),
    "coin-change": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "coin_change_min_coins", False),
    "longest-common-subsequence": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "lcs_length", False),
    "house-robber": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "house_robber_max", False),
    "longest-increasing-subsequence": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "lis_length", False),
    "graph-bfs": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "bfs_distances", False),
    "word-break": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "word_break_feasible", False),
    "edit-distance": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "edit_distance", False),
    "unique-paths": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "unique_paths_count", False),
    "n-queens": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "n_queens_count", False),
    "dijkstra-shortest-path": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "dijkstra_distances", False),
    "kmp-string-matching": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "kmp_occurrences", False),
    "minimum-path-sum": ("algorithm_atlas.atlascode.families.legacy_audit_oracles", "min_path_sum", False),
    "exponential-search": ("algorithm_atlas.atlascode.families.searching", "_search_oracle", False),
    "fibonacci-search": ("algorithm_atlas.atlascode.families.searching", "_search_oracle", False),
    "interpolation-search": ("algorithm_atlas.atlascode.families.searching", "_search_oracle", False),
    "jump-search": ("algorithm_atlas.atlascode.families.searching", "_search_oracle", False),
    "ternary-search": ("algorithm_atlas.atlascode.families.searching", "_search_oracle", False),
}


def _maybe_json(value):
    return json.loads(value) if isinstance(value, str) else value


def _corrupt(contract: FunctionContract, real_call: str) -> str:
    rt = contract.return_type
    if rt.kind == "boolean":
        return f"(not ({real_call}))"
    if rt.kind == "integer":
        return f"(({real_call}) + 1)"
    if rt.kind == "array" and rt.items is not None and rt.items.kind == "integer":
        # Value-level shift, not a reorder -- safe against a "sorted"
        # comparator (two-sum), which would neuter a plain reversal since
        # sorting a reversed 2-element array is a no-op.
        return f"([(_x + 1) for _x in ({real_call})])"
    raise ValueError(f"no corruption strategy for return kind {rt.kind!r}")


def build_wrapper(contract: FunctionContract, module_path: str, oracle_name: str, tuple_to_list: bool, wrong: bool) -> str:
    params = ", ".join(contract.parameter_names)
    real_call = f"__oracle_fn({', '.join(contract.parameter_names)})"
    if tuple_to_list:
        real_call = f"list({real_call})"
    body = _corrupt(contract, real_call) if wrong else real_call
    return (
        f"import sys\n"
        f"sys.path.insert(0, {str(BACKEND_ROOT)!r})\n"
        f"from {module_path} import {oracle_name} as __oracle_fn\n"
        f"def {contract.function_name}({params}):\n"
        f"    return {body}\n"
    )


def load_problem(con: sqlite3.Connection, pid: str) -> tuple[FunctionContract, list[FunctionCase]]:
    cur = con.execute("SELECT function_contract FROM problems WHERE id=?", (pid,))
    row = cur.fetchone()
    contract = FunctionContract.from_dict(json.loads(row[0]))
    cur = con.execute(
        "SELECT id, function_args, function_expected, \"order\" FROM test_cases "
        "WHERE problem_id=? AND function_args IS NOT NULL ORDER BY \"order\"",
        (pid,),
    )
    cases = [
        FunctionCase(
            id=r[0], arguments=_maybe_json(r[1]), expected=_maybe_json(r[2]),
            has_expected=True, is_hidden=False, order=r[3],
        )
        for r in cur.fetchall()
    ]
    return contract, cases


async def verify_one(pid: str, contract: FunctionContract, cases: list[FunctionCase], module_path: str, oracle_name: str, tuple_to_list: bool) -> dict:
    t0 = time.monotonic()
    correct_src = build_wrapper(contract, module_path, oracle_name, tuple_to_list, wrong=False)
    correct_result = await evaluate_function(correct_src, "python", contract, cases)
    n_pass = sum(1 for r in correct_result.case_results if r.passed)
    if n_pass != len(cases):
        sample_fail = next((r for r in correct_result.case_results if not r.passed), None)
        return {
            "pid": pid, "outcome": "reference_failed",
            "detail": f"reference only {n_pass}/{len(cases)} -- verdict={correct_result.verdict} "
                      f"sample={sample_fail.verdict if sample_fail else '?'} "
                      f"stderr={(sample_fail.stderr or '')[:200] if sample_fail else ''}",
            "duration_ms": (time.monotonic() - t0) * 1000,
        }

    wrong_src = build_wrapper(contract, module_path, oracle_name, tuple_to_list, wrong=True)
    wrong_result = await evaluate_function(wrong_src, "python", contract, cases)
    n_wrong_pass = sum(1 for r in wrong_result.case_results if r.passed)
    if n_wrong_pass >= len(cases):
        return {
            "pid": pid, "outcome": "corpus_weakness",
            "detail": f"corrupted solution still passed all {len(cases)} cases",
            "duration_ms": (time.monotonic() - t0) * 1000,
        }
    return {
        "pid": pid, "outcome": "verified", "detail": f"{n_pass}/{len(cases)} correct, wrong rejected on {len(cases) - n_wrong_pass}/{len(cases)}",
        "duration_ms": (time.monotonic() - t0) * 1000,
    }


async def main() -> int:
    con = sqlite3.connect(DB_PATH)
    ledger.ensure_schema(con)

    results = []
    for pid, (module_path, oracle_name, tuple_to_list) in _LEGACY_ORACLES.items():
        contract, cases = load_problem(con, pid)
        if not cases:
            results.append({"pid": pid, "outcome": "no_cases", "detail": "", "duration_ms": 0})
            continue
        r = await verify_one(pid, contract, cases, module_path, oracle_name, tuple_to_list)
        results.append(r)
        status = "PASS" if r["outcome"] == "verified" else "FAIL"
        print(f"[{status}] {pid:32s} {r['outcome']:18s} {r['detail'][:90]}")

    verified = [r for r in results if r["outcome"] == "verified"]
    for r in verified:
        row = con.execute(
            "SELECT function_contract, test_suite_version FROM problems WHERE id=?", (r["pid"],)
        ).fetchone()
        ledger.record_cell(
            con, problem_id=r["pid"], language="python", mode="function",
            verification_level=ledger.LEVEL_VERIFIED, status="pass",
            adapter_version="python-legacy-oracle-v1",
            contract_version=ledger.contract_hash(row[0]),
            test_suite_version=row[1],
            toolchain_version=sys.version.split()[0],
            duration_ms=r["duration_ms"],
        )

    print(f"\nTOTAL: {len(results)}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")

    (REPO_ROOT / "docs" / "atlascode-python-legacy-search-verification.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    con.close()
    return 0 if len(verified) == len(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
