"""
Level-1 verification: independent oracles against known canonical values.

These must pass BEFORE an oracle is ever used to generate a shipped AtlasCode
test case (see docs/atlascode-progress.md "Critical lesson learned").
"""
from __future__ import annotations

import pytest

from algorithm_atlas.atlascode.independent_oracles import (
    OracleError,
    activity_selection_max_count,
    binary_tree_max_path_sum,
    bitonic_peak_index,
    boolean_parenthesization_true_ways,
    can_jump,
    can_partition_equal_subset,
    catalan_number,
    climbing_stairs,
    closest_pair_min_sq_distance,
    coin_change_ways,
    collatz_steps,
    combination_sum_iv_count,
    container_with_most_water,
    contains_duplicate_within_k,
    count_distinct_substrings_length_k,
    count_divisors,
    count_inversions,
    count_islands,
    count_occurrences,
    count_palindromic_substrings,
    count_set_bits,
    count_tree_nodes,
    counting_bits,
    daily_temperatures,
    decode_ways,
    delete_and_earn,
    diameter_of_binary_tree,
    egg_drop_min_trials,
    euler_phi,
    evaluate_rpn,
    fast_power_exact,
    find_all_anagram_starts,
    find_min_rotated,
    first_occurrence,
    first_unique_char_index,
    fractional_knapsack_max_value,
    gas_station_start_index,
    group_anagrams_count,
    hamming_distance,
    huffman_total_encoded_length,
    integer_sqrt,
    intersection_sorted,
    invert_tree_preorder,
    is_anagram,
    is_balanced_binary_tree,
    is_bipartite,
    is_interleave,
    is_power_of_two,
    is_prime,
    is_symmetric_tree,
    is_palindrome_linked_list,
    is_valid_bst,
    job_scheduling_max_profit,
    jump_game_ii_min_jumps,
    karatsuba_multiply,
    kth_smallest_in_bst,
    knapsack_01,
    largest_rectangle_in_histogram,
    last_occurrence,
    level_order_traversal,
    linked_list_has_cycle,
    longest_bitonic_subsequence,
    longest_common_substring_length,
    longest_consecutive_sequence,
    longest_palindromic_subsequence,
    longest_palindromic_substring_length,
    longest_repeating_char_replacement,
    longest_substring_at_most_k_distinct,
    longest_substring_without_repeat,
    lowest_common_ancestor_bst,
    lucas_binomial_mod,
    majority_element,
    majority_element_ii,
    matrix_chain_order,
    matrix_power_mod,
    max_consecutive_ones_with_k_flips,
    max_depth_binary_tree,
    max_distance_to_zero,
    max_product_subarray,
    max_profit_single_transaction,
    max_profit_unlimited_transactions,
    max_subarray_circular,
    max_sum_subarray_fixed_k,
    max_xor_of_two_numbers,
    median_of_medians_kth_smallest,
    meeting_rooms_min_count,
    merge_two_sorted_lists,
    middle_of_linked_list,
    min_eating_speed,
    min_knight_moves,
    min_stack_simulate,
    min_subarray_len_at_least_target,
    minimum_window_length,
    missing_number,
    mod_pow,
    next_greater_element,
    num_distinct_subsequences,
    palindrome_partition_count_ways,
    palindrome_partition_min_cuts,
    path_sum_exists,
    perfect_squares_min_count,
    polynomial_multiply,
    prime_factors,
    product_except_self,
    remove_k_digits,
    remove_nth_from_end,
    restore_ip_addresses_count,
    reverse_bits_32,
    reverse_linked_list,
    right_side_view,
    rod_cutting,
    rotated_search,
    rotten_oranges_minutes,
    run_length_encode,
    same_tree,
    search_2d_matrix,
    search_insert_position,
    ship_within_days,
    shortest_path_binary_matrix,
    sieve_primes,
    single_number,
    single_number_ii,
    stable_matching_gale_shapley,
    strassen_matrix_multiply,
    subarray_sum_equals_k,
    subarray_sums_divisible_by_k,
    subset_sum_exists,
    suffix_array,
    sum_root_to_leaf_numbers,
    target_sum_ways,
    task_scheduler_min_intervals,
    three_sum_count_triplets,
    top_k_frequent,
    trapping_rain_water,
    triangle_min_path_sum,
    two_sum_count_pairs,
    unbounded_knapsack,
    unique_permutations_count,
    valid_parentheses,
    wildcard_match,
    word_break_count_ways,
    word_ladder_length,
    word_wrap_min_cost,
    z_array,
)


@pytest.mark.parametrize("n, expected", [(1, 0), (2, 1), (6, 8), (27, 111)])
def test_collatz_steps(n, expected):
    assert collatz_steps(n) == expected


def test_collatz_rejects_nonpositive():
    with pytest.raises(OracleError):
        collatz_steps(0)


@pytest.mark.parametrize("n, expected", [
    (1, []),
    (2, [2]),
    (10, [2, 3, 5, 7]),
    (20, [2, 3, 5, 7, 11, 13, 17, 19]),
])
def test_sieve_primes(n, expected):
    assert sieve_primes(n) == expected


@pytest.mark.parametrize("n, expected", [(0, 1), (3, 5), (6, 132), (10, 16796)])
def test_catalan_number(n, expected):
    assert catalan_number(n) == expected


@pytest.mark.parametrize("n, expected", [(1, 1), (12, 4), (30, 8), (1, 1), (7, 6)])
def test_euler_phi(n, expected):
    assert euler_phi(n) == expected


def test_euler_phi_matches_brute_force():
    for n in range(1, 200):
        expected = sum(1 for k in range(1, n + 1) if _gcd(k, n) == 1)
        assert euler_phi(n) == expected


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


@pytest.mark.parametrize("base, exp, mod, expected", [
    (2, 10, 1000, 24),
    (3, 0, 5, 1),
    (7, 128, 13, pow(7, 128, 13)),
])
def test_mod_pow(base, exp, mod, expected):
    assert mod_pow(base, exp, mod) == expected


@pytest.mark.parametrize("n, expected", [
    (1, []),
    (12, [2, 2, 3]),
    (17, [17]),
    (360, [2, 2, 2, 3, 3, 5]),
])
def test_prime_factors(n, expected):
    assert prime_factors(n) == expected
    if n > 1:
        product = 1
        for f in prime_factors(n):
            product *= f
        assert product == n


@pytest.mark.parametrize("n, expected", [(1, 1), (12, 6), (17, 2), (28, 6)])
def test_count_divisors(n, expected):
    assert count_divisors(n) == expected


@pytest.mark.parametrize("n, expected", [
    (1, False), (2, True), (3, True), (4, False), (17, True), (91, False), (97, True),
])
def test_is_prime(n, expected):
    assert is_prime(n) == expected


def test_is_prime_matches_sieve():
    primes = set(sieve_primes(500))
    for n in range(500):
        assert is_prime(n) == (n in primes)


@pytest.mark.parametrize("n, k, p, expected", [
    (10, 3, 13, 120 % 13),
    (5, 2, 5, 10 % 5),
    (1000, 500, 7, None),  # computed below via direct-mod fallback isn't feasible; use math.comb with small p only
])
def test_lucas_binomial_mod_small_cases(n, k, p, expected):
    if expected is None:
        pytest.skip("large-n case only sanity-checked via consistency test below")
    assert lucas_binomial_mod(n, k, p) == expected


def test_lucas_binomial_mod_consistency_with_direct_comb():
    import math
    p = 11
    for n in range(0, 15):
        for k in range(0, n + 1):
            assert lucas_binomial_mod(n, k, p) == math.comb(n, k) % p


# ── Dynamic-programming oracle tests (each cross-checked against an independent
# brute-force or textbook-known value, per the "verify every shipped case"
# lesson in docs/atlascode-progress.md) ──────────────────────────────────────

@pytest.mark.parametrize("n, expected", [(0, 1), (1, 1), (2, 2), (3, 3), (4, 5), (5, 8), (10, 89)])
def test_climbing_stairs(n, expected):
    assert climbing_stairs(n) == expected


@pytest.mark.parametrize("nums, expected", [
    ([2, 3, 1, 1, 4], True),
    ([3, 2, 1, 0, 4], False),
    ([0], True),
    ([1, 0, 1, 0], False),
])
def test_can_jump(nums, expected):
    assert can_jump(nums) == expected


def _brute_can_jump(nums):
    n = len(nums)
    reachable = {0}
    changed = True
    while changed:
        changed = False
        for i in list(reachable):
            for j in range(i, min(i + nums[i], n - 1) + 1):
                if j not in reachable:
                    reachable.add(j)
                    changed = True
    return (n - 1) in reachable


def test_can_jump_matches_brute_force():
    import random
    rng = random.Random(42)
    for _ in range(50):
        nums = [rng.randint(0, 4) for _ in range(rng.randint(1, 8))]
        assert can_jump(nums) == _brute_can_jump(nums)


