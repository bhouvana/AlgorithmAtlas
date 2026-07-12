"""Export the live `atlascode_matrix_ledger` table to a small, committable
JSON snapshot -- apps/backend/algorithm_atlas/atlascode/ledger_snapshot.json.

Why this exists: atlas.db itself is gitignored (231MB+, over GitHub's
100MB hard limit, and it's a full SQLite file with WAL/schema baggage that
doesn't belong in git). But the ledger TABLE alone -- one row per verified
(problem_id, language, mode) cell -- is small (a few hundred KB even at
thousands of rows) and is exactly the data a fresh deploy/clone needs to
know "this language/mode combo is already verified" without re-running the
real judge against every toolchain.

The snapshot is loaded by apps/backend/algorithm_atlas/atlascode/ledger_snapshot.py
during boot-time auto-seed (see main.py's _auto_seed_atlascode_if_empty) so
a fresh database gets the CURRENT verified-language state, not just a
Python-only fallback.

Re-run this any time local verification work adds new ledger rows, then
commit the refreshed snapshot -- it is a point-in-time export, not a live
sync. Safe to run any time: read-only against atlas.db, purely additive
(overwrites the snapshot file only).

Usage: python scripts/export_ledger_snapshot.py
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"
OUT_PATH = REPO_ROOT / "apps" / "backend" / "algorithm_atlas" / "atlascode" / "ledger_snapshot.json"

_COLUMNS = [
    "problem_id", "language", "mode", "verification_level", "status",
    "adapter_version", "contract_version", "test_suite_version",
    "toolchain_version", "failure_class", "failure_message",
    "duration_ms", "timestamp",
]


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        f"SELECT {', '.join(_COLUMNS)} FROM atlascode_matrix_ledger "
        "ORDER BY problem_id, language, mode"
    ).fetchall()
    con.close()

    data = {
        "generated_from": "scripts/export_ledger_snapshot.py (live atlas.db, no hand-typed rows)",
        "row_count": len(rows),
        "rows": [dict(r) for r in rows],
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, indent=None, separators=(",", ":")), encoding="utf-8")
    print(f"Exported {len(rows)} ledger rows to {OUT_PATH} ({OUT_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
