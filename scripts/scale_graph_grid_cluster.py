"""Scales minimum-path-sum, n-queens, graph-bfs, dijkstra-shortest-path,
kmp-string-matching (Function Mode) across the 8 working languages.
None are bigint-blocked (docs/atlascode-bigint-numeric-audit.json).
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


# ── minimum-path-sum ─────────────────────────────────────────────────────────
def _js_min_path_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "function min_path_sum(grid) {\n"
        "    const m = grid.length, n = grid[0].length;\n"
        "    const dp = Array.from({length:m}, () => new Array(n).fill(0));\n"
        "    dp[0][0] = grid[0][0];\n"
        "    for (let j=1;j<n;j++) dp[0][j] = dp[0][j-1] + grid[0][j];\n"
        "    for (let i=1;i<m;i++) dp[i][0] = dp[i-1][0] + grid[i][0];\n"
        "    for (let i=1;i<m;i++) for (let j=1;j<n;j++) dp[i][j] = grid[i][j] + Math.min(dp[i-1][j], dp[i][j-1]);\n"
        f"    return dp[m-1][n-1]{a};\n"
        "}\n"
    )


def _ts_min_path_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "function min_path_sum(grid: number[][]): number {\n"
        "    const m = grid.length, n = grid[0].length;\n"
        "    const dp: number[][] = Array.from({length:m}, () => new Array(n).fill(0));\n"
        "    dp[0][0] = grid[0][0];\n"
        "    for (let j=1;j<n;j++) dp[0][j] = dp[0][j-1] + grid[0][j];\n"
        "    for (let i=1;i<m;i++) dp[i][0] = dp[i-1][0] + grid[i][0];\n"
        "    for (let i=1;i<m;i++) for (let j=1;j<n;j++) dp[i][j] = grid[i][j] + Math.min(dp[i-1][j], dp[i][j-1]);\n"
        f"    return dp[m-1][n-1]{a};\n"
        "}\n"
    )


def _java_min_path_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public int min_path_sum(int[][] grid) {\n"
        "        int m = grid.length, n = grid[0].length;\n"
        "        int[][] dp = new int[m][n];\n"
        "        dp[0][0] = grid[0][0];\n"
        "        for (int j=1;j<n;j++) dp[0][j] = dp[0][j-1] + grid[0][j];\n"
        "        for (int i=1;i<m;i++) dp[i][0] = dp[i-1][0] + grid[i][0];\n"
        "        for (int i=1;i<m;i++) for (int j=1;j<n;j++) dp[i][j] = grid[i][j] + Math.min(dp[i-1][j], dp[i][j-1]);\n"
        f"        return dp[m-1][n-1]{a};\n"
        "    }\n"
        "}\n"
    )


def _cpp_min_path_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "public:\n"
        "    int min_path_sum(std::vector<std::vector<int>> grid) {\n"
        "        int m = grid.size(), n = grid[0].size();\n"
        "        std::vector<std::vector<int>> dp(m, std::vector<int>(n, 0));\n"
        "        dp[0][0] = grid[0][0];\n"
        "        for (int j=1;j<n;j++) dp[0][j] = dp[0][j-1] + grid[0][j];\n"
        "        for (int i=1;i<m;i++) dp[i][0] = dp[i-1][0] + grid[i][0];\n"
        "        for (int i=1;i<m;i++) for (int j=1;j<n;j++) dp[i][j] = grid[i][j] + std::min(dp[i-1][j], dp[i][j-1]);\n"
        f"        return dp[m-1][n-1]{a};\n"
        "    }\n"
        "};\n"
    )


def _csharp_min_path_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public static int min_path_sum(int[][] grid) {\n"
        "        int m = grid.Length, n = grid[0].Length;\n"
        "        int[,] dp = new int[m,n];\n"
        "        dp[0,0] = grid[0][0];\n"
        "        for (int j=1;j<n;j++) dp[0,j] = dp[0,j-1] + grid[0][j];\n"
        "        for (int i=1;i<m;i++) dp[i,0] = dp[i-1,0] + grid[i][0];\n"
        "        for (int i=1;i<m;i++) for (int j=1;j<n;j++) dp[i,j] = grid[i][j] + System.Math.Min(dp[i-1,j], dp[i,j-1]);\n"
        f"        return dp[m-1,n-1]{a};\n"
        "    }\n"
        "}\n"
    )


def _perl_min_path_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "sub min_path_sum {\n"
        "    my ($grid) = @_;\n"
        "    my $m = scalar(@$grid); my $n = scalar(@{$grid->[0]});\n"
        "    my @dp;\n"
        "    $dp[0][0] = $grid->[0][0];\n"
        "    for (my $j=1;$j<$n;$j++) { $dp[0][$j] = $dp[0][$j-1] + $grid->[0][$j]; }\n"
        "    for (my $i=1;$i<$m;$i++) { $dp[$i][0] = $dp[$i-1][0] + $grid->[$i][0]; }\n"
        "    for (my $i=1;$i<$m;$i++) {\n"
        "        for (my $j=1;$j<$n;$j++) {\n"
        "            my $mn = ($dp[$i-1][$j] < $dp[$i][$j-1]) ? $dp[$i-1][$j] : $dp[$i][$j-1];\n"
        "            $dp[$i][$j] = $grid->[$i][$j] + $mn;\n"
        "        }\n"
        "    }\n"
        f"    return $dp[$m-1][$n-1]{a};\n"
        "}\n"
    )


def _c_min_path_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "int min_path_sum(AtlasIntMatrix grid) {\n"
        "    int m = grid.size, n = grid.data[0].size;\n"
        "    int** dp = (int**)malloc(sizeof(int*)*m);\n"
        "    for (int i=0;i<m;i++) dp[i] = (int*)calloc(n, sizeof(int));\n"
        "    dp[0][0] = grid.data[0].data[0];\n"
        "    for (int j=1;j<n;j++) dp[0][j] = dp[0][j-1] + grid.data[0].data[j];\n"
        "    for (int i=1;i<m;i++) dp[i][0] = dp[i-1][0] + grid.data[i].data[0];\n"
        "    for (int i=1;i<m;i++) for (int j=1;j<n;j++) {\n"
        "        int mn = dp[i-1][j] < dp[i][j-1] ? dp[i-1][j] : dp[i][j-1];\n"
        "        dp[i][j] = grid.data[i].data[j] + mn;\n"
        "    }\n"
        f"    int result = dp[m-1][n-1]{a};\n"
        "    for (int i=0;i<m;i++) free(dp[i]);\n"
        "    free(dp);\n"
        "    return result;\n"
        "}\n"
    )


def _rust_min_path_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn min_path_sum(grid: Vec<Vec<i32>>) -> i32 {\n"
        "    let m = grid.len(); let n = grid[0].len();\n"
        "    let mut dp = vec![vec![0i32; n]; m];\n"
        "    dp[0][0] = grid[0][0];\n"
        "    for j in 1..n { dp[0][j] = dp[0][j-1] + grid[0][j]; }\n"
        "    for i in 1..m { dp[i][0] = dp[i-1][0] + grid[i][0]; }\n"
        "    for i in 1..m { for j in 1..n { dp[i][j] = grid[i][j] + dp[i-1][j].min(dp[i][j-1]); } }\n"
        f"    dp[m-1][n-1]{a}\n"
        "}\n"
    )


# ── n-queens ─────────────────────────────────────────────────────────────────
def _js_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (
        "function solve_n_queens(n) {\n"
        "    if (n === 0) return 1;\n"
        "    let count = 0;\n"
        "    const cols = new Set(), d1 = new Set(), d2 = new Set();\n"
        "    function backtrack(row) {\n"
        "        if (row === n) { count++; return; }\n"
        "        for (let col=0;col<n;col++) {\n"
        "            if (cols.has(col) || d1.has(row-col) || d2.has(row+col)) continue;\n"
        "            cols.add(col); d1.add(row-col); d2.add(row+col);\n"
        "            backtrack(row+1);\n"
        "            cols.delete(col); d1.delete(row-col); d2.delete(row+col);\n"
        "        }\n"
        "    }\n"
        "    backtrack(0);\n"
        f"    return count{a};\n"
        "}\n"
    )


def _ts_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (
        "function solve_n_queens(n: number): number {\n"
        "    if (n === 0) return 1;\n"
        "    let count = 0;\n"
        "    const cols = new Set<number>(), d1 = new Set<number>(), d2 = new Set<number>();\n"
        "    function backtrack(row: number): void {\n"
        "        if (row === n) { count++; return; }\n"
        "        for (let col=0;col<n;col++) {\n"
        "            if (cols.has(col) || d1.has(row-col) || d2.has(row+col)) continue;\n"
        "            cols.add(col); d1.add(row-col); d2.add(row+col);\n"
        "            backtrack(row+1);\n"
        "            cols.delete(col); d1.delete(row-col); d2.delete(row+col);\n"
        "        }\n"
        "    }\n"
        "    backtrack(0);\n"
        f"    return count{a};\n"
        "}\n"
    )


def _java_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    int count = 0;\n"
        "    public int solve_n_queens(int n) {\n"
        "        if (n == 0) return 1;\n"
        "        count = 0;\n"
        "        boolean[] cols = new boolean[2*n+1]; boolean[] d1 = new boolean[4*n+1]; boolean[] d2 = new boolean[4*n+1];\n"
        "        backtrack(0, n, cols, d1, d2, 2*n);\n"
        f"        return count{a};\n"
        "    }\n"
        "    void backtrack(int row, int n, boolean[] cols, boolean[] d1, boolean[] d2, int off) {\n"
        "        if (row == n) { count++; return; }\n"
        "        for (int col=0;col<n;col++) {\n"
        "            int i1 = row-col+off, i2 = row+col;\n"
        "            if (cols[col] || d1[i1] || d2[i2]) continue;\n"
        "            cols[col]=true; d1[i1]=true; d2[i2]=true;\n"
        "            backtrack(row+1, n, cols, d1, d2, off);\n"
        "            cols[col]=false; d1[i1]=false; d2[i2]=false;\n"
        "        }\n"
        "    }\n"
        "}\n"
    )


def _cpp_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "public:\n"
        "    int count = 0;\n"
        "    int solve_n_queens(int n) {\n"
        "        if (n == 0) return 1;\n"
        "        count = 0;\n"
        "        std::vector<bool> cols(n, false), d1(4*n+1, false), d2(4*n+1, false);\n"
        "        backtrack(0, n, cols, d1, d2, 2*n);\n"
        f"        return count{a};\n"
        "    }\n"
        "    void backtrack(int row, int n, std::vector<bool>& cols, std::vector<bool>& d1, std::vector<bool>& d2, int off) {\n"
        "        if (row == n) { count++; return; }\n"
        "        for (int col=0;col<n;col++) {\n"
        "            int i1 = row-col+off, i2 = row+col;\n"
        "            if (cols[col] || d1[i1] || d2[i2]) continue;\n"
        "            cols[col]=true; d1[i1]=true; d2[i2]=true;\n"
        "            backtrack(row+1, n, cols, d1, d2, off);\n"
        "            cols[col]=false; d1[i1]=false; d2[i2]=false;\n"
        "        }\n"
        "    }\n"
        "};\n"
    )


def _csharp_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    static int count = 0;\n"
        "    public static int solve_n_queens(int n) {\n"
        "        if (n == 0) return 1;\n"
        "        count = 0;\n"
        "        var cols = new bool[n]; var d1 = new bool[4*n+1]; var d2 = new bool[4*n+1];\n"
        "        Backtrack(0, n, cols, d1, d2, 2*n);\n"
        f"        return count{a};\n"
        "    }\n"
        "    static void Backtrack(int row, int n, bool[] cols, bool[] d1, bool[] d2, int off) {\n"
        "        if (row == n) { count++; return; }\n"
        "        for (int col=0;col<n;col++) {\n"
        "            int i1 = row-col+off, i2 = row+col;\n"
        "            if (cols[col] || d1[i1] || d2[i2]) continue;\n"
        "            cols[col]=true; d1[i1]=true; d2[i2]=true;\n"
        "            Backtrack(row+1, n, cols, d1, d2, off);\n"
        "            cols[col]=false; d1[i1]=false; d2[i2]=false;\n"
        "        }\n"
        "    }\n"
        "}\n"
    )


def _perl_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (
        "my $count;\n"
        "sub solve_n_queens {\n"
        "    my ($n) = @_;\n"
        "    return 1 if $n == 0;\n"
        "    $count = 0;\n"
        "    my %cols; my %d1; my %d2;\n"
        "    backtrack(0, $n, \\%cols, \\%d1, \\%d2);\n"
        f"    return {'$count + 1' if wrong else '$count'};\n"
        "}\n"
        "sub backtrack {\n"
        "    my ($row, $n, $cols, $d1, $d2) = @_;\n"
        "    if ($row == $n) { $count++; return; }\n"
        "    for (my $col=0;$col<$n;$col++) {\n"
        "        next if exists $cols->{$col} || exists $d1->{$row-$col} || exists $d2->{$row+$col};\n"
        "        $cols->{$col}=1; $d1->{$row-$col}=1; $d2->{$row+$col}=1;\n"
        "        backtrack($row+1, $n, $cols, $d1, $d2);\n"
        "        delete $cols->{$col}; delete $d1->{$row-$col}; delete $d2->{$row+$col};\n"
        "    }\n"
        "}\n"
    )


_C_NQUEENS_HELPER = (
    "static int g_count;\n"
    "static void nqueens_backtrack(int row, int n, int* cols, int* d1, int* d2, int off) {\n"
    "    if (row == n) { g_count++; return; }\n"
    "    for (int col=0;col<n;col++) {\n"
    "        int i1 = row-col+off, i2 = row+col;\n"
    "        if (cols[col] || d1[i1] || d2[i2]) continue;\n"
    "        cols[col]=1; d1[i1]=1; d2[i2]=1;\n"
    "        nqueens_backtrack(row+1, n, cols, d1, d2, off);\n"
    "        cols[col]=0; d1[i1]=0; d2[i2]=0;\n"
    "    }\n"
    "}\n"
)


def _c_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (
        _C_NQUEENS_HELPER +
        "int solve_n_queens(int n) {\n"
        "    if (n == 0) return 1;\n"
        "    g_count = 0;\n"
        "    int* cols = (int*)calloc(n, sizeof(int));\n"
        "    int* d1 = (int*)calloc(4*n+2, sizeof(int));\n"
        "    int* d2 = (int*)calloc(4*n+2, sizeof(int));\n"
        "    nqueens_backtrack(0, n, cols, d1, d2, 2*n);\n"
        "    free(cols); free(d1); free(d2);\n"
        f"    return g_count{a};\n"
        "}\n"
    )


def _rust_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (
        "fn backtrack(row: i32, n: i32, cols: &mut Vec<bool>, d1: &mut Vec<bool>, d2: &mut Vec<bool>, off: i32, count: &mut i32) {\n"
        "    if row == n { *count += 1; return; }\n"
        "    for col in 0..n {\n"
        "        let i1 = (row - col + off) as usize; let i2 = (row + col) as usize;\n"
        "        if cols[col as usize] || d1[i1] || d2[i2] { continue; }\n"
        "        cols[col as usize] = true; d1[i1] = true; d2[i2] = true;\n"
        "        backtrack(row+1, n, cols, d1, d2, off, count);\n"
        "        cols[col as usize] = false; d1[i1] = false; d2[i2] = false;\n"
        "    }\n"
        "}\n"
        "fn solve_n_queens(n: i32) -> i32 {\n"
        "    if n == 0 { return 1; }\n"
        "    let mut count = 0;\n"
        "    let mut cols = vec![false; n as usize];\n"
        "    let mut d1 = vec![false; (4*n+2) as usize];\n"
        "    let mut d2 = vec![false; (4*n+2) as usize];\n"
        "    backtrack(0, n, &mut cols, &mut d1, &mut d2, 2*n, &mut count);\n"
        f"    count{a}\n"
        "}\n"
    )


# ── graph-bfs ────────────────────────────────────────────────────────────────
def _js_bfs(wrong):
    a = " + 1" if wrong else ""
    return (
        "function bfs(adj, src, n) {\n"
        "    const dist = new Array(n).fill(-1); dist[src] = 0;\n"
        "    const q = [src]; let qi = 0;\n"
        "    while (qi < q.length) {\n"
        "        const u = q[qi]; qi++;\n"
        "        for (const v of adj[u]) { if (dist[v] === -1) { dist[v] = dist[u] + 1; q.push(v); } }\n"
        "    }\n"
        f"    return {'dist.map(x => x + 1)' if wrong else 'dist'};\n"
        "}\n"
    )


def _ts_bfs(wrong):
    a = " + 1" if wrong else ""
    return (
        "function bfs(adj: number[][], src: number, n: number): number[] {\n"
        "    const dist: number[] = new Array(n).fill(-1); dist[src] = 0;\n"
        "    const q: number[] = [src]; let qi = 0;\n"
        "    while (qi < q.length) {\n"
        "        const u = q[qi]; qi++;\n"
        "        for (const v of adj[u]) { if (dist[v] === -1) { dist[v] = dist[u] + 1; q.push(v); } }\n"
        "    }\n"
        f"    return {'dist.map(x => x + 1)' if wrong else 'dist'};\n"
        "}\n"
    )


def _java_bfs(wrong):
    return (
        "class Solution {\n"
        "    public int[] bfs(int[][] adj, int src, int n) {\n"
        "        int[] dist = new int[n]; java.util.Arrays.fill(dist, -1); dist[src] = 0;\n"
        "        java.util.ArrayDeque<Integer> q = new java.util.ArrayDeque<>(); q.add(src);\n"
        "        while (!q.isEmpty()) {\n"
        "            int u = q.poll();\n"
        "            for (int v : adj[u]) { if (dist[v] == -1) { dist[v] = dist[u] + 1; q.add(v); } }\n"
        "        }\n"
        + ("        for (int i=0;i<n;i++) dist[i]++;\n" if wrong else "") +
        "        return dist;\n"
        "    }\n"
        "}\n"
    )


def _cpp_bfs(wrong):
    return (
        "class Solution {\n"
        "public:\n"
        "    std::vector<int> bfs(std::vector<std::vector<int>> adj, int src, int n) {\n"
        "        std::vector<int> dist(n, -1); dist[src] = 0;\n"
        "        std::queue<int> q; q.push(src);\n"
        "        while (!q.empty()) {\n"
        "            int u = q.front(); q.pop();\n"
        "            for (int v : adj[u]) { if (dist[v] == -1) { dist[v] = dist[u] + 1; q.push(v); } }\n"
        "        }\n"
        + ("        for (int i=0;i<n;i++) dist[i]++;\n" if wrong else "") +
        "        return dist;\n"
        "    }\n"
        "};\n"
    )


def _csharp_bfs(wrong):
    return (
        "class Solution {\n"
        "    public static int[] bfs(int[][] adj, int src, int n) {\n"
        "        int[] dist = new int[n]; for (int i=0;i<n;i++) dist[i]=-1; dist[src]=0;\n"
        "        var q = new System.Collections.Generic.Queue<int>(); q.Enqueue(src);\n"
        "        while (q.Count > 0) {\n"
        "            int u = q.Dequeue();\n"
        "            foreach (int v in adj[u]) { if (dist[v] == -1) { dist[v] = dist[u] + 1; q.Enqueue(v); } }\n"
        "        }\n"
        + ("        for (int i=0;i<n;i++) dist[i]++;\n" if wrong else "") +
        "        return dist;\n"
        "    }\n"
        "}\n"
    )


def _perl_bfs(wrong):
    return (
        "sub bfs {\n"
        "    my ($adj, $src, $n) = @_;\n"
        "    my @dist = (-1) x $n; $dist[$src] = 0;\n"
        "    my @q = ($src); my $qi = 0;\n"
        "    while ($qi < scalar(@q)) {\n"
        "        my $u = $q[$qi]; $qi++;\n"
        "        foreach my $v (@{$adj->[$u]}) { if ($dist[$v] == -1) { $dist[$v] = $dist[$u] + 1; push @q, $v; } }\n"
        "    }\n"
        + ("    for (my $i=0;$i<$n;$i++) { $dist[$i]++; }\n" if wrong else "") +
        "    return \\@dist;\n"
        "}\n"
    )


def _c_bfs(wrong):
    return (
        "AtlasIntArray bfs(AtlasIntMatrix adj, int src, int n) {\n"
        "    int* dist = (int*)malloc(sizeof(int)*n);\n"
        "    for (int i=0;i<n;i++) dist[i] = -1;\n"
        "    dist[src] = 0;\n"
        "    int* q = (int*)malloc(sizeof(int)*n*n); int qh=0, qt=0;\n"
        "    q[qt++] = src;\n"
        "    while (qh < qt) {\n"
        "        int u = q[qh++];\n"
        "        for (int k=0;k<adj.data[u].size;k++) {\n"
        "            int v = adj.data[u].data[k];\n"
        "            if (dist[v] == -1) { dist[v] = dist[u] + 1; q[qt++] = v; }\n"
        "        }\n"
        "    }\n"
        + ("    for (int i=0;i<n;i++) dist[i]++;\n" if wrong else "") +
        "    AtlasIntArray result; result.size = n; result.data = dist;\n"
        "    free(q);\n"
        "    return result;\n"
        "}\n"
    )


def _rust_bfs(wrong):
    return (
        "use std::collections::VecDeque;\n\n"
        "fn bfs(adj: Vec<Vec<i32>>, src: i32, n: i32) -> Vec<i32> {\n"
        "    let mut dist = vec![-1i32; n as usize]; dist[src as usize] = 0;\n"
        "    let mut q: VecDeque<i32> = VecDeque::new(); q.push_back(src);\n"
        "    while let Some(u) = q.pop_front() {\n"
        "        for &v in adj[u as usize].iter() {\n"
        "            if dist[v as usize] == -1 { dist[v as usize] = dist[u as usize] + 1; q.push_back(v); }\n"
        "        }\n"
        "    }\n"
        + ("    for i in 0..n as usize { dist[i] += 1; }\n" if wrong else "") +
        "    dist\n"
        "}\n"
    )


# ── dijkstra-shortest-path ────────────────────────────────────────────────────
def _js_dijkstra(wrong):
    return (
        "function dijkstra(adj, n) {\n"
        "    const INF = Infinity;\n"
        "    const dist = new Array(n).fill(INF); dist[0] = 0;\n"
        "    const visited = new Array(n).fill(false);\n"
        "    for (let iter=0;iter<n;iter++) {\n"
        "        let u = -1, best = INF;\n"
        "        for (let i=0;i<n;i++) if (!visited[i] && dist[i] < best) { best = dist[i]; u = i; }\n"
        "        if (u === -1) break;\n"
        "        visited[u] = true;\n"
        "        for (const [v, w] of adj[u]) { if (dist[u] + w < dist[v]) dist[v] = dist[u] + w; }\n"
        "    }\n"
        "    const out = dist.map(d => d === INF ? -1 : d);\n"
        f"    return {'out.map(x => x === -1 ? -1 : x + 1)' if wrong else 'out'};\n"
        "}\n"
    )


def _ts_dijkstra(wrong):
    return (
        "function dijkstra(adj: number[][][], n: number): number[] {\n"
        "    const INF = Infinity;\n"
        "    const dist: number[] = new Array(n).fill(INF); dist[0] = 0;\n"
        "    const visited: boolean[] = new Array(n).fill(false);\n"
        "    for (let iter=0;iter<n;iter++) {\n"
        "        let u = -1, best = INF;\n"
        "        for (let i=0;i<n;i++) if (!visited[i] && dist[i] < best) { best = dist[i]; u = i; }\n"
        "        if (u === -1) break;\n"
        "        visited[u] = true;\n"
        "        for (const e of adj[u]) { const v = e[0], w = e[1]; if (dist[u] + w < dist[v]) dist[v] = dist[u] + w; }\n"
        "    }\n"
        "    const out = dist.map(d => d === INF ? -1 : d);\n"
        f"    return {'out.map(x => x === -1 ? -1 : x + 1)' if wrong else 'out'};\n"
        "}\n"
    )


def _java_dijkstra(wrong):
    return (
        "class Solution {\n"
        "    public int[] dijkstra(int[][][] adj, int n) {\n"
        "        long INF = Long.MAX_VALUE / 2;\n"
        "        long[] dist = new long[n]; java.util.Arrays.fill(dist, INF); dist[0] = 0;\n"
        "        boolean[] visited = new boolean[n];\n"
        "        for (int iter=0;iter<n;iter++) {\n"
        "            int u = -1; long best = INF;\n"
        "            for (int i=0;i<n;i++) if (!visited[i] && dist[i] < best) { best = dist[i]; u = i; }\n"
        "            if (u == -1) break;\n"
        "            visited[u] = true;\n"
        "            for (int[] e : adj[u]) { int v = e[0], w = e[1]; if (dist[u] + w < dist[v]) dist[v] = dist[u] + w; }\n"
        "        }\n"
        "        int[] out = new int[n];\n"
        "        for (int i=0;i<n;i++) out[i] = dist[i] >= INF ? -1 : (int) dist[i];\n"
        + ("        for (int i=0;i<n;i++) if (out[i] != -1) out[i]++;\n" if wrong else "") +
        "        return out;\n"
        "    }\n"
        "}\n"
    )


def _cpp_dijkstra(wrong):
    return (
        "class Solution {\n"
        "public:\n"
        "    std::vector<int> dijkstra(std::vector<std::vector<std::vector<int>>> adj, int n) {\n"
        "        const long long INF = LLONG_MAX / 2;\n"
        "        std::vector<long long> dist(n, INF); dist[0] = 0;\n"
        "        std::vector<bool> visited(n, false);\n"
        "        for (int iter=0;iter<n;iter++) {\n"
        "            int u = -1; long long best = INF;\n"
        "            for (int i=0;i<n;i++) if (!visited[i] && dist[i] < best) { best = dist[i]; u = i; }\n"
        "            if (u == -1) break;\n"
        "            visited[u] = true;\n"
        "            for (auto& e : adj[u]) { int v = e[0], w = e[1]; if (dist[u] + w < dist[v]) dist[v] = dist[u] + w; }\n"
        "        }\n"
        "        std::vector<int> out(n);\n"
        "        for (int i=0;i<n;i++) out[i] = dist[i] >= INF ? -1 : (int)dist[i];\n"
        + ("        for (int i=0;i<n;i++) if (out[i] != -1) out[i]++;\n" if wrong else "") +
        "        return out;\n"
        "    }\n"
        "};\n"
    )


def _csharp_dijkstra(wrong):
    return (
        "class Solution {\n"
        "    public static int[] dijkstra(int[][][] adj, int n) {\n"
        "        long INF = long.MaxValue / 2;\n"
        "        long[] dist = new long[n]; for (int i=0;i<n;i++) dist[i]=INF; dist[0]=0;\n"
        "        bool[] visited = new bool[n];\n"
        "        for (int iter=0;iter<n;iter++) {\n"
        "            int u = -1; long best = INF;\n"
        "            for (int i=0;i<n;i++) if (!visited[i] && dist[i] < best) { best = dist[i]; u = i; }\n"
        "            if (u == -1) break;\n"
        "            visited[u] = true;\n"
        "            foreach (var e in adj[u]) { int v = e[0], w = e[1]; if (dist[u] + w < dist[v]) dist[v] = dist[u] + w; }\n"
        "        }\n"
        "        int[] outArr = new int[n];\n"
        "        for (int i=0;i<n;i++) outArr[i] = dist[i] >= INF ? -1 : (int)dist[i];\n"
        + ("        for (int i=0;i<n;i++) if (outArr[i] != -1) outArr[i]++;\n" if wrong else "") +
        "        return outArr;\n"
        "    }\n"
        "}\n"
    )


def _perl_dijkstra(wrong):
    return (
        "sub dijkstra {\n"
        "    my ($adj, $n) = @_;\n"
        "    my $INF = 1e18;\n"
        "    my @dist = ($INF) x $n; $dist[0] = 0;\n"
        "    my @visited = (0) x $n;\n"
        "    for (my $iter=0;$iter<$n;$iter++) {\n"
        "        my $u = -1; my $best = $INF;\n"
        "        for (my $i=0;$i<$n;$i++) { if (!$visited[$i] && $dist[$i] < $best) { $best = $dist[$i]; $u = $i; } }\n"
        "        last if $u == -1;\n"
        "        $visited[$u] = 1;\n"
        "        foreach my $e (@{$adj->[$u]}) {\n"
        "            my ($v, $w) = @$e;\n"
        "            if ($dist[$u] + $w < $dist[$v]) { $dist[$v] = $dist[$u] + $w; }\n"
        "        }\n"
        "    }\n"
        "    my @out = map { $_ >= $INF ? -1 : $_ } @dist;\n"
        + ("    @out = map { $_ == -1 ? -1 : $_ + 1 } @out;\n" if wrong else "") +
        "    return \\@out;\n"
        "}\n"
    )


def _c_dijkstra(wrong):
    return (
        "AtlasIntArray dijkstra(AtlasIntCube adj, int n) {\n"
        "    long long INF = 1000000000000LL;\n"
        "    long long* dist = (long long*)malloc(sizeof(long long)*n);\n"
        "    for (int i=0;i<n;i++) dist[i] = INF;\n"
        "    dist[0] = 0;\n"
        "    int* visited = (int*)calloc(n, sizeof(int));\n"
        "    for (int iter=0;iter<n;iter++) {\n"
        "        int u = -1; long long best = INF;\n"
        "        for (int i=0;i<n;i++) if (!visited[i] && dist[i] < best) { best = dist[i]; u = i; }\n"
        "        if (u == -1) break;\n"
        "        visited[u] = 1;\n"
        "        for (int k=0;k<adj.data[u].size;k++) {\n"
        "            int v = adj.data[u].data[k].data[0];\n"
        "            int w = adj.data[u].data[k].data[1];\n"
        "            if (dist[u] + w < dist[v]) dist[v] = dist[u] + w;\n"
        "        }\n"
        "    }\n"
        "    int* out = (int*)malloc(sizeof(int)*n);\n"
        "    for (int i=0;i<n;i++) out[i] = (dist[i] >= INF) ? -1 : (int)dist[i];\n"
        + ("    for (int i=0;i<n;i++) if (out[i] != -1) out[i]++;\n" if wrong else "") +
        "    free(dist); free(visited);\n"
        "    AtlasIntArray result; result.size = n; result.data = out;\n"
        "    return result;\n"
        "}\n"
    )


def _rust_dijkstra(wrong):
    return (
        "fn dijkstra(adj: Vec<Vec<Vec<i32>>>, n: i32) -> Vec<i32> {\n"
        "    let n = n as usize;\n"
        "    const INF: i64 = 1_000_000_000_000;\n"
        "    let mut dist = vec![INF; n]; dist[0] = 0;\n"
        "    let mut visited = vec![false; n];\n"
        "    for _ in 0..n {\n"
        "        let mut u: i32 = -1; let mut best = INF;\n"
        "        for i in 0..n { if !visited[i] && dist[i] < best { best = dist[i]; u = i as i32; } }\n"
        "        if u == -1 { break; }\n"
        "        let u = u as usize;\n"
        "        visited[u] = true;\n"
        "        for e in adj[u].iter() {\n"
        "            let v = e[0] as usize; let w = e[1] as i64;\n"
        "            if dist[u] + w < dist[v] { dist[v] = dist[u] + w; }\n"
        "        }\n"
        "    }\n"
        "    let mut out: Vec<i32> = dist.iter().map(|&d| if d >= INF { -1 } else { d as i32 }).collect();\n"
        + ("    for i in 0..n { if out[i] != -1 { out[i] += 1; } }\n" if wrong else "") +
        "    out\n"
        "}\n"
    )


# ── kmp-string-matching ──────────────────────────────────────────────────────
def _js_kmp(wrong):
    return (
        "function kmp_search(T, P) {\n"
        "    const n = P.length;\n"
        "    const lps = new Array(n).fill(0);\n"
        "    let len = 0, i = 1;\n"
        "    while (i < n) {\n"
        "        if (P[i] === P[len]) { len++; lps[i] = len; i++; }\n"
        "        else if (len !== 0) len = lps[len-1];\n"
        "        else { lps[i] = 0; i++; }\n"
        "    }\n"
        "    const result = [];\n"
        "    let ti = 0, pi = 0;\n"
        "    while (ti < T.length) {\n"
        "        if (T[ti] === P[pi]) { ti++; pi++; if (pi === n) { result.push(ti-pi); pi = lps[pi-1]; } }\n"
        "        else if (pi !== 0) pi = lps[pi-1];\n"
        "        else ti++;\n"
        "    }\n"
        f"    return {'result.map(x => x + 1)' if wrong else 'result'};\n"
        "}\n"
    )


def _ts_kmp(wrong):
    return (
        "function kmp_search(T: string, P: string): number[] {\n"
        "    const n = P.length;\n"
        "    const lps: number[] = new Array(n).fill(0);\n"
        "    let len = 0, i = 1;\n"
        "    while (i < n) {\n"
        "        if (P[i] === P[len]) { len++; lps[i] = len; i++; }\n"
        "        else if (len !== 0) len = lps[len-1];\n"
        "        else { lps[i] = 0; i++; }\n"
        "    }\n"
        "    const result: number[] = [];\n"
        "    let ti = 0, pi = 0;\n"
        "    while (ti < T.length) {\n"
        "        if (T[ti] === P[pi]) { ti++; pi++; if (pi === n) { result.push(ti-pi); pi = lps[pi-1]; } }\n"
        "        else if (pi !== 0) pi = lps[pi-1];\n"
        "        else ti++;\n"
        "    }\n"
        f"    return {'result.map(x => x + 1)' if wrong else 'result'};\n"
        "}\n"
    )


def _java_kmp(wrong):
    return (
        "class Solution {\n"
        "    public int[] kmp_search(String T, String P) {\n"
        "        int n = P.length();\n"
        "        int[] lps = new int[n];\n"
        "        int len = 0, i = 1;\n"
        "        while (i < n) {\n"
        "            if (P.charAt(i) == P.charAt(len)) { len++; lps[i] = len; i++; }\n"
        "            else if (len != 0) len = lps[len-1];\n"
        "            else { lps[i] = 0; i++; }\n"
        "        }\n"
        "        java.util.List<Integer> result = new java.util.ArrayList<>();\n"
        "        int ti = 0, pi = 0;\n"
        "        while (ti < T.length()) {\n"
        "            if (T.charAt(ti) == P.charAt(pi)) { ti++; pi++; if (pi == n) { result.add(ti-pi); pi = lps[pi-1]; } }\n"
        "            else if (pi != 0) pi = lps[pi-1];\n"
        "            else ti++;\n"
        "        }\n"
        "        int[] out = new int[result.size()];\n"
        "        for (int k=0;k<out.length;k++) out[k] = result.get(k)" + (" + 1" if wrong else "") + ";\n"
        "        return out;\n"
        "    }\n"
        "}\n"
    )


def _cpp_kmp(wrong):
    return (
        "class Solution {\n"
        "public:\n"
        "    std::vector<int> kmp_search(std::string T, std::string P) {\n"
        "        int n = P.size();\n"
        "        std::vector<int> lps(n, 0);\n"
        "        int len = 0, i = 1;\n"
        "        while (i < n) {\n"
        "            if (P[i] == P[len]) { len++; lps[i] = len; i++; }\n"
        "            else if (len != 0) len = lps[len-1];\n"
        "            else { lps[i] = 0; i++; }\n"
        "        }\n"
        "        std::vector<int> result;\n"
        "        int ti = 0, pi = 0;\n"
        "        while (ti < (int)T.size()) {\n"
        "            if (T[ti] == P[pi]) { ti++; pi++; if (pi == n) { result.push_back(ti-pi); pi = lps[pi-1]; } }\n"
        "            else if (pi != 0) pi = lps[pi-1];\n"
        "            else ti++;\n"
        "        }\n"
        + ("        for (auto& x : result) x++;\n" if wrong else "") +
        "        return result;\n"
        "    }\n"
        "};\n"
    )


def _csharp_kmp(wrong):
    return (
        "class Solution {\n"
        "    public static int[] kmp_search(string T, string P) {\n"
        "        int n = P.Length;\n"
        "        int[] lps = new int[n];\n"
        "        int len = 0, i = 1;\n"
        "        while (i < n) {\n"
        "            if (P[i] == P[len]) { len++; lps[i] = len; i++; }\n"
        "            else if (len != 0) len = lps[len-1];\n"
        "            else { lps[i] = 0; i++; }\n"
        "        }\n"
        "        var result = new System.Collections.Generic.List<int>();\n"
        "        int ti = 0, pi = 0;\n"
        "        while (ti < T.Length) {\n"
        "            if (T[ti] == P[pi]) { ti++; pi++; if (pi == n) { result.Add(ti-pi); pi = lps[pi-1]; } }\n"
        "            else if (pi != 0) pi = lps[pi-1];\n"
        "            else ti++;\n"
        "        }\n"
        + ("        for (int k=0;k<result.Count;k++) result[k]++;\n" if wrong else "") +
        "        return result.ToArray();\n"
        "    }\n"
        "}\n"
    )


def _perl_kmp(wrong):
    return (
        "sub kmp_search {\n"
        "    my ($T, $P) = @_;\n"
        "    my $n = length($P);\n"
        "    my @lps = (0) x $n;\n"
        "    my $len = 0; my $i = 1;\n"
        "    while ($i < $n) {\n"
        "        if (substr($P,$i,1) eq substr($P,$len,1)) { $len++; $lps[$i] = $len; $i++; }\n"
        "        elsif ($len != 0) { $len = $lps[$len-1]; }\n"
        "        else { $lps[$i] = 0; $i++; }\n"
        "    }\n"
        "    my @result;\n"
        "    my $ti = 0; my $pi = 0;\n"
        "    my $tlen = length($T);\n"
        "    while ($ti < $tlen) {\n"
        "        if (substr($T,$ti,1) eq substr($P,$pi,1)) {\n"
        "            $ti++; $pi++;\n"
        "            if ($pi == $n) { push @result, $ti-$pi; $pi = $lps[$pi-1]; }\n"
        "        }\n"
        "        elsif ($pi != 0) { $pi = $lps[$pi-1]; }\n"
        "        else { $ti++; }\n"
        "    }\n"
        + ("    @result = map { $_ + 1 } @result;\n" if wrong else "") +
        "    return \\@result;\n"
        "}\n"
    )


def _c_kmp(wrong):
    return (
        "AtlasIntArray kmp_search(char* T, char* P) {\n"
        "    int n = 0; while (P[n]) n++;\n"
        "    int tlen = 0; while (T[tlen]) tlen++;\n"
        "    int* lps = (int*)calloc(n, sizeof(int));\n"
        "    int len = 0, i = 1;\n"
        "    while (i < n) {\n"
        "        if (P[i] == P[len]) { len++; lps[i] = len; i++; }\n"
        "        else if (len != 0) len = lps[len-1];\n"
        "        else { lps[i] = 0; i++; }\n"
        "    }\n"
        "    int* result = (int*)malloc(sizeof(int) * (tlen + 1));\n"
        "    int rc = 0;\n"
        "    int ti = 0, pi = 0;\n"
        "    while (ti < tlen) {\n"
        "        if (T[ti] == P[pi]) { ti++; pi++; if (pi == n) { result[rc++] = ti-pi; pi = lps[pi-1]; } }\n"
        "        else if (pi != 0) pi = lps[pi-1];\n"
        "        else ti++;\n"
        "    }\n"
        + ("    for (int k=0;k<rc;k++) result[k]++;\n" if wrong else "") +
        "    free(lps);\n"
        "    AtlasIntArray out; out.size = rc; out.data = result;\n"
        "    return out;\n"
        "}\n"
    )


def _rust_kmp(wrong):
    return (
        "fn kmp_search(t: String, p: String) -> Vec<i32> {\n"
        "    let tb: Vec<u8> = t.bytes().collect();\n"
        "    let pb: Vec<u8> = p.bytes().collect();\n"
        "    let n = pb.len();\n"
        "    let mut lps = vec![0usize; n];\n"
        "    let mut len = 0usize; let mut i = 1usize;\n"
        "    while i < n {\n"
        "        if pb[i] == pb[len] { len += 1; lps[i] = len; i += 1; }\n"
        "        else if len != 0 { len = lps[len-1]; }\n"
        "        else { lps[i] = 0; i += 1; }\n"
        "    }\n"
        "    let mut result: Vec<i32> = Vec::new();\n"
        "    let mut ti = 0usize; let mut pi = 0usize;\n"
        "    while ti < tb.len() {\n"
        "        if tb[ti] == pb[pi] {\n"
        "            ti += 1; pi += 1;\n"
        "            if pi == n { result.push((ti - pi) as i32); pi = lps[pi-1]; }\n"
        "        } else if pi != 0 { pi = lps[pi-1]; }\n"
        "        else { ti += 1; }\n"
        "    }\n"
        + ("    for x in result.iter_mut() { *x += 1; }\n" if wrong else "") +
        "    result\n"
        "}\n"
    )


_BUILDERS = {
    "minimum-path-sum": {"javascript": _js_min_path_sum, "typescript": _ts_min_path_sum, "java": _java_min_path_sum, "cpp": _cpp_min_path_sum,
                         "csharp": _csharp_min_path_sum, "perl": _perl_min_path_sum, "c": _c_min_path_sum, "rust": _rust_min_path_sum},
    "n-queens": {"javascript": _js_nqueens, "typescript": _ts_nqueens, "java": _java_nqueens, "cpp": _cpp_nqueens,
                "csharp": _csharp_nqueens, "perl": _perl_nqueens, "c": _c_nqueens, "rust": _rust_nqueens},
    "graph-bfs": {"javascript": _js_bfs, "typescript": _ts_bfs, "java": _java_bfs, "cpp": _cpp_bfs,
                 "csharp": _csharp_bfs, "perl": _perl_bfs, "c": _c_bfs, "rust": _rust_bfs},
    "dijkstra-shortest-path": {"javascript": _js_dijkstra, "typescript": _ts_dijkstra, "java": _java_dijkstra, "cpp": _cpp_dijkstra,
                               "csharp": _csharp_dijkstra, "perl": _perl_dijkstra, "c": _c_dijkstra, "rust": _rust_dijkstra},
    "kmp-string-matching": {"javascript": _js_kmp, "typescript": _ts_kmp, "java": _java_kmp, "cpp": _cpp_kmp,
                            "csharp": _csharp_kmp, "perl": _perl_kmp, "c": _c_kmp, "rust": _rust_kmp},
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
                          f"stderr={(sample_fail.stderr if sample_fail else '')[:200]}",
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
            print(f"[{status}] {lang:10s} {pid:24s} {r['outcome']:18s} {r['detail'][:130]}", flush=True)
            if r["outcome"] == "verified":
                ledger.record_cell(con, problem_id=pid, language=lang, mode="function",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=f"{lang}-graph-grid-v1", contract_version=cv, test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
