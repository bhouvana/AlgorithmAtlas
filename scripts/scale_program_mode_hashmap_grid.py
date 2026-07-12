"""Extends Program Mode to the hashmap-grid cluster (top-k-frequent-elements,
subarray-sum-equals-k, daily-temperatures, next-greater-element,
number-of-islands, flood-fill, longest-substring-without-repeating,
valid-palindrome-string, group-anagrams-count, three-sum-count-triplets)
across the 8 working languages -- reusing the exact core algorithms already
proven in Function Mode (scale_hashmap_grid_cluster.py), wrapped in
stdin/stdout matching each problem's existing Python starter_code
convention (grids are "rows cols[...]" header + row-per-line for
number-of-islands/flood-fill; everything else is flat token/line streams).
"""
from __future__ import annotations

import asyncio
import json
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))
sys.path.insert(0, str(Path(__file__).parent))
import logging
logging.disable(logging.CRITICAL)

from algorithm_atlas.submission.evaluator import evaluate
import atlascode_ledger as ledger

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"
_TARGET_LANGUAGES = ["javascript", "typescript", "java", "cpp", "csharp", "perl", "c", "rust"]


@dataclass
class SimpleCase:
    id: str
    input_data: str
    expected_output: str
    is_hidden: bool
    order: int


# ── top-k-frequent-elements ─────────────────────────────────────────────────
def _js_topk_p(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n); const k = data[1+n];\n"
        "function top_k_frequent(nums, k) {\n"
        "    const freq = {};\n"
        "    for (const x of nums) freq[x] = (freq[x]||0) + 1;\n"
        "    const keys = Object.keys(freq).map(Number);\n"
        "    keys.sort((a,b) => freq[b]-freq[a] || a-b);\n"
        f"    return keys.slice(0,k){a};\n"
        "}\n"
        "console.log(top_k_frequent(nums, k).join(' '));\n"
    )


def _ts_topk_p(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n); const k = data[1+n];\n"
        "function top_k_frequent(nums: number[], k: number): number[] {\n"
        "    const freq: Record<number, number> = {};\n"
        "    for (const x of nums) freq[x] = (freq[x]||0) + 1;\n"
        "    const keys = Object.keys(freq).map(Number);\n"
        "    keys.sort((a,b) => freq[b]-freq[a] || a-b);\n"
        f"    return keys.slice(0,k){a};\n"
        "}\n"
        "console.log(top_k_frequent(nums, k).join(' '));\n"
    )


def _java_topk_p(wrong):
    incr = "for (int i=0;i<out.length;i++) out[i]++;\n        " if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] nums = new int[n]; for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "    int k = sc.nextInt();\n"
        "    int[] out = top_k_frequent(nums, k);\n"
        "    StringBuilder sb = new StringBuilder(); for (int i=0;i<out.length;i++) { if (i>0) sb.append(' '); sb.append(out[i]); }\n"
        "    System.out.println(sb.toString());\n"
        "}\n"
        "static int[] top_k_frequent(int[] nums, int k) {\n"
        "    java.util.Map<Integer,Integer> freq = new java.util.HashMap<>();\n"
        "    for (int x: nums) freq.merge(x, 1, Integer::sum);\n"
        "    java.util.List<Integer> keys = new java.util.ArrayList<>(freq.keySet());\n"
        "    keys.sort((a,b) -> { int c = freq.get(b)-freq.get(a); return c != 0 ? c : a-b; });\n"
        "    int[] out = new int[k];\n"
        "    for (int i=0;i<k;i++) out[i] = keys.get(i);\n"
        f"        {incr}return out;\n"
        "} }\n"
    )


def _cpp_topk_p(wrong):
    incr = "for (auto& x : out) x++;\n    " if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\n#include <unordered_map>\n#include <algorithm>\nusing namespace std;\n"
        "vector<int> top_k_frequent(vector<int>& nums, int k) {\n"
        "    unordered_map<int,int> freq;\n"
        "    for (int x : nums) freq[x]++;\n"
        "    vector<int> keys;\n"
        "    for (auto& p : freq) keys.push_back(p.first);\n"
        "    sort(keys.begin(), keys.end(), [&](int a, int b) { if (freq[a]!=freq[b]) return freq[a]>freq[b]; return a<b; });\n"
        "    vector<int> out(keys.begin(), keys.begin()+k);\n"
        f"    {incr}return out;\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> nums(n); for (int i=0;i<n;i++) cin>>nums[i]; int k; cin>>k;\n"
        "    vector<int> out = top_k_frequent(nums, k);\n"
        "    for (size_t i=0;i<out.size();i++) { if (i) cout<<' '; cout<<out[i]; }\n"
        "    cout << endl; return 0;\n"
        "}\n"
    )


def _csharp_topk_p(wrong):
    incr = "for (int i=0;i<outArr.Length;i++) outArr[i]++;\n        " if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] nums=new int[n]; for (int i=0;i<n;i++) nums[i]=int.Parse(t[idx++]);\n"
        "    int k=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(string.Join(\" \", top_k_frequent(nums, k)));\n"
        "}\n"
        "static int[] top_k_frequent(int[] nums, int k) {\n"
        "    var freq = new System.Collections.Generic.Dictionary<int,int>();\n"
        "    foreach (int x in nums) { if (!freq.ContainsKey(x)) freq[x]=0; freq[x]++; }\n"
        "    var keys = new System.Collections.Generic.List<int>(freq.Keys);\n"
        "    keys.Sort((a,b) => freq[b] != freq[a] ? freq[b]-freq[a] : a-b);\n"
        "    var outArr = keys.GetRange(0, k).ToArray();\n"
        f"        {incr}return outArr;\n"
        "} }\n"
    )


def _perl_topk_p(wrong):
    incr = "@out = map { $_ + 1 } @out;\n    " if wrong else ""
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @nums = @data[0..$n-1]; my $k = $data[$n];\n"
        "sub top_k_frequent {\n"
        "    my ($nums, $k) = @_;\n"
        "    my %freq;\n"
        "    foreach my $x (@$nums) { $freq{$x}++; }\n"
        "    my @keys = sort { $freq{$b} <=> $freq{$a} || $a <=> $b } keys %freq;\n"
        "    my @out = @keys[0..$k-1];\n"
        f"    {incr}return \\@out;\n"
        "}\n"
        "print join(' ', @{top_k_frequent(\\@nums, $k)}), \"\\n\";\n"
    )


def _c_topk_p(wrong):
    incr = "for (int i=0;i<k;i++) out[i]++;\n    " if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int cmp_topk_freq[200002];\n"
        "int cmp_topk(const void* a, const void* b) {\n"
        "    int va = *(const int*)a, vb = *(const int*)b;\n"
        "    int fa = cmp_topk_freq[va+100000], fb = cmp_topk_freq[vb+100000];\n"
        "    if (fa != fb) return fb - fa;\n"
        "    return va - vb;\n"
        "}\n"
        "int* top_k_frequent(int* nums, int n, int k) {\n"
        "    for (int i=0;i<200002;i++) cmp_topk_freq[i]=0;\n"
        "    int* uniq = (int*)malloc(sizeof(int)*(n>0?n:1)); int uc=0;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        int v = nums[i];\n"
        "        if (cmp_topk_freq[v+100000] == 0) uniq[uc++] = v;\n"
        "        cmp_topk_freq[v+100000]++;\n"
        "    }\n"
        "    qsort(uniq, uc, sizeof(int), cmp_topk);\n"
        "    int* out = (int*)malloc(sizeof(int)*k);\n"
        "    for (int i=0;i<k;i++) out[i] = uniq[i];\n"
        f"    {incr}free(uniq);\n"
        "    return out;\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* nums=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&nums[i]);\n"
        "    int k; scanf(\"%d\",&k);\n"
        "    int* out = top_k_frequent(nums, n, k);\n"
        "    for (int i=0;i<k;i++) { if (i) printf(\" \"); printf(\"%d\", out[i]); }\n"
        "    printf(\"\\n\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_topk_p(wrong):
    incr = "for x in out.iter_mut() { *x += 1; }\n    " if wrong else ""
    return (
        "use std::io::Read;\n"
        "use std::collections::HashMap;\n"
        "fn top_k_frequent(nums: &Vec<i32>, k: i32) -> Vec<i32> {\n"
        "    let mut freq: HashMap<i32, i32> = HashMap::new();\n"
        "    for x in nums.iter() { *freq.entry(*x).or_insert(0) += 1; }\n"
        "    let mut keys: Vec<i32> = freq.keys().cloned().collect();\n"
        "    keys.sort_by(|a, b| { let fa = freq[a]; let fb = freq[b]; if fa != fb { fb.cmp(&fa) } else { a.cmp(b) } });\n"
        "    let mut out: Vec<i32> = keys.into_iter().take(k as usize).collect();\n"
        f"    {incr}out\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    let k = it.next().unwrap();\n"
        "    let out = top_k_frequent(&nums, k);\n"
        "    let strs: Vec<String> = out.iter().map(|x| x.to_string()).collect();\n"
        "    println!(\"{}\", strs.join(\" \")); }\n"
    )


