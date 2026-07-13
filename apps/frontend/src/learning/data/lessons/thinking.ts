import type { LessonData } from '../../lessons/GenericLesson';

export const thinkingLessons: Record<string, LessonData> = {
  'recursion': {
    concept: {
      overview: `Recursion is the ability of a function to call itself with a simpler version of the same problem. Once you internalize this idea, you will see it everywhere — in file systems, HTML parsing, mathematical formulas, compilers, and almost every elegant algorithm.

The mental model: a recursive function does a tiny piece of work, then delegates the rest to "a version of itself that handles a smaller input." This continues until the input is so small the answer is trivially known — the base case.

Consider computing factorial(5): instead of thinking about the full computation, ask: "if I already knew factorial(4), what would I need to do?" Just multiply by 5. And factorial(4) asks the same of factorial(3). This chain unwinds all the way to factorial(0) = 1.

The reason recursion is powerful: many problems have recursive structure. The solution to the full problem is naturally built from solutions to smaller subproblems. Recognizing this structure and expressing it recursively often produces code that is shorter, clearer, and more provably correct than the equivalent iterative version.`,
      keyPoints: [
        {
          title: 'Three Laws of Recursion',
          desc: '1. Must have a base case (stops the recursion). 2. Must move toward the base case with each call. 3. Must call itself on a smaller subproblem.',
          code: `def factorial(n: int) -> int:
    # Base case: smallest problem we can answer directly
    if n == 0:
        return 1
    # Recursive case: solve a smaller problem + combine
    return n * factorial(n - 1)

# factorial(5)
# → 5 * factorial(4)
# → 5 * 4 * factorial(3)
# → 5 * 4 * 3 * factorial(2)
# → 5 * 4 * 3 * 2 * factorial(1)
# → 5 * 4 * 3 * 2 * 1 * factorial(0)
# → 5 * 4 * 3 * 2 * 1 * 1 = 120`,
        },
        {
          title: 'The Call Stack',
          desc: 'Each recursive call creates a new "stack frame" holding local variables and the return address. The call stack grows until the base case is hit, then unwinds — each frame returning its result to the frame below it.',
          code: `# Visualizing the call stack for fibonacci(4):
# fib(4) calls fib(3) and fib(2)
#   fib(3) calls fib(2) and fib(1)
#     fib(2) calls fib(1) and fib(0)
#       fib(1) → 1    fib(0) → 0
#     fib(2) → 1
#   fib(1) → 1
#   fib(3) → 2
# fib(2) calls fib(1) and fib(0)
#   fib(2) → 1
# fib(4) → 3`,
        },
        {
          title: 'Recursion vs Loops',
          desc: 'Loops are explicit iteration; recursion is implicit iteration managed by the call stack. Both are equally powerful. Recursion shines when the problem has natural recursive structure (trees, divide & conquer); loops win when the structure is simple sequential iteration.',
        },
      ],
    },
    steps: [
      { n: '1', label: 'Identify the Base Case', desc: 'What is the smallest input where the answer is trivially known? For factorial: n=0 → 1. For binary search: empty array → not found. Define this first.', code: 'if n == 0: return 1  # base case' },
      { n: '2', label: 'Identify the Recursive Case', desc: 'Assume you already have the answer for (n-1) or a smaller subproblem. What single step combines that answer with the current input to get the full answer?', code: 'return n * factorial(n - 1)  # trust the recursive call' },
      { n: '3', label: 'Trust the Recursion', desc: 'Don\'t trace through all the nested calls in your head. Trust that factorial(n-1) correctly returns (n-1)! and write your solution in terms of that. This is the hardest mental shift.' },
      { n: '4', label: 'Verify the Unwinding', desc: 'Trace 2-3 levels to verify correctness. Check base case is reached. Check each call makes progress toward it. Check the combining step is correct.' },
      { n: '5', label: 'Check for Infinite Recursion', desc: 'Common mistake: forgetting the base case or not reducing the problem. If n stays the same or grows, recursion never terminates and you get a stack overflow.', code: 'def bad(n): return n * bad(n)  # infinite — never changes n' },
    ],
    codeExamples: [
      {
        label: 'Classic examples: factorial, Fibonacci, power',
        complexity: 'O(n) time, O(n) stack space',
        variant: 'default',
        code: `def factorial(n):
    if n <= 1: return 1
    return n * factorial(n - 1)

def fibonacci(n):
    if n <= 1: return n
    return fibonacci(n - 1) + fibonacci(n - 2)
    # Note: exponential — needs memoization for large n

def power(base, exp):
    if exp == 0: return 1
    if exp % 2 == 0:
        half = power(base, exp // 2)
        return half * half         # O(log n) — fast power!
    return base * power(base, exp - 1)

# Recursive tree traversal — the natural form
def sum_tree(node):
    if node is None: return 0
    return node.val + sum_tree(node.left) + sum_tree(node.right)`,
      },
      {
        label: 'Flatten a nested list (recursion shines here)',
        complexity: 'O(n) total elements',
        variant: 'good',
        code: `def flatten(nested):
    """[1, [2, [3, 4]], 5] → [1, 2, 3, 4, 5]"""
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))  # recurse into sublists
        else:
            result.append(item)
    return result

# Try this with an iterative approach — it's much messier.
# Recursion naturally mirrors the nested structure of the data.`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Factorial', value: 'O(n) time, O(n) space', color: 'text-emerald-400', note: 'n stack frames' },
        { case: 'Fibonacci (naive)', value: 'O(2ⁿ) time', color: 'text-red-400', note: 'Exponential — needs memoization' },
        { case: 'Power (fast)', value: 'O(log n) time', color: 'text-emerald-400', note: 'Halves exponent each call' },
        { case: 'Tree traversal', value: 'O(n) time, O(h) space', color: 'text-emerald-400', note: 'h = tree height' },
      ],
      note: 'Recursion\'s space cost is often overlooked. Each call frame uses stack space. Deep recursion (n > ~10,000) can cause stack overflow in most languages.',
    },
    realWorld: [
      { title: 'File System Traversal', desc: 'Listing all files in a directory is inherently recursive: list this folder\'s files, then recurse into each subfolder. `find`, `du`, and file explorers all use this pattern.' },
      { title: 'HTML/JSON Parsing', desc: 'HTML has nested structure: a div contains other divs which contain spans. Parsers naturally recurse into nested elements. JSON parsing is similarly recursive.' },
    ],
    commonMistakes: [
      { wrong: 'Tracing through all recursive calls mentally', right: 'Trust the recursive leap of faith', explain: 'Expert recursive thinkers don\'t trace every call. They define the base case, trust that the recursive call returns the correct answer, and write the combining step. Trust the abstraction.' },
      { wrong: 'Missing the base case', explain: 'Without a base case, recursion runs forever. Every recursive function needs at least one case where it returns a value directly without calling itself.' },
    ],
    videoId: "u8Xam9EsqXQ",
    videoTitle: "Learn Recursion in 8 Minutes",
    quiz: [
      { q: 'What is the "base case" in a recursive function?', options: ['The first call to the function', 'The condition where recursion stops and returns a value directly', 'The most complex input the function handles', 'The case where the function calls itself twice'], correct: 1, explanation: 'The base case is the simplest version of the problem where the answer is immediately known, stopping the recursion. Without it, the function recurses infinitely.' },
      { q: 'What happens when a recursive function has no base case?', options: ['It returns None', 'It runs once and stops', 'It recurses infinitely until a stack overflow error occurs', 'The compiler catches the error before running'], correct: 2, explanation: 'Without a base case, the function never stops calling itself. The call stack grows until the program runs out of stack memory, causing a stack overflow (RecursionError in Python, StackOverflowError in Java).' },
      { q: 'What does each recursive call create on the call stack?', options: ['A new thread of execution', 'A new stack frame holding that call\'s local variables', 'A new heap memory allocation', 'A new operating system process'], correct: 1, explanation: 'Each function call — recursive or not — creates a new stack frame containing local variables, parameters, and the return address. Recursion depth = stack frames simultaneously in use.' },
      { q: 'How does fast exponentiation (power(base, n)) achieve O(log n) using recursion?', options: ['It memorizes previous results', 'It halves the exponent each call: power(b, n) = power(b, n//2)²', 'It uses multiple recursive calls', 'It converts to multiplication loops'], correct: 1, explanation: 'By halving the exponent each call (power(b,n) = power(b, n/2)² when n is even), the problem size halves each step, giving O(log n) depth and O(log n) total work.' },
      { q: 'Why is recursive tree traversal more natural than iterative traversal?', options: ['Recursion is faster for trees', 'Trees have recursive structure — each node\'s subtrees are smaller trees', 'Iterative traversal doesn\'t work on trees', 'Recursion avoids memory allocation'], correct: 1, explanation: 'A tree\'s structure is inherently recursive: each subtree is itself a tree. Recursion naturally mirrors this structure, making the code shorter and easier to verify than an iterative version managing an explicit stack.' },
      { q: 'What is the main space cost of recursion that iteration avoids?', options: ['Heap memory allocation', 'Stack space: each recursive call uses a stack frame until it returns', 'Database connections', 'Network bandwidth'], correct: 1, explanation: 'Each recursive call occupies a stack frame until it returns. Deep recursion (e.g., n=100,000) can cause stack overflow. Iterative solutions reuse a single set of variables with no stack growth.' },
    ],
  },

  'divide-and-conquer': {
    concept: {
      overview: `Divide and Conquer is one of the most powerful ideas in all of computer science. The pattern: break a problem into smaller independent subproblems, solve each recursively, then combine the solutions. This seemingly simple idea is behind merge sort, binary search, the Fast Fourier Transform (which powers all digital audio and telecommunications), and Strassen's matrix multiplication.

The key insight: when you can split a problem in half and the two halves don't depend on each other, the total work often drops from O(n²) to O(n log n). Why? Because instead of doing O(n) work on a problem of size n, you do O(n) work on a problem of size n/2, then O(n) again, then again — but only log₂ n times (since n/2 → n/4 → ... → 1 takes log₂ n halvings).

Merge sort is the clearest example: split the array in half, sort each half (recursively), then merge the two sorted halves in O(n). The recursion tree has log₂ n levels, and each level does O(n) merging work — total O(n log n).

The Master Theorem gives a formula for analyzing divide-and-conquer: if you split into a subproblems of size n/b, and the combining step costs O(nᵈ), then total time is deterministically predictable.`,
      keyPoints: [
        {
          title: 'The Three Steps',
          desc: '1. DIVIDE: Split the problem into smaller subproblems (usually 2 halves). 2. CONQUER: Solve each subproblem recursively. 3. COMBINE: Merge the solutions into the final answer.',
          code: `def merge_sort(arr):
    # Base case: arrays of 0 or 1 element are already sorted
    if len(arr) <= 1:
        return arr

    # DIVIDE: split into halves
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])    # CONQUER left half
    right = merge_sort(arr[mid:])   # CONQUER right half

    # COMBINE: merge two sorted halves
    return merge(left, right)`,
        },
        {
          title: 'The Recursion Tree',
          desc: 'Visualize D&C as a tree: root = full problem, each level = one round of splitting. The tree has log₂ n levels. Total work = work per level × number of levels = O(n) × O(log n) = O(n log n).',
        },
        {
          title: 'Master Theorem',
          desc: 'For T(n) = aT(n/b) + f(n): if f(n) = O(nᵈ), compare d with log_b(a). The larger term dominates. Merge sort: a=2, b=2, d=1 → log₂(2)=1=d → O(n log n).',
        },
      ],
    },
    steps: [
      { n: '1', label: 'Identify Independence', desc: 'Check: do the subproblems need each other\'s results to be solved? If the left half\'s sort doesn\'t depend on the right half\'s sort, you can divide.' },
      { n: '2', label: 'Split at the Midpoint', desc: 'For array problems: split at index len//2. For matrix problems: split into quadrants. For strings: split at length//2.' },
      { n: '3', label: 'Recurse on Both Halves', desc: 'Call the same function on each half. Trust (per the recursion leap of faith) that these return correct answers for smaller inputs.' },
      { n: '4', label: 'Combine Results', desc: 'Merge the two sorted halves (merge sort), combine counts (inversions), combine partial sums. This step should be O(n) or O(n log n) at most.' },
      { n: '5', label: 'Analyze with Master Theorem', desc: 'Count a (subproblems), b (size divisor), d (combine cost exponent). Apply: if log_b(a) = d → O(n^d log n). If log_b(a) > d → O(n^log_b(a)).' },
    ],
    codeExamples: [
      {
        label: 'Merge sort — the canonical D&C algorithm',
        complexity: 'O(n log n) time, O(n) space',
        variant: 'default',
        code: `def merge_sort(arr):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result`,
      },
      {
        label: 'Count inversions (a D&C problem that builds on merge sort)',
        complexity: 'O(n log n)',
        variant: 'good',
        code: `def count_inversions(arr):
    """Count pairs (i,j) where i < j but arr[i] > arr[j].
    Modified merge sort: count inversions during merge."""
    if len(arr) <= 1:
        return arr, 0

    mid = len(arr) // 2
    left, left_inv = count_inversions(arr[:mid])
    right, right_inv = count_inversions(arr[mid:])

    merged = []
    inversions = left_inv + right_inv
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i]); i += 1
        else:
            # All remaining left elements are > right[j]
            inversions += len(left) - i
            merged.append(right[j]); j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, inversions`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Merge Sort', value: 'O(n log n)', color: 'text-emerald-400', note: 'Guaranteed — best, avg, worst' },
        { case: 'Binary Search', value: 'O(log n)', color: 'text-emerald-400', note: 'Divides search space in half each step' },
        { case: 'Fast Power', value: 'O(log n)', color: 'text-emerald-400', note: 'Halves exponent each call' },
        { case: 'FFT', value: 'O(n log n)', color: 'text-emerald-400', note: 'Transforms n-point DFT from O(n²) to O(n log n)' },
      ],
      note: 'The Master Theorem is your complexity calculator for D&C. T(n) = 2T(n/2) + O(n) → O(n log n). T(n) = 2T(n/2) + O(1) → O(n). T(n) = T(n/2) + O(1) → O(log n).',
    },
    realWorld: [
      { title: 'Fast Fourier Transform (FFT)', desc: 'The FFT computes the frequency spectrum of a signal — powering digital audio, video compression, wireless communications, and image processing. It applies D&C to reduce the naive O(n²) DFT to O(n log n).' },
      { title: 'Merge Sort in System Libraries', desc: 'Python\'s built-in sort (Timsort) is based on merge sort. Java\'s Arrays.sort for objects uses merge sort. Git\'s diff algorithm uses merge-like techniques for comparing file versions.' },
    ],
    commonMistakes: [
      { wrong: 'Using D&C when subproblems aren\'t independent', explain: 'D&C requires subproblems that don\'t need each other\'s results. When there\'s overlap (like in Fibonacci), you need Dynamic Programming with memoization instead.' },
      { wrong: 'Expensive combine step killing the O(n log n) advantage', explain: 'If combining costs O(n²), the total is O(n² log n) — worse than brute force in many cases. The combine step must be O(n) or O(n log n) for D&C to pay off.' },
    ],
    videoId: "TvQesCFPgLg",
    videoTitle: "Divide and Conquer Explained in 100 Seconds",
    quiz: [
      { q: 'What are the three steps of divide and conquer?', options: ['Read, Process, Write', 'Divide, Conquer, Combine', 'Init, Recurse, Return', 'Split, Merge, Sort'], correct: 1, explanation: 'Divide: break the problem into subproblems. Conquer: recursively solve each subproblem. Combine: merge the subproblem solutions into the final answer.' },
      { q: 'Why does merge sort achieve O(n log n) instead of O(n²)?', options: ['It avoids comparisons entirely', 'The array is always pre-sorted', 'The recursion tree has log₂ n levels, each doing O(n) merge work', 'It uses a hash table for sorting'], correct: 2, explanation: 'The array is halved each level, creating log₂ n levels of recursion. Each level merges all elements in O(n) total. So total work = O(n) × O(log n) = O(n log n).' },
      { q: 'What is the key requirement for divide and conquer to work?', options: ['The input must be sorted', 'Subproblems must be independent — solutions don\'t depend on each other', 'The problem must involve numbers', 'Subproblems must be equal size'], correct: 1, explanation: 'D&C requires that subproblems can be solved independently. When subproblems overlap (share sub-subproblems), D&C recomputes them repeatedly — Dynamic Programming is needed instead.' },
      { q: 'The Fast Fourier Transform (FFT) improves DFT from O(n²) to O(n log n) using what strategy?', options: ['Better hardware', 'Approximation (lossy FFT)', 'Divide and conquer on the frequency domain', 'Parallel processing'], correct: 2, explanation: 'The FFT recursively splits the n-point DFT into two n/2-point DFTs, applies D&C, and reduces from O(n²) to O(n log n). This is the Cooley-Tukey algorithm — one of the most important algorithms in history.' },
      { q: 'Given T(n) = 2T(n/2) + O(n) (merge sort recurrence), what is the solution?', options: ['O(n)', 'O(n log n)', 'O(n²)', 'O(log n)'], correct: 1, explanation: 'By the Master Theorem: a=2 subproblems, b=2 size divisor, combine cost d=1 (O(n)). Since log₂(2) = 1 = d, the result is O(n^d log n) = O(n log n).' },
      { q: 'When should you use Dynamic Programming instead of Divide and Conquer?', options: ['When the input is very large', 'When subproblems overlap (the same sub-subproblems are computed repeatedly)', 'When you need O(n²) complexity', 'When the recursion depth is limited'], correct: 1, explanation: 'Naive Fibonacci is D&C, but it recomputes fib(2) dozens of times. DP memoizes sub-results to avoid redundant computation. The distinguishing factor is whether subproblems overlap.' },
    ],
  },

  'two-pointers': {
    concept: {
      overview: `Two Pointers is a technique where you maintain two indices into an array and move them strategically — often toward each other — to eliminate the need for a nested loop. It's one of the most powerful linear-time tricks for array problems.

The classic example: given a sorted array, find two numbers that sum to a target. The brute force is O(n²): try every pair. Two pointers is O(n): put one pointer at the left (smallest) and one at the right (largest). If their sum is too small, move left pointer right (increase sum). If too large, move right pointer left (decrease sum). Each step eliminates one possibility, so we find the pair in at most n steps.

The insight: on a sorted array, you have powerful directional control over what happens when you move each pointer. Moving left right can only increase the sum; moving right left can only decrease it. This deterministic control lets you eliminate entire categories of possibilities with each step.

Two pointers also applies to strings (palindrome check), linked lists (cycle detection with slow/fast pointers), and partitioning (the key step in quicksort). The pattern: "instead of two nested loops scanning the same array, move two pointers intelligently in one pass."`,
      keyPoints: [
        {
          title: 'Opposite-End Pointers (Sorted Array)',
          desc: 'Left starts at index 0, right at index n-1. Move based on comparison with target. Eliminates one element per step → O(n).',
          code: `def two_sum_sorted(arr, target):
    left, right = 0, len(arr) - 1
    while left < right:
        total = arr[left] + arr[right]
        if total == target:
            return (left, right)     # found!
        elif total < target:
            left += 1                # sum too small → increase it
        else:
            right -= 1               # sum too large → decrease it
    return None  # no pair found`,
        },
        {
          title: 'Same-Direction Pointers (Fast/Slow)',
          desc: 'Both pointers move in the same direction but at different speeds. Used for cycle detection (Floyd\'s algorithm), finding the middle of a list, and removing duplicates.',
          code: `# Detect cycle in linked list (Floyd's algorithm)
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next          # moves 1 step
        fast = fast.next.next     # moves 2 steps
        if slow == fast:
            return True           # they meet → cycle!
    return False`,
        },
        {
          title: 'Palindrome Verification',
          desc: 'One pointer starts at each end and moves inward. If characters always match, it\'s a palindrome. O(n) in one pass — no extra space needed.',
          code: `def is_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True`,
        },
      ],
    },
    steps: [
      { n: '1', label: 'Identify the Pattern', desc: 'Is the problem about finding a pair in a sorted array? Checking a string property? Removing duplicates? These are two-pointer candidates.' },
      { n: '2', label: 'Initialize Pointers', desc: 'For opposite-end: left=0, right=n-1. For fast/slow: both start at head/0. For remove-duplicates: slow=0, fast=1.' },
      { n: '3', label: 'Define the Invariant', desc: 'What property is always maintained? For two-sum: all elements to the left of `left` are too small to form a valid pair. This invariant justifies each pointer move.' },
      { n: '4', label: 'Move Pointers Based on Comparison', desc: 'Each step, compare arr[left] and arr[right] (or some derived value) to the target. Move the pointer that brings you closer to the answer.' },
      { n: '5', label: 'Terminate When Pointers Cross', desc: 'For opposite-end: stop when left >= right. For fast/slow: stop when fast reaches null. Every element has been examined in one pass.' },
    ],
    codeExamples: [
      {
        label: 'Remove duplicates from sorted array in-place',
        complexity: 'O(n) time, O(1) space',
        variant: 'default',
        code: `def remove_duplicates(nums):
    """Returns the count of unique elements.
    Modifies nums in-place so the first k elements are unique."""
    if not nums: return 0
    slow = 0
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    return slow + 1

# [1, 1, 2, 3, 3, 4] → [1, 2, 3, 4, _, _], returns 4
# slow tracks where to write next unique element
# fast scans ahead looking for new unique elements`,
      },
      {
        label: 'Three-sum (two pointers inside a loop)',
        complexity: 'O(n²) — better than O(n³) brute force',
        variant: 'good',
        code: `def three_sum(nums):
    """Find all unique triplets that sum to 0."""
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i-1]:
            continue                  # skip duplicates
        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left+1]: left += 1
                while left < right and nums[right] == nums[right-1]: right -= 1
                left += 1; right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1
    return result`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Two-sum (sorted)', value: 'O(n)', color: 'text-emerald-400', note: 'vs O(n²) brute force' },
        { case: 'Palindrome check', value: 'O(n)', color: 'text-emerald-400', note: 'O(1) space' },
        { case: 'Three-sum', value: 'O(n²)', color: 'text-amber-400', note: 'vs O(n³) brute force' },
        { case: 'Remove duplicates', value: 'O(n)', color: 'text-emerald-400', note: 'O(1) space in-place' },
      ],
      note: 'Two pointers eliminates nested loops by using structural properties of the data (usually sorted order or palindromic structure). The key is always: "moving this pointer in direction X only improves/worsens the objective in direction Y."',
    },
    realWorld: [
      { title: 'Database Merge Join', desc: 'When joining two sorted tables, databases use a two-pointer approach: advance through both tables simultaneously, matching rows with equal join keys. O(n+m) instead of O(n×m).' },
      { title: 'Network Packet Reassembly', desc: 'TCP uses sliding window (a variant of two pointers) to track which packets have been received and which are still outstanding, enabling reliable streaming delivery.' },
    ],
    commonMistakes: [
      { wrong: 'Applying two pointers to unsorted arrays for sum problems', right: 'Sort first, then apply two pointers', explain: 'Two pointers for sum problems relies on sorted order to know which direction to move. On unsorted arrays, moving left right doesn\'t guarantee increasing the sum.' },
      { wrong: 'Terminating when left == right instead of left >= right', explain: 'When left equals right, both pointers point to the same element. You\'re looking for pairs (two distinct elements), so terminate when they meet (left >= right), not after.' },
    ],
    videoId: "QzZ7nmouLTI",
    videoTitle: "Two Pointers in 7 Minutes | LeetCode Pattern",
    quiz: [
      { q: 'What is the primary advantage of the two-pointer technique over nested loops?', options: ['It works on unsorted data', 'It reduces O(n²) pair-finding to O(n) with one pass', 'It uses less memory than a single loop', 'It avoids all comparisons'], correct: 1, explanation: 'Nested loops check every pair in O(n²). Two pointers use directional control to eliminate entire categories of pairs with each move, solving the same problem in O(n).' },
      { q: 'For two-sum on a sorted array, why does moving the left pointer right always increase the potential sum?', options: ['The left element is always smaller than the right element', 'Arrays are sorted ascending, so elements increase left to right', 'Moving left right decreases the range between pointers', 'The right pointer compensates by moving left'], correct: 1, explanation: 'In a sorted ascending array, elements increase from left to right. Moving the left pointer right gives a larger left element, which increases arr[left] + arr[right].' },
      { q: 'Floyd\'s cycle detection uses two pointers moving at different speeds. What does it mean when they meet?', options: ['The list is sorted', 'There is no cycle', 'There is a cycle — the slow pointer was lapped by the fast pointer', 'The list has duplicate values'], correct: 2, explanation: 'If a cycle exists, the fast pointer (2 steps) eventually laps the slow pointer (1 step) inside the cycle — they meet. If no cycle exists, the fast pointer reaches null.' },
      { q: 'Which type of problem is NOT naturally solved by two pointers?', options: ['Palindrome verification', 'Finding a cycle in a linked list', 'Finding the median of an unsorted array', 'Removing duplicates from a sorted array'], correct: 2, explanation: 'Finding the median of an unsorted array requires knowing the middle element, which needs either sorting (O(n log n)) or a selection algorithm. Two pointers don\'t help without sorted order.' },
      { q: 'In the three-sum problem (find all triplets summing to 0), two pointers reduces the complexity from O(n³) to what?', options: ['O(n)', 'O(n log n)', 'O(n²)', 'O(n² log n)'], correct: 2, explanation: 'Fix one element with an outer loop O(n), then use two pointers on the remaining sorted subarray O(n) to find pairs summing to the target. Total: O(n) × O(n) = O(n²).' },
      { q: 'What is the key prerequisite for using opposite-direction two pointers on a sum problem?', options: ['The array must contain only integers', 'The array must be sorted', 'The array must have even length', 'The target must be positive'], correct: 1, explanation: 'Sorted order is essential. It gives the directional guarantee: moving left right increases the sum; moving right left decreases it. Without sorting, we don\'t know which direction to move.' },
    ],
  },

  'sliding-window': {
    concept: {
      overview: `The sliding window technique solves problems on contiguous subarrays or substrings in O(n) time — without ever looking at the same element twice. The idea: maintain a "window" (a range [left, right]) that slides through the data. Expand right to include new elements; shrink left to remove elements that violate a constraint.

The classic problem: "find the maximum sum of any k consecutive elements." Brute force: try every window of size k → O(n×k). Sliding window: start with the first window's sum, then for each subsequent window, add the new right element and subtract the old left element → O(n).

But sliding window shines most on variable-size problems: "find the shortest subarray with sum ≥ target", "find the longest substring without repeating characters." The window expands until a constraint is violated, then shrinks until the constraint is restored. Since each element enters and leaves the window at most once, total work is O(n).

The mental model: a physical window sliding along a newspaper. You always see a fixed or bounded range of content. When you add the next column on the right, you lose the leftmost column. The key insight is that adding/removing one element from the window can be done in O(1).`,
      keyPoints: [
        {
          title: 'Fixed-Size Window',
          desc: 'Window size is constant (k). Add new right element, subtract old left element. Perfect for "max/min/sum of exactly k consecutive elements."',
          code: `def max_sum_subarray(arr, k):
    window_sum = sum(arr[:k])
    max_sum = window_sum

    for i in range(k, len(arr)):
        window_sum += arr[i]         # add new right element
        window_sum -= arr[i - k]     # remove old left element
        max_sum = max(max_sum, window_sum)

    return max_sum`,
        },
        {
          title: 'Variable-Size Window',
          desc: 'Window size changes dynamically based on a constraint. Expand right until constraint violated, shrink left until restored. Each element enters/leaves once → O(n).',
          code: `def longest_no_repeat(s: str) -> int:
    char_set = set()
    left = max_len = 0
    for right in range(len(s)):
        while s[right] in char_set:     # constraint violated
            char_set.remove(s[left])    # shrink left
            left += 1
        char_set.add(s[right])          # expand right
        max_len = max(max_len, right - left + 1)
    return max_len`,
        },
        {
          title: 'Window + Hash Map',
          desc: 'Combine sliding window with a hash map to track character counts within the window. This pattern solves "find anagram/permutation in string", "minimum window substring" in O(n).',
        },
      ],
    },
    steps: [
      { n: '1', label: 'Define the Window', desc: 'What are the window boundaries? Usually left=0, right=0, both starting at index 0. The window represents the "current candidate range."' },
      { n: '2', label: 'Define the Constraint', desc: 'What makes a window valid or invalid? For "no repeating chars": all characters in window must be unique. For "sum ≥ target": sum of window ≥ target.' },
      { n: '3', label: 'Expand Right', desc: 'Move right pointer forward one step, adding the new element to your window state (e.g., add to sum, insert into set/map).' },
      { n: '4', label: 'Shrink Left if Needed', desc: 'If the window now violates the constraint, advance left pointer, removing the old element from window state, until the constraint is satisfied again.' },
      { n: '5', label: 'Update Answer', desc: 'After each expansion (or after each valid window state), update the answer with the current window size, sum, or whatever metric you\'re optimizing.' },
    ],
    codeExamples: [
      {
        label: 'Minimum window substring (hard sliding window)',
        complexity: 'O(n) time, O(k) space for k unique chars',
        variant: 'default',
        code: `from collections import Counter

def min_window(s: str, t: str) -> str:
    """Find the smallest window in s that contains all chars of t."""
    need = Counter(t)
    missing = len(t)           # how many chars still needed
    best = ""
    left = 0

    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1       # satisfied one required char
        need[ch] -= 1

        if missing == 0:       # window contains all of t
            # Shrink from left while window is still valid
            while need[s[left]] < 0:
                need[s[left]] += 1
                left += 1
            window = s[left:right+1]
            if not best or len(window) < len(best):
                best = window
            # Prepare to extend again
            need[s[left]] += 1
            missing += 1
            left += 1
    return best`,
      },
      {
        label: 'All anagrams in a string',
        complexity: 'O(n) — classic sliding window with freq map',
        variant: 'good',
        code: `from collections import Counter

def find_anagrams(s: str, p: str) -> list:
    """Return start indices of all anagrams of p in s."""
    need = Counter(p)
    window = Counter(s[:len(p)])
    result = []

    if window == need:
        result.append(0)

    for i in range(len(p), len(s)):
        right_char = s[i]
        left_char = s[i - len(p)]

        window[right_char] += 1             # add right
        if window[left_char] == 1:
            del window[left_char]           # remove left
        else:
            window[left_char] -= 1

        if window == need:
            result.append(i - len(p) + 1)

    return result`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Fixed window (max sum k elements)', value: 'O(n)', color: 'text-emerald-400', note: 'vs O(nk) brute force' },
        { case: 'Longest substring no repeat', value: 'O(n)', color: 'text-emerald-400', note: 'Each element enters/leaves once' },
        { case: 'Minimum window substring', value: 'O(n)', color: 'text-emerald-400', note: 'Two-pointer pass with freq map' },
        { case: 'Space', value: 'O(k)', color: 'text-emerald-400', note: 'k = window size or unique chars' },
      ],
      note: 'The amortized O(n) proof: right pointer advances n times total; left pointer also advances at most n times total. So the inner shrink loop runs at most n times total across all outer iterations.',
    },
    realWorld: [
      { title: 'TCP Sliding Window', desc: 'TCP\'s flow control uses a sliding window: the receiver advertises a window size. The sender can have at most "window size" bytes unacknowledged at any time. This prevents overwhelming a slow receiver.' },
      { title: 'Network Rate Limiting', desc: 'API rate limiting (e.g., "max 100 requests per second") uses a sliding window counter. The window slides with time, expiring old requests as new ones come in.' },
    ],
    commonMistakes: [
      { wrong: 'Using sliding window on non-contiguous subsets', explain: 'Sliding window only works for contiguous subarrays/substrings. If the problem asks for subsequences (non-contiguous), a different approach (DP or two-pointers with a different structure) is needed.' },
      { wrong: 'Shrinking the window too aggressively', explain: 'After shrinking to restore the constraint, don\'t shrink further — the window is now valid and you want it as large as possible. Shrink only while constraint is violated.' },
    ],
    videoId: "FjlPyEHZ8e8",
    videoTitle: "Sliding Window Technique Explained Simply",
    quiz: [
      { q: 'What is the key operation that makes sliding window O(n) instead of O(n²)?', options: ['Using binary search inside the window', 'Adding one element and removing one element per step — O(1) per slide', 'Sorting the window at each step', 'Pre-computing prefix sums'], correct: 1, explanation: 'Each slide adds one element (right++) and removes one element (left++). If both add/remove are O(1) (using counters, sets, or arithmetic), the total work per slide is O(1), giving O(n) overall.' },
      { q: 'When should you use a fixed-size sliding window vs a variable-size one?', options: ['Fixed when data is sorted, variable when unsorted', 'Fixed when the window size is specified (e.g., k consecutive), variable when you\'re optimizing the window size', 'Always use fixed — it\'s simpler', 'Fixed for arrays, variable for strings'], correct: 1, explanation: 'Fixed-size windows are for "exactly k elements" problems. Variable-size windows are for "find the shortest/longest window satisfying a constraint" — the window shrinks or grows based on validity.' },
      { q: 'In the longest-substring-without-repeating-characters problem, when do you shrink the left pointer?', options: ['After every 10 characters', 'Whenever the window has more than 3 characters', 'Whenever a repeated character enters the window', 'Whenever the right pointer reaches the end'], correct: 2, explanation: 'Shrink left when a character enters the window that\'s already present (constraint violated: not all unique). Keep shrinking until the duplicate is removed and all characters are unique again.' },
      { q: 'Why is the amortized complexity of sliding window O(n) even though there is an inner shrink loop?', options: ['The inner loop never runs more than once per outer step', 'Each element is added to the window once and removed at most once, so total loop iterations ≤ 2n', 'The inner loop runs at constant speed', 'The outer loop compensates for the inner loop'], correct: 1, explanation: 'Amortized analysis: the right pointer advances n times total. The left pointer also advances at most n times total (across all shrink operations). So the total work is O(n) + O(n) = O(n).' },
      { q: 'Which problem is best solved with a sliding window?', options: ['Find two numbers in an unsorted array that sum to a target', 'Find the longest subarray with sum ≤ k', 'Sort an array in O(n log n)', 'Find the median of a stream of numbers'], correct: 1, explanation: '"Longest subarray with sum ≤ k" is a variable-size sliding window: expand right while sum ≤ k, shrink left when sum > k, track the maximum valid window length.' },
      { q: 'TCP uses a sliding window for flow control. What does the "window size" represent?', options: ['The maximum packet size in bytes', 'How many bytes the sender can transmit before waiting for an acknowledgment', 'The number of connections the server can handle', 'The time limit before a packet is retransmitted'], correct: 1, explanation: 'TCP\'s sliding window allows the sender to have up to "window size" bytes unacknowledged at any time, balancing throughput with the receiver\'s ability to process data.' },
    ],
  },

  'greedy-thinking': {
    concept: {
      overview: `Greedy algorithms make the locally optimal choice at each step — the best option right now — without reconsidering past choices. The surprising thing is that for many important problems, this produces the globally optimal solution.

The classic example is activity selection: given a list of meetings with start and end times, schedule as many as possible in one room. The greedy choice: always pick the meeting that ends earliest. This leaves the most room for future meetings. Remarkably, this always gives the maximum number of meetings — no backtracking needed.

But greedy doesn't always work. The coin change problem illustrates the failure mode: with coins {1, 3, 4} and target 6, greedy picks 4 then 1 then 1 (3 coins). The optimal solution is 3+3 (2 coins). Greedy failed because the "locally best" coin didn't lead to the globally best combination.

The key question for any greedy problem: "can I prove that the greedy choice never leads me away from an optimal solution?" If yes (via an exchange argument), greedy works. If no, you need dynamic programming.`,
      keyPoints: [
        {
          title: 'Greedy Choice Property',
          desc: 'At each step, choosing the locally optimal option doesn\'t prevent reaching the global optimum. This property must be proven — it\'s not obvious and doesn\'t hold for all problems.',
        },
        {
          title: 'Optimal Substructure',
          desc: 'After making the greedy choice, the remaining subproblem has the same structure as the original. The optimal solution to the remainder (combined with the greedy choice) gives the optimal total solution.',
          code: `# Activity Selection — greedy works
# Proof: if we don't pick the earliest-ending activity,
# we can always swap it in without worse outcome

def activity_selection(activities):
    # Sort by end time — greedy choice
    activities.sort(key=lambda x: x[1])
    selected = [activities[0]]
    for start, end in activities[1:]:
        if start >= selected[-1][1]:  # no overlap with last selected
            selected.append((start, end))
    return selected`,
        },
        {
          title: 'When Greedy Fails: Use DP',
          desc: 'Coins {1,3,4}, target 6: greedy picks 4→1→1 (3 coins). Optimal is 3→3 (2 coins). Greedy fails because a past choice (taking 4) closed off the optimal future path.',
          code: `# Coin change — greedy FAILS for arbitrary denominations
# Use DP instead
def coin_change_dp(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1`,
        },
      ],
    },
    steps: [
      { n: '1', label: 'Identify the Greedy Choice', desc: 'What is the "most promising" option at each step? For scheduling: earliest end time. For coin change: largest coin. For Huffman: least frequent symbol.' },
      { n: '2', label: 'Prove It Never Hurts', desc: 'Use an exchange argument: assume the optimal solution doesn\'t make the greedy choice. Show you can swap in the greedy choice and the solution doesn\'t get worse. Therefore greedy is safe.' },
      { n: '3', label: 'Apply Greedy Iteratively', desc: 'Sort by the greedy criterion if needed (sorting is often needed for greedy to work). Then iterate and make the greedy choice at each step.' },
      { n: '4', label: 'Update Remaining Problem', desc: 'After making the greedy choice, the remaining subproblem has the same structure. Solve it with the same greedy strategy.' },
      { n: '5', label: 'Know When to Stop and Use DP', desc: 'If you can construct a counterexample (a case where greedy fails), switch to dynamic programming. Greedy and DP are the two main tools for optimization problems.' },
    ],
    codeExamples: [
      {
        label: 'Activity selection — greedy works',
        complexity: 'O(n log n) to sort, then O(n)',
        variant: 'good',
        code: `def max_activities(intervals):
    """Schedule maximum non-overlapping intervals."""
    intervals.sort(key=lambda x: x[1])  # sort by end time
    count = 1
    last_end = intervals[0][1]

    for start, end in intervals[1:]:
        if start >= last_end:
            count += 1
            last_end = end

    return count

# Why greedy works: picking earliest-end activity leaves
# the most time for subsequent activities.
# Proof: any optimal solution can be transformed to
# include the earliest-end activity without loss.`,
      },
      {
        label: 'Fractional knapsack — greedy works; 0/1 knapsack — greedy fails',
        complexity: 'O(n log n)',
        variant: 'default',
        code: `def fractional_knapsack(items, capacity):
    """items: list of (value, weight). Maximize value."""
    # Greedy: sort by value-per-weight ratio
    items.sort(key=lambda x: x[0]/x[1], reverse=True)
    total_value = 0
    for value, weight in items:
        if capacity >= weight:
            total_value += value        # take the whole item
            capacity -= weight
        else:
            # Take a fraction
            total_value += value * (capacity / weight)
            break
    return total_value

# KEY: fractions are allowed → greedy works optimally
# If fractions are NOT allowed (0/1 knapsack) → need DP`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Activity selection', value: 'O(n log n)', color: 'text-emerald-400', note: 'Dominated by sorting' },
        { case: 'Fractional knapsack', value: 'O(n log n)', color: 'text-emerald-400', note: 'Sort by value/weight ratio' },
        { case: 'Huffman coding', value: 'O(n log n)', color: 'text-emerald-400', note: 'Min-heap with n extractions' },
        { case: 'Coin change (greedy fail)', value: 'Wrong answer', color: 'text-red-400', note: 'Needs DP: O(amount × coins)' },
      ],
      note: 'The exchange argument is the standard proof technique for greedy algorithms: if the optimal doesn\'t use the greedy choice, show you can swap without loss.',
    },
    realWorld: [
      { title: 'Meeting Room Scheduling', desc: 'Companies use greedy algorithms to maximize room utilization: always assign a meeting to the room that ends soonest (compatible with the meeting\'s start time). This is a generalization of activity selection.' },
      { title: 'Huffman Compression', desc: 'Huffman coding is a greedy algorithm: always merge the two least-frequent symbols. The resulting tree is provably optimal for prefix-free codes — greedy gives the exact optimal solution here.' },
    ],
    commonMistakes: [
      { wrong: 'Assuming greedy always gives the optimal answer', explain: 'Greedy gives optimal only when the greedy choice property holds. Always test with counterexamples. The coin change problem (with non-standard denominations) is a classic greedy failure.' },
      { wrong: 'Confusing greedy with dynamic programming', explain: 'Greedy makes one irreversible choice per step and doesn\'t reconsider. DP considers all possibilities and picks the best. Use greedy when you can prove it\'s safe; use DP when you cannot.' },
    ],
    videoId: "bC7o8P_Ste4",
    videoTitle: "Greedy Algorithms Tutorial - Solve Coding Challenges",
    quiz: [
      { q: 'What is the "greedy choice property"?', options: ['The greedy algorithm always makes the fastest choice', 'Making the locally optimal choice at each step never prevents finding the global optimum', 'Greedy algorithms never need to sort their input', 'Greedy works only when all choices are equal'], correct: 1, explanation: 'The greedy choice property guarantees that the locally optimal choice is always compatible with some globally optimal solution. This is what makes greedy algorithms correct — it must be proven, not assumed.' },
      { q: 'In the activity selection problem, what is the greedy criterion?', options: ['Pick the activity with the earliest start time', 'Pick the activity with the shortest duration', 'Pick the activity with the earliest end time', 'Pick the activity with the latest end time'], correct: 2, explanation: 'Picking the earliest end time leaves the most remaining time for future activities. This greedy choice can be proven optimal via an exchange argument.' },
      { q: 'Why does greedy fail for 0/1 knapsack but succeed for fractional knapsack?', options: ['0/1 knapsack has larger inputs', 'In fractional knapsack, taking a fraction of a high-ratio item is always safe; in 0/1, taking a whole item might block a better combination', 'The greedy sorting differs between the two problems', 'Greedy actually works for both'], correct: 1, explanation: 'With fractions allowed, the highest value-per-weight item is always the best use of available capacity. In 0/1 knapsack, taking a whole item might leave wasted capacity that no remaining items can fill optimally.' },
      { q: 'What is the exchange argument used to prove greedy correctness?', options: ['Show the greedy solution is faster than DP', 'Assume optimal doesn\'t use greedy choice; show swapping in the greedy choice doesn\'t worsen the solution', 'Prove the greedy algorithm terminates', 'Show greedy and brute force give the same answer on small inputs'], correct: 1, explanation: 'The exchange argument: take any optimal solution that doesn\'t use the greedy choice. Show you can modify it to include the greedy choice (by swapping) without reducing its quality. Therefore the greedy choice is always safe.' },
      { q: 'With coins {1, 3, 4} and target 6, greedy (largest first) picks 4+1+1=3 coins. What is the actual optimum?', options: ['3 coins — greedy was right', '2 coins: 3+3', '1 coin: we\'re missing a 6-coin', '4 coins: 1+1+1+1+1+1'], correct: 1, explanation: '3+3 = 6 uses only 2 coins vs greedy\'s 3 coins. Greedy fails here because taking 4 prevents using 3+3. This shows greedy doesn\'t always work for arbitrary coin denominations — use DP.' },
      { q: 'When should you prefer dynamic programming over a greedy algorithm?', options: ['When the input is unsorted', 'When the problem has overlapping subproblems and greedy can fail', 'When the problem involves graphs', 'When time complexity must be O(n)'], correct: 1, explanation: 'Use DP when you can construct a counterexample showing greedy fails, or when the optimal choice at each step depends on future choices (no greedy choice property). DP explores all possibilities via memoization.' },
    ],
  },

  'prefix-sums': {
    concept: {
      overview: `Prefix sums are one of the simplest yet most powerful preprocessing tricks in algorithms. The idea: spend O(n) time computing a "running total" array, then answer any "sum of elements from index L to R" query in O(1) — no matter how many queries you have.

Without prefix sums: computing the sum of arr[L..R] takes O(R-L+1) time — you have to add each element. With 10,000 queries on a 1M-element array, that's 10 billion operations.

With prefix sums: build prefix[i] = arr[0] + arr[1] + ... + arr[i-1]. Then sum(L, R) = prefix[R+1] - prefix[L]. This is O(1) per query, O(n) once to build. 10,000 queries → 10,000 operations.

The prefix sum is also the foundation for 2D prefix sums (used in image processing), difference arrays (range updates in O(1)), and more complex algorithms like Kadane's algorithm for maximum subarray sum.

Once you see prefix sums, you'll recognize the pattern everywhere: whenever a problem asks for repeated range queries, consider precomputation.`,
      keyPoints: [
        {
          title: 'Building the Prefix Array',
          desc: 'prefix[0] = 0. prefix[i] = prefix[i-1] + arr[i-1]. This means prefix[i] stores the sum of the first i elements.',
          code: `def build_prefix(arr):
    prefix = [0] * (len(arr) + 1)
    for i in range(len(arr)):
        prefix[i+1] = prefix[i] + arr[i]
    return prefix

# arr     = [3, 1, 4, 1, 5, 9]
# prefix  = [0, 3, 4, 8, 9, 14, 23]
#             ^  (sum of 0 elements)`,
        },
        {
          title: 'O(1) Range Sum Query',
          desc: 'sum(arr[L..R]) = prefix[R+1] - prefix[L]. This works because prefix[R+1] includes everything up to index R, and subtracting prefix[L] removes everything before L.',
          code: `def range_sum(prefix, L, R):
    return prefix[R+1] - prefix[L]

# sum(arr[2..4]) = prefix[5] - prefix[2]
#                = 14 - 4
#                = 10   ✓  (4 + 1 + 5 = 10)`,
        },
        {
          title: '2D Prefix Sums',
          desc: 'Extend to a 2D grid: prefix[i][j] = sum of all cells in the rectangle from (0,0) to (i-1,j-1). Used in image filtering (sliding kernel sums), video game area damage calculations, and satellite data analysis.',
        },
      ],
    },
    steps: [
      { n: '1', label: 'Create Prefix Array', desc: 'Allocate prefix[0..n] where n is the array length. Set prefix[0] = 0 (the sum of zero elements).' },
      { n: '2', label: 'Fill Left to Right', desc: 'For each i from 1 to n: prefix[i] = prefix[i-1] + arr[i-1]. One pass, O(n).' },
      { n: '3', label: 'Answer Range Query', desc: 'For sum of arr[L..R]: return prefix[R+1] - prefix[L]. O(1) — just two array lookups and one subtraction.' },
      { n: '4', label: 'Identify Prefix Sum Problems', desc: 'Look for: repeated range sum queries, "subarray sum equals target", "number of subarrays with sum k". These all use prefix sums as the key insight.' },
      { n: '5', label: 'Extend to Differences', desc: 'Difference arrays (the inverse of prefix sums) enable O(1) range updates: add value v to arr[L..R] by diff[L]+=v and diff[R+1]-=v, then take a prefix sum to reconstruct the array.' },
    ],
    codeExamples: [
      {
        label: 'Count subarrays with sum equal to k',
        complexity: 'O(n) — classic prefix sum + hash map',
        variant: 'default',
        code: `from collections import defaultdict

def subarray_sum_k(nums, k):
    """Count subarrays with sum exactly equal to k."""
    count = 0
    prefix_sum = 0
    seen = defaultdict(int)
    seen[0] = 1    # empty prefix has sum 0

    for num in nums:
        prefix_sum += num
        # If (prefix_sum - k) was seen before,
        # that many subarrays ending here have sum k
        count += seen[prefix_sum - k]
        seen[prefix_sum] += 1

    return count

# Example: nums=[1,2,3], k=3
# Subarrays summing to 3: [1,2] and [3] → returns 2`,
      },
      {
        label: '2D prefix sums — sum of any rectangle',
        complexity: 'O(1) query after O(mn) precomputation',
        variant: 'good',
        code: `def build_2d_prefix(grid):
    m, n = len(grid), len(grid[0])
    prefix = [[0] * (n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            prefix[i][j] = (grid[i-1][j-1]
                          + prefix[i-1][j]
                          + prefix[i][j-1]
                          - prefix[i-1][j-1])
    return prefix

def rect_sum(prefix, r1, c1, r2, c2):
    """Sum of rectangle from (r1,c1) to (r2,c2) inclusive."""
    return (prefix[r2+1][c2+1]
          - prefix[r1][c2+1]
          - prefix[r2+1][c1]
          + prefix[r1][c1])`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Build prefix array', value: 'O(n)', color: 'text-amber-400', note: 'One-time cost' },
        { case: 'Range sum query', value: 'O(1)', color: 'text-emerald-400', note: 'After O(n) preprocessing' },
        { case: 'Subarray sum = k', value: 'O(n)', color: 'text-emerald-400', note: 'Prefix sum + hash map' },
        { case: '2D prefix sum query', value: 'O(1)', color: 'text-emerald-400', note: 'After O(mn) preprocessing' },
      ],
      note: 'Prefix sums turn "scan the range every query" from O(n) per query to O(1). The preprocessing cost is always O(n) — worth paying when you have more than a constant number of queries.',
    },
    realWorld: [
      { title: 'Database Aggregation', desc: 'Analytical databases precompute cumulative sums (and other aggregates) for columns they expect frequent range queries on — the database equivalent of prefix sums.' },
      { title: 'Image Processing (Summed Area Table)', desc: 'Computer vision uses 2D prefix sums (called "summed area tables") to compute the pixel average of any rectangular region in O(1). This powers fast blur filters and Haar features in face detection.' },
    ],
    commonMistakes: [
      { wrong: 'Off-by-one in prefix array indexing', explain: 'The prefix array has n+1 elements (prefix[0..n]). prefix[0]=0 represents "sum of first 0 elements". range_sum(L,R) = prefix[R+1] - prefix[L], NOT prefix[R] - prefix[L].' },
      { wrong: 'Computing range sum from scratch each time', explain: 'Building the prefix array takes O(n) once. Answering q queries then costs O(q) total. Without prefix sums, q queries each taking O(n) = O(nq) total — often catastrophically slower.' },
    ],
    videoId: "yuws7YK0Yng",
    videoTitle: "Prefix Sum in 4 Minutes | LeetCode Pattern",
    quiz: [
      { q: 'Given prefix = [0, 3, 4, 8, 9, 14], what is the sum of arr[2..4]?', options: ['prefix[4] - prefix[2] = 9 - 4 = 5', 'prefix[5] - prefix[2] = 14 - 4 = 10', 'prefix[4] - prefix[1] = 9 - 3 = 6', 'prefix[3] - prefix[1] = 8 - 3 = 5'], correct: 1, explanation: 'sum(L..R) = prefix[R+1] - prefix[L]. For L=2, R=4: prefix[5] - prefix[2] = 14 - 4 = 10. Check: arr = [3,1,4,1,5,...] so arr[2]+arr[3]+arr[4] = 4+1+5 = 10 ✓' },
      { q: 'What is the time complexity of building a prefix sum array of size n?', options: ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'], correct: 2, explanation: 'Building the prefix array requires a single left-to-right pass over the n-element input array, computing prefix[i] = prefix[i-1] + arr[i-1] at each step. Total: O(n).' },
      { q: 'You need to answer 1 million range sum queries on a 10,000-element array. What is the total cost with prefix sums vs without?', options: ['Same: O(n × q) either way', 'Without: O(n×q) = 10¹⁰; With: O(n + q) = ~10⁶ + 10,000', 'With prefix sums: O(n² + q)', 'Without: O(q log n)'], correct: 1, explanation: 'Without prefix sums: each query scans O(n) elements → O(n×q) = 10,000 × 1,000,000 = 10 billion operations. With prefix sums: O(n) to build + O(1) per query = ~1 million operations.' },
      { q: 'How does the "count subarrays with sum = k" problem use prefix sums?', options: ['It computes all prefix sums then sorts them', 'If prefix[j] - prefix[i] = k, then arr[i..j-1] sums to k — track seen prefix sums in a hash map', 'It computes running maximums instead of sums', 'It uses prefix sums only for preprocessing'], correct: 1, explanation: 'sum(arr[i..j]) = k ↔ prefix[j+1] - prefix[i] = k ↔ prefix[i] = prefix[j+1] - k. Track how many times each prefix sum value was seen. For each new prefix sum, the count of valid subarrays ending here = seen[current - k].' },
      { q: 'What is a "difference array" and how does it relate to prefix sums?', options: ['An array storing differences between elements', 'The inverse of prefix sums: encodes range updates as O(1) point changes, reconstructed with a prefix sum', 'A sorted version of the prefix sum array', 'The derivative of the prefix sum function'], correct: 1, explanation: 'A difference array enables O(1) range updates: to add v to arr[L..R], do diff[L]+=v and diff[R+1]-=v. Taking a prefix sum of diff reconstructs the updated array. It\'s the inverse operation of prefix sum.' },
      { q: 'What is the primary use of 2D prefix sums (summed area tables)?', options: ['Sorting a 2D matrix efficiently', 'Finding any rectangle\'s element sum in O(1) after O(mn) preprocessing', 'Transposing a matrix in O(1)', 'Finding the longest path in a grid'], correct: 1, explanation: '2D prefix sums allow any rectangular subgrid sum to be computed in O(1) using the inclusion-exclusion formula. This powers fast image blur filters, face detection features, and many computer vision algorithms.' },
    ],
  },

  'brute-force-to-optimal': {
    concept: {
      overview: `Every great algorithm was once a clunky O(n³) brute force. The story of algorithm design is the story of finding elegant structure that eliminates redundant work.

The pattern: start with brute force (correct but slow), profile to find the bottleneck, find an insight that eliminates the bottleneck, implement the faster version, prove correctness, repeat.

A classic example: "find the maximum subarray sum." Brute force: try all pairs (i,j) and sum arr[i..j] → O(n³). Optimization 1: precompute prefix sums, so each sum query is O(1) → O(n²). Insight: "I can extend a positive subarray, but should restart when the sum goes negative." This leads to Kadane's algorithm → O(n). Three refinement steps, from O(n³) to O(n).

This evolution pattern — brute force → precomputation → invariant insight → linear algorithm — is universal. You see it in Fibonacci (O(2ⁿ) → O(n) → O(log n)), in string matching (O(nm) → O(n+m) KMP), and in graph algorithms (O(V³) Floyd-Warshall for all-pairs from a nested-loop baseline).

Learning to recognize brute force bottlenecks and the insights that eliminate them is the core skill of algorithm design.`,
      keyPoints: [
        {
          title: 'Maximum Subarray: Three Levels',
          desc: 'O(n³): try all (i,j), sum each. O(n²): precompute prefix sums, sum(i,j)=O(1). O(n): Kadane\'s — extend if positive, restart if negative.',
          code: `# Level 1: O(n³) brute force
def max_subarray_brute(arr):
    best = arr[0]
    for i in range(len(arr)):
        for j in range(i, len(arr)):
            best = max(best, sum(arr[i:j+1]))
    return best

# Level 3: O(n) Kadane's algorithm
def max_subarray_kadane(arr):
    current = best = arr[0]
    for x in arr[1:]:
        current = max(x, current + x)  # extend or restart
        best = max(best, current)
    return best`,
        },
        {
          title: 'The Bottleneck Identification Loop',
          desc: 'Ask: "What is the most expensive repeated operation?" In O(n³) max subarray, it\'s recomputing the same subarray sums. Eliminate that with prefix sums → O(n²). Then ask again: "What\'s redundant now?" Redundant comparisons → Kadane\'s insight.',
        },
        {
          title: 'The Three Question Framework',
          desc: '1. Can I precompute something to avoid repeated work? (memoization, prefix sums, sorting). 2. Can I use a data structure to make a slow operation fast? (heap for min, hash map for O(1) lookup). 3. Is there a mathematical invariant that lets me skip cases? (Kadane\'s "negative running sum" insight).',
        },
      ],
    },
    steps: [
      { n: '1', label: 'Write Brute Force First', desc: 'Implement the simplest correct solution, even if O(n³) or worse. This gives you a reference to test against and forces you to understand the problem structure.' },
      { n: '2', label: 'Identify the Bottleneck', desc: 'Count operations: which nested loop or repeated operation dominates? For maximum subarray O(n³): the innermost sum() call on O(n) elements.' },
      { n: '3', label: 'Find the Redundancy', desc: 'What are you computing multiple times? For max subarray: sum(arr[i..j]) overlaps with sum(arr[i..j-1]). Precomputing fixes this → O(n²).' },
      { n: '4', label: 'Find the Key Insight', desc: 'Is there a property of the optimal solution? For max subarray: optimal can\'t include a subarray with negative prefix sum (you\'d do better starting fresh). This insight → Kadane\'s.' },
      { n: '5', label: 'Verify and Test', desc: 'Run the optimized version against the brute force on random inputs. They should always agree. Test edge cases: empty array, all negatives, single element.' },
    ],
    codeExamples: [
      {
        label: 'Three levels: two-sum (O(n²) → O(n))',
        complexity: 'O(n) with hash map',
        variant: 'default',
        code: `# Level 1: O(n²) — try every pair
def two_sum_brute(nums, target):
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]

# Level 2: O(n) — hash map for O(1) complement lookup
def two_sum_optimal(nums, target):
    seen = {}    # value → index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i

# Insight: instead of searching for the complement in O(n),
# store each number as we go and look it up in O(1).`,
      },
      {
        label: 'Fibonacci: O(2ⁿ) → O(n) → O(log n)',
        complexity: 'O(log n) with matrix exponentiation',
        variant: 'good',
        code: `# O(2^n): naive recursion
def fib_naive(n):
    if n <= 1: return n
    return fib_naive(n-1) + fib_naive(n-2)

# O(n): dynamic programming (memoize or tabulate)
def fib_dp(n):
    if n <= 1: return n
    a, b = 0, 1
    for _ in range(n-1):
        a, b = b, a + b
    return b

# O(log n): matrix exponentiation
# [fib(n+1)]   [1 1]^n   [1]
# [fib(n)  ] = [1 0]   × [0]
def matrix_mul(A, B):
    return [[A[0][0]*B[0][0] + A[0][1]*B[1][0],
             A[0][0]*B[0][1] + A[0][1]*B[1][1]],
            [A[1][0]*B[0][0] + A[1][1]*B[1][0],
             A[1][0]*B[0][1] + A[1][1]*B[1][1]]]`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Max subarray (brute)', value: 'O(n³)', color: 'text-red-400', note: 'Triple nested loop' },
        { case: 'Max subarray (prefix)', value: 'O(n²)', color: 'text-amber-400', note: 'Precomputed sums' },
        { case: 'Max subarray (Kadane)', value: 'O(n)', color: 'text-emerald-400', note: 'Invariant insight' },
        { case: 'Two-sum (brute)', value: 'O(n²)', color: 'text-amber-400', note: 'All pairs' },
        { case: 'Two-sum (hash map)', value: 'O(n)', color: 'text-emerald-400', note: 'O(1) complement lookup' },
      ],
      note: 'Most optimization steps follow the pattern: "what am I computing repeatedly that I could store?" or "what invariant lets me skip whole categories of cases?"',
    },
    realWorld: [
      { title: 'Compiler Optimization', desc: 'Compilers apply exactly this process to your code: identify repeated computations (common subexpression elimination), reorder operations (loop hoisting), and exploit invariants (dead code elimination).' },
      { title: 'Database Query Planning', desc: 'Database query optimizers take a "brute force" execution plan (nested loops for each join) and transform it using insights like index lookups, hash joins, and predicate pushdown to arrive at an optimal plan.' },
    ],
    commonMistakes: [
      { wrong: 'Jumping to optimization before getting a correct solution', right: 'Write brute force first, then optimize', explain: 'An optimized solution that\'s incorrect is useless. Write brute force first — it gives you a correctness oracle, forces you to understand the problem, and often reveals the structure of the optimization.' },
      { wrong: 'Stopping after the first optimization', explain: 'O(n²) → O(n log n) is good progress, but many problems have O(n) solutions waiting to be found with one more insight. Keep asking: "what\'s still redundant?"' },
    ],
    videoId: "N7kBg905XRY",
    videoTitle: "How to Optimize Coding Interview Solutions (Brute Force to Optimal)",
    quiz: [
      { q: 'What is the best strategy for solving a new algorithmic problem you\'ve never seen?', options: ['Guess the optimal algorithm immediately', 'Write a correct brute force first, then optimize by identifying redundancy', 'Look up the problem online', 'Use recursion with memoization for all problems'], correct: 1, explanation: 'Brute force first establishes correctness. Then you can profile, identify the bottleneck, and apply optimizations systematically. Jumping to optimization without correctness risks solving the wrong problem.' },
      { q: 'Kadane\'s algorithm achieves O(n) for maximum subarray using what key insight?', options: ['It sorts the array first', 'A subarray with a negative current sum should be abandoned — starting fresh is always better', 'It uses dynamic programming with O(n) space', 'It applies binary search to find the boundaries'], correct: 1, explanation: 'Kadane\'s insight: if the running sum of a subarray goes negative, any extension that includes it is worse than starting fresh from the next element. This lets us make O(1) decisions at each element.' },
      { q: 'The two-sum problem (find indices of two numbers summing to target) goes from O(n²) to O(n) using what technique?', options: ['Sorting + binary search', 'Hash map storing value → index, O(1) complement lookup', 'Two pointers on sorted array', 'Prefix sums'], correct: 1, explanation: 'For each element x, we need to find (target-x) in the array. Instead of scanning O(n) each time, store each element in a hash map (O(1) insert and lookup). Total: O(n) single pass.' },
      { q: 'What is the typical first optimization applied to a brute-force O(n³) subarray algorithm?', options: ['Use a heap to track maximums', 'Sort the array', 'Precompute prefix sums to make range sum queries O(1), reducing to O(n²)', 'Apply binary search within the inner loop'], correct: 2, explanation: 'The innermost operation (computing the sum of a subarray) is O(n) in brute force but O(1) with precomputed prefix sums. This reduces O(n³) to O(n²) without changing the outer loop structure.' },
      { q: 'Fibonacci goes from O(2ⁿ) naive to O(n) DP. What further insight achieves O(log n)?', options: ['Memoizing more values', 'Sorting the computation order', 'Matrix exponentiation: representing fib recurrence as a 2×2 matrix power, computed with fast exponentiation', 'Using the golden ratio formula'], correct: 2, explanation: 'The fib recurrence is linear: [F(n+1), F(n)] = M^n × [1, 0] where M = [[1,1],[1,0]]. Matrix exponentiation computes M^n in O(log n) multiplications using divide and conquer fast power.' },
      { q: 'What are the three main techniques for moving from brute force to optimal?', options: ['Add memoization, change the data structure, sort the input', 'Precompute/memoize, upgrade data structures for fast queries, find invariants that skip cases', 'Use parallel computing, caching, and indexing', 'Binary search, sorting, hashing'], correct: 1, explanation: 'The three standard optimization patterns: (1) Precompute/memoize to avoid redundant work. (2) Use better data structures (heap for min, hash map for lookup). (3) Find mathematical invariants that allow skipping entire cases (like Kadane\'s negative sum rule).' },
    ],
  },
};
