"""Phase 15: toolchain discovery. Probes the exact binaries notebook.py's 17
RUNNERS actually invoke (read directly out of that file, not guessed) and
records what's really available in this environment -- resolved path,
version, and a cold/warm subprocess-launch timing sample. This is the
grounding evidence for every RUNTIME_UNAVAILABLE cell in the final matrix
report: a cell is only ever marked unavailable because this script actually
tried and failed, never because a language "seemed hard."

Writes docs/atlascode-toolchain-report.json. Safe to re-run; each run is a
fresh probe (compiler installs can change between sessions).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# name -> list of ALTERNATIVE requirement sets (each an AND-list of binaries
# that must ALL resolve for that alternative to count as satisfied; the
# language is available if ANY one alternative set is fully satisfied).
# Sourced by reading every run_* function in
# apps/backend/algorithm_atlas/api/v1/notebook.py directly -- e.g. kotlin
# genuinely needs BOTH kotlinc (compile) and java (run the produced jar); a
# resolved `java` alone is not sufficient, even though a naive first-match
# probe would say otherwise.
_VERSION_ARGS: dict[str, list[str]] = {
    "python": ["--version"], "node": ["--version"], "tsx": ["--version"], "npx": ["--version"],
    "g++": ["--version"], "c++": ["--version"], "gcc": ["--version"],
    "javac": ["--version"], "java": ["--version"], "go": ["version"], "rustc": ["--version"],
    "cmd": ["/c", "ver"], "bash": ["--version"], "sh": ["--version"], "ruby": ["--version"],
    "kotlinc": ["-version"], "swift": ["--version"], "Rscript": ["--version"], "rscript": ["--version"],
    "mcs": ["--version"], "csc": ["--version"], "mono": ["--version"], "dotnet": ["--version"],
    "php": ["--version"], "scala-cli": ["--version"], "scala": ["-version"], "perl": ["--version"],
}

LANGUAGE_REQUIREMENT_SETS: dict[str, list[list[str]]] = {
    "python":     [["python"]],
    "javascript": [["node"]],
    "typescript": [["tsx"], ["npx", "node"]],
    "cpp":        [["g++"], ["c++"]],
    "c":          [["gcc"]],
    "java":       [["javac", "java"]],
    "go":         [["go"]],
    "rust":       [["rustc"]],
    "shell":      [["cmd"]] if sys.platform == "win32" else [["bash"], ["sh"]],
    "ruby":       [["ruby"]],
    "kotlin":     [["kotlinc", "java"]],
    "swift":      [["swift"]],
    "r":          [["Rscript"], ["rscript"]],
    "csharp":     [["mcs", "mono"], ["dotnet"]],
    "php":        [["php"]],
    "scala":      [["scala-cli"], ["scala"]],
    "perl":       [["perl"]],
}


def _probe_binary(name: str, version_args: list[str]) -> dict:
    resolved = shutil.which(name)
    entry = {"binary": name, "resolved_path": resolved, "available": False, "version": None,
             "cold_start_ms": None}
    if not resolved and name != "cmd":
        return entry
    t0 = time.monotonic()
    try:
        # Invoke the RESOLVED path, not the bare name -- on Windows a `.cmd`/
        # `.bat` shim (e.g. npm's tsx.CMD) resolves fine via shutil.which but
        # fails to launch via CreateProcess when passed as a bare name
        # without an extension (WinError 193 / not a valid Win32
        # application). This bug silently made a genuinely-installed tsx
        # report as unavailable on first pass -- caught by testing the probe
        # directly against a known-installed binary rather than trusting it.
        proc = subprocess.run(
            [resolved or name, *version_args], capture_output=True, text=True, timeout=10,
        )
        elapsed_ms = (time.monotonic() - t0) * 1000
        entry["available"] = True
        entry["cold_start_ms"] = round(elapsed_ms, 1)
        out = (proc.stdout or "") + (proc.stderr or "")
        entry["version"] = out.strip().splitlines()[0] if out.strip() else ""
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return entry


def discover() -> dict:
    report: dict[str, dict] = {}
    probe_cache: dict[str, dict] = {}

    def probe(name: str) -> dict:
        if name not in probe_cache:
            probe_cache[name] = _probe_binary(name, _VERSION_ARGS.get(name, ["--version"]))
        return probe_cache[name]

    for lang, req_sets in LANGUAGE_REQUIREMENT_SETS.items():
        all_probed = {b: probe(b) for req_set in req_sets for b in req_set}
        satisfied_set = next(
            (req_set for req_set in req_sets if all(all_probed[b]["available"] for b in req_set)),
            None,
        )
        available = satisfied_set is not None
        report[lang] = {
            "language": lang,
            "requirement_sets_tried": req_sets,
            "binaries_probed": all_probed,
            "available": available,
            "satisfied_requirement_set": satisfied_set,
            "cold_start_ms": max((all_probed[b]["cold_start_ms"] or 0) for b in satisfied_set) if satisfied_set else None,
            "fallback_risk": (
                "typescript falls back to `npx tsx` (~10x slower per call) when global "
                "tsx is not resolvable" if lang == "typescript" and satisfied_set != ["tsx"]
                else None
            ),
        }
    return report


def main() -> None:
    report = discover()
    out_path = REPO_ROOT / "docs" / "atlascode-toolchain-report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    available = [l for l, r in report.items() if r["available"]]
    unavailable = [l for l, r in report.items() if not r["available"]]
    print(f"TOOLCHAIN DISCOVERY -- {len(available)}/{len(report)} available")
    for lang in sorted(report):
        r = report[lang]
        status = "AVAILABLE" if r["available"] else "UNAVAILABLE"
        if r["available"]:
            paths = ", ".join(f"{b}@{r['binaries_probed'][b]['resolved_path']}" for b in r["satisfied_requirement_set"])
            detail = paths
        else:
            detail = f"none of {r['requirement_sets_tried']} fully resolved"
        print(f"  [{status:11s}] {lang:12s} {detail}")
    print(f"\nUnavailable: {unavailable if unavailable else 'none'}")
    print(f"Report written: {out_path}")


if __name__ == "__main__":
    main()
