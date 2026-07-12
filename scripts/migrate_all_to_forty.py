"""Batch migration: replace all eligible problems' old test data with 40-test data."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))
sys.path.insert(0, str(Path(__file__).parent))

# Suppress Loguru BEFORE any other imports
import loguru
loguru.logger.remove()  # removes all sinks
loguru.logger.disable("algorithm_atlas")

# Also suppress standard logging
import logging
logging.disable(logging.CRITICAL + 10)

import seed_atlas_code as seed_mod
from algorithm_atlas.database import AsyncSessionLocal, init_db
from algorithm_atlas.models.atlas_code import Problem, TestCase
from algorithm_atlas.atlascode import testgen as tg
from sqlalchemy import delete, select


TOTAL = tg.TOTAL_TESTS

async def main(dry_run: bool = False) -> None:
    print("Assembling catalog...")
    all_problems, _, generated_slugs, _, _ = seed_mod.assemble_catalog()
    by_id = {p[0]["id"]: (p[0], p[1]) for p in all_problems}

    # Build family -> ids mapping
    families: dict[str, set[str]] = {}
    for alg_slug, (fam, pid) in generated_slugs.items():
        families.setdefault(fam, set()).add(pid)

    # Pattern-only problems
    curated = {p[0]["id"] for p in seed_mod.PROBLEMS}
    gen_slugs = {pid for ids in families.values() for pid in ids}
    pattern = set(by_id) - curated - gen_slugs
    if pattern:
        families["__pattern"] = pattern

    print(f"Catalog: {len(by_id)} problems ({len(curated)} curated, "
          f"{len(gen_slugs)} canonical-generated, {len(pattern)} pattern-only)")

    for fam in sorted(families):
        print(f"  {fam}: {len(families[fam])}")

    manifest = tg.load_manifest()
    await init_db()
    async with AsyncSessionLocal() as db:
        updated = 0
        already_40 = 0
        not_in_db = 0
        not_40_factory = 0

        for pid in sorted(by_id):
            prob_data, test_cases = by_id[pid]
            if len(test_cases) != TOTAL:
                not_40_factory += 1
                continue

            existing = await db.execute(select(Problem).where(Problem.id == pid))
            if existing.scalar_one_or_none() is None:
                not_in_db += 1
                continue

            existing_rows = (await db.execute(
                select(TestCase).where(TestCase.problem_id == pid)
            )).scalars().all()
            existing_count = len(existing_rows)

            if existing_count == TOTAL:
                already_40 += 1
                continue

            if dry_run:
                print(f"  [dry-run] {pid}: {existing_count} -> {TOTAL}")
                continue

            await db.execute(delete(TestCase).where(TestCase.problem_id == pid))
            for tc in test_cases:
                db.add(TestCase(problem_id=pid, **tc))
            manifest[pid] = tg.manifest_entries_for(pid, test_cases)
            updated += 1
            visible = sum(1 for t in test_cases if not t["is_hidden"])
            print(f"  migrated {pid}: {existing_count} -> {TOTAL} ({visible} visible)")

        if not dry_run and updated:
            await db.commit()
            tg.write_manifest(manifest)

    print(f"\n{'[DRY-RUN] ' if dry_run else ''}"
          f"Migrated: {updated}, Already 40: {already_40}, "
          f"Not in DB: {not_in_db}, Factory != 40: {not_40_factory}")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    asyncio.run(main(dry_run=dry_run))
    print("Done.")
