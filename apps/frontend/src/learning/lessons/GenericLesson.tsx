import { useState } from 'react';
import { motion } from 'framer-motion';
import { SimulationCanvas } from '../../simulation/SimulationCanvas';
import { SimulationControls } from '../../simulation/SimulationControls';
import type { VisualizationType } from '../../visualization/RendererRegistry';

export interface LessonStep {
  n: string;
  label: string;
  desc: string;
  code?: string;
}

export interface CodeExample {
  label: string;
  code: string;
  complexity?: string;
  variant?: 'default' | 'good' | 'warn';
}

export interface ComplexityRow {
  case: string;
  value: string;
  color: string;
  note: string;
}

export interface RealWorldItem {
  title: string;
  desc: string;
}

export interface MistakeItem {
  wrong: string;
  right?: string;
  explain: string;
}

export interface QuizQuestion {
  q: string;
  options: string[];
  correct: number;
  explanation: string;
}

export interface LessonData {
  concept: {
    overview: string;
    keyPoints?: Array<{ title: string; desc: string; code?: string }>;
  };
  steps?: LessonStep[];
  codeExamples?: CodeExample[];
  complexity?: {
    rows: ComplexityRow[];
    note?: string;
  };
  realWorld?: RealWorldItem[];
  commonMistakes?: MistakeItem[];
  quiz: QuizQuestion[];
}

// ── Catalog map: lesson ID → existing algorithm plugin ───────────────────────
interface CatalogEntry {
  slug: string;
  vizType: VisualizationType;
  target: 'server' | 'wasm' | 'both';
}

