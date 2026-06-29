/**
 * ArrayBarRenderer — renders SortState as an animated bar chart.
 *
 * Color priority (high → low):
 *   sorted     → emerald  (confirmed in final position)
 *   last_swap  → rose     (elements just swapped)
 *   comparing  → amber    (elements being compared)
 *   auxiliary  → yellow   (pivot, tracked minimum, etc.)
 *   default    → indigo   (unsorted, not active)
 */

import { useMemo } from 'react';

interface SortState {
  array: number[];
  comparing: [number, number] | null;
  last_swap: [number, number] | null;
  sorted_indices: number[];
  auxiliary_indices: number[];
  comparisons: number;
  swaps: number;
  description: string;
}

type BarColor = 'indigo' | 'amber' | 'rose' | 'emerald' | 'yellow';

const COLORS: Record<BarColor, { bg: string; shadow: string; label: string }> = {
  indigo:  { bg: 'bg-indigo-500',  shadow: 'shadow-indigo-500/30',  label: 'Unsorted'  },
  amber:   { bg: 'bg-amber-400',   shadow: 'shadow-amber-400/60',   label: 'Comparing' },
  rose:    { bg: 'bg-rose-500',    shadow: 'shadow-rose-500/70',    label: 'Swapped'   },
  emerald: { bg: 'bg-emerald-500', shadow: 'shadow-emerald-500/40', label: 'Sorted'    },
  yellow:  { bg: 'bg-yellow-300',  shadow: 'shadow-yellow-300/50',  label: 'Auxiliary' },
};

function getBarColor(
  index: number,
  comparing: [number, number] | null,
  lastSwap: [number, number] | null,
  sortedSet: Set<number>,
  auxiliarySet: Set<number>,
): BarColor {
  if (sortedSet.has(index)) return 'emerald';
  if (lastSwap && (lastSwap[0] === index || lastSwap[1] === index)) return 'rose';
  if (comparing && (comparing[0] === index || comparing[1] === index)) return 'amber';
  if (auxiliarySet.has(index)) return 'yellow';
  return 'indigo';
}

export function ArrayBarRenderer({ state }: { state: Record<string, unknown> }) {
  const s = state as unknown as SortState;

  const sortedSet    = useMemo(() => new Set(s.sorted_indices   ?? []), [s.sorted_indices]);
  const auxiliarySet = useMemo(() => new Set(s.auxiliary_indices ?? []), [s.auxiliary_indices]);
  const maxVal       = useMemo(() => Math.max(...(s.array ?? [1]), 1), [s.array]);

  if (!s.array || s.array.length === 0) {
    return <div className="flex items-center justify-center h-64 text-zinc-500">No array data</div>;
  }

  const n = s.array.length;
  // Show value labels only when bars are wide enough
  const showLabels = n <= 30;

  return (
    <div className="flex flex-col gap-4 select-none w-full">
      {/* Bar chart */}
      <div
        className="flex items-end w-full rounded-xl overflow-hidden"
        style={{ height: '300px', gap: n > 60 ? '1px' : n > 30 ? '2px' : '3px' }}
        aria-label={`Array of ${n} elements`}
      >
        {s.array.map((value, index) => {
          const color         = getBarColor(index, s.comparing, s.last_swap, sortedSet, auxiliarySet);
          const { bg, shadow } = COLORS[color];
          const heightPct     = Math.max(2, (value / maxVal) * 100);
          const isActive      = color === 'amber' || color === 'rose';
          const isSorted      = color === 'emerald';

          return (
            <div
              key={index}
              className="flex-1 flex flex-col items-center justify-end"
              style={{ height: '100%' }}
            >
              <div
                className={[
                  'w-full rounded-t-sm',
                  bg,
                  isActive ? `shadow-lg ${shadow}` : '',
                  isSorted  ? `shadow-sm ${shadow}` : '',
                ].join(' ')}
                style={{
                  height: `${heightPct}%`,
                  transition: 'height 0.18s cubic-bezier(0.4,0,0.2,1), background-color 0.18s ease',
                  transform: isActive ? 'scaleX(1.08)' : 'scaleX(1)',
                }}
                title={`[${index}] = ${value}`}
              >
                {showLabels && heightPct > 18 && (
                  <span
                    className="flex justify-center text-[8px] font-mono font-bold pt-0.5"
                    style={{ color: 'rgba(255,255,255,0.75)' }}
                  >
                    {value}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Stats row */}
      <div className="flex items-center justify-between px-1">
        <div className="flex gap-4 text-xs text-zinc-500 flex-wrap">
          {(['amber', 'rose', 'emerald', 'yellow', 'indigo'] as BarColor[])
            .filter(c => c !== 'yellow' || auxiliarySet.size > 0)
            .map(c => (
              <span key={c} className="flex items-center gap-1.5">
                <span className={`inline-block w-2.5 h-2.5 rounded-sm ${COLORS[c].bg}`} />
                {COLORS[c].label}
              </span>
            ))}
        </div>
        <div className="flex gap-4 text-xs font-mono">
          <span className="text-zinc-500">cmp <span className="text-white font-semibold">{(s.comparisons ?? 0).toLocaleString()}</span></span>
          <span className="text-zinc-500">swap <span className="text-white font-semibold">{(s.swaps ?? 0).toLocaleString()}</span></span>
        </div>
      </div>

      {/* Description */}
      {s.description && (
        <p className="text-center text-xs font-mono text-zinc-500 px-4 min-h-4">
          {s.description}
        </p>
      )}
    </div>
  );
}
