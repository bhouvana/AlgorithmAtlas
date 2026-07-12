# AtlasCode — Dual-Mode Run Architecture (Function Mode + Program Mode)

Companion to `docs/atlascode-judge-workspace.md` (which covers the Run/Submit
split and the single-language-agnostic evaluator). This doc covers the second
Run contract added on top of that: **Function Mode**.

Scope reminder: this is a **Run-only** feature. Submit (`api/v1/submissions.py`,
`submission/evaluator.py`) was not modified in any way and has no concept of
execution mode.

## The two contracts

**Program Mode** (existing, unchanged): the user writes a complete program.
It reads from stdin, writes to stdout. The judge pipes raw stdin in and
string-compares stdout. This is the only mode all ~216 problems and all 17
judge languages support.

**Function Mode** (new): the user writes only the requested function. The
judge:
1. loads the problem's typed arguments for a test case
2. generates a small driver and appends it to the user's code
3. runs the composed program (through the exact same subprocess
   infrastructure Program Mode uses)
4. parses the function's typed return value out of stdout
5. compares it to the typed expected value

These are genuinely different execution paths at every layer — not a
cosmetic toggle over the same backend logic. The Run endpoint dispatches to
`_run_program_mode` or `_run_function_mode` based on `RunRequest.execution_mode`.

## Why this was safe to build without new sandboxing work

Python has no `PREPARER` (no compile step) in `notebook.py`'s language
registry, so both `submission/evaluator.py.evaluate()` and
`function_mode/runner.py.evaluate_function()` spawn a **brand-new
`python -c <source>` OS subprocess for every single test case**. That gives
Function Mode, for free, from the existing Program Mode infrastructure:

- **Mutation isolation**: if a user's function does `nums.sort()` on its
  input, that mutation dies with the subprocess. The next case gets a fresh
  process with its own freshly-embedded arguments. Verified in
  `tests/test_atlascode_function_mode.py::test_argument_mutation_does_not_corrupt_later_cases`.
- **Timeout safety**: an infinite loop hits the same per-case subprocess
  timeout (`_TEST_TIMEOUT`, imported from `submission/evaluator.py` rather
  than re-declared) and is killed the same way Program Mode already kills a
  hanging program. Verified in `test_infinite_loop_times_out_safely`.

A future compiled-language Function Mode adapter (Java, C++, ...) would need
its own compile-once strategy and would have to re-examine this — flagged as
a real gap, not silently assumed to carry over.

## Function contract schema

`Problem.function_contract` (nullable JSON column). `None` = Program Mode
only for this problem.

```json
{
  "function_name": "top_k_frequent",
  "parameters": [
    { "name": "nums", "type": { "kind": "array", "items": { "kind": "integer" } } },
    { "name": "k", "type": { "kind": "integer" } }
  ],
  "return_type": { "kind": "array", "items": { "kind": "integer" } }
}
```

Defined in `atlascode/function_mode/contracts.py` as `FunctionContract` /
`Parameter` / `TypeSpec` dataclasses with `.to_dict()`/`.from_dict()`.

## Bounded type system

Implemented kinds (only what the migrated batch actually needs — see Phase 4
"don't overengineer speculative types"):

| kind | meaning |
|---|---|
| `integer` | Python `int`, excludes `bool` |
| `float` | compared with `1e-6` tolerance |
| `boolean` | Python `bool` |
| `string` | Python `str` |
| `array` | `list[T]`, requires `items` |
| `optional` | `T \| None`, requires `items` |

There is no separate `matrix` kind — a matrix is `array<array<integer>>`,
the same structural information without a duplicate representation.

