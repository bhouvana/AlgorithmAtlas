"""Scales valid-parentheses, valid-anagram, missing-number, single-number,
number-of-1-bits, power-of-two, hamming-distance, move-zeroes,
majority-element (Function Mode) across the 8 working languages.

reverse-bits deliberately EXCLUDED from this batch: its corpus includes
n=1 -> 2147483648 (2^31), which does not fit in a signed 32-bit int (max
2147483647) -- the same class of numeric-representation gap as the
bigint-blocked list, needs separate investigation before attempting.
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


# ── valid-parentheses ────────────────────────────────────────────────────────
def _js_valid_paren(wrong):
    return (
        "function is_valid(s) {\n"
        "    const stack = []; const pairs = {')':'(', ']':'[', '}':'{'};\n"
        "    for (const ch of s) {\n"
        "        if (ch==='('||ch==='['||ch==='{') stack.push(ch);\n"
        "        else { if (stack.length===0 || stack.pop() !== pairs[ch]) return false; }\n"
        "    }\n"
        f"    return {'stack.length !== 0' if wrong else 'stack.length === 0'};\n"
        "}\n"
    )


def _ts_valid_paren(wrong):
    return (
        "function is_valid(s: string): boolean {\n"
        "    const stack: string[] = []; const pairs: Record<string,string> = {')':'(', ']':'[', '}':'{'};\n"
        "    for (const ch of s) {\n"
        "        if (ch==='('||ch==='['||ch==='{') stack.push(ch);\n"
        "        else { if (stack.length===0 || stack.pop() !== pairs[ch]) return false; }\n"
        "    }\n"
        f"    return {'stack.length !== 0' if wrong else 'stack.length === 0'};\n"
        "}\n"
    )


def _java_valid_paren(wrong):
    return (
        "class Solution {\n"
        "    public boolean is_valid(String s) {\n"
        "        java.util.Deque<Character> stack = new java.util.ArrayDeque<>();\n"
        "        for (char ch : s.toCharArray()) {\n"
        "            if (ch=='('||ch=='['||ch=='{') stack.push(ch);\n"
        "            else {\n"
        "                if (stack.isEmpty()) return false;\n"
        "                char top = stack.pop();\n"
        "                if ((ch==')'&&top!='(') || (ch==']'&&top!='[') || (ch=='}'&&top!='{')) return false;\n"
        "            }\n"
        "        }\n"
        f"        return {'!stack.isEmpty()' if wrong else 'stack.isEmpty()'};\n"
        "    }\n"
        "}\n"
    )


def _cpp_valid_paren(wrong):
    return (
        "class Solution {\n"
        "public:\n"
        "    bool is_valid(std::string s) {\n"
        "        std::string stack;\n"
        "        for (char ch : s) {\n"
        "            if (ch=='('||ch=='['||ch=='{') stack.push_back(ch);\n"
        "            else {\n"
        "                if (stack.empty()) return false;\n"
        "                char top = stack.back(); stack.pop_back();\n"
        "                if ((ch==')'&&top!='(') || (ch==']'&&top!='[') || (ch=='}'&&top!='{')) return false;\n"
        "            }\n"
        "        }\n"
        f"        return {'!stack.empty()' if wrong else 'stack.empty()'};\n"
        "    }\n"
        "};\n"
    )


def _csharp_valid_paren(wrong):
    return (
        "class Solution {\n"
        "    public static bool is_valid(string s) {\n"
        "        var stack = new System.Collections.Generic.Stack<char>();\n"
        "        foreach (char ch in s) {\n"
        "            if (ch=='('||ch=='['||ch=='{') stack.Push(ch);\n"
        "            else {\n"
        "                if (stack.Count==0) return false;\n"
        "                char top = stack.Pop();\n"
        "                if ((ch==')'&&top!='(') || (ch==']'&&top!='[') || (ch=='}'&&top!='{')) return false;\n"
        "            }\n"
        "        }\n"
        f"        return {'stack.Count != 0' if wrong else 'stack.Count == 0'};\n"
        "    }\n"
        "}\n"
    )


def _perl_valid_paren(wrong):
    return (
        "sub is_valid {\n"
        "    my ($s) = @_;\n"
        "    my @stack;\n"
        "    my %pairs = (')' => '(', ']' => '[', '}' => '{');\n"
        "    foreach my $ch (split //, $s) {\n"
        "        if ($ch eq '(' || $ch eq '[' || $ch eq '{') { push @stack, $ch; }\n"
        "        else { return 0 if !@stack; my $top = pop @stack; return 0 if $top ne $pairs{$ch}; }\n"
        "    }\n"
        f"    return {'scalar(@stack) != 0' if wrong else 'scalar(@stack) == 0'};\n"
        "}\n"
    )


def _c_valid_paren(wrong):
    return (
        "int is_valid(char* s) {\n"
        "    int n = 0; while (s[n]) n++;\n"
        "    char* stack = (char*)malloc(n+1); int top = 0;\n"
        "    int ok = 1;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        char ch = s[i];\n"
        "        if (ch=='('||ch=='['||ch=='{') { stack[top++] = ch; }\n"
        "        else {\n"
        "            if (top==0) { ok = 0; break; }\n"
        "            char t = stack[--top];\n"
        "            if ((ch==')'&&t!='(') || (ch==']'&&t!='[') || (ch=='}'&&t!='{')) { ok = 0; break; }\n"
        "        }\n"
        "    }\n"
        f"    int result = ok && {'top != 0' if wrong else 'top == 0'};\n"
        "    free(stack);\n"
        "    return result;\n"
        "}\n"
    )


def _rust_valid_paren(wrong):
    return (
        "fn is_valid(s: String) -> bool {\n"
        "    let mut stack: Vec<char> = Vec::new();\n"
        "    for ch in s.chars() {\n"
        "        if ch=='('||ch=='['||ch=='{' { stack.push(ch); }\n"
        "        else {\n"
        "            let top = stack.pop();\n"
        "            match (ch, top) {\n"
        "                (')', Some('(')) => {},\n"
        "                (']', Some('[')) => {},\n"
        "                ('}', Some('{')) => {},\n"
        "                _ => return false,\n"
        "            }\n"
        "        }\n"
        "    }\n"
        f"    {'!stack.is_empty()' if wrong else 'stack.is_empty()'}\n"
        "}\n"
    )


# ── valid-anagram ────────────────────────────────────────────────────────────
def _js_valid_anagram(wrong):
    return (
        "function is_anagram(s, t) {\n"
        "    if (s.length !== t.length) return false;\n"
        "    const count = {};\n"
        "    for (const ch of s) count[ch] = (count[ch]||0) + 1;\n"
        "    for (const ch of t) { count[ch] = (count[ch]||0) - 1; if (count[ch] < 0) return false; }\n"
        f"    return {'!Object.values(count).every(v => v === 0)' if wrong else 'Object.values(count).every(v => v === 0)'};\n"
        "}\n"
    )


def _ts_valid_anagram(wrong):
    return (
        "function is_anagram(s: string, t: string): boolean {\n"
        "    if (s.length !== t.length) return false;\n"
        "    const count: Record<string, number> = {};\n"
        "    for (const ch of s) count[ch] = (count[ch]||0) + 1;\n"
        "    for (const ch of t) { count[ch] = (count[ch]||0) - 1; if (count[ch] < 0) return false; }\n"
        f"    return {'!Object.values(count).every(v => v === 0)' if wrong else 'Object.values(count).every(v => v === 0)'};\n"
        "}\n"
    )


def _java_valid_anagram(wrong):
    return (
        "class Solution {\n"
        "    public boolean is_anagram(String s, String t) {\n"
        "        if (s.length() != t.length()) return false;\n"
        "        int[] count = new int[256];\n"
        "        for (char c : s.toCharArray()) count[c]++;\n"
        "        for (char c : t.toCharArray()) count[c]--;\n"
        "        for (int c : count) if (c != 0) return " + ("true" if wrong else "false") + ";\n"
        f"        return {'false' if wrong else 'true'};\n"
        "    }\n"
        "}\n"
    )


def _cpp_valid_anagram(wrong):
    return (
        "class Solution {\n"
        "public:\n"
        "    bool is_anagram(std::string s, std::string t) {\n"
        "        if (s.size() != t.size()) return false;\n"
        "        int count[256] = {0};\n"
        "        for (char c : s) count[(unsigned char)c]++;\n"
        "        for (char c : t) count[(unsigned char)c]--;\n"
        "        for (int c : count) if (c != 0) return " + ("true" if wrong else "false") + ";\n"
        f"        return {'false' if wrong else 'true'};\n"
        "    }\n"
        "};\n"
    )


def _csharp_valid_anagram(wrong):
    return (
        "class Solution {\n"
        "    public static bool is_anagram(string s, string t) {\n"
        "        if (s.Length != t.Length) return false;\n"
        "        int[] count = new int[256];\n"
        "        foreach (char c in s) count[c]++;\n"
        "        foreach (char c in t) count[c]--;\n"
        "        foreach (int c in count) if (c != 0) return " + ("true" if wrong else "false") + ";\n"
        f"        return {'false' if wrong else 'true'};\n"
        "    }\n"
        "}\n"
    )


def _perl_valid_anagram(wrong):
    return (
        "sub is_anagram {\n"
        "    my ($s, $t) = @_;\n"
        "    return 0 if length($s) != length($t);\n"
        "    my %count;\n"
        "    foreach my $ch (split //, $s) { $count{$ch}++; }\n"
        "    foreach my $ch (split //, $t) { $count{$ch}--; return 0 if $count{$ch} < 0; }\n"
        "    foreach my $v (values %count) { return " + ("1" if wrong else "0") + " if $v != 0; }\n"
        f"    return {'0' if wrong else '1'};\n"
        "}\n"
    )


def _c_valid_anagram(wrong):
    return (
        "int is_anagram(char* s, char* t) {\n"
        "    int ns=0; while(s[ns])ns++; int nt=0; while(t[nt])nt++;\n"
        "    if (ns != nt) return 0;\n"
        "    int count[256] = {0};\n"
        "    for (int i=0;i<ns;i++) count[(unsigned char)s[i]]++;\n"
        "    for (int i=0;i<nt;i++) count[(unsigned char)t[i]]--;\n"
        "    for (int i=0;i<256;i++) if (count[i] != 0) return " + ("1" if wrong else "0") + ";\n"
        f"    return {'0' if wrong else '1'};\n"
        "}\n"
    )


def _rust_valid_anagram(wrong):
    return (
        "fn is_anagram(s: String, t: String) -> bool {\n"
        "    if s.len() != t.len() { return false; }\n"
        "    let mut count = [0i32; 256];\n"
        "    for b in s.bytes() { count[b as usize] += 1; }\n"
        "    for b in t.bytes() { count[b as usize] -= 1; }\n"
        "    for c in count.iter() { if *c != 0 { return " + ("true" if wrong else "false") + "; } }\n"
        f"    {'false' if wrong else 'true'}\n"
        "}\n"
    )


# ── missing-number ───────────────────────────────────────────────────────────
def _js_missing(wrong):
    a = " + 1" if wrong else ""
    return (
        "function missing_number(nums) {\n"
        "    const n = nums.length; let expected = n*(n+1)/2; let actual = 0;\n"
        "    for (const x of nums) actual += x;\n"
        f"    return (expected - actual){a};\n"
        "}\n"
    )


def _ts_missing(wrong):
    a = " + 1" if wrong else ""
    return (
        "function missing_number(nums: number[]): number {\n"
        "    const n = nums.length; let expected = n*(n+1)/2; let actual = 0;\n"
        "    for (const x of nums) actual += x;\n"
        f"    return (expected - actual){a};\n"
        "}\n"
    )


def _java_missing(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public int missing_number(int[] nums) {\n"
        "        int n = nums.length; long expected = (long)n*(n+1)/2; long actual = 0;\n"
        "        for (int x : nums) actual += x;\n"
        f"        return (int)(expected - actual){a};\n"
        "    }\n"
        "}\n"
    )


def _cpp_missing(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "public:\n"
        "    int missing_number(std::vector<int> nums) {\n"
        "        long long n = nums.size(); long long expected = n*(n+1)/2; long long actual = 0;\n"
        "        for (int x : nums) actual += x;\n"
        f"        return (int)(expected - actual){a};\n"
        "    }\n"
        "};\n"
    )


def _csharp_missing(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public static int missing_number(int[] nums) {\n"
        "        long n = nums.Length; long expected = n*(n+1)/2; long actual = 0;\n"
        "        foreach (int x in nums) actual += x;\n"
        f"        return (int)(expected - actual){a};\n"
        "    }\n"
        "}\n"
    )


def _perl_missing(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub missing_number {\n"
        "    my ($nums) = @_;\n"
        "    my $n = scalar(@$nums); my $expected = $n*($n+1)/2; my $actual = 0;\n"
        "    foreach my $x (@$nums) { $actual += $x; }\n"
        f"    return ($expected - $actual){a};\n"
        "}\n"
    )


def _c_missing(wrong):
    a = " + 1" if wrong else ""
    return (
        "int missing_number(AtlasIntArray nums) {\n"
        "    int n = nums.size;\n"
        "    long long expected = (long long)n*(n+1)/2; long long actual = 0;\n"
        "    for (int i=0;i<n;i++) actual += nums.data[i];\n"
        f"    return (int)(expected - actual){a};\n"
        "}\n"
    )


def _rust_missing(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn missing_number(nums: Vec<i32>) -> i32 {\n"
        "    let n = nums.len() as i64; let expected = n*(n+1)/2;\n"
        "    let actual: i64 = nums.iter().map(|&x| x as i64).sum();\n"
        f"    (expected - actual) as i32{a}\n"
        "}\n"
    )


# ── single-number ────────────────────────────────────────────────────────────
def _js_single(wrong):
    a = " + 1" if wrong else ""
    return f"function single_number(nums) {{ let r=0; for (const x of nums) r ^= x; return r{a}; }}\n"


def _ts_single(wrong):
    a = " + 1" if wrong else ""
    return f"function single_number(nums: number[]): number {{ let r=0; for (const x of nums) r ^= x; return r{a}; }}\n"


def _java_single(wrong):
    a = " + 1" if wrong else ""
    return f"class Solution {{ public int single_number(int[] nums) {{ int r=0; for (int x: nums) r ^= x; return r{a}; }} }}\n"


def _cpp_single(wrong):
    a = " + 1" if wrong else ""
    return f"class Solution {{ public: int single_number(std::vector<int> nums) {{ int r=0; for (int x: nums) r ^= x; return r{a}; }} }};\n"


def _csharp_single(wrong):
    a = " + 1" if wrong else ""
    return f"class Solution {{ public static int single_number(int[] nums) {{ int r=0; foreach (int x in nums) r ^= x; return r{a}; }} }}\n"


def _perl_single(wrong):
    # Perl's bitwise ^ defaults to unsigned 64-bit semantics, wrapping
    # negative operands (e.g. XOR-ing a -14 produces 18446744073709551602,
    # not -14) -- `use integer` forces signed native-integer arithmetic for
    # the bitwise ops, found via a real test failure, not assumed upfront.
    a = " + 1" if wrong else ""
    return f"use integer;\nsub single_number {{ my ($nums) = @_; my $r=0; foreach my $x (@$nums) {{ $r ^= $x; }} return $r{a}; }}\n"


def _c_single(wrong):
    a = " + 1" if wrong else ""
    return f"int single_number(AtlasIntArray nums) {{ int r=0; for (int i=0;i<nums.size;i++) r ^= nums.data[i]; return r{a}; }}\n"


def _rust_single(wrong):
    a = " + 1" if wrong else ""
    return f"fn single_number(nums: Vec<i32>) -> i32 {{ let mut r=0; for x in nums.iter() {{ r ^= x; }} r{a} }}\n"


# ── number-of-1-bits ─────────────────────────────────────────────────────────
def _js_popcount(wrong):
    a = " + 1" if wrong else ""
    return (
        "function hamming_weight(n) {\n"
        "    let count = 0; let x = n >>> 0;\n"
        "    while (x !== 0) { count += x & 1; x = x >>> 1; }\n"
        f"    return count{a};\n"
        "}\n"
    )


def _ts_popcount(wrong):
    a = " + 1" if wrong else ""
    return (
        "function hamming_weight(n: number): number {\n"
        "    let count = 0; let x = n >>> 0;\n"
        "    while (x !== 0) { count += x & 1; x = x >>> 1; }\n"
        f"    return count{a};\n"
        "}\n"
    )


def _java_popcount(wrong):
    a = " + 1" if wrong else ""
    return f"class Solution {{ public int hamming_weight(int n) {{ return Integer.bitCount(n){a}; }} }}\n"


def _cpp_popcount(wrong):
    a = " + 1" if wrong else ""
    return f"class Solution {{ public: int hamming_weight(int n) {{ return __builtin_popcount((unsigned int)n){a}; }} }};\n"


def _csharp_popcount(wrong):
    a = " + 1" if wrong else ""
    return f"class Solution {{ public static int hamming_weight(int n) {{ return System.Numerics.BitOperations.PopCount((uint)n){a}; }} }}\n"


def _perl_popcount(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub hamming_weight {\n"
        "    my ($n) = @_;\n"
        "    my $x = $n & 0xFFFFFFFF;\n"
        "    my $count = 0;\n"
        "    while ($x != 0) { $count += $x & 1; $x = $x >> 1; }\n"
        f"    return $count{a};\n"
        "}\n"
    )


def _c_popcount(wrong):
    a = " + 1" if wrong else ""
    return f"int hamming_weight(int n) {{ return __builtin_popcount((unsigned int)n){a}; }}\n"


def _rust_popcount(wrong):
    a = " + 1" if wrong else ""
    return f"fn hamming_weight(n: i32) -> i32 {{ (n as u32).count_ones() as i32{a} }}\n"


# ── power-of-two ─────────────────────────────────────────────────────────────
def _js_pow2(wrong):
    ret = "!(n > 0 && (n & (n - 1)) === 0)" if wrong else "n > 0 && (n & (n - 1)) === 0"
    return f"function is_power_of_two(n) {{ return {ret}; }}\n"


def _ts_pow2(wrong):
    ret = "!(n > 0 && (n & (n - 1)) === 0)" if wrong else "n > 0 && (n & (n - 1)) === 0"
    return f"function is_power_of_two(n: number): boolean {{ return {ret}; }}\n"


def _java_pow2(wrong):
    ret = "!(n > 0 && (n & (n - 1)) == 0)" if wrong else "n > 0 && (n & (n - 1)) == 0"
    return f"class Solution {{ public boolean is_power_of_two(int n) {{ return {ret}; }} }}\n"


def _cpp_pow2(wrong):
    ret = "!(n > 0 && (n & (n - 1)) == 0)" if wrong else "n > 0 && (n & (n - 1)) == 0"
    return f"class Solution {{ public: bool is_power_of_two(int n) {{ return {ret}; }} }};\n"


def _csharp_pow2(wrong):
    ret = "!(n > 0 && (n & (n - 1)) == 0)" if wrong else "n > 0 && (n & (n - 1)) == 0"
    return f"class Solution {{ public static bool is_power_of_two(int n) {{ return {ret}; }} }}\n"


def _perl_pow2(wrong):
    ret = "!($n > 0 && ($n & ($n - 1)) == 0)" if wrong else "$n > 0 && ($n & ($n - 1)) == 0"
    return f"sub is_power_of_two {{ my ($n) = @_; return ({ret}) ? 1 : 0; }}\n"


def _c_pow2(wrong):
    ret = "!(n > 0 && (n & (n - 1)) == 0)" if wrong else "n > 0 && (n & (n - 1)) == 0"
    return f"int is_power_of_two(int n) {{ return {ret}; }}\n"


def _rust_pow2(wrong):
    ret = "!(n > 0 && (n & (n - 1)) == 0)" if wrong else "n > 0 && (n & (n - 1)) == 0"
    return f"fn is_power_of_two(n: i32) -> bool {{ {ret} }}\n"


# ── hamming-distance ─────────────────────────────────────────────────────────
def _js_hamdist(wrong):
    a = " + 1" if wrong else ""
    return (
        "function hamming_distance(x, y) {\n"
        "    let v = (x ^ y) >>> 0; let count = 0;\n"
        "    while (v !== 0) { count += v & 1; v = v >>> 1; }\n"
        f"    return count{a};\n"
        "}\n"
    )


def _ts_hamdist(wrong):
    a = " + 1" if wrong else ""
    return (
        "function hamming_distance(x: number, y: number): number {\n"
        "    let v = (x ^ y) >>> 0; let count = 0;\n"
        "    while (v !== 0) { count += v & 1; v = v >>> 1; }\n"
        f"    return count{a};\n"
        "}\n"
    )


def _java_hamdist(wrong):
    a = " + 1" if wrong else ""
    return f"class Solution {{ public int hamming_distance(int x, int y) {{ return Integer.bitCount(x ^ y){a}; }} }}\n"


def _cpp_hamdist(wrong):
    a = " + 1" if wrong else ""
    return f"class Solution {{ public: int hamming_distance(int x, int y) {{ return __builtin_popcount((unsigned int)(x ^ y)){a}; }} }};\n"


def _csharp_hamdist(wrong):
    a = " + 1" if wrong else ""
    return f"class Solution {{ public static int hamming_distance(int x, int y) {{ return System.Numerics.BitOperations.PopCount((uint)(x ^ y)){a}; }} }}\n"


def _perl_hamdist(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub hamming_distance {\n"
        "    my ($x, $y) = @_;\n"
        "    my $v = ($x ^ $y) & 0xFFFFFFFF;\n"
        "    my $count = 0;\n"
        "    while ($v != 0) { $count += $v & 1; $v = $v >> 1; }\n"
        f"    return $count{a};\n"
        "}\n"
    )


def _c_hamdist(wrong):
    a = " + 1" if wrong else ""
    return f"int hamming_distance(int x, int y) {{ return __builtin_popcount((unsigned int)(x ^ y)){a}; }}\n"


def _rust_hamdist(wrong):
    a = " + 1" if wrong else ""
    return f"fn hamming_distance(x: i32, y: i32) -> i32 {{ ((x ^ y) as u32).count_ones() as i32{a} }}\n"


# ── move-zeroes ──────────────────────────────────────────────────────────────
def _js_move_zeroes(wrong):
    op = "===" if wrong else "!=="
    return (
        "function move_zeroes(nums) {\n"
        "    let j = 0;\n"
        f"    for (let i=0;i<nums.length;i++) {{ if (nums[i] {op} 0) {{ const t=nums[j]; nums[j]=nums[i]; nums[i]=t; j++; }} }}\n"
        "    return nums;\n"
        "}\n"
    )


def _ts_move_zeroes(wrong):
    op = "===" if wrong else "!=="
    return (
        "function move_zeroes(nums: number[]): number[] {\n"
        "    let j = 0;\n"
        f"    for (let i=0;i<nums.length;i++) {{ if (nums[i] {op} 0) {{ const t=nums[j]; nums[j]=nums[i]; nums[i]=t; j++; }} }}\n"
        "    return nums;\n"
        "}\n"
    )


def _java_move_zeroes(wrong):
    op = "==" if wrong else "!="
    return (
        "class Solution {\n"
        "    public int[] move_zeroes(int[] nums) {\n"
        "        int j = 0;\n"
        f"        for (int i=0;i<nums.length;i++) {{ if (nums[i] {op} 0) {{ int t=nums[j]; nums[j]=nums[i]; nums[i]=t; j++; }} }}\n"
        "        return nums;\n"
        "    }\n"
        "}\n"
    )


def _cpp_move_zeroes(wrong):
    op = "==" if wrong else "!="
    return (
        "class Solution {\n"
        "public:\n"
        "    std::vector<int> move_zeroes(std::vector<int> nums) {\n"
        "        int j = 0;\n"
        f"        for (int i=0;i<(int)nums.size();i++) {{ if (nums[i] {op} 0) {{ std::swap(nums[j], nums[i]); j++; }} }}\n"
        "        return nums;\n"
        "    }\n"
        "};\n"
    )


def _csharp_move_zeroes(wrong):
    op = "==" if wrong else "!="
    return (
        "class Solution {\n"
        "    public static int[] move_zeroes(int[] nums) {\n"
        "        int j = 0;\n"
        f"        for (int i=0;i<nums.Length;i++) {{ if (nums[i] {op} 0) {{ int t=nums[j]; nums[j]=nums[i]; nums[i]=t; j++; }} }}\n"
        "        return nums;\n"
        "    }\n"
        "}\n"
    )


def _perl_move_zeroes(wrong):
    op = "==" if wrong else "!="
    return (
        "sub move_zeroes {\n"
        "    my ($nums) = @_;\n"
        "    my $j = 0;\n"
        f"    for (my $i=0;$i<scalar(@$nums);$i++) {{ if ($nums->[$i] {op} 0) {{ my $t=$nums->[$j]; $nums->[$j]=$nums->[$i]; $nums->[$i]=$t; $j++; }} }}\n"
        "    return $nums;\n"
        "}\n"
    )


def _c_move_zeroes(wrong):
    op = "==" if wrong else "!="
    return (
        "AtlasIntArray move_zeroes(AtlasIntArray nums) {\n"
        "    int j = 0;\n"
        f"    for (int i=0;i<nums.size;i++) {{ if (nums.data[i] {op} 0) {{ int t=nums.data[j]; nums.data[j]=nums.data[i]; nums.data[i]=t; j++; }} }}\n"
        "    return nums;\n"
        "}\n"
    )


def _rust_move_zeroes(wrong):
    op = "== 0" if wrong else "!= 0"
    return (
        "fn move_zeroes(mut nums: Vec<i32>) -> Vec<i32> {\n"
        "    let mut j = 0;\n"
        f"    for i in 0..nums.len() {{ if nums[i] {op} {{ nums.swap(i, j); j += 1; }} }}\n"
        "    nums\n"
        "}\n"
    )


# ── majority-element ─────────────────────────────────────────────────────────
def _js_majority(wrong):
    a = " + 1" if wrong else ""
    return (
        "function majority_element(nums) {\n"
        "    let count = 0, candidate = 0;\n"
        "    for (const x of nums) { if (count === 0) candidate = x; count += (x === candidate) ? 1 : -1; }\n"
        f"    return candidate{a};\n"
        "}\n"
    )


def _ts_majority(wrong):
    a = " + 1" if wrong else ""
    return (
        "function majority_element(nums: number[]): number {\n"
        "    let count = 0, candidate = 0;\n"
        "    for (const x of nums) { if (count === 0) candidate = x; count += (x === candidate) ? 1 : -1; }\n"
        f"    return candidate{a};\n"
        "}\n"
    )


def _java_majority(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public int majority_element(int[] nums) {\n"
        "        int count=0, candidate=0;\n"
        "        for (int x: nums) { if (count==0) candidate=x; count += (x==candidate) ? 1 : -1; }\n"
        f"        return candidate{a};\n"
        "    }\n"
        "}\n"
    )


def _cpp_majority(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "public:\n"
        "    int majority_element(std::vector<int> nums) {\n"
        "        int count=0, candidate=0;\n"
        "        for (int x: nums) { if (count==0) candidate=x; count += (x==candidate) ? 1 : -1; }\n"
        f"        return candidate{a};\n"
        "    }\n"
        "};\n"
    )


def _csharp_majority(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public static int majority_element(int[] nums) {\n"
        "        int count=0, candidate=0;\n"
        "        foreach (int x in nums) { if (count==0) candidate=x; count += (x==candidate) ? 1 : -1; }\n"
        f"        return candidate{a};\n"
        "    }\n"
        "}\n"
    )


def _perl_majority(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub majority_element {\n"
        "    my ($nums) = @_;\n"
        "    my $count = 0; my $candidate = 0;\n"
        "    foreach my $x (@$nums) { if ($count == 0) { $candidate = $x; } $count += ($x == $candidate) ? 1 : -1; }\n"
        f"    return $candidate{a};\n"
        "}\n"
    )


def _c_majority(wrong):
    a = " + 1" if wrong else ""
    return (
        "int majority_element(AtlasIntArray nums) {\n"
        "    int count=0, candidate=0;\n"
        "    for (int i=0;i<nums.size;i++) { if (count==0) candidate=nums.data[i]; count += (nums.data[i]==candidate) ? 1 : -1; }\n"
        f"    return candidate{a};\n"
        "}\n"
    )


def _rust_majority(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn majority_element(nums: Vec<i32>) -> i32 {\n"
        "    let mut count = 0; let mut candidate = 0;\n"
        "    for x in nums.iter() { if count == 0 { candidate = *x; } count += if *x == candidate { 1 } else { -1 }; }\n"
        f"    candidate{a}\n"
        "}\n"
    )


_BUILDERS = {
    "valid-parentheses": {"javascript": _js_valid_paren, "typescript": _ts_valid_paren, "java": _java_valid_paren, "cpp": _cpp_valid_paren,
                          "csharp": _csharp_valid_paren, "perl": _perl_valid_paren, "c": _c_valid_paren, "rust": _rust_valid_paren},
    "valid-anagram": {"javascript": _js_valid_anagram, "typescript": _ts_valid_anagram, "java": _java_valid_anagram, "cpp": _cpp_valid_anagram,
                      "csharp": _csharp_valid_anagram, "perl": _perl_valid_anagram, "c": _c_valid_anagram, "rust": _rust_valid_anagram},
    "missing-number": {"javascript": _js_missing, "typescript": _ts_missing, "java": _java_missing, "cpp": _cpp_missing,
                       "csharp": _csharp_missing, "perl": _perl_missing, "c": _c_missing, "rust": _rust_missing},
    "single-number": {"javascript": _js_single, "typescript": _ts_single, "java": _java_single, "cpp": _cpp_single,
                      "csharp": _csharp_single, "perl": _perl_single, "c": _c_single, "rust": _rust_single},
    "number-of-1-bits": {"javascript": _js_popcount, "typescript": _ts_popcount, "java": _java_popcount, "cpp": _cpp_popcount,
                         "csharp": _csharp_popcount, "perl": _perl_popcount, "c": _c_popcount, "rust": _rust_popcount},
    "power-of-two": {"javascript": _js_pow2, "typescript": _ts_pow2, "java": _java_pow2, "cpp": _cpp_pow2,
                     "csharp": _csharp_pow2, "perl": _perl_pow2, "c": _c_pow2, "rust": _rust_pow2},
    "hamming-distance": {"javascript": _js_hamdist, "typescript": _ts_hamdist, "java": _java_hamdist, "cpp": _cpp_hamdist,
                         "csharp": _csharp_hamdist, "perl": _perl_hamdist, "c": _c_hamdist, "rust": _rust_hamdist},
    "move-zeroes": {"javascript": _js_move_zeroes, "typescript": _ts_move_zeroes, "java": _java_move_zeroes, "cpp": _cpp_move_zeroes,
                    "csharp": _csharp_move_zeroes, "perl": _perl_move_zeroes, "c": _c_move_zeroes, "rust": _rust_move_zeroes},
    "majority-element": {"javascript": _js_majority, "typescript": _ts_majority, "java": _java_majority, "cpp": _cpp_majority,
                         "csharp": _csharp_majority, "perl": _perl_majority, "c": _c_majority, "rust": _rust_majority},
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
            print(f"[{status}] {lang:10s} {pid:20s} {r['outcome']:18s} {r['detail'][:130]}", flush=True)
            if r["outcome"] == "verified":
                ledger.record_cell(con, problem_id=pid, language=lang, mode="function",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=f"{lang}-bit-misc-v1", contract_version=cv, test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
