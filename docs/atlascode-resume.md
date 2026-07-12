# AtlasCode — Session Log (Language Coverage work)

**Read this framing note before the log below**: every "eligible coverage
X%" / "N% of the matrix still open" figure in this file refers to
**Language Coverage** (how many of the 17-language × 2-mode cells are
verified per problem) — it does NOT mean the project or its problems are
X% incomplete. As of 2026-07-12, **all 216 AtlasCode problems are
Problem-Complete** (canonical implementation + working judge + a verified
reference solution for each one); language-coverage work below is ongoing
enhancement on top of an already-complete catalog, not a blocker to it. See
`docs/atlascode-complete-matrix.md` for the current split of both metrics.

## Update 5 — session 2026-07-12 (session close-out: 22-problem set opened for 6 languages)

Started opening mega_batch2.py's 22-problem set (string/multi-array/2D
shapes) for the same 6 newer languages, combined in one script
(`scale_program_mode_mega_batch6_multilang2.py`), continuing the breadth
pattern. Scoped to 4 of the 22 (the str1-shaped, non-DP-table ones:
first-unique-character-index, longest-palindromic-substring,
longest-valid-parentheses, manacher) x 6 languages = 24 cells, all
verified. The harness now supports all 8 shapes (arr1, arr1_int, str1,
str1_int, str2, arr2_samelen, arr2_int, triangle) for go/ruby/kotlin/php/
scala/r -- reuse it directly for the other 18 problems in mega_batch2.py
next session (palindrome-partition/partitioning/subsequence,
restore-ip-addresses-count, longest-repeating-char-replacement,
longest-substring-at-most-k-distinct, longest-common-substring,
minimum-window-substring-length, boolean-parenthesization, matrix-chain-
multiplication, burst-balloons, task-scheduler, coin-change, coin-change-
ways, job-scheduling, meeting-rooms, unbounded-knapsack, triangle-minimum-
path-sum) -- bodies for these are already written in Python/JS/Java/C++/
C#/Perl/C/Rust inside `scale_program_mode_mega_batch2.py`; only need
syntax translation into the same 6 languages, same as this batch.

One more Go bug found: `str1`/`str2` shapes don't use `strconv` (no
integer parsing in their read code), and Go's unused-import rule turns
that into a hard compile error, not a warning -- fixed by making the
`strconv` import conditional on shape in `assemble()`.

**Session totals (start → end)**: 2472 → **3176 verified cells** (+704),
Program Mode 691 → 1395 (+704, Function Mode untouched this session).
Eligible coverage 34.68% → 44.56%. Backend regression stayed clean the
entire session (658 passed / 0 failed / 1 skipped, confirmed after every
batch). Zero corpus weaknesses recorded — every "wrong" variant was
genuinely rejected by the real 40-case corpus before any cell was marked
verified.

**Scripts created this session** (all safe to re-run — idempotent via
`already_verified`, only touch unverified cells):
`scale_program_mode_search_dp_gap.py`, `scale_program_mode_mega_batch1.py`
(36 problems x 8 core langs), `_mega_batch2.py` (22 problems x 8 core
langs), `_mega_batch3_go.py` (36 x go), `_mega_batch4_ruby.py` (36 x
ruby), `_mega_batch5_multilang.py` (36 x kotlin/php/scala/r),
`_mega_batch6_multilang2.py` (4 x go/ruby/kotlin/php/scala/r, extensible
to the other 18).

**One real backend fix landed** (not just script workarounds): `run_r()`
in `apps/backend/algorithm_atlas/api/v1/notebook.py` now uses
`tempfile.TemporaryDirectory(ignore_cleanup_errors=True)` — a genuine
Windows race in R subprocess cleanup was crashing real judge runs, fixed
at the source.

**What's honestly still remaining** (don't understate this): eligible
coverage is 44.56%, so **55% of the full 216x17x2 matrix is still
unverified**. Remaining volume, roughly:
- The other 18 mega_batch2 problems x 6 newer languages (~108 cells,
  harness ready, straight transliteration).
