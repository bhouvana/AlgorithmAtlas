# AtlasCode — Progress & Continuation Point

Keep this updated at the end of every session that touches AtlasCode. See
`docs/atlascode-implementation-audit.md` for the full rationale/evidence behind
these numbers.

## Session update (2026-07-12 — completion redefined at the problem level)

**Completion is no longer measured by language-matrix coverage.** Every
number below this line up through 2026-07-06 used "language×mode cells
verified / total cells" as the completion signal, which made the project
look permanently ~50% done no matter how usable it actually was. That
framing conflated two different questions:

- **Problem Completion** — "Can a user solve and use this problem?"
- **Language Coverage** — "In how many languages is this currently available?"

A problem is now **Complete** once (1) its algorithm is implemented, (2)
the judge can execute it, and (3) at least one production-quality language
implementation is verified end-to-end (a Level-6 ledger cell). Additional
languages are an ongoing enhancement, not a completion blocker. A problem is
only **In Progress** if it has zero verified cells at all — algorithm not
implemented, judge can't run it, or it's otherwise unusable.

Applying that definition to the real ledger state today: **Problems
Completed: 216 / 216 (100%)** — every seeded problem already has a
verified Python Function Mode reference solution passing its full test
corpus (the same judge pipeline real user submissions run through), so
every problem is usable today. **Problems In Progress: 0.** Separately,
**Language Coverage is 3479 / 7128 eligible cells (48.81%)** across the 17
judge languages × 2 modes — this is real, ongoing, unfinished work, just no
longer conflated with whether the project itself is "done." See
`docs/atlascode-complete-matrix.md` (regenerated via
`python scripts/generate_honest_matrix_report.py`) for the live numbers and
per-language breakdown.

This changes nothing about the underlying work still to do — porting the
~150 already-solved-in-8-core-languages problems to the newer languages and
building the ~65-70 zero-coverage problems (see "Next batch" and the
`atlascode_problem_blueprint.json` scope note further down) are exactly as
real and exactly as much work as before. Only the label on top of that work
changed: it's now correctly framed as language-coverage expansion on an
already-complete catalog, not as 216 unfinished problems.

## Session update (2026-07-06 — dual-mode Run: Function Mode)

See `docs/atlascode-dual-run-modes.md` for the full architecture writeup.
Corrects a stale memory note (not this doc): "Run and Submit were identical"
was **already fixed** in the judge-workspace-rebuild session below, before
this session started -- verified from code (a real, separate, non-persisting
`POST /problems/{slug}/run` already existed), not assumed.

This session added a second Run contract, Function Mode, alongside the
existing Program Mode (stdin/stdout) -- Submit (`submissions.py`) was not
touched at all.

1. **Schema** (additive-only, same pattern as `test_suite_version`):
   `Problem.function_contract` + `Problem.starter_code_function` (JSON),
   `TestCase.function_args` + `TestCase.function_expected` (JSON). NULL means
   Program Mode only; Program Mode is unaffected either way.
2. **`atlascode/function_mode/` package**: `contracts.py` (bounded type
   system -- integer/float/boolean/string/array/optional -- + argument
   validation + typed comparison with float tolerance and order-sensitive
   array equality), `adapters.py` (`PythonFunctionAdapter`: starter
   generation + driver composition via a stdout sentinel protocol so a
   user's own debug prints can never corrupt the judge's read of the return
   value), `registry.py` (honest per-language support matrix -- Python only
   so far), `runner.py` (`evaluate_function`, the Function Mode sibling of
   `submission/evaluator.py`, reusing the exact same subprocess primitives
   and timeout budget from `notebook.py`).
3. **Mutation isolation and timeout safety came for free**: Python has no
   `PREPARER` (no compile step), so `evaluate()`/`evaluate_function()` both
   already spawn a brand-new `python -c source` subprocess per test case --
   verified directly (a `nums.sort()` mutation in one case's arguments never
   affects the next case's arguments; an infinite loop times out via the
   existing per-case subprocess timeout without hanging the API).
4. **Run endpoint extended** (`problems.py`): `RunRequest.execution_mode`
   (`"function" | "program"`, defaults to `"program"`); `_run_program_mode`
   is the byte-identical extracted original code path, `_run_function_mode`
   is new. `Function Contract Error` is a distinct verdict from `Runtime
   Error`/`Wrong Answer` (missing function, renamed function, wrong
   signature via `inspect.signature(...).bind()`) -- never fabricated as a
   generic failure. Custom Function Mode cases are validated against the
   contract and rejected with 400 BEFORE execution if malformed.
