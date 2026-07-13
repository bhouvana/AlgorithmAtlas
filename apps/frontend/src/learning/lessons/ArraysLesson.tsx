import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

type ArrayOp = 'access' | 'search' | 'insert' | 'delete' | 'push';

const OPS: { id: ArrayOp; label: string; complexity: string; color: string; desc: string }[] = [
  { id: 'access', label: 'Access by index', complexity: 'O(1)', color: 'text-emerald-400', desc: 'Direct memory address calculation: base + index × elementSize. Instant!' },
  { id: 'search', label: 'Linear search',   complexity: 'O(n)', color: 'text-violet-400',  desc: 'Must check each element one by one until found. O(n) in worst case.' },
  { id: 'insert', label: 'Insert at front',  complexity: 'O(n)', color: 'text-orange-400',  desc: 'Every existing element must shift right by one position to make room.' },
  { id: 'push',   label: 'Append to end',   complexity: 'O(1)*', color: 'text-cyan-400',   desc: 'Amortized O(1) — usually instant, occasionally O(n) when array must grow.' },
  { id: 'delete', label: 'Delete from front',complexity: 'O(n)', color: 'text-rose-400',   desc: 'Every element after the deleted one must shift left by one position.' },
];

const QUIZ_QUESTIONS = [
  {
    q: 'Why is random access (arr[i]) O(1)?',
    options: ['The CPU searches through elements', 'Memory addresses are calculated directly', 'Arrays are always sorted', 'The OS pre-caches all values'],
    correct: 1,
    explanation: 'Arrays store elements in contiguous memory. Address of arr[i] = base_address + i × element_size — a single arithmetic operation regardless of i.',
  },
  {
    q: 'You need to frequently insert elements at the beginning. What should you use instead of an array?',
    options: ['A bigger array', 'A hash map', 'A linked list or deque', 'A binary tree'],
    correct: 2,
    explanation: 'Linked lists support O(1) front insertion (just update the head pointer). Arrays require O(n) shifting. Python\'s deque or C++\'s std::deque are better choices.',
  },
  {
    q: 'arr.push() in JavaScript is amortized O(1). What does "amortized" mean?',
    options: ['It is always O(1)', 'Occasionally O(n) but averages O(1) over many calls', 'It is O(n) in the worst case', 'It depends on the array size'],
    correct: 1,
    explanation: 'Dynamic arrays double their capacity when full (O(n) copy). But doublings are rare enough that averaging over many pushes, each push costs O(1) amortized.',
  },
];

