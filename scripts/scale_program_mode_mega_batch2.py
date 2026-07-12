"""Program Mode gap closure, mega batch 2: the remaining problems that were
already Level-6 Function Mode across all 8 core languages but had zero
Program Mode coverage, using shapes NOT covered by mega_batch1.py (strings,
two-same-length-arrays, two-arrays-plus-capacity, triangle/2D-array).

Same harness-factoring approach as mega_batch1.py (see its docstring), just
with more shapes: str1, str1_int, str2, arr2_samelen, arr2_int, triangle --
plus the arr1/arr1_int/int1/int2/int3 shapes reused verbatim.
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
    if shape == "str1":
        if lang == "javascript": return f"function {fn}(s) {{"
        if lang == "typescript": return f"function {fn}(s: string): {rt} {{"
        if lang == "java": return f"static {rt} {fn}(String s) {{"
        if lang == "cpp": return f"{rt} {fn}(string s) {{"
        if lang == "csharp": return f"static {rt} {fn}(string s) {{"
        if lang == "perl": return f"sub {fn} {{ my ($s) = @_;"
        if lang == "c": return f"{rt} {fn}(char* s) {{"
        if lang == "rust": return f"fn {fn}(s: &str) -> {rt} {{"
    if shape == "str1_int":
        if lang == "javascript": return f"function {fn}(s, extra) {{"
        if lang == "typescript": return f"function {fn}(s: string, extra: number): {rt} {{"
        if lang == "java": return f"static {rt} {fn}(String s, int extra) {{"
        if lang == "cpp": return f"{rt} {fn}(string s, int extra) {{"
        if lang == "csharp": return f"static {rt} {fn}(string s, int extra) {{"
        if lang == "perl": return f"sub {fn} {{ my ($s, $extra) = @_;"
        if lang == "c": return f"{rt} {fn}(char* s, int extra) {{"
        if lang == "rust": return f"fn {fn}(s: &str, extra: i32) -> {rt} {{"
    if shape == "str2":
        if lang == "javascript": return f"function {fn}(s, t) {{"
        if lang == "typescript": return f"function {fn}(s: string, t: string): {rt} {{"
        if lang == "java": return f"static {rt} {fn}(String s, String t) {{"
        if lang == "cpp": return f"{rt} {fn}(string s, string t) {{"
        if lang == "csharp": return f"static {rt} {fn}(string s, string t) {{"
        if lang == "perl": return f"sub {fn} {{ my ($s, $t) = @_;"
        if lang == "c": return f"{rt} {fn}(char* s, char* t) {{"
        if lang == "rust": return f"fn {fn}(s: &str, t: &str) -> {rt} {{"
    if shape == "arr2_samelen":
        if lang == "javascript": return f"function {fn}(a, b) {{"
        if lang == "typescript": return f"function {fn}(a: number[], b: number[]): {rt} {{"
        if lang == "java": return f"static {rt} {fn}(int[] a, int[] b) {{"
        if lang == "cpp": return f"{rt} {fn}(vector<int>& a, vector<int>& b) {{"
        if lang == "csharp": return f"static {rt} {fn}(int[] a, int[] b) {{"
        if lang == "perl": return f"sub {fn} {{ my ($arrA, $arrB) = @_;"
        if lang == "c": return f"{rt} {fn}(int* a, int* b, int n) {{"
        if lang == "rust": return f"fn {fn}(a: &Vec<i32>, b: &Vec<i32>) -> {rt} {{"
    if shape == "arr2_int":
        if lang == "javascript": return f"function {fn}(a, b, extra) {{"
        if lang == "typescript": return f"function {fn}(a: number[], b: number[], extra: number): {rt} {{"
        if lang == "java": return f"static {rt} {fn}(int[] a, int[] b, int extra) {{"
        if lang == "cpp": return f"{rt} {fn}(vector<int>& a, vector<int>& b, int extra) {{"
        if lang == "csharp": return f"static {rt} {fn}(int[] a, int[] b, int extra) {{"
        if lang == "perl": return f"sub {fn} {{ my ($arrA, $arrB, $extra) = @_;"
        if lang == "c": return f"{rt} {fn}(int* a, int* b, int n, int extra) {{"
        if lang == "rust": return f"fn {fn}(a: &Vec<i32>, b: &Vec<i32>, extra: i32) -> {rt} {{"
    if shape == "triangle":
        if lang == "javascript": return f"function {fn}(triangle) {{"
        if lang == "typescript": return f"function {fn}(triangle: number[][]): {rt} {{"
        if lang == "java": return f"static {rt} {fn}(int[][] triangle) {{"
        if lang == "cpp": return f"{rt} {fn}(vector<vector<int>>& triangle) {{"
        if lang == "csharp": return f"static {rt} {fn}(int[][] triangle) {{"
        if lang == "perl": return f"sub {fn} {{ my ($triangle) = @_;"
        if lang == "c": return f"{rt} {fn}(int** triangle, int n) {{"
        if lang == "rust": return f"fn {fn}(triangle: &Vec<Vec<i32>>) -> {rt} {{"
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
    if shape == "str1":
        if lang in ("javascript", "typescript"):
            return "const s = require('fs').readFileSync(0,'utf8').trim();"
        if lang == "java":
            return "Scanner sc = new Scanner(System.in);\nString s = sc.hasNext() ? sc.next() : \"\";"
        if lang == "cpp":
            return "string s; cin >> s;"
        if lang == "csharp":
            return "string s = System.Console.In.ReadToEnd().Trim();"
        if lang == "perl":
            return "my $s = do { local $/; <STDIN> };\n$s =~ s/^\\s+|\\s+$//g;"
        if lang == "c":
            return "char* s = (char*)calloc(300005,1);\nscanf(\"%s\", s);"
        if lang == "rust":
            return "let mut s = String::new();\nstd::io::stdin().read_to_string(&mut s).unwrap();\nlet s = s.trim().to_string();"
    if shape == "str1_int":
        if lang in ("javascript", "typescript"):
            return ("const __line = require('fs').readFileSync(0,'utf8').replace(/\\r?\\n$/,'');\n"
                     "const __idx = __line.lastIndexOf(' ');\nconst s = __line.slice(0,__idx);\nconst extra = parseInt(__line.slice(__idx+1));")
        if lang == "java":
            return ("java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));\n"
                     "String __line = br.readLine();\nint __idx = __line.lastIndexOf(' ');\n"
                     "String s = __line.substring(0,__idx);\nint extra = Integer.parseInt(__line.substring(__idx+1).trim());")
        if lang == "cpp":
            return ("string __line; getline(cin, __line);\nint __idx = (int)__line.find_last_of(' ');\n"
                     "string s = __line.substr(0, __idx);\nint extra = stoi(__line.substr(__idx+1));")
        if lang == "csharp":
            return ("string __line = System.Console.In.ReadLine();\nint __idx = __line.LastIndexOf(' ');\n"
                     "string s = __line.Substring(0, __idx);\nint extra = int.Parse(__line.Substring(__idx+1).Trim());")
        if lang == "perl":
            return ("my $__line = <STDIN>; chomp $__line;\nmy $__idx = rindex($__line, ' ');\n"
                     "my $s = substr($__line, 0, $__idx);\nmy $extra = substr($__line, $__idx+1) + 0;")
        if lang == "c":
            return ("char __line[300005]; fgets(__line, sizeof(__line), stdin);\n"
                     "int __len = (int)strlen(__line);\nwhile (__len>0 && (__line[__len-1]=='\\n'||__line[__len-1]=='\\r')) { __line[--__len]=0; }\n"
                     "int __idx = -1; for (int i=__len-1;i>=0;i--) { if (__line[i]==' ') { __idx=i; break; } }\n"
                     "char* s = (char*)malloc(__idx+1); strncpy(s, __line, __idx); s[__idx]=0;\n"
                     "int extra = atoi(__line+__idx+1);")
        if lang == "rust":
            return ("let mut __line = String::new();\nstd::io::stdin().read_line(&mut __line).unwrap();\n"
                     "let __line = __line.trim_end_matches(['\\n','\\r']).to_string();\n"
                     "let __idx = __line.rfind(' ').unwrap();\n"
                     "let s = __line[..__idx].to_string();\nlet extra: i32 = __line[__idx+1..].parse().unwrap();")
    if shape == "str2":
        if lang in ("javascript", "typescript"):
            return "const __lines = require('fs').readFileSync(0,'utf8').split('\\n');\nconst s = __lines[0]; const t = (__lines[1]||'').replace(/\\r$/,'');"
        if lang == "java":
            return ("java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));\n"
                     "String s = br.readLine(); String t = br.readLine(); if (t==null) t=\"\";")
        if lang == "cpp":
            return "string s, t; getline(cin, s); getline(cin, t);"
        if lang == "csharp":
            return "string s = System.Console.In.ReadLine();\nstring t = System.Console.In.ReadLine(); if (t==null) t=\"\";"
        if lang == "perl":
            return "my $s = <STDIN>; chomp $s;\nmy $t = <STDIN>; $t = \"\" unless defined $t; chomp $t;"
        if lang == "c":
            return ("char* s = (char*)calloc(300005,1); char* t = (char*)calloc(300005,1);\n"
                     "fgets(s, 300005, stdin); fgets(t, 300005, stdin);\n"
                     "{ int l=(int)strlen(s); while(l>0 && (s[l-1]=='\\n'||s[l-1]=='\\r')) s[--l]=0; }\n"
                     "{ int l=(int)strlen(t); while(l>0 && (t[l-1]=='\\n'||t[l-1]=='\\r')) t[--l]=0; }")
        if lang == "rust":
            return ("let mut __input = String::new();\nstd::io::stdin().read_to_string(&mut __input).unwrap();\n"
                     "let mut __lines = __input.split('\\n');\n"
                     "let s = __lines.next().unwrap_or(\"\").trim_end_matches('\\r').to_string();\n"
                     "let t = __lines.next().unwrap_or(\"\").trim_end_matches('\\r').to_string();")
    if shape == "arr2_samelen":
        if lang in ("javascript", "typescript"):
            return ("const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                     "const n = data[0]; const a = data.slice(1,1+n); const b = data.slice(1+n,1+2*n);")
        if lang == "java":
            return ("Scanner sc = new Scanner(System.in);\nint n = sc.nextInt();\n"
                     "int[] a = new int[n]; for (int i=0;i<n;i++) a[i]=sc.nextInt();\n"
                     "int[] b = new int[n]; for (int i=0;i<n;i++) b[i]=sc.nextInt();")
        if lang == "cpp":
            return "int n; cin >> n;\nvector<int> a(n), b(n);\nfor (int i=0;i<n;i++) cin >> a[i];\nfor (int i=0;i<n;i++) cin >> b[i];"
        if lang == "csharp":
            return ("var tokens = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, "
                     "System.StringSplitOptions.RemoveEmptyEntries);\nint idx=0; int n=int.Parse(tokens[idx++]);\n"
                     "int[] a=new int[n]; for(int i=0;i<n;i++) a[i]=int.Parse(tokens[idx++]);\n"
                     "int[] b=new int[n]; for(int i=0;i<n;i++) b[i]=int.Parse(tokens[idx++]);")
        if lang == "perl":
            return "my @data = split ' ', do { local $/; <STDIN> };\nmy $n = shift @data;\nmy @a = @data[0..$n-1];\nmy @b = @data[$n..2*$n-1];"
        if lang == "c":
            return ("int n; scanf(\"%d\",&n);\nint* a=(int*)malloc(sizeof(int)*(n>0?n:1)); for(int i=0;i<n;i++) scanf(\"%d\",&a[i]);\n"
                     "int* b=(int*)malloc(sizeof(int)*(n>0?n:1)); for(int i=0;i<n;i++) scanf(\"%d\",&b[i]);")
        if lang == "rust":
            return ("let mut input=String::new(); std::io::stdin().read_to_string(&mut input).unwrap();\n"
                     "let mut it=input.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
                     "let n=it.next().unwrap() as usize;\n"
                     "let a: Vec<i32>=(0..n).map(|_| it.next().unwrap()).collect();\n"
                     "let b: Vec<i32>=(0..n).map(|_| it.next().unwrap()).collect();")
    if shape == "arr2_int":
        base = read_code(lang, "arr2_samelen")
        extra_line = {
            "javascript": "const extra = data[1+2*n];",
            "typescript": "const extra = data[1+2*n];",
            "java": "int extra = sc.nextInt();",
            "cpp": "int extra; cin >> extra;",
            "csharp": "int extra = int.Parse(tokens[idx++]);",
            "perl": "my $extra = $data[2*$n];",
            "c": "int extra; scanf(\"%d\", &extra);",
            "rust": "let extra = it.next().unwrap();",
        }[lang]
        return base + "\n" + extra_line
    if shape == "triangle":
        if lang in ("javascript", "typescript"):
            return ("const __d = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                     "let __p=0; const n=__d[__p++]; const triangle = [];\n"
                     "for (let i=0;i<n;i++) { const row=[]; for (let j=0;j<=i;j++) row.push(__d[__p++]); triangle.push(row); }")
        if lang == "java":
            return ("Scanner sc = new Scanner(System.in);\nint n = sc.nextInt();\nint[][] triangle = new int[n][];\n"
                     "for (int i=0;i<n;i++) { triangle[i]=new int[i+1]; for (int j=0;j<=i;j++) triangle[i][j]=sc.nextInt(); }")
        if lang == "cpp":
            return ("int n; cin >> n;\nvector<vector<int>> triangle(n);\n"
                     "for (int i=0;i<n;i++) { triangle[i].resize(i+1); for (int j=0;j<=i;j++) cin >> triangle[i][j]; }")
        if lang == "csharp":
            return ("var tokens = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, "
                     "System.StringSplitOptions.RemoveEmptyEntries);\nint idx=0; int n=int.Parse(tokens[idx++]);\n"
                     "int[][] triangle=new int[n][];\nfor (int i=0;i<n;i++) { triangle[i]=new int[i+1]; for (int j=0;j<=i;j++) triangle[i][j]=int.Parse(tokens[idx++]); }")
        if lang == "perl":
            return ("my @data = split ' ', do { local $/; <STDIN> };\nmy $p=0; my $n=$data[$p++]; my @triangle;\n"
                     "for (my $i=0;$i<$n;$i++) { my @row; for (my $j=0;$j<=$i;$j++) { push @row, $data[$p++]; } push @triangle, \\@row; }")
        if lang == "c":
            return ("int n; scanf(\"%d\",&n);\nint** triangle=(int**)malloc(sizeof(int*)*n);\n"
                     "for (int i=0;i<n;i++) { triangle[i]=(int*)malloc(sizeof(int)*(i+1)); for (int j=0;j<=i;j++) scanf(\"%d\",&triangle[i][j]); }")
        if lang == "rust":
            return ("let mut input=String::new(); std::io::stdin().read_to_string(&mut input).unwrap();\n"
                     "let mut it=input.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
                     "let n=it.next().unwrap() as usize;\nlet mut triangle: Vec<Vec<i32>> = Vec::new();\n"
                     "for i in 0..n { let row: Vec<i32> = (0..=i).map(|_| it.next().unwrap()).collect(); triangle.push(row); }")
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
    if shape == "str1":
        if lang == "perl": return "$s"
        if lang == "rust": return "&s"
        return "s"
    if shape == "str1_int":
        if lang == "perl": return "$s, $extra"
        if lang == "rust": return "&s, extra"
        return "s, extra"
    if shape == "str2":
        if lang == "perl": return "$s, $t"
        if lang == "rust": return "&s, &t"
        return "s, t"
    if shape == "arr2_samelen":
        if lang == "perl": return "\\@a, \\@b"
        if lang == "c": return "a, b, n"
        if lang == "rust": return "&a, &b"
        return "a, b"
    if shape == "arr2_int":
        if lang == "perl": return "\\@a, \\@b, $extra"
        if lang == "c": return "a, b, n, extra"
        if lang == "rust": return "&a, &b, extra"
        return "a, b, extra"
    if shape == "triangle":
        if lang == "perl": return "\\@triangle"
        if lang == "c": return "triangle, n"
        if lang == "rust": return "&triangle"
        return "triangle"
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
        return f"import java.util.*;\npublic class Main {{\npublic static void main(String[] args) throws Exception {{\n{read}\n{call}\n{p}\n}}\n{func}\n}}\n"
    if lang == "cpp":
        call = f"{rt} result = {fn}({args});"
        return (f"#include <iostream>\n#include <vector>\n#include <algorithm>\n#include <cmath>\n"
                 f"#include <unordered_map>\n#include <climits>\n#include <deque>\n#include <set>\n#include <array>\n#include <cstdlib>\n#include <cstring>\n"
                 f"using namespace std;\n\n{func}\n\nint main() {{\n{read}\n{call}\n{p}\nreturn 0;\n}}\n")
    if lang == "csharp":
        call = f"{rt} result = {fn}({args});"
        return f"using System;\nusing System.Collections.Generic;\nclass Program {{\nstatic void Main() {{\n{read}\n{call}\n{p}\n}}\n{func}\n}}\n"
    if lang == "perl":
        call = f"my $result = {fn}({args});"
        return f"{read}\n{func}\n{call}\n{p}\n"
    if lang == "c":
        call = f"{rt} result = {fn}({args});"
        return f"#include <stdio.h>\n#include <stdlib.h>\n#include <math.h>\n#include <string.h>\n\n{func}\n\nint main() {{\n{read}\n{call}\n{p}\nreturn 0;\n}}\n"
    if lang == "rust":
        call = f"let result = {fn}({args});"
        return f"use std::io::Read;\n\n{func}\n\nfn main() {{\n{read}\n{call}\n{p}\n}}\n"
    raise ValueError(lang)


PROBLEMS: dict[str, dict] = {}


def add(pid, shape, fn, kind, bodies):
    PROBLEMS[pid] = {"shape": shape, "fn": fn, "kind": kind, "bodies": bodies}


# ── str1 problems ────────────────────────────────────────────────────────────

add("first-unique-character-index", "str1", "first_uniq_char", "int", {
    "javascript": "const cnt = new Map();\nfor (const ch of s) cnt.set(ch, (cnt.get(ch)||0)+1);\nlet result = -1;\nfor (let i=0;i<s.length;i++) { if (cnt.get(s[i])===1) { result=i; break; } }",
    "typescript": "const cnt = new Map<string, number>();\nfor (const ch of s) cnt.set(ch, (cnt.get(ch)||0)+1);\nlet result: number = -1;\nfor (let i=0;i<s.length;i++) { if (cnt.get(s[i])===1) { result=i; break; } }",
    "java": "int[] cnt = new int[128];\nfor (char ch : s.toCharArray()) cnt[ch]++;\nlong result = -1;\nfor (int i=0;i<s.length();i++) { if (cnt[s.charAt(i)]==1) { result=i; break; } }",
    "cpp": "int cnt[128]={0};\nfor (char ch : s) cnt[(int)ch]++;\nlong long result = -1;\nfor (int i=0;i<(int)s.size();i++) { if (cnt[(int)s[i]]==1) { result=i; break; } }",
    "csharp": "int[] cnt = new int[128];\nforeach (char ch in s) cnt[ch]++;\nlong result = -1;\nfor (int i=0;i<s.Length;i++) { if (cnt[s[i]]==1) { result=i; break; } }",
    "perl": "my %cnt;\nfor my $ch (split //, $s) { $cnt{$ch}++; }\nmy $result = -1;\nfor (my $i=0;$i<length($s);$i++) { my $ch=substr($s,$i,1); if ($cnt{$ch}==1) { $result=$i; last; } }",
    "c": "int cnt[128]={0};\nint len=(int)strlen(s);\nfor (int i=0;i<len;i++) cnt[(int)s[i]]++;\nlong long result = -1;\nfor (int i=0;i<len;i++) { if (cnt[(int)s[i]]==1) { result=i; break; } }",
    "rust": "let mut cnt = [0i32;128];\nfor b in s.bytes() { cnt[b as usize] += 1; }\nlet mut result: i64 = -1;\nfor (i,b) in s.bytes().enumerate() { if cnt[b as usize]==1 { result = i as i64; break; } }",
})

add("longest-palindromic-substring", "str1", "longest_palindrome", "int", {
    "javascript": "let best=0;\nfunction expand(l,r){ while(l>=0&&r<s.length&&s[l]===s[r]){l--;r++;} return r-l-1; }\nfor (let i=0;i<s.length;i++) { best=Math.max(best, expand(i,i), expand(i,i+1)); }\nlet result = best;",
    "typescript": "let best=0;\nconst expand=(l:number,r:number):number=>{ while(l>=0&&r<s.length&&s[l]===s[r]){l--;r++;} return r-l-1; };\nfor (let i=0;i<s.length;i++) { best=Math.max(best, expand(i,i), expand(i,i+1)); }\nlet result: number = best;",
    "java": "int m=s.length(); long best=0;\nfor (int i=0;i<m;i++) { int l=i, r=i; while(l>=0&&r<m&&s.charAt(l)==s.charAt(r)){l--;r++;} best=Math.max(best, r-l-1); l=i; r=i+1; while(l>=0&&r<m&&s.charAt(l)==s.charAt(r)){l--;r++;} best=Math.max(best, r-l-1); }\nlong result = best;",
    "cpp": "int m=(int)s.size(); long long best=0;\nfor (int i=0;i<m;i++) { int l=i, r=i; while(l>=0&&r<m&&s[l]==s[r]){l--;r++;} best=max(best,(long long)(r-l-1)); l=i; r=i+1; while(l>=0&&r<m&&s[l]==s[r]){l--;r++;} best=max(best,(long long)(r-l-1)); }\nlong long result = best;",
    "csharp": "int m=s.Length; long best=0;\nfor (int i=0;i<m;i++) { int l=i, r=i; while(l>=0&&r<m&&s[l]==s[r]){l--;r++;} best=Math.Max(best, r-l-1); l=i; r=i+1; while(l>=0&&r<m&&s[l]==s[r]){l--;r++;} best=Math.Max(best, r-l-1); }\nlong result = best;",
    "perl": "my $m=length($s); my $best=0;\nfor (my $i=0;$i<$m;$i++) { my $l=$i; my $r=$i; while($l>=0&&$r<$m&&substr($s,$l,1) eq substr($s,$r,1)){$l--;$r++;} my $len=$r-$l-1; $best=$len if $len>$best; $l=$i; $r=$i+1; while($l>=0&&$r<$m&&substr($s,$l,1) eq substr($s,$r,1)){$l--;$r++;} $len=$r-$l-1; $best=$len if $len>$best; }\nmy $result = $best;",
    "c": "int m=(int)strlen(s); long long best=0;\nfor (int i=0;i<m;i++) { int l=i, r=i; while(l>=0&&r<m&&s[l]==s[r]){l--;r++;} long long len=r-l-1; if(len>best) best=len; l=i; r=i+1; while(l>=0&&r<m&&s[l]==s[r]){l--;r++;} len=r-l-1; if(len>best) best=len; }\nlong long result = best;",
    "rust": "let sb: Vec<u8> = s.bytes().collect(); let m = sb.len() as i64; let mut best: i64 = 0;\nfor i in 0..m { let (mut l, mut r) = (i,i); while l>=0 && r<m && sb[l as usize]==sb[r as usize] { l-=1; r+=1; } if r-l-1>best { best=r-l-1; } let (mut l2, mut r2) = (i,i+1); while l2>=0 && r2<m && sb[l2 as usize]==sb[r2 as usize] { l2-=1; r2+=1; } if r2-l2-1>best { best=r2-l2-1; } }\nlet result: i64 = best;",
})

add("longest-valid-parentheses", "str1", "longest_valid_parentheses", "int", {
    "javascript": "const stack=[-1]; let best=0;\nfor (let i=0;i<s.length;i++) { if (s[i]==='(') stack.push(i); else { stack.pop(); if (stack.length===0) stack.push(i); else best=Math.max(best, i-stack[stack.length-1]); } }\nlet result = best;",
    "typescript": "const stack: number[]=[-1]; let best=0;\nfor (let i=0;i<s.length;i++) { if (s[i]==='(') stack.push(i); else { stack.pop(); if (stack.length===0) stack.push(i); else best=Math.max(best, i-stack[stack.length-1]); } }\nlet result: number = best;",
    "java": "int[] stack=new int[s.length()+1]; int sp=0; stack[sp++]=-1; long best=0;\nfor (int i=0;i<s.length();i++) { if (s.charAt(i)=='(') stack[sp++]=i; else { sp--; if (sp==0) stack[sp++]=i; else best=Math.max(best, i-stack[sp-1]); } }\nlong result = best;",
    "cpp": "vector<int> stack; stack.push_back(-1); long long best=0;\nfor (int i=0;i<(int)s.size();i++) { if (s[i]=='(') stack.push_back(i); else { stack.pop_back(); if (stack.empty()) stack.push_back(i); else best=max(best,(long long)(i-stack.back())); } }\nlong long result = best;",
    "csharp": "var stack=new List<int>(); stack.Add(-1); long best=0;\nfor (int i=0;i<s.Length;i++) { if (s[i]=='(') stack.Add(i); else { stack.RemoveAt(stack.Count-1); if (stack.Count==0) stack.Add(i); else best=Math.Max(best, i-stack[stack.Count-1]); } }\nlong result = best;",
    "perl": "my @stack=(-1); my $best=0;\nfor (my $i=0;$i<length($s);$i++) { my $ch=substr($s,$i,1); if ($ch eq '(') { push @stack, $i; } else { pop @stack; if (scalar(@stack)==0) { push @stack, $i; } else { my $len=$i-$stack[-1]; $best=$len if $len>$best; } } }\nmy $result = $best;",
    "c": "int m=(int)strlen(s); int* stack=(int*)malloc(sizeof(int)*(m+2)); int sp=0; stack[sp++]=-1; long long best=0;\nfor (int i=0;i<m;i++) { if (s[i]=='(') { stack[sp++]=i; } else { sp--; if (sp==0) { stack[sp++]=i; } else { long long len=i-stack[sp-1]; if(len>best) best=len; } } }\nlong long result = best;",
    "rust": "let sb: Vec<u8> = s.bytes().collect(); let mut stack: Vec<i64> = vec![-1]; let mut best: i64 = 0;\nfor i in 0..sb.len() as i64 { if sb[i as usize] == b'(' { stack.push(i); } else { stack.pop(); if stack.is_empty() { stack.push(i); } else { let len = i - stack[stack.len()-1]; if len > best { best = len; } } } }\nlet result: i64 = best;",
})

add("manacher", "str1", "count_palindromic_substrings", "int", {
    "javascript": "let count=0;\nfunction expand(l,r){ let c=0; while(l>=0&&r<s.length&&s[l]===s[r]){c++;l--;r++;} return c; }\nfor (let i=0;i<s.length;i++) { count+=expand(i,i); count+=expand(i,i+1); }\nlet result = count;",
    "typescript": "let count=0;\nconst expand=(l:number,r:number):number=>{ let c=0; while(l>=0&&r<s.length&&s[l]===s[r]){c++;l--;r++;} return c; };\nfor (let i=0;i<s.length;i++) { count+=expand(i,i); count+=expand(i,i+1); }\nlet result: number = count;",
    "java": "int m=s.length(); long count=0;\nfor (int i=0;i<m;i++) { int l=i, r=i; while(l>=0&&r<m&&s.charAt(l)==s.charAt(r)){count++;l--;r++;} l=i; r=i+1; while(l>=0&&r<m&&s.charAt(l)==s.charAt(r)){count++;l--;r++;} }\nlong result = count;",
    "cpp": "int m=(int)s.size(); long long count=0;\nfor (int i=0;i<m;i++) { int l=i, r=i; while(l>=0&&r<m&&s[l]==s[r]){count++;l--;r++;} l=i; r=i+1; while(l>=0&&r<m&&s[l]==s[r]){count++;l--;r++;} }\nlong long result = count;",
    "csharp": "int m=s.Length; long count=0;\nfor (int i=0;i<m;i++) { int l=i, r=i; while(l>=0&&r<m&&s[l]==s[r]){count++;l--;r++;} l=i; r=i+1; while(l>=0&&r<m&&s[l]==s[r]){count++;l--;r++;} }\nlong result = count;",
    "perl": "my $m=length($s); my $count=0;\nfor (my $i=0;$i<$m;$i++) { my $l=$i; my $r=$i; while($l>=0&&$r<$m&&substr($s,$l,1) eq substr($s,$r,1)){$count++;$l--;$r++;} $l=$i; $r=$i+1; while($l>=0&&$r<$m&&substr($s,$l,1) eq substr($s,$r,1)){$count++;$l--;$r++;} }\nmy $result = $count;",
    "c": "int m=(int)strlen(s); long long count=0;\nfor (int i=0;i<m;i++) { int l=i, r=i; while(l>=0&&r<m&&s[l]==s[r]){count++;l--;r++;} l=i; r=i+1; while(l>=0&&r<m&&s[l]==s[r]){count++;l--;r++;} }\nlong long result = count;",
    "rust": "let sb: Vec<u8> = s.bytes().collect(); let m = sb.len() as i64; let mut count: i64 = 0;\nfor i in 0..m { let (mut l, mut r) = (i,i); while l>=0 && r<m && sb[l as usize]==sb[r as usize] { count+=1; l-=1; r+=1; } let (mut l2, mut r2) = (i,i+1); while l2>=0 && r2<m && sb[l2 as usize]==sb[r2 as usize] { count+=1; l2-=1; r2+=1; } }\nlet result: i64 = count;",
})

add("palindrome-partition", "str1", "min_cut", "int", {
    "javascript": "const m=s.length;\nconst isPal = Array.from({length:m},()=>new Array(m).fill(false));\nfor (let i=0;i<m;i++) isPal[i][i]=true;\nfor (let len=2;len<=m;len++) { for (let i=0;i+len-1<m;i++) { const j=i+len-1; if (s[i]===s[j] && (len===2||isPal[i+1][j-1])) isPal[i][j]=true; } }\nconst dp=new Array(m).fill(0);\nfor (let i=0;i<m;i++) { if (isPal[0][i]) { dp[i]=0; continue; } let best=Infinity; for (let j=0;j<i;j++) { if (isPal[j+1][i]) best=Math.min(best, dp[j]+1); } dp[i]=best; }\nlet result = m===0?0:dp[m-1];",
    "typescript": "const m=s.length;\nconst isPal: boolean[][] = Array.from({length:m},()=>new Array(m).fill(false));\nfor (let i=0;i<m;i++) isPal[i][i]=true;\nfor (let len=2;len<=m;len++) { for (let i=0;i+len-1<m;i++) { const j=i+len-1; if (s[i]===s[j] && (len===2||isPal[i+1][j-1])) isPal[i][j]=true; } }\nconst dp: number[]=new Array(m).fill(0);\nfor (let i=0;i<m;i++) { if (isPal[0][i]) { dp[i]=0; continue; } let best=Infinity; for (let j=0;j<i;j++) { if (isPal[j+1][i]) best=Math.min(best, dp[j]+1); } dp[i]=best; }\nlet result: number = m===0?0:dp[m-1];",
    "java": "int m=s.length();\nboolean[][] isPal=new boolean[m][m];\nfor (int i=0;i<m;i++) isPal[i][i]=true;\nfor (int len=2;len<=m;len++) { for (int i=0;i+len-1<m;i++) { int j=i+len-1; if (s.charAt(i)==s.charAt(j) && (len==2||isPal[i+1][j-1])) isPal[i][j]=true; } }\nint[] dp=new int[m];\nfor (int i=0;i<m;i++) { if (isPal[0][i]) { dp[i]=0; continue; } int best=Integer.MAX_VALUE; for (int j=0;j<i;j++) { if (isPal[j+1][i]) best=Math.min(best, dp[j]+1); } dp[i]=best; }\nlong result = m==0?0:dp[m-1];",
    "cpp": "int m=(int)s.size();\nvector<vector<char>> isPal(m, vector<char>(m,0));\nfor (int i=0;i<m;i++) isPal[i][i]=1;\nfor (int len=2;len<=m;len++) { for (int i=0;i+len-1<m;i++) { int j=i+len-1; if (s[i]==s[j] && (len==2||isPal[i+1][j-1])) isPal[i][j]=1; } }\nvector<int> dp(m,0);\nfor (int i=0;i<m;i++) { if (isPal[0][i]) { dp[i]=0; continue; } int best=INT_MAX; for (int j=0;j<i;j++) { if (isPal[j+1][i]) best=min(best, dp[j]+1); } dp[i]=best; }\nlong long result = m==0?0:dp[m-1];",
    "csharp": "int m=s.Length;\nbool[,] isPal=new bool[m,m];\nfor (int i=0;i<m;i++) isPal[i,i]=true;\nfor (int len=2;len<=m;len++) { for (int i=0;i+len-1<m;i++) { int j=i+len-1; if (s[i]==s[j] && (len==2||isPal[i+1,j-1])) isPal[i,j]=true; } }\nint[] dp=new int[m==0?1:m];\nfor (int i=0;i<m;i++) { if (isPal[0,i]) { dp[i]=0; continue; } int best=int.MaxValue; for (int j=0;j<i;j++) { if (isPal[j+1,i]) best=Math.Min(best, dp[j]+1); } dp[i]=best; }\nlong result = m==0?0:dp[m-1];",
    "perl": "my $m=length($s);\nmy @isPal; for(my $i=0;$i<$m;$i++){ for(my $j=0;$j<$m;$j++){ $isPal[$i][$j]=0; } }\nfor(my $i=0;$i<$m;$i++){ $isPal[$i][$i]=1; }\nfor(my $len=2;$len<=$m;$len++){ for(my $i=0;$i+$len-1<$m;$i++){ my $j=$i+$len-1; if (substr($s,$i,1) eq substr($s,$j,1) && ($len==2 || $isPal[$i+1][$j-1])) { $isPal[$i][$j]=1; } } }\nmy @dp=(0) x ($m>0?$m:1);\nfor(my $i=0;$i<$m;$i++){ if ($isPal[0][$i]) { $dp[$i]=0; next; } my $best=999999999; for(my $j=0;$j<$i;$j++){ if ($isPal[$j+1][$i]) { my $c=$dp[$j]+1; $best=$c if $c<$best; } } $dp[$i]=$best; }\nmy $result = $m==0 ? 0 : $dp[$m-1];",
    "c": "int m=(int)strlen(s);\nchar** isPal=(char**)malloc(sizeof(char*)*(m>0?m:1));\nfor (int i=0;i<m;i++) { isPal[i]=(char*)calloc(m,1); }\nfor (int i=0;i<m;i++) isPal[i][i]=1;\nfor (int len=2;len<=m;len++) { for (int i=0;i+len-1<m;i++) { int j=i+len-1; if (s[i]==s[j] && (len==2||isPal[i+1][j-1])) isPal[i][j]=1; } }\nint* dp=(int*)calloc(m>0?m:1,sizeof(int));\nfor (int i=0;i<m;i++) { if (isPal[0][i]) { dp[i]=0; continue; } int best=1000000000; for (int j=0;j<i;j++) { if (isPal[j+1][i] && dp[j]+1<best) best=dp[j]+1; } dp[i]=best; }\nlong long result = m==0?0:dp[m-1];",
    "rust": "let sb: Vec<u8> = s.bytes().collect(); let m = sb.len();\nlet mut is_pal = vec![vec![false; m.max(1)]; m.max(1)];\nfor i in 0..m { is_pal[i][i] = true; }\nfor len in 2..=m { for i in 0..=(m.saturating_sub(len)) { if i+len-1>=m { continue; } let j=i+len-1; if sb[i]==sb[j] && (len==2 || is_pal[i+1][j-1]) { is_pal[i][j]=true; } } }\nlet mut dp = vec![0i64; m.max(1)];\nfor i in 0..m { if is_pal[0][i] { dp[i]=0; continue; } let mut best=i64::MAX; for j in 0..i { if is_pal[j+1][i] && dp[j]+1<best { best=dp[j]+1; } } dp[i]=best; }\nlet result: i64 = if m==0 { 0 } else { dp[m-1] };",
})

add("palindrome-partitioning", "str1", "count_partitions", "int", {
    "javascript": "const m=s.length;\nconst isPal = Array.from({length:m},()=>new Array(m).fill(false));\nfor (let i=0;i<m;i++) isPal[i][i]=true;\nfor (let len=2;len<=m;len++) { for (let i=0;i+len-1<m;i++) { const j=i+len-1; if (s[i]===s[j] && (len===2||isPal[i+1][j-1])) isPal[i][j]=true; } }\nconst dp=new Array(m+1).fill(0); dp[0]=1;\nfor (let i=1;i<=m;i++) { let sum=0; for (let j=0;j<i;j++) { if (isPal[j][i-1]) sum+=dp[j]; } dp[i]=sum; }\nlet result = dp[m];",
    "typescript": "const m=s.length;\nconst isPal: boolean[][] = Array.from({length:m},()=>new Array(m).fill(false));\nfor (let i=0;i<m;i++) isPal[i][i]=true;\nfor (let len=2;len<=m;len++) { for (let i=0;i+len-1<m;i++) { const j=i+len-1; if (s[i]===s[j] && (len===2||isPal[i+1][j-1])) isPal[i][j]=true; } }\nconst dp: number[]=new Array(m+1).fill(0); dp[0]=1;\nfor (let i=1;i<=m;i++) { let sum=0; for (let j=0;j<i;j++) { if (isPal[j][i-1]) sum+=dp[j]; } dp[i]=sum; }\nlet result: number = dp[m];",
    "java": "int m=s.length();\nboolean[][] isPal=new boolean[m][m];\nfor (int i=0;i<m;i++) isPal[i][i]=true;\nfor (int len=2;len<=m;len++) { for (int i=0;i+len-1<m;i++) { int j=i+len-1; if (s.charAt(i)==s.charAt(j) && (len==2||isPal[i+1][j-1])) isPal[i][j]=true; } }\nlong[] dp=new long[m+1]; dp[0]=1;\nfor (int i=1;i<=m;i++) { long sum=0; for (int j=0;j<i;j++) { if (isPal[j][i-1]) sum+=dp[j]; } dp[i]=sum; }\nlong result = dp[m];",
    "cpp": "int m=(int)s.size();\nvector<vector<char>> isPal(m, vector<char>(m,0));\nfor (int i=0;i<m;i++) isPal[i][i]=1;\nfor (int len=2;len<=m;len++) { for (int i=0;i+len-1<m;i++) { int j=i+len-1; if (s[i]==s[j] && (len==2||isPal[i+1][j-1])) isPal[i][j]=1; } }\nvector<long long> dp(m+1,0); dp[0]=1;\nfor (int i=1;i<=m;i++) { long long sum=0; for (int j=0;j<i;j++) { if (isPal[j][i-1]) sum+=dp[j]; } dp[i]=sum; }\nlong long result = dp[m];",
    "csharp": "int m=s.Length;\nbool[,] isPal=new bool[m,m];\nfor (int i=0;i<m;i++) isPal[i,i]=true;\nfor (int len=2;len<=m;len++) { for (int i=0;i+len-1<m;i++) { int j=i+len-1; if (s[i]==s[j] && (len==2||isPal[i+1,j-1])) isPal[i,j]=true; } }\nlong[] dp=new long[m+1]; dp[0]=1;\nfor (int i=1;i<=m;i++) { long sum=0; for (int j=0;j<i;j++) { if (isPal[j,i-1]) sum+=dp[j]; } dp[i]=sum; }\nlong result = dp[m];",
    "perl": "my $m=length($s);\nmy @isPal; for(my $i=0;$i<$m;$i++){ for(my $j=0;$j<$m;$j++){ $isPal[$i][$j]=0; } }\nfor(my $i=0;$i<$m;$i++){ $isPal[$i][$i]=1; }\nfor(my $len=2;$len<=$m;$len++){ for(my $i=0;$i+$len-1<$m;$i++){ my $j=$i+$len-1; if (substr($s,$i,1) eq substr($s,$j,1) && ($len==2 || $isPal[$i+1][$j-1])) { $isPal[$i][$j]=1; } } }\nmy @dp=(0) x ($m+1); $dp[0]=1;\nfor(my $i=1;$i<=$m;$i++){ my $sum=0; for(my $j=0;$j<$i;$j++){ $sum+=$dp[$j] if $isPal[$j][$i-1]; } $dp[$i]=$sum; }\nmy $result = $dp[$m];",
    "c": "int m=(int)strlen(s);\nchar** isPal=(char**)malloc(sizeof(char*)*(m>0?m:1));\nfor (int i=0;i<m;i++) { isPal[i]=(char*)calloc(m,1); }\nfor (int i=0;i<m;i++) isPal[i][i]=1;\nfor (int len=2;len<=m;len++) { for (int i=0;i+len-1<m;i++) { int j=i+len-1; if (s[i]==s[j] && (len==2||isPal[i+1][j-1])) isPal[i][j]=1; } }\nlong long* dp=(long long*)calloc(m+1,sizeof(long long)); dp[0]=1;\nfor (int i=1;i<=m;i++) { long long sum=0; for (int j=0;j<i;j++) { if (isPal[j][i-1]) sum+=dp[j]; } dp[i]=sum; }\nlong long result = dp[m];",
    "rust": "let sb: Vec<u8> = s.bytes().collect(); let m = sb.len();\nlet mut is_pal = vec![vec![false; m.max(1)]; m.max(1)];\nfor i in 0..m { is_pal[i][i] = true; }\nfor len in 2..=m { for i in 0..=(m.saturating_sub(len)) { if i+len-1>=m { continue; } let j=i+len-1; if sb[i]==sb[j] && (len==2 || is_pal[i+1][j-1]) { is_pal[i][j]=true; } } }\nlet mut dp = vec![0i64; m+1]; dp[0]=1;\nfor i in 1..=m { let mut sum: i64 = 0; for j in 0..i { if is_pal[j][i-1] { sum += dp[j]; } } dp[i]=sum; }\nlet result: i64 = dp[m];",
})

add("palindrome-subsequence", "str1", "lps", "int", {
    "javascript": "const m=s.length;\nconst dp = Array.from({length:m},()=>new Array(m).fill(0));\nfor (let i=m-1;i>=0;i--) { dp[i][i]=1; for (let j=i+1;j<m;j++) { if (s[i]===s[j]) dp[i][j]=dp[i+1][j-1]+2; else dp[i][j]=Math.max(dp[i+1][j], dp[i][j-1]); } }\nlet result = m===0?0:dp[0][m-1];",
    "typescript": "const m=s.length;\nconst dp: number[][] = Array.from({length:m},()=>new Array(m).fill(0));\nfor (let i=m-1;i>=0;i--) { dp[i][i]=1; for (let j=i+1;j<m;j++) { if (s[i]===s[j]) dp[i][j]=dp[i+1][j-1]+2; else dp[i][j]=Math.max(dp[i+1][j], dp[i][j-1]); } }\nlet result: number = m===0?0:dp[0][m-1];",
    "java": "int m=s.length();\nint[][] dp=new int[m][m];\nfor (int i=m-1;i>=0;i--) { dp[i][i]=1; for (int j=i+1;j<m;j++) { if (s.charAt(i)==s.charAt(j)) dp[i][j]=(i+1<=j-1?dp[i+1][j-1]:0)+2; else dp[i][j]=Math.max(dp[i+1][j], dp[i][j-1]); } }\nlong result = m==0?0:dp[0][m-1];",
    "cpp": "int m=(int)s.size();\nvector<vector<int>> dp(m, vector<int>(m,0));\nfor (int i=m-1;i>=0;i--) { dp[i][i]=1; for (int j=i+1;j<m;j++) { if (s[i]==s[j]) dp[i][j]=(i+1<=j-1?dp[i+1][j-1]:0)+2; else dp[i][j]=max(dp[i+1][j], dp[i][j-1]); } }\nlong long result = m==0?0:dp[0][m-1];",
    "csharp": "int m=s.Length;\nint[,] dp=new int[m>0?m:1,m>0?m:1];\nfor (int i=m-1;i>=0;i--) { dp[i,i]=1; for (int j=i+1;j<m;j++) { if (s[i]==s[j]) dp[i,j]=(i+1<=j-1?dp[i+1,j-1]:0)+2; else dp[i,j]=Math.Max(dp[i+1,j], dp[i,j-1]); } }\nlong result = m==0?0:dp[0,m-1];",
    "perl": "my $m=length($s);\nmy @dp; for(my $i=0;$i<$m;$i++){ for(my $j=0;$j<$m;$j++){ $dp[$i][$j]=0; } }\nfor(my $i=$m-1;$i>=0;$i--){ $dp[$i][$i]=1; for(my $j=$i+1;$j<$m;$j++){ if (substr($s,$i,1) eq substr($s,$j,1)) { my $inner = ($i+1<=$j-1) ? $dp[$i+1][$j-1] : 0; $dp[$i][$j]=$inner+2; } else { $dp[$i][$j] = ($dp[$i+1][$j] > $dp[$i][$j-1]) ? $dp[$i+1][$j] : $dp[$i][$j-1]; } } }\nmy $result = $m==0 ? 0 : $dp[0][$m-1];",
    "c": "int m=(int)strlen(s);\nint** dp=(int**)malloc(sizeof(int*)*(m>0?m:1));\nfor (int i=0;i<m;i++) dp[i]=(int*)calloc(m,sizeof(int));\nfor (int i=m-1;i>=0;i--) { dp[i][i]=1; for (int j=i+1;j<m;j++) { if (s[i]==s[j]) dp[i][j]=((i+1<=j-1)?dp[i+1][j-1]:0)+2; else dp[i][j]=dp[i+1][j]>dp[i][j-1]?dp[i+1][j]:dp[i][j-1]; } }\nlong long result = m==0?0:dp[0][m-1];",
    "rust": "let sb: Vec<u8> = s.bytes().collect(); let m = sb.len();\nlet mut dp = vec![vec![0i64; m.max(1)]; m.max(1)];\nfor i in (0..m).rev() { dp[i][i]=1; for j in (i+1)..m { if sb[i]==sb[j] { let inner = if i+1<=j-1 { dp[i+1][j-1] } else { 0 }; dp[i][j]=inner+2; } else { dp[i][j]=dp[i+1][j].max(dp[i][j-1]); } } }\nlet result: i64 = if m==0 { 0 } else { dp[0][m-1] };",
})

add("restore-ip-addresses-count", "str1", "restore_ip_count", "int", {
    "javascript": "const m=s.length; let count=0;\nfunction valid(seg){ if (seg.length>1 && seg[0]==='0') return false; const v=parseInt(seg,10); return v>=0 && v<=255; }\nfor (let a=1;a<=3&&a<m;a++) for (let b=a+1;b<a+4&&b<m;b++) for (let c=b+1;c<b+4&&c<m;c++) { const s1=s.slice(0,a), s2=s.slice(a,b), s3=s.slice(b,c), s4=s.slice(c); if (s4.length>=1&&s4.length<=3&&valid(s1)&&valid(s2)&&valid(s3)&&valid(s4)) count++; }\nlet result = count;",
    "typescript": "const m=s.length; let count=0;\nconst valid=(seg:string):boolean=>{ if (seg.length>1 && seg[0]==='0') return false; const v=parseInt(seg,10); return v>=0 && v<=255; };\nfor (let a=1;a<=3&&a<m;a++) for (let b=a+1;b<a+4&&b<m;b++) for (let c=b+1;c<b+4&&c<m;c++) { const s1=s.slice(0,a), s2=s.slice(a,b), s3=s.slice(b,c), s4=s.slice(c); if (s4.length>=1&&s4.length<=3&&valid(s1)&&valid(s2)&&valid(s3)&&valid(s4)) count++; }\nlet result: number = count;",
    "java": "int m=s.length(); long count=0;\nfor (int a=1;a<=3&&a<m;a++) for (int b=a+1;b<a+4&&b<m;b++) for (int c=b+1;c<b+4&&c<m;c++) { String s1=s.substring(0,a), s2=s.substring(a,b), s3=s.substring(b,c), s4=s.substring(c); if (s4.length()>=1&&s4.length()<=3&&validSeg(s1)&&validSeg(s2)&&validSeg(s3)&&validSeg(s4)) count++; }\nlong result = count;",
    "cpp": "int m=(int)s.size(); long long count=0;\nfor (int a=1;a<=3&&a<m;a++) for (int b=a+1;b<a+4&&b<m;b++) for (int c=b+1;c<b+4&&c<m;c++) { string s1=s.substr(0,a), s2=s.substr(a,b-a), s3=s.substr(b,c-b), s4=s.substr(c); if (s4.size()>=1&&s4.size()<=3&&validSeg(s1)&&validSeg(s2)&&validSeg(s3)&&validSeg(s4)) count++; }\nlong long result = count;",
    "csharp": "int m=s.Length; long count=0;\nfor (int a=1;a<=3&&a<m;a++) for (int b=a+1;b<a+4&&b<m;b++) for (int c=b+1;c<b+4&&c<m;c++) { string s1=s.Substring(0,a), s2=s.Substring(a,b-a), s3=s.Substring(b,c-b), s4=s.Substring(c); if (s4.Length>=1&&s4.Length<=3&&ValidSeg(s1)&&ValidSeg(s2)&&ValidSeg(s3)&&ValidSeg(s4)) count++; }\nlong result = count;",
    "perl": "my $m=length($s); my $count=0;\nfor (my $a=1;$a<=3&&$a<$m;$a++) { for (my $b=$a+1;$b<$a+4&&$b<$m;$b++) { for (my $c=$b+1;$c<$b+4&&$c<$m;$c++) { my $s1=substr($s,0,$a); my $s2=substr($s,$a,$b-$a); my $s3=substr($s,$b,$c-$b); my $s4=substr($s,$c); if (length($s4)>=1 && length($s4)<=3 && validSeg($s1) && validSeg($s2) && validSeg($s3) && validSeg($s4)) { $count++; } } } }\nmy $result = $count;",
    "c": "int m=(int)strlen(s); long long count=0;\nfor (int a=1;a<=3&&a<m;a++) for (int b=a+1;b<a+4&&b<m;b++) for (int c=b+1;c<b+4&&c<m;c++) { int l4=m-c; if (l4<1||l4>3) continue; if (validSeg(s,0,a)&&validSeg(s,a,b-a)&&validSeg(s,b,c-b)&&validSeg(s,c,l4)) count++; }\nlong long result = count;",
    "rust": "let sb: Vec<u8> = s.bytes().collect(); let m = sb.len() as i64; let mut count: i64 = 0;\nfor a in 1..std::cmp::min(4,m) { for b in (a+1)..std::cmp::min(a+4,m) { for c in (b+1)..std::cmp::min(b+4,m) { let l4 = m-c; if l4<1 || l4>3 { continue; } if valid_seg(&sb,0,a) && valid_seg(&sb,a,b-a) && valid_seg(&sb,b,c-b) && valid_seg(&sb,c,l4) { count += 1; } } } }\nlet result: i64 = count;",
})

# restore-ip-addresses-count needs a small `valid segment` helper in every
# non-JS/TS language (JS/TS inline it as a closure in the body itself).
RESTORE_IP_PRELUDE = {
    "java": "static boolean validSeg(String seg) { if (seg.length()>1 && seg.charAt(0)=='0') return false; if (seg.length()==0 || seg.length()>3) return false; int v=Integer.parseInt(seg); return v>=0 && v<=255; }\n",
    "cpp": "bool validSeg(string seg) { if (seg.size()>1 && seg[0]=='0') return false; if (seg.empty() || seg.size()>3) return false; int v=stoi(seg); return v>=0 && v<=255; }\n",
    "csharp": "static bool ValidSeg(string seg) { if (seg.Length>1 && seg[0]=='0') return false; if (seg.Length==0 || seg.Length>3) return false; int v=int.Parse(seg); return v>=0 && v<=255; }\n",
    "perl": "sub validSeg { my ($seg) = @_; return 0 if length($seg)>1 && substr($seg,0,1) eq '0'; return 0 if length($seg)==0 || length($seg)>3; my $v = $seg + 0; return ($v>=0 && $v<=255) ? 1 : 0; }\n",
    "c": "int validSeg(const char* s, int start, int len) { if (len<=0||len>3) return 0; if (len>1 && s[start]=='0') return 0; int v=0; for (int i=0;i<len;i++) v=v*10+(s[start+i]-'0'); return v>=0 && v<=255; }\n",
    "rust": "fn valid_seg(sb: &Vec<u8>, start: i64, len: i64) -> bool { if len<=0 || len>3 { return false; } if len>1 && sb[start as usize]==b'0' { return false; } let mut v: i64 = 0; for i in 0..len { v = v*10 + (sb[(start+i) as usize]-b'0') as i64; } v>=0 && v<=255 }\n",
}

# ── str1_int problems ─────────────────────────────────────────────────────────

add("longest-repeating-char-replacement", "str1_int", "character_replacement", "int", {
    "javascript": "const cnt=new Array(26).fill(0); let left=0, maxCount=0, best=0;\nfor (let right=0; right<s.length; right++) { const c=s.charCodeAt(right)-65; cnt[c]++; maxCount=Math.max(maxCount,cnt[c]); while ((right-left+1)-maxCount>extra) { cnt[s.charCodeAt(left)-65]--; left++; } best=Math.max(best, right-left+1); }\nlet result = best;",
    "typescript": "const cnt: number[]=new Array(26).fill(0); let left=0, maxCount=0, best=0;\nfor (let right=0; right<s.length; right++) { const c=s.charCodeAt(right)-65; cnt[c]++; maxCount=Math.max(maxCount,cnt[c]); while ((right-left+1)-maxCount>extra) { cnt[s.charCodeAt(left)-65]--; left++; } best=Math.max(best, right-left+1); }\nlet result: number = best;",
    "java": "int[] cnt=new int[26]; int left=0, maxCount=0, best=0;\nfor (int right=0; right<s.length(); right++) { int c=s.charAt(right)-'A'; cnt[c]++; maxCount=Math.max(maxCount,cnt[c]); while ((right-left+1)-maxCount>extra) { cnt[s.charAt(left)-'A']--; left++; } best=Math.max(best, right-left+1); }\nlong result = best;",
    "cpp": "int cnt[26]={0}; int left=0, maxCount=0, best=0;\nfor (int right=0; right<(int)s.size(); right++) { int c=s[right]-'A'; cnt[c]++; maxCount=max(maxCount,cnt[c]); while ((right-left+1)-maxCount>extra) { cnt[s[left]-'A']--; left++; } best=max(best, right-left+1); }\nlong long result = best;",
    "csharp": "int[] cnt=new int[26]; int left=0, maxCount=0, best=0;\nfor (int right=0; right<s.Length; right++) { int c=s[right]-'A'; cnt[c]++; maxCount=Math.Max(maxCount,cnt[c]); while ((right-left+1)-maxCount>extra) { cnt[s[left]-'A']--; left++; } best=Math.Max(best, right-left+1); }\nlong result = best;",
    "perl": "my @cnt=(0) x 26; my $left=0; my $maxCount=0; my $best=0;\nfor (my $right=0; $right<length($s); $right++) { my $c=ord(substr($s,$right,1))-65; $cnt[$c]++; $maxCount=$cnt[$c] if $cnt[$c]>$maxCount; while (($right-$left+1)-$maxCount>$extra) { $cnt[ord(substr($s,$left,1))-65]--; $left++; } my $len=$right-$left+1; $best=$len if $len>$best; }\nmy $result = $best;",
    "c": "int cnt[26]={0}; int left=0, maxCount=0, best=0; int len=(int)strlen(s);\nfor (int right=0; right<len; right++) { int c=s[right]-'A'; cnt[c]++; if(cnt[c]>maxCount) maxCount=cnt[c]; while ((right-left+1)-maxCount>extra) { cnt[s[left]-'A']--; left++; } if(right-left+1>best) best=right-left+1; }\nlong long result = best;",
    "rust": "let sb: Vec<u8> = s.bytes().collect(); let mut cnt = [0i32;26]; let mut left = 0usize; let mut max_count = 0i32; let mut best: i64 = 0;\nfor right in 0..sb.len() { let c = (sb[right]-b'A') as usize; cnt[c]+=1; if cnt[c]>max_count { max_count=cnt[c]; } while ((right-left+1) as i32)-max_count > extra { cnt[(sb[left]-b'A') as usize]-=1; left+=1; } let len=(right-left+1) as i64; if len>best { best=len; } }\nlet result: i64 = best;",
})

add("longest-substring-at-most-k-distinct", "str1_int", "longest_k_distinct", "int", {
    "javascript": "const cnt=new Map(); let left=0, best=0;\nfor (let right=0; right<s.length; right++) { cnt.set(s[right], (cnt.get(s[right])||0)+1); while (cnt.size>extra) { const lc=s[left]; cnt.set(lc, cnt.get(lc)-1); if (cnt.get(lc)===0) cnt.delete(lc); left++; } best=Math.max(best, right-left+1); }\nlet result = best;",
    "typescript": "const cnt=new Map<string,number>(); let left=0, best=0;\nfor (let right=0; right<s.length; right++) { cnt.set(s[right], (cnt.get(s[right])||0)+1); while (cnt.size>extra) { const lc=s[left]; cnt.set(lc, cnt.get(lc)!-1); if (cnt.get(lc)===0) cnt.delete(lc); left++; } best=Math.max(best, right-left+1); }\nlet result: number = best;",
    "java": "Map<Character,Integer> cnt=new HashMap<>(); int left=0, best=0;\nfor (int right=0; right<s.length(); right++) { char c=s.charAt(right); cnt.merge(c,1,Integer::sum); while (cnt.size()>extra) { char lc=s.charAt(left); cnt.put(lc, cnt.get(lc)-1); if (cnt.get(lc)==0) cnt.remove(lc); left++; } best=Math.max(best, right-left+1); }\nlong result = best;",
    "cpp": "unordered_map<char,int> cnt; int left=0, best=0;\nfor (int right=0; right<(int)s.size(); right++) { cnt[s[right]]++; while ((int)cnt.size()>extra) { char lc=s[left]; cnt[lc]--; if (cnt[lc]==0) cnt.erase(lc); left++; } best=max(best, right-left+1); }\nlong long result = best;",
    "csharp": "var cnt=new Dictionary<char,int>(); int left=0, best=0;\nfor (int right=0; right<s.Length; right++) { char c=s[right]; if (cnt.ContainsKey(c)) cnt[c]++; else cnt[c]=1; while (cnt.Count>extra) { char lc=s[left]; cnt[lc]--; if (cnt[lc]==0) cnt.Remove(lc); left++; } best=Math.Max(best, right-left+1); }\nlong result = best;",
    "perl": "my %cnt; my $left=0; my $best=0;\nfor (my $right=0; $right<length($s); $right++) { my $c=substr($s,$right,1); $cnt{$c}++; while (scalar(keys %cnt)>$extra) { my $lc=substr($s,$left,1); $cnt{$lc}--; delete $cnt{$lc} if $cnt{$lc}==0; $left++; } my $len=$right-$left+1; $best=$len if $len>$best; }\nmy $result = $best;",
    "c": "int cnt[256]={0}; int distinct=0; int left=0, best=0; int len=(int)strlen(s);\nfor (int right=0; right<len; right++) { if (cnt[(int)s[right]]==0) distinct++; cnt[(int)s[right]]++; while (distinct>extra) { cnt[(int)s[left]]--; if (cnt[(int)s[left]]==0) distinct--; left++; } if(right-left+1>best) best=right-left+1; }\nlong long result = best;",
    "rust": "use std::collections::HashMap;\nlet sb: Vec<u8> = s.bytes().collect(); let mut cnt: HashMap<u8,i32> = HashMap::new(); let mut left = 0usize; let mut best: i64 = 0;\nfor right in 0..sb.len() { *cnt.entry(sb[right]).or_insert(0) += 1; while cnt.len() as i32 > extra { let lc = sb[left]; *cnt.get_mut(&lc).unwrap() -= 1; if cnt[&lc]==0 { cnt.remove(&lc); } left += 1; } let len = (right-left+1) as i64; if len > best { best = len; } }\nlet result: i64 = best;",
})

# ── str2 problems ─────────────────────────────────────────────────────────────

add("longest-common-substring", "str2", "longest_common_substring", "int", {
    "javascript": "const m=s.length, n2=t.length;\nconst dp = Array.from({length:m+1},()=>new Array(n2+1).fill(0));\nlet best=0;\nfor (let i=1;i<=m;i++) for (let j=1;j<=n2;j++) { if (s[i-1]===t[j-1]) { dp[i][j]=dp[i-1][j-1]+1; best=Math.max(best,dp[i][j]); } }\nlet result = best;",
    "typescript": "const m=s.length, n2=t.length;\nconst dp: number[][] = Array.from({length:m+1},()=>new Array(n2+1).fill(0));\nlet best=0;\nfor (let i=1;i<=m;i++) for (let j=1;j<=n2;j++) { if (s[i-1]===t[j-1]) { dp[i][j]=dp[i-1][j-1]+1; best=Math.max(best,dp[i][j]); } }\nlet result: number = best;",
    "java": "int m=s.length(), n2=t.length();\nint[][] dp=new int[m+1][n2+1]; long best=0;\nfor (int i=1;i<=m;i++) for (int j=1;j<=n2;j++) { if (s.charAt(i-1)==t.charAt(j-1)) { dp[i][j]=dp[i-1][j-1]+1; best=Math.max(best,dp[i][j]); } }\nlong result = best;",
    "cpp": "int m=(int)s.size(), n2=(int)t.size();\nvector<vector<int>> dp(m+1, vector<int>(n2+1,0)); long long best=0;\nfor (int i=1;i<=m;i++) for (int j=1;j<=n2;j++) { if (s[i-1]==t[j-1]) { dp[i][j]=dp[i-1][j-1]+1; best=max(best,(long long)dp[i][j]); } }\nlong long result = best;",
    "csharp": "int m=s.Length, n2=t.Length;\nint[,] dp=new int[m+1,n2+1]; long best=0;\nfor (int i=1;i<=m;i++) for (int j=1;j<=n2;j++) { if (s[i-1]==t[j-1]) { dp[i,j]=dp[i-1,j-1]+1; best=Math.Max(best,dp[i,j]); } }\nlong result = best;",
    "perl": "my $m=length($s); my $n2=length($t);\nmy @dp; for(my $i=0;$i<=$m;$i++){ for(my $j=0;$j<=$n2;$j++){ $dp[$i][$j]=0; } }\nmy $best=0;\nfor(my $i=1;$i<=$m;$i++){ for(my $j=1;$j<=$n2;$j++){ if (substr($s,$i-1,1) eq substr($t,$j-1,1)) { $dp[$i][$j]=$dp[$i-1][$j-1]+1; $best=$dp[$i][$j] if $dp[$i][$j]>$best; } } }\nmy $result = $best;",
    "c": "int m=(int)strlen(s), n2=(int)strlen(t);\nint** dp=(int**)malloc(sizeof(int*)*(m+1));\nfor (int i=0;i<=m;i++) dp[i]=(int*)calloc(n2+1,sizeof(int));\nlong long best=0;\nfor (int i=1;i<=m;i++) for (int j=1;j<=n2;j++) { if (s[i-1]==t[j-1]) { dp[i][j]=dp[i-1][j-1]+1; if (dp[i][j]>best) best=dp[i][j]; } }\nlong long result = best;",
    "rust": "let sb: Vec<u8> = s.bytes().collect(); let tb: Vec<u8> = t.bytes().collect();\nlet m = sb.len(); let n2 = tb.len();\nlet mut dp = vec![vec![0i64; n2+1]; m+1]; let mut best: i64 = 0;\nfor i in 1..=m { for j in 1..=n2 { if sb[i-1]==tb[j-1] { dp[i][j]=dp[i-1][j-1]+1; if dp[i][j]>best { best=dp[i][j]; } } } }\nlet result: i64 = best;",
})

add("minimum-window-substring-length", "str2", "min_window_length", "int", {
    "javascript": "const need=new Map();\nfor (const ch of t) need.set(ch,(need.get(ch)||0)+1);\nlet required=need.size, formed=0; const window=new Map();\nlet left=0, best=Infinity;\nfor (let right=0; right<s.length; right++) { const c=s[right]; window.set(c,(window.get(c)||0)+1); if (need.has(c) && window.get(c)===need.get(c)) formed++; while (formed===required) { best=Math.min(best, right-left+1); const lc=s[left]; window.set(lc, window.get(lc)-1); if (need.has(lc) && window.get(lc)<need.get(lc)) formed--; left++; } }\nlet result = best===Infinity?0:best;",
    "typescript": "const need=new Map<string,number>();\nfor (const ch of t) need.set(ch,(need.get(ch)||0)+1);\nlet required=need.size, formed=0; const window=new Map<string,number>();\nlet left=0, best=Infinity;\nfor (let right=0; right<s.length; right++) { const c=s[right]; window.set(c,(window.get(c)||0)+1); if (need.has(c) && window.get(c)===need.get(c)) formed++; while (formed===required) { best=Math.min(best, right-left+1); const lc=s[left]; window.set(lc, window.get(lc)!-1); if (need.has(lc) && window.get(lc)!<need.get(lc)!) formed--; left++; } }\nlet result: number = best===Infinity?0:best;",
    "java": "Map<Character,Integer> need=new HashMap<>();\nfor (char c: t.toCharArray()) need.merge(c,1,Integer::sum);\nint required=need.size(), formed=0; Map<Character,Integer> window=new HashMap<>();\nint left=0; long best=Long.MAX_VALUE;\nfor (int right=0; right<s.length(); right++) { char c=s.charAt(right); window.merge(c,1,Integer::sum); if (need.containsKey(c) && window.get(c).intValue()==need.get(c).intValue()) formed++; while (formed==required) { best=Math.min(best, right-left+1); char lc=s.charAt(left); window.put(lc, window.get(lc)-1); if (need.containsKey(lc) && window.get(lc)<need.get(lc)) formed--; left++; } }\nlong result = best==Long.MAX_VALUE?0:best;",
    "cpp": "unordered_map<char,int> need;\nfor (char c: t) need[c]++;\nint required=(int)need.size(), formed=0; unordered_map<char,int> window;\nint left=0; long long best=LLONG_MAX;\nfor (int right=0; right<(int)s.size(); right++) { char c=s[right]; window[c]++; if (need.count(c) && window[c]==need[c]) formed++; while (formed==required) { best=min(best,(long long)(right-left+1)); char lc=s[left]; window[lc]--; if (need.count(lc) && window[lc]<need[lc]) formed--; left++; } }\nlong long result = best==LLONG_MAX?0:best;",
    "csharp": "var need=new Dictionary<char,int>();\nforeach (char c in t) { if (need.ContainsKey(c)) need[c]++; else need[c]=1; }\nint required=need.Count, formed=0; var window=new Dictionary<char,int>();\nint left=0; long best=long.MaxValue;\nfor (int right=0; right<s.Length; right++) { char c=s[right]; if (window.ContainsKey(c)) window[c]++; else window[c]=1; if (need.ContainsKey(c) && window[c]==need[c]) formed++; while (formed==required) { best=Math.Min(best, right-left+1); char lc=s[left]; window[lc]--; if (need.ContainsKey(lc) && window[lc]<need[lc]) formed--; left++; } }\nlong result = best==long.MaxValue?0:best;",
    "perl": "my %need;\nfor my $ch (split //, $t) { $need{$ch}++; }\nmy $required=scalar(keys %need); my $formed=0; my %window;\nmy $left=0; my $best=9**9**9;\nfor (my $right=0; $right<length($s); $right++) { my $c=substr($s,$right,1); $window{$c}++; if (exists $need{$c} && $window{$c}==$need{$c}) { $formed++; } while ($formed==$required) { my $len=$right-$left+1; $best=$len if $len<$best; my $lc=substr($s,$left,1); $window{$lc}--; if (exists $need{$lc} && $window{$lc}<$need{$lc}) { $formed--; } $left++; } }\nmy $result = ($best == 9**9**9) ? 0 : $best;",
    "c": "int need[256]={0}; int required=0;\n{ int seen[256]={0}; int tl=(int)strlen(t); for (int i=0;i<tl;i++) { if (need[(int)t[i]]==0) { required++; } need[(int)t[i]]++; (void)seen; } }\nint window[256]={0}; int formed=0; int left=0; long long best=9223372036854775807LL; int len=(int)strlen(s);\nfor (int right=0; right<len; right++) { unsigned char c=s[right]; window[c]++; if (need[c]>0 && window[c]==need[c]) formed++; while (formed==required) { long long clen=right-left+1; if (clen<best) best=clen; unsigned char lc=s[left]; window[lc]--; if (need[lc]>0 && window[lc]<need[lc]) formed--; left++; } }\nlong long result = (best==9223372036854775807LL) ? 0 : best;",
    "rust": "use std::collections::HashMap;\nlet sb: Vec<u8> = s.bytes().collect(); let tb: Vec<u8> = t.bytes().collect();\nlet mut need: HashMap<u8,i32> = HashMap::new();\nfor &c in tb.iter() { *need.entry(c).or_insert(0) += 1; }\nlet required = need.len() as i32; let mut formed = 0i32; let mut window: HashMap<u8,i32> = HashMap::new();\nlet mut left = 0usize; let mut best: i64 = i64::MAX;\nfor right in 0..sb.len() { let c = sb[right]; *window.entry(c).or_insert(0) += 1; if need.contains_key(&c) && window[&c]==need[&c] { formed += 1; } while formed == required { let len=(right-left+1) as i64; if len<best { best=len; } let lc = sb[left]; *window.get_mut(&lc).unwrap() -= 1; if need.contains_key(&lc) && window[&lc]<need[&lc] { formed -= 1; } left += 1; } }\nlet result: i64 = if best == i64::MAX { 0 } else { best };",
})

add("boolean-parenthesization", "str2", "count_ways", "int", {
    "javascript": "const m=s.length;\nconst T=Array.from({length:m},()=>new Array(m).fill(0));\nconst F=Array.from({length:m},()=>new Array(m).fill(0));\nfor (let i=0;i<m;i++) { T[i][i]= s[i]==='T' ? 1 : 0; F[i][i]= s[i]==='F' ? 1 : 0; }\nfor (let len=2;len<=m;len++) { for (let i=0;i+len-1<m;i++) { const j=i+len-1; let tCount=0, fCount=0; for (let k=i;k<j;k++) { const op=t[k]; const lt=T[i][k], lf=F[i][k], rt=T[k+1][j], rf=F[k+1][j]; const total=(lt+lf)*(rt+rf); if (op==='&') { tCount += lt*rt; fCount += total - lt*rt; } else if (op==='|') { fCount += lf*rf; tCount += total - lf*rf; } else { tCount += lt*rf + lf*rt; fCount += lt*rt + lf*rf; } } T[i][j]=tCount; F[i][j]=fCount; } }\nlet result = T[0][m-1];",
    "typescript": "const m=s.length;\nconst T: number[][] = Array.from({length:m},()=>new Array(m).fill(0));\nconst F: number[][] = Array.from({length:m},()=>new Array(m).fill(0));\nfor (let i=0;i<m;i++) { T[i][i]= s[i]==='T' ? 1 : 0; F[i][i]= s[i]==='F' ? 1 : 0; }\nfor (let len=2;len<=m;len++) { for (let i=0;i+len-1<m;i++) { const j=i+len-1; let tCount=0, fCount=0; for (let k=i;k<j;k++) { const op=t[k]; const lt=T[i][k], lf=F[i][k], rt=T[k+1][j], rf=F[k+1][j]; const total=(lt+lf)*(rt+rf); if (op==='&') { tCount += lt*rt; fCount += total - lt*rt; } else if (op==='|') { fCount += lf*rf; tCount += total - lf*rf; } else { tCount += lt*rf + lf*rt; fCount += lt*rt + lf*rf; } } T[i][j]=tCount; F[i][j]=fCount; } }\nlet result: number = T[0][m-1];",
    "java": "int m=s.length();\nlong[][] T=new long[m][m]; long[][] F=new long[m][m];\nfor (int i=0;i<m;i++) { T[i][i]= s.charAt(i)=='T' ? 1 : 0; F[i][i]= s.charAt(i)=='F' ? 1 : 0; }\nfor (int len=2;len<=m;len++) { for (int i=0;i+len-1<m;i++) { int j=i+len-1; long tt=0, ff=0; for (int k=i;k<j;k++) { char op=t.charAt(k); long lt=T[i][k], lf=F[i][k], rt=T[k+1][j], rf=F[k+1][j]; long total=(lt+lf)*(rt+rf); if (op=='&') { tt += lt*rt; ff += total - lt*rt; } else if (op=='|') { ff += lf*rf; tt += total - lf*rf; } else { tt += lt*rf + lf*rt; ff += lt*rt + lf*rf; } } T[i][j]=tt; F[i][j]=ff; } }\nlong result = T[0][m-1];",
    "cpp": "int m=(int)s.size();\nvector<vector<long long>> T(m, vector<long long>(m,0)), F(m, vector<long long>(m,0));\nfor (int i=0;i<m;i++) { T[i][i]= s[i]=='T' ? 1 : 0; F[i][i]= s[i]=='F' ? 1 : 0; }\nfor (int len=2;len<=m;len++) { for (int i=0;i+len-1<m;i++) { int j=i+len-1; long long tt=0, ff=0; for (int k=i;k<j;k++) { char op=t[k]; long long lt=T[i][k], lf=F[i][k], rt=T[k+1][j], rf=F[k+1][j]; long long total=(lt+lf)*(rt+rf); if (op=='&') { tt += lt*rt; ff += total - lt*rt; } else if (op=='|') { ff += lf*rf; tt += total - lf*rf; } else { tt += lt*rf + lf*rt; ff += lt*rt + lf*rf; } } T[i][j]=tt; F[i][j]=ff; } }\nlong long result = T[0][m-1];",
    "csharp": "int m=s.Length;\nlong[,] T=new long[m,m]; long[,] F=new long[m,m];\nfor (int i=0;i<m;i++) { T[i,i]= s[i]=='T' ? 1 : 0; F[i,i]= s[i]=='F' ? 1 : 0; }\nfor (int len=2;len<=m;len++) { for (int i=0;i+len-1<m;i++) { int j=i+len-1; long tt=0, ff=0; for (int k=i;k<j;k++) { char op=t[k]; long lt=T[i,k], lf=F[i,k], rt=T[k+1,j], rf=F[k+1,j]; long total=(lt+lf)*(rt+rf); if (op=='&') { tt += lt*rt; ff += total - lt*rt; } else if (op=='|') { ff += lf*rf; tt += total - lf*rf; } else { tt += lt*rf + lf*rt; ff += lt*rt + lf*rf; } } T[i,j]=tt; F[i,j]=ff; } }\nlong result = T[0,m-1];",
    "perl": "my $m=length($s);\nmy @T; my @F;\nfor(my $i=0;$i<$m;$i++){ for(my $j=0;$j<$m;$j++){ $T[$i][$j]=0; $F[$i][$j]=0; } }\nfor(my $i=0;$i<$m;$i++){ $T[$i][$i] = (substr($s,$i,1) eq 'T') ? 1 : 0; $F[$i][$i] = (substr($s,$i,1) eq 'F') ? 1 : 0; }\nfor(my $len=2;$len<=$m;$len++){ for(my $i=0;$i+$len-1<$m;$i++){ my $j=$i+$len-1; my $tt=0; my $ff=0; for(my $k=$i;$k<$j;$k++){ my $op=substr($t,$k,1); my $lt=$T[$i][$k]; my $lf=$F[$i][$k]; my $rt=$T[$k+1][$j]; my $rf=$F[$k+1][$j]; my $total=($lt+$lf)*($rt+$rf); if ($op eq '&') { $tt += $lt*$rt; $ff += $total - $lt*$rt; } elsif ($op eq '|') { $ff += $lf*$rf; $tt += $total - $lf*$rf; } else { $tt += $lt*$rf + $lf*$rt; $ff += $lt*$rt + $lf*$rf; } } $T[$i][$j]=$tt; $F[$i][$j]=$ff; } }\nmy $result = $T[0][$m-1];",
    "c": "int m=(int)strlen(s);\nlong long** T=(long long**)malloc(sizeof(long long*)*m);\nlong long** F=(long long**)malloc(sizeof(long long*)*m);\nfor (int i=0;i<m;i++) { T[i]=(long long*)calloc(m,sizeof(long long)); F[i]=(long long*)calloc(m,sizeof(long long)); }\nfor (int i=0;i<m;i++) { T[i][i]= s[i]=='T' ? 1 : 0; F[i][i]= s[i]=='F' ? 1 : 0; }\nfor (int len=2;len<=m;len++) { for (int i=0;i+len-1<m;i++) { int j=i+len-1; long long tt=0, ff=0; for (int k=i;k<j;k++) { char op=t[k]; long long lt=T[i][k], lf=F[i][k], rt=T[k+1][j], rf=F[k+1][j]; long long total=(lt+lf)*(rt+rf); if (op=='&') { tt += lt*rt; ff += total - lt*rt; } else if (op=='|') { ff += lf*rf; tt += total - lf*rf; } else { tt += lt*rf + lf*rt; ff += lt*rt + lf*rf; } } T[i][j]=tt; F[i][j]=ff; } }\nlong long result = T[0][m-1];",
    "rust": "let sb: Vec<u8> = s.bytes().collect(); let tb: Vec<u8> = t.bytes().collect(); let m = sb.len();\nlet mut tt_tab = vec![vec![0i64; m]; m]; let mut ff_tab = vec![vec![0i64; m]; m];\nfor i in 0..m { tt_tab[i][i] = if sb[i]==b'T' {1} else {0}; ff_tab[i][i] = if sb[i]==b'F' {1} else {0}; }\nfor len in 2..=m { for i in 0..=(m-len) { let j=i+len-1; let mut tt=0i64; let mut ff=0i64; for k in i..j { let op=tb[k]; let (lt,lf,rt,rf)=(tt_tab[i][k],ff_tab[i][k],tt_tab[k+1][j],ff_tab[k+1][j]); let total=(lt+lf)*(rt+rf); if op==b'&' { tt += lt*rt; ff += total - lt*rt; } else if op==b'|' { ff += lf*rf; tt += total - lf*rf; } else { tt += lt*rf + lf*rt; ff += lt*rt + lf*rf; } } tt_tab[i][j]=tt; ff_tab[i][j]=ff; } }\nlet result: i64 = tt_tab[0][m-1];",
})

# ── arr1 problems (reused shape) ────────────────────────────────────────────

add("matrix-chain-multiplication", "arr1", "matrix_chain_order", "int", {
    "javascript": "const p = nums; const m2 = p.length - 1;\nconst dp = Array.from({length:m2+1},()=>new Array(m2+1).fill(0));\nfor (let len=2;len<=m2;len++) { for (let i=1;i<=m2-len+1;i++) { const j=i+len-1; dp[i][j]=Infinity; for (let k=i;k<j;k++) { const cost = dp[i][k]+dp[k+1][j]+p[i-1]*p[k]*p[j]; if (cost<dp[i][j]) dp[i][j]=cost; } } }\nlet result = m2<1 ? 0 : dp[1][m2];",
    "typescript": "const p = nums; const m2 = p.length - 1;\nconst dp: number[][] = Array.from({length:m2+1},()=>new Array(m2+1).fill(0));\nfor (let len=2;len<=m2;len++) { for (let i=1;i<=m2-len+1;i++) { const j=i+len-1; dp[i][j]=Infinity; for (let k=i;k<j;k++) { const cost = dp[i][k]+dp[k+1][j]+p[i-1]*p[k]*p[j]; if (cost<dp[i][j]) dp[i][j]=cost; } } }\nlet result: number = m2<1 ? 0 : dp[1][m2];",
    "java": "int[] p = nums; int m2 = p.length - 1;\nlong[][] dp=new long[m2+1][m2+1];\nfor (int len=2;len<=m2;len++) { for (int i=1;i<=m2-len+1;i++) { int j=i+len-1; dp[i][j]=Long.MAX_VALUE/2; for (int k=i;k<j;k++) { long cost = dp[i][k]+dp[k+1][j]+(long)p[i-1]*p[k]*p[j]; if (cost<dp[i][j]) dp[i][j]=cost; } } }\nlong result = m2<1 ? 0 : dp[1][m2];",
    "cpp": "vector<int>& p = nums; int m2 = (int)p.size() - 1;\nvector<vector<long long>> dp(m2+1, vector<long long>(m2+1,0));\nfor (int len=2;len<=m2;len++) { for (int i=1;i<=m2-len+1;i++) { int j=i+len-1; dp[i][j]=LLONG_MAX/2; for (int k=i;k<j;k++) { long long cost = dp[i][k]+dp[k+1][j]+(long long)p[i-1]*p[k]*p[j]; if (cost<dp[i][j]) dp[i][j]=cost; } } }\nlong long result = m2<1 ? 0 : dp[1][m2];",
    "csharp": "int[] p = nums; int m2 = p.Length - 1;\nlong[,] dp=new long[m2+1,m2+1];\nfor (int len=2;len<=m2;len++) { for (int i=1;i<=m2-len+1;i++) { int j=i+len-1; dp[i,j]=long.MaxValue/2; for (int k=i;k<j;k++) { long cost = dp[i,k]+dp[k+1,j]+(long)p[i-1]*p[k]*p[j]; if (cost<dp[i,j]) dp[i,j]=cost; } } }\nlong result = m2<1 ? 0 : dp[1,m2];",
    "perl": "my @p = @$nums; my $m2 = scalar(@p) - 1;\nmy @dp; for(my $i=0;$i<=$m2;$i++){ for(my $j=0;$j<=$m2;$j++){ $dp[$i][$j]=0; } }\nfor(my $len=2;$len<=$m2;$len++){ for(my $i=1;$i<=$m2-$len+1;$i++){ my $j=$i+$len-1; $dp[$i][$j]=9**9**9; for(my $k=$i;$k<$j;$k++){ my $cost=$dp[$i][$k]+$dp[$k+1][$j]+$p[$i-1]*$p[$k]*$p[$j]; $dp[$i][$j]=$cost if $cost<$dp[$i][$j]; } } }\nmy $result = $m2<1 ? 0 : $dp[1][$m2];",
    "c": "int* p = nums; int m2 = n - 1;\nlong long** dp=(long long**)malloc(sizeof(long long*)*(m2+1));\nfor (int i=0;i<=m2;i++) dp[i]=(long long*)calloc(m2+1,sizeof(long long));\nfor (int len=2;len<=m2;len++) { for (int i=1;i<=m2-len+1;i++) { int j=i+len-1; dp[i][j]=9223372036854775807LL/2; for (int k=i;k<j;k++) { long long cost = dp[i][k]+dp[k+1][j]+(long long)p[i-1]*p[k]*p[j]; if (cost<dp[i][j]) dp[i][j]=cost; } } }\nlong long result = m2<1 ? 0 : dp[1][m2];",
    "rust": "let p = nums; let m2 = p.len() - 1;\nlet mut dp = vec![vec![0i64; m2+1]; m2+1];\nfor len in 2..=m2 { for i in 1..=(m2-len+1) { let j=i+len-1; dp[i][j]=i64::MAX/2; for k in i..j { let cost = dp[i][k]+dp[k+1][j]+(p[i-1] as i64)*(p[k] as i64)*(p[j] as i64); if cost<dp[i][j] { dp[i][j]=cost; } } } }\nlet result: i64 = if m2<1 { 0 } else { dp[1][m2] };",
})

add("burst-balloons", "arr1", "max_coins", "int", {
    "javascript": "const b=[1,...nums,1]; const m2=b.length;\nconst dp=Array.from({length:m2},()=>new Array(m2).fill(0));\nfor (let len=2;len<m2;len++) { for (let left=0;left+len<m2;left++) { const right=left+len; let best=0; for (let k=left+1;k<right;k++) { const val=dp[left][k]+dp[k][right]+b[left]*b[k]*b[right]; if (val>best) best=val; } dp[left][right]=best; } }\nlet result = dp[0][m2-1];",
    "typescript": "const b=[1,...nums,1]; const m2=b.length;\nconst dp: number[][] = Array.from({length:m2},()=>new Array(m2).fill(0));\nfor (let len=2;len<m2;len++) { for (let left=0;left+len<m2;left++) { const right=left+len; let best=0; for (let k=left+1;k<right;k++) { const val=dp[left][k]+dp[k][right]+b[left]*b[k]*b[right]; if (val>best) best=val; } dp[left][right]=best; } }\nlet result: number = dp[0][m2-1];",
    "java": "int m0=nums.length; int[] b=new int[m0+2]; b[0]=1; b[m0+1]=1; for (int i=0;i<m0;i++) b[i+1]=nums[i]; int m2=b.length;\nlong[][] dp=new long[m2][m2];\nfor (int len=2;len<m2;len++) { for (int left=0;left+len<m2;left++) { int right=left+len; long best=0; for (int k=left+1;k<right;k++) { long val=dp[left][k]+dp[k][right]+(long)b[left]*b[k]*b[right]; if (val>best) best=val; } dp[left][right]=best; } }\nlong result = dp[0][m2-1];",
    "cpp": "int m0=(int)nums.size(); vector<int> b(m0+2); b[0]=1; b[m0+1]=1; for (int i=0;i<m0;i++) b[i+1]=nums[i]; int m2=(int)b.size();\nvector<vector<long long>> dp(m2, vector<long long>(m2,0));\nfor (int len=2;len<m2;len++) { for (int left=0;left+len<m2;left++) { int right=left+len; long long best=0; for (int k=left+1;k<right;k++) { long long val=dp[left][k]+dp[k][right]+(long long)b[left]*b[k]*b[right]; if (val>best) best=val; } dp[left][right]=best; } }\nlong long result = dp[0][m2-1];",
    "csharp": "int m0=nums.Length; int[] b=new int[m0+2]; b[0]=1; b[m0+1]=1; for (int i=0;i<m0;i++) b[i+1]=nums[i]; int m2=b.Length;\nlong[,] dp=new long[m2,m2];\nfor (int len=2;len<m2;len++) { for (int left=0;left+len<m2;left++) { int right=left+len; long best=0; for (int k=left+1;k<right;k++) { long val=dp[left,k]+dp[k,right]+(long)b[left]*b[k]*b[right]; if (val>best) best=val; } dp[left,right]=best; } }\nlong result = dp[0,m2-1];",
    "perl": "my @b=(1, @$nums, 1); my $m2=scalar(@b);\nmy @dp; for(my $i=0;$i<$m2;$i++){ for(my $j=0;$j<$m2;$j++){ $dp[$i][$j]=0; } }\nfor(my $len=2;$len<$m2;$len++){ for(my $left=0;$left+$len<$m2;$left++){ my $right=$left+$len; my $best=0; for(my $k=$left+1;$k<$right;$k++){ my $val=$dp[$left][$k]+$dp[$k][$right]+$b[$left]*$b[$k]*$b[$right]; $best=$val if $val>$best; } $dp[$left][$right]=$best; } }\nmy $result = $dp[0][$m2-1];",
    "c": "int m0=n; int* b=(int*)malloc(sizeof(int)*(m0+2)); b[0]=1; b[m0+1]=1; for (int i=0;i<m0;i++) b[i+1]=nums[i]; int m2=m0+2;\nlong long** dp=(long long**)malloc(sizeof(long long*)*m2);\nfor (int i=0;i<m2;i++) dp[i]=(long long*)calloc(m2,sizeof(long long));\nfor (int len=2;len<m2;len++) { for (int left=0;left+len<m2;left++) { int right=left+len; long long best=0; for (int k=left+1;k<right;k++) { long long val=dp[left][k]+dp[k][right]+(long long)b[left]*b[k]*b[right]; if (val>best) best=val; } dp[left][right]=best; } }\nlong long result = dp[0][m2-1];",
    "rust": "let mut b: Vec<i64> = vec![1]; b.extend(nums.iter().map(|&x| x as i64)); b.push(1); let m2 = b.len();\nlet mut dp = vec![vec![0i64; m2]; m2];\nfor len in 2..m2 { for left in 0..(m2-len) { let right = left+len; let mut best = 0i64; for k in (left+1)..right { let val = dp[left][k]+dp[k][right]+b[left]*b[k]*b[right]; if val>best { best=val; } } dp[left][right]=best; } }\nlet result: i64 = dp[0][m2-1];",
})

# ── arr1_int problems (reused shape) ────────────────────────────────────────

add("task-scheduler", "arr1_int", "least_interval", "int", {
    "javascript": "const total = nums.reduce((a,b)=>a+b,0); const maxCount = Math.max(...nums); let numMax=0; for (const x of nums) if (x===maxCount) numMax++;\nlet result = Math.max(total, (maxCount-1)*(extra+1)+numMax);",
    "typescript": "const total: number = nums.reduce((a,b)=>a+b,0); const maxCount = Math.max(...nums); let numMax=0; for (const x of nums) if (x===maxCount) numMax++;\nlet result: number = Math.max(total, (maxCount-1)*(extra+1)+numMax);",
    "java": "long total=0; for (int x: nums) total+=x; int maxCount=0; for (int x: nums) maxCount=Math.max(maxCount,x); long numMax=0; for (int x: nums) if (x==maxCount) numMax++;\nlong result = Math.max(total, (long)(maxCount-1)*(extra+1)+numMax);",
    "cpp": "long long total=0; for (int x: nums) total+=x; int maxCount=0; for (int x: nums) maxCount=max(maxCount,x); long long numMax=0; for (int x: nums) if (x==maxCount) numMax++;\nlong long result = max(total, (long long)(maxCount-1)*(extra+1)+numMax);",
    "csharp": "long total=0; foreach (int x in nums) total+=x; int maxCount=0; foreach (int x in nums) maxCount=Math.Max(maxCount,x); long numMax=0; foreach (int x in nums) if (x==maxCount) numMax++;\nlong result = Math.Max(total, (long)(maxCount-1)*(extra+1)+numMax);",
    "perl": "my $total=0; for my $x (@$nums) { $total+=$x; }\nmy $maxCount=0; for my $x (@$nums) { $maxCount=$x if $x>$maxCount; }\nmy $numMax=0; for my $x (@$nums) { $numMax++ if $x==$maxCount; }\nmy $alt = ($maxCount-1)*($extra+1)+$numMax;\nmy $result = $total > $alt ? $total : $alt;",
    "c": "long long total=0; for(int i=0;i<n;i++) total+=nums[i];\nint maxCount=0; for(int i=0;i<n;i++) if(nums[i]>maxCount) maxCount=nums[i];\nlong long numMax=0; for(int i=0;i<n;i++) if(nums[i]==maxCount) numMax++;\nlong long alt = (long long)(maxCount-1)*(extra+1)+numMax;\nlong long result = total>alt ? total : alt;",
    "rust": "let total: i64 = nums.iter().map(|&x| x as i64).sum();\nlet max_count = *nums.iter().max().unwrap();\nlet num_max: i64 = nums.iter().filter(|&&x| x==max_count).count() as i64;\nlet alt: i64 = (max_count as i64 - 1)*(extra as i64+1)+num_max;\nlet result: i64 = total.max(alt);",
})

add("coin-change", "arr1_int", "coin_change", "int", {
    "javascript": "const dp = new Array(extra+1).fill(Infinity); dp[0]=0;\nfor (let i=1;i<=extra;i++) { for (const c of nums) { if (c<=i && dp[i-c]+1<dp[i]) dp[i]=dp[i-c]+1; } }\nlet result = dp[extra]===Infinity ? -1 : dp[extra];",
    "typescript": "const dp: number[] = new Array(extra+1).fill(Infinity); dp[0]=0;\nfor (let i=1;i<=extra;i++) { for (const c of nums) { if (c<=i && dp[i-c]+1<dp[i]) dp[i]=dp[i-c]+1; } }\nlet result: number = dp[extra]===Infinity ? -1 : dp[extra];",
    "java": "long INF=Long.MAX_VALUE/2; long[] dp=new long[extra+1]; Arrays.fill(dp, INF); dp[0]=0;\nfor (int i=1;i<=extra;i++) { for (int c: nums) { if (c<=i && dp[i-c]+1<dp[i]) dp[i]=dp[i-c]+1; } }\nlong result = dp[extra]>=INF ? -1 : dp[extra];",
    "cpp": "long long INF=LLONG_MAX/2; vector<long long> dp(extra+1, INF); dp[0]=0;\nfor (int i=1;i<=extra;i++) { for (int c: nums) { if (c<=i && dp[i-c]+1<dp[i]) dp[i]=dp[i-c]+1; } }\nlong long result = dp[extra]>=INF ? -1 : dp[extra];",
    "csharp": "long INF=long.MaxValue/2; long[] dp=new long[extra+1]; for(int i=0;i<=extra;i++) dp[i]=INF; dp[0]=0;\nfor (int i=1;i<=extra;i++) { foreach (int c in nums) { if (c<=i && dp[i-c]+1<dp[i]) dp[i]=dp[i-c]+1; } }\nlong result = dp[extra]>=INF ? -1 : dp[extra];",
    "perl": "my @dp=(1000000000) x ($extra+1); $dp[0]=0;\nfor (my $i=1;$i<=$extra;$i++) { for my $c (@$nums) { if ($c<=$i && $dp[$i-$c]+1<$dp[$i]) { $dp[$i]=$dp[$i-$c]+1; } } }\nmy $result = $dp[$extra]>=1000000000 ? -1 : $dp[$extra];",
    "c": "long long INF=9000000000000000LL; long long* dp=(long long*)malloc(sizeof(long long)*(extra+1)); for(int i=0;i<=extra;i++) dp[i]=INF; dp[0]=0;\nfor (int i=1;i<=extra;i++) { for (int k=0;k<n;k++) { int c=nums[k]; if (c<=i && dp[i-c]+1<dp[i]) dp[i]=dp[i-c]+1; } }\nlong long result = dp[extra]>=INF ? -1 : dp[extra];",
    "rust": "let target = extra as usize; let inf: i64 = i64::MAX/2;\nlet mut dp = vec![inf; target+1]; dp[0]=0;\nfor i in 1..=target { for &c in nums.iter() { let cu = c as usize; if cu<=i && dp[i-cu]+1<dp[i] { dp[i]=dp[i-cu]+1; } } }\nlet result: i64 = if dp[target]>=inf { -1 } else { dp[target] };",
})

add("coin-change-ways", "arr1_int", "change", "int", {
    "javascript": "const dp = new Array(extra+1).fill(0); dp[0]=1;\nfor (const c of nums) { for (let i=c;i<=extra;i++) { dp[i]+=dp[i-c]; } }\nlet result = dp[extra];",
    "typescript": "const dp: number[] = new Array(extra+1).fill(0); dp[0]=1;\nfor (const c of nums) { for (let i=c;i<=extra;i++) { dp[i]+=dp[i-c]; } }\nlet result: number = dp[extra];",
    "java": "long[] dp=new long[extra+1]; dp[0]=1;\nfor (int c: nums) { for (int i=c;i<=extra;i++) { dp[i]+=dp[i-c]; } }\nlong result = dp[extra];",
    "cpp": "vector<long long> dp(extra+1,0); dp[0]=1;\nfor (int c: nums) { for (int i=c;i<=extra;i++) { dp[i]+=dp[i-c]; } }\nlong long result = dp[extra];",
    "csharp": "long[] dp=new long[extra+1]; dp[0]=1;\nforeach (int c in nums) { for (int i=c;i<=extra;i++) { dp[i]+=dp[i-c]; } }\nlong result = dp[extra];",
    "perl": "my @dp=(0) x ($extra+1); $dp[0]=1;\nfor my $c (@$nums) { for (my $i=$c;$i<=$extra;$i++) { $dp[$i]+=$dp[$i-$c]; } }\nmy $result = $dp[$extra];",
    "c": "long long* dp=(long long*)calloc(extra+1,sizeof(long long)); dp[0]=1;\nfor (int k=0;k<n;k++) { int c=nums[k]; for (int i=c;i<=extra;i++) { dp[i]+=dp[i-c]; } }\nlong long result = dp[extra];",
    "rust": "let target = extra as usize;\nlet mut dp = vec![0i64; target+1]; dp[0]=1;\nfor &c in nums.iter() { let cu = c as usize; for i in cu..=target { dp[i]+=dp[i-cu]; } }\nlet result: i64 = dp[target];",
})

# ── arr2_samelen / arr2_int / triangle problems ─────────────────────────────

add("job-scheduling", "arr2_samelen", "job_scheduling", "int", {
    "javascript": "const m2=a.length; const idx=Array.from({length:m2},(_,i)=>i); idx.sort((x,y)=>b[y]-b[x]);\nconst maxD = Math.max(...a); const slot=new Array(maxD+1).fill(false); let total=0;\nfor (const i of idx) { for (let d=a[i]; d>=1; d--) { if (!slot[d]) { slot[d]=true; total+=b[i]; break; } } }\nlet result = total;",
    "typescript": "const m2=a.length; const idx=Array.from({length:m2},(_,i)=>i); idx.sort((x,y)=>b[y]-b[x]);\nconst maxD = Math.max(...a); const slot: boolean[]=new Array(maxD+1).fill(false); let total=0;\nfor (const i of idx) { for (let d=a[i]; d>=1; d--) { if (!slot[d]) { slot[d]=true; total+=b[i]; break; } } }\nlet result: number = total;",
    "java": "int m2=a.length; Integer[] idx=new Integer[m2]; for (int i=0;i<m2;i++) idx[i]=i; Arrays.sort(idx, (x,y)->b[y]-b[x]);\nint maxD=0; for (int x: a) maxD=Math.max(maxD,x); boolean[] slot=new boolean[maxD+1]; long total=0;\nfor (int i: idx) { for (int d=a[i]; d>=1; d--) { if (!slot[d]) { slot[d]=true; total+=b[i]; break; } } }\nlong result = total;",
    "cpp": "int m2=(int)a.size(); vector<int> idx(m2); for (int i=0;i<m2;i++) idx[i]=i; sort(idx.begin(), idx.end(), [&](int x,int y){ return b[x]>b[y]; });\nint maxD=0; for (int x: a) maxD=max(maxD,x); vector<char> slot(maxD+1,0); long long total=0;\nfor (int i: idx) { for (int d=a[i]; d>=1; d--) { if (!slot[d]) { slot[d]=1; total+=b[i]; break; } } }\nlong long result = total;",
    "csharp": "int m2=a.Length; int[] idx=new int[m2]; for (int i=0;i<m2;i++) idx[i]=i; Array.Sort(idx, (x,y)=>b[y]-b[x]);\nint maxD=0; foreach (int x in a) maxD=Math.Max(maxD,x); bool[] slot=new bool[maxD+1]; long total=0;\nforeach (int i in idx) { for (int d=a[i]; d>=1; d--) { if (!slot[d]) { slot[d]=true; total+=b[i]; break; } } }\nlong result = total;",
    "perl": "my $m2=scalar(@$arrA); my @idx=(0..$m2-1);\n@idx = sort { $arrB->[$b] <=> $arrB->[$a] } @idx;\nmy $maxD=0; for my $x (@$arrA) { $maxD=$x if $x>$maxD; }\nmy @slot=(0) x ($maxD+1); my $total=0;\nfor my $i (@idx) { for (my $d=$arrA->[$i]; $d>=1; $d--) { unless ($slot[$d]) { $slot[$d]=1; $total+=$arrB->[$i]; last; } } }\nmy $result = $total;",
    "c": "int m2=n; int* idx=(int*)malloc(sizeof(int)*m2); for (int i=0;i<m2;i++) idx[i]=i;\nfor (int i=0;i<m2;i++) for (int j=0;j<m2-i-1;j++) { if (b[idx[j]]<b[idx[j+1]]) { int tmp=idx[j]; idx[j]=idx[j+1]; idx[j+1]=tmp; } }\nint maxD=0; for (int i=0;i<m2;i++) if (a[i]>maxD) maxD=a[i];\nchar* slot=(char*)calloc(maxD+1,1); long long total=0;\nfor (int ii=0;ii<m2;ii++) { int i=idx[ii]; for (int d=a[i]; d>=1; d--) { if (!slot[d]) { slot[d]=1; total+=b[i]; break; } } }\nlong long result = total;",
    "rust": "let m2 = a.len(); let mut idx: Vec<usize> = (0..m2).collect(); idx.sort_by(|&x,&y| b[y].cmp(&b[x]));\nlet maxd = *a.iter().max().unwrap() as usize; let mut slot = vec![false; maxd+1]; let mut total: i64 = 0;\nfor &i in idx.iter() { let mut d = a[i] as i64; while d >= 1 { if !slot[d as usize] { slot[d as usize]=true; total += b[i] as i64; break; } d -= 1; } }\nlet result: i64 = total;",
})

add("meeting-rooms", "arr2_samelen", "min_meeting_rooms", "int", {
    "javascript": "const starts=[...a].sort((x,y)=>x-y); const ends=[...b].sort((x,y)=>x-y);\nlet rooms=0, best=0, si=0, ei=0;\nwhile (si<starts.length) { if (starts[si]<ends[ei]) { rooms++; best=Math.max(best,rooms); si++; } else { rooms--; ei++; } }\nlet result = best;",
    "typescript": "const starts=[...a].sort((x,y)=>x-y); const ends=[...b].sort((x,y)=>x-y);\nlet rooms=0, best=0, si=0, ei=0;\nwhile (si<starts.length) { if (starts[si]<ends[ei]) { rooms++; best=Math.max(best,rooms); si++; } else { rooms--; ei++; } }\nlet result: number = best;",
    "java": "int[] starts=a.clone(); int[] ends=b.clone(); Arrays.sort(starts); Arrays.sort(ends);\nint rooms=0; long best=0; int si=0, ei=0;\nwhile (si<starts.length) { if (starts[si]<ends[ei]) { rooms++; best=Math.max(best,rooms); si++; } else { rooms--; ei++; } }\nlong result = best;",
    "cpp": "vector<int> starts=a, ends=b; sort(starts.begin(),starts.end()); sort(ends.begin(),ends.end());\nint rooms=0; long long best=0; int si=0, ei=0;\nwhile (si<(int)starts.size()) { if (starts[si]<ends[ei]) { rooms++; best=max(best,(long long)rooms); si++; } else { rooms--; ei++; } }\nlong long result = best;",
    "csharp": "int[] starts=(int[])a.Clone(); int[] ends=(int[])b.Clone(); Array.Sort(starts); Array.Sort(ends);\nint rooms=0; long best=0; int si=0, ei=0;\nwhile (si<starts.Length) { if (starts[si]<ends[ei]) { rooms++; best=Math.Max(best,rooms); si++; } else { rooms--; ei++; } }\nlong result = best;",
    "perl": "my @starts = sort { $a <=> $b } @$arrA; my @ends = sort { $a <=> $b } @$arrB;\nmy $rooms=0; my $best=0; my $si=0; my $ei=0;\nwhile ($si<scalar(@starts)) { if ($starts[$si]<$ends[$ei]) { $rooms++; $best=$rooms if $rooms>$best; $si++; } else { $rooms--; $ei++; } }\nmy $result = $best;",
    "c": "int* starts=(int*)malloc(sizeof(int)*n); int* ends=(int*)malloc(sizeof(int)*n);\nfor (int i=0;i<n;i++) { starts[i]=a[i]; ends[i]=b[i]; }\nfor (int i=0;i<n;i++) for (int j=0;j<n-i-1;j++) { if (starts[j]>starts[j+1]) { int t=starts[j]; starts[j]=starts[j+1]; starts[j+1]=t; } if (ends[j]>ends[j+1]) { int t=ends[j]; ends[j]=ends[j+1]; ends[j+1]=t; } }\nint rooms=0; long long best=0; int si=0, ei=0;\nwhile (si<n) { if (starts[si]<ends[ei]) { rooms++; if (rooms>best) best=rooms; si++; } else { rooms--; ei++; } }\nlong long result = best;",
    "rust": "let mut starts = a.clone(); let mut ends = b.clone(); starts.sort(); ends.sort();\nlet mut rooms: i64 = 0; let mut best: i64 = 0; let mut si = 0usize; let mut ei = 0usize;\nwhile si < starts.len() { if starts[si] < ends[ei] { rooms += 1; if rooms > best { best = rooms; } si += 1; } else { rooms -= 1; ei += 1; } }\nlet result: i64 = best;",
})

add("unbounded-knapsack", "arr2_int", "unbounded_knapsack", "int", {
    "javascript": "const dp = new Array(extra+1).fill(0);\nfor (let c=1;c<=extra;c++) { for (let i=0;i<a.length;i++) { if (a[i]<=c) dp[c]=Math.max(dp[c], dp[c-a[i]]+b[i]); } }\nlet result = dp[extra];",
    "typescript": "const dp: number[] = new Array(extra+1).fill(0);\nfor (let c=1;c<=extra;c++) { for (let i=0;i<a.length;i++) { if (a[i]<=c) dp[c]=Math.max(dp[c], dp[c-a[i]]+b[i]); } }\nlet result: number = dp[extra];",
    "java": "long[] dp=new long[extra+1];\nfor (int c=1;c<=extra;c++) { for (int i=0;i<a.length;i++) { if (a[i]<=c) dp[c]=Math.max(dp[c], dp[c-a[i]]+b[i]); } }\nlong result = dp[extra];",
    "cpp": "vector<long long> dp(extra+1,0);\nfor (int c=1;c<=extra;c++) { for (int i=0;i<(int)a.size();i++) { if (a[i]<=c) dp[c]=max(dp[c], dp[c-a[i]]+b[i]); } }\nlong long result = dp[extra];",
    "csharp": "long[] dp=new long[extra+1];\nfor (int c=1;c<=extra;c++) { for (int i=0;i<a.Length;i++) { if (a[i]<=c) dp[c]=Math.Max(dp[c], dp[c-a[i]]+b[i]); } }\nlong result = dp[extra];",
    "perl": "my @dp=(0) x ($extra+1);\nfor (my $c=1;$c<=$extra;$c++) { for (my $i=0;$i<scalar(@$arrA);$i++) { if ($arrA->[$i]<=$c) { my $v=$dp[$c-$arrA->[$i]]+$arrB->[$i]; $dp[$c]=$v if $v>$dp[$c]; } } }\nmy $result = $dp[$extra];",
    "c": "long long* dp=(long long*)calloc(extra+1,sizeof(long long));\nfor (int c=1;c<=extra;c++) { for (int i=0;i<n;i++) { if (a[i]<=c) { long long v=dp[c-a[i]]+b[i]; if (v>dp[c]) dp[c]=v; } } }\nlong long result = dp[extra];",
    "rust": "let cap = extra as usize;\nlet mut dp = vec![0i64; cap+1];\nfor c in 1..=cap { for i in 0..a.len() { let w = a[i] as usize; if w<=c { let v = dp[c-w]+b[i] as i64; if v>dp[c] { dp[c]=v; } } } }\nlet result: i64 = dp[cap];",
})

add("triangle-minimum-path-sum", "triangle", "minimum_total", "int", {
    "javascript": "const m2=triangle.length;\nlet dp = triangle[m2-1].slice();\nfor (let i=m2-2;i>=0;i--) { const next=new Array(i+1); for (let j=0;j<=i;j++) { next[j]=triangle[i][j]+Math.min(dp[j],dp[j+1]); } dp=next; }\nlet result = m2===0?0:dp[0];",
    "typescript": "const m2=triangle.length;\nlet dp: number[] = triangle[m2-1].slice();\nfor (let i=m2-2;i>=0;i--) { const next: number[]=new Array(i+1); for (let j=0;j<=i;j++) { next[j]=triangle[i][j]+Math.min(dp[j],dp[j+1]); } dp=next; }\nlet result: number = m2===0?0:dp[0];",
    "java": "int m2=triangle.length;\nlong[] dp=new long[m2]; if (m2>0) for (int j=0;j<m2;j++) dp[j]=triangle[m2-1][j];\nfor (int i=m2-2;i>=0;i--) { long[] next=new long[i+1]; for (int j=0;j<=i;j++) { next[j]=triangle[i][j]+Math.min(dp[j],dp[j+1]); } dp=next; }\nlong result = m2==0?0:dp[0];",
    "cpp": "int m2=(int)triangle.size();\nvector<long long> dp(m2>0?m2:0); if (m2>0) for (int j=0;j<m2;j++) dp[j]=triangle[m2-1][j];\nfor (int i=m2-2;i>=0;i--) { vector<long long> next(i+1); for (int j=0;j<=i;j++) { next[j]=triangle[i][j]+min(dp[j],dp[j+1]); } dp=next; }\nlong long result = m2==0?0:dp[0];",
    "csharp": "int m2=triangle.Length;\nlong[] dp=new long[m2>0?m2:1]; if (m2>0) for (int j=0;j<m2;j++) dp[j]=triangle[m2-1][j];\nfor (int i=m2-2;i>=0;i--) { long[] next=new long[i+1]; for (int j=0;j<=i;j++) { next[j]=triangle[i][j]+Math.Min(dp[j],dp[j+1]); } dp=next; }\nlong result = m2==0?0:dp[0];",
    "perl": "my $m2=scalar(@$triangle);\nmy @dp = $m2>0 ? @{$triangle->[$m2-1]} : ();\nfor (my $i=$m2-2;$i>=0;$i--) { my @next; for (my $j=0;$j<=$i;$j++) { my $mn = $dp[$j]<$dp[$j+1] ? $dp[$j] : $dp[$j+1]; $next[$j]=$triangle->[$i][$j]+$mn; } @dp=@next; }\nmy $result = $m2==0 ? 0 : $dp[0];",
    "c": "int m2=n;\nlong long* dp=(long long*)malloc(sizeof(long long)*(m2>0?m2:1)); if (m2>0) for (int j=0;j<m2;j++) dp[j]=triangle[m2-1][j];\nfor (int i=m2-2;i>=0;i--) { long long* next=(long long*)malloc(sizeof(long long)*(i+1)); for (int j=0;j<=i;j++) { long long mn = dp[j]<dp[j+1]?dp[j]:dp[j+1]; next[j]=triangle[i][j]+mn; } dp=next; }\nlong long result = m2==0?0:dp[0];",
    "rust": "let m2 = triangle.len();\nlet mut dp: Vec<i64> = if m2>0 { triangle[m2-1].iter().map(|&x| x as i64).collect() } else { Vec::new() };\nfor i in (0..m2.saturating_sub(1)).rev() { let mut next = vec![0i64; i+1]; for j in 0..=i { next[j] = triangle[i][j] as i64 + dp[j].min(dp[j+1]); } dp = next; }\nlet result: i64 = if m2==0 { 0 } else { dp[0] };",
})


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
    program = assemble(lang, shape, fn, kind, body, wrong)
    if pid == "restore-ip-addresses-count":
        prelude = RESTORE_IP_PRELUDE.get(lang, "")
        if prelude:
            marker = sig(lang, shape, fn, kind)
            program = program.replace(marker, prelude + marker, 1)
    if pid == "boolean-parenthesization":
        # str2 shape names the second param `t`, matching (symbols, ops) --
        # ops string is read into `t` already, no extra prelude needed.
        pass
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
        return {"pid": pid, "lang": lang, "outcome": "reference_failed",
                "detail": f"{correct_result.tests_passed}/{correct_result.tests_total} verdict={correct_result.verdict} "
                          f"{(correct_result.compile_output or '')[:200]}",
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
                    adapter_version="program-mega-batch2-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"],
                )

    verified = [r for r in results if r["outcome"] == "verified"]
    failed = [r for r in results if r["outcome"] != "verified"]
    print(f"\nTOTAL: {len(results)}  verified={len(verified)}  failed={len(failed)}")
    if failed:
        print("\nFAILED CELLS:")
        for r in failed:
            print(f"  {r['pid']}/{r['lang']}: {r['outcome']} -- {r['detail'][:160]}")
    con.close()
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
