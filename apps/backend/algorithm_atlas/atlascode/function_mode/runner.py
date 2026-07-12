"""
Function Mode's evaluation loop -- the sibling of submission/evaluator.py's
Program Mode evaluate(). Reuses the exact same low-level subprocess execution
primitive (notebook.py's RUNNERS, the same per-case/total timeout budget as
Program Mode) but the verdict logic is typed-return based, never a stdout
string compare, so it cannot share evaluate()'s comparison code.

Every case always executes to completion or its own timeout -- same
no-short-circuit policy as Program Mode, for the same reason (honest partial
pass reporting).

For a COMPILED-language adapter (one exposing `compose_program(user_code,
contract)` instead of `compose_source(user_code, contract, arguments)` --
see compiled_adapters.py), this loop instead compiles ONCE via notebook.py's
existing PREPARERS/_run_prepared (the same compile-once infrastructure
Program Mode's own evaluator.py already relies on for cpp/c/java/rust/
kotlin), then invokes the SAME compiled artifact once per case with that
case's arguments on stdin -- never recompiling per test case.
"""
from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Any

from ...api.v1.notebook import PREPARERS, RUNNERS, LangRunResult, _run_prepared
from ...submission.evaluator import _MAX_TOTAL_TIMEOUT as MAX_TOTAL_TIMEOUT
from ...submission.evaluator import _TEST_TIMEOUT as TEST_TIMEOUT
from .contracts import FunctionContract, compare_typed
from .protocol import CONTRACT_ERROR_SENTINEL, RESULT_SENTINEL, find_sentinel_payload
from .registry import get_adapter


@dataclass
class FunctionCase:
    """One case to run in Function Mode -- shape mirrors
    submission.evaluator.TestCaseLike but carries typed arguments/expected
    instead of stdin/stdout strings."""
    id: str
    arguments: dict[str, Any]
    expected: Any
    has_expected: bool
    is_hidden: bool
    order: int = 0


@dataclass
class FunctionCaseResult:
    case_id: str
    verdict: str  # Accepted | Wrong Answer | Runtime Error | Time Limit Exceeded | Function Contract Error | executed
    passed: bool
    arguments: dict[str, Any]
    expected_return: Any
    actual_return: Any
    stdout: str
    stderr: str
    runtime_ms: float
    memory_kb: float | None
    exit_code: int | None
    timed_out: bool
    contract_error: dict | None = None


@dataclass
class FunctionEvaluationResult:
    verdict: str
    case_results: list[FunctionCaseResult] = field(default_factory=list)
    total_runtime_ms: float = 0.0
    compile_output: str | None = None


# Contract Error ranks above Runtime Error: a missing/renamed function is a
# structural problem with what the judge was asked to run, not a bug in an
# otherwise-valid program (see Phase 18).
_VERDICT_PRIORITY = {
    "Time Limit Exceeded": 0,
    "Function Contract Error": 1,
    "Runtime Error": 2,
    "Wrong Answer": 3,
}


def _overall_verdict(results: list[FunctionCaseResult]) -> str:
    if not results:
        return "Internal Judge Error"
    failing = [r for r in results if not r.passed and r.verdict != "executed"]
    if not failing:
        return "Accepted"
    failing.sort(key=lambda r: _VERDICT_PRIORITY.get(r.verdict, 99))
    return failing[0].verdict


def _judge_case(r: LangRunResult, c: FunctionCase, contract: FunctionContract) -> FunctionCaseResult:
    args_out = {} if c.is_hidden else c.arguments
    expected_out = None if c.is_hidden else c.expected

    if r.timed_out:
        return FunctionCaseResult(
            case_id=c.id, verdict="Time Limit Exceeded", passed=False,
            arguments=args_out, expected_return=expected_out, actual_return=None,
            stdout="", stderr="" if c.is_hidden else r.stderr,
            runtime_ms=r.duration_ms, memory_kb=r.memory_kb, exit_code=r.exit_code, timed_out=True,
        )

    if r.exit_code not in (0, None):
        # A real, uncaught exception from inside the user's function (the
        # driver never wraps the call itself in try/except) -- an honest
        # Runtime Error, never silently mapped to Wrong Answer or swallowed.
        return FunctionCaseResult(
            case_id=c.id, verdict="Runtime Error", passed=False,
            arguments=args_out, expected_return=expected_out, actual_return=None,
            stdout="" if c.is_hidden else r.stdout, stderr="" if c.is_hidden else r.stderr,
            runtime_ms=r.duration_ms, memory_kb=r.memory_kb, exit_code=r.exit_code, timed_out=False,
        )

    contract_payload = find_sentinel_payload(r.stdout, CONTRACT_ERROR_SENTINEL)
    if contract_payload is not None:
        try:
            detail = json.loads(contract_payload)
        except json.JSONDecodeError:
            detail = {"reason": "unknown", "message": contract_payload}
        return FunctionCaseResult(
            case_id=c.id, verdict="Function Contract Error", passed=False,
            arguments=args_out, expected_return=expected_out, actual_return=None,
            stdout="" if c.is_hidden else r.stdout, stderr="" if c.is_hidden else r.stderr,
            runtime_ms=r.duration_ms, memory_kb=r.memory_kb, exit_code=r.exit_code, timed_out=False,
            contract_error=None if c.is_hidden else detail,
        )

    result_payload = find_sentinel_payload(r.stdout, RESULT_SENTINEL)
    if result_payload is None:
        # Exited 0 but the driver never printed a result line -- a judge-side
        # anomaly (e.g. a language runtime quirk), never reported as a silent
        # pass or a fabricated value.
        return FunctionCaseResult(
            case_id=c.id, verdict="Runtime Error", passed=False,
            arguments=args_out, expected_return=expected_out, actual_return=None,
            stdout="" if c.is_hidden else r.stdout,
            stderr="" if c.is_hidden else (r.stderr or "The judge driver produced no result."),
            runtime_ms=r.duration_ms, memory_kb=r.memory_kb, exit_code=r.exit_code, timed_out=False,
        )

    try:
        actual = json.loads(result_payload)
    except json.JSONDecodeError:
        return FunctionCaseResult(
            case_id=c.id, verdict="Runtime Error", passed=False,
            arguments=args_out, expected_return=expected_out, actual_return=None,
            stdout="" if c.is_hidden else r.stdout,
            stderr="" if c.is_hidden else "The function's return value could not be serialized to JSON.",
            runtime_ms=r.duration_ms, memory_kb=r.memory_kb, exit_code=r.exit_code, timed_out=False,
        )

    if not c.has_expected:
        return FunctionCaseResult(
            case_id=c.id, verdict="executed", passed=False,
            arguments=args_out, expected_return=None, actual_return=actual,
            stdout=r.stdout, stderr=r.stderr,
            runtime_ms=r.duration_ms, memory_kb=r.memory_kb, exit_code=r.exit_code, timed_out=False,
        )

    passed = compare_typed(actual, c.expected, contract.return_type)
    return FunctionCaseResult(
        case_id=c.id, verdict="Accepted" if passed else "Wrong Answer", passed=passed,
        arguments=args_out, expected_return=expected_out, actual_return=None if c.is_hidden else actual,
        stdout="" if c.is_hidden else r.stdout, stderr="" if c.is_hidden else r.stderr,
        runtime_ms=r.duration_ms, memory_kb=r.memory_kb, exit_code=r.exit_code, timed_out=False,
    )


