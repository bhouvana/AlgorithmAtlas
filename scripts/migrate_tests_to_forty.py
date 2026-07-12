"""
Refresh test_cases for ALREADY-SEEDED AtlasCode problems to the new
exactly-40-test standard (see docs/atlascode-40-test-standard.md).

seed_atlas_code.py deliberately skips any problem whose id already exists in
the DB (so re-running it never touches already-shipped content). That's the
right default for normal seeding, but it means a family factory upgraded to
emit 40 tests (via testgen.py) has no path to update rows that were already
inserted with the old 3-6-test data. This script is that path: it re-derives
the (now 40-test) problem definitions from assemble_catalog(), and for any
problem whose id is already in the DB, deletes its old TestCase rows and
inserts the fresh 40 — the Problem row itself (statement/starter code/etc.)
is left untouched.

Usage:
    python scripts/migrate_tests_to_forty.py greedy tree-variants
    python scripts/migrate_tests_to_forty.py --all-generated
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))
sys.path.insert(0, str(Path(__file__).parent))

import logging
logging.disable(logging.CRITICAL)

from sqlalchemy import delete, select

from algorithm_atlas.database import AsyncSessionLocal, init_db
from algorithm_atlas.models.atlas_code import Problem, TestCase
from algorithm_atlas.atlascode import testgen as tg

import seed_atlas_code as seed_mod

# family name -> set of problem ids it owns, as seen in assemble_catalog()'s
# generated_slugs family tag. Extend this as more families migrate to 40.
FAMILY_REGISTRY = {
    "greedy": None,  # resolved dynamically below via generated_slugs family tag
}


async def migrate(problem_ids: set[str], dry_run: bool = False) -> None:
    all_problems, _, generated_slugs, _, _ = seed_mod.assemble_catalog()
    by_id = {p[0]["id"]: (p[0], p[1]) for p in all_problems}

    missing = problem_ids - set(by_id)
    if missing:
        print(f"WARNING: not produced by any factory (skipped): {sorted(missing)}")

    manifest = tg.load_manifest()
    await init_db()
    async with AsyncSessionLocal() as db:
        updated = 0
        for pid in sorted(problem_ids & set(by_id)):
            prob_data, test_cases = by_id[pid]
            if len(test_cases) != tg.TOTAL_TESTS:
                print(f"  SKIP {pid}: factory produced {len(test_cases)} tests, not {tg.TOTAL_TESTS} — not migrated yet")
                continue

            existing = await db.execute(select(Problem).where(Problem.id == pid))
            if existing.scalar_one_or_none() is None:
                print(f"  SKIP {pid}: not present in DB (would be a normal seed, not a migration)")
                continue

            if dry_run:
                print(f"  [dry-run] would replace test_cases for {pid} ({len(test_cases)} tests)")
                continue

            await db.execute(delete(TestCase).where(TestCase.problem_id == pid))
            for tc in test_cases:
                db.add(TestCase(problem_id=pid, **tc))
            manifest[pid] = tg.manifest_entries_for(pid, test_cases)
            updated += 1
            print(f"  migrated {pid}: {len(test_cases)} tests "
                  f"({sum(1 for t in test_cases if not t['is_hidden'])} visible)")

        if not dry_run:
            await db.commit()
            tg.write_manifest(manifest)

    print(f"\n{'[dry-run] would migrate' if dry_run else 'Migrated'} {updated} problem(s) to exactly-40 tests.")


def _family_problem_ids(family_module_names: list[str]) -> set[str]:
    """Resolve problem ids for a family by looking up its *_testdata module's
    plan-registry dict (the pattern established by greedy_testdata.py:
    GREEDY_TEST_PLANS). Falls back to: any generated problem whose family tag
    (from assemble_catalog's generated_slugs) matches."""
    _, _, generated_slugs, _, _ = seed_mod.assemble_catalog()
    family_tags = {name.replace("_", "-") for name in family_module_names}
    ids = {pid for (_family, pid) in generated_slugs.values() if _family in family_tags}
    return ids


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("families", nargs="*", help="family tag(s), e.g. greedy tree-variants")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.families:
        print("Usage: python scripts/migrate_tests_to_forty.py <family> [<family> ...] [--dry-run]")
        sys.exit(2)

    ids = _family_problem_ids(args.families)
    print(f"Resolved {len(ids)} problem id(s) for families {args.families}: {sorted(ids)}")
    asyncio.run(migrate(ids, dry_run=args.dry_run))