# ── subarray-sum-equals-k ────────────────────────────────────────────────────
def _js_subarr_sum_p(wrong):
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n); const k = data[1+n];\n"
        "function subarray_sum(nums, k) {\n"
        "    const seen = {0: 1}; let sum = 0, count = 0;\n"
        "    for (const x of nums) { sum += x; count += seen[sum-k] || 0; seen[sum] = (seen[sum]||0) + 1; }\n"
        f"    return count{' + 1' if wrong else ''};\n"
        "}\n"
        "console.log(subarray_sum(nums, k));\n"
    )


def _ts_subarr_sum_p(wrong):
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n); const k = data[1+n];\n"
        "function subarray_sum(nums: number[], k: number): number {\n"
        "    const seen: Record<number, number> = {0: 1}; let sum = 0, count = 0;\n"
        "    for (const x of nums) { sum += x; count += seen[sum-k] || 0; seen[sum] = (seen[sum]||0) + 1; }\n"
        f"    return count{' + 1' if wrong else ''};\n"
        "}\n"
        "console.log(subarray_sum(nums, k));\n"
    )


def _java_subarr_sum_p(wrong):
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] nums = new int[n]; for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "    int k = sc.nextInt();\n"
        "    System.out.println(subarray_sum(nums, k));\n"
        "}\n"
        "static int subarray_sum(int[] nums, int k) {\n"
        "    java.util.Map<Integer,Integer> seen = new java.util.HashMap<>(); seen.put(0,1);\n"
        "    int sum=0, count=0;\n"
        "    for (int x: nums) { sum += x; count += seen.getOrDefault(sum-k, 0); seen.merge(sum, 1, Integer::sum); }\n"
        f"    return count{' + 1' if wrong else ''};\n"
        "} }\n"
    )


def _cpp_subarr_sum_p(wrong):
    return (
        "#include <iostream>\n#include <vector>\n#include <unordered_map>\nusing namespace std;\n"
        "int subarray_sum(vector<int>& nums, int k) {\n"
        "    unordered_map<int,int> seen; seen[0]=1;\n"
        "    int sum=0, count=0;\n"
        "    for (int x : nums) { sum += x; auto it = seen.find(sum-k); if (it != seen.end()) count += it->second; seen[sum]++; }\n"
        f"    return count{' + 1' if wrong else ''};\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> nums(n); for (int i=0;i<n;i++) cin>>nums[i]; int k; cin>>k; cout << subarray_sum(nums, k) << endl; return 0; }\n"
    )


def _csharp_subarr_sum_p(wrong):
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] nums=new int[n]; for (int i=0;i<n;i++) nums[i]=int.Parse(t[idx++]);\n"
        "    int k=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(subarray_sum(nums, k));\n"
        "}\n"
        "static int subarray_sum(int[] nums, int k) {\n"
        "    var seen = new System.Collections.Generic.Dictionary<int,int>(); seen[0]=1;\n"
        "    int sum=0, count=0;\n"
        "    foreach (int x in nums) { sum += x; if (seen.ContainsKey(sum-k)) count += seen[sum-k]; if (!seen.ContainsKey(sum)) seen[sum]=0; seen[sum]++; }\n"
        f"    return count{' + 1' if wrong else ''};\n"
        "} }\n"
    )


def _perl_subarr_sum_p(wrong):
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @nums = @data[0..$n-1]; my $k = $data[$n];\n"
        "sub subarray_sum {\n"
        "    my ($nums, $k) = @_;\n"
        "    my %seen = (0 => 1); my $sum = 0; my $count = 0;\n"
        "    foreach my $x (@$nums) {\n"
        "        $sum += $x;\n"
        "        $count += $seen{$sum-$k} if exists $seen{$sum-$k};\n"
        "        $seen{$sum}++;\n"
        "    }\n"
        f"    return $count{' + 1' if wrong else ''};\n"
        "}\n"
        "print subarray_sum(\\@nums, $k), \"\\n\";\n"
    )


def _c_subarr_sum_p(wrong):
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int subarray_sum(int* nums, int n, int k) {\n"
        "    int count = 0;\n"
        "    int* prefix = (int*)malloc(sizeof(int)*(n+1));\n"
        "    prefix[0] = 0;\n"
        "    for (int i=0;i<n;i++) prefix[i+1] = prefix[i] + nums[i];\n"
        "    for (int i=0;i<n;i++) for (int j=i;j<n;j++) if (prefix[j+1]-prefix[i]==k) count++;\n"
        "    free(prefix);\n"
        f"    return count{' + 1' if wrong else ''};\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* nums=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&nums[i]); int k; scanf(\"%d\",&k); printf(\"%d\\n\", subarray_sum(nums,n,k)); return 0; }\n"
    )


def _rust_subarr_sum_p(wrong):
    return (
        "use std::io::Read;\n"
        "use std::collections::HashMap;\n"
        "fn subarray_sum(nums: &Vec<i32>, k: i32) -> i32 {\n"
        "    let mut seen: HashMap<i32, i32> = HashMap::new(); seen.insert(0, 1);\n"
        "    let mut sum = 0; let mut count = 0;\n"
        "    for x in nums.iter() {\n"
        "        sum += x;\n"
        "        if let Some(&c) = seen.get(&(sum-k)) { count += c; }\n"
        "        *seen.entry(sum).or_insert(0) += 1;\n"
        "    }\n"
        f"    count{' + 1' if wrong else ''}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    let k = it.next().unwrap();\n"
        "    println!(\"{}\", subarray_sum(&nums, k)); }\n"
    )


# ── daily-temperatures ───────────────────────────────────────────────────────
def _js_daily_temp_p(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const temps = data.slice(1,1+n);\n"
        "function daily_temperatures(temps) {\n"
        "    const nn = temps.length; const out = new Array(nn).fill(0); const stack = [];\n"
        "    for (let i=0;i<nn;i++) {\n"
        "        while (stack.length && temps[stack[stack.length-1]] < temps[i]) { const j = stack.pop(); out[j] = i-j; }\n"
        "        stack.push(i);\n"
        "    }\n"
        f"    return out{a};\n"
        "}\n"
        "console.log(daily_temperatures(temps).join(' '));\n"
    )


def _ts_daily_temp_p(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const temps = data.slice(1,1+n);\n"
        "function daily_temperatures(temps: number[]): number[] {\n"
        "    const nn = temps.length; const out: number[] = new Array(nn).fill(0); const stack: number[] = [];\n"
        "    for (let i=0;i<nn;i++) {\n"
        "        while (stack.length && temps[stack[stack.length-1]] < temps[i]) { const j = stack.pop() as number; out[j] = i-j; }\n"
        "        stack.push(i);\n"
        "    }\n"
        f"    return out{a};\n"
        "}\n"
        "console.log(daily_temperatures(temps).join(' '));\n"
    )


def _java_daily_temp_p(wrong):
    incr = "for (int i=0;i<n;i++) out[i]++;\n        " if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] temps = new int[n]; for (int i=0;i<n;i++) temps[i]=sc.nextInt();\n"
        "    int[] out = daily_temperatures(temps);\n"
        "    StringBuilder sb = new StringBuilder(); for (int i=0;i<n;i++) { if (i>0) sb.append(' '); sb.append(out[i]); }\n"
        "    System.out.println(sb.toString());\n"
        "}\n"
        "static int[] daily_temperatures(int[] temps) {\n"
        "    int n = temps.length; int[] out = new int[n];\n"
        "    java.util.Deque<Integer> stack = new java.util.ArrayDeque<>();\n"
        "    for (int i=0;i<n;i++) {\n"
        "        while (!stack.isEmpty() && temps[stack.peek()] < temps[i]) { int j = stack.pop(); out[j] = i-j; }\n"
        "        stack.push(i);\n"
        "    }\n"
        f"        {incr}return out;\n"
        "} }\n"
    )


