import type { LessonData } from '../../lessons/GenericLesson';

export const greedyBacktrackingAdvancedLessons: Record<string, LessonData> = {

  'activity-selection': {
    concept: {
      overview:
        'The Activity Selection Problem asks: given n activities each with a start and finish time, select the maximum number of non-overlapping activities. The greedy solution — always pick the activity with the earliest finish time — is provably optimal and runs in O(n log n) after sorting.',
      keyPoints: [
        { title: 'Greedy Choice', desc: 'Always select the activity with the earliest finish time among remaining non-conflicting activities. This leaves the maximum remaining time for future activities.' },
        { title: 'Proof of Optimality', desc: 'By exchange argument: any optimal solution can be modified to use the earliest-finish activity without decreasing the count. So greedy is always at least as good as any other choice.' },
        { title: 'O(n log n)', desc: 'Sort activities by finish time (O(n log n)), then a single greedy pass selects activities in O(n). Total: O(n log n).' },
      ],
    },
    steps: [
      { n: '1', label: 'Sort by finish time', desc: 'Sort all activities by their finish time ascending.', code: 'activities.sort(key=lambda a: a[1])' },
      { n: '2', label: 'Select first activity', desc: 'Always include the activity with earliest finish time.', code: 'selected = [activities[0]]\nlast_finish = activities[0][1]' },
      { n: '3', label: 'Greedily select remaining', desc: 'For each activity: if its start time >= last finish time, select it.', code: 'for start, finish in activities[1:]:\n    if start >= last_finish:\n        selected.append((start, finish))\n        last_finish = finish' },
      { n: '4', label: 'Return selected activities', desc: 'The selected list contains the maximum non-overlapping set.' },
    ],
    codeExamples: [
      {
        label: 'Activity Selection — Greedy',
        complexity: 'O(n log n)',
        code: 'def activity_selection(activities):\n    # activities = [(start, finish), ...]\n    activities.sort(key=lambda a: a[1])  # sort by finish time\n\n    selected = [activities[0]]\n    last_finish = activities[0][1]\n\n    for start, finish in activities[1:]:\n        if start >= last_finish:\n            selected.append((start, finish))\n            last_finish = finish\n\n    return selected\n\n# Example:\n# acts = [(1,4),(3,5),(0,6),(5,7),(3,9),(5,9),(6,10),(8,11)]\n# activity_selection(acts) -> [(1,4),(5,7),(8,11)] = 3 activities',
      },
      {
        label: 'Meeting Room Variant (count minimum rooms)',
        complexity: 'O(n log n)',
        code: 'import heapq\n\ndef min_meeting_rooms(meetings):\n    if not meetings: return 0\n    meetings.sort(key=lambda m: m[0])  # sort by start\n\n    heap = []  # min-heap of end times\n    for start, end in meetings:\n        if heap and heap[0] <= start:\n            heapq.heapreplace(heap, end)  # reuse room\n        else:\n            heapq.heappush(heap, end)  # new room needed\n\n    return len(heap)',
      },
    ],
    complexity: {
      rows: [
        { case: 'Sort', value: 'O(n log n)', color: 'text-amber-400', note: 'Sorting activities by finish time' },
        { case: 'Selection pass', value: 'O(n)', color: 'text-indigo-400', note: 'Single linear scan after sorting' },
        { case: 'Space', value: 'O(1)', color: 'text-emerald-400', note: 'Only store last finish time' },
      ],
    },
    realWorld: [
      { title: 'Meeting Room Scheduling', desc: 'Schedule maximum meetings in a conference room given each meeting\'s start and end time.' },
      { title: 'CPU Task Scheduling', desc: 'Select maximum tasks to complete on a single CPU without preemption.' },
      { title: 'Event Planning', desc: 'Maximize events attended at a conference given overlapping session times.' },
      { title: 'Classroom Allocation', desc: 'Assign maximum courses to a classroom by picking non-overlapping time slots.' },
    ],
    quiz: [
      { q: 'What is the greedy choice for activity selection?', options: ['Activity with earliest start time', 'Shortest duration activity', 'Activity with earliest finish time', 'Activity with latest start time'], correct: 2, explanation: 'Choosing earliest finish time leaves maximum remaining time for future activities.' },
      { q: 'Why does the greedy algorithm work for activity selection?', options: ['Because it tries all combinations', 'Exchange argument shows earliest-finish never worse than any other choice', 'Because activities are sorted', 'It only works for small inputs'], correct: 1, explanation: 'Any solution using a different first activity can be swapped to use earliest-finish without reducing count.' },
      { q: 'What is the time complexity after sorting?', options: ['O(n²)', 'O(n log n)', 'O(n)', 'O(log n)'], correct: 1, explanation: 'Sorting is O(n log n); the greedy pass is O(n). Total dominated by sort: O(n log n).' },
      { q: 'Which of the following is NOT a valid real-world application of activity selection?', options: ['Scheduling meetings in a conference room', 'Maximizing events attended at a conference', 'Finding the shortest path in a graph', 'Allocating a classroom to non-overlapping courses'], correct: 2, explanation: 'Shortest path is solved by Dijkstra\'s algorithm, not activity selection. Activity selection applies to scheduling non-overlapping intervals.' },
      { q: 'If activities are already sorted by finish time, what is the time complexity of the greedy selection pass?', options: ['O(n log n)', 'O(n²)', 'O(n)', 'O(1)'], correct: 2, explanation: 'A single linear scan through pre-sorted activities is O(n) — each activity is examined exactly once.' },
      { q: 'What would happen if you used "earliest start time" as the greedy choice instead of "earliest finish time"?', options: ['It would always give the optimal answer', 'It could select an activity that blocks many future activities', 'It runs faster than earliest finish time', 'It produces the same result as earliest finish time'], correct: 1, explanation: 'An activity starting earliest may have a very late finish time, preventing many other valid activities from being selected — earliest start is not optimal.' },
    ],
  },

  'huffman-coding': {
    concept: {
      overview:
        'Huffman coding is an optimal prefix-free encoding scheme where more frequent characters receive shorter binary codes and less frequent characters receive longer ones. Built greedily with a min-heap: repeatedly merge the two lowest-frequency nodes into a new parent. The resulting binary tree defines the code — left edges = 0, right edges = 1.',
      keyPoints: [
        { title: 'Prefix-Free', desc: 'No codeword is a prefix of another. This ensures unambiguous decoding without separator characters. Example: if \'a\'=01, no other character can start with 01.' },
        { title: 'Greedy Construction', desc: 'Always merge the two nodes with lowest frequency. The greedy choice is provably optimal — it minimizes the total weighted path length (sum of freq * code_length).' },
        { title: 'Entropy Bound', desc: 'Huffman coding achieves an average code length within 1 bit of the theoretical Shannon entropy H = -sum(p * log2(p)), making it near-optimal compression.' },
      ],
    },
    steps: [
      { n: '1', label: 'Count frequencies', desc: 'Count how many times each character appears in the input.', code: 'from collections import Counter\nfreqs = Counter(text)' },
      { n: '2', label: 'Build min-heap', desc: 'Create a min-heap of (frequency, char) pairs.', code: 'import heapq\nheap = [[freq, [char, ""]] for char, freq in freqs.items()]\nheapq.heapify(heap)' },
      { n: '3', label: 'Merge two smallest', desc: 'Pop the two smallest nodes, prepend "0" to left codes and "1" to right codes, push combined node.', code: 'while len(heap) > 1:\n    lo = heapq.heappop(heap)\n    hi = heapq.heappop(heap)\n    for pair in lo[1:]: pair[1] = "0" + pair[1]\n    for pair in hi[1:]: pair[1] = "1" + pair[1]\n    heapq.heappush(heap, [lo[0]+hi[0]] + lo[1:] + hi[1:])' },
      { n: '4', label: 'Read codes', desc: 'The final node in the heap contains all (char, code) pairs.', code: 'codes = {pair[0]: pair[1] for pair in heap[0][1:]}' },
    ],
    codeExamples: [
      {
        label: 'Huffman Encoding',
        complexity: 'O(n log n)',
        code: 'import heapq\nfrom collections import Counter\n\ndef huffman_codes(text):\n    freq = Counter(text)\n    heap = [[f, [c, ""]] for c, f in freq.items()]\n    heapq.heapify(heap)\n\n    while len(heap) > 1:\n        lo = heapq.heappop(heap)\n        hi = heapq.heappop(heap)\n        for pair in lo[1:]: pair[1] = "0" + pair[1]\n        for pair in hi[1:]: pair[1] = "1" + pair[1]\n        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])\n\n    return {pair[0]: pair[1] for pair in heap[0][1:]}\n\n# For "aabbbcccc":\n# a->00, b->01, c->1\n# Avg bits per char: 2*2/9 + 3*2/9 + 4*1/9 ≈ 1.56',
      },
      {
        label: 'Encode and Decode',
        complexity: 'O(n)',
        code: 'def encode(text, codes):\n    return "".join(codes[c] for c in text)\n\ndef decode(encoded, codes):\n    # Reverse codes: bit_string -> char\n    reverse = {v: k for k, v in codes.items()}\n    result = []\n    current = ""\n    for bit in encoded:\n        current += bit\n        if current in reverse:\n            result.append(reverse[current])\n            current = ""\n    return "".join(result)',
      },
    ],
    complexity: {
      rows: [
        { case: 'Build tree', value: 'O(n log n)', color: 'text-amber-400', note: 'n heap operations each O(log n)' },
        { case: 'Encode/Decode', value: 'O(L)', color: 'text-indigo-400', note: 'L = length of encoded string' },
        { case: 'Space', value: 'O(n)', color: 'text-indigo-400', note: 'Code table has n entries (n = unique chars)' },
      ],
    },
    realWorld: [
      { title: 'ZIP / DEFLATE', desc: 'ZIP files use Huffman coding as part of the DEFLATE compression algorithm.' },
      { title: 'JPEG Images', desc: 'JPEG uses a modified Huffman scheme to compress the quantized DCT coefficients.' },
      { title: 'MP3 Audio', desc: 'MP3 uses Huffman coding for entropy coding of audio spectral coefficients.' },
      { title: 'HTTP/2', desc: 'HPACK header compression in HTTP/2 uses a static Huffman code for header field values.' },
    ],
    quiz: [
      { q: 'What makes Huffman coding "prefix-free"?', options: ['All codes have the same length', 'No codeword is a prefix of another', 'Codes use no zeros', 'Characters are sorted alphabetically'], correct: 1, explanation: 'Prefix-free means the encoding is unambiguously decodable — each code is a leaf in the binary tree, never an internal node.' },
      { q: 'What greedy choice does Huffman coding make at each step?', options: ['Merge two highest-frequency nodes', 'Merge two lowest-frequency nodes', 'Add the most frequent character first', 'Assign shortest code to rarest character'], correct: 1, explanation: 'Merging the two nodes with lowest frequency minimizes the total weighted path length.' },
      { q: 'What does the frequency of a character affect in Huffman coding?', options: ['Its position in the alphabet', 'The length of its binary code', 'Whether it is included', 'Its position in the heap'], correct: 1, explanation: 'More frequent characters get shorter codes (closer to root in the Huffman tree), reducing average bits per character.' },
      { q: 'What data structure is used during Huffman tree construction?', options: ['Stack', 'Queue', 'Min-heap (priority queue)', 'Hash table'], correct: 2, explanation: 'A min-heap lets us efficiently extract the two nodes with the lowest frequency at each step in O(log n) time.' },
      { q: 'How close to optimal is Huffman coding compared to Shannon entropy?', options: ['Exactly at entropy', 'Within 1 bit per symbol of the Shannon entropy', 'Always 2 bits worse than entropy', 'It is unrelated to entropy'], correct: 1, explanation: 'Huffman coding achieves average code length within 1 bit of the theoretical minimum Shannon entropy H = -Σ p·log₂(p).' },
      { q: 'Which real-world format uses Huffman coding as part of its compression?', options: ['PNG (lossless images)', 'BMP (bitmap images)', 'WAV (uncompressed audio)', 'CSV (text data)'], correct: 0, explanation: 'PNG uses DEFLATE compression, which combines LZ77 (dictionary matching) with Huffman coding for entropy coding of the output.' },
    ],
  },

  'fractional-knapsack': {
    concept: {
      overview:
        'In the Fractional Knapsack problem, you can take any fraction of an item — unlike the 0/1 version. The greedy solution is optimal: sort items by value-per-weight (value density) and take as much of the most valuable item as possible, then the next, until the knapsack is full.',
      keyPoints: [
        { title: 'Greedy Works Here', desc: 'Unlike 0/1 knapsack, greedy works for fractional because taking more of any item never "blocks" another optimal choice. The continuous divisibility allows greedy to be globally optimal.' },
        { title: 'Value Density', desc: 'Sort by value/weight ratio (value density). Greedily take items in order of density — take the full item if it fits, otherwise take the fraction that fills the remaining capacity.' },
        { title: 'O(n log n)', desc: 'Dominated by sorting. After sorting, a single O(n) pass fills the knapsack. Compare to 0/1 knapsack\'s O(nW) DP — fractional is much faster.' },
      ],
    },
    steps: [
      { n: '1', label: 'Compute value densities', desc: 'For each item, compute value/weight ratio.', code: 'items = sorted(items, key=lambda x: x[1]/x[0], reverse=True)' },
      { n: '2', label: 'Sort by density', desc: 'Sort items descending by value/weight. The most valuable-per-unit items come first.' },
      { n: '3', label: 'Fill greedily', desc: 'Take each item fully if it fits; otherwise take the fraction that fills remaining capacity.', code: 'total_value = 0\nfor weight, value in items:\n    if remaining >= weight:\n        total_value += value\n        remaining -= weight\n    else:\n        total_value += value * (remaining / weight)\n        break' },
    ],
    codeExamples: [
      {
        label: 'Fractional Knapsack',
        complexity: 'O(n log n)',
        code: 'def fractional_knapsack(items, capacity):\n    # items = [(weight, value), ...]\n    # Sort by value/weight ratio descending\n    items = sorted(items, key=lambda x: x[1]/x[0], reverse=True)\n\n    total_value = 0\n    remaining = capacity\n\n    for weight, value in items:\n        if remaining <= 0:\n            break\n        if weight <= remaining:\n            total_value += value\n            remaining -= weight\n        else:\n            # Take fraction\n            fraction = remaining / weight\n            total_value += value * fraction\n            remaining = 0\n\n    return total_value\n\n# Example: capacity=50\n# items=[(10,60),(20,100),(30,120)]\n# Density: 6, 5, 4\n# Take all 10+20=30, then 20/30 of last\n# Value = 60+100+80 = 240',
      },
      {
        label: 'Why greedy fails for 0/1 Knapsack',
        code: '# Counter-example showing greedy fails for 0/1:\n# capacity = 10\n# items: [(weight, value)]\n# item A: (10, 60) -> density 6.0\n# item B: (6, 40)  -> density 6.67 *highest*\n# item C: (4, 30)  -> density 7.5  *highest*\n\n# Greedy 0/1 picks C then B (weight 10, value 70)\n# Optimal 0/1 picks A (weight 10, value 60)...wait\n# Actually picks B+C (weight 10, value 70) -- same here\n\n# Better counter-example:\n# capacity=10, items=[(6,12),(4,10),(3,6)]\n# density: 2.0, 2.5, 2.0\n# Greedy picks (4,10) then (6,12) -- 10kg, value=22\n#            ...but (6,12)+(4,10) IS optimal!\n# The key: for 0/1, greedy SOMETIMES works but NOT always guaranteed',
        variant: 'warn',
      },
    ],
    complexity: {
      rows: [
        { case: 'Sort', value: 'O(n log n)', color: 'text-amber-400', note: 'Sort by value density' },
        { case: 'Fill pass', value: 'O(n)', color: 'text-indigo-400', note: 'Single pass through sorted items' },
        { case: 'Space', value: 'O(1)', color: 'text-emerald-400', note: 'Constant extra space' },
      ],
    },
    realWorld: [
      { title: 'Investment Allocation', desc: 'Allocate a fixed budget across divisible investments to maximize expected return (e.g., index funds).' },
      { title: 'Bandwidth Distribution', desc: 'Distribute limited network bandwidth to data streams proportionally by priority.' },
      { title: 'Cargo Loading', desc: 'Load a ship with divisible bulk goods (grain, liquid) to maximize value within weight capacity.' },
      { title: 'Ad Budget Allocation', desc: 'Spend a fixed marketing budget across campaigns where partial spending is allowed.' },
    ],
    quiz: [
      { q: 'Why does greedy work for fractional knapsack but not 0/1 knapsack?', options: ['Fractional has fewer items', 'Divisibility ensures partial items don\'t block future optimal choices', 'Fractional is always faster', 'The weights are different'], correct: 1, explanation: 'When items are divisible, taking a fraction never prevents an optimal future choice — greedy is globally optimal.' },
      { q: 'What is the greedy criterion for fractional knapsack?', options: ['Sort by value descending', 'Sort by weight ascending', 'Sort by value/weight ratio descending', 'Sort by weight/value ratio'], correct: 2, explanation: 'Value density (value/weight) determines how much value you get per unit of capacity used.' },
      { q: 'What is the time complexity of fractional knapsack?', options: ['O(nW)', 'O(n²)', 'O(n log n)', 'O(n)'], correct: 2, explanation: 'Sorting is O(n log n); the greedy fill pass is O(n). Total: O(n log n).' },
      { q: 'What is the time complexity of the 0/1 knapsack solved with dynamic programming?', options: ['O(n log n)', 'O(n²)', 'O(nW) where W is capacity', 'O(2^n)'], correct: 2, explanation: '0/1 knapsack DP fills an n×W table, giving O(nW) time — much slower than fractional knapsack\'s O(n log n) greedy solution.' },
      { q: 'In fractional knapsack, if two items have the same value/weight ratio, which should you pick first?', options: ['The heavier one', 'The lighter one', 'It does not matter — both choices yield the same total value', 'The one with higher absolute value'], correct: 2, explanation: 'Items with identical value density contribute the same value per unit of capacity, so their selection order does not affect the optimal total value.' },
      { q: 'Which property of items makes fractional knapsack solvable by greedy?', options: ['Items are sorted by weight', 'Items can be taken in any fraction (continuous divisibility)', 'Items have integer weights', 'Items have the same value'], correct: 1, explanation: 'Continuous divisibility means you can always fill remaining capacity with the best available item, so greedy never needs to "look ahead".' },
    ],
  },

  'n-queens': {
    concept: {
      overview:
        'The N-Queens problem asks: place N queens on an N×N chessboard so that no two queens threaten each other — no two in the same row, column, or diagonal. Backtracking explores placements row by row, immediately pruning branches when a placement causes a conflict, making it far more efficient than brute force.',
      keyPoints: [
        { title: 'Backtracking', desc: 'Try placing a queen in each column of the current row. If placement is safe, recurse to the next row. If we reach row N, a solution is found. If no column works, backtrack to the previous row.' },
        { title: 'Constraint Checking', desc: 'Track occupied columns and both diagonals (/ and \\). A position (r,c) conflicts with (r2,c2) if c==c2 (same column), r-c==r2-c2 (same main diagonal), or r+c==r2+c2 (same anti-diagonal).' },
        { title: 'Pruning Power', desc: 'Without pruning, brute force checks N^N placements. Backtracking prunes invalid branches early — for N=8 only ~2000 nodes are explored vs 16 million for brute force.' },
      ],
    },
    steps: [
      { n: '1', label: 'Set up constraint tracking', desc: 'Track which columns and diagonals are under attack.', code: 'cols = set()\ndiag1 = set()  # row - col\ndiag2 = set()  # row + col\nboard = ["."] * N' },
      { n: '2', label: 'Try each column in current row', desc: 'For each column c in the current row, check if (row, c) is safe.', code: 'for c in range(N):\n    if c in cols or (row-c) in diag1 or (row+c) in diag2:\n        continue' },
      { n: '3', label: 'Place queen and recurse', desc: 'Place queen at (row, c), update constraints, recurse to row+1.', code: 'cols.add(c); diag1.add(row-c); diag2.add(row+c)\nboard[c] = "Q"\nbacktrack(row + 1)\nboard[c] = "."  # undo' },
      { n: '4', label: 'Backtrack', desc: 'After recursion, remove the queen and undo all constraint updates.', code: 'cols.remove(c); diag1.remove(row-c); diag2.remove(row+c)' },
      { n: '5', label: 'Base case', desc: 'When row == N, all queens placed without conflict. Add current board to solutions.', code: 'if row == N:\n    solutions.append(["".join(row) for row in board])\n    return' },
    ],
    codeExamples: [
      {
        label: 'N-Queens Backtracking',
        complexity: 'O(N!) worst case',
        code: 'def solve_n_queens(N):\n    solutions = []\n    cols = set()\n    diag1 = set()  # row - col\n    diag2 = set()  # row + col\n    board = [[\".\"]*N for _ in range(N)]\n\n    def backtrack(row):\n        if row == N:\n            solutions.append([\"\".join(r) for r in board])\n            return\n        for c in range(N):\n            if c in cols or (row-c) in diag1 or (row+c) in diag2:\n                continue\n            # Place queen\n            board[row][c] = "Q"\n            cols.add(c); diag1.add(row-c); diag2.add(row+c)\n            backtrack(row + 1)\n            # Remove queen (backtrack)\n            board[row][c] = "."\n            cols.discard(c); diag1.discard(row-c); diag2.discard(row+c)\n\n    backtrack(0)\n    return solutions\n\n# N=8: 92 solutions\n# N=1: 1 solution',
      },
      {
        label: 'Count Solutions Only',
        complexity: 'O(N!)',
        code: 'def count_n_queens(N):\n    count = [0]\n    cols = set()\n    d1, d2 = set(), set()\n\n    def bt(row):\n        if row == N:\n            count[0] += 1\n            return\n        for c in range(N):\n            if c not in cols and (row-c) not in d1 and (row+c) not in d2:\n                cols.add(c); d1.add(row-c); d2.add(row+c)\n                bt(row+1)\n                cols.discard(c); d1.discard(row-c); d2.discard(row+c)\n\n    bt(0)\n    return count[0]\n\n# count_n_queens(8) = 92',
      },
    ],
    complexity: {
      rows: [
        { case: 'Time (worst)', value: 'O(N!)', color: 'text-red-400', note: 'Upper bound; pruning makes actual much faster' },
        { case: 'Space', value: 'O(N)', color: 'text-indigo-400', note: 'Board is N×N, recursion depth N, constraint sets O(N)' },
        { case: 'Solutions (N=8)', value: '92', color: 'text-emerald-400', note: 'Classic result; grows rapidly with N' },
      ],
    },
    realWorld: [
      { title: 'Constraint Satisfaction', desc: 'N-Queens is the canonical CSP (Constraint Satisfaction Problem) — techniques apply to scheduling, planning.' },
      { title: 'Register Allocation', desc: 'Assigning variables to CPU registers without conflicts uses similar backtracking on constraint graphs.' },
      { title: 'Puzzle Solving', desc: 'N-Queens engines are used in puzzle solving platforms and AI textbook examples of backtracking.' },
      { title: 'Test Case Generation', desc: 'Combinatorial testing uses similar constraint-based backtracking to generate test cases covering all constraints.' },
    ],
    quiz: [
      { q: 'How does backtracking improve over brute force for N-Queens?', options: ['It uses parallel processing', 'It prunes branches early when constraints are violated', 'It sorts queens by value', 'It uses dynamic programming'], correct: 1, explanation: 'Backtracking stops exploring a branch the moment a conflict is detected, avoiding millions of wasted placements.' },
      { q: 'What three constraints must be satisfied for each queen?', options: ['Same row, column, and rank', 'Different row, different column, different diagonal', 'Adjacent rows only', 'Queens in corners only'], correct: 1, explanation: 'No two queens can share a row, column, or diagonal (both main and anti-diagonal).' },
      { q: 'How many solutions does 8-Queens have?', options: ['12', '42', '92', '184'], correct: 2, explanation: 'There are exactly 92 distinct solutions to the 8-Queens problem (12 fundamental solutions, 80 reflections/rotations).' },
      { q: 'How is the anti-diagonal constraint tracked efficiently in N-Queens backtracking?', options: ['Scanning entire board each time', 'Using row + col as the diagonal identifier', 'Sorting columns', 'Using a 2D visited array'], correct: 1, explanation: 'Cells on the same anti-diagonal share the same row + col sum. Storing these sums in a set allows O(1) conflict checking.' },
      { q: 'What is the space complexity of the N-Queens backtracking solution (excluding output)?', options: ['O(N²)', 'O(N!)', 'O(N)', 'O(1)'], correct: 2, explanation: 'We store N queens\' column positions, three constraint sets of size O(N), and the recursion stack of depth N — all O(N).' },
      { q: 'If a valid placement is found at row r during N-Queens backtracking, what happens next?', options: ['The algorithm stops immediately', 'We recurse to row r+1 to place the next queen', 'We restart from row 0', 'We validate the entire board'], correct: 1, explanation: 'After placing a queen in a valid column at row r, we recurse to row r+1. If row r+1 has no valid columns, we backtrack to row r.' },
    ],
  },

  'sudoku': {
    concept: {
      overview:
        'Sudoku Solver uses backtracking to fill a 9×9 grid with digits 1-9 such that each row, column, and 3×3 box contains every digit exactly once. For each empty cell, we try each valid digit, place it, recurse to the next empty cell, and backtrack if we reach a dead end. Constraint propagation can dramatically prune the search space.',
      keyPoints: [
        { title: 'Backtracking Core', desc: 'Find empty cell, try digits 1-9, check validity (row + column + box), recurse. If recursion fails (no valid digit), backtrack: reset cell and return False to try the next digit in the parent call.' },
        { title: 'Constraint Checking', desc: 'Three constraints: digit not in same row, not in same column, not in same 3×3 box. Box index = (row//3)*3 + col//3. Checking all three in O(1) with sets.' },
        { title: 'Constraint Propagation', desc: 'Advanced solvers use "naked singles" (only one digit valid for a cell) and "hidden singles" (digit can go in only one cell in a row/col/box) to reduce backtracking.' },
      ],
    },
    steps: [
      { n: '1', label: 'Find empty cell', desc: 'Scan the grid for the first empty cell (marked 0 or ".").', code: 'def find_empty(board):\n    for r in range(9):\n        for c in range(9):\n            if board[r][c] == 0:\n                return r, c\n    return None' },
      { n: '2', label: 'Try digits 1-9', desc: 'For each digit 1-9, check if placing it is valid.', code: 'for digit in range(1, 10):\n    if is_valid(board, row, col, digit):\n        board[row][col] = digit' },
      { n: '3', label: 'Check validity', desc: 'Verify digit not in current row, column, or 3×3 box.', code: 'def is_valid(board, row, col, digit):\n    if digit in board[row]: return False\n    if digit in [board[r][col] for r in range(9)]: return False\n    br, bc = (row//3)*3, (col//3)*3\n    for r in range(br, br+3):\n        for c in range(bc, bc+3):\n            if board[r][c] == digit: return False\n    return True' },
      { n: '4', label: 'Recurse and backtrack', desc: 'Recurse to next cell. If recursion returns True, done. If False, reset cell and try next digit.', code: 'if solve(board): return True\nboard[row][col] = 0  # backtrack' },
    ],
    codeExamples: [
      {
        label: 'Sudoku Solver — Backtracking',
        complexity: 'O(9^empty_cells) worst case',
        code: 'def solve_sudoku(board):\n    empty = find_empty(board)\n    if not empty:\n        return True  # all cells filled!\n    row, col = empty\n\n    for digit in range(1, 10):\n        if is_valid(board, row, col, digit):\n            board[row][col] = digit\n            if solve_sudoku(board):\n                return True\n            board[row][col] = 0  # backtrack\n\n    return False  # trigger backtracking\n\ndef find_empty(board):\n    for r in range(9):\n        for c in range(9):\n            if board[r][c] == 0:\n                return (r, c)\n    return None\n\ndef is_valid(board, row, col, digit):\n    if digit in board[row]:\n        return False\n    if any(board[r][col] == digit for r in range(9)):\n        return False\n    br, bc = (row // 3)*3, (col // 3)*3\n    for r in range(br, br+3):\n        for c in range(bc, bc+3):\n            if board[r][c] == digit:\n                return False\n    return True',
      },
      {
        label: 'Optimized: Most Constrained Cell First',
        complexity: 'Much faster in practice',
        code: '# Choose the cell with fewest valid options first\n# (Minimum Remaining Values heuristic)\ndef find_most_constrained(board):\n    min_options = 10\n    best_cell = None\n    for r in range(9):\n        for c in range(9):\n            if board[r][c] == 0:\n                options = sum(is_valid(board,r,c,d) for d in range(1,10))\n                if options < min_options:\n                    min_options = options\n                    best_cell = (r, c)\n    return best_cell\n\n# This dramatically reduces search tree size\n# compared to always picking the first empty cell',
        variant: 'good',
      },
    ],
    complexity: {
      rows: [
        { case: 'Worst case', value: 'O(9^81)', color: 'text-red-400', note: 'All cells empty, 9 choices each (theoretical max)' },
        { case: 'Practical', value: 'O(9^empty)', color: 'text-indigo-400', note: 'Typical puzzles have 50-60 empty cells; pruning is very effective' },
        { case: 'Space', value: 'O(81)', color: 'text-emerald-400', note: 'Board is 9×9, recursion depth ≤ 81' },
      ],
    },
    realWorld: [
      { title: 'Puzzle Solvers', desc: 'Every Sudoku app and website uses backtracking (often with constraint propagation) to solve puzzles.' },
      { title: 'Constraint Satisfaction AI', desc: 'Sudoku is a teaching example for CSP algorithms in AI courses (AC-3, backtracking search).' },
      { title: 'Logic Puzzles', desc: 'Similar constraint-satisfaction backtracking solves Kakuro, Nonograms, and other logic puzzles.' },
      { title: 'Formal Verification', desc: 'SAT solvers (like those used in chip design verification) use similar DPLL backtracking algorithms.' },
    ],
    quiz: [
      { q: 'What is the backtracking step in Sudoku solving?', options: ['Scan for empty cells', 'Reset cell to 0 and return False when no digit works', 'Check all constraints', 'Fill with random digit'], correct: 1, explanation: 'When no valid digit (1-9) can be placed in the current empty cell, reset it to 0 and return False to trigger backtracking.' },
      { q: 'What three constraints must each digit satisfy?', options: ['Row, column, 3x3 box', 'Row, color, position', 'Top half, bottom half, middle', 'Size, shape, value'], correct: 0, explanation: 'Each digit 1-9 must appear exactly once in its row, once in its column, and once in its 3×3 box.' },
      { q: 'What is the Minimum Remaining Values heuristic for Sudoku?', options: ['Fill cells with most neighbors first', 'Choose the empty cell with fewest valid options', 'Start from bottom-right', 'Fill largest values first'], correct: 1, explanation: 'MRV selects the most constrained cell first, reducing branching factor and speeding up backtracking dramatically.' },
      { q: 'What is the box index formula for the 3×3 sub-grid containing cell (row, col)?', options: ['row * col', '(row // 3) * 3 + col // 3', 'row + col', '(row % 3) + (col % 3)'], correct: 1, explanation: '(row // 3) * 3 + col // 3 maps each cell to one of the 9 boxes (0–8), allowing O(1) box membership checks.' },
      { q: 'What does "constraint propagation" mean in the context of Sudoku solving?', options: ['Trying all 9 digits at each cell', 'Deducing forced cell values from existing constraints before backtracking', 'Generating all possible boards', 'Sorting cells by row number'], correct: 1, explanation: 'Constraint propagation (e.g., naked singles) eliminates impossible digits from cells using current placements, reducing the search space before any backtracking is needed.' },
      { q: 'Why does basic Sudoku backtracking perform well in practice despite an O(9^81) worst case?', options: ['Sudoku boards are always nearly complete', 'Constraint checking prunes invalid branches very early in the recursion', 'The algorithm uses memoization', 'It runs in parallel'], correct: 1, explanation: 'With 25–30 pre-filled clues, most branches are pruned within the first few recursive calls when constraint violations are detected early.' },
    ],
  },

  'permutations': {
    concept: {
      overview:
        'Generate all permutations of a set of elements using backtracking. For n elements, there are n! permutations. The swap-based approach avoids extra memory: at each recursion level, swap the current index with each subsequent index to place every element at the current position, then recurse.',
      keyPoints: [
        { title: 'n! Permutations', desc: 'The number of permutations of n distinct elements is n! (n factorial). For n=10 this is 3.6 million. Generating all requires at least O(n * n!) time for output.' },
        { title: 'Swap-Based Backtracking', desc: 'At position i, swap arr[i] with arr[j] for each j from i to n-1, placing every element at position i. Recurse on position i+1. After recursion, swap back (backtrack).' },
        { title: 'Subsets and Combinations', desc: 'Similar backtracking generates subsets (choose include/exclude at each step) and combinations (choose k of n). The recursive structure is identical; only the choice at each node differs.' },
      ],
    },
    steps: [
      { n: '1', label: 'Base case', desc: 'When start == len(arr), we\'ve fixed all positions. Record the current arrangement.', code: 'if start == len(arr):\n    results.append(arr[:])\n    return' },
      { n: '2', label: 'Try each element at current position', desc: 'For each index j from start to end, place arr[j] at position start by swapping.', code: 'for j in range(start, len(arr)):\n    arr[start], arr[j] = arr[j], arr[start]' },
      { n: '3', label: 'Recurse', desc: 'After swap, recurse with start+1 to fix the next position.', code: 'permute(arr, start+1, results)' },
      { n: '4', label: 'Backtrack', desc: 'Swap back to restore original order before trying the next j.', code: 'arr[start], arr[j] = arr[j], arr[start]  # undo swap' },
    ],
    codeExamples: [
      {
        label: 'All Permutations (swap-based)',
        complexity: 'O(n * n!)',
        code: 'def permutations(arr):\n    results = []\n\n    def backtrack(start):\n        if start == len(arr):\n            results.append(arr[:])  # copy current arrangement\n            return\n        for j in range(start, len(arr)):\n            arr[start], arr[j] = arr[j], arr[start]  # place arr[j] at start\n            backtrack(start + 1)\n            arr[start], arr[j] = arr[j], arr[start]  # undo\n\n    backtrack(0)\n    return results\n\n# permutations([1,2,3]) returns:\n# [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,2,1],[3,1,2]]',
      },
      {
        label: 'All Subsets (Power Set)',
        complexity: 'O(n * 2^n)',
        code: 'def subsets(nums):\n    result = []\n\n    def backtrack(start, current):\n        result.append(current[:])  # record every partial state\n        for i in range(start, len(nums)):\n            current.append(nums[i])\n            backtrack(i + 1, current)\n            current.pop()  # backtrack\n\n    backtrack(0, [])\n    return result\n\n# subsets([1,2,3]) returns:\n# [[], [1], [1,2], [1,2,3], [1,3], [2], [2,3], [3]]',
      },
    ],
    complexity: {
      rows: [
        { case: 'Time (permutations)', value: 'O(n × n!)', color: 'text-red-400', note: 'n! permutations, each length n to copy' },
        { case: 'Time (subsets)', value: 'O(n × 2^n)', color: 'text-red-400', note: '2^n subsets of average size n/2' },
        { case: 'Space', value: 'O(n)', color: 'text-indigo-400', note: 'Recursion depth n; not counting output' },
      ],
    },
    realWorld: [
      { title: 'Brute-Force TSP', desc: 'Travelling Salesman Problem brute force tries all n! orderings of cities to find the shortest tour.' },
      { title: 'Anagram Generation', desc: 'Generating all anagrams of a word requires producing all permutations of its characters.' },
      { title: 'Test Case Generation', desc: 'Combinatorial testing generates all permutations/subsets of input parameters.' },
      { title: 'Scheduling', desc: 'Enumerating all possible job schedules to find the optimal ordering under constraints.' },
    ],
    quiz: [
      { q: 'How many permutations does a set of 5 distinct elements have?', options: ['25', '120', '10', '32'], correct: 1, explanation: '5! = 5 × 4 × 3 × 2 × 1 = 120. Factorial grows very rapidly.' },
      { q: 'What is the purpose of swapping back after recursion?', options: ['To sort the array', 'To restore the original order (backtracking)', 'To generate duplicates', 'To mark visited elements'], correct: 1, explanation: 'After exploring a branch with a particular swap, we undo it to explore other possibilities at the same level.' },
      { q: 'How many subsets does a set of n elements have?', options: ['n!', 'n²', '2^n', 'n log n'], correct: 2, explanation: 'Each element is either in or out of a subset: 2 choices × n elements = 2^n total subsets.' },
      { q: 'Why does the swap-based permutation algorithm avoid extra memory for the current path?', options: ['It uses a global variable', 'It rearranges the input array in place, so arr itself always holds the current permutation', 'It copies the array at every step', 'It uses an index stack'], correct: 1, explanation: 'By swapping elements within the original array rather than building a new list, we avoid O(n) extra space for each recursive call.' },
      { q: 'What modification turns the permutation backtracking into a combination generator (choose k of n)?', options: ['Remove the swap-back step', 'Stop recursion when the current list has k elements and only iterate i from start onwards', 'Sort the array first', 'Use a queue instead of recursion'], correct: 1, explanation: 'Combinations fix the size at k and enforce ordering by only extending with indices greater than the last chosen index, avoiding duplicates and size overruns.' },
      { q: 'What is the time complexity to generate all permutations of n elements, including copying each permutation?', options: ['O(n!)', 'O(n × n!)', 'O(2^n)', 'O(n² × n!)'], correct: 1, explanation: 'There are n! permutations and each copy (to store the result) takes O(n) time, giving a total of O(n × n!).' },
    ],
  },

  'kmp': {
    concept: {
      overview:
        'The Knuth-Morris-Pratt (KMP) algorithm searches for a pattern of length m in a text of length n in O(n+m) time, never revisiting a character in the text. It achieves this by precomputing a "failure function" (also called the partial match or prefix table) that encodes the longest proper prefix of the pattern that is also a suffix — allowing smart jumps on mismatch.',
      keyPoints: [
        { title: 'Failure Function', desc: 'The failure function fail[j] = the length of the longest proper prefix of pattern[0..j] that is also a suffix. This tells us where to resume in the pattern after a mismatch, without restarting from 0.' },
        { title: 'Never Goes Backward', desc: 'The text pointer i only moves forward. On mismatch, only the pattern pointer j jumps back using fail[j-1]. This guarantees O(n) for the search phase.' },
        { title: 'O(n+m) Total', desc: 'Preprocessing the failure function takes O(m). The search phase takes O(n). Compare to naive O(nm) string search.' },
      ],
    },
    steps: [
      { n: '1', label: 'Build failure function', desc: 'For each position j in pattern, compute the longest prefix-suffix match length.', code: 'def build_failure(pattern):\n    m = len(pattern)\n    fail = [0] * m\n    j = 0\n    for i in range(1, m):\n        while j > 0 and pattern[i] != pattern[j]:\n            j = fail[j-1]\n        if pattern[i] == pattern[j]:\n            j += 1\n        fail[i] = j\n    return fail' },
      { n: '2', label: 'Initialize search', desc: 'Start text pointer i=0 and pattern pointer j=0.', code: 'i = 0  # text pointer\nj = 0  # pattern pointer' },
      { n: '3', label: 'Match characters', desc: 'Compare text[i] and pattern[j]. On match, advance both. On mismatch, use failure function to update j.', code: 'while i < n:\n    if text[i] == pattern[j]:\n        i += 1; j += 1\n    elif j > 0:\n        j = fail[j-1]  # smart jump\n    else:\n        i += 1' },
      { n: '4', label: 'Record matches', desc: 'When j == m (full pattern matched), record the match at i-m and update j using failure function.', code: 'if j == m:\n    matches.append(i - m)\n    j = fail[j-1]  # continue searching' },
    ],
    codeExamples: [
      {
        label: 'KMP Search',
        complexity: 'O(n+m)',
        code: 'def kmp_search(text, pattern):\n    n, m = len(text), len(pattern)\n    if m == 0: return []\n\n    # Build failure function\n    fail = [0] * m\n    j = 0\n    for i in range(1, m):\n        while j > 0 and pattern[i] != pattern[j]:\n            j = fail[j-1]\n        if pattern[i] == pattern[j]:\n            j += 1\n        fail[i] = j\n\n    # Search\n    matches = []\n    j = 0\n    for i in range(n):\n        while j > 0 and text[i] != pattern[j]:\n            j = fail[j-1]\n        if text[i] == pattern[j]:\n            j += 1\n        if j == m:\n            matches.append(i - m + 1)\n            j = fail[j-1]\n\n    return matches\n\n# kmp_search("ABABDABACDABABCABAB", "ABABCABAB")\n# -> [10]',
      },
      {
        label: 'Failure Function Example',
        code: '# Pattern: "ABABCABAB"\n# Index:    0 1 2 3 4 5 6 7 8\n# fail[]:   0 0 1 2 0 1 2 3 4\n\n# fail[4] = 0: "ABABC" -> longest prefix==suffix: "" (length 0)\n# fail[7] = 3: "ABABCABA" -> "ABA" is both prefix and suffix (length 3)\n# fail[8] = 4: "ABABCABAB" -> "ABAB" (length 4)\n\n# On mismatch at pattern pos j, jump to fail[j-1]\n# This avoids re-scanning text characters already matched',
        variant: 'good',
      },
    ],
    complexity: {
      rows: [
        { case: 'Preprocessing', value: 'O(m)', color: 'text-indigo-400', note: 'Build failure function in O(m)' },
        { case: 'Search', value: 'O(n)', color: 'text-indigo-400', note: 'Text pointer never moves backward' },
        { case: 'Total', value: 'O(n+m)', color: 'text-indigo-400', note: 'vs naive O(nm)' },
        { case: 'Space', value: 'O(m)', color: 'text-indigo-400', note: 'Failure function array of length m' },
      ],
    },
    realWorld: [
      { title: 'Text Editors', desc: 'Find/Replace in editors like vim, VS Code, and grep use KMP-inspired algorithms.' },
      { title: 'Bioinformatics', desc: 'Searching for gene sequences (patterns) within DNA strings (text) in genome databases.' },
      { title: 'Network Intrusion Detection', desc: 'Deep packet inspection scans network traffic for known attack signature patterns.' },
      { title: 'File Search', desc: 'Searching for byte sequences in binary files uses multi-pattern KMP variants (Aho-Corasick).' },
    ],
    quiz: [
      { q: 'What does the failure function fail[j] represent?', options: ['Number of matches at position j', 'Length of longest proper prefix of pattern[0..j] that is also a suffix', 'Number of characters to skip', 'Pattern length minus j'], correct: 1, explanation: 'The failure function encodes where to resume matching in the pattern after a mismatch, avoiding redundant character comparisons.' },
      { q: 'Why is KMP O(n+m) instead of O(nm)?', options: ['It uses hashing', 'The text pointer never moves backward', 'It only processes unique characters', 'It skips every other character'], correct: 1, explanation: 'Text pointer i only advances. On mismatch, pattern pointer j jumps back via failure function, never moving i backward.' },
      { q: 'What does the failure function encode for pattern "ABAB"?', options: ['[0,0,0,0]', '[0,0,1,2]', '[1,1,2,3]', '[0,1,0,1]'], correct: 1, explanation: 'fail[0]=0, fail[1]=0 (B has no prefix=suffix), fail[2]=1 (A), fail[3]=2 (AB). "ABAB" has prefix "AB" = suffix "AB".' },
      { q: 'What happens in KMP when a mismatch occurs at pattern position j == 0?', options: ['The pattern pointer jumps to fail[-1]', 'The text pointer advances by one and the pattern restarts from 0', 'The search terminates', 'The pattern is reversed'], correct: 1, explanation: 'When j==0 and there is a mismatch, there is no fallback in the pattern; we simply advance the text pointer i and keep j at 0.' },
      { q: 'Compared to the naive string search, what is KMP\'s main advantage?', options: ['It uses less memory', 'It never moves the text pointer backward, achieving O(n) instead of O(nm)', 'It works on unsorted text', 'It handles Unicode automatically'], correct: 1, explanation: 'Naive search can reset the text pointer by up to m positions on each mismatch. KMP\'s failure function eliminates backward text movement entirely.' },
      { q: 'Which algorithm extends KMP to efficiently search for multiple patterns simultaneously?', options: ['Rabin-Karp', 'Boyer-Moore', 'Aho-Corasick', 'Z-algorithm'], correct: 2, explanation: 'Aho-Corasick builds a trie of all patterns with KMP-style failure links, enabling simultaneous multi-pattern search in O(n + total_pattern_length + matches) time.' },
    ],
  },

  'rabin-karp': {
    concept: {
      overview:
        'Rabin-Karp uses a rolling hash to slide a window across the text and compare hash values with the pattern hash. Matching hashes trigger a character-by-character verification (to handle hash collisions). Its O(n+m) average complexity makes it especially powerful for multi-pattern search.',
      keyPoints: [
        { title: 'Rolling Hash', desc: 'Compute hash of the first m-character window, then slide: subtract leftmost character\'s contribution and add new rightmost character. Each slide takes O(1) — this is the key insight.' },
        { title: 'Spurious Hits', desc: 'When hashes match but strings don\'t (hash collision), this is a spurious hit. Verification (O(m)) catches these. A good hash function minimizes spurious hits, keeping average complexity O(n+m).' },
        { title: 'Multi-Pattern', desc: 'Rabin-Karp can search for k patterns simultaneously: compute all k pattern hashes once, compare each window hash against all k. Better than running KMP k times for large k.' },
      ],
    },
    steps: [
      { n: '1', label: 'Choose hash base and modulus', desc: 'Use a prime modulus to reduce collisions. Base = alphabet size (e.g., 256 for ASCII).', code: 'BASE = 256\nMOD = 101  # prime' },
      { n: '2', label: 'Compute initial hashes', desc: 'Compute hash of pattern and first m characters of text.', code: 'p_hash = t_hash = 0\nfor i in range(m):\n    p_hash = (p_hash * BASE + ord(pattern[i])) % MOD\n    t_hash = (t_hash * BASE + ord(text[i])) % MOD' },
      { n: '3', label: 'Slide window', desc: 'For each position, if hashes match verify. Then compute next hash by removing leftmost and adding rightmost char.', code: 'h = pow(BASE, m-1, MOD)  # leftmost char coefficient\nfor i in range(n - m + 1):\n    if p_hash == t_hash:\n        if text[i:i+m] == pattern:  # verify\n            matches.append(i)\n    if i < n - m:\n        t_hash = (BASE*(t_hash - ord(text[i])*h) + ord(text[i+m])) % MOD\n        t_hash = (t_hash + MOD) % MOD  # handle negative' },
    ],
    codeExamples: [
      {
        label: 'Rabin-Karp Search',
        complexity: 'O(n+m) average, O(nm) worst',
        code: 'def rabin_karp(text, pattern):\n    n, m = len(text), len(pattern)\n    if m > n: return []\n\n    BASE, MOD = 256, 101\n    h = pow(BASE, m-1, MOD)  # for removing leftmost char\n\n    p_hash = 0  # pattern hash\n    t_hash = 0  # text window hash\n    for i in range(m):\n        p_hash = (BASE * p_hash + ord(pattern[i])) % MOD\n        t_hash = (BASE * t_hash + ord(text[i])) % MOD\n\n    matches = []\n    for i in range(n - m + 1):\n        if p_hash == t_hash:\n            if text[i:i+m] == pattern:  # verify (handle collisions)\n                matches.append(i)\n        if i < n - m:\n            # Roll the hash\n            t_hash = (BASE * (t_hash - ord(text[i]) * h) + ord(text[i+m])) % MOD\n            if t_hash < 0:\n                t_hash += MOD\n\n    return matches',
      },
      {
        label: 'Multi-Pattern Search',
        complexity: 'O(n + sum of pattern lengths)',
        code: '# Rabin-Karp excels at searching many patterns at once\ndef multi_pattern_search(text, patterns):\n    n = len(text)\n    results = {p: [] for p in patterns}\n\n    for pattern in patterns:\n        m = len(pattern)\n        # Run Rabin-Karp for each pattern\n        # For k patterns: O(n*k) with naive, same O(n+m*k) with RK\n        # Alternative: build Aho-Corasick trie for O(n + total_m)\n        matches = rabin_karp(text, pattern)\n        results[pattern] = matches\n\n    return results\n\n# Better: Aho-Corasick for truly simultaneous multi-pattern',
        variant: 'good',
      },
    ],
    complexity: {
      rows: [
        { case: 'Average case', value: 'O(n+m)', color: 'text-indigo-400', note: 'With good hash function and few collisions' },
        { case: 'Worst case', value: 'O(nm)', color: 'text-orange-400', note: 'Many hash collisions (pathological input)' },
        { case: 'Space', value: 'O(1)', color: 'text-emerald-400', note: 'Only a few hash values stored' },
      ],
    },
    realWorld: [
      { title: 'Plagiarism Detection', desc: 'Hash rolling windows of student code to find copied sections matching a pattern database.' },
      { title: 'Bioinformatics', desc: 'Scanning genome sequences for multiple motifs simultaneously using rolling hash comparison.' },
      { title: 'File Deduplication', desc: 'Rsync uses a rolling checksum (similar to Rabin-Karp) to find matching blocks between files.' },
      { title: 'Network Security', desc: 'Intrusion detection systems scan packet payloads for multiple attack signatures using rolling hashes.' },
    ],
    quiz: [
      { q: 'What is a spurious hit in Rabin-Karp?', options: ['A missed match', 'A hash match that is not an actual string match', 'A pattern longer than text', 'Negative hash value'], correct: 1, explanation: 'A spurious hit occurs when hash(window) == hash(pattern) but the actual characters don\'t match — a hash collision.' },
      { q: 'Why is Rabin-Karp worst case O(nm)?', options: ['Sorting takes O(nm)', 'All windows cause hash collisions requiring O(m) verification each', 'The rolling hash fails', 'The modulus is too small'], correct: 1, explanation: 'If every window hash matches the pattern hash (e.g., all same character), every position requires O(m) verification.' },
      { q: 'What advantage does Rabin-Karp have over KMP for multiple patterns?', options: ['It is always faster', 'It can search for k patterns by comparing each window hash against k pattern hashes simultaneously', 'It has O(1) space', 'It handles Unicode better'], correct: 1, explanation: 'One pass over the text with O(k) hash comparisons per position finds all k patterns — vs k separate KMP passes.' },
      { q: 'What is the role of the large prime modulus in the Rabin-Karp rolling hash?', options: ['It sorts the characters', 'It reduces the probability of hash collisions', 'It speeds up multiplication', 'It ensures all hashes are positive'], correct: 1, explanation: 'A large prime modulus distributes hash values more uniformly, making it unlikely that two different strings produce the same hash (spurious hit).' },
      { q: 'In the Rabin-Karp rolling hash, what is the purpose of the value h = BASE^(m-1) mod MOD?', options: ['It stores the pattern hash', 'It represents the weight of the leftmost character for removal during the slide', 'It is the initial text hash', 'It counts characters'], correct: 1, explanation: 'When sliding the window, the leftmost character\'s contribution (ord(text[i]) * BASE^(m-1)) must be subtracted. Precomputing h avoids recomputing this power each step.' },
      { q: 'What distinguishes Rabin-Karp from KMP in terms of correctness guarantees?', options: ['Rabin-Karp is always faster', 'Rabin-Karp requires a verification step after each hash match to handle collisions; KMP has no false positives', 'KMP requires verification; Rabin-Karp does not', 'Both algorithms have the same false positive rate'], correct: 1, explanation: 'KMP compares characters directly and never produces false positives. Rabin-Karp compares hashes which can collide, requiring character-by-character verification on hash matches.' },
    ],
  },

  'network-flow': {
    concept: {
      overview:
        'Network Flow finds the maximum amount of flow that can be sent from a source (s) to a sink (t) through a directed graph where each edge has a capacity. The Ford-Fulkerson method repeatedly finds augmenting paths and sends flow along them. By the max-flow min-cut theorem, the maximum flow equals the minimum cut capacity.',
      keyPoints: [
        { title: 'Residual Graph', desc: 'For each edge (u,v,cap) in the flow network, maintain a residual edge (v,u,cap-flow) and a backward edge (u,v,flow) for potential reversal. Augmenting paths use the residual graph.' },
        { title: 'Augmenting Path', desc: 'Any path from s to t in the residual graph with positive residual capacity. Flow along this path equals the minimum residual capacity (bottleneck). Edmonds-Karp uses BFS to find shortest augmenting path.' },
        { title: 'Max-Flow Min-Cut', desc: 'The maximum flow equals the minimum cut — the minimum total capacity of edges whose removal disconnects s from t. This duality is one of the most beautiful theorems in combinatorics.' },
      ],
    },
    steps: [
      { n: '1', label: 'Build residual graph', desc: 'Create graph with forward edges (capacity) and backward edges (initially 0).', code: 'graph[u][v] = capacity\ngraph[v][u] = 0  # backward edge' },
      { n: '2', label: 'Find augmenting path (BFS)', desc: 'Use BFS to find a path from source to sink in residual graph where all edges have positive capacity.', code: 'def bfs(source, sink, parent):\n    visited = {source}\n    queue = deque([source])\n    while queue:\n        u = queue.popleft()\n        for v in range(V):\n            if v not in visited and graph[u][v] > 0:\n                visited.add(v)\n                parent[v] = u\n                if v == sink: return True\n                queue.append(v)\n    return False' },
      { n: '3', label: 'Find bottleneck', desc: 'Trace the path backwards from sink to source and find the minimum residual capacity.', code: 'path_flow = float("inf")\nv = sink\nwhile v != source:\n    u = parent[v]\n    path_flow = min(path_flow, graph[u][v])\n    v = parent[v]' },
      { n: '4', label: 'Augment flow', desc: 'Update residual capacities along the path.', code: 'v = sink\nwhile v != source:\n    u = parent[v]\n    graph[u][v] -= path_flow\n    graph[v][u] += path_flow\n    v = parent[v]\nmax_flow += path_flow' },
    ],
    codeExamples: [
      {
        label: 'Edmonds-Karp (BFS-based Ford-Fulkerson)',
        complexity: 'O(VE²)',
        code: 'from collections import deque\n\ndef edmonds_karp(graph, source, sink, V):\n    max_flow = 0\n\n    while True:\n        parent = [-1] * V\n        visited = {source}\n        queue = deque([source])\n\n        while queue and parent[sink] == -1:\n            u = queue.popleft()\n            for v in range(V):\n                if v not in visited and graph[u][v] > 0:\n                    visited.add(v)\n                    parent[v] = u\n                    queue.append(v)\n\n        if parent[sink] == -1:\n            break  # no more augmenting paths\n\n        # Find path bottleneck\n        path_flow = float("inf")\n        v = sink\n        while v != source:\n            u = parent[v]\n            path_flow = min(path_flow, graph[u][v])\n            v = u\n\n        # Augment along path\n        v = sink\n        while v != source:\n            u = parent[v]\n            graph[u][v] -= path_flow\n            graph[v][u] += path_flow\n            v = u\n\n        max_flow += path_flow\n\n    return max_flow',
      },
      {
        label: 'Max Bipartite Matching (application)',
        complexity: 'O(VE)',
        code: '# Network flow solves bipartite matching!\n# Left nodes: 0..L-1, Right nodes: L..L+R-1\n# Source s connects to all left, all right connect to sink t\n\ndef max_bipartite_matching(L, R, edges):\n    V = L + R + 2\n    s, t = V-2, V-1\n    graph = [[0]*V for _ in range(V)]\n\n    for u in range(L):   # source -> left nodes\n        graph[s][u] = 1\n    for v in range(R):   # right nodes -> sink\n        graph[L+v][t] = 1\n    for u, v in edges:   # left -> right\n        graph[u][L+v] = 1\n\n    return edmonds_karp(graph, s, t, V)',
      },
    ],
    complexity: {
      rows: [
        { case: 'Edmonds-Karp', value: 'O(VE²)', color: 'text-violet-400', note: 'BFS finds shortest augmenting path' },
        { case: 'Ford-Fulkerson', value: 'O(E × max_flow)', color: 'text-red-400', note: 'Can be slow for large capacities' },
        { case: 'Dinic\'s Algorithm', value: 'O(V²E)', color: 'text-amber-400', note: 'Faster in practice for unit-capacity graphs' },
      ],
    },
    realWorld: [
      { title: 'Traffic Engineering', desc: 'Maximize vehicle throughput from origin to destination through a road network with lane capacities.' },
      { title: 'Job Assignment', desc: 'Assign workers to jobs via max bipartite matching — which reduces to max flow.' },
      { title: 'Airline Scheduling', desc: 'Maximize passengers routed through a hub-and-spoke network with flight capacity constraints.' },
      { title: 'Image Segmentation', desc: 'Graph cuts for image segmentation use min-cut (dual of max-flow) to separate foreground/background.' },
    ],
    quiz: [
      { q: 'What is a residual graph in network flow?', options: ['The original flow network', 'A graph showing remaining capacity on edges and possible flow reversal', 'The shortest path tree', 'The minimum spanning tree'], correct: 1, explanation: 'The residual graph includes forward edges (remaining capacity) and backward edges (current flow, allowing cancellation).' },
      { q: 'What does the Max-Flow Min-Cut theorem state?', options: ['Maximum flow equals number of vertices', 'Maximum flow equals minimum cut capacity', 'Flow can exceed cut capacity', 'Every cut equals the flow'], correct: 1, explanation: 'The maximum amount of flow from s to t exactly equals the minimum capacity of any s-t cut.' },
      { q: 'What makes Edmonds-Karp different from basic Ford-Fulkerson?', options: ['Uses DFS instead of BFS', 'Uses BFS to find shortest augmenting paths', 'Only works for unit capacities', 'Requires sorted edges'], correct: 1, explanation: 'Edmonds-Karp specifies BFS for finding augmenting paths, guaranteeing O(VE²) regardless of capacity values.' },
      { q: 'Why can basic Ford-Fulkerson (using DFS) be very slow with large capacities?', options: ['DFS misses augmenting paths', 'It may augment by 1 unit per iteration, requiring up to max_flow iterations', 'DFS cannot traverse residual edges', 'Large capacities require sorting'], correct: 1, explanation: 'If DFS picks an augmenting path with bottleneck 1 every time, it needs O(max_flow) iterations — making complexity O(E × max_flow) which is unbounded for large capacities.' },
      { q: 'How does max-flow relate to bipartite matching?', options: ['They are unrelated problems', 'Max bipartite matching equals the max flow in a derived network with unit capacities', 'Bipartite matching requires min-cut', 'Flow algorithms cannot solve matching problems'], correct: 1, explanation: 'Connect a super-source to all left nodes and all right nodes to a super-sink with unit-capacity edges. Max flow in this network equals the maximum bipartite matching.' },
      { q: 'What property of the residual graph indicates that no more augmenting paths exist?', options: ['The source has no outgoing edges', 'There is no path from source to sink with positive residual capacity', 'All edge capacities are zero', 'The graph has an odd number of vertices'], correct: 1, explanation: 'When BFS (or DFS) on the residual graph cannot reach the sink from the source, the algorithm terminates. The current flow is maximum by the max-flow min-cut theorem.' },
    ],
  },

  'suffix-arrays': {
    concept: {
      overview:
        'A suffix array is an array of integers representing the starting positions of all suffixes of a string, sorted in lexicographic order. For "banana", the sorted suffixes give SA = [5,3,1,0,4,2]. Combined with the LCP (Longest Common Prefix) array, suffix arrays enable O(m log n) pattern search, finding longest repeated substrings, and data compression in O(n) space.',
      keyPoints: [
        { title: 'Compact Representation', desc: 'Suffix arrays store O(n) integers vs O(n²) for a full suffix trie. With the LCP array they provide most of a suffix tree\'s functionality at fraction of the memory.' },
        { title: 'Binary Search Pattern Matching', desc: 'To find pattern P in text T, binary search the suffix array. All occurrences are contiguous in the array. Binary search takes O(m log n) comparisons.' },
        { title: 'LCP Array', desc: 'LCP[i] = length of longest common prefix between SA[i] and SA[i-1]. Enables efficient range minimum queries (RMQ) for finding longest repeated substrings in O(n) time.' },
      ],
    },
    steps: [
      { n: '1', label: 'Generate all suffixes', desc: 'For string of length n, generate suffixes s[i:] for i from 0 to n-1.', code: 'suffixes = [(s[i:], i) for i in range(len(s))]' },
      { n: '2', label: 'Sort suffixes', desc: 'Sort (suffix, index) pairs lexicographically.', code: 'suffixes.sort(key=lambda x: x[0])\nsa = [idx for _, idx in suffixes]' },
      { n: '3', label: 'Build LCP array', desc: 'For each adjacent pair in suffix array, compute their longest common prefix.', code: 'def build_lcp(s, sa):\n    n = len(s)\n    rank = [0] * n\n    for i, idx in enumerate(sa): rank[idx] = i\n    lcp = [0] * n\n    h = 0\n    for i in range(n):\n        if rank[i] > 0:\n            j = sa[rank[i]-1]\n            while i+h < n and j+h < n and s[i+h]==s[j+h]: h+=1\n            lcp[rank[i]] = h\n            if h > 0: h -= 1\n    return lcp' },
      { n: '4', label: 'Pattern search via binary search', desc: 'Binary search SA to find leftmost and rightmost occurrence of pattern.', code: 'import bisect\nlo = bisect.bisect_left(sa, pattern, key=lambda i: s[i:])\nhi = bisect.bisect_right(sa, pattern, key=lambda i: s[i:len(i)+len(pattern)])' },
    ],
    codeExamples: [
      {
        label: 'Naive Suffix Array Construction',
        complexity: 'O(n² log n)',
        code: 'def build_suffix_array(s):\n    n = len(s)\n    # Create (suffix, original_index) pairs\n    suffixes = sorted(range(n), key=lambda i: s[i:])\n    return suffixes\n\n# For "banana":\n# Suffixes: banana,anana,nana,ana,na,a\n# Sorted:   a,ana,anana,banana,na,nana\n# SA:       [5,3,1,0,4,2]\n\n# Efficient O(n log n) construction:\n# Use prefix doubling (Manber-Myers algorithm)\n# or DC3/Skew algorithm for O(n)',
      },
      {
        label: 'Pattern Search using Suffix Array',
        complexity: 'O(m log n)',
        code: 'def search_pattern(s, sa, pattern):\n    n, m = len(s), len(pattern)\n\n    # Find leftmost occurrence (lower bound)\n    lo, hi = 0, n\n    while lo < hi:\n        mid = (lo + hi) // 2\n        suffix = s[sa[mid]:sa[mid]+m]\n        if suffix < pattern:\n            lo = mid + 1\n        else:\n            hi = mid\n    left = lo\n\n    # Find rightmost occurrence (upper bound)\n    hi = n\n    while lo < hi:\n        mid = (lo + hi) // 2\n        suffix = s[sa[mid]:sa[mid]+m]\n        if suffix <= pattern:\n            lo = mid + 1\n        else:\n            hi = mid\n    right = lo\n\n    return sa[left:right]  # all occurrences\n\n# Returns sorted list of starting positions',
      },
    ],
    complexity: {
      rows: [
        { case: 'Build (naive)', value: 'O(n² log n)', color: 'text-red-400', note: 'Sorting n strings of avg length n/2' },
        { case: 'Build (DC3/SA-IS)', value: 'O(n)', color: 'text-emerald-400', note: 'Linear construction using clever recursion' },
        { case: 'Pattern search', value: 'O(m log n)', color: 'text-cyan-400', note: 'Binary search with m-char comparisons' },
        { case: 'Space', value: 'O(n)', color: 'text-indigo-400', note: 'SA and LCP arrays each of size n' },
      ],
    },
    realWorld: [
      { title: 'Genome Sequencing', desc: 'Suffix arrays index the human genome (~3 billion chars) for fast read alignment in tools like BWA and Bowtie.' },
      { title: 'Full-Text Search', desc: 'Search engines pre-build suffix arrays/trees for fast substring search in large document corpora.' },
      { title: 'Data Compression', desc: 'Burrows-Wheeler Transform (BWT, used in bzip2) is computed efficiently via suffix arrays.' },
      { title: 'Plagiarism Detection', desc: 'Finding longest common substrings between documents uses LCP arrays built from their concatenation.' },
    ],
    quiz: [
      { q: 'What does a suffix array contain?', options: ['All substrings sorted', 'Starting indices of all suffixes in lexicographic order', 'Character frequencies', 'Prefix sums of the string'], correct: 1, explanation: 'SA[i] gives the starting position in the original string of the i-th lexicographically smallest suffix.' },
      { q: 'How do you search for a pattern using a suffix array?', options: ['Linear scan of SA', 'Binary search on the suffix array', 'Hash the pattern', 'DFS on suffix tree'], correct: 1, explanation: 'All occurrences of a pattern form a contiguous range in the suffix array. Binary search finds this range in O(m log n).' },
      { q: 'What does the LCP array store?', options: ['Character counts', 'Longest common prefix between adjacent sorted suffixes', 'Pattern match positions', 'Suffix lengths'], correct: 1, explanation: 'LCP[i] = length of longest common prefix between SA[i-1]-th and SA[i]-th suffixes. Enables efficient repeated substring finding.' },
      { q: 'What is the time complexity of the naive suffix array construction by sorting all suffixes?', options: ['O(n)', 'O(n log n)', 'O(n² log n)', 'O(n²)'], correct: 2, explanation: 'Sorting n suffixes with a comparator that compares strings of length up to n costs O(n) per comparison and O(n log n) comparisons, giving O(n² log n) total.' },
      { q: 'What is the Burrows-Wheeler Transform (BWT) and how does it use suffix arrays?', options: ['A lossy image format that discards pixel data', 'A reversible text permutation that groups similar characters, computable in O(n) via the suffix array', 'A hash function for strings', 'A type of binary search tree'], correct: 1, explanation: 'BWT(S) = the last character of each rotation of S sorted lexicographically. The suffix array gives sorted rotations in O(n) space, enabling BWT computation — the core of bzip2 compression.' },
      { q: 'How do you find the longest repeated substring of a string using the suffix array and LCP array?', options: ['Binary search the suffix array', 'Find the maximum value in the LCP array — it is the length of the longest repeated substring', 'Count character frequencies', 'Run DFS on the suffix trie'], correct: 1, explanation: 'The maximum LCP value corresponds to two adjacent suffixes in sorted order that share the longest common prefix — which is the longest substring appearing at least twice in the string.' },
    ],
  },

};
