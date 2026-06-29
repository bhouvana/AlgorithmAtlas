/**
 * ArraySearchRenderer — renders SearchState.
 *
 * Color semantics:
 *   found      → green   (target located)
 *   current    → amber   (index currently examined)
 *   eliminated → neutral (ruled out by the search algorithm)
 *   in_range   → indigo  (within active search bounds, not yet eliminated)
 *   out_range  → neutral/dark (outside current [low, high] window)
 *
 * Search bounds (low/high) are shown as bracket markers above the bar chart.
 */

import { useMemo } from 'react';

interface SearchState {
  array: number[];
  target: number;
  current: number | null;
  low: number | null;
  high: number | null;
  eliminated: number[];
  found_at: number | null;
  comparisons: number;
  description: string;
}

interface ArraySearchRendererProps {
  state: Record<string, unknown>;
}

type BarColor = 'green' | 'amber' | 'indigo' | 'neutral' | 'dark';

const COLOR_CLASSES: Record<BarColor, string> = {
  green:   'bg-emerald-500',
  amber:   'bg-amber-400',
  indigo:  'bg-indigo-500',
  neutral: 'bg-neutral-600',
  dark:    'bg-neutral-800',
};

function getBarColor(
  index: number,
  s: SearchState,
  eliminatedSet: Set<number>,
): BarColor {
  if (s.found_at === index) return 'green';
  if (s.current === index) return 'amber';
  if (eliminatedSet.has(index)) return 'neutral';
  if (s.low !== null && s.high !== null) {
    if (index >= s.low && index <= s.high) return 'indigo';
    return 'dark';
  }
  return 'indigo';
}

export function ArraySearchRenderer({ state }: ArraySearchRendererProps) {
  const s = state as unknown as SearchState;

  const eliminatedSet = useMemo(
    () => new Set(s.eliminated ?? []),
    [s.eliminated],
  );

  const maxVal = useMemo(
    () => Math.max(...(s.array ?? [1]), 1),
    [s.array],
  );

  if (!s.array || s.array.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-neutral-400">
        No array data
      </div>
    );
  }

  const hasRange = s.low !== null && s.high !== null;

  return (
    <div className="flex flex-col gap-4 select-none">
      {/* Target indicator */}
      <div className="text-center text-sm text-neutral-300">
        Searching for{' '}
        <span className="font-mono font-bold text-amber-300">{s.target}</span>
        {s.found_at !== null && (
          <span className="ml-2 text-emerald-400 font-semibold">
            — found at index {s.found_at}!
          </span>
        )}
        {s.found_at === null && s.eliminated.length === s.array.length && (
          <span className="ml-2 text-red-400 font-semibold">— not found</span>
        )}
      </div>

      {/* Range label */}
      {hasRange && (
        <div className="text-center text-xs text-neutral-500">
          Active range: [{s.low} … {s.high}]
        </div>
      )}

      {/* Bar chart */}
      <div
        className="flex items-end gap-0.5 w-full relative"
        style={{ height: '280px' }}
        aria-label={`Array of ${s.array.length} elements, searching for ${s.target}`}
      >
        {s.array.map((value, index) => {
          const color = getBarColor(index, s, eliminatedSet);
          const heightPercent = (value / maxVal) * 100;
          const isLowBound = s.low === index;
          const isHighBound = s.high === index;

          return (
            <div
              key={index}
              className="flex-1 flex flex-col items-center justify-end relative"
              style={{ height: '100%' }}
            >
              {/* Bracket markers */}
              {(isLowBound || isHighBound) && (
                <span
                  className="absolute top-0 text-xs text-sky-400 font-mono leading-none"
                  title={isLowBound ? 'low' : 'high'}
                >
                  {isLowBound ? 'L' : 'H'}
                </span>
              )}
              <div
                className={`w-full rounded-t transition-all duration-75 ${COLOR_CLASSES[color]}`}
                style={{ height: `${heightPercent}%` }}
                title={`[${index}] = ${value}`}
              />
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex gap-4 text-xs text-neutral-400 justify-center flex-wrap">
        <LegendItem color="amber" label="Examining" />
        <LegendItem color="green" label="Found" />
        <LegendItem color="indigo" label="In Range" />
        <LegendItem color="neutral" label="Eliminated" />
        <LegendItem color="dark" label="Out of Range" />
      </div>

      {/* Metrics */}
      <div className="flex gap-6 justify-center text-sm text-neutral-300">
        <Metric label="Comparisons" value={s.comparisons} />
        <Metric label="Eliminated" value={s.eliminated?.length ?? 0} />
        <Metric label="Size" value={s.array.length} />
      </div>

      {/* Event description */}
      {s.description && (
        <div className="text-center text-xs text-neutral-400 italic px-4 min-h-[1.25rem]">
          {s.description}
        </div>
      )}
    </div>
  );
}

function LegendItem({ color, label }: { color: BarColor; label: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <div className={`w-3 h-3 rounded-sm ${COLOR_CLASSES[color]}`} />
      <span>{label}</span>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex flex-col items-center">
      <span className="text-neutral-500 text-xs uppercase tracking-wider">{label}</span>
      <span className="font-mono font-semibold text-white">{value.toLocaleString()}</span>
    </div>
  );
}
