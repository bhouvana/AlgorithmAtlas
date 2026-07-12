"""
40-test case plans for the `array-hashing-variants` family (see testgen.py
for the shared bucket contract: visible 5 / basic 7 / boundary 8 /
adversarial 8 / mutation 7 / stress 5 = 40). One entry per slug in
array_hashing_variants.py's `_SPECS`.

Each `to_input` mirrors the exact stdin format the original hand-written
`_Spec.cases` already used (verified against array_hashing_variants.py
before writing this).
"""
from __future__ import annotations

import random

from .. import testgen as tg


def _arr(xs) -> str:
    return " ".join(str(x) for x in xs)


# ── contains-duplicate-within-k: oracle(nums, k) ──────────────────────────────

def _to_input_contains_dup(nums, k):
    return f"{len(nums)} {_arr(nums)} {k}"


def _plan_contains_dup(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_contains_dup

    def gen_small():
        n = rng.randint(1, 8)
        return (tg.rand_int_array(rng, n, 0, 5), rng.randint(0, n))

    def gen_stress():
        n = rng.randint(2000, 8000)
        return (tg.rand_int_array(rng, n, 0, 50), rng.randint(0, n))

    visible = [
        ([1, 2, 3, 1], 3),
        ([1, 2, 3, 1], 2),
        ([1, 0, 1, 1], 1),
        ([1], 0),
        ([1, 2, 1], 1),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([1], 0),
        ([1, 1], 0),
        ([1, 2, 1], 0),
        ([5, 5], 100000),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, 2, 3, 4, 1], 3),        # duplicate exactly at distance k
        ([1, 2, 3, 4, 1], 2),        # duplicate just beyond distance k
        ([0, 1, 2, 3, 0, 4, 5], 4),  # dup at distance exactly k after gap
        ([1, 2, 1, 2, 1], 1),        # alternating dup pattern
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 2, 1], 1),   # dup at distance == k boundary (<=k true)
        ([1, 2, 3, 1], 2),  # dup at distance k+1 (should be false)
        ([7, 7], 0),      # adjacent dup at k=0
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── product-of-array-except-self: oracle(nums) — requires len(nums) >= 2 ─────

def _to_input_product_except_self(nums):
    return f"{len(nums)} {_arr(nums)}"


def _plan_product_except_self(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_product_except_self

    def gen_small():
        n = rng.randint(2, 8)
        return (tg.rand_int_array(rng, n, -10, 10),)

    def gen_stress():
        n = rng.randint(2000, 6000)
        return (tg.rand_int_array(rng, n, -20, 20),)

    visible = [
        ([1, 2, 3, 4],), ([-1, 1, 0, -3, 3],), ([5, 5],), ([2, 2, 2],), ([1, -1, 2],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([0, 0],), ([1, 0],), ([-1, -1],), ([0, 1, 2],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([0, 0, 5, 6],),          # two zeros -> all-zero result
        ([0, 4, 5],),             # single zero -> only that index nonzero
        ([-1, -1, -1, -1],),      # all-negative, sign flips per exclusion
        ([10, -10, 10, -10],),    # alternating signs cancel differently per position
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 1],),      # trivial product identity check
        ([2, 3, 0],),   # zero at the end
        ([0, 2, 3],),   # zero at the start
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── subarray-sum-equals-k: oracle(nums, k) ────────────────────────────────────

def _to_input_subarray_sum_k(nums, k):
    return f"{len(nums)} {_arr(nums)} {k}"


def _plan_subarray_sum_k(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_subarray_sum_k

    def gen_small():
        n = rng.randint(1, 8)
        return (tg.rand_int_array(rng, n, -5, 5), rng.randint(-10, 10))

    def gen_stress():
        n = rng.randint(2000, 6000)
        return (tg.rand_int_array(rng, n, -10, 10), rng.randint(-50, 50))

    visible = [
        ([1, 1, 1], 2), ([1, 2, 3], 3), ([1, -1, 0], 0), ([0], 0), ([1, 2, -3], 0),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([0], 1), ([5], 5), ([-5], -5), ([0, 0, 0], 0),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, -1, 1, -1, 1], 0),     # many zero-sum subarrays overlapping
        ([3, 4, 7, 2, -3, 1, 4, 2], 7),  # multiple valid subarrays of different lengths
        ([-1, -1, -1, -1], -2),     # negative running sums
        ([1, 2, 3, -3, -2, -1], 0),  # sum returns to zero repeatedly
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1], 1),      # single-element exact match
        ([2, -2], 0),  # cancels to zero over the whole array
        ([1, 2], 5),   # no subarray sums to k (answer 0)
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── top-k-frequent-elements: oracle(nums, k) — requires 1<=k<=distinct count ──