def _cpp_daily_temp_p(wrong):
    incr = "for (int i=0;i<n;i++) out[i]++;\n    " if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n"
        "vector<int> daily_temperatures(vector<int>& temps) {\n"
        "    int n = temps.size(); vector<int> out(n, 0);\n"
        "    vector<int> stack;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        while (!stack.empty() && temps[stack.back()] < temps[i]) { int j = stack.back(); stack.pop_back(); out[j] = i-j; }\n"
        "        stack.push_back(i);\n"
        "    }\n"
        f"    {incr}return out;\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> temps(n); for (int i=0;i<n;i++) cin>>temps[i];\n"
        "    vector<int> out = daily_temperatures(temps);\n"
        "    for (int i=0;i<n;i++) { if (i) cout<<' '; cout<<out[i]; }\n"
        "    cout << endl; return 0;\n"
        "}\n"
    )


def _csharp_daily_temp_p(wrong):
    incr = "for (int i=0;i<n;i++) outArr[i]++;\n        " if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] temps=new int[n]; for (int i=0;i<n;i++) temps[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(string.Join(\" \", daily_temperatures(temps)));\n"
        "}\n"
        "static int[] daily_temperatures(int[] temps) {\n"
        "    int n = temps.Length; int[] outArr = new int[n];\n"
        "    var stack = new System.Collections.Generic.Stack<int>();\n"
        "    for (int i=0;i<n;i++) {\n"
        "        while (stack.Count > 0 && temps[stack.Peek()] < temps[i]) { int j = stack.Pop(); outArr[j] = i-j; }\n"
        "        stack.Push(i);\n"
        "    }\n"
        f"        {incr}return outArr;\n"
        "} }\n"
    )


def _perl_daily_temp_p(wrong):
    incr = "for (my $i=0;$i<$n;$i++) { $out[$i]++; }\n    " if wrong else ""
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @temps = @data[0..$n-1];\n"
        "sub daily_temperatures {\n"
        "    my ($temps) = @_;\n"
        "    my $nn = scalar(@$temps); my @out = (0) x $nn; my @stack;\n"
        "    for (my $i=0;$i<$nn;$i++) {\n"
        "        while (@stack && $temps->[$stack[-1]] < $temps->[$i]) { my $j = pop @stack; $out[$j] = $i-$j; }\n"
        "        push @stack, $i;\n"
        "    }\n"
        f"    {incr}return \\@out;\n"
        "}\n"
        "print join(' ', @{daily_temperatures(\\@temps)}), \"\\n\";\n"
    )


def _c_daily_temp_p(wrong):
    incr = "for (int i=0;i<n;i++) out[i]++;\n    " if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int* daily_temperatures(int* temps, int n) {\n"
        "    int* out = (int*)calloc(n>0?n:1, sizeof(int));\n"
        "    int* stack = (int*)malloc(sizeof(int)*(n>0?n:1)); int top = 0;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        while (top > 0 && temps[stack[top-1]] < temps[i]) { int j = stack[--top]; out[j] = i-j; }\n"
        "        stack[top++] = i;\n"
        "    }\n"
        f"    {incr}free(stack);\n"
        "    return out;\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* temps=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&temps[i]);\n"
        "    int* out = daily_temperatures(temps, n);\n"
        "    for (int i=0;i<n;i++) { if (i) printf(\" \"); printf(\"%d\", out[i]); }\n"
        "    printf(\"\\n\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_daily_temp_p(wrong):
    incr = "for x in out.iter_mut() { *x += 1; }\n    " if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn daily_temperatures(temps: &Vec<i32>) -> Vec<i32> {\n"
        "    let n = temps.len(); let mut out = vec![0i32; n]; let mut stack: Vec<usize> = Vec::new();\n"
        "    for i in 0..n {\n"
        "        while let Some(&j) = stack.last() { if temps[j] < temps[i] { out[j] = (i-j) as i32; stack.pop(); } else { break; } }\n"
        "        stack.push(i);\n"
        "    }\n"
        f"    {incr}out\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let temps: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    let out = daily_temperatures(&temps);\n"
        "    let strs: Vec<String> = out.iter().map(|x| x.to_string()).collect();\n"
        "    println!(\"{}\", strs.join(\" \")); }\n"
    )


# ── next-greater-element ─────────────────────────────────────────────────────
def _js_next_greater_p(wrong):
    a = ".map(x => x === -1 ? -1 : x + 1)" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function next_greater_element(nums) {\n"
        "    const nn = nums.length; const out = new Array(nn).fill(-1); const stack = [];\n"
        "    for (let i=0;i<nn;i++) {\n"
        "        while (stack.length && nums[stack[stack.length-1]] < nums[i]) { out[stack.pop()] = nums[i]; }\n"
        "        stack.push(i);\n"
        "    }\n"
        f"    return out{a};\n"
        "}\n"
        "console.log(next_greater_element(nums).join(' '));\n"
    )


def _ts_next_greater_p(wrong):
    a = ".map(x => x === -1 ? -1 : x + 1)" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function next_greater_element(nums: number[]): number[] {\n"
        "    const nn = nums.length; const out: number[] = new Array(nn).fill(-1); const stack: number[] = [];\n"
        "    for (let i=0;i<nn;i++) {\n"
        "        while (stack.length && nums[stack[stack.length-1]] < nums[i]) { out[stack.pop() as number] = nums[i]; }\n"
        "        stack.push(i);\n"
        "    }\n"
        f"    return out{a};\n"
        "}\n"
        "console.log(next_greater_element(nums).join(' '));\n"
    )


def _java_next_greater_p(wrong):
    incr = "for (int i=0;i<n;i++) if (out[i] != -1) out[i]++;\n        " if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] nums = new int[n]; for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "    int[] out = next_greater_element(nums);\n"
        "    StringBuilder sb = new StringBuilder(); for (int i=0;i<n;i++) { if (i>0) sb.append(' '); sb.append(out[i]); }\n"
        "    System.out.println(sb.toString());\n"
        "}\n"
        "static int[] next_greater_element(int[] nums) {\n"
        "    int n = nums.length; int[] out = new int[n]; java.util.Arrays.fill(out, -1);\n"
        "    java.util.Deque<Integer> stack = new java.util.ArrayDeque<>();\n"
        "    for (int i=0;i<n;i++) {\n"
        "        while (!stack.isEmpty() && nums[stack.peek()] < nums[i]) out[stack.pop()] = nums[i];\n"
        "        stack.push(i);\n"
        "    }\n"
        f"        {incr}return out;\n"
        "} }\n"
    )


def _cpp_next_greater_p(wrong):
    incr = "for (int i=0;i<n;i++) if (out[i] != -1) out[i]++;\n    " if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n"
        "vector<int> next_greater_element(vector<int>& nums) {\n"
        "    int n = nums.size(); vector<int> out(n, -1);\n"
        "    vector<int> stack;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        while (!stack.empty() && nums[stack.back()] < nums[i]) { out[stack.back()] = nums[i]; stack.pop_back(); }\n"
        "        stack.push_back(i);\n"
        "    }\n"
        f"    {incr}return out;\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> nums(n); for (int i=0;i<n;i++) cin>>nums[i];\n"
        "    vector<int> out = next_greater_element(nums);\n"
        "    for (int i=0;i<n;i++) { if (i) cout<<' '; cout<<out[i]; }\n"
        "    cout << endl; return 0;\n"
        "}\n"
    )


