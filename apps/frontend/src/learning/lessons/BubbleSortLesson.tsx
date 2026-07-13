import { SortVisualizer } from '../visualizations/SortVisualizer';

const QUIZ_QUESTIONS = [
  {
    q: 'What is the worst-case time complexity of Bubble Sort?',
    options: ['O(n)', 'O(n log n)', 'O(n²)', 'O(log n)'],
    correct: 2,
    explanation: 'In the worst case (reverse-sorted array), Bubble Sort makes n-1 passes, each comparing up to n-1 pairs: O(n²) total comparisons.',
  },
  {
    q: 'When does Bubble Sort achieve its best-case O(n)?',
    options: ['Always', 'When array is already sorted', 'When array has n/2 elements', 'Never'],
    correct: 1,
    explanation: 'With early exit optimization: if we complete a pass with no swaps, the array is already sorted and we can stop — only 1 pass = O(n).',
  },
  {
    q: 'Why is Bubble Sort rarely used in production?',
    options: ['It uses too much memory', 'O(n²) is too slow for large arrays', "It doesn't work on all data types", 'It is not stable'],
    correct: 1,
    explanation: 'Bubble Sort is O(n²) in average/worst case. Real sorting algorithms like Timsort or introsort (used by Python/C++/Java) are O(n log n).',
  },
];

import { useState } from 'react';
import { motion } from 'framer-motion';

