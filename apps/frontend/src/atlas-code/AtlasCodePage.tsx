import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Code2, Trophy, Zap, Target, ArrowRight, Calendar, Brain } from 'lucide-react';
import { getDailyChallenge, getProgress, listProblems } from './api/problems';
import type { DailyChallengeOut, ProgressOut, ProblemSummary } from './api/problems';

const DIFFICULTY_COLOR: Record<string, string> = {
  Easy: 'text-emerald-400',
  Medium: 'text-amber-400',
  Hard: 'text-rose-400',
};

function StatCard({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string | number }) {
  return (
    <div className="flex flex-col gap-1 bg-white/5 rounded-2xl p-4 border border-charcoal/10">
      <Icon className="w-5 h-5 text-indigo-400 mb-1" />
      <div className="text-2xl font-bold text-white">{value}</div>
      <div className="text-xs text-zinc-500">{label}</div>
    </div>
  );
}

export function AtlasCodePage() {
  const [daily, setDaily] = useState<DailyChallengeOut | null>(null);
  const [progress, setProgress] = useState<ProgressOut | null>(null);
  const [recentProblems, setRecentProblems] = useState<ProblemSummary[]>([]);

  useEffect(() => {
    getDailyChallenge().then(setDaily).catch(() => {});
    getProgress('anonymous').then(setProgress).catch(() => {});
    listProblems({ limit: 6 }).then(setRecentProblems).catch(() => {});
  }, []);

  return (
    <div className="min-h-screen pt-20 px-4 pb-16">
      <div className="max-w-5xl mx-auto">
        {/* Hero */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-16"
        >
          <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 rounded-full px-4 py-1.5 text-sm text-indigo-400 mb-6">
            <Code2 className="w-4 h-4" />
            <span>AtlasCode — Learn by Doing</span>
          </div>
          <h1 className="text-5xl font-bold text-white mb-4 tracking-tight">
            Code. Visualize. Master.
          </h1>
          <p className="text-xl text-zinc-400 max-w-2xl mx-auto mb-10">
            Solve algorithm problems with an interactive IDE, instant visualization of your code's execution, and Atlas AI as your personal coach.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link
              to="/atlas-code/catalog"
              className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-xl font-medium transition-colors"
            >
              Browse Problems <ArrowRight className="w-4 h-4" />
            </Link>
            {daily && (
              <Link
                to={`/atlas-code/problem/${daily.problem_id}`}
                className="inline-flex items-center gap-2 bg-white/5 hover:bg-white/10 border border-charcoal/10 text-white px-6 py-3 rounded-xl font-medium transition-colors"
              >
                <Calendar className="w-4 h-4 text-amber-400" />
                Daily Challenge
              </Link>
            )}
          </div>
        </motion.div>

        {/* Progress stats */}
        {progress && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-2 gap-3 mb-12"
          >
            <StatCard icon={Trophy} label="Problems Solved" value={progress.solved_problems.length} />
            <StatCard icon={Target} label="Attempted" value={progress.attempted_problems.length} />
          </motion.div>
        )}

        {/* Daily Challenge banner */}
        {daily && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="mb-10"
          >
            <Link
              to={`/atlas-code/problem/${daily.problem_id}`}
              className="flex items-center justify-between bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20 rounded-2xl p-5 hover:border-amber-500/40 transition-colors group"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-amber-500/20 flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-amber-400" />
                </div>
                <div>
                  <div className="text-xs text-amber-400 font-medium mb-0.5">Daily Challenge — +{daily.bonus_xp} XP</div>
                  <div className="text-white font-semibold">{daily.problem_title}</div>
                  <div className="text-xs text-zinc-500 mt-0.5">
                    <span className={DIFFICULTY_COLOR[daily.problem_difficulty]}>{daily.problem_difficulty}</span>
                    {' · '}{daily.problem_category}
                  </div>
                </div>
              </div>
              <ArrowRight className="w-5 h-5 text-zinc-500 group-hover:text-white transition-colors" />
            </Link>
          </motion.div>
        )}

        {/* Feature bento grid */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-12"
        >
          {[
            {
              icon: Code2,
              color: 'text-indigo-400',
              bg: 'bg-indigo-500/10',
              title: '17 Languages',
              desc: 'Python, JavaScript, C++, Java, Go, Rust, and more — all in your browser.',
            },
            {
              icon: Zap,
              color: 'text-amber-400',
              bg: 'bg-amber-500/10',
              title: 'Live Visualization',
              desc: 'Click "Visualize" to watch your solution execute step-by-step in the Atlas engine.',
            },
            {
              icon: Brain,
              color: 'text-emerald-400',
              bg: 'bg-emerald-500/10',
              title: 'AI Code Review',
              desc: 'Atlas AI reviews your code, explains failing cases, and suggests improvements.',
            },
          ].map(({ icon: Icon, color, bg, title, desc }) => (
            <div key={title} className="bg-white/4 border border-charcoal/10 rounded-2xl p-5">
              <div className={`w-10 h-10 rounded-xl ${bg} flex items-center justify-center mb-3`}>
                <Icon className={`w-5 h-5 ${color}`} />
              </div>
              <div className="text-white font-semibold mb-1">{title}</div>
              <div className="text-sm text-zinc-500">{desc}</div>
            </div>
          ))}
        </motion.div>

        {/* Recent / starter problems */}
        {recentProblems.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white">Start Here</h2>
              <Link to="/atlas-code/catalog" className="text-sm text-indigo-400 hover:text-indigo-300">
                View all →
              </Link>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {recentProblems.map((p) => (
                <Link
                  key={p.id}
                  to={`/atlas-code/problem/${p.id}`}
                  className="bg-white/4 border border-charcoal/10 rounded-xl p-4 hover:border-indigo-500/40 hover:bg-white/6 transition-all group"
                >
                  <div className="flex items-start justify-between mb-2">
                    <span className={`text-xs font-medium ${DIFFICULTY_COLOR[p.difficulty]}`}>{p.difficulty}</span>
                    <span className="text-xs text-zinc-600">{p.acceptance_rate.toFixed(0)}%</span>
                  </div>
                  <div className="text-sm font-medium text-white group-hover:text-indigo-300 transition-colors">{p.title}</div>
                  <div className="text-xs text-zinc-600 mt-1 capitalize">{p.category.replace(/-/g, ' ')}</div>
                </Link>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