function ArrayPlayground() {
  const [arr, setArr] = useState([3, 7, 1, 9, 4, 6]);
  const [highlighted, setHighlighted] = useState<number | null>(null);
  const [operation, setOperation] = useState<string>('');
  const [inputVal, setInputVal] = useState('');
  const [inputIdx, setInputIdx] = useState('');

  const flash = (idx: number | null, op: string) => {
    setHighlighted(idx);
    setOperation(op);
    setTimeout(() => setHighlighted(null), 1000);
  };

  const access = () => {
    const i = parseInt(inputIdx);
    if (isNaN(i) || i < 0 || i >= arr.length) { setOperation(`⚠️ Index ${inputIdx} out of bounds (0–${arr.length - 1})`); return; }
    flash(i, `arr[${i}] = ${arr[i]}`);
  };

  const search = () => {
    const v = parseInt(inputVal);
    const i = arr.indexOf(v);
    if (i === -1) { setOperation(`${v} not found after checking ${arr.length} elements`); return; }
    flash(i, `Found ${v} at index ${i} after ${i + 1} comparison${i === 0 ? '' : 's'}`);
  };

  const insertFront = () => {
    const v = parseInt(inputVal);
    if (isNaN(v)) { setOperation('Enter a number first'); return; }
    setArr([v, ...arr]);
    setOperation(`Inserted ${v} at front — all ${arr.length} elements shifted right → O(n)`);
  };

  const push = () => {
    const v = parseInt(inputVal);
    if (isNaN(v)) { setOperation('Enter a number first'); return; }
    setArr([...arr, v]);
    flash(arr.length, `Appended ${v} to end → O(1) amortized`);
  };

  const deleteFirst = () => {
    if (!arr.length) return;
    const removed = arr[0];
    setArr(arr.slice(1));
    setOperation(`Deleted ${removed} from front — ${arr.length - 1} elements shifted left → O(n)`);
  };

  const reset = () => { setArr([3, 7, 1, 9, 4, 6]); setOperation(''); setHighlighted(null); };

  return (
    <div className="rounded-xl border border-charcoal/10 bg-zinc-950/50 p-5 space-y-4">
      {/* Array display */}
      <div className="flex gap-2 flex-wrap items-end">
        <AnimatePresence mode="popLayout">
          {arr.map((val, i) => (
            <motion.div
              key={`${i}-${val}`}
              layout
              initial={{ opacity: 0, scale: 0.7, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.7, y: 10 }}
              transition={{ type: 'spring', stiffness: 300, damping: 24 }}
              className="flex flex-col items-center gap-1"
            >
              <motion.div
                animate={{ backgroundColor: highlighted === i ? 'rgba(99,102,241,0.3)' : 'rgba(39,39,42,0.6)' }}
                className={`w-12 h-12 rounded-lg flex items-center justify-center font-mono font-semibold text-sm border transition-colors duration-200 ${
                  highlighted === i ? 'border-indigo-500/60 text-indigo-200' : 'border-white/10 text-zinc-200'
                }`}
              >
                {val}
              </motion.div>
              <span className="text-[9px] text-zinc-600 font-mono">{i}</span>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Input row */}
      <div className="flex gap-2 flex-wrap">
        <input
          type="number" placeholder="Value" value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          className="w-20 px-2 py-1.5 bg-zinc-900 border border-white/10 rounded-lg text-white text-xs font-mono focus:outline-none focus:border-indigo-500/50"
        />
        <input
          type="number" placeholder="Index" value={inputIdx}
          onChange={(e) => setInputIdx(e.target.value)}
          className="w-20 px-2 py-1.5 bg-zinc-900 border border-white/10 rounded-lg text-white text-xs font-mono focus:outline-none focus:border-indigo-500/50"
        />
        <button onClick={access}     className="px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 rounded-lg text-xs hover:bg-emerald-500/20 transition-colors">Access[i]</button>
        <button onClick={search}     className="px-3 py-1.5 bg-violet-500/10 border border-violet-500/20 text-violet-300 rounded-lg text-xs hover:bg-violet-500/20 transition-colors">Search</button>
        <button onClick={insertFront} className="px-3 py-1.5 bg-orange-500/10 border border-orange-500/20 text-orange-300 rounded-lg text-xs hover:bg-orange-500/20 transition-colors">Insert Front</button>
        <button onClick={push}       className="px-3 py-1.5 bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 rounded-lg text-xs hover:bg-cyan-500/20 transition-colors">Push End</button>
        <button onClick={deleteFirst} className="px-3 py-1.5 bg-rose-500/10 border border-rose-500/20 text-rose-300 rounded-lg text-xs hover:bg-rose-500/20 transition-colors">Delete Front</button>
        <button onClick={reset}      className="px-3 py-1.5 border border-charcoal/10 text-zinc-400 rounded-lg text-xs hover:text-white transition-colors ml-auto">Reset</button>
      </div>

      {/* Operation output */}
      {operation && (
        <motion.div
          key={operation}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          className="px-3 py-2 rounded-lg bg-zinc-900/60 border border-charcoal/10 text-xs text-zinc-300 font-mono"
        >
          → {operation}
        </motion.div>
      )}
    </div>
  );
}

export function ArraysLesson() {
  const [activeOp, setActiveOp] = useState<ArrayOp | null>(null);
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
        <h2 className="text-2xl font-bold text-white mb-4">The Foundation of All Data Structures</h2>
        <p className="text-zinc-300 text-base leading-relaxed mb-4">
          Arrays are the simplest and most fundamental data structure. They store elements in <strong className="text-white">contiguous memory</strong> — each element is physically next to the previous one. This gives arrays their superpower: instant access to any element by index in <strong className="text-amber-300">O(1)</strong> time.
        </p>
        <p className="text-zinc-300 text-base leading-relaxed">
          Under the hood, arrays are a block of memory. Accessing <code className="text-indigo-300 bg-indigo-500/10 px-1 rounded">arr[5]</code> simply computes <code className="text-indigo-300 bg-indigo-500/10 px-1 rounded">base_address + 5 × 4 bytes</code> and reads directly. No searching, no traversal — pure arithmetic.
        </p>

        {/* Memory visualization */}
        <div className="mt-6 rounded-xl border border-charcoal/10 bg-zinc-950/60 p-5 overflow-x-auto">
          <div className="text-xs text-zinc-500 mb-3 font-mono">Memory layout (4 bytes each for 32-bit integers)</div>
          <div className="flex gap-0 min-w-max">
            {[42, 17, 83, 5, 61, 29].map((val, i) => (
              <div key={i} className="flex flex-col">
                <div className={`w-16 h-12 border border-zinc-700 flex items-center justify-center font-mono font-bold text-sm ${i === 0 ? 'rounded-l-lg' : ''} ${i === 5 ? 'rounded-r-lg' : ''} bg-zinc-900 text-zinc-200`}>
                  {val}
                </div>
                <div className="text-center text-[9px] text-zinc-500 font-mono mt-1">
                  {`0x${(0x1000 + i * 4).toString(16)}`}
                </div>
                <div className="text-center text-[9px] text-zinc-600 font-mono">
                  [{i}]
                </div>
              </div>
            ))}
          </div>
          <div className="mt-3 text-xs text-zinc-500">
            arr[3] → address = 0x1000 + 3 × 4 = <span className="text-indigo-400 font-mono">0x100C</span> → value = <span className="text-indigo-400 font-mono">5</span>
          </div>
        </div>
      </section>

      {/* ── Interactive Playground ────────────────────────────────────────── */}
      <section>
        <div className="mb-3"><span className="text-xs font-mono text-amber-400 uppercase tracking-widest">Playground</span></div>
        <h2 className="text-xl font-bold text-white mb-2">Try Array Operations</h2>
        <p className="text-zinc-400 text-sm mb-5">
          Interact with a live array. Notice which operations animate all elements shifting (O(n)) versus those that change only one position (O(1)).
        </p>
        <ArrayPlayground />
      </section>

      {/* ── Operation Complexity ──────────────────────────────────────────── */}
      <section>
        <div className="mb-3"><span className="text-xs font-mono text-violet-400 uppercase tracking-widest">Complexity Explorer</span></div>
        <h2 className="text-xl font-bold text-white mb-4">Operation Complexity</h2>
        <p className="text-zinc-400 text-sm mb-5">Click any operation to learn why it has that complexity.</p>
        <div className="space-y-2">
          {OPS.map((op) => (
            <motion.button
              key={op.id}
              onClick={() => setActiveOp(activeOp === op.id ? null : op.id)}
              className={`w-full text-left rounded-xl border p-4 transition-all duration-200 ${
                activeOp === op.id ? 'border-indigo-500/40 bg-indigo-500/8' : 'border-white/8 bg-zinc-900/30 hover:bg-zinc-900/50'
              }`}
              layout
            >
              <div className="flex items-center justify-between">
                <span className="text-zinc-300 text-sm">{op.label}</span>
                <code className={`font-mono font-bold ${op.color}`}>{op.complexity}</code>
              </div>
              <AnimatePresence>
                {activeOp === op.id && (
                  <motion.p
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="text-zinc-400 text-xs mt-3 pt-3 border-t border-white/8"
                  >
                    {op.desc}
                  </motion.p>
                )}
              </AnimatePresence>
            </motion.button>
          ))}
        </div>
      </section>

      {/* ── When to Use ───────────────────────────────────────────────────── */}
      <section>
        <div className="mb-3"><span className="text-xs font-mono text-emerald-400 uppercase tracking-widest">Decision Guide</span></div>
        <h2 className="text-xl font-bold text-white mb-5">Array vs Alternatives</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-white/8">
                <th className="text-left py-2 px-3 text-zinc-400 font-medium">Use case</th>
                <th className="text-left py-2 px-3 text-zinc-400 font-medium">Best choice</th>
                <th className="text-left py-2 px-3 text-zinc-400 font-medium">Why</th>
              </tr>
            </thead>
            <tbody>
              {[
                { use: 'Frequent random access', best: '✓ Array', why: 'O(1) index access is unbeatable' },
                { use: 'Frequent front insertions', best: '✗ Array → Deque/LinkedList', why: 'O(n) shifting; use O(1) front insert structures' },
                { use: 'Fixed size known upfront', best: '✓ Array', why: 'Minimal overhead, cache-friendly' },
                { use: 'Key-value lookup', best: '✗ Array → HashMap', why: 'O(n) search vs O(1) hash lookup' },
                { use: 'Stack (LIFO)', best: '✓ Array with push/pop', why: 'push/pop are both O(1) amortized' },
                { use: 'Queue (FIFO)', best: '✗ Array → Deque', why: 'dequeue from front is O(n) in arrays' },
              ].map((row) => (
                <tr key={row.use} className="border-b border-white/5">
                  <td className="py-2.5 px-3 text-zinc-300">{row.use}</td>
                  <td className="py-2.5 px-3">
                    <span className={row.best.startsWith('✓') ? 'text-emerald-400' : 'text-rose-400'}>{row.best}</span>
                  </td>
                  <td className="py-2.5 px-3 text-zinc-400">{row.why}</td>
                </tr>
              ))}
            </tbody>
          </table>
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
                  let style = 'border-white/10 text-zinc-400 hover:border-white/20 hover:text-zinc-200';
                  if (revealed) {
                    if (correct) style = 'border-emerald-500/50 bg-emerald-500/10 text-emerald-300';
                    else if (chosen) style = 'border-red-500/50 bg-red-500/10 text-red-300';
                    else style = 'border-white/5 text-zinc-600';
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