def _to_input_top_k_frequent(nums, k):
    return f"{len(nums)} {_arr(nums)} {k}"


def _plan_top_k_frequent(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_top_k_frequent

    def gen_small():
        distinct = rng.randint(1, 5)
        pool = rng.sample(range(1, 30), distinct)
        n = rng.randint(distinct, distinct + 6)
        nums = [rng.choice(pool) for _ in range(n)]
        # ensure every distinct value from pool appears at least once
        for v in pool:
            if v not in nums:
                nums.append(v)
        rng.shuffle(nums)
        k = rng.randint(1, distinct)
        return (nums, k)

    def gen_stress():
        distinct = rng.randint(200, 500)
        pool = list(range(distinct))
        n = rng.randint(distinct, distinct * 4)
        nums = [rng.choice(pool) for _ in range(n)]
        for v in pool:
            if v not in nums:
                nums.append(v)
        rng.shuffle(nums)
        k = rng.randint(1, distinct)
        return (nums, k)

    visible = [
        ([1, 1, 1, 2, 2, 3], 2),
        ([1], 1),
        ([4, 4, 4, 4], 1),
        ([5, 5, 6, 6, 7, 7], 2),
        ([1, 1, 2, 3], 2),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([1], 1),
        ([1, 2], 2),
        ([9, 9, 9], 1),
        ([1, 2, 3], 3),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, 2, 3, 4, 5], 3),           # all equal frequency -- must break ties by value
        ([5, 5, 1, 1, 3, 3, 2], 2),      # tied frequencies, must pick smaller values first
        ([9, 9, 9, 1, 2, 3], 2),         # one dominant, rest tied
        ([2, 2, 1, 1, 3, 3, 4, 4], 3),   # all pairs tied, ascending tie-break matters
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 1, 2, 2, 3], 2),   # tie between 1 and 2, must pick smaller-valued tie first
        ([3, 3, 1, 1], 1),      # tie for the only slot -- picks value 1
        ([2, 2, 2, 1], 2),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── longest-consecutive-sequence: oracle(nums) — nums may be empty ───────────

def _to_input_longest_consecutive(nums):
    return f"{len(nums)} {_arr(nums)}".rstrip()


