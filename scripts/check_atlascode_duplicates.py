"""
Semantic duplicate detection for the AtlasCode catalog.

Manual duplicate-checking stopped scaling once variant-family expansion
started shipping 5-15 problems per batch (see docs/atlascode-resume.md). This
script builds a deterministic "semantic signature" per problem from real
introspected data — never from titles alone — and classifies every pair:

  EXACT_DUPLICATE   same oracle function AND same canonical algorithm link
                    (or both unlinked) — almost certainly the same problem
                    shipped twice under different slugs.
  LIKELY_DUPLICATE  same oracle function, different algorithm link, OR same
                    algorithm link with very high title/statement overlap.
  RELATED_VARIANT   same canonical algorithm link but a different oracle
                    (legitimate — e.g. several tree problems built on the
                    same "diameter" algorithm), or same category with high
                    but not exact structural overlap.
  DISTINCT          everything else.

Deterministic rules run first and are authoritative for EXACT/LIKELY.
Title-similarity (difflib) is a secondary signal only, used for
RELATED_VARIANT vs DISTINCT — it never silently deletes or merges content
(see the mega-prompt's own "no automatic deletion" requirement).

Usage:
    python scripts/check_atlascode_duplicates.py
    python scripts/check_atlascode_duplicates.py --verbose   # print every pair, not just non-DISTINCT
"""
from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))
sys.path.insert(0, str(Path(__file__).parent))

import logging
logging.disable(logging.CRITICAL)

FAMILY_MODULES = [
    "array_hashing_variants", "backtracking_count_variants", "bfs_graph_variants",
    "binary_search_variants", "bit_manipulation_variants", "divide_and_conquer",
    "dp_variants", "dynamic_programming", "greedy", "linked_list_variants",
    "number_theory", "sliding_window_variants", "stack_variants",
    "string_family", "tree_variants",
    "famous_easy", "famous_arrays_matrix", "famous_graphs_trees_lists", "famous_hard",
]
# sorting.py / searching.py are intentionally excluded: they are 1:1 with the
# canonical algorithm registry (one problem per algorithm), never duplicated
# among themselves by construction.


@dataclass
class ProblemSignature:
    problem_id: str
    family: str
    category: str
    title: str
    difficulty: str
    algorithm_slug: str | None
    oracle_identity: str | None  # "<module>.<qualname>" or None if unknown (curated)
    statement: str


def _oracle_identity(oracle) -> str | None:
    if oracle is None:
        return None
    return f"{getattr(oracle, '__module__', '?')}.{getattr(oracle, '__qualname__', '?')}"


def collect_family_signatures() -> list[ProblemSignature]:
    sigs: list[ProblemSignature] = []
    for mod_name in FAMILY_MODULES:
        module = importlib.import_module(f"algorithm_atlas.atlascode.families.{mod_name}")
        specs = getattr(module, "_SPECS", None)
        if not specs:
            continue
        for slug, spec in specs.items():
            algorithm_slug = getattr(spec, "algorithm_slug", slug)  # families default algorithm_slug=slug unless overridden
            title = getattr(spec, "title", slug.replace("-", " ").title())
            sigs.append(ProblemSignature(
                problem_id=slug,
                family=mod_name,
                category=getattr(spec, "category", mod_name),
                title=title,
                difficulty=getattr(spec, "difficulty", "Medium"),
                algorithm_slug=algorithm_slug,
                oracle_identity=_oracle_identity(getattr(spec, "oracle", None)),
                statement=getattr(spec, "statement", ""),
            ))
    return sigs


def collect_curated_signatures() -> list[ProblemSignature]:
    import seed_atlas_code as seed_mod
    sigs = []
    for prob, _tests in seed_mod.PROBLEMS:
        sigs.append(ProblemSignature(
            problem_id=prob["id"],
            family="curated",
            category=prob.get("category", "?"),
            title=prob.get("title", prob["id"]),
            difficulty=prob.get("difficulty", "Medium"),
            algorithm_slug=prob.get("algorithm_slug"),
            oracle_identity=None,  # curated problems are hand-authored, no shared oracle module
            statement=prob.get("problem_statement", ""),
        ))
    return sigs


import re