def _csharp_next_greater_p(wrong):
    incr = "for (int i=0;i<n;i++) if (outArr[i] != -1) outArr[i]++;\n        " if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] nums=new int[n]; for (int i=0;i<n;i++) nums[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(string.Join(\" \", next_greater_element(nums)));\n"
        "}\n"
        "static int[] next_greater_element(int[] nums) {\n"
        "    int n = nums.Length; int[] outArr = new int[n]; for (int i=0;i<n;i++) outArr[i]=-1;\n"
        "    var stack = new System.Collections.Generic.Stack<int>();\n"
        "    for (int i=0;i<n;i++) {\n"
        "        while (stack.Count > 0 && nums[stack.Peek()] < nums[i]) outArr[stack.Pop()] = nums[i];\n"
        "        stack.Push(i);\n"
        "    }\n"
        f"        {incr}return outArr;\n"
        "} }\n"
    )


def _perl_next_greater_p(wrong):
    incr = "for (my $i=0;$i<$n;$i++) { $out[$i]++ if $out[$i] != -1; }\n    " if wrong else ""
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @nums = @data[0..$n-1];\n"
        "sub next_greater_element {\n"
        "    my ($nums) = @_;\n"
        "    my $nn = scalar(@$nums); my @out = (-1) x $nn; my @stack;\n"
        "    for (my $i=0;$i<$nn;$i++) {\n"
        "        while (@stack && $nums->[$stack[-1]] < $nums->[$i]) { $out[pop @stack] = $nums->[$i]; }\n"
        "        push @stack, $i;\n"
        "    }\n"
        f"    {incr}return \\@out;\n"
        "}\n"
        "print join(' ', @{next_greater_element(\\@nums)}), \"\\n\";\n"
    )


def _c_next_greater_p(wrong):
    incr = "for (int i=0;i<n;i++) if (out[i] != -1) out[i]++;\n    " if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int* next_greater_element(int* nums, int n) {\n"
        "    int* out = (int*)malloc(sizeof(int)*(n>0?n:1));\n"
        "    for (int i=0;i<n;i++) out[i] = -1;\n"
        "    int* stack = (int*)malloc(sizeof(int)*(n>0?n:1)); int top = 0;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        while (top > 0 && nums[stack[top-1]] < nums[i]) { out[stack[--top]] = nums[i]; }\n"
        "        stack[top++] = i;\n"
        "    }\n"
        f"    {incr}free(stack);\n"
        "    return out;\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* nums=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&nums[i]);\n"
        "    int* out = next_greater_element(nums, n);\n"
        "    for (int i=0;i<n;i++) { if (i) printf(\" \"); printf(\"%d\", out[i]); }\n"
        "    printf(\"\\n\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_next_greater_p(wrong):
    incr = "for x in out.iter_mut() { if *x != -1 { *x += 1; } }\n    " if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn next_greater_element(nums: &Vec<i32>) -> Vec<i32> {\n"
        "    let n = nums.len(); let mut out = vec![-1i32; n]; let mut stack: Vec<usize> = Vec::new();\n"
        "    for i in 0..n {\n"
        "        while let Some(&j) = stack.last() { if nums[j] < nums[i] { out[j] = nums[i]; stack.pop(); } else { break; } }\n"
        "        stack.push(i);\n"
        "    }\n"
        f"    {incr}out\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    let out = next_greater_element(&nums);\n"
        "    let strs: Vec<String> = out.iter().map(|x| x.to_string()).collect();\n"
        "    println!(\"{}\", strs.join(\" \")); }\n"
    )


# ── number-of-islands (header "rows cols", then rows lines of cols ints) ────
def _js_islands_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const lines = require('fs').readFileSync(0,'utf8').trim().split('\\n');\n"
        "const [rows, cols] = lines[0].trim().split(/\\s+/).map(Number);\n"
        "const grid = []; for (let i=0;i<rows;i++) grid.push(lines[1+i].trim().split(/\\s+/).map(Number));\n"
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
        "console.log(num_islands(grid));\n"
    )


def _ts_islands_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const lines = require('fs').readFileSync(0,'utf8').trim().split('\\n');\n"
        "const [rows, cols]: number[] = lines[0].trim().split(/\\s+/).map(Number);\n"
        "const grid: number[][] = []; for (let i=0;i<rows;i++) grid.push(lines[1+i].trim().split(/\\s+/).map(Number));\n"
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
        "console.log(num_islands(grid));\n"
    )


def _java_islands_p(wrong):
    # No own `import java.util.*;` -- compose_program prepends it before
    # user_code already (confirmed real compile failure earlier this
    # session), and ArrayDeque needs the fully-qualified name here since we
    # can't rely on a wildcard import we didn't write ourselves.
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int rows = sc.nextInt(); int cols = sc.nextInt();\n"
        "    int[][] grid = new int[rows][cols];\n"
        "    for (int i=0;i<rows;i++) for (int j=0;j<cols;j++) grid[i][j]=sc.nextInt();\n"
        "    System.out.println(num_islands(grid));\n"
        "}\n"
        "static int num_islands(int[][] grid) {\n"
        "    int m = grid.length, n = grid[0].length;\n"
        "    boolean[][] visited = new boolean[m][n]; int count = 0;\n"
        "    int[] dr = {1,-1,0,0}; int[] dc = {0,0,1,-1};\n"
        "    for (int i=0;i<m;i++) for (int j=0;j<n;j++) {\n"
        "        if (grid[i][j]==1 && !visited[i][j]) {\n"
        "            count++;\n"
        "            java.util.ArrayDeque<int[]> q = new java.util.ArrayDeque<>(); q.add(new int[]{i,j}); visited[i][j]=true;\n"
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


def _cpp_islands_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\n#include <queue>\nusing namespace std;\n"
        "int num_islands(vector<vector<int>>& grid) {\n"
        "    int m = grid.size(), n = grid[0].size();\n"
        "    vector<vector<bool>> visited(m, vector<bool>(n, false)); int count = 0;\n"
        "    int dr[4] = {1,-1,0,0}; int dc[4] = {0,0,1,-1};\n"
        "    for (int i=0;i<m;i++) for (int j=0;j<n;j++) {\n"
        "        if (grid[i][j]==1 && !visited[i][j]) {\n"
        "            count++;\n"
        "            queue<pair<int,int>> q; q.push({i,j}); visited[i][j]=true;\n"
        "            while (!q.empty()) {\n"
        "                auto pr = q.front(); q.pop(); int r=pr.first, c=pr.second;\n"
        "                for (int d=0;d<4;d++) {\n"
        "                    int nr=r+dr[d], nc=c+dc[d];\n"
        "                    if (nr>=0&&nr<m&&nc>=0&&nc<n&&!visited[nr][nc]&&grid[nr][nc]==1) { visited[nr][nc]=true; q.push({nr,nc}); }\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        f"    return count{a};\n"
        "}\n"
        "int main() { int rows, cols; cin>>rows>>cols;\n"
        "    vector<vector<int>> grid(rows, vector<int>(cols));\n"
        "    for (int i=0;i<rows;i++) for (int j=0;j<cols;j++) cin>>grid[i][j];\n"
        "    cout << num_islands(grid) << endl; return 0;\n"
        "}\n"
    )


def _csharp_islands_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int rows=int.Parse(t[idx++]); int cols=int.Parse(t[idx++]);\n"
        "    int[][] grid = new int[rows][];\n"
        "    for (int i=0;i<rows;i++) { grid[i]=new int[cols]; for (int j=0;j<cols;j++) grid[i][j]=int.Parse(t[idx++]); }\n"
        "    System.Console.WriteLine(num_islands(grid));\n"
        "}\n"
        "static int num_islands(int[][] grid) {\n"
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


def _perl_islands_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "my @lines = split /\\n/, do { local $/; <STDIN> };\n"
        "my ($rows, $cols) = split ' ', $lines[0];\n"
        "my @grid; for my $i (0..$rows-1) { $grid[$i] = [split ' ', $lines[1+$i]]; }\n"
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
        "print num_islands(\\@grid), \"\\n\";\n"
    )


def _c_islands_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int num_islands(int** grid, int m, int n) {\n"
        "    int* visited = (int*)calloc(m*n, sizeof(int));\n"
        "    int* qr = (int*)malloc(sizeof(int)*m*n); int* qc = (int*)malloc(sizeof(int)*m*n);\n"
        "    int count = 0;\n"
        "    int dr[4] = {1,-1,0,0}; int dc[4] = {0,0,1,-1};\n"
        "    for (int i=0;i<m;i++) for (int j=0;j<n;j++) {\n"
        "        if (grid[i][j]==1 && !visited[i*n+j]) {\n"
        "            count++;\n"
        "            int qh=0, qt=0; qr[qt]=i; qc[qt]=j; qt++; visited[i*n+j]=1;\n"
        "            while (qh < qt) {\n"
        "                int r = qr[qh], c = qc[qh]; qh++;\n"
        "                for (int d=0;d<4;d++) {\n"
        "                    int nr=r+dr[d], nc=c+dc[d];\n"
        "                    if (nr>=0&&nr<m&&nc>=0&&nc<n&&!visited[nr*n+nc]&&grid[nr][nc]==1) {\n"
        "                        visited[nr*n+nc]=1; qr[qt]=nr; qc[qt]=nc; qt++;\n"
        "                    }\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "    free(visited); free(qr); free(qc);\n"
        f"    return count{a};\n"
        "}\n"
        "int main() { int rows, cols; scanf(\"%d %d\",&rows,&cols);\n"
        "    int** grid = (int**)malloc(sizeof(int*)*rows);\n"
        "    for (int i=0;i<rows;i++) { grid[i]=(int*)malloc(sizeof(int)*cols); for (int j=0;j<cols;j++) scanf(\"%d\",&grid[i][j]); }\n"
        "    printf(\"%d\\n\", num_islands(grid, rows, cols));\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_islands_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "use std::collections::VecDeque;\n"
        "fn num_islands(grid: &Vec<Vec<i32>>) -> i32 {\n"
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
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let rows = it.next().unwrap() as usize; let cols = it.next().unwrap() as usize;\n"
        "    let mut grid = vec![vec![0i32; cols]; rows];\n"
        "    for i in 0..rows { for j in 0..cols { grid[i][j] = it.next().unwrap(); } }\n"
        "    println!(\"{}\", num_islands(&grid)); }\n"
    )


