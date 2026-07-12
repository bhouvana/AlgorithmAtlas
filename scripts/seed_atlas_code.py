"""
Seed AtlasCode problems + test cases into the SQLite database.

Run from the repo root:
    python scripts/seed_atlas_code.py

Idempotent: skips problems that already exist.

The actual PROBLEMS data + assemble_catalog()/seed() implementation now
lives in apps/backend/algorithm_atlas/atlascode/seed.py (moved 2026-07-12)
so the running backend can import and call it directly at boot time (see
main.py's lifespan) without depending on this scripts/ directory, which
isn't copied into the Docker image. This file is now a thin CLI wrapper
that re-exports the same names so nothing else has to change: the command
above still works exactly as before, and the other scripts that
`import seed_atlas_code as seed_mod` (check_atlascode_duplicates.py,
migrate_*_to_forty.py, time_bsv.py, time_families.py) still see the same
PROBLEMS / assemble_catalog / seed attributes on this module.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Allow importing from apps/backend when run as a loose script from a full
# repo checkout (the deployed backend imports algorithm_atlas.atlascode.seed
# directly and never needs this).
sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))

from algorithm_atlas.atlascode.seed import PROBLEMS, assemble_catalog, seed  # noqa: F401 -- re-exported for seed_mod.PROBLEMS / seed_mod.assemble_catalog callers
from algorithm_atlas.atlascode.seed import _print_summary  # noqa: F401 -- seed() calls this internally; moved alongside it (see seed.py) so it's resolvable in-module there, re-exported here only in case anything scripts-side still expects it on this module

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed AtlasCode problems (curated + generated).")
    parser.add_argument("--dry-run", action="store_true", help="Discover/generate/validate but don't write to the DB.")
    parser.add_argument("--validate-only", action="store_true", help="Only run discovery + validation; no DB access at all.")
    args = parser.parse_args()

    asyncio.run(seed(dry_run=args.dry_run, validate_only=args.validate_only))
