"""Scales the final 17 problems (Function Mode) across the 8 original
working languages: maximum-subarray-circular, meeting-rooms,
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


# ── maximum-subarray-circular (Kadane + total-minus-min, all-negative edge) ─
def _js_maxsubcirc(wrong):
    a = " + 1" if wrong else ""
    return (f"function max_subarray_sum_circular(nums) {{\n"
            f"    let total=0, curMax=0, best=-Infinity, curMin=0, worst=Infinity;\n"
            f"    for (const x of nums) {{\n"
            f"        total+=x;\n"
            f"        curMax=Math.max(curMax+x,x); best=Math.max(best,curMax);\n"
            f"        curMin=Math.min(curMin+x,x); worst=Math.min(worst,curMin);\n"
            f"    }}\n"
            f"    if (best<0) return best{a};\n"
            f"    return Math.max(best, total-worst){a};\n}}\n")


def _ts_maxsubcirc(wrong):
    a = " + 1" if wrong else ""
    return (f"function max_subarray_sum_circular(nums: number[]): number {{\n"
            f"    let total=0, curMax=0, best=-Infinity, curMin=0, worst=Infinity;\n"
            f"    for (const x of nums) {{\n"
            f"        total+=x;\n"
            f"        curMax=Math.max(curMax+x,x); best=Math.max(best,curMax);\n"
            f"        curMin=Math.min(curMin+x,x); worst=Math.min(worst,curMin);\n"
            f"    }}\n"
            f"    if (best<0) return best{a};\n"
            f"    return Math.max(best, total-worst){a};\n}}\n")


def _java_maxsubcirc(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int max_subarray_sum_circular(int[] nums) {{\n"
            f"    long total=0, curMax=0, best=Long.MIN_VALUE, curMin=0, worst=Long.MAX_VALUE;\n"
            f"    for (int x: nums) {{\n"
            f"        total+=x;\n"
            f"        curMax=Math.max(curMax+x,x); best=Math.max(best,curMax);\n"
            f"        curMin=Math.min(curMin+x,x); worst=Math.min(worst,curMin);\n"
            f"    }}\n"
            f"    if (best<0) return (int)(best{a});\n"
            f"    return (int)(Math.max(best, total-worst){a});\n}} }}\n")


def _cpp_maxsubcirc(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int max_subarray_sum_circular(std::vector<int> nums) {{\n"
            f"    long long total=0, curMax=0, best=LLONG_MIN, curMin=0, worst=LLONG_MAX;\n"
            f"    for (int x: nums) {{\n"
            f"        total+=x;\n"
            f"        curMax=std::max(curMax+x,(long long)x); best=std::max(best,curMax);\n"
            f"        curMin=std::min(curMin+x,(long long)x); worst=std::min(worst,curMin);\n"
            f"    }}\n"
            f"    if (best<0) return (int)(best{a});\n"
            f"    return (int)(std::max(best, total-worst){a});\n}} }};\n")


def _csharp_maxsubcirc(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int max_subarray_sum_circular(int[] nums) {{\n"
            f"    long total=0, curMax=0, best=long.MinValue, curMin=0, worst=long.MaxValue;\n"
            f"    foreach (int x in nums) {{\n"
            f"        total+=x;\n"
            f"        curMax=System.Math.Max(curMax+x,x); best=System.Math.Max(best,curMax);\n"
            f"        curMin=System.Math.Min(curMin+x,x); worst=System.Math.Min(worst,curMin);\n"
            f"    }}\n"
            f"    if (best<0) return (int)(best{a});\n"
            f"    return (int)(System.Math.Max(best, total-worst){a});\n}} }}\n")


def _perl_maxsubcirc(wrong):
    a = " + 1" if wrong else ""
    return (f"sub max_subarray_sum_circular {{\n"
            f"    my ($nums) = @_;\n"
            f"    my $total=0; my $curMax=0; my $best=-9**9**9; my $curMin=0; my $worst=9**9**9;\n"
            f"    foreach my $x (@$nums) {{\n"
            f"        $total+=$x;\n"
            f"        $curMax=($curMax+$x>$x)?$curMax+$x:$x; $best=$curMax if $curMax>$best;\n"
            f"        $curMin=($curMin+$x<$x)?$curMin+$x:$x; $worst=$curMin if $curMin<$worst;\n"
            f"    }}\n"
            f"    return $best{a} if $best<0;\n"
            f"    my $alt = $total-$worst;\n"
            f"    return (($best>$alt)?$best:$alt){a};\n}}\n")


def _c_maxsubcirc(wrong):
    a = " + 1" if wrong else ""
    return (f"int max_subarray_sum_circular(AtlasIntArray nums) {{\n"
            f"    long long total=0, curMax=0, best=LLONG_MIN, curMin=0, worst=LLONG_MAX;\n"
            f"    for (int i=0;i<nums.size;i++) {{\n"
            f"        int x=nums.data[i];\n"
            f"        total+=x;\n"
            f"        curMax = (curMax+x>x)?curMax+x:x; if (curMax>best) best=curMax;\n"
            f"        curMin = (curMin+x<x)?curMin+x:x; if (curMin<worst) worst=curMin;\n"
            f"    }}\n"
            f"    if (best<0) return (int)(best{a});\n"
            f"    long long alt = total-worst;\n"
            f"    return (int)(((best>alt)?best:alt){a});\n}}\n")


def _rust_maxsubcirc(wrong):
    a = " + 1" if wrong else ""
    return (f"fn max_subarray_sum_circular(nums: Vec<i32>) -> i32 {{\n"
            f"    let mut total: i64=0; let mut cur_max: i64=0; let mut best: i64=i64::MIN;\n"
            f"    let mut cur_min: i64=0; let mut worst: i64=i64::MAX;\n"
            f"    for x in nums.iter() {{\n"
            f"        let x = *x as i64;\n"
            f"        total+=x;\n"
            f"        cur_max = (cur_max+x).max(x); best=best.max(cur_max);\n"
            f"        cur_min = (cur_min+x).min(x); worst=worst.min(cur_min);\n"
            f"    }}\n"
            f"    if best<0 {{ return (best{a}) as i32; }}\n"
            f"    (best.max(total-worst){a}) as i32\n}}\n")


# ── meeting-rooms (min rooms via two-pointer sweep) ──────────────────────────
def _js_meetrooms(wrong):
    a = " + 1" if wrong else ""
    return (f"function min_meeting_rooms(starts, ends) {{\n"
            f"    const s=starts.slice().sort((a,b)=>a-b), e=ends.slice().sort((a,b)=>a-b);\n"
            f"    let rooms=0, best=0, si=0, ei=0;\n"
            f"    while (si<s.length) {{\n"
            f"        if (s[si]<e[ei]) {{ rooms++; si++; best=Math.max(best,rooms); }}\n"
            f"        else {{ rooms--; ei++; }}\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _ts_meetrooms(wrong):
    a = " + 1" if wrong else ""
    return (f"function min_meeting_rooms(starts: number[], ends: number[]): number {{\n"
            f"    const s=starts.slice().sort((a,b)=>a-b), e=ends.slice().sort((a,b)=>a-b);\n"
            f"    let rooms=0, best=0, si=0, ei=0;\n"
            f"    while (si<s.length) {{\n"
            f"        if (s[si]<e[ei]) {{ rooms++; si++; best=Math.max(best,rooms); }}\n"
            f"        else {{ rooms--; ei++; }}\n"
            f"    }}\n"
            f"    return best{a};\n}}\n")


def _java_meetrooms(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int min_meeting_rooms(int[] starts, int[] ends) {{\n"
            f"    int[] s=starts.clone(), e=ends.clone(); java.util.Arrays.sort(s); java.util.Arrays.sort(e);\n"
            f"    int rooms=0, best=0, si=0, ei=0;\n"
            f"    while (si<s.length) {{\n"
            f"        if (s[si]<e[ei]) {{ rooms++; si++; best=Math.max(best,rooms); }}\n"
            f"        else {{ rooms--; ei++; }}\n"
            f"    }}\n"
            f"    return best{a};\n}} }}\n")


def _cpp_meetrooms(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int min_meeting_rooms(std::vector<int> starts, std::vector<int> ends) {{\n"
            f"    std::vector<int> s=starts, e=ends; std::sort(s.begin(),s.end()); std::sort(e.begin(),e.end());\n"
            f"    int rooms=0, best=0; size_t si=0, ei=0;\n"
            f"    while (si<s.size()) {{\n"
            f"        if (s[si]<e[ei]) {{ rooms++; si++; best=std::max(best,rooms); }}\n"
            f"        else {{ rooms--; ei++; }}\n"
            f"    }}\n"
            f"    return best{a};\n}} }};\n")


def _csharp_meetrooms(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int min_meeting_rooms(int[] starts, int[] ends) {{\n"
            f"    int[] s=(int[])starts.Clone(), e=(int[])ends.Clone(); System.Array.Sort(s); System.Array.Sort(e);\n"
            f"    int rooms=0, best=0, si=0, ei=0;\n"
            f"    while (si<s.Length) {{\n"
            f"        if (s[si]<e[ei]) {{ rooms++; si++; best=System.Math.Max(best,rooms); }}\n"
            f"        else {{ rooms--; ei++; }}\n"
            f"    }}\n"
            f"    return best{a};\n}} }}\n")


def _perl_meetrooms(wrong):
    a = " + 1" if wrong else ""
    return (f"sub min_meeting_rooms {{\n"
            f"    my ($starts, $ends) = @_;\n"
            f"    my @s = sort {{ $a <=> $b }} @$starts; my @e = sort {{ $a <=> $b }} @$ends;\n"
            f"    my $rooms=0; my $best=0; my $si=0; my $ei=0;\n"
            f"    while ($si<scalar(@s)) {{\n"
            f"        if ($s[$si]<$e[$ei]) {{ $rooms++; $si++; $best=$rooms if $rooms>$best; }}\n"
            f"        else {{ $rooms--; $ei++; }}\n"
            f"    }}\n"
            f"    return $best{a};\n}}\n")


def _c_meetrooms(wrong):
    a = " + 1" if wrong else ""
    return (f"int cmp_int_asc(const void* a, const void* b) {{ return *(const int*)a - *(const int*)b; }}\n"
            f"int min_meeting_rooms(AtlasIntArray starts, AtlasIntArray ends) {{\n"
            f"    int n = starts.size;\n"
            f"    int* s = (int*)malloc(sizeof(int)*(n>0?n:1)); int* e = (int*)malloc(sizeof(int)*(n>0?n:1));\n"
            f"    for (int i=0;i<n;i++) {{ s[i]=starts.data[i]; e[i]=ends.data[i]; }}\n"
            f"    qsort(s, n, sizeof(int), cmp_int_asc); qsort(e, n, sizeof(int), cmp_int_asc);\n"
            f"    int rooms=0, best=0, si=0, ei=0;\n"
            f"    while (si<n) {{\n"
            f"        if (s[si]<e[ei]) {{ rooms++; si++; if (rooms>best) best=rooms; }}\n"
            f"        else {{ rooms--; ei++; }}\n"
            f"    }}\n"
            f"    free(s); free(e);\n"
            f"    return best{a};\n}}\n")


def _rust_meetrooms(wrong):
    a = " + 1" if wrong else ""
    return (f"fn min_meeting_rooms(starts: Vec<i32>, ends: Vec<i32>) -> i32 {{\n"
            f"    let mut s = starts.clone(); let mut e = ends.clone(); s.sort(); e.sort();\n"
            f"    let mut rooms=0i32; let mut best=0i32; let mut si=0usize; let mut ei=0usize;\n"
            f"    while si<s.len() {{\n"
            f"        if s[si]<e[ei] {{ rooms+=1; si+=1; best=best.max(rooms); }}\n"
            f"        else {{ rooms-=1; ei+=1; }}\n"
            f"    }}\n"
            f"    best{a}\n}}\n")


# ── merge-sorted-arrays-inplace / merge-two-sorted-lists (same merge algo) ──
def _merge_body(fname, lang):
    if lang == "js":
        return (f"function {fname}(a, b) {{\n"
                f"    const out=[]; let i=0,j=0;\n"
                f"    while (i<a.length && j<b.length) {{ if (a[i]<=b[j]) out.push(a[i++]); else out.push(b[j++]); }}\n"
                f"    while (i<a.length) out.push(a[i++]);\n"
                f"    while (j<b.length) out.push(b[j++]);\n"
                f"    return out;\n}}\n")
    if lang == "ts":
        return (f"function {fname}(a: number[], b: number[]): number[] {{\n"
                f"    const out: number[]=[]; let i=0,j=0;\n"
                f"    while (i<a.length && j<b.length) {{ if (a[i]<=b[j]) out.push(a[i++]); else out.push(b[j++]); }}\n"
                f"    while (i<a.length) out.push(a[i++]);\n"
                f"    while (j<b.length) out.push(b[j++]);\n"
                f"    return out;\n}}\n")
    if lang == "java":
        return (f"class Solution {{ public int[] {fname}(int[] a, int[] b) {{\n"
                f"    int[] out = new int[a.length+b.length]; int i=0,j=0,k=0;\n"
                f"    while (i<a.length && j<b.length) {{ if (a[i]<=b[j]) out[k++]=a[i++]; else out[k++]=b[j++]; }}\n"
                f"    while (i<a.length) out[k++]=a[i++];\n"
                f"    while (j<b.length) out[k++]=b[j++];\n"
                f"    return out;\n}} }}\n")
    if lang == "cpp":
        return (f"class Solution {{ public: std::vector<int> {fname}(std::vector<int> a, std::vector<int> b) {{\n"
                f"    std::vector<int> out; size_t i=0,j=0;\n"
                f"    while (i<a.size() && j<b.size()) {{ if (a[i]<=b[j]) out.push_back(a[i++]); else out.push_back(b[j++]); }}\n"
                f"    while (i<a.size()) out.push_back(a[i++]);\n"
                f"    while (j<b.size()) out.push_back(b[j++]);\n"
                f"    return out;\n}} }};\n")
    if lang == "csharp":
        return (f"class Solution {{ public static int[] {fname}(int[] a, int[] b) {{\n"
                f"    int[] outArr = new int[a.Length+b.Length]; int i=0,j=0,k=0;\n"
                f"    while (i<a.Length && j<b.Length) {{ if (a[i]<=b[j]) outArr[k++]=a[i++]; else outArr[k++]=b[j++]; }}\n"
                f"    while (i<a.Length) outArr[k++]=a[i++];\n"
                f"    while (j<b.Length) outArr[k++]=b[j++];\n"
                f"    return outArr;\n}} }}\n")
    if lang == "perl":
        return (f"sub {fname} {{\n"
                f"    my ($a, $b) = @_;\n"
                f"    my @out; my $i=0; my $j=0;\n"
                f"    while ($i<scalar(@$a) && $j<scalar(@$b)) {{ if ($a->[$i]<=$b->[$j]) {{ push @out, $a->[$i]; $i++; }} else {{ push @out, $b->[$j]; $j++; }} }}\n"
                f"    while ($i<scalar(@$a)) {{ push @out, $a->[$i]; $i++; }}\n"
                f"    while ($j<scalar(@$b)) {{ push @out, $b->[$j]; $j++; }}\n"
                f"    return \\@out;\n}}\n")
    if lang == "c":
        return (f"AtlasIntArray {fname}(AtlasIntArray a, AtlasIntArray b) {{\n"
                f"    int* out = (int*)malloc(sizeof(int)*(a.size+b.size+1)); int i=0,j=0,k=0;\n"
                f"    while (i<a.size && j<b.size) {{ if (a.data[i]<=b.data[j]) out[k++]=a.data[i++]; else out[k++]=b.data[j++]; }}\n"
                f"    while (i<a.size) out[k++]=a.data[i++];\n"
                f"    while (j<b.size) out[k++]=b.data[j++];\n"
                f"    AtlasIntArray result; result.size=k; result.data=out;\n"
                f"    return result;\n}}\n")
    if lang == "rust":
        return (f"fn {fname}(a: Vec<i32>, b: Vec<i32>) -> Vec<i32> {{\n"
                f"    let mut out: Vec<i32> = Vec::new(); let mut i=0usize; let mut j=0usize;\n"
                f"    while i<a.len() && j<b.len() {{ if a[i]<=b[j] {{ out.push(a[i]); i+=1; }} else {{ out.push(b[j]); j+=1; }} }}\n"
                f"    while i<a.len() {{ out.push(a[i]); i+=1; }}\n"
                f"    while j<b.len() {{ out.push(b[j]); j+=1; }}\n"
                f"    out\n}}\n")


def _js_mergesorted(wrong):
    body = _merge_body("merge_sorted", "js")
    if wrong:
        body = body.replace("return out;", "return out.map(x => x + 1);")
    return body


def _ts_mergesorted(wrong):
    body = _merge_body("merge_sorted", "ts")
    if wrong:
        body = body.replace("return out;", "return out.map(x => x + 1);")
    return body


def _java_mergesorted(wrong):
    body = _merge_body("merge_sorted", "java")
    if wrong:
        body = body.replace("return out;", "for (int i=0;i<out.length;i++) out[i]++; return out;")
    return body


def _cpp_mergesorted(wrong):
    body = _merge_body("merge_sorted", "cpp")
    if wrong:
        body = body.replace("return out;", "for (auto& x: out) x++; return out;")
    return body


def _csharp_mergesorted(wrong):
    body = _merge_body("merge_sorted", "csharp")
    if wrong:
        body = body.replace("return outArr;", "for (int i=0;i<outArr.Length;i++) outArr[i]++; return outArr;")
    return body


def _perl_mergesorted(wrong):
    body = _merge_body("merge_sorted", "perl")
    if wrong:
        body = body.replace("return \\@out;", "@out = map { $_ + 1 } @out;\n    return \\@out;")
    return body


def _c_mergesorted(wrong):
    body = _merge_body("merge_sorted", "c")
    if wrong:
        body = body.replace("AtlasIntArray result; result.size=k; result.data=out;",
                             "for (int q=0;q<k;q++) out[q]++;\n    AtlasIntArray result; result.size=k; result.data=out;")
    return body


def _rust_mergesorted(wrong):
    body = _merge_body("merge_sorted", "rust")
    if wrong:
        body = body.replace("    out\n}", "    for x in out.iter_mut() { *x += 1; }\n    out\n}")
    return body


def _js_mergetwolists(wrong):
    body = _merge_body("merge_two_lists", "js")
    if wrong:
        body = body.replace("return out;", "return out.map(x => x + 1);")
    return body


def _ts_mergetwolists(wrong):
    body = _merge_body("merge_two_lists", "ts")
    if wrong:
        body = body.replace("return out;", "return out.map(x => x + 1);")
    return body


def _java_mergetwolists(wrong):
    body = _merge_body("merge_two_lists", "java")
    if wrong:
        body = body.replace("return out;", "for (int i=0;i<out.length;i++) out[i]++; return out;")
    return body


def _cpp_mergetwolists(wrong):
    body = _merge_body("merge_two_lists", "cpp")
    if wrong:
        body = body.replace("return out;", "for (auto& x: out) x++; return out;")
    return body


def _csharp_mergetwolists(wrong):
    body = _merge_body("merge_two_lists", "csharp")
    if wrong:
        body = body.replace("return outArr;", "for (int i=0;i<outArr.Length;i++) outArr[i]++; return outArr;")
    return body


def _perl_mergetwolists(wrong):
    body = _merge_body("merge_two_lists", "perl")
    if wrong:
        body = body.replace("return \\@out;", "@out = map { $_ + 1 } @out;\n    return \\@out;")
    return body


def _c_mergetwolists(wrong):
    body = _merge_body("merge_two_lists", "c")
    if wrong:
        body = body.replace("AtlasIntArray result; result.size=k; result.data=out;",
                             "for (int q=0;q<k;q++) out[q]++;\n    AtlasIntArray result; result.size=k; result.data=out;")
    return body


def _rust_mergetwolists(wrong):
    body = _merge_body("merge_two_lists", "rust")
    if wrong:
        body = body.replace("    out\n}", "    for x in out.iter_mut() { *x += 1; }\n    out\n}")
    return body


# ── middle-of-linked-list (values[n/2]) ──────────────────────────────────────
def _js_midlist(wrong):
    a = " + 1" if wrong else ""
    return f"function middle_node(values) {{\n    return values[Math.floor(values.length/2)]{a};\n}}\n"


def _ts_midlist(wrong):
    a = " + 1" if wrong else ""
    return f"function middle_node(values: number[]): number {{\n    return values[Math.floor(values.length/2)]{a};\n}}\n"


def _java_midlist(wrong):
    a = " + 1" if wrong else ""
    return f"class Solution {{ public int middle_node(int[] values) {{\n    return values[values.length/2]{a};\n}} }}\n"


def _cpp_midlist(wrong):
    a = " + 1" if wrong else ""
    return f"class Solution {{ public: int middle_node(std::vector<int> values) {{\n    return values[values.size()/2]{a};\n}} }};\n"


def _csharp_midlist(wrong):
    a = " + 1" if wrong else ""
    return f"class Solution {{ public static int middle_node(int[] values) {{\n    return values[values.Length/2]{a};\n}} }}\n"


def _perl_midlist(wrong):
    a = " + 1" if wrong else ""
    return f"sub middle_node {{\n    my ($values) = @_;\n    return $values->[int(scalar(@$values)/2)]{a};\n}}\n"


def _c_midlist(wrong):
    a = " + 1" if wrong else ""
    return f"int middle_node(AtlasIntArray values) {{\n    return values.data[values.size/2]{a};\n}}\n"


def _rust_midlist(wrong):
    a = " + 1" if wrong else ""
    return f"fn middle_node(values: Vec<i32>) -> i32 {{\n    values[values.len()/2]{a}\n}}\n"


# ── min-subarray-len-target-sum (sliding window, 0 if none) ─────────────────
def _js_minsublen(wrong):
    a = " + 1" if wrong else ""
    return (f"function min_subarray_len(nums, target) {{\n"
            f"    let left=0, sum=0, best=Infinity;\n"
            f"    for (let right=0;right<nums.length;right++) {{\n"
            f"        sum+=nums[right];\n"
            f"        while (sum>=target) {{ best=Math.min(best, right-left+1); sum-=nums[left]; left++; }}\n"
            f"    }}\n"
            f"    const r = best===Infinity?0:best;\n"
            f"    return r===0?r:r{a};\n}}\n")


def _ts_minsublen(wrong):
    a = " + 1" if wrong else ""
    return (f"function min_subarray_len(nums: number[], target: number): number {{\n"
            f"    let left=0, sum=0, best=Infinity;\n"
            f"    for (let right=0;right<nums.length;right++) {{\n"
            f"        sum+=nums[right];\n"
            f"        while (sum>=target) {{ best=Math.min(best, right-left+1); sum-=nums[left]; left++; }}\n"
            f"    }}\n"
            f"    const r = best===Infinity?0:best;\n"
            f"    return r===0?r:r{a};\n}}\n")


def _java_minsublen(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int min_subarray_len(int[] nums, int target) {{\n"
            f"    int left=0; long sum=0; int best=Integer.MAX_VALUE;\n"
            f"    for (int right=0;right<nums.length;right++) {{\n"
            f"        sum+=nums[right];\n"
            f"        while (sum>=target) {{ best=Math.min(best, right-left+1); sum-=nums[left]; left++; }}\n"
            f"    }}\n"
            f"    int r = best==Integer.MAX_VALUE?0:best;\n"
            f"    return r==0?r:r{a};\n}} }}\n")


def _cpp_minsublen(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int min_subarray_len(std::vector<int> nums, int target) {{\n"
            f"    int left=0; long long sum=0; int best=INT_MAX;\n"
            f"    for (int right=0;right<(int)nums.size();right++) {{\n"
            f"        sum+=nums[right];\n"
            f"        while (sum>=target) {{ best=std::min(best, right-left+1); sum-=nums[left]; left++; }}\n"
            f"    }}\n"
            f"    int r = best==INT_MAX?0:best;\n"
            f"    return r==0?r:r{a};\n}} }};\n")


def _csharp_minsublen(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int min_subarray_len(int[] nums, int target) {{\n"
            f"    int left=0; long sum=0; int best=int.MaxValue;\n"
            f"    for (int right=0;right<nums.Length;right++) {{\n"
            f"        sum+=nums[right];\n"
            f"        while (sum>=target) {{ best=System.Math.Min(best, right-left+1); sum-=nums[left]; left++; }}\n"
            f"    }}\n"
            f"    int r = best==int.MaxValue?0:best;\n"
            f"    return r==0?r:r{a};\n}} }}\n")


def _perl_minsublen(wrong):
    a = " + 1" if wrong else ""
    return (f"sub min_subarray_len {{\n"
            f"    my ($nums, $target) = @_;\n"
            f"    my $left=0; my $sum=0; my $best=9**9**9;\n"
            f"    for (my $right=0;$right<scalar(@$nums);$right++) {{\n"
            f"        $sum+=$nums->[$right];\n"
            f"        while ($sum>=$target) {{ my $len=$right-$left+1; $best=$len if $len<$best; $sum-=$nums->[$left]; $left++; }}\n"
            f"    }}\n"
            f"    my $r = ($best==9**9**9)?0:$best;\n"
            f"    return ($r==0)?$r:$r{a};\n}}\n")


def _c_minsublen(wrong):
    a = " + 1" if wrong else ""
    return (f"int min_subarray_len(AtlasIntArray nums, int target) {{\n"
            f"    int left=0; long long sum=0; int best=2147483647;\n"
            f"    for (int right=0;right<nums.size;right++) {{\n"
            f"        sum+=nums.data[right];\n"
            f"        while (sum>=target) {{ int len=right-left+1; if (len<best) best=len; sum-=nums.data[left]; left++; }}\n"
            f"    }}\n"
            f"    int r = (best==2147483647)?0:best;\n"
            f"    return r==0?r:r{a};\n}}\n")


def _rust_minsublen(wrong):
    a = " + 1" if wrong else ""
    return (f"fn min_subarray_len(nums: Vec<i32>, target: i32) -> i32 {{\n"
            f"    let mut left=0i32; let mut sum: i64=0; let mut best=i32::MAX;\n"
            f"    for right in 0..nums.len() as i32 {{\n"
            f"        sum += nums[right as usize] as i64;\n"
            f"        while sum>=target as i64 {{ best=best.min(right-left+1); sum -= nums[left as usize] as i64; left+=1; }}\n"
            f"    }}\n"
            f"    let r = if best==i32::MAX {{ 0 }} else {{ best }};\n"
            f"    if r==0 {{ r }} else {{ r{a} }}\n}}\n")


# ── minimum-knight-moves (BFS w/ HashSet visited, symmetric abs coords) ─────
def _js_knight(wrong):
    a = " + 1" if wrong else ""
    return (f"function min_knight_moves(x, y) {{\n"
            f"    x=Math.abs(x); y=Math.abs(y);\n"
            f"    const moves=[[1,2],[2,1],[-1,2],[-2,1],[1,-2],[2,-1],[-1,-2],[-2,-1]];\n"
            f"    const visited=new Set(['0,0']); let q=[[0,0,0]]; let qi=0;\n"
            f"    while (qi<q.length) {{\n"
            f"        const [cx,cy,d]=q[qi]; qi++;\n"
            f"        if (cx===x && cy===y) return d{a};\n"
            f"        for (const [dx,dy] of moves) {{\n"
            f"            const nx=cx+dx, ny=cy+dy;\n"
            f"            if (nx>=-2 && ny>=-2 && nx<=x+2 && ny<=y+2) {{\n"
            f"                const key=nx+','+ny;\n"
            f"                if (!visited.has(key)) {{ visited.add(key); q.push([nx,ny,d+1]); }}\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return -1;\n}}\n")


def _ts_knight(wrong):
    a = " + 1" if wrong else ""
    return (f"function min_knight_moves(x: number, y: number): number {{\n"
            f"    x=Math.abs(x); y=Math.abs(y);\n"
            f"    const moves: number[][]=[[1,2],[2,1],[-1,2],[-2,1],[1,-2],[2,-1],[-1,-2],[-2,-1]];\n"
            f"    const visited=new Set<string>(['0,0']); let q: number[][]=[[0,0,0]]; let qi=0;\n"
            f"    while (qi<q.length) {{\n"
            f"        const [cx,cy,d]=q[qi]; qi++;\n"
            f"        if (cx===x && cy===y) return d{a};\n"
            f"        for (const [dx,dy] of moves) {{\n"
            f"            const nx=cx+dx, ny=cy+dy;\n"
            f"            if (nx>=-2 && ny>=-2 && nx<=x+2 && ny<=y+2) {{\n"
            f"                const key=nx+','+ny;\n"
            f"                if (!visited.has(key)) {{ visited.add(key); q.push([nx,ny,d+1]); }}\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return -1;\n}}\n")


def _java_knight(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int min_knight_moves(int x, int y) {{\n"
            f"    x=Math.abs(x); y=Math.abs(y);\n"
            f"    int[][] moves = {{{{1,2}},{{2,1}},{{-1,2}},{{-2,1}},{{1,-2}},{{2,-1}},{{-1,-2}},{{-2,-1}}}};\n"
            f"    java.util.Set<String> visited = new java.util.HashSet<>(); visited.add(\"0,0\");\n"
            f"    java.util.Deque<int[]> q = new java.util.ArrayDeque<>(); q.add(new int[]{{0,0,0}});\n"
            f"    while (!q.isEmpty()) {{\n"
            f"        int[] cur = q.poll(); int cx=cur[0], cy=cur[1], d=cur[2];\n"
            f"        if (cx==x && cy==y) return d{a};\n"
            f"        for (int[] mv : moves) {{\n"
            f"            int nx=cx+mv[0], ny=cy+mv[1];\n"
            f"            if (nx>=-2 && ny>=-2 && nx<=x+2 && ny<=y+2) {{\n"
            f"                String key = nx+\",\"+ny;\n"
            f"                if (!visited.contains(key)) {{ visited.add(key); q.add(new int[]{{nx,ny,d+1}}); }}\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return -1;\n}} }}\n")


def _cpp_knight(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int min_knight_moves(int x, int y) {{\n"
            f"    x=std::abs(x); y=std::abs(y);\n"
            f"    int mvx[8]={{1,2,-1,-2,1,2,-1,-2}}; int mvy[8]={{2,1,2,1,-2,-1,-2,-1}};\n"
            f"    std::set<std::pair<int,int>> visited; visited.insert({{0,0}});\n"
            f"    std::queue<std::tuple<int,int,int>> q; q.push({{0,0,0}});\n"
            f"    while (!q.empty()) {{\n"
            f"        auto [cx,cy,d] = q.front(); q.pop();\n"
            f"        if (cx==x && cy==y) return d{a};\n"
            f"        for (int k=0;k<8;k++) {{\n"
            f"            int nx=cx+mvx[k], ny=cy+mvy[k];\n"
            f"            if (nx>=-2 && ny>=-2 && nx<=x+2 && ny<=y+2) {{\n"
            f"                if (!visited.count({{nx,ny}})) {{ visited.insert({{nx,ny}}); q.push({{nx,ny,d+1}}); }}\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return -1;\n}} }};\n")


def _csharp_knight(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int min_knight_moves(int x, int y) {{\n"
            f"    x=System.Math.Abs(x); y=System.Math.Abs(y);\n"
            f"    int[] mvx = {{1,2,-1,-2,1,2,-1,-2}}; int[] mvy = {{2,1,2,1,-2,-1,-2,-1}};\n"
            f"    var visited = new System.Collections.Generic.HashSet<(int,int)>(); visited.Add((0,0));\n"
            f"    var q = new System.Collections.Generic.Queue<(int,int,int)>(); q.Enqueue((0,0,0));\n"
            f"    while (q.Count>0) {{\n"
            f"        var (cx,cy,d) = q.Dequeue();\n"
            f"        if (cx==x && cy==y) return d{a};\n"
            f"        for (int k=0;k<8;k++) {{\n"
            f"            int nx=cx+mvx[k], ny=cy+mvy[k];\n"
            f"            if (nx>=-2 && ny>=-2 && nx<=x+2 && ny<=y+2) {{\n"
            f"                if (!visited.Contains((nx,ny))) {{ visited.Add((nx,ny)); q.Enqueue((nx,ny,d+1)); }}\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return -1;\n}} }}\n")


def _perl_knight(wrong):
    a = " + 1" if wrong else ""
    return (f"sub min_knight_moves {{\n"
            f"    my ($x, $y) = @_;\n"
            f"    $x=abs($x); $y=abs($y);\n"
            f"    my @mvx=(1,2,-1,-2,1,2,-1,-2); my @mvy=(2,1,2,1,-2,-1,-2,-1);\n"
            f"    my %visited=('0,0'=>1); my @q=([0,0,0]); my $qi=0;\n"
            f"    while ($qi<scalar(@q)) {{\n"
            f"        my ($cx,$cy,$d) = @{{$q[$qi]}}; $qi++;\n"
            f"        return $d{a} if $cx==$x && $cy==$y;\n"
            f"        for (my $k=0;$k<8;$k++) {{\n"
            f"            my $nx=$cx+$mvx[$k]; my $ny=$cy+$mvy[$k];\n"
            f"            if ($nx>=-2 && $ny>=-2 && $nx<=$x+2 && $ny<=$y+2) {{\n"
            f"                my $key=\"$nx,$ny\";\n"
            f"                if (!exists $visited{{$key}}) {{ $visited{{$key}}=1; push @q, [$nx,$ny,$d+1]; }}\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return -1;\n}}\n")


def _c_knight(wrong):
    a = " + 1" if wrong else ""
    return (f"typedef struct {{ int x,y,d; }} KState;\n"
            f"int min_knight_moves(int x, int y) {{\n"
            f"    if (x<0) x=-x; if (y<0) y=-y;\n"
            f"    int mvx[8]={{1,2,-1,-2,1,2,-1,-2}}; int mvy[8]={{2,1,2,1,-2,-1,-2,-1}};\n"
            f"    int W = x+5, H = y+5; int OX=2, OY=2;\n"
            f"    int* visited = (int*)calloc(W*H, sizeof(int));\n"
            f"    KState* q = (KState*)malloc(sizeof(KState)*W*H); int qh=0, qt=0;\n"
            f"    q[qt].x=0; q[qt].y=0; q[qt].d=0; qt++;\n"
            f"    visited[(0+OX)*H+(0+OY)]=1;\n"
            f"    int result=-1;\n"
            f"    while (qh<qt) {{\n"
            f"        KState cur = q[qh]; qh++;\n"
            f"        if (cur.x==x && cur.y==y) {{ result=cur.d; break; }}\n"
            f"        for (int k=0;k<8;k++) {{\n"
            f"            int nx=cur.x+mvx[k], ny=cur.y+mvy[k];\n"
            f"            if (nx>=-2 && ny>=-2 && nx<=x+2 && ny<=y+2) {{\n"
            f"                int ix=nx+OX, iy=ny+OY;\n"
            f"                if (ix>=0 && ix<W && iy>=0 && iy<H && !visited[ix*H+iy]) {{\n"
            f"                    visited[ix*H+iy]=1; q[qt].x=nx; q[qt].y=ny; q[qt].d=cur.d+1; qt++;\n"
            f"                }}\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    free(visited); free(q);\n"
            f"    return result{a};\n}}\n")


def _rust_knight(wrong):
    a = " + 1" if wrong else ""
    return (f"use std::collections::{{HashSet,VecDeque}};\n"
            f"fn min_knight_moves(x: i32, y: i32) -> i32 {{\n"
            f"    let x = x.abs(); let y = y.abs();\n"
            f"    let moves: [(i32,i32);8] = [(1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)];\n"
            f"    let mut visited: HashSet<(i32,i32)> = HashSet::new(); visited.insert((0,0));\n"
            f"    let mut q: VecDeque<(i32,i32,i32)> = VecDeque::new(); q.push_back((0,0,0));\n"
            f"    while let Some((cx,cy,d)) = q.pop_front() {{\n"
            f"        if cx==x && cy==y {{ return d{a}; }}\n"
            f"        for (dx,dy) in moves.iter() {{\n"
            f"            let nx=cx+dx; let ny=cy+dy;\n"
            f"            if nx>=-2 && ny>=-2 && nx<=x+2 && ny<=y+2 {{\n"
            f"                if !visited.contains(&(nx,ny)) {{ visited.insert((nx,ny)); q.push_back((nx,ny,d+1)); }}\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    -1\n}}\n")


# ── number-of-divisors (trial division sqrt(n)) ─────────────────────────────
def _js_numdiv(wrong):
    a = " + 1" if wrong else ""
    return (f"function number_of_divisors(n) {{\n"
            f"    let count=0;\n"
            f"    for (let i=1;i*i<=n;i++) {{ if (n%i===0) {{ count+=2; if (i*i===n) count--; }} }}\n"
            f"    return count{a};\n}}\n")


def _ts_numdiv(wrong):
    a = " + 1" if wrong else ""
    return (f"function number_of_divisors(n: number): number {{\n"
            f"    let count=0;\n"
            f"    for (let i=1;i*i<=n;i++) {{ if (n%i===0) {{ count+=2; if (i*i===n) count--; }} }}\n"
            f"    return count{a};\n}}\n")


def _java_numdiv(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int number_of_divisors(int n) {{\n"
            f"    int count=0;\n"
            f"    for (long i=1;i*i<=n;i++) {{ if (n%i==0) {{ count+=2; if (i*i==n) count--; }} }}\n"
            f"    return count{a};\n}} }}\n")


def _cpp_numdiv(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int number_of_divisors(int n) {{\n"
            f"    int count=0;\n"
            f"    for (long long i=1;i*i<=n;i++) {{ if (n%i==0) {{ count+=2; if (i*i==n) count--; }} }}\n"
            f"    return count{a};\n}} }};\n")


def _csharp_numdiv(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int number_of_divisors(int n) {{\n"
            f"    int count=0;\n"
            f"    for (long i=1;i*i<=n;i++) {{ if (n%i==0) {{ count+=2; if (i*i==n) count--; }} }}\n"
            f"    return count{a};\n}} }}\n")


def _perl_numdiv(wrong):
    a = " + 1" if wrong else ""
    return (f"sub number_of_divisors {{\n"
            f"    my ($n) = @_;\n"
            f"    my $count=0;\n"
            f"    for (my $i=1;$i*$i<=$n;$i++) {{ if ($n%$i==0) {{ $count+=2; $count-- if $i*$i==$n; }} }}\n"
            f"    return $count{a};\n}}\n")


def _c_numdiv(wrong):
    a = " + 1" if wrong else ""
    return (f"int number_of_divisors(int n) {{\n"
            f"    int count=0;\n"
            f"    for (long long i=1;i*i<=n;i++) {{ if (n%i==0) {{ count+=2; if (i*i==n) count--; }} }}\n"
            f"    return count{a};\n}}\n")


def _rust_numdiv(wrong):
    a = " + 1" if wrong else ""
    return (f"fn number_of_divisors(n: i32) -> i32 {{\n"
            f"    let mut count=0i32; let mut i: i64=1;\n"
            f"    while i*i<=n as i64 {{ if (n as i64)%i==0 {{ count+=2; if i*i==n as i64 {{ count-=1; }} }} i+=1; }}\n"
            f"    count{a}\n}}\n")


# ── palindrome-linked-list (two-pointer boolean) ────────────────────────────
def _js_palindlist(wrong):
    ret = "false" if wrong else "true"
    return (f"function is_palindrome(values) {{\n"
            f"    let lo=0, hi=values.length-1;\n"
            f"    while (lo<hi) {{ if (values[lo]!==values[hi]) return false; lo++; hi--; }}\n"
            f"    return {ret};\n}}\n")


def _ts_palindlist(wrong):
    ret = "false" if wrong else "true"
    return (f"function is_palindrome(values: number[]): boolean {{\n"
            f"    let lo=0, hi=values.length-1;\n"
            f"    while (lo<hi) {{ if (values[lo]!==values[hi]) return false; lo++; hi--; }}\n"
            f"    return {ret};\n}}\n")


def _java_palindlist(wrong):
    ret = "false" if wrong else "true"
    return (f"class Solution {{ public boolean is_palindrome(int[] values) {{\n"
            f"    int lo=0, hi=values.length-1;\n"
            f"    while (lo<hi) {{ if (values[lo]!=values[hi]) return false; lo++; hi--; }}\n"
            f"    return {ret};\n}} }}\n")


def _cpp_palindlist(wrong):
    ret = "false" if wrong else "true"
    return (f"class Solution {{ public: bool is_palindrome(std::vector<int> values) {{\n"
            f"    int lo=0, hi=(int)values.size()-1;\n"
            f"    while (lo<hi) {{ if (values[lo]!=values[hi]) return false; lo++; hi--; }}\n"
            f"    return {ret};\n}} }};\n")


def _csharp_palindlist(wrong):
    ret = "false" if wrong else "true"
    return (f"class Solution {{ public static bool is_palindrome(int[] values) {{\n"
            f"    int lo=0, hi=values.Length-1;\n"
            f"    while (lo<hi) {{ if (values[lo]!=values[hi]) return false; lo++; hi--; }}\n"
            f"    return {ret};\n}} }}\n")


def _perl_palindlist(wrong):
    ret = "0" if wrong else "1"
    return (f"sub is_palindrome {{\n"
            f"    my ($values) = @_;\n"
            f"    my $lo=0; my $hi=scalar(@$values)-1;\n"
            f"    while ($lo<$hi) {{ return 0 if $values->[$lo]!=$values->[$hi]; $lo++; $hi--; }}\n"
            f"    return {ret};\n}}\n")


def _c_palindlist(wrong):
    ret = "0" if wrong else "1"
    return (f"int is_palindrome(AtlasIntArray values) {{\n"
            f"    int lo=0, hi=values.size-1;\n"
            f"    while (lo<hi) {{ if (values.data[lo]!=values.data[hi]) return 0; lo++; hi--; }}\n"
            f"    return {ret};\n}}\n")


def _rust_palindlist(wrong):
    ret = "false" if wrong else "true"
    return (f"fn is_palindrome(values: Vec<i32>) -> bool {{\n"
            f"    let (mut lo, mut hi) = (0i32, values.len() as i32 - 1);\n"
            f"    while lo<hi {{ if values[lo as usize]!=values[hi as usize] {{ return false; }} lo+=1; hi-=1; }}\n"
            f"    {ret}\n}}\n")


# ── perfect-squares-min-count (DP, n up to 9999) ────────────────────────────
def _js_perfsq(wrong):
    a = " + 1" if wrong else ""
    return (f"function num_squares(n) {{\n"
            f"    const dp=new Array(n+1).fill(Infinity); dp[0]=0;\n"
            f"    for (let i=1;i<=n;i++) for (let j=1;j*j<=i;j++) dp[i]=Math.min(dp[i], dp[i-j*j]+1);\n"
            f"    return dp[n]{a};\n}}\n")


def _ts_perfsq(wrong):
    a = " + 1" if wrong else ""
    return (f"function num_squares(n: number): number {{\n"
            f"    const dp: number[]=new Array(n+1).fill(Infinity); dp[0]=0;\n"
            f"    for (let i=1;i<=n;i++) for (let j=1;j*j<=i;j++) dp[i]=Math.min(dp[i], dp[i-j*j]+1);\n"
            f"    return dp[n]{a};\n}}\n")


def _java_perfsq(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int num_squares(int n) {{\n"
            f"    int[] dp = new int[n+1]; java.util.Arrays.fill(dp, Integer.MAX_VALUE/2); dp[0]=0;\n"
            f"    for (int i=1;i<=n;i++) for (int j=1;j*j<=i;j++) dp[i]=Math.min(dp[i], dp[i-j*j]+1);\n"
            f"    return dp[n]{a};\n}} }}\n")


def _cpp_perfsq(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int num_squares(int n) {{\n"
            f"    std::vector<int> dp(n+1, 1000000000); dp[0]=0;\n"
            f"    for (int i=1;i<=n;i++) for (int j=1;j*j<=i;j++) dp[i]=std::min(dp[i], dp[i-j*j]+1);\n"
            f"    return dp[n]{a};\n}} }};\n")


def _csharp_perfsq(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int num_squares(int n) {{\n"
            f"    int[] dp = new int[n+1]; for (int i=0;i<=n;i++) dp[i]=1000000000; dp[0]=0;\n"
            f"    for (int i=1;i<=n;i++) for (int j=1;j*j<=i;j++) dp[i]=System.Math.Min(dp[i], dp[i-j*j]+1);\n"
            f"    return dp[n]{a};\n}} }}\n")


def _perl_perfsq(wrong):
    a = " + 1" if wrong else ""
    return (f"sub num_squares {{\n"
            f"    my ($n) = @_;\n"
            f"    my @dp = (1000000000) x ($n+1); $dp[0]=0;\n"
            f"    for (my $i=1;$i<=$n;$i++) {{ for (my $j=1;$j*$j<=$i;$j++) {{ my $v=$dp[$i-$j*$j]+1; $dp[$i]=$v if $v<$dp[$i]; }} }}\n"
            f"    return $dp[$n]{a};\n}}\n")


def _c_perfsq(wrong):
    a = " + 1" if wrong else ""
    return (f"int num_squares(int n) {{\n"
            f"    int* dp = (int*)malloc(sizeof(int)*(n+1));\n"
            f"    for (int i=0;i<=n;i++) dp[i]=1000000000; dp[0]=0;\n"
            f"    for (int i=1;i<=n;i++) for (int j=1;j*j<=i;j++) if (dp[i-j*j]+1<dp[i]) dp[i]=dp[i-j*j]+1;\n"
            f"    int r=dp[n]; free(dp);\n"
            f"    return r{a};\n}}\n")


def _rust_perfsq(wrong):
    a = " + 1" if wrong else ""
    return (f"fn num_squares(n: i32) -> i32 {{\n"
            f"    let nn = n as usize; let mut dp = vec![1_000_000_000i32; nn+1]; dp[0]=0;\n"
            f"    for i in 1..=nn {{ let mut j=1usize; while j*j<=i {{ if dp[i-j*j]+1<dp[i] {{ dp[i]=dp[i-j*j]+1; }} j+=1; }} }}\n"
            f"    dp[nn]{a}\n}}\n")


# ── reverse-linked-list (reverse array) ─────────────────────────────────────
def _js_revlist(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return f"function reverse_list(values) {{\n    return values.slice().reverse(){a};\n}}\n"


def _ts_revlist(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return f"function reverse_list(values: number[]): number[] {{\n    return values.slice().reverse(){a};\n}}\n"


def _java_revlist(wrong):
    incr = "for (int i=0;i<out.length;i++) out[i]++;\n        " if wrong else ""
    return (f"class Solution {{ public int[] reverse_list(int[] values) {{\n"
            f"    int n=values.length; int[] out=new int[n];\n"
            f"    for (int i=0;i<n;i++) out[i]=values[n-1-i];\n"
            f"        {incr}return out;\n}} }}\n")


def _cpp_revlist(wrong):
    incr = "for (auto& x: out) x++;\n    " if wrong else ""
    return (f"class Solution {{ public: std::vector<int> reverse_list(std::vector<int> values) {{\n"
            f"    std::vector<int> out(values.rbegin(), values.rend());\n"
            f"    {incr}return out;\n}} }};\n")


def _csharp_revlist(wrong):
    incr = "for (int i=0;i<outArr.Length;i++) outArr[i]++;\n        " if wrong else ""
    return (f"class Solution {{ public static int[] reverse_list(int[] values) {{\n"
            f"    int n=values.Length; int[] outArr=new int[n];\n"
            f"    for (int i=0;i<n;i++) outArr[i]=values[n-1-i];\n"
            f"        {incr}return outArr;\n}} }}\n")


def _perl_revlist(wrong):
    incr = "@out = map { $_ + 1 } @out;\n    " if wrong else ""
    return (f"sub reverse_list {{\n"
            f"    my ($values) = @_;\n"
            f"    my @out = reverse @$values;\n"
            f"    {incr}return \\@out;\n}}\n")


def _c_revlist(wrong):
    incr = "for (int i=0;i<n;i++) out[i]++;\n    " if wrong else ""
    return (f"AtlasIntArray reverse_list(AtlasIntArray values) {{\n"
            f"    int n=values.size; int* out=(int*)malloc(sizeof(int)*(n>0?n:1));\n"
            f"    for (int i=0;i<n;i++) out[i]=values.data[n-1-i];\n"
            f"    {incr}AtlasIntArray result; result.size=n; result.data=out;\n"
            f"    return result;\n}}\n")


def _rust_revlist(wrong):
    incr = "for x in out.iter_mut() { *x += 1; }\n    " if wrong else ""
    return (f"fn reverse_list(values: Vec<i32>) -> Vec<i32> {{\n"
            f"    let mut out: Vec<i32> = values.into_iter().rev().collect();\n"
            f"    {incr}out\n}}\n")


# ── rod-cutting (unbounded knapsack, O(n^2)) ────────────────────────────────
def _js_rodcut(wrong):
    a = " + 1" if wrong else ""
    return (f"function rod_cutting(prices, n) {{\n"
            f"    const dp = new Array(n+1).fill(0);\n"
            f"    for (let i=1;i<=n;i++) for (let len=1;len<=Math.min(i,prices.length);len++) dp[i]=Math.max(dp[i], dp[i-len]+prices[len-1]);\n"
            f"    return dp[n]{a};\n}}\n")


def _ts_rodcut(wrong):
    a = " + 1" if wrong else ""
    return (f"function rod_cutting(prices: number[], n: number): number {{\n"
            f"    const dp: number[] = new Array(n+1).fill(0);\n"
            f"    for (let i=1;i<=n;i++) for (let len=1;len<=Math.min(i,prices.length);len++) dp[i]=Math.max(dp[i], dp[i-len]+prices[len-1]);\n"
            f"    return dp[n]{a};\n}}\n")


def _java_rodcut(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int rod_cutting(int[] prices, int n) {{\n"
            f"    int[] dp = new int[n+1];\n"
            f"    for (int i=1;i<=n;i++) for (int len=1;len<=Math.min(i,prices.length);len++) dp[i]=Math.max(dp[i], dp[i-len]+prices[len-1]);\n"
            f"    return dp[n]{a};\n}} }}\n")


def _cpp_rodcut(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int rod_cutting(std::vector<int> prices, int n) {{\n"
            f"    std::vector<int> dp(n+1, 0);\n"
            f"    for (int i=1;i<=n;i++) for (int len=1;len<=std::min(i,(int)prices.size());len++) dp[i]=std::max(dp[i], dp[i-len]+prices[len-1]);\n"
            f"    return dp[n]{a};\n}} }};\n")


def _csharp_rodcut(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int rod_cutting(int[] prices, int n) {{\n"
            f"    int[] dp = new int[n+1];\n"
            f"    for (int i=1;i<=n;i++) for (int len=1;len<=System.Math.Min(i,prices.Length);len++) dp[i]=System.Math.Max(dp[i], dp[i-len]+prices[len-1]);\n"
            f"    return dp[n]{a};\n}} }}\n")


def _perl_rodcut(wrong):
    a = " + 1" if wrong else ""
    return (f"sub rod_cutting {{\n"
            f"    my ($prices, $n) = @_;\n"
            f"    my @dp = (0) x ($n+1);\n"
            f"    for (my $i=1;$i<=$n;$i++) {{\n"
            f"        my $maxlen = ($i<scalar(@$prices))?$i:scalar(@$prices);\n"
            f"        for (my $len=1;$len<=$maxlen;$len++) {{ my $v=$dp[$i-$len]+$prices->[$len-1]; $dp[$i]=$v if $v>$dp[$i]; }}\n"
            f"    }}\n"
            f"    return $dp[$n]{a};\n}}\n")


def _c_rodcut(wrong):
    a = " + 1" if wrong else ""
    return (f"int rod_cutting(AtlasIntArray prices, int n) {{\n"
            f"    int* dp = (int*)calloc(n+1, sizeof(int));\n"
            f"    for (int i=1;i<=n;i++) {{\n"
            f"        int maxlen = i<prices.size?i:prices.size;\n"
            f"        for (int len=1;len<=maxlen;len++) {{ int v=dp[i-len]+prices.data[len-1]; if (v>dp[i]) dp[i]=v; }}\n"
            f"    }}\n"
            f"    int r=dp[n]; free(dp);\n"
            f"    return r{a};\n}}\n")


def _rust_rodcut(wrong):
    a = " + 1" if wrong else ""
    return (f"fn rod_cutting(prices: Vec<i32>, n: i32) -> i32 {{\n"
            f"    let nn = n as usize; let mut dp = vec![0i32; nn+1];\n"
            f"    for i in 1..=nn {{\n"
            f"        let maxlen = i.min(prices.len());\n"
            f"        for len in 1..=maxlen {{ let v = dp[i-len]+prices[len-1]; if v>dp[i] {{ dp[i]=v; }} }}\n"
            f"    }}\n"
            f"    dp[nn]{a}\n}}\n")


# ── rotated-binary-search ────────────────────────────────────────────────────
def _js_rotsearch(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (f"function search(nums, target) {{\n"
            f"    let lo=0, hi=nums.length-1;\n"
            f"    while (lo<=hi) {{\n"
            f"        const mid=(lo+hi)>>1;\n"
            f"        if (nums[mid]===target) return {ret};\n"
            f"        if (nums[lo]<=nums[mid]) {{ if (nums[lo]<=target && target<nums[mid]) hi=mid-1; else lo=mid+1; }}\n"
            f"        else {{ if (nums[mid]<target && target<=nums[hi]) lo=mid+1; else hi=mid-1; }}\n"
            f"    }}\n"
            f"    return -1;\n}}\n")


def _ts_rotsearch(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (f"function search(nums: number[], target: number): number {{\n"
            f"    let lo=0, hi=nums.length-1;\n"
            f"    while (lo<=hi) {{\n"
            f"        const mid=(lo+hi)>>1;\n"
            f"        if (nums[mid]===target) return {ret};\n"
            f"        if (nums[lo]<=nums[mid]) {{ if (nums[lo]<=target && target<nums[mid]) hi=mid-1; else lo=mid+1; }}\n"
            f"        else {{ if (nums[mid]<target && target<=nums[hi]) lo=mid+1; else hi=mid-1; }}\n"
            f"    }}\n"
            f"    return -1;\n}}\n")


def _java_rotsearch(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (f"class Solution {{ public int search(int[] nums, int target) {{\n"
            f"    int lo=0, hi=nums.length-1;\n"
            f"    while (lo<=hi) {{\n"
            f"        int mid=(lo+hi)>>>1;\n"
            f"        if (nums[mid]==target) return {ret};\n"
            f"        if (nums[lo]<=nums[mid]) {{ if (nums[lo]<=target && target<nums[mid]) hi=mid-1; else lo=mid+1; }}\n"
            f"        else {{ if (nums[mid]<target && target<=nums[hi]) lo=mid+1; else hi=mid-1; }}\n"
            f"    }}\n"
            f"    return -1;\n}} }}\n")


def _cpp_rotsearch(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (f"class Solution {{ public: int search(std::vector<int> nums, int target) {{\n"
            f"    int lo=0, hi=(int)nums.size()-1;\n"
            f"    while (lo<=hi) {{\n"
            f"        int mid=lo+(hi-lo)/2;\n"
            f"        if (nums[mid]==target) return {ret};\n"
            f"        if (nums[lo]<=nums[mid]) {{ if (nums[lo]<=target && target<nums[mid]) hi=mid-1; else lo=mid+1; }}\n"
            f"        else {{ if (nums[mid]<target && target<=nums[hi]) lo=mid+1; else hi=mid-1; }}\n"
            f"    }}\n"
            f"    return -1;\n}} }};\n")


def _csharp_rotsearch(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (f"class Solution {{ public static int search(int[] nums, int target) {{\n"
            f"    int lo=0, hi=nums.Length-1;\n"
            f"    while (lo<=hi) {{\n"
            f"        int mid=lo+(hi-lo)/2;\n"
            f"        if (nums[mid]==target) return {ret};\n"
            f"        if (nums[lo]<=nums[mid]) {{ if (nums[lo]<=target && target<nums[mid]) hi=mid-1; else lo=mid+1; }}\n"
            f"        else {{ if (nums[mid]<target && target<=nums[hi]) lo=mid+1; else hi=mid-1; }}\n"
            f"    }}\n"
            f"    return -1;\n}} }}\n")


def _perl_rotsearch(wrong):
    ret = "$mid + 1" if wrong else "$mid"
    return (f"sub search {{\n"
            f"    my ($nums, $target) = @_;\n"
            f"    my $lo=0; my $hi=scalar(@$nums)-1;\n"
            f"    while ($lo<=$hi) {{\n"
            f"        my $mid=int(($lo+$hi)/2);\n"
            f"        return {ret} if $nums->[$mid]==$target;\n"
            f"        if ($nums->[$lo]<=$nums->[$mid]) {{\n"
            f"            if ($nums->[$lo]<=$target && $target<$nums->[$mid]) {{ $hi=$mid-1; }} else {{ $lo=$mid+1; }}\n"
            f"        }} else {{\n"
            f"            if ($nums->[$mid]<$target && $target<=$nums->[$hi]) {{ $lo=$mid+1; }} else {{ $hi=$mid-1; }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return -1;\n}}\n")


def _c_rotsearch(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (f"int search(AtlasIntArray nums, int target) {{\n"
            f"    int lo=0, hi=nums.size-1;\n"
            f"    while (lo<=hi) {{\n"
            f"        int mid=lo+(hi-lo)/2;\n"
            f"        if (nums.data[mid]==target) return {ret};\n"
            f"        if (nums.data[lo]<=nums.data[mid]) {{ if (nums.data[lo]<=target && target<nums.data[mid]) hi=mid-1; else lo=mid+1; }}\n"
            f"        else {{ if (nums.data[mid]<target && target<=nums.data[hi]) lo=mid+1; else hi=mid-1; }}\n"
            f"    }}\n"
            f"    return -1;\n}}\n")


def _rust_rotsearch(wrong):
    ret = "mid as i32 + 1" if wrong else "mid as i32"
    return (f"fn search(nums: Vec<i32>, target: i32) -> i32 {{\n"
            f"    if nums.is_empty() {{ return -1; }}\n"
            f"    let (mut lo, mut hi): (i32,i32) = (0, nums.len() as i32 -1);\n"
            f"    while lo<=hi {{\n"
            f"        let mid=lo+(hi-lo)/2;\n"
            f"        if nums[mid as usize]==target {{ return {ret}; }}\n"
            f"        if nums[lo as usize]<=nums[mid as usize] {{\n"
            f"            if nums[lo as usize]<=target && target<nums[mid as usize] {{ hi=mid-1; }} else {{ lo=mid+1; }}\n"
            f"        }} else {{\n"
            f"            if nums[mid as usize]<target && target<=nums[hi as usize] {{ lo=mid+1; }} else {{ hi=mid-1; }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    -1\n}}\n")


# ── search-insert-position (lower_bound) ─────────────────────────────────────
def _js_searchinsert(wrong):
    a = " + 1" if wrong else ""
    return (f"function search_insert(nums, target) {{\n"
            f"    let lo=0, hi=nums.length;\n"
            f"    while (lo<hi) {{ const mid=(lo+hi)>>1; if (nums[mid]<target) lo=mid+1; else hi=mid; }}\n"
            f"    return lo{a};\n}}\n")


def _ts_searchinsert(wrong):
    a = " + 1" if wrong else ""
    return (f"function search_insert(nums: number[], target: number): number {{\n"
            f"    let lo=0, hi=nums.length;\n"
            f"    while (lo<hi) {{ const mid=(lo+hi)>>1; if (nums[mid]<target) lo=mid+1; else hi=mid; }}\n"
            f"    return lo{a};\n}}\n")


def _java_searchinsert(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int search_insert(int[] nums, int target) {{\n"
            f"    int lo=0, hi=nums.length;\n"
            f"    while (lo<hi) {{ int mid=(lo+hi)>>>1; if (nums[mid]<target) lo=mid+1; else hi=mid; }}\n"
            f"    return lo{a};\n}} }}\n")


def _cpp_searchinsert(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int search_insert(std::vector<int> nums, int target) {{\n"
            f"    int lo=0, hi=(int)nums.size();\n"
            f"    while (lo<hi) {{ int mid=lo+(hi-lo)/2; if (nums[mid]<target) lo=mid+1; else hi=mid; }}\n"
            f"    return lo{a};\n}} }};\n")


def _csharp_searchinsert(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int search_insert(int[] nums, int target) {{\n"
            f"    int lo=0, hi=nums.Length;\n"
            f"    while (lo<hi) {{ int mid=lo+(hi-lo)/2; if (nums[mid]<target) lo=mid+1; else hi=mid; }}\n"
            f"    return lo{a};\n}} }}\n")


def _perl_searchinsert(wrong):
    a = " + 1" if wrong else ""
    return (f"sub search_insert {{\n"
            f"    my ($nums, $target) = @_;\n"
            f"    my $lo=0; my $hi=scalar(@$nums);\n"
            f"    while ($lo<$hi) {{ my $mid=int(($lo+$hi)/2); if ($nums->[$mid]<$target) {{ $lo=$mid+1; }} else {{ $hi=$mid; }} }}\n"
            f"    return $lo{a};\n}}\n")


def _c_searchinsert(wrong):
    a = " + 1" if wrong else ""
    return (f"int search_insert(AtlasIntArray nums, int target) {{\n"
            f"    int lo=0, hi=nums.size;\n"
            f"    while (lo<hi) {{ int mid=lo+(hi-lo)/2; if (nums.data[mid]<target) lo=mid+1; else hi=mid; }}\n"
            f"    return lo{a};\n}}\n")


def _rust_searchinsert(wrong):
    ret = "lo as i32 + 1" if wrong else "lo as i32"
    return (f"fn search_insert(nums: Vec<i32>, target: i32) -> i32 {{\n"
            f"    let mut lo=0usize; let mut hi=nums.len();\n"
            f"    while lo<hi {{ let mid=lo+(hi-lo)/2; if nums[mid]<target {{ lo=mid+1; }} else {{ hi=mid; }} }}\n"
            f"    {ret}\n}}\n")


# ── staircase (climb stairs, DP fib-like) ────────────────────────────────────
def _js_staircase(wrong):
    a = " + 1" if wrong else ""
    return (f"function climb_stairs(n) {{\n"
            f"    if (n===0) return 1{a};\n"
            f"    if (n<=2) return n{a};\n"
            f"    let a1=1, b=2;\n"
            f"    for (let i=3;i<=n;i++) {{ const t=a1+b; a1=b; b=t; }}\n"
            f"    return b{a};\n}}\n")


def _ts_staircase(wrong):
    a = " + 1" if wrong else ""
    return (f"function climb_stairs(n: number): number {{\n"
            f"    if (n===0) return 1{a};\n"
            f"    if (n<=2) return n{a};\n"
            f"    let a1=1, b=2;\n"
            f"    for (let i=3;i<=n;i++) {{ const t=a1+b; a1=b; b=t; }}\n"
            f"    return b{a};\n}}\n")


def _java_staircase(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int climb_stairs(int n) {{\n"
            f"    if (n==0) return 1{a};\n"
            f"    if (n<=2) return n{a};\n"
            f"    long a1=1, b=2;\n"
            f"    for (int i=3;i<=n;i++) {{ long t=a1+b; a1=b; b=t; }}\n"
            f"    return (int)(b{a});\n}} }}\n")


def _cpp_staircase(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int climb_stairs(int n) {{\n"
            f"    if (n==0) return 1{a};\n"
            f"    if (n<=2) return n{a};\n"
            f"    long long a1=1, b=2;\n"
            f"    for (int i=3;i<=n;i++) {{ long long t=a1+b; a1=b; b=t; }}\n"
            f"    return (int)(b{a});\n}} }};\n")


def _csharp_staircase(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int climb_stairs(int n) {{\n"
            f"    if (n==0) return 1{a};\n"
            f"    if (n<=2) return n{a};\n"
            f"    long a1=1, b=2;\n"
            f"    for (int i=3;i<=n;i++) {{ long t=a1+b; a1=b; b=t; }}\n"
            f"    return (int)(b{a});\n}} }}\n")


def _perl_staircase(wrong):
    a = " + 1" if wrong else ""
    return (f"sub climb_stairs {{\n"
            f"    my ($n) = @_;\n"
            f"    return (1{a}) if $n==0;\n"
            f"    return $n{a} if $n<=2;\n"
            f"    my $a1=1; my $b=2;\n"
            f"    for (my $i=3;$i<=$n;$i++) {{ my $t=$a1+$b; $a1=$b; $b=$t; }}\n"
            f"    return $b{a};\n}}\n")


def _c_staircase(wrong):
    a = " + 1" if wrong else ""
    return (f"int climb_stairs(int n) {{\n"
            f"    if (n==0) return 1{a};\n"
            f"    if (n<=2) return n{a};\n"
            f"    long long a1=1, b=2;\n"
            f"    for (int i=3;i<=n;i++) {{ long long t=a1+b; a1=b; b=t; }}\n"
            f"    return (int)(b{a});\n}}\n")


def _rust_staircase(wrong):
    a = " + 1" if wrong else ""
    return (f"fn climb_stairs(n: i32) -> i32 {{\n"
            f"    if n==0 {{ return 1{a}; }}\n"
            f"    if n<=2 {{ return n{a}; }}\n"
            f"    let mut a1: i64=1; let mut b: i64=2;\n"
            f"    for _ in 3..=n {{ let t=a1+b; a1=b; b=t; }}\n"
            f"    (b{a}) as i32\n}}\n")


# ── subarray-product-less-than-k (sliding window count) ─────────────────────
def _js_subprod(wrong):
    a = " + 1" if wrong else ""
    return (f"function num_subarrays_product_less_than_k(nums, k) {{\n"
            f"    if (k<=1) return 0{a};\n"
            f"    let prod=1, left=0, count=0;\n"
            f"    for (let right=0;right<nums.length;right++) {{\n"
            f"        prod*=nums[right];\n"
            f"        while (prod>=k) {{ prod/=nums[left]; left++; }}\n"
            f"        count += right-left+1;\n"
            f"    }}\n"
            f"    return count{a};\n}}\n")


def _ts_subprod(wrong):
    a = " + 1" if wrong else ""
    return (f"function num_subarrays_product_less_than_k(nums: number[], k: number): number {{\n"
            f"    if (k<=1) return 0{a};\n"
            f"    let prod=1, left=0, count=0;\n"
            f"    for (let right=0;right<nums.length;right++) {{\n"
            f"        prod*=nums[right];\n"
            f"        while (prod>=k) {{ prod/=nums[left]; left++; }}\n"
            f"        count += right-left+1;\n"
            f"    }}\n"
            f"    return count{a};\n}}\n")


def _java_subprod(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int num_subarrays_product_less_than_k(int[] nums, int k) {{\n"
            f"    if (k<=1) return 0{a};\n"
            f"    long prod=1; int left=0; long count=0;\n"
            f"    for (int right=0;right<nums.length;right++) {{\n"
            f"        prod*=nums[right];\n"
            f"        while (prod>=k) {{ prod/=nums[left]; left++; }}\n"
            f"        count += right-left+1;\n"
            f"    }}\n"
            f"    return (int)(count{a});\n}} }}\n")


def _cpp_subprod(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int num_subarrays_product_less_than_k(std::vector<int> nums, int k) {{\n"
            f"    if (k<=1) return 0{a};\n"
            f"    long long prod=1; int left=0; long long count=0;\n"
            f"    for (int right=0;right<(int)nums.size();right++) {{\n"
            f"        prod*=nums[right];\n"
            f"        while (prod>=k) {{ prod/=nums[left]; left++; }}\n"
            f"        count += right-left+1;\n"
            f"    }}\n"
            f"    return (int)(count{a});\n}} }};\n")


def _csharp_subprod(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int num_subarrays_product_less_than_k(int[] nums, int k) {{\n"
            f"    if (k<=1) return 0{a};\n"
            f"    long prod=1; int left=0; long count=0;\n"
            f"    for (int right=0;right<nums.Length;right++) {{\n"
            f"        prod*=nums[right];\n"
            f"        while (prod>=k) {{ prod/=nums[left]; left++; }}\n"
            f"        count += right-left+1;\n"
            f"    }}\n"
            f"    return (int)(count{a});\n}} }}\n")


def _perl_subprod(wrong):
    a = " + 1" if wrong else ""
    return (f"sub num_subarrays_product_less_than_k {{\n"
            f"    my ($nums, $k) = @_;\n"
            f"    return (0{a}) if $k<=1;\n"
            f"    my $prod=1; my $left=0; my $count=0;\n"
            f"    for (my $right=0;$right<scalar(@$nums);$right++) {{\n"
            f"        $prod*=$nums->[$right];\n"
            f"        while ($prod>=$k) {{ $prod=int($prod/$nums->[$left]); $left++; }}\n"
            f"        $count += $right-$left+1;\n"
            f"    }}\n"
            f"    return $count{a};\n}}\n")


def _c_subprod(wrong):
    a = " + 1" if wrong else ""
    return (f"int num_subarrays_product_less_than_k(AtlasIntArray nums, int k) {{\n"
            f"    if (k<=1) return 0{a};\n"
            f"    long long prod=1; int left=0; long long count=0;\n"
            f"    for (int right=0;right<nums.size;right++) {{\n"
            f"        prod*=nums.data[right];\n"
            f"        while (prod>=k) {{ prod/=nums.data[left]; left++; }}\n"
            f"        count += right-left+1;\n"
            f"    }}\n"
            f"    return (int)(count{a});\n}}\n")


def _rust_subprod(wrong):
    a = " + 1" if wrong else ""
    return (f"fn num_subarrays_product_less_than_k(nums: Vec<i32>, k: i32) -> i32 {{\n"
            f"    if k<=1 {{ return 0{a}; }}\n"
            f"    let mut prod: i64=1; let mut left=0i32; let mut count: i64=0;\n"
            f"    for right in 0..nums.len() as i32 {{\n"
            f"        prod *= nums[right as usize] as i64;\n"
            f"        while prod>=k as i64 {{ prod /= nums[left as usize] as i64; left+=1; }}\n"
            f"        count += (right-left+1) as i64;\n"
            f"    }}\n"
            f"    (count{a}) as i32\n}}\n")


# ── subarray-sums-divisible-by-k (prefix mod count) ─────────────────────────
def _js_subdivk(wrong):
    a = " + 1" if wrong else ""
    return (f"function subarrays_div_by_k(nums, k) {{\n"
            f"    const seen = new Array(k).fill(0); seen[0]=1;\n"
            f"    let sum=0, count=0;\n"
            f"    for (const x of nums) {{ sum += x; let mod=((sum%k)+k)%k; count += seen[mod]; seen[mod]++; }}\n"
            f"    return count{a};\n}}\n")


def _ts_subdivk(wrong):
    a = " + 1" if wrong else ""
    return (f"function subarrays_div_by_k(nums: number[], k: number): number {{\n"
            f"    const seen: number[] = new Array(k).fill(0); seen[0]=1;\n"
            f"    let sum=0, count=0;\n"
            f"    for (const x of nums) {{ sum += x; let mod=((sum%k)+k)%k; count += seen[mod]; seen[mod]++; }}\n"
            f"    return count{a};\n}}\n")


def _java_subdivk(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int subarrays_div_by_k(int[] nums, int k) {{\n"
            f"    long[] seen = new long[k]; seen[0]=1;\n"
            f"    long sum=0, count=0;\n"
            f"    for (int x: nums) {{ sum += x; int mod=(int)(((sum%k)+k)%k); count += seen[mod]; seen[mod]++; }}\n"
            f"    return (int)(count{a});\n}} }}\n")


def _cpp_subdivk(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int subarrays_div_by_k(std::vector<int> nums, int k) {{\n"
            f"    std::vector<long long> seen(k, 0); seen[0]=1;\n"
            f"    long long sum=0, count=0;\n"
            f"    for (int x: nums) {{ sum += x; int mod=(int)(((sum%k)+k)%k); count += seen[mod]; seen[mod]++; }}\n"
            f"    return (int)(count{a});\n}} }};\n")


def _csharp_subdivk(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int subarrays_div_by_k(int[] nums, int k) {{\n"
            f"    long[] seen = new long[k]; seen[0]=1;\n"
            f"    long sum=0, count=0;\n"
            f"    foreach (int x in nums) {{ sum += x; int mod=(int)(((sum%k)+k)%k); count += seen[mod]; seen[mod]++; }}\n"
            f"    return (int)(count{a});\n}} }}\n")


def _perl_subdivk(wrong):
    a = " + 1" if wrong else ""
    return (f"sub subarrays_div_by_k {{\n"
            f"    my ($nums, $k) = @_;\n"
            f"    my @seen = (0) x $k; $seen[0]=1;\n"
            f"    my $sum=0; my $count=0;\n"
            f"    foreach my $x (@$nums) {{ $sum += $x; my $mod=(($sum%$k)+$k)%$k; $count += $seen[$mod]; $seen[$mod]++; }}\n"
            f"    return $count{a};\n}}\n")


def _c_subdivk(wrong):
    a = " + 1" if wrong else ""
    return (f"int subarrays_div_by_k(AtlasIntArray nums, int k) {{\n"
            f"    long long* seen = (long long*)calloc(k, sizeof(long long)); seen[0]=1;\n"
            f"    long long sum=0, count=0;\n"
            f"    for (int i=0;i<nums.size;i++) {{\n"
            f"        sum += nums.data[i]; int mod=(int)(((sum%k)+k)%k); count += seen[mod]; seen[mod]++;\n"
            f"    }}\n"
            f"    free(seen);\n"
            f"    return (int)(count{a});\n}}\n")


def _rust_subdivk(wrong):
    a = " + 1" if wrong else ""
    return (f"fn subarrays_div_by_k(nums: Vec<i32>, k: i32) -> i32 {{\n"
            f"    let mut seen = vec![0i64; k as usize]; seen[0]=1;\n"
            f"    let mut sum: i64=0; let mut count: i64=0;\n"
            f"    for x in nums.iter() {{\n"
            f"        sum += *x as i64; let m = (((sum%k as i64)+k as i64)%k as i64) as usize;\n"
            f"        count += seen[m]; seen[m]+=1;\n"
            f"    }}\n"
            f"    (count{a}) as i32\n}}\n")


# ── subset-sum (DP boolean, small n<=20 target<=5000) ───────────────────────
def _js_subsetsum(wrong):
    ret = "false" if wrong else "true"
    return (f"function subset_sum(nums, target) {{\n"
            f"    const dp = new Array(target+1).fill(false); dp[0]=true;\n"
            f"    for (const x of nums) for (let i=target;i>=x;i--) if (dp[i-x]) dp[i]=true;\n"
            f"    return dp[target]?{ret}:false;\n}}\n")


def _ts_subsetsum(wrong):
    ret = "false" if wrong else "true"
    return (f"function subset_sum(nums: number[], target: number): boolean {{\n"
            f"    const dp: boolean[] = new Array(target+1).fill(false); dp[0]=true;\n"
            f"    for (const x of nums) for (let i=target;i>=x;i--) if (dp[i-x]) dp[i]=true;\n"
            f"    return dp[target]?{ret}:false;\n}}\n")


def _java_subsetsum(wrong):
    ret = "false" if wrong else "true"
    return (f"class Solution {{ public boolean subset_sum(int[] nums, int target) {{\n"
            f"    boolean[] dp = new boolean[target+1]; dp[0]=true;\n"
            f"    for (int x: nums) for (int i=target;i>=x;i--) if (dp[i-x]) dp[i]=true;\n"
            f"    return dp[target]?{ret}:false;\n}} }}\n")


def _cpp_subsetsum(wrong):
    ret = "false" if wrong else "true"
    return (f"class Solution {{ public: bool subset_sum(std::vector<int> nums, int target) {{\n"
            f"    std::vector<bool> dp(target+1, false); dp[0]=true;\n"
            f"    for (int x: nums) for (int i=target;i>=x;i--) if (dp[i-x]) dp[i]=true;\n"
            f"    return dp[target]?{ret}:false;\n}} }};\n")


def _csharp_subsetsum(wrong):
    ret = "false" if wrong else "true"
    return (f"class Solution {{ public static bool subset_sum(int[] nums, int target) {{\n"
            f"    bool[] dp = new bool[target+1]; dp[0]=true;\n"
            f"    foreach (int x in nums) for (int i=target;i>=x;i--) if (dp[i-x]) dp[i]=true;\n"
            f"    return dp[target]?{ret}:false;\n}} }}\n")


def _perl_subsetsum(wrong):
    ret = "0" if wrong else "1"
    return (f"sub subset_sum {{\n"
            f"    my ($nums, $target) = @_;\n"
            f"    my @dp = (0) x ($target+1); $dp[0]=1;\n"
            f"    foreach my $x (@$nums) {{ for (my $i=$target;$i>=$x;$i--) {{ $dp[$i]=1 if $dp[$i-$x]; }} }}\n"
            f"    return $dp[$target] ? {ret} : 0;\n}}\n")


def _c_subsetsum(wrong):
    ret = "0" if wrong else "1"
    return (f"int subset_sum(AtlasIntArray nums, int target) {{\n"
            f"    int* dp = (int*)calloc(target+1, sizeof(int)); dp[0]=1;\n"
            f"    for (int k=0;k<nums.size;k++) {{ int x=nums.data[k]; for (int i=target;i>=x;i--) if (dp[i-x]) dp[i]=1; }}\n"
            f"    int r = dp[target] ? {ret} : 0;\n"
            f"    free(dp);\n"
            f"    return r;\n}}\n")


def _rust_subsetsum(wrong):
    ret = "false" if wrong else "true"
    return (f"fn subset_sum(nums: Vec<i32>, target: i32) -> bool {{\n"
            f"    let t = target as usize; let mut dp = vec![false; t+1]; dp[0]=true;\n"
            f"    for x in nums.iter() {{ let xu = *x as usize; for i in (xu..=t).rev() {{ if dp[i-xu] {{ dp[i]=true; }} }} }}\n"
            f"    if dp[t] {{ {ret} }} else {{ false }}\n}}\n")


_BUILDERS = {
    "maximum-subarray-circular": {"javascript": _js_maxsubcirc, "typescript": _ts_maxsubcirc, "java": _java_maxsubcirc, "cpp": _cpp_maxsubcirc,
                                  "csharp": _csharp_maxsubcirc, "perl": _perl_maxsubcirc, "c": _c_maxsubcirc, "rust": _rust_maxsubcirc},
    "meeting-rooms": {"javascript": _js_meetrooms, "typescript": _ts_meetrooms, "java": _java_meetrooms, "cpp": _cpp_meetrooms,
                      "csharp": _csharp_meetrooms, "perl": _perl_meetrooms, "c": _c_meetrooms, "rust": _rust_meetrooms},
    "merge-sorted-arrays-inplace": {"javascript": _js_mergesorted, "typescript": _ts_mergesorted, "java": _java_mergesorted, "cpp": _cpp_mergesorted,
                                    "csharp": _csharp_mergesorted, "perl": _perl_mergesorted, "c": _c_mergesorted, "rust": _rust_mergesorted},
    "merge-two-sorted-lists": {"javascript": _js_mergetwolists, "typescript": _ts_mergetwolists, "java": _java_mergetwolists, "cpp": _cpp_mergetwolists,
                               "csharp": _csharp_mergetwolists, "perl": _perl_mergetwolists, "c": _c_mergetwolists, "rust": _rust_mergetwolists},
    "middle-of-linked-list": {"javascript": _js_midlist, "typescript": _ts_midlist, "java": _java_midlist, "cpp": _cpp_midlist,
                              "csharp": _csharp_midlist, "perl": _perl_midlist, "c": _c_midlist, "rust": _rust_midlist},
    "min-subarray-len-target-sum": {"javascript": _js_minsublen, "typescript": _ts_minsublen, "java": _java_minsublen, "cpp": _cpp_minsublen,
                                    "csharp": _csharp_minsublen, "perl": _perl_minsublen, "c": _c_minsublen, "rust": _rust_minsublen},
    "minimum-knight-moves": {"javascript": _js_knight, "typescript": _ts_knight, "java": _java_knight, "cpp": _cpp_knight,
                             "csharp": _csharp_knight, "perl": _perl_knight, "c": _c_knight, "rust": _rust_knight},
    "number-of-divisors": {"javascript": _js_numdiv, "typescript": _ts_numdiv, "java": _java_numdiv, "cpp": _cpp_numdiv,
                           "csharp": _csharp_numdiv, "perl": _perl_numdiv, "c": _c_numdiv, "rust": _rust_numdiv},
    "palindrome-linked-list": {"javascript": _js_palindlist, "typescript": _ts_palindlist, "java": _java_palindlist, "cpp": _cpp_palindlist,
                               "csharp": _csharp_palindlist, "perl": _perl_palindlist, "c": _c_palindlist, "rust": _rust_palindlist},
    "perfect-squares-min-count": {"javascript": _js_perfsq, "typescript": _ts_perfsq, "java": _java_perfsq, "cpp": _cpp_perfsq,
                                  "csharp": _csharp_perfsq, "perl": _perl_perfsq, "c": _c_perfsq, "rust": _rust_perfsq},
    "reverse-linked-list": {"javascript": _js_revlist, "typescript": _ts_revlist, "java": _java_revlist, "cpp": _cpp_revlist,
                            "csharp": _csharp_revlist, "perl": _perl_revlist, "c": _c_revlist, "rust": _rust_revlist},
    "rod-cutting": {"javascript": _js_rodcut, "typescript": _ts_rodcut, "java": _java_rodcut, "cpp": _cpp_rodcut,
                    "csharp": _csharp_rodcut, "perl": _perl_rodcut, "c": _c_rodcut, "rust": _rust_rodcut},
    "rotated-binary-search": {"javascript": _js_rotsearch, "typescript": _ts_rotsearch, "java": _java_rotsearch, "cpp": _cpp_rotsearch,
                              "csharp": _csharp_rotsearch, "perl": _perl_rotsearch, "c": _c_rotsearch, "rust": _rust_rotsearch},
    "search-insert-position": {"javascript": _js_searchinsert, "typescript": _ts_searchinsert, "java": _java_searchinsert, "cpp": _cpp_searchinsert,
                               "csharp": _csharp_searchinsert, "perl": _perl_searchinsert, "c": _c_searchinsert, "rust": _rust_searchinsert},
    "staircase": {"javascript": _js_staircase, "typescript": _ts_staircase, "java": _java_staircase, "cpp": _cpp_staircase,
                 "csharp": _csharp_staircase, "perl": _perl_staircase, "c": _c_staircase, "rust": _rust_staircase},
    "subarray-product-less-than-k": {"javascript": _js_subprod, "typescript": _ts_subprod, "java": _java_subprod, "cpp": _cpp_subprod,
                                     "csharp": _csharp_subprod, "perl": _perl_subprod, "c": _c_subprod, "rust": _rust_subprod},
    "subarray-sums-divisible-by-k": {"javascript": _js_subdivk, "typescript": _ts_subdivk, "java": _java_subdivk, "cpp": _cpp_subdivk,
                                     "csharp": _csharp_subdivk, "perl": _perl_subdivk, "c": _c_subdivk, "rust": _rust_subdivk},
    "subset-sum": {"javascript": _js_subsetsum, "typescript": _ts_subsetsum, "java": _java_subsetsum, "cpp": _cpp_subsetsum,
                   "csharp": _csharp_subsetsum, "perl": _perl_subsetsum, "c": _c_subsetsum, "rust": _rust_subsetsum},
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
                    adapter_version=f"{lang}-function-mega3-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
