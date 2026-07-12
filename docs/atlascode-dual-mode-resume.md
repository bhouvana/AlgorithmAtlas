# AtlasCode Dual-Mode Run — Resume Point (session 2026-07-06, fifth session)

For the original architecture writeup see `docs/atlascode-dual-run-modes.md`.
This file is the short version for picking up cold in a new session.

## 1. Where are we?

Continuation session. Did NOT restart the project. Two pieces of work: (1) a
bounded audit of all 17 runners' source transport, since the prior session's
python/javascript argv-length bug turned out to be a whole vulnerability
class, not a one-off; (2) the next real language adapter in the sequence,
TypeScript, fully verified end-to-end (not just implemented). The full
216×17×2 matrix is still NOT done — honestly scoped below.

## 2. What is verified (re-run the commands below before trusting this)?

- **17-runner source-transport audit** (`docs/atlascode-runner-transport-audit.json`,
  generated from a manual read of every function in `notebook.py`'s
  `RUNNERS` dict, not inferred):
  - **2 more unsafe runners found beyond the already-fixed python/javascript**:
    `run_shell` (`cmd /c <source>` / `sh -c <source>` — source embedded
    directly in argv) and `run_ruby` (`ruby -e <source>` — same class of
    bug). Both fixed to temp-file transport this session, mirroring the
    existing `_run_via_tempfile` helper (`run_shell` writes a temp `.bat` on
    Windows / `.sh` on POSIX; `run_ruby` writes a temp `.rb`).
  - **15/17 runners were already safe**: typescript, cpp, c, java, go, rust,
    kotlin, swift, r, csharp, php, scala, perl all write source to a temp
    file (or temp dir + compile step) before ever invoking a subprocess —
    confirmed by reading each function, not assumed from naming.
  - Verified live: `run_shell` executed a 65KB generated `.bat` source
    correctly (exit 0, expected stdout, no `not found` misclassification).
    `run_ruby` could not be live-verified in this environment (`ruby` is not
    installed here — confirmed via `shutil.which`), but the code path is
    identical to the already-proven `_run_via_tempfile` used by python/js.
  - **11 new permanent regression tests**
    (`tests/test_notebook_runner_transport.py`): python/javascript at 32KB
    and 64KB generated source (well past Windows' ~32,767-char CreateProcess
    limit), stderr capture, timeout enforcement, and temp-file cleanup all
    still correct at these sizes; shell at 32KB (Windows-only, `skipif`
    guarded) plus its own cleanup check.
- **TypeScript Function Mode adapter** (new, this session) — the 3rd
  Function Mode language:
  - `TypeScriptFunctionAdapter` in
    `apps/backend/algorithm_atlas/atlascode/function_mode/adapters.py`: same
    JS-family calling convention as `JavaScriptFunctionAdapter` (positional
    args, `fn.length` arity check, snake_case `function_name` reused
    verbatim — same documented gaps as JS, not re-litigated here), but
    `generate_starter` emits real TypeScript type annotations
    (`number`/`string`/`boolean`/`T[]`/`T | null`) instead of JSDoc comments,
    since the language actually supports them. The generated driver itself
    stays loosely typed (`any` throughout) — deliberate, since `run_typescript`
    executes via `tsx`, which transpiles without type-checking, so strict
    driver typing would buy nothing.
  - Registered in `registry.py`'s `ADAPTERS` dict under `"typescript"`.
  - No infra fix was needed for this language: `run_typescript` already
    wrote source to a temp `.ts` file before this session started (confirmed
    by reading the code before starting, not assumed).
  - `scripts/backfill_ts_starter_code.py` added a `typescript` key to
    `starter_code_function` for the same 6 already-migrated problems — run
    for real against the live DB (not dry-run only): `Updated: 6 / 6`.
  - **Verified for real**: `scripts/verify_ts_function_mode.py` runs actual
    `tsx` subprocesses against the SAME 240 real DB test cases (never a
    second corpus) for all 6 problems — correct solution → 40/40 Accepted
    for every problem, deliberately-wrong solution → genuinely rejected (a
    real adversarial bug per problem), one partial-credit solution → genuine
    mixed 20/40, missing-function → real `Function Contract Error`. Full
    output captured this session, all passing.
  - **6 new permanent pytest tests**
    (`tests/test_atlascode_function_mode.py::TestTypeScriptAdapter`),
    mirroring `TestJavaScriptAdapter` exactly (visible-all-pass,
    wrong-solution-fails, missing-function, wrong-arity, runtime-error,
    boolean-return). Full suite: 573→**579 passed**, 1 skipped (was 562
    before the runner-transport tests, 573 after those, 579 after the
    TypeScript tests).
  - `docs/atlascode-dual-mode-coverage.json` regenerated:
    `function_mode_adapters_implemented` 2→**3**,
    `function_mode_run_verified` 12→**18** (6 problems × 3 languages, each
    cell backed by a real subprocess judge run, not inferred).
