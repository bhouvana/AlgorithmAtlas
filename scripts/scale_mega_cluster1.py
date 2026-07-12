"""Scales 35 new problems (Function Mode) across the 8 original working
languages in one large batch: bitonic-peak-index, coin-change,
coin-change-ways, count-occurrences-sorted, delete-and-earn,
euler-phi-sieve, find-minimum-rotated-sorted-array, integer-square-root,
job-scheduling, jump-game-ii-min-jumps, kth-largest-element,
koko-eating-bananas, largest-rectangle-in-histogram, last-occurrence,
longest-bitonic-subsequence, max-consecutive-ones-with-k-flips,
max-sum-subarray-fixed-k, maximum-subarray-circular, meeting-rooms,
merge-sorted-arrays-inplace, merge-two-sorted-lists,
middle-of-linked-list, min-subarray-len-target-sum,
minimum-knight-moves, number-of-divisors, palindrome-linked-list,
perfect-squares-min-count, reverse-linked-list, rod-cutting,
rotated-binary-search, search-insert-position, staircase,
subarray-product-less-than-k, subarray-sums-divisible-by-k, subset-sum.
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


# ── bitonic-peak-index ──────────────────────────────────────────────────────
def _js_bitonic(wrong):
    ret = "lo + 1" if wrong else "lo"
    return (f"function peak_index(nums) {{\n"
            f"    let lo=0, hi=nums.length-1;\n"
            f"    while (lo<hi) {{ const mid=(lo+hi)>>1; if (nums[mid]<nums[mid+1]) lo=mid+1; else hi=mid; }}\n"
            f"    return {ret};\n}}\n")


def _ts_bitonic(wrong):
    ret = "lo + 1" if wrong else "lo"
    return (f"function peak_index(nums: number[]): number {{\n"
            f"    let lo=0, hi=nums.length-1;\n"
            f"    while (lo<hi) {{ const mid=(lo+hi)>>1; if (nums[mid]<nums[mid+1]) lo=mid+1; else hi=mid; }}\n"
            f"    return {ret};\n}}\n")


def _java_bitonic(wrong):
    ret = "lo + 1" if wrong else "lo"
    return (f"class Solution {{ public int peak_index(int[] nums) {{\n"
            f"    int lo=0, hi=nums.length-1;\n"
            f"    while (lo<hi) {{ int mid=(lo+hi)>>>1; if (nums[mid]<nums[mid+1]) lo=mid+1; else hi=mid; }}\n"
            f"    return {ret};\n}} }}\n")


def _cpp_bitonic(wrong):
    ret = "lo + 1" if wrong else "lo"
    return (f"class Solution {{ public: int peak_index(std::vector<int> nums) {{\n"
            f"    int lo=0, hi=(int)nums.size()-1;\n"
            f"    while (lo<hi) {{ int mid=lo+(hi-lo)/2; if (nums[mid]<nums[mid+1]) lo=mid+1; else hi=mid; }}\n"
            f"    return {ret};\n}} }};\n")


def _csharp_bitonic(wrong):
    ret = "lo + 1" if wrong else "lo"
    return (f"class Solution {{ public static int peak_index(int[] nums) {{\n"
            f"    int lo=0, hi=nums.Length-1;\n"
            f"    while (lo<hi) {{ int mid=lo+(hi-lo)/2; if (nums[mid]<nums[mid+1]) lo=mid+1; else hi=mid; }}\n"
            f"    return {ret};\n}} }}\n")


def _perl_bitonic(wrong):
    ret = "$lo + 1" if wrong else "$lo"
    return (f"sub peak_index {{\n"
            f"    my ($nums) = @_;\n"
            f"    my $lo=0; my $hi=scalar(@$nums)-1;\n"
            f"    while ($lo<$hi) {{ my $mid=int(($lo+$hi)/2); if ($nums->[$mid]<$nums->[$mid+1]) {{ $lo=$mid+1; }} else {{ $hi=$mid; }} }}\n"
            f"    return {ret};\n}}\n")


def _c_bitonic(wrong):
    ret = "lo + 1" if wrong else "lo"
    return (f"int peak_index(AtlasIntArray nums) {{\n"
            f"    int lo=0, hi=nums.size-1;\n"
            f"    while (lo<hi) {{ int mid=lo+(hi-lo)/2; if (nums.data[mid]<nums.data[mid+1]) lo=mid+1; else hi=mid; }}\n"
            f"    return {ret};\n}}\n")


def _rust_bitonic(wrong):
    ret = "lo as i32 + 1" if wrong else "lo as i32"
    return (f"fn peak_index(nums: Vec<i32>) -> i32 {{\n"
            f"    let mut lo=0usize; let mut hi=nums.len()-1;\n"
            f"    while lo<hi {{ let mid=lo+(hi-lo)/2; if nums[mid]<nums[mid+1] {{ lo=mid+1; }} else {{ hi=mid; }} }}\n"
            f"    {ret}\n}}\n")


# ── coin-change (min coins, unbounded) ──────────────────────────────────────
def _js_coinchange(wrong):
    a = " + 1" if wrong else ""
    return (f"function coin_change(coins, amount) {{\n"
            f"    const INF = Infinity; const dp = new Array(amount+1).fill(INF); dp[0]=0;\n"
            f"    for (let i=1;i<=amount;i++) for (const c of coins) if (c<=i && dp[i-c]+1<dp[i]) dp[i]=dp[i-c]+1;\n"
            f"    const r = dp[amount]===INF ? -1 : dp[amount];\n"
            f"    return r===-1?r:r{a};\n}}\n")


def _ts_coinchange(wrong):
    a = " + 1" if wrong else ""
    return (f"function coin_change(coins: number[], amount: number): number {{\n"
            f"    const INF = Infinity; const dp: number[] = new Array(amount+1).fill(INF); dp[0]=0;\n"
            f"    for (let i=1;i<=amount;i++) for (const c of coins) if (c<=i && dp[i-c]+1<dp[i]) dp[i]=dp[i-c]+1;\n"
            f"    const r = dp[amount]===INF ? -1 : dp[amount];\n"
            f"    return r===-1?r:r{a};\n}}\n")


def _java_coinchange(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int coin_change(int[] coins, int amount) {{\n"
            f"    int INF = Integer.MAX_VALUE/2; int[] dp = new int[amount+1]; java.util.Arrays.fill(dp, INF); dp[0]=0;\n"
            f"    for (int i=1;i<=amount;i++) for (int c: coins) if (c<=i && dp[i-c]+1<dp[i]) dp[i]=dp[i-c]+1;\n"
            f"    int r = dp[amount]>=INF ? -1 : dp[amount];\n"
            f"    return r==-1?r:r{a};\n}} }}\n")


def _cpp_coinchange(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int coin_change(std::vector<int> coins, int amount) {{\n"
            f"    int INF = 1000000000; std::vector<int> dp(amount+1, INF); dp[0]=0;\n"
            f"    for (int i=1;i<=amount;i++) for (int c: coins) if (c<=i && dp[i-c]+1<dp[i]) dp[i]=dp[i-c]+1;\n"
            f"    int r = dp[amount]>=INF ? -1 : dp[amount];\n"
            f"    return r==-1?r:r{a};\n}} }};\n")


def _csharp_coinchange(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int coin_change(int[] coins, int amount) {{\n"
            f"    int INF = 1000000000; int[] dp = new int[amount+1]; for (int i=0;i<=amount;i++) dp[i]=INF; dp[0]=0;\n"
            f"    for (int i=1;i<=amount;i++) foreach (int c in coins) if (c<=i && dp[i-c]+1<dp[i]) dp[i]=dp[i-c]+1;\n"
            f"    int r = dp[amount]>=INF ? -1 : dp[amount];\n"
            f"    return r==-1?r:r{a};\n}} }}\n")


def _perl_coinchange(wrong):
    a = " + 1" if wrong else ""
    return (f"sub coin_change {{\n"
            f"    my ($coins, $amount) = @_;\n"
            f"    my $INF = 1000000000; my @dp = ($INF) x ($amount+1); $dp[0]=0;\n"
            f"    for (my $i=1;$i<=$amount;$i++) {{ foreach my $c (@$coins) {{ if ($c<=$i && $dp[$i-$c]+1<$dp[$i]) {{ $dp[$i]=$dp[$i-$c]+1; }} }} }}\n"
            f"    my $r = $dp[$amount]>=$INF ? -1 : $dp[$amount];\n"
            f"    return ($r==-1) ? $r : $r{a};\n}}\n")


def _c_coinchange(wrong):
    a = " + 1" if wrong else ""
    return (f"int coin_change(AtlasIntArray coins, int amount) {{\n"
            f"    int INF = 1000000000; int* dp = (int*)malloc(sizeof(int)*(amount+1));\n"
            f"    for (int i=0;i<=amount;i++) dp[i]=INF; dp[0]=0;\n"
            f"    for (int i=1;i<=amount;i++) for (int k=0;k<coins.size;k++) {{ int c=coins.data[k]; if (c<=i && dp[i-c]+1<dp[i]) dp[i]=dp[i-c]+1; }}\n"
            f"    int r = dp[amount]>=INF ? -1 : dp[amount];\n"
            f"    free(dp);\n"
            f"    return r==-1?r:r{a};\n}}\n")


def _rust_coinchange(wrong):
    a = " + 1" if wrong else ""
    return (f"fn coin_change(coins: Vec<i32>, amount: i32) -> i32 {{\n"
            f"    let n = amount as usize; let inf = 1_000_000_000;\n"
            f"    let mut dp = vec![inf; n+1]; dp[0]=0;\n"
            f"    for i in 1..=n {{ for &c in coins.iter() {{ if (c as usize)<=i && dp[i-c as usize]+1<dp[i] {{ dp[i]=dp[i-c as usize]+1; }} }} }}\n"
            f"    let r = if dp[n]>=inf {{ -1 }} else {{ dp[n] }};\n"
            f"    if r==-1 {{ r }} else {{ r{a} }}\n}}\n")


# ── coin-change-ways (count ways, unbounded, order-independent) ────────────
def _js_coinways(wrong):
    a = " + 1" if wrong else ""
    return (f"function change(coins, amount) {{\n"
            f"    const dp = new Array(amount+1).fill(0); dp[0]=1;\n"
            f"    for (const c of coins) for (let i=c;i<=amount;i++) dp[i]+=dp[i-c];\n"
            f"    return dp[amount]{a};\n}}\n")


def _ts_coinways(wrong):
    a = " + 1" if wrong else ""
    return (f"function change(coins: number[], amount: number): number {{\n"
            f"    const dp: number[] = new Array(amount+1).fill(0); dp[0]=1;\n"
            f"    for (const c of coins) for (let i=c;i<=amount;i++) dp[i]+=dp[i-c];\n"
            f"    return dp[amount]{a};\n}}\n")


def _java_coinways(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int change(int[] coins, int amount) {{\n"
            f"    long[] dp = new long[amount+1]; dp[0]=1;\n"
            f"    for (int c: coins) for (int i=c;i<=amount;i++) dp[i]+=dp[i-c];\n"
            f"    return (int)(dp[amount]{a});\n}} }}\n")


def _cpp_coinways(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int change(std::vector<int> coins, int amount) {{\n"
            f"    std::vector<long long> dp(amount+1, 0); dp[0]=1;\n"
            f"    for (int c: coins) for (int i=c;i<=amount;i++) dp[i]+=dp[i-c];\n"
            f"    return (int)(dp[amount]{a});\n}} }};\n")


def _csharp_coinways(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int change(int[] coins, int amount) {{\n"
            f"    long[] dp = new long[amount+1]; dp[0]=1;\n"
            f"    foreach (int c in coins) for (int i=c;i<=amount;i++) dp[i]+=dp[i-c];\n"
            f"    return (int)(dp[amount]{a});\n}} }}\n")


def _perl_coinways(wrong):
    a = " + 1" if wrong else ""
    return (f"sub change {{\n"
            f"    my ($coins, $amount) = @_;\n"
            f"    my @dp = (0) x ($amount+1); $dp[0]=1;\n"
            f"    foreach my $c (@$coins) {{ for (my $i=$c;$i<=$amount;$i++) {{ $dp[$i]+=$dp[$i-$c]; }} }}\n"
            f"    return $dp[$amount]{a};\n}}\n")


def _c_coinways(wrong):
    a = " + 1" if wrong else ""
    return (f"int change(AtlasIntArray coins, int amount) {{\n"
            f"    long long* dp = (long long*)calloc(amount+1, sizeof(long long)); dp[0]=1;\n"
            f"    for (int k=0;k<coins.size;k++) {{ int c=coins.data[k]; for (int i=c;i<=amount;i++) dp[i]+=dp[i-c]; }}\n"
            f"    long long r = dp[amount]; free(dp);\n"
            f"    return (int)(r{a});\n}}\n")


def _rust_coinways(wrong):
    a = " + 1" if wrong else ""
    return (f"fn change(coins: Vec<i32>, amount: i32) -> i32 {{\n"
            f"    let n = amount as usize; let mut dp = vec![0i64; n+1]; dp[0]=1;\n"
            f"    for &c in coins.iter() {{ for i in (c as usize)..=n {{ dp[i]+=dp[i-c as usize]; }} }}\n"
            f"    (dp[n]{a}) as i32\n}}\n")


# ── count-occurrences-sorted ─────────────────────────────────────────────────
def _js_countocc(wrong):
    a = " + 1" if wrong else ""
    return (f"function count_occurrences(nums, target) {{\n"
            f"    function lb(t) {{ let lo=0,hi=nums.length; while(lo<hi){{const mid=(lo+hi)>>1; if(nums[mid]<t)lo=mid+1;else hi=mid;}} return lo; }}\n"
            f"    const first=lb(target), last=lb(target+1);\n"
            f"    return (last-first){a};\n}}\n")


def _ts_countocc(wrong):
    a = " + 1" if wrong else ""
    return (f"function count_occurrences(nums: number[], target: number): number {{\n"
            f"    function lb(t: number): number {{ let lo=0,hi=nums.length; while(lo<hi){{const mid=(lo+hi)>>1; if(nums[mid]<t)lo=mid+1;else hi=mid;}} return lo; }}\n"
            f"    const first=lb(target), last=lb(target+1);\n"
            f"    return (last-first){a};\n}}\n")


def _java_countocc(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int count_occurrences(int[] nums, int target) {{\n"
            f"    return (lb(nums, target+1) - lb(nums, target)){a};\n}}\n"
            f"static int lb(int[] nums, int t) {{ int lo=0,hi=nums.length; while(lo<hi){{int mid=(lo+hi)>>>1; if(nums[mid]<t)lo=mid+1;else hi=mid;}} return lo; }} }}\n")


def _cpp_countocc(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int count_occurrences(std::vector<int> nums, int target) {{\n"
            f"    return (lb(nums, target+1) - lb(nums, target)){a};\n}}\n"
            f"int lb(std::vector<int>& nums, int t) {{ int lo=0,hi=(int)nums.size(); while(lo<hi){{int mid=lo+(hi-lo)/2; if(nums[mid]<t)lo=mid+1;else hi=mid;}} return lo; }} }};\n")


def _csharp_countocc(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int count_occurrences(int[] nums, int target) {{\n"
            f"    return (Lb(nums, target+1) - Lb(nums, target)){a};\n}}\n"
            f"static int Lb(int[] nums, int t) {{ int lo=0,hi=nums.Length; while(lo<hi){{int mid=lo+(hi-lo)/2; if(nums[mid]<t)lo=mid+1;else hi=mid;}} return lo; }} }}\n")


def _perl_countocc(wrong):
    a = " + 1" if wrong else ""
    return (f"sub lb {{ my ($nums,$t)=@_; my $lo=0; my $hi=scalar(@$nums);\n"
            f"    while($lo<$hi){{my $mid=int(($lo+$hi)/2); if($nums->[$mid]<$t){{$lo=$mid+1;}}else{{$hi=$mid;}}}} return $lo; }}\n"
            f"sub count_occurrences {{\n"
            f"    my ($nums, $target) = @_;\n"
            f"    return (lb($nums,$target+1) - lb($nums,$target)){a};\n}}\n")


def _c_countocc(wrong):
    a = " + 1" if wrong else ""
    return (f"int lb_co(AtlasIntArray nums, int t) {{ int lo=0,hi=nums.size; while(lo<hi){{int mid=lo+(hi-lo)/2; if(nums.data[mid]<t)lo=mid+1;else hi=mid;}} return lo; }}\n"
            f"int count_occurrences(AtlasIntArray nums, int target) {{\n"
            f"    return (lb_co(nums, target+1) - lb_co(nums, target)){a};\n}}\n")


def _rust_countocc(wrong):
    a = " + 1" if wrong else ""
    return (f"fn lb_co(nums: &Vec<i32>, t: i32) -> i32 {{ let mut lo=0i32; let mut hi=nums.len() as i32;\n"
            f"    while lo<hi {{ let mid=lo+(hi-lo)/2; if nums[mid as usize]<t {{ lo=mid+1; }} else {{ hi=mid; }} }} lo }}\n"
            f"fn count_occurrences(nums: Vec<i32>, target: i32) -> i32 {{\n"
            f"    (lb_co(&nums, target+1) - lb_co(&nums, target)){a}\n}}\n")


# ── delete-and-earn ──────────────────────────────────────────────────────────
def _js_deleteearn(wrong):
    a = " + 1" if wrong else ""
    return (f"function delete_and_earn(nums) {{\n"
            f"    if (nums.length===0) return 0{a};\n"
            f"    const maxV = Math.max(...nums); const bucket = new Array(maxV+1).fill(0);\n"
            f"    for (const x of nums) bucket[x]+=x;\n"
            f"    let prev=0, cur=0;\n"
            f"    for (let v=0;v<=maxV;v++) {{ const t=Math.max(cur, prev+bucket[v]); prev=cur; cur=t; }}\n"
            f"    return cur{a};\n}}\n")


def _ts_deleteearn(wrong):
    a = " + 1" if wrong else ""
    return (f"function delete_and_earn(nums: number[]): number {{\n"
            f"    if (nums.length===0) return 0{a};\n"
            f"    const maxV = Math.max(...nums); const bucket: number[] = new Array(maxV+1).fill(0);\n"
            f"    for (const x of nums) bucket[x]+=x;\n"
            f"    let prev=0, cur=0;\n"
            f"    for (let v=0;v<=maxV;v++) {{ const t=Math.max(cur, prev+bucket[v]); prev=cur; cur=t; }}\n"
            f"    return cur{a};\n}}\n")


def _java_deleteearn(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int delete_and_earn(int[] nums) {{\n"
            f"    if (nums.length==0) return 0{a};\n"
            f"    int maxV=0; for (int x: nums) maxV=Math.max(maxV,x);\n"
            f"    long[] bucket = new long[maxV+1]; for (int x: nums) bucket[x]+=x;\n"
            f"    long prev=0, cur=0;\n"
            f"    for (int v=0;v<=maxV;v++) {{ long t=Math.max(cur, prev+bucket[v]); prev=cur; cur=t; }}\n"
            f"    return (int)(cur{a});\n}} }}\n")


def _cpp_deleteearn(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int delete_and_earn(std::vector<int> nums) {{\n"
            f"    if (nums.empty()) return 0{a};\n"
            f"    int maxV=0; for (int x: nums) maxV=std::max(maxV,x);\n"
            f"    std::vector<long long> bucket(maxV+1, 0); for (int x: nums) bucket[x]+=x;\n"
            f"    long long prev=0, cur=0;\n"
            f"    for (int v=0;v<=maxV;v++) {{ long long t=std::max(cur, prev+bucket[v]); prev=cur; cur=t; }}\n"
            f"    return (int)(cur{a});\n}} }};\n")


def _csharp_deleteearn(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int delete_and_earn(int[] nums) {{\n"
            f"    if (nums.Length==0) return 0{a};\n"
            f"    int maxV=0; foreach (int x in nums) maxV=System.Math.Max(maxV,x);\n"
            f"    long[] bucket = new long[maxV+1]; foreach (int x in nums) bucket[x]+=x;\n"
            f"    long prev=0, cur=0;\n"
            f"    for (int v=0;v<=maxV;v++) {{ long t=System.Math.Max(cur, prev+bucket[v]); prev=cur; cur=t; }}\n"
            f"    return (int)(cur{a});\n}} }}\n")


def _perl_deleteearn(wrong):
    a = " + 1" if wrong else ""
    return (f"sub delete_and_earn {{\n"
            f"    my ($nums) = @_;\n"
            f"    return (0{a}) if scalar(@$nums)==0;\n"
            f"    my $maxV=0; foreach my $x (@$nums) {{ $maxV=$x if $x>$maxV; }}\n"
            f"    my @bucket = (0) x ($maxV+1); foreach my $x (@$nums) {{ $bucket[$x]+=$x; }}\n"
            f"    my $prev=0; my $cur=0;\n"
            f"    for (my $v=0;$v<=$maxV;$v++) {{ my $t=($cur>$prev+$bucket[$v])?$cur:$prev+$bucket[$v]; $prev=$cur; $cur=$t; }}\n"
            f"    return $cur{a};\n}}\n")


def _c_deleteearn(wrong):
    a = " + 1" if wrong else ""
    return (f"int delete_and_earn(AtlasIntArray nums) {{\n"
            f"    if (nums.size==0) return 0{a};\n"
            f"    int maxV=0; for (int i=0;i<nums.size;i++) if (nums.data[i]>maxV) maxV=nums.data[i];\n"
            f"    long long* bucket = (long long*)calloc(maxV+1, sizeof(long long));\n"
            f"    for (int i=0;i<nums.size;i++) bucket[nums.data[i]]+=nums.data[i];\n"
            f"    long long prev=0, cur=0;\n"
            f"    for (int v=0;v<=maxV;v++) {{ long long t=(cur>prev+bucket[v])?cur:prev+bucket[v]; prev=cur; cur=t; }}\n"
            f"    free(bucket);\n"
            f"    return (int)(cur{a});\n}}\n")


def _rust_deleteearn(wrong):
    a = " + 1" if wrong else ""
    return (f"fn delete_and_earn(nums: Vec<i32>) -> i32 {{\n"
            f"    if nums.is_empty() {{ return 0{a}; }}\n"
            f"    let max_v = *nums.iter().max().unwrap() as usize;\n"
            f"    let mut bucket = vec![0i64; max_v+1];\n"
            f"    for &x in nums.iter() {{ bucket[x as usize] += x as i64; }}\n"
            f"    let mut prev: i64 = 0; let mut cur: i64 = 0;\n"
            f"    for v in 0..=max_v {{ let t = cur.max(prev+bucket[v]); prev = cur; cur = t; }}\n"
            f"    (cur{a}) as i32\n}}\n")


# ── euler-phi-sieve (single-n totient, trial division) ──────────────────────
def _js_ephisieve(wrong):
    a = " + 1" if wrong else ""
    return (f"function euler_phi_sieve(n) {{\n"
            f"    let result=n, x=n, p=2;\n"
            f"    while (p*p<=x) {{ if (x%p===0) {{ while (x%p===0) x=Math.floor(x/p); result-=Math.floor(result/p); }} p++; }}\n"
            f"    if (x>1) result-=Math.floor(result/x);\n"
            f"    return result{a};\n}}\n")


def _ts_ephisieve(wrong):
    a = " + 1" if wrong else ""
    return (f"function euler_phi_sieve(n: number): number {{\n"
            f"    let result=n, x=n, p=2;\n"
            f"    while (p*p<=x) {{ if (x%p===0) {{ while (x%p===0) x=Math.floor(x/p); result-=Math.floor(result/p); }} p++; }}\n"
            f"    if (x>1) result-=Math.floor(result/x);\n"
            f"    return result{a};\n}}\n")


def _java_ephisieve(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int euler_phi_sieve(int n) {{\n"
            f"    int result=n, x=n; int p=2;\n"
            f"    while ((long)p*p<=x) {{ if (x%p==0) {{ while (x%p==0) x/=p; result-=result/p; }} p++; }}\n"
            f"    if (x>1) result-=result/x;\n"
            f"    return result{a};\n}} }}\n")


def _cpp_ephisieve(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int euler_phi_sieve(int n) {{\n"
            f"    int result=n, x=n; long long p=2;\n"
            f"    while (p*p<=x) {{ if (x%p==0) {{ while (x%p==0) x/=p; result-=result/p; }} p++; }}\n"
            f"    if (x>1) result-=result/x;\n"
            f"    return result{a};\n}} }};\n")


def _csharp_ephisieve(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int euler_phi_sieve(int n) {{\n"
            f"    int result=n, x=n; long p=2;\n"
            f"    while (p*p<=x) {{ if (x%p==0) {{ while (x%p==0) x/=(int)p; result-=result/(int)p; }} p++; }}\n"
            f"    if (x>1) result-=result/x;\n"
            f"    return result{a};\n}} }}\n")


def _perl_ephisieve(wrong):
    a = " + 1" if wrong else ""
    return (f"use integer;\nsub euler_phi_sieve {{\n"
            f"    my ($n) = @_;\n"
            f"    my $result=$n; my $x=$n; my $p=2;\n"
            f"    while ($p*$p<=$x) {{ if ($x%$p==0) {{ while ($x%$p==0) {{ $x=$x/$p; }} $result-=$result/$p; }} $p++; }}\n"
            f"    if ($x>1) {{ $result-=$result/$x; }}\n"
            f"    return $result{a};\n}}\n")


def _c_ephisieve(wrong):
    a = " + 1" if wrong else ""
    return (f"int euler_phi_sieve(int n) {{\n"
            f"    int result=n, x=n; long long p=2;\n"
            f"    while (p*p<=x) {{ if (x%p==0) {{ while (x%p==0) x/=(int)p; result-=result/(int)p; }} p++; }}\n"
            f"    if (x>1) result-=result/x;\n"
            f"    return result{a};\n}}\n")


def _rust_ephisieve(wrong):
    a = " + 1" if wrong else ""
    return (f"fn euler_phi_sieve(n: i32) -> i32 {{\n"
            f"    let mut result=n; let mut x=n; let mut p: i64=2;\n"
            f"    while p*p<=x as i64 {{ if x%(p as i32)==0 {{ while x%(p as i32)==0 {{ x/=p as i32; }} result-=result/(p as i32); }} p+=1; }}\n"
            f"    if x>1 {{ result-=result/x; }}\n"
            f"    result{a}\n}}\n")


# ── find-minimum-rotated-sorted-array ────────────────────────────────────────
def _js_findmin(wrong):
    a = " + 1" if wrong else ""
    return (f"function find_min(nums) {{\n"
            f"    let lo=0, hi=nums.length-1;\n"
            f"    while (lo<hi) {{ const mid=(lo+hi)>>1; if (nums[mid]>nums[hi]) lo=mid+1; else hi=mid; }}\n"
            f"    return nums[lo]{a};\n}}\n")


def _ts_findmin(wrong):
    a = " + 1" if wrong else ""
    return (f"function find_min(nums: number[]): number {{\n"
            f"    let lo=0, hi=nums.length-1;\n"
            f"    while (lo<hi) {{ const mid=(lo+hi)>>1; if (nums[mid]>nums[hi]) lo=mid+1; else hi=mid; }}\n"
            f"    return nums[lo]{a};\n}}\n")


def _java_findmin(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int find_min(int[] nums) {{\n"
            f"    int lo=0, hi=nums.length-1;\n"
            f"    while (lo<hi) {{ int mid=(lo+hi)>>>1; if (nums[mid]>nums[hi]) lo=mid+1; else hi=mid; }}\n"
            f"    return nums[lo]{a};\n}} }}\n")


def _cpp_findmin(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int find_min(std::vector<int> nums) {{\n"
            f"    int lo=0, hi=(int)nums.size()-1;\n"
            f"    while (lo<hi) {{ int mid=lo+(hi-lo)/2; if (nums[mid]>nums[hi]) lo=mid+1; else hi=mid; }}\n"
            f"    return nums[lo]{a};\n}} }};\n")


def _csharp_findmin(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int find_min(int[] nums) {{\n"
            f"    int lo=0, hi=nums.Length-1;\n"
            f"    while (lo<hi) {{ int mid=lo+(hi-lo)/2; if (nums[mid]>nums[hi]) lo=mid+1; else hi=mid; }}\n"
            f"    return nums[lo]{a};\n}} }}\n")


def _perl_findmin(wrong):
    a = " + 1" if wrong else ""
    return (f"sub find_min {{\n"
            f"    my ($nums) = @_;\n"
            f"    my $lo=0; my $hi=scalar(@$nums)-1;\n"
            f"    while ($lo<$hi) {{ my $mid=int(($lo+$hi)/2); if ($nums->[$mid]>$nums->[$hi]) {{ $lo=$mid+1; }} else {{ $hi=$mid; }} }}\n"
            f"    return $nums->[$lo]{a};\n}}\n")


def _c_findmin(wrong):
    a = " + 1" if wrong else ""
    return (f"int find_min(AtlasIntArray nums) {{\n"
            f"    int lo=0, hi=nums.size-1;\n"
            f"    while (lo<hi) {{ int mid=lo+(hi-lo)/2; if (nums.data[mid]>nums.data[hi]) lo=mid+1; else hi=mid; }}\n"
            f"    return nums.data[lo]{a};\n}}\n")


def _rust_findmin(wrong):
    a = " + 1" if wrong else ""
    return (f"fn find_min(nums: Vec<i32>) -> i32 {{\n"
            f"    let mut lo=0usize; let mut hi=nums.len()-1;\n"
            f"    while lo<hi {{ let mid=lo+(hi-lo)/2; if nums[mid]>nums[hi] {{ lo=mid+1; }} else {{ hi=mid; }} }}\n"
            f"    nums[lo]{a}\n}}\n")


# ── integer-square-root ──────────────────────────────────────────────────────
def _js_isqrt(wrong):
    a = " + 1" if wrong else ""
    return (f"function my_sqrt(n) {{\n"
            f"    let lo=0, hi=46341;\n"
            f"    while (lo<hi) {{ const mid=(lo+hi+1)>>1; if (mid*mid<=n) lo=mid; else hi=mid-1; }}\n"
            f"    return lo{a};\n}}\n")


def _ts_isqrt(wrong):
    a = " + 1" if wrong else ""
    return (f"function my_sqrt(n: number): number {{\n"
            f"    let lo=0, hi=46341;\n"
            f"    while (lo<hi) {{ const mid=(lo+hi+1)>>1; if (mid*mid<=n) lo=mid; else hi=mid-1; }}\n"
            f"    return lo{a};\n}}\n")


def _java_isqrt(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int my_sqrt(int n) {{\n"
            f"    long lo=0, hi=46341;\n"
            f"    while (lo<hi) {{ long mid=(lo+hi+1)/2; if (mid*mid<=n) lo=mid; else hi=mid-1; }}\n"
            f"    return (int)(lo{a});\n}} }}\n")


def _cpp_isqrt(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int my_sqrt(int n) {{\n"
            f"    long long lo=0, hi=46341;\n"
            f"    while (lo<hi) {{ long long mid=(lo+hi+1)/2; if (mid*mid<=n) lo=mid; else hi=mid-1; }}\n"
            f"    return (int)(lo{a});\n}} }};\n")


def _csharp_isqrt(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int my_sqrt(int n) {{\n"
            f"    long lo=0, hi=46341;\n"
            f"    while (lo<hi) {{ long mid=(lo+hi+1)/2; if (mid*mid<=n) lo=mid; else hi=mid-1; }}\n"
            f"    return (int)(lo{a});\n}} }}\n")


def _perl_isqrt(wrong):
    a = " + 1" if wrong else ""
    return (f"sub my_sqrt {{\n"
            f"    my ($n) = @_;\n"
            f"    my $lo=0; my $hi=46341;\n"
            f"    while ($lo<$hi) {{ my $mid=int(($lo+$hi+1)/2); if ($mid*$mid<=$n) {{ $lo=$mid; }} else {{ $hi=$mid-1; }} }}\n"
            f"    return $lo{a};\n}}\n")


def _c_isqrt(wrong):
    a = " + 1" if wrong else ""
    return (f"int my_sqrt(int n) {{\n"
            f"    long long lo=0, hi=46341;\n"
            f"    while (lo<hi) {{ long long mid=(lo+hi+1)/2; if (mid*mid<=n) lo=mid; else hi=mid-1; }}\n"
            f"    return (int)(lo{a});\n}}\n")


def _rust_isqrt(wrong):
    a = " + 1" if wrong else ""
    return (f"fn my_sqrt(n: i32) -> i32 {{\n"
            f"    let (mut lo, mut hi): (i64, i64) = (0, 46341);\n"
            f"    while lo<hi {{ let mid=(lo+hi+1)/2; if mid*mid<=n as i64 {{ lo=mid; }} else {{ hi=mid-1; }} }}\n"
            f"    (lo{a}) as i32\n}}\n")


_BUILDERS = {
    "bitonic-peak-index": {"javascript": _js_bitonic, "typescript": _ts_bitonic, "java": _java_bitonic, "cpp": _cpp_bitonic,
                           "csharp": _csharp_bitonic, "perl": _perl_bitonic, "c": _c_bitonic, "rust": _rust_bitonic},
    "coin-change": {"javascript": _js_coinchange, "typescript": _ts_coinchange, "java": _java_coinchange, "cpp": _cpp_coinchange,
                    "csharp": _csharp_coinchange, "perl": _perl_coinchange, "c": _c_coinchange, "rust": _rust_coinchange},
    "coin-change-ways": {"javascript": _js_coinways, "typescript": _ts_coinways, "java": _java_coinways, "cpp": _cpp_coinways,
                         "csharp": _csharp_coinways, "perl": _perl_coinways, "c": _c_coinways, "rust": _rust_coinways},
    "count-occurrences-sorted": {"javascript": _js_countocc, "typescript": _ts_countocc, "java": _java_countocc, "cpp": _cpp_countocc,
                                 "csharp": _csharp_countocc, "perl": _perl_countocc, "c": _c_countocc, "rust": _rust_countocc},
    "delete-and-earn": {"javascript": _js_deleteearn, "typescript": _ts_deleteearn, "java": _java_deleteearn, "cpp": _cpp_deleteearn,
                        "csharp": _csharp_deleteearn, "perl": _perl_deleteearn, "c": _c_deleteearn, "rust": _rust_deleteearn},
    "euler-phi-sieve": {"javascript": _js_ephisieve, "typescript": _ts_ephisieve, "java": _java_ephisieve, "cpp": _cpp_ephisieve,
                        "csharp": _csharp_ephisieve, "perl": _perl_ephisieve, "c": _c_ephisieve, "rust": _rust_ephisieve},
    "find-minimum-rotated-sorted-array": {"javascript": _js_findmin, "typescript": _ts_findmin, "java": _java_findmin, "cpp": _cpp_findmin,
                                          "csharp": _csharp_findmin, "perl": _perl_findmin, "c": _c_findmin, "rust": _rust_findmin},
    "integer-square-root": {"javascript": _js_isqrt, "typescript": _ts_isqrt, "java": _java_isqrt, "cpp": _cpp_isqrt,
                            "csharp": _csharp_isqrt, "perl": _perl_isqrt, "c": _c_isqrt, "rust": _rust_isqrt},
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
                    adapter_version=f"{lang}-function-mega1-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
