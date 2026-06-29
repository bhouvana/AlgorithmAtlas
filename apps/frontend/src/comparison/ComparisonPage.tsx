/**
 * ComparisonPage — side-by-side algorithm visualization.
 *
 * Route: /compare?a=<slug>&b=<slug>
 *
 * Normal mode: each panel controls its own simulation independently.
 * Lock mode: a shared control bar drives both simulations in sync.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Lock, Unlock, RotateCcw } from 'lucide-react';
import { api, type AlgorithmSummary } from '../core/api/client';
import { WebSocketController } from '../simulation/controllers/WebSocketController';
import type { SimulationFrame, SimulationStatus } from '../simulation/controllers/SimulationController';
import { getRenderer, type VisualizationType } from '../visualization/RendererRegistry';
import { cn } from '../lib/utils';

// ── Local simulation hook (no global store) ───────────────────────────────────

interface LocalSim {
  controller: WebSocketController | null;
  frame: SimulationFrame | null;
  status: SimulationStatus;
  totalFrames: number | null;
  currentFrameIndex: number;
  playbackSpeed: number;
  setFrame: (f: SimulationFrame) => void;
  setStatus: (s: SimulationStatus) => void;
  setTotalFrames: (n: number | null) => void;
  setPlaybackSpeed: (n: number) => void;
}

function useLocalSimulation(
  algorithmSlug: string | null,
  params: Record<string, unknown>,
  seed: number,
): LocalSim {
  const [frame, setFrame] = useState<SimulationFrame | null>(null);
  const [status, setStatus] = useState<SimulationStatus>('created');
  const [totalFrames, setTotalFrames] = useState<number | null>(null);
  const [currentFrameIndex, setCurrentFrameIndex] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);
  const controllerRef = useRef<WebSocketController | null>(null);

  const handleFrame = useCallback((f: SimulationFrame) => {
    setFrame(f);
    setCurrentFrameIndex(f.frame_index);
  }, []);

  useEffect(() => {
    if (!algorithmSlug) return;

    let cancelled = false;
    controllerRef.current?.destroy();
    controllerRef.current = null;
    setFrame(null);
    setStatus('created');
    setTotalFrames(null);
    setCurrentFrameIndex(0);

    api.simulations
      .create({ algorithm_slug: algorithmSlug, params, seed })
      .then((session) => {
        if (cancelled) return;
        const ctrl = new WebSocketController(
          session.session_id,
          api.ws.simulationUrl(session.session_id),
        );
        controllerRef.current = ctrl;
        ctrl.onFrame = (f) => { if (!cancelled) handleFrame(f); };
        ctrl.onStatus = (s, meta) => {
          if (cancelled) return;
          setStatus(s);
          if (meta?.total_frames != null) setTotalFrames(meta.total_frames as number);
        };
        ctrl.onError = (code, msg) => {
          if (!cancelled) console.error(`[${algorithmSlug}] ${code}: ${msg}`);
        };
        return ctrl.connect();
      })
      .then((initialFrame) => {
        if (!cancelled && initialFrame) {
          handleFrame(initialFrame);
          setStatus('paused');
        }
      })
      .catch((err) => {
        if (!cancelled) {
          console.error('Comparison panel failed to start:', err);
          setStatus('error');
        }
      });

    return () => {
      cancelled = true;
      controllerRef.current?.destroy();
      controllerRef.current = null;
    };
  }, [algorithmSlug, seed, JSON.stringify(params)]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    controller: controllerRef.current,
    frame,
    status,
    totalFrames,
    currentFrameIndex,
    playbackSpeed,
    setFrame: handleFrame,
    setStatus,
    setTotalFrames,
    setPlaybackSpeed,
  };
}

// ── Compact controls ──────────────────────────────────────────────────────────

const SPEEDS = [0.5, 1, 2, 4] as const;

interface CompactControlsProps {
  sim: LocalSim;
  /** When set, every action fires on both sim and syncTarget simultaneously. */
  syncTarget?: LocalSim | null;
  hideSpeedRow?: boolean;
}