const CATALOG_MAP: Record<string, CatalogEntry> = {
  // Foundations — conceptual lessons use bubble-sort / bfs / bfs as illustrative demos
  'what-is-an-algorithm':  { slug: 'bubble-sort',                    vizType: 'ARRAY_BARS',        target: 'wasm'   },
  'big-o-notation':        { slug: 'bubble-sort',                    vizType: 'ARRAY_BARS',        target: 'wasm'   },
  'time-vs-space':         { slug: 'merge-sort',                     vizType: 'ARRAY_BARS',        target: 'wasm'   },
  'arrays':                { slug: 'bubble-sort',                    vizType: 'ARRAY_BARS',        target: 'wasm'   },
  'linked-lists':          { slug: 'linked-list',                    vizType: 'ARRAY_BARS',        target: 'server' },
  'stacks':                { slug: 'dfs',                            vizType: 'GRAPH',             target: 'server' },
  'queues':                { slug: 'bfs',                            vizType: 'GRAPH',             target: 'server' },
  'hash-tables':           { slug: 'hash-table-chaining',            vizType: 'ARRAY_BARS',        target: 'server' },
  'strings':               { slug: 'z-algorithm',                    vizType: 'ARRAY_BARS_SEARCH', target: 'server' },
  // Custom lessons (previously LESSON_MAP — now use catalog viz)
  'bubble-sort':           { slug: 'bubble-sort',                    vizType: 'ARRAY_BARS',        target: 'wasm'   },
  'binary-search':         { slug: 'binary-search',                  vizType: 'ARRAY_BARS_SEARCH', target: 'server' },
  // Sorting
  'selection-sort':        { slug: 'selection-sort',                 vizType: 'ARRAY_BARS',        target: 'wasm'   },
  'insertion-sort':        { slug: 'insertion-sort',                 vizType: 'ARRAY_BARS',        target: 'wasm'   },
  'merge-sort':            { slug: 'merge-sort',                     vizType: 'ARRAY_BARS',        target: 'wasm'   },
  'quick-sort':            { slug: 'quick-sort',                     vizType: 'ARRAY_BARS',        target: 'wasm'   },
  'heap-sort':             { slug: 'heap-sort',                      vizType: 'ARRAY_BARS',        target: 'server' },
  'counting-sort':         { slug: 'counting-sort',                  vizType: 'ARRAY_BARS',        target: 'server' },
  'radix-sort':            { slug: 'radix-sort',                     vizType: 'ARRAY_BARS',        target: 'server' },
  // Searching
  'linear-search':         { slug: 'linear-search',                  vizType: 'ARRAY_BARS_SEARCH', target: 'server' },
  'ternary-search':        { slug: 'ternary-search',                 vizType: 'ARRAY_BARS_SEARCH', target: 'server' },
  'interpolation-search':  { slug: 'interpolation-search',           vizType: 'ARRAY_BARS_SEARCH', target: 'server' },
  // Trees
  'binary-trees':          { slug: 'inorder',                        vizType: 'TREE',              target: 'server' },
  'binary-search-trees':   { slug: 'bst-search',                    vizType: 'TREE',              target: 'server' },
  'avl-trees':             { slug: 'avl-tree',                       vizType: 'TREE',              target: 'server' },
  'heaps':                 { slug: 'binary-heap',                    vizType: 'TREE',              target: 'server' },
  'tries':                 { slug: 'trie',                           vizType: 'TREE',              target: 'server' },
  'segment-trees':         { slug: 'segment-tree',                   vizType: 'MATRIX',            target: 'server' },
  'fenwick-trees':         { slug: 'fenwick-tree',                   vizType: 'MATRIX',            target: 'server' },
  // Graphs
  'graph-representation':  { slug: 'bfs',                            vizType: 'GRAPH',             target: 'server' },
  'bfs':                   { slug: 'bfs',                            vizType: 'GRAPH',             target: 'server' },
  'dfs':                   { slug: 'dfs',                            vizType: 'GRAPH',             target: 'server' },
  'topological-sort':      { slug: 'topological-sort',               vizType: 'GRAPH',             target: 'server' },
  'dijkstra':              { slug: 'dijkstra',                       vizType: 'GRAPH',             target: 'server' },
  'bellman-ford':          { slug: 'bellman-ford',                   vizType: 'GRAPH',             target: 'server' },
  'floyd-warshall':        { slug: 'floyd-warshall',                 vizType: 'MATRIX',            target: 'server' },
  'minimum-spanning-tree': { slug: 'kruskals-mst',                   vizType: 'GRAPH',             target: 'server' },
  'union-find':            { slug: 'kruskals-mst',                   vizType: 'GRAPH',             target: 'server' },
  // Dynamic Programming
  'memoization':           { slug: 'fibonacci-dp',                   vizType: 'MATRIX',            target: 'server' },
  'tabulation':            { slug: 'staircase',                      vizType: 'MATRIX',            target: 'server' },
  'knapsack':              { slug: 'knapsack-01',                    vizType: 'MATRIX',            target: 'server' },
  'lcs':                   { slug: 'longest-common-subsequence',     vizType: 'MATRIX',            target: 'server' },
  'edit-distance':         { slug: 'edit-distance',                  vizType: 'MATRIX',            target: 'server' },
  'lis':                   { slug: 'longest-increasing-subsequence', vizType: 'MATRIX',            target: 'server' },
  // Greedy
  'activity-selection':    { slug: 'activity-selection',             vizType: 'ARRAY_BARS',        target: 'server' },
  'huffman-coding':        { slug: 'huffman-coding',                 vizType: 'ARRAY_BARS',        target: 'server' },
  'fractional-knapsack':   { slug: 'fractional-knapsack',           vizType: 'ARRAY_BARS',        target: 'server' },
  // Backtracking
  'n-queens':              { slug: 'n-queens',                       vizType: 'GRID',              target: 'server' },
  'sudoku':                { slug: 'sudoku-solver',                  vizType: 'MATRIX',            target: 'server' },
  'permutations':          { slug: 'permutations',                   vizType: 'ARRAY_BARS',        target: 'server' },
  // Advanced Strings / Patterns
  'kmp':                   { slug: 'kmp',                            vizType: 'ARRAY_BARS_SEARCH', target: 'server' },
  'rabin-karp':            { slug: 'rabin-karp',                    vizType: 'ARRAY_BARS_SEARCH', target: 'server' },
  // Advanced Graph
  'network-flow':          { slug: 'ford-fulkerson',                 vizType: 'GRAPH',             target: 'server' },
  'suffix-arrays':         { slug: 'suffix-array',                   vizType: 'MATRIX',            target: 'server' },
};