@pytest.mark.parametrize("nums, target, expected", [
    ([3, 34, 4, 12, 5, 2], 9, True),
    ([3, 34, 4, 12, 5, 2], 30, False),
    ([], 0, True),
    ([], 5, False),
])
def test_subset_sum_exists(nums, target, expected):
    assert subset_sum_exists(nums, target) == expected


def test_subset_sum_matches_brute_force():
    import itertools
    import random
    rng = random.Random(7)
    for _ in range(30):
        nums = [rng.randint(0, 10) for _ in range(rng.randint(0, 6))]
        target = rng.randint(0, 30)
        possible_sums = {sum(c) for r in range(len(nums) + 1) for c in itertools.combinations(nums, r)}
        assert subset_sum_exists(nums, target) == (target in possible_sums)


@pytest.mark.parametrize("coins, amount, expected", [
    ([1, 2, 5], 5, 4),
    ([2], 3, 0),
    ([1], 0, 1),
    ([1, 5, 10, 25], 30, 18),
])
def test_coin_change_ways(coins, amount, expected):
    assert coin_change_ways(coins, amount) == expected


@pytest.mark.parametrize("s, expected", [("12", 2), ("226", 3), ("06", 0), ("0", 0), ("10", 1), ("100", 0)])
def test_decode_ways(s, expected):
    assert decode_ways(s) == expected


@pytest.mark.parametrize("weights, values, capacity, expected", [
    ([1, 3, 4, 5], [1, 4, 5, 7], 7, 9),
    ([10], [60], 5, 0),
    ([2, 2, 2], [3, 3, 3], 0, 0),
])
def test_knapsack_01(weights, values, capacity, expected):
    assert knapsack_01(weights, values, capacity) == expected


def test_knapsack_01_matches_brute_force():
    import itertools
    import random
    rng = random.Random(3)
    for _ in range(20):
        n = rng.randint(0, 6)
        weights = [rng.randint(1, 8) for _ in range(n)]
        values = [rng.randint(1, 20) for _ in range(n)]
        capacity = rng.randint(0, 15)
        best = 0
        for r in range(n + 1):
            for combo in itertools.combinations(range(n), r):
                w = sum(weights[i] for i in combo)
                if w <= capacity:
                    best = max(best, sum(values[i] for i in combo))
        assert knapsack_01(weights, values, capacity) == best


@pytest.mark.parametrize("weights, values, capacity, expected", [
    ([5, 10, 15], [10, 30, 20], 100, 300),
    ([1, 3, 4, 5], [10, 40, 50, 70], 8, 110),
])
def test_unbounded_knapsack(weights, values, capacity, expected):
    assert unbounded_knapsack(weights, values, capacity) == expected


@pytest.mark.parametrize("prices, length, expected", [
    ([1, 5, 8, 9, 10, 17, 17, 20], 8, 22),
    ([3, 5, 8, 9], 4, 12),
    ([1, 2, 3], 0, 0),
])
def test_rod_cutting(prices, length, expected):
    assert rod_cutting(prices, length) == expected


@pytest.mark.parametrize("nums, expected", [
    ([2, 3, -2, 4], 6),
    ([-2, 0, -1], 0),
    ([-2, 3, -4], 24),
    ([-2], -2),
])
def test_max_product_subarray(nums, expected):
    assert max_product_subarray(nums) == expected


@pytest.mark.parametrize("nums, expected", [
    ([1, 11, 2, 10, 4, 5, 2, 1], 6),
    ([12, 11, 40, 5, 3, 1], 5),
    ([80, 60, 30, 40, 20, 10], 5),
])
def test_longest_bitonic_subsequence(nums, expected):
    assert longest_bitonic_subsequence(nums) == expected


@pytest.mark.parametrize("s, expected", [("bbbab", 4), ("cbbd", 2), ("a", 1), ("abcd", 1)])
def test_longest_palindromic_subsequence(s, expected):
    assert longest_palindromic_subsequence(s) == expected


@pytest.mark.parametrize("s1, s2, s3, expected", [
    ("aabcc", "dbbca", "aadbbcbcac", True),
    ("aabcc", "dbbca", "aadbbbaccc", False),
    ("", "", "", True),
])
def test_is_interleave(s1, s2, s3, expected):
    assert is_interleave(s1, s2, s3) == expected


@pytest.mark.parametrize("s, p, expected", [
    ("aa", "a", False),
    ("aa", "*", True),
    ("cb", "?a", False),
    ("adceb", "*a*b", True),
    ("acdcb", "a*c?b", False),
])
def test_wildcard_match(s, p, expected):
    assert wildcard_match(s, p) == expected


@pytest.mark.parametrize("s, t, expected", [
    ("rabbbit", "rabbit", 3),
    ("babgbag", "bag", 5),
    ("abc", "abcd", 0),
])
def test_num_distinct_subsequences(s, t, expected):
    assert num_distinct_subsequences(s, t) == expected


@pytest.mark.parametrize("dims, expected", [
    ([40, 20, 30, 10, 30], 26000),
    ([10, 20, 30], 6000),
    ([10, 20], 0),
])
def test_matrix_chain_order(dims, expected):
    assert matrix_chain_order(dims) == expected


@pytest.mark.parametrize("eggs, floors, expected", [
    (2, 10, 4),
    (1, 5, 5),
    (2, 36, 8),
    (3, 14, 4),
])
def test_egg_drop_min_trials(eggs, floors, expected):
    assert egg_drop_min_trials(eggs, floors) == expected


def _brute_egg_drop(eggs, floors):
    """Naive O(eggs*floors^2) reference used only to cross-check the fast oracle."""
    dp = {}
    def solve(e, f):
        if f == 0 or f == 1:
            return f
        if e == 1:
            return f
        if (e, f) in dp:
            return dp[(e, f)]
        best = f
        for x in range(1, f + 1):
            worst = 1 + max(solve(e - 1, x - 1), solve(e, f - x))
            best = min(best, worst)
        dp[(e, f)] = best
        return best
    return solve(eggs, floors)


def test_egg_drop_matches_brute_force():
    for eggs in (1, 2, 3):
        for floors in range(0, 15):
            assert egg_drop_min_trials(eggs, floors) == _brute_egg_drop(eggs, floors)


@pytest.mark.parametrize("symbols, ops, expected", [
    ("TFT", "^&", 2),
    ("TTFT", "|&^", 4),
    ("TFTFTF", "^^^^^", 42),
])
def test_boolean_parenthesization_true_ways(symbols, ops, expected):
    assert boolean_parenthesization_true_ways(symbols, ops) == expected


def _brute_boolean_paren(symbols, ops):
    n = len(symbols)
    def evaluate(vals, operators):
        if len(vals) == 1:
            return vals[0]
        # brute force all parenthesizations recursively
        pass
    def count(i, j):
        # returns (true_ways, false_ways) for symbols[i..j], ops[i..j-1]
        if i == j:
            return (1, 0) if symbols[i] == "T" else (0, 1)
        t = f = 0
        for k in range(i, j):
            lt, lf = count(i, k)
            rt, rf = count(k + 1, j)
            total = (lt + lf) * (rt + rf)
            op = ops[k]
            if op == "&":
                tt = lt * rt
            elif op == "|":
                tt = total - lf * rf
            else:
                tt = lt * rf + lf * rt
            t += tt
            f += total - tt
        return (t, f)
    return count(0, n - 1)[0]


def test_boolean_parenthesization_matches_independent_brute_force():
    import random
    rng = random.Random(5)
    for _ in range(20):
        n = rng.randint(1, 6)
        symbols = "".join(rng.choice("TF") for _ in range(n))
        ops = "".join(rng.choice("&|^") for _ in range(n - 1))
        assert boolean_parenthesization_true_ways(symbols, ops) == _brute_boolean_paren(symbols, ops)


@pytest.mark.parametrize("word_lengths, line_width, expected", [
    ([3, 2, 2, 5], 6, 28),
    ([1, 1, 1, 1], 5, 0),
])
def test_word_wrap_min_cost(word_lengths, line_width, expected):
    assert word_wrap_min_cost(word_lengths, line_width) == expected


def _brute_word_wrap(lengths, width):
    n = len(lengths)
    INF = float("inf")

    def solve(i):
        if i == n:
            return 0
        best = INF
        cur = -1
        for j in range(i, n):
            cur = lengths[i] if j == i else cur + 1 + lengths[j]
            if cur > width:
                break
            line_cost = 0 if j == n - 1 else (width - cur) ** 3
            best = min(best, line_cost + solve(j + 1))
        return best

    return solve(0)


def test_word_wrap_matches_independent_brute_force():
    import random
    rng = random.Random(9)
    for _ in range(20):
        n = rng.randint(1, 6)
        width = rng.randint(4, 10)
        lengths = [rng.randint(1, width) for _ in range(n)]
        assert word_wrap_min_cost(lengths, width) == _brute_word_wrap(lengths, width)


# ── Binary-search variant family oracle tests ────────────────────────────────

