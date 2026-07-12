"""Scales the next 9 problems (Function Mode) across the 8 original working
languages: job-scheduling, jump-game-ii-min-jumps, kth-largest-element,
koko-eating-bananas, largest-rectangle-in-histogram, last-occurrence,
longest-bitonic-subsequence, max-consecutive-ones-with-k-flips,
max-sum-subarray-fixed-k.
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


# ── job-scheduling (max deadline ~988, greedy slot-filling) ──────────────────
def _js_jobsched(wrong):
    a = " + 1" if wrong else ""
    return (f"function job_scheduling(deadlines, profits) {{\n"
            f"    const n = deadlines.length;\n"
            f"    const idx = Array.from({{length:n}}, (_,i)=>i).sort((a,b)=>profits[b]-profits[a]);\n"
            f"    const maxD = Math.max(...deadlines);\n"
            f"    const slot = new Array(maxD+1).fill(false);\n"
            f"    let total = 0;\n"
            f"    for (const i of idx) {{\n"
            f"        for (let d=Math.min(deadlines[i], maxD); d>=1; d--) {{\n"
            f"            if (!slot[d]) {{ slot[d]=true; total+=profits[i]; break; }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return total{a};\n}}\n")


def _ts_jobsched(wrong):
    a = " + 1" if wrong else ""
    return (f"function job_scheduling(deadlines: number[], profits: number[]): number {{\n"
            f"    const n = deadlines.length;\n"
            f"    const idx = Array.from({{length:n}}, (_,i)=>i).sort((a,b)=>profits[b]-profits[a]);\n"
            f"    const maxD = Math.max(...deadlines);\n"
            f"    const slot: boolean[] = new Array(maxD+1).fill(false);\n"
            f"    let total = 0;\n"
            f"    for (const i of idx) {{\n"
            f"        for (let d=Math.min(deadlines[i], maxD); d>=1; d--) {{\n"
            f"            if (!slot[d]) {{ slot[d]=true; total+=profits[i]; break; }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return total{a};\n}}\n")


def _java_jobsched(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int job_scheduling(int[] deadlines, int[] profits) {{\n"
            f"    int n = deadlines.length;\n"
            f"    Integer[] idx = new Integer[n]; for (int i=0;i<n;i++) idx[i]=i;\n"
            f"    java.util.Arrays.sort(idx, (a,b) -> profits[b]-profits[a]);\n"
            f"    int maxD=0; for (int d: deadlines) maxD=Math.max(maxD,d);\n"
            f"    boolean[] slot = new boolean[maxD+1]; long total=0;\n"
            f"    for (int i : idx) {{\n"
            f"        for (int d=Math.min(deadlines[i], maxD); d>=1; d--) {{\n"
            f"            if (!slot[d]) {{ slot[d]=true; total+=profits[i]; break; }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return (int)(total{a});\n}} }}\n")


def _cpp_jobsched(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int job_scheduling(std::vector<int> deadlines, std::vector<int> profits) {{\n"
            f"    int n = deadlines.size();\n"
            f"    std::vector<int> idx(n); for (int i=0;i<n;i++) idx[i]=i;\n"
            f"    std::sort(idx.begin(), idx.end(), [&](int a, int b){{ return profits[a]>profits[b]; }});\n"
            f"    int maxD=0; for (int d: deadlines) maxD=std::max(maxD,d);\n"
            f"    std::vector<bool> slot(maxD+1, false); long long total=0;\n"
            f"    for (int i : idx) {{\n"
            f"        for (int d=std::min(deadlines[i], maxD); d>=1; d--) {{\n"
            f"            if (!slot[d]) {{ slot[d]=true; total+=profits[i]; break; }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return (int)(total{a});\n}} }};\n")


def _csharp_jobsched(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int job_scheduling(int[] deadlines, int[] profits) {{\n"
            f"    int n = deadlines.Length;\n"
            f"    int[] idx = new int[n]; for (int i=0;i<n;i++) idx[i]=i;\n"
            f"    System.Array.Sort(idx, (a,b) => profits[b]-profits[a]);\n"
            f"    int maxD=0; foreach (int d in deadlines) maxD=System.Math.Max(maxD,d);\n"
            f"    bool[] slot = new bool[maxD+1]; long total=0;\n"
            f"    foreach (int i in idx) {{\n"
            f"        for (int d=System.Math.Min(deadlines[i], maxD); d>=1; d--) {{\n"
            f"            if (!slot[d]) {{ slot[d]=true; total+=profits[i]; break; }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return (int)(total{a});\n}} }}\n")


def _perl_jobsched(wrong):
    a = " + 1" if wrong else ""
    return (f"sub job_scheduling {{\n"
            f"    my ($deadlines, $profits) = @_;\n"
            f"    my $n = scalar(@$deadlines);\n"
            f"    my @idx = sort {{ $profits->[$b] <=> $profits->[$a] }} (0..$n-1);\n"
            f"    my $maxD=0; foreach my $d (@$deadlines) {{ $maxD=$d if $d>$maxD; }}\n"
            f"    my @slot = (0) x ($maxD+1); my $total=0;\n"
            f"    foreach my $i (@idx) {{\n"
            f"        for (my $d=($deadlines->[$i]<$maxD?$deadlines->[$i]:$maxD);$d>=1;$d--) {{\n"
            f"            if (!$slot[$d]) {{ $slot[$d]=1; $total+=$profits->[$i]; last; }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return $total{a};\n}}\n")


def _c_jobsched(wrong):
    a = " + 1" if wrong else ""
    return (f"int cmp_js_profits_idx; long* cmp_js_profits;\n"
            f"int cmp_js(const void* a, const void* b) {{\n"
            f"    int ia=*(const int*)a, ib=*(const int*)b;\n"
            f"    return cmp_js_profits[ib]-cmp_js_profits[ia];\n"
            f"}}\n"
            f"int job_scheduling(AtlasIntArray deadlines, AtlasIntArray profits) {{\n"
            f"    int n = deadlines.size;\n"
            f"    long* pbuf = (long*)malloc(sizeof(long)*(n>0?n:1));\n"
            f"    for (int i=0;i<n;i++) pbuf[i]=profits.data[i];\n"
            f"    cmp_js_profits = pbuf;\n"
            f"    int* idx = (int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) idx[i]=i;\n"
            f"    qsort(idx, n, sizeof(int), cmp_js);\n"
            f"    int maxD=0; for (int i=0;i<n;i++) if (deadlines.data[i]>maxD) maxD=deadlines.data[i];\n"
            f"    int* slot = (int*)calloc(maxD+1, sizeof(int)); long long total=0;\n"
            f"    for (int k=0;k<n;k++) {{\n"
            f"        int i = idx[k];\n"
            f"        int lim = deadlines.data[i]<maxD?deadlines.data[i]:maxD;\n"
            f"        for (int d=lim;d>=1;d--) {{ if (!slot[d]) {{ slot[d]=1; total+=profits.data[i]; break; }} }}\n"
            f"    }}\n"
            f"    free(pbuf); free(idx); free(slot);\n"
            f"    return (int)(total{a});\n}}\n")


def _rust_jobsched(wrong):
    a = " + 1" if wrong else ""
    return (f"fn job_scheduling(deadlines: Vec<i32>, profits: Vec<i32>) -> i32 {{\n"
            f"    let n = deadlines.len();\n"
            f"    let mut idx: Vec<usize> = (0..n).collect();\n"
            f"    idx.sort_by_key(|&i| -profits[i] as i64);\n"
            f"    let max_d = *deadlines.iter().max().unwrap_or(&0) as usize;\n"
            f"    let mut slot = vec![false; max_d+1]; let mut total: i64 = 0;\n"
            f"    for &i in idx.iter() {{\n"
            f"        let lim = (deadlines[i] as usize).min(max_d);\n"
            f"        for d in (1..=lim).rev() {{ if !slot[d] {{ slot[d]=true; total += profits[i] as i64; break; }} }}\n"
            f"    }}\n"
            f"    (total{a}) as i32\n}}\n")


# ── jump-game-ii-min-jumps (greedy) ──────────────────────────────────────────
def _js_jumpii(wrong):
    a = " + 1" if wrong else ""
    return (f"function jump(nums) {{\n"
            f"    let jumps=0, curEnd=0, farthest=0;\n"
            f"    for (let i=0;i<nums.length-1;i++) {{\n"
            f"        farthest = Math.max(farthest, i+nums[i]);\n"
            f"        if (i===curEnd) {{ jumps++; curEnd=farthest; }}\n"
            f"    }}\n"
            f"    return jumps{a};\n}}\n")


def _ts_jumpii(wrong):
    a = " + 1" if wrong else ""
    return (f"function jump(nums: number[]): number {{\n"
            f"    let jumps=0, curEnd=0, farthest=0;\n"
            f"    for (let i=0;i<nums.length-1;i++) {{\n"
            f"        farthest = Math.max(farthest, i+nums[i]);\n"
            f"        if (i===curEnd) {{ jumps++; curEnd=farthest; }}\n"
            f"    }}\n"
            f"    return jumps{a};\n}}\n")


def _java_jumpii(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int jump(int[] nums) {{\n"
            f"    int jumps=0, curEnd=0, farthest=0;\n"
            f"    for (int i=0;i<nums.length-1;i++) {{\n"
            f"        farthest = Math.max(farthest, i+nums[i]);\n"
            f"        if (i==curEnd) {{ jumps++; curEnd=farthest; }}\n"
            f"    }}\n"
            f"    return jumps{a};\n}} }}\n")


def _cpp_jumpii(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int jump(std::vector<int> nums) {{\n"
            f"    int jumps=0, curEnd=0, farthest=0;\n"
            f"    for (int i=0;i<(int)nums.size()-1;i++) {{\n"
            f"        farthest = std::max(farthest, i+nums[i]);\n"
            f"        if (i==curEnd) {{ jumps++; curEnd=farthest; }}\n"
            f"    }}\n"
            f"    return jumps{a};\n}} }};\n")


def _csharp_jumpii(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int jump(int[] nums) {{\n"
            f"    int jumps=0, curEnd=0, farthest=0;\n"
            f"    for (int i=0;i<nums.Length-1;i++) {{\n"
            f"        farthest = System.Math.Max(farthest, i+nums[i]);\n"
            f"        if (i==curEnd) {{ jumps++; curEnd=farthest; }}\n"
            f"    }}\n"
            f"    return jumps{a};\n}} }}\n")


def _perl_jumpii(wrong):
    a = " + 1" if wrong else ""
    return (f"sub jump {{\n"
            f"    my ($nums) = @_;\n"
            f"    my $jumps=0; my $curEnd=0; my $farthest=0;\n"
            f"    for (my $i=0;$i<scalar(@$nums)-1;$i++) {{\n"
            f"        my $cand = $i+$nums->[$i]; $farthest=$cand if $cand>$farthest;\n"
            f"        if ($i==$curEnd) {{ $jumps++; $curEnd=$farthest; }}\n"
            f"    }}\n"
            f"    return $jumps{a};\n}}\n")


def _c_jumpii(wrong):
    a = " + 1" if wrong else ""
    return (f"int jump(AtlasIntArray nums) {{\n"
            f"    int jumps=0, curEnd=0, farthest=0;\n"
            f"    for (int i=0;i<nums.size-1;i++) {{\n"
            f"        int cand = i+nums.data[i]; if (cand>farthest) farthest=cand;\n"
            f"        if (i==curEnd) {{ jumps++; curEnd=farthest; }}\n"
            f"    }}\n"
            f"    return jumps{a};\n}}\n")


def _rust_jumpii(wrong):
    a = " + 1" if wrong else ""
    return (f"fn jump(nums: Vec<i32>) -> i32 {{\n"
            f"    let mut jumps=0; let mut cur_end=0i32; let mut farthest=0i32;\n"
            f"    for i in 0..(nums.len() as i32 -1) {{\n"
            f"        farthest = farthest.max(i+nums[i as usize]);\n"
            f"        if i==cur_end {{ jumps+=1; cur_end=farthest; }}\n"
            f"    }}\n"
            f"    jumps{a}\n}}\n")


# ── kth-largest-element (sort desc, take k-1) ────────────────────────────────
def _js_kthlarge(wrong):
    a = " + 1" if wrong else ""
    return (f"function kth_largest(nums, k) {{\n"
            f"    const sorted = nums.slice().sort((a,b)=>b-a);\n"
            f"    return sorted[k-1]{a};\n}}\n")


def _ts_kthlarge(wrong):
    a = " + 1" if wrong else ""
    return (f"function kth_largest(nums: number[], k: number): number {{\n"
            f"    const sorted = nums.slice().sort((a,b)=>b-a);\n"
            f"    return sorted[k-1]{a};\n}}\n")


def _java_kthlarge(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int kth_largest(int[] nums, int k) {{\n"
            f"    int[] sorted = nums.clone(); java.util.Arrays.sort(sorted);\n"
            f"    return sorted[sorted.length-k]{a};\n}} }}\n")


def _cpp_kthlarge(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int kth_largest(std::vector<int> nums, int k) {{\n"
            f"    std::sort(nums.begin(), nums.end());\n"
            f"    return nums[nums.size()-k]{a};\n}} }};\n")


def _csharp_kthlarge(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int kth_largest(int[] nums, int k) {{\n"
            f"    int[] sorted = (int[])nums.Clone(); System.Array.Sort(sorted);\n"
            f"    return sorted[sorted.Length-k]{a};\n}} }}\n")


def _perl_kthlarge(wrong):
    a = " + 1" if wrong else ""
    return (f"sub kth_largest {{\n"
            f"    my ($nums, $k) = @_;\n"
            f"    my @sorted = sort {{ $b <=> $a }} @$nums;\n"
            f"    return $sorted[$k-1]{a};\n}}\n")


def _c_kthlarge(wrong):
    a = " + 1" if wrong else ""
    return (f"int cmp_kth(const void* a, const void* b) {{ return *(const int*)b - *(const int*)a; }}\n"
            f"int kth_largest(AtlasIntArray nums, int k) {{\n"
            f"    int* sorted = (int*)malloc(sizeof(int)*nums.size);\n"
            f"    for (int i=0;i<nums.size;i++) sorted[i]=nums.data[i];\n"
            f"    qsort(sorted, nums.size, sizeof(int), cmp_kth);\n"
            f"    int r = sorted[k-1]; free(sorted);\n"
            f"    return r{a};\n}}\n")


def _rust_kthlarge(wrong):
    a = " + 1" if wrong else ""
    return (f"fn kth_largest(nums: Vec<i32>, k: i32) -> i32 {{\n"
            f"    let mut sorted = nums.clone(); sorted.sort_by(|a,b| b.cmp(a));\n"
            f"    (sorted[(k-1) as usize]){a}\n}}\n")


# ── koko-eating-bananas (binary search on speed) ────────────────────────────
def _js_koko(wrong):
    a = " + 1" if wrong else ""
    return (f"function min_eating_speed(piles, h) {{\n"
            f"    function hoursNeeded(speed) {{ let hrs=0; for (const p of piles) hrs+=Math.ceil(p/speed); return hrs; }}\n"
            f"    let lo=1, hi=Math.max(...piles);\n"
            f"    while (lo<hi) {{ const mid=(lo+hi)>>1; if (hoursNeeded(mid)<=h) hi=mid; else lo=mid+1; }}\n"
            f"    return lo{a};\n}}\n")


def _ts_koko(wrong):
    a = " + 1" if wrong else ""
    return (f"function min_eating_speed(piles: number[], h: number): number {{\n"
            f"    function hoursNeeded(speed: number): number {{ let hrs=0; for (const p of piles) hrs+=Math.ceil(p/speed); return hrs; }}\n"
            f"    let lo=1, hi=Math.max(...piles);\n"
            f"    while (lo<hi) {{ const mid=(lo+hi)>>1; if (hoursNeeded(mid)<=h) hi=mid; else lo=mid+1; }}\n"
            f"    return lo{a};\n}}\n")


def _java_koko(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int min_eating_speed(int[] piles, int h) {{\n"
            f"    int lo=1, hi=0; for (int p: piles) hi=Math.max(hi,p);\n"
            f"    while (lo<hi) {{ int mid=(lo+hi)/2; if (hoursNeeded(piles,mid)<=h) hi=mid; else lo=mid+1; }}\n"
            f"    return lo{a};\n}}\n"
            f"long hoursNeeded(int[] piles, int speed) {{ long hrs=0; for (int p: piles) hrs += (p+speed-1)/speed; return hrs; }} }}\n")


def _cpp_koko(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int min_eating_speed(std::vector<int> piles, int h) {{\n"
            f"    int lo=1, hi=0; for (int p: piles) hi=std::max(hi,p);\n"
            f"    while (lo<hi) {{ int mid=lo+(hi-lo)/2; if (hoursNeeded(piles,mid)<=h) hi=mid; else lo=mid+1; }}\n"
            f"    return lo{a};\n}}\n"
            f"long long hoursNeeded(std::vector<int>& piles, int speed) {{ long long hrs=0; for (int p: piles) hrs += (p+speed-1)/speed; return hrs; }} }};\n")


def _csharp_koko(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int min_eating_speed(int[] piles, int h) {{\n"
            f"    int lo=1, hi=0; foreach (int p in piles) hi=System.Math.Max(hi,p);\n"
            f"    while (lo<hi) {{ int mid=lo+(hi-lo)/2; if (HoursNeeded(piles,mid)<=h) hi=mid; else lo=mid+1; }}\n"
            f"    return lo{a};\n}}\n"
            f"static long HoursNeeded(int[] piles, int speed) {{ long hrs=0; foreach (int p in piles) hrs += (p+speed-1)/speed; return hrs; }} }}\n")


def _perl_koko(wrong):
    a = " + 1" if wrong else ""
    return (f"sub hours_needed {{ my ($piles,$speed)=@_; my $hrs=0; foreach my $p (@$piles) {{ $hrs += int(($p+$speed-1)/$speed); }} return $hrs; }}\n"
            f"sub min_eating_speed {{\n"
            f"    my ($piles, $h) = @_;\n"
            f"    my $lo=1; my $hi=0; foreach my $p (@$piles) {{ $hi=$p if $p>$hi; }}\n"
            f"    while ($lo<$hi) {{ my $mid=int(($lo+$hi)/2); if (hours_needed($piles,$mid)<=$h) {{ $hi=$mid; }} else {{ $lo=$mid+1; }} }}\n"
            f"    return $lo{a};\n}}\n")


def _c_koko(wrong):
    a = " + 1" if wrong else ""
    return (f"long long hours_needed_koko(AtlasIntArray piles, int speed) {{\n"
            f"    long long hrs=0; for (int i=0;i<piles.size;i++) hrs += (piles.data[i]+speed-1)/speed;\n"
            f"    return hrs;\n}}\n"
            f"int min_eating_speed(AtlasIntArray piles, int h) {{\n"
            f"    int lo=1, hi=0; for (int i=0;i<piles.size;i++) if (piles.data[i]>hi) hi=piles.data[i];\n"
            f"    while (lo<hi) {{ int mid=lo+(hi-lo)/2; if (hours_needed_koko(piles,mid)<=h) hi=mid; else lo=mid+1; }}\n"
            f"    return lo{a};\n}}\n")


def _rust_koko(wrong):
    a = " + 1" if wrong else ""
    return (f"fn hours_needed(piles: &Vec<i32>, speed: i32) -> i64 {{\n"
            f"    piles.iter().map(|&p| ((p+speed-1)/speed) as i64).sum()\n}}\n"
            f"fn min_eating_speed(piles: Vec<i32>, h: i32) -> i32 {{\n"
            f"    let mut lo=1i32; let mut hi=*piles.iter().max().unwrap();\n"
            f"    while lo<hi {{ let mid=lo+(hi-lo)/2; if hours_needed(&piles,mid)<=h as i64 {{ hi=mid; }} else {{ lo=mid+1; }} }}\n"
            f"    lo{a}\n}}\n")


# ── largest-rectangle-in-histogram (monotonic stack, O(n)) ──────────────────
def _js_lrh(wrong):
    a = " + 1" if wrong else ""
    return (f"function largest_rectangle_area(heights) {{\n"
            f"    const stack=[]; let best=0; const n=heights.length;\n"
            f"    for (let i=0;i<=n;i++) {{\n"
            f"        const h = i===n ? 0 : heights[i];\n"
            f"        while (stack.length && heights[stack[stack.length-1]]>=h) {{\n"
            f"            const top=stack.pop();\n"
            f"            const width = stack.length===0 ? i : i-stack[stack.length-1]-1;\n"
            f"            best = Math.max(best, heights[top]*width);\n"
            f"        }}\n"
            f"        stack.push(i);\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _ts_lrh(wrong):
    a = " + 1" if wrong else ""
    return (f"function largest_rectangle_area(heights: number[]): number {{\n"
            f"    const stack: number[]=[]; let best=0; const n=heights.length;\n"
            f"    for (let i=0;i<=n;i++) {{\n"
            f"        const h = i===n ? 0 : heights[i];\n"
            f"        while (stack.length && heights[stack[stack.length-1]]>=h) {{\n"
            f"            const top=stack.pop() as number;\n"
            f"            const width = stack.length===0 ? i : i-stack[stack.length-1]-1;\n"
            f"            best = Math.max(best, heights[top]*width);\n"
            f"        }}\n"
            f"        stack.push(i);\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _java_lrh(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int largest_rectangle_area(int[] heights) {{\n"
            f"    java.util.Deque<Integer> stack=new java.util.ArrayDeque<>(); long best=0; int n=heights.length;\n"
            f"    for (int i=0;i<=n;i++) {{\n"
            f"        int h = i==n ? 0 : heights[i];\n"
            f"        while (!stack.isEmpty() && heights[stack.peek()]>=h) {{\n"
            f"            int top=stack.pop();\n"
            f"            int width = stack.isEmpty() ? i : i-stack.peek()-1;\n"
            f"            best = Math.max(best, (long)heights[top]*width);\n"
            f"        }}\n"
            f"        stack.push(i);\n"
            f"    }}\n"
            f"    return (int)(best{a});\n}} }}\n")


def _cpp_lrh(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int largest_rectangle_area(std::vector<int> heights) {{\n"
            f"    std::vector<int> stack; long long best=0; int n=heights.size();\n"
            f"    for (int i=0;i<=n;i++) {{\n"
            f"        int h = i==n ? 0 : heights[i];\n"
            f"        while (!stack.empty() && heights[stack.back()]>=h) {{\n"
            f"            int top=stack.back(); stack.pop_back();\n"
            f"            int width = stack.empty() ? i : i-stack.back()-1;\n"
            f"            best = std::max(best, (long long)heights[top]*width);\n"
            f"        }}\n"
            f"        stack.push_back(i);\n"
            f"    }}\n"
            f"    return (int)(best{a});\n}} }};\n")


def _csharp_lrh(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int largest_rectangle_area(int[] heights) {{\n"
            f"    var stack = new System.Collections.Generic.Stack<int>(); long best=0; int n=heights.Length;\n"
            f"    for (int i=0;i<=n;i++) {{\n"
            f"        int h = i==n ? 0 : heights[i];\n"
            f"        while (stack.Count>0 && heights[stack.Peek()]>=h) {{\n"
            f"            int top=stack.Pop();\n"
            f"            int width = stack.Count==0 ? i : i-stack.Peek()-1;\n"
            f"            best = System.Math.Max(best, (long)heights[top]*width);\n"
            f"        }}\n"
            f"        stack.Push(i);\n"
            f"    }}\n"
            f"    return (int)(best{a});\n}} }}\n")


def _perl_lrh(wrong):
    a = " + 1" if wrong else ""
    return (f"sub largest_rectangle_area {{\n"
            f"    my ($heights) = @_;\n"
            f"    my @stack; my $best=0; my $n=scalar(@$heights);\n"
            f"    for (my $i=0;$i<=$n;$i++) {{\n"
            f"        my $h = ($i==$n) ? 0 : $heights->[$i];\n"
            f"        while (@stack && $heights->[$stack[-1]]>=$h) {{\n"
            f"            my $top=pop @stack;\n"
            f"            my $width = (scalar(@stack)==0) ? $i : $i-$stack[-1]-1;\n"
            f"            my $area = $heights->[$top]*$width;\n"
            f"            $best=$area if $area>$best;\n"
            f"        }}\n"
            f"        push @stack, $i;\n"
            f"    }}\n"
            f"    return $best{a};\n}}\n")


def _c_lrh(wrong):
    a = " + 1" if wrong else ""
    return (f"int largest_rectangle_area(AtlasIntArray heights) {{\n"
            f"    int n = heights.size;\n"
            f"    int* stack = (int*)malloc(sizeof(int)*(n+2)); int top=0;\n"
            f"    long long best=0;\n"
            f"    for (int i=0;i<=n;i++) {{\n"
            f"        int h = (i==n) ? 0 : heights.data[i];\n"
            f"        while (top>0 && heights.data[stack[top-1]]>=h) {{\n"
            f"            int t=stack[--top];\n"
            f"            int width = (top==0) ? i : i-stack[top-1]-1;\n"
            f"            long long area = (long long)heights.data[t]*width;\n"
            f"            if (area>best) best=area;\n"
            f"        }}\n"
            f"        stack[top++]=i;\n"
            f"    }}\n"
            f"    free(stack);\n"
            f"    return (int)(best{a});\n}}\n")


def _rust_lrh(wrong):
    a = " + 1" if wrong else ""
    return (f"fn largest_rectangle_area(heights: Vec<i32>) -> i32 {{\n"
            f"    let mut stack: Vec<i32> = Vec::new(); let mut best: i64 = 0; let n = heights.len() as i32;\n"
            f"    for i in 0..=n {{\n"
            f"        let h = if i==n {{ 0 }} else {{ heights[i as usize] }};\n"
            f"        while let Some(&top) = stack.last() {{\n"
            f"            if heights[top as usize] >= h {{\n"
            f"                stack.pop();\n"
            f"                let width = match stack.last() {{ Some(&j) => i-j-1, None => i }};\n"
            f"                let area = heights[top as usize] as i64 * width as i64;\n"
            f"                if area>best {{ best=area; }}\n"
            f"            }} else {{ break; }}\n"
            f"        }}\n"
            f"        stack.push(i);\n"
            f"    }}\n"
            f"    (best{a}) as i32\n}}\n")


# ── last-occurrence (binary search rightmost) ────────────────────────────────
def _js_lastocc(wrong):
    ret = "mid - 1" if wrong else "mid"
    return (f"function last_occurrence(nums, target) {{\n"
            f"    let lo=0, hi=nums.length-1, ans=-1;\n"
            f"    while (lo<=hi) {{\n"
            f"        const mid=(lo+hi)>>1;\n"
            f"        if (nums[mid]===target) {{ ans={ret}; lo=mid+1; }}\n"
            f"        else if (nums[mid]<target) lo=mid+1; else hi=mid-1;\n"
            f"    }}\n"
            f"    return ans;\n}}\n")


def _ts_lastocc(wrong):
    ret = "mid - 1" if wrong else "mid"
    return (f"function last_occurrence(nums: number[], target: number): number {{\n"
            f"    let lo=0, hi=nums.length-1, ans=-1;\n"
            f"    while (lo<=hi) {{\n"
            f"        const mid=(lo+hi)>>1;\n"
            f"        if (nums[mid]===target) {{ ans={ret}; lo=mid+1; }}\n"
            f"        else if (nums[mid]<target) lo=mid+1; else hi=mid-1;\n"
            f"    }}\n"
            f"    return ans;\n}}\n")


def _java_lastocc(wrong):
    ret = "mid - 1" if wrong else "mid"
    return (f"class Solution {{ public int last_occurrence(int[] nums, int target) {{\n"
            f"    int lo=0, hi=nums.length-1, ans=-1;\n"
            f"    while (lo<=hi) {{\n"
            f"        int mid=(lo+hi)>>>1;\n"
            f"        if (nums[mid]==target) {{ ans={ret}; lo=mid+1; }}\n"
            f"        else if (nums[mid]<target) lo=mid+1; else hi=mid-1;\n"
            f"    }}\n"
            f"    return ans;\n}} }}\n")


def _cpp_lastocc(wrong):
    ret = "mid - 1" if wrong else "mid"
    return (f"class Solution {{ public: int last_occurrence(std::vector<int> nums, int target) {{\n"
            f"    int lo=0, hi=(int)nums.size()-1, ans=-1;\n"
            f"    while (lo<=hi) {{\n"
            f"        int mid=lo+(hi-lo)/2;\n"
            f"        if (nums[mid]==target) {{ ans={ret}; lo=mid+1; }}\n"
            f"        else if (nums[mid]<target) lo=mid+1; else hi=mid-1;\n"
            f"    }}\n"
            f"    return ans;\n}} }};\n")


def _csharp_lastocc(wrong):
    ret = "mid - 1" if wrong else "mid"
    return (f"class Solution {{ public static int last_occurrence(int[] nums, int target) {{\n"
            f"    int lo=0, hi=nums.Length-1, ans=-1;\n"
            f"    while (lo<=hi) {{\n"
            f"        int mid=lo+(hi-lo)/2;\n"
            f"        if (nums[mid]==target) {{ ans={ret}; lo=mid+1; }}\n"
            f"        else if (nums[mid]<target) lo=mid+1; else hi=mid-1;\n"
            f"    }}\n"
            f"    return ans;\n}} }}\n")


def _perl_lastocc(wrong):
    ret = "$mid - 1" if wrong else "$mid"
    return (f"sub last_occurrence {{\n"
            f"    my ($nums, $target) = @_;\n"
            f"    my $lo=0; my $hi=scalar(@$nums)-1; my $ans=-1;\n"
            f"    while ($lo<=$hi) {{\n"
            f"        my $mid=int(($lo+$hi)/2);\n"
            f"        if ($nums->[$mid]==$target) {{ $ans={ret}; $lo=$mid+1; }}\n"
            f"        elsif ($nums->[$mid]<$target) {{ $lo=$mid+1; }} else {{ $hi=$mid-1; }}\n"
            f"    }}\n"
            f"    return $ans;\n}}\n")


def _c_lastocc(wrong):
    ret = "mid - 1" if wrong else "mid"
    return (f"int last_occurrence(AtlasIntArray nums, int target) {{\n"
            f"    int lo=0, hi=nums.size-1, ans=-1;\n"
            f"    while (lo<=hi) {{\n"
            f"        int mid=lo+(hi-lo)/2;\n"
            f"        if (nums.data[mid]==target) {{ ans={ret}; lo=mid+1; }}\n"
            f"        else if (nums.data[mid]<target) lo=mid+1; else hi=mid-1;\n"
            f"    }}\n"
            f"    return ans;\n}}\n")


def _rust_lastocc(wrong):
    ret = "mid - 1" if wrong else "mid"
    return (f"fn last_occurrence(nums: Vec<i32>, target: i32) -> i32 {{\n"
            f"    if nums.is_empty() {{ return -1; }}\n"
            f"    let (mut lo, mut hi): (i32,i32) = (0, nums.len() as i32 -1); let mut ans=-1;\n"
            f"    while lo<=hi {{\n"
            f"        let mid=lo+(hi-lo)/2;\n"
            f"        if nums[mid as usize]==target {{ ans={ret}; lo=mid+1; }}\n"
            f"        else if nums[mid as usize]<target {{ lo=mid+1; }} else {{ hi=mid-1; }}\n"
            f"    }}\n"
            f"    ans\n}}\n")


# ── longest-bitonic-subsequence (O(n^2) LIS+LDS DP, max n=800) ─────────────
def _js_lbs(wrong):
    a = " + 1" if wrong else ""
    return (f"function lbs(nums) {{\n"
            f"    const n=nums.length; const inc=new Array(n).fill(1), dec=new Array(n).fill(1);\n"
            f"    for (let i=0;i<n;i++) for (let j=0;j<i;j++) if (nums[j]<nums[i]) inc[i]=Math.max(inc[i], inc[j]+1);\n"
            f"    for (let i=n-1;i>=0;i--) for (let j=n-1;j>i;j--) if (nums[j]<nums[i]) dec[i]=Math.max(dec[i], dec[j]+1);\n"
            f"    let best=0; for (let i=0;i<n;i++) best=Math.max(best, inc[i]+dec[i]-1);\n"
            f"    return best{a};\n}}\n")


def _ts_lbs(wrong):
    a = " + 1" if wrong else ""
    return (f"function lbs(nums: number[]): number {{\n"
            f"    const n=nums.length; const inc: number[]=new Array(n).fill(1), dec: number[]=new Array(n).fill(1);\n"
            f"    for (let i=0;i<n;i++) for (let j=0;j<i;j++) if (nums[j]<nums[i]) inc[i]=Math.max(inc[i], inc[j]+1);\n"
            f"    for (let i=n-1;i>=0;i--) for (let j=n-1;j>i;j--) if (nums[j]<nums[i]) dec[i]=Math.max(dec[i], dec[j]+1);\n"
            f"    let best=0; for (let i=0;i<n;i++) best=Math.max(best, inc[i]+dec[i]-1);\n"
            f"    return best{a};\n}}\n")


def _java_lbs(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int lbs(int[] nums) {{\n"
            f"    int n=nums.length; int[] inc=new int[n], dec=new int[n];\n"
            f"    java.util.Arrays.fill(inc,1); java.util.Arrays.fill(dec,1);\n"
            f"    for (int i=0;i<n;i++) for (int j=0;j<i;j++) if (nums[j]<nums[i]) inc[i]=Math.max(inc[i], inc[j]+1);\n"
            f"    for (int i=n-1;i>=0;i--) for (int j=n-1;j>i;j--) if (nums[j]<nums[i]) dec[i]=Math.max(dec[i], dec[j]+1);\n"
            f"    int best=0; for (int i=0;i<n;i++) best=Math.max(best, inc[i]+dec[i]-1);\n"
            f"    return best{a};\n}} }}\n")


def _cpp_lbs(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int lbs(std::vector<int> nums) {{\n"
            f"    int n=nums.size(); std::vector<int> inc(n,1), dec(n,1);\n"
            f"    for (int i=0;i<n;i++) for (int j=0;j<i;j++) if (nums[j]<nums[i]) inc[i]=std::max(inc[i], inc[j]+1);\n"
            f"    for (int i=n-1;i>=0;i--) for (int j=n-1;j>i;j--) if (nums[j]<nums[i]) dec[i]=std::max(dec[i], dec[j]+1);\n"
            f"    int best=0; for (int i=0;i<n;i++) best=std::max(best, inc[i]+dec[i]-1);\n"
            f"    return best{a};\n}} }};\n")


def _csharp_lbs(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int lbs(int[] nums) {{\n"
            f"    int n=nums.Length; int[] inc=new int[n], dec=new int[n];\n"
            f"    for (int i=0;i<n;i++) {{ inc[i]=1; dec[i]=1; }}\n"
            f"    for (int i=0;i<n;i++) for (int j=0;j<i;j++) if (nums[j]<nums[i]) inc[i]=System.Math.Max(inc[i], inc[j]+1);\n"
            f"    for (int i=n-1;i>=0;i--) for (int j=n-1;j>i;j--) if (nums[j]<nums[i]) dec[i]=System.Math.Max(dec[i], dec[j]+1);\n"
            f"    int best=0; for (int i=0;i<n;i++) best=System.Math.Max(best, inc[i]+dec[i]-1);\n"
            f"    return best{a};\n}} }}\n")


def _perl_lbs(wrong):
    a = " + 1" if wrong else ""
    return (f"sub lbs {{\n"
            f"    my ($nums) = @_;\n"
            f"    my $n = scalar(@$nums); my @inc = (1) x $n; my @dec = (1) x $n;\n"
            f"    for (my $i=0;$i<$n;$i++) {{ for (my $j=0;$j<$i;$j++) {{ if ($nums->[$j]<$nums->[$i] && $inc[$j]+1>$inc[$i]) {{ $inc[$i]=$inc[$j]+1; }} }} }}\n"
            f"    for (my $i=$n-1;$i>=0;$i--) {{ for (my $j=$n-1;$j>$i;$j--) {{ if ($nums->[$j]<$nums->[$i] && $dec[$j]+1>$dec[$i]) {{ $dec[$i]=$dec[$j]+1; }} }} }}\n"
            f"    my $best=0; for (my $i=0;$i<$n;$i++) {{ my $v=$inc[$i]+$dec[$i]-1; $best=$v if $v>$best; }}\n"
            f"    return $best{a};\n}}\n")


def _c_lbs(wrong):
    a = " + 1" if wrong else ""
    return (f"int lbs(AtlasIntArray nums) {{\n"
            f"    int n = nums.size;\n"
            f"    int* inc = (int*)malloc(sizeof(int)*n); int* dec = (int*)malloc(sizeof(int)*n);\n"
            f"    for (int i=0;i<n;i++) {{ inc[i]=1; dec[i]=1; }}\n"
            f"    for (int i=0;i<n;i++) for (int j=0;j<i;j++) if (nums.data[j]<nums.data[i] && inc[j]+1>inc[i]) inc[i]=inc[j]+1;\n"
            f"    for (int i=n-1;i>=0;i--) for (int j=n-1;j>i;j--) if (nums.data[j]<nums.data[i] && dec[j]+1>dec[i]) dec[i]=dec[j]+1;\n"
            f"    int best=0; for (int i=0;i<n;i++) {{ int v=inc[i]+dec[i]-1; if (v>best) best=v; }}\n"
            f"    free(inc); free(dec);\n"
            f"    return best{a};\n}}\n")


def _rust_lbs(wrong):
    a = " + 1" if wrong else ""
    return (f"fn lbs(nums: Vec<i32>) -> i32 {{\n"
            f"    let n = nums.len(); let mut inc = vec![1i32; n]; let mut dec = vec![1i32; n];\n"
            f"    for i in 0..n {{ for j in 0..i {{ if nums[j]<nums[i] && inc[j]+1>inc[i] {{ inc[i]=inc[j]+1; }} }} }}\n"
            f"    for i in (0..n).rev() {{ for j in (i+1..n).rev() {{ if nums[j]<nums[i] && dec[j]+1>dec[i] {{ dec[i]=dec[j]+1; }} }} }}\n"
            f"    let mut best=0; for i in 0..n {{ let v=inc[i]+dec[i]-1; if v>best {{ best=v; }} }}\n"
            f"    best{a}\n}}\n")


# ── max-consecutive-ones-with-k-flips (sliding window) ──────────────────────
def _js_maxconsflip(wrong):
    a = " + 1" if wrong else ""
    return (f"function longest_ones(nums, k) {{\n"
            f"    let left=0, zeros=0, best=0;\n"
            f"    for (let right=0;right<nums.length;right++) {{\n"
            f"        if (nums[right]===0) zeros++;\n"
            f"        while (zeros>k) {{ if (nums[left]===0) zeros--; left++; }}\n"
            f"        best = Math.max(best, right-left+1);\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _ts_maxconsflip(wrong):
    a = " + 1" if wrong else ""
    return (f"function longest_ones(nums: number[], k: number): number {{\n"
            f"    let left=0, zeros=0, best=0;\n"
            f"    for (let right=0;right<nums.length;right++) {{\n"
            f"        if (nums[right]===0) zeros++;\n"
            f"        while (zeros>k) {{ if (nums[left]===0) zeros--; left++; }}\n"
            f"        best = Math.max(best, right-left+1);\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _java_maxconsflip(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int longest_ones(int[] nums, int k) {{\n"
            f"    int left=0, zeros=0, best=0;\n"
            f"    for (int right=0;right<nums.length;right++) {{\n"
            f"        if (nums[right]==0) zeros++;\n"
            f"        while (zeros>k) {{ if (nums[left]==0) zeros--; left++; }}\n"
            f"        best = Math.max(best, right-left+1);\n"
            f"    }}\n"
            f"    return best{a};\n}} }}\n")


def _cpp_maxconsflip(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int longest_ones(std::vector<int> nums, int k) {{\n"
            f"    int left=0, zeros=0, best=0;\n"
            f"    for (int right=0;right<(int)nums.size();right++) {{\n"
            f"        if (nums[right]==0) zeros++;\n"
            f"        while (zeros>k) {{ if (nums[left]==0) zeros--; left++; }}\n"
            f"        best = std::max(best, right-left+1);\n"
            f"    }}\n"
            f"    return best{a};\n}} }};\n")


def _csharp_maxconsflip(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int longest_ones(int[] nums, int k) {{\n"
            f"    int left=0, zeros=0, best=0;\n"
            f"    for (int right=0;right<nums.Length;right++) {{\n"
            f"        if (nums[right]==0) zeros++;\n"
            f"        while (zeros>k) {{ if (nums[left]==0) zeros--; left++; }}\n"
            f"        best = System.Math.Max(best, right-left+1);\n"
            f"    }}\n"
            f"    return best{a};\n}} }}\n")


def _perl_maxconsflip(wrong):
    a = " + 1" if wrong else ""
    return (f"sub longest_ones {{\n"
            f"    my ($nums, $k) = @_;\n"
            f"    my $left=0; my $zeros=0; my $best=0;\n"
            f"    for (my $right=0;$right<scalar(@$nums);$right++) {{\n"
            f"        $zeros++ if $nums->[$right]==0;\n"
            f"        while ($zeros>$k) {{ $zeros-- if $nums->[$left]==0; $left++; }}\n"
            f"        my $len = $right-$left+1; $best=$len if $len>$best;\n"
            f"    }}\n"
            f"    return $best{a};\n}}\n")


def _c_maxconsflip(wrong):
    a = " + 1" if wrong else ""
    return (f"int longest_ones(AtlasIntArray nums, int k) {{\n"
            f"    int left=0, zeros=0, best=0;\n"
            f"    for (int right=0;right<nums.size;right++) {{\n"
            f"        if (nums.data[right]==0) zeros++;\n"
            f"        while (zeros>k) {{ if (nums.data[left]==0) zeros--; left++; }}\n"
            f"        int len = right-left+1; if (len>best) best=len;\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _rust_maxconsflip(wrong):
    a = " + 1" if wrong else ""
    return (f"fn longest_ones(nums: Vec<i32>, k: i32) -> i32 {{\n"
            f"    let mut left=0i32; let mut zeros=0i32; let mut best=0i32;\n"
            f"    for right in 0..nums.len() as i32 {{\n"
            f"        if nums[right as usize]==0 {{ zeros+=1; }}\n"
            f"        while zeros>k {{ if nums[left as usize]==0 {{ zeros-=1; }} left+=1; }}\n"
            f"        let len = right-left+1; if len>best {{ best=len; }}\n"
            f"    }}\n"
            f"    best{a}\n}}\n")


# ── max-sum-subarray-fixed-k (sliding window sum) ───────────────────────────
def _js_maxsumk(wrong):
    a = " + 1" if wrong else ""
    return (f"function max_sum_fixed_k(nums, k) {{\n"
            f"    let sum=0; for (let i=0;i<k;i++) sum+=nums[i];\n"
            f"    let best=sum;\n"
            f"    for (let i=k;i<nums.length;i++) {{ sum += nums[i]-nums[i-k]; best=Math.max(best,sum); }}\n"
            f"    return best{a};\n}}\n")


def _ts_maxsumk(wrong):
    a = " + 1" if wrong else ""
    return (f"function max_sum_fixed_k(nums: number[], k: number): number {{\n"
            f"    let sum=0; for (let i=0;i<k;i++) sum+=nums[i];\n"
            f"    let best=sum;\n"
            f"    for (let i=k;i<nums.length;i++) {{ sum += nums[i]-nums[i-k]; best=Math.max(best,sum); }}\n"
            f"    return best{a};\n}}\n")


def _java_maxsumk(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int max_sum_fixed_k(int[] nums, int k) {{\n"
            f"    long sum=0; for (int i=0;i<k;i++) sum+=nums[i];\n"
            f"    long best=sum;\n"
            f"    for (int i=k;i<nums.length;i++) {{ sum += nums[i]-nums[i-k]; best=Math.max(best,sum); }}\n"
            f"    return (int)(best{a});\n}} }}\n")


def _cpp_maxsumk(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int max_sum_fixed_k(std::vector<int> nums, int k) {{\n"
            f"    long long sum=0; for (int i=0;i<k;i++) sum+=nums[i];\n"
            f"    long long best=sum;\n"
            f"    for (int i=k;i<(int)nums.size();i++) {{ sum += nums[i]-nums[i-k]; best=std::max(best,sum); }}\n"
            f"    return (int)(best{a});\n}} }};\n")


def _csharp_maxsumk(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int max_sum_fixed_k(int[] nums, int k) {{\n"
            f"    long sum=0; for (int i=0;i<k;i++) sum+=nums[i];\n"
            f"    long best=sum;\n"
            f"    for (int i=k;i<nums.Length;i++) {{ sum += nums[i]-nums[i-k]; best=System.Math.Max(best,sum); }}\n"
            f"    return (int)(best{a});\n}} }}\n")


def _perl_maxsumk(wrong):
    a = " + 1" if wrong else ""
    return (f"sub max_sum_fixed_k {{\n"
            f"    my ($nums, $k) = @_;\n"
            f"    my $sum=0; for (my $i=0;$i<$k;$i++) {{ $sum+=$nums->[$i]; }}\n"
            f"    my $best=$sum;\n"
            f"    for (my $i=$k;$i<scalar(@$nums);$i++) {{ $sum += $nums->[$i]-$nums->[$i-$k]; $best=$sum if $sum>$best; }}\n"
            f"    return $best{a};\n}}\n")


def _c_maxsumk(wrong):
    a = " + 1" if wrong else ""
    return (f"int max_sum_fixed_k(AtlasIntArray nums, int k) {{\n"
            f"    long long sum=0; for (int i=0;i<k;i++) sum+=nums.data[i];\n"
            f"    long long best=sum;\n"
            f"    for (int i=k;i<nums.size;i++) {{ sum += nums.data[i]-nums.data[i-k]; if (sum>best) best=sum; }}\n"
            f"    return (int)(best{a});\n}}\n")


def _rust_maxsumk(wrong):
    a = " + 1" if wrong else ""
    return (f"fn max_sum_fixed_k(nums: Vec<i32>, k: i32) -> i32 {{\n"
            f"    let k = k as usize;\n"
            f"    let mut sum: i64 = nums[0..k].iter().map(|&x| x as i64).sum();\n"
            f"    let mut best = sum;\n"
            f"    for i in k..nums.len() {{ sum += (nums[i]-nums[i-k]) as i64; if sum>best {{ best=sum; }} }}\n"
            f"    (best{a}) as i32\n}}\n")


_BUILDERS = {
    "job-scheduling": {"javascript": _js_jobsched, "typescript": _ts_jobsched, "java": _java_jobsched, "cpp": _cpp_jobsched,
                       "csharp": _csharp_jobsched, "perl": _perl_jobsched, "c": _c_jobsched, "rust": _rust_jobsched},
    "jump-game-ii-min-jumps": {"javascript": _js_jumpii, "typescript": _ts_jumpii, "java": _java_jumpii, "cpp": _cpp_jumpii,
                              "csharp": _csharp_jumpii, "perl": _perl_jumpii, "c": _c_jumpii, "rust": _rust_jumpii},
    "kth-largest-element": {"javascript": _js_kthlarge, "typescript": _ts_kthlarge, "java": _java_kthlarge, "cpp": _cpp_kthlarge,
                            "csharp": _csharp_kthlarge, "perl": _perl_kthlarge, "c": _c_kthlarge, "rust": _rust_kthlarge},
    "koko-eating-bananas": {"javascript": _js_koko, "typescript": _ts_koko, "java": _java_koko, "cpp": _cpp_koko,
                            "csharp": _csharp_koko, "perl": _perl_koko, "c": _c_koko, "rust": _rust_koko},
    "largest-rectangle-in-histogram": {"javascript": _js_lrh, "typescript": _ts_lrh, "java": _java_lrh, "cpp": _cpp_lrh,
                                       "csharp": _csharp_lrh, "perl": _perl_lrh, "c": _c_lrh, "rust": _rust_lrh},
    "last-occurrence": {"javascript": _js_lastocc, "typescript": _ts_lastocc, "java": _java_lastocc, "cpp": _cpp_lastocc,
                        "csharp": _csharp_lastocc, "perl": _perl_lastocc, "c": _c_lastocc, "rust": _rust_lastocc},
    "longest-bitonic-subsequence": {"javascript": _js_lbs, "typescript": _ts_lbs, "java": _java_lbs, "cpp": _cpp_lbs,
                                    "csharp": _csharp_lbs, "perl": _perl_lbs, "c": _c_lbs, "rust": _rust_lbs},
    "max-consecutive-ones-with-k-flips": {"javascript": _js_maxconsflip, "typescript": _ts_maxconsflip, "java": _java_maxconsflip, "cpp": _cpp_maxconsflip,
                                          "csharp": _csharp_maxconsflip, "perl": _perl_maxconsflip, "c": _c_maxconsflip, "rust": _rust_maxconsflip},
    "max-sum-subarray-fixed-k": {"javascript": _js_maxsumk, "typescript": _ts_maxsumk, "java": _java_maxsumk, "cpp": _cpp_maxsumk,
                                "csharp": _csharp_maxsumk, "perl": _perl_maxsumk, "c": _c_maxsumk, "rust": _rust_maxsumk},
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
            "detail": f"{n_pass}/{len(cases)} correct, wrong rejected on {len(cases) - n_wrong_pass}/{len(cases)}",
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
            print(f"[{status}] {lang:10s}(function) {pid:34s} {r['outcome']:18s} {r['detail'][:130]}", flush=True)
            if r["outcome"] == "verified":
                ledger.record_cell(con, problem_id=pid, language=lang, mode="function",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=f"{lang}-function-mega2-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
