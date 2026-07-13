/**
 * CatalogPage — browse and filter the algorithm catalog.
 *
 * Phase 4.3 additions:
 *   - Offline awareness via useServerAvailable hook
 *   - Offline banner with "Launch server" Tauri command in desktop app
 *   - WASM-only badge in offline mode
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Search, X, ChevronDown, ChevronLeft, ChevronRight, Zap } from 'lucide-react';
import { api, type AlgorithmSummary, type CategoryInfo } from '../core/api/client';
import { useServerAvailable, isTauriApp } from '../core/hooks/useServerAvailable';
import { tauriInvoke } from '../core/tauri';
import { AnimateIn } from '../components/ui/AnimateIn';
import { cn } from '../lib/utils';

// ── Category color map ────────────────────────────────────────────────────────

const CATEGORY_COLORS: Record<string, string> = {
  'sorting': '#4F46E5',
  'searching': '#0EA5E9',
  'graph': '#10B981',
  'dynamic-programming': '#8B5CF6',
  'tree': '#F59E0B',
  'backtracking': '#EF4444',
  'greedy': '#F97316',
  'divide-and-conquer': '#06B6D4',
  'string': '#EC4899',
  'number-theory': '#84CC16',
  'machine-learning': '#6366F1',
  'computational-geometry': '#14B8A6',
  'randomized': '#A78BFA',
  'optimization': '#FB923C',
  'probability': '#38BDF8',
  'cellular-automata': '#4ADE80',
  'cryptography': '#F43F5E',
  'distributed-systems': '#FCD34D',
  'data-structures': '#C084FC',
};

// ── Complexity badge inline styles (inset ring, no choppy CSS border) ─────────

const COMPLEXITY_BADGE_STYLES: Record<string, { color: string; bg: string; ring: string }> = {
  'O(1)':       { color: '#34d399', bg: 'rgba(16,185,129,0.07)',  ring: 'rgba(16,185,129,0.25)' },
  'O(log n)':   { color: '#2dd4bf', bg: 'rgba(20,184,166,0.07)',  ring: 'rgba(20,184,166,0.25)' },
  'O(n)':       { color: '#60a5fa', bg: 'rgba(59,130,246,0.07)',  ring: 'rgba(59,130,246,0.25)' },
  'O(n log n)': { color: '#818cf8', bg: 'rgba(99,102,241,0.07)',  ring: 'rgba(99,102,241,0.25)' },
  'O(n²)':      { color: '#fbbf24', bg: 'rgba(245,158,11,0.07)',  ring: 'rgba(245,158,11,0.25)' },
  'O(2^n)':     { color: '#fb923c', bg: 'rgba(249,115,22,0.07)',  ring: 'rgba(249,115,22,0.25)' },
  'O(n!)':      { color: '#f87171', bg: 'rgba(239,68,68,0.07)',   ring: 'rgba(239,68,68,0.25)'  },
};
const DEFAULT_BADGE_STYLE = { color: '#a1a1aa', bg: 'rgba(161,161,170,0.07)', ring: 'rgba(161,161,170,0.18)' };

// ── Offline banner ────────────────────────────────────────────────────────────

type LaunchState = 'idle' | 'launching' | 'launched' | 'error';

function OfflineBanner({ onLaunched }: { onLaunched: () => void }) {
  const [launchState, setLaunchState] = useState<LaunchState>('idle');
  const [errorMsg, setErrorMsg] = useState('');
  const inTauri = isTauriApp();

  const handleLaunch = useCallback(async () => {
    setLaunchState('launching');
    try {
      await tauriInvoke<boolean>('launch_backend');
      setLaunchState('launched');
      // Give uvicorn ~1.5 s to start, then re-probe
      setTimeout(onLaunched, 1500);
    } catch (e) {
      setErrorMsg(String(e));
      setLaunchState('error');
    }
  }, [onLaunched]);

  return (
    <div className="flex items-center justify-between gap-3 px-4 py-3 rounded-xl bg-amber-900/20 border border-amber-700/30 text-sm">
      <div className="flex items-center gap-2">
        <span className="text-amber-400 text-base">⚡</span>
        <span className="text-amber-300 font-medium">Offline mode</span>
        <span className="text-amber-600 text-xs">
          — only WASM-enabled algorithms are available. Start the API server for the full catalog.
        </span>
      </div>
      {inTauri && (
        <button
          onClick={handleLaunch}
          disabled={launchState === 'launching' || launchState === 'launched'}
          className="shrink-0 px-3 py-1 rounded-lg bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white text-xs font-medium transition-colors"
        >
          {launchState === 'launching' ? 'Starting…'
           : launchState === 'launched' ? 'Started'
           : launchState === 'error'    ? 'Failed'
           :                             'Launch server'}
        </button>
      )}
      {launchState === 'error' && (
        <span className="text-red-400 text-xs font-mono">{errorMsg}</span>
      )}
    </div>
  );
}

// ── Complexity ordering for sort ──────────────────────────────────────────────

const COMPLEXITY_ORDER: Record<string, number> = {
  'O(1)': 0, 'O(log n)': 1, 'O(n)': 2,
  'O(n log n)': 3, 'O(n²)': 4, 'O(2^n)': 5, 'O(n!)': 6,
};

type SortBy = 'name' | 'complexity' | 'category';

const PAGE_SIZE = 24;

// ── Main page ─────────────────────────────────────────────────────────────────

export function CatalogPage() {
  const [algorithms,         setAlgorithms]         = useState<AlgorithmSummary[]>([]);
  const [categories,         setCategories]         = useState<CategoryInfo[]>([]);
  const [selectedCat,        setSelectedCat]        = useState<string | null>(null);
  const [selectedComplexity, setSelectedComplexity] = useState<string | null>(null);
  const [selectedTag,        setSelectedTag]        = useState<string | null>(null);
  const [search,             setSearch]             = useState('');
  const [sortBy,             setSortBy]             = useState<SortBy>('name');
  const [loading,            setLoading]            = useState(true);
  const [error,              setError]              = useState<string | null>(null);
  const [loadKey,            setLoadKey]            = useState(0);
  const [currentPage,        setCurrentPage]        = useState(1);

  const serverAvailable = useServerAvailable();
  const isOffline = serverAvailable === false;

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([api.algorithms.list(), api.algorithms.categories()])
      .then(([algs, cats]) => {
        setAlgorithms(algs);
        setCategories(cats);
        setLoading(false);
      })
      .catch((e: Error) => {
        setError(e.message);
        setLoading(false);
      });
  }, [loadKey]);

  const handleServerLaunched = useCallback(() => setLoadKey((k) => k + 1), []);

  // Reset to page 1 when any filter or sort changes
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedCat, selectedComplexity, selectedTag, search, sortBy]);

  // Scroll to top of page when page changes (skip on first render)
  const firstRender = useRef(true);
  useEffect(() => {
    if (firstRender.current) { firstRender.current = false; return; }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [currentPage]);

  // All unique complexity classes present in the data, in canonical order
  const allComplexities = useMemo(() => {
    const seen = new Set<string>();
    algorithms.forEach((a) => seen.add(a.complexity.time_average));
    return [...seen].sort(
      (a, b) => (COMPLEXITY_ORDER[a] ?? 99) - (COMPLEXITY_ORDER[b] ?? 99),
    );
  }, [algorithms]);


  const filtered = useMemo(() => {
    let result = algorithms;
    if (isOffline) result = result.filter((a) => a.execution_target === 'wasm' || a.execution_target === 'both');
    if (selectedCat)        result = result.filter((a) => a.category === selectedCat);
    if (selectedComplexity) result = result.filter((a) => a.complexity.time_average === selectedComplexity);
    if (selectedTag)        result = result.filter((a) => a.tags.includes(selectedTag));
    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter(
        (a) =>
          a.name.toLowerCase().includes(q) ||
          a.tags.some((t) => t.toLowerCase().includes(q)) ||
          a.description.toLowerCase().includes(q),
      );
    }
    const copy = [...result];
    if (sortBy === 'name') {
      copy.sort((a, b) => a.name.localeCompare(b.name));
    } else if (sortBy === 'complexity') {
      copy.sort(
        (a, b) =>
          (COMPLEXITY_ORDER[a.complexity.time_average] ?? 99) -
          (COMPLEXITY_ORDER[b.complexity.time_average] ?? 99),
      );
    } else {
      copy.sort((a, b) => a.category.localeCompare(b.category) || a.name.localeCompare(b.name));
    }
    return copy;
  }, [algorithms, selectedCat, selectedComplexity, selectedTag, search, sortBy, isOffline]);

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paginated = useMemo(
    () => filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE),
    [filtered, currentPage],
  );

  const activeFilterCount = [selectedCat, selectedComplexity, selectedTag].filter(Boolean).length;

  const clearAllFilters = () => {
    setSelectedCat(null);
    setSelectedComplexity(null);
    setSelectedTag(null);
    setSearch('');
  };

  return (
    <div className="min-h-screen">
      <div className="max-w-6xl mx-auto px-6 pt-8 pb-16">

        {/* ── Hero header ───────────────────────────────────────────────────── */}
        <AnimateIn className="mb-8">
          <div className="flex flex-col items-center text-center gap-3">
            <h1 className="text-4xl font-bold text-white tracking-tight">
              Algorithm Catalog
            </h1>
            <p className="text-zinc-400 text-sm">
              {isOffline
                ? `${algorithms.filter((a) => a.execution_target !== 'server').length} WASM algorithms available offline`
                : `${algorithms.length} algorithms across ${categories.length} categories`}
            </p>
            {activeFilterCount > 0 && (
              <button
                onClick={clearAllFilters}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-zinc-800/60 border border-charcoal/10 text-zinc-400 text-xs hover:text-white hover:border-white/15 transition-all duration-200"
              >
                <X className="w-3 h-3" />
                Clear {activeFilterCount} filter{activeFilterCount > 1 ? 's' : ''}
              </button>
            )}
          </div>
        </AnimateIn>

        {/* ── Offline banner ─────────────────────────────────────────────────── */}
        {isOffline && (
          <AnimateIn delay={0.03} className="mb-6">
            <OfflineBanner onLaunched={handleServerLaunched} />
          </AnimateIn>
        )}

        {/* ── Search bar ────────────────────────────────────────────────────── */}
        <AnimateIn delay={0.05} className="mb-4">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 pointer-events-none" />
            <input
              type="search"
              placeholder="Search algorithms, categories, complexity..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-11 pr-10 h-12 rounded-2xl bg-[#18181B] border border-charcoal/10 text-white placeholder:text-zinc-600 text-sm focus:outline-none focus:border-indigo-500/50 focus:ring-2 focus:ring-indigo-500/20 transition-all duration-200"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </AnimateIn>

        {/* ── Category pills ────────────────────────────────────────────────── */}
        <AnimateIn delay={0.07} className="mb-4">
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
            {/* "All" pill */}
            <button
              onClick={() => setSelectedCat(null)}
              className={cn(
                'relative shrink-0 flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium border transition-all duration-200',
                selectedCat === null
                  ? 'bg-indigo-600/20 border-indigo-500/50 text-indigo-300'
                  : 'bg-[#18181B] border-charcoal/10 text-zinc-400 hover:border-indigo-500/30 hover:text-white',
              )}
            >
              {selectedCat === null && (
                <motion.span
                  layoutId="cat-active"
                  className="absolute inset-0 rounded-full bg-indigo-600/15 border border-indigo-500/40"
                  transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                />
              )}
              <span className="relative">All</span>
              <span className="relative text-[10px] opacity-60">{algorithms.length}</span>
            </button>

            {categories.map((cat) => (
              <button
                key={cat.slug}
                onClick={() => setSelectedCat(cat.slug)}
                className={cn(
                  'relative shrink-0 flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium border transition-all duration-200',
                  selectedCat === cat.slug
                    ? 'bg-indigo-600/20 border-indigo-500/50 text-indigo-300'
                    : 'bg-[#18181B] border-charcoal/10 text-zinc-400 hover:border-indigo-500/30 hover:text-white',
                )}
              >
                {selectedCat === cat.slug && (
                  <motion.span
                    layoutId="cat-active"
                    className="absolute inset-0 rounded-full bg-indigo-600/15 border border-indigo-500/40"
                    transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                  />
                )}
                <span
                  className="relative w-1.5 h-1.5 rounded-full shrink-0"
                  style={{ backgroundColor: CATEGORY_COLORS[cat.slug] ?? '#6B7280' }}
                />
                <span className="relative capitalize">{cat.name}</span>
                <span className="relative text-[10px] opacity-60">{cat.algorithm_count}</span>
              </button>
            ))}
          </div>
        </AnimateIn>

        {/* ── Sort + complexity row ─────────────────────────────────────────── */}
        <AnimateIn delay={0.09} className="mb-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative">
              <select
                value={selectedComplexity ?? ''}
                onChange={(e) => setSelectedComplexity(e.target.value || null)}
                className="appearance-none bg-[#18181B] border border-charcoal/10 text-white text-sm rounded-xl pl-3 pr-8 h-9 focus:border-indigo-500/50 focus:outline-none transition-colors cursor-pointer"
              >
                <option value="">Any complexity</option>
                {allComplexities.map((c) => (
                  <option key={c} value={c}>{c} avg</option>
                ))}
              </select>
              <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-500 pointer-events-none" />
            </div>

            <div className="relative">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortBy)}
                className="appearance-none bg-[#18181B] border border-charcoal/10 text-white text-sm rounded-xl pl-3 pr-8 h-9 focus:border-indigo-500/50 focus:outline-none transition-colors cursor-pointer"
              >
                <option value="name">Sort: A–Z</option>
                <option value="complexity">Sort: Complexity</option>
                <option value="category">Sort: Category</option>
              </select>
              <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-500 pointer-events-none" />
            </div>

          </div>
        </AnimateIn>

        {/* ── Algorithm grid ────────────────────────────────────────────────── */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 12 }).map((_, i) => (
              <div
                key={i}
                className="h-44 rounded-2xl bg-[#18181B] border border-charcoal/10 animate-pulse"
              />
            ))}
          </div>
        ) : error && !isOffline ? (
          <div className="flex flex-col items-center justify-center h-64 gap-3">
            <div className="w-12 h-12 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center">
              <X className="w-5 h-5 text-red-400" />
            </div>
            <p className="text-red-400 font-medium">Failed to load catalog</p>
            <p className="text-zinc-600 text-sm font-mono">{error}</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 gap-4 text-center">
            <div className="w-16 h-16 rounded-2xl bg-[#18181B] border border-charcoal/10 flex items-center justify-center">
              <Search className="w-7 h-7 text-zinc-600" />
            </div>
            <p className="text-zinc-400 font-medium">No algorithms match your search</p>
            <p className="text-zinc-600 text-sm">Try adjusting your filters or search terms</p>
            <button
              onClick={clearAllFilters}
              className="px-4 py-2 rounded-xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-300 text-sm hover:bg-indigo-600/30 transition-colors"
            >
              Clear all filters
            </button>
          </div>
        ) : (
          <>
            <AnimatePresence mode="popLayout">
              <motion.div
                key={`grid-page-${currentPage}`}
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
              >
                {paginated.map((alg, index) => (
                  <motion.div
                    key={alg.slug}
                    layout
                    initial={{ opacity: 0, y: 12, scale: 0.97 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.97 }}
                    transition={{ duration: 0.2, delay: Math.min(index * 0.022, 0.28), ease: [0.22, 1, 0.36, 1] }}
                  >
                    <AlgorithmCard
                      algorithm={alg}
                      onTagClick={setSelectedTag}
                    />
                  </motion.div>
                ))}
              </motion.div>
            </AnimatePresence>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-10 flex flex-col items-center gap-3">
                <p className="text-xs text-zinc-600">
                  Showing {(currentPage - 1) * PAGE_SIZE + 1}–{Math.min(currentPage * PAGE_SIZE, filtered.length)} of {filtered.length} algorithms
                </p>
                <Pagination current={currentPage} total={totalPages} onChange={setCurrentPage} />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// ── Pagination ────────────────────────────────────────────────────────────────

function Pagination({ current, total, onChange }: { current: number; total: number; onChange: (p: number) => void }) {
  const pages: (number | '...')[] = [];

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i);
  } else {
    pages.push(1);
    if (current > 3) pages.push('...');
    const lo = Math.max(2, current - 1);
    const hi = Math.min(total - 1, current + 1);
    for (let i = lo; i <= hi; i++) pages.push(i);
    if (current < total - 2) pages.push('...');
    pages.push(total);
  }

  const btn =
    'flex items-center justify-center w-8 h-8 rounded-xl text-sm font-medium transition-all duration-150';

  return (
    <div className="flex items-center gap-1.5">
      <button
        onClick={() => onChange(current - 1)}
        disabled={current === 1}
        className={cn(btn, 'border border-charcoal/10 text-zinc-400 disabled:opacity-25 hover:border-white/20 hover:text-white')}
        aria-label="Previous page"
      >
        <ChevronLeft className="w-4 h-4" />
      </button>

      {pages.map((p, i) =>
        p === '...' ? (
          <span key={`e${i}`} className="w-8 text-center text-zinc-600 text-sm select-none">…</span>
        ) : (
          <button
            key={p}
            onClick={() => onChange(p as number)}
            className={cn(
              btn,
              p === current
                ? 'bg-indigo-600/20 border border-indigo-500/50 text-indigo-300'
                : 'border border-charcoal/10 text-zinc-400 hover:border-white/20 hover:text-white',
            )}
          >
            {p}
          </button>
        ),
      )}

      <button
        onClick={() => onChange(current + 1)}
        disabled={current === total}
        className={cn(btn, 'border border-charcoal/10 text-zinc-400 disabled:opacity-25 hover:border-white/20 hover:text-white')}
        aria-label="Next page"
      >
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  );
}

