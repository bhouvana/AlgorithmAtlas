import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Pause, ChevronLeft, ChevronRight, RotateCcw, Target } from 'lucide-react';

interface SearchFrame {
  array: number[];
  low: number;
  high: number;
  mid: number | null;
  found: number | null;
  eliminated: number[];
  description: string;
  step: number;
}

function buildBinarySearchFrames(arr: number[], target: number): SearchFrame[] {
  const frames: SearchFrame[] = [];
  const sorted = [...arr].sort((a, b) => a - b);
  let low = 0, high = sorted.length - 1;
  const eliminated: number[] = [];
  let step = 0;

  frames.push({ array: sorted, low, high, mid: null, found: null, eliminated: [], description: `Searching for ${target} in a sorted array of ${sorted.length} elements.`, step });

  while (low <= high) {
    const mid = Math.floor((low + high) / 2);
    step++;
    frames.push({ array: sorted, low, high, mid, found: null, eliminated: [...eliminated], description: `Step ${step}: mid = ⌊(${low} + ${high}) / 2⌋ = ${mid}. Checking a[${mid}] = ${sorted[mid]}.`, step });

    if (sorted[mid] === target) {
      frames.push({ array: sorted, low, high, mid, found: mid, eliminated: [...eliminated], description: `Found! ${target} is at index ${mid}. Binary search took ${step} step${step > 1 ? 's' : ''}. Linear would need up to ${sorted.length}.`, step });
      return frames;
    } else if (sorted[mid] < target) {
      for (let i = low; i <= mid; i++) eliminated.push(i);
      frames.push({ array: sorted, low: mid + 1, high, mid, found: null, eliminated: [...eliminated], description: `${sorted[mid]} < ${target}: target is in the RIGHT half. Eliminated indices ${low}–${mid}. Search space: ${high - mid} elements.`, step });
      low = mid + 1;
    } else {
      for (let i = mid; i <= high; i++) eliminated.push(i);
      frames.push({ array: sorted, low, high: mid - 1, mid, found: null, eliminated: [...eliminated], description: `${sorted[mid]} > ${target}: target is in the LEFT half. Eliminated indices ${mid}–${high}. Search space: ${mid - low} elements.`, step });
      high = mid - 1;
    }
  }

  frames.push({ array: sorted, low, high, mid: null, found: null, eliminated: [...eliminated], description: `${target} is not in the array. Search complete after ${step} step${step > 1 ? 's' : ''}.`, step });
  return frames;
}

function randomSortedArray(size = 16): number[] {
  const set = new Set<number>();
  while (set.size < size) set.add(Math.floor(Math.random() * 98) + 1);
  return [...set].sort((a, b) => a - b);
}

