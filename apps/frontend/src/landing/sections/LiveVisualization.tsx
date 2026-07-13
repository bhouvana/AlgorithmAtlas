import { useEffect, useMemo, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { AnimateIn } from '../../components/ui/AnimateIn';
import { cn } from '../../lib/utils';

// ---------------------------------------------------------------------------
// Tiny in-browser sort-step generators — the same "record every comparison
// and swap as a frame" idea the real SimulationCanvas engine uses server-side,
// scaled down to run instantly on the client for a zero-latency hero demo.
// ---------------------------------------------------------------------------

interface Frame {
  array: number[];
  compare: [number, number] | null;
  swap: [number, number] | null;
  sorted: number[];
  comparisons: number;
  swaps: number;
}

function seededArray(seed: number, n = 16): number[] {
  let s = seed;
  const rand = () => {
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    return s / 0x7fffffff;
  };
  return Array.from({ length: n }, () => Math.floor(rand() * 84) + 12);
}

function bubbleSortFrames(input: number[]): Frame[] {
  const arr = [...input];
  const frames: Frame[] = [];
  let comparisons = 0;
  let swaps = 0;
  const sorted: number[] = [];
  for (let i = 0; i < arr.length - 1; i++) {
    let didSwap = false;
    for (let j = 0; j < arr.length - i - 1; j++) {
      comparisons++;
      frames.push({ array: [...arr], compare: [j, j + 1], swap: null, sorted: [...sorted], comparisons, swaps });
      if (arr[j] > arr[j + 1]) {
        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
        swaps++;
        didSwap = true;
        frames.push({ array: [...arr], compare: null, swap: [j, j + 1], sorted: [...sorted], comparisons, swaps });
      }
    }
    sorted.unshift(arr.length - 1 - i);
    if (!didSwap) break;
  }
  sorted.length = 0;
  for (let k = 0; k < arr.length; k++) sorted.push(k);
  frames.push({ array: [...arr], compare: null, swap: null, sorted, comparisons, swaps });
  return frames;
}

function quickSortFrames(input: number[]): Frame[] {
  const arr = [...input];
  const frames: Frame[] = [];
  let comparisons = 0;
  let swaps = 0;
  const sortedSet = new Set<number>();

  function partition(lo: number, hi: number): number {
    const pivot = arr[hi];
    let i = lo - 1;
    for (let j = lo; j < hi; j++) {
      comparisons++;
      frames.push({ array: [...arr], compare: [j, hi], swap: null, sorted: [...sortedSet], comparisons, swaps });
      if (arr[j] < pivot) {
        i++;
        if (i !== j) {
          [arr[i], arr[j]] = [arr[j], arr[i]];
          swaps++;
          frames.push({ array: [...arr], compare: null, swap: [i, j], sorted: [...sortedSet], comparisons, swaps });
        }
      }
    }
    [arr[i + 1], arr[hi]] = [arr[hi], arr[i + 1]];
    swaps++;
    frames.push({ array: [...arr], compare: null, swap: [i + 1, hi], sorted: [...sortedSet], comparisons, swaps });
    return i + 1;
  }

  function sort(lo: number, hi: number) {
    if (lo < hi) {
      const p = partition(lo, hi);
      sortedSet.add(p);
      sort(lo, p - 1);
      sort(p + 1, hi);
    } else if (lo === hi) {
      sortedSet.add(lo);
    }
  }

  sort(0, arr.length - 1);
  frames.push({ array: [...arr], compare: null, swap: null, sorted: arr.map((_, i) => i), comparisons, swaps });
  return frames;
}

function insertionSortFrames(input: number[]): Frame[] {
  const arr = [...input];
  const frames: Frame[] = [];
  let comparisons = 0;
  let swaps = 0;
  for (let i = 1; i < arr.length; i++) {
    let j = i;
    while (j > 0) {
      comparisons++;
      frames.push({ array: [...arr], compare: [j - 1, j], swap: null, sorted: Array.from({ length: i }, (_, k) => k), comparisons, swaps });
      if (arr[j - 1] > arr[j]) {
        [arr[j - 1], arr[j]] = [arr[j], arr[j - 1]];
        swaps++;
        frames.push({ array: [...arr], compare: null, swap: [j - 1, j], sorted: Array.from({ length: i }, (_, k) => k), comparisons, swaps });
        j--;
      } else break;
    }
  }
  frames.push({ array: [...arr], compare: null, swap: null, sorted: arr.map((_, i) => i), comparisons, swaps });
  return frames;
}

const ALGORITHMS = [
  { id: 'bubble', label: 'Bubble Sort', complexity: 'O(n²)', gen: bubbleSortFrames },
  { id: 'insertion', label: 'Insertion Sort', complexity: 'O(n²)', gen: insertionSortFrames },
  { id: 'quick', label: 'Quick Sort', complexity: 'O(n log n)', gen: quickSortFrames },
] as const;

type AlgoId = (typeof ALGORITHMS)[number]['id'];

const FRAME_MS = 140;
const LOOP_PAUSE_MS = 1400;

function barColor(idx: number, frame: Frame): string {
  if (frame.sorted.includes(idx)) return '#34d399';
  if (frame.swap && frame.swap.includes(idx)) return '#fb7185';
  if (frame.compare && frame.compare.includes(idx)) return '#fbbf24';
  return '#6366f1';
}

export function LiveVisualizationSection() {
  const [algoId, setAlgoId] = useState<AlgoId>('bubble');
  const [seed, setSeed] = useState(7);
  const [frameIdx, setFrameIdx] = useState(0);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const frames = useMemo(() => {
    const algo = ALGORITHMS.find((a) => a.id === algoId)!;
    return algo.gen(seededArray(seed));
  }, [algoId, seed]);

  useEffect(() => {
    setFrameIdx(0);
  }, [frames]);

  useEffect(() => {
    const isLast = frameIdx >= frames.length - 1;
    const delay = isLast ? LOOP_PAUSE_MS : FRAME_MS;
    timerRef.current = setTimeout(() => {
      if (isLast) {
        setSeed((s) => s + 1);
      } else {
        setFrameIdx((i) => i + 1);
      }
    }, delay);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [frameIdx, frames.length]);

  const frame = frames[Math.min(frameIdx, frames.length - 1)];
  const max = Math.max(...frame.array);
  const activeAlgo = ALGORITHMS.find((a) => a.id === algoId)!;

  return (
    <section className="py-24 px-4">
      <div className="max-w-5xl mx-auto">
        <AnimateIn className="text-center mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-xs font-medium mb-6">
            Live in your browser
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
            Watch algorithms think.
          </h2>
          <p className="text-zinc-400 text-lg max-w-xl mx-auto">
            Every comparison, every swap, captured as a frame and played back at your pace.
            This is a live, running simulation, not a recording.
          </p>
        </AnimateIn>

        <AnimateIn delay={0.1}>
          <div className="rounded-2xl border border-charcoal/10 bg-[#0D0D10] shadow-card overflow-hidden">
            {/* window chrome + algo tabs */}
            <div className="flex flex-wrap items-center gap-2 px-5 py-3.5 border-b border-charcoal/10 bg-white/[0.02]">
              <div className="flex items-center gap-1.5 mr-2">
                <span className="w-2.5 h-2.5 rounded-full bg-red-500/70" />
                <span className="w-2.5 h-2.5 rounded-full bg-yellow-500/70" />
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/70" />
              </div>
              <div className="flex items-center gap-1 flex-1 flex-wrap">
                {ALGORITHMS.map((a) => (
                  <button
                    key={a.id}
                    onClick={() => setAlgoId(a.id)}
                    className={cn(
                      'px-3 py-1.5 rounded-lg text-xs font-medium font-mono transition-colors duration-200',
                      algoId === a.id
                        ? 'bg-indigo-500/15 text-indigo-300 border border-indigo-500/30'
                        : 'text-zinc-500 hover:text-zinc-300 border border-transparent',
                    )}
                  >
                    {a.label}
                  </button>
                ))}
              </div>
              <span className="text-xs font-mono text-zinc-500 px-2 py-1 rounded-md bg-white/5">
                {activeAlgo.complexity}
              </span>
            </div>

            {/* bars */}
            <div className="h-64 sm:h-72 flex items-end justify-center gap-1.5 px-6 pt-10 pb-4">
              {frame.array.map((value, i) => (
                <motion.div
                  key={i}
                  className="flex-1 max-w-[28px] rounded-t-md"
                  animate={{
                    height: `${(value / max) * 100}%`,
                    backgroundColor: barColor(i, frame),
                  }}
                  transition={{ duration: FRAME_MS / 1000, ease: 'easeOut' }}
                />
              ))}
            </div>

            {/* stats row */}
            <div className="flex items-center justify-center gap-8 px-6 py-4 border-t border-charcoal/10 bg-white/[0.02] font-mono text-sm">
              <span className="text-zinc-500">
                comparisons <span className="text-zinc-200 font-semibold">{frame.comparisons}</span>
              </span>
              <span className="text-zinc-500">
                swaps <span className="text-zinc-200 font-semibold">{frame.swaps}</span>
              </span>
              <span className="text-zinc-500">
                frame <span className="text-zinc-200 font-semibold">{Math.min(frameIdx, frames.length - 1) + 1}</span>
                <span className="text-zinc-600">/{frames.length}</span>
              </span>
            </div>
          </div>
        </AnimateIn>

        <AnimateIn delay={0.2} className="flex items-center justify-center gap-6 mt-6 text-xs text-zinc-500">
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-[#6366f1]" /> unsorted</span>
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-[#fbbf24]" /> comparing</span>
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-[#fb7185]" /> swapping</span>
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-[#34d399]" /> sorted</span>
        </AnimateIn>
      </div>
    </section>
  );
}
