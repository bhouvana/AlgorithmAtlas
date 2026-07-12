"""Scales the next 11 problems (Function Mode) across the 8 original
working languages: majority-element-ii, manacher, matrix-chain-multiplication,
maximum-xor-of-two-numbers, miller-rabin, minimum-window-substring-length,
modular-exponentiation, palindrome-partition, palindrome-partitioning,
palindrome-subsequence, partition-equal-subset-sum.
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


# ── majority-element-ii (Boyer-Moore n/3, sorted ascending output) ─────────
def _js_majii(wrong):
    incr = ".map(x => x + 1)" if wrong else ""
    return (f"function majority_element_ii(nums) {{\n"
            f"    let c1=null, c2=null, cnt1=0, cnt2=0;\n"
            f"    for (const x of nums) {{\n"
            f"        if (c1===x) cnt1++;\n"
            f"        else if (c2===x) cnt2++;\n"
            f"        else if (cnt1===0) {{ c1=x; cnt1=1; }}\n"
            f"        else if (cnt2===0) {{ c2=x; cnt2=1; }}\n"
            f"        else {{ cnt1--; cnt2--; }}\n"
            f"    }}\n"
            f"    cnt1=0; cnt2=0;\n"
            f"    for (const x of nums) {{ if (x===c1) cnt1++; else if (x===c2) cnt2++; }}\n"
            f"    const out=[];\n"
            f"    if (cnt1>Math.floor(nums.length/3)) out.push(c1);\n"
            f"    if (cnt2>Math.floor(nums.length/3)) out.push(c2);\n"
            f"    out.sort((a,b)=>a-b);\n"
            f"    return out{incr};\n}}\n")


def _ts_majii(wrong):
    incr = ".map(x => x + 1)" if wrong else ""
    return (f"function majority_element_ii(nums: number[]): number[] {{\n"
            f"    let c1: number|null=null, c2: number|null=null, cnt1=0, cnt2=0;\n"
            f"    for (const x of nums) {{\n"
            f"        if (c1===x) cnt1++;\n"
            f"        else if (c2===x) cnt2++;\n"
            f"        else if (cnt1===0) {{ c1=x; cnt1=1; }}\n"
            f"        else if (cnt2===0) {{ c2=x; cnt2=1; }}\n"
            f"        else {{ cnt1--; cnt2--; }}\n"
            f"    }}\n"
            f"    cnt1=0; cnt2=0;\n"
            f"    for (const x of nums) {{ if (x===c1) cnt1++; else if (x===c2) cnt2++; }}\n"
            f"    const out: number[]=[];\n"
            f"    if (cnt1>Math.floor(nums.length/3)) out.push(c1 as number);\n"
            f"    if (cnt2>Math.floor(nums.length/3)) out.push(c2 as number);\n"
            f"    out.sort((a,b)=>a-b);\n"
            f"    return out{incr};\n}}\n")


def _java_majii(wrong):
    incr = "for (int i=0;i<out.length;i++) out[i]++;\n        " if wrong else ""
    return (f"class Solution {{ public int[] majority_element_ii(int[] nums) {{\n"
            f"    Integer c1=null, c2=null; int cnt1=0, cnt2=0;\n"
            f"    for (int x: nums) {{\n"
            f"        if (c1!=null && c1==x) cnt1++;\n"
            f"        else if (c2!=null && c2==x) cnt2++;\n"
            f"        else if (cnt1==0) {{ c1=x; cnt1=1; }}\n"
            f"        else if (cnt2==0) {{ c2=x; cnt2=1; }}\n"
            f"        else {{ cnt1--; cnt2--; }}\n"
            f"    }}\n"
            f"    cnt1=0; cnt2=0;\n"
            f"    for (int x: nums) {{ if (c1!=null && x==c1) cnt1++; else if (c2!=null && x==c2) cnt2++; }}\n"
            f"    java.util.List<Integer> list = new java.util.ArrayList<>();\n"
            f"    if (cnt1>nums.length/3) list.add(c1);\n"
            f"    if (cnt2>nums.length/3) list.add(c2);\n"
            f"    java.util.Collections.sort(list);\n"
            f"    int[] out = new int[list.size()]; for (int i=0;i<out.length;i++) out[i]=list.get(i);\n"
            f"        {incr}return out;\n}} }}\n")


def _cpp_majii(wrong):
    incr = "for (auto& x: out) x++;\n    " if wrong else ""
    return (f"class Solution {{ public: std::vector<int> majority_element_ii(std::vector<int> nums) {{\n"
            f"    long c1=0, c2=0; int cnt1=0, cnt2=0; bool has1=false, has2=false;\n"
            f"    for (int x: nums) {{\n"
            f"        if (has1 && c1==x) cnt1++;\n"
            f"        else if (has2 && c2==x) cnt2++;\n"
            f"        else if (cnt1==0) {{ c1=x; cnt1=1; has1=true; }}\n"
            f"        else if (cnt2==0) {{ c2=x; cnt2=1; has2=true; }}\n"
            f"        else {{ cnt1--; cnt2--; }}\n"
            f"    }}\n"
            f"    cnt1=0; cnt2=0;\n"
            f"    for (int x: nums) {{ if (has1 && x==c1) cnt1++; else if (has2 && x==c2) cnt2++; }}\n"
            f"    std::vector<int> out;\n"
            f"    if (cnt1>(int)nums.size()/3) out.push_back((int)c1);\n"
            f"    if (cnt2>(int)nums.size()/3) out.push_back((int)c2);\n"
            f"    std::sort(out.begin(), out.end());\n"
            f"    {incr}return out;\n}} }};\n")


def _csharp_majii(wrong):
    incr = "for (int i=0;i<outArr.Length;i++) outArr[i]++;\n        " if wrong else ""
    return (f"class Solution {{ public static int[] majority_element_ii(int[] nums) {{\n"
            f"    long c1=0, c2=0; int cnt1=0, cnt2=0; bool has1=false, has2=false;\n"
            f"    foreach (int x in nums) {{\n"
            f"        if (has1 && c1==x) cnt1++;\n"
            f"        else if (has2 && c2==x) cnt2++;\n"
            f"        else if (cnt1==0) {{ c1=x; cnt1=1; has1=true; }}\n"
            f"        else if (cnt2==0) {{ c2=x; cnt2=1; has2=true; }}\n"
            f"        else {{ cnt1--; cnt2--; }}\n"
            f"    }}\n"
            f"    cnt1=0; cnt2=0;\n"
            f"    foreach (int x in nums) {{ if (has1 && x==c1) cnt1++; else if (has2 && x==c2) cnt2++; }}\n"
            f"    var list = new System.Collections.Generic.List<int>();\n"
            f"    if (cnt1>nums.Length/3) list.Add((int)c1);\n"
            f"    if (cnt2>nums.Length/3) list.Add((int)c2);\n"
            f"    list.Sort();\n"
            f"    int[] outArr = list.ToArray();\n"
            f"        {incr}return outArr;\n}} }}\n")


def _perl_majii(wrong):
    incr = "@out = map { $_ + 1 } @out;\n    " if wrong else ""
    return (f"sub majority_element_ii {{\n"
            f"    my ($nums) = @_;\n"
            f"    my $c1; my $c2; my $cnt1=0; my $cnt2=0;\n"
            f"    foreach my $x (@$nums) {{\n"
            f"        if (defined($c1) && $c1==$x) {{ $cnt1++; }}\n"
            f"        elsif (defined($c2) && $c2==$x) {{ $cnt2++; }}\n"
            f"        elsif ($cnt1==0) {{ $c1=$x; $cnt1=1; }}\n"
            f"        elsif ($cnt2==0) {{ $c2=$x; $cnt2=1; }}\n"
            f"        else {{ $cnt1--; $cnt2--; }}\n"
            f"    }}\n"
            f"    $cnt1=0; $cnt2=0;\n"
            f"    foreach my $x (@$nums) {{ if (defined($c1) && $x==$c1) {{ $cnt1++; }} elsif (defined($c2) && $x==$c2) {{ $cnt2++; }} }}\n"
            f"    my @out;\n"
            f"    push @out, $c1 if $cnt1>int(scalar(@$nums)/3);\n"
            f"    push @out, $c2 if $cnt2>int(scalar(@$nums)/3);\n"
            f"    @out = sort {{ $a <=> $b }} @out;\n"
            f"    {incr}return \\@out;\n}}\n")


def _c_majii(wrong):
    incr = "for (int i=0;i<oc;i++) out[i]++;\n    " if wrong else ""
    return (f"int cmp_asc_int(const void* a, const void* b) {{ return *(const int*)a - *(const int*)b; }}\n"
            f"AtlasIntArray majority_element_ii(AtlasIntArray nums) {{\n"
            f"    long c1=0, c2=0; int cnt1=0, cnt2=0; int has1=0, has2=0;\n"
            f"    for (int i=0;i<nums.size;i++) {{\n"
            f"        int x=nums.data[i];\n"
            f"        if (has1 && c1==x) cnt1++;\n"
            f"        else if (has2 && c2==x) cnt2++;\n"
            f"        else if (cnt1==0) {{ c1=x; cnt1=1; has1=1; }}\n"
            f"        else if (cnt2==0) {{ c2=x; cnt2=1; has2=1; }}\n"
            f"        else {{ cnt1--; cnt2--; }}\n"
            f"    }}\n"
            f"    cnt1=0; cnt2=0;\n"
            f"    for (int i=0;i<nums.size;i++) {{ int x=nums.data[i]; if (has1 && x==c1) cnt1++; else if (has2 && x==c2) cnt2++; }}\n"
            f"    int* out = (int*)malloc(sizeof(int)*2); int oc=0;\n"
            f"    if (cnt1>nums.size/3) out[oc++]=(int)c1;\n"
            f"    if (cnt2>nums.size/3) out[oc++]=(int)c2;\n"
            f"    qsort(out, oc, sizeof(int), cmp_asc_int);\n"
            f"    {incr}AtlasIntArray result; result.size=oc; result.data=out;\n"
            f"    return result;\n}}\n")


def _rust_majii(wrong):
    incr = "for x in out.iter_mut() { *x += 1; }\n    " if wrong else ""
    return (f"fn majority_element_ii(nums: Vec<i32>) -> Vec<i32> {{\n"
            f"    let mut c1=0i32; let mut c2=0i32; let mut cnt1=0i32; let mut cnt2=0i32;\n"
            f"    let mut has1=false; let mut has2=false;\n"
            f"    for &x in nums.iter() {{\n"
            f"        if has1 && c1==x {{ cnt1+=1; }}\n"
            f"        else if has2 && c2==x {{ cnt2+=1; }}\n"
            f"        else if cnt1==0 {{ c1=x; cnt1=1; has1=true; }}\n"
            f"        else if cnt2==0 {{ c2=x; cnt2=1; has2=true; }}\n"
            f"        else {{ cnt1-=1; cnt2-=1; }}\n"
            f"    }}\n"
            f"    cnt1=0; cnt2=0;\n"
            f"    for &x in nums.iter() {{ if has1 && x==c1 {{ cnt1+=1; }} else if has2 && x==c2 {{ cnt2+=1; }} }}\n"
            f"    let mut out: Vec<i32> = Vec::new();\n"
            f"    if cnt1 > (nums.len() as i32)/3 {{ out.push(c1); }}\n"
            f"    if cnt2 > (nums.len() as i32)/3 {{ out.push(c2); }}\n"
            f"    out.sort();\n"
            f"    {incr}out\n}}\n")


# ── manacher (count palindromic substrings, O(n^2) expand-around-center) ──
def _js_manacher(wrong):
    a = " + 1" if wrong else ""
    return (f"function count_palindromic_substrings(s) {{\n"
            f"    let count=0;\n"
            f"    function expand(l,r) {{ let c=0; while (l>=0 && r<s.length && s[l]===s[r]) {{ c++; l--; r++; }} return c; }}\n"
            f"    for (let i=0;i<s.length;i++) {{ count+=expand(i,i); count+=expand(i,i+1); }}\n"
            f"    return count{a};\n}}\n")


def _ts_manacher(wrong):
    a = " + 1" if wrong else ""
    return (f"function count_palindromic_substrings(s: string): number {{\n"
            f"    let count=0;\n"
            f"    function expand(l: number,r: number): number {{ let c=0; while (l>=0 && r<s.length && s[l]===s[r]) {{ c++; l--; r++; }} return c; }}\n"
            f"    for (let i=0;i<s.length;i++) {{ count+=expand(i,i); count+=expand(i,i+1); }}\n"
            f"    return count{a};\n}}\n")


def _java_manacher(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int count_palindromic_substrings(String s) {{\n"
            f"    int count=0;\n"
            f"    for (int i=0;i<s.length();i++) {{ count+=expand(s,i,i); count+=expand(s,i,i+1); }}\n"
            f"    return count{a};\n}}\n"
            f"int expand(String s, int l, int r) {{ int c=0; while (l>=0 && r<s.length() && s.charAt(l)==s.charAt(r)) {{ c++; l--; r++; }} return c; }} }}\n")


def _cpp_manacher(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int count_palindromic_substrings(std::string s) {{\n"
            f"    int count=0;\n"
            f"    for (int i=0;i<(int)s.size();i++) {{ count+=expand(s,i,i); count+=expand(s,i,i+1); }}\n"
            f"    return count{a};\n}}\n"
            f"int expand(std::string& s, int l, int r) {{ int c=0; while (l>=0 && r<(int)s.size() && s[l]==s[r]) {{ c++; l--; r++; }} return c; }} }};\n")


def _csharp_manacher(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int count_palindromic_substrings(string s) {{\n"
            f"    int count=0;\n"
            f"    for (int i=0;i<s.Length;i++) {{ count+=Expand(s,i,i); count+=Expand(s,i,i+1); }}\n"
            f"    return count{a};\n}}\n"
            f"static int Expand(string s, int l, int r) {{ int c=0; while (l>=0 && r<s.Length && s[l]==s[r]) {{ c++; l--; r++; }} return c; }} }}\n")


def _perl_manacher(wrong):
    a = " + 1" if wrong else ""
    return (f"sub expand_manacher {{\n"
            f"    my ($s, $l, $r) = @_;\n"
            f"    my $c=0;\n"
            f"    while ($l>=0 && $r<length($s) && substr($s,$l,1) eq substr($s,$r,1)) {{ $c++; $l--; $r++; }}\n"
            f"    return $c;\n}}\n"
            f"sub count_palindromic_substrings {{\n"
            f"    my ($s) = @_;\n"
            f"    my $count=0;\n"
            f"    for (my $i=0;$i<length($s);$i++) {{ $count+=expand_manacher($s,$i,$i); $count+=expand_manacher($s,$i,$i+1); }}\n"
            f"    return $count{a};\n}}\n")


def _c_manacher(wrong):
    a = " + 1" if wrong else ""
    return (f"int expand_manacher(char* s, int n, int l, int r) {{\n"
            f"    int c=0;\n"
            f"    while (l>=0 && r<n && s[l]==s[r]) {{ c++; l--; r++; }}\n"
            f"    return c;\n}}\n"
            f"int count_palindromic_substrings(char* s) {{\n"
            f"    int n = strlen(s); int count=0;\n"
            f"    for (int i=0;i<n;i++) {{ count+=expand_manacher(s,n,i,i); count+=expand_manacher(s,n,i,i+1); }}\n"
            f"    return count{a};\n}}\n")


def _rust_manacher(wrong):
    a = " + 1" if wrong else ""
    return (f"fn expand_manacher(s: &Vec<char>, mut l: i32, mut r: i32) -> i32 {{\n"
            f"    let mut c=0i32;\n"
            f"    while l>=0 && (r as usize)<s.len() && s[l as usize]==s[r as usize] {{ c+=1; l-=1; r+=1; }}\n"
            f"    c\n}}\n"
            f"fn count_palindromic_substrings(s: String) -> i32 {{\n"
            f"    let chars: Vec<char> = s.chars().collect();\n"
            f"    let mut count=0i32;\n"
            f"    for i in 0..chars.len() as i32 {{ count+=expand_manacher(&chars,i,i); count+=expand_manacher(&chars,i,i+1); }}\n"
            f"    count{a}\n}}\n")


# ── matrix-chain-multiplication (interval DP, dims array, max len=60) ──────
def _js_mcm(wrong):
    a = " + 1" if wrong else ""
    return (f"function matrix_chain_order(dims) {{\n"
            f"    const n = dims.length-1;\n"
            f"    const dp = Array.from({{length:n+1}}, () => new Array(n+1).fill(0));\n"
            f"    for (let len=2;len<=n;len++) {{\n"
            f"        for (let i=1;i+len-1<=n;i++) {{\n"
            f"            const j=i+len-1; dp[i][j]=Infinity;\n"
            f"            for (let k=i;k<j;k++) {{\n"
            f"                const cost=dp[i][k]+dp[k+1][j]+dims[i-1]*dims[k]*dims[j];\n"
            f"                if (cost<dp[i][j]) dp[i][j]=cost;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return dp[1][n]{a};\n}}\n")


def _ts_mcm(wrong):
    a = " + 1" if wrong else ""
    return (f"function matrix_chain_order(dims: number[]): number {{\n"
            f"    const n = dims.length-1;\n"
            f"    const dp: number[][] = Array.from({{length:n+1}}, () => new Array(n+1).fill(0));\n"
            f"    for (let len=2;len<=n;len++) {{\n"
            f"        for (let i=1;i+len-1<=n;i++) {{\n"
            f"            const j=i+len-1; dp[i][j]=Infinity;\n"
            f"            for (let k=i;k<j;k++) {{\n"
            f"                const cost=dp[i][k]+dp[k+1][j]+dims[i-1]*dims[k]*dims[j];\n"
            f"                if (cost<dp[i][j]) dp[i][j]=cost;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return dp[1][n]{a};\n}}\n")


def _java_mcm(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int matrix_chain_order(int[] dims) {{\n"
            f"    int n = dims.length-1;\n"
            f"    long[][] dp = new long[n+1][n+1];\n"
            f"    for (int len=2;len<=n;len++) {{\n"
            f"        for (int i=1;i+len-1<=n;i++) {{\n"
            f"            int j=i+len-1; dp[i][j]=Long.MAX_VALUE/2;\n"
            f"            for (int k=i;k<j;k++) {{\n"
            f"                long cost=dp[i][k]+dp[k+1][j]+(long)dims[i-1]*dims[k]*dims[j];\n"
            f"                if (cost<dp[i][j]) dp[i][j]=cost;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return (int)(dp[1][n]{a});\n}} }}\n")


def _cpp_mcm(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int matrix_chain_order(std::vector<int> dims) {{\n"
            f"    int n = dims.size()-1;\n"
            f"    std::vector<std::vector<long long>> dp(n+1, std::vector<long long>(n+1, 0));\n"
            f"    for (int len=2;len<=n;len++) {{\n"
            f"        for (int i=1;i+len-1<=n;i++) {{\n"
            f"            int j=i+len-1; dp[i][j]=LLONG_MAX/2;\n"
            f"            for (int k=i;k<j;k++) {{\n"
            f"                long long cost=dp[i][k]+dp[k+1][j]+(long long)dims[i-1]*dims[k]*dims[j];\n"
            f"                if (cost<dp[i][j]) dp[i][j]=cost;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return (int)(dp[1][n]{a});\n}} }};\n")


def _csharp_mcm(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int matrix_chain_order(int[] dims) {{\n"
            f"    int n = dims.Length-1;\n"
            f"    long[,] dp = new long[n+1,n+1];\n"
            f"    for (int len=2;len<=n;len++) {{\n"
            f"        for (int i=1;i+len-1<=n;i++) {{\n"
            f"            int j=i+len-1; dp[i,j]=long.MaxValue/2;\n"
            f"            for (int k=i;k<j;k++) {{\n"
            f"                long cost=dp[i,k]+dp[k+1,j]+(long)dims[i-1]*dims[k]*dims[j];\n"
            f"                if (cost<dp[i,j]) dp[i,j]=cost;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return (int)(dp[1,n]{a});\n}} }}\n")


def _perl_mcm(wrong):
    a = " + 1" if wrong else ""
    return (f"sub matrix_chain_order {{\n"
            f"    my ($dims) = @_;\n"
            f"    my $n = scalar(@$dims)-1;\n"
            f"    my @dp; for my $i (0..$n) {{ for my $j (0..$n) {{ $dp[$i][$j]=0; }} }}\n"
            f"    for (my $len=2;$len<=$n;$len++) {{\n"
            f"        for (my $i=1;$i+$len-1<=$n;$i++) {{\n"
            f"            my $j=$i+$len-1; $dp[$i][$j]=9**9**9;\n"
            f"            for (my $k=$i;$k<$j;$k++) {{\n"
            f"                my $cost=$dp[$i][$k]+$dp[$k+1][$j]+$dims->[$i-1]*$dims->[$k]*$dims->[$j];\n"
            f"                $dp[$i][$j]=$cost if $cost<$dp[$i][$j];\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return $dp[1][$n]{a};\n}}\n")


def _c_mcm(wrong):
    a = " + 1" if wrong else ""
    return (f"int matrix_chain_order(AtlasIntArray dims) {{\n"
            f"    int n = dims.size-1;\n"
            f"    long long** dp = (long long**)malloc(sizeof(long long*)*(n+1));\n"
            f"    for (int i=0;i<=n;i++) dp[i]=(long long*)calloc(n+1, sizeof(long long));\n"
            f"    for (int len=2;len<=n;len++) {{\n"
            f"        for (int i=1;i+len-1<=n;i++) {{\n"
            f"            int j=i+len-1; dp[i][j]=1000000000000LL;\n"
            f"            for (int k=i;k<j;k++) {{\n"
            f"                long long cost=dp[i][k]+dp[k+1][j]+(long long)dims.data[i-1]*dims.data[k]*dims.data[j];\n"
            f"                if (cost<dp[i][j]) dp[i][j]=cost;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    long long r=dp[1][n];\n"
            f"    for (int i=0;i<=n;i++) free(dp[i]);\n"
            f"    free(dp);\n"
            f"    return (int)(r{a});\n}}\n")


def _rust_mcm(wrong):
    a = " + 1" if wrong else ""
    return (f"fn matrix_chain_order(dims: Vec<i32>) -> i32 {{\n"
            f"    let n = dims.len()-1;\n"
            f"    let mut dp = vec![vec![0i64; n+1]; n+1];\n"
            f"    for len in 2..=n {{\n"
            f"        for i in 1..=(n-len+1) {{\n"
            f"            let j = i+len-1; dp[i][j]=i64::MAX/2;\n"
            f"            for k in i..j {{\n"
            f"                let cost = dp[i][k]+dp[k+1][j]+(dims[i-1] as i64)*(dims[k] as i64)*(dims[j] as i64);\n"
            f"                if cost<dp[i][j] {{ dp[i][j]=cost; }}\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    (dp[1][n]{a}) as i32\n}}\n")


# ── maximum-xor-of-two-numbers (O(n^2) brute force, max n=878) ─────────────
def _js_maxxor(wrong):
    a = " + 1" if wrong else ""
    return (f"function find_max_xor(nums) {{\n"
            f"    let best=0;\n"
            f"    for (let i=0;i<nums.length;i++) for (let j=i+1;j<nums.length;j++) {{\n"
            f"        const x=nums[i]^nums[j]; if (x>best) best=x;\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _ts_maxxor(wrong):
    a = " + 1" if wrong else ""
    return (f"function find_max_xor(nums: number[]): number {{\n"
            f"    let best=0;\n"
            f"    for (let i=0;i<nums.length;i++) for (let j=i+1;j<nums.length;j++) {{\n"
            f"        const x=nums[i]^nums[j]; if (x>best) best=x;\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _java_maxxor(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int find_max_xor(int[] nums) {{\n"
            f"    int best=0;\n"
            f"    for (int i=0;i<nums.length;i++) for (int j=i+1;j<nums.length;j++) {{\n"
            f"        int x=nums[i]^nums[j]; if (x>best) best=x;\n"
            f"    }}\n"
            f"    return best{a};\n}} }}\n")


def _cpp_maxxor(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int find_max_xor(std::vector<int> nums) {{\n"
            f"    int best=0;\n"
            f"    for (size_t i=0;i<nums.size();i++) for (size_t j=i+1;j<nums.size();j++) {{\n"
            f"        int x=nums[i]^nums[j]; if (x>best) best=x;\n"
            f"    }}\n"
            f"    return best{a};\n}} }};\n")


def _csharp_maxxor(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int find_max_xor(int[] nums) {{\n"
            f"    int best=0;\n"
            f"    for (int i=0;i<nums.Length;i++) for (int j=i+1;j<nums.Length;j++) {{\n"
            f"        int x=nums[i]^nums[j]; if (x>best) best=x;\n"
            f"    }}\n"
            f"    return best{a};\n}} }}\n")


def _perl_maxxor(wrong):
    a = " + 1" if wrong else ""
    return (f"sub find_max_xor {{\n"
            f"    my ($nums) = @_;\n"
            f"    my $best=0; my $n=scalar(@$nums);\n"
            f"    for (my $i=0;$i<$n;$i++) {{ for (my $j=$i+1;$j<$n;$j++) {{ my $x=$nums->[$i]^$nums->[$j]; $best=$x if $x>$best; }} }}\n"
            f"    return $best{a};\n}}\n")


def _c_maxxor(wrong):
    a = " + 1" if wrong else ""
    return (f"int find_max_xor(AtlasIntArray nums) {{\n"
            f"    int best=0;\n"
            f"    for (int i=0;i<nums.size;i++) for (int j=i+1;j<nums.size;j++) {{\n"
            f"        int x=nums.data[i]^nums.data[j]; if (x>best) best=x;\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _rust_maxxor(wrong):
    a = " + 1" if wrong else ""
    return (f"fn find_max_xor(nums: Vec<i32>) -> i32 {{\n"
            f"    let mut best=0i32;\n"
            f"    for i in 0..nums.len() {{ for j in (i+1)..nums.len() {{\n"
            f"        let x = nums[i]^nums[j]; if x>best {{ best=x; }}\n"
            f"    }} }}\n"
            f"    best{a}\n}}\n")


# ── miller-rabin (primality; deterministic trial division for correctness) ─
def _js_millerrabin(wrong):
    ret = "false" if wrong else "true"
    return (f"function miller_rabin(n) {{\n"
            f"    if (n<2) return false;\n"
            f"    if (n<4) return {ret};\n"
            f"    if (n%2===0) return false;\n"
            f"    for (let i=3;i*i<=n;i+=2) if (n%i===0) return false;\n"
            f"    return {ret};\n}}\n")


def _ts_millerrabin(wrong):
    ret = "false" if wrong else "true"
    return (f"function miller_rabin(n: number): boolean {{\n"
            f"    if (n<2) return false;\n"
            f"    if (n<4) return {ret};\n"
            f"    if (n%2===0) return false;\n"
            f"    for (let i=3;i*i<=n;i+=2) if (n%i===0) return false;\n"
            f"    return {ret};\n}}\n")


def _java_millerrabin(wrong):
    ret = "false" if wrong else "true"
    return (f"class Solution {{ public boolean miller_rabin(int n) {{\n"
            f"    if (n<2) return false;\n"
            f"    if (n<4) return {ret};\n"
            f"    if (n%2==0) return false;\n"
            f"    for (long i=3;i*i<=n;i+=2) if (n%i==0) return false;\n"
            f"    return {ret};\n}} }}\n")


def _cpp_millerrabin(wrong):
    ret = "false" if wrong else "true"
    return (f"class Solution {{ public: bool miller_rabin(int n) {{\n"
            f"    if (n<2) return false;\n"
            f"    if (n<4) return {ret};\n"
            f"    if (n%2==0) return false;\n"
            f"    for (long long i=3;i*i<=n;i+=2) if (n%i==0) return false;\n"
            f"    return {ret};\n}} }};\n")


def _csharp_millerrabin(wrong):
    ret = "false" if wrong else "true"
    return (f"class Solution {{ public static bool miller_rabin(int n) {{\n"
            f"    if (n<2) return false;\n"
            f"    if (n<4) return {ret};\n"
            f"    if (n%2==0) return false;\n"
            f"    for (long i=3;i*i<=n;i+=2) if (n%i==0) return false;\n"
            f"    return {ret};\n}} }}\n")


def _perl_millerrabin(wrong):
    ret = "0" if wrong else "1"
    return (f"sub miller_rabin {{\n"
            f"    my ($n) = @_;\n"
            f"    return 0 if $n<2;\n"
            f"    return {ret} if $n<4;\n"
            f"    return 0 if $n%2==0;\n"
            f"    for (my $i=3;$i*$i<=$n;$i+=2) {{ return 0 if $n%$i==0; }}\n"
            f"    return {ret};\n}}\n")


def _c_millerrabin(wrong):
    ret = "0" if wrong else "1"
    return (f"int miller_rabin(int n) {{\n"
            f"    if (n<2) return 0;\n"
            f"    if (n<4) return {ret};\n"
            f"    if (n%2==0) return 0;\n"
            f"    for (long long i=3;i*i<=n;i+=2) if (n%i==0) return 0;\n"
            f"    return {ret};\n}}\n")


def _rust_millerrabin(wrong):
    ret = "false" if wrong else "true"
    return (f"fn miller_rabin(n: i32) -> bool {{\n"
            f"    if n<2 {{ return false; }}\n"
            f"    if n<4 {{ return {ret}; }}\n"
            f"    if n%2==0 {{ return false; }}\n"
            f"    let mut i: i64=3;\n"
            f"    while i*i<=n as i64 {{ if (n as i64)%i==0 {{ return false; }} i+=2; }}\n"
            f"    {ret}\n}}\n")


# ── minimum-window-substring-length (sliding window, max n=31890, need O(n)) ─
def _js_minwin(wrong):
    a = " + 1" if wrong else ""
    return (f"function min_window_length(s, t) {{\n"
            f"    if (t.length===0 || s.length<t.length) return 0{a};\n"
            f"    const need={{}}; for (const ch of t) need[ch]=(need[ch]||0)+1;\n"
            f"    let required=Object.keys(need).length, formed=0;\n"
            f"    const window={{}};\n"
            f"    let left=0, best=Infinity;\n"
            f"    for (let right=0;right<s.length;right++) {{\n"
            f"        const ch=s[right]; window[ch]=(window[ch]||0)+1;\n"
            f"        if (need[ch]!==undefined && window[ch]===need[ch]) formed++;\n"
            f"        while (formed===required) {{\n"
            f"            best=Math.min(best, right-left+1);\n"
            f"            const lc=s[left]; window[lc]--;\n"
            f"            if (need[lc]!==undefined && window[lc]<need[lc]) formed--;\n"
            f"            left++;\n"
            f"        }}\n"
            f"    }}\n"
            f"    const r = best===Infinity?0:best;\n"
            f"    return r===0?r:r{a};\n}}\n")


def _ts_minwin(wrong):
    a = " + 1" if wrong else ""
    return (f"function min_window_length(s: string, t: string): number {{\n"
            f"    if (t.length===0 || s.length<t.length) return 0{a};\n"
            f"    const need: Record<string,number>={{}}; for (const ch of t) need[ch]=(need[ch]||0)+1;\n"
            f"    let required=Object.keys(need).length, formed=0;\n"
            f"    const window: Record<string,number>={{}};\n"
            f"    let left=0, best=Infinity;\n"
            f"    for (let right=0;right<s.length;right++) {{\n"
            f"        const ch=s[right]; window[ch]=(window[ch]||0)+1;\n"
            f"        if (need[ch]!==undefined && window[ch]===need[ch]) formed++;\n"
            f"        while (formed===required) {{\n"
            f"            best=Math.min(best, right-left+1);\n"
            f"            const lc=s[left]; window[lc]--;\n"
            f"            if (need[lc]!==undefined && window[lc]<need[lc]) formed--;\n"
            f"            left++;\n"
            f"        }}\n"
            f"    }}\n"
            f"    const r = best===Infinity?0:best;\n"
            f"    return r===0?r:r{a};\n}}\n")


def _java_minwin(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int min_window_length(String s, String t) {{\n"
            f"    if (t.length()==0 || s.length()<t.length()) return 0{a};\n"
            f"    java.util.Map<Character,Integer> need = new java.util.HashMap<>();\n"
            f"    for (char ch: t.toCharArray()) need.merge(ch,1,Integer::sum);\n"
            f"    int required=need.size(), formed=0;\n"
            f"    java.util.Map<Character,Integer> window = new java.util.HashMap<>();\n"
            f"    int left=0; int best=Integer.MAX_VALUE;\n"
            f"    for (int right=0;right<s.length();right++) {{\n"
            f"        char ch=s.charAt(right); window.merge(ch,1,Integer::sum);\n"
            f"        if (need.containsKey(ch) && window.get(ch).intValue()==need.get(ch).intValue()) formed++;\n"
            f"        while (formed==required) {{\n"
            f"            best=Math.min(best, right-left+1);\n"
            f"            char lc=s.charAt(left); window.put(lc, window.get(lc)-1);\n"
            f"            if (need.containsKey(lc) && window.get(lc)<need.get(lc)) formed--;\n"
            f"            left++;\n"
            f"        }}\n"
            f"    }}\n"
            f"    int r = best==Integer.MAX_VALUE?0:best;\n"
            f"    return r==0?r:r{a};\n}} }}\n")


def _cpp_minwin(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int min_window_length(std::string s, std::string t) {{\n"
            f"    if (t.empty() || s.size()<t.size()) return 0{a};\n"
            f"    std::unordered_map<char,int> need; for (char ch: t) need[ch]++;\n"
            f"    int required=need.size(), formed=0;\n"
            f"    std::unordered_map<char,int> window;\n"
            f"    int left=0, best=INT_MAX;\n"
            f"    for (int right=0;right<(int)s.size();right++) {{\n"
            f"        char ch=s[right]; window[ch]++;\n"
            f"        if (need.count(ch) && window[ch]==need[ch]) formed++;\n"
            f"        while (formed==required) {{\n"
            f"            best=std::min(best, right-left+1);\n"
            f"            char lc=s[left]; window[lc]--;\n"
            f"            if (need.count(lc) && window[lc]<need[lc]) formed--;\n"
            f"            left++;\n"
            f"        }}\n"
            f"    }}\n"
            f"    int r = best==INT_MAX?0:best;\n"
            f"    return r==0?r:r{a};\n}} }};\n")


def _csharp_minwin(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int min_window_length(string s, string t) {{\n"
            f"    if (t.Length==0 || s.Length<t.Length) return 0{a};\n"
            f"    var need = new System.Collections.Generic.Dictionary<char,int>();\n"
            f"    foreach (char ch in t) {{ if (!need.ContainsKey(ch)) need[ch]=0; need[ch]++; }}\n"
            f"    int required=need.Count, formed=0;\n"
            f"    var window = new System.Collections.Generic.Dictionary<char,int>();\n"
            f"    int left=0, best=int.MaxValue;\n"
            f"    for (int right=0;right<s.Length;right++) {{\n"
            f"        char ch=s[right]; if (!window.ContainsKey(ch)) window[ch]=0; window[ch]++;\n"
            f"        if (need.ContainsKey(ch) && window[ch]==need[ch]) formed++;\n"
            f"        while (formed==required) {{\n"
            f"            best=System.Math.Min(best, right-left+1);\n"
            f"            char lc=s[left]; window[lc]--;\n"
            f"            if (need.ContainsKey(lc) && window[lc]<need[lc]) formed--;\n"
            f"            left++;\n"
            f"        }}\n"
            f"    }}\n"
            f"    int r = best==int.MaxValue?0:best;\n"
            f"    return r==0?r:r{a};\n}} }}\n")


def _perl_minwin(wrong):
    a = " + 1" if wrong else ""
    return (f"sub min_window_length {{\n"
            f"    my ($s, $t) = @_;\n"
            f"    return (0{a}) if length($t)==0 || length($s)<length($t);\n"
            f"    my %need; foreach my $ch (split //, $t) {{ $need{{$ch}}++; }}\n"
            f"    my $required=scalar(keys %need); my $formed=0;\n"
            f"    my %window; my $left=0; my $best=9**9**9;\n"
            f"    my @schars = split //, $s;\n"
            f"    for (my $right=0;$right<scalar(@schars);$right++) {{\n"
            f"        my $ch=$schars[$right]; $window{{$ch}}++;\n"
            f"        if (exists $need{{$ch}} && $window{{$ch}}==$need{{$ch}}) {{ $formed++; }}\n"
            f"        while ($formed==$required) {{\n"
            f"            my $len=$right-$left+1; $best=$len if $len<$best;\n"
            f"            my $lc=$schars[$left]; $window{{$lc}}--;\n"
            f"            if (exists $need{{$lc}} && $window{{$lc}}<$need{{$lc}}) {{ $formed--; }}\n"
            f"            $left++;\n"
            f"        }}\n"
            f"    }}\n"
            f"    my $r = ($best==9**9**9)?0:$best;\n"
            f"    return ($r==0)?$r:$r{a};\n}}\n")


def _c_minwin(wrong):
    a = " + 1" if wrong else ""
    return (f"int min_window_length(char* s, char* t) {{\n"
            f"    int tn = strlen(t); int sn = strlen(s);\n"
            f"    if (tn==0 || sn<tn) return 0{a};\n"
            f"    int need[256]={{0}}; int required=0;\n"
            f"    for (int i=0;i<tn;i++) {{ if (need[(unsigned char)t[i]]==0) required++; need[(unsigned char)t[i]]++; }}\n"
            f"    int window[256]={{0}}; int formed=0; int left=0; int best=2147483647;\n"
            f"    for (int right=0;right<sn;right++) {{\n"
            f"        unsigned char ch=s[right]; window[ch]++;\n"
            f"        if (need[ch]>0 && window[ch]==need[ch]) formed++;\n"
            f"        while (formed==required) {{\n"
            f"            int len=right-left+1; if (len<best) best=len;\n"
            f"            unsigned char lc=s[left]; window[lc]--;\n"
            f"            if (need[lc]>0 && window[lc]<need[lc]) formed--;\n"
            f"            left++;\n"
            f"        }}\n"
            f"    }}\n"
            f"    int r = (best==2147483647)?0:best;\n"
            f"    return r==0?r:r{a};\n}}\n")


def _rust_minwin(wrong):
    a = " + 1" if wrong else ""
    return (f"fn min_window_length(s: String, t: String) -> i32 {{\n"
            f"    if t.is_empty() || s.len()<t.len() {{ return 0{a}; }}\n"
            f"    let sb: Vec<u8> = s.bytes().collect(); let tb: Vec<u8> = t.bytes().collect();\n"
            f"    let mut need = [0i32; 256];\n"
            f"    let mut required = 0i32;\n"
            f"    for &b in tb.iter() {{ if need[b as usize]==0 {{ required+=1; }} need[b as usize]+=1; }}\n"
            f"    let mut window = [0i32; 256]; let mut formed=0i32; let mut left=0i32; let mut best=i32::MAX;\n"
            f"    for right in 0..sb.len() as i32 {{\n"
            f"        let ch = sb[right as usize] as usize; window[ch]+=1;\n"
            f"        if need[ch]>0 && window[ch]==need[ch] {{ formed+=1; }}\n"
            f"        while formed==required {{\n"
            f"            let len = right-left+1; if len<best {{ best=len; }}\n"
            f"            let lc = sb[left as usize] as usize; window[lc]-=1;\n"
            f"            if need[lc]>0 && window[lc]<need[lc] {{ formed-=1; }}\n"
            f"            left+=1;\n"
            f"        }}\n"
            f"    }}\n"
            f"    let r = if best==i32::MAX {{ 0 }} else {{ best }};\n"
            f"    if r==0 {{ r }} else {{ r{a} }}\n}}\n")


# ── modular-exponentiation (fast pow mod) ────────────────────────────────────
def _js_modpow(wrong):
    a = " + 1" if wrong else ""
    return (f"function modular_exponentiation(base, exp, mod) {{\n"
            f"    if (mod===1) return 0{a};\n"
            f"    let m=BigInt(mod); let result=1n; let b=((BigInt(base)%m)+m)%m; let e=BigInt(exp);\n"
            f"    while (e>0n) {{ if (e&1n) result=(result*b)%m; b=(b*b)%m; e>>=1n; }}\n"
            f"    return Number(result){a};\n}}\n")


def _ts_modpow(wrong):
    a = " + 1" if wrong else ""
    return (f"function modular_exponentiation(base: number, exp: number, mod: number): number {{\n"
            f"    if (mod===1) return 0{a};\n"
            f"    let m=BigInt(mod); let result=1n; let b=((BigInt(base)%m)+m)%m; let e=BigInt(exp);\n"
            f"    while (e>0n) {{ if (e&1n) result=(result*b)%m; b=(b*b)%m; e>>=1n; }}\n"
            f"    return Number(result){a};\n}}\n")


def _java_modpow(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int modular_exponentiation(int base, int exp, int mod) {{\n"
            f"    if (mod==1) return 0{a};\n"
            f"    long result=1; long b=((base%mod)+mod)%mod; long e=exp;\n"
            f"    while (e>0) {{ if ((e&1)==1) result=(result*b)%mod; b=(b*b)%mod; e>>=1; }}\n"
            f"    return (int)(result{a});\n}} }}\n")


def _cpp_modpow(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int modular_exponentiation(int base, int exp, int mod) {{\n"
            f"    if (mod==1) return 0{a};\n"
            f"    long long result=1; long long b=((base%mod)+mod)%mod; long long e=exp;\n"
            f"    while (e>0) {{ if (e&1) result=(result*b)%mod; b=(b*b)%mod; e>>=1; }}\n"
            f"    return (int)(result{a});\n}} }};\n")


def _csharp_modpow(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int modular_exponentiation(int base_, int exp, int mod) {{\n"
            f"    if (mod==1) return 0{a};\n"
            f"    long result=1; long b=((base_%mod)+mod)%mod; long e=exp;\n"
            f"    while (e>0) {{ if ((e&1)==1) result=(result*b)%mod; b=(b*b)%mod; e>>=1; }}\n"
            f"    return (int)(result{a});\n}} }}\n")


def _perl_modpow(wrong):
    a = " + 1" if wrong else ""
    return (f"sub modular_exponentiation {{\n"
            f"    my ($base, $exp, $mod) = @_;\n"
            f"    return (0{a}) if $mod==1;\n"
            f"    my $result=1; my $b=(($base%$mod)+$mod)%$mod; my $e=$exp;\n"
            f"    while ($e>0) {{ if ($e & 1) {{ $result=($result*$b)%$mod; }} $b=($b*$b)%$mod; $e=int($e/2); }}\n"
            f"    return $result{a};\n}}\n")


def _c_modpow(wrong):
    a = " + 1" if wrong else ""
    return (f"int modular_exponentiation(int base, int exp, int mod) {{\n"
            f"    if (mod==1) return 0{a};\n"
            f"    long long result=1; long long b=((long long)(base%mod)+mod)%mod; long long e=exp;\n"
            f"    while (e>0) {{ if (e&1) result=(result*b)%mod; b=(b*b)%mod; e>>=1; }}\n"
            f"    return (int)(result{a});\n}}\n")


def _rust_modpow(wrong):
    a = " + 1" if wrong else ""
    return (f"fn modular_exponentiation(base: i32, exp: i32, m: i32) -> i32 {{\n"
            f"    if m==1 {{ return 0{a}; }}\n"
            f"    let mm = m as i64; let mut result: i64=1; let mut b = ((base as i64 % mm)+mm)%mm; let mut e = exp as i64;\n"
            f"    while e>0 {{ if e&1==1 {{ result=(result*b)%mm; }} b=(b*b)%mm; e>>=1; }}\n"
            f"    (result{a}) as i32\n}}\n")


# ── palindrome-partition (min cuts DP, O(n^2)) ──────────────────────────────
def _js_palpart(wrong):
    a = " + 1" if wrong else ""
    return (f"function min_cut(s) {{\n"
            f"    const n=s.length;\n"
            f"    const isPal = Array.from({{length:n}}, () => new Array(n).fill(false));\n"
            f"    for (let i=0;i<n;i++) isPal[i][i]=true;\n"
            f"    for (let len=2;len<=n;len++) {{\n"
            f"        for (let i=0;i+len-1<n;i++) {{\n"
            f"            const j=i+len-1;\n"
            f"            if (s[i]===s[j] && (len===2 || isPal[i+1][j-1])) isPal[i][j]=true;\n"
            f"        }}\n"
            f"    }}\n"
            f"    const dp=new Array(n).fill(0);\n"
            f"    for (let i=0;i<n;i++) {{\n"
            f"        if (isPal[0][i]) {{ dp[i]=0; continue; }}\n"
            f"        dp[i]=i;\n"
            f"        for (let j=1;j<=i;j++) if (isPal[j][i] && dp[j-1]+1<dp[i]) dp[i]=dp[j-1]+1;\n"
            f"    }}\n"
            f"    return dp[n-1]{a};\n}}\n")


def _ts_palpart(wrong):
    a = " + 1" if wrong else ""
    return (f"function min_cut(s: string): number {{\n"
            f"    const n=s.length;\n"
            f"    const isPal: boolean[][] = Array.from({{length:n}}, () => new Array(n).fill(false));\n"
            f"    for (let i=0;i<n;i++) isPal[i][i]=true;\n"
            f"    for (let len=2;len<=n;len++) {{\n"
            f"        for (let i=0;i+len-1<n;i++) {{\n"
            f"            const j=i+len-1;\n"
            f"            if (s[i]===s[j] && (len===2 || isPal[i+1][j-1])) isPal[i][j]=true;\n"
            f"        }}\n"
            f"    }}\n"
            f"    const dp: number[]=new Array(n).fill(0);\n"
            f"    for (let i=0;i<n;i++) {{\n"
            f"        if (isPal[0][i]) {{ dp[i]=0; continue; }}\n"
            f"        dp[i]=i;\n"
            f"        for (let j=1;j<=i;j++) if (isPal[j][i] && dp[j-1]+1<dp[i]) dp[i]=dp[j-1]+1;\n"
            f"    }}\n"
            f"    return dp[n-1]{a};\n}}\n")


def _java_palpart(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int min_cut(String s) {{\n"
            f"    int n=s.length();\n"
            f"    boolean[][] isPal = new boolean[n][n];\n"
            f"    for (int i=0;i<n;i++) isPal[i][i]=true;\n"
            f"    for (int len=2;len<=n;len++) {{\n"
            f"        for (int i=0;i+len-1<n;i++) {{\n"
            f"            int j=i+len-1;\n"
            f"            if (s.charAt(i)==s.charAt(j) && (len==2 || isPal[i+1][j-1])) isPal[i][j]=true;\n"
            f"        }}\n"
            f"    }}\n"
            f"    int[] dp = new int[n];\n"
            f"    for (int i=0;i<n;i++) {{\n"
            f"        if (isPal[0][i]) {{ dp[i]=0; continue; }}\n"
            f"        dp[i]=i;\n"
            f"        for (int j=1;j<=i;j++) if (isPal[j][i] && dp[j-1]+1<dp[i]) dp[i]=dp[j-1]+1;\n"
            f"    }}\n"
            f"    return dp[n-1]{a};\n}} }}\n")


def _cpp_palpart(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int min_cut(std::string s) {{\n"
            f"    int n=s.size();\n"
            f"    std::vector<std::vector<bool>> isPal(n, std::vector<bool>(n,false));\n"
            f"    for (int i=0;i<n;i++) isPal[i][i]=true;\n"
            f"    for (int len=2;len<=n;len++) {{\n"
            f"        for (int i=0;i+len-1<n;i++) {{\n"
            f"            int j=i+len-1;\n"
            f"            if (s[i]==s[j] && (len==2 || isPal[i+1][j-1])) isPal[i][j]=true;\n"
            f"        }}\n"
            f"    }}\n"
            f"    std::vector<int> dp(n, 0);\n"
            f"    for (int i=0;i<n;i++) {{\n"
            f"        if (isPal[0][i]) {{ dp[i]=0; continue; }}\n"
            f"        dp[i]=i;\n"
            f"        for (int j=1;j<=i;j++) if (isPal[j][i] && dp[j-1]+1<dp[i]) dp[i]=dp[j-1]+1;\n"
            f"    }}\n"
            f"    return dp[n-1]{a};\n}} }};\n")


def _csharp_palpart(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int min_cut(string s) {{\n"
            f"    int n=s.Length;\n"
            f"    bool[,] isPal = new bool[n,n];\n"
            f"    for (int i=0;i<n;i++) isPal[i,i]=true;\n"
            f"    for (int len=2;len<=n;len++) {{\n"
            f"        for (int i=0;i+len-1<n;i++) {{\n"
            f"            int j=i+len-1;\n"
            f"            if (s[i]==s[j] && (len==2 || isPal[i+1,j-1])) isPal[i,j]=true;\n"
            f"        }}\n"
            f"    }}\n"
            f"    int[] dp = new int[n];\n"
            f"    for (int i=0;i<n;i++) {{\n"
            f"        if (isPal[0,i]) {{ dp[i]=0; continue; }}\n"
            f"        dp[i]=i;\n"
            f"        for (int j=1;j<=i;j++) if (isPal[j,i] && dp[j-1]+1<dp[i]) dp[i]=dp[j-1]+1;\n"
            f"    }}\n"
            f"    return dp[n-1]{a};\n}} }}\n")


def _perl_palpart(wrong):
    a = " + 1" if wrong else ""
    return (f"sub min_cut {{\n"
            f"    my ($s) = @_;\n"
            f"    my $n = length($s);\n"
            f"    my @isPal; for my $i (0..$n-1) {{ for my $j (0..$n-1) {{ $isPal[$i][$j]=0; }} }}\n"
            f"    for (my $i=0;$i<$n;$i++) {{ $isPal[$i][$i]=1; }}\n"
            f"    for (my $len=2;$len<=$n;$len++) {{\n"
            f"        for (my $i=0;$i+$len-1<$n;$i++) {{\n"
            f"            my $j=$i+$len-1;\n"
            f"            if (substr($s,$i,1) eq substr($s,$j,1) && ($len==2 || $isPal[$i+1][$j-1])) {{ $isPal[$i][$j]=1; }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    my @dp = (0) x $n;\n"
            f"    for (my $i=0;$i<$n;$i++) {{\n"
            f"        if ($isPal[0][$i]) {{ $dp[$i]=0; next; }}\n"
            f"        $dp[$i]=$i;\n"
            f"        for (my $j=1;$j<=$i;$j++) {{ if ($isPal[$j][$i] && $dp[$j-1]+1<$dp[$i]) {{ $dp[$i]=$dp[$j-1]+1; }} }}\n"
            f"    }}\n"
            f"    return $dp[$n-1]{a};\n}}\n")


def _c_palpart(wrong):
    a = " + 1" if wrong else ""
    return (f"int min_cut(char* s) {{\n"
            f"    int n = strlen(s);\n"
            f"    char** isPal = (char**)malloc(sizeof(char*)*n);\n"
            f"    for (int i=0;i<n;i++) isPal[i]=(char*)calloc(n, sizeof(char));\n"
            f"    for (int i=0;i<n;i++) isPal[i][i]=1;\n"
            f"    for (int len=2;len<=n;len++) {{\n"
            f"        for (int i=0;i+len-1<n;i++) {{\n"
            f"            int j=i+len-1;\n"
            f"            if (s[i]==s[j] && (len==2 || isPal[i+1][j-1])) isPal[i][j]=1;\n"
            f"        }}\n"
            f"    }}\n"
            f"    int* dp = (int*)calloc(n, sizeof(int));\n"
            f"    for (int i=0;i<n;i++) {{\n"
            f"        if (isPal[0][i]) {{ dp[i]=0; continue; }}\n"
            f"        dp[i]=i;\n"
            f"        for (int j=1;j<=i;j++) if (isPal[j][i] && dp[j-1]+1<dp[i]) dp[i]=dp[j-1]+1;\n"
            f"    }}\n"
            f"    int r=dp[n-1];\n"
            f"    for (int i=0;i<n;i++) free(isPal[i]);\n"
            f"    free(isPal); free(dp);\n"
            f"    return r{a};\n}}\n")


def _rust_palpart(wrong):
    a = " + 1" if wrong else ""
    return (f"fn min_cut(s: String) -> i32 {{\n"
            f"    let chars: Vec<char> = s.chars().collect(); let n = chars.len();\n"
            f"    let mut is_pal = vec![vec![false; n]; n];\n"
            f"    for i in 0..n {{ is_pal[i][i]=true; }}\n"
            f"    for len in 2..=n {{\n"
            f"        for i in 0..(n-len+1) {{\n"
            f"            let j = i+len-1;\n"
            f"            if chars[i]==chars[j] && (len==2 || is_pal[i+1][j-1]) {{ is_pal[i][j]=true; }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    let mut dp = vec![0i32; n];\n"
            f"    for i in 0..n {{\n"
            f"        if is_pal[0][i] {{ dp[i]=0; continue; }}\n"
            f"        dp[i]=i as i32;\n"
            f"        for j in 1..=i {{ if is_pal[j][i] && dp[j-1]+1<dp[i] {{ dp[i]=dp[j-1]+1; }} }}\n"
            f"    }}\n"
            f"    (dp[n-1]{a})\n}}\n")


# ── palindrome-partitioning (count ways DP, O(n^2)) ─────────────────────────
def _js_palpartcount(wrong):
    a = " + 1" if wrong else ""
    return (f"function count_partitions(s) {{\n"
            f"    const n=s.length;\n"
            f"    const isPal = Array.from({{length:n}}, () => new Array(n).fill(false));\n"
            f"    for (let i=0;i<n;i++) isPal[i][i]=true;\n"
            f"    for (let len=2;len<=n;len++) {{\n"
            f"        for (let i=0;i+len-1<n;i++) {{\n"
            f"            const j=i+len-1;\n"
            f"            if (s[i]===s[j] && (len===2 || isPal[i+1][j-1])) isPal[i][j]=true;\n"
            f"        }}\n"
            f"    }}\n"
            f"    const dp=new Array(n+1).fill(0); dp[0]=1;\n"
            f"    for (let i=1;i<=n;i++) {{\n"
            f"        for (let j=0;j<i;j++) {{ if (isPal[j][i-1]) dp[i]+=dp[j]; }}\n"
            f"    }}\n"
            f"    return dp[n]{a};\n}}\n")


def _ts_palpartcount(wrong):
    a = " + 1" if wrong else ""
    return (f"function count_partitions(s: string): number {{\n"
            f"    const n=s.length;\n"
            f"    const isPal: boolean[][]=Array.from({{length:n}}, () => new Array(n).fill(false));\n"
            f"    for (let i=0;i<n;i++) isPal[i][i]=true;\n"
            f"    for (let len=2;len<=n;len++) {{\n"
            f"        for (let i=0;i+len-1<n;i++) {{\n"
            f"            const j=i+len-1;\n"
            f"            if (s[i]===s[j] && (len===2 || isPal[i+1][j-1])) isPal[i][j]=true;\n"
            f"        }}\n"
            f"    }}\n"
            f"    const dp: number[]=new Array(n+1).fill(0); dp[0]=1;\n"
            f"    for (let i=1;i<=n;i++) {{\n"
            f"        for (let j=0;j<i;j++) {{ if (isPal[j][i-1]) dp[i]+=dp[j]; }}\n"
            f"    }}\n"
            f"    return dp[n]{a};\n}}\n")


def _java_palpartcount(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int count_partitions(String s) {{\n"
            f"    int n=s.length();\n"
            f"    boolean[][] isPal = new boolean[n][n];\n"
            f"    for (int i=0;i<n;i++) isPal[i][i]=true;\n"
            f"    for (int len=2;len<=n;len++) {{\n"
            f"        for (int i=0;i+len-1<n;i++) {{\n"
            f"            int j=i+len-1;\n"
            f"            if (s.charAt(i)==s.charAt(j) && (len==2 || isPal[i+1][j-1])) isPal[i][j]=true;\n"
            f"        }}\n"
            f"    }}\n"
            f"    long[] dp = new long[n+1]; dp[0]=1;\n"
            f"    for (int i=1;i<=n;i++) for (int j=0;j<i;j++) if (isPal[j][i-1]) dp[i]+=dp[j];\n"
            f"    return (int)(dp[n]{a});\n}} }}\n")


def _cpp_palpartcount(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int count_partitions(std::string s) {{\n"
            f"    int n=s.size();\n"
            f"    std::vector<std::vector<bool>> isPal(n, std::vector<bool>(n,false));\n"
            f"    for (int i=0;i<n;i++) isPal[i][i]=true;\n"
            f"    for (int len=2;len<=n;len++) {{\n"
            f"        for (int i=0;i+len-1<n;i++) {{\n"
            f"            int j=i+len-1;\n"
            f"            if (s[i]==s[j] && (len==2 || isPal[i+1][j-1])) isPal[i][j]=true;\n"
            f"        }}\n"
            f"    }}\n"
            f"    std::vector<long long> dp(n+1, 0); dp[0]=1;\n"
            f"    for (int i=1;i<=n;i++) for (int j=0;j<i;j++) if (isPal[j][i-1]) dp[i]+=dp[j];\n"
            f"    return (int)(dp[n]{a});\n}} }};\n")


def _csharp_palpartcount(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int count_partitions(string s) {{\n"
            f"    int n=s.Length;\n"
            f"    bool[,] isPal = new bool[n,n];\n"
            f"    for (int i=0;i<n;i++) isPal[i,i]=true;\n"
            f"    for (int len=2;len<=n;len++) {{\n"
            f"        for (int i=0;i+len-1<n;i++) {{\n"
            f"            int j=i+len-1;\n"
            f"            if (s[i]==s[j] && (len==2 || isPal[i+1,j-1])) isPal[i,j]=true;\n"
            f"        }}\n"
            f"    }}\n"
            f"    long[] dp = new long[n+1]; dp[0]=1;\n"
            f"    for (int i=1;i<=n;i++) for (int j=0;j<i;j++) if (isPal[j,i-1]) dp[i]+=dp[j];\n"
            f"    return (int)(dp[n]{a});\n}} }}\n")


def _perl_palpartcount(wrong):
    a = " + 1" if wrong else ""
    return (f"sub count_partitions {{\n"
            f"    my ($s) = @_;\n"
            f"    my $n = length($s);\n"
            f"    my @isPal; for my $i (0..$n-1) {{ for my $j (0..$n-1) {{ $isPal[$i][$j]=0; }} }}\n"
            f"    for (my $i=0;$i<$n;$i++) {{ $isPal[$i][$i]=1; }}\n"
            f"    for (my $len=2;$len<=$n;$len++) {{\n"
            f"        for (my $i=0;$i+$len-1<$n;$i++) {{\n"
            f"            my $j=$i+$len-1;\n"
            f"            if (substr($s,$i,1) eq substr($s,$j,1) && ($len==2 || $isPal[$i+1][$j-1])) {{ $isPal[$i][$j]=1; }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    my @dp = (0) x ($n+1); $dp[0]=1;\n"
            f"    for (my $i=1;$i<=$n;$i++) {{ for (my $j=0;$j<$i;$j++) {{ $dp[$i]+=$dp[$j] if $isPal[$j][$i-1]; }} }}\n"
            f"    return $dp[$n]{a};\n}}\n")


def _c_palpartcount(wrong):
    a = " + 1" if wrong else ""
    return (f"int count_partitions(char* s) {{\n"
            f"    int n = strlen(s);\n"
            f"    char** isPal = (char**)malloc(sizeof(char*)*n);\n"
            f"    for (int i=0;i<n;i++) isPal[i]=(char*)calloc(n, sizeof(char));\n"
            f"    for (int i=0;i<n;i++) isPal[i][i]=1;\n"
            f"    for (int len=2;len<=n;len++) {{\n"
            f"        for (int i=0;i+len-1<n;i++) {{\n"
            f"            int j=i+len-1;\n"
            f"            if (s[i]==s[j] && (len==2 || isPal[i+1][j-1])) isPal[i][j]=1;\n"
            f"        }}\n"
            f"    }}\n"
            f"    long long* dp = (long long*)calloc(n+1, sizeof(long long)); dp[0]=1;\n"
            f"    for (int i=1;i<=n;i++) for (int j=0;j<i;j++) if (isPal[j][i-1]) dp[i]+=dp[j];\n"
            f"    long long r=dp[n];\n"
            f"    for (int i=0;i<n;i++) free(isPal[i]);\n"
            f"    free(isPal); free(dp);\n"
            f"    return (int)(r{a});\n}}\n")


def _rust_palpartcount(wrong):
    a = " + 1" if wrong else ""
    return (f"fn count_partitions(s: String) -> i32 {{\n"
            f"    let chars: Vec<char> = s.chars().collect(); let n = chars.len();\n"
            f"    let mut is_pal = vec![vec![false; n]; n];\n"
            f"    for i in 0..n {{ is_pal[i][i]=true; }}\n"
            f"    for len in 2..=n {{\n"
            f"        for i in 0..(n-len+1) {{\n"
            f"            let j = i+len-1;\n"
            f"            if chars[i]==chars[j] && (len==2 || is_pal[i+1][j-1]) {{ is_pal[i][j]=true; }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    let mut dp = vec![0i64; n+1]; dp[0]=1;\n"
            f"    for i in 1..=n {{ for j in 0..i {{ if is_pal[j][i-1] {{ dp[i]+=dp[j]; }} }} }}\n"
            f"    (dp[n]{a}) as i32\n}}\n")


# ── palindrome-subsequence (LPS length DP, O(n^2)) ──────────────────────────
def _js_lps_seq(wrong):
    a = " + 1" if wrong else ""
    return (f"function lps(s) {{\n"
            f"    const n=s.length;\n"
            f"    const dp = Array.from({{length:n}}, () => new Array(n).fill(0));\n"
            f"    for (let i=n-1;i>=0;i--) {{\n"
            f"        dp[i][i]=1;\n"
            f"        for (let j=i+1;j<n;j++) {{\n"
            f"            if (s[i]===s[j]) dp[i][j]=dp[i+1][j-1]+2;\n"
            f"            else dp[i][j]=Math.max(dp[i+1][j], dp[i][j-1]);\n"
            f"        }}\n"
            f"    }}\n"
            f"    return (n===0?0:dp[0][n-1]){a};\n}}\n")


def _ts_lps_seq(wrong):
    a = " + 1" if wrong else ""
    return (f"function lps(s: string): number {{\n"
            f"    const n=s.length;\n"
            f"    const dp: number[][]=Array.from({{length:n}}, () => new Array(n).fill(0));\n"
            f"    for (let i=n-1;i>=0;i--) {{\n"
            f"        dp[i][i]=1;\n"
            f"        for (let j=i+1;j<n;j++) {{\n"
            f"            if (s[i]===s[j]) dp[i][j]=dp[i+1][j-1]+2;\n"
            f"            else dp[i][j]=Math.max(dp[i+1][j], dp[i][j-1]);\n"
            f"        }}\n"
            f"    }}\n"
            f"    return (n===0?0:dp[0][n-1]){a};\n}}\n")


def _java_lps_seq(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int lps(String s) {{\n"
            f"    int n=s.length();\n"
            f"    if (n==0) return 0{a};\n"
            f"    int[][] dp = new int[n][n];\n"
            f"    for (int i=n-1;i>=0;i--) {{\n"
            f"        dp[i][i]=1;\n"
            f"        for (int j=i+1;j<n;j++) {{\n"
            f"            if (s.charAt(i)==s.charAt(j)) dp[i][j]=(i+1<=j-1?dp[i+1][j-1]:0)+2;\n"
            f"            else dp[i][j]=Math.max(dp[i+1][j], dp[i][j-1]);\n"
            f"        }}\n"
            f"    }}\n"
            f"    return dp[0][n-1]{a};\n}} }}\n")


def _cpp_lps_seq(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int lps(std::string s) {{\n"
            f"    int n=s.size();\n"
            f"    if (n==0) return 0{a};\n"
            f"    std::vector<std::vector<int>> dp(n, std::vector<int>(n,0));\n"
            f"    for (int i=n-1;i>=0;i--) {{\n"
            f"        dp[i][i]=1;\n"
            f"        for (int j=i+1;j<n;j++) {{\n"
            f"            if (s[i]==s[j]) dp[i][j]=(i+1<=j-1?dp[i+1][j-1]:0)+2;\n"
            f"            else dp[i][j]=std::max(dp[i+1][j], dp[i][j-1]);\n"
            f"        }}\n"
            f"    }}\n"
            f"    return dp[0][n-1]{a};\n}} }};\n")


def _csharp_lps_seq(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int lps(string s) {{\n"
            f"    int n=s.Length;\n"
            f"    if (n==0) return 0{a};\n"
            f"    int[,] dp = new int[n,n];\n"
            f"    for (int i=n-1;i>=0;i--) {{\n"
            f"        dp[i,i]=1;\n"
            f"        for (int j=i+1;j<n;j++) {{\n"
            f"            if (s[i]==s[j]) dp[i,j]=(i+1<=j-1?dp[i+1,j-1]:0)+2;\n"
            f"            else dp[i,j]=System.Math.Max(dp[i+1,j], dp[i,j-1]);\n"
            f"        }}\n"
            f"    }}\n"
            f"    return dp[0,n-1]{a};\n}} }}\n")


def _perl_lps_seq(wrong):
    a = " + 1" if wrong else ""
    return (f"sub lps {{\n"
            f"    my ($s) = @_;\n"
            f"    my $n = length($s);\n"
            f"    return (0{a}) if $n==0;\n"
            f"    my @dp; for my $i (0..$n-1) {{ for my $j (0..$n-1) {{ $dp[$i][$j]=0; }} }}\n"
            f"    for (my $i=$n-1;$i>=0;$i--) {{\n"
            f"        $dp[$i][$i]=1;\n"
            f"        for (my $j=$i+1;$j<$n;$j++) {{\n"
            f"            if (substr($s,$i,1) eq substr($s,$j,1)) {{\n"
            f"                my $inner = ($i+1<=$j-1) ? $dp[$i+1][$j-1] : 0;\n"
            f"                $dp[$i][$j]=$inner+2;\n"
            f"            }} else {{\n"
            f"                $dp[$i][$j] = ($dp[$i+1][$j] > $dp[$i][$j-1]) ? $dp[$i+1][$j] : $dp[$i][$j-1];\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return $dp[0][$n-1]{a};\n}}\n")


def _c_lps_seq(wrong):
    a = " + 1" if wrong else ""
    return (f"int lps(char* s) {{\n"
            f"    int n = strlen(s);\n"
            f"    if (n==0) return 0{a};\n"
            f"    int** dp = (int**)malloc(sizeof(int*)*n);\n"
            f"    for (int i=0;i<n;i++) dp[i]=(int*)calloc(n, sizeof(int));\n"
            f"    for (int i=n-1;i>=0;i--) {{\n"
            f"        dp[i][i]=1;\n"
            f"        for (int j=i+1;j<n;j++) {{\n"
            f"            if (s[i]==s[j]) dp[i][j]=((i+1<=j-1)?dp[i+1][j-1]:0)+2;\n"
            f"            else dp[i][j]=(dp[i+1][j]>dp[i][j-1])?dp[i+1][j]:dp[i][j-1];\n"
            f"        }}\n"
            f"    }}\n"
            f"    int r=dp[0][n-1];\n"
            f"    for (int i=0;i<n;i++) free(dp[i]);\n"
            f"    free(dp);\n"
            f"    return r{a};\n}}\n")


def _rust_lps_seq(wrong):
    a = " + 1" if wrong else ""
    return (f"fn lps(s: String) -> i32 {{\n"
            f"    let chars: Vec<char> = s.chars().collect(); let n = chars.len();\n"
            f"    if n==0 {{ return 0{a}; }}\n"
            f"    let mut dp = vec![vec![0i32; n]; n];\n"
            f"    for i in (0..n).rev() {{\n"
            f"        dp[i][i]=1;\n"
            f"        for j in (i+1)..n {{\n"
            f"            if chars[i]==chars[j] {{\n"
            f"                let inner = if i+1<=j-1 {{ dp[i+1][j-1] }} else {{ 0 }};\n"
            f"                dp[i][j] = inner+2;\n"
            f"            }} else {{\n"
            f"                dp[i][j] = dp[i+1][j].max(dp[i][j-1]);\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    (dp[0][n-1]{a})\n}}\n")


# ── partition-equal-subset-sum (subset sum on total/2) ─────────────────────
def _js_partequal(wrong):
    ret = "false" if wrong else "true"
    return (f"function can_partition(nums) {{\n"
            f"    const total = nums.reduce((a,b)=>a+b,0);\n"
            f"    if (total%2!==0) return false;\n"
            f"    const target = total/2;\n"
            f"    const dp=new Array(target+1).fill(false); dp[0]=true;\n"
            f"    for (const x of nums) for (let i=target;i>=x;i--) if (dp[i-x]) dp[i]=true;\n"
            f"    return dp[target]?{ret}:false;\n}}\n")


def _ts_partequal(wrong):
    ret = "false" if wrong else "true"
    return (f"function can_partition(nums: number[]): boolean {{\n"
            f"    const total = nums.reduce((a,b)=>a+b,0);\n"
            f"    if (total%2!==0) return false;\n"
            f"    const target = total/2;\n"
            f"    const dp: boolean[]=new Array(target+1).fill(false); dp[0]=true;\n"
            f"    for (const x of nums) for (let i=target;i>=x;i--) if (dp[i-x]) dp[i]=true;\n"
            f"    return dp[target]?{ret}:false;\n}}\n")


def _java_partequal(wrong):
    ret = "false" if wrong else "true"
    return (f"class Solution {{ public boolean can_partition(int[] nums) {{\n"
            f"    int total=0; for (int x: nums) total+=x;\n"
            f"    if (total%2!=0) return false;\n"
            f"    int target=total/2;\n"
            f"    boolean[] dp = new boolean[target+1]; dp[0]=true;\n"
            f"    for (int x: nums) for (int i=target;i>=x;i--) if (dp[i-x]) dp[i]=true;\n"
            f"    return dp[target]?{ret}:false;\n}} }}\n")


def _cpp_partequal(wrong):
    ret = "false" if wrong else "true"
    return (f"class Solution {{ public: bool can_partition(std::vector<int> nums) {{\n"
            f"    int total=0; for (int x: nums) total+=x;\n"
            f"    if (total%2!=0) return false;\n"
            f"    int target=total/2;\n"
            f"    std::vector<bool> dp(target+1, false); dp[0]=true;\n"
            f"    for (int x: nums) for (int i=target;i>=x;i--) if (dp[i-x]) dp[i]=true;\n"
            f"    return dp[target]?{ret}:false;\n}} }};\n")


def _csharp_partequal(wrong):
    ret = "false" if wrong else "true"
    return (f"class Solution {{ public static bool can_partition(int[] nums) {{\n"
            f"    int total=0; foreach (int x in nums) total+=x;\n"
            f"    if (total%2!=0) return false;\n"
            f"    int target=total/2;\n"
            f"    bool[] dp = new bool[target+1]; dp[0]=true;\n"
            f"    foreach (int x in nums) for (int i=target;i>=x;i--) if (dp[i-x]) dp[i]=true;\n"
            f"    return dp[target]?{ret}:false;\n}} }}\n")


def _perl_partequal(wrong):
    ret = "0" if wrong else "1"
    return (f"sub can_partition {{\n"
            f"    my ($nums) = @_;\n"
            f"    my $total=0; foreach my $x (@$nums) {{ $total+=$x; }}\n"
            f"    return 0 if $total%2!=0;\n"
            f"    my $target=$total/2;\n"
            f"    my @dp = (0) x ($target+1); $dp[0]=1;\n"
            f"    foreach my $x (@$nums) {{ for (my $i=$target;$i>=$x;$i--) {{ $dp[$i]=1 if $dp[$i-$x]; }} }}\n"
            f"    return $dp[$target] ? {ret} : 0;\n}}\n")


def _c_partequal(wrong):
    ret = "0" if wrong else "1"
    return (f"int can_partition(AtlasIntArray nums) {{\n"
            f"    int total=0; for (int i=0;i<nums.size;i++) total+=nums.data[i];\n"
            f"    if (total%2!=0) return 0;\n"
            f"    int target=total/2;\n"
            f"    int* dp = (int*)calloc(target+1, sizeof(int)); dp[0]=1;\n"
            f"    for (int k=0;k<nums.size;k++) {{ int x=nums.data[k]; for (int i=target;i>=x;i--) if (dp[i-x]) dp[i]=1; }}\n"
            f"    int r = dp[target] ? {ret} : 0;\n"
            f"    free(dp);\n"
            f"    return r;\n}}\n")


def _rust_partequal(wrong):
    ret = "false" if wrong else "true"
    return (f"fn can_partition(nums: Vec<i32>) -> bool {{\n"
            f"    let total: i32 = nums.iter().sum();\n"
            f"    if total%2!=0 {{ return false; }}\n"
            f"    let target = (total/2) as usize;\n"
            f"    let mut dp = vec![false; target+1]; dp[0]=true;\n"
            f"    for x in nums.iter() {{ let xu = *x as usize; for i in (xu..=target).rev() {{ if dp[i-xu] {{ dp[i]=true; }} }} }}\n"
            f"    if dp[target] {{ {ret} }} else {{ false }}\n}}\n")


_BUILDERS = {
    "majority-element-ii": {"javascript": _js_majii, "typescript": _ts_majii, "java": _java_majii, "cpp": _cpp_majii,
                            "csharp": _csharp_majii, "perl": _perl_majii, "c": _c_majii, "rust": _rust_majii},
    "manacher": {"javascript": _js_manacher, "typescript": _ts_manacher, "java": _java_manacher, "cpp": _cpp_manacher,
                "csharp": _csharp_manacher, "perl": _perl_manacher, "c": _c_manacher, "rust": _rust_manacher},
    "matrix-chain-multiplication": {"javascript": _js_mcm, "typescript": _ts_mcm, "java": _java_mcm, "cpp": _cpp_mcm,
                                    "csharp": _csharp_mcm, "perl": _perl_mcm, "c": _c_mcm, "rust": _rust_mcm},
    "maximum-xor-of-two-numbers": {"javascript": _js_maxxor, "typescript": _ts_maxxor, "java": _java_maxxor, "cpp": _cpp_maxxor,
                                   "csharp": _csharp_maxxor, "perl": _perl_maxxor, "c": _c_maxxor, "rust": _rust_maxxor},
    "miller-rabin": {"javascript": _js_millerrabin, "typescript": _ts_millerrabin, "java": _java_millerrabin, "cpp": _cpp_millerrabin,
                     "csharp": _csharp_millerrabin, "perl": _perl_millerrabin, "c": _c_millerrabin, "rust": _rust_millerrabin},
    "minimum-window-substring-length": {"javascript": _js_minwin, "typescript": _ts_minwin, "java": _java_minwin, "cpp": _cpp_minwin,
                                        "csharp": _csharp_minwin, "perl": _perl_minwin, "c": _c_minwin, "rust": _rust_minwin},
    "modular-exponentiation": {"javascript": _js_modpow, "typescript": _ts_modpow, "java": _java_modpow, "cpp": _cpp_modpow,
                               "csharp": _csharp_modpow, "perl": _perl_modpow, "c": _c_modpow, "rust": _rust_modpow},
    "palindrome-partition": {"javascript": _js_palpart, "typescript": _ts_palpart, "java": _java_palpart, "cpp": _cpp_palpart,
                             "csharp": _csharp_palpart, "perl": _perl_palpart, "c": _c_palpart, "rust": _rust_palpart},
    "palindrome-partitioning": {"javascript": _js_palpartcount, "typescript": _ts_palpartcount, "java": _java_palpartcount, "cpp": _cpp_palpartcount,
                                "csharp": _csharp_palpartcount, "perl": _perl_palpartcount, "c": _c_palpartcount, "rust": _rust_palpartcount},
    "palindrome-subsequence": {"javascript": _js_lps_seq, "typescript": _ts_lps_seq, "java": _java_lps_seq, "cpp": _cpp_lps_seq,
                               "csharp": _csharp_lps_seq, "perl": _perl_lps_seq, "c": _c_lps_seq, "rust": _rust_lps_seq},
    "partition-equal-subset-sum": {"javascript": _js_partequal, "typescript": _ts_partequal, "java": _java_partequal, "cpp": _cpp_partequal,
                                   "csharp": _csharp_partequal, "perl": _perl_partequal, "c": _c_partequal, "rust": _rust_partequal},
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
                    adapter_version=f"{lang}-function-mega5-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
