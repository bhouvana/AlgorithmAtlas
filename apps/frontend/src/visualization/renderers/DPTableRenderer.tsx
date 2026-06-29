/**
 * DPTableRenderer — visualizes DPState (2D memoization table).
 *
 * Layout:
 *   - 1-row tables render as a horizontal array (e.g. Fibonacci)
 *   - Multi-row tables render as a 2D grid (e.g. LCS)
 *
 * Cell colors:
 *   amber   — current_cell (being computed now)
 *   green   — computed cells with a non-null value
 *   neutral — not yet computed
 */

import { useMemo } from 'react';
import type { RendererProps } from '../RendererRegistry';

interface DPState {
  table: (number | null)[][];
  current_cell: [number, number] | null;
  computed_cells: [number, number][];
  description: string;
  row_labels?: string[];
  col_labels?: string[];
}

const VW = 600;
const VH_1D = 160;
const VH_2D = 400;
const PAD = 36;
const DESC_H = 28;

const C = {
  current:    { fill: '#fbbf24', stroke: '#f59e0b', text: '#1c1917' },
  computed:   { fill: '#166534', stroke: '#15803d', text: '#bbf7d0' },
  pending:    { fill: '#171717', stroke: '#3f3f46', text: '#525252' },
  highlight:  { fill: '#312e81', stroke: '#4f46e5', text: '#c7d2fe' },
  bg:         '#171717',
  gridLine:   '#262626',
  labelText:  '#525252',
};

function cellColor(row: number, col: number, state: DPState) {
  if (state.current_cell && state.current_cell[0] === row && state.current_cell[1] === col) {
    return C.current;
  }
  const isComputed = state.computed_cells.some(([r, c]) => r === row && c === col);
  if (isComputed) return C.computed;
  return C.pending;
}

function formatVal(v: number | null | undefined): string {
  if (v === null || v === undefined) return '';
  if (typeof v === 'number') {
    if (Number.isInteger(v)) return String(v);
    return v.toFixed(1);
  }
  return String(v);
}

// ── 1-D renderer (single row) ────────────────────────────────────────────────

function Render1D({ state }: { state: DPState }) {
  const row = state.table[0] ?? [];
  const n = row.length;
  const cellW = Math.min(56, (VW - PAD * 2) / Math.max(n, 1));
  const cellH = 44;
  const startX = PAD + (VW - PAD * 2 - n * cellW) / 2;
  const startY = VH_1D / 2 - cellH - DESC_H / 2;
  const colLabels = state.col_labels;

  return (
    <svg viewBox={`0 0 ${VW} ${VH_1D}`} className="w-full rounded-xl" style={{ background: C.bg }}>
      {row.map((val, j) => {
        const colors = cellColor(0, j, state);
        const x = startX + j * cellW;
        return (
          <g key={j}>
            <rect x={x} y={startY} width={cellW} height={cellH}
              fill={colors.fill} stroke={colors.stroke} strokeWidth={1} />
            <text x={x + cellW / 2} y={startY + cellH / 2}
              textAnchor="middle" dominantBaseline="central"
              fill={colors.text} fontSize={13} fontWeight="600"
              fontFamily="ui-monospace, monospace">
              {formatVal(val)}
            </text>
            <text x={x + cellW / 2} y={startY + cellH + 13}
              textAnchor="middle" fill={C.labelText} fontSize={9}
              fontFamily="ui-monospace, monospace">
              {colLabels ? colLabels[j] : j}
            </text>
          </g>
        );
      })}
      <text x={VW / 2} y={VH_1D - 8} textAnchor="middle"
        fill="#737373" fontSize={10} fontFamily="ui-monospace, monospace">
        {state.description ?? ''}
      </text>
    </svg>
  );
}

// ── 2-D renderer (multi-row grid) ────────────────────────────────────────────

