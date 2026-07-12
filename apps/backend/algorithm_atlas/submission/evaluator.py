"""
SubmissionEvaluator — runs a user's code against a list of test cases.

Every test case is ALWAYS executed to completion (or its own per-case
timeout) — this evaluator never short-circuits on the first failure. That is
required for honest partial-pass reporting: "1/5 passed" needs real results
for cases 2-5 too, not just "not run because case 2 failed".

Verdict precedence for the single OVERALL submission verdict (every case is
still reported individually in `test_results`; this only picks what a judge
shows as "the" headline verdict):
  Compilation Error   -> the compile step failed (no case executed)
  Time Limit Exceeded -> any case timed out
  Runtime Error       -> any case crashed (nonzero exit, no timeout)
  Wrong Answer        -> any case's output didn't match
  Accepted            -> every case passed

Compilation Error is only ever set STRUCTURALLY (a real nonzero compiler exit
code from notebook.py's PREPARERS / _compile_and_run), never guessed from
stderr text. Languages without an isolable compile step in this judge
(interpreted languages, plus csharp's dotnet-run fallback, scala, swift, go)
report a syntax/setup failure as Runtime Error instead of Compilation Error —
a documented scope boundary, not a bug (see
docs/atlascode-judge-workspace.md).

Performance: for languages in notebook.PREPARERS (cpp, c, java, rust,
kotlin), the source is compiled ONCE and the compiled artifact is re-run for
every test case, instead of recompiling per case (measured ~460-490ms per
g++ compile+run of a trivial program — recompiling 40x would cost ~18-20s of
pure overhead per submission).
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Protocol

from ..api.v1.notebook import PREPARERS, RUNNERS, LangRunResult, _run_prepared
from ..models.atlas_code import TestCase

# Bumped whenever evaluator.py's judging semantics change in a way that could
# change a verdict for the same code+tests (e.g. verdict precedence rules,
# comparison normalization). Submissions snapshot this at submit time.
JUDGE_VERSION = "2.0"  # v2: runs every case (no short-circuit), structural compile/runtime/timeout detection

# Per-test-case wall-clock budget (seconds)
_TEST_TIMEOUT = 5.0
# Hard safety cap across an entire evaluation run (compile-once + up to ~40
# cases). Not expected to be hit in normal operation; exists so a pathological
# problem (e.g. a huge case count) can't hang a request indefinitely.
_MAX_TOTAL_TIMEOUT = 90.0

# Languages with a real, isolable Compilation Error signal (see module
# docstring). Kept separate from PREPARERS because the csharp mcs/mono branch
# also detects compile failures structurally but isn't compile-ONCE-optimized.
_STRUCTURAL_COMPILE_LANGUAGES = frozenset(PREPARERS) | {"csharp"}


class TestCaseLike(Protocol):
    """Shape both a persisted TestCase row and an ad-hoc custom case share —
    lets Run evaluate user-typed scratch cases with the exact same code path
    as Submit's persisted rows, never a separate/duplicated judging path."""
    id: str
    input_data: str
    expected_output: str
    is_hidden: bool
    order: int


@dataclass
class TestResult:
    test_case_id: str
    passed: bool
    verdict: str          # Accepted | Wrong Answer | Runtime Error | Time Limit Exceeded | Compilation Error
    input_data: str
    actual_output: str
    expected_output: str
    stdout: str
    stderr: str
    runtime_ms: float
    memory_kb: float | None
    exit_code: int | None
    timed_out: bool
    is_hidden: bool
    output_truncated: bool = False


@dataclass
class EvaluationResult:
    verdict: str          # overall verdict
    test_results: list[TestResult] = field(default_factory=list)
    total_runtime_ms: float = 0.0
    tests_passed: int = 0
    tests_total: int = 0
    compile_output: str | None = None
    peak_memory_kb: float | None = None


_MAX_ECHO_CHARS = 20_000  # cap per-field text kept in the response (not fabricated, just capped)


def _cap(text: str) -> tuple[str, bool]:
    if len(text) <= _MAX_ECHO_CHARS:
        return text, False
    return text[:_MAX_ECHO_CHARS], True


