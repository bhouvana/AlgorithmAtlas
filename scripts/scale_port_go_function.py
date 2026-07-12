"""Ports Go (Function Mode) solutions for the ~173 problems missing Go
coverage. Single-language variant of the scale_mega_cluster*.py pattern.

Go calling convention (see GoFunctionAdapter in compiled_adapters.py):
  - plain top-level `func name(params) returnType { ... }`, no class wrapper
  - tree params/returns use `*TreeNode` with `.Val`/`.Left`/`.Right` fields;
    the harness auto-injects the TreeNode struct unless user code defines
    "type TreeNode struct" itself (we never define it -- let the harness).
  - "linked list" problems in this corpus are actually plain int arrays
    (function_contract uses `array<integer>`, not a real node type).
  - only these packages are auto-imported when referenced by substring:
    sort, strconv, strings, math, unicode, container/heap, container/list,
    bytes, errors. fmt/encoding/json/io/os are always available.
  - Go Function Mode has NO tuple support -> min-stack-simulation is a
    documented architectural gap (same as C), skipped.
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
LANG = "go"

_BUILDERS = {}


def register(pid):
    def deco(fn):
        _BUILDERS[pid] = fn
        return fn
    return deco


# ═════════════════════════════════════════════════════════════════════════
# Batch 1: simple array / math problems
# ═════════════════════════════════════════════════════════════════════════

@register("remove-nth-from-end")
def _b_remove_nth_from_end(wrong):
    a = ".map(x=>x+1)" if False else ""
    extra = "\n\tfor i := range out { out[i]++ }" if wrong else ""
    return (
        "func remove_nth_from_end(values []int, k int) []int {\n"
        "\tn := len(values)\n\tidx := n - k\n"
        "\tout := []int{}\n"
        "\tfor i := 0; i < n; i++ {\n\t\tif i != idx { out = append(out, values[i]) }\n\t}\n"
        f"{extra}\n"
        "\treturn out\n}\n"
    )


@register("activity-selection")
def _b_activity_selection(wrong):
    a = " + 1" if wrong else ""
    return (
        "func max_activities(starts []int, ends []int) int {\n"
        "\tn := len(starts)\n"
        "\tidx := make([]int, n)\n"
        "\tfor i := range idx { idx[i] = i }\n"
        "\tsort.Slice(idx, func(a, b int) bool { return ends[idx[a]] < ends[idx[b]] })\n"
        "\tcount := 0\n\tlastEnd := -1 << 62\n"
        "\tfor _, i := range idx {\n"
        "\t\tif starts[i] >= lastEnd { count++; lastEnd = ends[i] }\n\t}\n"
        f"\treturn count{a}\n}}\n"
    )


@register("best-time-to-buy-sell-stock")
def _b_best_time_buy_sell(wrong):
    a = " + 1" if wrong else ""
    return (
        "func max_profit(prices []int) int {\n"
        "\tif len(prices) == 0 { return 0 }\n"
        "\tminPrice := prices[0]\n\tbest := 0\n"
        "\tfor _, p := range prices {\n"
        "\t\tif p < minPrice { minPrice = p }\n"
        "\t\tif p-minPrice > best { best = p - minPrice }\n\t}\n"
        f"\treturn best{a}\n}}\n"
    )


@register("best-time-to-buy-sell-stock-ii")
def _b_best_time_buy_sell_ii(wrong):
    a = " + 1" if wrong else ""
    return (
        "func max_profit(prices []int) int {\n"
        "\ttotal := 0\n"
        "\tfor i := 1; i < len(prices); i++ {\n"
        "\t\tif prices[i] > prices[i-1] { total += prices[i] - prices[i-1] }\n\t}\n"
        f"\treturn total{a}\n}}\n"
    )


@register("bitonic-peak-index")
def _b_bitonic_peak_index(wrong):
    a = " + 1" if wrong else ""
    return (
        "func peak_index(nums []int) int {\n"
        "\tlo, hi := 0, len(nums)-1\n"
        "\tfor lo < hi {\n"
        "\t\tmid := (lo + hi) / 2\n"
        "\t\tif nums[mid] < nums[mid+1] { lo = mid + 1 } else { hi = mid }\n\t}\n"
        f"\treturn lo{a}\n}}\n"
    )


@register("catalan-number")
def _b_catalan_number(wrong):
    a = " + 1" if wrong else ""
    return (
        "func catalan_number(n int) int {\n"
        "\tdp := make([]int64, n+1)\n\tdp[0] = 1\n"
        "\tfor i := 1; i <= n; i++ {\n"
        "\t\tvar s int64 = 0\n"
        "\t\tfor j := 0; j < i; j++ { s += dp[j] * dp[i-1-j] }\n"
        "\t\tdp[i] = s\n\t}\n"
        f"\treturn int(dp[n]){a}\n}}\n"
    )


@register("collatz")
def _b_collatz(wrong):
    a = " + 1" if wrong else ""
    return (
        "func collatz(n int) int {\n"
        "\tsteps := 0\n\tx := int64(n)\n"
        "\tfor x != 1 {\n"
        "\t\tif x%2 == 0 { x = x / 2 } else { x = 3*x + 1 }\n"
        "\t\tsteps++\n\t}\n"
        f"\treturn steps{a}\n}}\n"
    )


@register("container-with-most-water")
def _b_container_with_most_water(wrong):
    a = " + 1" if wrong else ""
    return (
        "func max_area(heights []int) int {\n"
        "\tl, r := 0, len(heights)-1\n\tbest := 0\n"
        "\tfor l < r {\n"
        "\t\th := heights[l]\n\t\tif heights[r] < h { h = heights[r] }\n"
        "\t\tarea := h * (r - l)\n\t\tif area > best { best = area }\n"
        "\t\tif heights[l] < heights[r] { l++ } else { r-- }\n\t}\n"
        f"\treturn best{a}\n}}\n"
    )


@register("count-occurrences-sorted")
def _b_count_occurrences_sorted(wrong):
    a = " + 1" if wrong else ""
    return (
        "func count_occurrences(nums []int, target int) int {\n"
        "\tlo := sort.SearchInts(nums, target)\n"
        "\thi := sort.SearchInts(nums, target+1)\n"
        f"\treturn (hi - lo){a}\n}}\n"
    )


@register("counting-bits")
def _b_counting_bits(wrong):
    extra = "\n\tif len(dp) > 0 { dp[len(dp)-1]++ }" if wrong else ""
    return (
        "func count_bits(n int) []int {\n"
        "\tdp := make([]int, n+1)\n"
        "\tfor i := 1; i <= n; i++ { dp[i] = dp[i>>1] + (i & 1) }\n"
        f"{extra}\n"
        "\treturn dp\n}\n"
    )


@register("counting-inversions")
def _b_counting_inversions(wrong):
    a = " + 1" if wrong else ""
    return (
        "func count_inversions(nums []int) int {\n"
        "\tn := len(nums)\n\tcount := 0\n"
        "\tfor i := 0; i < n; i++ {\n"
        "\t\tfor j := i + 1; j < n; j++ {\n"
        "\t\t\tif nums[i] > nums[j] { count++ }\n\t\t}\n\t}\n"
        f"\treturn count{a}\n}}\n"
    )


@register("daily-temperatures")
def _b_daily_temperatures(wrong):
    extra = "\n\tif len(res) > 0 { res[0]++ }" if wrong else ""
    return (
        "func daily_temperatures(temps []int) []int {\n"
        "\tn := len(temps)\n\tres := make([]int, n)\n"
        "\tstack := []int{}\n"
        "\tfor i := 0; i < n; i++ {\n"
        "\t\tfor len(stack) > 0 && temps[stack[len(stack)-1]] < temps[i] {\n"
        "\t\t\tj := stack[len(stack)-1]\n\t\t\tstack = stack[:len(stack)-1]\n"
        "\t\t\tres[j] = i - j\n\t\t}\n"
        "\t\tstack = append(stack, i)\n\t}\n"
        f"{extra}\n"
        "\treturn res\n}\n"
    )


@register("evaluate-reverse-polish-notation")
def _b_evaluate_rpn(wrong):
    a = " + 1" if wrong else ""
    return (
        "func eval_rpn(tokens []string) int {\n"
        "\tstack := []int{}\n"
        "\tfor _, t := range tokens {\n"
        "\t\tif t == \"+\" || t == \"-\" || t == \"*\" || t == \"/\" {\n"
        "\t\t\tb := stack[len(stack)-1]\n\t\t\ta := stack[len(stack)-2]\n"
        "\t\t\tstack = stack[:len(stack)-2]\n"
        "\t\t\tvar r int\n"
        "\t\t\tswitch t {\n"
        "\t\t\tcase \"+\": r = a + b\n"
        "\t\t\tcase \"-\": r = a - b\n"
        "\t\t\tcase \"*\": r = a * b\n"
        "\t\t\tdefault: r = a / b\n"
        "\t\t\t}\n"
        "\t\t\tstack = append(stack, r)\n"
        "\t\t} else {\n"
        "\t\t\tv, _ := strconv.Atoi(t)\n\t\t\tstack = append(stack, v)\n"
        "\t\t}\n\t}\n"
        f"\treturn stack[len(stack)-1]{a}\n}}\n"
    )


@register("fast-power")
def _b_fast_power(wrong):
    a = " + 1" if wrong else ""
    return (
        "func fast_power(base int, exp int) int {\n"
        "\tvar result int64 = 1\n\tvar b int64 = int64(base)\n\te := exp\n"
        "\tfor e > 0 {\n"
        "\t\tif e&1 == 1 { result *= b }\n"
        "\t\tb *= b\n\t\te >>= 1\n\t}\n"
        f"\treturn int(result){a}\n}}\n"
    )


@register("fibonacci-dp")
def _b_fibonacci_dp(wrong):
    a = " + 1" if wrong else ""
    return (
        "func fib(n int) int {\n"
        "\tif n < 2 { return n" + a + " }\n"
        "\ta, b := 0, 1\n"
        "\tfor i := 2; i <= n; i++ { a, b = b, a+b }\n"
        f"\treturn b{a}\n}}\n"
    )


@register("find-duplicate-number")
def _b_find_duplicate_number(wrong):
    a = " + 1" if wrong else ""
    return (
        "func find_duplicate(nums []int) int {\n"
        "\tslow, fast := nums[0], nums[nums[0]]\n"
        "\tfor slow != fast { slow = nums[slow]; fast = nums[nums[fast]] }\n"
        "\tslow2 := 0\n"
        "\tfor slow2 != slow { slow2 = nums[slow2]; slow = nums[slow] }\n"
        f"\treturn slow2{a}\n}}\n"
    )


@register("find-minimum-rotated-sorted-array")
def _b_find_minimum_rotated(wrong):
    a = " + 1" if wrong else ""
    return (
        "func find_min(nums []int) int {\n"
        "\tlo, hi := 0, len(nums)-1\n"
        "\tfor lo < hi {\n"
        "\t\tmid := (lo + hi) / 2\n"
        "\t\tif nums[mid] > nums[hi] { lo = mid + 1 } else { hi = mid }\n\t}\n"
        f"\treturn nums[lo]{a}\n}}\n"
    )


@register("first-occurrence")
def _b_first_occurrence(wrong):
    a = " + 1" if wrong else ""
    return (
        "func first_occurrence(nums []int, target int) int {\n"
        "\tlo, hi := 0, len(nums)-1\n\tres := -1\n"
        "\tfor lo <= hi {\n"
        "\t\tmid := (lo + hi) / 2\n"
        "\t\tif nums[mid] == target { res = mid; hi = mid - 1 } else if nums[mid] < target { lo = mid + 1 } else { hi = mid - 1 }\n\t}\n"
        f"\treturn res{a}\n}}\n"
    )


@register("last-occurrence")
def _b_last_occurrence(wrong):
    a = " + 1" if wrong else ""
    return (
        "func last_occurrence(nums []int, target int) int {\n"
        "\tlo, hi := 0, len(nums)-1\n\tres := -1\n"
        "\tfor lo <= hi {\n"
        "\t\tmid := (lo + hi) / 2\n"
        "\t\tif nums[mid] == target { res = mid; lo = mid + 1 } else if nums[mid] < target { lo = mid + 1 } else { hi = mid - 1 }\n\t}\n"
        f"\treturn res{a}\n}}\n"
    )


@register("linear-search")
def _b_linear_search(wrong):
    a = " + 1" if wrong else ""
    return (
        "func linear_search(nums []int, target int) int {\n"
        "\tfor i, v := range nums { if v == target { return i" + a + " } }\n"
        f"\treturn -1{a}\n}}\n"
    )


@register("gas-station")
def _b_gas_station(wrong):
    a = " + 1" if wrong else ""
    return (
        "func can_complete_circuit(gas []int, cost []int) int {\n"
        "\ttotal, tank, start := 0, 0, 0\n"
        "\tfor i := 0; i < len(gas); i++ {\n"
        "\t\tdiff := gas[i] - cost[i]\n\t\ttotal += diff\n\t\ttank += diff\n"
        "\t\tif tank < 0 { start = i + 1; tank = 0 }\n\t}\n"
        "\tif total < 0 { return -1" + a + " }\n"
        f"\treturn start{a}\n}}\n"
    )


@register("hamming-distance")
def _b_hamming_distance(wrong):
    a = " + 1" if wrong else ""
    return (
        "func hamming_distance(x int, y int) int {\n"
        "\tv := x ^ y\n\tcount := 0\n"
        "\tfor v != 0 { count += v & 1; v >>= 1 }\n"
        f"\treturn count{a}\n}}\n"
    )


@register("integer-square-root")
def _b_integer_square_root(wrong):
    a = " + 1" if wrong else ""
    return (
        "func my_sqrt(n int) int {\n"
        "\tif n < 2 { return n" + a + " }\n"
        "\tlo, hi := 1, n\n"
        "\tfor lo <= hi {\n"
        "\t\tmid := lo + (hi-lo)/2\n"
        "\t\tif mid <= n/mid { lo = mid + 1 } else { hi = mid - 1 }\n\t}\n"
        f"\treturn hi{a}\n}}\n"
    )


@register("intersection-of-two-arrays")
def _b_intersection_of_two_arrays(wrong):
    a = ", 999999" if wrong else ""
    return (
        "func intersection(nums1 []int, nums2 []int) []int {\n"
        "\tset1 := map[int]bool{}\n\tfor _, v := range nums1 { set1[v] = true }\n"
        "\tseen := map[int]bool{}\n\tres := []int{}\n"
        "\tfor _, v := range nums2 {\n"
        "\t\tif set1[v] && !seen[v] { res = append(res, v); seen[v] = true }\n\t}\n"
        "\tsort.Ints(res)\n"
        f"\treturn append(res{a})\n}}\n"
    )


@register("jump-game")
def _b_jump_game(wrong):
    neg = "!" if wrong else ""
    return (
        "func can_jump(nums []int) bool {\n"
        "\treach := 0\n"
        "\tfor i := 0; i < len(nums); i++ {\n"
        "\t\tif i > reach { return " + neg + "true }\n"
        "\t\tif i+nums[i] > reach { reach = i + nums[i] }\n\t}\n"
        f"\treturn {neg}true\n}}\n"
    )


@register("jump-game-ii-min-jumps")
def _b_jump_game_ii(wrong):
    a = " + 1" if wrong else ""
    return (
        "func jump(nums []int) int {\n"
        "\tjumps, curEnd, farthest := 0, 0, 0\n"
        "\tfor i := 0; i < len(nums)-1; i++ {\n"
        "\t\tif i+nums[i] > farthest { farthest = i + nums[i] }\n"
        "\t\tif i == curEnd { jumps++; curEnd = farthest }\n\t}\n"
        f"\treturn jumps{a}\n}}\n"
    )


@register("karatsuba")
def _b_karatsuba(wrong):
    a = " + 1" if wrong else ""
    return (
        "func karatsuba(a int, b int) int {\n"
        f"\treturn a*b{a}\n}}\n"
    )


@register("kth-largest-element")
def _b_kth_largest_element(wrong):
    a = " + 1" if wrong else ""
    return (
        "func kth_largest(nums []int, k int) int {\n"
        "\tcp := append([]int{}, nums...)\n"
        "\tsort.Sort(sort.Reverse(sort.IntSlice(cp)))\n"
        f"\treturn cp[k-1]{a}\n}}\n"
    )


@register("median-of-medians")
def _b_median_of_medians(wrong):
    a = " + 1" if wrong else ""
    return (
        "func kth_smallest(nums []int, k int) int {\n"
        "\tcp := append([]int{}, nums...)\n"
        "\tsort.Ints(cp)\n"
        f"\treturn cp[k-1]{a}\n}}\n"
    )


@register("longest-consecutive-sequence")
def _b_longest_consecutive_sequence(wrong):
    a = " + 1" if wrong else ""
    return (
        "func longest_consecutive(nums []int) int {\n"
        "\tset := map[int]bool{}\n\tfor _, v := range nums { set[v] = true }\n"
        "\tbest := 0\n"
        "\tfor v := range set {\n"
        "\t\tif !set[v-1] {\n"
        "\t\t\tlen_ := 1\n\t\t\tcur := v\n"
        "\t\t\tfor set[cur+1] { cur++; len_++ }\n"
        "\t\t\tif len_ > best { best = len_ }\n\t\t}\n\t}\n"
        f"\treturn best{a}\n}}\n"
    )


@register("majority-element")
def _b_majority_element(wrong):
    a = " + 1" if wrong else ""
    return (
        "func majority_element(nums []int) int {\n"
        "\tcount, cand := 0, 0\n"
        "\tfor _, v := range nums {\n"
        "\t\tif count == 0 { cand = v }\n"
        "\t\tif v == cand { count++ } else { count-- }\n\t}\n"
        f"\treturn cand{a}\n}}\n"
    )


@register("majority-element-ii")
def _b_majority_element_ii(wrong):
    extra = "\n\tres = append(res, 999999)" if wrong else ""
    return (
        "func majority_element_ii(nums []int) []int {\n"
        "\tvar cand1, cand2 int\n\tvar cnt1, cnt2 int\n\tcand1, cand2 = 0, 1\n"
        "\tfor _, v := range nums {\n"
        "\t\tif cand1 == v { cnt1++ } else if cand2 == v { cnt2++ } else if cnt1 == 0 { cand1 = v; cnt1 = 1 } else if cnt2 == 0 { cand2 = v; cnt2 = 1 } else { cnt1--; cnt2-- }\n\t}\n"
        "\tcnt1, cnt2 = 0, 0\n"
        "\tfor _, v := range nums {\n"
        "\t\tif v == cand1 { cnt1++ } else if v == cand2 { cnt2++ }\n\t}\n"
        "\tres := []int{}\n\tn := len(nums)\n"
        "\tif cnt1 > n/3 { res = append(res, cand1) }\n"
        "\tif cnt2 > n/3 { res = append(res, cand2) }\n"
        "\tsort.Ints(res)\n"
        f"{extra}\n"
        "\treturn res\n}\n"
    )


@register("maximum-product-subarray")
def _b_maximum_product_subarray(wrong):
    a = " + 1" if wrong else ""
    return (
        "func max_product(nums []int) int {\n"
        "\tmaxP, minP, best := nums[0], nums[0], nums[0]\n"
        "\tfor i := 1; i < len(nums); i++ {\n"
        "\t\tv := nums[i]\n"
        "\t\tif v < 0 { maxP, minP = minP, maxP }\n"
        "\t\tif v > maxP*v { maxP = v } else { maxP = maxP * v }\n"
        "\t\tif v < minP*v { minP = v } else { minP = minP * v }\n"
        "\t\tif maxP > best { best = maxP }\n\t}\n"
        f"\treturn best{a}\n}}\n"
    )


@register("maximum-subarray-circular")
def _b_maximum_subarray_circular(wrong):
    a = " + 1" if wrong else ""
    return (
        "func max_subarray_sum_circular(nums []int) int {\n"
        "\ttotal, curMax, best, curMin, worst := 0, 0, nums[0], 0, nums[0]\n"
        "\tfor _, v := range nums {\n"
        "\t\ttotal += v\n"
        "\t\tif curMax < 0 { curMax = v } else { curMax += v }\n"
        "\t\tif curMax > best { best = curMax }\n"
        "\t\tif curMin > 0 { curMin = v } else { curMin += v }\n"
        "\t\tif curMin < worst { worst = curMin }\n\t}\n"
        "\tif best < 0 { return best" + a + " }\n"
        "\tif total-worst > best { return (total - worst)" + a + " }\n"
        f"\treturn best{a}\n}}\n"
    )


@register("median-of-two-sorted-arrays")
def _b_median_of_two_sorted_arrays(wrong):
    a = " + 1.0" if wrong else ""
    return (
        "func find_median(nums1 []int, nums2 []int) float64 {\n"
        "\tmerged := append([]int{}, nums1...)\n\tmerged = append(merged, nums2...)\n"
        "\tsort.Ints(merged)\n\tn := len(merged)\n"
        "\tif n%2 == 1 { return float64(merged[n/2])" + a + " }\n"
        f"\treturn (float64(merged[n/2-1])+float64(merged[n/2]))/2.0{a}\n}}\n"
    )


@register("meeting-rooms")
def _b_meeting_rooms(wrong):
    a = " + 1" if wrong else ""
    return (
        "func min_meeting_rooms(starts []int, ends []int) int {\n"
        "\ts := append([]int{}, starts...)\n\te := append([]int{}, ends...)\n"
        "\tsort.Ints(s)\n\tsort.Ints(e)\n"
        "\ti, j, rooms, best := 0, 0, 0, 0\n"
        "\tfor i < len(s) {\n"
        "\t\tif s[i] < e[j] { rooms++; i++; if rooms > best { best = rooms } } else { rooms--; j++ }\n\t}\n"
        f"\treturn best{a}\n}}\n"
    )


@register("merge-sorted-arrays-inplace")
def _b_merge_sorted_arrays_inplace(wrong):
    extra = "\n\tres = append(res, 999999)" if wrong else ""
    return (
        "func merge_sorted(a []int, b []int) []int {\n"
        "\tres := make([]int, 0, len(a)+len(b))\n\ti, j := 0, 0\n"
        "\tfor i < len(a) && j < len(b) {\n"
        "\t\tif a[i] <= b[j] { res = append(res, a[i]); i++ } else { res = append(res, b[j]); j++ }\n\t}\n"
        "\tres = append(res, a[i:]...)\n\tres = append(res, b[j:]...)\n"
        f"{extra}\n"
        "\treturn res\n}\n"
    )


@register("merge-two-sorted-lists")
def _b_merge_two_sorted_lists(wrong):
    extra = "\n\tres = append(res, 999999)" if wrong else ""
    return (
        "func merge_two_lists(a []int, b []int) []int {\n"
        "\tres := make([]int, 0, len(a)+len(b))\n\ti, j := 0, 0\n"
        "\tfor i < len(a) && j < len(b) {\n"
        "\t\tif a[i] <= b[j] { res = append(res, a[i]); i++ } else { res = append(res, b[j]); j++ }\n\t}\n"
        "\tres = append(res, a[i:]...)\n\tres = append(res, b[j:]...)\n"
        f"{extra}\n"
        "\treturn res\n}\n"
    )


@register("middle-of-linked-list")
def _b_middle_of_linked_list(wrong):
    a = " + 1" if wrong else ""
    return (
        "func middle_node(values []int) int {\n"
        "\tslow, fast := 0, 0\n\tn := len(values)\n"
        "\tfor fast < n-1 && fast+1 < n {\n"
        "\t\tslow++\n\t\tfast += 2\n\t}\n"
        f"\treturn values[slow]{a}\n}}\n"
    )


@register("missing-number")
def _b_missing_number(wrong):
    a = " + 1" if wrong else ""
    return (
        "func missing_number(nums []int) int {\n"
        "\tn := len(nums)\n\texpected := n * (n + 1) / 2\n\tactual := 0\n"
        "\tfor _, v := range nums { actual += v }\n"
        f"\treturn (expected - actual){a}\n}}\n"
    )


@register("modular-exponentiation")
def _b_modular_exponentiation(wrong):
    a = " + 1" if wrong else ""
    return (
        "func modular_exponentiation(base int, exp int, mod int) int {\n"
        "\tvar result int64 = 1\n\tb := int64(base) % int64(mod)\n\te := exp\n\tm := int64(mod)\n"
        "\tif b < 0 { b += m }\n"
        "\tfor e > 0 {\n"
        "\t\tif e&1 == 1 { result = (result * b) % m }\n"
        "\t\tb = (b * b) % m\n\t\te >>= 1\n\t}\n"
        f"\treturn int(result){a}\n}}\n"
    )


@register("move-zeroes")
def _b_move_zeroes(wrong):
    extra = "\n\tif len(nums) > 0 { nums[0] = 999999 }" if wrong else ""
    return (
        "func move_zeroes(nums []int) []int {\n"
        "\tres := make([]int, len(nums))\n\tidx := 0\n"
        "\tfor _, v := range nums { if v != 0 { res[idx] = v; idx++ } }\n"
        f"{extra}\n"
        "\treturn res\n}\n"
    )


@register("next-greater-element")
def _b_next_greater_element(wrong):
    extra = "\n\tif len(res) > 0 { res[0]++ }" if wrong else ""
    return (
        "func next_greater_element(nums []int) []int {\n"
        "\tn := len(nums)\n\tres := make([]int, n)\n\tfor i := range res { res[i] = -1 }\n"
        "\tstack := []int{}\n"
        "\tfor i := 0; i < n; i++ {\n"
        "\t\tfor len(stack) > 0 && nums[stack[len(stack)-1]] < nums[i] {\n"
        "\t\t\tj := stack[len(stack)-1]\n\t\t\tstack = stack[:len(stack)-1]\n"
        "\t\t\tres[j] = nums[i]\n\t\t}\n"
        "\t\tstack = append(stack, i)\n\t}\n"
        f"{extra}\n"
        "\treturn res\n}\n"
    )


@register("number-of-1-bits")
def _b_number_of_1_bits(wrong):
    a = " + 1" if wrong else ""
    return (
        "func hamming_weight(n int) int {\n"
        "\tcount := 0\n\tv := uint32(n)\n"
        "\tfor v != 0 { count += int(v & 1); v >>= 1 }\n"
        f"\treturn count{a}\n}}\n"
    )


@register("number-of-divisors")
def _b_number_of_divisors(wrong):
    a = " + 1" if wrong else ""
    return (
        "func number_of_divisors(n int) int {\n"
        "\tcount := 0\n"
        "\tfor i := 1; i*i <= n; i++ {\n"
        "\t\tif n%i == 0 {\n\t\t\tcount++\n\t\t\tif i != n/i { count++ }\n\t\t}\n\t}\n"
        f"\treturn count{a}\n}}\n"
    )


@register("palindrome-linked-list")
def _b_palindrome_linked_list(wrong):
    neg = "!" if wrong else ""
    return (
        "func is_palindrome(values []int) bool {\n"
        "\ti, j := 0, len(values)-1\n"
        "\tfor i < j { if values[i] != values[j] { return " + neg + "false }\n\t\ti++\n\t\tj--\n\t}\n"
        f"\treturn {neg}true\n}}\n"
    )


@register("linked-list-cycle-detect")
def _b_linked_list_cycle_detect(wrong):
    neg = "!" if wrong else ""
    return (
        "func has_cycle(values []int, pos int) bool {\n"
        f"\treturn {neg}(pos >= 0 && pos < len(values))\n}}\n"
    )


@register("polynomial-multiplication")
def _b_polynomial_multiplication(wrong):
    extra = "\n\tif len(res) > 0 { res[0]++ }" if wrong else ""
    return (
        "func multiply_polynomials(a []int, b []int) []int {\n"
        "\tif len(a) == 0 || len(b) == 0 { return []int{} }\n"
        "\tres := make([]int, len(a)+len(b)-1)\n"
        "\tfor i, av := range a {\n\t\tfor j, bv := range b { res[i+j] += av * bv }\n\t}\n"
        f"{extra}\n"
        "\treturn res\n}\n"
    )


@register("power-of-two")
def _b_power_of_two(wrong):
    neg = "!" if wrong else ""
    return (
        "func is_power_of_two(n int) bool {\n"
        f"\treturn {neg}(n > 0 && (n&(n-1)) == 0)\n}}\n"
    )


@register("product-of-array-except-self")
def _b_product_of_array_except_self(wrong):
    extra = "\n\tif len(res) > 0 { res[0]++ }" if wrong else ""
    return (
        "func product_except_self(nums []int) []int {\n"
        "\tn := len(nums)\n\tres := make([]int, n)\n"
        "\tres[0] = 1\n"
        "\tfor i := 1; i < n; i++ { res[i] = res[i-1] * nums[i-1] }\n"
        "\tright := 1\n"
        "\tfor i := n - 1; i >= 0; i-- { res[i] *= right; right *= nums[i] }\n"
        f"{extra}\n"
        "\treturn res\n}\n"
    )


@register("reverse-bits")
def _b_reverse_bits(wrong):
    a = " + 1" if wrong else ""
    return (
        "func reverse_bits(n int) int {\n"
        "\tvar result uint32 = 0\n\tv := uint32(n)\n"
        "\tfor i := 0; i < 32; i++ {\n"
        "\t\tresult = (result << 1) | (v & 1)\n\t\tv >>= 1\n\t}\n"
        f"\treturn int(result){a}\n}}\n"
    )


@register("reverse-linked-list")
def _b_reverse_linked_list(wrong):
    extra = "\n\tif len(res) > 0 { res[0]++ }" if wrong else ""
    return (
        "func reverse_list(values []int) []int {\n"
        "\tn := len(values)\n\tres := make([]int, n)\n"
        "\tfor i, v := range values { res[n-1-i] = v }\n"
        f"{extra}\n"
        "\treturn res\n}\n"
    )


@register("rotate-image-90")
def _b_rotate_image_90(wrong):
    extra = "\n\tif len(res) > 0 && len(res[0]) > 0 { res[0][0]++ }" if wrong else ""
    return (
        "func rotate(matrix [][]int) [][]int {\n"
        "\tn := len(matrix)\n\tres := make([][]int, n)\n"
        "\tfor i := range res { res[i] = make([]int, n) }\n"
        "\tfor i := 0; i < n; i++ {\n\t\tfor j := 0; j < n; j++ { res[j][n-1-i] = matrix[i][j] }\n\t}\n"
        f"{extra}\n"
        "\treturn res\n}\n"
    )


@register("rotated-binary-search")
def _b_rotated_binary_search(wrong):
    a = " + 1" if wrong else ""
    return (
        "func search(nums []int, target int) int {\n"
        "\tlo, hi := 0, len(nums)-1\n"
        "\tfor lo <= hi {\n"
        "\t\tmid := (lo + hi) / 2\n"
        "\t\tif nums[mid] == target { return mid" + a + " }\n"
        "\t\tif nums[lo] <= nums[mid] {\n"
        "\t\t\tif nums[lo] <= target && target < nums[mid] { hi = mid - 1 } else { lo = mid + 1 }\n"
        "\t\t} else {\n"
        "\t\t\tif nums[mid] < target && target <= nums[hi] { lo = mid + 1 } else { hi = mid - 1 }\n"
        "\t\t}\n\t}\n"
        f"\treturn -1{a}\n}}\n"
    )


@register("search-2d-matrix")
def _b_search_2d_matrix(wrong):
    neg = "!" if wrong else ""
    return (
        "func search_matrix(matrix [][]int, target int) bool {\n"
        "\tif len(matrix) == 0 || len(matrix[0]) == 0 { return " + neg + "false }\n"
        "\trows, cols := len(matrix), len(matrix[0])\n"
        "\tr, c := 0, cols-1\n"
        "\tfor r < rows && c >= 0 {\n"
        "\t\tif matrix[r][c] == target { return " + neg + "true }\n"
        "\t\tif matrix[r][c] > target { c-- } else { r++ }\n\t}\n"
        f"\treturn {neg}false\n}}\n"
    )


@register("search-insert-position")
def _b_search_insert_position(wrong):
    a = " + 1" if wrong else ""
    return (
        "func search_insert(nums []int, target int) int {\n"
        "\tlo, hi := 0, len(nums)\n"
        "\tfor lo < hi {\n"
        "\t\tmid := (lo + hi) / 2\n"
        "\t\tif nums[mid] < target { lo = mid + 1 } else { hi = mid }\n\t}\n"
        f"\treturn lo{a}\n}}\n"
    )


@register("set-matrix-zeroes")
def _b_set_matrix_zeroes(wrong):
    extra = "\n\tif len(res) > 0 && len(res[0]) > 0 { res[0][0] = 999999 }" if wrong else ""
    return (
        "func set_zeroes(matrix [][]int) [][]int {\n"
        "\trows, cols := len(matrix), len(matrix[0])\n"
        "\tres := make([][]int, rows)\n\tfor i := range res { res[i] = append([]int{}, matrix[i]...) }\n"
        "\tzr := map[int]bool{}\n\tzc := map[int]bool{}\n"
        "\tfor i := 0; i < rows; i++ {\n\t\tfor j := 0; j < cols; j++ { if matrix[i][j] == 0 { zr[i] = true; zc[j] = true } }\n\t}\n"
        "\tfor i := 0; i < rows; i++ {\n\t\tfor j := 0; j < cols; j++ { if zr[i] || zc[j] { res[i][j] = 0 } }\n\t}\n"
        f"{extra}\n"
        "\treturn res\n}\n"
    )


@register("single-number")
def _b_single_number(wrong):
    a = " + 1" if wrong else ""
    return (
        "func single_number(nums []int) int {\n"
        "\tres := 0\n\tfor _, v := range nums { res ^= v }\n"
        f"\treturn res{a}\n}}\n"
    )


@register("single-number-ii")
def _b_single_number_ii(wrong):
    a = " + 1" if wrong else ""
    return (
        "func single_number(nums []int) int {\n"
        "\tones, twos := 0, 0\n"
        "\tfor _, x := range nums { ones = (ones ^ x) &^ twos; twos = (twos ^ x) &^ ones }\n"
        f"\treturn ones{a}\n}}\n"
    )


@register("sliding-window-maximum")
def _b_sliding_window_maximum(wrong):
    extra = "\n\tif len(res) > 0 { res[0]++ }" if wrong else ""
    return (
        "func max_sliding_window(nums []int, k int) []int {\n"
        "\tres := []int{}\n\tdeque := []int{}\n"
        "\tfor i, v := range nums {\n"
        "\t\tfor len(deque) > 0 && nums[deque[len(deque)-1]] <= v { deque = deque[:len(deque)-1] }\n"
        "\t\tdeque = append(deque, i)\n"
        "\t\tif deque[0] <= i-k { deque = deque[1:] }\n"
        "\t\tif i >= k-1 { res = append(res, nums[deque[0]]) }\n\t}\n"
        f"{extra}\n"
        "\treturn res\n}\n"
    )


@register("spiral-matrix-traversal")
def _b_spiral_matrix_traversal(wrong):
    extra = "\n\tif len(res) > 0 { res[0]++ }" if wrong else ""
    return (
        "func spiral_order(matrix [][]int) []int {\n"
        "\tres := []int{}\n\tif len(matrix) == 0 { return res }\n"
        "\ttop, bottom := 0, len(matrix)-1\n\tleft, right := 0, len(matrix[0])-1\n"
        "\tfor top <= bottom && left <= right {\n"
        "\t\tfor j := left; j <= right; j++ { res = append(res, matrix[top][j]) }\n\t\ttop++\n"
        "\t\tfor i := top; i <= bottom; i++ { res = append(res, matrix[i][right]) }\n\t\tright--\n"
        "\t\tif top <= bottom {\n\t\t\tfor j := right; j >= left; j-- { res = append(res, matrix[bottom][j]) }\n\t\t\tbottom--\n\t\t}\n"
        "\t\tif left <= right {\n\t\t\tfor i := bottom; i >= top; i-- { res = append(res, matrix[i][left]) }\n\t\t\tleft++\n\t\t}\n\t}\n"
        f"{extra}\n"
        "\treturn res\n}\n"
    )


@register("subarray-product-less-than-k")
def _b_subarray_product_less_than_k(wrong):
    a = " + 1" if wrong else ""
    return (
        "func num_subarrays_product_less_than_k(nums []int, k int) int {\n"
        "\tif k <= 1 { return 0" + a + " }\n"
        "\tprod, left, count := 1, 0, 0\n"
        "\tfor right := 0; right < len(nums); right++ {\n"
        "\t\tprod *= nums[right]\n"
        "\t\tfor prod >= k { prod /= nums[left]; left++ }\n"
        "\t\tcount += right - left + 1\n\t}\n"
        f"\treturn count{a}\n}}\n"
    )


@register("subarray-sum-equals-k")
def _b_subarray_sum_equals_k(wrong):
    a = " + 1" if wrong else ""
    return (
        "func subarray_sum(nums []int, k int) int {\n"
        "\tfreq := map[int]int{0: 1}\n\tsum, count := 0, 0\n"
        "\tfor _, v := range nums {\n"
        "\t\tsum += v\n"
        "\t\tcount += freq[sum-k]\n"
        "\t\tfreq[sum]++\n\t}\n"
        f"\treturn count{a}\n}}\n"
    )


@register("subarray-sums-divisible-by-k")
def _b_subarray_sums_divisible_by_k(wrong):
    a = " + 1" if wrong else ""
    return (
        "func subarrays_div_by_k(nums []int, k int) int {\n"
        "\tfreq := make([]int, k)\n\tfreq[0] = 1\n\tsum, count := 0, 0\n"
        "\tfor _, v := range nums {\n"
        "\t\tsum += v\n\t\tr := ((sum % k) + k) % k\n"
        "\t\tcount += freq[r]\n\t\tfreq[r]++\n\t}\n"
        f"\treturn count{a}\n}}\n"
    )


@register("three-sum-count-triplets")
def _b_three_sum_count_triplets(wrong):
    a = " + 1" if wrong else ""
    return (
        "func three_sum_count(nums []int) int {\n"
        "\tcp := append([]int{}, nums...)\n\tsort.Ints(cp)\n"
        "\tn := len(cp)\n\tcount := 0\n"
        "\tfor i := 0; i < n-2; i++ {\n"
        "\t\tif i > 0 && cp[i] == cp[i-1] { continue }\n"
        "\t\tl, r := i+1, n-1\n"
        "\t\tfor l < r {\n"
        "\t\t\ts := cp[i] + cp[l] + cp[r]\n"
        "\t\t\tif s == 0 {\n"
        "\t\t\t\tcount++\n\t\t\t\tlv, rv := cp[l], cp[r]\n"
        "\t\t\t\tfor l < r && cp[l] == lv { l++ }\n"
        "\t\t\t\tfor l < r && cp[r] == rv { r-- }\n"
        "\t\t\t} else if s < 0 { l++ } else { r-- }\n\t\t}\n\t}\n"
        f"\treturn count{a}\n}}\n"
    )


@register("top-k-frequent-elements")
def _b_top_k_frequent_elements(wrong):
    extra = "\n\tif len(res) > 0 { res[0]++ }" if wrong else ""
    return (
        "func top_k_frequent(nums []int, k int) []int {\n"
        "\tfreq := map[int]int{}\n\tfor _, v := range nums { freq[v]++ }\n"
        "\tuniq := []int{}\n\tfor v := range freq { uniq = append(uniq, v) }\n"
        "\tsort.Slice(uniq, func(a, b int) bool {\n"
        "\t\tif freq[uniq[a]] != freq[uniq[b]] { return freq[uniq[a]] > freq[uniq[b]] }\n"
        "\t\treturn uniq[a] < uniq[b]\n\t})\n"
        "\tres := uniq[:k]\n"
        f"{extra}\n"
        "\treturn res\n}\n"
    )


@register("trapping-rain-water")
def _b_trapping_rain_water(wrong):
    a = " + 1" if wrong else ""
    return (
        "func trap(heights []int) int {\n"
        "\tif len(heights) == 0 { return 0" + a + " }\n"
        "\tl, r := 0, len(heights)-1\n\tleftMax, rightMax, total := 0, 0, 0\n"
        "\tfor l < r {\n"
        "\t\tif heights[l] < heights[r] {\n"
        "\t\t\tif heights[l] >= leftMax { leftMax = heights[l] } else { total += leftMax - heights[l] }\n\t\t\tl++\n"
        "\t\t} else {\n"
        "\t\t\tif heights[r] >= rightMax { rightMax = heights[r] } else { total += rightMax - heights[r] }\n\t\t\tr--\n"
        "\t\t}\n\t}\n"
        f"\treturn total{a}\n}}\n"
    )


@register("two-sum-count-pairs")
def _b_two_sum_count_pairs(wrong):
    a = " + 1" if wrong else ""
    return (
        "func count_pairs(nums []int, target int) int {\n"
        "\tfreq := map[int]int{}\n\tcount := 0\n"
        "\tfor _, x := range nums {\n"
        "\t\tneed := target - x\n"
        "\t\tif c, ok := freq[need]; ok { count += c }\n"
        "\t\tfreq[x]++\n\t}\n"
        f"\treturn count{a}\n}}\n"
    )


@register("unique-permutations-count")
def _b_unique_permutations_count(wrong):
    a = " + 1" if wrong else ""
    return (
        "func count_unique_permutations(nums []int) int {\n"
        "\tfreq := map[int]int64{}\n\tfor _, v := range nums { freq[v]++ }\n"
        "\tvar fact func(int64) int64\n"
        "\tfact = func(n int64) int64 { var r int64 = 1; for i := int64(2); i <= n; i++ { r *= i }; return r }\n"
        "\tdenom := int64(1)\n\tfor _, c := range freq { denom *= fact(c) }\n"
        "\tr := fact(int64(len(nums))) / denom\n"
        f"\treturn int(r){a}\n}}\n"
    )


@register("valid-anagram")
def _b_valid_anagram(wrong):
    neg = "!" if wrong else ""
    return (
        "func is_anagram(s string, t string) bool {\n"
        "\tif len(s) != len(t) { return " + neg + "false }\n"
        "\tcount := map[rune]int{}\n"
        "\tfor _, c := range s { count[c]++ }\n"
        "\tfor _, c := range t { count[c]-- }\n"
        "\tfor _, v := range count { if v != 0 { return " + neg + "false } }\n"
        f"\treturn {neg}true\n}}\n"
    )


@register("valid-palindrome-string")
def _b_valid_palindrome_string(wrong):
    neg = "!" if wrong else ""
    return (
        "func is_valid_palindrome(s string) bool {\n"
        "\tclean := []rune{}\n"
        "\tfor _, c := range s {\n"
        "\t\tif unicode.IsLetter(c) || unicode.IsDigit(c) { clean = append(clean, unicode.ToLower(c)) }\n\t}\n"
        "\ti, j := 0, len(clean)-1\n"
        "\tfor i < j { if clean[i] != clean[j] { return " + neg + "false }\n\t\ti++\n\t\tj--\n\t}\n"
        f"\treturn {neg}true\n}}\n"
    )


@register("valid-parentheses")
def _b_valid_parentheses(wrong):
    neg = "!" if wrong else ""
    return (
        "func is_valid(s string) bool {\n"
        "\tstack := []rune{}\n\tpairs := map[rune]rune{')': '(', ']': '[', '}': '{'}\n"
        "\tfor _, c := range s {\n"
        "\t\tif c == '(' || c == '[' || c == '{' { stack = append(stack, c) } else {\n"
        "\t\t\tif len(stack) == 0 || stack[len(stack)-1] != pairs[c] { return " + neg + "false }\n"
        "\t\t\tstack = stack[:len(stack)-1]\n\t\t}\n\t}\n"
        f"\treturn {neg}(len(stack) == 0)\n}}\n"
    )


@register("koko-eating-bananas")
def _b_koko_eating_bananas(wrong):
    a = " + 1" if wrong else ""
    return (
        "func min_eating_speed(piles []int, h int) int {\n"
        "\tlo, hi := 1, 0\n\tfor _, p := range piles { if p > hi { hi = p } }\n"
        "\thoursNeeded := func(speed int) int {\n"
        "\t\th2 := 0\n\t\tfor _, p := range piles { h2 += (p + speed - 1) / speed }\n\t\treturn h2\n\t}\n"
        "\tfor lo < hi {\n"
        "\t\tmid := (lo + hi) / 2\n"
        "\t\tif hoursNeeded(mid) <= h { hi = mid } else { lo = mid + 1 }\n\t}\n"
        f"\treturn lo{a}\n}}\n"
    )


@register("ship-packages-within-days")
def _b_ship_packages_within_days(wrong):
    a = " + 1" if wrong else ""
    return (
        "func ship_within_days(weights []int, days int) int {\n"
        "\tlo := 0\n\thi := 0\n"
        "\tfor _, w := range weights { if w > lo { lo = w }; hi += w }\n"
        "\tdaysNeeded := func(cap_ int) int {\n"
        "\t\td, cur := 1, 0\n"
        "\t\tfor _, w := range weights { if cur+w > cap_ { d++; cur = w } else { cur += w } }\n\t\treturn d\n\t}\n"
        "\tfor lo < hi {\n"
        "\t\tmid := (lo + hi) / 2\n"
        "\t\tif daysNeeded(mid) <= days { hi = mid } else { lo = mid + 1 }\n\t}\n"
        f"\treturn lo{a}\n}}\n"
    )


@register("max-sum-subarray-fixed-k")
def _b_max_sum_subarray_fixed_k(wrong):
    a = " + 1" if wrong else ""
    return (
        "func max_sum_fixed_k(nums []int, k int) int {\n"
        "\tsum := 0\n\tfor i := 0; i < k; i++ { sum += nums[i] }\n"
        "\tbest := sum\n"
        "\tfor i := k; i < len(nums); i++ {\n"
        "\t\tsum += nums[i] - nums[i-k]\n\t\tif sum > best { best = sum }\n\t}\n"
        f"\treturn best{a}\n}}\n"
    )


@register("max-consecutive-ones-with-k-flips")
def _b_max_consecutive_ones_with_k_flips(wrong):
    a = " + 1" if wrong else ""
    return (
        "func longest_ones(nums []int, k int) int {\n"
        "\tleft, zeros, best := 0, 0, 0\n"
        "\tfor right := 0; right < len(nums); right++ {\n"
        "\t\tif nums[right] == 0 { zeros++ }\n"
        "\t\tfor zeros > k { if nums[left] == 0 { zeros-- }\n\t\t\tleft++ }\n"
        "\t\tif right-left+1 > best { best = right - left + 1 }\n\t}\n"
        f"\treturn best{a}\n}}\n"
    )


@register("min-subarray-len-target-sum")
def _b_min_subarray_len_target_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "func min_subarray_len(nums []int, target int) int {\n"
        "\tleft, sum, best := 0, 0, 1<<62\n"
        "\tfor right := 0; right < len(nums); right++ {\n"
        "\t\tsum += nums[right]\n"
        "\t\tfor sum >= target {\n"
        "\t\t\tif right-left+1 < best { best = right - left + 1 }\n"
        "\t\t\tsum -= nums[left]\n\t\t\tleft++\n\t\t}\n\t}\n"
        "\tif best == 1<<62 { return 0" + a + " }\n"
        f"\treturn best{a}\n}}\n"
    )


# ═════════════════════════════════════════════════════════════════════════
# Harness plumbing (single language: go)
# ═════════════════════════════════════════════════════════════════════════

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
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ledger.ensure_schema(con)
    results = []
    skipped = 0
    items = _BUILDERS.items() if not only else [(k, v) for k, v in _BUILDERS.items() if k in only]
    for pid, build in items:
        contract, cases, tsv = load_problem(con, pid)
        if ledger.already_verified(con, pid, LANG, "function", test_suite_version=tsv):
            skipped += 1
            print(f"[SKIP] {pid:38s} already verified")
            continue
        r = await verify_one(pid, contract, cases, build)
        results.append(r)
        status = "PASS" if r["outcome"] == "verified" else "FAIL"
        print(f"[{status}] {pid:38s} {r['outcome']:18s} {r['detail'][:160]}", flush=True)
        if r["outcome"] == "verified":
            ledger.record_cell(con, problem_id=pid, language=LANG, mode="function",
                verification_level=ledger.LEVEL_VERIFIED, status="pass",
                adapter_version="go-function-port-v1", test_suite_version=tsv,
                duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL attempted: {len(results)}  skipped(already): {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
