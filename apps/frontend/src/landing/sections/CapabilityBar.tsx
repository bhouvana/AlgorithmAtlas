import { Link } from 'react-router-dom';
import { Play, GitCompare, Zap, GraduationCap, Code2, Sparkles } from 'lucide-react';
import { AnimateIn } from '../../components/ui/AnimateIn';

const CAPABILITIES = [
  { icon: Play, label: 'Step-by-step simulation', to: '/algorithms', color: 'text-indigo-400' },
  { icon: GitCompare, label: 'Side-by-side comparison', to: '/compare', color: 'text-blue-400' },
  { icon: Zap, label: 'Real-time execution', to: '/notebook', color: 'text-amber-400' },
  { icon: GraduationCap, label: 'Structured learning', to: '/learning', color: 'text-emerald-400' },
  { icon: Code2, label: 'Verified coding challenges', to: '/atlas-code', color: 'text-rose-400' },
  { icon: Sparkles, label: 'AI co-pilot', to: '/algorithms', color: 'text-purple-400' },
];

export function CapabilityBarSection() {
  return (
    <section className="px-4 pb-4">
      <AnimateIn className="max-w-5xl mx-auto">
        <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-3">
          {CAPABILITIES.map((c) => {
            const Icon = c.icon;
            return (
              <Link
                key={c.label}
                to={c.to}
                className="flex items-center gap-2 px-4 py-2 rounded-full border border-white/8 bg-white/[0.03] hover:bg-white/[0.06] hover:border-white/15 transition-colors duration-200"
              >
                <Icon size={14} className={c.color} />
                <span className="text-xs font-medium text-zinc-300 whitespace-nowrap">{c.label}</span>
              </Link>
            );
          })}
        </div>
      </AnimateIn>
    </section>
  );
}