_VERDICT_PRIORITY = {"Time Limit Exceeded": 0, "Runtime Error": 1, "Wrong Answer": 2}


def _overall_verdict(results: list[TestResult], compile_failed: bool) -> str:
    if compile_failed:
        return "Compilation Error"
    if not results:
        return "Internal Judge Error"
    failing = [r for r in results if not r.passed]
    if not failing:
        return "Accepted"
    failing.sort(key=lambda r: _VERDICT_PRIORITY.get(r.verdict, 99))
    return failing[0].verdict


def _judge_case(r: LangRunResult, tc: TestCaseLike) -> TestResult:
    truncated = False
    if r.timed_out:
        return TestResult(
            test_case_id=tc.id, passed=False, verdict="Time Limit Exceeded",
            input_data="" if tc.is_hidden else tc.input_data,
            actual_output="", expected_output="" if tc.is_hidden else tc.expected_output,
            stdout="", stderr="" if tc.is_hidden else r.stderr,
            runtime_ms=r.duration_ms, memory_kb=r.memory_kb, exit_code=r.exit_code,
            timed_out=True, is_hidden=tc.is_hidden,
        )

    if r.exit_code not in (0, None):
        stderr_capped, truncated = _cap(r.stderr)
        return TestResult(
            test_case_id=tc.id, passed=False, verdict="Runtime Error",
            input_data="" if tc.is_hidden else tc.input_data,
            actual_output="",
            expected_output="" if tc.is_hidden else tc.expected_output,
            stdout="" if tc.is_hidden else r.stdout,
            stderr="" if tc.is_hidden else stderr_capped,
            runtime_ms=r.duration_ms, memory_kb=r.memory_kb, exit_code=r.exit_code,
            timed_out=False, is_hidden=tc.is_hidden, output_truncated=truncated and not tc.is_hidden,
        )

    actual = r.stdout.replace("\r\n", "\n").strip()
    expected = tc.expected_output.replace("\r\n", "\n").strip()
    passed = actual == expected
    actual_capped, truncated = _cap(actual)
    return TestResult(
        test_case_id=tc.id, passed=passed, verdict="Accepted" if passed else "Wrong Answer",
        input_data="" if tc.is_hidden else tc.input_data,
        actual_output="" if tc.is_hidden else actual_capped,
        expected_output="" if tc.is_hidden else expected,
        stdout="" if tc.is_hidden else actual_capped,
        stderr="" if tc.is_hidden else r.stderr,
        runtime_ms=r.duration_ms, memory_kb=r.memory_kb, exit_code=r.exit_code,
        timed_out=False, is_hidden=tc.is_hidden, output_truncated=truncated and not tc.is_hidden,
    )


def _compile_error_case(tc: TestCaseLike, compile_output: str, r: LangRunResult) -> TestResult:
    return TestResult(
        test_case_id=tc.id, passed=False, verdict="Compilation Error",
        input_data="" if tc.is_hidden else tc.input_data,
        actual_output="", expected_output="" if tc.is_hidden else tc.expected_output,
        stdout="", stderr="" if tc.is_hidden else compile_output,
        runtime_ms=r.duration_ms, memory_kb=None, exit_code=r.exit_code,
        timed_out=False, is_hidden=tc.is_hidden,
    )


