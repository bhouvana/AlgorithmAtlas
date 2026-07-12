import { useEffect, useRef, useState } from 'react';
import { useInView } from 'framer-motion';
import { AnimateIn } from '../../components/ui/AnimateIn';

interface StatItem {
  value: number;
  suffix: string;
  label: string;
  color: string;
}

// AtlasCode's problem-completion count is a floor, not a live query — the
// landing page is static-rendered. Keep this at or below the real DB count
// (confirmed via `python scripts/generate_honest_matrix_report.py` at the
// time this was last updated); round DOWN when in doubt, never up.
// Completion is measured at the PROBLEM level (see
// docs/atlascode-complete-matrix.md "Problem Completion"): a problem counts
// once it has a working judge + at least one verified language, regardless
// of how many of the 17 target languages are covered so far (tracked
// separately as Language Coverage, currently 48.81%).
// Last confirmed 2026-07-12: 216/216 problems complete (215 at the
// exactly-40-test standard, 1 documented exception, n-queens, ships 12).
export const ATLASCODE_VERIFIED_PROBLEMS = 216;

// Learning curriculum: apps/frontend/src/learning/data/curriculum.ts
// MODULES.length = 73, TRACKS.length = 12 (confirmed 2026-07-12).
const STATS: StatItem[] = [
  { value: 250, suffix: '+', label: 'Algorithms', color: 'from-indigo-400 to-indigo-300' },
  { value: ATLASCODE_VERIFIED_PROBLEMS, suffix: '+', label: 'AtlasCode Problems', color: 'from-rose-400 to-orange-300' },
  { value: 73, suffix: '', label: 'Lessons', color: 'from-emerald-400 to-teal-300' },
  { value: 13, suffix: '', label: 'Viz Types', color: 'from-purple-400 to-pink-300' },
  { value: 17, suffix: '', label: 'Languages', color: 'from-cyan-400 to-teal-300' },
];

function useCountUp(target: number, duration = 1500) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: '-80px' });

  useEffect(() => {
    if (!inView) return;
    let startTime: number | null = null;
    const step = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCount(Math.round(eased * target));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [inView, target, duration]);

  return { count, ref };
}

function StatCard({ value, suffix, label, color }: StatItem) {
  const { count, ref } = useCountUp(value);

  return (
    <div ref={ref} className="flex flex-col items-center gap-2 p-6">
      <span
        className={`text-4xl sm:text-5xl font-bold bg-gradient-to-r ${color} bg-clip-text text-transparent tabular-nums`}
      >
        {count}
        {suffix}
      </span>
      <span className="text-zinc-400 text-sm font-medium">{label}</span>
    </div>
  );
}

export function StatsSection() {
  return (
    <section className="py-20 px-4">
      <AnimateIn className="max-w-4xl mx-auto">
        <div className="rounded-2xl border border-white/8 bg-[#18181B] grid grid-cols-2 sm:grid-cols-5 divide-x divide-y sm:divide-y-0 divide-white/8 overflow-hidden shadow-card">
          {STATS.map((stat) => (
            <StatCard key={stat.label} {...stat} />
          ))}
        </div>
      </AnimateIn>
    </section>
  );
}
