"""Ports Function Mode Swift solutions for as many of the 208 currently-
missing problems as possible, single language "swift". Mirrors the pattern
in scale_mega_cluster6.py but for one language and a much larger problem set.

Each entry in _BUILDERS maps problem_id -> build(wrong: bool) -> str, a
top-level Swift `func` (no class wrapper -- see compiled_adapters.py's
SwiftFunctionAdapter docstring). Every parameter uses the `_` external-label
wildcard since the driver calls positionally.

10 problems are EXCLUDED as a genuine architectural limitation shared with
every fixed-width-int language (see docs/atlascode-bigint-numeric-audit.json):
fibonacci-dp, karatsuba, catalan-number, fast-power, decode-ways,
unique-paths, combination-sum-iv-count, evaluate-reverse-polish-notation,
maximum-product-subarray, sum-root-to-leaf-numbers -- real corpus values
exceed even Int64 range (Swift's Int is 64-bit on this platform, unlike
C's 32-bit `int`, so it recovers trapping-rain-water/reverse-bits/
combination-sum-count which those languages had to skip).

min-stack-simulation is EXCLUDED because Swift Function Mode does not
support tuple-typed contracts yet.
"""
from __future__ import annotations

import asyncio
import json
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))
sys.path.insert(0, str(Path(__file__).parent))
import logging
logging.disable(logging.CRITICAL)

from algorithm_atlas.atlascode.function_mode.contracts import FunctionContract
from algorithm_atlas.atlascode.function_mode.runner import FunctionCase, evaluate_function
import atlascode_ledger as ledger

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"
LANG = "swift"

# ── shared tree helper injected for tree problems ───────────────────────────
_TREE_HELPERS = ""  # TreeNode class is auto-injected by compose_program; no local decl needed


# ═════════════════════════ SORTING (MUT=arr, all identical signature) ══════
def _sort_builder(name, body_lines, wrong_body_lines):
    def build(wrong):
        lines = wrong_body_lines if wrong else body_lines
        joined = "\n".join("    " + l for l in lines)
        return f"func {name}(_ arr: inout [Int]) {{\n{joined}\n}}\n"
    return build

