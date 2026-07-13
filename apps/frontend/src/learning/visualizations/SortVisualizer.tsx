import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Pause, SkipBack, SkipForward, RotateCcw, Shuffle, ChevronLeft, ChevronRight } from 'lucide-react';

export type SortAlgo = 'bubble' | 'selection' | 'insertion' | 'merge' | 'quick';

interface SortFrame {
  array: number[];
  comparing: number[];   // indices being compared
  swapping: number[];    // indices being swapped
  sorted: number[];      // indices confirmed sorted
  pivot: number | null;  // pivot index (quick sort)
  description: string;
}

// ── Bubble Sort frames ──────────────────────────────────────────────────────
function buildBubbleFrames(arr: number[]): SortFrame[] {
  const frames: SortFrame[] = [];
  const a = [...arr];
  const sorted: number[] = [];

  frames.push({ array: [...a], comparing: [], swapping: [], sorted: [], pivot: null, description: 'Starting bubble sort. We compare adjacent elements and swap them if they are out of order.' });

  for (let i = 0; i < a.length; i++) {
    let swapped = false;
    for (let j = 0; j < a.length - i - 1; j++) {
      frames.push({ array: [...a], comparing: [j, j + 1], swapping: [], sorted: [...sorted], pivot: null, description: `Comparing a[${j}]=${a[j]} and a[${j+1}]=${a[j+1]}` });
      if (a[j] > a[j + 1]) {
        [a[j], a[j + 1]] = [a[j + 1], a[j]];
        swapped = true;
        frames.push({ array: [...a], comparing: [], swapping: [j, j + 1], sorted: [...sorted], pivot: null, description: `Swapped! ${a[j+1]} > ${a[j]}, so we move the larger element right.` });
      }
    }
    sorted.unshift(a.length - 1 - i);
    frames.push({ array: [...a], comparing: [], swapping: [], sorted: [...sorted], pivot: null, description: `Pass ${i + 1} complete. The largest unsorted element is now in its final position.` });
    if (!swapped) { frames.push({ array: [...a], comparing: [], swapping: [], sorted: [...a.keys()], pivot: null, description: 'No swaps in this pass — the array is sorted! Early exit.' }); break; }
  }
  frames.push({ array: [...a], comparing: [], swapping: [], sorted: [...a.keys()], pivot: null, description: '✅ Array is fully sorted!' });
  return frames;
}

// ── Insertion Sort frames ───────────────────────────────────────────────────
function buildInsertionFrames(arr: number[]): SortFrame[] {
  const frames: SortFrame[] = [];
  const a = [...arr];
  frames.push({ array: [...a], comparing: [], swapping: [], sorted: [0], pivot: null, description: 'Starting insertion sort. We build a sorted portion from left to right.' });

  for (let i = 1; i < a.length; i++) {
    const key = a[i];
    let j = i - 1;
    frames.push({ array: [...a], comparing: [i], swapping: [], sorted: [...Array(i).keys()], pivot: null, description: `Picking up element ${key} at index ${i} to insert into sorted portion.` });
    while (j >= 0 && a[j] > key) {
      frames.push({ array: [...a], comparing: [j, j + 1], swapping: [], sorted: [...Array(i).keys()], pivot: null, description: `${a[j]} > ${key}: shift ${a[j]} one position to the right.` });
      a[j + 1] = a[j];
      frames.push({ array: [...a], comparing: [], swapping: [j, j + 1], sorted: [...Array(i).keys()], pivot: null, description: `Shifted ${a[j]} right.` });
      j--;
    }
    a[j + 1] = key;
    frames.push({ array: [...a], comparing: [], swapping: [], sorted: [...Array(i + 1).keys()], pivot: null, description: `Inserted ${key} at position ${j + 1}. Sorted portion now has ${i + 1} elements.` });
  }
  frames.push({ array: [...a], comparing: [], swapping: [], sorted: [...a.keys()], pivot: null, description: '✅ Array is fully sorted!' });
  return frames;
}

