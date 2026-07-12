"""Scales word-break, longest-increasing-subsequence,
longest-common-subsequence, edit-distance (Function Mode) across the 8
working languages -- classic, well-understood DP algorithms, none
bigint-blocked (docs/atlascode-bigint-numeric-audit.json).
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


# ── word-break ───────────────────────────────────────────────────────────────
def _js_word_break(wrong):
    return (
        "function word_break(s, word_dict) {\n"
        "    const dict = new Set(word_dict);\n"
        "    const n = s.length;\n"
        "    const dp = new Array(n+1).fill(false); dp[0] = true;\n"
        "    for (let i=1;i<=n;i++) { for (let j=0;j<i;j++) { if (dp[j] && dict.has(s.substring(j,i))) { dp[i]=true; break; } } }\n"
        f"    return {'!dp[n]' if wrong else 'dp[n]'};\n"
        "}\n"
    )


def _ts_word_break(wrong):
    return (
        "function word_break(s: string, word_dict: string[]): boolean {\n"
        "    const dict = new Set(word_dict);\n"
        "    const n = s.length;\n"
        "    const dp: boolean[] = new Array(n+1).fill(false); dp[0] = true;\n"
        "    for (let i=1;i<=n;i++) { for (let j=0;j<i;j++) { if (dp[j] && dict.has(s.substring(j,i))) { dp[i]=true; break; } } }\n"
        f"    return {'!dp[n]' if wrong else 'dp[n]'};\n"
        "}\n"
    )


def _java_word_break(wrong):
    return (
        "class Solution {\n"
        "    public boolean word_break(String s, String[] word_dict) {\n"
        "        java.util.Set<String> dict = new java.util.HashSet<>(java.util.Arrays.asList(word_dict));\n"
        "        int n = s.length();\n"
        "        boolean[] dp = new boolean[n+1]; dp[0] = true;\n"
        "        for (int i=1;i<=n;i++) { for (int j=0;j<i;j++) { if (dp[j] && dict.contains(s.substring(j,i))) { dp[i]=true; break; } } }\n"
        f"        return {'!dp[n]' if wrong else 'dp[n]'};\n"
        "    }\n"
        "}\n"
    )


def _cpp_word_break(wrong):
    return (
        "class Solution {\n"
        "public:\n"
        "    bool word_break(std::string s, std::vector<std::string> word_dict) {\n"
        "        std::unordered_set<std::string> dict(word_dict.begin(), word_dict.end());\n"
        "        int n = s.size();\n"
        "        std::vector<bool> dp(n+1, false); dp[0] = true;\n"
        "        for (int i=1;i<=n;i++) { for (int j=0;j<i;j++) { if (dp[j] && dict.count(s.substr(j,i-j))) { dp[i]=true; break; } } }\n"
        f"        return {'!dp[n]' if wrong else 'dp[n]'};\n"
        "    }\n"
        "};\n"
    )


def _csharp_word_break(wrong):
    return (
        "class Solution {\n"
        "    public static bool word_break(string s, string[] word_dict) {\n"
        "        var dict = new System.Collections.Generic.HashSet<string>(word_dict);\n"
        "        int n = s.Length;\n"
        "        bool[] dp = new bool[n+1]; dp[0] = true;\n"
        "        for (int i=1;i<=n;i++) { for (int j=0;j<i;j++) { if (dp[j] && dict.Contains(s.Substring(j,i-j))) { dp[i]=true; break; } } }\n"
        f"        return {'!dp[n]' if wrong else 'dp[n]'};\n"
        "    }\n"
        "}\n"
    )


def _perl_word_break(wrong):
    return (
        "sub word_break {\n"
        "    my ($s, $word_dict) = @_;\n"
        "    my %dict = map { $_ => 1 } @$word_dict;\n"
        "    my $n = length($s);\n"
        "    my @dp = (0) x ($n+1); $dp[0] = 1;\n"
        "    for (my $i=1;$i<=$n;$i++) {\n"
        "        for (my $j=0;$j<$i;$j++) {\n"
        "            if ($dp[$j] && exists $dict{substr($s,$j,$i-$j)}) { $dp[$i]=1; last; }\n"
        "        }\n"
        "    }\n"
        f"    return {'!$dp[$n]' if wrong else '$dp[$n]'};\n"
        "}\n"
    )


def _c_word_break(wrong):
    ret = "!dp[n]" if wrong else "dp[n]"
    return (
        "int word_break(char* s, AtlasStringArray word_dict) {\n"
        "    int n = 0; while (s[n]) n++;\n"
        "    int* dp = (int*)calloc(n+1, sizeof(int)); dp[0] = 1;\n"
        "    for (int i=1;i<=n;i++) {\n"
        "        for (int j=0;j<i;j++) {\n"
        "            if (!dp[j]) continue;\n"
        "            int len = i - j;\n"
        "            for (int w=0; w<word_dict.size; w++) {\n"
        "                char* word = word_dict.data[w];\n"
        "                int wl = 0; while (word[wl]) wl++;\n"
        "                if (wl != len) continue;\n"
        "                int match = 1;\n"
        "                for (int k=0;k<len;k++) { if (s[j+k] != word[k]) { match = 0; break; } }\n"
        "                if (match) { dp[i] = 1; break; }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        f"    int result = {ret};\n"
        "    free(dp);\n"
        "    return result;\n"
        "}\n"
    )


def _rust_word_break(wrong):
    ret = "!dp[n]" if wrong else "dp[n]"
    return (
        "use std::collections::HashSet;\n\n"
        "fn word_break(s: String, word_dict: Vec<String>) -> bool {\n"
        "    let dict: HashSet<String> = word_dict.into_iter().collect();\n"
        "    let n = s.len();\n"
        "    let chars: Vec<char> = s.chars().collect();\n"
        "    let mut dp = vec![false; n+1]; dp[0] = true;\n"
        "    for i in 1..=n {\n"
        "        for j in 0..i {\n"
        "            if dp[j] {\n"
        "                let sub: String = chars[j..i].iter().collect();\n"
        "                if dict.contains(&sub) { dp[i] = true; break; }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        f"    {ret}\n"
        "}\n"
    )


# ── longest-increasing-subsequence ───────────────────────────────────────────
def _js_lis(wrong):
    a = " + 1" if wrong else ""
    return (
        "function lis(nums) {\n"
        "    if (nums.length === 0) return 0;\n"
        "    const tails = [];\n"
        "    for (const x of nums) {\n"
        "        let lo = 0, hi = tails.length;\n"
        "        while (lo < hi) { const mid = (lo+hi)>>1; if (tails[mid] < x) lo = mid+1; else hi = mid; }\n"
        "        if (lo === tails.length) tails.push(x); else tails[lo] = x;\n"
        "    }\n"
        f"    return tails.length{a};\n"
        "}\n"
    )


def _ts_lis(wrong):
    a = " + 1" if wrong else ""
    return (
        "function lis(nums: number[]): number {\n"
        "    if (nums.length === 0) return 0;\n"
        "    const tails: number[] = [];\n"
        "    for (const x of nums) {\n"
        "        let lo = 0, hi = tails.length;\n"
        "        while (lo < hi) { const mid = (lo+hi)>>1; if (tails[mid] < x) lo = mid+1; else hi = mid; }\n"
        "        if (lo === tails.length) tails.push(x); else tails[lo] = x;\n"
        "    }\n"
        f"    return tails.length{a};\n"
        "}\n"
    )


def _java_lis(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public int lis(int[] nums) {\n"
        "        if (nums.length == 0) return 0;\n"
        "        int[] tails = new int[nums.length]; int size = 0;\n"
        "        for (int x : nums) {\n"
        "            int lo = 0, hi = size;\n"
        "            while (lo < hi) { int mid = (lo+hi)/2; if (tails[mid] < x) lo = mid+1; else hi = mid; }\n"
        "            tails[lo] = x; if (lo == size) size++;\n"
        "        }\n"
        f"        return size{a};\n"
        "    }\n"
        "}\n"
    )


def _cpp_lis(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "public:\n"
        "    int lis(std::vector<int> nums) {\n"
        "        std::vector<int> tails;\n"
        "        for (int x : nums) {\n"
        "            auto it = std::lower_bound(tails.begin(), tails.end(), x);\n"
        "            if (it == tails.end()) tails.push_back(x); else *it = x;\n"
        "        }\n"
        f"        return (int)tails.size(){a};\n"
        "    }\n"
        "};\n"
    )


def _csharp_lis(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public static int lis(int[] nums) {\n"
        "        var tails = new System.Collections.Generic.List<int>();\n"
        "        foreach (int x in nums) {\n"
        "            int lo = 0, hi = tails.Count;\n"
        "            while (lo < hi) { int mid = (lo+hi)/2; if (tails[mid] < x) lo = mid+1; else hi = mid; }\n"
        "            if (lo == tails.Count) tails.Add(x); else tails[lo] = x;\n"
        "        }\n"
        f"        return tails.Count{a};\n"
        "    }\n"
        "}\n"
    )


def _perl_lis(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub lis {\n"
        "    my ($nums) = @_;\n"
        "    my @tails;\n"
        "    foreach my $x (@$nums) {\n"
        "        my $lo = 0; my $hi = scalar(@tails);\n"
        "        while ($lo < $hi) { my $mid = int(($lo+$hi)/2); if ($tails[$mid] < $x) { $lo = $mid+1; } else { $hi = $mid; } }\n"
        "        $tails[$lo] = $x;\n"
        "    }\n"
        f"    return scalar(@tails){a};\n"
        "}\n"
    )


def _c_lis(wrong):
    a = " + 1" if wrong else ""
    return (
        "int lis(AtlasIntArray nums) {\n"
        "    int* tails = (int*)malloc(sizeof(int) * (nums.size > 0 ? nums.size : 1));\n"
        "    int size = 0;\n"
        "    for (int k=0;k<nums.size;k++) {\n"
        "        int x = nums.data[k];\n"
        "        int lo = 0, hi = size;\n"
        "        while (lo < hi) { int mid = (lo+hi)/2; if (tails[mid] < x) lo = mid+1; else hi = mid; }\n"
        "        tails[lo] = x; if (lo == size) size++;\n"
        "    }\n"
        "    free(tails);\n"
        f"    return size{a};\n"
        "}\n"
    )


def _rust_lis(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn lis(nums: Vec<i32>) -> i32 {\n"
        "    let mut tails: Vec<i32> = Vec::new();\n"
        "    for x in nums.iter() {\n"
        "        let pos = tails.partition_point(|&t| t < *x);\n"
        "        if pos == tails.len() { tails.push(*x); } else { tails[pos] = *x; }\n"
        "    }\n"
        f"    tails.len() as i32{a}\n"
        "}\n"
    )


# ── longest-common-subsequence ───────────────────────────────────────────────
def _js_lcs(wrong):
    a = " + 1" if wrong else ""
    return (
        "function lcs(s1, s2) {\n"
        "    const n = s1.length, m = s2.length;\n"
        "    const dp = Array.from({length: n+1}, () => new Array(m+1).fill(0));\n"
        "    for (let i=1;i<=n;i++) for (let j=1;j<=m;j++) {\n"
        "        if (s1[i-1] === s2[j-1]) dp[i][j] = dp[i-1][j-1] + 1;\n"
        "        else dp[i][j] = Math.max(dp[i-1][j], dp[i][j-1]);\n"
        "    }\n"
        f"    return dp[n][m]{a};\n"
        "}\n"
    )


def _ts_lcs(wrong):
    a = " + 1" if wrong else ""
    return (
        "function lcs(s1: string, s2: string): number {\n"
        "    const n = s1.length, m = s2.length;\n"
        "    const dp: number[][] = Array.from({length: n+1}, () => new Array(m+1).fill(0));\n"
        "    for (let i=1;i<=n;i++) for (let j=1;j<=m;j++) {\n"
        "        if (s1[i-1] === s2[j-1]) dp[i][j] = dp[i-1][j-1] + 1;\n"
        "        else dp[i][j] = Math.max(dp[i-1][j], dp[i][j-1]);\n"
        "    }\n"
        f"    return dp[n][m]{a};\n"
        "}\n"
    )


def _java_lcs(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public int lcs(String s1, String s2) {\n"
        "        int n = s1.length(), m = s2.length();\n"
        "        int[][] dp = new int[n+1][m+1];\n"
        "        for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) {\n"
        "            if (s1.charAt(i-1) == s2.charAt(j-1)) dp[i][j] = dp[i-1][j-1] + 1;\n"
        "            else dp[i][j] = Math.max(dp[i-1][j], dp[i][j-1]);\n"
        "        }\n"
        f"        return dp[n][m]{a};\n"
        "    }\n"
        "}\n"
    )


def _cpp_lcs(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "public:\n"
        "    int lcs(std::string s1, std::string s2) {\n"
        "        int n = s1.size(), m = s2.size();\n"
        "        std::vector<std::vector<int>> dp(n+1, std::vector<int>(m+1, 0));\n"
        "        for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) {\n"
        "            if (s1[i-1] == s2[j-1]) dp[i][j] = dp[i-1][j-1] + 1;\n"
        "            else dp[i][j] = std::max(dp[i-1][j], dp[i][j-1]);\n"
        "        }\n"
        f"        return dp[n][m]{a};\n"
        "    }\n"
        "};\n"
    )


def _csharp_lcs(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public static int lcs(string s1, string s2) {\n"
        "        int n = s1.Length, m = s2.Length;\n"
        "        int[,] dp = new int[n+1, m+1];\n"
        "        for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) {\n"
        "            if (s1[i-1] == s2[j-1]) dp[i,j] = dp[i-1,j-1] + 1;\n"
        "            else dp[i,j] = System.Math.Max(dp[i-1,j], dp[i,j-1]);\n"
        "        }\n"
        f"        return dp[n,m]{a};\n"
        "    }\n"
        "}\n"
    )


def _perl_lcs(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub lcs {\n"
        "    my ($s1, $s2) = @_;\n"
        "    my $n = length($s1); my $m = length($s2);\n"
        "    my @dp; for my $i (0..$n) { for my $j (0..$m) { $dp[$i][$j] = 0; } }\n"
        "    for (my $i=1;$i<=$n;$i++) {\n"
        "        for (my $j=1;$j<=$m;$j++) {\n"
        "            if (substr($s1,$i-1,1) eq substr($s2,$j-1,1)) { $dp[$i][$j] = $dp[$i-1][$j-1] + 1; }\n"
        "            else { $dp[$i][$j] = ($dp[$i-1][$j] > $dp[$i][$j-1]) ? $dp[$i-1][$j] : $dp[$i][$j-1]; }\n"
        "        }\n"
        "    }\n"
        f"    return $dp[$n][$m]{a};\n"
        "}\n"
    )


def _c_lcs(wrong):
    a = " + 1" if wrong else ""
    return (
        "int lcs(char* s1, char* s2) {\n"
        "    int n = 0; while (s1[n]) n++;\n"
        "    int m = 0; while (s2[m]) m++;\n"
        "    int** dp = (int**)malloc(sizeof(int*)*(n+1));\n"
        "    for (int i=0;i<=n;i++) { dp[i] = (int*)calloc(m+1, sizeof(int)); }\n"
        "    for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) {\n"
        "        if (s1[i-1] == s2[j-1]) dp[i][j] = dp[i-1][j-1] + 1;\n"
        "        else dp[i][j] = dp[i-1][j] > dp[i][j-1] ? dp[i-1][j] : dp[i][j-1];\n"
        "    }\n"
        f"    int result = dp[n][m]{a};\n"
        "    for (int i=0;i<=n;i++) free(dp[i]);\n"
        "    free(dp);\n"
        "    return result;\n"
        "}\n"
    )


def _rust_lcs(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn lcs(s1: String, s2: String) -> i32 {\n"
        "    let a: Vec<char> = s1.chars().collect();\n"
        "    let b: Vec<char> = s2.chars().collect();\n"
        "    let n = a.len(); let m = b.len();\n"
        "    let mut dp = vec![vec![0i32; m+1]; n+1];\n"
        "    for i in 1..=n { for j in 1..=m {\n"
        "        if a[i-1] == b[j-1] { dp[i][j] = dp[i-1][j-1] + 1; }\n"
        "        else { dp[i][j] = dp[i-1][j].max(dp[i][j-1]); }\n"
        "    } }\n"
        f"    dp[n][m]{a}\n"
        "}\n"
    )


# ── edit-distance ────────────────────────────────────────────────────────────
def _js_edit_distance(wrong):
    a = " + 1" if wrong else ""
    return (
        "function edit_distance(w1, w2) {\n"
        "    const n = w1.length, m = w2.length;\n"
        "    const dp = Array.from({length: n+1}, () => new Array(m+1).fill(0));\n"
        "    for (let i=0;i<=n;i++) dp[i][0] = i;\n"
        "    for (let j=0;j<=m;j++) dp[0][j] = j;\n"
        "    for (let i=1;i<=n;i++) for (let j=1;j<=m;j++) {\n"
        "        if (w1[i-1] === w2[j-1]) dp[i][j] = dp[i-1][j-1];\n"
        "        else dp[i][j] = 1 + Math.min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]);\n"
        "    }\n"
        f"    return dp[n][m]{a};\n"
        "}\n"
    )


def _ts_edit_distance(wrong):
    a = " + 1" if wrong else ""
    return (
        "function edit_distance(w1: string, w2: string): number {\n"
        "    const n = w1.length, m = w2.length;\n"
        "    const dp: number[][] = Array.from({length: n+1}, () => new Array(m+1).fill(0));\n"
        "    for (let i=0;i<=n;i++) dp[i][0] = i;\n"
        "    for (let j=0;j<=m;j++) dp[0][j] = j;\n"
        "    for (let i=1;i<=n;i++) for (let j=1;j<=m;j++) {\n"
        "        if (w1[i-1] === w2[j-1]) dp[i][j] = dp[i-1][j-1];\n"
        "        else dp[i][j] = 1 + Math.min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]);\n"
        "    }\n"
        f"    return dp[n][m]{a};\n"
        "}\n"
    )


def _java_edit_distance(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public int edit_distance(String w1, String w2) {\n"
        "        int n = w1.length(), m = w2.length();\n"
        "        int[][] dp = new int[n+1][m+1];\n"
        "        for (int i=0;i<=n;i++) dp[i][0] = i;\n"
        "        for (int j=0;j<=m;j++) dp[0][j] = j;\n"
        "        for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) {\n"
        "            if (w1.charAt(i-1) == w2.charAt(j-1)) dp[i][j] = dp[i-1][j-1];\n"
        "            else dp[i][j] = 1 + Math.min(dp[i-1][j], Math.min(dp[i][j-1], dp[i-1][j-1]));\n"
        "        }\n"
        f"        return dp[n][m]{a};\n"
        "    }\n"
        "}\n"
    )


def _cpp_edit_distance(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "public:\n"
        "    int edit_distance(std::string w1, std::string w2) {\n"
        "        int n = w1.size(), m = w2.size();\n"
        "        std::vector<std::vector<int>> dp(n+1, std::vector<int>(m+1, 0));\n"
        "        for (int i=0;i<=n;i++) dp[i][0] = i;\n"
        "        for (int j=0;j<=m;j++) dp[0][j] = j;\n"
        "        for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) {\n"
        "            if (w1[i-1] == w2[j-1]) dp[i][j] = dp[i-1][j-1];\n"
        "            else dp[i][j] = 1 + std::min({dp[i-1][j], dp[i][j-1], dp[i-1][j-1]});\n"
        "        }\n"
        f"        return dp[n][m]{a};\n"
        "    }\n"
        "};\n"
    )


def _csharp_edit_distance(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public static int edit_distance(string w1, string w2) {\n"
        "        int n = w1.Length, m = w2.Length;\n"
        "        int[,] dp = new int[n+1, m+1];\n"
        "        for (int i=0;i<=n;i++) dp[i,0] = i;\n"
        "        for (int j=0;j<=m;j++) dp[0,j] = j;\n"
        "        for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) {\n"
        "            if (w1[i-1] == w2[j-1]) dp[i,j] = dp[i-1,j-1];\n"
        "            else dp[i,j] = 1 + System.Math.Min(dp[i-1,j], System.Math.Min(dp[i,j-1], dp[i-1,j-1]));\n"
        "        }\n"
        f"        return dp[n,m]{a};\n"
        "    }\n"
        "}\n"
    )


def _perl_edit_distance(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub edit_distance {\n"
        "    my ($w1, $w2) = @_;\n"
        "    my $n = length($w1); my $m = length($w2);\n"
        "    my @dp;\n"
        "    for my $i (0..$n) { $dp[$i][0] = $i; }\n"
        "    for my $j (0..$m) { $dp[0][$j] = $j; }\n"
        "    for (my $i=1;$i<=$n;$i++) {\n"
        "        for (my $j=1;$j<=$m;$j++) {\n"
        "            if (substr($w1,$i-1,1) eq substr($w2,$j-1,1)) { $dp[$i][$j] = $dp[$i-1][$j-1]; }\n"
        "            else {\n"
        "                my $mn = $dp[$i-1][$j];\n"
        "                $mn = $dp[$i][$j-1] if $dp[$i][$j-1] < $mn;\n"
        "                $mn = $dp[$i-1][$j-1] if $dp[$i-1][$j-1] < $mn;\n"
        "                $dp[$i][$j] = 1 + $mn;\n"
        "            }\n"
        "        }\n"
        "    }\n"
        f"    return $dp[$n][$m]{a};\n"
        "}\n"
    )


def _c_edit_distance(wrong):
    a = " + 1" if wrong else ""
    return (
        "int edit_distance(char* w1, char* w2) {\n"
        "    int n = 0; while (w1[n]) n++;\n"
        "    int m = 0; while (w2[m]) m++;\n"
        "    int** dp = (int**)malloc(sizeof(int*)*(n+1));\n"
        "    for (int i=0;i<=n;i++) dp[i] = (int*)malloc(sizeof(int)*(m+1));\n"
        "    for (int i=0;i<=n;i++) dp[i][0] = i;\n"
        "    for (int j=0;j<=m;j++) dp[0][j] = j;\n"
        "    for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) {\n"
        "        if (w1[i-1] == w2[j-1]) dp[i][j] = dp[i-1][j-1];\n"
        "        else {\n"
        "            int mn = dp[i-1][j];\n"
        "            if (dp[i][j-1] < mn) mn = dp[i][j-1];\n"
        "            if (dp[i-1][j-1] < mn) mn = dp[i-1][j-1];\n"
        "            dp[i][j] = 1 + mn;\n"
        "        }\n"
        "    }\n"
        f"    int result = dp[n][m]{a};\n"
        "    for (int i=0;i<=n;i++) free(dp[i]);\n"
        "    free(dp);\n"
        "    return result;\n"
        "}\n"
    )


def _rust_edit_distance(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn edit_distance(w1: String, w2: String) -> i32 {\n"
        "    let a: Vec<char> = w1.chars().collect();\n"
        "    let b: Vec<char> = w2.chars().collect();\n"
        "    let n = a.len(); let m = b.len();\n"
        "    let mut dp = vec![vec![0i32; m+1]; n+1];\n"
        "    for i in 0..=n { dp[i][0] = i as i32; }\n"
        "    for j in 0..=m { dp[0][j] = j as i32; }\n"
        "    for i in 1..=n { for j in 1..=m {\n"
        "        if a[i-1] == b[j-1] { dp[i][j] = dp[i-1][j-1]; }\n"
        "        else { dp[i][j] = 1 + dp[i-1][j].min(dp[i][j-1]).min(dp[i-1][j-1]); }\n"
        "    } }\n"
        f"    dp[n][m]{a}\n"
        "}\n"
    )


_BUILDERS = {
    "word-break": {"javascript": _js_word_break, "typescript": _ts_word_break, "java": _java_word_break, "cpp": _cpp_word_break,
                   "csharp": _csharp_word_break, "perl": _perl_word_break, "c": _c_word_break, "rust": _rust_word_break},
    "longest-increasing-subsequence": {"javascript": _js_lis, "typescript": _ts_lis, "java": _java_lis, "cpp": _cpp_lis,
                                       "csharp": _csharp_lis, "perl": _perl_lis, "c": _c_lis, "rust": _rust_lis},
    "longest-common-subsequence": {"javascript": _js_lcs, "typescript": _ts_lcs, "java": _java_lcs, "cpp": _cpp_lcs,
                                   "csharp": _csharp_lcs, "perl": _perl_lcs, "c": _c_lcs, "rust": _rust_lcs},
    "edit-distance": {"javascript": _js_edit_distance, "typescript": _ts_edit_distance, "java": _java_edit_distance, "cpp": _cpp_edit_distance,
                      "csharp": _csharp_edit_distance, "perl": _perl_edit_distance, "c": _c_edit_distance, "rust": _rust_edit_distance},
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
                          f"stderr={(sample_fail.stderr if sample_fail else '')[:200]}",
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
            print(f"[{status}] {lang:10s} {pid:32s} {r['outcome']:18s} {r['detail'][:130]}", flush=True)
            if r["outcome"] == "verified":
                ledger.record_cell(con, problem_id=pid, language=lang, mode="function",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=f"{lang}-dp-string-v1", contract_version=cv, test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
