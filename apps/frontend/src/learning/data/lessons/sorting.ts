import type { LessonData } from '../../lessons/GenericLesson';

export const sortingLessons: Record<string, LessonData> = {
  'selection-sort': {
    concept: {
      overview:
        'Selection sort works by repeatedly finding the minimum element in the unsorted portion of the array and swapping it into its correct position at the front. The array is conceptually divided into a sorted left portion and an unsorted right portion, which grows one element at a time. Because it always scans the entire remaining unsorted region, it runs in O(n²) time regardless of the input order.',
      keyPoints: [
        {
          title: 'Minimal Writes',
          desc: 'Selection sort makes exactly n-1 swaps total, making it ideal for storage media where write operations are expensive or have limited cycles.',
        },
        {
          title: 'In-Place',
          desc: 'No extra memory is needed beyond a few variables. The sorting happens directly within the original array with O(1) auxiliary space.',
        },
        {
          title: 'Not Adaptive',
          desc: 'Even if the array is already sorted, selection sort still performs all n*(n-1)/2 comparisons. It cannot take advantage of existing order.',
        },
      ],
    },
    steps: [
      {
        n: '1',
        label: 'Start with the full unsorted range',
        desc: 'Initially the entire array is unsorted. We track a boundary i that starts at index 0 and moves right as elements are placed into their correct positions.',
      },
      {
        n: '2',
        label: 'Find the minimum in the unsorted range',
        desc: 'Scan every element from index i to n-1. Keep track of the index of the smallest element found so far.',
        code: 'min_idx = i; for j in range(i+1, n): if arr[j] < arr[min_idx]: min_idx = j',
      },
      {
        n: '3',
        label: 'Swap minimum with first unsorted element',
        desc: 'Once the minimum is found, swap it with the element at position i. Now arr[i] holds the correct value for that position.',
        code: 'arr[i], arr[min_idx] = arr[min_idx], arr[i]',
      },
      {
        n: '4',
        label: 'Advance the sorted boundary',
        desc: 'Increment i to move the sorted/unsorted boundary one position to the right. The element just placed will never be touched again.',
      },
      {
        n: '5',
        label: 'Repeat until done',
        desc: 'Repeat steps 2-4 for each position from 0 to n-2. After n-1 passes the entire array is sorted; the last element falls into place automatically.',
      },
    ],
    codeExamples: [
      {
        label: 'Selection Sort — Python pseudocode',
        complexity: 'O(n²)',
        variant: 'default',
        code: `def selection_sort(arr):
    n = len(arr)
    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

# Example
arr = [64, 25, 12, 22, 11]
selection_sort(arr)
# Result: [11, 12, 22, 25, 64]`,
      },
      {
        label: 'Why exactly n-1 swaps?',
        complexity: 'O(n) swaps',
        variant: 'good',
        code: `# Each outer loop iteration does at most ONE swap.
# Outer loop runs from i=0 to i=n-2 → exactly n-1 iterations.
# Therefore total swaps <= n-1.
#
# Compare to bubble sort which can do O(n²) swaps.
# Selection sort wins when swap cost >> compare cost.
#
# Swap cost matters for:
#   - Flash memory (limited write cycles)
#   - Network-transferred objects
#   - Large in-memory records`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Best Case',    value: 'O(n²)', color: 'text-orange-400', note: 'Even on a sorted array, all comparisons are still made' },
        { case: 'Average Case', value: 'O(n²)', color: 'text-orange-400', note: 'n*(n-1)/2 comparisons on average' },
        { case: 'Worst Case',   value: 'O(n²)', color: 'text-orange-400', note: 'Reverse sorted — same as best case' },
        { case: 'Space',        value: 'O(1)',   color: 'text-emerald-400', note: 'In-place; only a few index variables needed' },
      ],
      note: 'Selection sort is not adaptive — it always performs the same number of comparisons regardless of input order. Its advantage is the guaranteed minimum number of swaps.',
    },
    realWorld: [
      {
        title: 'Embedded Systems',
        desc: 'Microcontrollers with EEPROM or flash storage have limited write endurance. Selection sort\'s guaranteed n-1 swaps minimises wear on storage cells.',
      },
      {
        title: 'Simple Card Sorting',
        desc: 'When physically sorting a small hand of cards, people often scan for the lowest card and move it to the front — the natural human analogy of selection sort.',
      },
      {
        title: 'Costly Write Operations',
        desc: 'When each write is much more expensive than a read (e.g., writing to remote storage over a slow link), minimising swap count matters more than minimising comparisons.',
      },
      {
        title: 'Educational Purposes',
        desc: 'Selection sort is one of the first sorting algorithms taught because its logic is simple: always pick the smallest remaining item. It clearly demonstrates algorithm thinking.',
      },
    ],
    commonMistakes: [
      {
        wrong: 'for i in range(n):  # outer loop goes to n',
        right:  'for i in range(n - 1):  # stop at n-1',
        explain: 'The outer loop should run from 0 to n-2 inclusive. When i = n-1 there is only one element left and it is already in the correct position. Iterating to n causes an unnecessary (harmless but wasted) pass.',
      },
    ],
    videoId: "EwjnF7rFLns",
    videoTitle: "Learn Selection Sort in 8 Minutes",
    quiz: [
      {
        q: 'Why is selection sort O(n²) even when the input array is already sorted?',
        options: [
          'It detects sorted order and skips iterations',
          'It still scans the entire remaining unsorted portion on every pass to find the minimum',
          'It performs extra swaps on sorted input',
          'The merge step takes O(n²) time',
        ],
        correct: 1,
        explanation: 'Selection sort has no early-exit condition. On every outer iteration i it always scans from i+1 to n-1 looking for the minimum, even if the minimum is already in place. This gives identical performance on sorted and unsorted arrays.',
      },
      {
        q: 'How many swaps does selection sort make on an array of size n?',
        options: [
          'O(n²) in the worst case',
          'O(n log n) on average',
          'Exactly n-1 swaps (one per outer iteration)',
          'Zero swaps if the array is already sorted',
        ],
        correct: 2,
        explanation: 'Each of the n-1 outer loop iterations performs exactly one swap (placing the minimum of the remaining subarray into position i). Total swaps = n-1, which is O(n) — a key advantage over bubble or insertion sort.',
      },
      {
        q: 'Is selection sort a stable sorting algorithm?',
        options: [
          'Yes — equal elements always maintain their relative order',
          'No — a swap can move an element past another element with the same key',
          'Yes — because it only swaps adjacent elements',
          'It depends on the input data type',
        ],
        correct: 1,
        explanation: 'Selection sort is NOT stable. When it swaps the minimum into position i, it may jump over another element that has the same key as the displaced element, changing their relative order. A concrete example: [3a, 3b, 1] → after first swap becomes [1, 3b, 3a], reversing the two 3s.',
      },
      {
        q: 'What is the space complexity of selection sort?',
        options: [
          'O(n) — it needs a copy of the array for comparisons',
          'O(log n) — for the recursion stack',
          'O(1) — it sorts in-place using only a constant number of index variables',
          'O(n²) — one temporary variable per comparison',
        ],
        correct: 2,
        explanation: 'Selection sort is an in-place algorithm. It only needs a few integer variables (i, j, min_idx) regardless of input size. There is no recursion and no auxiliary array, so auxiliary space is O(1).',
      },
      {
        q: 'In which scenario is selection sort a reasonable practical choice despite its O(n²) time?',
        options: [
          'When sorting millions of elements in real-time',
          'When write operations are very expensive (e.g., flash memory with limited write cycles) and n is small',
          'When stability is required and n is large',
          'When the input is already partially sorted',
        ],
        correct: 1,
        explanation: 'Selection sort makes at most n-1 swaps (writes), which is the minimum possible for a general comparison-based sort. On media where each write wears out the storage cell — such as EEPROM or NOR flash — minimising writes outweighs the cost of extra comparisons, making selection sort worthwhile for small n.',
      },
      {
        q: 'Is selection sort a comparison-based sorting algorithm?',
        options: [
          'No — it uses element values directly as array indices',
          'Yes — it determines order solely by comparing pairs of elements',
          'No — it counts occurrences of each value',
          'Yes — but only for numeric data',
        ],
        correct: 1,
        explanation: 'Selection sort is comparison-based: the only information it uses about two elements is the result of comparing them (which is smaller). This means it is subject to the Ω(n log n) lower bound for comparison sorts in general, though its particular access pattern keeps it at O(n²).',
      },
    ],
  },

  'insertion-sort': {
    concept: {
      overview:
        'Insertion sort builds a sorted subarray one element at a time. For each new element, it scans backward through the sorted portion, shifting elements right until it finds the correct insertion position. This makes it highly efficient for nearly sorted data and well-suited for online scenarios where elements arrive one at a time. Its worst-case performance is O(n²) but its best case on already-sorted input is O(n).',
      keyPoints: [
        {
          title: 'Adaptive',
          desc: 'The number of operations adapts to existing order. Nearly sorted arrays finish in close to O(n) time because few shifts are needed per element.',
        },
        {
          title: 'Online Algorithm',
          desc: 'Insertion sort can process elements as they arrive in a stream without needing all data upfront. Each new element is inserted into the already-sorted prefix.',
        },
        {
          title: 'Stable & In-Place',
          desc: 'Equal elements are never swapped past each other (shifts stop at equal keys), so relative order is preserved. Only O(1) extra space is needed.',
        },
      ],
    },
    steps: [
      {
        n: '1',
        label: 'Start with first element as sorted',
        desc: 'Treat the element at index 0 as a sorted subarray of length 1. A single element is trivially sorted.',
      },
      {
        n: '2',
        label: 'Pick the next element (key)',
        desc: 'Take the element at the next unsorted position j. Store it as key — this is the value we need to insert into the correct place in the sorted prefix.',
        code: 'key = arr[j]',
      },
      {
        n: '3',
        label: 'Shift sorted elements right while greater than key',
        desc: 'Walk backward from position j-1. Each element larger than key gets shifted one position to the right, making room for the key.',
        code: 'while j > 0 and arr[j-1] > key: arr[j] = arr[j-1]; j -= 1',
      },
      {
        n: '4',
        label: 'Insert key in correct position',
        desc: 'Once we find a position where arr[j-1] <= key (or reach the start), insert key at arr[j]. The sorted portion has grown by one element.',
        code: 'arr[j] = key',
      },
      {
        n: '5',
        label: 'Repeat for all elements',
        desc: 'Repeat steps 2-4 for every index from 1 to n-1. After each pass the sorted prefix grows by one, until the whole array is sorted.',
      },
    ],
    codeExamples: [
      {
        label: 'Insertion Sort — Python pseudocode',
        complexity: 'O(n²) worst',
        variant: 'default',
        code: `def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i
        while j > 0 and arr[j - 1] > key:
            arr[j] = arr[j - 1]
            j -= 1
        arr[j] = key
    return arr

# Example
arr = [5, 2, 4, 6, 1, 3]
insertion_sort(arr)
# Result: [1, 2, 3, 4, 5, 6]`,
      },
      {
        label: 'Nearly Sorted Input — Best Case O(n)',
        complexity: 'O(n) best',
        variant: 'good',
        code: `# On a nearly sorted array each element moves
# only a small constant number of positions.
#
# Example: [1, 2, 4, 3, 5]
#   i=1: key=2, no shift needed
#   i=2: key=4, no shift needed
#   i=3: key=3, shift 4 right once → [1,2,3,4,5]
#   i=4: key=5, no shift needed
#
# Total shifts = 1  (only one element out of place)
# Time ≈ O(n) — this is the adaptive property.
#
# TimSort exploits this by detecting sorted "runs"
# and merging them rather than re-sorting from scratch.`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Best Case',    value: 'O(n)',  color: 'text-indigo-400', note: 'Already sorted — inner while loop never executes' },
        { case: 'Average Case', value: 'O(n²)', color: 'text-orange-400', note: 'Random data — each element shifts about halfway back' },
        { case: 'Worst Case',   value: 'O(n²)', color: 'text-orange-400', note: 'Reverse sorted — every element shifts all the way to front' },
        { case: 'Space',        value: 'O(1)',  color: 'text-emerald-400', note: 'In-place; only key and index variables needed' },
      ],
      note: 'Insertion sort is the algorithm of choice for small arrays (< ~16 elements). Most production sorting algorithms (TimSort, IntroSort) switch to insertion sort for small partitions to exploit cache locality and low overhead.',
    },
    realWorld: [
      {
        title: 'Sorting Playing Cards',
        desc: 'When a card player picks up cards one at a time and slots each into the correct position in their hand, they are naturally performing insertion sort.',
      },
      {
        title: 'Nearly-Sorted Database Rows',
        desc: 'When new rows are appended to an almost-sorted table (e.g., timestamped event logs with slight delays), insertion sort runs close to O(n) because most rows are already close to their final position.',
      },
      {
        title: 'Online Algorithm for Streams',
        desc: 'Insertion sort can maintain a sorted list as new items arrive without buffering the entire dataset. Each new arrival is slotted into the correct position immediately.',
      },
      {
        title: 'Hybrid Sorts (TimSort)',
        desc: 'Python\'s built-in sort and Java\'s Arrays.sort use TimSort, which applies insertion sort on small subarrays (< 64 elements) where its cache-friendly sequential access pattern beats merge sort\'s overhead.',
      },
    ],
    videoId: "Ph0mCreBQdM",
    videoTitle: "Insertion Sort with Visualization and Animation",
    quiz: [
      {
        q: 'When is insertion sort O(n)?',
        options: [
          'When the array has no duplicate elements',
          'When the array is already sorted in ascending order',
          'When the array contains only integers',
          'When the array has exactly n distinct values',
        ],
        correct: 1,
        explanation: 'On a sorted array the inner while loop condition (arr[j-1] > key) is never true, so no shifts occur. The outer loop still runs n-1 times but each iteration does O(1) work, giving O(n) total.',
      },
      {
        q: 'What property makes insertion sort stable?',
        options: [
          'It uses O(1) extra space',
          'It only compares adjacent elements and shifts (never swaps past equal keys)',
          'It always processes elements from left to right',
          'It runs in O(n log n) average time',
        ],
        correct: 1,
        explanation: 'The inner loop condition is arr[j-1] > key (strictly greater than). When arr[j-1] equals key the loop stops, so equal elements are never moved past each other. This preserves their original relative order, which is the definition of stability.',
      },
      {
        q: 'What does it mean for insertion sort to be an "online" algorithm?',
        options: [
          'It can be run on internet-connected servers',
          'It requires the entire array to be loaded into memory before starting',
          'It can process and sort elements one at a time as they arrive, without seeing future input',
          'It works only with numeric data',
        ],
        correct: 2,
        explanation: 'An online algorithm processes input piece by piece as it arrives. Insertion sort maintains a sorted prefix at all times; when a new element arrives it is inserted in the correct position immediately. No future elements need to be seen.',
      },
      {
        q: 'What is the worst-case time complexity of insertion sort and what input triggers it?',
        options: [
          'O(n log n) — triggered by random input',
          'O(n²) — triggered by a reverse-sorted array where every element must shift all the way to the front',
          'O(n²) — triggered by an already-sorted array',
          'O(n) — insertion sort is always linear',
        ],
        correct: 1,
        explanation: 'When the input is in reverse sorted order, each new element at position i must be shifted past all i elements already in the sorted prefix. The total shifts sum to 1 + 2 + … + (n-1) = n(n-1)/2, giving O(n²) worst-case time.',
      },
      {
        q: 'Which real-world sorting implementation relies on insertion sort as a sub-routine for small subarrays?',
        options: [
          'Heap sort — it switches to insertion sort when the heap has fewer than 16 elements',
          'TimSort (used in Python and Java) — it applies insertion sort on small "run" segments before merging them',
          'Counting sort — it uses insertion sort to resolve duplicate keys',
          'Radix sort — it uses insertion sort at the final digit pass',
        ],
        correct: 1,
        explanation: 'TimSort, the hybrid algorithm behind Python\'s list.sort() and Java\'s Arrays.sort for objects, detects natural sorted runs and uses binary insertion sort on subarrays smaller than ~64 elements. Insertion sort\'s low overhead and cache-friendly sequential access make it faster than merge sort for these tiny partitions.',
      },
      {
        q: 'How does insertion sort compare to selection sort in terms of the number of writes (swaps/shifts)?',
        options: [
          'Insertion sort always makes fewer writes than selection sort',
          'Selection sort makes at most n-1 swaps; insertion sort can make O(n²) shifts in the worst case',
          'Both algorithms always make the same number of writes',
          'Insertion sort makes exactly n-1 swaps just like selection sort',
        ],
        correct: 1,
        explanation: 'Selection sort guarantees exactly n-1 swaps regardless of input. Insertion sort shifts elements one position at a time and can require O(n²) write operations on a reverse-sorted array. For write-expensive media, selection sort\'s minimal write count is the key advantage over insertion sort.',
      },
    ],
  },

  'merge-sort': {
    concept: {
      overview:
        'Merge sort is a divide-and-conquer algorithm that recursively splits the array in half, sorts each half independently, and then merges the two sorted halves back into a single sorted array. Because every merge operation visits each element exactly once and there are O(log n) levels of recursion, the total time is always O(n log n). This guaranteed performance comes at the cost of O(n) extra memory for the merge step.',
      keyPoints: [
        {
          title: 'Divide and Conquer',
          desc: 'The problem is split in half at each level of recursion. With log n levels and O(n) work per level, the overall complexity is O(n log n) in all cases.',
        },
        {
          title: 'Guaranteed O(n log n)',
          desc: 'Unlike quicksort, merge sort has no worst-case degradation. It always runs in O(n log n) time regardless of input order, making it predictable.',
        },
        {
          title: 'Requires Extra Memory',
          desc: 'The merge step needs a temporary array to hold merged results. This gives O(n) auxiliary space, unlike in-place algorithms like heapsort.',
        },
      ],
    },
    steps: [
      {
        n: '1',
        label: 'Base case: single element is sorted',
        desc: 'If the array has 0 or 1 elements, it is already sorted. Return it immediately. This is the base case that terminates the recursion.',
        code: 'if len(arr) <= 1: return arr',
      },
      {
        n: '2',
        label: 'Split the array in half',
        desc: 'Find the midpoint and divide the array into a left half and a right half. Each half will be sorted independently.',
        code: 'mid = len(arr) // 2; left = arr[:mid]; right = arr[mid:]',
      },
      {
        n: '3',
        label: 'Recursively sort the left half',
        desc: 'Apply merge sort to the left half. This will recursively split and merge until left is fully sorted.',
        code: 'left = merge_sort(left)',
      },
      {
        n: '4',
        label: 'Recursively sort the right half',
        desc: 'Apply merge sort to the right half independently. After this step both halves are sorted.',
        code: 'right = merge_sort(right)',
      },
      {
        n: '5',
        label: 'Merge the two sorted halves',
        desc: 'Use two pointers, one for each half. Repeatedly pick the smaller front element and append it to the result. When one half is exhausted, append all remaining elements from the other half.',
        code: 'while i < len(left) and j < len(right): pick smaller of left[i] or right[j]',
      },
    ],
    codeExamples: [
      {
        label: 'Merge Sort — Python pseudocode',
        complexity: 'O(n log n)',
        variant: 'default',
        code: `def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left  = merge_sort(arr[:mid])
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
        label: 'Why the merge step is O(n)',
        complexity: 'O(n) per merge',
        variant: 'good',
        code: `# During merge(left, right):
#   - left has n/2 elements, right has n/2 elements
#   - Each iteration of the while loop places one element
#   - Total placements = n  →  O(n) per merge
#
# Recursion tree has log2(n) levels.
# Each level merges a total of n elements across all calls.
# Total work = O(n) * O(log n) levels = O(n log n)
#
# Level 0: one merge of size n
# Level 1: two merges of size n/2 each  → still n total
# Level 2: four merges of size n/4 each → still n total
# ...
# Level log(n): n merges of size 1 each → still n total`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Best Case',    value: 'O(n log n)', color: 'text-amber-400', note: 'Same as worst case — no adaptive shortcut exists' },
        { case: 'Average Case', value: 'O(n log n)', color: 'text-amber-400', note: 'Consistent regardless of input distribution' },
        { case: 'Worst Case',   value: 'O(n log n)', color: 'text-amber-400', note: 'Guaranteed — never degrades like quicksort can' },
        { case: 'Space',        value: 'O(n)',        color: 'text-indigo-400', note: 'Temporary arrays needed during merge steps' },
      ],
      note: 'Merge sort\'s guaranteed O(n log n) makes it the preferred choice when predictable worst-case performance matters. It is the basis of TimSort (Python, Java) and is widely used for external sorting of data too large to fit in RAM.',
    },
    realWorld: [
      {
        title: 'External Sorting of Large Files',
        desc: 'When sorting a dataset too large to fit in memory, merge sort is the natural choice: sort chunks that fit in RAM, write them to disk, then merge the sorted files using buffered I/O.',
      },
      {
        title: 'Merge Operations in Databases',
        desc: 'Database engines use merge-based algorithms for joining sorted tables (sort-merge join) and for merging sorted index segments during compaction.',
      },
      {
        title: "Python's TimSort",
        desc: "Python's built-in list.sort() and sorted() use TimSort, a hybrid algorithm that detects natural sorted runs and merges them using merge sort's merge step for guaranteed O(n log n).",
      },
      {
        title: 'Version Control File Merging',
        desc: 'Three-way file merging in Git and other VCS tools is conceptually similar to merge sort\'s merge step: two sequences of lines are compared and combined while preserving order.',
      },
    ],
    videoId: "3j0SWDX4AtU",
    videoTitle: "Learn Merge Sort in 13 Minutes",
    quiz: [
      {
        q: 'What is the time complexity of the merge step alone (merging two sorted halves of total size n)?',
        options: [
          'O(log n)',
          'O(n log n)',
          'O(n)',
          'O(n²)',
        ],
        correct: 2,
        explanation: 'The merge step uses two pointers that each advance at most n total steps. Every element is placed into the result array exactly once, so the merge step runs in O(n) time.',
      },
      {
        q: 'Why does merge sort require O(n) extra space?',
        options: [
          'For storing the recursion call stack',
          'For the temporary arrays needed during each merge operation',
          'For storing sorted indices',
          'Merge sort is in-place and uses O(1) space',
        ],
        correct: 1,
        explanation: 'During the merge step, we cannot merge two adjacent subarrays in-place without O(n) extra space (doing so in-place is complex and slow). The temporary result array holds n elements at the top level of recursion.',
      },
      {
        q: 'Is merge sort a stable sorting algorithm?',
        options: [
          'No — the merge step can reorder equal elements',
          'Yes — when merging, equal elements from the left half are always chosen before the right, preserving order',
          'It depends on the implementation',
          'No — divide operations destroy original order',
        ],
        correct: 1,
        explanation: 'The merge step uses the condition left[i] <= right[j]: when keys are equal, the left element is chosen first. Since left elements come from earlier in the original array, equal elements maintain their original relative order.',
      },
      {
        q: 'What is the space complexity of merge sort and what causes it?',
        options: [
          'O(1) — merge sort is fully in-place',
          'O(log n) — only the recursion call stack is needed',
          'O(n) — a temporary output array of size n is required during the merge step',
          'O(n log n) — a separate array is needed at every level of recursion simultaneously',
        ],
        correct: 2,
        explanation: 'Although O(log n) stack frames exist simultaneously, the dominant cost is the temporary array allocated during the merge step. At the top-level merge, this array holds n elements. Across all recursive calls the total extra memory at any point in time is O(n).',
      },
      {
        q: 'Merge sort is preferred over quick sort in which of these scenarios?',
        options: [
          'When sorting small arrays in-place where cache performance matters most',
          'When a guaranteed O(n log n) worst-case and stability are both required (e.g., sorting linked lists or external data)',
          'When the input is always random and average-case performance is all that matters',
          'When O(1) auxiliary space is required',
        ],
        correct: 1,
        explanation: 'Merge sort guarantees O(n log n) in all cases and is stable, making it ideal when predictability and key-order preservation matter. It is also naturally suited to linked lists (no random access needed) and external sorting (merging sorted runs on disk), where quick sort\'s in-place advantage disappears.',
      },
      {
        q: 'How many levels of recursion does merge sort create for an array of n elements?',
        options: [
          'n levels — one per element',
          'n/2 levels — one per pair of elements',
          'O(log n) levels — the array is halved at each level',
          'O(n²) levels — each level spawns two recursive calls',
        ],
        correct: 2,
        explanation: 'At each level of recursion, every subproblem is split in half. Starting from size n, the sizes halve each level: n → n/2 → n/4 → … → 1. The number of halvings needed to reach size 1 is log₂(n), giving O(log n) recursion depth.',
      },
    ],
  },

  'quick-sort': {
    concept: {
      overview:
        'Quick sort selects a pivot element, partitions the array so that all elements smaller than the pivot go to its left and all larger elements go to its right, then recursively sorts each partition. With a good pivot choice the array splits roughly in half at each level, giving O(n log n) average time. However, a bad pivot (such as always picking the smallest element on a sorted array) causes O(n) levels and O(n²) total work.',
      keyPoints: [
        {
          title: 'In-Place Partitioning',
          desc: 'Quick sort rearranges elements within the original array using only O(log n) stack space for the recursion, making it memory-efficient compared to merge sort.',
        },
        {
          title: 'Cache-Friendly',
          desc: 'Partitioning scans contiguous memory sequentially, resulting in excellent cache hit rates. This is why quicksort outperforms merge sort in practice despite identical asymptotic complexity.',
        },
        {
          title: 'Pivot Selection Matters',
          desc: 'Choosing the median-of-three or a random pivot avoids the O(n²) worst case. Most production implementations use randomisation or the median-of-three heuristic.',
        },
      ],
    },
    steps: [
      {
        n: '1',
        label: 'Choose a pivot element',
        desc: 'Select one element from the array as the pivot. Common choices: last element (simple but risky), random element (avoids worst case), median of first/middle/last (balances partitions).',
        code: 'pivot = arr[high]  # or choose random index',
      },
      {
        n: '2',
        label: 'Partition: move smaller elements left, larger right',
        desc: 'Rearrange so all elements < pivot come before it and all elements > pivot come after it. Elements equal to pivot can go on either side.',
        code: 'i = low - 1; for j in low..high-1: if arr[j] <= pivot: i++; swap arr[i] arr[j]',
      },
      {
        n: '3',
        label: 'Place pivot in its correct position',
        desc: 'After partitioning, swap pivot from arr[high] to arr[i+1]. The pivot is now at its final sorted position — it will never move again.',
        code: 'arr[i+1], arr[high] = arr[high], arr[i+1]; return i+1',
      },
      {
        n: '4',
        label: 'Recurse on the left subarray',
        desc: 'Apply quick sort to arr[low..pivot_index-1]. This portion contains all elements less than the pivot.',
        code: 'quicksort(arr, low, pivot_index - 1)',
      },
      {
        n: '5',
        label: 'Recurse on the right subarray',
        desc: 'Apply quick sort to arr[pivot_index+1..high]. This portion contains all elements greater than the pivot.',
        code: 'quicksort(arr, pivot_index + 1, high)',
      },
    ],
    codeExamples: [
      {
        label: 'Quick Sort with Lomuto Partition — Python pseudocode',
        complexity: 'O(n log n) avg',
        variant: 'default',
        code: `def quicksort(arr, low, high):
    if low < high:
        pi = partition(arr, low, high)
        quicksort(arr, low, pi - 1)
        quicksort(arr, pi + 1, high)

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

# Usage
arr = [10, 7, 8, 9, 1, 5]
quicksort(arr, 0, len(arr) - 1)`,
      },
      {
        label: 'Randomised Pivot — Avoiding O(n²) Worst Case',
        complexity: 'O(n log n) expected',
        variant: 'good',
        code: `import random

def quicksort_random(arr, low, high):
    if low < high:
        # Swap a random element into the pivot position
        rand_idx = random.randint(low, high)
        arr[rand_idx], arr[high] = arr[high], arr[rand_idx]
        pi = partition(arr, low, high)
        quicksort_random(arr, low, pi - 1)
        quicksort_random(arr, pi + 1, high)

# With random pivot the probability of hitting
# worst case on any fixed input becomes negligible.
# Expected depth = O(log n), total work = O(n log n).`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Best Case',    value: 'O(n log n)', color: 'text-amber-400', note: 'Pivot always splits array perfectly in half' },
        { case: 'Average Case', value: 'O(n log n)', color: 'text-amber-400', note: 'Expected with random pivot or typical random input' },
        { case: 'Worst Case',   value: 'O(n²)',      color: 'text-orange-400', note: 'Already sorted with last-element pivot — one partition has n-1 elements' },
        { case: 'Space',        value: 'O(log n)',   color: 'text-cyan-400',   note: 'Recursion stack depth; O(n) in worst case without tail-call optimisation' },
      ],
      note: 'In practice quicksort is often 2-3x faster than merge sort on random data due to better cache utilisation and lower constant factors. Most language standard libraries use introsort (quicksort + heapsort fallback) to get O(n log n) worst-case guarantees.',
    },
    realWorld: [
      {
        title: 'C Standard Library qsort',
        desc: 'The C standard library\'s qsort() function is typically implemented as quicksort or introsort. It is used by virtually every C program that needs sorting.',
      },
      {
        title: 'Language Built-in Sorts',
        desc: 'Java\'s Arrays.sort for primitives, C++\'s std::sort, and many others use introsort — a hybrid that starts with quicksort and switches to heapsort if recursion depth exceeds a threshold.',
      },
      {
        title: 'Database Index Sorting',
        desc: 'Database engines sort in-memory result sets using variants of quicksort before returning rows or building index pages, exploiting its cache efficiency.',
      },
      {
        title: 'General-Purpose In-Memory Sorting',
        desc: 'When data fits in RAM and worst-case O(n²) is mitigated by randomisation, quicksort\'s cache-friendly access pattern and low overhead make it the practical choice.',
      },
    ],
    commonMistakes: [
      {
        wrong: 'Always using the first or last element as pivot on production data',
        right:  'Use random pivot or median-of-three pivot selection',
        explain: 'Sorted or nearly-sorted input is extremely common in practice. With a fixed first/last pivot selection, sorted input triggers O(n²) performance. Randomisation or median-of-three avoids this pathological case.',
      },
    ],
    videoId: "Vtckgz38QHs",
    videoTitle: "Learn Quick Sort in 13 Minutes",
    quiz: [
      {
        q: 'What is the role of the pivot in quick sort?',
        options: [
          'It is the element that ends up in the exact middle of the array',
          'It is the element chosen to partition the array — everything smaller goes left, larger goes right',
          'It is always the median value of the array',
          'It is a temporary variable used to swap two elements',
        ],
        correct: 1,
        explanation: 'The pivot is an element chosen as a partition point. After partitioning, the pivot is in its final sorted position. All elements to its left are smaller and all to its right are larger. The pivot\'s final position is not necessarily the middle.',
      },
      {
        q: 'When does quick sort hit its O(n²) worst case?',
        options: [
          'When the array contains many duplicate elements',
          'When the pivot always splits the array into one element and n-1 elements (e.g., sorted input with last-element pivot)',
          'When the array size is a power of 2',
          'When there are more than 1000 elements',
        ],
        correct: 1,
        explanation: 'Worst case occurs when every partition is maximally unbalanced: one side has 0 elements and the other has n-1. This happens when always choosing the smallest or largest as pivot (e.g., last element on a sorted array). The recursion tree has n levels instead of log n.',
      },
      {
        q: 'How can the O(n²) worst case of quick sort be avoided in practice?',
        options: [
          'By switching to merge sort for all inputs',
          'By using randomised pivot selection or median-of-three',
          'By sorting the array first before applying quick sort',
          'By always choosing the first element as pivot',
        ],
        correct: 1,
        explanation: 'With a randomly chosen pivot, the probability of consistently bad splits on any fixed input is negligibly small, giving O(n log n) expected time. Median-of-three (median of first, middle, last) is a deterministic alternative that avoids the sorted-input worst case.',
      },
      {
        q: 'Is quick sort a stable sorting algorithm?',
        options: [
          'Yes — the partition step preserves the relative order of equal elements',
          'No — the partition step can swap equal elements past each other, changing their relative order',
          'Yes — because it is an in-place algorithm',
          'It depends on whether a random or fixed pivot is used',
        ],
        correct: 1,
        explanation: 'Quick sort is NOT stable in its standard form. During partitioning, elements are swapped based solely on whether they are less than or greater than the pivot. Two elements with equal keys can be exchanged, destroying their original relative order.',
      },
      {
        q: 'What is the auxiliary space complexity of quick sort (not counting the input array)?',
        options: [
          'O(1) — quick sort uses no extra memory at all',
          'O(n) — it needs a copy of the array for partitioning',
          'O(log n) on average — for the recursion call stack depth',
          'O(n log n) — one stack frame per comparison',
        ],
        correct: 2,
        explanation: 'Quick sort partitions in-place and needs no auxiliary array. The only extra memory is the recursion call stack, which is O(log n) deep on average when partitions are roughly equal. In the worst case (maximally unbalanced partitions) stack depth is O(n), which can be mitigated by always recursing on the smaller partition first.',
      },
      {
        q: 'Why does quick sort often outperform merge sort in practice despite both being O(n log n) on average?',
        options: [
          'Quick sort makes fewer comparisons in the worst case',
          'Quick sort is always stable, which reduces overhead',
          'Quick sort\'s in-place partitioning has better cache locality — it accesses contiguous memory sequentially, unlike merge sort\'s temporary buffer copies',
          'Quick sort has a lower constant in its O(n log n) because it uses counting instead of comparisons',
        ],
        correct: 2,
        explanation: 'Both algorithms average O(n log n) comparisons, but quick sort\'s partition step scans the array linearly in both directions without allocating extra memory. This sequential, cache-friendly access pattern has far fewer cache misses than merge sort\'s pattern of reading from a source array and writing to a separate output buffer, explaining quick sort\'s 2-3× real-world advantage.',
      },
    ],
  },

  'heap-sort': {
    concept: {
      overview:
        'Heap sort uses the heap data structure to sort in-place. It first builds a max-heap from the array in O(n) time, then repeatedly extracts the maximum by swapping the root with the last unsorted element and restoring the heap property (heapify). This process places elements in sorted order without needing any extra memory. Heap sort guarantees O(n log n) in all cases and O(1) extra space.',
      keyPoints: [
        {
          title: 'In-Place Unlike Merge Sort',
          desc: 'Heap sort uses O(1) auxiliary space. The heap is built directly inside the input array, and elements are sorted in-place by repeated extraction.',
        },
        {
          title: 'Uses Heap Property',
          desc: 'In a max-heap, every parent is greater than or equal to its children. This guarantees the root is always the maximum, which is extracted to the sorted end of the array.',
        },
        {
          title: 'Not Stable',
          desc: 'The heap operations (heapify, swap root to end) can reorder equal elements relative to each other. Heap sort does not preserve the original relative order of equal keys.',
        },
      ],
    },
    steps: [
      {
        n: '1',
        label: 'Build a max-heap from the array',
        desc: 'Call heapify on all non-leaf nodes starting from the last non-leaf (index n//2 - 1) down to the root (index 0). This builds a valid max-heap in O(n) time.',
        code: 'for i in range(n // 2 - 1, -1, -1): heapify(arr, n, i)',
      },
      {
        n: '2',
        label: 'Extract the maximum — swap root with last element',
        desc: 'The root arr[0] is the largest element. Swap it with arr[heap_size-1] to place it at the end of the array in its final sorted position.',
        code: 'arr[0], arr[i] = arr[i], arr[0]  # i = current heap size - 1',
      },
      {
        n: '3',
        label: 'Reduce heap size and heapify root',
        desc: 'Decrease the logical heap size by one (the last element is now sorted). Call heapify on the root to restore the max-heap property.',
        code: 'heapify(arr, heap_size - 1, 0)',
      },
      {
        n: '4',
        label: 'Repeat extraction until heap size is 1',
        desc: 'Repeat steps 2-3 for each heap size from n down to 2. Each iteration places one more element in its final position at the end of the array.',
        code: 'for i in range(n - 1, 0, -1): swap + heapify',
      },
    ],
    codeExamples: [
      {
        label: 'Heap Sort — Python pseudocode',
        complexity: 'O(n log n)',
        variant: 'default',
        code: `def heapify(arr, n, i):
    largest = i
    left  = 2 * i + 1
    right = 2 * i + 2
    if left  < n and arr[left]  > arr[largest]: largest = left
    if right < n and arr[right] > arr[largest]: largest = right
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)

def heap_sort(arr):
    n = len(arr)
    # Build max-heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    # Extract elements one by one
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(arr, i, 0)`,
      },
      {
        label: 'Why Build-Heap is O(n) not O(n log n)',
        complexity: 'O(n) build',
        variant: 'good',
        code: `# Intuition: most nodes are near the bottom of the heap
# and require very little heapify work.
#
# Mathematical analysis:
#   Height h nodes need at most h swaps during heapify.
#   At height h there are at most ceil(n / 2^(h+1)) nodes.
#
#   Total work = sum over h=0..log(n) of h * n/2^(h+1)
#              = n * sum(h / 2^(h+1))
#              = n * 2          (geometric series)
#              = O(n)
#
# Contrast: n individual insertions into a heap = O(n log n)
# But build-heap from bottom up = O(n) — much faster!`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Best Case',    value: 'O(n log n)', color: 'text-amber-400', note: 'No early exit; all n log n operations always execute' },
        { case: 'Average Case', value: 'O(n log n)', color: 'text-amber-400', note: 'Consistent performance regardless of input' },
        { case: 'Worst Case',   value: 'O(n log n)', color: 'text-amber-400', note: 'Guaranteed — no degenerate cases unlike quicksort' },
        { case: 'Space',        value: 'O(1)',        color: 'text-emerald-400', note: 'In-place; recursion in heapify uses O(log n) stack' },
      ],
      note: 'Heap sort combines the best properties of selection sort (O(1) space) and merge sort (O(n log n) guaranteed), but its poor cache behaviour (non-sequential memory access in heapify) makes it slower than quicksort in practice.',
    },
    realWorld: [
      {
        title: 'Priority Queues',
        desc: 'The underlying heap data structure is used directly to implement priority queues in operating system schedulers, event simulations, and Dijkstra\'s shortest path algorithm.',
      },
      {
        title: 'OS Process Scheduling',
        desc: 'Operating system process schedulers use min-heaps or max-heaps to efficiently find and dispatch the highest-priority runnable process in O(log n) time.',
      },
      {
        title: 'Finding k Largest Elements',
        desc: 'To find the top-k elements from a stream of n items, maintain a min-heap of size k. Each new element is compared to the heap\'s minimum — O(n log k) total time.',
      },
      {
        title: 'Embedded Systems Needing Guaranteed O(n log n)',
        desc: 'Real-time systems with hard timing constraints need predictable worst-case performance. Heap sort provides O(n log n) guaranteed with O(1) space, unlike quicksort.',
      },
    ],
    videoId: "2DmK_H7IdTo",
    videoTitle: "Heap Sort in 4 Minutes",
    quiz: [
      {
        q: 'What heap property does heap sort rely on?',
        options: [
          'Min-heap: every parent is smaller than its children',
          'Max-heap: every parent is greater than or equal to its children, so the root is always the maximum',
          'Balanced BST property: left subtree keys < root < right subtree keys',
          'Complete binary tree: all levels are fully filled',
        ],
        correct: 1,
        explanation: 'Heap sort uses a max-heap where every parent is >= its children. This guarantees arr[0] (the root) is always the maximum element in the current heap, which can then be extracted and placed at the sorted end of the array.',
      },
      {
        q: 'Why does building the initial heap take O(n) time rather than O(n log n)?',
        options: [
          'Because heapify is O(1) for each element',
          'Because nodes near the bottom of the heap require less heapify work — summing across all nodes gives O(n)',
          'Because the array is partially sorted before heapify',
          'Because only the root needs to be heapified',
        ],
        correct: 1,
        explanation: 'Nodes at depth d from the bottom require at most d swaps during heapify. There are far more nodes near the leaves (which need 0-1 swaps) than near the root (which needs up to log n swaps). The weighted sum converges to O(n) by a geometric series argument.',
      },
      {
        q: 'Is heap sort a stable sorting algorithm?',
        options: [
          'Yes — the heap property preserves relative order of equal keys',
          'No — the swap-to-end step can reorder equal elements',
          'Yes — because it is in-place',
          'It depends on whether a min-heap or max-heap is used',
        ],
        correct: 1,
        explanation: 'Heap sort is NOT stable. When the root (maximum) is swapped to the end of the array, it may jump past other elements with the same key that were originally after it. The heap operations do not track or preserve original insertion order.',
      },
      {
        q: 'What is the worst-case time complexity of heap sort?',
        options: [
          'O(n²) — when the input is already sorted',
          'O(n log n) — guaranteed in all cases, unlike quick sort',
          'O(n) — because build-heap is O(n)',
          'O(n log n) only on average; worst case is O(n²)',
        ],
        correct: 1,
        explanation: 'Heap sort guarantees O(n log n) in every case. Building the heap takes O(n) and each of the n-1 extraction steps calls heapify in O(log n), giving O(n) + O(n log n) = O(n log n) total. There is no degenerate input that causes degradation, unlike quick sort.',
      },
      {
        q: 'Why does heap sort have poor cache performance compared to quick sort?',
        options: [
          'Heap sort allocates a large auxiliary array that does not fit in cache',
          'Heapify jumps between parent and child nodes at indices i, 2i+1, and 2i+2, causing non-sequential (scattered) memory access patterns with many cache misses',
          'Heap sort uses recursion, which flushes the CPU cache on every call',
          'Heap sort reads the same elements multiple times, saturating the cache bandwidth',
        ],
        correct: 1,
        explanation: 'During heapify, accesses jump between a node at index i and its children at 2i+1 and 2i+2. For large heaps these indices are far apart in memory, causing frequent cache misses. Quick sort\'s partition step scans adjacent elements sequentially, fitting naturally into cache lines and achieving much better practical throughput.',
      },
      {
        q: 'Heap sort is best suited for which of the following use cases?',
        options: [
          'Sorting linked lists where pointer manipulation is cheap',
          'Situations requiring guaranteed O(n log n) worst-case time with O(1) auxiliary space, such as real-time embedded systems',
          'Sorting nearly sorted data where an adaptive algorithm would be faster',
          'External sorting of datasets too large to fit in RAM',
        ],
        correct: 1,
        explanation: 'Heap sort uniquely combines guaranteed O(n log n) worst-case performance with O(1) auxiliary space. This makes it attractive for real-time or memory-constrained systems where neither the unpredictability of quick sort nor the O(n) extra space of merge sort is acceptable. Its poor cache behaviour is a trade-off worth accepting in such environments.',
      },
    ],
  },

  'counting-sort': {
    concept: {
      overview:
        'Counting sort is a non-comparison-based sorting algorithm that counts the number of occurrences of each distinct integer value, then uses those counts to place elements directly into their correct output positions. Because it never compares elements against each other, it breaks through the O(n log n) lower bound that applies to comparison-based sorts. Its time complexity is O(n + k) where k is the range of input values.',
      keyPoints: [
        {
          title: 'Non-Comparison Sort',
          desc: 'Counting sort does not compare elements. It exploits the fact that integer keys can be used as array indices, breaking the O(n log n) lower bound for comparison-based sorts.',
        },
        {
          title: 'Requires Bounded Integer Keys',
          desc: 'The algorithm requires integer keys in a known, bounded range [min, max]. It cannot sort floating-point numbers, strings, or objects without a special key mapping.',
        },
        {
          title: 'Stable When Done Correctly',
          desc: 'Using prefix sums (cumulative counts) to place elements ensures equal keys appear in their original relative order, making counting sort stable.',
        },
      ],
    },
    steps: [
      {
        n: '1',
        label: 'Find min and max values',
        desc: 'Scan the array once to find the minimum and maximum values. These define the range of the count array.',
        code: 'min_val = min(arr); max_val = max(arr); k = max_val - min_val + 1',
      },
      {
        n: '2',
        label: 'Create count array of size k',
        desc: 'Allocate a count array of size (max - min + 1) initialised to zero. Index i in the count array corresponds to value (i + min) in the input.',
        code: 'count = [0] * k',
      },
      {
        n: '3',
        label: 'Count each element',
        desc: 'Scan the input array and increment count[value - min] for each element.',
        code: 'for x in arr: count[x - min_val] += 1',
      },
      {
        n: '4',
        label: 'Compute prefix sums (cumulative counts)',
        desc: 'Transform the count array so each position holds the total number of elements less than or equal to that value. This gives the final output position of each value.',
        code: 'for i in range(1, k): count[i] += count[i - 1]',
      },
      {
        n: '5',
        label: 'Place elements in output using prefix sums',
        desc: 'Iterate the input in reverse (for stability). For each element, use the prefix sum to find its output index, place it there, then decrement the count.',
        code: 'for x in reversed(arr): output[count[x-min_val]-1] = x; count[x-min_val] -= 1',
      },
      {
        n: '6',
        label: 'Copy output back to original array',
        desc: 'Copy the sorted output array back to arr. The array is now fully sorted.',
        code: 'arr[:] = output',
      },
    ],
    codeExamples: [
      {
        label: 'Counting Sort — Python pseudocode',
        complexity: 'O(n + k)',
        variant: 'default',
        code: `def counting_sort(arr):
    if not arr:
        return arr
    min_val = min(arr)
    max_val = max(arr)
    k = max_val - min_val + 1

    count = [0] * k
    for x in arr:
        count[x - min_val] += 1

    # Prefix sums for stable placement
    for i in range(1, k):
        count[i] += count[i - 1]

    output = [0] * len(arr)
    for x in reversed(arr):
        count[x - min_val] -= 1
        output[count[x - min_val]] = x

    return output

# Example: scores 0-100
scores = [4, 2, 2, 8, 3, 3, 1]
print(counting_sort(scores))  # [1, 2, 2, 3, 3, 4, 8]`,
      },
      {
        label: 'When Counting Sort Beats Merge Sort',
        complexity: 'O(n) when k << n',
        variant: 'good',
        code: `# Counting sort wins when k (range) is much smaller than n.
#
# Example 1: Sort 1 million exam scores 0-100
#   n = 1,000,000    k = 101
#   Merge sort: O(n log n) = ~20,000,000 ops
#   Counting sort: O(n + k) = ~1,000,101 ops  MUCH FASTER
#
# Example 2: Sort 100 random integers 0-1,000,000
#   n = 100    k = 1,000,001
#   Merge sort: O(n log n) ≈ 700 ops
#   Counting sort: O(n + k) ≈ 1,000,100 ops  MUCH SLOWER
#
# Rule of thumb: use counting sort when k = O(n).`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Time',       value: 'O(n + k)', color: 'text-indigo-400', note: 'n = number of elements, k = range (max - min + 1)' },
        { case: 'Space',      value: 'O(n + k)', color: 'text-indigo-400', note: 'Output array (n) and count array (k)' },
        { case: 'Best/Worst', value: 'O(n + k)', color: 'text-indigo-400', note: 'No variance based on input order — always the same' },
        { case: 'Comparison', value: 'N/A',      color: 'text-zinc-400',   note: 'Not a comparison sort — not bounded by O(n log n)' },
      ],
      note: 'When k = O(n) (the range is proportional to the number of elements), counting sort runs in O(n) time — optimal. When k >> n, the large count array wastes both time and memory.',
    },
    realWorld: [
      {
        title: 'Sorting Exam Scores',
        desc: 'Exam scores typically range from 0 to 100, a range of 101. Counting sort can sort millions of scores in O(n) time with a tiny count array of 101 elements.',
      },
      {
        title: 'Sorting Ages',
        desc: 'Human ages span roughly 0-120. Counting sort can sort a database of millions of people by age in linear time with a count array of only 121 entries.',
      },
      {
        title: 'Character Frequency Analysis',
        desc: 'Sorting characters in a string (256 ASCII values or 65536 Unicode code points) by frequency can be done with counting sort, and is a building block for Huffman encoding.',
      },
      {
        title: "Radix Sort's Subroutine",
        desc: 'Counting sort is used as the stable intermediate sorting step inside radix sort. Each digit pass uses counting sort over the range 0-9 (or 0-255 for byte-level radix sort).',
      },
    ],
    videoId: "OKd534EWcdk",
    videoTitle: "Learn Counting Sort Algorithm in Less Than 6 Minutes",
    quiz: [
      {
        q: 'What does k represent in the O(n + k) complexity of counting sort?',
        options: [
          'The number of comparisons made',
          'The number of recursive calls',
          'The range of input values: k = max - min + 1',
          'The number of duplicate elements',
        ],
        correct: 2,
        explanation: 'k is the size of the count array, which equals the range of input values (max - min + 1). Initialising and scanning this count array takes O(k) time, giving a total of O(n + k).',
      },
      {
        q: 'When is counting sort faster than merge sort?',
        options: [
          'Always — it has better asymptotic complexity',
          'When k (the range of values) is O(n) or smaller, making O(n + k) = O(n)',
          'When the input is already nearly sorted',
          'When n is very small (< 16 elements)',
        ],
        correct: 1,
        explanation: 'Counting sort beats merge sort when k is small relative to n. If k = O(n), then O(n + k) = O(n) which beats O(n log n). But when k >> n (e.g., sorting 100 integers in range 0-1,000,000), the O(k) overhead makes counting sort much worse.',
      },
      {
        q: 'What type of data can counting sort NOT handle directly?',
        options: [
          'Positive integers',
          'Negative integers',
          'Floating-point numbers and arbitrary objects without integer key mapping',
          'Arrays with duplicate values',
        ],
        correct: 2,
        explanation: 'Counting sort requires integer keys in a bounded range because it uses key values as array indices. Floating-point numbers, strings, and arbitrary objects cannot be used directly as indices without first mapping them to a bounded integer range.',
      },
      {
        q: 'Is counting sort a stable sorting algorithm?',
        options: [
          'No — the count array loses track of the original order of equal elements',
          'Yes — when the prefix-sum technique is used and elements are placed by iterating the input in reverse, equal keys retain their original relative order',
          'It depends on the range k',
          'Yes — but only when all input values are distinct',
        ],
        correct: 1,
        explanation: 'The standard counting sort implementation with prefix sums iterates the original array in reverse when placing elements into the output. This ensures that among equal keys, the element that appeared later in the input is placed later in the output, preserving relative order and making the sort stable.',
      },
      {
        q: 'What happens to counting sort\'s performance when the value range k is much larger than n?',
        options: [
          'Performance improves because the count array has more space',
          'Performance degrades because initialising and scanning the O(k) count array dominates, making it slower than O(n log n) comparison sorts',
          'Performance is unchanged because only n elements are ever counted',
          'Counting sort automatically switches to merge sort internally',
        ],
        correct: 1,
        explanation: 'Counting sort allocates and zeroes a count array of size k. When k >> n (e.g., sorting 100 integers in the range 0–1,000,000), the O(k) overhead completely dominates O(n), making counting sort far slower than merge sort\'s O(n log n). A rule of thumb is to use counting sort only when k = O(n).',
      },
      {
        q: 'Counting sort is classified as a non-comparison sort. What does this mean for its theoretical time complexity lower bound?',
        options: [
          'It is still bounded by Ω(n log n) because all sorting algorithms share that lower bound',
          'It bypasses the Ω(n log n) comparison-sort lower bound and can achieve O(n) time by using integer key values as direct array indices',
          'Its lower bound is Ω(n²) because it must count every pair of elements',
          'The lower bound does not apply because counting sort only works on integers',
        ],
        correct: 1,
        explanation: 'The Ω(n log n) lower bound applies only to comparison-based sorting algorithms, which derive order information solely from pairwise comparisons. Counting sort instead uses integer key values directly as array indices, extracting more information per operation. When k = O(n) this allows O(n) sorting — a genuine improvement over the comparison-sort lower bound.',
      },
    ],
  },

  'bubble-sort': {
    concept: {
      overview:
        'Bubble Sort repeatedly scans the array, comparing adjacent pairs and swapping them if out of order. After each full pass, the largest unsorted element "bubbles up" to its correct position at the end. With early-exit optimization, an already-sorted array is detected in O(n).',
      keyPoints: [
        {
          title: 'In-Place',
          desc: 'O(1) extra space — all swaps happen directly within the original array without any auxiliary storage.',
        },
        {
          title: 'Stable',
          desc: 'Equal elements are never swapped past each other (only strict > triggers a swap), so their relative order is preserved.',
        },
        {
          title: 'Early Exit',
          desc: 'If a full pass completes without a single swap, the array is already sorted. This optimisation makes bubble sort O(n) on already-sorted input.',
        },
      ],
    },
    steps: [
      {
        n: '1',
        label: 'Compare Adjacent',
        desc: 'Compare arr[i] and arr[i+1] for each consecutive pair in the current unsorted range.',
        code: 'if arr[i] > arr[i + 1]: swap',
      },
      {
        n: '2',
        label: 'Swap if Needed',
        desc: 'If the left element is greater than the right, swap them so the larger value moves one step to the right.',
        code: 'arr[i], arr[i + 1] = arr[i + 1], arr[i]',
      },
      {
        n: '3',
        label: 'Bubble Up',
        desc: 'After one full pass, the largest element in the unsorted region has bubbled all the way to its correct position at the end.',
      },
      {
        n: '4',
        label: 'Shrink Range',
        desc: 'The last j elements are guaranteed to be in their final sorted positions, so the next pass only needs to scan up to index n - j - 1.',
        code: 'for i in range(n - 1 - j):  # shrink upper bound each pass',
      },
      {
        n: '5',
        label: 'Early Exit',
        desc: 'Track whether any swap occurred during a pass. If no swap happened, the array is already sorted — stop immediately instead of continuing unnecessary passes.',
        code: 'swapped = False\n# ... inner loop ...\nif not swapped: break',
      },
    ],
    codeExamples: [
      {
        label: 'Bubble Sort — Basic O(n²)',
        complexity: 'O(n²)',
        variant: 'default',
        code: `def bubble_sort_basic(arr):
    n = len(arr)
    for j in range(n - 1):
        for i in range(n - 1 - j):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
    return arr

# Example
arr = [5, 3, 8, 1, 2]
bubble_sort_basic(arr)
# Result: [1, 2, 3, 5, 8]`,
      },
      {
        label: 'Bubble Sort — Optimized (early exit + shrinking range)',
        complexity: 'O(n) best / O(n²) worst',
        variant: 'good',
        code: `def bubble_sort(arr):
    n = len(arr)
    for j in range(n - 1):
        swapped = False
        # Shrink the upper bound each pass
        for i in range(n - 1 - j):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True
        # Early exit: no swap means already sorted
        if not swapped:
            break
    return arr

# Already-sorted input finishes in a single O(n) pass
arr = [1, 2, 3, 4, 5]
bubble_sort(arr)  # exits after one pass — O(n)`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Worst Case',   value: 'O(n²)', color: 'text-orange-400', note: 'Reverse-sorted input — every pair needs a swap on every pass' },
        { case: 'Average Case', value: 'O(n²)', color: 'text-orange-400', note: 'Random input — n*(n-1)/2 comparisons on average' },
        { case: 'Best Case',    value: 'O(n)',  color: 'text-emerald-400', note: 'Already-sorted input with early-exit optimisation — single pass' },
        { case: 'Space',        value: 'O(1)',  color: 'text-emerald-400', note: 'In-place; only a swap temp and a boolean flag are needed' },
      ],
      note: 'Bubble sort is rarely used in production because even its optimised form is O(n²) average and worst case. Its main practical value is on nearly-sorted data where early exit kicks in quickly, and as a teaching algorithm.',
    },
    realWorld: [
      {
        title: 'Teaching Tool',
        desc: 'Bubble sort is one of the simplest algorithms to visualise and understand, making it a standard first sorting algorithm in CS101 courses worldwide.',
      },
      {
        title: 'Nearly-Sorted Data',
        desc: 'With early exit, bubble sort detects and finishes already- or nearly-sorted arrays in O(n) time, making it competitive with insertion sort for small perturbations in an otherwise ordered list.',
      },
    ],
    commonMistakes: [
      {
        wrong: '# No early-exit flag — always runs all n-1 passes',
        right:  'swapped = False  # track per pass; break if no swap occurred',
        explain: 'Without an early-exit flag, bubble sort always performs n*(n-1)/2 comparisons even on an already-sorted array, losing the O(n) best-case advantage entirely.',
      },
      {
        wrong: 'for i in range(n - 1):  # inner bound never shrinks',
        right:  'for i in range(n - 1 - j):  # shrink by j each outer pass',
        explain: 'After j outer passes, the last j elements are in their final positions. Not shrinking the inner loop\'s upper bound wastes time re-examining elements that are already correctly placed.',
      },
      {
        wrong: '# Using bubble sort on a large (n > 10,000) dataset',
        right:  '# Use merge sort, heap sort, or Timsort for large inputs',
        explain: 'Bubble sort\'s O(n²) average complexity makes it impractically slow for large arrays. Even on modern hardware, sorting 100,000 elements takes ~10 billion operations versus ~1.7 million for O(n log n) algorithms.',
      },
    ],
    videoId: "Dv4qLJcxus8",
    videoTitle: "Learn Bubble Sort in 7 Minutes",
    quiz: [
      {
        q: 'What is the worst-case time complexity of bubble sort and what input triggers it?',
        options: [
          'O(n) — a reverse-sorted array where all pairs need swapping',
          'O(n log n) — random input with many duplicates',
          'O(n²) — a reverse-sorted array where every pair must be swapped on every pass',
          'O(n²) — an already-sorted array because the algorithm cannot detect it',
        ],
        correct: 2,
        explanation: 'When the array is in reverse order, every adjacent pair is out of order on every pass. The total number of swaps and comparisons sums to n*(n-1)/2, giving O(n²) worst-case time.',
      },
      {
        q: 'When does bubble sort achieve its best-case O(n) time complexity?',
        options: [
          'When the array has no duplicate elements',
          'When the array is already sorted in ascending order and the early-exit optimisation is implemented',
          'When the array has exactly two elements',
          'When the array is sorted in descending order',
        ],
        correct: 1,
        explanation: 'With the early-exit flag, a single pass over an already-sorted array finds no swaps and immediately breaks out of the outer loop. Only n-1 comparisons are made, giving O(n) best-case time. Without the flag, best case is still O(n²).',
      },
      {
        q: 'Why is it called "bubble sort"?',
        options: [
          'Because it was invented by a researcher named Bubble',
          'Because it uses a bubble (temporary variable) to hold values during swaps',
          'Because larger elements gradually "bubble up" toward the end of the array after each pass',
          'Because it sorts data in bubble-shaped groups',
        ],
        correct: 2,
        explanation: 'After each full pass, the largest remaining unsorted element has been moved one position at a time all the way to its correct position at the right end of the unsorted region — visually resembling a bubble rising to the surface.',
      },
      {
        q: 'Is bubble sort a stable sorting algorithm?',
        options: [
          'No — swapping adjacent elements always changes relative order',
          'Yes — it only swaps when arr[i] > arr[i+1] (strict greater-than), so equal elements are never swapped past each other',
          'It depends on whether the early-exit optimisation is enabled',
          'No — stability is only possible with O(n log n) algorithms',
        ],
        correct: 1,
        explanation: 'The swap condition is strict: arr[i] > arr[i+1]. When two elements are equal, no swap occurs, so they remain in their original relative order. This makes bubble sort stable.',
      },
      {
        q: 'What is the space complexity of bubble sort?',
        options: [
          'O(n) — it needs a copy of the array to perform comparisons',
          'O(log n) — for the implicit recursion stack',
          'O(1) — it sorts in-place using only a boolean flag and a temporary swap variable',
          'O(n²) — one temporary value per comparison',
        ],
        correct: 2,
        explanation: 'Bubble sort is an in-place algorithm. It only requires a constant number of extra variables (a loop index, a boolean swapped flag, and a temporary value during swaps) regardless of the input size, so auxiliary space is O(1).',
      },
      {
        q: 'Why is bubble sort rarely used in production code despite being easy to implement?',
        options: [
          'It is not stable, which disqualifies it from most use cases',
          'It requires O(n) extra space, making it memory-inefficient',
          'Its O(n²) average and worst-case time complexity makes it impractically slow compared to O(n log n) algorithms like merge sort or Timsort for any non-trivial input size',
          'It cannot handle arrays containing duplicate values',
        ],
        correct: 2,
        explanation: 'Bubble sort\'s O(n²) average performance means sorting 100,000 elements requires roughly 5 billion operations, while merge sort needs only about 1.7 million. For nearly-sorted small arrays the early-exit optimisation helps, but even then insertion sort is generally faster in practice because it makes fewer writes per pass.',
      },
    ],
  },

  'radix-sort': {
    concept: {
      overview:
        'Radix sort extends the idea of counting sort to handle large integer ranges by sorting digit by digit, from the least significant digit (LSD) to the most significant digit (MSD). At each digit position it applies a stable sort (typically counting sort over range 0-9), so after d passes over all digit positions the array is fully sorted. The key insight is that by always using a stable subroutine, the order established by earlier digits is preserved when sorting later digits.',
      keyPoints: [
        {
          title: 'Non-Comparison Sort',
          desc: 'Like counting sort, radix sort never compares elements directly. It processes each digit as an integer key, breaking through the O(n log n) comparison sort barrier.',
        },
        {
          title: 'Digit-by-Digit Processing',
          desc: 'Sorting digit by digit distributes the work across d passes, each of which is O(n + k). This handles large key ranges (like 64-bit integers) that would make counting sort impractical.',
        },
        {
          title: 'Requires Stable Intermediate Sort',
          desc: 'The intermediate sort for each digit position must be stable. Otherwise, the order established by less significant digits would be destroyed by more significant digit passes.',
        },
      ],
    },
    steps: [
      {
        n: '1',
        label: 'Find max value to determine number of digits d',
        desc: 'Scan the array to find the maximum value. The number of digits d = floor(log10(max)) + 1 determines how many passes are needed.',
        code: 'max_val = max(arr); d = len(str(max_val))',
      },
      {
        n: '2',
        label: 'For each digit position: apply stable sort on that digit',
        desc: 'Starting at the ones place (exp = 1), sort the array stably by the current digit. Move to tens (exp = 10), hundreds (exp = 100), and so on.',
        code: 'exp = 1; while max_val // exp > 0: counting_sort_by_digit(arr, exp); exp *= 10',
      },
      {
        n: '3',
        label: 'Extract the current digit for each element',
        desc: 'The digit at position exp for element x is computed as (x // exp) % 10. This gives a value from 0 to 9 used as the counting sort key.',
        code: 'digit = (x // exp) % 10',
      },
      {
        n: '4',
        label: 'After d passes the array is fully sorted',
        desc: 'Once all digit positions have been processed, the array is sorted. The stability of each pass ensures that previous ordering is preserved as more significant digits are considered.',
      },
    ],
    codeExamples: [
      {
        label: 'Radix Sort (LSD) — Python pseudocode',
        complexity: 'O(d * (n + k))',
        variant: 'default',
        code: `def counting_sort_by_digit(arr, exp):
    n = len(arr)
    output = [0] * n
    count  = [0] * 10

    for x in arr:
        digit = (x // exp) % 10
        count[digit] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    for x in reversed(arr):
        digit = (x // exp) % 10
        count[digit] -= 1
        output[count[digit]] = x

    arr[:] = output

def radix_sort(arr):
    if not arr:
        return arr
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        counting_sort_by_digit(arr, exp)
        exp *= 10
    return arr`,
      },
      {
        label: 'Why stability is essential in radix sort',
        complexity: 'O(d*(n+k))',
        variant: 'warn',
        code: `# Sorting [329, 457, 657, 839, 436, 720, 355] digit by digit:
#
# Pass 1 (ones digit):
#   720, 355, 436, 457, 657, 329, 839
#   (sorted by last digit: 0,5,6,7,7,9,9)
#
# Pass 2 (tens digit) — MUST use stable sort:
#   720, 329, 436, 839, 355, 457, 657
#   (sorted by middle digit, equal ones preserved)
#
# Pass 3 (hundreds digit) — MUST use stable sort:
#   329, 355, 436, 457, 657, 720, 839  SORTED!
#
# If pass 2 were UNSTABLE, 457 and 657 could swap →
# pass 3 would see them in wrong order → corrupt result.`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Time',   value: 'O(d*(n+k))', color: 'text-indigo-400', note: 'd = digits, n = elements, k = digit range (10 for decimal)' },
        { case: 'Space',  value: 'O(n + k)',   color: 'text-indigo-400', note: 'Output buffer (n) and digit count array (k=10)' },
        { case: 'd value', value: 'O(log_k(max))', color: 'text-cyan-400', note: 'Number of digit passes; constant for fixed-width integers' },
        { case: 'vs Comparison', value: 'O(n) when d=O(1)', color: 'text-emerald-400', note: 'For 32-bit ints with base 256: d=4 passes — effectively O(n)' },
      ],
      note: 'For fixed-width integers (32-bit or 64-bit), d is a constant, making radix sort effectively O(n). Using base 256 instead of base 10 reduces d to 4 or 8 passes and gives a large practical speedup.',
    },
    realWorld: [
      {
        title: 'Sorting Phone Numbers',
        desc: 'Phone numbers are fixed-width integers (10-11 digits). Radix sort can sort millions of phone numbers in near-linear time by processing each digit position independently.',
      },
      {
        title: 'IP Address Sorting',
        desc: 'IPv4 addresses are 32-bit unsigned integers. Radix sort with base 256 sorts them in exactly 4 passes — effectively O(n) for any size dataset.',
      },
      {
        title: 'Postal Code Sorting',
        desc: 'Physical mail sorting machines traditionally sorted letters by postal code digit by digit — the real-world origin of LSD radix sort before it was formalised as a computer algorithm.',
      },
      {
        title: 'Card Sorting Machines',
        desc: 'Punched card sorters from the 1890s (used for census tabulation) sorted cards one column at a time — exactly the LSD radix sort principle applied to physical cards.',
      },
    ],
    videoId: "XiuSW_mEn7g",
    videoTitle: "Radix Sort Algorithm Introduction in 5 Minutes",
    quiz: [
      {
        q: 'What does "radix" mean in radix sort?',
        options: [
          'The root node of a sorting tree',
          'The base of the number system used (e.g., 10 for decimal digits, 2 for binary)',
          'The maximum value in the array',
          'The number of elements to be sorted',
        ],
        correct: 1,
        explanation: 'Radix means the base of the number system. Radix sort processes one "digit" in that base per pass. Decimal radix sort uses base 10 (digits 0-9). Binary radix sort uses base 2. Byte-level radix sort uses base 256 (values 0-255).',
      },
      {
        q: 'Why must the intermediate sort in each radix sort pass be stable?',
        options: [
          'To reduce the number of passes required',
          'To ensure the ordering established by less significant digits is preserved when sorting more significant digits',
          'To reduce memory usage during sorting',
          'To handle negative numbers correctly',
        ],
        correct: 1,
        explanation: 'After sorting by the ones digit, two elements with equal tens digits must remain in ones-digit order when the tens-digit pass runs. A stable sort preserves their relative order. An unstable sort could discard the work done by previous passes, producing incorrect results.',
      },
      {
        q: 'What is the primary advantage of radix sort over comparison-based sorts like merge sort?',
        options: [
          'It uses O(1) extra memory',
          'It can sort any data type without modification',
          'For fixed-width integer keys it achieves O(n) time, bypassing the O(n log n) lower bound for comparison sorts',
          'It is simpler to implement than merge sort',
        ],
        correct: 2,
        explanation: 'Comparison-based sorts cannot do better than O(n log n) in the worst case. Radix sort sidesteps this by never comparing elements — it uses digit values as indices. For 32-bit integers with base 256, only 4 passes are needed regardless of n, giving O(4n) = O(n) performance.',
      },
      {
        q: 'What is the space complexity of LSD radix sort?',
        options: [
          'O(1) — it sorts completely in-place with no extra arrays',
          'O(n + k) — an output buffer of size n and a digit count array of size k are needed',
          'O(n log n) — a separate buffer is needed for every level of digit processing',
          'O(d * n) — one full copy of the array is kept for each digit pass',
        ],
        correct: 1,
        explanation: 'Each pass of LSD radix sort uses counting sort as its subroutine. Counting sort needs an output array of size n and a count array of size k (the digit base, e.g., 10 or 256). These are reused across all d passes, so total extra space is O(n + k) — not multiplied by d.',
      },
      {
        q: 'Which variant of radix sort processes digits starting from the most significant digit (MSD)?',
        options: [
          'LSD radix sort — least significant digit first is the same as most significant digit first',
          'MSD radix sort — it partitions recursively by the most significant digit, similar in spirit to quick sort',
          'Counting radix sort — it always processes digits in the order they appear in the count array',
          'Stable radix sort — stability forces processing from the most significant digit',
        ],
        correct: 1,
        explanation: 'MSD (Most Significant Digit) radix sort starts from the highest digit and recursively sorts sub-groups, similar to a multi-key quick sort. LSD (Least Significant Digit) radix sort starts from the lowest digit and applies a stable sort in a flat sequence of passes. LSD is simpler and more cache-friendly; MSD naturally handles variable-length strings and can short-circuit early.',
      },
      {
        q: 'Radix sort with base 256 sorts 32-bit unsigned integers in how many passes, and why is this efficient?',
        options: [
          '32 passes — one per bit of the integer',
          '8 passes — one per nibble (4-bit group)',
          '4 passes — one per byte (8-bit group), giving O(4n) = O(n) total work',
          '10 passes — one per decimal digit in a 10-digit number',
        ],
        correct: 2,
        explanation: 'A 32-bit integer has 4 bytes. Using base 256 (k = 256 buckets), each pass sorts by one byte. Four passes cover all 32 bits. Each pass is O(n + 256) = O(n), giving O(4n) total — effectively linear. Choosing a larger base reduces d but increases k; base 256 is a well-tuned sweet spot that keeps k small enough for cache while minimising d.',
      },
    ],
  },
};
