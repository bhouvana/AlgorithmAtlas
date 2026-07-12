# AtlasCode Judge Workspace — Architecture

This document describes the current AtlasCode problem-solving workspace: the
Run-based judge pipeline, the execution contract, the bottom-console UI, and
the deliberate scope decisions behind what's shipped vs deferred.

## 1. Product surface: Run only

The workspace ships **one** judging action: **Run**. It evaluates the
problem's visible test cases (or a selected subset, or user-authored custom
cases) through the real judge and shows per-case results immediately. It
never persists anything and never touches hidden test data.

**Submit (the authoritative, all-hidden-tests judge run with persisted
history and cross-submission quality comparison) exists and is fully
functional in the backend**, but is intentionally not exposed in this
workspace's UI. Without a broader multi-user ecosystem, a submission history
and percentile comparison has no real audience yet and reads as decorative
rather than useful — surfacing it prematurely was explicit product feedback
during this build ("remove Submit completely, only keep Run"). The
`POST /api/v1/submissions` endpoint, `Submission` model, hidden-test
redaction, and `/quality` percentile endpoint are all still live and tested;
re-enabling Submit in the UI later is a frontend-only change (wire the
button back to `submitSolution()`, per `git history` — no backend work
required).

## 2. Execution contract (`apps/backend/algorithm_atlas/api/v1/notebook.py`)

Every language runner returns `LangRunResult`, not a bare tuple:

```python
@dataclass
class LangRunResult:
    stdout: str
    stderr: str
    duration_ms: float
    exit_code: int | None
    timed_out: bool = False
    memory_kb: float | None = None
    compile_output: str | None = None   # non-None only for a failed compile
    compile_failed: bool = False
```

- **exit_code**: real, from the subprocess — not inferred from stderr content.
- **memory_kb**: real, sampled via `psutil` while the subprocess is alive (a
  background thread runs `Popen.communicate()` so the main thread is free to
  poll). On Windows this reads the OS-tracked `peak_wset`; on POSIX it's a
  running max of `rss` samples bounded by the ~3ms poll interval — a real
  measurement, not a fabricated one, but an approximation on POSIX
  specifically (documented here, not hidden). A process that exits faster
  than one poll interval yields `memory_kb=None`, never a guessed value.
- **compile_failed / compile_output**: structural, only for languages with an
  isolable compile step (see §4). Never guessed from stderr text.

### Compile-once-per-submission

Recompiling C++/Java/Rust/Kotlin/C from scratch for every test case was
measured at **~460–490ms per compile+run cycle** (trivial program). For a
40-case judge run that's 18–20 seconds of pure recompilation overhead.
`PreparedProgram` (in `notebook.py`) compiles once and re-invokes the same
binary per case — measured at ~29ms/case after the first compile (a
15–17× speedup). `PREPARERS: dict[str, ...]` holds the compile-once path for
cpp, c, rust, kotlin, java; other languages (interpreted, or without a split
compile/run step in this codebase — csharp's dotnet fallback, scala, swift,
go) still compile+run per case, documented as a known limitation rather than
force-fit into the same abstraction.

## 3. Evaluator (`apps/backend/algorithm_atlas/submission/evaluator.py`)

`evaluate(source, language, test_cases)` is the single judging function used
by both Run and Submit (Submit backend). **It never short-circuits** — every
case in the list always executes (or hits its own per-case timeout), because
honest partial-pass reporting ("3/5 passed") requires knowing the outcome of
all 5, not just the cases before the first failure. This was a real,
measured bug in the pre-existing evaluator (`break` on first `Wrong Answer` /
`Runtime Error` / `Time Limit Exceeded`).

Verdict precedence for the one **headline** verdict shown (every case's own
verdict is still reported individually):

```
Compilation Error   > Time Limit Exceeded > Runtime Error > Wrong Answer > Accepted
```

