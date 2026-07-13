/**
 * BenchmarkPanel — empirical complexity visualization.
 *
 * For server-executed algorithms: calls the benchmark API and renders a line chart.
 * For WASM-executed algorithms: shows both server time AND WASM browser time.
 *
 * Phase 3.5: WASM algorithms get a side-by-side comparison chart with two lines —
 * indigo for Python/server, emerald for WASM/browser.
 */

import { useCallback, useEffect, useState } from 'react';
import { api, type BenchmarkSizeResult, type BenchmarkConfigResponse } from '../core/api/client';
import { WasmController } from '../simulation/controllers/WasmController';

// ── Chart geometry ────────────────────────────────────────────────────────────

const W = 560;
const H = 240;
const PAD = { top: 16, right: 24, bottom: 40, left: 52 };
const INNER_W = W - PAD.left - PAD.right;
const INNER_H = H - PAD.top - PAD.bottom;
const TICK_COUNT = 5;

function scaleLinear(domain: [number, number], range: [number, number]) {
  const [d0, d1] = domain;
  const [r0, r1] = range;
  const factor = (r1 - r0) / (d1 - d0 || 1);
  return (v: number) => r0 + (v - d0) * factor;
}

function niceTicks(min: number, max: number, count: number): number[] {
  if (max === min) return [min];
  const step = (max - min) / (count - 1);
  return Array.from({ length: count }, (_, i) => min + i * step);
}

