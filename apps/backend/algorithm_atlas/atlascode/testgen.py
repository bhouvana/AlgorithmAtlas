"""
Shared 40-test-case generation infrastructure for AtlasCode problems.

Repository-wide standard (see docs/atlascode-40-test-standard.md):
  Every ACTIVE problem ships EXACTLY 40 judge test cases, split into six
  quality buckets:

    visible      5   (is_hidden=False, shown to the user as examples)
    basic        7   (hidden, straightforward correctness)
    boundary     8   (hidden, edge/degenerate inputs)
    adversarial  8   (hidden, inputs a plausible wrong solution gets wrong)
    mutation     7   (hidden, targets a specific mutation of the reference
                      algorithm — off-by-one, wrong comparator, dropped case)
    stress       5   (hidden, large/near-constraint-limit inputs)
                40 total (35 hidden + 5 visible)

A problem's test data is never hand-typed 40 times. Each family factory
supplies a small ``case_plan``: for every bucket, a list of raw argument
tuples (the same Python objects passed to the independent oracle — NOT the
serialized stdin string). This module turns that plan into TestCase rows by:

  1. calling the oracle on each argument tuple to get the ground-truth answer
     (never hand-typed expected output — this was already the project's rule
     for the original 4-test-per-problem generation, extended here);
  2. serializing the arguments to the stdin string via the problem's
     ``to_input`` formatter;
  3. rejecting any case whose *normalized* stdin string collides with one
     already accepted for that problem (no duplicate-padding, ever);
  4. enforcing the exact per-bucket quota and the exact 40-total contract —
     a problem that is short a case in any bucket fails LOUD at generation
     time (``TestPlanError``), it does not silently ship 39 or 41 tests.

This module also writes ``atlascode_test_manifest.json`` at the repo root
(problem_id -> ordered list of {index, bucket, is_hidden}) — the per-test
metadata the DB schema deliberately does not carry (TestCase stays a plain
stdin/stdout row; bucket/strategy provenance lives in the manifest instead,
per the project's "don't force a migration for what a manifest can hold"
rule).
"""
from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

# ── Bucket contract ───────────────────────────────────────────────────────────

BUCKETS: tuple[str, ...] = ("visible", "basic", "boundary", "adversarial", "mutation", "stress")
BUCKET_QUOTA: dict[str, int] = {
    "visible": 5,
    "basic": 7,
    "boundary": 8,
    "adversarial": 8,
    "mutation": 7,
    "stress": 5,
}
TOTAL_TESTS = sum(BUCKET_QUOTA.values())
assert TOTAL_TESTS == 40

# Cumulative (start, end) order-index range per bucket, in BUCKETS order —
# since build_forty() always emits buckets in this fixed sequence, a test's
# bucket is fully determined by its `order` index. No per-row bucket column
# or side-channel field needed; the manifest is derived from this at any time.
_BUCKET_RANGES: dict[str, tuple[int, int]] = {}
_cursor = 0
for _b in BUCKETS:
    _BUCKET_RANGES[_b] = (_cursor, _cursor + BUCKET_QUOTA[_b])
    _cursor += BUCKET_QUOTA[_b]
del _cursor, _b


def bucket_for_order(order: int) -> str:
    for name, (start, end) in _BUCKET_RANGES.items():
        if start <= order < end:
            return name
    raise ValueError(f"order {order} out of range for a {TOTAL_TESTS}-test problem")

CasePlan = dict[str, list[tuple]]


class TestPlanError(ValueError):
    """A problem's case plan violates the exactly-40 / no-duplicates contract."""


def problem_rng(problem_id: str, salt: str = "") -> random.Random:
    """Deterministic RNG seeded from the problem id (+ optional salt) so
    generated test data is reproducible across re-runs without storing seeds
    for every individual case."""
    return random.Random(f"atlascode::{problem_id}::{salt}")


_WS_RE = re.compile(r"\s+")


def _dedup_key(input_data: str) -> str:
    """Normalize purely for duplicate detection — never mutates stored data.
    Collapses all whitespace runs (including newlines) to a single space so
    e.g. a matrix printed with '\\n' vs ' ' row separators is still caught as
    the same underlying case."""
    return _WS_RE.sub(" ", input_data.strip())


