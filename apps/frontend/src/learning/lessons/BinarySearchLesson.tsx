import { useState } from 'react';
import { motion } from 'framer-motion';
import { BinarySearchVisualizer } from '../visualizations/BinarySearchVisualizer';

const QUIZ_QUESTIONS = [
  {
    q: 'Binary Search requires the array to be:',
    options: ['Filled with integers', 'Sorted', 'Unique values only', 'At least 10 elements'],
    correct: 1,
    explanation: 'Binary Search only works on sorted data — it makes decisions about which half to discard based on relative ordering. On unsorted data, results are undefined.',
  },
  {
    q: 'How many comparisons does Binary Search need to find an element in an array of 256 elements?',
    options: ['Up to 256', 'Up to 128', 'Up to 8', 'Exactly 1'],
    correct: 2,
    explanation: 'log₂(256) = 8. Binary Search halves the search space each step, so 256 → 128 → 64 → 32 → 16 → 8 → 4 → 2 → 1. At most 8 comparisons!',
  },
  {
    q: 'What is the correct mid-point formula to avoid integer overflow in most languages?',
    options: ['(low + high) / 2', '(low + high) >> 1', 'low + (high - low) / 2', 'high / 2'],
    correct: 2,
    explanation: '`low + (high - low) / 2` avoids overflow that can occur in C++/Java when low + high exceeds INT_MAX. In JavaScript this is less of an issue, but it\'s good practice.',
  },
];

