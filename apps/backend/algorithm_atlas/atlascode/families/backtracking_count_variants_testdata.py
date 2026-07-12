"""
40-test case plans for the `backtracking-count-variants` family (see
testgen.py for the shared bucket contract: visible 5 / basic 7 / boundary 8 /
adversarial 8 / mutation 7 / stress 5 = 40). One entry per slug in
backtracking_count_variants.py's `_SPECS`.

Each `to_input` mirrors the exact stdin format the original hand-written
`_Spec.cases` already used (verified against backtracking_count_variants.py
before writing this).
"""
from __future__ import annotations

import random

from .. import testgen as tg


def _arr(xs) -> str:
    return " ".join(str(x) for x in xs)


# ── palindrome-partition: oracle(s) — min cuts, s must be non-empty ──────────

def _to_input_pal_partition_cuts(s):
    return s


def _plan_palindrome_partition(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_pal_partition_cuts

    def gen_small():
        n = rng.randint(1, 10)
        return (tg.rand_string(rng, n, "ab"),)

    def gen_stress():
        n = rng.randint(800, 2000)
        return (tg.rand_string(rng, n, "ab"),)

    visible = [
        ("aab",), ("a",), ("ab",), ("racecar",), ("aabb",),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ("a",), ("aa",), ("ab",), ("aba",),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("a" * 12,),                          # already a full palindrome -- 0 cuts
        ("ab" * 6,),                          # alternating, forces many cuts
        ("aabaa" + "b" + "aabaa",),           # nested palindromic structure
        ("abcdefg",),                          # all-distinct chars -- worst case, n-1 cuts
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("aa",),    # single palindrome, 0 cuts
        ("aab",),   # exactly one cut needed ("aa"|"b")
        ("abc",),   # all distinct, needs 2 cuts
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── palindrome-partitioning: oracle(s) — count ways, s may be empty ─────────

def _to_input_pal_partition_count(s):
    return s


def _plan_palindrome_partitioning(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_pal_partition_count

    def gen_small():
        n = rng.randint(1, 9)
        return (tg.rand_string(rng, n, "ab"),)

    def gen_stress():
        # constraint: 1 <= s.length <= 16
        n = 16
        return (tg.rand_string(rng, n, "ab"),)

    visible = [
        ("aab",), ("a",), ("aaa",), ("abc",), ("aa",),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ("a",), ("aa",), ("ab",), ("aba",),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("a" * 16,),                # every possible cut valid -- maximal way-count (2^15)
        ("ab" * 8,),                # alternating, forces exactly one full split
        ("aaab",),                  # mixed run then a distinct tail char
        ("abababab",),              # repeating 2-cycle, tests DP memoization correctness
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("aa",),    # 2 ways: "a"+"a" or "aa"
        ("aab",),   # 2 ways: "a"+"a"+"b" or "aa"+"b"
        ("abc",),   # exactly 1 way (all singles)
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── restore-ip-addresses-count: oracle(s) — 4 <= s.length <= 12, digits only ─

def _to_input_restore_ip(s):
    return s


def _rand_digit_string(rng: random.Random, n: int) -> str:
    return "".join(rng.choice("0123456789") for _ in range(n))


def _plan_restore_ip(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_restore_ip

    def gen_small():
        n = rng.randint(4, 10)
        return (_rand_digit_string(rng, n),)

    def gen_stress():
        # constraint: s.length <= 12; the oracle is O(1) combinatorial so
        # "stress" here means exhausting the full length range repeatedly.
        n = 12
        return (_rand_digit_string(rng, n),)

    visible = [
        ("25525511135",), ("0000",), ("101023",), ("1111",), ("11111",),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ("0000",), ("1111",), ("255255255255",), ("0100100100",),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("000000000000",),   # all-zero max length -- leading-zero rule blocks nearly everything
        ("999999999999",),   # every 3-digit segment exceeds 255 -- answer 0
        ("101010101010",),   # alternating digits with many leading-zero segment traps
        ("192168001001",),   # looks like a real IP -- classic case with multiple leading zeros
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("1111",),    # minimal length -- exactly 1 way (1.1.1.1)
        ("0110",),    # leading zero mid-string must be rejected correctly
        ("255255255255",),  # exactly at the max digit value per segment
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── word-break-count-ways: oracle(s, word_dict) ───────────────────────────────

def _to_input_word_break(s, word_dict):
    return f"{s}\n{_arr(word_dict)}"


def _plan_word_break(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_word_break

    def gen_small():
        alphabet = "ab"
        words = sorted({tg.rand_string(rng, rng.randint(1, 3), alphabet) for _ in range(4)})
        n = rng.randint(4, 12)
        s = "".join(rng.choice(words) for _ in range(1, 4))[:n] or words[0]
        if not s:
            s = words[0]
        return (s, words)

    def gen_stress():
        alphabet = "abc"
        words = sorted({tg.rand_string(rng, rng.randint(1, 3), alphabet) for _ in range(6)})
        s = "".join(rng.choice(words) for _ in range(6))[:20]
        return (s, words)

    visible = [
        ("catsanddog", ["cats", "cat", "and", "sand", "dog"]),
        ("leetcode", ["leet", "code"]),
        ("a", ["a"]),
        ("aaaa", ["a", "aa"]),
        ("applepie", ["apple", "pie", "app", "lepie"]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ("a", ["a"]),
        ("a", ["b"]),
        ("ab", ["a", "b"]),
        ("aa", ["a"]),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("aaaaaaaaaa", ["a", "aa", "aaa"]),          # classic exponential-branching trap without memoization
        ("catsandog", ["cats", "cat", "and", "sand", "dog"]),  # unsegmentable -- answer 0
        ("pineapplepenapple", ["apple", "pen", "applepen", "pine", "pineapple"]),  # multiple valid segmentations
        ("aabb", ["a", "ab", "b", "aab", "abb"]),     # overlapping candidate words at each position
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("aa", ["a", "aa"]),      # two ways: "a"+"a" or "aa"
        ("ab", ["a", "b"]),       # exactly one way
        ("abc", ["ab", "c", "a", "bc"]),  # two distinct valid segmentations
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── unique-permutations-count: oracle(nums) — 1 <= len(nums) <= 10 ──────────

def _to_input_unique_perms(nums):
    return f"{len(nums)} {_arr(nums)}"


def _plan_unique_permutations(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_unique_perms

    def gen_small():
        n = rng.randint(1, 6)
        pool = rng.randint(1, 3)
        return ([rng.randint(1, pool) for _ in range(n)],)

    def gen_stress():
        # constraint caps length at 10; "stress" = maximal length with
        # maximal distinct-permutation branching (all distinct values).
        n = 10
        return (tg.rand_distinct_int_array(rng, n, 1, 50),)

    visible = [
        ([1, 1, 2],), ([1, 2, 3],), ([1, 1, 1],), ([1, 1, 2, 2],), ([2, 2, 3],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([1],), ([1, 1],), ([1, 2],), ([1, 1, 1, 1],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1] * 10,),                              # all identical -- exactly 1 distinct permutation
        (list(range(1, 11)),),                    # all distinct -- maximal 10! permutations
        ([1, 1, 1, 1, 1, 2, 2, 2, 2, 2],),         # two equally-sized groups
        ([1, 1, 1, 1, 1, 1, 1, 1, 1, 2],),         # one dominant value plus a single outlier
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 1],),      # collapses 2! to 1
        ([1, 2],),      # stays at 2! = 2
        ([1, 1, 2],),   # 3!/2! = 3
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── registry ───────────────────────────────────────────────────────────────────

BACKTRACKING_COUNT_TEST_PLANS: dict[str, tuple] = {
    # slug -> (to_input, format_output, plan_fn)
    "palindrome-partition": (_to_input_pal_partition_cuts, str, _plan_palindrome_partition),
    "palindrome-partitioning": (_to_input_pal_partition_count, str, _plan_palindrome_partitioning),
    "restore-ip-addresses-count": (_to_input_restore_ip, str, _plan_restore_ip),
    "word-break-count-ways": (_to_input_word_break, str, _plan_word_break),
    "unique-permutations-count": (_to_input_unique_perms, str, _plan_unique_permutations),
}
