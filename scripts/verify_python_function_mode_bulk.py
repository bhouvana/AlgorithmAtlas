"""Bulk, automated Python Function Mode runtime verification across every
problem that has BOTH a function_contract AND an auto-derivable reference
solution -- no hand-authored per-problem solution required (that approach
doesn't scale past a handful of problems; see verify_js_function_mode.py for
the hand-authored style used on just the original 6).

Two auto-derivation strategies, both grounded in real, already-existing code
(never invented):
  1. `mutates_argument` contracts (the 21 in-place-sort problems): Python's
     builtin `list.sort()` IS a correct reference solution for "sort this
     array", independent of which specific algorithm name the problem uses --
     the end STATE is what Function Mode checks, not the algorithm.
  2. Contracts backed by a family factory `oracle` callable
     (scripts/migrate_atlascode_function_mode.py's `load_family_oracles()`):
     the oracle itself becomes the reference solution, wrapped in a thin
     Python function matching the contract's declared name/parameter order.

For each: run the REAL 40-case (or however many) corpus through the REAL
Python subprocess judge (`evaluate_function`) with (a) the auto-derived
CORRECT solution -- must be all-Accepted, and (b) a generically-corrupted
WRONG variant -- must be rejected on at least one case (proves the corpus
isn't vacuously weak). Every result is a REAL subprocess execution, not
inferred.
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

import migrate_atlascode_function_mode as M

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"
BACKEND_ROOT = REPO_ROOT / "apps" / "backend"


def _maybe_json(value):
    return json.loads(value) if isinstance(value, str) else value


def load_all_contracted_problems() -> list[tuple[str, FunctionContract, list[FunctionCase]]]:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT id, function_contract FROM problems WHERE function_contract IS NOT NULL ORDER BY id")
    problems = cur.fetchall()
    out = []
    for row in problems:
        pid = row["id"]
        contract = FunctionContract.from_dict(json.loads(row["function_contract"]))
        cur.execute(
            "SELECT id, function_args, function_expected, \"order\" FROM test_cases "
            "WHERE problem_id = ? AND function_args IS NOT NULL ORDER BY \"order\"",
            (pid,),
        )
        cases = [
            FunctionCase(
                id=r["id"], arguments=_maybe_json(r["function_args"]),
                expected=_maybe_json(r["function_expected"]), has_expected=True,
                is_hidden=False, order=r["order"],
            )
            for r in cur.fetchall()
        ]
        out.append((pid, contract, cases))
    con.close()
    return out


def _corrupt_expr_for_return(contract: FunctionContract, real_call: str) -> str:
    rt = contract.return_type
    if rt.kind == "boolean":
        return f"(not ({real_call}))"
    if rt.kind == "integer":
        return f"(({real_call}) + 1)"
    if rt.kind == "float":
        return f"(({real_call}) + 1.0)"
    if rt.kind == "string":
        return f"(({real_call}) + 'X')"
    if rt.kind == "array":
        return f"(list(reversed({real_call})) if ({real_call}) else [999999999])"
    if rt.kind == "tree":
        # real_call evaluates to an actual TreeNode object here (or None),
        # never a list -- `list(reversed(...))` (the array corruption above)
        # would crash on a non-iterable TreeNode. Bumping the root's value
        # is a minimal, always-applicable corruption that changes the
        # serialized level-order array for every non-empty tree case.
        return f"(lambda __r: (setattr(__r, 'val', __r.val + 1), __r)[1] if __r is not None else __r)({real_call})"
    return f"({real_call})"


_SERIALIZE_HELPER_PY = (
    "def __atlas_tree_to_array(root):\n"
    "    if root is None:\n"
    "        return []\n"
    "    out = [root.val]\n"
    "    queue = [root]\n"
    "    qi = 0\n"
    "    while qi < len(queue):\n"
    "        node = queue[qi]\n"
    "        qi += 1\n"
    "        for child in (node.left, node.right):\n"
    "            if child is None:\n"
    "                out.append(None)\n"
    "            else:\n"
    "                out.append(child.val)\n"
    "                queue.append(child)\n"
    "    while out and out[-1] is None:\n"
    "        out.pop()\n"
    "    return out\n"
)


# A real, generic Function Mode contract takes ONE `intervals: array<array<int>>`
# parameter -- but these 2 problems' independent oracles (written before
# Function Mode existed, for Program Mode's own parallel-arrays stdin
# parsing convention: `starts = [...]; ends = [...]`) take TWO separate
# arrays instead. This is a real, permanent calling-convention mismatch
# between the oracle and the contract, not something either side should
# change (the contract matches the actual Function Mode starter code
# real users see; the oracle is shared/independent and used by other call
# sites) -- so the verification harness unzips here, once, explicitly.
_INTERVAL_UNZIP_PIDS = {"insert-interval", "merge-overlapping-intervals"}


def _build_interval_unzip_wrapper(contract: FunctionContract, oracle_module: str, oracle_name: str, wrong: bool) -> str:
    params = ", ".join(contract.parameter_names)
    other_params = [p for p in contract.parameter_names if p != "intervals"]
    real_call = f"__oracle_fn([p[0] for p in intervals], [p[1] for p in intervals], {', '.join(other_params)})"
    body = _corrupt_expr_for_return(contract, real_call) if wrong else real_call
    return (
        f"import sys\n"
        f"sys.path.insert(0, {str(BACKEND_ROOT)!r})\n"
        f"from {oracle_module} import {oracle_name} as __oracle_fn\n"
        f"def {contract.function_name}({params}):\n"
        f"    return {body}\n"
    )


def build_oracle_wrapper(pid: str, contract: FunctionContract, oracle, wrong: bool) -> str | None:
    if pid in _INTERVAL_UNZIP_PIDS:
        return _build_interval_unzip_wrapper(contract, oracle.__module__, oracle.__name__, wrong)

    # Independent oracles for tree problems take the RAW BFS array and build
    # their own internal tree (see independent_oracles.binary_tree_max_path_sum)
    # -- but by the time OUR driver calls this wrapper, tree-typed parameters
    # have already been converted to a real TreeNode object (matching what a
    # genuine user submission receives). Convert back to an array for the
    # oracle call; this is purely a verification-harness bridging detail, not
    # a contract or adapter behavior change.
    tree_params = {p.name for p in contract.parameters if p.type.kind == "tree"}
    call_args = [
        f"__atlas_tree_to_array({name})" if name in tree_params else name
        for name in contract.parameter_names
    ]
    real_call = f"__oracle_fn({', '.join(call_args)})"
    # An oracle whose return is itself the tree-shaped answer (e.g.
    # construct-tree-preorder-inorder's oracle returns its own raw BFS array
    # -- see the function's own docstring) must be rebuilt into a real
    # TreeNode graph before returning, since compose_source's tree-return
    # path (`__atlas_serialize_tree(__atlas_result)`) expects an actual
    # `.val/.left/.right` object, not a plain list. `__atlas_build_tree` is
    # defined later in the SAME composed module (by adapters.py's
    # compose_source, in the driver block) -- safe to reference here since
    # Python only resolves it at call time, well after the whole module has
    # finished executing top-to-bottom.
    if contract.return_type.kind == "tree":
        real_call = f"__atlas_build_tree({real_call})"
    # An oracle returning a raw list where the contract's return type is
    # "string" (e.g. prime-factorization/sieve-of-eratosthenes: independent
    # oracles return `list[int]`, but Program Mode's own driver joins that
    # list with spaces before printing, which is what the contract's
    # return_type actually reflects) -- format exactly like every other
    # space-joined array-of-scalars problem in this codebase, without
    # calling the oracle twice.
    elif contract.return_type.kind == "string":
        real_call = f"(lambda __v: __v if isinstance(__v, str) else ' '.join(map(str, __v)))({real_call})"
    if wrong:
        body = _corrupt_expr_for_return(contract, real_call)
    else:
        body = real_call
    params = ", ".join(contract.parameter_names)
    helper = _SERIALIZE_HELPER_PY if tree_params else ""
    if oracle.__name__ == "<lambda>":
        # Can't import an anonymous lambda by name (it has no bound name at
        # module scope, e.g. linked_list_variants.py's inline
        # `oracle=lambda values, pos: ...`) -- re-look-up the SAME callable
        # via its family module's _SPECS dict instead, which is exactly
        # where load_family_oracles() found it in the first place. This
        # path is ONLY for lambdas: most oracles (independent_oracles.py
        # functions referenced from a _SPECS dict via `oracle=oracles.foo`)
        # have `oracle.__module__` pointing at independent_oracles.py
        # itself, which has no `_SPECS` dict at all -- using this lookup
        # unconditionally regressed ~150 previously-passing problems the
        # first time this was tried (ImportError: cannot import name
        # '_SPECS' from '...independent_oracles'), caught by re-running the
        # full bulk verification immediately after the change.
        import_lines = (
            f"from {oracle.__module__} import _SPECS as __specs\n"
            f"__oracle_fn = __specs[{pid!r}].oracle\n"
        )
    else:
        import_lines = f"from {oracle.__module__} import {oracle.__name__} as __oracle_fn\n"
    return (
        f"import sys\n"
        f"sys.path.insert(0, {str(BACKEND_ROOT)!r})\n"
        f"{import_lines}"
        f"{helper}"
        f"def {contract.function_name}({params}):\n"
        f"    return {body}\n"
    )


def build_sort_wrapper(contract: FunctionContract, wrong: bool) -> str:
    params = ", ".join(contract.parameter_names)
    mutated = contract.mutates_argument
    if wrong:
        # Sorts DESCENDING instead of ascending -- wrong for any problem
        # whose corpus contains a non-palindromic unsorted array (true for
        # basically every real case in a 40-case corpus).
        body = f"    {mutated}.sort(reverse=True)\n"
    else:
        body = f"    {mutated}.sort()\n"
    return f"def {contract.function_name}({params}):\n{body}    return None\n"


async def _verify_one(pid: str, contract: FunctionContract, cases: list[FunctionCase], oracle_of: dict) -> tuple[str, str, str | None]:
    """Returns (pid, outcome, detail). outcome in:
    auto_verified | correct_only | skipped | failure."""
    if not cases:
        return pid, "skipped", None
    if contract.mutates_argument is not None:
        correct_src = build_sort_wrapper(contract, wrong=False)
        wrong_src = build_sort_wrapper(contract, wrong=True)
    else:
        oracle = oracle_of.get(pid)
        if oracle is None:
            return pid, "skipped", None
        correct_src = build_oracle_wrapper(pid, contract, oracle, wrong=False)
        wrong_src = build_oracle_wrapper(pid, contract, oracle, wrong=True)

    try:
        correct_result = await evaluate_function(correct_src, "python", contract, cases)
        n_pass = sum(1 for r in correct_result.case_results if r.passed)
        if n_pass != len(cases):
            sample_fail = next((r for r in correct_result.case_results if not r.passed), None)
            detail = (
                f"reference solution only {n_pass}/{len(cases)} -- verdict={correct_result.verdict} "
                f"sample={sample_fail.verdict if sample_fail else '?'} stderr={(sample_fail.stderr or '')[:150] if sample_fail else ''}"
            )
            return pid, "failure", detail

        wrong_result = await evaluate_function(wrong_src, "python", contract, cases)
        n_wrong_pass = sum(1 for r in wrong_result.case_results if r.passed)
        if n_wrong_pass < len(cases):
            return pid, "auto_verified", None
        return pid, "failure", f"WEAK CORPUS -- corrupted solution still passed all {len(cases)} cases"
    except Exception as e:
        return pid, "failure", f"exception during verification: {e!r}"


async def main() -> int:
    problems = load_all_contracted_problems()
    oracle_of = M.load_family_oracles()

    verified: list[str] = []
    rejected_ok: list[str] = []
    skipped_no_solution: list[str] = []
    failures: list[str] = []

    sem = asyncio.Semaphore(10)  # bounded concurrency across INDEPENDENT problems

    async def _bounded(pid, contract, cases):
        async with sem:
            return await _verify_one(pid, contract, cases, oracle_of)

    t0 = time.monotonic()
    tasks = [asyncio.create_task(_bounded(pid, contract, cases)) for pid, contract, cases in problems]
    done = 0
    for coro in asyncio.as_completed(tasks):
        pid, outcome, detail = await coro
        done += 1
        if outcome == "auto_verified":
            verified.append(pid)
            rejected_ok.append(pid)
        elif outcome == "skipped":
            skipped_no_solution.append(pid)
        elif outcome == "failure":
            failures.append(f"{pid}: {detail}")
        if done % 25 == 0:
            elapsed = time.monotonic() - t0
            print(f"[{done}/{len(problems)}] rate={done/elapsed:.1f}/sec verified={len(rejected_ok)} failures={len(failures)}")

    print("\nBULK PYTHON FUNCTION MODE RUNTIME VERIFICATION")
    print(f"  total contracted problems: {len(problems)}")
    print(f"  auto-verified (correct=all-pass, wrong=rejected): {len(rejected_ok)}")
    print(f"  correct-passed but corpus didn't reject wrong: {len(verified) - len(rejected_ok)}")
    print(f"  skipped (no auto-derivable reference solution): {len(skipped_no_solution)}")
    print(f"  failures: {len(failures)}")
    for f in failures[:40]:
        print(f"    - {f}")

    report = {
        "auto_verified": rejected_ok,
        "correct_only_no_rejection_check": [p for p in verified if p not in rejected_ok],
        "skipped_no_reference": skipped_no_solution,
        "failures": failures,
    }
    (REPO_ROOT / "docs" / "atlascode-function-mode-python-runtime-verification.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