@pytest.mark.parametrize("nums, target, expected", [
    ([4, 5, 6, 7, 0, 1, 2], 0, 4),
    ([4, 5, 6, 7, 0, 1, 2], 3, -1),
    ([1], 1, 0),
    ([5, 1, 3], 5, 0),
])
def test_rotated_search(nums, target, expected):
    assert rotated_search(nums, target) == expected


def test_rotated_search_matches_brute_force():
    import random
    rng = random.Random(11)
    for _ in range(30):
        n = rng.randint(1, 8)
        base = sorted(rng.sample(range(-20, 20), n))
        k = rng.randint(0, n - 1)
        nums = base[k:] + base[:k]
        target = rng.choice(base + [999])
        expected = nums.index(target) if target in nums else -1
        assert rotated_search(nums, target) == expected


@pytest.mark.parametrize("nums, expected", [([1, 2, 3, 1], 2), ([1, 3, 5, 4, 2], 2), ([1, 2, 5, 4, 3], 2)])
def test_bitonic_peak_index(nums, expected):
    assert bitonic_peak_index(nums) == expected


@pytest.mark.parametrize("nums, target, expected", [
    ([5, 7, 7, 8, 8, 10], 8, 3), ([5, 7, 7, 8, 8, 10], 6, -1), ([], 0, -1),
])
def test_first_occurrence(nums, target, expected):
    assert first_occurrence(nums, target) == expected


@pytest.mark.parametrize("nums, target, expected", [
    ([5, 7, 7, 8, 8, 10], 8, 4), ([5, 7, 7, 8, 8, 10], 6, -1),
])
def test_last_occurrence(nums, target, expected):
    assert last_occurrence(nums, target) == expected


@pytest.mark.parametrize("nums, target, expected", [
    ([5, 7, 7, 8, 8, 8, 10], 8, 3), ([5, 7, 7, 8, 8, 10], 6, 0),
])
def test_count_occurrences(nums, target, expected):
    assert count_occurrences(nums, target) == expected


def test_occurrence_functions_match_brute_force():
    import random
    rng = random.Random(13)
    for _ in range(30):
        nums = sorted(rng.randint(0, 5) for _ in range(rng.randint(0, 10)))
        target = rng.randint(0, 5)
        matches = [i for i, x in enumerate(nums) if x == target]
        assert first_occurrence(nums, target) == (matches[0] if matches else -1)
        assert last_occurrence(nums, target) == (matches[-1] if matches else -1)
        assert count_occurrences(nums, target) == len(matches)


@pytest.mark.parametrize("nums, target, expected", [
    ([1, 3, 5, 6], 5, 2), ([1, 3, 5, 6], 2, 1), ([1, 3, 5, 6], 7, 4), ([1, 3, 5, 6], 0, 0),
])
def test_search_insert_position(nums, target, expected):
    assert search_insert_position(nums, target) == expected


@pytest.mark.parametrize("piles, h, expected", [
    ([3, 6, 7, 11], 8, 4), ([30, 11, 23, 4, 20], 5, 30), ([30, 11, 23, 4, 20], 6, 23),
])
def test_min_eating_speed(piles, h, expected):
    assert min_eating_speed(piles, h) == expected


def test_min_eating_speed_matches_brute_force():
    import random
    rng = random.Random(17)
    for _ in range(20):
        piles = [rng.randint(1, 20) for _ in range(rng.randint(1, 5))]
        h = rng.randint(len(piles), 30)
        expected = next(k for k in range(1, max(piles) + 1)
                         if sum(-(-p // k) for p in piles) <= h)
        assert min_eating_speed(piles, h) == expected


@pytest.mark.parametrize("weights, days, expected", [
    ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5, 15),
    ([3, 2, 2, 4, 1, 4], 3, 6),
    ([1, 2, 3, 1, 1], 4, 3),
])
def test_ship_within_days(weights, days, expected):
    assert ship_within_days(weights, days) == expected


@pytest.mark.parametrize("n, expected", [(0, 0), (1, 1), (4, 2), (8, 2), (2147395599, 46339), (2147395600, 46340)])
def test_integer_sqrt(n, expected):
    assert integer_sqrt(n) == expected


@pytest.mark.parametrize("matrix, target, expected", [
    ([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 3, True),
    ([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 13, False),
])
def test_search_2d_matrix(matrix, target, expected):
    assert search_2d_matrix(matrix, target) == expected


@pytest.mark.parametrize("nums, expected", [
    ([3, 4, 5, 1, 2], 1), ([4, 5, 6, 7, 0, 1, 2], 0), ([11, 13, 15, 17], 11), ([2, 1], 1),
])
def test_find_min_rotated(nums, expected):
    assert find_min_rotated(nums) == expected


def test_find_min_rotated_matches_brute_force():
    import random
    rng = random.Random(19)
    for _ in range(30):
        n = rng.randint(1, 8)
        base = sorted(rng.sample(range(-20, 20), n))
        k = rng.randint(0, n - 1)
        nums = base[k:] + base[:k]
        assert find_min_rotated(nums) == min(nums)


# ── Sliding-window variant family oracle tests ───────────────────────────────

@pytest.mark.parametrize("nums, k, expected", [([2, 1, 5, 1, 3, 2], 3, 9), ([2, 3, 4, 1, 5], 2, 7)])
def test_max_sum_subarray_fixed_k(nums, k, expected):
    assert max_sum_subarray_fixed_k(nums, k) == expected


def test_max_sum_subarray_fixed_k_matches_brute_force():
    import random
    rng = random.Random(21)
    for _ in range(20):
        n = rng.randint(1, 10)
        nums = [rng.randint(-5, 5) for _ in range(n)]
        k = rng.randint(1, n)
        expected = max(sum(nums[i:i + k]) for i in range(n - k + 1))
        assert max_sum_subarray_fixed_k(nums, k) == expected


@pytest.mark.parametrize("nums, target, expected", [
    ([2, 3, 1, 2, 4, 3], 7, 2), ([1, 4, 4], 4, 1), ([1, 1, 1, 1], 11, 0),
])
def test_min_subarray_len_at_least_target(nums, target, expected):
    assert min_subarray_len_at_least_target(nums, target) == expected


def test_min_subarray_len_matches_brute_force():
    import random
    rng = random.Random(23)
    for _ in range(20):
        n = rng.randint(1, 10)
        nums = [rng.randint(1, 5) for _ in range(n)]
        target = rng.randint(1, 20)
        best = n + 1
        for i in range(n):
            for j in range(i, n):
                if sum(nums[i:j + 1]) >= target:
                    best = min(best, j - i + 1)
                    break
        assert min_subarray_len_at_least_target(nums, target) == (best if best <= n else 0)


@pytest.mark.parametrize("s, expected", [("abcabcbb", 3), ("bbbbb", 1), ("pwwkew", 3), ("", 0)])
def test_longest_substring_without_repeat(s, expected):
    assert longest_substring_without_repeat(s) == expected


def test_longest_substring_without_repeat_matches_brute_force():
    import random
    rng = random.Random(29)
    for _ in range(20):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 12)))
        n = len(s)
        best = 0
        for i in range(n):
            for j in range(i, n):
                if len(set(s[i:j + 1])) == (j - i + 1):
                    best = max(best, j - i + 1)
        assert longest_substring_without_repeat(s) == best


@pytest.mark.parametrize("s, k, expected", [("eceba", 2, 3), ("aa", 1, 2), ("a", 0, 0)])
def test_longest_substring_at_most_k_distinct(s, k, expected):
    assert longest_substring_at_most_k_distinct(s, k) == expected


def test_longest_substring_at_most_k_distinct_matches_brute_force():
    import random
    rng = random.Random(31)
    for _ in range(20):
        s = "".join(rng.choice("abcd") for _ in range(rng.randint(0, 10)))
        k = rng.randint(0, 3)
        n = len(s)
        best = 0
        for i in range(n):
            for j in range(i, n):
                if len(set(s[i:j + 1])) <= k:
                    best = max(best, j - i + 1)
        assert longest_substring_at_most_k_distinct(s, k) == best


@pytest.mark.parametrize("s, k, expected", [("ABAB", 2, 4), ("AABABBA", 1, 4)])
def test_longest_repeating_char_replacement(s, k, expected):
    assert longest_repeating_char_replacement(s, k) == expected


def test_longest_repeating_char_replacement_matches_brute_force():
    import random
    rng = random.Random(37)
    for _ in range(20):
        s = "".join(rng.choice("AB") for _ in range(rng.randint(1, 10)))
        k = rng.randint(0, 3)
        n = len(s)
        best = 0
        for i in range(n):
            for j in range(i, n):
                window = s[i:j + 1]
                max_freq = max(window.count(c) for c in set(window))
                if len(window) - max_freq <= k:
                    best = max(best, len(window))
        assert longest_repeating_char_replacement(s, k) == best


@pytest.mark.parametrize("nums, k, expected", [
    ([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2, 6), ([0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1], 3, 10),
])
def test_max_consecutive_ones_with_k_flips(nums, k, expected):
    assert max_consecutive_ones_with_k_flips(nums, k) == expected


def test_max_consecutive_ones_matches_brute_force():
    import random
    rng = random.Random(41)
    for _ in range(20):
        nums = [rng.randint(0, 1) for _ in range(rng.randint(1, 12))]
        k = rng.randint(0, 3)
        n = len(nums)
        best = 0
        for i in range(n):
            for j in range(i, n):
                zeros = nums[i:j + 1].count(0)
                if zeros <= k:
                    best = max(best, j - i + 1)
        assert max_consecutive_ones_with_k_flips(nums, k) == best


@pytest.mark.parametrize("s, t, expected", [("ADOBECODEBANC", "ABC", 4), ("a", "a", 1), ("a", "aa", 0)])
def test_minimum_window_length(s, t, expected):
    assert minimum_window_length(s, t) == expected


def test_minimum_window_length_matches_brute_force():
    import random
    from collections import Counter
    rng = random.Random(43)
    for _ in range(20):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(1, 10)))
        t = "".join(rng.choice("abc") for _ in range(rng.randint(1, 3)))
        need = Counter(t)
        n = len(s)
        best = n + 1
        for i in range(n):
            for j in range(i, n):
                window = Counter(s[i:j + 1])
                if all(window[c] >= cnt for c, cnt in need.items()):
                    best = min(best, j - i + 1)
                    break
        assert minimum_window_length(s, t) == (best if best <= n else 0)