async def evaluate(
    source: str,
    language: str,
    test_cases: list[TestCaseLike],
) -> EvaluationResult:
    """
    Run `source` (in `language`) against every case in `test_cases`, in
    `order`. Every case always executes — no short-circuiting. Hidden cases
    (`is_hidden=True`) still execute; their input/expected/actual output are
    redacted in the returned TestResult (never sent to the API layer at all).

    Callers decide WHICH cases to pass in: Submit passes every persisted
    TestCase for the problem; Run passes only the visible/selected/custom
    subset. This function has no concept of "Run" vs "Submit" — that
    distinction belongs to the API layer, not the judge.
    """
    ordered = sorted(test_cases, key=lambda tc: tc.order)

    if not ordered:
        return EvaluationResult(
            verdict="Internal Judge Error", tests_total=0,
            compile_output="No test cases were provided to the judge.",
        )

    preparer = PREPARERS.get(language)
    runner = RUNNERS.get(language)
    if preparer is None and runner is None:
        return EvaluationResult(
            verdict="Compilation Error", tests_total=len(ordered),
            compile_output=f"Language '{language}' is not supported by the judge.",
        )

    deadline = time.monotonic() + _MAX_TOTAL_TIMEOUT
    results: list[TestResult] = []
    total_ms = 0.0
    peak_mem: float | None = None
    compile_output: str | None = None
    compile_failed = False

    prepared = None
    if preparer is not None:
        prepared, compile_failure = await preparer(source, _TEST_TIMEOUT + 10.0)
        if compile_failure is not None:
            compile_failed = True
            compile_output = compile_failure.compile_output
            total_ms += compile_failure.duration_ms
            for tc in ordered:
                results.append(_compile_error_case(tc, compile_output or "", compile_failure))
            return EvaluationResult(
                verdict="Compilation Error", test_results=results, total_runtime_ms=total_ms,
                tests_passed=0, tests_total=len(ordered), compile_output=compile_output,
            )

    try:
        for tc in ordered:
            if time.monotonic() > deadline:
                # Aggregate judge time budget exhausted (e.g. a hanging
                # program would otherwise cost N-cases x per-case-timeout to
                # fully judge). This is honestly labeled as a budget cutoff,
                # not a claim that THIS specific case was individually
                # measured to time out.
                results.append(TestResult(
                    test_case_id=tc.id, passed=False, verdict="Time Limit Exceeded",
                    input_data="" if tc.is_hidden else tc.input_data,
                    actual_output="", expected_output="" if tc.is_hidden else tc.expected_output,
                    stdout="", stderr="" if tc.is_hidden else "Judge time budget exhausted before this case could run.",
                    runtime_ms=0.0, memory_kb=None,
                    exit_code=None, timed_out=True, is_hidden=tc.is_hidden,
                ))
                continue

            input_bytes = tc.input_data.encode("utf-8") if tc.input_data else None
            try:
                if prepared is not None:
                    r = await asyncio.wait_for(
                        _run_prepared(prepared, _TEST_TIMEOUT, input_bytes),
                        timeout=_TEST_TIMEOUT + 2,
                    )
                else:
                    r = await asyncio.wait_for(
                        runner(source, _TEST_TIMEOUT, input_bytes=input_bytes),
                        timeout=_TEST_TIMEOUT + 2,
                    )
            except asyncio.TimeoutError:
                r = LangRunResult(
                    stdout="", stderr=f"TimeoutError: execution exceeded {_TEST_TIMEOUT}s limit",
                    duration_ms=_TEST_TIMEOUT * 1000, exit_code=None, timed_out=True,
                )

            total_ms += r.duration_ms
            if r.memory_kb is not None:
                peak_mem = max(peak_mem or 0.0, r.memory_kb)

            # A non-compile-once language (no `prepared`) can still report a
            # structural compile failure on its first invocation (csharp
            # mcs/mono branch, or a compile-once language whose PREPARER
            # somehow wasn't used) — every remaining case is the same source,
            # so stop and mark all of them Compilation Error rather than
            # re-attempting a doomed compile per case.
            if r.compile_failed:
                compile_failed = True
                compile_output = r.compile_output
                remaining = ordered[len(results):]
                for rem in remaining:
                    results.append(_compile_error_case(rem, compile_output or "", r))
                break

            results.append(_judge_case(r, tc))
    finally:
        if prepared is not None:
            prepared.cleanup()

    tests_passed = sum(1 for r in results if r.passed)
    overall = _overall_verdict(results, compile_failed)
    return EvaluationResult(
        verdict=overall,
        test_results=results,
        total_runtime_ms=total_ms,
        tests_passed=tests_passed,
        tests_total=len(ordered),
        compile_output=compile_output,
        peak_memory_kb=peak_mem,
    )
