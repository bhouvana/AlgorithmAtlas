"""Phase 9 Level B (compile verification): for every one of the 215 migrated
contracts, generate the STUB starter as the "user code" (its default-value
return, e.g. `return 0;`) and compile it for each compile-once language --
proves every actual TypeSpec shape in the real corpus produces valid,
compiling code for that language's adapter, without requiring a real
algorithmic solution per problem (that's Level C, done separately and only
for a hand-verified sample -- see test_atlascode_function_mode.py's
TestJavaAdapter/TestCppAdapter and the manual spot-checks in this session's
transcript).

This is real evidence, not inference: every row is an actual javac/g++
subprocess compile, not a guess that "the codegen probably works."
"""
from __future__ import annotations

import asyncio
import json
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))
import logging
logging.disable(logging.CRITICAL)

from algorithm_atlas.api.v1.notebook import PREPARERS
from algorithm_atlas.atlascode.function_mode.contracts import FunctionContract
from algorithm_atlas.atlascode.function_mode.registry import ADAPTERS, COMPILED_LANGUAGES

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"


def load_contracts() -> list[tuple[str, FunctionContract]]:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT id, function_contract FROM problems WHERE function_contract IS NOT NULL ORDER BY id")
    out = [(pid, FunctionContract.from_dict(json.loads(fc))) for pid, fc in cur.fetchall()]
    con.close()
    return out


async def sweep_language(language: str, contracts: list[tuple[str, FunctionContract]]) -> dict:
    adapter = ADAPTERS[language]
    preparer = PREPARERS[language]
    sem = asyncio.Semaphore(6)
    results: dict[str, dict] = {}

    async def check_one(pid: str, contract: FunctionContract):
        async with sem:
            try:
                starter = adapter.generate_starter(contract)
                program = adapter.compose_program(starter, contract)
            except Exception as e:
                results[pid] = {"status": "codegen_error", "detail": repr(e)}
                return
            try:
                prepared, compile_failure = await preparer(program, 30.0)
            except Exception as e:
                results[pid] = {"status": "prepare_exception", "detail": repr(e)}
                return
            if prepared is None:
                results[pid] = {
                    "status": "compile_failed",
                    "detail": (compile_failure.compile_output or "")[:500] if compile_failure else "",
                }
            else:
                prepared.cleanup()
                results[pid] = {"status": "compile_ok"}

    await asyncio.gather(*[check_one(pid, c) for pid, c in contracts])
    return results


async def main() -> None:
    contracts = load_contracts()
    print(f"Compile-sanity sweep: {len(contracts)} contracted problems x {sorted(COMPILED_LANGUAGES)}")
    report: dict[str, dict] = {}
    for lang in sorted(COMPILED_LANGUAGES):
        t0 = time.monotonic()
        results = await sweep_language(lang, contracts)
        ok = sum(1 for r in results.values() if r["status"] == "compile_ok")
        print(f"[{lang}] {ok}/{len(results)} compile_ok  ({time.monotonic()-t0:.1f}s)")
        failures = {pid: r for pid, r in results.items() if r["status"] != "compile_ok"}
        for pid, r in list(failures.items())[:15]:
            print(f"    FAIL {pid}: {r['status']} {r['detail'][:200]}")
        report[lang] = results

    (REPO_ROOT / "docs" / "atlascode-compile-sanity-sweep.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\nWritten: docs/atlascode-compile-sanity-sweep.json")


if __name__ == "__main__":
    asyncio.run(main())
