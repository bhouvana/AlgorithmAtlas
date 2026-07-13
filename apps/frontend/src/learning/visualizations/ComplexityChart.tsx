import { useState, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';

interface ComplexityFn {
  id: string;
  label: string;
  color: string;
  bgColor: string;
  fn: (n: number) => number;
  enabled: boolean;
}

const MAX_N = 50;
const MAX_Y = 2500;
const W = 560;
const H = 320;
const PAD = { top: 16, right: 16, bottom: 40, left: 52 };

function scaleX(n: number) {
  return PAD.left + ((n / MAX_N) * (W - PAD.left - PAD.right));
}
function scaleY(y: number) {
  const clamped = Math.min(y, MAX_Y);
  return H - PAD.bottom - ((clamped / MAX_Y) * (H - PAD.top - PAD.bottom));
}

function buildPath(fn: (n: number) => number, steps = 200): string {
  const pts: string[] = [];
  for (let i = 0; i <= steps; i++) {
    const n = (i / steps) * MAX_N;
    const y = fn(n);
    if (y > MAX_Y * 1.1) break;
    const px = scaleX(n);
    const py = scaleY(y);
    pts.push(`${i === 0 ? 'M' : 'L'}${px.toFixed(1)},${py.toFixed(1)}`);
  }
  return pts.join(' ');
}

const COMPLEXITIES: ComplexityFn[] = [
  { id: 'o1',      label: 'O(1)',       color: '#22c55e', bgColor: 'bg-green-500',   fn: ()  => 1,                           enabled: true  },
  { id: 'ologn',   label: 'O(log n)',   color: '#06b6d4', bgColor: 'bg-cyan-500',    fn: (n) => n > 0 ? Math.log2(n) * 8 : 0, enabled: true  },
  { id: 'on',      label: 'O(n)',       color: '#a78bfa', bgColor: 'bg-violet-400',  fn: (n) => n * 15,                      enabled: true  },
  { id: 'onlogn',  label: 'O(n log n)', color: '#f59e0b', bgColor: 'bg-amber-500',   fn: (n) => n > 0 ? n * Math.log2(n) * 5 : 0, enabled: true },
  { id: 'on2',     label: 'O(n²)',      color: '#f97316', bgColor: 'bg-orange-500',  fn: (n) => n * n,                       enabled: true  },
  { id: 'o2n',     label: 'O(2ⁿ)',      color: '#ef4444', bgColor: 'bg-red-500',     fn: (n) => Math.pow(2, n / 3.5),        enabled: false },
];

export function ComplexityChart() {
  const [fns, setFns] = useState<ComplexityFn[]>(COMPLEXITIES);
  const [hoverN, setHoverN] = useState<number | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const toggle = useCallback((id: string) => {
    setFns((prev) => prev.map((f) => f.id === id ? { ...f, enabled: !f.enabled } : f));
  }, []);

  const handleMouseMove = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    const rect = svgRef.current?.getBoundingClientRect();
    if (!rect) return;
    const px = e.clientX - rect.left;
    const n = Math.round(((px - PAD.left) / (W - PAD.left - PAD.right)) * MAX_N);
    setHoverN(Math.max(0, Math.min(MAX_N, n)));
  }, []);

  const xTicks = [0, 10, 20, 30, 40, 50];
  const yTicks = [0, 500, 1000, 1500, 2000, 2500];

  return (
    <div className="space-y-4">
      {/* Toggle buttons */}
      <div className="flex flex-wrap gap-2">
        {fns.map((f) => (
          <button
            key={f.id}
            onClick={() => toggle(f.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all duration-200 border ${
              f.enabled
                ? 'border-white/20 text-white bg-white/5'
                : 'border-white/5 text-zinc-500 bg-transparent'
            }`}
          >
            <span
              className="w-2.5 h-2.5 rounded-full flex-shrink-0 transition-opacity"
              style={{ backgroundColor: f.color, opacity: f.enabled ? 1 : 0.3 }}
            />
            {f.label}
          </button>
        ))}
      </div>

      {/* Chart */}
      <div className="relative rounded-xl overflow-hidden bg-zinc-950/60 border border-charcoal/10">
        <svg
          ref={svgRef}
          viewBox={`0 0 ${W} ${H}`}
          className="w-full"
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setHoverN(null)}
        >
          {/* Grid lines */}
          {yTicks.map((y) => (
            <g key={y}>
              <line
                x1={PAD.left} y1={scaleY(y)}
                x2={W - PAD.right} y2={scaleY(y)}
                stroke="white" strokeOpacity={0.05} strokeWidth={1}
              />
              <text
                x={PAD.left - 6} y={scaleY(y) + 4}
                textAnchor="end" fill="#71717a" fontSize={9} fontFamily="monospace"
              >
                {y === 0 ? '0' : y >= 1000 ? `${y / 1000}k` : y}
              </text>
            </g>
          ))}
          {xTicks.map((n) => (
            <g key={n}>
              <line
                x1={scaleX(n)} y1={PAD.top}
                x2={scaleX(n)} y2={H - PAD.bottom}
                stroke="white" strokeOpacity={0.05} strokeWidth={1}
              />
              <text
                x={scaleX(n)} y={H - PAD.bottom + 14}
                textAnchor="middle" fill="#71717a" fontSize={9} fontFamily="monospace"
              >
                {n}
              </text>
            </g>
          ))}

          {/* Axis labels */}
          <text x={(W + PAD.left) / 2} y={H - 4} textAnchor="middle" fill="#52525b" fontSize={10}>
            n (input size)
          </text>
          <text
            x={14} y={(H + PAD.top) / 2}
            textAnchor="middle" fill="#52525b" fontSize={10}
            transform={`rotate(-90, 14, ${(H + PAD.top) / 2})`}
          >
            operations
          </text>

          {/* Complexity curves */}
          {fns.filter((f) => f.enabled).map((f) => (
            <motion.path
              key={f.id}
              d={buildPath(f.fn)}
              fill="none"
              stroke={f.color}
              strokeWidth={2}
              strokeLinecap="round"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
            />
          ))}

          {/* Hover line + dots */}
          {hoverN !== null && (
            <>
              <line
                x1={scaleX(hoverN)} y1={PAD.top}
                x2={scaleX(hoverN)} y2={H - PAD.bottom}
                stroke="white" strokeOpacity={0.2} strokeWidth={1} strokeDasharray="4 3"
              />
              {fns.filter((f) => f.enabled).map((f) => {
                const val = f.fn(hoverN);
                if (val > MAX_Y) return null;
                return (
                  <circle
                    key={f.id}
                    cx={scaleX(hoverN)} cy={scaleY(val)}
                    r={4} fill={f.color} stroke="#09090B" strokeWidth={2}
                  />
                );
              })}
            </>
          )}
        </svg>

        {/* Hover tooltip */}
        {hoverN !== null && (
          <div className="absolute top-2 right-2 bg-zinc-900/95 border border-charcoal/10 rounded-lg px-3 py-2 text-xs font-mono space-y-0.5 backdrop-blur">
            <div className="text-zinc-400 mb-1">n = {hoverN}</div>
            {fns.filter((f) => f.enabled).map((f) => {
              const val = f.fn(hoverN);
              return (
                <div key={f.id} className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: f.color }} />
                  <span className="text-zinc-300 w-20">{f.label}</span>
                  <span className="text-white tabular-nums">
                    {val > MAX_Y ? '∞' : val < 10 ? val.toFixed(1) : Math.round(val).toLocaleString()}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <p className="text-xs text-zinc-500 text-center">
        Hover over the chart to compare exact values at any input size
      </p>
    </div>
  );
}
