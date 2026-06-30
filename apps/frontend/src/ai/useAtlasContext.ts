/**
 * useAtlasContext — assembles the full AtlasContext from live app state.
 *
 * Reads from:
 *   - useLocation()          → current page
 *   - useParams()            → algorithm slug
 *   - useSimulationStore()   → visualization state + current frame
 *   - useProgressStore()     → XP, level, completedLessons
 *   - NotebookBridgeContext  → language, source, lastOutput, lastError
 *   - getOrCreateUserId()    → anonymous persistent user ID
 */
import { useLocation, useParams } from 'react-router-dom';
import { useContext } from 'react';

import { useSimulationStore } from '../core/store/simulationStore';
import { useProgressStore } from '../learning/store/progressStore';
import { NotebookBridgeContext } from '../notebook/NotebookBridgeContext';
import { getOrCreateUserId } from './api';
import type { AtlasContext } from './types';

function derivePage(pathname: string): string {
  if (pathname === '/') return 'landing';
  if (pathname.startsWith('/algorithms/')) return 'algorithm';
  if (pathname.startsWith('/algorithms')) return 'catalog';
  if (pathname.startsWith('/compare')) return 'compare';
  if (pathname.startsWith('/notebook')) return 'notebook';
  if (pathname.startsWith('/experiments')) return 'experiments';
  if (pathname.startsWith('/learning/')) return 'lesson';
  if (pathname.startsWith('/learning')) return 'learning';
  return 'landing';
}

export function useAtlasContext(): AtlasContext {
  const { pathname } = useLocation();
  const params = useParams<{ slug?: string; id?: string }>();

  const sim = useSimulationStore();
  const progress = useProgressStore();
  const notebook = useContext(NotebookBridgeContext);

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
  const notebookCtx = notebook
    ? {
        language: notebook.language,
        source: notebook.source,
        lastOutput: notebook.lastOutput,
        lastError: notebook.lastError,
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

  return ctx;
}
