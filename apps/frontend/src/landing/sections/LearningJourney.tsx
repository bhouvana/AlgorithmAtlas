import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { GraduationCap, ArrowRight } from 'lucide-react';
import { AnimateIn } from '../../components/ui/AnimateIn';
import { Button } from '../../components/ui/Button';

// Mirrors apps/frontend/src/learning/data/curriculum.ts TRACKS + per-track
// module counts (confirmed 2026-07-12: 73 modules across 12 tracks).
const TRACKS = [
  { label: 'Algorithms in the Wild', icon: '🌍', count: 7, color: '#2dd4bf' },
  { label: 'Algorithmic Thinking', icon: '🧠', count: 7, color: '#60a5fa' },
  { label: 'Foundations', icon: '🧱', count: 9, color: '#fbbf24' },
  { label: 'Sorting', icon: '↕️', count: 8, color: '#818cf8' },
  { label: 'Searching', icon: '🔍', count: 4, color: '#22d3ee' },
  { label: 'Trees', icon: '🌳', count: 7, color: '#34d399' },
  { label: 'Graphs', icon: '🕸️', count: 9, color: '#a78bfa' },
  { label: 'Dynamic Programming', icon: '🧠', count: 6, color: '#f472b6' },
  { label: 'Greedy', icon: '⚡', count: 3, color: '#facc15' },
  { label: 'Backtracking', icon: '↩️', count: 3, color: '#fb923c' },
  { label: 'Practical Patterns', icon: '🎯', count: 6, color: '#e879f9' },
  { label: 'Advanced', icon: '🚀', count: 4, color: '#fb7185' },
];

export function LearningJourneySection() {
  return (
    <section className="py-24 px-4">
      <div className="max-w-6xl mx-auto">
        <AnimateIn className="text-center mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 text-xs font-medium mb-6">
            <GraduationCap size={12} />
            Structured Learning
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
            One path, from first principles to mastery.
          </h2>
          <p className="text-zinc-400 text-lg max-w-xl mx-auto">
            73 lessons across 12 tracks. Every lesson pairs an interactive visualization with
            worked examples, complexity analysis, and a quiz that actually checks understanding.
          </p>
        </AnimateIn>

        <div className="relative overflow-x-auto pb-6 -mx-4 px-4">
          <div className="relative min-w-[1100px] h-64">
            {/* connecting line */}
            <div className="absolute left-0 right-0 top-1/2 h-px bg-gradient-to-r from-transparent via-white/15 to-transparent" />

            <div className="relative flex justify-between h-full">
              {TRACKS.map((track, i) => {
                const above = i % 2 === 0;
                return (
                  <motion.div
                    key={track.label}
                    initial={{ opacity: 0, y: above ? 16 : -16 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: '-40px' }}
                    transition={{ duration: 0.4, delay: i * 0.05, ease: [0.22, 1, 0.36, 1] }}
                    className={`relative flex flex-col items-center w-[84px] ${above ? 'justify-end' : 'justify-start'}`}
                    style={{ marginTop: above ? 0 : 'auto', marginBottom: above ? 'auto' : 0 }}
                  >
                    {above && <TrackCard track={track} />}
                    <span
                      className="w-3 h-3 rounded-full border-2 border-[#09090B] my-2 flex-shrink-0"
                      style={{ backgroundColor: track.color, boxShadow: `0 0 12px ${track.color}66` }}
                    />
                    {!above && <TrackCard track={track} />}
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>

        <AnimateIn delay={0.15} className="flex justify-center mt-6">
          <Link to="/learning">
            <Button variant="primary" size="lg" icon={<ArrowRight size={16} />}>
              Browse the curriculum
            </Button>
          </Link>
        </AnimateIn>
      </div>
    </section>
  );
}

function TrackCard({ track }: { track: (typeof TRACKS)[number] }) {
  return (
    <div className="flex flex-col items-center text-center gap-1.5 w-[100px] -mx-2">
      <span className="text-2xl leading-none">{track.icon}</span>
      <span className="text-[11px] font-medium text-zinc-300 leading-tight">{track.label}</span>
      <span className="text-[10px] font-mono text-zinc-600">{track.count} lessons</span>
    </div>
  );
}