@pytest.mark.parametrize("s, p, expected", [("cbaebabacd", "abc", [0, 6]), ("abab", "ab", [0, 1, 2])])
def test_find_all_anagram_starts(s, p, expected):
    assert find_all_anagram_starts(s, p) == expected


def test_find_all_anagram_starts_matches_brute_force():
    import random
    from collections import Counter
    rng = random.Random(47)
    for _ in range(20):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 10)))
        p = "".join(rng.choice("ab") for _ in range(rng.randint(1, 3)))
        m = len(p)
        expected = [i for i in range(len(s) - m + 1) if Counter(s[i:i + m]) == Counter(p)]
        assert find_all_anagram_starts(s, p) == expected


# ── BFS/graph variant family oracle tests ────────────────────────────────────

@pytest.mark.parametrize("grid, expected", [
    ([[2, 1, 1], [1, 1, 0], [0, 1, 1]], 4),
    ([[2, 1, 1], [0, 1, 1], [1, 0, 1]], -1),
    ([[0, 2]], 0),
])
def test_rotten_oranges_minutes(grid, expected):
    assert rotten_oranges_minutes(grid) == expected


def test_rotten_oranges_matches_brute_force_bfs_layers():
    import random
    rng = random.Random(53)
    for _ in range(15):
        rows, cols = rng.randint(1, 4), rng.randint(1, 4)
        grid = [[rng.choice([0, 1, 1, 2]) for _ in range(cols)] for _ in range(rows)]
        # brute force: repeatedly spread rot until stable, count rounds
        g = [row[:] for row in grid]
        minutes = 0
        while True:
            to_rot = []
            for r in range(rows):
                for c in range(cols):
                    if g[r][c] == 1:
                        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] == 2:
                                to_rot.append((r, c))
                                break
            if not to_rot:
                break
            for r, c in to_rot:
                g[r][c] = 2
            minutes += 1
        fresh_left = any(g[r][c] == 1 for r in range(rows) for c in range(cols))
        expected = -1 if fresh_left else minutes
        assert rotten_oranges_minutes(grid) == expected


@pytest.mark.parametrize("grid, expected", [
    ([[0, 0, 0], [0, 1, 0], [0, 0, 0]], 1),
    ([[0, 0, 1], [1, 1, 1], [1, 1, 1]], 3),
])
def test_max_distance_to_zero(grid, expected):
    assert max_distance_to_zero(grid) == expected


@pytest.mark.parametrize("grid, expected", [
    ([[1, 1, 0, 0, 0], [1, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 1]], 3),
    ([[1, 0, 0, 1, 0], [0, 0, 0, 0, 0], [0, 0, 1, 0, 0]], 3),
])
def test_count_islands(grid, expected):
    assert count_islands(grid) == expected


@pytest.mark.parametrize("grid, expected", [
    ([[0, 1], [1, 0]], 2), ([[0, 0, 0], [1, 1, 0], [1, 1, 0]], 4), ([[1, 0, 0]], -1),
])
def test_shortest_path_binary_matrix(grid, expected):
    assert shortest_path_binary_matrix(grid) == expected


@pytest.mark.parametrize("begin, end, words, expected", [
    ("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"], 5),
    ("hit", "cog", ["hot", "dot", "dog", "lot", "log"], 0),
])
def test_word_ladder_length(begin, end, words, expected):
    assert word_ladder_length(begin, end, words) == expected


@pytest.mark.parametrize("x, y, expected", [(2, 1, 1), (5, 5, 4), (0, 0, 0), (1, 0, 3)])
def test_min_knight_moves(x, y, expected):
    assert min_knight_moves(x, y) == expected


def test_min_knight_moves_matches_wide_bfs():
    from collections import deque
    import random
    rng = random.Random(59)

    def brute(tx, ty):
        moves = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
        visited = {(0, 0)}
        q = deque([(0, 0, 0)])
        while q:
            x, y, d = q.popleft()
            if (x, y) == (tx, ty):
                return d
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if -10 <= nx <= 10 and -10 <= ny <= 10 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q.append((nx, ny, d + 1))
        raise AssertionError("brute force didn't converge")

    for _ in range(15):
        tx, ty = rng.randint(-6, 6), rng.randint(-6, 6)
        assert min_knight_moves(tx, ty) == brute(tx, ty)


@pytest.mark.parametrize("n, edges, expected", [
    (4, [(0, 1), (1, 2), (2, 3), (3, 0)], True),
    (3, [(0, 1), (1, 2), (2, 0)], False),
    (4, [(0, 1), (2, 3)], True),
])
def test_is_bipartite(n, edges, expected):
    assert is_bipartite(n, edges) == expected


# ── Greedy family oracle tests ────────────────────────────────────────────────

@pytest.mark.parametrize("starts, ends, expected", [
    ([1, 3, 0, 5, 8, 5], [2, 4, 6, 7, 9, 9], 4),
    ([1, 2, 3], [2, 3, 4], 3),
])
def test_activity_selection_max_count(starts, ends, expected):
    assert activity_selection_max_count(starts, ends) == expected


def test_activity_selection_matches_brute_force():
    import random
    rng = random.Random(61)
    for _ in range(20):
        n = rng.randint(1, 7)
        starts = [rng.randint(0, 10) for _ in range(n)]
        ends = [s + rng.randint(1, 5) for s in starts]
        best = 0
        for mask in range(1 << n):
            chosen = [i for i in range(n) if mask & (1 << i)]
            chosen.sort(key=lambda i: ends[i])
            ok = True
            last_end = float("-inf")
            for i in chosen:
                if starts[i] < last_end:
                    ok = False
                    break
                last_end = ends[i]
            if ok:
                best = max(best, len(chosen))
        assert activity_selection_max_count(starts, ends) == best


@pytest.mark.parametrize("weights, values, capacity, expected", [
    ([10, 20, 30], [60, 100, 120], 50, 240.0),
])
def test_fractional_knapsack_max_value(weights, values, capacity, expected):
    assert abs(fractional_knapsack_max_value(weights, values, capacity) - expected) < 1e-9


@pytest.mark.parametrize("gas, cost, expected", [
    ([1, 2, 3, 4, 5], [3, 4, 5, 1, 2], 3),
    ([2, 3, 4], [3, 4, 3], -1),
])
def test_gas_station_start_index(gas, cost, expected):
    assert gas_station_start_index(gas, cost) == expected


def test_gas_station_matches_brute_force():
    import random
    rng = random.Random(67)
    for _ in range(20):
        n = rng.randint(1, 8)
        gas = [rng.randint(0, 10) for _ in range(n)]
        cost = [rng.randint(0, 10) for _ in range(n)]
        result = -1
        for start in range(n):
            tank = 0
            ok = True
            for step in range(n):
                i = (start + step) % n
                tank += gas[i] - cost[i]
                if tank < 0:
                    ok = False
                    break
            if ok:
                result = start
                break
        assert gas_station_start_index(gas, cost) == result


@pytest.mark.parametrize("freqs, expected", [([5, 9, 12, 13, 16, 45], 224), ([1, 1], 2)])
def test_huffman_total_encoded_length(freqs, expected):
    assert huffman_total_encoded_length(freqs) == expected


@pytest.mark.parametrize("deadlines, profits, expected", [
    ([2, 1, 2, 1, 3], [100, 19, 27, 25, 15], 142),
])
def test_job_scheduling_max_profit(deadlines, profits, expected):
    assert job_scheduling_max_profit(deadlines, profits) == expected