// ── Algorithm card ─────────────────────────────────────────────────────────────

function AlgorithmCard({
  algorithm: alg,
  onTagClick,
}: {
  algorithm: AlgorithmSummary;
  onTagClick: (tag: string) => void;
}) {
  const [hovered, setHovered] = useState(false);
  const categoryColor = CATEGORY_COLORS[alg.category] ?? '#6B7280';
  const badgeStyle = COMPLEXITY_BADGE_STYLES[alg.complexity.time_average] ?? DEFAULT_BADGE_STYLE;

  return (
    <motion.div
      whileHover={{ y: -3 }}
      transition={{ duration: 0.18, ease: 'easeOut' }}
      className="h-full"
    >
      <Link
        to={`/algorithms/${alg.slug}`}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        className="group flex flex-col rounded-2xl h-full overflow-hidden cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-all duration-300"
        style={{
          background: '#0D0D11',
          boxShadow: hovered
            ? `0 0 0 1px ${categoryColor}35, 0 12px 40px ${categoryColor}14`
            : '0 0 0 1px rgba(255,255,255,0.045)',
        }}
      >
        {/* Colored accent strip at top */}
        <div
          className="h-[3px] w-full flex-shrink-0 transition-opacity duration-300"
          style={{
            background: `linear-gradient(90deg, ${categoryColor}, ${categoryColor}70, transparent)`,
            opacity: hovered ? 1 : 0.7,
          }}
        />

        {/* Card body */}
        <div className="flex flex-col gap-3 p-5 flex-1">
          {/* Category label + WASM badge */}
          <div className="flex items-center justify-between gap-2">
            <span
              className="text-[11px] font-medium capitalize truncate"
              style={{ color: `${categoryColor}bb` }}
            >
              {alg.category.replace(/-/g, ' ')}
            </span>
            {(alg.execution_target === 'wasm' || alg.execution_target === 'both') && (
              <span className="shrink-0 flex items-center gap-1 px-1.5 py-0.5 rounded-md text-[10px] font-medium bg-emerald-500/10 border border-emerald-500/25 text-emerald-400">
                <Zap className="w-2.5 h-2.5" />
                WASM
              </span>
            )}
          </div>

          {/* Algorithm name */}
          <h3 className="text-[15px] font-semibold text-white leading-snug">
            {alg.name}
          </h3>

          {/* Description — shown in card */}
          {alg.description && (
            <p className="text-xs text-zinc-500 leading-relaxed line-clamp-2">
              {alg.description}
            </p>
          )}

          {/* Bottom: complexity + tags */}
          <div className="flex items-center justify-between gap-2 mt-auto pt-1">
            <span
              className="text-xs font-mono rounded-lg px-2 py-0.5"
              style={{
                color: badgeStyle.color,
                backgroundColor: badgeStyle.bg,
                boxShadow: `inset 0 0 0 1px ${badgeStyle.ring}`,
              }}
            >
              {alg.complexity.time_average}
            </span>
            <div className="flex flex-wrap gap-1">
              {alg.tags.slice(0, 2).map((tag) => (
                <span
                  key={tag}
                  role="button"
                  tabIndex={0}
                  onClick={(e) => { e.preventDefault(); onTagClick(tag); }}
                  onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); onTagClick(tag); } }}
                  className="px-1.5 py-0.5 rounded-md text-[10px] text-zinc-600 hover:text-indigo-300 hover:bg-indigo-900/30 transition-colors cursor-pointer"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}
