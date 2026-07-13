"""Loads the committed problems+test_cases snapshot (problems_snapshot.json.gz,
alongside this file) into the live database via bulk INSERT.

Why this exists: regenerating all 216 problems via assemble_catalog() /
seed() is real, CPU/memory-heavy work (see scripts/export_problems_snapshot.py's
docstring) -- confirmed to OOM-kill Render's free-tier 512MB container on
every boot, in an infinite crash-loop (no persistent disk -> every restart
starts from an empty DB and retries the same OOM). Loading pre-built rows
is a plain bulk INSERT -- no test generation, no brute-force adversarial
search, no dedup-checking -- so it's dramatically cheaper and finishes in
seconds instead of OOM-crashing partway through an 8-minute generation run.

This is preferred over seed_atlascode() whenever the snapshot file exists;
seed_atlascode() remains the fallback (see main.py's
_auto_seed_atlascode_if_empty) for environments where the snapshot is
absent or stale relative to the family builders (e.g. fresh problems added
locally but not yet re-exported).
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

SNAPSHOT_PATH = Path(__file__).parent / "problems_snapshot.json.gz"


async def load_problems_snapshot(conn: AsyncConnection) -> int:
    """Returns the number of problems actually inserted (0 if the snapshot
    is missing, or every problem already exists)."""
    if not SNAPSHOT_PATH.exists():
        return 0

    data = json.loads(gzip.decompress(SNAPSHOT_PATH.read_bytes()))
    p_cols = data["problems_columns"]
    p_rows = data["problems_rows"]
    tc_cols = data["test_cases_columns"]
    tc_rows = data["test_cases_rows"]
    if not p_rows:
        return 0

    # Column names are double-quoted: `order` is an actual column on
    # test_cases but is also a reserved SQL keyword -- unquoted, SQLite
    # raises `OperationalError: near "order": syntax error` on every insert.
    p_placeholders = ", ".join(f":{c}" for c in p_cols)
    p_stmt = text(
        f"INSERT OR IGNORE INTO problems ({', '.join(f'\"{c}\"' for c in p_cols)}) "
        f"VALUES ({p_placeholders})"
    )
    tc_placeholders = ", ".join(f":{c}" for c in tc_cols)
    tc_stmt = text(
        f"INSERT OR IGNORE INTO test_cases ({', '.join(f'\"{c}\"' for c in tc_cols)}) "
        f"VALUES ({tc_placeholders})"
    )

    before = (await conn.execute(text("SELECT COUNT(*) FROM problems"))).scalar_one()

    # Passing the full parameter list to a single execute() uses SQLAlchemy's
    # executemany path -- one driver round-trip setup instead of ~8800
    # individual awaits, which matters on a memory/time-constrained boot.
    if p_rows:
        await conn.execute(p_stmt, [dict(zip(p_cols, row)) for row in p_rows])
    if tc_rows:
        await conn.execute(tc_stmt, [dict(zip(tc_cols, row)) for row in tc_rows])

    after = (await conn.execute(text("SELECT COUNT(*) FROM problems"))).scalar_one()
    return after - before
