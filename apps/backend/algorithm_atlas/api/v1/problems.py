"""
Problems API

GET  /api/v1/problems              list + filter
GET  /api/v1/problems/:slug        detail (visible test cases only)
GET  /api/v1/problems/:slug/hints  progressive hints
POST /api/v1/problems/:slug/run    fast iteration -- visible/selected/custom
                                    cases only, never persisted, never touches
                                    hidden tests or progress/acceptance stats
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ...atlascode.function_mode.contracts import FunctionContract, validate_arguments
from ...atlascode.function_mode.registry import get_adapter
from ...atlascode.function_mode.runner import FunctionCase, evaluate_function
from ...atlascode.problems_snapshot import ensure_test_cases_loaded
from ...database import get_db
from ...models.atlas_code import Problem, TestCase
from ...submission.evaluator import JUDGE_VERSION, evaluate

router = APIRouter(prefix="/problems", tags=["atlas-code"])

# Same 17-language target list as scripts/generate_honest_matrix_report.py --
# kept in sync manually since the ledger table isn't a mapped ORM model.
TARGET_LANGUAGES_TOTAL = 17

# "Function Mode" == LeetCode Mode (write only the function, judge drives it);
# "Program Mode" == Codeforces Mode (write a full stdin/stdout program). The
# internal `mode`/`execution_mode` values in the DB and API stay 'function'/
# 'program' -- this is a display-naming decision only (2026-07-12: catalog
# completion/coverage UI), not a contract change.


async def _language_coverage(db: AsyncSession, problem_ids: list[str]) -> dict[str, dict]:
    """Per-problem verified-language sets, read from the persistent
    `atlascode_matrix_ledger` table (scripts/atlascode_ledger.py) -- the same
    Level-6 ledger the honest matrix report (docs/atlascode-complete-matrix.md)
    is generated from. Not a mapped ORM model (it's written by standalone
    verification scripts), so queried via raw SQL on the same DB connection.

    Completion here matches the problem-level definition established in
    docs/atlascode-complete-matrix.md: a problem is complete once it has at
    least one Level-6-verified cell in EITHER mode/language -- additional
    languages are Language Coverage, not a completion gate.
    """
    if not problem_ids:
        return {}
    placeholders = ", ".join(f":id{i}" for i in range(len(problem_ids)))
    params = {f"id{i}": pid for i, pid in enumerate(problem_ids)}
    try:
        rows = (await db.execute(
            text(
                "SELECT problem_id, mode, language FROM atlascode_matrix_ledger "
                f"WHERE verification_level = 6 AND problem_id IN ({placeholders})"
            ),
            params,
        )).fetchall()
    except SQLAlchemyError:
        # The ledger table is normally created by init_db() (see database.py's
        # _ensure_ledger_table) -- this is a last-resort guard, not the
        # primary fix, so the catalog/detail endpoints degrade to "no
        # verified languages yet" instead of 500ing the whole page if the
        # table is ever missing or briefly unavailable for any other reason.
        await db.rollback()
        logger.warning("atlascode_matrix_ledger query failed; reporting zero language coverage", exc_info=True)
        rows = []

    out: dict[str, dict] = {
        pid: {"leetcode_languages": set(), "codeforces_languages": set()} for pid in problem_ids
    }
    for problem_id, mode, language in rows:
        key = "leetcode_languages" if mode == "function" else "codeforces_languages"
        out[problem_id][key].add(language)

    return {
        pid: {
            "leetcode_languages": sorted(v["leetcode_languages"]),
            "codeforces_languages": sorted(v["codeforces_languages"]),
            "is_complete": bool(v["leetcode_languages"] or v["codeforces_languages"]),
        }
        for pid, v in out.items()
    }

# Function Mode verdicts that normalize to the same passed/failed vocabulary
# Program Mode already uses -- Contract Error / Runtime Error / Time Limit
# Exceeded / Compilation Error are surfaced as-is (see Phase 18: never
# collapse a structural contract error into a generic "failed").
_FUNCTION_COMPARISON_VERDICTS = {"Accepted", "Wrong Answer"}


# ── Response schemas ──────────────────────────────────────────────────────────

class TestCaseOut(BaseModel):
    id: str
    input_data: str
    expected_output: str
    explanation: Optional[str]
    order: int
    # Function Mode -- None for problems/cases without a function_contract;
    # lets the Testcase tab preview typed arguments before Run, in Function
    # Mode, for a visible case (same underlying case as input_data/
    # expected_output above, just the typed representation).
    function_args: Optional[dict] = None
    function_expected: Optional[Any] = None

    class Config:
        from_attributes = True


class ProblemSummary(BaseModel):
    id: str
    title: str
    difficulty: str
    category: str
    acceptance_rate: float
    estimated_minutes: int
    companies: list
    total_submissions: int
    total_accepted: int
    # Problem-level completion + Language Coverage (2026-07-12 redefinition,
    # see docs/atlascode-complete-matrix.md) -- NOT from the ORM row, filled
    # in by list_problems()/get_problem() via _language_coverage() below.
    is_complete: bool = True
    leetcode_languages: list[str] = []
    codeforces_languages: list[str] = []

    class Config:
        from_attributes = True


class ProblemDetail(BaseModel):
    id: str
    title: str
    difficulty: str
    category: str
    problem_statement: str
    examples: list
    constraints: list
    companies: list
    acceptance_rate: float
    estimated_minutes: int
    algorithm_slug: Optional[str]
    starter_code: dict
    # Function Mode (see atlascode/function_mode/). function_contract is None
    # when this problem doesn't support Function Mode yet -- Program Mode
    # (starter_code above) is unaffected either way (Phase 22 honest matrix).
    function_contract: Optional[dict]
    starter_code_function: dict
    total_submissions: int
    total_accepted: int
    visible_test_cases: list[TestCaseOut]
    # See ProblemSummary above -- same problem-level completion model.
    is_complete: bool = True
    leetcode_languages: list[str] = []
    codeforces_languages: list[str] = []

    class Config:
        from_attributes = True


class HintOut(BaseModel):
    level: int
    text: str


# ── Run schemas ───────────────────────────────────────────────────────────────
# Run is deliberately a SEPARATE, non-persisting code path from Submit
# (submissions.py): it never touches hidden test cases, never writes a
# Submission row, and never updates UserProgress/acceptance stats. It exists
# purely for fast iteration against visible or user-authored cases.

class CustomCaseIn(BaseModel):
    # Program Mode fields
    input_data: str = Field("", max_length=65_536)
    expected_output: Optional[str] = None  # None => just show output, no pass/fail claim
    # Function Mode fields (used instead of input_data/expected_output when
    # execution_mode == "function" -- see Phase 14: typed arguments, not raw
    # stdin, and validated against the contract BEFORE execution).
    arguments: Optional[dict[str, Any]] = None
    expected_return: Optional[Any] = None
    has_expected_return: bool = False  # explicit flag -- None is a valid expected value


class RunRequest(BaseModel):
    language: str
    code: str = Field(..., max_length=65_536)
    mode: Literal["visible", "selected", "custom"] = "visible"
    # Which Run contract to execute under (see atlascode/function_mode/).
    # "program" preserves 100% of the existing stdin/stdout behavior below.
    execution_mode: Literal["function", "program"] = "program"
    case_indices: Optional[list[int]] = None   # indices into visible_test_cases; used when mode == "selected"
    custom_cases: Optional[list[CustomCaseIn]] = None  # used when mode == "custom"


class RunCaseResult(BaseModel):
    case_index: int
    label: str
    is_hidden: bool = False   # Run never touches hidden cases -- always False
    has_expected: bool
    # passed | failed | executed | Runtime Error | Time Limit Exceeded |
    # Compilation Error | Function Contract Error (function mode only)
    status: str
    input_data: str
    expected_output: Optional[str]
    actual_output: str
    stdout: str
    stderr: str
    runtime_ms: float
    memory_kb: Optional[float]
    exit_code: Optional[int]
    timed_out: bool
    # Function Mode only (all None/omitted in Program Mode results) -- the
    # frontend must label these "Arguments"/"Expected Return"/"Actual Return",
    # never "stdin"/"stdout" (Phase 16: the UI language must reflect the
    # contract actually being judged).
    arguments: Optional[dict[str, Any]] = None
    expected_return: Optional[Any] = None
    actual_return: Optional[Any] = None
    contract_error: Optional[dict] = None


class RunSummary(BaseModel):
    passed: int
    failed: int
    total: int
    runtime_ms: float


class RunResult(BaseModel):
    run_id: str
    status: str  # "completed"
    language: str
    execution_mode: Literal["function", "program"]
    judge_version: str
    summary: RunSummary
    compile_output: Optional[str]
    cases: list[RunCaseResult]


@dataclass
class _AdHocCase:
    """Duck-types evaluator.TestCaseLike for a user-authored scratch case that
    is never persisted to the test_cases table."""
    id: str
    input_data: str
    expected_output: str
    is_hidden: bool
    order: int


# A pass/fail verdict is only meaningful when the case HAS an expected output.
# A custom case with none still runs for real (real stdout/stderr/runtime/
# memory/exit_code) but is reported as "executed", never a fabricated
# pass/fail — see Phase 14/Scenario C in docs/atlascode-judge-workspace.md.
_COMPARISON_VERDICTS = {"Accepted", "Wrong Answer"}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[ProblemSummary])
async def list_problems(
    response: Response,
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[ProblemSummary]:
    filters = []
    if category:
        filters.append(Problem.category == category)
    if difficulty:
        filters.append(Problem.difficulty == difficulty)
    if search:
        filters.append(Problem.title.ilike(f"%{search}%"))

    count_stmt = select(func.count()).select_from(Problem)
    for f in filters:
        count_stmt = count_stmt.where(f)
    total = (await db.execute(count_stmt)).scalar_one()
    # Exposed as a response header (not a body-shape change) so existing
    # consumers of the plain list[ProblemSummary] body are unaffected; the
    # catalog page's pagination controls are the only reader of this header.
    response.headers["X-Total-Count"] = str(total)

    stmt = select(Problem)
    for f in filters:
        stmt = stmt.where(f)
    stmt = stmt.order_by(Problem.category, Problem.title).offset(offset).limit(limit)
    rows = (await db.execute(stmt)).scalars().all()

    coverage = await _language_coverage(db, [r.id for r in rows])
    default_cov = {"is_complete": True, "leetcode_languages": [], "codeforces_languages": []}
    return [
        ProblemSummary(
            id=r.id, title=r.title, difficulty=r.difficulty, category=r.category,
            acceptance_rate=r.acceptance_rate, estimated_minutes=r.estimated_minutes,
            companies=r.companies or [], total_submissions=r.total_submissions,
            total_accepted=r.total_accepted, **coverage.get(r.id, default_cov),
        )
        for r in rows
    ]


@router.get("/{slug}", response_model=ProblemDetail)
async def get_problem(slug: str, db: AsyncSession = Depends(get_db)) -> ProblemDetail:
    # Must run before this request's first db.execute() -- see
    # ensure_test_cases_loaded()'s docstring for why (avoids a lock race
    # between this session's about-to-autobegin transaction and the lazy
    # loader's own short-lived sync sqlite3 connection to the same file).
    await ensure_test_cases_loaded(slug)
    result = await db.execute(select(Problem).where(Problem.id == slug))
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    tc_result = await db.execute(
        select(TestCase)
        .where(TestCase.problem_id == slug, TestCase.is_hidden == False)  # noqa: E712
        .order_by(TestCase.order)
    )
    visible_tcs = tc_result.scalars().all()

    coverage = (await _language_coverage(db, [slug])).get(
        slug, {"is_complete": True, "leetcode_languages": [], "codeforces_languages": []}
    )

    return ProblemDetail(
        id=problem.id,
        title=problem.title,
        difficulty=problem.difficulty,
        category=problem.category,
        problem_statement=problem.problem_statement,
        examples=problem.examples or [],
        constraints=problem.constraints or [],
        companies=problem.companies or [],
        acceptance_rate=problem.acceptance_rate,
        estimated_minutes=problem.estimated_minutes,
        algorithm_slug=problem.algorithm_slug,
        starter_code=problem.starter_code or {},
        function_contract=problem.function_contract,
        starter_code_function=problem.starter_code_function or {},
        total_submissions=problem.total_submissions,
        total_accepted=problem.total_accepted,
        visible_test_cases=[TestCaseOut.model_validate(tc) for tc in visible_tcs],
        **coverage,
    )


@router.get("/{slug}/hints", response_model=list[HintOut])
async def get_hints(
    slug: str,
    max_level: int = Query(1, ge=1, le=7),
    db: AsyncSession = Depends(get_db),
) -> list[HintOut]:
    result = await db.execute(select(Problem).where(Problem.id == slug))
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")
    hints = problem.hints or []
    return [HintOut(**h) for h in hints if h.get("level", 0) <= max_level]


@router.post("/{slug}/run", response_model=RunResult)
async def run_problem(slug: str, body: RunRequest, db: AsyncSession = Depends(get_db)) -> RunResult:
    """
    Fast iteration -- never persists, never touches hidden cases or
    progress/acceptance stats, regardless of which Run contract is used.

    execution_mode == "program" (default): unchanged behavior, see
    _run_program_mode below.
    execution_mode == "function": a completely separate contract -- see
    _run_function_mode and atlascode/function_mode/.
    """
    # See get_problem()'s matching call -- must precede this request's first
    # db.execute().
    await ensure_test_cases_loaded(slug)
    result = await db.execute(select(Problem).where(Problem.id == slug))
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    if body.execution_mode == "function":
        return await _run_function_mode(problem, body, db)
    return await _run_program_mode(problem, body, db)


async def _run_program_mode(problem: Problem, body: RunRequest, db: AsyncSession) -> RunResult:
    """
    Evaluates only visible/selected/custom cases through the exact same judge
    as Submit (`submission.evaluator.evaluate`), but:
      - never loads or executes hidden test cases
      - never persists a Submission row
      - never updates UserProgress, solved state, or acceptance stats

    Unchanged from before Function Mode existed -- only extracted into its
    own function so run_problem() could dispatch on execution_mode.
    """
    slug = problem.id
    tc_result = await db.execute(
        select(TestCase)
        .where(TestCase.problem_id == slug, TestCase.is_hidden == False)  # noqa: E712
        .order_by(TestCase.order)
    )
    visible_tcs = list(tc_result.scalars().all())

    labels: dict[str, str]
    has_expected: dict[str, bool]

    if body.mode == "custom":
        if not body.custom_cases:
            raise HTTPException(status_code=400, detail="mode='custom' requires at least one custom_case")
        cases: list = [
            _AdHocCase(
                id=f"custom-{i}", input_data=c.input_data,
                expected_output=c.expected_output or "", is_hidden=False, order=i,
            )
            for i, c in enumerate(body.custom_cases)
        ]
        labels = {c.id: f"Custom {i + 1}" for i, c in enumerate(cases)}
        has_expected = {
            cases[i].id: (body.custom_cases[i].expected_output is not None)
            for i in range(len(cases))
        }
    elif body.mode == "selected":
        if not body.case_indices:
            raise HTTPException(status_code=400, detail="mode='selected' requires case_indices")
        selected_idx = [i for i in body.case_indices if 0 <= i < len(visible_tcs)]
        if not selected_idx:
            raise HTTPException(status_code=400, detail="No valid case_indices for this problem's visible cases")
        cases = [visible_tcs[i] for i in selected_idx]
        labels = {tc.id: f"Case {idx + 1}" for tc, idx in zip(cases, selected_idx)}
        has_expected = {tc.id: True for tc in cases}
    else:  # "visible"
        if not visible_tcs:
            raise HTTPException(status_code=400, detail="This problem has no visible test cases to run")
        cases = visible_tcs
        labels = {tc.id: f"Case {i + 1}" for i, tc in enumerate(cases)}
        has_expected = {tc.id: True for tc in cases}

    eval_result = await evaluate(body.code, body.language, cases)

    case_results: list[RunCaseResult] = []
    for i, (tc, tr) in enumerate(zip(cases, eval_result.test_results)):
        expects = has_expected.get(tc.id, True)
        status = tr.verdict
        if not expects and tr.verdict in _COMPARISON_VERDICTS:
            status = "executed"
        case_results.append(RunCaseResult(
            case_index=i,
            label=labels.get(tc.id, f"Case {i + 1}"),
            is_hidden=False,
            has_expected=expects,
            status=status,
            input_data=tc.input_data,
            expected_output=tc.expected_output if expects else None,
            actual_output=tr.actual_output,
            stdout=tr.stdout,
            stderr=tr.stderr,
            runtime_ms=tr.runtime_ms,
            memory_kb=tr.memory_kb,
            exit_code=tr.exit_code,
            timed_out=tr.timed_out,
        ))

    # evaluator reports "Accepted"/"Wrong Answer" per-case (see TestResult.verdict);
    # normalize expectation-bearing cases to passed/failed so the frontend
    # never has to special-case the judge's internal verdict vocabulary. A
    # no-expected-output custom case is neither a pass nor a failure, so it's
    # excluded from the passed/failed/total summary entirely.
    for c in case_results:
        if c.has_expected and c.status == "Accepted":
            c.status = "passed"
        elif c.has_expected and c.status == "Wrong Answer":
            c.status = "failed"

    comparable = [c for c in case_results if c.has_expected]
    passed = sum(1 for c in comparable if c.status == "passed")
    failed = len(comparable) - passed

    return RunResult(
        run_id=f"run-{problem.id}-{int(eval_result.total_runtime_ms * 1000)}",
        status="completed",
        language=body.language,
        execution_mode="program",
        judge_version=JUDGE_VERSION,
        summary=RunSummary(
            passed=passed, failed=failed, total=len(comparable),
            runtime_ms=eval_result.total_runtime_ms,
        ),
        compile_output=eval_result.compile_output,
        cases=case_results,
    )


async def _run_function_mode(problem: Problem, body: RunRequest, db: AsyncSession) -> RunResult:
    """
    Function Mode's Run path -- typed arguments in, typed return out, judged
    by atlascode/function_mode/runner.evaluate_function. Never touches hidden
    test cases, never persists anything (same guarantees as Program Mode).
    """
    if not problem.function_contract:
        raise HTTPException(
            status_code=422,
            detail=f"Function Mode is not supported for problem '{problem.id}' yet.",
        )
    contract = FunctionContract.from_dict(problem.function_contract)

    if get_adapter(body.language) is None:
        raise HTTPException(
            status_code=422,
            detail=f"Function Mode is not supported for language '{body.language}' yet.",
        )

    tc_result = await db.execute(
        select(TestCase)
        .where(TestCase.problem_id == problem.id, TestCase.is_hidden == False)  # noqa: E712
        .order_by(TestCase.order)
    )
    visible_tcs = list(tc_result.scalars().all())

    labels: dict[str, str] = {}
    function_cases: list[FunctionCase] = []

    if body.mode == "custom":
        if not body.custom_cases:
            raise HTTPException(status_code=400, detail="mode='custom' requires at least one custom_case")
        for i, c in enumerate(body.custom_cases):
            if c.arguments is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Custom case {i + 1}: Function Mode requires 'arguments', not 'input_data'",
                )
            errors = validate_arguments(c.arguments, contract)
            if errors:
                raise HTTPException(
                    status_code=400,
                    detail=f"Custom case {i + 1} does not match this problem's function signature: " + "; ".join(errors),
                )
            case_id = f"custom-{i}"
            function_cases.append(FunctionCase(
                id=case_id, arguments=c.arguments,
                expected=c.expected_return, has_expected=c.has_expected_return,
                is_hidden=False, order=i,
            ))
            labels[case_id] = f"Custom {i + 1}"
    elif body.mode == "selected":
        if not body.case_indices:
            raise HTTPException(status_code=400, detail="mode='selected' requires case_indices")
        selected_idx = [i for i in body.case_indices if 0 <= i < len(visible_tcs)]
        if not selected_idx:
            raise HTTPException(status_code=400, detail="No valid case_indices for this problem's visible cases")
        for tc, idx in zip((visible_tcs[i] for i in selected_idx), selected_idx):
            function_cases.append(FunctionCase(
                id=tc.id, arguments=tc.function_args or {}, expected=tc.function_expected,
                has_expected=True, is_hidden=False, order=idx,
            ))
            labels[tc.id] = f"Case {idx + 1}"
    else:  # "visible"
        if not visible_tcs:
            raise HTTPException(status_code=400, detail="This problem has no visible test cases to run")
        for i, tc in enumerate(visible_tcs):
            function_cases.append(FunctionCase(
                id=tc.id, arguments=tc.function_args or {}, expected=tc.function_expected,
                has_expected=True, is_hidden=False, order=i,
            ))
            labels[tc.id] = f"Case {i + 1}"

    eval_result = await evaluate_function(body.code, body.language, contract, function_cases)

    has_expected_by_id = {fc.id: fc.has_expected for fc in function_cases}

    case_results: list[RunCaseResult] = []
    for i, r in enumerate(eval_result.case_results):
        expects = has_expected_by_id.get(r.case_id, True)
        status = r.verdict
        if not expects and r.verdict in _FUNCTION_COMPARISON_VERDICTS:
            status = "executed"
        elif r.verdict == "Accepted":
            status = "passed"
        elif r.verdict == "Wrong Answer":
            status = "failed"
        case_results.append(RunCaseResult(
            case_index=i,
            label=labels.get(r.case_id, f"Case {i + 1}"),
            is_hidden=False,
            has_expected=expects,
            status=status,
            input_data=json.dumps(r.arguments),
            expected_output=json.dumps(r.expected_return) if expects else None,
            actual_output=json.dumps(r.actual_return) if r.actual_return is not None else "",
            stdout=r.stdout,
            stderr=r.stderr,
            runtime_ms=r.runtime_ms,
            memory_kb=r.memory_kb,
            exit_code=r.exit_code,
            timed_out=r.timed_out,
            arguments=r.arguments,
            expected_return=r.expected_return,
            actual_return=r.actual_return,
            contract_error=r.contract_error,
        ))

    comparable = [c for c in case_results if c.has_expected]
    passed = sum(1 for c in comparable if c.status == "passed")
    failed = len(comparable) - passed

    return RunResult(
        run_id=f"run-{problem.id}-{int(eval_result.total_runtime_ms * 1000)}",
        status="completed",
        language=body.language,
        execution_mode="function",
        judge_version=JUDGE_VERSION,
        summary=RunSummary(
            passed=passed, failed=failed, total=len(comparable),
            runtime_ms=eval_result.total_runtime_ms,
        ),
        compile_output=eval_result.compile_output,
        cases=case_results,
    )