// ── Selection Sort frames ───────────────────────────────────────────────────
function buildSelectionFrames(arr: number[]): SortFrame[] {
  const frames: SortFrame[] = [];
  const a = [...arr];
  const sorted: number[] = [];
  frames.push({ array: [...a], comparing: [], swapping: [], sorted: [], pivot: null, description: 'Starting selection sort. Each pass finds the minimum and places it.' });

  for (let i = 0; i < a.length - 1; i++) {
    let minIdx = i;
    frames.push({ array: [...a], comparing: [i], swapping: [], sorted: [...sorted], pivot: minIdx, description: `Pass ${i + 1}: scanning for the minimum element from index ${i}.` });
    for (let j = i + 1; j < a.length; j++) {
      frames.push({ array: [...a], comparing: [j, minIdx], swapping: [], sorted: [...sorted], pivot: minIdx, description: `Comparing a[${j}]=${a[j]} with current min a[${minIdx}]=${a[minIdx]}.` });
      if (a[j] < a[minIdx]) {
        minIdx = j;
        frames.push({ array: [...a], comparing: [j], swapping: [], sorted: [...sorted], pivot: minIdx, description: `New minimum found: ${a[minIdx]} at index ${minIdx}.` });
      }
    }
    if (minIdx !== i) {
      [a[i], a[minIdx]] = [a[minIdx], a[i]];
      frames.push({ array: [...a], comparing: [], swapping: [i, minIdx], sorted: [...sorted], pivot: null, description: `Swapping minimum ${a[i]} to position ${i}.` });
    }
    sorted.push(i);
    frames.push({ array: [...a], comparing: [], swapping: [], sorted: [...sorted], pivot: null, description: `${a[i]} placed at position ${i} — now in its final sorted position.` });
  }
  frames.push({ array: [...a], comparing: [], swapping: [], sorted: [...a.keys()], pivot: null, description: '✅ Array is fully sorted!' });
  return frames;
}

function buildFrames(algo: SortAlgo, arr: number[]): SortFrame[] {
  if (algo === 'bubble')    return buildBubbleFrames(arr);
  if (algo === 'insertion') return buildInsertionFrames(arr);
  if (algo === 'selection') return buildSelectionFrames(arr);
  return buildBubbleFrames(arr);
}

function randomArray(size = 12): number[] {
  return Array.from({ length: size }, () => Math.floor(Math.random() * 95) + 5);
}

interface Props {
  algorithm?: SortAlgo;
  showAlgoSelector?: boolean;
  initialArray?: number[];
  size?: number;
}