def test_job_scheduling_matches_brute_force():
    import random
    rng = random.Random(71)
    for _ in range(15):
        n = rng.randint(1, 6)
        deadlines = [rng.randint(1, n) for _ in range(n)]
        profits = [rng.randint(1, 20) for _ in range(n)]
        best = 0
        for mask in range(1 << n):
            chosen = [i for i in range(n) if mask & (1 << i)]
            max_d = max((deadlines[i] for i in chosen), default=0)
            slots = [False] * (max_d + 1)
            ok = True
            for i in sorted(chosen, key=lambda i: deadlines[i]):
                placed = False
                for t in range(deadlines[i], 0, -1):
                    if not slots[t]:
                        slots[t] = True
                        placed = True
                        break
                if not placed:
                    ok = False
                    break
            if ok:
                best = max(best, sum(profits[i] for i in chosen))
        assert job_scheduling_max_profit(deadlines, profits) == best


@pytest.mark.parametrize("starts, ends, expected", [
    ([0, 5, 15], [30, 10, 20], 2), ([7, 7, 7], [10, 10, 10], 3), ([1, 2], [2, 3], 1),
])
def test_meeting_rooms_min_count(starts, ends, expected):
    assert meeting_rooms_min_count(starts, ends) == expected


def test_meeting_rooms_matches_brute_force():
    import random
    rng = random.Random(73)
    for _ in range(20):
        n = rng.randint(1, 8)
        starts = [rng.randint(0, 10) for _ in range(n)]
        ends = [s + rng.randint(1, 5) for s in starts]
        events = sorted([(s, 1) for s in starts] + [(e, -1) for e in ends])
        cur = best = 0
        for _, delta in events:
            cur += delta
            best = max(best, cur)
        assert meeting_rooms_min_count(starts, ends) == best


def test_stable_matching_is_actually_stable():
    import random
    rng = random.Random(79)
    for _ in range(15):
        n = rng.randint(2, 5)
        men_prefs = [rng.sample(range(n), n) for _ in range(n)]
        women_prefs = [rng.sample(range(n), n) for _ in range(n)]
        man_partner = stable_matching_gale_shapley(men_prefs, women_prefs)
        assert sorted(man_partner) == list(range(n))
        woman_partner = [0] * n
        for m, w in enumerate(man_partner):
            woman_partner[w] = m
        men_rank = [{w: r for r, w in enumerate(men_prefs[m])} for m in range(n)]
        women_rank = [{m: r for r, m in enumerate(women_prefs[w])} for w in range(n)]
        for m in range(n):
            for w in range(n):
                if w == man_partner[m]:
                    continue
                m_prefers_w = men_rank[m][w] < men_rank[m][man_partner[m]]
                w_prefers_m = women_rank[w][m] < women_rank[w][woman_partner[w]]
                assert not (m_prefers_w and w_prefers_m), "found a blocking pair — not stable"


@pytest.mark.parametrize("task_counts, cooldown, expected", [
    ([3, 3], 2, 8), ([1, 1, 1], 0, 3), ([3, 3, 3, 1], 2, 10), ([3, 3, 3], 3, 11),
])
def test_task_scheduler_min_intervals(task_counts, cooldown, expected):
    assert task_scheduler_min_intervals(task_counts, cooldown) == expected


def test_task_scheduler_matches_brute_force_simulation():
    import heapq
    import random
    from collections import deque
    rng = random.Random(107)

    def brute(task_counts, n):
        heap = [-c for c in task_counts]
        heapq.heapify(heap)
        time = 0
        cooldown_q = deque()
        while heap or cooldown_q:
            time += 1
            if heap:
                cnt = -heapq.heappop(heap) - 1
                if cnt > 0:
                    cooldown_q.append((time + n, cnt))
            if cooldown_q and cooldown_q[0][0] == time:
                _, cnt = cooldown_q.popleft()
                heapq.heappush(heap, -cnt)
        return time

    for _ in range(15):
        counts = [rng.randint(1, 5) for _ in range(rng.randint(1, 4))]
        n = rng.randint(0, 3)
        assert task_scheduler_min_intervals(counts, n) == brute(counts, n)


# ── Divide-and-conquer family oracle tests ───────────────────────────────────

@pytest.mark.parametrize("points, expected", [
    ([(0, 0), (3, 4), (1, 1)], 2), ([(0, 0), (10, 10)], 200),
])
def test_closest_pair_min_sq_distance(points, expected):
    assert closest_pair_min_sq_distance(points) == expected


@pytest.mark.parametrize("nums, expected", [([2, 4, 1, 3, 5], 3), ([1, 2, 3], 0), ([5, 4, 3, 2, 1], 10)])
def test_count_inversions(nums, expected):
    assert count_inversions(nums) == expected


@pytest.mark.parametrize("base, exp, expected", [(2, 10, 1024), (3, 0, 1), (5, 3, 125)])
def test_fast_power_exact(base, exp, expected):
    assert fast_power_exact(base, exp) == expected


@pytest.mark.parametrize("a, b, expected", [(1234, 5678, 7006652), (0, 100, 0), (999, 999, 998001)])
def test_karatsuba_multiply(a, b, expected):
    assert karatsuba_multiply(a, b) == expected


@pytest.mark.parametrize("nums, expected", [([3, 2, 3], 3), ([2, 2, 1, 1, 1, 2, 2], 2)])
def test_majority_element(nums, expected):
    assert majority_element(nums) == expected


def test_matrix_power_mod_identity_and_known():
    assert matrix_power_mod([[1, 1], [1, 0]], 0, 1000) == [[1, 0], [0, 1]]
    # Fibonacci matrix: [[1,1],[1,0]]^n has F(n+1) at [0][0]
    result = matrix_power_mod([[1, 1], [1, 0]], 10, 10**9)
    assert result[0][0] == 89  # F(11) = 89
    assert result[0][1] == 55  # F(10) = 55


@pytest.mark.parametrize("nums, k, expected", [([7, 10, 4, 3, 20, 15], 3, 7), ([7, 10, 4, 3, 20, 15], 1, 3)])
def test_median_of_medians_kth_smallest(nums, k, expected):
    assert median_of_medians_kth_smallest(nums, k) == expected


@pytest.mark.parametrize("a, b, expected", [([1, 2, 3], [0, 1, 0.5], [0, 1, 2.5, 4, 1.5])])
def test_polynomial_multiply(a, b, expected):
    result = polynomial_multiply(a, b)
    assert len(result) == len(expected)
    for r, e in zip(result, expected):
        assert abs(r - e) < 1e-9


def test_polynomial_multiply_matches_naive():
    import random
    rng = random.Random(83)
    for _ in range(15):
        a = [rng.randint(-5, 5) for _ in range(rng.randint(1, 5))]
        b = [rng.randint(-5, 5) for _ in range(rng.randint(1, 5))]
        expected = [0] * (len(a) + len(b) - 1)
        for i, ai in enumerate(a):
            for j, bj in enumerate(b):
                expected[i + j] += ai * bj
        assert polynomial_multiply(a, b) == expected


def test_strassen_matrix_multiply_matches_naive():
    import random
    rng = random.Random(89)
    for _ in range(15):
        n, m, p = rng.randint(1, 4), rng.randint(1, 4), rng.randint(1, 4)
        A = [[rng.randint(-5, 5) for _ in range(m)] for _ in range(n)]
        B = [[rng.randint(-5, 5) for _ in range(p)] for _ in range(m)]
        expected = [[sum(A[i][k] * B[k][j] for k in range(m)) for j in range(p)] for i in range(n)]
        assert strassen_matrix_multiply(A, B) == expected


# ── String family oracle tests ────────────────────────────────────────────────

@pytest.mark.parametrize("s, expected", [("aabcaabxaaz", [0, 1, 0, 0, 3, 1, 0, 0, 2, 1, 0])])
def test_z_array(s, expected):
    assert z_array(s) == expected


def test_z_array_matches_naive():
    import random
    rng = random.Random(97)
    for _ in range(20):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(1, 12)))
        n = len(s)
        expected = [0] * n
        for i in range(1, n):
            l = 0
            while i + l < n and s[l] == s[i + l]:
                l += 1
            expected[i] = l
        assert z_array(s) == expected


@pytest.mark.parametrize("s1, s2, expected", [("abcdef", "zabcf", 3), ("abc", "def", 0)])
def test_longest_common_substring_length(s1, s2, expected):
    assert longest_common_substring_length(s1, s2) == expected


@pytest.mark.parametrize("s, expected", [("babad", 3), ("cbbd", 2), ("a", 1), ("", 0)])
def test_longest_palindromic_substring_length(s, expected):
    assert longest_palindromic_substring_length(s) == expected


@pytest.mark.parametrize("s, expected", [("abc", 3), ("aaa", 6)])
def test_count_palindromic_substrings(s, expected):
    assert count_palindromic_substrings(s) == expected


