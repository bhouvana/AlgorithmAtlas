import { useState } from 'react';
import { motion } from 'framer-motion';
import { ComplexityChart } from '../visualizations/ComplexityChart';

const COMPLEXITIES = [
  { name: 'O(1)',       label: 'Constant',      color: 'text-green-400',  bg: 'bg-green-500/10 border-green-500/20', example: 'Array index access a[5]', desc: 'Always the same time, no matter the input size.' },
  { name: 'O(log n)',   label: 'Logarithmic',   color: 'text-cyan-400',   bg: 'bg-cyan-500/10 border-cyan-500/20',  example: 'Binary search in sorted array', desc: 'Halves the problem each step. Amazingly fast for large n.' },
  { name: 'O(n)',       label: 'Linear',        color: 'text-violet-400', bg: 'bg-violet-500/10 border-violet-500/20',example: 'Find max in unsorted array', desc: 'One operation per input element. The baseline for efficient algorithms.' },
  { name: 'O(n log n)', label: 'Linearithmic',  color: 'text-amber-400',  bg: 'bg-amber-500/10 border-amber-500/20', example: 'Merge sort, Quick sort (avg)', desc: 'The best you can do for comparison-based sorting.' },
  { name: 'O(n²)',      label: 'Quadratic',     color: 'text-orange-400', bg: 'bg-orange-500/10 border-orange-500/20',example: 'Bubble sort, nested loops', desc: 'Every pair of elements. Acceptable for n < 1000, painful beyond.' },
  { name: 'O(2ⁿ)',      label: 'Exponential',   color: 'text-red-400',    bg: 'bg-red-500/10 border-red-500/20',     example: 'Naive recursive Fibonacci', desc: 'Doubles with each new element. Unusable for n > 30.' },
];

const QUIZ_QUESTIONS = [
  {
    q: 'What is the time complexity of accessing the 5th element of an array?',
    options: ['O(n)', 'O(log n)', 'O(1)', 'O(n²)'],
    correct: 2,
    explanation: 'Array access by index is always O(1) — the computer can jump directly to any position using pointer arithmetic.',
  },
  {
    q: 'An algorithm loops through n elements, and for each one loops through n again. What is its complexity?',
    options: ['O(n)', 'O(2n)', 'O(n log n)', 'O(n²)'],
    correct: 3,
    explanation: 'Nested loops that each run n times multiply to give O(n × n) = O(n²). Classic example: Bubble Sort.',
  },
  {
    q: 'Binary search on 1,000,000 elements takes at most how many comparisons?',
    options: ['500,000', '1,000', '~20', '100'],
    correct: 2,
    explanation: 'log₂(1,000,000) ≈ 20. Binary search is O(log n) — it halves the search space each step, so 1M elements needs only ~20 steps!',
  },
];

