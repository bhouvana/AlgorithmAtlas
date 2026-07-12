"""Loads the committed ledger snapshot (ledger_snapshot.json, alongside this
file) into the live `atlascode_matrix_ledger` table.

Why this exists: atlas.db is gitignored and never travels with the repo, so
a fresh database (a first Render deploy, or anyone cloning the repo) starts
with ZERO verified-language history even though the real local database has
thousands of already-verified (problem_id, language, mode) cells. The
snapshot is a small, committable point-in-time export of that ledger (see
scripts/export_ledger_snapshot.py) -- loading it here means a fresh boot
gets the SAME verified-language state as local development, not just a
Python-only fallback.

Idempotent (INSERT OR IGNORE against the ledger's UNIQUE(problem_id,
language, mode) constraint) and cheap (a few thousand rows) -- safe to call
on every boot, not just when the database is empty, so the ledger
self-heals to at least the snapshot's state even if it was ever reset.
"""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

SNAPSHOT_PATH = Path(__file__).parent / "ledger_snapshot.json"

_COLUMNS = [
    "problem_id", "language", "mode", "verification_level", "status",
    "adapter_version", "contract_version", "test_suite_version",
    "toolchain_version", "failure_class", "failure_message",
    "duration_ms", "timestamp",
]


async def load_ledger_snapshot(conn: AsyncConnection) -> int:
    """Returns the number of rows actually inserted (0 if the snapshot is
    missing, or if every row already exists)."""
    if not SNAPSHOT_PATH.exists():
        return 0

    data = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    rows = data.get("rows", [])
    if not rows:
        return 0

    placeholders = ", ".join(f":{c}" for c in _COLUMNS)
    stmt = text(
        f"INSERT OR IGNORE INTO atlascode_matrix_ledger ({', '.join(_COLUMNS)}) "
        f"VALUES ({placeholders})"
    )

    before = (await conn.execute(text("SELECT COUNT(*) FROM atlascode_matrix_ledger"))).scalar_one()
    for row in rows:
        await conn.execute(stmt, {c: row.get(c) for c in _COLUMNS})
    after = (await conn.execute(text("SELECT COUNT(*) FROM atlascode_matrix_ledger"))).scalar_one()

    return after - before
