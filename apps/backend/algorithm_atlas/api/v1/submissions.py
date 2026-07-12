"""
Submissions API

POST /api/v1/submissions          submit + evaluate
GET  /api/v1/submissions/:id      fetch one submission result
GET  /api/v1/submissions          list submissions for a problem/user
"""
from __future__ import annotations

import statistics
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_serializer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import get_db
from ...models.atlas_code import Problem, Submission, TestCase, UserProgress
from ...submission.evaluator import JUDGE_VERSION, TestResult, evaluate

router = APIRouter(prefix="/submissions", tags=["atlas-code"])


# ── Request / Response schemas ────────────────────────────────────────────────

class SubmitRequest(BaseModel):
    problem_id: str
    language: str
    code: str = Field(..., max_length=65_536)
    user_id: str = "anonymous"


class TestResultOut(BaseModel):
    test_case_id: str
    passed: bool
    verdict: str
    input_data: str
    actual_output: str
    expected_output: str
    stdout: str
    stderr: str
    runtime_ms: float
    memory_kb: Optional[float]
    exit_code: Optional[int]
    timed_out: bool
    is_hidden: bool
    output_truncated: bool = False


class SubmissionOut(BaseModel):
    id: str
    problem_id: str
    user_id: str
    language: str
    verdict: str
    runtime_ms: Optional[float]
    memory_kb: Optional[float]
    test_cases_passed: int
    test_cases_total: int
    compile_output: Optional[str]
    judge_version: Optional[str]
    test_suite_version: Optional[str]
    test_results: list[TestResultOut]
    ai_review: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True

    @field_serializer("created_at")
    def _serialize_created_at(self, value: datetime) -> str:
        # SQLite has no native timezone-aware storage: SQLAlchemy round-trips
        # a DateTime(timezone=True) column as a NAIVE datetime even though it
        # was written as UTC (Submission.created_at's default is
        # datetime.now(timezone.utc)). Serializing that naive value straight
        # to JSON produces an offset-less ISO string ("...T08:39:29" with no
        # 'Z'), which every browser's `new Date(...)` parses as LOCAL time --
        # on a UTC+5:30 client that silently shows "5h ago" for a submission
        # that just happened. Every value here is UTC by construction, so a
        # naive datetime is always re-tagged as UTC, never guessed.
        aware = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        return aware.astimezone(timezone.utc).isoformat()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _xp_for_verdict(verdict: str, difficulty: str) -> int:
    if verdict != "Accepted":
        return 0
    return {"Easy": 10, "Medium": 20, "Hard": 40}.get(difficulty, 10)


async def _update_progress(
    db: AsyncSession,
    user_id: str,
    problem: Problem,
    verdict: str,
    language: str,
) -> None:
    result = await db.execute(
        select(UserProgress).where(UserProgress.user_id == user_id)
    )
    progress = result.scalar_one_or_none()
    if progress is None:
        progress = UserProgress(user_id=user_id)
        db.add(progress)

    solved = list(progress.solved_problems or [])
    attempted = list(progress.attempted_problems or [])
    lang_stats = dict(progress.language_stats or {})

    if problem.id not in attempted:
        attempted.append(problem.id)
    if verdict == "Accepted" and problem.id not in solved:
        solved.append(problem.id)
        progress.xp = (progress.xp or 0) + _xp_for_verdict(verdict, problem.difficulty)
        lang_stats[language] = lang_stats.get(language, 0) + 1

    progress.solved_problems = solved
    progress.attempted_problems = attempted
    progress.language_stats = lang_stats
    progress.last_active = datetime.now(timezone.utc).date()
    await db.flush()


# ── Endpoints ─────────────────────────────────────────────────────────────────

def _to_test_result_out(r: TestResult) -> TestResultOut:
    return TestResultOut(
        test_case_id=r.test_case_id,
        passed=r.passed,
        verdict=r.verdict,
        input_data=r.input_data,
        actual_output=r.actual_output,
        expected_output=r.expected_output,
        stdout=r.stdout,
        stderr=r.stderr,
        runtime_ms=r.runtime_ms,
        memory_kb=r.memory_kb,
        exit_code=r.exit_code,
        timed_out=r.timed_out,
        is_hidden=r.is_hidden,
        output_truncated=r.output_truncated,
    )