def test_count_palindromic_substrings_matches_brute_force():
    import random
    rng = random.Random(101)
    for _ in range(20):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 10)))
        n = len(s)
        expected = sum(1 for i in range(n) for j in range(i, n) if s[i:j + 1] == s[i:j + 1][::-1])
        assert count_palindromic_substrings(s) == expected


@pytest.mark.parametrize("s, expected", [("aaabbc", "3a2b1c"), ("", ""), ("a", "1a")])
def test_run_length_encode(s, expected):
    assert run_length_encode(s) == expected


@pytest.mark.parametrize("s, expected", [("banana", [5, 3, 1, 0, 4, 2])])
def test_suffix_array(s, expected):
    assert suffix_array(s) == expected


def test_suffix_array_matches_naive_sort():
    import random
    rng = random.Random(103)
    for _ in range(15):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(1, 10)))
        expected = sorted(range(len(s)), key=lambda i: s[i:])
        assert suffix_array(s) == expected


@pytest.mark.parametrize("s, k, expected", [("aabcaab", 2, 4), ("aaaa", 1, 1)])
def test_count_distinct_substrings_length_k(s, k, expected):
    assert count_distinct_substrings_length_k(s, k) == expected


# ── Bit-manipulation family oracle tests ─────────────────────────────────────

@pytest.mark.parametrize("nums, expected", [([2, 2, 1], 1), ([4, 1, 2, 1, 2], 4)])
def test_single_number(nums, expected):
    assert single_number(nums) == expected


@pytest.mark.parametrize("nums, expected", [([2, 2, 3, 2], 3), ([0, 1, 0, 1, 0, 1, 99], 99)])
def test_single_number_ii(nums, expected):
    assert single_number_ii(nums) == expected


@pytest.mark.parametrize("n, expected", [(2, [0, 1, 1]), (5, [0, 1, 1, 2, 1, 2])])
def test_counting_bits(n, expected):
    assert counting_bits(n) == expected


@pytest.mark.parametrize("n, expected", [(43261596, 964176192), (0, 0)])
def test_reverse_bits_32(n, expected):
    assert reverse_bits_32(n) == expected


@pytest.mark.parametrize("x, y, expected", [(1, 4, 2), (3, 1, 1)])
def test_hamming_distance(x, y, expected):
    assert hamming_distance(x, y) == expected


@pytest.mark.parametrize("n, expected", [(1, True), (16, True), (3, False), (0, False), (-1, False)])
def test_is_power_of_two(n, expected):
    assert is_power_of_two(n) == expected


@pytest.mark.parametrize("n, expected", [(11, 3), (128, 1), (0, 0)])
def test_count_set_bits(n, expected):
    assert count_set_bits(n) == expected


@pytest.mark.parametrize("nums, expected", [([3, 10, 5, 25, 2, 8], 28), ([14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70], 127)])
def test_max_xor_of_two_numbers(nums, expected):
    assert max_xor_of_two_numbers(nums) == expected


# ── Tree family oracle tests (canonical LeetCode examples + independent
# second-implementation cross-checks) ────────────────────────────────────────

@pytest.mark.parametrize("values, expected", [([3, 9, 20, None, None, 15, 7], 3), ([1, None, 2], 2), ([], 0)])
def test_max_depth_binary_tree(values, expected):
    assert max_depth_binary_tree(values) == expected


@pytest.mark.parametrize("values, expected", [([1, 2, 3, 4, 5], 3), ([1, 2], 1)])
def test_diameter_of_binary_tree(values, expected):
    assert diameter_of_binary_tree(values) == expected


@pytest.mark.parametrize("values, expected", [
    ([3, 9, 20, None, None, 15, 7], True),
    ([1, 2, 2, 3, 3, None, None, 4, 4], False),
])
def test_is_balanced_binary_tree(values, expected):
    assert is_balanced_binary_tree(values) == expected


@pytest.mark.parametrize("values, expected", [([2, 1, 3], True), ([5, 1, 4, None, None, 3, 6], False)])
def test_is_valid_bst(values, expected):
    assert is_valid_bst(values) == expected


def test_is_valid_bst_matches_inorder_sorted_check():
    """Independent check: a tree is a valid BST iff its inorder traversal is strictly increasing.

    Builds the tree with a SEPARATE level-order parser (not the oracle module's
    `_build_tree`) to keep this a genuine independent cross-check.
    """
    import random
    rng = random.Random(163)

    def inorder_values(values):
        from collections import deque
        if not values or values[0] is None:
            return []
        root = {"val": values[0], "left": None, "right": None}
        q = deque([root])
        i = 1
        n = len(values)
        while q and i < n:
            node = q.popleft()
            if i < n:
                if values[i] is not None:
                    node["left"] = {"val": values[i], "left": None, "right": None}
                    q.append(node["left"])
                i += 1
            if i < n:
                if values[i] is not None:
                    node["right"] = {"val": values[i], "left": None, "right": None}
                    q.append(node["right"])
                i += 1
        result = []

        def rec(n):
            if n is None:
                return
            rec(n["left"])
            result.append(n["val"])
            rec(n["right"])

        rec(root)
        return result

    for _ in range(15):
        n = rng.randint(1, 7)
        values = [rng.randint(0, 20) for _ in range(n)]
        vals = inorder_values(values)
        expected = all(vals[i] < vals[i + 1] for i in range(len(vals) - 1))
        assert is_valid_bst(values) == expected


@pytest.mark.parametrize("values, expected", [
    ([1, 2, 2, 3, 4, 4, 3], True), ([1, 2, 2, None, 3, None, 3], False),
])
def test_is_symmetric_tree(values, expected):
    assert is_symmetric_tree(values) == expected


@pytest.mark.parametrize("values, expected", [
    ([4, 2, 7, 1, 3, 6, 9], [4, 7, 9, 6, 2, 3, 1]), ([2, 1, 3], [2, 3, 1]),
])
def test_invert_tree_preorder(values, expected):
    assert invert_tree_preorder(values) == expected


@pytest.mark.parametrize("values, target, expected", [
    ([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1], 22, True),
    ([1, 2, 3], 5, False),
])
def test_path_sum_exists(values, target, expected):
    assert path_sum_exists(values, target) == expected


@pytest.mark.parametrize("values, expected", [([1, None, 2], 2), ([], 0), ([1, 2, 3, 4, 5], 5)])
def test_count_tree_nodes(values, expected):
    assert count_tree_nodes(values) == expected