// ── Shared quiz renderer ─────────────────────────────────────────────────────
function Quiz({ questions }: { questions: QuizQuestion[] }) {
  const [answers, setAnswers] = useState<(number | null)[]>(questions.map(() => null));

  const pick = (qi: number, ai: number) => {
    if (answers[qi] !== null) return;
    setAnswers((prev) => { const n = [...prev]; n[qi] = ai; return n; });
  };

  return (
    <div className="space-y-6">
      {questions.map((q, qi) => (
        <div key={qi} className="rounded-xl border border-white/8 bg-zinc-900/30 p-5">
          <div className="font-medium text-white mb-4 text-sm">{q.q}</div>
          <div className="grid grid-cols-2 gap-2">
            {q.options.map((opt, ai) => {
              const chosen = answers[qi] === ai;
              const revealed = answers[qi] !== null;
              const correct = ai === q.correct;
              let style = 'border-white/10 text-zinc-400 hover:border-white/20 hover:text-zinc-200';
              if (revealed) {
                if (correct) style = 'border-emerald-500/50 bg-emerald-500/10 text-emerald-300';
                else if (chosen) style = 'border-red-500/50 bg-red-500/10 text-red-300';
                else style = 'border-white/5 text-zinc-600';
              }
              return (
                <button key={ai} onClick={() => pick(qi, ai)} disabled={revealed}
                  className={`text-left px-3 py-2 rounded-lg border text-sm transition-all duration-150 ${style}`}>
                  <span className="font-mono text-xs opacity-50 mr-2">{String.fromCharCode(65 + ai)}.</span>
                  {opt}
                </button>
              );
            })}
          </div>
          {answers[qi] !== null && (
            <motion.div initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }}
              className="mt-3 px-3 py-2 rounded-lg bg-zinc-800/50 text-xs text-zinc-300 border border-white/5">
              💡 {q.explanation}
            </motion.div>
          )}
        </div>
      ))}
    </div>
  );
}

