import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, BookOpen, Clock, CheckCircle2, Zap, Trophy, ChevronRight } from 'lucide-react';
import { MODULES, TRACKS, type Difficulty, type Track, type Module } from './data/curriculum';
import { useProgressStore, useCompletionStats, xpProgressPercent, xpForNextLevel } from './store/progressStore';

// ── Hero stat card ──────────────────────────────────────────────────────────
function StatCard({ icon, label, value, accent }: { icon: React.ReactNode; label: string; value: string | number; accent: string }) {
  return (
    <div className={`rounded-2xl border border-charcoal/10 bg-zinc-900/40 p-4 flex items-center gap-3`}>
      <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${accent}`}>{icon}</div>
      <div>
        <div className="text-xl font-bold text-white leading-none">{value}</div>
        <div className="text-xs text-zinc-500 mt-0.5">{label}</div>
      </div>
    </div>
  );
}

// ── XP Progress bar ─────────────────────────────────────────────────────────
function XPSection() {
  const { xp, level, done } = useCompletionStats();
  const pct = xpProgressPercent(xp);
  const remaining = xpForNextLevel(xp);
  const nextLevel = level + 1;

  return (
    <div className="rounded-2xl border border-charcoal/10 bg-gradient-to-br from-indigo-500/10 to-violet-500/5 p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center">
            <Zap size={14} className="text-indigo-400" />
          </div>
          <div>
            <span className="text-white font-bold text-sm">Level {level}</span>
            <span className="text-zinc-500 text-xs ml-2">Algorithm Scholar</span>
          </div>
        </div>
        <span className="text-xs text-zinc-400">{xp} XP total</span>
      </div>
      <div className="flex items-center gap-2">
        <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full"
            animate={{ width: `${pct}%` }}
            transition={{ duration: 1, ease: 'easeOut' }}
          />
        </div>
        <span className="text-xs text-zinc-500 whitespace-nowrap">{remaining} XP → Lv {nextLevel}</span>
      </div>
      <div className="mt-3 flex gap-3 text-xs text-zinc-400">
        <span><span className="text-white font-semibold">{done}</span> lessons completed</span>
        <span>·</span>
        <span><span className="text-white font-semibold">{MODULES.length - done}</span> remaining</span>
      </div>
    </div>
  );
}

// ── Module card ─────────────────────────────────────────────────────────────
function ModuleCard({ module, isDone, isStarted }: {
  module: Module;
  isDone: boolean;
  isStarted: boolean;
}) {
  const diffColor =
    module.difficulty === 'beginner'     ? 'text-emerald-400 bg-emerald-500/10' :
    module.difficulty === 'intermediate' ? 'text-amber-400 bg-amber-500/10' :
                                           'text-rose-400 bg-rose-500/10';

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`group relative rounded-2xl border bg-zinc-900/50 p-4 transition-all duration-200 ${
        isDone
          ? 'border-emerald-500/20 hover:border-emerald-500/30 cursor-pointer'
          : 'border-charcoal/10 hover:border-white/16 cursor-pointer'
      }`}
    >
      {/* Top row */}
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="flex items-center gap-2.5">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-lg bg-gradient-to-br ${module.accent} border border-charcoal/10`}>
            {module.icon}
          </div>
          <div>
            <div className="font-semibold text-white text-sm leading-tight">{module.title}</div>
            <div className={`text-[10px] px-1.5 py-0.5 rounded font-medium mt-0.5 inline-block ${diffColor}`}>
              {module.difficulty}
            </div>
          </div>
        </div>

        {isDone ? (
          <CheckCircle2 size={14} className="text-emerald-400 flex-shrink-0 mt-1" />
        ) : isStarted ? (
          <div className="w-2.5 h-2.5 rounded-full bg-indigo-400 flex-shrink-0 mt-2 animate-pulse" />
        ) : null}
      </div>

      <p className="text-zinc-400 text-xs leading-relaxed mb-3 line-clamp-2">{module.description}</p>

      {/* Footer */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-xs text-zinc-500">
          <Clock size={10} />
          <span>{module.estimatedMinutes}m</span>
          {module.timeComplexity && (
            <>
              <span>·</span>
              <code className="font-mono text-zinc-400">{module.timeComplexity.split(',')[0]}</code>
            </>
          )}
        </div>
        {(
          <span className={`text-[10px] font-medium ${isDone ? 'text-emerald-400' : 'text-indigo-400'} group-hover:translate-x-0.5 transition-transform`}>
            {isDone ? 'Review' : isStarted ? 'Continue' : 'Start'} →
          </span>
        )}
      </div>

      {/* Not yet available overlay for modules without full lessons */}
      {!module.hasFullLesson && (
        <div className="absolute top-2 right-2">
          <span className="text-[9px] font-mono text-zinc-600 bg-zinc-800/60 px-1.5 py-0.5 rounded border border-charcoal/10">soon</span>
        </div>
      )}
    </motion.div>
  );
}

