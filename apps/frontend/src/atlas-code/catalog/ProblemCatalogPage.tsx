import { useEffect, useState, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, Filter, CheckCircle2, Clock, ChevronLeft, ChevronRight } from 'lucide-react';
import { listProblems, listProblemsPage, getProgress } from '../api/problems';
import type { ProblemSummary, ProgressOut } from '../api/problems';
import { useAtlasCodeStore } from '../store/atlasCodeStore';
import { cn } from '../../lib/utils';
import { TARGET_LANGUAGES_TOTAL, languageLabel } from '../languages';

const PAGE_SIZE = 25;

const DIFFICULTIES = ['All', 'Easy', 'Medium', 'Hard'] as const;
const DIFFICULTY_COLOR: Record<string, string> = {
  Easy: 'text-emerald-400',
  Medium: 'text-amber-400',
  Hard: 'text-rose-400',
};
const DIFFICULTY_BG: Record<string, string> = {
  Easy: 'bg-emerald-500/10 border-emerald-500/20',
  Medium: 'bg-amber-500/10 border-amber-500/20',
  Hard: 'bg-rose-500/10 border-rose-500/20',
};

// Problem Completion (headline) + Language Coverage (secondary), per the
// 2026-07-12 completion redefinition -- see docs/atlascode-complete-matrix.md.
// A problem is Complete once it has >=1 verified language in EITHER mode;
// the LC/CF pills below show how many of the 17 target languages are
// verified per mode -- an ongoing enhancement, never a completion blocker.
function CompletionDot({ isComplete }: { isComplete: boolean }) {
  return (
    <span
      title={
        isComplete
          ? 'Problem Complete — canonical implementation, working judge, and a verified reference solution.'
          : 'In Progress — this problem is not yet fully usable in the judge.'
      }
      className={cn(
        'inline-block w-1.5 h-1.5 rounded-full flex-shrink-0',
        isComplete ? 'bg-emerald-400' : 'bg-amber-400',
      )}
    />
  );
}

function LanguagePill({
  label,
  languages,
  colorClass,
}: {
  label: string;
  languages: string[];
  colorClass: string;
}) {
  const tooltip = languages.length > 0
    ? `${label} verified in: ${languages.map(languageLabel).join(', ')}`
    : `${label}: no verified languages yet`;
  return (
    <span
      title={tooltip}
      className={cn(
        'text-[11px] font-medium px-1.5 py-0.5 rounded-md border tabular-nums',
        languages.length > 0 ? colorClass : 'text-zinc-700 border-zinc-800 bg-transparent',
      )}
    >
      {label} {languages.length}/{TARGET_LANGUAGES_TOTAL}
    </span>
  );
}

function ProblemRow({
  problem,
  solved,
  attempted,
}: {
  problem: ProblemSummary;
  solved: boolean;
  attempted: boolean;
}) {
  return (
    <Link
      to={`/atlas-code/problem/${problem.id}`}
      className="flex items-center gap-4 px-4 py-3 rounded-xl hover:bg-white/5 transition-colors group"
    >
      <div className="w-5 flex-shrink-0">
        {solved ? (
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
        ) : attempted ? (
          <div className="w-4 h-4 rounded-full border-2 border-amber-400/50" />
        ) : (
          <div className="w-4 h-4 rounded-full border border-zinc-700" />
        )}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5">
          <CompletionDot isComplete={problem.is_complete} />
          <span className="text-sm font-medium text-white group-hover:text-indigo-300 transition-colors truncate block">
            {problem.title}
          </span>
        </div>
        <span className="text-xs text-zinc-600 capitalize">{problem.category.replace(/-/g, ' ')}</span>
      </div>

      <div className="flex items-center gap-2 flex-shrink-0 hidden lg:flex">
        <LanguagePill label="LeetCode" languages={problem.leetcode_languages} colorClass="text-indigo-300 border-indigo-500/25 bg-indigo-500/10" />
        <LanguagePill label="Codeforces" languages={problem.codeforces_languages} colorClass="text-teal-300 border-teal-500/25 bg-teal-500/10" />
      </div>

      <div className="flex items-center gap-4 flex-shrink-0">
        <span
          className={cn(
            'text-xs font-medium px-2 py-0.5 rounded-full border',
            DIFFICULTY_BG[problem.difficulty],
            DIFFICULTY_COLOR[problem.difficulty],
          )}
        >
          {problem.difficulty}
        </span>

        {problem.companies.length > 0 && (
          <span className="text-xs text-zinc-600 hidden sm:block">
            {problem.companies.slice(0, 2).join(', ')}
          </span>
        )}

        <div className="flex items-center gap-1 text-xs text-zinc-600 hidden md:flex">
          <Clock className="w-3 h-3" />
          {problem.estimated_minutes}m
        </div>

        <span className="text-xs text-zinc-600 w-12 text-right hidden md:block">
          {problem.acceptance_rate.toFixed(0)}%
        </span>
      </div>
    </Link>
  );
}