- swift (blocked, toolchain reinstall needed) x everything (216x2 = 432
  cells once/if unblocked).
- The 8 deliberately-deferred core-8 problems (word-wrap needs a real
  oracle, majority-element-ii needs ordering-safe design, 2 tree-shaped
  problems need a new `tree` shape, 4 array-output problems need a new
  return-kind).
- The ~90+ problems that have never been touched by ANY of this session's
  scripts (no Function Mode OR Program Mode beyond Python) — opening a
  brand new problem cluster is real algorithm-design work, not
  transliteration, and is the least-leveraged, highest-effort remaining
  category. Check current exact count via
  `python scripts/generate_honest_matrix_report.py` before picking the
  next cluster, this list drifts.

---

## Update 4 — session 2026-07-12 (breadth push: 6 newer languages, one combined batch)

User feedback mid-session: doing newer languages one-at-a-time (go, then
ruby) was too slow -- explicitly asked for all languages across all
problems, not sequential single-language batches. Response: closed out
Ruby (`mega_batch4_ruby.py`, 36/36 problems, uses Ruby's native arbitrary-
precision integers so none of the overflow classes below applied), then
built `scale_program_mode_mega_batch5_multilang.py` covering **four
languages in one script** (kotlin, php, scala, r) x the same 36 problems =
144 cells, matching mega_batch1/2's original breadth-first pattern instead
of one-language-per-file. All 6 working newer languages (go, ruby, kotlin,
php, scala, r) are now fully ported for this 36-problem set; swift remains
blocked (toolchain missing from disk, unchanged).

Result: **Ruby 36/36 + {kotlin,php,scala,r} 144/144 = 180 new cells, 0
ultimately unresolved**. Totals now: **3152 verified** (Function 1781,
Program 1371), eligible coverage 44.22%. Backend regression: 658/0/1 clean.

**Real bugs found closing this batch** (on top of the classes already
documented below):
1. **R prints large numbers in scientific notation by default** (`cat(1e7,
   "\n")` → `"1e+07"`, not `"10000000"`) -- silently wrong output for any
   problem whose answer gets large enough, with no error/crash to flag it.
   Fixed globally in the harness with `options(scipen = 999)` at the top
   of every generated R program, not per-problem.
2. **R's `queue <- queue[-1]` (pop-front) and `c(vec, x)` (append) are both
   O(n) per call** -- a BFS (minimum-knight-moves) that's O(n) in every
   other language became O(n^2) in R and hit the judge's time limit on the
   larger test cases. Fixed by pre-allocating fixed-size integer vectors
   sized from the actual search bound (`side = 2*(max(|x|,|y|)+4)+1`) and
   using integer head/tail indices instead of list mutation -- and went
   one step further, replacing the `visited` environment-based hashmap
   (string-keyed `assign`/`exists`, real but still slow per-call in R)
   with a plain pre-allocated logical matrix indexed directly by
   coordinate, which is what actually got it under the time limit.
3. **Backend bug, not a per-problem bug**: `run_r()` in
   `apps/backend/algorithm_atlas/api/v1/notebook.py` intermittently (but
   reproducibly for longer-running R scripts) crashed the whole judge
   process with `PermissionError: [WinError 32] The process cannot access
   the file... main.r` when `tempfile.TemporaryDirectory()`'s cleanup ran
   immediately after `_run_subprocess` reported the Rscript process had
   exited -- Windows hadn't actually released the file handle yet. Root
   cause is a Windows-specific race, not something a retry-in-the-script
   layer should paper over. Fixed at the source: added
   `ignore_cleanup_errors=True` to the `TemporaryDirectory()` call (stdlib
   parameter for exactly this scenario, Python 3.10+) so a failed cleanup
   no longer crashes real judge traffic -- the run's result is already
   captured before cleanup runs, so a rare leaked temp dir (which Windows
   reclaims on its own) is a fully acceptable trade-off. This was a live
   backend fix, not a scale-script workaround -- verify it's still in
   place if `run_r` is ever refactored.

