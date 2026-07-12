import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Code2, CheckCircle2 } from 'lucide-react';
import { AnimateIn } from '../../components/ui/AnimateIn';
import { Button } from '../../components/ui/Button';
import { ATLASCODE_VERIFIED_PROBLEMS } from './Stats';

const ATLASCODE_JOURNEY = ['Learn', 'Visualize', 'Code', 'Run', 'Debug', 'Improve'];

function AtlasCodeMockPanel() {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#0D0D10] shadow-card overflow-hidden aspect-square flex flex-col">
      <div className="flex items-center gap-1.5 px-4 py-3 border-b border-white/5 bg-white/[0.02]">
        <span className="w-2.5 h-2.5 rounded-full bg-red-500/70" />
        <span className="w-2.5 h-2.5 rounded-full bg-yellow-500/70" />
        <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/70" />
        <span className="ml-3 text-xs text-zinc-500 font-mono">two-sum.py — AtlasCode</span>
      </div>

      <div className="flex flex-col flex-1 min-h-0">
        <div className="p-6 border-b border-white/5">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Easy
            </span>
            <span className="text-zinc-500 text-xs font-mono">hashing</span>
          </div>
          <h4 className="text-white font-semibold text-base mb-2">Two Sum</h4>
          <p className="text-zinc-400 text-sm leading-relaxed">
            Given an array of integers and a target, print the indices of the two
            numbers that add up to the target.
          </p>
        </div>

        <div className="p-6 flex flex-col gap-4 flex-1 min-h-0">
          <pre className="text-sm font-mono leading-relaxed text-zinc-300 overflow-auto flex-1">
{`def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return seen[target - x], i
        seen[x] = i`}
          </pre>
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2, duration: 0.4 }}
            className="flex items-center gap-2 rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-4 py-3"
          >
            <CheckCircle2 size={16} className="text-emerald-400 flex-shrink-0" />
            <span className="text-emerald-400 text-sm font-medium">Accepted</span>
            <span className="text-zinc-500 text-sm ml-auto font-mono">40/40 tests · 34ms</span>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

export function AtlasCodeShowcaseSection() {
  return (
    <section className="py-24 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <AnimateIn direction="right">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-rose-500/30 bg-rose-500/10 text-rose-300 text-xs font-medium mb-6">
              <Code2 size={12} />
              AtlasCode
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-5 leading-tight">
              From understanding the algorithm
              <br />
              to proving you can implement it.
            </h2>
            <p className="text-zinc-400 text-lg mb-6 leading-relaxed">
              Visualize an algorithm, then write real code against it.{' '}
              {ATLASCODE_VERIFIED_PROBLEMS}+ independently verified challenges,
              each judged against 40 hand-designed test cases — basic
              correctness, boundary conditions, adversarial inputs, and
              performance stress — across up to 17 supported languages.
            </p>
            <p className="text-zinc-500 text-sm mb-6 leading-relaxed">
              Solve in <span className="text-zinc-300 font-medium">LeetCode Mode</span> (write
              just the function) or <span className="text-zinc-300 font-medium">Codeforces Mode</span> (write
              a full stdin/stdout program). Every problem is complete and solvable today; the
              Problem Catalog shows per-problem language coverage separately, so it's always
              clear what's verified in which language without anything reading as unfinished.
            </p>

            <div className="flex flex-wrap items-center gap-2 mb-8">
              {ATLASCODE_JOURNEY.map((step, i) => (
                <div key={step} className="flex items-center gap-2">
                  <span className="text-sm font-medium text-zinc-300 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">
                    {step}
                  </span>
                  {i < ATLASCODE_JOURNEY.length - 1 && (
                    <span className="text-zinc-700">→</span>
                  )}
                </div>
              ))}
            </div>

            <Link to="/atlas-code">
              <Button variant="primary" size="lg" icon={<Code2 size={16} />}>
                Explore AtlasCode
              </Button>
            </Link>
          </AnimateIn>

          <AnimateIn direction="left" delay={0.1}>
            <AtlasCodeMockPanel />
          </AnimateIn>
        </div>
      </div>
    </section>
  );
}
