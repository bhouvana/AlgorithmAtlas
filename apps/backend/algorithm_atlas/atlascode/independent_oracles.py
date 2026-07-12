"""
Independent, plugin-free reference oracles for AtlasCode judging.

These functions are the SOLE source of truth for generated test-case expected
outputs. Unlike `oracle.py` (which reads answers off a visualization plugin's
terminal state), nothing here ever imports or executes a plugin. That
separation exists because plugin terminal state is optimized for animating an
algorithm, not for judging correctness, and has already produced two silent
bugs in this codebase:

  - sieve-of-eratosthenes clamped its internal `n` to max(20, min(limit, 50))
    before computing — a stdin value outside [20,50] silently computed the
    wrong range.
  - collatz's terminal step count was a decimated/truncated frame count
    (`_MAX_STEPS`), not the true mathematical step count (n=27 reported 39
    steps; the correct answer is 111).

Every function below is a short, independently reviewable reference
implementation with its own unit tests in
tests/atlascode/test_independent_oracles.py. If a function's output is not
unique for a given input (e.g. extended Euclidean's (x, y) pair, a primitive
root, a Goldbach pair), it must NOT be used to generate an exact-match test
case — flag that algorithm NEEDS_REVIEW/PROPERTY_JUDGE instead.
"""
from __future__ import annotations

import math


class OracleError(Exception):
    """Raised when an oracle is asked to evaluate an input outside its domain."""


def collatz_steps(n: int) -> int:
    """Number of steps for the Collatz sequence starting at n to reach 1."""
    if n < 1:
        raise OracleError(f"collatz undefined for n={n}")
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


def sieve_primes(n: int) -> list[int]:
    """All primes <= n, ascending. Empty list for n < 2."""
    if n < 0:
        raise OracleError(f"sieve undefined for n={n}")
    if n < 2:
        return []
    is_p = [True] * (n + 1)
    is_p[0] = is_p[1] = False
    p = 2
    while p * p <= n:
        if is_p[p]:
            for multiple in range(p * p, n + 1, p):
                is_p[multiple] = False
        p += 1
    return [i for i, ok in enumerate(is_p) if ok]


def catalan_number(n: int) -> int:
    """n-th Catalan number C(n) = C(2n, n) / (n + 1)."""
    if n < 0:
        raise OracleError(f"catalan undefined for n={n}")
    return math.comb(2 * n, n) // (n + 1)


def euler_phi(n: int) -> int:
    """Euler's totient function phi(n): count of integers in [1, n] coprime to n."""
    if n < 1:
        raise OracleError(f"euler_phi undefined for n={n}")
    result = n
    m = n
    p = 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            result -= result // p
        p += 1
    if m > 1:
        result -= result // m
    return result


def mod_pow(base: int, exp: int, mod: int) -> int:
    """base^exp mod m, handling exp==0 and mod==1 correctly."""
    if mod < 1:
        raise OracleError(f"mod_pow undefined for mod={mod}")
    if exp < 0:
        raise OracleError("mod_pow undefined for negative exponents")
    return pow(base, exp, mod)


def prime_factors(n: int) -> list[int]:
    """Prime factors of n with multiplicity, ascending (e.g. 12 -> [2, 2, 3])."""
    if n < 1:
        raise OracleError(f"prime_factors undefined for n={n}")
    if n == 1:
        return []
    factors = []
    m = n
    p = 2
    while p * p <= m:
        while m % p == 0:
            factors.append(p)
            m //= p
        p += 1 if p == 2 else 2
    if m > 1:
        factors.append(m)
    return factors


def count_divisors(n: int) -> int:
    """Number of positive divisors of n (e.g. d(12) = 6: 1,2,3,4,6,12)."""
    if n < 1:
        raise OracleError(f"count_divisors undefined for n={n}")
    count = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            count += 1 if i * i == n else 2
        i += 1
    return count


