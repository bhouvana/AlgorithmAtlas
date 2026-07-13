"""Loads the committed problems+test_cases snapshot (problems_snapshot.db.gz,
alongside this file) into the live database via SQLite's own ATTACH DATABASE
bulk copy.

Why SQLite-to-SQLite instead of JSON: an earlier version of this snapshot
shipped as gzip-compressed JSON, decompressed and json.loads()'d in one shot.
That materializes ~220MB of raw JSON text into hundreds of thousands of
Python dict/list/str objects all at once -- confirmed via Render's dashboard
to STILL OOM-kill the free-tier 512MB container even though the actual DB
insert only took ~3 seconds locally once run; the memory spike was in Python
object construction during json.loads(), not the insert itself. Copying
table-to-table with SQLite's own ATTACH DATABASE + INSERT...SELECT does the
row copy entirely inside the C library's page cache -- no Python object
materialization of row data at all, and the gzip decompression is streamed
in fixed-size chunks rather than one giant in-memory blob.

Runs on a worker thread via run_in_executor: sqlite3 (the stdlib sync
driver) is used directly against the live db file rather than going through
the app's async SQLAlchemy/aiosqlite engine, both to avoid SQLite's
restriction on ATTACH inside an already-open transaction (SQLAlchemy's
engine.begin() always starts one) and to keep this CPU/IO-bound work off
the event loop -- same reasoning as assemble_catalog() in seed.py.
"""
from __future__ import annotations

import asyncio
import gzip
import os
import shutil
import sqlite3
from pathlib import Path

SNAPSHOT_PATH = Path(__file__).parent / "problems_snapshot.db.gz"


def _load_sync(db_path: Path) -> int:
    """Runs on a worker thread. Returns the number of problems inserted
    (0 if the snapshot is missing, or every problem already exists)."""
    if not SNAPSHOT_PATH.exists():
        return 0

    tmp_db_path = db_path.parent / f".problems_snapshot_tmp_{os.getpid()}.db"
    tmp_db_path.unlink(missing_ok=True)
    try:
        # Streamed in fixed-size chunks -- bounded memory regardless of the
        # decompressed size (~230MB), unlike a single gzip.decompress() call.
        with gzip.open(SNAPSHOT_PATH, "rb") as f_in, open(tmp_db_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out, length=1024 * 1024)

        con = sqlite3.connect(str(db_path), timeout=30)
        try:
            before = con.execute("SELECT COUNT(*) FROM problems").fetchone()[0]
            con.execute("ATTACH DATABASE ? AS snap", (str(tmp_db_path),))
            try:
                # Explicit, name-matched column lists (not `SELECT *`, which
                # matches by position) -- robust if the live schema has since
                # gained columns the snapshot predates (they're just left
                # NULL/default); a genuinely removed column is a real error,
                # same as it would be for any stale snapshot.
                p_cols = [r[1] for r in con.execute("PRAGMA snap.table_info(problems)").fetchall()]
                tc_cols = [r[1] for r in con.execute("PRAGMA snap.table_info(test_cases)").fetchall()]
                p_col_list = ", ".join(f'"{c}"' for c in p_cols)
                tc_col_list = ", ".join(f'"{c}"' for c in tc_cols)
                con.execute(
                    f'INSERT OR IGNORE INTO problems ({p_col_list}) '
                    f'SELECT {p_col_list} FROM snap.problems'
                )
                con.execute(
                    f'INSERT OR IGNORE INTO test_cases ({tc_col_list}) '
                    f'SELECT {tc_col_list} FROM snap.test_cases'
                )
                con.commit()
            finally:
                con.execute("DETACH DATABASE snap")
            after = con.execute("SELECT COUNT(*) FROM problems").fetchone()[0]
        finally:
            con.close()
        return after - before
    finally:
        tmp_db_path.unlink(missing_ok=True)


async def load_problems_snapshot(db_path: Path) -> int:
    """Returns the number of problems actually inserted (0 if the snapshot
    is missing, or every problem already exists)."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _load_sync, db_path)
