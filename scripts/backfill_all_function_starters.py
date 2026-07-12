"""Bulk version of backfill_js_starter_code.py / backfill_ts_starter_code.py:
adds a starter_code_function entry for EVERY language in registry.ADAPTERS
(currently python/javascript/typescript), for every problem with a
function_contract, not just the original 6. Idempotent -- skips a
(problem, language) pair that already has a starter.

Run from repo root: python scripts/backfill_all_function_starters.py [--dry-run]
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))

from algorithm_atlas.atlascode.function_mode.contracts import FunctionContract
from algorithm_atlas.atlascode.function_mode.registry import ADAPTERS
from algorithm_atlas.database import AsyncSessionLocal, init_db
from algorithm_atlas.models.atlas_code import Problem
from sqlalchemy import select


async def backfill(dry_run: bool = False) -> None:
    await init_db()

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Problem).where(Problem.function_contract.isnot(None)))
        problems = list(result.scalars().all())

        updated = 0
        skipped = 0
        failed: list[tuple[str, str, str]] = []
        for p in problems:
            try:
                contract = FunctionContract.from_dict(p.function_contract)
            except Exception as e:
                failed.append((p.id, "*", str(e)))
                continue
            existing = dict(p.starter_code_function or {})
            changed = False
            for lang, adapter in ADAPTERS.items():
                if lang in existing:
                    skipped += 1
                    continue
                try:
                    existing[lang] = adapter.generate_starter(contract)
                    changed = True
                    updated += 1
                except Exception as e:
                    failed.append((p.id, lang, str(e)))
            if changed and not dry_run:
                p.starter_code_function = existing

        if not dry_run:
            await db.commit()
        print(f"{'Would add' if dry_run else 'Added'}: {updated} starter(s) across {len(problems)} problems")
        print(f"Skipped (already present): {skipped}")
        if failed:
            print(f"Failed: {len(failed)}")
            for pid, lang, err in failed[:20]:
                print(f"  {pid} [{lang}]: {err}")

    from algorithm_atlas.database import engine as _engine
    await _engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    asyncio.run(backfill(dry_run=args.dry_run))