function formatMs(ms: number): string {
  if (ms < 1) return `${(ms * 1000).toFixed(0)}µs`;
  if (ms < 1000) return `${ms.toFixed(ms < 10 ? 2 : 1)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

// ── SVG Chart ─────────────────────────────────────────────────────────────────

interface ChartSeries {
  data: { input_size: number; ms: number }[];
  color: string;
  gradientId: string;
  label: string;
}

interface ChartProps {
  series: ChartSeries[];
}

function BenchmarkChart({ series }: ChartProps) {
  const [tooltip, setTooltip] = useState<{ x: number; y: number; label: string } | null>(null);

  const allMs = series.flatMap((s) => s.data.map((d) => d.ms));
  const allSizes = series.flatMap((s) => s.data.map((d) => d.input_size));

  const xMin = Math.min(...allSizes);
  const xMax = Math.max(...allSizes);
  const yMin = 0;
  const yMax = Math.max(...allMs, 0.001) * 1.12;

  const scaleX = scaleLinear([xMin, xMax], [0, INNER_W]);
  const scaleY = scaleLinear([yMin, yMax], [INNER_H, 0]);

  const xTicks = niceTicks(xMin, xMax, Math.min(TICK_COUNT, allSizes.length));
  const yTicks = niceTicks(yMin, yMax, TICK_COUNT);

  return (
    <div className="relative">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full"
        style={{ maxHeight: '260px' }}
        onMouseLeave={() => setTooltip(null)}
        aria-label="Benchmark chart"
      >
        {/* Grid lines */}
        {yTicks.map((v, i) => {
          const cy = PAD.top + scaleY(v);
          return <line key={i} x1={PAD.left} y1={cy} x2={PAD.left + INNER_W} y2={cy} stroke="#262626" strokeWidth={1} />;
        })}

        {/* Y-axis labels */}
        {yTicks.map((v, i) => (
          <text key={i} x={PAD.left - 6} y={PAD.top + scaleY(v)} textAnchor="end" dominantBaseline="central" fill="#525252" fontSize={9} fontFamily="ui-monospace, monospace">
            {formatMs(v)}
          </text>
        ))}

        {/* X-axis labels */}
        {xTicks.map((v, i) => (
          <text key={i} x={PAD.left + scaleX(v)} y={PAD.top + INNER_H + 14} textAnchor="middle" fill="#525252" fontSize={9} fontFamily="ui-monospace, monospace">
            {v}
          </text>
        ))}

        {/* Axis labels */}
        <text x={PAD.left + INNER_W / 2} y={H - 4} textAnchor="middle" fill="#404040" fontSize={9} fontFamily="ui-monospace, monospace">input size</text>
        <text x={10} y={PAD.top + INNER_H / 2} textAnchor="middle" fill="#404040" fontSize={9} fontFamily="ui-monospace, monospace" transform={`rotate(-90, 10, ${PAD.top + INNER_H / 2})`}>time (ms)</text>

        {/* Gradient defs */}
        <defs>
          {series.map((s) => (
            <linearGradient key={s.gradientId} id={s.gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={s.color} />
              <stop offset="100%" stopColor={s.color} stopOpacity={0} />
            </linearGradient>
          ))}
        </defs>

        {/* Series */}
        {series.map((s) => {
          const pts = s.data.map((d) => ({
            cx: PAD.left + scaleX(d.input_size),
            cy: PAD.top + scaleY(d.ms),
            d,
          }));
          const pathD = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.cx.toFixed(1)} ${p.cy.toFixed(1)}`).join(' ');
          const areaD = pathD
            + ` L ${pts[pts.length - 1].cx.toFixed(1)} ${(PAD.top + INNER_H).toFixed(1)}`
            + ` L ${pts[0].cx.toFixed(1)} ${(PAD.top + INNER_H).toFixed(1)} Z`;

          return (
            <g key={s.label}>
              <path d={areaD} fill={`url(#${s.gradientId})`} opacity={0.2} />
              <path d={pathD} fill="none" stroke={s.color} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
              {pts.map((p, i) => (
                <g key={i}>
                  <circle cx={p.cx} cy={p.cy} r={4} fill={s.color} stroke="#1c1917" strokeWidth={1.5} />
                  <rect
                    x={p.cx - 12} y={PAD.top}
                    width={24} height={INNER_H}
                    fill="transparent"
                    onMouseEnter={() => setTooltip({
                      x: p.cx,
                      y: p.cy,
                      label: `${s.label}  n=${p.d.input_size}  ${formatMs(p.d.ms)}`,
                    })}
                  />
                </g>
              ))}
            </g>
          );
        })}

        {/* Tooltip */}
        {tooltip && (() => {
          const tx = tooltip.x + 8;
          const ty = Math.max(PAD.top + 4, tooltip.y - 30);
          return (
            <g>
              <rect x={tx - 2} y={ty - 10} width={tooltip.label.length * 6.2 + 6} height={18} rx={3} fill="#262626" stroke="#404040" strokeWidth={1} />
              <text x={tx + 1} y={ty + 2} fill="#e5e5e5" fontSize={10} fontFamily="ui-monospace, monospace">{tooltip.label}</text>
            </g>
          );
        })()}
      </svg>

      {/* Legend */}
      {series.length > 1 && (
        <div className="flex gap-4 justify-center text-xs text-neutral-400 -mt-1">
          {series.map((s) => (
            <div key={s.label} className="flex items-center gap-1.5">
              <div className="w-3 h-0.5 rounded" style={{ backgroundColor: s.color }} />
              <span>{s.label}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Panel ─────────────────────────────────────────────────────────────────────

interface BenchmarkPanelProps {
  algorithmSlug: string;
  executionTarget?: 'server' | 'wasm' | 'both';
}

interface BenchmarkState {
  server: BenchmarkSizeResult[] | null;
  wasm: { input_size: number; wasm_ms: number }[] | null;
  serverEngine?: 'python' | 'rust';
}

type State =
  | { phase: 'idle' }
  | { phase: 'loading' }
  | { phase: 'done'; data: BenchmarkState }
  | { phase: 'error'; message: string };

const WASM_SIZES = [10, 25, 50, 100, 200, 500, 1000, 2000, 5000];
const FALLBACK_SIZES = [10, 25, 50, 100, 200, 500, 1000];

export function BenchmarkPanel({ algorithmSlug, executionTarget = 'server' }: BenchmarkPanelProps) {
  const [state, setState] = useState<State>({ phase: 'idle' });
  const [benchConfig, setBenchConfig] = useState<BenchmarkConfigResponse | null>(null);
  const isWasm = executionTarget === 'wasm' || executionTarget === 'both';

  // Fetch category-appropriate config on mount
  useEffect(() => {
    api.benchmarks.config(algorithmSlug)
      .then(setBenchConfig)
      .catch(() => { /* backend offline — fallback to defaults */ });
  }, [algorithmSlug]);

  const run = useCallback(async () => {
    setState({ phase: 'loading' });
    try {
      const sizes = benchConfig?.default_sizes ?? FALLBACK_SIZES;
      const sizeParam = benchConfig?.size_param ?? 'array_size';

      // Server benchmark (Python / Rust execution time)
      const serverResult = isWasm
        ? null
        : await api.benchmarks.run({
            algorithm_slug: algorithmSlug,
            sizes,
            size_param: sizeParam,
            trials: 3,
          });

      // WASM benchmark (browser execution time)
      let wasmResult: { input_size: number; wasm_ms: number }[] | null = null;
      if (isWasm) {
        const ctrl = new WasmController(algorithmSlug, { array_size: 20, input_order: 'random' }, 42);
        wasmResult = await ctrl.benchmarkSizes(WASM_SIZES, 3);
      }

      setState({
        phase: 'done',
        data: {
          server: serverResult?.results ?? null,
          wasm: wasmResult,
          serverEngine: serverResult?.engine,
        },
      });
    } catch (e) {
      setState({ phase: 'error', message: e instanceof Error ? e.message : String(e) });
    }
  }, [algorithmSlug, isWasm, benchConfig]);

  const sizes = isWasm ? WASM_SIZES : (benchConfig?.default_sizes ?? FALLBACK_SIZES);
  const sizeLabel = benchConfig?.label ?? 'n';

  return (
    <div className="flex flex-col gap-3 p-4 bg-neutral-900 rounded-xl border border-charcoal/10">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-neutral-500 uppercase tracking-wider">
            Empirical Benchmark
          </span>
          {isWasm && (
            <span className="px-1.5 py-0.5 rounded bg-emerald-900/40 border border-emerald-700/30 text-emerald-400 text-xs font-mono">
              WASM
            </span>
          )}
          {state.phase === 'done' && state.data.serverEngine === 'rust' && (
            <span className="px-1.5 py-0.5 rounded bg-orange-900/40 border border-orange-700/30 text-orange-400 text-xs font-mono">
              Rust
            </span>
          )}
        </div>
        <button
          onClick={run}
          disabled={state.phase === 'loading'}
          className="px-3 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400"
        >
          {state.phase === 'loading' ? 'Running…' : state.phase === 'done' ? 'Re-run' : 'Run Benchmark'}
        </button>
      </div>

      {state.phase === 'idle' && (
        <p className="text-xs text-neutral-600 font-mono">
          {isWasm
            ? `Measures WASM browser execution time across n ∈ {${WASM_SIZES.join(', ')}}. Runs in-browser, no server required.`
            : `Measures actual execution time across ${sizeLabel} ∈ {${sizes.join(', ')}}. Each size is run 3 times and the median is reported.`}
        </p>
      )}

      {state.phase === 'loading' && (
        <div className="flex items-center justify-center h-32 gap-3 text-neutral-500">
          <div className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-xs font-mono">
            {isWasm ? `Benchmarking WASM across ${WASM_SIZES.length} input sizes…` : `Benchmarking ${sizes.length} input sizes…`}
          </span>
        </div>
      )}

      {state.phase === 'error' && (
        <div className="text-xs text-red-400 font-mono bg-red-900/20 rounded-lg p-3">
          {state.message}
        </div>
      )}

      {state.phase === 'done' && (() => {
        const { server, wasm } = state.data;

        const chartSeries: ChartSeries[] = [];
        if (server) {
          chartSeries.push({
            label: 'Server (Python)',
            color: '#818cf8',
            gradientId: 'benchGradServer',
            data: server.map((d) => ({ input_size: d.input_size, ms: d.total_ms })),
          });
        }
        if (wasm) {
          chartSeries.push({
            label: 'Browser (WASM)',
            color: '#34d399',
            gradientId: 'benchGradWasm',
            data: wasm.map((d) => ({ input_size: d.input_size, ms: d.wasm_ms })),
          });
        }

        return (
          <>
            {chartSeries.length > 0 && <BenchmarkChart series={chartSeries} />}

            {/* Tabular results */}
            {wasm && (
              <div className="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-9 gap-1 mt-1">
                {wasm.map((d) => (
                  <div key={d.input_size} className="flex flex-col items-center gap-0.5 text-xs font-mono">
                    <span className="text-neutral-600">n={d.input_size}</span>
                    <span className="text-emerald-400">{formatMs(d.wasm_ms)}</span>
                  </div>
                ))}
              </div>
            )}
            {server && (
              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-7 gap-1 mt-1">
                {server.map((d) => (
                  <div key={d.input_size} className="flex flex-col items-center gap-0.5 text-xs font-mono">
                    <span className="text-neutral-600">n={d.input_size}</span>
                    <span className="text-neutral-300">{formatMs(d.total_ms)}</span>
                    <span className="text-neutral-600">{d.frame_count}f</span>
                  </div>
                ))}
              </div>
            )}
          </>
        );
      })()}
    </div>
  );
}