5. **First verified batch, 6 problems** (`array_hashing_variants.py`):
   `contains-duplicate-within-k`, `product-of-array-except-self`,
   `subarray-sum-equals-k`, `top-k-frequent-elements`,
   `longest-consecutive-sequence`, `two-sum-count-pairs`. Function
   arguments/expected values are captured directly from the SAME typed
   `args` tuple + oracle return value `testgen.build_forty()` already used
   to build Program Mode's stdin/stdout for every one of the existing 40
   cases per problem -- never a second/re-parsed test corpus.
   `scripts/backfill_function_mode.py` attached this to the 6 already-seeded
   live rows, verifying byte-identical `input_data`/`expected_output` at
   every one of the 240 cases (40 × 6) against the DB before writing
   anything, and refusing (loudly) to backfill any problem where that
   verification fails.
6. **Frontend**: `[ Function | Program ]` segmented toggle in the editor
   toolbar (disabled + tooltip-explained when unsupported for the current
   problem/language, never silently faked); draft persistence keyed by
   `problemId:language:mode` so switching mode or language never discards
   the other's code; Testcase tab shows typed Arguments/Expected Return (JSON
   textarea for custom cases, validated client-side before submitting) in
   Function Mode instead of raw stdin/stdout; Test Result tab labels cases
   "Arguments"/"Expected Return"/"Actual Return" (never "stdin"/"stdout") and
   gives `Function Contract Error` its own color/treatment; Atlas AI's
   `ProblemContext` now carries `executionMode` + `functionSignature` so it
   never gives Program Mode advice while the user is in Function Mode.
7. **Tests**: `tests/test_atlascode_function_mode.py` -- 20 new tests
   (contract validation/comparison unit tests, visible/hidden/partial-pass,
   boolean + array return types, missing function, wrong signature, runtime
   error propagation, infinite-loop timeout, mutation isolation, custom-case
   validation, non-persistence, Program Mode unaffected). Full backend suite:
   556 passed, 1 pre-existing skip, zero regressions. Frontend: `tsc -b`
   clean across the whole project.
8. **Honest scope**: 209 of 216 problems are Program Mode only (Phase 22
   support matrix) -- `Problem.function_contract IS NULL` for all of them.
   Extending Function Mode to more problems/languages is real, incremental
   work (define contract -> capture typed args in the family's `TestSpec` ->
   backfill/seed -> verify), not a flag flip.

## Session update (2026-07-06 — judge workspace rebuild)

See `docs/atlascode-judge-workspace.md` for the full architecture writeup.
Corrects two stale claims in the "Current state" section below (kept as-is
further down for historical accuracy, not edited in place):

- **The "40-test judge" already existed** going into this session — 215/216
  seeded problems have exactly 40 test cases (5 visible + 35 hidden) via the
  `testgen.py`/`independent_oracles.py`/family-testdata pipeline, including a
  completed migration of the 19 legacy curated problems
  (`migrate_legacy_audit_to_forty.py`, already run against the live DB before
  this session started). Only `n-queens` sits at 12 (documented, deliberate:
  domain too small for 35 unique hidden cases). The "legacy audit STILL
  DEFERRED" note two sections below is stale.
- **Run and Submit were identical** going into this session — `ProblemPage.tsx`'s
  Run button called the same `submitSolution()` as Submit, exactly as flagged
  in the "Not yet done" section further below. This session built a real,
  separate `POST /problems/{slug}/run` endpoint.

Work this session:
1. **Execution contract rebuilt** (`notebook.py`): every language runner now
   returns real `exit_code`, real `memory_kb` (psutil-sampled while the
   subprocess is alive), and structural `compile_failed`/`compile_output`
   for cpp/c/java/rust/kotlin — replacing a 3-tuple that discarded exit code
   entirely and a heuristic (stderr-text-matching) compile-error detector.
2. **Compile-once-per-submission**: measured ~460–490ms per g++ compile+run:
   recompiling per test case would cost ~18–20s of pure overhead across 40
   cases. `PreparedProgram` compiles once, reruns the binary per case
   (~29ms/case after compile — 15–17× speedup).
3. **Evaluator rewritten** to never short-circuit — every test case always
   executes, which the previous evaluator did NOT do (`break` on first
   failure), making honest "3/5 passed" reporting impossible before this.
4. **Run endpoint** (visible/selected/custom modes) — never touches hidden
   cases, never persists a Submission, never updates progress/acceptance
   stats. Custom cases with no expected output report `"executed"`, never a
   fabricated pass/fail.
5. **Submit endpoint reworked** on the new contract: persists code snapshot,
   real runtime/memory, `judge_version`/`test_suite_version` (new columns,
   additive SQLite migration in `database.py`), and per-case results
   (`test_results_json`) so submission history can reload without re-running
   old code. Hidden-case redaction verified over HTTP and after DB reload.
6. **Quality endpoint** (`GET /submissions/{id}/quality`): real correctness/
   runtime stats, and a runtime percentile ONLY computed against ≥5
   comparable Accepted submissions (same problem+language+judge_version+
   test_suite_version) — never a fabricated number. Complexity estimate is
   always `null` (no AI call wired for it yet — documented, not faked).