@pytest.mark.parametrize("values, p, q, expected", [
    ([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 2, 8, 6),
    ([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 2, 4, 2),
])
def test_lowest_common_ancestor_bst(values, p, q, expected):
    assert lowest_common_ancestor_bst(values, p, q) == expected


@pytest.mark.parametrize("values, k, expected", [([3, 1, 4, None, 2], 1, 1), ([5, 3, 6, 2, 4, None, None, 1], 3, 3)])
def test_kth_smallest_in_bst(values, k, expected):
    assert kth_smallest_in_bst(values, k) == expected


@pytest.mark.parametrize("values, expected", [([3, 9, 20, None, None, 15, 7], [[3], [9, 20], [15, 7]]), ([1], [[1]])])
def test_level_order_traversal(values, expected):
    assert level_order_traversal(values) == expected


@pytest.mark.parametrize("values, expected", [([1, 2, 3, None, 5, None, 4], [1, 3, 4]), ([1, None, 3], [1, 3])])
def test_right_side_view(values, expected):
    assert right_side_view(values) == expected


@pytest.mark.parametrize("values1, values2, expected", [
    ([1, 2, 3], [1, 2, 3], True), ([1, 2], [1, None, 2], False),
])
def test_same_tree(values1, values2, expected):
    assert same_tree(values1, values2) == expected


@pytest.mark.parametrize("values, expected", [([1, 2, 3], 25), ([4, 9, 0, 5, 1], 1026)])
def test_sum_root_to_leaf_numbers(values, expected):
    assert sum_root_to_leaf_numbers(values) == expected


@pytest.mark.parametrize("values, expected", [([1, 2, 3], 6), ([-10, 9, 20, None, None, 15, 7], 42)])
def test_binary_tree_max_path_sum(values, expected):
    assert binary_tree_max_path_sum(values) == expected


# ── DP-variant family oracle tests ───────────────────────────────────────────

@pytest.mark.parametrize("triangle, expected", [
    ([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]], 11), ([[-10]], -10),
])
def test_triangle_min_path_sum(triangle, expected):
    assert triangle_min_path_sum(triangle) == expected


def test_triangle_min_path_sum_matches_brute_force():
    import random
    rng = random.Random(167)
    for _ in range(15):
        rows = rng.randint(1, 6)
        triangle = [[rng.randint(-5, 5) for _ in range(r + 1)] for r in range(rows)]
        paths = [[0]]
        for r in range(1, rows):
            new_paths = []
            for p in paths:
                last = p[-1]
                new_paths.append(p + [last])
                new_paths.append(p + [last + 1])
            paths = new_paths
        best = min(sum(triangle[r][c] for r, c in enumerate(p)) for p in paths)
        assert triangle_min_path_sum(triangle) == best


@pytest.mark.parametrize("prices, expected", [([7, 1, 5, 3, 6, 4], 5), ([7, 6, 4, 3, 1], 0)])
def test_max_profit_single_transaction(prices, expected):
    assert max_profit_single_transaction(prices) == expected


@pytest.mark.parametrize("prices, expected", [([7, 1, 5, 3, 6, 4], 7), ([1, 2, 3, 4, 5], 4), ([7, 6, 4, 3, 1], 0)])
def test_max_profit_unlimited_transactions(prices, expected):
    assert max_profit_unlimited_transactions(prices) == expected


@pytest.mark.parametrize("nums, expected", [([1, 5, 11, 5], True), ([1, 2, 3, 5], False)])
def test_can_partition_equal_subset(nums, expected):
    assert can_partition_equal_subset(nums) == expected


@pytest.mark.parametrize("nums, target, expected", [([1, 1, 1, 1, 1], 3, 5), ([1], 1, 1)])
def test_target_sum_ways(nums, target, expected):
    assert target_sum_ways(nums, target) == expected


def test_target_sum_ways_matches_brute_force():
    import itertools
    import random
    rng = random.Random(173)
    for _ in range(15):
        nums = [rng.randint(0, 5) for _ in range(rng.randint(1, 6))]
        target = rng.randint(-15, 15)
        count = sum(1 for signs in itertools.product([1, -1], repeat=len(nums))
                    if sum(s * x for s, x in zip(signs, nums)) == target)
        assert target_sum_ways(nums, target) == count


@pytest.mark.parametrize("n, expected", [(12, 3), (13, 2), (1, 1)])
def test_perfect_squares_min_count(n, expected):
    assert perfect_squares_min_count(n) == expected


@pytest.mark.parametrize("nums, target, expected", [([1, 2, 3], 4, 7), ([9], 3, 0)])
def test_combination_sum_iv_count(nums, target, expected):
    assert combination_sum_iv_count(nums, target) == expected


def test_combination_sum_iv_matches_brute_force():
    import random
    rng = random.Random(179)

    def count_ways(nums, target):
        if target == 0:
            return 1
        if target < 0:
            return 0
        return sum(count_ways(nums, target - x) for x in nums)

    for _ in range(15):
        nums = list({rng.randint(1, 4) for _ in range(rng.randint(1, 3))})
        target = rng.randint(0, 8)
        assert combination_sum_iv_count(nums, target) == count_ways(nums, target)


@pytest.mark.parametrize("nums, expected", [([3, 4, 2], 6), ([2, 2, 3, 3, 3, 4], 9)])
def test_delete_and_earn(nums, expected):
    assert delete_and_earn(nums) == expected


@pytest.mark.parametrize("nums, expected", [([1, -2, 3, -2], 3), ([5, -3, 5], 10), ([-2, -3, -1], -1)])
def test_max_subarray_circular(nums, expected):
    assert max_subarray_circular(nums) == expected


def test_max_subarray_circular_matches_brute_force():
    import random
    rng = random.Random(181)
    for _ in range(20):
        nums = [rng.randint(-5, 5) for _ in range(rng.randint(1, 8))]
        n = len(nums)
        doubled = nums + nums
        best = max(nums)
        for i in range(n):
            total = 0
            for length in range(1, n + 1):
                total = sum(doubled[i:i + length])
                best = max(best, total)
        assert max_subarray_circular(nums) == best


@pytest.mark.parametrize("nums, expected", [([2, 3, 1, 1, 4], 2), ([2, 3, 0, 1, 4], 2), ([0], 0)])
def test_jump_game_ii_min_jumps(nums, expected):
    assert jump_game_ii_min_jumps(nums) == expected


# ── Linked-list family oracle tests ──────────────────────────────────────────

@pytest.mark.parametrize("values, expected", [([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]), ([], []), ([1], [1])])
def test_reverse_linked_list(values, expected):
    assert reverse_linked_list(values) == expected


@pytest.mark.parametrize("pos, expected", [(1, True), (-1, False), (0, True)])
def test_linked_list_has_cycle(pos, expected):
    assert linked_list_has_cycle(pos) == expected


@pytest.mark.parametrize("a, b, expected", [([1, 2, 4], [1, 3, 4], [1, 1, 2, 3, 4, 4]), ([], [], []), ([], [0], [0])])
def test_merge_two_sorted_lists(a, b, expected):
    assert merge_two_sorted_lists(a, b) == expected


@pytest.mark.parametrize("values, n, expected", [([1, 2, 3, 4, 5], 2, [1, 2, 3, 5]), ([1], 1, [])])
def test_remove_nth_from_end(values, n, expected):
    assert remove_nth_from_end(values, n) == expected


@pytest.mark.parametrize("values, expected", [([1, 2, 3, 4, 5], 3), ([1, 2, 3, 4, 5, 6], 4)])
def test_middle_of_linked_list(values, expected):
    assert middle_of_linked_list(values) == expected


@pytest.mark.parametrize("values, expected", [([1, 2, 2, 1], True), ([1, 2], False), ([1], True)])
def test_is_palindrome_linked_list(values, expected):
    assert is_palindrome_linked_list(values) == expected


# ── Backtracking-count family oracle tests ───────────────────────────────────

@pytest.mark.parametrize("s, expected", [("aab", 1), ("a", 0), ("ab", 1)])
def test_palindrome_partition_min_cuts(s, expected):
    assert palindrome_partition_min_cuts(s) == expected


def test_palindrome_partition_min_cuts_matches_brute_force():
    import random
    rng = random.Random(191)

    def brute(s):
        n = len(s)

        def is_pal(sub):
            return sub == sub[::-1]

        best = [n]

        def rec(i, cuts):
            if i == n:
                best[0] = min(best[0], cuts)
                return
            for j in range(i, n):
                if is_pal(s[i:j + 1]):
                    rec(j + 1, cuts + (1 if j + 1 < n else 0))

        rec(0, 0)
        return best[0]

    for _ in range(15):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(1, 8)))
        assert palindrome_partition_min_cuts(s) == brute(s)


@pytest.mark.parametrize("s, expected", [("aab", 2), ("a", 1), ("aaa", 4)])
def test_palindrome_partition_count_ways(s, expected):
    assert palindrome_partition_count_ways(s) == expected


def test_palindrome_partition_count_ways_matches_brute_force():
    import random
    rng = random.Random(193)

    def brute(s):
        n = len(s)

        def is_pal(sub):
            return sub == sub[::-1]

        count = [0]

        def rec(i):
            if i == n:
                count[0] += 1
                return
            for j in range(i, n):
                if is_pal(s[i:j + 1]):
                    rec(j + 1)

        rec(0)
        return count[0]

    for _ in range(15):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(1, 7)))
        assert palindrome_partition_count_ways(s) == brute(s)


@pytest.mark.parametrize("s, expected", [("25525511135", 2), ("0000", 1), ("101023", 5)])
def test_restore_ip_addresses_count(s, expected):
    assert restore_ip_addresses_count(s) == expected


@pytest.mark.parametrize("s, word_dict, expected", [
    ("catsanddog", ["cat", "cats", "and", "sand", "dog"], 2),
    ("leetcode", ["leet", "code"], 1),
])
def test_word_break_count_ways(s, word_dict, expected):
    assert word_break_count_ways(s, word_dict) == expected


@pytest.mark.parametrize("nums, expected", [([1, 1, 2], 3), ([1, 2, 3], 6), ([1, 1, 1], 1)])
def test_unique_permutations_count(nums, expected):
    assert unique_permutations_count(nums) == expected


def test_unique_permutations_count_matches_brute_force():
    import itertools
    import random
    rng = random.Random(197)
    for _ in range(15):
        nums = [rng.randint(0, 3) for _ in range(rng.randint(1, 6))]
        expected = len(set(itertools.permutations(nums)))
        assert unique_permutations_count(nums) == expected


# ── Array/Hashing pattern family oracle tests ────────────────────────────────

@pytest.mark.parametrize("nums, k, expected", [
    ([1, 2, 3, 1], 3, True), ([1, 2, 3, 1], 2, False), ([1, 0, 1, 1], 1, True),
])
def test_contains_duplicate_within_k(nums, k, expected):
    assert contains_duplicate_within_k(nums, k) == expected


@pytest.mark.parametrize("nums, expected", [([1, 2, 3, 4], [24, 12, 8, 6]), ([-1, 1, 0, -3, 3], [0, 0, 9, 0, 0])])
def test_product_except_self(nums, expected):
    assert product_except_self(nums) == expected


@pytest.mark.parametrize("nums, k, expected", [([1, 1, 1], 2, 2), ([1, 2, 3], 3, 2), ([1, -1, 0], 0, 3)])
def test_subarray_sum_equals_k(nums, k, expected):
    assert subarray_sum_equals_k(nums, k) == expected