_bitonic_sort = _sort_builder(
    "bitonic_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_bucket_sort = _sort_builder(
    "bucket_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_cocktail_sort = _sort_builder(
    "cocktail_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_comb_sort = _sort_builder(
    "comb_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_counting_sort = _sort_builder(
    "counting_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_cycle_sort = _sort_builder(
    "cycle_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_gnome_sort = _sort_builder(
    "gnome_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_heap_sort = _sort_builder(
    "heap_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_insertion_sort = _sort_builder(
    "insertion_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_merge_sort_b = _sort_builder(
    "merge_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_odd_even_sort = _sort_builder(
    "odd_even_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_pancake_sort = _sort_builder(
    "pancake_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_patience_sort = _sort_builder(
    "patience_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_quick_sort_b = _sort_builder(
    "quick_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_radix_sort = _sort_builder(
    "radix_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_selection_sort = _sort_builder(
    "selection_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_shell_sort = _sort_builder(
    "shell_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_stooge_sort = _sort_builder(
    "stooge_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_strand_sort = _sort_builder(
    "strand_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)
_tim_sort = _sort_builder(
    "tim_sort",
    ["arr.sort()"],
    ["arr.sort(); if arr.count > 0 { arr[0] += 1 }"],
)


# ═════════════════════════ MATH / BIT MISC ═════════════════════════════════
def _gcd_euclidean(wrong):
    op = "-" if wrong else "+"
    return (f"func gcd(_ a: Int, _ b: Int) -> Int {{\n"
            f"    var x = a, y = b\n"
            f"    while y != 0 {{ let t = y; y = x % y; x = t }}\n"
            f"    return x {op} 0\n}}\n")


def _collatz(wrong):
    a = " + 1" if wrong else ""
    return (f"func collatz(_ n: Int) -> Int {{\n"
            f"    var m = n; var steps = 0\n"
            f"    while m != 1 {{ m = (m % 2 == 0) ? m / 2 : 3 * m + 1; steps += 1 }}\n"
            f"    return steps{a}\n}}\n")


def _hamming_distance(wrong):
    a = " + 1" if wrong else ""
    return (f"func hamming_distance(_ x: Int, _ y: Int) -> Int {{\n"
            f"    return (x ^ y).nonzeroBitCount{a}\n}}\n")


def _number_of_1_bits(wrong):
    a = " + 1" if wrong else ""
    return (f"func hamming_weight(_ n: Int) -> Int {{\n"
            f"    return UInt32(truncatingIfNeeded: n).nonzeroBitCount{a}\n}}\n")


def _power_of_two(wrong):
    op = "!" if wrong else ""
    return (f"func is_power_of_two(_ n: Int) -> Bool {{\n"
            f"    return {op}(n > 0 && (n & (n - 1)) == 0)\n}}\n")


def _reverse_bits(wrong):
    a = " + 1" if wrong else ""
    return (f"func reverse_bits(_ n: Int) -> Int {{\n"
            f"    var result: Int = 0\n"
            f"    var v = UInt32(truncatingIfNeeded: n)\n"
            f"    for _ in 0..<32 {{\n"
            f"        result = (result << 1) | Int(v & 1)\n"
            f"        v >>= 1\n"
            f"    }}\n"
            f"    return result{a}\n}}\n")


def _integer_square_root(wrong):
    a = " + 1" if wrong else ""
    return (f"func my_sqrt(_ n: Int) -> Int {{\n"
            f"    if n < 2 {{ return n{a} }}\n"
            f"    var lo = 1, hi = n\n"
            f"    while lo < hi {{\n"
            f"        let mid = lo + (hi - lo + 1) / 2\n"
            f"        if mid <= n / mid {{ lo = mid }} else {{ hi = mid - 1 }}\n"
            f"    }}\n"
            f"    return lo{a}\n}}\n")


def _modular_exponentiation(wrong):
    a = " + 1" if wrong else ""
    return (f"func modular_exponentiation(_ base: Int, _ exp: Int, _ mod: Int) -> Int {{\n"
            f"    if mod == 1 {{ return 0{a} }}\n"
            f"    var result = 1\n"
            f"    var b = base % mod\n"
            f"    if b < 0 {{ b += mod }}\n"
            f"    var e = exp\n"
            f"    while e > 0 {{\n"
            f"        if e & 1 == 1 {{ result = (result * b) % mod }}\n"
            f"        e >>= 1\n"
            f"        b = (b * b) % mod\n"
            f"    }}\n"
            f"    return result{a}\n}}\n")


def _number_of_divisors(wrong):
    a = " + 1" if wrong else ""
    return (f"func number_of_divisors(_ n: Int) -> Int {{\n"
            f"    var count = 0\n"
            f"    var i = 1\n"
            f"    while i * i <= n {{\n"
            f"        if n % i == 0 {{ count += (i * i == n) ? 1 : 2 }}\n"
            f"        i += 1\n"
            f"    }}\n"
            f"    return count{a}\n}}\n")


def _sieve_of_eratosthenes(wrong):
    a = "x" if wrong else ""
    return (f"func sieve_of_eratosthenes(_ n: Int) -> String {{\n"
            f"    if n < 2 {{ return \"\"{a} }}\n"
            f"    var isComposite = [Bool](repeating: false, count: n + 1)\n"
            f"    var primes: [Int] = []\n"
            f"    var i = 2\n"
            f"    while i <= n {{\n"
            f"        if !isComposite[i] {{\n"
            f"            primes.append(i)\n"
            f"            var j = i * i\n"
            f"            while j <= n {{ isComposite[j] = true; j += i }}\n"
            f"        }}\n"
            f"        i += 1\n"
            f"    }}\n"
            f"    return primes.map {{ String($0) }}.joined(separator: \" \"){a}\n}}\n")


def _euler_phi_sieve(wrong):
    a = " + 1" if wrong else ""
    return (f"func euler_phi_sieve(_ n: Int) -> Int {{\n"
            f"    var phi = Array(0...n)\n"
            f"    var i = 2\n"
            f"    while i <= n {{\n"
            f"        if phi[i] == i {{\n"
            f"            var j = i\n"
            f"            while j <= n {{ phi[j] -= phi[j] / i; j += i }}\n"
            f"        }}\n"
            f"        i += 1\n"
            f"    }}\n"
            f"    return phi[n]{a}\n}}\n")


def _euler_totient(wrong):
    a = " + 1" if wrong else ""
    return (f"func euler_totient(_ n: Int) -> Int {{\n"
            f"    var result = n\n"
            f"    var m = n\n"
            f"    var p = 2\n"
            f"    while p * p <= m {{\n"
            f"        if m % p == 0 {{\n"
            f"            while m % p == 0 {{ m /= p }}\n"
            f"            result -= result / p\n"
            f"        }}\n"
            f"        p += 1\n"
            f"    }}\n"
            f"    if m > 1 {{ result -= result / m }}\n"
            f"    return result{a}\n}}\n")


def _lucas_theorem(wrong):
    a = " + 1" if wrong else ""
    return (f"func ncr_small(_ n: Int, _ r: Int) -> Int {{\n"
            f"    if r > n {{ return 0 }}\n"
            f"    if r == 0 || r == n {{ return 1 }}\n"
            f"    var res = 1\n"
            f"    var rr = min(r, n - r)\n"
            f"    for i in 0..<rr {{ res = res * (n - i) / (i + 1) }}\n"
            f"    return res\n}}\n"
            f"func lucas_theorem(_ n: Int, _ k: Int, _ p: Int) -> Int {{\n"
            f"    var nn = n, kk = k\n"
            f"    var result = 1\n"
            f"    while nn > 0 || kk > 0 {{\n"
            f"        let ni = nn % p, ki = kk % p\n"
            f"        if ki > ni {{ return 0{a} }}\n"
            f"        result = (result * ncr_small(ni, ki)) % p\n"
            f"        nn /= p; kk /= p\n"
            f"    }}\n"
            f"    return result{a}\n}}\n")


def _miller_rabin(wrong):
    op = "!" if wrong else ""
    return (f"func mulmod_mr(_ a: Int, _ b: Int, _ m: Int) -> Int {{\n"
            f"    return Int((UInt64(a) &* UInt64(b)) % UInt64(m))\n}}\n"
            f"func powmod_mr(_ base: Int, _ exp: Int, _ m: Int) -> Int {{\n"
            f"    var result = 1 % m\n"
            f"    var b = base % m\n"
            f"    var e = exp\n"
            f"    while e > 0 {{\n"
            f"        if e & 1 == 1 {{ result = mulmod_mr(result, b, m) }}\n"
            f"        b = mulmod_mr(b, b, m)\n"
            f"        e >>= 1\n"
            f"    }}\n"
            f"    return result\n}}\n"
            f"func is_prime_mr(_ n: Int) -> Bool {{\n"
            f"    if n < 2 {{ return false }}\n"
            f"    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] {{\n"
            f"        if n % p == 0 {{ return n == p }}\n"
            f"    }}\n"
            f"    var d = n - 1; var r = 0\n"
            f"    while d % 2 == 0 {{ d /= 2; r += 1 }}\n"
            f"    for a in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] {{\n"
            f"        if a >= n {{ continue }}\n"
            f"        var x = powmod_mr(a, d, n)\n"
            f"        if x == 1 || x == n - 1 {{ continue }}\n"
            f"        var composite = true\n"
            f"        for _ in 0..<(r - 1) {{\n"
            f"            x = mulmod_mr(x, x, n)\n"
            f"            if x == n - 1 {{ composite = false; break }}\n"
            f"        }}\n"
            f"        if composite {{ return false }}\n"
            f"    }}\n"
            f"    return true\n}}\n"
            f"func miller_rabin(_ n: Int) -> Bool {{\n"
            f"    return {op}is_prime_mr(n)\n}}\n")


# ═════════════════════════ SEARCH ══════════════════════════════════════════
def _linear_search(wrong):
    a = " + 1" if wrong else ""
    return (f"func linear_search(_ nums: [Int], _ target: Int) -> Int {{\n"
            f"    for i in 0..<nums.count {{ if nums[i] == target {{ return i{a} }} }}\n"
            f"    return -1\n}}\n")


def _binary_search_b(wrong):
    a = " + 1" if wrong else ""
    return (f"func binary_search(_ nums: [Int], _ target: Int) -> Int {{\n"
            f"    var lo = 0, hi = nums.count - 1\n"
            f"    while lo <= hi {{\n"
            f"        let mid = lo + (hi - lo) / 2\n"
            f"        if nums[mid] == target {{ return mid{a} }}\n"
            f"        if nums[mid] < target {{ lo = mid + 1 }} else {{ hi = mid - 1 }}\n"
            f"    }}\n"
            f"    return -1\n}}\n")


def _first_occurrence(wrong):
    a = " + 1" if wrong else ""
    return (f"func first_occurrence(_ nums: [Int], _ target: Int) -> Int {{\n"
            f"    var lo = 0, hi = nums.count - 1, ans = -1\n"
            f"    while lo <= hi {{\n"
            f"        let mid = lo + (hi - lo) / 2\n"
            f"        if nums[mid] == target {{ ans = mid; hi = mid - 1 }}\n"
            f"        else if nums[mid] < target {{ lo = mid + 1 }} else {{ hi = mid - 1 }}\n"
            f"    }}\n"
            f"    return ans{a}\n}}\n")


def _last_occurrence(wrong):
    a = " + 1" if wrong else ""
    return (f"func last_occurrence(_ nums: [Int], _ target: Int) -> Int {{\n"
            f"    var lo = 0, hi = nums.count - 1, ans = -1\n"
            f"    while lo <= hi {{\n"
            f"        let mid = lo + (hi - lo) / 2\n"
            f"        if nums[mid] == target {{ ans = mid; lo = mid + 1 }}\n"
            f"        else if nums[mid] < target {{ lo = mid + 1 }} else {{ hi = mid - 1 }}\n"
            f"    }}\n"
            f"    return ans{a}\n}}\n")


def _count_occurrences_sorted(wrong):
    a = " + 1" if wrong else ""
    return (f"func first_occ_c(_ nums: [Int], _ target: Int) -> Int {{\n"
            f"    var lo = 0, hi = nums.count - 1, ans = -1\n"
            f"    while lo <= hi {{\n"
            f"        let mid = lo + (hi - lo) / 2\n"
            f"        if nums[mid] == target {{ ans = mid; hi = mid - 1 }}\n"
            f"        else if nums[mid] < target {{ lo = mid + 1 }} else {{ hi = mid - 1 }}\n"
            f"    }}\n"
            f"    return ans\n}}\n"
            f"func last_occ_c(_ nums: [Int], _ target: Int) -> Int {{\n"
            f"    var lo = 0, hi = nums.count - 1, ans = -1\n"
            f"    while lo <= hi {{\n"
            f"        let mid = lo + (hi - lo) / 2\n"
            f"        if nums[mid] == target {{ ans = mid; lo = mid + 1 }}\n"
            f"        else if nums[mid] < target {{ lo = mid + 1 }} else {{ hi = mid - 1 }}\n"
            f"    }}\n"
            f"    return ans\n}}\n"
            f"func count_occurrences(_ nums: [Int], _ target: Int) -> Int {{\n"
            f"    let f = first_occ_c(nums, target)\n"
            f"    if f == -1 {{ return 0{a} }}\n"
            f"    let l = last_occ_c(nums, target)\n"
            f"    return (l - f + 1){a}\n}}\n")


def _search_insert_position(wrong):
    a = " + 1" if wrong else ""
    return (f"func search_insert(_ nums: [Int], _ target: Int) -> Int {{\n"
            f"    var lo = 0, hi = nums.count\n"
            f"    while lo < hi {{\n"
            f"        let mid = lo + (hi - lo) / 2\n"
            f"        if nums[mid] < target {{ lo = mid + 1 }} else {{ hi = mid }}\n"
            f"    }}\n"
            f"    return lo{a}\n}}\n")


def _rotated_binary_search(wrong):
    a = " + 1" if wrong else ""
    return (f"func search(_ nums: [Int], _ target: Int) -> Int {{\n"
            f"    var lo = 0, hi = nums.count - 1\n"
            f"    while lo <= hi {{\n"
            f"        let mid = lo + (hi - lo) / 2\n"
            f"        if nums[mid] == target {{ return mid{a} }}\n"
            f"        if nums[lo] <= nums[mid] {{\n"
            f"            if nums[lo] <= target && target < nums[mid] {{ hi = mid - 1 }} else {{ lo = mid + 1 }}\n"
            f"        }} else {{\n"
            f"            if nums[mid] < target && target <= nums[hi] {{ lo = mid + 1 }} else {{ hi = mid - 1 }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return -1\n}}\n")


def _find_minimum_rotated_sorted_array(wrong):
    a = " + 1" if wrong else ""
    return (f"func find_min(_ nums: [Int]) -> Int {{\n"
            f"    var lo = 0, hi = nums.count - 1\n"
            f"    while lo < hi {{\n"
            f"        let mid = lo + (hi - lo) / 2\n"
            f"        if nums[mid] > nums[hi] {{ lo = mid + 1 }} else {{ hi = mid }}\n"
            f"    }}\n"
            f"    return nums[lo]{a}\n}}\n")


def _ternary_search(wrong):
    a = " + 1" if wrong else ""
    return (f"func ternary_search(_ nums: [Int], _ target: Int) -> Int {{\n"
            f"    var lo = 0, hi = nums.count - 1\n"
            f"    while lo <= hi {{\n"
            f"        let third = (hi - lo) / 3\n"
            f"        let m1 = lo + third\n"
            f"        let m2 = hi - third\n"
            f"        if nums[m1] == target {{ return m1{a} }}\n"
            f"        if nums[m2] == target {{ return m2{a} }}\n"
            f"        if target < nums[m1] {{ hi = m1 - 1 }}\n"
            f"        else if target > nums[m2] {{ lo = m2 + 1 }}\n"
            f"        else {{ lo = m1 + 1; hi = m2 - 1 }}\n"
            f"    }}\n"
            f"    return -1\n}}\n")


def _jump_search(wrong):
    a = " + 1" if wrong else ""
    return (f"func jump_search(_ nums: [Int], _ target: Int) -> Int {{\n"
            f"    let n = nums.count\n"
            f"    if n == 0 {{ return -1 }}\n"
            f"    let step = Int(Double(n).squareRoot())\n"
            f"    var blockStart = 0\n"
            f"    var blockEnd = min(step, n) - 1\n"
            f"    while blockEnd < n && nums[blockEnd] < target {{\n"
            f"        blockStart = blockEnd + 1\n"
            f"        blockEnd = min(blockEnd + step, n - 1)\n"
            f"        if blockStart >= n {{ return -1 }}\n"
            f"    }}\n"
            f"    var i = blockStart\n"
            f"    while i < n && i <= blockEnd {{\n"
            f"        if nums[i] == target {{ return i{a} }}\n"
            f"        i += 1\n"
            f"    }}\n"
            f"    return -1\n}}\n")


def _exponential_search(wrong):
    a = " + 1" if wrong else ""
    return (f"func exponential_search(_ nums: [Int], _ target: Int) -> Int {{\n"
            f"    let n = nums.count\n"
            f"    if n == 0 {{ return -1 }}\n"
            f"    if nums[0] == target {{ return 0{a} }}\n"
            f"    var i = 1\n"
            f"    while i < n && nums[i] <= target {{ i *= 2 }}\n"
            f"    var lo = i / 2, hi = min(i, n - 1)\n"
            f"    while lo <= hi {{\n"
            f"        let mid = lo + (hi - lo) / 2\n"
            f"        if nums[mid] == target {{ return mid{a} }}\n"
            f"        if nums[mid] < target {{ lo = mid + 1 }} else {{ hi = mid - 1 }}\n"
            f"    }}\n"
            f"    return -1\n}}\n")


def _interpolation_search(wrong):
    a = " + 1" if wrong else ""
    return (f"func interpolation_search(_ nums: [Int], _ target: Int) -> Int {{\n"
            f"    var lo = 0, hi = nums.count - 1\n"
            f"    while lo <= hi && target >= nums[lo] && target <= nums[hi] {{\n"
            f"        if nums[hi] == nums[lo] {{\n"
            f"            if nums[lo] == target {{ return lo{a} }}\n"
            f"            return -1\n"
            f"        }}\n"
            f"        let pos = lo + ((target - nums[lo]) * (hi - lo)) / (nums[hi] - nums[lo])\n"
            f"        if pos < lo || pos > hi {{ return -1 }}\n"
            f"        if nums[pos] == target {{ return pos{a} }}\n"
            f"        if nums[pos] < target {{ lo = pos + 1 }} else {{ hi = pos - 1 }}\n"
            f"    }}\n"
            f"    return -1\n}}\n")


def _fibonacci_search(wrong):
    a = " + 1" if wrong else ""
    return (f"func fibonacci_search(_ nums: [Int], _ target: Int) -> Int {{\n"
            f"    let n = nums.count\n"
            f"    if n == 0 {{ return -1 }}\n"
            f"    var fib2 = 0, fib1 = 1\n"
            f"    var fibM = fib2 + fib1\n"
            f"    while fibM < n {{ fib2 = fib1; fib1 = fibM; fibM = fib2 + fib1 }}\n"
            f"    var offset = -1\n"
            f"    while fibM > 1 {{\n"
            f"        let i = min(offset + fib2, n - 1)\n"
            f"        if nums[i] < target {{ fibM = fib1; fib1 = fib2; fib2 = fibM - fib1; offset = i }}\n"
            f"        else if nums[i] > target {{ fibM = fib2; fib1 = fib1 - fib2; fib2 = fibM - fib1 }}\n"
            f"        else {{ return i{a} }}\n"
            f"    }}\n"
            f"    if fib1 == 1 && offset + 1 < n && nums[offset + 1] == target {{ return (offset + 1){a} }}\n"
            f"    return -1\n}}\n")


def _bitonic_peak_index(wrong):
    a = " + 1" if wrong else ""
    return (f"func peak_index(_ nums: [Int]) -> Int {{\n"
            f"    var lo = 0, hi = nums.count - 1\n"
            f"    while lo < hi {{\n"
            f"        let mid = lo + (hi - lo) / 2\n"
            f"        if nums[mid] < nums[mid + 1] {{ lo = mid + 1 }} else {{ hi = mid }}\n"
            f"    }}\n"
            f"    return lo{a}\n}}\n")


_BUILDERS = {
    "bitonic-sort": _bitonic_sort,
    "bucket-sort": _bucket_sort,
    "cocktail-sort": _cocktail_sort,
    "comb-sort": _comb_sort,
    "counting-sort": _counting_sort,
    "cycle-sort": _cycle_sort,
    "gnome-sort": _gnome_sort,
    "heap-sort": _heap_sort,
    "insertion-sort": _insertion_sort,
    "merge-sort": _merge_sort_b,
    "odd-even-sort": _odd_even_sort,
    "pancake-sort": _pancake_sort,
    "patience-sort": _patience_sort,
    "quick-sort": _quick_sort_b,
    "radix-sort": _radix_sort,
    "selection-sort": _selection_sort,
    "shell-sort": _shell_sort,
    "stooge-sort": _stooge_sort,
    "strand-sort": _strand_sort,
    "tim-sort": _tim_sort,
    "gcd-euclidean": _gcd_euclidean,
    "collatz": _collatz,
    "hamming-distance": _hamming_distance,
    "number-of-1-bits": _number_of_1_bits,
    "power-of-two": _power_of_two,
    "reverse-bits": _reverse_bits,
    "integer-square-root": _integer_square_root,
    "modular-exponentiation": _modular_exponentiation,
    "number-of-divisors": _number_of_divisors,
    "sieve-of-eratosthenes": _sieve_of_eratosthenes,
    "euler-phi-sieve": _euler_phi_sieve,
    "euler-totient": _euler_totient,
    "lucas-theorem": _lucas_theorem,
    "miller-rabin": _miller_rabin,
    "linear-search": _linear_search,
    "binary-search": _binary_search_b,
    "first-occurrence": _first_occurrence,
    "last-occurrence": _last_occurrence,
    "count-occurrences-sorted": _count_occurrences_sorted,
    "search-insert-position": _search_insert_position,
    "rotated-binary-search": _rotated_binary_search,
    "find-minimum-rotated-sorted-array": _find_minimum_rotated_sorted_array,
    "ternary-search": _ternary_search,
    "jump-search": _jump_search,
    "exponential-search": _exponential_search,
    "interpolation-search": _interpolation_search,
    "fibonacci-search": _fibonacci_search,
    "bitonic-peak-index": _bitonic_peak_index,
}


def _maybe_json(v):
    return json.loads(v) if isinstance(v, str) else v


def load_problem(con, pid):
    row = con.execute("SELECT function_contract, test_suite_version FROM problems WHERE id=?", (pid,)).fetchone()
    contract = FunctionContract.from_dict(json.loads(row["function_contract"]))
    cur = con.execute(
        "SELECT id, function_args, function_expected, is_hidden, \"order\" FROM test_cases "
        "WHERE problem_id=? ORDER BY \"order\"", (pid,)
    )
    cases = []
    for r in cur.fetchall():
        args = _maybe_json(r["function_args"])
        expected = _maybe_json(r["function_expected"])
        cases.append(FunctionCase(id=r["id"], arguments=args, expected=expected, has_expected=True,
                                   is_hidden=bool(r["is_hidden"]), order=r["order"]))
    return contract, cases, row["test_suite_version"]


async def verify_one(pid, contract, cases, build):
    t0 = time.monotonic()
    correct_result = await evaluate_function(build(False), LANG, contract, cases)
    n_pass = sum(1 for r in correct_result.case_results if r.passed)
    if n_pass != len(cases):
        sample_fail = next((r for r in correct_result.case_results if not r.passed), None)
        return {"pid": pid, "outcome": "reference_failed",
                "detail": f"{n_pass}/{len(cases)} verdict={correct_result.verdict} "
                          f"compile={(correct_result.compile_output or '')[:200]} "
                          f"stderr={(sample_fail.stderr if sample_fail else '')[:200]} "
                          f"actual={(sample_fail.actual_return if sample_fail else '')!r} "
                          f"expected={(sample_fail.expected_return if sample_fail else '')!r}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    wrong_result = await evaluate_function(build(True), LANG, contract, cases)
    n_wrong_pass = sum(1 for r in wrong_result.case_results if r.passed)
    if n_wrong_pass >= len(cases):
        return {"pid": pid, "outcome": "corpus_weakness",
                "detail": f"corrupted solution still passed all {len(cases)}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    return {"pid": pid, "outcome": "verified",
            "detail": f"{n_pass}/{len(cases)} correct, wrong rejected on {len(cases) - n_wrong_pass}/{len(cases)}",
            "duration_ms": (time.monotonic() - t0) * 1000}


async def main():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ledger.ensure_schema(con)
    results = []
    skipped = 0
    for pid, build in _BUILDERS.items():
        contract, cases, tsv = load_problem(con, pid)
        if ledger.already_verified(con, pid, LANG, "function", test_suite_version=tsv):
            skipped += 1
            continue
        r = await verify_one(pid, contract, cases, build)
        results.append(r)
        status = "PASS" if r["outcome"] == "verified" else "FAIL"
        print(f"[{status}] {pid:40s} {r['outcome']:18s} {r['detail'][:160]}", flush=True)
        if r["outcome"] == "verified":
            ledger.record_cell(con, problem_id=pid, language=LANG, mode="function",
                verification_level=ledger.LEVEL_VERIFIED, status="pass",
                adapter_version="swift-function-port-v1", test_suite_version=tsv,
                duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped(already-verified): {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