async def evaluate_function(
    user_code: str,
    language: str,
    contract: FunctionContract,
    cases: list[FunctionCase],
) -> FunctionEvaluationResult:
    adapter = get_adapter(language)
    runner = RUNNERS.get(language)
    if adapter is None or runner is None:
        return FunctionEvaluationResult(
            verdict="Compilation Error",
            compile_output=f"Function Mode is not supported for language '{language}' yet.",
        )

    ordered = sorted(cases, key=lambda c: c.order)
    if not ordered:
        return FunctionEvaluationResult(verdict="Internal Judge Error")

    deadline = time.monotonic() + MAX_TOTAL_TIMEOUT
    results: list[FunctionCaseResult] = []
    total_ms = 0.0

    compose_program = getattr(adapter, "compose_program", None)
    preparer = PREPARERS.get(language)

    if compose_program is not None and preparer is not None:
        # Compile-once path (Phase 7/29): one compile, then the SAME
        # artifact is invoked once per case with that case's typed
        # arguments as JSON on stdin -- never recompiling per case.
        program_source = compose_program(user_code, contract)
        prepared, compile_failure = await preparer(program_source, TEST_TIMEOUT + 10.0)
        if prepared is None:
            return FunctionEvaluationResult(
                verdict="Compilation Error",
                compile_output=compile_failure.compile_output if compile_failure else "compilation failed",
            )
        try:
            for c in ordered:
                if time.monotonic() > deadline:
                    results.append(FunctionCaseResult(
                        case_id=c.id, verdict="Time Limit Exceeded", passed=False,
                        arguments={} if c.is_hidden else c.arguments,
                        expected_return=None if c.is_hidden else c.expected, actual_return=None,
                        stdout="", stderr="" if c.is_hidden else "Judge time budget exhausted before this case could run.",
                        runtime_ms=0.0, memory_kb=None, exit_code=None, timed_out=True,
                    ))
                    continue

                input_bytes = json.dumps(c.arguments).encode("utf-8")
                try:
                    r: LangRunResult = await asyncio.wait_for(
                        _run_prepared(prepared, TEST_TIMEOUT, input_bytes), timeout=TEST_TIMEOUT + 2
                    )
                except asyncio.TimeoutError:
                    r = LangRunResult(
                        stdout="", stderr=f"TimeoutError: execution exceeded {TEST_TIMEOUT}s limit",
                        duration_ms=TEST_TIMEOUT * 1000, exit_code=None, timed_out=True,
                    )
                total_ms += r.duration_ms
                results.append(_judge_case(r, c, contract))
        finally:
            prepared.cleanup()

        return FunctionEvaluationResult(
            verdict=_overall_verdict(results),
            case_results=results,
            total_runtime_ms=total_ms,
        )

    for c in ordered:
        if time.monotonic() > deadline:
            results.append(FunctionCaseResult(
                case_id=c.id, verdict="Time Limit Exceeded", passed=False,
                arguments={} if c.is_hidden else c.arguments,
                expected_return=None if c.is_hidden else c.expected, actual_return=None,
                stdout="", stderr="" if c.is_hidden else "Judge time budget exhausted before this case could run.",
                runtime_ms=0.0, memory_kb=None, exit_code=None, timed_out=True,
            ))
            continue

        source = adapter.compose_source(user_code, contract, c.arguments)
        try:
            r: LangRunResult = await asyncio.wait_for(runner(source, TEST_TIMEOUT), timeout=TEST_TIMEOUT + 2)
        except asyncio.TimeoutError:
            r = LangRunResult(
                stdout="", stderr=f"TimeoutError: execution exceeded {TEST_TIMEOUT}s limit",
                duration_ms=TEST_TIMEOUT * 1000, exit_code=None, timed_out=True,
            )

        total_ms += r.duration_ms
        results.append(_judge_case(r, c, contract))

    return FunctionEvaluationResult(
        verdict=_overall_verdict(results),
        case_results=results,
        total_runtime_ms=total_ms,
    )
