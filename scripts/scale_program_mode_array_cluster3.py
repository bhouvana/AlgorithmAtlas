"""Extends Program Mode to array-cluster3 (best-time-to-buy-sell-stock(-ii),
container-with-most-water, trapping-rain-water[js/ts/perl only -- genuine
int32 overflow for java/cpp/csharp/c/rust, see
docs/atlascode-bigint-numeric-audit.json], jump-game,
product-of-array-except-self, intersection-of-two-arrays,
longest-consecutive-sequence, find-duplicate-number, counting-bits) across
the 8 working languages -- reusing the exact core algorithms already
proven in Function Mode (scale_array_cluster3.py), wrapped in stdin/stdout
matching each problem's existing Python starter_code convention.
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
_TRAP_LANGUAGES = ["javascript", "typescript", "perl"]


@dataclass
class SimpleCase:
    id: str
    input_data: str
    expected_output: str
    is_hidden: bool
    order: int


# ── generic single-int-array -> single-int problems (bts1, bts2, container, trap, lcseq, find_dup) ──
def _js_int_array_to_int(body, wrong):
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        f"{body(wrong)}"
        f"console.log({_fn_name(body)}(nums));\n"
    )


def _fn_name(body):
    return _FN_NAMES[body]


# bts1/bts2/container/trap/lcseq/find_dup share signature (nums) -> int
def _js_bts1_p(wrong):
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const prices = data.slice(1,1+n);\n"
        "function max_profit(prices) {\n"
        "    let minP = prices[0], best = 0;\n"
        "    for (let i=1;i<prices.length;i++) { best = Math.max(best, prices[i]-minP); minP = Math.min(minP, prices[i]); }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "}\n"
        "console.log(max_profit(prices));\n"
    )


def _ts_bts1_p(wrong):
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const prices = data.slice(1,1+n);\n"
        "function max_profit(prices: number[]): number {\n"
        "    let minP = prices[0], best = 0;\n"
        "    for (let i=1;i<prices.length;i++) { best = Math.max(best, prices[i]-minP); minP = Math.min(minP, prices[i]); }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "}\n"
        "console.log(max_profit(prices));\n"
    )


def _java_bts1_p(wrong):
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] prices = new int[n]; for (int i=0;i<n;i++) prices[i]=sc.nextInt();\n"
        "    System.out.println(max_profit(prices));\n"
        "}\n"
        "static int max_profit(int[] prices) {\n"
        "    int minP = prices[0], best = 0;\n"
        "    for (int i=1;i<prices.length;i++) { best = Math.max(best, prices[i]-minP); minP = Math.min(minP, prices[i]); }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "} }\n"
    )


def _cpp_bts1_p(wrong):
    return (
        "#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n"
        "int max_profit(vector<int>& prices) {\n"
        "    int minP = prices[0], best = 0;\n"
        "    for (int i=1;i<(int)prices.size();i++) { best = max(best, prices[i]-minP); minP = min(minP, prices[i]); }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> prices(n); for (int i=0;i<n;i++) cin>>prices[i]; cout << max_profit(prices) << endl; return 0; }\n"
    )


def _csharp_bts1_p(wrong):
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] prices=new int[n]; for (int i=0;i<n;i++) prices[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(max_profit(prices));\n"
        "}\n"
        "static int max_profit(int[] prices) {\n"
        "    int minP = prices[0], best = 0;\n"
        "    for (int i=1;i<prices.Length;i++) { best = System.Math.Max(best, prices[i]-minP); minP = System.Math.Min(minP, prices[i]); }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "} }\n"
    )


def _perl_bts1_p(wrong):
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @prices = @data[0..$n-1];\n"
        "sub max_profit {\n"
        "    my ($prices) = @_;\n"
        "    my $minP = $prices->[0]; my $best = 0;\n"
        "    for (my $i=1;$i<scalar(@$prices);$i++) {\n"
        "        my $profit = $prices->[$i] - $minP;\n"
        "        $best = $profit if $profit > $best;\n"
        "        $minP = $prices->[$i] if $prices->[$i] < $minP;\n"
        "    }\n"
        f"    return $best{' + 1' if wrong else ''};\n"
        "}\n"
        "print max_profit(\\@prices), \"\\n\";\n"
    )


def _c_bts1_p(wrong):
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int max_profit(int* prices, int n) {\n"
        "    int minP = prices[0], best = 0;\n"
        "    for (int i=1;i<n;i++) {\n"
        "        int profit = prices[i] - minP;\n"
        "        if (profit > best) best = profit;\n"
        "        if (prices[i] < minP) minP = prices[i];\n"
        "    }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* prices=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&prices[i]); printf(\"%d\\n\", max_profit(prices,n)); return 0; }\n"
    )


def _rust_bts1_p(wrong):
    return (
        "use std::io::Read;\n"
        "fn max_profit(prices: &Vec<i32>) -> i32 {\n"
        "    let mut min_p = prices[0]; let mut best = 0;\n"
        "    for i in 1..prices.len() { best = best.max(prices[i]-min_p); min_p = min_p.min(prices[i]); }\n"
        f"    best{' + 1' if wrong else ''}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let prices: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    println!(\"{}\", max_profit(&prices)); }\n"
    )


def _js_bts2_p(wrong):
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const prices = data.slice(1,1+n);\n"
        "function max_profit(prices) {\n"
        "    let total = 0;\n"
        "    for (let i=1;i<prices.length;i++) { if (prices[i] > prices[i-1]) total += prices[i]-prices[i-1]; }\n"
        f"    return total{' + 1' if wrong else ''};\n"
        "}\n"
        "console.log(max_profit(prices));\n"
    )


def _ts_bts2_p(wrong):
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const prices = data.slice(1,1+n);\n"
        "function max_profit(prices: number[]): number {\n"
        "    let total = 0;\n"
        "    for (let i=1;i<prices.length;i++) { if (prices[i] > prices[i-1]) total += prices[i]-prices[i-1]; }\n"
        f"    return total{' + 1' if wrong else ''};\n"
        "}\n"
        "console.log(max_profit(prices));\n"
    )


def _java_bts2_p(wrong):
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] prices = new int[n]; for (int i=0;i<n;i++) prices[i]=sc.nextInt();\n"
        "    System.out.println(max_profit(prices));\n"
        "}\n"
        "static int max_profit(int[] prices) {\n"
        "    int total = 0;\n"
        "    for (int i=1;i<prices.length;i++) { if (prices[i] > prices[i-1]) total += prices[i]-prices[i-1]; }\n"
        f"    return total{' + 1' if wrong else ''};\n"
        "} }\n"
    )


def _cpp_bts2_p(wrong):
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n"
        "int max_profit(vector<int>& prices) {\n"
        "    int total = 0;\n"
        "    for (int i=1;i<(int)prices.size();i++) { if (prices[i] > prices[i-1]) total += prices[i]-prices[i-1]; }\n"
        f"    return total{' + 1' if wrong else ''};\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> prices(n); for (int i=0;i<n;i++) cin>>prices[i]; cout << max_profit(prices) << endl; return 0; }\n"
    )


def _csharp_bts2_p(wrong):
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] prices=new int[n]; for (int i=0;i<n;i++) prices[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(max_profit(prices));\n"
        "}\n"
        "static int max_profit(int[] prices) {\n"
        "    int total = 0;\n"
        "    for (int i=1;i<prices.Length;i++) { if (prices[i] > prices[i-1]) total += prices[i]-prices[i-1]; }\n"
        f"    return total{' + 1' if wrong else ''};\n"
        "} }\n"
    )


def _perl_bts2_p(wrong):
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @prices = @data[0..$n-1];\n"
        "sub max_profit {\n"
        "    my ($prices) = @_;\n"
        "    my $total = 0;\n"
        "    for (my $i=1;$i<scalar(@$prices);$i++) { if ($prices->[$i] > $prices->[$i-1]) { $total += $prices->[$i]-$prices->[$i-1]; } }\n"
        f"    return $total{' + 1' if wrong else ''};\n"
        "}\n"
        "print max_profit(\\@prices), \"\\n\";\n"
    )


def _c_bts2_p(wrong):
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int max_profit(int* prices, int n) {\n"
        "    int total = 0;\n"
        "    for (int i=1;i<n;i++) { if (prices[i] > prices[i-1]) total += prices[i]-prices[i-1]; }\n"
        f"    return total{' + 1' if wrong else ''};\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* prices=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&prices[i]); printf(\"%d\\n\", max_profit(prices,n)); return 0; }\n"
    )


def _rust_bts2_p(wrong):
    return (
        "use std::io::Read;\n"
        "fn max_profit(prices: &Vec<i32>) -> i32 {\n"
        "    let mut total = 0;\n"
        "    for i in 1..prices.len() { if prices[i] > prices[i-1] { total += prices[i]-prices[i-1]; } }\n"
        f"    total{' + 1' if wrong else ''}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let prices: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    println!(\"{}\", max_profit(&prices)); }\n"
    )


def _js_container_p(wrong):
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const heights = data.slice(1,1+n);\n"
        "function max_area(heights) {\n"
        "    let lo=0, hi=heights.length-1, best=0;\n"
        "    while (lo<hi) {\n"
        "        const area = Math.min(heights[lo],heights[hi]) * (hi-lo);\n"
        "        if (area > best) best = area;\n"
        "        if (heights[lo] < heights[hi]) lo++; else hi--;\n"
        "    }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "}\n"
        "console.log(max_area(heights));\n"
    )


def _ts_container_p(wrong):
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const heights = data.slice(1,1+n);\n"
        "function max_area(heights: number[]): number {\n"
        "    let lo=0, hi=heights.length-1, best=0;\n"
        "    while (lo<hi) {\n"
        "        const area = Math.min(heights[lo],heights[hi]) * (hi-lo);\n"
        "        if (area > best) best = area;\n"
        "        if (heights[lo] < heights[hi]) lo++; else hi--;\n"
        "    }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "}\n"
        "console.log(max_area(heights));\n"
    )


def _java_container_p(wrong):
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] heights = new int[n]; for (int i=0;i<n;i++) heights[i]=sc.nextInt();\n"
        "    System.out.println(max_area(heights));\n"
        "}\n"
        "static int max_area(int[] heights) {\n"
        "    int lo=0, hi=heights.length-1, best=0;\n"
        "    while (lo<hi) {\n"
        "        int area = Math.min(heights[lo],heights[hi]) * (hi-lo);\n"
        "        if (area > best) best = area;\n"
        "        if (heights[lo] < heights[hi]) lo++; else hi--;\n"
        "    }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "} }\n"
    )


def _cpp_container_p(wrong):
    return (
        "#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n"
        "int max_area(vector<int>& heights) {\n"
        "    int lo=0, hi=(int)heights.size()-1, best=0;\n"
        "    while (lo<hi) {\n"
        "        int area = min(heights[lo],heights[hi]) * (hi-lo);\n"
        "        if (area > best) best = area;\n"
        "        if (heights[lo] < heights[hi]) lo++; else hi--;\n"
        "    }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> heights(n); for (int i=0;i<n;i++) cin>>heights[i]; cout << max_area(heights) << endl; return 0; }\n"
    )


def _csharp_container_p(wrong):
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] heights=new int[n]; for (int i=0;i<n;i++) heights[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(max_area(heights));\n"
        "}\n"
        "static int max_area(int[] heights) {\n"
        "    int lo=0, hi=heights.Length-1, best=0;\n"
        "    while (lo<hi) {\n"
        "        int area = System.Math.Min(heights[lo],heights[hi]) * (hi-lo);\n"
        "        if (area > best) best = area;\n"
        "        if (heights[lo] < heights[hi]) lo++; else hi--;\n"
        "    }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "} }\n"
    )


def _perl_container_p(wrong):
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @heights = @data[0..$n-1];\n"
        "sub max_area {\n"
        "    my ($heights) = @_;\n"
        "    my $lo = 0; my $hi = scalar(@$heights) - 1; my $best = 0;\n"
        "    while ($lo < $hi) {\n"
        "        my $m = ($heights->[$lo] < $heights->[$hi]) ? $heights->[$lo] : $heights->[$hi];\n"
        "        my $area = $m * ($hi - $lo);\n"
        "        $best = $area if $area > $best;\n"
        "        if ($heights->[$lo] < $heights->[$hi]) { $lo++; } else { $hi--; }\n"
        "    }\n"
        f"    return $best{' + 1' if wrong else ''};\n"
        "}\n"
        "print max_area(\\@heights), \"\\n\";\n"
    )


def _c_container_p(wrong):
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int max_area(int* heights, int n) {\n"
        "    int lo=0, hi=n-1, best=0;\n"
        "    while (lo<hi) {\n"
        "        int m = heights[lo] < heights[hi] ? heights[lo] : heights[hi];\n"
        "        int area = m * (hi-lo);\n"
        "        if (area > best) best = area;\n"
        "        if (heights[lo] < heights[hi]) lo++; else hi--;\n"
        "    }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* heights=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&heights[i]); printf(\"%d\\n\", max_area(heights,n)); return 0; }\n"
    )


def _rust_container_p(wrong):
    return (
        "use std::io::Read;\n"
        "fn max_area(heights: &Vec<i32>) -> i32 {\n"
        "    let mut lo = 0usize; let mut hi = heights.len()-1; let mut best = 0;\n"
        "    while lo < hi {\n"
        "        let area = heights[lo].min(heights[hi]) * (hi-lo) as i32;\n"
        "        if area > best { best = area; }\n"
        "        if heights[lo] < heights[hi] { lo += 1; } else { hi -= 1; }\n"
        "    }\n"
        f"    best{' + 1' if wrong else ''}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let heights: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    println!(\"{}\", max_area(&heights)); }\n"
    )


# ── trapping-rain-water (js/ts/perl only) ───────────────────────────────────
def _js_trap_p(wrong):
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const heights = data.slice(1,1+n);\n"
        "function trap(heights) {\n"
        "    let lo=0, hi=heights.length-1, leftMax=0, rightMax=0, total=0;\n"
        "    while (lo<hi) {\n"
        "        if (heights[lo] < heights[hi]) { leftMax = Math.max(leftMax, heights[lo]); total += leftMax - heights[lo]; lo++; }\n"
        "        else { rightMax = Math.max(rightMax, heights[hi]); total += rightMax - heights[hi]; hi--; }\n"
        "    }\n"
        f"    return total{' + 1' if wrong else ''};\n"
        "}\n"
        "console.log(trap(heights));\n"
    )


def _ts_trap_p(wrong):
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const heights = data.slice(1,1+n);\n"
        "function trap(heights: number[]): number {\n"
        "    let lo=0, hi=heights.length-1, leftMax=0, rightMax=0, total=0;\n"
        "    while (lo<hi) {\n"
        "        if (heights[lo] < heights[hi]) { leftMax = Math.max(leftMax, heights[lo]); total += leftMax - heights[lo]; lo++; }\n"
        "        else { rightMax = Math.max(rightMax, heights[hi]); total += rightMax - heights[hi]; hi--; }\n"
        "    }\n"
        f"    return total{' + 1' if wrong else ''};\n"
        "}\n"
        "console.log(trap(heights));\n"
    )


def _perl_trap_p(wrong):
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @heights = @data[0..$n-1];\n"
        "sub trap {\n"
        "    my ($heights) = @_;\n"
        "    my $lo=0; my $hi=scalar(@$heights)-1; my $leftMax=0; my $rightMax=0; my $total=0;\n"
        "    while ($lo<$hi) {\n"
        "        if ($heights->[$lo] < $heights->[$hi]) {\n"
        "            $leftMax = $heights->[$lo] if $heights->[$lo] > $leftMax;\n"
        "            $total += $leftMax - $heights->[$lo]; $lo++;\n"
        "        } else {\n"
        "            $rightMax = $heights->[$hi] if $heights->[$hi] > $rightMax;\n"
        "            $total += $rightMax - $heights->[$hi]; $hi--;\n"
        "        }\n"
        "    }\n"
        f"    return $total{' + 1' if wrong else ''};\n"
        "}\n"
        "print trap(\\@heights), \"\\n\";\n"
    )


# ── jump-game ────────────────────────────────────────────────────────────────
def _js_jump_game_p(wrong):
    ret = "reach < nums.length - 1" if wrong else "reach >= nums.length - 1"
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function can_jump(nums) {\n"
        "    let reach = 0;\n"
        "    for (let i=0;i<nums.length;i++) { if (i > reach) break; reach = Math.max(reach, i + nums[i]); }\n"
        f"    return {ret};\n"
        "}\n"
        "console.log(can_jump(nums) ? 'true' : 'false');\n"
    )


def _ts_jump_game_p(wrong):
    ret = "reach < nums.length - 1" if wrong else "reach >= nums.length - 1"
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function can_jump(nums: number[]): boolean {\n"
        "    let reach = 0;\n"
        "    for (let i=0;i<nums.length;i++) { if (i > reach) break; reach = Math.max(reach, i + nums[i]); }\n"
        f"    return {ret};\n"
        "}\n"
        "console.log(can_jump(nums) ? 'true' : 'false');\n"
    )


def _java_jump_game_p(wrong):
    ret = "reach < nums.length - 1" if wrong else "reach >= nums.length - 1"
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] nums = new int[n]; for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "    System.out.println(can_jump(nums) ? \"true\" : \"false\");\n"
        "}\n"
        "static boolean can_jump(int[] nums) {\n"
        "    int reach = 0;\n"
        "    for (int i=0;i<nums.length;i++) { if (i > reach) break; reach = Math.max(reach, i + nums[i]); }\n"
        f"    return {ret};\n"
        "} }\n"
    )


def _cpp_jump_game_p(wrong):
    ret = "reach < (int)nums.size() - 1" if wrong else "reach >= (int)nums.size() - 1"
    return (
        "#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n"
        "bool can_jump(vector<int>& nums) {\n"
        "    int reach = 0;\n"
        "    for (int i=0;i<(int)nums.size();i++) { if (i > reach) break; reach = max(reach, i + nums[i]); }\n"
        f"    return {ret};\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> nums(n); for (int i=0;i<n;i++) cin>>nums[i]; cout << (can_jump(nums) ? \"true\" : \"false\") << endl; return 0; }\n"
    )


def _csharp_jump_game_p(wrong):
    ret = "reach < nums.Length - 1" if wrong else "reach >= nums.Length - 1"
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] nums=new int[n]; for (int i=0;i<n;i++) nums[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(can_jump(nums) ? \"true\" : \"false\");\n"
        "}\n"
        "static bool can_jump(int[] nums) {\n"
        "    int reach = 0;\n"
        "    for (int i=0;i<nums.Length;i++) { if (i > reach) break; reach = System.Math.Max(reach, i + nums[i]); }\n"
        f"    return {ret};\n"
        "} }\n"
    )


def _perl_jump_game_p(wrong):
    ret = "$reach < scalar(@nums) - 1" if wrong else "$reach >= scalar(@nums) - 1"
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @nums = @data[0..$n-1];\n"
        "my $reach = 0;\n"
        "for (my $i=0;$i<scalar(@nums);$i++) {\n"
        "    last if $i > $reach;\n"
        "    my $cand = $i + $nums[$i];\n"
        "    $reach = $cand if $cand > $reach;\n"
        "}\n"
        f"print (({ret}) ? \"true\\n\" : \"false\\n\");\n"
    )


def _c_jump_game_p(wrong):
    ret = "reach < n - 1" if wrong else "reach >= n - 1"
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int can_jump(int* nums, int n) {\n"
        "    int reach = 0;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        if (i > reach) break;\n"
        "        int cand = i + nums[i];\n"
        "        if (cand > reach) reach = cand;\n"
        "    }\n"
        f"    return {ret};\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* nums=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&nums[i]); printf(\"%s\\n\", can_jump(nums,n) ? \"true\" : \"false\"); return 0; }\n"
    )


def _rust_jump_game_p(wrong):
    ret = "(reach as i32) < nums.len() as i32 - 1" if wrong else "reach as i32 >= nums.len() as i32 - 1"
    return (
        "use std::io::Read;\n"
        "fn can_jump(nums: &Vec<i32>) -> bool {\n"
        "    let mut reach: i32 = 0;\n"
        "    for i in 0..nums.len() {\n"
        "        if i as i32 > reach { break; }\n"
        "        reach = reach.max(i as i32 + nums[i]);\n"
        "    }\n"
        f"    {ret}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    println!(\"{}\", if can_jump(&nums) { \"true\" } else { \"false\" }); }\n"
    )


# ── product-of-array-except-self ────────────────────────────────────────────
def _js_prod_except_p(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function product_except_self(nums) {\n"
        "    const nn = nums.length; const out = new Array(nn).fill(1);\n"
        "    let prefix = 1;\n"
        "    for (let i=0;i<nn;i++) { out[i] = prefix; prefix *= nums[i]; }\n"
        "    let suffix = 1;\n"
        "    for (let i=nn-1;i>=0;i--) { out[i] *= suffix; suffix *= nums[i]; }\n"
        f"    return out{a};\n"
        "}\n"
        "console.log(product_except_self(nums).join(' '));\n"
    )


def _ts_prod_except_p(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function product_except_self(nums: number[]): number[] {\n"
        "    const nn = nums.length; const out: number[] = new Array(nn).fill(1);\n"
        "    let prefix = 1;\n"
        "    for (let i=0;i<nn;i++) { out[i] = prefix; prefix *= nums[i]; }\n"
        "    let suffix = 1;\n"
        "    for (let i=nn-1;i>=0;i--) { out[i] *= suffix; suffix *= nums[i]; }\n"
        f"    return out{a};\n"
        "}\n"
        "console.log(product_except_self(nums).join(' '));\n"
    )


def _java_prod_except_p(wrong):
    incr = "for (int i=0;i<n;i++) out[i]++;\n        " if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] nums = new int[n]; for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "    int[] out = product_except_self(nums);\n"
        "    StringBuilder sb = new StringBuilder(); for (int i=0;i<n;i++) { if (i>0) sb.append(' '); sb.append(out[i]); }\n"
        "    System.out.println(sb.toString());\n"
        "}\n"
        "static int[] product_except_self(int[] nums) {\n"
        "    int n = nums.length; int[] out = new int[n];\n"
        "    int prefix = 1;\n"
        "    for (int i=0;i<n;i++) { out[i] = prefix; prefix *= nums[i]; }\n"
        "    int suffix = 1;\n"
        "    for (int i=n-1;i>=0;i--) { out[i] *= suffix; suffix *= nums[i]; }\n"
        f"        {incr}return out;\n"
        "} }\n"
    )


def _cpp_prod_except_p(wrong):
    incr = "for (int i=0;i<n;i++) out[i]++;\n    " if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n"
        "vector<int> product_except_self(vector<int>& nums) {\n"
        "    int n = nums.size(); vector<int> out(n, 1);\n"
        "    int prefix = 1;\n"
        "    for (int i=0;i<n;i++) { out[i] = prefix; prefix *= nums[i]; }\n"
        "    int suffix = 1;\n"
        "    for (int i=n-1;i>=0;i--) { out[i] *= suffix; suffix *= nums[i]; }\n"
        f"    {incr}return out;\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> nums(n); for (int i=0;i<n;i++) cin>>nums[i];\n"
        "    vector<int> out = product_except_self(nums);\n"
        "    for (int i=0;i<n;i++) { if (i) cout<<' '; cout<<out[i]; }\n"
        "    cout << endl; return 0;\n"
        "}\n"
    )


def _csharp_prod_except_p(wrong):
    incr = "for (int i=0;i<n;i++) outArr[i]++;\n        " if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] nums=new int[n]; for (int i=0;i<n;i++) nums[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(string.Join(\" \", product_except_self(nums)));\n"
        "}\n"
        "static int[] product_except_self(int[] nums) {\n"
        "    int n = nums.Length; int[] outArr = new int[n];\n"
        "    int prefix = 1;\n"
        "    for (int i=0;i<n;i++) { outArr[i] = prefix; prefix *= nums[i]; }\n"
        "    int suffix = 1;\n"
        "    for (int i=n-1;i>=0;i--) { outArr[i] *= suffix; suffix *= nums[i]; }\n"
        f"        {incr}return outArr;\n"
        "} }\n"
    )


def _perl_prod_except_p(wrong):
    incr = "for (my $i=0;$i<$nn;$i++) { $out[$i]++; }\n    " if wrong else ""
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @nums = @data[0..$n-1];\n"
        "sub product_except_self {\n"
        "    my ($nums) = @_;\n"
        "    my $nn = scalar(@$nums); my @out = (1) x $nn;\n"
        "    my $prefix = 1;\n"
        "    for (my $i=0;$i<$nn;$i++) { $out[$i] = $prefix; $prefix *= $nums->[$i]; }\n"
        "    my $suffix = 1;\n"
        "    for (my $i=$nn-1;$i>=0;$i--) { $out[$i] *= $suffix; $suffix *= $nums->[$i]; }\n"
        f"    {incr}return \\@out;\n"
        "}\n"
        "print join(' ', @{product_except_self(\\@nums)}), \"\\n\";\n"
    )


def _c_prod_except_p(wrong):
    incr = "for (int i=0;i<n;i++) out[i]++;\n    " if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int* product_except_self(int* nums, int n) {\n"
        "    int* out = (int*)malloc(sizeof(int)*(n>0?n:1));\n"
        "    for (int i=0;i<n;i++) out[i]=1;\n"
        "    int prefix = 1;\n"
        "    for (int i=0;i<n;i++) { out[i] = prefix; prefix *= nums[i]; }\n"
        "    int suffix = 1;\n"
        "    for (int i=n-1;i>=0;i--) { out[i] *= suffix; suffix *= nums[i]; }\n"
        f"    {incr}return out;\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* nums=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&nums[i]);\n"
        "    int* out = product_except_self(nums, n);\n"
        "    for (int i=0;i<n;i++) { if (i) printf(\" \"); printf(\"%d\", out[i]); }\n"
        "    printf(\"\\n\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_prod_except_p(wrong):
    incr = "for i in 0..n { out[i] += 1; }\n    " if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn product_except_self(nums: &Vec<i32>) -> Vec<i32> {\n"
        "    let n = nums.len(); let mut out = vec![1i32; n];\n"
        "    let mut prefix = 1;\n"
        "    for i in 0..n { out[i] = prefix; prefix *= nums[i]; }\n"
        "    let mut suffix = 1;\n"
        "    for i in (0..n).rev() { out[i] *= suffix; suffix *= nums[i]; }\n"
        f"    {incr}out\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    let out = product_except_self(&nums);\n"
        "    let strs: Vec<String> = out.iter().map(|x| x.to_string()).collect();\n"
        "    println!(\"{}\", strs.join(\" \")); }\n"
    )


# ── intersection-of-two-arrays (sorted unique intersection) ─────────────────
def _js_intersection_p(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "let idx=0; const n1=data[idx++]; const nums1=data.slice(idx,idx+n1); idx+=n1;\n"
        "const n2=data[idx++]; const nums2=data.slice(idx,idx+n2);\n"
        "function intersection(nums1, nums2) {\n"
        "    const s1 = new Set(nums1), s2 = new Set(nums2);\n"
        "    const out = [...s1].filter(x => s2.has(x)).sort((a,b)=>a-b);\n"
        f"    return out{a};\n"
        "}\n"
        "console.log(intersection(nums1, nums2).join(' '));\n"
    )


def _ts_intersection_p(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "let idx=0; const n1=data[idx++]; const nums1=data.slice(idx,idx+n1); idx+=n1;\n"
        "const n2=data[idx++]; const nums2=data.slice(idx,idx+n2);\n"
        "function intersection(nums1: number[], nums2: number[]): number[] {\n"
        "    const s1 = new Set(nums1), s2 = new Set(nums2);\n"
        "    const out = [...s1].filter(x => s2.has(x)).sort((a,b)=>a-b);\n"
        f"    return out{a};\n"
        "}\n"
        "console.log(intersection(nums1, nums2).join(' '));\n"
    )


def _java_intersection_p(wrong):
    incr = "for (int i=0;i<out.length;i++) out[i]++;\n        " if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n1 = sc.nextInt(); int[] nums1 = new int[n1]; for (int i=0;i<n1;i++) nums1[i]=sc.nextInt();\n"
        "    int n2 = sc.nextInt(); int[] nums2 = new int[n2]; for (int i=0;i<n2;i++) nums2[i]=sc.nextInt();\n"
        "    int[] out = intersection(nums1, nums2);\n"
        "    StringBuilder sb = new StringBuilder(); for (int i=0;i<out.length;i++) { if (i>0) sb.append(' '); sb.append(out[i]); }\n"
        "    System.out.println(sb.toString());\n"
        "}\n"
        "static int[] intersection(int[] nums1, int[] nums2) {\n"
        "    java.util.Set<Integer> s1 = new java.util.HashSet<>(); for (int x: nums1) s1.add(x);\n"
        "    java.util.Set<Integer> s2 = new java.util.HashSet<>(); for (int x: nums2) s2.add(x);\n"
        "    s1.retainAll(s2);\n"
        "    int[] out = s1.stream().mapToInt(Integer::intValue).sorted().toArray();\n"
        f"        {incr}return out;\n"
        "} }\n"
    )


def _cpp_intersection_p(wrong):
    incr = "for (auto& x : out) x++;\n    " if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\n#include <set>\n#include <algorithm>\nusing namespace std;\n"
        "vector<int> intersection(vector<int>& nums1, vector<int>& nums2) {\n"
        "    set<int> s1(nums1.begin(), nums1.end()), s2(nums2.begin(), nums2.end());\n"
        "    vector<int> out;\n"
        "    for (int x : s1) if (s2.count(x)) out.push_back(x);\n"
        "    sort(out.begin(), out.end());\n"
        f"    {incr}return out;\n"
        "}\n"
        "int main() { int n1; cin>>n1; vector<int> nums1(n1); for (int i=0;i<n1;i++) cin>>nums1[i];\n"
        "    int n2; cin>>n2; vector<int> nums2(n2); for (int i=0;i<n2;i++) cin>>nums2[i];\n"
        "    vector<int> out = intersection(nums1, nums2);\n"
        "    for (size_t i=0;i<out.size();i++) { if (i) cout<<' '; cout<<out[i]; }\n"
        "    cout << endl; return 0;\n"
        "}\n"
    )


def _csharp_intersection_p(wrong):
    incr = "for (int i=0;i<outArr.Length;i++) outArr[i]++;\n        " if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n1=int.Parse(t[idx++]); int[] nums1=new int[n1]; for (int i=0;i<n1;i++) nums1[i]=int.Parse(t[idx++]);\n"
        "    int n2=int.Parse(t[idx++]); int[] nums2=new int[n2]; for (int i=0;i<n2;i++) nums2[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(string.Join(\" \", intersection(nums1, nums2)));\n"
        "}\n"
        "static int[] intersection(int[] nums1, int[] nums2) {\n"
        "    var s1 = new System.Collections.Generic.HashSet<int>(nums1);\n"
        "    var s2 = new System.Collections.Generic.HashSet<int>(nums2);\n"
        "    s1.IntersectWith(s2);\n"
        "    var outArr = new System.Collections.Generic.List<int>(s1); outArr.Sort();\n"
        f"        {incr}return outArr.ToArray();\n"
        "} }\n"
    )


def _perl_intersection_p(wrong):
    incr = "@out = map { $_ + 1 } @out;\n    " if wrong else ""
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $idx = 0; my $n1 = $data[$idx++]; my @nums1 = @data[$idx..$idx+$n1-1]; $idx+=$n1;\n"
        "my $n2 = $data[$idx++]; my @nums2 = @data[$idx..$idx+$n2-1];\n"
        "sub intersection {\n"
        "    my ($nums1, $nums2) = @_;\n"
        "    my %s1 = map { $_ => 1 } @$nums1;\n"
        "    my %s2 = map { $_ => 1 } @$nums2;\n"
        "    my @out = sort { $a <=> $b } grep { exists $s2{$_} } keys %s1;\n"
        f"    {incr}return \\@out;\n"
        "}\n"
        "print join(' ', @{intersection(\\@nums1, \\@nums2)}), \"\\n\";\n"
    )


def _c_intersection_p(wrong):
    incr = "for (int i=0;i<oc;i++) out[i]++;\n    " if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int cmpint(const void* a, const void* b) { return *(const int*)a - *(const int*)b; }\n"
        "int* intersection(int* nums1, int n1, int* nums2, int n2, int* out_size) {\n"
        "    int* out = (int*)malloc(sizeof(int) * (n1 > 0 ? n1 : 1));\n"
        "    int oc = 0;\n"
        "    for (int i=0;i<n1;i++) {\n"
        "        int v = nums1[i]; int dup = 0;\n"
        "        for (int k=0;k<oc;k++) if (out[k]==v) { dup=1; break; }\n"
        "        if (dup) continue;\n"
        "        int found = 0;\n"
        "        for (int j=0;j<n2;j++) if (nums2[j]==v) { found=1; break; }\n"
        "        if (found) out[oc++] = v;\n"
        "    }\n"
        "    qsort(out, oc, sizeof(int), cmpint);\n"
        f"    {incr}*out_size = oc;\n"
        "    return out;\n"
        "}\n"
        "int main() { int n1; scanf(\"%d\",&n1); int* nums1=(int*)malloc(sizeof(int)*(n1>0?n1:1)); for (int i=0;i<n1;i++) scanf(\"%d\",&nums1[i]);\n"
        "    int n2; scanf(\"%d\",&n2); int* nums2=(int*)malloc(sizeof(int)*(n2>0?n2:1)); for (int i=0;i<n2;i++) scanf(\"%d\",&nums2[i]);\n"
        "    int oc; int* out = intersection(nums1, n1, nums2, n2, &oc);\n"
        "    for (int i=0;i<oc;i++) { if (i) printf(\" \"); printf(\"%d\", out[i]); }\n"
        "    printf(\"\\n\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_intersection_p(wrong):
    incr = "for x in out.iter_mut() { *x += 1; }\n    " if wrong else ""
    return (
        "use std::io::Read;\n"
        "use std::collections::HashSet;\n"
        "fn intersection(nums1: &Vec<i32>, nums2: &Vec<i32>) -> Vec<i32> {\n"
        "    let s1: HashSet<i32> = nums1.iter().cloned().collect();\n"
        "    let s2: HashSet<i32> = nums2.iter().cloned().collect();\n"
        "    let mut out: Vec<i32> = s1.intersection(&s2).cloned().collect();\n"
        "    out.sort();\n"
        f"    {incr}out\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n1 = it.next().unwrap() as usize; let nums1: Vec<i32> = (0..n1).map(|_| it.next().unwrap()).collect();\n"
        "    let n2 = it.next().unwrap() as usize; let nums2: Vec<i32> = (0..n2).map(|_| it.next().unwrap()).collect();\n"
        "    let out = intersection(&nums1, &nums2);\n"
        "    let strs: Vec<String> = out.iter().map(|x| x.to_string()).collect();\n"
        "    println!(\"{}\", strs.join(\" \")); }\n"
    )


# ── longest-consecutive-sequence ────────────────────────────────────────────
def _js_lcseq_p(wrong):
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function longest_consecutive(nums) {\n"
        "    const s = new Set(nums); let best = 0;\n"
        "    for (const x of s) {\n"
        "        if (!s.has(x-1)) { let len=1; let cur=x; while (s.has(cur+1)) { cur++; len++; } best = Math.max(best, len); }\n"
        "    }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "}\n"
        "console.log(longest_consecutive(nums));\n"
    )


def _ts_lcseq_p(wrong):
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function longest_consecutive(nums: number[]): number {\n"
        "    const s = new Set(nums); let best = 0;\n"
        "    for (const x of s) {\n"
        "        if (!s.has(x-1)) { let len=1; let cur=x; while (s.has(cur+1)) { cur++; len++; } best = Math.max(best, len); }\n"
        "    }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "}\n"
        "console.log(longest_consecutive(nums));\n"
    )


def _java_lcseq_p(wrong):
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] nums = new int[n]; for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "    System.out.println(longest_consecutive(nums));\n"
        "}\n"
        "static int longest_consecutive(int[] nums) {\n"
        "    java.util.Set<Integer> s = new java.util.HashSet<>(); for (int x: nums) s.add(x);\n"
        "    int best = 0;\n"
        "    for (int x : s) {\n"
        "        if (!s.contains(x-1)) { int len=1; int cur=x; while (s.contains(cur+1)) { cur++; len++; } best = Math.max(best, len); }\n"
        "    }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "} }\n"
    )


def _cpp_lcseq_p(wrong):
    return (
        "#include <iostream>\n#include <vector>\n#include <unordered_set>\n#include <algorithm>\nusing namespace std;\n"
        "int longest_consecutive(vector<int>& nums) {\n"
        "    unordered_set<int> s(nums.begin(), nums.end()); int best = 0;\n"
        "    for (int x : s) {\n"
        "        if (!s.count(x-1)) { int len=1, cur=x; while (s.count(cur+1)) { cur++; len++; } best = max(best, len); }\n"
        "    }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> nums(n); for (int i=0;i<n;i++) cin>>nums[i]; cout << longest_consecutive(nums) << endl; return 0; }\n"
    )


def _csharp_lcseq_p(wrong):
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] nums=new int[n]; for (int i=0;i<n;i++) nums[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(longest_consecutive(nums));\n"
        "}\n"
        "static int longest_consecutive(int[] nums) {\n"
        "    var s = new System.Collections.Generic.HashSet<int>(nums); int best = 0;\n"
        "    foreach (int x in s) {\n"
        "        if (!s.Contains(x-1)) { int len=1, cur=x; while (s.Contains(cur+1)) { cur++; len++; } best = System.Math.Max(best, len); }\n"
        "    }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "} }\n"
    )


def _perl_lcseq_p(wrong):
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @nums = @data[0..$n-1];\n"
        "sub longest_consecutive {\n"
        "    my ($nums) = @_;\n"
        "    my %s = map { $_ => 1 } @$nums;\n"
        "    my $best = 0;\n"
        "    foreach my $x (keys %s) {\n"
        "        if (!exists $s{$x-1}) {\n"
        "            my $len = 1; my $cur = $x;\n"
        "            while (exists $s{$cur+1}) { $cur++; $len++; }\n"
        "            $best = $len if $len > $best;\n"
        "        }\n"
        "    }\n"
        f"    return $best{' + 1' if wrong else ''};\n"
        "}\n"
        "print longest_consecutive(\\@nums), \"\\n\";\n"
    )


def _c_lcseq_p(wrong):
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int longest_consecutive(int* nums, int n) {\n"
        "    int best = 0;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        int x = nums[i];\n"
        "        int hasPrev = 0;\n"
        "        for (int j=0;j<n;j++) if (nums[j] == x-1) { hasPrev=1; break; }\n"
        "        if (hasPrev) continue;\n"
        "        int len = 1; int cur = x; int found = 1;\n"
        "        while (found) {\n"
        "            found = 0;\n"
        "            for (int j=0;j<n;j++) if (nums[j] == cur+1) { found=1; break; }\n"
        "            if (found) { cur++; len++; }\n"
        "        }\n"
        "        if (len > best) best = len;\n"
        "    }\n"
        f"    return best{' + 1' if wrong else ''};\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* nums=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&nums[i]); printf(\"%d\\n\", longest_consecutive(nums,n)); return 0; }\n"
    )


def _rust_lcseq_p(wrong):
    return (
        "use std::io::Read;\n"
        "use std::collections::HashSet;\n"
        "fn longest_consecutive(nums: &Vec<i32>) -> i32 {\n"
        "    let s: HashSet<i32> = nums.iter().cloned().collect();\n"
        "    let mut best = 0;\n"
        "    for &x in s.iter() {\n"
        "        if !s.contains(&(x-1)) {\n"
        "            let mut len = 1; let mut cur = x;\n"
        "            while s.contains(&(cur+1)) { cur += 1; len += 1; }\n"
        "            best = best.max(len);\n"
        "        }\n"
        "    }\n"
        f"    best{' + 1' if wrong else ''}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    println!(\"{}\", longest_consecutive(&nums)); }\n"
    )


# ── find-duplicate-number ────────────────────────────────────────────────────
def _js_find_dup_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function find_duplicate(nums) {\n"
        "    const seen = new Set();\n"
        "    for (const x of nums) { if (seen.has(x)) return x" + a + "; seen.add(x); }\n"
        "    return -1;\n"
        "}\n"
        "console.log(find_duplicate(nums));\n"
    )


def _ts_find_dup_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function find_duplicate(nums: number[]): number {\n"
        "    const seen = new Set<number>();\n"
        "    for (const x of nums) { if (seen.has(x)) return x" + a + "; seen.add(x); }\n"
        "    return -1;\n"
        "}\n"
        "console.log(find_duplicate(nums));\n"
    )


def _java_find_dup_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] nums = new int[n]; for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "    System.out.println(find_duplicate(nums));\n"
        "}\n"
        "static int find_duplicate(int[] nums) {\n"
        "    java.util.Set<Integer> seen = new java.util.HashSet<>();\n"
        "    for (int x : nums) { if (seen.contains(x)) return x" + a + "; seen.add(x); }\n"
        "    return -1;\n"
        "} }\n"
    )


def _cpp_find_dup_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\n#include <unordered_set>\nusing namespace std;\n"
        "int find_duplicate(vector<int>& nums) {\n"
        "    unordered_set<int> seen;\n"
        "    for (int x : nums) { if (seen.count(x)) return x" + a + "; seen.insert(x); }\n"
        "    return -1;\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> nums(n); for (int i=0;i<n;i++) cin>>nums[i]; cout << find_duplicate(nums) << endl; return 0; }\n"
    )


def _csharp_find_dup_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] nums=new int[n]; for (int i=0;i<n;i++) nums[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(find_duplicate(nums));\n"
        "}\n"
        "static int find_duplicate(int[] nums) {\n"
        "    var seen = new System.Collections.Generic.HashSet<int>();\n"
        "    foreach (int x in nums) { if (seen.Contains(x)) return x" + a + "; seen.Add(x); }\n"
        "    return -1;\n"
        "} }\n"
    )


def _perl_find_dup_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @nums = @data[0..$n-1];\n"
        "sub find_duplicate {\n"
        "    my ($nums) = @_;\n"
        "    my %seen;\n"
        "    foreach my $x (@$nums) { return ($x" + a + ") if exists $seen{$x}; $seen{$x} = 1; }\n"
        "    return -1;\n"
        "}\n"
        "print find_duplicate(\\@nums), \"\\n\";\n"
    )


def _c_find_dup_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int find_duplicate(int* nums, int n) {\n"
        "    for (int i=0;i<n;i++) {\n"
        "        for (int j=0;j<i;j++) if (nums[j] == nums[i]) return nums[i]" + a + ";\n"
        "    }\n"
        "    return -1;\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* nums=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&nums[i]); printf(\"%d\\n\", find_duplicate(nums,n)); return 0; }\n"
    )


def _rust_find_dup_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "use std::collections::HashSet;\n"
        "fn find_duplicate(nums: &Vec<i32>) -> i32 {\n"
        "    let mut seen: HashSet<i32> = HashSet::new();\n"
        "    for x in nums.iter() { if seen.contains(x) { return (*x)" + a + "; } seen.insert(*x); }\n"
        "    -1\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    println!(\"{}\", find_duplicate(&nums)); }\n"
    )


# ── counting-bits ────────────────────────────────────────────────────────────
def _js_countbits_p(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "const n = parseInt(require('fs').readFileSync(0,'utf8').trim());\n"
        "function count_bits(n) {\n"
        "    const out = new Array(n+1).fill(0);\n"
        "    for (let i=1;i<=n;i++) out[i] = out[i >> 1] + (i & 1);\n"
        f"    return out{a};\n"
        "}\n"
        "console.log(count_bits(n).join(' '));\n"
    )


def _ts_countbits_p(wrong):
    a = ".map(x => x + 1)" if wrong else ""
    return (
        "const n: number = parseInt(require('fs').readFileSync(0,'utf8').trim());\n"
        "function count_bits(n: number): number[] {\n"
        "    const out: number[] = new Array(n+1).fill(0);\n"
        "    for (let i=1;i<=n;i++) out[i] = out[i >> 1] + (i & 1);\n"
        f"    return out{a};\n"
        "}\n"
        "console.log(count_bits(n).join(' '));\n"
    )


def _java_countbits_p(wrong):
    incr = "for (int i=0;i<=n;i++) out[i]++;\n        " if wrong else ""
    return (
        "public class Main { public static void main(String[] args) {\n"
        "    int n = Integer.parseInt(new java.util.Scanner(System.in).nextLine().trim());\n"
        "    int[] out = count_bits(n);\n"
        "    StringBuilder sb = new StringBuilder(); for (int i=0;i<=n;i++) { if (i>0) sb.append(' '); sb.append(out[i]); }\n"
        "    System.out.println(sb.toString());\n"
        "}\n"
        "static int[] count_bits(int n) {\n"
        "    int[] out = new int[n+1];\n"
        "    for (int i=1;i<=n;i++) out[i] = out[i>>1] + (i&1);\n"
        f"        {incr}return out;\n"
        "} }\n"
    )


def _cpp_countbits_p(wrong):
    incr = "for (int i=0;i<=n;i++) out[i]++;\n    " if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n"
        "vector<int> count_bits(int n) {\n"
        "    vector<int> out(n+1, 0);\n"
        "    for (int i=1;i<=n;i++) out[i] = out[i>>1] + (i&1);\n"
        f"    {incr}return out;\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> out = count_bits(n);\n"
        "    for (int i=0;i<=n;i++) { if (i) cout<<' '; cout<<out[i]; }\n"
        "    cout << endl; return 0;\n"
        "}\n"
    )


def _csharp_countbits_p(wrong):
    incr = "for (int i=0;i<=n;i++) outArr[i]++;\n        " if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    int n = int.Parse(System.Console.In.ReadToEnd().Trim());\n"
        "    System.Console.WriteLine(string.Join(\" \", count_bits(n)));\n"
        "}\n"
        "static int[] count_bits(int n) {\n"
        "    int[] outArr = new int[n+1];\n"
        "    for (int i=1;i<=n;i++) outArr[i] = outArr[i>>1] + (i&1);\n"
        f"        {incr}return outArr;\n"
        "} }\n"
    )


def _perl_countbits_p(wrong):
    incr = "for (my $i=0;$i<=$n;$i++) { $out[$i]++; }\n    " if wrong else ""
    return (
        "my $n = <STDIN>; chomp $n; $n = $n + 0;\n"
        "sub count_bits {\n"
        "    my ($n) = @_;\n"
        "    my @out = (0) x ($n+1);\n"
        "    for (my $i=1;$i<=$n;$i++) { $out[$i] = $out[$i >> 1] + ($i & 1); }\n"
        f"    {incr}return \\@out;\n"
        "}\n"
        "print join(' ', @{count_bits($n)}), \"\\n\";\n"
    )


def _c_countbits_p(wrong):
    incr = "for (int i=0;i<=n;i++) data[i]++;\n    " if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int* count_bits(int n) {\n"
        "    int* data = (int*)calloc(n+1, sizeof(int));\n"
        "    for (int i=1;i<=n;i++) data[i] = data[i>>1] + (i&1);\n"
        f"    {incr}return data;\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* out = count_bits(n);\n"
        "    for (int i=0;i<=n;i++) { if (i) printf(\" \"); printf(\"%d\", out[i]); }\n"
        "    printf(\"\\n\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_countbits_p(wrong):
    incr = "for i in 0..=n as usize { out[i] += 1; }\n    " if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn count_bits(n: i32) -> Vec<i32> {\n"
        "    let mut out = vec![0i32; (n+1) as usize];\n"
        "    for i in 1..=n as usize { out[i] = out[i>>1] + (i as i32 & 1); }\n"
        f"    {incr}out\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let n: i32 = s.trim().parse().unwrap();\n"
        "    let out = count_bits(n);\n"
        "    let strs: Vec<String> = out.iter().map(|x| x.to_string()).collect();\n"
        "    println!(\"{}\", strs.join(\" \")); }\n"
    )


_BUILDERS = {
    "best-time-to-buy-sell-stock": {"javascript": _js_bts1_p, "typescript": _ts_bts1_p, "java": _java_bts1_p, "cpp": _cpp_bts1_p,
                                    "csharp": _csharp_bts1_p, "perl": _perl_bts1_p, "c": _c_bts1_p, "rust": _rust_bts1_p},
    "best-time-to-buy-sell-stock-ii": {"javascript": _js_bts2_p, "typescript": _ts_bts2_p, "java": _java_bts2_p, "cpp": _cpp_bts2_p,
                                       "csharp": _csharp_bts2_p, "perl": _perl_bts2_p, "c": _c_bts2_p, "rust": _rust_bts2_p},
    "container-with-most-water": {"javascript": _js_container_p, "typescript": _ts_container_p, "java": _java_container_p, "cpp": _cpp_container_p,
                                  "csharp": _csharp_container_p, "perl": _perl_container_p, "c": _c_container_p, "rust": _rust_container_p},
    "trapping-rain-water": {"javascript": _js_trap_p, "typescript": _ts_trap_p, "perl": _perl_trap_p},
    "jump-game": {"javascript": _js_jump_game_p, "typescript": _ts_jump_game_p, "java": _java_jump_game_p, "cpp": _cpp_jump_game_p,
                 "csharp": _csharp_jump_game_p, "perl": _perl_jump_game_p, "c": _c_jump_game_p, "rust": _rust_jump_game_p},
    "product-of-array-except-self": {"javascript": _js_prod_except_p, "typescript": _ts_prod_except_p, "java": _java_prod_except_p, "cpp": _cpp_prod_except_p,
                                     "csharp": _csharp_prod_except_p, "perl": _perl_prod_except_p, "c": _c_prod_except_p, "rust": _rust_prod_except_p},
    "intersection-of-two-arrays": {"javascript": _js_intersection_p, "typescript": _ts_intersection_p, "java": _java_intersection_p, "cpp": _cpp_intersection_p,
                                   "csharp": _csharp_intersection_p, "perl": _perl_intersection_p, "c": _c_intersection_p, "rust": _rust_intersection_p},
    "longest-consecutive-sequence": {"javascript": _js_lcseq_p, "typescript": _ts_lcseq_p, "java": _java_lcseq_p, "cpp": _cpp_lcseq_p,
                                     "csharp": _csharp_lcseq_p, "perl": _perl_lcseq_p, "c": _c_lcseq_p, "rust": _rust_lcseq_p},
    "find-duplicate-number": {"javascript": _js_find_dup_p, "typescript": _ts_find_dup_p, "java": _java_find_dup_p, "cpp": _cpp_find_dup_p,
                              "csharp": _csharp_find_dup_p, "perl": _perl_find_dup_p, "c": _c_find_dup_p, "rust": _rust_find_dup_p},
    "counting-bits": {"javascript": _js_countbits_p, "typescript": _ts_countbits_p, "java": _java_countbits_p, "cpp": _cpp_countbits_p,
                      "csharp": _csharp_countbits_p, "perl": _perl_countbits_p, "c": _c_countbits_p, "rust": _rust_countbits_p},
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
            print(f"[{status}] {lang:10s}(program) {pid:30s} {r['outcome']:18s} {r['detail'][:120]}", flush=True)
            if r["outcome"] == "verified":
                row = con.execute("SELECT starter_code FROM problems WHERE id=?", (pid,)).fetchone()
                sc = json.loads(row["starter_code"])
                sc[lang] = builders[lang](False)
                con.execute("UPDATE problems SET starter_code=? WHERE id=?", (json.dumps(sc), pid))
                con.commit()
                ledger.record_cell(con, problem_id=pid, language=lang, mode="program",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=f"{lang}-program-array-cluster3-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