def _plan_longest_consecutive(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_longest_consecutive

    def gen_small():
        n = rng.randint(1, 10)
        return (tg.rand_int_array(rng, n, -20, 20),)

    def gen_stress():
        n = rng.randint(2000, 8000)
        return (tg.rand_int_array(rng, n, -5000, 5000),)

    visible = [
        ([100, 4, 200, 1, 3, 2],), ([0, 3, 7, 2, 5, 8, 4, 6, 0, 1],), ([],), ([5],), ([1, 2, 0, 1],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([],), ([1],), ([1, 1],), ([-1, 0, 1],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (list(range(20)),),                       # one long consecutive run
        ([1, 3, 5, 7, 9, 11],),                    # no consecutive pairs at all (all odd, gaps of 2)
        (list(range(0, 10)) + list(range(100, 110)),),  # two disjoint equal-length runs
        ([5, 5, 5, 6, 6, 7],),                     # heavy duplicates within the run
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 2],),      # minimal run of length 2
        ([1, 3],),      # gap of 2, not consecutive
        ([-1, 0],),     # run crossing zero
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── group-anagrams-count: oracle(strs) ────────────────────────────────────────

def _to_input_group_anagrams(strs):
    n = len(strs)
    return "\n".join([str(n)] + list(strs))


def _plan_group_anagrams(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_group_anagrams

    def _rand_word(n):
        return tg.rand_string(rng, n, "abc")

    def gen_small():
        n = rng.randint(1, 8)
        return ([_rand_word(rng.randint(1, 5)) for _ in range(n)],)

    def gen_stress():
        n = rng.randint(1000, 3000)
        return ([_rand_word(rng.randint(1, 6)) for _ in range(n)],)

    visible = [
        (["eat", "tea", "tan", "ate", "nat", "bat"],),
        ([""],),
        (["a", "a", "a"],),
        (["ab", "ba", "cd", "dc"],),
        (["abc", "bca", "cab", "xyz"],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        (["a"],),
        (["", ""],),
        (["z", "y"],),
        (["ab"],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (["abc", "bca", "cab", "acb", "bac", "cba"],),   # all 6 permutations of one word, one group
        (["aab", "aba", "baa", "abb", "bab", "bba"],),   # two anagram classes mixed together
        (["a"] * 10,),                                    # many identical single-char strings
        (["abcd", "dcba", "abdc", "wxyz"],),              # near-anagrams that aren't quite matches
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        (["ab", "ba"],),     # exactly one anagram pair -> 1 group
        (["ab", "ac"],),     # look similar but aren't anagrams -> 2 groups
        (["aa", "aa"],),     # identical strings still just one group
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── valid-anagram: oracle(s, t) ────────────────────────────────────────────────

def _to_input_valid_anagram(s, t):
    return f"{s}\n{t}"


def _plan_valid_anagram(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_valid_anagram

    def gen_small():
        n = rng.randint(1, 8)
        s = tg.rand_string(rng, n, "abc")
        if rng.random() < 0.5:
            t = "".join(rng.sample(s, len(s))) if len(set(s)) > 1 else s
        else:
            t = tg.rand_string(rng, rng.randint(1, 8), "abc")
        return (s, t)

    def gen_stress():
        n = rng.randint(3000, 8000)
        s = tg.rand_string(rng, n, "abcdefghijklmnopqrstuvwxyz")
        t = "".join(rng.sample(s, len(s)))
        return (s, t)

    visible = [
        ("anagram", "nagaram"), ("rat", "car"), ("a", "a"), ("ab", "aa"), ("abc", "cab"),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ("a", "b"), ("ab", "ba"), ("a", "aa"), ("aa", "a"),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("aabbcc", "abcabc"),     # true anagram with repeated chars, shuffled
        ("aabbcc", "aabbcd"),     # one character off despite matching length
        ("aaaa", "aaab"),         # same length, one char frequency differs
        ("abcdef", "fedcba"),     # full reversal, still an anagram
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("ab", "ab"),     # identical strings
        ("aab", "aba"),   # true anagram, reordered
        ("aab", "abb"),   # same length, different multiset
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── first-unique-character-index: oracle(s) ───────────────────────────────────

def _to_input_first_unique(s):
    return s


def _plan_first_unique(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_first_unique

    def gen_small():
        n = rng.randint(1, 10)
        return (tg.rand_string(rng, n, "abc"),)

    def gen_stress():
        n = rng.randint(3000, 8000)
        return (tg.rand_string(rng, n, "abcdefghijklmnopqrstuvwxyz"),)

    visible = [
        ("leetcode",), ("loveleetcode",), ("aabb",), ("z",), ("cccats",),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ("a",), ("aa",), ("ab",), ("ba",),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("aabbccd",),      # unique char is at the very end
        ("xaabbcc",),      # unique char is at the very start
        ("aabbccxx",),     # no unique character exists at all
        ("abababc",),      # unique char buried among many repeats
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("aa",),    # no unique char -> -1
        ("ba",),    # unique char at index 0
        ("ab",),    # unique char at index 0, both technically unique but first wins
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── intersection-of-two-arrays: oracle(nums1, nums2) — either may be empty ───

def _to_input_intersection(nums1, nums2):
    return f"{len(nums1)} {_arr(nums1)} {len(nums2)} {_arr(nums2)}".replace("  ", " ").strip()


def _plan_intersection(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_intersection

    def gen_small():
        n1 = rng.randint(0, 6)
        n2 = rng.randint(0, 6)
        return (tg.rand_int_array(rng, n1, 0, 10), tg.rand_int_array(rng, n2, 0, 10))

    def gen_stress():
        n1 = rng.randint(500, 1000)
        n2 = rng.randint(500, 1000)
        return (tg.rand_int_array(rng, n1, 0, 2000), tg.rand_int_array(rng, n2, 0, 2000))

    visible = [
        ([1, 2, 2, 1], [2, 2]),
        ([4, 9, 5], [9, 4, 9, 8, 4]),
        ([], [1, 2]),
        ([1, 2], []),
        ([1, 2, 3], [3, 4, 5]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([], []),
        ([1], [1]),
        ([1], [2]),
        ([0], [0]),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, 1, 1, 1], [1, 1]),           # heavy duplicates on both sides, answer is still just {1}
        ([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]),  # same set, reversed order
        ([1, 2, 3], [4, 5, 6]),           # completely disjoint
        (list(range(50)), list(range(25, 75))),  # partial overlap band
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 2], [2, 3]),   # partial overlap of one element
        ([2, 2], [2]),      # duplicate-heavy vs single occurrence
        ([1], []),          # one side empty
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── missing-number: oracle(nums) — n distinct values from [0, n] missing one ──

def _to_input_missing_number(nums):
    return f"{len(nums)} {_arr(nums)}"


def _plan_missing_number(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_missing_number

    def gen_small():
        n = rng.randint(1, 10)
        full = list(range(n + 1))
        missing = rng.choice(full)
        nums = [x for x in full if x != missing]
        rng.shuffle(nums)
        return (nums,)

    def gen_stress():
        n = rng.randint(3000, 8000)
        full = list(range(n + 1))
        missing = rng.choice(full)
        nums = [x for x in full if x != missing]
        rng.shuffle(nums)
        return (nums,)

    visible = [
        ([3, 0, 1],), ([0, 1],), ([9, 6, 4, 2, 3, 5, 7, 0, 1],), ([0],), ([1, 0, 3],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([1],),   # missing 0
        ([0],),   # missing 1
        ([0, 1],),  # missing 2
        ([1, 2],),  # missing 0
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (list(range(1, 11)),),        # missing the smallest value 0
        (list(range(10)),),           # missing the largest value 10
        (list(range(5)) + list(range(6, 11)),),  # missing a middle value
        ([0] + list(range(2, 11)),),  # missing value adjacent to duplicated-looking edge
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1],),  # smallest possible input, missing 0
        ([0],),  # smallest possible input, missing 1
        ([2, 0],),  # missing 1, out of order
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── majority-element-ii: oracle(nums) ─────────────────────────────────────────

def _to_input_majority_ii(nums):
    return f"{len(nums)} {_arr(nums)}"


def _plan_majority_ii(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_majority_ii

    def gen_small():
        n = rng.randint(1, 9)
        return (tg.rand_int_array(rng, n, 1, 4),)

    def gen_stress():
        n = rng.randint(3000, 9000)
        return (tg.rand_int_array(rng, n, 1, 50),)

    visible = [
        ([3, 2, 3],), ([1],), ([1, 2, 3],), ([1, 2, 1, 3, 1, 4],), ([2, 2, 2, 3, 3],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([1],), ([1, 1],), ([1, 2],), ([1, 1, 1],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, 1, 2, 2, 3, 3],),          # exactly at the n/3 boundary for three values, none qualify
        ([1, 1, 1, 2, 2, 2, 3],),       # two values tie right above n/3
        ([5] * 7 + [6] * 6,),           # one clear majority plus one near-miss
        ([1, 2, 3, 4, 5, 6, 7],),       # all distinct, no majority at all
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 1, 1],),      # single value fills whole array
        ([1, 1, 2, 2],),   # two values tied at exactly half each
        ([1, 2, 2],),      # only one qualifies
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── two-sum-count-pairs: oracle(nums, target) — nums may be empty ────────────

def _to_input_two_sum_count(nums, target):
    return f"{len(nums)} {_arr(nums)} {target}".replace("  ", " ")


def _plan_two_sum_count(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_two_sum_count

    def gen_small():
        n = rng.randint(0, 8)
        return (tg.rand_int_array(rng, n, -5, 5), rng.randint(-10, 10))

    def gen_stress():
        n = rng.randint(2000, 6000)
        return (tg.rand_int_array(rng, n, -100, 100), rng.randint(-200, 200))

    visible = [
        ([1, 1, 1], 2), ([1, 5, 3, 3, 3], 6), ([], 5), ([3, 3], 6), ([2, 4, 6], 8),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([], 0), ([1], 2), ([1], 1), ([0, 0], 0),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([3, 3, 3, 3], 6),           # every pair among duplicates counts
        ([-1, 1, -1, 1], 0),         # negative and positive pairing to zero
        ([5, 5, 5, 5, 5], 10),       # C(5,2) pairs summing correctly
        ([1, 2, 3, 4, 5], 100),      # target unreachable -> answer 0
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([2, 2], 4),    # self-pair via duplicate values, not doubling one index
        ([2], 4),       # single element can't pair with itself
        ([1, 3, 2], 4),  # exactly one valid pair among three
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── subarray-sums-divisible-by-k: oracle(nums, k) — requires k != 0 ──────────

def _to_input_subarray_div_k(nums, k):
    return f"{len(nums)} {_arr(nums)} {k}"


def _plan_subarray_div_k(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_subarray_div_k

    def gen_small():
        n = rng.randint(1, 8)
        return (tg.rand_int_array(rng, n, -10, 10), rng.randint(1, 10))

    def gen_stress():
        n = rng.randint(2000, 6000)
        return (tg.rand_int_array(rng, n, -50, 50), rng.randint(1, 100))

    visible = [
        ([4, 5, 0, -2, -3, 1], 5), ([5], 9), ([1, 2, 3], 3), ([-1, 2, 9, -1], 2), ([2, 4, 6], 2),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([0], 1), ([1], 1), ([-1], 1), ([5], 100000),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([0, 0, 0, 0],  5),         # all-zero array, every subarray divisible
        ([-5, -5, -5], 5),          # negative sums modulo k
        ([1, 2, 3, 4, 5, 6, 7], 7),  # many overlapping remainder-0 windows
        ([-3, 1, 4, -1, 5, -9, 2, 6], 5),  # mixed sign running sums
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1], 1),    # trivially divisible (k=1 matches everything)
        ([1, 1], 2),  # single subarray of two elements divisible
        ([3, 3, 3], 3),  # every prefix divisible
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── three-sum-count-triplets: oracle(nums) — needs length >= 3 ───────────────

def _to_input_three_sum(nums):
    return f"{len(nums)} {_arr(nums)}"


def _plan_three_sum(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_three_sum

    def gen_small():
        n = rng.randint(3, 9)
        return (tg.rand_int_array(rng, n, -6, 6),)

    def gen_stress():
        n = rng.randint(400, 900)
        return (tg.rand_int_array(rng, n, -100, 100),)

    visible = [
        ([-1, 0, 1, 2, -1, -4],), ([0, 1, 1],), ([0, 0, 0],), ([1, 2, 3, 4],), ([-2, 0, 2],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([0, 0, 0],), ([1, 2, 3],), ([-1, -1, 2],), ([0, 0, 1],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([0] * 9,),                              # all zeros -> exactly one distinct triplet (0,0,0)
        ([-4, -1, -1, 0, 1, 2],),                 # duplicate values require distinct-triplet dedup
        ([3, -2, 1, 0, -1, -1, 2, -3],),          # multiple overlapping candidate triplets
        (list(range(-5, 5)),),                    # a long consecutive range around zero
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([-1, 0, 1],),   # minimal single valid triplet
        ([1, -1, 0, 0],),  # duplicate zero must not double-count triplet (0,0, ... )
        ([2, -1, -1],),  # duplicate value forming a valid triplet
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── container-with-most-water: oracle(heights) — needs length >= 2 ───────────

def _to_input_container(heights):
    return f"{len(heights)} {_arr(heights)}"


def _plan_container(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_container

    def gen_small():
        n = rng.randint(2, 9)
        return (tg.rand_int_array(rng, n, 0, 20),)

    def gen_stress():
        n = rng.randint(2000, 6000)
        return (tg.rand_int_array(rng, n, 0, 100000),)

    visible = [
        ([1, 8, 6, 2, 5, 4, 8, 3, 7],), ([1, 1],), ([4, 3],), ([1, 2, 4, 3, 5],), ([3, 9, 3],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([0, 0],), ([0, 5],), ([5, 0],), ([1, 1],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([5, 4, 3, 2, 1, 5],),          # equal end heights beat a taller interior bar
        (list(range(1, 11)),),          # strictly increasing heights
        (list(range(10, 0, -1)),),      # strictly decreasing heights
        ([1, 100, 1, 1, 1, 100, 1],),   # two tall towers far apart with short bars between
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 2, 1],),     # picking the tallest bars isn't always optimal
        ([2, 1, 2],),     # equal end heights, short middle
        ([1, 3, 2, 5, 25, 24, 5],),  # classic trap for greedy-by-height mistakes
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── registry ───────────────────────────────────────────────────────────────────

ARRAY_HASHING_TEST_PLANS: dict[str, tuple] = {
    # slug -> (to_input, format_output, plan_fn)
    "contains-duplicate-within-k": (_to_input_contains_dup, lambda a: "true" if a else "false", _plan_contains_dup),
    "product-of-array-except-self": (_to_input_product_except_self, lambda a: " ".join(map(str, a)), _plan_product_except_self),
    "subarray-sum-equals-k": (_to_input_subarray_sum_k, str, _plan_subarray_sum_k),
    "top-k-frequent-elements": (_to_input_top_k_frequent, lambda a: " ".join(map(str, a)), _plan_top_k_frequent),
    "longest-consecutive-sequence": (_to_input_longest_consecutive, str, _plan_longest_consecutive),
    "group-anagrams-count": (_to_input_group_anagrams, str, _plan_group_anagrams),
    "valid-anagram": (_to_input_valid_anagram, lambda a: "true" if a else "false", _plan_valid_anagram),
    "first-unique-character-index": (_to_input_first_unique, str, _plan_first_unique),
    "intersection-of-two-arrays": (_to_input_intersection, lambda a: " ".join(map(str, a)), _plan_intersection),
    "missing-number": (_to_input_missing_number, str, _plan_missing_number),
    "majority-element-ii": (_to_input_majority_ii, lambda a: " ".join(map(str, a)), _plan_majority_ii),
    "two-sum-count-pairs": (_to_input_two_sum_count, str, _plan_two_sum_count),
    "subarray-sums-divisible-by-k": (_to_input_subarray_div_k, str, _plan_subarray_div_k),
    "three-sum-count-triplets": (_to_input_three_sum, str, _plan_three_sum),
    "container-with-most-water": (_to_input_container, str, _plan_container),
}
