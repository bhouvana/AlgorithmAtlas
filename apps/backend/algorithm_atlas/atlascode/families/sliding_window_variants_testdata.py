"""
40-test case plans for the `sliding-window-variants` family (see testgen.py
for the shared bucket contract: visible 5 / basic 7 / boundary 8 /
adversarial 8 / mutation 7 / stress 5 = 40). One entry per slug in
sliding_window_variants.py's `_SPECS`.

Each `to_input` mirrors the exact stdin format sliding_window_variants.py's
builder already used (verified against the original hand-written
`_Spec.cases` before writing this).
"""
from __future__ import annotations

import random

from .. import testgen as tg


def _arr(xs) -> str:
    return " ".join(str(x) for x in xs)


def _fmt_int_list(xs) -> str:
    return " ".join(str(x) for x in xs) if xs else ""


# ── max-sum-subarray-fixed-k: oracle(nums, k), 1 <= k <= len(nums) ───────────

def _to_input_fixed_k(nums, k):
    return f"{len(nums)} {_arr(nums)} {k}"


def _plan_max_sum_subarray_fixed_k(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_fixed_k

    def gen_small():
        n = rng.randint(1, 10)
        k = rng.randint(1, n)
        return (tg.rand_int_array(rng, n, -20, 20), k)

    def gen_stress():
        n = rng.randint(50_000, 100_000)
        k = rng.randint(1, n)
        return (tg.rand_int_array(rng, n, -1000, 1000), k)

    visible = [
        ([2, 1, 5, 1, 3, 2], 3), ([2, 3, 4, 1, 5], 2), ([7], 1), ([-1, -2, -3, -4], 2),
        ([5, 5, 5, 5], 2),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([5], 1), ([1, 2], 2), ([1, 2, 3], 3), ([-5, -5], 1),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([-1, -1, -1, 10, -1], 1),        # single huge spike surrounded by negatives
        ([10, -10, 10, -10, 10], 2),      # oscillating values around zero
        ([-5, -4, -3, -2, -1], 3),        # all negative — max is least negative window
        (list(range(20, 0, -1)), 5),      # strictly descending
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 1, 1, 1], 4),  # k == n (whole array is the only window)
        ([3, -1, 4], 1),    # k == 1 (degenerates to max element)
        ([1, 2, 3, 4, 5], 4),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── min-subarray-len-target-sum: oracle(nums, target), nums[i] >= 1, target >= 1 ──

def _to_input_min_len(nums, target):
    return f"{len(nums)} {_arr(nums)} {target}"


def _plan_min_subarray_len(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_min_len

    def gen_small():
        n = rng.randint(1, 10)
        nums = tg.rand_int_array(rng, n, 1, 10)
        target = rng.randint(1, sum(nums) + 5)
        return (nums, target)

    def gen_stress():
        n = rng.randint(50_000, 100_000)
        nums = tg.rand_int_array(rng, n, 1, 100)
        target = rng.randint(1, sum(nums))
        return (nums, target)

    visible = [
        ([2, 3, 1, 2, 4, 3], 7), ([1, 4, 4], 4), ([1, 1, 1, 1], 11), ([5], 5),
        ([1, 2, 3, 4, 5], 15),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([5], 1), ([5], 5), ([5], 6), ([1], 1),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1] * 20, 1),                    # smallest possible window (length 1) buried in many
        ([10, 1, 1, 1, 1, 1, 1, 1, 1, 1], 10),  # a single large element already meets target
        ([1, 1, 1, 1, 1, 1, 1, 1, 1, 100], 100),  # target only reachable via the last huge element
        (list(range(1, 11)), 55),          # target == exact total sum (whole array required)
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 1, 1, 1], 5),   # target exceeds total sum -> must print 0
        ([2, 2, 2], 6),      # target == total sum exactly
        ([3, 1, 1, 1], 3),   # first element alone already satisfies target
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── longest-substring-without-repeating: oracle(s) ────────────────────────────

def _to_input_single_str(s):
    return s