export function BubbleSortLesson() {
  const [quizAnswers, setQuizAnswers] = useState<(number | null)[]>([null, null, null]);
  const [quizRevealed, setQuizRevealed] = useState<boolean[]>([false, false, false]);

  const answer = (qi: number, ai: number) => {
    if (quizAnswers[qi] !== null) return;
    setQuizAnswers((prev) => { const n = [...prev]; n[qi] = ai; return n; });
    setQuizRevealed((prev) => { const n = [...prev]; n[qi] = true; return n; });
  };

  return (
    <div className="space-y-16">

      {/* ── Concept ──────────────────────────────────────────────────────── */}
      <section>
        <div className="mb-3"><span className="text-xs font-mono text-indigo-400 uppercase tracking-widest">Concept</span></div>
        <h2 className="text-2xl font-bold text-white mb-4">How Bubble Sort Works</h2>
        <p className="text-zinc-300 text-base leading-relaxed mb-4">
          Bubble Sort is the simplest sorting algorithm — and the most intuitive. It makes <strong className="text-white">repeated passes</strong> through the array, comparing adjacent pairs and swapping them if they are out of order. After each pass, the largest unsorted element "bubbles up" to its correct position at the end.
        </p>
        <div className="grid md:grid-cols-3 gap-3">
          {[
            { step: '1', label: 'Compare neighbors', desc: 'Look at elements at positions i and i+1' },
            { step: '2', label: 'Swap if needed',    desc: 'If left > right, swap them' },
            { step: '3', label: 'Repeat',            desc: 'Continue until no swaps needed' },
          ].map((s) => (
            <div key={s.step} className="rounded-xl border border-charcoal/10 bg-zinc-900/40 p-4 flex gap-3">
              <div className="w-7 h-7 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-xs font-bold text-indigo-300 flex-shrink-0">{s.step}</div>
              <div>
                <div className="font-medium text-white text-sm mb-0.5">{s.label}</div>
                <div className="text-zinc-400 text-xs">{s.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Visualization ─────────────────────────────────────────────────── */}
      <section>
        <div className="mb-3"><span className="text-xs font-mono text-amber-400 uppercase tracking-widest">Visualization</span></div>
        <h2 className="text-xl font-bold text-white mb-2">Watch It Step by Step</h2>
        <p className="text-zinc-400 text-sm mb-5">
          Use Play/Pause or step through frame-by-frame. Compare how Bubble, Insertion, and Selection sort handle the same array.
        </p>
        <div className="rounded-xl border border-charcoal/10 bg-zinc-950/50 p-5">
          <SortVisualizer showAlgoSelector={true} size={14} />
        </div>
      </section>

      {/* ── The Code ──────────────────────────────────────────────────────── */}
      <section>
        <div className="mb-3"><span className="text-xs font-mono text-violet-400 uppercase tracking-widest">Implementation</span></div>
        <h2 className="text-xl font-bold text-white mb-5">Bubble Sort in Code</h2>
        <div className="space-y-4">
          <div className="rounded-xl border border-charcoal/10 bg-zinc-950/60 overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-charcoal/10 bg-zinc-900/40">
              <span className="text-xs text-zinc-400">Basic version</span>
              <code className="text-xs font-mono text-orange-400">O(n²)</code>
            </div>
            <pre className="p-4 text-xs font-mono text-zinc-300 overflow-x-auto leading-relaxed">{`function bubbleSort(arr) {
  const n = arr.length;
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]]; // swap
      }
    }
    // After pass i, the last i elements are in place
  }
  return arr;
}`}</pre>
          </div>

          <div className="rounded-xl border border-emerald-500/20 bg-zinc-950/60 overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-emerald-500/10 bg-emerald-500/5">
              <span className="text-xs text-emerald-400">Optimized with early exit</span>
              <code className="text-xs font-mono text-emerald-400">O(n) best case</code>
            </div>
            <pre className="p-4 text-xs font-mono text-zinc-300 overflow-x-auto leading-relaxed">{`function bubbleSortOptimized(arr) {
  const n = arr.length;
  for (let i = 0; i < n; i++) {
    let swapped = false;                  // track if any swap happened
    for (let j = 0; j < n - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
        swapped = true;
      }
    }
    if (!swapped) break;                  // already sorted → stop early
  }
  return arr;
}`}</pre>
          </div>
        </div>
      </section>

      {/* ── Complexity ────────────────────────────────────────────────────── */}
      <section>
        <div className="mb-3"><span className="text-xs font-mono text-cyan-400 uppercase tracking-widest">Complexity</span></div>
        <h2 className="text-xl font-bold text-white mb-5">Time & Space Breakdown</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-charcoal/10">
                <th className="text-left py-2 px-3 text-zinc-400 font-medium text-xs">Case</th>
                <th className="text-left py-2 px-3 text-zinc-400 font-medium text-xs">Time</th>
                <th className="text-left py-2 px-3 text-zinc-400 font-medium text-xs">When</th>
              </tr>
            </thead>
            <tbody>
              {[
                { c: 'Best',    t: 'O(n)',  color: 'text-emerald-400', w: 'Already sorted array + early exit' },
                { c: 'Average', t: 'O(n²)', color: 'text-amber-400',   w: 'Random order array' },
                { c: 'Worst',   t: 'O(n²)', color: 'text-red-400',     w: 'Reverse-sorted array' },
                { c: 'Space',   t: 'O(1)',  color: 'text-cyan-400',    w: 'Sorts in-place, no extra memory' },
              ].map((row) => (
                <tr key={row.c} className="border-b border-charcoal/10">
                  <td className="py-2.5 px-3 text-zinc-300 font-medium text-xs">{row.c}</td>
                  <td className="py-2.5 px-3"><code className={`font-mono font-bold text-sm ${row.color}`}>{row.t}</code></td>
                  <td className="py-2.5 px-3 text-zinc-400 text-xs">{row.w}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 p-4 rounded-xl border border-indigo-500/20 bg-indigo-500/5 text-sm text-zinc-300">
          <span className="text-indigo-300 font-medium">Stability:</span> Bubble Sort is <strong className="text-white">stable</strong> — equal elements maintain their original relative order (we only swap when strictly greater).
        </div>
      </section>

      {/* ── Common Mistakes ───────────────────────────────────────────────── */}
      <section>
        <div className="mb-3"><span className="text-xs font-mono text-rose-400 uppercase tracking-widest">Common Mistakes</span></div>
        <h2 className="text-xl font-bold text-white mb-5">Pitfalls to Avoid</h2>
        <div className="space-y-3">
          {[
            {
              bad: 'for (let j = 0; j < n - 1; j++)',
              good: 'for (let j = 0; j < n - i - 1; j++)',
              explain: 'The inner loop bound should shrink each outer pass. The last i elements are already sorted — no need to re-check them.',
            },
            {
              bad: 'if (arr[j] >= arr[j + 1]) swap()',
              good: 'if (arr[j] > arr[j + 1]) swap()',
              explain: 'Using >= instead of > destroys stability: equal elements get unnecessarily swapped, changing their relative order.',
            },
          ].map((m) => (
            <div key={m.bad} className="rounded-xl border border-charcoal/10 bg-zinc-900/30 p-4">
              <div className="flex gap-3 mb-2">
                <div className="font-mono text-xs text-red-400 bg-red-500/10 px-2 py-1 rounded flex-1">✗ {m.bad}</div>
              </div>
              <div className="flex gap-3 mb-3">
                <div className="font-mono text-xs text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded flex-1">✓ {m.good}</div>
              </div>
              <div className="text-zinc-400 text-xs">{m.explain}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Quiz ──────────────────────────────────────────────────────────── */}
      <section>
        <div className="mb-3"><span className="text-xs font-mono text-rose-400 uppercase tracking-widest">Quiz</span></div>
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
                  let style = 'border-charcoal/10 text-zinc-400 hover:border-white/20 hover:text-zinc-200';
                  if (revealed) {
                    if (correct) style = 'border-emerald-500/50 bg-emerald-500/10 text-emerald-300';
                    else if (chosen) style = 'border-red-500/50 bg-red-500/10 text-red-300';
                    else style = 'border-charcoal/10 text-zinc-600';
                  }
                  return (
                    <button key={ai} onClick={() => answer(qi, ai)} disabled={revealed}
                      className={`text-left px-3 py-2 rounded-lg border text-sm transition-all duration-150 ${style}`}>
                      <span className="font-mono text-xs opacity-50 mr-2">{String.fromCharCode(65 + ai)}.</span>
                      {opt}
                    </button>
                  );
                })}
              </div>
              {quizRevealed[qi] && (
                <motion.div initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }}
                  className="mt-3 px-3 py-2 rounded-lg bg-zinc-800/50 text-xs text-zinc-300 border border-charcoal/10">
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