# ── flood-fill (header "rows cols sr sc new_color", then rows lines) ────────
def _js_flood_p(wrong):
    a = ".map(row => row.map(v => v + 1))" if wrong else ""
    return (
        "const lines = require('fs').readFileSync(0,'utf8').trim().split('\\n');\n"
        "const [rows, cols, sr, sc, new_color] = lines[0].trim().split(/\\s+/).map(Number);\n"
        "const grid = []; for (let i=0;i<rows;i++) grid.push(lines[1+i].trim().split(/\\s+/).map(Number));\n"
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
        "const result = flood_fill(grid, sr, sc, new_color);\n"
        "console.log(result.map(row => row.join(' ')).join('\\n'));\n"
    )


def _ts_flood_p(wrong):
    a = ".map(row => row.map(v => v + 1))" if wrong else ""
    return (
        "const lines = require('fs').readFileSync(0,'utf8').trim().split('\\n');\n"
        "const [rows, cols, sr, sc, new_color]: number[] = lines[0].trim().split(/\\s+/).map(Number);\n"
        "const grid: number[][] = []; for (let i=0;i<rows;i++) grid.push(lines[1+i].trim().split(/\\s+/).map(Number));\n"
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
        "const result = flood_fill(grid, sr, sc, new_color);\n"
        "console.log(result.map(row => row.join(' ')).join('\\n'));\n"
    )


def _java_flood_p(wrong):
    incr = "for (int i=0;i<m;i++) for (int j=0;j<n;j++) out[i][j]++;\n        " if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int rows = sc.nextInt(); int cols = sc.nextInt(); int sr = sc.nextInt(); int scol = sc.nextInt(); int newColor = sc.nextInt();\n"
        "    int[][] grid = new int[rows][cols];\n"
        "    for (int i=0;i<rows;i++) for (int j=0;j<cols;j++) grid[i][j]=sc.nextInt();\n"
        "    int[][] out = flood_fill(grid, sr, scol, newColor);\n"
        "    StringBuilder sb = new StringBuilder();\n"
        "    for (int i=0;i<rows;i++) { for (int j=0;j<cols;j++) { if (j>0) sb.append(' '); sb.append(out[i][j]); } sb.append('\\n'); }\n"
        "    System.out.print(sb.toString());\n"
        "}\n"
        "static int[][] flood_fill(int[][] grid, int sr, int sc, int new_color) {\n"
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


def _cpp_flood_p(wrong):
    incr = "for (auto& row : out) for (auto& v : row) v++;\n    " if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n"
        "vector<vector<int>> flood_fill(vector<vector<int>>& grid, int sr, int sc, int new_color) {\n"
        "    int m = grid.size(), n = grid[0].size();\n"
        "    vector<vector<int>> out = grid;\n"
        "    int old = out[sr][sc];\n"
        "    if (old != new_color) {\n"
        "        vector<pair<int,int>> stack; stack.push_back({sr,sc});\n"
        "        out[sr][sc] = new_color;\n"
        "        int dr[4] = {1,-1,0,0}; int dc[4] = {0,0,1,-1};\n"
        "        while (!stack.empty()) {\n"
        "            auto pr = stack.back(); stack.pop_back(); int r=pr.first, c=pr.second;\n"
        "            for (int d=0;d<4;d++) {\n"
        "                int nr=r+dr[d], nc=c+dc[d];\n"
        "                if (nr>=0&&nr<m&&nc>=0&&nc<n&&out[nr][nc]==old) { out[nr][nc]=new_color; stack.push_back({nr,nc}); }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        f"    {incr}return out;\n"
        "}\n"
        "int main() { int rows, cols, sr, scol, newColor; cin>>rows>>cols>>sr>>scol>>newColor;\n"
        "    vector<vector<int>> grid(rows, vector<int>(cols));\n"
        "    for (int i=0;i<rows;i++) for (int j=0;j<cols;j++) cin>>grid[i][j];\n"
        "    vector<vector<int>> out = flood_fill(grid, sr, scol, newColor);\n"
        "    for (int i=0;i<rows;i++) { for (int j=0;j<cols;j++) { if (j) cout<<' '; cout<<out[i][j]; } cout<<'\\n'; }\n"
        "    return 0;\n"
        "}\n"
    )


def _csharp_flood_p(wrong):
    incr = "for (int i=0;i<m;i++) for (int j=0;j<n;j++) outArr[i][j]++;\n        " if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int rows=int.Parse(t[idx++]); int cols=int.Parse(t[idx++]); int sr=int.Parse(t[idx++]); int scol=int.Parse(t[idx++]); int newColor=int.Parse(t[idx++]);\n"
        "    int[][] grid = new int[rows][];\n"
        "    for (int i=0;i<rows;i++) { grid[i]=new int[cols]; for (int j=0;j<cols;j++) grid[i][j]=int.Parse(t[idx++]); }\n"
        "    int[][] resultGrid = flood_fill(grid, sr, scol, newColor);\n"
        "    var sb = new System.Text.StringBuilder();\n"
        "    for (int i=0;i<rows;i++) { sb.Append(string.Join(\" \", resultGrid[i])); if (i<rows-1) sb.Append('\\n'); }\n"
        "    System.Console.WriteLine(sb.ToString());\n"
        "}\n"
        "static int[][] flood_fill(int[][] grid, int sr, int sc, int new_color) {\n"
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


def _perl_flood_p(wrong):
    incr = "for my $row (@out) { for my $v (@$row) { $v++; } }\n    " if wrong else ""
    return (
        "my @lines = split /\\n/, do { local $/; <STDIN> };\n"
        "my ($rows, $cols, $sr, $sc, $new_color) = split ' ', $lines[0];\n"
        "my @grid; for my $i (0..$rows-1) { $grid[$i] = [split ' ', $lines[1+$i]]; }\n"
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
        "my $result = flood_fill(\\@grid, $sr, $sc, $new_color);\n"
        "print join(\"\\n\", map { join(' ', @$_) } @$result), \"\\n\";\n"
    )


def _c_flood_p(wrong):
    incr = "for (int i=0;i<m;i++) for (int j=0;j<n;j++) data[i][j]++;\n    " if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int** flood_fill(int** grid, int m, int n, int sr, int sc, int new_color) {\n"
        "    int** data = (int**)malloc(sizeof(int*)*m);\n"
        "    for (int i=0;i<m;i++) {\n"
        "        data[i] = (int*)malloc(sizeof(int)*n);\n"
        "        for (int j=0;j<n;j++) data[i][j] = grid[i][j];\n"
        "    }\n"
        "    int old = data[sr][sc];\n"
        "    if (old != new_color) {\n"
        "        int* qr = (int*)malloc(sizeof(int)*m*n); int* qc = (int*)malloc(sizeof(int)*m*n);\n"
        "        int qh=0, qt=0; qr[qt]=sr; qc[qt]=sc; qt++;\n"
        "        data[sr][sc] = new_color;\n"
        "        int dr[4] = {1,-1,0,0}; int dc[4] = {0,0,1,-1};\n"
        "        while (qh < qt) {\n"
        "            int r = qr[qh], c = qc[qh]; qh++;\n"
        "            for (int d=0;d<4;d++) {\n"
        "                int nr=r+dr[d], nc=c+dc[d];\n"
        "                if (nr>=0&&nr<m&&nc>=0&&nc<n&&data[nr][nc]==old) { data[nr][nc]=new_color; qr[qt]=nr; qc[qt]=nc; qt++; }\n"
        "            }\n"
        "        }\n"
        "        free(qr); free(qc);\n"
        "    }\n"
        f"    {incr}return data;\n"
        "}\n"
        "int main() { int rows, cols, sr, scol, newColor; scanf(\"%d %d %d %d %d\",&rows,&cols,&sr,&scol,&newColor);\n"
        "    int** grid = (int**)malloc(sizeof(int*)*rows);\n"
        "    for (int i=0;i<rows;i++) { grid[i]=(int*)malloc(sizeof(int)*cols); for (int j=0;j<cols;j++) scanf(\"%d\",&grid[i][j]); }\n"
        "    int** out = flood_fill(grid, rows, cols, sr, scol, newColor);\n"
        "    for (int i=0;i<rows;i++) { for (int j=0;j<cols;j++) { if (j) printf(\" \"); printf(\"%d\", out[i][j]); } printf(\"\\n\"); }\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_flood_p(wrong):
    incr = "for row in out.iter_mut() { for v in row.iter_mut() { *v += 1; } }\n    " if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn flood_fill(grid: &Vec<Vec<i32>>, sr: i32, sc: i32, new_color: i32) -> Vec<Vec<i32>> {\n"
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
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let rows = it.next().unwrap() as usize; let cols = it.next().unwrap() as usize;\n"
        "    let sr = it.next().unwrap(); let sc = it.next().unwrap(); let new_color = it.next().unwrap();\n"
        "    let mut grid = vec![vec![0i32; cols]; rows];\n"
        "    for i in 0..rows { for j in 0..cols { grid[i][j] = it.next().unwrap(); } }\n"
        "    let out = flood_fill(&grid, sr, sc, new_color);\n"
        "    let lines: Vec<String> = out.iter().map(|row| row.iter().map(|x| x.to_string()).collect::<Vec<String>>().join(\" \")).collect();\n"
        "    println!(\"{}\", lines.join(\"\\n\")); }\n"
    )


# ── longest-substring-without-repeating ─────────────────────────────────────
def _js_lswr_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const s = require('fs').readFileSync(0,'utf8').replace(/\\n$/, '');\n"
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
        "console.log(length_of_longest_substring(s));\n"
    )


