import type { LessonData } from '../../lessons/GenericLesson';

export const patternsLessons: Record<string, LessonData> = {
  'bit-manipulation': {
    concept: {
      overview: `Integers are just bits — sequences of 0s and 1s in the CPU's registers. Bit manipulation uses the CPU's native bitwise operations (AND, OR, XOR, shifts) to perform operations on individual bits, often solving problems that seem hard in decimal but trivial in binary.

Bitwise operations are single CPU instructions — the fastest possible operations. They power: checking if a number is a power of 2 (one instruction), swapping two integers without a temp variable (three instructions), counting "1" bits (a loop or a single hardware instruction), and detecting the single unique number in an array of duplicates (XOR in one pass).

The essential operations: AND (&) — bits that are 1 in BOTH operands. OR (|) — bits that are 1 in EITHER. XOR (^) — bits that differ (0^anything = anything; x^x = 0). NOT (~) — flip all bits. Left shift (<<) — multiply by 2^k. Right shift (>>) — divide by 2^k (integer).

Once you see bit patterns, you'll recognize them everywhere: permission systems (Unix file permissions are 3 bits each: rwx), bloom filters, chess engines (represent the board as 12 64-bit integers), and graphics (RGBA colors packed into a 32-bit int).`,
      keyPoints: [
        {
          title: 'The Six Bitwise Operations',
          desc: 'AND, OR, XOR, NOT, left shift, right shift. Each is a single CPU instruction. Combined, they solve problems that seem to require loops or conditionals.',
          code: `a = 0b1010   # 10 in decimal
b = 0b1100   # 12 in decimal

print(a & b)   # 0b1000 = 8   (AND: both bits must be 1)
print(a | b)   # 0b1110 = 14  (OR: either bit can be 1)
print(a ^ b)   # 0b0110 = 6   (XOR: bits must differ)
print(~a)      # -11           (NOT: flip all bits)
print(a << 1)  # 0b10100 = 20 (left shift = ×2)
print(a >> 1)  # 0b0101 = 5   (right shift = ÷2)`,
        },
        {
          title: 'XOR Magic',
          desc: 'XOR has special properties: x^x=0, x^0=x, and it\'s commutative+associative. So XOR-ing all numbers in an array where every number appears twice (except one) leaves only the unique number.',
          code: `def find_unique(nums):
    result = 0
    for n in nums:
        result ^= n    # x^x=0, so duplicates cancel
    return result      # only the unique number remains

print(find_unique([2, 3, 2, 4, 4]))  # → 3
# XOR all: 2^3^2^4^4 = (2^2)^(4^4)^3 = 0^0^3 = 3`,
        },
        {
          title: 'Power of Two Check',
          desc: 'A power of 2 in binary has exactly one "1" bit: 4=100, 8=1000, 16=10000. n & (n-1) clears the lowest set bit. If the result is 0, n had only one set bit → power of 2.',
          code: `def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0

# 8 in binary:   1000
# 7 in binary:   0111
# 8 & 7       =  0000 → True (is power of 2)
# 6 in binary:   0110
# 5 in binary:   0101
# 6 & 5       =  0100 ≠ 0 → False (not power of 2)`,
        },
      ],
    },
    steps: [
      { n: '1', label: 'Think in Binary', desc: 'Convert the problem to binary. What does each bit represent? What operation sets, clears, or checks a specific bit?' },
      { n: '2', label: 'Learn the Idioms', desc: 'Set bit k: n |= (1 << k). Clear bit k: n &= ~(1 << k). Toggle bit k: n ^= (1 << k). Check bit k: (n >> k) & 1.' },
      { n: '3', label: 'Use XOR for Cancellation', desc: 'XOR is the "difference without carry" operation. Use it when you need to find what\'s unique or different. x^x=0 makes duplicates cancel perfectly.' },
      { n: '4', label: 'Use Shifts for Multiplication/Division', desc: 'n << k = n × 2^k. n >> k = n ÷ 2^k (integer). These are faster than multiplication and reveal bit structure.' },
      { n: '5', label: 'Recognize Bit Patterns', desc: 'n & (n-1): clears lowest set bit. n & (-n): isolates lowest set bit. n & 1: checks parity (odd/even). These patterns appear constantly in bit problems.' },
    ],
    codeExamples: [
      {
        label: 'Essential bit manipulation tricks',
        complexity: 'O(1) per operation — single CPU instruction',
        variant: 'default',
        code: `# Count set bits (population count)
def count_bits(n):
    count = 0
    while n:
        count += n & 1       # check lowest bit
        n >>= 1              # shift right
    return count
# Faster: bin(n).count('1') or Python's int.bit_count()

# Number of 1s in binary representations 0..n
def count_bits_dp(n):
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)  # dp[i//2] + lowest bit
    return dp

# Single number (XOR all)
def single_number(nums):
    return 0 if not nums else nums[0] ^ single_number(nums[1:])

# Swap without temp variable
a, b = 5, 3
a ^= b; b ^= a; a ^= b
# a=3, b=5 (but just use a,b = b,a in Python!)`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Any single bit operation', value: 'O(1)', color: 'text-emerald-400', note: 'Single CPU instruction' },
        { case: 'Find unique (XOR all)', value: 'O(n)', color: 'text-emerald-400', note: 'vs O(n) hash map — same big-O, but no memory' },
        { case: 'Count set bits (Brian Kernighan)', value: 'O(k)', color: 'text-emerald-400', note: 'k = number of set bits' },
        { case: 'Power of 2 check', value: 'O(1)', color: 'text-emerald-400', note: 'n & (n-1) == 0' },
      ],
      note: 'Bit tricks often match the big-O of straightforward solutions but win on constants (no memory allocation, single CPU instruction). They shine in inner loops where constant factors matter.',
    },
    realWorld: [
      { title: 'Unix File Permissions', desc: 'chmod 755 = 111 101 101 in binary = rwx r-x r-x. Each permission group is 3 bits. Checking, setting, and clearing permissions is bitwise AND/OR/XOR on a 9-bit number.' },
      { title: 'Chess Engines (Bitboards)', desc: 'Professional chess engines (Stockfish) represent each piece type as a 64-bit integer — one bit per square. Board operations become bitwise shifts and masks, 64 squares analyzed simultaneously in one instruction.' },
    ],
    commonMistakes: [
      { wrong: 'Using & instead of && (bitwise AND vs logical AND)', explain: 'In Python, & is bitwise (operates on each bit). and is logical (treats entire value as bool). 4 & 2 = 0 (false in bool context), but 4 and 2 = 2 (truthy). Always know which one you need.' },
      { wrong: 'Forgetting that ~ flips ALL bits including the sign bit', explain: '~n = -(n+1) in two\'s complement. ~0 = -1, ~7 = -8. When using ~ to create masks, use & with 0xFF...F to limit to the bit width you need.' },
    ],
    videoId: "NLKQEOgBAnw",
    videoTitle: "Algorithms: Bit Manipulation",
    quiz: [
      { q: 'What does the expression n & (n-1) accomplish?', options: ['Checks if n is odd', 'Clears the lowest set bit of n', 'Sets the highest bit of n', 'Doubles n'], correct: 1, explanation: 'n has some lowest set bit at position k. n-1 flips bit k to 0 and sets all bits below k. AND-ing them clears bit k and keeps everything above k. This is Brian Kernighan\'s bit clearing trick.' },
      { q: 'Why does XOR-ing all numbers in an array (where each appears twice except one) leave the unique number?', options: ['XOR adds duplicate values together', 'x^x = 0 for any x, so duplicates cancel out, leaving only the unique value', 'XOR sorts the bits in ascending order', 'XOR is commutative but not associative'], correct: 1, explanation: 'XOR properties: x^x=0 (same values cancel), x^0=x (XOR with 0 is identity), commutative and associative. So a^b^c^b^a = a^a ^ b^b ^ c = 0^0^c = c.' },
      { q: 'What is the result of 5 << 2?', options: ['1', '10', '20', '40'], correct: 2, explanation: '5 in binary is 101. Left-shifting by 2 gives 10100 = 20. Left shift by k is equivalent to multiplying by 2^k: 5 × 2² = 5 × 4 = 20.' },
      { q: 'How do you check if bit k of an integer n is set?', options: ['n % (2^k) == 0', '(n >> k) & 1', 'n & k', 'n | (1 << k)'], correct: 1, explanation: 'Right-shift n by k positions, bringing bit k to the least significant position. AND with 1 to isolate it: (n >> k) & 1 = 1 if bit k is set, 0 otherwise.' },
      { q: 'How do you set bit k of integer n?', options: ['n &= (1 << k)', 'n |= (1 << k)', 'n ^= (1 << k)', 'n -= (1 << k)'], correct: 1, explanation: '1 << k creates a mask with only bit k set. OR-ing with n sets bit k to 1 without affecting other bits. AND would clear other bits; XOR would toggle; subtraction is messy.' },
      { q: 'What real-world system extensively uses bit manipulation for board representation?', options: ['Social networks for friend graphs', 'Chess engines (e.g., Stockfish) using 64-bit "bitboards"', 'DNS for IP address lookup', 'Compilers for type checking'], correct: 1, explanation: 'Chess engines represent each piece type as a 64-bit integer (one bit per square). Move generation, attack detection, and board evaluation become bitwise operations — 64 squares processed simultaneously in one CPU instruction.' },
    ],
  },

  'monotonic-stack': {
    concept: {
      overview: `A monotonic stack is a stack that maintains a sorted order (either always increasing or always decreasing from bottom to top). When an element that would violate the order enters, you pop elements until the order is restored. Each pop directly answers a pending question.

The canonical problem: "for each element in an array, find the next greater element to its right." The brute force is O(n²). The monotonic stack is O(n).

How it works: iterate left to right, maintaining a decreasing stack (largest at bottom). When a new element x comes in: while x is greater than the stack top, pop and record "the next greater element for that popped element is x." Then push x.

The elegance: when you pop an element, you answer its "next greater" question in O(1). Each element is pushed once and popped once → O(n) total.

Once you see this pattern, you'll recognize it in: "largest rectangle in histogram" (classic interview question), "trapping rainwater" (O(n) solution), "stock span problem", and "visible buildings from a height array."`,
      keyPoints: [
        {
          title: 'Decreasing Stack for Next Greater',
          desc: 'Maintain a stack where elements decrease from bottom to top. When a larger element arrives, it triggers pops that answer "next greater element" questions for all smaller elements below it.',
          code: `def next_greater(nums):
    n = len(nums)
    result = [-1] * n
    stack = []   # stores indices, decreasing by value

    for i, num in enumerate(nums):
        while stack and nums[stack[-1]] < num:
            idx = stack.pop()
            result[idx] = num   # num is next greater for idx
        stack.append(i)

    return result
# [2, 1, 2, 4, 3] → [4, 2, 4, -1, -1]`,
        },
        {
          title: 'Increasing Stack for Next Smaller',
          desc: 'Reverse the comparison: maintain an increasing stack. When a smaller element arrives, trigger pops that answer "next smaller element" questions. Used in histogram largest rectangle.',
        },
        {
          title: 'Stock Span Problem',
          desc: 'For each day, find how many consecutive previous days had price ≤ today\'s price. Monotonic stack on prices: when today\'s price triggers a pop, the span extends through the popped element\'s span.',
          code: `def stock_span(prices):
    stack = []  # (price, span) pairs
    spans = []
    for price in prices:
        span = 1
        while stack and stack[-1][0] <= price:
            span += stack.pop()[1]   # extend span
        stack.append((price, span))
        spans.append(span)
    return spans`,
        },
      ],
    },
    steps: [
      { n: '1', label: 'Identify the Question', desc: '"Next greater/smaller", "previous greater/smaller", "span while condition holds" — these all hint at a monotonic stack.' },
      { n: '2', label: 'Choose Stack Direction', desc: 'Next GREATER element → decreasing stack (pop when new element is larger). Next SMALLER element → increasing stack (pop when new element is smaller).' },
      { n: '3', label: 'Iterate and Maintain', desc: 'For each element, maintain the stack invariant: pop violating elements (answering their question), then push the current element.' },
      { n: '4', label: 'Answer on Pop', desc: 'When element i is popped because of element j: j is the "next greater/smaller" for i. Record this answer immediately.' },
      { n: '5', label: 'Handle Remaining Stack', desc: 'After the full array: elements still in the stack have no next greater/smaller element. Set their answer to -1 or 0 accordingly.' },
    ],
    codeExamples: [
      {
        label: 'Largest rectangle in histogram — classic monotonic stack',
        complexity: 'O(n) time, O(n) space',
        variant: 'default',
        code: `def largest_rectangle(heights):
    """Find the largest rectangle that fits under the histogram."""
    stack = []   # increasing stack of indices
    max_area = 0
    heights.append(0)   # sentinel: ensures all bars are popped

    for i, h in enumerate(heights):
        start = i
        while stack and heights[stack[-1]] > h:
            idx = stack.pop()
            width = i - (stack[-1] + 1 if stack else 0)
            max_area = max(max_area, heights[idx] * width)
            start = idx
        stack.append(start)

    return max_area

# [2, 1, 5, 6, 2, 3] → 10
# The rectangle of height 5 with width 2 (bars 2 and 3)`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Next greater element', value: 'O(n)', color: 'text-emerald-400', note: 'vs O(n²) brute force' },
        { case: 'Largest rectangle', value: 'O(n)', color: 'text-emerald-400', note: 'Each bar pushed/popped once' },
        { case: 'Trapping rainwater', value: 'O(n)', color: 'text-emerald-400', note: 'Monotonic stack or two pointers' },
        { case: 'Space', value: 'O(n)', color: 'text-amber-400', note: 'Stack holds at most n elements' },
      ],
      note: 'The key amortized argument: each element is pushed exactly once and popped at most once. Total push+pop operations ≤ 2n, so the while loop total runs at most n times across all outer iterations.',
    },
    realWorld: [
      { title: 'Temperature Forecasting', desc: '"Daily temperatures" is a direct application: given daily temperatures, find how many days until a warmer day. This is exactly next-greater-element, solved in O(n) with a monotonic stack.' },
      { title: 'Browser History Navigation', desc: 'Building a "back/forward" navigation system where each page has a stack of pages you can return to uses monotonic-stack-like principles to maintain the ordered history.' },
    ],
    commonMistakes: [
      { wrong: 'Confusing increasing vs decreasing stack', explain: 'Next GREATER uses a DECREASING stack (small elements at top, large at bottom). When a larger value arrives, smaller values are popped because their "next greater" has been found. It feels backwards at first.' },
      { wrong: 'Forgetting to handle elements remaining in the stack', explain: 'After iterating the full array, elements still in the stack have no next greater/smaller element to their right. Iterate the remaining stack and mark their answers as -1 or use a sentinel value at the end of the array.' },
    ],
    videoId: "DtJVwbbicjQ",
    videoTitle: "Monotonic Stack in 6 Minutes | LeetCode Pattern",
    quiz: [
      { q: 'What does a "monotonic stack" maintain?', options: ['A stack with at most one element', 'A stack where elements are always in sorted order (all increasing or all decreasing)', 'A stack that never grows beyond O(log n) size', 'A stack that can only hold unique values'], correct: 1, explanation: 'A monotonic stack enforces a sorted order invariant. When a new element would violate the order, elements are popped until the invariant is restored.' },
      { q: 'For the "next greater element" problem, which type of stack is used?', options: ['Increasing stack', 'Decreasing stack', 'Random-order stack', 'Min-heap instead of stack'], correct: 1, explanation: 'A decreasing stack (largest at bottom, smallest at top) is used. When a new element is larger than the top, the top is popped and that element\'s "next greater" is answered.' },
      { q: 'What is the time complexity of finding next-greater-element for all n elements using a monotonic stack?', options: ['O(n²)', 'O(n log n)', 'O(n)', 'O(n + max_value)'], correct: 2, explanation: 'Each element is pushed exactly once and popped at most once. Total operations: at most 2n pushes/pops → O(n) regardless of the specific input.' },
      { q: 'In the "largest rectangle in histogram" problem, what does popping an element from the monotonic stack represent?', options: ['The element is a local minimum', 'The current bar is shorter than the popped bar — the popped bar\'s maximum-width rectangle can now be computed', 'The stack has exceeded its size limit', 'The popped element is irrelevant to the answer'], correct: 1, explanation: 'When a shorter bar arrives, it limits how far a taller bar to its left can extend rightward. The pop computes the taller bar\'s largest rectangle (width = current index minus the new stack top).' },
      { q: 'What sentinel trick is commonly used with monotonic stacks to simplify the code?', options: ['Prepend the maximum value to the array', 'Append a 0 (or very small value) to the array to flush remaining stack elements', 'Use a null pointer as the bottom of the stack', 'Initialize the stack with all indices'], correct: 1, explanation: 'Appending 0 (or -infinity) to the end of the array ensures every element in the stack is eventually popped and answered. Without this sentinel, you need a separate cleanup loop for remaining stack elements.' },
      { q: 'Which of these problems is NOT naturally solved with a monotonic stack?', options: ['Next greater element', 'Trapping rainwater', 'Stock span problem', 'Finding the median of a stream'], correct: 3, explanation: 'Finding the median of a stream requires two heaps (a max-heap and min-heap), not a monotonic stack. The others all use monotonic stacks: next-greater, rainwater (height tracking), and stock span (consecutive non-decreasing days).' },
    ],
  },

  'interval-scheduling': {
    concept: {
      overview: `Intervals are ubiquitous: meeting time slots, video clip segments, chromosomal regions in genomics, CPU burst times, hotel bookings. Interval problems ask: merge overlapping regions, find free slots, count conflicts, schedule as many as possible.

The core operation: sort intervals by start time (or end time, depending on the problem). Once sorted, a single scan resolves most interval problems in O(n).

Merging overlapping intervals: sort by start. Maintain the "current interval." For each new interval: if it overlaps (new start ≤ current end), extend (update current end to max of both ends). If no overlap, output current and start fresh.

Meeting rooms required: this is an interval scheduling problem asking for the maximum number of simultaneously active intervals. Use a min-heap of end times: for each new meeting, if the heap's minimum end ≤ new start, reuse that room (pop and update). Otherwise, allocate a new room (push). The heap size at any point is the number of active meetings.

The key insight connecting all interval problems: sorting by start time converts an O(n²) scan-all-pairs problem into a single O(n) sweep.`,
      keyPoints: [
        {
          title: 'Merge Overlapping Intervals',
          desc: 'Sort by start time. Scan linearly: if new interval overlaps with last merged, extend it. Otherwise, start a new merged interval.',
          code: `def merge_intervals(intervals):
    if not intervals: return []
    intervals.sort()
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:      # overlaps
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end]) # no overlap
    return merged

# [[1,3],[2,6],[8,10],[15,18]] → [[1,6],[8,10],[15,18]]`,
        },
        {
          title: 'Minimum Meeting Rooms',
          desc: 'Count the maximum overlap at any point in time. Use a min-heap of end times: for each meeting, reuse a room that ended before the meeting starts (min-heap gives the earliest-ending room).',
          code: `import heapq

def min_meeting_rooms(intervals):
    intervals.sort()
    rooms = []   # min-heap of end times
    for start, end in intervals:
        if rooms and rooms[0] <= start:
            heapq.heapreplace(rooms, end)  # reuse room
        else:
            heapq.heappush(rooms, end)     # new room
    return len(rooms)`,
        },
        {
          title: 'Check if Person Can Attend All Meetings',
          desc: 'Sort by start time. If any two consecutive intervals overlap (intervals[i][0] < intervals[i-1][1]), the person can\'t attend both. O(n log n).',
        },
      ],
    },
    steps: [
      { n: '1', label: 'Sort by Start Time', desc: 'Almost every interval problem begins by sorting by start time. This converts a 2D intersection problem into a 1D sequential scan.' },
      { n: '2', label: 'Define "Overlap"', desc: 'Two intervals [a,b] and [c,d] overlap if a ≤ d AND c ≤ b. Equivalently: they do NOT overlap only if b < c or d < a (one ends before the other starts).' },
      { n: '3', label: 'Sweep Left to Right', desc: 'After sorting, scan the intervals from left to right. Maintain state about the "current active interval" or "currently allocated rooms."' },
      { n: '4', label: 'Use a Heap for Room Count', desc: 'When counting required rooms (maximum overlap), a min-heap of end times lets you efficiently find and reuse the room that ended earliest.' },
      { n: '5', label: 'Handle Edge Cases', desc: 'Check: what if two meetings start at exactly the same time? What if a meeting starts exactly when another ends (do they conflict)? Clarify whether endpoints are inclusive or exclusive.' },
    ],
    codeExamples: [
      {
        label: 'Insert interval into sorted non-overlapping list',
        complexity: 'O(n)',
        variant: 'default',
        code: `def insert(intervals, new_interval):
    result = []
    i = 0
    n = len(intervals)

    # Add all intervals ending before new_interval starts
    while i < n and intervals[i][1] < new_interval[0]:
        result.append(intervals[i])
        i += 1

    # Merge all overlapping intervals with new_interval
    while i < n and intervals[i][0] <= new_interval[1]:
        new_interval[0] = min(new_interval[0], intervals[i][0])
        new_interval[1] = max(new_interval[1], intervals[i][1])
        i += 1
    result.append(new_interval)

    # Add remaining non-overlapping intervals
    while i < n:
        result.append(intervals[i])
        i += 1

    return result`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Sort intervals', value: 'O(n log n)', color: 'text-amber-400', note: 'Always the first step' },
        { case: 'Merge overlapping', value: 'O(n)', color: 'text-emerald-400', note: 'After sorting, single scan' },
        { case: 'Min meeting rooms', value: 'O(n log n)', color: 'text-amber-400', note: 'Sort + heap operations' },
        { case: 'Check conflicts', value: 'O(n log n)', color: 'text-amber-400', note: 'Sort + O(n) scan' },
      ],
      note: 'The "sort by start time then sweep" pattern converts O(n²) pairwise comparisons to O(n log n) dominated by sorting, with O(n) work in the scan phase.',
    },
    realWorld: [
      { title: 'Google Calendar', desc: 'Finding free time slots between meetings, detecting double-bookings, and suggesting meeting times that work for all attendees are all interval problems solved with sorted-sweep algorithms.' },
      { title: 'Video Editing Software', desc: 'Merging clips, detecting overlapping track segments, and computing the total coverage of a timeline are all interval merging problems.' },
    ],
    commonMistakes: [
      { wrong: 'Forgetting to sort before sweeping', explain: 'Without sorting, you need to check every interval against every other (O(n²)). Sorting by start time enables the linear sweep by guaranteeing that overlapping intervals appear consecutively.' },
      { wrong: 'Off-by-one with inclusive vs exclusive endpoints', explain: 'Be clear: [1,3] and [3,5] — do they overlap? If endpoints are inclusive, yes (they share point 3). If [1,3) is half-open, no. This distinction affects the overlap check condition.' },
    ],
    videoId: "hG9QDwiE28w",
    videoTitle: "Merge Interval Algorithm In 4 Minutes",
    quiz: [
      { q: 'What is the first step in solving most interval problems?', options: ['Build a graph of interval relationships', 'Sort intervals by their start time', 'Count the total span of all intervals', 'Apply binary search for overlap detection'], correct: 1, explanation: 'Sorting by start time is the foundational step. It ensures overlapping intervals are adjacent in the sorted list, enabling a single O(n) scan instead of O(n²) pairwise comparisons.' },
      { q: 'When do two intervals [a,b] and [c,d] overlap (assuming inclusive endpoints)?', options: ['Only when a == c', 'When a ≤ d AND c ≤ b', 'When |a-c| < |b-d|', 'When b - a == d - c'], correct: 1, explanation: 'Two intervals overlap when neither ends before the other starts. They do NOT overlap only if b < c or d < a. The overlap condition is: start of one ≤ end of the other (both directions).' },
      { q: 'In the "minimum meeting rooms" problem, what does each element in the min-heap represent?', options: ['The start time of the next meeting', 'The end time of a meeting in progress — representing when a room becomes available', 'The number of attendees in each room', 'The duration of the longest meeting'], correct: 1, explanation: 'The min-heap stores the end times of all currently active meetings. The minimum element is the room that becomes free earliest. When a new meeting starts after this minimum, we can reuse that room.' },
      { q: 'How do you merge [1,4] and [3,6] that overlap?', options: ['[1,4], [3,6] — keep both, they partially overlap', '[3,4] — only the overlapping portion', '[1,6] — extend to cover both fully', '[1,3], [4,6] — split at the overlap'], correct: 2, explanation: 'When merging overlapping intervals, take the minimum start and maximum end: min(1,3)=1 and max(4,6)=6, giving [1,6]. This single interval represents the full coverage of both.' },
      { q: 'What is the time complexity of merging n intervals?', options: ['O(n)', 'O(n log n)', 'O(n²)', 'O(n log² n)'], correct: 1, explanation: 'Sorting takes O(n log n). The merge scan takes O(n) — linear pass through the sorted intervals. The dominating term is O(n log n) from sorting.' },
      { q: 'The problem "given n intervals, find the maximum number of simultaneously active intervals" is equivalent to?', options: ['Merging all intervals', 'Finding the minimum number of rooms needed for all meetings', 'Finding the interval with the maximum duration', 'Computing the total coverage length'], correct: 1, explanation: 'The maximum number of simultaneously active intervals equals the minimum number of meeting rooms needed — both measure the peak overlap count at any moment in time.' },
    ],
  },

  'recursion-to-iteration': {
    concept: {
      overview: `Every recursive function has an equivalent iterative version. Why does this matter? Because recursion uses the call stack — and the call stack is limited (typically 1K–8K frames). For deep trees or large arrays, recursive DFS will crash with a stack overflow.

The conversion is systematic: replace the implicit call stack with an explicit stack (a list or deque you manage). Instead of "call the function on this input," push the input onto your stack. Instead of "return from the function," pop from the stack and process.

This reveals something profound: recursion and iteration are the same computation, just expressed differently. Recursion delegates memory management to the OS call stack; iteration manages memory explicitly.

Understanding this conversion also helps you reason about tail recursion optimization: if the recursive call is the very last operation (a "tail call"), the language can reuse the current stack frame instead of creating a new one. Python doesn't do this (Python rarely optimizes tail calls), but functional languages like Haskell and Scheme do.

Mastering this conversion gives you control: you can tune stack behavior, handle arbitrarily deep inputs without crashes, and implement algorithms iteratively when the language's recursion limit would be hit.`,
      keyPoints: [
        {
          title: 'The Direct Conversion Template',
          desc: 'Every recursive function becomes: initialize explicit stack with the initial input, loop while stack is non-empty, pop current state, do the work, push sub-problems.',
          code: `# Recursive DFS
def dfs_recursive(node):
    if not node: return
    process(node)
    dfs_recursive(node.left)
    dfs_recursive(node.right)

# Iterative DFS — explicit stack
def dfs_iterative(root):
    if not root: return
    stack = [root]
    while stack:
        node = stack.pop()
        process(node)
        # Push right first so left is processed first (LIFO)
        if node.right: stack.append(node.right)
        if node.left: stack.append(node.left)`,
        },
        {
          title: 'Handling Return Values',
          desc: 'Recursive functions return values up the call chain. Iteratively, you must track state explicitly — often with an additional result variable or by pushing (node, state) pairs onto the stack.',
          code: `# Tree sum: recursive
def sum_tree(node):
    if not node: return 0
    return node.val + sum_tree(node.left) + sum_tree(node.right)

# Tree sum: iterative
def sum_tree_iter(root):
    total = 0
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        total += node.val
        if node.left: stack.append(node.left)
        if node.right: stack.append(node.right)
    return total`,
        },
        {
          title: 'When Ordering Matters',
          desc: 'Inorder traversal (left → root → right) requires knowing when you\'re returning from the left subtree. This requires tracking "phase" on the stack — push (node, visited) tuples.',
        },
      ],
    },
    steps: [
      { n: '1', label: 'Identify What Goes on the Call Stack', desc: 'In the recursive version, each call has: the node/value being processed, any local variables, and the return address. These become your stack elements.' },
      { n: '2', label: 'Replace Recursive Call with Stack Push', desc: 'Wherever the recursive function calls itself: push the sub-problem inputs onto the explicit stack instead.' },
      { n: '3', label: 'Replace Base Case with Loop Termination', desc: 'The recursive base case (return when null/empty) becomes the loop condition: the loop runs while the stack is non-empty.' },
      { n: '4', label: 'Handle Pre/Post-Order Processing', desc: 'Pre-order (process before recursing) is easy. Post-order (process after all recursive calls) requires tracking which children have been processed — push phase info.' },
      { n: '5', label: 'Verify Order with Examples', desc: 'Trace the iterative version on a 3-node tree. Compare output with the recursive version. Order of pushes matters (push right before left for left-first traversal in LIFO).' },
    ],
    codeExamples: [
      {
        label: 'Inorder traversal — tricky iterative conversion',
        complexity: 'O(n) time, O(h) space',
        variant: 'default',
        code: `def inorder_recursive(root):
    if not root: return []
    return inorder_recursive(root.left) + [root.val] + inorder_recursive(root.right)

def inorder_iterative(root):
    """Inorder (left→root→right) without recursion."""
    result = []
    stack = []
    curr = root

    while curr or stack:
        # Go as far left as possible
        while curr:
            stack.append(curr)
            curr = curr.left

        # Process the node (leftmost unprocessed)
        curr = stack.pop()
        result.append(curr.val)

        # Now go right
        curr = curr.right

    return result`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Time complexity', value: 'Same as recursive', color: 'text-emerald-400', note: 'Same work, different control flow' },
        { case: 'Space (iterative)', value: 'O(h)', color: 'text-emerald-400', note: 'h = max stack depth = tree height' },
        { case: 'Space (recursive)', value: 'O(h)', color: 'text-emerald-400', note: 'Call stack frames, OS-managed' },
        { case: 'Stack depth limit (Python recursion)', value: '~1000 default', color: 'text-red-400', note: 'Iterative avoids this limit' },
      ],
      note: 'The iterative version uses the same O(h) space, but from the heap (your explicit stack) rather than the call stack. This removes the OS recursion limit and allows arbitrarily deep traversals.',
    },
    realWorld: [
      { title: 'Compiler/Interpreter Implementation', desc: 'Compilers implement recursive descent parsers iteratively with explicit stacks to avoid stack overflow on deeply nested code (thousands of parentheses deep). The JVM bytecode interpreter is a stack machine.' },
      { title: 'Game Tree Search (Alpha-Beta Pruning)', desc: 'Game tree search (chess, Go) must search millions of nodes. Iterative deepening DFS with an explicit stack avoids call stack limits and enables finer memory control.' },
    ],
    commonMistakes: [
      { wrong: 'Pushing left before right for pre-order traversal', right: 'Push right first, then left', explain: 'Stacks are LIFO. To process left before right, you must push right first (so it\'s processed last). If you push left first, right is processed first — giving reverse pre-order.' },
      { wrong: 'Assuming iterative is always faster than recursive', explain: 'The algorithmic complexity is identical. Iterative may be slightly faster in practice (avoiding function call overhead), but the difference is usually negligible. The real advantage is avoiding stack overflow, not raw speed.' },
    ],
    videoId: "1rWjjO-rZk0",
    videoTitle: "Recursion vs Iteration: Explained Simply for Beginners",
    quiz: [
      { q: 'What data structure makes recursive algorithms equivalent to iterative ones?', options: ['Queue (FIFO)', 'Hash map', 'Explicit stack (LIFO)', 'Priority heap'], correct: 2, explanation: 'The call stack is a LIFO (Last In First Out) structure. Replacing it with an explicit LIFO stack (list/deque with push/pop) gives an equivalent iterative algorithm.' },
      { q: 'Why might you prefer an iterative DFS over recursive DFS for very deep trees?', options: ['Iterative DFS has better time complexity', 'Recursive DFS can cause a stack overflow when the tree depth exceeds the OS call stack limit', 'Recursive DFS doesn\'t visit all nodes', 'Iterative DFS uses less total memory'], correct: 1, explanation: 'Python\'s recursion limit defaults to ~1000 frames. For a tree with depth 10,000, recursive DFS hits this limit and crashes. Iterative DFS uses a heap-allocated stack with no such limitation.' },
      { q: 'In iterative pre-order traversal (root→left→right), why must you push right before left?', options: ['The stack processes right before left by default', 'Stacks are LIFO: push right first so left (pushed second) is popped and processed first', 'Right subtrees are always smaller', 'It doesn\'t matter — both orderings work'], correct: 1, explanation: 'With LIFO ordering, the last element pushed is processed first. To process left before right, push right first (processed later) then push left (processed immediately). Reverse the push order of the processing order.' },
      { q: 'What is "tail recursion" and why do some languages optimize it?', options: ['A recursive call in a loop', 'When the recursive call is the very last operation — the current frame can be reused instead of stacked', 'Recursion that calls two functions', 'A recursive call with no arguments'], correct: 1, explanation: 'A tail call is a function call that is the very last thing a function does. Since the caller\'s frame is no longer needed, the language can reuse it instead of creating a new frame, making tail-recursive functions use O(1) stack space.' },
      { q: 'In iterative inorder traversal, what must you track to know when to process a node (between left and right subtrees)?', options: ['The depth of each node', 'The current traversal phase — go left until null, then process, then go right', 'The total number of nodes visited', 'Whether the node has been marked as visited'], correct: 1, explanation: 'Inorder requires: go as far left as possible, then process, then go right. The iterative version tracks a "current" pointer that descends left; when null, pops from the stack (processes), then moves right.' },
      { q: 'What is the space complexity of iterative DFS on a balanced binary tree of n nodes?', options: ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'], correct: 1, explanation: 'For a balanced tree of height h = O(log n), the explicit stack holds at most h+1 elements at any time (one per level). So space is O(log n). For a completely skewed tree (worst case), height = O(n) and stack is O(n).' },
    ],
  },

  'amortized-analysis': {
    concept: {
      overview: `Dynamic arrays (Python list, Java ArrayList, C++ vector) have a seemingly paradoxical property: they occasionally take O(n) time for a single append, yet we say the average append is O(1). How can a slow operation be fast "on average"?

Amortized analysis answers this. Instead of analyzing the worst case of a single operation, it analyzes the total cost of a sequence of operations, then divides by the number of operations. If n operations cost O(n) total, each costs O(1) amortized.

The dynamic array story: when the array is full, it doubles in size — copying all elements (O(n) cost). But doubling means the next n operations won't trigger a resize. So we "pay back" the O(n) copy cost over the next n operations: O(1) each.

More formally: start with capacity 1. Capacity doubles at sizes 1, 2, 4, 8, ..., n. Total copies: 1+2+4+...+n ≈ 2n. So n insertions cost 2n total copies → O(1) amortized per insertion.

This thinking pattern unlocks understanding of hash table resizing, union-find path compression, and splay trees — all structures where individual operations can be expensive but sequences are provably efficient.`,
      keyPoints: [
        {
          title: 'The Doubling Strategy',
          desc: 'When the array is full, allocate 2× capacity and copy all elements. Cost = O(n). But the next n inserts are O(1) each, so the O(n) cost is amortized over n operations → O(1) per insert.',
          code: `class DynamicArray:
    def __init__(self):
        self._data = [None]   # capacity 1
        self._size = 0

    def append(self, val):
        if self._size == len(self._data):
            # RESIZE: O(n) but happens rarely
            new_data = [None] * (2 * len(self._data))
            for i in range(self._size):
                new_data[i] = self._data[i]
            self._data = new_data
        self._data[self._size] = val   # O(1)
        self._size += 1`,
        },
        {
          title: 'Counting Total Cost',
          desc: 'Total copies for n appends: 1+2+4+8+...+n (doubling points) < 2n. So n appends do at most 2n total work → O(1) amortized each.',
        },
        {
          title: 'The Banker\'s Method',
          desc: 'Each cheap operation "saves" some credit. When an expensive operation occurs, it spends those saved credits. If each operation\'s credit charge is O(1), the amortized cost is O(1).',
        },
      ],
    },
    steps: [
      { n: '1', label: 'Identify the Expensive Operation', desc: 'What is the single worst-case operation? For dynamic arrays: the resize/copy. For hash tables: rehashing. For union-find: the very first path compression.' },
      { n: '2', label: 'Count How Often It Occurs', desc: 'How many times does the expensive operation occur in n total operations? For dynamic arrays: O(log n) times (at capacities 1, 2, 4, ..., n). Each costs O(current size).' },
      { n: '3', label: 'Sum the Total Costs', desc: 'Add up the costs of all expensive operations. For dynamic array: 1+2+4+...+n ≈ 2n. For n total inserts: 2n total work → O(1) amortized per insert.' },
      { n: '4', label: 'Divide by Number of Operations', desc: 'Total cost / n operations = amortized cost per operation. O(2n) / n = O(1). This is the amortized cost guarantee.' },
      { n: '5', label: 'Verify the Growth Strategy Matters', desc: 'Why doubling and not +1 each time? Adding +1 capacity each time: resizes at 1, 2, 3, ..., n → total copies = 1+2+3+...+n = O(n²). That\'s O(n) amortized per insert — much worse!' },
    ],
    codeExamples: [
      {
        label: 'Dynamic array vs fixed +1 growth — why doubling matters',
        complexity: 'O(1) amortized with doubling; O(n) with +1',
        variant: 'default',
        code: `def benchmark_growth_strategies(n):
    """Compare total copies for n appends."""

    # Strategy 1: Double capacity when full
    size, cap, copies_double = 0, 1, 0
    for _ in range(n):
        if size == cap:
            copies_double += size  # copy all elements
            cap *= 2               # double capacity
        size += 1
    # Total copies ≈ 2n → O(1) amortized per append

    # Strategy 2: Add 1 to capacity when full
    size, cap, copies_linear = 0, 1, 0
    for _ in range(n):
        if size == cap:
            copies_linear += size  # copy all elements
            cap += 1               # add just 1
        size += 1
    # Total copies = 1+2+3+...+n = n(n+1)/2 ≈ n²/2 → O(n) amortized!

    print(f"Doubling: {copies_double} copies for {n} appends")
    print(f"Linear:   {copies_linear} copies for {n} appends")

# n=1000: Doubling: ~1996 copies; Linear: ~499500 copies`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Single worst-case append (resize)', value: 'O(n)', color: 'text-red-400', note: 'Copying all elements' },
        { case: 'Append (amortized)', value: 'O(1)', color: 'text-emerald-400', note: 'Total 2n copies across n appends' },
        { case: 'Hash table insert (amortized)', value: 'O(1)', color: 'text-emerald-400', note: 'Rehashing amortized over inserts' },
        { case: 'Union-Find find (amortized)', value: 'O(α(n)) ≈ O(1)', color: 'text-emerald-400', note: 'Path compression amortizes O(log n)' },
      ],
      note: 'Amortized O(1) doesn\'t mean every operation is O(1). It means: averaged over a long sequence of operations, each is O(1). Individual operations can still be O(n) — just rarely.',
    },
    realWorld: [
      { title: 'Python list.append()', desc: 'Python\'s list uses the doubling strategy. Checking CPython source: it grows by ~12.5% after small sizes, which still gives O(1) amortized. You can verify with sys.getsizeof() to see capacity jumps.' },
      { title: 'Hash Table Load Factor', desc: 'Python dicts and Java HashMaps resize when the load factor exceeds 0.75. The resize cost is O(n) but happens O(log n) times, giving O(1) amortized insert across all insertions.' },
    ],
    commonMistakes: [
      { wrong: 'Thinking amortized O(1) means every operation is O(1)', explain: 'Amortized O(1) means the average over a sequence is O(1). Individual operations can be O(n). For latency-sensitive systems (real-time, game engines), worst-case O(n) spikes matter — consider pre-allocated fixed-size structures instead.' },
      { wrong: 'Using +1 growth instead of doubling in a custom dynamic array', explain: 'Adding 1 element per resize causes O(n²) total copies for n inserts — catastrophically slow. Always use multiplicative growth (doubling or 1.5×) to ensure amortized O(1).' },
    ],
    videoId: "Gep3j6JYfSk",
    videoTitle: "Amortized Time Complexity Explained - Algorithm Analysis for Beginners",
    quiz: [
      { q: 'What does "O(1) amortized" mean for a dynamic array\'s append operation?', options: ['Every single append completes in exactly 1 step', 'The worst-case append is O(1)', 'Averaged over n appends, each append costs O(1) total work', 'Amortized is a stricter guarantee than worst-case O(1)'], correct: 2, explanation: 'Amortized O(1) means: if you perform n append operations, the total cost is O(n). Individual appends can be O(n) (when resizing occurs), but these are rare enough that the average per-operation cost is O(1).' },
      { q: 'A dynamic array doubles capacity (from size n to 2n) when full. What is the total number of element copies for n consecutive appends?', options: ['O(n²)', 'O(n log n)', 'O(n)', 'O(1)'], correct: 2, explanation: 'Copies at each doubling: 1+2+4+8+...+n/2 (geometric series) ≈ n. Total copies ≤ 2n = O(n). Dividing by n appends: O(1) amortized per append.' },
      { q: 'Why is "add exactly 1 to capacity on resize" catastrophically worse than doubling?', options: ['It causes incorrect answers', 'It results in O(n²) total copies for n appends — O(n) amortized per append', 'Memory allocation fails with +1 growth', 'It doesn\'t support deletion'], correct: 1, explanation: 'With +1 growth, resizes occur n times with costs 1, 2, 3, ..., n-1. Total copies = n(n-1)/2 = O(n²). This means O(n) amortized per append — linear cost for each addition.' },
      { q: 'What is the "banker\'s method" for amortized analysis?', options: ['Borrow memory from the OS', 'Assign each cheap operation extra "credit"; expensive operations spend saved credit to show total cost stays bounded', 'Bank the operation results for future use', 'Pre-compute all operations to determine their cost'], correct: 1, explanation: 'The banker\'s method assigns each operation an "amortized cost." Cheap operations (append to non-full array: 1 element + 1 extra credit saved) fund expensive operations (resize: spends n saved credits) so total amortized cost = actual total cost.' },
      { q: 'Union-Find with path compression achieves O(α(n)) amortized per operation. What does α represent?', options: ['The number of connected components', 'The inverse Ackermann function — grows slower than log(log(log(n))), effectively constant', 'The depth of the deepest tree', 'The total number of union operations'], correct: 1, explanation: 'α(n) is the inverse Ackermann function — it grows slower than log*, which grows slower than log(log(log(n))). For all practical values of n (even 2^65536), α(n) ≤ 5. It is effectively constant.' },
      { q: 'In a latency-sensitive real-time system (e.g., a game running at 60fps), why might amortized O(1) dynamic array appends be problematic?', options: ['They use too much memory', 'The occasional O(n) resize spike could cause a frame drop or missed deadline', 'Amortized analysis doesn\'t apply to real-time systems', 'Dynamic arrays are too slow for games'], correct: 1, explanation: 'Real-time systems care about worst-case, not amortized. A resize spike that takes O(n) time (e.g., 16ms) could miss a 16.67ms frame deadline. Pre-allocate fixed capacity or use a ring buffer for bounded worst-case latency.' },
    ],
  },

  'cache-and-locality': {
    concept: {
      overview: `Modern CPUs run at 4+ GHz, but RAM accesses can take 100+ nanoseconds — 400+ CPU cycles wasted waiting. To bridge this gap, CPUs have a hierarchy of caches: L1 (few KB, ~1 cycle), L2 (few MB, ~10 cycles), L3 (tens of MB, ~40 cycles), RAM (~100 cycles).

The key mechanism: when you read any memory address, the CPU loads not just that one byte but an entire "cache line" — typically 64 bytes of contiguous memory. So reading arr[0] automatically loads arr[0] through arr[15] (for 4-byte integers) into L1 cache. Then arr[1] through arr[15] are essentially free.

Sequential access patterns (arrays, vectors) are cache-friendly: each cache miss loads 16 consecutive elements, most of which are used immediately. Random access patterns (linked lists, trees with pointer chasing) cause a cache miss for nearly every element — each pointer dereference jumps to a random memory location, guaranteeing a cache miss.

This is why a sequential array scan of 100M elements can be faster than traversing a linked list of the same data — even though both are O(n). The constant factor difference is 100x or more.

Understanding cache behavior explains why: row-major matrix access beats column-major, arrays outperform linked lists for traversal, and high-frequency trading systems lay out data structures for cache alignment.`,
      keyPoints: [
        {
          title: 'Cache Lines and Spatial Locality',
          desc: 'A cache line is typically 64 bytes. Reading any byte loads the entire line. Arrays are contiguous in memory — accessing arr[i] prefetches arr[i+1]...arr[i+15]. Each cache line miss amortizes over 16 reads.',
          code: `# Cache-FRIENDLY: sequential array access
def sum_array(arr):
    total = 0
    for x in arr:     # arr[0], arr[1], arr[2] ... sequential
        total += x    # each cache miss loads 16 ints → 16 hits
    return total

# Cache-UNFRIENDLY: linked list traversal
def sum_linked(head):
    total = 0
    node = head
    while node:
        total += node.val
        node = node.next  # random memory jump → cache miss every time
    return total`,
        },
        {
          title: 'Matrix Row-Major vs Column-Major Access',
          desc: '2D arrays are stored row by row in memory. Accessing matrix[i][j] and matrix[i][j+1] are contiguous. Accessing matrix[i][j] and matrix[i+1][j] jumps an entire row in memory → cache miss per access.',
          code: `# Row-major access (C, Python): FAST — sequential in memory
def row_major_sum(matrix):
    total = 0
    for row in matrix:
        for val in row:    # consecutive memory locations
            total += val
    return total

# Column-major access: SLOW — jumps by row_length each step
def col_major_sum(matrix):
    total = 0
    for j in range(len(matrix[0])):
        for i in range(len(matrix)):   # jumps every row_size bytes
            total += matrix[i][j]
    return total`,
        },
        {
          title: 'Temporal Locality',
          desc: 'Recently used memory is likely to be used again soon. Keeping "hot data" in tight loops ensures it stays in L1/L2 cache. Large working sets that don\'t fit in cache cause "cache thrashing."',
        },
      ],
    },
    steps: [
      { n: '1', label: 'Understand What Cache Holds', desc: 'L1: last ~4K data elements you accessed. L2: last ~250K. If your algorithm works on data that fits in L1, it runs at ~4 cycles per operation. If it spills to RAM: ~100 cycles.' },
      { n: '2', label: 'Prefer Arrays Over Linked Structures for Traversal', desc: 'Array elements are contiguous. Linked list nodes are scattered. For sequential traversal of n elements: array touches n/16 cache lines; linked list touches n cache lines.' },
      { n: '3', label: 'Traverse Matrices Row by Row', desc: 'In C, Java, Python, and most languages, 2D arrays are row-major. Always access row[i][0], row[i][1], ... before moving to row[i+1][0]. Column-first access causes n×(n/16) extra cache misses.' },
      { n: '4', label: 'Keep Hot Data Compact', desc: 'Store frequently accessed fields together (Structure of Arrays vs Array of Structures). In a game engine, keeping all X-coordinates in one array (not in separate Player structs) enables SIMD and cache efficiency.' },
      { n: '5', label: 'Profile Before Optimizing', desc: 'Cache behavior is hardware-specific. Use cache profiling tools (cachegrind, perf) to measure actual cache misses. Never assume — measure, then optimize the measured bottleneck.' },
    ],
    codeExamples: [
      {
        label: 'Matrix multiplication: cache-naive vs cache-aware',
        complexity: 'O(n³) both; cache-aware is 5-10x faster in practice',
        variant: 'default',
        code: `def matmul_naive(A, B):
    """Standard i,j,k order — B is accessed column-by-column → cache hostile"""
    n = len(A)
    C = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]  # B[k][j] — column access!
    return C

def matmul_cache_friendly(A, B):
    """Transpose B first so inner loop is row-access → cache friendly"""
    n = len(A)
    BT = [[B[j][i] for j in range(n)] for i in range(n)]  # transpose
    C = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] += A[i][k] * BT[j][k]  # BT[j][k] — row access ✓
    return C

# For n=512: cache-friendly version is 5-10x faster in practice
# despite identical O(n³) complexity!`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Array sequential scan', value: 'n/16 cache misses', color: 'text-emerald-400', note: '16 ints per 64-byte cache line' },
        { case: 'Linked list traversal', value: 'n cache misses', color: 'text-red-400', note: 'Random pointer → miss every node' },
        { case: 'Row-major matrix access', value: 'n²/16 cache misses', color: 'text-emerald-400', note: 'Contiguous row access' },
        { case: 'Column-major matrix access', value: 'n² cache misses', color: 'text-red-400', note: 'Jumps entire row each step' },
      ],
      note: 'Cache misses cost 100-300ns each. At 4 billion cache-friendly operations/second vs 30-100 million cache-hostile operations/second, the difference is often 10-100x in practice — far larger than big-O predicts.',
    },
    realWorld: [
      { title: 'High-Frequency Trading', desc: 'HFT firms spend millions organizing data structures for cache alignment. Keeping order book data in contiguous arrays (not linked lists) gives them nanosecond-level advantages in market response time.' },
      { title: 'Game Engine ECS (Entity-Component System)', desc: 'Modern game engines use "Data-Oriented Design": instead of objects with all fields, keep all positions in one array, all velocities in another. This allows processing millions of game objects per frame with perfect cache utilization.' },
    ],
    commonMistakes: [
      { wrong: 'Using linked lists for sequential traversal when performance matters', right: 'Use arrays/vectors for cache-friendly traversal', explain: 'Linked list traversal is O(n) like array traversal, but causes n cache misses instead of n/16. For 100M elements, this is a 6× difference in cache misses and often a 3-5× difference in wall-clock time.' },
      { wrong: 'Assuming O notation captures all performance differences', explain: 'Two O(n) algorithms can differ by 10-100× in real performance due to cache behavior. Always profile after optimizing big-O — cache effects often dominate constants on modern hardware.' },
    ],
    videoId: "ZI9R-ErbKV4",
    videoTitle: "Cache Friendly Algorithm",
    quiz: [
      { q: 'What is a "cache line" and why does it matter for performance?', options: ['A line of code that accesses the cache', 'A 64-byte block of contiguous memory loaded together from RAM into L1 cache', 'The maximum number of cache entries', 'The time it takes to load one byte from memory'], correct: 1, explanation: 'A cache line is 64 bytes of contiguous memory loaded atomically. Reading any one byte loads the entire line. This means sequential array access amortizes each cache miss over ~16 integers — a 16× advantage over random access.' },
      { q: 'Why is sequential array traversal faster than linked list traversal for the same n elements?', options: ['Arrays support parallelism; linked lists don\'t', 'Arrays are contiguous in memory (cache-friendly); linked list nodes are scattered (random pointer dereferences cause cache misses)', 'Linked lists have O(n²) traversal time', 'Arrays don\'t need pointer arithmetic'], correct: 1, explanation: 'Array elements sit consecutively in memory. After the first cache miss, the next 15 elements are already in L1 cache. Linked list nodes are malloc\'d randomly; each pointer dereference jumps to an arbitrary memory location, causing a new cache miss.' },
      { q: 'In a C/Python/Java 2D array (row-major storage), which access pattern is cache-friendly?', options: ['Accessing matrix[0][0], matrix[1][0], matrix[2][0] (column-first)', 'Accessing matrix[0][0], matrix[0][1], matrix[0][2] (row-first)', 'Random access across both dimensions', 'Always start from the last row'], correct: 1, explanation: 'Row-major storage means consecutive elements in a row are contiguous in memory. Accessing row[0][0], row[0][1], row[0][2] hits one cache line. Column-first access (row[0][j], row[1][j]) jumps an entire row_width in memory each step — a cache miss every access.' },
      { q: 'What is the practical speedup of the cache-friendly matrix multiplication (transposing B first)?', options: ['1.01× (negligible)', '2× (roughly double)', '5-10× despite identical O(n³) complexity', '100× — cache is 100x faster'], correct: 2, explanation: 'Transposing B makes its inner-loop access row-major instead of column-major. This can reduce cache misses by 16× in the inner loop, leading to 5-10× real speedup for large matrices with identical O(n³) big-O complexity.' },
      { q: 'Why might a linked list\'s O(n) traversal be 10x slower than an array\'s O(n) traversal?', options: ['Linked lists have O(n log n) traversal, not O(n)', 'Linked list traversal causes n cache misses vs array\'s n/16 cache misses — a 16× difference', 'Arrays use CPU caches; linked lists don\'t', 'Pointer dereferencing is a slow CPU operation'], correct: 1, explanation: 'Both are O(n) algorithmically, but constant factors differ enormously. Arrays trigger ~n/16 cache misses (sequential = cache-friendly). Linked lists trigger ~n cache misses (random pointer chasing = cache-hostile). Each miss costs ~100ns → 10-100× wall-clock difference.' },
      { q: 'What is "Structure of Arrays" (SoA) vs "Array of Structures" (AoS) and when does SoA win?', options: ['SoA separates fields into individual arrays; AoS stores objects with all fields together. SoA wins when processing many objects but only accessing one field at a time.', 'SoA is for sorted data; AoS is for unsorted', 'They have identical cache performance', 'SoA is for small arrays; AoS is for large arrays'], correct: 0, explanation: 'AoS: [{x,y,z}, {x,y,z}...]. SoA: {xs:[...], ys:[...], zs:[...]}. When updating all X-coordinates, SoA accesses x[0],x[1],x[2]... sequentially (cache hit). AoS accesses x-then-skips-y-and-z (cache waste). Game engines and SIMD workloads favor SoA for this reason.' },
    ],
  },
};
