/**
 * ParticleFieldRenderer — renders CellularAutomataState (PARTICLE_FIELD).
 *
 * Draws a 2-D grid where each cell is a colored square.
 * Cell value semantics (algorithm-defined, but common convention):
 *   0 = dead / empty  → dark background
 *   1 = alive / active → bright accent
 *   2 = trail / history → mid tone
 *   3 = special (ant, predator, fire) → warning color
 *   4+ = custom, cycling through palette
 */

import { useMemo } from 'react';

interface CellularAutomataState {
  grid: number[][];
  width: number;
  height: number;
  generation: number;
  alive_count: number;
  description: string;
}

interface Props {
  state: Record<string, unknown>;
  width?: number;
  height?: number;
}

// Color palette indexed by cell value
const CELL_COLORS = [
  'transparent',       // 0 — dead / empty
  '#6366f1',           // 1 — alive / active (indigo)
  '#818cf8',           // 2 — trail (lighter indigo)
  '#f59e0b',           // 3 — special: ant, fire, predator (amber)
  '#10b981',           // 4 — secondary alive (emerald)
  '#ec4899',           // 5 — tertiary (pink)
  '#3b82f6',           // 6 — quaternary (blue)
  '#a78bfa',           // 7 — quinary (purple)
];

function cellColor(value: number): string {
  if (value <= 0) return CELL_COLORS[0];
  return CELL_COLORS[value % CELL_COLORS.length] ?? CELL_COLORS[1];
}

export function ParticleFieldRenderer({ state }: Props) {
  const s = state as unknown as CellularAutomataState;
  const grid = s.grid ?? [];
  const rows = grid.length;
  const cols = grid[0]?.length ?? 0;

  // Choose cell size so the grid fits in a ~400px container
  const maxDim = Math.max(rows, cols, 1);
  const cellPx = Math.max(2, Math.min(12, Math.floor(400 / maxDim)));
  const canvasW = cols * cellPx;
  const canvasH = rows * cellPx;

  // Build SVG rects only for non-zero cells (sparse rendering)
  const rects = useMemo(() => {
    const out: JSX.Element[] = [];
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const val = grid[r]?.[c] ?? 0;
        if (val === 0) continue;
        out.push(
          <rect
            key={`${r}-${c}`}
            x={c * cellPx}
            y={r * cellPx}
            width={cellPx}
            height={cellPx}
            fill={cellColor(val)}
            rx={cellPx > 4 ? 1 : 0}
          />,
        );
      }
    }
    return out;
  }, [grid, rows, cols, cellPx]);

  if (rows === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-neutral-500 text-sm">
        No grid data
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2 items-center w-full">
      {/* Stats bar */}
      <div className="flex gap-4 text-xs font-mono text-neutral-500">
        <span>gen <span className="text-neutral-300">{s.generation}</span></span>
        <span>alive <span className="text-indigo-400">{s.alive_count}</span></span>
        <span className="text-neutral-600">{rows}×{cols}</span>
      </div>

      {/* Grid */}
      <div
        className="overflow-auto rounded-lg border border-white/5 bg-neutral-950"
        style={{ maxWidth: '100%', maxHeight: 420 }}
      >
        <svg
          width={canvasW}
          height={canvasH}
          viewBox={`0 0 ${canvasW} ${canvasH}`}
          style={{ display: 'block' }}
        >
          {/* Background */}
          <rect width={canvasW} height={canvasH} fill="#0a0a0f" />
          {/* Grid lines — only when cells are large enough */}
          {cellPx >= 6 && (
            <g stroke="#1f2937" strokeWidth="0.5" opacity="0.4">
              {Array.from({ length: cols + 1 }).map((_, i) => (
                <line key={`v${i}`} x1={i * cellPx} y1={0} x2={i * cellPx} y2={canvasH} />
              ))}
              {Array.from({ length: rows + 1 }).map((_, i) => (
                <line key={`h${i}`} x1={0} y1={i * cellPx} x2={canvasW} y2={i * cellPx} />
              ))}
            </g>
          )}
          {/* Cells */}
          {rects}
        </svg>
      </div>

      {/* Description */}
      {s.description && (
        <p className="text-xs text-neutral-500 font-mono text-center truncate max-w-full">
          {s.description}
        </p>
      )}
    </div>
  );
}
