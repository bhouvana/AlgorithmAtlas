import type { LessonData } from '../../lessons/GenericLesson';

export const foundationsLessons: Record<string, LessonData> = {

  // ─────────────────────────────────────────────────────────────────────────
  'what-is-an-algorithm': {
    concept: {
      overview:
        'An algorithm is a finite, ordered set of well-defined instructions that takes some input, processes it through a sequence of steps, and produces a correct output. Every algorithm must eventually halt — infinite loops are not algorithms. The gap between an algorithm and a program is the gap between an idea and its expression in a particular language or machine.',
      keyPoints: [
        {
          title: 'Correctness',
          desc: 'The algorithm must produce the right answer for every valid input, including edge cases like empty lists or single elements. Correctness is usually proved by reasoning about invariants — conditions that remain true at each step.',
        },
        {
          title: 'Efficiency',
          desc: 'A correct but slow algorithm can be useless in practice. Efficiency is measured in time (how many operations?) and space (how much memory?). We express growth rates with Big O notation to compare algorithms independently of hardware.',
        },
        {
          title: 'Clarity',
          desc: 'A good algorithm can be understood, communicated, and translated into any programming language. Pseudocode strips away syntax details so we can focus on the logic. Clear algorithms are easier to prove correct and easier to optimize.',
        },
      ],
    },
    steps: [
      {
        n: '1',
        label: 'Understand the problem',
        desc: 'Read the problem carefully. Identify what is given (inputs) and what is required (outputs). Clarify ambiguous requirements — does "sort" mean ascending or descending? Are duplicates allowed?',
      },
      {
        n: '2',
        label: 'Define inputs and outputs',
        desc: 'State precisely what the algorithm accepts and what it must return. Specify constraints: integer range, list length, whether input is sorted. These constraints will guide your choice of approach.',
      },
      {
        n: '3',
        label: 'Devise the steps',
        desc: 'Write pseudocode or draw diagrams. Break the problem into subproblems. Consider brute-force first, then ask whether a smarter structure or observation leads to a faster solution.',
      },
      {
        n: '4',
        label: 'Trace through examples',
        desc: 'Run your steps on a small concrete example by hand. Try the normal case, the smallest possible input (empty list, n=0), and a worst-case scenario. Bugs found here cost nothing to fix.',
      },
      {
        n: '5',
        label: 'Analyze correctness',
        desc: 'Identify the loop invariant — the property that holds before and after each iteration. If the invariant plus the loop termination condition implies the correct answer, the algorithm is correct.',
      },
      {
        n: '6',
        label: 'Analyze efficiency and implement',
        desc: 'Count the dominant operations to get Big O time and space. If the complexity is acceptable, translate the pseudocode into your target language, then test it with unit tests including edge cases.',
      },
    ],
    codeExamples: [
      {
        label: 'Find the maximum value in a list',
        code:
'def find_max(items):\n' +
'    # Requires: items is a non-empty list\n' +
'    # Returns: the largest element\n' +
'    best = items[0]\n' +
'    for item in items[1:]:\n' +
'        if item > best:\n' +
'            best = item\n' +
'    return best\n' +
'\n' +
'print(find_max([3, 1, 4, 1, 5, 9, 2, 6]))  # 9',
        complexity: 'O(n) time, O(1) space',
        variant: 'good',
      },
      {
        label: 'Countdown — simple finite algorithm',
        code:
'def countdown(n):\n' +
'    # Requires: n >= 0\n' +
'    # Produces output, then terminates\n' +
'    while n > 0:\n' +
'        print(n)\n' +
'        n = n - 1\n' +
'    print("Go!")\n' +
'\n' +
'countdown(5)  # 5 4 3 2 1 Go!',
        complexity: 'O(n) time, O(1) space',
        variant: 'default',
      },
    ],
    complexity: {
      rows: [
        { case: 'find_max — time', value: 'O(n)', color: 'text-indigo-400', note: 'Must inspect every element once' },
        { case: 'find_max — space', value: 'O(1)', color: 'text-emerald-400', note: 'Only stores one variable (best)' },
        { case: 'Worst-case input', value: 'O(n)', color: 'text-indigo-400', note: 'No early exit — always scans full list' },
      ],
      note: 'The complexity of an algorithm depends on its approach, not just the problem. Sorting can be O(n log n) or O(n²) depending on the algorithm chosen.',
    },
    realWorld: [
      {
        title: 'GPS Route Planning',
        desc: "Navigation apps run Dijkstra's or A* algorithms to find the shortest path between two points on a road graph. The algorithm processes millions of nodes and edges in milliseconds thanks to efficient data structures.",
      },
      {
        title: 'Search Engine Indexing',
        desc: "Google's crawlers build inverted indexes mapping every word to the pages it appears on. Retrieving results for your query is then an algorithm that scores and ranks millions of entries in under 100 ms.",
      },
      {
        title: 'Recipe Following',
        desc: 'A cooking recipe is a perfect everyday algorithm: finite steps, specific inputs (ingredients, quantities), a defined output (dish), and an order that matters — you must boil water before adding pasta.',
      },
      {
        title: 'Music Recommendation',
        desc: 'Spotify and YouTube run collaborative-filtering algorithms that compare your listening history with millions of other users to compute a ranked list of songs you are likely to enjoy next.',
      },
    ],
    quiz: [
      {
        q: 'Which property is REQUIRED for a procedure to be called an algorithm?',
        options: [
          'It must be written in Python',
          'It must eventually terminate for all valid inputs',
          'It must use recursion',
          'It must run in O(n) time',
        ],
        correct: 1,
        explanation: 'Finiteness (guaranteed termination) is a core property. An infinite loop is not an algorithm. Language choice and complexity class are not requirements.',
      },
      {
        q: 'What is pseudocode used for?',
        options: [
          'It is a compiled language faster than C',
          'It obfuscates code for security',
          'It expresses algorithm logic without being tied to a specific language syntax',
          'It automatically generates unit tests',
        ],
        correct: 2,
        explanation: 'Pseudocode is informal notation that captures the logic of an algorithm. It helps you think and communicate without worrying about semicolons, types, or imports.',
      },
      {
        q: 'An algorithm that always produces the correct output for every valid input is said to be:',
        options: ['Efficient', 'Correct', 'Optimal', 'Deterministic'],
        correct: 1,
        explanation: 'Correctness means the algorithm satisfies its specification for all valid inputs. An algorithm can be correct but inefficient, or efficient but incorrect.',
      },
      {
        q: 'What is a loop invariant?',
        options: [
          'A variable that never changes its value inside a loop',
          'A condition that is true before and after each iteration of a loop, used to prove correctness',
          'A loop that runs in constant time',
          'A loop that has no break statements',
        ],
        correct: 1,
        explanation: 'A loop invariant is a property that holds before the first iteration and is preserved by each iteration. When the loop terminates, the invariant plus the exit condition together imply the algorithm produced the correct result.',
      },
      {
        q: 'Which of the following best describes the relationship between an algorithm and a program?',
        options: [
          'They are the same thing — every program is an algorithm',
          'An algorithm is the abstract logical idea; a program is one concrete expression of it in a specific language',
          'A program is always faster than the algorithm it implements',
          'An algorithm must be written in pseudocode, never in a real language',
        ],
        correct: 1,
        explanation: 'An algorithm is language-agnostic: it describes what to do and in what order. A program is the algorithm expressed in a particular programming language with its specific syntax and constructs.',
      },
      {
        q: 'Which step of algorithm design helps catch bugs at the lowest possible cost?',
        options: [
          'Writing unit tests after deployment',
          'Tracing through concrete examples by hand before writing any code',
          'Profiling the algorithm in production',
          'Compiling the pseudocode directly',
        ],
        correct: 1,
        explanation: 'Running the algorithm on small examples by hand — including edge cases — catches logic errors before any code is written. Fixing a design flaw in pseudocode takes seconds; fixing it after implementation can take hours.',
      },
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────
  'time-vs-space': {
    concept: {
      overview:
        'Time complexity measures how the number of operations grows as the input size n increases. Space complexity measures how much extra memory an algorithm needs beyond its input. The two are often in tension: you can frequently trade extra memory for faster runtime, or sacrifice speed to reduce memory usage.',
      keyPoints: [
        {
          title: 'Big O Notation',
          desc: 'Big O describes the upper bound on growth rate, ignoring constants and lower-order terms. O(n) means runtime grows linearly; O(n²) means quadratically. We focus on growth rate because it dominates for large n.',
        },
        {
          title: 'The Space-Time Tradeoff',
          desc: 'Caching (memoization) stores previously computed results in a table to avoid recomputation. This trades O(n) extra space for a dramatic speedup — Fibonacci goes from O(2^n) to O(n) time. Database indexes are the classic production example.',
        },
        {
          title: 'Drop Constants',
          desc: 'O(2n) and O(100n) are both written as O(n) because the constant factor is swamped by n at scale. What matters is whether the algorithm is linear, quadratic, logarithmic, etc. — the shape of the growth curve.',
        },
      ],
    },
    steps: [
      {
        n: '1',
        label: 'Count the dominant operations',
        desc: 'Identify the operation that runs the most. In a nested loop over an n-element list, the inner body runs n² times — that is the dominant cost. Assignments and comparisons outside the loop are negligible.',
      },
      {
        n: '2',
        label: 'Count space allocations',
        desc: 'Track every data structure you create whose size grows with n. A result list of size n costs O(n) space. A single accumulator variable costs O(1). Recursive call stacks also consume space — O(depth) frames.',
      },
      {
        n: '3',
        label: 'Identify the dominant term',
        desc: 'If an algorithm does n² work then n more work, the total is O(n² + n) = O(n²). The lower-order term vanishes at large n and is dropped. Only the fastest-growing term survives.',
      },
      {
        n: '4',
        label: 'Drop constants',
        desc: 'O(3n + 5) simplifies to O(n). The constant 3 and offset 5 do not change the growth rate. Modern CPUs can run a billion operations per second, so what kills you is when n doubles and your runtime quadruples.',
      },
      {
        n: '5',
        label: 'Express with Big O',
        desc: 'Choose the tightest class that fits: O(1), O(log n), O(n), O(n log n), O(n²), O(2^n), O(n!). Common classes, roughly in order from best to worst for large n.',
        code: 'O(1) < O(log n) < O(n) < O(n log n) < O(n^2) < O(2^n)',
      },
    ],
    codeExamples: [
      {
        label: 'Fibonacci — naive recursive (exponential time)',
        code:
'def fib_naive(n):\n' +
'    # Time: O(2^n)  Space: O(n) call stack\n' +
'    if n <= 1:\n' +
'        return n\n' +
'    return fib_naive(n - 1) + fib_naive(n - 2)\n' +
'\n' +
'# fib_naive(40) recalculates fib(2) over 100 million times!',
        complexity: 'O(2^n) time',
        variant: 'warn',
      },
      {
        label: 'Fibonacci — memoized (linear time, linear space tradeoff)',
        code:
'def fib_memo(n, cache={}):\n' +
'    # Time: O(n)  Space: O(n) for cache\n' +
'    if n in cache:\n' +
'        return cache[n]\n' +
'    if n <= 1:\n' +
'        return n\n' +
'    cache[n] = fib_memo(n - 1, cache) + fib_memo(n - 2, cache)\n' +
'    return cache[n]\n' +
'\n' +
'# fib_memo(40) runs in microseconds instead of seconds',
        complexity: 'O(n) time, O(n) space',
        variant: 'good',
      },
    ],
    complexity: {
      rows: [
        { case: 'fib_naive time', value: 'O(2^n)', color: 'text-red-400', note: 'Exponential — doubles with every increment of n' },
        { case: 'fib_memo time', value: 'O(n)', color: 'text-indigo-400', note: 'Each subproblem solved exactly once' },
        { case: 'fib_memo space', value: 'O(n)', color: 'text-indigo-400', note: 'Cache stores one entry per value 0..n' },
        { case: 'fib_iterative space', value: 'O(1)', color: 'text-emerald-400', note: 'Only two variables needed — best tradeoff overall' },
      ],
      note: 'The iterative Fibonacci solution achieves O(n) time AND O(1) space — sometimes you can have both, but memoization is the canonical space-for-time example.',
    },
    realWorld: [
      {
        title: 'Database Indexes',
        desc: 'A B-tree index on a database column uses O(n) extra disk space to enable O(log n) lookups instead of O(n) full-table scans. Every production database makes this space-for-time tradeoff.',
      },
      {
        title: 'Image Compression',
        desc: 'JPEG and PNG algorithms store compressed data using more CPU time during encoding but save enormous amounts of disk space and network bandwidth — a time-for-space tradeoff.',
      },
      {
        title: 'Web Caching (CDNs)',
        desc: 'Content delivery networks store copies of files on servers near users. Extra disk space is traded for dramatically lower response times and reduced load on origin servers.',
      },
      {
        title: 'Video Streaming',
        desc: 'Streaming services buffer (pre-load) video data into memory before playback. Extra RAM usage prevents mid-playback stalls — space is traded for smoother time performance.',
      },
    ],
    quiz: [
      {
        q: 'You have two algorithms for the same problem: Algorithm A takes O(n) time and O(n) space; Algorithm B takes O(n²) time and O(1) space. Which uses more memory but runs faster for large n?',
        options: ['Algorithm B', 'Algorithm A', 'Both are identical', 'Neither — it depends on the hardware'],
        correct: 1,
        explanation: 'Algorithm A uses O(n) space (more) but runs in O(n) time which is much faster than O(n²) for large n. This is the classic space-for-time tradeoff.',
      },
      {
        q: 'What does O(1) space complexity mean?',
        options: [
          'The algorithm uses exactly one byte of memory',
          'The algorithm uses a constant amount of extra memory regardless of input size',
          'The algorithm runs in constant time',
          'The algorithm has no loops',
        ],
        correct: 1,
        explanation: 'O(1) space means the extra memory used does not grow with the input size. A few variables are fine; creating an output array of size n would be O(n) space.',
      },
      {
        q: 'What is the space complexity of a recursive function that calls itself n times deep?',
        options: ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'],
        correct: 2,
        explanation: 'Each recursive call adds a stack frame. n nested calls means n frames on the call stack simultaneously, giving O(n) space. This is why deep recursion can cause stack overflow.',
      },
      {
        q: 'A nested loop where the outer loop runs n times and the inner loop also runs n times has what time complexity?',
        options: ['O(n)', 'O(2n)', 'O(n²)', 'O(log n)'],
        correct: 2,
        explanation: 'The inner body executes n × n = n² times in total. This is quadratic time — O(n²). Doubling n quadruples the runtime, which becomes prohibitive for large inputs.',
      },
      {
        q: 'Which Big O class describes binary search on a sorted array?',
        options: ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)'],
        correct: 1,
        explanation: 'Binary search halves the search space on every step. Starting from n elements: n → n/2 → n/4 → … → 1 takes at most log₂(n) steps. This is the canonical O(log n) algorithm.',
      },
      {
        q: 'What is the primary benefit of memoization from a complexity perspective?',
        options: [
          'It reduces space usage to O(1)',
          'It converts an exponential-time algorithm to polynomial time by storing and reusing computed subresults',
          'It eliminates the need for a base case in recursion',
          'It makes the algorithm deterministic',
        ],
        correct: 1,
        explanation: 'Memoization caches the result of each unique subproblem the first time it is computed. Future calls with the same arguments return instantly. Fibonacci drops from O(2^n) to O(n) — exponential to linear — at the cost of O(n) extra space.',
      },
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────
  'strings': {
    concept: {
      overview:
        'A string is a sequence of characters stored in contiguous memory, where each character is encoded as a number (ASCII for English, Unicode/UTF-8 for the full world of characters). In most languages strings are immutable — once created they cannot be modified in place, so every "modification" creates a new string.',
      keyPoints: [
        {
          title: 'Immutability',
          desc: 'Python, Java, and JavaScript strings cannot be changed after creation. s[0] = "X" raises an error in Python. To modify a string you must build a new one — often via a list of characters that you join at the end.',
        },
        {
          title: 'Character Encoding',
          desc: 'ASCII maps 128 characters to numbers 0-127. Unicode extends this to over 140,000 characters covering every human writing system. UTF-8 is the dominant encoding on the web and stores ASCII characters in 1 byte, others in 2-4 bytes.',
        },
        {
          title: 'Common Operations',
          desc: 'Index access is O(1). Slicing, searching (find/index), and comparisons are O(n). Concatenating inside a loop is O(n²) — join a list instead. Splitting on a delimiter and joining are both O(n).',
          code: "result = ''.join(chars)  # O(n) — not O(n²)",
        },
      ],
    },
    steps: [
      {
        n: '1',
        label: 'Access a character by index',
        desc: "Characters are stored contiguously so index access is O(1) — the runtime jumps directly to position i in memory. s[0] is the first character, s[-1] is the last (Python). Indexing beyond the bounds raises an error.",
        code: 's = "hello"  =>  s[1] == "e"  (O(1))',
      },
      {
        n: '2',
        label: 'Slicing creates a copy',
        desc: "A slice s[i:j] allocates a brand-new string containing characters i through j-1. This costs O(j-i) time and space. Because strings are immutable, you cannot get a zero-copy view like some languages allow for byte arrays.",
        code: "s[1:4]  =>  'ell'  (new object, O(k) where k = j-i)",
      },
      {
        n: '3',
        label: 'Concatenation creates a new string',
        desc: "s + t allocates a new string of length len(s)+len(t) and copies both. Doing this in a loop n times gives O(1+2+...+n) = O(n²) total work. Always collect parts in a list, then join once.",
        code: "result = ''.join([s1, s2, s3])  # one allocation",
      },
      {
        n: '4',
        label: 'Searching is a linear scan',
        desc: "s.find(sub) scans left to right comparing sub at each position. Worst case O(n·m) where n=len(s) and m=len(sub). KMP and Rabin-Karp algorithms solve this in O(n+m) but are rarely needed in practice.",
        code: '"banana".find("an")  =>  1  (scans left to right)',
      },
      {
        n: '5',
        label: 'Comparison is character by character',
        desc: "s == t compares characters one by one until a mismatch or end. Worst case O(min(len(s),len(t))). Lexicographic ordering (for sorting strings) works the same way.",
      },
    ],
    codeExamples: [
      {
        label: 'Check if a string is a palindrome',
        code:
'def is_palindrome(s):\n' +
'    # Time: O(n)  Space: O(1) (two-pointer, no copy)\n' +
'    left, right = 0, len(s) - 1\n' +
'    while left < right:\n' +
'        if s[left] != s[right]:\n' +
'            return False\n' +
'        left += 1\n' +
'        right -= 1\n' +
'    return True\n' +
'\n' +
'print(is_palindrome("racecar"))  # True\n' +
'print(is_palindrome("hello"))    # False',
        complexity: 'O(n) time, O(1) space',
        variant: 'good',
      },
      {
        label: 'Reverse a string efficiently using a list',
        code:
'def reverse_string(s):\n' +
'    # Strings are immutable — collect chars, then join\n' +
'    # Time: O(n)  Space: O(n)\n' +
'    chars = list(s)          # convert to mutable list\n' +
'    left, right = 0, len(chars) - 1\n' +
'    while left < right:\n' +
'        chars[left], chars[right] = chars[right], chars[left]\n' +
'        left += 1\n' +
'        right -= 1\n' +
'    return "".join(chars)    # one allocation\n' +
'\n' +
'print(reverse_string("algorithm"))  # "mhtirogla"',
        complexity: 'O(n) time, O(n) space',
        variant: 'default',
      },
    ],
    complexity: {
      rows: [
        { case: 'Index access s[i]', value: 'O(1)', color: 'text-emerald-400', note: 'Direct memory offset — constant time' },
        { case: 'Search / find', value: 'O(n)', color: 'text-indigo-400', note: 'Scans the string linearly' },
        { case: 'Slice s[i:j]', value: 'O(k)', color: 'text-indigo-400', note: 'k = j-i characters copied to new string' },
        { case: 'Concatenation in loop', value: 'O(n²)', color: 'text-orange-400', note: 'Each += copies the growing string again' },
      ],
      note: "Use ''.join(parts) instead of repeated concatenation. The difference between O(n) and O(n²) is enormous — for n=10,000 it's 10,000× slower.",
    },
    realWorld: [
      {
        title: 'Text Editors',
        desc: 'Editors like VS Code use rope data structures instead of plain strings so that insertions in the middle of a large file are O(log n) instead of O(n). Immutable strings make naive editing very expensive.',
      },
      {
        title: 'DNA Sequencing',
        desc: 'A genome is a string of billions of A, C, G, T characters. Bioinformatics algorithms like Smith-Waterman find matching subsequences and mutations using string-matching techniques at massive scale.',
      },
      {
        title: 'URL Parsing',
        desc: 'Web servers parse URLs by splitting on "/" and "?" delimiters, then decoding percent-encoded characters. This is pure string manipulation running millions of times per second on busy servers.',
      },
      {
        title: 'Search and Replace',
        desc: 'Regular expressions compile a pattern into a state machine that can find and replace substrings in O(n) time. Every code editor, grep, and sed command relies on efficient string search algorithms.',
      },
    ],
    quiz: [
      {
        q: 'What is the time complexity of building a string by concatenating n single-character strings one at a time using "+"?',
        options: ['O(1)', 'O(n)', 'O(n²)', 'O(n log n)'],
        correct: 2,
        explanation: "Each concatenation copies the entire string so far. Sizes are 1+2+3+...+n = n(n+1)/2 = O(n²). Use ''.join(list) to avoid this.",
      },
      {
        q: 'In Python, what does "immutable string" mean?',
        options: [
          'The string cannot be assigned to a variable',
          'The string cannot be printed',
          'The characters in the string cannot be changed after the string is created',
          'The string can only contain lowercase letters',
        ],
        correct: 2,
        explanation: 'Immutable means the object\'s state cannot change. s[0] = "X" raises a TypeError in Python. To "modify" a string you build a new one.',
      },
      {
        q: 'Which approach to checking a palindrome uses O(1) extra space?',
        options: [
          'Reverse the string and compare with ==',
          'Use two pointers moving from both ends toward the center',
          'Convert to a list and reverse in place',
          'Split the string into a set of characters',
        ],
        correct: 1,
        explanation: "The two-pointer technique only uses two integer variables regardless of string length — O(1) space. Reversing creates a copy (O(n) space).",
      },
      {
        q: 'Why is concatenating strings inside a loop with "+" considered an antipattern in Python and Java?',
        options: [
          'The "+" operator is not defined for strings',
          'Each concatenation allocates a brand-new string copying all prior characters, making the total work O(n²)',
          'It produces incorrect results when strings contain special characters',
          'Loops are not allowed to contain string operations',
        ],
        correct: 1,
        explanation: 'Because strings are immutable, each "+" must allocate a new string and copy both operands. After n concatenations the total bytes copied are 1+2+…+n = O(n²). Collect parts in a list and call join() once for O(n) total work.',
      },
      {
        q: 'What encoding system covers the full range of human written characters, including emoji and non-Latin scripts?',
        options: ['ASCII', 'UTF-8 / Unicode', 'Base64', 'ISO 8859-1'],
        correct: 1,
        explanation: 'ASCII only covers 128 characters (English letters, digits, punctuation). Unicode defines over 140,000 code points covering every writing system. UTF-8 is the dominant encoding that stores Unicode characters using 1–4 bytes per character.',
      },
      {
        q: 'What is the time complexity of the naive substring search (checking every position in s for pattern p)?',
        options: ['O(n)', 'O(n + m)', 'O(n · m)', 'O(m²)'],
        correct: 2,
        explanation: 'The naive algorithm tries aligning p at each of the n positions in s and compares up to m characters. Worst case is O(n · m) — e.g., searching "aaaa…a" for "aaa…ab". Algorithms like KMP achieve O(n + m).',
      },
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────
  'linked-lists': {
    concept: {
      overview:
        'A linked list is a linear data structure made of nodes, where each node holds a value and a pointer (reference) to the next node. Unlike arrays, nodes do not need to live in contiguous memory — they can be scattered anywhere in the heap and connected through pointers. This makes inserting and deleting at the head O(1), while random access costs O(n).',
      keyPoints: [
        {
          title: 'Dynamic Size',
          desc: 'Arrays have a fixed capacity or must be reallocated when full. Linked lists grow and shrink at runtime by simply allocating or deallocating individual nodes. No pre-sizing or copying needed.',
        },
        {
          title: 'O(1) Head Insert',
          desc: 'Prepending an element just creates a new node and makes it point to the old head — two pointer assignments regardless of list length. Array prepend is O(n) because every existing element must shift right.',
          code: 'new_node.next = head; head = new_node',
        },
        {
          title: 'No Random Access',
          desc: 'To read element at index i you must follow i next-pointers starting from head — O(n). There is no arithmetic shortcut like arrays. This makes linked lists a poor choice when you need frequent index-based lookups.',
        },
      ],
    },
    steps: [
      {
        n: '1',
        label: 'Create the head node',
        desc: 'A linked list starts with a head pointer. If the list is empty, head is None/null. Every operation begins by checking whether head is None to handle the empty-list edge case.',
        code: 'class Node:\n    def __init__(self, val):\n        self.val = val\n        self.next = None',
      },
      {
        n: '2',
        label: 'Traverse by following next pointers',
        desc: 'Start at head and move to current.next repeatedly until current is None. This visits every node once in O(n) time. You cannot jump to the middle directly — you must walk there.',
        code: 'current = head\nwhile current:\n    print(current.val)\n    current = current.next',
      },
      {
        n: '3',
        label: 'Insert at head — O(1)',
        desc: 'Create a new node, set its next pointer to the current head, then update head to point to the new node. Two assignments — constant time regardless of list length.',
        code: 'new_node.next = head; head = new_node',
      },
      {
        n: '4',
        label: 'Insert in the middle or tail — O(n)',
        desc: 'Walk to the node just before the target position, then redirect pointers: new_node.next = current.next; current.next = new_node. Finding the position takes O(n) time.',
      },
      {
        n: '5',
        label: 'Delete a node — O(n)',
        desc: 'Walk to the node before the target, then set predecessor.next = target.next, bypassing the target node. Deleting the head is O(1): head = head.next. Always handle the empty-list and single-node cases.',
        code: 'predecessor.next = target.next  # bypasses target',
      },
    ],
    codeExamples: [
      {
        label: 'Node class and insert-at-head',
        code:
'class Node:\n' +
'    def __init__(self, val):\n' +
'        self.val = val\n' +
'        self.next = None\n' +
'\n' +
'class LinkedList:\n' +
'    def __init__(self):\n' +
'        self.head = None\n' +
'\n' +
'    def prepend(self, val):          # O(1)\n' +
'        node = Node(val)\n' +
'        node.next = self.head\n' +
'        self.head = node\n' +
'\n' +
'    def to_list(self):               # O(n)\n' +
'        result = []\n' +
'        cur = self.head\n' +
'        while cur:\n' +
'            result.append(cur.val)\n' +
'            cur = cur.next\n' +
'        return result\n' +
'\n' +
'lst = LinkedList()\n' +
'lst.prepend(3); lst.prepend(2); lst.prepend(1)\n' +
'print(lst.to_list())  # [1, 2, 3]',
        complexity: 'O(1) prepend',
        variant: 'good',
      },
      {
        label: 'Find the middle node (slow-fast pointer trick)',
        code:
'def find_middle(head):\n' +
'    # slow moves 1 step, fast moves 2 steps\n' +
'    # when fast reaches end, slow is at middle\n' +
'    slow = head\n' +
'    fast = head\n' +
'    while fast and fast.next:\n' +
'        slow = slow.next\n' +
'        fast = fast.next.next\n' +
'    return slow   # middle node\n' +
'\n' +
'# Works in O(n) time, O(1) space — no length needed',
        complexity: 'O(n) time, O(1) space',
        variant: 'default',
      },
    ],
    complexity: {
      rows: [
        { case: 'Access by index', value: 'O(n)', color: 'text-indigo-400', note: 'Must follow n pointers from head' },
        { case: 'Insert at head', value: 'O(1)', color: 'text-emerald-400', note: 'Just redirect head pointer' },
        { case: 'Insert at tail / middle', value: 'O(n)', color: 'text-indigo-400', note: 'Must traverse to find position' },
        { case: 'Search / delete', value: 'O(n)', color: 'text-indigo-400', note: 'Linear scan required' },
      ],
      note: 'A doubly linked list adds a prev pointer to each node, enabling O(1) deletion when you already have a reference to the node — useful in LRU cache implementations.',
    },
    realWorld: [
      {
        title: 'Browser History',
        desc: 'Your browser\'s back/forward history is a doubly linked list. Visiting a new page appends to the tail; pressing Back follows the prev pointer. This gives O(1) navigation in both directions.',
      },
      {
        title: 'Undo / Redo in Editors',
        desc: 'Text editors store edit operations as a linked list. Undo pops from the head; redo re-applies from the redo stack. The structure grows dynamically with each edit without pre-allocating memory.',
      },
      {
        title: 'Music Playlists',
        desc: 'A circular linked list models a looping playlist naturally. The last song\'s next pointer points back to the first. Skipping to the next track is O(1).',
      },
      {
        title: 'OS Memory Allocation',
        desc: 'Operating system free-list allocators track available memory blocks as a linked list of (address, size) pairs. Allocating memory removes a block; freeing adds one back — both O(1) at the correct position.',
      },
    ],
    quiz: [
      {
        q: 'Why is accessing the element at index i in a linked list O(n)?',
        options: [
          'Linked list nodes are not sorted',
          'You must follow next pointers from the head one at a time to reach position i',
          'The list must be copied before access',
          'Pointer arithmetic is slower than array indexing',
        ],
        correct: 1,
        explanation: 'There is no way to jump to position i directly. You start at head and advance i times. This takes O(i) steps, which is O(n) in the worst case.',
      },
      {
        q: 'What is the key advantage of a linked list over an array for insertions?',
        options: [
          'Linked lists use less memory overall',
          'Linked list elements can be accessed in O(1)',
          'Inserting at the head is O(1) — no shifting of elements required',
          'Linked lists support binary search',
        ],
        correct: 2,
        explanation: 'Prepending to a linked list is O(1) — just redirect the head pointer. Array prepend is O(n) because every existing element must shift one position to the right.',
      },
      {
        q: 'What is a doubly linked list?',
        options: [
          'A list with two separate head pointers',
          'A list where each node has both a next and a prev pointer',
          'Two singly linked lists joined together',
          'A list that can hold two values per node',
        ],
        correct: 1,
        explanation: 'A doubly linked list adds a prev pointer to each node so you can traverse in both directions. This enables O(1) deletion when you hold a reference to the node — critical for LRU caches.',
      },
      {
        q: 'What is the slow-and-fast pointer (Floyd\'s) technique used for in linked lists?',
        options: [
          'Sorting nodes in O(n log n) time',
          'Detecting cycles and finding the middle node by advancing two pointers at different speeds',
          'Reversing the list in O(1) space',
          'Merging two sorted linked lists',
        ],
        correct: 1,
        explanation: 'The slow pointer advances one step at a time; the fast pointer advances two. If there is a cycle, fast will lap slow and they will meet. If there is no cycle, fast reaches the end while slow is at the midpoint. Both operations are O(n) time and O(1) space.',
      },
      {
        q: 'How do you delete a node from a singly linked list when you have a reference to the node that comes just before it?',
        options: [
          'Set the target node\'s value to null',
          'Set predecessor.next = target.next, bypassing the target node',
          'Traverse the list again from head to find the predecessor',
          'Swap the target with the tail, then remove the tail',
        ],
        correct: 1,
        explanation: 'Deletion in a singly linked list is a pointer redirect: set predecessor.next to skip over the target and point to target.next. The target node becomes unreachable and is garbage-collected. This is O(1) once you have the predecessor reference.',
      },
      {
        q: 'What is the space overhead per element in a singly linked list compared to an array?',
        options: [
          'No overhead — both use the same memory per element',
          'One extra pointer per node (next), storing the address of the following node',
          'Two extra pointers per node (next and prev)',
          'A full copy of the list stored in a backup array',
        ],
        correct: 1,
        explanation: 'Each linked list node must store the data value plus a next pointer (typically 8 bytes on a 64-bit system). Arrays store only the values contiguously with no pointer overhead, making arrays more memory-efficient when the element count is known in advance.',
      },
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────
  'stacks': {
    concept: {
      overview:
        'A stack is a Last In, First Out (LIFO) data structure where all insertions and removals happen at the same end, called the top. Think of a stack of plates: you add a new plate on top and always remove the top plate first. This simple constraint makes stacks perfect for any problem where you need to process things in reverse order of their arrival.',
      keyPoints: [
        {
          title: 'LIFO Order',
          desc: 'The last element pushed is always the first one popped. This is useful whenever you need to reverse a sequence or "undo" the most recent action — the most recent push is always on top.',
          code: 'push(1) push(2) push(3) => pop()=3 pop()=2 pop()=1',
        },
        {
          title: 'O(1) Operations',
          desc: 'Push (add to top) and pop (remove from top) are both O(1) because no shifting or searching is needed. The top is always directly accessible. This is why the call stack in your CPU can handle millions of function calls efficiently.',
        },
        {
          title: 'The Call Stack',
          desc: 'Your programming language runtime uses a stack for function calls. When you call a function, a frame is pushed containing local variables and the return address. When the function returns, its frame is popped. Stack overflow occurs when too many frames accumulate.',
        },
      ],
    },
    steps: [
      {
        n: '1',
        label: 'Push — add element to the top',
        desc: 'Append the new element to the end of the underlying list (which represents the top of the stack). This is O(1) amortized for a dynamic array — no shifting required.',
        code: 'stack.append(item)  # top is the end of the list',
      },
      {
        n: '2',
        label: 'Pop — remove and return the top element',
        desc: 'Remove and return the last element of the underlying list. Raises an error (or returns a sentinel) if the stack is empty. Always check IsEmpty before popping to avoid runtime errors.',
        code: 'item = stack.pop()  # O(1), removes from end',
      },
      {
        n: '3',
        label: 'Peek — view top without removing',
        desc: 'Read the last element without modifying the stack. Useful when you need to look at what is on top before deciding whether to pop it — common in expression parsers and bracket matchers.',
        code: 'top = stack[-1]  # read last element, no removal',
      },
      {
        n: '4',
        label: 'IsEmpty check',
        desc: 'Check whether the stack has any elements before popping. Popping an empty stack is a runtime error. Many algorithms loop "while stack is not empty" as the exit condition.',
        code: 'if not stack:  # evaluates to True when list is empty',
      },
      {
        n: '5',
        label: 'Dynamic growth',
        desc: 'Python lists (and most dynamic arrays) double their capacity when full, so push stays O(1) amortized. Fixed-size arrays require a size check and error if the stack is full (stack overflow in bounded systems).',
      },
    ],
    codeExamples: [
      {
        label: 'Stack using a Python list — push, pop, peek',
        code:
'class Stack:\n' +
'    def __init__(self):\n' +
'        self._data = []\n' +
'\n' +
'    def push(self, item):    # O(1) amortized\n' +
'        self._data.append(item)\n' +
'\n' +
'    def pop(self):           # O(1)\n' +
'        if self.is_empty():\n' +
'            raise IndexError("pop from empty stack")\n' +
'        return self._data.pop()\n' +
'\n' +
'    def peek(self):          # O(1)\n' +
'        if self.is_empty():\n' +
'            raise IndexError("peek at empty stack")\n' +
'        return self._data[-1]\n' +
'\n' +
'    def is_empty(self):\n' +
'        return len(self._data) == 0\n' +
'\n' +
's = Stack()\n' +
's.push(10); s.push(20); s.push(30)\n' +
'print(s.pop())   # 30\n' +
'print(s.peek())  # 20',
        complexity: 'O(1) push/pop/peek',
        variant: 'good',
      },
      {
        label: 'Balanced brackets checker using a stack',
        code:
'def is_balanced(s):\n' +
'    # Classic stack application: O(n) time, O(n) space\n' +
'    stack = []\n' +
'    pairs = {")": "(", "]": "[", "}": "{"}\n' +
'    for ch in s:\n' +
'        if ch in "([{":\n' +
'            stack.append(ch)\n' +
'        elif ch in ")]}":\n' +
'            if not stack or stack[-1] != pairs[ch]:\n' +
'                return False\n' +
'            stack.pop()\n' +
'    return len(stack) == 0\n' +
'\n' +
'print(is_balanced("({[]})"))  # True\n' +
'print(is_balanced("([)]"))    # False',
        complexity: 'O(n) time, O(n) space',
        variant: 'default',
      },
    ],
    complexity: {
      rows: [
        { case: 'Push', value: 'O(1)', color: 'text-emerald-400', note: 'Append to end — no shifting' },
        { case: 'Pop', value: 'O(1)', color: 'text-emerald-400', note: 'Remove from end — no shifting' },
        { case: 'Peek', value: 'O(1)', color: 'text-emerald-400', note: 'Read last element without removal' },
        { case: 'Space', value: 'O(n)', color: 'text-indigo-400', note: 'Grows linearly with number of elements pushed' },
      ],
      note: 'All core stack operations are O(1). The space cost is O(n) because you must store each element. This makes stacks extremely efficient for problems that fit the LIFO pattern.',
    },
    realWorld: [
      {
        title: 'Function Call Stack',
        desc: 'Every time you call a function, the runtime pushes a stack frame with local variables and the return address. When the function returns, the frame is popped. Deep recursion can exhaust the stack — hence "stack overflow".',
      },
      {
        title: 'Undo Operations',
        desc: 'Text editors push each change onto an undo stack. Pressing Ctrl+Z pops the most recent action and reverses it. The LIFO order ensures you always undo the most recent change first.',
      },
      {
        title: 'Browser Back Button',
        desc: 'As you navigate, each visited URL is pushed onto a history stack. Pressing Back pops the current page and goes to the previous one. This is why you cannot randomly jump to the 5th page back without going through 1, 2, 3, 4.',
      },
      {
        title: 'Expression Evaluation',
        desc: 'Compilers and calculators use stacks to evaluate arithmetic expressions. Operands are pushed; when an operator is encountered, two operands are popped, the result computed, and pushed back. Shunting-yard algorithm uses this pattern.',
      },
    ],
    quiz: [
      {
        q: 'What does LIFO stand for and what does it mean for a stack?',
        options: [
          'Last Index, First Out — the last index is accessed first',
          'Last In, First Out — the most recently pushed element is the first to be popped',
          'Linear Input, Fixed Output — output is always the same size',
          'Linked Index, Forward Order — elements are linked in order',
        ],
        correct: 1,
        explanation: 'LIFO = Last In, First Out. The element pushed most recently sits on top and will be the next one popped. This is the defining property of a stack.',
      },
      {
        q: 'Which operation adds an element to a stack?',
        options: ['enqueue', 'push', 'insert', 'append_front'],
        correct: 1,
        explanation: 'The standard term for adding an element to the top of a stack is "push". Removing is "pop". These terms come from the physical analogy of pushing plates onto a spring-loaded dispenser.',
      },
      {
        q: 'What causes a "stack overflow" error in programming?',
        options: [
          'Pushing more data than the OS allows onto the heap',
          'Using a loop instead of recursion',
          'The call stack running out of space due to too many nested function calls (often infinite recursion)',
          'Accessing a negative index',
        ],
        correct: 2,
        explanation: 'The call stack has a fixed maximum depth (typically 1,000-10,000 frames). Infinite or very deep recursion keeps pushing frames until the stack is exhausted, causing a stack overflow error.',
      },
      {
        q: 'What is the "peek" operation on a stack?',
        options: [
          'Remove and return the top element',
          'Check whether the stack is empty',
          'Read the top element without removing it',
          'Insert an element below the current top',
        ],
        correct: 2,
        explanation: 'Peek (also called "top") lets you inspect the most recently pushed element without modifying the stack. It is O(1) and commonly used when the algorithm needs to look before deciding whether to pop.',
      },
      {
        q: 'Which problem is a classic application of a stack?',
        options: [
          'Finding the shortest path in a graph',
          'Checking that parentheses/brackets are balanced in an expression',
          'Sorting a list of numbers',
          'Counting occurrences of words in a document',
        ],
        correct: 1,
        explanation: 'Bracket matching is the textbook stack problem: push every opening bracket; when a closing bracket is seen, pop and verify it matches. If the stack is empty at the end, all brackets are balanced. The LIFO order naturally pairs the most recent open bracket with the next closing bracket.',
      },
      {
        q: 'What is the amortized time complexity of push on a dynamic-array-backed stack?',
        options: ['O(n) always', 'O(log n)', 'O(1) amortized', 'O(n²)'],
        correct: 2,
        explanation: 'Most pushes are O(1) — append to the end. Occasionally the array must double in capacity and copy all elements (O(n)), but this doubling happens so rarely that the average cost per push over any sequence of n pushes is O(1) amortized.',
      },
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────
  'queues': {
    concept: {
      overview:
        'A queue is a First In, First Out (FIFO) data structure where elements are added at the back (enqueue) and removed from the front (dequeue). Think of a checkout line at a supermarket: the first person to join the line is the first person served. Queues are fundamental to scheduling, buffering, and breadth-first graph traversal.',
      keyPoints: [
        {
          title: 'FIFO Order',
          desc: 'The first element enqueued is the first one dequeued. This ensures fairness and ordering — requests are handled in the order they arrive. Contrast with a stack where the most recent item wins.',
          code: 'enqueue(1,2,3) => dequeue()=1, dequeue()=2, dequeue()=3',
        },
        {
          title: 'Use collections.deque',
          desc: 'Python lists can simulate a queue but list.pop(0) is O(n) because all elements shift left. collections.deque supports O(1) popleft() and append(). Always use deque for queues in Python.',
          code: 'from collections import deque; q = deque()',
        },
        {
          title: 'Variants: Deque and Priority Queue',
          desc: 'A deque (double-ended queue) allows O(1) add/remove at both ends. A priority queue dequeues the highest-priority element rather than the oldest — implemented with a heap and used in Dijkstra\'s algorithm.',
        },
      ],
    },
    steps: [
      {
        n: '1',
        label: 'Enqueue — add element to the back',
        desc: 'Append the new element to the back (right) of the deque. This is O(1). In a circular array implementation, the tail pointer advances by one position (modulo capacity).',
        code: 'q.append(item)  # adds to back, O(1)',
      },
      {
        n: '2',
        label: 'Dequeue — remove element from the front',
        desc: 'Remove and return the element at the front (left) of the deque. O(1) with collections.deque. Raises an error if the queue is empty. Always check before dequeuing.',
        code: 'item = q.popleft()  # removes from front, O(1)',
      },
      {
        n: '3',
        label: 'Peek front',
        desc: 'Look at the front element without removing it. With a deque this is q[0]. Useful in BFS when you need to inspect the next node before deciding to process it.',
        code: 'front = q[0]  # read only, O(1)',
      },
      {
        n: '4',
        label: 'IsEmpty check',
        desc: 'Check whether any elements remain before dequeuing. An empty deque evaluates to False in Python. Many BFS and simulation loops run "while q:" to process all enqueued elements.',
        code: 'while q:  # loop until queue is empty',
      },
      {
        n: '5',
        label: 'Handle wrap-around in circular queues',
        desc: 'In fixed-size circular queue arrays, the front and back pointers wrap around using modular arithmetic. When back reaches the end of the array it wraps to index 0, reusing freed space from dequeued elements.',
        code: 'back = (back + 1) % capacity  # wrap around',
      },
    ],
    codeExamples: [
      {
        label: 'Queue using collections.deque — enqueue and dequeue',
        code:
'from collections import deque\n' +
'\n' +
'class Queue:\n' +
'    def __init__(self):\n' +
'        self._data = deque()\n' +
'\n' +
'    def enqueue(self, item):    # O(1)\n' +
'        self._data.append(item)\n' +
'\n' +
'    def dequeue(self):          # O(1)\n' +
'        if self.is_empty():\n' +
'            raise IndexError("dequeue from empty queue")\n' +
'        return self._data.popleft()\n' +
'\n' +
'    def peek(self):             # O(1)\n' +
'        return self._data[0]\n' +
'\n' +
'    def is_empty(self):\n' +
'        return len(self._data) == 0\n' +
'\n' +
'q = Queue()\n' +
'q.enqueue("Alice"); q.enqueue("Bob"); q.enqueue("Carol")\n' +
'print(q.dequeue())  # "Alice"  (first in, first out)\n' +
'print(q.peek())     # "Bob"',
        complexity: 'O(1) enqueue/dequeue',
        variant: 'good',
      },
      {
        label: 'BFS level-order traversal of a binary tree using a queue',
        code:
'from collections import deque\n' +
'\n' +
'def level_order(root):\n' +
'    # Visit nodes level by level: O(n) time, O(n) space\n' +
'    if not root:\n' +
'        return []\n' +
'    result = []\n' +
'    q = deque([root])\n' +
'    while q:\n' +
'        node = q.popleft()\n' +
'        result.append(node.val)\n' +
'        if node.left:  q.append(node.left)\n' +
'        if node.right: q.append(node.right)\n' +
'    return result\n' +
'\n' +
'# The queue ensures nodes are processed in arrival order (FIFO)',
        complexity: 'O(n) time, O(n) space',
        variant: 'default',
      },
    ],
    complexity: {
      rows: [
        { case: 'Enqueue', value: 'O(1)', color: 'text-emerald-400', note: 'Append to back of deque — constant time' },
        { case: 'Dequeue', value: 'O(1)', color: 'text-emerald-400', note: 'Remove from front of deque — constant time' },
        { case: 'Dequeue with list.pop(0)', value: 'O(n)', color: 'text-orange-400', note: 'Avoid! Every element shifts left by one' },
        { case: 'Space', value: 'O(n)', color: 'text-indigo-400', note: 'Stores all currently enqueued elements' },
      ],
      note: 'Always use collections.deque in Python for queue operations. list.pop(0) looks innocent but is O(n) and will bottleneck any algorithm that dequeues frequently.',
    },
    realWorld: [
      {
        title: 'Print Queue',
        desc: 'When multiple users send documents to a shared printer, jobs enter a queue and are printed in order. FIFO ensures fairness — the first document submitted is the first printed.',
      },
      {
        title: 'CPU Scheduling',
        desc: 'Operating systems use queues (and priority queues) to schedule processes. A basic round-robin scheduler cycles through a queue of runnable processes, giving each a time slice in order.',
      },
      {
        title: 'BFS Graph Traversal',
        desc: 'Breadth-first search uses a queue to explore a graph level by level. The queue ensures nodes are visited in order of their distance from the source — critical for finding shortest paths in unweighted graphs.',
      },
      {
        title: 'Message Queues',
        desc: 'Systems like RabbitMQ and AWS SQS let microservices communicate asynchronously. Producers enqueue messages; consumers dequeue and process them at their own pace, decoupling the two services.',
      },
    ],
    quiz: [
      {
        q: 'What does FIFO mean?',
        options: [
          'First Index, Fixed Output',
          'Fast Input, Fast Output',
          'First In, First Out — the earliest enqueued element is dequeued first',
          'Forward Iteration, Forward Output',
        ],
        correct: 2,
        explanation: 'FIFO = First In, First Out. The element waiting longest at the front is served first, just like a checkout line. This is the defining property of a queue.',
      },
      {
        q: 'In a queue, where do you add new elements?',
        options: ['The front', 'The back (rear/tail)', 'The middle', 'Anywhere — order does not matter'],
        correct: 1,
        explanation: "New elements are enqueued at the back. Elements are dequeued from the front. This separation of addition point and removal point is what enforces FIFO order.",
      },
      {
        q: 'What is a circular queue and why is it useful?',
        options: [
          'A queue shaped like a circle in memory — purely aesthetic',
          'A queue whose elements wrap around a fixed-size array, reusing space freed by dequeued elements',
          'A queue that loops back to the front after reaching the maximum size, discarding old elements',
          'A doubly linked list used as a queue',
        ],
        correct: 1,
        explanation: 'A circular queue uses modular arithmetic to wrap the head and tail pointers around a fixed-size array. Freed slots (from dequeued items) are reused, avoiding the need to shift elements or allocate new memory.',
      },
      {
        q: 'Why should you use collections.deque instead of a plain list when implementing a queue in Python?',
        options: [
          'deque stores elements in sorted order automatically',
          'list.pop(0) is O(n) because every element shifts left; deque.popleft() is O(1)',
          'deque supports negative indexing but list does not',
          'deque uses less memory than a list',
        ],
        correct: 1,
        explanation: 'Removing from the front of a Python list (list.pop(0)) shifts every remaining element one position to the left — O(n). collections.deque is implemented as a doubly-linked list of fixed-size blocks, so popleft() is always O(1).',
      },
      {
        q: 'Which graph traversal algorithm relies fundamentally on a queue to work correctly?',
        options: [
          'Depth-First Search (DFS)',
          'Breadth-First Search (BFS)',
          'Dijkstra\'s algorithm with a priority queue',
          'Topological sort using DFS',
        ],
        correct: 1,
        explanation: 'BFS uses a queue to process nodes level by level. Newly discovered neighbors are enqueued; the oldest unprocessed node is always dequeued next. This FIFO order guarantees that nodes closer to the source are visited before nodes farther away.',
      },
      {
        q: 'A priority queue differs from a regular queue in what key way?',
        options: [
          'It can only hold integer values',
          'Elements are dequeued in insertion order regardless of value',
          'The element with the highest (or lowest) priority is always dequeued first, not the oldest element',
          'It requires a doubly linked list implementation',
        ],
        correct: 2,
        explanation: 'A priority queue ignores arrival order and always serves the highest-priority element next. It is typically implemented with a binary heap (O(log n) enqueue and dequeue) and is used in Dijkstra\'s shortest-path algorithm and task schedulers.',
      },
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────
  'big-o-notation': {
    concept: {
      overview:
        "Big O notation is the universal language for measuring how an algorithm's runtime scales with input size. It describes the shape of growth — not the exact execution time on any particular machine. We drop constants and lower-order terms because they become irrelevant as n grows large: what matters is whether your algorithm is linear, quadratic, logarithmic, or exponential.",
      keyPoints: [
        {
          title: 'Drop Constants',
          desc: 'O(5n) and O(100n) are both written as O(n). Constants depend on the machine, the language, and the compiler — they tell us nothing about how the algorithm scales. Only the growth shape matters.',
          code: '5n  →  O(n)     (constant dropped)\n100n²  →  O(n²)  (constant dropped)',
        },
        {
          title: 'Drop Non-Dominants',
          desc: 'O(n² + n) simplifies to O(n²) because for large n the n term is dwarfed by n². We keep only the fastest-growing term — the one that dominates the cost at scale.',
          code: 'n² + n  →  O(n²)  (n is non-dominant)',
        },
        {
          title: 'Worst Case',
          desc: 'Big O describes the ceiling — the worst-case number of operations. Knowing the worst case lets you make guarantees about your algorithm regardless of what input it receives.',
        },
      ],
    },
    steps: [
      {
        n: '1',
        label: 'O(1) — Constant',
        desc: 'The operation takes the same amount of time no matter how large the input is. Array index access and hash table lookups are classic examples — they jump directly to the result without scanning.',
        code: 'arr[5]          # O(1) — direct memory offset\nmy_dict["key"]  # O(1) — hash to bucket',
      },
      {
        n: '2',
        label: 'O(log n) — Logarithmic',
        desc: 'The algorithm halves (or otherwise reduces) the problem size at each step. Binary search on a sorted array of 1,000,000 elements takes at most 20 comparisons. Logarithmic algorithms scale beautifully.',
        code: '# Binary search: halves search space each step\n# n=1,000,000  →  ≈20 steps\n# n=1,000,000,000  →  ≈30 steps',
      },
      {
        n: '3',
        label: 'O(n) — Linear',
        desc: 'The algorithm must inspect each element once. Finding the maximum value in an unsorted array requires checking every element — you cannot skip any because the max could be anywhere.',
        code: 'def find_max(arr):\n    best = arr[0]\n    for x in arr:   # O(n) — one pass\n        if x > best: best = x\n    return best',
      },
      {
        n: '4',
        label: 'O(n log n) — Linearithmic',
        desc: 'This is the complexity of efficient comparison-based sorting algorithms like merge sort and quicksort (average case). It is also proven to be the theoretical lower bound for comparison sorting — you cannot do better in the general case.',
        code: '# Merge sort: divide (log n levels) × merge (O(n) per level)\n# Quicksort average: O(n log n)\n# Python sorted(), list.sort(): Timsort = O(n log n)',
      },
      {
        n: '5',
        label: 'O(n²) — Quadratic',
        desc: 'A nested loop where both dimensions scale with n. Bubble sort, insertion sort, and selection sort are classic examples. Fine for small inputs (n < 1000), but becomes prohibitively slow as n grows — doubling n quadruples the work.',
        code: 'for i in range(n):       # outer loop: n times\n    for j in range(n):   # inner loop: n times\n        process(i, j)    # total: n² operations',
      },
      {
        n: '6',
        label: 'O(2ⁿ) — Exponential',
        desc: 'Each additional input element doubles the work. Naive recursive Fibonacci recomputes the same subproblems over and over — fib(50) makes trillions of calls. Exponential algorithms are practically unusable beyond n ≈ 30 without optimization.',
        code: 'def fib(n):              # O(2^n) — exponential!\n    if n <= 1: return n\n    return fib(n-1) + fib(n-2)  # two recursive calls each time',
      },
    ],
    codeExamples: [
      {
        label: 'O(1) — Constant time array access',
        code:
'arr = [10, 20, 30, 40, 50]\n' +
'\n' +
'# Direct memory offset: base + i × element_size\n' +
'# Same speed whether the array has 5 or 5 million elements\n' +
'value = arr[4]   # O(1) — always exactly one operation\n' +
'print(value)     # 50',
        complexity: 'O(1)',
        variant: 'good',
      },
      {
        label: 'O(n) — Linear search',
        code:
'def linear_search(arr, target):\n' +
'    # Must check each element in sequence\n' +
'    # Worst case: target is last or not present\n' +
'    for i, val in enumerate(arr):  # O(n) comparisons\n' +
'        if val == target:\n' +
'            return i\n' +
'    return -1\n' +
'\n' +
'data = [3, 7, 1, 9, 4, 6, 2]\n' +
'print(linear_search(data, 9))  # 3 (found at index 3)',
        complexity: 'O(n) time, O(1) space',
        variant: 'default',
      },
      {
        label: 'O(n²) — Nested loops',
        code:
'def find_pairs_summing_to(arr, target):\n' +
'    # Check every pair — O(n²)\n' +
'    pairs = []\n' +
'    for i in range(len(arr)):\n' +
'        for j in range(i + 1, len(arr)):  # nested loop\n' +
'            if arr[i] + arr[j] == target:\n' +
'                pairs.append((arr[i], arr[j]))\n' +
'    return pairs\n' +
'\n' +
'# Note: a hash table can solve this in O(n) time instead\n' +
'print(find_pairs_summing_to([1, 2, 3, 4], 5))  # [(1,4),(2,3)]',
        complexity: 'O(n²) time — consider O(n) hash approach',
        variant: 'warn',
      },
    ],
    complexity: {
      rows: [
        { case: 'O(1) — Constant',      value: 'O(1)',       color: 'text-emerald-400', note: 'Array index, hash lookup — fastest possible' },
        { case: 'O(log n) — Logarithmic', value: 'O(log n)', color: 'text-cyan-400',    note: 'Binary search — halves problem each step' },
        { case: 'O(n) — Linear',        value: 'O(n)',       color: 'text-violet-400',  note: 'Single pass through input — find max, linear search' },
        { case: 'O(n log n) — Linearithmic', value: 'O(n log n)', color: 'text-amber-400', note: 'Merge sort, Timsort — optimal comparison sort' },
        { case: 'O(n²) — Quadratic',    value: 'O(n²)',      color: 'text-orange-400',  note: 'Nested loops — bubble sort, brute-force pairs' },
        { case: 'O(2ⁿ) — Exponential',  value: 'O(2ⁿ)',      color: 'text-red-400',     note: 'Naive Fibonacci — unusable beyond n≈30' },
      ],
      note: 'Each class represents an order-of-magnitude difference in scalability. An O(n²) algorithm on n=1,000,000 elements performs a trillion operations; an O(n log n) algorithm performs only about 20 million.',
    },
    realWorld: [
      {
        title: 'Database Indexing',
        desc: 'A full table scan to find a row is O(n) — it reads every row. A B-tree index reduces this to O(log n). For a table with 10 million rows that is the difference between 10 million disk reads and about 23. This is why indexes exist.',
      },
      {
        title: 'Sorting in the Standard Library',
        desc: "Python's sorted() and list.sort() use Timsort, which runs in O(n log n). This is not an accident — it is provably optimal for comparison-based sorting. Languages from Java to JavaScript converged on O(n log n) algorithms for the same reason.",
      },
    ],
    commonMistakes: [
      {
        wrong: 'Keeping lower-order terms: writing O(n² + n) instead of O(n²)',
        right: 'O(n²)',
        explain: 'For large n, n² completely dominates n. When n=1000, n²=1,000,000 and n=1,000 — the n term is 0.1% of the total. Drop it.',
      },
      {
        wrong: 'Confusing average case with worst case: saying "quicksort is O(n log n)"',
        explain: 'Quicksort is O(n log n) on average but O(n²) in the worst case (sorted input with bad pivot choice). Big O without qualification means worst case. Always state the case explicitly when it matters.',
      },
    ],
    quiz: [
      {
        q: 'What is the time complexity of accessing an element in an array by index, e.g. arr[42]?',
        options: ['O(n) — must scan to position 42', 'O(log n) — binary search to find it', 'O(1) — direct memory offset', 'O(42) — depends on the index'],
        correct: 2,
        explanation: 'Array elements are stored in contiguous memory. The address of element i is simply base + i × element_size — a single arithmetic operation regardless of array size. That is O(1).',
      },
      {
        q: 'A function has two nested loops, each running n times. What is its time complexity?',
        options: ['O(2n)', 'O(n)', 'O(n²)', 'O(n + n)'],
        correct: 2,
        explanation: 'The inner loop body executes n × n = n² times. We drop the constant coefficient (1), giving O(n²). This is quadratic — doubling n quadruples the runtime.',
      },
      {
        q: 'Binary search on a sorted array of 1,000,000 elements takes at most how many comparisons?',
        options: ['1,000,000', '500,000', 'About 20', 'About 1,000'],
        correct: 2,
        explanation: 'Binary search halves the search space at each step: log₂(1,000,000) ≈ 20. After 20 comparisons at most, the target is either found or confirmed absent. This is the power of O(log n).',
      },
      {
        q: 'What does O(log n) mean intuitively?',
        options: [
          'The algorithm reads half the input each time it runs',
          'The problem size is halved (or similarly reduced) at each step, so the number of steps grows very slowly',
          'The algorithm has a logarithm written somewhere in the code',
          'The runtime decreases as n increases',
        ],
        correct: 1,
        explanation: "O(log n) means the input size is reduced by a constant factor (often halved) each step. Binary search discards half the remaining candidates every comparison. Even for n = 1 billion, you need only ≈30 steps.",
      },
      {
        q: 'What does "drop constants" mean in Big O analysis?',
        options: [
          'Ignore all numbers in the code',
          'Write O(n) instead of O(5n) because constants do not affect the growth rate',
          'Delete constant-time operations from the algorithm',
          'Only count operations that run more than once',
        ],
        correct: 1,
        explanation: 'O(5n) and O(1000n) both describe linear growth. The constant factor depends on hardware and implementation details — it tells us nothing about how the algorithm scales. We simplify to O(n) to focus on the growth shape.',
      },
      {
        q: 'Which complexity class is the proven lower bound for comparison-based sorting algorithms?',
        options: ['O(n)', 'O(n log n)', 'O(n²)', 'O(log n)'],
        correct: 1,
        explanation: 'Information theory proves that any comparison-based sort must make at least Ω(n log n) comparisons in the worst case. Merge sort and Timsort achieve this bound. You cannot sort by comparisons faster than O(n log n) in general.',
      },
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────
  'arrays': {
    concept: {
      overview:
        'An array is a contiguous block of memory holding elements of the same type, laid out one after another with no gaps. Because each element occupies a fixed number of bytes, you can jump to any element in O(1) using pointer arithmetic: address = base + i × elementSize. This makes arrays the fastest data structure for index-based access and the foundation of most higher-level data structures.',
      keyPoints: [
        {
          title: 'O(1) Access',
          desc: 'Random access is instant because the memory address of element i is computed directly: addr = base + i × size. No searching, no pointer chasing — a single arithmetic operation.',
          code: 'addr = base + i × elementSize  # O(1) always',
        },
        {
          title: 'O(n) Search',
          desc: 'If the array is unsorted, finding an element requires a linear scan — you must check each element one by one. A sorted array can use binary search (O(log n)), but that requires maintaining sort order.',
        },
        {
          title: 'O(n) Insert',
          desc: 'Inserting at the front or middle requires shifting all subsequent elements one position to the right to make room. The number of shifts is proportional to the remaining length — O(n).',
          code: '# Insert at index 0: shift every element right by 1\n# [1,2,3] → insert 0 → [0,1,2,3] — 3 shifts',
        },
      ],
    },
    steps: [
      {
        n: '1',
        label: 'Access by Index — O(1)',
        desc: 'The CPU computes the target address from base pointer + index × element size. This is a single arithmetic instruction — it takes the same time whether the array has 10 or 10 million elements.',
        code: 'arr = [10, 20, 30, 40, 50]\nval = arr[3]   # addr = base + 3×4 bytes → 40 (O(1))',
      },
      {
        n: '2',
        label: 'Linear Search — O(n)',
        desc: 'Without an index or sorted order, finding a specific value means checking each element from left to right until a match is found or the array is exhausted. Worst case visits all n elements.',
        code: 'def search(arr, target):\n    for i, v in enumerate(arr):  # up to n iterations\n        if v == target: return i\n    return -1',
      },
      {
        n: '3',
        label: 'Insert at Front — O(n)',
        desc: 'To make room at index 0, every existing element must shift one position to the right. With n elements, that is n shifts. This is the most expensive common array operation.',
        code: '# Python list insert at front\narr.insert(0, new_value)  # O(n) — shifts all elements right',
      },
      {
        n: '4',
        label: 'Append to End — O(1) Amortized',
        desc: 'Dynamic arrays (Python list, JavaScript Array, C++ vector) allocate extra capacity and double it when full. Most appends just place the element at the next slot — O(1). Occasional doublings cost O(n) but happen so rarely the amortized cost per append is O(1).',
        code: 'arr.append(value)   # O(1) amortized\n# When capacity is exceeded, array doubles: rare O(n) resize',
      },
      {
        n: '5',
        label: 'Delete — O(n)',
        desc: 'Deleting from the middle or front leaves a gap. All elements after the deleted position must shift one place to the left to close it. Deleting from the end is O(1) — no shifting needed.',
        code: 'del arr[0]          # O(n) — all elements shift left\narr.pop()           # O(1) — remove last element, no shift',
      },
    ],
    codeExamples: [
      {
        label: 'O(1) index access and O(n) search',
        code:
'arr = [15, 3, 9, 27, 6, 12]\n' +
'\n' +
'# O(1) — direct address computation\nprint(arr[3])           # 27, instant regardless of size\n' +
'\n' +
'# O(n) — linear scan (unsorted array)\ndef find(arr, target):\n    for i, v in enumerate(arr):\n        if v == target:\n            return i\n    return -1\n' +
'\n' +
'print(find(arr, 27))    # 3  (found at index 3)',
        complexity: 'Access: O(1) | Search: O(n)',
        variant: 'good',
      },
      {
        label: 'O(n) insert at front — shifting elements',
        code:
'arr = [1, 2, 3, 4, 5]\n' +
'\n' +
'# Inserting at front shifts every element right\n# Before: [1, 2, 3, 4, 5]\n# After:  [0, 1, 2, 3, 4, 5]  — 5 elements shifted\narr.insert(0, 0)  # O(n)\nprint(arr)        # [0, 1, 2, 3, 4, 5]\n' +
'\n' +
'# If you frequently insert at the front, use a deque instead:\nfrom collections import deque\nd = deque([1, 2, 3, 4, 5])\nd.appendleft(0)   # O(1) — no shifting',
        complexity: 'O(n) for insert at front',
        variant: 'warn',
      },
      {
        label: 'O(1) amortized append — dynamic array growth',
        code:
'import sys\n' +
'\n' +
'arr = []\nfor i in range(9):\n    old_size = sys.getsizeof(arr)\n    arr.append(i)\n    new_size = sys.getsizeof(arr)\n    grew = "← RESIZED" if new_size > old_size else ""\n    print(f"appended {i}: size={new_size} bytes {grew}")\n' +
'\n' +
'# Python lists over-allocate capacity and resize infrequently\n# Each append is O(1) amortized even though resizes are O(n)',
        complexity: 'O(1) amortized per append',
        variant: 'default',
      },
    ],
    complexity: {
      rows: [
        { case: 'Access arr[i]',     value: 'O(1)',    color: 'text-emerald-400', note: 'Direct address — base + i × size' },
        { case: 'Search (unsorted)', value: 'O(n)',    color: 'text-violet-400',  note: 'Linear scan — must check every element' },
        { case: 'Insert at front',   value: 'O(n)',    color: 'text-orange-400',  note: 'All elements shift right by one position' },
        { case: 'Append to end',     value: 'O(1)*',  color: 'text-cyan-400',    note: 'Amortized — occasional O(n) resize but rare' },
        { case: 'Space',             value: 'O(n)',    color: 'text-violet-400',  note: 'One slot per element stored' },
      ],
      note: '* Amortized O(1): dynamic arrays double capacity when full. The costly resize happens so rarely that the average cost per append across any n appends is O(1).',
    },
    realWorld: [
      {
        title: 'CPU Caches',
        desc: "Arrays store elements contiguously in memory. When the CPU fetches arr[0] it loads an entire cache line (~64 bytes) into L1 cache, so arr[1], arr[2], arr[3] etc. are already warm. This spatial locality makes sequential array access dramatically faster than pointer-chasing structures like linked lists.",
      },
      {
        title: 'Dynamic Arrays in Standard Libraries',
        desc: "Python's list, JavaScript's Array, and C++'s vector are all dynamic arrays under the hood. They start with a small capacity and double when full, giving O(1) amortized append with the convenience of arbitrary size. Nearly every program uses them constantly.",
      },
    ],
    commonMistakes: [
      {
        wrong: 'Inserting at the front of an array inside a loop: O(n) × O(n) = O(n²)',
        right: 'Use collections.deque for frequent front insertions — appendleft() is O(1)',
        explain: 'Each arr.insert(0, x) shifts all existing elements right — O(n). Doing this inside a loop of n iterations gives O(n²) total. For n=100,000 that is 10 billion operations instead of 100,000.',
      },
      {
        wrong: 'Mutating an array while iterating over it',
        explain: 'Inserting or deleting elements during a for-loop changes the indices of subsequent elements, causing skipped or double-processed items. Always iterate over a copy or collect indices first: for item in arr[:]: or indices = [i for i, v in enumerate(arr) if condition].',
      },
    ],
    quiz: [
      {
        q: 'Why is arr[i] O(1) for any index i?',
        options: [
          'The array keeps a sorted index for fast lookup',
          'The CPU computes the exact memory address using base + i × elementSize — one arithmetic operation',
          'Arrays cache the last accessed element',
          'Python optimizes index access with a hash table',
        ],
        correct: 1,
        explanation: 'Array elements are stored at fixed, equally-spaced memory addresses. Given the base address and element size, the address of element i is base + i × size — computable in one instruction, independent of n.',
      },
      {
        q: 'You need a data structure that supports very frequent insertions at the front. What should you use instead of an array?',
        options: [
          'A larger array with extra space at the beginning',
          'A hash table',
          'A deque (double-ended queue)',
          'A sorted array',
        ],
        correct: 2,
        explanation: 'collections.deque supports O(1) appendleft() by maintaining pointers to both ends of a doubly-linked block structure. Array insert at front is O(n) — use a deque when front insertions are frequent.',
      },
      {
        q: 'What does "amortized O(1)" mean for dynamic array append?',
        options: [
          'Every single append is exactly O(1)',
          'The append is O(1) on average across many operations — occasional O(n) resizes are so rare the average cost is O(1)',
          'The array pre-allocates n slots at creation to guarantee O(1)',
          'Amortized means the cost is spread to other operations',
        ],
        correct: 1,
        explanation: 'When a dynamic array is full it doubles capacity and copies all elements (O(n)). But doubling happens exponentially rarely — after n appends total resize work is O(n), so the average cost per append is O(n)/n = O(1). This is amortized constant time.',
      },
      {
        q: 'Why are arrays more cache-friendly than linked lists for sequential access?',
        options: [
          'Arrays use less total memory',
          'Array elements are contiguous in memory so the CPU cache pre-loads adjacent elements automatically',
          'Linked lists require more comparisons per element',
          'Arrays use a hash function to choose memory locations',
        ],
        correct: 1,
        explanation: 'The CPU fetches memory in cache lines (~64 bytes). Contiguous array elements all land in the same cache lines, so after reading arr[0] the next several elements are already cached. Linked list nodes scatter across the heap — each node access likely causes a cache miss.',
      },
      {
        q: 'What is the worst-case time complexity of linear search on an unsorted array of n elements?',
        options: ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'],
        correct: 2,
        explanation: 'In the worst case the target is the last element or not present at all, requiring n comparisons. There is no shortcut on an unsorted array — every element could be the answer.',
      },
      {
        q: 'Why is inserting an element at the front of an array O(n)?',
        options: [
          'The array must be re-sorted after every insertion',
          'Every existing element must shift one position to the right to make room at index 0',
          'The array must allocate new memory for each insertion',
          'Front insertion requires scanning the array first',
        ],
        correct: 1,
        explanation: 'There is no gap at index 0. To place a new element there, every one of the n existing elements must move one slot to the right. That is n write operations — O(n). Appending to the end requires no shifting, so it is O(1) amortized.',
      },
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────
  'hash-tables': {
    concept: {
      overview:
        'A hash table (or hash map) stores key-value pairs and achieves O(1) average-case time for insert, lookup, and delete. It works by applying a hash function to each key to compute an array index (bucket), then storing the value there. When two keys hash to the same index — a collision — the table resolves it using chaining (linked list at each bucket) or open addressing (probing for the next empty slot).',
      keyPoints: [
        {
          title: 'Hash Function',
          desc: 'A hash function takes a key and returns an integer. The table uses hash(key) % table_size to select a bucket. A good hash function spreads keys uniformly to minimize collisions. Python\'s built-in hash() is used internally by dict.',
          code: 'index = hash(key) % table_size',
        },
        {
          title: 'Collision Handling',
          desc: 'Chaining stores a linked list at each bucket — multiple keys can share a slot. Open addressing probes for the next empty slot (linear, quadratic, or double-hashing). Chaining is simpler; open addressing has better cache locality.',
        },
        {
          title: 'Load Factor and Resizing',
          desc: 'Load factor = entries / buckets. When it exceeds ~0.7, collisions increase and performance degrades toward O(n). The table rehashes all entries into a larger array. Python dicts resize at 2/3 load factor.',
          code: 'load_factor = num_entries / num_buckets',
        },
      ],
    },
    steps: [
      {
        n: '1',
        label: 'Compute hash(key) % size',
        desc: 'The hash function converts the key to a large integer. Modulo table_size maps it to a valid index in [0, size-1]. For string keys, a polynomial rolling hash sums up character values multiplied by powers of a prime.',
        code: 'bucket = hash("apple") % 16  # e.g., => 7',
      },
      {
        n: '2',
        label: 'Go to that bucket',
        desc: 'Index directly into the backing array at the computed position. In the average case with uniform hashing, each bucket holds O(1) entries, making this lookup O(1). This is the key insight — direct addressing by hash.',
      },
      {
        n: '3',
        label: 'Handle collisions with chaining',
        desc: 'Each bucket holds a linked list (or Python list) of (key, value) pairs. When two keys hash to the same bucket, both go into the list. Lookup scans the list linearly — usually very short (≤1-2 entries) with a good hash function.',
        code: 'buckets[7] = [("apple", 1), ("mango", 3)]  # both hash to 7',
      },
      {
        n: '4',
        label: 'Retrieve by re-hashing the key',
        desc: 'To look up a key, hash it again to get the bucket, then scan the bucket\'s list for a matching key. Because the hash function is deterministic, the same key always maps to the same bucket.',
        code: 'bucket = hash(key) % size; scan bucket for key',
      },
      {
        n: '5',
        label: 'Resize when load factor is too high',
        desc: 'When entries/buckets > threshold (typically 0.7), allocate a new array roughly twice as large, then re-insert all existing entries by re-hashing. This is O(n) but happens rarely — O(1) amortized per insertion.',
        code: 'if load_factor > 0.7: resize_and_rehash()',
      },
    ],
    codeExamples: [
      {
        label: 'Simple hash table with chaining (Python)',
        code:
'class HashTable:\n' +
'    def __init__(self, size=16):\n' +
'        self.size = size\n' +
'        self.buckets = [[] for _ in range(size)]\n' +
'\n' +
'    def _index(self, key):\n' +
'        return hash(key) % self.size\n' +
'\n' +
'    def put(self, key, value):     # O(1) avg\n' +
'        idx = self._index(key)\n' +
'        for i, (k, v) in enumerate(self.buckets[idx]):\n' +
'            if k == key:\n' +
'                self.buckets[idx][i] = (key, value)  # update\n' +
'                return\n' +
'        self.buckets[idx].append((key, value))       # insert\n' +
'\n' +
'    def get(self, key):            # O(1) avg\n' +
'        idx = self._index(key)\n' +
'        for k, v in self.buckets[idx]:\n' +
'            if k == key:\n' +
'                return v\n' +
'        raise KeyError(key)\n' +
'\n' +
'ht = HashTable()\n' +
'ht.put("name", "Alice")\n' +
'print(ht.get("name"))  # "Alice"',
        complexity: 'O(1) avg put/get',
        variant: 'good',
      },
      {
        label: 'Frequency count using Python dict (hash table)',
        code:
'def word_count(text):\n' +
'    # Count occurrences of each word: O(n) time, O(k) space\n' +
'    # where k = number of unique words\n' +
'    counts = {}           # Python dict is a hash table\n' +
'    for word in text.split():\n' +
'        counts[word] = counts.get(word, 0) + 1\n' +
'    return counts\n' +
'\n' +
'result = word_count("the cat sat on the mat")\n' +
'print(result)\n' +
'# {"the": 2, "cat": 1, "sat": 1, "on": 1, "mat": 1}',
        complexity: 'O(n) time, O(k) space',
        variant: 'default',
      },
    ],
    complexity: {
      rows: [
        { case: 'Insert (average)', value: 'O(1)', color: 'text-emerald-400', note: 'Hash to bucket, append — uniform distribution assumed' },
        { case: 'Lookup (average)', value: 'O(1)', color: 'text-emerald-400', note: 'Hash to bucket, scan short chain' },
        { case: 'Delete (average)', value: 'O(1)', color: 'text-emerald-400', note: 'Hash to bucket, remove from chain' },
        { case: 'All ops (worst case)', value: 'O(n)', color: 'text-indigo-400', note: 'All keys collide into one bucket — linear scan' },
        { case: 'Space', value: 'O(n)', color: 'text-indigo-400', note: 'One entry per stored key-value pair' },
      ],
      note: 'Worst case O(n) happens only with a pathologically bad hash function or adversarial inputs. In practice with a good hash function, all operations are effectively O(1).',
    },
    realWorld: [
      {
        title: 'Python dict and set',
        desc: 'Python\'s built-in dict and set are both implemented as hash tables. Every time you do d[key] or key in s, you are using a hash function to jump directly to the right bucket in O(1) time.',
      },
      {
        title: 'Database Indexing',
        desc: 'Hash indexes in databases (like PostgreSQL\'s hash index type) allow O(1) lookup for exact-match queries. They are faster than B-tree indexes for equality checks, though B-trees also support range queries.',
      },
      {
        title: 'Caching (Memoization)',
        desc: 'Web servers and functions use hash tables to cache results. A memoized function hashes its arguments to check if the result was already computed. Cache hits avoid expensive recalculation in O(1).',
      },
      {
        title: 'Compiler Symbol Tables',
        desc: 'When a compiler processes your code, it stores every variable name and its type, scope, and memory location in a hash table called a symbol table. Lookups during compilation are O(1) thanks to hashing.',
      },
    ],
    quiz: [
      {
        q: 'What is a hash collision?',
        options: [
          'When two hash tables are merged together',
          'When the hash function produces the same index for two different keys',
          'When a key is not found in the hash table',
          'When the table runs out of memory',
        ],
        correct: 1,
        explanation: "A collision occurs when hash(key1) % size == hash(key2) % size for two different keys. Both need to be stored at the same bucket, so the table must handle this with chaining or open addressing.",
      },
      {
        q: 'What is a good load factor threshold for a hash table before resizing?',
        options: ['1.0 (full)', '0.1 (very sparse)', 'Around 0.7 (70% full)', '2.0 (over-full)'],
        correct: 2,
        explanation: 'A load factor around 0.7 balances memory efficiency and collision rate. Above 0.7, collisions increase significantly and average lookup time grows. Python\'s dict resizes at 2/3 (~0.67) load factor.',
      },
      {
        q: 'Why is the worst-case time complexity of hash table lookup O(n)?',
        options: [
          'The hash function always produces a sorted order',
          'All keys hash to the same bucket, making it a linear scan through a long chain',
          'The table must be resized before each lookup',
          'Hash tables do not support deletion',
        ],
        correct: 1,
        explanation: 'If every key hashes to the same bucket (e.g., with a broken hash function), the bucket\'s chain holds all n entries and lookup degrades to O(n) linear search. A good hash function makes this astronomically unlikely.',
      },
      {
        q: 'What property must a key have to be usable in a Python dict or set?',
        options: [
          'It must be a string',
          'It must be hashable — immutable types whose hash value does not change during their lifetime',
          'It must be a positive integer',
          'It must be smaller than the table size',
        ],
        correct: 1,
        explanation: 'Python dicts and sets require keys to be hashable. Immutable types (int, str, tuple of immutables) are hashable. Mutable types like list and dict are not — their contents can change, which would corrupt the hash table if the hash changed after insertion.',
      },
      {
        q: 'What is the difference between chaining and open addressing for collision resolution?',
        options: [
          'Chaining uses a second hash function; open addressing uses a linked list',
          'Chaining stores colliding entries in a linked list at the bucket; open addressing probes for the next empty slot in the array',
          'Open addressing requires more memory than chaining in all cases',
          'Chaining only works for integer keys; open addressing works for any key type',
        ],
        correct: 1,
        explanation: 'With chaining, each bucket holds a list of all entries that hashed there — unlimited entries per bucket, no reshuffling. With open addressing, when a collision occurs the algorithm probes other slots (linear, quadratic, or double-hashing) until an empty one is found. Open addressing has better cache locality; chaining is simpler to implement.',
      },
      {
        q: 'Which real-world data structure in Python is implemented internally as a hash table?',
        options: [
          'list',
          'tuple',
          'dict',
          'bytearray',
        ],
        correct: 2,
        explanation: 'Python\'s dict (and set) are implemented as hash tables. Every d[key] lookup hashes the key to find the bucket in O(1) average time. Python lists are dynamic arrays — they use index-based access, not hashing.',
      },
    ],
  },

};