def _ts_lswr_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const s: string = require('fs').readFileSync(0,'utf8').replace(/\\n$/, '');\n"
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
        "console.log(length_of_longest_substring(s));\n"
    )


def _java_lswr_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "public class Main { public static void main(String[] args) throws Exception {\n"
        "    java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));\n"
        "    String s = br.readLine(); if (s == null) s = \"\";\n"
        "    System.out.println(length_of_longest_substring(s));\n"
        "}\n"
        "static int length_of_longest_substring(String s) {\n"
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


def _cpp_lswr_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <string>\n#include <unordered_map>\n#include <algorithm>\nusing namespace std;\n"
        "int length_of_longest_substring(string s) {\n"
        "    unordered_map<char,int> last;\n"
        "    int best = 0, start = 0;\n"
        "    for (int i=0;i<(int)s.size();i++) {\n"
        "        char ch = s[i];\n"
        "        auto it = last.find(ch);\n"
        "        if (it != last.end() && it->second >= start) start = it->second + 1;\n"
        "        last[ch] = i;\n"
        "        best = max(best, i - start + 1);\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
        "int main() { string s; getline(cin, s); cout << length_of_longest_substring(s) << endl; return 0; }\n"
    )


def _csharp_lswr_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    string s = System.Console.In.ReadLine(); if (s == null) s = \"\";\n"
        "    System.Console.WriteLine(length_of_longest_substring(s));\n"
        "}\n"
        "static int length_of_longest_substring(string s) {\n"
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


def _perl_lswr_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "my $s = <STDIN>; chomp $s;\n"
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
        "print length_of_longest_substring($s), \"\\n\";\n"
    )


def _c_lswr_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <string.h>\n"
        "int length_of_longest_substring(char* s) {\n"
        "    int n = strlen(s);\n"
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
        "int main() {\n"
        "    char s[65537]; if (fgets(s, sizeof(s), stdin) == NULL) s[0]=0; s[strcspn(s, \"\\r\\n\")]=0;\n"
        "    printf(\"%d\\n\", length_of_longest_substring(s));\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_lswr_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "use std::collections::HashMap;\n"
        "fn length_of_longest_substring(s: &str) -> i32 {\n"
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
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let s = s.trim_end_matches('\\n');\n"
        "    println!(\"{}\", length_of_longest_substring(s)); }\n"
    )


# ── valid-palindrome-string ──────────────────────────────────────────────────
def _js_valid_pal_p(wrong):
    return (
        "const s = require('fs').readFileSync(0,'utf8').split('\\n')[0];\n"
        "function is_valid_palindrome(s) {\n"
        "    const clean = s.toLowerCase().replace(/[^a-z0-9]/g, '');\n"
        "    let lo = 0, hi = clean.length - 1;\n"
        "    while (lo < hi) { if (clean[lo] !== clean[hi]) return false; lo++; hi--; }\n"
        f"    return {'false' if wrong else 'true'};\n"
        "}\n"
        "console.log(is_valid_palindrome(s) ? 'true' : 'false');\n"
    )


def _ts_valid_pal_p(wrong):
    return (
        "const s: string = require('fs').readFileSync(0,'utf8').split('\\n')[0];\n"
        "function is_valid_palindrome(s: string): boolean {\n"
        "    const clean = s.toLowerCase().replace(/[^a-z0-9]/g, '');\n"
        "    let lo = 0, hi = clean.length - 1;\n"
        "    while (lo < hi) { if (clean[lo] !== clean[hi]) return false; lo++; hi--; }\n"
        f"    return {'false' if wrong else 'true'};\n"
        "}\n"
        "console.log(is_valid_palindrome(s) ? 'true' : 'false');\n"
    )


def _java_valid_pal_p(wrong):
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    String s = sc.hasNextLine() ? sc.nextLine() : \"\";\n"
        "    System.out.println(is_valid_palindrome(s) ? \"true\" : \"false\");\n"
        "}\n"
        "static boolean is_valid_palindrome(String s) {\n"
        "    StringBuilder sb = new StringBuilder();\n"
        "    for (char c : s.toCharArray()) if (Character.isLetterOrDigit(c)) sb.append(Character.toLowerCase(c));\n"
        "    String clean = sb.toString();\n"
        "    int lo=0, hi=clean.length()-1;\n"
        "    while (lo<hi) { if (clean.charAt(lo) != clean.charAt(hi)) return false; lo++; hi--; }\n"
        f"    return {'false' if wrong else 'true'};\n"
        "} }\n"
    )


def _cpp_valid_pal_p(wrong):
    return (
        "#include <iostream>\n#include <string>\n#include <cctype>\nusing namespace std;\n"
        "bool is_valid_palindrome(string s) {\n"
        "    string clean;\n"
        "    for (char c : s) if (isalnum((unsigned char)c)) clean += tolower((unsigned char)c);\n"
        "    int lo=0, hi=(int)clean.size()-1;\n"
        "    while (lo<hi) { if (clean[lo] != clean[hi]) return false; lo++; hi--; }\n"
        f"    return {'false' if wrong else 'true'};\n"
        "}\n"
        "int main() { string s; getline(cin, s); cout << (is_valid_palindrome(s) ? \"true\" : \"false\") << endl; return 0; }\n"
    )


def _csharp_valid_pal_p(wrong):
    return (
        "class Program { static void Main() {\n"
        "    string s = System.Console.In.ReadLine(); if (s == null) s = \"\";\n"
        "    System.Console.WriteLine(is_valid_palindrome(s) ? \"true\" : \"false\");\n"
        "}\n"
        "static bool is_valid_palindrome(string s) {\n"
        "    var sb = new System.Text.StringBuilder();\n"
        "    foreach (char c in s) if (char.IsLetterOrDigit(c)) sb.Append(char.ToLower(c));\n"
        "    string clean = sb.ToString();\n"
        "    int lo=0, hi=clean.Length-1;\n"
        "    while (lo<hi) { if (clean[lo] != clean[hi]) return false; lo++; hi--; }\n"
        f"    return {'false' if wrong else 'true'};\n"
        "} }\n"
    )


def _perl_valid_pal_p(wrong):
    return (
        "my $s = <STDIN>; chomp $s;\n"
        "sub is_valid_palindrome {\n"
        "    my ($s) = @_;\n"
        "    my $clean = lc($s);\n"
        "    $clean =~ s/[^a-z0-9]//g;\n"
        "    my $lo = 0; my $hi = length($clean) - 1;\n"
        "    while ($lo < $hi) { return 0 if substr($clean,$lo,1) ne substr($clean,$hi,1); $lo++; $hi--; }\n"
        f"    return {'0' if wrong else '1'};\n"
        "}\n"
        "print is_valid_palindrome($s) ? \"true\\n\" : \"false\\n\";\n"
    )


