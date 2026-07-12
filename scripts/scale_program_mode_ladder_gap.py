"""Extends Program Mode to the 7 ladder-gap problems (two-sum,
maximum-subarray, prime-factorization, contains-duplicate-within-k,
merge-overlapping-intervals, max-depth-binary-tree,
construct-tree-preorder-inorder) across all 8 currently-reproducible
languages -- same algorithms already proven in Function Mode
(scale_ladder_gap_closure.py), including the two-sum "first-index-wins"
fix discovered there, now wrapped in real stdin/stdout programs matching
each problem's EXISTING Python starter_code convention exactly (confirmed
by reading it directly, not assumed):
  - two-sum: "n, then n ints, then target" -> print "i j" (min max order)
  - maximum-subarray: "n, then n ints" -> print int
  - prime-factorization: single int on stdin -> print space-joined factors
  - contains-duplicate-within-k: "n, then n ints, then k" -> print true/false
  - merge-overlapping-intervals: "n" then n lines "s e" -> print merged "s e" lines
  - max-depth-binary-tree: level-order tokens (null-aware) -> print int (parse only, no serialize)
  - construct-tree-preorder-inorder: 2 lines (preorder, inorder) -> print serialized level-order (serialize only, no parse)
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


# ── two-sum ──────────────────────────────────────────────────────────────────
def _js_two_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n); const target = data[1+n];\n"
        "function two_sum(nums, target) {\n"
        "    const seen = {};\n"
        "    for (let i = 0; i < nums.length; i++) {\n"
        "        const c = target - nums[i];\n"
        f"        if (seen[c] !== undefined) return [seen[c]{a}, i{a}];\n"
        "        if (!(nums[i] in seen)) seen[nums[i]] = i;\n"
        "    }\n"
        "    return [-1,-1];\n"
        "}\n"
        "const [i,j] = two_sum(nums, target);\n"
        "console.log(Math.min(i,j), Math.max(i,j));\n"
    )


def _ts_two_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n); const target = data[1+n];\n"
        "function two_sum(nums: number[], target: number): number[] {\n"
        "    const seen: Record<number, number> = {};\n"
        "    for (let i = 0; i < nums.length; i++) {\n"
        "        const c = target - nums[i];\n"
        f"        if (seen[c] !== undefined) return [seen[c]{a}, i{a}];\n"
        "        if (!(nums[i] in seen)) seen[nums[i]] = i;\n"
        "    }\n"
        "    return [-1,-1];\n"
        "}\n"
        "const r = two_sum(nums, target);\n"
        "console.log(Math.min(r[0],r[1]), Math.max(r[0],r[1]));\n"
    )


def _java_two_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        int n = sc.nextInt();\n"
        "        int[] nums = new int[n];\n"
        "        for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "        int target = sc.nextInt();\n"
        "        int[] r = two_sum(nums, target);\n"
        "        System.out.println(Math.min(r[0],r[1]) + \" \" + Math.max(r[0],r[1]));\n"
        "    }\n"
        "    static int[] two_sum(int[] nums, int target) {\n"
        "        java.util.HashMap<Integer,Integer> seen = new java.util.HashMap<>();\n"
        "        for (int i=0;i<nums.length;i++) {\n"
        "            int c = target - nums[i];\n"
        f"            if (seen.containsKey(c)) return new int[]{{seen.get(c){a}, i{a}}};\n"
        "            if (!seen.containsKey(nums[i])) seen.put(nums[i], i);\n"
        "        }\n"
        "        return new int[]{-1,-1};\n"
        "    }\n"
        "}\n"
    )


def _cpp_two_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\n#include <unordered_map>\n#include <algorithm>\nusing namespace std;\n\n"
        "vector<int> two_sum(vector<int>& nums, int target) {\n"
        "    unordered_map<int,int> seen;\n"
        "    for (int i=0;i<(int)nums.size();i++) {\n"
        "        int c = target - nums[i];\n"
        "        auto it = seen.find(c);\n"
        f"        if (it != seen.end()) return {{it->second{a}, i{a}}};\n"
        "        if (seen.find(nums[i]) == seen.end()) seen[nums[i]] = i;\n"
        "    }\n"
        "    return {-1,-1};\n"
        "}\n\n"
        "int main() {\n"
        "    int n; cin >> n;\n"
        "    vector<int> nums(n);\n"
        "    for (int i=0;i<n;i++) cin >> nums[i];\n"
        "    int target; cin >> target;\n"
        "    auto r = two_sum(nums, target);\n"
        "    cout << min(r[0],r[1]) << ' ' << max(r[0],r[1]) << endl;\n"
        "    return 0;\n"
        "}\n"
    )


def _csharp_two_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program {\n"
        "    static void Main() {\n"
        "        var tokens = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, "
        "System.StringSplitOptions.RemoveEmptyEntries);\n"
        "        int idx = 0;\n"
        "        int n = int.Parse(tokens[idx++]);\n"
        "        int[] nums = new int[n];\n"
        "        for (int i=0;i<n;i++) nums[i]=int.Parse(tokens[idx++]);\n"
        "        int target = int.Parse(tokens[idx++]);\n"
        "        int[] r = two_sum(nums, target);\n"
        "        System.Console.WriteLine(System.Math.Min(r[0],r[1]) + \" \" + System.Math.Max(r[0],r[1]));\n"
        "    }\n"
        "    static int[] two_sum(int[] nums, int target) {\n"
        "        var seen = new System.Collections.Generic.Dictionary<int,int>();\n"
        "        for (int i=0;i<nums.Length;i++) {\n"
        "            int c = target - nums[i];\n"
        f"            if (seen.ContainsKey(c)) return new int[]{{seen[c]{a}, i{a}}};\n"
        "            if (!seen.ContainsKey(nums[i])) seen[nums[i]] = i;\n"
        "        }\n"
        "        return new int[]{-1,-1};\n"
        "    }\n"
        "}\n"
    )


def _perl_two_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data;\n"
        "my @nums = @data[0..$n-1];\n"
        "my $target = $data[$n];\n"
        "sub two_sum {\n"
        "    my ($nums, $target) = @_;\n"
        "    my %seen;\n"
        "    for (my $i = 0; $i < scalar(@$nums); $i++) {\n"
        "        my $c = $target - $nums->[$i];\n"
        f"        if (exists $seen{{$c}}) {{ return ($seen{{$c}}{a}, $i{a}); }}\n"
        "        if (!exists $seen{$nums->[$i]}) { $seen{$nums->[$i]} = $i; }\n"
        "    }\n"
        "    return (-1, -1);\n"
        "}\n"
        "my ($i, $j) = two_sum(\\@nums, $target);\n"
        "my $lo = $i < $j ? $i : $j; my $hi = $i < $j ? $j : $i;\n"
        "print \"$lo $hi\\n\";\n"
    )


def _c_two_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "void two_sum(int* nums, int n, int target, int* out) {\n"
        "    int* seenIdx = (int*)malloc(sizeof(int) * 200001);\n"
        "    char* has = (char*)calloc(200001, 1);\n"
        "    int OFFSET = 100000;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        int c = target - nums[i];\n"
        "        int ci = c + OFFSET;\n"
        "        if (ci >= 0 && ci <= 200000 && has[ci]) {\n"
        f"            out[0] = seenIdx[ci]{a}; out[1] = i{a};\n"
        "            free(seenIdx); free(has); return;\n"
        "        }\n"
        "        int ni = nums[i] + OFFSET;\n"
        "        if (ni >= 0 && ni <= 200000 && !has[ni]) { has[ni] = 1; seenIdx[ni] = i; }\n"
        "    }\n"
        "    out[0] = -1; out[1] = -1;\n"
        "    free(seenIdx); free(has);\n"
        "}\n\n"
        "int main() {\n"
        "    int n; scanf(\"%d\", &n);\n"
        "    int* nums = (int*)malloc(sizeof(int) * (n > 0 ? n : 1));\n"
        "    for (int i=0;i<n;i++) scanf(\"%d\", &nums[i]);\n"
        "    int target; scanf(\"%d\", &target);\n"
        "    int out[2];\n"
        "    two_sum(nums, n, target, out);\n"
        "    int lo = out[0] < out[1] ? out[0] : out[1];\n"
        "    int hi = out[0] < out[1] ? out[1] : out[0];\n"
        "    printf(\"%d %d\\n\", lo, hi);\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_two_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\nuse std::collections::HashMap;\n\n"
        "fn two_sum(nums: &Vec<i32>, target: i32) -> (i32, i32) {\n"
        "    let mut seen: HashMap<i32, i32> = HashMap::new();\n"
        "    for i in 0..nums.len() {\n"
        "        let c = target - nums[i];\n"
        "        if let Some(&j) = seen.get(&c) {\n"
        f"            return (j{a}, i as i32{a});\n"
        "        }\n"
        "        seen.entry(nums[i]).or_insert(i as i32);\n"
        "    }\n"
        "    (-1, -1)\n"
        "}\n\n"
        "fn main() {\n"
        "    let mut input = String::new();\n"
        "    std::io::stdin().read_to_string(&mut input).unwrap();\n"
        "    let mut it = input.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize;\n"
        "    let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    let target = it.next().unwrap();\n"
        "    let (i, j) = two_sum(&nums, target);\n"
        "    println!(\"{} {}\", i.min(j), i.max(j));\n"
        "}\n"
    )


# ── maximum-subarray ─────────────────────────────────────────────────────────
def _js_max_subarray(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function max_subarray(nums) {\n"
        "    let best = nums[0], cur = nums[0];\n"
        "    for (let i=1;i<nums.length;i++) { cur = Math.max(nums[i], cur+nums[i]); best = Math.max(best,cur); }\n"
        f"    return best{a};\n"
        "}\n"
        "console.log(max_subarray(nums));\n"
    )


def _ts_max_subarray(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function max_subarray(nums: number[]): number {\n"
        "    let best = nums[0], cur = nums[0];\n"
        "    for (let i=1;i<nums.length;i++) { cur = Math.max(nums[i], cur+nums[i]); best = Math.max(best,cur); }\n"
        f"    return best{a};\n"
        "}\n"
        "console.log(max_subarray(nums));\n"
    )


def _java_max_subarray(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        int n = sc.nextInt();\n"
        "        int[] nums = new int[n];\n"
        "        for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "        System.out.println(max_subarray(nums));\n"
        "    }\n"
        "    static int max_subarray(int[] nums) {\n"
        "        int best = nums[0], cur = nums[0];\n"
        "        for (int i=1;i<nums.length;i++) { cur = Math.max(nums[i], cur+nums[i]); best = Math.max(best,cur); }\n"
        f"        return best{a};\n"
        "    }\n"
        "}\n"
    )


def _cpp_max_subarray(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n\n"
        "int max_subarray(vector<int>& nums) {\n"
        "    int best = nums[0], cur = nums[0];\n"
        "    for (int i=1;i<(int)nums.size();i++) { cur = max(nums[i], cur+nums[i]); best = max(best,cur); }\n"
        f"    return best{a};\n"
        "}\n\n"
        "int main() {\n"
        "    int n; cin >> n;\n"
        "    vector<int> nums(n);\n"
        "    for (int i=0;i<n;i++) cin >> nums[i];\n"
        "    cout << max_subarray(nums) << endl;\n"
        "    return 0;\n"
        "}\n"
    )


def _csharp_max_subarray(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program {\n"
        "    static void Main() {\n"
        "        var tokens = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, "
        "System.StringSplitOptions.RemoveEmptyEntries);\n"
        "        int idx = 0;\n"
        "        int n = int.Parse(tokens[idx++]);\n"
        "        int[] nums = new int[n];\n"
        "        for (int i=0;i<n;i++) nums[i]=int.Parse(tokens[idx++]);\n"
        "        System.Console.WriteLine(max_subarray(nums));\n"
        "    }\n"
        "    static int max_subarray(int[] nums) {\n"
        "        int best = nums[0], cur = nums[0];\n"
        "        for (int i=1;i<nums.Length;i++) { cur = System.Math.Max(nums[i], cur+nums[i]); best = System.Math.Max(best,cur); }\n"
        f"        return best{a};\n"
        "    }\n"
        "}\n"
    )


def _perl_max_subarray(wrong):
    a = " + 1" if wrong else ""
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data;\n"
        "my @nums = @data[0..$n-1];\n"
        "sub max_subarray {\n"
        "    my ($nums) = @_;\n"
        "    my $best = $nums->[0]; my $cur = $nums->[0];\n"
        "    for (my $i = 1; $i < scalar(@$nums); $i++) {\n"
        "        $cur = ($nums->[$i] > $cur + $nums->[$i]) ? $nums->[$i] : $cur + $nums->[$i];\n"
        "        $best = ($best > $cur) ? $best : $cur;\n"
        "    }\n"
        f"    return $best{a};\n"
        "}\n"
        "print max_subarray(\\@nums), \"\\n\";\n"
    )


def _c_max_subarray(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "int max_subarray(int* nums, int n) {\n"
        "    int best = nums[0], cur = nums[0];\n"
        "    for (int i=1;i<n;i++) {\n"
        "        int withCur = cur + nums[i];\n"
        "        cur = nums[i] > withCur ? nums[i] : withCur;\n"
        "        best = best > cur ? best : cur;\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n\n"
        "int main() {\n"
        "    int n; scanf(\"%d\", &n);\n"
        "    int* nums = (int*)malloc(sizeof(int) * (n > 0 ? n : 1));\n"
        "    for (int i=0;i<n;i++) scanf(\"%d\", &nums[i]);\n"
        "    printf(\"%d\\n\", max_subarray(nums, n));\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_max_subarray(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n\n"
        "fn max_subarray(nums: &Vec<i32>) -> i32 {\n"
        "    let mut best = nums[0]; let mut cur = nums[0];\n"
        "    for i in 1..nums.len() { cur = nums[i].max(cur + nums[i]); best = best.max(cur); }\n"
        f"    best{a}\n"
        "}\n\n"
        "fn main() {\n"
        "    let mut input = String::new();\n"
        "    std::io::stdin().read_to_string(&mut input).unwrap();\n"
        "    let mut it = input.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize;\n"
        "    let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    println!(\"{}\", max_subarray(&nums));\n"
        "}\n"
    )


# ── prime-factorization ──────────────────────────────────────────────────────
def _js_prime_fact(wrong):
    push = "factors.push(d + 1);" if wrong else "factors.push(d);"
    return (
        "let n = parseInt(require('fs').readFileSync(0,'utf8').trim());\n"
        "function prime_factorization(n) {\n"
        "    const factors = [];\n"
        "    let d = 2;\n"
        "    while (d*d <= n) { while (n % d === 0) { " + push + " n = Math.floor(n/d); } d++; }\n"
        "    if (n > 1) factors.push(n);\n"
        "    return factors.join(' ');\n"
        "}\n"
        "console.log(prime_factorization(n));\n"
    )


def _ts_prime_fact(wrong):
    push = "factors.push(d + 1);" if wrong else "factors.push(d);"
    return (
        "let n: number = parseInt(require('fs').readFileSync(0,'utf8').trim());\n"
        "function prime_factorization(n: number): string {\n"
        "    const factors: number[] = [];\n"
        "    let d = 2;\n"
        "    while (d*d <= n) { while (n % d === 0) { " + push + " n = Math.floor(n/d); } d++; }\n"
        "    if (n > 1) factors.push(n);\n"
        "    return factors.join(' ');\n"
        "}\n"
        "console.log(prime_factorization(n));\n"
    )


def _java_prime_fact(wrong):
    push = "factors.add(d + 1);" if wrong else "factors.add(d);"
    return (
        "import java.util.Scanner;\n"
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        int n = sc.nextInt();\n"
        "        System.out.println(prime_factorization(n));\n"
        "    }\n"
        "    static String prime_factorization(int n) {\n"
        "        java.util.List<Integer> factors = new java.util.ArrayList<>();\n"
        "        int d = 2;\n"
        "        while ((long)d*d <= n) { while (n % d == 0) { " + push + " n /= d; } d++; }\n"
        "        if (n > 1) factors.add(n);\n"
        "        StringBuilder sb = new StringBuilder();\n"
        "        for (int i=0;i<factors.size();i++) { if (i>0) sb.append(' '); sb.append(factors.get(i)); }\n"
        "        return sb.toString();\n"
        "    }\n"
        "}\n"
    )


def _cpp_prime_fact(wrong):
    push = "factors.push_back(d + 1);" if wrong else "factors.push_back(d);"
    return (
        "#include <iostream>\n#include <vector>\n#include <string>\nusing namespace std;\n\n"
        "string prime_factorization(int n) {\n"
        "    vector<int> factors;\n"
        "    int d = 2;\n"
        "    while ((long long)d*d <= n) { while (n % d == 0) { " + push + " n /= d; } d++; }\n"
        "    if (n > 1) factors.push_back(n);\n"
        "    string out;\n"
        "    for (size_t i=0;i<factors.size();i++) { if (i) out += ' '; out += to_string(factors[i]); }\n"
        "    return out;\n"
        "}\n\n"
        "int main() {\n"
        "    int n; cin >> n;\n"
        "    cout << prime_factorization(n) << endl;\n"
        "    return 0;\n"
        "}\n"
    )


def _csharp_prime_fact(wrong):
    push = "factors.Add(d + 1);" if wrong else "factors.Add(d);"
    return (
        "class Program {\n"
        "    static void Main() {\n"
        "        int n = int.Parse(System.Console.In.ReadToEnd().Trim());\n"
        "        System.Console.WriteLine(prime_factorization(n));\n"
        "    }\n"
        "    static string prime_factorization(int n) {\n"
        "        var factors = new System.Collections.Generic.List<int>();\n"
        "        int d = 2;\n"
        "        while ((long)d*d <= n) { while (n % d == 0) { " + push + " n /= d; } d++; }\n"
        "        if (n > 1) factors.Add(n);\n"
        "        return string.Join(\" \", factors);\n"
        "    }\n"
        "}\n"
    )


def _perl_prime_fact(wrong):
    push = "push @factors, $d + 1;" if wrong else "push @factors, $d;"
    return (
        "my $n = <STDIN>; chomp $n; $n = $n + 0;\n"
        "sub prime_factorization {\n"
        "    my ($n) = @_;\n"
        "    my @factors;\n"
        "    my $d = 2;\n"
        "    while ($d * $d <= $n) {\n"
        "        while ($n % $d == 0) { " + push + " $n = int($n / $d); }\n"
        "        $d++;\n"
        "    }\n"
        "    push @factors, $n if $n > 1;\n"
        "    return join(' ', @factors);\n"
        "}\n"
        "print prime_factorization($n), \"\\n\";\n"
    )


def _c_prime_fact(wrong):
    push = "factors[fc++] = d + 1;" if wrong else "factors[fc++] = d;"
    return (
        "#include <stdio.h>\n\n"
        "int main() {\n"
        "    int n; scanf(\"%d\", &n);\n"
        "    int factors[64]; int fc = 0;\n"
        "    int d = 2;\n"
        "    while ((long long)d*d <= n) {\n"
        "        while (n % d == 0) { " + push + " n /= d; }\n"
        "        d++;\n"
        "    }\n"
        "    if (n > 1) factors[fc++] = n;\n"
        "    for (int i=0;i<fc;i++) { if (i) printf(\" \"); printf(\"%d\", factors[i]); }\n"
        "    printf(\"\\n\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_prime_fact(wrong):
    push = "factors.push(d + 1);" if wrong else "factors.push(d);"
    return (
        "use std::io::Read;\n\n"
        "fn main() {\n"
        "    let mut input = String::new();\n"
        "    std::io::stdin().read_to_string(&mut input).unwrap();\n"
        "    let mut n: i64 = input.trim().parse().unwrap();\n"
        "    let mut factors: Vec<i64> = Vec::new();\n"
        "    let mut d: i64 = 2;\n"
        "    while d * d <= n {\n"
        "        while n % d == 0 { " + push + " n /= d; }\n"
        "        d += 1;\n"
        "    }\n"
        "    if n > 1 { factors.push(n); }\n"
        "    let strs: Vec<String> = factors.iter().map(|x| x.to_string()).collect();\n"
        "    println!(\"{}\", strs.join(\" \"));\n"
        "}\n"
    )


# ── contains-duplicate-within-k ──────────────────────────────────────────────
def _js_contains_dup(wrong):
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n); const k = data[1+n];\n"
        "function contains_nearby_duplicate(nums, k) {\n"
        "    const last = {}; let found = false;\n"
        "    for (let i=0;i<nums.length;i++) {\n"
        "        if (last[nums[i]] !== undefined && i - last[nums[i]] <= k) found = true;\n"
        "        last[nums[i]] = i;\n"
        "    }\n"
        f"    return {'!found' if wrong else 'found'};\n"
        "}\n"
        "console.log(contains_nearby_duplicate(nums, k) ? 'true' : 'false');\n"
    )


def _ts_contains_dup(wrong):
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n); const k = data[1+n];\n"
        "function contains_nearby_duplicate(nums: number[], k: number): boolean {\n"
        "    const last: Record<number, number> = {}; let found = false;\n"
        "    for (let i=0;i<nums.length;i++) {\n"
        "        if (last[nums[i]] !== undefined && i - last[nums[i]] <= k) found = true;\n"
        "        last[nums[i]] = i;\n"
        "    }\n"
        f"    return {'!found' if wrong else 'found'};\n"
        "}\n"
        "console.log(contains_nearby_duplicate(nums, k) ? 'true' : 'false');\n"
    )


def _java_contains_dup(wrong):
    return (
        "import java.util.Scanner;\n"
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        int n = sc.nextInt();\n"
        "        int[] nums = new int[n];\n"
        "        for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "        int k = sc.nextInt();\n"
        "        System.out.println(contains_nearby_duplicate(nums, k) ? \"true\" : \"false\");\n"
        "    }\n"
        "    static boolean contains_nearby_duplicate(int[] nums, int k) {\n"
        "        java.util.HashMap<Integer,Integer> last = new java.util.HashMap<>();\n"
        "        boolean found = false;\n"
        "        for (int i=0;i<nums.length;i++) {\n"
        "            if (last.containsKey(nums[i]) && i - last.get(nums[i]) <= k) found = true;\n"
        "            last.put(nums[i], i);\n"
        "        }\n"
        f"        return {'!found' if wrong else 'found'};\n"
        "    }\n"
        "}\n"
    )


def _cpp_contains_dup(wrong):
    return (
        "#include <iostream>\n#include <vector>\n#include <unordered_map>\nusing namespace std;\n\n"
        "bool contains_nearby_duplicate(vector<int>& nums, int k) {\n"
        "    unordered_map<int,int> last; bool found = false;\n"
        "    for (int i=0;i<(int)nums.size();i++) {\n"
        "        auto it = last.find(nums[i]);\n"
        "        if (it != last.end() && i - it->second <= k) found = true;\n"
        "        last[nums[i]] = i;\n"
        "    }\n"
        f"    return {'!found' if wrong else 'found'};\n"
        "}\n\n"
        "int main() {\n"
        "    int n; cin >> n;\n"
        "    vector<int> nums(n);\n"
        "    for (int i=0;i<n;i++) cin >> nums[i];\n"
        "    int k; cin >> k;\n"
        "    cout << (contains_nearby_duplicate(nums, k) ? \"true\" : \"false\") << endl;\n"
        "    return 0;\n"
        "}\n"
    )


def _csharp_contains_dup(wrong):
    return (
        "class Program {\n"
        "    static void Main() {\n"
        "        var tokens = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, "
        "System.StringSplitOptions.RemoveEmptyEntries);\n"
        "        int idx = 0;\n"
        "        int n = int.Parse(tokens[idx++]);\n"
        "        int[] nums = new int[n];\n"
        "        for (int i=0;i<n;i++) nums[i]=int.Parse(tokens[idx++]);\n"
        "        int k = int.Parse(tokens[idx++]);\n"
        "        System.Console.WriteLine(contains_nearby_duplicate(nums, k) ? \"true\" : \"false\");\n"
        "    }\n"
        "    static bool contains_nearby_duplicate(int[] nums, int k) {\n"
        "        var last = new System.Collections.Generic.Dictionary<int,int>();\n"
        "        bool found = false;\n"
        "        for (int i=0;i<nums.Length;i++) {\n"
        "            if (last.ContainsKey(nums[i]) && i - last[nums[i]] <= k) found = true;\n"
        "            last[nums[i]] = i;\n"
        "        }\n"
        f"        return {'!found' if wrong else 'found'};\n"
        "    }\n"
        "}\n"
    )


def _perl_contains_dup(wrong):
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data;\n"
        "my @nums = @data[0..$n-1];\n"
        "my $k = $data[$n];\n"
        "sub contains_nearby_duplicate {\n"
        "    my ($nums, $k) = @_;\n"
        "    my %last; my $found = 0;\n"
        "    for (my $i = 0; $i < scalar(@$nums); $i++) {\n"
        "        if (exists $last{$nums->[$i]} && $i - $last{$nums->[$i]} <= $k) { $found = 1; }\n"
        "        $last{$nums->[$i]} = $i;\n"
        "    }\n"
        f"    return {'!$found' if wrong else '$found'};\n"
        "}\n"
        "print contains_nearby_duplicate(\\@nums, $k) ? \"true\\n\" : \"false\\n\";\n"
    )


def _c_contains_dup(wrong):
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "int contains_nearby_duplicate(int* nums, int n, int k) {\n"
        "    int OFFSET = 100000;\n"
        "    int* lastIdx = (int*)malloc(sizeof(int) * 200001);\n"
        "    char* has = (char*)calloc(200001, 1);\n"
        "    int found = 0;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        int ni = nums[i] + OFFSET;\n"
        "        if (ni >= 0 && ni <= 200000) {\n"
        "            if (has[ni] && i - lastIdx[ni] <= k) found = 1;\n"
        "            has[ni] = 1; lastIdx[ni] = i;\n"
        "        }\n"
        "    }\n"
        "    free(lastIdx); free(has);\n"
        f"    return {'!found' if wrong else 'found'};\n"
        "}\n\n"
        "int main() {\n"
        "    int n; scanf(\"%d\", &n);\n"
        "    int* nums = (int*)malloc(sizeof(int) * (n > 0 ? n : 1));\n"
        "    for (int i=0;i<n;i++) scanf(\"%d\", &nums[i]);\n"
        "    int k; scanf(\"%d\", &k);\n"
        "    printf(\"%s\\n\", contains_nearby_duplicate(nums, n, k) ? \"true\" : \"false\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_contains_dup(wrong):
    return (
        "use std::io::Read;\nuse std::collections::HashMap;\n\n"
        "fn contains_nearby_duplicate(nums: &Vec<i32>, k: i32) -> bool {\n"
        "    let mut last: HashMap<i32, i32> = HashMap::new();\n"
        "    let mut found = false;\n"
        "    for i in 0..nums.len() {\n"
        "        if let Some(&j) = last.get(&nums[i]) {\n"
        "            if (i as i32) - j <= k { found = true; }\n"
        "        }\n"
        "        last.insert(nums[i], i as i32);\n"
        "    }\n"
        f"    {'!found' if wrong else 'found'}\n"
        "}\n\n"
        "fn main() {\n"
        "    let mut input = String::new();\n"
        "    std::io::stdin().read_to_string(&mut input).unwrap();\n"
        "    let mut it = input.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize;\n"
        "    let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    let k = it.next().unwrap();\n"
        "    println!(\"{}\", if contains_nearby_duplicate(&nums, k) { \"true\" } else { \"false\" });\n"
        "}\n"
    )


# ── merge-overlapping-intervals ──────────────────────────────────────────────
def _js_merge_intervals(wrong):
    op = "<" if wrong else "<="
    return (
        "const lines = require('fs').readFileSync(0,'utf8').split('\\n');\n"
        "const n = parseInt(lines[0]);\n"
        "const intervals = [];\n"
        "for (let i=0;i<n;i++) { const p = lines[1+i].trim().split(/\\s+/).map(Number); intervals.push(p); }\n"
        "function merge_intervals(intervals) {\n"
        "    if (intervals.length === 0) return [];\n"
        "    const sorted = intervals.map(x => x.slice()).sort((a,b)=>a[0]-b[0]);\n"
        "    const result = [sorted[0]];\n"
        "    for (let i=1;i<sorted.length;i++) {\n"
        "        const last = result[result.length-1]; const cur = sorted[i];\n"
        f"        if (cur[0] {op} last[1]) last[1] = Math.max(last[1], cur[1]);\n"
        "        else result.push(cur);\n"
        "    }\n"
        "    return result;\n"
        "}\n"
        "for (const [s,e] of merge_intervals(intervals)) console.log(s, e);\n"
    )


def _ts_merge_intervals(wrong):
    op = "<" if wrong else "<="
    return (
        "const lines = require('fs').readFileSync(0,'utf8').split('\\n');\n"
        "const n = parseInt(lines[0]);\n"
        "const intervals: number[][] = [];\n"
        "for (let i=0;i<n;i++) { const p = lines[1+i].trim().split(/\\s+/).map(Number); intervals.push(p); }\n"
        "function merge_intervals(intervals: number[][]): number[][] {\n"
        "    if (intervals.length === 0) return [];\n"
        "    const sorted = intervals.map(x => x.slice()).sort((a,b)=>a[0]-b[0]);\n"
        "    const result: number[][] = [sorted[0]];\n"
        "    for (let i=1;i<sorted.length;i++) {\n"
        "        const last = result[result.length-1]; const cur = sorted[i];\n"
        f"        if (cur[0] {op} last[1]) last[1] = Math.max(last[1], cur[1]);\n"
        "        else result.push(cur);\n"
        "    }\n"
        "    return result;\n"
        "}\n"
        "for (const p of merge_intervals(intervals)) console.log(p[0], p[1]);\n"
    )


def _java_merge_intervals(wrong):
    op = "<" if wrong else "<="
    return (
        "import java.util.Scanner;\n"
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        int n = Integer.parseInt(sc.nextLine().trim());\n"
        "        int[][] intervals = new int[n][2];\n"
        "        for (int i=0;i<n;i++) {\n"
        "            String[] p = sc.nextLine().trim().split(\"\\\\s+\");\n"
        "            intervals[i][0] = Integer.parseInt(p[0]); intervals[i][1] = Integer.parseInt(p[1]);\n"
        "        }\n"
        "        for (int[] r : merge_intervals(intervals)) System.out.println(r[0] + \" \" + r[1]);\n"
        "    }\n"
        "    static int[][] merge_intervals(int[][] intervals) {\n"
        "        int n = intervals.length;\n"
        "        if (n == 0) return new int[0][0];\n"
        "        Integer[] idx = new Integer[n];\n"
        "        for (int i=0;i<n;i++) idx[i]=i;\n"
        "        java.util.Arrays.sort(idx, (a,b) -> intervals[a][0]-intervals[b][0]);\n"
        "        java.util.List<int[]> result = new java.util.ArrayList<>();\n"
        "        for (int k=0;k<n;k++) {\n"
        "            int[] cur = intervals[idx[k]];\n"
        "            if (!result.isEmpty()) {\n"
        "                int[] last = result.get(result.size()-1);\n"
        f"                if (cur[0] {op} last[1]) {{ last[1] = Math.max(last[1], cur[1]); continue; }}\n"
        "            }\n"
        "            result.add(new int[]{cur[0], cur[1]});\n"
        "        }\n"
        "        return result.toArray(new int[0][]);\n"
        "    }\n"
        "}\n"
    )


def _cpp_merge_intervals(wrong):
    op = "<" if wrong else "<="
    return (
        "#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n\n"
        "vector<vector<int>> merge_intervals(vector<vector<int>> intervals) {\n"
        "    if (intervals.empty()) return {};\n"
        "    sort(intervals.begin(), intervals.end(), [](const vector<int>& a, const vector<int>& b){ return a[0] < b[0]; });\n"
        "    vector<vector<int>> result; result.push_back(intervals[0]);\n"
        "    for (size_t i=1;i<intervals.size();i++) {\n"
        "        auto& last = result.back(); auto& cur = intervals[i];\n"
        f"        if (cur[0] {op} last[1]) last[1] = max(last[1], cur[1]);\n"
        "        else result.push_back(cur);\n"
        "    }\n"
        "    return result;\n"
        "}\n\n"
        "int main() {\n"
        "    int n; cin >> n;\n"
        "    vector<vector<int>> intervals(n, vector<int>(2));\n"
        "    for (int i=0;i<n;i++) cin >> intervals[i][0] >> intervals[i][1];\n"
        "    for (auto& r : merge_intervals(intervals)) cout << r[0] << ' ' << r[1] << endl;\n"
        "    return 0;\n"
        "}\n"
    )


def _csharp_merge_intervals(wrong):
    op = "<" if wrong else "<="
    return (
        "class Program {\n"
        "    static void Main() {\n"
        "        var tokens = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, "
        "System.StringSplitOptions.RemoveEmptyEntries);\n"
        "        int idx = 0;\n"
        "        int n = int.Parse(tokens[idx++]);\n"
        "        int[][] intervals = new int[n][];\n"
        "        for (int i=0;i<n;i++) { intervals[i] = new int[]{int.Parse(tokens[idx++]), int.Parse(tokens[idx++])}; }\n"
        "        foreach (var r in merge_intervals(intervals)) System.Console.WriteLine(r[0] + \" \" + r[1]);\n"
        "    }\n"
        "    static System.Collections.Generic.List<int[]> merge_intervals(int[][] intervals) {\n"
        "        var result = new System.Collections.Generic.List<int[]>();\n"
        "        if (intervals.Length == 0) return result;\n"
        "        var sorted = new System.Collections.Generic.List<int[]>(intervals);\n"
        "        sorted.Sort((a,b) => a[0].CompareTo(b[0]));\n"
        "        result.Add(new int[]{sorted[0][0], sorted[0][1]});\n"
        "        for (int i=1;i<sorted.Count;i++) {\n"
        "            var last = result[result.Count-1]; var cur = sorted[i];\n"
        f"            if (cur[0] {op} last[1]) last[1] = System.Math.Max(last[1], cur[1]);\n"
        "            else result.Add(new int[]{cur[0], cur[1]});\n"
        "        }\n"
        "        return result;\n"
        "    }\n"
        "}\n"
    )


def _perl_merge_intervals(wrong):
    op = "<" if wrong else "<="
    return (
        "my @lines = split /\\n/, do { local $/; <STDIN> };\n"
        "my $n = $lines[0] + 0;\n"
        "my @intervals;\n"
        "for (my $i=0;$i<$n;$i++) { my @p = split ' ', $lines[1+$i]; push @intervals, [@p]; }\n"
        "sub merge_intervals {\n"
        "    my ($intervals) = @_;\n"
        "    return [] unless @$intervals;\n"
        "    my @sorted = sort { $a->[0] <=> $b->[0] } @$intervals;\n"
        "    my @result = ([$sorted[0][0], $sorted[0][1]]);\n"
        "    for (my $i=1;$i<scalar(@sorted);$i++) {\n"
        "        my $last = $result[-1]; my $cur = $sorted[$i];\n"
        f"        if ($cur->[0] {op} $last->[1]) {{ $last->[1] = $cur->[1] if $cur->[1] > $last->[1]; }}\n"
        "        else { push @result, [$cur->[0], $cur->[1]]; }\n"
        "    }\n"
        "    return \\@result;\n"
        "}\n"
        "for my $r (@{merge_intervals(\\@intervals)}) { print \"$r->[0] $r->[1]\\n\"; }\n"
    )


def _c_merge_intervals(wrong):
    op = "<" if wrong else "<="
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "int cmp(const void* a, const void* b) {\n"
        "    const int* ia = *(const int**)a; const int* ib = *(const int**)b;\n"
        "    return ia[0] - ib[0];\n"
        "}\n\n"
        "int main() {\n"
        "    int n; scanf(\"%d\", &n);\n"
        "    int** intervals = (int**)malloc(sizeof(int*) * (n > 0 ? n : 1));\n"
        "    for (int i=0;i<n;i++) { intervals[i] = (int*)malloc(sizeof(int)*2); scanf(\"%d %d\", &intervals[i][0], &intervals[i][1]); }\n"
        "    if (n == 0) return 0;\n"
        "    qsort(intervals, n, sizeof(int*), cmp);\n"
        "    int** result = (int**)malloc(sizeof(int*) * n);\n"
        "    int rc = 0;\n"
        "    result[rc] = (int*)malloc(sizeof(int)*2);\n"
        "    result[rc][0] = intervals[0][0]; result[rc][1] = intervals[0][1]; rc++;\n"
        "    for (int i=1;i<n;i++) {\n"
        "        int* last = result[rc-1]; int* cur = intervals[i];\n"
        f"        if (cur[0] {op} last[1]) {{ if (cur[1] > last[1]) last[1] = cur[1]; }}\n"
        "        else { result[rc] = (int*)malloc(sizeof(int)*2); result[rc][0]=cur[0]; result[rc][1]=cur[1]; rc++; }\n"
        "    }\n"
        "    for (int i=0;i<rc;i++) printf(\"%d %d\\n\", result[i][0], result[i][1]);\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_merge_intervals(wrong):
    op = "<" if wrong else "<="
    return (
        "use std::io::Read;\n\n"
        "fn merge_intervals(mut intervals: Vec<Vec<i32>>) -> Vec<Vec<i32>> {\n"
        "    if intervals.is_empty() { return vec![]; }\n"
        "    intervals.sort_by(|a, b| a[0].cmp(&b[0]));\n"
        "    let mut result: Vec<Vec<i32>> = vec![intervals[0].clone()];\n"
        "    for i in 1..intervals.len() {\n"
        "        let cur = &intervals[i];\n"
        "        let last_idx = result.len() - 1;\n"
        f"        if cur[0] {op} result[last_idx][1] {{ if cur[1] > result[last_idx][1] {{ result[last_idx][1] = cur[1]; }} }}\n"
        "        else { result.push(cur.clone()); }\n"
        "    }\n"
        "    result\n"
        "}\n\n"
        "fn main() {\n"
        "    let mut input = String::new();\n"
        "    std::io::stdin().read_to_string(&mut input).unwrap();\n"
        "    let mut lines = input.lines();\n"
        "    let n: usize = lines.next().unwrap().trim().parse().unwrap();\n"
        "    let mut intervals: Vec<Vec<i32>> = Vec::new();\n"
        "    for _ in 0..n {\n"
        "        let l = lines.next().unwrap();\n"
        "        let p: Vec<i32> = l.split_whitespace().map(|x| x.parse().unwrap()).collect();\n"
        "        intervals.push(p);\n"
        "    }\n"
        "    for r in merge_intervals(intervals) { println!(\"{} {}\", r[0], r[1]); }\n"
        "}\n"
    )


# ── max-depth-binary-tree (parse tokens -> tree; no serialize needed) ───────
_JS_PARSE_TREE = (
    "function parseTree(tokens) {\n"
    "    if (tokens.length === 0 || tokens[0] === 'null') return null;\n"
    "    const root = { val: parseInt(tokens[0]), left: null, right: null };\n"
    "    const queue = [root]; let i = 1, qi = 0;\n"
    "    while (qi < queue.length && i < tokens.length) {\n"
    "        const node = queue[qi]; qi++;\n"
    "        if (i < tokens.length) { if (tokens[i] !== 'null') { node.left = { val: parseInt(tokens[i]), left: null, right: null }; queue.push(node.left); } i++; }\n"
    "        if (i < tokens.length) { if (tokens[i] !== 'null') { node.right = { val: parseInt(tokens[i]), left: null, right: null }; queue.push(node.right); } i++; }\n"
    "    }\n"
    "    return root;\n"
    "}\n"
)


def _js_max_depth(wrong):
    a = "" if wrong else "1 + "
    return (
        "const tokens = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).filter(t => t.length > 0);\n"
        f"{_JS_PARSE_TREE}"
        "const root = parseTree(tokens);\n"
        "function max_depth(root) {\n"
        "    if (root === null) return 0;\n"
        f"    return {a}Math.max(max_depth(root.left), max_depth(root.right));\n"
        "}\n"
        "console.log(max_depth(root));\n"
    )


def _ts_max_depth(wrong):
    a = "" if wrong else "1 + "
    return (
        "interface TreeNode { val: number; left: TreeNode | null; right: TreeNode | null; }\n"
        "const tokens: string[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).filter((t: string) => t.length > 0);\n"
        "function parseTree(tokens: string[]): TreeNode | null {\n"
        "    if (tokens.length === 0 || tokens[0] === 'null') return null;\n"
        "    const root: TreeNode = { val: parseInt(tokens[0]), left: null, right: null };\n"
        "    const queue: TreeNode[] = [root]; let i = 1, qi = 0;\n"
        "    while (qi < queue.length && i < tokens.length) {\n"
        "        const node = queue[qi]; qi++;\n"
        "        if (i < tokens.length) { if (tokens[i] !== 'null') { node.left = { val: parseInt(tokens[i]), left: null, right: null }; queue.push(node.left); } i++; }\n"
        "        if (i < tokens.length) { if (tokens[i] !== 'null') { node.right = { val: parseInt(tokens[i]), left: null, right: null }; queue.push(node.right); } i++; }\n"
        "    }\n"
        "    return root;\n"
        "}\n"
        "const root = parseTree(tokens);\n"
        "function max_depth(root: TreeNode | null): number {\n"
        "    if (root === null) return 0;\n"
        f"    return {a}Math.max(max_depth(root.left), max_depth(root.right));\n"
        "}\n"
        "console.log(max_depth(root));\n"
    )


def _java_max_depth(wrong):
    a = "" if wrong else "1 + "
    return (
        "import java.util.*;\n"
        "class Node { int val; Node left; Node right; Node(int v) { val = v; } }\n"
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        List<String> tokens = new ArrayList<>();\n"
        "        while (sc.hasNext()) tokens.add(sc.next());\n"
        "        Node root = parseTree(tokens);\n"
        "        System.out.println(max_depth(root));\n"
        "    }\n"
        "    static Node parseTree(List<String> tokens) {\n"
        "        if (tokens.isEmpty() || tokens.get(0).equals(\"null\")) return null;\n"
        "        Node root = new Node(Integer.parseInt(tokens.get(0)));\n"
        "        List<Node> queue = new ArrayList<>(); queue.add(root);\n"
        "        int i = 1, qi = 0;\n"
        "        while (qi < queue.size() && i < tokens.size()) {\n"
        "            Node node = queue.get(qi); qi++;\n"
        "            if (i < tokens.size()) { if (!tokens.get(i).equals(\"null\")) { node.left = new Node(Integer.parseInt(tokens.get(i))); queue.add(node.left); } i++; }\n"
        "            if (i < tokens.size()) { if (!tokens.get(i).equals(\"null\")) { node.right = new Node(Integer.parseInt(tokens.get(i))); queue.add(node.right); } i++; }\n"
        "        }\n"
        "        return root;\n"
        "    }\n"
        "    static int max_depth(Node root) {\n"
        "        if (root == null) return 0;\n"
        f"        return {a}Math.max(max_depth(root.left), max_depth(root.right));\n"
        "    }\n"
        "}\n"
    )


def _cpp_max_depth(wrong):
    a = "" if wrong else "1 + "
    return (
        "#include <iostream>\n#include <vector>\n#include <string>\nusing namespace std;\n\n"
        "struct Node { int val; Node* left; Node* right; Node(int v): val(v), left(nullptr), right(nullptr) {} };\n\n"
        "Node* parseTree(vector<string>& tokens) {\n"
        "    if (tokens.empty() || tokens[0] == \"null\") return nullptr;\n"
        "    Node* root = new Node(stoi(tokens[0]));\n"
        "    vector<Node*> queue = {root};\n"
        "    size_t i = 1, qi = 0;\n"
        "    while (qi < queue.size() && i < tokens.size()) {\n"
        "        Node* node = queue[qi]; qi++;\n"
        "        if (i < tokens.size()) { if (tokens[i] != \"null\") { node->left = new Node(stoi(tokens[i])); queue.push_back(node->left); } i++; }\n"
        "        if (i < tokens.size()) { if (tokens[i] != \"null\") { node->right = new Node(stoi(tokens[i])); queue.push_back(node->right); } i++; }\n"
        "    }\n"
        "    return root;\n"
        "}\n\n"
        "int max_depth(Node* root) {\n"
        "    if (root == nullptr) return 0;\n"
        f"    return {a}max(max_depth(root->left), max_depth(root->right));\n"
        "}\n\n"
        "int main() {\n"
        "    vector<string> tokens; string tok;\n"
        "    while (cin >> tok) tokens.push_back(tok);\n"
        "    Node* root = parseTree(tokens);\n"
        "    cout << max_depth(root) << endl;\n"
        "    return 0;\n"
        "}\n"
    )


# ── construct-tree-preorder-inorder (build tree; serialize -> no parse) ────
def _js_build_tree(wrong):
    left_expr, right_expr = ("preorder.slice(1 + mid), inorder.slice(mid + 1)",
                              "preorder.slice(1, 1 + mid), inorder.slice(0, mid)") if wrong else \
        ("preorder.slice(1, 1 + mid), inorder.slice(0, mid)",
         "preorder.slice(1 + mid), inorder.slice(mid + 1)")
    return (
        "const lines = require('fs').readFileSync(0,'utf8').split('\\n');\n"
        "const preorder = lines[0].trim().split(/\\s+/).filter(x=>x.length).map(Number);\n"
        "const inorder = lines[1].trim().split(/\\s+/).filter(x=>x.length).map(Number);\n"
        "function build_tree(preorder, inorder) {\n"
        "    if (preorder.length === 0) return null;\n"
        "    const rootVal = preorder[0];\n"
        "    const mid = inorder.indexOf(rootVal);\n"
        "    const root = { val: rootVal, left: null, right: null };\n"
        f"    root.left = build_tree({left_expr});\n"
        f"    root.right = build_tree({right_expr});\n"
        "    return root;\n"
        "}\n"
        "function serialize(root) {\n"
        "    const out = []; if (root === null) return out;\n"
        "    out.push(root.val); const queue = [root]; let qi = 0;\n"
        "    while (qi < queue.length) {\n"
        "        const node = queue[qi]; qi++;\n"
        "        for (const child of [node.left, node.right]) {\n"
        "            if (child === null) out.push(null); else { out.push(child.val); queue.push(child); }\n"
        "        }\n"
        "    }\n"
        "    while (out.length && out[out.length-1] === null) out.pop();\n"
        "    return out;\n"
        "}\n"
        "const root = build_tree(preorder, inorder);\n"
        "console.log(serialize(root).map(v => v === null ? 'null' : v).join(' '));\n"
    )


def _ts_build_tree(wrong):
    left_expr, right_expr = ("preorder.slice(1 + mid), inorder.slice(mid + 1)",
                              "preorder.slice(1, 1 + mid), inorder.slice(0, mid)") if wrong else \
        ("preorder.slice(1, 1 + mid), inorder.slice(0, mid)",
         "preorder.slice(1 + mid), inorder.slice(mid + 1)")
    return (
        "interface TreeNode { val: number; left: TreeNode | null; right: TreeNode | null; }\n"
        "const lines = require('fs').readFileSync(0,'utf8').split('\\n');\n"
        "const preorder: number[] = lines[0].trim().split(/\\s+/).filter((x: string)=>x.length).map(Number);\n"
        "const inorder: number[] = lines[1].trim().split(/\\s+/).filter((x: string)=>x.length).map(Number);\n"
        "function build_tree(preorder: number[], inorder: number[]): TreeNode | null {\n"
        "    if (preorder.length === 0) return null;\n"
        "    const rootVal = preorder[0];\n"
        "    const mid = inorder.indexOf(rootVal);\n"
        "    const root: TreeNode = { val: rootVal, left: null, right: null };\n"
        f"    root.left = build_tree({left_expr});\n"
        f"    root.right = build_tree({right_expr});\n"
        "    return root;\n"
        "}\n"
        "function serialize(root: TreeNode | null): (number|null)[] {\n"
        "    const out: (number|null)[] = []; if (root === null) return out;\n"
        "    out.push(root.val); const queue: TreeNode[] = [root]; let qi = 0;\n"
        "    while (qi < queue.length) {\n"
        "        const node = queue[qi]; qi++;\n"
        "        for (const child of [node.left, node.right]) {\n"
        "            if (child === null) out.push(null); else { out.push(child.val); queue.push(child); }\n"
        "        }\n"
        "    }\n"
        "    while (out.length && out[out.length-1] === null) out.pop();\n"
        "    return out;\n"
        "}\n"
        "const root = build_tree(preorder, inorder);\n"
        "console.log(serialize(root).map(v => v === null ? 'null' : String(v)).join(' '));\n"
    )


def _java_build_tree(wrong):
    if wrong:
        recurse = (
            "        root.left = helper(pre, ps + 1 + leftSize, pe, in, mid + 1, ie);\n"
            "        root.right = helper(pre, ps + 1, ps + 1 + leftSize, in, is, mid);\n"
        )
    else:
        recurse = (
            "        root.left = helper(pre, ps + 1, ps + 1 + leftSize, in, is, mid);\n"
            "        root.right = helper(pre, ps + 1 + leftSize, pe, in, mid + 1, ie);\n"
        )
    return (
        "import java.util.*;\n"
        "class Node { int val; Node left; Node right; Node(int v) { val = v; } }\n"
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        int[] preorder = Arrays.stream(sc.nextLine().trim().split(\"\\\\s+\")).mapToInt(Integer::parseInt).toArray();\n"
        "        int[] inorder = Arrays.stream(sc.nextLine().trim().split(\"\\\\s+\")).mapToInt(Integer::parseInt).toArray();\n"
        "        Node root = build_tree(preorder, inorder);\n"
        "        List<String> out = new ArrayList<>();\n"
        "        for (Object v : serialize(root)) out.add(v == null ? \"null\" : v.toString());\n"
        "        System.out.println(String.join(\" \", out));\n"
        "    }\n"
        "    static Node build_tree(int[] preorder, int[] inorder) {\n"
        "        return helper(preorder, 0, preorder.length, inorder, 0, inorder.length);\n"
        "    }\n"
        "    static Node helper(int[] pre, int ps, int pe, int[] in, int is, int ie) {\n"
        "        if (ps >= pe) return null;\n"
        "        int rootVal = pre[ps];\n"
        "        int mid = is; while (in[mid] != rootVal) mid++;\n"
        "        int leftSize = mid - is;\n"
        "        Node root = new Node(rootVal);\n"
        + recurse +
        "        return root;\n"
        "    }\n"
        "    static List<Integer> serialize(Node root) {\n"
        "        List<Integer> out = new ArrayList<>();\n"
        "        if (root == null) return out;\n"
        "        out.add(root.val);\n"
        "        List<Node> queue = new ArrayList<>(); queue.add(root);\n"
        "        int qi = 0;\n"
        "        while (qi < queue.size()) {\n"
        "            Node node = queue.get(qi); qi++;\n"
        "            for (Node child : new Node[]{node.left, node.right}) {\n"
        "                if (child == null) out.add(null); else { out.add(child.val); queue.add(child); }\n"
        "            }\n"
        "        }\n"
        "        while (!out.isEmpty() && out.get(out.size()-1) == null) out.remove(out.size()-1);\n"
        "        return out;\n"
        "    }\n"
        "}\n"
    )


def _cpp_build_tree(wrong):
    if wrong:
        recurse = (
            "    root->left = helper(pre, ps + 1 + leftSize, pe, in, mid + 1, ie);\n"
            "    root->right = helper(pre, ps + 1, ps + 1 + leftSize, in, is, mid);\n"
        )
    else:
        recurse = (
            "    root->left = helper(pre, ps + 1, ps + 1 + leftSize, in, is, mid);\n"
            "    root->right = helper(pre, ps + 1 + leftSize, pe, in, mid + 1, ie);\n"
        )
    return (
        "#include <iostream>\n#include <vector>\n#include <string>\n#include <sstream>\nusing namespace std;\n\n"
        "struct Node { int val; Node* left; Node* right; Node(int v): val(v), left(nullptr), right(nullptr) {} };\n\n"
        "Node* helper(vector<int>& pre, int ps, int pe, vector<int>& in, int is, int ie) {\n"
        "    if (ps >= pe) return nullptr;\n"
        "    int rootVal = pre[ps];\n"
        "    int mid = is; while (in[mid] != rootVal) mid++;\n"
        "    int leftSize = mid - is;\n"
        "    Node* root = new Node(rootVal);\n"
        + recurse +
        "    return root;\n"
        "}\n\n"
        "Node* build_tree(vector<int> preorder, vector<int> inorder) {\n"
        "    return helper(preorder, 0, (int)preorder.size(), inorder, 0, (int)inorder.size());\n"
        "}\n\n"
        "vector<string> serializeTree(Node* root) {\n"
        "    vector<string> out;\n"
        "    if (root == nullptr) return out;\n"
        "    out.push_back(to_string(root->val));\n"
        "    vector<Node*> queue = {root}; size_t qi = 0;\n"
        "    while (qi < queue.size()) {\n"
        "        Node* node = queue[qi]; qi++;\n"
        "        for (Node* child : {node->left, node->right}) {\n"
        "            if (child == nullptr) out.push_back(\"null\"); else { out.push_back(to_string(child->val)); queue.push_back(child); }\n"
        "        }\n"
        "    }\n"
        "    while (!out.empty() && out.back() == \"null\") out.pop_back();\n"
        "    return out;\n"
        "}\n\n"
        "int main() {\n"
        "    string line1, line2;\n"
        "    getline(cin, line1); getline(cin, line2);\n"
        "    vector<int> preorder, inorder;\n"
        "    istringstream ss1(line1), ss2(line2);\n"
        "    int x;\n"
        "    while (ss1 >> x) preorder.push_back(x);\n"
        "    while (ss2 >> x) inorder.push_back(x);\n"
        "    Node* root = build_tree(preorder, inorder);\n"
        "    auto out = serializeTree(root);\n"
        "    for (size_t i=0;i<out.size();i++) { if (i) cout << ' '; cout << out[i]; }\n"
        "    cout << endl;\n"
        "    return 0;\n"
        "}\n"
    )


_SIMPLE_BUILDERS = {
    "two-sum": {"javascript": _js_two_sum, "typescript": _ts_two_sum, "java": _java_two_sum, "cpp": _cpp_two_sum,
                "csharp": _csharp_two_sum, "perl": _perl_two_sum, "c": _c_two_sum, "rust": _rust_two_sum},
    "maximum-subarray": {"javascript": _js_max_subarray, "typescript": _ts_max_subarray, "java": _java_max_subarray, "cpp": _cpp_max_subarray,
                         "csharp": _csharp_max_subarray, "perl": _perl_max_subarray, "c": _c_max_subarray, "rust": _rust_max_subarray},
    "prime-factorization": {"javascript": _js_prime_fact, "typescript": _ts_prime_fact, "java": _java_prime_fact, "cpp": _cpp_prime_fact,
                            "csharp": _csharp_prime_fact, "perl": _perl_prime_fact, "c": _c_prime_fact, "rust": _rust_prime_fact},
    "contains-duplicate-within-k": {"javascript": _js_contains_dup, "typescript": _ts_contains_dup, "java": _java_contains_dup, "cpp": _cpp_contains_dup,
                                    "csharp": _csharp_contains_dup, "perl": _perl_contains_dup, "c": _c_contains_dup, "rust": _rust_contains_dup},
    "merge-overlapping-intervals": {"javascript": _js_merge_intervals, "typescript": _ts_merge_intervals, "java": _java_merge_intervals, "cpp": _cpp_merge_intervals,
                                    "csharp": _csharp_merge_intervals, "perl": _perl_merge_intervals, "c": _c_merge_intervals, "rust": _rust_merge_intervals},
}

# Tree problems: only javascript/typescript/java/cpp implemented in this
# batch (csharp/perl/c/rust already have these two verified from their
# original ladders -- confirmed via the ledger before writing this script).
_TREE_BUILDERS = {
    "max-depth-binary-tree": {"javascript": _js_max_depth, "typescript": _ts_max_depth, "java": _java_max_depth, "cpp": _cpp_max_depth},
    "construct-tree-preorder-inorder": {"javascript": _js_build_tree, "typescript": _ts_build_tree, "java": _java_build_tree, "cpp": _cpp_build_tree},
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

    groups = []
    for pid, builders in _SIMPLE_BUILDERS.items():
        for lang in _TARGET_LANGUAGES:
            groups.append((pid, lang, builders[lang]))
    for pid, builders in _TREE_BUILDERS.items():
        for lang in builders:
            groups.append((pid, lang, builders[lang]))

    results = []
    skipped = 0
    for pid, lang, build in groups:
        cases, tsv = load_cases(con, pid)
        if ledger.already_verified(con, pid, lang, "program", test_suite_version=tsv):
            skipped += 1
            continue
        r = await verify_one(pid, lang, cases, build)
        results.append(r)
        status = "PASS" if r["outcome"] == "verified" else "FAIL"
        print(f"[{status}] {lang:10s}(program) {pid:32s} {r['outcome']:18s} {r['detail'][:130]}", flush=True)
        if r["outcome"] == "verified":
            row = con.execute("SELECT starter_code FROM problems WHERE id=?", (pid,)).fetchone()
            sc = json.loads(row["starter_code"])
            sc[lang] = build(False)
            con.execute("UPDATE problems SET starter_code=? WHERE id=?", (json.dumps(sc), pid))
            con.commit()
            ledger.record_cell(
                con, problem_id=pid, language=lang, mode="program",
                verification_level=ledger.LEVEL_VERIFIED, status="pass",
                adapter_version=f"{lang}-program-ladder-gap-v1",
                test_suite_version=tsv, duration_ms=r["duration_ms"],
            )

    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL attempted: {len(results)}  skipped: {skipped}")
    print(f"verified={len(verified)}  reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    (REPO_ROOT / "docs" / "atlascode-program-mode-ladder-gap.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