@dataclass(frozen=True)
class TestSpec:
    """The minimal contract a problem needs to generate its 40 tests."""
    oracle: Callable[..., Any]
    to_input: Callable[..., str]
    format_output: Callable[[Any], str] = str
    # Optional: cases already known-good from hand authorship, reused as-is
    # instead of regenerated (keeps the original pedagogical examples).
    seed_cases: list[tuple[str, tuple, bool]] = field(default_factory=list)
    # Optional: Function Mode support. When set, each generated row also gets
    # function_args ({name: value} zipped from this list against the SAME
    # `args` tuple already used for to_input/oracle -- never a separate/
    # re-parsed representation) and function_expected (the oracle's raw,
    # unformatted return value). None means Function Mode isn't supported for
    # this problem -- Program Mode generation is completely unaffected.
    function_arg_names: list[str] | None = None


def build_forty(problem_id: str, spec: TestSpec, case_plan: CasePlan) -> list[dict]:
    """Turn a case_plan into exactly 40 TestCase-row dicts (order 0..39).

    Raises TestPlanError if any bucket is short, if the total isn't 40, or if
    two accepted cases normalize to the same stdin.
    """
    seen: set[str] = set()
    rows: list[dict] = []
    order = 0

    for bucket in BUCKETS:
        quota = BUCKET_QUOTA[bucket]
        candidates = case_plan.get(bucket, [])
        if len(candidates) < quota:
            raise TestPlanError(
                f"{problem_id}: bucket '{bucket}' needs {quota} case(s), got {len(candidates)}"
            )
        accepted = 0
        for args in candidates:
            if accepted == quota:
                break
            input_data = spec.to_input(*args)
            key = _dedup_key(input_data)
            if key in seen:
                continue  # generator over-produced candidates on purpose; skip dupes silently
            seen.add(key)
            answer = spec.oracle(*args)
            row: dict[str, Any] = {
                "input_data": input_data,
                "expected_output": spec.format_output(answer),
                "is_hidden": bucket != "visible",
                "explanation": "",
                "order": order,
            }
            if spec.function_arg_names is not None:
                if len(spec.function_arg_names) != len(args):
                    raise TestPlanError(
                        f"{problem_id}: function_arg_names has {len(spec.function_arg_names)} "
                        f"name(s) but the case tuple has {len(args)} value(s)"
                    )
                row["function_args"] = dict(zip(spec.function_arg_names, args))
                row["function_expected"] = answer
            rows.append(row)
            order += 1
            accepted += 1
        if accepted < quota:
            raise TestPlanError(
                f"{problem_id}: bucket '{bucket}' produced only {accepted}/{quota} "
                f"UNIQUE case(s) — generator needs more distinct candidates"
            )

    if len(rows) != TOTAL_TESTS:
        raise TestPlanError(f"{problem_id}: expected {TOTAL_TESTS} total tests, built {len(rows)}")
    return rows


def manifest_entries_for(problem_id: str, rows: list[dict]) -> list[dict]:
    """Derive {index, bucket, is_hidden} manifest rows from plain TestCase
    dicts (bucket is implied by `order`, see bucket_for_order)."""
    return [
        {"index": row["order"], "bucket": bucket_for_order(row["order"]), "is_hidden": row["is_hidden"]}
        for row in rows
    ]


# ── Manifest persistence ──────────────────────────────────────────────────────

def _repo_root_manifest_path() -> Path:
    """atlascode_test_manifest.json lives at the repo root locally, 4 parents
    up from this file (used only by the one-off scripts/migrate_*_to_forty.py
    scripts, run from a full checkout). In the deployed Docker image,
    apps/backend/ is flattened directly onto /app (Dockerfile: `COPY
    apps/backend .`), so this file's parent chain is 2 levels shallower there
    and .parents[4] doesn't exist -- IndexError. Nothing in the deployed app
    ever calls write_manifest/load_manifest, so a fallback path here is
    harmless; what's NOT harmless is this module failing to import at all,
    which previously took down every AtlasCode problem-family import behind
    it (including the boot-time auto-seed) with a crash that had nothing to
    do with test manifests.
    """
    try:
        return Path(__file__).parents[4] / "atlascode_test_manifest.json"
    except IndexError:
        return Path(__file__).parent / "atlascode_test_manifest.json"


MANIFEST_PATH = _repo_root_manifest_path()


