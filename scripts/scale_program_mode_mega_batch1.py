"""Program Mode gap closure, mega batch 1: 41 problems that are already
Level-6 Function Mode across all 8 core languages (javascript, typescript,
java, cpp, csharp, perl, c, rust) but had zero Program Mode coverage.

Rather than hand-writing 41*8 full programs (read + function + print
boilerplate repeated verbatim), this script factors the I/O contract into
4 shapes (arr1, arr1_int, int1/int2/int3) that cover every problem in this
batch, and generates the read/print harness from the shape. Only the core
algorithm body is hand-written per (problem, language) -- the harness
appends `return result;` (or `return $result;` for Perl) automatically, so
every body's job is just to compute a local `result`.

Pattern: for each (problem, language), run the correct body on the full
40-case corpus (must pass all), then run with a genuric wrong-adjustment
(+1 for int results, negation for bool results) that must fail at least
one case. Only Level 6 when both hold -- mirrors every prior scale_*.py.
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
LANGS = ["javascript", "typescript", "java", "cpp", "csharp", "perl", "c", "rust"]

RETTYPE_INT = {"javascript": "", "typescript": "number", "java": "long", "cpp": "long long",
               "csharp": "long", "perl": "", "c": "long long", "rust": "i64"}
RETTYPE_BOOL = {"javascript": "", "typescript": "boolean", "java": "boolean", "cpp": "bool",
                 "csharp": "bool", "perl": "", "c": "int", "rust": "bool"}


def rettype(lang, kind):
    return RETTYPE_INT[lang] if kind == "int" else RETTYPE_BOOL[lang]


def sig(lang, shape, fn, kind):
    rt = rettype(lang, kind)
    if shape == "arr1":
        if lang == "javascript": return f"function {fn}(nums) {{"
        if lang == "typescript": return f"function {fn}(nums: number[]): {rt} {{"
        if lang == "java": return f"static {rt} {fn}(int[] nums) {{"
        if lang == "cpp": return f"{rt} {fn}(vector<int>& nums) {{"
        if lang == "csharp": return f"static {rt} {fn}(int[] nums) {{"
        if lang == "perl": return f"sub {fn} {{ my ($nums) = @_;"
        if lang == "c": return f"{rt} {fn}(int* nums, int n) {{"
        if lang == "rust": return f"fn {fn}(nums: &Vec<i32>) -> {rt} {{"
    if shape == "arr1_int":
        if lang == "javascript": return f"function {fn}(nums, extra) {{"
        if lang == "typescript": return f"function {fn}(nums: number[], extra: number): {rt} {{"
        if lang == "java": return f"static {rt} {fn}(int[] nums, int extra) {{"
        if lang == "cpp": return f"{rt} {fn}(vector<int>& nums, int extra) {{"
        if lang == "csharp": return f"static {rt} {fn}(int[] nums, int extra) {{"
        if lang == "perl": return f"sub {fn} {{ my ($nums, $extra) = @_;"
        if lang == "c": return f"{rt} {fn}(int* nums, int n, int extra) {{"
        if lang == "rust": return f"fn {fn}(nums: &Vec<i32>, extra: i32) -> {rt} {{"
    if shape == "int1":
        if lang == "javascript": return f"function {fn}(n) {{"
        if lang == "typescript": return f"function {fn}(n: number): {rt} {{"
        if lang == "java": return f"static {rt} {fn}(long n) {{"
        if lang == "cpp": return f"{rt} {fn}(long long n) {{"
        if lang == "csharp": return f"static {rt} {fn}(long n) {{"
        if lang == "perl": return f"sub {fn} {{ my ($n) = @_;"
        if lang == "c": return f"{rt} {fn}(long long n) {{"
        if lang == "rust": return f"fn {fn}(n: i64) -> {rt} {{"
    if shape == "int2":
        if lang == "javascript": return f"function {fn}(a, b) {{"
        if lang == "typescript": return f"function {fn}(a: number, b: number): {rt} {{"
        if lang == "java": return f"static {rt} {fn}(long a, long b) {{"
        if lang == "cpp": return f"{rt} {fn}(long long a, long long b) {{"
        if lang == "csharp": return f"static {rt} {fn}(long a, long b) {{"
        if lang == "perl": return f"sub {fn} {{ my ($a, $b) = @_;"
        if lang == "c": return f"{rt} {fn}(long long a, long long b) {{"
        if lang == "rust": return f"fn {fn}(a: i64, b: i64) -> {rt} {{"
    if shape == "int3":
        if lang == "javascript": return f"function {fn}(a, b, c) {{"
        if lang == "typescript": return f"function {fn}(a: number, b: number, c: number): {rt} {{"
        if lang == "java": return f"static {rt} {fn}(long a, long b, long c) {{"
        if lang == "cpp": return f"{rt} {fn}(long long a, long long b, long long c) {{"
        if lang == "csharp": return f"static {rt} {fn}(long a, long b, long c) {{"
        if lang == "perl": return f"sub {fn} {{ my ($a, $b, $c) = @_;"
        if lang == "c": return f"{rt} {fn}(long long a, long long b, long long c) {{"
        if lang == "rust": return f"fn {fn}(a: i64, b: i64, c: i64) -> {rt} {{"
    raise ValueError(shape)


def read_code(lang, shape):
    if shape == "arr1":
        if lang in ("javascript", "typescript"):
            return ("const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                     "const n = data[0]; const nums = data.slice(1,1+n);")
        if lang == "java":
            return "Scanner sc = new Scanner(System.in);\nint n = sc.nextInt();\nint[] nums = new int[n];\nfor (int i=0;i<n;i++) nums[i]=sc.nextInt();"
        if lang == "cpp":
            return "int n; cin >> n;\nvector<int> nums(n);\nfor (int i=0;i<n;i++) cin >> nums[i];"
        if lang == "csharp":
            return ("var tokens = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, "
                     "System.StringSplitOptions.RemoveEmptyEntries);\nint idx = 0;\nint n = int.Parse(tokens[idx++]);\n"
                     "int[] nums = new int[n];\nfor (int i=0;i<n;i++) nums[i]=int.Parse(tokens[idx++]);")
        if lang == "perl":
            return "my @data = split ' ', do { local $/; <STDIN> };\nmy $n = shift @data;\nmy @nums = @data[0..$n-1];"
        if lang == "c":
            return ("int n; scanf(\"%d\", &n);\nint* nums = (int*)malloc(sizeof(int) * (n > 0 ? n : 1));\n"
                     "for (int i=0;i<n;i++) scanf(\"%d\", &nums[i]);")
        if lang == "rust":
            return ("let mut input = String::new();\nstd::io::stdin().read_to_string(&mut input).unwrap();\n"
                     "let mut it = input.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
                     "let n = it.next().unwrap() as usize;\nlet nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();")
    if shape == "arr1_int":
        base = read_code(lang, "arr1")
        extra_line = {
            "javascript": "const extra = data[1+n];",
            "typescript": "const extra = data[1+n];",
            "java": "int extra = sc.nextInt();",
            "cpp": "int extra; cin >> extra;",
            "csharp": "int extra = int.Parse(tokens[idx++]);",
            "perl": "my $extra = $data[$n];",
            "c": "int extra; scanf(\"%d\", &extra);",
            "rust": "let extra = it.next().unwrap();",
        }[lang]
        return base + "\n" + extra_line
    if shape == "int1":
        if lang in ("javascript", "typescript"):
            return "const n = parseInt(require('fs').readFileSync(0,'utf8').trim());"
        if lang == "java":
            return "Scanner sc = new Scanner(System.in);\nlong n = sc.nextLong();"
        if lang == "cpp":
            return "long long n; cin >> n;"
        if lang == "csharp":
            return "long n = long.Parse(System.Console.In.ReadToEnd().Trim());"
        if lang == "perl":
            return "my $n = do { local $/; <STDIN> };\n$n =~ s/^\\s+|\\s+$//g;"
        if lang == "c":
            return "long long n; scanf(\"%lld\", &n);"
        if lang == "rust":
            return "let mut input = String::new();\nstd::io::stdin().read_to_string(&mut input).unwrap();\nlet n: i64 = input.trim().parse().unwrap();"
    if shape == "int2":
        if lang in ("javascript", "typescript"):
            return "const __t = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\nconst a = __t[0], b = __t[1];"
        if lang == "java":
            return "Scanner sc = new Scanner(System.in);\nlong a = sc.nextLong(), b = sc.nextLong();"
        if lang == "cpp":
            return "long long a, b; cin >> a >> b;"
        if lang == "csharp":
            return ("var tokens = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, "
                     "System.StringSplitOptions.RemoveEmptyEntries);\nlong a = long.Parse(tokens[0]), b = long.Parse(tokens[1]);")
        if lang == "perl":
            return "my @data = split ' ', do { local $/; <STDIN> };\nmy ($a, $b) = @data;"
        if lang == "c":
            return "long long a, b; scanf(\"%lld %lld\", &a, &b);"
        if lang == "rust":
            return ("let mut input = String::new();\nstd::io::stdin().read_to_string(&mut input).unwrap();\n"
                     "let mut it = input.split_whitespace().map(|x| x.parse::<i64>().unwrap());\n"
                     "let a = it.next().unwrap();\nlet b = it.next().unwrap();")
    if shape == "int3":
        if lang in ("javascript", "typescript"):
            return "const __t = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\nconst a = __t[0], b = __t[1], c = __t[2];"
        if lang == "java":
            return "Scanner sc = new Scanner(System.in);\nlong a = sc.nextLong(), b = sc.nextLong(), c = sc.nextLong();"
        if lang == "cpp":
            return "long long a, b, c; cin >> a >> b >> c;"
        if lang == "csharp":
            return ("var tokens = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, "
                     "System.StringSplitOptions.RemoveEmptyEntries);\n"
                     "long a = long.Parse(tokens[0]), b = long.Parse(tokens[1]), c = long.Parse(tokens[2]);")
        if lang == "perl":
            return "my @data = split ' ', do { local $/; <STDIN> };\nmy ($a, $b, $c) = @data;"
        if lang == "c":
            return "long long a, b, c; scanf(\"%lld %lld %lld\", &a, &b, &c);"
        if lang == "rust":
            return ("let mut input = String::new();\nstd::io::stdin().read_to_string(&mut input).unwrap();\n"
                     "let mut it = input.split_whitespace().map(|x| x.parse::<i64>().unwrap());\n"
                     "let a = it.next().unwrap();\nlet b = it.next().unwrap();\nlet c = it.next().unwrap();")
    raise ValueError((lang, shape))


def call_args(lang, shape):
    if shape == "arr1":
        if lang == "perl": return "\\@nums"
        if lang == "c": return "nums, n"
        if lang == "rust": return "&nums"
        return "nums"
    if shape == "arr1_int":
        if lang == "perl": return "\\@nums, $extra"
        if lang == "c": return "nums, n, extra"
        if lang == "rust": return "&nums, extra"
        return "nums, extra"
    if shape == "int1":
        return "$n" if lang == "perl" else "n"
    if shape == "int2":
        return "$a, $b" if lang == "perl" else "a, b"
    if shape == "int3":
        return "$a, $b, $c" if lang == "perl" else "a, b, c"
    raise ValueError(shape)


def print_stmt(lang, kind, wrong):
    if kind == "int":
        delta = 1 if wrong else 0
        if lang in ("javascript", "typescript"): return f"console.log(result + {delta});"
        if lang == "java": return f"System.out.println(result + {delta}L);"
        if lang == "cpp": return f"cout << (result + {delta}LL) << endl;"
        if lang == "csharp": return f"System.Console.WriteLine(result + {delta}L);"
        if lang == "perl": return f"print(($result + {delta}), \"\\n\");"
        if lang == "c": return f"printf(\"%lld\\n\", (long long)(result + {delta}LL));"
        if lang == "rust": return f"println!(\"{{}}\", result + {delta}i64);"
    else:
        neg = "!" if wrong else ""
        if lang in ("javascript", "typescript"): return f"console.log({neg}result);"
        if lang == "java": return f"System.out.println({neg}result);"
        if lang == "cpp": return f"cout << boolalpha << ({neg}result) << endl;"
        if lang == "csharp": return f"System.Console.WriteLine(({neg}result) ? \"true\" : \"false\");"
        if lang == "perl":
            negp = "!" if wrong else ""
            return f"print(({negp}$result) ? \"true\" : \"false\", \"\\n\");"
        if lang == "c": return f"printf(\"%s\\n\", ({neg}result) ? \"true\" : \"false\");"
        if lang == "rust": return f"println!(\"{{}}\", {neg}result);"
    raise ValueError((lang, kind))


def assemble(lang, shape, fn, kind, body, wrong):
    read = read_code(lang, shape)
    signature = sig(lang, shape, fn, kind)
    args = call_args(lang, shape)
    ret = "return $result;" if lang == "perl" else "return result;"
    func = f"{signature}\n{body}\n{ret}\n}}"
    rt = rettype(lang, kind)
    p = print_stmt(lang, kind, wrong)

    if lang == "javascript" or lang == "typescript":
        call = f"const result = {fn}({args});"
        return f"{read}\n{func}\n{call}\n{p}\n"
    if lang == "java":
        call = f"{rt} result = {fn}({args});"
        return f"import java.util.*;\npublic class Main {{\npublic static void main(String[] args) {{\n{read}\n{call}\n{p}\n}}\n{func}\n}}\n"
    if lang == "cpp":
        call = f"{rt} result = {fn}({args});"
        return (f"#include <iostream>\n#include <vector>\n#include <algorithm>\n#include <cmath>\n"
                 f"#include <unordered_map>\n#include <climits>\n#include <deque>\n#include <set>\n#include <array>\n#include <cstdlib>\n"
                 f"using namespace std;\n\n{func}\n\nint main() {{\n{read}\n{call}\n{p}\nreturn 0;\n}}\n")
    if lang == "csharp":
        call = f"{rt} result = {fn}({args});"
        return f"using System;\nusing System.Collections.Generic;\nclass Program {{\nstatic void Main() {{\n{read}\n{call}\n{p}\n}}\n{func}\n}}\n"
    if lang == "perl":
        call = f"my $result = {fn}({args});"
        return f"{read}\n{func}\n{call}\n{p}\n"
    if lang == "c":
        call = f"{rt} result = {fn}({args});"
        return f"#include <stdio.h>\n#include <stdlib.h>\n#include <math.h>\n\n{func}\n\nint main() {{\n{read}\n{call}\n{p}\nreturn 0;\n}}\n"
    if lang == "rust":
        call = f"let result = {fn}({args});"
        return f"use std::io::Read;\n\n{func}\n\nfn main() {{\n{read}\n{call}\n{p}\n}}\n"
    raise ValueError(lang)


# ---------------------------------------------------------------------------
# Per-problem: (shape, function_name, return_kind, {lang: body})
# body computes local `result` (matching the shape's declared return type);
# the harness appends `return result;` after it.
# ---------------------------------------------------------------------------

PROBLEMS: dict[str, dict] = {}


def add(pid, shape, fn, kind, bodies):
    PROBLEMS[pid] = {"shape": shape, "fn": fn, "kind": kind, "bodies": bodies}


add("bitonic-peak-index", "arr1", "peak_index", "int", {
    "javascript": "let lo = 0, hi = nums.length - 1;\nwhile (lo < hi) { const mid = (lo + hi) >> 1; if (nums[mid] < nums[mid+1]) lo = mid + 1; else hi = mid; }\nlet result = lo;",
    "typescript": "let lo = 0, hi = nums.length - 1;\nwhile (lo < hi) { const mid = (lo + hi) >> 1; if (nums[mid] < nums[mid+1]) lo = mid + 1; else hi = mid; }\nlet result: number = lo;",
    "java": "int lo = 0, hi = nums.length - 1;\nwhile (lo < hi) { int mid = (lo + hi) / 2; if (nums[mid] < nums[mid+1]) lo = mid + 1; else hi = mid; }\nlong result = lo;",
    "cpp": "int lo = 0, hi = (int)nums.size() - 1;\nwhile (lo < hi) { int mid = (lo + hi) / 2; if (nums[mid] < nums[mid+1]) lo = mid + 1; else hi = mid; }\nlong long result = lo;",
    "csharp": "int lo = 0, hi = nums.Length - 1;\nwhile (lo < hi) { int mid = (lo + hi) / 2; if (nums[mid] < nums[mid+1]) lo = mid + 1; else hi = mid; }\nlong result = lo;",
    "perl": "my $lo = 0; my $hi = scalar(@$nums) - 1;\nwhile ($lo < $hi) { my $mid = int(($lo + $hi) / 2); if ($nums->[$mid] < $nums->[$mid+1]) { $lo = $mid + 1; } else { $hi = $mid; } }\nmy $result = $lo;",
    "c": "int lo = 0, hi = n - 1;\nwhile (lo < hi) { int mid = (lo + hi) / 2; if (nums[mid] < nums[mid+1]) lo = mid + 1; else hi = mid; }\nlong long result = lo;",
    "rust": "let mut lo: i64 = 0; let mut hi: i64 = nums.len() as i64 - 1;\nwhile lo < hi { let mid = (lo + hi) / 2; if nums[mid as usize] < nums[(mid+1) as usize] { lo = mid + 1; } else { hi = mid; } }\nlet result: i64 = lo;",
})

add("find-minimum-rotated-sorted-array", "arr1", "find_min", "int", {
    "javascript": "let lo = 0, hi = nums.length - 1;\nwhile (lo < hi) { const mid = (lo + hi) >> 1; if (nums[mid] > nums[hi]) lo = mid + 1; else hi = mid; }\nlet result = nums[lo];",
    "typescript": "let lo = 0, hi = nums.length - 1;\nwhile (lo < hi) { const mid = (lo + hi) >> 1; if (nums[mid] > nums[hi]) lo = mid + 1; else hi = mid; }\nlet result: number = nums[lo];",
    "java": "int lo = 0, hi = nums.length - 1;\nwhile (lo < hi) { int mid = (lo + hi) / 2; if (nums[mid] > nums[hi]) lo = mid + 1; else hi = mid; }\nlong result = nums[lo];",
    "cpp": "int lo = 0, hi = (int)nums.size() - 1;\nwhile (lo < hi) { int mid = (lo + hi) / 2; if (nums[mid] > nums[hi]) lo = mid + 1; else hi = mid; }\nlong long result = nums[lo];",
    "csharp": "int lo = 0, hi = nums.Length - 1;\nwhile (lo < hi) { int mid = (lo + hi) / 2; if (nums[mid] > nums[hi]) lo = mid + 1; else hi = mid; }\nlong result = nums[lo];",
    "perl": "my $lo = 0; my $hi = scalar(@$nums) - 1;\nwhile ($lo < $hi) { my $mid = int(($lo + $hi) / 2); if ($nums->[$mid] > $nums->[$hi]) { $lo = $mid + 1; } else { $hi = $mid; } }\nmy $result = $nums->[$lo];",
    "c": "int lo = 0, hi = n - 1;\nwhile (lo < hi) { int mid = (lo + hi) / 2; if (nums[mid] > nums[hi]) lo = mid + 1; else hi = mid; }\nlong long result = nums[lo];",
    "rust": "let mut lo: i64 = 0; let mut hi: i64 = nums.len() as i64 - 1;\nwhile lo < hi { let mid = (lo + hi) / 2; if nums[mid as usize] > nums[hi as usize] { lo = mid + 1; } else { hi = mid; } }\nlet result: i64 = nums[lo as usize] as i64;",
})

add("count-occurrences-sorted", "arr1_int", "count_occurrences", "int", {
    "javascript": "function lb(t){let lo=0,hi=nums.length;while(lo<hi){const m=(lo+hi)>>1;if(nums[m]<t)lo=m+1;else hi=m;}return lo;}\nlet result = lb(extra+1) - lb(extra);",
    "typescript": "const lb=(t:number):number=>{let lo=0,hi=nums.length;while(lo<hi){const m=(lo+hi)>>1;if(nums[m]<t)lo=m+1;else hi=m;}return lo;};\nlet result: number = lb(extra+1) - lb(extra);",
    "java": "long result = 0;\nfor (int x : nums) if (x == extra) result++;",
    "cpp": "long long result = 0;\nfor (int x : nums) if (x == extra) result++;",
    "csharp": "long result = 0;\nforeach (int x in nums) if (x == extra) result++;",
    "perl": "my $result = 0;\nfor my $x (@$nums) { $result++ if $x == $extra; }",
    "c": "long long result = 0;\nfor (int i=0;i<n;i++) if (nums[i]==extra) result++;",
    "rust": "let result: i64 = nums.iter().filter(|&&x| x == extra).count() as i64;",
})

add("last-occurrence", "arr1_int", "last_occurrence", "int", {
    "javascript": "let lo=0,hi=nums.length-1,ans=-1;\nwhile(lo<=hi){const mid=(lo+hi)>>1;if(nums[mid]===extra){ans=mid;lo=mid+1;}else if(nums[mid]<extra)lo=mid+1;else hi=mid-1;}\nlet result = ans;",
    "typescript": "let lo=0,hi=nums.length-1,ans=-1;\nwhile(lo<=hi){const mid=(lo+hi)>>1;if(nums[mid]===extra){ans=mid;lo=mid+1;}else if(nums[mid]<extra)lo=mid+1;else hi=mid-1;}\nlet result: number = ans;",
    "java": "int lo=0,hi=nums.length-1,ans=-1;\nwhile(lo<=hi){int mid=(lo+hi)/2;if(nums[mid]==extra){ans=mid;lo=mid+1;}else if(nums[mid]<extra)lo=mid+1;else hi=mid-1;}\nlong result = ans;",
    "cpp": "int lo=0,hi=(int)nums.size()-1,ans=-1;\nwhile(lo<=hi){int mid=(lo+hi)/2;if(nums[mid]==extra){ans=mid;lo=mid+1;}else if(nums[mid]<extra)lo=mid+1;else hi=mid-1;}\nlong long result = ans;",
    "csharp": "int lo=0,hi=nums.Length-1,ans=-1;\nwhile(lo<=hi){int mid=(lo+hi)/2;if(nums[mid]==extra){ans=mid;lo=mid+1;}else if(nums[mid]<extra)lo=mid+1;else hi=mid-1;}\nlong result = ans;",
    "perl": "my $lo=0; my $hi=scalar(@$nums)-1; my $ans=-1;\nwhile($lo<=$hi){my $mid=int(($lo+$hi)/2);if($nums->[$mid]==$extra){$ans=$mid;$lo=$mid+1;}elsif($nums->[$mid]<$extra){$lo=$mid+1;}else{$hi=$mid-1;}}\nmy $result = $ans;",
    "c": "int lo=0,hi=n-1,ans=-1;\nwhile(lo<=hi){int mid=(lo+hi)/2;if(nums[mid]==extra){ans=mid;lo=mid+1;}else if(nums[mid]<extra)lo=mid+1;else hi=mid-1;}\nlong long result = ans;",
    "rust": "let mut lo: i64=0; let mut hi: i64 = nums.len() as i64 -1; let mut ans: i64=-1;\nwhile lo<=hi { let mid=(lo+hi)/2; if nums[mid as usize]==extra { ans=mid; lo=mid+1; } else if nums[mid as usize]<extra { lo=mid+1; } else { hi=mid-1; } }\nlet result: i64 = ans;",
})

add("koko-eating-bananas", "arr1_int", "min_eating_speed", "int", {
    "javascript": "function feas(sp){let h=0;for(const p of nums)h+=Math.ceil(p/sp);return h<=extra;}\nlet lo=1,hi=Math.max(...nums);\nwhile(lo<hi){const mid=(lo+hi)>>1;if(feas(mid))hi=mid;else lo=mid+1;}\nlet result=lo;",
    "typescript": "const feas=(sp:number):boolean=>{let h=0;for(const p of nums)h+=Math.ceil(p/sp);return h<=extra;};\nlet lo=1,hi=Math.max(...nums);\nwhile(lo<hi){const mid=(lo+hi)>>1;if(feas(mid))hi=mid;else lo=mid+1;}\nlet result: number=lo;",
    "java": "int hiV=0; for(int p: nums) hiV=Math.max(hiV,p);\nlong lo=1, hi=hiV;\nwhile(lo<hi){ long mid=(lo+hi)/2; long h=0; for(int p: nums) h += (p+mid-1)/mid; if(h<=extra) hi=mid; else lo=mid+1; }\nlong result = lo;",
    "cpp": "int hiV=0; for(int p: nums) hiV=max(hiV,p);\nlong long lo=1, hi=hiV;\nwhile(lo<hi){ long long mid=(lo+hi)/2; long long h=0; for(int p: nums) h += (p+mid-1)/mid; if(h<=extra) hi=mid; else lo=mid+1; }\nlong long result = lo;",
    "csharp": "int hiV=0; foreach(int p in nums) hiV=Math.Max(hiV,p);\nlong lo=1, hi=hiV;\nwhile(lo<hi){ long mid=(lo+hi)/2; long h=0; foreach(int p in nums) h += (p+mid-1)/mid; if(h<=extra) hi=mid; else lo=mid+1; }\nlong result = lo;",
    "perl": "my $hiV=0; for my $p (@$nums) { $hiV=$p if $p>$hiV; }\nmy $lo=1; my $hi=$hiV;\nwhile($lo<$hi){ my $mid=int(($lo+$hi)/2); my $h=0; for my $p (@$nums) { $h += int(($p+$mid-1)/$mid); } if($h<=$extra){$hi=$mid;} else {$lo=$mid+1;} }\nmy $result = $lo;",
    "c": "int hiV=0; for(int i=0;i<n;i++) if(nums[i]>hiV) hiV=nums[i];\nlong long lo=1, hi=hiV;\nwhile(lo<hi){ long long mid=(lo+hi)/2; long long h=0; for(int i=0;i<n;i++) h += (nums[i]+mid-1)/mid; if(h<=extra) hi=mid; else lo=mid+1; }\nlong long result = lo;",
    "rust": "let hiv = *nums.iter().max().unwrap() as i64;\nlet mut lo: i64 = 1; let mut hi: i64 = hiv;\nwhile lo < hi { let mid = (lo+hi)/2; let mut h: i64 = 0; for &p in nums.iter() { h += (p as i64 + mid - 1) / mid; } if h <= extra as i64 { hi = mid; } else { lo = mid + 1; } }\nlet result: i64 = lo;",
})

add("kth-largest-element", "arr1_int", "kth_largest", "int", {
    "javascript": "const s = [...nums].sort((a,b)=>b-a);\nlet result = s[extra-1];",
    "typescript": "const s = [...nums].sort((a,b)=>b-a);\nlet result: number = s[extra-1];",
    "java": "int[] s = nums.clone(); Arrays.sort(s);\nlong result = s[s.length-extra];",
    "cpp": "vector<int> s = nums; sort(s.begin(), s.end());\nlong long result = s[s.size()-extra];",
    "csharp": "int[] s = (int[])nums.Clone(); Array.Sort(s);\nlong result = s[s.Length-extra];",
    "perl": "my @s = sort { $a <=> $b } @$nums;\nmy $result = $s[scalar(@s)-$extra];",
    "c": "int* s = (int*)malloc(sizeof(int)*n); for(int i=0;i<n;i++) s[i]=nums[i];\nfor(int i=0;i<n;i++) for(int j=0;j<n-i-1;j++) if(s[j]>s[j+1]){int t=s[j];s[j]=s[j+1];s[j+1]=t;}\nlong long result = s[n-extra];",
    "rust": "let mut s = nums.clone(); s.sort();\nlet result: i64 = s[s.len()-(extra as usize)] as i64;",
})

add("largest-rectangle-in-histogram", "arr1", "largest_rectangle", "int", {
    "javascript": "const st=[]; let best=0; const h=[...nums,0];\nfor(let i=0;i<h.length;i++){ while(st.length && h[st[st.length-1]]>=h[i]){ const top=st.pop(); const width = st.length? i-st[st.length-1]-1 : i; best=Math.max(best, h[top]*width); } st.push(i); }\nlet result = best;",
    "typescript": "const st: number[]=[]; let best=0; const h=[...nums,0];\nfor(let i=0;i<h.length;i++){ while(st.length && h[st[st.length-1]]>=h[i]){ const top=st.pop()!; const width = st.length? i-st[st.length-1]-1 : i; best=Math.max(best, h[top]*width); } st.push(i); }\nlet result: number = best;",
    "java": "int m = nums.length; int[] h = new int[m+1]; for(int i=0;i<m;i++) h[i]=nums[i]; h[m]=0;\nint[] st = new int[m+2]; int sp=0; long best=0;\nfor(int i=0;i<=m;i++){ while(sp>0 && h[st[sp-1]]>=h[i]){ int top=st[--sp]; int width = sp>0? i-st[sp-1]-1 : i; best=Math.max(best,(long)h[top]*width); } st[sp++]=i; }\nlong result = best;",
    "cpp": "int m=(int)nums.size(); vector<int> h(nums); h.push_back(0);\nvector<int> st; long long best=0;\nfor(int i=0;i<(int)h.size();i++){ while(!st.empty() && h[st.back()]>=h[i]){ int top=st.back(); st.pop_back(); long long width = st.empty()? i : i-st.back()-1; best=max(best,(long long)h[top]*width); } st.push_back(i); }\nlong long result = best;",
    "csharp": "int m=nums.Length; int[] h=new int[m+1]; for(int i=0;i<m;i++) h[i]=nums[i]; h[m]=0;\nint[] st=new int[m+2]; int sp=0; long best=0;\nfor(int i=0;i<=m;i++){ while(sp>0 && h[st[sp-1]]>=h[i]){ int top=st[--sp]; int width = sp>0? i-st[sp-1]-1 : i; best=Math.Max(best,(long)h[top]*width); } st[sp++]=i; }\nlong result = best;",
    "perl": "my @h = (@$nums, 0); my @st=(); my $best=0;\nfor (my $i=0;$i<scalar(@h);$i++){ while(scalar(@st) && $h[$st[-1]]>=$h[$i]){ my $top=pop @st; my $width = scalar(@st) ? $i-$st[-1]-1 : $i; my $area=$h[$top]*$width; $best=$area if $area>$best; } push @st, $i; }\nmy $result = $best;",
    "c": "int m=n; int* h=(int*)malloc(sizeof(int)*(m+1)); for(int i=0;i<m;i++) h[i]=nums[i]; h[m]=0;\nint* st=(int*)malloc(sizeof(int)*(m+2)); int sp=0; long long best=0;\nfor(int i=0;i<=m;i++){ while(sp>0 && h[st[sp-1]]>=h[i]){ int top=st[--sp]; long long width = sp>0? i-st[sp-1]-1 : i; long long area=(long long)h[top]*width; if(area>best) best=area; } st[sp++]=i; }\nlong long result = best;",
    "rust": "let mut h: Vec<i64> = nums.iter().map(|&x| x as i64).collect(); h.push(0);\nlet mut st: Vec<i64> = Vec::new(); let mut best: i64 = 0;\nfor i in 0..h.len() as i64 { while let Some(&top) = st.last() { if h[top as usize] >= h[i as usize] { st.pop(); let width = if let Some(&p)=st.last() { i-p-1 } else { i }; let area = h[top as usize]*width; if area>best { best=area; } } else { break; } } st.push(i); }\nlet result: i64 = best;",
})

add("longest-bitonic-subsequence", "arr1", "longest_bitonic_subsequence", "int", {
    "javascript": "const m=nums.length; const inc=new Array(m).fill(1), dec=new Array(m).fill(1);\nfor(let i=0;i<m;i++) for(let j=0;j<i;j++) if(nums[j]<nums[i]) inc[i]=Math.max(inc[i],inc[j]+1);\nfor(let i=m-1;i>=0;i--) for(let j=m-1;j>i;j--) if(nums[j]<nums[i]) dec[i]=Math.max(dec[i],dec[j]+1);\nlet best=0; for(let i=0;i<m;i++) best=Math.max(best, inc[i]+dec[i]-1);\nlet result = best;",
    "typescript": "const m=nums.length; const inc=new Array(m).fill(1), dec=new Array(m).fill(1);\nfor(let i=0;i<m;i++) for(let j=0;j<i;j++) if(nums[j]<nums[i]) inc[i]=Math.max(inc[i],inc[j]+1);\nfor(let i=m-1;i>=0;i--) for(let j=m-1;j>i;j--) if(nums[j]<nums[i]) dec[i]=Math.max(dec[i],dec[j]+1);\nlet best=0; for(let i=0;i<m;i++) best=Math.max(best, inc[i]+dec[i]-1);\nlet result: number = best;",
    "java": "int m=nums.length; int[] inc=new int[m], dec=new int[m]; Arrays.fill(inc,1); Arrays.fill(dec,1);\nfor(int i=0;i<m;i++) for(int j=0;j<i;j++) if(nums[j]<nums[i]) inc[i]=Math.max(inc[i],inc[j]+1);\nfor(int i=m-1;i>=0;i--) for(int j=m-1;j>i;j--) if(nums[j]<nums[i]) dec[i]=Math.max(dec[i],dec[j]+1);\nlong best=0; for(int i=0;i<m;i++) best=Math.max(best, inc[i]+dec[i]-1);\nlong result = best;",
    "cpp": "int m=(int)nums.size(); vector<int> inc(m,1), dec(m,1);\nfor(int i=0;i<m;i++) for(int j=0;j<i;j++) if(nums[j]<nums[i]) inc[i]=max(inc[i],inc[j]+1);\nfor(int i=m-1;i>=0;i--) for(int j=m-1;j>i;j--) if(nums[j]<nums[i]) dec[i]=max(dec[i],dec[j]+1);\nlong long best=0; for(int i=0;i<m;i++) best=max(best,(long long)inc[i]+dec[i]-1);\nlong long result = best;",
    "csharp": "int m=nums.Length; int[] inc=new int[m], dec=new int[m]; for(int i=0;i<m;i++){inc[i]=1;dec[i]=1;}\nfor(int i=0;i<m;i++) for(int j=0;j<i;j++) if(nums[j]<nums[i]) inc[i]=Math.Max(inc[i],inc[j]+1);\nfor(int i=m-1;i>=0;i--) for(int j=m-1;j>i;j--) if(nums[j]<nums[i]) dec[i]=Math.Max(dec[i],dec[j]+1);\nlong best=0; for(int i=0;i<m;i++) best=Math.Max(best, inc[i]+dec[i]-1);\nlong result = best;",
    "perl": "my $m=scalar(@$nums); my @inc=(1) x $m; my @dec=(1) x $m;\nfor(my $i=0;$i<$m;$i++){ for(my $j=0;$j<$i;$j++){ if($nums->[$j]<$nums->[$i] && $inc[$j]+1>$inc[$i]){ $inc[$i]=$inc[$j]+1; } } }\nfor(my $i=$m-1;$i>=0;$i--){ for(my $j=$m-1;$j>$i;$j--){ if($nums->[$j]<$nums->[$i] && $dec[$j]+1>$dec[$i]){ $dec[$i]=$dec[$j]+1; } } }\nmy $best=0; for(my $i=0;$i<$m;$i++){ my $v=$inc[$i]+$dec[$i]-1; $best=$v if $v>$best; }\nmy $result=$best;",
    "c": "int m=n; int* inc=(int*)malloc(sizeof(int)*m); int* dec=(int*)malloc(sizeof(int)*m);\nfor(int i=0;i<m;i++){inc[i]=1;dec[i]=1;}\nfor(int i=0;i<m;i++) for(int j=0;j<i;j++) if(nums[j]<nums[i] && inc[j]+1>inc[i]) inc[i]=inc[j]+1;\nfor(int i=m-1;i>=0;i--) for(int j=m-1;j>i;j--) if(nums[j]<nums[i] && dec[j]+1>dec[i]) dec[i]=dec[j]+1;\nlong long best=0; for(int i=0;i<m;i++){ long long v=(long long)inc[i]+dec[i]-1; if(v>best) best=v; }\nlong long result = best;",
    "rust": "let m = nums.len(); let mut inc = vec![1i64; m]; let mut dec = vec![1i64; m];\nfor i in 0..m { for j in 0..i { if nums[j] < nums[i] && inc[j]+1 > inc[i] { inc[i] = inc[j]+1; } } }\nfor i in (0..m).rev() { for j in (i+1..m).rev() { if nums[j] < nums[i] && dec[j]+1 > dec[i] { dec[i] = dec[j]+1; } } }\nlet mut best: i64 = 0; for i in 0..m { let v = inc[i]+dec[i]-1; if v > best { best = v; } }\nlet result: i64 = best;",
})

add("max-consecutive-ones-with-k-flips", "arr1_int", "max_consecutive_ones", "int", {
    "javascript": "let left=0, zeros=0, best=0;\nfor(let right=0; right<nums.length; right++){ if(nums[right]===0) zeros++; while(zeros>extra){ if(nums[left]===0) zeros--; left++; } best=Math.max(best, right-left+1); }\nlet result = best;",
    "typescript": "let left=0, zeros=0, best=0;\nfor(let right=0; right<nums.length; right++){ if(nums[right]===0) zeros++; while(zeros>extra){ if(nums[left]===0) zeros--; left++; } best=Math.max(best, right-left+1); }\nlet result: number = best;",
    "java": "int left=0, zeros=0, best=0;\nfor(int right=0; right<nums.length; right++){ if(nums[right]==0) zeros++; while(zeros>extra){ if(nums[left]==0) zeros--; left++; } best=Math.max(best, right-left+1); }\nlong result = best;",
    "cpp": "int left=0, zeros=0, best=0;\nfor(int right=0; right<(int)nums.size(); right++){ if(nums[right]==0) zeros++; while(zeros>extra){ if(nums[left]==0) zeros--; left++; } best=max(best, right-left+1); }\nlong long result = best;",
    "csharp": "int left=0, zeros=0, best=0;\nfor(int right=0; right<nums.Length; right++){ if(nums[right]==0) zeros++; while(zeros>extra){ if(nums[left]==0) zeros--; left++; } best=Math.Max(best, right-left+1); }\nlong result = best;",
    "perl": "my $left=0; my $zeros=0; my $best=0;\nfor(my $right=0; $right<scalar(@$nums); $right++){ $zeros++ if $nums->[$right]==0; while($zeros>$extra){ $zeros-- if $nums->[$left]==0; $left++; } my $len=$right-$left+1; $best=$len if $len>$best; }\nmy $result = $best;",
    "c": "int left=0, zeros=0, best=0;\nfor(int right=0; right<n; right++){ if(nums[right]==0) zeros++; while(zeros>extra){ if(nums[left]==0) zeros--; left++; } if(right-left+1>best) best=right-left+1; }\nlong long result = best;",
    "rust": "let mut left = 0usize; let mut zeros = 0i32; let mut best = 0i64;\nfor right in 0..nums.len() { if nums[right]==0 { zeros += 1; } while zeros > extra { if nums[left]==0 { zeros -= 1; } left += 1; } let len = (right-left+1) as i64; if len > best { best = len; } }\nlet result: i64 = best;",
})

add("max-sum-subarray-fixed-k", "arr1_int", "max_sum_fixed_k", "int", {
    "javascript": "let sum=0; for(let i=0;i<extra;i++) sum+=nums[i];\nlet best=sum;\nfor(let i=extra;i<nums.length;i++){ sum += nums[i]-nums[i-extra]; best=Math.max(best,sum); }\nlet result = best;",
    "typescript": "let sum=0; for(let i=0;i<extra;i++) sum+=nums[i];\nlet best=sum;\nfor(let i=extra;i<nums.length;i++){ sum += nums[i]-nums[i-extra]; best=Math.max(best,sum); }\nlet result: number = best;",
    "java": "long sum=0; for(int i=0;i<extra;i++) sum+=nums[i];\nlong best=sum;\nfor(int i=extra;i<nums.length;i++){ sum += nums[i]-nums[i-extra]; best=Math.max(best,sum); }\nlong result = best;",
    "cpp": "long long sum=0; for(int i=0;i<extra;i++) sum+=nums[i];\nlong long best=sum;\nfor(int i=extra;i<(int)nums.size();i++){ sum += nums[i]-nums[i-extra]; best=max(best,sum); }\nlong long result = best;",
    "csharp": "long sum=0; for(int i=0;i<extra;i++) sum+=nums[i];\nlong best=sum;\nfor(int i=extra;i<nums.Length;i++){ sum += nums[i]-nums[i-extra]; best=Math.Max(best,sum); }\nlong result = best;",
    "perl": "my $sum=0; for(my $i=0;$i<$extra;$i++){ $sum+=$nums->[$i]; }\nmy $best=$sum;\nfor(my $i=$extra;$i<scalar(@$nums);$i++){ $sum += $nums->[$i]-$nums->[$i-$extra]; $best=$sum if $sum>$best; }\nmy $result = $best;",
    "c": "long long sum=0; for(int i=0;i<extra;i++) sum+=nums[i];\nlong long best=sum;\nfor(int i=extra;i<n;i++){ sum += nums[i]-nums[i-extra]; if(sum>best) best=sum; }\nlong long result = best;",
    "rust": "let k = extra as usize;\nlet mut sum: i64 = nums[0..k].iter().map(|&x| x as i64).sum();\nlet mut best = sum;\nfor i in k..nums.len() { sum += nums[i] as i64 - nums[i-k] as i64; if sum > best { best = sum; } }\nlet result: i64 = best;",
})

add("maximum-subarray-circular", "arr1", "max_subarray_circular", "int", {
    "javascript": "let total=0, maxCur=0, maxBest=-Infinity, minCur=0, minBest=Infinity;\nfor(const x of nums){ total+=x; maxCur=Math.max(x,maxCur+x); maxBest=Math.max(maxBest,maxCur); minCur=Math.min(x,minCur+x); minBest=Math.min(minBest,minCur); }\nlet result = maxBest<0 ? maxBest : Math.max(maxBest, total-minBest);",
    "typescript": "let total=0, maxCur=0, maxBest=-Infinity, minCur=0, minBest=Infinity;\nfor(const x of nums){ total+=x; maxCur=Math.max(x,maxCur+x); maxBest=Math.max(maxBest,maxCur); minCur=Math.min(x,minCur+x); minBest=Math.min(minBest,minCur); }\nlet result: number = maxBest<0 ? maxBest : Math.max(maxBest, total-minBest);",
    "java": "long total=0, maxCur=0, maxBest=Long.MIN_VALUE, minCur=0, minBest=Long.MAX_VALUE;\nfor(int x : nums){ total+=x; maxCur=Math.max(x,maxCur+x); maxBest=Math.max(maxBest,maxCur); minCur=Math.min(x,minCur+x); minBest=Math.min(minBest,minCur); }\nlong result = maxBest<0 ? maxBest : Math.max(maxBest, total-minBest);",
    "cpp": "long long total=0, maxCur=0, maxBest=LLONG_MIN, minCur=0, minBest=LLONG_MAX;\nfor(int x : nums){ total+=x; maxCur=max((long long)x,maxCur+x); maxBest=max(maxBest,maxCur); minCur=min((long long)x,minCur+x); minBest=min(minBest,minCur); }\nlong long result = maxBest<0 ? maxBest : max(maxBest, total-minBest);",
    "csharp": "long total=0, maxCur=0, maxBest=long.MinValue, minCur=0, minBest=long.MaxValue;\nforeach(int x in nums){ total+=x; maxCur=Math.Max(x,maxCur+x); maxBest=Math.Max(maxBest,maxCur); minCur=Math.Min(x,minCur+x); minBest=Math.Min(minBest,minCur); }\nlong result = maxBest<0 ? maxBest : Math.Max(maxBest, total-minBest);",
    "perl": "my $total=0; my $maxCur=0; my $maxBest=-9**9**9; my $minCur=0; my $minBest=9**9**9;\nfor my $x (@$nums){ $total+=$x; $maxCur = $x>$maxCur+$x ? $x : $maxCur+$x; $maxBest=$maxCur if $maxCur>$maxBest; $minCur = $x<$minCur+$x ? $x : $minCur+$x; $minBest=$minCur if $minCur<$minBest; }\nmy $result = $maxBest<0 ? $maxBest : ($maxBest > $total-$minBest ? $maxBest : $total-$minBest);",
    "c": "long long total=0, maxCur=0, maxBest=-9223372036854775807LL, minCur=0, minBest=9223372036854775807LL;\nfor(int i=0;i<n;i++){ int x=nums[i]; total+=x; maxCur = x>maxCur+x ? x : maxCur+x; if(maxCur>maxBest) maxBest=maxCur; minCur = x<minCur+x ? x : minCur+x; if(minCur<minBest) minBest=minCur; }\nlong long result = maxBest<0 ? maxBest : (maxBest>total-minBest?maxBest:total-minBest);",
    "rust": "let mut total: i64 = 0; let mut max_cur: i64 = 0; let mut max_best: i64 = i64::MIN; let mut min_cur: i64 = 0; let mut min_best: i64 = i64::MAX;\nfor &xx in nums.iter() { let x = xx as i64; total += x; max_cur = x.max(max_cur + x); max_best = max_best.max(max_cur); min_cur = x.min(min_cur + x); min_best = min_best.min(min_cur); }\nlet result: i64 = if max_best < 0 { max_best } else { max_best.max(total - min_best) };",
})

add("maximum-xor-of-two-numbers", "arr1", "find_maximum_xor", "int", {
    "javascript": "let best=0;\nfor(let i=0;i<nums.length;i++) for(let j=i+1;j<nums.length;j++) best=Math.max(best, nums[i]^nums[j]);\nlet result = best;",
    "typescript": "let best=0;\nfor(let i=0;i<nums.length;i++) for(let j=i+1;j<nums.length;j++) best=Math.max(best, nums[i]^nums[j]);\nlet result: number = best;",
    "java": "long best=0;\nfor(int i=0;i<nums.length;i++) for(int j=i+1;j<nums.length;j++) best=Math.max(best, (long)(nums[i]^nums[j]));\nlong result = best;",
    "cpp": "long long best=0;\nfor(int i=0;i<(int)nums.size();i++) for(int j=i+1;j<(int)nums.size();j++) best=max(best,(long long)(nums[i]^nums[j]));\nlong long result = best;",
    "csharp": "long best=0;\nfor(int i=0;i<nums.Length;i++) for(int j=i+1;j<nums.Length;j++) best=Math.Max(best,(long)(nums[i]^nums[j]));\nlong result = best;",
    "perl": "my $best=0;\nfor(my $i=0;$i<scalar(@$nums);$i++){ for(my $j=$i+1;$j<scalar(@$nums);$j++){ my $v=(0+$nums->[$i]) ^ (0+$nums->[$j]); $best=$v if $v>$best; } }\nmy $result = $best;",
    "c": "long long best=0;\nfor(int i=0;i<n;i++) for(int j=i+1;j<n;j++){ long long v = nums[i]^nums[j]; if(v>best) best=v; }\nlong long result = best;",
    "rust": "let mut best: i64 = 0;\nfor i in 0..nums.len() { for j in (i+1)..nums.len() { let v = (nums[i] ^ nums[j]) as i64; if v > best { best = v; } } }\nlet result: i64 = best;",
})

add("middle-of-linked-list", "arr1", "middle_node", "int", {
    "javascript": "let slow=0, fast=0; const m=nums.length;\nwhile(fast<m-1){ slow++; fast+=2; }\nlet result = nums[slow];",
    "typescript": "let slow=0, fast=0; const m=nums.length;\nwhile(fast<m-1){ slow++; fast+=2; }\nlet result: number = nums[slow];",
    "java": "int slow=0, fast=0, m=nums.length;\nwhile(fast<m-1){ slow++; fast+=2; }\nlong result = nums[slow];",
    "cpp": "int slow=0, fast=0, m=(int)nums.size();\nwhile(fast<m-1){ slow++; fast+=2; }\nlong long result = nums[slow];",
    "csharp": "int slow=0, fast=0, m=nums.Length;\nwhile(fast<m-1){ slow++; fast+=2; }\nlong result = nums[slow];",
    "perl": "my $slow=0; my $fast=0; my $m=scalar(@$nums);\nwhile($fast<$m-1){ $slow++; $fast+=2; }\nmy $result = $nums->[$slow];",
    "c": "int slow=0, fast=0, m=n;\nwhile(fast<m-1){ slow++; fast+=2; }\nlong long result = nums[slow];",
    "rust": "let mut slow: i64 = 0; let mut fast: i64 = 0; let m = nums.len() as i64;\nwhile fast < m-1 { slow += 1; fast += 2; }\nlet result: i64 = nums[slow as usize] as i64;",
})

add("min-subarray-len-target-sum", "arr1_int", "min_subarray_len", "int", {
    "javascript": "let left=0, sum=0, best=Infinity;\nfor(let right=0; right<nums.length; right++){ sum+=nums[right]; while(sum>=extra){ best=Math.min(best, right-left+1); sum-=nums[left]; left++; } }\nlet result = best===Infinity ? 0 : best;",
    "typescript": "let left=0, sum=0, best=Infinity;\nfor(let right=0; right<nums.length; right++){ sum+=nums[right]; while(sum>=extra){ best=Math.min(best, right-left+1); sum-=nums[left]; left++; } }\nlet result: number = best===Infinity ? 0 : best;",
    "java": "int left=0; long sum=0; long best=Long.MAX_VALUE;\nfor(int right=0; right<nums.length; right++){ sum+=nums[right]; while(sum>=extra){ best=Math.min(best, right-left+1); sum-=nums[left]; left++; } }\nlong result = best==Long.MAX_VALUE ? 0 : best;",
    "cpp": "int left=0; long long sum=0; long long best=LLONG_MAX;\nfor(int right=0; right<(int)nums.size(); right++){ sum+=nums[right]; while(sum>=extra){ best=min(best,(long long)(right-left+1)); sum-=nums[left]; left++; } }\nlong long result = best==LLONG_MAX ? 0 : best;",
    "csharp": "int left=0; long sum=0; long best=long.MaxValue;\nfor(int right=0; right<nums.Length; right++){ sum+=nums[right]; while(sum>=extra){ best=Math.Min(best, right-left+1); sum-=nums[left]; left++; } }\nlong result = best==long.MaxValue ? 0 : best;",
    "perl": "my $left=0; my $sum=0; my $best=9**9**9;\nfor(my $right=0; $right<scalar(@$nums); $right++){ $sum+=$nums->[$right]; while($sum>=$extra){ my $len=$right-$left+1; $best=$len if $len<$best; $sum-=$nums->[$left]; $left++; } }\nmy $result = ($best == 9**9**9) ? 0 : $best;",
    "c": "int left=0; long long sum=0; long long best=9223372036854775807LL;\nfor(int right=0; right<n; right++){ sum+=nums[right]; while(sum>=extra){ long long len=right-left+1; if(len<best) best=len; sum-=nums[left]; left++; } }\nlong long result = (best==9223372036854775807LL) ? 0 : best;",
    "rust": "let mut left = 0usize; let mut sum: i64 = 0; let mut best: i64 = i64::MAX;\nfor right in 0..nums.len() { sum += nums[right] as i64; while sum >= extra as i64 { let len = (right-left+1) as i64; if len < best { best = len; } sum -= nums[left] as i64; left += 1; } }\nlet result: i64 = if best == i64::MAX { 0 } else { best };",
})

add("partition-equal-subset-sum", "arr1", "can_partition", "bool", {
    "javascript": "const total = nums.reduce((a,b)=>a+b,0);\nlet result;\nif (total % 2 !== 0) { result = false; } else { const target = total/2; const dp = new Array(target+1).fill(false); dp[0]=true; for (const x of nums) { for (let j=target; j>=x; j--) { if (dp[j-x]) dp[j]=true; } } result = dp[target]; }",
    "typescript": "const total = nums.reduce((a,b)=>a+b,0);\nlet result: boolean;\nif (total % 2 !== 0) { result = false; } else { const target = total/2; const dp = new Array(target+1).fill(false); dp[0]=true; for (const x of nums) { for (let j=target; j>=x; j--) { if (dp[j-x]) dp[j]=true; } } result = dp[target]; }",
    "java": "long total=0; for (int x: nums) total+=x;\nboolean result;\nif (total % 2 != 0) { result = false; } else { int target=(int)(total/2); boolean[] dp=new boolean[target+1]; dp[0]=true; for (int x: nums) { for (int j=target;j>=x;j--) { if (dp[j-x]) dp[j]=true; } } result = dp[target]; }",
    "cpp": "long long total=0; for (int x: nums) total+=x;\nbool result;\nif (total % 2 != 0) { result = false; } else { int target=(int)(total/2); vector<char> dp(target+1,0); dp[0]=1; for (int x: nums) { for (int j=target;j>=x;j--) { if (dp[j-x]) dp[j]=1; } } result = dp[target]!=0; }",
    "csharp": "long total=0; foreach (int x in nums) total+=x;\nbool result;\nif (total % 2 != 0) { result = false; } else { int target=(int)(total/2); bool[] dp=new bool[target+1]; dp[0]=true; foreach (int x in nums) { for (int j=target;j>=x;j--) { if (dp[j-x]) dp[j]=true; } } result = dp[target]; }",
    "perl": "my $total=0; for my $x (@$nums) { $total+=$x; }\nmy $result;\nif ($total % 2 != 0) { $result = 0; } else { my $target=$total/2; my @dp=(0) x ($target+1); $dp[0]=1; for my $x (@$nums) { for (my $j=$target; $j>=$x; $j--) { $dp[$j]=1 if $dp[$j-$x]; } } $result = $dp[$target]; }",
    "c": "long long total=0; for(int i=0;i<n;i++) total+=nums[i];\nint result;\nif (total % 2 != 0) { result = 0; } else { int target=(int)(total/2); char* dp=(char*)calloc(target+1,1); dp[0]=1; for(int i=0;i<n;i++){ int x=nums[i]; for(int j=target;j>=x;j--){ if(dp[j-x]) dp[j]=1; } } result = dp[target]; }",
    "rust": "let total: i64 = nums.iter().map(|&x| x as i64).sum();\nlet result: bool;\nif total % 2 != 0 { result = false; } else { let target = (total/2) as usize; let mut dp = vec![false; target+1]; dp[0] = true; for &xx in nums.iter() { let x = xx as usize; for j in (x..=target).rev() { if dp[j-x] { dp[j] = true; } } } result = dp[target]; }",
})

add("perfect-squares-min-count", "int1", "num_squares", "int", {
    "javascript": "const N = n;\nconst dp = new Array(N+1).fill(Infinity); dp[0]=0;\nfor (let i=1;i<=N;i++){ for (let j=1;j*j<=i;j++){ dp[i]=Math.min(dp[i], dp[i-j*j]+1); } }\nlet result = dp[N];",
    "typescript": "const N: number = n;\nconst dp: number[] = new Array(N+1).fill(Infinity); dp[0]=0;\nfor (let i=1;i<=N;i++){ for (let j=1;j*j<=i;j++){ dp[i]=Math.min(dp[i], dp[i-j*j]+1); } }\nlet result: number = dp[N];",
    "java": "int N=(int)n;\nint[] dp=new int[N+1]; Arrays.fill(dp, Integer.MAX_VALUE/2); dp[0]=0;\nfor (int i=1;i<=N;i++){ for (int j=1;j*j<=i;j++){ dp[i]=Math.min(dp[i], dp[i-j*j]+1); } }\nlong result = dp[N];",
    "cpp": "int N=(int)n;\nvector<int> dp(N+1, INT_MAX/2); dp[0]=0;\nfor (int i=1;i<=N;i++){ for (int j=1;j*j<=i;j++){ dp[i]=min(dp[i], dp[i-j*j]+1); } }\nlong long result = dp[N];",
    "csharp": "int N=(int)n;\nint[] dp=new int[N+1]; for(int i=0;i<=N;i++) dp[i]=int.MaxValue/2; dp[0]=0;\nfor (int i=1;i<=N;i++){ for (int j=1;j*j<=i;j++){ dp[i]=Math.Min(dp[i], dp[i-j*j]+1); } }\nlong result = dp[N];",
    "perl": "my $N=$n;\nmy @dp=(1000000000) x ($N+1); $dp[0]=0;\nfor(my $i=1;$i<=$N;$i++){ for(my $j=1;$j*$j<=$i;$j++){ my $c=$dp[$i-$j*$j]+1; $dp[$i]=$c if $c<$dp[$i]; } }\nmy $result = $dp[$N];",
    "c": "int N=(int)n;\nint* dp=(int*)malloc(sizeof(int)*(N+1)); for(int i=0;i<=N;i++) dp[i]=1000000000; dp[0]=0;\nfor(int i=1;i<=N;i++){ for(int j=1;j*j<=i;j++){ if(dp[i-j*j]+1<dp[i]) dp[i]=dp[i-j*j]+1; } }\nlong long result = dp[N];",
    "rust": "let nn = n as usize;\nlet mut dp = vec![i64::MAX/2; nn+1]; dp[0] = 0;\nfor i in 1..=nn { let mut j = 1; while j*j <= i { if dp[i-j*j]+1 < dp[i] { dp[i] = dp[i-j*j]+1; } j += 1; } }\nlet result: i64 = dp[nn];",
})

add("rod-cutting", "arr1", "rod_cutting", "int", {
    "javascript": "const m = nums.length;\nconst dp = new Array(m+1).fill(0);\nfor (let i=1;i<=m;i++){ let best=-Infinity; for (let cut=1;cut<=i;cut++){ best=Math.max(best, nums[cut-1]+dp[i-cut]); } dp[i]=best; }\nlet result = dp[m];",
    "typescript": "const m: number = nums.length;\nconst dp: number[] = new Array(m+1).fill(0);\nfor (let i=1;i<=m;i++){ let best=-Infinity; for (let cut=1;cut<=i;cut++){ best=Math.max(best, nums[cut-1]+dp[i-cut]); } dp[i]=best; }\nlet result: number = dp[m];",
    "java": "int m=nums.length;\nlong[] dp=new long[m+1];\nfor (int i=1;i<=m;i++){ long best=Long.MIN_VALUE; for (int cut=1;cut<=i;cut++){ best=Math.max(best, nums[cut-1]+dp[i-cut]); } dp[i]=best; }\nlong result = dp[m];",
    "cpp": "int m=(int)nums.size();\nvector<long long> dp(m+1,0);\nfor (int i=1;i<=m;i++){ long long best=LLONG_MIN; for (int cut=1;cut<=i;cut++){ best=max(best,(long long)nums[cut-1]+dp[i-cut]); } dp[i]=best; }\nlong long result = dp[m];",
    "csharp": "int m=nums.Length;\nlong[] dp=new long[m+1];\nfor (int i=1;i<=m;i++){ long best=long.MinValue; for (int cut=1;cut<=i;cut++){ best=Math.Max(best, nums[cut-1]+dp[i-cut]); } dp[i]=best; }\nlong result = dp[m];",
    "perl": "my $m=scalar(@$nums);\nmy @dp=(0) x ($m+1);\nfor(my $i=1;$i<=$m;$i++){ my $best=-9**9**9; for(my $cut=1;$cut<=$i;$cut++){ my $v=$nums->[$cut-1]+$dp[$i-$cut]; $best=$v if $v>$best; } $dp[$i]=$best; }\nmy $result = $dp[$m];",
    "c": "int m=n;\nlong long* dp=(long long*)calloc(m+1,sizeof(long long));\nfor(int i=1;i<=m;i++){ long long best=-9223372036854775807LL; for(int cut=1;cut<=i;cut++){ long long v=(long long)nums[cut-1]+dp[i-cut]; if(v>best) best=v; } dp[i]=best; }\nlong long result = dp[m];",
    "rust": "let m = nums.len();\nlet mut dp = vec![0i64; m+1];\nfor i in 1..=m { let mut best = i64::MIN; for cut in 1..=i { let v = nums[cut-1] as i64 + dp[i-cut]; if v > best { best = v; } } dp[i] = best; }\nlet result: i64 = dp[m];",
})

add("single-number-ii", "arr1", "single_number", "int", {
    "javascript": "let result = 0;\nfor (let bit=0; bit<32; bit++){ let cnt=0; for (const x of nums) { const ux = x<0 ? x+4294967296 : x; cnt += Math.floor(ux/Math.pow(2,bit)) % 2; } if (cnt % 3 !== 0) result += Math.pow(2,bit); }\nif (result >= 2147483648) result -= 4294967296;",
    "typescript": "let result: number = 0;\nfor (let bit=0; bit<32; bit++){ let cnt=0; for (const x of nums) { const ux = x<0 ? x+4294967296 : x; cnt += Math.floor(ux/Math.pow(2,bit)) % 2; } if (cnt % 3 !== 0) result += Math.pow(2,bit); }\nif (result >= 2147483648) result -= 4294967296;",
    "java": "long result = 0;\nfor (int bit=0; bit<32; bit++){ long cnt=0; for (int x : nums) { long ux = x<0 ? (long)x+4294967296L : (long)x; cnt += (ux >> bit) & 1; } if (cnt % 3 != 0) result += (1L<<bit); }\nif (result >= 2147483648L) result -= 4294967296L;",
    "cpp": "long long result = 0;\nfor (int bit=0; bit<32; bit++){ long long cnt=0; for (int x : nums) { long long ux = x<0 ? (long long)x+4294967296LL : (long long)x; cnt += (ux >> bit) & 1; } if (cnt % 3 != 0) result += (1LL<<bit); }\nif (result >= 2147483648LL) result -= 4294967296LL;",
    "csharp": "long result = 0;\nfor (int bit=0; bit<32; bit++){ long cnt=0; foreach (int x in nums) { long ux = x<0 ? (long)x+4294967296L : (long)x; cnt += (ux >> bit) & 1; } if (cnt % 3 != 0) result += (1L<<bit); }\nif (result >= 2147483648L) result -= 4294967296L;",
    "perl": "my $result = 0;\nfor (my $bit=0; $bit<32; $bit++){ my $cnt=0; for my $x (@$nums) { my $ux = $x<0 ? $x+4294967296 : $x; $cnt += (int($ux / (2**$bit))) % 2; } if ($cnt % 3 != 0) { $result += 2**$bit; } }\nif ($result >= 2147483648) { $result -= 4294967296; }",
    "c": "long long result = 0;\nfor (int bit=0; bit<32; bit++){ long long cnt=0; for (int i=0;i<n;i++) { long long ux = nums[i]<0 ? (long long)nums[i]+4294967296LL : (long long)nums[i]; cnt += (ux >> bit) & 1; } if (cnt % 3 != 0) result += (1LL<<bit); }\nif (result >= 2147483648LL) result -= 4294967296LL;",
    "rust": "let mut result: i64 = 0;\nfor bit in 0..32 { let mut cnt: i64 = 0; for &x in nums.iter() { let ux: i64 = if x < 0 { x as i64 + 4294967296i64 } else { x as i64 }; cnt += (ux >> bit) & 1; } if cnt % 3 != 0 { result += 1i64 << bit; } }\nif result >= 2147483648i64 { result -= 4294967296i64; }",
})

add("subset-sum", "arr1_int", "subset_sum", "bool", {
    "javascript": "const dp = new Array(extra+1).fill(false); dp[0]=true;\nfor (const x of nums) { if (x<=extra) for (let j=extra; j>=x; j--) { if (dp[j-x]) dp[j]=true; } }\nlet result = extra>=0 ? dp[extra] : false;",
    "typescript": "const dp: boolean[] = new Array(extra+1).fill(false); dp[0]=true;\nfor (const x of nums) { if (x<=extra) for (let j=extra; j>=x; j--) { if (dp[j-x]) dp[j]=true; } }\nlet result: boolean = extra>=0 ? dp[extra] : false;",
    "java": "boolean[] dp=new boolean[extra+1]; dp[0]=true;\nfor (int x: nums) { if (x<=extra) for (int j=extra;j>=x;j--) { if (dp[j-x]) dp[j]=true; } }\nboolean result = extra>=0 && dp[extra];",
    "cpp": "vector<char> dp(extra+1,0); dp[0]=1;\nfor (int x: nums) { if (x<=extra) for (int j=extra;j>=x;j--) { if (dp[j-x]) dp[j]=1; } }\nbool result = extra>=0 && dp[extra]!=0;",
    "csharp": "bool[] dp=new bool[extra+1]; dp[0]=true;\nforeach (int x in nums) { if (x<=extra) for (int j=extra;j>=x;j--) { if (dp[j-x]) dp[j]=true; } }\nbool result = extra>=0 && dp[extra];",
    "perl": "my @dp=(0) x ($extra+1); $dp[0]=1;\nfor my $x (@$nums) { if ($x<=$extra) { for (my $j=$extra; $j>=$x; $j--) { $dp[$j]=1 if $dp[$j-$x]; } } }\nmy $result = ($extra>=0) && $dp[$extra];",
    "c": "char* dp=(char*)calloc(extra+1,1); dp[0]=1;\nfor(int i=0;i<n;i++){ int x=nums[i]; if(x<=extra) for(int j=extra;j>=x;j--){ if(dp[j-x]) dp[j]=1; } }\nint result = (extra>=0) && dp[extra];",
    "rust": "let target = extra as usize;\nlet mut dp = vec![false; target+1]; dp[0] = true;\nfor &xx in nums.iter() { let x = xx as usize; if x <= target { for j in (x..=target).rev() { if dp[j-x] { dp[j] = true; } } } }\nlet result: bool = dp[target];",
})

add("target-sum-ways", "arr1_int", "find_target_sum_ways", "int", {
    "javascript": "const total = nums.reduce((a,b)=>a+b,0);\nlet result;\nif ((total+extra) % 2 !== 0 || total < Math.abs(extra)) { result = 0; } else { const s = (total+extra)/2; const dp = new Array(s+1).fill(0); dp[0]=1; for (const x of nums) { for (let j=s;j>=x;j--) { dp[j]+=dp[j-x]; } } result = dp[s]; }",
    "typescript": "const total: number = nums.reduce((a,b)=>a+b,0);\nlet result: number;\nif ((total+extra) % 2 !== 0 || total < Math.abs(extra)) { result = 0; } else { const s = (total+extra)/2; const dp: number[] = new Array(s+1).fill(0); dp[0]=1; for (const x of nums) { for (let j=s;j>=x;j--) { dp[j]+=dp[j-x]; } } result = dp[s]; }",
    "java": "long total=0; for (int x: nums) total+=x;\nlong result;\nif ((total+extra) % 2 != 0 || total < Math.abs(extra)) { result = 0; } else { int s=(int)((total+extra)/2); long[] dp=new long[s+1]; dp[0]=1; for (int x: nums) { for (int j=s;j>=x;j--) { dp[j]+=dp[j-x]; } } result = dp[s]; }",
    "cpp": "long long total=0; for (int x: nums) total+=x;\nlong long result;\nif ((total+extra) % 2 != 0 || total < llabs((long long)extra)) { result = 0; } else { int s=(int)((total+extra)/2); vector<long long> dp(s+1,0); dp[0]=1; for (int x: nums) { for (int j=s;j>=x;j--) { dp[j]+=dp[j-x]; } } result = dp[s]; }",
    "csharp": "long total=0; foreach (int x in nums) total+=x;\nlong result;\nif ((total+extra) % 2 != 0 || total < Math.Abs(extra)) { result = 0; } else { int s=(int)((total+extra)/2); long[] dp=new long[s+1]; dp[0]=1; foreach (int x in nums) { for (int j=s;j>=x;j--) { dp[j]+=dp[j-x]; } } result = dp[s]; }",
    "perl": "my $total=0; for my $x (@$nums) { $total+=$x; }\nmy $result;\nif ((($total+$extra) % 2 != 0) || ($total < abs($extra))) { $result = 0; } else { my $s=($total+$extra)/2; my @dp=(0) x ($s+1); $dp[0]=1; for my $x (@$nums) { for (my $j=$s; $j>=$x; $j--) { $dp[$j]+=$dp[$j-$x]; } } $result = $dp[$s]; }",
    "c": "long long total=0; for(int i=0;i<n;i++) total+=nums[i];\nlong long result;\nlong long absExtra = extra<0 ? -extra : extra;\nif ((total+extra) % 2 != 0 || total < absExtra) { result = 0; } else { int s=(int)((total+extra)/2); long long* dp=(long long*)calloc(s+1,sizeof(long long)); dp[0]=1; for(int i=0;i<n;i++){ int x=nums[i]; for(int j=s;j>=x;j--){ dp[j]+=dp[j-x]; } } result = dp[s]; }",
    "rust": "let total: i64 = nums.iter().map(|&x| x as i64).sum();\nlet extra64 = extra as i64;\nlet result: i64;\nif (total+extra64) % 2 != 0 || total < extra64.abs() { result = 0; } else { let s = ((total+extra64)/2) as usize; let mut dp = vec![0i64; s+1]; dp[0] = 1; for &xx in nums.iter() { let x = xx as usize; for j in (x..=s).rev() { dp[j] += dp[j-x]; } } result = dp[s]; }",
})

add("two-sum-count-pairs", "arr1_int", "count_pairs", "int", {
    "javascript": "const freq = new Map();\nfor (const x of nums) freq.set(x, (freq.get(x)||0)+1);\nlet result = 0;\nfor (const [v,c] of freq) { const comp = extra - v; if (comp === v) { result += c*(c-1)/2; } else if (comp > v) { result += c * (freq.get(comp)||0); } }",
    "typescript": "const freq = new Map<number, number>();\nfor (const x of nums) freq.set(x, (freq.get(x)||0)+1);\nlet result: number = 0;\nfor (const [v,c] of freq) { const comp = extra - v; if (comp === v) { result += c*(c-1)/2; } else if (comp > v) { result += c * (freq.get(comp)||0); } }",
    "java": "Map<Integer,Integer> freq = new HashMap<>();\nfor (int x: nums) freq.merge(x, 1, Integer::sum);\nlong result = 0;\nfor (Map.Entry<Integer,Integer> e : freq.entrySet()) { int v=e.getKey(); long c=e.getValue(); long comp = extra - v; if (comp == v) { result += c*(c-1)/2; } else if (comp > v) { result += c * freq.getOrDefault((int)comp, 0); } }",
    "cpp": "unordered_map<int,long long> freq;\nfor (int x: nums) freq[x]++;\nlong long result = 0;\nfor (auto& e : freq) { long long v=e.first, c=e.second; long long comp = extra - v; if (comp == v) { result += c*(c-1)/2; } else if (comp > v) { auto it=freq.find((int)comp); if (it!=freq.end()) result += c * it->second; } }",
    "csharp": "var freq = new Dictionary<int,long>();\nforeach (int x in nums) { if (freq.ContainsKey(x)) freq[x]++; else freq[x]=1; }\nlong result = 0;\nforeach (var e in freq) { long v=e.Key, c=e.Value; long comp = extra - v; if (comp == v) { result += c*(c-1)/2; } else if (comp > v) { result += c * (freq.ContainsKey((int)comp) ? freq[(int)comp] : 0); } }",
    "perl": "my %freq;\nfor my $x (@$nums) { $freq{$x}++; }\nmy $result = 0;\nfor my $v (keys %freq) { my $c = $freq{$v}; my $comp = $extra - $v; if ($comp == $v) { $result += $c*($c-1)/2; } elsif ($comp > $v) { $result += $c * ($freq{$comp} // 0); } }",
    "c": "int result = 0;\nfor (int i=0;i<n;i++) for (int j=i+1;j<n;j++) if ((long long)nums[i]+nums[j]==extra) result++;\nlong long resultL = result;",
    "rust": "use std::collections::HashMap;\nlet mut freq: HashMap<i32,i64> = HashMap::new();\nfor &x in nums.iter() { *freq.entry(x).or_insert(0) += 1; }\nlet mut result: i64 = 0;\nfor (&v, &c) in freq.iter() { let comp = extra - v; if comp == v { result += c*(c-1)/2; } else if comp > v { if let Some(&c2) = freq.get(&comp) { result += c * c2; } } }",
})
# NOTE: the C body for two-sum-count-pairs sets `resultL`, not `result` -- fixed below.
PROBLEMS["two-sum-count-pairs"]["bodies"]["c"] = (
    "long long result = 0;\n"
    "for (int i=0;i<n;i++) for (int j=i+1;j<n;j++) if ((long long)nums[i]+nums[j]==extra) result++;"
)

add("unique-permutations-count", "arr1", "count_unique_permutations", "int", {
    "javascript": "const freq = new Map();\nfor (const x of nums) freq.set(x, (freq.get(x)||0)+1);\nconst fact = (k) => { let r=1; for (let i=2;i<=k;i++) r*=i; return r; };\nlet denom = 1;\nfor (const c of freq.values()) denom *= fact(c);\nlet result = fact(nums.length) / denom;",
    "typescript": "const freq = new Map<number, number>();\nfor (const x of nums) freq.set(x, (freq.get(x)||0)+1);\nconst fact = (k: number): number => { let r=1; for (let i=2;i<=k;i++) r*=i; return r; };\nlet denom = 1;\nfor (const c of freq.values()) denom *= fact(c);\nlet result: number = fact(nums.length) / denom;",
    "java": "Map<Integer,Integer> freq = new HashMap<>();\nfor (int x: nums) freq.merge(x, 1, Integer::sum);\nlong num = 1; for (int i=2;i<=nums.length;i++) num*=i;\nlong denom = 1;\nfor (int c : freq.values()) { long f=1; for (int i=2;i<=c;i++) f*=i; denom*=f; }\nlong result = num/denom;",
    "cpp": "unordered_map<int,int> freq;\nfor (int x: nums) freq[x]++;\nlong long num=1; for (int i=2;i<=(int)nums.size();i++) num*=i;\nlong long denom=1;\nfor (auto& e : freq) { long long f=1; for (int i=2;i<=e.second;i++) f*=i; denom*=f; }\nlong long result = num/denom;",
    "csharp": "var freq = new Dictionary<int,int>();\nforeach (int x in nums) { if (freq.ContainsKey(x)) freq[x]++; else freq[x]=1; }\nlong num=1; for (int i=2;i<=nums.Length;i++) num*=i;\nlong denom=1;\nforeach (var c in freq.Values) { long f=1; for (int i=2;i<=c;i++) f*=i; denom*=f; }\nlong result = num/denom;",
    "perl": "my %freq;\nfor my $x (@$nums) { $freq{$x}++; }\nmy $num=1; for (my $i=2;$i<=scalar(@$nums);$i++) { $num*=$i; }\nmy $denom=1;\nfor my $c (values %freq) { my $f=1; for (my $i=2;$i<=$c;$i++) { $f*=$i; } $denom*=$f; }\nmy $result = $num/$denom;",
    "c": "int vals[100]; int cnts[100]; int distinctN=0;\nfor(int i=0;i<n;i++){ int found=0; for(int j=0;j<distinctN;j++){ if(vals[j]==nums[i]){ cnts[j]++; found=1; break; } } if(!found){ vals[distinctN]=nums[i]; cnts[distinctN]=1; distinctN++; } }\nlong long num=1; for(int i=2;i<=n;i++) num*=i;\nlong long denom=1;\nfor(int j=0;j<distinctN;j++){ long long f=1; for(int i=2;i<=cnts[j];i++) f*=i; denom*=f; }\nlong long result = num/denom;",
    "rust": "use std::collections::HashMap;\nlet mut freq: HashMap<i32,i64> = HashMap::new();\nfor &x in nums.iter() { *freq.entry(x).or_insert(0) += 1; }\nlet mut num: i64 = 1; for i in 2..=(nums.len() as i64) { num *= i; }\nlet mut denom: i64 = 1;\nfor &c in freq.values() { let mut f: i64 = 1; for i in 2..=c { f *= i; } denom *= f; }\nlet result: i64 = num/denom;",
})

add("ship-packages-within-days", "arr1_int", "ship_within_days", "int", {
    "javascript": "function feas(cap){ let days=1, cur=0; for (const w of nums) { if (cur+w>cap) { days++; cur=w; } else { cur+=w; } } return days<=extra; }\nlet lo = Math.max(...nums), hi = nums.reduce((a,b)=>a+b,0);\nwhile (lo<hi) { const mid=Math.floor((lo+hi)/2); if (feas(mid)) hi=mid; else lo=mid+1; }\nlet result = lo;",
    "typescript": "const feas=(cap:number):boolean=>{ let days=1, cur=0; for (const w of nums) { if (cur+w>cap) { days++; cur=w; } else { cur+=w; } } return days<=extra; };\nlet lo = Math.max(...nums), hi = nums.reduce((a,b)=>a+b,0);\nwhile (lo<hi) { const mid=Math.floor((lo+hi)/2); if (feas(mid)) hi=mid; else lo=mid+1; }\nlet result: number = lo;",
    "java": "long hiV=0, maxV=0; for (int w: nums) { hiV+=w; maxV=Math.max(maxV,w); }\nlong lo=maxV, hi=hiV;\nwhile (lo<hi) { long mid=(lo+hi)/2; long days=1, cur=0; for (int w: nums) { if (cur+w>mid) { days++; cur=w; } else { cur+=w; } } if (days<=extra) hi=mid; else lo=mid+1; }\nlong result = lo;",
    "cpp": "long long hiV=0, maxV=0; for (int w: nums) { hiV+=w; maxV=max(maxV,(long long)w); }\nlong long lo=maxV, hi=hiV;\nwhile (lo<hi) { long long mid=(lo+hi)/2; long long days=1, cur=0; for (int w: nums) { if (cur+w>mid) { days++; cur=w; } else { cur+=w; } } if (days<=extra) hi=mid; else lo=mid+1; }\nlong long result = lo;",
    "csharp": "long hiV=0, maxV=0; foreach (int w in nums) { hiV+=w; maxV=Math.Max(maxV,w); }\nlong lo=maxV, hi=hiV;\nwhile (lo<hi) { long mid=(lo+hi)/2; long days=1, cur=0; foreach (int w in nums) { if (cur+w>mid) { days++; cur=w; } else { cur+=w; } } if (days<=extra) hi=mid; else lo=mid+1; }\nlong result = lo;",
    "perl": "my $hiV=0; my $maxV=0; for my $w (@$nums) { $hiV+=$w; $maxV=$w if $w>$maxV; }\nmy $lo=$maxV; my $hi=$hiV;\nwhile ($lo<$hi) { my $mid=int(($lo+$hi)/2); my $days=1; my $cur=0; for my $w (@$nums) { if ($cur+$w>$mid) { $days++; $cur=$w; } else { $cur+=$w; } } if ($days<=$extra) { $hi=$mid; } else { $lo=$mid+1; } }\nmy $result = $lo;",
    "c": "long long hiV=0, maxV=0; for(int i=0;i<n;i++){ hiV+=nums[i]; if(nums[i]>maxV) maxV=nums[i]; }\nlong long lo=maxV, hi=hiV;\nwhile (lo<hi) { long long mid=(lo+hi)/2; long long days=1, cur=0; for(int i=0;i<n;i++){ if(cur+nums[i]>mid){ days++; cur=nums[i]; } else { cur+=nums[i]; } } if(days<=extra) hi=mid; else lo=mid+1; }\nlong long result = lo;",
    "rust": "let hiv: i64 = nums.iter().map(|&x| x as i64).sum();\nlet maxv: i64 = *nums.iter().max().unwrap() as i64;\nlet mut lo = maxv; let mut hi = hiv;\nwhile lo < hi { let mid = (lo+hi)/2; let mut days: i64 = 1; let mut cur: i64 = 0; for &w in nums.iter() { let w64 = w as i64; if cur + w64 > mid { days += 1; cur = w64; } else { cur += w64; } } if days <= extra as i64 { hi = mid; } else { lo = mid + 1; } }\nlet result: i64 = lo;",
})

add("subarray-product-less-than-k", "arr1_int", "num_subarray_product_less_than_k", "int", {
    "javascript": "if (extra<=1) { var result = 0; } else { let left=0, prod=1, count=0; for (let right=0; right<nums.length; right++) { prod*=nums[right]; while (prod>=extra) { prod/=nums[left]; left++; } count += right-left+1; } var result = count; }",
    "typescript": "let result: number;\nif (extra<=1) { result = 0; } else { let left=0, prod=1, count=0; for (let right=0; right<nums.length; right++) { prod*=nums[right]; while (prod>=extra) { prod/=nums[left]; left++; } count += right-left+1; } result = count; }",
    "java": "long result;\nif (extra<=1) { result = 0; } else { int left=0; long prod=1, count=0; for (int right=0; right<nums.length; right++) { prod*=nums[right]; while (prod>=extra) { prod/=nums[left]; left++; } count += right-left+1; } result = count; }",
    "cpp": "long long result;\nif (extra<=1) { result = 0; } else { int left=0; long long prod=1, count=0; for (int right=0; right<(int)nums.size(); right++) { prod*=nums[right]; while (prod>=extra) { prod/=nums[left]; left++; } count += right-left+1; } result = count; }",
    "csharp": "long result;\nif (extra<=1) { result = 0; } else { int left=0; long prod=1, count=0; for (int right=0; right<nums.Length; right++) { prod*=nums[right]; while (prod>=extra) { prod/=nums[left]; left++; } count += right-left+1; } result = count; }",
    "perl": "my $result;\nif ($extra<=1) { $result = 0; } else { my $left=0; my $prod=1; my $count=0; for (my $right=0; $right<scalar(@$nums); $right++) { $prod*=$nums->[$right]; while ($prod>=$extra) { $prod=int($prod/$nums->[$left]); $left++; } $count += $right-$left+1; } $result = $count; }",
    "c": "long long result;\nif (extra<=1) { result = 0; } else { int left=0; long long prod=1, count=0; for (int right=0; right<n; right++) { prod*=nums[right]; while (prod>=extra) { prod/=nums[left]; left++; } count += right-left+1; } result = count; }",
    "rust": "let result: i64;\nif extra <= 1 { result = 0; } else { let mut left = 0usize; let mut prod: i64 = 1; let mut count: i64 = 0; for right in 0..nums.len() { prod *= nums[right] as i64; while prod >= extra as i64 { prod /= nums[left] as i64; left += 1; } count += (right-left+1) as i64; } result = count; }",
})

add("subarray-sums-divisible-by-k", "arr1_int", "subarrays_div_by_k", "int", {
    "javascript": "const seen = new Map(); seen.set(0,1);\nlet sum=0, count=0;\nfor (const x of nums) { sum += x; let r = ((sum % extra) + extra) % extra; count += (seen.get(r)||0); seen.set(r, (seen.get(r)||0)+1); }\nlet result = count;",
    "typescript": "const seen = new Map<number, number>(); seen.set(0,1);\nlet sum=0, count=0;\nfor (const x of nums) { sum += x; let r = ((sum % extra) + extra) % extra; count += (seen.get(r)||0); seen.set(r, (seen.get(r)||0)+1); }\nlet result: number = count;",
    "java": "Map<Long,Long> seen = new HashMap<>(); seen.put(0L,1L);\nlong sum=0, count=0;\nfor (int x: nums) { sum += x; long r = ((sum % extra) + extra) % extra; count += seen.getOrDefault(r,0L); seen.merge(r, 1L, Long::sum); }\nlong result = count;",
    "cpp": "unordered_map<long long,long long> seen; seen[0]=1;\nlong long sum=0, count=0;\nfor (int x: nums) { sum += x; long long r = ((sum % extra) + extra) % extra; count += seen[r]; seen[r]++; }\nlong long result = count;",
    "csharp": "var seen = new Dictionary<long,long>(); seen[0]=1;\nlong sum=0, count=0;\nforeach (int x in nums) { sum += x; long r = ((sum % extra) + extra) % extra; count += seen.ContainsKey(r) ? seen[r] : 0; if (seen.ContainsKey(r)) seen[r]++; else seen[r]=1; }\nlong result = count;",
    "perl": "my %seen; $seen{0}=1;\nmy $sum=0; my $count=0;\nfor my $x (@$nums) { $sum += $x; my $r = (($sum % $extra) + $extra) % $extra; $count += ($seen{$r} // 0); $seen{$r} = ($seen{$r} // 0) + 1; }\nmy $result = $count;",
    "c": "long long* keys=(long long*)calloc(n+1,sizeof(long long)); long long* vals=(long long*)calloc(n+1,sizeof(long long)); int m=0;\nkeys[0]=0; vals[0]=1; m=1;\nlong long sum=0, count=0;\nfor (int i=0;i<n;i++) { sum += nums[i]; long long r = ((sum % extra) + extra) % extra; long long cur=0; int idx=-1; for(int k=0;k<m;k++){ if(keys[k]==r){ cur=vals[k]; idx=k; break; } } count += cur; if(idx>=0){ vals[idx]++; } else { keys[m]=r; vals[m]=1; m++; } }\nlong long result = count;",
    "rust": "use std::collections::HashMap;\nlet mut seen: HashMap<i64,i64> = HashMap::new(); seen.insert(0,1);\nlet mut sum: i64 = 0; let mut count: i64 = 0;\nfor &x in nums.iter() { sum += x as i64; let r = ((sum % extra as i64) + extra as i64) % extra as i64; count += *seen.get(&r).unwrap_or(&0); *seen.entry(r).or_insert(0) += 1; }\nlet result: i64 = count;",
})

add("euler-phi-sieve", "int1", "euler_phi_sieve", "int", {
    "javascript": "let N = n, result = N;\nlet p = 2, num = N;\nwhile (p*p<=num) { if (num % p === 0) { while (num % p === 0) num/=p; result -= result/p; } p++; }\nif (num>1) result -= result/num;",
    "typescript": "let N: number = n; let result: number = N;\nlet p = 2, num = N;\nwhile (p*p<=num) { if (num % p === 0) { while (num % p === 0) num/=p; result -= result/p; } p++; }\nif (num>1) result -= result/num;",
    "java": "long N=n; long result=N; long num=N;\nfor (long p=2; p*p<=num; p++) { if (num % p == 0) { while (num % p == 0) num/=p; result -= result/p; } }\nif (num>1) result -= result/num;",
    "cpp": "long long N=n; long long result=N; long long num=N;\nfor (long long p=2; p*p<=num; p++) { if (num % p == 0) { while (num % p == 0) num/=p; result -= result/p; } }\nif (num>1) result -= result/num;",
    "csharp": "long N=n; long result=N; long num=N;\nfor (long p=2; p*p<=num; p++) { if (num % p == 0) { while (num % p == 0) num/=p; result -= result/p; } }\nif (num>1) result -= result/num;",
    "perl": "my $N=$n; my $result=$N; my $num=$N;\nfor (my $p=2; $p*$p<=$num; $p++) { if ($num % $p == 0) { while ($num % $p == 0) { $num = int($num/$p); } $result -= int($result/$p); } }\nif ($num>1) { $result -= int($result/$num); }",
    "c": "long long N=n; long long result=N; long long num=N;\nfor (long long p=2; p*p<=num; p++) { if (num % p == 0) { while (num % p == 0) num/=p; result -= result/p; } }\nif (num>1) result -= result/num;",
    "rust": "let nn = n; let mut result = nn; let mut num = nn;\nlet mut p: i64 = 2;\nwhile p*p <= num { if num % p == 0 { while num % p == 0 { num /= p; } result -= result/p; } p += 1; }\nif num > 1 { result -= result/num; }",
})

add("integer-square-root", "int1", "my_sqrt", "int", {
    "javascript": "let lo=0, hi=n;\nwhile (lo<hi) { const mid = Math.floor((lo+hi+1)/2); if (mid*mid<=n) lo=mid; else hi=mid-1; }\nlet result = lo;",
    "typescript": "let lo=0, hi=n;\nwhile (lo<hi) { const mid = Math.floor((lo+hi+1)/2); if (mid*mid<=n) lo=mid; else hi=mid-1; }\nlet result: number = lo;",
    "java": "long lo=0, hi=n;\nwhile (lo<hi) { long mid=(lo+hi+1)/2; if (mid*mid<=n) lo=mid; else hi=mid-1; }\nlong result = lo;",
    "cpp": "long long lo=0, hi=n;\nwhile (lo<hi) { long long mid=(lo+hi+1)/2; if (mid*mid<=n) lo=mid; else hi=mid-1; }\nlong long result = lo;",
    "csharp": "long lo=0, hi=n;\nwhile (lo<hi) { long mid=(lo+hi+1)/2; if (mid*mid<=n) lo=mid; else hi=mid-1; }\nlong result = lo;",
    "perl": "my $lo=0; my $hi=$n;\nwhile ($lo<$hi) { my $mid=int(($lo+$hi+1)/2); if ($mid*$mid<=$n) { $lo=$mid; } else { $hi=$mid-1; } }\nmy $result = $lo;",
    "c": "long long lo=0, hi=n;\nwhile (lo<hi) { long long mid=(lo+hi+1)/2; if (mid*mid<=n) lo=mid; else hi=mid-1; }\nlong long result = lo;",
    "rust": "let mut lo: i64 = 0; let mut hi: i64 = n;\nwhile lo < hi { let mid = (lo+hi+1)/2; if mid*mid <= n { lo = mid; } else { hi = mid-1; } }\nlet result: i64 = lo;",
})

add("miller-rabin", "int1", "miller_rabin", "bool", {
    "javascript": "let result;\nif (n<2) result=false; else { result=true; for (let i=2;i*i<=n;i++) { if (n % i === 0) { result=false; break; } } }",
    "typescript": "let result: boolean;\nif (n<2) result=false; else { result=true; for (let i=2;i*i<=n;i++) { if (n % i === 0) { result=false; break; } } }",
    "java": "boolean result;\nif (n<2) { result=false; } else { boolean prime=true; for (long i=2;i*i<=n;i++) { if (n % i == 0) { prime=false; break; } } result=prime; }",
    "cpp": "bool result;\nif (n<2) { result=false; } else { bool prime=true; for (long long i=2;i*i<=n;i++) { if (n % i == 0) { prime=false; break; } } result=prime; }",
    "csharp": "bool result;\nif (n<2) { result=false; } else { bool prime=true; for (long i=2;i*i<=n;i++) { if (n % i == 0) { prime=false; break; } } result=prime; }",
    "perl": "my $result;\nif ($n<2) { $result=0; } else { $result=1; for (my $i=2;$i*$i<=$n;$i++) { if ($n % $i == 0) { $result=0; last; } } }",
    "c": "int result;\nif (n<2) { result=0; } else { result=1; for (long long i=2;i*i<=n;i++) { if (n % i == 0) { result=0; break; } } }",
    "rust": "let result: bool;\nif n < 2 { result = false; } else { let mut prime = true; let mut i: i64 = 2; while i*i <= n { if n % i == 0 { prime = false; break; } i += 1; } result = prime; }",
})

add("number-of-divisors", "int1", "number_of_divisors", "int", {
    "javascript": "let count=0;\nfor (let i=1;i*i<=n;i++) { if (n % i === 0) { count += (i*i===n) ? 1 : 2; } }\nlet result = count;",
    "typescript": "let count=0;\nfor (let i=1;i*i<=n;i++) { if (n % i === 0) { count += (i*i===n) ? 1 : 2; } }\nlet result: number = count;",
    "java": "long count=0;\nfor (long i=1;i*i<=n;i++) { if (n % i == 0) { count += (i*i==n) ? 1 : 2; } }\nlong result = count;",
    "cpp": "long long count=0;\nfor (long long i=1;i*i<=n;i++) { if (n % i == 0) { count += (i*i==n) ? 1 : 2; } }\nlong long result = count;",
    "csharp": "long count=0;\nfor (long i=1;i*i<=n;i++) { if (n % i == 0) { count += (i*i==n) ? 1 : 2; } }\nlong result = count;",
    "perl": "my $count=0;\nfor (my $i=1;$i*$i<=$n;$i++) { if ($n % $i == 0) { $count += ($i*$i==$n) ? 1 : 2; } }\nmy $result = $count;",
    "c": "long long count=0;\nfor (long long i=1;i*i<=n;i++) { if (n % i == 0) { count += (i*i==n) ? 1 : 2; } }\nlong long result = count;",
    "rust": "let mut count: i64 = 0;\nlet mut i: i64 = 1;\nwhile i*i <= n { if n % i == 0 { count += if i*i == n { 1 } else { 2 }; } i += 1; }\nlet result: i64 = count;",
})

add("palindrome-linked-list", "arr1", "is_palindrome", "bool", {
    "javascript": "let lo=0, hi=nums.length-1, result=true;\nwhile (lo<hi) { if (nums[lo]!==nums[hi]) { result=false; break; } lo++; hi--; }",
    "typescript": "let lo=0, hi=nums.length-1; let result=true;\nwhile (lo<hi) { if (nums[lo]!==nums[hi]) { result=false; break; } lo++; hi--; }",
    "java": "int lo=0, hi=nums.length-1; boolean result=true;\nwhile (lo<hi) { if (nums[lo]!=nums[hi]) { result=false; break; } lo++; hi--; }",
    "cpp": "int lo=0, hi=(int)nums.size()-1; bool result=true;\nwhile (lo<hi) { if (nums[lo]!=nums[hi]) { result=false; break; } lo++; hi--; }",
    "csharp": "int lo=0, hi=nums.Length-1; bool result=true;\nwhile (lo<hi) { if (nums[lo]!=nums[hi]) { result=false; break; } lo++; hi--; }",
    "perl": "my $lo=0; my $hi=scalar(@$nums)-1; my $result=1;\nwhile ($lo<$hi) { if ($nums->[$lo]!=$nums->[$hi]) { $result=0; last; } $lo++; $hi--; }",
    "c": "int lo=0, hi=n-1, result=1;\nwhile (lo<hi) { if (nums[lo]!=nums[hi]) { result=0; break; } lo++; hi--; }",
    "rust": "let mut lo = 0i64; let mut hi = nums.len() as i64 - 1; let mut result = true;\nwhile lo < hi { if nums[lo as usize] != nums[hi as usize] { result = false; break; } lo += 1; hi -= 1; }",
})

add("delete-and-earn", "arr1", "delete_and_earn", "int", {
    "javascript": "const maxV = Math.max(...nums);\nconst points = new Array(maxV+1).fill(0);\nfor (const x of nums) points[x]+=x;\nlet prev2=0, prev1=0;\nfor (const p of points) { const cur=Math.max(prev1, prev2+p); prev2=prev1; prev1=cur; }\nlet result = prev1;",
    "typescript": "const maxV: number = Math.max(...nums);\nconst points: number[] = new Array(maxV+1).fill(0);\nfor (const x of nums) points[x]+=x;\nlet prev2=0, prev1=0;\nfor (const p of points) { const cur=Math.max(prev1, prev2+p); prev2=prev1; prev1=cur; }\nlet result: number = prev1;",
    "java": "int maxV=0; for (int x: nums) maxV=Math.max(maxV,x);\nlong[] points=new long[maxV+1];\nfor (int x: nums) points[x]+=x;\nlong prev2=0, prev1=0;\nfor (long p: points) { long cur=Math.max(prev1, prev2+p); prev2=prev1; prev1=cur; }\nlong result = prev1;",
    "cpp": "int maxV=0; for (int x: nums) maxV=max(maxV,x);\nvector<long long> points(maxV+1,0);\nfor (int x: nums) points[x]+=x;\nlong long prev2=0, prev1=0;\nfor (long long p: points) { long long cur=max(prev1, prev2+p); prev2=prev1; prev1=cur; }\nlong long result = prev1;",
    "csharp": "int maxV=0; foreach (int x in nums) maxV=Math.Max(maxV,x);\nlong[] points=new long[maxV+1];\nforeach (int x in nums) points[x]+=x;\nlong prev2=0, prev1=0;\nforeach (long p in points) { long cur=Math.Max(prev1, prev2+p); prev2=prev1; prev1=cur; }\nlong result = prev1;",
    "perl": "my $maxV=0; for my $x (@$nums) { $maxV=$x if $x>$maxV; }\nmy @points=(0) x ($maxV+1);\nfor my $x (@$nums) { $points[$x]+=$x; }\nmy $prev2=0; my $prev1=0;\nfor my $p (@points) { my $cur = ($prev1 > $prev2+$p) ? $prev1 : $prev2+$p; $prev2=$prev1; $prev1=$cur; }\nmy $result = $prev1;",
    "c": "int maxV=0; for(int i=0;i<n;i++) if(nums[i]>maxV) maxV=nums[i];\nlong long* points=(long long*)calloc(maxV+1,sizeof(long long));\nfor(int i=0;i<n;i++) points[nums[i]]+=nums[i];\nlong long prev2=0, prev1=0;\nfor(int i=0;i<=maxV;i++){ long long cur = prev1>prev2+points[i] ? prev1 : prev2+points[i]; prev2=prev1; prev1=cur; }\nlong long result = prev1;",
    "rust": "let maxv = *nums.iter().max().unwrap() as usize;\nlet mut points = vec![0i64; maxv+1];\nfor &x in nums.iter() { points[x as usize] += x as i64; }\nlet mut prev2: i64 = 0; let mut prev1: i64 = 0;\nfor &p in points.iter() { let cur = prev1.max(prev2+p); prev2 = prev1; prev1 = cur; }\nlet result: i64 = prev1;",
})

add("jump-game-ii-min-jumps", "arr1", "jump", "int", {
    "javascript": "let jumps=0, curEnd=0, farthest=0;\nfor (let i=0;i<nums.length-1;i++) { farthest=Math.max(farthest, i+nums[i]); if (i===curEnd) { jumps++; curEnd=farthest; } }\nlet result = jumps;",
    "typescript": "let jumps=0, curEnd=0, farthest=0;\nfor (let i=0;i<nums.length-1;i++) { farthest=Math.max(farthest, i+nums[i]); if (i===curEnd) { jumps++; curEnd=farthest; } }\nlet result: number = jumps;",
    "java": "int jumps=0, curEnd=0, farthest=0;\nfor (int i=0;i<nums.length-1;i++) { farthest=Math.max(farthest, i+nums[i]); if (i==curEnd) { jumps++; curEnd=farthest; } }\nlong result = jumps;",
    "cpp": "int jumps=0, curEnd=0, farthest=0;\nfor (int i=0;i<(int)nums.size()-1;i++) { farthest=max(farthest, i+nums[i]); if (i==curEnd) { jumps++; curEnd=farthest; } }\nlong long result = jumps;",
    "csharp": "int jumps=0, curEnd=0, farthest=0;\nfor (int i=0;i<nums.Length-1;i++) { farthest=Math.Max(farthest, i+nums[i]); if (i==curEnd) { jumps++; curEnd=farthest; } }\nlong result = jumps;",
    "perl": "my $jumps=0; my $curEnd=0; my $farthest=0;\nfor (my $i=0;$i<scalar(@$nums)-1;$i++) { my $v=$i+$nums->[$i]; $farthest=$v if $v>$farthest; if ($i==$curEnd) { $jumps++; $curEnd=$farthest; } }\nmy $result = $jumps;",
    "c": "int jumps=0, curEnd=0, farthest=0;\nfor (int i=0;i<n-1;i++) { int v=i+nums[i]; if(v>farthest) farthest=v; if (i==curEnd) { jumps++; curEnd=farthest; } }\nlong long result = jumps;",
    "rust": "let mut jumps: i64 = 0; let mut cur_end: i64 = 0; let mut farthest: i64 = 0;\nfor i in 0..(nums.len() as i64 - 1) { let v = i + nums[i as usize] as i64; if v > farthest { farthest = v; } if i == cur_end { jumps += 1; cur_end = farthest; } }\nlet result: i64 = jumps;",
})

add("linked-list-cycle-detect", "arr1_int", "has_cycle", "bool", {
    "javascript": "let result = extra !== -1;",
    "typescript": "let result: boolean = extra !== -1;",
    "java": "boolean result = extra != -1;",
    "cpp": "bool result = extra != -1;",
    "csharp": "bool result = extra != -1;",
    "perl": "my $result = ($extra != -1);",
    "c": "int result = (extra != -1);",
    "rust": "let result: bool = extra != -1;",
})

add("lucas-theorem", "int3", "lucas_theorem", "int", {
    "javascript": "function powMod(base,exp,mod){ base%=mod; let r=1; while(exp>0){ if(exp%2===1) r=r*base%mod; base=base*base%mod; exp=Math.floor(exp/2); } return r; }\nfunction smallC(nn,kk,pp){ if(kk<0||kk>nn) return 0; let num=1; for(let i=nn-kk+1;i<=nn;i++) num=num*(i%pp)%pp; let den=1; for(let i=1;i<=kk;i++) den=den*i%pp; return num*powMod(den,pp-2,pp)%pp; }\nfunction lucas(nn,kk,pp){ if(kk===0) return 1%pp; const ni=nn%pp, ki=kk%pp; return (smallC(ni,ki,pp)*lucas(Math.floor(nn/pp),Math.floor(kk/pp),pp))%pp; }\nlet result = lucas(a,b,c);",
    "typescript": "function powMod(base:number,exp:number,mod:number):number{ base%=mod; let r=1; while(exp>0){ if(exp%2===1) r=r*base%mod; base=base*base%mod; exp=Math.floor(exp/2); } return r; }\nfunction smallC(nn:number,kk:number,pp:number):number{ if(kk<0||kk>nn) return 0; let num=1; for(let i=nn-kk+1;i<=nn;i++) num=num*(i%pp)%pp; let den=1; for(let i=1;i<=kk;i++) den=den*i%pp; return num*powMod(den,pp-2,pp)%pp; }\nfunction lucas(nn:number,kk:number,pp:number):number{ if(kk===0) return 1%pp; const ni=nn%pp, ki=kk%pp; return (smallC(ni,ki,pp)*lucas(Math.floor(nn/pp),Math.floor(kk/pp),pp))%pp; }\nlet result: number = lucas(a,b,c);",
    "java": "long result = lucasR(a,b,c);",
    "cpp": "long long result = lucasR(a,b,c);",
    "csharp": "long result = lucasR(a,b,c);",
    "perl": "my $result = lucasR($a,$b,$c);",
    "c": "long long result = lucasR(a,b,c);",
    "rust": "let result: i64 = lucas_r(a,b,c);",
})

add("modular-exponentiation", "int3", "modular_exponentiation", "int", {
    "javascript": "let base=BigInt(a)%BigInt(c), exp=BigInt(b), mod=BigInt(c), r=1n%mod;\nwhile (exp>0n) { if (exp%2n===1n) r=(r*base)%mod; base=(base*base)%mod; exp/=2n; }\nlet result = Number(r);",
    "typescript": "let base=BigInt(a)%BigInt(c), exp=BigInt(b), mod=BigInt(c), r=1n%mod;\nwhile (exp>0n) { if (exp%2n===1n) r=(r*base)%mod; base=(base*base)%mod; exp/=2n; }\nlet result: number = Number(r);",
    "java": "long base=a%c, exp=b, mod=c, r=1%mod;\nwhile (exp>0) { if (exp%2==1) r=(r*base)%mod; base=(base*base)%mod; exp/=2; }\nlong result = r;",
    "cpp": "long long base=a%c, exp=b, mod=c, r=1%mod;\nwhile (exp>0) { if (exp%2==1) r=(r*base)%mod; base=(base*base)%mod; exp/=2; }\nlong long result = r;",
    "csharp": "long baseV=a%c, exp=b, mod=c, r=1%mod;\nwhile (exp>0) { if (exp%2==1) r=(r*baseV)%mod; baseV=(baseV*baseV)%mod; exp/=2; }\nlong result = r;",
    "perl": "my $baseV=$a % $c; my $exp=$b; my $mod=$c; my $r=1 % $mod;\nwhile ($exp>0) { if ($exp % 2 == 1) { $r=($r*$baseV) % $mod; } $baseV=($baseV*$baseV) % $mod; $exp=int($exp/2); }\nmy $result = $r;",
    "c": "long long baseV=a%c, exp=b, mod=c, r=1%mod;\nwhile (exp>0) { if (exp%2==1) r=(r*baseV)%mod; baseV=(baseV*baseV)%mod; exp/=2; }\nlong long result = r;",
    "rust": "let mut base_v = a % c; let mut exp = b; let modv = c; let mut r: i64 = 1 % modv;\nwhile exp > 0 { if exp % 2 == 1 { r = (r * base_v) % modv; } base_v = (base_v * base_v) % modv; exp /= 2; }\nlet result: i64 = r;",
})

add("minimum-knight-moves", "int2", "min_knight_moves", "int", {
    "javascript": "const tx=Math.abs(a), ty=Math.abs(b);\nconst visited = new Set(); const q=[[0,0,0]]; visited.add('0,0');\nconst dirs=[[1,2],[2,1],[-1,2],[-2,1],[1,-2],[2,-1],[-1,-2],[-2,-1]];\nlet ans=0, qi=0;\nwhile(qi<q.length){ const [x,y,d]=q[qi++]; if(x===tx&&y===ty){ ans=d; break; } for(const [dx,dy] of dirs){ const nx=x+dx, ny=y+dy; if(nx>=-2&&ny>=-2&&nx<=tx+2&&ny<=ty+2){ const key=nx+','+ny; if(!visited.has(key)){ visited.add(key); q.push([nx,ny,d+1]); } } } }\nlet result = ans;",
    "typescript": "const tx=Math.abs(a), ty=Math.abs(b);\nconst visited = new Set<string>(); const q:number[][]=[[0,0,0]]; visited.add('0,0');\nconst dirs=[[1,2],[2,1],[-1,2],[-2,1],[1,-2],[2,-1],[-1,-2],[-2,-1]];\nlet ans=0, qi=0;\nwhile(qi<q.length){ const [x,y,d]=q[qi++]; if(x===tx&&y===ty){ ans=d; break; } for(const [dx,dy] of dirs){ const nx=x+dx, ny=y+dy; if(nx>=-2&&ny>=-2&&nx<=tx+2&&ny<=ty+2){ const key=nx+','+ny; if(!visited.has(key)){ visited.add(key); q.push([nx,ny,d+1]); } } } }\nlet result: number = ans;",
    "java": "long tx=Math.abs(a), ty=Math.abs(b);\njava.util.ArrayDeque<long[]> q=new java.util.ArrayDeque<>(); java.util.HashSet<String> vis=new java.util.HashSet<>();\nq.add(new long[]{0,0,0}); vis.add(\"0,0\");\nlong[][] dirs={{1,2},{2,1},{-1,2},{-2,1},{1,-2},{2,-1},{-1,-2},{-2,-1}};\nlong ans=0;\nwhile(!q.isEmpty()){ long[] cur=q.poll(); long x=cur[0], y=cur[1], d=cur[2]; if(x==tx&&y==ty){ ans=d; break; } for(long[] dir: dirs){ long nx=x+dir[0], ny=y+dir[1]; if(nx>=-2&&ny>=-2&&nx<=tx+2&&ny<=ty+2){ String key=nx+\",\"+ny; if(!vis.contains(key)){ vis.add(key); q.add(new long[]{nx,ny,d+1}); } } } }\nlong result = ans;",
    "cpp": "long long tx=llabs(a), ty=llabs(b);\ndeque<array<long long,3>> q; set<pair<long long,long long>> vis;\nq.push_back({0,0,0}); vis.insert({0,0});\nlong long dirs[8][2]={{1,2},{2,1},{-1,2},{-2,1},{1,-2},{2,-1},{-1,-2},{-2,-1}};\nlong long ans=0;\nwhile(!q.empty()){ auto cur=q.front(); q.pop_front(); long long x=cur[0], y=cur[1], d=cur[2]; if(x==tx&&y==ty){ ans=d; break; } for(auto& dir: dirs){ long long nx=x+dir[0], ny=y+dir[1]; if(nx>=-2&&ny>=-2&&nx<=tx+2&&ny<=ty+2){ if(!vis.count({nx,ny})){ vis.insert({nx,ny}); q.push_back({nx,ny,d+1}); } } } }\nlong long result = ans;",
    "csharp": "long tx=Math.Abs(a), ty=Math.Abs(b);\nvar q=new Queue<(long,long,long)>(); var vis=new HashSet<(long,long)>();\nq.Enqueue((0,0,0)); vis.Add((0,0));\nlong[][] dirs=new long[][]{new long[]{1,2},new long[]{2,1},new long[]{-1,2},new long[]{-2,1},new long[]{1,-2},new long[]{2,-1},new long[]{-1,-2},new long[]{-2,-1}};\nlong ans=0;\nwhile(q.Count>0){ var (x,y,d)=q.Dequeue(); if(x==tx&&y==ty){ ans=d; break; } foreach(var dir in dirs){ long nx=x+dir[0], ny=y+dir[1]; if(nx>=-2&&ny>=-2&&nx<=tx+2&&ny<=ty+2){ if(!vis.Contains((nx,ny))){ vis.Add((nx,ny)); q.Enqueue((nx,ny,d+1)); } } } }\nlong result = ans;",
    "perl": "my $tx=abs($a); my $ty=abs($b);\nmy @q=([0,0,0]); my %vis=(\"0,0\"=>1);\nmy @dirs=([1,2],[2,1],[-1,2],[-2,1],[1,-2],[2,-1],[-1,-2],[-2,-1]);\nmy $ans=0;\nwhile(scalar(@q)){ my $cur=shift @q; my ($x,$y,$d)=@$cur; if($x==$tx&&$y==$ty){ $ans=$d; last; } for my $dir (@dirs){ my $nx=$x+$dir->[0]; my $ny=$y+$dir->[1]; if($nx>=-2&&$ny>=-2&&$nx<=$tx+2&&$ny<=$ty+2){ my $key=\"$nx,$ny\"; unless($vis{$key}){ $vis{$key}=1; push @q, [$nx,$ny,$d+1]; } } } }\nmy $result = $ans;",
    "c": "long long tx = a<0?-a:a; long long ty = b<0?-b:b;\nlong long bound = (tx>ty?tx:ty)+4; long long side = 2*bound+1; long long cells = side*side;\nlong long* qx=(long long*)malloc(sizeof(long long)*cells); long long* qy=(long long*)malloc(sizeof(long long)*cells); long long* qd=(long long*)malloc(sizeof(long long)*cells); long long qh=0, qt=0;\nchar* vis=(char*)calloc(cells,1);\nqx[qt]=0; qy[qt]=0; qd[qt]=0; qt++; vis[bound*side+bound]=1;\nlong long dirs[8][2]={{1,2},{2,1},{-1,2},{-2,1},{1,-2},{2,-1},{-1,-2},{-2,-1}};\nlong long ans=0;\nwhile(qh<qt){ long long x=qx[qh], y=qy[qh], d=qd[qh]; qh++; if(x==tx&&y==ty){ ans=d; break; } for(int k=0;k<8;k++){ long long nx=x+dirs[k][0], ny=y+dirs[k][1]; if(nx>=-bound&&ny>=-bound&&nx<=bound&&ny<=bound){ long long idx=(nx+bound)*side+(ny+bound); if(!vis[idx]){ vis[idx]=1; qx[qt]=nx; qy[qt]=ny; qd[qt]=d+1; qt++; } } } }\nlong long result = ans;",
    "rust": "use std::collections::{HashSet, VecDeque};\nlet tx = a.abs(); let ty = b.abs();\nlet mut q: VecDeque<(i64,i64,i64)> = VecDeque::new(); let mut vis: HashSet<(i64,i64)> = HashSet::new();\nq.push_back((0,0,0)); vis.insert((0,0));\nlet dirs: [(i64,i64);8] = [(1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)];\nlet mut ans: i64 = 0;\nwhile let Some((x,y,d)) = q.pop_front() { if x==tx && y==ty { ans = d; break; } for &(dx,dy) in dirs.iter() { let nx=x+dx; let ny=y+dy; if nx>=-2 && ny>=-2 && nx<=tx+2 && ny<=ty+2 && !vis.contains(&(nx,ny)) { vis.insert((nx,ny)); q.push_back((nx,ny,d+1)); } } }\nlet result: i64 = ans;",
})

# lucas-theorem needs a small helper function above the main function in
# non-JS/TS languages (recursion + small-binomial); injected via a per-language
# prelude appended right before the harness-generated function.
LUCAS_PRELUDE = {
    "java": ("static long powMod(long base, long exp, long mod) { base%=mod; long r=1; while (exp>0) { if (exp%2==1) r=r*base%mod; base=base*base%mod; exp/=2; } return r; }\n"
             "static long smallC(long nn, long kk, long pp) { if (kk<0||kk>nn) return 0; long num=1; for (long i=nn-kk+1;i<=nn;i++) num=num*(i%pp)%pp; long den=1; for (long i=1;i<=kk;i++) den=den*i%pp; return num*powMod(den,pp-2,pp)%pp; }\n"
             "static long lucasR(long nn, long kk, long pp) { if (kk==0) return 1%pp; long ni=nn%pp, ki=kk%pp; return (smallC(ni,ki,pp)*lucasR(nn/pp,kk/pp,pp))%pp; }\n"),
    "cpp": ("long long powMod(long long base, long long exp, long long mod) { base%=mod; long long r=1; while (exp>0) { if (exp%2==1) r=r*base%mod; base=base*base%mod; exp/=2; } return r; }\n"
             "long long smallC(long long nn, long long kk, long long pp) { if (kk<0||kk>nn) return 0; long long num=1; for (long long i=nn-kk+1;i<=nn;i++) num=num*(i%pp)%pp; long long den=1; for (long long i=1;i<=kk;i++) den=den*i%pp; return num*powMod(den,pp-2,pp)%pp; }\n"
             "long long lucasR(long long nn, long long kk, long long pp) { if (kk==0) return 1%pp; long long ni=nn%pp, ki=kk%pp; return (smallC(ni,ki,pp)*lucasR(nn/pp,kk/pp,pp))%pp; }\n"),
    "csharp": ("static long powMod(long baseV, long exp, long mod) { baseV%=mod; long r=1; while (exp>0) { if (exp%2==1) r=r*baseV%mod; baseV=baseV*baseV%mod; exp/=2; } return r; }\n"
               "static long smallC(long nn, long kk, long pp) { if (kk<0||kk>nn) return 0; long num=1; for (long i=nn-kk+1;i<=nn;i++) num=num*(i%pp)%pp; long den=1; for (long i=1;i<=kk;i++) den=den*i%pp; return num*powMod(den,pp-2,pp)%pp; }\n"
               "static long lucasR(long nn, long kk, long pp) { if (kk==0) return 1%pp; long ni=nn%pp, ki=kk%pp; return (smallC(ni,ki,pp)*lucasR(nn/pp,kk/pp,pp))%pp; }\n"),
    "perl": ("sub powMod { my ($baseV,$exp,$mod)=@_; $baseV=$baseV%$mod; my $r=1; while ($exp>0) { if ($exp%2==1) { $r=$r*$baseV%$mod; } $baseV=$baseV*$baseV%$mod; $exp=int($exp/2); } return $r; }\n"
             "sub smallC { my ($nn,$kk,$pp)=@_; return 0 if $kk<0||$kk>$nn; my $num=1; for (my $i=$nn-$kk+1;$i<=$nn;$i++) { $num=$num*($i%$pp)%$pp; } my $den=1; for (my $i=1;$i<=$kk;$i++) { $den=$den*$i%$pp; } return $num*powMod($den,$pp-2,$pp)%$pp; }\n"
             "sub lucasR { my ($nn,$kk,$pp)=@_; return 1%$pp if $kk==0; my $ni=$nn%$pp; my $ki=$kk%$pp; return (smallC($ni,$ki,$pp)*lucasR(int($nn/$pp),int($kk/$pp),$pp))%$pp; }\n"),
    "c": ("long long powMod(long long base, long long exp, long long mod) { base%=mod; long long r=1; while (exp>0) { if (exp%2==1) r=r*base%mod; base=base*base%mod; exp/=2; } return r; }\n"
          "long long smallC(long long nn, long long kk, long long pp) { if (kk<0||kk>nn) return 0; long long num=1; for (long long i=nn-kk+1;i<=nn;i++) num=num*(i%pp)%pp; long long den=1; for (long long i=1;i<=kk;i++) den=den*i%pp; return num*powMod(den,pp-2,pp)%pp; }\n"
          "long long lucasR(long long nn, long long kk, long long pp) { if (kk==0) return 1%pp; long long ni=nn%pp, ki=kk%pp; return (smallC(ni,ki,pp)*lucasR(nn/pp,kk/pp,pp))%pp; }\n"),
    "rust": ("fn pow_mod(base_in: i64, exp_in: i64, modv: i64) -> i64 { let mut base = base_in % modv; let mut exp = exp_in; let mut r: i64 = 1; while exp > 0 { if exp % 2 == 1 { r = r*base%modv; } base = base*base%modv; exp /= 2; } r }\n"
             "fn small_c(nn: i64, kk: i64, pp: i64) -> i64 { if kk<0 || kk>nn { return 0; } let mut num: i64 = 1; for i in (nn-kk+1)..=nn { num = num*(i%pp)%pp; } let mut den: i64 = 1; for i in 1..=kk { den = den*i%pp; } num*pow_mod(den,pp-2,pp)%pp }\n"
             "fn lucas_r(nn: i64, kk: i64, pp: i64) -> i64 { if kk==0 { return 1%pp; } let ni=nn%pp; let ki=kk%pp; (small_c(ni,ki,pp)*lucas_r(nn/pp,kk/pp,pp))%pp }\n"),
}


# ---------------------------------------------------------------------------
# Driver: for each (problem, language) not yet Level-6 in the ledger, build
# the correct program and a genuinely-wrong variant (harness prints
# result+1 for int, !result for bool), run both against the real 40-case
# corpus, and only record Level 6 when correct passes all + wrong fails >=1.
# ---------------------------------------------------------------------------

@dataclass
class SimpleCase:
    id: str
    input_data: str
    expected_output: str
    is_hidden: bool
    order: int


def build_program(lang, pid, wrong):
    spec = PROBLEMS[pid]
    shape, fn, kind = spec["shape"], spec["fn"], spec["kind"]
    body = spec["bodies"][lang]
    prelude = LUCAS_PRELUDE.get(lang, "") if pid == "lucas-theorem" else ""
    program = assemble(lang, shape, fn, kind, body, wrong)
    if prelude:
        # Insert the helper function(s) right before the harness's function
        # definition so recursive calls resolve (works for every target
        # language's declaration-order rules used here).
        marker = sig(lang, shape, fn, kind)
        program = program.replace(marker, prelude + marker, 1)
    return program


def load_cases(con, pid):
    cur = con.execute(
        "SELECT id, input_data, expected_output, is_hidden, \"order\" FROM test_cases "
        "WHERE problem_id=? ORDER BY \"order\"", (pid,)
    )
    cases = [SimpleCase(id=r["id"], input_data=r["input_data"], expected_output=r["expected_output"],
                         is_hidden=bool(r["is_hidden"]), order=r["order"]) for r in cur.fetchall()]
    row = con.execute("SELECT test_suite_version FROM problems WHERE id=?", (pid,)).fetchone()
    return cases, row["test_suite_version"]


async def verify_one(pid, lang, cases):
    t0 = time.monotonic()
    correct_result = await evaluate(build_program(lang, pid, False), lang, cases)
    if correct_result.tests_passed != correct_result.tests_total:
        extra = correct_result.compile_output or ""
        if not extra and correct_result.test_results:
            for tr in correct_result.test_results:
                if not tr.passed:
                    extra = f"verdict={tr.verdict} stderr={tr.stderr[:150]} actual={tr.actual_output[:60]!r} expected={tr.expected_output[:60]!r}"
                    break
        return {"pid": pid, "lang": lang, "outcome": "reference_failed",
                "detail": f"{correct_result.tests_passed}/{correct_result.tests_total} verdict={correct_result.verdict} {extra[:200]}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    wrong_result = await evaluate(build_program(lang, pid, True), lang, cases)
    if wrong_result.tests_passed >= wrong_result.tests_total:
        return {"pid": pid, "lang": lang, "outcome": "corpus_weakness", "detail": "wrong solution still passed all cases",
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
    for pid in PROBLEMS:
        cases, tsv = load_cases(con, pid)
        for lang in LANGS:
            if ledger.already_verified(con, pid, lang, "program", test_suite_version=tsv):
                print(f"[SKIP] {pid}/{lang} already verified")
                continue
            r = await verify_one(pid, lang, cases)
            results.append(r)
            status = "PASS" if r["outcome"] == "verified" else "FAIL"
            print(f"[{status}] {lang}(program) {pid:38s} {r['outcome']:18s} {r['detail'][:140]}", flush=True)
            if r["outcome"] == "verified":
                row = con.execute("SELECT starter_code FROM problems WHERE id=?", (pid,)).fetchone()
                sc = json.loads(row["starter_code"])
                sc[lang] = build_program(lang, pid, False)
                con.execute("UPDATE problems SET starter_code=? WHERE id=?", (json.dumps(sc), pid))
                con.commit()
                ledger.record_cell(
                    con, problem_id=pid, language=lang, mode="program",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version="program-mega-batch1-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"],
                )

    verified = [r for r in results if r["outcome"] == "verified"]
    failed = [r for r in results if r["outcome"] != "verified"]
    print(f"\nTOTAL: {len(results)}  verified={len(verified)}  failed={len(failed)}")
    if failed:
        print("\nFAILED CELLS (fix and re-run -- already-verified cells are skipped automatically):")
        for r in failed:
            print(f"  {r['pid']}/{r['lang']}: {r['outcome']} -- {r['detail'][:160]}")
    con.close()
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
