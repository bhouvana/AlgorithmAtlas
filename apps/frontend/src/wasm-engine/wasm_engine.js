/**
 * WASM engine — pure JavaScript fallback implementation.
 *
 * Implements the same interface as the wasm-pack compiled Rust engine.
 * Replaced by the real WASM binary when `npm run build:wasm` is run,
 * but this JS version is fully functional for all supported algorithms.
 *
 * Supported slugs: bubble-sort, insertion-sort, selection-sort,
 *                  merge-sort, quick-sort
 */

export default async function init() {
  // Nothing to initialise for the JS fallback.
}

// ── Seeded PRNG (mulberry32) ───────────────────────────────────────────────────

function mulberry32(seed) {
  return function () {
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

function makeArray(size, seed, order) {
  const rng = mulberry32(seed);
  const arr = Array.from({ length: size }, (_, i) => i + 1);

  if (order === 'random') {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(rng() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
  } else if (order === 'reversed') {
    arr.reverse();
  } else if (order === 'nearly_sorted') {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(rng() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    arr.sort((a, b) => a - b);
    const swaps = Math.max(1, Math.floor(size * 0.08));
    for (let k = 0; k < swaps; k++) {
      const i = Math.floor(rng() * size);
      const j = Math.floor(rng() * size);
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
  }
  // 'sorted' → already sorted

  return arr;
}

// ── Frame builder helpers ──────────────────────────────────────────────────────

function frame(index, array, comparing, lastSwap, sortedIndices, auxiliaryIndices, comparisons, swaps, description) {
  return {
    frame_index: index,
    timestamp_ms: index * 100,
    event_label: description || null,
    state: {
      array: [...array],
      comparing: comparing ?? null,
      last_swap: lastSwap ?? null,
      sorted_indices: [...(sortedIndices ?? [])],
      auxiliary_indices: [...(auxiliaryIndices ?? [])],
      comparisons,
      swaps,
      description: description ?? '',
    },
  };
}

// ── Bubble Sort ────────────────────────────────────────────────────────────────

function runBubbleSort(arr) {
  const frames = [];
  const a = [...arr];
  const n = a.length;
  const sorted = new Set();
  let comparisons = 0, swaps = 0, fi = 0;

  frames.push(frame(fi++, a, null, null, [...sorted], [], comparisons, swaps, 'Initial array'));

  for (let i = 0; i < n - 1; i++) {
    let swapped = false;
    for (let j = 0; j < n - i - 1; j++) {
      comparisons++;
      frames.push(frame(fi++, a, [j, j + 1], null, [...sorted], [], comparisons, swaps,
        `Compare [${j}]=${a[j]} and [${j+1}]=${a[j+1]}`));
      if (a[j] > a[j + 1]) {
        [a[j], a[j + 1]] = [a[j + 1], a[j]];
        swaps++;
        swapped = true;
        frames.push(frame(fi++, a, null, [j, j + 1], [...sorted], [], comparisons, swaps,
          `Swap [${j}] ↔ [${j+1}]`));
      }
    }
    sorted.add(n - i - 1);
    frames.push(frame(fi++, a, null, null, [...sorted], [], comparisons, swaps,
      `Position ${n-i-1} is sorted`));
    if (!swapped) break;
  }

  sorted.add(0);
  frames.push(frame(fi++, a, null, null, [...sorted], [], comparisons, swaps, 'Array sorted!'));
  return frames;
}

// ── Insertion Sort ─────────────────────────────────────────────────────────────

function runInsertionSort(arr) {
  const frames = [];
  const a = [...arr];
  const n = a.length;
  let comparisons = 0, swaps = 0, fi = 0;

  frames.push(frame(fi++, a, null, null, [0], [], comparisons, swaps, 'Initial array — index 0 trivially sorted'));

  for (let i = 1; i < n; i++) {
    const key = a[i];
    let j = i - 1;
    frames.push(frame(fi++, a, null, null,
      Array.from({length: i}, (_, k) => k), [i], comparisons, swaps,
      `Insert key=${key} from position ${i}`));

    while (j >= 0) {
      comparisons++;
      frames.push(frame(fi++, a, [j, j + 1], null,
        Array.from({length: j}, (_, k) => k), [i], comparisons, swaps,
        `Compare key=${key} with [${j}]=${a[j]}`));
      if (a[j] > key) {
        a[j + 1] = a[j];
        swaps++;
        frames.push(frame(fi++, a, null, [j, j + 1],
          Array.from({length: j}, (_, k) => k), [], comparisons, swaps,
          `Shift [${j}]=${a[j]} right`));
        j--;
      } else {
        break;
      }
    }
    a[j + 1] = key;
    frames.push(frame(fi++, a, null, null,
      Array.from({length: i + 1}, (_, k) => k), [], comparisons, swaps,
      `Placed key=${key} at position ${j+1}`));
  }

  frames.push(frame(fi++, a, null, null,
    Array.from({length: n}, (_, k) => k), [], comparisons, swaps, 'Array sorted!'));
  return frames;
}

// ── Selection Sort ─────────────────────────────────────────────────────────────

function runSelectionSort(arr) {
  const frames = [];
  const a = [...arr];
  const n = a.length;
  const sorted = new Set();
  let comparisons = 0, swaps = 0, fi = 0;

  frames.push(frame(fi++, a, null, null, [], [], comparisons, swaps, 'Initial array'));

  for (let i = 0; i < n - 1; i++) {
    let minIdx = i;
    frames.push(frame(fi++, a, null, null, [...sorted], [i], comparisons, swaps,
      `Find minimum in [${i}..${n-1}]`));

    for (let j = i + 1; j < n; j++) {
      comparisons++;
      frames.push(frame(fi++, a, [minIdx, j], null, [...sorted], [minIdx], comparisons, swaps,
        `Compare min=[${minIdx}]=${a[minIdx]} with [${j}]=${a[j]}`));
      if (a[j] < a[minIdx]) {
        minIdx = j;
        frames.push(frame(fi++, a, null, null, [...sorted], [minIdx], comparisons, swaps,
          `New minimum: [${minIdx}]=${a[minIdx]}`));
      }
    }

    if (minIdx !== i) {
      [a[i], a[minIdx]] = [a[minIdx], a[i]];
      swaps++;
      frames.push(frame(fi++, a, null, [i, minIdx], [...sorted], [], comparisons, swaps,
        `Swap [${i}] ↔ [${minIdx}]`));
    }
    sorted.add(i);
    frames.push(frame(fi++, a, null, null, [...sorted], [], comparisons, swaps,
      `Position ${i} sorted`));
  }

  sorted.add(n - 1);
  frames.push(frame(fi++, a, null, null, [...sorted], [], comparisons, swaps, 'Array sorted!'));
  return frames;
}

// ── Merge Sort ─────────────────────────────────────────────────────────────────

function runMergeSort(arr) {
  const frames = [];
  const a = [...arr];
  const n = a.length;
  let comparisons = 0, swaps = 0, fi = 0;

  frames.push(frame(fi++, a, null, null, [], [], comparisons, swaps, 'Initial array'));

  function merge(left, right, lo) {
    const merged = [];
    let i = 0, j = 0;
    while (i < left.length && j < right.length) {
      comparisons++;
      const li = lo + i, ri = lo + left.length + j;
      frames.push(frame(fi++, a, [li, ri], null, [], [], comparisons, swaps,
        `Compare ${left[i]} and ${right[j]}`));
      if (left[i] <= right[j]) {
        merged.push(left[i++]);
      } else {
        merged.push(right[j++]);
      }
    }
    while (i < left.length) merged.push(left[i++]);
    while (j < right.length) merged.push(right[j++]);

    for (let k = 0; k < merged.length; k++) {
      a[lo + k] = merged[k];
      swaps++;
    }
    frames.push(frame(fi++, a, null, null, [], [], comparisons, swaps,
      `Merged [${lo}..${lo + merged.length - 1}]`));
  }

  function sort(lo, hi) {
    if (hi - lo <= 0) return;
    const mid = Math.floor((lo + hi) / 2);
    frames.push(frame(fi++, a, null, null, [], [lo, mid, hi], comparisons, swaps,
      `Split [${lo}..${hi}] at mid=${mid}`));
    sort(lo, mid);
    sort(mid + 1, hi);
    merge(a.slice(lo, mid + 1), a.slice(mid + 1, hi + 1), lo);
  }

  sort(0, n - 1);
  frames.push(frame(fi++, a, null, null,
    Array.from({ length: n }, (_, i) => i), [], comparisons, swaps, 'Array sorted!'));
  return frames;
}

// ── Quick Sort ─────────────────────────────────────────────────────────────────

function runQuickSort(arr) {
  const frames = [];
  const a = [...arr];
  const n = a.length;
  const sorted = new Set();
  let comparisons = 0, swaps = 0, fi = 0;

  frames.push(frame(fi++, a, null, null, [], [], comparisons, swaps, 'Initial array'));

  function partition(lo, hi) {
    const pivot = a[hi];
    frames.push(frame(fi++, a, null, null, [...sorted], [hi], comparisons, swaps,
      `Pivot = ${pivot} at [${hi}]`));
    let i = lo - 1;

    for (let j = lo; j < hi; j++) {
      comparisons++;
      frames.push(frame(fi++, a, [j, hi], null, [...sorted], [hi], comparisons, swaps,
        `Compare [${j}]=${a[j]} with pivot=${pivot}`));
      if (a[j] <= pivot) {
        i++;
        if (i !== j) {
          [a[i], a[j]] = [a[j], a[i]];
          swaps++;
          frames.push(frame(fi++, a, null, [i, j], [...sorted], [hi], comparisons, swaps,
            `Swap [${i}] ↔ [${j}]`));
        }
      }
    }
    const pivotIdx = i + 1;
    if (pivotIdx !== hi) {
      [a[pivotIdx], a[hi]] = [a[hi], a[pivotIdx]];
      swaps++;
      frames.push(frame(fi++, a, null, [pivotIdx, hi], [...sorted], [], comparisons, swaps,
        `Place pivot at [${pivotIdx}]`));
    }
    sorted.add(pivotIdx);
    frames.push(frame(fi++, a, null, null, [...sorted], [], comparisons, swaps,
      `Pivot ${pivot} in final position ${pivotIdx}`));
    return pivotIdx;
  }

  function sort(lo, hi) {
    if (lo >= hi) {
      if (lo === hi) sorted.add(lo);
      return;
    }
    const p = partition(lo, hi);
    sort(lo, p - 1);
    sort(p + 1, hi);
  }

  sort(0, n - 1);
  const allSorted = Array.from({ length: n }, (_, i) => i);
  frames.push(frame(fi++, a, null, null, allSorted, [], comparisons, swaps, 'Array sorted!'));
  return frames;
}

// ── Dispatcher ────────────────────────────────────────────────────────────────

const SORT_RUNNERS = {
  'bubble-sort':    runBubbleSort,
  'insertion-sort': runInsertionSort,
  'selection-sort': runSelectionSort,
  'merge-sort':     runMergeSort,
  'quick-sort':     runQuickSort,
};

export function run_sort(slug, seed, arraySize, inputOrder) {
  const runner = SORT_RUNNERS[slug];
  if (!runner) {
    console.warn(`[wasm-engine] Unknown algorithm slug: "${slug}"`);
    return '[]';
  }
  const arr = makeArray(arraySize, seed, inputOrder);
  try {
    const frames = runner(arr);
    return JSON.stringify(frames);
  } catch (err) {
    console.error(`[wasm-engine] Error running "${slug}":`, err);
    return '[]';
  }
}

export function benchmark_sort(slug, seed, arraySize, inputOrder, trials) {
  const runner = SORT_RUNNERS[slug];
  if (!runner) return 0;
  let total = 0;
  for (let t = 0; t < trials; t++) {
    const arr = makeArray(arraySize, seed + t, inputOrder);
    const start = performance.now();
    runner(arr);
    total += performance.now() - start;
  }
  return total / trials;
}
