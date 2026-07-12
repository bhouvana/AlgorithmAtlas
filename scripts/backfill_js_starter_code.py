"""
Add a 'javascript' key to starter_code_function for the problems that
already have a function_contract (currently the 6 array-hashing-variants
problems). This is intentionally a much smaller operation than
backfill_function_mode.py: it never touches function_contract or any
TestCase row, it only adds one language's starter template to an existing
JSON column -- there is no test-corpus risk to verify against.

Run from repo root: python scripts/backfill_js_starter_code.py [--dry-run]
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))

from algorithm_atlas.atlascode.function_mode.adapters import JavaScriptFunctionAdapter
from algorithm_atlas.atlascode.function_mode.contracts import FunctionContract
from algorithm_atlas.database import AsyncSessionLocal, init_db
from algorithm_atlas.models.atlas_code import Problem
from sqlalchemy import select


async def backfill(dry_run: bool = False) -> None:
    await init_db()
    adapter = JavaScriptFunctionAdapter()

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Problem).where(Problem.function_contract.isnot(None)))
        problems = list(result.scalars().all())

        updated = 0
        for p in problems:
            if "javascript" in (p.starter_code_function or {}):
                print(f"  skip  {p.id}: javascript starter already present")
                continue
            contract = FunctionContract.from_dict(p.function_contract)
            starter = adapter.generate_starter(contract)
            if dry_run:
                print(f"  [dry-run] would add javascript starter to {p.id}:\n{starter}")
            else:
                p.starter_code_function = {**(p.starter_code_function or {}), "javascript": starter}
            updated += 1

        if not dry_run:
            await db.commit()
        print(f"\n{'Would update' if dry_run else 'Updated'}: {updated} / {len(problems)} function-contract problems")

    # Without this, aiosqlite's background connection thread keeps the process
    # alive after asyncio.run() returns -- found as a real latent bug while
    # authoring the TypeScript adapter's equivalent script (this one has the
    # identical pattern, so the same hang applies here too).
    from algorithm_atlas.database import engine as _engine
    await _engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    asyncio.run(backfill(dry_run=args.dry_run))