// ── Section renderers ────────────────────────────────────────────────────────
function ConceptSection({ data }: { data: LessonData }) {
  return (
    <div className="space-y-6">
      <p className="text-zinc-300 text-base leading-relaxed whitespace-pre-line">{data.concept.overview}</p>
      {data.concept.keyPoints && (
        <div className="grid md:grid-cols-3 gap-3">
          {data.concept.keyPoints.map((kp) => (
            <div key={kp.title} className="rounded-xl border border-white/8 bg-zinc-900/40 p-4">
              <div className="font-semibold text-white text-sm mb-1">{kp.title}</div>
              {kp.code && <div className="font-mono text-indigo-300 text-sm mb-2">{kp.code}</div>}
              <div className="text-zinc-400 text-xs">{kp.desc}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function VisualizationSection({
  lessonId,
  data,
  openSteps,
  toggleStep,
}: {
  lessonId?: string;
  data: LessonData;
  openSteps: Set<string>;
  toggleStep: (key: string) => void;
}) {
  const catalog = lessonId ? CATALOG_MAP[lessonId] : undefined;

  if (catalog) {
    return (
      <div className="space-y-4">
        <div className="mb-2">
          <span className="text-xs font-mono text-amber-400 uppercase tracking-widest">Interactive Visualization</span>
        </div>
        <div className="rounded-xl border border-white/8 bg-zinc-950/60 overflow-hidden">
          <SimulationCanvas
            algorithmSlug={catalog.slug}
            visualizationType={catalog.vizType}
            executionTarget={catalog.target}
            seed={42}
            params={{}}
          />
        </div>
        <SimulationControls />
        {data.steps && data.steps.length > 0 && (
          <div className="mt-8 space-y-2">
            <div className="mb-4">
              <span className="text-xs font-mono text-zinc-500 uppercase tracking-widest">Step-by-step Breakdown</span>
            </div>
            {data.steps.map((s) => (
              <motion.button
                key={s.n}
                onClick={() => toggleStep(s.n)}
                className="w-full text-left rounded-xl border border-white/8 bg-zinc-900/30 hover:bg-zinc-900/50 p-4 transition-all duration-150"
                layout
              >
                <div className="flex items-start gap-4">
                  <div className="w-6 h-6 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-xs font-bold text-indigo-300 flex-shrink-0 mt-0.5">{s.n}</div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-white text-sm">{s.label}</div>
                    {openSteps.has(s.n) && (
                      <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}
                        className="text-zinc-400 text-xs mt-2">
                        {s.desc}
                        {s.code && (
                          <code className="block mt-2 font-mono text-indigo-300 bg-indigo-500/10 px-2 py-1 rounded">{s.code}</code>
                        )}
                      </motion.div>
                    )}
                  </div>
                  <span className="text-zinc-600 text-xs">{openSteps.has(s.n) ? '▲' : '▼'}</span>
                </div>
              </motion.button>
            ))}
          </div>
        )}
      </div>
    );
  }

  // Fallback: steps accordion only
  if (!data.steps || data.steps.length === 0) {
    return <p className="text-zinc-500 text-sm py-12 text-center">No step-by-step breakdown available for this lesson.</p>;
  }
  return (
    <div className="space-y-2">
      <div className="mb-4"><span className="text-xs font-mono text-amber-400 uppercase tracking-widest">How It Works</span></div>
      {data.steps.map((s) => (
        <motion.button
          key={s.n}
          onClick={() => toggleStep(s.n)}
          className="w-full text-left rounded-xl border border-white/8 bg-zinc-900/30 hover:bg-zinc-900/50 p-4 transition-all duration-150"
          layout
        >
          <div className="flex items-start gap-4">
            <div className="w-6 h-6 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-xs font-bold text-indigo-300 flex-shrink-0 mt-0.5">{s.n}</div>
            <div className="flex-1 min-w-0">
              <div className="font-medium text-white text-sm">{s.label}</div>
              {openSteps.has(s.n) && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}
                  className="text-zinc-400 text-xs mt-2">
                  {s.desc}
                  {s.code && (
                    <code className="block mt-2 font-mono text-indigo-300 bg-indigo-500/10 px-2 py-1 rounded">{s.code}</code>
                  )}
                </motion.div>
              )}
            </div>
            <span className="text-zinc-600 text-xs">{openSteps.has(s.n) ? '▲' : '▼'}</span>
          </div>
        </motion.button>
      ))}
    </div>
  );
}

function ExamplesSection({ data }: { data: LessonData }) {
  if (!data.codeExamples || data.codeExamples.length === 0) {
    return <p className="text-zinc-500 text-sm py-12 text-center">No code examples available for this lesson.</p>;
  }
  return (
    <div className="space-y-4">
      <div className="mb-4"><span className="text-xs font-mono text-violet-400 uppercase tracking-widest">Implementation</span></div>
      {data.codeExamples.map((ex, i) => {
        const borderColor = ex.variant === 'good' ? 'border-emerald-500/20' : ex.variant === 'warn' ? 'border-amber-500/20' : 'border-white/8';
        const headerBg   = ex.variant === 'good' ? 'bg-emerald-500/5'      : ex.variant === 'warn' ? 'bg-amber-500/5'      : 'bg-zinc-900/40';
        const complexityColor = ex.complexity?.startsWith('O(1)') ? 'text-emerald-400'
          : ex.complexity?.includes('log') ? 'text-cyan-400'
          : ex.complexity?.includes('²') || ex.complexity?.includes('n²') ? 'text-orange-400'
          : 'text-violet-400';
        return (
          <div key={i} className={`rounded-xl border ${borderColor} bg-zinc-950/60 overflow-hidden`}>
            <div className={`flex items-center justify-between px-4 py-2 border-b border-white/5 ${headerBg}`}>
              <span className="text-xs text-zinc-400">{ex.label}</span>
              {ex.complexity && <code className={`text-xs font-mono font-bold ${complexityColor}`}>{ex.complexity}</code>}
            </div>
            <pre className="p-4 text-xs font-mono text-zinc-300 overflow-x-auto leading-relaxed">{ex.code}</pre>
          </div>
        );
      })}
    </div>
  );
}

function ComplexitySection({ data }: { data: LessonData }) {
  return (
    <div className="space-y-10">
      {data.complexity ? (
        <div>
          <div className="mb-4"><span className="text-xs font-mono text-cyan-400 uppercase tracking-widest">Complexity</span></div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/8">
                  <th className="text-left py-2 px-3 text-zinc-400 font-medium text-xs">Case</th>
                  <th className="text-left py-2 px-3 text-zinc-400 font-medium text-xs">Complexity</th>
                  <th className="text-left py-2 px-3 text-zinc-400 font-medium text-xs">When / Why</th>
                </tr>
              </thead>
              <tbody>
                {data.complexity.rows.map((row) => (
                  <tr key={row.case} className="border-b border-white/5">
                    <td className="py-2.5 px-3 text-zinc-300 font-medium text-xs">{row.case}</td>
                    <td className="py-2.5 px-3"><code className={`font-mono font-bold text-sm ${row.color}`}>{row.value}</code></td>
                    <td className="py-2.5 px-3 text-zinc-400 text-xs">{row.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {data.complexity.note && (
            <div className="mt-3 px-4 py-3 rounded-xl border border-indigo-500/20 bg-indigo-500/5 text-xs text-zinc-300">
              {data.complexity.note}
            </div>
          )}
        </div>
      ) : (
        <p className="text-zinc-500 text-sm py-12 text-center">No complexity analysis available for this lesson.</p>
      )}

      {data.realWorld && data.realWorld.length > 0 && (
        <div>
          <div className="mb-4"><span className="text-xs font-mono text-emerald-400 uppercase tracking-widest">Real World</span></div>
          <div className="grid md:grid-cols-2 gap-4">
            {data.realWorld.map((item) => (
              <div key={item.title} className="rounded-xl border border-white/8 bg-zinc-900/30 p-4">
                <div className="font-semibold text-white text-sm mb-2">{item.title}</div>
                <div className="text-zinc-400 text-xs leading-relaxed">{item.desc}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {data.commonMistakes && data.commonMistakes.length > 0 && (
        <div>
          <div className="mb-4"><span className="text-xs font-mono text-rose-400 uppercase tracking-widest">Common Mistakes</span></div>
          <div className="space-y-3">
            {data.commonMistakes.map((m, i) => (
              <div key={i} className="rounded-xl border border-white/8 bg-zinc-900/30 p-4">
                <div className="flex gap-2 items-start mb-2">
                  <span className="text-red-400 text-xs mt-0.5">✗</span>
                  <code className="font-mono text-xs text-red-300 bg-red-500/10 px-1.5 py-0.5 rounded">{m.wrong}</code>
                </div>
                {m.right && (
                  <div className="flex gap-2 items-start mb-2">
                    <span className="text-emerald-400 text-xs mt-0.5">✓</span>
                    <code className="font-mono text-xs text-emerald-300 bg-emerald-500/10 px-1.5 py-0.5 rounded">{m.right}</code>
                  </div>
                )}
                <div className="text-zinc-400 text-xs mt-1">{m.explain}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Main GenericLesson renderer ──────────────────────────────────────────────
export function GenericLesson({
  data,
  activeSection = 0,
  lessonId,
}: {
  data: LessonData;
  activeSection?: number;
  lessonId?: string;
}) {
  const [openSteps, setOpenSteps] = useState<Set<string>>(new Set());

  const toggleStep = (key: string) =>
    setOpenSteps((prev) => {
      const next = new Set(prev);
      next.has(key) ? next.delete(key) : next.add(key);
      return next;
    });

  return (
    <motion.div
      key={activeSection}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      {activeSection === 0 && <ConceptSection data={data} />}
      {activeSection === 1 && (
        <VisualizationSection
          lessonId={lessonId}
          data={data}
          openSteps={openSteps}
          toggleStep={toggleStep}
        />
      )}
      {activeSection === 2 && <ExamplesSection data={data} />}
      {activeSection === 3 && <ComplexitySection data={data} />}
      {activeSection === 4 && (
        <div>
          <div className="mb-4"><span className="text-xs font-mono text-rose-400 uppercase tracking-widest">Quiz</span></div>
          <h2 className="text-xl font-bold text-white mb-6">Test Your Understanding</h2>
          <Quiz questions={data.quiz} />
        </div>
      )}
    </motion.div>
  );
}