`validate_value`/`validate_arguments` (structural type-check, used to reject
malformed custom cases **before** execution) and `compare_typed` (semantic
comparison — arrays are never silently sorted; order only doesn't matter if
a future problem's contract explicitly says so, which none currently do)
live in the same module.

## Canonical testcase capture — no second test corpus

The existing 40-test-per-problem pipeline (`atlascode/testgen.py`,
`build_forty()`) already computes, per case, a typed argument tuple (`args`)
and the oracle's raw return value (`answer`) — it just stringifies both into
`input_data`/`expected_output` and discards the typed values. `TestSpec`
gained one new optional field, `function_arg_names: list[str] | None`; when
set, `build_forty()` also stashes `function_args = dict(zip(names, args))`
and `function_expected = answer` on the same row. Same case, same RNG draw,
two representations — never a second, independently-generated set of tests.

## Language adapter architecture

`atlascode/function_mode/adapters.py` defines the `FunctionModeAdapter`
protocol (`generate_starter(contract)`, `compose_source(user_code, contract,
arguments)`). Only `PythonFunctionAdapter` exists; `registry.py`'s
`ADAPTERS` dict is the single, honest source of truth for which languages
support Function Mode (`get_adapter(lang)` returns `None` for anything else,
and the Run endpoint returns a 422 rather than silently falling back to
Program Mode).

### Driver protocol (Python)

The composed source is: `<user code>` + a driver block that

1. looks up the required function by name (`globals().get(name)`) — missing
   → a `@@ATLASCODE_CONTRACT_ERROR@@{"reason": "missing_function", ...}`
   stdout sentinel line, never a generic failure
2. binds the canonical arguments to the function's real signature via
   `inspect.signature(fn).bind(**args)` — a `TypeError` here (wrong
   parameter names/arity — e.g. the user changed the signature) is also a
   structural Contract Error, distinguished from a `TypeError` raised
   *inside* a correctly-shaped call, which is a genuine bug and must surface
   as a real `Runtime Error`
3. calls the function with **no try/except around the call itself** — an
   uncaught exception exits nonzero and is picked up by the existing
   Runtime Error detection Program Mode already has (`exit_code not in (0,
   None)`)
4. serializes the return value as JSON behind a
   `@@ATLASCODE_RESULT@@<json>` sentinel line

Driver generation uses `%`-style string templating, not f-strings/`.format`,
specifically because the generated target code is full of literal
`{`/`}` dict syntax — `%`-substitution is the only formatting mechanism that
doesn't also use braces, so there's no risk of a brace-escaping mistake
silently corrupting the driver.

**Sentinel parsing takes the LAST matching line**, not the first — a user's
own `print()` debugging statements inside their function are tolerated and
never confused with the driver's own output (verified in the adapter's
manual smoke test during development; the "noisy debug print" scenario).

The hidden driver source is **never sent to the frontend** — only the
parsed, typed result.

## Run request/response shape

```jsonc
POST /api/v1/problems/{slug}/run
{
  "language": "python",
  "code": "...",
  "mode": "visible" | "selected" | "custom",
  "execution_mode": "function" | "program",   // defaults to "program"
  "case_indices": [0, 1],                      // mode == "selected"
  "custom_cases": [                            // mode == "custom"
    // Program Mode shape:
    { "input_data": "...", "expected_output": "..." },
    // Function Mode shape:
    { "arguments": { "nums": [1,2,3], "k": 2 }, "expected_return": [1,2], "has_expected_return": true }
  ]
}
```

`RunCaseResult` carries both the legacy `input_data`/`expected_output`/
`actual_output` string fields (JSON-stringified in Function Mode, for any
caller that only reads the old shape) **and** typed `arguments` /
`expected_return` / `actual_return` / `contract_error` fields the frontend
actually renders from in Function Mode. `RunResult.execution_mode` tells the
frontend which shape it's looking at.

Custom Function Mode cases are validated against the contract
(`validate_arguments`) and rejected with **400 before execution** if
malformed — never run with wrong argument names/types (Phase 14).

## Frontend