def _plan_longest_substring_without_repeat(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_single_str

    def gen_small():
        n = rng.randint(1, 12)
        return (tg.rand_string(rng, n, "abc"),)

    def gen_stress():
        n = rng.randint(20_000, 50_000)
        return (tg.rand_string(rng, n, "abcdefghijklmnopqrstuvwxyz"),)

    visible = [("abcabcbb",), ("bbbbb",), ("pwwkew",), ("",), ("abcdef",)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [("",), ("a",), ("aa",), ("ab",)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("abba",),        # repeat reappears just after the window moved past it once
        ("tmmzuxt",),     # classic tricky case (repeat far back, must not double-shrink)
        ("a" * 30 + "b",),  # long uniform run then a single distinct char
        ("abcabcabcabc",),  # periodic repeats
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("au",),      # repeat pointer must not go before current window's left
        ("dvdf",),    # classic off-by-one trap for last_seen[c] >= left check
        ("abba",),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── longest-substring-at-most-k-distinct: oracle(s, k), k >= 0 ───────────────

def _to_input_str_k(s, k):
    return f"{s} {k}"


def _plan_longest_substring_at_most_k_distinct(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_str_k

    def gen_small():
        n = rng.randint(1, 12)
        k = rng.randint(0, 5)
        return (tg.rand_string(rng, n, "abcde"), k)

    def gen_stress():
        n = rng.randint(20_000, 50_000)
        k = rng.randint(1, 26)
        return (tg.rand_string(rng, n, "abcdefghijklmnopqrstuvwxyz"), k)

    visible = [("eceba", 2), ("aa", 1), ("a", 0), ("abcabcabc", 3), ("abaccc", 2)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [("a", 0), ("a", 1), ("a", 2), ("ab", 0)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("aaaaabbbbb", 1),   # exactly 2 runs; k=1 forces picking one run only
        ("abcabcabc", 1),    # highly interleaved distinct chars, k=1
        ("a" * 15 + "b" * 15, 2),  # two long runs, k=2 allows whole string
        ("abcdefghij", 5),   # all-distinct string, k less than total distinct count
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("aabbcc", 2),   # window must shrink exactly when distinct count exceeds k
        ("aaa", 0),      # k=0 must yield 0 regardless of string
        ("abac", 2),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── longest-repeating-char-replacement: oracle(s, k), k >= 0, uppercase only ──

def _plan_longest_repeating_char_replacement(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_str_k

    def gen_small():
        n = rng.randint(1, 12)
        k = rng.randint(0, n)
        return (tg.rand_string(rng, n, "ABC"), k)

    def gen_stress():
        n = rng.randint(20_000, 50_000)
        k = rng.randint(0, n)
        return (tg.rand_string(rng, n, "ABCDEFGHIJKLMNOPQRSTUVWXYZ"), k)

    visible = [("ABAB", 2), ("AABABBA", 1), ("A", 0), ("AAAA", 5), ("ABCD", 3)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [("A", 0), ("A", 1), ("AB", 0), ("AB", 1)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("ABABABAB", 0),        # k=0 — window can never grow past 1 unique run
        ("ABABABAB", 100),      # k huge — whole string replaceable
        ("AAAABBBBCCCC", 4),    # exactly enough flips to merge two runs
        ("A" * 20 + "B" * 20, 1),  # long uniform runs joined by a small budget
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("AABA", 0),   # window shrink triggered by max_count staying stale
        ("AAAB", 0),
        ("ABBB", 1),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── max-consecutive-ones-with-k-flips: oracle(nums binary array, k), k >= 0 ──

def _to_input_binary_k(nums, k):
    return f"{len(nums)} {_arr(nums)} {k}"


def _plan_max_consecutive_ones_with_k_flips(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_binary_k

    def gen_small():
        n = rng.randint(1, 12)
        nums = [rng.randint(0, 1) for _ in range(n)]
        k = rng.randint(0, n)
        return (nums, k)

    def gen_stress():
        n = rng.randint(50_000, 100_000)
        nums = [rng.randint(0, 1) for _ in range(n)]
        k = rng.randint(0, n)
        return (nums, k)

    visible = [
        ([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2), ([0, 0, 1, 1, 0, 0], 0), ([0], 5),
        ([1, 1, 1, 1, 1], 0), ([0, 0, 0], 1),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([0], 0), ([1], 0), ([0], 1), ([1, 0], 1)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([0] * 10, 3),                 # k less than total zeros — window can't cover all
        ([0] * 10, 10),                # k equal to total length — whole array flips to ones
        ([1, 0, 1, 0, 1, 0, 1, 0], 2), # alternating pattern, small budget
        ([1] * 5 + [0] * 5 + [1] * 5, 5),  # two runs of ones separated by a gap exactly k wide
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([0, 0, 1, 1, 0], 1),  # shrink boundary — zeros count vs k off-by-one
        ([1, 0, 0, 1], 2),
        ([0, 1, 0, 1, 0], 2),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── minimum-window-substring-length: oracle(s, t), t non-empty ────────────────

def _to_input_two_lines(s, t):
    return f"{s}\n{t}"


def _plan_minimum_window_length(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_two_lines

    def gen_small():
        s = tg.rand_string(rng, rng.randint(1, 15), "abc")
        t = tg.rand_string(rng, rng.randint(1, 4), "abc")
        return (s, t)

    def gen_stress():
        s = tg.rand_string(rng, rng.randint(20_000, 40_000), "abcdefghij")
        t = tg.rand_string(rng, rng.randint(1, 100), "abcdefghij")
        return (s, t)

    visible = [
        ("ADOBECODEBANC", "ABC"), ("a", "a"), ("a", "aa"), ("aa", "aa"), ("ab", "b"),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [("a", "a"), ("a", "b"), ("ab", "a"), ("ab", "ab")]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("aaaaaaaaaa", "aaa"),        # t needs multiplicity, not just presence
        ("abcabcabc", "cba"),         # t's chars scattered, order-independent match
        ("a" * 20 + "bcd", "abcd"),   # window must span almost the whole string
        ("xyz", "abc"),                # t's characters never appear -> no valid window
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("aa", "aa"),   # multiplicity exactly matches — no slack
        ("aab", "ab"),  # extra duplicate char before the valid window
        ("abc", "cba"),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── find-all-anagrams-in-string: oracle(s, p) ─────────────────────────────────

def _plan_find_all_anagram_starts(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_two_lines

    def gen_small():
        s = tg.rand_string(rng, rng.randint(1, 15), "ab")
        p = tg.rand_string(rng, rng.randint(1, 4), "ab")
        return (s, p)

    def gen_stress():
        s = tg.rand_string(rng, rng.randint(10_000, 30_000), "abcde")
        p = tg.rand_string(rng, rng.randint(1, 50), "abcde")
        return (s, p)

    visible = [
        ("cbaebabacd", "abc"), ("abab", "ab"), ("a", "ab"), ("aaaaaaaaaa", "aaa"),
        ("abcabc", "cab"),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [("a", "a"), ("a", "b"), ("ab", "a"), ("ab", "ab")]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("aaaaaaaaaa", "aa"),        # overlapping anagram windows everywhere
        ("abababab", "ba"),          # alternating pattern, many matches
        ("a" * 15 + "b" * 15, "ab"),  # anagram exists only at the exact boundary
        ("xyz" * 5, "zyx"),           # p is a permutation, repeated block structure
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("ab", "ab"),   # p length == s length, single boundary check
        ("aab", "ab"),  # window slide by exactly one after a miss
        ("baa", "ab"),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── registry ───────────────────────────────────────────────────────────────────

SLIDING_WINDOW_TEST_PLANS: dict[str, tuple] = {
    # slug -> (to_input, format_output, plan_fn)
    "max-sum-subarray-fixed-k": (_to_input_fixed_k, str, _plan_max_sum_subarray_fixed_k),
    "min-subarray-len-target-sum": (_to_input_min_len, str, _plan_min_subarray_len),
    "longest-substring-without-repeating": (_to_input_single_str, str, _plan_longest_substring_without_repeat),
    "longest-substring-at-most-k-distinct": (_to_input_str_k, str, _plan_longest_substring_at_most_k_distinct),
    "longest-repeating-char-replacement": (_to_input_str_k, str, _plan_longest_repeating_char_replacement),
    "max-consecutive-ones-with-k-flips": (_to_input_binary_k, str, _plan_max_consecutive_ones_with_k_flips),
    "minimum-window-substring-length": (_to_input_two_lines, str, _plan_minimum_window_length),
    "find-all-anagrams-in-string": (_to_input_two_lines, _fmt_int_list, _plan_find_all_anagram_starts),
}