- **Real infrastructure finding, not just the adapter**: this dev
  environment had no globally-installed `tsx` binary, so every
  `run_typescript` call fell back to `npx tsx <path>` — measured at
  **~5.1 seconds per call** (npx resolution overhead, not compile time).
  For a 40-case Function Mode judge run under the existing 90s
  `_MAX_TOTAL_TIMEOUT`, that overhead alone would exceed the budget before
  ~18 cases finished — TypeScript Function Mode submissions would have
  systematically timed out in this environment even though every line of
  code was correct. Fixed operationally: `npm install -g tsx` (had to set
  `COMSPEC` first — esbuild's Windows postinstall script crashes with
  `ERR_INVALID_ARG_TYPE` when `COMSPEC` is unset, which it was in this
  session's shell). After the fix, `shutil.which("tsx")` succeeds and
  `run_typescript` takes its fast direct-binary path: **~540ms/call**, a
  ~9.4x improvement, comfortably inside the timeout budget. This is an
  **environment/deployment dependency, not a code bug** — flagging it
  because it would silently degrade to mass timeouts in any environment
  where `tsx` isn't globally resolvable, and the prior session's single-call
  Playwright verification of `run_typescript` was too fast a smoke test to
  ever have surfaced it.
- **Latent hang bug found + fixed in migration scripts**: both
  `backfill_js_starter_code.py` (pre-existing, from the prior session) and
  the new `backfill_ts_starter_code.py` used `database.py`'s module-level
  `engine` via `AsyncSessionLocal`/`init_db()` but never called
  `engine.dispose()` — the aiosqlite background connection thread kept the
  process alive after `asyncio.run()` returned, so the script's actual work
  finished in under a second but the process itself never exited on its
  own (confirmed via `timeout 30 python ...` → exit 124 before the fix, exit
  0 after). Fixed by disposing the engine at the end of both scripts. Real
  find, not hypothetical: this is exactly the kind of "looks hung, isn't
  actually making progress" failure mode the mission warned about, just
  caught at 15-second/6-problem scale instead of hours/216-problem scale.
- **DB path footgun found, not fixed** (deliberately, see below): there are
  two `atlas.db` files in this repo —
  `apps/backend/atlas.db` (110KB, 0 rows, stale/empty — schema is current
  but was apparently created by some invocation with `cwd=apps/backend`)
  and the real one at repo root (101MB, 216 problems, matches every number
  in this document). `config.py`'s `SQLITE_URL` is a relative
  `sqlite+aiosqlite:///./atlas.db`, so it resolves differently depending on
  the process's working directory at startup. Every command in this
  document assumes **repo root** as cwd. Not deleted or touched — it's not
  clear whether it's meaningful leftover state, and deleting a DB file
  unprompted is exactly the kind of action that needs a human's go-ahead
  first.

## 3. What is NOT done (be honest about this with the user)

- **210/216 problems still have zero Function Mode contract.** Only the
  same 6 array-hashing-variants problems as last session.
- **14/17 languages still have zero Function Mode adapter** (python,
  javascript, typescript now exist). Next in the natural sequence: a
  compiled language (e.g. Java or C++) would be the first real test of
  `evaluate_function`'s "only interpreted-language adapters exist today"
  assumption (see `runner.py`'s own docstring) — composing+running full
  source per case for a compiled language means recompiling per test case
  unless a compile-once strategy is added first. This is real, not
  mechanical, scope.
- **15/17 languages have zero per-problem Program Mode starter code**
  (only python 216/216, javascript/typescript 1/216 each) — unchanged from
  last session, still real, still separate from the Function Mode gap.
- **No formal per-language callable-name schema** — unchanged, still
  flagged, still not built.
- **No resumable/checkpointed migration infrastructure was built** — this
  session's TS backfill was again small enough (6 problems, one language)
  to do directly, same judgment call as last session. Once work turns to
  many more problems/languages per sitting, build this first.
- **Full 216×17 exhaustive route/language Playwright pass was not run** —
  same reasoning as last session, unchanged.
- **`run_ruby`'s temp-file fix could not be live-verified** in this
  environment (no `ruby` binary installed) — the code path is proven
  correct by direct equivalence to `_run_via_tempfile`, which IS proven
  (python/javascript/shell all use it), but this is inference, not a live
  ruby subprocess run. Flag this distinction; don't claim ruby was "tested."
- **The global `tsx` install is a manual environment fix, not a code
  change** — if this dev environment is ever reset/recreated, `run_typescript`
  will silently fall back to the slow `npx tsx` path again with no error,
  just quietly-worse performance risking Function Mode timeouts. No
  auto-detection or startup check for this was added — flagged as a real
  gap, not built, since it's arguably a deployment/ops concern (a Dockerfile
  or setup script installing `tsx` globally) rather than an application-code
  fix.

## 4. What batch comes next?

1. **A compiled-language Function Mode adapter** (Java or C++ suggested) —
   the first one that will force a real design decision in
   `function_mode/runner.py`, which currently composes+runs full source
   per test case (fine for python/javascript/typescript, expensive for a
   compile step). Decide: compile-once-per-submission (mirroring
   `notebook.py`'s existing `PREPARERS` pattern for Program Mode) versus
   accepting per-case recompilation cost with a tighter case count. Do this
   design work before writing the adapter, not after.
2. **Program Mode starter-code gap** (15/17 languages, all 216 problems) —
   still arguably higher product value, still unstarted, still needs
   per-problem stdin-parsing boilerplate rather than a script.
3. **Resumable migration infrastructure (Phase 19-21)** — still not built,
   still needed before either of the above at real scale.
4. **Resolve or explain the two-`atlas.db` situation** — at minimum,
   confirm with the user whether `apps/backend/atlas.db` is meaningful
   leftover state before anyone deletes it, and consider making
   `SQLITE_URL` an absolute path so cwd can never silently pick the wrong
   file again.

## 5. What commands validate current state?

```powershell
cd algorithm-atlas
python -m pytest apps/backend/tests -q                        # 579 passed, 1 skipped
python scripts/generate_dual_mode_coverage.py                  # regenerates docs/atlascode-dual-mode-coverage.json
python scripts/verify_js_function_mode.py                      # live node subprocess verification, 6 problems
python scripts/verify_ts_function_mode.py                      # live tsx subprocess verification, 6 problems (~3-5 min: ~521 subprocess launches)
python scripts/smoke_test_problem_routes.py                    # requires backend running on :8000; all 216 problems
npx tsc -b   # (from apps/frontend) -- must be clean
```

Before running anything TypeScript-related, confirm `tsx` resolves fast:
```powershell
where tsx   # should print a path, not nothing
```
If it prints nothing, `npm install -g tsx` first (on Windows, `$env:COMSPEC`
must be set in the shell running the install, or esbuild's postinstall
script crashes) — otherwise every `run_typescript` call silently falls back
to `npx tsx` at ~10x the latency, which risks the 90s per-submission timeout
budget on a full 40-case run.

Backend must be run with `--reload` during active development in this repo
(unchanged from last session's finding), and **from repo root** so the
relative `./atlas.db` resolves to the real 216-problem database, not the
stale empty one in `apps/backend/`:
```
python -m uvicorn algorithm_atlas.main:app --app-dir apps/backend --host 0.0.0.0 --port 8000 --reload
```

## 6. What must never be regenerated / reverted?

- Everything carried forward from the prior session's equivalent section
  (independent oracles, tree serialization format, `\r\n` normalization,
  `assemble_catalog()`'s 5-tuple signature, `resolveMode()`, the
  `supportsFunctionMode` undefined-safety fix) — unchanged this session,
  still applies.
- The temp-file execution fix in `run_python`/`run_javascript`/`run_shell`/
  `run_ruby` — reverting any of these to inline argv reopens the
  argv-length bug for that language.
- `TypeScriptFunctionAdapter`'s loosely-typed (`any`) driver and its reuse
  of the JS adapter's positional-argument/`fn.length` convention — this is
  deliberate, matching the documented JS adapter rationale, not an
  oversight to "improve" with stricter types.
- The `engine.dispose()` calls added to `backfill_js_starter_code.py` and
  `backfill_ts_starter_code.py` — removing them reintroduces the
  process-never-exits hang.
