"""
Backfill Function Mode metadata (function_contract, starter_code_function,
per-TestCase function_args/function_expected) onto Problem rows that were
already seeded by seed_atlas_code.py BEFORE Function Mode existed.

seed_atlas_code.py's seed() skips any problem id that already exists in the
DB -- correct for Program Mode data (never touch a live problem's test
corpus), but that also means simply re-running it will never attach the new
Function Mode columns to already-seeded rows. This script is the one-time,
explicit, verified bridge for that gap:

  1. Regenerate each family's problem list in-memory (same deterministic
     tg.problem_rng(slug) + case-plan pipeline seed_atlas_code.py already
     uses -- NOT a new/second test corpus).
  2. For every problem with a function_contract in the regenerated data,
     load its EXISTING DB rows and verify, case by case (matched by `order`),
     that input_data/expected_output are byte-identical to what's freshly
     regenerated. Any mismatch aborts that problem with a loud error and
     writes nothing for it -- this guards against the plan generator (RNG
     draws, bucket ordering) having drifted since the original seed, which
     would otherwise silently attach a WRONG typed argument to an existing
     hidden test case.
  3. Only after verification: UPDATE (never delete/recreate) the existing
     Problem/TestCase rows with the new columns.

Run from the repo root:
    python scripts/backfill_function_mode.py [--dry-run]
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))

from algorithm_atlas.atlascode.families.array_hashing_variants import build_array_hashing_variant_problems
from algorithm_atlas.database import AsyncSessionLocal, init_db
from algorithm_atlas.models.atlas_code import Problem, TestCase
from sqlalchemy import select

# One entry per family factory that may contain Function Mode contracts.
# Each factory is called with (registered_algorithms=[], existing_problem_ids=set())
# so it regenerates EVERY one of its problems fresh, regardless of what's
# already in the DB -- this script decides what to skip, not the factory.
_FAMILY_BUILDERS = [
    ("array-hashing-variants", build_array_hashing_variant_problems),
]


async def backfill(dry_run: bool = False) -> None:
    await init_db()

    async with AsyncSessionLocal() as db:
        updated = 0
        skipped_no_contract = 0
        skipped_already_set = 0
        skipped_not_found = 0

        for family_name, builder in _FAMILY_BUILDERS:
            problems, _skipped = builder([], set())
            for prob_data, tc_list in problems:
                contract = prob_data.get("function_contract")
                if not contract:
                    skipped_no_contract += 1
                    continue

                result = await db.execute(select(Problem).where(Problem.id == prob_data["id"]))
                problem = result.scalar_one_or_none()
                if problem is None:
                    print(f"  SKIP  {prob_data['id']}: not found in DB (never seeded)")
                    skipped_not_found += 1
                    continue

                if problem.function_contract:
                    print(f"  skip  {prob_data['id']}: function_contract already set")
                    skipped_already_set += 1
                    continue

                tc_result = await db.execute(
                    select(TestCase).where(TestCase.problem_id == problem.id).order_by(TestCase.order)
                )
                existing_tcs = list(tc_result.scalars().all())

                if len(existing_tcs) != len(tc_list):
                    print(
                        f"  ABORT {prob_data['id']}: DB has {len(existing_tcs)} test case(s), "
                        f"regenerated plan has {len(tc_list)} -- refusing to backfill (case count drift)"
                    )
                    continue

                mismatch = None
                for existing, fresh in zip(existing_tcs, tc_list):
                    if existing.order != fresh["order"]:
                        mismatch = f"order mismatch at index (db={existing.order}, fresh={fresh['order']})"
                        break
                    if existing.input_data != fresh["input_data"]:
                        mismatch = f"input_data mismatch at order={existing.order}"
                        break
                    if existing.expected_output != fresh["expected_output"]:
                        mismatch = f"expected_output mismatch at order={existing.order}"
                        break
                if mismatch:
                    print(f"  ABORT {prob_data['id']}: {mismatch} -- refusing to backfill this problem")
                    continue

                if dry_run:
                    print(f"  [dry-run] would backfill {prob_data['id']} ({family_name}) -- "
                          f"{len(tc_list)} verified cases")
                    updated += 1
                    continue

                problem.function_contract = contract
                problem.starter_code_function = prob_data.get("starter_code_function") or {}
                for existing, fresh in zip(existing_tcs, tc_list):
                    existing.function_args = fresh.get("function_args")
                    existing.function_expected = fresh.get("function_expected")

                updated += 1
                print(f"  backfilled {prob_data['id']} ({family_name}) -- {len(tc_list)} cases verified + updated")

        if not dry_run:
            await db.commit()

        print("\n" + "=" * 50)
        print("FUNCTION MODE BACKFILL SUMMARY")
        print("=" * 50)
        print(f"{'Would update' if dry_run else 'Updated'}: {updated}")
        print(f"Skipped (no function_contract in this batch): {skipped_no_contract}")
        print(f"Skipped (already backfilled): {skipped_already_set}")
        print(f"Skipped (not found in DB): {skipped_not_found}")
        print("=" * 50)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Backfill Function Mode metadata onto already-seeded problems.")
    parser.add_argument("--dry-run", action="store_true", help="Verify + report, but write nothing to the DB.")
    args = parser.parse_args()

    asyncio.run(backfill(dry_run=args.dry_run))
