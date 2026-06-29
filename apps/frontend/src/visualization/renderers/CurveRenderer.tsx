/**
 * CurveRenderer — renders CurveState (CURVE).
 *
 * Shows an optimization landscape (1-D function) with:
 *   - Background curve (the objective function)
 *   - Trajectory of visited points (history_x, history_y)
 *   - Current position marker
 *   - Best position marker
 *   - Gradient arrow at current position
 */

import { useMemo } from 'react';

interface CurveStateData {
  landscape_x: number[];
  landscape_y: number[];
  current_x: number;
  current_y: number;
  history_x: number[];
  history_y: number[];
  iteration: number;
  best_x: number;
  best_y: number;
  gradient: number | null;
  extra: string;
  description: string;
}

interface Props {
  state: Record<string, unknown>;
}

const PAD = { top: 20, right: 20, bottom: 40, left: 50 };
const W = 480;
const H = 260;
const INNER_W = W - PAD.left - PAD.right;
const INNER_H = H - PAD.top - PAD.bottom;

function linspace(a: number, b: number, n: number): number[] {
  return Array.from({ length: n }, (_, i) => a + (i / (n - 1)) * (b - a));
}

export function CurveRenderer({ state }: Props) {
  const s = state as unknown as CurveStateData;
  const lx = s.landscape_x ?? [];
  const ly = s.landscape_y ?? [];
  const hx = s.history_x ?? [];
  const hy = s.history_y ?? [];

  const { xMin, xMax, yMin, yMax } = useMemo(() => {
    const allX = [...lx, ...hx, s.current_x, s.best_x].filter(isFinite);
    const allY = [...ly, ...hy, s.current_y, s.best_y].filter(isFinite);
    const xMin = allX.length ? Math.min(...allX) : -5;
    const xMax = allX.length ? Math.max(...allX) : 5;
    const yMin = allY.length ? Math.min(...allY) : 0;
    const yMax = allY.length ? Math.max(...allY) : 10;
    const yPad = (yMax - yMin) * 0.1 || 1;
    return { xMin, xMax, yMin: yMin - yPad, yMax: yMax + yPad };
  }, [lx, ly, hx, hy, s.current_x, s.current_y, s.best_x, s.best_y]);

  const toSvgX = (x: number) =>
    PAD.left + ((x - xMin) / (xMax - xMin || 1)) * INNER_W;
  const toSvgY = (y: number) =>
    PAD.top + (1 - (y - yMin) / (yMax - yMin || 1)) * INNER_H;

  // Landscape path
  const landscapePath = useMemo(() => {
    if (lx.length < 2) return '';
    return lx
      .map((x, i) => `${i === 0 ? 'M' : 'L'}${toSvgX(x).toFixed(1)},${toSvgY(ly[i] ?? 0).toFixed(1)}`)
      .join(' ');
  }, [lx, ly, xMin, xMax, yMin, yMax]); // eslint-disable-line react-hooks/exhaustive-deps

  // History path
  const historyPath = useMemo(() => {
    if (hx.length < 2) return '';
    return hx
      .map((x, i) => `${i === 0 ? 'M' : 'L'}${toSvgX(x).toFixed(1)},${toSvgY(hy[i] ?? 0).toFixed(1)}`)
      .join(' ');
  }, [hx, hy, xMin, xMax, yMin, yMax]); // eslint-disable-line react-hooks/exhaustive-deps

  const cx = toSvgX(s.current_x ?? 0);
  const cy = toSvgY(s.current_y ?? 0);
  const bx = toSvgX(s.best_x ?? 0);
  const by = toSvgY(s.best_y ?? 0);

  // Y-axis ticks
  const yTicks = useMemo(() => {
    const n = 5;
    return linspace(yMin, yMax, n).map((v) => ({
      v,
      y: toSvgY(v),
      label: v.toFixed(1),
    }));
  }, [yMin, yMax]); // eslint-disable-line react-hooks/exhaustive-deps

  const xTicks = useMemo(() => {
    const n = 5;
    return linspace(xMin, xMax, n).map((v) => ({
      v,
      x: toSvgX(v),
      label: v.toFixed(1),
    }));
  }, [xMin, xMax]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="flex flex-col gap-2 items-center w-full">
      {/* Stats */}
      <div className="flex gap-4 text-xs font-mono text-neutral-500">
        <span>iter <span className="text-neutral-300">{s.iteration ?? 0}</span></span>
        <span>f(x) <span className="text-indigo-400">{(s.current_y ?? 0).toFixed(4)}</span></span>
        <span>best <span className="text-emerald-400">{(s.best_y ?? 0).toFixed(4)}</span></span>
        {s.gradient != null && (
          <span>∇ <span className="text-amber-400">{s.gradient.toFixed(4)}</span></span>
        )}
      </div>

      <svg
        viewBox={`0 0 ${W} ${H}`}
        width="100%"
        style={{ maxWidth: W, fontFamily: 'monospace' }}
      >
        {/* Y-axis ticks */}
        {yTicks.map(({ v, y, label }) => (
          <g key={v}>
            <line x1={PAD.left - 4} y1={y} x2={PAD.left} y2={y} stroke="#374151" strokeWidth="1" />
            <text x={PAD.left - 7} y={y + 3.5} textAnchor="end" fontSize="9" fill="#6b7280">
              {label}
            </text>
          </g>
        ))}

        {/* X-axis ticks */}
        {xTicks.map(({ v, x, label }) => (
          <g key={v}>
            <line x1={x} y1={H - PAD.bottom} x2={x} y2={H - PAD.bottom + 4} stroke="#374151" strokeWidth="1" />
            <text x={x} y={H - PAD.bottom + 14} textAnchor="middle" fontSize="9" fill="#6b7280">
              {label}
            </text>
          </g>
        ))}

        {/* Grid lines */}
        <g stroke="#1f2937" strokeWidth="0.5" strokeDasharray="3 3">
          {yTicks.map(({ v, y }) => (
            <line key={v} x1={PAD.left} y1={y} x2={W - PAD.right} y2={y} />
          ))}
          {xTicks.map(({ v, x }) => (
            <line key={v} x1={x} y1={PAD.top} x2={x} y2={H - PAD.bottom} />
          ))}
        </g>

        {/* Axes */}
        <line x1={PAD.left} y1={PAD.top} x2={PAD.left} y2={H - PAD.bottom} stroke="#374151" strokeWidth="1" />
        <line x1={PAD.left} y1={H - PAD.bottom} x2={W - PAD.right} y2={H - PAD.bottom} stroke="#374151" strokeWidth="1" />

        {/* Axis labels */}
        <text x={W / 2} y={H - 4} textAnchor="middle" fontSize="10" fill="#6b7280">x</text>
        <text x={12} y={H / 2} textAnchor="middle" fontSize="10" fill="#6b7280" transform={`rotate(-90,12,${H / 2})`}>f(x)</text>

        {/* Landscape curve */}
        {landscapePath && (
          <path d={landscapePath} fill="none" stroke="#4b5563" strokeWidth="1.5" />
        )}

        {/* History trajectory */}
        {historyPath && (
          <path d={historyPath} fill="none" stroke="#6366f1" strokeWidth="1" strokeDasharray="3 2" opacity="0.6" />
        )}

        {/* History dots */}
        {hx.map((x, i) => (
          <circle
            key={i}
            cx={toSvgX(x)}
            cy={toSvgY(hy[i] ?? 0)}
            r={2}
            fill="#6366f1"
            opacity={0.3 + (i / Math.max(hx.length - 1, 1)) * 0.5}
          />
        ))}

        {/* Best position marker */}
        <circle cx={bx} cy={by} r={6} fill="none" stroke="#10b981" strokeWidth="1.5" />
        <circle cx={bx} cy={by} r={2} fill="#10b981" />
        <text x={bx + 8} y={by - 4} fontSize="9" fill="#10b981">best</text>

        {/* Gradient arrow at current position */}
        {s.gradient != null && isFinite(cx) && isFinite(cy) && (
          <g>
            <defs>
              <marker id="grad-arrow" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
                <path d="M0,0 L0,6 L6,3 z" fill="#f59e0b" />
              </marker>
            </defs>
            <line
              x1={cx}
              y1={cy}
              x2={Math.min(W - PAD.right, Math.max(PAD.left, cx - s.gradient * 15))}
              y2={cy}
              stroke="#f59e0b"
              strokeWidth="1.5"
              markerEnd="url(#grad-arrow)"
            />
          </g>
        )}

        {/* Current position */}
        <circle cx={cx} cy={cy} r={5} fill="#f59e0b" />
        <circle cx={cx} cy={cy} r={8} fill="none" stroke="#f59e0b" strokeWidth="1" opacity="0.5" />
      </svg>

      {s.description && (
        <p className="text-xs text-neutral-500 font-mono text-center truncate max-w-full">
          {s.description}
        </p>
      )}
    </div>
  );
}
