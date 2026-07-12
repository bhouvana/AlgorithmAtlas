"""
Real, live verification of the JavaScript Function Mode adapter against the
6 already-migrated problems' REAL DB test cases (the same 240 typed cases
Python Function Mode already uses -- never a second corpus, per
docs/atlascode-dual-run-modes.md's rule).

For each problem this actually runs the judge (real `node` subprocess, real
JS driver composition) with:
  1. a correct reference JS solution -> must be Accepted (40/40)
  2. a deliberately wrong JS solution -> must fail at least one case
  3. (one problem) a partial-credit solution -> must show a genuine
     mixed pass/fail count, proving per-case result plumbing works, not
     just all-or-nothing

This is Phase 24/28/29 for the javascript adapter: adapter unit +
correct-passes + wrong-rejected + partial-pass, all against real execution,
not asserted from code review.

Run from repo root: python scripts/verify_js_function_mode.py
"""
from __future__ import annotations

import asyncio
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))
import logging
logging.disable(logging.CRITICAL)

from algorithm_atlas.atlascode.function_mode.contracts import FunctionContract
from algorithm_atlas.atlascode.function_mode.runner import FunctionCase, evaluate_function

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"

CORRECT_JS = {
    "contains-duplicate-within-k": """
function contains_nearby_duplicate(nums, k) {
  const lastSeen = {};
  for (let i = 0; i < nums.length; i++) {
    const x = nums[i];
    if (Object.prototype.hasOwnProperty.call(lastSeen, x) && i - lastSeen[x] <= k) return true;
    lastSeen[x] = i;
  }
  return false;
}
""",
    "product-of-array-except-self": """
function product_except_self(nums) {
  const n = nums.length;
  const result = new Array(n).fill(1);
  let prefix = 1;
  for (let i = 0; i < n; i++) { result[i] = prefix; prefix *= nums[i]; }
  let suffix = 1;
  for (let i = n - 1; i >= 0; i--) { result[i] *= suffix; suffix *= nums[i]; }
  return result;
}
""",
    "subarray-sum-equals-k": """
function subarray_sum(nums, k) {
  const counts = new Map([[0, 1]]);
  let total = 0, result = 0;
  for (const x of nums) {
    total += x;
    result += counts.get(total - k) || 0;
    counts.set(total, (counts.get(total) || 0) + 1);
  }
  return result;
}
""",
    "top-k-frequent-elements": """
function top_k_frequent(nums, k) {
  const counts = new Map();
  for (const x of nums) counts.set(x, (counts.get(x) || 0) + 1);
  const items = Array.from(counts.entries());
  items.sort((a, b) => (b[1] - a[1]) || (a[0] - b[0]));
  return items.slice(0, k).map(([v]) => v);
}
""",
    "longest-consecutive-sequence": """
function longest_consecutive(nums) {
  const s = new Set(nums);
  let best = 0;
  for (const x of s) {
    if (!s.has(x - 1)) {
      let length = 1;
      while (s.has(x + length)) length++;
      best = Math.max(best, length);
    }
  }
  return best;
}
""",
    "two-sum-count-pairs": """
function count_pairs(nums, target) {
  const seen = new Map();
  let count = 0;
  for (const x of nums) {
    count += seen.get(target - x) || 0;
    seen.set(x, (seen.get(x) || 0) + 1);
  }
  return count;
}
""",
}

WRONG_JS = {
    # Off-by-one: strict '<' instead of '<=' -- misses the boundary case k apart.
    "contains-duplicate-within-k": """
function contains_nearby_duplicate(nums, k) {
  const lastSeen = {};
  for (let i = 0; i < nums.length; i++) {
    const x = nums[i];
    if (Object.prototype.hasOwnProperty.call(lastSeen, x) && i - lastSeen[x] < k) return true;
    lastSeen[x] = i;
  }
  return false;
}
""",
    # Only the prefix pass -- ignores the suffix multiplication entirely.
    "product-of-array-except-self": """
function product_except_self(nums) {
  const n = nums.length;
  const result = new Array(n).fill(1);
  let prefix = 1;
  for (let i = 0; i < n; i++) { result[i] = prefix; prefix *= nums[i]; }
  return result;
}
""",
    # Missing the {0: 1} base case -- undercounts subarrays starting at index 0.
    "subarray-sum-equals-k": """
function subarray_sum(nums, k) {
  const counts = new Map();
  let total = 0, result = 0;
  for (const x of nums) {
    total += x;
    result += counts.get(total - k) || 0;
    counts.set(total, (counts.get(total) || 0) + 1);
  }
  return result;
}
""",
    # No deterministic tie-break -- fails whenever two values share a frequency.
    "top-k-frequent-elements": """
function top_k_frequent(nums, k) {
  const counts = new Map();
  for (const x of nums) counts.set(x, (counts.get(x) || 0) + 1);
  const items = Array.from(counts.entries());
  items.sort((a, b) => b[1] - a[1]);
  return items.slice(0, k).map(([v]) => v);
}
""",
    # Returns distinct-element count instead of the longest consecutive run.
    "longest-consecutive-sequence": """
function longest_consecutive(nums) {
  return new Set(nums).size;
}
""",
    # Counts ordered pairs both ways (i,j) and (j,i) -- double-counts.
    "two-sum-count-pairs": """
function count_pairs(nums, target) {
  let count = 0;
  for (let i = 0; i < nums.length; i++) {
    for (let j = 0; j < nums.length; j++) {
      if (i !== j && nums[i] + nums[j] === target) count++;
    }
  }
  return count;
}
""",
}