@router.post("", response_model=SubmissionOut, status_code=201)
async def submit(body: SubmitRequest, db: AsyncSession = Depends(get_db)) -> SubmissionOut:
    # Load problem + EVERY persisted test case (visible + hidden) -- Submit is
    # the authoritative judge run, unlike Run which only ever sees a subset.
    prob_result = await db.execute(select(Problem).where(Problem.id == body.problem_id))
    problem = prob_result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem '{body.problem_id}' not found")

    tc_result = await db.execute(
        select(TestCase)
        .where(TestCase.problem_id == body.problem_id)
        .order_by(TestCase.order)
    )
    test_cases = tc_result.scalars().all()
    if not test_cases:
        raise HTTPException(status_code=422, detail=f"Problem '{body.problem_id}' has no test cases configured")

    # Evaluate against the FULL suite (every case always runs -- see
    # evaluator.py's module docstring on why it never short-circuits).
    eval_result = await evaluate(body.code, body.language, list(test_cases))

    avg_ms = (
        eval_result.total_runtime_ms / max(len(eval_result.test_results), 1)
        if eval_result.test_results else None
    )

    test_results_out = [_to_test_result_out(r) for r in eval_result.test_results]

    # Persist submission -- code snapshot, real measured runtime/memory, and
    # the judge/test-suite versions ACTIVE AT THIS MOMENT (so a later fix to
    # this problem's test data doesn't retroactively change what an old
    # submission is compared against).
    sub = Submission(
        problem_id=body.problem_id,
        user_id=body.user_id,
        language=body.language,
        code=body.code,
        verdict=eval_result.verdict,
        runtime_ms=avg_ms,
        memory_kb=eval_result.peak_memory_kb,
        test_cases_passed=eval_result.tests_passed,
        test_cases_total=eval_result.tests_total,
        compile_output=eval_result.compile_output,
        judge_version=JUDGE_VERSION,
        test_suite_version=problem.test_suite_version or "1.0",
        test_results_json=[r.model_dump() for r in test_results_out],
    )
    db.add(sub)

    # Update problem stats
    problem.total_submissions = (problem.total_submissions or 0) + 1
    if eval_result.verdict == "Accepted":
        problem.total_accepted = (problem.total_accepted or 0) + 1
    if problem.total_submissions > 0:
        problem.acceptance_rate = round(
            problem.total_accepted / problem.total_submissions * 100, 1
        )

    # Update user progress -- ONLY Submit does this; Run never calls this path.
    await _update_progress(db, body.user_id, problem, eval_result.verdict, body.language)
    await db.flush()

    return SubmissionOut(
        id=sub.id,
        problem_id=sub.problem_id,
        user_id=sub.user_id,
        language=sub.language,
        verdict=sub.verdict,
        runtime_ms=sub.runtime_ms,
        memory_kb=sub.memory_kb,
        test_cases_passed=sub.test_cases_passed,
        test_cases_total=sub.test_cases_total,
        compile_output=sub.compile_output,
        judge_version=sub.judge_version,
        test_suite_version=sub.test_suite_version,
        test_results=test_results_out,
        ai_review=None,
        created_at=sub.created_at,
    )


def _submission_to_out(sub: Submission) -> SubmissionOut:
    # test_results_json is None for submissions made before this field existed
    # -- an honest empty list, not a fabricated re-run of historical code.
    raw_results = sub.test_results_json or []
    return SubmissionOut(
        id=sub.id,
        problem_id=sub.problem_id,
        user_id=sub.user_id,
        language=sub.language,
        verdict=sub.verdict,
        runtime_ms=sub.runtime_ms,
        memory_kb=sub.memory_kb,
        test_cases_passed=sub.test_cases_passed,
        test_cases_total=sub.test_cases_total,
        compile_output=sub.compile_output,
        judge_version=sub.judge_version,
        test_suite_version=sub.test_suite_version,
        test_results=[TestResultOut.model_validate(r) for r in raw_results],
        ai_review=sub.ai_review,
        created_at=sub.created_at,
    )


@router.get("/{submission_id}", response_model=SubmissionOut)
async def get_submission(submission_id: str, db: AsyncSession = Depends(get_db)) -> SubmissionOut:
    result = await db.execute(select(Submission).where(Submission.id == submission_id))
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    return _submission_to_out(sub)