def write_manifest(entries_by_problem: dict[str, list[dict]], path: Path = MANIFEST_PATH) -> None:
    path.write_text(json.dumps(entries_by_problem, indent=2, sort_keys=True), encoding="utf-8")


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, list[dict]]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def fill_unique(
    quota: int,
    gen_fn: Callable[[], tuple],
    to_input: Callable[..., str],
    seen: set[str],
    max_attempts: int = 2000,
) -> list[tuple]:
    """Call gen_fn() repeatedly until `quota` args-tuples produce distinct
    (by to_input dedup key) stdin strings not already in `seen`. `seen` is
    mutated in place so callers can share one set across all buckets of a
    problem (guarantees no cross-bucket duplication, e.g. a hand-picked
    'boundary' case accidentally reappearing verbatim in 'stress').

    This is the mechanism that lets bucket generators be simple/random
    without ever risking padding: any collision is silently redrawn, and a
    generator that structurally can't produce `quota` distinct cases fails
    loudly instead of shipping duplicates.
    """
    accepted: list[tuple] = []
    attempts = 0
    while len(accepted) < quota and attempts < max_attempts:
        attempts += 1
        args = gen_fn()
        key = _dedup_key(to_input(*args))
        if key in seen:
            continue
        seen.add(key)
        accepted.append(args)
    if len(accepted) < quota:
        raise TestPlanError(
            f"fill_unique: only found {len(accepted)}/{quota} unique cases in {max_attempts} attempts"
        )
    return accepted


def register(
    anchors: list[tuple],
    to_input: Callable[..., str],
    seen: set[str],
) -> list[tuple]:
    """Register hand-picked anchor cases into the shared `seen` dedup set,
    dropping (loudly, via a shorter return list) any that collide with a
    case from an earlier bucket. Always call this on anchors BEFORE calling
    fill_unique for the same bucket's random remainder — otherwise a literal
    duplicate anchor silently shrinks the bucket below quota and
    build_forty() raises later with a confusing message."""
    out = []
    for args in anchors:
        key = _dedup_key(to_input(*args))
        if key in seen:
            continue
        seen.add(key)
        out.append(args)
    return out


# ── Reusable input-shape generators ───────────────────────────────────────────
# Small, generic building blocks shared across many families. Each returns raw
# Python values (not serialized strings) — pair with a problem's own
# `to_input` to get the stdin format.

def rand_int_array(rng: random.Random, n: int, lo: int, hi: int) -> list[int]:
    return [rng.randint(lo, hi) for _ in range(n)]


def rand_distinct_int_array(rng: random.Random, n: int, lo: int, hi: int) -> list[int]:
    return rng.sample(range(lo, hi + 1), n)


def rand_sorted_array(rng: random.Random, n: int, lo: int, hi: int, strict: bool = False) -> list[int]:
    if strict:
        return sorted(rng.sample(range(lo, hi + 1), n))
    return sorted(rand_int_array(rng, n, lo, hi))


def rand_string(rng: random.Random, n: int, alphabet: str = "abcdefghijklmnopqrstuvwxyz") -> str:
    return "".join(rng.choice(alphabet) for _ in range(n))


def rand_permutation(rng: random.Random, n: int) -> list[int]:
    vals = list(range(n))
    rng.shuffle(vals)
    return vals


def rand_graph_edges(rng: random.Random, n: int, m: int, directed: bool = False) -> list[tuple[int, int]]:
    """m random distinct edges over n labeled nodes (no self-loops)."""
    possible = [(u, v) for u in range(n) for v in range(n) if u != v and (directed or u < v)]
    m = min(m, len(possible))
    return rng.sample(possible, m)


# ── Generic adversarial/boundary/mutation PATTERN libraries ──────────────────
# These encode the handful of structural traps that recur across almost every
# algorithm operating on a given shape (array, string, interval-list, tree,
# graph), so a family's case_plan can compose them instead of re-deriving
# problem-specific insight from scratch every time. Each returns raw values
# for that shape only — a problem's own generator still assembles the final
# oracle-args tuple (e.g. zipping two int-array patterns into (starts, ends)).

