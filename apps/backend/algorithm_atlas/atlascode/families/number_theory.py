"""
Number-theory family factory.

ARCHITECTURE (revised — see docs/atlascode-progress.md "Oracle separation"):
Expected outputs here come EXCLUSIVELY from `atlascode/independent_oracles.py`
— short, hand-reviewed, unit-tested pure functions that never touch a
visualization plugin. This replaced the earlier approach of reading answers
off a plugin's `steps()` terminal state (still in `oracle.py`, still used by
sorting/searching where the terminal state is self-verifying via an
invariant check). Two number-theory problems generated that way
(`sieve-of-eratosthenes`, `collatz`) turned out to be silently wrong: the
plugin clamped/decimated internally in ways invisible unless you check the
exact inputs you're about to ship. See independent_oracles.py's module
docstring for the specifics.

Every algorithm below is included only if its independent oracle produces a
SINGLE unambiguous answer for a given input (a hard requirement — see
`docs/atlascode-progress.md`). Algorithms whose "correct" output is not
unique (extended-euclidean's (x, y) pair, a primitive root, a Goldbach pair,
a Pollard-rho factor, a discrete log with non-unique representation, a
minimal linear recurrence) are intentionally left out of this batch and
fall through to NEEDS_REVIEW/PROPERTY_JUDGE in the coverage manifest —
building a property-validator layer for them is future work, not something
to fake with a single hard-coded "expected" string.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .. import independent_oracles as oracles
from .. import testgen as tg
from .number_theory_testdata import NUMBER_THEORY_TEST_PLANS
from ...plugins.registry import RegisteredAlgorithm


def _fmt_int(answer: object) -> str:
    return str(answer)


def _fmt_bool(answer: object) -> str:
    return "true" if answer else "false"


def _fmt_int_list(answer: object) -> str:
    return " ".join(str(x) for x in answer)


@dataclass(frozen=True)
class _Spec:
    input_keys: tuple[str, ...]                 # ordered stdin fields
    oracle: Callable[..., object]                # independent_oracles function
    cases: list[tuple[dict, bool]]               # (inputs, is_hidden)
    statement: str
    constraints: list
    format_output: Callable[[object], str] = _fmt_int
    difficulty: str = "Easy"
    func_params: str = "n"                       # starter-code function signature


def _parse_stdin_code(keys: tuple[str, ...]) -> str:
    if len(keys) == 1:
        return f"{keys[0]} = int(sys.stdin.read().strip())\n"
    names = ", ".join(keys)
    return (
        "data = sys.stdin.read().split()\n"
        f"{names} = {', '.join(f'int(data[{i}])' for i in range(len(keys)))}\n"
    )


_SPECS: dict[str, _Spec] = {
    "catalan-number": _Spec(
        input_keys=("n",),
        oracle=oracles.catalan_number,
        cases=[({"n": 3}, False), ({"n": 6}, False), ({"n": 0}, True), ({"n": 10}, True)],
        statement="Given `n`, print the **n-th Catalan number** C(n) = C(2n, n) / (n + 1).",
        constraints=["0 ≤ n ≤ 1000"],
    ),
    "euler-phi-sieve": _Spec(
        input_keys=("n",),
        oracle=oracles.euler_phi,
        cases=[({"n": 12}, False), ({"n": 1}, False), ({"n": 2}, True), ({"n": 30}, True), ({"n": 500}, True)],
        statement=(
            "Given `n`, print **Euler's totient function φ(n)** — the count of integers "
            "in [1, n] coprime to n — computed by first sieving smallest-prime-factors "
            "up to n, then deriving φ from the factorization."
        ),
        constraints=["1 ≤ n ≤ 500"],
    ),
    "collatz": _Spec(
        input_keys=("n",),
        oracle=oracles.collatz_steps,
        cases=[
            ({"n": 6}, False), ({"n": 1}, False), ({"n": 27}, False),
            ({"n": 2}, True), ({"n": 15}, True), ({"n": 837799}, True),
        ],
        statement=(
            "Given `n`, simulate the **Collatz sequence** (n → n/2 if even, else "
            "n → 3n+1) until it reaches 1, and print the **number of steps** taken. "
            "n=1 takes 0 steps."
        ),
        constraints=["1 ≤ n ≤ 10^6"],
    ),
    "sieve-of-eratosthenes": _Spec(
        input_keys=("n",),
        oracle=oracles.sieve_primes,
        cases=[
            ({"n": 10}, False), ({"n": 1}, False), ({"n": 2}, False),
            ({"n": 0}, True), ({"n": 30}, True), ({"n": 100}, True),
        ],
        statement=(
            "Given `n`, print **all prime numbers ≤ n**, space-separated in ascending "
            "order, using the Sieve of Eratosthenes. Print an empty line if there are none."
        ),
        constraints=["0 ≤ n ≤ 10^5"],
        format_output=_fmt_int_list,
    ),
    "modular-exponentiation": _Spec(
        input_keys=("base", "exp", "mod"),
        oracle=oracles.mod_pow,
        cases=[
            ({"base": 2, "exp": 10, "mod": 1000}, False),
            ({"base": 3, "exp": 0, "mod": 5}, False),
            ({"base": 7, "exp": 128, "mod": 13}, True),
            ({"base": 123456789, "exp": 987654321, "mod": 1000000007}, True),
        ],
        statement=(
            "Given `base`, `exp`, and `mod`, compute **base^exp mod mod** using fast "
            "(binary) modular exponentiation in O(log exp) time."
        ),
        constraints=["0 ≤ base, exp ≤ 10^9", "1 ≤ mod ≤ 10^9"],
        func_params="base, exp, mod",
    ),
    "prime-factorization": _Spec(
        input_keys=("n",),
        oracle=oracles.prime_factors,
        cases=[
            ({"n": 12}, False), ({"n": 17}, False),
            ({"n": 360}, True), ({"n": 999983}, True),
        ],
        statement=(
            "Given `n`, print its **prime factorization** as prime factors with "
            "multiplicity, space-separated in ascending order (e.g. 12 → `2 2 3`)."
        ),
        constraints=["2 ≤ n ≤ 10^6"],
        format_output=_fmt_int_list,
    ),
    "number-of-divisors": _Spec(
        input_keys=("n",),
        oracle=oracles.count_divisors,
        cases=[
            ({"n": 1}, False), ({"n": 12}, False),
            ({"n": 17}, True), ({"n": 720720}, True),
        ],
        statement="Given `n`, print the **number of positive divisors** of n, d(n).",
        constraints=["1 ≤ n ≤ 10^6"],
    ),
    "euler-totient": _Spec(
        input_keys=("n",),
        oracle=oracles.euler_phi,
        cases=[
            ({"n": 1}, False), ({"n": 9}, False),
            ({"n": 36}, True), ({"n": 998244}, True),
        ],
        statement=(
            "Given `n`, print **Euler's totient function φ(n)** computed via **prime "
            "factorization** (φ(n) = n·∏(1 − 1/p) over distinct prime factors p of n), "
            "in O(√n) time."
        ),
        constraints=["1 ≤ n ≤ 10^6"],
    ),
    "miller-rabin": _Spec(
        input_keys=("n",),
        oracle=oracles.is_prime,
        cases=[
            ({"n": 2}, False), ({"n": 91}, False),
            ({"n": 97}, True), ({"n": 999983}, True), ({"n": 1}, True),
        ],
        statement=(
            "Given `n`, print `true` if n is **prime** and `false` otherwise, using the "
            "Miller-Rabin primality test."
        ),
        constraints=["0 ≤ n ≤ 10^7"],
        format_output=_fmt_bool,
    ),
    "lucas-theorem": _Spec(
        input_keys=("n", "k", "p"),
        oracle=oracles.lucas_binomial_mod,
        cases=[
            ({"n": 10, "k": 3, "p": 13}, False),
            ({"n": 5, "k": 2, "p": 5}, False),
            ({"n": 1000, "k": 500, "p": 13}, True),
            ({"n": 1000000000, "k": 123456, "p": 97}, True),
        ],
        statement=(
            "Given `n`, `k`, and a **prime** `p`, compute **C(n, k) mod p** using "
            "Lucas' theorem (decompose n and k in base p, multiply per-digit binomial "
            "coefficients mod p)."
        ),
        constraints=["0 ≤ k ≤ n ≤ 10^9", "2 ≤ p ≤ 97 (p prime)"],
        func_params="n, k, p",
    ),
    # NOT included (see module docstring): extended-euclidean, chinese-remainder,
    # goldbach, pollard-rho, primitive-root, tonelli-shanks, baby-step-giant-step,
    # berlekamp-massey — each has a non-unique or not-yet-verified answer contract.
}


def build_number_theory_problems(
    algorithms: list[RegisteredAlgorithm],
    curated_slugs: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    by_slug = {r.slug: r for r in algorithms if r.category == "number-theory"}
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for slug, spec in _SPECS.items():
        if slug in curated_slugs:
            continue
        reg = by_slug.get(slug)
        if reg is None:
            skipped.append((slug, "not found in canonical registry"))
            continue

        func_name = slug.replace("-", "_")

        test_plan = NUMBER_THEORY_TEST_PLANS.get(slug)
        if test_plan is None:
            skipped.append((slug, "no 40-test case plan registered in number_theory_testdata.py"))
            continue
        to_input, format_output, plan_fn = test_plan
        try:
            rng = tg.problem_rng(slug)
            case_plan = plan_fn(rng)
            test_spec = tg.TestSpec(oracle=spec.oracle, to_input=to_input, format_output=format_output)
            test_cases = tg.build_forty(slug, test_spec, case_plan)
        except (oracles.OracleError, tg.TestPlanError) as exc:
            skipped.append((slug, str(exc)))
            continue

        if not test_cases:
            skipped.append((slug, "no test cases produced"))
            continue

        intuition = reg.manifest.get("intuition", "") or reg.manifest.get("description", "")
        problem = {
            "id": slug,
            "title": reg.name,
            "difficulty": spec.difficulty,
            "category": "number-theory",
            "algorithm_slug": slug,
            "estimated_minutes": 15,
            "problem_statement": spec.statement,
            "examples": [],
            "constraints": spec.constraints,
            "hints": [{"level": 1, "text": intuition[:300] or f"Implement {reg.name}."}],
            "companies": [],
            "starter_code": {
                "python": (
                    "import sys\n"
                    f"{_parse_stdin_code(spec.input_keys)}\n"
                    f"def {func_name}({spec.func_params}):\n    pass\n\n"
                    f"print({func_name}({', '.join(spec.input_keys)}))\n"
                ),
            },
        }
        problems.append((problem, test_cases))

    return problems, skipped