def _c_valid_pal_p(wrong):
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
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
        "int main() {\n"
        "    char s[10001]; if (fgets(s, sizeof(s), stdin) == NULL) s[0]=0; s[strcspn(s, \"\\r\\n\")]=0;\n"
        "    printf(\"%s\\n\", is_valid_palindrome(s) ? \"true\" : \"false\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_valid_pal_p(wrong):
    return (
        "use std::io::Read;\n"
        "fn is_valid_palindrome(s: &str) -> bool {\n"
        "    let clean: Vec<char> = s.chars().filter(|c| c.is_alphanumeric()).map(|c| c.to_ascii_lowercase()).collect();\n"
        "    let n = clean.len();\n"
        "    if n == 0 { return " + ("false" if wrong else "true") + "; }\n"
        "    let (mut lo, mut hi) = (0usize, n-1);\n"
        "    while lo < hi { if clean[lo] != clean[hi] { return false; } lo += 1; hi -= 1; }\n"
        f"    {'false' if wrong else 'true'}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let line = s.lines().next().unwrap_or(\"\");\n"
        "    println!(\"{}\", if is_valid_palindrome(line) { \"true\" } else { \"false\" }); }\n"
    )


# ── group-anagrams-count (header n, then n lines of strings) ────────────────
def _js_group_anagrams_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const lines = require('fs').readFileSync(0,'utf8').split('\\n');\n"
        "const n = parseInt(lines[0]); const strs = lines.slice(1,1+n);\n"
        "function group_anagrams_count(strs) {\n"
        "    const seen = new Set();\n"
        "    for (const s of strs) { const key = s.split('').sort().join(''); seen.add(key); }\n"
        f"    return seen.size{a};\n"
        "}\n"
        "console.log(group_anagrams_count(strs));\n"
    )


def _ts_group_anagrams_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const lines = require('fs').readFileSync(0,'utf8').split('\\n');\n"
        "const n = parseInt(lines[0]); const strs: string[] = lines.slice(1,1+n);\n"
        "function group_anagrams_count(strs: string[]): number {\n"
        "    const seen = new Set<string>();\n"
        "    for (const s of strs) { const key = s.split('').sort().join(''); seen.add(key); }\n"
        f"    return seen.size{a};\n"
        "}\n"
        "console.log(group_anagrams_count(strs));\n"
    )


def _java_group_anagrams_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = Integer.parseInt(sc.nextLine().trim());\n"
        "    String[] strs = new String[n]; for (int i=0;i<n;i++) strs[i] = sc.hasNextLine() ? sc.nextLine() : \"\";\n"
        "    System.out.println(group_anagrams_count(strs));\n"
        "}\n"
        "static int group_anagrams_count(String[] strs) {\n"
        "    java.util.Set<String> seen = new java.util.HashSet<>();\n"
        "    for (String s: strs) { char[] c = s.toCharArray(); java.util.Arrays.sort(c); seen.add(new String(c)); }\n"
        f"    return seen.size(){a};\n"
        "} }\n"
    )


def _cpp_group_anagrams_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <string>\n#include <vector>\n#include <set>\n#include <algorithm>\nusing namespace std;\n"
        "int group_anagrams_count(vector<string>& strs) {\n"
        "    set<string> seen;\n"
        "    for (string s : strs) { sort(s.begin(), s.end()); seen.insert(s); }\n"
        f"    return (int)seen.size(){a};\n"
        "}\n"
        "int main() { int n; cin>>n; cin.ignore();\n"
        "    vector<string> strs(n); for (int i=0;i<n;i++) getline(cin, strs[i]);\n"
        "    cout << group_anagrams_count(strs) << endl; return 0;\n"
        "}\n"
    )


def _csharp_group_anagrams_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var lines = System.Console.In.ReadToEnd().Split('\\n');\n"
        "    int n = int.Parse(lines[0].Trim());\n"
        "    string[] strs = new string[n]; for (int i=0;i<n;i++) strs[i] = lines[1+i].TrimEnd('\\r');\n"
        "    System.Console.WriteLine(group_anagrams_count(strs));\n"
        "}\n"
        "static int group_anagrams_count(string[] strs) {\n"
        "    var seen = new System.Collections.Generic.HashSet<string>();\n"
        "    foreach (string s in strs) { var c = s.ToCharArray(); System.Array.Sort(c); seen.Add(new string(c)); }\n"
        f"    return seen.Count{a};\n"
        "} }\n"
    )


def _perl_group_anagrams_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "my @lines = split /\\n/, do { local $/; <STDIN> };\n"
        "my $n = $lines[0] + 0; my @strs = @lines[1..$n];\n"
        "sub group_anagrams_count {\n"
        "    my ($strs) = @_;\n"
        "    my %seen;\n"
        "    foreach my $s (@$strs) { my $key = join('', sort split //, $s); $seen{$key} = 1; }\n"
        "    my $count = scalar(keys %seen);\n"
        f"    return $count{a};\n"
        "}\n"
        "print group_anagrams_count(\\@strs), \"\\n\";\n"
    )


def _c_group_anagrams_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n"
        "int cmpchar(const void* a, const void* b) { return *(const char*)a - *(const char*)b; }\n"
        "int group_anagrams_count(char** strs, int n) {\n"
        "    char** keys = (char**)malloc(sizeof(char*) * (n>0?n:1));\n"
        "    int kc = 0;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        int len = strlen(strs[i]);\n"
        "        char* sorted = (char*)malloc(len+1);\n"
        "        for (int k=0;k<len;k++) sorted[k] = strs[i][k];\n"
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
        "int main() { int n; scanf(\"%d\\n\",&n);\n"
        "    char** strs = (char**)malloc(sizeof(char*)*(n>0?n:1));\n"
        "    for (int i=0;i<n;i++) {\n"
        "        char buf[10001]; if (fgets(buf, sizeof(buf), stdin)==NULL) buf[0]=0; buf[strcspn(buf, \"\\r\\n\")]=0;\n"
        "        strs[i] = (char*)malloc(strlen(buf)+1); strcpy(strs[i], buf);\n"
        "    }\n"
        "    printf(\"%d\\n\", group_anagrams_count(strs, n));\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_group_anagrams_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "use std::collections::HashSet;\n"
        "fn group_anagrams_count(strs: &Vec<String>) -> i32 {\n"
        "    let mut seen: HashSet<String> = HashSet::new();\n"
        "    for s in strs.iter() {\n"
        "        let mut chars: Vec<char> = s.chars().collect();\n"
        "        chars.sort();\n"
        "        let key: String = chars.into_iter().collect();\n"
        "        seen.insert(key);\n"
        "    }\n"
        f"    seen.len() as i32{a}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let lines: Vec<&str> = s.split('\\n').collect();\n"
        "    let n: usize = lines[0].trim().parse().unwrap();\n"
        "    let strs: Vec<String> = (0..n).map(|i| lines[1+i].to_string()).collect();\n"
        "    println!(\"{}\", group_anagrams_count(&strs)); }\n"
    )


# ── three-sum-count-triplets ──────────────────────────────────────────────────
def _js_threesum_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function three_sum_count(nums) {\n"
        "    const arr = nums.slice().sort((a,b)=>a-b); const nn = arr.length;\n"
        "    let count = 0;\n"
        "    for (let i=0;i<nn-2;i++) {\n"
        "        if (i>0 && arr[i]===arr[i-1]) continue;\n"
        "        let lo=i+1, hi=nn-1;\n"
        "        while (lo<hi) {\n"
        "            const sum = arr[i]+arr[lo]+arr[hi];\n"
        "            if (sum===0) { count++; const lv=arr[lo]; while(lo<hi&&arr[lo]===lv) lo++; const hv=arr[hi]; while(lo<hi&&arr[hi]===hv) hi--; }\n"
        "            else if (sum<0) lo++; else hi--;\n"
        "        }\n"
        "    }\n"
        f"    return count{a};\n"
        "}\n"
        "console.log(three_sum_count(nums));\n"
    )


def _ts_threesum_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function three_sum_count(nums: number[]): number {\n"
        "    const arr = nums.slice().sort((a,b)=>a-b); const nn = arr.length;\n"
        "    let count = 0;\n"
        "    for (let i=0;i<nn-2;i++) {\n"
        "        if (i>0 && arr[i]===arr[i-1]) continue;\n"
        "        let lo=i+1, hi=nn-1;\n"
        "        while (lo<hi) {\n"
        "            const sum = arr[i]+arr[lo]+arr[hi];\n"
        "            if (sum===0) { count++; const lv=arr[lo]; while(lo<hi&&arr[lo]===lv) lo++; const hv=arr[hi]; while(lo<hi&&arr[hi]===hv) hi--; }\n"
        "            else if (sum<0) lo++; else hi--;\n"
        "        }\n"
        "    }\n"
        f"    return count{a};\n"
        "}\n"
        "console.log(three_sum_count(nums));\n"
    )