def is_prime(n: int) -> bool:
    """Deterministic primality test (trial division) — used as ground truth
    for miller-rabin's true/false output, independent of any probabilistic
    witness set the plugin's visualization might use."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def lucas_binomial_mod(n: int, k: int, p: int) -> int:
    """C(n, k) mod p via Lucas' theorem (p must be prime)."""
    if p < 2:
        raise OracleError(f"lucas_binomial_mod undefined for p={p}")
    if k < 0 or k > n:
        return 0
    if n == 0:
        return 1
    return (math.comb(n % p, k % p) % p) * lucas_binomial_mod(n // p, k // p, p) % p


# ── Dynamic programming (added for the DP batch — see docs/atlascode-progress.md) ──
# Every answer below is a unique scalar/boolean (no multi-valid-answer structures
# like "a valid alignment" or "a set of partitions"), so each is safe for an
# exact-match STANDARD_JUDGE. Textbook recurrences only; each has a brute-force
# cross-check in tests/unit/test_independent_oracles.py.

def climbing_stairs(n: int) -> int:
    """Ways to climb n stairs taking 1 or 2 steps at a time. f(0)=f(1)=1."""
    if n < 0:
        raise OracleError(f"climbing_stairs undefined for n={n}")
    if n <= 1:
        return 1
    prev2, prev1 = 1, 1
    for _ in range(2, n + 1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1


def can_jump(nums: list[int]) -> bool:
    """True if index 0 can reach the last index, where nums[i] is the max jump from i."""
    if not nums:
        raise OracleError("can_jump undefined for empty array")
    reach = 0
    for i, step in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + step)
    return reach >= len(nums) - 1


def subset_sum_exists(nums: list[int], target: int) -> bool:
    """True if some subset of nums (non-negative ints) sums exactly to target."""
    if target < 0:
        raise OracleError(f"subset_sum_exists undefined for target={target}")
    reachable = {0}
    for x in nums:
        if x < 0:
            raise OracleError("subset_sum_exists requires non-negative values")
        reachable |= {s + x for s in reachable if s + x <= target}
    return target in reachable


def coin_change_ways(coins: list[int], amount: int) -> int:
    """Number of combinations (order-independent, unbounded supply) of coins summing to amount."""
    if amount < 0:
        raise OracleError(f"coin_change_ways undefined for amount={amount}")
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        if c <= 0:
            raise OracleError("coin_change_ways requires positive denominations")
        for a in range(c, amount + 1):
            dp[a] += dp[a - c]
    return dp[amount]


def decode_ways(s: str) -> int:
    """Number of ways to decode a digit string into letters A(1)..Z(26). '0' alone is invalid."""
    if not s:
        raise OracleError("decode_ways undefined for empty string")
    n = len(s)
    dp = [0] * (n + 1)
    dp[0] = 1
    dp[1] = 1 if s[0] != "0" else 0
    for i in range(2, n + 1):
        if s[i - 1] != "0":
            dp[i] += dp[i - 1]
        two = int(s[i - 2:i])
        if 10 <= two <= 26:
            dp[i] += dp[i - 2]
    return dp[n]


def knapsack_01(weights: list[int], values: list[int], capacity: int) -> int:
    """Max total value picking each item at most once within capacity."""
    if len(weights) != len(values) or capacity < 0:
        raise OracleError("knapsack_01: mismatched lengths or negative capacity")
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        if w < 0 or v < 0:
            raise OracleError("knapsack_01 requires non-negative weights/values")
        for c in range(capacity, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[capacity]


def unbounded_knapsack(weights: list[int], values: list[int], capacity: int) -> int:
    """Max total value picking items with unlimited supply within capacity."""
    if len(weights) != len(values) or capacity < 0:
        raise OracleError("unbounded_knapsack: mismatched lengths or negative capacity")
    dp = [0] * (capacity + 1)
    for c in range(1, capacity + 1):
        for w, v in zip(weights, values):
            if 0 < w <= c:
                dp[c] = max(dp[c], dp[c - w] + v)
    return dp[capacity]


def rod_cutting(prices: list[int], length: int) -> int:
    """Max revenue cutting a rod of `length` into integer pieces; prices[i-1] = price of length i."""
    if length < 0 or len(prices) < length:
        raise OracleError("rod_cutting: length out of range for given prices")
    dp = [0] * (length + 1)
    for l in range(1, length + 1):
        dp[l] = max(prices[i - 1] + dp[l - i] for i in range(1, l + 1))
    return dp[length]


def max_product_subarray(nums: list[int]) -> int:
    """Max product of a contiguous, non-empty subarray (handles negatives via running min/max)."""
    if not nums:
        raise OracleError("max_product_subarray undefined for empty array")
    max_p = min_p = result = nums[0]
    for x in nums[1:]:
        candidates = (x, max_p * x, min_p * x)
        max_p, min_p = max(candidates), min(candidates)
        result = max(result, max_p)
    return result


def longest_bitonic_subsequence(nums: list[int]) -> int:
    """Length of the longest subsequence that strictly increases then strictly decreases."""
    n = len(nums)
    if n == 0:
        raise OracleError("longest_bitonic_subsequence undefined for empty array")
    inc = [1] * n
    dec = [1] * n
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                inc[i] = max(inc[i], inc[j] + 1)
    for i in range(n - 1, -1, -1):
        for j in range(n - 1, i, -1):
            if nums[j] < nums[i]:
                dec[i] = max(dec[i], dec[j] + 1)
    return max(inc[i] + dec[i] - 1 for i in range(n))


def longest_palindromic_subsequence(s: str) -> int:
    """Length of the longest subsequence of s that reads the same forwards and backwards."""
    if not s:
        raise OracleError("longest_palindromic_subsequence undefined for empty string")
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                dp[i][j] = (dp[i + 1][j - 1] + 2) if j > i + 1 else 2
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return dp[0][n - 1]


def is_interleave(s1: str, s2: str, s3: str) -> bool:
    """True if s3 is an interleaving of s1 and s2 (preserving relative order of each)."""
    n, m = len(s1), len(s2)
    if n + m != len(s3):
        return False
    dp = [[False] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = True
    for i in range(n + 1):
        for j in range(m + 1):
            if i > 0 and s1[i - 1] == s3[i + j - 1] and dp[i - 1][j]:
                dp[i][j] = True
            if j > 0 and s2[j - 1] == s3[i + j - 1] and dp[i][j - 1]:
                dp[i][j] = True
    return dp[n][m]


def wildcard_match(s: str, p: str) -> bool:
    """True if pattern p ('?' = any single char, '*' = any sequence incl. empty) matches s fully."""
    n, m = len(s), len(p)
    dp = [[False] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = True
    for j in range(1, m + 1):
        if p[j - 1] == "*":
            dp[0][j] = dp[0][j - 1]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if p[j - 1] == "*":
                dp[i][j] = dp[i - 1][j] or dp[i][j - 1]
            elif p[j - 1] == "?" or p[j - 1] == s[i - 1]:
                dp[i][j] = dp[i - 1][j - 1]
    return dp[n][m]


def num_distinct_subsequences(s: str, t: str) -> int:
    """Number of distinct subsequences of s equal to t."""
    n, m = len(s), len(t)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = 1
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dp[i][j] = dp[i - 1][j]
            if s[i - 1] == t[j - 1]:
                dp[i][j] += dp[i - 1][j - 1]
    return dp[n][m]


def matrix_chain_order(dims: list[int]) -> int:
    """Minimum scalar multiplications to fully parenthesize a chain of matrices.

    dims has length n+1 for n matrices, where matrix i has shape dims[i] x dims[i+1].
    """
    n = len(dims) - 1
    if n < 1:
        raise OracleError("matrix_chain_order requires at least 1 matrix")
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = min(
                dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                for k in range(i, j)
            )
    return dp[0][n - 1]


def egg_drop_min_trials(eggs: int, floors: int) -> int:
    """Min trials to determine the critical floor in the worst case with `eggs` eggs.

    Uses the standard f(t, e) = f(t-1, e-1) + f(t-1, e) + 1 formulation
    (max floors distinguishable with t trials and e eggs), increasing t until
    f(t, eggs) >= floors — O(eggs * answer) instead of the naive O(eggs * floors^2).
    """
    if eggs < 1 or floors < 0:
        raise OracleError(f"egg_drop_min_trials undefined for eggs={eggs}, floors={floors}")
    if floors == 0:
        return 0
    f = [0] * (eggs + 1)
    trials = 0
    while f[eggs] < floors:
        trials += 1
        new_f = [0] * (eggs + 1)
        for e in range(1, eggs + 1):
            new_f[e] = f[e - 1] + f[e] + 1
        f = new_f
    return trials


def boolean_parenthesization_true_ways(symbols: str, ops: str) -> int:
    """Ways to parenthesize a boolean expression (symbols 'T'/'F' joined by ops '&','|','^')
    so that it evaluates to True."""
    n = len(symbols)
    if n == 0 or len(ops) != n - 1 or any(c not in "TF" for c in symbols) or any(c not in "&|^" for c in ops):
        raise OracleError("boolean_parenthesization_true_ways: malformed expression")
    true_count = [[0] * n for _ in range(n)]
    false_count = [[0] * n for _ in range(n)]
    for i in range(n):
        true_count[i][i] = 1 if symbols[i] == "T" else 0
        false_count[i][i] = 1 if symbols[i] == "F" else 0
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            t = f = 0
            for k in range(i, j):
                op = ops[k]
                lt, lf = true_count[i][k], false_count[i][k]
                rt, rf = true_count[k + 1][j], false_count[k + 1][j]
                total = (lt + lf) * (rt + rf)
                if op == "&":
                    tt = lt * rt
                elif op == "|":
                    tt = total - lf * rf
                else:  # '^'
                    tt = lt * rf + lf * rt
                t += tt
                f += total - tt
            true_count[i][j] = t
            false_count[i][j] = f
    return true_count[0][n - 1]


def word_wrap_min_cost(word_lengths: list[int], line_width: int) -> int:
    """Min total badness wrapping words into lines of at most `line_width` chars.

    Badness of a non-last line with `extra` unused chars is extra**3; the last
    line always costs 0 (classic "word wrap" / print-neatly formulation).
    """
    n = len(word_lengths)
    if n == 0:
        raise OracleError("word_wrap_min_cost undefined for empty word list")
    if any(w > line_width for w in word_lengths):
        raise OracleError("word_wrap_min_cost: a word is longer than line_width")
    INF = float("inf")
    extra = [[INF] * n for _ in range(n)]
    for i in range(n):
        cur = word_lengths[i]
        extra[i][i] = line_width - cur
        for j in range(i + 1, n):
            cur += 1 + word_lengths[j]
            if cur > line_width:
                break
            extra[i][j] = line_width - cur
    dp = [INF] * (n + 1)
    dp[n] = 0
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            if extra[i][j] == INF:
                break
            line_cost = 0 if j == n - 1 else extra[i][j] ** 3
            if dp[j + 1] != INF:
                dp[i] = min(dp[i], line_cost + dp[j + 1])
    return int(dp[0])


# ── Binary-search variant family — see docs/atlascode-progress.md ──
# Every contract below is chosen SPECIFICALLY to have a unique answer (a
# plain "find a peak" is NOT included because arbitrary arrays can have
# multiple valid peaks — that needs a property validator, not built yet;
# "find the peak of a strictly bitonic array" is used instead, which is
# unique and still exercises the same binary-search-on-shape technique).

def rotated_search(nums: list[int], target: int) -> int:
    """Index of target in a rotated ascending array of distinct ints, else -1."""
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


def bitonic_peak_index(nums: list[int]) -> int:
    """Index of the peak in an array that strictly increases then strictly decreases."""
    if len(nums) < 3:
        raise OracleError("bitonic_peak_index requires a genuine increase-then-decrease shape")
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return lo


def first_occurrence(nums: list[int], target: int) -> int:
    """Leftmost index of target in a sorted (non-decreasing) array, else -1."""
    lo, hi, ans = 0, len(nums) - 1, -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            ans = mid
            hi = mid - 1
        elif nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return ans


def last_occurrence(nums: list[int], target: int) -> int:
    """Rightmost index of target in a sorted (non-decreasing) array, else -1."""
    lo, hi, ans = 0, len(nums) - 1, -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            ans = mid
            lo = mid + 1
        elif nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return ans


def count_occurrences(nums: list[int], target: int) -> int:
    """Number of occurrences of target in a sorted array."""
    first = first_occurrence(nums, target)
    if first == -1:
        return 0
    return last_occurrence(nums, target) - first + 1


def search_insert_position(nums: list[int], target: int) -> int:
    """Index where target would be inserted to keep nums sorted (bisect_left)."""
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def min_eating_speed(piles: list[int], h: int) -> int:
    """Minimum integer eating speed k so all piles finish within h hours (Koko)."""
    if h < len(piles):
        raise OracleError("min_eating_speed: fewer hours than piles makes it infeasible")

    def hours_needed(k: int) -> int:
        return sum((p + k - 1) // k for p in piles)

    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if hours_needed(mid) <= h:
            hi = mid
        else:
            lo = mid + 1
    return lo


def ship_within_days(weights: list[int], days: int) -> int:
    """Minimum ship capacity so all weights (in order) ship within `days` days."""
    if days < 1:
        raise OracleError("ship_within_days: days must be positive")

    def days_needed(capacity: int) -> int:
        d, load = 1, 0
        for w in weights:
            if load + w > capacity:
                d += 1
                load = 0
            load += w
        return d

    lo, hi = max(weights), sum(weights)
    while lo < hi:
        mid = (lo + hi) // 2
        if days_needed(mid) <= days:
            hi = mid
        else:
            lo = mid + 1
    return lo


def integer_sqrt(n: int) -> int:
    """Floor of the square root of n via binary search."""
    if n < 0:
        raise OracleError("integer_sqrt undefined for negative n")
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid * mid <= n:
            lo = mid
        else:
            hi = mid - 1
    return lo


def search_2d_matrix(matrix: list[list[int]], target: int) -> bool:
    """True if target exists in a matrix where each row is ascending and each
    row's first element exceeds the previous row's last element (LeetCode-74 shape)."""
    if not matrix or not matrix[0]:
        return False
    rows, cols = len(matrix), len(matrix[0])
    lo, hi = 0, rows * cols - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        val = matrix[mid // cols][mid % cols]
        if val == target:
            return True
        if val < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False


def find_min_rotated(nums: list[int]) -> int:
    """Minimum element of a rotated ascending array of distinct ints."""
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]


# ── Sliding-window variant family — see docs/atlascode-progress.md ──
# These are PATTERN_PROBLEM origin (no single canonical algorithm backs
# "sliding window" in the registry); every answer is a unique scalar/list.

def max_sum_subarray_fixed_k(nums: list[int], k: int) -> int:
    """Maximum sum of any contiguous subarray of exactly length k."""
    if k <= 0 or k > len(nums):
        raise OracleError(f"max_sum_subarray_fixed_k: invalid k={k} for length {len(nums)}")
    window = sum(nums[:k])
    best = window
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]
        best = max(best, window)
    return best


def min_subarray_len_at_least_target(nums: list[int], target: int) -> int:
    """Length of the shortest contiguous subarray with sum >= target (0 if none)."""
    if target <= 0:
        raise OracleError("min_subarray_len_at_least_target requires a positive target")
    n = len(nums)
    left = 0
    total = 0
    best = n + 1
    for right in range(n):
        total += nums[right]
        while total >= target:
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return best if best <= n else 0


def longest_substring_without_repeat(s: str) -> int:
    """Length of the longest substring of s with no repeated characters."""
    last_seen: dict[str, int] = {}
    left = 0
    best = 0
    for right, c in enumerate(s):
        if c in last_seen and last_seen[c] >= left:
            left = last_seen[c] + 1
        last_seen[c] = right
        best = max(best, right - left + 1)
    return best


def longest_substring_at_most_k_distinct(s: str, k: int) -> int:
    """Length of the longest substring of s containing at most k distinct characters."""
    if k < 0:
        raise OracleError("longest_substring_at_most_k_distinct: k must be non-negative")
    if k == 0:
        return 0
    counts: dict[str, int] = {}
    left = 0
    best = 0
    distinct = 0
    for right, c in enumerate(s):
        if counts.get(c, 0) == 0:
            distinct += 1
        counts[c] = counts.get(c, 0) + 1
        while distinct > k:
            counts[s[left]] -= 1
            if counts[s[left]] == 0:
                distinct -= 1
            left += 1
        best = max(best, right - left + 1)
    return best


def longest_repeating_char_replacement(s: str, k: int) -> int:
    """Length of the longest substring that can become all-one-character with
    at most k character replacements."""
    if k < 0:
        raise OracleError("longest_repeating_char_replacement: k must be non-negative")
    counts: dict[str, int] = {}
    left = 0
    best = 0
    max_count = 0
    for right, c in enumerate(s):
        counts[c] = counts.get(c, 0) + 1
        max_count = max(max_count, counts[c])
        while (right - left + 1) - max_count > k:
            counts[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best


def max_consecutive_ones_with_k_flips(nums: list[int], k: int) -> int:
    """Max length of a contiguous run of 1s in a binary array after flipping at most k zeros."""
    if k < 0:
        raise OracleError("max_consecutive_ones_with_k_flips: k must be non-negative")
    left = 0
    zeros = 0
    best = 0
    for right, x in enumerate(nums):
        if x == 0:
            zeros += 1
        while zeros > k:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        best = max(best, right - left + 1)
    return best


def minimum_window_length(s: str, t: str) -> int:
    """Length of the smallest substring of s containing every character of t
    (with multiplicity); 0 if no such window exists."""
    if not t:
        raise OracleError("minimum_window_length requires a non-empty t")
    need: dict[str, int] = {}
    for c in t:
        need[c] = need.get(c, 0) + 1
    missing = len(t)
    left = 0
    best = len(s) + 1
    for right in range(1, len(s) + 1):
        c = s[right - 1]
        if need.get(c, 0) > 0:
            missing -= 1
        need[c] = need.get(c, 0) - 1
        while missing == 0:
            best = min(best, right - left)
            left_c = s[left]
            need[left_c] = need.get(left_c, 0) + 1
            if need[left_c] > 0:
                missing += 1
            left += 1
    return best if best <= len(s) else 0


def rotten_oranges_minutes(grid: list[list[int]]) -> int:
    """Minutes for rot (2) to spread 4-directionally to all fresh (1) cells; -1 if impossible."""
    from collections import deque
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    g = [row[:] for row in grid]
    q: deque = deque()
    fresh = 0
    for r in range(rows):
        for c in range(cols):
            if g[r][c] == 2:
                q.append((r, c, 0))
            elif g[r][c] == 1:
                fresh += 1
    minutes = 0
    while q:
        r, c, t = q.popleft()
        minutes = max(minutes, t)
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] == 1:
                g[nr][nc] = 2
                fresh -= 1
                q.append((nr, nc, t + 1))
    return minutes if fresh == 0 else -1


def max_distance_to_zero(grid: list[list[int]]) -> int:
    """Max, over all cells, of the 4-directional distance to the nearest 0 cell."""
    from collections import deque
    rows, cols = len(grid), len(grid[0])
    dist = [[-1] * cols for _ in range(rows)]
    q: deque = deque()
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                dist[r][c] = 0
                q.append((r, c))
    if not q:
        raise OracleError("max_distance_to_zero requires at least one 0 cell")
    best = 0
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                best = max(best, dist[nr][nc])
                q.append((nr, nc))
    return best


def count_islands(grid: list[list[int]]) -> int:
    """Number of 4-directionally-connected components of 1s in a 0/1 grid."""
    from collections import deque
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    visited = [[False] * cols for _ in range(rows)]
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and not visited[r][c]:
                count += 1
                visited[r][c] = True
                q = deque([(r, c)])
                while q:
                    cr, cc = q.popleft()
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1 and not visited[nr][nc]:
                            visited[nr][nc] = True
                            q.append((nr, nc))
    return count


def shortest_path_binary_matrix(grid: list[list[int]]) -> int:
    """8-directional shortest path length (in cells) from top-left to bottom-right
    of an n x n grid of 0 (open) / 1 (blocked); -1 if no path."""
    from collections import deque
    n = len(grid)
    if n == 0 or grid[0][0] != 0 or grid[n - 1][n - 1] != 0:
        return -1
    dist = [[-1] * n for _ in range(n)]
    dist[0][0] = 1
    q = deque([(0, 0)])
    while q:
        r, c = q.popleft()
        if r == n - 1 and c == n - 1:
            return dist[r][c]
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0 and dist[nr][nc] == -1:
                    dist[nr][nc] = dist[r][c] + 1
                    q.append((nr, nc))
    return -1


def word_ladder_length(begin_word: str, end_word: str, word_list: list[str]) -> int:
    """Number of words in the shortest transformation sequence from begin_word to
    end_word (inclusive), changing one letter at a time via words in word_list; 0 if impossible."""
    from collections import deque
    import string
    words = set(word_list)
    if end_word not in words:
        return 0
    q = deque([(begin_word, 1)])
    visited = {begin_word}
    while q:
        word, steps = q.popleft()
        if word == end_word:
            return steps
        for i in range(len(word)):
            for ch in string.ascii_lowercase:
                if ch == word[i]:
                    continue
                nxt = word[:i] + ch + word[i + 1:]
                if nxt in words and nxt not in visited:
                    visited.add(nxt)
                    q.append((nxt, steps + 1))
    return 0


def min_knight_moves(x: int, y: int) -> int:
    """Minimum knight moves from (0,0) to (x,y) on an infinite chessboard."""
    from collections import deque
    x, y = abs(x), abs(y)
    moves = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
    visited = {(0, 0)}
    q = deque([(0, 0, 0)])
    while q:
        cx, cy, d = q.popleft()
        if (cx, cy) == (x, y):
            return d
        for dx, dy in moves:
            nx, ny = cx + dx, cy + dy
            if -2 <= nx <= x + 2 and -2 <= ny <= y + 2 and (nx, ny) not in visited:
                visited.add((nx, ny))
                q.append((nx, ny, d + 1))
    raise OracleError(f"min_knight_moves: no path found to ({x},{y}) — unexpected")


def is_bipartite(n: int, edges: list[tuple[int, int]]) -> bool:
    """True if the undirected graph on n nodes (0-indexed) can be 2-colored
    (handles disconnected components)."""
    from collections import deque
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    color = [-1] * n
    for start in range(n):
        if color[start] != -1:
            continue
        color[start] = 0
        q = deque([start])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if color[v] == -1:
                    color[v] = 1 - color[u]
                    q.append(v)
                elif color[v] == color[u]:
                    return False
    return True


# ── Greedy family — see docs/atlascode-progress.md ──

def activity_selection_max_count(starts: list[int], ends: list[int]) -> int:
    """Max number of non-overlapping activities (classic interval scheduling)."""
    if len(starts) != len(ends):
        raise OracleError("activity_selection_max_count: mismatched lengths")
    activities = sorted(zip(ends, starts))
    count = 0
    last_end = float("-inf")
    for end, start in activities:
        if start >= last_end:
            count += 1
            last_end = end
    return count


def fractional_knapsack_max_value(weights: list[int], values: list[int], capacity: int) -> float:
    """Max value achievable taking fractional amounts of items, greedy by value/weight ratio."""
    if len(weights) != len(values) or capacity < 0:
        raise OracleError("fractional_knapsack_max_value: mismatched lengths or negative capacity")
    items = sorted(zip(weights, values), key=lambda wv: wv[1] / wv[0], reverse=True)
    remaining = capacity
    total = 0.0
    for w, v in items:
        if remaining <= 0:
            break
        take = min(w, remaining)
        total += v * (take / w)
        remaining -= take
    return total


def gas_station_start_index(gas: list[int], cost: list[int]) -> int:
    """Unique starting station index to complete the circuit, or -1 if impossible."""
    if len(gas) != len(cost):
        raise OracleError("gas_station_start_index: mismatched lengths")
    n = len(gas)
    if sum(gas) - sum(cost) < 0:
        return -1
    tank = 0
    start = 0
    for i in range(n):
        tank += gas[i] - cost[i]
        if tank < 0:
            start = i + 1
            tank = 0
    return start


def huffman_total_encoded_length(freqs: list[int]) -> int:
    """Total weighted path length (sum of freq*code_length) of an optimal Huffman tree.

    Invariant regardless of tie-breaking during construction: this equals the
    sum of all internal-node merge costs.
    """
    import heapq
    if len(freqs) < 2:
        raise OracleError("huffman_total_encoded_length requires at least 2 symbols")
    heap = list(freqs)
    heapq.heapify(heap)
    total = 0
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        merged = a + b
        total += merged
        heapq.heappush(heap, merged)
    return total


def job_scheduling_max_profit(deadlines: list[int], profits: list[int]) -> int:
    """Max profit scheduling unit-time jobs, each must finish by its deadline (1-indexed slot)."""
    if len(deadlines) != len(profits):
        raise OracleError("job_scheduling_max_profit: mismatched lengths")
    jobs = sorted(zip(profits, deadlines), reverse=True)
    max_deadline = max(deadlines) if deadlines else 0
    slots = [False] * (max_deadline + 1)
    total = 0
    for profit, deadline in jobs:
        for t in range(min(deadline, max_deadline), 0, -1):
            if not slots[t]:
                slots[t] = True
                total += profit
                break
    return total


def meeting_rooms_min_count(starts: list[int], ends: list[int]) -> int:
    """Minimum number of meeting rooms needed to hold all given meetings."""
    import heapq
    if len(starts) != len(ends):
        raise OracleError("meeting_rooms_min_count: mismatched lengths")
    meetings = sorted(zip(starts, ends))
    heap: list[int] = []
    for s, e in meetings:
        if heap and heap[0] <= s:
            heapq.heapreplace(heap, e)
        else:
            heapq.heappush(heap, e)
    return len(heap)


def stable_matching_gale_shapley(men_prefs: list[list[int]], women_prefs: list[list[int]]) -> list[int]:
    """Man-optimal stable matching (Gale-Shapley, men propose). Returns partner[m] = woman index."""
    n = len(men_prefs)
    if len(women_prefs) != n:
        raise OracleError("stable_matching_gale_shapley: mismatched preference list sizes")
    women_rank = [[0] * n for _ in range(n)]
    for w in range(n):
        for rank, m in enumerate(women_prefs[w]):
            women_rank[w][m] = rank
    next_proposal = [0] * n
    woman_partner = [-1] * n
    free_men = list(range(n))
    while free_men:
        m = free_men.pop(0)
        w = men_prefs[m][next_proposal[m]]
        next_proposal[m] += 1
        if woman_partner[w] == -1:
            woman_partner[w] = m
        elif women_rank[w][m] < women_rank[w][woman_partner[w]]:
            free_men.append(woman_partner[w])
            woman_partner[w] = m
        else:
            free_men.append(m)
    man_partner = [-1] * n
    for w, m in enumerate(woman_partner):
        man_partner[m] = w
    return man_partner


def task_scheduler_min_intervals(task_counts: list[int], cooldown: int) -> int:
    """Min total intervals (incl. idles) to run all tasks with a cooldown between same-type tasks."""
    if cooldown < 0 or not task_counts:
        raise OracleError("task_scheduler_min_intervals: invalid input")
    max_count = max(task_counts)
    num_max = task_counts.count(max_count)
    total_tasks = sum(task_counts)
    formula = (max_count - 1) * (cooldown + 1) + num_max
    return max(total_tasks, formula)


# ── Divide-and-conquer family — see docs/atlascode-progress.md ──

def closest_pair_min_sq_distance(points: list[tuple[int, int]]) -> int:
    """Minimum squared Euclidean distance between any two distinct points (integer, avoids float judging)."""
    n = len(points)
    if n < 2:
        raise OracleError("closest_pair_min_sq_distance requires at least 2 points")
    best = None
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            d = dx * dx + dy * dy
            if best is None or d < best:
                best = d
    return best


def count_inversions(nums: list[int]) -> int:
    """Number of index pairs (i, j) with i < j and nums[i] > nums[j]."""
    n = len(nums)
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] > nums[j]:
                count += 1
    return count


def fast_power_exact(base: int, exp: int) -> int:
    """Exact base**exp (arbitrary precision), the value a divide-and-conquer fast-power computes."""
    if exp < 0:
        raise OracleError("fast_power_exact undefined for negative exponents")
    return base ** exp


def karatsuba_multiply(a: int, b: int) -> int:
    """Exact product a*b (arbitrary precision) — the value Karatsuba multiplication computes."""
    return a * b


def majority_element(nums: list[int]) -> int:
    """The element occurring in more than half of nums (guaranteed to exist by the problem contract)."""
    from collections import Counter
    if not nums:
        raise OracleError("majority_element undefined for empty array")
    val, cnt = Counter(nums).most_common(1)[0]
    if cnt <= len(nums) // 2:
        raise OracleError("majority_element: no element exceeds n/2 occurrences")
    return val


def matrix_power_mod(matrix: list[list[int]], k: int, mod: int) -> list[list[int]]:
    """matrix**k mod `mod`, via fast exponentiation by squaring."""
    n = len(matrix)
    if k < 0 or mod < 1:
        raise OracleError("matrix_power_mod: invalid k or mod")

    def mat_mult(A, B):
        return [[sum(A[i][x] * B[x][j] for x in range(n)) % mod for j in range(n)] for i in range(n)]

    result = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    base = [row[:] for row in matrix]
    e = k
    while e > 0:
        if e & 1:
            result = mat_mult(result, base)
        base = mat_mult(base, base)
        e >>= 1
    return result


def median_of_medians_kth_smallest(nums: list[int], k: int) -> int:
    """The k-th smallest element (1-indexed) of nums — the value median-of-medians selection finds."""
    if k < 1 or k > len(nums):
        raise OracleError(f"median_of_medians_kth_smallest: k={k} out of range for length {len(nums)}")
    return sorted(nums)[k - 1]


def polynomial_multiply(a: list[int], b: list[int]) -> list[int]:
    """Coefficient list of the product of two polynomials (a[i], b[i] = coefficient of x^i)."""
    if not a or not b:
        raise OracleError("polynomial_multiply requires non-empty coefficient lists")
    result = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            result[i + j] += ai * bj
    return result


def strassen_matrix_multiply(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    """Standard matrix product A x B — the value Strassen's algorithm computes faster asymptotically."""
    n, m, p = len(a), len(a[0]), len(b[0])
    if len(b) != m:
        raise OracleError("strassen_matrix_multiply: incompatible dimensions")
    return [[sum(a[i][x] * b[x][j] for x in range(m)) for j in range(p)] for i in range(n)]


# ── String family — see docs/atlascode-progress.md ──

def z_array(s: str) -> list[int]:
    """Z-array of s (Z[i] = length of the longest substring starting at i that
    is also a prefix of s); Z[0] is defined as 0 by convention (unused)."""
    n = len(s)
    z = [0] * n
    l, r = 0, 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z


def longest_common_substring_length(s1: str, s2: str) -> int:
    """Length of the longest CONTIGUOUS common substring of s1 and s2 (0 if none share any character)."""
    n, m = len(s1), len(s2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    best = 0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                best = max(best, dp[i][j])
    return best


def longest_palindromic_substring_length(s: str) -> int:
    """Length of the longest substring of s that is a palindrome (expand-around-center)."""
    n = len(s)
    if n == 0:
        return 0
    best = 1

    def expand(l: int, r: int) -> int:
        while l >= 0 and r < n and s[l] == s[r]:
            l -= 1
            r += 1
        return r - l - 1

    for i in range(n):
        best = max(best, expand(i, i), expand(i, i + 1))
    return best


def count_palindromic_substrings(s: str) -> int:
    """Total number of palindromic substrings of s (counting distinct positions, not distinct values)."""
    n = len(s)
    count = 0

    def expand(l: int, r: int) -> None:
        nonlocal count
        while l >= 0 and r < n and s[l] == s[r]:
            count += 1
            l -= 1
            r += 1

    for i in range(n):
        expand(i, i)
        expand(i, i + 1)
    return count


def run_length_encode(s: str) -> str:
    """Run-length encoding: each maximal run of a repeated character becomes '<count><char>'."""
    if not s:
        return ""
    parts = []
    i = 0
    n = len(s)
    while i < n:
        j = i
        while j < n and s[j] == s[i]:
            j += 1
        parts.append(f"{j - i}{s[i]}")
        i = j
    return "".join(parts)


def suffix_array(s: str) -> list[int]:
    """Suffix array of s: starting indices of all suffixes, sorted lexicographically."""
    if not s:
        raise OracleError("suffix_array undefined for empty string")
    n = len(s)
    return sorted(range(n), key=lambda i: s[i:])


def count_distinct_substrings_length_k(s: str, k: int) -> int:
    """Number of distinct substrings of s with length exactly k."""
    if k <= 0 or k > len(s):
        raise OracleError(f"count_distinct_substrings_length_k: invalid k={k} for length {len(s)}")
    return len({s[i:i + k] for i in range(len(s) - k + 1)})


# ── Array/Hashing pattern family — see docs/atlascode-progress.md ──
# PATTERN_PROBLEM origin (no single canonical algorithm backs "array/hashing").

def contains_duplicate_within_k(nums: list[int], k: int) -> bool:
    """True if two equal elements exist within index distance <= k."""
    if k < 0:
        raise OracleError("contains_duplicate_within_k: k must be non-negative")
    last_seen: dict[int, int] = {}
    for i, x in enumerate(nums):
        if x in last_seen and i - last_seen[x] <= k:
            return True
        last_seen[x] = i
    return False


def product_except_self(nums: list[int]) -> list[int]:
    """result[i] = product of all nums except nums[i], without division."""
    n = len(nums)
    if n < 2:
        raise OracleError("product_except_self requires at least 2 elements")
    result = [1] * n
    prefix = 1
    for i in range(n):
        result[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(n - 1, -1, -1):
        result[i] *= suffix
        suffix *= nums[i]
    return result


def subarray_sum_equals_k(nums: list[int], k: int) -> int:
    """Number of contiguous subarrays summing to exactly k."""
    counts: dict[int, int] = {0: 1}
    total = 0
    result = 0
    for x in nums:
        total += x
        result += counts.get(total - k, 0)
        counts[total] = counts.get(total, 0) + 1
    return result


def top_k_frequent(nums: list[int], k: int) -> list[int]:
    """The k most frequent elements; ties broken by smaller value first (deterministic)."""
    from collections import Counter
    if k <= 0 or k > len(set(nums)):
        raise OracleError(f"top_k_frequent: invalid k={k}")
    counts = Counter(nums)
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [v for v, _ in items[:k]]


def longest_consecutive_sequence(nums: list[int]) -> int:
    """Length of the longest run of consecutive integers present in nums (any order)."""
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:
            length = 1
            while x + length in s:
                length += 1
            best = max(best, length)
    return best


def group_anagrams_count(strs: list[str]) -> int:
    """Number of distinct anagram groups among strs."""
    return len({"".join(sorted(s)) for s in strs})


def is_anagram(s: str, t: str) -> bool:
    """True if t is an anagram of s (same multiset of characters)."""
    from collections import Counter
    return Counter(s) == Counter(t)


def first_unique_char_index(s: str) -> int:
    """Index of the first character that appears exactly once in s, else -1."""
    from collections import Counter
    counts = Counter(s)
    for i, c in enumerate(s):
        if counts[c] == 1:
            return i
    return -1


def intersection_sorted(nums1: list[int], nums2: list[int]) -> list[int]:
    """Sorted list of distinct values present in both nums1 and nums2."""
    return sorted(set(nums1) & set(nums2))


def missing_number(nums: list[int]) -> int:
    """The single missing number from the range [0, n] given n numbers from it."""
    n = len(nums)
    return n * (n + 1) // 2 - sum(nums)


def majority_element_ii(nums: list[int]) -> list[int]:
    """All elements occurring more than n/3 times, sorted ascending (0, 1, or 2 such values)."""
    from collections import Counter
    n = len(nums)
    counts = Counter(nums)
    return sorted(x for x, cnt in counts.items() if cnt > n // 3)


def two_sum_count_pairs(nums: list[int], target: int) -> int:
    """Number of index pairs (i, j) with i < j and nums[i] + nums[j] == target."""
    seen: dict[int, int] = {}
    count = 0
    for x in nums:
        count += seen.get(target - x, 0)
        seen[x] = seen.get(x, 0) + 1
    return count


def subarray_sums_divisible_by_k(nums: list[int], k: int) -> int:
    """Number of contiguous subarrays whose sum is divisible by k."""
    if k == 0:
        raise OracleError("subarray_sums_divisible_by_k: k must be non-zero")
    counts: dict[int, int] = {0: 1}
    total = 0
    result = 0
    for x in nums:
        total += x
        r = total % k
        result += counts.get(r, 0)
        counts[r] = counts.get(r, 0) + 1
    return result


def three_sum_count_triplets(nums: list[int]) -> int:
    """Number of DISTINCT value-triplets (by value, not index) summing to zero."""
    nums = sorted(nums)
    n = len(nums)
    count = 0
    for i in range(n):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        lo, hi = i + 1, n - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if s == 0:
                count += 1
                lo += 1
                hi -= 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1
                while lo < hi and nums[hi] == nums[hi + 1]:
                    hi -= 1
            elif s < 0:
                lo += 1
            else:
                hi -= 1
    return count


def container_with_most_water(heights: list[int]) -> int:
    """Max water area between two vertical lines (two-pointer)."""
    lo, hi = 0, len(heights) - 1
    best = 0
    while lo < hi:
        best = max(best, min(heights[lo], heights[hi]) * (hi - lo))
        if heights[lo] < heights[hi]:
            lo += 1
        else:
            hi -= 1
    return best


# ── Stack family — see docs/atlascode-progress.md ──

def valid_parentheses(s: str) -> bool:
    """True if s is a well-formed sequence of (), [], {}."""
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for c in s:
        if c in "([{":
            stack.append(c)
        elif c in pairs:
            if not stack or stack.pop() != pairs[c]:
                return False
        else:
            raise OracleError(f"valid_parentheses: unexpected character {c!r}")
    return not stack


def daily_temperatures(temps: list[int]) -> list[int]:
    """days_to_wait[i] = smallest j>0 with temps[i+j] > temps[i], else 0 (monotonic stack)."""
    n = len(temps)
    result = [0] * n
    stack: list[int] = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            result[j] = i - j
        stack.append(i)
    return result


def next_greater_element(nums: list[int]) -> list[int]:
    """result[i] = next element to the right greater than nums[i], else -1 (non-circular)."""
    n = len(nums)
    result = [-1] * n
    stack: list[int] = []
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            result[stack.pop()] = x
        stack.append(i)
    return result


def largest_rectangle_in_histogram(heights: list[int]) -> int:
    """Max rectangle area in a histogram (monotonic stack)."""
    stack: list[int] = []
    best = 0
    for i, h in enumerate(heights + [0]):
        while stack and heights[stack[-1]] >= h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            best = max(best, height * width)
        stack.append(i)
    return best


def min_stack_simulate(ops: list[tuple[str, int | None]]) -> list[int]:
    """Simulate PUSH x / POP operations; return the stack minimum after each PUSH."""
    stack: list[int] = []
    result = []
    for op in ops:
        if op[0] == "PUSH":
            stack.append(op[1])
            result.append(min(stack))
        elif op[0] == "POP":
            if not stack:
                raise OracleError("min_stack_simulate: POP on empty stack")
            stack.pop()
        else:
            raise OracleError(f"min_stack_simulate: unknown op {op[0]!r}")
    return result


def evaluate_rpn(tokens: list[str]) -> int:
    """Evaluate a Reverse Polish Notation expression (integer division truncates toward zero)."""
    stack: list[int] = []
    for tok in tokens:
        if tok in ("+", "-", "*", "/"):
            if len(stack) < 2:
                raise OracleError("evaluate_rpn: malformed expression")
            b = stack.pop()
            a = stack.pop()
            if tok == "+":
                stack.append(a + b)
            elif tok == "-":
                stack.append(a - b)
            elif tok == "*":
                stack.append(a * b)
            else:
                stack.append(int(a / b))
        else:
            stack.append(int(tok))
    if len(stack) != 1:
        raise OracleError("evaluate_rpn: malformed expression")
    return stack[0]


def remove_k_digits(num: str, k: int) -> str:
    """Smallest possible number (as a string, no leading zeros) after removing k digits."""
    if k < 0 or k > len(num):
        raise OracleError("remove_k_digits: invalid k")
    stack: list[str] = []
    remaining = k
    for d in num:
        while remaining > 0 and stack and stack[-1] > d:
            stack.pop()
            remaining -= 1
        stack.append(d)
    if remaining > 0:
        stack = stack[:-remaining]
    result = "".join(stack).lstrip("0")
    return result if result else "0"


def trapping_rain_water(heights: list[int]) -> int:
    """Total water trapped between bars after raining (two-pointer)."""
    n = len(heights)
    if n == 0:
        return 0
    left, right = 0, n - 1
    left_max, right_max = heights[0], heights[-1]
    water = 0
    while left < right:
        if left_max <= right_max:
            left += 1
            left_max = max(left_max, heights[left])
            water += left_max - heights[left]
        else:
            right -= 1
            right_max = max(right_max, heights[right])
            water += right_max - heights[right]
    return water


# ── Bit-manipulation pattern family — see docs/atlascode-progress.md ──

def single_number(nums: list[int]) -> int:
    """The element appearing exactly once, given every other element appears exactly twice (XOR trick)."""
    result = 0
    for x in nums:
        result ^= x
    return result


def single_number_ii(nums: list[int]) -> int:
    """The element appearing exactly once, given every other element appears exactly three times."""
    result = 0
    for bit in range(32):
        count = sum((x >> bit) & 1 for x in nums)
        if count % 3:
            result |= (1 << bit)
    return result


def counting_bits(n: int) -> list[int]:
    """popcount(i) for every i in [0, n]."""
    if n < 0:
        raise OracleError("counting_bits undefined for negative n")
    return [bin(i).count("1") for i in range(n + 1)]


def reverse_bits_32(n: int) -> int:
    """Reverse the bits of a 32-bit unsigned integer."""
    if not 0 <= n < (1 << 32):
        raise OracleError("reverse_bits_32 requires a 32-bit unsigned value")
    result = 0
    for _ in range(32):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result


def hamming_distance(x: int, y: int) -> int:
    """Number of bit positions where x and y differ."""
    return bin(x ^ y).count("1")


def is_power_of_two(n: int) -> bool:
    """True if n is a positive power of two."""
    return n > 0 and (n & (n - 1)) == 0


def count_set_bits(n: int) -> int:
    """Number of 1 bits in the binary representation of non-negative n."""
    if n < 0:
        raise OracleError("count_set_bits undefined for negative n")
    return bin(n).count("1")


def max_xor_of_two_numbers(nums: list[int]) -> int:
    """Maximum XOR value of any pair of elements in nums."""
    if len(nums) < 2:
        raise OracleError("max_xor_of_two_numbers requires at least 2 elements")
    best = 0
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            best = max(best, nums[i] ^ nums[j])
    return best


# ── Tree pattern family — see docs/atlascode-progress.md ──
# Canonical serialization: level-order list with None for missing children
# (LeetCode convention), e.g. [3, 9, 20, None, None, 15, 7]. Established here
# as the ONE shared tree input format for every tree problem in AtlasCode.

class _TreeNode:
    __slots__ = ("val", "left", "right")

    def __init__(self, val: int) -> None:
        self.val = val
        self.left: "_TreeNode | None" = None
        self.right: "_TreeNode | None" = None


def _build_tree(values: list) -> "_TreeNode | None":
    from collections import deque
    if not values or values[0] is None:
        return None
    root = _TreeNode(values[0])
    queue = deque([root])
    i = 1
    n = len(values)
    while queue and i < n:
        node = queue.popleft()
        if i < n:
            if values[i] is not None:
                node.left = _TreeNode(values[i])
                queue.append(node.left)
            i += 1
        if i < n:
            if values[i] is not None:
                node.right = _TreeNode(values[i])
                queue.append(node.right)
            i += 1
    return root


def max_depth_binary_tree(values: list) -> int:
    """Maximum depth (number of nodes on the longest root-to-leaf path)."""
    root = _build_tree(values)

    def depth(node):
        if node is None:
            return 0
        return 1 + max(depth(node.left), depth(node.right))

    return depth(root)


def diameter_of_binary_tree(values: list) -> int:
    """Length (in edges) of the longest path between any two nodes."""
    root = _build_tree(values)
    best = 0

    def height(node):
        nonlocal best
        if node is None:
            return 0
        l = height(node.left)
        r = height(node.right)
        best = max(best, l + r)
        return 1 + max(l, r)

    height(root)
    return best


def is_balanced_binary_tree(values: list) -> bool:
    """True if, for every node, the left/right subtree heights differ by at most 1."""
    root = _build_tree(values)

    def check(node):
        if node is None:
            return 0
        l = check(node.left)
        if l == -1:
            return -1
        r = check(node.right)
        if r == -1 or abs(l - r) > 1:
            return -1
        return 1 + max(l, r)

    return check(root) != -1


def is_valid_bst(values: list) -> bool:
    """True if the tree satisfies the binary search tree property."""
    root = _build_tree(values)

    def valid(node, lo, hi):
        if node is None:
            return True
        if not (lo < node.val < hi):
            return False
        return valid(node.left, lo, node.val) and valid(node.right, node.val, hi)

    return valid(root, float("-inf"), float("inf"))


def is_symmetric_tree(values: list) -> bool:
    """True if the tree is a mirror image of itself around its center."""
    root = _build_tree(values)

    def mirror(a, b):
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)

    return root is None or mirror(root.left, root.right)


def invert_tree_preorder(values: list) -> list[int]:
    """Preorder traversal of the tree after swapping every left/right child."""
    root = _build_tree(values)

    def invert(node):
        if node is None:
            return
        node.left, node.right = node.right, node.left
        invert(node.left)
        invert(node.right)

    invert(root)
    result = []

    def preorder(node):
        if node is None:
            return
        result.append(node.val)
        preorder(node.left)
        preorder(node.right)

    preorder(root)
    return result


def path_sum_exists(values: list, target: int) -> bool:
    """True if some root-to-leaf path sums exactly to target."""
    root = _build_tree(values)

    def dfs(node, remaining):
        if node is None:
            return False
        if node.left is None and node.right is None:
            return remaining == node.val
        return dfs(node.left, remaining - node.val) or dfs(node.right, remaining - node.val)

    return dfs(root, target)


def count_tree_nodes(values: list) -> int:
    """Total number of nodes in the tree."""
    root = _build_tree(values)

    def count(node):
        if node is None:
            return 0
        return 1 + count(node.left) + count(node.right)

    return count(root)


def lowest_common_ancestor_bst(values: list, p: int, q: int) -> int:
    """Value of the lowest common ancestor of nodes with values p and q in a BST."""
    node = _build_tree(values)
    while node:
        if p < node.val and q < node.val:
            node = node.left
        elif p > node.val and q > node.val:
            node = node.right
        else:
            return node.val
    raise OracleError("lowest_common_ancestor_bst: traversal fell off the tree")


def kth_smallest_in_bst(values: list, k: int) -> int:
    """The k-th smallest value (1-indexed) in a BST, via inorder traversal."""
    root = _build_tree(values)
    result: list[int] = []

    def inorder(node):
        if node is None or len(result) >= k:
            return
        inorder(node.left)
        if len(result) < k:
            result.append(node.val)
        inorder(node.right)

    inorder(root)
    if len(result) < k:
        raise OracleError(f"kth_smallest_in_bst: k={k} exceeds tree size")
    return result[k - 1]


def level_order_traversal(values: list) -> list[list[int]]:
    """Node values grouped by depth level, top to bottom, left to right."""
    root = _build_tree(values)
    if root is None:
        return []
    result = []
    level = [root]
    while level:
        result.append([n.val for n in level])
        next_level = []
        for n in level:
            if n.left:
                next_level.append(n.left)
            if n.right:
                next_level.append(n.right)
        level = next_level
    return result


def right_side_view(values: list) -> list[int]:
    """The value of the rightmost node at each depth level, top to bottom."""
    root = _build_tree(values)
    if root is None:
        return []
    result = []
    level = [root]
    while level:
        result.append(level[-1].val)
        next_level = []
        for n in level:
            if n.left:
                next_level.append(n.left)
            if n.right:
                next_level.append(n.right)
        level = next_level
    return result


def same_tree(values1: list, values2: list) -> bool:
    """True if two trees are structurally identical with the same node values."""
    t1 = _build_tree(values1)
    t2 = _build_tree(values2)

    def same(a, b):
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return a.val == b.val and same(a.left, b.left) and same(a.right, b.right)

    return same(t1, t2)


def sum_root_to_leaf_numbers(values: list) -> int:
    """Sum over all root-to-leaf paths, each read as one decimal number."""
    root = _build_tree(values)
    total = 0

    def dfs(node, cur):
        nonlocal total
        if node is None:
            return
        cur = cur * 10 + node.val
        if node.left is None and node.right is None:
            total += cur
            return
        dfs(node.left, cur)
        dfs(node.right, cur)

    dfs(root, 0)
    return total


def binary_tree_max_path_sum(values: list) -> int:
    """Maximum sum of any downward-or-through-node path (path may start/end at any node)."""
    root = _build_tree(values)
    best = float("-inf")

    def dfs(node):
        nonlocal best
        if node is None:
            return 0
        l = max(dfs(node.left), 0)
        r = max(dfs(node.right), 0)
        best = max(best, node.val + l + r)
        return node.val + max(l, r)

    dfs(root)
    return int(best)


# ── Dynamic-programming variant family — see docs/atlascode-progress.md ──

def triangle_min_path_sum(triangle: list[list[int]]) -> int:
    """Minimum sum path from the top of a triangle to the bottom (adjacent moves only)."""
    if not triangle:
        raise OracleError("triangle_min_path_sum requires a non-empty triangle")
    dp = triangle[-1][:]
    for row in range(len(triangle) - 2, -1, -1):
        for col in range(row + 1):
            dp[col] = triangle[row][col] + min(dp[col], dp[col + 1])
    return dp[0]


def max_profit_single_transaction(prices: list[int]) -> int:
    """Max profit from at most one buy then one later sell (0 if no profit possible)."""
    if not prices:
        return 0
    min_price = prices[0]
    best = 0
    for p in prices[1:]:
        best = max(best, p - min_price)
        min_price = min(min_price, p)
    return best


def max_profit_unlimited_transactions(prices: list[int]) -> int:
    """Max profit from any number of buy/sell transactions (no overlapping holdings)."""
    profit = 0
    for i in range(1, len(prices)):
        if prices[i] > prices[i - 1]:
            profit += prices[i] - prices[i - 1]
    return profit


def can_partition_equal_subset(nums: list[int]) -> bool:
    """True if nums can be split into two subsets with equal sums."""
    total = sum(nums)
    if total % 2 != 0:
        return False
    return subset_sum_exists(nums, total // 2)


def target_sum_ways(nums: list[int], target: int) -> int:
    """Number of ways to assign +/- signs to nums so they sum to target."""
    counts: dict[int, int] = {0: 1}
    for x in nums:
        new_counts: dict[int, int] = {}
        for total, cnt in counts.items():
            new_counts[total + x] = new_counts.get(total + x, 0) + cnt
            new_counts[total - x] = new_counts.get(total - x, 0) + cnt
        counts = new_counts
    return counts.get(target, 0)


def perfect_squares_min_count(n: int) -> int:
    """Minimum number of perfect squares (1, 4, 9, ...) summing to n."""
    if n < 0:
        raise OracleError("perfect_squares_min_count undefined for negative n")
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        best = float("inf")
        j = 1
        while j * j <= i:
            best = min(best, dp[i - j * j] + 1)
            j += 1
        dp[i] = best
    return dp[n]


def combination_sum_iv_count(nums: list[int], target: int) -> int:
    """Number of ORDERED sequences (permutations, elements reusable) from nums summing to target."""
    dp = [0] * (target + 1)
    dp[0] = 1
    for t in range(1, target + 1):
        for x in nums:
            if x <= t:
                dp[t] += dp[t - x]
    return dp[target]


def delete_and_earn(nums: list[int]) -> int:
    """Max points from repeatedly taking a value (removing all instances of value±1) — house-robber on frequency array."""
    from collections import Counter
    if not nums:
        return 0
    counts = Counter(nums)
    max_val = max(counts)
    points = [0] * (max_val + 1)
    for val, cnt in counts.items():
        points[val] = val * cnt
    prev, curr = 0, 0
    for val in range(max_val + 1):
        prev, curr = curr, max(curr, prev + points[val])
    return curr


def max_subarray_circular(nums: list[int]) -> int:
    """Max sum of a contiguous subarray in a CIRCULAR array (wraparound allowed)."""
    if not nums:
        raise OracleError("max_subarray_circular undefined for empty array")
    total = sum(nums)

    def kadane_max(arr):
        best = cur = arr[0]
        for x in arr[1:]:
            cur = max(x, cur + x)
            best = max(best, cur)
        return best

    def kadane_min(arr):
        best = cur = arr[0]
        for x in arr[1:]:
            cur = min(x, cur + x)
            best = min(best, cur)
        return best

    max_normal = kadane_max(nums)
    if max_normal < 0:
        return max_normal
    max_wrap = total - kadane_min(nums)
    return max(max_normal, max_wrap)


def jump_game_ii_min_jumps(nums: list[int]) -> int:
    """Minimum number of jumps to reach the last index (guaranteed reachable)."""
    n = len(nums)
    if n <= 1:
        return 0
    jumps = 0
    cur_end = 0
    farthest = 0
    for i in range(n - 1):
        farthest = max(farthest, i + nums[i])
        if i == cur_end:
            jumps += 1
            cur_end = farthest
    return jumps


# ── Linked-list pattern family — see docs/atlascode-progress.md ──
# Represented as plain arrays over stdin (standard online-judge simplification
# for a stdin/stdout judge — no pointer structure needed to test the logic).

def reverse_linked_list(values: list[int]) -> list[int]:
    """The list reversed."""
    return values[::-1]


def linked_list_has_cycle(pos: int) -> bool:
    """True if the list has a cycle (pos = index the tail connects back to, -1 for none)."""
    return pos != -1


def merge_two_sorted_lists(a: list[int], b: list[int]) -> list[int]:
    """The merged, still-sorted list from two already-sorted lists."""
    return sorted(a + b)


def remove_nth_from_end(values: list[int], n: int) -> list[int]:
    """The list with the n-th node from the end removed (1-indexed)."""
    if not 1 <= n <= len(values):
        raise OracleError(f"remove_nth_from_end: n={n} out of range for length {len(values)}")
    idx = len(values) - n
    return values[:idx] + values[idx + 1:]


def middle_of_linked_list(values: list[int]) -> int:
    """The middle node's value (the SECOND middle for even-length lists, LeetCode convention)."""
    if not values:
        raise OracleError("middle_of_linked_list undefined for an empty list")
    return values[len(values) // 2]


def is_palindrome_linked_list(values: list[int]) -> bool:
    """True if the list reads the same forwards and backwards."""
    return values == values[::-1]


# ── Backtracking-count family — see docs/atlascode-progress.md ──
# Every answer is a COUNT (never an enumeration of the actual structures),
# which keeps it a unique scalar and avoids the multi-valid-answer trap that
# otherwise keeps `backtracking` in PROPERTY_JUDGE.

def _is_palindrome_table(s: str) -> list[list[bool]]:
    n = len(s)
    is_pal = [[False] * n for _ in range(n)]
    for i in range(n):
        is_pal[i][i] = True
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and (length == 2 or is_pal[i + 1][j - 1]):
                is_pal[i][j] = True
    return is_pal


def palindrome_partition_min_cuts(s: str) -> int:
    """Minimum cuts needed to partition s so every piece is a palindrome."""
    n = len(s)
    if n == 0:
        raise OracleError("palindrome_partition_min_cuts undefined for empty string")
    is_pal = _is_palindrome_table(s)
    dp = [0] * n
    for i in range(n):
        if is_pal[0][i]:
            dp[i] = 0
        else:
            dp[i] = min(dp[j] + 1 for j in range(i) if is_pal[j + 1][i])
    return dp[n - 1]


def palindrome_partition_count_ways(s: str) -> int:
    """Number of ways to partition s so every piece is a palindrome."""
    n = len(s)
    is_pal = _is_palindrome_table(s)
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        for j in range(i):
            if is_pal[j][i - 1]:
                dp[i] += dp[j]
    return dp[n]


def restore_ip_addresses_count(s: str) -> int:
    """Number of ways to insert 3 dots into s to form a valid IPv4 address."""
    n = len(s)

    def valid(seg: str) -> bool:
        if not seg or len(seg) > 3:
            return False
        if len(seg) > 1 and seg[0] == "0":
            return False
        return 0 <= int(seg) <= 255

    count = 0
    for i in range(1, 4):
        for j in range(i + 1, i + 4):
            for k in range(j + 1, j + 4):
                if k < n:
                    a, b, c, d = s[:i], s[i:j], s[j:k], s[k:]
                    if valid(a) and valid(b) and valid(c) and valid(d):
                        count += 1
    return count


def word_break_count_ways(s: str, word_dict: list[str]) -> int:
    """Number of distinct ways to segment s into space-separated dictionary words."""
    words = set(word_dict)
    n = len(s)
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in words:
                dp[i] += dp[j]
    return dp[n]


def unique_permutations_count(nums: list[int]) -> int:
    """Number of DISTINCT permutations of a multiset (accounts for repeated values)."""
    from collections import Counter
    import math
    counts = Counter(nums)
    result = math.factorial(len(nums))
    for c in counts.values():
        result //= math.factorial(c)
    return result


def find_all_anagram_starts(s: str, p: str) -> list[int]:
    """All starting indices in s where a permutation (anagram) of p occurs, ascending."""
    n, m = len(s), len(p)
    if m == 0 or m > n:
        return []
    need: dict[str, int] = {}
    for c in p:
        need[c] = need.get(c, 0) + 1
    window: dict[str, int] = {}
    for c in s[:m]:
        window[c] = window.get(c, 0) + 1
    result = []
    if window == need:
        result.append(0)
    for i in range(m, n):
        right_c = s[i]
        window[right_c] = window.get(right_c, 0) + 1
        left_c = s[i - m]
        window[left_c] -= 1
        if window[left_c] == 0:
            del window[left_c]
        if window == need:
            result.append(i - m + 1)
    return result