function Render2D({ state }: { state: DPState }) {
  const rows = state.table.length;
  const cols = state.table[0]?.length ?? 0;
  const labelColW = 22;
  const labelRowH = 18;

  const availW = VW - PAD * 2 - labelColW;
  const availH = VH_2D - PAD * 2 - labelRowH - DESC_H;
  const cellW = Math.max(20, Math.min(48, availW / Math.max(cols, 1)));
  const cellH = Math.max(18, Math.min(36, availH / Math.max(rows, 1)));

  const gridW = cellW * cols;
  const gridH = cellH * rows;
  const gridX = PAD + labelColW + (availW - gridW) / 2;
  const gridY = PAD + labelRowH + (availH - gridH) / 2;

  const rowLabels = state.row_labels;
  const colLabels = state.col_labels;
  const fontSize = Math.max(8, Math.min(11, cellW * 0.38));

  return (
    <svg viewBox={`0 0 ${VW} ${VH_2D}`} className="w-full rounded-xl"
      style={{ background: C.bg, maxHeight: '400px' }}>
      {/* Column labels */}
      {Array.from({ length: cols }, (_, j) => (
        <text key={j}
          x={gridX + j * cellW + cellW / 2} y={gridY - 6}
          textAnchor="middle" fill={C.labelText} fontSize={9}
          fontFamily="ui-monospace, monospace">
          {colLabels ? colLabels[j] : j}
        </text>
      ))}
      {/* Row labels */}
      {Array.from({ length: rows }, (_, i) => (
        <text key={i}
          x={gridX - 6} y={gridY + i * cellH + cellH / 2}
          textAnchor="end" dominantBaseline="central"
          fill={C.labelText} fontSize={9}
          fontFamily="ui-monospace, monospace">
          {rowLabels ? rowLabels[i] : i}
        </text>
      ))}
      {/* Cells */}
      {state.table.map((row, i) =>
        row.map((val, j) => {
          const colors = cellColor(i, j, state);
          const x = gridX + j * cellW;
          const y = gridY + i * cellH;
          return (
            <g key={`${i}-${j}`}>
              <rect x={x} y={y} width={cellW} height={cellH}
                fill={colors.fill} stroke={C.gridLine} strokeWidth={0.5} />
              {/* Colored fill overlay for non-pending */}
              {colors !== C.pending && (
                <rect x={x} y={y} width={cellW} height={cellH}
                  fill={colors.fill} stroke={colors.stroke} strokeWidth={1.5} />
              )}
              <text x={x + cellW / 2} y={y + cellH / 2}
                textAnchor="middle" dominantBaseline="central"
                fill={colors.text} fontSize={fontSize} fontWeight="500"
                fontFamily="ui-monospace, monospace">
                {formatVal(val)}
              </text>
            </g>
          );
        })
      )}
      {/* Description */}
      <text x={VW / 2} y={VH_2D - 10} textAnchor="middle"
        fill="#737373" fontSize={10} fontFamily="ui-monospace, monospace">
        {state.description ?? ''}
      </text>
    </svg>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export function DPTableRenderer({ state: rawState }: RendererProps) {
  const state = rawState as unknown as DPState;
  const rows = (state.table ?? []).length;

  const legend = useMemo(() => [
    { color: C.current.fill,  label: 'Computing' },
    { color: C.computed.fill, label: 'Computed' },
    { color: C.pending.fill,  label: 'Pending' },
  ], []);

  if (rows === 0) {
    return <div className="flex items-center justify-center h-32 text-neutral-500 font-mono text-sm">No table data</div>;
  }

  return (
    <div className="flex flex-col gap-2">
      {rows === 1 ? <Render1D state={state} /> : <Render2D state={state} />}
      <div className="flex items-center gap-3 px-2 text-xs font-mono">
        {legend.map(({ color, label }) => (
          <span key={label} className="flex items-center gap-1 text-neutral-400">
            <span className="inline-block w-2.5 h-2.5 rounded-sm" style={{ background: color }} />
            {label}
          </span>
        ))}
        <span className="ml-auto text-neutral-600">
          filled <span className="text-neutral-300">{state.computed_cells?.length ?? 0}</span>
        </span>
      </div>
    </div>
  );
}