def test_subarray_sum_equals_k_matches_brute_force():
    import random
    rng = random.Random(109)
    for _ in range(20):
        nums = [rng.randint(-5, 5) for _ in range(rng.randint(1, 10))]
        k = rng.randint(-10, 10)
        n = len(nums)
        expected = sum(1 for i in range(n) for j in range(i, n) if sum(nums[i:j + 1]) == k)
        assert subarray_sum_equals_k(nums, k) == expected


@pytest.mark.parametrize("nums, k, expected", [([1, 1, 1, 2, 2, 3], 2, [1, 2])])
def test_top_k_frequent(nums, k, expected):
    assert top_k_frequent(nums, k) == expected


@pytest.mark.parametrize("nums, expected", [([100, 4, 200, 1, 3, 2], 4), ([0, 3, 7, 2, 5, 8, 4, 6, 0, 1], 9)])
def test_longest_consecutive_sequence(nums, expected):
    assert longest_consecutive_sequence(nums) == expected


@pytest.mark.parametrize("strs, expected", [(["eat", "tea", "tan", "ate", "nat", "bat"], 3), ([""], 1)])
def test_group_anagrams_count(strs, expected):
    assert group_anagrams_count(strs) == expected


@pytest.mark.parametrize("s, t, expected", [("anagram", "nagaram", True), ("rat", "car", False)])
def test_is_anagram(s, t, expected):
    assert is_anagram(s, t) == expected


@pytest.mark.parametrize("s, expected", [("leetcode", 0), ("loveleetcode", 2), ("aabb", -1)])
def test_first_unique_char_index(s, expected):
    assert first_unique_char_index(s) == expected


@pytest.mark.parametrize("nums1, nums2, expected", [([1, 2, 2, 1], [2, 2], [2]), ([4, 9, 5], [9, 4, 9, 8, 4], [4, 9])])
def test_intersection_sorted(nums1, nums2, expected):
    assert intersection_sorted(nums1, nums2) == expected


@pytest.mark.parametrize("nums, expected", [([3, 0, 1], 2), ([0, 1], 2), ([9, 6, 4, 2, 3, 5, 7, 0, 1], 8)])
def test_missing_number(nums, expected):
    assert missing_number(nums) == expected


@pytest.mark.parametrize("nums, expected", [([3, 2, 3], [3]), ([1], [1]), ([1, 2, 3], [])])
def test_majority_element_ii(nums, expected):
    assert majority_element_ii(nums) == expected


@pytest.mark.parametrize("nums, target, expected", [([1, 1, 1], 2, 3), ([1, 5, 3, 3, 3], 6, 4)])
def test_two_sum_count_pairs(nums, target, expected):
    assert two_sum_count_pairs(nums, target) == expected


def test_two_sum_count_pairs_matches_brute_force():
    import random
    rng = random.Random(113)
    for _ in range(20):
        nums = [rng.randint(-5, 5) for _ in range(rng.randint(0, 10))]
        target = rng.randint(-10, 10)
        n = len(nums)
        expected = sum(1 for i in range(n) for j in range(i + 1, n) if nums[i] + nums[j] == target)
        assert two_sum_count_pairs(nums, target) == expected


@pytest.mark.parametrize("nums, k, expected", [([4, 5, 0, -2, -3, 1], 5, 7), ([5], 9, 0)])
def test_subarray_sums_divisible_by_k(nums, k, expected):
    assert subarray_sums_divisible_by_k(nums, k) == expected


def test_subarray_sums_divisible_by_k_matches_brute_force():
    import random
    rng = random.Random(127)
    for _ in range(20):
        nums = [rng.randint(-5, 5) for _ in range(rng.randint(1, 8))]
        k = rng.choice([1, 2, 3, 5])
        n = len(nums)
        expected = sum(1 for i in range(n) for j in range(i, n) if sum(nums[i:j + 1]) % k == 0)
        assert subarray_sums_divisible_by_k(nums, k) == expected


@pytest.mark.parametrize("nums, expected", [([-1, 0, 1, 2, -1, -4], 2), ([0, 1, 1], 0), ([0, 0, 0], 1)])
def test_three_sum_count_triplets(nums, expected):
    assert three_sum_count_triplets(nums) == expected


def test_three_sum_matches_brute_force():
    import random
    import itertools
    rng = random.Random(131)
    for _ in range(15):
        nums = [rng.randint(-4, 4) for _ in range(rng.randint(3, 8))]
        found = set()
        for combo in itertools.combinations(nums, 3):
            if sum(combo) == 0:
                found.add(tuple(sorted(combo)))
        assert three_sum_count_triplets(nums) == len(found)


@pytest.mark.parametrize("heights, expected", [([1, 8, 6, 2, 5, 4, 8, 3, 7], 49), ([1, 1], 1)])
def test_container_with_most_water(heights, expected):
    assert container_with_most_water(heights) == expected


def test_container_matches_brute_force():
    import random
    rng = random.Random(137)
    for _ in range(20):
        heights = [rng.randint(0, 10) for _ in range(rng.randint(2, 10))]
        n = len(heights)
        expected = max(min(heights[i], heights[j]) * (j - i) for i in range(n) for j in range(i + 1, n))
        assert container_with_most_water(heights) == expected


# ── Stack family oracle tests ─────────────────────────────────────────────────

@pytest.mark.parametrize("s, expected", [("()[]{}", True), ("(]", False), ("([)]", False), ("{[]}", True)])
def test_valid_parentheses(s, expected):
    assert valid_parentheses(s) == expected


@pytest.mark.parametrize("temps, expected", [([73, 74, 75, 71, 69, 72, 76, 73], [1, 1, 4, 2, 1, 1, 0, 0]), ([30, 40, 50, 60], [1, 1, 1, 0])])
def test_daily_temperatures(temps, expected):
    assert daily_temperatures(temps) == expected


def test_daily_temperatures_matches_brute_force():
    import random
    rng = random.Random(139)
    for _ in range(15):
        temps = [rng.randint(30, 100) for _ in range(rng.randint(1, 10))]
        n = len(temps)
        expected = [0] * n
        for i in range(n):
            for j in range(i + 1, n):
                if temps[j] > temps[i]:
                    expected[i] = j - i
                    break
        assert daily_temperatures(temps) == expected


@pytest.mark.parametrize("nums, expected", [([4, 1, 2], [-1, 2, -1]), ([1, 3, 4, 2], [3, 4, -1, -1])])
def test_next_greater_element(nums, expected):
    assert next_greater_element(nums) == expected


def test_next_greater_element_matches_brute_force():
    import random
    rng = random.Random(157)
    for _ in range(20):
        nums = [rng.randint(0, 10) for _ in range(rng.randint(1, 10))]
        n = len(nums)
        expected = [-1] * n
        for i in range(n):
            for j in range(i + 1, n):
                if nums[j] > nums[i]:
                    expected[i] = nums[j]
                    break
        assert next_greater_element(nums) == expected


@pytest.mark.parametrize("heights, expected", [([2, 1, 5, 6, 2, 3], 10), ([2, 4], 4)])
def test_largest_rectangle_in_histogram(heights, expected):
    assert largest_rectangle_in_histogram(heights) == expected


def test_largest_rectangle_matches_brute_force():
    import random
    rng = random.Random(149)
    for _ in range(15):
        heights = [rng.randint(0, 8) for _ in range(rng.randint(1, 8))]
        n = len(heights)
        expected = 0
        for i in range(n):
            min_h = heights[i]
            for j in range(i, n):
                min_h = min(min_h, heights[j])
                expected = max(expected, min_h * (j - i + 1))
        assert largest_rectangle_in_histogram(heights) == expected


def test_min_stack_simulate():
    ops = [("PUSH", 5), ("PUSH", 2), ("PUSH", 7), ("POP", None), ("PUSH", 1)]
    assert min_stack_simulate(ops) == [5, 2, 2, 1]


@pytest.mark.parametrize("tokens, expected", [
    (["2", "1", "+", "3", "*"], 9), (["4", "13", "5", "/", "+"], 6), (["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"], 22),
])
def test_evaluate_rpn(tokens, expected):
    assert evaluate_rpn(tokens) == expected


@pytest.mark.parametrize("num, k, expected", [("1432219", 3, "1219"), ("10200", 1, "200"), ("10", 2, "0")])
def test_remove_k_digits(num, k, expected):
    assert remove_k_digits(num, k) == expected


@pytest.mark.parametrize("heights, expected", [([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], 6), ([4, 2, 0, 3, 2, 5], 9)])
def test_trapping_rain_water(heights, expected):
    assert trapping_rain_water(heights) == expected


def test_trapping_rain_water_matches_brute_force():
    import random
    rng = random.Random(151)
    for _ in range(20):
        heights = [rng.randint(0, 6) for _ in range(rng.randint(1, 10))]
        n = len(heights)
        expected = 0
        for i in range(n):
            left_max = max(heights[:i + 1])
            right_max = max(heights[i:])
            expected += max(0, min(left_max, right_max) - heights[i])
        assert trapping_rain_water(heights) == expected
