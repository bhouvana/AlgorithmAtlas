"""Scales the final 11 problems (Function Mode) across the 8 original
working languages: remove-nth-from-end, restore-ip-addresses-count,
single-number-ii, ship-packages-within-days, target-sum-ways, task-scheduler,
triangle-minimum-path-sum, two-sum-count-pairs, unbounded-knapsack,
word-wrap, unique-permutations-count.
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


# ── remove-nth-from-end (simple array removal) ──────────────────────────────
def _js_removenth(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (f"function remove_nth_from_end(values, k) {{\n"
            f"    const n=values.length; const idx=n-k;\n"
            f"    const out=[...values.slice(0,idx), ...values.slice(idx+1)];\n"
            f"    return out{a};\n}}\n")


def _ts_removenth(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (f"function remove_nth_from_end(values: number[], k: number): number[] {{\n"
            f"    const n=values.length; const idx=n-k;\n"
            f"    const out: number[]=[...values.slice(0,idx), ...values.slice(idx+1)];\n"
            f"    return out{a};\n}}\n")


def _java_removenth(wrong):
    incr = "for (int i=0;i<out.length;i++) out[i]++;\n        " if wrong else ""
    return (f"class Solution {{ public int[] remove_nth_from_end(int[] values, int k) {{\n"
            f"    int n=values.length; int idx=n-k;\n"
            f"    int[] out=new int[n-1]; int p=0;\n"
            f"    for (int i=0;i<n;i++) {{ if (i!=idx) out[p++]=values[i]; }}\n"
            f"        {incr}return out;\n}} }}\n")


def _cpp_removenth(wrong):
    incr = "for (auto& x: out) x++;\n    " if wrong else ""
    return (f"class Solution {{ public: std::vector<int> remove_nth_from_end(std::vector<int> values, int k) {{\n"
            f"    int n=values.size(); int idx=n-k;\n"
            f"    std::vector<int> out;\n"
            f"    for (int i=0;i<n;i++) if (i!=idx) out.push_back(values[i]);\n"
            f"    {incr}return out;\n}} }};\n")


def _csharp_removenth(wrong):
    incr = "for (int i=0;i<outArr.Length;i++) outArr[i]++;\n        " if wrong else ""
    return (f"class Solution {{ public static int[] remove_nth_from_end(int[] values, int k) {{\n"
            f"    int n=values.Length; int idx=n-k;\n"
            f"    int[] outArr=new int[n-1]; int p=0;\n"
            f"    for (int i=0;i<n;i++) {{ if (i!=idx) outArr[p++]=values[i]; }}\n"
            f"        {incr}return outArr;\n}} }}\n")


def _perl_removenth(wrong):
    incr = "@out = map { $_ + 1 } @out;\n    " if wrong else ""
    return (f"sub remove_nth_from_end {{\n"
            f"    my ($values, $k) = @_;\n"
            f"    my $n = scalar(@$values); my $idx = $n-$k;\n"
            f"    my @out;\n"
            f"    for (my $i=0;$i<$n;$i++) {{ push @out, $values->[$i] if $i!=$idx; }}\n"
            f"    {incr}return \\@out;\n}}\n")


def _c_removenth(wrong):
    incr = "for (int i=0;i<n-1;i++) out[i]++;\n    " if wrong else ""
    return (f"AtlasIntArray remove_nth_from_end(AtlasIntArray values, int k) {{\n"
            f"    int n=values.size; int idx=n-k;\n"
            f"    int* out = (int*)malloc(sizeof(int)*(n-1>0?n-1:1)); int p=0;\n"
            f"    for (int i=0;i<n;i++) {{ if (i!=idx) out[p++]=values.data[i]; }}\n"
            f"    {incr}AtlasIntArray result; result.size=n-1; result.data=out;\n"
            f"    return result;\n}}\n")


def _rust_removenth(wrong):
    incr = "for x in out.iter_mut() { *x += 1; }\n    " if wrong else ""
    return (f"fn remove_nth_from_end(values: Vec<i32>, k: i32) -> Vec<i32> {{\n"
            f"    let n = values.len() as i32; let idx = n-k;\n"
            f"    let mut out: Vec<i32> = Vec::new();\n"
            f"    for i in 0..n {{ if i!=idx {{ out.push(values[i as usize]); }} }}\n"
            f"    {incr}out\n}}\n")


# ── restore-ip-addresses-count (backtracking count of valid splits) ─────────
def _js_restoreip(wrong):
    a = " + 1" if wrong else ""
    return (f"function restore_ip_count(s) {{\n"
            f"    const n=s.length; let count=0;\n"
            f"    function valid(seg) {{\n"
            f"        if (seg.length===0 || seg.length>3) return false;\n"
            f"        if (seg.length>1 && seg[0]==='0') return false;\n"
            f"        return parseInt(seg,10)<=255;\n"
            f"    }}\n"
            f"    for (let i=1;i<=3 && i<n;i++) {{\n"
            f"        for (let j=i+1;j<=i+3 && j<n;j++) {{\n"
            f"            for (let k=j+1;k<=j+3 && k<n;k++) {{\n"
            f"                const p1=s.slice(0,i), p2=s.slice(i,j), p3=s.slice(j,k), p4=s.slice(k);\n"
            f"                if (valid(p1) && valid(p2) && valid(p3) && valid(p4)) count++;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return count{a};\n}}\n")


def _ts_restoreip(wrong):
    a = " + 1" if wrong else ""
    return (f"function restore_ip_count(s: string): number {{\n"
            f"    const n=s.length; let count=0;\n"
            f"    function valid(seg: string): boolean {{\n"
            f"        if (seg.length===0 || seg.length>3) return false;\n"
            f"        if (seg.length>1 && seg[0]==='0') return false;\n"
            f"        return parseInt(seg,10)<=255;\n"
            f"    }}\n"
            f"    for (let i=1;i<=3 && i<n;i++) {{\n"
            f"        for (let j=i+1;j<=i+3 && j<n;j++) {{\n"
            f"            for (let k=j+1;k<=j+3 && k<n;k++) {{\n"
            f"                const p1=s.slice(0,i), p2=s.slice(i,j), p3=s.slice(j,k), p4=s.slice(k);\n"
            f"                if (valid(p1) && valid(p2) && valid(p3) && valid(p4)) count++;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return count{a};\n}}\n")


def _java_restoreip(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int restore_ip_count(String s) {{\n"
            f"    int n=s.length(); int count=0;\n"
            f"    for (int i=1;i<=3 && i<n;i++) {{\n"
            f"        for (int j=i+1;j<=i+3 && j<n;j++) {{\n"
            f"            for (int k=j+1;k<=j+3 && k<n;k++) {{\n"
            f"                String p1=s.substring(0,i), p2=s.substring(i,j), p3=s.substring(j,k), p4=s.substring(k);\n"
            f"                if (valid(p1) && valid(p2) && valid(p3) && valid(p4)) count++;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return count{a};\n}}\n"
            f"boolean valid(String seg) {{\n"
            f"    if (seg.length()==0 || seg.length()>3) return false;\n"
            f"    if (seg.length()>1 && seg.charAt(0)=='0') return false;\n"
            f"    return Integer.parseInt(seg)<=255;\n}} }}\n")


def _cpp_restoreip(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int restore_ip_count(std::string s) {{\n"
            f"    int n=s.size(); int count=0;\n"
            f"    for (int i=1;i<=3 && i<n;i++) {{\n"
            f"        for (int j=i+1;j<=i+3 && j<n;j++) {{\n"
            f"            for (int k=j+1;k<=j+3 && k<n;k++) {{\n"
            f"                std::string p1=s.substr(0,i), p2=s.substr(i,j-i), p3=s.substr(j,k-j), p4=s.substr(k);\n"
            f"                if (valid(p1) && valid(p2) && valid(p3) && valid(p4)) count++;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return count{a};\n}}\n"
            f"bool valid(std::string seg) {{\n"
            f"    if (seg.empty() || seg.size()>3) return false;\n"
            f"    if (seg.size()>1 && seg[0]=='0') return false;\n"
            f"    return std::stoi(seg)<=255;\n}} }};\n")


def _csharp_restoreip(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int restore_ip_count(string s) {{\n"
            f"    int n=s.Length; int count=0;\n"
            f"    for (int i=1;i<=3 && i<n;i++) {{\n"
            f"        for (int j=i+1;j<=i+3 && j<n;j++) {{\n"
            f"            for (int k=j+1;k<=j+3 && k<n;k++) {{\n"
            f"                string p1=s.Substring(0,i), p2=s.Substring(i,j-i), p3=s.Substring(j,k-j), p4=s.Substring(k);\n"
            f"                if (Valid(p1) && Valid(p2) && Valid(p3) && Valid(p4)) count++;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return count{a};\n}}\n"
            f"static bool Valid(string seg) {{\n"
            f"    if (seg.Length==0 || seg.Length>3) return false;\n"
            f"    if (seg.Length>1 && seg[0]=='0') return false;\n"
            f"    return int.Parse(seg)<=255;\n}} }}\n")


def _perl_restoreip(wrong):
    a = " + 1" if wrong else ""
    return (f"sub valid_ip_seg {{\n"
            f"    my ($seg) = @_;\n"
            f"    return 0 if length($seg)==0 || length($seg)>3;\n"
            f"    return 0 if length($seg)>1 && substr($seg,0,1) eq '0';\n"
            f"    return (($seg+0)<=255) ? 1 : 0;\n}}\n"
            f"sub restore_ip_count {{\n"
            f"    my ($s) = @_;\n"
            f"    my $n = length($s); my $count=0;\n"
            f"    for (my $i=1;$i<=3 && $i<$n;$i++) {{\n"
            f"        for (my $j=$i+1;$j<=$i+3 && $j<$n;$j++) {{\n"
            f"            for (my $k=$j+1;$k<=$j+3 && $k<$n;$k++) {{\n"
            f"                my $p1=substr($s,0,$i); my $p2=substr($s,$i,$j-$i); my $p3=substr($s,$j,$k-$j); my $p4=substr($s,$k);\n"
            f"                $count++ if valid_ip_seg($p1) && valid_ip_seg($p2) && valid_ip_seg($p3) && valid_ip_seg($p4);\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return $count{a};\n}}\n")


def _c_restoreip(wrong):
    a = " + 1" if wrong else ""
    return (f"int valid_ip_seg(char* seg, int len) {{\n"
            f"    if (len==0 || len>3) return 0;\n"
            f"    if (len>1 && seg[0]=='0') return 0;\n"
            f"    int val=0; for (int i=0;i<len;i++) val=val*10+(seg[i]-'0');\n"
            f"    return val<=255;\n}}\n"
            f"int restore_ip_count(char* s) {{\n"
            f"    int n = strlen(s); int count=0;\n"
            f"    for (int i=1;i<=3 && i<n;i++) {{\n"
            f"        for (int j=i+1;j<=i+3 && j<n;j++) {{\n"
            f"            for (int k=j+1;k<=j+3 && k<n;k++) {{\n"
            f"                if (valid_ip_seg(s,i) && valid_ip_seg(s+i,j-i) && valid_ip_seg(s+j,k-j) && valid_ip_seg(s+k,n-k)) count++;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return count{a};\n}}\n")


def _rust_restoreip(wrong):
    a = " + 1" if wrong else ""
    return (f"fn valid_ip_seg(seg: &str) -> bool {{\n"
            f"    if seg.is_empty() || seg.len()>3 {{ return false; }}\n"
            f"    if seg.len()>1 && seg.starts_with('0') {{ return false; }}\n"
            f"    seg.parse::<i32>().map(|v| v<=255).unwrap_or(false)\n}}\n"
            f"fn restore_ip_count(s: String) -> i32 {{\n"
            f"    let chars: Vec<char> = s.chars().collect(); let n = chars.len();\n"
            f"    let mut count=0i32;\n"
            f"    for i in 1..=3.min(n.saturating_sub(1)) {{\n"
            f"        for j in (i+1)..=(i+3).min(n.saturating_sub(1)) {{\n"
            f"            for k in (j+1)..=(j+3).min(n.saturating_sub(1)) {{\n"
            f"                let p1: String = chars[0..i].iter().collect();\n"
            f"                let p2: String = chars[i..j].iter().collect();\n"
            f"                let p3: String = chars[j..k].iter().collect();\n"
            f"                let p4: String = chars[k..n].iter().collect();\n"
            f"                if valid_ip_seg(&p1) && valid_ip_seg(&p2) && valid_ip_seg(&p3) && valid_ip_seg(&p4) {{ count+=1; }}\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    count{a}\n}}\n")


# ── single-number-ii (appears 3x except one, bit counting) ─────────────────
def _js_singlenumii(wrong):
    a = " + 1" if wrong else ""
    return (f"function single_number(nums) {{\n"
            f"    let ones=0, twos=0;\n"
            f"    for (const x of nums) {{ ones=(ones^x)&~twos; twos=(twos^x)&~ones; }}\n"
            f"    return ones{a};\n}}\n")


def _ts_singlenumii(wrong):
    a = " + 1" if wrong else ""
    return (f"function single_number(nums: number[]): number {{\n"
            f"    let ones=0, twos=0;\n"
            f"    for (const x of nums) {{ ones=(ones^x)&~twos; twos=(twos^x)&~ones; }}\n"
            f"    return ones{a};\n}}\n")


def _java_singlenumii(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int single_number(int[] nums) {{\n"
            f"    int ones=0, twos=0;\n"
            f"    for (int x: nums) {{ ones=(ones^x)&~twos; twos=(twos^x)&~ones; }}\n"
            f"    return ones{a};\n}} }}\n")


def _cpp_singlenumii(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int single_number(std::vector<int> nums) {{\n"
            f"    int ones=0, twos=0;\n"
            f"    for (int x: nums) {{ ones=(ones^x)&~twos; twos=(twos^x)&~ones; }}\n"
            f"    return ones{a};\n}} }};\n")


def _csharp_singlenumii(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int single_number(int[] nums) {{\n"
            f"    int ones=0, twos=0;\n"
            f"    foreach (int x in nums) {{ ones=(ones^x)&~twos; twos=(twos^x)&~ones; }}\n"
            f"    return ones{a};\n}} }}\n")


def _perl_singlenumii(wrong):
    a = " + 1" if wrong else ""
    return (f"use integer;\n"
            f"sub single_number {{\n"
            f"    my ($nums) = @_;\n"
            f"    my $ones=0; my $twos=0;\n"
            f"    foreach my $x (@$nums) {{ $ones=($ones^$x)&~$twos; $twos=($twos^$x)&~$ones; }}\n"
            f"    return $ones{a};\n}}\n")


def _c_singlenumii(wrong):
    a = " + 1" if wrong else ""
    return (f"int single_number(AtlasIntArray nums) {{\n"
            f"    int ones=0, twos=0;\n"
            f"    for (int i=0;i<nums.size;i++) {{ int x=nums.data[i]; ones=(ones^x)&~twos; twos=(twos^x)&~ones; }}\n"
            f"    return ones{a};\n}}\n")


def _rust_singlenumii(wrong):
    a = " + 1" if wrong else ""
    return (f"fn single_number(nums: Vec<i32>) -> i32 {{\n"
            f"    let mut ones=0i32; let mut twos=0i32;\n"
            f"    for x in nums.iter() {{ ones=(ones^x)&!twos; twos=(twos^x)&!ones; }}\n"
            f"    ones{a}\n}}\n")


# ── ship-packages-within-days (binary search on capacity) ───────────────────
def _js_shipdays(wrong):
    a = " + 1" if wrong else ""
    return (f"function ship_within_days(weights, days) {{\n"
            f"    function daysNeeded(cap) {{\n"
            f"        let d=1, cur=0;\n"
            f"        for (const w of weights) {{ if (cur+w>cap) {{ d++; cur=w; }} else cur+=w; }}\n"
            f"        return d;\n"
            f"    }}\n"
            f"    let lo=Math.max(...weights), hi=weights.reduce((a,b)=>a+b,0);\n"
            f"    while (lo<hi) {{ const mid=Math.floor((lo+hi)/2); if (daysNeeded(mid)<=days) hi=mid; else lo=mid+1; }}\n"
            f"    return lo{a};\n}}\n")


def _ts_shipdays(wrong):
    a = " + 1" if wrong else ""
    return (f"function ship_within_days(weights: number[], days: number): number {{\n"
            f"    function daysNeeded(cap: number): number {{\n"
            f"        let d=1, cur=0;\n"
            f"        for (const w of weights) {{ if (cur+w>cap) {{ d++; cur=w; }} else cur+=w; }}\n"
            f"        return d;\n"
            f"    }}\n"
            f"    let lo=Math.max(...weights), hi=weights.reduce((a,b)=>a+b,0);\n"
            f"    while (lo<hi) {{ const mid=Math.floor((lo+hi)/2); if (daysNeeded(mid)<=days) hi=mid; else lo=mid+1; }}\n"
            f"    return lo{a};\n}}\n")


def _java_shipdays(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int ship_within_days(int[] weights, int days) {{\n"
            f"    long lo=0, hi=0; for (int w: weights) {{ lo=Math.max(lo,w); hi+=w; }}\n"
            f"    while (lo<hi) {{ long mid=(lo+hi)/2; if (daysNeeded(weights,mid)<=days) hi=mid; else lo=mid+1; }}\n"
            f"    return (int)(lo{a});\n}}\n"
            f"int daysNeeded(int[] weights, long cap) {{\n"
            f"    int d=1; long cur=0;\n"
            f"    for (int w: weights) {{ if (cur+w>cap) {{ d++; cur=w; }} else cur+=w; }}\n"
            f"    return d;\n}} }}\n")


def _cpp_shipdays(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int ship_within_days(std::vector<int> weights, int days) {{\n"
            f"    long long lo=0, hi=0; for (int w: weights) {{ lo=std::max(lo,(long long)w); hi+=w; }}\n"
            f"    while (lo<hi) {{ long long mid=(lo+hi)/2; if (daysNeeded(weights,mid)<=days) hi=mid; else lo=mid+1; }}\n"
            f"    return (int)(lo{a});\n}}\n"
            f"int daysNeeded(std::vector<int>& weights, long long cap) {{\n"
            f"    int d=1; long long cur=0;\n"
            f"    for (int w: weights) {{ if (cur+w>cap) {{ d++; cur=w; }} else cur+=w; }}\n"
            f"    return d;\n}} }};\n")


def _csharp_shipdays(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int ship_within_days(int[] weights, int days) {{\n"
            f"    long lo=0, hi=0; foreach (int w in weights) {{ lo=System.Math.Max(lo,w); hi+=w; }}\n"
            f"    while (lo<hi) {{ long mid=(lo+hi)/2; if (DaysNeeded(weights,mid)<=days) hi=mid; else lo=mid+1; }}\n"
            f"    return (int)(lo{a});\n}}\n"
            f"static int DaysNeeded(int[] weights, long cap) {{\n"
            f"    int d=1; long cur=0;\n"
            f"    foreach (int w in weights) {{ if (cur+w>cap) {{ d++; cur=w; }} else cur+=w; }}\n"
            f"    return d;\n}} }}\n")


def _perl_shipdays(wrong):
    a = " + 1" if wrong else ""
    return (f"sub days_needed_ship {{\n"
            f"    my ($weights, $cap) = @_;\n"
            f"    my $d=1; my $cur=0;\n"
            f"    foreach my $w (@$weights) {{ if ($cur+$w>$cap) {{ $d++; $cur=$w; }} else {{ $cur+=$w; }} }}\n"
            f"    return $d;\n}}\n"
            f"sub ship_within_days {{\n"
            f"    my ($weights, $days) = @_;\n"
            f"    my $lo=0; my $hi=0;\n"
            f"    foreach my $w (@$weights) {{ $lo=$w if $w>$lo; $hi+=$w; }}\n"
            f"    while ($lo<$hi) {{ my $mid=int(($lo+$hi)/2); if (days_needed_ship($weights,$mid)<=$days) {{ $hi=$mid; }} else {{ $lo=$mid+1; }} }}\n"
            f"    return $lo{a};\n}}\n")


def _c_shipdays(wrong):
    a = " + 1" if wrong else ""
    return (f"int days_needed_ship(int* weights, int n, long long cap) {{\n"
            f"    int d=1; long long cur=0;\n"
            f"    for (int i=0;i<n;i++) {{ if (cur+weights[i]>cap) {{ d++; cur=weights[i]; }} else cur+=weights[i]; }}\n"
            f"    return d;\n}}\n"
            f"int ship_within_days(AtlasIntArray weights, int days) {{\n"
            f"    long long lo=0, hi=0;\n"
            f"    for (int i=0;i<weights.size;i++) {{ if (weights.data[i]>lo) lo=weights.data[i]; hi+=weights.data[i]; }}\n"
            f"    while (lo<hi) {{ long long mid=(lo+hi)/2; if (days_needed_ship(weights.data,weights.size,mid)<=days) hi=mid; else lo=mid+1; }}\n"
            f"    return (int)(lo{a});\n}}\n")


def _rust_shipdays(wrong):
    a = " + 1" if wrong else ""
    return (f"fn days_needed_ship(weights: &Vec<i32>, cap: i64) -> i32 {{\n"
            f"    let mut d=1i32; let mut cur=0i64;\n"
            f"    for &w in weights.iter() {{ if cur+(w as i64)>cap {{ d+=1; cur=w as i64; }} else {{ cur+=w as i64; }} }}\n"
            f"    d\n}}\n"
            f"fn ship_within_days(weights: Vec<i32>, days: i32) -> i32 {{\n"
            f"    let mut lo: i64 = *weights.iter().max().unwrap() as i64;\n"
            f"    let mut hi: i64 = weights.iter().map(|&x| x as i64).sum();\n"
            f"    while lo<hi {{ let mid=(lo+hi)/2; if days_needed_ship(&weights,mid)<=days {{ hi=mid; }} else {{ lo=mid+1; }} }}\n"
            f"    (lo{a}) as i32\n}}\n")


# ── target-sum-ways (DP with offset, small n<=20) ───────────────────────────
def _js_targetsum(wrong):
    a = " + 1" if wrong else ""
    return (f"function find_target_sum_ways(nums, target) {{\n"
            f"    const total = nums.reduce((a,b)=>a+b,0);\n"
            f"    if (Math.abs(target)>total) return 0{a};\n"
            f"    const offset=total; const size=2*total+1;\n"
            f"    let dp=new Array(size).fill(0); dp[offset]=1;\n"
            f"    for (const x of nums) {{\n"
            f"        const ndp=new Array(size).fill(0);\n"
            f"        for (let s=0;s<size;s++) {{\n"
            f"            if (dp[s]===0) continue;\n"
            f"            if (s+x<size) ndp[s+x]+=dp[s];\n"
            f"            if (s-x>=0) ndp[s-x]+=dp[s];\n"
            f"        }}\n"
            f"        dp=ndp;\n"
            f"    }}\n"
            f"    const idx=target+offset;\n"
            f"    return (idx>=0 && idx<size ? dp[idx] : 0){a};\n}}\n")


def _ts_targetsum(wrong):
    a = " + 1" if wrong else ""
    return (f"function find_target_sum_ways(nums: number[], target: number): number {{\n"
            f"    const total = nums.reduce((a,b)=>a+b,0);\n"
            f"    if (Math.abs(target)>total) return 0{a};\n"
            f"    const offset=total; const size=2*total+1;\n"
            f"    let dp: number[]=new Array(size).fill(0); dp[offset]=1;\n"
            f"    for (const x of nums) {{\n"
            f"        const ndp: number[]=new Array(size).fill(0);\n"
            f"        for (let s=0;s<size;s++) {{\n"
            f"            if (dp[s]===0) continue;\n"
            f"            if (s+x<size) ndp[s+x]+=dp[s];\n"
            f"            if (s-x>=0) ndp[s-x]+=dp[s];\n"
            f"        }}\n"
            f"        dp=ndp;\n"
            f"    }}\n"
            f"    const idx=target+offset;\n"
            f"    return (idx>=0 && idx<size ? dp[idx] : 0){a};\n}}\n")


def _java_targetsum(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int find_target_sum_ways(int[] nums, int target) {{\n"
            f"    int total=0; for (int x: nums) total+=x;\n"
            f"    if (Math.abs(target)>total) return 0{a};\n"
            f"    int offset=total; int size=2*total+1;\n"
            f"    long[] dp=new long[size]; dp[offset]=1;\n"
            f"    for (int x: nums) {{\n"
            f"        long[] ndp=new long[size];\n"
            f"        for (int s=0;s<size;s++) {{\n"
            f"            if (dp[s]==0) continue;\n"
            f"            if (s+x<size) ndp[s+x]+=dp[s];\n"
            f"            if (s-x>=0) ndp[s-x]+=dp[s];\n"
            f"        }}\n"
            f"        dp=ndp;\n"
            f"    }}\n"
            f"    int idx=target+offset;\n"
            f"    long r = (idx>=0 && idx<size) ? dp[idx] : 0;\n"
            f"    return (int)(r{a});\n}} }}\n")


def _cpp_targetsum(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int find_target_sum_ways(std::vector<int> nums, int target) {{\n"
            f"    int total=0; for (int x: nums) total+=x;\n"
            f"    if (std::abs(target)>total) return 0{a};\n"
            f"    int offset=total; int size=2*total+1;\n"
            f"    std::vector<long long> dp(size, 0); dp[offset]=1;\n"
            f"    for (int x: nums) {{\n"
            f"        std::vector<long long> ndp(size, 0);\n"
            f"        for (int s=0;s<size;s++) {{\n"
            f"            if (dp[s]==0) continue;\n"
            f"            if (s+x<size) ndp[s+x]+=dp[s];\n"
            f"            if (s-x>=0) ndp[s-x]+=dp[s];\n"
            f"        }}\n"
            f"        dp=ndp;\n"
            f"    }}\n"
            f"    int idx=target+offset;\n"
            f"    long long r = (idx>=0 && idx<size) ? dp[idx] : 0;\n"
            f"    return (int)(r{a});\n}} }};\n")


def _csharp_targetsum(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int find_target_sum_ways(int[] nums, int target) {{\n"
            f"    int total=0; foreach (int x in nums) total+=x;\n"
            f"    if (System.Math.Abs(target)>total) return 0{a};\n"
            f"    int offset=total; int size=2*total+1;\n"
            f"    long[] dp=new long[size]; dp[offset]=1;\n"
            f"    foreach (int x in nums) {{\n"
            f"        long[] ndp=new long[size];\n"
            f"        for (int s=0;s<size;s++) {{\n"
            f"            if (dp[s]==0) continue;\n"
            f"            if (s+x<size) ndp[s+x]+=dp[s];\n"
            f"            if (s-x>=0) ndp[s-x]+=dp[s];\n"
            f"        }}\n"
            f"        dp=ndp;\n"
            f"    }}\n"
            f"    int idx=target+offset;\n"
            f"    long r = (idx>=0 && idx<size) ? dp[idx] : 0;\n"
            f"    return (int)(r{a});\n}} }}\n")


def _perl_targetsum(wrong):
    a = " + 1" if wrong else ""
    return (f"sub find_target_sum_ways {{\n"
            f"    my ($nums, $target) = @_;\n"
            f"    my $total=0; foreach my $x (@$nums) {{ $total+=$x; }}\n"
            f"    return (0{a}) if abs($target)>$total;\n"
            f"    my $offset=$total; my $size=2*$total+1;\n"
            f"    my @dp = (0) x $size; $dp[$offset]=1;\n"
            f"    foreach my $x (@$nums) {{\n"
            f"        my @ndp = (0) x $size;\n"
            f"        for (my $s=0;$s<$size;$s++) {{\n"
            f"            next if $dp[$s]==0;\n"
            f"            $ndp[$s+$x]+=$dp[$s] if $s+$x<$size;\n"
            f"            $ndp[$s-$x]+=$dp[$s] if $s-$x>=0;\n"
            f"        }}\n"
            f"        @dp=@ndp;\n"
            f"    }}\n"
            f"    my $idx=$target+$offset;\n"
            f"    my $r = ($idx>=0 && $idx<$size) ? $dp[$idx] : 0;\n"
            f"    return $r{a};\n}}\n")


def _c_targetsum(wrong):
    a = " + 1" if wrong else ""
    return (f"int find_target_sum_ways(AtlasIntArray nums, int target) {{\n"
            f"    int total=0; for (int i=0;i<nums.size;i++) total+=nums.data[i];\n"
            f"    if (abs(target)>total) return 0{a};\n"
            f"    int offset=total; int size=2*total+1;\n"
            f"    long long* dp = (long long*)calloc(size, sizeof(long long)); dp[offset]=1;\n"
            f"    for (int k=0;k<nums.size;k++) {{\n"
            f"        int x = nums.data[k];\n"
            f"        long long* ndp = (long long*)calloc(size, sizeof(long long));\n"
            f"        for (int s=0;s<size;s++) {{\n"
            f"            if (dp[s]==0) continue;\n"
            f"            if (s+x<size) ndp[s+x]+=dp[s];\n"
            f"            if (s-x>=0) ndp[s-x]+=dp[s];\n"
            f"        }}\n"
            f"        free(dp); dp=ndp;\n"
            f"    }}\n"
            f"    int idx=target+offset;\n"
            f"    long long r = (idx>=0 && idx<size) ? dp[idx] : 0;\n"
            f"    free(dp);\n"
            f"    return (int)(r{a});\n}}\n")


def _rust_targetsum(wrong):
    a = " + 1" if wrong else ""
    return (f"fn find_target_sum_ways(nums: Vec<i32>, target: i32) -> i32 {{\n"
            f"    let total: i32 = nums.iter().sum();\n"
            f"    if target.abs()>total {{ return 0{a}; }}\n"
            f"    let offset = total; let size = (2*total+1) as usize;\n"
            f"    let mut dp = vec![0i64; size]; dp[offset as usize]=1;\n"
            f"    for &x in nums.iter() {{\n"
            f"        let mut ndp = vec![0i64; size];\n"
            f"        for s in 0..size as i32 {{\n"
            f"            if dp[s as usize]==0 {{ continue; }}\n"
            f"            if (s+x) < size as i32 {{ ndp[(s+x) as usize] += dp[s as usize]; }}\n"
            f"            if (s-x) >= 0 {{ ndp[(s-x) as usize] += dp[s as usize]; }}\n"
            f"        }}\n"
            f"        dp = ndp;\n"
            f"    }}\n"
            f"    let idx = target+offset;\n"
            f"    let r = if idx>=0 && (idx as usize)<size {{ dp[idx as usize] }} else {{ 0 }};\n"
            f"    (r{a}) as i32\n}}\n")


# ── task-scheduler (frequency-based greedy formula) ─────────────────────────
def _js_taskscheduler(wrong):
    a = " + 1" if wrong else ""
    return (f"function least_interval(counts, cooldown) {{\n"
            f"    const maxCount = Math.max(...counts);\n"
            f"    const maxCountFreq = counts.filter(c=>c===maxCount).length;\n"
            f"    const total = counts.reduce((a,b)=>a+b,0);\n"
            f"    const formula = (maxCount-1)*(cooldown+1)+maxCountFreq;\n"
            f"    return Math.max(total, formula){a};\n}}\n")


def _ts_taskscheduler(wrong):
    a = " + 1" if wrong else ""
    return (f"function least_interval(counts: number[], cooldown: number): number {{\n"
            f"    const maxCount = Math.max(...counts);\n"
            f"    const maxCountFreq = counts.filter(c=>c===maxCount).length;\n"
            f"    const total = counts.reduce((a,b)=>a+b,0);\n"
            f"    const formula = (maxCount-1)*(cooldown+1)+maxCountFreq;\n"
            f"    return Math.max(total, formula){a};\n}}\n")


def _java_taskscheduler(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int least_interval(int[] counts, int cooldown) {{\n"
            f"    int maxCount=0; for (int c: counts) maxCount=Math.max(maxCount,c);\n"
            f"    int maxCountFreq=0; for (int c: counts) if (c==maxCount) maxCountFreq++;\n"
            f"    int total=0; for (int c: counts) total+=c;\n"
            f"    int formula=(maxCount-1)*(cooldown+1)+maxCountFreq;\n"
            f"    return Math.max(total, formula){a};\n}} }}\n")


def _cpp_taskscheduler(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int least_interval(std::vector<int> counts, int cooldown) {{\n"
            f"    int maxCount=0; for (int c: counts) maxCount=std::max(maxCount,c);\n"
            f"    int maxCountFreq=0; for (int c: counts) if (c==maxCount) maxCountFreq++;\n"
            f"    int total=0; for (int c: counts) total+=c;\n"
            f"    int formula=(maxCount-1)*(cooldown+1)+maxCountFreq;\n"
            f"    return std::max(total, formula){a};\n}} }};\n")


def _csharp_taskscheduler(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int least_interval(int[] counts, int cooldown) {{\n"
            f"    int maxCount=0; foreach (int c in counts) maxCount=System.Math.Max(maxCount,c);\n"
            f"    int maxCountFreq=0; foreach (int c in counts) if (c==maxCount) maxCountFreq++;\n"
            f"    int total=0; foreach (int c in counts) total+=c;\n"
            f"    int formula=(maxCount-1)*(cooldown+1)+maxCountFreq;\n"
            f"    return System.Math.Max(total, formula){a};\n}} }}\n")


def _perl_taskscheduler(wrong):
    a = " + 1" if wrong else ""
    return (f"sub least_interval {{\n"
            f"    my ($counts, $cooldown) = @_;\n"
            f"    my $maxCount=0; foreach my $c (@$counts) {{ $maxCount=$c if $c>$maxCount; }}\n"
            f"    my $maxCountFreq=0; foreach my $c (@$counts) {{ $maxCountFreq++ if $c==$maxCount; }}\n"
            f"    my $total=0; foreach my $c (@$counts) {{ $total+=$c; }}\n"
            f"    my $formula=($maxCount-1)*($cooldown+1)+$maxCountFreq;\n"
            f"    return (($total>$formula)?$total:$formula){a};\n}}\n")


def _c_taskscheduler(wrong):
    a = " + 1" if wrong else ""
    return (f"int least_interval(AtlasIntArray counts, int cooldown) {{\n"
            f"    int maxCount=0; for (int i=0;i<counts.size;i++) if (counts.data[i]>maxCount) maxCount=counts.data[i];\n"
            f"    int maxCountFreq=0; for (int i=0;i<counts.size;i++) if (counts.data[i]==maxCount) maxCountFreq++;\n"
            f"    int total=0; for (int i=0;i<counts.size;i++) total+=counts.data[i];\n"
            f"    int formula=(maxCount-1)*(cooldown+1)+maxCountFreq;\n"
            f"    int r = (total>formula)?total:formula;\n"
            f"    return r{a};\n}}\n")


def _rust_taskscheduler(wrong):
    a = " + 1" if wrong else ""
    return (f"fn least_interval(counts: Vec<i32>, cooldown: i32) -> i32 {{\n"
            f"    let max_count = *counts.iter().max().unwrap();\n"
            f"    let max_count_freq = counts.iter().filter(|&&c| c==max_count).count() as i32;\n"
            f"    let total: i32 = counts.iter().sum();\n"
            f"    let formula = (max_count-1)*(cooldown+1)+max_count_freq;\n"
            f"    (total.max(formula)){a}\n}}\n")


# ── triangle-minimum-path-sum (2D nested array, bottom-up DP) ───────────────
def _js_triangle(wrong):
    a = " + 1" if wrong else ""
    return (f"function minimum_total(triangle) {{\n"
            f"    const n=triangle.length;\n"
            f"    const dp=triangle[n-1].slice();\n"
            f"    for (let i=n-2;i>=0;i--) {{\n"
            f"        for (let j=0;j<=i;j++) dp[j]=triangle[i][j]+Math.min(dp[j],dp[j+1]);\n"
            f"    }}\n"
            f"    return dp[0]{a};\n}}\n")


def _ts_triangle(wrong):
    a = " + 1" if wrong else ""
    return (f"function minimum_total(triangle: number[][]): number {{\n"
            f"    const n=triangle.length;\n"
            f"    const dp: number[]=triangle[n-1].slice();\n"
            f"    for (let i=n-2;i>=0;i--) {{\n"
            f"        for (let j=0;j<=i;j++) dp[j]=triangle[i][j]+Math.min(dp[j],dp[j+1]);\n"
            f"    }}\n"
            f"    return dp[0]{a};\n}}\n")


def _java_triangle(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int minimum_total(int[][] triangle) {{\n"
            f"    int n=triangle.length;\n"
            f"    int[] dp = triangle[n-1].clone();\n"
            f"    for (int i=n-2;i>=0;i--) {{\n"
            f"        for (int j=0;j<=i;j++) dp[j]=triangle[i][j]+Math.min(dp[j],dp[j+1]);\n"
            f"    }}\n"
            f"    return dp[0]{a};\n}} }}\n")


def _cpp_triangle(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int minimum_total(std::vector<std::vector<int>> triangle) {{\n"
            f"    int n=triangle.size();\n"
            f"    std::vector<int> dp = triangle[n-1];\n"
            f"    for (int i=n-2;i>=0;i--) {{\n"
            f"        for (int j=0;j<=i;j++) dp[j]=triangle[i][j]+std::min(dp[j],dp[j+1]);\n"
            f"    }}\n"
            f"    return dp[0]{a};\n}} }};\n")


def _csharp_triangle(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int minimum_total(int[][] triangle) {{\n"
            f"    int n=triangle.Length;\n"
            f"    int[] dp = (int[])triangle[n-1].Clone();\n"
            f"    for (int i=n-2;i>=0;i--) {{\n"
            f"        for (int j=0;j<=i;j++) dp[j]=triangle[i][j]+System.Math.Min(dp[j],dp[j+1]);\n"
            f"    }}\n"
            f"    return dp[0]{a};\n}} }}\n")


def _perl_triangle(wrong):
    a = " + 1" if wrong else ""
    return (f"sub minimum_total {{\n"
            f"    my ($triangle) = @_;\n"
            f"    my $n = scalar(@$triangle);\n"
            f"    my @dp = @{{$triangle->[$n-1]}};\n"
            f"    for (my $i=$n-2;$i>=0;$i--) {{\n"
            f"        for (my $j=0;$j<=$i;$j++) {{\n"
            f"            my $m = ($dp[$j]<$dp[$j+1])?$dp[$j]:$dp[$j+1];\n"
            f"            $dp[$j]=$triangle->[$i][$j]+$m;\n"
            f"        }}\n"
            f"    }}\n"
            f"    return $dp[0]{a};\n}}\n")


def _c_triangle(wrong):
    a = " + 1" if wrong else ""
    return (f"int minimum_total(AtlasIntMatrix triangle) {{\n"
            f"    int n = triangle.size;\n"
            f"    int lastLen = triangle.data[n-1].size;\n"
            f"    int* dp = (int*)malloc(sizeof(int)*lastLen);\n"
            f"    for (int j=0;j<lastLen;j++) dp[j]=triangle.data[n-1].data[j];\n"
            f"    for (int i=n-2;i>=0;i--) {{\n"
            f"        for (int j=0;j<=i;j++) {{\n"
            f"            int m = (dp[j]<dp[j+1]) ? dp[j] : dp[j+1];\n"
            f"            dp[j]=triangle.data[i].data[j]+m;\n"
            f"        }}\n"
            f"    }}\n"
            f"    int r=dp[0]; free(dp);\n"
            f"    return r{a};\n}}\n")


def _rust_triangle(wrong):
    a = " + 1" if wrong else ""
    return (f"fn minimum_total(triangle: Vec<Vec<i32>>) -> i32 {{\n"
            f"    let n = triangle.len();\n"
            f"    let mut dp = triangle[n-1].clone();\n"
            f"    for i in (0..n-1).rev() {{\n"
            f"        for j in 0..=i {{ dp[j] = triangle[i][j] + dp[j].min(dp[j+1]); }}\n"
            f"    }}\n"
            f"    (dp[0]){a}\n}}\n")


# ── two-sum-count-pairs (count unordered index-pairs summing to target) ────
def _js_twosumcount(wrong):
    a = " + 1" if wrong else ""
    return (f"function count_pairs(nums, target) {{\n"
            f"    const freq={{}}; let count=0;\n"
            f"    for (const x of nums) {{\n"
            f"        const need=target-x;\n"
            f"        if (freq[need]) count+=freq[need];\n"
            f"        freq[x]=(freq[x]||0)+1;\n"
            f"    }}\n"
            f"    return count{a};\n}}\n")


def _ts_twosumcount(wrong):
    a = " + 1" if wrong else ""
    return (f"function count_pairs(nums: number[], target: number): number {{\n"
            f"    const freq: Record<number,number>={{}}; let count=0;\n"
            f"    for (const x of nums) {{\n"
            f"        const need=target-x;\n"
            f"        if (freq[need]) count+=freq[need];\n"
            f"        freq[x]=(freq[x]||0)+1;\n"
            f"    }}\n"
            f"    return count{a};\n}}\n")


def _java_twosumcount(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int count_pairs(int[] nums, int target) {{\n"
            f"    java.util.Map<Integer,Integer> freq = new java.util.HashMap<>(); long count=0;\n"
            f"    for (int x: nums) {{\n"
            f"        int need=target-x;\n"
            f"        count += freq.getOrDefault(need, 0);\n"
            f"        freq.merge(x,1,Integer::sum);\n"
            f"    }}\n"
            f"    return (int)(count{a});\n}} }}\n")


def _cpp_twosumcount(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int count_pairs(std::vector<int> nums, int target) {{\n"
            f"    std::unordered_map<int,int> freq; long long count=0;\n"
            f"    for (int x: nums) {{\n"
            f"        int need=target-x;\n"
            f"        auto it=freq.find(need); if (it!=freq.end()) count+=it->second;\n"
            f"        freq[x]++;\n"
            f"    }}\n"
            f"    return (int)(count{a});\n}} }};\n")


def _csharp_twosumcount(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int count_pairs(int[] nums, int target) {{\n"
            f"    var freq = new System.Collections.Generic.Dictionary<int,int>(); long count=0;\n"
            f"    foreach (int x in nums) {{\n"
            f"        int need=target-x;\n"
            f"        if (freq.ContainsKey(need)) count+=freq[need];\n"
            f"        if (!freq.ContainsKey(x)) freq[x]=0; freq[x]++;\n"
            f"    }}\n"
            f"    return (int)(count{a});\n}} }}\n")


def _perl_twosumcount(wrong):
    a = " + 1" if wrong else ""
    return (f"sub count_pairs {{\n"
            f"    my ($nums, $target) = @_;\n"
            f"    my %freq; my $count=0;\n"
            f"    foreach my $x (@$nums) {{\n"
            f"        my $need=$target-$x;\n"
            f"        $count+=$freq{{$need}} if exists $freq{{$need}};\n"
            f"        $freq{{$x}}++;\n"
            f"    }}\n"
            f"    return $count{a};\n}}\n")


def _c_twosumcount(wrong):
    a = " + 1" if wrong else ""
    return (f"int count_pairs(AtlasIntArray nums, int target) {{\n"
            f"    int minv=0, maxv=0;\n"
            f"    for (int i=0;i<nums.size;i++) {{ if (nums.data[i]<minv) minv=nums.data[i]; if (nums.data[i]>maxv) maxv=nums.data[i]; }}\n"
            f"    int range = maxv-minv+1;\n"
            f"    int* freq = (int*)calloc(range, sizeof(int));\n"
            f"    long long count=0;\n"
            f"    for (int i=0;i<nums.size;i++) {{\n"
            f"        int x = nums.data[i]; int need = target-x;\n"
            f"        if (need>=minv && need<=maxv) count+=freq[need-minv];\n"
            f"        freq[x-minv]++;\n"
            f"    }}\n"
            f"    free(freq);\n"
            f"    return (int)(count{a});\n}}\n")


def _rust_twosumcount(wrong):
    a = " + 1" if wrong else ""
    return (f"fn count_pairs(nums: Vec<i32>, target: i32) -> i32 {{\n"
            f"    let mut freq: std::collections::HashMap<i32,i32> = std::collections::HashMap::new();\n"
            f"    let mut count: i64 = 0;\n"
            f"    for &x in nums.iter() {{\n"
            f"        let need = target-x;\n"
            f"        if let Some(&c) = freq.get(&need) {{ count += c as i64; }}\n"
            f"        *freq.entry(x).or_insert(0) += 1;\n"
            f"    }}\n"
            f"    (count{a}) as i32\n}}\n")


# ── unbounded-knapsack (weights/values, capacity) ───────────────────────────
def _js_unboundedks(wrong):
    a = " + 1" if wrong else ""
    return (f"function unbounded_knapsack(weights, values, capacity) {{\n"
            f"    const dp=new Array(capacity+1).fill(0);\n"
            f"    for (let c=1;c<=capacity;c++) {{\n"
            f"        for (let i=0;i<weights.length;i++) {{\n"
            f"            if (weights[i]<=c) dp[c]=Math.max(dp[c], dp[c-weights[i]]+values[i]);\n"
            f"        }}\n"
            f"    }}\n"
            f"    return dp[capacity]{a};\n}}\n")


def _ts_unboundedks(wrong):
    a = " + 1" if wrong else ""
    return (f"function unbounded_knapsack(weights: number[], values: number[], capacity: number): number {{\n"
            f"    const dp: number[]=new Array(capacity+1).fill(0);\n"
            f"    for (let c=1;c<=capacity;c++) {{\n"
            f"        for (let i=0;i<weights.length;i++) {{\n"
            f"            if (weights[i]<=c) dp[c]=Math.max(dp[c], dp[c-weights[i]]+values[i]);\n"
            f"        }}\n"
            f"    }}\n"
            f"    return dp[capacity]{a};\n}}\n")


def _java_unboundedks(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int unbounded_knapsack(int[] weights, int[] values, int capacity) {{\n"
            f"    int[] dp = new int[capacity+1];\n"
            f"    for (int c=1;c<=capacity;c++) {{\n"
            f"        for (int i=0;i<weights.length;i++) {{\n"
            f"            if (weights[i]<=c) dp[c]=Math.max(dp[c], dp[c-weights[i]]+values[i]);\n"
            f"        }}\n"
            f"    }}\n"
            f"    return dp[capacity]{a};\n}} }}\n")


def _cpp_unboundedks(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int unbounded_knapsack(std::vector<int> weights, std::vector<int> values, int capacity) {{\n"
            f"    std::vector<int> dp(capacity+1, 0);\n"
            f"    for (int c=1;c<=capacity;c++) {{\n"
            f"        for (size_t i=0;i<weights.size();i++) {{\n"
            f"            if (weights[i]<=c) dp[c]=std::max(dp[c], dp[c-weights[i]]+values[i]);\n"
            f"        }}\n"
            f"    }}\n"
            f"    return dp[capacity]{a};\n}} }};\n")


def _csharp_unboundedks(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int unbounded_knapsack(int[] weights, int[] values, int capacity) {{\n"
            f"    int[] dp = new int[capacity+1];\n"
            f"    for (int c=1;c<=capacity;c++) {{\n"
            f"        for (int i=0;i<weights.Length;i++) {{\n"
            f"            if (weights[i]<=c) dp[c]=System.Math.Max(dp[c], dp[c-weights[i]]+values[i]);\n"
            f"        }}\n"
            f"    }}\n"
            f"    return dp[capacity]{a};\n}} }}\n")


def _perl_unboundedks(wrong):
    a = " + 1" if wrong else ""
    return (f"sub unbounded_knapsack {{\n"
            f"    my ($weights, $values, $capacity) = @_;\n"
            f"    my @dp = (0) x ($capacity+1);\n"
            f"    for (my $c=1;$c<=$capacity;$c++) {{\n"
            f"        for (my $i=0;$i<scalar(@$weights);$i++) {{\n"
            f"            if ($weights->[$i]<=$c) {{\n"
            f"                my $v = $dp[$c-$weights->[$i]]+$values->[$i];\n"
            f"                $dp[$c]=$v if $v>$dp[$c];\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return $dp[$capacity]{a};\n}}\n")


def _c_unboundedks(wrong):
    a = " + 1" if wrong else ""
    return (f"int unbounded_knapsack(AtlasIntArray weights, AtlasIntArray values, int capacity) {{\n"
            f"    int* dp = (int*)calloc(capacity+1, sizeof(int));\n"
            f"    for (int c=1;c<=capacity;c++) {{\n"
            f"        for (int i=0;i<weights.size;i++) {{\n"
            f"            if (weights.data[i]<=c) {{\n"
            f"                int v = dp[c-weights.data[i]]+values.data[i];\n"
            f"                if (v>dp[c]) dp[c]=v;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    int r=dp[capacity]; free(dp);\n"
            f"    return r{a};\n}}\n")


def _rust_unboundedks(wrong):
    a = " + 1" if wrong else ""
    return (f"fn unbounded_knapsack(weights: Vec<i32>, values: Vec<i32>, capacity: i32) -> i32 {{\n"
            f"    let cap = capacity as usize; let mut dp = vec![0i32; cap+1];\n"
            f"    for c in 1..=cap {{\n"
            f"        for i in 0..weights.len() {{\n"
            f"            let w = weights[i] as usize;\n"
            f"            if w<=c {{ let v = dp[c-w]+values[i]; if v>dp[c] {{ dp[c]=v; }} }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    (dp[cap]){a}\n}}\n")


# ── word-wrap (DP min cost line-wrap, lengths + width) ──────────────────────
def _js_wordwrap(wrong):
    a = " + 1" if wrong else ""
    return (f"function word_wrap(lengths, width) {{\n"
            f"    const n=lengths.length; const INF=1e15;\n"
            f"    const dp=new Array(n+1).fill(INF); dp[n]=0;\n"
            f"    for (let i=n-1;i>=0;i--) {{\n"
            f"        let lineLen=-1;\n"
            f"        for (let j=i;j<n;j++) {{\n"
            f"            lineLen += lengths[j]+1;\n"
            f"            if (lineLen>width) break;\n"
            f"            const cost = (j===n-1) ? 0 : (width-lineLen)*(width-lineLen)*(width-lineLen);\n"
            f"            if (dp[j+1]+cost<dp[i]) dp[i]=dp[j+1]+cost;\n"
            f"        }}\n"
            f"    }}\n"
            f"    return dp[0]{a};\n}}\n")


def _ts_wordwrap(wrong):
    a = " + 1" if wrong else ""
    return (f"function word_wrap(lengths: number[], width: number): number {{\n"
            f"    const n=lengths.length; const INF=1e15;\n"
            f"    const dp: number[]=new Array(n+1).fill(INF); dp[n]=0;\n"
            f"    for (let i=n-1;i>=0;i--) {{\n"
            f"        let lineLen=-1;\n"
            f"        for (let j=i;j<n;j++) {{\n"
            f"            lineLen += lengths[j]+1;\n"
            f"            if (lineLen>width) break;\n"
            f"            const cost = (j===n-1) ? 0 : (width-lineLen)*(width-lineLen)*(width-lineLen);\n"
            f"            if (dp[j+1]+cost<dp[i]) dp[i]=dp[j+1]+cost;\n"
            f"        }}\n"
            f"    }}\n"
            f"    return dp[0]{a};\n}}\n")


def _java_wordwrap(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int word_wrap(int[] lengths, int width) {{\n"
            f"    int n=lengths.length; long INF=Long.MAX_VALUE/2;\n"
            f"    long[] dp = new long[n+1]; java.util.Arrays.fill(dp, INF); dp[n]=0;\n"
            f"    for (int i=n-1;i>=0;i--) {{\n"
            f"        long lineLen=-1;\n"
            f"        for (int j=i;j<n;j++) {{\n"
            f"            lineLen += lengths[j]+1;\n"
            f"            if (lineLen>width) break;\n"
            f"            long cost = (j==n-1) ? 0 : (width-lineLen)*(width-lineLen)*(width-lineLen);\n"
            f"            if (dp[j+1]+cost<dp[i]) dp[i]=dp[j+1]+cost;\n"
            f"        }}\n"
            f"    }}\n"
            f"    return (int)(dp[0]{a});\n}} }}\n")


def _cpp_wordwrap(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int word_wrap(std::vector<int> lengths, int width) {{\n"
            f"    int n=lengths.size(); long long INF=1000000000000LL;\n"
            f"    std::vector<long long> dp(n+1, INF); dp[n]=0;\n"
            f"    for (int i=n-1;i>=0;i--) {{\n"
            f"        long long lineLen=-1;\n"
            f"        for (int j=i;j<n;j++) {{\n"
            f"            lineLen += lengths[j]+1;\n"
            f"            if (lineLen>width) break;\n"
            f"            long long cost = (j==n-1) ? 0 : (width-lineLen)*(width-lineLen)*(width-lineLen);\n"
            f"            if (dp[j+1]+cost<dp[i]) dp[i]=dp[j+1]+cost;\n"
            f"        }}\n"
            f"    }}\n"
            f"    return (int)(dp[0]{a});\n}} }};\n")


def _csharp_wordwrap(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int word_wrap(int[] lengths, int width) {{\n"
            f"    int n=lengths.Length; long INF=long.MaxValue/2;\n"
            f"    long[] dp = new long[n+1]; for (int i=0;i<=n;i++) dp[i]=INF; dp[n]=0;\n"
            f"    for (int i=n-1;i>=0;i--) {{\n"
            f"        long lineLen=-1;\n"
            f"        for (int j=i;j<n;j++) {{\n"
            f"            lineLen += lengths[j]+1;\n"
            f"            if (lineLen>width) break;\n"
            f"            long cost = (j==n-1) ? 0 : (width-lineLen)*(width-lineLen)*(width-lineLen);\n"
            f"            if (dp[j+1]+cost<dp[i]) dp[i]=dp[j+1]+cost;\n"
            f"        }}\n"
            f"    }}\n"
            f"    return (int)(dp[0]{a});\n}} }}\n")


def _perl_wordwrap(wrong):
    a = " + 1" if wrong else ""
    return (f"sub word_wrap {{\n"
            f"    my ($lengths, $width) = @_;\n"
            f"    my $n = scalar(@$lengths); my $INF = 9**9**9;\n"
            f"    my @dp = ($INF) x ($n+1); $dp[$n]=0;\n"
            f"    for (my $i=$n-1;$i>=0;$i--) {{\n"
            f"        my $lineLen=-1;\n"
            f"        for (my $j=$i;$j<$n;$j++) {{\n"
            f"            $lineLen += $lengths->[$j]+1;\n"
            f"            last if $lineLen>$width;\n"
            f"            my $cost = ($j==$n-1) ? 0 : ($width-$lineLen)*($width-$lineLen)*($width-$lineLen);\n"
            f"            my $v = $dp[$j+1]+$cost;\n"
            f"            $dp[$i]=$v if $v<$dp[$i];\n"
            f"        }}\n"
            f"    }}\n"
            f"    return $dp[0]{a};\n}}\n")


def _c_wordwrap(wrong):
    a = " + 1" if wrong else ""
    return (f"int word_wrap(AtlasIntArray lengths, int width) {{\n"
            f"    int n = lengths.size; long long INF = 1000000000000LL;\n"
            f"    long long* dp = (long long*)malloc(sizeof(long long)*(n+1));\n"
            f"    for (int i=0;i<=n;i++) dp[i]=INF; dp[n]=0;\n"
            f"    for (int i=n-1;i>=0;i--) {{\n"
            f"        long long lineLen=-1;\n"
            f"        for (int j=i;j<n;j++) {{\n"
            f"            lineLen += lengths.data[j]+1;\n"
            f"            if (lineLen>width) break;\n"
            f"            long long cost = (j==n-1) ? 0 : (width-lineLen)*(width-lineLen)*(width-lineLen);\n"
            f"            if (dp[j+1]+cost<dp[i]) dp[i]=dp[j+1]+cost;\n"
            f"        }}\n"
            f"    }}\n"
            f"    long long r=dp[0]; free(dp);\n"
            f"    return (int)(r{a});\n}}\n")


def _rust_wordwrap(wrong):
    a = " + 1" if wrong else ""
    return (f"fn word_wrap(lengths: Vec<i32>, width: i32) -> i32 {{\n"
            f"    let n = lengths.len(); let inf: i64 = 1_000_000_000_000;\n"
            f"    let mut dp = vec![inf; n+1]; dp[n]=0;\n"
            f"    for i in (0..n).rev() {{\n"
            f"        let mut line_len: i64 = -1;\n"
            f"        for j in i..n {{\n"
            f"            line_len += (lengths[j]+1) as i64;\n"
            f"            if line_len > width as i64 {{ break; }}\n"
            f"            let cost: i64 = if j==n-1 {{ 0 }} else {{ (width as i64-line_len)*(width as i64-line_len)*(width as i64-line_len) }};\n"
            f"            if dp[j+1]+cost<dp[i] {{ dp[i]=dp[j+1]+cost; }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    (dp[0]{a}) as i32\n}}\n")


# ── unique-permutations-count (n! / prod(count(v)!), small n<=10) ──────────
def _js_uniqueperm(wrong):
    a = " + 1" if wrong else ""
    return (f"function count_unique_permutations(nums) {{\n"
            f"    function fact(n) {{ let r=1; for (let i=2;i<=n;i++) r*=i; return r; }}\n"
            f"    const freq={{}};\n"
            f"    for (const x of nums) freq[x]=(freq[x]||0)+1;\n"
            f"    let denom=1; for (const k in freq) denom*=fact(freq[k]);\n"
            f"    return Math.round(fact(nums.length)/denom){a};\n}}\n")


def _ts_uniqueperm(wrong):
    a = " + 1" if wrong else ""
    return (f"function count_unique_permutations(nums: number[]): number {{\n"
            f"    function fact(n: number): number {{ let r=1; for (let i=2;i<=n;i++) r*=i; return r; }}\n"
            f"    const freq: Record<number,number>={{}};\n"
            f"    for (const x of nums) freq[x]=(freq[x]||0)+1;\n"
            f"    let denom=1; for (const k in freq) denom*=fact(freq[k]);\n"
            f"    return Math.round(fact(nums.length)/denom){a};\n}}\n")


def _java_uniqueperm(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public int count_unique_permutations(int[] nums) {{\n"
            f"    java.util.Map<Integer,Integer> freq = new java.util.HashMap<>();\n"
            f"    for (int x: nums) freq.merge(x,1,Integer::sum);\n"
            f"    long denom=1; for (int v: freq.values()) denom*=fact(v);\n"
            f"    long r = fact(nums.length)/denom;\n"
            f"    return (int)(r{a});\n}}\n"
            f"long fact(int n) {{ long r=1; for (int i=2;i<=n;i++) r*=i; return r; }} }}\n")


def _cpp_uniqueperm(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public: int count_unique_permutations(std::vector<int> nums) {{\n"
            f"    std::unordered_map<int,int> freq;\n"
            f"    for (int x: nums) freq[x]++;\n"
            f"    long long denom=1; for (auto& p: freq) denom*=fact(p.second);\n"
            f"    long long r = fact(nums.size())/denom;\n"
            f"    return (int)(r{a});\n}}\n"
            f"long long fact(long long n) {{ long long r=1; for (long long i=2;i<=n;i++) r*=i; return r; }} }};\n")


def _csharp_uniqueperm(wrong):
    a = " + 1" if wrong else ""
    return (f"class Solution {{ public static int count_unique_permutations(int[] nums) {{\n"
            f"    var freq = new System.Collections.Generic.Dictionary<int,int>();\n"
            f"    foreach (int x in nums) {{ if (!freq.ContainsKey(x)) freq[x]=0; freq[x]++; }}\n"
            f"    long denom=1; foreach (var v in freq.Values) denom*=Fact(v);\n"
            f"    long r = Fact(nums.Length)/denom;\n"
            f"    return (int)(r{a});\n}}\n"
            f"static long Fact(long n) {{ long r=1; for (long i=2;i<=n;i++) r*=i; return r; }} }}\n")


def _perl_uniqueperm(wrong):
    a = " + 1" if wrong else ""
    return (f"sub fact_up {{ my ($n) = @_; my $r=1; for (my $i=2;$i<=$n;$i++) {{ $r*=$i; }} return $r; }}\n"
            f"sub count_unique_permutations {{\n"
            f"    my ($nums) = @_;\n"
            f"    my %freq; foreach my $x (@$nums) {{ $freq{{$x}}++; }}\n"
            f"    my $denom=1; foreach my $v (values %freq) {{ $denom*=fact_up($v); }}\n"
            f"    my $r = fact_up(scalar(@$nums))/$denom;\n"
            f"    return $r{a};\n}}\n")


def _c_uniqueperm(wrong):
    a = " + 1" if wrong else ""
    return (f"long long fact_up(int n) {{ long long r=1; for (int i=2;i<=n;i++) r*=i; return r; }}\n"
            f"int count_unique_permutations(AtlasIntArray nums) {{\n"
            f"    int minv=nums.data[0], maxv=nums.data[0];\n"
            f"    for (int i=0;i<nums.size;i++) {{ if (nums.data[i]<minv) minv=nums.data[i]; if (nums.data[i]>maxv) maxv=nums.data[i]; }}\n"
            f"    int range = maxv-minv+1;\n"
            f"    int* freq = (int*)calloc(range, sizeof(int));\n"
            f"    for (int i=0;i<nums.size;i++) freq[nums.data[i]-minv]++;\n"
            f"    long long denom=1; for (int i=0;i<range;i++) if (freq[i]>0) denom*=fact_up(freq[i]);\n"
            f"    long long r = fact_up(nums.size)/denom;\n"
            f"    free(freq);\n"
            f"    return (int)(r{a});\n}}\n")


def _rust_uniqueperm(wrong):
    a = " + 1" if wrong else ""
    return (f"fn fact_up(n: i64) -> i64 {{ let mut r=1i64; for i in 2..=n {{ r*=i; }} r }}\n"
            f"fn count_unique_permutations(nums: Vec<i32>) -> i32 {{\n"
            f"    let mut freq: std::collections::HashMap<i32,i64> = std::collections::HashMap::new();\n"
            f"    for &x in nums.iter() {{ *freq.entry(x).or_insert(0) += 1; }}\n"
            f"    let mut denom: i64 = 1; for &v in freq.values() {{ denom *= fact_up(v); }}\n"
            f"    let r = fact_up(nums.len() as i64) / denom;\n"
            f"    (r{a}) as i32\n}}\n")


_BUILDERS = {
    "remove-nth-from-end": {"javascript": _js_removenth, "typescript": _ts_removenth, "java": _java_removenth, "cpp": _cpp_removenth,
                            "csharp": _csharp_removenth, "perl": _perl_removenth, "c": _c_removenth, "rust": _rust_removenth},
    "restore-ip-addresses-count": {"javascript": _js_restoreip, "typescript": _ts_restoreip, "java": _java_restoreip, "cpp": _cpp_restoreip,
                                   "csharp": _csharp_restoreip, "perl": _perl_restoreip, "c": _c_restoreip, "rust": _rust_restoreip},
    "single-number-ii": {"javascript": _js_singlenumii, "typescript": _ts_singlenumii, "java": _java_singlenumii, "cpp": _cpp_singlenumii,
                        "csharp": _csharp_singlenumii, "perl": _perl_singlenumii, "c": _c_singlenumii, "rust": _rust_singlenumii},
    "ship-packages-within-days": {"javascript": _js_shipdays, "typescript": _ts_shipdays, "java": _java_shipdays, "cpp": _cpp_shipdays,
                                  "csharp": _csharp_shipdays, "perl": _perl_shipdays, "c": _c_shipdays, "rust": _rust_shipdays},
    "target-sum-ways": {"javascript": _js_targetsum, "typescript": _ts_targetsum, "java": _java_targetsum, "cpp": _cpp_targetsum,
                        "csharp": _csharp_targetsum, "perl": _perl_targetsum, "c": _c_targetsum, "rust": _rust_targetsum},
    "task-scheduler": {"javascript": _js_taskscheduler, "typescript": _ts_taskscheduler, "java": _java_taskscheduler, "cpp": _cpp_taskscheduler,
                       "csharp": _csharp_taskscheduler, "perl": _perl_taskscheduler, "c": _c_taskscheduler, "rust": _rust_taskscheduler},
    "triangle-minimum-path-sum": {"javascript": _js_triangle, "typescript": _ts_triangle, "java": _java_triangle, "cpp": _cpp_triangle,
                                  "csharp": _csharp_triangle, "perl": _perl_triangle, "c": _c_triangle, "rust": _rust_triangle},
    "two-sum-count-pairs": {"javascript": _js_twosumcount, "typescript": _ts_twosumcount, "java": _java_twosumcount, "cpp": _cpp_twosumcount,
                            "csharp": _csharp_twosumcount, "perl": _perl_twosumcount, "c": _c_twosumcount, "rust": _rust_twosumcount},
    "unbounded-knapsack": {"javascript": _js_unboundedks, "typescript": _ts_unboundedks, "java": _java_unboundedks, "cpp": _cpp_unboundedks,
                           "csharp": _csharp_unboundedks, "perl": _perl_unboundedks, "c": _c_unboundedks, "rust": _rust_unboundedks},
    "word-wrap": {"javascript": _js_wordwrap, "typescript": _ts_wordwrap, "java": _java_wordwrap, "cpp": _cpp_wordwrap,
                 "csharp": _csharp_wordwrap, "perl": _perl_wordwrap, "c": _c_wordwrap, "rust": _rust_wordwrap},
    "unique-permutations-count": {"javascript": _js_uniqueperm, "typescript": _ts_uniqueperm, "java": _java_uniqueperm, "cpp": _cpp_uniqueperm,
                                  "csharp": _csharp_uniqueperm, "perl": _perl_uniqueperm, "c": _c_uniqueperm, "rust": _rust_uniqueperm},
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
                    adapter_version=f"{lang}-function-mega6-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