- **Toggle**: `[ Function | Program ]` segmented control in the editor
  toolbar (`ProblemPage.tsx`'s `ModeToggle`), disabled + tooltip-explained
  (not hidden) when the current problem/language pair has no
  `function_contract`/`starter_code_function` entry.
- **Draft identity**: `problemId:language:mode` (`atlasCodeStore.ts`'s
  `draftsByKey`). Every keystroke mirrors into this map immediately (not
  only at switch-time), so a Reset can't be silently undone by switching
  mode and back. Persisted to localStorage alongside custom scratch cases.
- **Default mode resolution**: last mode used for *this* problem
  (`lastModeByProblem`, persisted) → Program Mode. A problem is never
  defaulted into Function Mode on first visit even if supported — Program
  Mode users are never surprised by a silent mode switch.
- **Testcase tab**: Function Mode shows Arguments/Expected Return (JSON) for
  visible cases and a JSON-textarea editor (client-side JSON-parse validated
  before the Run button is even enabled) for custom cases, instead of raw
  stdin/stdout text areas.
- **Result tab**: Function Mode cases render "Arguments"/"Expected
  Return"/"Actual Return", never "stdin"/"stdout" — the UI language always
  matches the contract actually being judged (Phase 16). `Function Contract
  Error` gets its own status color, distinct from Wrong Answer/Runtime Error.
- **Atlas AI bridge**: `ProblemContext` carries `executionMode` +
  `functionSignature` (e.g. `"top_k_frequent(nums, k)"`), so Atlas AI never
  suggests reading `sys.stdin` while the user is in Function Mode.

## Support matrix (as of this session)

| | Function Mode | Program Mode |
|---|---|---|
| `contains-duplicate-within-k` | ✅ (python) | ✅ (all 17 langs registry-wide, python seeded) |
| `product-of-array-except-self` | ✅ (python) | ✅ |
| `subarray-sum-equals-k` | ✅ (python) | ✅ |
| `top-k-frequent-elements` | ✅ (python) | ✅ |
| `longest-consecutive-sequence` | ✅ (python) | ✅ |
| `two-sum-count-pairs` | ✅ (python) | ✅ |
| everything else (~209 problems) | ❌ (`function_contract IS NULL`) | ✅ |

Non-Python Function Mode support: 0 languages. Extending it means writing a
new `FunctionModeAdapter` and registering it in `registry.py` — Program Mode
support for that language is completely unaffected either way.

## Migrating another problem to Function Mode

Sequential, per Phase 24's anti-hallucination rules — never in bulk without
verification:

1. Inspect the problem's real starter code to get the EXACT existing
   function name/parameter names (Function Mode must teach the same
   signature Program Mode's starter already uses).
2. Add a `function_contract=FunctionContract(...)` to the family's `_Spec`
   entry, using the bounded `TypeSpec` kinds above.
3. Pass `function_arg_names=contract.parameter_names` into that family's
   `tg.TestSpec(...)` construction.
4. For an **already-seeded** problem: run (or extend)
   `scripts/backfill_function_mode.py`, which regenerates the family's cases
   with the SAME `tg.problem_rng(slug)` seed, verifies every regenerated
   case is byte-identical to what's already in the DB (by `order`), and only
   then writes the new columns — aborting loudly on any mismatch instead of
   silently attaching a wrong argument to an existing hidden test.
5. For a **new** problem: `seed_atlas_code.py` picks up the contract
   automatically (`build_*_problems` already emits `function_contract`/
   `starter_code_function` when the spec has one).
6. Add contract-specific tests (see `test_atlascode_function_mode.py` for
   the pattern: good/wrong/missing-function/wrong-signature/runtime-error/
   timeout/mutation/custom-case-validation).

## Known limitations (honest, not silently deferred)

- Only Python has a Function Mode adapter. The other 16 judge languages are
  Program Mode only.
- Only 6 of ~216 problems have a `function_contract`. Everything else is
  Program Mode only.
- No `matrix`/`linked_list`/`binary_tree`/graph structured types exist yet —
  none of the migrated problems need them. Adding one means extending
  `TypeSpec`'s `kind` union and `PythonFunctionAdapter`'s (de)serialization,
  not a blanket redesign.
- Function Mode custom-case input is a raw JSON textarea, not a generated
  per-parameter form. A per-type widget (a dedicated array editor, etc.) is
  a real, separate frontend investment, not built this session.
- Compiled-language Function Mode (once a second adapter exists) will need
  its own compile-once strategy re-examined for mutation isolation and
  timeout behavior — do not assume the Python adapter's "fresh subprocess
  per case gives you isolation for free" argument carries over.
