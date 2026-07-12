"""Scales the next 11 problems (Function Mode) across the 8 original
working languages: boolean-parenthesization, burst-balloons,
combination-sum-count, first-unique-character-index, linked-list-cycle-detect,
longest-common-substring, longest-palindromic-substring,
longest-repeating-char-replacement, longest-substring-at-most-k-distinct,
longest-valid-parentheses, lucas-theorem.
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


# ── boolean-parenthesization (DP count ways True, symbols T/F, ops &|^) ─────
def _js_boolparen(wrong):
    a = " + 1" if wrong else ""
    return (f"function count_ways(symbols, ops) {{\n"
            f"    const n = symbols.length;\n"
            f"    const T = Array.from({{length:n}}, () => new Array(n).fill(0));\n"
            f"    const F = Array.from({{length:n}}, () => new Array(n).fill(0));\n"
            f"    for (let i=0;i<n;i++) {{ if (symbols[i]==='T') T[i][i]=1; else F[i][i]=1; }}\n"
            f"    for (let len=2;len<=n;len++) {{\n"
            f"        for (let i=0;i+len-1<n;i++) {{\n"
            f"            const j=i+len-1;\n"
            f"            for (let k=i;k<j;k++) {{\n"
            f"                const op=ops[k];\n"
            f"                const lt=T[i][k], lf=F[i][k], rt=T[k+1][j], rf=F[k+1][j];\n"
            f"                const total=(lt+lf)*(rt+rf);\n"
            f"                let trueWays;\n"
            f"                if (op==='&') trueWays = lt*rt;\n"
            f"                else if (op==='|') trueWays = total - lf*rf;\n"
            f"                else trueWays = lt*rf + lf*rt;\n"
            f"                T[i][j]+=trueWays; F[i][j]+=(total-trueWays);\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return T[0][n-1]{a};\n}}\n")


def _ts_boolparen(wrong):
    a = " + 1" if wrong else ""
    return (f"function count_ways(symbols: string, ops: string): number {{\n"
            f"    const n = symbols.length;\n"
            f"    const T: number[][] = Array.from({{length:n}}, () => new Array(n).fill(0));\n"
            f"    const F: number[][] = Array.from({{length:n}}, () => new Array(n).fill(0));\n"
            f"    for (let i=0;i<n;i++) {{ if (symbols[i]==='T') T[i][i]=1; else F[i][i]=1; }}\n"
            f"    for (let len=2;len<=n;len++) {{\n"
            f"        for (let i=0;i+len-1<n;i++) {{\n"
            f"            const j=i+len-1;\n"
            f"            for (let k=i;k<j;k++) {{\n"
            f"                const op=ops[k];\n"
            f"                const lt=T[i][k], lf=F[i][k], rt=T[k+1][j], rf=F[k+1][j];\n"
            f"                const total=(lt+lf)*(rt+rf);\n"
            f"                let trueWays;\n"
            f"                if (op==='&') trueWays = lt*rt;\n"
            f"                else if (op==='|') trueWays = total - lf*rf;\n"
            f"                else trueWays = lt*rf + lf*rt;\n"
            f"                T[i][j]+=trueWays; F[i][j]+=(total-trueWays);\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return T[0][n-1]{a};\n}}\n")


def _java_boolparen(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int count_ways(String symbols, String ops) {{\n"
            f"    int n = symbols.length();\n"
            f"    long[][] T = new long[n][n]; long[][] F = new long[n][n];\n"
            f"    for (int i=0;i<n;i++) {{ if (symbols.charAt(i)=='T') T[i][i]=1; else F[i][i]=1; }}\n"
            f"    for (int len=2;len<=n;len++) {{\n"
            f"        for (int i=0;i+len-1<n;i++) {{\n"
            f"            int j=i+len-1;\n"
            f"            for (int k=i;k<j;k++) {{\n"
            f"                char op=ops.charAt(k);\n"
            f"                long lt=T[i][k], lf=F[i][k], rt=T[k+1][j], rf=F[k+1][j];\n"
            f"                long total=(lt+lf)*(rt+rf);\n"
            f"                long trueWays;\n"
            f"                if (op=='&') trueWays = lt*rt;\n"
            f"                else if (op=='|') trueWays = total - lf*rf;\n"
            f"                else trueWays = lt*rf + lf*rt;\n"
            f"                T[i][j]+=trueWays; F[i][j]+=(total-trueWays);\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return (int)(T[0][n-1]{a});\n}} }}\n")


def _cpp_boolparen(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int count_ways(std::string symbols, std::string ops) {{\n"
            f"    int n = symbols.size();\n"
            f"    std::vector<std::vector<long long>> T(n, std::vector<long long>(n,0));\n"
            f"    std::vector<std::vector<long long>> F(n, std::vector<long long>(n,0));\n"
            f"    for (int i=0;i<n;i++) {{ if (symbols[i]=='T') T[i][i]=1; else F[i][i]=1; }}\n"
            f"    for (int len=2;len<=n;len++) {{\n"
            f"        for (int i=0;i+len-1<n;i++) {{\n"
            f"            int j=i+len-1;\n"
            f"            for (int k=i;k<j;k++) {{\n"
            f"                char op=ops[k];\n"
            f"                long long lt=T[i][k], lf=F[i][k], rt=T[k+1][j], rf=F[k+1][j];\n"
            f"                long long total=(lt+lf)*(rt+rf);\n"
            f"                long long trueWays;\n"
            f"                if (op=='&') trueWays = lt*rt;\n"
            f"                else if (op=='|') trueWays = total - lf*rf;\n"
            f"                else trueWays = lt*rf + lf*rt;\n"
            f"                T[i][j]+=trueWays; F[i][j]+=(total-trueWays);\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return (int)(T[0][n-1]{a});\n}} }};\n")


def _csharp_boolparen(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int count_ways(string symbols, string ops) {{\n"
            f"    int n = symbols.Length;\n"
            f"    long[,] T = new long[n,n]; long[,] F = new long[n,n];\n"
            f"    for (int i=0;i<n;i++) {{ if (symbols[i]=='T') T[i,i]=1; else F[i,i]=1; }}\n"
            f"    for (int len=2;len<=n;len++) {{\n"
            f"        for (int i=0;i+len-1<n;i++) {{\n"
            f"            int j=i+len-1;\n"
            f"            for (int k=i;k<j;k++) {{\n"
            f"                char op=ops[k];\n"
            f"                long lt=T[i,k], lf=F[i,k], rt=T[k+1,j], rf=F[k+1,j];\n"
            f"                long total=(lt+lf)*(rt+rf);\n"
            f"                long trueWays;\n"
            f"                if (op=='&') trueWays = lt*rt;\n"
            f"                else if (op=='|') trueWays = total - lf*rf;\n"
            f"                else trueWays = lt*rf + lf*rt;\n"
            f"                T[i,j]+=trueWays; F[i,j]+=(total-trueWays);\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return (int)(T[0,n-1]{a});\n}} }}\n")


def _perl_boolparen(wrong):
    a = " + 1" if wrong else ""
    return (f"sub count_ways {{\n"
            f"    my ($symbols, $ops) = @_;\n"
            f"    my $n = length($symbols);\n"
            f"    my @T; my @F;\n"
            f"    for my $i (0..$n-1) {{ for my $j (0..$n-1) {{ $T[$i][$j]=0; $F[$i][$j]=0; }} }}\n"
            f"    for (my $i=0;$i<$n;$i++) {{ if (substr($symbols,$i,1) eq 'T') {{ $T[$i][$i]=1; }} else {{ $F[$i][$i]=1; }} }}\n"
            f"    for (my $len=2;$len<=$n;$len++) {{\n"
            f"        for (my $i=0;$i+$len-1<$n;$i++) {{\n"
            f"            my $j=$i+$len-1;\n"
            f"            for (my $k=$i;$k<$j;$k++) {{\n"
            f"                my $op=substr($ops,$k,1);\n"
            f"                my $lt=$T[$i][$k]; my $lf=$F[$i][$k]; my $rt=$T[$k+1][$j]; my $rf=$F[$k+1][$j];\n"
            f"                my $total=($lt+$lf)*($rt+$rf);\n"
            f"                my $trueWays;\n"
            f"                if ($op eq '&') {{ $trueWays = $lt*$rt; }}\n"
            f"                elsif ($op eq '|') {{ $trueWays = $total - $lf*$rf; }}\n"
            f"                else {{ $trueWays = $lt*$rf + $lf*$rt; }}\n"
            f"                $T[$i][$j]+=$trueWays; $F[$i][$j]+=($total-$trueWays);\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return $T[0][$n-1]{a};\n}}\n")


def _c_boolparen(wrong):
    a = " + 1" if wrong else ""
    return (f"int count_ways(char* symbols, char* ops) {{\n"
            f"    int n = strlen(symbols);\n"
            f"    long long** T = (long long**)malloc(sizeof(long long*)*n);\n"
            f"    long long** F = (long long**)malloc(sizeof(long long*)*n);\n"
            f"    for (int i=0;i<n;i++) {{ T[i]=(long long*)calloc(n,sizeof(long long)); F[i]=(long long*)calloc(n,sizeof(long long)); }}\n"
            f"    for (int i=0;i<n;i++) {{ if (symbols[i]=='T') T[i][i]=1; else F[i][i]=1; }}\n"
            f"    for (int len=2;len<=n;len++) {{\n"
            f"        for (int i=0;i+len-1<n;i++) {{\n"
            f"            int j=i+len-1;\n"
            f"            for (int k=i;k<j;k++) {{\n"
            f"                char op=ops[k];\n"
            f"                long long lt=T[i][k], lf=F[i][k], rt=T[k+1][j], rf=F[k+1][j];\n"
            f"                long long total=(lt+lf)*(rt+rf);\n"
            f"                long long trueWays;\n"
            f"                if (op=='&') trueWays = lt*rt;\n"
            f"                else if (op=='|') trueWays = total - lf*rf;\n"
            f"                else trueWays = lt*rf + lf*rt;\n"
            f"                T[i][j]+=trueWays; F[i][j]+=(total-trueWays);\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    long long r = T[0][n-1];\n"
            f"    for (int i=0;i<n;i++) {{ free(T[i]); free(F[i]); }}\n"
            f"    free(T); free(F);\n"
            f"    return (int)(r{a});\n}}\n")


def _rust_boolparen(wrong):
    a = " + 1" if wrong else ""
    return (f"fn count_ways(symbols: String, ops: String) -> i32 {{\n"
            f"    let syms: Vec<char> = symbols.chars().collect(); let opsv: Vec<char> = ops.chars().collect();\n"
            f"    let n = syms.len();\n"
            f"    let mut t = vec![vec![0i64; n]; n]; let mut f = vec![vec![0i64; n]; n];\n"
            f"    for i in 0..n {{ if syms[i]=='T' {{ t[i][i]=1; }} else {{ f[i][i]=1; }} }}\n"
            f"    for len in 2..=n {{\n"
            f"        for i in 0..(n-len+1) {{\n"
            f"            let j = i+len-1;\n"
            f"            for k in i..j {{\n"
            f"                let op = opsv[k];\n"
            f"                let (lt,lf,rt,rf) = (t[i][k], f[i][k], t[k+1][j], f[k+1][j]);\n"
            f"                let total = (lt+lf)*(rt+rf);\n"
            f"                let true_ways = if op=='&' {{ lt*rt }} else if op=='|' {{ total - lf*rf }} else {{ lt*rf + lf*rt }};\n"
            f"                t[i][j] += true_ways; f[i][j] += total-true_ways;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    (t[0][n-1]{a}) as i32\n}}\n")


# ── burst-balloons (interval DP, O(n^3), max n~174) ─────────────────────────
def _js_burstballoons(wrong):
    a = " + 1" if wrong else ""
    return (f"function max_coins(balloons) {{\n"
            f"    const n = balloons.length;\n"
            f"    const nums = [1, ...balloons, 1];\n"
            f"    const dp = Array.from({{length:n+2}}, () => new Array(n+2).fill(0));\n"
            f"    for (let len=1;len<=n;len++) {{\n"
            f"        for (let left=1;left+len-1<=n;left++) {{\n"
            f"            const right=left+len-1;\n"
            f"            for (let k=left;k<=right;k++) {{\n"
            f"                const coins = nums[left-1]*nums[k]*nums[right+1] + dp[left][k-1] + dp[k+1][right];\n"
            f"                if (coins>dp[left][right]) dp[left][right]=coins;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return dp[1][n]{a};\n}}\n")


def _ts_burstballoons(wrong):
    a = " + 1" if wrong else ""
    return (f"function max_coins(balloons: number[]): number {{\n"
            f"    const n = balloons.length;\n"
            f"    const nums: number[] = [1, ...balloons, 1];\n"
            f"    const dp: number[][] = Array.from({{length:n+2}}, () => new Array(n+2).fill(0));\n"
            f"    for (let len=1;len<=n;len++) {{\n"
            f"        for (let left=1;left+len-1<=n;left++) {{\n"
            f"            const right=left+len-1;\n"
            f"            for (let k=left;k<=right;k++) {{\n"
            f"                const coins = nums[left-1]*nums[k]*nums[right+1] + dp[left][k-1] + dp[k+1][right];\n"
            f"                if (coins>dp[left][right]) dp[left][right]=coins;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return dp[1][n]{a};\n}}\n")


def _java_burstballoons(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int max_coins(int[] balloons) {{\n"
            f"    int n = balloons.length;\n"
            f"    long[] nums = new long[n+2]; nums[0]=1; nums[n+1]=1;\n"
            f"    for (int i=0;i<n;i++) nums[i+1]=balloons[i];\n"
            f"    long[][] dp = new long[n+2][n+2];\n"
            f"    for (int len=1;len<=n;len++) {{\n"
            f"        for (int left=1;left+len-1<=n;left++) {{\n"
            f"            int right=left+len-1;\n"
            f"            for (int k=left;k<=right;k++) {{\n"
            f"                long coins = nums[left-1]*nums[k]*nums[right+1] + dp[left][k-1] + dp[k+1][right];\n"
            f"                if (coins>dp[left][right]) dp[left][right]=coins;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return (int)(dp[1][n]{a});\n}} }}\n")


def _cpp_burstballoons(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int max_coins(std::vector<int> balloons) {{\n"
            f"    int n = balloons.size();\n"
            f"    std::vector<long long> nums(n+2); nums[0]=1; nums[n+1]=1;\n"
            f"    for (int i=0;i<n;i++) nums[i+1]=balloons[i];\n"
            f"    std::vector<std::vector<long long>> dp(n+2, std::vector<long long>(n+2, 0));\n"
            f"    for (int len=1;len<=n;len++) {{\n"
            f"        for (int left=1;left+len-1<=n;left++) {{\n"
            f"            int right=left+len-1;\n"
            f"            for (int k=left;k<=right;k++) {{\n"
            f"                long long coins = nums[left-1]*nums[k]*nums[right+1] + dp[left][k-1] + dp[k+1][right];\n"
            f"                if (coins>dp[left][right]) dp[left][right]=coins;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return (int)(dp[1][n]{a});\n}} }};\n")


def _csharp_burstballoons(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int max_coins(int[] balloons) {{\n"
            f"    int n = balloons.Length;\n"
            f"    long[] nums = new long[n+2]; nums[0]=1; nums[n+1]=1;\n"
            f"    for (int i=0;i<n;i++) nums[i+1]=balloons[i];\n"
            f"    long[,] dp = new long[n+2,n+2];\n"
            f"    for (int len=1;len<=n;len++) {{\n"
            f"        for (int left=1;left+len-1<=n;left++) {{\n"
            f"            int right=left+len-1;\n"
            f"            for (int k=left;k<=right;k++) {{\n"
            f"                long coins = nums[left-1]*nums[k]*nums[right+1] + dp[left,k-1] + dp[k+1,right];\n"
            f"                if (coins>dp[left,right]) dp[left,right]=coins;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return (int)(dp[1,n]{a});\n}} }}\n")


def _perl_burstballoons(wrong):
    a = " + 1" if wrong else ""
    return (f"sub max_coins {{\n"
            f"    my ($balloons) = @_;\n"
            f"    my $n = scalar(@$balloons);\n"
            f"    my @nums = (1, @$balloons, 1);\n"
            f"    my @dp; for my $i (0..$n+1) {{ for my $j (0..$n+1) {{ $dp[$i][$j]=0; }} }}\n"
            f"    for (my $len=1;$len<=$n;$len++) {{\n"
            f"        for (my $left=1;$left+$len-1<=$n;$left++) {{\n"
            f"            my $right=$left+$len-1;\n"
            f"            for (my $k=$left;$k<=$right;$k++) {{\n"
            f"                my $coins = $nums[$left-1]*$nums[$k]*$nums[$right+1] + $dp[$left][$k-1] + $dp[$k+1][$right];\n"
            f"                $dp[$left][$right]=$coins if $coins>$dp[$left][$right];\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return $dp[1][$n]{a};\n}}\n")


def _c_burstballoons(wrong):
    a = " + 1" if wrong else ""
    return (f"int max_coins(AtlasIntArray balloons) {{\n"
            f"    int n = balloons.size;\n"
            f"    long long* nums = (long long*)malloc(sizeof(long long)*(n+2));\n"
            f"    nums[0]=1; nums[n+1]=1;\n"
            f"    for (int i=0;i<n;i++) nums[i+1]=balloons.data[i];\n"
            f"    long long** dp = (long long**)malloc(sizeof(long long*)*(n+2));\n"
            f"    for (int i=0;i<n+2;i++) dp[i]=(long long*)calloc(n+2, sizeof(long long));\n"
            f"    for (int len=1;len<=n;len++) {{\n"
            f"        for (int left=1;left+len-1<=n;left++) {{\n"
            f"            int right=left+len-1;\n"
            f"            for (int k=left;k<=right;k++) {{\n"
            f"                long long coins = nums[left-1]*nums[k]*nums[right+1] + dp[left][k-1] + dp[k+1][right];\n"
            f"                if (coins>dp[left][right]) dp[left][right]=coins;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    long long r = dp[1][n];\n"
            f"    for (int i=0;i<n+2;i++) free(dp[i]);\n"
            f"    free(dp); free(nums);\n"
            f"    return (int)(r{a});\n}}\n")


def _rust_burstballoons(wrong):
    a = " + 1" if wrong else ""
    return (f"fn max_coins(balloons: Vec<i32>) -> i32 {{\n"
            f"    let n = balloons.len();\n"
            f"    let mut nums = vec![1i64; n+2];\n"
            f"    for i in 0..n {{ nums[i+1] = balloons[i] as i64; }}\n"
            f"    let mut dp = vec![vec![0i64; n+2]; n+2];\n"
            f"    for len in 1..=n {{\n"
            f"        for left in 1..=(n-len+1) {{\n"
            f"            let right = left+len-1;\n"
            f"            for k in left..=right {{\n"
            f"                let coins = nums[left-1]*nums[k]*nums[right+1] + dp[left][k-1] + dp[k+1][right];\n"
            f"                if coins>dp[left][right] {{ dp[left][right]=coins; }}\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    (dp[1][n]{a}) as i32\n}}\n")


# ── combination-sum-count (DP unbounded, count arrangements order-sensitive?) ─
# Note: this is order-INSENSITIVE combination count (classic "combination
# sum II count" analog to coin-change-ways) -- verified via corpus behavior
# matching unordered subset selection with repetition.
def _js_combsumcount(wrong):
    a = " + 1" if wrong else ""
    return (f"function combination_sum_count(candidates, target) {{\n"
            f"    const dp = new Array(target+1).fill(0); dp[0]=1;\n"
            f"    for (const c of candidates) for (let i=c;i<=target;i++) dp[i]+=dp[i-c];\n"
            f"    return dp[target]{a};\n}}\n")


def _ts_combsumcount(wrong):
    a = " + 1" if wrong else ""
    return (f"function combination_sum_count(candidates: number[], target: number): number {{\n"
            f"    const dp: number[] = new Array(target+1).fill(0); dp[0]=1;\n"
            f"    for (const c of candidates) for (let i=c;i<=target;i++) dp[i]+=dp[i-c];\n"
            f"    return dp[target]{a};\n}}\n")


def _java_combsumcount(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int combination_sum_count(int[] candidates, int target) {{\n"
            f"    long[] dp = new long[target+1]; dp[0]=1;\n"
            f"    for (int c: candidates) for (int i=c;i<=target;i++) dp[i]+=dp[i-c];\n"
            f"    return (int)(dp[target]{a});\n}} }}\n")


def _cpp_combsumcount(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int combination_sum_count(std::vector<int> candidates, int target) {{\n"
            f"    std::vector<long long> dp(target+1, 0); dp[0]=1;\n"
            f"    for (int c: candidates) for (int i=c;i<=target;i++) dp[i]+=dp[i-c];\n"
            f"    return (int)(dp[target]{a});\n}} }};\n")


def _csharp_combsumcount(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int combination_sum_count(int[] candidates, int target) {{\n"
            f"    long[] dp = new long[target+1]; dp[0]=1;\n"
            f"    foreach (int c in candidates) for (int i=c;i<=target;i++) dp[i]+=dp[i-c];\n"
            f"    return (int)(dp[target]{a});\n}} }}\n")


def _perl_combsumcount(wrong):
    a = " + 1" if wrong else ""
    return (f"sub combination_sum_count {{\n"
            f"    my ($candidates, $target) = @_;\n"
            f"    my @dp = (0) x ($target+1); $dp[0]=1;\n"
            f"    foreach my $c (@$candidates) {{ for (my $i=$c;$i<=$target;$i++) {{ $dp[$i]+=$dp[$i-$c]; }} }}\n"
            f"    return $dp[$target]{a};\n}}\n")


def _c_combsumcount(wrong):
    a = " + 1" if wrong else ""
    return (f"int combination_sum_count(AtlasIntArray candidates, int target) {{\n"
            f"    long long* dp = (long long*)calloc(target+1, sizeof(long long)); dp[0]=1;\n"
            f"    for (int k=0;k<candidates.size;k++) {{ int c=candidates.data[k]; for (int i=c;i<=target;i++) dp[i]+=dp[i-c]; }}\n"
            f"    long long r=dp[target]; free(dp);\n"
            f"    return (int)(r{a});\n}}\n")


def _rust_combsumcount(wrong):
    a = " + 1" if wrong else ""
    return (f"fn combination_sum_count(candidates: Vec<i32>, target: i32) -> i32 {{\n"
            f"    let t = target as usize; let mut dp = vec![0i64; t+1]; dp[0]=1;\n"
            f"    for &c in candidates.iter() {{ for i in (c as usize)..=t {{ dp[i]+=dp[i-c as usize]; }} }}\n"
            f"    (dp[t]{a}) as i32\n}}\n")


# ── first-unique-character-index (freq count) ────────────────────────────────
def _js_firstuniq(wrong):
    a = " + 1" if wrong else ""
    return (f"function first_uniq_char(s) {{\n"
            f"    const freq={{}};\n"
            f"    for (const ch of s) freq[ch]=(freq[ch]||0)+1;\n"
            f"    for (let i=0;i<s.length;i++) if (freq[s[i]]===1) return i{a};\n"
            f"    return -1;\n}}\n")


def _ts_firstuniq(wrong):
    a = " + 1" if wrong else ""
    return (f"function first_uniq_char(s: string): number {{\n"
            f"    const freq: Record<string,number>={{}};\n"
            f"    for (const ch of s) freq[ch]=(freq[ch]||0)+1;\n"
            f"    for (let i=0;i<s.length;i++) if (freq[s[i]]===1) return i{a};\n"
            f"    return -1;\n}}\n")


def _java_firstuniq(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int first_uniq_char(String s) {{\n"
            f"    int[] freq = new int[256];\n"
            f"    for (char ch: s.toCharArray()) freq[ch]++;\n"
            f"    for (int i=0;i<s.length();i++) if (freq[s.charAt(i)]==1) return i{a};\n"
            f"    return -1;\n}} }}\n")


def _cpp_firstuniq(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int first_uniq_char(std::string s) {{\n"
            f"    int freq[256]={{0}};\n"
            f"    for (unsigned char ch: s) freq[ch]++;\n"
            f"    for (int i=0;i<(int)s.size();i++) if (freq[(unsigned char)s[i]]==1) return i{a};\n"
            f"    return -1;\n}} }};\n")


def _csharp_firstuniq(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int first_uniq_char(string s) {{\n"
            f"    int[] freq = new int[256];\n"
            f"    foreach (char ch in s) freq[ch]++;\n"
            f"    for (int i=0;i<s.Length;i++) if (freq[s[i]]==1) return i{a};\n"
            f"    return -1;\n}} }}\n")


def _perl_firstuniq(wrong):
    a = " + 1" if wrong else ""
    return (f"sub first_uniq_char {{\n"
            f"    my ($s) = @_;\n"
            f"    my %freq;\n"
            f"    foreach my $ch (split //, $s) {{ $freq{{$ch}}++; }}\n"
            f"    my @chars = split //, $s;\n"
            f"    for (my $i=0;$i<scalar(@chars);$i++) {{ return $i{a} if $freq{{$chars[$i]}}==1; }}\n"
            f"    return -1;\n}}\n")


def _c_firstuniq(wrong):
    a = " + 1" if wrong else ""
    return (f"int first_uniq_char(char* s) {{\n"
            f"    int freq[256]={{0}}; int n=strlen(s);\n"
            f"    for (int i=0;i<n;i++) freq[(unsigned char)s[i]]++;\n"
            f"    for (int i=0;i<n;i++) if (freq[(unsigned char)s[i]]==1) return i{a};\n"
            f"    return -1;\n}}\n")


def _rust_firstuniq(wrong):
    a = " + 1" if wrong else ""
    return (f"fn first_uniq_char(s: String) -> i32 {{\n"
            f"    let chars: Vec<char> = s.chars().collect();\n"
            f"    let mut freq = std::collections::HashMap::new();\n"
            f"    for &ch in chars.iter() {{ *freq.entry(ch).or_insert(0) += 1; }}\n"
            f"    for i in 0..chars.len() {{ if freq[&chars[i]]==1 {{ return (i as i32){a}; }} }}\n"
            f"    -1\n}}\n")


# ── linked-list-cycle-detect (values as next-list, pos=-1 means no cycle) ──
def _js_llcycle(wrong):
    ret = "false" if wrong else "true"
    return (f"function has_cycle(values, pos) {{\n"
            f"    if (pos<0 || values.length===0) return false;\n"
            f"    const n=values.length;\n"
            f"    let slow=0, fast=0;\n"
            f"    function nxt(i) {{ return i+1<n ? i+1 : pos; }}\n"
            f"    do {{\n"
            f"        slow=nxt(slow); fast=nxt(nxt(fast));\n"
            f"    }} while (slow!==fast);\n"
            f"    return {ret};\n}}\n")


def _ts_llcycle(wrong):
    ret = "false" if wrong else "true"
    return (f"function has_cycle(values: number[], pos: number): boolean {{\n"
            f"    if (pos<0 || values.length===0) return false;\n"
            f"    const n=values.length;\n"
            f"    let slow=0, fast=0;\n"
            f"    const nxt = (i: number): number => i+1<n ? i+1 : pos;\n"
            f"    do {{\n"
            f"        slow=nxt(slow); fast=nxt(nxt(fast));\n"
            f"    }} while (slow!==fast);\n"
            f"    return {ret};\n}}\n")


def _java_llcycle(wrong):
    ret = "false" if wrong else "true"
    return (f"class Solution {{ public boolean has_cycle(int[] values, int pos) {{\n"
            f"    if (pos<0 || values.length==0) return false;\n"
            f"    int n=values.length;\n"
            f"    int slow=0, fast=0;\n"
            f"    do {{\n"
            f"        slow=nxt(slow,n,pos); fast=nxt(nxt(fast,n,pos),n,pos);\n"
            f"    }} while (slow!=fast);\n"
            f"    return {ret};\n}}\n"
            f"static int nxt(int i, int n, int pos) {{ return i+1<n ? i+1 : pos; }} }}\n")


def _cpp_llcycle(wrong):
    ret = "false" if wrong else "true"
    return (f"class Solution {{ public: bool has_cycle(std::vector<int> values, int pos) {{\n"
            f"    if (pos<0 || values.empty()) return false;\n"
            f"    int n=values.size();\n"
            f"    int slow=0, fast=0;\n"
            f"    do {{\n"
            f"        slow=nxt(slow,n,pos); fast=nxt(nxt(fast,n,pos),n,pos);\n"
            f"    }} while (slow!=fast);\n"
            f"    return {ret};\n}}\n"
            f"int nxt(int i, int n, int pos) {{ return i+1<n ? i+1 : pos; }} }};\n")


def _csharp_llcycle(wrong):
    ret = "false" if wrong else "true"
    return (f"class Solution {{ public static bool has_cycle(int[] values, int pos) {{\n"
            f"    if (pos<0 || values.Length==0) return false;\n"
            f"    int n=values.Length;\n"
            f"    int slow=0, fast=0;\n"
            f"    do {{\n"
            f"        slow=Nxt(slow,n,pos); fast=Nxt(Nxt(fast,n,pos),n,pos);\n"
            f"    }} while (slow!=fast);\n"
            f"    return {ret};\n}}\n"
            f"static int Nxt(int i, int n, int pos) {{ return i+1<n ? i+1 : pos; }} }}\n")


def _perl_llcycle(wrong):
    ret = "0" if wrong else "1"
    return (f"sub nxt_ll {{ my ($i,$n,$pos)=@_; return ($i+1<$n) ? $i+1 : $pos; }}\n"
            f"sub has_cycle {{\n"
            f"    my ($values, $pos) = @_;\n"
            f"    return 0 if $pos<0 || scalar(@$values)==0;\n"
            f"    my $n = scalar(@$values);\n"
            f"    my $slow=0; my $fast=0;\n"
            f"    do {{\n"
            f"        $slow=nxt_ll($slow,$n,$pos); $fast=nxt_ll(nxt_ll($fast,$n,$pos),$n,$pos);\n"
            f"    }} while ($slow!=$fast);\n"
            f"    return {ret};\n}}\n")


def _c_llcycle(wrong):
    ret = "0" if wrong else "1"
    return (f"int nxt_ll(int i, int n, int pos) {{ return (i+1<n) ? i+1 : pos; }}\n"
            f"int has_cycle(AtlasIntArray values, int pos) {{\n"
            f"    if (pos<0 || values.size==0) return 0;\n"
            f"    int n=values.size;\n"
            f"    int slow=0, fast=0;\n"
            f"    do {{\n"
            f"        slow=nxt_ll(slow,n,pos); fast=nxt_ll(nxt_ll(fast,n,pos),n,pos);\n"
            f"    }} while (slow!=fast);\n"
            f"    return {ret};\n}}\n")


def _rust_llcycle(wrong):
    ret = "false" if wrong else "true"
    return (f"fn nxt_ll(i: i32, n: i32, pos: i32) -> i32 {{ if i+1<n {{ i+1 }} else {{ pos }} }}\n"
            f"fn has_cycle(values: Vec<i32>, pos: i32) -> bool {{\n"
            f"    if pos<0 || values.is_empty() {{ return false; }}\n"
            f"    let n = values.len() as i32;\n"
            f"    let mut slow=0i32; let mut fast=0i32;\n"
            f"    loop {{\n"
            f"        slow = nxt_ll(slow,n,pos); fast = nxt_ll(nxt_ll(fast,n,pos),n,pos);\n"
            f"        if slow==fast {{ break; }}\n"
            f"    }}\n"
            f"    {ret}\n}}\n")


# ── longest-common-substring (DP O(n*m)) ────────────────────────────────────
def _js_lcsubstr(wrong):
    a = " + 1" if wrong else ""
    return (f"function longest_common_substring(s1, s2) {{\n"
            f"    const n=s1.length, m=s2.length;\n"
            f"    const dp=Array.from({{length:n+1}}, () => new Array(m+1).fill(0));\n"
            f"    let best=0;\n"
            f"    for (let i=1;i<=n;i++) for (let j=1;j<=m;j++) {{\n"
            f"        if (s1[i-1]===s2[j-1]) {{ dp[i][j]=dp[i-1][j-1]+1; if (dp[i][j]>best) best=dp[i][j]; }}\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _ts_lcsubstr(wrong):
    a = " + 1" if wrong else ""
    return (f"function longest_common_substring(s1: string, s2: string): number {{\n"
            f"    const n=s1.length, m=s2.length;\n"
            f"    const dp: number[][]=Array.from({{length:n+1}}, () => new Array(m+1).fill(0));\n"
            f"    let best=0;\n"
            f"    for (let i=1;i<=n;i++) for (let j=1;j<=m;j++) {{\n"
            f"        if (s1[i-1]===s2[j-1]) {{ dp[i][j]=dp[i-1][j-1]+1; if (dp[i][j]>best) best=dp[i][j]; }}\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _java_lcsubstr(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int longest_common_substring(String s1, String s2) {{\n"
            f"    int n=s1.length(), m=s2.length();\n"
            f"    int[][] dp = new int[n+1][m+1]; int best=0;\n"
            f"    for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) {{\n"
            f"        if (s1.charAt(i-1)==s2.charAt(j-1)) {{ dp[i][j]=dp[i-1][j-1]+1; best=Math.max(best,dp[i][j]); }}\n"
            f"    }}\n"
            f"    return best{a};\n}} }}\n")


def _cpp_lcsubstr(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int longest_common_substring(std::string s1, std::string s2) {{\n"
            f"    int n=s1.size(), m=s2.size();\n"
            f"    std::vector<std::vector<int>> dp(n+1, std::vector<int>(m+1,0)); int best=0;\n"
            f"    for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) {{\n"
            f"        if (s1[i-1]==s2[j-1]) {{ dp[i][j]=dp[i-1][j-1]+1; best=std::max(best,dp[i][j]); }}\n"
            f"    }}\n"
            f"    return best{a};\n}} }};\n")


def _csharp_lcsubstr(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int longest_common_substring(string s1, string s2) {{\n"
            f"    int n=s1.Length, m=s2.Length;\n"
            f"    int[,] dp = new int[n+1,m+1]; int best=0;\n"
            f"    for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) {{\n"
            f"        if (s1[i-1]==s2[j-1]) {{ dp[i,j]=dp[i-1,j-1]+1; best=System.Math.Max(best,dp[i,j]); }}\n"
            f"    }}\n"
            f"    return best{a};\n}} }}\n")


def _perl_lcsubstr(wrong):
    a = " + 1" if wrong else ""
    return (f"sub longest_common_substring {{\n"
            f"    my ($s1, $s2) = @_;\n"
            f"    my $n = length($s1); my $m = length($s2);\n"
            f"    my @dp; for my $i (0..$n) {{ for my $j (0..$m) {{ $dp[$i][$j]=0; }} }}\n"
            f"    my $best=0;\n"
            f"    for (my $i=1;$i<=$n;$i++) {{\n"
            f"        for (my $j=1;$j<=$m;$j++) {{\n"
            f"            if (substr($s1,$i-1,1) eq substr($s2,$j-1,1)) {{\n"
            f"                $dp[$i][$j]=$dp[$i-1][$j-1]+1; $best=$dp[$i][$j] if $dp[$i][$j]>$best;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return $best{a};\n}}\n")


def _c_lcsubstr(wrong):
    a = " + 1" if wrong else ""
    return (f"int longest_common_substring(char* s1, char* s2) {{\n"
            f"    int n = strlen(s1); int m = strlen(s2);\n"
            f"    int** dp = (int**)malloc(sizeof(int*)*(n+1));\n"
            f"    for (int i=0;i<=n;i++) dp[i]=(int*)calloc(m+1, sizeof(int));\n"
            f"    int best=0;\n"
            f"    for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) {{\n"
            f"        if (s1[i-1]==s2[j-1]) {{ dp[i][j]=dp[i-1][j-1]+1; if (dp[i][j]>best) best=dp[i][j]; }}\n"
            f"    }}\n"
            f"    for (int i=0;i<=n;i++) free(dp[i]);\n"
            f"    free(dp);\n"
            f"    return best{a};\n}}\n")


def _rust_lcsubstr(wrong):
    a = " + 1" if wrong else ""
    return (f"fn longest_common_substring(s1: String, s2: String) -> i32 {{\n"
            f"    let c1: Vec<char> = s1.chars().collect(); let c2: Vec<char> = s2.chars().collect();\n"
            f"    let n=c1.len(); let m=c2.len();\n"
            f"    let mut dp = vec![vec![0i32; m+1]; n+1]; let mut best=0i32;\n"
            f"    for i in 1..=n {{ for j in 1..=m {{\n"
            f"        if c1[i-1]==c2[j-1] {{ dp[i][j]=dp[i-1][j-1]+1; if dp[i][j]>best {{ best=dp[i][j]; }} }}\n"
            f"    }} }}\n"
            f"    best{a}\n}}\n")


# ── longest-palindromic-substring (returns LENGTH, expand-around-center) ───
def _js_lps_substr(wrong):
    a = " + 1" if wrong else ""
    return (f"function longest_palindrome(s) {{\n"
            f"    if (s.length===0) return 0{a};\n"
            f"    let best=1;\n"
            f"    function expand(l,r) {{ while (l>=0 && r<s.length && s[l]===s[r]) {{ l--; r++; }} return r-l-1; }}\n"
            f"    for (let i=0;i<s.length;i++) {{\n"
            f"        best=Math.max(best, expand(i,i));\n"
            f"        best=Math.max(best, expand(i,i+1));\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _ts_lps_substr(wrong):
    a = " + 1" if wrong else ""
    return (f"function longest_palindrome(s: string): number {{\n"
            f"    if (s.length===0) return 0{a};\n"
            f"    let best=1;\n"
            f"    function expand(l: number,r: number): number {{ while (l>=0 && r<s.length && s[l]===s[r]) {{ l--; r++; }} return r-l-1; }}\n"
            f"    for (let i=0;i<s.length;i++) {{\n"
            f"        best=Math.max(best, expand(i,i));\n"
            f"        best=Math.max(best, expand(i,i+1));\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _java_lps_substr(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int longest_palindrome(String s) {{\n"
            f"    if (s.length()==0) return 0{a};\n"
            f"    int best=1;\n"
            f"    for (int i=0;i<s.length();i++) {{\n"
            f"        best=Math.max(best, expand(s,i,i));\n"
            f"        best=Math.max(best, expand(s,i,i+1));\n"
            f"    }}\n"
            f"    return best{a};\n}}\n"
            f"static int expand(String s, int l, int r) {{ while (l>=0 && r<s.length() && s.charAt(l)==s.charAt(r)) {{ l--; r++; }} return r-l-1; }} }}\n")


def _cpp_lps_substr(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int longest_palindrome(std::string s) {{\n"
            f"    if (s.empty()) return 0{a};\n"
            f"    int best=1;\n"
            f"    for (int i=0;i<(int)s.size();i++) {{\n"
            f"        best=std::max(best, expand(s,i,i));\n"
            f"        best=std::max(best, expand(s,i,i+1));\n"
            f"    }}\n"
            f"    return best{a};\n}}\n"
            f"int expand(std::string& s, int l, int r) {{ while (l>=0 && r<(int)s.size() && s[l]==s[r]) {{ l--; r++; }} return r-l-1; }} }};\n")


def _csharp_lps_substr(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int longest_palindrome(string s) {{\n"
            f"    if (s.Length==0) return 0{a};\n"
            f"    int best=1;\n"
            f"    for (int i=0;i<s.Length;i++) {{\n"
            f"        best=System.Math.Max(best, Expand(s,i,i));\n"
            f"        best=System.Math.Max(best, Expand(s,i,i+1));\n"
            f"    }}\n"
            f"    return best{a};\n}}\n"
            f"static int Expand(string s, int l, int r) {{ while (l>=0 && r<s.Length && s[l]==s[r]) {{ l--; r++; }} return r-l-1; }} }}\n")


def _perl_lps_substr(wrong):
    a = " + 1" if wrong else ""
    return (f"sub expand_lps {{\n"
            f"    my ($s, $l, $r) = @_;\n"
            f"    while ($l>=0 && $r<length($s) && substr($s,$l,1) eq substr($s,$r,1)) {{ $l--; $r++; }}\n"
            f"    return $r-$l-1;\n}}\n"
            f"sub longest_palindrome {{\n"
            f"    my ($s) = @_;\n"
            f"    return (0{a}) if length($s)==0;\n"
            f"    my $best=1;\n"
            f"    for (my $i=0;$i<length($s);$i++) {{\n"
            f"        my $e1=expand_lps($s,$i,$i); $best=$e1 if $e1>$best;\n"
            f"        my $e2=expand_lps($s,$i,$i+1); $best=$e2 if $e2>$best;\n"
            f"    }}\n"
            f"    return $best{a};\n}}\n")


def _c_lps_substr(wrong):
    a = " + 1" if wrong else ""
    return (f"int expand_lps(char* s, int n, int l, int r) {{\n"
            f"    while (l>=0 && r<n && s[l]==s[r]) {{ l--; r++; }}\n"
            f"    return r-l-1;\n}}\n"
            f"int longest_palindrome(char* s) {{\n"
            f"    int n = strlen(s);\n"
            f"    if (n==0) return 0{a};\n"
            f"    int best=1;\n"
            f"    for (int i=0;i<n;i++) {{\n"
            f"        int e1=expand_lps(s,n,i,i); if (e1>best) best=e1;\n"
            f"        int e2=expand_lps(s,n,i,i+1); if (e2>best) best=e2;\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _rust_lps_substr(wrong):
    a = " + 1" if wrong else ""
    return (f"fn expand_lps(s: &Vec<char>, mut l: i32, mut r: i32) -> i32 {{\n"
            f"    while l>=0 && (r as usize)<s.len() && s[l as usize]==s[r as usize] {{ l-=1; r+=1; }}\n"
            f"    r-l-1\n}}\n"
            f"fn longest_palindrome(s: String) -> i32 {{\n"
            f"    let chars: Vec<char> = s.chars().collect();\n"
            f"    if chars.is_empty() {{ return 0{a}; }}\n"
            f"    let mut best=1i32;\n"
            f"    for i in 0..chars.len() as i32 {{\n"
            f"        let e1 = expand_lps(&chars,i,i); if e1>best {{ best=e1; }}\n"
            f"        let e2 = expand_lps(&chars,i,i+1); if e2>best {{ best=e2; }}\n"
            f"    }}\n"
            f"    best{a}\n}}\n")


# ── longest-repeating-char-replacement (sliding window with freq) ──────────
def _js_charrepl(wrong):
    a = " + 1" if wrong else ""
    return (f"function character_replacement(s, k) {{\n"
            f"    const freq={{}}; let left=0, maxCount=0, best=0;\n"
            f"    for (let right=0;right<s.length;right++) {{\n"
            f"        const ch=s[right]; freq[ch]=(freq[ch]||0)+1;\n"
            f"        maxCount=Math.max(maxCount, freq[ch]);\n"
            f"        while (right-left+1-maxCount>k) {{ freq[s[left]]--; left++; }}\n"
            f"        best=Math.max(best, right-left+1);\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _ts_charrepl(wrong):
    a = " + 1" if wrong else ""
    return (f"function character_replacement(s: string, k: number): number {{\n"
            f"    const freq: Record<string,number>={{}}; let left=0, maxCount=0, best=0;\n"
            f"    for (let right=0;right<s.length;right++) {{\n"
            f"        const ch=s[right]; freq[ch]=(freq[ch]||0)+1;\n"
            f"        maxCount=Math.max(maxCount, freq[ch]);\n"
            f"        while (right-left+1-maxCount>k) {{ freq[s[left]]--; left++; }}\n"
            f"        best=Math.max(best, right-left+1);\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _java_charrepl(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int character_replacement(String s, int k) {{\n"
            f"    int[] freq = new int[26]; int left=0, maxCount=0, best=0;\n"
            f"    for (int right=0;right<s.length();right++) {{\n"
            f"        int idx = s.charAt(right)-'A'; freq[idx]++;\n"
            f"        maxCount=Math.max(maxCount, freq[idx]);\n"
            f"        while (right-left+1-maxCount>k) {{ freq[s.charAt(left)-'A']--; left++; }}\n"
            f"        best=Math.max(best, right-left+1);\n"
            f"    }}\n"
            f"    return best{a};\n}} }}\n")


def _cpp_charrepl(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int character_replacement(std::string s, int k) {{\n"
            f"    int freq[26]={{0}}; int left=0, maxCount=0, best=0;\n"
            f"    for (int right=0;right<(int)s.size();right++) {{\n"
            f"        int idx=s[right]-'A'; freq[idx]++;\n"
            f"        maxCount=std::max(maxCount, freq[idx]);\n"
            f"        while (right-left+1-maxCount>k) {{ freq[s[left]-'A']--; left++; }}\n"
            f"        best=std::max(best, right-left+1);\n"
            f"    }}\n"
            f"    return best{a};\n}} }};\n")


def _csharp_charrepl(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int character_replacement(string s, int k) {{\n"
            f"    int[] freq = new int[26]; int left=0, maxCount=0, best=0;\n"
            f"    for (int right=0;right<s.Length;right++) {{\n"
            f"        int idx=s[right]-'A'; freq[idx]++;\n"
            f"        maxCount=System.Math.Max(maxCount, freq[idx]);\n"
            f"        while (right-left+1-maxCount>k) {{ freq[s[left]-'A']--; left++; }}\n"
            f"        best=System.Math.Max(best, right-left+1);\n"
            f"    }}\n"
            f"    return best{a};\n}} }}\n")


def _perl_charrepl(wrong):
    a = " + 1" if wrong else ""
    return (f"sub character_replacement {{\n"
            f"    my ($s, $k) = @_;\n"
            f"    my @freq = (0) x 26; my $left=0; my $maxCount=0; my $best=0;\n"
            f"    my @chars = split //, $s;\n"
            f"    for (my $right=0;$right<scalar(@chars);$right++) {{\n"
            f"        my $idx = ord($chars[$right]) - ord('A'); $freq[$idx]++;\n"
            f"        $maxCount=$freq[$idx] if $freq[$idx]>$maxCount;\n"
            f"        while ($right-$left+1-$maxCount>$k) {{ $freq[ord($chars[$left])-ord('A')]--; $left++; }}\n"
            f"        my $len=$right-$left+1; $best=$len if $len>$best;\n"
            f"    }}\n"
            f"    return $best{a};\n}}\n")


def _c_charrepl(wrong):
    a = " + 1" if wrong else ""
    return (f"int character_replacement(char* s, int k) {{\n"
            f"    int n = strlen(s);\n"
            f"    int freq[26]={{0}}; int left=0, maxCount=0, best=0;\n"
            f"    for (int right=0;right<n;right++) {{\n"
            f"        int idx=s[right]-'A'; freq[idx]++;\n"
            f"        if (freq[idx]>maxCount) maxCount=freq[idx];\n"
            f"        while (right-left+1-maxCount>k) {{ freq[s[left]-'A']--; left++; }}\n"
            f"        int len=right-left+1; if (len>best) best=len;\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _rust_charrepl(wrong):
    a = " + 1" if wrong else ""
    return (f"fn character_replacement(s: String, k: i32) -> i32 {{\n"
            f"    let chars: Vec<u8> = s.bytes().collect();\n"
            f"    let mut freq = [0i32; 26]; let mut left=0i32; let mut max_count=0i32; let mut best=0i32;\n"
            f"    for right in 0..chars.len() as i32 {{\n"
            f"        let idx = (chars[right as usize] - b'A') as usize; freq[idx]+=1;\n"
            f"        if freq[idx]>max_count {{ max_count=freq[idx]; }}\n"
            f"        while right-left+1-max_count>k {{ freq[(chars[left as usize]-b'A') as usize]-=1; left+=1; }}\n"
            f"        if right-left+1>best {{ best=right-left+1; }}\n"
            f"    }}\n"
            f"    best{a}\n}}\n")


# ── longest-substring-at-most-k-distinct (sliding window, freq map) ─────────
def _js_kdistinct(wrong):
    a = " + 1" if wrong else ""
    return (f"function longest_k_distinct(s, k) {{\n"
            f"    if (k===0) return 0{a};\n"
            f"    const freq={{}}; let left=0, best=0, distinct=0;\n"
            f"    for (let right=0;right<s.length;right++) {{\n"
            f"        const ch=s[right]; if (!freq[ch]) {{ freq[ch]=0; }}\n"
            f"        if (freq[ch]===0) distinct++;\n"
            f"        freq[ch]++;\n"
            f"        while (distinct>k) {{ const lc=s[left]; freq[lc]--; if (freq[lc]===0) distinct--; left++; }}\n"
            f"        best=Math.max(best, right-left+1);\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _ts_kdistinct(wrong):
    a = " + 1" if wrong else ""
    return (f"function longest_k_distinct(s: string, k: number): number {{\n"
            f"    if (k===0) return 0{a};\n"
            f"    const freq: Record<string,number>={{}}; let left=0, best=0, distinct=0;\n"
            f"    for (let right=0;right<s.length;right++) {{\n"
            f"        const ch=s[right]; if (!freq[ch]) {{ freq[ch]=0; }}\n"
            f"        if (freq[ch]===0) distinct++;\n"
            f"        freq[ch]++;\n"
            f"        while (distinct>k) {{ const lc=s[left]; freq[lc]--; if (freq[lc]===0) distinct--; left++; }}\n"
            f"        best=Math.max(best, right-left+1);\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _java_kdistinct(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int longest_k_distinct(String s, int k) {{\n"
            f"    if (k==0) return 0{a};\n"
            f"    java.util.Map<Character,Integer> freq = new java.util.HashMap<>();\n"
            f"    int left=0, best=0;\n"
            f"    for (int right=0;right<s.length();right++) {{\n"
            f"        char ch=s.charAt(right); freq.merge(ch,1,Integer::sum);\n"
            f"        while (freq.size()>k) {{ char lc=s.charAt(left); freq.put(lc, freq.get(lc)-1); if (freq.get(lc)==0) freq.remove(lc); left++; }}\n"
            f"        best=Math.max(best, right-left+1);\n"
            f"    }}\n"
            f"    return best{a};\n}} }}\n")


def _cpp_kdistinct(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int longest_k_distinct(std::string s, int k) {{\n"
            f"    if (k==0) return 0{a};\n"
            f"    std::unordered_map<char,int> freq;\n"
            f"    int left=0, best=0;\n"
            f"    for (int right=0;right<(int)s.size();right++) {{\n"
            f"        freq[s[right]]++;\n"
            f"        while ((int)freq.size()>k) {{ char lc=s[left]; freq[lc]--; if (freq[lc]==0) freq.erase(lc); left++; }}\n"
            f"        best=std::max(best, right-left+1);\n"
            f"    }}\n"
            f"    return best{a};\n}} }};\n")


def _csharp_kdistinct(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int longest_k_distinct(string s, int k) {{\n"
            f"    if (k==0) return 0{a};\n"
            f"    var freq = new System.Collections.Generic.Dictionary<char,int>();\n"
            f"    int left=0, best=0;\n"
            f"    for (int right=0;right<s.Length;right++) {{\n"
            f"        char ch=s[right]; if (!freq.ContainsKey(ch)) freq[ch]=0; freq[ch]++;\n"
            f"        while (freq.Count>k) {{ char lc=s[left]; freq[lc]--; if (freq[lc]==0) freq.Remove(lc); left++; }}\n"
            f"        best=System.Math.Max(best, right-left+1);\n"
            f"    }}\n"
            f"    return best{a};\n}} }}\n")


def _perl_kdistinct(wrong):
    a = " + 1" if wrong else ""
    return (f"sub longest_k_distinct {{\n"
            f"    my ($s, $k) = @_;\n"
            f"    return (0{a}) if $k==0;\n"
            f"    my %freq; my $left=0; my $best=0;\n"
            f"    my @chars = split //, $s;\n"
            f"    for (my $right=0;$right<scalar(@chars);$right++) {{\n"
            f"        $freq{{$chars[$right]}}++;\n"
            f"        while (scalar(keys %freq)>$k) {{\n"
            f"            my $lc=$chars[$left]; $freq{{$lc}}--; delete $freq{{$lc}} if $freq{{$lc}}==0; $left++;\n"
            f"        }}\n"
            f"        my $len=$right-$left+1; $best=$len if $len>$best;\n"
            f"    }}\n"
            f"    return $best{a};\n}}\n")


def _c_kdistinct(wrong):
    a = " + 1" if wrong else ""
    return (f"int longest_k_distinct(char* s, int k) {{\n"
            f"    if (k==0) return 0{a};\n"
            f"    int n = strlen(s);\n"
            f"    int freq[256]={{0}}; int distinct=0; int left=0, best=0;\n"
            f"    for (int right=0;right<n;right++) {{\n"
            f"        unsigned char ch = s[right];\n"
            f"        if (freq[ch]==0) distinct++;\n"
            f"        freq[ch]++;\n"
            f"        while (distinct>k) {{\n"
            f"            unsigned char lc=s[left]; freq[lc]--; if (freq[lc]==0) distinct--; left++;\n"
            f"        }}\n"
            f"        int len=right-left+1; if (len>best) best=len;\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _rust_kdistinct(wrong):
    a = " + 1" if wrong else ""
    return (f"fn longest_k_distinct(s: String, k: i32) -> i32 {{\n"
            f"    if k==0 {{ return 0{a}; }}\n"
            f"    let chars: Vec<char> = s.chars().collect();\n"
            f"    let mut freq: std::collections::HashMap<char,i32> = std::collections::HashMap::new();\n"
            f"    let mut left=0i32; let mut best=0i32;\n"
            f"    for right in 0..chars.len() as i32 {{\n"
            f"        *freq.entry(chars[right as usize]).or_insert(0) += 1;\n"
            f"        while (freq.len() as i32)>k {{\n"
            f"            let lc = chars[left as usize];\n"
            f"            let e = freq.get_mut(&lc).unwrap(); *e -= 1;\n"
            f"            if *e==0 {{ freq.remove(&lc); }}\n"
            f"            left+=1;\n"
            f"        }}\n"
            f"        if right-left+1>best {{ best=right-left+1; }}\n"
            f"    }}\n"
            f"    best{a}\n}}\n")


# ── longest-valid-parentheses (stack-based, O(n), max n=5887) ──────────────
def _js_lvp(wrong):
    a = " + 1" if wrong else ""
    return (f"function longest_valid_parentheses(s) {{\n"
            f"    const stack=[-1]; let best=0;\n"
            f"    for (let i=0;i<s.length;i++) {{\n"
            f"        if (s[i]==='(') stack.push(i);\n"
            f"        else {{\n"
            f"            stack.pop();\n"
            f"            if (stack.length===0) stack.push(i);\n"
            f"            else best=Math.max(best, i-stack[stack.length-1]);\n"
            f"        }}\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _ts_lvp(wrong):
    a = " + 1" if wrong else ""
    return (f"function longest_valid_parentheses(s: string): number {{\n"
            f"    const stack: number[]=[-1]; let best=0;\n"
            f"    for (let i=0;i<s.length;i++) {{\n"
            f"        if (s[i]==='(') stack.push(i);\n"
            f"        else {{\n"
            f"            stack.pop();\n"
            f"            if (stack.length===0) stack.push(i);\n"
            f"            else best=Math.max(best, i-stack[stack.length-1]);\n"
            f"        }}\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _java_lvp(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int longest_valid_parentheses(String s) {{\n"
            f"    java.util.Deque<Integer> stack=new java.util.ArrayDeque<>(); stack.push(-1); int best=0;\n"
            f"    for (int i=0;i<s.length();i++) {{\n"
            f"        if (s.charAt(i)=='(') stack.push(i);\n"
            f"        else {{\n"
            f"            stack.pop();\n"
            f"            if (stack.isEmpty()) stack.push(i);\n"
            f"            else best=Math.max(best, i-stack.peek());\n"
            f"        }}\n"
            f"    }}\n"
            f"    return best{a};\n}} }}\n")


def _cpp_lvp(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int longest_valid_parentheses(std::string s) {{\n"
            f"    std::vector<int> stack; stack.push_back(-1); int best=0;\n"
            f"    for (int i=0;i<(int)s.size();i++) {{\n"
            f"        if (s[i]=='(') stack.push_back(i);\n"
            f"        else {{\n"
            f"            stack.pop_back();\n"
            f"            if (stack.empty()) stack.push_back(i);\n"
            f"            else best=std::max(best, i-stack.back());\n"
            f"        }}\n"
            f"    }}\n"
            f"    return best{a};\n}} }};\n")


def _csharp_lvp(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int longest_valid_parentheses(string s) {{\n"
            f"    var stack = new System.Collections.Generic.Stack<int>(); stack.Push(-1); int best=0;\n"
            f"    for (int i=0;i<s.Length;i++) {{\n"
            f"        if (s[i]=='(') stack.Push(i);\n"
            f"        else {{\n"
            f"            stack.Pop();\n"
            f"            if (stack.Count==0) stack.Push(i);\n"
            f"            else best=System.Math.Max(best, i-stack.Peek());\n"
            f"        }}\n"
            f"    }}\n"
            f"    return best{a};\n}} }}\n")


def _perl_lvp(wrong):
    a = " + 1" if wrong else ""
    return (f"sub longest_valid_parentheses {{\n"
            f"    my ($s) = @_;\n"
            f"    my @stack = (-1); my $best=0;\n"
            f"    my @chars = split //, $s;\n"
            f"    for (my $i=0;$i<scalar(@chars);$i++) {{\n"
            f"        if ($chars[$i] eq '(') {{ push @stack, $i; }}\n"
            f"        else {{\n"
            f"            pop @stack;\n"
            f"            if (scalar(@stack)==0) {{ push @stack, $i; }}\n"
            f"            else {{ my $len=$i-$stack[-1]; $best=$len if $len>$best; }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return $best{a};\n}}\n")


def _c_lvp(wrong):
    a = " + 1" if wrong else ""
    return (f"int longest_valid_parentheses(char* s) {{\n"
            f"    int n = strlen(s);\n"
            f"    int* stack = (int*)malloc(sizeof(int)*(n+2)); int top=0;\n"
            f"    stack[top++]=-1; int best=0;\n"
            f"    for (int i=0;i<n;i++) {{\n"
            f"        if (s[i]=='(') stack[top++]=i;\n"
            f"        else {{\n"
            f"            top--;\n"
            f"            if (top==0) stack[top++]=i;\n"
            f"            else {{ int len=i-stack[top-1]; if (len>best) best=len; }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    free(stack);\n"
            f"    return best{a};\n}}\n")


def _rust_lvp(wrong):
    a = " + 1" if wrong else ""
    return (f"fn longest_valid_parentheses(s: String) -> i32 {{\n"
            f"    let mut stack: Vec<i32> = vec![-1]; let mut best=0i32;\n"
            f"    for (i, ch) in s.chars().enumerate() {{\n"
            f"        let i = i as i32;\n"
            f"        if ch=='(' {{ stack.push(i); }}\n"
            f"        else {{\n"
            f"            stack.pop();\n"
            f"            if stack.is_empty() {{ stack.push(i); }}\n"
            f"            else {{ let len = i - stack[stack.len()-1]; if len>best {{ best=len; }} }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    best{a}\n}}\n")


# ── lucas-theorem (C(n,k) mod p, p prime, small p) ──────────────────────────
def _js_lucas(wrong):
    a = " + 1" if wrong else ""
    return (f"function lucas_theorem(n, k, p) {{\n"
            f"    function smallComb(nn, kk) {{\n"
            f"        if (kk>nn || kk<0) return 0;\n"
            f"        let num=1, den=1;\n"
            f"        for (let i=0;i<kk;i++) {{ num=(num*((nn-i)%p))%p; den=(den*(i+1))%p; }}\n"
            f"        let denInv=1, base=den%p, e=p-2;\n"
            f"        while (e>0) {{ if (e&1) denInv=(denInv*base)%p; base=(base*base)%p; e>>=1; }}\n"
            f"        return (num*denInv)%p;\n"
            f"    }}\n"
            f"    let result=1, nn=n, kk=k;\n"
            f"    while (nn>0 || kk>0) {{\n"
            f"        const ni=nn%p, ki=kk%p;\n"
            f"        if (ki>ni) return 0{a};\n"
            f"        result=(result*smallComb(ni,ki))%p;\n"
            f"        nn=Math.floor(nn/p); kk=Math.floor(kk/p);\n"
            f"    }}\n"
            f"    return result{a};\n}}\n")


def _ts_lucas(wrong):
    a = " + 1" if wrong else ""
    return (f"function lucas_theorem(n: number, k: number, p: number): number {{\n"
            f"    function smallComb(nn: number, kk: number): number {{\n"
            f"        if (kk>nn || kk<0) return 0;\n"
            f"        let num=1, den=1;\n"
            f"        for (let i=0;i<kk;i++) {{ num=(num*((nn-i)%p))%p; den=(den*(i+1))%p; }}\n"
            f"        let denInv=1, base=den%p, e=p-2;\n"
            f"        while (e>0) {{ if (e&1) denInv=(denInv*base)%p; base=(base*base)%p; e>>=1; }}\n"
            f"        return (num*denInv)%p;\n"
            f"    }}\n"
            f"    let result=1, nn=n, kk=k;\n"
            f"    while (nn>0 || kk>0) {{\n"
            f"        const ni=nn%p, ki=kk%p;\n"
            f"        if (ki>ni) return 0{a};\n"
            f"        result=(result*smallComb(ni,ki))%p;\n"
            f"        nn=Math.floor(nn/p); kk=Math.floor(kk/p);\n"
            f"    }}\n"
            f"    return result{a};\n}}\n")


def _java_lucas(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int lucas_theorem(int n, int k, int p) {{\n"
            f"    long result=1; long nn=n, kk=k;\n"
            f"    while (nn>0 || kk>0) {{\n"
            f"        long ni=nn%p, ki=kk%p;\n"
            f"        if (ki>ni) return (int)(0{a});\n"
            f"        result=(result*smallComb(ni,ki,p))%p;\n"
            f"        nn/=p; kk/=p;\n"
            f"    }}\n"
            f"    return (int)(result{a});\n}}\n"
            f"long smallComb(long nn, long kk, long p) {{\n"
            f"    if (kk>nn || kk<0) return 0;\n"
            f"    long num=1, den=1;\n"
            f"    for (long i=0;i<kk;i++) {{ num=(num*((nn-i)%p))%p; den=(den*(i+1))%p; }}\n"
            f"    long denInv=1, base=den%p, e=p-2;\n"
            f"    while (e>0) {{ if ((e&1)==1) denInv=(denInv*base)%p; base=(base*base)%p; e>>=1; }}\n"
            f"    return (num*denInv)%p;\n}} }}\n")


def _cpp_lucas(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int lucas_theorem(int n, int k, int p) {{\n"
            f"    long long result=1; long long nn=n, kk=k;\n"
            f"    while (nn>0 || kk>0) {{\n"
            f"        long long ni=nn%p, ki=kk%p;\n"
            f"        if (ki>ni) return (int)(0{a});\n"
            f"        result=(result*smallComb(ni,ki,p))%p;\n"
            f"        nn/=p; kk/=p;\n"
            f"    }}\n"
            f"    return (int)(result{a});\n}}\n"
            f"long long smallComb(long long nn, long long kk, long long p) {{\n"
            f"    if (kk>nn || kk<0) return 0;\n"
            f"    long long num=1, den=1;\n"
            f"    for (long long i=0;i<kk;i++) {{ num=(num*((nn-i)%p))%p; den=(den*(i+1))%p; }}\n"
            f"    long long denInv=1, base=den%p, e=p-2;\n"
            f"    while (e>0) {{ if (e&1) denInv=(denInv*base)%p; base=(base*base)%p; e>>=1; }}\n"
            f"    return (num*denInv)%p;\n}} }};\n")


def _csharp_lucas(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int lucas_theorem(int n, int k, int p) {{\n"
            f"    long result=1; long nn=n, kk=k;\n"
            f"    while (nn>0 || kk>0) {{\n"
            f"        long ni=nn%p, ki=kk%p;\n"
            f"        if (ki>ni) return (int)(0{a});\n"
            f"        result=(result*SmallComb(ni,ki,p))%p;\n"
            f"        nn/=p; kk/=p;\n"
            f"    }}\n"
            f"    return (int)(result{a});\n}}\n"
            f"static long SmallComb(long nn, long kk, long p) {{\n"
            f"    if (kk>nn || kk<0) return 0;\n"
            f"    long num=1, den=1;\n"
            f"    for (long i=0;i<kk;i++) {{ num=(num*((nn-i)%p))%p; den=(den*(i+1))%p; }}\n"
            f"    long denInv=1, pw=den%p, e=p-2;\n"
            f"    while (e>0) {{ if ((e&1)==1) denInv=(denInv*pw)%p; pw=(pw*pw)%p; e>>=1; }}\n"
            f"    return (num*denInv)%p;\n}} }}\n")


def _perl_lucas(wrong):
    a = " + 1" if wrong else ""
    return (f"sub small_comb {{\n"
            f"    my ($nn, $kk, $p) = @_;\n"
            f"    return 0 if $kk>$nn || $kk<0;\n"
            f"    my $num=1; my $den=1;\n"
            f"    for (my $i=0;$i<$kk;$i++) {{ $num=($num*(($nn-$i)%$p))%$p; $den=($den*($i+1))%$p; }}\n"
            f"    my $denInv=1; my $base=$den%$p; my $e=$p-2;\n"
            f"    while ($e>0) {{ if ($e & 1) {{ $denInv=($denInv*$base)%$p; }} $base=($base*$base)%$p; $e=$e>>1; }}\n"
            f"    return ($num*$denInv)%$p;\n}}\n"
            f"sub lucas_theorem {{\n"
            f"    my ($n, $k, $p) = @_;\n"
            f"    my $result=1; my $nn=$n; my $kk=$k;\n"
            f"    while ($nn>0 || $kk>0) {{\n"
            f"        my $ni=$nn%$p; my $ki=$kk%$p;\n"
            f"        return (0{a}) if $ki>$ni;\n"
            f"        $result=($result*small_comb($ni,$ki,$p))%$p;\n"
            f"        $nn=int($nn/$p); $kk=int($kk/$p);\n"
            f"    }}\n"
            f"    return $result{a};\n}}\n")


def _c_lucas(wrong):
    a = " + 1" if wrong else ""
    return (f"long long small_comb_lucas(long long nn, long long kk, long long p) {{\n"
            f"    if (kk>nn || kk<0) return 0;\n"
            f"    long long num=1, den=1;\n"
            f"    for (long long i=0;i<kk;i++) {{ num=(num*((nn-i)%p))%p; den=(den*(i+1))%p; }}\n"
            f"    long long denInv=1, base=den%p, e=p-2;\n"
            f"    while (e>0) {{ if (e&1) denInv=(denInv*base)%p; base=(base*base)%p; e>>=1; }}\n"
            f"    return (num*denInv)%p;\n}}\n"
            f"int lucas_theorem(int n, int k, int p) {{\n"
            f"    long long result=1; long long nn=n, kk=k;\n"
            f"    while (nn>0 || kk>0) {{\n"
            f"        long long ni=nn%p, ki=kk%p;\n"
            f"        if (ki>ni) return (int)(0{a});\n"
            f"        result=(result*small_comb_lucas(ni,ki,p))%p;\n"
            f"        nn/=p; kk/=p;\n"
            f"    }}\n"
            f"    return (int)(result{a});\n}}\n")


def _rust_lucas(wrong):
    a = " + 1" if wrong else ""
    return (f"fn small_comb(nn: i64, kk: i64, p: i64) -> i64 {{\n"
            f"    if kk>nn || kk<0 {{ return 0; }}\n"
            f"    let mut num=1i64; let mut den=1i64;\n"
            f"    for i in 0..kk {{ num=(num*((nn-i)%p))%p; den=(den*(i+1))%p; }}\n"
            f"    let mut den_inv=1i64; let mut base=den%p; let mut e=p-2;\n"
            f"    while e>0 {{ if e&1==1 {{ den_inv=(den_inv*base)%p; }} base=(base*base)%p; e>>=1; }}\n"
            f"    (num*den_inv)%p\n}}\n"
            f"fn lucas_theorem(n: i32, k: i32, p: i32) -> i32 {{\n"
            f"    let (mut result, mut nn, mut kk) = (1i64, n as i64, k as i64); let pp = p as i64;\n"
            f"    while nn>0 || kk>0 {{\n"
            f"        let (ni, ki) = (nn%pp, kk%pp);\n"
            f"        if ki>ni {{ return (0{a}) as i32; }}\n"
            f"        result=(result*small_comb(ni,ki,pp))%pp;\n"
            f"        nn/=pp; kk/=pp;\n"
            f"    }}\n"
            f"    (result{a}) as i32\n}}\n")


_BUILDERS = {
    "boolean-parenthesization": {"javascript": _js_boolparen, "typescript": _ts_boolparen, "java": _java_boolparen, "cpp": _cpp_boolparen,
                                 "csharp": _csharp_boolparen, "perl": _perl_boolparen, "c": _c_boolparen, "rust": _rust_boolparen},
    "burst-balloons": {"javascript": _js_burstballoons, "typescript": _ts_burstballoons, "java": _java_burstballoons, "cpp": _cpp_burstballoons,
                       "csharp": _csharp_burstballoons, "perl": _perl_burstballoons, "c": _c_burstballoons, "rust": _rust_burstballoons},
    "combination-sum-count": {"javascript": _js_combsumcount, "typescript": _ts_combsumcount, "java": _java_combsumcount, "cpp": _cpp_combsumcount,
                              "csharp": _csharp_combsumcount, "perl": _perl_combsumcount, "c": _c_combsumcount, "rust": _rust_combsumcount},
    "first-unique-character-index": {"javascript": _js_firstuniq, "typescript": _ts_firstuniq, "java": _java_firstuniq, "cpp": _cpp_firstuniq,
                                     "csharp": _csharp_firstuniq, "perl": _perl_firstuniq, "c": _c_firstuniq, "rust": _rust_firstuniq},
    "linked-list-cycle-detect": {"javascript": _js_llcycle, "typescript": _ts_llcycle, "java": _java_llcycle, "cpp": _cpp_llcycle,
                                 "csharp": _csharp_llcycle, "perl": _perl_llcycle, "c": _c_llcycle, "rust": _rust_llcycle},
    "longest-common-substring": {"javascript": _js_lcsubstr, "typescript": _ts_lcsubstr, "java": _java_lcsubstr, "cpp": _cpp_lcsubstr,
                                 "csharp": _csharp_lcsubstr, "perl": _perl_lcsubstr, "c": _c_lcsubstr, "rust": _rust_lcsubstr},
    "longest-palindromic-substring": {"javascript": _js_lps_substr, "typescript": _ts_lps_substr, "java": _java_lps_substr, "cpp": _cpp_lps_substr,
                                      "csharp": _csharp_lps_substr, "perl": _perl_lps_substr, "c": _c_lps_substr, "rust": _rust_lps_substr},
    "longest-repeating-char-replacement": {"javascript": _js_charrepl, "typescript": _ts_charrepl, "java": _java_charrepl, "cpp": _cpp_charrepl,
                                          "csharp": _csharp_charrepl, "perl": _perl_charrepl, "c": _c_charrepl, "rust": _rust_charrepl},
    "longest-substring-at-most-k-distinct": {"javascript": _js_kdistinct, "typescript": _ts_kdistinct, "java": _java_kdistinct, "cpp": _cpp_kdistinct,
                                             "csharp": _csharp_kdistinct, "perl": _perl_kdistinct, "c": _c_kdistinct, "rust": _rust_kdistinct},
    "longest-valid-parentheses": {"javascript": _js_lvp, "typescript": _ts_lvp, "java": _java_lvp, "cpp": _cpp_lvp,
                                  "csharp": _csharp_lvp, "perl": _perl_lvp, "c": _c_lvp, "rust": _rust_lvp},
    "lucas-theorem": {"javascript": _js_lucas, "typescript": _ts_lucas, "java": _java_lucas, "cpp": _cpp_lucas,
                      "csharp": _csharp_lucas, "perl": _perl_lucas, "c": _c_lucas, "rust": _rust_lucas},
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
                    adapter_version=f"{lang}-function-mega4-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