export function SortVisualizer({ algorithm = 'bubble', showAlgoSelector = true, initialArray, size = 12 }: Props) {
  const [algo, setAlgo] = useState<SortAlgo>(algorithm);
  const [baseArray, setBaseArray] = useState(() => initialArray ?? randomArray(size));
  const [frames, setFrames] = useState<SortFrame[]>([]);
  const [frameIdx, setFrameIdx] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(3); // 1–5
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const reset = useCallback((arr?: number[]) => {
    const a = arr ?? baseArray;
    setFrames(buildFrames(algo, a));
    setFrameIdx(0);
    setPlaying(false);
  }, [algo, baseArray]);

  useEffect(() => { reset(); }, [algo, baseArray]);

  useEffect(() => {
    if (!playing) { if (intervalRef.current) clearInterval(intervalRef.current); return; }
    const delay = [600, 400, 220, 120, 50][speed - 1];
    intervalRef.current = setInterval(() => {
      setFrameIdx((idx) => {
        if (idx >= frames.length - 1) { setPlaying(false); return idx; }
        return idx + 1;
      });
    }, delay);
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [playing, speed, frames.length]);

  const shuffle = () => {
    const a = randomArray(size);
    setBaseArray(a);
    reset(a);
  };

  const frame = frames[frameIdx];
  if (!frame) return null;

  const maxVal = Math.max(...frame.array);
  const ALGOS: { id: SortAlgo; label: string }[] = [
    { id: 'bubble', label: 'Bubble' },
    { id: 'insertion', label: 'Insertion' },
    { id: 'selection', label: 'Selection' },
  ];

  return (
    <div className="space-y-4">
      {showAlgoSelector && (
        <div className="flex gap-2 flex-wrap">
          {ALGOS.map((a) => (
            <button
              key={a.id}
              onClick={() => { setAlgo(a.id); }}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-150 border ${
                algo === a.id
                  ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300'
                  : 'border-charcoal/10 text-zinc-400 hover:text-zinc-200 hover:border-white/20'
              }`}
            >
              {a.label} Sort
            </button>
          ))}
        </div>
      )}

      {/* Array bars */}
      <div className="relative rounded-xl bg-zinc-950/60 border border-charcoal/10 p-4 pt-6 overflow-hidden">
        <div className="flex items-end justify-center gap-1 h-40">
          {frame.array.map((val, i) => {
            const isComparing = frame.comparing.includes(i);
            const isSwapping  = frame.swapping.includes(i);
            const isSorted    = frame.sorted.includes(i);
            const isPivot     = frame.pivot === i;
            const height = Math.round((val / maxVal) * 100);

            let barColor = 'bg-zinc-600';
            if (isSorted)    barColor = 'bg-emerald-500';
            if (isComparing) barColor = 'bg-indigo-400';
            if (isSwapping)  barColor = 'bg-amber-400';
            if (isPivot)     barColor = 'bg-rose-400';

            return (
              <motion.div
                key={i}
                layout
                className={`relative rounded-t-sm flex-1 min-w-0 transition-colors duration-150 ${barColor}`}
                style={{ height: `${height}%` }}
                animate={{ height: `${height}%` }}
                transition={{ type: 'spring', stiffness: 300, damping: 25 }}
              >
                {frame.array.length <= 16 && (
                  <span className="absolute -top-5 left-0 right-0 text-center text-[9px] font-mono text-zinc-400">
                    {val}
                  </span>
                )}
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Description */}
      <AnimatePresence mode="wait">
        <motion.div
          key={frameIdx}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={{ duration: 0.15 }}
          className="min-h-[2.5rem] px-3 py-2 rounded-lg bg-zinc-900/50 border border-charcoal/10 text-sm text-zinc-300"
        >
          {frame.description}
        </motion.div>
      </AnimatePresence>

      {/* Legend */}
      <div className="flex gap-4 text-xs text-zinc-500 flex-wrap">
        {[
          { color: 'bg-indigo-400', label: 'Comparing' },
          { color: 'bg-amber-400',  label: 'Swapping'  },
          { color: 'bg-emerald-500',label: 'Sorted'    },
          { color: 'bg-zinc-600',   label: 'Unsorted'  },
        ].map((item) => (
          <span key={item.label} className="flex items-center gap-1.5">
            <span className={`w-2.5 h-2.5 rounded-sm ${item.color}`} />
            {item.label}
          </span>
        ))}
      </div>

      {/* Controls */}
      <div className="flex items-center gap-2 flex-wrap">
        <div className="flex items-center gap-1 bg-zinc-900/60 rounded-lg p-1 border border-charcoal/10">
          <button onClick={() => setFrameIdx(0)} className="p-1.5 text-zinc-400 hover:text-white rounded transition-colors" title="Restart">
            <SkipBack size={14} />
          </button>
          <button onClick={() => setFrameIdx((i) => Math.max(0, i - 1))} className="p-1.5 text-zinc-400 hover:text-white rounded transition-colors" title="Step back">
            <ChevronLeft size={14} />
          </button>
          <button
            onClick={() => setPlaying((p) => !p)}
            className="px-3 py-1.5 bg-indigo-500 hover:bg-indigo-400 rounded text-white transition-colors flex items-center gap-1.5 text-xs font-medium"
          >
            {playing ? <Pause size={12} /> : <Play size={12} />}
            {playing ? 'Pause' : 'Play'}
          </button>
          <button onClick={() => setFrameIdx((i) => Math.min(frames.length - 1, i + 1))} className="p-1.5 text-zinc-400 hover:text-white rounded transition-colors" title="Step forward">
            <ChevronRight size={14} />
          </button>
          <button onClick={() => setFrameIdx(frames.length - 1)} className="p-1.5 text-zinc-400 hover:text-white rounded transition-colors" title="Jump to end">
            <SkipForward size={14} />
          </button>
        </div>

        <button onClick={shuffle} className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-charcoal/10 text-xs text-zinc-400 hover:text-white hover:border-white/20 transition-all">
          <Shuffle size={12} /> Shuffle
        </button>
        <button onClick={() => reset()} className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-charcoal/10 text-xs text-zinc-400 hover:text-white hover:border-white/20 transition-all">
          <RotateCcw size={12} /> Reset
        </button>

        {/* Speed */}
        <div className="flex items-center gap-2 ml-auto">
          <span className="text-xs text-zinc-500">Speed</span>
          <input
            type="range" min={1} max={5} value={speed}
            onChange={(e) => setSpeed(Number(e.target.value))}
            className="w-20 accent-indigo-500"
          />
        </div>
      </div>

      {/* Progress */}
      <div className="flex items-center gap-2">
        <div className="flex-1 h-1 bg-zinc-800 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-indigo-500 rounded-full"
            animate={{ width: `${frames.length > 1 ? (frameIdx / (frames.length - 1)) * 100 : 0}%` }}
            transition={{ duration: 0.1 }}
          />
        </div>
        <span className="text-xs text-zinc-500 tabular-nums">
          {frameIdx + 1} / {frames.length}
        </span>
      </div>
    </div>
  );
}
