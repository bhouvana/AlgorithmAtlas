"""Export `problems` + `test_cases` to a compressed, committable SQLite
snapshot -- apps/backend/algorithm_atlas/atlascode/problems_snapshot.db.gz.

Why this exists: regenerating all 216 problems' test data via
assemble_catalog() (see seed.py) is real, CPU/memory-heavy work -- dozens
of family builders doing brute-force adversarial test generation,
dedup-checking, and independent-oracle verification. That's appropriate
for a dev machine building NEW problems, but it's fatal on a
memory-constrained deploy target: confirmed on Render's free tier (512MB),
the boot-time auto-seed OOM-killed the container every single time before
finishing, in an infinite crash-loop (no persistent disk means every
restart starts from an empty DB and tries again, forever).

This is a SQLite database file (not JSON): the loader (problems_snapshot.py)
copies rows via SQLite's own ATTACH DATABASE + INSERT...SELECT, which never
materializes the row data as Python objects. An earlier JSON version of this
snapshot decompressed+json.loads()'d ~220MB of text into hundreds of
thousands of Python dict/list/str objects in one shot -- confirmed to STILL
OOM-kill Render's 512MB container even though the actual insert was fast.
Uncompressed this sqlite file is comparable in size to the raw data
(~220MB, 8612 test cases, some with large "stress"-bucket inputs); gzip -9
brings it to ~75MB, under GitHub's 100MB hard limit. Still large -- re-run
this and re-commit only when problem/test-case data actually changes (new
problems, corpus fixes), not for unrelated commits.

Usage: python scripts/export_problems_snapshot.py
"""
from __future__ import annotations

import gzip
import shutil
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"
TMP_SNAPSHOT_DB = REPO_ROOT / "_problems_snapshot_export_tmp.db"
OUT_PATH = REPO_ROOT / "apps" / "backend" / "algorithm_atlas" / "atlascode" / "problems_snapshot.db.gz"


def main() -> None:
    TMP_SNAPSHOT_DB.unlink(missing_ok=True)

    con = sqlite3.connect(TMP_SNAPSHOT_DB)
    try:
        con.execute("ATTACH DATABASE ? AS src", (str(DB_PATH),))
        con.execute("CREATE TABLE problems AS SELECT * FROM src.problems")
        con.execute("CREATE TABLE test_cases AS SELECT * FROM src.test_cases")
        p_count = con.execute("SELECT COUNT(*) FROM problems").fetchone()[0]
        tc_count = con.execute("SELECT COUNT(*) FROM test_cases").fetchone()[0]
        con.execute("DETACH DATABASE src")
        con.commit()
    finally:
        con.close()

    if p_count == 0:
        TMP_SNAPSHOT_DB.unlink()
        raise SystemExit("atlas.db has zero problems -- refusing to export an empty snapshot")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TMP_SNAPSHOT_DB, "rb") as f_in, gzip.open(OUT_PATH, "wb", compresslevel=9) as f_out:
        shutil.copyfileobj(f_in, f_out, length=1024 * 1024)

    raw_size = TMP_SNAPSHOT_DB.stat().st_size
    compressed_size = OUT_PATH.stat().st_size
    TMP_SNAPSHOT_DB.unlink()

    print(
        f"Exported {p_count} problems / {tc_count} test cases to {OUT_PATH}\n"
        f"  raw sqlite: {raw_size:,} bytes ({raw_size / 1024 / 1024:.1f} MB)\n"
        f"  gzip: {compressed_size:,} bytes ({compressed_size / 1024 / 1024:.1f} MB)"
    )


if __name__ == "__main__":
    main()