**Pattern for the next language** (any of the 6 already-working ones, for
a NEW problem set beyond these 36): same shape harness, but budget real
time for language-specific perf/precision quirks on non-trivial
algorithms (BFS, big-number modular arithmetic) -- R needed 3 fixes here
that no other language needed at all. Always run the FULL 40-case corpus,
never just the 6-8 case smoke subset, before trusting a "done" batch --
two of R's three bugs here only showed up on cases beyond the smoke
subset (the scientific-notation one on a specific large-value case, the
performance one only on the largest coordinate cases).

---

## Update 3 — session 2026-07-12 (Go language expansion)

Ported all 36 mega_batch1.py problems to Go (`scripts/scale_program_mode_mega_batch3_go.py`)
— chosen first among the 6 working newer languages because its 5 shapes
(arr1/arr1_int/int1/int2/int3) are the simplest and I already had every
algorithm proven correct in 8 other languages, so this was pure syntax
translation with zero new algorithm-design risk. Result: **36/36 verified
on the first full-corpus run after a clean smoke test** (0 bugs found this
time — the harness pattern + reusing already-debugged algorithms is
paying off). Go is strict about unused imports (compile error), so the
harness fixes the import list to `{fmt, io, os, strconv, strings}` and
every body avoids the `sort`/`math` packages in favor of manual loops
(same style as the C bodies).

Totals now: **2972 verified** (Function 1781, Program 1191), eligible
coverage 41.69%. Backend regression: 658 passed / 0 failed / 1 skipped.

**Next**: same 36-problem set (or the batch2 22-problem set) ported to
another working newer language — ruby, kotlin, php, scala, or r all
confirmed usable this session (source `scripts/toolchain_path.sh`-style
PATH prefix per command, see [[project_atlascode_toolchain_env]]). Each
new language is its own `scale_program_mode_mega_batchN_<lang>.py` file
following the exact same pattern as batch3_go: define sig/read_code/
call_args/print_stmt per shape, reuse the proven algorithm logic, smoke
test on 6-8 cases before the full 40-case run.

---

## Update 2 — session 2026-07-12 (continued, mega-batch push)

User explicitly directed: stop doing small 3-problem batches, do large batches
(35+ problems each) and keep chaining them without stopping. Built a
shape-based code-generation harness (`scripts/scale_program_mode_mega_batch1.py`
and `..._mega_batch2.py`) so only the core algorithm per (problem, language)
needs to be hand-written -- the read/print/wrong-variant boilerplate is
generated from one of ~11 I/O shapes (arr1, arr1_int, int1/2/3, str1,
str1_int, str2, arr2_samelen, arr2_int, triangle).

- **mega_batch1.py**: 36 problems x 8 core languages (javascript, typescript,
  java, cpp, csharp, perl, c, rust) = 288/288 cells verified.
- **mega_batch2.py**: 22 more problems (string-shaped, multi-array, 2D
  triangle) x same 8 languages = 176/176 cells verified.
- Combined: **+464 Level-6 Program Mode cells this push**, zero corpus
  weaknesses. Totals now: **2936 verified** (Function 1781, Program 1155),
  eligible coverage 41.19% (up from 34.68%).
- Full backend regression: **658 passed / 0 failed / 1 skipped** (clean,
  even the previously-flaky-under-load Scala test passed).

**Real bugs found and fixed while scaling** (evidence this wasn't
rubber-stamped):
1. Perl's `^` XOR on values fresh from `split()` does STRING xor unless
   coerced numeric (`0+$x`) -- same class of bug the resume notes below
   already flagged for a different operator; hit again on
   maximum-xor-of-two-numbers.
