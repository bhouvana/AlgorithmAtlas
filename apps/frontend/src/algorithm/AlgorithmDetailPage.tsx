/**
 * AlgorithmDetailPage — main learning page for a single algorithm.
 *
 * Layout (top to bottom):
 *   Breadcrumb  — catalog / category / name
 *   Hero        — name, complexity badges, description, tags
 *   Tab bar     — Simulation | Code | Info
 *   Tab content — animated panel per tab
 */

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Code2, Info, ChevronLeft, Share2, GitCompare, Zap, Server } from 'lucide-react';
import { api, type AlgorithmDetail } from '../core/api/client';
import { SimulationCanvas } from '../simulation/SimulationCanvas';
import { SimulationControls } from '../simulation/SimulationControls';
import { ParameterPanel, type ParameterValues } from '../simulation/ParameterPanel';

import { CodeViewer } from './CodeViewer';
import { useKeyboardControls } from '../shared/hooks/useKeyboardControls';
import type { VisualizationType } from '../visualization/RendererRegistry';
import { cn } from '../lib/utils';

type DetailTab = 'simulate' | 'code' | 'info';

export function AlgorithmDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const [algorithm, setAlgorithm] = useState<AlgorithmDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [simParams, setSimParams] = useState<ParameterValues>({});
  const [paramKey, setParamKey] = useState(0);
  const [activeTab, setActiveTab] = useState<DetailTab>('simulate');

  useKeyboardControls();

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    api.algorithms.get(slug)
      .then((data) => { setAlgorithm(data); setLoading(false); })
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, [slug]);

  const handleParamApply = useCallback((values: ParameterValues) => {
    setSimParams(values);
    setParamKey((k) => k + 1);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-[#18181B] border border-charcoal/10 flex items-center justify-center animate-pulse">
            <span className="text-indigo-400 text-xl">⬡</span>
          </div>
          <p className="text-zinc-500 text-sm">Loading algorithm...</p>
        </div>
      </div>
    );
  }

  if (error || !algorithm) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <p className="text-red-400 text-sm">{error ?? 'Algorithm not found'}</p>
          <Link to="/algorithms" className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors">
            ← Back to catalog
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <div className="max-w-5xl mx-auto px-6 py-10 flex flex-col gap-8">

        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm text-zinc-500">
          <Link
            to="/algorithms"
            className="hover:text-zinc-300 transition-colors flex items-center gap-1"
          >
            <ChevronLeft className="w-3 h-3" /> Catalog
          </Link>
          <span>/</span>
          <span className="capitalize text-zinc-400">{algorithm.category.replace(/-/g, ' ')}</span>
          <span>/</span>
          <span className="text-white">{algorithm.name}</span>
        </div>

        {/* Hero */}
        <div className="flex flex-col gap-4">
          <div className="flex items-start justify-between gap-4">
            <h1 className="text-4xl font-bold text-white leading-tight">{algorithm.name}</h1>
            <div className="flex items-center gap-2 flex-shrink-0">
              <EmbedButton slug={algorithm.slug} />
              <Link
                to={`/compare?a=${algorithm.slug}`}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#18181B] border border-charcoal/10 text-zinc-400 hover:text-white hover:border-white/20 text-xs transition-all"
              >
                <GitCompare className="w-3 h-3" /> Compare
              </Link>
            </div>
          </div>

          {/* Complexity badges row */}
          <div className="flex flex-wrap gap-2">
            {[
              { label: 'Best',    value: algorithm.complexity.time_best,    textColor: '#34d399', bgColor: 'rgba(16,185,129,0.08)',  shadowColor: 'rgba(16,185,129,0.18)' },
              { label: 'Average', value: algorithm.complexity.time_average, textColor: '#60a5fa', bgColor: 'rgba(59,130,246,0.08)',   shadowColor: 'rgba(59,130,246,0.18)' },
              { label: 'Worst',   value: algorithm.complexity.time_worst,   textColor: '#fbbf24', bgColor: 'rgba(245,158,11,0.08)',   shadowColor: 'rgba(245,158,11,0.18)' },
              { label: 'Space',   value: algorithm.complexity.space,        textColor: '#c084fc', bgColor: 'rgba(168,85,247,0.08)',   shadowColor: 'rgba(168,85,247,0.18)' },
            ].map(({ label, value, textColor, bgColor, shadowColor }) => (
              <span
                key={label}
                className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-mono"
                style={{
                  color: textColor,
                  backgroundColor: bgColor,
                  boxShadow: `inset 0 0 0 1px ${shadowColor}`,
                }}
              >
                <span style={{ opacity: 0.6 }}>{label}</span>
                <span className="font-semibold">{value}</span>
              </span>
            ))}
          </div>

          {/* Description */}
          <p className="text-zinc-400 leading-relaxed max-w-2xl">{algorithm.description}</p>

          {/* Tags */}
          {algorithm.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {algorithm.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2.5 py-1 rounded-lg text-zinc-500 text-xs"
                  style={{ backgroundColor: 'rgba(255,255,255,0.04)', boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.07)' }}
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Tab navigation — floating pill style */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1 p-1 rounded-2xl bg-[#18181B] border border-charcoal/10">
            {[
              { key: 'simulate', label: 'Simulation', icon: <Play className="w-3.5 h-3.5" /> },
              { key: 'code',     label: 'Code',       icon: <Code2 className="w-3.5 h-3.5" /> },
              { key: 'info',     label: 'Info',       icon: <Info className="w-3.5 h-3.5" /> },
            ].map(({ key, label, icon }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key as DetailTab)}
                className={cn(
                  'relative flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200',
                  activeTab === key ? 'text-white' : 'text-zinc-500 hover:text-zinc-300'
                )}
              >
                {activeTab === key && (
                  <motion.div
                    layoutId="tab-active"
                    className="absolute inset-0 bg-[#09090B] rounded-xl border border-charcoal/10"
                    transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                  />
                )}
                <span className="relative z-10">{icon}</span>
                <span className="relative z-10">{label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Tab content */}
        <AnimatePresence mode="wait">

          {/* ── Simulate tab ──────────────────────────────────────────── */}
          {activeTab === 'simulate' && (
            <motion.div
              key="simulate"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
              className="flex flex-col gap-4"
            >
              {/* Parameter panel */}
              {Object.keys(algorithm.default_params).length > 0 && (
                <div className="rounded-2xl bg-[#18181B] border border-charcoal/10 p-4">
                  <ParameterPanel
                    schema={algorithm.default_params}
                    onApply={handleParamApply}
                  />
                </div>
              )}

              {/* Main simulation area */}
              <div className="rounded-2xl bg-[#111113] border border-charcoal/10 overflow-hidden">
                {/* Top bar */}
                <div className="flex items-center justify-between px-5 py-3 border-b border-charcoal/10">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-zinc-500 font-mono uppercase tracking-wider">
                      Simulation
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    {algorithm.execution_target === 'wasm' ? (
                      <span className="flex items-center gap-1 text-xs text-emerald-400">
                        <Zap className="w-3 h-3" /> Browser
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-xs text-zinc-500">
                        <Server className="w-3 h-3" /> Server
                      </span>
                    )}
                  </div>
                </div>

                {/* Canvas */}
                <div className="p-6">
                  <SimulationCanvas
                    key={paramKey}
                    algorithmSlug={algorithm.slug}
                    visualizationType={algorithm.visualization_type as VisualizationType}
                    executionTarget={algorithm.execution_target as 'server' | 'wasm' | 'both'}
                    seed={42}
                    params={simParams}
                  />
                </div>

                {/* Controls */}
                <div className="px-6 pb-6">
                  <SimulationControls />
                </div>
              </div>


            </motion.div>
          )}

          {/* ── Code tab ──────────────────────────────────────────────── */}
          {activeTab === 'code' && (
            <motion.div
              key="code"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
            >
              <div className="rounded-2xl bg-[#111113] border border-charcoal/10 overflow-hidden">
                <div className="flex items-center gap-2 px-5 py-3 border-b border-charcoal/10">
                  <Code2 className="w-4 h-4 text-zinc-500" />
                  <span className="text-xs text-zinc-500 font-mono uppercase tracking-wider">
                    Source Code
                  </span>
                </div>
                <CodeViewer slug={slug!} />
              </div>
            </motion.div>
          )}

          {/* ── Info tab ──────────────────────────────────────────────── */}
          {activeTab === 'info' && (
            <motion.div
              key="info"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
              className="flex flex-col gap-4"
            >
              <Section title="Description">
                <p className="text-zinc-300 leading-relaxed">{algorithm.description}</p>
              </Section>

              {algorithm.intuition && (
                <Section title="Intuition">
                  <p className="text-zinc-300 leading-relaxed">{algorithm.intuition}</p>
                </Section>
              )}

              {algorithm.references.length > 0 && (
                <Section title="References">
                  <ul className="flex flex-col gap-2">
                    {algorithm.references.map((ref, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-zinc-400">
                        <ReferenceTypeTag type={ref.type} />
                        {ref.url ? (
                          <a
                            href={ref.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-indigo-400 hover:underline"
                          >
                            {ref.title}
                          </a>
                        ) : (
                          <span>{ref.title}</span>
                        )}
                      </li>
                    ))}
                  </ul>
                </Section>
              )}
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </div>
  );
}

// ── Sub-components ───────────────────────────────────────────────────────────

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-2xl bg-[#18181B] border border-charcoal/10 p-6 flex flex-col gap-3">
      <h2 className="text-xs font-mono uppercase tracking-wider text-zinc-500">{title}</h2>
      {children}
    </div>
  );
}

function ReferenceTypeTag({ type }: { type: string }) {
  const colors: Record<string, string> = {
    book:    'bg-amber-900/40 text-amber-400',
    paper:   'bg-blue-900/40 text-blue-400',
    video:   'bg-red-900/40 text-red-400',
    article: 'bg-green-900/40 text-green-400',
  };
  return (
    <span
      className={`shrink-0 px-1.5 py-0.5 rounded text-xs ${colors[type] ?? 'bg-zinc-800 text-zinc-400'}`}
    >
      {type}
    </span>
  );
}

function EmbedButton({ slug }: { slug: string }) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const dialogRef = useRef<HTMLDivElement>(null);

  const origin = typeof window !== 'undefined' ? window.location.origin : '';
  const src = `${origin}/embed/${slug}?n=30&autoplay=1`;
  const snippet = `<iframe\n  src="${src}"\n  width="720"\n  height="420"\n  frameborder="0"\n  allowfullscreen\n></iframe>`;

  const copy = () => {
    navigator.clipboard.writeText(snippet).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  // Close on outside click
  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (dialogRef.current && !dialogRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [open]);

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#18181B] border border-charcoal/10 text-zinc-400 hover:text-white hover:border-white/20 text-xs transition-all"
      >
        <Share2 className="w-3 h-3" /> Embed
      </button>

      {open && (
        <div
          ref={dialogRef}
          className="absolute right-0 top-10 z-50 w-80 rounded-2xl border border-charcoal/10 bg-[#111113] shadow-[0_24px_64px_rgba(0,0,0,0.6)] p-5 flex flex-col gap-3"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-zinc-300">Embed this visualization</span>
            <button
              onClick={() => setOpen(false)}
              className="text-zinc-600 hover:text-zinc-300 text-sm leading-none"
            >
              ✕
            </button>
          </div>

          <pre className="rounded-lg bg-[#09090B] border border-charcoal/10 p-3 text-xs text-zinc-400 whitespace-pre-wrap break-all font-mono leading-relaxed select-all">
            {snippet}
          </pre>

          <button
            onClick={copy}
            className={cn(
              'w-full rounded-lg py-1.5 text-xs font-medium transition-colors',
              copied
                ? 'bg-emerald-600/30 text-emerald-400 border border-emerald-700/30'
                : 'bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 border border-indigo-700/30'
            )}
          >
            {copied ? 'Copied!' : 'Copy snippet'}
          </button>

          <p className="text-xs text-zinc-600 leading-relaxed">
            Add <code className="text-zinc-400">seed=</code> or{' '}
            <code className="text-zinc-400">speed=</code> params to customise. Remove{' '}
            <code className="text-zinc-400">autoplay=1</code> to start paused.
          </p>
        </div>
      )}
    </div>
  );
}
