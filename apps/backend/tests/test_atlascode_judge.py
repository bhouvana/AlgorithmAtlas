"""
AtlasCode judge tests: Run vs Submit semantics, partial-pass accuracy, hidden
test redaction, and the honest quality-analysis endpoint.

Isolated from the shared dev database: builds its own temp SQLite engine and
overrides the `get_db` FastAPI dependency, so these tests never touch
apps/backend's ./atlas.db (which real seed data lives in) and never need
manual cleanup between runs.
"""
from __future__ import annotations

import os
import tempfile
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from algorithm_atlas.database import Base, get_db
from algorithm_atlas.main import app
from algorithm_atlas.models.atlas_code import Problem, TestCase

# Async tests run automatically -- pyproject.toml sets asyncio_mode = "auto".


@pytest.fixture(scope="module")
async def test_engine():
    tmp = Path(tempfile.gettempdir()) / f"atlascode_judge_test_{os.getpid()}.db"
    tmp.unlink(missing_ok=True)
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp.as_posix()}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()
    tmp.unlink(missing_ok=True)


@pytest.fixture(scope="module")
def session_factory(test_engine):
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="module", autouse=True)
async def override_db(session_factory):
    async def _override() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.pop(get_db, None)


# A tiny, fully deterministic problem: print double the input integer.
# 3 visible cases + 2 hidden cases -- enough to exercise partial-pass and
# hidden-redaction without depending on the real 40-test seed data.
PROBLEM_ID = "test-double-it"
GOOD_SOLUTION = "x = int(input())\nprint(x * 2)\n"
WRONG_SOLUTION = "x = int(input())\nprint(x)\n"  # forgets to double -- fails every non-zero case
CRASHING_SOLUTION = "x = int(input())\nraise ValueError('boom')\n"
HANGING_SOLUTION = "import time\ntime.sleep(30)\n"
SYNTAX_ERROR_SOLUTION = "def f(:\n  pass\n"


@pytest.fixture(scope="module", autouse=True)
async def seed_problem(session_factory, override_db):
    async with session_factory() as db:
        db.add(Problem(
            id=PROBLEM_ID, title="Double It", difficulty="Easy", category="testing",
            problem_statement="Print double the input integer.",
            starter_code={"python": "x = int(input())\n"},
        ))
        cases = [
            (0, "1", "2", False),
            (1, "2", "4", False),
            (2, "0", "0", False),
            (3, "100", "200", True),
            (4, "-5", "-10", True),
        ]
        for order, inp, exp, hidden in cases:
            db.add(TestCase(
                problem_id=PROBLEM_ID, input_data=inp, expected_output=exp,
                is_hidden=hidden, order=order,
            ))
        await db.commit()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ── Run endpoint ────────────────────────────────────────────────────────────