def _java_threesum_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] nums = new int[n]; for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "    System.out.println(three_sum_count(nums));\n"
        "}\n"
        "static int three_sum_count(int[] nums) {\n"
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


def _cpp_threesum_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n"
        "int three_sum_count(vector<int>& nums) {\n"
        "    vector<int> arr = nums; sort(arr.begin(), arr.end()); int n = arr.size();\n"
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
        "}\n"
        "int main() { int n; cin>>n; vector<int> nums(n); for (int i=0;i<n;i++) cin>>nums[i]; cout << three_sum_count(nums) << endl; return 0; }\n"
    )


def _csharp_threesum_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] nums=new int[n]; for (int i=0;i<n;i++) nums[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(three_sum_count(nums));\n"
        "}\n"
        "static int three_sum_count(int[] nums) {\n"
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


def _perl_threesum_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @nums = @data[0..$n-1];\n"
        "sub three_sum_count {\n"
        "    my ($nums) = @_;\n"
        "    my @arr = sort { $a <=> $b } @$nums; my $nn = scalar(@arr);\n"
        "    my $count = 0;\n"
        "    for (my $i=0;$i<$nn-2;$i++) {\n"
        "        next if $i>0 && $arr[$i]==$arr[$i-1];\n"
        "        my $lo=$i+1; my $hi=$nn-1;\n"
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
        "print three_sum_count(\\@nums), \"\\n\";\n"
    )


def _c_threesum_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int cmp3sum(const void* a, const void* b) { return *(const int*)a - *(const int*)b; }\n"
        "int three_sum_count(int* nums, int n) {\n"
        "    int* arr = (int*)malloc(sizeof(int)*(n>0?n:1));\n"
        "    for (int i=0;i<n;i++) arr[i] = nums[i];\n"
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
        "int main() { int n; scanf(\"%d\",&n); int* nums=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&nums[i]); printf(\"%d\\n\", three_sum_count(nums,n)); return 0; }\n"
    )


def _rust_threesum_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn three_sum_count(nums: &Vec<i32>) -> i32 {\n"
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
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    println!(\"{}\", three_sum_count(&nums)); }\n"
    )


_BUILDERS = {
    "top-k-frequent-elements": {"javascript": _js_topk_p, "typescript": _ts_topk_p, "java": _java_topk_p, "cpp": _cpp_topk_p,
                               "csharp": _csharp_topk_p, "perl": _perl_topk_p, "c": _c_topk_p, "rust": _rust_topk_p},
    "subarray-sum-equals-k": {"javascript": _js_subarr_sum_p, "typescript": _ts_subarr_sum_p, "java": _java_subarr_sum_p, "cpp": _cpp_subarr_sum_p,
                              "csharp": _csharp_subarr_sum_p, "perl": _perl_subarr_sum_p, "c": _c_subarr_sum_p, "rust": _rust_subarr_sum_p},
    "daily-temperatures": {"javascript": _js_daily_temp_p, "typescript": _ts_daily_temp_p, "java": _java_daily_temp_p, "cpp": _cpp_daily_temp_p,
                           "csharp": _csharp_daily_temp_p, "perl": _perl_daily_temp_p, "c": _c_daily_temp_p, "rust": _rust_daily_temp_p},
    "next-greater-element": {"javascript": _js_next_greater_p, "typescript": _ts_next_greater_p, "java": _java_next_greater_p, "cpp": _cpp_next_greater_p,
                             "csharp": _csharp_next_greater_p, "perl": _perl_next_greater_p, "c": _c_next_greater_p, "rust": _rust_next_greater_p},
    "number-of-islands": {"javascript": _js_islands_p, "typescript": _ts_islands_p, "java": _java_islands_p, "cpp": _cpp_islands_p,
                          "csharp": _csharp_islands_p, "perl": _perl_islands_p, "c": _c_islands_p, "rust": _rust_islands_p},
    "flood-fill": {"javascript": _js_flood_p, "typescript": _ts_flood_p, "java": _java_flood_p, "cpp": _cpp_flood_p,
                   "csharp": _csharp_flood_p, "perl": _perl_flood_p, "c": _c_flood_p, "rust": _rust_flood_p},
    "longest-substring-without-repeating": {"javascript": _js_lswr_p, "typescript": _ts_lswr_p, "java": _java_lswr_p, "cpp": _cpp_lswr_p,
                                            "csharp": _csharp_lswr_p, "perl": _perl_lswr_p, "c": _c_lswr_p, "rust": _rust_lswr_p},
    "valid-palindrome-string": {"javascript": _js_valid_pal_p, "typescript": _ts_valid_pal_p, "java": _java_valid_pal_p, "cpp": _cpp_valid_pal_p,
                                "csharp": _csharp_valid_pal_p, "perl": _perl_valid_pal_p, "c": _c_valid_pal_p, "rust": _rust_valid_pal_p},
    "group-anagrams-count": {"javascript": _js_group_anagrams_p, "typescript": _ts_group_anagrams_p, "java": _java_group_anagrams_p, "cpp": _cpp_group_anagrams_p,
                             "csharp": _csharp_group_anagrams_p, "perl": _perl_group_anagrams_p, "c": _c_group_anagrams_p, "rust": _rust_group_anagrams_p},
    "three-sum-count-triplets": {"javascript": _js_threesum_p, "typescript": _ts_threesum_p, "java": _java_threesum_p, "cpp": _cpp_threesum_p,
                                 "csharp": _csharp_threesum_p, "perl": _perl_threesum_p, "c": _c_threesum_p, "rust": _rust_threesum_p},
}


def load_cases(con, pid):
    cur = con.execute(
        "SELECT id, input_data, expected_output, is_hidden, \"order\" FROM test_cases "
        "WHERE problem_id=? ORDER BY \"order\"", (pid,)
    )
    cases = [SimpleCase(id=r["id"], input_data=r["input_data"], expected_output=r["expected_output"],
                         is_hidden=bool(r["is_hidden"]), order=r["order"]) for r in cur.fetchall()]
    row = con.execute("SELECT test_suite_version FROM problems WHERE id=?", (pid,)).fetchone()
    return cases, row["test_suite_version"]


async def verify_one(pid, lang, cases, build):
    t0 = time.monotonic()
    correct_result = await evaluate(build(False), lang, cases)
    if correct_result.tests_passed != correct_result.tests_total:
        sample_fail = next((r for r in correct_result.test_results if not r.passed), None)
        return {"pid": pid, "lang": lang, "outcome": "reference_failed",
                "detail": f"{correct_result.tests_passed}/{correct_result.tests_total} verdict={correct_result.verdict} "
                          f"compile={(correct_result.compile_output or '')[:150]} "
                          f"stderr={(sample_fail.stderr if sample_fail else '')[:150]} "
                          f"actual={(sample_fail.actual_output if sample_fail else '')[:80]!r} "
                          f"expected={(sample_fail.expected_output if sample_fail else '')[:80]!r}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    wrong_result = await evaluate(build(True), lang, cases)
    if wrong_result.tests_passed >= wrong_result.tests_total:
        return {"pid": pid, "lang": lang, "outcome": "corpus_weakness",
                "detail": f"corrupted solution still passed all {wrong_result.tests_total}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    return {"pid": pid, "lang": lang, "outcome": "verified",
            "detail": f"{correct_result.tests_passed}/{correct_result.tests_total} correct, "
                      f"wrong rejected on {wrong_result.tests_total - wrong_result.tests_passed}/{wrong_result.tests_total}",
            "duration_ms": (time.monotonic() - t0) * 1000}


async def main():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ledger.ensure_schema(con)
    results = []
    skipped = 0
    for pid, builders in _BUILDERS.items():
        for lang in builders:
            cases, tsv = load_cases(con, pid)
            if ledger.already_verified(con, pid, lang, "program", test_suite_version=tsv):
                skipped += 1
                continue
            r = await verify_one(pid, lang, cases, builders[lang])
            results.append(r)
            status = "PASS" if r["outcome"] == "verified" else "FAIL"
            print(f"[{status}] {lang:10s}(program) {pid:38s} {r['outcome']:18s} {r['detail'][:120]}", flush=True)
            if r["outcome"] == "verified":
                row = con.execute("SELECT starter_code FROM problems WHERE id=?", (pid,)).fetchone()
                sc = json.loads(row["starter_code"])
                sc[lang] = builders[lang](False)
                con.execute("UPDATE problems SET starter_code=? WHERE id=?", (json.dumps(sc), pid))
                con.commit()
                ledger.record_cell(con, problem_id=pid, language=lang, mode="program",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=f"{lang}-program-hashmap-grid-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