export function BinarySearchVisualizer() {
  const [array, setArray] = useState(() => randomSortedArray(16));
  const [targetIdx, setTargetIdx] = useState(7);
  const [frames, setFrames] = useState<SearchFrame[]>([]);
  const [frameIdx, setFrameIdx] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [searching, setSearching] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const startSearch = useCallback(() => {
    const t = array[targetIdx];
    const f = buildBinarySearchFrames(array, t);
    setFrames(f);
    setFrameIdx(0);
    setSearching(true);
    setPlaying(false);
  }, [array, targetIdx]);

  const reset = () => {
    const a = randomSortedArray(16);
    setArray(a);
    setTargetIdx(Math.floor(Math.random() * 16));
    setFrames([]);
    setFrameIdx(0);
    setSearching(false);
    setPlaying(false);
  };

  useEffect(() => {
    if (!playing) { if (intervalRef.current) clearInterval(intervalRef.current); return; }
    intervalRef.current = setInterval(() => {
      setFrameIdx((idx) => {
        if (idx >= frames.length - 1) { setPlaying(false); return idx; }
        return idx + 1;
      });
    }, 700);
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [playing, frames.length]);

  const frame = searching && frames[frameIdx] ? frames[frameIdx] : null;
  const displayArray = frame ? frame.array : array;

  return (
    <div className="space-y-4">
      {/* Target selector */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex items-center gap-2 text-sm">
          <Target size={14} className="text-indigo-400" />
          <span className="text-zinc-400">Search target:</span>
          <span className="font-mono text-indigo-300 text-base font-semibold">{array[targetIdx]}</span>
        </div>
        <div className="flex gap-1 ml-auto">
          {!searching ? (
            <button
              onClick={startSearch}
              className="flex items-center gap-1.5 px-4 py-2 bg-indigo-500 hover:bg-indigo-400 rounded-lg text-white text-sm font-medium transition-colors"
            >
              <Play size={13} /> Start Search
            </button>
          ) : (
            <>
              <button onClick={() => setFrameIdx((i) => Math.max(0, i - 1))} className="p-2 text-zinc-400 hover:text-white border border-white/10 rounded-lg transition-colors">
                <ChevronLeft size={14} />
              </button>
              <button
                onClick={() => setPlaying((p) => !p)}
                className="px-3 py-2 bg-indigo-500 hover:bg-indigo-400 rounded-lg text-white text-sm transition-colors flex items-center gap-1.5"
              >
                {playing ? <Pause size={13} /> : <Play size={13} />}
              </button>
              <button onClick={() => setFrameIdx((i) => Math.min(frames.length - 1, i + 1))} className="p-2 text-zinc-400 hover:text-white border border-white/10 rounded-lg transition-colors">
                <ChevronRight size={14} />
              </button>
            </>
          )}
          <button onClick={reset} className="flex items-center gap-1.5 px-3 py-2 border border-white/10 rounded-lg text-sm text-zinc-400 hover:text-white transition-colors">
            <RotateCcw size={13} /> New Array
          </button>
        </div>
      </div>

      {/* Array display */}
      <div className="rounded-xl bg-zinc-950/60 border border-white/8 p-4 overflow-x-auto">
        <div className="flex gap-1 min-w-max mx-auto" style={{ width: 'fit-content' }}>
          {displayArray.map((val, i) => {
            const isElim  = frame?.eliminated.includes(i);
            const isActive = frame?.low !== undefined && frame?.high !== undefined && i >= frame.low && i <= frame.high;
            const isMid   = frame?.mid === i;
            const isFound = frame?.found === i;
            const isTarget = !searching && i === targetIdx;

            let bg = 'bg-zinc-800/80 border-white/8 text-zinc-300';
            if (isTarget) bg = 'bg-indigo-500/30 border-indigo-500/50 text-indigo-300';
            if (searching) {
              if (isElim)  bg = 'bg-zinc-900/40 border-white/4 text-zinc-600';
              else if (isFound) bg = 'bg-emerald-500/30 border-emerald-500/50 text-emerald-300 ring-1 ring-emerald-500/50';
              else if (isMid)   bg = 'bg-amber-500/30 border-amber-500/50 text-amber-300 ring-1 ring-amber-500/50';
              else if (isActive) bg = 'bg-indigo-500/20 border-indigo-500/30 text-indigo-300';
              else bg = 'bg-zinc-900/40 border-white/4 text-zinc-600';
            }

            return (
              <motion.div
                key={i}
                animate={{ opacity: isElim ? 0.35 : 1 }}
                transition={{ duration: 0.3 }}
                className={`relative flex flex-col items-center gap-0.5`}
              >
                <div className={`w-10 h-10 flex items-center justify-center rounded-lg border text-xs font-mono font-semibold transition-all duration-300 ${bg}`}>
                  {val}
                </div>
                <span className="text-[9px] text-zinc-600 font-mono">{i}</span>
                {isMid && (
                  <motion.div
                    initial={{ opacity: 0, y: -4 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute -top-5 text-[9px] font-mono text-amber-400 whitespace-nowrap"
                  >
                    mid
                  </motion.div>
                )}
                {isFound && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="absolute -top-5 text-[9px] font-mono text-emerald-400"
                  >
                    ✓
                  </motion.div>
                )}
              </motion.div>
            );
          })}
        </div>

        {/* Bracket showing search range */}
        {frame && frame.low !== undefined && (
          <div className="mt-3 flex items-center justify-center">
            <div className="text-xs text-zinc-500 font-mono">
              Search window: [{frame.low} .. {Math.max(frame.low, frame.high)}]
              {' '}({Math.max(0, frame.high - frame.low + 1)} elements)
            </div>
          </div>
        )}
      </div>

      {/* Description */}
      {frame && (
        <AnimatePresence mode="wait">
          <motion.div
            key={frameIdx}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.15 }}
            className="px-4 py-3 rounded-lg bg-zinc-900/50 border border-white/5 text-sm text-zinc-300"
          >
            {frame.description}
          </motion.div>
        </AnimatePresence>
      )}

      {!searching && (
        <p className="text-sm text-zinc-500 text-center">
          Click on an element to change the search target, then hit Start Search.
        </p>
      )}

      {/* Legend */}
      <div className="flex gap-4 text-xs text-zinc-500 flex-wrap">
        {[
          { color: 'bg-amber-500/40 border-amber-500/50',   label: 'Mid pointer' },
          { color: 'bg-indigo-500/20 border-indigo-500/30', label: 'Active range' },
          { color: 'bg-emerald-500/30 border-emerald-500/50',label: 'Found' },
          { color: 'bg-zinc-900/40 border-white/4',         label: 'Eliminated' },
        ].map((item) => (
          <span key={item.label} className="flex items-center gap-1.5">
            <span className={`w-3 h-3 rounded border ${item.color}`} />
            {item.label}
          </span>
        ))}
      </div>
    </div>
  );
}
