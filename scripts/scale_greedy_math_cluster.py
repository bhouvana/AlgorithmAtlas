"""Scales activity-selection, closest-pair, collatz, counting-inversions,
egg-drop, euler-totient, gas-station, insert-interval, first-occurrence,
house-robber-circular (Function Mode) across the 8 working languages.
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


# ── activity-selection (max non-overlapping intervals, greedy by end) ──────
def _js_activity(wrong):
    ret = "count - 1" if wrong else "count"
    return (
        "function max_activities(starts, ends) {\n"
        "    const n = starts.length;\n"
        "    const idx = Array.from({length:n}, (_,i)=>i).sort((a,b)=>ends[a]-ends[b]);\n"
        "    let count = 0, lastEnd = -Infinity;\n"
        "    for (const i of idx) { if (starts[i] >= lastEnd) { count++; lastEnd = ends[i]; } }\n"
        f"    return {ret};\n"
        "}\n"
    )


def _ts_activity(wrong):
    ret = "count - 1" if wrong else "count"
    return (
        "function max_activities(starts: number[], ends: number[]): number {\n"
        "    const n = starts.length;\n"
        "    const idx = Array.from({length:n}, (_,i)=>i).sort((a,b)=>ends[a]-ends[b]);\n"
        "    let count = 0, lastEnd = -Infinity;\n"
        "    for (const i of idx) { if (starts[i] >= lastEnd) { count++; lastEnd = ends[i]; } }\n"
        f"    return {ret};\n"
        "}\n"
    )


def _java_activity(wrong):
    ret = "count - 1" if wrong else "count"
    return (
        "class Solution { public int max_activities(int[] starts, int[] ends) {\n"
        "    int n = starts.length;\n"
        "    Integer[] idx = new Integer[n]; for (int i=0;i<n;i++) idx[i]=i;\n"
        "    java.util.Arrays.sort(idx, (a,b) -> ends[a]-ends[b]);\n"
        "    int count = 0; long lastEnd = Long.MIN_VALUE;\n"
        "    for (int i : idx) { if (starts[i] >= lastEnd) { count++; lastEnd = ends[i]; } }\n"
        f"    return {ret};\n"
        "} }\n"
    )


def _cpp_activity(wrong):
    ret = "count - 1" if wrong else "count"
    return (
        "class Solution { public: int max_activities(std::vector<int> starts, std::vector<int> ends) {\n"
        "    int n = starts.size();\n"
        "    std::vector<int> idx(n); for (int i=0;i<n;i++) idx[i]=i;\n"
        "    std::sort(idx.begin(), idx.end(), [&](int a, int b){ return ends[a] < ends[b]; });\n"
        "    int count = 0; long long lastEnd = LLONG_MIN;\n"
        "    for (int i : idx) { if (starts[i] >= lastEnd) { count++; lastEnd = ends[i]; } }\n"
        f"    return {ret};\n"
        "} };\n"
    )


def _csharp_activity(wrong):
    ret = "count - 1" if wrong else "count"
    return (
        "class Solution { public static int max_activities(int[] starts, int[] ends) {\n"
        "    int n = starts.Length;\n"
        "    int[] idx = new int[n]; for (int i=0;i<n;i++) idx[i]=i;\n"
        "    System.Array.Sort(idx, (a,b) => ends[a]-ends[b]);\n"
        "    int count = 0; long lastEnd = long.MinValue;\n"
        "    foreach (int i in idx) { if (starts[i] >= lastEnd) { count++; lastEnd = ends[i]; } }\n"
        f"    return {ret};\n"
        "} }\n"
    )


def _perl_activity(wrong):
    ret = "$count - 1" if wrong else "$count"
    return (
        "sub max_activities {\n"
        "    my ($starts, $ends) = @_;\n"
        "    my @idx = sort { $ends->[$a] <=> $ends->[$b] } (0..scalar(@$starts)-1);\n"
        "    my $count = 0; my $lastEnd = -9**9**9;\n"
        "    foreach my $i (@idx) { if ($starts->[$i] >= $lastEnd) { $count++; $lastEnd = $ends->[$i]; } }\n"
        f"    return {ret};\n"
        "}\n"
    )


def _c_activity(wrong):
    ret = "count - 1" if wrong else "count"
    return (
        "int cmp_activity_idx; long long* cmp_activity_ends;\n"
        "int cmp_activity(const void* a, const void* b) {\n"
        "    int ia = *(const int*)a, ib = *(const int*)b;\n"
        "    long long diff = cmp_activity_ends[ia] - cmp_activity_ends[ib];\n"
        "    return diff < 0 ? -1 : (diff > 0 ? 1 : 0);\n"
        "}\n"
        "int max_activities(AtlasIntArray starts, AtlasIntArray ends) {\n"
        "    int n = starts.size;\n"
        "    long long* endsBuf = (long long*)malloc(sizeof(long long)*(n>0?n:1));\n"
        "    for (int i=0;i<n;i++) endsBuf[i] = ends.data[i];\n"
        "    cmp_activity_ends = endsBuf;\n"
        "    int* idx = (int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) idx[i]=i;\n"
        "    qsort(idx, n, sizeof(int), cmp_activity);\n"
        "    int count = 0; long long lastEnd = LLONG_MIN;\n"
        "    for (int k=0;k<n;k++) { int i = idx[k]; if (starts.data[i] >= lastEnd) { count++; lastEnd = ends.data[i]; } }\n"
        "    free(endsBuf); free(idx);\n"
        f"    return {ret};\n"
        "}\n"
    )


def _rust_activity(wrong):
    ret = "count - 1" if wrong else "count"
    return (
        "fn max_activities(starts: Vec<i32>, ends: Vec<i32>) -> i32 {\n"
        "    let n = starts.len();\n"
        "    let mut idx: Vec<usize> = (0..n).collect();\n"
        "    idx.sort_by_key(|&i| ends[i]);\n"
        "    let mut count = 0; let mut last_end: i64 = i64::MIN;\n"
        "    for &i in idx.iter() { if starts[i] as i64 >= last_end { count += 1; last_end = ends[i] as i64; } }\n"
        f"    {ret}\n"
        "}\n"
    )


# ── closest-pair (min squared distance, brute force) ────────────────────────
def _js_closest(wrong):
    a = " + 1" if wrong else ""
    return (
        "function closest_pair_sq_dist(points) {\n"
        "    let best = Infinity;\n"
        "    for (let i=0;i<points.length;i++) for (let j=i+1;j<points.length;j++) {\n"
        "        const dx = points[i][0]-points[j][0], dy = points[i][1]-points[j][1];\n"
        "        const d = dx*dx+dy*dy;\n"
        "        if (d < best) best = d;\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
    )


def _ts_closest(wrong):
    a = " + 1" if wrong else ""
    return (
        "function closest_pair_sq_dist(points: number[][]): number {\n"
        "    let best = Infinity;\n"
        "    for (let i=0;i<points.length;i++) for (let j=i+1;j<points.length;j++) {\n"
        "        const dx = points[i][0]-points[j][0], dy = points[i][1]-points[j][1];\n"
        "        const d = dx*dx+dy*dy;\n"
        "        if (d < best) best = d;\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
    )


def _java_closest(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public int closest_pair_sq_dist(int[][] points) {\n"
        "    long best = Long.MAX_VALUE;\n"
        "    for (int i=0;i<points.length;i++) for (int j=i+1;j<points.length;j++) {\n"
        "        long dx = points[i][0]-points[j][0], dy = points[i][1]-points[j][1];\n"
        "        long d = dx*dx+dy*dy;\n"
        "        if (d < best) best = d;\n"
        "    }\n"
        f"    return (int)(best{a});\n"
        "} }\n"
    )


def _cpp_closest(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public: int closest_pair_sq_dist(std::vector<std::vector<int>> points) {\n"
        "    long long best = LLONG_MAX;\n"
        "    for (size_t i=0;i<points.size();i++) for (size_t j=i+1;j<points.size();j++) {\n"
        "        long long dx = points[i][0]-points[j][0], dy = points[i][1]-points[j][1];\n"
        "        long long d = dx*dx+dy*dy;\n"
        "        if (d < best) best = d;\n"
        "    }\n"
        f"    return (int)(best{a});\n"
        "} };\n"
    )


def _csharp_closest(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public static int closest_pair_sq_dist(int[][] points) {\n"
        "    long best = long.MaxValue;\n"
        "    for (int i=0;i<points.Length;i++) for (int j=i+1;j<points.Length;j++) {\n"
        "        long dx = points[i][0]-points[j][0], dy = points[i][1]-points[j][1];\n"
        "        long d = dx*dx+dy*dy;\n"
        "        if (d < best) best = d;\n"
        "    }\n"
        f"    return (int)(best{a});\n"
        "} }\n"
    )


def _perl_closest(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub closest_pair_sq_dist {\n"
        "    my ($points) = @_;\n"
        "    my $best = 9**9**9;\n"
        "    for (my $i=0;$i<scalar(@$points);$i++) {\n"
        "        for (my $j=$i+1;$j<scalar(@$points);$j++) {\n"
        "            my $dx = $points->[$i][0]-$points->[$j][0]; my $dy = $points->[$i][1]-$points->[$j][1];\n"
        "            my $d = $dx*$dx+$dy*$dy;\n"
        "            $best = $d if $d < $best;\n"
        "        }\n"
        "    }\n"
        f"    return $best{a};\n"
        "}\n"
    )


def _c_closest(wrong):
    a = " + 1" if wrong else ""
    return (
        "long long closest_pair_sq_dist(AtlasIntMatrix points) {\n"
        "    long long best = LLONG_MAX;\n"
        "    for (int i=0;i<points.size;i++) for (int j=i+1;j<points.size;j++) {\n"
        "        long long dx = points.data[i].data[0]-points.data[j].data[0];\n"
        "        long long dy = points.data[i].data[1]-points.data[j].data[1];\n"
        "        long long d = dx*dx+dy*dy;\n"
        "        if (d < best) best = d;\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
    )


def _rust_closest(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn closest_pair_sq_dist(points: Vec<Vec<i32>>) -> i32 {\n"
        "    let mut best: i64 = i64::MAX;\n"
        "    for i in 0..points.len() { for j in (i+1)..points.len() {\n"
        "        let dx = (points[i][0]-points[j][0]) as i64; let dy = (points[i][1]-points[j][1]) as i64;\n"
        "        let d = dx*dx+dy*dy;\n"
        "        if d < best { best = d; }\n"
        "    } }\n"
        f"    (best as i32){a}\n"
        "}\n"
    )


# ── collatz (step count to reach 1) ─────────────────────────────────────────
def _js_collatz(wrong):
    a = " + 1" if wrong else ""
    return (
        "function collatz(n) {\n"
        "    let steps = 0; let x = n;\n"
        "    while (x !== 1) { if (x % 2 === 0) x = x/2; else x = 3*x+1; steps++; }\n"
        f"    return steps{a};\n"
        "}\n"
    )


def _ts_collatz(wrong):
    a = " + 1" if wrong else ""
    return (
        "function collatz(n: number): number {\n"
        "    let steps = 0; let x = n;\n"
        "    while (x !== 1) { if (x % 2 === 0) x = x/2; else x = 3*x+1; steps++; }\n"
        f"    return steps{a};\n"
        "}\n"
    )


def _java_collatz(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public int collatz(int n) {\n"
        "    int steps = 0; long x = n;\n"
        "    while (x != 1) { if (x % 2 == 0) x = x/2; else x = 3*x+1; steps++; }\n"
        f"    return steps{a};\n"
        "} }\n"
    )


def _cpp_collatz(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public: int collatz(int n) {\n"
        "    int steps = 0; long long x = n;\n"
        "    while (x != 1) { if (x % 2 == 0) x = x/2; else x = 3*x+1; steps++; }\n"
        f"    return steps{a};\n"
        "} };\n"
    )


def _csharp_collatz(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public static int collatz(int n) {\n"
        "    int steps = 0; long x = n;\n"
        "    while (x != 1) { if (x % 2 == 0) x = x/2; else x = 3*x+1; steps++; }\n"
        f"    return steps{a};\n"
        "} }\n"
    )


def _perl_collatz(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub collatz {\n"
        "    my ($n) = @_;\n"
        "    my $steps = 0; my $x = $n;\n"
        "    while ($x != 1) { if ($x % 2 == 0) { $x = $x/2; } else { $x = 3*$x+1; } $steps++; }\n"
        f"    return $steps{a};\n"
        "}\n"
    )


def _c_collatz(wrong):
    a = " + 1" if wrong else ""
    return (
        "int collatz(int n) {\n"
        "    int steps = 0; long long x = n;\n"
        "    while (x != 1) { if (x % 2 == 0) x = x/2; else x = 3*x+1; steps++; }\n"
        f"    return steps{a};\n"
        "}\n"
    )


def _rust_collatz(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn collatz(n: i32) -> i32 {\n"
        "    let mut steps = 0; let mut x: i64 = n as i64;\n"
        "    while x != 1 { if x % 2 == 0 { x = x/2; } else { x = 3*x+1; } steps += 1; }\n"
        f"    steps{a}\n"
        "}\n"
    )


# ── counting-inversions (O(n^2) brute force, corpus max n=1485) ────────────
def _js_countinv(wrong):
    a = " + 1" if wrong else ""
    return (
        "function count_inversions(nums) {\n"
        "    let count = 0;\n"
        "    for (let i=0;i<nums.length;i++) for (let j=i+1;j<nums.length;j++) if (nums[i] > nums[j]) count++;\n"
        f"    return count{a};\n"
        "}\n"
    )


def _ts_countinv(wrong):
    a = " + 1" if wrong else ""
    return (
        "function count_inversions(nums: number[]): number {\n"
        "    let count = 0;\n"
        "    for (let i=0;i<nums.length;i++) for (let j=i+1;j<nums.length;j++) if (nums[i] > nums[j]) count++;\n"
        f"    return count{a};\n"
        "}\n"
    )


def _java_countinv(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public int count_inversions(int[] nums) {\n"
        "    long count = 0;\n"
        "    for (int i=0;i<nums.length;i++) for (int j=i+1;j<nums.length;j++) if (nums[i] > nums[j]) count++;\n"
        f"    return (int)(count{a});\n"
        "} }\n"
    )


def _cpp_countinv(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public: int count_inversions(std::vector<int> nums) {\n"
        "    long long count = 0;\n"
        "    for (size_t i=0;i<nums.size();i++) for (size_t j=i+1;j<nums.size();j++) if (nums[i] > nums[j]) count++;\n"
        f"    return (int)(count{a});\n"
        "} };\n"
    )


def _csharp_countinv(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public static int count_inversions(int[] nums) {\n"
        "    long count = 0;\n"
        "    for (int i=0;i<nums.Length;i++) for (int j=i+1;j<nums.Length;j++) if (nums[i] > nums[j]) count++;\n"
        f"    return (int)(count{a});\n"
        "} }\n"
    )


def _perl_countinv(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub count_inversions {\n"
        "    my ($nums) = @_;\n"
        "    my $count = 0; my $n = scalar(@$nums);\n"
        "    for (my $i=0;$i<$n;$i++) { for (my $j=$i+1;$j<$n;$j++) { $count++ if $nums->[$i] > $nums->[$j]; } }\n"
        f"    return $count{a};\n"
        "}\n"
    )


def _c_countinv(wrong):
    a = " + 1" if wrong else ""
    return (
        "int count_inversions(AtlasIntArray nums) {\n"
        "    long long count = 0;\n"
        "    for (int i=0;i<nums.size;i++) for (int j=i+1;j<nums.size;j++) if (nums.data[i] > nums.data[j]) count++;\n"
        f"    return (int)(count{a});\n"
        "}\n"
    )


def _rust_countinv(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn count_inversions(nums: Vec<i32>) -> i32 {\n"
        "    let mut count: i64 = 0;\n"
        "    for i in 0..nums.len() { for j in (i+1)..nums.len() { if nums[i] > nums[j] { count += 1; } } }\n"
        f"    (count{a}) as i32\n"
        "}\n"
    )


# ── egg-drop (min trials, O(eggs*floors) DP) ─────────────────────────────────
def _js_eggdrop(wrong):
    a = " + 1" if wrong else ""
    return (
        "function egg_drop(eggs, floors) {\n"
        "    if (floors === 0) return 0" + a + ";\n"
        "    const dp = new Array(eggs+1).fill(0);\n"
        "    let moves = 0;\n"
        "    while (dp[eggs] < floors) {\n"
        "        moves++;\n"
        "        for (let k=eggs;k>=1;k--) dp[k] = dp[k] + dp[k-1] + 1;\n"
        "    }\n"
        f"    return moves{a};\n"
        "}\n"
    )


def _ts_eggdrop(wrong):
    a = " + 1" if wrong else ""
    return (
        "function egg_drop(eggs: number, floors: number): number {\n"
        "    if (floors === 0) return 0" + a + ";\n"
        "    const dp: number[] = new Array(eggs+1).fill(0);\n"
        "    let moves = 0;\n"
        "    while (dp[eggs] < floors) {\n"
        "        moves++;\n"
        "        for (let k=eggs;k>=1;k--) dp[k] = dp[k] + dp[k-1] + 1;\n"
        "    }\n"
        f"    return moves{a};\n"
        "}\n"
    )


def _java_eggdrop(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public int egg_drop(int eggs, int floors) {\n"
        "    if (floors == 0) return 0" + a + ";\n"
        "    int[] dp = new int[eggs+1];\n"
        "    int moves = 0;\n"
        "    while (dp[eggs] < floors) {\n"
        "        moves++;\n"
        "        for (int k=eggs;k>=1;k--) dp[k] = dp[k] + dp[k-1] + 1;\n"
        "    }\n"
        f"    return moves{a};\n"
        "} }\n"
    )


def _cpp_eggdrop(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public: int egg_drop(int eggs, int floors) {\n"
        "    if (floors == 0) return 0" + a + ";\n"
        "    std::vector<int> dp(eggs+1, 0);\n"
        "    int moves = 0;\n"
        "    while (dp[eggs] < floors) {\n"
        "        moves++;\n"
        "        for (int k=eggs;k>=1;k--) dp[k] = dp[k] + dp[k-1] + 1;\n"
        "    }\n"
        f"    return moves{a};\n"
        "} };\n"
    )


def _csharp_eggdrop(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public static int egg_drop(int eggs, int floors) {\n"
        "    if (floors == 0) return 0" + a + ";\n"
        "    int[] dp = new int[eggs+1];\n"
        "    int moves = 0;\n"
        "    while (dp[eggs] < floors) {\n"
        "        moves++;\n"
        "        for (int k=eggs;k>=1;k--) dp[k] = dp[k] + dp[k-1] + 1;\n"
        "    }\n"
        f"    return moves{a};\n"
        "} }\n"
    )


def _perl_eggdrop(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub egg_drop {\n"
        "    my ($eggs, $floors) = @_;\n"
        "    return (0" + a + ") if $floors == 0;\n"
        "    my @dp = (0) x ($eggs+1);\n"
        "    my $moves = 0;\n"
        "    while ($dp[$eggs] < $floors) {\n"
        "        $moves++;\n"
        "        for (my $k=$eggs;$k>=1;$k--) { $dp[$k] = $dp[$k] + $dp[$k-1] + 1; }\n"
        "    }\n"
        f"    return $moves{a};\n"
        "}\n"
    )


def _c_eggdrop(wrong):
    a = " + 1" if wrong else ""
    return (
        "int egg_drop(int eggs, int floors) {\n"
        "    if (floors == 0) return 0" + a + ";\n"
        "    int* dp = (int*)calloc(eggs+1, sizeof(int));\n"
        "    int moves = 0;\n"
        "    while (dp[eggs] < floors) {\n"
        "        moves++;\n"
        "        for (int k=eggs;k>=1;k--) dp[k] = dp[k] + dp[k-1] + 1;\n"
        "    }\n"
        "    free(dp);\n"
        f"    return moves{a};\n"
        "}\n"
    )


def _rust_eggdrop(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn egg_drop(eggs: i32, floors: i32) -> i32 {\n"
        "    if floors == 0 { return 0" + a + "; }\n"
        "    let e = eggs as usize;\n"
        "    let mut dp = vec![0i32; e+1];\n"
        "    let mut moves = 0;\n"
        "    while dp[e] < floors {\n"
        "        moves += 1;\n"
        "        for k in (1..=e).rev() { dp[k] = dp[k] + dp[k-1] + 1; }\n"
        "    }\n"
        f"    moves{a}\n"
        "}\n"
    )


# ── euler-totient (trial division, n up to 1,000,000) ───────────────────────
def _js_totient(wrong):
    a = " + 1" if wrong else ""
    return (
        "function euler_totient(n) {\n"
        "    let result = n; let x = n; let p = 2;\n"
        "    while (p*p <= x) {\n"
        "        if (x % p === 0) { while (x % p === 0) x = Math.floor(x/p); result -= Math.floor(result/p); }\n"
        "        p++;\n"
        "    }\n"
        "    if (x > 1) result -= Math.floor(result/x);\n"
        f"    return result{a};\n"
        "}\n"
    )


def _ts_totient(wrong):
    a = " + 1" if wrong else ""
    return (
        "function euler_totient(n: number): number {\n"
        "    let result = n; let x = n; let p = 2;\n"
        "    while (p*p <= x) {\n"
        "        if (x % p === 0) { while (x % p === 0) x = Math.floor(x/p); result -= Math.floor(result/p); }\n"
        "        p++;\n"
        "    }\n"
        "    if (x > 1) result -= Math.floor(result/x);\n"
        f"    return result{a};\n"
        "}\n"
    )


def _java_totient(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public int euler_totient(int n) {\n"
        "    int result = n; int x = n; int p = 2;\n"
        "    while ((long)p*p <= x) {\n"
        "        if (x % p == 0) { while (x % p == 0) x /= p; result -= result/p; }\n"
        "        p++;\n"
        "    }\n"
        "    if (x > 1) result -= result/x;\n"
        f"    return result{a};\n"
        "} }\n"
    )


def _cpp_totient(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public: int euler_totient(int n) {\n"
        "    int result = n; int x = n; long long p = 2;\n"
        "    while (p*p <= x) {\n"
        "        if (x % p == 0) { while (x % p == 0) x /= p; result -= result/p; }\n"
        "        p++;\n"
        "    }\n"
        "    if (x > 1) result -= result/x;\n"
        f"    return result{a};\n"
        "} };\n"
    )


def _csharp_totient(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public static int euler_totient(int n) {\n"
        "    int result = n; int x = n; long p = 2;\n"
        "    while (p*p <= x) {\n"
        "        if (x % p == 0) { while (x % p == 0) x /= (int)p; result -= result/(int)p; }\n"
        "        p++;\n"
        "    }\n"
        "    if (x > 1) result -= result/x;\n"
        f"    return result{a};\n"
        "} }\n"
    )


def _perl_totient(wrong):
    a = " + 1" if wrong else ""
    return (
        "use integer;\n"
        "sub euler_totient {\n"
        "    my ($n) = @_;\n"
        "    my $result = $n; my $x = $n; my $p = 2;\n"
        "    while ($p*$p <= $x) {\n"
        "        if ($x % $p == 0) { while ($x % $p == 0) { $x = $x/$p; } $result -= $result/$p; }\n"
        "        $p++;\n"
        "    }\n"
        "    if ($x > 1) { $result -= $result/$x; }\n"
        f"    return $result{a};\n"
        "}\n"
    )


def _c_totient(wrong):
    a = " + 1" if wrong else ""
    return (
        "int euler_totient(int n) {\n"
        "    int result = n; int x = n; long long p = 2;\n"
        "    while (p*p <= x) {\n"
        "        if (x % p == 0) { while (x % p == 0) x /= (int)p; result -= result/(int)p; }\n"
        "        p++;\n"
        "    }\n"
        "    if (x > 1) result -= result/x;\n"
        f"    return result{a};\n"
        "}\n"
    )


def _rust_totient(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn euler_totient(n: i32) -> i32 {\n"
        "    let mut result = n; let mut x = n; let mut p: i64 = 2;\n"
        "    while p*p <= x as i64 {\n"
        "        if x % (p as i32) == 0 { while x % (p as i32) == 0 { x /= p as i32; } result -= result/(p as i32); }\n"
        "        p += 1;\n"
        "    }\n"
        "    if x > 1 { result -= result/x; }\n"
        f"    result{a}\n"
        "}\n"
    )


# ── gas-station (greedy, O(n)) ────────────────────────────────────────────────
def _js_gasstation(wrong):
    ret = "start + 1" if wrong else "(total >= 0 ? start : -1)"
    return (
        "function can_complete_circuit(gas, cost) {\n"
        "    let total = 0, tank = 0, start = 0;\n"
        "    for (let i=0;i<gas.length;i++) {\n"
        "        const diff = gas[i]-cost[i]; total += diff; tank += diff;\n"
        "        if (tank < 0) { start = i+1; tank = 0; }\n"
        "    }\n"
        f"    return {ret};\n"
        "}\n"
    )


def _ts_gasstation(wrong):
    ret = "start + 1" if wrong else "(total >= 0 ? start : -1)"
    return (
        "function can_complete_circuit(gas: number[], cost: number[]): number {\n"
        "    let total = 0, tank = 0, start = 0;\n"
        "    for (let i=0;i<gas.length;i++) {\n"
        "        const diff = gas[i]-cost[i]; total += diff; tank += diff;\n"
        "        if (tank < 0) { start = i+1; tank = 0; }\n"
        "    }\n"
        f"    return {ret};\n"
        "}\n"
    )


def _java_gasstation(wrong):
    ret = "start + 1" if wrong else "(total >= 0 ? start : -1)"
    return (
        "class Solution { public int can_complete_circuit(int[] gas, int[] cost) {\n"
        "    long total = 0, tank = 0; int start = 0;\n"
        "    for (int i=0;i<gas.length;i++) {\n"
        "        long diff = gas[i]-cost[i]; total += diff; tank += diff;\n"
        "        if (tank < 0) { start = i+1; tank = 0; }\n"
        "    }\n"
        f"    return {ret};\n"
        "} }\n"
    )


def _cpp_gasstation(wrong):
    ret = "start + 1" if wrong else "(total >= 0 ? start : -1)"
    return (
        "class Solution { public: int can_complete_circuit(std::vector<int> gas, std::vector<int> cost) {\n"
        "    long long total = 0, tank = 0; int start = 0;\n"
        "    for (size_t i=0;i<gas.size();i++) {\n"
        "        long long diff = gas[i]-cost[i]; total += diff; tank += diff;\n"
        "        if (tank < 0) { start = i+1; tank = 0; }\n"
        "    }\n"
        f"    return {ret};\n"
        "} };\n"
    )


def _csharp_gasstation(wrong):
    ret = "start + 1" if wrong else "(total >= 0 ? start : -1)"
    return (
        "class Solution { public static int can_complete_circuit(int[] gas, int[] cost) {\n"
        "    long total = 0, tank = 0; int start = 0;\n"
        "    for (int i=0;i<gas.Length;i++) {\n"
        "        long diff = gas[i]-cost[i]; total += diff; tank += diff;\n"
        "        if (tank < 0) { start = i+1; tank = 0; }\n"
        "    }\n"
        f"    return {ret};\n"
        "} }\n"
    )


def _perl_gasstation(wrong):
    ret = "$start + 1" if wrong else "($total >= 0 ? $start : -1)"
    return (
        "sub can_complete_circuit {\n"
        "    my ($gas, $cost) = @_;\n"
        "    my $total = 0; my $tank = 0; my $start = 0;\n"
        "    for (my $i=0;$i<scalar(@$gas);$i++) {\n"
        "        my $diff = $gas->[$i]-$cost->[$i]; $total += $diff; $tank += $diff;\n"
        "        if ($tank < 0) { $start = $i+1; $tank = 0; }\n"
        "    }\n"
        f"    return {ret};\n"
        "}\n"
    )


def _c_gasstation(wrong):
    ret = "start + 1" if wrong else "(total >= 0 ? start : -1)"
    return (
        "int can_complete_circuit(AtlasIntArray gas, AtlasIntArray cost) {\n"
        "    long long total = 0, tank = 0; int start = 0;\n"
        "    for (int i=0;i<gas.size;i++) {\n"
        "        long long diff = gas.data[i]-cost.data[i]; total += diff; tank += diff;\n"
        "        if (tank < 0) { start = i+1; tank = 0; }\n"
        "    }\n"
        f"    return {ret};\n"
        "}\n"
    )


def _rust_gasstation(wrong):
    ret = "start + 1" if wrong else "(if total >= 0 { start } else { -1 })"
    return (
        "fn can_complete_circuit(gas: Vec<i32>, cost: Vec<i32>) -> i32 {\n"
        "    let mut total: i64 = 0; let mut tank: i64 = 0; let mut start: i32 = 0;\n"
        "    for i in 0..gas.len() {\n"
        "        let diff = (gas[i]-cost[i]) as i64; total += diff; tank += diff;\n"
        "        if tank < 0 { start = i as i32 + 1; tank = 0; }\n"
        "    }\n"
        f"    {ret}\n"
        "}\n"
    )


# ── insert-interval (merge new interval into sorted non-overlapping list) ──
def _js_insertint(wrong):
    incr = "for (const r of out) r[1] += 1;\n    " if wrong else ""
    return (
        "function insert_interval(intervals, new_s, new_e) {\n"
        "    const out = []; let i = 0; const n = intervals.length;\n"
        "    while (i < n && intervals[i][1] < new_s) { out.push(intervals[i]); i++; }\n"
        "    let s = new_s, e = new_e;\n"
        "    while (i < n && intervals[i][0] <= e) { s = Math.min(s, intervals[i][0]); e = Math.max(e, intervals[i][1]); i++; }\n"
        "    out.push([s,e]);\n"
        "    while (i < n) { out.push(intervals[i]); i++; }\n"
        f"    {incr}return out;\n"
        "}\n"
    )


def _ts_insertint(wrong):
    incr = "for (const r of out) r[1] += 1;\n    " if wrong else ""
    return (
        "function insert_interval(intervals: number[][], new_s: number, new_e: number): number[][] {\n"
        "    const out: number[][] = []; let i = 0; const n = intervals.length;\n"
        "    while (i < n && intervals[i][1] < new_s) { out.push(intervals[i]); i++; }\n"
        "    let s = new_s, e = new_e;\n"
        "    while (i < n && intervals[i][0] <= e) { s = Math.min(s, intervals[i][0]); e = Math.max(e, intervals[i][1]); i++; }\n"
        "    out.push([s,e]);\n"
        "    while (i < n) { out.push(intervals[i]); i++; }\n"
        f"    {incr}return out;\n"
        "}\n"
    )


def _java_insertint(wrong):
    incr = "for (int[] r : out) r[1] += 1;\n        " if wrong else ""
    return (
        "class Solution { public int[][] insert_interval(int[][] intervals, int new_s, int new_e) {\n"
        "    java.util.List<int[]> out = new java.util.ArrayList<>();\n"
        "    int i = 0, n = intervals.length;\n"
        "    while (i < n && intervals[i][1] < new_s) { out.add(intervals[i]); i++; }\n"
        "    int s = new_s, e = new_e;\n"
        "    while (i < n && intervals[i][0] <= e) { s = Math.min(s, intervals[i][0]); e = Math.max(e, intervals[i][1]); i++; }\n"
        "    out.add(new int[]{s,e});\n"
        "    while (i < n) { out.add(intervals[i]); i++; }\n"
        f"        {incr}return out.toArray(new int[0][]);\n"
        "} }\n"
    )


def _cpp_insertint(wrong):
    incr = "for (auto& r : out) r[1] += 1;\n    " if wrong else ""
    return (
        "class Solution { public: std::vector<std::vector<int>> insert_interval(std::vector<std::vector<int>> intervals, int new_s, int new_e) {\n"
        "    std::vector<std::vector<int>> out;\n"
        "    int i = 0, n = intervals.size();\n"
        "    while (i < n && intervals[i][1] < new_s) { out.push_back(intervals[i]); i++; }\n"
        "    int s = new_s, e = new_e;\n"
        "    while (i < n && intervals[i][0] <= e) { s = std::min(s, intervals[i][0]); e = std::max(e, intervals[i][1]); i++; }\n"
        "    out.push_back({s,e});\n"
        "    while (i < n) { out.push_back(intervals[i]); i++; }\n"
        f"    {incr}return out;\n"
        "} };\n"
    )


def _csharp_insertint(wrong):
    incr = "foreach (int[] r in outList) r[1] += 1;\n        " if wrong else ""
    return (
        "class Solution { public static int[][] insert_interval(int[][] intervals, int new_s, int new_e) {\n"
        "    var outList = new System.Collections.Generic.List<int[]>();\n"
        "    int i = 0, n = intervals.Length;\n"
        "    while (i < n && intervals[i][1] < new_s) { outList.Add(intervals[i]); i++; }\n"
        "    int s = new_s, e = new_e;\n"
        "    while (i < n && intervals[i][0] <= e) { s = System.Math.Min(s, intervals[i][0]); e = System.Math.Max(e, intervals[i][1]); i++; }\n"
        "    outList.Add(new int[]{s,e});\n"
        "    while (i < n) { outList.Add(intervals[i]); i++; }\n"
        f"        {incr}return outList.ToArray();\n"
        "} }\n"
    )


def _perl_insertint(wrong):
    incr = "foreach my $r (@out) { $r->[1] += 1; }\n    " if wrong else ""
    return (
        "sub insert_interval {\n"
        "    my ($intervals, $new_s, $new_e) = @_;\n"
        "    my @out; my $i = 0; my $n = scalar(@$intervals);\n"
        "    while ($i < $n && $intervals->[$i][1] < $new_s) { push @out, $intervals->[$i]; $i++; }\n"
        "    my $s = $new_s; my $e = $new_e;\n"
        "    while ($i < $n && $intervals->[$i][0] <= $e) {\n"
        "        $s = $intervals->[$i][0] if $intervals->[$i][0] < $s;\n"
        "        $e = $intervals->[$i][1] if $intervals->[$i][1] > $e;\n"
        "        $i++;\n"
        "    }\n"
        "    push @out, [$s, $e];\n"
        "    while ($i < $n) { push @out, $intervals->[$i]; $i++; }\n"
        f"    {incr}return \\@out;\n"
        "}\n"
    )


def _c_insertint(wrong):
    incr = "for (int i=0;i<oc;i++) out[i].data[1] += 1;\n    " if wrong else ""
    return (
        "AtlasIntMatrix insert_interval(AtlasIntMatrix intervals, int new_s, int new_e) {\n"
        "    int n = intervals.size;\n"
        "    AtlasIntArray* out = (AtlasIntArray*)malloc(sizeof(AtlasIntArray)*(n+1));\n"
        "    int oc = 0;\n"
        "    int i = 0;\n"
        "    while (i < n && intervals.data[i].data[1] < new_s) {\n"
        "        out[oc].size = 2; out[oc].data = (int*)malloc(sizeof(int)*2);\n"
        "        out[oc].data[0] = intervals.data[i].data[0]; out[oc].data[1] = intervals.data[i].data[1];\n"
        "        oc++; i++;\n"
        "    }\n"
        "    int s = new_s, e = new_e;\n"
        "    while (i < n && intervals.data[i].data[0] <= e) {\n"
        "        if (intervals.data[i].data[0] < s) s = intervals.data[i].data[0];\n"
        "        if (intervals.data[i].data[1] > e) e = intervals.data[i].data[1];\n"
        "        i++;\n"
        "    }\n"
        "    out[oc].size = 2; out[oc].data = (int*)malloc(sizeof(int)*2);\n"
        "    out[oc].data[0] = s; out[oc].data[1] = e; oc++;\n"
        "    while (i < n) {\n"
        "        out[oc].size = 2; out[oc].data = (int*)malloc(sizeof(int)*2);\n"
        "        out[oc].data[0] = intervals.data[i].data[0]; out[oc].data[1] = intervals.data[i].data[1];\n"
        "        oc++; i++;\n"
        "    }\n"
        f"    {incr}AtlasIntMatrix result; result.size = oc; result.data = out;\n"
        "    return result;\n"
        "}\n"
    )


def _rust_insertint(wrong):
    incr = "for r in out.iter_mut() { r[1] += 1; }\n    " if wrong else ""
    return (
        "fn insert_interval(intervals: Vec<Vec<i32>>, new_s: i32, new_e: i32) -> Vec<Vec<i32>> {\n"
        "    let mut out: Vec<Vec<i32>> = Vec::new();\n"
        "    let n = intervals.len(); let mut i = 0;\n"
        "    while i < n && intervals[i][1] < new_s { out.push(intervals[i].clone()); i += 1; }\n"
        "    let mut s = new_s; let mut e = new_e;\n"
        "    while i < n && intervals[i][0] <= e { s = s.min(intervals[i][0]); e = e.max(intervals[i][1]); i += 1; }\n"
        "    out.push(vec![s,e]);\n"
        "    while i < n { out.push(intervals[i].clone()); i += 1; }\n"
        f"    {incr}out\n"
        "}\n"
    )


# ── first-occurrence (binary search, leftmost index of target, -1 if absent) ─
def _js_firstocc(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "function first_occurrence(nums, target) {\n"
        "    let lo = 0, hi = nums.length-1, ans = -1;\n"
        "    while (lo <= hi) {\n"
        "        const mid = (lo+hi) >> 1;\n"
        f"        if (nums[mid] === target) {{ ans = {ret}; hi = mid-1; }}\n"
        "        else if (nums[mid] < target) lo = mid+1; else hi = mid-1;\n"
        "    }\n"
        "    return ans;\n"
        "}\n"
    )


def _ts_firstocc(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "function first_occurrence(nums: number[], target: number): number {\n"
        "    let lo = 0, hi = nums.length-1, ans = -1;\n"
        "    while (lo <= hi) {\n"
        "        const mid = (lo+hi) >> 1;\n"
        f"        if (nums[mid] === target) {{ ans = {ret}; hi = mid-1; }}\n"
        "        else if (nums[mid] < target) lo = mid+1; else hi = mid-1;\n"
        "    }\n"
        "    return ans;\n"
        "}\n"
    )


def _java_firstocc(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "class Solution { public int first_occurrence(int[] nums, int target) {\n"
        "    int lo = 0, hi = nums.length-1, ans = -1;\n"
        "    while (lo <= hi) {\n"
        "        int mid = (lo+hi) >>> 1;\n"
        f"        if (nums[mid] == target) {{ ans = {ret}; hi = mid-1; }}\n"
        "        else if (nums[mid] < target) lo = mid+1; else hi = mid-1;\n"
        "    }\n"
        "    return ans;\n"
        "} }\n"
    )


def _cpp_firstocc(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "class Solution { public: int first_occurrence(std::vector<int> nums, int target) {\n"
        "    int lo = 0, hi = (int)nums.size()-1, ans = -1;\n"
        "    while (lo <= hi) {\n"
        "        int mid = lo + (hi-lo)/2;\n"
        f"        if (nums[mid] == target) {{ ans = {ret}; hi = mid-1; }}\n"
        "        else if (nums[mid] < target) lo = mid+1; else hi = mid-1;\n"
        "    }\n"
        "    return ans;\n"
        "} };\n"
    )


def _csharp_firstocc(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "class Solution { public static int first_occurrence(int[] nums, int target) {\n"
        "    int lo = 0, hi = nums.Length-1, ans = -1;\n"
        "    while (lo <= hi) {\n"
        "        int mid = lo + (hi-lo)/2;\n"
        f"        if (nums[mid] == target) {{ ans = {ret}; hi = mid-1; }}\n"
        "        else if (nums[mid] < target) lo = mid+1; else hi = mid-1;\n"
        "    }\n"
        "    return ans;\n"
        "} }\n"
    )


def _perl_firstocc(wrong):
    ret = "$mid + 1" if wrong else "$mid"
    return (
        "sub first_occurrence {\n"
        "    my ($nums, $target) = @_;\n"
        "    my $lo = 0; my $hi = scalar(@$nums)-1; my $ans = -1;\n"
        "    while ($lo <= $hi) {\n"
        "        my $mid = int(($lo+$hi)/2);\n"
        f"        if ($nums->[$mid] == $target) {{ $ans = {ret}; $hi = $mid-1; }}\n"
        "        elsif ($nums->[$mid] < $target) { $lo = $mid+1; } else { $hi = $mid-1; }\n"
        "    }\n"
        "    return $ans;\n"
        "}\n"
    )


def _c_firstocc(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "int first_occurrence(AtlasIntArray nums, int target) {\n"
        "    int lo = 0, hi = nums.size-1, ans = -1;\n"
        "    while (lo <= hi) {\n"
        "        int mid = lo + (hi-lo)/2;\n"
        f"        if (nums.data[mid] == target) {{ ans = {ret}; hi = mid-1; }}\n"
        "        else if (nums.data[mid] < target) lo = mid+1; else hi = mid-1;\n"
        "    }\n"
        "    return ans;\n"
        "}\n"
    )


def _rust_firstocc(wrong):
    ret = "mid as i32 + 1" if wrong else "mid as i32"
    return (
        "fn first_occurrence(nums: Vec<i32>, target: i32) -> i32 {\n"
        "    if nums.is_empty() { return -1; }\n"
        "    let (mut lo, mut hi): (i32, i32) = (0, nums.len() as i32 - 1);\n"
        "    let mut ans: i32 = -1;\n"
        "    while lo <= hi {\n"
        "        let mid = lo + (hi-lo)/2;\n"
        f"        if nums[mid as usize] == target {{ ans = {ret}; hi = mid-1; }}\n"
        "        else if nums[mid as usize] < target { lo = mid+1; } else { hi = mid-1; }\n"
        "    }\n"
        "    ans\n"
        "}\n"
    )


# ── house-robber-circular (max non-adjacent sum, circular array) ────────────
def _js_robcirc(wrong):
    a = " + 1" if wrong else ""
    return (
        "function rob_line(nums) {\n"
        "    let prev = 0, cur = 0;\n"
        "    for (const x of nums) { const t = Math.max(cur, prev+x); prev = cur; cur = t; }\n"
        "    return cur;\n"
        "}\n"
        "function rob_circular(nums) {\n"
        "    const n = nums.length;\n"
        "    if (n === 1) return nums[0]" + a + ";\n"
        "    const a1 = rob_line(nums.slice(0, n-1));\n"
        "    const a2 = rob_line(nums.slice(1));\n"
        f"    return Math.max(a1, a2){a};\n"
        "}\n"
    )


def _ts_robcirc(wrong):
    a = " + 1" if wrong else ""
    return (
        "function rob_line(nums: number[]): number {\n"
        "    let prev = 0, cur = 0;\n"
        "    for (const x of nums) { const t = Math.max(cur, prev+x); prev = cur; cur = t; }\n"
        "    return cur;\n"
        "}\n"
        "function rob_circular(nums: number[]): number {\n"
        "    const n = nums.length;\n"
        "    if (n === 1) return nums[0]" + a + ";\n"
        "    const a1 = rob_line(nums.slice(0, n-1));\n"
        "    const a2 = rob_line(nums.slice(1));\n"
        f"    return Math.max(a1, a2){a};\n"
        "}\n"
    )


def _java_robcirc(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public int rob_circular(int[] nums) {\n"
        "    int n = nums.length;\n"
        "    if (n == 1) return nums[0]" + a + ";\n"
        "    int a1 = robLine(nums, 0, n-2);\n"
        "    int a2 = robLine(nums, 1, n-1);\n"
        f"    return Math.max(a1, a2){a};\n"
        "}\n"
        "int robLine(int[] nums, int lo, int hi) {\n"
        "    int prev = 0, cur = 0;\n"
        "    for (int i=lo;i<=hi;i++) { int t = Math.max(cur, prev+nums[i]); prev = cur; cur = t; }\n"
        "    return cur;\n"
        "} }\n"
    )


def _cpp_robcirc(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public: int rob_circular(std::vector<int> nums) {\n"
        "    int n = nums.size();\n"
        "    if (n == 1) return nums[0]" + a + ";\n"
        "    int a1 = robLine(nums, 0, n-2);\n"
        "    int a2 = robLine(nums, 1, n-1);\n"
        f"    return std::max(a1, a2){a};\n"
        "}\n"
        "int robLine(std::vector<int>& nums, int lo, int hi) {\n"
        "    int prev = 0, cur = 0;\n"
        "    for (int i=lo;i<=hi;i++) { int t = std::max(cur, prev+nums[i]); prev = cur; cur = t; }\n"
        "    return cur;\n"
        "} };\n"
    )


def _csharp_robcirc(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public static int rob_circular(int[] nums) {\n"
        "    int n = nums.Length;\n"
        "    if (n == 1) return nums[0]" + a + ";\n"
        "    int a1 = RobLine(nums, 0, n-2);\n"
        "    int a2 = RobLine(nums, 1, n-1);\n"
        f"    return System.Math.Max(a1, a2){a};\n"
        "}\n"
        "static int RobLine(int[] nums, int lo, int hi) {\n"
        "    int prev = 0, cur = 0;\n"
        "    for (int i=lo;i<=hi;i++) { int t = System.Math.Max(cur, prev+nums[i]); prev = cur; cur = t; }\n"
        "    return cur;\n"
        "} }\n"
    )


def _perl_robcirc(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub rob_line {\n"
        "    my ($nums, $lo, $hi) = @_;\n"
        "    my $prev = 0; my $cur = 0;\n"
        "    for (my $i=$lo;$i<=$hi;$i++) { my $t = ($cur > $prev+$nums->[$i]) ? $cur : $prev+$nums->[$i]; $prev = $cur; $cur = $t; }\n"
        "    return $cur;\n"
        "}\n"
        "sub rob_circular {\n"
        "    my ($nums) = @_;\n"
        "    my $n = scalar(@$nums);\n"
        "    return (${\\ $nums->[0]}" + a + ") if $n == 1;\n"
        "    my $a1 = rob_line($nums, 0, $n-2);\n"
        "    my $a2 = rob_line($nums, 1, $n-1);\n"
        f"    return (($a1 > $a2) ? $a1 : $a2){a};\n"
        "}\n"
    )


def _c_robcirc(wrong):
    a = " + 1" if wrong else ""
    return (
        "int rob_line(AtlasIntArray nums, int lo, int hi) {\n"
        "    int prev = 0, cur = 0;\n"
        "    for (int i=lo;i<=hi;i++) { int t = (cur > prev+nums.data[i]) ? cur : prev+nums.data[i]; prev = cur; cur = t; }\n"
        "    return cur;\n"
        "}\n"
        "int rob_circular(AtlasIntArray nums) {\n"
        "    int n = nums.size;\n"
        "    if (n == 1) return nums.data[0]" + a + ";\n"
        "    int a1 = rob_line(nums, 0, n-2);\n"
        "    int a2 = rob_line(nums, 1, n-1);\n"
        f"    return (a1 > a2 ? a1 : a2){a};\n"
        "}\n"
    )


def _rust_robcirc(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn rob_line(nums: &Vec<i32>, lo: usize, hi: usize) -> i32 {\n"
        "    let mut prev = 0; let mut cur = 0;\n"
        "    for i in lo..=hi { let t = cur.max(prev+nums[i]); prev = cur; cur = t; }\n"
        "    cur\n"
        "}\n"
        "fn rob_circular(nums: Vec<i32>) -> i32 {\n"
        "    let n = nums.len();\n"
        "    if n == 1 { return nums[0]" + a + "; }\n"
        "    let a1 = rob_line(&nums, 0, n-2);\n"
        "    let a2 = rob_line(&nums, 1, n-1);\n"
        f"    a1.max(a2){a}\n"
        "}\n"
    )


_BUILDERS = {
    "activity-selection": {"javascript": _js_activity, "typescript": _ts_activity, "java": _java_activity, "cpp": _cpp_activity,
                          "csharp": _csharp_activity, "perl": _perl_activity, "c": _c_activity, "rust": _rust_activity},
    "closest-pair": {"javascript": _js_closest, "typescript": _ts_closest, "java": _java_closest, "cpp": _cpp_closest,
                     "csharp": _csharp_closest, "perl": _perl_closest, "c": _c_closest, "rust": _rust_closest},
    "collatz": {"javascript": _js_collatz, "typescript": _ts_collatz, "java": _java_collatz, "cpp": _cpp_collatz,
               "csharp": _csharp_collatz, "perl": _perl_collatz, "c": _c_collatz, "rust": _rust_collatz},
    "counting-inversions": {"javascript": _js_countinv, "typescript": _ts_countinv, "java": _java_countinv, "cpp": _cpp_countinv,
                            "csharp": _csharp_countinv, "perl": _perl_countinv, "c": _c_countinv, "rust": _rust_countinv},
    "egg-drop": {"javascript": _js_eggdrop, "typescript": _ts_eggdrop, "java": _java_eggdrop, "cpp": _cpp_eggdrop,
                "csharp": _csharp_eggdrop, "perl": _perl_eggdrop, "c": _c_eggdrop, "rust": _rust_eggdrop},
    "euler-totient": {"javascript": _js_totient, "typescript": _ts_totient, "java": _java_totient, "cpp": _cpp_totient,
                      "csharp": _csharp_totient, "perl": _perl_totient, "c": _c_totient, "rust": _rust_totient},
    "gas-station": {"javascript": _js_gasstation, "typescript": _ts_gasstation, "java": _java_gasstation, "cpp": _cpp_gasstation,
                    "csharp": _csharp_gasstation, "perl": _perl_gasstation, "c": _c_gasstation, "rust": _rust_gasstation},
    "insert-interval": {"javascript": _js_insertint, "typescript": _ts_insertint, "java": _java_insertint, "cpp": _cpp_insertint,
                        "csharp": _csharp_insertint, "perl": _perl_insertint, "c": _c_insertint, "rust": _rust_insertint},
    "first-occurrence": {"javascript": _js_firstocc, "typescript": _ts_firstocc, "java": _java_firstocc, "cpp": _cpp_firstocc,
                         "csharp": _csharp_firstocc, "perl": _perl_firstocc, "c": _c_firstocc, "rust": _rust_firstocc},
    "house-robber-circular": {"javascript": _js_robcirc, "typescript": _ts_robcirc, "java": _java_robcirc, "cpp": _cpp_robcirc,
                              "csharp": _csharp_robcirc, "perl": _perl_robcirc, "c": _c_robcirc, "rust": _rust_robcirc},
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


async def verify_one(pid, lang, contract, cases, build):
    t0 = time.monotonic()
    correct_result = await evaluate_function(build(False), lang, contract, cases)
    n_pass = sum(1 for r in correct_result.case_results if r.passed)
    if n_pass != len(cases):
        sample_fail = next((r for r in correct_result.case_results if not r.passed), None)
        return {"pid": pid, "lang": lang, "outcome": "reference_failed",
                "detail": f"{n_pass}/{len(cases)} verdict={correct_result.verdict} "
                          f"compile={(correct_result.compile_output or '')[:150]} "
                          f"stderr={(sample_fail.stderr if sample_fail else '')[:150]} "
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
            "detail": f"{n_pass}/{len(cases)} correct, "
                      f"wrong rejected on {len(cases) - n_wrong_pass}/{len(cases)}",
            "duration_ms": (time.monotonic() - t0) * 1000}


async def main():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ledger.ensure_schema(con)
    results = []
    skipped = 0
    for pid, builders in _BUILDERS.items():
        contract, cases, tsv = load_problem(con, pid)
        for lang in _TARGET_LANGUAGES:
            if ledger.already_verified(con, pid, lang, "function", test_suite_version=tsv):
                skipped += 1
                continue
            r = await verify_one(pid, lang, contract, cases, builders[lang])
            results.append(r)
            status = "PASS" if r["outcome"] == "verified" else "FAIL"
            print(f"[{status}] {lang:10s}(function) {pid:24s} {r['outcome']:18s} {r['detail'][:130]}", flush=True)
            if r["outcome"] == "verified":
                ledger.record_cell(con, problem_id=pid, language=lang, mode="function",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=f"{lang}-function-greedy-math-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