2. JS/TS `number` (double) loses precision above 2^53 -- both
   modular-exponentiation (base*base intermediate) and lucas-theorem
   needed exact arithmetic. modular-exponentiation: fixed with BigInt.
   lucas-theorem: the deeper issue was the algorithm itself, not just JS --
   computing raw C(n,k) via the multiplicative formula produces
   astronomically large intermediates (C(96,48) has 28 digits) that
   overflow EVERY fixed-width type including 64-bit `long`/`long long`/i64,
   not just JS numbers. Fixed by rewriting smallC to compute the binomial
   coefficient mod p directly (factorial mod p + modular inverse via
   Fermat's little theorem, base^(p-2) mod p) so intermediates never exceed
   p -- ported this corrected algorithm to all 8 languages via
   `LUCAS_PRELUDE`.
3. C's `minimum-knight-moves` used a hardcoded 41x41 visited grid assuming
   coordinates near the origin -- real corpus has coordinates up to ±300,
   silently corrupting memory / producing wrong answers via out-of-bounds
   array access (undefined behavior, no crash). Fixed by sizing the grid
   dynamically from the actual target coordinates (malloc'd, `bound =
   max(|x|,|y|)+4`).
4. Perl's `arr2_samelen`/`arr2_int` shape (job-scheduling, meeting-rooms,
   unbounded-knapsack) originally named the sub's array params `$a`/`$b` --
   these collide with Perl's sort()-block special variables, silently
   breaking any `sort { $a <=> $b }` inside the body (or inside a caller
   using them elsewhere). Renamed the shape's Perl params to
   `$arrA`/`$arrB`; sort blocks now work correctly.
5. Java's Scanner `.next()` throws `NoSuchElementException` on empty input
   (str1 shape) -- real corpus has empty-string test cases. Fixed with
   `sc.hasNext() ? sc.next() : ""`. Same empty-input class of bug as the
   `Scanner.nextLine()` fix from the prior session, different method.
6. C's `scanf("%s", s)` leaves the buffer **uninitialized** (garbage) when
   stdin has no token to read (empty-string input) -- `malloc` doesn't
   zero, so `strlen()` on the garbage buffer returns an arbitrary length.
   Fixed by switching to `calloc` for every C str1/str2 buffer.
7. Java needed `throws Exception` on `main` once `BufferedReader.readLine()`
   was introduced for str1_int/str2 shapes (checked `IOException`).

**Batch-writing pattern that worked well this session** (reuse for future
batches): define I/O shapes once (sig/read_code/call_args/print_stmt keyed
by shape+language), then only write the ~5-15 line algorithm body per
(problem, language) -- the harness supplies boilerplate + the generic
"wrong" variant (`result+1` for int, `!result` for bool) automatically, so
correctness bugs are isolated to the body and caught immediately by
smoke-testing on a 6-8 case subset before spending time on the full 40-case
run.

**What's left in the "core-8 Function-Mode-full, Program-Mode-empty" pool**:
now down to 8 problems, all deliberately deferred as genuinely harder:
`word-wrap` (tried to reverse-engineer the DP cost formula from test cases
twice, couldn't match the expected outputs -- needs a real oracle, not a
guess), `majority-element-ii` (Boyer-Moore n/3 candidates, output ordering
ambiguity risk), `construct-tree-preorder-inorder` + `max-depth-binary-tree`
(genuine `tree` contract type, needs a new shape), `merge-sorted-arrays-
inplace` + `merge-two-sorted-lists` + `remove-nth-from-end` +
`reverse-linked-list` (array-output return kind not yet built into the
harness -- these are NOT real linked-list types despite the names, just
plain int-array params/returns, so they're tractable, just need an "array"
print/wrong-variant kind added to the shape system).

**Next highest-leverage work**: port the now-58-strong core-8 Program Mode
set to the newer 7 languages (go, kotlin, ruby, php, r, scala all confirmed
usable this session via the PATH prefix; swift still broken, see
[[project_atlascode_toolchain_env]]) -- same shapes, same proven algorithm
bodies, just new per-language sig/read_code/call_args/print_stmt harness
entries. That's a ~350-cell pool (58 problems x 6 languages) using
infrastructure that already exists, versus opening entirely new problem
clusters which requires fresh algorithm design AND fresh corpus risk.

---

## Update — session 2026-07-12

Continued from the 2026-07-07 checkpoint below (which was itself already
superseded by an intermediate session that pushed totals to 2448 verified
Level-6 cells / 0 stale by the time this session started — confirmed live
via `check_ledger_staleness.py`, don't trust the "1,466" figure below, it's
stale). This session closed one more Program Mode gap:
`scripts/scale_program_mode_search_dp_gap.py` (new file) ports
`staircase`, `search-insert-position`, `rotated-binary-search` — all
already Level-6 Function Mode across the 8 core languages — to Program
Mode for the same 8 languages (javascript, typescript, java, cpp, csharp,
perl, c, rust). All 24 cells verified real-corpus-pass + wrong-rejected on
first run. Totals now: **2472 Level-6 cells** (Function 1781, Program
691), eligible coverage 34.68%. Full backend regression: 657 passed / 1
flaky-under-load Scala test (passes standalone) / 1 skipped — net
improvement over the previous 633/25/1 baseline now that the toolchain
PATH workaround (source the SDK paths per-command, see
[[project_atlascode_toolchain_env]]) is confirmed still working and all 7
newer-language toolchains are live in this environment (0 stale cells).

Next batch: same pattern, pick more of the ~69 problems that are
Function-Mode-full across the 8 core languages but Program-Mode-empty
(query in the resume doc's section 5 pattern still applies) — full current
list obtainable via a ledger query joining problem_id/mode/language.
Remaining volume is still large (eligible cells minus 2472 verified); this
is genuinely multi-session work, not something finishable in one sitting.

---

# AtlasCode Dual-Matrix — Resume Point (session 2026-07-07, mega-prompt continuation)

For the full mission framing see the mega-prompt in this session's transcript.
This file is the short version for picking up cold in a new session.

## 1. Where are we?

Continuing the AtlasCode dual-mode (Function + Program) coverage matrix
across 216 problems × 17 languages. Did NOT restart the project. This
session: audited repo truth (found stale report generators + an
environment PATH regression), closed Python Function Mode to 216/216,
then scaled Function Mode AND Program Mode together across the 8
languages that work in this sandbox (javascript, typescript, java, cpp,
csharp, perl, c, rust), problem-family by problem-family.

## 2. What is verified right now (re-run before trusting)?

```powershell
python scripts/check_ledger_staleness.py       # honest current-vs-stale breakdown
python scripts/generate_honest_matrix_report.py  # regenerates docs/atlascode-complete-matrix.json/.md
```

As of last checkpoint this session:
- **1,466 total Level-6 ledger rows** (879 Function Mode + 587 Program
  Mode), up from 293 at session start.
- **1,405 currently reproducible** in this environment; **61 stale**
  (go/kotlin/ruby/php/r/scala/swift -- see item 4 below, unchanged all session).
- Function Mode coverage per working language: ~121-122/216 problems
  (javascript/typescript/java/cpp/csharp/perl/rust; c is 118/216 --
  trapping-rain-water and reverse-bits are genuinely excluded for c/cpp/
  java/csharp/rust, see item on numeric gaps below).
- **Program Mode gap closed for the 3 clusters Function Mode had already
  covered but Program Mode hadn't**: bit-misc (9 problems x 8 languages,
  72/72), array-cluster3 (9 problems, 75/75 -- trapping-rain-water limited
  to js/ts/perl per the numeric gap), hashmap-grid (10 problems, 80/80).
  Program Mode is now at ~74-75/216 per working language, much closer to
  Function Mode's ~121-122/216. Remaining Program Mode gap: the languages
  are now roughly in sync per-cluster: whatever Function Mode has covered
  for a cluster, Program Mode now has too, for all clusters scaled this
  session. The next volume of work is opening NEW clusters (both modes
  together) for the ~90+ problems neither mode covers yet beyond Python.
- **Real bugs found + fixed while closing this Program Mode gap** (on top
  of the ones already listed below): Perl's `^` bitwise operator does
  STRING (byte-wise) xor on operands that were never coerced to numeric
  context -- hamming-distance's Program Mode wrapper needed `$x = $x + 0;`
  before XOR-ing, since values straight from `split()` are plain strings.
  C#'s `out` is a reserved keyword -- flood-fill's Program Mode wrapper
  used it as a local variable name (`int[][] out = ...`), a real
  Compilation Error (CS1001), fixed by renaming to `resultGrid`. Java's
  `Scanner.nextLine()` throws `NoSuchElementException` (not an empty
  string) when the stream is fully exhausted with zero bytes left --
  group-anagrams-count's last test string was sometimes an empty string
  with no trailing content, fixed with `sc.hasNextLine() ? sc.nextLine() :
  ""`. A THIRD real C buffer overflow (same class as kmp/lcs from earlier
  this session): longest-substring-without-repeating's real corpus has
  strings up to 46,429 chars but the Program Mode wrapper used
  `char s[10001]`, bumped to `char s[65537]`.
- Python Function Mode: **216/216**, 0 failures, 0 skips (closed this
  session -- the 23 previously-skipped problems all had real independent
  oracles sitting unwired in `legacy_audit_oracles.py`/`searching.py`;
  wired them in via `scripts/verify_python_legacy_search_function_mode.py`).
- 47 problems now share Level-6 Function Mode coverage across all 8
  working languages (sort-family x21, search-family x7, ladder-gap x7,
  gcd-euclidean, house-robber, word-break, LIS, LCS, edit-distance,
  minimum-path-sum, n-queens, graph-bfs, dijkstra-shortest-path,
  kmp-string-matching).
- Program Mode: same problem set now has real starter code (saved into
  `problems.starter_code`) + real judge verification across all 8 working
  languages -- previously 0% for every non-Python language, now genuinely
  covered for these 47/216 problems (except Function-mode-only min-stack-
  simulation gap for C, a permanent tuple-support gap, not a to-do).
- Full backend regression: **633 passed / 25 pre-existing failures / 1
  skipped**, unchanged and reconfirmed after every single batch this
  session (never regressed).

## 3. What is NOT done (be honest with the user)

- **~90+ problems** still have zero Function/Program Mode coverage beyond
  Python for the 8 working languages -- this is the main remaining volume
  of work. Cluster-by-cluster scaling (see scripts named `scale_*.py` /
  `scale_program_mode_*.py` in `scripts/`) is the proven, working pattern:
  pick a handful of problems, write real per-language reference + wrong
  solutions, smoke-test on a small case subset FIRST, then run the full
  40-case corpus, record only genuine passes to the ledger. Remaining
  problems include (non-exhaustive, captured mid-session):
  activity-selection, binary-tree-max-path-sum, closest-pair, coin-change,
  collatz, counting-inversions, distinct-subsequences, egg-drop,
  euler-totient, fractional-knapsack, gas-station, insert-interval,
  is-balanced-binary-tree, is-bipartite, is-valid-bst, job-scheduling,
  knapsack-01, kth-largest-element, largest-rectangle-in-histogram,
  level-order-traversal, linked-list-cycle-detect,
  longest-palindromic-substring, lowest-common-ancestor-binary-tree,
  manacher, matrix-chain-multiplication, median-of-two-sorted-arrays,
  meeting-rooms, merge-two-sorted-lists, middle-of-linked-list,
  number-of-divisors, palindrome-linked-list, partition-equal-subset-sum,
  path-sum-exists, perfect-squares-min-count, regular-expression-matching,
  remove-nth-from-end, reverse-linked-list, right-side-view,
  rotate-image-90, same-tree, search-2d-matrix, set-matrix-zeroes,
  sliding-window-maximum, spiral-matrix-traversal, staircase, subset-sum,
  task-scheduler, unbounded-knapsack, wildcard-matching,
  word-ladder-length, word-search-grid, and more -- verify the exact
  remaining set via a DB query before picking the next cluster, don't
  trust this list blindly since it may drift.
  min-stack-simulation Program Mode is still 0/17 languages -- flagged for
  dedicated future work due to tuple-typed ops array complexity.
- **7 languages (go, kotlin, ruby, php, r, scala) are blocked purely by a
  stale-PATH issue in this session's shell** -- the toolchains are
  genuinely installed (portable SDKs under `C:\Users\poorn\*-sdk\`) and
  already in the permanent User PATH registry value, but this session's
  shell processes were spawned before that update took effect. **A fresh
  terminal/session should immediately unblock all 6** -- re-run
  `python scripts/check_ledger_staleness.py` after restarting to confirm.
- **Swift is separately blocked**: the toolchain is genuinely gone from
  disk (no `swift-sdk` directory anywhere, no Program Files\Swift), not
  just a PATH issue. Needs an actual reinstall decision from the user.
- **10 problems are architecturally blocked for every non-Python language**
  until a real arbitrary-precision numeric type is added to the Function
  Mode contract system: fibonacci-dp, karatsuba, catalan-number,
  fast-power, decode-ways, unique-paths, combination-sum-iv-count,
  evaluate-reverse-polish-notation, maximum-product-subarray,
  sum-root-to-leaf-numbers. See `docs/atlascode-bigint-numeric-audit.json`.
  Do NOT attempt naive fixed-width-int solutions for these -- they will
  correctly fail on the large-value stress cases already in the corpus.
- **min-stack-simulation is permanently unsupported for C** (no tuple
  type) -- see `docs/atlascode-tuple-capability-matrix.json`. Also
  unsupported for Go and Swift once those come back online.
- **Hidden-test secrecy has not been explicitly re-audited this session**
  (inherited from prior sessions' work, not re-verified).
- **Shell Program Mode coverage has not been touched this session** --
  Shell is Program-Mode-only by design; its actual starter/execution
  coverage status wasn't re-checked.

## 4. Toolchain unblock (resolved this session, no restart needed)

**go/kotlin/ruby/php/r/scala are now genuinely usable in THIS session**,
without a terminal restart. Confirmed two ways: (1) `check_ledger_staleness.py`
now reports 0 stale cells for all 6 (up from a shallow probe that used to
under-detect them), and (2) directly re-verified with a real
`evaluate_function()` compile+run call per language (not just a version
check) on gcd-euclidean -- all 5/5 cases Accepted for go, kotlin, ruby, php,
scala (r confirmed separately, 5/5 Accepted too).

**The trick**: this session's Bash tool shell process has a stale `PATH`
env var (it was spawned before the toolchains' directories were added to
the persistent Windows User PATH registry value) -- but env var changes
don't propagate to an already-running process, and each new Bash tool
invocation inherits that SAME stale parent environment (confirmed: `export
PATH=...` in one command has zero effect on the next command). The fix
that works within this constraint: prefix any command that needs these
toolchains with `source scripts/toolchain_path.sh &&` (a small script
this session created that appends all 6 SDK directories, plus Swift's, to
PATH). This must be done PER COMMAND -- it does not persist. Any future
`scale_*.py` script targeting these languages must have this sourced
before the `python scripts/scale_*.py` invocation in the same Bash call.

**Swift is a real, separate, NOT-yet-resolved blocker** -- do not assume
it works. `swift --version` succeeds (the binary launches), but actual
compilation fails: `error: unable to load standard library for target
'x86_64-unknown-windows-msvc'`. Tried and failed to fix within this
session: (a) plain PATH extension -- fails, (b) setting `SDKROOT` to the
Windows Kits 10 SDK path -- fails with the identical error. This is a
genuine Swift-on-Windows toolchain/linker configuration problem (likely
needs `vcvarsall.bat`/MSVC environment variables -- `LIB`/`INCLUDE` --
which a plain PATH addition does not provide, or a different Swift
install method entirely), not something fixable by continuing to poke at
PATH. Do not mark Swift as unblocked without a fresh, direct
`evaluate_function()` test proving a real compile+run succeeds -- the
ledger's existing 8-cell Swift ladder and the staleness checker's "current"
verdict for Swift turned out to be a false positive this session (the
staleness probe is shallower than an actual compile).

## 5. What pattern to follow for the next batch (proven this session)

1. Pick 1-5 problems not yet covered for the 8 working languages (check
   via a quick DB query: `SELECT problem_id FROM atlascode_matrix_ledger
   WHERE language='javascript' AND mode='function'` vs the full 216).
2. Read each problem's REAL `function_contract` (parameter names/order/
   types) via `FunctionContract.from_dict` + call `adapter.generate_starter()`
   for every target language to get exact signatures -- never guess types,
   especially for C (`AtlasIntArray`/`AtlasIntMatrix`/`AtlasIntCube`/
   `AtlasStringArray` field names: `.data`/`.size`, confirmed this session).
3. Write correct + a genuinely-wrong (off-by-one, negation, or descending-
   sort style) implementation per language.
4. **Smoke-test on a 4-6 case subset FIRST** before running the full
   40-case corpus across all languages -- this session caught several real
   bugs cheaply this way (a two-sum duplicate-key ordering bug, a JS/TS
   empty-tree-input parsing bug, a C fixed-buffer overflow on a 16KB test
   string) instead of burning a full run to discover them.
5. Only record Level 6 in the ledger when correct-all-pass AND
   wrong-is-genuinely-rejected on the REAL 40-case corpus (or 12 for
   n-queens).
6. For Program Mode: read the EXISTING Python `starter_code` for that
   problem directly (it defines the real stdin/stdout contract already
   used to generate `test_cases.input_data`/`expected_output`) -- reuse the
   SAME parsing convention in the new language, never invent a new format.
7. Run full backend regression (`pytest apps/backend/tests -q`) after each
   batch -- expect exactly 633 passed / 25 failed / 1 skipped unless you've
   fixed the PATH issue (in which case failures should drop).
8. Regenerate `docs/atlascode-complete-matrix.json` after significant
   batches via `python scripts/generate_honest_matrix_report.py`.

## 6. What must never be regenerated / reverted

- Everything from prior sessions' equivalent sections (independent
  oracles, tree serialization format, `\r\n` normalization, temp-file
  execution fixes, `engine.dispose()` calls) -- unchanged, still applies.
- The two-sum "first-index-wins" fix (`if (!(nums[i] in seen)) seen[...] = i`)
  in every language's two-sum implementation -- reverting to unconditional
  overwrite reopens a real duplicate-value ordering bug.
- The C buffer sizes for kmp-string-matching (`char T[65537], P[65537]`)
  and longest-common-subsequence (`char s1[4001], s2[4001]`) -- shrinking
  these reopens a real stack-buffer-overflow-on-long-input bug found this
  session (corpus has lines up to 16,200 chars).
- `docs/atlascode-complete-matrix.json`/`.md` should always be regenerated
  from `scripts/generate_honest_matrix_report.py`, never hand-edited --
  the OLD `scripts/generate_final_matrix_report.py` was confirmed this
  session to contain stale hardcoded per-language strings; don't trust it.

## 7. Known systemic non-issues (checked, not bugs)

- Comparator consistency: structurally guaranteed by one shared
  `contracts.compare_typed` function every language's result flows
  through -- no per-language comparator drift possible.
- Tuple capability: 13/17 languages support tuples (verified via
  min-stack-simulation), C/Go/Swift honestly don't (raise ValueError),
  Kotlin/Scala support 2-element only -- see
  `docs/atlascode-tuple-capability-matrix.json`.
- Tree semantics: same canonical level-order-with-null format proven
  across 12+ languages via max-depth-binary-tree +
  construct-tree-preorder-inorder.
- Compile-once behavior: confirmed structurally in `runner.py` (one
  `preparer()` call outside the per-case loop) for all 9 compiled
  languages -- not per-case recompilation.
