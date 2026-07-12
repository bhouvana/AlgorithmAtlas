"""Function Mode expansion across all 8 "core" languages (javascript,
typescript, java, cpp, csharp, perl, c, rust) at once, for 9 problems that
currently have ZERO non-Python Function Mode coverage: median-of-medians,
run-length-encoding, sieve-of-eratosthenes, string-hashing, z-algorithm,
distinct-subsets-count, rotate-image-90, search-2d-matrix, remove-k-digits.

Multi-language variant of scale_port_go_function.py's single-language
pattern -- IMPLS[pid][lang] holds (correct_source, wrong_source) pairs,
looped over every (pid, lang) combination.

Values checked against the REAL 40-case corpus before writing any
algorithm (see conversation/audit): median-of-medians nums arrays up to
~58K elements (needs a real O(n log n) sort, not bubble sort); sieve n up
to 100000; remove-k-digits num length up to ~47.7K with k up to ~21.9K
(needs the O(n) monotonic-stack solution, not anything O(n*k)).
reverse-bits was deliberately EXCLUDED from this batch: its corpus n goes
up to 4294967293 (near 2**32-1), whose reversed bit-pattern can exceed
int32 range, but every compiled adapter's TypeSpec "integer" hard-maps to
a 32-bit native int (see compiled_adapters.py _java_type/_c_type/
_rust_type/_cpp_type/_csharp_type) with no wider-int distinction -- same
class of gap as the 10 problems in docs/atlascode-bigint-numeric-audit.json,
just not yet in that audit. Needs a real fix (widen the TypeSpec or special-
case this problem), not a blind implementation attempt.
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
LANGS = ["javascript", "typescript", "java", "cpp", "csharp", "perl", "c", "rust"]

IMPLS: dict[str, dict[str, tuple[str, str]]] = {}


def reg(pid, lang, correct, wrong):
    IMPLS.setdefault(pid, {})[lang] = (correct, wrong)


# ═════════════════════════════════════════════════════════════════════════
# median-of-medians -> kth_smallest(nums, k)  (1-indexed k-th smallest)
# wrong: returns the k-th LARGEST instead (index n-k), safe (never OOB
# for 1<=k<=n) but wrong whenever the array isn't a palindrome of itself.
# ═════════════════════════════════════════════════════════════════════════

reg("median-of-medians", "javascript",
    "function kth_smallest(nums, k) {\n"
    "    const s = nums.slice().sort((a, b) => a - b);\n"
    "    return s[k - 1];\n"
    "}\n",
    "function kth_smallest(nums, k) {\n"
    "    const s = nums.slice().sort((a, b) => a - b);\n"
    "    return s[s.length - k];\n"
    "}\n")

reg("median-of-medians", "typescript",
    "function kth_smallest(nums: number[], k: number): number {\n"
    "    const s = nums.slice().sort((a, b) => a - b);\n"
    "    return s[k - 1];\n"
    "}\n",
    "function kth_smallest(nums: number[], k: number): number {\n"
    "    const s = nums.slice().sort((a, b) => a - b);\n"
    "    return s[s.length - k];\n"
    "}\n")

reg("median-of-medians", "perl",
    "sub kth_smallest {\n"
    "    my ($nums, $k) = @_;\n"
    "    my @s = sort { $a <=> $b } @{$nums};\n"
    "    return $s[$k - 1];\n"
    "}\n",
    "sub kth_smallest {\n"
    "    my ($nums, $k) = @_;\n"
    "    my @s = sort { $a <=> $b } @{$nums};\n"
    "    return $s[scalar(@s) - $k];\n"
    "}\n")

reg("median-of-medians", "java",
    "class Solution {\n"
    "    public int kth_smallest(int[] nums, int k) {\n"
    "        int[] s = nums.clone();\n"
    "        java.util.Arrays.sort(s);\n"
    "        return s[k - 1];\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public int kth_smallest(int[] nums, int k) {\n"
    "        int[] s = nums.clone();\n"
    "        java.util.Arrays.sort(s);\n"
    "        return s[s.length - k];\n"
    "    }\n"
    "}\n")

reg("median-of-medians", "cpp",
    "class Solution {\n"
    "public:\n"
    "    int kth_smallest(std::vector<int> nums, int k) {\n"
    "        std::sort(nums.begin(), nums.end());\n"
    "        return nums[k - 1];\n"
    "    }\n"
    "};\n",
    "class Solution {\n"
    "public:\n"
    "    int kth_smallest(std::vector<int> nums, int k) {\n"
    "        std::sort(nums.begin(), nums.end());\n"
    "        return nums[nums.size() - k];\n"
    "    }\n"
    "};\n")

reg("median-of-medians", "csharp",
    "class Solution {\n"
    "    public static int kth_smallest(int[] nums, int k) {\n"
    "        var s = (int[])nums.Clone();\n"
    "        System.Array.Sort(s);\n"
    "        return s[k - 1];\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public static int kth_smallest(int[] nums, int k) {\n"
    "        var s = (int[])nums.Clone();\n"
    "        System.Array.Sort(s);\n"
    "        return s[s.Length - k];\n"
    "    }\n"
    "}\n")

reg("median-of-medians", "c",
    "int __atlas_cmp_int(const void *a, const void *b) {\n"
    "    int x = *(const int *)a, y = *(const int *)b;\n"
    "    return x - y;\n"
    "}\n"
    "int kth_smallest(AtlasIntArray nums, int k) {\n"
    "    int n = nums.size;\n"
    "    int *a = (int *)malloc(sizeof(int) * (n ? n : 1));\n"
    "    memcpy(a, nums.data, sizeof(int) * n);\n"
    "    qsort(a, n, sizeof(int), __atlas_cmp_int);\n"
    "    int res = a[k - 1];\n"
    "    free(a);\n"
    "    return res;\n"
    "}\n",
    "int __atlas_cmp_int(const void *a, const void *b) {\n"
    "    int x = *(const int *)a, y = *(const int *)b;\n"
    "    return x - y;\n"
    "}\n"
    "int kth_smallest(AtlasIntArray nums, int k) {\n"
    "    int n = nums.size;\n"
    "    int *a = (int *)malloc(sizeof(int) * (n ? n : 1));\n"
    "    memcpy(a, nums.data, sizeof(int) * n);\n"
    "    qsort(a, n, sizeof(int), __atlas_cmp_int);\n"
    "    int res = a[n - k];\n"
    "    free(a);\n"
    "    return res;\n"
    "}\n")

reg("median-of-medians", "rust",
    "fn kth_smallest(mut nums: Vec<i32>, k: i32) -> i32 {\n"
    "    nums.sort();\n"
    "    nums[(k - 1) as usize]\n"
    "}\n",
    "fn kth_smallest(mut nums: Vec<i32>, k: i32) -> i32 {\n"
    "    nums.sort();\n"
    "    let n = nums.len() as i32;\n"
    "    nums[(n - k) as usize]\n"
    "}\n")


# ═════════════════════════════════════════════════════════════════════════
# run-length-encoding -> rle_encode(s)  ("aaabbc" -> "3a2b1c")
# wrong: emits char-then-count ("a3b2c1") instead of count-then-char.
# ═════════════════════════════════════════════════════════════════════════

reg("run-length-encoding", "javascript",
    "function rle_encode(s) {\n"
    "    let out = '';\n"
    "    let i = 0;\n"
    "    while (i < s.length) {\n"
    "        let j = i;\n"
    "        while (j < s.length && s[j] === s[i]) j++;\n"
    "        out += (j - i) + s[i];\n"
    "        i = j;\n"
    "    }\n"
    "    return out;\n"
    "}\n",
    "function rle_encode(s) {\n"
    "    let out = '';\n"
    "    let i = 0;\n"
    "    while (i < s.length) {\n"
    "        let j = i;\n"
    "        while (j < s.length && s[j] === s[i]) j++;\n"
    "        out += s[i] + (j - i);\n"
    "        i = j;\n"
    "    }\n"
    "    return out;\n"
    "}\n")

reg("run-length-encoding", "typescript",
    "function rle_encode(s: string): string {\n"
    "    let out = '';\n"
    "    let i = 0;\n"
    "    while (i < s.length) {\n"
    "        let j = i;\n"
    "        while (j < s.length && s[j] === s[i]) j++;\n"
    "        out += (j - i) + s[i];\n"
    "        i = j;\n"
    "    }\n"
    "    return out;\n"
    "}\n",
    "function rle_encode(s: string): string {\n"
    "    let out = '';\n"
    "    let i = 0;\n"
    "    while (i < s.length) {\n"
    "        let j = i;\n"
    "        while (j < s.length && s[j] === s[i]) j++;\n"
    "        out += s[i] + (j - i);\n"
    "        i = j;\n"
    "    }\n"
    "    return out;\n"
    "}\n")

reg("run-length-encoding", "perl",
    "sub rle_encode {\n"
    "    my ($s) = @_;\n"
    "    my @chars = split //, $s;\n"
    "    my $out = '';\n"
    "    my $i = 0;\n"
    "    my $n = scalar(@chars);\n"
    "    while ($i < $n) {\n"
    "        my $j = $i;\n"
    "        while ($j < $n && $chars[$j] eq $chars[$i]) { $j++; }\n"
    "        $out .= ($j - $i) . $chars[$i];\n"
    "        $i = $j;\n"
    "    }\n"
    "    return $out;\n"
    "}\n",
    "sub rle_encode {\n"
    "    my ($s) = @_;\n"
    "    my @chars = split //, $s;\n"
    "    my $out = '';\n"
    "    my $i = 0;\n"
    "    my $n = scalar(@chars);\n"
    "    while ($i < $n) {\n"
    "        my $j = $i;\n"
    "        while ($j < $n && $chars[$j] eq $chars[$i]) { $j++; }\n"
    "        $out .= $chars[$i] . ($j - $i);\n"
    "        $i = $j;\n"
    "    }\n"
    "    return $out;\n"
    "}\n")

reg("run-length-encoding", "java",
    "class Solution {\n"
    "    public String rle_encode(String s) {\n"
    "        StringBuilder out = new StringBuilder();\n"
    "        int i = 0, n = s.length();\n"
    "        while (i < n) {\n"
    "            int j = i;\n"
    "            while (j < n && s.charAt(j) == s.charAt(i)) j++;\n"
    "            out.append(j - i).append(s.charAt(i));\n"
    "            i = j;\n"
    "        }\n"
    "        return out.toString();\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public String rle_encode(String s) {\n"
    "        StringBuilder out = new StringBuilder();\n"
    "        int i = 0, n = s.length();\n"
    "        while (i < n) {\n"
    "            int j = i;\n"
    "            while (j < n && s.charAt(j) == s.charAt(i)) j++;\n"
    "            out.append(s.charAt(i)).append(j - i);\n"
    "            i = j;\n"
    "        }\n"
    "        return out.toString();\n"
    "    }\n"
    "}\n")

reg("run-length-encoding", "cpp",
    "class Solution {\n"
    "public:\n"
    "    std::string rle_encode(std::string s) {\n"
    "        std::string out;\n"
    "        size_t i = 0, n = s.size();\n"
    "        while (i < n) {\n"
    "            size_t j = i;\n"
    "            while (j < n && s[j] == s[i]) j++;\n"
    "            out += std::to_string(j - i);\n"
    "            out += s[i];\n"
    "            i = j;\n"
    "        }\n"
    "        return out;\n"
    "    }\n"
    "};\n",
    "class Solution {\n"
    "public:\n"
    "    std::string rle_encode(std::string s) {\n"
    "        std::string out;\n"
    "        size_t i = 0, n = s.size();\n"
    "        while (i < n) {\n"
    "            size_t j = i;\n"
    "            while (j < n && s[j] == s[i]) j++;\n"
    "            out += s[i];\n"
    "            out += std::to_string(j - i);\n"
    "            i = j;\n"
    "        }\n"
    "        return out;\n"
    "    }\n"
    "};\n")

reg("run-length-encoding", "csharp",
    "class Solution {\n"
    "    public static string rle_encode(string s) {\n"
    "        var out_ = new System.Text.StringBuilder();\n"
    "        int i = 0, n = s.Length;\n"
    "        while (i < n) {\n"
    "            int j = i;\n"
    "            while (j < n && s[j] == s[i]) j++;\n"
    "            out_.Append(j - i).Append(s[i]);\n"
    "            i = j;\n"
    "        }\n"
    "        return out_.ToString();\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public static string rle_encode(string s) {\n"
    "        var out_ = new System.Text.StringBuilder();\n"
    "        int i = 0, n = s.Length;\n"
    "        while (i < n) {\n"
    "            int j = i;\n"
    "            while (j < n && s[j] == s[i]) j++;\n"
    "            out_.Append(s[i]).Append(j - i);\n"
    "            i = j;\n"
    "        }\n"
    "        return out_.ToString();\n"
    "    }\n"
    "}\n")

reg("run-length-encoding", "c",
    "char* rle_encode(char* s) {\n"
    "    int n = (int)strlen(s);\n"
    "    char *out = (char *)malloc((size_t)n * 12 + 8);\n"
    "    int pos = 0, i = 0;\n"
    "    while (i < n) {\n"
    "        int j = i;\n"
    "        while (j < n && s[j] == s[i]) j++;\n"
    "        pos += sprintf(out + pos, \"%d\", j - i);\n"
    "        out[pos++] = s[i];\n"
    "        i = j;\n"
    "    }\n"
    "    out[pos] = '\\0';\n"
    "    return out;\n"
    "}\n",
    "char* rle_encode(char* s) {\n"
    "    int n = (int)strlen(s);\n"
    "    char *out = (char *)malloc((size_t)n * 12 + 8);\n"
    "    int pos = 0, i = 0;\n"
    "    while (i < n) {\n"
    "        int j = i;\n"
    "        while (j < n && s[j] == s[i]) j++;\n"
    "        out[pos++] = s[i];\n"
    "        pos += sprintf(out + pos, \"%d\", j - i);\n"
    "        i = j;\n"
    "    }\n"
    "    out[pos] = '\\0';\n"
    "    return out;\n"
    "}\n")

reg("run-length-encoding", "rust",
    "fn rle_encode(s: String) -> String {\n"
    "    let chars: Vec<char> = s.chars().collect();\n"
    "    let n = chars.len();\n"
    "    let mut out = String::new();\n"
    "    let mut i = 0;\n"
    "    while i < n {\n"
    "        let mut j = i;\n"
    "        while j < n && chars[j] == chars[i] { j += 1; }\n"
    "        out.push_str(&(j - i).to_string());\n"
    "        out.push(chars[i]);\n"
    "        i = j;\n"
    "    }\n"
    "    out\n"
    "}\n",
    "fn rle_encode(s: String) -> String {\n"
    "    let chars: Vec<char> = s.chars().collect();\n"
    "    let n = chars.len();\n"
    "    let mut out = String::new();\n"
    "    let mut i = 0;\n"
    "    while i < n {\n"
    "        let mut j = i;\n"
    "        while j < n && chars[j] == chars[i] { j += 1; }\n"
    "        out.push(chars[i]);\n"
    "        out.push_str(&(j - i).to_string());\n"
    "        i = j;\n"
    "    }\n"
    "    out\n"
    "}\n")


# ═════════════════════════════════════════════════════════════════════════
# sieve-of-eratosthenes -> sieve_of_eratosthenes(n) -> space-separated
# primes <= n.  wrong: starts the output loop at 1 (wrongly includes 1).
# ═════════════════════════════════════════════════════════════════════════

reg("sieve-of-eratosthenes", "javascript",
    "function sieve_of_eratosthenes(n) {\n"
    "    const isComposite = new Uint8Array(n + 1);\n"
    "    const out = [];\n"
    "    for (let i = 2; i <= n; i++) {\n"
    "        if (!isComposite[i]) {\n"
    "            out.push(i);\n"
    "            for (let j = i * 2; j <= n; j += i) isComposite[j] = 1;\n"
    "        }\n"
    "    }\n"
    "    return out.join(' ');\n"
    "}\n",
    "function sieve_of_eratosthenes(n) {\n"
    "    const isComposite = new Uint8Array(n + 1);\n"
    "    const out = [];\n"
    "    for (let i = 1; i <= n; i++) {\n"
    "        if (!isComposite[i]) {\n"
    "            out.push(i);\n"
    "            for (let j = i * 2; j <= n; j += i) isComposite[j] = 1;\n"
    "        }\n"
    "    }\n"
    "    return out.join(' ');\n"
    "}\n")

reg("sieve-of-eratosthenes", "typescript",
    "function sieve_of_eratosthenes(n: number): string {\n"
    "    const isComposite = new Uint8Array(n + 1);\n"
    "    const out: number[] = [];\n"
    "    for (let i = 2; i <= n; i++) {\n"
    "        if (!isComposite[i]) {\n"
    "            out.push(i);\n"
    "            for (let j = i * 2; j <= n; j += i) isComposite[j] = 1;\n"
    "        }\n"
    "    }\n"
    "    return out.join(' ');\n"
    "}\n",
    "function sieve_of_eratosthenes(n: number): string {\n"
    "    const isComposite = new Uint8Array(n + 1);\n"
    "    const out: number[] = [];\n"
    "    for (let i = 1; i <= n; i++) {\n"
    "        if (!isComposite[i]) {\n"
    "            out.push(i);\n"
    "            for (let j = i * 2; j <= n; j += i) isComposite[j] = 1;\n"
    "        }\n"
    "    }\n"
    "    return out.join(' ');\n"
    "}\n")

reg("sieve-of-eratosthenes", "perl",
    "sub sieve_of_eratosthenes {\n"
    "    my ($n) = @_;\n"
    "    my @is_composite = (0) x ($n + 1);\n"
    "    my @out = ();\n"
    "    for (my $i = 2; $i <= $n; $i++) {\n"
    "        if (!$is_composite[$i]) {\n"
    "            push @out, $i;\n"
    "            for (my $j = $i * 2; $j <= $n; $j += $i) { $is_composite[$j] = 1; }\n"
    "        }\n"
    "    }\n"
    "    return join(' ', @out);\n"
    "}\n",
    "sub sieve_of_eratosthenes {\n"
    "    my ($n) = @_;\n"
    "    my @is_composite = (0) x ($n + 1);\n"
    "    my @out = ();\n"
    "    for (my $i = 1; $i <= $n; $i++) {\n"
    "        if (!$is_composite[$i]) {\n"
    "            push @out, $i;\n"
    "            for (my $j = $i * 2; $j <= $n; $j += $i) { $is_composite[$j] = 1; }\n"
    "        }\n"
    "    }\n"
    "    return join(' ', @out);\n"
    "}\n")

reg("sieve-of-eratosthenes", "java",
    "class Solution {\n"
    "    public String sieve_of_eratosthenes(int n) {\n"
    "        boolean[] isComposite = new boolean[n + 1];\n"
    "        StringBuilder out = new StringBuilder();\n"
    "        boolean first = true;\n"
    "        for (int i = 2; i <= n; i++) {\n"
    "            if (!isComposite[i]) {\n"
    "                if (!first) out.append(' ');\n"
    "                out.append(i);\n"
    "                first = false;\n"
    "                for (long j = (long) i * 2; j <= n; j += i) isComposite[(int) j] = true;\n"
    "            }\n"
    "        }\n"
    "        return out.toString();\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public String sieve_of_eratosthenes(int n) {\n"
    "        boolean[] isComposite = new boolean[n + 1];\n"
    "        StringBuilder out = new StringBuilder();\n"
    "        boolean first = true;\n"
    "        for (int i = 1; i <= n; i++) {\n"
    "            if (!isComposite[i]) {\n"
    "                if (!first) out.append(' ');\n"
    "                out.append(i);\n"
    "                first = false;\n"
    "                for (long j = (long) i * 2; j <= n; j += i) isComposite[(int) j] = true;\n"
    "            }\n"
    "        }\n"
    "        return out.toString();\n"
    "    }\n"
    "}\n")

reg("sieve-of-eratosthenes", "cpp",
    "class Solution {\n"
    "public:\n"
    "    std::string sieve_of_eratosthenes(int n) {\n"
    "        std::vector<char> isComposite(n + 1, 0);\n"
    "        std::string out;\n"
    "        bool first = true;\n"
    "        for (int i = 2; i <= n; i++) {\n"
    "            if (!isComposite[i]) {\n"
    "                if (!first) out += ' ';\n"
    "                out += std::to_string(i);\n"
    "                first = false;\n"
    "                for (long long j = (long long) i * 2; j <= n; j += i) isComposite[j] = 1;\n"
    "            }\n"
    "        }\n"
    "        return out;\n"
    "    }\n"
    "};\n",
    "class Solution {\n"
    "public:\n"
    "    std::string sieve_of_eratosthenes(int n) {\n"
    "        std::vector<char> isComposite(n + 1, 0);\n"
    "        std::string out;\n"
    "        bool first = true;\n"
    "        for (int i = 1; i <= n; i++) {\n"
    "            if (!isComposite[i]) {\n"
    "                if (!first) out += ' ';\n"
    "                out += std::to_string(i);\n"
    "                first = false;\n"
    "                for (long long j = (long long) i * 2; j <= n; j += i) isComposite[j] = 1;\n"
    "            }\n"
    "        }\n"
    "        return out;\n"
    "    }\n"
    "};\n")

reg("sieve-of-eratosthenes", "csharp",
    "class Solution {\n"
    "    public static string sieve_of_eratosthenes(int n) {\n"
    "        var isComposite = new bool[n + 1];\n"
    "        var out_ = new System.Text.StringBuilder();\n"
    "        bool first = true;\n"
    "        for (int i = 2; i <= n; i++) {\n"
    "            if (!isComposite[i]) {\n"
    "                if (!first) out_.Append(' ');\n"
    "                out_.Append(i);\n"
    "                first = false;\n"
    "                for (long j = (long)i * 2; j <= n; j += i) isComposite[j] = true;\n"
    "            }\n"
    "        }\n"
    "        return out_.ToString();\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public static string sieve_of_eratosthenes(int n) {\n"
    "        var isComposite = new bool[n + 1];\n"
    "        var out_ = new System.Text.StringBuilder();\n"
    "        bool first = true;\n"
    "        for (int i = 1; i <= n; i++) {\n"
    "            if (!isComposite[i]) {\n"
    "                if (!first) out_.Append(' ');\n"
    "                out_.Append(i);\n"
    "                first = false;\n"
    "                for (long j = (long)i * 2; j <= n; j += i) isComposite[j] = true;\n"
    "            }\n"
    "        }\n"
    "        return out_.ToString();\n"
    "    }\n"
    "}\n")

reg("sieve-of-eratosthenes", "c",
    "char* sieve_of_eratosthenes(int n) {\n"
    "    char *isComposite = (char *)calloc((size_t)n + 1, 1);\n"
    "    char *out = (char *)malloc((size_t)n * 8 + 8);\n"
    "    int pos = 0;\n"
    "    int first = 1;\n"
    "    for (int i = 2; i <= n; i++) {\n"
    "        if (!isComposite[i]) {\n"
    "            if (!first) out[pos++] = ' ';\n"
    "            pos += sprintf(out + pos, \"%d\", i);\n"
    "            first = 0;\n"
    "            for (long j = (long) i * 2; j <= n; j += i) isComposite[j] = 1;\n"
    "        }\n"
    "    }\n"
    "    out[pos] = '\\0';\n"
    "    free(isComposite);\n"
    "    return out;\n"
    "}\n",
    "char* sieve_of_eratosthenes(int n) {\n"
    "    char *isComposite = (char *)calloc((size_t)n + 1, 1);\n"
    "    char *out = (char *)malloc((size_t)n * 8 + 8);\n"
    "    int pos = 0;\n"
    "    int first = 1;\n"
    "    for (int i = 1; i <= n; i++) {\n"
    "        if (!isComposite[i]) {\n"
    "            if (!first) out[pos++] = ' ';\n"
    "            pos += sprintf(out + pos, \"%d\", i);\n"
    "            first = 0;\n"
    "            for (long j = (long) i * 2; j <= n; j += i) isComposite[j] = 1;\n"
    "        }\n"
    "    }\n"
    "    out[pos] = '\\0';\n"
    "    free(isComposite);\n"
    "    return out;\n"
    "}\n")

reg("sieve-of-eratosthenes", "rust",
    "fn sieve_of_eratosthenes(n: i32) -> String {\n"
    "    let n = n as usize;\n"
    "    let mut is_composite = vec![false; n + 1];\n"
    "    let mut out: Vec<String> = Vec::new();\n"
    "    for i in 2..=n {\n"
    "        if !is_composite[i] {\n"
    "            out.push(i.to_string());\n"
    "            let mut j = i * 2;\n"
    "            while j <= n { is_composite[j] = true; j += i; }\n"
    "        }\n"
    "    }\n"
    "    out.join(\" \")\n"
    "}\n",
    "fn sieve_of_eratosthenes(n: i32) -> String {\n"
    "    let n = n as usize;\n"
    "    let mut is_composite = vec![false; n + 1];\n"
    "    let mut out: Vec<String> = Vec::new();\n"
    "    for i in 1..=n {\n"
    "        if !is_composite[i] {\n"
    "            out.push(i.to_string());\n"
    "            let mut j = i * 2;\n"
    "            while j <= n { is_composite[j] = true; j += i; }\n"
    "        }\n"
    "    }\n"
    "    out.join(\" \")\n"
    "}\n")


# ═════════════════════════════════════════════════════════════════════════
# string-hashing -> count_distinct_substrings(s, k) -> # of DISTINCT
# length-k substrings.  wrong: returns TOTAL (non-deduped) substring count.
# ═════════════════════════════════════════════════════════════════════════

reg("string-hashing", "javascript",
    "function count_distinct_substrings(s, k) {\n"
    "    const seen = new Set();\n"
    "    for (let i = 0; i + k <= s.length; i++) seen.add(s.substring(i, i + k));\n"
    "    return seen.size;\n"
    "}\n",
    "function count_distinct_substrings(s, k) {\n"
    "    let count = 0;\n"
    "    for (let i = 0; i + k <= s.length; i++) count++;\n"
    "    return count;\n"
    "}\n")

reg("string-hashing", "typescript",
    "function count_distinct_substrings(s: string, k: number): number {\n"
    "    const seen = new Set<string>();\n"
    "    for (let i = 0; i + k <= s.length; i++) seen.add(s.substring(i, i + k));\n"
    "    return seen.size;\n"
    "}\n",
    "function count_distinct_substrings(s: string, k: number): number {\n"
    "    let count = 0;\n"
    "    for (let i = 0; i + k <= s.length; i++) count++;\n"
    "    return count;\n"
    "}\n")

reg("string-hashing", "perl",
    "sub count_distinct_substrings {\n"
    "    my ($s, $k) = @_;\n"
    "    my %seen;\n"
    "    my $n = length($s);\n"
    "    for (my $i = 0; $i + $k <= $n; $i++) { $seen{substr($s, $i, $k)} = 1; }\n"
    "    return scalar(keys %seen);\n"
    "}\n",
    "sub count_distinct_substrings {\n"
    "    my ($s, $k) = @_;\n"
    "    my $n = length($s);\n"
    "    my $count = 0;\n"
    "    for (my $i = 0; $i + $k <= $n; $i++) { $count++; }\n"
    "    return $count;\n"
    "}\n")

reg("string-hashing", "java",
    "class Solution {\n"
    "    public int count_distinct_substrings(String s, int k) {\n"
    "        java.util.Set<String> seen = new java.util.HashSet<>();\n"
    "        for (int i = 0; i + k <= s.length(); i++) seen.add(s.substring(i, i + k));\n"
    "        return seen.size();\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public int count_distinct_substrings(String s, int k) {\n"
    "        int count = 0;\n"
    "        for (int i = 0; i + k <= s.length(); i++) count++;\n"
    "        return count;\n"
    "    }\n"
    "}\n")

reg("string-hashing", "cpp",
    "class Solution {\n"
    "public:\n"
    "    int count_distinct_substrings(std::string s, int k) {\n"
    "        std::unordered_set<std::string> seen;\n"
    "        for (int i = 0; i + k <= (int) s.size(); i++) seen.insert(s.substr(i, k));\n"
    "        return (int) seen.size();\n"
    "    }\n"
    "};\n",
    "class Solution {\n"
    "public:\n"
    "    int count_distinct_substrings(std::string s, int k) {\n"
    "        int count = 0;\n"
    "        for (int i = 0; i + k <= (int) s.size(); i++) count++;\n"
    "        return count;\n"
    "    }\n"
    "};\n")

reg("string-hashing", "csharp",
    "class Solution {\n"
    "    public static int count_distinct_substrings(string s, int k) {\n"
    "        var seen = new System.Collections.Generic.HashSet<string>();\n"
    "        for (int i = 0; i + k <= s.Length; i++) seen.Add(s.Substring(i, k));\n"
    "        return seen.Count;\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public static int count_distinct_substrings(string s, int k) {\n"
    "        int count = 0;\n"
    "        for (int i = 0; i + k <= s.Length; i++) count++;\n"
    "        return count;\n"
    "    }\n"
    "}\n")

reg("string-hashing", "c",
    "int count_distinct_substrings(char* s, int k) {\n"
    "    int n = (int)strlen(s);\n"
    "    int total = n - k + 1;\n"
    "    if (total <= 0) return 0;\n"
    "    char **subs = (char **)malloc(sizeof(char *) * total);\n"
    "    for (int i = 0; i < total; i++) subs[i] = s + i;\n"
    "    for (int i = 0; i < total; i++) {\n"
    "        for (int j = i + 1; j < total; j++) {\n"
    "            if (strncmp(subs[i], subs[j], (size_t) k) > 0) {\n"
    "                char *t = subs[i]; subs[i] = subs[j]; subs[j] = t;\n"
    "            }\n"
    "        }\n"
    "    }\n"
    "    int distinct = total > 0 ? 1 : 0;\n"
    "    for (int i = 1; i < total; i++) {\n"
    "        if (strncmp(subs[i], subs[i - 1], (size_t) k) != 0) distinct++;\n"
    "    }\n"
    "    free(subs);\n"
    "    return distinct;\n"
    "}\n",
    "int count_distinct_substrings(char* s, int k) {\n"
    "    int n = (int)strlen(s);\n"
    "    int total = n - k + 1;\n"
    "    if (total <= 0) return 0;\n"
    "    return total;\n"
    "}\n")

reg("string-hashing", "rust",
    "fn count_distinct_substrings(s: String, k: i32) -> i32 {\n"
    "    let chars: Vec<char> = s.chars().collect();\n"
    "    let n = chars.len() as i32;\n"
    "    let mut seen = std::collections::HashSet::new();\n"
    "    let mut i = 0;\n"
    "    while i + k <= n {\n"
    "        let sub: String = chars[i as usize..(i + k) as usize].iter().collect();\n"
    "        seen.insert(sub);\n"
    "        i += 1;\n"
    "    }\n"
    "    seen.len() as i32\n"
    "}\n",
    "fn count_distinct_substrings(s: String, k: i32) -> i32 {\n"
    "    let chars: Vec<char> = s.chars().collect();\n"
    "    let n = chars.len() as i32;\n"
    "    let mut count = 0;\n"
    "    let mut i = 0;\n"
    "    while i + k <= n { count += 1; i += 1; }\n"
    "    count\n"
    "}\n")


# ═════════════════════════════════════════════════════════════════════════
# z-algorithm -> z_function(s) -> array<int>, z[0] = 0 by this contract's
# convention.  wrong: reverses the output array.
# ═════════════════════════════════════════════════════════════════════════

reg("z-algorithm", "javascript",
    "function z_function(s) {\n"
    "    const n = s.length;\n"
    "    const z = new Array(n).fill(0);\n"
    "    let l = 0, r = 0;\n"
    "    for (let i = 1; i < n; i++) {\n"
    "        if (i < r) z[i] = Math.min(r - i, z[i - l]);\n"
    "        while (i + z[i] < n && s[z[i]] === s[i + z[i]]) z[i]++;\n"
    "        if (i + z[i] > r) { l = i; r = i + z[i]; }\n"
    "    }\n"
    "    return z;\n"
    "}\n",
    "function z_function(s) {\n"
    "    const n = s.length;\n"
    "    const z = new Array(n).fill(0);\n"
    "    let l = 0, r = 0;\n"
    "    for (let i = 1; i < n; i++) {\n"
    "        if (i < r) z[i] = Math.min(r - i, z[i - l]);\n"
    "        while (i + z[i] < n && s[z[i]] === s[i + z[i]]) z[i]++;\n"
    "        if (i + z[i] > r) { l = i; r = i + z[i]; }\n"
    "    }\n"
    "    return z.slice().reverse();\n"
    "}\n")

reg("z-algorithm", "typescript",
    "function z_function(s: string): number[] {\n"
    "    const n = s.length;\n"
    "    const z: number[] = new Array(n).fill(0);\n"
    "    let l = 0, r = 0;\n"
    "    for (let i = 1; i < n; i++) {\n"
    "        if (i < r) z[i] = Math.min(r - i, z[i - l]);\n"
    "        while (i + z[i] < n && s[z[i]] === s[i + z[i]]) z[i]++;\n"
    "        if (i + z[i] > r) { l = i; r = i + z[i]; }\n"
    "    }\n"
    "    return z;\n"
    "}\n",
    "function z_function(s: string): number[] {\n"
    "    const n = s.length;\n"
    "    const z: number[] = new Array(n).fill(0);\n"
    "    let l = 0, r = 0;\n"
    "    for (let i = 1; i < n; i++) {\n"
    "        if (i < r) z[i] = Math.min(r - i, z[i - l]);\n"
    "        while (i + z[i] < n && s[z[i]] === s[i + z[i]]) z[i]++;\n"
    "        if (i + z[i] > r) { l = i; r = i + z[i]; }\n"
    "    }\n"
    "    return z.slice().reverse();\n"
    "}\n")

reg("z-algorithm", "perl",
    "sub z_function {\n"
    "    my ($s) = @_;\n"
    "    my @chars = split //, $s;\n"
    "    my $n = scalar(@chars);\n"
    "    my @z = (0) x $n;\n"
    "    my ($l, $r) = (0, 0);\n"
    "    for (my $i = 1; $i < $n; $i++) {\n"
    "        if ($i < $r) { my $v = $r - $i; my $w = $z[$i - $l]; $z[$i] = $v < $w ? $v : $w; }\n"
    "        while ($i + $z[$i] < $n && $chars[$z[$i]] eq $chars[$i + $z[$i]]) { $z[$i]++; }\n"
    "        if ($i + $z[$i] > $r) { $l = $i; $r = $i + $z[$i]; }\n"
    "    }\n"
    "    return \\@z;\n"
    "}\n",
    "sub z_function {\n"
    "    my ($s) = @_;\n"
    "    my @chars = split //, $s;\n"
    "    my $n = scalar(@chars);\n"
    "    my @z = (0) x $n;\n"
    "    my ($l, $r) = (0, 0);\n"
    "    for (my $i = 1; $i < $n; $i++) {\n"
    "        if ($i < $r) { my $v = $r - $i; my $w = $z[$i - $l]; $z[$i] = $v < $w ? $v : $w; }\n"
    "        while ($i + $z[$i] < $n && $chars[$z[$i]] eq $chars[$i + $z[$i]]) { $z[$i]++; }\n"
    "        if ($i + $z[$i] > $r) { $l = $i; $r = $i + $z[$i]; }\n"
    "    }\n"
    "    return [reverse @z];\n"
    "}\n")

reg("z-algorithm", "java",
    "class Solution {\n"
    "    public int[] z_function(String s) {\n"
    "        int n = s.length();\n"
    "        int[] z = new int[n];\n"
    "        int l = 0, r = 0;\n"
    "        for (int i = 1; i < n; i++) {\n"
    "            if (i < r) z[i] = Math.min(r - i, z[i - l]);\n"
    "            while (i + z[i] < n && s.charAt(z[i]) == s.charAt(i + z[i])) z[i]++;\n"
    "            if (i + z[i] > r) { l = i; r = i + z[i]; }\n"
    "        }\n"
    "        return z;\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public int[] z_function(String s) {\n"
    "        int n = s.length();\n"
    "        int[] z = new int[n];\n"
    "        int l = 0, r = 0;\n"
    "        for (int i = 1; i < n; i++) {\n"
    "            if (i < r) z[i] = Math.min(r - i, z[i - l]);\n"
    "            while (i + z[i] < n && s.charAt(z[i]) == s.charAt(i + z[i])) z[i]++;\n"
    "            if (i + z[i] > r) { l = i; r = i + z[i]; }\n"
    "        }\n"
    "        int[] rev = new int[n];\n"
    "        for (int i = 0; i < n; i++) rev[i] = z[n - 1 - i];\n"
    "        return rev;\n"
    "    }\n"
    "}\n")

reg("z-algorithm", "cpp",
    "class Solution {\n"
    "public:\n"
    "    std::vector<int> z_function(std::string s) {\n"
    "        int n = (int) s.size();\n"
    "        std::vector<int> z(n, 0);\n"
    "        int l = 0, r = 0;\n"
    "        for (int i = 1; i < n; i++) {\n"
    "            if (i < r) z[i] = std::min(r - i, z[i - l]);\n"
    "            while (i + z[i] < n && s[z[i]] == s[i + z[i]]) z[i]++;\n"
    "            if (i + z[i] > r) { l = i; r = i + z[i]; }\n"
    "        }\n"
    "        return z;\n"
    "    }\n"
    "};\n",
    "class Solution {\n"
    "public:\n"
    "    std::vector<int> z_function(std::string s) {\n"
    "        int n = (int) s.size();\n"
    "        std::vector<int> z(n, 0);\n"
    "        int l = 0, r = 0;\n"
    "        for (int i = 1; i < n; i++) {\n"
    "            if (i < r) z[i] = std::min(r - i, z[i - l]);\n"
    "            while (i + z[i] < n && s[z[i]] == s[i + z[i]]) z[i]++;\n"
    "            if (i + z[i] > r) { l = i; r = i + z[i]; }\n"
    "        }\n"
    "        std::reverse(z.begin(), z.end());\n"
    "        return z;\n"
    "    }\n"
    "};\n")

reg("z-algorithm", "csharp",
    "class Solution {\n"
    "    public static int[] z_function(string s) {\n"
    "        int n = s.Length;\n"
    "        var z = new int[n];\n"
    "        int l = 0, r = 0;\n"
    "        for (int i = 1; i < n; i++) {\n"
    "            if (i < r) z[i] = System.Math.Min(r - i, z[i - l]);\n"
    "            while (i + z[i] < n && s[z[i]] == s[i + z[i]]) z[i]++;\n"
    "            if (i + z[i] > r) { l = i; r = i + z[i]; }\n"
    "        }\n"
    "        return z;\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public static int[] z_function(string s) {\n"
    "        int n = s.Length;\n"
    "        var z = new int[n];\n"
    "        int l = 0, r = 0;\n"
    "        for (int i = 1; i < n; i++) {\n"
    "            if (i < r) z[i] = System.Math.Min(r - i, z[i - l]);\n"
    "            while (i + z[i] < n && s[z[i]] == s[i + z[i]]) z[i]++;\n"
    "            if (i + z[i] > r) { l = i; r = i + z[i]; }\n"
    "        }\n"
    "        System.Array.Reverse(z);\n"
    "        return z;\n"
    "    }\n"
    "}\n")

reg("z-algorithm", "c",
    "AtlasIntArray z_function(char* s) {\n"
    "    int n = (int)strlen(s);\n"
    "    int *z = (int *)calloc((size_t)(n ? n : 1), sizeof(int));\n"
    "    int l = 0, r = 0;\n"
    "    for (int i = 1; i < n; i++) {\n"
    "        if (i < r) { int v = r - i, w = z[i - l]; z[i] = v < w ? v : w; }\n"
    "        while (i + z[i] < n && s[z[i]] == s[i + z[i]]) z[i]++;\n"
    "        if (i + z[i] > r) { l = i; r = i + z[i]; }\n"
    "    }\n"
    "    AtlasIntArray out; out.data = z; out.size = n;\n"
    "    return out;\n"
    "}\n",
    "AtlasIntArray z_function(char* s) {\n"
    "    int n = (int)strlen(s);\n"
    "    int *z = (int *)calloc((size_t)(n ? n : 1), sizeof(int));\n"
    "    int l = 0, r = 0;\n"
    "    for (int i = 1; i < n; i++) {\n"
    "        if (i < r) { int v = r - i, w = z[i - l]; z[i] = v < w ? v : w; }\n"
    "        while (i + z[i] < n && s[z[i]] == s[i + z[i]]) z[i]++;\n"
    "        if (i + z[i] > r) { l = i; r = i + z[i]; }\n"
    "    }\n"
    "    int *rev = (int *)malloc(sizeof(int) * (size_t)(n ? n : 1));\n"
    "    for (int i = 0; i < n; i++) rev[i] = z[n - 1 - i];\n"
    "    free(z);\n"
    "    AtlasIntArray out; out.data = rev; out.size = n;\n"
    "    return out;\n"
    "}\n")

reg("z-algorithm", "rust",
    "fn z_function(s: String) -> Vec<i32> {\n"
    "    let chars: Vec<char> = s.chars().collect();\n"
    "    let n = chars.len();\n"
    "    let mut z = vec![0i32; n];\n"
    "    let (mut l, mut r) = (0usize, 0usize);\n"
    "    for i in 1..n {\n"
    "        if i < r { z[i] = std::cmp::min((r - i) as i32, z[i - l]); }\n"
    "        while (i as i32 + z[i]) < n as i32\n"
    "            && chars[z[i] as usize] == chars[i + z[i] as usize] {\n"
    "            z[i] += 1;\n"
    "        }\n"
    "        if i as i32 + z[i] > r as i32 { l = i; r = i + z[i] as usize; }\n"
    "    }\n"
    "    z\n"
    "}\n",
    "fn z_function(s: String) -> Vec<i32> {\n"
    "    let chars: Vec<char> = s.chars().collect();\n"
    "    let n = chars.len();\n"
    "    let mut z = vec![0i32; n];\n"
    "    let (mut l, mut r) = (0usize, 0usize);\n"
    "    for i in 1..n {\n"
    "        if i < r { z[i] = std::cmp::min((r - i) as i32, z[i - l]); }\n"
    "        while (i as i32 + z[i]) < n as i32\n"
    "            && chars[z[i] as usize] == chars[i + z[i] as usize] {\n"
    "            z[i] += 1;\n"
    "        }\n"
    "        if i as i32 + z[i] > r as i32 { l = i; r = i + z[i] as usize; }\n"
    "    }\n"
    "    z.reverse();\n"
    "    z\n"
    "}\n")


# ═════════════════════════════════════════════════════════════════════════
# distinct-subsets-count -> count_distinct_subsets(nums) -> product of
# (multiplicity + 1) over distinct values.  wrong: product of multiplicity
# alone (no +1).
# ═════════════════════════════════════════════════════════════════════════

reg("distinct-subsets-count", "javascript",
    "function count_distinct_subsets(nums) {\n"
    "    const counts = new Map();\n"
    "    for (const x of nums) counts.set(x, (counts.get(x) || 0) + 1);\n"
    "    let result = 1;\n"
    "    for (const c of counts.values()) result *= (c + 1);\n"
    "    return result;\n"
    "}\n",
    "function count_distinct_subsets(nums) {\n"
    "    const counts = new Map();\n"
    "    for (const x of nums) counts.set(x, (counts.get(x) || 0) + 1);\n"
    "    let result = 1;\n"
    "    for (const c of counts.values()) result *= c;\n"
    "    return result;\n"
    "}\n")

reg("distinct-subsets-count", "typescript",
    "function count_distinct_subsets(nums: number[]): number {\n"
    "    const counts = new Map<number, number>();\n"
    "    for (const x of nums) counts.set(x, (counts.get(x) || 0) + 1);\n"
    "    let result = 1;\n"
    "    for (const c of counts.values()) result *= (c + 1);\n"
    "    return result;\n"
    "}\n",
    "function count_distinct_subsets(nums: number[]): number {\n"
    "    const counts = new Map<number, number>();\n"
    "    for (const x of nums) counts.set(x, (counts.get(x) || 0) + 1);\n"
    "    let result = 1;\n"
    "    for (const c of counts.values()) result *= c;\n"
    "    return result;\n"
    "}\n")

reg("distinct-subsets-count", "perl",
    "sub count_distinct_subsets {\n"
    "    my ($nums) = @_;\n"
    "    my %counts;\n"
    "    foreach my $x (@{$nums}) { $counts{$x}++; }\n"
    "    my $result = 1;\n"
    "    foreach my $c (values %counts) { $result *= ($c + 1); }\n"
    "    return $result;\n"
    "}\n",
    "sub count_distinct_subsets {\n"
    "    my ($nums) = @_;\n"
    "    my %counts;\n"
    "    foreach my $x (@{$nums}) { $counts{$x}++; }\n"
    "    my $result = 1;\n"
    "    foreach my $c (values %counts) { $result *= $c; }\n"
    "    return $result;\n"
    "}\n")

reg("distinct-subsets-count", "java",
    "class Solution {\n"
    "    public int count_distinct_subsets(int[] nums) {\n"
    "        java.util.Map<Integer, Integer> counts = new java.util.HashMap<>();\n"
    "        for (int x : nums) counts.merge(x, 1, Integer::sum);\n"
    "        int result = 1;\n"
    "        for (int c : counts.values()) result *= (c + 1);\n"
    "        return result;\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public int count_distinct_subsets(int[] nums) {\n"
    "        java.util.Map<Integer, Integer> counts = new java.util.HashMap<>();\n"
    "        for (int x : nums) counts.merge(x, 1, Integer::sum);\n"
    "        int result = 1;\n"
    "        for (int c : counts.values()) result *= c;\n"
    "        return result;\n"
    "    }\n"
    "}\n")

reg("distinct-subsets-count", "cpp",
    "class Solution {\n"
    "public:\n"
    "    int count_distinct_subsets(std::vector<int> nums) {\n"
    "        std::unordered_map<int, int> counts;\n"
    "        for (int x : nums) counts[x]++;\n"
    "        long long result = 1;\n"
    "        for (auto &p : counts) result *= (p.second + 1);\n"
    "        return (int) result;\n"
    "    }\n"
    "};\n",
    "class Solution {\n"
    "public:\n"
    "    int count_distinct_subsets(std::vector<int> nums) {\n"
    "        std::unordered_map<int, int> counts;\n"
    "        for (int x : nums) counts[x]++;\n"
    "        long long result = 1;\n"
    "        for (auto &p : counts) result *= p.second;\n"
    "        return (int) result;\n"
    "    }\n"
    "};\n")

reg("distinct-subsets-count", "csharp",
    "class Solution {\n"
    "    public static int count_distinct_subsets(int[] nums) {\n"
    "        var counts = new System.Collections.Generic.Dictionary<int, int>();\n"
    "        foreach (var x in nums) { counts[x] = counts.ContainsKey(x) ? counts[x] + 1 : 1; }\n"
    "        long result = 1;\n"
    "        foreach (var c in counts.Values) result *= (c + 1);\n"
    "        return (int) result;\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public static int count_distinct_subsets(int[] nums) {\n"
    "        var counts = new System.Collections.Generic.Dictionary<int, int>();\n"
    "        foreach (var x in nums) { counts[x] = counts.ContainsKey(x) ? counts[x] + 1 : 1; }\n"
    "        long result = 1;\n"
    "        foreach (var c in counts.Values) result *= c;\n"
    "        return (int) result;\n"
    "    }\n"
    "}\n")

reg("distinct-subsets-count", "c",
    "int count_distinct_subsets(AtlasIntArray nums) {\n"
    "    int n = nums.size;\n"
    "    int *vals = (int *)malloc(sizeof(int) * (n ? n : 1));\n"
    "    int *cnts = (int *)malloc(sizeof(int) * (n ? n : 1));\n"
    "    int m = 0;\n"
    "    for (int i = 0; i < n; i++) {\n"
    "        int x = nums.data[i];\n"
    "        int found = 0;\n"
    "        for (int j = 0; j < m; j++) { if (vals[j] == x) { cnts[j]++; found = 1; break; } }\n"
    "        if (!found) { vals[m] = x; cnts[m] = 1; m++; }\n"
    "    }\n"
    "    long long result = 1;\n"
    "    for (int j = 0; j < m; j++) result *= (cnts[j] + 1);\n"
    "    free(vals); free(cnts);\n"
    "    return (int) result;\n"
    "}\n",
    "int count_distinct_subsets(AtlasIntArray nums) {\n"
    "    int n = nums.size;\n"
    "    int *vals = (int *)malloc(sizeof(int) * (n ? n : 1));\n"
    "    int *cnts = (int *)malloc(sizeof(int) * (n ? n : 1));\n"
    "    int m = 0;\n"
    "    for (int i = 0; i < n; i++) {\n"
    "        int x = nums.data[i];\n"
    "        int found = 0;\n"
    "        for (int j = 0; j < m; j++) { if (vals[j] == x) { cnts[j]++; found = 1; break; } }\n"
    "        if (!found) { vals[m] = x; cnts[m] = 1; m++; }\n"
    "    }\n"
    "    long long result = 1;\n"
    "    for (int j = 0; j < m; j++) result *= cnts[j];\n"
    "    free(vals); free(cnts);\n"
    "    return (int) result;\n"
    "}\n")

reg("distinct-subsets-count", "rust",
    "fn count_distinct_subsets(nums: Vec<i32>) -> i32 {\n"
    "    let mut counts = std::collections::HashMap::new();\n"
    "    for x in nums { *counts.entry(x).or_insert(0) += 1; }\n"
    "    let mut result: i64 = 1;\n"
    "    for c in counts.values() { result *= (*c as i64 + 1); }\n"
    "    result as i32\n"
    "}\n",
    "fn count_distinct_subsets(nums: Vec<i32>) -> i32 {\n"
    "    let mut counts = std::collections::HashMap::new();\n"
    "    for x in nums { *counts.entry(x).or_insert(0) += 1; }\n"
    "    let mut result: i64 = 1;\n"
    "    for c in counts.values() { result *= *c as i64; }\n"
    "    result as i32\n"
    "}\n")


# ═════════════════════════════════════════════════════════════════════════
# rotate-image-90 -> rotate(matrix) -> new matrix rotated 90 CW.
# wrong: rotates counter-clockwise instead.
# ═════════════════════════════════════════════════════════════════════════

reg("rotate-image-90", "javascript",
    "function rotate(matrix) {\n"
    "    const n = matrix.length;\n"
    "    const out = Array.from({ length: n }, () => new Array(n).fill(0));\n"
    "    for (let i = 0; i < n; i++)\n"
    "        for (let j = 0; j < n; j++)\n"
    "            out[i][j] = matrix[n - 1 - j][i];\n"
    "    return out;\n"
    "}\n",
    "function rotate(matrix) {\n"
    "    const n = matrix.length;\n"
    "    const out = Array.from({ length: n }, () => new Array(n).fill(0));\n"
    "    for (let i = 0; i < n; i++)\n"
    "        for (let j = 0; j < n; j++)\n"
    "            out[i][j] = matrix[j][n - 1 - i];\n"
    "    return out;\n"
    "}\n")

reg("rotate-image-90", "typescript",
    "function rotate(matrix: number[][]): number[][] {\n"
    "    const n = matrix.length;\n"
    "    const out: number[][] = Array.from({ length: n }, () => new Array(n).fill(0));\n"
    "    for (let i = 0; i < n; i++)\n"
    "        for (let j = 0; j < n; j++)\n"
    "            out[i][j] = matrix[n - 1 - j][i];\n"
    "    return out;\n"
    "}\n",
    "function rotate(matrix: number[][]): number[][] {\n"
    "    const n = matrix.length;\n"
    "    const out: number[][] = Array.from({ length: n }, () => new Array(n).fill(0));\n"
    "    for (let i = 0; i < n; i++)\n"
    "        for (let j = 0; j < n; j++)\n"
    "            out[i][j] = matrix[j][n - 1 - i];\n"
    "    return out;\n"
    "}\n")

reg("rotate-image-90", "perl",
    "sub rotate {\n"
    "    my ($matrix) = @_;\n"
    "    my $n = scalar(@{$matrix});\n"
    "    my @out;\n"
    "    for (my $i = 0; $i < $n; $i++) {\n"
    "        for (my $j = 0; $j < $n; $j++) {\n"
    "            $out[$i][$j] = $matrix->[$n - 1 - $j][$i];\n"
    "        }\n"
    "    }\n"
    "    return \\@out;\n"
    "}\n",
    "sub rotate {\n"
    "    my ($matrix) = @_;\n"
    "    my $n = scalar(@{$matrix});\n"
    "    my @out;\n"
    "    for (my $i = 0; $i < $n; $i++) {\n"
    "        for (my $j = 0; $j < $n; $j++) {\n"
    "            $out[$i][$j] = $matrix->[$j][$n - 1 - $i];\n"
    "        }\n"
    "    }\n"
    "    return \\@out;\n"
    "}\n")

reg("rotate-image-90", "java",
    "class Solution {\n"
    "    public int[][] rotate(int[][] matrix) {\n"
    "        int n = matrix.length;\n"
    "        int[][] out = new int[n][n];\n"
    "        for (int i = 0; i < n; i++)\n"
    "            for (int j = 0; j < n; j++)\n"
    "                out[i][j] = matrix[n - 1 - j][i];\n"
    "        return out;\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public int[][] rotate(int[][] matrix) {\n"
    "        int n = matrix.length;\n"
    "        int[][] out = new int[n][n];\n"
    "        for (int i = 0; i < n; i++)\n"
    "            for (int j = 0; j < n; j++)\n"
    "                out[i][j] = matrix[j][n - 1 - i];\n"
    "        return out;\n"
    "    }\n"
    "}\n")

reg("rotate-image-90", "cpp",
    "class Solution {\n"
    "public:\n"
    "    std::vector<std::vector<int>> rotate(std::vector<std::vector<int>> matrix) {\n"
    "        int n = (int) matrix.size();\n"
    "        std::vector<std::vector<int>> out(n, std::vector<int>(n, 0));\n"
    "        for (int i = 0; i < n; i++)\n"
    "            for (int j = 0; j < n; j++)\n"
    "                out[i][j] = matrix[n - 1 - j][i];\n"
    "        return out;\n"
    "    }\n"
    "};\n",
    "class Solution {\n"
    "public:\n"
    "    std::vector<std::vector<int>> rotate(std::vector<std::vector<int>> matrix) {\n"
    "        int n = (int) matrix.size();\n"
    "        std::vector<std::vector<int>> out(n, std::vector<int>(n, 0));\n"
    "        for (int i = 0; i < n; i++)\n"
    "            for (int j = 0; j < n; j++)\n"
    "                out[i][j] = matrix[j][n - 1 - i];\n"
    "        return out;\n"
    "    }\n"
    "};\n")

reg("rotate-image-90", "csharp",
    "class Solution {\n"
    "    public static int[][] rotate(int[][] matrix) {\n"
    "        int n = matrix.Length;\n"
    "        var out_ = new int[n][];\n"
    "        for (int i = 0; i < n; i++) out_[i] = new int[n];\n"
    "        for (int i = 0; i < n; i++)\n"
    "            for (int j = 0; j < n; j++)\n"
    "                out_[i][j] = matrix[n - 1 - j][i];\n"
    "        return out_;\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public static int[][] rotate(int[][] matrix) {\n"
    "        int n = matrix.Length;\n"
    "        var out_ = new int[n][];\n"
    "        for (int i = 0; i < n; i++) out_[i] = new int[n];\n"
    "        for (int i = 0; i < n; i++)\n"
    "            for (int j = 0; j < n; j++)\n"
    "                out_[i][j] = matrix[j][n - 1 - i];\n"
    "        return out_;\n"
    "    }\n"
    "}\n")

reg("rotate-image-90", "c",
    "AtlasIntMatrix rotate(AtlasIntMatrix matrix) {\n"
    "    int n = matrix.size;\n"
    "    AtlasIntMatrix out;\n"
    "    out.size = n;\n"
    "    out.data = (AtlasIntArray *)malloc(sizeof(AtlasIntArray) * (n ? n : 1));\n"
    "    for (int i = 0; i < n; i++) {\n"
    "        out.data[i].size = n;\n"
    "        out.data[i].data = (int *)malloc(sizeof(int) * (n ? n : 1));\n"
    "        for (int j = 0; j < n; j++)\n"
    "            out.data[i].data[j] = matrix.data[n - 1 - j].data[i];\n"
    "    }\n"
    "    return out;\n"
    "}\n",
    "AtlasIntMatrix rotate(AtlasIntMatrix matrix) {\n"
    "    int n = matrix.size;\n"
    "    AtlasIntMatrix out;\n"
    "    out.size = n;\n"
    "    out.data = (AtlasIntArray *)malloc(sizeof(AtlasIntArray) * (n ? n : 1));\n"
    "    for (int i = 0; i < n; i++) {\n"
    "        out.data[i].size = n;\n"
    "        out.data[i].data = (int *)malloc(sizeof(int) * (n ? n : 1));\n"
    "        for (int j = 0; j < n; j++)\n"
    "            out.data[i].data[j] = matrix.data[j].data[n - 1 - i];\n"
    "    }\n"
    "    return out;\n"
    "}\n")

reg("rotate-image-90", "rust",
    "fn rotate(matrix: Vec<Vec<i32>>) -> Vec<Vec<i32>> {\n"
    "    let n = matrix.len();\n"
    "    let mut out = vec![vec![0i32; n]; n];\n"
    "    for i in 0..n {\n"
    "        for j in 0..n {\n"
    "            out[i][j] = matrix[n - 1 - j][i];\n"
    "        }\n"
    "    }\n"
    "    out\n"
    "}\n",
    "fn rotate(matrix: Vec<Vec<i32>>) -> Vec<Vec<i32>> {\n"
    "    let n = matrix.len();\n"
    "    let mut out = vec![vec![0i32; n]; n];\n"
    "    for i in 0..n {\n"
    "        for j in 0..n {\n"
    "            out[i][j] = matrix[j][n - 1 - i];\n"
    "        }\n"
    "    }\n"
    "    out\n"
    "}\n")


# ═════════════════════════════════════════════════════════════════════════
# search-2d-matrix -> search_matrix(matrix, target) -> bool.  wrong:
# always returns false (guaranteed rejected as long as >=1 hidden true case
# exists, which the visible corpus already confirms).
# ═════════════════════════════════════════════════════════════════════════

reg("search-2d-matrix", "javascript",
    "function search_matrix(matrix, target) {\n"
    "    const rows = matrix.length;\n"
    "    if (rows === 0) return false;\n"
    "    const cols = matrix[0].length;\n"
    "    let lo = 0, hi = rows * cols - 1;\n"
    "    while (lo <= hi) {\n"
    "        const mid = (lo + hi) >> 1;\n"
    "        const v = matrix[Math.floor(mid / cols)][mid % cols];\n"
    "        if (v === target) return true;\n"
    "        if (v < target) lo = mid + 1; else hi = mid - 1;\n"
    "    }\n"
    "    return false;\n"
    "}\n",
    "function search_matrix(matrix, target) {\n"
    "    return false;\n"
    "}\n")

reg("search-2d-matrix", "typescript",
    "function search_matrix(matrix: number[][], target: number): boolean {\n"
    "    const rows = matrix.length;\n"
    "    if (rows === 0) return false;\n"
    "    const cols = matrix[0].length;\n"
    "    let lo = 0, hi = rows * cols - 1;\n"
    "    while (lo <= hi) {\n"
    "        const mid = (lo + hi) >> 1;\n"
    "        const v = matrix[Math.floor(mid / cols)][mid % cols];\n"
    "        if (v === target) return true;\n"
    "        if (v < target) lo = mid + 1; else hi = mid - 1;\n"
    "    }\n"
    "    return false;\n"
    "}\n",
    "function search_matrix(matrix: number[][], target: number): boolean {\n"
    "    return false;\n"
    "}\n")

reg("search-2d-matrix", "perl",
    "sub search_matrix {\n"
    "    my ($matrix, $target) = @_;\n"
    "    my $rows = scalar(@{$matrix});\n"
    "    return 0 if $rows == 0;\n"
    "    my $cols = scalar(@{$matrix->[0]});\n"
    "    my ($lo, $hi) = (0, $rows * $cols - 1);\n"
    "    while ($lo <= $hi) {\n"
    "        my $mid = int(($lo + $hi) / 2);\n"
    "        my $v = $matrix->[int($mid / $cols)][$mid % $cols];\n"
    "        if ($v == $target) { return 1; }\n"
    "        if ($v < $target) { $lo = $mid + 1; } else { $hi = $mid - 1; }\n"
    "    }\n"
    "    return 0;\n"
    "}\n",
    "sub search_matrix {\n"
    "    my ($matrix, $target) = @_;\n"
    "    return 0;\n"
    "}\n")

reg("search-2d-matrix", "java",
    "class Solution {\n"
    "    public boolean search_matrix(int[][] matrix, int target) {\n"
    "        int rows = matrix.length;\n"
    "        if (rows == 0) return false;\n"
    "        int cols = matrix[0].length;\n"
    "        int lo = 0, hi = rows * cols - 1;\n"
    "        while (lo <= hi) {\n"
    "            int mid = (lo + hi) / 2;\n"
    "            int v = matrix[mid / cols][mid % cols];\n"
    "            if (v == target) return true;\n"
    "            if (v < target) lo = mid + 1; else hi = mid - 1;\n"
    "        }\n"
    "        return false;\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public boolean search_matrix(int[][] matrix, int target) {\n"
    "        return false;\n"
    "    }\n"
    "}\n")

reg("search-2d-matrix", "cpp",
    "class Solution {\n"
    "public:\n"
    "    bool search_matrix(std::vector<std::vector<int>> matrix, int target) {\n"
    "        int rows = (int) matrix.size();\n"
    "        if (rows == 0) return false;\n"
    "        int cols = (int) matrix[0].size();\n"
    "        int lo = 0, hi = rows * cols - 1;\n"
    "        while (lo <= hi) {\n"
    "            int mid = (lo + hi) / 2;\n"
    "            int v = matrix[mid / cols][mid % cols];\n"
    "            if (v == target) return true;\n"
    "            if (v < target) lo = mid + 1; else hi = mid - 1;\n"
    "        }\n"
    "        return false;\n"
    "    }\n"
    "};\n",
    "class Solution {\n"
    "public:\n"
    "    bool search_matrix(std::vector<std::vector<int>> matrix, int target) {\n"
    "        return false;\n"
    "    }\n"
    "};\n")

reg("search-2d-matrix", "csharp",
    "class Solution {\n"
    "    public static bool search_matrix(int[][] matrix, int target) {\n"
    "        int rows = matrix.Length;\n"
    "        if (rows == 0) return false;\n"
    "        int cols = matrix[0].Length;\n"
    "        int lo = 0, hi = rows * cols - 1;\n"
    "        while (lo <= hi) {\n"
    "            int mid = (lo + hi) / 2;\n"
    "            int v = matrix[mid / cols][mid % cols];\n"
    "            if (v == target) return true;\n"
    "            if (v < target) lo = mid + 1; else hi = mid - 1;\n"
    "        }\n"
    "        return false;\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public static bool search_matrix(int[][] matrix, int target) {\n"
    "        return false;\n"
    "    }\n"
    "}\n")

reg("search-2d-matrix", "c",
    "int search_matrix(AtlasIntMatrix matrix, int target) {\n"
    "    int rows = matrix.size;\n"
    "    if (rows == 0) return 0;\n"
    "    int cols = matrix.data[0].size;\n"
    "    int lo = 0, hi = rows * cols - 1;\n"
    "    while (lo <= hi) {\n"
    "        int mid = (lo + hi) / 2;\n"
    "        int v = matrix.data[mid / cols].data[mid % cols];\n"
    "        if (v == target) return 1;\n"
    "        if (v < target) lo = mid + 1; else hi = mid - 1;\n"
    "    }\n"
    "    return 0;\n"
    "}\n",
    "int search_matrix(AtlasIntMatrix matrix, int target) {\n"
    "    return 0;\n"
    "}\n")

reg("search-2d-matrix", "rust",
    "fn search_matrix(matrix: Vec<Vec<i32>>, target: i32) -> bool {\n"
    "    let rows = matrix.len();\n"
    "    if rows == 0 { return false; }\n"
    "    let cols = matrix[0].len();\n"
    "    let mut lo: i64 = 0;\n"
    "    let mut hi: i64 = (rows * cols) as i64 - 1;\n"
    "    while lo <= hi {\n"
    "        let mid = (lo + hi) / 2;\n"
    "        let v = matrix[(mid as usize) / cols][(mid as usize) % cols];\n"
    "        if v == target { return true; }\n"
    "        if v < target { lo = mid + 1; } else { hi = mid - 1; }\n"
    "    }\n"
    "    false\n"
    "}\n",
    "fn search_matrix(matrix: Vec<Vec<i32>>, target: i32) -> bool {\n"
    "    false\n"
    "}\n")


# ═════════════════════════════════════════════════════════════════════════
# remove-k-digits -> remove_k_digits(num, k) -> greedy monotonic stack.
# wrong: skips the leading-zero strip.
# ═════════════════════════════════════════════════════════════════════════

reg("remove-k-digits", "javascript",
    "function remove_k_digits(num, k) {\n"
    "    const stack = [];\n"
    "    let rem = k;\n"
    "    for (const ch of num) {\n"
    "        while (rem > 0 && stack.length > 0 && stack[stack.length - 1] > ch) { stack.pop(); rem--; }\n"
    "        stack.push(ch);\n"
    "    }\n"
    "    while (rem > 0) { stack.pop(); rem--; }\n"
    "    let result = stack.join('').replace(/^0+/, '');\n"
    "    return result === '' ? '0' : result;\n"
    "}\n",
    "function remove_k_digits(num, k) {\n"
    "    const stack = [];\n"
    "    let rem = k;\n"
    "    for (const ch of num) {\n"
    "        while (rem > 0 && stack.length > 0 && stack[stack.length - 1] > ch) { stack.pop(); rem--; }\n"
    "        stack.push(ch);\n"
    "    }\n"
    "    while (rem > 0) { stack.pop(); rem--; }\n"
    "    const result = stack.join('');\n"
    "    return result === '' ? '0' : result;\n"
    "}\n")

reg("remove-k-digits", "typescript",
    "function remove_k_digits(num: string, k: number): string {\n"
    "    const stack: string[] = [];\n"
    "    let rem = k;\n"
    "    for (const ch of num) {\n"
    "        while (rem > 0 && stack.length > 0 && stack[stack.length - 1] > ch) { stack.pop(); rem--; }\n"
    "        stack.push(ch);\n"
    "    }\n"
    "    while (rem > 0) { stack.pop(); rem--; }\n"
    "    let result = stack.join('').replace(/^0+/, '');\n"
    "    return result === '' ? '0' : result;\n"
    "}\n",
    "function remove_k_digits(num: string, k: number): string {\n"
    "    const stack: string[] = [];\n"
    "    let rem = k;\n"
    "    for (const ch of num) {\n"
    "        while (rem > 0 && stack.length > 0 && stack[stack.length - 1] > ch) { stack.pop(); rem--; }\n"
    "        stack.push(ch);\n"
    "    }\n"
    "    while (rem > 0) { stack.pop(); rem--; }\n"
    "    const result = stack.join('');\n"
    "    return result === '' ? '0' : result;\n"
    "}\n")

reg("remove-k-digits", "perl",
    "sub remove_k_digits {\n"
    "    my ($num, $k) = @_;\n"
    "    my @stack;\n"
    "    my $rem = $k;\n"
    "    foreach my $ch (split //, $num) {\n"
    "        while ($rem > 0 && @stack && $stack[-1] gt $ch) { pop @stack; $rem--; }\n"
    "        push @stack, $ch;\n"
    "    }\n"
    "    while ($rem > 0 && @stack) { pop @stack; $rem--; }\n"
    "    my $result = join('', @stack);\n"
    "    $result =~ s/^0+//;\n"
    "    return $result eq '' ? '0' : $result;\n"
    "}\n",
    "sub remove_k_digits {\n"
    "    my ($num, $k) = @_;\n"
    "    my @stack;\n"
    "    my $rem = $k;\n"
    "    foreach my $ch (split //, $num) {\n"
    "        while ($rem > 0 && @stack && $stack[-1] gt $ch) { pop @stack; $rem--; }\n"
    "        push @stack, $ch;\n"
    "    }\n"
    "    while ($rem > 0 && @stack) { pop @stack; $rem--; }\n"
    "    my $result = join('', @stack);\n"
    "    return $result eq '' ? '0' : $result;\n"
    "}\n")

reg("remove-k-digits", "java",
    "class Solution {\n"
    "    public String remove_k_digits(String num, int k) {\n"
    "        StringBuilder stack = new StringBuilder();\n"
    "        int rem = k;\n"
    "        for (int i = 0; i < num.length(); i++) {\n"
    "            char ch = num.charAt(i);\n"
    "            while (rem > 0 && stack.length() > 0 && stack.charAt(stack.length() - 1) > ch) {\n"
    "                stack.deleteCharAt(stack.length() - 1);\n"
    "                rem--;\n"
    "            }\n"
    "            stack.append(ch);\n"
    "        }\n"
    "        while (rem > 0 && stack.length() > 0) { stack.deleteCharAt(stack.length() - 1); rem--; }\n"
    "        int i = 0;\n"
    "        while (i < stack.length() && stack.charAt(i) == '0') i++;\n"
    "        String result = stack.substring(i);\n"
    "        return result.isEmpty() ? \"0\" : result;\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public String remove_k_digits(String num, int k) {\n"
    "        StringBuilder stack = new StringBuilder();\n"
    "        int rem = k;\n"
    "        for (int i = 0; i < num.length(); i++) {\n"
    "            char ch = num.charAt(i);\n"
    "            while (rem > 0 && stack.length() > 0 && stack.charAt(stack.length() - 1) > ch) {\n"
    "                stack.deleteCharAt(stack.length() - 1);\n"
    "                rem--;\n"
    "            }\n"
    "            stack.append(ch);\n"
    "        }\n"
    "        while (rem > 0 && stack.length() > 0) { stack.deleteCharAt(stack.length() - 1); rem--; }\n"
    "        String result = stack.toString();\n"
    "        return result.isEmpty() ? \"0\" : result;\n"
    "    }\n"
    "}\n")

reg("remove-k-digits", "cpp",
    "class Solution {\n"
    "public:\n"
    "    std::string remove_k_digits(std::string num, int k) {\n"
    "        std::string stack;\n"
    "        int rem = k;\n"
    "        for (char ch : num) {\n"
    "            while (rem > 0 && !stack.empty() && stack.back() > ch) { stack.pop_back(); rem--; }\n"
    "            stack.push_back(ch);\n"
    "        }\n"
    "        while (rem > 0 && !stack.empty()) { stack.pop_back(); rem--; }\n"
    "        size_t i = 0;\n"
    "        while (i < stack.size() && stack[i] == '0') i++;\n"
    "        std::string result = stack.substr(i);\n"
    "        return result.empty() ? \"0\" : result;\n"
    "    }\n"
    "};\n",
    "class Solution {\n"
    "public:\n"
    "    std::string remove_k_digits(std::string num, int k) {\n"
    "        std::string stack;\n"
    "        int rem = k;\n"
    "        for (char ch : num) {\n"
    "            while (rem > 0 && !stack.empty() && stack.back() > ch) { stack.pop_back(); rem--; }\n"
    "            stack.push_back(ch);\n"
    "        }\n"
    "        while (rem > 0 && !stack.empty()) { stack.pop_back(); rem--; }\n"
    "        return stack.empty() ? \"0\" : stack;\n"
    "    }\n"
    "};\n")

reg("remove-k-digits", "csharp",
    "class Solution {\n"
    "    public static string remove_k_digits(string num, int k) {\n"
    "        var stack = new System.Text.StringBuilder();\n"
    "        int rem = k;\n"
    "        foreach (char ch in num) {\n"
    "            while (rem > 0 && stack.Length > 0 && stack[stack.Length - 1] > ch) {\n"
    "                stack.Length--;\n"
    "                rem--;\n"
    "            }\n"
    "            stack.Append(ch);\n"
    "        }\n"
    "        while (rem > 0 && stack.Length > 0) { stack.Length--; rem--; }\n"
    "        string s = stack.ToString().TrimStart('0');\n"
    "        return s == \"\" ? \"0\" : s;\n"
    "    }\n"
    "}\n",
    "class Solution {\n"
    "    public static string remove_k_digits(string num, int k) {\n"
    "        var stack = new System.Text.StringBuilder();\n"
    "        int rem = k;\n"
    "        foreach (char ch in num) {\n"
    "            while (rem > 0 && stack.Length > 0 && stack[stack.Length - 1] > ch) {\n"
    "                stack.Length--;\n"
    "                rem--;\n"
    "            }\n"
    "            stack.Append(ch);\n"
    "        }\n"
    "        while (rem > 0 && stack.Length > 0) { stack.Length--; rem--; }\n"
    "        string s = stack.ToString();\n"
    "        return s == \"\" ? \"0\" : s;\n"
    "    }\n"
    "}\n")

reg("remove-k-digits", "c",
    "char* remove_k_digits(char* num, int k) {\n"
    "    int n = (int)strlen(num);\n"
    "    char *stack = (char *)malloc((size_t)n + 1);\n"
    "    int top = 0;\n"
    "    int rem = k;\n"
    "    for (int i = 0; i < n; i++) {\n"
    "        char ch = num[i];\n"
    "        while (rem > 0 && top > 0 && stack[top - 1] > ch) { top--; rem--; }\n"
    "        stack[top++] = ch;\n"
    "    }\n"
    "    while (rem > 0 && top > 0) { top--; rem--; }\n"
    "    int start = 0;\n"
    "    while (start < top && stack[start] == '0') start++;\n"
    "    char *out = (char *)malloc((size_t)(top - start) + 2);\n"
    "    if (start == top) { strcpy(out, \"0\"); }\n"
    "    else { memcpy(out, stack + start, (size_t)(top - start)); out[top - start] = '\\0'; }\n"
    "    free(stack);\n"
    "    return out;\n"
    "}\n",
    "char* remove_k_digits(char* num, int k) {\n"
    "    int n = (int)strlen(num);\n"
    "    char *stack = (char *)malloc((size_t)n + 1);\n"
    "    int top = 0;\n"
    "    int rem = k;\n"
    "    for (int i = 0; i < n; i++) {\n"
    "        char ch = num[i];\n"
    "        while (rem > 0 && top > 0 && stack[top - 1] > ch) { top--; rem--; }\n"
    "        stack[top++] = ch;\n"
    "    }\n"
    "    while (rem > 0 && top > 0) { top--; rem--; }\n"
    "    char *out = (char *)malloc((size_t)top + 2);\n"
    "    if (top == 0) { strcpy(out, \"0\"); }\n"
    "    else { memcpy(out, stack, (size_t)top); out[top] = '\\0'; }\n"
    "    free(stack);\n"
    "    return out;\n"
    "}\n")

reg("remove-k-digits", "rust",
    "fn remove_k_digits(num: String, k: i32) -> String {\n"
    "    let mut stack: Vec<char> = Vec::new();\n"
    "    let mut rem = k;\n"
    "    for ch in num.chars() {\n"
    "        while rem > 0 && !stack.is_empty() && *stack.last().unwrap() > ch { stack.pop(); rem -= 1; }\n"
    "        stack.push(ch);\n"
    "    }\n"
    "    while rem > 0 && !stack.is_empty() { stack.pop(); rem -= 1; }\n"
    "    let s: String = stack.into_iter().collect();\n"
    "    let trimmed = s.trim_start_matches('0');\n"
    "    if trimmed.is_empty() { \"0\".to_string() } else { trimmed.to_string() }\n"
    "}\n",
    "fn remove_k_digits(num: String, k: i32) -> String {\n"
    "    let mut stack: Vec<char> = Vec::new();\n"
    "    let mut rem = k;\n"
    "    for ch in num.chars() {\n"
    "        while rem > 0 && !stack.is_empty() && *stack.last().unwrap() > ch { stack.pop(); rem -= 1; }\n"
    "        stack.push(ch);\n"
    "    }\n"
    "    while rem > 0 && !stack.is_empty() { stack.pop(); rem -= 1; }\n"
    "    let s: String = stack.into_iter().collect();\n"
    "    if s.is_empty() { \"0\".to_string() } else { s }\n"
    "}\n")


# ═════════════════════════════════════════════════════════════════════════
# Harness plumbing (multi-language)
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


async def verify_one(pid, lang, contract, cases, correct_src, wrong_src):
    t0 = time.monotonic()
    correct_result = await evaluate_function(correct_src, lang, contract, cases)
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
    wrong_result = await evaluate_function(wrong_src, lang, contract, cases)
    n_wrong_pass = sum(1 for r in wrong_result.case_results if r.passed)
    if n_wrong_pass >= len(cases):
        return {"pid": pid, "lang": lang, "outcome": "corpus_weakness",
                "detail": f"corrupted solution still passed all {len(cases)}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    return {"pid": pid, "lang": lang, "outcome": "verified",
            "detail": f"{n_pass}/{len(cases)} correct, wrong rejected on {len(cases) - n_wrong_pass}/{len(cases)}",
            "duration_ms": (time.monotonic() - t0) * 1000}


async def main():
    only_pids = sys.argv[1:] if len(sys.argv) > 1 else None
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ledger.ensure_schema(con)
    results = []
    skipped = 0
    pids = [p for p in IMPLS if not only_pids or p in only_pids]
    for pid in pids:
        contract, cases, tsv = load_problem(con, pid)
        for lang in LANGS:
            if lang not in IMPLS[pid]:
                continue
            if ledger.already_verified(con, pid, lang, "function", test_suite_version=tsv):
                skipped += 1
                print(f"[SKIP] {pid:28s} {lang:12s} already verified")
                continue
            correct_src, wrong_src = IMPLS[pid][lang]
            r = await verify_one(pid, lang, contract, cases, correct_src, wrong_src)
            results.append(r)
            status = "PASS" if r["outcome"] == "verified" else "FAIL"
            print(f"[{status}] {pid:28s} {lang:12s} {r['outcome']:18s} {r['detail'][:150]}", flush=True)
            if r["outcome"] == "verified":
                ledger.record_cell(con, problem_id=pid, language=lang, mode="function",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version="core8-function-batch1-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL attempted: {len(results)}  skipped(already): {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
