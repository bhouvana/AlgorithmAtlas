# AtlasCode Famous-Concepts Audit (2026-07-05)

Cross-referenced every candidate concept from the mega-prompt's own suggestion
list against the **live** 189-problem catalog (queried directly from `atlas.db`,
not from memory or the blueprint file) before writing a single new problem.
Per the mega-prompt's own copyright rule, every new problem below ships with
original AtlasCode wording/examples/tests — no LeetCode statement, example, or
test data is copied.

## Already covered (rejected as new candidates — would be duplicates)

| Candidate | Existing AtlasCode slug | Why it's the same concept |
|---|---|---|
| Two Sum | `two-sum`, `two-sum-count-pairs` | exact match |
| Valid Parentheses | `valid-parentheses` | exact match |
| Best Time to Buy/Sell Stock (I, II) | `best-time-to-buy-sell-stock(-ii)` | exact match |
| Valid Anagram | `valid-anagram` | exact match |
| Maximum Subarray | `maximum-subarray` | exact match (Kadane's) |
| Merge Two Sorted Lists | `merge-two-sorted-lists` | exact match |
| Reverse Linked List | `reverse-linked-list` | exact match |
| Linked List Cycle | `linked-list-cycle-detect` | exact match |
| Binary Tree Max Depth | `max-depth-binary-tree` | exact match |
| Invert Binary Tree | `invert-tree-preorder` | exact match |
| Same Tree | `same-tree` | exact match |
| Symmetric Tree | `is-symmetric-tree` | exact match |
| Climbing Stairs | `staircase` | exact match |
| Single Number (I, II) | `single-number(-ii)` | exact match |
| Majority Element (I, II) | `majority-element(-ii)` | exact match |
| Missing Number | `missing-number` | exact match |
| First Unique Character | `first-unique-character-index` | exact match |
| Three Sum | `three-sum-count-triplets` | same computation (counts distinct triplets instead of listing them — already a deliberate exact-match-judge-safe variant) |
| Group Anagrams | `group-anagrams-count` | same computation, count framing |
| Product of Array Except Self | `product-of-array-except-self` | exact match |
| Longest Substring Without Repeating | `longest-substring-without-repeating` | exact match |
| Longest Repeating Char Replacement | `longest-repeating-char-replacement` | exact match |
| Minimum Size Subarray Sum | `min-subarray-len-target-sum` | exact match |
| Search in Rotated Sorted Array | `rotated-binary-search` | exact match |
| Find Minimum in Rotated Sorted Array | `find-minimum-rotated-sorted-array` | exact match |
| Container With Most Water | `container-with-most-water` | exact match |
| Top K Frequent Elements | `top-k-frequent-elements` | exact match |
| Non-overlapping Intervals | `activity-selection` | mathematically identical (`n - max_non_overlapping`) |
| Number of Islands | `number-of-islands` | exact match |
| Rotting Oranges | `rotten-oranges-minutes` | exact match |
| Combination Sum (generate) | — | too close to `catalan-number`/backtracking-count family in spirit; superseded below by a distinct count-framed version |
| Generate Parentheses (count) | `catalan-number` | mathematically identical oracle (Catalan number) |
| Permutations (count) | `unique-permutations-count` | exact match |
| House Robber | `house-robber` | exact match |
| Unique Paths | `unique-paths` | exact match |
| Decode Ways | `decode-ways` | exact match |
| Coin Change (min coins, ways) | `coin-change`, `coin-change-ways` | exact match |
| Longest Increasing Subsequence | `longest-increasing-subsequence` | exact match |
| Longest Common Subsequence | `longest-common-subsequence` | exact match |
| Partition Equal Subset Sum | `partition-equal-subset-sum` | exact match |
| Binary Tree Level Order Traversal | `level-order-traversal` | exact match |
| Validate BST | `is-valid-bst` | exact match |
| Kth Smallest in BST | `kth-smallest-in-bst` | exact match |
| LRU Cache | — | needs a multi-command simulation I/O shape the judge doesn't support yet; deferred, not silently dropped |
| Daily Temperatures | `daily-temperatures` | exact match |
| Next Greater Element | `next-greater-element` | exact match |
| Trapping Rain Water | `trapping-rain-water` | exact match |
| Minimum Window Substring | `minimum-window-substring-length` | exact match |
| Largest Rectangle in Histogram | `largest-rectangle-in-histogram` | exact match |
| Palindrome Partitioning (min cuts) | `palindrome-partition` | exact match |
| Wildcard Matching | `wildcard-matching` | exact match |
| Binary Tree Maximum Path Sum | `binary-tree-max-path-sum` | exact match |
| Word Ladder | `word-ladder-length` | exact match |
| N-Queens | `n-queens` | exact match |
| Edit Distance | `edit-distance` | exact match |
| Pow(x, n) | `fast-power` | identical algorithm (fast exponentiation) |
| Longest Palindromic Subsequence | `palindrome-subsequence` | exact match |
| Coin Change min-coins duplicate | `coin-change` | exact match |
| Copy List with Random Pointer | — | output representation (arbitrary pointer graph) not tractable in the current stdin/stdout exact-match judge; deferred |
| Clone Graph | — | same reason — deferred, flagged as needing a structural-equivalence judge mode, not built this session |

## Genuinely missing — selected for this batch (22 problems)

Selected for (a) high recognizability, (b) a clearly distinct oracle/algorithm
from everything in the table above (verified via `scripts/check_atlascode_duplicates.py`
after implementation — see Part III results), (c) tractability in the
existing stdin/stdout exact-match judge.

**Easy (5)**
1. `move-zeroes` — move all zeros to the end preserving relative order of non-zeros
2. `flood-fill` — single-source grid paint (distinct from `number-of-islands`'s connectivity count and `rotten-oranges`'s multi-source BFS)
3. `merge-sorted-arrays-inplace` — merge two sorted arrays (array contract, distinct from the linked-list version already shipped)
4. `valid-palindrome-string` — alphanumeric-only, case-insensitive two-pointer check (distinct from `palindrome-linked-list` and `longest-palindromic-substring`)
5. `find-duplicate-number` — Floyd's cycle detection treating array values as pointers (distinct from `missing-number`)

**Medium (17)**
6. `kth-largest-element` — heap-based order statistic (independent oracle, distinct framing from `median-of-medians`)
7. `merge-overlapping-intervals` — returns the merged interval list (distinct output contract from `meeting-rooms`'/`activity-selection`'s scalar counts)
8. `insert-interval` — insert + merge into an already-sorted disjoint interval list
9. `course-schedule-feasible` — topological-sort feasibility (Kahn's algorithm; distinct from `is-bipartite`'s coloring)
10. `word-search-grid` — 2D backtracking path search for a target word
11. `combination-sum-count` — count of multisets summing to a target (matches the project's existing `-count` exact-match-safe convention)
12. `distinct-subsets-count` — count of distinct subsets from a multiset with duplicates
13. `house-robber-circular` — circular-street DP variant of `house-robber`
14. `lowest-common-ancestor-binary-tree` — general binary tree LCA (no BST ordering assumption — different algorithm from `lowest-common-ancestor-bst`)
15. `construct-tree-preorder-inorder` — reconstruct a binary tree from its preorder+inorder traversals
16. `sliding-window-maximum` — monotonic-deque max-of-every-window (distinct output shape from every existing window problem)
17. `binary-tree-zigzag-level-order` — alternating-direction level order (distinct output pattern from `level-order-traversal`)
18. `add-two-numbers-linked-list` — digit-by-digit linked-list addition
19. `subarray-product-less-than-k` — sliding window on product, not sum
20. `spiral-matrix-traversal` — simulate spiral matrix walk
21. `rotate-image-90` — in-place matrix rotation
22. `set-matrix-zeroes` — matrix zeroing propagation

**Hard (6)**
23. `median-of-two-sorted-arrays` — binary-search-on-partition (flagship hard, distinct from every existing binary-search variant)
24. `regular-expression-matching` — `.`/`*` regex DP (distinct transition rules from `wildcard-matching`'s `?`/`*`)
25. `merge-k-sorted-lists` — heap-driven k-way linked-list merge
26. `burst-balloons` — interval DP (distinct pattern from `matrix-chain-multiplication`)
27. `maximal-rectangle` — 2D extension of `largest-rectangle-in-histogram` (different input shape: matrix, not array)
28. `longest-valid-parentheses` — hard stack/DP variant, distinct from `valid-parentheses` (boolean) and `remove-k-digits`

Total selected: **28** (5 Easy / 11 Medium / 6 Hard... plus 6 Hard = 28; see
implementation status in `docs/atlascode-resume.md` for exactly how many of
these 28 shipped fully-verified vs were dropped after failing verification).

## Deliberately deferred (not built this session, not silently dropped)

- `lru-cache-simulation` — needs a multi-command sequence I/O shape (`INSERT`/`GET`/... commands with per-command output lines) the current single-input/single-output judge contract doesn't cleanly express yet.
- `clone-graph` — output is an arbitrary object graph; needs a structural-equivalence judge mode (compare graph isomorphism, not string equality), not built this session.
- `reverse-nodes-in-k-group` — genuinely missing and famous, but linked-list I/O + k-group reversal was deprioritized below the 28 selected above for time; flagged for the next batch.
