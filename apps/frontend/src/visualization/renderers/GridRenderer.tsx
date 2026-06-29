/**
 * GridRenderer — SVG visualization for grid-based pathfinding (A*, BFS on grid, etc.)
 *
 * Cell colors:
 *   neutral  — empty / unvisited
 *   stone    — wall
 *   amber    — start
 *   emerald  — goal
 *   indigo   — open list (frontier)
 *   gray     — closed list (visited)
 *   green    — final path
 *   teal     — current cell being expanded
 */

import { useMemo } from 'react';
import type { RendererProps } from '../RendererRegistry';

interface GridState {
  grid: number[][];
  current: [number, number] | null;
  path: [number, number][];
  description: string;
}

// Cell type constants (must match Python SDK)
const CELL_EMPTY  = 0;
const CELL_WALL   = 1;
const CELL_START  = 2;
const CELL_GOAL   = 3;
const CELL_OPEN   = 4;
const CELL_CLOSED = 5;
const CELL_PATH   = 6;

const CELL_COLORS: Record<number, { fill: string; stroke: string }> = {
  [CELL_EMPTY]:  { fill: '#262626', stroke: '#3f3f46' },
  [CELL_WALL]:   { fill: '#18181b', stroke: '#3f3f46' },
  [CELL_START]:  { fill: '#f59e0b', stroke: '#d97706' },
  [CELL_GOAL]:   { fill: '#22c55e', stroke: '#16a34a' },
  [CELL_OPEN]:   { fill: '#4f46e5', stroke: '#4338ca' },
  [CELL_CLOSED]: { fill: '#52525b', stroke: '#3f3f46' },
  [CELL_PATH]:   { fill: '#0ea5e9', stroke: '#0284c7' },
};

const C_CURRENT = { fill: '#fbbf24', stroke: '#f59e0b' };
const C_BG = '#171717';

const VW = 600;
const VH = 460;
const PAD = 30;

export function GridRenderer({ state: rawState }: RendererProps) {
  const state = rawState as unknown as GridState;
  const grid = state.grid ?? [];
  const rows = grid.length;
  const cols = rows > 0 ? grid[0].length : 0;

  const { cellW, cellH } = useMemo(() => {
    if (rows === 0 || cols === 0) return { cellW: 20, cellH: 20 };
    const innerW = VW - PAD * 2;
    const innerH = VH - PAD * 2 - 32; // -32 for description bar
    return {
      cellW: innerW / cols,
      cellH: innerH / rows,
    };
  }, [rows, cols]);

  const currentSet = useMemo(() => {
    if (!state.current) return new Set<string>();
    return new Set([`${state.current[0]},${state.current[1]}`]);
  }, [state.current]);

  const pathSet = useMemo(() => {
    const s = new Set<string>();
    for (const [r, c] of (state.path ?? [])) s.add(`${r},${c}`);
    return s;
  }, [state.path]);

  const openCount   = grid.flat().filter(c => c === CELL_OPEN).length;
  const closedCount = grid.flat().filter(c => c === CELL_CLOSED).length;
  const pathLen     = (state.path ?? []).length;

  return (
    <div className="flex flex-col gap-2">
      <svg
        viewBox={`0 0 ${VW} ${VH}`}
        className="w-full rounded-xl"
        style={{ background: C_BG, maxHeight: '460px' }}
        aria-label="Grid pathfinding visualization"
      >
        {grid.map((row, r) =>
          row.map((cellType, c) => {
            const key = `${r},${c}`;
            const isCurrent = currentSet.has(key);
            const isPath = pathSet.has(key);
            const colors = isCurrent
              ? C_CURRENT
              : isPath && cellType === CELL_EMPTY
              ? CELL_COLORS[CELL_PATH]
              : (CELL_COLORS[cellType] ?? CELL_COLORS[CELL_EMPTY]);
            const x = PAD + c * cellW;
            const y = PAD + r * cellH;
            return (
              <rect
                key={key}
                x={x + 0.5}
                y={y + 0.5}
                width={cellW - 1}
                height={cellH - 1}
                fill={colors.fill}
                stroke={colors.stroke}
                strokeWidth={0.5}
                rx={1}
              />
            );
          })
        )}

        {/* Description bar */}
        <text
          x={VW / 2}
          y={VH - 10}
          textAnchor="middle"
          fill="#737373"
          fontSize={10}
          fontFamily="ui-monospace, monospace"
        >
          {state.description ?? ''}
        </text>
      </svg>

      {/* Legend + stats */}
      <div className="flex items-center justify-between px-2">
        <div className="flex items-center gap-3 text-xs font-mono">
          <LegendBox color={CELL_COLORS[CELL_START].fill}  label="Start" />
          <LegendBox color={CELL_COLORS[CELL_GOAL].fill}   label="Goal" />
          <LegendBox color={CELL_COLORS[CELL_OPEN].fill}   label="Open" />
          <LegendBox color={CELL_COLORS[CELL_CLOSED].fill} label="Closed" />
          <LegendBox color={CELL_COLORS[CELL_PATH].fill}   label="Path" />
          <LegendBox color={CELL_COLORS[CELL_WALL].fill}   label="Wall" />
        </div>
        <div className="flex gap-3 text-xs font-mono text-neutral-500">
          <span>open <span className="text-neutral-300">{openCount}</span></span>
          <span>closed <span className="text-neutral-300">{closedCount}</span></span>
          {pathLen > 0 && <span>path <span className="text-neutral-300">{pathLen - 1}</span></span>}
        </div>
      </div>
    </div>
  );
}

function LegendBox({ color, label }: { color: string; label: string }) {
  return (
    <span className="flex items-center gap-1 text-neutral-400">
      <span className="inline-block w-3 h-3 rounded-sm" style={{ background: color }} />
      {label}
    </span>
  );
}
