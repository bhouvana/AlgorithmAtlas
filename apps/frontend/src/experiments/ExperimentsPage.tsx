/**
 * ExperimentsPage — browse, view, and manage saved experiments.
 *
 * Route: /experiments
 *
 * Features:
 * - List all experiments (paginated)
 * - Filter by algorithm slug
 * - View experiment detail (cells + outputs)
 * - Rename, delete experiments
 * - Link back to algorithm detail page
 */

import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FlaskConical,
  Eye,
  Trash2,
  Search,
  X,
  ChevronLeft,
  Plus,
  ChevronDown,
} from 'lucide-react';
import { api, type ExperimentSummary, type ExperimentDetail, type NotebookCellData } from '../core/api/client';
import { cn } from '../lib/utils';

// ── Helpers ────────────────────────────────────────────────────────────────────

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

// ── Experiment card ─────────────────────────────────────────────────────────────

function ExperimentCard({
  exp,
  onSelect,
  onDelete,
}: {
  exp: ExperimentSummary;
  onSelect: () => void;
  onDelete: () => void;
}) {
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm(`Delete "${exp.name}"?`)) return;
    setDeleting(true);
    try {
      await api.experiments.delete(exp.id);
      onDelete();
    } catch {
      setDeleting(false);
    }
  };

  return (
    <motion.div
      whileHover={{ y: -3 }}
      transition={{ duration: 0.2 }}
      onClick={onSelect}
      className="bg-[#18181B] border border-white/8 rounded-2xl p-5 flex flex-col gap-3 hover:border-white/15 cursor-pointer transition-colors"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-white font-semibold text-sm leading-snug">{exp.name}</h3>
        <span className="text-xs text-zinc-500 font-mono shrink-0">{formatDate(exp.created_at)}</span>
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        <Link
          to={`/algorithms/${exp.algorithm_slug}`}
          onClick={(e) => e.stopPropagation()}
          className="text-xs px-2 py-0.5 rounded-lg bg-indigo-500/15 border border-indigo-500/25 text-indigo-300 hover:bg-indigo-500/25 transition-colors"
        >
          {exp.algorithm_slug}
        </Link>
        <span className="text-xs text-zinc-600">{exp.cell_count} cells</span>
        {exp.seed !== undefined && (
          <>
            <span className="text-xs text-zinc-700">·</span>
            <span className="text-xs text-zinc-600 font-mono">seed={exp.seed}</span>
          </>
        )}
      </div>

      {exp.notes && (
        <p className="text-zinc-500 text-xs line-clamp-2">{exp.notes}</p>
      )}

      <div className="flex items-center gap-2 mt-auto pt-2 border-t border-white/5">
        <button
          onClick={(e) => { e.stopPropagation(); onSelect(); }}
          className="flex items-center gap-1 text-xs text-zinc-500 hover:text-white transition-colors"
        >
          <Eye className="w-3.5 h-3.5" /> View
        </button>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="flex items-center gap-1 text-xs text-zinc-500 hover:text-red-400 transition-colors ml-auto disabled:opacity-50"
        >
          <Trash2 className="w-3.5 h-3.5" />
          {deleting ? 'Deleting…' : 'Delete'}
        </button>
      </div>
    </motion.div>
  );
}

// ── Cell view (in detail panel) ────────────────────────────────────────────────

