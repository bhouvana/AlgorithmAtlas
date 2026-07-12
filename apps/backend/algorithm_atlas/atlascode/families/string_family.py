"""
String family factory. Of the 14 uncurated canonical `string` algorithms,
this batch covers 7 with genuinely distinct contracts. Deliberately
DEFERRED (not implemented) to avoid semantic duplicates or unresolved
contract ambiguity:
  - boyer-moore, rabin-karp: same "find all occurrences" task as the already-
    curated kmp-string-matching problem — no new problem contract without a
    different objective.
  - aho-corasick, aho-corasick-count: multi-pattern matching contracts not
    yet designed.
  - burrows-wheeler: canonical output representation (BWT string + index)
    not yet decided.
  - suffix-array-lcp, suffix-automaton: contracts not yet designed.

`z-algorithm` outputs the raw Z-array (distinct from any occurrence-finding
problem — tests understanding of the Z-function itself). `manacher` is
framed as "count all palindromic substrings" (distinct from
`longest-palindromic-substring`'s length-only output) so the two don't
collide on contract despite both touching palindromes.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .. import independent_oracles as oracles
from .. import testgen as tg
from .string_family_testdata import STRING_FAMILY_TEST_PLANS
from ...plugins.registry import RegisteredAlgorithm


def _fmt_int(answer: object) -> str:
    return str(answer)


def _fmt_int_list(answer: object) -> str:
    return " ".join(str(x) for x in answer)


def _fmt_str(answer: object) -> str:
    return str(answer)


@dataclass(frozen=True)
class _Spec:
    oracle: Callable[..., object]
    cases: list[tuple[str, tuple, bool]]
    statement: str
    constraints: list[str]
    starter_code: str
    difficulty: str = "Medium"
    estimated_minutes: int = 25
    format_output: Callable[[object], str] = _fmt_int


_SPECS: dict[str, _Spec] = {
    "z-algorithm": _Spec(
        oracle=oracles.z_array,
        cases=[
            ("aabcaabxaaz", ("aabcaabxaaz",), False),
            ("aaaa", ("aaaa",), False),
            ("a", ("a",), True),
            ("abcabc", ("abcabc",), True),
        ],
        statement=(
            "Given a string `s`, print its **Z-array**: `Z[i]` is the length of "
            "the longest substring starting at `i` that is also a prefix of `s` "
            "(by convention `Z[0] = 0`), space-separated."
        ),
        constraints=["1 ≤ s.length ≤ 10^5"],
        starter_code=(
            "import sys\ns = sys.stdin.read().strip()\n\n"
            "def z_function(s):\n    pass\n\nprint(' '.join(map(str, z_function(s))))\n"
        ),
        format_output=_fmt_int_list,
    ),
    "longest-common-substring": _Spec(
        oracle=oracles.longest_common_substring_length,
        cases=[
            ("abcdef\nzabcf", ("abcdef", "zabcf"), False),
            ("abc\ndef", ("abc", "def"), False),
            ("a\na", ("a", "a"), True),
            ("aabbcc\nbbccdd", ("aabbcc", "bbccdd"), True),
        ],
        statement=(
            "Given strings `s1` and `s2`, print the length of their longest "
            "**contiguous** common substring."
        ),
        constraints=["1 ≤ s1.length, s2.length ≤ 1000"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\ns1, s2 = lines[0], lines[1]\n\n"
            "def longest_common_substring(s1, s2):\n    pass\n\n"
            "print(longest_common_substring(s1, s2))\n"
        ),
    ),
    "longest-palindromic-substring": _Spec(
        oracle=oracles.longest_palindromic_substring_length,
        cases=[
            ("babad", ("babad",), False), ("cbbd", ("cbbd",), False),
            ("a", ("a",), True), ("racecarxyz", ("racecarxyz",), True),
        ],
        statement=(
            "Given a string `s`, print the length of the **longest palindromic "
            "substring** of `s`."
        ),
        constraints=["1 ≤ s.length ≤ 1000"],
        starter_code=(
            "import sys\ns = sys.stdin.read().rstrip('\\n')\n\n"
            "def longest_palindrome(s):\n    pass\n\nprint(longest_palindrome(s))\n"
        ),
        difficulty="Easy",
        estimated_minutes=20,
    ),
    "manacher": _Spec(
        oracle=oracles.count_palindromic_substrings,
        cases=[
            ("abc", ("abc",), False), ("aaa", ("aaa",), False),
            ("", ("",), True), ("aba", ("aba",), True),
        ],
        statement=(
            "Given a string `s`, print the **total number of palindromic "
            "substrings** (counting each position separately — e.g. 'aaa' has "
            "6: 'a','a','a','aa','aa','aaa'). Solve in O(n) using Manacher's "
            "algorithm."
        ),
        constraints=["0 ≤ s.length ≤ 1000"],
        starter_code=(
            "import sys\ns = sys.stdin.read().rstrip('\\n')\n\n"
            "def count_palindromic_substrings(s):\n    pass\n\n"
            "print(count_palindromic_substrings(s))\n"
        ),
    ),
    "run-length-encoding": _Spec(
        oracle=oracles.run_length_encode,
        cases=[
            ("aaabbc", ("aaabbc",), False), ("a", ("a",), False),
            ("", ("",), True), ("aabbccddeeff", ("aabbccddeeff",), True),
        ],
        statement=(
            "Given a string `s`, print its **run-length encoding**: each maximal "
            "run of a repeated character becomes `<count><char>` (e.g. `aaabbc` → "
            "`3a2b1c`). Print an empty line for an empty string."
        ),
        constraints=["0 ≤ s.length ≤ 10^5"],
        starter_code=(
            "import sys\ns = sys.stdin.read().rstrip('\\n')\n\n"
            "def rle_encode(s):\n    pass\n\nprint(rle_encode(s))\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
        format_output=_fmt_str,
    ),
    "suffix-array": _Spec(
        oracle=oracles.suffix_array,
        cases=[
            ("banana", ("banana",), False), ("abc", ("abc",), False),
            ("a", ("a",), True), ("aaaa", ("aaaa",), True),
        ],
        statement=(
            "Given a string `s`, print its **suffix array**: the starting "
            "indices of all suffixes of `s`, sorted lexicographically by suffix, "
            "space-separated."
        ),
        constraints=["1 ≤ s.length ≤ 1000"],
        starter_code=(
            "import sys\ns = sys.stdin.read().rstrip('\\n')\n\n"
            "def build_suffix_array(s):\n    pass\n\n"
            "print(' '.join(map(str, build_suffix_array(s))))\n"
        ),
        difficulty="Hard",
        estimated_minutes=35,
        format_output=_fmt_int_list,
    ),
    "string-hashing": _Spec(
        oracle=oracles.count_distinct_substrings_length_k,
        cases=[
            ("aabcaab 2", ("aabcaab", 2), False), ("aaaa 1", ("aaaa", 1), False),
            ("abcabc 3", ("abcabc", 3), True), ("a 1", ("a", 1), True),
        ],
        statement=(
            "Given a string `s` and an integer `k`, print the number of "
            "**distinct substrings of length exactly `k`**. Solve using a "
            "rolling hash to compare substrings in O(1) after O(n) preprocessing."
        ),
        constraints=["1 ≤ k ≤ s.length ≤ 10^5"],
        starter_code=(
            "import sys\nline = sys.stdin.read().rstrip('\\n')\ns, k = line.rsplit(' ', 1)\nk = int(k)\n\n"
            "def count_distinct_substrings(s, k):\n    pass\n\n"
            "print(count_distinct_substrings(s, k))\n"
        ),
    ),
}


def build_string_problems(
    algorithms: list[RegisteredAlgorithm],
    curated_slugs: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    by_slug = {r.slug: r for r in algorithms if r.category == "string"}
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for slug, spec in _SPECS.items():
        if slug in curated_slugs:
            continue
        reg = by_slug.get(slug)
        if reg is None:
            skipped.append((slug, "not found in canonical registry"))
            continue

        test_plan = STRING_FAMILY_TEST_PLANS.get(slug)
        if test_plan is None:
            skipped.append((slug, "no 40-test case plan registered in string_family_testdata.py"))
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
            "category": "strings",
            "algorithm_slug": slug,
            "estimated_minutes": spec.estimated_minutes,
            "problem_statement": spec.statement,
            "examples": [],
            "constraints": spec.constraints,
            "hints": [{"level": 1, "text": intuition[:300] or f"Implement {reg.name}."}],
            "companies": [],
            "starter_code": {"python": spec.starter_code},
        }
        problems.append((problem, test_cases))

    return problems, skipped
