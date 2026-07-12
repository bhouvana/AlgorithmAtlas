"""Extends Program Mode to the greedy-math cluster (activity-selection,
closest-pair, collatz, counting-inversions, egg-drop, euler-totient,
gas-station, insert-interval, first-occurrence, house-robber-circular)
across the 8 working languages -- reusing the exact core algorithms
already proven in Function Mode (scale_greedy_math_cluster.py), wrapped in
stdin/stdout matching each problem's existing Python starter_code
convention.
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


# ── activity-selection ──────────────────────────────────────────────────────
def _js_activity_p(wrong):
    ret = "count - 1" if wrong else "count"
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "let idx=0; const n=data[idx++]; const starts=data.slice(idx,idx+n); idx+=n; const ends=data.slice(idx,idx+n);\n"
        "function max_activities(starts, ends) {\n"
        "    const nn = starts.length;\n"
        "    const order = Array.from({length:nn}, (_,i)=>i).sort((a,b)=>ends[a]-ends[b]);\n"
        "    let count = 0, lastEnd = -Infinity;\n"
        "    for (const i of order) { if (starts[i] >= lastEnd) { count++; lastEnd = ends[i]; } }\n"
        f"    return {ret};\n"
        "}\n"
        "console.log(max_activities(starts, ends));\n"
    )


def _ts_activity_p(wrong):
    ret = "count - 1" if wrong else "count"
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "let idx=0; const n=data[idx++]; const starts=data.slice(idx,idx+n); idx+=n; const ends=data.slice(idx,idx+n);\n"
        "function max_activities(starts: number[], ends: number[]): number {\n"
        "    const nn = starts.length;\n"
        "    const order = Array.from({length:nn}, (_,i)=>i).sort((a,b)=>ends[a]-ends[b]);\n"
        "    let count = 0, lastEnd = -Infinity;\n"
        "    for (const i of order) { if (starts[i] >= lastEnd) { count++; lastEnd = ends[i]; } }\n"
        f"    return {ret};\n"
        "}\n"
        "console.log(max_activities(starts, ends));\n"
    )


def _java_activity_p(wrong):
    ret = "count - 1" if wrong else "count"
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] starts = new int[n]; for (int i=0;i<n;i++) starts[i]=sc.nextInt();\n"
        "    int[] ends = new int[n]; for (int i=0;i<n;i++) ends[i]=sc.nextInt();\n"
        "    System.out.println(max_activities(starts, ends));\n"
        "}\n"
        "static int max_activities(int[] starts, int[] ends) {\n"
        "    int n = starts.length;\n"
        "    Integer[] idx = new Integer[n]; for (int i=0;i<n;i++) idx[i]=i;\n"
        "    java.util.Arrays.sort(idx, (a,b) -> ends[a]-ends[b]);\n"
        "    int count = 0; long lastEnd = Long.MIN_VALUE;\n"
        "    for (int i : idx) { if (starts[i] >= lastEnd) { count++; lastEnd = ends[i]; } }\n"
        f"    return {ret};\n"
        "} }\n"
    )


def _cpp_activity_p(wrong):
    ret = "count - 1" if wrong else "count"
    return (
        "#include <iostream>\n#include <vector>\n#include <algorithm>\n#include <climits>\nusing namespace std;\n"
        "int max_activities(vector<int>& starts, vector<int>& ends) {\n"
        "    int n = starts.size();\n"
        "    vector<int> idx(n); for (int i=0;i<n;i++) idx[i]=i;\n"
        "    sort(idx.begin(), idx.end(), [&](int a, int b){ return ends[a] < ends[b]; });\n"
        "    int count = 0; long long lastEnd = LLONG_MIN;\n"
        "    for (int i : idx) { if (starts[i] >= lastEnd) { count++; lastEnd = ends[i]; } }\n"
        f"    return {ret};\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> starts(n); for (int i=0;i<n;i++) cin>>starts[i];\n"
        "    vector<int> ends(n); for (int i=0;i<n;i++) cin>>ends[i];\n"
        "    cout << max_activities(starts, ends) << endl; return 0;\n"
        "}\n"
    )


def _csharp_activity_p(wrong):
    ret = "count - 1" if wrong else "count"
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] starts=new int[n]; for (int i=0;i<n;i++) starts[i]=int.Parse(t[idx++]);\n"
        "    int[] ends=new int[n]; for (int i=0;i<n;i++) ends[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(max_activities(starts, ends));\n"
        "}\n"
        "static int max_activities(int[] starts, int[] ends) {\n"
        "    int n = starts.Length;\n"
        "    int[] order = new int[n]; for (int i=0;i<n;i++) order[i]=i;\n"
        "    System.Array.Sort(order, (a,b) => ends[a]-ends[b]);\n"
        "    int count = 0; long lastEnd = long.MinValue;\n"
        "    foreach (int i in order) { if (starts[i] >= lastEnd) { count++; lastEnd = ends[i]; } }\n"
        f"    return {ret};\n"
        "} }\n"
    )


def _perl_activity_p(wrong):
    ret = "$count - 1" if wrong else "$count"
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $idx = 0; my $n = $data[$idx++]; my @starts = @data[$idx..$idx+$n-1]; $idx+=$n;\n"
        "my @ends = @data[$idx..$idx+$n-1];\n"
        "sub max_activities {\n"
        "    my ($starts, $ends) = @_;\n"
        "    my @order = sort { $ends->[$a] <=> $ends->[$b] } (0..scalar(@$starts)-1);\n"
        "    my $count = 0; my $lastEnd = -9**9**9;\n"
        "    foreach my $i (@order) { if ($starts->[$i] >= $lastEnd) { $count++; $lastEnd = $ends->[$i]; } }\n"
        f"    return {ret};\n"
        "}\n"
        "print max_activities(\\@starts, \\@ends), \"\\n\";\n"
    )


def _c_activity_p(wrong):
    ret = "count - 1" if wrong else "count"
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <limits.h>\n"
        "long long* g_cmp_ends;\n"
        "int cmp_activity(const void* a, const void* b) {\n"
        "    int ia = *(const int*)a, ib = *(const int*)b;\n"
        "    long long diff = g_cmp_ends[ia] - g_cmp_ends[ib];\n"
        "    return diff < 0 ? -1 : (diff > 0 ? 1 : 0);\n"
        "}\n"
        "int max_activities(int* starts, int* ends, int n) {\n"
        "    long long* endsBuf = (long long*)malloc(sizeof(long long)*(n>0?n:1));\n"
        "    for (int i=0;i<n;i++) endsBuf[i] = ends[i];\n"
        "    g_cmp_ends = endsBuf;\n"
        "    int* idx = (int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) idx[i]=i;\n"
        "    qsort(idx, n, sizeof(int), cmp_activity);\n"
        "    int count = 0; long long lastEnd = LLONG_MIN;\n"
        "    for (int k=0;k<n;k++) { int i = idx[k]; if (starts[i] >= lastEnd) { count++; lastEnd = ends[i]; } }\n"
        "    free(endsBuf); free(idx);\n"
        f"    return {ret};\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* starts=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&starts[i]);\n"
        "    int* ends=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&ends[i]);\n"
        "    printf(\"%d\\n\", max_activities(starts, ends, n));\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_activity_p(wrong):
    ret = "count - 1" if wrong else "count"
    return (
        "use std::io::Read;\n"
        "fn max_activities(starts: &Vec<i32>, ends: &Vec<i32>) -> i32 {\n"
        "    let n = starts.len();\n"
        "    let mut idx: Vec<usize> = (0..n).collect();\n"
        "    idx.sort_by_key(|&i| ends[i]);\n"
        "    let mut count = 0; let mut last_end: i64 = i64::MIN;\n"
        "    for &i in idx.iter() { if starts[i] as i64 >= last_end { count += 1; last_end = ends[i] as i64; } }\n"
        f"    {ret}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize;\n"
        "    let starts: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    let ends: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    println!(\"{}\", max_activities(&starts, &ends)); }\n"
    )


# ── closest-pair ─────────────────────────────────────────────────────────────
def _js_closest_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const lines = require('fs').readFileSync(0,'utf8').trim().split('\\n');\n"
        "const n = parseInt(lines[0]); const points = [];\n"
        "for (let i=0;i<n;i++) points.push(lines[1+i].trim().split(/\\s+/).map(Number));\n"
        "function closest_pair_sq_dist(points) {\n"
        "    let best = Infinity;\n"
        "    for (let i=0;i<points.length;i++) for (let j=i+1;j<points.length;j++) {\n"
        "        const dx = points[i][0]-points[j][0], dy = points[i][1]-points[j][1];\n"
        "        const d = dx*dx+dy*dy;\n"
        "        if (d < best) best = d;\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
        "console.log(closest_pair_sq_dist(points));\n"
    )


def _ts_closest_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const lines = require('fs').readFileSync(0,'utf8').trim().split('\\n');\n"
        "const n = parseInt(lines[0]); const points: number[][] = [];\n"
        "for (let i=0;i<n;i++) points.push(lines[1+i].trim().split(/\\s+/).map(Number));\n"
        "function closest_pair_sq_dist(points: number[][]): number {\n"
        "    let best = Infinity;\n"
        "    for (let i=0;i<points.length;i++) for (let j=i+1;j<points.length;j++) {\n"
        "        const dx = points[i][0]-points[j][0], dy = points[i][1]-points[j][1];\n"
        "        const d = dx*dx+dy*dy;\n"
        "        if (d < best) best = d;\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
        "console.log(closest_pair_sq_dist(points));\n"
    )


def _java_closest_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[][] points = new int[n][2];\n"
        "    for (int i=0;i<n;i++) { points[i][0]=sc.nextInt(); points[i][1]=sc.nextInt(); }\n"
        "    System.out.println(closest_pair_sq_dist(points));\n"
        "}\n"
        "static long closest_pair_sq_dist(int[][] points) {\n"
        "    long best = Long.MAX_VALUE;\n"
        "    for (int i=0;i<points.length;i++) for (int j=i+1;j<points.length;j++) {\n"
        "        long dx = points[i][0]-points[j][0], dy = points[i][1]-points[j][1];\n"
        "        long d = dx*dx+dy*dy;\n"
        "        if (d < best) best = d;\n"
        "    }\n"
        f"    return best{a};\n"
        "} }\n"
    )


def _cpp_closest_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\n#include <climits>\nusing namespace std;\n"
        "long long closest_pair_sq_dist(vector<vector<int>>& points) {\n"
        "    long long best = LLONG_MAX;\n"
        "    for (size_t i=0;i<points.size();i++) for (size_t j=i+1;j<points.size();j++) {\n"
        "        long long dx = points[i][0]-points[j][0], dy = points[i][1]-points[j][1];\n"
        "        long long d = dx*dx+dy*dy;\n"
        "        if (d < best) best = d;\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
        "int main() { int n; cin>>n; vector<vector<int>> points(n, vector<int>(2));\n"
        "    for (int i=0;i<n;i++) cin>>points[i][0]>>points[i][1];\n"
        "    cout << closest_pair_sq_dist(points) << endl; return 0;\n"
        "}\n"
    )


def _csharp_closest_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[][] points=new int[n][];\n"
        "    for (int i=0;i<n;i++) { points[i]=new int[]{int.Parse(t[idx++]), int.Parse(t[idx++])}; }\n"
        "    System.Console.WriteLine(closest_pair_sq_dist(points));\n"
        "}\n"
        "static long closest_pair_sq_dist(int[][] points) {\n"
        "    long best = long.MaxValue;\n"
        "    for (int i=0;i<points.Length;i++) for (int j=i+1;j<points.Length;j++) {\n"
        "        long dx = points[i][0]-points[j][0], dy = points[i][1]-points[j][1];\n"
        "        long d = dx*dx+dy*dy;\n"
        "        if (d < best) best = d;\n"
        "    }\n"
        f"    return best{a};\n"
        "} }\n"
    )


def _perl_closest_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "my @lines = split /\\n/, do { local $/; <STDIN> };\n"
        "my $n = $lines[0] + 0; my @points;\n"
        "for my $i (0..$n-1) { $points[$i] = [split ' ', $lines[1+$i]]; }\n"
        "sub closest_pair_sq_dist {\n"
        "    my ($points) = @_;\n"
        "    my $best = 9**9**9;\n"
        "    for (my $i=0;$i<scalar(@$points);$i++) {\n"
        "        for (my $j=$i+1;$j<scalar(@$points);$j++) {\n"
        "            my $dx = $points->[$i][0]-$points->[$j][0]; my $dy = $points->[$i][1]-$points->[$j][1];\n"
        "            my $d = $dx*$dx+$dy*$dy;\n"
        "            $best = $d if $d < $best;\n"
        "        }\n"
        "    }\n"
        f"    return $best{a};\n"
        "}\n"
        "print closest_pair_sq_dist(\\@points), \"\\n\";\n"
    )


def _c_closest_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <limits.h>\n"
        "long long closest_pair_sq_dist(int** points, int n) {\n"
        "    long long best = LLONG_MAX;\n"
        "    for (int i=0;i<n;i++) for (int j=i+1;j<n;j++) {\n"
        "        long long dx = points[i][0]-points[j][0];\n"
        "        long long dy = points[i][1]-points[j][1];\n"
        "        long long d = dx*dx+dy*dy;\n"
        "        if (d < best) best = d;\n"
        "    }\n"
        f"    return best{a};\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n);\n"
        "    int** points = (int**)malloc(sizeof(int*)*n);\n"
        "    for (int i=0;i<n;i++) { points[i]=(int*)malloc(sizeof(int)*2); scanf(\"%d %d\",&points[i][0],&points[i][1]); }\n"
        "    printf(\"%lld\\n\", closest_pair_sq_dist(points, n));\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_closest_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn closest_pair_sq_dist(points: &Vec<Vec<i32>>) -> i64 {\n"
        "    let mut best: i64 = i64::MAX;\n"
        "    for i in 0..points.len() { for j in (i+1)..points.len() {\n"
        "        let dx = (points[i][0]-points[j][0]) as i64; let dy = (points[i][1]-points[j][1]) as i64;\n"
        "        let d = dx*dx+dy*dy;\n"
        "        if d < best { best = d; }\n"
        "    } }\n"
        f"    best{a}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut lines = s.lines();\n"
        "    let n: usize = lines.next().unwrap().trim().parse().unwrap();\n"
        "    let mut points: Vec<Vec<i32>> = Vec::new();\n"
        "    for _ in 0..n { let l = lines.next().unwrap(); let v: Vec<i32> = l.split_whitespace().map(|x| x.parse().unwrap()).collect(); points.push(v); }\n"
        "    println!(\"{}\", closest_pair_sq_dist(&points)); }\n"
    )


# ── collatz ──────────────────────────────────────────────────────────────────
def _js_collatz_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const n = parseInt(require('fs').readFileSync(0,'utf8').trim());\n"
        "function collatz(n) {\n"
        "    let steps = 0; let x = n;\n"
        "    while (x !== 1) { if (x % 2 === 0) x = x/2; else x = 3*x+1; steps++; }\n"
        f"    return steps{a};\n"
        "}\n"
        "console.log(collatz(n));\n"
    )


def _ts_collatz_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const n: number = parseInt(require('fs').readFileSync(0,'utf8').trim());\n"
        "function collatz(n: number): number {\n"
        "    let steps = 0; let x = n;\n"
        "    while (x !== 1) { if (x % 2 === 0) x = x/2; else x = 3*x+1; steps++; }\n"
        f"    return steps{a};\n"
        "}\n"
        "console.log(collatz(n));\n"
    )


def _java_collatz_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "public class Main { public static void main(String[] args) {\n"
        "    int n = Integer.parseInt(new java.util.Scanner(System.in).nextLine().trim());\n"
        "    System.out.println(collatz(n));\n"
        "}\n"
        "static int collatz(int n) {\n"
        "    int steps = 0; long x = n;\n"
        "    while (x != 1) { if (x % 2 == 0) x = x/2; else x = 3*x+1; steps++; }\n"
        f"    return steps{a};\n"
        "} }\n"
    )


def _cpp_collatz_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\nusing namespace std;\n"
        "int collatz(int n) {\n"
        "    int steps = 0; long long x = n;\n"
        "    while (x != 1) { if (x % 2 == 0) x = x/2; else x = 3*x+1; steps++; }\n"
        f"    return steps{a};\n"
        "}\n"
        "int main() { int n; cin>>n; cout << collatz(n) << endl; return 0; }\n"
    )


def _csharp_collatz_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    int n = int.Parse(System.Console.In.ReadToEnd().Trim());\n"
        "    System.Console.WriteLine(collatz(n));\n"
        "}\n"
        "static int collatz(int n) {\n"
        "    int steps = 0; long x = n;\n"
        "    while (x != 1) { if (x % 2 == 0) x = x/2; else x = 3*x+1; steps++; }\n"
        f"    return steps{a};\n"
        "} }\n"
    )


def _perl_collatz_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "my $n = <STDIN>; chomp $n; $n = $n + 0;\n"
        "sub collatz {\n"
        "    my ($n) = @_;\n"
        "    my $steps = 0; my $x = $n;\n"
        "    while ($x != 1) { if ($x % 2 == 0) { $x = $x/2; } else { $x = 3*$x+1; } $steps++; }\n"
        f"    return $steps{a};\n"
        "}\n"
        "print collatz($n), \"\\n\";\n"
    )


def _c_collatz_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n"
        "int collatz(int n) {\n"
        "    int steps = 0; long long x = n;\n"
        "    while (x != 1) { if (x % 2 == 0) x = x/2; else x = 3*x+1; steps++; }\n"
        f"    return steps{a};\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); printf(\"%d\\n\", collatz(n)); return 0; }\n"
    )


def _rust_collatz_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn collatz(n: i32) -> i32 {\n"
        "    let mut steps = 0; let mut x: i64 = n as i64;\n"
        "    while x != 1 { if x % 2 == 0 { x = x/2; } else { x = 3*x+1; } steps += 1; }\n"
        f"    steps{a}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let n: i32 = s.trim().parse().unwrap();\n"
        "    println!(\"{}\", collatz(n)); }\n"
    )


# ── counting-inversions ──────────────────────────────────────────────────────
def _js_countinv_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function count_inversions(nums) {\n"
        "    let count = 0;\n"
        "    for (let i=0;i<nums.length;i++) for (let j=i+1;j<nums.length;j++) if (nums[i] > nums[j]) count++;\n"
        f"    return count{a};\n"
        "}\n"
        "console.log(count_inversions(nums));\n"
    )


def _ts_countinv_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function count_inversions(nums: number[]): number {\n"
        "    let count = 0;\n"
        "    for (let i=0;i<nums.length;i++) for (let j=i+1;j<nums.length;j++) if (nums[i] > nums[j]) count++;\n"
        f"    return count{a};\n"
        "}\n"
        "console.log(count_inversions(nums));\n"
    )


def _java_countinv_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] nums = new int[n]; for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "    System.out.println(count_inversions(nums));\n"
        "}\n"
        "static long count_inversions(int[] nums) {\n"
        "    long count = 0;\n"
        "    for (int i=0;i<nums.length;i++) for (int j=i+1;j<nums.length;j++) if (nums[i] > nums[j]) count++;\n"
        f"    return count{a};\n"
        "} }\n"
    )


def _cpp_countinv_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n"
        "long long count_inversions(vector<int>& nums) {\n"
        "    long long count = 0;\n"
        "    for (size_t i=0;i<nums.size();i++) for (size_t j=i+1;j<nums.size();j++) if (nums[i] > nums[j]) count++;\n"
        f"    return count{a};\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> nums(n); for (int i=0;i<n;i++) cin>>nums[i]; cout << count_inversions(nums) << endl; return 0; }\n"
    )


def _csharp_countinv_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] nums=new int[n]; for (int i=0;i<n;i++) nums[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(count_inversions(nums));\n"
        "}\n"
        "static long count_inversions(int[] nums) {\n"
        "    long count = 0;\n"
        "    for (int i=0;i<nums.Length;i++) for (int j=i+1;j<nums.Length;j++) if (nums[i] > nums[j]) count++;\n"
        f"    return count{a};\n"
        "} }\n"
    )


def _perl_countinv_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @nums = @data[0..$n-1];\n"
        "sub count_inversions {\n"
        "    my ($nums) = @_;\n"
        "    my $count = 0; my $nn = scalar(@$nums);\n"
        "    for (my $i=0;$i<$nn;$i++) { for (my $j=$i+1;$j<$nn;$j++) { $count++ if $nums->[$i] > $nums->[$j]; } }\n"
        f"    return $count{a};\n"
        "}\n"
        "print count_inversions(\\@nums), \"\\n\";\n"
    )


def _c_countinv_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "long long count_inversions(int* nums, int n) {\n"
        "    long long count = 0;\n"
        "    for (int i=0;i<n;i++) for (int j=i+1;j<n;j++) if (nums[i] > nums[j]) count++;\n"
        f"    return count{a};\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* nums=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&nums[i]); printf(\"%lld\\n\", count_inversions(nums,n)); return 0; }\n"
    )


def _rust_countinv_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn count_inversions(nums: &Vec<i32>) -> i64 {\n"
        "    let mut count: i64 = 0;\n"
        "    for i in 0..nums.len() { for j in (i+1)..nums.len() { if nums[i] > nums[j] { count += 1; } } }\n"
        f"    count{a}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    println!(\"{}\", count_inversions(&nums)); }\n"
    )


# ── egg-drop ─────────────────────────────────────────────────────────────────
def _js_eggdrop_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const [eggs, floors] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "function egg_drop(eggs, floors) {\n"
        "    if (floors === 0) return 0" + a + ";\n"
        "    const dp = new Array(eggs+1).fill(0);\n"
        "    let moves = 0;\n"
        "    while (dp[eggs] < floors) {\n"
        "        moves++;\n"
        "        for (let k=eggs;k>=1;k--) dp[k] = dp[k] + dp[k-1] + 1;\n"
        "    }\n"
        f"    return moves{a};\n"
        "}\n"
        "console.log(egg_drop(eggs, floors));\n"
    )


def _ts_eggdrop_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const [eggs, floors]: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "function egg_drop(eggs: number, floors: number): number {\n"
        "    if (floors === 0) return 0" + a + ";\n"
        "    const dp: number[] = new Array(eggs+1).fill(0);\n"
        "    let moves = 0;\n"
        "    while (dp[eggs] < floors) {\n"
        "        moves++;\n"
        "        for (let k=eggs;k>=1;k--) dp[k] = dp[k] + dp[k-1] + 1;\n"
        "    }\n"
        f"    return moves{a};\n"
        "}\n"
        "console.log(egg_drop(eggs, floors));\n"
    )


def _java_eggdrop_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int eggs = sc.nextInt(); int floors = sc.nextInt();\n"
        "    System.out.println(egg_drop(eggs, floors));\n"
        "}\n"
        "static int egg_drop(int eggs, int floors) {\n"
        "    if (floors == 0) return 0" + a + ";\n"
        "    int[] dp = new int[eggs+1];\n"
        "    int moves = 0;\n"
        "    while (dp[eggs] < floors) {\n"
        "        moves++;\n"
        "        for (int k=eggs;k>=1;k--) dp[k] = dp[k] + dp[k-1] + 1;\n"
        "    }\n"
        f"    return moves{a};\n"
        "} }\n"
    )


def _cpp_eggdrop_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n"
        "int egg_drop(int eggs, int floors) {\n"
        "    if (floors == 0) return 0" + a + ";\n"
        "    vector<int> dp(eggs+1, 0);\n"
        "    int moves = 0;\n"
        "    while (dp[eggs] < floors) {\n"
        "        moves++;\n"
        "        for (int k=eggs;k>=1;k--) dp[k] = dp[k] + dp[k-1] + 1;\n"
        "    }\n"
        f"    return moves{a};\n"
        "}\n"
        "int main() { int eggs, floors; cin>>eggs>>floors; cout << egg_drop(eggs, floors) << endl; return 0; }\n"
    )


def _csharp_eggdrop_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int eggs=int.Parse(t[0]); int floors=int.Parse(t[1]);\n"
        "    System.Console.WriteLine(egg_drop(eggs, floors));\n"
        "}\n"
        "static int egg_drop(int eggs, int floors) {\n"
        "    if (floors == 0) return 0" + a + ";\n"
        "    int[] dp = new int[eggs+1];\n"
        "    int moves = 0;\n"
        "    while (dp[eggs] < floors) {\n"
        "        moves++;\n"
        "        for (int k=eggs;k>=1;k--) dp[k] = dp[k] + dp[k-1] + 1;\n"
        "    }\n"
        f"    return moves{a};\n"
        "} }\n"
    )


def _perl_eggdrop_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "my ($eggs, $floors) = split ' ', do { local $/; <STDIN> };\n"
        "sub egg_drop {\n"
        "    my ($eggs, $floors) = @_;\n"
        "    return (0" + a + ") if $floors == 0;\n"
        "    my @dp = (0) x ($eggs+1);\n"
        "    my $moves = 0;\n"
        "    while ($dp[$eggs] < $floors) {\n"
        "        $moves++;\n"
        "        for (my $k=$eggs;$k>=1;$k--) { $dp[$k] = $dp[$k] + $dp[$k-1] + 1; }\n"
        "    }\n"
        f"    return $moves{a};\n"
        "}\n"
        "print egg_drop($eggs, $floors), \"\\n\";\n"
    )


def _c_eggdrop_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int egg_drop(int eggs, int floors) {\n"
        "    if (floors == 0) return 0" + a + ";\n"
        "    int* dp = (int*)calloc(eggs+1, sizeof(int));\n"
        "    int moves = 0;\n"
        "    while (dp[eggs] < floors) {\n"
        "        moves++;\n"
        "        for (int k=eggs;k>=1;k--) dp[k] = dp[k] + dp[k-1] + 1;\n"
        "    }\n"
        "    free(dp);\n"
        f"    return moves{a};\n"
        "}\n"
        "int main() { int eggs, floors; scanf(\"%d %d\",&eggs,&floors); printf(\"%d\\n\", egg_drop(eggs,floors)); return 0; }\n"
    )


def _rust_eggdrop_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn egg_drop(eggs: i32, floors: i32) -> i32 {\n"
        "    if floors == 0 { return 0" + a + "; }\n"
        "    let e = eggs as usize;\n"
        "    let mut dp = vec![0i32; e+1];\n"
        "    let mut moves = 0;\n"
        "    while dp[e] < floors {\n"
        "        moves += 1;\n"
        "        for k in (1..=e).rev() { dp[k] = dp[k] + dp[k-1] + 1; }\n"
        "    }\n"
        f"    moves{a}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let eggs = it.next().unwrap(); let floors = it.next().unwrap();\n"
        "    println!(\"{}\", egg_drop(eggs, floors)); }\n"
    )


# ── euler-totient ────────────────────────────────────────────────────────────
def _js_totient_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const n = parseInt(require('fs').readFileSync(0,'utf8').trim());\n"
        "function euler_totient(n) {\n"
        "    let result = n; let x = n; let p = 2;\n"
        "    while (p*p <= x) {\n"
        "        if (x % p === 0) { while (x % p === 0) x = Math.floor(x/p); result -= Math.floor(result/p); }\n"
        "        p++;\n"
        "    }\n"
        "    if (x > 1) result -= Math.floor(result/x);\n"
        f"    return result{a};\n"
        "}\n"
        "console.log(euler_totient(n));\n"
    )


def _ts_totient_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const n: number = parseInt(require('fs').readFileSync(0,'utf8').trim());\n"
        "function euler_totient(n: number): number {\n"
        "    let result = n; let x = n; let p = 2;\n"
        "    while (p*p <= x) {\n"
        "        if (x % p === 0) { while (x % p === 0) x = Math.floor(x/p); result -= Math.floor(result/p); }\n"
        "        p++;\n"
        "    }\n"
        "    if (x > 1) result -= Math.floor(result/x);\n"
        f"    return result{a};\n"
        "}\n"
        "console.log(euler_totient(n));\n"
    )


def _java_totient_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "public class Main { public static void main(String[] args) {\n"
        "    int n = Integer.parseInt(new java.util.Scanner(System.in).nextLine().trim());\n"
        "    System.out.println(euler_totient(n));\n"
        "}\n"
        "static int euler_totient(int n) {\n"
        "    int result = n; int x = n; int p = 2;\n"
        "    while ((long)p*p <= x) {\n"
        "        if (x % p == 0) { while (x % p == 0) x /= p; result -= result/p; }\n"
        "        p++;\n"
        "    }\n"
        "    if (x > 1) result -= result/x;\n"
        f"    return result{a};\n"
        "} }\n"
    )


def _cpp_totient_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\nusing namespace std;\n"
        "int euler_totient(int n) {\n"
        "    int result = n; int x = n; long long p = 2;\n"
        "    while (p*p <= x) {\n"
        "        if (x % p == 0) { while (x % p == 0) x /= p; result -= result/p; }\n"
        "        p++;\n"
        "    }\n"
        "    if (x > 1) result -= result/x;\n"
        f"    return result{a};\n"
        "}\n"
        "int main() { int n; cin>>n; cout << euler_totient(n) << endl; return 0; }\n"
    )


def _csharp_totient_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    int n = int.Parse(System.Console.In.ReadToEnd().Trim());\n"
        "    System.Console.WriteLine(euler_totient(n));\n"
        "}\n"
        "static int euler_totient(int n) {\n"
        "    int result = n; int x = n; long p = 2;\n"
        "    while (p*p <= x) {\n"
        "        if (x % p == 0) { while (x % p == 0) x /= (int)p; result -= result/(int)p; }\n"
        "        p++;\n"
        "    }\n"
        "    if (x > 1) result -= result/x;\n"
        f"    return result{a};\n"
        "} }\n"
    )


def _perl_totient_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "use integer;\n"
        "my $n = <STDIN>; chomp $n; $n = $n + 0;\n"
        "sub euler_totient {\n"
        "    my ($n) = @_;\n"
        "    my $result = $n; my $x = $n; my $p = 2;\n"
        "    while ($p*$p <= $x) {\n"
        "        if ($x % $p == 0) { while ($x % $p == 0) { $x = $x/$p; } $result -= $result/$p; }\n"
        "        $p++;\n"
        "    }\n"
        "    if ($x > 1) { $result -= $result/$x; }\n"
        f"    return $result{a};\n"
        "}\n"
        "print euler_totient($n), \"\\n\";\n"
    )


def _c_totient_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n"
        "int euler_totient(int n) {\n"
        "    int result = n; int x = n; long long p = 2;\n"
        "    while (p*p <= x) {\n"
        "        if (x % p == 0) { while (x % p == 0) x /= (int)p; result -= result/(int)p; }\n"
        "        p++;\n"
        "    }\n"
        "    if (x > 1) result -= result/x;\n"
        f"    return result{a};\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); printf(\"%d\\n\", euler_totient(n)); return 0; }\n"
    )


def _rust_totient_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn euler_totient(n: i32) -> i32 {\n"
        "    let mut result = n; let mut x = n; let mut p: i64 = 2;\n"
        "    while p*p <= x as i64 {\n"
        "        if x % (p as i32) == 0 { while x % (p as i32) == 0 { x /= p as i32; } result -= result/(p as i32); }\n"
        "        p += 1;\n"
        "    }\n"
        "    if x > 1 { result -= result/x; }\n"
        f"    result{a}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let n: i32 = s.trim().parse().unwrap();\n"
        "    println!(\"{}\", euler_totient(n)); }\n"
    )


# ── gas-station ──────────────────────────────────────────────────────────────
def _js_gasstation_p(wrong):
    ret = "start + 1" if wrong else "(total >= 0 ? start : -1)"
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "let idx=0; const n=data[idx++]; const gas=data.slice(idx,idx+n); idx+=n; const cost=data.slice(idx,idx+n);\n"
        "function can_complete_circuit(gas, cost) {\n"
        "    let total = 0, tank = 0, start = 0;\n"
        "    for (let i=0;i<gas.length;i++) {\n"
        "        const diff = gas[i]-cost[i]; total += diff; tank += diff;\n"
        "        if (tank < 0) { start = i+1; tank = 0; }\n"
        "    }\n"
        f"    return {ret};\n"
        "}\n"
        "console.log(can_complete_circuit(gas, cost));\n"
    )


def _ts_gasstation_p(wrong):
    ret = "start + 1" if wrong else "(total >= 0 ? start : -1)"
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "let idx=0; const n=data[idx++]; const gas=data.slice(idx,idx+n); idx+=n; const cost=data.slice(idx,idx+n);\n"
        "function can_complete_circuit(gas: number[], cost: number[]): number {\n"
        "    let total = 0, tank = 0, start = 0;\n"
        "    for (let i=0;i<gas.length;i++) {\n"
        "        const diff = gas[i]-cost[i]; total += diff; tank += diff;\n"
        "        if (tank < 0) { start = i+1; tank = 0; }\n"
        "    }\n"
        f"    return {ret};\n"
        "}\n"
        "console.log(can_complete_circuit(gas, cost));\n"
    )


def _java_gasstation_p(wrong):
    ret = "start + 1" if wrong else "(total >= 0 ? start : -1)"
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] gas = new int[n]; for (int i=0;i<n;i++) gas[i]=sc.nextInt();\n"
        "    int[] cost = new int[n]; for (int i=0;i<n;i++) cost[i]=sc.nextInt();\n"
        "    System.out.println(can_complete_circuit(gas, cost));\n"
        "}\n"
        "static int can_complete_circuit(int[] gas, int[] cost) {\n"
        "    long total = 0, tank = 0; int start = 0;\n"
        "    for (int i=0;i<gas.length;i++) {\n"
        "        long diff = gas[i]-cost[i]; total += diff; tank += diff;\n"
        "        if (tank < 0) { start = i+1; tank = 0; }\n"
        "    }\n"
        f"    return {ret};\n"
        "} }\n"
    )


def _cpp_gasstation_p(wrong):
    ret = "start + 1" if wrong else "(total >= 0 ? start : -1)"
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n"
        "int can_complete_circuit(vector<int>& gas, vector<int>& cost) {\n"
        "    long long total = 0, tank = 0; int start = 0;\n"
        "    for (size_t i=0;i<gas.size();i++) {\n"
        "        long long diff = gas[i]-cost[i]; total += diff; tank += diff;\n"
        "        if (tank < 0) { start = i+1; tank = 0; }\n"
        "    }\n"
        f"    return {ret};\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> gas(n); for (int i=0;i<n;i++) cin>>gas[i];\n"
        "    vector<int> cost(n); for (int i=0;i<n;i++) cin>>cost[i];\n"
        "    cout << can_complete_circuit(gas, cost) << endl; return 0;\n"
        "}\n"
    )


def _csharp_gasstation_p(wrong):
    ret = "start + 1" if wrong else "(total >= 0 ? start : -1)"
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] gas=new int[n]; for (int i=0;i<n;i++) gas[i]=int.Parse(t[idx++]);\n"
        "    int[] cost=new int[n]; for (int i=0;i<n;i++) cost[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(can_complete_circuit(gas, cost));\n"
        "}\n"
        "static int can_complete_circuit(int[] gas, int[] cost) {\n"
        "    long total = 0, tank = 0; int start = 0;\n"
        "    for (int i=0;i<gas.Length;i++) {\n"
        "        long diff = gas[i]-cost[i]; total += diff; tank += diff;\n"
        "        if (tank < 0) { start = i+1; tank = 0; }\n"
        "    }\n"
        f"    return {ret};\n"
        "} }\n"
    )


def _perl_gasstation_p(wrong):
    ret = "$start + 1" if wrong else "($total >= 0 ? $start : -1)"
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $idx = 0; my $n = $data[$idx++]; my @gas = @data[$idx..$idx+$n-1]; $idx+=$n;\n"
        "my @cost = @data[$idx..$idx+$n-1];\n"
        "sub can_complete_circuit {\n"
        "    my ($gas, $cost) = @_;\n"
        "    my $total = 0; my $tank = 0; my $start = 0;\n"
        "    for (my $i=0;$i<scalar(@$gas);$i++) {\n"
        "        my $diff = $gas->[$i]-$cost->[$i]; $total += $diff; $tank += $diff;\n"
        "        if ($tank < 0) { $start = $i+1; $tank = 0; }\n"
        "    }\n"
        f"    return {ret};\n"
        "}\n"
        "print can_complete_circuit(\\@gas, \\@cost), \"\\n\";\n"
    )


def _c_gasstation_p(wrong):
    ret = "start + 1" if wrong else "(total >= 0 ? start : -1)"
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int can_complete_circuit(int* gas, int* cost, int n) {\n"
        "    long long total = 0, tank = 0; int start = 0;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        long long diff = gas[i]-cost[i]; total += diff; tank += diff;\n"
        "        if (tank < 0) { start = i+1; tank = 0; }\n"
        "    }\n"
        f"    return {ret};\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* gas=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&gas[i]);\n"
        "    int* cost=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&cost[i]);\n"
        "    printf(\"%d\\n\", can_complete_circuit(gas, cost, n));\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_gasstation_p(wrong):
    ret = "start + 1" if wrong else "(if total >= 0 { start } else { -1 })"
    return (
        "use std::io::Read;\n"
        "fn can_complete_circuit(gas: &Vec<i32>, cost: &Vec<i32>) -> i32 {\n"
        "    let mut total: i64 = 0; let mut tank: i64 = 0; let mut start: i32 = 0;\n"
        "    for i in 0..gas.len() {\n"
        "        let diff = (gas[i]-cost[i]) as i64; total += diff; tank += diff;\n"
        "        if tank < 0 { start = i as i32 + 1; tank = 0; }\n"
        "    }\n"
        f"    {ret}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize;\n"
        "    let gas: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    let cost: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    println!(\"{}\", can_complete_circuit(&gas, &cost)); }\n"
    )


# ── insert-interval ──────────────────────────────────────────────────────────
def _js_insertint_p(wrong):
    incr = "for (const r of out) r[1] += 1;\n    " if wrong else ""
    return (
        "const lines = require('fs').readFileSync(0,'utf8').trim().split('\\n');\n"
        "const n = parseInt(lines[0]); const intervals = [];\n"
        "for (let i=0;i<n;i++) intervals.push(lines[1+i].trim().split(/\\s+/).map(Number));\n"
        "const [new_s, new_e] = lines[1+n].trim().split(/\\s+/).map(Number);\n"
        "function insert_interval(intervals, new_s, new_e) {\n"
        "    const out = []; let i = 0; const nn = intervals.length;\n"
        "    while (i < nn && intervals[i][1] < new_s) { out.push(intervals[i]); i++; }\n"
        "    let s = new_s, e = new_e;\n"
        "    while (i < nn && intervals[i][0] <= e) { s = Math.min(s, intervals[i][0]); e = Math.max(e, intervals[i][1]); i++; }\n"
        "    out.push([s,e]);\n"
        "    while (i < nn) { out.push(intervals[i]); i++; }\n"
        f"    {incr}return out;\n"
        "}\n"
        "console.log(insert_interval(intervals, new_s, new_e).map(r => r.join(' ')).join('\\n'));\n"
    )


def _ts_insertint_p(wrong):
    incr = "for (const r of out) r[1] += 1;\n    " if wrong else ""
    return (
        "const lines = require('fs').readFileSync(0,'utf8').trim().split('\\n');\n"
        "const n = parseInt(lines[0]); const intervals: number[][] = [];\n"
        "for (let i=0;i<n;i++) intervals.push(lines[1+i].trim().split(/\\s+/).map(Number));\n"
        "const [new_s, new_e]: number[] = lines[1+n].trim().split(/\\s+/).map(Number);\n"
        "function insert_interval(intervals: number[][], new_s: number, new_e: number): number[][] {\n"
        "    const out: number[][] = []; let i = 0; const nn = intervals.length;\n"
        "    while (i < nn && intervals[i][1] < new_s) { out.push(intervals[i]); i++; }\n"
        "    let s = new_s, e = new_e;\n"
        "    while (i < nn && intervals[i][0] <= e) { s = Math.min(s, intervals[i][0]); e = Math.max(e, intervals[i][1]); i++; }\n"
        "    out.push([s,e]);\n"
        "    while (i < nn) { out.push(intervals[i]); i++; }\n"
        f"    {incr}return out;\n"
        "}\n"
        "console.log(insert_interval(intervals, new_s, new_e).map(r => r.join(' ')).join('\\n'));\n"
    )


def _java_insertint_p(wrong):
    incr = "for (int[] r : out) r[1] += 1;\n        " if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[][] intervals = new int[n][2];\n"
        "    for (int i=0;i<n;i++) { intervals[i][0]=sc.nextInt(); intervals[i][1]=sc.nextInt(); }\n"
        "    int new_s = sc.nextInt(); int new_e = sc.nextInt();\n"
        "    int[][] out = insert_interval(intervals, new_s, new_e);\n"
        "    StringBuilder sb = new StringBuilder();\n"
        "    for (int i=0;i<out.length;i++) { if (i>0) sb.append('\\n'); sb.append(out[i][0]).append(' ').append(out[i][1]); }\n"
        "    System.out.println(sb.toString());\n"
        "}\n"
        "static int[][] insert_interval(int[][] intervals, int new_s, int new_e) {\n"
        "    java.util.List<int[]> out = new java.util.ArrayList<>();\n"
        "    int i = 0, n = intervals.length;\n"
        "    while (i < n && intervals[i][1] < new_s) { out.add(intervals[i]); i++; }\n"
        "    int s = new_s, e = new_e;\n"
        "    while (i < n && intervals[i][0] <= e) { s = Math.min(s, intervals[i][0]); e = Math.max(e, intervals[i][1]); i++; }\n"
        "    out.add(new int[]{s,e});\n"
        "    while (i < n) { out.add(intervals[i]); i++; }\n"
        f"        {incr}return out.toArray(new int[0][]);\n"
        "} }\n"
    )


def _cpp_insertint_p(wrong):
    incr = "for (auto& r : out) r[1] += 1;\n    " if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n"
        "vector<vector<int>> insert_interval(vector<vector<int>>& intervals, int new_s, int new_e) {\n"
        "    vector<vector<int>> out;\n"
        "    int i = 0, n = intervals.size();\n"
        "    while (i < n && intervals[i][1] < new_s) { out.push_back(intervals[i]); i++; }\n"
        "    int s = new_s, e = new_e;\n"
        "    while (i < n && intervals[i][0] <= e) { s = min(s, intervals[i][0]); e = max(e, intervals[i][1]); i++; }\n"
        "    out.push_back({s,e});\n"
        "    while (i < n) { out.push_back(intervals[i]); i++; }\n"
        f"    {incr}return out;\n"
        "}\n"
        "int main() { int n; cin>>n; vector<vector<int>> intervals(n, vector<int>(2));\n"
        "    for (int i=0;i<n;i++) cin>>intervals[i][0]>>intervals[i][1];\n"
        "    int new_s, new_e; cin>>new_s>>new_e;\n"
        "    vector<vector<int>> out = insert_interval(intervals, new_s, new_e);\n"
        "    for (size_t i=0;i<out.size();i++) { if (i) cout<<'\\n'; cout<<out[i][0]<<' '<<out[i][1]; }\n"
        "    cout << endl; return 0;\n"
        "}\n"
    )


def _csharp_insertint_p(wrong):
    incr = "foreach (int[] r in outList) r[1] += 1;\n        " if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[][] intervals=new int[n][];\n"
        "    for (int i=0;i<n;i++) intervals[i]=new int[]{int.Parse(t[idx++]), int.Parse(t[idx++])};\n"
        "    int new_s=int.Parse(t[idx++]); int new_e=int.Parse(t[idx++]);\n"
        "    int[][] outArr = insert_interval(intervals, new_s, new_e);\n"
        "    var lines = new System.Collections.Generic.List<string>();\n"
        "    foreach (var r in outArr) lines.Add(r[0] + \" \" + r[1]);\n"
        "    System.Console.WriteLine(string.Join(\"\\n\", lines));\n"
        "}\n"
        "static int[][] insert_interval(int[][] intervals, int new_s, int new_e) {\n"
        "    var outList = new System.Collections.Generic.List<int[]>();\n"
        "    int i = 0, n = intervals.Length;\n"
        "    while (i < n && intervals[i][1] < new_s) { outList.Add(intervals[i]); i++; }\n"
        "    int s = new_s, e = new_e;\n"
        "    while (i < n && intervals[i][0] <= e) { s = System.Math.Min(s, intervals[i][0]); e = System.Math.Max(e, intervals[i][1]); i++; }\n"
        "    outList.Add(new int[]{s,e});\n"
        "    while (i < n) { outList.Add(intervals[i]); i++; }\n"
        f"        {incr}return outList.ToArray();\n"
        "} }\n"
    )


def _perl_insertint_p(wrong):
    incr = "foreach my $r (@out) { $r->[1] += 1; }\n    " if wrong else ""
    return (
        "my @lines = split /\\n/, do { local $/; <STDIN> };\n"
        "my $n = $lines[0] + 0; my @intervals;\n"
        "for my $i (0..$n-1) { $intervals[$i] = [split ' ', $lines[1+$i]]; }\n"
        "my ($new_s, $new_e) = split ' ', $lines[1+$n];\n"
        "sub insert_interval {\n"
        "    my ($intervals, $new_s, $new_e) = @_;\n"
        "    my @out; my $i = 0; my $nn = scalar(@$intervals);\n"
        "    while ($i < $nn && $intervals->[$i][1] < $new_s) { push @out, $intervals->[$i]; $i++; }\n"
        "    my $s = $new_s; my $e = $new_e;\n"
        "    while ($i < $nn && $intervals->[$i][0] <= $e) {\n"
        "        $s = $intervals->[$i][0] if $intervals->[$i][0] < $s;\n"
        "        $e = $intervals->[$i][1] if $intervals->[$i][1] > $e;\n"
        "        $i++;\n"
        "    }\n"
        "    push @out, [$s, $e];\n"
        "    while ($i < $nn) { push @out, $intervals->[$i]; $i++; }\n"
        f"    {incr}return \\@out;\n"
        "}\n"
        "print join(\"\\n\", map { join(' ', @$_) } @{insert_interval(\\@intervals, $new_s, $new_e)}), \"\\n\";\n"
    )


def _c_insertint_p(wrong):
    incr = "for (int i=0;i<oc;i++) out[i][1] += 1;\n    " if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int** insert_interval(int** intervals, int n, int new_s, int new_e, int* out_size) {\n"
        "    int** out = (int**)malloc(sizeof(int*)*(n+1));\n"
        "    int oc = 0;\n"
        "    int i = 0;\n"
        "    while (i < n && intervals[i][1] < new_s) {\n"
        "        out[oc] = (int*)malloc(sizeof(int)*2); out[oc][0]=intervals[i][0]; out[oc][1]=intervals[i][1]; oc++; i++;\n"
        "    }\n"
        "    int s = new_s, e = new_e;\n"
        "    while (i < n && intervals[i][0] <= e) {\n"
        "        if (intervals[i][0] < s) s = intervals[i][0];\n"
        "        if (intervals[i][1] > e) e = intervals[i][1];\n"
        "        i++;\n"
        "    }\n"
        "    out[oc] = (int*)malloc(sizeof(int)*2); out[oc][0]=s; out[oc][1]=e; oc++;\n"
        "    while (i < n) {\n"
        "        out[oc] = (int*)malloc(sizeof(int)*2); out[oc][0]=intervals[i][0]; out[oc][1]=intervals[i][1]; oc++; i++;\n"
        "    }\n"
        f"    {incr}*out_size = oc;\n"
        "    return out;\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n);\n"
        "    int** intervals = (int**)malloc(sizeof(int*)*(n>0?n:1));\n"
        "    for (int i=0;i<n;i++) { intervals[i]=(int*)malloc(sizeof(int)*2); scanf(\"%d %d\",&intervals[i][0],&intervals[i][1]); }\n"
        "    int new_s, new_e; scanf(\"%d %d\",&new_s,&new_e);\n"
        "    int oc; int** out = insert_interval(intervals, n, new_s, new_e, &oc);\n"
        "    for (int i=0;i<oc;i++) { if (i) printf(\"\\n\"); printf(\"%d %d\", out[i][0], out[i][1]); }\n"
        "    printf(\"\\n\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_insertint_p(wrong):
    incr = "for r in out.iter_mut() { r[1] += 1; }\n    " if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn insert_interval(intervals: &Vec<Vec<i32>>, new_s: i32, new_e: i32) -> Vec<Vec<i32>> {\n"
        "    let mut out: Vec<Vec<i32>> = Vec::new();\n"
        "    let n = intervals.len(); let mut i = 0;\n"
        "    while i < n && intervals[i][1] < new_s { out.push(intervals[i].clone()); i += 1; }\n"
        "    let mut s = new_s; let mut e = new_e;\n"
        "    while i < n && intervals[i][0] <= e { s = s.min(intervals[i][0]); e = e.max(intervals[i][1]); i += 1; }\n"
        "    out.push(vec![s,e]);\n"
        "    while i < n { out.push(intervals[i].clone()); i += 1; }\n"
        f"    {incr}out\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut lines = s.lines();\n"
        "    let n: usize = lines.next().unwrap().trim().parse().unwrap();\n"
        "    let mut intervals: Vec<Vec<i32>> = Vec::new();\n"
        "    for _ in 0..n { let l = lines.next().unwrap(); let v: Vec<i32> = l.split_whitespace().map(|x| x.parse().unwrap()).collect(); intervals.push(v); }\n"
        "    let last = lines.next().unwrap(); let mut it = last.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let new_s = it.next().unwrap(); let new_e = it.next().unwrap();\n"
        "    let out = insert_interval(&intervals, new_s, new_e);\n"
        "    let lines_out: Vec<String> = out.iter().map(|r| format!(\"{} {}\", r[0], r[1])).collect();\n"
        "    println!(\"{}\", lines_out.join(\"\\n\")); }\n"
    )


# ── first-occurrence ─────────────────────────────────────────────────────────
def _js_firstocc_p(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n); const target = data[1+n];\n"
        "function first_occurrence(nums, target) {\n"
        "    let lo = 0, hi = nums.length-1, ans = -1;\n"
        "    while (lo <= hi) {\n"
        "        const mid = (lo+hi) >> 1;\n"
        f"        if (nums[mid] === target) {{ ans = {ret}; hi = mid-1; }}\n"
        "        else if (nums[mid] < target) lo = mid+1; else hi = mid-1;\n"
        "    }\n"
        "    return ans;\n"
        "}\n"
        "console.log(first_occurrence(nums, target));\n"
    )


def _ts_firstocc_p(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n); const target = data[1+n];\n"
        "function first_occurrence(nums: number[], target: number): number {\n"
        "    let lo = 0, hi = nums.length-1, ans = -1;\n"
        "    while (lo <= hi) {\n"
        "        const mid = (lo+hi) >> 1;\n"
        f"        if (nums[mid] === target) {{ ans = {ret}; hi = mid-1; }}\n"
        "        else if (nums[mid] < target) lo = mid+1; else hi = mid-1;\n"
        "    }\n"
        "    return ans;\n"
        "}\n"
        "console.log(first_occurrence(nums, target));\n"
    )


def _java_firstocc_p(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] nums = new int[n]; for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "    int target = sc.nextInt();\n"
        "    System.out.println(first_occurrence(nums, target));\n"
        "}\n"
        "static int first_occurrence(int[] nums, int target) {\n"
        "    int lo = 0, hi = nums.length-1, ans = -1;\n"
        "    while (lo <= hi) {\n"
        "        int mid = (lo+hi) >>> 1;\n"
        f"        if (nums[mid] == target) {{ ans = {ret}; hi = mid-1; }}\n"
        "        else if (nums[mid] < target) lo = mid+1; else hi = mid-1;\n"
        "    }\n"
        "    return ans;\n"
        "} }\n"
    )


def _cpp_firstocc_p(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n"
        "int first_occurrence(vector<int>& nums, int target) {\n"
        "    int lo = 0, hi = (int)nums.size()-1, ans = -1;\n"
        "    while (lo <= hi) {\n"
        "        int mid = lo + (hi-lo)/2;\n"
        f"        if (nums[mid] == target) {{ ans = {ret}; hi = mid-1; }}\n"
        "        else if (nums[mid] < target) lo = mid+1; else hi = mid-1;\n"
        "    }\n"
        "    return ans;\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> nums(n); for (int i=0;i<n;i++) cin>>nums[i]; int target; cin>>target;\n"
        "    cout << first_occurrence(nums, target) << endl; return 0;\n"
        "}\n"
    )


def _csharp_firstocc_p(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] nums=new int[n]; for (int i=0;i<n;i++) nums[i]=int.Parse(t[idx++]);\n"
        "    int target=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(first_occurrence(nums, target));\n"
        "}\n"
        "static int first_occurrence(int[] nums, int target) {\n"
        "    int lo = 0, hi = nums.Length-1, ans = -1;\n"
        "    while (lo <= hi) {\n"
        "        int mid = lo + (hi-lo)/2;\n"
        f"        if (nums[mid] == target) {{ ans = {ret}; hi = mid-1; }}\n"
        "        else if (nums[mid] < target) lo = mid+1; else hi = mid-1;\n"
        "    }\n"
        "    return ans;\n"
        "} }\n"
    )


def _perl_firstocc_p(wrong):
    ret = "$mid + 1" if wrong else "$mid"
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @nums = @data[0..$n-1]; my $target = $data[$n];\n"
        "sub first_occurrence {\n"
        "    my ($nums, $target) = @_;\n"
        "    my $lo = 0; my $hi = scalar(@$nums)-1; my $ans = -1;\n"
        "    while ($lo <= $hi) {\n"
        "        my $mid = int(($lo+$hi)/2);\n"
        f"        if ($nums->[$mid] == $target) {{ $ans = {ret}; $hi = $mid-1; }}\n"
        "        elsif ($nums->[$mid] < $target) { $lo = $mid+1; } else { $hi = $mid-1; }\n"
        "    }\n"
        "    return $ans;\n"
        "}\n"
        "print first_occurrence(\\@nums, $target), \"\\n\";\n"
    )


def _c_firstocc_p(wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int first_occurrence(int* nums, int n, int target) {\n"
        "    int lo = 0, hi = n-1, ans = -1;\n"
        "    while (lo <= hi) {\n"
        "        int mid = lo + (hi-lo)/2;\n"
        f"        if (nums[mid] == target) {{ ans = {ret}; hi = mid-1; }}\n"
        "        else if (nums[mid] < target) lo = mid+1; else hi = mid-1;\n"
        "    }\n"
        "    return ans;\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* nums=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&nums[i]);\n"
        "    int target; scanf(\"%d\",&target);\n"
        "    printf(\"%d\\n\", first_occurrence(nums, n, target));\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_firstocc_p(wrong):
    ret = "mid as i32 + 1" if wrong else "mid as i32"
    return (
        "use std::io::Read;\n"
        "fn first_occurrence(nums: &Vec<i32>, target: i32) -> i32 {\n"
        "    if nums.is_empty() { return -1; }\n"
        "    let (mut lo, mut hi): (i32, i32) = (0, nums.len() as i32 - 1);\n"
        "    let mut ans: i32 = -1;\n"
        "    while lo <= hi {\n"
        "        let mid = lo + (hi-lo)/2;\n"
        f"        if nums[mid as usize] == target {{ ans = {ret}; hi = mid-1; }}\n"
        "        else if nums[mid as usize] < target { lo = mid+1; } else { hi = mid-1; }\n"
        "    }\n"
        "    ans\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    let target = it.next().unwrap();\n"
        "    println!(\"{}\", first_occurrence(&nums, target)); }\n"
    )


# ── house-robber-circular ────────────────────────────────────────────────────
def _js_robcirc_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function rob_line(nums) {\n"
        "    let prev = 0, cur = 0;\n"
        "    for (const x of nums) { const t = Math.max(cur, prev+x); prev = cur; cur = t; }\n"
        "    return cur;\n"
        "}\n"
        "function rob_circular(nums) {\n"
        "    const nn = nums.length;\n"
        "    if (nn === 1) return nums[0]" + a + ";\n"
        "    const a1 = rob_line(nums.slice(0, nn-1));\n"
        "    const a2 = rob_line(nums.slice(1));\n"
        f"    return Math.max(a1, a2){a};\n"
        "}\n"
        "console.log(rob_circular(nums));\n"
    )


def _ts_robcirc_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function rob_line(nums: number[]): number {\n"
        "    let prev = 0, cur = 0;\n"
        "    for (const x of nums) { const t = Math.max(cur, prev+x); prev = cur; cur = t; }\n"
        "    return cur;\n"
        "}\n"
        "function rob_circular(nums: number[]): number {\n"
        "    const nn = nums.length;\n"
        "    if (nn === 1) return nums[0]" + a + ";\n"
        "    const a1 = rob_line(nums.slice(0, nn-1));\n"
        "    const a2 = rob_line(nums.slice(1));\n"
        f"    return Math.max(a1, a2){a};\n"
        "}\n"
        "console.log(rob_circular(nums));\n"
    )


def _java_robcirc_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] nums = new int[n]; for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "    System.out.println(rob_circular(nums));\n"
        "}\n"
        "static int robLine(int[] nums, int lo, int hi) {\n"
        "    int prev = 0, cur = 0;\n"
        "    for (int i=lo;i<=hi;i++) { int t = Math.max(cur, prev+nums[i]); prev = cur; cur = t; }\n"
        "    return cur;\n"
        "}\n"
        "static int rob_circular(int[] nums) {\n"
        "    int n = nums.length;\n"
        "    if (n == 1) return nums[0]" + a + ";\n"
        "    int a1 = robLine(nums, 0, n-2);\n"
        "    int a2 = robLine(nums, 1, n-1);\n"
        f"    return Math.max(a1, a2){a};\n"
        "} }\n"
    )


def _cpp_robcirc_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n"
        "int robLine(vector<int>& nums, int lo, int hi) {\n"
        "    int prev = 0, cur = 0;\n"
        "    for (int i=lo;i<=hi;i++) { int t = max(cur, prev+nums[i]); prev = cur; cur = t; }\n"
        "    return cur;\n"
        "}\n"
        "int rob_circular(vector<int>& nums) {\n"
        "    int n = nums.size();\n"
        "    if (n == 1) return nums[0]" + a + ";\n"
        "    int a1 = robLine(nums, 0, n-2);\n"
        "    int a2 = robLine(nums, 1, n-1);\n"
        f"    return max(a1, a2){a};\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> nums(n); for (int i=0;i<n;i++) cin>>nums[i]; cout << rob_circular(nums) << endl; return 0; }\n"
    )


def _csharp_robcirc_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] nums=new int[n]; for (int i=0;i<n;i++) nums[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(rob_circular(nums));\n"
        "}\n"
        "static int RobLine(int[] nums, int lo, int hi) {\n"
        "    int prev = 0, cur = 0;\n"
        "    for (int i=lo;i<=hi;i++) { int t = System.Math.Max(cur, prev+nums[i]); prev = cur; cur = t; }\n"
        "    return cur;\n"
        "}\n"
        "static int rob_circular(int[] nums) {\n"
        "    int n = nums.Length;\n"
        "    if (n == 1) return nums[0]" + a + ";\n"
        "    int a1 = RobLine(nums, 0, n-2);\n"
        "    int a2 = RobLine(nums, 1, n-1);\n"
        f"    return System.Math.Max(a1, a2){a};\n"
        "} }\n"
    )


def _perl_robcirc_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @nums = @data[0..$n-1];\n"
        "sub rob_line {\n"
        "    my ($nums, $lo, $hi) = @_;\n"
        "    my $prev = 0; my $cur = 0;\n"
        "    for (my $i=$lo;$i<=$hi;$i++) { my $t = ($cur > $prev+$nums->[$i]) ? $cur : $prev+$nums->[$i]; $prev = $cur; $cur = $t; }\n"
        "    return $cur;\n"
        "}\n"
        "sub rob_circular {\n"
        "    my ($nums) = @_;\n"
        "    my $nn = scalar(@$nums);\n"
        "    return (${\\ $nums->[0]}" + a + ") if $nn == 1;\n"
        "    my $a1 = rob_line($nums, 0, $nn-2);\n"
        "    my $a2 = rob_line($nums, 1, $nn-1);\n"
        f"    return (($a1 > $a2) ? $a1 : $a2){a};\n"
        "}\n"
        "print rob_circular(\\@nums), \"\\n\";\n"
    )


def _c_robcirc_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int rob_line(int* nums, int lo, int hi) {\n"
        "    int prev = 0, cur = 0;\n"
        "    for (int i=lo;i<=hi;i++) { int t = (cur > prev+nums[i]) ? cur : prev+nums[i]; prev = cur; cur = t; }\n"
        "    return cur;\n"
        "}\n"
        "int rob_circular(int* nums, int n) {\n"
        "    if (n == 1) return nums[0]" + a + ";\n"
        "    int a1 = rob_line(nums, 0, n-2);\n"
        "    int a2 = rob_line(nums, 1, n-1);\n"
        f"    return (a1 > a2 ? a1 : a2){a};\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* nums=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&nums[i]);\n"
        "    printf(\"%d\\n\", rob_circular(nums, n));\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_robcirc_p(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn rob_line(nums: &Vec<i32>, lo: usize, hi: usize) -> i32 {\n"
        "    let mut prev = 0; let mut cur = 0;\n"
        "    for i in lo..=hi { let t = cur.max(prev+nums[i]); prev = cur; cur = t; }\n"
        "    cur\n"
        "}\n"
        "fn rob_circular(nums: &Vec<i32>) -> i32 {\n"
        "    let n = nums.len();\n"
        "    if n == 1 { return nums[0]" + a + "; }\n"
        "    let a1 = rob_line(nums, 0, n-2);\n"
        "    let a2 = rob_line(nums, 1, n-1);\n"
        f"    a1.max(a2){a}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    println!(\"{}\", rob_circular(&nums)); }\n"
    )


_BUILDERS = {
    "activity-selection": {"javascript": _js_activity_p, "typescript": _ts_activity_p, "java": _java_activity_p, "cpp": _cpp_activity_p,
                          "csharp": _csharp_activity_p, "perl": _perl_activity_p, "c": _c_activity_p, "rust": _rust_activity_p},
    "closest-pair": {"javascript": _js_closest_p, "typescript": _ts_closest_p, "java": _java_closest_p, "cpp": _cpp_closest_p,
                     "csharp": _csharp_closest_p, "perl": _perl_closest_p, "c": _c_closest_p, "rust": _rust_closest_p},
    "collatz": {"javascript": _js_collatz_p, "typescript": _ts_collatz_p, "java": _java_collatz_p, "cpp": _cpp_collatz_p,
               "csharp": _csharp_collatz_p, "perl": _perl_collatz_p, "c": _c_collatz_p, "rust": _rust_collatz_p},
    "counting-inversions": {"javascript": _js_countinv_p, "typescript": _ts_countinv_p, "java": _java_countinv_p, "cpp": _cpp_countinv_p,
                            "csharp": _csharp_countinv_p, "perl": _perl_countinv_p, "c": _c_countinv_p, "rust": _rust_countinv_p},
    "egg-drop": {"javascript": _js_eggdrop_p, "typescript": _ts_eggdrop_p, "java": _java_eggdrop_p, "cpp": _cpp_eggdrop_p,
                "csharp": _csharp_eggdrop_p, "perl": _perl_eggdrop_p, "c": _c_eggdrop_p, "rust": _rust_eggdrop_p},
    "euler-totient": {"javascript": _js_totient_p, "typescript": _ts_totient_p, "java": _java_totient_p, "cpp": _cpp_totient_p,
                      "csharp": _csharp_totient_p, "perl": _perl_totient_p, "c": _c_totient_p, "rust": _rust_totient_p},
    "gas-station": {"javascript": _js_gasstation_p, "typescript": _ts_gasstation_p, "java": _java_gasstation_p, "cpp": _cpp_gasstation_p,
                    "csharp": _csharp_gasstation_p, "perl": _perl_gasstation_p, "c": _c_gasstation_p, "rust": _rust_gasstation_p},
    "insert-interval": {"javascript": _js_insertint_p, "typescript": _ts_insertint_p, "java": _java_insertint_p, "cpp": _cpp_insertint_p,
                        "csharp": _csharp_insertint_p, "perl": _perl_insertint_p, "c": _c_insertint_p, "rust": _rust_insertint_p},
    "first-occurrence": {"javascript": _js_firstocc_p, "typescript": _ts_firstocc_p, "java": _java_firstocc_p, "cpp": _cpp_firstocc_p,
                         "csharp": _csharp_firstocc_p, "perl": _perl_firstocc_p, "c": _c_firstocc_p, "rust": _rust_firstocc_p},
    "house-robber-circular": {"javascript": _js_robcirc_p, "typescript": _ts_robcirc_p, "java": _java_robcirc_p, "cpp": _cpp_robcirc_p,
                              "csharp": _csharp_robcirc_p, "perl": _perl_robcirc_p, "c": _c_robcirc_p, "rust": _rust_robcirc_p},
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
        for lang in _TARGET_LANGUAGES:
            cases, tsv = load_cases(con, pid)
            if ledger.already_verified(con, pid, lang, "program", test_suite_version=tsv):
                skipped += 1
                continue
            r = await verify_one(pid, lang, cases, builders[lang])
            results.append(r)
            status = "PASS" if r["outcome"] == "verified" else "FAIL"
            print(f"[{status}] {lang:10s}(program) {pid:24s} {r['outcome']:18s} {r['detail'][:130]}", flush=True)
            if r["outcome"] == "verified":
                row = con.execute("SELECT starter_code FROM problems WHERE id=?", (pid,)).fetchone()
                sc = json.loads(row["starter_code"])
                sc[lang] = builders[lang](False)
                con.execute("UPDATE problems SET starter_code=? WHERE id=?", (json.dumps(sc), pid))
                con.commit()
                ledger.record_cell(con, problem_id=pid, language=lang, mode="program",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=f"{lang}-program-greedy-math-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
