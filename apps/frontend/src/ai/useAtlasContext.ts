/**
 * useAtlasContext — assembles the full AtlasContext from live app state.
 *
 * Reads from:
 *   - useLocation()          → current page
 *   - useParams()            → algorithm slug
 *   - useSimulationStore()   → visualization state + current frame
 *   - useProgressStore()     → XP, level, completedLessons
 *   - useAtlasStore          → notebook bridge (language, source, lastOutput, lastError)
 *                              + AtlasCode problem bridge (Run-only; no hidden test data)
 *   - getOrCreateUserId()    → anonymous persistent user ID
 */
import { useLocation, useParams } from 'react-router-dom';

import { useSimulationStore } from '../core/store/simulationStore';
import { useProgressStore } from '../learning/store/progressStore';
import { useAtlasStore } from './store';
import { getOrCreateUserId } from './api';
import type { AtlasContext } from './types';

function derivePage(pathname: string): string {
  if (pathname === '/') return 'landing';
  if (pathname.startsWith('/atlas-code/problem/')) return 'atlascode';
  if (pathname.startsWith('/atlas-code')) return 'atlascode-catalog';
  if (pathname.startsWith('/algorithms/')) return 'algorithm';
  if (pathname.startsWith('/algorithms')) return 'catalog';
  if (pathname.startsWith('/compare')) return 'compare';
  if (pathname.startsWith('/compiler')) return 'notebook';
  if (pathname.startsWith('/learning/')) return 'lesson';
  if (pathname.startsWith('/learning')) return 'learning';
  return 'landing';
}

export function useAtlasContext(): AtlasContext {
  const { pathname } = useLocation();
  const params = useParams<{ slug?: string; id?: string }>();

  const sim = useSimulationStore();
  const progress = useProgressStore();
  const notebookBridge = useAtlasStore((s) => s.notebookBridge);
  const problemBridge = useAtlasStore((s) => s.problemBridge);

  const page = derivePage(pathname);
  const userId = getOrCreateUserId();

  // ── Simulation context ─────────────────────────────────────────────────────
  const simulationCtx = sim.controller
    ? {
        status: sim.status,
        currentFrameIndex: sim.currentFrameIndex,
        totalFrames: sim.totalFrames,
        playbackSpeed: sim.playbackSpeed,
        currentFrame: (sim.currentFrame?.state ?? null) as Record<string, unknown> | null,
        eventLabel: sim.currentFrame?.event_label ?? null,
      }
    : undefined;

  // ── Algorithm context from simulation store slug ───────────────────────────
  const algorithmSlug = sim.algorithmSlug ?? params.slug ?? undefined;

  // ── Learning progress ──────────────────────────────────────────────────────
  const completedLessons = Object.keys(progress.lessons)
    .filter((id) => progress.lessons[id]?.completedAt != null);
  const xp = progress.xp ?? 0;
  const level = progress.level ?? 1;

  const learningProgressCtx = {
    xp,
    level,
    completedLessons,
    currentStreak: 0, // streak not yet tracked in store
  };

  // ── Notebook context ───────────────────────────────────────────────────────
  const notebookCtx = notebookBridge
    ? {
        language: notebookBridge.language,
        source: notebookBridge.source,
        lastOutput: notebookBridge.lastOutput,
        lastError: notebookBridge.lastError,
      }
    : undefined;

  // ── Comparison context ─────────────────────────────────────────────────────
  const comparisonCtx =
    page === 'compare'
      ? { algorithmA: null, algorithmB: null }  // filled in by ComparisonPage if exposed
      : undefined;

  const ctx: AtlasContext = {
    page,
    userId,
    learningProgress: learningProgressCtx,
  };

  if (algorithmSlug) {
    ctx.algorithm = {
      slug: algorithmSlug,
      name: algorithmSlug.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
      category: '',
      visualization_type: '',
    };
  }

  if (simulationCtx) ctx.simulation = simulationCtx;
  if (notebookCtx && page === 'notebook') ctx.notebook = notebookCtx;
  if (comparisonCtx) ctx.comparison = comparisonCtx;
  if (problemBridge && page === 'atlascode') ctx.problem = problemBridge;

  return ctx;
}
