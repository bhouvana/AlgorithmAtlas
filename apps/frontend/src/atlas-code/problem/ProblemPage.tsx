import { useEffect, useRef, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import MonacoEditor from '@monaco-editor/react';
import {
  ChevronLeft, Play, Lightbulb, RotateCcw,
  Clock, Zap, Eye, EyeOff, ChevronDown,
} from 'lucide-react';
import { getProblem, getHints, runProblem, supportsFunctionMode } from '../api/problems';
import type { ExecutionMode, HintOut, ProblemDetail } from '../api/problems';
import { useAtlasCodeStore } from '../store/atlasCodeStore';
import { useAtlasStore } from '../../ai/store';
import { cn } from '../../lib/utils';
import { BottomConsole } from './console/BottomConsole';
import type { RunSpec } from './console/types';
import { useResizeDrag } from './useResizeDrag';
import { ALL_LANGUAGES } from '../languages';

// ── Custom language dropdown -- matches the Notebook's LangPicker pattern
// (dark grey, rounded, devicon logos) rather than a native <select>, which
// can't be restyled past its closed-state appearance in most browsers.
function LangPicker({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const current = ALL_LANGUAGES.find((l) => l.value === value) ?? ALL_LANGUAGES[0];

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#1A1A2A] border border-charcoal/10 hover:border-white/20 transition-colors text-sm"
      >
        <i className={cn(current.devicon, 'text-base leading-none')} />
        <span className="text-white font-medium">{current.label}</span>
        <ChevronDown className={cn('w-3.5 h-3.5 text-zinc-500 transition-transform', open && 'rotate-180')} />
      </button>

      {open && (
        <div className="absolute top-full mt-1 right-0 z-40 w-48 max-h-80 overflow-y-auto rounded-xl bg-[#1A1A2E] border border-charcoal/10 shadow-[0_8px_32px_rgba(0,0,0,0.5)] py-1">
          {ALL_LANGUAGES.map((l) => (
            <button
              key={l.value}
              onClick={() => { onChange(l.value); setOpen(false); }}
              className={cn(
                'w-full flex items-center gap-2.5 px-3 py-2 text-sm transition-colors hover:bg-white/5',
                l.value === current.value ? 'text-white' : 'text-zinc-400 hover:text-white',
              )}
            >
              <i className={cn(l.devicon, 'text-base leading-none flex-shrink-0')} />
              <span>{l.label}</span>
              {l.value === current.value && <span className="ml-auto text-indigo-400">✓</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Dual-mode Run toggle ──────────────────────────────────────────────────────
// A professional segmented control, not a checkbox or a vendor-styled switch
// (Phase 1). "Function" is disabled (never silently swapped to Program) when
// the problem/language combination has no function_contract yet -- an honest
// per-problem support boundary (Phase 22), not a fake universal claim.
function ModeToggle({
  problem, language, value, onChange,
}: {
  problem: ProblemDetail; language: string; value: ExecutionMode; onChange: (m: ExecutionMode) => void;
}) {
  // Display names only -- internal ExecutionMode keys stay 'function'/'program'
  // (DB column, API contract, localStorage keys all reference these values;
  // see apps/backend/algorithm_atlas/api/v1/problems.py's naming-decision note).
  const functionSupported = supportsFunctionMode(problem, language);
  const options: { key: ExecutionMode; label: string; tooltip: string; disabled?: boolean }[] = [
    {
      key: 'function',
      label: 'LeetCode Mode',
      tooltip: functionSupported
        ? 'Write only the requested function. AtlasCode handles testcase parsing, function invocation, and result formatting.'
        : `LeetCode Mode isn't available for this problem in ${language} yet -- use Codeforces Mode.`,
      disabled: !functionSupported,
    },
    {
      key: 'program',
      label: 'Codeforces Mode',
      tooltip: 'Write a complete program. Read from standard input and write to standard output.',
    },
  ];

  return (
    <div className="flex items-center rounded-lg border border-charcoal/10 bg-[#1A1A2A] p-0.5">
      {options.map((opt) => (
        <button
          key={opt.key}
          onClick={() => !opt.disabled && onChange(opt.key)}
          disabled={opt.disabled}
          title={opt.tooltip}
          className={cn(
            'px-3 py-1 text-sm font-medium rounded-md transition-colors',
            value === opt.key
              ? 'bg-indigo-600 text-white'
              : opt.disabled
                ? 'text-zinc-700 cursor-not-allowed'
                : 'text-zinc-400 hover:text-white'
          )}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

const MONACO_LANG: Record<string, string> = {
  python: 'python', javascript: 'javascript', typescript: 'typescript',
  cpp: 'cpp', c: 'c', java: 'java', go: 'go', rust: 'rust',
  shell: 'shell', ruby: 'ruby', kotlin: 'kotlin', swift: 'swift',
  r: 'r', csharp: 'csharp', php: 'php', scala: 'scala', perl: 'perl',
};

const DIFF_COLOR: Record<string, string> = {
  Easy: 'text-emerald-400', Medium: 'text-amber-400', Hard: 'text-rose-400',
};

function HintPanel({ hints, revealedLevel, onReveal }: {
  hints: HintOut[];
  revealedLevel: number;
  onReveal: () => void;
}) {
  const available = hints.filter((h) => h.level <= revealedLevel);
  const canReveal = revealedLevel < hints.length;

  return (
    <div className="space-y-2">
      {available.map((h) => (
        <motion.div
          key={h.level}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-amber-500/5 border border-amber-500/15 rounded-xl px-3 py-2.5"
        >
          <div className="text-xs text-amber-400 font-medium mb-1">Hint {h.level}</div>
          <div className="text-sm text-zinc-300">{h.text}</div>
        </motion.div>
      ))}
      {canReveal ? (
        <button
          onClick={onReveal}
          className="w-full flex items-center justify-center gap-2 py-2 rounded-xl border border-amber-500/20 text-amber-400 text-xs hover:bg-amber-500/5 transition-colors"
        >
          <Lightbulb className="w-3.5 h-3.5" />
          {revealedLevel === 0 ? 'Show First Hint' : 'Next Hint'}
        </button>
      ) : (
        <div className="text-center text-xs text-zinc-600 py-1">No more hints available</div>
      )}
    </div>
  );
}

export function ProblemPage() {
  const { slug } = useParams<{ slug: string }>();
  const {
    currentProblem, currentLanguage, executionMode, editorCode,
    isRunning, lastRunResult, revealedHintLevel,
    problemPaneWidthPx, consoleCollapsed, consoleHeightPct,
    setProblem, setLanguage, setExecutionMode, setCode,
    setRunning, setLastRunResult, revealNextHint,
    adjustProblemPaneWidthPx, adjustConsoleHeightPct, setConsoleTab,
  } = useAtlasCodeStore();
  const setProblemBridge = useAtlasStore((s) => s.setProblemBridge);

  const [loading, setLoading] = useState(true);
  const [hints, setHints] = useState<HintOut[]>([]);
  const [showStatement, setShowStatement] = useState(true);
  const [showHints, setShowHints] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);

  const editorRef = useRef<{ layout: () => void } | null>(null);
  const workspaceRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    getProblem(slug).then(setProblem).finally(() => setLoading(false));
    getHints(slug, 7).then(setHints).catch(() => {});
  }, [slug, setProblem]);

  const problem = currentProblem?.id === slug ? currentProblem : null;

  const handleRun = useCallback(async (spec: RunSpec) => {
    if (!problem || isRunning) return;
    setRunning(true);
    setRunError(null);
    try {
      const base = { language: currentLanguage, code: editorCode, execution_mode: executionMode };
      const body =
        spec.mode === 'visible' ? { ...base, mode: 'visible' as const }
          : spec.mode === 'selected' ? { ...base, mode: 'selected' as const, case_indices: spec.indices }
            : { ...base, mode: 'custom' as const, custom_cases: spec.cases };
      const result = await runProblem(problem.id, body);
      setLastRunResult(result);
      setConsoleTab('result');
    } catch (e) {
      setRunError(e instanceof Error ? e.message : 'Run failed');
      setConsoleTab('console');
    } finally {
      setRunning(false);
    }
  }, [problem, isRunning, currentLanguage, executionMode, editorCode, setRunning, setLastRunResult, setConsoleTab]);

  const handleRunAllVisible = useCallback(() => handleRun({ mode: 'visible' }), [handleRun]);

  // Keyboard shortcuts: Ctrl/Cmd+Enter = Run, Alt+1/2/3 = switch console tabs.
  // Checked against Monaco's own bindings (word navigation, multi-cursor,
  // etc.) -- none of these combinations collide with Monaco defaults.
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const mod = e.ctrlKey || e.metaKey;
      if (mod && e.key === 'Enter') {
        e.preventDefault();
        handleRunAllVisible();
      } else if (e.altKey && e.key === '1') {
        setConsoleTab('testcase');
      } else if (e.altKey && e.key === '2') {
        setConsoleTab('result');
      } else if (e.altKey && e.key === '3') {
        setConsoleTab('console');
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [handleRunAllVisible, setConsoleTab]);

  const onVerticalDividerDown = useResizeDrag(adjustProblemPaneWidthPx, 'x');
  const onConsoleResizeDeltaY = useCallback(
    (deltaY: number) => {
      const total = workspaceRef.current?.getBoundingClientRect().height ?? 800;
      adjustConsoleHeightPct(-(deltaY / total) * 100);
    },
    [adjustConsoleHeightPct]
  );

  // Atlas AI problem context bridge. Derived entirely from Run (visible/
  // selected/custom cases) -- this workspace has no Submit/hidden-test path,
  // so there is structurally no hidden data this could ever leak.
  useEffect(() => {
    if (!currentProblem) return;
    const firstFailing = lastRunResult?.cases.find((c) => c.has_expected && c.status === 'failed');
    const contract = currentProblem.function_contract;
    setProblemBridge({
      slug: currentProblem.id,
      title: currentProblem.title,
      difficulty: currentProblem.difficulty,
      language: currentLanguage,
      executionMode,
      functionSignature: executionMode === 'function' && contract
        ? `${contract.function_name}(${contract.parameters.map((p) => p.name).join(', ')})`
        : null,
      source: editorCode,
      lastRunSummary: lastRunResult
        ? { passed: lastRunResult.summary.passed, failed: lastRunResult.summary.failed, total: lastRunResult.summary.total }
        : null,
      lastRunVerdict: lastRunResult?.compile_output ? 'Compilation Error' : null,
      firstFailingCase: firstFailing
        ? executionMode === 'function'
          ? {
              label: firstFailing.label,
              input: JSON.stringify(firstFailing.arguments ?? {}),
              expected: firstFailing.expected_return !== undefined ? JSON.stringify(firstFailing.expected_return) : null,
              actual: JSON.stringify(firstFailing.actual_return ?? null),
            }
          : {
              label: firstFailing.label,
              input: firstFailing.input_data,
              expected: firstFailing.expected_output,
              actual: firstFailing.actual_output,
            }
        : null,
    });
  }, [currentProblem, currentLanguage, executionMode, editorCode, lastRunResult, setProblemBridge]);

  useEffect(() => () => setProblemBridge(null), [setProblemBridge]);

  if (loading) {
    return (
      <div className="min-h-screen pt-20 flex items-center justify-center">
        <div className="text-zinc-500">Loading problem…</div>
      </div>
    );
  }

  if (!problem) {
    return (
      <div className="min-h-screen pt-20 flex flex-col items-center justify-center gap-4">
        <div className="text-zinc-400">Problem not found.</div>
        <Link to="/atlas-code/catalog" className="text-indigo-400 hover:text-indigo-300 text-sm">
          ← Back to catalog
        </Link>
      </div>
    );
  }

  return (
    <div className="h-screen pt-16 flex flex-col overflow-hidden">
      {/* Top bar */}
      <div className="flex-shrink-0 border-b border-charcoal/10 bg-[#09090B] px-4 h-11 flex items-center gap-4">
        <Link
          to="/atlas-code/catalog"
          className="flex items-center gap-1.5 text-sm text-zinc-500 hover:text-white transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          Catalog
        </Link>
        <span className="text-zinc-700">/</span>
        <span className="text-base text-white font-medium truncate max-w-xs">{problem.title}</span>
        <span className={cn('text-sm font-medium ml-auto', DIFF_COLOR[problem.difficulty])}>
          {problem.difficulty}
        </span>
        {problem.algorithm_slug && (
          <Link
            to={`/algorithms/${problem.algorithm_slug}`}
            className="text-sm text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            <Zap className="w-3.5 h-3.5" />
            Visualize
          </Link>
        )}
      </div>

      {/* Workspace: top row (problem pane + editor) + resizable bottom console */}
      <div ref={workspaceRef} className="flex-1 min-h-0 flex overflow-hidden">
          {/* LEFT: Problem statement */}
          <div
            style={{ width: problemPaneWidthPx }}
            className="flex-shrink-0 overflow-y-auto bg-[#0c0c0f]"
          >
            <div className="p-5">
              <div className="flex items-start justify-between mb-4">
                <h1 className="text-xl font-bold text-white leading-snug">{problem.title}</h1>
                <button
                  onClick={() => setShowStatement((v) => !v)}
                  className="text-zinc-600 hover:text-white p-1 transition-colors ml-2 flex-shrink-0"
                  title="Toggle statement"
                >
                  {showStatement ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              <div className="flex flex-wrap gap-2 mb-4">
                <span className={cn('text-sm font-medium px-2.5 py-1 rounded-full border',
                  problem.difficulty === 'Easy' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                    : problem.difficulty === 'Medium' ? 'bg-amber-500/10 border-amber-500/20 text-amber-400'
                      : 'bg-rose-500/10 border-rose-500/20 text-rose-400'
                )}>
                  {problem.difficulty}
                </span>
                <span className="text-sm px-2.5 py-1 rounded-full border border-charcoal/10 text-zinc-400 capitalize">
                  {problem.category.replace(/-/g, ' ')}
                </span>
                {problem.estimated_minutes > 0 && (
                  <span className="text-sm px-2.5 py-1 rounded-full border border-charcoal/10 text-zinc-400 flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" />{problem.estimated_minutes}m
                  </span>
                )}
              </div>

              {showStatement && (
                <>
                  <div className="text-base text-zinc-300 leading-relaxed whitespace-pre-wrap mb-5">
                    {problem.problem_statement}
                  </div>

                  {problem.examples?.length > 0 && (
                    <div className="mb-5">
                      <h3 className="text-sm font-semibold text-zinc-500 uppercase tracking-wider mb-3">Examples</h3>
                      {problem.examples.map((ex, i) => (
                        <div key={i} className="mb-3 rounded-xl bg-white/3 border border-charcoal/10 p-3">
                          <div className="text-sm text-zinc-500 mb-1.5 font-medium">Example {i + 1}</div>
                          <div className="space-y-1">
                            <div className="text-sm font-mono text-zinc-400">
                              <span className="text-zinc-600">Input: </span>{ex.input}
                            </div>
                            <div className="text-sm font-mono text-zinc-400">
                              <span className="text-zinc-600">Output: </span>{ex.output}
                            </div>
                            {ex.explanation && (
                              <div className="text-sm text-zinc-500 pt-1">{ex.explanation}</div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {problem.constraints?.length > 0 && (
                    <div className="mb-5">
                      <h3 className="text-sm font-semibold text-zinc-500 uppercase tracking-wider mb-2">Constraints</h3>
                      <ul className="space-y-1">
                        {problem.constraints.map((c, i) => (
                          <li key={i} className="text-sm text-zinc-400 flex gap-2">
                            <span className="text-zinc-700 flex-shrink-0">·</span>
                            <code className="font-mono">{c}</code>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {problem.companies?.length > 0 && (
                    <div className="mb-5">
                      <h3 className="text-sm font-semibold text-zinc-500 uppercase tracking-wider mb-2">
                        Companies
                      </h3>
                      <div className="flex flex-wrap gap-1.5">
                        {problem.companies.map((c) => (
                          <span key={c} className="text-sm px-2.5 py-1 rounded-md bg-white/4 border border-charcoal/10 text-zinc-400">
                            {c}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {hints.length > 0 && (
                    <div>
                      <button
                        onClick={() => setShowHints((v) => !v)}
                        className="w-full flex items-center justify-between text-sm font-semibold text-zinc-500 uppercase tracking-wider mb-2 hover:text-zinc-300 transition-colors"
                      >
                        <span>Hints ({hints.length})</span>
                        <Lightbulb className="w-3.5 h-3.5" />
                      </button>
                      {showHints && (
                        <HintPanel hints={hints} revealedLevel={revealedHintLevel} onReveal={revealNextHint} />
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Vertical divider */}
          <div
            onPointerDown={onVerticalDividerDown}
            className="w-1 flex-shrink-0 cursor-col-resize group relative"
          >
            <div className="absolute inset-y-0 left-0 w-px bg-white/8 group-hover:bg-indigo-500/40 group-hover:w-0.5 transition-colors" />
          </div>

          {/* RIGHT: editor + bottom console column -- the console must only
              ever span this column's width, never underlap the problem pane */}
          <div className="flex-1 min-w-0 flex flex-col overflow-hidden">
          <div
            className="flex-shrink-0 flex flex-col overflow-hidden"
            style={{
              height: consoleCollapsed ? undefined : `${100 - consoleHeightPct}%`,
              flexGrow: consoleCollapsed ? 1 : 0,
            }}
          >
            <div className="flex-shrink-0 flex items-center gap-3 px-4 py-2.5 border-b border-charcoal/10 bg-[#09090B]">
              <div className="flex-1" />

              <ModeToggle
                problem={problem}
                language={currentLanguage}
                value={executionMode}
                onChange={setExecutionMode}
              />

              <LangPicker value={currentLanguage} onChange={setLanguage} />

              <button
                onClick={() => useAtlasCodeStore.getState().resetEditor()}
                className="flex items-center gap-1.5 text-sm text-zinc-500 hover:text-white px-2.5 py-1.5 rounded-lg hover:bg-white/5 transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Reset
              </button>

              <button
                onClick={handleRunAllVisible}
                disabled={isRunning}
                title="Run visible cases (Ctrl/Cmd+Enter)"
                className="flex items-center gap-1.5 text-sm bg-indigo-600 hover:bg-indigo-500 text-white px-3.5 py-1.5 rounded-lg transition-colors disabled:opacity-50 font-medium"
              >
                {isRunning ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Running…
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    Run
                  </>
                )}
              </button>
            </div>

            <div className="flex-1 overflow-hidden">
              <MonacoEditor
                height="100%"
                language={MONACO_LANG[currentLanguage] ?? 'python'}
                value={editorCode}
                onChange={(v) => setCode(v ?? '')}
                onMount={(editor) => { editorRef.current = editor; }}
                theme="vs-dark"
                options={{
                  fontSize: 15,
                  fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
                  fontLigatures: true,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  lineNumbers: 'on',
                  renderLineHighlight: 'gutter',
                  padding: { top: 12, bottom: 12 },
                  bracketPairColorization: { enabled: true },
                  smoothScrolling: true,
                  cursorBlinking: 'smooth',
                  wordWrap: 'on',
                  automaticLayout: true,
                }}
              />
            </div>
            {runError && (
              <div className="flex-shrink-0 px-3 py-1.5 text-sm text-rose-400 bg-rose-500/5 border-t border-rose-500/20">
                {runError}
              </div>
            )}
          </div>

          {/* Bottom execution console -- confined to this column's width */}
          <div
            className="flex-shrink-0 border-t border-charcoal/10 flex flex-col overflow-hidden"
            style={{
              height: consoleCollapsed ? undefined : `${consoleHeightPct}%`,
              flexGrow: consoleCollapsed ? 1 : 0,
            }}
          >
            <BottomConsole
              problem={problem}
              isRunning={isRunning}
              onRun={handleRun}
              onResizeDeltaY={onConsoleResizeDeltaY}
            />
          </div>
          </div>
      </div>
    </div>
  );
}
