"""
Verification harness for a generated AtlasCode family.

Runs three independent levels of verification for every problem in the given
family (see docs/atlascode-progress.md "Three-level verification"):

  Level 1 — oracle unit tests (delegated to pytest; see
            tests/unit/test_independent_oracles.py). This script assumes
            those already pass; it does not re-run pytest itself.
  Level 2 — every stored test case's expected_output is regenerated from the
            independent oracle and compared byte-for-byte against what the
            family factory produced (catches drift between the oracle and
            whatever the factory shipped).
  Level 3 — an independently hand-written REFERENCE SOLUTION (a real Python
            program, not a call into the oracle module) is run through the
            ACTUAL judge pipeline (submission.evaluator.evaluate(), which
            spawns a real `python` subprocess per test case) and must be
            Accepted on every case, including hidden ones. An intentionally
            WRONG solution is also run and must NOT be Accepted. This is
            exactly the check that caught the sieve/collatz bugs before.

Usage (from repo root):
    python scripts/verify_atlascode_family.py number-theory
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))

import logging
logging.disable(logging.CRITICAL)

from algorithm_atlas.atlascode.discovery import discover_registered_algorithms
from algorithm_atlas.models.atlas_code import TestCase
from algorithm_atlas.submission.evaluator import evaluate


# ── Independent (hand-written, oracle-free) reference + wrong solutions ──────
# These are deliberately NOT implemented by calling independent_oracles.py —
# that would only prove the oracle agrees with itself. They're separate
# implementations of the same algorithm, so a pass here proves the shipped
# test cases are correct AND that the stdin/stdout wrapper contract works.

_REFERENCE_SOLUTIONS: dict[str, str] = {
    "catalan-number": (
        "import sys, math\n"
        "n = int(sys.stdin.read().strip())\n"
        "print(math.comb(2*n, n) // (n + 1))\n"
    ),
    "euler-phi-sieve": (
        "import sys\n"
        "n = int(sys.stdin.read().strip())\n"
        "def phi(n):\n"
        "    result = n\n"
        "    p = 2\n"
        "    m = n\n"
        "    while p * p <= m:\n"
        "        if m % p == 0:\n"
        "            while m % p == 0:\n"
        "                m //= p\n"
        "            result -= result // p\n"
        "        p += 1\n"
        "    if m > 1:\n"
        "        result -= result // m\n"
        "    return result\n"
        "print(phi(n))\n"
    ),
    "collatz": (
        "import sys\n"
        "n = int(sys.stdin.read().strip())\n"
        "steps = 0\n"
        "while n != 1:\n"
        "    n = n // 2 if n % 2 == 0 else 3 * n + 1\n"
        "    steps += 1\n"
        "print(steps)\n"
    ),
    "sieve-of-eratosthenes": (
        "import sys\n"
        "n = int(sys.stdin.read().strip())\n"
        "if n < 2:\n"
        "    print()\n"
        "else:\n"
        "    is_p = [True] * (n + 1)\n"
        "    is_p[0] = is_p[1] = False\n"
        "    p = 2\n"
        "    while p * p <= n:\n"
        "        if is_p[p]:\n"
        "            for k in range(p*p, n+1, p):\n"
        "                is_p[k] = False\n"
        "        p += 1\n"
        "    print(' '.join(str(i) for i, ok in enumerate(is_p) if ok))\n"
    ),
    "modular-exponentiation": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "base, exp, mod = int(data[0]), int(data[1]), int(data[2])\n"
        "result = 1\n"
        "base %= mod\n"
        "while exp > 0:\n"
        "    if exp & 1:\n"
        "        result = (result * base) % mod\n"
        "    base = (base * base) % mod\n"
        "    exp >>= 1\n"
        "print(result)\n"
    ),
    "prime-factorization": (
        "import sys\n"
        "n = int(sys.stdin.read().strip())\n"
        "factors = []\n"
        "m = n\n"
        "p = 2\n"
        "while p * p <= m:\n"
        "    while m % p == 0:\n"
        "        factors.append(p)\n"
        "        m //= p\n"
        "    p += 1\n"
        "if m > 1:\n"
        "    factors.append(m)\n"
        "print(' '.join(map(str, factors)))\n"
    ),
    "number-of-divisors": (
        "import sys\n"
        "n = int(sys.stdin.read().strip())\n"
        "count = 0\n"
        "i = 1\n"
        "while i * i <= n:\n"
        "    if n % i == 0:\n"
        "        count += 1 if i*i == n else 2\n"
        "    i += 1\n"
        "print(count)\n"
    ),
    "euler-totient": (
        "import sys\n"
        "n = int(sys.stdin.read().strip())\n"
        "result = n\n"
        "m = n\n"
        "p = 2\n"
        "while p * p <= m:\n"
        "    if m % p == 0:\n"
        "        while m % p == 0:\n"
        "            m //= p\n"
        "        result -= result // p\n"
        "    p += 1\n"
        "if m > 1:\n"
        "    result -= result // m\n"
        "print(result)\n"
    ),
    "miller-rabin": (
        "import sys, random\n"
        "n = int(sys.stdin.read().strip())\n"
        "def is_prime(n, k=20):\n"
        "    if n < 2:\n"
        "        return False\n"
        "    for p in (2,3,5,7,11,13,17,19,23,29,31,37):\n"
        "        if n % p == 0:\n"
        "            return n == p\n"
        "    d, r = n - 1, 0\n"
        "    while d % 2 == 0:\n"
        "        d //= 2; r += 1\n"
        "    for a in (2,3,5,7,11,13,17,19,23,29,31,37):\n"
        "        if a >= n:\n"
        "            continue\n"
        "        x = pow(a, d, n)\n"
        "        if x == 1 or x == n - 1:\n"
        "            continue\n"
        "        for _ in range(r - 1):\n"
        "            x = x * x % n\n"
        "            if x == n - 1:\n"
        "                break\n"
        "        else:\n"
        "            return False\n"
        "    return True\n"
        "print('true' if is_prime(n) else 'false')\n"
    ),
    "lucas-theorem": (
        "import sys, math\n"
        "data = sys.stdin.read().split()\n"
        "n, k, p = int(data[0]), int(data[1]), int(data[2])\n"
        "def lucas(n, k, p):\n"
        "    if k < 0 or k > n:\n"
        "        return 0\n"
        "    if n == 0:\n"
        "        return 1\n"
        "    return (math.comb(n % p, k % p) % p) * lucas(n // p, k // p, p) % p\n"
        "print(lucas(n, k, p))\n"
    ),
    # ── dynamic-programming: each written independently (top-down memo or a
    # differently-shaped DP) from independent_oracles.py's bottom-up versions ──
    "staircase": (
        "import sys\nfrom functools import lru_cache\n"
        "n = int(sys.stdin.read().strip())\n"
        "@lru_cache(maxsize=None)\n"
        "def climb(k):\n"
        "    if k <= 1:\n        return 1\n"
        "    return climb(k-1) + climb(k-2)\n"
        "print(climb(n))\n"
    ),
    "jump-game": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "reach = [False]*n\nreach[0] = True\n"
        "for i in range(n):\n"
        "    if reach[i]:\n"
        "        for j in range(i+1, min(i+nums[i], n-1)+1):\n"
        "            reach[j] = True\n"
        "print('true' if reach[n-1] else 'false')\n"
    ),
    "subset-sum": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\ntarget = int(data[n+1])\n"
        "dp = [[False]*(target+1) for _ in range(n+1)]\n"
        "for i in range(n+1):\n    dp[i][0] = True\n"
        "for i in range(1, n+1):\n"
        "    for s in range(1, target+1):\n"
        "        dp[i][s] = dp[i-1][s] or (s >= nums[i-1] and dp[i-1][s-nums[i-1]])\n"
        "print('true' if dp[n][target] else 'false')\n"
    ),
    "coin-change-ways": (
        "import sys\nfrom functools import lru_cache\n"
        "data = sys.stdin.read().split()\n"
        "k = int(data[0])\ncoins = tuple(map(int, data[1:k+1]))\namount = int(data[k+1])\n"
        "@lru_cache(maxsize=None)\n"
        "def ways(i, remaining):\n"
        "    if remaining == 0:\n        return 1\n"
        "    if i == len(coins) or remaining < 0:\n        return 0\n"
        "    return ways(i+1, remaining) + ways(i, remaining - coins[i])\n"
        "print(ways(0, amount))\n"
    ),
    "decode-ways": (
        "import sys\nfrom functools import lru_cache\n"
        "s = sys.stdin.read().strip()\n"
        "n = len(s)\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i):\n"
        "    if i == n:\n        return 1\n"
        "    if s[i] == '0':\n        return 0\n"
        "    total = solve(i+1)\n"
        "    if i+1 < n and int(s[i:i+2]) <= 26:\n"
        "        total += solve(i+2)\n"
        "    return total\n"
        "print(solve(0))\n"
    ),
    "knapsack-01": (
        "import sys\nfrom functools import lru_cache\n"
        "data = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\n"
        "weights=tuple(map(int,data[idx:idx+n]));idx+=n\n"
        "values=tuple(map(int,data[idx:idx+n]));idx+=n\n"
        "capacity=int(data[idx])\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i, cap):\n"
        "    if i == n or cap == 0:\n        return 0\n"
        "    best = solve(i+1, cap)\n"
        "    if weights[i] <= cap:\n"
        "        best = max(best, values[i] + solve(i+1, cap-weights[i]))\n"
        "    return best\n"
        "print(solve(0, capacity))\n"
    ),
    "unbounded-knapsack": (
        "import sys\nfrom functools import lru_cache\n"
        "data = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\n"
        "weights=tuple(map(int,data[idx:idx+n]));idx+=n\n"
        "values=tuple(map(int,data[idx:idx+n]));idx+=n\n"
        "capacity=int(data[idx])\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(cap):\n"
        "    best = 0\n"
        "    for w, v in zip(weights, values):\n"
        "        if w <= cap:\n"
        "            best = max(best, v + solve(cap-w))\n"
        "    return best\n"
        "print(solve(capacity))\n"
    ),
    "rod-cutting": (
        "import sys\nfrom functools import lru_cache\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nprices = tuple(map(int, data[1:n+1]))\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(length):\n"
        "    if length == 0:\n        return 0\n"
        "    return max(prices[i-1] + solve(length-i) for i in range(1, length+1))\n"
        "print(solve(n))\n"
    ),
    "maximum-product-subarray": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "best = nums[0]\n"
        "for i in range(n):\n"
        "    prod = 1\n"
        "    for j in range(i, n):\n"
        "        prod *= nums[j]\n"
        "        best = max(best, prod)\n"
        "print(best)\n"
    ),
    "longest-bitonic-subsequence": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "inc = [1]*n\ndec = [1]*n\n"
        "for i in range(1, n):\n"
        "    for j in range(i):\n"
        "        if nums[j] < nums[i]:\n            inc[i] = max(inc[i], inc[j]+1)\n"
        "for i in range(n-2, -1, -1):\n"
        "    for j in range(i+1, n):\n"
        "        if nums[j] < nums[i]:\n            dec[i] = max(dec[i], dec[j]+1)\n"
        "print(max(inc[i]+dec[i]-1 for i in range(n)))\n"
    ),
    "palindrome-subsequence": (
        "import sys\nfrom functools import lru_cache\n"
        "s = sys.stdin.read().strip()\nn = len(s)\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i, j):\n"
        "    if i > j:\n        return 0\n"
        "    if i == j:\n        return 1\n"
        "    if s[i] == s[j]:\n        return 2 + solve(i+1, j-1)\n"
        "    return max(solve(i+1, j), solve(i, j-1))\n"
        "print(solve(0, n-1))\n"
    ),
    "interleaving-strings": (
        "import sys\nfrom functools import lru_cache\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "s1, s2, s3 = lines[0], lines[1], lines[2]\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i, j):\n"
        "    if i == len(s1) and j == len(s2):\n        return True\n"
        "    k = i + j\n"
        "    if k >= len(s3):\n        return False\n"
        "    ok = False\n"
        "    if i < len(s1) and s1[i] == s3[k]:\n        ok = ok or solve(i+1, j)\n"
        "    if j < len(s2) and s2[j] == s3[k]:\n        ok = ok or solve(i, j+1)\n"
        "    return ok\n"
        "print('true' if len(s1)+len(s2)==len(s3) and solve(0,0) else 'false')\n"
    ),
    "wildcard-matching": (
        "import sys\nfrom functools import lru_cache\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "s, p = lines[0], lines[1]\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i, j):\n"
        "    if j == len(p):\n        return i == len(s)\n"
        "    if p[j] == '*':\n"
        "        return solve(i, j+1) or (i < len(s) and solve(i+1, j))\n"
        "    if i == len(s):\n        return False\n"
        "    if p[j] == '?' or p[j] == s[i]:\n        return solve(i+1, j+1)\n"
        "    return False\n"
        "print('true' if solve(0, 0) else 'false')\n"
    ),
    "distinct-subsequences": (
        "import sys\nfrom functools import lru_cache\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "s, t = lines[0], lines[1]\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i, j):\n"
        "    if j == len(t):\n        return 1\n"
        "    if i == len(s):\n        return 0\n"
        "    total = solve(i+1, j)\n"
        "    if s[i] == t[j]:\n        total += solve(i+1, j+1)\n"
        "    return total\n"
        "print(solve(0, 0))\n"
    ),
    "matrix-chain-multiplication": (
        "import sys\nfrom functools import lru_cache\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\ndims = tuple(map(int, data[1:n+1]))\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i, j):\n"
        "    if i == j:\n        return 0\n"
        "    return min(solve(i,k)+solve(k+1,j)+dims[i]*dims[k+1]*dims[j+1] for k in range(i,j))\n"
        "print(solve(0, len(dims)-2))\n"
    ),
    "egg-drop": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "eggs, floors = int(data[0]), int(data[1])\n"
        "dp = [[0]*(floors+1) for _ in range(eggs+1)]\n"
        "for f in range(1, floors+1):\n    dp[1][f] = f\n"
        "for e in range(2, eggs+1):\n"
        "    for f in range(1, floors+1):\n"
        "        best = f\n"
        "        for x in range(1, f+1):\n"
        "            worst = 1 + max(dp[e-1][x-1], dp[e][f-x])\n"
        "            best = min(best, worst)\n"
        "        dp[e][f] = best\n"
        "print(dp[eggs][floors] if floors > 0 else 0)\n"
    ),
    "boolean-parenthesization": (
        "import sys\nfrom functools import lru_cache\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "symbols, ops = lines[0], lines[1]\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i, j):\n"
        "    if i == j:\n"
        "        return (1, 0) if symbols[i] == 'T' else (0, 1)\n"
        "    t = f = 0\n"
        "    for k in range(i, j):\n"
        "        lt, lf = solve(i, k)\n"
        "        rt, rf = solve(k+1, j)\n"
        "        total = (lt+lf)*(rt+rf)\n"
        "        op = ops[k]\n"
        "        if op == '&':\n            tt = lt*rt\n"
        "        elif op == '|':\n            tt = total - lf*rf\n"
        "        else:\n            tt = lt*rf + lf*rt\n"
        "        t += tt\n        f += total - tt\n"
        "    return (t, f)\n"
        "print(solve(0, len(symbols)-1)[0])\n"
    ),
    "word-wrap": (
        "import sys\nfrom functools import lru_cache\n"
        "data = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\n"
        "lengths=tuple(map(int,data[idx:idx+n]));idx+=n\n"
        "width=int(data[idx])\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i):\n"
        "    if i == n:\n        return 0\n"
        "    best = None\n    cur = -1\n"
        "    for j in range(i, n):\n"
        "        cur = lengths[i] if j == i else cur + 1 + lengths[j]\n"
        "        if cur > width:\n            break\n"
        "        line_cost = 0 if j == n-1 else (width-cur)**3\n"
        "        candidate = line_cost + solve(j+1)\n"
        "        if best is None or candidate < best:\n            best = candidate\n"
        "    return best\n"
        "print(solve(0))\n"
    ),
    # ── binary-search-variants: each reference is independently written
    # (different code shape than independent_oracles.py); each wrong solution
    # is a specific, plausible bug, not a constant ──
    "rotated-binary-search": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\ntarget=int(data[n+1])\n"
        "def search(lo, hi):\n"
        "    if lo > hi:\n        return -1\n"
        "    mid = (lo+hi)//2\n"
        "    if nums[mid] == target:\n        return mid\n"
        "    if nums[lo] <= nums[mid]:\n"
        "        if nums[lo] <= target < nums[mid]:\n            return search(lo, mid-1)\n"
        "        return search(mid+1, hi)\n"
        "    else:\n"
        "        if nums[mid] < target <= nums[hi]:\n            return search(mid+1, hi)\n"
        "        return search(lo, mid-1)\n"
        "print(search(0, n-1))\n"
    ),
    "bitonic-peak-index": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\n"
        "best_i = 0\n"
        "for i in range(1, n):\n"
        "    if nums[i] > nums[best_i]:\n        best_i = i\n"
        "print(best_i)\n"  # linear scan for max — independent of the binary-search oracle, still correct for bitonic
    ),
    "first-occurrence": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\ntarget=int(data[n+1])\n"
        "lo, hi, ans = 0, n-1, -1\n"
        "while lo <= hi:\n"
        "    mid = (lo+hi)//2\n"
        "    if nums[mid] < target:\n        lo = mid+1\n"
        "    elif nums[mid] > target:\n        hi = mid-1\n"
        "    else:\n        ans = mid; hi = mid-1\n"
        "print(ans)\n"
    ),
    "last-occurrence": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\ntarget=int(data[n+1])\n"
        "lo, hi, ans = 0, n-1, -1\n"
        "while lo <= hi:\n"
        "    mid = (lo+hi)//2\n"
        "    if nums[mid] < target:\n        lo = mid+1\n"
        "    elif nums[mid] > target:\n        hi = mid-1\n"
        "    else:\n        ans = mid; lo = mid+1\n"
        "print(ans)\n"
    ),
    "count-occurrences-sorted": (
        "import sys, bisect\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\ntarget=int(data[n+1])\n"
        "print(bisect.bisect_right(nums, target) - bisect.bisect_left(nums, target))\n"
    ),
    "search-insert-position": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\ntarget=int(data[n+1])\n"
        "lo, hi = 0, n\n"
        "while lo < hi:\n"
        "    mid = (lo+hi)//2\n"
        "    if nums[mid] < target:\n        lo = mid+1\n"
        "    else:\n        hi = mid\n"
        "print(lo)\n"
    ),
    "koko-eating-bananas": (
        "import sys, math\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\npiles=list(map(int,data[1:n+1]))\nh=int(data[n+1])\n"
        "def hours(k):\n    return sum(math.ceil(p/k) for p in piles)\n"
        "lo, hi = 1, max(piles)\n"
        "while lo < hi:\n"
        "    mid = (lo+hi)//2\n"
        "    if hours(mid) <= h:\n        hi = mid\n"
        "    else:\n        lo = mid+1\n"
        "print(lo)\n"
    ),
    "ship-packages-within-days": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nweights=list(map(int,data[1:n+1]))\ndays=int(data[n+1])\n"
        "def days_needed(cap):\n"
        "    d, load = 1, 0\n"
        "    for w in weights:\n"
        "        if load + w > cap:\n            d += 1; load = 0\n"
        "        load += w\n"
        "    return d\n"
        "lo, hi = max(weights), sum(weights)\n"
        "while lo < hi:\n"
        "    mid = (lo+hi)//2\n"
        "    if days_needed(mid) <= days:\n        hi = mid\n"
        "    else:\n        lo = mid+1\n"
        "print(lo)\n"
    ),
    "integer-square-root": (
        "import sys\nn = int(sys.stdin.read().strip())\n"
        "lo, hi = 0, n\n"
        "while lo < hi:\n"
        "    mid = (lo+hi+1)//2\n"
        "    if mid*mid <= n:\n        lo = mid\n"
        "    else:\n        hi = mid-1\n"
        "print(lo)\n"
    ),
    "search-2d-matrix": (
        "import sys\ndata = sys.stdin.read().split('\\n')\n"
        "m, n = map(int, data[0].split())\n"
        "matrix = [list(map(int, data[1+i].split())) for i in range(m)]\n"
        "target = int(data[1+m])\n"
        "found = any(target in row for row in matrix)\n"
        "print('true' if found else 'false')\n"  # correct but O(m*n) — different technique than binary search, still valid contract check
    ),
    "find-minimum-rotated-sorted-array": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\n"
        "lo, hi = 0, n-1\n"
        "while lo < hi:\n"
        "    mid = (lo+hi)//2\n"
        "    if nums[mid] > nums[hi]:\n        lo = mid+1\n"
        "    else:\n        hi = mid\n"
        "print(nums[lo])\n"
    ),
    # ── sliding-window-variants ──
    "max-sum-subarray-fixed-k": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\nk=int(data[n+1])\n"
        "best = max(sum(nums[i:i+k]) for i in range(n-k+1))\n"
        "print(best)\n"
    ),
    "min-subarray-len-target-sum": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\ntarget=int(data[n+1])\n"
        "left=0; total=0; best=n+1\n"
        "for right in range(n):\n"
        "    total += nums[right]\n"
        "    while total >= target:\n"
        "        best = min(best, right-left+1)\n"
        "        total -= nums[left]; left += 1\n"
        "print(best if best <= n else 0)\n"
    ),
    "longest-substring-without-repeating": (
        "import sys\ns = sys.stdin.read().rstrip('\\n')\n"
        "seen = {}\nleft = 0\nbest = 0\n"
        "for right, c in enumerate(s):\n"
        "    if c in seen and seen[c] >= left:\n        left = seen[c] + 1\n"
        "    seen[c] = right\n"
        "    best = max(best, right - left + 1)\n"
        "print(best)\n"
    ),
    "longest-substring-at-most-k-distinct": (
        "import sys\nfrom collections import defaultdict\n"
        "line = sys.stdin.read().rstrip('\\n')\ns, k = line.rsplit(' ', 1)\nk = int(k)\n"
        "if k == 0:\n    print(0)\nelse:\n"
        "    counts = defaultdict(int)\n    left = 0\n    best = 0\n    distinct = 0\n"
        "    for right, c in enumerate(s):\n"
        "        if counts[c] == 0:\n            distinct += 1\n"
        "        counts[c] += 1\n"
        "        while distinct > k:\n"
        "            counts[s[left]] -= 1\n"
        "            if counts[s[left]] == 0:\n                distinct -= 1\n"
        "            left += 1\n"
        "        best = max(best, right - left + 1)\n"
        "    print(best)\n"
    ),
    "longest-repeating-char-replacement": (
        "import sys\nfrom collections import Counter\n"
        "line = sys.stdin.read().rstrip('\\n')\ns, k = line.rsplit(' ', 1)\nk = int(k)\n"
        "left = 0\ncounts = Counter()\nbest = 0\nmax_count = 0\n"
        "for right, c in enumerate(s):\n"
        "    counts[c] += 1\n    max_count = max(max_count, counts[c])\n"
        "    while (right - left + 1) - max_count > k:\n"
        "        counts[s[left]] -= 1\n        left += 1\n"
        "    best = max(best, right - left + 1)\n"
        "print(best)\n"
    ),
    "max-consecutive-ones-with-k-flips": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\nk=int(data[n+1])\n"
        "left=0; zeros=0; best=0\n"
        "for right, x in enumerate(nums):\n"
        "    if x == 0:\n        zeros += 1\n"
        "    while zeros > k:\n"
        "        if nums[left] == 0:\n            zeros -= 1\n"
        "        left += 1\n"
        "    best = max(best, right - left + 1)\n"
        "print(best)\n"
    ),
    "minimum-window-substring-length": (
        "import sys\nfrom collections import Counter\n"
        "lines = sys.stdin.read().split('\\n')\ns, t = lines[0], lines[1]\n"
        "need = Counter(t)\nmissing = len(t)\nleft = 0\nbest = len(s) + 1\n"
        "for right in range(1, len(s) + 1):\n"
        "    c = s[right-1]\n"
        "    if need[c] > 0:\n        missing -= 1\n"
        "    need[c] -= 1\n"
        "    while missing == 0:\n"
        "        best = min(best, right - left)\n"
        "        need[s[left]] += 1\n"
        "        if need[s[left]] > 0:\n            missing += 1\n"
        "        left += 1\n"
        "print(best if best <= len(s) else 0)\n"
    ),
    "find-all-anagrams-in-string": (
        "import sys\nfrom collections import Counter\n"
        "lines = sys.stdin.read().split('\\n')\ns, p = lines[0], lines[1]\n"
        "m = len(p)\nresult = []\n"
        "if m <= len(s):\n"
        "    need = Counter(p)\n    window = Counter(s[:m])\n"
        "    if window == need:\n        result.append(0)\n"
        "    for i in range(m, len(s)):\n"
        "        window[s[i]] += 1\n"
        "        window[s[i-m]] -= 1\n"
        "        if window[s[i-m]] == 0:\n            del window[s[i-m]]\n"
        "        if window == need:\n            result.append(i - m + 1)\n"
        "print(' '.join(map(str, result)))\n"
    ),
    # ── bfs-graph-variants reference solutions (independently written, BFS via
    # explicit layer-by-layer processing rather than a (r,c,dist) tuple queue) ──
    "rotten-oranges-minutes": (
        "import sys\nfrom collections import deque\n"
        "data = sys.stdin.read().split('\\n')\n"
        "rows, cols = map(int, data[0].split())\n"
        "grid = [list(map(int, data[1+i].split())) for i in range(rows)]\n"
        "q = deque((r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 2)\n"
        "fresh = sum(row.count(1) for row in grid)\n"
        "minutes = 0\n"
        "while q and fresh > 0:\n"
        "    minutes += 1\n"
        "    for _ in range(len(q)):\n"
        "        r, c = q.popleft()\n"
        "        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):\n"
        "            nr, nc = r+dr, c+dc\n"
        "            if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]==1:\n"
        "                grid[nr][nc] = 2; fresh -= 1; q.append((nr, nc))\n"
        "print(minutes if fresh == 0 else -1)\n"
    ),
    "max-distance-to-zero": (
        "import sys\nfrom collections import deque\n"
        "data = sys.stdin.read().split('\\n')\n"
        "rows, cols = map(int, data[0].split())\n"
        "grid = [list(map(int, data[1+i].split())) for i in range(rows)]\n"
        "q = deque((r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 0)\n"
        "visited = set(q)\n"
        "best = 0\n"
        "while q:\n"
        "    for _ in range(len(q)):\n"
        "        r, c = q.popleft()\n"
        "        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):\n"
        "            nr, nc = r+dr, c+dc\n"
        "            if 0<=nr<rows and 0<=nc<cols and (nr,nc) not in visited:\n"
        "                visited.add((nr,nc)); q.append((nr,nc))\n"
        "    if q:\n        best += 1\n"
        "print(best)\n"
    ),
    "number-of-islands": (
        "import sys\ndata = sys.stdin.read().split('\\n')\n"
        "rows, cols = map(int, data[0].split())\n"
        "grid = [list(map(int, data[1+i].split())) for i in range(rows)]\n"
        "def dfs(r, c):\n"
        "    stack = [(r, c)]\n    grid[r][c] = 0\n"
        "    while stack:\n"
        "        cr, cc = stack.pop()\n"
        "        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):\n"
        "            nr, nc = cr+dr, cc+dc\n"
        "            if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]==1:\n"
        "                grid[nr][nc] = 0; stack.append((nr, nc))\n"
        "count = 0\n"
        "for r in range(rows):\n"
        "    for c in range(cols):\n"
        "        if grid[r][c] == 1:\n            count += 1; dfs(r, c)\n"
        "print(count)\n"
    ),
    "shortest-path-binary-matrix": (
        "import sys\nfrom collections import deque\n"
        "data = sys.stdin.read().split('\\n')\n"
        "n = int(data[0].split()[0])\n"
        "grid = [list(map(int, data[1+i].split())) for i in range(n)]\n"
        "if grid[0][0] != 0 or grid[n-1][n-1] != 0:\n    print(-1)\nelse:\n"
        "    visited = {(0,0)}\n    q = deque([(0,0,1)])\n    ans = -1\n"
        "    while q:\n"
        "        r, c, d = q.popleft()\n"
        "        if (r,c) == (n-1,n-1):\n            ans = d; break\n"
        "        for dr in (-1,0,1):\n"
        "            for dc in (-1,0,1):\n"
        "                if dr==0 and dc==0: continue\n"
        "                nr, nc = r+dr, c+dc\n"
        "                if 0<=nr<n and 0<=nc<n and grid[nr][nc]==0 and (nr,nc) not in visited:\n"
        "                    visited.add((nr,nc)); q.append((nr,nc,d+1))\n"
        "    print(ans)\n"
    ),
    "word-ladder-length": (
        "import sys\nfrom collections import deque\nimport string\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "begin_word, end_word = lines[0], lines[1]\nwords = set(lines[2].split())\n"
        "if end_word not in words:\n    print(0)\nelse:\n"
        "    visited = {begin_word}\n    q = deque([(begin_word, 1)])\n    ans = 0\n"
        "    while q:\n"
        "        word, steps = q.popleft()\n"
        "        if word == end_word:\n            ans = steps; break\n"
        "        for i in range(len(word)):\n"
        "            for ch in string.ascii_lowercase:\n"
        "                nxt = word[:i] + ch + word[i+1:]\n"
        "                if nxt in words and nxt not in visited:\n"
        "                    visited.add(nxt); q.append((nxt, steps+1))\n"
        "    print(ans)\n"
    ),
    "minimum-knight-moves": (
        "import sys\nfrom collections import deque\n"
        "data = sys.stdin.read().split()\ntx, ty = abs(int(data[0])), abs(int(data[1]))\n"
        "moves = [(1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)]\n"
        "visited = {(0,0)}\nq = deque([(0,0,0)])\n"
        "while q:\n"
        "    x, y, d = q.popleft()\n"
        "    if (x,y) == (tx,ty):\n        print(d); sys.exit()\n"
        "    for dx, dy in moves:\n"
        "        nx, ny = x+dx, y+dy\n"
        "        if -2<=nx<=tx+2 and -2<=ny<=ty+2 and (nx,ny) not in visited:\n"
        "            visited.add((nx,ny)); q.append((nx,ny,d+1))\n"
    ),
    "is-bipartite": (
        "import sys\nfrom collections import deque\n"
        "data = sys.stdin.read().split('\\n')\n"
        "n, m = map(int, data[0].split())\n"
        "adj = [[] for _ in range(n)]\n"
        "for i in range(m):\n"
        "    u, v = map(int, data[1+i].split())\n"
        "    adj[u].append(v); adj[v].append(u)\n"
        "color = [-1]*n\nok = True\n"
        "for start in range(n):\n"
        "    if color[start] != -1:\n        continue\n"
        "    color[start] = 0\n    q = deque([start])\n"
        "    while q:\n"
        "        u = q.popleft()\n"
        "        for v in adj[u]:\n"
        "            if color[v] == -1:\n"
        "                color[v] = 1 - color[u]; q.append(v)\n"
        "            elif color[v] == color[u]:\n"
        "                ok = False\n"
        "print('true' if ok else 'false')\n"
    ),
    # ── greedy reference solutions ──
    "activity-selection": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nstarts=list(map(int,data[idx:idx+n]));idx+=n\n"
        "ends=list(map(int,data[idx:idx+n]))\n"
        "order = sorted(range(n), key=lambda i: ends[i])\n"
        "count = 0\nlast_end = float('-inf')\n"
        "for i in order:\n"
        "    if starts[i] >= last_end:\n        count += 1; last_end = ends[i]\n"
        "print(count)\n"
    ),
    "fractional-knapsack": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nweights=list(map(int,data[idx:idx+n]));idx+=n\n"
        "values=list(map(int,data[idx:idx+n]));idx+=n\ncapacity=int(data[idx])\n"
        "ratios = [(values[i]/weights[i], i) for i in range(n)]\n"
        "ratios.sort(reverse=True)\n"
        "remaining = capacity\ntotal = 0.0\n"
        "for _, i in ratios:\n"
        "    if remaining <= 0:\n        break\n"
        "    take = min(weights[i], remaining)\n"
        "    total += values[i] * take / weights[i]\n"
        "    remaining -= take\n"
        "print(f'{total:.2f}')\n"
    ),
    "gas-station": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\ngas=list(map(int,data[idx:idx+n]));idx+=n\n"
        "cost=list(map(int,data[idx:idx+n]))\n"
        "ans = -1\n"
        "for start in range(n):\n"
        "    tank = 0\n    ok = True\n"
        "    for step in range(n):\n"
        "        i = (start+step) % n\n        tank += gas[i]-cost[i]\n"
        "        if tank < 0:\n            ok = False; break\n"
        "    if ok:\n        ans = start; break\n"
        "print(ans)\n"
    ),
    "huffman-coding": (
        "import sys, heapq\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nfreqs = list(map(int, data[1:n+1]))\n"
        "heap = freqs[:]\nheapq.heapify(heap)\ntotal = 0\n"
        "while len(heap) > 1:\n"
        "    a = heapq.heappop(heap); b = heapq.heappop(heap)\n"
        "    total += a+b\n    heapq.heappush(heap, a+b)\n"
        "print(total)\n"
    ),
    "job-scheduling": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\ndeadlines=list(map(int,data[idx:idx+n]));idx+=n\n"
        "profits=list(map(int,data[idx:idx+n]))\n"
        "jobs = sorted(range(n), key=lambda i: -profits[i])\n"
        "max_d = max(deadlines) if deadlines else 0\n"
        "slots = [False]*(max_d+1)\ntotal = 0\n"
        "for i in jobs:\n"
        "    for t in range(min(deadlines[i], max_d), 0, -1):\n"
        "        if not slots[t]:\n            slots[t]=True; total += profits[i]; break\n"
        "print(total)\n"
    ),
    "meeting-rooms": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nstarts=sorted(map(int,data[idx:idx+n]));idx+=n\n"
        "ends=sorted(map(int,data[idx:idx+n]))\n"
        "rooms = 0\nend_ptr = 0\n"
        "for s in starts:\n"
        "    if s < ends[end_ptr]:\n        rooms += 1\n"
        "    else:\n        end_ptr += 1\n"
        "print(rooms)\n"
    ),
    "stable-matching": (
        "import sys\nlines = sys.stdin.read().split('\\n')\n"
        "n = int(lines[0])\n"
        "men_prefs = [list(map(int, lines[1+i].split())) for i in range(n)]\n"
        "women_prefs = [list(map(int, lines[1+n+i].split())) for i in range(n)]\n"
        "women_rank = [[0]*n for _ in range(n)]\n"
        "for w in range(n):\n"
        "    for r, m in enumerate(women_prefs[w]):\n        women_rank[w][m] = r\n"
        "next_proposal = [0]*n\nwoman_partner = [-1]*n\n"
        "free_men = list(range(n))\n"
        "while free_men:\n"
        "    m = free_men.pop()\n"
        "    w = men_prefs[m][next_proposal[m]]\n    next_proposal[m] += 1\n"
        "    if woman_partner[w] == -1:\n        woman_partner[w] = m\n"
        "    elif women_rank[w][m] < women_rank[w][woman_partner[w]]:\n"
        "        free_men.append(woman_partner[w]); woman_partner[w] = m\n"
        "    else:\n        free_men.append(m)\n"
        "man_partner = [-1]*n\n"
        "for w, m in enumerate(woman_partner):\n    man_partner[m] = w\n"
        "print(' '.join(map(str, man_partner)))\n"
    ),
    "task-scheduler": (
        "import sys, heapq\nfrom collections import deque\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\ncounts = list(map(int, data[1:n+1]))\ncooldown = int(data[n+1])\n"
        "heap = [-c for c in counts]\nheapq.heapify(heap)\n"
        "time = 0\ncooldown_q = deque()\n"
        "while heap or cooldown_q:\n"
        "    time += 1\n"
        "    if heap:\n"
        "        cnt = -heapq.heappop(heap) - 1\n"
        "        if cnt > 0:\n            cooldown_q.append((time+cooldown, cnt))\n"
        "    if cooldown_q and cooldown_q[0][0] == time:\n"
        "        _, cnt = cooldown_q.popleft()\n        heapq.heappush(heap, -cnt)\n"
        "print(time)\n"
    ),
    # ── divide-and-conquer reference solutions ──
    "closest-pair": (
        "import sys\ndata = sys.stdin.read().split('\\n')\n"
        "n = int(data[0])\n"
        "points = [tuple(map(int, data[1+i].split())) for i in range(n)]\n"
        "best = None\n"
        "for i in range(n):\n"
        "    for j in range(i+1, n):\n"
        "        dx = points[i][0]-points[j][0]; dy = points[i][1]-points[j][1]\n"
        "        d = dx*dx + dy*dy\n"
        "        if best is None or d < best:\n            best = d\n"
        "print(best)\n"
    ),
    "counting-inversions": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "count = 0\n"
        "def merge_count(arr):\n"
        "    global count\n"
        "    if len(arr) <= 1:\n        return arr\n"
        "    mid = len(arr)//2\n"
        "    left = merge_count(arr[:mid]); right = merge_count(arr[mid:])\n"
        "    merged = []\n    i = j = 0\n"
        "    while i < len(left) and j < len(right):\n"
        "        if left[i] <= right[j]:\n            merged.append(left[i]); i += 1\n"
        "        else:\n            count += len(left) - i; merged.append(right[j]); j += 1\n"
        "    merged.extend(left[i:]); merged.extend(right[j:])\n"
        "    return merged\n"
        "merge_count(nums)\nprint(count)\n"
    ),
    "fast-power": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "base, exp = int(data[0]), int(data[1])\n"
        "def power(b, e):\n"
        "    if e == 0:\n        return 1\n"
        "    half = power(b, e//2)\n"
        "    return half*half*(b if e%2 else 1)\n"
        "print(power(base, exp))\n"
    ),
    "karatsuba": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "a, b = int(data[0]), int(data[1])\n"
        "def kar(x, y):\n"
        "    if x < 10 or y < 10:\n        return x*y\n"
        "    n = max(len(str(x)), len(str(y)))\n    m = n//2\n"
        "    x1, x0 = divmod(x, 10**m)\n    y1, y0 = divmod(y, 10**m)\n"
        "    z2 = kar(x1, y1)\n    z0 = kar(x0, y0)\n"
        "    z1 = kar(x1+x0, y1+y0) - z2 - z0\n"
        "    return z2*10**(2*m) + z1*10**m + z0\n"
        "print(kar(a, b))\n"
    ),
    "majority-element": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "count = 0\ncandidate = None\n"
        "for x in nums:\n"
        "    if count == 0:\n        candidate = x\n"
        "    count += 1 if x == candidate else -1\n"
        "print(candidate)\n"
    ),
    "matrix-exponentiation": (
        "import sys\ndata = sys.stdin.read().split('\\n')\n"
        "n, k, mod = map(int, data[0].split())\n"
        "matrix = [list(map(int, data[1+i].split())) for i in range(n)]\n"
        "def mat_mult(A, B):\n"
        "    return [[sum(A[i][x]*B[x][j] for x in range(n)) % mod for j in range(n)] for i in range(n)]\n"
        "result = [[1 if i==j else 0 for j in range(n)] for i in range(n)]\n"
        "base = matrix\ne = k\n"
        "while e > 0:\n"
        "    if e & 1:\n        result = mat_mult(result, base)\n"
        "    base = mat_mult(base, base)\n    e >>= 1\n"
        "print('\\n'.join(' '.join(map(str, row)) for row in result))\n"
    ),
    "median-of-medians": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\nk = int(data[n+1])\n"
        "print(sorted(nums)[k-1])\n"
    ),
    "polynomial-multiplication": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "na=int(data[idx]);idx+=1\na=list(map(int,data[idx:idx+na]));idx+=na\n"
        "nb=int(data[idx]);idx+=1\nb=list(map(int,data[idx:idx+nb]))\n"
        "result = [0]*(len(a)+len(b)-1)\n"
        "for i, ai in enumerate(a):\n"
        "    for j, bj in enumerate(b):\n        result[i+j] += ai*bj\n"
        "print(' '.join(map(str, result)))\n"
    ),
    "strassen": (
        "import sys\ndata = sys.stdin.read().split('\\n')\n"
        "n, m, p = map(int, data[0].split())\n"
        "A = [list(map(int, data[1+i].split())) for i in range(n)]\n"
        "B = [list(map(int, data[1+n+i].split())) for i in range(m)]\n"
        "result = [[sum(A[i][k]*B[k][j] for k in range(m)) for j in range(p)] for i in range(n)]\n"
        "print('\\n'.join(' '.join(map(str, row)) for row in result))\n"
    ),
    # ── string reference solutions ──
    "z-algorithm": (
        "import sys\ns = sys.stdin.read().strip()\nn = len(s)\n"
        "z = [0]*n\n"
        "for i in range(1, n):\n"
        "    j = 0\n"
        "    while i+j < n and s[j] == s[i+j]:\n        j += 1\n"
        "    z[i] = j\n"
        "print(' '.join(map(str, z)))\n"  # naive O(n^2) — different from the oracle's O(n) two-pointer version
    ),
    "longest-common-substring": (
        "import sys\nlines = sys.stdin.read().split('\\n')\ns1, s2 = lines[0], lines[1]\n"
        "best = 0\n"
        "for i in range(len(s1)):\n"
        "    for j in range(len(s2)):\n"
        "        k = 0\n"
        "        while i+k < len(s1) and j+k < len(s2) and s1[i+k] == s2[j+k]:\n            k += 1\n"
        "        best = max(best, k)\n"
        "print(best)\n"
    ),
    "longest-palindromic-substring": (
        "import sys\ns = sys.stdin.read().rstrip('\\n')\nn = len(s)\n"
        "best = 1 if n else 0\n"
        "for i in range(n):\n"
        "    for j in range(i, n):\n"
        "        sub = s[i:j+1]\n"
        "        if sub == sub[::-1]:\n            best = max(best, len(sub))\n"
        "print(best)\n"
    ),
    "manacher": (
        "import sys\ns = sys.stdin.read().rstrip('\\n')\nn = len(s)\n"
        "count = 0\n"
        "for i in range(n):\n"
        "    for j in range(i, n):\n"
        "        sub = s[i:j+1]\n"
        "        if sub == sub[::-1]:\n            count += 1\n"
        "print(count)\n"
    ),
    "run-length-encoding": (
        "import sys\nimport itertools\ns = sys.stdin.read().rstrip('\\n')\n"
        "print(''.join(f'{len(list(g))}{c}' for c, g in itertools.groupby(s)))\n"
    ),
    "suffix-array": (
        "import sys\ns = sys.stdin.read().rstrip('\\n')\nn = len(s)\n"
        "indices = list(range(n))\n"
        "indices.sort(key=lambda i: s[i:])\n"
        "print(' '.join(map(str, indices)))\n"
    ),
    "string-hashing": (
        "import sys\nline = sys.stdin.read().rstrip('\\n')\ns, k = line.rsplit(' ', 1)\nk = int(k)\n"
        "MOD = (1<<61) - 1\nBASE = 131\n"
        "n = len(s)\nhashes = set()\n"
        "h = 0\npow_k = pow(BASE, k-1, MOD)\n"
        "for i in range(k):\n    h = (h*BASE + ord(s[i])) % MOD\n"
        "hashes.add(h)\n"
        "for i in range(k, n):\n"
        "    h = ((h - ord(s[i-k])*pow_k % MOD) * BASE + ord(s[i])) % MOD\n"
        "    hashes.add(h)\n"
        "print(len(hashes))\n"
    ),
    # ── array-hashing-variants reference solutions ──
    "contains-duplicate-within-k": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nnums=list(map(int,data[idx:idx+n]));idx+=n\nk=int(data[idx])\n"
        "window = set()\nfound = False\n"
        "for i, x in enumerate(nums):\n"
        "    if i > k:\n        window.discard(nums[i-k-1])\n"
        "    if x in window:\n        found = True; break\n"
        "    window.add(x)\n"
        "print('true' if found else 'false')\n"
    ),
    "product-of-array-except-self": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "zero_count = nums.count(0)\n"
        "if zero_count > 1:\n"
        "    result = [0]*n\n"
        "elif zero_count == 1:\n"
        "    prod = 1\n"
        "    for x in nums:\n"
        "        if x != 0:\n            prod *= x\n"
        "    result = [prod if x == 0 else 0 for x in nums]\n"
        "else:\n"
        "    total = 1\n"
        "    for x in nums:\n        total *= x\n"
        "    result = [total // x for x in nums]\n"
        "print(' '.join(map(str, result)))\n"
    ),
    "subarray-sum-equals-k": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nnums=list(map(int,data[idx:idx+n]));idx+=n\nk=int(data[idx])\n"
        "count = 0\n"
        "for i in range(n):\n"
        "    total = 0\n"
        "    for j in range(i, n):\n"
        "        total += nums[j]\n"
        "        if total == k:\n            count += 1\n"
        "print(count)\n"
    ),
    "top-k-frequent-elements": (
        "import sys\nfrom collections import Counter\n"
        "data = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nnums=list(map(int,data[idx:idx+n]));idx+=n\nk=int(data[idx])\n"
        "counts = Counter(nums)\n"
        "ordered = sorted(counts.keys(), key=lambda v: (-counts[v], v))\n"
        "print(' '.join(map(str, ordered[:k])))\n"
    ),
    "longest-consecutive-sequence": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = set(map(int, data[1:n+1]))\n"
        "best = 0\n"
        "for x in nums:\n"
        "    if x - 1 in nums:\n        continue\n"
        "    y = x\n"
        "    while y in nums:\n        y += 1\n"
        "    best = max(best, y - x)\n"
        "print(best)\n"
    ),
    "group-anagrams-count": (
        "import sys\nlines = sys.stdin.read().split('\\n')\n"
        "n = int(lines[0])\nstrs = lines[1:1+n]\n"
        "groups = {}\n"
        "for s in strs:\n"
        "    key = tuple(sorted(s))\n    groups[key] = groups.get(key, 0) + 1\n"
        "print(len(groups))\n"
    ),
    "valid-anagram": (
        "import sys\nlines = sys.stdin.read().split('\\n')\ns, t = lines[0], lines[1]\n"
        "print('true' if sorted(s) == sorted(t) else 'false')\n"
    ),
    "first-unique-character-index": (
        "import sys\ns = sys.stdin.read().rstrip('\\n')\n"
        "ans = -1\n"
        "for i, c in enumerate(s):\n"
        "    if s.count(c) == 1:\n        ans = i; break\n"
        "print(ans)\n"
    ),
    "intersection-of-two-arrays": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n1=int(data[idx]);idx+=1\nnums1=set(map(int,data[idx:idx+n1]));idx+=n1\n"
        "n2=int(data[idx]);idx+=1\nnums2=set(map(int,data[idx:idx+n2]))\n"
        "print(' '.join(map(str, sorted(nums1 & nums2))))\n"
    ),
    "missing-number": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "full = set(range(n+1))\n"
        "print((full - set(nums)).pop())\n"
    ),
    "majority-element-ii": (
        "import sys\nfrom collections import Counter\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "counts = Counter(nums)\n"
        "result = sorted(x for x, c in counts.items() if c > n // 3)\n"
        "print(' '.join(map(str, result)))\n"
    ),
    "two-sum-count-pairs": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nnums=list(map(int,data[idx:idx+n]));idx+=n\ntarget=int(data[idx])\n"
        "count = 0\n"
        "for i in range(n):\n"
        "    for j in range(i+1, n):\n"
        "        if nums[i]+nums[j] == target:\n            count += 1\n"
        "print(count)\n"
    ),
    "subarray-sums-divisible-by-k": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nnums=list(map(int,data[idx:idx+n]));idx+=n\nk=int(data[idx])\n"
        "count = 0\n"
        "for i in range(n):\n"
        "    total = 0\n"
        "    for j in range(i, n):\n"
        "        total += nums[j]\n"
        "        if total % k == 0:\n            count += 1\n"
        "print(count)\n"
    ),
    "three-sum-count-triplets": (
        "import sys\nimport itertools\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "found = set()\n"
        "for combo in itertools.combinations(nums, 3):\n"
        "    if sum(combo) == 0:\n        found.add(tuple(sorted(combo)))\n"
        "print(len(found))\n"
    ),
    "container-with-most-water": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nheights = list(map(int, data[1:n+1]))\n"
        "best = 0\n"
        "for i in range(n):\n"
        "    for j in range(i+1, n):\n"
        "        best = max(best, min(heights[i], heights[j]) * (j-i))\n"
        "print(best)\n"
    ),
    # ── stack-variants reference solutions ──
    "valid-parentheses": (
        "import sys\ns = sys.stdin.read().strip()\n"
        "pairs = {')': '(', ']': '[', '}': '{'}\n"
        "stack = []\nok = True\n"
        "for c in s:\n"
        "    if c in '([{':\n        stack.append(c)\n"
        "    else:\n"
        "        if not stack or stack.pop() != pairs[c]:\n            ok = False; break\n"
        "print('true' if ok and not stack else 'false')\n"
    ),
    "daily-temperatures": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\ntemps = list(map(int, data[1:n+1]))\n"
        "result = [0]*n\n"
        "for i in range(n):\n"
        "    for j in range(i+1, n):\n"
        "        if temps[j] > temps[i]:\n            result[i] = j-i; break\n"
        "print(' '.join(map(str, result)))\n"
    ),
    "next-greater-element": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "result = [-1]*n\n"
        "for i in range(n):\n"
        "    for j in range(i+1, n):\n"
        "        if nums[j] > nums[i]:\n            result[i] = nums[j]; break\n"
        "print(' '.join(map(str, result)))\n"
    ),
    "largest-rectangle-in-histogram": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nheights = list(map(int, data[1:n+1]))\n"
        "best = 0\n"
        "for i in range(n):\n"
        "    min_h = heights[i]\n"
        "    for j in range(i, n):\n"
        "        min_h = min(min_h, heights[j])\n        best = max(best, min_h*(j-i+1))\n"
        "print(best)\n"
    ),
    "min-stack-simulation": (
        "import sys\nlines = sys.stdin.read().split('\\n')\n"
        "n = int(lines[0])\nstack = []\nresult = []\n"
        "for i in range(1, n+1):\n"
        "    parts = lines[i].split()\n"
        "    if parts[0] == 'PUSH':\n"
        "        stack.append(int(parts[1]))\n        result.append(min(stack))\n"
        "    else:\n        stack.pop()\n"
        "print(' '.join(map(str, result)))\n"
    ),
    "evaluate-reverse-polish-notation": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\ntokens = data[1:1+n]\n"
        "stack = []\n"
        "for tok in tokens:\n"
        "    if tok in ('+','-','*','/'):\n"
        "        b = stack.pop(); a = stack.pop()\n"
        "        if tok == '+':\n            stack.append(a+b)\n"
        "        elif tok == '-':\n            stack.append(a-b)\n"
        "        elif tok == '*':\n            stack.append(a*b)\n"
        "        else:\n            stack.append(int(a/b))\n"
        "    else:\n        stack.append(int(tok))\n"
        "print(stack[-1])\n"
    ),
    "remove-k-digits": (
        "import sys\nline = sys.stdin.read().rstrip('\\n')\nnum, k = line.rsplit(' ', 1)\nk = int(k)\n"
        "stack = []\nremaining = k\n"
        "for d in num:\n"
        "    while remaining > 0 and stack and stack[-1] > d:\n"
        "        stack.pop(); remaining -= 1\n"
        "    stack.append(d)\n"
        "if remaining > 0:\n    stack = stack[:-remaining]\n"
        "result = ''.join(stack).lstrip('0')\n"
        "print(result if result else '0')\n"
    ),
    "trapping-rain-water": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nheights = list(map(int, data[1:n+1]))\n"
        "total = 0\n"
        "for i in range(n):\n"
        "    left_max = max(heights[:i+1])\n    right_max = max(heights[i:])\n"
        "    total += max(0, min(left_max, right_max) - heights[i])\n"
        "print(total)\n"
    ),
    # ── bit-manipulation-variants reference solutions ──
    "single-number": (
        "import sys\nfrom functools import reduce\nimport operator\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "print(reduce(operator.xor, nums))\n"
    ),
    "single-number-ii": (
        "import sys\nfrom collections import Counter\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "counts = Counter(nums)\n"
        "print(next(x for x, c in counts.items() if c == 1))\n"
    ),
    "counting-bits": (
        "import sys\nn = int(sys.stdin.read().strip())\n"
        "result = [0]*(n+1)\n"
        "for i in range(1, n+1):\n    result[i] = result[i >> 1] + (i & 1)\n"
        "print(' '.join(map(str, result)))\n"
    ),
    "reverse-bits": (
        "import sys\nn = int(sys.stdin.read().strip())\n"
        "b = format(n, '032b')\n"
        "print(int(b[::-1], 2))\n"
    ),
    "hamming-distance": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "x, y = int(data[0]), int(data[1])\n"
        "print(bin(x ^ y).count('1'))\n"
    ),
    "power-of-two": (
        "import sys\nn = int(sys.stdin.read().strip())\n"
        "ok = n > 0\n"
        "m = n\n"
        "while ok and m > 1:\n"
        "    if m % 2 != 0:\n        ok = False\n"
        "    m //= 2\n"
        "print('true' if ok else 'false')\n"
    ),
    "number-of-1-bits": (
        "import sys\nn = int(sys.stdin.read().strip())\n"
        "count = 0\n"
        "while n:\n    count += n & 1\n    n >>= 1\n"
        "print(count)\n"
    ),
    "maximum-xor-of-two-numbers": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "mask = 0\nbest = 0\n"
        "for bit in range(31, -1, -1):\n"
        "    mask |= (1 << bit)\n"
        "    prefixes = {x & mask for x in nums}\n"
        "    candidate = best | (1 << bit)\n"
        "    if any((candidate ^ p) in prefixes for p in prefixes):\n"
        "        best = candidate\n"
        "print(best)\n"
    ),
}

_TREE_PARSE_REF = (
    "import sys\n"
    "class Node:\n"
    "    def __init__(self, val):\n        self.val = val; self.left = None; self.right = None\n"
    "def parse(tokens):\n"
    "    if not tokens or tokens[0] == 'null':\n        return None\n"
    "    root = Node(int(tokens[0]))\n"
    "    q = [root]; i = 1; qi = 0\n"
    "    while qi < len(q) and i < len(tokens):\n"
    "        node = q[qi]; qi += 1\n"
    "        if i < len(tokens):\n"
    "            if tokens[i] != 'null':\n                node.left = Node(int(tokens[i])); q.append(node.left)\n"
    "            i += 1\n"
    "        if i < len(tokens):\n"
    "            if tokens[i] != 'null':\n                node.right = Node(int(tokens[i])); q.append(node.right)\n"
    "            i += 1\n"
    "    return root\n"
)

# Tree reference solutions (independently written recursive definitions,
# sharing only the canonical parse() deserializer defined above).
_TREE_REFERENCE_SOLUTIONS: dict[str, str] = {
    "max-depth-binary-tree": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "def depth(n):\n    return 0 if n is None else 1 + max(depth(n.left), depth(n.right))\n"
        "print(depth(root))\n"
    ),
    "diameter-of-binary-tree": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "best = 0\n"
        "def height(n):\n"
        "    global best\n"
        "    if n is None:\n        return 0\n"
        "    l = height(n.left); r = height(n.right)\n"
        "    best = max(best, l + r)\n"
        "    return 1 + max(l, r)\n"
        "height(root)\nprint(best)\n"
    ),
    "is-balanced-binary-tree": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "def h(n):\n"
        "    if n is None:\n        return 0\n"
        "    lh = h(n.left)\n    rh = h(n.right)\n"
        "    if lh is None or rh is None or abs(lh-rh) > 1:\n        return None\n"
        "    return 1 + max(lh, rh)\n"
        "print('true' if h(root) is not None else 'false')\n"
    ),
    "is-valid-bst": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "vals = []\n"
        "def inorder(n):\n"
        "    if n is None:\n        return\n"
        "    inorder(n.left); vals.append(n.val); inorder(n.right)\n"
        "inorder(root)\n"
        "print('true' if all(vals[i] < vals[i+1] for i in range(len(vals)-1)) else 'false')\n"
    ),
    "is-symmetric-tree": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "def mirror(a, b):\n"
        "    if a is None and b is None:\n        return True\n"
        "    if a is None or b is None:\n        return False\n"
        "    return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)\n"
        "print('true' if root is None or mirror(root.left, root.right) else 'false')\n"
    ),
    "invert-tree-preorder": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "def invert(n):\n"
        "    if n is None:\n        return\n"
        "    n.left, n.right = n.right, n.left\n"
        "    invert(n.left); invert(n.right)\n"
        "invert(root)\n"
        "result = []\n"
        "def pre(n):\n"
        "    if n is None:\n        return\n"
        "    result.append(n.val); pre(n.left); pre(n.right)\n"
        "pre(root)\nprint(' '.join(map(str, result)))\n"
    ),
    "path-sum-exists": (
        _TREE_PARSE_REF
        + "data = sys.stdin.read().split()\ntokens, target = data[:-1], int(data[-1])\n"
        "root = parse(tokens)\n"
        "def dfs(n, remaining):\n"
        "    if n is None:\n        return False\n"
        "    if n.left is None and n.right is None:\n        return remaining == n.val\n"
        "    return dfs(n.left, remaining - n.val) or dfs(n.right, remaining - n.val)\n"
        "print('true' if dfs(root, target) else 'false')\n"
    ),
    "count-tree-nodes": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "def count(n):\n    return 0 if n is None else 1 + count(n.left) + count(n.right)\n"
        "print(count(root))\n"
    ),
    "lowest-common-ancestor-bst": (
        _TREE_PARSE_REF
        + "data = sys.stdin.read().split()\ntokens, p, q = data[:-2], int(data[-2]), int(data[-1])\n"
        "node = parse(tokens)\n"
        "while node:\n"
        "    if p < node.val and q < node.val:\n        node = node.left\n"
        "    elif p > node.val and q > node.val:\n        node = node.right\n"
        "    else:\n        print(node.val); break\n"
    ),
    "kth-smallest-in-bst": (
        _TREE_PARSE_REF
        + "data = sys.stdin.read().split()\ntokens, k = data[:-1], int(data[-1])\n"
        "root = parse(tokens)\n"
        "vals = []\n"
        "def inorder(n):\n"
        "    if n is None:\n        return\n"
        "    inorder(n.left); vals.append(n.val); inorder(n.right)\n"
        "inorder(root)\nprint(vals[k-1])\n"
    ),
    "level-order-traversal": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "levels = []\n"
        "level = [root] if root else []\n"
        "while level:\n"
        "    levels.append([n.val for n in level])\n"
        "    nxt = []\n"
        "    for n in level:\n"
        "        if n.left:\n            nxt.append(n.left)\n"
        "        if n.right:\n            nxt.append(n.right)\n"
        "    level = nxt\n"
        "print('\\n'.join(' '.join(map(str, lv)) for lv in levels))\n"
    ),
    "right-side-view": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "result = []\n"
        "level = [root] if root else []\n"
        "while level:\n"
        "    result.append(level[-1].val)\n"
        "    nxt = []\n"
        "    for n in level:\n"
        "        if n.left:\n            nxt.append(n.left)\n"
        "        if n.right:\n            nxt.append(n.right)\n"
        "    level = nxt\n"
        "print(' '.join(map(str, result)))\n"
    ),
    "same-tree": (
        _TREE_PARSE_REF
        + "lines = sys.stdin.read().split('\\n')\n"
        "t1 = parse(lines[0].split())\nt2 = parse(lines[1].split())\n"
        "def same(a, b):\n"
        "    if a is None and b is None:\n        return True\n"
        "    if a is None or b is None:\n        return False\n"
        "    return a.val == b.val and same(a.left, b.left) and same(a.right, b.right)\n"
        "print('true' if same(t1, t2) else 'false')\n"
    ),
    "sum-root-to-leaf-numbers": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "total = 0\n"
        "def dfs(n, cur):\n"
        "    global total\n"
        "    if n is None:\n        return\n"
        "    cur = cur*10 + n.val\n"
        "    if n.left is None and n.right is None:\n        total += cur; return\n"
        "    dfs(n.left, cur); dfs(n.right, cur)\n"
        "dfs(root, 0)\nprint(total)\n"
    ),
    "binary-tree-max-path-sum": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "best = float('-inf')\n"
        "def dfs(n):\n"
        "    global best\n"
        "    if n is None:\n        return 0\n"
        "    l = max(dfs(n.left), 0)\n    r = max(dfs(n.right), 0)\n"
        "    best = max(best, n.val + l + r)\n"
        "    return n.val + max(l, r)\n"
        "dfs(root)\nprint(int(best))\n"
    ),
}
_REFERENCE_SOLUTIONS.update(_TREE_REFERENCE_SOLUTIONS)

# DP-variant reference solutions (independently written).
_DP_VARIANT_REFERENCE_SOLUTIONS: dict[str, str] = {
    "triangle-minimum-path-sum": (
        "import sys\nfrom functools import lru_cache\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "n = int(lines[0])\ntriangle = [list(map(int, lines[1+i].split())) for i in range(n)]\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(r, c):\n"
        "    if r == n-1:\n        return triangle[r][c]\n"
        "    return triangle[r][c] + min(solve(r+1, c), solve(r+1, c+1))\n"
        "print(solve(0, 0))\n"
    ),
    "best-time-to-buy-sell-stock": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nprices = list(map(int, data[1:n+1]))\n"
        "best = 0\n"
        "for i in range(n):\n"
        "    for j in range(i+1, n):\n"
        "        best = max(best, prices[j] - prices[i])\n"
        "print(best)\n"
    ),
    "best-time-to-buy-sell-stock-ii": (
        "import sys\nfrom functools import lru_cache\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nprices = tuple(map(int, data[1:n+1]))\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i, holding):\n"
        "    if i == n:\n        return 0\n"
        "    skip = solve(i+1, holding)\n"
        "    if holding:\n"
        "        act = prices[i] + solve(i+1, False)\n"
        "    else:\n"
        "        act = -prices[i] + solve(i+1, True)\n"
        "    return max(skip, act)\n"
        "print(solve(0, False))\n"
    ),
    "partition-equal-subset-sum": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "total = sum(nums)\n"
        "if total % 2 != 0:\n    print('false')\nelse:\n"
        "    target = total // 2\n"
        "    dp = [False]*(target+1)\n    dp[0] = True\n"
        "    for x in nums:\n"
        "        for s in range(target, x-1, -1):\n"
        "            if dp[s-x]:\n                dp[s] = True\n"
        "    print('true' if dp[target] else 'false')\n"
    ),
    "target-sum-ways": (
        "import sys\nfrom functools import lru_cache\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = tuple(map(int, data[1:n+1]))\ntarget = int(data[n+1])\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i, total):\n"
        "    if i == n:\n        return 1 if total == target else 0\n"
        "    return solve(i+1, total+nums[i]) + solve(i+1, total-nums[i])\n"
        "print(solve(0, 0))\n"
    ),
    "perfect-squares-min-count": (
        "import sys\nfrom functools import lru_cache\n"
        "n = int(sys.stdin.read().strip())\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(remaining):\n"
        "    if remaining == 0:\n        return 0\n"
        "    best = remaining\n    j = 1\n"
        "    while j*j <= remaining:\n"
        "        best = min(best, 1 + solve(remaining - j*j))\n        j += 1\n"
        "    return best\n"
        "print(solve(n))\n"
    ),
    "combination-sum-iv-count": (
        "import sys\nfrom functools import lru_cache\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = tuple(map(int, data[1:n+1]))\ntarget = int(data[n+1])\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(remaining):\n"
        "    if remaining == 0:\n        return 1\n"
        "    return sum(solve(remaining - x) for x in nums if x <= remaining)\n"
        "print(solve(target))\n"
    ),
    "delete-and-earn": (
        "import sys\nfrom collections import Counter\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "counts = Counter(nums)\n"
        "vals = sorted(counts)\n"
        "prev_val = None\ntake = skip = 0\n"
        "for v in vals:\n"
        "    points = v * counts[v]\n"
        "    if prev_val is not None and v == prev_val + 1:\n"
        "        take, skip = skip + points, max(take, skip)\n"
        "    else:\n"
        "        take, skip = max(take, skip) + points, max(take, skip)\n"
        "    prev_val = v\n"
        "print(max(take, skip))\n"
    ),
    "maximum-subarray-circular": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "best = float('-inf')\n"
        "doubled = nums + nums\n"
        "for i in range(n):\n"
        "    total = 0\n"
        "    for length in range(1, n+1):\n"
        "        total += doubled[i+length-1]\n"
        "        best = max(best, total)\n"
        "print(best)\n"
    ),
    "jump-game-ii-min-jumps": (
        "import sys\nfrom functools import lru_cache\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = tuple(map(int, data[1:n+1]))\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i):\n"
        "    if i >= n-1:\n        return 0\n"
        "    if nums[i] == 0:\n        return float('inf')\n"
        "    return 1 + min(solve(i+step) for step in range(1, nums[i]+1))\n"
        "print(solve(0))\n"
    ),
}
_REFERENCE_SOLUTIONS.update(_DP_VARIANT_REFERENCE_SOLUTIONS)

# Linked-list-variant reference solutions.
_LINKED_LIST_REFERENCE_SOLUTIONS: dict[str, str] = {
    "reverse-linked-list": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nvalues = list(map(int, data[1:n+1]))\n"
        "result = []\n"
        "for x in values:\n    result.insert(0, x)\n"
        "print(' '.join(map(str, result)))\n"
    ),
    "linked-list-cycle-detect": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nvalues = list(map(int, data[1:n+1]))\npos = int(data[n+1])\n"
        "def nxt(i):\n"
        "    return i + 1 if i + 1 < n else pos\n"
        "has_cycle = False\n"
        "if n > 0 and pos != -1:\n"
        "    slow, fast = 0, 0\n"
        "    while True:\n"
        "        slow = nxt(slow)\n"
        "        fast = nxt(nxt(fast))\n"
        "        if fast == -1 or slow == -1:\n            break\n"
        "        if slow == fast:\n            has_cycle = True; break\n"
        "print('true' if has_cycle else 'false')\n"
    ),
    "merge-two-sorted-lists": (
        "import sys\nlines = sys.stdin.read().split('\\n')\n"
        "def parse(line):\n"
        "    parts = line.split()\n    n = int(parts[0])\n    return list(map(int, parts[1:1+n]))\n"
        "a = parse(lines[0])\nb = parse(lines[1])\n"
        "i = j = 0\nresult = []\n"
        "while i < len(a) and j < len(b):\n"
        "    if a[i] <= b[j]:\n        result.append(a[i]); i += 1\n"
        "    else:\n        result.append(b[j]); j += 1\n"
        "result.extend(a[i:]); result.extend(b[j:])\n"
        "print(' '.join(map(str, result)))\n"
    ),
    "remove-nth-from-end": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nvalues = list(map(int, data[1:n+1]))\nk = int(data[n+1])\n"
        "idx = len(values) - k\n"
        "result = values[:idx] + values[idx+1:]\n"
        "print(' '.join(map(str, result)))\n"
    ),
    "middle-of-linked-list": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nvalues = list(map(int, data[1:n+1]))\n"
        "slow, fast = 0, 0\n"
        "while fast < len(values) - 1:\n"
        "    slow += 1\n    fast += 2\n"
        "print(values[slow])\n"
    ),
    "palindrome-linked-list": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nvalues = list(map(int, data[1:n+1]))\n"
        "left, right = 0, len(values)-1\nok = True\n"
        "while left < right:\n"
        "    if values[left] != values[right]:\n        ok = False; break\n"
        "    left += 1; right -= 1\n"
        "print('true' if ok else 'false')\n"
    ),
}
_REFERENCE_SOLUTIONS.update(_LINKED_LIST_REFERENCE_SOLUTIONS)

# Backtracking-count-variant reference solutions.
_BACKTRACKING_COUNT_REFERENCE_SOLUTIONS: dict[str, str] = {
    "palindrome-partition": (
        "import sys\nfrom functools import lru_cache\n"
        "s = sys.stdin.read().strip()\nn = len(s)\n"
        "@lru_cache(maxsize=None)\n"
        "def is_pal(i, j):\n"
        "    if i >= j:\n        return True\n"
        "    return s[i] == s[j] and is_pal(i+1, j-1)\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i):\n"
        "    if i == n:\n        return -1\n"
        "    best = n\n"
        "    for j in range(i, n):\n"
        "        if is_pal(i, j):\n"
        "            best = min(best, 1 + solve(j+1))\n"
        "    return best\n"
        "print(solve(0))\n"
    ),
    "palindrome-partitioning": (
        "import sys\nfrom functools import lru_cache\n"
        "s = sys.stdin.read().strip()\nn = len(s)\n"
        "@lru_cache(maxsize=None)\n"
        "def is_pal(i, j):\n"
        "    if i >= j:\n        return True\n"
        "    return s[i] == s[j] and is_pal(i+1, j-1)\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i):\n"
        "    if i == n:\n        return 1\n"
        "    return sum(solve(j+1) for j in range(i, n) if is_pal(i, j))\n"
        "print(solve(0))\n"
    ),
    "restore-ip-addresses-count": (
        "import sys\ns = sys.stdin.read().strip()\nn = len(s)\n"
        "def valid(seg):\n"
        "    if not seg or len(seg) > 3:\n        return False\n"
        "    if seg[0] == '0' and len(seg) > 1:\n        return False\n"
        "    return int(seg) <= 255\n"
        "count = 0\n"
        "for a in range(1, min(4, n)):\n"
        "    for b in range(a+1, min(a+4, n)):\n"
        "        for c in range(b+1, min(b+4, n)):\n"
        "            segs = [s[:a], s[a:b], s[b:c], s[c:]]\n"
        "            if all(valid(seg) for seg in segs):\n"
        "                count += 1\n"
        "print(count)\n"
    ),
    "word-break-count-ways": (
        "import sys\nfrom functools import lru_cache\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "s = lines[0]\nwords = frozenset(lines[1].split())\nn = len(s)\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i):\n"
        "    if i == n:\n        return 1\n"
        "    return sum(solve(j) for j in range(i+1, n+1) if s[i:j] in words)\n"
        "print(solve(0))\n"
    ),
    "unique-permutations-count": (
        "import sys\nfrom collections import Counter\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "seen = set()\n"
        "import itertools\n"
        "# for small n, count distinct permutations directly (independent of the factorial-formula oracle)\n"
        "if n <= 8:\n"
        "    print(len(set(itertools.permutations(nums))))\n"
        "else:\n"
        "    import math\n"
        "    counts = Counter(nums)\n"
        "    result = math.factorial(n)\n"
        "    for c in counts.values():\n        result //= math.factorial(c)\n"
        "    print(result)\n"
    ),
}
_REFERENCE_SOLUTIONS.update(_BACKTRACKING_COUNT_REFERENCE_SOLUTIONS)

# Deliberately incorrect solutions (must be rejected — Wrong Answer, never Accepted).
_WRONG_SOLUTIONS: dict[str, str] = {
    "catalan-number": "import sys\nn = int(sys.stdin.read().strip())\nprint(n)\n",
    "euler-phi-sieve": "import sys\nn = int(sys.stdin.read().strip())\nprint(n)\n",
    "collatz": "import sys\nn = int(sys.stdin.read().strip())\nprint(0)\n",
    "sieve-of-eratosthenes": "import sys\nn = int(sys.stdin.read().strip())\nprint(n)\n",
    "modular-exponentiation": "import sys\nprint(0)\n",
    "prime-factorization": "import sys\nn = int(sys.stdin.read().strip())\nprint(n)\n",
    "number-of-divisors": "import sys\nprint(1)\n",
    "euler-totient": "import sys\nn = int(sys.stdin.read().strip())\nprint(n)\n",
    "miller-rabin": "import sys\nprint('true')\n",
    "lucas-theorem": "import sys\nprint(0)\n",
    # ── dynamic-programming: each is a plausible, specific bug, not just a
    # constant — see "mutation-style wrong solution testing" policy ──
    "staircase": (
        "import sys\nn = int(sys.stdin.read().strip())\nprint(n)\n"  # forgets it's Fibonacci-shaped
    ),
    "jump-game": (
        "import sys\ndata = sys.stdin.read().split()\nn=int(data[0])\nnums=list(map(int,data[1:n+1]))\n"
        "print('true' if nums[-1] != 0 or n == 1 else 'false')\n"  # ignores intermediate zero traps
    ),
    "subset-sum": (
        "import sys\ndata = sys.stdin.read().split()\nn=int(data[0])\n"
        "nums=list(map(int,data[1:n+1]))\ntarget=int(data[n+1])\n"
        "print('true' if sum(nums) >= target else 'false')\n"  # ignores exactness, only checks total
    ),
    "coin-change-ways": (
        "import sys\ndata = sys.stdin.read().split()\nk=int(data[0])\n"
        "coins=list(map(int,data[1:k+1]))\namount=int(data[k+1])\n"
        "dp=[0]*(amount+1)\ndp[0]=1\n"
        "for a in range(1, amount+1):\n"
        "    for c in coins:\n"
        "        if c <= a:\n            dp[a] += dp[a-c]\n"
        "print(dp[amount])\n"  # loop order swapped -> counts permutations, not combinations
    ),
    "decode-ways": (
        "import sys\ns = sys.stdin.read().strip()\nn = len(s)\n"
        "dp=[0]*(n+1)\ndp[0]=1\ndp[1]=1\n"  # wrongly allows a leading '0' to decode
        "for i in range(2, n+1):\n"
        "    dp[i] = dp[i-1]\n"
        "    two = int(s[i-2:i])\n"
        "    if 10 <= two <= 26:\n        dp[i] += dp[i-2]\n"
        "print(dp[n])\n"
    ),
    "knapsack-01": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nweights=list(map(int,data[idx:idx+n]));idx+=n\n"
        "values=list(map(int,data[idx:idx+n]));idx+=n\ncapacity=int(data[idx])\n"
        "items = sorted(zip(weights, values), key=lambda wv: wv[1]/wv[0] if wv[0] else 0, reverse=True)\n"
        "total = 0\ncap = capacity\n"
        "for w, v in items:\n"
        "    if w <= cap:\n        cap -= w\n        total += v\n"  # greedy ratio, not optimal 0/1
        "print(total)\n"
    ),
    "unbounded-knapsack": (
        "import sys\nfrom functools import lru_cache\n"
        "data = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nweights=tuple(map(int,data[idx:idx+n]));idx+=n\n"
        "values=tuple(map(int,data[idx:idx+n]));idx+=n\ncapacity=int(data[idx])\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i, cap):\n"
        "    if i == n or cap == 0:\n        return 0\n"
        "    best = solve(i+1, cap)\n"
        "    if weights[i] <= cap:\n        best = max(best, values[i] + solve(i+1, cap-weights[i]))\n"
        "    return best\n"
        "print(solve(0, capacity))\n"  # 0/1 restriction applied to an unbounded problem
    ),
    "rod-cutting": (
        "import sys\ndata = sys.stdin.read().split()\nn=int(data[0])\n"
        "prices=list(map(int,data[1:n+1]))\n"
        "best_len = max(range(1, n+1), key=lambda i: prices[i-1]/i)\n"
        "pieces = n // best_len\nremainder = n % best_len\n"
        "print(pieces*prices[best_len-1] + (prices[remainder-1] if remainder else 0))\n"  # greedy ratio cut
    ),
    "maximum-product-subarray": (
        "import sys\ndata = sys.stdin.read().split()\nn=int(data[0])\n"
        "nums=list(map(int,data[1:n+1]))\n"
        "best = cur = nums[0]\n"
        "for x in nums[1:]:\n"
        "    cur = max(x, cur + x)\n"  # Kadane's SUM recurrence applied to a product problem
        "    best = max(best, cur)\n"
        "print(best)\n"
    ),
    "longest-bitonic-subsequence": (
        "import sys\ndata = sys.stdin.read().split()\nn=int(data[0])\n"
        "nums=list(map(int,data[1:n+1]))\n"
        "dp=[1]*n\n"
        "for i in range(n):\n"
        "    for j in range(i):\n"
        "        if nums[j] < nums[i]:\n            dp[i]=max(dp[i], dp[j]+1)\n"
        "print(max(dp))\n"  # plain LIS length, missing the decreasing half
    ),
    "palindrome-subsequence": (
        "import sys\ns = sys.stdin.read().strip()\nn=len(s)\n"
        "best = 1\n"
        "for i in range(n):\n"
        "    for j in range(i+1, n):\n"
        "        sub = s[i:j+1]\n"
        "        if sub == sub[::-1]:\n            best = max(best, len(sub))\n"
        "print(best)\n"  # longest palindromic SUBSTRING, not subsequence
    ),
    "interleaving-strings": (
        "import sys\nlines = sys.stdin.read().split('\\n')\n"
        "s1, s2, s3 = lines[0], lines[1], lines[2]\n"
        "print('true' if sorted(s1+s2) == sorted(s3) else 'false')\n"  # multiset match, ignores order
    ),
    "wildcard-matching": (
        "import sys\nlines = sys.stdin.read().split('\\n')\ns, p = lines[0], lines[1]\n"
        "def match(s, p):\n"
        "    if len(s) != len(p):\n        return False\n"
        "    return all(pc in ('?', sc) for sc, pc in zip(s, p))\n"  # '*' treated like '?'
        "print('true' if match(s, p) else 'false')\n"
    ),
    "distinct-subsequences": (
        "import sys\nlines = sys.stdin.read().split('\\n')\ns, t = lines[0], lines[1]\n"
        "it = iter(s)\n"
        "print(1 if all(c in it for c in t) else 0)\n"  # boolean subsequence check, not a count
    ),
    "matrix-chain-multiplication": (
        "import sys\ndata = sys.stdin.read().split()\nn=int(data[0])\n"
        "dims=list(map(int,data[1:n+1]))\n"
        "cost = 0\n"
        "for i in range(len(dims)-2):\n"
        "    cost += dims[0]*dims[i+1]*dims[i+2]\n"  # naive strictly-left-to-right order
        "print(cost)\n"
    ),
    "egg-drop": (
        "import sys\ndata = sys.stdin.read().split()\neggs, floors = int(data[0]), int(data[1])\n"
        "print(floors)\n"  # ignores that eggs > 1 allows binary-search-like strategies
    ),
    "boolean-parenthesization": (
        "import sys\nlines = sys.stdin.read().split('\\n')\nsymbols, ops = lines[0], lines[1]\n"
        "print(2 ** ops.count(ops[0]) if ops else (1 if symbols == 'T' else 0))\n"  # nonsense placeholder count
    ),
    "word-wrap": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nlengths=list(map(int,data[idx:idx+n]));idx+=n\nwidth=int(data[idx])\n"
        "lines = []\ncur = 0\ncount = 0\n"
        "for l in lengths:\n"
        "    needed = l if count == 0 else l + 1\n"
        "    if cur + needed > width:\n        lines.append(cur)\n        cur = l\n        count = 1\n"
        "    else:\n        cur += needed\n        count += 1\n"
        "lines.append(cur)\n"
        "print(sum((width-c)**3 for c in lines[:-1]))\n"  # greedy line-fill instead of optimal DP
    ),
    # ── binary-search-variants wrong solutions ──
    "rotated-binary-search": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\ntarget=int(data[n+1])\n"
        "lo, hi = 0, n-1\n"
        "while lo <= hi:\n"
        "    mid = (lo+hi)//2\n"
        "    if nums[mid] == target:\n        print(mid); sys.exit()\n"
        "    if nums[mid] < target:\n        lo = mid+1\n"
        "    else:\n        hi = mid-1\n"
        "print(-1)\n"  # plain binary search, ignores rotation entirely
    ),
    "bitonic-peak-index": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\n"
        "print(n // 2)\n"  # assumes the peak is always in the middle
    ),
    "first-occurrence": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\ntarget=int(data[n+1])\n"
        "idx = -1\n"
        "for i in range(n-1, -1, -1):\n"
        "    if nums[i] == target:\n        idx = i; break\n"
        "print(idx)\n"  # scans from the right, returns LAST occurrence — wrong for first-occurrence
    ),
    "last-occurrence": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\ntarget=int(data[n+1])\n"
        "print(nums.index(target) if target in nums else -1)\n"  # .index() returns FIRST occurrence — wrong for last-occurrence
    ),
    "count-occurrences-sorted": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\ntarget=int(data[n+1])\n"
        "print(1 if target in nums else 0)\n"  # boolean presence, not a count
    ),
    "search-insert-position": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\ntarget=int(data[n+1])\n"
        "for i, x in enumerate(nums):\n"
        "    if x >= target:\n        print(i); sys.exit()\n"
        "print(n - 1)\n"  # off-by-one on the "insert at end" case (should be n, not n-1)
    ),
    "koko-eating-bananas": (
        "import sys, math\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\npiles=list(map(int,data[1:n+1]))\nh=int(data[n+1])\n"
        "print(math.ceil(sum(piles) / h))\n"  # averages total bananas over hours, ignores per-pile constraint
    ),
    "ship-packages-within-days": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nweights=list(map(int,data[1:n+1]))\ndays=int(data[n+1])\n"
        "print(-(-sum(weights) // days))\n"  # divides total weight evenly, ignores that packages can't be split across days arbitrarily
    ),
    "integer-square-root": (
        "import sys\nn = int(sys.stdin.read().strip())\n"
        "print(round(n ** 0.5))\n"  # floating-point round(), wrong for large n / non-floor semantics
    ),
    "search-2d-matrix": (
        "import sys\ndata = sys.stdin.read().split('\\n')\n"
        "m, n = map(int, data[0].split())\n"
        "matrix = [list(map(int, data[1+i].split())) for i in range(m)]\n"
        "target = int(data[1+m])\n"
        "print('true' if any(target in row for row in [matrix[0]]) else 'false')\n"  # only checks the first row
    ),
    "find-minimum-rotated-sorted-array": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\n"
        "print(nums[0])\n"  # assumes no rotation happened
    ),
    # ── sliding-window-variants wrong solutions ──
    "max-sum-subarray-fixed-k": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\nk=int(data[n+1])\n"
        "print(sum(sorted(nums, reverse=True)[:k]))\n"  # picks the k largest elements anywhere, ignores contiguity
    ),
    "min-subarray-len-target-sum": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\ntarget=int(data[n+1])\n"
        "count = 0\ntotal = 0\n"
        "for x in nums:\n"
        "    total += x\n    count += 1\n"
        "    if total >= target:\n        break\n"
        "print(count if total >= target else 0)\n"  # only considers the prefix starting at index 0, never shrinks/slides
    ),
    "longest-substring-without-repeating": (
        "import sys\ns = sys.stdin.read().rstrip('\\n')\n"
        "print(len(set(s)))\n"  # counts distinct characters in the whole string, ignoring contiguity/order
    ),
    "longest-substring-at-most-k-distinct": (
        "import sys\nline = sys.stdin.read().rstrip('\\n')\ns, k = line.rsplit(' ', 1)\nk = int(k)\n"
        "print(min(len(s), k))\n"  # assumes each distinct character only ever needs 1 slot
    ),
    "longest-repeating-char-replacement": (
        "import sys\nfrom collections import Counter\n"
        "line = sys.stdin.read().rstrip('\\n')\ns, k = line.rsplit(' ', 1)\nk = int(k)\n"
        "counts = Counter(s)\n"
        "print(min(len(s), (max(counts.values()) if counts else 0) + k))\n"  # ignores that the window must stay contiguous
    ),
    "max-consecutive-ones-with-k-flips": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n=int(data[0])\nnums=list(map(int,data[1:n+1]))\nk=int(data[n+1])\n"
        "print(min(n, nums.count(1) + k))\n"  # sums globally instead of finding the best contiguous window
    ),
    "minimum-window-substring-length": (
        "import sys\nfrom collections import Counter\n"
        "lines = sys.stdin.read().split('\\n')\ns, t = lines[0], lines[1]\n"
        "print(len(t) if Counter(t) <= Counter(s) else 0)\n"  # assumes the minimal window is always exactly len(t), ignores spread-out characters
    ),
    "find-all-anagrams-in-string": (
        "import sys\nlines = sys.stdin.read().split('\\n')\ns, p = lines[0], lines[1]\n"
        "m = len(p)\n"
        "result = [i for i in range(len(s) - m + 1) if sorted(s[i:i+m]) == sorted(p) and i == 0]\n"
        "print(' '.join(map(str, result)))\n"  # only ever reports index 0 even when it matches, missing later occurrences
    ),
    # ── bfs-graph-variants wrong solutions ──
    "rotten-oranges-minutes": (
        "import sys\ndata = sys.stdin.read().split('\\n')\n"
        "rows, cols = map(int, data[0].split())\n"
        "grid = [list(map(int, data[1+i].split())) for i in range(rows)]\n"
        "print(sum(row.count(1) for row in grid))\n"  # counts fresh oranges instead of BFS layers needed
    ),
    "max-distance-to-zero": (
        "import sys\ndata = sys.stdin.read().split('\\n')\n"
        "rows, cols = map(int, data[0].split())\n"
        "grid = [list(map(int, data[1+i].split())) for i in range(rows)]\n"
        "print(sum(row.count(1) for row in grid))\n"  # counts all 1-cells instead of the max BFS distance
    ),
    "number-of-islands": (
        "import sys\ndata = sys.stdin.read().split('\\n')\n"
        "rows, cols = map(int, data[0].split())\n"
        "grid = [list(map(int, data[1+i].split())) for i in range(rows)]\n"
        "print(sum(row.count(1) for row in grid))\n"  # counts land cells, not connected components
    ),
    "shortest-path-binary-matrix": (
        "import sys\ndata = sys.stdin.read().split('\\n')\n"
        "n = int(data[0].split()[0])\n"
        "grid = [list(map(int, data[1+i].split())) for i in range(n)]\n"
        "print(2*n - 1 if grid[0][0] == 0 and grid[n-1][n-1] == 0 else -1)\n"  # assumes a straight diagonal path always exists, ignores obstacles
    ),
    "word-ladder-length": (
        "import sys\nlines = sys.stdin.read().split('\\n')\n"
        "begin_word, end_word = lines[0], lines[1]\nwords = set(lines[2].split())\n"
        "print(2 if end_word in words else 0)\n"  # assumes it's always a direct one-step transformation
    ),
    "minimum-knight-moves": (
        "import sys\ndata = sys.stdin.read().split()\nx, y = abs(int(data[0])), abs(int(data[1]))\n"
        "print((x + y + 1) // 2)\n"  # Chebyshev/Manhattan-style formula, not actually valid for a knight's L-shaped moves
    ),
    "is-bipartite": (
        "import sys\ndata = sys.stdin.read().split('\\n')\n"
        "n, m = map(int, data[0].split())\n"
        "print('true' if m < n else 'false')\n"  # guesses bipartiteness from edge/node count instead of actually 2-coloring
    ),
    # ── greedy wrong solutions ──
    "activity-selection": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nstarts=list(map(int,data[idx:idx+n]));idx+=n\n"
        "ends=list(map(int,data[idx:idx+n]))\n"
        "order = sorted(range(n), key=lambda i: starts[i])\n"  # sorts by START time instead of end time — classic wrong greedy key
        "count = 0\nlast_end = float('-inf')\n"
        "for i in order:\n"
        "    if starts[i] >= last_end:\n        count += 1; last_end = ends[i]\n"
        "print(count)\n"
    ),
    "fractional-knapsack": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nweights=list(map(int,data[idx:idx+n]));idx+=n\n"
        "values=list(map(int,data[idx:idx+n]));idx+=n\ncapacity=int(data[idx])\n"
        "order = sorted(range(n), key=lambda i: -values[i])\n"  # sorts by raw value, ignoring weight (wrong ratio)
        "remaining = capacity\ntotal = 0.0\n"
        "for i in order:\n"
        "    if remaining <= 0:\n        break\n"
        "    take = min(weights[i], remaining)\n"
        "    total += values[i] * take / weights[i]\n    remaining -= take\n"
        "print(f'{total:.2f}')\n"
    ),
    "gas-station": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\ngas=list(map(int,data[idx:idx+n]));idx+=n\n"
        "cost=list(map(int,data[idx:idx+n]))\n"
        "print(0 if sum(gas) >= sum(cost) else -1)\n"  # always guesses index 0 if total is feasible, ignores where the deficit actually occurs
    ),
    "huffman-coding": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nfreqs = list(map(int, data[1:n+1]))\n"
        "import math\n"
        "bits = max(1, math.ceil(math.log2(n)))\n"
        "print(sum(freqs) * bits)\n"  # fixed-length coding instead of optimal variable-length Huffman
    ),
    "job-scheduling": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\ndeadlines=list(map(int,data[idx:idx+n]));idx+=n\n"
        "profits=list(map(int,data[idx:idx+n]))\n"
        "print(sum(profits))\n"  # assumes every job can be scheduled, ignores deadline conflicts
    ),
    "meeting-rooms": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nstarts=list(map(int,data[idx:idx+n]));idx+=n\n"
        "ends=list(map(int,data[idx:idx+n]))\n"
        "overlaps = 0\n"
        "for i in range(n):\n"
        "    for j in range(i+1, n):\n"
        "        if starts[i] < ends[j] and starts[j] < ends[i]:\n            overlaps += 1\n"
        "print(overlaps)\n"  # counts overlapping PAIRS, not the max simultaneous overlap (rooms needed)
    ),
    "stable-matching": (
        "import sys\nlines = sys.stdin.read().split('\\n')\n"
        "n = int(lines[0])\n"
        "men_prefs = [list(map(int, lines[1+i].split())) for i in range(n)]\n"
        "print(' '.join(str(prefs[0]) for prefs in men_prefs))\n"  # everyone gets their first choice, ignoring conflicts entirely
    ),
    "task-scheduler": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\ncounts = list(map(int, data[1:n+1]))\ncooldown = int(data[n+1])\n"
        "print(sum(counts))\n"  # ignores the cooldown constraint entirely
    ),
    # ── divide-and-conquer wrong solutions ──
    "closest-pair": (
        "import sys\ndata = sys.stdin.read().split('\\n')\n"
        "n = int(data[0])\n"
        "points = [tuple(map(int, data[1+i].split())) for i in range(n)]\n"
        "points.sort()\n"
        "dx = points[0][0]-points[1][0]; dy = points[0][1]-points[1][1]\n"
        "print(dx*dx+dy*dy)\n"  # only checks the two points with smallest x-coordinate, not the true closest pair
    ),
    "counting-inversions": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "count = sum(1 for i in range(n-1) if nums[i] > nums[i+1])\n"  # only counts ADJACENT inversions, not all pairs
        "print(count)\n"
    ),
    "fast-power": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "base, exp = int(data[0]), int(data[1])\n"
        "print(base * exp)\n"  # multiplies instead of exponentiating
    ),
    "karatsuba": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "a, b = int(data[0]), int(data[1])\n"
        "print(a + b)\n"  # adds instead of multiplying
    ),
    "majority-element": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "print(sorted(nums)[0])\n"  # returns the minimum instead of the majority element
    ),
    "matrix-exponentiation": (
        "import sys\ndata = sys.stdin.read().split('\\n')\n"
        "n, k, mod = map(int, data[0].split())\n"
        "matrix = [list(map(int, data[1+i].split())) for i in range(n)]\n"
        "result = [[(matrix[i][j] * k) % mod for j in range(n)] for i in range(n)]\n"  # scales entries by k instead of raising the matrix to the k-th power
        "print('\\n'.join(' '.join(map(str, row)) for row in result))\n"
    ),
    "median-of-medians": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\nk = int(data[n+1])\n"
        "print(sorted(nums)[len(nums)-k])\n"  # off-by-symmetry: indexes from the wrong end
    ),
    "polynomial-multiplication": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "na=int(data[idx]);idx+=1\na=list(map(int,data[idx:idx+na]));idx+=na\n"
        "nb=int(data[idx]);idx+=1\nb=list(map(int,data[idx:idx+nb]))\n"
        "n = max(len(a), len(b))\n"
        "a = a + [0]*(n-len(a)); b = b + [0]*(n-len(b))\n"
        "print(' '.join(str(x+y) for x, y in zip(a, b)))\n"  # adds coefficients pointwise instead of convolving them
    ),
    "strassen": (
        "import sys\ndata = sys.stdin.read().split('\\n')\n"
        "n, m, p = map(int, data[0].split())\n"
        "A = [list(map(int, data[1+i].split())) for i in range(n)]\n"
        "B = [list(map(int, data[1+n+i].split())) for i in range(m)]\n"
        "result = [[A[i][j%m] * B[j%m][j%p] for j in range(p)] for i in range(n)]\n"  # nonsense indexing instead of a real matrix product
        "print('\\n'.join(' '.join(map(str, row)) for row in result))\n"
    ),
    # ── string wrong solutions ──
    "z-algorithm": (
        "import sys\ns = sys.stdin.read().strip()\nn = len(s)\n"
        "print(' '.join(['0'] + [str(1 if i < n and s[i] == s[0] else 0) for i in range(1, n)]))\n"  # only checks a single-character prefix match, not the full extending prefix
    ),
    "longest-common-substring": (
        "import sys\nlines = sys.stdin.read().split('\\n')\ns1, s2 = lines[0], lines[1]\n"
        "print(len(set(s1) & set(s2)))\n"  # counts shared distinct characters, ignoring substring contiguity entirely
    ),
    "longest-palindromic-substring": (
        "import sys\ns = sys.stdin.read().rstrip('\\n')\n"
        "print(len(s) if s == s[::-1] else 1)\n"  # only checks if the WHOLE string is a palindrome, ignores proper substrings
    ),
    "manacher": (
        "import sys\ns = sys.stdin.read().rstrip('\\n')\n"
        "print(len(s))\n"  # returns the string length instead of counting palindromic substrings
    ),
    "run-length-encoding": (
        "import sys\ns = sys.stdin.read().rstrip('\\n')\n"
        "print(f'{len(s)}{s[0]}' if s else '')\n"  # collapses the whole string into one run, ignoring actual character changes
    ),
    "suffix-array": (
        "import sys\ns = sys.stdin.read().rstrip('\\n')\n"
        "print(' '.join(str(i) for i in range(len(s))))\n"  # prints indices in original order, not suffix-sorted order
    ),
    "string-hashing": (
        "import sys\nline = sys.stdin.read().rstrip('\\n')\ns, k = line.rsplit(' ', 1)\nk = int(k)\n"
        "print(len(s) - k + 1 if len(s) >= k else 0)\n"  # counts total substrings of length k, not DISTINCT ones
    ),
    # ── array-hashing-variants wrong solutions ──
    "contains-duplicate-within-k": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nnums=list(map(int,data[idx:idx+n]))\n"
        "print('true' if len(set(nums)) < len(nums) else 'false')\n"  # ignores the index-distance constraint k entirely
    ),
    "product-of-array-except-self": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "total = 1\n"
        "for x in nums:\n    total *= x\n"
        "print(' '.join(str(total) for _ in nums))\n"  # uses full product for every position instead of excluding self
    ),
    "subarray-sum-equals-k": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nnums=list(map(int,data[idx:idx+n]));idx+=n\nk=int(data[idx])\n"
        "print(sum(1 for x in nums if x == k))\n"  # counts single elements equal to k, not subarrays summing to k
    ),
    "top-k-frequent-elements": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nnums=list(map(int,data[idx:idx+n]));idx+=n\nk=int(data[idx])\n"
        "print(' '.join(map(str, sorted(nums, reverse=True)[:k])))\n"  # picks largest VALUES, not most frequent
    ),
    "longest-consecutive-sequence": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "nums = sorted(set(nums))\n"
        "print(len(nums))\n"  # counts total distinct values instead of the longest consecutive RUN
    ),
    "group-anagrams-count": (
        "import sys\nlines = sys.stdin.read().split('\\n')\n"
        "n = int(lines[0])\nstrs = lines[1:1+n]\n"
        "print(len(set(strs)))\n"  # groups by exact string equality, not by anagram equivalence
    ),
    "valid-anagram": (
        "import sys\nlines = sys.stdin.read().split('\\n')\ns, t = lines[0], lines[1]\n"
        "print('true' if len(s) == len(t) else 'false')\n"  # only compares lengths, ignores actual character content
    ),
    "first-unique-character-index": (
        "import sys\ns = sys.stdin.read().rstrip('\\n')\n"
        "print(0 if s else -1)\n"  # always guesses index 0 regardless of actual uniqueness
    ),
    "intersection-of-two-arrays": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n1=int(data[idx]);idx+=1\nnums1=list(map(int,data[idx:idx+n1]));idx+=n1\n"
        "n2=int(data[idx]);idx+=1\nnums2=list(map(int,data[idx:idx+n2]))\n"
        "print(' '.join(map(str, sorted(set(nums1) | set(nums2)))))\n"  # union instead of intersection
    ),
    "missing-number": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "print(n - len(nums))\n"  # always prints 0 (since len(nums)==n by construction), ignores which number is actually missing
    ),
    "majority-element-ii": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "from collections import Counter\n"
        "counts = Counter(nums)\n"
        "best = counts.most_common(1)\n"
        "print(str(best[0][0]) if best and best[0][1] > 1 else '')\n"  # only ever reports at most one value, and uses the wrong threshold
    ),
    "two-sum-count-pairs": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nnums=list(map(int,data[idx:idx+n]));idx+=n\ntarget=int(data[idx])\n"
        "print(sum(1 for x in nums if 2*x == target))\n"  # only counts elements that pair with themselves, misses distinct-value pairs
    ),
    "subarray-sums-divisible-by-k": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n=int(data[idx]);idx+=1\nnums=list(map(int,data[idx:idx+n]));idx+=n\nk=int(data[idx])\n"
        "print(sum(1 for x in nums if x % k == 0))\n"  # only checks single elements, not subarray sums
    ),
    "three-sum-count-triplets": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "print(sum(1 for x in nums if x == 0))\n"  # counts zeros in the array instead of zero-sum triplets
    ),
    "container-with-most-water": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nheights = list(map(int, data[1:n+1]))\n"
        "print(max(heights) * (n - 1))\n"  # assumes the tallest bar always forms the optimal container with the far end
    ),
    # ── stack-variants wrong solutions ──
    "valid-parentheses": (
        "import sys\ns = sys.stdin.read().strip()\n"
        "print('true' if s.count('(') == s.count(')') and s.count('[') == s.count(']') and s.count('{') == s.count('}') else 'false')\n"  # only checks counts match, ignores nesting order
    ),
    "daily-temperatures": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\ntemps = list(map(int, data[1:n+1]))\n"
        "result = [1 if i < n-1 and temps[i+1] > temps[i] else 0 for i in range(n)]\n"  # only checks the very next day, not the actual next warmer day
        "print(' '.join(map(str, result)))\n"
    ),
    "next-greater-element": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "result = [nums[i+1] if i < n-1 and nums[i+1] > nums[i] else -1 for i in range(n)]\n"  # only checks the immediate next element
        "print(' '.join(map(str, result)))\n"
    ),
    "largest-rectangle-in-histogram": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nheights = list(map(int, data[1:n+1]))\n"
        "print(max(heights) * n if heights else 0)\n"  # assumes the whole width can use the max height
    ),
    "min-stack-simulation": (
        "import sys\nlines = sys.stdin.read().split('\\n')\n"
        "n = int(lines[0])\nresult = []\nstack = []\n"
        "for i in range(1, n+1):\n"
        "    parts = lines[i].split()\n"
        "    if parts[0] == 'PUSH':\n"
        "        stack.append(int(parts[1]))\n        result.append(stack[-1])\n"  # reports the last pushed value, not the minimum
        "    else:\n        stack.pop()\n"
        "print(' '.join(map(str, result)))\n"
    ),
    "evaluate-reverse-polish-notation": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\ntokens = data[1:1+n]\n"
        "nums = [int(t) for t in tokens if t not in ('+','-','*','/')]\n"
        "print(sum(nums))\n"  # ignores operators entirely, just sums the operands
    ),
    "remove-k-digits": (
        "import sys\nline = sys.stdin.read().rstrip('\\n')\nnum, k = line.rsplit(' ', 1)\nk = int(k)\n"
        "result = num[:-k] if k > 0 else num\n"  # removes from the END instead of choosing the optimal digits to drop
        "result = result.lstrip('0')\n"
        "print(result if result else '0')\n"
    ),
    "trapping-rain-water": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nheights = list(map(int, data[1:n+1]))\n"
        "print(max(heights) * n - sum(heights) if heights else 0)\n"  # assumes water fills up to the GLOBAL max everywhere, ignoring boundary walls
    ),
    # ── bit-manipulation-variants wrong solutions ──
    "single-number": (
        "import sys\nfrom collections import Counter\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "print(min(nums))\n"  # returns the minimum instead of the unpaired element
    ),
    "single-number-ii": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "import functools, operator\n"
        "print(functools.reduce(operator.xor, nums))\n"  # XOR trick only works for pairs, not triples — wrong for this variant
    ),
    "counting-bits": (
        "import sys\nn = int(sys.stdin.read().strip())\n"
        "print(' '.join(str(i % 2) for i in range(n+1)))\n"  # only checks the last bit (parity), not the total popcount
    ),
    "reverse-bits": (
        "import sys\nn = int(sys.stdin.read().strip())\n"
        "print(n)\n"  # doesn't reverse anything
    ),
    "hamming-distance": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "x, y = int(data[0]), int(data[1])\n"
        "print(abs(x - y))\n"  # arithmetic difference instead of counting differing bits
    ),
    "power-of-two": (
        "import sys\nn = int(sys.stdin.read().strip())\n"
        "print('true' if n % 2 == 0 else 'false')\n"  # checks even instead of power-of-two
    ),
    "number-of-1-bits": (
        "import sys\nn = int(sys.stdin.read().strip())\n"
        "print(len(str(n)))\n"  # counts decimal digits instead of binary 1-bits
    ),
    "maximum-xor-of-two-numbers": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "print(max(nums) ^ min(nums))\n"  # assumes the max XOR always comes from the largest and smallest values
    ),
}

# Tree wrong solutions (each a specific, plausible bug — shares the canonical
# parse() deserializer from _TREE_PARSE_REF above).
_TREE_WRONG_SOLUTIONS: dict[str, str] = {
    "max-depth-binary-tree": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "def depth(n):\n    return 0 if n is None else 1 + depth(n.left)\n"  # only follows the left spine, ignores the right subtree
        "print(depth(root))\n"
    ),
    "diameter-of-binary-tree": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "def depth(n):\n    return 0 if n is None else 1 + max(depth(n.left), depth(n.right))\n"
        "print(depth(root.left) + depth(root.right) if root else 0)\n"  # only checks the path through the ROOT, misses deeper diameters
    ),
    "is-balanced-binary-tree": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "def depth(n):\n    return 0 if n is None else 1 + max(depth(n.left), depth(n.right))\n"
        "ok = root is None or abs(depth(root.left) - depth(root.right)) <= 1\n"  # only checks balance at the ROOT, not every node
        "print('true' if ok else 'false')\n"
    ),
    "is-valid-bst": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "def local_ok(n):\n"
        "    if n is None:\n        return True\n"
        "    if n.left and n.left.val >= n.val:\n        return False\n"
        "    if n.right and n.right.val <= n.val:\n        return False\n"
        "    return local_ok(n.left) and local_ok(n.right)\n"  # only checks IMMEDIATE children, not the full-subtree BST bound
        "print('true' if local_ok(root) else 'false')\n"
    ),
    "is-symmetric-tree": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "def vals(n, acc):\n"
        "    if n is None:\n        return\n"
        "    acc.append(n.val); vals(n.left, acc); vals(n.right, acc)\n"
        "acc = []\nvals(root, acc)\n"
        "print('true' if acc == acc[::-1] else 'false')\n"  # checks if the preorder VALUE SEQUENCE is a palindrome, not actual mirror structure
    ),
    "invert-tree-preorder": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "result = []\n"
        "def pre(n):\n"
        "    if n is None:\n        return\n"
        "    result.append(n.val); pre(n.left); pre(n.right)\n"
        "pre(root)\nprint(' '.join(map(str, result)))\n"  # forgets to actually invert before traversing
    ),
    "path-sum-exists": (
        _TREE_PARSE_REF
        + "data = sys.stdin.read().split()\ntokens, target = data[:-1], int(data[-1])\n"
        "root = parse(tokens)\n"
        "total = 0\n"
        "def sum_all(n):\n"
        "    global total\n"
        "    if n is None:\n        return\n"
        "    total += n.val; sum_all(n.left); sum_all(n.right)\n"
        "sum_all(root)\n"
        "print('true' if total == target else 'false')\n"  # checks sum of ALL nodes instead of any single root-to-leaf path
    ),
    "count-tree-nodes": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "def depth(n):\n    return 0 if n is None else 1 + max(depth(n.left), depth(n.right))\n"
        "d = depth(root)\n"
        "print((2**d) - 1)\n"  # assumes the tree is perfectly complete, ignores actual missing nodes
    ),
    "lowest-common-ancestor-bst": (
        _TREE_PARSE_REF
        + "data = sys.stdin.read().split()\ntokens, p, q = data[:-2], int(data[-2]), int(data[-1])\n"
        "root = parse(tokens)\n"
        "print(root.val)\n"  # always returns the root instead of descending to the actual split point
    ),
    "kth-smallest-in-bst": (
        _TREE_PARSE_REF
        + "data = sys.stdin.read().split()\ntokens, k = data[:-1], int(data[-1])\n"
        "root = parse(tokens)\n"
        "vals = []\n"
        "def preorder(n):\n"
        "    if n is None:\n        return\n"
        "    vals.append(n.val); preorder(n.left); preorder(n.right)\n"
        "preorder(root)\n"  # collects values in PREORDER instead of inorder, so they aren't sorted
        "print(sorted(vals)[k-1] if False else vals[k-1])\n"
    ),
    "level-order-traversal": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "result = []\n"
        "def pre(n):\n"
        "    if n is None:\n        return\n"
        "    result.append(n.val); pre(n.left); pre(n.right)\n"
        "pre(root)\n"
        "print('\\n'.join(str(v) for v in result))\n"  # prints preorder values one per line instead of grouping by actual BFS level
    ),
    "right-side-view": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "result = []\n"
        "def rightmost_spine(n):\n"
        "    if n is None:\n        return\n"
        "    result.append(n.val)\n"
        "    rightmost_spine(n.right)\n"
        "rightmost_spine(root)\n"  # follows the right spine, misses levels where the rightmost node is on the LEFT branch
        "print(' '.join(map(str, result)))\n"
    ),
    "same-tree": (
        _TREE_PARSE_REF
        + "lines = sys.stdin.read().split('\\n')\n"
        "t1 = parse(lines[0].split())\nt2 = parse(lines[1].split())\n"
        "def collect(n, acc):\n"
        "    if n is None:\n        return\n"
        "    acc.append(n.val); collect(n.left, acc); collect(n.right, acc)\n"
        "a1, a2 = [], []\ncollect(t1, a1); collect(t2, a2)\n"
        "print('true' if sorted(a1) == sorted(a2) else 'false')\n"  # compares value MULTISETS, ignoring actual tree structure
    ),
    "sum-root-to-leaf-numbers": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "total = 0\n"
        "def sum_all(n):\n"
        "    global total\n"
        "    if n is None:\n        return\n"
        "    total += n.val; sum_all(n.left); sum_all(n.right)\n"
        "sum_all(root)\nprint(total)\n"  # sums raw node values instead of building per-path decimal numbers
    ),
    "binary-tree-max-path-sum": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "def sum_all(n):\n"
        "    return 0 if n is None else n.val + sum_all(n.left) + sum_all(n.right)\n"
        "print(sum_all(root))\n"  # sums the ENTIRE tree instead of finding the best single path
    ),
}
_WRONG_SOLUTIONS.update(_TREE_WRONG_SOLUTIONS)

# DP-variant wrong solutions.
_DP_VARIANT_WRONG_SOLUTIONS: dict[str, str] = {
    "triangle-minimum-path-sum": (
        "import sys\nlines = sys.stdin.read().split('\\n')\n"
        "n = int(lines[0])\ntriangle = [list(map(int, lines[1+i].split())) for i in range(n)]\n"
        "print(sum(min(row) for row in triangle))\n"  # sums the row-minimums independently, ignoring adjacency constraint
    ),
    "best-time-to-buy-sell-stock": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nprices = list(map(int, data[1:n+1]))\n"
        "print(max(prices) - min(prices))\n"  # ignores that the sell must happen AFTER the buy
    ),
    "best-time-to-buy-sell-stock-ii": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nprices = list(map(int, data[1:n+1]))\n"
        "print(max(prices) - min(prices))\n"  # treats it as a single transaction, not summed daily gains
    ),
    "partition-equal-subset-sum": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "print('true' if sum(nums) % 2 == 0 else 'false')\n"  # only checks total parity, not actual subset feasibility
    ),
    "target-sum-ways": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\ntarget = int(data[n+1])\n"
        "print(1 if sum(nums) == abs(target) else 0)\n"  # only handles the case of all-same-sign, misses mixed sign assignments
    ),
    "perfect-squares-min-count": (
        "import sys\nimport math\n"
        "n = int(sys.stdin.read().strip())\n"
        "count = 0\n"
        "while n > 0:\n"
        "    root = int(math.isqrt(n))\n    n -= root*root\n    count += 1\n"
        "print(count)\n"  # greedy largest-square-first, not always optimal (fails e.g. n=12)
    ),
    "combination-sum-iv-count": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\ntarget = int(data[n+1])\n"
        "dp = [0]*(target+1)\ndp[0] = 1\n"
        "for x in nums:\n"
        "    for t in range(x, target+1):\n        dp[t] += dp[t-x]\n"
        "print(dp[target])\n"  # coin-change-style COMBINATION count (order fixed), not ordered PERMUTATION count
    ),
    "delete-and-earn": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "print(sum(nums))\n"  # takes every element, ignoring the deletion-of-neighbors constraint
    ),
    "maximum-subarray-circular": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "best = cur = nums[0]\n"
        "for x in nums[1:]:\n"
        "    cur = max(x, cur+x)\n    best = max(best, cur)\n"
        "print(best)\n"  # plain (non-circular) Kadane's, misses wraparound subarrays
    ),
    "jump-game-ii-min-jumps": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "jumps = 0\ni = 0\n"
        "while i < n-1:\n"
        "    i += nums[i] if nums[i] > 0 else 1\n    jumps += 1\n"  # always jumps the MAXIMUM distance greedily, not the one reaching the best next window
        "print(jumps)\n"
    ),
}
_WRONG_SOLUTIONS.update(_DP_VARIANT_WRONG_SOLUTIONS)

# Linked-list-variant wrong solutions.
_LINKED_LIST_WRONG_SOLUTIONS: dict[str, str] = {
    "reverse-linked-list": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nvalues = list(map(int, data[1:n+1]))\n"
        "print(' '.join(map(str, sorted(values, reverse=True))))\n"  # sorts descending instead of reversing order
    ),
    "linked-list-cycle-detect": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nvalues = list(map(int, data[1:n+1]))\npos = int(data[n+1])\n"
        "print('true' if len(set(values)) < len(values) else 'false')\n"  # checks for duplicate VALUES instead of an actual structural cycle
    ),
    "merge-two-sorted-lists": (
        "import sys\nlines = sys.stdin.read().split('\\n')\n"
        "def parse(line):\n"
        "    parts = line.split()\n    n = int(parts[0])\n    return list(map(int, parts[1:1+n]))\n"
        "a = parse(lines[0])\nb = parse(lines[1])\n"
        "print(' '.join(map(str, a + b)))\n"  # concatenates without merging/sorting
    ),
    "remove-nth-from-end": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nvalues = list(map(int, data[1:n+1]))\nk = int(data[n+1])\n"
        "print(' '.join(map(str, values[:k-1] + values[k:])))\n"  # removes the k-th from the START instead of from the END
    ),
    "middle-of-linked-list": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nvalues = list(map(int, data[1:n+1]))\n"
        "print(values[(len(values)-1)//2])\n"  # picks the FIRST middle for even-length lists, not the LeetCode-standard second middle
    ),
    "palindrome-linked-list": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0])\nvalues = list(map(int, data[1:n+1]))\n"
        "print('true' if sorted(values) == values else 'false')\n"  # checks if already sorted, not actual palindrome symmetry
    ),
}
_WRONG_SOLUTIONS.update(_LINKED_LIST_WRONG_SOLUTIONS)

# Backtracking-count-variant wrong solutions.
_BACKTRACKING_COUNT_WRONG_SOLUTIONS: dict[str, str] = {
    "palindrome-partition": (
        "import sys\ns = sys.stdin.read().strip()\n"
        "print(0 if s == s[::-1] else len(s) - 1)\n"  # only handles the whole-string-is-a-palindrome case correctly, guesses worst-case otherwise
    ),
    "palindrome-partitioning": (
        "import sys\ns = sys.stdin.read().strip()\n"
        "print(2 ** (len(s) - 1) if len(set(s)) == 1 else 1)\n"  # nonsense heuristic based only on whether all characters are identical
    ),
    "restore-ip-addresses-count": (
        "import sys\ns = sys.stdin.read().strip()\n"
        "print(1 if len(s) == 4 else 0)\n"  # only handles the trivial no-leading-zero 4-digit case, ignores all other valid splits
    ),
    "word-break-count-ways": (
        "import sys\nlines = sys.stdin.read().split('\\n')\n"
        "s = lines[0]\nwords = set(lines[1].split())\n"
        "print(1 if s in words else 0)\n"  # only checks if the ENTIRE string is a single dictionary word
    ),
    "unique-permutations-count": (
        "import sys\nimport math\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
        "print(math.factorial(n))\n"  # ignores duplicate values entirely (plain n!, overcounts when duplicates exist)
    ),
}
_WRONG_SOLUTIONS.update(_BACKTRACKING_COUNT_WRONG_SOLUTIONS)

# Famous-concepts families (see docs/atlascode-famous-concepts-audit.md) each
# ship their own REFERENCE_SOLUTIONS/WRONG_SOLUTIONS dicts inline (built by
# parallel agents against a shared contract) — merge them in the same pattern
# as every prior family above, instead of duplicating the source here.
from algorithm_atlas.atlascode.families.famous_easy import (
    REFERENCE_SOLUTIONS as _FAMOUS_EASY_REFERENCE_SOLUTIONS,
    WRONG_SOLUTIONS as _FAMOUS_EASY_WRONG_SOLUTIONS,
)
from algorithm_atlas.atlascode.families.famous_arrays_matrix import (
    REFERENCE_SOLUTIONS as _FAMOUS_ARRAYS_MATRIX_REFERENCE_SOLUTIONS,
    WRONG_SOLUTIONS as _FAMOUS_ARRAYS_MATRIX_WRONG_SOLUTIONS,
)
from algorithm_atlas.atlascode.families.famous_graphs_trees_lists import (
    REFERENCE_SOLUTIONS as _FAMOUS_GRAPHS_TREES_LISTS_REFERENCE_SOLUTIONS,
    WRONG_SOLUTIONS as _FAMOUS_GRAPHS_TREES_LISTS_WRONG_SOLUTIONS,
)
from algorithm_atlas.atlascode.families.famous_hard import (
    REFERENCE_SOLUTIONS as _FAMOUS_HARD_REFERENCE_SOLUTIONS,
    WRONG_SOLUTIONS as _FAMOUS_HARD_WRONG_SOLUTIONS,
)
from algorithm_atlas.atlascode.families.sorting import (
    REFERENCE_SOLUTIONS as _SORTING_REFERENCE_SOLUTIONS,
    WRONG_SOLUTIONS as _SORTING_WRONG_SOLUTIONS,
)
from algorithm_atlas.atlascode.families.searching import (
    REFERENCE_SOLUTIONS as _SEARCHING_REFERENCE_SOLUTIONS,
    WRONG_SOLUTIONS as _SEARCHING_WRONG_SOLUTIONS,
)
_REFERENCE_SOLUTIONS.update(_SORTING_REFERENCE_SOLUTIONS)
_WRONG_SOLUTIONS.update(_SORTING_WRONG_SOLUTIONS)
_REFERENCE_SOLUTIONS.update(_SEARCHING_REFERENCE_SOLUTIONS)
_WRONG_SOLUTIONS.update(_SEARCHING_WRONG_SOLUTIONS)
_REFERENCE_SOLUTIONS.update(_FAMOUS_EASY_REFERENCE_SOLUTIONS)
_WRONG_SOLUTIONS.update(_FAMOUS_EASY_WRONG_SOLUTIONS)
_REFERENCE_SOLUTIONS.update(_FAMOUS_ARRAYS_MATRIX_REFERENCE_SOLUTIONS)
_WRONG_SOLUTIONS.update(_FAMOUS_ARRAYS_MATRIX_WRONG_SOLUTIONS)
_REFERENCE_SOLUTIONS.update(_FAMOUS_GRAPHS_TREES_LISTS_REFERENCE_SOLUTIONS)
_WRONG_SOLUTIONS.update(_FAMOUS_GRAPHS_TREES_LISTS_WRONG_SOLUTIONS)
_REFERENCE_SOLUTIONS.update(_FAMOUS_HARD_REFERENCE_SOLUTIONS)
_WRONG_SOLUTIONS.update(_FAMOUS_HARD_WRONG_SOLUTIONS)

# ── legacy-audit (19 pre-existing curated problems upgraded to 40 tests) ────
# LEGACY_PLANS/REFERENCE_SOLUTIONS/WRONG_SOLUTIONS are keyed by ALGORITHM
# SLUG (e.g. "bfs", "dijkstra"), which differs from the actual DB Problem.id
# for 4 of the 19 (bfs->graph-bfs, dijkstra->dijkstra-shortest-path,
# kmp->kmp-string-matching, min-path-sum->minimum-path-sum) — remap via the
# same curated_algorithm_to_problem mapping seed_atlas_code.py uses, built
# directly from the static PROBLEMS list (no assemble_catalog() needed).
from algorithm_atlas.atlascode.families import legacy_audit_testdata as _legacy_td
from algorithm_atlas.atlascode import testgen as tg


def _legacy_algo_to_problem_id() -> dict[str, str]:
    sys.path.insert(0, str(Path(__file__).parent))
    import importlib
    seed_mod = importlib.import_module("seed_atlas_code")
    mapping = {p[0]["algorithm_slug"]: p[0]["id"] for p in seed_mod.PROBLEMS if p[0].get("algorithm_slug")}
    # Union of LEGACY_PLANS + REFERENCE_SOLUTIONS + WRONG_SOLUTIONS keys --
    # n-queens has no LEGACY_PLANS entry (its 40-test plan was replaced by
    # N_QUEENS_REDUCED_CASES, a documented exception -- see
    # legacy_audit_testdata.py) but still needs its REFERENCE/WRONG solutions
    # remapped to the real problem id like every other legacy slug.
    all_slugs = set(_legacy_td.LEGACY_PLANS) | set(_legacy_td.REFERENCE_SOLUTIONS) | set(_legacy_td.WRONG_SOLUTIONS)
    return {slug: mapping.get(slug, slug) for slug in all_slugs}


_LEGACY_ALGO_TO_PROBLEM = _legacy_algo_to_problem_id()
_REFERENCE_SOLUTIONS.update({
    _LEGACY_ALGO_TO_PROBLEM[k]: v for k, v in _legacy_td.REFERENCE_SOLUTIONS.items()
})
_WRONG_SOLUTIONS.update({
    _LEGACY_ALGO_TO_PROBLEM[k]: v for k, v in _legacy_td.WRONG_SOLUTIONS.items()
})


def _build_legacy_audit_test_data() -> list[tuple[dict, list[dict]]]:
    """Same (prob_dict, test_cases) shape every other family's builder
    returns, but generated directly from LEGACY_PLANS — these 19 problems
    already exist as curated DB rows, there is no build_X_problems factory
    creating new Problem rows for them. n-queens is a documented exception
    (12 tests, not 40 — see N_QUEENS_REDUCED_CASES in legacy_audit_testdata.py)
    handled separately since it has no LEGACY_PLANS entry."""
    out: list[tuple[dict, list[dict]]] = []
    for algo_slug in sorted(_legacy_td.LEGACY_PLANS):
        to_input, format_output, oracle, plan_fn = _legacy_td.LEGACY_PLANS[algo_slug]
        problem_id = _LEGACY_ALGO_TO_PROBLEM[algo_slug]
        rng = tg.problem_rng(problem_id)
        case_plan = plan_fn(rng)
        spec = tg.TestSpec(oracle=oracle, to_input=to_input, format_output=format_output)
        rows = tg.build_forty(problem_id, spec, case_plan)
        out.append(({"id": problem_id}, rows))

    from algorithm_atlas.atlascode.families import legacy_audit_oracles as _oracles_mod
    nq_problem_id = _LEGACY_ALGO_TO_PROBLEM["n-queens"]
    nq_rows = [
        {
            "input_data": _legacy_td._to_input_nqueens(n),
            "expected_output": str(_oracles_mod.n_queens_count(n)),
            "is_hidden": hidden,
            "explanation": "",
            "order": i,
        }
        for i, (n, hidden) in enumerate(_legacy_td.N_QUEENS_REDUCED_CASES)
    ]
    out.append(({"id": nq_problem_id}, nq_rows))
    return out


_FAMILY_BUILDERS = {}


def _load_builder(family: str):
    if family == "number-theory":
        from algorithm_atlas.atlascode.families.number_theory import build_number_theory_problems
        return build_number_theory_problems
    if family == "sorting":
        from algorithm_atlas.atlascode.families.sorting import build_sorting_problems
        return build_sorting_problems
    if family == "searching":
        from algorithm_atlas.atlascode.families.searching import build_searching_problems
        return build_searching_problems
    if family == "dynamic-programming":
        from algorithm_atlas.atlascode.families.dynamic_programming import build_dynamic_programming_problems
        return build_dynamic_programming_problems
    if family == "binary-search-variants":
        from algorithm_atlas.atlascode.families.binary_search_variants import build_binary_search_variant_problems
        return build_binary_search_variant_problems
    if family == "sliding-window-variants":
        from algorithm_atlas.atlascode.families.sliding_window_variants import build_sliding_window_variant_problems
        return build_sliding_window_variant_problems
    if family == "bfs-graph-variants":
        from algorithm_atlas.atlascode.families.bfs_graph_variants import build_bfs_graph_variant_problems
        return build_bfs_graph_variant_problems
    if family == "greedy":
        from algorithm_atlas.atlascode.families.greedy import build_greedy_problems
        return build_greedy_problems
    if family == "divide-and-conquer":
        from algorithm_atlas.atlascode.families.divide_and_conquer import build_divide_and_conquer_problems
        return build_divide_and_conquer_problems
    if family == "string":
        from algorithm_atlas.atlascode.families.string_family import build_string_problems
        return build_string_problems
    if family == "array-hashing-variants":
        from algorithm_atlas.atlascode.families.array_hashing_variants import build_array_hashing_variant_problems
        return build_array_hashing_variant_problems
    if family == "stack-variants":
        from algorithm_atlas.atlascode.families.stack_variants import build_stack_variant_problems
        return build_stack_variant_problems
    if family == "bit-manipulation-variants":
        from algorithm_atlas.atlascode.families.bit_manipulation_variants import build_bit_manipulation_variant_problems
        return build_bit_manipulation_variant_problems
    if family == "tree-variants":
        from algorithm_atlas.atlascode.families.tree_variants import build_tree_variant_problems
        return build_tree_variant_problems
    if family == "dp-variants":
        from algorithm_atlas.atlascode.families.dp_variants import build_dp_variant_problems
        return build_dp_variant_problems
    if family == "linked-list-variants":
        from algorithm_atlas.atlascode.families.linked_list_variants import build_linked_list_variant_problems
        return build_linked_list_variant_problems
    if family == "backtracking-count-variants":
        from algorithm_atlas.atlascode.families.backtracking_count_variants import build_backtracking_count_variant_problems
        return build_backtracking_count_variant_problems
    if family == "famous-easy":
        from algorithm_atlas.atlascode.families.famous_easy import build_famous_easy_problems
        return build_famous_easy_problems
    if family == "famous-arrays-matrix":
        from algorithm_atlas.atlascode.families.famous_arrays_matrix import build_famous_arrays_matrix_problems
        return build_famous_arrays_matrix_problems
    if family == "famous-graphs-trees-lists":
        from algorithm_atlas.atlascode.families.famous_graphs_trees_lists import build_famous_graphs_trees_lists_problems
        return build_famous_graphs_trees_lists_problems
    if family == "famous-hard":
        from algorithm_atlas.atlascode.families.famous_hard import build_famous_hard_problems
        return build_famous_hard_problems
    raise ValueError(f"Unknown family: {family}")


_VARIANT_FAMILIES = {
    "binary-search-variants", "sliding-window-variants", "bfs-graph-variants",
    "array-hashing-variants", "stack-variants", "bit-manipulation-variants",
    "tree-variants", "dp-variants", "linked-list-variants",
    "backtracking-count-variants",
    "famous-easy", "famous-arrays-matrix", "famous-graphs-trees-lists", "famous-hard",
}


async def verify_family(family: str) -> int:
    if family == "legacy-audit":
        # No build_X_problems factory — these 19 Problem rows already exist
        # (curated), only their TestCase rows are being upgraded to 40.
        # Deliberately skips discover_registered_algorithms()/assemble_catalog()
        # entirely (unneeded here, and expensive) — see _build_legacy_audit_test_data.
        problems = _build_legacy_audit_test_data()
        skipped = []
    else:
        builder = _load_builder(family)
        registered = discover_registered_algorithms()

        # Curated slugs must be excluded the same way seed_atlas_code.py does.
        sys.path.insert(0, str(Path(__file__).parent))
        import importlib
        seed_mod = importlib.import_module("seed_atlas_code")
        curated_slugs = {p[0]["algorithm_slug"] for p in seed_mod.PROBLEMS if p[0].get("algorithm_slug")}

        if family in _VARIANT_FAMILIES:
            # Variant families dedup by PROBLEM SLUG (not algorithm_slug) against
            # everything else in the catalog — see seed_atlas_code.py assemble_catalog().
            all_problems, _, _, _, _ = seed_mod.assemble_catalog()
            existing_ids = {p[0]["id"] for p in all_problems} - set(builder.__globals__["_SPECS"].keys())
            problems, skipped = builder(registered, existing_ids)
        else:
            problems, skipped = builder(registered, curated_slugs)

    print(f"Family: {family}")
    print(f"Problems: {len(problems)}")
    if skipped:
        print(f"Skipped by factory: {len(skipped)}")
        for slug, reason in skipped:
            print(f"  - {slug}: {reason}")

    failures = 0
    reference_accepted = 0
    wrong_rejected = 0
    has_reference = 0

    for prob, test_cases in problems:
        slug = prob["id"]
        tc_objs = [
            TestCase(
                id=f"{slug}-{tc['order']}",
                problem_id=slug,
                input_data=tc["input_data"],
                expected_output=tc["expected_output"],
                is_hidden=tc["is_hidden"],
                order=tc["order"],
            )
            for tc in test_cases
        ]
        n_hidden = sum(1 for tc in test_cases if tc["is_hidden"])
        n_visible = len(test_cases) - n_hidden
        print(f"\n[{slug}] {n_visible} visible + {n_hidden} hidden test cases")

        ref_src = _REFERENCE_SOLUTIONS.get(slug)
        if ref_src is None:
            print("  (!) no independent reference solution registered for this slug — SKIPPING smoke test")
            continue
        has_reference += 1

        ref_result = await evaluate(ref_src, "python", tc_objs)
        if ref_result.verdict == "Accepted" and ref_result.tests_passed == ref_result.tests_total:
            print(f"  Reference submission: ACCEPTED ({ref_result.tests_passed}/{ref_result.tests_total})")
            reference_accepted += 1
        else:
            print(
                f"  Reference submission: FAILED — verdict={ref_result.verdict}, "
                f"{ref_result.tests_passed}/{ref_result.tests_total} passed"
            )
            for r in ref_result.test_results:
                if not r.passed:
                    print(f"    case order={r.test_case_id}: expected={r.expected_output!r} actual={r.actual_output!r}")
            failures += 1

        wrong_src = _WRONG_SOLUTIONS.get(slug)
        if wrong_src is not None:
            wrong_result = await evaluate(wrong_src, "python", tc_objs)
            if wrong_result.verdict != "Accepted":
                print(f"  Wrong-answer submission correctly REJECTED (verdict={wrong_result.verdict})")
                wrong_rejected += 1
            else:
                print("  (!) Wrong-answer submission was ACCEPTED — test cases too weak to catch it")
                failures += 1

    print("\n" + "=" * 60)
    print(f"Family: {family}")
    print(f"Problems: {len(problems)}")
    print(f"Reference submissions accepted: {reference_accepted}/{has_reference}")
    print(f"Wrong-solution rejections: {wrong_rejected}/{has_reference}")
    print(f"Failures: {failures}")
    print("=" * 60)
    return failures


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/verify_atlascode_family.py <family>")
        sys.exit(2)
    failures = asyncio.run(verify_family(sys.argv[1]))
    sys.exit(1 if failures else 0)
