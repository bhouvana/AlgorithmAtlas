"""Scales best-time-to-buy-sell-stock(-ii), container-with-most-water,
trapping-rain-water, jump-game, product-of-array-except-self,
intersection-of-two-arrays, longest-consecutive-sequence,
find-duplicate-number, counting-bits (Function Mode) across the 8 working
languages.
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
_TARGET_LANGUAGES = ["javascript", "typescript", "java", "cpp", "csharp", "perl", "c", "rust"]


# ── best-time-to-buy-sell-stock ─────────────────────────────────────────────
def _js_bts1(wrong):
    a = " + 1" if wrong else ""
    return (
        "function max_profit(prices) {\n"
        "    let minP = prices[0], best = 0;\n"
        "    for (let i=1;i<prices.length;i++) { best = Math.max(best, prices[i]-minP); minP = Math.min(minP, prices[i]); }\n"
        f"    return best{a};\n"
        "}\n"
    )


def _ts_bts1(wrong):
    a = " + 1" if wrong else ""
    return (
        "function max_profit(prices: number[]): number {\n"
        "    let minP = prices[0], best = 0;\n"
        "    for (let i=1;i<prices.length;i++) { best = Math.max(best, prices[i]-minP); minP = Math.min(minP, prices[i]); }\n"
        f"    return best{a};\n"
        "}\n"
    )


def _java_bts1(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public int max_profit(int[] prices) {\n"
        "    int minP = prices[0], best = 0;\n"
        "    for (int i=1;i<prices.length;i++) { best = Math.max(best, prices[i]-minP); minP = Math.min(minP, prices[i]); }\n"
        f"    return best{a};\n"
        "} }\n"
    )


def _cpp_bts1(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public: int max_profit(std::vector<int> prices) {\n"
        "    int minP = prices[0], best = 0;\n"
        "    for (int i=1;i<(int)prices.size();i++) { best = std::max(best, prices[i]-minP); minP = std::min(minP, prices[i]); }\n"
        f"    return best{a};\n"
        "} };\n"
    )


def _csharp_bts1(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public static int max_profit(int[] prices) {\n"
        "    int minP = prices[0], best = 0;\n"
        "    for (int i=1;i<prices.Length;i++) { best = System.Math.Max(best, prices[i]-minP); minP = System.Math.Min(minP, prices[i]); }\n"
        f"    return best{a};\n"
        "} }\n"
    )


def _perl_bts1(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub max_profit {\n"
        "    my ($prices) = @_;\n"
        "    my $minP = $prices->[0]; my $best = 0;\n"
        "    for (my $i=1;$i<scalar(@$prices);$i++) {\n"
        "        my $profit = $prices->[$i] - $minP;\n"
        "        $best = $profit if $profit > $best;\n"
        "        $minP = $prices->[$i] if $prices->[$i] < $minP;\n"
        "    }\n"
        f"    return $best{a};\n"
        "}\n"
    )


def _c_bts1(wrong):
    a = " + 1" if wrong else ""
    return (
        "int max_profit(AtlasIntArray prices) {\n"
        "    int minP = prices.data[0], best = 0;\n"
        "    for (int i=1;i<prices.size;i++) {\n"
        "        int profit = prices.data[i] - minP;\n"
        "        if (profit > best) best = profit;\n"
        "        if (prices.data[i] < minP) minP = prices.data[i];\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
    )


def _rust_bts1(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn max_profit(prices: Vec<i32>) -> i32 {\n"
        "    let mut min_p = prices[0]; let mut best = 0;\n"
        "    for i in 1..prices.len() { best = best.max(prices[i]-min_p); min_p = min_p.min(prices[i]); }\n"
        f"    best{a}\n"
        "}\n"
    )


# ── best-time-to-buy-sell-stock-ii ──────────────────────────────────────────
def _js_bts2(wrong):
    a = " + 1" if wrong else ""
    return (
        "function max_profit(prices) {\n"
        "    let total = 0;\n"
        "    for (let i=1;i<prices.length;i++) { if (prices[i] > prices[i-1]) total += prices[i]-prices[i-1]; }\n"
        f"    return total{a};\n"
        "}\n"
    )


def _ts_bts2(wrong):
    a = " + 1" if wrong else ""
    return (
        "function max_profit(prices: number[]): number {\n"
        "    let total = 0;\n"
        "    for (let i=1;i<prices.length;i++) { if (prices[i] > prices[i-1]) total += prices[i]-prices[i-1]; }\n"
        f"    return total{a};\n"
        "}\n"
    )


def _java_bts2(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public int max_profit(int[] prices) {\n"
        "    int total = 0;\n"
        "    for (int i=1;i<prices.length;i++) { if (prices[i] > prices[i-1]) total += prices[i]-prices[i-1]; }\n"
        f"    return total{a};\n"
        "} }\n"
    )


def _cpp_bts2(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public: int max_profit(std::vector<int> prices) {\n"
        "    int total = 0;\n"
        "    for (int i=1;i<(int)prices.size();i++) { if (prices[i] > prices[i-1]) total += prices[i]-prices[i-1]; }\n"
        f"    return total{a};\n"
        "} };\n"
    )


def _csharp_bts2(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public static int max_profit(int[] prices) {\n"
        "    int total = 0;\n"
        "    for (int i=1;i<prices.Length;i++) { if (prices[i] > prices[i-1]) total += prices[i]-prices[i-1]; }\n"
        f"    return total{a};\n"
        "} }\n"
    )


def _perl_bts2(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub max_profit {\n"
        "    my ($prices) = @_;\n"
        "    my $total = 0;\n"
        "    for (my $i=1;$i<scalar(@$prices);$i++) { if ($prices->[$i] > $prices->[$i-1]) { $total += $prices->[$i]-$prices->[$i-1]; } }\n"
        f"    return $total{a};\n"
        "}\n"
    )


def _c_bts2(wrong):
    a = " + 1" if wrong else ""
    return (
        "int max_profit(AtlasIntArray prices) {\n"
        "    int total = 0;\n"
        "    for (int i=1;i<prices.size;i++) { if (prices.data[i] > prices.data[i-1]) total += prices.data[i]-prices.data[i-1]; }\n"
        f"    return total{a};\n"
        "}\n"
    )


def _rust_bts2(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn max_profit(prices: Vec<i32>) -> i32 {\n"
        "    let mut total = 0;\n"
        "    for i in 1..prices.len() { if prices[i] > prices[i-1] { total += prices[i]-prices[i-1]; } }\n"
        f"    total{a}\n"
        "}\n"
    )


# ── container-with-most-water ───────────────────────────────────────────────
# Wrong-corruption is +1 on the final result, not a >= vs > comparator swap:
# the >= variant was found (via corpus_weakness detection) to never actually
# change the winning area across the real 40-case corpus, since ties don't
# arise in the test data -- a genuinely too-weak defect, not a language issue.
def _js_container(wrong):
    a = " + 1" if wrong else ""
    return (
        "function max_area(heights) {\n"
        "    let lo=0, hi=heights.length-1, best=0;\n"
        "    while (lo<hi) {\n"
        "        const area = Math.min(heights[lo],heights[hi]) * (hi-lo);\n"
        "        if (area > best) best = area;\n"
        "        if (heights[lo] < heights[hi]) lo++; else hi--;\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
    )


def _ts_container(wrong):
    a = " + 1" if wrong else ""
    return (
        "function max_area(heights: number[]): number {\n"
        "    let lo=0, hi=heights.length-1, best=0;\n"
        "    while (lo<hi) {\n"
        "        const area = Math.min(heights[lo],heights[hi]) * (hi-lo);\n"
        "        if (area > best) best = area;\n"
        "        if (heights[lo] < heights[hi]) lo++; else hi--;\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
    )


def _java_container(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public int max_area(int[] heights) {\n"
        "    int lo=0, hi=heights.length-1, best=0;\n"
        "    while (lo<hi) {\n"
        "        int area = Math.min(heights[lo],heights[hi]) * (hi-lo);\n"
        "        if (area > best) best = area;\n"
        "        if (heights[lo] < heights[hi]) lo++; else hi--;\n"
        "    }\n"
        f"    return best{a};\n"
        "} }\n"
    )


def _cpp_container(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public: int max_area(std::vector<int> heights) {\n"
        "    int lo=0, hi=(int)heights.size()-1, best=0;\n"
        "    while (lo<hi) {\n"
        "        int area = std::min(heights[lo],heights[hi]) * (hi-lo);\n"
        "        if (area > best) best = area;\n"
        "        if (heights[lo] < heights[hi]) lo++; else hi--;\n"
        "    }\n"
        f"    return best{a};\n"
        "} };\n"
    )


def _csharp_container(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public static int max_area(int[] heights) {\n"
        "    int lo=0, hi=heights.Length-1, best=0;\n"
        "    while (lo<hi) {\n"
        "        int area = System.Math.Min(heights[lo],heights[hi]) * (hi-lo);\n"
        "        if (area > best) best = area;\n"
        "        if (heights[lo] < heights[hi]) lo++; else hi--;\n"
        "    }\n"
        f"    return best{a};\n"
        "} }\n"
    )


def _perl_container(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub max_area {\n"
        "    my ($heights) = @_;\n"
        "    my $lo = 0; my $hi = scalar(@$heights) - 1; my $best = 0;\n"
        "    while ($lo < $hi) {\n"
        "        my $m = ($heights->[$lo] < $heights->[$hi]) ? $heights->[$lo] : $heights->[$hi];\n"
        "        my $area = $m * ($hi - $lo);\n"
        "        $best = $area if $area > $best;\n"
        "        if ($heights->[$lo] < $heights->[$hi]) { $lo++; } else { $hi--; }\n"
        "    }\n"
        f"    return $best{a};\n"
        "}\n"
    )


def _c_container(wrong):
    a = " + 1" if wrong else ""
    return (
        "int max_area(AtlasIntArray heights) {\n"
        "    int lo=0, hi=heights.size-1, best=0;\n"
        "    while (lo<hi) {\n"
        "        int m = heights.data[lo] < heights.data[hi] ? heights.data[lo] : heights.data[hi];\n"
        "        int area = m * (hi-lo);\n"
        "        if (area > best) best = area;\n"
        "        if (heights.data[lo] < heights.data[hi]) lo++; else hi--;\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
    )


def _rust_container(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn max_area(heights: Vec<i32>) -> i32 {\n"
        "    let mut lo = 0usize; let mut hi = heights.len()-1; let mut best = 0;\n"
        "    while lo < hi {\n"
        "        let area = heights[lo].min(heights[hi]) * (hi-lo) as i32;\n"
        "        if area > best { best = area; }\n"
        "        if heights[lo] < heights[hi] { lo += 1; } else { hi -= 1; }\n"
        "    }\n"
        f"    best{a}\n"
        "}\n"
    )


# ── trapping-rain-water ──────────────────────────────────────────────────────
def _js_trap(wrong):
    a = " + 1" if wrong else ""
    return (
        "function trap(heights) {\n"
        "    let lo=0, hi=heights.length-1, leftMax=0, rightMax=0, total=0;\n"
        "    while (lo<hi) {\n"
        "        if (heights[lo] < heights[hi]) {\n"
        "            leftMax = Math.max(leftMax, heights[lo]); total += leftMax - heights[lo]; lo++;\n"
        "        } else { rightMax = Math.max(rightMax, heights[hi]); total += rightMax - heights[hi]; hi--; }\n"
        "    }\n"
        f"    return total{a};\n"
        "}\n"
    )


def _ts_trap(wrong):
    a = " + 1" if wrong else ""
    return (
        "function trap(heights: number[]): number {\n"
        "    let lo=0, hi=heights.length-1, leftMax=0, rightMax=0, total=0;\n"
        "    while (lo<hi) {\n"
        "        if (heights[lo] < heights[hi]) {\n"
        "            leftMax = Math.max(leftMax, heights[lo]); total += leftMax - heights[lo]; lo++;\n"
        "        } else { rightMax = Math.max(rightMax, heights[hi]); total += rightMax - heights[hi]; hi--; }\n"
        "    }\n"
        f"    return total{a};\n"
        "}\n"
    )


def _java_trap(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public int trap(int[] heights) {\n"
        "    int lo=0, hi=heights.length-1, leftMax=0, rightMax=0, total=0;\n"
        "    while (lo<hi) {\n"
        "        if (heights[lo] < heights[hi]) { leftMax = Math.max(leftMax, heights[lo]); total += leftMax - heights[lo]; lo++; }\n"
        "        else { rightMax = Math.max(rightMax, heights[hi]); total += rightMax - heights[hi]; hi--; }\n"
        "    }\n"
        f"    return total{a};\n"
        "} }\n"
    )


def _cpp_trap(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public: int trap(std::vector<int> heights) {\n"
        "    int lo=0, hi=(int)heights.size()-1, leftMax=0, rightMax=0, total=0;\n"
        "    while (lo<hi) {\n"
        "        if (heights[lo] < heights[hi]) { leftMax = std::max(leftMax, heights[lo]); total += leftMax - heights[lo]; lo++; }\n"
        "        else { rightMax = std::max(rightMax, heights[hi]); total += rightMax - heights[hi]; hi--; }\n"
        "    }\n"
        f"    return total{a};\n"
        "} };\n"
    )


def _csharp_trap(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public static int trap(int[] heights) {\n"
        "    int lo=0, hi=heights.Length-1, leftMax=0, rightMax=0, total=0;\n"
        "    while (lo<hi) {\n"
        "        if (heights[lo] < heights[hi]) { leftMax = System.Math.Max(leftMax, heights[lo]); total += leftMax - heights[lo]; lo++; }\n"
        "        else { rightMax = System.Math.Max(rightMax, heights[hi]); total += rightMax - heights[hi]; hi--; }\n"
        "    }\n"
        f"    return total{a};\n"
        "} }\n"
    )


def _perl_trap(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub trap {\n"
        "    my ($heights) = @_;\n"
        "    my $lo=0; my $hi=scalar(@$heights)-1; my $leftMax=0; my $rightMax=0; my $total=0;\n"
        "    while ($lo<$hi) {\n"
        "        if ($heights->[$lo] < $heights->[$hi]) {\n"
        "            $leftMax = $heights->[$lo] if $heights->[$lo] > $leftMax;\n"
        "            $total += $leftMax - $heights->[$lo]; $lo++;\n"
        "        } else {\n"
        "            $rightMax = $heights->[$hi] if $heights->[$hi] > $rightMax;\n"
        "            $total += $rightMax - $heights->[$hi]; $hi--;\n"
        "        }\n"
        "    }\n"
        f"    return $total{a};\n"
        "}\n"
    )


def _c_trap(wrong):
    a = " + 1" if wrong else ""
    return (
        "int trap(AtlasIntArray heights) {\n"
        "    int lo=0, hi=heights.size-1, leftMax=0, rightMax=0, total=0;\n"
        "    while (lo<hi) {\n"
        "        if (heights.data[lo] < heights.data[hi]) {\n"
        "            if (heights.data[lo] > leftMax) leftMax = heights.data[lo];\n"
        "            total += leftMax - heights.data[lo]; lo++;\n"
        "        } else {\n"
        "            if (heights.data[hi] > rightMax) rightMax = heights.data[hi];\n"
        "            total += rightMax - heights.data[hi]; hi--;\n"
        "        }\n"
        "    }\n"
        f"    return total{a};\n"
        "}\n"
    )


def _rust_trap(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn trap(heights: Vec<i32>) -> i32 {\n"
        "    let mut lo = 0usize; let mut hi = heights.len()-1;\n"
        "    let mut left_max = 0; let mut right_max = 0; let mut total = 0;\n"
        "    while lo < hi {\n"
        "        if heights[lo] < heights[hi] {\n"
        "            left_max = left_max.max(heights[lo]); total += left_max - heights[lo]; lo += 1;\n"
        "        } else {\n"
        "            right_max = right_max.max(heights[hi]); total += right_max - heights[hi]; hi -= 1;\n"
        "        }\n"
        "    }\n"
        f"    total{a}\n"
        "}\n"
    )


# ── jump-game ────────────────────────────────────────────────────────────────
def _js_jump_game(wrong):
    ret = "reach < nums.length - 1" if wrong else "reach >= nums.length - 1"
    return (
        "function can_jump(nums) {\n"
        "    let reach = 0;\n"
        "    for (let i=0;i<nums.length;i++) { if (i > reach) break; reach = Math.max(reach, i + nums[i]); }\n"
        f"    return {ret};\n"
        "}\n"
    )


def _ts_jump_game(wrong):
    ret = "reach < nums.length - 1" if wrong else "reach >= nums.length - 1"
    return (
        "function can_jump(nums: number[]): boolean {\n"
        "    let reach = 0;\n"
        "    for (let i=0;i<nums.length;i++) { if (i > reach) break; reach = Math.max(reach, i + nums[i]); }\n"
        f"    return {ret};\n"
        "}\n"
    )


def _java_jump_game(wrong):
    ret = "reach < nums.length - 1" if wrong else "reach >= nums.length - 1"
    return (
        "class Solution { public boolean can_jump(int[] nums) {\n"
        "    int reach = 0;\n"
        "    for (int i=0;i<nums.length;i++) { if (i > reach) break; reach = Math.max(reach, i + nums[i]); }\n"
        f"    return {ret};\n"
        "} }\n"
    )


def _cpp_jump_game(wrong):
    ret = "reach < (int)heights.size() - 1" if wrong else "reach >= (int)heights.size() - 1"
    ret = ret.replace("heights", "nums")
    return (
        "class Solution { public: bool can_jump(std::vector<int> nums) {\n"
        "    int reach = 0;\n"
        "    for (int i=0;i<(int)nums.size();i++) { if (i > reach) break; reach = std::max(reach, i + nums[i]); }\n"
        f"    return {ret};\n"
        "} };\n"
    )


def _csharp_jump_game(wrong):
    ret = "reach < nums.Length - 1" if wrong else "reach >= nums.Length - 1"
    return (
        "class Solution { public static bool can_jump(int[] nums) {\n"
        "    int reach = 0;\n"
        "    for (int i=0;i<nums.Length;i++) { if (i > reach) break; reach = System.Math.Max(reach, i + nums[i]); }\n"
        f"    return {ret};\n"
        "} }\n"
    )


def _perl_jump_game(wrong):
    ret = "$reach < scalar(@$nums) - 1" if wrong else "$reach >= scalar(@$nums) - 1"
    return (
        "sub can_jump {\n"
        "    my ($nums) = @_;\n"
        "    my $reach = 0;\n"
        "    for (my $i=0;$i<scalar(@$nums);$i++) {\n"
        "        last if $i > $reach;\n"
        "        my $cand = $i + $nums->[$i];\n"
        "        $reach = $cand if $cand > $reach;\n"
        "    }\n"
        f"    return ({ret}) ? 1 : 0;\n"
        "}\n"
    )


def _c_jump_game(wrong):
    ret = "reach < nums.size - 1" if wrong else "reach >= nums.size - 1"
    return (
        "int can_jump(AtlasIntArray nums) {\n"
        "    int reach = 0;\n"
        "    for (int i=0;i<nums.size;i++) {\n"
        "        if (i > reach) break;\n"
        "        int cand = i + nums.data[i];\n"
        "        if (cand > reach) reach = cand;\n"
        "    }\n"
        f"    return {ret};\n"
        "}\n"
    )


def _rust_jump_game(wrong):
    ret = "(reach as i32) < nums.len() as i32 - 1" if wrong else "reach as i32 >= nums.len() as i32 - 1"
    return (
        "fn can_jump(nums: Vec<i32>) -> bool {\n"
        "    let mut reach: i32 = 0;\n"
        "    for i in 0..nums.len() {\n"
        "        if i as i32 > reach { break; }\n"
        "        reach = reach.max(i as i32 + nums[i]);\n"
        "    }\n"
        f"    {ret}\n"
        "}\n"
    )


# ── product-of-array-except-self ────────────────────────────────────────────
def _js_prod_except(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "function product_except_self(nums) {\n"
        "    const n = nums.length; const out = new Array(n).fill(1);\n"
        "    let prefix = 1;\n"
        "    for (let i=0;i<n;i++) { out[i] = prefix; prefix *= nums[i]; }\n"
        "    let suffix = 1;\n"
        "    for (let i=n-1;i>=0;i--) { out[i] *= suffix; suffix *= nums[i]; }\n"
        f"    return out{a};\n"
        "}\n"
    )


def _ts_prod_except(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "function product_except_self(nums: number[]): number[] {\n"
        "    const n = nums.length; const out: number[] = new Array(n).fill(1);\n"
        "    let prefix = 1;\n"
        "    for (let i=0;i<n;i++) { out[i] = prefix; prefix *= nums[i]; }\n"
        "    let suffix = 1;\n"
        "    for (let i=n-1;i>=0;i--) { out[i] *= suffix; suffix *= nums[i]; }\n"
        f"    return out{a};\n"
        "}\n"
    )


def _java_prod_except(wrong):
    incr = "for (int i=0;i<n;i++) out[i]++;\n        " if wrong else ""
    return (
        "class Solution { public int[] product_except_self(int[] nums) {\n"
        "    int n = nums.length; int[] out = new int[n];\n"
        "    int prefix = 1;\n"
        "    for (int i=0;i<n;i++) { out[i] = prefix; prefix *= nums[i]; }\n"
        "    int suffix = 1;\n"
        "    for (int i=n-1;i>=0;i--) { out[i] *= suffix; suffix *= nums[i]; }\n"
        f"        {incr}return out;\n"
        "} }\n"
    )


def _cpp_prod_except(wrong):
    incr = "for (int i=0;i<n;i++) out[i]++;\n    " if wrong else ""
    return (
        "class Solution { public: std::vector<int> product_except_self(std::vector<int> nums) {\n"
        "    int n = nums.size(); std::vector<int> out(n, 1);\n"
        "    int prefix = 1;\n"
        "    for (int i=0;i<n;i++) { out[i] = prefix; prefix *= nums[i]; }\n"
        "    int suffix = 1;\n"
        "    for (int i=n-1;i>=0;i--) { out[i] *= suffix; suffix *= nums[i]; }\n"
        f"    {incr}return out;\n"
        "} };\n"
    )


def _csharp_prod_except(wrong):
    incr = "for (int i=0;i<n;i++) outArr[i]++;\n        " if wrong else ""
    return (
        "class Solution { public static int[] product_except_self(int[] nums) {\n"
        "    int n = nums.Length; int[] outArr = new int[n];\n"
        "    int prefix = 1;\n"
        "    for (int i=0;i<n;i++) { outArr[i] = prefix; prefix *= nums[i]; }\n"
        "    int suffix = 1;\n"
        "    for (int i=n-1;i>=0;i--) { outArr[i] *= suffix; suffix *= nums[i]; }\n"
        f"        {incr}return outArr;\n"
        "} }\n"
    )


def _perl_prod_except(wrong):
    incr = "for (my $i=0;$i<$n;$i++) { $out[$i]++; }\n    " if wrong else ""
    return (
        "sub product_except_self {\n"
        "    my ($nums) = @_;\n"
        "    my $n = scalar(@$nums); my @out = (1) x $n;\n"
        "    my $prefix = 1;\n"
        "    for (my $i=0;$i<$n;$i++) { $out[$i] = $prefix; $prefix *= $nums->[$i]; }\n"
        "    my $suffix = 1;\n"
        "    for (my $i=$n-1;$i>=0;$i--) { $out[$i] *= $suffix; $suffix *= $nums->[$i]; }\n"
        f"    {incr}return \\@out;\n"
        "}\n"
    )


def _c_prod_except(wrong):
    incr = "for (int i=0;i<n;i++) out.data[i]++;\n    " if wrong else ""
    return (
        "AtlasIntArray product_except_self(AtlasIntArray nums) {\n"
        "    int n = nums.size;\n"
        "    int* data = (int*)malloc(sizeof(int)*(n>0?n:1));\n"
        "    for (int i=0;i<n;i++) data[i]=1;\n"
        "    int prefix = 1;\n"
        "    for (int i=0;i<n;i++) { data[i] = prefix; prefix *= nums.data[i]; }\n"
        "    int suffix = 1;\n"
        "    for (int i=n-1;i>=0;i--) { data[i] *= suffix; suffix *= nums.data[i]; }\n"
        "    AtlasIntArray out; out.size = n; out.data = data;\n"
        f"    {incr}return out;\n"
        "}\n"
    )


def _rust_prod_except(wrong):
    incr = "for i in 0..n { out[i] += 1; }\n    " if wrong else ""
    return (
        "fn product_except_self(nums: Vec<i32>) -> Vec<i32> {\n"
        "    let n = nums.len(); let mut out = vec![1i32; n];\n"
        "    let mut prefix = 1;\n"
        "    for i in 0..n { out[i] = prefix; prefix *= nums[i]; }\n"
        "    let mut suffix = 1;\n"
        "    for i in (0..n).rev() { out[i] *= suffix; suffix *= nums[i]; }\n"
        f"    {incr}out\n"
        "}\n"
    )


# ── intersection-of-two-arrays (sorted unique intersection) ─────────────────
def _js_intersection(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "function intersection(nums1, nums2) {\n"
        "    const s1 = new Set(nums1), s2 = new Set(nums2);\n"
        "    const out = [...s1].filter(x => s2.has(x)).sort((a,b)=>a-b);\n"
        f"    return out{a};\n"
        "}\n"
    )


def _ts_intersection(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "function intersection(nums1: number[], nums2: number[]): number[] {\n"
        "    const s1 = new Set(nums1), s2 = new Set(nums2);\n"
        "    const out = [...s1].filter(x => s2.has(x)).sort((a,b)=>a-b);\n"
        f"    return out{a};\n"
        "}\n"
    )


def _java_intersection(wrong):
    incr = "for (int i=0;i<out.length;i++) out[i]++;\n        " if wrong else ""
    return (
        "class Solution { public int[] intersection(int[] nums1, int[] nums2) {\n"
        "    java.util.Set<Integer> s1 = new java.util.HashSet<>(); for (int x: nums1) s1.add(x);\n"
        "    java.util.Set<Integer> s2 = new java.util.HashSet<>(); for (int x: nums2) s2.add(x);\n"
        "    s1.retainAll(s2);\n"
        "    int[] out = s1.stream().mapToInt(Integer::intValue).sorted().toArray();\n"
        f"        {incr}return out;\n"
        "} }\n"
    )


def _cpp_intersection(wrong):
    incr = "for (auto& x : out) x++;\n    " if wrong else ""
    return (
        "class Solution { public: std::vector<int> intersection(std::vector<int> nums1, std::vector<int> nums2) {\n"
        "    std::set<int> s1(nums1.begin(), nums1.end()), s2(nums2.begin(), nums2.end());\n"
        "    std::vector<int> out;\n"
        "    for (int x : s1) if (s2.count(x)) out.push_back(x);\n"
        "    std::sort(out.begin(), out.end());\n"
        f"    {incr}return out;\n"
        "} };\n"
    )


def _csharp_intersection(wrong):
    incr = "for (int i=0;i<outArr.Length;i++) outArr[i]++;\n        " if wrong else ""
    return (
        "class Solution { public static int[] intersection(int[] nums1, int[] nums2) {\n"
        "    var s1 = new System.Collections.Generic.HashSet<int>(nums1);\n"
        "    var s2 = new System.Collections.Generic.HashSet<int>(nums2);\n"
        "    s1.IntersectWith(s2);\n"
        "    var outArr = new System.Collections.Generic.List<int>(s1); outArr.Sort();\n"
        f"        {incr}return outArr.ToArray();\n"
        "} }\n"
    )


def _perl_intersection(wrong):
    incr = "@out = map { $_ + 1 } @out;\n    " if wrong else ""
    return (
        "sub intersection {\n"
        "    my ($nums1, $nums2) = @_;\n"
        "    my %s1 = map { $_ => 1 } @$nums1;\n"
        "    my %s2 = map { $_ => 1 } @$nums2;\n"
        "    my @out = sort { $a <=> $b } grep { exists $s2{$_} } keys %s1;\n"
        f"    {incr}return \\@out;\n"
        "}\n"
    )


def _c_intersection(wrong):
    incr = "for (int i=0;i<oc;i++) out[i]++;\n    " if wrong else ""
    return (
        "int cmpint(const void* a, const void* b) { return *(const int*)a - *(const int*)b; }\n"
        "AtlasIntArray intersection(AtlasIntArray nums1, AtlasIntArray nums2) {\n"
        "    int* out = (int*)malloc(sizeof(int) * (nums1.size > 0 ? nums1.size : 1));\n"
        "    int oc = 0;\n"
        "    for (int i=0;i<nums1.size;i++) {\n"
        "        int v = nums1.data[i]; int dup = 0;\n"
        "        for (int k=0;k<oc;k++) if (out[k]==v) { dup=1; break; }\n"
        "        if (dup) continue;\n"
        "        int found = 0;\n"
        "        for (int j=0;j<nums2.size;j++) if (nums2.data[j]==v) { found=1; break; }\n"
        "        if (found) out[oc++] = v;\n"
        "    }\n"
        "    qsort(out, oc, sizeof(int), cmpint);\n"
        f"    {incr}AtlasIntArray result; result.size = oc; result.data = out;\n"
        "    return result;\n"
        "}\n"
    )


def _rust_intersection(wrong):
    incr = "for x in out.iter_mut() { *x += 1; }\n    " if wrong else ""
    return (
        "use std::collections::HashSet;\n"
        "fn intersection(nums1: Vec<i32>, nums2: Vec<i32>) -> Vec<i32> {\n"
        "    let s1: HashSet<i32> = nums1.into_iter().collect();\n"
        "    let s2: HashSet<i32> = nums2.into_iter().collect();\n"
        "    let mut out: Vec<i32> = s1.intersection(&s2).cloned().collect();\n"
        "    out.sort();\n"
        f"    {incr}out\n"
        "}\n"
    )


# ── longest-consecutive-sequence ────────────────────────────────────────────
def _js_lcseq(wrong):
    a = " + 1" if wrong else ""
    return (
        "function longest_consecutive(nums) {\n"
        "    const s = new Set(nums); let best = 0;\n"
        "    for (const x of s) {\n"
        "        if (!s.has(x-1)) { let len=1; let cur=x; while (s.has(cur+1)) { cur++; len++; } best = Math.max(best, len); }\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
    )


def _ts_lcseq(wrong):
    a = " + 1" if wrong else ""
    return (
        "function longest_consecutive(nums: number[]): number {\n"
        "    const s = new Set(nums); let best = 0;\n"
        "    for (const x of s) {\n"
        "        if (!s.has(x-1)) { let len=1; let cur=x; while (s.has(cur+1)) { cur++; len++; } best = Math.max(best, len); }\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
    )


def _java_lcseq(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public int longest_consecutive(int[] nums) {\n"
        "    java.util.Set<Integer> s = new java.util.HashSet<>(); for (int x: nums) s.add(x);\n"
        "    int best = 0;\n"
        "    for (int x : s) {\n"
        "        if (!s.contains(x-1)) { int len=1; int cur=x; while (s.contains(cur+1)) { cur++; len++; } best = Math.max(best, len); }\n"
        "    }\n"
        f"    return best{a};\n"
        "} }\n"
    )


def _cpp_lcseq(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public: int longest_consecutive(std::vector<int> nums) {\n"
        "    std::unordered_set<int> s(nums.begin(), nums.end()); int best = 0;\n"
        "    for (int x : s) {\n"
        "        if (!s.count(x-1)) { int len=1, cur=x; while (s.count(cur+1)) { cur++; len++; } best = std::max(best, len); }\n"
        "    }\n"
        f"    return best{a};\n"
        "} };\n"
    )


def _csharp_lcseq(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public static int longest_consecutive(int[] nums) {\n"
        "    var s = new System.Collections.Generic.HashSet<int>(nums); int best = 0;\n"
        "    foreach (int x in s) {\n"
        "        if (!s.Contains(x-1)) { int len=1, cur=x; while (s.Contains(cur+1)) { cur++; len++; } best = System.Math.Max(best, len); }\n"
        "    }\n"
        f"    return best{a};\n"
        "} }\n"
    )


def _perl_lcseq(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub longest_consecutive {\n"
        "    my ($nums) = @_;\n"
        "    my %s = map { $_ => 1 } @$nums;\n"
        "    my $best = 0;\n"
        "    foreach my $x (keys %s) {\n"
        "        if (!exists $s{$x-1}) {\n"
        "            my $len = 1; my $cur = $x;\n"
        "            while (exists $s{$cur+1}) { $cur++; $len++; }\n"
        "            $best = $len if $len > $best;\n"
        "        }\n"
        "    }\n"
        f"    return $best{a};\n"
        "}\n"
    )


def _c_lcseq(wrong):
    a = " + 1" if wrong else ""
    return (
        "int longest_consecutive(AtlasIntArray nums) {\n"
        "    int best = 0;\n"
        "    for (int i=0;i<nums.size;i++) {\n"
        "        int x = nums.data[i];\n"
        "        int hasPrev = 0;\n"
        "        for (int j=0;j<nums.size;j++) if (nums.data[j] == x-1) { hasPrev=1; break; }\n"
        "        if (hasPrev) continue;\n"
        "        int len = 1; int cur = x; int found = 1;\n"
        "        while (found) {\n"
        "            found = 0;\n"
        "            for (int j=0;j<nums.size;j++) if (nums.data[j] == cur+1) { found=1; break; }\n"
        "            if (found) { cur++; len++; }\n"
        "        }\n"
        "        if (len > best) best = len;\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
    )


def _rust_lcseq(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::collections::HashSet;\n"
        "fn longest_consecutive(nums: Vec<i32>) -> i32 {\n"
        "    let s: HashSet<i32> = nums.into_iter().collect();\n"
        "    let mut best = 0;\n"
        "    for &x in s.iter() {\n"
        "        if !s.contains(&(x-1)) {\n"
        "            let mut len = 1; let mut cur = x;\n"
        "            while s.contains(&(cur+1)) { cur += 1; len += 1; }\n"
        "            best = best.max(len);\n"
        "        }\n"
        "    }\n"
        f"    best{a}\n"
        "}\n"
    )


# ── find-duplicate-number ────────────────────────────────────────────────────
def _js_find_dup(wrong):
    a = " + 1" if wrong else ""
    return (
        "function find_duplicate(nums) {\n"
        "    const seen = new Set();\n"
        "    for (const x of nums) { if (seen.has(x)) return x" + a + "; seen.add(x); }\n"
        "    return -1;\n"
        "}\n"
    )


def _ts_find_dup(wrong):
    a = " + 1" if wrong else ""
    return (
        "function find_duplicate(nums: number[]): number {\n"
        "    const seen = new Set<number>();\n"
        "    for (const x of nums) { if (seen.has(x)) return x" + a + "; seen.add(x); }\n"
        "    return -1;\n"
        "}\n"
    )


def _java_find_dup(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public int find_duplicate(int[] nums) {\n"
        "    java.util.Set<Integer> seen = new java.util.HashSet<>();\n"
        "    for (int x : nums) { if (seen.contains(x)) return x" + a + "; seen.add(x); }\n"
        "    return -1;\n"
        "} }\n"
    )


def _cpp_find_dup(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public: int find_duplicate(std::vector<int> nums) {\n"
        "    std::unordered_set<int> seen;\n"
        "    for (int x : nums) { if (seen.count(x)) return x" + a + "; seen.insert(x); }\n"
        "    return -1;\n"
        "} };\n"
    )


def _csharp_find_dup(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public static int find_duplicate(int[] nums) {\n"
        "    var seen = new System.Collections.Generic.HashSet<int>();\n"
        "    foreach (int x in nums) { if (seen.Contains(x)) return x" + a + "; seen.Add(x); }\n"
        "    return -1;\n"
        "} }\n"
    )


def _perl_find_dup(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub find_duplicate {\n"
        "    my ($nums) = @_;\n"
        "    my %seen;\n"
        "    foreach my $x (@$nums) { return ($x" + a + ") if exists $seen{$x}; $seen{$x} = 1; }\n"
        "    return -1;\n"
        "}\n"
    )


def _c_find_dup(wrong):
    a = " + 1" if wrong else ""
    return (
        "int find_duplicate(AtlasIntArray nums) {\n"
        "    for (int i=0;i<nums.size;i++) {\n"
        "        for (int j=0;j<i;j++) if (nums.data[j] == nums.data[i]) return nums.data[i]" + a + ";\n"
        "    }\n"
        "    return -1;\n"
        "}\n"
    )


def _rust_find_dup(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::collections::HashSet;\n"
        "fn find_duplicate(nums: Vec<i32>) -> i32 {\n"
        "    let mut seen: HashSet<i32> = HashSet::new();\n"
        "    for x in nums.iter() { if seen.contains(x) { return (*x)" + a + "; } seen.insert(*x); }\n"
        "    -1\n"
        "}\n"
    )


# ── counting-bits ────────────────────────────────────────────────────────────
def _js_countbits(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "function count_bits(n) {\n"
        "    const out = new Array(n+1).fill(0);\n"
        "    for (let i=1;i<=n;i++) out[i] = out[i >> 1] + (i & 1);\n"
        f"    return out{a};\n"
        "}\n"
    )


def _ts_countbits(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "function count_bits(n: number): number[] {\n"
        "    const out: number[] = new Array(n+1).fill(0);\n"
        "    for (let i=1;i<=n;i++) out[i] = out[i >> 1] + (i & 1);\n"
        f"    return out{a};\n"
        "}\n"
    )


def _java_countbits(wrong):
    incr = "for (int i=0;i<=n;i++) out[i]++;\n        " if wrong else ""
    return (
        "class Solution { public int[] count_bits(int n) {\n"
        "    int[] out = new int[n+1];\n"
        "    for (int i=1;i<=n;i++) out[i] = out[i>>1] + (i&1);\n"
        f"        {incr}return out;\n"
        "} }\n"
    )


def _cpp_countbits(wrong):
    incr = "for (int i=0;i<=n;i++) out[i]++;\n    " if wrong else ""
    return (
        "class Solution { public: std::vector<int> count_bits(int n) {\n"
        "    std::vector<int> out(n+1, 0);\n"
        "    for (int i=1;i<=n;i++) out[i] = out[i>>1] + (i&1);\n"
        f"    {incr}return out;\n"
        "} };\n"
    )


def _csharp_countbits(wrong):
    incr = "for (int i=0;i<=n;i++) outArr[i]++;\n        " if wrong else ""
    return (
        "class Solution { public static int[] count_bits(int n) {\n"
        "    int[] outArr = new int[n+1];\n"
        "    for (int i=1;i<=n;i++) outArr[i] = outArr[i>>1] + (i&1);\n"
        f"        {incr}return outArr;\n"
        "} }\n"
    )


def _perl_countbits(wrong):
    incr = "for (my $i=0;$i<=$n;$i++) { $out[$i]++; }\n    " if wrong else ""
    return (
        "sub count_bits {\n"
        "    my ($n) = @_;\n"
        "    my @out = (0) x ($n+1);\n"
        "    for (my $i=1;$i<=$n;$i++) { $out[$i] = $out[$i >> 1] + ($i & 1); }\n"
        f"    {incr}return \\@out;\n"
        "}\n"
    )


def _c_countbits(wrong):
    incr = "for (int i=0;i<=n;i++) data[i]++;\n    " if wrong else ""
    return (
        "AtlasIntArray count_bits(int n) {\n"
        "    int* data = (int*)calloc(n+1, sizeof(int));\n"
        "    for (int i=1;i<=n;i++) data[i] = data[i>>1] + (i&1);\n"
        f"    {incr}AtlasIntArray out; out.size = n+1; out.data = data;\n"
        "    return out;\n"
        "}\n"
    )


def _rust_countbits(wrong):
    incr = "for i in 0..=n as usize { out[i] += 1; }\n    " if wrong else ""
    return (
        "fn count_bits(n: i32) -> Vec<i32> {\n"
        "    let mut out = vec![0i32; (n+1) as usize];\n"
        "    for i in 1..=n as usize { out[i] = out[i>>1] + (i as i32 & 1); }\n"
        f"    {incr}out\n"
        "}\n"
    )


_BUILDERS = {
    "best-time-to-buy-sell-stock": {"javascript": _js_bts1, "typescript": _ts_bts1, "java": _java_bts1, "cpp": _cpp_bts1,
                                    "csharp": _csharp_bts1, "perl": _perl_bts1, "c": _c_bts1, "rust": _rust_bts1},
    "best-time-to-buy-sell-stock-ii": {"javascript": _js_bts2, "typescript": _ts_bts2, "java": _java_bts2, "cpp": _cpp_bts2,
                                       "csharp": _csharp_bts2, "perl": _perl_bts2, "c": _c_bts2, "rust": _rust_bts2},
    "container-with-most-water": {"javascript": _js_container, "typescript": _ts_container, "java": _java_container, "cpp": _cpp_container,
                                  "csharp": _csharp_container, "perl": _perl_container, "c": _c_container, "rust": _rust_container},
    "trapping-rain-water": {"javascript": _js_trap, "typescript": _ts_trap, "java": _java_trap, "cpp": _cpp_trap,
                            "csharp": _csharp_trap, "perl": _perl_trap, "c": _c_trap, "rust": _rust_trap},
    "jump-game": {"javascript": _js_jump_game, "typescript": _ts_jump_game, "java": _java_jump_game, "cpp": _cpp_jump_game,
                 "csharp": _csharp_jump_game, "perl": _perl_jump_game, "c": _c_jump_game, "rust": _rust_jump_game},
    "product-of-array-except-self": {"javascript": _js_prod_except, "typescript": _ts_prod_except, "java": _java_prod_except, "cpp": _cpp_prod_except,
                                     "csharp": _csharp_prod_except, "perl": _perl_prod_except, "c": _c_prod_except, "rust": _rust_prod_except},
    "intersection-of-two-arrays": {"javascript": _js_intersection, "typescript": _ts_intersection, "java": _java_intersection, "cpp": _cpp_intersection,
                                   "csharp": _csharp_intersection, "perl": _perl_intersection, "c": _c_intersection, "rust": _rust_intersection},
    "longest-consecutive-sequence": {"javascript": _js_lcseq, "typescript": _ts_lcseq, "java": _java_lcseq, "cpp": _cpp_lcseq,
                                     "csharp": _csharp_lcseq, "perl": _perl_lcseq, "c": _c_lcseq, "rust": _rust_lcseq},
    "find-duplicate-number": {"javascript": _js_find_dup, "typescript": _ts_find_dup, "java": _java_find_dup, "cpp": _cpp_find_dup,
                              "csharp": _csharp_find_dup, "perl": _perl_find_dup, "c": _c_find_dup, "rust": _rust_find_dup},
    "counting-bits": {"javascript": _js_countbits, "typescript": _ts_countbits, "java": _java_countbits, "cpp": _cpp_countbits,
                      "csharp": _csharp_countbits, "perl": _perl_countbits, "c": _c_countbits, "rust": _rust_countbits},
}


def _maybe_json(v):
    return json.loads(v) if isinstance(v, str) else v


def load_problem(con, pid):
    row = con.execute("SELECT function_contract, test_suite_version FROM problems WHERE id=?", (pid,)).fetchone()
    contract = FunctionContract.from_dict(json.loads(row["function_contract"]))
    cur = con.execute(
        "SELECT id, function_args, function_expected, \"order\" FROM test_cases "
        "WHERE problem_id=? AND function_args IS NOT NULL ORDER BY \"order\"", (pid,),
    )
    cases = [
        FunctionCase(id=r["id"], arguments=_maybe_json(r["function_args"]), expected=_maybe_json(r["function_expected"]),
                     has_expected=True, is_hidden=False, order=r["order"])
        for r in cur.fetchall()
    ]
    return contract, cases, row["function_contract"], row["test_suite_version"]


async def verify_one(pid, lang, contract, cases, build):
    t0 = time.monotonic()
    correct_result = await evaluate_function(build(False), lang, contract, cases)
    n_pass = sum(1 for r in correct_result.case_results if r.passed)
    if n_pass != len(cases):
        sample_fail = next((r for r in correct_result.case_results if not r.passed), None)
        return {"pid": pid, "lang": lang, "outcome": "reference_failed",
                "detail": f"{n_pass}/{len(cases)} verdict={correct_result.verdict} "
                          f"compile={(correct_result.compile_output or '')[:200]} "
                          f"stderr={(sample_fail.stderr if sample_fail else '')[:200]} "
                          f"actual={(sample_fail.actual_return if sample_fail else '')!r} "
                          f"expected={(sample_fail.expected_return if sample_fail else '')!r}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    wrong_result = await evaluate_function(build(True), lang, contract, cases)
    n_wrong_pass = sum(1 for r in wrong_result.case_results if r.passed)
    if n_wrong_pass >= len(cases):
        return {"pid": pid, "lang": lang, "outcome": "corpus_weakness",
                "detail": f"corrupted solution still passed all {len(cases)}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    return {"pid": pid, "lang": lang, "outcome": "verified",
            "detail": f"{n_pass}/{len(cases)} correct, wrong rejected on {len(cases) - n_wrong_pass}/{len(cases)}",
            "duration_ms": (time.monotonic() - t0) * 1000}


async def main():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ledger.ensure_schema(con)
    results = []
    skipped = 0
    for pid, builders in _BUILDERS.items():
        for lang in _TARGET_LANGUAGES:
            contract, cases, raw, tsv = load_problem(con, pid)
            cv = ledger.contract_hash(raw)
            if ledger.already_verified(con, pid, lang, "function", contract_version=cv, test_suite_version=tsv):
                skipped += 1
                continue
            r = await verify_one(pid, lang, contract, cases, builders[lang])
            results.append(r)
            status = "PASS" if r["outcome"] == "verified" else "FAIL"
            print(f"[{status}] {lang:10s} {pid:30s} {r['outcome']:18s} {r['detail'][:130]}", flush=True)
            if r["outcome"] == "verified":
                ledger.record_cell(con, problem_id=pid, language=lang, mode="function",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=f"{lang}-array-cluster3-v1", contract_version=cv, test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
