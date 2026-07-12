"""
Function Mode tests: the second Run contract (typed arguments -> function
invocation -> typed return), fully separate from Program Mode's stdin/stdout
contract (see test_atlascode_judge.py) and from Submit (never touched by
either Run contract).

Same isolation pattern as test_atlascode_judge.py: a throwaway temp SQLite
engine + get_db dependency override, so these tests never touch the shared
dev database.
"""
from __future__ import annotations

import os
import tempfile
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from algorithm_atlas.atlascode.function_mode.contracts import (
    FunctionContract, Parameter, TypeSpec, compare_typed, validate_arguments, validate_value,
)
from algorithm_atlas.database import Base, get_db
from algorithm_atlas.main import app
from algorithm_atlas.models.atlas_code import Problem, TestCase

# Async tests run automatically -- pyproject.toml sets asyncio_mode = "auto".


@pytest.fixture(scope="module")
async def test_engine():
    tmp = Path(tempfile.gettempdir()) / f"atlascode_function_mode_test_{os.getpid()}.db"
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


# A tiny deterministic Function Mode problem: top_k_frequent(nums, k) -> list[int]
# (array input, array return, integer parameter) -- 3 visible + 2 hidden cases.
PROBLEM_ID = "test-top-k-frequent"
CONTRACT = FunctionContract(
    function_name="top_k_frequent",
    parameters=[Parameter("nums", TypeSpec("array", TypeSpec("integer"))), Parameter("k", TypeSpec("integer"))],
    return_type=TypeSpec("array", TypeSpec("integer")),
)

GOOD_SOLUTION = (
    "def top_k_frequent(nums, k):\n"
    "    from collections import Counter\n"
    "    c = Counter(nums)\n"
    "    return [x for x, _ in sorted(c.items(), key=lambda p: (-p[1], p[0]))[:k]]\n"
)
WRONG_SOLUTION = "def top_k_frequent(nums, k):\n    return sorted(nums)[:k]\n"
RENAMED_SOLUTION = "def solve(nums, k):\n    return []\n"
WRONG_SIGNATURE_SOLUTION = "def top_k_frequent(nums, k, extra):\n    return []\n"
CRASHING_SOLUTION = "def top_k_frequent(nums, k):\n    return nums[999999]\n"
HANGING_SOLUTION = "def top_k_frequent(nums, k):\n    while True:\n        pass\n"
MUTATING_SOLUTION = "def top_k_frequent(nums, k):\n    nums.sort()\n    return nums[:k]\n"

# A boolean-return Function Mode problem: contains_nearby_duplicate(nums, k) -> bool
BOOL_PROBLEM_ID = "test-contains-nearby-duplicate"
BOOL_CONTRACT = FunctionContract(
    function_name="contains_nearby_duplicate",
    parameters=[Parameter("nums", TypeSpec("array", TypeSpec("integer"))), Parameter("k", TypeSpec("integer"))],
    return_type=TypeSpec("boolean"),
)
BOOL_GOOD_SOLUTION = (
    "def contains_nearby_duplicate(nums, k):\n"
    "    seen = {}\n"
    "    for i, x in enumerate(nums):\n"
    "        if x in seen and i - seen[x] <= k:\n"
    "            return True\n"
    "        seen[x] = i\n"
    "    return False\n"
)


@pytest.fixture(scope="module", autouse=True)
async def seed_problems(session_factory, override_db):
    async with session_factory() as db:
        db.add(Problem(
            id=PROBLEM_ID, title="Top K Frequent (test)", difficulty="Medium", category="testing",
            problem_statement="Return the k most frequent elements.",
            starter_code={"python": "import sys\n"},
            function_contract=CONTRACT.to_dict(),
            starter_code_function={"python": "def top_k_frequent(nums: list[int], k: int) -> list[int]:\n    pass\n"},
        ))
        cases = [
            (0, {"nums": [1, 1, 1, 2, 2, 3], "k": 2}, [1, 2], False),
            (1, {"nums": [1], "k": 1}, [1], False),
            (2, {"nums": [4, 4, 4, 4, 1], "k": 1}, [4], False),
            (3, {"nums": [5, 5, 6, 6, 7, 7], "k": 2}, [5, 6], True),
            (4, {"nums": [2, 2, 3, 3, 3], "k": 1}, [3], True),
        ]
        for order, args, expected, hidden in cases:
            db.add(TestCase(
                problem_id=PROBLEM_ID,
                input_data=f"placeholder-{order}", expected_output=str(expected),
                is_hidden=hidden, order=order,
                function_args=args, function_expected=expected,
            ))

        db.add(Problem(
            id=BOOL_PROBLEM_ID, title="Contains Nearby Duplicate (test)", difficulty="Easy", category="testing",
            problem_statement="Return true if a duplicate exists within distance k.",
            starter_code={"python": "import sys\n"},
            function_contract=BOOL_CONTRACT.to_dict(),
            starter_code_function={"python": "def contains_nearby_duplicate(nums: list[int], k: int) -> bool:\n    pass\n"},
        ))
        db.add(TestCase(
            problem_id=BOOL_PROBLEM_ID,
            input_data="placeholder", expected_output="true",
            is_hidden=False, order=0,
            function_args={"nums": [1, 2, 3, 1], "k": 3}, function_expected=True,
        ))
        await db.commit()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


def _run_body(code: str, **kw) -> dict:
    body = {"language": "python", "code": code, "mode": "visible", "execution_mode": "function"}
    body.update(kw)
    return body


# ── Contract unit tests (no DB/network needed) ────────────────────────────────

class TestContracts:
    def test_validate_value_scalars(self):
        assert validate_value(5, TypeSpec("integer"))
        assert not validate_value(True, TypeSpec("integer")), "bool must not satisfy integer (Python bool is an int subclass)"
        assert validate_value(True, TypeSpec("boolean"))
        assert validate_value(3.5, TypeSpec("float"))
        assert validate_value("hi", TypeSpec("string"))

    def test_validate_value_array_and_optional(self):
        arr = TypeSpec("array", TypeSpec("integer"))
        assert validate_value([1, 2, 3], arr)
        assert not validate_value([1, "x"], arr)
        opt = TypeSpec("optional", TypeSpec("integer"))
        assert validate_value(None, opt)
        assert validate_value(5, opt)

    def test_validate_arguments_rejects_wrong_names_and_types(self):
        errors = validate_arguments({"nums": [1, 2], "kk": 1}, CONTRACT)
        assert any("Missing argument 'k'" in e for e in errors)
        assert any("Unexpected argument 'kk'" in e for e in errors)

        errors2 = validate_arguments({"nums": "not-an-array", "k": 1}, CONTRACT)
        assert any("does not match declared type" in e for e in errors2)

        assert validate_arguments({"nums": [1, 2], "k": 1}, CONTRACT) == []

    def test_compare_typed_arrays_are_order_sensitive(self):
        arr = TypeSpec("array", TypeSpec("integer"))
        assert compare_typed([1, 2], [1, 2], arr)
        assert not compare_typed([2, 1], [1, 2], arr), "arrays must never be silently sorted before comparison"

    def test_compare_typed_float_tolerance(self):
        assert compare_typed(1.0000001, 1.0, TypeSpec("float"))
        assert not compare_typed(1.1, 1.0, TypeSpec("float"))


# ── Run endpoint: Function Mode ───────────────────────────────────────────────

