"""Master orchestrator for the AtlasCode dual-mode completion pass (Phase 22).

Ties together the individual scripts this session built, in the dependency
order Phase 27 specifies. Each phase is independently re-runnable (the
underlying scripts are idempotent: contract migration skips problems that
already have a function_contract, starter backfill skips languages already
present, the compile sweep just re-checks). This orchestrator adds a
resumable skip layer on top via a hash-free checkpoint file recording which
phases completed in the last run, so a re-invocation with --resume doesn't
redo expensive work (the toolchain probe, the 40-case migration, the
node-per-node compile sweep) that already succeeded.

Usage:
    python scripts/complete_dual_mode_matrix.py [--resume] [--skip-sweep]

This does NOT re-implement the underlying logic -- it shells out to the
real scripts (migrate_atlascode_function_mode.py, backfill_all_function_starters.py,
etc.) so there is exactly one source of truth per phase, not two.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
CHECKPOINT_PATH = REPO_ROOT / "docs" / "atlascode-orchestrator-checkpoint.json"

PHASES: list[tuple[str, list[str]]] = [
    ("resolve_db_and_toolchains", [sys.executable, "scripts/discover_toolchains.py"]),
    ("migrate_contracts_and_cases", [sys.executable, "scripts/migrate_atlascode_function_mode.py"]),
    ("backfill_starters", [sys.executable, "scripts/backfill_all_function_starters.py"]),
    ("regenerate_tree_mutation_starters", [sys.executable, "scripts/regenerate_tree_mutation_starters.py"]),
    ("compile_sanity_sweep", [sys.executable, "scripts/compile_sanity_sweep.py"]),
    ("bulk_python_runtime_verification", [sys.executable, "scripts/verify_python_function_mode_bulk.py"]),
]


def load_checkpoint() -> dict:
    if CHECKPOINT_PATH.exists():
        return json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
    return {"completed_phases": {}}


def save_checkpoint(cp: dict) -> None:
    CHECKPOINT_PATH.write_text(json.dumps(cp, indent=2), encoding="utf-8")


def run_phase(name: str, cmd: list[str]) -> tuple[bool, str]:
    print(f"\n{'='*70}\nPHASE: {name}\n{'='*70}")
    t0 = time.monotonic()
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=1800)
    elapsed = time.monotonic() - t0
    print(proc.stdout[-4000:])
    if proc.returncode != 0:
        print(f"[{name}] FAILED (exit {proc.returncode}) after {elapsed:.1f}s")
        print(proc.stderr[-2000:])
        return False, proc.stderr[-2000:]
    print(f"[{name}] OK ({elapsed:.1f}s)")
    return True, ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true", help="skip phases already marked completed")
    parser.add_argument("--skip-sweep", action="store_true", help="skip the compile-sanity sweep (slow)")
    parser.add_argument("--only", help="comma-separated phase names to run, ignoring the rest")
    args = parser.parse_args()

    cp = load_checkpoint() if args.resume else {"completed_phases": {}}
    only = set(args.only.split(",")) if args.only else None

    for name, cmd in PHASES:
        if only and name not in only:
            continue
        if args.skip_sweep and name == "compile_sanity_sweep":
            continue
        if args.resume and cp["completed_phases"].get(name, {}).get("ok"):
            print(f"[{name}] SKIP (already completed this session, --resume)")
            continue
        ok, err = run_phase(name, cmd)
        cp["completed_phases"][name] = {"ok": ok, "error": err, "ts": time.time()}
        save_checkpoint(cp)
        if not ok:
            print(f"\nStopping: phase '{name}' failed. Fix and re-run with --resume to continue from here.")
            sys.exit(1)

    print("\nAll requested phases completed. Run scripts/generate_final_matrix_report.py for the honest final tally.")


if __name__ == "__main__":
    main()