function CellView({ cell, index }: { cell: NotebookCellData; index: number }) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="rounded-xl border border-white/8 bg-[#18181B] overflow-hidden">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-white/3 transition-colors text-left"
      >
        <span className="text-xs font-mono text-indigo-400 w-6">[{index + 1}]</span>
        <span className="text-xs font-mono text-zinc-400 truncate flex-1">
          {cell.source.split('\n')[0].slice(0, 80)}
        </span>
        {cell.executed_at && (
          <span className="text-[10px] text-zinc-600 shrink-0">
            {new Date(cell.executed_at).toLocaleTimeString()}
          </span>
        )}
        <ChevronDown className={cn('w-3.5 h-3.5 text-zinc-600 transition-transform shrink-0', expanded && 'rotate-180')} />
      </button>

      {expanded && (
        <div className="border-t border-white/8">
          <pre className="px-4 py-3 text-xs font-mono text-zinc-200 whitespace-pre-wrap overflow-x-auto leading-relaxed bg-[#0D0D0F]">
            {cell.source || '# empty cell'}
          </pre>
          {(cell.output || cell.error) && (
            <div className={cn(
              'border-t border-white/8 px-4 py-3',
              cell.error ? 'bg-red-500/5' : 'bg-emerald-500/5',
            )}>
              {cell.error ? (
                <pre className="text-xs font-mono text-red-400 whitespace-pre-wrap">{cell.error}</pre>
              ) : (
                <pre className="text-xs font-mono text-emerald-300 whitespace-pre-wrap">{cell.output}</pre>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Detail slide-in panel ──────────────────────────────────────────────────────

function ExperimentDetailPanel({
  id,
  onClose,
  onDeleted,
}: {
  id: string;
  onClose: () => void;
  onDeleted: () => void;
}) {
  const [detail, setDetail] = useState<ExperimentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState('');

  useEffect(() => {
    api.experiments.get(id)
      .then((d) => { setDetail(d); setName(d.name); })
      .catch(() => {/* noop */})
      .finally(() => setLoading(false));
  }, [id]);

  const saveName = async () => {
    if (!detail || !name.trim()) return;
    const updated = await api.experiments.update(id, { name });
    setDetail((d) => d ? { ...d, name: updated.name } : d);
    setEditing(false);
  };

  const handleDelete = async () => {
    if (!confirm(`Delete "${detail?.name}"?`)) return;
    await api.experiments.delete(id);
    onDeleted();
  };

  return (
    <>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
      />

      {/* Slide-in panel */}
      <motion.div
        initial={{ x: '100%' }}
        animate={{ x: 0 }}
        exit={{ x: '100%' }}
        transition={{ type: 'spring', damping: 30, stiffness: 300 }}
        className="fixed right-0 top-0 bottom-0 w-[480px] z-50 bg-[#111113] border-l border-white/10 shadow-[-24px_0_64px_rgba(0,0,0,0.5)] overflow-y-auto"
      >
        {/* Panel header */}
        <div className="sticky top-0 bg-[#111113] border-b border-white/8 px-6 py-4 flex items-center gap-3">
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-white/5 text-zinc-500 hover:text-white transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <div className="flex-1 min-w-0">
            {editing ? (
              <div className="flex items-center gap-2">
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="bg-[#18181B] border border-white/8 rounded-xl px-3 py-1.5 text-sm text-white outline-none focus:border-indigo-500/50 flex-1"
                  autoFocus
                  onKeyDown={(e) => e.key === 'Enter' && saveName()}
                />
                <button onClick={saveName} className="text-xs px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl">Save</button>
                <button onClick={() => setEditing(false)} className="text-xs px-2 py-1.5 text-zinc-400 hover:text-white">Cancel</button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white truncate">
                  {loading ? 'Loading…' : (detail?.name ?? 'Experiment')}
                </h2>
                {detail && (
                  <button
                    onClick={() => setEditing(true)}
                    className="text-xs text-zinc-600 hover:text-zinc-300 transition-colors"
                  >
                    ✎
                  </button>
                )}
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-white/5 text-zinc-500 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Panel body */}
        <div className="p-6">
          {loading && (
            <div className="flex items-center justify-center py-16 text-zinc-500 text-sm">
              Loading…
            </div>
          )}

          {!loading && !detail && (
            <div className="flex items-center justify-center py-16 text-red-400 text-sm">
              Experiment not found.
            </div>
          )}

          {detail && (
            <>
              {/* Metadata badges */}
              <div className="flex flex-wrap gap-2 mb-5">
                <Link
                  to={`/algorithms/${detail.algorithm_slug}`}
                  className="px-2.5 py-1 rounded-lg bg-indigo-500/15 border border-indigo-500/25 text-indigo-300 text-xs font-mono hover:bg-indigo-500/25 transition-colors"
                >
                  {detail.algorithm_slug}
                </Link>
                <span className="px-2.5 py-1 rounded-lg bg-white/5 text-zinc-400 text-xs font-mono">
                  seed={detail.seed}
                </span>
                <span className="px-2.5 py-1 rounded-lg bg-white/5 text-zinc-400 text-xs">
                  {detail.cells.length} cells
                </span>
                <span className="px-2.5 py-1 rounded-lg bg-white/5 text-zinc-500 text-xs">
                  {new Date(detail.created_at).toLocaleString()}
                </span>
              </div>

              {detail.notes && (
                <div className="mb-5 p-3.5 rounded-xl bg-white/3 border border-white/8">
                  <p className="text-sm text-zinc-400">{detail.notes}</p>
                </div>
              )}

              {detail.params && Object.keys(detail.params).length > 0 && (
                <div className="mb-5 p-3.5 rounded-xl bg-white/3 border border-white/8">
                  <p className="text-xs text-zinc-600 mb-1.5">Parameters</p>
                  <pre className="text-xs font-mono text-zinc-300">
                    {JSON.stringify(detail.params, null, 2)}
                  </pre>
                </div>
              )}

              {/* Action buttons */}
              <div className="flex items-center gap-2 mb-6">
                <Link
                  to="/notebook"
                  className="flex items-center gap-1.5 text-xs px-3 py-2 bg-indigo-600/20 hover:bg-indigo-600/40 border border-indigo-500/25 text-indigo-300 rounded-xl transition-colors"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Open in Notebook
                </Link>
                <button
                  onClick={handleDelete}
                  className="flex items-center gap-1.5 text-xs px-3 py-2 text-zinc-500 hover:text-red-400 border border-white/8 hover:border-red-500/30 rounded-xl transition-colors ml-auto"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  Delete
                </button>
              </div>

              {/* Cells */}
              <div className="flex flex-col gap-3">
                {detail.cells
                  .sort((a, b) => a.order - b.order)
                  .map((cell, i) => (
                    <CellView key={cell.id} cell={cell} index={i} />
                  ))}
                {detail.cells.length === 0 && (
                  <p className="text-sm text-zinc-500 py-8 text-center">No cells saved.</p>
                )}
              </div>
            </>
          )}
        </div>
      </motion.div>
    </>
  );
}

// ── Main page ───────────────────────────────────────────────────────────────────

export function ExperimentsPage() {
  const [experiments, setExperiments] = useState<ExperimentSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const PER_PAGE = 20;

  const load = useCallback(() => {
    setLoading(true);
    api.experiments.list({ limit: PER_PAGE, offset: page * PER_PAGE })
      .then((r) => { setExperiments(r.items); setTotal(r.total); })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [page]);

  useEffect(() => { load(); }, [load]);

  const filtered = search
    ? experiments.filter(
        (e) =>
          e.name.toLowerCase().includes(search.toLowerCase()) ||
          e.algorithm_slug.includes(search.toLowerCase()),
      )
    : experiments;

  return (
    <div className="min-h-screen">
      {/* Page header */}
      <div className="max-w-6xl mx-auto px-6 pt-10 pb-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <FlaskConical className="w-7 h-7 text-indigo-400" />
              <h1 className="text-3xl font-bold text-white">Experiments</h1>
            </div>
            <p className="text-zinc-500 text-sm">
              {total > 0
                ? `${total} saved experiment${total !== 1 ? 's' : ''}`
                : 'Saved algorithm experiments and notebook runs'}
            </p>
          </div>
          <Link
            to="/notebook"
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm transition-colors mt-1"
          >
            <Plus className="w-3.5 h-3.5" />
            New notebook
          </Link>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6">
        {/* Search bar */}
        <div className="relative mb-6">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-600" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name or algorithm…"
            className="w-full bg-[#111113] border border-white/8 rounded-2xl pl-11 pr-4 py-3 text-sm text-white placeholder:text-zinc-600 outline-none focus:border-indigo-500/40 transition-colors"
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              className="absolute right-4 top-1/2 -translate-y-1/2 p-0.5 rounded text-zinc-600 hover:text-white transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-900/20 border border-red-500/20 text-red-400 text-sm">
            {error} — is the backend running?
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-16 text-zinc-500 text-sm">
            <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mr-3" />
            Loading…
          </div>
        )}

        {/* Empty state */}
        {!loading && filtered.length === 0 && (
          <div className="flex flex-col items-center justify-center h-64 gap-4 text-center">
            <FlaskConical className="w-12 h-12 text-zinc-700" />
            <p className="text-zinc-400 font-medium">No experiments yet</p>
            <p className="text-zinc-600 text-sm">
              {search ? 'No experiments match your search.' : 'Run code in the Notebook to save experiments'}
            </p>
            {!search && (
              <Link
                to="/notebook"
                className="px-4 py-2 rounded-xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-300 text-sm hover:bg-indigo-600/30 transition-colors"
              >
                Open Notebook →
              </Link>
            )}
          </div>
        )}

        {/* Experiment grid */}
        {!loading && filtered.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((exp) => (
              <ExperimentCard
                key={exp.id}
                exp={exp}
                onSelect={() => setSelectedId(exp.id)}
                onDelete={load}
              />
            ))}
          </div>
        )}

        {/* Pagination */}
        {total > PER_PAGE && (
          <div className="flex items-center justify-center gap-3 mt-8 pb-8">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-4 py-2 text-sm text-zinc-400 hover:text-white disabled:opacity-30 bg-[#18181B] border border-white/8 rounded-xl transition-colors"
            >
              ← Prev
            </button>
            <span className="text-sm text-zinc-500 font-mono">
              {page + 1} / {Math.ceil(total / PER_PAGE)}
            </span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={(page + 1) * PER_PAGE >= total}
              className="px-4 py-2 text-sm text-zinc-400 hover:text-white disabled:opacity-30 bg-[#18181B] border border-white/8 rounded-xl transition-colors"
            >
              Next →
            </button>
          </div>
        )}
      </div>

      {/* Detail slide-in */}
      <AnimatePresence>
        {selectedId && (
          <ExperimentDetailPanel
            key={selectedId}
            id={selectedId}
            onClose={() => setSelectedId(null)}
            onDeleted={() => { setSelectedId(null); load(); }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