# One deliberately PARTIAL solution (correct algorithm capped to only look at
# the first 2 elements) to prove per-case pass/fail plumbing, not just
# all-pass / all-fail.
PARTIAL_JS = {
    "two-sum-count-pairs": """
function count_pairs(nums, target) {
  const capped = nums.slice(0, 2);
  const seen = new Map();
  let count = 0;
  for (const x of capped) {
    count += seen.get(target - x) || 0;
    seen.set(x, (seen.get(x) || 0) + 1);
  }
  return count;
}
""",
}


def _maybe_json(value):
    """SQLite's JSON columns store scalar values (int/bool/str) as their
    native SQLite type but compound values (list/dict) as serialized JSON
    text -- only decode when it's actually a string."""
    return json.loads(value) if isinstance(value, str) else value


def load_problem(pid: str) -> tuple[FunctionContract, list[FunctionCase]]:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT function_contract FROM problems WHERE id = ?", (pid,))
    row = cur.fetchone()
    contract = FunctionContract.from_dict(json.loads(row["function_contract"]))
    cur.execute(
        "SELECT id, function_args, function_expected, \"order\" FROM test_cases "
        "WHERE problem_id = ? ORDER BY \"order\"",
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
    con.close()
    return contract, cases


async def main() -> int:
    failures = []
    for pid, correct_code in CORRECT_JS.items():
        contract, cases = load_problem(pid)
        assert len(cases) == 40, f"{pid}: expected 40 cases, got {len(cases)}"

        result = await evaluate_function(correct_code, "javascript", contract, cases)
        n_passed = sum(1 for r in result.case_results if r.passed)
        ok = n_passed == 40
        print(f"[correct] {pid}: {n_passed}/40 passed, verdict={result.verdict} {'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append(f"{pid}: correct solution only passed {n_passed}/40")

        wrong_code = WRONG_JS[pid]
        wrong_result = await evaluate_function(wrong_code, "javascript", contract, cases)
        n_wrong_passed = sum(1 for r in wrong_result.case_results if r.passed)
        rejected = n_wrong_passed < 40
        print(f"[wrong]   {pid}: {n_wrong_passed}/40 passed (should be <40) {'OK' if rejected else 'FAIL -- weak test data!'}")
        if not rejected:
            failures.append(f"{pid}: wrong solution passed all 40 -- test corpus too weak to catch it")

    for pid, partial_code in PARTIAL_JS.items():
        contract, cases = load_problem(pid)
        result = await evaluate_function(partial_code, "javascript", contract, cases)
        n_passed = sum(1 for r in result.case_results if r.passed)
        is_partial = 0 < n_passed < 40
        print(f"[partial] {pid}: {n_passed}/40 passed {'OK (genuine partial)' if is_partial else 'FAIL -- expected a mixed result'}")
        if not is_partial:
            failures.append(f"{pid}: partial-credit solution did not produce a mixed pass/fail count ({n_passed}/40)")

    # Contract Error smoke test: a solution that never defines the required function.
    contract, cases = load_problem("two-sum-count-pairs")
    missing_result = await evaluate_function("function not_the_right_name() {}", "javascript", contract, cases[:1])
    missing_ok = missing_result.case_results[0].verdict == "Function Contract Error"
    print(f"[contract-error] missing function -> verdict={missing_result.case_results[0].verdict} {'OK' if missing_ok else 'FAIL'}")
    if not missing_ok:
        failures.append("missing-function case did not produce Function Contract Error")

    print()
    if failures:
        print(f"{len(failures)} FAILURE(S):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("All JavaScript Function Mode checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