An aggregate time budget (`_MAX_TOTAL_TIMEOUT`, 90s) bounds worst-case
latency for a pathologically hanging submission — cases past the budget are
marked `Time Limit Exceeded` with an honest note ("Judge time budget
exhausted before this case could run"), never a fabricated per-case timing
claim.

`TestCaseLike` is a `Protocol`, not a concrete class — Run's user-authored
custom cases (never persisted to `test_cases`) and Submit's real `TestCase`
rows go through the exact same judging code path, via a lightweight
`_AdHocCase` dataclass for the former.

## 4. Verdict states — what's structural vs. heuristic

| Verdict | Detection | Notes |
|---|---|---|
| Accepted / Wrong Answer | exact string compare, `\r\n`→`\n` normalized | |
| Runtime Error | real nonzero `exit_code` | |
| Time Limit Exceeded | real `timed_out` flag from the subprocess layer | |
| Compilation Error | real nonzero compiler exit code | **only** for cpp, c, java, rust, kotlin, and csharp's mcs/mono path |
| Internal Judge Error | unsupported language / zero test cases | |

Languages without an isolable compile step in this judge (Python, JS, TS,
shell, ruby, php, perl, R, go, scala, swift, csharp's dotnet-run fallback)
report a syntax/setup failure as **Runtime Error**, not Compilation Error —
a documented scope boundary, not a bug. Building a real per-language
compile/run split for all 17 languages is a larger, lower-priority
follow-up.

## 5. Run endpoint (`POST /api/v1/problems/{slug}/run`)

```json
{ "language": "python", "code": "...", "mode": "visible" | "selected" | "custom",
  "case_indices": [0, 2],
  "custom_cases": [{ "input_data": "...", "expected_output": "..." }] }
```

- `mode=visible`: every visible case for the problem.
- `mode=selected`: a subset of visible cases by index.
- `mode=custom`: user-authored scratch cases, never persisted server-side.
  `expected_output` is optional — when omitted, the case is judged as
  `"executed"` (real output shown), **never** a fabricated pass/fail.
- Never loads, executes, or returns anything about hidden test cases.
- Never creates a `Submission` row, never touches `UserProgress`/acceptance
  stats.

## 6. Frontend workspace

```
Topbar (Catalog / title / difficulty / Visualize)
┌───────────────────────┬──────────────────────────────────────┐
│ Problem statement     │ Language ▾   Reset   Run              │
│ (resizable width)     │ ────────────────────────────────────  │
│                       │ Monaco editor                         │
│                       │ ──────────────────────────────────── │ ← resizable divider
│                       │ Testcase | Test Result | Console      │
│                       │ (bottom console, resizable height)    │
└───────────────────────┴──────────────────────────────────────┘
```

- **Resizing**: `useResizeDrag` (pointer events, incremental deltas) drives
  `adjustProblemPaneWidthPx` / `adjustConsoleHeightPct` — both are *delta*
  store actions (`set((s) => ...)`), not absolute setters, specifically so a
  single continuous drag gesture accumulates against the latest state rather
  than a value captured when the drag started (a real stale-closure bug
  caught during this build).
- **Testcase tab**: visible cases (checkboxes for batch "Run Selected") +
  user-authored custom cases (editable input/expected, duplicate/reset/delete).
  Custom cases persist locally per problem (zustand `persist`, not server-side).
- **Test Result tab**: partial-pass header banner (passed/total, runtime,
  memory), per-case tabs. Only **visible cases and non-passing cases** get an
  individual tab — a passing case with no diagnostic value left to show
  doesn't need one. (There is no hidden-case concept in Run's results at all,
  since Run never touches hidden cases.)
- **Console tab**: concatenated raw stdout/stderr/compile-output log across
  all cases in the last Run, with copy/clear/wrap controls.
- **Language dropdown**: all 17 judge-supported languages are always
  selectable, regardless of which ones the current problem has starter code
  for — a problem without a template for a given language shows a blank
  editor for it (not Python's code mislabeled under different syntax
  highlighting, which was the actual pre-existing bug).
- Monaco: `automaticLayout: true` handles editor resize correctly across
  both the horizontal and vertical divider drags without manual `.layout()`
  calls.

## 7. Atlas AI integration

`useAtlasStore.problemBridge` (frontend, `src/ai/store.ts`) mirrors the
existing `notebookBridge` pattern. `ProblemPage.tsx` keeps it in sync with
`{ slug, title, difficulty, language, source, lastRunSummary,
lastRunVerdict, firstFailingCase }` on every relevant state change, and
clears it on unmount. `useAtlasContext.ts` folds it into `AtlasContext.problem`
when `page === 'atlascode'`. The backend's `context_builder.py` renders it
into the same natural-language context paragraph injected into every AI
agent's system prompt, alongside the existing notebook/simulation/lesson
context blocks.

Because this workspace has no Submit/hidden-test path, the bridge is
**structurally incapable** of leaking hidden test data — there's no hidden
data flowing through the Run-only pipeline in the first place.

## 8. Honest data — what's real, what's deferred

| Dimension | Status |
|---|---|
| Correctness (passed/total) | Real |
| Runtime (per-case, median/p95/slowest) | Real |
| Memory | Real (psutil), with the documented POSIX-approximation caveat above |
| Compilation/Runtime/TLE detection | Real for the languages listed in §4 |
| Runtime percentile ("beats N%") | Real, backend-only (`/submissions/{id}/quality`) — requires ≥5 comparable Accepted submissions for the same problem+language+judge_version+test_suite_version; not surfaced in the Run-only UI |
| Complexity estimate | **Not implemented.** No AI call is wired for this; `complexity_estimate` is always `null`, never a fabricated Big-O guess |
| judge_version / test_suite_version | Real, stamped per-submission (backend) so a later test-data fix doesn't retroactively skew old comparisons |

## 9. Known limitations (not fixed this session, flagged not ignored)

- Compile/Runtime Error distinction is heuristic-free but incomplete: only
  5 of 17 languages have a real compile step in this judge.
- Memory measurement on POSIX is a polling approximation, not a kernel-level
  peak (Windows' `peak_wset` is exact; POSIX has no equivalent exposed via
  `psutil` without `resource.getrusage`, which has its own cross-thread
  accounting problems under concurrent execution — deliberately not used).
- No backend test isolation tooling changes were made beyond this feature's
  own test file (`tests/test_atlascode_judge.py` uses a temp SQLite engine +
  `dependency_overrides`, the correct pattern for future AtlasCode backend
  tests to copy) — the pre-existing `tests/test_api.py` still runs against
  whatever `atlas.db` the working directory resolves to.
- Complexity estimation, Submit UI, submission history UI, and quality-panel
  UI are backend-complete, frontend-deferred (see §1).
