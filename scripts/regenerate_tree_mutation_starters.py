"""One-off: regenerate starter_code_function ONLY for problems whose contract
uses a tree type or mutates_argument, since adapters.py's generate_starter
changed (tree class prefix / TS interface) AFTER the first bulk backfill ran.
Never touches the original 6 array-hashing-variants problems (they use
neither feature, so their starters are already correct and untouched here
regardless).
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))

from algorithm_atlas.atlascode.function_mode.contracts import FunctionContract
from algorithm_atlas.atlascode.function_mode.registry import ADAPTERS
from algorithm_atlas.database import AsyncSessionLocal, init_db
from algorithm_atlas.models.atlas_code import Problem
from sqlalchemy import select


async def main() -> None:
    await init_db()
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Problem).where(Problem.function_contract.isnot(None)))
        problems = list(result.scalars().all())

        updated = 0
        for p in problems:
            contract = FunctionContract.from_dict(p.function_contract)
            uses_tree = any(t.kind == "tree" for t in [pr.type for pr in contract.parameters] + [contract.return_type])
            if not (uses_tree or contract.mutates_argument is not None):
                continue
            starters = {lang: adapter.generate_starter(contract) for lang, adapter in ADAPTERS.items()}
            p.starter_code_function = starters
            updated += 1

        await db.commit()
        print(f"Regenerated starters for {updated} tree/mutation problems")

    from algorithm_atlas.database import engine as _engine
    await _engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
