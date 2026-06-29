/**
 * SimulationCanvas — mounts the correct renderer for the current algorithm
 * and wires the controller's event stream to the simulation store.
 *
 * This is the only component that knows about the controller lifecycle.
 * It creates the controller, connects it, and tears it down on unmount.
 *
 * Routing:
 *   execution_target === "wasm"   → WasmController (all frames computed client-side)
 *   execution_target === "server" → WebSocketController (frames streamed from backend)
 *   execution_target === "both"   → WasmController (prefer local; server used for benchmark)
 */

import { useEffect, useRef, useState } from 'react';
import { api } from '../core/api/client';
import { useSimulationStore } from '../core/store/simulationStore';
import { WebSocketController } from './controllers/WebSocketController';
import { WasmController } from './controllers/WasmController';
import { getRenderer, type VisualizationType } from '../visualization/RendererRegistry';
import type { SimulationController } from './controllers/SimulationController';

interface SimulationCanvasProps {
  algorithmSlug: string;
  visualizationType: VisualizationType;
  executionTarget?: 'server' | 'wasm' | 'both';
  params?: Record<string, unknown>;
  seed?: number;
}

export function SimulationCanvas({
  algorithmSlug,
  visualizationType,
  executionTarget = 'server',
  params = {},
  seed = 42,
}: SimulationCanvasProps) {
  const {
    currentFrame,
    setController,
    setFrame,
    setStatus,
    setTotalFrames,
    setSessionId,
    setAlgorithmSlug,
    reset,
  } = useSimulationStore();

  const controllerRef = useRef<SimulationController | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [retryKey, setRetryKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setErrorMsg(null);

    async function startSimulation() {
      controllerRef.current?.destroy();
      reset();

      try {
        let ctrl: SimulationController;

        if (executionTarget === 'wasm' || executionTarget === 'both') {
          // ── WASM path: no server session needed ─────────────────────────
          ctrl = new WasmController(algorithmSlug, params, seed);
          setSessionId(ctrl.sessionId);
          setAlgorithmSlug(algorithmSlug);
        } else {
          // ── Server path: create session, open WebSocket ─────────────────
          const session = await api.simulations.create({
            algorithm_slug: algorithmSlug,
            params,
            seed,
          });

          if (cancelled) return;

          setSessionId(session.session_id);
          setAlgorithmSlug(algorithmSlug);

          ctrl = new WebSocketController(
            session.session_id,
            api.ws.simulationUrl(session.session_id),
          );
        }

        controllerRef.current = ctrl;

        ctrl.onFrame = (frame) => { if (!cancelled) setFrame(frame); };
        ctrl.onStatus = (status, meta) => {
          if (!cancelled) {
            setStatus(status);
            if (meta?.['total_frames'] !== undefined) {
              setTotalFrames(meta['total_frames'] as number);
            }
          }
        };
        ctrl.onError = (code, message) => {
          console.error(`[${algorithmSlug}] Simulation error ${code}: ${message}`);
        };

        const initialFrame = await ctrl.connect();
        if (!cancelled) {
          setController(ctrl);
          setFrame(initialFrame);
          setStatus('paused');
          // WASM controllers know totalFrames immediately after connect()
          if (ctrl.totalFrames !== null) {
            setTotalFrames(ctrl.totalFrames);
          }
        }
      } catch (err) {
        if (!cancelled) {
          console.error('Failed to start simulation:', err);
          setStatus('error');
          setErrorMsg(err instanceof Error ? err.message : String(err));
        }
      }
    }

    startSimulation();

    return () => {
      cancelled = true;
      controllerRef.current?.destroy();
      controllerRef.current = null;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [algorithmSlug, executionTarget, seed, JSON.stringify(params), retryKey]);

  const Renderer = getRenderer(visualizationType);

  return (
    <div className="w-full">
      {currentFrame ? (
        <Renderer state={currentFrame.state} />
      ) : errorMsg ? (
        <div className="flex items-center justify-center h-64 text-neutral-500">
          <div className="flex flex-col items-center gap-3 max-w-sm text-center px-4">
            <div className="w-8 h-8 rounded-full bg-red-500/10 flex items-center justify-center">
              <svg className="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <span className="text-sm text-red-400">Simulation failed to start</span>
            <span className="text-xs text-neutral-600 font-mono break-all">{errorMsg}</span>
            <button
              onClick={() => setRetryKey(k => k + 1)}
              className="px-3 py-1.5 rounded-lg text-xs bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-center h-64 text-neutral-500">
          <div className="flex flex-col items-center gap-3">
            <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm">
              {executionTarget === 'wasm' || executionTarget === 'both'
                ? 'Loading WASM engine…'
                : 'Initializing simulation…'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
