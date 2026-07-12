"""Scales top-k-frequent-elements, subarray-sum-equals-k,
daily-temperatures, next-greater-element, number-of-islands, flood-fill,
longest-substring-without-repeating, valid-palindrome-string,
group-anagrams-count, three-sum-count-triplets (Function Mode) across the
8 working languages.
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


# ── top-k-frequent-elements (sort by -freq, then value ascending) ──────────
def _js_topk(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "function top_k_frequent(nums, k) {\n"
        "    const freq = {};\n"
        "    for (const x of nums) freq[x] = (freq[x]||0) + 1;\n"
        "    const keys = Object.keys(freq).map(Number);\n"
        "    keys.sort((a,b) => freq[b]-freq[a] || a-b);\n"
        f"    return keys.slice(0,k){a};\n"
        "}\n"
    )


def _ts_topk(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "function top_k_frequent(nums: number[], k: number): number[] {\n"
        "    const freq: Record<number, number> = {};\n"
        "    for (const x of nums) freq[x] = (freq[x]||0) + 1;\n"
        "    const keys = Object.keys(freq).map(Number);\n"
        "    keys.sort((a,b) => freq[b]-freq[a] || a-b);\n"
        f"    return keys.slice(0,k){a};\n"
        "}\n"
    )


def _java_topk(wrong):
    incr = "for (int i=0;i<out.length;i++) out[i]++;\n        " if wrong else ""
    return (
        "class Solution { public int[] top_k_frequent(int[] nums, int k) {\n"
        "    java.util.Map<Integer,Integer> freq = new java.util.HashMap<>();\n"
        "    for (int x: nums) freq.merge(x, 1, Integer::sum);\n"
        "    java.util.List<Integer> keys = new java.util.ArrayList<>(freq.keySet());\n"
        "    keys.sort((a,b) -> { int c = freq.get(b)-freq.get(a); return c != 0 ? c : a-b; });\n"
        "    int[] out = new int[k];\n"
        "    for (int i=0;i<k;i++) out[i] = keys.get(i);\n"
        f"        {incr}return out;\n"
        "} }\n"
    )


def _cpp_topk(wrong):
    incr = "for (auto& x : out) x++;\n    " if wrong else ""
    return (
        "class Solution { public: std::vector<int> top_k_frequent(std::vector<int> nums, int k) {\n"
        "    std::unordered_map<int,int> freq;\n"
        "    for (int x : nums) freq[x]++;\n"
        "    std::vector<int> keys;\n"
        "    for (auto& p : freq) keys.push_back(p.first);\n"
        "    std::sort(keys.begin(), keys.end(), [&](int a, int b) { if (freq[a]!=freq[b]) return freq[a]>freq[b]; return a<b; });\n"
        "    std::vector<int> out(keys.begin(), keys.begin()+k);\n"
        f"    {incr}return out;\n"
        "} };\n"
    )


def _csharp_topk(wrong):
    incr = "for (int i=0;i<outArr.Length;i++) outArr[i]++;\n        " if wrong else ""
    return (
        "class Solution { public static int[] top_k_frequent(int[] nums, int k) {\n"
        "    var freq = new System.Collections.Generic.Dictionary<int,int>();\n"
        "    foreach (int x in nums) { if (!freq.ContainsKey(x)) freq[x]=0; freq[x]++; }\n"
        "    var keys = new System.Collections.Generic.List<int>(freq.Keys);\n"
        "    keys.Sort((a,b) => freq[b] != freq[a] ? freq[b]-freq[a] : a-b);\n"
        "    var outArr = keys.GetRange(0, k).ToArray();\n"
        f"        {incr}return outArr;\n"
        "} }\n"
    )


def _perl_topk(wrong):
    incr = "@out = map { $_ + 1 } @out;\n    " if wrong else ""
    return (
        "sub top_k_frequent {\n"
        "    my ($nums, $k) = @_;\n"
        "    my %freq;\n"
        "    foreach my $x (@$nums) { $freq{$x}++; }\n"
        "    my @keys = sort { $freq{$b} <=> $freq{$a} || $a <=> $b } keys %freq;\n"
        "    my @out = @keys[0..$k-1];\n"
        f"    {incr}return \\@out;\n"
        "}\n"
    )


def _c_topk(wrong):
    incr = "for (int i=0;i<k;i++) out[i]++;\n    " if wrong else ""
    return (
        "int cmp_topk_key, cmp_topk_freq[200002];\n"
        "int cmp_topk(const void* a, const void* b) {\n"
        "    int va = *(const int*)a, vb = *(const int*)b;\n"
        "    int fa = cmp_topk_freq[va+100000], fb = cmp_topk_freq[vb+100000];\n"
        "    if (fa != fb) return fb - fa;\n"
        "    return va - vb;\n"
        "}\n"
        "AtlasIntArray top_k_frequent(AtlasIntArray nums, int k) {\n"
        "    for (int i=0;i<200002;i++) cmp_topk_freq[i]=0;\n"
        "    int* uniq = (int*)malloc(sizeof(int)*(nums.size>0?nums.size:1)); int uc=0;\n"
        "    for (int i=0;i<nums.size;i++) {\n"
        "        int v = nums.data[i];\n"
        "        if (cmp_topk_freq[v+100000] == 0) uniq[uc++] = v;\n"
        "        cmp_topk_freq[v+100000]++;\n"
        "    }\n"
        "    qsort(uniq, uc, sizeof(int), cmp_topk);\n"
        "    int* out = (int*)malloc(sizeof(int)*k);\n"
        "    for (int i=0;i<k;i++) out[i] = uniq[i];\n"
        f"    {incr}AtlasIntArray result; result.size = k; result.data = out;\n"
        "    free(uniq);\n"
        "    return result;\n"
        "}\n"
    )


def _rust_topk(wrong):
    incr = "for x in out.iter_mut() { *x += 1; }\n    " if wrong else ""
    return (
        "use std::collections::HashMap;\n"
        "fn top_k_frequent(nums: Vec<i32>, k: i32) -> Vec<i32> {\n"
        "    let mut freq: HashMap<i32, i32> = HashMap::new();\n"
        "    for x in nums.iter() { *freq.entry(*x).or_insert(0) += 1; }\n"
        "    let mut keys: Vec<i32> = freq.keys().cloned().collect();\n"
        "    keys.sort_by(|a, b| { let fa = freq[a]; let fb = freq[b]; if fa != fb { fb.cmp(&fa) } else { a.cmp(b) } });\n"
        "    let mut out: Vec<i32> = keys.into_iter().take(k as usize).collect();\n"
        f"    {incr}out\n"
        "}\n"
    )


# ── subarray-sum-equals-k ────────────────────────────────────────────────────
def _js_subarr_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "function subarray_sum(nums, k) {\n"
        "    const seen = {0: 1}; let sum = 0, count = 0;\n"
        "    for (const x of nums) { sum += x; count += seen[sum-k] || 0; seen[sum] = (seen[sum]||0) + 1; }\n"
        f"    return count{a};\n"
        "}\n"
    )


def _ts_subarr_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "function subarray_sum(nums: number[], k: number): number {\n"
        "    const seen: Record<number, number> = {0: 1}; let sum = 0, count = 0;\n"
        "    for (const x of nums) { sum += x; count += seen[sum-k] || 0; seen[sum] = (seen[sum]||0) + 1; }\n"
        f"    return count{a};\n"
        "}\n"
    )


def _java_subarr_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public int subarray_sum(int[] nums, int k) {\n"
        "    java.util.Map<Integer,Integer> seen = new java.util.HashMap<>(); seen.put(0,1);\n"
        "    int sum=0, count=0;\n"
        "    for (int x: nums) { sum += x; count += seen.getOrDefault(sum-k, 0); seen.merge(sum, 1, Integer::sum); }\n"
        f"    return count{a};\n"
        "} }\n"
    )


def _cpp_subarr_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public: int subarray_sum(std::vector<int> nums, int k) {\n"
        "    std::unordered_map<int,int> seen; seen[0]=1;\n"
        "    int sum=0, count=0;\n"
        "    for (int x : nums) { sum += x; auto it = seen.find(sum-k); if (it != seen.end()) count += it->second; seen[sum]++; }\n"
        f"    return count{a};\n"
        "} };\n"
    )


def _csharp_subarr_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public static int subarray_sum(int[] nums, int k) {\n"
        "    var seen = new System.Collections.Generic.Dictionary<int,int>(); seen[0]=1;\n"
        "    int sum=0, count=0;\n"
        "    foreach (int x in nums) { sum += x; if (seen.ContainsKey(sum-k)) count += seen[sum-k]; if (!seen.ContainsKey(sum)) seen[sum]=0; seen[sum]++; }\n"
        f"    return count{a};\n"
        "} }\n"
    )


def _perl_subarr_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub subarray_sum {\n"
        "    my ($nums, $k) = @_;\n"
        "    my %seen = (0 => 1); my $sum = 0; my $count = 0;\n"
        "    foreach my $x (@$nums) {\n"
        "        $sum += $x;\n"
        "        $count += $seen{$sum-$k} if exists $seen{$sum-$k};\n"
        "        $seen{$sum}++;\n"
        "    }\n"
        f"    return $count{a};\n"
        "}\n"
    )


def _c_subarr_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "int subarray_sum(AtlasIntArray nums, int k) {\n"
        "    int n = nums.size;\n"
        "    int count = 0;\n"
        "    int* prefix = (int*)malloc(sizeof(int)*(n+1));\n"
        "    prefix[0] = 0;\n"
        "    for (int i=0;i<n;i++) prefix[i+1] = prefix[i] + nums.data[i];\n"
        "    for (int i=0;i<n;i++) for (int j=i;j<n;j++) if (prefix[j+1]-prefix[i]==k) count++;\n"
        "    free(prefix);\n"
        f"    return count{a};\n"
        "}\n"
    )


def _rust_subarr_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::collections::HashMap;\n"
        "fn subarray_sum(nums: Vec<i32>, k: i32) -> i32 {\n"
        "    let mut seen: HashMap<i32, i32> = HashMap::new(); seen.insert(0, 1);\n"
        "    let mut sum = 0; let mut count = 0;\n"
        "    for x in nums.iter() {\n"
        "        sum += x;\n"
        "        if let Some(&c) = seen.get(&(sum-k)) { count += c; }\n"
        "        *seen.entry(sum).or_insert(0) += 1;\n"
        "    }\n"
        f"    count{a}\n"
        "}\n"
    )


# ── daily-temperatures ───────────────────────────────────────────────────────
def _js_daily_temp(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "function daily_temperatures(temps) {\n"
        "    const n = temps.length; const out = new Array(n).fill(0); const stack = [];\n"
        "    for (let i=0;i<n;i++) {\n"
        "        while (stack.length && temps[stack[stack.length-1]] < temps[i]) { const j = stack.pop(); out[j] = i-j; }\n"
        "        stack.push(i);\n"
        "    }\n"
        f"    return out{a};\n"
        "}\n"
    )


def _ts_daily_temp(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "function daily_temperatures(temps: number[]): number[] {\n"
        "    const n = temps.length; const out: number[] = new Array(n).fill(0); const stack: number[] = [];\n"
        "    for (let i=0;i<n;i++) {\n"
        "        while (stack.length && temps[stack[stack.length-1]] < temps[i]) { const j = stack.pop() as number; out[j] = i-j; }\n"
        "        stack.push(i);\n"
        "    }\n"
        f"    return out{a};\n"
        "}\n"
    )


def _java_daily_temp(wrong):
    incr = "for (int i=0;i<n;i++) out[i]++;\n        " if wrong else ""
    return (
        "class Solution { public int[] daily_temperatures(int[] temps) {\n"
        "    int n = temps.length; int[] out = new int[n];\n"
        "    java.util.Deque<Integer> stack = new java.util.ArrayDeque<>();\n"
        "    for (int i=0;i<n;i++) {\n"
        "        while (!stack.isEmpty() && temps[stack.peek()] < temps[i]) { int j = stack.pop(); out[j] = i-j; }\n"
        "        stack.push(i);\n"
        "    }\n"
        f"        {incr}return out;\n"
        "} }\n"
    )


def _cpp_daily_temp(wrong):
    incr = "for (int i=0;i<n;i++) out[i]++;\n    " if wrong else ""
    return (
        "class Solution { public: std::vector<int> daily_temperatures(std::vector<int> temps) {\n"
        "    int n = temps.size(); std::vector<int> out(n, 0);\n"
        "    std::vector<int> stack;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        while (!stack.empty() && temps[stack.back()] < temps[i]) { int j = stack.back(); stack.pop_back(); out[j] = i-j; }\n"
        "        stack.push_back(i);\n"
        "    }\n"
        f"    {incr}return out;\n"
        "} };\n"
    )


def _csharp_daily_temp(wrong):
    incr = "for (int i=0;i<n;i++) outArr[i]++;\n        " if wrong else ""
    return (
        "class Solution { public static int[] daily_temperatures(int[] temps) {\n"
        "    int n = temps.Length; int[] outArr = new int[n];\n"
        "    var stack = new System.Collections.Generic.Stack<int>();\n"
        "    for (int i=0;i<n;i++) {\n"
        "        while (stack.Count > 0 && temps[stack.Peek()] < temps[i]) { int j = stack.Pop(); outArr[j] = i-j; }\n"
        "        stack.Push(i);\n"
        "    }\n"
        f"        {incr}return outArr;\n"
        "} }\n"
    )


def _perl_daily_temp(wrong):
    incr = "for (my $i=0;$i<$n;$i++) { $out[$i]++; }\n    " if wrong else ""
    return (
        "sub daily_temperatures {\n"
        "    my ($temps) = @_;\n"
        "    my $n = scalar(@$temps); my @out = (0) x $n; my @stack;\n"
        "    for (my $i=0;$i<$n;$i++) {\n"
        "        while (@stack && $temps->[$stack[-1]] < $temps->[$i]) { my $j = pop @stack; $out[$j] = $i-$j; }\n"
        "        push @stack, $i;\n"
        "    }\n"
        f"    {incr}return \\@out;\n"
        "}\n"
    )


def _c_daily_temp(wrong):
    incr = "for (int i=0;i<n;i++) out[i]++;\n    " if wrong else ""
    return (
        "AtlasIntArray daily_temperatures(AtlasIntArray temps) {\n"
        "    int n = temps.size;\n"
        "    int* out = (int*)calloc(n>0?n:1, sizeof(int));\n"
        "    int* stack = (int*)malloc(sizeof(int)*(n>0?n:1)); int top = 0;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        while (top > 0 && temps.data[stack[top-1]] < temps.data[i]) { int j = stack[--top]; out[j] = i-j; }\n"
        "        stack[top++] = i;\n"
        "    }\n"
        f"    {incr}free(stack);\n"
        "    AtlasIntArray result; result.size = n; result.data = out;\n"
        "    return result;\n"
        "}\n"
    )


def _rust_daily_temp(wrong):
    incr = "for x in out.iter_mut() { *x += 1; }\n    " if wrong else ""
    return (
        "fn daily_temperatures(temps: Vec<i32>) -> Vec<i32> {\n"
        "    let n = temps.len(); let mut out = vec![0i32; n]; let mut stack: Vec<usize> = Vec::new();\n"
        "    for i in 0..n {\n"
        "        while let Some(&j) = stack.last() { if temps[j] < temps[i] { out[j] = (i-j) as i32; stack.pop(); } else { break; } }\n"
        "        stack.push(i);\n"
        "    }\n"
        f"    {incr}out\n"
        "}\n"
    )


# ── next-greater-element (non-circular, -1 if none) ─────────────────────────
def _js_next_greater(wrong):
    a = ".map(x => x === -1 ? -1 : x + 1)" if wrong else ""
    return (
        "function next_greater_element(nums) {\n"
        "    const n = nums.length; const out = new Array(n).fill(-1); const stack = [];\n"
        "    for (let i=0;i<n;i++) {\n"
        "        while (stack.length && nums[stack[stack.length-1]] < nums[i]) { out[stack.pop()] = nums[i]; }\n"
        "        stack.push(i);\n"
        "    }\n"
        f"    return out{a};\n"
        "}\n"
    )


def _ts_next_greater(wrong):
    a = ".map(x => x === -1 ? -1 : x + 1)" if wrong else ""
    return (
        "function next_greater_element(nums: number[]): number[] {\n"
        "    const n = nums.length; const out: number[] = new Array(n).fill(-1); const stack: number[] = [];\n"
        "    for (let i=0;i<n;i++) {\n"
        "        while (stack.length && nums[stack[stack.length-1]] < nums[i]) { out[stack.pop() as number] = nums[i]; }\n"
        "        stack.push(i);\n"
        "    }\n"
        f"    return out{a};\n"
        "}\n"
    )


def _java_next_greater(wrong):
    incr = "for (int i=0;i<n;i++) if (out[i] != -1) out[i]++;\n        " if wrong else ""
    return (
        "class Solution { public int[] next_greater_element(int[] nums) {\n"
        "    int n = nums.length; int[] out = new int[n]; java.util.Arrays.fill(out, -1);\n"
        "    java.util.Deque<Integer> stack = new java.util.ArrayDeque<>();\n"
        "    for (int i=0;i<n;i++) {\n"
        "        while (!stack.isEmpty() && nums[stack.peek()] < nums[i]) out[stack.pop()] = nums[i];\n"
        "        stack.push(i);\n"
        "    }\n"
        f"        {incr}return out;\n"
        "} }\n"
    )


def _cpp_next_greater(wrong):
    incr = "for (int i=0;i<n;i++) if (out[i] != -1) out[i]++;\n    " if wrong else ""
    return (
        "class Solution { public: std::vector<int> next_greater_element(std::vector<int> nums) {\n"
        "    int n = nums.size(); std::vector<int> out(n, -1);\n"
        "    std::vector<int> stack;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        while (!stack.empty() && nums[stack.back()] < nums[i]) { out[stack.back()] = nums[i]; stack.pop_back(); }\n"
        "        stack.push_back(i);\n"
        "    }\n"
        f"    {incr}return out;\n"
        "} };\n"
    )


def _csharp_next_greater(wrong):
    incr = "for (int i=0;i<n;i++) if (outArr[i] != -1) outArr[i]++;\n        " if wrong else ""
    return (
        "class Solution { public static int[] next_greater_element(int[] nums) {\n"
        "    int n = nums.Length; int[] outArr = new int[n]; for (int i=0;i<n;i++) outArr[i]=-1;\n"
        "    var stack = new System.Collections.Generic.Stack<int>();\n"
        "    for (int i=0;i<n;i++) {\n"
        "        while (stack.Count > 0 && nums[stack.Peek()] < nums[i]) outArr[stack.Pop()] = nums[i];\n"
        "        stack.Push(i);\n"
        "    }\n"
        f"        {incr}return outArr;\n"
        "} }\n"
    )


def _perl_next_greater(wrong):
    incr = "for (my $i=0;$i<$n;$i++) { $out[$i]++ if $out[$i] != -1; }\n    " if wrong else ""
    return (
        "sub next_greater_element {\n"
        "    my ($nums) = @_;\n"
        "    my $n = scalar(@$nums); my @out = (-1) x $n; my @stack;\n"
        "    for (my $i=0;$i<$n;$i++) {\n"
        "        while (@stack && $nums->[$stack[-1]] < $nums->[$i]) { $out[pop @stack] = $nums->[$i]; }\n"
        "        push @stack, $i;\n"
        "    }\n"
        f"    {incr}return \\@out;\n"
        "}\n"
    )


def _c_next_greater(wrong):
    incr = "for (int i=0;i<n;i++) if (out[i] != -1) out[i]++;\n    " if wrong else ""
    return (
        "AtlasIntArray next_greater_element(AtlasIntArray nums) {\n"
        "    int n = nums.size;\n"
        "    int* out = (int*)malloc(sizeof(int)*(n>0?n:1));\n"
        "    for (int i=0;i<n;i++) out[i] = -1;\n"
        "    int* stack = (int*)malloc(sizeof(int)*(n>0?n:1)); int top = 0;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        while (top > 0 && nums.data[stack[top-1]] < nums.data[i]) { out[stack[--top]] = nums.data[i]; }\n"
        "        stack[top++] = i;\n"
        "    }\n"
        f"    {incr}free(stack);\n"
        "    AtlasIntArray result; result.size = n; result.data = out;\n"
        "    return result;\n"
        "}\n"
    )


def _rust_next_greater(wrong):
    incr = "for x in out.iter_mut() { if *x != -1 { *x += 1; } }\n    " if wrong else ""
    return (
        "fn next_greater_element(nums: Vec<i32>) -> Vec<i32> {\n"
        "    let n = nums.len(); let mut out = vec![-1i32; n]; let mut stack: Vec<usize> = Vec::new();\n"
        "    for i in 0..n {\n"
        "        while let Some(&j) = stack.last() { if nums[j] < nums[i] { out[j] = nums[i]; stack.pop(); } else { break; } }\n"
        "        stack.push(i);\n"
        "    }\n"
        f"    {incr}out\n"
        "}\n"
    )


# ── number-of-islands (grid: array<array<int>>, 4-directional flood count) ──
def _js_islands(wrong):
    a = " + 1" if wrong else ""
    return (
        "function num_islands(grid) {\n"
        "    const m = grid.length, n = grid[0].length;\n"
        "    const visited = Array.from({length:m}, () => new Array(n).fill(false));\n"
        "    let count = 0;\n"
        "    function bfs(sr, sc) {\n"
        "        const q = [[sr,sc]]; visited[sr][sc] = true; let qi = 0;\n"
        "        while (qi < q.length) {\n"
        "            const [r,c] = q[qi]; qi++;\n"
        "            for (const [dr,dc] of [[1,0],[-1,0],[0,1],[0,-1]]) {\n"
        "                const nr=r+dr, nc=c+dc;\n"
        "                if (nr>=0&&nr<m&&nc>=0&&nc<n&&!visited[nr][nc]&&grid[nr][nc]===1) { visited[nr][nc]=true; q.push([nr,nc]); }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "    for (let i=0;i<m;i++) for (let j=0;j<n;j++) { if (grid[i][j]===1 && !visited[i][j]) { count++; bfs(i,j); } }\n"
        f"    return count{a};\n"
        "}\n"
    )


def _ts_islands(wrong):
    a = " + 1" if wrong else ""
    return (
        "function num_islands(grid: number[][]): number {\n"
        "    const m = grid.length, n = grid[0].length;\n"
        "    const visited: boolean[][] = Array.from({length:m}, () => new Array(n).fill(false));\n"
        "    let count = 0;\n"
        "    function bfs(sr: number, sc: number): void {\n"
        "        const q: number[][] = [[sr,sc]]; visited[sr][sc] = true; let qi = 0;\n"
        "        while (qi < q.length) {\n"
        "            const [r,c] = q[qi]; qi++;\n"
        "            for (const [dr,dc] of [[1,0],[-1,0],[0,1],[0,-1]]) {\n"
        "                const nr=r+dr, nc=c+dc;\n"
        "                if (nr>=0&&nr<m&&nc>=0&&nc<n&&!visited[nr][nc]&&grid[nr][nc]===1) { visited[nr][nc]=true; q.push([nr,nc]); }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "    for (let i=0;i<m;i++) for (let j=0;j<n;j++) { if (grid[i][j]===1 && !visited[i][j]) { count++; bfs(i,j); } }\n"
        f"    return count{a};\n"
        "}\n"
    )


def _java_islands(wrong):
    # No own `import java.util.*;` here -- compose_program already prepends
    # that unconditionally before user_code (confirmed by inspecting the
    # generated source directly after a real compile failure), so a second
    # import statement here would land after the harness's own TreeNode
    # class, which is illegal Java (imports must precede all type decls).
    a = " + 1" if wrong else ""
    return (
        "class Solution { public int num_islands(int[][] grid) {\n"
        "    int m = grid.length, n = grid[0].length;\n"
        "    boolean[][] visited = new boolean[m][n]; int count = 0;\n"
        "    int[] dr = {1,-1,0,0}; int[] dc = {0,0,1,-1};\n"
        "    for (int i=0;i<m;i++) for (int j=0;j<n;j++) {\n"
        "        if (grid[i][j]==1 && !visited[i][j]) {\n"
        "            count++;\n"
        "            ArrayDeque<int[]> q = new ArrayDeque<>(); q.add(new int[]{i,j}); visited[i][j]=true;\n"
        "            while (!q.isEmpty()) {\n"
        "                int[] cur = q.poll();\n"
        "                for (int d=0;d<4;d++) {\n"
        "                    int nr = cur[0]+dr[d], nc = cur[1]+dc[d];\n"
        "                    if (nr>=0&&nr<m&&nc>=0&&nc<n&&!visited[nr][nc]&&grid[nr][nc]==1) { visited[nr][nc]=true; q.add(new int[]{nr,nc}); }\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        f"    return count{a};\n"
        "} }\n"
    )


def _cpp_islands(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public: int num_islands(std::vector<std::vector<int>> grid) {\n"
        "    int m = grid.size(), n = grid[0].size();\n"
        "    std::vector<std::vector<bool>> visited(m, std::vector<bool>(n, false)); int count = 0;\n"
        "    int dr[4] = {1,-1,0,0}; int dc[4] = {0,0,1,-1};\n"
        "    for (int i=0;i<m;i++) for (int j=0;j<n;j++) {\n"
        "        if (grid[i][j]==1 && !visited[i][j]) {\n"
        "            count++;\n"
        "            std::queue<std::pair<int,int>> q; q.push({i,j}); visited[i][j]=true;\n"
        "            while (!q.empty()) {\n"
        "                auto [r,c] = q.front(); q.pop();\n"
        "                for (int d=0;d<4;d++) {\n"
        "                    int nr=r+dr[d], nc=c+dc[d];\n"
        "                    if (nr>=0&&nr<m&&nc>=0&&nc<n&&!visited[nr][nc]&&grid[nr][nc]==1) { visited[nr][nc]=true; q.push({nr,nc}); }\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        f"    return count{a};\n"
        "} };\n"
    )


def _csharp_islands(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public static int num_islands(int[][] grid) {\n"
        "    int m = grid.Length, n = grid[0].Length;\n"
        "    bool[,] visited = new bool[m,n]; int count = 0;\n"
        "    int[] dr = {1,-1,0,0}; int[] dc = {0,0,1,-1};\n"
        "    for (int i=0;i<m;i++) for (int j=0;j<n;j++) {\n"
        "        if (grid[i][j]==1 && !visited[i,j]) {\n"
        "            count++;\n"
        "            var q = new System.Collections.Generic.Queue<(int,int)>(); q.Enqueue((i,j)); visited[i,j]=true;\n"
        "            while (q.Count > 0) {\n"
        "                var (r,c) = q.Dequeue();\n"
        "                for (int d=0;d<4;d++) {\n"
        "                    int nr=r+dr[d], nc=c+dc[d];\n"
        "                    if (nr>=0&&nr<m&&nc>=0&&nc<n&&!visited[nr,nc]&&grid[nr][nc]==1) { visited[nr,nc]=true; q.Enqueue((nr,nc)); }\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        f"    return count{a};\n"
        "} }\n"
    )


def _perl_islands(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub num_islands {\n"
        "    my ($grid) = @_;\n"
        "    my $m = scalar(@$grid); my $n = scalar(@{$grid->[0]});\n"
        "    my @visited; for my $i (0..$m-1) { for my $j (0..$n-1) { $visited[$i][$j] = 0; } }\n"
        "    my $count = 0;\n"
        "    my @dr = (1,-1,0,0); my @dc = (0,0,1,-1);\n"
        "    for (my $i=0;$i<$m;$i++) {\n"
        "        for (my $j=0;$j<$n;$j++) {\n"
        "            if ($grid->[$i][$j]==1 && !$visited[$i][$j]) {\n"
        "                $count++;\n"
        "                my @q = ([$i,$j]); $visited[$i][$j]=1; my $qi=0;\n"
        "                while ($qi < scalar(@q)) {\n"
        "                    my ($r,$c) = @{$q[$qi]}; $qi++;\n"
        "                    for (my $d=0;$d<4;$d++) {\n"
        "                        my $nr = $r+$dr[$d]; my $nc = $c+$dc[$d];\n"
        "                        if ($nr>=0 && $nr<$m && $nc>=0 && $nc<$n && !$visited[$nr][$nc] && $grid->[$nr][$nc]==1) {\n"
        "                            $visited[$nr][$nc]=1; push @q, [$nr,$nc];\n"
        "                        }\n"
        "                    }\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        f"    return $count{a};\n"
        "}\n"
    )


def _c_islands(wrong):
    a = " + 1" if wrong else ""
    return (
        "int num_islands(AtlasIntMatrix grid) {\n"
        "    int m = grid.size, n = grid.data[0].size;\n"
        "    int* visited = (int*)calloc(m*n, sizeof(int));\n"
        "    int* qr = (int*)malloc(sizeof(int)*m*n); int* qc = (int*)malloc(sizeof(int)*m*n);\n"
        "    int count = 0;\n"
        "    int dr[4] = {1,-1,0,0}; int dc[4] = {0,0,1,-1};\n"
        "    for (int i=0;i<m;i++) for (int j=0;j<n;j++) {\n"
        "        if (grid.data[i].data[j]==1 && !visited[i*n+j]) {\n"
        "            count++;\n"
        "            int qh=0, qt=0; qr[qt]=i; qc[qt]=j; qt++; visited[i*n+j]=1;\n"
        "            while (qh < qt) {\n"
        "                int r = qr[qh], c = qc[qh]; qh++;\n"
        "                for (int d=0;d<4;d++) {\n"
        "                    int nr=r+dr[d], nc=c+dc[d];\n"
        "                    if (nr>=0&&nr<m&&nc>=0&&nc<n&&!visited[nr*n+nc]&&grid.data[nr].data[nc]==1) {\n"
        "                        visited[nr*n+nc]=1; qr[qt]=nr; qc[qt]=nc; qt++;\n"
        "                    }\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "    free(visited); free(qr); free(qc);\n"
        f"    return count{a};\n"
        "}\n"
    )


def _rust_islands(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::collections::VecDeque;\n"
        "fn num_islands(grid: Vec<Vec<i32>>) -> i32 {\n"
        "    let m = grid.len(); let n = grid[0].len();\n"
        "    let mut visited = vec![vec![false; n]; m];\n"
        "    let mut count = 0;\n"
        "    let dirs: [(i32,i32);4] = [(1,0),(-1,0),(0,1),(0,-1)];\n"
        "    for i in 0..m { for j in 0..n {\n"
        "        if grid[i][j]==1 && !visited[i][j] {\n"
        "            count += 1;\n"
        "            let mut q: VecDeque<(usize,usize)> = VecDeque::new();\n"
        "            q.push_back((i,j)); visited[i][j] = true;\n"
        "            while let Some((r,c)) = q.pop_front() {\n"
        "                for (dr,dc) in dirs.iter() {\n"
        "                    let nr = r as i32 + dr; let nc = c as i32 + dc;\n"
        "                    if nr>=0 && nr<m as i32 && nc>=0 && nc<n as i32 {\n"
        "                        let (nru, ncu) = (nr as usize, nc as usize);\n"
        "                        if !visited[nru][ncu] && grid[nru][ncu]==1 { visited[nru][ncu]=true; q.push_back((nru,ncu)); }\n"
        "                    }\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "    } }\n"
        f"    count{a}\n"
        "}\n"
    )


# ── flood-fill ───────────────────────────────────────────────────────────────
def _js_flood(wrong):
    a = ".map(row => row.map(v => v + 1))" if wrong else ""
    return (
        "function flood_fill(grid, sr, sc, new_color) {\n"
        "    const m = grid.length, n = grid[0].length;\n"
        "    const out = grid.map(r => r.slice());\n"
        "    const old = out[sr][sc];\n"
        "    if (old === new_color) return out" + a + ";\n"
        "    const stack = [[sr,sc]];\n"
        "    out[sr][sc] = new_color;\n"
        "    while (stack.length) {\n"
        "        const [r,c] = stack.pop();\n"
        "        for (const [dr,dc] of [[1,0],[-1,0],[0,1],[0,-1]]) {\n"
        "            const nr=r+dr, nc=c+dc;\n"
        "            if (nr>=0&&nr<m&&nc>=0&&nc<n&&out[nr][nc]===old) { out[nr][nc]=new_color; stack.push([nr,nc]); }\n"
        "        }\n"
        "    }\n"
        f"    return out{a};\n"
        "}\n"
    )


def _ts_flood(wrong):
    a = ".map(row => row.map(v => v + 1))" if wrong else ""
    return (
        "function flood_fill(grid: number[][], sr: number, sc: number, new_color: number): number[][] {\n"
        "    const m = grid.length, n = grid[0].length;\n"
        "    const out = grid.map(r => r.slice());\n"
        "    const old = out[sr][sc];\n"
        "    if (old === new_color) return out" + a + ";\n"
        "    const stack: number[][] = [[sr,sc]];\n"
        "    out[sr][sc] = new_color;\n"
        "    while (stack.length) {\n"
        "        const [r,c] = stack.pop() as number[];\n"
        "        for (const [dr,dc] of [[1,0],[-1,0],[0,1],[0,-1]]) {\n"
        "            const nr=r+dr, nc=c+dc;\n"
        "            if (nr>=0&&nr<m&&nc>=0&&nc<n&&out[nr][nc]===old) { out[nr][nc]=new_color; stack.push([nr,nc]); }\n"
        "        }\n"
        "    }\n"
        f"    return out{a};\n"
        "}\n"
    )


def _java_flood(wrong):
    incr = "for (int i=0;i<m;i++) for (int j=0;j<n;j++) out[i][j]++;\n        " if wrong else ""
    return (
        "class Solution { public int[][] flood_fill(int[][] grid, int sr, int sc, int new_color) {\n"
        "    int m = grid.length, n = grid[0].length;\n"
        "    int[][] out = new int[m][n];\n"
        "    for (int i=0;i<m;i++) out[i] = grid[i].clone();\n"
        "    int old = out[sr][sc];\n"
        "    if (old != new_color) {\n"
        "        java.util.Deque<int[]> stack = new java.util.ArrayDeque<>(); stack.push(new int[]{sr,sc});\n"
        "        out[sr][sc] = new_color;\n"
        "        int[] dr = {1,-1,0,0}; int[] dc = {0,0,1,-1};\n"
        "        while (!stack.isEmpty()) {\n"
        "            int[] cur = stack.pop();\n"
        "            for (int d=0;d<4;d++) {\n"
        "                int nr = cur[0]+dr[d], nc = cur[1]+dc[d];\n"
        "                if (nr>=0&&nr<m&&nc>=0&&nc<n&&out[nr][nc]==old) { out[nr][nc]=new_color; stack.push(new int[]{nr,nc}); }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        f"        {incr}return out;\n"
        "} }\n"
    )


def _cpp_flood(wrong):
    incr = "for (auto& row : out) for (auto& v : row) v++;\n    " if wrong else ""
    return (
        "class Solution { public: std::vector<std::vector<int>> flood_fill(std::vector<std::vector<int>> grid, int sr, int sc, int new_color) {\n"
        "    int m = grid.size(), n = grid[0].size();\n"
        "    std::vector<std::vector<int>> out = grid;\n"
        "    int old = out[sr][sc];\n"
        "    if (old != new_color) {\n"
        "        std::vector<std::pair<int,int>> stack; stack.push_back({sr,sc});\n"
        "        out[sr][sc] = new_color;\n"
        "        int dr[4] = {1,-1,0,0}; int dc[4] = {0,0,1,-1};\n"
        "        while (!stack.empty()) {\n"
        "            auto [r,c] = stack.back(); stack.pop_back();\n"
        "            for (int d=0;d<4;d++) {\n"
        "                int nr=r+dr[d], nc=c+dc[d];\n"
        "                if (nr>=0&&nr<m&&nc>=0&&nc<n&&out[nr][nc]==old) { out[nr][nc]=new_color; stack.push_back({nr,nc}); }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        f"    {incr}return out;\n"
        "} };\n"
    )


def _csharp_flood(wrong):
    incr = "for (int i=0;i<m;i++) for (int j=0;j<n;j++) outArr[i][j]++;\n        " if wrong else ""
    return (
        "class Solution { public static int[][] flood_fill(int[][] grid, int sr, int sc, int new_color) {\n"
        "    int m = grid.Length, n = grid[0].Length;\n"
        "    int[][] outArr = new int[m][];\n"
        "    for (int i=0;i<m;i++) outArr[i] = (int[])grid[i].Clone();\n"
        "    int old = outArr[sr][sc];\n"
        "    if (old != new_color) {\n"
        "        var stack = new System.Collections.Generic.Stack<(int,int)>(); stack.Push((sr,sc));\n"
        "        outArr[sr][sc] = new_color;\n"
        "        int[] dr = {1,-1,0,0}; int[] dc = {0,0,1,-1};\n"
        "        while (stack.Count > 0) {\n"
        "            var (r,c) = stack.Pop();\n"
        "            for (int d=0;d<4;d++) {\n"
        "                int nr=r+dr[d], nc=c+dc[d];\n"
        "                if (nr>=0&&nr<m&&nc>=0&&nc<n&&outArr[nr][nc]==old) { outArr[nr][nc]=new_color; stack.Push((nr,nc)); }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        f"        {incr}return outArr;\n"
        "} }\n"
    )


def _perl_flood(wrong):
    incr = "for my $row (@out) { for my $v (@$row) { $v++; } }\n    " if wrong else ""
    return (
        "sub flood_fill {\n"
        "    my ($grid, $sr, $sc, $new_color) = @_;\n"
        "    my $m = scalar(@$grid); my $n = scalar(@{$grid->[0]});\n"
        "    my @out; for my $i (0..$m-1) { $out[$i] = [@{$grid->[$i]}]; }\n"
        "    my $old = $out[$sr][$sc];\n"
        "    if ($old != $new_color) {\n"
        "        my @stack = ([$sr,$sc]); $out[$sr][$sc] = $new_color;\n"
        "        my @dr = (1,-1,0,0); my @dc = (0,0,1,-1);\n"
        "        while (@stack) {\n"
        "            my ($r,$c) = @{pop @stack};\n"
        "            for (my $d=0;$d<4;$d++) {\n"
        "                my $nr = $r+$dr[$d]; my $nc = $c+$dc[$d];\n"
        "                if ($nr>=0 && $nr<$m && $nc>=0 && $nc<$n && $out[$nr][$nc]==$old) { $out[$nr][$nc]=$new_color; push @stack, [$nr,$nc]; }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        f"    {incr}return \\@out;\n"
        "}\n"
    )


def _c_flood(wrong):
    incr = "for (int i=0;i<m;i++) for (int j=0;j<n;j++) data[i].data[j]++;\n    " if wrong else ""
    return (
        "AtlasIntMatrix flood_fill(AtlasIntMatrix grid, int sr, int sc, int new_color) {\n"
        "    int m = grid.size, n = grid.data[0].size;\n"
        "    AtlasIntArray* data = (AtlasIntArray*)malloc(sizeof(AtlasIntArray)*m);\n"
        "    for (int i=0;i<m;i++) {\n"
        "        data[i].size = n; data[i].data = (int*)malloc(sizeof(int)*n);\n"
        "        for (int j=0;j<n;j++) data[i].data[j] = grid.data[i].data[j];\n"
        "    }\n"
        "    int old = data[sr].data[sc];\n"
        "    if (old != new_color) {\n"
        "        int* qr = (int*)malloc(sizeof(int)*m*n); int* qc = (int*)malloc(sizeof(int)*m*n);\n"
        "        int qh=0, qt=0; qr[qt]=sr; qc[qt]=sc; qt++;\n"
        "        data[sr].data[sc] = new_color;\n"
        "        int dr[4] = {1,-1,0,0}; int dc[4] = {0,0,1,-1};\n"
        "        while (qh < qt) {\n"
        "            int r = qr[qh], c = qc[qh]; qh++;\n"
        "            for (int d=0;d<4;d++) {\n"
        "                int nr=r+dr[d], nc=c+dc[d];\n"
        "                if (nr>=0&&nr<m&&nc>=0&&nc<n&&data[nr].data[nc]==old) { data[nr].data[nc]=new_color; qr[qt]=nr; qc[qt]=nc; qt++; }\n"
        "            }\n"
        "        }\n"
        "        free(qr); free(qc);\n"
        "    }\n"
        f"    {incr}AtlasIntMatrix result; result.size = m; result.data = data;\n"
        "    return result;\n"
        "}\n"
    )


def _rust_flood(wrong):
    incr = "for row in out.iter_mut() { for v in row.iter_mut() { *v += 1; } }\n    " if wrong else ""
    return (
        "fn flood_fill(grid: Vec<Vec<i32>>, sr: i32, sc: i32, new_color: i32) -> Vec<Vec<i32>> {\n"
        "    let m = grid.len(); let n = grid[0].len();\n"
        "    let mut out = grid.clone();\n"
        "    let (sr, sc) = (sr as usize, sc as usize);\n"
        "    let old = out[sr][sc];\n"
        "    if old != new_color {\n"
        "        let mut stack: Vec<(usize,usize)> = vec![(sr,sc)];\n"
        "        out[sr][sc] = new_color;\n"
        "        let dirs: [(i32,i32);4] = [(1,0),(-1,0),(0,1),(0,-1)];\n"
        "        while let Some((r,c)) = stack.pop() {\n"
        "            for (dr,dc) in dirs.iter() {\n"
        "                let nr = r as i32 + dr; let nc = c as i32 + dc;\n"
        "                if nr>=0 && nr<m as i32 && nc>=0 && nc<n as i32 {\n"
        "                    let (nru, ncu) = (nr as usize, nc as usize);\n"
        "                    if out[nru][ncu]==old { out[nru][ncu]=new_color; stack.push((nru,ncu)); }\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        f"    {incr}out\n"
        "}\n"
    )


# ── longest-substring-without-repeating ─────────────────────────────────────
def _js_lswr(wrong):
    a = " + 1" if wrong else ""
    return (
        "function length_of_longest_substring(s) {\n"
        "    const last = {}; let best = 0, start = 0;\n"
        "    for (let i=0;i<s.length;i++) {\n"
        "        const ch = s[i];\n"
        "        if (last[ch] !== undefined && last[ch] >= start) start = last[ch] + 1;\n"
        "        last[ch] = i;\n"
        "        best = Math.max(best, i - start + 1);\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
    )


def _ts_lswr(wrong):
    a = " + 1" if wrong else ""
    return (
        "function length_of_longest_substring(s: string): number {\n"
        "    const last: Record<string, number> = {}; let best = 0, start = 0;\n"
        "    for (let i=0;i<s.length;i++) {\n"
        "        const ch = s[i];\n"
        "        if (last[ch] !== undefined && last[ch] >= start) start = last[ch] + 1;\n"
        "        last[ch] = i;\n"
        "        best = Math.max(best, i - start + 1);\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
    )


def _java_lswr(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public int length_of_longest_substring(String s) {\n"
        "    java.util.Map<Character,Integer> last = new java.util.HashMap<>();\n"
        "    int best = 0, start = 0;\n"
        "    for (int i=0;i<s.length();i++) {\n"
        "        char ch = s.charAt(i);\n"
        "        if (last.containsKey(ch) && last.get(ch) >= start) start = last.get(ch) + 1;\n"
        "        last.put(ch, i);\n"
        "        best = Math.max(best, i - start + 1);\n"
        "    }\n"
        f"    return best{a};\n"
        "} }\n"
    )


def _cpp_lswr(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public: int length_of_longest_substring(std::string s) {\n"
        "    std::unordered_map<char,int> last;\n"
        "    int best = 0, start = 0;\n"
        "    for (int i=0;i<(int)s.size();i++) {\n"
        "        char ch = s[i];\n"
        "        auto it = last.find(ch);\n"
        "        if (it != last.end() && it->second >= start) start = it->second + 1;\n"
        "        last[ch] = i;\n"
        "        best = std::max(best, i - start + 1);\n"
        "    }\n"
        f"    return best{a};\n"
        "} };\n"
    )


def _csharp_lswr(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public static int length_of_longest_substring(string s) {\n"
        "    var last = new System.Collections.Generic.Dictionary<char,int>();\n"
        "    int best = 0, start = 0;\n"
        "    for (int i=0;i<s.Length;i++) {\n"
        "        char ch = s[i];\n"
        "        if (last.ContainsKey(ch) && last[ch] >= start) start = last[ch] + 1;\n"
        "        last[ch] = i;\n"
        "        best = System.Math.Max(best, i - start + 1);\n"
        "    }\n"
        f"    return best{a};\n"
        "} }\n"
    )


def _perl_lswr(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub length_of_longest_substring {\n"
        "    my ($s) = @_;\n"
        "    my %last; my $best = 0; my $start = 0;\n"
        "    my @chars = split //, $s;\n"
        "    for (my $i=0;$i<scalar(@chars);$i++) {\n"
        "        my $ch = $chars[$i];\n"
        "        if (exists $last{$ch} && $last{$ch} >= $start) { $start = $last{$ch} + 1; }\n"
        "        $last{$ch} = $i;\n"
        "        my $len = $i - $start + 1;\n"
        "        $best = $len if $len > $best;\n"
        "    }\n"
        f"    return $best{a};\n"
        "}\n"
    )


def _c_lswr(wrong):
    a = " + 1" if wrong else ""
    return (
        "int length_of_longest_substring(char* s) {\n"
        "    int n = 0; while (s[n]) n++;\n"
        "    int last[256]; for (int i=0;i<256;i++) last[i] = -1;\n"
        "    int best = 0, start = 0;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        unsigned char ch = s[i];\n"
        "        if (last[ch] >= start) start = last[ch] + 1;\n"
        "        last[ch] = i;\n"
        "        int len = i - start + 1;\n"
        "        if (len > best) best = len;\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
    )


def _rust_lswr(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::collections::HashMap;\n"
        "fn length_of_longest_substring(s: String) -> i32 {\n"
        "    let chars: Vec<char> = s.chars().collect();\n"
        "    let mut last: HashMap<char, i32> = HashMap::new();\n"
        "    let mut best = 0; let mut start: i32 = 0;\n"
        "    for i in 0..chars.len() {\n"
        "        let ch = chars[i];\n"
        "        if let Some(&p) = last.get(&ch) { if p >= start { start = p + 1; } }\n"
        "        last.insert(ch, i as i32);\n"
        "        let len = i as i32 - start + 1;\n"
        "        if len > best { best = len; }\n"
        "    }\n"
        f"    best{a}\n"
        "}\n"
    )


# ── valid-palindrome-string ──────────────────────────────────────────────────
def _js_valid_pal(wrong):
    return (
        "function is_valid_palindrome(s) {\n"
        "    const clean = s.toLowerCase().replace(/[^a-z0-9]/g, '');\n"
        "    let lo = 0, hi = clean.length - 1;\n"
        "    while (lo < hi) { if (clean[lo] !== clean[hi]) return false; lo++; hi--; }\n"
        f"    return {'false' if wrong else 'true'};\n"
        "}\n"
    )


def _ts_valid_pal(wrong):
    return (
        "function is_valid_palindrome(s: string): boolean {\n"
        "    const clean = s.toLowerCase().replace(/[^a-z0-9]/g, '');\n"
        "    let lo = 0, hi = clean.length - 1;\n"
        "    while (lo < hi) { if (clean[lo] !== clean[hi]) return false; lo++; hi--; }\n"
        f"    return {'false' if wrong else 'true'};\n"
        "}\n"
    )


def _java_valid_pal(wrong):
    return (
        "class Solution { public boolean is_valid_palindrome(String s) {\n"
        "    StringBuilder sb = new StringBuilder();\n"
        "    for (char c : s.toCharArray()) if (Character.isLetterOrDigit(c)) sb.append(Character.toLowerCase(c));\n"
        "    String clean = sb.toString();\n"
        "    int lo=0, hi=clean.length()-1;\n"
        "    while (lo<hi) { if (clean.charAt(lo) != clean.charAt(hi)) return false; lo++; hi--; }\n"
        f"    return {'false' if wrong else 'true'};\n"
        "} }\n"
    )


def _cpp_valid_pal(wrong):
    return (
        "class Solution { public: bool is_valid_palindrome(std::string s) {\n"
        "    std::string clean;\n"
        "    for (char c : s) if (isalnum((unsigned char)c)) clean += tolower((unsigned char)c);\n"
        "    int lo=0, hi=(int)clean.size()-1;\n"
        "    while (lo<hi) { if (clean[lo] != clean[hi]) return false; lo++; hi--; }\n"
        f"    return {'false' if wrong else 'true'};\n"
        "} };\n"
    )


def _csharp_valid_pal(wrong):
    return (
        "class Solution { public static bool is_valid_palindrome(string s) {\n"
        "    var sb = new System.Text.StringBuilder();\n"
        "    foreach (char c in s) if (char.IsLetterOrDigit(c)) sb.Append(char.ToLower(c));\n"
        "    string clean = sb.ToString();\n"
        "    int lo=0, hi=clean.Length-1;\n"
        "    while (lo<hi) { if (clean[lo] != clean[hi]) return false; lo++; hi--; }\n"
        f"    return {'false' if wrong else 'true'};\n"
        "} }\n"
    )


def _perl_valid_pal(wrong):
    return (
        "sub is_valid_palindrome {\n"
        "    my ($s) = @_;\n"
        "    my $clean = lc($s);\n"
        "    $clean =~ s/[^a-z0-9]//g;\n"
        "    my $lo = 0; my $hi = length($clean) - 1;\n"
        "    while ($lo < $hi) { return 0 if substr($clean,$lo,1) ne substr($clean,$hi,1); $lo++; $hi--; }\n"
        f"    return {'0' if wrong else '1'};\n"
        "}\n"
    )


def _c_valid_pal(wrong):
    return (
        "int is_valid_palindrome(char* s) {\n"
        "    int n = 0; while (s[n]) n++;\n"
        "    char* clean = (char*)malloc(n+1); int cn = 0;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        char c = s[i];\n"
        "        if ((c>='a'&&c<='z')||(c>='0'&&c<='9')) clean[cn++] = c;\n"
        "        else if (c>='A'&&c<='Z') clean[cn++] = c - 'A' + 'a';\n"
        "    }\n"
        "    int lo=0, hi=cn-1, ok=1;\n"
        "    while (lo<hi) { if (clean[lo] != clean[hi]) { ok=0; break; } lo++; hi--; }\n"
        "    free(clean);\n"
        f"    return {'!ok' if wrong else 'ok'};\n"
        "}\n"
    )


def _rust_valid_pal(wrong):
    return (
        "fn is_valid_palindrome(s: String) -> bool {\n"
        "    let clean: Vec<char> = s.chars().filter(|c| c.is_alphanumeric()).map(|c| c.to_ascii_lowercase()).collect();\n"
        "    let n = clean.len();\n"
        "    if n == 0 { return " + ("false" if wrong else "true") + "; }\n"
        "    let (mut lo, mut hi) = (0usize, n-1);\n"
        "    while lo < hi { if clean[lo] != clean[hi] { return false; } lo += 1; hi -= 1; }\n"
        f"    {'false' if wrong else 'true'}\n"
        "}\n"
    )


# ── group-anagrams-count ─────────────────────────────────────────────────────
def _js_group_anagrams(wrong):
    a = " + 1" if wrong else ""
    return (
        "function group_anagrams_count(strs) {\n"
        "    const seen = new Set();\n"
        "    for (const s of strs) { const key = s.split('').sort().join(''); seen.add(key); }\n"
        f"    return seen.size{a};\n"
        "}\n"
    )


def _ts_group_anagrams(wrong):
    a = " + 1" if wrong else ""
    return (
        "function group_anagrams_count(strs: string[]): number {\n"
        "    const seen = new Set<string>();\n"
        "    for (const s of strs) { const key = s.split('').sort().join(''); seen.add(key); }\n"
        f"    return seen.size{a};\n"
        "}\n"
    )


def _java_group_anagrams(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public int group_anagrams_count(String[] strs) {\n"
        "    java.util.Set<String> seen = new java.util.HashSet<>();\n"
        "    for (String s: strs) { char[] c = s.toCharArray(); java.util.Arrays.sort(c); seen.add(new String(c)); }\n"
        f"    return seen.size(){a};\n"
        "} }\n"
    )


def _cpp_group_anagrams(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public: int group_anagrams_count(std::vector<std::string> strs) {\n"
        "    std::set<std::string> seen;\n"
        "    for (std::string s : strs) { std::sort(s.begin(), s.end()); seen.insert(s); }\n"
        f"    return (int)seen.size(){a};\n"
        "} };\n"
    )


def _csharp_group_anagrams(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public static int group_anagrams_count(string[] strs) {\n"
        "    var seen = new System.Collections.Generic.HashSet<string>();\n"
        "    foreach (string s in strs) { var c = s.ToCharArray(); System.Array.Sort(c); seen.Add(new string(c)); }\n"
        f"    return seen.Count{a};\n"
        "} }\n"
    )


def _perl_group_anagrams(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub group_anagrams_count {\n"
        "    my ($strs) = @_;\n"
        "    my %seen;\n"
        "    foreach my $s (@$strs) { my $key = join('', sort split //, $s); $seen{$key} = 1; }\n"
        "    my $count = scalar(keys %seen);\n"
        f"    return $count{a};\n"
        "}\n"
    )


def _c_group_anagrams(wrong):
    a = " + 1" if wrong else ""
    return (
        "int cmpchar(const void* a, const void* b) { return *(const char*)a - *(const char*)b; }\n"
        "int group_anagrams_count(AtlasStringArray strs) {\n"
        "    char** keys = (char**)malloc(sizeof(char*) * (strs.size>0?strs.size:1));\n"
        "    int kc = 0;\n"
        "    for (int i=0;i<strs.size;i++) {\n"
        "        int len = 0; while (strs.data[i][len]) len++;\n"
        "        char* sorted = (char*)malloc(len+1);\n"
        "        for (int k=0;k<len;k++) sorted[k] = strs.data[i][k];\n"
        "        sorted[len] = 0;\n"
        "        qsort(sorted, len, sizeof(char), cmpchar);\n"
        "        int dup = 0;\n"
        "        for (int k=0;k<kc;k++) if (strcmp(keys[k], sorted) == 0) { dup = 1; break; }\n"
        "        if (!dup) keys[kc++] = sorted; else free(sorted);\n"
        "    }\n"
        "    int result = kc;\n"
        "    for (int i=0;i<kc;i++) free(keys[i]);\n"
        "    free(keys);\n"
        f"    return result{a};\n"
        "}\n"
    )


def _rust_group_anagrams(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::collections::HashSet;\n"
        "fn group_anagrams_count(strs: Vec<String>) -> i32 {\n"
        "    let mut seen: HashSet<String> = HashSet::new();\n"
        "    for s in strs.iter() {\n"
        "        let mut chars: Vec<char> = s.chars().collect();\n"
        "        chars.sort();\n"
        "        let key: String = chars.into_iter().collect();\n"
        "        seen.insert(key);\n"
        "    }\n"
        f"    seen.len() as i32{a}\n"
        "}\n"
    )


# ── three-sum-count-triplets (distinct value-triplets summing to 0) ─────────
def _js_threesum(wrong):
    a = " + 1" if wrong else ""
    return (
        "function three_sum_count(nums) {\n"
        "    const arr = nums.slice().sort((a,b)=>a-b); const n = arr.length;\n"
        "    let count = 0;\n"
        "    for (let i=0;i<n-2;i++) {\n"
        "        if (i>0 && arr[i]===arr[i-1]) continue;\n"
        "        let lo=i+1, hi=n-1;\n"
        "        while (lo<hi) {\n"
        "            const sum = arr[i]+arr[lo]+arr[hi];\n"
        "            if (sum===0) { count++; const lv=arr[lo]; while(lo<hi&&arr[lo]===lv) lo++; const hv=arr[hi]; while(lo<hi&&arr[hi]===hv) hi--; }\n"
        "            else if (sum<0) lo++; else hi--;\n"
        "        }\n"
        "    }\n"
        f"    return count{a};\n"
        "}\n"
    )


def _ts_threesum(wrong):
    a = " + 1" if wrong else ""
    return (
        "function three_sum_count(nums: number[]): number {\n"
        "    const arr = nums.slice().sort((a,b)=>a-b); const n = arr.length;\n"
        "    let count = 0;\n"
        "    for (let i=0;i<n-2;i++) {\n"
        "        if (i>0 && arr[i]===arr[i-1]) continue;\n"
        "        let lo=i+1, hi=n-1;\n"
        "        while (lo<hi) {\n"
        "            const sum = arr[i]+arr[lo]+arr[hi];\n"
        "            if (sum===0) { count++; const lv=arr[lo]; while(lo<hi&&arr[lo]===lv) lo++; const hv=arr[hi]; while(lo<hi&&arr[hi]===hv) hi--; }\n"
        "            else if (sum<0) lo++; else hi--;\n"
        "        }\n"
        "    }\n"
        f"    return count{a};\n"
        "}\n"
    )


def _java_threesum(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public int three_sum_count(int[] nums) {\n"
        "    int[] arr = nums.clone(); java.util.Arrays.sort(arr); int n = arr.length;\n"
        "    int count = 0;\n"
        "    for (int i=0;i<n-2;i++) {\n"
        "        if (i>0 && arr[i]==arr[i-1]) continue;\n"
        "        int lo=i+1, hi=n-1;\n"
        "        while (lo<hi) {\n"
        "            int sum = arr[i]+arr[lo]+arr[hi];\n"
        "            if (sum==0) { count++; int lv=arr[lo]; while(lo<hi&&arr[lo]==lv) lo++; int hv=arr[hi]; while(lo<hi&&arr[hi]==hv) hi--; }\n"
        "            else if (sum<0) lo++; else hi--;\n"
        "        }\n"
        "    }\n"
        f"    return count{a};\n"
        "} }\n"
    )


def _cpp_threesum(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public: int three_sum_count(std::vector<int> nums) {\n"
        "    std::vector<int> arr = nums; std::sort(arr.begin(), arr.end()); int n = arr.size();\n"
        "    int count = 0;\n"
        "    for (int i=0;i<n-2;i++) {\n"
        "        if (i>0 && arr[i]==arr[i-1]) continue;\n"
        "        int lo=i+1, hi=n-1;\n"
        "        while (lo<hi) {\n"
        "            int sum = arr[i]+arr[lo]+arr[hi];\n"
        "            if (sum==0) { count++; int lv=arr[lo]; while(lo<hi&&arr[lo]==lv) lo++; int hv=arr[hi]; while(lo<hi&&arr[hi]==hv) hi--; }\n"
        "            else if (sum<0) lo++; else hi--;\n"
        "        }\n"
        "    }\n"
        f"    return count{a};\n"
        "} };\n"
    )


def _csharp_threesum(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution { public static int three_sum_count(int[] nums) {\n"
        "    int[] arr = (int[])nums.Clone(); System.Array.Sort(arr); int n = arr.Length;\n"
        "    int count = 0;\n"
        "    for (int i=0;i<n-2;i++) {\n"
        "        if (i>0 && arr[i]==arr[i-1]) continue;\n"
        "        int lo=i+1, hi=n-1;\n"
        "        while (lo<hi) {\n"
        "            int sum = arr[i]+arr[lo]+arr[hi];\n"
        "            if (sum==0) { count++; int lv=arr[lo]; while(lo<hi&&arr[lo]==lv) lo++; int hv=arr[hi]; while(lo<hi&&arr[hi]==hv) hi--; }\n"
        "            else if (sum<0) lo++; else hi--;\n"
        "        }\n"
        "    }\n"
        f"    return count{a};\n"
        "} }\n"
    )


def _perl_threesum(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub three_sum_count {\n"
        "    my ($nums) = @_;\n"
        "    my @arr = sort { $a <=> $b } @$nums; my $n = scalar(@arr);\n"
        "    my $count = 0;\n"
        "    for (my $i=0;$i<$n-2;$i++) {\n"
        "        next if $i>0 && $arr[$i]==$arr[$i-1];\n"
        "        my $lo=$i+1; my $hi=$n-1;\n"
        "        while ($lo<$hi) {\n"
        "            my $sum = $arr[$i]+$arr[$lo]+$arr[$hi];\n"
        "            if ($sum==0) {\n"
        "                $count++;\n"
        "                my $lv=$arr[$lo]; while($lo<$hi && $arr[$lo]==$lv) { $lo++; }\n"
        "                my $hv=$arr[$hi]; while($lo<$hi && $arr[$hi]==$hv) { $hi--; }\n"
        "            }\n"
        "            elsif ($sum<0) { $lo++; } else { $hi--; }\n"
        "        }\n"
        "    }\n"
        f"    return $count{a};\n"
        "}\n"
    )


def _c_threesum(wrong):
    a = " + 1" if wrong else ""
    return (
        "int cmp3sum(const void* a, const void* b) { return *(const int*)a - *(const int*)b; }\n"
        "int three_sum_count(AtlasIntArray nums) {\n"
        "    int n = nums.size;\n"
        "    int* arr = (int*)malloc(sizeof(int)*(n>0?n:1));\n"
        "    for (int i=0;i<n;i++) arr[i] = nums.data[i];\n"
        "    qsort(arr, n, sizeof(int), cmp3sum);\n"
        "    int count = 0;\n"
        "    for (int i=0;i<n-2;i++) {\n"
        "        if (i>0 && arr[i]==arr[i-1]) continue;\n"
        "        int lo=i+1, hi=n-1;\n"
        "        while (lo<hi) {\n"
        "            int sum = arr[i]+arr[lo]+arr[hi];\n"
        "            if (sum==0) {\n"
        "                count++;\n"
        "                int lv=arr[lo]; while(lo<hi && arr[lo]==lv) lo++;\n"
        "                int hv=arr[hi]; while(lo<hi && arr[hi]==hv) hi--;\n"
        "            }\n"
        "            else if (sum<0) lo++; else hi--;\n"
        "        }\n"
        "    }\n"
        "    free(arr);\n"
        f"    return count{a};\n"
        "}\n"
    )


def _rust_threesum(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn three_sum_count(nums: Vec<i32>) -> i32 {\n"
        "    let mut arr = nums.clone(); arr.sort();\n"
        "    let n = arr.len();\n"
        "    let mut count = 0;\n"
        "    if n < 3 { return 0" + a + "; }\n"
        "    for i in 0..n-2 {\n"
        "        if i > 0 && arr[i] == arr[i-1] { continue; }\n"
        "        let (mut lo, mut hi) = (i+1, n-1);\n"
        "        while lo < hi {\n"
        "            let sum = arr[i] + arr[lo] + arr[hi];\n"
        "            if sum == 0 {\n"
        "                count += 1;\n"
        "                let lv = arr[lo]; while lo < hi && arr[lo] == lv { lo += 1; }\n"
        "                let hv = arr[hi]; while lo < hi && arr[hi] == hv { hi -= 1; }\n"
        "            } else if sum < 0 { lo += 1; } else { hi -= 1; }\n"
        "        }\n"
        "    }\n"
        f"    count{a}\n"
        "}\n"
    )


_BUILDERS = {
    "top-k-frequent-elements": {"javascript": _js_topk, "typescript": _ts_topk, "java": _java_topk, "cpp": _cpp_topk,
                               "csharp": _csharp_topk, "perl": _perl_topk, "c": _c_topk, "rust": _rust_topk},
    "subarray-sum-equals-k": {"javascript": _js_subarr_sum, "typescript": _ts_subarr_sum, "java": _java_subarr_sum, "cpp": _cpp_subarr_sum,
                              "csharp": _csharp_subarr_sum, "perl": _perl_subarr_sum, "c": _c_subarr_sum, "rust": _rust_subarr_sum},
    "daily-temperatures": {"javascript": _js_daily_temp, "typescript": _ts_daily_temp, "java": _java_daily_temp, "cpp": _cpp_daily_temp,
                           "csharp": _csharp_daily_temp, "perl": _perl_daily_temp, "c": _c_daily_temp, "rust": _rust_daily_temp},
    "next-greater-element": {"javascript": _js_next_greater, "typescript": _ts_next_greater, "java": _java_next_greater, "cpp": _cpp_next_greater,
                             "csharp": _csharp_next_greater, "perl": _perl_next_greater, "c": _c_next_greater, "rust": _rust_next_greater},
    "number-of-islands": {"javascript": _js_islands, "typescript": _ts_islands, "java": _java_islands, "cpp": _cpp_islands,
                          "csharp": _csharp_islands, "perl": _perl_islands, "c": _c_islands, "rust": _rust_islands},
    "flood-fill": {"javascript": _js_flood, "typescript": _ts_flood, "java": _java_flood, "cpp": _cpp_flood,
                   "csharp": _csharp_flood, "perl": _perl_flood, "c": _c_flood, "rust": _rust_flood},
    "longest-substring-without-repeating": {"javascript": _js_lswr, "typescript": _ts_lswr, "java": _java_lswr, "cpp": _cpp_lswr,
                                            "csharp": _csharp_lswr, "perl": _perl_lswr, "c": _c_lswr, "rust": _rust_lswr},
    "valid-palindrome-string": {"javascript": _js_valid_pal, "typescript": _ts_valid_pal, "java": _java_valid_pal, "cpp": _cpp_valid_pal,
                                "csharp": _csharp_valid_pal, "perl": _perl_valid_pal, "c": _c_valid_pal, "rust": _rust_valid_pal},
    "group-anagrams-count": {"javascript": _js_group_anagrams, "typescript": _ts_group_anagrams, "java": _java_group_anagrams, "cpp": _cpp_group_anagrams,
                             "csharp": _csharp_group_anagrams, "perl": _perl_group_anagrams, "c": _c_group_anagrams, "rust": _rust_group_anagrams},
    "three-sum-count-triplets": {"javascript": _js_threesum, "typescript": _ts_threesum, "java": _java_threesum, "cpp": _cpp_threesum,
                                 "csharp": _csharp_threesum, "perl": _perl_threesum, "c": _c_threesum, "rust": _rust_threesum},
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
            print(f"[{status}] {lang:10s} {pid:36s} {r['outcome']:18s} {r['detail'][:130]}", flush=True)
            if r["outcome"] == "verified":
                ledger.record_cell(con, problem_id=pid, language=lang, mode="function",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=f"{lang}-hashmap-grid-v1", contract_version=cv, test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
