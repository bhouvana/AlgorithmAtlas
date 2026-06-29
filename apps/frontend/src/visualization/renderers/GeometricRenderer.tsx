/**
 * GeometricRenderer — renders GridState from computational geometry algorithms
 * that use the GEOMETRIC visualization type.
 *
 * Since the existing comp-geo algorithms encode their state into a GridState
 * (using GRID cell values to represent points/hull/active), this renderer
 * provides a cleaner display by treating the grid as a 2-D coordinate plane
 * and drawing points/lines/polygons properly with SVG.
 *
 * Cell conventions (mirrors the GridState cell constants):
 *   0 — empty
 *   1 — input point (CELL_WALL reused)
 *   4 — active / candidate (CELL_OPEN)
 *   5 — interior / eliminated (CELL_CLOSED)
 *   6 — hull / path vertex (CELL_PATH)
 */

import { useMemo } from 'react';

interface GridStateData {
  grid: number[][];
  current: [number, number] | null;
  path: [number, number][];
  description: string;
}

interface Props {
  state: Record<string, unknown>;
}

const SVG_W = 380;
const SVG_H = 320;
const PAD = 24;
const INNER_W = SVG_W - 2 * PAD;
const INNER_H = SVG_H - 2 * PAD;

const CELL_COLORS: Record<number, string> = {
  1: '#6366f1',   // input point — indigo
  4: '#f59e0b',   // active — amber
  5: '#374151',   // eliminated — grey
  6: '#10b981',   // hull / path — emerald
};

export function GeometricRenderer({ state }: Props) {
  const s = state as unknown as GridStateData;
  const grid = s.grid ?? [];
  const rows = grid.length;
  const cols = grid[0]?.length ?? 0;

  // Collect all points by cell type
  const points = useMemo(() => {
    const out: { r: number; c: number; val: number }[] = [];
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const val = grid[r]?.[c] ?? 0;
        if (val !== 0) out.push({ r, c, val });
      }
    }
    return out;
  }, [grid, rows, cols]);

  // Convert grid (row,col) → SVG (x,y), flipping row axis
  const toSvg = (r: number, c: number) => ({
    x: PAD + (c / Math.max(cols - 1, 1)) * INNER_W,
    y: PAD + (1 - r / Math.max(rows - 1, 1)) * INNER_H,
  });

  // Hull polygon from path
  const hullPath = useMemo(() => {
    const hull = s.path ?? [];
    if (hull.length < 2) return '';
    return hull
      .map((pt, i) => {
        const { x, y } = toSvg(pt[0], pt[1]);
        return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(' ') + ' Z';
  }, [s.path, rows, cols]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="flex flex-col gap-2 items-center w-full">
      <svg viewBox={`0 0 ${SVG_W} ${SVG_H}`} width="100%" style={{ maxWidth: SVG_W }}>
        {/* Axes */}
        <line x1={PAD} y1={SVG_H - PAD} x2={SVG_W - PAD} y2={SVG_H - PAD}
          stroke="#1f2937" strokeWidth="1" />
        <line x1={PAD} y1={PAD} x2={PAD} y2={SVG_H - PAD}
          stroke="#1f2937" strokeWidth="1" />

        {/* Hull polygon (filled, low opacity) */}
        {hullPath && (
          <path d={hullPath} fill="#10b981" fillOpacity="0.08" stroke="#10b981" strokeWidth="1.5" />
        )}

        {/* Points */}
        {points.map(({ r, c, val }) => {
          const { x, y } = toSvg(r, c);
          const color = CELL_COLORS[val] ?? '#6b7280';
          return (
            <g key={`${r}-${c}`}>
              <circle cx={x} cy={y} r={val === 6 ? 5 : 4}
                fill={color} stroke="#0a0a0f" strokeWidth="1" />
            </g>
          );
        })}

        {/* Current point (large ring) */}
        {s.current && (() => {
          const { x, y } = toSvg(s.current[0], s.current[1]);
          return (
            <circle cx={x} cy={y} r={9}
              fill="none" stroke="#f59e0b" strokeWidth="1.5" opacity="0.8" />
          );
        })()}
      </svg>

      {/* Legend */}
      <div className="flex gap-3 text-xs font-mono text-neutral-500">
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-indigo-500 inline-block" /> point</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-500 inline-block" /> active</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" /> hull</span>
      </div>

      {s.description && (
        <p className="text-xs text-neutral-500 font-mono text-center truncate max-w-full">
          {s.description}
        </p>
      )}
    </div>
  );
}