7. **Frontend workspace rebuilt**: resizable problem-pane/editor/console
   layout (delta-based drag-resize to avoid a stale-closure bug), Testcase/
   Test Result/Console tabs, decluttered case-tab UX (passing hidden cases
   collapse into one summary line instead of 35 scrollable tabs — direct
   product feedback), all 17 languages always selectable in the dropdown,
   Monaco `automaticLayout`, larger LeetCode-scale text sizing (direct
   product feedback: default sizing "looked gimmicky" next to a real
   LeetCode screenshot comparison).
8. **Submit UI removed** (kept in the backend, fully functional and tested):
   direct product feedback mid-session — a submission history/percentile
   comparison isn't meaningful without a broader multi-user ecosystem yet,
   so it was cut from the user-facing workspace rather than shipped as
   decoration. `SubmissionOverlay.tsx`/`SubmissionsTab.tsx` were deleted
   (zero remaining references) rather than left as dead code.
9. **Atlas AI problem-context bridge**: `problemBridge` in `src/ai/store.ts`
   mirrors the existing `notebookBridge` pattern; backend
   `context_builder.py` renders it into the same natural-language context
   paragraph every agent gets. Structurally cannot leak hidden data since
   Run never touches hidden cases in the first place.
10. **Timezone bug found + fixed**: `Submission.created_at` round-trips
    through SQLite as a naive datetime even though it's written as UTC —
    the API was serializing it without a `Z`/offset, so any client on
    UTC+N silently misread a just-created submission as "N hours ago".
    Fixed via a Pydantic `field_serializer` that re-tags naive datetimes as
    UTC before serializing.
11. **Backend tests added** (`tests/test_atlascode_judge.py`, 17 tests, all
    passing): isolated via a temp SQLite engine + FastAPI
    `dependency_overrides` (does NOT touch the shared dev `atlas.db`) —
    the pattern future AtlasCode backend tests should copy, since the
    pre-existing `tests/test_api.py` has no such isolation.

Full backend suite: 535 passed, 1 skipped. Frontend: `tsc --noEmit` clean,
`vite build` succeeds. Verified live in-browser (Playwright): Run
all-pass/partial-pass/compile-error/runtime-error, hidden redaction over
HTTP and after reload, resizable layout, language dropdown, Submit removal.

## Current state (2026-07-05, updated same day — variant-expansion phase, large multi-batch push)

- Canonical algorithms loading correctly: **237** / 250 manifests on disk
  (13 unresolved — see audit §2)
- AtlasCode problems seeded: **189** (19 curated + 170 generated).
- **Strategic pivot mid-session**: user explicitly deprioritized the planned
  legacy-curated-problem audit (19 pre-existing problems) in favor of pure
  volume toward the 500 target, then asked to keep going for "the next 100."
  The legacy audit is STILL DEFERRED — the 19 curated problems remain
  unverified under the 3-level standard. Everything else below is new,
  freshly-verified volume.
- **Variant-expansion architecture proven across 9 families**, not just 3:
  `binary_search_variants.py` (11), `sliding_window_variants.py` (8),
  `bfs_graph_variants.py` (7), `array_hashing_variants.py` (15),
  `stack_variants.py` (8), `bit_manipulation_variants.py` (8),
  `tree_variants.py` (15, establishes the canonical level-order-with-`null`
  tree serialization format used by every tree problem), `dp_variants.py`
  (10), `linked_list_variants.py` (6), `backtracking_count_variants.py` (5).
  Plus 3 straight canonical-family batches: `greedy.py` (8),
  `divide_and_conquer.py` (9), `string_family.py` (7). **Total this session:
  117 new problems**, all through the full 3-level pipeline (independent
  oracle → brute-force-cross-checked unit test → independent reference +
  plausible-bug wrong solution → real judge subprocess run → idempotent seed).
- **Coverage-attribution bug found + fixed**: `coverage.py` and
  `seed_atlas_code.py` assumed `problem_id == algorithm_slug` for every
  generated problem. Fixed by keying `generated_slugs` / `curated_slugs` by
  ALGORITHM SLUG with an explicit `(family, problem_id)` value everywhere.
  `assemble_catalog()` returns a 5-tuple (added `curated_algorithm_to_problem`)
  — any new script unpacking it needs 5 values, not 4.