export function BinarySearchLesson() {
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
        <h2 className="text-2xl font-bold text-white mb-4">The Divide & Conquer Power</h2>
        <p className="text-zinc-300 text-base leading-relaxed mb-4">
          Binary Search is the algorithmic equivalent of looking up a word in a dictionary. Instead of checking every page (linear search), you <strong className="text-white">open to the middle</strong>, decide which half contains your target, and repeat on only that half. Each step eliminates <em>half</em> of the remaining possibilities.
        </p>
        <div className="p-4 rounded-xl border border-cyan-500/20 bg-cyan-500/5 text-sm mb-5">
          <div className="text-cyan-300 font-medium mb-2">The key insight</div>
          <p className="text-zinc-300">
            If the array is sorted, <code className="text-cyan-300 bg-cyan-500/10 px-1 rounded">mid</code> tells us everything about both halves. If <code>target &gt; arr[mid]</code>, every element in the left half is also less than target — eliminate them all at once.
          </p>
        </div>

        {/* Algorithm steps */}
        <div className="space-y-2">
          {[
            { n: '1', label: 'Initialize', desc: 'Set low = 0, high = array.length - 1', code: 'low = 0, high = n - 1' },
            { n: '2', label: 'Find midpoint', desc: 'Calculate mid = ⌊(low + high) / 2⌋', code: 'mid = low + (high - low) / 2' },
            { n: '3', label: 'Compare', desc: 'Check if arr[mid] matches target', code: 'if arr[mid] === target → found!' },
            { n: '4', label: 'Eliminate half', desc: 'Discard the half that cannot contain target', code: 'if arr[mid] < target: low = mid + 1\nelse: high = mid - 1' },
            { n: '5', label: 'Repeat or fail', desc: 'Continue until found or low > high (not found)', code: 'while (low <= high)' },
          ].map((s) => (
            <div key={s.n} className="flex gap-4 rounded-xl border border-charcoal/10 bg-zinc-900/30 p-3.5 items-start">
              <div className="w-6 h-6 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-xs font-bold text-indigo-300 flex-shrink-0 mt-0.5">{s.n}</div>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-white text-sm">{s.label}</div>
                <div className="text-zinc-400 text-xs mt-0.5">{s.desc}</div>
              </div>
              <code className="font-mono text-xs text-indigo-300 bg-indigo-500/10 px-2 py-1 rounded whitespace-pre flex-shrink-0">{s.code}</code>
            </div>
          ))}
        </div>
      </section>

      {/* ── Visualization ─────────────────────────────────────────────────── */}
      <section>
        <div className="mb-3"><span className="text-xs font-mono text-amber-400 uppercase tracking-widest">Visualization</span></div>
        <h2 className="text-xl font-bold text-white mb-2">Watch the Elimination</h2>
        <p className="text-zinc-400 text-sm mb-5">
          Hit "Start Search" to see exactly which elements get eliminated each step. Notice how the active range shrinks by half each comparison.
        </p>
        <div className="rounded-xl border border-charcoal/10 bg-zinc-950/50 p-5">
          <BinarySearchVisualizer />
        </div>
      </section>

      {/* ── Implementation ────────────────────────────────────────────────── */}
      <section>
        <div className="mb-3"><span className="text-xs font-mono text-violet-400 uppercase tracking-widest">Implementation</span></div>
        <h2 className="text-xl font-bold text-white mb-5">Binary Search in Code</h2>
        <div className="space-y-4">
          <div className="rounded-xl border border-charcoal/10 bg-zinc-950/60 overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-charcoal/10 bg-zinc-900/40">
              <span className="text-xs text-zinc-400">Iterative (recommended)</span>
              <code className="text-xs font-mono text-cyan-400">O(log n)</code>
            </div>
            <pre className="p-4 text-xs font-mono text-zinc-300 overflow-x-auto leading-relaxed">{`function binarySearch(arr, target) {
  let low = 0, high = arr.length - 1;

  while (low <= high) {
    const mid = low + Math.floor((high - low) / 2);

    if (arr[mid] === target) return mid;       // found!
    if (arr[mid] < target)   low = mid + 1;   // search right half
    else                     high = mid - 1;  // search left half
  }

  return -1; // not found
}`}</pre>
          </div>

          <div className="rounded-xl border border-charcoal/10 bg-zinc-950/60 overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-charcoal/10 bg-zinc-900/40">
              <span className="text-xs text-zinc-400">Recursive version</span>
              <code className="text-xs font-mono text-violet-400">O(log n) time, O(log n) space</code>
            </div>
            <pre className="p-4 text-xs font-mono text-zinc-300 overflow-x-auto leading-relaxed">{`function binarySearchRecursive(arr, target, low = 0, high = arr.length - 1) {
  if (low > high) return -1; // base case: not found

  const mid = low + Math.floor((high - low) / 2);

  if (arr[mid] === target)    return mid;
  if (arr[mid] < target)      return binarySearchRecursive(arr, target, mid + 1, high);
  return binarySearchRecursive(arr, target, low, mid - 1);
}`}</pre>
          </div>
        </div>
      </section>

      {/* ── Complexity & Comparison ───────────────────────────────────────── */}
      <section>
        <div className="mb-3"><span className="text-xs font-mono text-cyan-400 uppercase tracking-widest">Complexity</span></div>
        <h2 className="text-xl font-bold text-white mb-5">Binary vs Linear Search</h2>
        <div className="overflow-x-auto mb-5">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-charcoal/10">
                <th className="text-left py-2 px-3 text-zinc-400 font-medium text-xs">Array Size</th>
                <th className="text-left py-2 px-3 text-zinc-400 font-medium text-xs">Linear Search (worst)</th>
                <th className="text-left py-2 px-3 text-zinc-400 font-medium text-xs text-cyan-400">Binary Search (worst)</th>
                <th className="text-left py-2 px-3 text-zinc-400 font-medium text-xs">Speedup</th>
              </tr>
            </thead>
            <tbody>
              {[
                { n: '100', lin: '100', bin: '7',  ratio: '14×' },
                { n: '1,000', lin: '1,000', bin: '10', ratio: '100×' },
                { n: '1,000,000', lin: '1,000,000', bin: '20', ratio: '50,000×' },
                { n: '1,000,000,000', lin: '1 billion', bin: '30', ratio: '33 million×' },
              ].map((row) => (
                <tr key={row.n} className="border-b border-charcoal/10">
                  <td className="py-2.5 px-3 text-zinc-300 font-mono text-xs">{row.n}</td>
                  <td className="py-2.5 px-3 text-orange-400 font-mono text-xs">{row.lin}</td>
                  <td className="py-2.5 px-3 text-cyan-400 font-mono text-xs font-bold">{row.bin}</td>
                  <td className="py-2.5 px-3 text-emerald-400 text-xs">{row.ratio}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="grid md:grid-cols-3 gap-3">
          {[
            { label: 'Best Case', val: 'O(1)', color: 'text-emerald-400', note: 'Target is the middle element' },
            { label: 'Worst Case', val: 'O(log n)', color: 'text-cyan-400', note: 'Target at edges or not present' },
            { label: 'Space', val: 'O(1)', color: 'text-indigo-400', note: 'Iterative version uses no extra space' },
          ].map((c) => (
            <div key={c.label} className="rounded-xl border border-charcoal/10 bg-zinc-900/30 p-4 text-center">
              <div className="text-zinc-500 text-xs mb-1">{c.label}</div>
              <div className={`font-mono font-bold text-2xl ${c.color} mb-1`}>{c.val}</div>
              <div className="text-zinc-500 text-xs">{c.note}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Real World ────────────────────────────────────────────────────── */}
      <section>
        <div className="mb-3"><span className="text-xs font-mono text-emerald-400 uppercase tracking-widest">Real World</span></div>
        <h2 className="text-xl font-bold text-white mb-5">Binary Search in the Wild</h2>
        <div className="grid md:grid-cols-2 gap-4">
          {[
            { title: 'Database Indexes', desc: "B-trees (the index structure behind PostgreSQL, MySQL, SQLite) use binary search internally to find rows in O(log n) instead of O(n) table scans." },
            { title: 'std::lower_bound', desc: "C++'s standard library, Java's Arrays.binarySearch, Python's bisect — all use binary search for sorted collections." },
            { title: 'Git bisect', desc: "git bisect uses binary search to find which commit introduced a bug. You get O(log n) commits to check instead of O(n)." },
            { title: 'Finding cutoffs', desc: 'Binary search on the answer: "what is the minimum speed to finish in time?" — a common interview and competitive programming pattern.' },
          ].map((item) => (
            <div key={item.title} className="rounded-xl border border-charcoal/10 bg-zinc-900/30 p-4">
              <div className="font-semibold text-white text-sm mb-2">{item.title}</div>
              <div className="text-zinc-400 text-xs leading-relaxed">{item.desc}</div>
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
