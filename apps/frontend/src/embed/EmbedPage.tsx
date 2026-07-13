/**
 * EmbedPage — minimal iframe-embeddable algorithm visualization.
 *
 * Route: /embed/:slug
 * Query params:
 *   seed=<int>        PRNG seed (default 42)
 *   n=<int>           array_size (default 20)
 *   autoplay=1        start playing immediately
 *   speed=<float>     playback speed (default 1)
 *
 * Example embed:
 *   <iframe
 *     src="/embed/bubble-sort?n=30&autoplay=1"
 *     width="720" height="420"
 *     frameborder="0" allowfullscreen
 *   />
 */

import { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { api, type AlgorithmDetail } from '../core/api/client';
import { SimulationCanvas } from '../simulation/SimulationCanvas';
import { SimulationControls } from '../simulation/SimulationControls';
import { useSimulationStore } from '../core/store/simulationStore';
import type { VisualizationType } from '../visualization/RendererRegistry';

export function EmbedPage() {
  const { slug } = useParams<{ slug: string }>();
  const [searchParams] = useSearchParams();
  const [algorithm, setAlgorithm] = useState<AlgorithmDetail | null>(null);
  const [ready, setReady] = useState(false);

  const seed      = parseInt(searchParams.get('seed') ?? '42', 10);
  const arraySize = parseInt(searchParams.get('n')    ?? '20', 10);
  const autoplay  = searchParams.get('autoplay') === '1';
  const speed     = parseFloat(searchParams.get('speed') ?? '1');

  const controller = useSimulationStore((s) => s.controller);
  const status     = useSimulationStore((s) => s.status);

  useEffect(() => {
    if (!slug) return;
    api.algorithms.get(slug)
      .then((data) => { setAlgorithm(data); setReady(true); })
      .catch(() => setReady(true));
  }, [slug]);

  // Auto-play once connected
  useEffect(() => {
    if (!autoplay || !controller || status !== 'paused') return;
    controller.play(speed);
  }, [autoplay, controller, status, speed]);

  if (!ready) {
    return (
      <div className="h-screen flex items-center justify-center bg-neutral-950">
        <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!algorithm || !slug) {
    return (
      <div className="h-screen flex items-center justify-center bg-neutral-950 text-neutral-500 text-sm">
        Algorithm not found
      </div>
    );
  }

  return (
    <div className="h-screen bg-neutral-950 flex flex-col">
      {/* Minimal header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-white/5 shrink-0">
        <span className="text-sm font-medium text-neutral-300">{algorithm.name}</span>
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono text-neutral-600">
            {algorithm.complexity.time_average} avg
          </span>
          <a
            href={`/algorithms/${slug}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            ⬡ Atlas ↗
          </a>
        </div>
      </div>

      {/* Visualization */}
      <div className="flex-1 min-h-0 p-3 flex flex-col gap-2">
        <div className="flex-1 min-h-0 bg-neutral-900 rounded-xl border border-charcoal/10 overflow-hidden">
          <SimulationCanvas
            algorithmSlug={slug}
            visualizationType={algorithm.visualization_type as VisualizationType}
            executionTarget={algorithm.execution_target as 'server' | 'wasm' | 'both'}
            seed={seed}
            params={arraySize !== 20 ? { array_size: arraySize } : {}}
          />
        </div>
        <SimulationControls />
      </div>
    </div>
  );
}