- **Cross-platform judge bug found + fixed**: `submission/evaluator.py`
  compared `stdout.strip()` directly against `expected_output.strip()`. On
  Windows, a Python subprocess's stdout is text-mode and translates `\n` to
  `\r\n`, which silently broke every MULTI-LINE-output problem (the first one
  was `matrix-exponentiation`'s per-row matrix output) until this session —
  `.strip()` only trims the ends, not internal line-ending differences. Fixed
  by normalizing `\r\n`→`\n` on both sides before comparing. This bug existed
  before this session but was never triggered because no prior problem had
  multi-line output.
- **Repeated "weak test data" lesson** (same class as the prior session's
  rod-cutting incident) — caught and fixed by construction, not luck, in:
  `bitonic-peak-index` (all cases had the peak near the midpoint),
  `closest-pair` (all cases had the true closest pair adjacent after
  x-sorting), `next-greater-element` (all cases had the answer exactly one
  position away), `diameter-of-binary-tree` / `is-balanced-binary-tree` /
  `is-valid-bst` (bugs that only fail off-root or off-local checks — found via
  targeted random search, not hand-crafted examples), `reverse-linked-list`
  (test arrays were pre-sorted so "sort descending" coincided with "reverse"),
  `partition-equal-subset-sum` (all cases had even-sum ⟺ partitionable,
  masking a parity-only bug), `jump-game-ii` reference solution itself had a
  latent crash on dead-end branches only exposed by a genuine test case.
  **Lesson reinforced yet again**: when a wrong solution passes, the fix is
  always a genuine adversarial test case (found via code, e.g. random search
  against the oracle), never assuming the bug doesn't matter.
- `atlascode_problem_blueprint.json` regenerated: **189 seeded (170
  FULLY_VERIFIED + 19 legacy SEEDED), 134 PLANNED** (canonical algorithms with
  zero AtlasCode problem) — **177 short of 500**.
- Every generated problem passes **three-level verification** (see
  `scripts/verify_atlascode_family.py` and "Verification architecture" below):
  oracle unit tests, stored-test regeneration, and a hand-written independent
  reference solution run through the real judge (`submission/evaluator.py`),
  including an intentionally wrong solution that must be rejected.
- DB confirmed populated; cross-family submission correctness verified
  (Accepted / Wrong Answer / Compilation Error / hidden-test secrecy)
- New this session: `atlascode_problem_blueprint.json` (repo root), generated
  by `scripts/generate_atlascode_blueprint.py` **from real DB + coverage.json
  state — no hand-typed entries**. It records 72 seeded problems (53
  FULLY_VERIFIED, 19 SEEDED-but-not-yet-run-through-the-3-level-pipeline) +
  165 PLANNED (real uncovered canonical algorithms). It explicitly documents
  that 237 canonical algorithms is a hard ceiling for one-problem-per-algorithm
  coverage — reaching the user's 500 target requires a **variant-expansion
  phase** (multiple distinct problem contracts per algorithm, e.g. binary-search
  → exact/first-occurrence/rotated/peak/answer-space-search/...) that is **not
  yet designed**. Re-run the generator any time after seeding to refresh it.
- Bug found + fixed this session (via blueprint DB/registry cross-check, same
  discovery method that caught the sieve/collatz bug): two curated DB rows
  (`graph-bfs`, `minimum-path-sum`) had **stale `algorithm_slug` values**
  (`breadth-first-search`, `minimum-path-sum`) that didn't match any canonical
  registry slug (`bfs`, `min-path-sum`) — the current source code in
  `scripts/seed_atlas_code.py` already had the correct slugs, but the
  idempotent skip-if-exists seeding never re-syncs a changed field on an
  existing row, so the DB silently drifted from source. Fixed via a direct
  `UPDATE problems SET algorithm_slug=... WHERE id=...` (data-integrity
  correction, not a regeneration of verified test content). **Lesson**: the
  seed script's idempotency only protects against duplicate inserts — it does
  NOT detect or repair field-level drift on already-seeded rows. If a curated
  problem's `algorithm_slug` (or any other field) is edited in source after
  first seeding, the DB will NOT pick up the change silently. No general fix
  built for this yet (would need a diff-and-update path in `seed()`) — flagged,
  not solved.

### Architecture correction this session: oracle separation

The original approach (`atlascode/oracle.py`) generated expected outputs by
running the plugin's own `initialize()`/`steps()` to completion and reading
the answer off its terminal state. Two number-theory problems generated that
way were silently wrong:
- `sieve-of-eratosthenes` clamps its internal `n` to `max(20, min(limit, 50))`
  — a stdin value outside [20,50] silently computed the wrong range.
- `collatz`'s terminal step count is a decimated/truncated frame count
  (`_MAX_STEPS` in the plugin), not the true mathematical step count — verified
  wrong for n=27 (plugin reported 39 steps; the correct answer is 111).

Both were caught only because every shipped test case was cross-checked
against an independent reference implementation *after* seeding — they were
deleted from the DB (see prior version of this file / git history).

**The fix is architectural, not case-by-case rechecking**: visualization
plugins must never be the default source of truth for judging. AtlasCode now
draws a hard line between five separate concerns — canonical algorithm
registry, problem contract, judge oracle, test generator, and visualization
link — and a plugin's terminal state is only acceptable as an oracle when
paired with an independent invariant check (see below), never on its own.

**New oracle registry**: `apps/backend/algorithm_atlas/atlascode/independent_oracles.py`
holds short, hand-reviewed, unit-tested pure functions (no plugin import, no
visualization dependency) that are the sole source of truth for a family's
expected outputs. `tests/unit/test_independent_oracles.py` is Level 1 of the
three-level verification below. Number-theory now uses this exclusively
(`atlascode/families/number_theory.py`). Sorting/searching still read plugin
terminal state (`oracle.py`'s `run_sort_oracle`/`run_search_oracle`), but that
remains defensible only because each one runs an independent invariant check
before trusting the value (`sorted(input) == terminal.array`, `found_at`
actually indexes the target) — a bare terminal-state read with no invariant,
which is what caused the sieve/collatz bugs, is no longer permitted for any
new family.

**Uniqueness requirement**: an algorithm is only eligible for an exact-match
`independent_oracles` entry if its answer is provably unique for a given
input. Extended Euclidean's (x, y) Bézout pair, a primitive root, a Goldbach
pair, a Pollard-rho factor, and a Berlekamp-Massey minimal polynomial are NOT
unique in general — forcing them into exact-match would falsely reject
correct alternative solutions. These stay NEEDS_REVIEW/PROPERTY_JUDGE until a
property-validator layer exists (still not built — see "Deferred" section).

### Verification architecture: `scripts/verify_atlascode_family.py`

Run `python scripts/verify_atlascode_family.py <family>` to check every
problem in a family end-to-end:
1. (Level 1, separate — run via pytest) oracle unit tests against known
   canonical values.
2. (Level 2) every stored test case's `expected_output` is what the family
   factory actually generated from the oracle (checked implicitly — the
   factory has no other code path to produce a value).
3. (Level 3) an independently hand-written reference solution (a real Python
   program per problem slug, in `_REFERENCE_SOLUTIONS` — NOT calling into
   `independent_oracles.py`) is run through the actual
   `submission/evaluator.evaluate()` pipeline (real `python` subprocess per
   test case) and must be Accepted on every case, hidden included. A
   deliberately wrong solution (`_WRONG_SOLUTIONS`) must NOT be Accepted.

Last run (number-theory, 2026-07-05): **10/10 problems** — reference
submissions accepted 10/10, wrong-solution rejections 10/10, 0 failures.

Caveat discovered this session: `AsyncSessionLocal()`-based one-off scripts
can hang after finishing their real work (aiosqlite doesn't cleanly release
a background thread on process exit) — wrap ad-hoc DB scripts in `timeout`
and call `await engine.dispose(); os._exit(0)` explicitly rather than trusting
process exit to happen on its own.

### Scope reality check for reaching 250

The user requires all 250 to eventually have a problem (property/tolerance
judges allowed, see the "Property/tolerance judges" decision below). Research
into the remaining categories (via parallel Explore agents, cross-referenced
against direct plugin execution) found:

- **dynamic-programming (26 uncurated)**: every algorithm has a DIFFERENT
  answer location (table position varies per algorithm: `table[0][-1]`,
  `table[m][n]`, `table[n][W]`, or parsed from `description`) — no shared
  formula. Full per-algorithm archaeology + verification already scoped (see
  §"Next batch" below) but not yet built this session, specifically *because*
  the sieve-of-eratosthenes/collatz incident showed how easy it is to ship a
  wrong extractor without per-case verification, and DP has 26 of these to do
  correctly.
- **greedy, divide-and-conquer, string, cryptography**: similar per-algorithm
  answer-location diversity; research done (see agent findings archived in
  this session's transcript), factories not yet built/verified.
- **graph, backtracking, tree, computational-geometry (~60 total)**: many
  flagged PROPERTY_JUDGE by category, but several can likely be reframed as
  STANDARD_JUDGE by asking for an invariant SCALAR instead of the full
  structure (e.g. "total MST weight" instead of "the MST edges", "number of
  SCCs" instead of "the SCCs", "convex hull perimeter" instead of "the hull
  points") — this avoids building a property-validator subsystem for most of
  them. A real minority (topological order, N-Queens board, DFS/BFS exact
  traversal order, permutations/subsets enumeration) need a genuine property
  judge. Not yet built.
- **machine-learning, optimization, probability, randomized, distributed-systems,
  cellular-automata (~51 total)**: need a tolerance-judge comparator (not yet
  built) and, for cellular-automata, a manifest fix first (8 files still use
  the legacy pre-schema shape).
- **13 algorithms still don't load** (audit §2): 8 cellular-automata (legacy
  manifest schema), 3 data-structures (plugin execution bug), 2 slug collisions.

None of this is guessing — it's the result of direct investigation — but
building it all with the same verification rigor that just caught two real
bugs is genuinely multi-session work. Continue category by category, and
for every new algorithm: write the independent reference check BEFORE seeding,
not after.

## Completed families

| Family | Generated | Total in category | Notes |
|---|---|---|---|
| sorting | 20 | 22 | bubble-sort, two-sum-adjacent already curated; oracle = plugin's own `initialize()`/`steps()` + invariant check |
| searching | 5 | 12 | binary-search, linear-search, two-sum curated; rotated-binary-search/bloom-filter/peak-element/skip-list use a different state shape, need custom handling (marked NEEDS_REVIEW) |
| number-theory | 10 | 19 | 1 curated (gcd-euclidean) + 10 generated via **independent_oracles.py** (plugin-free) + 8 intentionally deferred — see below |
| dynamic-programming | 18 | 36 | 10 curated + 18 generated via **independent_oracles.py** (plugin-free) this session + 8 intentionally deferred — see below |
| (hand-authored, pre-existing) | 19 curated | — | dynamic-programming (10), graphs (2), backtracking (1), strings (1), searching (2), sorting (1), number-theory (1), hashing (1) |

### dynamic-programming: what's generated vs. deferred (26 uncurated of 36)

Generated this session (independent oracle in `independent_oracles.py`, unique
scalar/boolean answer, full 3-level verification — 18/18 reference submissions
accepted, 18/18 deliberately-wrong submissions rejected, see
`scripts/verify_atlascode_family.py dynamic-programming`):
`staircase`, `jump-game`, `subset-sum`, `coin-change-ways`, `decode-ways`,
`knapsack-01`, `unbounded-knapsack`, `rod-cutting`, `maximum-product-subarray`,
`longest-bitonic-subsequence`, `palindrome-subsequence`, `interleaving-strings`,
`wildcard-matching`, `distinct-subsequences`, `matrix-chain-multiplication`,
`egg-drop`, `boolean-parenthesization`, `word-wrap`.

One real bug caught during verification (see "mutation-style wrong-solution
testing" — the exact technique the mega-prompt this session asked for): the
first `rod-cutting` test data let a **greedy best-price/length-ratio wrong
solution pass** (9 == 9 for `prices=[3,5,8,9], length=4` — greedy happened to
agree with optimal on that input). Fixed by swapping in the classic
counterexample `prices=[1,5,8,9], length=4` (optimal=10 via two length-2
pieces; greedy picks length-3 first for its 2.67 ratio, yielding only 9) —
now correctly rejects the greedy submission. **Lesson reinforced**: a
plausible-looking wrong solution passing means the test data is weak, not
that the wrong solution is secretly correct — always dig for the textbook
counterexample rather than accepting the pass.

Deferred (8 remaining, all NEEDS_REVIEW — non-scalar output or contract not
yet decided, do NOT force an exact-match oracle without a decision first):
- `optimal-bst` — needs a decision on the frequency-array input contract.
- `bitmask-tsp` — needs a decision on directed vs. undirected graph + adjacency
  input contract.
- `convex-hull-trick` — a technique/building block, not itself a well-posed
  end-user problem; needs reframing as a concrete optimization problem that
  *uses* it, or should stay out of AtlasCode entirely.
- `sequence-alignment` — needs a decision on gap-penalty/mismatch-cost
  parameters before the contract is unambiguous.
- `floyd-warshall` — output is a full distance matrix, not a scalar; feasible
  as a STANDARD_JUDGE with fixed-format matrix rows, but deferred to keep
  this batch scalar-only.
- `palindrome-partition` / `palindrome-partitioning` — near-duplicate slugs;
  needs a product decision on which contract each owns (e.g. one = min cuts,
  other = count of ways) before shipping both, to avoid a semantic duplicate.
- `stock-cooldown` — needs a decision on which stock-DP variant (cooldown
  length, transaction fee, or both) this contract represents.

### number-theory: what's generated vs. deferred (18 uncurated of 19)

Generated this session (independent oracle, unique exact-match answer):
`catalan-number`, `euler-phi-sieve` (both switched off the old plugin-terminal-state
extractor onto `independent_oracles.py`), `collatz`, `sieve-of-eratosthenes` (both
restored after removal), `modular-exponentiation`, `prime-factorization`,
`number-of-divisors`, `euler-totient`, `miller-rabin`, `lucas-theorem`.

Deferred (8 remaining, all NEEDS_REVIEW/PROPERTY_JUDGE — answer not unique or
contract not yet verified, do NOT force an exact-match oracle):
- `extended-euclidean` — the (x, y) Bézout pair is not unique; needs either a
  property validator (`a*x + b*y == gcd(a,b)` and bounds check) or a precisely
  specified canonical form.
- `chinese-remainder` — needs a decision on non-coprime moduli (generalized
  CRT) and a canonical mod-lcm output range before it can be exact-match.
- `goldbach` — a Goldbach pair (p, q) with p+q=n is not unique in general.
- `pollard-rho` — a nontrivial factor is not unique (could return either
  factor of a composite, or different factors depending on polynomial/seed).
- `primitive-root` — a primitive root mod p is not unique.
- `tonelli-shanks` — a modular square root has two valid roots (±r mod p).
- `baby-step-giant-step` — discrete log solution uniqueness depends on the
  group order; not yet verified to be single-valued for the tested inputs.
- `berlekamp-massey` — the minimal linear recurrence's coefficient
  representation needs its own canonical-form check before trusting exact-match.

## Variant families (new architecture, 2026-07-05 second session)

Every family through dynamic-programming maps AT MOST ONE problem per
canonical algorithm — a hard ceiling of 237 problems even if every algorithm
got covered. Reaching 500 requires multiple distinct problem CONTRACTS per
technique. Three variant families now exist, all following the same
dedup rule: **dedup by the new problem's own slug against the full existing
catalog, not by algorithm_slug** (multiple variant problems legitimately
share one algorithm_slug — e.g. 9 of 11 binary-search-variants problems all
link `algorithm_slug="binary-search"`, which is already curated).

| Family | Problems | origin_type | Notes |
|---|---|---|---|
| `binary_search_variants.py` | 11 | 1 CANONICAL_IMPLEMENTATION (`rotated-binary-search`, real new algorithm coverage) + 10 ALGORITHM_VARIANT | first/last-occurrence, count, insert-position, koko-eating-bananas, ship-packages, integer-sqrt, search-2d-matrix, bitonic-peak (deliberately NOT linked to canonical `peak-element` — that algorithm's real contract allows multiple valid peaks, needs a property validator not built yet; bitonic framing is unique-answer so it's filed as a `binary-search` variant instead, to avoid overclaiming coverage), find-min-rotated |
| `sliding_window_variants.py` | 8 | PATTERN_PROBLEM (`algorithm_slug=None`) | no canonical algorithm backs "sliding window" itself; linking to an unrelated slug would misrepresent coverage |
| `bfs_graph_variants.py` | 7 | 1 CANONICAL_IMPLEMENTATION (`is-bipartite` → `bipartite-check`, promoted out of PROPERTY_JUDGE since its boolean answer IS unique) + 6 ALGORITHM_VARIANT of `bfs` | rotten-oranges, max-distance-to-zero, number-of-islands, shortest-path-binary-matrix, word-ladder-length, minimum-knight-moves |

All 26 passed the full 3-level pipeline (114→204 oracle unit tests across the
session, all with brute-force cross-checks; 26/26 reference submissions
accepted; 26/26 deliberately-wrong submissions rejected via
`scripts/verify_atlascode_family.py <family-name>`).

One real test-weakness caught mid-batch (same class of bug as the DP
rod-cutting incident): `bitonic-peak-index`'s first test data let a `return
len(nums)//2` wrong solution pass because every test array happened to have
its peak near the middle. Fixed by adding a skewed bitonic array
(`[1,9,8,7,6,5,4,3]`, peak at index 1, not index 4) — always add at least one
adversarially-shaped case per problem, don't just add "a couple more" of the
same shape.

**Formal identity model NOT yet built** (deferred): the mega-prompt's
requested `origin_type`/`variant_kind`/`semantic_signature` schema fields are
described here in prose per-family, not yet encoded as structured JSON schema
on every blueprint entry. `generate_atlascode_blueprint.py` still only
derives FULLY_VERIFIED/SEEDED/PLANNED status from real DB+coverage state — it
does not yet compute a semantic signature for automated duplicate detection.
Manual duplicate avoidance this session: checked plugin directories for
already-existing canonical slugs before naming each variant (caught that
`peak-element` and `rotated-binary-search` already existed as separate
canonical algorithms with different contracts than what was first assumed).

## Next batch (in priority order — do NOT restart from scratch, extend `atlascode/families/`)

1. ~~**dynamic-programming**~~ — **18/26 done this session** (see above). The
   remaining 8 need a product decision (ambiguous contract or non-scalar
   output), not more engineering — resolve those decisions before writing
   more DP oracles, don't skip straight past them to a new family.
2. **string** (13 uncurated of 14) — most have simple independent references
   (KMP prefix function, Z-function, edit distance, LCS, palindrome checks);
   follow the number-theory / dynamic-programming pattern (independent oracle
   in `independent_oracles.py` + `families/string.py` + wire into
   `seed_atlas_code.py` and `verify_atlascode_family.py` + run the 3-level
   pipeline before seeding). This is the next recommended batch.
3. **greedy** (9 uncurated of 9) and **divide-and-conquer** (9 uncurated of 9).
4. **cryptography** (10) and **data-structures** (3 remaining after the 3 curated) —
   `NEEDS_REVIEW`, good STANDARD_JUDGE/STRUCTURED_JUDGE candidates but state
   shapes not yet inspected.
5. Resolve the 8 deferred DP contracts (see above) once a property-validator
   or matrix-output comparator exists, or once a product decision is made on
   the ambiguous ones (sequence-alignment, palindrome-partition(ing)).

## Deferred to a property-judge phase (60 algorithms: graph, backtracking, tree, computational-geometry)

Do not force these into exact-match string comparison. Before generating any of
these, build a comparator layer in `submission/evaluator.py` (or a new
`atlascode/comparators.py`) supporting at least:
- `UNORDERED_LINES` / topological-order validity (every required vertex once,
  every edge constraint respected)
- structural validators (N-Queens: N queens, valid rows/cols/diagonals; MST:
  valid spanning tree + optimal weight via a reference oracle)

## Not fixed this session (flagged, not ignored)

- 8 cellular-automata manifests use a pre-schema-v1.0 shape (`slug` not `id`,
  flat `complexity` string). Not fixed because fixing them safely requires a
  `time_best`/`time_worst` breakdown not present in the source files — would be
  fabrication. Irrelevant to AtlasCode (`INTERACTIVE_ONLY`), but affects the
  general Catalog/benchmark pages too.
- 3 data-structures plugins (`b-tree`, `red-black-tree`, `rope`) pass manifest
  validation now but fail at module execution
  (`'NoneType' object has no attribute '__dict__'`) — a loader/plugin bug
  unrelated to AtlasCode, needs its own investigation.
- 2 cross-category slug collisions (`closest-pair`, `monte-carlo-pi`) — the
  registry is a flat slug-keyed dict; only one of the two category listings
  wins. Needs a product decision (rename one, or make the registry key
  `(category, slug)`), not something to silently patch.

## Not yet done (deferred before the catalog-coverage correction, still pending)

- `/problems/{slug}/run` endpoint that evaluates only *visible* test cases and
  does **not** persist a `Submission` or update `UserProgress`/acceptance stats.
  Currently `ProblemPage.tsx`'s "Run" button calls the same `submitSolution()`
  as "Submit", which pollutes stats/progress and evaluates hidden cases on every
  Run click.
- `ProblemPage.tsx`'s language dropdown lists 8 languages regardless of which
  languages a given problem actually has `starter_code` for; selecting one
  without a template silently falls back to the Python starter while Monaco's
  syntax mode changes — should be filtered to `Object.keys(problem.starter_code)`.
- Atlas AI context: no `ProblemContext` exists yet in
  `apps/backend/algorithm_atlas/ai/context_builder.py` /
  `apps/frontend/src/ai/types.ts` / `apps/frontend/src/ai/store.ts`. The
  existing `notebookBridge` pattern in `ai/store.ts` +
  `useAtlasContext.ts` is the template to follow for a `problemBridge`.
- No backend tests for `problems.py` / `submissions.py` / `progress.py`.
- Full backend test suite (`pytest apps/backend/tests -q` and
  `python -m pytest plugins/ -q`) not re-run after this session's manifest
  fixes — should be run before considering this batch fully closed.

## How to resume

```powershell
cd algorithm-atlas
python -m pytest apps/backend/tests/unit/test_independent_oracles.py -q   # Level 1
python scripts/seed_atlas_code.py --validate-only   # discovery + validation, no DB writes
python scripts/seed_atlas_code.py --dry-run          # + shows what would be inserted
python scripts/verify_atlascode_family.py <family>   # Level 2+3 before seeding a new family
python scripts/seed_atlas_code.py                     # actually seed (idempotent)
python scripts/generate_atlascode_blueprint.py        # refresh atlascode_problem_blueprint.json from real DB state
```

Then extend `apps/backend/algorithm_atlas/atlascode/families/` with the next
factory and re-run — the seed script auto-discovers new family modules once
they're imported into `scripts/seed_atlas_code.py`'s `assemble_catalog()`.

**Toward the 500-problem target**: `atlascode_problem_blueprint.json` (repo
root, regenerate via the command above) is the source of truth for progress —
it's built from real DB + coverage state, never hand-typed. As of this
session: 72 seeded (53 FULLY_VERIFIED + 19 SEEDED-not-yet-3-level-verified),
165 PLANNED (real uncovered canonical algorithms), which caps
one-problem-per-algorithm coverage at 237 — **63 short of even the 250
canonical-algorithm ceiling, and 263 short of 500**. Closing the remaining gap
to 500 requires a variant-expansion phase (multiple distinct problem
CONTRACTS per algorithm — e.g. binary-search's ~12 variants described in the
mega-prompt this session) that has not been designed for any family yet. Do
not fabricate blueprint entries for that phase; design and verify each
variant family the same way sorting/searching/number-theory/dynamic-programming
were built, one small batch at a time.