@router.get("", response_model=list[SubmissionOut])
async def list_submissions(
    problem_id: Optional[str] = Query(None),
    user_id: str = Query("anonymous"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[SubmissionOut]:
    stmt = select(Submission).where(Submission.user_id == user_id)
    if problem_id:
        stmt = stmt.where(Submission.problem_id == problem_id)
    stmt = stmt.order_by(Submission.created_at.desc()).limit(limit)
    rows = (await db.execute(stmt)).scalars().all()
    return [_submission_to_out(r) for r in rows]


# ── Quality analysis ──────────────────────────────────────────────────────────
# Every dimension here is either real measured data or explicitly marked
# unavailable -- never a fabricated score or percentile (see
# docs/atlascode-judge-workspace.md "Submission Quality" section).

MIN_COMPARABLE_SAMPLE = 5


class QualityRuntime(BaseModel):
    median_ms: Optional[float]
    p95_ms: Optional[float]
    slowest_ms: Optional[float]
    measured_cases: int


class QualityPercentile(BaseModel):
    available: bool
    percentile: Optional[float]  # "faster than N% of comparable accepted submissions"
    comparable_count: int
    reason: Optional[str]


class SubmissionQualityOut(BaseModel):
    submission_id: str
    correctness_pct: float
    tests_passed: int
    tests_total: int
    runtime: QualityRuntime
    memory_kb: Optional[float]
    memory_available: bool
    runtime_percentile: QualityPercentile
    # Explicitly None -- complexity estimation requires an AI call this pass
    # doesn't wire up; a labeled "AI-estimated, confidence: medium" value is a
    # documented fast-follow (see docs/atlascode-judge-workspace.md), never
    # faked as a real measurement.
    complexity_estimate: Optional[str] = None
    complexity_confidence: Optional[str] = None


@router.get("/{submission_id}/quality", response_model=SubmissionQualityOut)
async def get_submission_quality(submission_id: str, db: AsyncSession = Depends(get_db)) -> SubmissionQualityOut:
    result = await db.execute(select(Submission).where(Submission.id == submission_id))
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    raw_results = sub.test_results_json or []
    runtimes = sorted(
        r["runtime_ms"] for r in raw_results if isinstance(r.get("runtime_ms"), (int, float))
    )
    runtime_stats = QualityRuntime(
        median_ms=statistics.median(runtimes) if runtimes else None,
        p95_ms=runtimes[max(0, int(len(runtimes) * 0.95) - 1)] if runtimes else None,
        slowest_ms=runtimes[-1] if runtimes else None,
        measured_cases=len(runtimes),
    )

    correctness_pct = (
        round(sub.test_cases_passed / sub.test_cases_total * 100, 1) if sub.test_cases_total else 0.0
    )

    # Percentile only computed for Accepted submissions, only against OTHER
    # accepted submissions for the same problem + language + judge_version +
    # test_suite_version -- comparing across incompatible test suites or
    # judge behavior would be a meaningless number dressed up as real data.
    percentile = QualityPercentile(available=False, percentile=None, comparable_count=0, reason=None)
    if sub.verdict == "Accepted" and sub.runtime_ms is not None:
        stmt = select(Submission.runtime_ms).where(
            Submission.problem_id == sub.problem_id,
            Submission.language == sub.language,
            Submission.verdict == "Accepted",
            Submission.judge_version == sub.judge_version,
            Submission.test_suite_version == sub.test_suite_version,
            Submission.runtime_ms.is_not(None),
            Submission.id != sub.id,
        )
        others = [row[0] for row in (await db.execute(stmt)).all()]
        if len(others) >= MIN_COMPARABLE_SAMPLE:
            faster_or_equal = sum(1 for o in others if o >= sub.runtime_ms)
            percentile = QualityPercentile(
                available=True,
                percentile=round(faster_or_equal / len(others) * 100, 1),
                comparable_count=len(others),
                reason=None,
            )
        else:
            percentile = QualityPercentile(
                available=False, percentile=None, comparable_count=len(others),
                reason="Not enough comparable accepted submissions yet",
            )

    return SubmissionQualityOut(
        submission_id=sub.id,
        correctness_pct=correctness_pct,
        tests_passed=sub.test_cases_passed,
        tests_total=sub.test_cases_total,
        runtime=runtime_stats,
        memory_kb=sub.memory_kb,
        memory_available=sub.memory_kb is not None,
        runtime_percentile=percentile,
    )
