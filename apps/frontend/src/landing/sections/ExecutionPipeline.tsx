import { Fragment, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { FileCode2, Cog, Boxes, Scale, CheckCircle2 } from 'lucide-react';
import { AnimateIn } from '../../components/ui/AnimateIn';
import { cn } from '../../lib/utils';

// Mirrors the real judge pipeline documented in
// docs/atlascode-judge-workspace.md: source -> compile-once -> sandboxed
// per-case execution -> comparator -> verdict. Not aspirational copy — this
// is the actual architecture (PreparedProgram, real exit codes, psutil
// memory sampling, contracts.compare_typed).
const STAGES = [
  {
    icon: FileCode2,
    title: 'Source',
    detail: 'Your code, in any of 17 supported languages.',
    color: '#818cf8',
  },
  {
    icon: Cog,
    title: 'Compile once',
    detail: 'Compiled languages build a single PreparedProgram, reused across all 40 cases.',
    color: '#facc15',
  },
  {
    icon: Boxes,
    title: 'Sandboxed run',
    detail: 'Each case runs isolated with a real exit code, wall time, and sampled memory.',
    color: '#38bdf8',
  },
  {
    icon: Scale,
    title: 'Compare',
    detail: 'One shared comparator normalizes output, never a per-language drift.',
    color: '#f472b6',
  },
  {
    icon: CheckCircle2,
    title: 'Verdict',
    detail: 'Accepted, or the first failing case with a concrete diff.',
    color: '#34d399',
  },
] as const;

const STEP_MS = 900;

export function ExecutionPipelineSection() {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setActive((i) => (i + 1) % (STAGES.length + 1)), STEP_MS);
    return () => clearInterval(t);
  }, []);

  return (
    <section className="py-24 px-4">
      <div className="max-w-5xl mx-auto">
        <AnimateIn className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-amber-500/30 bg-amber-500/10 text-amber-300 text-xs font-medium mb-6">
            Under the hood
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
            A real judge, not a toy checker.
          </h2>
          <p className="text-zinc-400 text-lg max-w-xl mx-auto">
            Every submission compiles once, runs sandboxed per test case, and is scored by a
            single comparator shared across every language, so "correct" means the same thing
            everywhere.
          </p>
          <p className="text-zinc-500 text-sm max-w-xl mx-auto mt-3">
            Available in both{' '}
            <span className="text-zinc-300 font-medium">LeetCode Mode</span> (function only) and{' '}
            <span className="text-zinc-300 font-medium">Codeforces Mode</span> (full stdin/stdout
            program): same pipeline, same comparator, either way.
          </p>
        </AnimateIn>

        <AnimateIn delay={0.1}>
          {/* flex row of [icon column, connector, icon column, connector, ...] —
             each connector is its own small element living ONLY in the gap
             between two icon boxes, so the line can never visually cross
             behind/through a square (the old single full-width rail did,
             since it ran at the icons' vertical center the whole way). */}
          <div className="flex flex-col sm:flex-row items-center sm:items-start gap-8 sm:gap-0">
            {STAGES.map((stage, i) => {
              const Icon = stage.icon;
              const lit = i <= active;
              const isCurrent = i === active;
              const nextStage = STAGES[i + 1];
              const connectorFilled = active > i;
              return (
                <Fragment key={stage.title}>
                  <div className="flex flex-col items-center text-center gap-3 sm:flex-1 sm:min-w-0">
                    <motion.div
                      className="relative w-16 h-16 rounded-2xl flex items-center justify-center border flex-shrink-0"
                      animate={{
                        borderColor: lit ? `${stage.color}66` : 'rgba(255,255,255,0.08)',
                        backgroundColor: lit ? `${stage.color}14` : 'rgba(255,255,255,0.02)',
                        scale: isCurrent ? 1.08 : 1,
                        boxShadow: isCurrent
                          ? `0 0 0 1px ${stage.color}55, 0 0 22px 4px ${stage.color}40`
                          : '0 0 0 0 transparent',
                      }}
                      transition={{ duration: 0.3 }}
                    >
                      <Icon size={22} style={{ color: lit ? stage.color : '#71717a' }} />
                    </motion.div>
                    <h3 className={cn('text-sm font-semibold transition-colors duration-300 h-5', lit ? 'text-white' : 'text-zinc-500')}>
                      {stage.title}
                    </h3>
                    {/* Fixed min-height so all 5 columns bottom-align evenly
                       regardless of description length (the longest detail
                       text wraps to 3 lines at this width). */}
                    <p className="text-xs text-zinc-500 leading-relaxed max-w-[160px] min-h-[58px]">{stage.detail}</p>
                  </div>

                  {nextStage && (
                    <div className="hidden sm:flex flex-shrink-0 w-8 md:w-12 items-center" style={{ marginTop: '31px' }}>
                      <div className="relative w-full h-px bg-white/10 rounded-full overflow-hidden">
                        <motion.div
                          className="absolute inset-y-0 left-0 h-px"
                          style={{ background: `linear-gradient(90deg, ${stage.color}, ${nextStage.color})` }}
                          animate={{ width: connectorFilled ? '100%' : '0%' }}
                          transition={{ duration: STEP_MS / 1000, ease: 'easeInOut' }}
                        />
                      </div>
                    </div>
                  )}
                </Fragment>
              );
            })}
          </div>
        </AnimateIn>
      </div>
    </section>
  );
}