const DIFFICULTY_OPTIONS: { value: Difficulty | 'all'; label: string }[] = [
  { value: 'all',           label: 'All Levels' },
  { value: 'beginner',      label: 'Beginner' },
  { value: 'intermediate',  label: 'Intermediate' },
  { value: 'advanced',      label: 'Advanced' },
];

export function LearningPage() {
  const [search, setSearch] = useState('');
  const [diffFilter, setDiffFilter] = useState<Difficulty | 'all'>('all');
  const [activeTrack, setActiveTrack] = useState<Track | 'all'>('all');

  const { lessons } = useProgressStore();
  const { done } = useCompletionStats();

  const completedIds = useMemo(() => new Set(Object.entries(lessons).filter(([, l]) => l.completedAt).map(([id]) => id)), [lessons]);
  const startedIds   = useMemo(() => new Set(Object.keys(lessons)), [lessons]);


  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return MODULES.filter((m) => {
      if (diffFilter !== 'all' && m.difficulty !== diffFilter) return false;
      if (activeTrack !== 'all' && m.track !== activeTrack) return false;
      if (q && !m.title.toLowerCase().includes(q) && !m.description.toLowerCase().includes(q) && !m.tags.some((t) => t.includes(q))) return false;
      return true;
    });
  }, [search, diffFilter, activeTrack]);

  const byTrack = useMemo(() => {
    const result: Record<string, Module[]> = {};
    for (const m of filtered) {
      if (!result[m.track]) result[m.track] = [];
      result[m.track].push(m);
    }
    return result;
  }, [filtered]);

  const visibleTracks = activeTrack === 'all'
    ? TRACKS.filter((t) => byTrack[t.id]?.length)
    : TRACKS.filter((t) => t.id === activeTrack && byTrack[t.id]?.length);

  return (
    <div className="max-w-5xl mx-auto px-4 py-10 space-y-10">

      {/* ── Page header ──────────────────────────────────────────────────── */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <BookOpen size={14} className="text-indigo-400" />
          <span className="text-xs font-mono text-indigo-400 uppercase tracking-widest">Learning</span>
        </div>
        <h1 className="text-3xl font-bold text-white mb-2">Algorithm Atlas</h1>
        <p className="text-zinc-400 text-base">
          Master data structures & algorithms through interactive lessons, live visualizations, and hands-on challenges.
        </p>
      </div>

      {/* ── Progress section ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="col-span-2 sm:col-span-4">
          <XPSection />
        </div>
        <StatCard icon={<CheckCircle2 size={16} className="text-emerald-400" />} label="Lessons done" value={done} accent="bg-emerald-500/10" />
        <StatCard icon={<BookOpen size={16} className="text-indigo-400" />} label="Total modules" value={MODULES.length} accent="bg-indigo-500/10" />
        <StatCard icon={<Trophy size={16} className="text-amber-400" />} label="Achievements" value={useProgressStore.getState().achievements.length} accent="bg-amber-500/10" />
        <StatCard icon={<Zap size={16} className="text-violet-400" />} label="Tracks" value={TRACKS.length} accent="bg-violet-500/10" />
      </div>

      {/* ── Search & Filters ─────────────────────────────────────────────── */}
      <div className="space-y-3">
        {/* Search */}
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
          <input
            type="text"
            placeholder="Search algorithms, topics…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 bg-zinc-900/60 border border-charcoal/10 rounded-xl text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-indigo-500/50 transition-colors"
          />
        </div>

        {/* Track pills */}
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setActiveTrack('all')}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all border ${
              activeTrack === 'all'
                ? 'bg-white/10 border-charcoal/10 text-white'
                : 'border-charcoal/10 text-zinc-500 hover:text-zinc-300 hover:border-white/12'
            }`}
          >
            All Tracks
          </button>
          {TRACKS.map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTrack(activeTrack === t.id ? 'all' : t.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all border ${
                activeTrack === t.id
                  ? 'bg-white/10 border-charcoal/10 text-white'
                  : 'border-charcoal/10 text-zinc-500 hover:text-zinc-300 hover:border-white/12'
              }`}
            >
              {t.icon} {t.label}
            </button>
          ))}
        </div>

        {/* Difficulty pills */}
        <div className="flex gap-2 flex-wrap">
          {DIFFICULTY_OPTIONS.map((d) => (
            <button
              key={d.value}
              onClick={() => setDiffFilter(d.value)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all border ${
                diffFilter === d.value
                  ? d.value === 'beginner'     ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
                  : d.value === 'intermediate' ? 'bg-amber-500/20 border-amber-500/40 text-amber-300'
                  : d.value === 'advanced'     ? 'bg-rose-500/20 border-rose-500/40 text-rose-300'
                  :                              'bg-white/10 border-charcoal/10 text-white'
                  : 'border-charcoal/10 text-zinc-500 hover:text-zinc-300 hover:border-white/12'
              }`}
            >
              {d.label}
            </button>
          ))}
        </div>

        {filtered.length === 0 && (
          <p className="text-zinc-500 text-sm text-center py-8">No modules match your filters.</p>
        )}
      </div>

      {/* ── Tracks & Modules ─────────────────────────────────────────────── */}
      {visibleTracks.map((track) => {
        const mods = byTrack[track.id] ?? [];
        const trackDone = mods.filter((m) => completedIds.has(m.id)).length;
        const trackPct = Math.round((trackDone / mods.length) * 100);

        return (
          <section key={track.id}>
            {/* Track header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2.5">
                <span className="text-xl">{track.icon}</span>
                <h2 className={`text-lg font-bold ${track.color}`}>{track.label}</h2>
                <span className="text-xs text-zinc-600 font-mono">{mods.length} modules</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-20 h-1.5 bg-zinc-800 rounded-full overflow-hidden hidden sm:block">
                  <motion.div
                    className="h-full bg-indigo-500 rounded-full"
                    animate={{ width: `${trackPct}%` }}
                    transition={{ duration: 0.8 }}
                  />
                </div>
                <span className="text-xs text-zinc-500">{trackDone}/{mods.length}</span>
              </div>
            </div>

            {/* Module grid */}
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {mods.map((mod) => {
                const done2 = completedIds.has(mod.id);
                const started = startedIds.has(mod.id) && !done2;

                return (
                  <Link key={mod.id} to={`/learning/${mod.id}`}>
                    <ModuleCard module={mod} isDone={done2} isStarted={started} />
                  </Link>
                );
              })}
            </div>
          </section>
        );
      })}

      {/* ── CTA at bottom ────────────────────────────────────────────────── */}
      <div className="rounded-2xl border border-indigo-500/20 bg-indigo-500/5 p-6 text-center">
        <div className="text-2xl mb-2">🏆</div>
        <h3 className="text-white font-bold mb-1">All 73 modules available</h3>
        <p className="text-zinc-400 text-sm mb-4">
          Every lesson is packed with explanations, code examples, complexity analysis, real-world applications, and a quiz.
        </p>
        <Link
          to="/algorithms"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-500 hover:bg-indigo-400 text-white text-sm font-medium rounded-xl transition-colors"
        >
          Explore the Algorithm Catalog <ChevronRight size={14} />
        </Link>
      </div>
    </div>
  );
}