_WORD_RE = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(_WORD_RE.findall(text.lower()))


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def classify_pair(a: ProblemSignature, b: ProblemSignature) -> str | None:
    """Returns a classification label, or None for DISTINCT (to keep verbose
    output manageable — DISTINCT is not printed by default).

    Word-level (token-set) Jaccard similarity is used instead of
    character-level ratio deliberately: short titles ("First Occurrence" vs
    "Koko Eating Bananas") can spike a character-based ratio purely from
    coincidental letter overlap even when semantically unrelated — this
    produced false positives across an entire legitimately-distinct variant
    cluster during initial testing. Statement text is long-form prose, so a
    high statement-Jaccard is a much stronger signal than a high title-Jaccard.
    """
    same_oracle = a.oracle_identity is not None and a.oracle_identity == b.oracle_identity
    same_algo = a.algorithm_slug is not None and a.algorithm_slug == b.algorithm_slug
    both_unlinked = a.algorithm_slug is None and b.algorithm_slug is None

    title_sim = _jaccard(_tokens(a.title), _tokens(b.title))
    statement_sim = _jaccard(_tokens(a.statement), _tokens(b.statement)) if a.statement and b.statement else 0.0

    if same_oracle and (same_algo or both_unlinked):
        return "EXACT_DUPLICATE"
    if same_oracle:
        # same underlying computation, but linked to different canonical
        # algorithms — still very likely the same problem shipped twice.
        return "LIKELY_DUPLICATE"
    if same_algo and (statement_sim > 0.7 or title_sim > 0.9):
        return "LIKELY_DUPLICATE"
    if same_algo:
        # documented-legitimate pattern: many variant problems intentionally
        # share one canonical algorithm_slug (e.g. binary-search-variants).
        return "RELATED_VARIANT"
    if a.category == b.category and statement_sim > 0.5:
        return "RELATED_VARIANT"
    return None


def main(verbose: bool = False) -> int:
    sigs = collect_family_signatures() + collect_curated_signatures()
    print(f"Problems scanned: {len(sigs)}")

    counts = {"EXACT_DUPLICATE": 0, "LIKELY_DUPLICATE": 0, "RELATED_VARIANT": 0}
    findings: list[tuple[str, ProblemSignature, ProblemSignature]] = []

    # Bucket by (oracle_identity) and (algorithm_slug) first to avoid an
    # O(n^2) scan over ~230+ problems doing full pairwise work — only compare
    # within buckets that share at least one strong signal, then fall back to
    # a same-category pass for the title-similarity-only RELATED_VARIANT case.
    by_oracle: dict[str, list[ProblemSignature]] = {}
    by_algo: dict[str, list[ProblemSignature]] = {}
    by_category: dict[str, list[ProblemSignature]] = {}
    for s in sigs:
        if s.oracle_identity:
            by_oracle.setdefault(s.oracle_identity, []).append(s)
        if s.algorithm_slug:
            by_algo.setdefault(s.algorithm_slug, []).append(s)
        by_category.setdefault(s.category, []).append(s)

    seen_pairs: set[tuple[str, str]] = set()

    def _consider(a: ProblemSignature, b: ProblemSignature):
        if a.problem_id == b.problem_id:
            return
        key = tuple(sorted((a.problem_id, b.problem_id)))
        if key in seen_pairs:
            return
        seen_pairs.add(key)
        label = classify_pair(a, b)
        if label:
            counts[label] += 1
            findings.append((label, a, b))

    for group in by_oracle.values():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                _consider(group[i], group[j])
    for group in by_algo.values():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                _consider(group[i], group[j])
    for group in by_category.values():
        if len(group) > 40:
            continue  # category too large for a cheap full scan; oracle/algo passes already cover the strong signals
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                _consider(group[i], group[j])

    distinct = len(sigs)  # informational only — "distinct" here means "no other problem flagged against it", not a pairwise count

    order = ["EXACT_DUPLICATE", "LIKELY_DUPLICATE", "RELATED_VARIANT"]
    findings.sort(key=lambda f: order.index(f[0]))
    for label, a, b in findings:
        if verbose or label != "RELATED_VARIANT":
            print(f"  [{label}] {a.problem_id} ({a.family}) <-> {b.problem_id} ({b.family})")

    print("\n" + "=" * 50)
    print("ATLASCODE DUPLICATE AUDIT")
    print("=" * 50)
    print(f"Problems scanned: {len(sigs)}")
    print(f"Exact duplicates: {counts['EXACT_DUPLICATE']}")
    print(f"Likely duplicates: {counts['LIKELY_DUPLICATE']}")
    print(f"Related variants: {counts['RELATED_VARIANT']}")
    print(f"Distinct (flagged-against-nothing): {distinct - len({p for f in findings for p in (f[1].problem_id, f[2].problem_id)})}")
    print("=" * 50)
    return counts["EXACT_DUPLICATE"] + counts["LIKELY_DUPLICATE"]


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv
    exit_code = main(verbose=verbose)
    sys.exit(1 if exit_code else 0)
