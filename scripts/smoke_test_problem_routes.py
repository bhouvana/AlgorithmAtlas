"""
Phase 50 route smoke test, API layer: hit GET /api/v1/problems/{slug} for
EVERY real problem in the DB (all 216, not a sample) and assert the shape
the frontend actually depends on is present and internally consistent --
this is the check that would have caught the blank-page bug's underlying
data shape issue before it ever reached a browser.

Requires the backend running on localhost:8000.
Run from repo root: python scripts/smoke_test_problem_routes.py
"""
from __future__ import annotations

import sqlite3
import sys
import urllib.request
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"
BASE = "http://localhost:8000/api/v1/problems"

REQUIRED_KEYS = {
    "id", "title", "difficulty", "category", "problem_statement", "examples",
    "constraints", "algorithm_slug", "starter_code", "function_contract",
    "starter_code_function", "visible_test_cases",
}


def all_problem_ids() -> list[str]:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT id FROM problems ORDER BY id")
    ids = [r[0] for r in cur.fetchall()]
    con.close()
    return ids


def check_one(pid: str) -> list[str]:
    problems = []
    try:
        with urllib.request.urlopen(f"{BASE}/{pid}", timeout=10) as resp:
            if resp.status != 200:
                return [f"{pid}: HTTP {resp.status}"]
            data = json.loads(resp.read())
    except Exception as e:
        return [f"{pid}: request failed -- {e}"]

    missing = REQUIRED_KEYS - data.keys()
    if missing:
        problems.append(f"{pid}: missing keys {missing}")

    # The exact shape that once crashed the frontend: function_contract must
    # be present (even if null), starter_code_function must be an object.
    if "function_contract" in data and data["function_contract"] is not None and not isinstance(data["function_contract"], dict):
        problems.append(f"{pid}: function_contract is neither null nor an object")
    if "starter_code_function" in data and not isinstance(data["starter_code_function"], dict):
        problems.append(f"{pid}: starter_code_function is not an object")
    if "starter_code" in data and not isinstance(data["starter_code"], dict):
        problems.append(f"{pid}: starter_code is not an object")
    if "python" not in data.get("starter_code", {}):
        problems.append(f"{pid}: no python starter_code (Program Mode baseline requires at least one language)")
    if not data.get("visible_test_cases"):
        problems.append(f"{pid}: zero visible_test_cases -- Testcase tab would render empty")

    return problems


def main() -> int:
    ids = all_problem_ids()
    all_problems: list[str] = []
    for i, pid in enumerate(ids, 1):
        issues = check_one(pid)
        all_problems.extend(issues)
        if i % 50 == 0 or i == len(ids):
            print(f"[{i}/{len(ids)}] checked...")

    print()
    if all_problems:
        print(f"{len(all_problems)} ISSUE(S) across {len(ids)} problems:")
        for p in all_problems:
            print(f"  - {p}")
        return 1
    print(f"All {len(ids)} problem routes returned a well-shaped response. 0 issues.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
