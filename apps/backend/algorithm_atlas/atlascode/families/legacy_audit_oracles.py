"""
Independent, plugin-free reference oracles for the 19 LEGACY curated
AtlasCode problems being upgraded from hand-typed (3-5 case) test data to
the project's 40-test standard (see testgen.py).

These 19 problems already have LIVE `problem_statement` / `starter_code`
rows in the database (curated, not factory-generated) — this module does
NOT touch that data. It only supplies ground-truth answer functions that
`legacy_audit_testdata.py` uses to generate new test cases matching the
EXACT existing stdin/stdout contract of each problem's starter code.

Every function here is written independently of `independent_oracles.py`
and of any plugin/visualization code, per the project's oracle-independence
rule. Where a problem's answer is not unique in general (e.g. two-sum has
many valid index pairs when duplicates exist, BFS-with-ties has many valid
shortest-path trees but only one *distance* vector), the oracle returns the
canonical value implied by the ALREADY-SHIPPED sample I/O in the task
brief — not just any correct answer — since real users are already relying
on that exact contract.
"""
from __future__ import annotations

from collections import deque


class OracleError(Exception):
    """Raised when an oracle is asked to evaluate an input outside its domain."""


# ── binary-search: sorted array, print index or -1 ───────────────────────────

def binary_search_index(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


# ── linear-search: unsorted array, print FIRST index or -1 ───────────────────

def linear_search_first_index(nums: list[int], target: int) -> int:
    for i, x in enumerate(nums):
        if x == target:
            return i
    return -1


# ── bubble-sort: print fully sorted array ─────────────────────────────────────

def bubble_sort_result(nums: list[int]) -> list[int]:
    arr = list(nums)
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


# ── fibonacci-dp: fib(0)=0, fib(1)=1 ─────────────────────────────────────────

def fibonacci(n: int) -> int:
    if n < 0:
        raise OracleError(f"fibonacci undefined for n={n}")
    if n == 0:
        return 0
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


# ── gcd-euclidean ──────────────────────────────────────────────────────────

def gcd_euclidean(a: int, b: int) -> int:
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


# ── two-sum: print a valid index pair, smaller first ─────────────────────────

def two_sum_indices(nums: list[int], target: int) -> tuple[int, int]:
    """Canonical pair: the pair found by the classic single-pass hashmap
    scan (first index seen for the complement wins), matching LeetCode's
    #1 standard contract and the sample I/O in the brief."""
    seen: dict[int, int] = {}
    for i, x in enumerate(nums):
        complement = target - x
        if complement in seen:
            j = seen[complement]
            return (j, i) if j < i else (i, j)
        if x not in seen:
            seen[x] = i
    raise OracleError(f"two_sum: no valid pair for target={target} in {nums}")


# ── maximum-subarray: Kadane's ────────────────────────────────────────────────

def max_subarray(nums: list[int]) -> int:
    if not nums:
        raise OracleError("max_subarray undefined for empty array")
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best


# ── coin-change: min coins to make amount, -1 if impossible ──────────────────

def coin_change_min_coins(coins: list[int], amount: int) -> int:
    if amount < 0:
        raise OracleError(f"coin_change undefined for amount={amount}")
    INF = amount + 1
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] != INF else -1


# ── longest-common-subsequence: length only ──────────────────────────────────

def lcs_length(s1: str, s2: str) -> int:
    n, m = len(s1), len(s2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]


# ── house-robber: no two ADJACENT indices, linear (not circular) ─────────────

def house_robber_max(nums: list[int]) -> int:
    prev, cur = 0, 0
    for x in nums:
        prev, cur = cur, max(cur, prev + x)
    return cur


# ── longest-increasing-subsequence: STRICTLY increasing ──────────────────────

def lis_length(nums: list[int]) -> int:
    if not nums:
        return 0
    import bisect
    tails: list[int] = []
    for x in nums:
        pos = bisect.bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x
    return len(tails)


# ── graph-bfs: unweighted undirected, hop distances from src, -1 if unreachable

def bfs_distances(adj: list[list[int]], src: int, n: int) -> list[int]:
    dist = [-1] * n
    dist[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


# ── word-break: feasibility ───────────────────────────────────────────────────

def word_break_feasible(s: str, word_dict: set[str]) -> bool:
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_dict:
                dp[i] = True
                break
    return dp[n]


# ── edit-distance: classic Levenshtein, insert/delete/replace cost 1 ─────────

def edit_distance(w1: str, w2: str) -> int:
    n, m = len(w1), len(w2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if w1[i - 1] == w2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[n][m]


# ── unique-paths: count paths, right/down moves only ──────────────────────────

def unique_paths_count(m: int, n: int) -> int:
    if m < 1 or n < 1:
        raise OracleError(f"unique_paths undefined for m={m}, n={n}")
    row = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            row[j] += row[j - 1]
    return row[-1]


# ── n-queens: count distinct solutions (no reflection/rotation dedup) ────────

def n_queens_count(n: int) -> int:
    if n < 0:
        raise OracleError(f"n_queens undefined for n={n}")
    if n == 0:
        return 1
    count = 0
    cols: set[int] = set()
    diag1: set[int] = set()
    diag2: set[int] = set()

    def backtrack(row: int) -> None:
        nonlocal count
        if row == n:
            count += 1
            return
        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)
            backtrack(row + 1)
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)

    backtrack(0)
    return count


# ── dijkstra: directed weighted graph, source=0, non-negative weights ────────

def dijkstra_distances(adj: list[list[tuple[int, int]]], n: int) -> list[int]:
    import heapq
    INF = float("inf")
    dist = [INF] * n
    dist[0] = 0
    pq: list[tuple[int, int]] = [(0, 0)]
    visited = [False] * n
    while pq:
        d, u = heapq.heappop(pq)
        if visited[u]:
            continue
        visited[u] = True
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return [d if d != INF else -1 for d in dist]


# ── kmp: all start indices where pattern P occurs in text T, [-1] if none ────

def kmp_occurrences(T: str, P: str) -> list[int]:
    if not P:
        raise OracleError("kmp undefined for empty pattern")
    # build failure function (longest proper prefix==suffix) for P
    lps = [0] * len(P)
    length = 0
    i = 1
    while i < len(P):
        if P[i] == P[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length != 0:
            length = lps[length - 1]
        else:
            lps[i] = 0
            i += 1

    result: list[int] = []
    i = j = 0
    while i < len(T):
        if T[i] == P[j]:
            i += 1
            j += 1
            if j == len(P):
                result.append(i - j)
                j = lps[j - 1]
        elif j != 0:
            j = lps[j - 1]
        else:
            i += 1
    return result


# ── minimum-path-sum: m x n grid, right/down moves, sum incl. both endpoints ─

def min_path_sum(grid: list[list[int]]) -> int:
    m = len(grid)
    n = len(grid[0]) if m else 0
    if m == 0 or n == 0:
        raise OracleError("min_path_sum undefined for empty grid")
    dp = [[0] * n for _ in range(m)]
    dp[0][0] = grid[0][0]
    for j in range(1, n):
        dp[0][j] = dp[0][j - 1] + grid[0][j]
    for i in range(1, m):
        dp[i][0] = dp[i - 1][0] + grid[i][0]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = grid[i][j] + min(dp[i - 1][j], dp[i][j - 1])
    return dp[m - 1][n - 1]
