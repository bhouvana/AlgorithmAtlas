/**
 * ProbabilityRenderer — renders ProbabilityState (PROBABILITY_SPACE).
 *
 * Layout:
 *   Top:    Histogram with running sample distribution
 *   Bottom: Convergence line showing estimate vs true value
 *   Stats:  trial count, estimate, error
 */

import { useMemo } from 'react';

interface ProbStateData {
  samples: number[];
  histogram_bins: number[];
  histogram_counts: number[];
  trial: number;
  total_trials: number;
  estimate: number;
  true_value: number | null;
  path_x: number[];
  path_y: number[];
  description: string;
}

interface Props {
  state: Record<string, unknown>;
}

const W = 480;
const HIST_H = 160;
const CONV_H = 100;
const PAD = { top: 10, right: 16, bottom: 30, left: 44 };
const INNER_W = W - PAD.left - PAD.right;

export function ProbabilityRenderer({ state }: Props) {
  const s = state as unknown as ProbStateData;
  const bins = s.histogram_bins ?? [];
  const counts = s.histogram_counts ?? [];
  const px = s.path_x ?? [];
  const py = s.path_y ?? [];
  const maxCount = Math.max(...counts, 1);
  const error = s.true_value != null ? Math.abs(s.estimate - s.true_value) : null;
  const pct = s.total_trials > 0 ? Math.round((s.trial / s.total_trials) * 100) : 0;

  // Histogram bar layout
  const bars = useMemo(() => {
    if (bins.length < 2) return [];
    const n = bins.length - 1; // number of bars = edges - 1
    const barW = INNER_W / n;
    return Array.from({ length: n }, (_, i) => {
      const barH = ((counts[i] ?? 0) / maxCount) * (HIST_H - PAD.top - PAD.bottom);
      return {
        x: PAD.left + i * barW,
        y: PAD.top + (HIST_H - PAD.top - PAD.bottom) - barH,
        w: Math.max(1, barW - 1),
        h: barH,
        label: `${(bins[i] ?? 0).toFixed(1)}`,
      };
    });
  }, [bins, counts, maxCount]);

  // Convergence path
  const convPath = useMemo(() => {
    if (px.length < 2) return '';
    const xMin = Math.min(...px);
    const xMax = Math.max(...px);
    const yMin = Math.min(...py, s.true_value ?? 0) * 0.95;
    const yMax = Math.max(...py, s.true_value ?? 0) * 1.05 || 1;
    const toX = (v: number) => PAD.left + ((v - xMin) / (xMax - xMin || 1)) * INNER_W;
    const toY = (v: number) =>
      PAD.top + (1 - (v - yMin) / (yMax - yMin || 1)) * (CONV_H - PAD.top - PAD.bottom);
    return px
      .map((x, i) => `${i === 0 ? 'M' : 'L'}${toX(x).toFixed(1)},${toY(py[i] ?? 0).toFixed(1)}`)
      .join(' ');
  }, [px, py, s.true_value]);

  return (
    <div className="flex flex-col gap-2 items-center w-full">
      {/* Stats bar */}
      <div className="flex gap-4 text-xs font-mono text-neutral-500">
        <span>trial <span className="text-neutral-300">{s.trial}</span>/{s.total_trials}</span>
        <span>est <span className="text-indigo-400">{(s.estimate ?? 0).toFixed(5)}</span></span>
        {s.true_value != null && (
          <span>true <span className="text-emerald-400">{s.true_value.toFixed(5)}</span></span>
        )}
        {error != null && (
          <span>err <span className="text-amber-400">{error.toFixed(5)}</span></span>
        )}
      </div>

      {/* Progress bar */}
      <div className="w-full rounded-full bg-white/5 h-1 overflow-hidden">
        <div className="h-1 bg-indigo-600 transition-all" style={{ width: `${pct}%` }} />
      </div>

      <svg viewBox={`0 0 ${W} ${HIST_H + CONV_H + 8}`} width="100%" style={{ maxWidth: W }}>
        {/* ── Histogram ── */}
        <g>
          <text x={PAD.left} y={PAD.top - 2} fontSize="9" fill="#6b7280">Distribution</text>
          {/* Bars */}
          {bars.map((b, i) => (
            <rect key={i} x={b.x} y={b.y} width={b.w} height={b.h}
              fill="#6366f1" opacity="0.7" rx="1" />
          ))}
          {/* Axes */}
          <line x1={PAD.left} y1={PAD.top} x2={PAD.left} y2={HIST_H - PAD.bottom} stroke="#374151" strokeWidth="1" />
          <line x1={PAD.left} y1={HIST_H - PAD.bottom} x2={W - PAD.right} y2={HIST_H - PAD.bottom} stroke="#374151" strokeWidth="1" />
          {/* Count labels */}
          {[0, 0.5, 1].map((frac) => {
            const v = Math.round(frac * maxCount);
            const y = PAD.top + (1 - frac) * (HIST_H - PAD.top - PAD.bottom);
            return (
              <g key={frac}>
                <line x1={PAD.left - 3} y1={y} x2={PAD.left} y2={y} stroke="#374151" strokeWidth="1" />
                <text x={PAD.left - 5} y={y + 3} textAnchor="end" fontSize="8" fill="#6b7280">{v}</text>
              </g>
            );
          })}
        </g>

        {/* ── Convergence chart ── */}
        {px.length >= 2 && (
          <g transform={`translate(0, ${HIST_H + 8})`}>
            <text x={PAD.left} y={PAD.top - 2} fontSize="9" fill="#6b7280">Convergence</text>
            <line x1={PAD.left} y1={PAD.top} x2={PAD.left} y2={CONV_H - PAD.bottom} stroke="#374151" strokeWidth="1" />
            <line x1={PAD.left} y1={CONV_H - PAD.bottom} x2={W - PAD.right} y2={CONV_H - PAD.bottom} stroke="#374151" strokeWidth="1" />
            <path d={convPath} fill="none" stroke="#6366f1" strokeWidth="1.5" />
            {s.true_value != null && (
              <line
                x1={PAD.left} y1={CONV_H / 2} x2={W - PAD.right} y2={CONV_H / 2}
                stroke="#10b981" strokeWidth="1" strokeDasharray="4 2"
              />
            )}
          </g>
        )}
      </svg>

      {s.description && (
        <p className="text-xs text-neutral-500 font-mono text-center truncate max-w-full">
          {s.description}
        </p>
      )}
    </div>
  );
}
