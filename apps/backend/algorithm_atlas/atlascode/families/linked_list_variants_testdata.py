"""
40-test case plans for the `linked-list-variants` family (see testgen.py for
the shared bucket contract: visible 5 / basic 7 / boundary 8 / adversarial 8
/ mutation 7 / stress 5 = 40). One entry per slug in
linked_list_variants.py's `_SPECS`.

Each `to_input` mirrors the exact stdin format the original hand-written
`_Spec.cases` already used (verified against linked_list_variants.py and the
reference/wrong solutions registered in scripts/verify_atlascode_family.py).
Lists here are the project's plain-array simplification of a linked list
(see linked_list_variants.py's module docstring) — no pointer structure, no
canonical tree-style serialization applies to this family.
"""
from __future__ import annotations

import random

from .. import independent_oracles as oracles
from .. import testgen as tg


def _arr(xs) -> str:
    return " ".join(str(x) for x in xs)


# ── reverse-linked-list: oracle(values) ───────────────────────────────────────

def _to_input_values(values):
    return f"{len(values)} {_arr(values)}"


def _plan_reverse(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_values

    def gen_small():
        n = rng.randint(0, 8)
        return (tg.rand_int_array(rng, n, -50, 50),)

    def gen_stress():
        n = rng.randint(3000, 5000)
        return (tg.rand_int_array(rng, n, -1000, 1000),)

    visible = [
        ([1, 2, 3, 4, 5],), ([],), ([7],), ([3, 1, 4, 2],), ([5, 5, 5],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([],), ([1],), ([1, 2],), ([-1],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (list(range(1, 10)),),                # strictly ascending — sorted-descending wrong-answer trap
        (list(range(9, 0, -1)),),              # already reversed order in the input itself
        ([4] * 8,),                             # all-equal — reversal is a no-op visually but order still matters internally
        ([-5, -4, -3, -2, -1],),               # negative ascending values
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 2],),      # minimal pair — off-by-one swap catchable
        ([1, 2, 3],),   # odd length — middle element must stay put
        ([2, 1],),      # already-reverse-sorted pair
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── linked-list-cycle-detect: oracle(pos) ─────────────────────────────────────
# to_input encodes (values, pos) to match the problem's stdin contract, but
# the independent oracle only depends on `pos` (see independent_oracles.py) —
# case tuples are (values, pos) and the plan always passes both through.

def _to_input_cycle(values, pos):
    return f"{len(values)} {_arr(values)} {pos}"


def _cycle_oracle(values, pos):
    """Adapter: the case-plan tuples carry (values, pos) so `to_input` can
    serialize the full stdin line, but the independent oracle only depends
    on `pos` (see independent_oracles.linked_list_has_cycle) — unwrap here
    so build_forty() can call spec.oracle(*args) uniformly."""
    return oracles.linked_list_has_cycle(pos)


def _plan_cycle(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_cycle

    def gen_small_acyclic():
        n = rng.randint(1, 8)
        return (tg.rand_int_array(rng, n, -50, 50), -1)

    def gen_small_cyclic():
        n = rng.randint(1, 8)
        pos = rng.randint(0, n - 1)
        return (tg.rand_int_array(rng, n, -50, 50), pos)

    def gen_stress():
        n = rng.randint(3000, 5000)
        if rng.random() < 0.5:
            return (tg.rand_int_array(rng, n, -1000, 1000), -1)
        return (tg.rand_int_array(rng, n, -1000, 1000), rng.randint(0, n - 1))

    visible = [
        ([1, 2, 3], 1), ([1, 2], -1), ([1], 0), ([1, 2, 3, 4], -1), ([5, 6, 7], 0),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, lambda: (gen_small_cyclic() if rng.random() < 0.5 else gen_small_acyclic()), ti, seen)
    boundary_anchors = [
        ([1], -1),   # single node, no cycle
        ([1], 0),    # single node self-loop
        ([1, 2], 0),  # two nodes, cycle back to head
        ([1, 2], 1),  # two nodes, tail self-loop
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(
        8 - len(boundary_anchors), lambda: (gen_small_cyclic() if rng.random() < 0.5 else gen_small_acyclic()), ti, seen
    )
    adversarial_anchors = [
        ([1, 2, 3, 4, 5, 6, 7, 8], 0),   # cycle back to the very start — long loop
        ([1, 2, 3, 4, 5, 6, 7, 8], 7),   # tail self-loop on a long list
        ([3, 3, 3, 3, 3], -1),            # all-duplicate VALUES but acyclic — trap for value-based wrong solution
        ([3, 3, 3, 3, 3], 2),             # all-duplicate values, cycle mid-list
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 2, 3], 2),   # cycle exactly at the last node (self-loop at tail)
        ([1, 2, 3], 0),   # cycle back to head — full-list loop
        ([1, 2, 3], -1),  # matching acyclic control for the same values
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(
        7 - len(mutation_anchors), lambda: (gen_small_cyclic() if rng.random() < 0.5 else gen_small_acyclic()), ti, seen
    )
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── merge-two-sorted-lists: oracle(a, b) ──────────────────────────────────────

def _to_input_merge(a, b):
    return f"{len(a)} {_arr(a)}\n{len(b)} {_arr(b)}"


def _plan_merge(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_merge

    def gen_small():
        na, nb = rng.randint(0, 5), rng.randint(0, 5)
        return (tg.rand_sorted_array(rng, na, -30, 30), tg.rand_sorted_array(rng, nb, -30, 30))

    def gen_stress():
        na, nb = rng.randint(1500, 2500), rng.randint(1500, 2500)
        return (tg.rand_sorted_array(rng, na, -10_000, 10_000), tg.rand_sorted_array(rng, nb, -10_000, 10_000))

    visible = [
        ([1, 2, 4], [1, 3, 4]), ([], []), ([], [0]), ([1, 5], [0, 2, 6]), ([2, 3], [1, 4]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([], []), ([1], []), ([], [1]), ([1], [1])]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, 1, 1], [1, 1, 1]),                 # all-equal across both lists — order/stability trap
        (list(range(0, 20, 2)), list(range(1, 20, 2))),  # perfectly interleaving evens/odds
        ([-10, -5, 0], [-8, -3, 5]),             # negative values interleaved
        (list(range(10)), []),                    # one list fully empty, other populated
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 3, 5], [2, 4, 6]),   # strict interleave, no ties
        ([1, 2, 3], [1, 2, 3]),   # identical lists — duplicate merge order
        ([5], [1, 2, 3, 4]),      # one single large element vs a whole smaller run
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── remove-nth-from-end: oracle(values, n) ────────────────────────────────────
# NOTE: the oracle raises OracleError unless 1 <= n <= len(values) — every
# generated case must respect that range.

def _to_input_remove_nth(values, k):
    return f"{len(values)} {_arr(values)} {k}"


def _plan_remove_nth(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_remove_nth

    def gen_small():
        n = rng.randint(1, 8)
        return (tg.rand_int_array(rng, n, -50, 50), rng.randint(1, n))

    def gen_stress():
        n = rng.randint(3000, 5000)
        return (tg.rand_int_array(rng, n, -1000, 1000), rng.randint(1, n))

    visible = [
        ([1, 2, 3, 4, 5], 2), ([1], 1), ([1, 2], 2), ([1, 2, 3], 1), ([9, 8, 7, 6], 3),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([1], 1), ([1, 2], 1), ([1, 2], 2), ([1, 2, 3], 3)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (list(range(1, 11)), 10),    # remove the HEAD (n = length)
        (list(range(1, 11)), 1),     # remove the TAIL (n = 1)
        ([5, 5, 5, 5, 5], 3),         # all-equal values — position matters, not value
        (list(range(1, 11)), 5),     # remove a strictly interior node
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 2, 3, 4, 5], 5),   # n = length: removes index 0, not the "k-th from start" trap
        ([1, 2, 3, 4, 5], 1),   # n = 1: removes the last index, not index k-1
        ([1, 2, 3], 2),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── middle-of-linked-list: oracle(values) ─────────────────────────────────────
# NOTE: the oracle raises OracleError on an empty list — every case needs
# len(values) >= 1. Constraint caps length at 100.

def _plan_middle(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_values

    def gen_small():
        n = rng.randint(1, 10)
        return (tg.rand_int_array(rng, n, -50, 50),)

    def gen_stress():
        n = rng.randint(80, 100)
        return (tg.rand_int_array(rng, n, -1000, 1000),)

    visible = [
        ([1, 2, 3, 4, 5],), ([1, 2, 3, 4, 5, 6],), ([9],), ([1, 2],), ([1, 2, 3],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([1],), ([1, 2],), ([1, 2, 3],), ([-5],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, 2, 3, 4],),                # even length — second-middle convention trap
        ([1, 2, 3, 4, 5, 6, 7, 8],),    # longer even length
        ([7] * 9,),                      # all-equal, odd length
        ([7] * 10,),                     # all-equal, even length
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 2, 3, 4],),      # even length 4 — must pick values[2], not values[1]
        ([1, 2, 3, 4, 5, 6],),  # even length 6 — must pick values[3]
        ([1, 2],),              # smallest even case
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── palindrome-linked-list: oracle(values) ────────────────────────────────────
# NOTE: constraints require length >= 1.

def _plan_palindrome(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_values

    def _make_palindrome(n: int) -> list[int]:
        half = [rng.randint(-30, 30) for _ in range((n + 1) // 2)]
        if n % 2 == 0:
            return half + half[::-1]
        return half + half[-2::-1]

    def gen_small_palindrome():
        n = rng.randint(1, 8)
        return (_make_palindrome(n),)

    def gen_small_non_palindrome():
        n = rng.randint(2, 8)
        for _ in range(50):
            vals = tg.rand_int_array(rng, n, -30, 30)
            if vals != vals[::-1]:
                return (vals,)
        return ([1, 2],)

    def gen_stress():
        n = rng.randint(3000, 5000)
        if rng.random() < 0.5:
            return (_make_palindrome(n),)
        for _ in range(50):
            vals = tg.rand_int_array(rng, n, -1000, 1000)
            if vals != vals[::-1]:
                return (vals,)
        return (tg.rand_int_array(rng, n, -1000, 1000),)

    visible = [
        ([1, 2, 2, 1],), ([1, 2],), ([5],), ([1, 2, 1],), ([3, 3],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, lambda: (gen_small_palindrome() if rng.random() < 0.5 else gen_small_non_palindrome()), ti, seen)
    boundary_anchors = [([1],), ([1, 1],), ([1, 2],), ([1, 2, 1],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(
        8 - len(boundary_anchors), lambda: (gen_small_palindrome() if rng.random() < 0.5 else gen_small_non_palindrome()), ti, seen
    )
    adversarial_anchors = [
        ([1] * 9,),                          # all-equal, odd length — trivially a palindrome
        ([1] * 10,),                         # all-equal, even length
        (list(range(1, 6)) + list(range(4, 0, -1)),),   # true palindrome with distinct values
        (list(range(1, 6)) + list(range(5, 0, -1)),),   # off-by-one near-palindrome (NOT one — extra middle value repeats)
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 2, 3, 2, 1],),   # true odd-length palindrome — sorted() would also "look" ordered but isn't the check
        ([1, 2, 2, 1],),       # true even-length palindrome
        ([1, 2, 3],),          # ascending but NOT a palindrome (sorted-order wrong-answer trap)
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small_non_palindrome, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── registry ───────────────────────────────────────────────────────────────────
# NOTE: linked-list-cycle-detect's independent oracle only takes `pos`, not
# `values` (see independent_oracles.linked_list_has_cycle), but its case-plan
# tuples are (values, pos) so to_input can serialize the full stdin line.
# build_forty() always calls `spec.oracle(*args)` with the SAME args tuple
# used for `to_input`, so linked_list_variants.py's builder must use
# `_cycle_oracle` (exported here) as that slug's TestSpec.oracle instead of
# the raw independent_oracles.linked_list_has_cycle.

LINKED_LIST_TEST_PLANS: dict[str, tuple] = {
    # slug -> (to_input, format_output, plan_fn)
    "reverse-linked-list": (_to_input_values, lambda a: " ".join(map(str, a)), _plan_reverse),
    "linked-list-cycle-detect": (_to_input_cycle, lambda a: "true" if a else "false", _plan_cycle),
    "merge-two-sorted-lists": (_to_input_merge, lambda a: " ".join(map(str, a)), _plan_merge),
    "remove-nth-from-end": (_to_input_remove_nth, lambda a: " ".join(map(str, a)), _plan_remove_nth),
    "middle-of-linked-list": (_to_input_values, str, _plan_middle),
    "palindrome-linked-list": (_to_input_values, lambda a: "true" if a else "false", _plan_palindrome),
}