class TestRunEndpoint:
    async def test_run_visible_all_pass(self, client: AsyncClient):
        r = await client.post(
            f"/api/v1/problems/{PROBLEM_ID}/run",
            json={"language": "python", "code": GOOD_SOLUTION, "mode": "visible"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["summary"] == {"passed": 3, "failed": 0, "total": 3, "runtime_ms": pytest.approx(body["summary"]["runtime_ms"])}
        assert len(body["cases"]) == 3
        assert all(not c["is_hidden"] for c in body["cases"])

    async def test_run_never_touches_hidden_cases(self, client: AsyncClient):
        r = await client.post(
            f"/api/v1/problems/{PROBLEM_ID}/run",
            json={"language": "python", "code": GOOD_SOLUTION, "mode": "visible"},
        )
        body = r.json()
        assert body["summary"]["total"] == 3, "Run must only ever see visible cases, never all 5"

    async def test_run_partial_pass_reports_every_case(self, client: AsyncClient):
        r = await client.post(
            f"/api/v1/problems/{PROBLEM_ID}/run",
            json={"language": "python", "code": WRONG_SOLUTION, "mode": "visible"},
        )
        body = r.json()
        # WRONG_SOLUTION prints the input unchanged: passes only the x=0 case (0*2==0)
        assert body["summary"]["passed"] == 1
        assert body["summary"]["failed"] == 2
        assert len(body["cases"]) == 3, "every visible case must be reported, not just up to the first failure"

    async def test_run_selected_single_case(self, client: AsyncClient):
        r = await client.post(
            f"/api/v1/problems/{PROBLEM_ID}/run",
            json={"language": "python", "code": GOOD_SOLUTION, "mode": "selected", "case_indices": [1]},
        )
        body = r.json()
        assert len(body["cases"]) == 1
        assert body["cases"][0]["label"] == "Case 2"

    async def test_run_custom_case_without_expected_output_is_not_fabricated(self, client: AsyncClient):
        r = await client.post(
            f"/api/v1/problems/{PROBLEM_ID}/run",
            json={
                "language": "python", "code": GOOD_SOLUTION, "mode": "custom",
                "custom_cases": [{"input_data": "7"}],
            },
        )
        body = r.json()
        case = body["cases"][0]
        assert case["has_expected"] is False
        assert case["status"] == "executed"
        assert case["actual_output"] == "14"
        assert body["summary"]["total"] == 0, "a no-expected-output case must not count toward passed/total"

    async def test_run_custom_case_with_expected_output_compares(self, client: AsyncClient):
        r = await client.post(
            f"/api/v1/problems/{PROBLEM_ID}/run",
            json={
                "language": "python", "code": GOOD_SOLUTION, "mode": "custom",
                "custom_cases": [{"input_data": "7", "expected_output": "14"}],
            },
        )
        body = r.json()
        assert body["cases"][0]["status"] == "passed"

    async def test_run_does_not_persist_submission_or_progress(self, client: AsyncClient):
        before = await client.get("/api/v1/submissions", params={"problem_id": PROBLEM_ID})
        await client.post(
            f"/api/v1/problems/{PROBLEM_ID}/run",
            json={"language": "python", "code": GOOD_SOLUTION, "mode": "visible"},
        )
        after = await client.get("/api/v1/submissions", params={"problem_id": PROBLEM_ID})
        assert len(before.json()) == len(after.json()), "Run must never create a Submission row"

    async def test_run_compile_error_structural(self, client: AsyncClient):
        r = await client.post(
            f"/api/v1/problems/{PROBLEM_ID}/run",
            json={"language": "python", "code": SYNTAX_ERROR_SOLUTION, "mode": "visible"},
        )
        body = r.json()
        # Python has no isolable compile step in this judge -- a syntax error
        # surfaces as Runtime Error, not Compilation Error (documented scope
        # boundary, see evaluator.py module docstring).
        assert body["cases"][0]["status"] == "Runtime Error"


# ── Submit endpoint ──────────────────────────────────────────────────────────

class TestSubmitEndpoint:
    async def test_submit_accepted_runs_all_five(self, client: AsyncClient):
        r = await client.post(
            "/api/v1/submissions",
            json={"problem_id": PROBLEM_ID, "language": "python", "code": GOOD_SOLUTION, "user_id": "pytest-user"},
        )
        assert r.status_code == 201
        body = r.json()
        assert body["verdict"] == "Accepted"
        assert body["test_cases_total"] == 5
        assert body["test_cases_passed"] == 5
        assert len(body["test_results"]) == 5
        assert body["judge_version"] is not None
        assert body["test_suite_version"] is not None

    async def test_submit_hidden_cases_redacted(self, client: AsyncClient):
        r = await client.post(
            "/api/v1/submissions",
            json={"problem_id": PROBLEM_ID, "language": "python", "code": GOOD_SOLUTION, "user_id": "pytest-user"},
        )
        body = r.json()
        hidden = [c for c in body["test_results"] if c["is_hidden"]]
        assert len(hidden) == 2
        for c in hidden:
            assert c["input_data"] == ""
            assert c["expected_output"] == ""
            assert c["actual_output"] == ""
            assert c["stdout"] == ""
            # Runtime IS real data, not redacted -- it's not secret content.
            assert c["runtime_ms"] > 0

    async def test_submit_wrong_answer_reports_all_cases_no_short_circuit(self, client: AsyncClient):
        r = await client.post(
            "/api/v1/submissions",
            json={"problem_id": PROBLEM_ID, "language": "python", "code": WRONG_SOLUTION, "user_id": "pytest-user-2"},
        )
        body = r.json()
        assert body["verdict"] == "Wrong Answer"
        assert body["test_cases_passed"] == 1  # only the x=0 case
        assert len(body["test_results"]) == 5, "every case must run even though case 1 already fails"

    async def test_submit_runtime_error(self, client: AsyncClient):
        r = await client.post(
            "/api/v1/submissions",
            json={"problem_id": PROBLEM_ID, "language": "python", "code": CRASHING_SOLUTION, "user_id": "pytest-user-3"},
        )
        body = r.json()
        assert body["verdict"] == "Runtime Error"

    async def test_submit_updates_progress_but_run_does_not(self, client: AsyncClient):
        user = "pytest-progress-user"
        await client.get(f"/api/v1/progress/{user}")  # ensure lazy-create path doesn't error
        await client.post(
            f"/api/v1/problems/{PROBLEM_ID}/run",
            json={"language": "python", "code": GOOD_SOLUTION, "mode": "visible"},
        )
        prog_after_run = await client.get(f"/api/v1/progress/{user}")
        assert PROBLEM_ID not in prog_after_run.json()["attempted_problems"]

        await client.post(
            "/api/v1/submissions",
            json={"problem_id": PROBLEM_ID, "language": "python", "code": GOOD_SOLUTION, "user_id": user},
        )
        prog_after_submit = await client.get(f"/api/v1/progress/{user}")
        assert PROBLEM_ID in prog_after_submit.json()["solved_problems"]

    async def test_submission_persists_and_reloads_with_redaction_intact(self, client: AsyncClient):
        submit = await client.post(
            "/api/v1/submissions",
            json={"problem_id": PROBLEM_ID, "language": "python", "code": GOOD_SOLUTION, "user_id": "pytest-reload-user"},
        )
        sub_id = submit.json()["id"]
        fetched = await client.get(f"/api/v1/submissions/{sub_id}")
        body = fetched.json()
        assert len(body["test_results"]) == 5
        hidden = [c for c in body["test_results"] if c["is_hidden"]]
        assert all(c["actual_output"] == "" for c in hidden)

    async def test_submit_no_test_cases_returns_422(self, client: AsyncClient, session_factory):
        async with session_factory() as db:
            db.add(Problem(
                id="test-empty-problem", title="Empty", difficulty="Easy", category="testing",
                problem_statement="No tests.", starter_code={"python": ""},
            ))
            await db.commit()
        r = await client.post(
            "/api/v1/submissions",
            json={"problem_id": "test-empty-problem", "language": "python", "code": "print(1)", "user_id": "pytest-user"},
        )
        assert r.status_code == 422


# ── Quality endpoint ─────────────────────────────────────────────────────────

class TestQualityEndpoint:
    async def test_quality_reflects_real_measured_data(self, client: AsyncClient):
        submit = await client.post(
            "/api/v1/submissions",
            json={"problem_id": PROBLEM_ID, "language": "python", "code": GOOD_SOLUTION, "user_id": "pytest-quality-user"},
        )
        sub_id = submit.json()["id"]
        r = await client.get(f"/api/v1/submissions/{sub_id}/quality")
        body = r.json()
        assert body["correctness_pct"] == 100.0
        assert body["runtime"]["measured_cases"] == 5
        assert body["memory_available"] is True
        assert body["complexity_estimate"] is None, "must not fabricate a complexity estimate"

    async def test_quality_percentile_unavailable_below_sample_threshold(
        self, client: AsyncClient, session_factory,
    ):
        # Isolated problem so this submission has zero comparable accepted
        # submissions -- other tests in this module accumulate 5+ Accepted
        # submissions against PROBLEM_ID, which would make percentile
        # available there (a real, correct behavior, just not what this
        # specific test needs to verify).
        solo_problem_id = "test-percentile-isolation"
        async with session_factory() as db:
            db.add(Problem(
                id=solo_problem_id, title="Solo", difficulty="Easy", category="testing",
                problem_statement="Print double.", starter_code={"python": ""},
            ))
            db.add(TestCase(
                problem_id=solo_problem_id, input_data="1", expected_output="2",
                is_hidden=False, order=0,
            ))
            await db.commit()

        submit = await client.post(
            "/api/v1/submissions",
            json={"problem_id": solo_problem_id, "language": "python", "code": GOOD_SOLUTION, "user_id": "pytest-quality-user-2"},
        )
        sub_id = submit.json()["id"]
        r = await client.get(f"/api/v1/submissions/{sub_id}/quality")
        body = r.json()
        assert body["runtime_percentile"]["available"] is False
        assert body["runtime_percentile"]["reason"] is not None