def int_array_patterns(rng: random.Random, n: int, lo: int, hi: int) -> dict[str, list[int]]:
    """Named structural variants of an n-length int array in [lo, hi]."""
    mid = (lo + hi) // 2
    return {
        "all_equal": [mid] * n,
        "all_min": [lo] * n,
        "all_max": [hi] * n,
        "ascending": sorted(rand_int_array(rng, n, lo, hi)),
        "descending": sorted(rand_int_array(rng, n, lo, hi), reverse=True),
        "alternating_extremes": [lo if i % 2 == 0 else hi for i in range(n)],
        "single_outlier": [mid] * (n - 1) + [hi] if n > 1 else [hi],
        "many_duplicates": sorted(rng.choices(range(lo, min(lo + max(2, n // 4), hi + 1)), k=n)),
        "strictly_increasing": list(range(lo, lo + n)) if hi - lo + 1 >= n else sorted(rand_distinct_int_array(rng, min(n, hi - lo + 1), lo, hi)),
        "palindrome": (lambda h: h + h[::-1])([rng.randint(lo, hi) for _ in range(n // 2)]) + ([mid] if n % 2 else []),
    }


def string_patterns(rng: random.Random, n: int, alphabet: str = "abcdefghijklmnopqrstuvwxyz") -> dict[str, str]:
    a = alphabet[0]
    return {
        "all_same_char": a * n,
        "two_char_alternating": "".join(alphabet[i % 2] for i in range(n)),
        "all_distinct_prefix": "".join(alphabet[i % len(alphabet)] for i in range(n)) if n <= len(alphabet) else rand_string(rng, n, alphabet),
        "palindrome": (lambda h: h + h[::-1])(rand_string(rng, n // 2, alphabet)) + (rand_string(rng, 1, alphabet) if n % 2 else ""),
        "random": rand_string(rng, n, alphabet),
        "single_char": a,
        "worst_case_repeat": a * (n - 1) + alphabet[1 % len(alphabet)] if n > 1 else a,
    }


def interval_patterns(rng: random.Random, n: int, lo: int, hi: int) -> dict[str, tuple[list[int], list[int]]]:
    """(starts, ends) pairs with starts[i] < ends[i], as (starts, ends)."""
    def _rand_pair():
        s = sorted(rng.sample(range(lo, hi), min(n, hi - lo)))[:n]
        while len(s) < n:
            s.append(rng.randint(lo, hi - 1))
        e = [min(hi, x + rng.randint(1, max(1, (hi - lo) // 4))) for x in s]
        return s, e

    touching = list(range(lo, lo + n + 1))
    chain_starts, chain_ends = touching[:-1], touching[1:]
    identical = [lo] * n, [min(lo + 1, hi)] * n
    nested_starts = [lo] * n
    nested_ends = [hi - i for i in range(n)] if hi - n >= lo else [hi] * n
    rs, re_ = _rand_pair()
    return {
        "random": (rs, re_),
        "touching_chain": (chain_starts[:n], chain_ends[:n]),
        "all_identical": identical,
        "nested": (nested_starts, sorted(nested_ends, reverse=True)),
        "reverse_sorted": (sorted(rs, reverse=True), sorted(re_, reverse=True)),
    }


def _chain_serialize(values: list[int], side: str) -> list[int | None]:
    """Build a single-direction chain (root -> side -> side -> ...) as a real
    node structure, then BFS-serialize it to the canonical level-order-with-
    null format (matches families/tree_variants.py's `_parse_tree_code`
    parser exactly: only non-null nodes contribute child slots)."""
    other = "r" if side == "l" else "l"
    root = None
    tail = None
    for v in values:
        node = {"v": v, "l": None, "r": None}
        if root is None:
            root = node
        else:
            tail[side] = node
        tail = node
    if root is None:
        return []
    out: list[int | None] = [root["v"]]
    queue = [root]
    qi = 0
    while qi < len(queue):
        node = queue[qi]
        qi += 1
        for key in ("l", "r"):
            child = node[key]
            if child is None:
                out.append(None)
            else:
                out.append(child["v"])
                queue.append(child)
    while out and out[-1] is None:
        out.pop()
    return out


def tree_shape_patterns(rng: random.Random, n: int, lo: int = -50, hi: int = 50) -> dict[str, list[int | None]]:
    if n == 0:
        return {"empty": []}
    cur = [rng.randint(lo, hi) for _ in range(n)]
    return {
        "random_shape": rand_tree_level_order(rng, n, lo, hi),
        "left_skewed": _chain_serialize(cur, "l"),
        "right_skewed": _chain_serialize(cur, "r"),
        "single_node": [rng.randint(lo, hi)],
        "all_same_value": [rng.choice(range(lo, hi + 1))] * n,
    }


def rand_tree_level_order(rng: random.Random, n: int, lo: int = -50, hi: int = 50) -> list[int | None]:
    """A random-shaped binary tree (some None gaps) with n real nodes,
    level-order with explicit None for missing children (project's canonical
    tree serialization — see tree_variants.py)."""
    if n == 0:
        return []
    values: list[int | None] = [rng.randint(lo, hi)]
    frontier = 1
    placed = 1
    while placed < n:
        row = []
        for _ in range(frontier * 2):
            if placed < n and rng.random() < 0.7:
                row.append(rng.randint(lo, hi))
                placed += 1
            else:
                row.append(None)
        values.extend(row)
        frontier = sum(1 for v in row if v is not None)
        if frontier == 0 and placed < n:
            # forced dead end — restart the deepest None into a value
            for i in range(len(values) - 1, -1, -1):
                if values[i] is None:
                    values[i] = rng.randint(lo, hi)
                    placed += 1
                    frontier = 1
                    break
    # trim trailing Nones (canonical form omits them)
    while values and values[-1] is None:
        values.pop()
    return values