function CompactControls({ sim, syncTarget, hideSpeedRow }: CompactControlsProps) {
  const { controller, status, currentFrameIndex, totalFrames, playbackSpeed, setFrame, setStatus, setTotalFrames, setPlaybackSpeed } = sim;

  const isRunning = status === 'running';
  const isAtStart = currentFrameIndex === 0;
  const isAtEnd = totalFrames !== null && currentFrameIndex >= totalFrames - 1;
  const hasCtrl = controller !== null;

  const fire = (fn: (ctrl: WebSocketController) => void) => {
    if (controller) fn(controller);
    if (syncTarget?.controller) fn(syncTarget.controller);
  };

  const step = (dir: 'fwd' | 'bwd') => {
    if (dir === 'fwd') {
      controller?.stepForward().then(setFrame).catch(() => {});
      syncTarget?.controller?.stepForward().then(syncTarget.setFrame).catch(() => {});
    } else {
      controller?.stepBackward().then(setFrame).catch(() => {});
      syncTarget?.controller?.stepBackward().then(syncTarget.setFrame).catch(() => {});
    }
  };

  const togglePlay = () => {
    if (isRunning) {
      fire((c) => c.pause());
      setStatus('paused');
      if (syncTarget) syncTarget.setStatus('paused');
    } else {
      fire((c) => c.play(playbackSpeed));
      setStatus('running');
      if (syncTarget) syncTarget.setStatus('running');
    }
  };

  const handleReset = () => {
    controller?.reset().then((f) => { setFrame(f); setStatus('paused'); setTotalFrames(null); });
    syncTarget?.controller?.reset().then((f) => {
      syncTarget.setFrame(f);
      syncTarget.setStatus('paused');
      syncTarget.setTotalFrames(null);
    });
  };

  const handleSeek = (v: string) => {
    const idx = parseInt(v, 10);
    if (isNaN(idx)) return;
    controller?.seek(idx).then(setFrame).catch(() => {});
    syncTarget?.controller?.seek(idx).then(syncTarget.setFrame).catch(() => {});
  };

  const handleSpeed = (s: number) => {
    setPlaybackSpeed(s);
    if (syncTarget) syncTarget.setPlaybackSpeed(s);
    fire((c) => c.setSpeed(s));
  };

  return (
    <div className="flex flex-col gap-3 px-1">
      {/* Buttons row */}
      <div className="flex items-center justify-center gap-2">
        <button
          onClick={handleReset}
          disabled={!hasCtrl || isAtStart}
          title="Reset"
          className="w-8 h-8 rounded-lg bg-[#18181B] border border-white/8 text-zinc-400 hover:text-white hover:border-white/20 disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-xs flex items-center justify-center"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={() => step('bwd')}
          disabled={!hasCtrl || isAtStart}
          title="Step ←"
          className="px-4 py-2 rounded-xl bg-[#18181B] border border-white/8 text-zinc-400 hover:text-white text-sm disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          ← Step
        </button>
        <button
          onClick={togglePlay}
          disabled={!hasCtrl || status === 'completed'}
          className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 text-white text-sm font-medium transition-colors"
        >
          {isRunning ? 'Pause' : 'Play'}
        </button>
        <button
          onClick={() => step('fwd')}
          disabled={!hasCtrl || isAtEnd}
          title="Step →"
          className="px-4 py-2 rounded-xl bg-[#18181B] border border-white/8 text-zinc-400 hover:text-white text-sm disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          Step →
        </button>
      </div>

      {/* Scrubber */}
      {totalFrames !== null && totalFrames > 1 && (
        <div className="flex items-center gap-3 px-2">
          <span className="text-xs font-mono text-zinc-600 w-6 text-right">{currentFrameIndex}</span>
          <input
            type="range" min={0} max={totalFrames - 1} value={currentFrameIndex}
            onChange={(e) => handleSeek(e.target.value)}
            className="flex-1 h-1 accent-indigo-500"
          />
          <span className="text-xs font-mono text-zinc-600 w-6">{totalFrames - 1}</span>
        </div>
      )}

      {/* Speed */}
      {!hideSpeedRow && (
        <div className="flex items-center justify-center gap-1.5">
          <span className="text-xs text-zinc-600 mr-1">Speed</span>
          {SPEEDS.map((s) => (
            <button
              key={s}
              onClick={() => handleSpeed(s)}
              className={cn(
                'px-2 py-0.5 rounded-lg text-xs font-mono transition-colors',
                playbackSpeed === s
                  ? 'bg-indigo-600 text-white'
                  : 'bg-[#18181B] border border-white/8 text-zinc-500 hover:text-white hover:border-white/20',
              )}
            >
              ×{s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Single algorithm panel ─────────────────────────────────────────────────────

function AlgorithmPanel({
  slug,
  algorithmName,
  visualizationType,
  sim,
}: {
  slug: string;
  algorithmName?: string;
  visualizationType: VisualizationType;
  sim: LocalSim;
}) {
  const Renderer = getRenderer(visualizationType);

  return (
    <div className="rounded-2xl bg-[#111113] border border-white/8 overflow-hidden">
      {/* Panel header */}
      <div className="px-5 py-3 border-b border-white/8 flex items-center justify-between">
        <span className="text-sm font-medium text-white">
          {algorithmName ?? slug}
        </span>
        <div className="flex items-center gap-2">
          {sim.frame?.event_label && (
            <span className="text-xs font-mono text-zinc-500 truncate max-w-[160px]">
              {sim.frame.event_label}
            </span>
          )}
          <span className="text-xs font-mono text-zinc-700">
            {sim.currentFrameIndex}
            {sim.totalFrames !== null && ` / ${sim.totalFrames - 1}`}
          </span>
        </div>
      </div>

      {/* Visualization */}
      <div className="p-4 min-h-[300px] flex items-center justify-center">
        {sim.frame ? (
          <Renderer state={sim.frame.state} />
        ) : (
          <div className="flex flex-col items-center gap-3 text-zinc-600">
            <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-xs">Loading…</span>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Complexity comparison table ───────────────────────────────────────────────

function ComplexityTable({ algoA, algoB }: { algoA: AlgorithmSummary; algoB: AlgorithmSummary }) {
  const rows = [
    ['Time (best)',  algoA.complexity.time_best,    algoB.complexity.time_best],
    ['Time (avg)',   algoA.complexity.time_average,  algoB.complexity.time_average],
    ['Time (worst)', algoA.complexity.time_worst,   algoB.complexity.time_worst],
    ['Space',        algoA.complexity.space,         algoB.complexity.space],
  ] as const;

  return (
    <div className="max-w-7xl mx-auto px-6 pb-8">
      <div className="rounded-2xl bg-[#111113] border border-white/8 overflow-hidden">
        <div className="px-5 py-3 border-b border-white/8">
          <span className="text-sm font-medium text-white">Complexity Comparison</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/8">
                <th className="text-left px-5 py-3 text-zinc-500 font-medium text-xs uppercase tracking-wider">Metric</th>
                <th className="text-center px-5 py-3 text-indigo-300 font-medium text-xs uppercase tracking-wider">{algoA.name}</th>
                <th className="text-center px-5 py-3 text-indigo-300 font-medium text-xs uppercase tracking-wider">{algoB.name}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(([label, a, b]) => (
                <tr key={label} className="border-b border-white/5 last:border-0">
                  <td className="px-5 py-3 text-zinc-500 text-sm">{label}</td>
                  <td className="px-5 py-3 text-center font-mono text-sky-300 text-sm">{a}</td>
                  <td className="px-5 py-3 text-center font-mono text-sky-300 text-sm">{b}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

const DEFAULT_A = 'bubble-sort';
const DEFAULT_B = 'quick-sort';

export function ComparisonPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [algorithms, setAlgorithms] = useState<AlgorithmSummary[]>([]);
  const [locked, setLocked] = useState(false);

  const slugA = searchParams.get('a') ?? DEFAULT_A;
  const slugB = searchParams.get('b') ?? DEFAULT_B;

  useEffect(() => {
    api.algorithms.list().then(setAlgorithms).catch(console.error);
  }, []);

  function setSlug(side: 'a' | 'b', slug: string) {
    const next = new URLSearchParams(searchParams);
    next.set(side, slug);
    setSearchParams(next, { replace: true });
  }

  const algoA = algorithms.find((a) => a.slug === slugA);
  const algoB = algorithms.find((a) => a.slug === slugB);

  // Lift both sims to page level so lock mode can drive them together
  const simA = useLocalSimulation(slugA, {}, 42);
  const simB = useLocalSimulation(slugB, {}, 42);

  return (
    <div className="min-h-screen">
      {/* Page header */}
      <div className="max-w-7xl mx-auto px-6 pt-6 pb-6 flex flex-col items-center text-center gap-2">
        <Link
          to="/algorithms"
          className="text-xs text-zinc-600 hover:text-zinc-400 transition-colors mb-1"
        >
          ← Back to Catalog
        </Link>
        <h1 className="text-3xl font-bold text-white">Compare Algorithms</h1>
        <p className="text-zinc-500 text-sm">Run two algorithms side by side and compare performance</p>
      </div>

      {/* Algorithm selectors + sync lock */}
      {algorithms.length > 0 && (
        <div className="max-w-7xl mx-auto px-6 pb-6">
          <div className="flex items-center justify-center gap-4">
            {/* Selector A */}
            <div className="relative flex-1 max-w-xs">
              <select
                value={slugA}
                onChange={(e) => setSlug('a', e.target.value)}
                className="w-full bg-[#18181B] border border-white/8 text-white text-sm rounded-xl px-4 h-10 focus:border-indigo-500/50 focus:outline-none appearance-none cursor-pointer"
              >
                {algorithms.map((a) => (
                  <option key={a.slug} value={a.slug}>{a.name}</option>
                ))}
              </select>
              <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 text-xs">▼</div>
            </div>

            {/* VS badge */}
            <span className="text-indigo-400 font-bold text-sm px-2">VS</span>

            {/* Selector B */}
            <div className="relative flex-1 max-w-xs">
              <select
                value={slugB}
                onChange={(e) => setSlug('b', e.target.value)}
                className="w-full bg-[#18181B] border border-white/8 text-white text-sm rounded-xl px-4 h-10 focus:border-indigo-500/50 focus:outline-none appearance-none cursor-pointer"
              >
                {algorithms.map((a) => (
                  <option key={a.slug} value={a.slug}>{a.name}</option>
                ))}
              </select>
              <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 text-xs">▼</div>
            </div>

            {/* Sync lock button */}
            <button
              onClick={() => setLocked((l) => !l)}
              title={locked ? 'Unlock playback' : 'Lock playback in sync'}
              className={cn(
                'flex items-center gap-2 px-4 h-10 rounded-xl border text-sm font-medium transition-colors shrink-0',
                locked
                  ? 'bg-indigo-600/20 border-indigo-500/40 text-indigo-300 hover:bg-indigo-600/30'
                  : 'bg-[#18181B] border-white/8 text-zinc-400 hover:text-white hover:border-white/20',
              )}
            >
              {locked ? <Lock className="w-3.5 h-3.5" /> : <Unlock className="w-3.5 h-3.5" />}
              {locked ? 'Locked' : 'Lock sync'}
            </button>
          </div>
        </div>
      )}

      {/* Split visualization panels */}
      <div className="grid grid-cols-2 gap-4 max-w-7xl mx-auto px-6">
        <AlgorithmPanel
          key={slugA}
          slug={slugA}
          algorithmName={algoA?.name}
          visualizationType={(algoA?.visualization_type ?? 'ARRAY_BARS') as VisualizationType}
          sim={simA}
        />
        <AlgorithmPanel
          key={slugB}
          slug={slugB}
          algorithmName={algoB?.name}
          visualizationType={(algoB?.visualization_type ?? 'ARRAY_BARS') as VisualizationType}
          sim={simB}
        />
      </div>

      {/* Single unified control bar — always controls both panels */}
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className={cn(
          'w-full max-w-xl mx-auto rounded-2xl p-4',
          locked
            ? 'bg-[#111113] border border-indigo-500/20'
            : 'bg-[#111113] border border-white/8',
        )}>
          {locked && (
            <div className="flex items-center justify-center gap-2 mb-3">
              <Lock className="w-3 h-3 text-indigo-400" />
              <span className="text-xs text-indigo-400 font-medium">Synchronized</span>
            </div>
          )}
          <CompactControls sim={simA} syncTarget={simB} />
        </div>
      </div>

      {/* Complexity comparison table */}
      {algoA && algoB && (
        <div className="mt-6">
          <ComplexityTable algoA={algoA} algoB={algoB} />
        </div>
      )}
    </div>
  );
}