export function BigOLesson() {
  const [activeComplexity, setActiveComplexity] = useState<string | null>(null);
  const [quizAnswers, setQuizAnswers] = useState<(number | null)[]>([null, null, null]);
  const [quizRevealed, setQuizRevealed] = useState<boolean[]>([false, false, false]);

  const answer = (qi: number, ai: number) => {
    if (quizAnswers[qi] !== null) return;
    setQuizAnswers((prev) => { const n = [...prev]; n[qi] = ai; return n; });
    setQuizRevealed((prev) => { const n = [...prev]; n[qi] = true; return n; });
  };

  return (
    <div className="space-y-16">

      {/* ── Concept Overview ─────────────────────────────────────────────── */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs font-mono text-indigo-400 uppercase tracking-widest">Concept</span>
        </div>
        <h2 className="text-2xl font-bold text-white mb-4">What is Big O Notation?</h2>
        <div className="prose prose-invert prose-zinc max-w-none">
          <p className="text-zinc-300 text-base leading-relaxed">
            Big O notation is the universal language that engineers use to describe <strong className="text-white">how an algorithm's runtime grows</strong> as the input gets larger. Instead of saying "this function takes 2.4 milliseconds," we say it's <strong className="text-amber-300">O(n²)</strong> — which tells us exactly how it will behave on 10× more data.
          </p>
          <p className="text-zinc-300 text-base leading-relaxed mt-3">
            Think of it as measuring the <em>shape</em> of growth, not the exact time. A constant like O(1) is a flat line. O(n) is a straight slope. O(n²) curves upward fast. We ignore constants and smaller terms — <code className="text-indigo-300 bg-indigo-500/10 px-1 rounded">3n + 100</code> is still just O(n).
          </p>
        </div>

        {/* The three rules */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-6">
          {[
            { title: 'Drop the Constants', code: '5n → O(n)', desc: 'We care about growth shape, not multipliers.' },
            { title: 'Drop Non-Dominants', code: 'n² + n → O(n²)', desc: 'At large n, the biggest term wins.' },
            { title: 'Worst Case', code: 'We measure the ceiling', desc: 'Big O describes the upper bound on time.' },
          ].map((rule) => (
            <div key={rule.title} className="rounded-xl border border-charcoal/10 bg-zinc-900/40 p-4">
              <div className="font-semibold text-white text-sm mb-1">{rule.title}</div>
              <div className="font-mono text-indigo-300 text-sm mb-2">{rule.code}</div>
              <div className="text-zinc-400 text-xs">{rule.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Complexity Classes ────────────────────────────────────────────── */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs font-mono text-amber-400 uppercase tracking-widest">Complexity Classes</span>
        </div>
        <h2 className="text-xl font-bold text-white mb-4">The Big O Hierarchy</h2>
        <p className="text-zinc-400 text-sm mb-5">Click any class to learn more about it.</p>

        <div className="space-y-2">
          {COMPLEXITIES.map((c) => (
            <motion.button
              key={c.name}
              onClick={() => setActiveComplexity(activeComplexity === c.name ? null : c.name)}
              className={`w-full text-left rounded-xl border p-4 transition-all duration-200 ${
                activeComplexity === c.name ? c.bg : 'border-white/8 bg-zinc-900/30 hover:bg-zinc-900/50'
              }`}
              layout
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <code className={`font-mono font-bold text-lg ${c.color}`}>{c.name}</code>
                  <span className="text-zinc-300 text-sm">{c.label}</span>
                </div>
                <span className="text-zinc-500 text-xs font-mono">{c.example}</span>
              </div>
              {activeComplexity === c.name && (
                <motion.p
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="text-zinc-300 text-sm mt-3 pt-3 border-t border-white/10"
                >
                  {c.desc}
                </motion.p>
              )}
            </motion.button>
          ))}
        </div>
      </section>

      {/* ── Interactive Complexity Chart ──────────────────────────────────── */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs font-mono text-cyan-400 uppercase tracking-widest">Visualization</span>
        </div>
        <h2 className="text-xl font-bold text-white mb-2">See How They Diverge</h2>
        <p className="text-zinc-400 text-sm mb-5">
          Toggle complexities on/off and hover to compare exact values. Watch how O(n²) and O(2ⁿ) explode while O(log n) stays calm.
        </p>
        <ComplexityChart />
      </section>

      {/* ── Code Examples ─────────────────────────────────────────────────── */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs font-mono text-violet-400 uppercase tracking-widest">Examples</span>
        </div>
        <h2 className="text-xl font-bold text-white mb-5">Reading Big O in Code</h2>

        <div className="space-y-4">
          {[
            {
              label: 'O(1) — Direct access',
              complexity: 'O(1)',
              color: 'text-green-400',
              code: `function getFirst(arr) {\n  return arr[0];  // Always one operation\n}`,
            },
            {
              label: 'O(n) — Single loop',
              complexity: 'O(n)',
              color: 'text-violet-400',
              code: `function findMax(arr) {\n  let max = arr[0];\n  for (let i = 1; i < arr.length; i++) {\n    if (arr[i] > max) max = arr[i]; // n iterations\n  }\n  return max;\n}`,
            },
            {
              label: 'O(n²) — Nested loops',
              complexity: 'O(n²)',
              color: 'text-orange-400',
              code: `function hasDuplicate(arr) {\n  for (let i = 0; i < arr.length; i++) {\n    for (let j = i + 1; j < arr.length; j++) {\n      if (arr[i] === arr[j]) return true; // n * n iterations\n    }\n  }\n  return false;\n}`,
            },
          ].map((ex) => (
            <div key={ex.label} className="rounded-xl border border-charcoal/10 bg-zinc-950/60 overflow-hidden">
              <div className="flex items-center justify-between px-4 py-2 border-b border-white/5 bg-zinc-900/40">
                <span className="text-xs text-zinc-400">{ex.label}</span>
                <code className={`text-xs font-mono font-bold ${ex.color}`}>{ex.complexity}</code>
              </div>
              <pre className="p-4 text-xs font-mono text-zinc-300 overflow-x-auto leading-relaxed">
                {ex.code}
              </pre>
            </div>
          ))}
        </div>
      </section>

      {/* ── Real World Applications ───────────────────────────────────────── */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs font-mono text-emerald-400 uppercase tracking-widest">Real World</span>
        </div>
        <h2 className="text-xl font-bold text-white mb-5">Why Engineers Obsess Over Big O</h2>
        <div className="grid md:grid-cols-2 gap-4">
          {[
            { company: 'Google Search', scenario: 'Indexing billions of web pages', bad: 'O(n²) would take centuries', good: 'O(n log n) indexing makes results instant' },
            { company: 'Databases', scenario: 'Finding a row among millions', bad: 'O(n) table scan = slow queries', good: 'O(log n) B-tree index = millisecond lookups' },
            { company: 'Social Networks', scenario: 'Finding mutual friends', bad: 'O(n³) naive = unusable at scale', good: 'Graph algorithms + distributed compute' },
            { company: 'GPS/Navigation', scenario: 'Shortest path through a city', bad: 'O(n!) brute force = impossible', good: "O(E log V) Dijkstra's = instant directions" },
          ].map((item) => (
            <div key={item.company} className="rounded-xl border border-charcoal/10 bg-zinc-900/30 p-4">
              <div className="font-semibold text-white text-sm mb-2">{item.company}</div>
              <div className="text-zinc-400 text-xs mb-3">{item.scenario}</div>
              <div className="space-y-1.5">
                <div className="flex gap-2 text-xs">
                  <span className="text-red-400">✗</span>
                  <span className="text-zinc-500">{item.bad}</span>
                </div>
                <div className="flex gap-2 text-xs">
                  <span className="text-emerald-400">✓</span>
                  <span className="text-zinc-300">{item.good}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Quiz ──────────────────────────────────────────────────────────── */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs font-mono text-rose-400 uppercase tracking-widest">Quiz</span>
        </div>
        <h2 className="text-xl font-bold text-white mb-6">Test Your Understanding</h2>

        <div className="space-y-6">
          {QUIZ_QUESTIONS.map((q, qi) => (
            <div key={qi} className="rounded-xl border border-charcoal/10 bg-zinc-900/30 p-5">
              <div className="font-medium text-white mb-4 text-sm">{q.q}</div>
              <div className="grid grid-cols-2 gap-2">
                {q.options.map((opt, ai) => {
                  const chosen = quizAnswers[qi] === ai;
                  const revealed = quizRevealed[qi];
                  const correct = ai === q.correct;
                  let style = 'border-white/10 text-zinc-400 hover:border-white/20 hover:text-zinc-200';
                  if (revealed) {
                    if (correct) style = 'border-emerald-500/50 bg-emerald-500/10 text-emerald-300';
                    else if (chosen) style = 'border-red-500/50 bg-red-500/10 text-red-300';
                    else style = 'border-white/5 text-zinc-600';
                  }
                  return (
                    <button
                      key={ai}
                      onClick={() => answer(qi, ai)}
                      disabled={revealed}
                      className={`text-left px-3 py-2 rounded-lg border text-sm transition-all duration-150 ${style}`}
                    >
                      <span className="font-mono text-xs opacity-50 mr-2">{String.fromCharCode(65 + ai)}.</span>
                      {opt}
                    </button>
                  );
                })}
              </div>
              {quizRevealed[qi] && (
                <motion.div
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-3 px-3 py-2 rounded-lg bg-zinc-800/50 text-xs text-zinc-300 border border-charcoal/10"
                >
                  💡 {q.explanation}
                </motion.div>
              )}
            </div>
          ))}
        </div>
      </section>

    </div>
  );
}