export function ProblemCatalogPage() {
  const { selectedDifficulty, selectedCategory, searchQuery, setDifficulty, setCategory, setSearch } =
    useAtlasCodeStore();

  const [problems, setProblems] = useState<ProblemSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [categories, setCategories] = useState<string[]>([]);
  const [progress, setProgress] = useState<ProgressOut | null>(null);
  const [loading, setLoading] = useState(true);

  // Category list fetched once (unfiltered, uncapped) purely to populate the
  // filter dropdown -- separate from the paginated/filtered page fetch below,
  // which is what keeps 216+ problems from all loading on every render.
  useEffect(() => {
    listProblems({ limit: 1000 }).then((all) => {
      setCategories(['all', ...Array.from(new Set(all.map((p) => p.category))).sort()]);
    }).catch(() => {});
    getProgress('anonymous').then(setProgress).catch(() => {});
  }, []);

  // Reset to page 0 whenever a filter changes (a stale page number past the
  // new filtered result count would just show an empty page).
  const filterKey = `${selectedDifficulty}|${selectedCategory}|${searchQuery}`;
  const prevFilterKey = useRef(filterKey);
  useEffect(() => {
    if (prevFilterKey.current !== filterKey) {
      prevFilterKey.current = filterKey;
      setPage(0);
    }
  }, [filterKey]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { items, total: t } = await listProblemsPage({
        category: selectedCategory !== 'all' ? selectedCategory : undefined,
        difficulty: selectedDifficulty !== 'All' ? selectedDifficulty : undefined,
        search: searchQuery || undefined,
        limit: PAGE_SIZE,
        offset: page * PAGE_SIZE,
      });
      setProblems(items);
      setTotal(t);
    } finally {
      setLoading(false);
    }
  }, [selectedCategory, selectedDifficulty, searchQuery, page]);

  useEffect(() => { load(); }, [load]);

  const solved = new Set(progress?.solved_problems ?? []);
  const attempted = new Set(progress?.attempted_problems ?? []);
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="min-h-screen pt-20 px-4 pb-16">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-1">Problem Catalog</h1>
          <p className="text-zinc-500 text-sm">
            {total} problems · {solved.size} solved · {attempted.size - solved.size} attempted
          </p>
          <p className="text-zinc-600 text-xs mt-1 flex items-center gap-1.5">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400" />
            A problem is Complete once it has a working judge and one verified language — LeetCode/Codeforces pills show per-problem language coverage, a separate, ongoing metric.
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-3 mb-6">
          {/* Search */}
          <div className="relative flex-1 min-w-52">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <input
              value={searchQuery}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search problems…"
              className="w-full bg-white/5 border border-charcoal/10 rounded-xl pl-9 pr-4 py-2 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-indigo-500/50"
            />
          </div>

          {/* Difficulty pills */}
          <div className="flex gap-1.5 bg-white/5 border border-charcoal/10 rounded-xl p-1">
            {DIFFICULTIES.map((d) => (
              <button
                key={d}
                onClick={() => setDifficulty(d)}
                className={cn(
                  'px-3 py-1 rounded-lg text-xs font-medium transition-colors',
                  selectedDifficulty === d
                    ? 'bg-white/15 text-white'
                    : 'text-zinc-500 hover:text-zinc-300',
                )}
              >
                {d}
              </button>
            ))}
          </div>

          {/* Category */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-500 pointer-events-none" />
            <select
              value={selectedCategory}
              onChange={(e) => setCategory(e.target.value)}
              className="bg-white/5 border border-charcoal/10 rounded-xl pl-8 pr-4 py-2 text-sm text-white appearance-none focus:outline-none focus:border-indigo-500/50 cursor-pointer"
            >
              {categories.map((c) => (
                <option key={c} value={c} className="bg-[#09090B]">
                  {c === 'all' ? 'All Categories' : c.replace(/-/g, ' ')}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Table header */}
        <div className="flex items-center gap-4 px-4 pb-2 border-b border-charcoal/10 text-xs text-zinc-600 font-medium">
          <div className="w-5 flex-shrink-0" />
          <div className="flex-1">Problem</div>
          <div className="flex items-center gap-4 flex-shrink-0">
            <span className="w-16 text-center">Difficulty</span>
            <span className="hidden sm:block w-24">Companies</span>
            <span className="hidden md:block w-12 text-right">Time</span>
            <span className="hidden md:block w-12 text-right">Accept</span>
          </div>
        </div>

        {/* Problem list */}
        {loading ? (
          <div className="text-center py-16 text-zinc-500">Loading problems…</div>
        ) : problems.length === 0 ? (
          <div className="text-center py-16 text-zinc-500">No problems match your filters.</div>
        ) : (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="divide-y divide-white/4">
            {problems.map((p) => (
              <ProblemRow
                key={p.id}
                problem={p}
                solved={solved.has(p.id)}
                attempted={attempted.has(p.id)}
              />
            ))}
          </motion.div>
        )}

        {/* Pagination */}
        {!loading && total > PAGE_SIZE && (
          <div className="flex items-center justify-between pt-6 mt-2 border-t border-charcoal/10">
            <span className="text-xs text-zinc-500">
              Page {page + 1} of {totalPages} · showing {problems.length} of {total}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className="flex items-center gap-1 text-sm text-zinc-400 hover:text-white disabled:opacity-40 disabled:hover:text-zinc-400 px-3 py-1.5 rounded-lg hover:bg-white/5 transition-colors"
              >
                <ChevronLeft className="w-4 h-4" /> Prev
              </button>
              <button
                onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                disabled={page >= totalPages - 1}
                className="flex items-center gap-1 text-sm text-zinc-400 hover:text-white disabled:opacity-40 disabled:hover:text-zinc-400 px-3 py-1.5 rounded-lg hover:bg-white/5 transition-colors"
              >
                Next <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