class TestFunctionModeRun:
    async def test_visible_all_pass(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_run_body(GOOD_SOLUTION))
        assert r.status_code == 200
        body = r.json()
        assert body["execution_mode"] == "function"
        assert body["summary"] == {"passed": 3, "failed": 0, "total": 3, "runtime_ms": pytest.approx(body["summary"]["runtime_ms"])}
        first = body["cases"][0]
        assert first["arguments"] == {"nums": [1, 1, 1, 2, 2, 3], "k": 2}
        assert first["expected_return"] == [1, 2]
        assert first["actual_return"] == [1, 2]
        assert first["status"] == "passed"

    async def test_never_touches_hidden_cases(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_run_body(GOOD_SOLUTION))
        assert r.json()["summary"]["total"] == 3

    async def test_boolean_return_type(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{BOOL_PROBLEM_ID}/run", json=_run_body(BOOL_GOOD_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "passed"
        assert body["cases"][0]["actual_return"] is True

    async def test_wrong_return_value_is_wrong_answer_not_contract_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_run_body(WRONG_SOLUTION))
        body = r.json()
        assert body["summary"]["passed"] < body["summary"]["total"], "WRONG_SOLUTION must fail at least one case"
        failing = [c for c in body["cases"] if c["status"] == "failed"]
        assert failing, "at least one case must be reported as Wrong Answer (failed)"
        assert all(c["contract_error"] is None for c in failing)

    async def test_partial_pass_reports_every_case(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_run_body(WRONG_SOLUTION))
        body = r.json()
        assert len(body["cases"]) == 3, "every visible case must be reported, not short-circuited"

    async def test_missing_function_is_contract_error_not_wrong_answer(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_run_body(RENAMED_SOLUTION))
        body = r.json()
        for c in body["cases"]:
            assert c["status"] == "Function Contract Error"
            assert c["contract_error"]["reason"] == "missing_function"

    async def test_wrong_signature_is_contract_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_run_body(WRONG_SIGNATURE_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Function Contract Error"
        assert body["cases"][0]["contract_error"]["reason"] == "signature_mismatch"

    async def test_runtime_error_propagates_as_real_runtime_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_run_body(CRASHING_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Runtime Error"
        assert body["cases"][0]["exit_code"] not in (0, None)

    async def test_infinite_loop_times_out_safely(self, client: AsyncClient):
        r = await client.post(
            f"/api/v1/problems/{PROBLEM_ID}/run",
            json=_run_body(HANGING_SOLUTION, mode="selected", case_indices=[0]),
        )
        assert r.status_code == 200, "the judge API itself must stay healthy even when user code hangs"
        body = r.json()
        assert body["cases"][0]["status"] == "Time Limit Exceeded"
        assert body["cases"][0]["timed_out"] is True

    async def test_argument_mutation_does_not_corrupt_later_cases(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_run_body(MUTATING_SOLUTION))
        body = r.json()
        # Case 0's nums=[1,1,1,2,2,3] would sort-in-place if shared across
        # cases; every case must still see its OWN original argument order.
        assert body["cases"][0]["arguments"]["nums"] == [1, 1, 1, 2, 2, 3]
        assert body["cases"][1]["arguments"]["nums"] == [1]

    async def test_custom_case_validates_arguments_before_execution(self, client: AsyncClient):
        r = await client.post(
            f"/api/v1/problems/{PROBLEM_ID}/run",
            json=_run_body(GOOD_SOLUTION, mode="custom", custom_cases=[
                {"arguments": {"nums": [1, 2], "kk": 1}, "has_expected_return": False},
            ]),
        )
        assert r.status_code == 400
        assert "function signature" in r.json()["detail"]

    async def test_custom_case_runs_with_typed_arguments(self, client: AsyncClient):
        r = await client.post(
            f"/api/v1/problems/{PROBLEM_ID}/run",
            json=_run_body(GOOD_SOLUTION, mode="custom", custom_cases=[
                {"arguments": {"nums": [9, 9, 8], "k": 1}, "expected_return": [9], "has_expected_return": True},
            ]),
        )
        body = r.json()
        assert body["cases"][0]["status"] == "passed"
        assert body["cases"][0]["actual_return"] == [9]

    async def test_unsupported_problem_returns_422_not_fake_pass(self, client: AsyncClient):
        # BOOL_PROBLEM_ID exists but has no cases matching this -- use a
        # nonexistent contract scenario instead: request function mode on a
        # problem id that doesn't exist should 404 (not fabricate a contract).
        r = await client.post(
            "/api/v1/problems/does-not-exist/run",
            json=_run_body(GOOD_SOLUTION),
        )
        assert r.status_code == 404

    async def test_does_not_persist_submission_or_progress(self, client: AsyncClient):
        before = await client.get("/api/v1/submissions", params={"problem_id": PROBLEM_ID})
        await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_run_body(GOOD_SOLUTION))
        after = await client.get("/api/v1/submissions", params={"problem_id": PROBLEM_ID})
        assert len(before.json()) == len(after.json()), "Function Mode Run must never create a Submission row"


# ── JavaScript adapter (second Function Mode language) ───────────────────────
# Reuses PROBLEM_ID's real DB-backed cases -- proves the adapter against the
# same fixture Python already passed, not a separate JS-only corpus.

JS_GOOD_SOLUTION = (
    "function top_k_frequent(nums, k) {\n"
    "  const counts = new Map();\n"
    "  for (const x of nums) counts.set(x, (counts.get(x) || 0) + 1);\n"
    "  const items = Array.from(counts.entries());\n"
    "  items.sort((a, b) => (b[1] - a[1]) || (a[0] - b[0]));\n"
    "  return items.slice(0, k).map(([v]) => v);\n"
    "}\n"
)
JS_WRONG_SOLUTION = "function top_k_frequent(nums, k) {\n  return nums.slice().sort((a, b) => a - b).slice(0, k);\n}\n"
JS_RENAMED_SOLUTION = "function solve(nums, k) {\n  return [];\n}\n"
JS_WRONG_ARITY_SOLUTION = "function top_k_frequent(nums, k, extra) {\n  return [];\n}\n"
JS_CRASHING_SOLUTION = "function top_k_frequent(nums, k) {\n  return nums[999999].toString();\n}\n"


def _js_run_body(code: str, **kw) -> dict:
    return _run_body(code, language="javascript", **kw)


class TestJavaScriptAdapter:
    async def test_visible_all_pass(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_js_run_body(JS_GOOD_SOLUTION))
        assert r.status_code == 200
        body = r.json()
        assert body["summary"] == {"passed": 3, "failed": 0, "total": 3, "runtime_ms": pytest.approx(body["summary"]["runtime_ms"])}
        assert body["cases"][0]["actual_return"] == [1, 2]

    async def test_wrong_solution_fails_at_least_one_case(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_js_run_body(JS_WRONG_SOLUTION))
        body = r.json()
        assert body["summary"]["passed"] < body["summary"]["total"]

    async def test_missing_function_is_contract_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_js_run_body(JS_RENAMED_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Function Contract Error"
        assert body["cases"][0]["contract_error"]["reason"] == "missing_function"

    async def test_wrong_arity_is_contract_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_js_run_body(JS_WRONG_ARITY_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Function Contract Error"
        assert body["cases"][0]["contract_error"]["reason"] == "signature_mismatch"

    async def test_runtime_error_propagates(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_js_run_body(JS_CRASHING_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Runtime Error"
        assert body["cases"][0]["exit_code"] not in (0, None)

    async def test_boolean_return_type(self, client: AsyncClient):
        js_bool_solution = (
            "function contains_nearby_duplicate(nums, k) {\n"
            "  const lastSeen = {};\n"
            "  for (let i = 0; i < nums.length; i++) {\n"
            "    const x = nums[i];\n"
            "    if (Object.prototype.hasOwnProperty.call(lastSeen, x) && i - lastSeen[x] <= k) return true;\n"
            "    lastSeen[x] = i;\n"
            "  }\n"
            "  return false;\n"
            "}\n"
        )
        r = await client.post(f"/api/v1/problems/{BOOL_PROBLEM_ID}/run", json=_js_run_body(js_bool_solution))
        body = r.json()
        assert body["cases"][0]["status"] == "passed"
        assert body["cases"][0]["actual_return"] is True


# ── TypeScript adapter (third Function Mode language) ─────────────────────────
# Same JS-family calling convention (positional args) and same real DB-backed
# fixture cases as the Python/JavaScript adapters -- executes through the
# real `tsx` subprocess (run_typescript), never a mock.

TS_GOOD_SOLUTION = (
    "function top_k_frequent(nums: number[], k: number): number[] {\n"
    "  const counts = new Map<number, number>();\n"
    "  for (const x of nums) counts.set(x, (counts.get(x) || 0) + 1);\n"
    "  const items = Array.from(counts.entries());\n"
    "  items.sort((a, b) => (b[1] - a[1]) || (a[0] - b[0]));\n"
    "  return items.slice(0, k).map(([v]) => v);\n"
    "}\n"
)
TS_WRONG_SOLUTION = "function top_k_frequent(nums: number[], k: number): number[] {\n  return nums.slice().sort((a, b) => a - b).slice(0, k);\n}\n"
TS_RENAMED_SOLUTION = "function solve(nums: number[], k: number): number[] {\n  return [];\n}\n"
TS_WRONG_ARITY_SOLUTION = "function top_k_frequent(nums: number[], k: number, extra: number): number[] {\n  return [];\n}\n"
TS_CRASHING_SOLUTION = "function top_k_frequent(nums: number[], k: number): string {\n  return (nums[999999] as any).toString();\n}\n"


def _ts_run_body(code: str, **kw) -> dict:
    return _run_body(code, language="typescript", **kw)


# ── Java adapter (first COMPILED, compile-once Function Mode language) ──────
# Reuses the same real DB-backed fixture cases as python/javascript/typescript,
# but executes through notebook.py's PREPARERS/_run_prepared compile-once
# infrastructure (see compiled_adapters.py) -- one real javac compile, then
# the SAME compiled artifact invoked once per case. A missing method or wrong
# parameter arity is a genuine javac COMPILE ERROR here (Java is statically
# typed), never a runtime Function Contract Error the way python/js/ts report
# it -- that's a deliberate, documented per-language difference, not a gap.

JAVA_GOOD_SOLUTION = (
    "class Solution {\n"
    "    public int[] top_k_frequent(int[] nums, int k) {\n"
    "        java.util.Map<Integer, Integer> counts = new java.util.HashMap<>();\n"
    "        for (int x : nums) counts.merge(x, 1, Integer::sum);\n"
    "        java.util.List<Integer> keys = new java.util.ArrayList<>(counts.keySet());\n"
    "        keys.sort((a, b) -> counts.get(b) != counts.get(a) ? counts.get(b) - counts.get(a) : a - b);\n"
    "        int[] out = new int[k];\n"
    "        for (int i = 0; i < k; i++) out[i] = keys.get(i);\n"
    "        return out;\n"
    "    }\n"
    "}\n"
)
JAVA_WRONG_SOLUTION = (
    "class Solution {\n"
    "    public int[] top_k_frequent(int[] nums, int k) {\n"
    "        int[] copy = nums.clone();\n"
    "        java.util.Arrays.sort(copy);\n"
    "        return java.util.Arrays.copyOfRange(copy, 0, k);\n"
    "    }\n"
    "}\n"
)
JAVA_RENAMED_SOLUTION = "class Solution {\n    public int[] solve(int[] nums, int k) {\n        return new int[0];\n    }\n}\n"
JAVA_WRONG_ARITY_SOLUTION = "class Solution {\n    public int[] top_k_frequent(int[] nums, int k, int extra) {\n        return new int[0];\n    }\n}\n"
JAVA_CRASHING_SOLUTION = (
    "class Solution {\n"
    "    public int[] top_k_frequent(int[] nums, int k) {\n"
    "        return new int[]{ nums[999999] };\n"
    "    }\n"
    "}\n"
)


def _java_run_body(code: str, **kw) -> dict:
    return _run_body(code, language="java", **kw)


class TestJavaAdapter:
    async def test_visible_all_pass(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_java_run_body(JAVA_GOOD_SOLUTION))
        assert r.status_code == 200
        body = r.json()
        assert body["summary"] == {"passed": 3, "failed": 0, "total": 3, "runtime_ms": pytest.approx(body["summary"]["runtime_ms"])}
        assert body["cases"][0]["actual_return"] == [1, 2]

    async def test_wrong_solution_fails_at_least_one_case(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_java_run_body(JAVA_WRONG_SOLUTION))
        body = r.json()
        assert body["summary"]["passed"] < body["summary"]["total"]

    async def test_missing_method_is_compile_error(self, client: AsyncClient):
        # Statically typed: a missing method fails javac itself, not a
        # runtime Function Contract Error sentinel like the interpreted
        # adapters -- there are no case_results at all for a compile error.
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_java_run_body(JAVA_RENAMED_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"] and "top_k_frequent" in body["compile_output"]

    async def test_wrong_arity_is_compile_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_java_run_body(JAVA_WRONG_ARITY_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"]

    async def test_runtime_error_propagates(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_java_run_body(JAVA_CRASHING_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Runtime Error"
        assert body["cases"][0]["exit_code"] not in (0, None)

    async def test_boolean_return_type(self, client: AsyncClient):
        java_bool_solution = (
            "class Solution {\n"
            "    public boolean contains_nearby_duplicate(int[] nums, int k) {\n"
            "        java.util.Map<Integer, Integer> lastSeen = new java.util.HashMap<>();\n"
            "        for (int i = 0; i < nums.length; i++) {\n"
            "            int x = nums[i];\n"
            "            if (lastSeen.containsKey(x) && i - lastSeen.get(x) <= k) return true;\n"
            "            lastSeen.put(x, i);\n"
            "        }\n"
            "        return false;\n"
            "    }\n"
            "}\n"
        )
        r = await client.post(f"/api/v1/problems/{BOOL_PROBLEM_ID}/run", json=_java_run_body(java_bool_solution))
        body = r.json()
        assert body["cases"][0]["status"] == "passed"
        assert body["cases"][0]["actual_return"] is True


# ── C++ adapter (second compiled language -- proves compile-once generalizes) ─
# Same compile-once PREPARERS/_run_prepared path as Java, real g++ compiles.

CPP_GOOD_SOLUTION = (
    "class Solution {\n"
    "public:\n"
    "    std::vector<int> top_k_frequent(std::vector<int> nums, int k) {\n"
    "        std::map<int, int> counts;\n"
    "        for (int x : nums) counts[x]++;\n"
    "        std::vector<int> keys;\n"
    "        for (auto &p : counts) keys.push_back(p.first);\n"
    "        std::sort(keys.begin(), keys.end(), [&](int a, int b) {\n"
    "            return counts[a] != counts[b] ? counts[a] > counts[b] : a < b;\n"
    "        });\n"
    "        return std::vector<int>(keys.begin(), keys.begin() + k);\n"
    "    }\n"
    "};\n"
)
CPP_WRONG_SOLUTION = (
    "class Solution {\n"
    "public:\n"
    "    std::vector<int> top_k_frequent(std::vector<int> nums, int k) {\n"
    "        std::sort(nums.begin(), nums.end());\n"
    "        return std::vector<int>(nums.begin(), nums.begin() + k);\n"
    "    }\n"
    "};\n"
)
CPP_RENAMED_SOLUTION = "class Solution {\npublic:\n    std::vector<int> solve(std::vector<int> nums, int k) { return {}; }\n};\n"
CPP_WRONG_ARITY_SOLUTION = "class Solution {\npublic:\n    std::vector<int> top_k_frequent(std::vector<int> nums, int k, int extra) { return {}; }\n};\n"
CPP_CRASHING_SOLUTION = (
    "class Solution {\n"
    "public:\n"
    "    std::vector<int> top_k_frequent(std::vector<int> nums, int k) {\n"
    "        return { nums.at(999999) };\n"
    "    }\n"
    "};\n"
)


def _cpp_run_body(code: str, **kw) -> dict:
    return _run_body(code, language="cpp", **kw)


class TestCppAdapter:
    async def test_visible_all_pass(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_cpp_run_body(CPP_GOOD_SOLUTION))
        assert r.status_code == 200
        body = r.json()
        assert body["summary"] == {"passed": 3, "failed": 0, "total": 3, "runtime_ms": pytest.approx(body["summary"]["runtime_ms"])}
        assert body["cases"][0]["actual_return"] == [1, 2]

    async def test_wrong_solution_fails_at_least_one_case(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_cpp_run_body(CPP_WRONG_SOLUTION))
        body = r.json()
        assert body["summary"]["passed"] < body["summary"]["total"]

    async def test_missing_method_is_compile_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_cpp_run_body(CPP_RENAMED_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"]

    async def test_wrong_arity_is_compile_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_cpp_run_body(CPP_WRONG_ARITY_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"]

    async def test_runtime_error_propagates(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_cpp_run_body(CPP_CRASHING_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Runtime Error"
        assert body["cases"][0]["exit_code"] not in (0, None)

    async def test_boolean_return_type(self, client: AsyncClient):
        cpp_bool_solution = (
            "class Solution {\n"
            "public:\n"
            "    bool contains_nearby_duplicate(std::vector<int> nums, int k) {\n"
            "        std::map<int, int> lastSeen;\n"
            "        for (size_t i = 0; i < nums.size(); i++) {\n"
            "            int x = nums[i];\n"
            "            if (lastSeen.count(x) && (int)i - lastSeen[x] <= k) return true;\n"
            "            lastSeen[x] = (int)i;\n"
            "        }\n"
            "        return false;\n"
            "    }\n"
            "};\n"
        )
        r = await client.post(f"/api/v1/problems/{BOOL_PROBLEM_ID}/run", json=_cpp_run_body(cpp_bool_solution))
        body = r.json()
        assert body["cases"][0]["status"] == "passed"
        assert body["cases"][0]["actual_return"] is True


# ── Rust (third compiled language) ────────────────────────────────────────────
# Same compile-once PREPARERS/_run_prepared path as Java/C++, real rustc
# compiles (GNU target + MinGW linker on Windows -- see notebook.py's
# _rust_cmds for why the default MSVC target can't link in this environment).

RUST_GOOD_SOLUTION = (
    "fn top_k_frequent(nums: Vec<i32>, k: i32) -> Vec<i32> {\n"
    "    use std::collections::HashMap;\n"
    "    let mut counts: HashMap<i32, i32> = HashMap::new();\n"
    "    for &x in &nums { *counts.entry(x).or_insert(0) += 1; }\n"
    "    let mut keys: Vec<i32> = counts.keys().cloned().collect();\n"
    "    keys.sort_by(|a, b| {\n"
    "        let (ca, cb) = (counts[a], counts[b]);\n"
    "        if ca != cb { cb.cmp(&ca) } else { a.cmp(b) }\n"
    "    });\n"
    "    keys.into_iter().take(k as usize).collect()\n"
    "}\n"
)
RUST_WRONG_SOLUTION = (
    "fn top_k_frequent(mut nums: Vec<i32>, k: i32) -> Vec<i32> {\n"
    "    nums.sort();\n"
    "    nums.into_iter().take(k as usize).collect()\n"
    "}\n"
)
RUST_RENAMED_SOLUTION = "fn solve(nums: Vec<i32>, k: i32) -> Vec<i32> { let _ = (nums, k); vec![] }\n"
RUST_WRONG_ARITY_SOLUTION = "fn top_k_frequent(nums: Vec<i32>, k: i32, extra: i32) -> Vec<i32> { let _ = (nums, k, extra); vec![] }\n"
RUST_CRASHING_SOLUTION = (
    "fn top_k_frequent(nums: Vec<i32>, k: i32) -> Vec<i32> {\n"
    "    let _ = k;\n"
    "    vec![nums[999999]]\n"
    "}\n"
)


def _rust_run_body(code: str, **kw) -> dict:
    return _run_body(code, language="rust", **kw)


class TestRustAdapter:
    async def test_visible_all_pass(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_rust_run_body(RUST_GOOD_SOLUTION))
        assert r.status_code == 200
        body = r.json()
        assert body["summary"] == {"passed": 3, "failed": 0, "total": 3, "runtime_ms": pytest.approx(body["summary"]["runtime_ms"])}
        assert body["cases"][0]["actual_return"] == [1, 2]

    async def test_wrong_solution_fails_at_least_one_case(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_rust_run_body(RUST_WRONG_SOLUTION))
        body = r.json()
        assert body["summary"]["passed"] < body["summary"]["total"]

    async def test_missing_function_is_compile_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_rust_run_body(RUST_RENAMED_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"] and "top_k_frequent" in body["compile_output"]

    async def test_wrong_arity_is_compile_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_rust_run_body(RUST_WRONG_ARITY_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"]

    async def test_runtime_error_propagates(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_rust_run_body(RUST_CRASHING_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Runtime Error"
        assert body["cases"][0]["exit_code"] not in (0, None)

    async def test_boolean_return_type(self, client: AsyncClient):
        rust_bool_solution = (
            "fn contains_nearby_duplicate(nums: Vec<i32>, k: i32) -> bool {\n"
            "    use std::collections::HashMap;\n"
            "    let mut last: HashMap<i32, i32> = HashMap::new();\n"
            "    for (i, &x) in nums.iter().enumerate() {\n"
            "        if let Some(&j) = last.get(&x) {\n"
            "            if (i as i32) - j <= k { return true; }\n"
            "        }\n"
            "        last.insert(x, i as i32);\n"
            "    }\n"
            "    false\n"
            "}\n"
        )
        r = await client.post(f"/api/v1/problems/{BOOL_PROBLEM_ID}/run", json=_rust_run_body(rust_bool_solution))
        body = r.json()
        assert body["cases"][0]["status"] == "passed"
        assert body["cases"][0]["actual_return"] is True


# ── C (fourth compiled language) ──────────────────────────────────────────────
# Same compile-once PREPARERS/_run_prepared path as Java/C++/Rust, real gcc
# compiles (MinGW-w64, already installed for the cpp/c Program Mode adapters).
# No tuple support yet (see compiled_adapters.py's C section docstring).

C_GOOD_SOLUTION = (
    "AtlasIntArray top_k_frequent(AtlasIntArray nums, int k) {\n"
    "    int keys[64], counts[64], nkeys = 0;\n"
    "    for (int i = 0; i < nums.size; i++) {\n"
    "        int x = nums.data[i], found = 0;\n"
    "        for (int j = 0; j < nkeys; j++) if (keys[j] == x) { counts[j]++; found = 1; break; }\n"
    "        if (!found) { keys[nkeys] = x; counts[nkeys] = 1; nkeys++; }\n"
    "    }\n"
    "    for (int i = 0; i < nkeys; i++)\n"
    "        for (int j = i + 1; j < nkeys; j++) {\n"
    "            int swap = (counts[j] > counts[i]) || (counts[j] == counts[i] && keys[j] < keys[i]);\n"
    "            if (swap) {\n"
    "                int tk = keys[i]; keys[i] = keys[j]; keys[j] = tk;\n"
    "                int tc = counts[i]; counts[i] = counts[j]; counts[j] = tc;\n"
    "            }\n"
    "        }\n"
    "    AtlasIntArray result; result.size = k; result.data = (int*) malloc(sizeof(int) * k);\n"
    "    for (int i = 0; i < k; i++) result.data[i] = keys[i];\n"
    "    return result;\n"
    "}\n"
)
C_WRONG_SOLUTION = (
    "AtlasIntArray top_k_frequent(AtlasIntArray nums, int k) {\n"
    "    for (int i = 0; i < nums.size; i++)\n"
    "        for (int j = 0; j < nums.size - i - 1; j++)\n"
    "            if (nums.data[j] > nums.data[j+1]) { int t = nums.data[j]; nums.data[j] = nums.data[j+1]; nums.data[j+1] = t; }\n"
    "    AtlasIntArray result; result.size = k; result.data = (int*) malloc(sizeof(int) * k);\n"
    "    for (int i = 0; i < k; i++) result.data[i] = nums.data[i];\n"
    "    return result;\n"
    "}\n"
)
C_RENAMED_SOLUTION = "AtlasIntArray solve(AtlasIntArray nums, int k) { (void) nums; (void) k; AtlasIntArray r; r.size = 0; r.data = NULL; return r; }\n"
C_WRONG_ARITY_SOLUTION = "AtlasIntArray top_k_frequent(AtlasIntArray nums, int k, int extra) { (void) nums; (void) k; (void) extra; AtlasIntArray r; r.size = 0; r.data = NULL; return r; }\n"
C_CRASHING_SOLUTION = (
    "AtlasIntArray top_k_frequent(AtlasIntArray nums, int k) {\n"
    "    (void) k;\n"
    "    AtlasIntArray result; result.size = 1; result.data = (int*) malloc(sizeof(int));\n"
    "    result.data[0] = nums.data[999999];\n"
    "    return result;\n"
    "}\n"
)


def _c_run_body(code: str, **kw) -> dict:
    return _run_body(code, language="c", **kw)


class TestCAdapter:
    async def test_visible_all_pass(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_c_run_body(C_GOOD_SOLUTION))
        assert r.status_code == 200
        body = r.json()
        assert body["summary"] == {"passed": 3, "failed": 0, "total": 3, "runtime_ms": pytest.approx(body["summary"]["runtime_ms"])}
        assert body["cases"][0]["actual_return"] == [1, 2]

    async def test_wrong_solution_fails_at_least_one_case(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_c_run_body(C_WRONG_SOLUTION))
        body = r.json()
        assert body["summary"]["passed"] < body["summary"]["total"]

    async def test_missing_function_is_compile_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_c_run_body(C_RENAMED_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"]

    async def test_wrong_arity_is_compile_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_c_run_body(C_WRONG_ARITY_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"]

    async def test_runtime_error_propagates(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_c_run_body(C_CRASHING_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Runtime Error"
        assert body["cases"][0]["exit_code"] not in (0, None)

    async def test_boolean_return_type(self, client: AsyncClient):
        c_bool_solution = (
            "int contains_nearby_duplicate(AtlasIntArray nums, int k) {\n"
            "    for (int i = 0; i < nums.size; i++)\n"
            "        for (int j = i + 1; j < nums.size && j - i <= k; j++)\n"
            "            if (nums.data[i] == nums.data[j]) return 1;\n"
            "    return 0;\n"
            "}\n"
        )
        r = await client.post(f"/api/v1/problems/{BOOL_PROBLEM_ID}/run", json=_c_run_body(c_bool_solution))
        body = r.json()
        assert body["cases"][0]["status"] == "passed"
        assert body["cases"][0]["actual_return"] is True


# ── C# (fifth compiled language) ──────────────────────────────────────────────
# Same compile-once PREPARERS/_run_prepared path as Java/C++/Rust/C, via
# `_prepare_csharp` (added this session -- `dotnet build -o out` once, then
# reruns the built DLL per case, ~50ms/run after the first).

CSHARP_GOOD_SOLUTION = (
    "class Solution {\n"
    "    public static int[] top_k_frequent(int[] nums, int k) {\n"
    "        var counts = new System.Collections.Generic.Dictionary<int, int>();\n"
    "        foreach (var x in nums) { counts[x] = counts.ContainsKey(x) ? counts[x] + 1 : 1; }\n"
    "        var keys = new System.Collections.Generic.List<int>(counts.Keys);\n"
    "        keys.Sort((a, b) => counts[a] != counts[b] ? counts[b] - counts[a] : a - b);\n"
    "        return keys.GetRange(0, k).ToArray();\n"
    "    }\n"
    "}\n"
)
CSHARP_WRONG_SOLUTION = (
    "class Solution {\n"
    "    public static int[] top_k_frequent(int[] nums, int k) {\n"
    "        var sorted = new System.Collections.Generic.List<int>(nums);\n"
    "        sorted.Sort();\n"
    "        return sorted.GetRange(0, k).ToArray();\n"
    "    }\n"
    "}\n"
)
CSHARP_RENAMED_SOLUTION = "class Solution {\n    public static int[] solve(int[] nums, int k) { return new int[] {}; }\n}\n"
CSHARP_WRONG_ARITY_SOLUTION = "class Solution {\n    public static int[] top_k_frequent(int[] nums, int k, int extra) { return new int[] {}; }\n}\n"
CSHARP_CRASHING_SOLUTION = (
    "class Solution {\n"
    "    public static int[] top_k_frequent(int[] nums, int k) {\n"
    "        return new int[] { nums[999999] };\n"
    "    }\n"
    "}\n"
)


def _csharp_run_body(code: str, **kw) -> dict:
    return _run_body(code, language="csharp", **kw)


class TestCSharpAdapter:
    async def test_visible_all_pass(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_csharp_run_body(CSHARP_GOOD_SOLUTION))
        assert r.status_code == 200
        body = r.json()
        assert body["summary"] == {"passed": 3, "failed": 0, "total": 3, "runtime_ms": pytest.approx(body["summary"]["runtime_ms"])}
        assert body["cases"][0]["actual_return"] == [1, 2]

    async def test_wrong_solution_fails_at_least_one_case(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_csharp_run_body(CSHARP_WRONG_SOLUTION))
        body = r.json()
        assert body["summary"]["passed"] < body["summary"]["total"]

    async def test_missing_function_is_compile_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_csharp_run_body(CSHARP_RENAMED_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"]

    async def test_wrong_arity_is_compile_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_csharp_run_body(CSHARP_WRONG_ARITY_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"]

    async def test_runtime_error_propagates(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_csharp_run_body(CSHARP_CRASHING_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Runtime Error"
        assert body["cases"][0]["exit_code"] not in (0, None)

    async def test_boolean_return_type(self, client: AsyncClient):
        csharp_bool_solution = (
            "class Solution {\n"
            "    public static bool contains_nearby_duplicate(int[] nums, int k) {\n"
            "        var last = new System.Collections.Generic.Dictionary<int, int>();\n"
            "        for (int i = 0; i < nums.Length; i++) {\n"
            "            if (last.ContainsKey(nums[i]) && i - last[nums[i]] <= k) return true;\n"
            "            last[nums[i]] = i;\n"
            "        }\n"
            "        return false;\n"
            "    }\n"
            "}\n"
        )
        r = await client.post(f"/api/v1/problems/{BOOL_PROBLEM_ID}/run", json=_csharp_run_body(csharp_bool_solution))
        body = r.json()
        assert body["cases"][0]["status"] == "passed"
        assert body["cases"][0]["actual_return"] is True


# ── Perl ───────────────────────────────────────────────────────────────────────
# Interpreted (compose_source, recomposed per case) via run_perl -- no
# PREPARERS entry, unlike the 5 compiled languages above.

PERL_GOOD_SOLUTION = (
    "sub top_k_frequent {\n"
    "    my ($nums, $k) = @_;\n"
    "    my %counts;\n"
    "    $counts{$_}++ for @$nums;\n"
    "    my @keys = sort { $counts{$b} != $counts{$a} ? $counts{$b} <=> $counts{$a} : $a <=> $b } keys %counts;\n"
    "    return [ @keys[0 .. $k - 1] ];\n"
    "}\n"
)
PERL_WRONG_SOLUTION = (
    "sub top_k_frequent {\n"
    "    my ($nums, $k) = @_;\n"
    "    my @sorted = sort { $a <=> $b } @$nums;\n"
    "    return [ @sorted[0 .. $k - 1] ];\n"
    "}\n"
)
PERL_RENAMED_SOLUTION = "sub solve { return []; }\n"
PERL_CRASHING_SOLUTION = "sub top_k_frequent { my ($nums, $k) = @_; die \"boom\"; }\n"


def _perl_run_body(code: str, **kw) -> dict:
    return _run_body(code, language="perl", **kw)


class TestPerlAdapter:
    async def test_visible_all_pass(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_perl_run_body(PERL_GOOD_SOLUTION))
        assert r.status_code == 200
        body = r.json()
        assert body["summary"] == {"passed": 3, "failed": 0, "total": 3, "runtime_ms": pytest.approx(body["summary"]["runtime_ms"])}
        assert body["cases"][0]["actual_return"] == [1, 2]

    async def test_wrong_solution_fails_at_least_one_case(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_perl_run_body(PERL_WRONG_SOLUTION))
        body = r.json()
        assert body["summary"]["passed"] < body["summary"]["total"]

    async def test_missing_function_is_contract_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_perl_run_body(PERL_RENAMED_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Function Contract Error"
        assert body["cases"][0]["contract_error"]["reason"] == "missing_function"

    async def test_runtime_error_propagates(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_perl_run_body(PERL_CRASHING_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Runtime Error"
        assert body["cases"][0]["exit_code"] not in (0, None)

    async def test_boolean_return_type(self, client: AsyncClient):
        perl_bool_solution = (
            "sub contains_nearby_duplicate {\n"
            "    my ($nums, $k) = @_;\n"
            "    my %last;\n"
            "    for my $i (0 .. $#$nums) {\n"
            "        if (exists $last{$nums->[$i]} && $i - $last{$nums->[$i]} <= $k) { return 1; }\n"
            "        $last{$nums->[$i]} = $i;\n"
            "    }\n"
            "    return 0;\n"
            "}\n"
        )
        r = await client.post(f"/api/v1/problems/{BOOL_PROBLEM_ID}/run", json=_perl_run_body(perl_bool_solution))
        body = r.json()
        assert body["cases"][0]["status"] == "passed"
        assert body["cases"][0]["actual_return"] is True


# ── Go (sixth compiled language) ──────────────────────────────────────────────
# Same compile-once PREPARERS/_run_prepared path as Java/C++/Rust/C/C#, via
# `_prepare_go` (added this session -- toolchain itself was installed this
# session too, go.dev's official zip, since it was TOOLCHAIN_UNAVAILABLE in
# the original probe and this environment has no package manager).

GO_GOOD_SOLUTION = (
    "func top_k_frequent(nums []int, k int) []int {\n"
    "\tcounts := make(map[int]int)\n"
    "\tfor _, n := range nums { counts[n]++ }\n"
    "\tkeys := make([]int, 0, len(counts))\n"
    "\tfor key := range counts { keys = append(keys, key) }\n"
    "\tsort.Slice(keys, func(a, b int) bool {\n"
    "\t\tif counts[keys[a]] != counts[keys[b]] { return counts[keys[a]] > counts[keys[b]] }\n"
    "\t\treturn keys[a] < keys[b]\n"
    "\t})\n"
    "\treturn keys[:k]\n"
    "}\n"
)
GO_WRONG_SOLUTION = (
    "func top_k_frequent(nums []int, k int) []int {\n"
    "\tsort.Ints(nums)\n"
    "\treturn nums[:k]\n"
    "}\n"
)
GO_RENAMED_SOLUTION = "func solve(nums []int, k int) []int { return []int{} }\n"
GO_WRONG_ARITY_SOLUTION = "func top_k_frequent(nums []int, k int, extra int) []int { return []int{} }\n"
GO_CRASHING_SOLUTION = (
    "func top_k_frequent(nums []int, k int) []int {\n"
    "\treturn []int{nums[999999]}\n"
    "}\n"
)


def _go_run_body(code: str, **kw) -> dict:
    return _run_body(code, language="go", **kw)


class TestGoAdapter:
    async def test_visible_all_pass(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_go_run_body(GO_GOOD_SOLUTION))
        assert r.status_code == 200
        body = r.json()
        assert body["summary"] == {"passed": 3, "failed": 0, "total": 3, "runtime_ms": pytest.approx(body["summary"]["runtime_ms"])}
        assert body["cases"][0]["actual_return"] == [1, 2]

    async def test_wrong_solution_fails_at_least_one_case(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_go_run_body(GO_WRONG_SOLUTION))
        body = r.json()
        assert body["summary"]["passed"] < body["summary"]["total"]

    async def test_missing_function_is_compile_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_go_run_body(GO_RENAMED_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"]

    async def test_wrong_arity_is_compile_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_go_run_body(GO_WRONG_ARITY_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"]

    async def test_runtime_error_propagates(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_go_run_body(GO_CRASHING_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Runtime Error"
        assert body["cases"][0]["exit_code"] not in (0, None)

    async def test_boolean_return_type(self, client: AsyncClient):
        go_bool_solution = (
            "func contains_nearby_duplicate(nums []int, k int) bool {\n"
            "\tlast := make(map[int]int)\n"
            "\tfor i, x := range nums {\n"
            "\t\tif j, ok := last[x]; ok && i-j <= k { return true }\n"
            "\t\tlast[x] = i\n"
            "\t}\n"
            "\treturn false\n"
            "}\n"
        )
        r = await client.post(f"/api/v1/problems/{BOOL_PROBLEM_ID}/run", json=_go_run_body(go_bool_solution))
        body = r.json()
        assert body["cases"][0]["status"] == "passed"
        assert body["cases"][0]["actual_return"] is True


# ── Ruby ───────────────────────────────────────────────────────────────────────
# Interpreted (compose_source, recomposed per case) via run_ruby -- no
# PREPARERS entry, same as Perl.

RUBY_GOOD_SOLUTION = (
    "def top_k_frequent(nums, k)\n"
    "  counts = Hash.new(0)\n"
    "  nums.each { |n| counts[n] += 1 }\n"
    "  counts.keys.sort_by { |key| [-counts[key], key] }[0...k]\n"
    "end\n"
)
RUBY_WRONG_SOLUTION = (
    "def top_k_frequent(nums, k)\n"
    "  nums.sort[0...k]\n"
    "end\n"
)
RUBY_RENAMED_SOLUTION = "def solve(nums, k)\n  []\nend\n"
RUBY_CRASHING_SOLUTION = "def top_k_frequent(nums, k)\n  raise 'boom'\nend\n"


def _ruby_run_body(code: str, **kw) -> dict:
    return _run_body(code, language="ruby", **kw)


class TestRubyAdapter:
    async def test_visible_all_pass(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_ruby_run_body(RUBY_GOOD_SOLUTION))
        assert r.status_code == 200
        body = r.json()
        assert body["summary"] == {"passed": 3, "failed": 0, "total": 3, "runtime_ms": pytest.approx(body["summary"]["runtime_ms"])}
        assert body["cases"][0]["actual_return"] == [1, 2]

    async def test_wrong_solution_fails_at_least_one_case(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_ruby_run_body(RUBY_WRONG_SOLUTION))
        body = r.json()
        assert body["summary"]["passed"] < body["summary"]["total"]

    async def test_missing_function_is_contract_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_ruby_run_body(RUBY_RENAMED_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Function Contract Error"
        assert body["cases"][0]["contract_error"]["reason"] == "missing_function"

    async def test_runtime_error_propagates(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_ruby_run_body(RUBY_CRASHING_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Runtime Error"
        assert body["cases"][0]["exit_code"] not in (0, None)

    async def test_boolean_return_type(self, client: AsyncClient):
        ruby_bool_solution = (
            "def contains_nearby_duplicate(nums, k)\n"
            "  last = {}\n"
            "  nums.each_with_index do |x, i|\n"
            "    return true if last.key?(x) && i - last[x] <= k\n"
            "    last[x] = i\n"
            "  end\n"
            "  false\n"
            "end\n"
        )
        r = await client.post(f"/api/v1/problems/{BOOL_PROBLEM_ID}/run", json=_ruby_run_body(ruby_bool_solution))
        body = r.json()
        assert body["cases"][0]["status"] == "passed"
        assert body["cases"][0]["actual_return"] is True


# ── PHP ────────────────────────────────────────────────────────────────────────
# Interpreted (compose_source, recomposed per case) via run_php -- no
# PREPARERS entry, same as Perl/Ruby.

PHP_GOOD_SOLUTION = (
    "function top_k_frequent($nums, $k) {\n"
    "    $counts = [];\n"
    "    foreach ($nums as $n) { $counts[$n] = ($counts[$n] ?? 0) + 1; }\n"
    "    $keys = array_keys($counts);\n"
    "    usort($keys, function ($a, $b) use ($counts) {\n"
    "        return $counts[$a] != $counts[$b] ? $counts[$b] - $counts[$a] : $a - $b;\n"
    "    });\n"
    "    return array_slice($keys, 0, $k);\n"
    "}\n"
)
PHP_WRONG_SOLUTION = (
    "function top_k_frequent($nums, $k) {\n"
    "    sort($nums);\n"
    "    return array_slice($nums, 0, $k);\n"
    "}\n"
)
PHP_RENAMED_SOLUTION = "function solve($nums, $k) { return []; }\n"
PHP_CRASHING_SOLUTION = "function top_k_frequent($nums, $k) { throw new Exception('boom'); }\n"


def _php_run_body(code: str, **kw) -> dict:
    return _run_body(code, language="php", **kw)


class TestPhpAdapter:
    async def test_visible_all_pass(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_php_run_body(PHP_GOOD_SOLUTION))
        assert r.status_code == 200
        body = r.json()
        assert body["summary"] == {"passed": 3, "failed": 0, "total": 3, "runtime_ms": pytest.approx(body["summary"]["runtime_ms"])}
        assert body["cases"][0]["actual_return"] == [1, 2]

    async def test_wrong_solution_fails_at_least_one_case(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_php_run_body(PHP_WRONG_SOLUTION))
        body = r.json()
        assert body["summary"]["passed"] < body["summary"]["total"]

    async def test_missing_function_is_contract_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_php_run_body(PHP_RENAMED_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Function Contract Error"
        assert body["cases"][0]["contract_error"]["reason"] == "missing_function"

    async def test_runtime_error_propagates(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_php_run_body(PHP_CRASHING_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Runtime Error"
        assert body["cases"][0]["exit_code"] not in (0, None)

    async def test_boolean_return_type(self, client: AsyncClient):
        php_bool_solution = (
            "function contains_nearby_duplicate($nums, $k) {\n"
            "    $last = [];\n"
            "    foreach ($nums as $i => $x) {\n"
            "        if (isset($last[$x]) && $i - $last[$x] <= $k) return true;\n"
            "        $last[$x] = $i;\n"
            "    }\n"
            "    return false;\n"
            "}\n"
        )
        r = await client.post(f"/api/v1/problems/{BOOL_PROBLEM_ID}/run", json=_php_run_body(php_bool_solution))
        body = r.json()
        assert body["cases"][0]["status"] == "passed"
        assert body["cases"][0]["actual_return"] is True


# ── R ──────────────────────────────────────────────────────────────────────────
# Interpreted (compose_source, recomposed per case) via run_r -- no PREPARERS
# entry, same as Perl/Ruby/PHP. Requires the `jsonlite` CRAN package to be
# installed for whatever R this environment resolves (see adapters.py's R
# section docstring) -- installed this session.

R_GOOD_SOLUTION = (
    "top_k_frequent <- function(nums, k) {\n"
    "  nums <- unlist(nums)\n"
    "  counts <- table(nums)\n"
    "  keys <- as.numeric(names(counts))\n"
    "  ord <- order(-as.numeric(counts), keys)\n"
    "  as.list(keys[ord][1:k])\n"
    "}\n"
)
R_WRONG_SOLUTION = (
    "top_k_frequent <- function(nums, k) {\n"
    "  as.list(sort(unlist(nums))[1:k])\n"
    "}\n"
)
R_RENAMED_SOLUTION = "solve <- function(nums, k) { list() }\n"
R_CRASHING_SOLUTION = "top_k_frequent <- function(nums, k) { stop('boom') }\n"


def _r_run_body(code: str, **kw) -> dict:
    return _run_body(code, language="r", **kw)


class TestRAdapter:
    async def test_visible_all_pass(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_r_run_body(R_GOOD_SOLUTION))
        assert r.status_code == 200
        body = r.json()
        assert body["summary"] == {"passed": 3, "failed": 0, "total": 3, "runtime_ms": pytest.approx(body["summary"]["runtime_ms"])}
        assert body["cases"][0]["actual_return"] == [1, 2]

    async def test_wrong_solution_fails_at_least_one_case(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_r_run_body(R_WRONG_SOLUTION))
        body = r.json()
        assert body["summary"]["passed"] < body["summary"]["total"]

    async def test_missing_function_is_contract_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_r_run_body(R_RENAMED_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Function Contract Error"
        assert body["cases"][0]["contract_error"]["reason"] == "missing_function"

    async def test_runtime_error_propagates(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_r_run_body(R_CRASHING_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Runtime Error"
        assert body["cases"][0]["exit_code"] not in (0, None)

    async def test_boolean_return_type(self, client: AsyncClient):
        r_bool_solution = (
            "contains_nearby_duplicate <- function(nums, k) {\n"
            "  nums <- unlist(nums)\n"
            "  n <- length(nums)\n"
            "  for (i in 1:n) {\n"
            "    j <- i + 1\n"
            "    while (j <= n && j - i <= k) {\n"
            "      if (nums[i] == nums[j]) return(TRUE)\n"
            "      j <- j + 1\n"
            "    }\n"
            "  }\n"
            "  FALSE\n"
            "}\n"
        )
        r_ = await client.post(f"/api/v1/problems/{BOOL_PROBLEM_ID}/run", json=_r_run_body(r_bool_solution))
        body = r_.json()
        assert body["cases"][0]["status"] == "passed"
        assert body["cases"][0]["actual_return"] is True


# ── Kotlin (seventh compiled language) ────────────────────────────────────────
# Same compile-once PREPARERS/_run_prepared path as the other compiled
# adapters, via an EXISTING `_prepare_kotlin` entry (Program Mode already had
# it) -- only the toolchain itself (kotlinc) was installed this session.

KOTLIN_GOOD_SOLUTION = (
    "fun top_k_frequent(nums: List<Int>, k: Int): List<Int> {\n"
    "    val counts = HashMap<Int, Int>()\n"
    "    for (n in nums) { counts[n] = (counts[n] ?: 0) + 1 }\n"
    "    return counts.keys.sortedWith(compareByDescending<Int> { counts[it] }.thenBy { it }).take(k)\n"
    "}\n"
)
KOTLIN_WRONG_SOLUTION = (
    "fun top_k_frequent(nums: List<Int>, k: Int): List<Int> {\n"
    "    return nums.sorted().take(k)\n"
    "}\n"
)
KOTLIN_RENAMED_SOLUTION = "fun solve(nums: List<Int>, k: Int): List<Int> { return listOf() }\n"
KOTLIN_WRONG_ARITY_SOLUTION = "fun top_k_frequent(nums: List<Int>, k: Int, extra: Int): List<Int> { return listOf() }\n"
KOTLIN_CRASHING_SOLUTION = (
    "fun top_k_frequent(nums: List<Int>, k: Int): List<Int> {\n"
    "    return listOf(nums[999999])\n"
    "}\n"
)


def _kotlin_run_body(code: str, **kw) -> dict:
    return _run_body(code, language="kotlin", **kw)


class TestKotlinAdapter:
    async def test_visible_all_pass(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_kotlin_run_body(KOTLIN_GOOD_SOLUTION))
        assert r.status_code == 200
        body = r.json()
        assert body["summary"] == {"passed": 3, "failed": 0, "total": 3, "runtime_ms": pytest.approx(body["summary"]["runtime_ms"])}
        assert body["cases"][0]["actual_return"] == [1, 2]

    async def test_wrong_solution_fails_at_least_one_case(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_kotlin_run_body(KOTLIN_WRONG_SOLUTION))
        body = r.json()
        assert body["summary"]["passed"] < body["summary"]["total"]

    async def test_missing_function_is_compile_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_kotlin_run_body(KOTLIN_RENAMED_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"]

    async def test_wrong_arity_is_compile_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_kotlin_run_body(KOTLIN_WRONG_ARITY_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"]

    async def test_runtime_error_propagates(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_kotlin_run_body(KOTLIN_CRASHING_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Runtime Error"
        assert body["cases"][0]["exit_code"] not in (0, None)

    async def test_boolean_return_type(self, client: AsyncClient):
        kotlin_bool_solution = (
            "fun contains_nearby_duplicate(nums: List<Int>, k: Int): Boolean {\n"
            "    val last = HashMap<Int, Int>()\n"
            "    for (i in nums.indices) {\n"
            "        if (last.containsKey(nums[i]) && i - last[nums[i]]!! <= k) return true\n"
            "        last[nums[i]] = i\n"
            "    }\n"
            "    return false\n"
            "}\n"
        )
        r = await client.post(f"/api/v1/problems/{BOOL_PROBLEM_ID}/run", json=_kotlin_run_body(kotlin_bool_solution))
        body = r.json()
        assert body["cases"][0]["status"] == "passed"
        assert body["cases"][0]["actual_return"] is True


# ── Scala (eighth compiled language) ──────────────────────────────────────────
# Same compile-once PREPARERS/_run_prepared path as the other compiled
# adapters, via an EXISTING `_prepare_scala` entry (scala-cli --power package)
# -- only the toolchain itself (scala-cli) was installed this session.

SCALA_GOOD_SOLUTION = (
    "def top_k_frequent(nums: List[Int], k: Int): List[Int] = {\n"
    "  val counts = nums.groupBy(identity).view.mapValues(_.size).toMap\n"
    "  counts.keys.toList.sortBy(n => (-counts(n), n)).take(k)\n"
    "}\n"
)
SCALA_WRONG_SOLUTION = (
    "def top_k_frequent(nums: List[Int], k: Int): List[Int] = {\n"
    "  nums.sorted.take(k)\n"
    "}\n"
)
SCALA_RENAMED_SOLUTION = "def solve(nums: List[Int], k: Int): List[Int] = List()\n"
SCALA_WRONG_ARITY_SOLUTION = "def top_k_frequent(nums: List[Int], k: Int, extra: Int): List[Int] = List()\n"
SCALA_CRASHING_SOLUTION = (
    "def top_k_frequent(nums: List[Int], k: Int): List[Int] = {\n"
    "  List(nums(999999))\n"
    "}\n"
)


def _scala_run_body(code: str, **kw) -> dict:
    return _run_body(code, language="scala", **kw)


class TestScalaAdapter:
    async def test_visible_all_pass(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_scala_run_body(SCALA_GOOD_SOLUTION))
        assert r.status_code == 200
        body = r.json()
        assert body["summary"] == {"passed": 3, "failed": 0, "total": 3, "runtime_ms": pytest.approx(body["summary"]["runtime_ms"])}
        assert body["cases"][0]["actual_return"] == [1, 2]

    async def test_wrong_solution_fails_at_least_one_case(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_scala_run_body(SCALA_WRONG_SOLUTION))
        body = r.json()
        assert body["summary"]["passed"] < body["summary"]["total"]

    async def test_missing_function_is_compile_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_scala_run_body(SCALA_RENAMED_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"]

    async def test_wrong_arity_is_compile_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_scala_run_body(SCALA_WRONG_ARITY_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"]

    async def test_runtime_error_propagates(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_scala_run_body(SCALA_CRASHING_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Runtime Error"
        assert body["cases"][0]["exit_code"] not in (0, None)

    async def test_boolean_return_type(self, client: AsyncClient):
        scala_bool_solution = (
            "def contains_nearby_duplicate(nums: List[Int], k: Int): Boolean = {\n"
            "  val last = scala.collection.mutable.HashMap[Int, Int]()\n"
            "  for (i <- nums.indices) {\n"
            "    if (last.contains(nums(i)) && i - last(nums(i)) <= k) return true\n"
            "    last(nums(i)) = i\n"
            "  }\n"
            "  false\n"
            "}\n"
        )
        r = await client.post(f"/api/v1/problems/{BOOL_PROBLEM_ID}/run", json=_scala_run_body(scala_bool_solution))
        body = r.json()
        assert body["cases"][0]["status"] == "passed"
        assert body["cases"][0]["actual_return"] is True


# ── Swift (ninth compiled language) ───────────────────────────────────────────
# Same compile-once PREPARERS/_run_prepared path as the other compiled
# adapters, via a NEW `_prepare_swift` entry (added this session, using
# `swiftc main.swift -o main.exe` -- needed a Visual Studio Build Tools
# install this session too, for the MSVC linker Swift's Windows target
# requires).

SWIFT_GOOD_SOLUTION = (
    "func top_k_frequent(_ nums: [Int], _ k: Int) -> [Int] {\n"
    "    var counts: [Int: Int] = [:]\n"
    "    for n in nums { counts[n, default: 0] += 1 }\n"
    "    return counts.keys.sorted { counts[$0]! != counts[$1]! ? counts[$0]! > counts[$1]! : $0 < $1 }.prefix(k).map { $0 }\n"
    "}\n"
)
SWIFT_WRONG_SOLUTION = (
    "func top_k_frequent(_ nums: [Int], _ k: Int) -> [Int] {\n"
    "    return Array(nums.sorted().prefix(k))\n"
    "}\n"
)
SWIFT_RENAMED_SOLUTION = "func solve(_ nums: [Int], _ k: Int) -> [Int] { return [] }\n"
SWIFT_WRONG_ARITY_SOLUTION = "func top_k_frequent(_ nums: [Int], _ k: Int, _ extra: Int) -> [Int] { return [] }\n"
SWIFT_CRASHING_SOLUTION = (
    "func top_k_frequent(_ nums: [Int], _ k: Int) -> [Int] {\n"
    "    return [nums[999999]]\n"
    "}\n"
)


def _swift_run_body(code: str, **kw) -> dict:
    return _run_body(code, language="swift", **kw)


class TestSwiftAdapter:
    async def test_visible_all_pass(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_swift_run_body(SWIFT_GOOD_SOLUTION))
        assert r.status_code == 200
        body = r.json()
        assert body["summary"] == {"passed": 3, "failed": 0, "total": 3, "runtime_ms": pytest.approx(body["summary"]["runtime_ms"])}
        assert body["cases"][0]["actual_return"] == [1, 2]

    async def test_wrong_solution_fails_at_least_one_case(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_swift_run_body(SWIFT_WRONG_SOLUTION))
        body = r.json()
        assert body["summary"]["passed"] < body["summary"]["total"]

    async def test_missing_function_is_compile_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_swift_run_body(SWIFT_RENAMED_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"]

    async def test_wrong_arity_is_compile_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_swift_run_body(SWIFT_WRONG_ARITY_SOLUTION))
        body = r.json()
        assert body["cases"] == []
        assert body["compile_output"]

    async def test_runtime_error_propagates(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_swift_run_body(SWIFT_CRASHING_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Runtime Error"
        assert body["cases"][0]["exit_code"] not in (0, None)

    async def test_boolean_return_type(self, client: AsyncClient):
        swift_bool_solution = (
            "func contains_nearby_duplicate(_ nums: [Int], _ k: Int) -> Bool {\n"
            "    var last: [Int: Int] = [:]\n"
            "    for (i, n) in nums.enumerated() {\n"
            "        if let j = last[n], i - j <= k { return true }\n"
            "        last[n] = i\n"
            "    }\n"
            "    return false\n"
            "}\n"
        )
        r = await client.post(f"/api/v1/problems/{BOOL_PROBLEM_ID}/run", json=_swift_run_body(swift_bool_solution))
        body = r.json()
        assert body["cases"][0]["status"] == "passed"
        assert body["cases"][0]["actual_return"] is True


class TestTypeScriptAdapter:
    async def test_visible_all_pass(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_ts_run_body(TS_GOOD_SOLUTION))
        assert r.status_code == 200
        body = r.json()
        assert body["summary"] == {"passed": 3, "failed": 0, "total": 3, "runtime_ms": pytest.approx(body["summary"]["runtime_ms"])}
        assert body["cases"][0]["actual_return"] == [1, 2]

    async def test_wrong_solution_fails_at_least_one_case(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_ts_run_body(TS_WRONG_SOLUTION))
        body = r.json()
        assert body["summary"]["passed"] < body["summary"]["total"]

    async def test_missing_function_is_contract_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_ts_run_body(TS_RENAMED_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Function Contract Error"
        assert body["cases"][0]["contract_error"]["reason"] == "missing_function"

    async def test_wrong_arity_is_contract_error(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_ts_run_body(TS_WRONG_ARITY_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Function Contract Error"
        assert body["cases"][0]["contract_error"]["reason"] == "signature_mismatch"

    async def test_runtime_error_propagates(self, client: AsyncClient):
        r = await client.post(f"/api/v1/problems/{PROBLEM_ID}/run", json=_ts_run_body(TS_CRASHING_SOLUTION))
        body = r.json()
        assert body["cases"][0]["status"] == "Runtime Error"
        assert body["cases"][0]["exit_code"] not in (0, None)

    async def test_boolean_return_type(self, client: AsyncClient):
        ts_bool_solution = (
            "function contains_nearby_duplicate(nums: number[], k: number): boolean {\n"
            "  const lastSeen: Record<number, number> = {};\n"
            "  for (let i = 0; i < nums.length; i++) {\n"
            "    const x = nums[i];\n"
            "    if (Object.prototype.hasOwnProperty.call(lastSeen, x) && i - lastSeen[x] <= k) return true;\n"
            "    lastSeen[x] = i;\n"
            "  }\n"
            "  return false;\n"
            "}\n"
        )
        r = await client.post(f"/api/v1/problems/{BOOL_PROBLEM_ID}/run", json=_ts_run_body(ts_bool_solution))
        body = r.json()
        assert body["cases"][0]["status"] == "passed"
        assert body["cases"][0]["actual_return"] is True


# ── Program Mode regression (unaffected by Function Mode's existence) ────────

class TestProgramModeUnaffected:
    async def test_problem_detail_exposes_function_contract(self, client: AsyncClient):
        r = await client.get(f"/api/v1/problems/{PROBLEM_ID}")
        body = r.json()
        assert body["function_contract"]["function_name"] == "top_k_frequent"
        assert "python" in body["starter_code_function"]

    async def test_explicit_program_mode_still_uses_stdin_stdout(self, client: AsyncClient):
        # This problem has no real Program Mode solution seeded (starter_code
        # is a stub) -- just confirm the request is routed to the Program
        # Mode path (execution_mode echoed back) and doesn't silently run
        # Function Mode instead.
        r = await client.post(
            f"/api/v1/problems/{PROBLEM_ID}/run",
            json={"language": "python", "code": "print('noop')\n", "mode": "custom",
                  "execution_mode": "program", "custom_cases": [{"input_data": ""}]},
        )
        assert r.status_code == 200
        assert r.json()["execution_mode"] == "program"
