"""Backfills the persistent matrix ledger (scripts/atlascode_ledger.py) with
every problem scripts/verify_python_function_mode_bulk.py already proved
Level 6 (real correct-solution-passes + real wrong-solution-rejected) for
Python -- so the ledger becomes the single comprehensive source of truth
instead of under-representing work that was verified via the bulk script
before the ledger existed.

Only records "auto_verified" entries as LEVEL_VERIFIED. "skipped_no_reference"
and "failures" are NOT recorded as any level -- they are genuinely unresolved
(no reference solution available, or an unresolved discrepancy), and the
ledger must never claim a level for a cell that wasn't actually judged.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))
import atlascode_ledger as L


def main() -> None:
    report_path = REPO_ROOT / "docs" / "atlascode-function-mode-python-runtime-verification.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    verified = report.get("auto_verified", [])

    dbcon = sqlite3.connect(L.DB_PATH)
    dbcon.row_factory = sqlite3.Row
    con = L.connect()
    L.ensure_schema(con)

    n = 0
    for pid in verified:
        row = dbcon.execute(
            "SELECT function_contract, test_suite_version FROM problems WHERE id=?", (pid,)
        ).fetchone()
        if row is None:
            continue
        L.record_cell(
            con, problem_id=pid, language="python", mode="function",
            verification_level=L.LEVEL_VERIFIED, status="pass",
            contract_version=L.contract_hash(row["function_contract"]),
            test_suite_version=row["test_suite_version"],
            adapter_version="python-oracle-bulk-v1",
        )
        n += 1

    con.close()
    dbcon.close()
    print(f"Backfilled {n} Python Level-6 cells from {report_path.name}")
    print(f"  skipped_no_reference (not recorded, genuinely unresolved): {len(report.get('skipped_no_reference', []))}")
    print(f"  failures (not recorded, genuinely unresolved): {len(report.get('failures', []))}")


if __name__ == "__main__":
    main()
