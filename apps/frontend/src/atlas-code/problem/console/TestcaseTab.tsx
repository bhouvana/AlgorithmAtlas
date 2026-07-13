import { useState } from 'react';
import { Play, Plus, Trash2, Copy, RotateCcw } from 'lucide-react';
import type { ProblemDetail, TestCaseOut } from '../../api/problems';
import { useAtlasCodeStore, type CustomCase } from '../../store/atlasCodeStore';
import { cn } from '../../../lib/utils';
import type { RunSpec } from './types';
import { formatCompactJson } from './formatJson';

interface Props {
  problem: ProblemDetail;
  isRunning: boolean;
  onRun: (spec: RunSpec) => void;
}

type CaseKey = { kind: 'visible'; index: number } | { kind: 'custom'; id: string };

function parseJsonOrUndefined(text: string): { ok: true; value: unknown } | { ok: false; error: string } {
  if (text.trim() === '') return { ok: false, error: 'empty' };
  try {
    return { ok: true, value: JSON.parse(text) };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : 'Invalid JSON' };
  }
}

export function TestcaseTab({ problem, isRunning, onRun }: Props) {
  const {
    executionMode,
    selectedCaseIndices, toggleSelectedCase,
    customCasesByProblem, addCustomCase, updateCustomCase, removeCustomCase, duplicateCustomCase,
  } = useAtlasCodeStore();
  const isFunctionMode = executionMode === 'function';

  const customCases = customCasesByProblem[problem.id] ?? [];
  const visible = problem.visible_test_cases;

  const [active, setActive] = useState<CaseKey>(
    visible.length > 0 ? { kind: 'visible', index: 0 } : { kind: 'custom', id: customCases[0]?.id ?? '' }
  );

  const activeVisible: TestCaseOut | null =
    active.kind === 'visible' ? visible[active.index] ?? null : null;
  const activeCustom: CustomCase | null =
    active.kind === 'custom' ? customCases.find((c) => c.id === active.id) ?? null : null;

  return (
    <div className="flex flex-col h-full">
      {/* Case tab strip */}
      <div className="flex-shrink-0 flex items-center gap-1.5 px-3 py-2 border-b border-charcoal/10 overflow-x-auto">
        {visible.map((tc, i) => {
          const k: CaseKey = { kind: 'visible', index: i };
          const isActive = active.kind === 'visible' && active.index === i;
          const isSelected = selectedCaseIndices.includes(i);
          return (
            <button
              key={tc.id}
              onClick={() => setActive(k)}
              className={cn(
                'flex-shrink-0 flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg border transition-colors',
                isActive ? 'border-indigo-500/40 bg-indigo-500/10 text-white' : 'border-charcoal/10 text-zinc-500 hover:text-zinc-300'
              )}
            >
              <input
                type="checkbox"
                checked={isSelected}
                onClick={(e) => e.stopPropagation()}
                onChange={() => toggleSelectedCase(i)}
                className="w-3.5 h-3.5 accent-indigo-500"
                title="Select for batch run"
              />
              Case {i + 1}
            </button>
          );
        })}
        {customCases.map((c, i) => {
          const k: CaseKey = { kind: 'custom', id: c.id };
          const isActive = active.kind === 'custom' && active.id === c.id;
          return (
            <button
              key={c.id}
              onClick={() => setActive(k)}
              className={cn(
                'flex-shrink-0 text-sm px-3 py-1.5 rounded-lg border transition-colors',
                isActive ? 'border-violet-500/40 bg-violet-500/10 text-white' : 'border-charcoal/10 text-zinc-500 hover:text-zinc-300'
              )}
            >
              Custom {i + 1}
            </button>
          );
        })}
        <button
          onClick={() => {
            addCustomCase(problem.id);
          }}
          className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-lg border border-charcoal/10 text-zinc-500 hover:text-white hover:border-white/20 transition-colors"
          title="Add custom case"
        >
          <Plus className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Batch action bar */}
      {selectedCaseIndices.length > 0 && (
        <div className="flex-shrink-0 flex items-center justify-between px-3 py-1.5 border-b border-charcoal/10 bg-indigo-500/5">
          <span className="text-sm text-zinc-400">{selectedCaseIndices.length} case(s) selected</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onRun({ mode: 'selected', indices: selectedCaseIndices })}
              disabled={isRunning}
              className="text-sm text-indigo-400 hover:text-indigo-300 disabled:opacity-50"
            >
              Run Selected
            </button>
          </div>
        </div>
      )}

      {/* Active case detail */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeVisible && isFunctionMode && (
          <div className="space-y-3">
            <div>
              <div className="text-sm text-zinc-600 mb-1">Arguments</div>
              <pre className="text-sm text-zinc-300 bg-white/3 rounded-lg px-3 py-2 font-mono overflow-x-auto whitespace-pre-wrap">
                {formatCompactJson(activeVisible.function_args)}
              </pre>
            </div>
            <div>
              <div className="text-sm text-zinc-600 mb-1">Expected Return</div>
              <pre className="text-sm text-zinc-300 bg-white/3 rounded-lg px-3 py-2 font-mono overflow-x-auto whitespace-pre-wrap">
                {formatCompactJson(activeVisible.function_expected)}
              </pre>
            </div>
            {activeVisible.explanation && (
              <div className="text-sm text-zinc-500">{activeVisible.explanation}</div>
            )}
            <button
              onClick={() => onRun({ mode: 'selected', indices: [active.kind === 'visible' ? active.index : 0] })}
              disabled={isRunning}
              className="flex items-center gap-1.5 text-sm bg-white/8 hover:bg-white/12 border border-charcoal/10 text-white px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              Run This Case
            </button>
          </div>
        )}

        {activeVisible && !isFunctionMode && (
          <div className="space-y-3">
            <div>
              <div className="text-sm text-zinc-600 mb-1">Input</div>
              <pre className="text-sm text-zinc-300 bg-white/3 rounded-lg px-3 py-2 font-mono overflow-x-auto whitespace-pre-wrap">
                {activeVisible.input_data}
              </pre>
            </div>
            <div>
              <div className="text-sm text-zinc-600 mb-1">Expected Output</div>
              <pre className="text-sm text-zinc-300 bg-white/3 rounded-lg px-3 py-2 font-mono overflow-x-auto whitespace-pre-wrap">
                {activeVisible.expected_output}
              </pre>
            </div>
            {activeVisible.explanation && (
              <div className="text-sm text-zinc-500">{activeVisible.explanation}</div>
            )}
            <button
              onClick={() => onRun({ mode: 'selected', indices: [active.kind === 'visible' ? active.index : 0] })}
              disabled={isRunning}
              className="flex items-center gap-1.5 text-sm bg-white/8 hover:bg-white/12 border border-charcoal/10 text-white px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              Run This Case
            </button>
          </div>
        )}

        {activeCustom && isFunctionMode && (() => {
          const parsedArgs = parseJsonOrUndefined(activeCustom.arguments_json);
          const hasExpectedText = activeCustom.expected_return_json !== null;
          const parsedExpected = hasExpectedText
            ? parseJsonOrUndefined(activeCustom.expected_return_json ?? '')
            : null;
          const canRun = parsedArgs.ok && (!hasExpectedText || (parsedExpected && parsedExpected.ok));
          return (
            <div className="space-y-3">
              <div>
                <div className="text-sm text-zinc-600 mb-1">Arguments (JSON object)</div>
                <textarea
                  value={activeCustom.arguments_json}
                  onChange={(e) => updateCustomCase(problem.id, activeCustom.id, { arguments_json: e.target.value })}
                  rows={4}
                  placeholder={JSON.stringify(problem.function_contract?.parameters.reduce(
                    (acc, p) => ({ ...acc, [p.name]: null }), {} as Record<string, null>
                  ) ?? {})}
                  className="w-full text-sm text-zinc-200 bg-white/3 rounded-lg px-3 py-2 font-mono resize-y border border-charcoal/10 focus:border-violet-500/40 focus:outline-none"
                />
                {!parsedArgs.ok && activeCustom.arguments_json.trim() !== '' && (
                  <div className="text-sm text-rose-400 mt-1">Invalid JSON: {parsedArgs.error}</div>
                )}
              </div>
              <div>
                <div className="text-sm text-zinc-600 mb-1 flex items-center justify-between">
                  <span>Expected Return (optional JSON value)</span>
                  {activeCustom.expected_return_json !== null && (
                    <button
                      onClick={() => updateCustomCase(problem.id, activeCustom.id, { expected_return_json: null })}
                      className="text-zinc-600 hover:text-zinc-400"
                    >
                      clear
                    </button>
                  )}
                </div>
                <textarea
                  value={activeCustom.expected_return_json ?? ''}
                  onChange={(e) => updateCustomCase(problem.id, activeCustom.id, { expected_return_json: e.target.value })}
                  rows={2}
                  placeholder="Leave blank to just see the return value, no pass/fail"
                  className="w-full text-sm text-zinc-200 bg-white/3 rounded-lg px-3 py-2 font-mono resize-y border border-charcoal/10 focus:border-violet-500/40 focus:outline-none"
                />
                {hasExpectedText && parsedExpected && !parsedExpected.ok && (
                  <div className="text-sm text-rose-400 mt-1">Invalid JSON: {parsedExpected.error}</div>
                )}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    if (!canRun || !parsedArgs.ok) return;
                    onRun({
                      mode: 'custom',
                      cases: [{
                        arguments: parsedArgs.value as Record<string, unknown>,
                        expected_return: hasExpectedText && parsedExpected && parsedExpected.ok ? parsedExpected.value : undefined,
                        has_expected_return: hasExpectedText && !!parsedExpected?.ok,
                      }],
                    });
                  }}
                  disabled={isRunning || !canRun}
                  className="flex items-center gap-1.5 text-sm bg-white/8 hover:bg-white/12 border border-charcoal/10 text-white px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
                >
                  <Play className="w-3.5 h-3.5" />
                  Run This Case
                </button>
                <button
                  onClick={() => duplicateCustomCase(problem.id, activeCustom.id)}
                  className="flex items-center gap-1.5 text-sm text-zinc-500 hover:text-white px-2 py-1.5 rounded-lg hover:bg-white/5 transition-colors"
                >
                  <Copy className="w-3.5 h-3.5" /> Duplicate
                </button>
                <button
                  onClick={() => updateCustomCase(problem.id, activeCustom.id, { arguments_json: '', expected_return_json: null })}
                  className="flex items-center gap-1.5 text-sm text-zinc-500 hover:text-white px-2 py-1.5 rounded-lg hover:bg-white/5 transition-colors"
                >
                  <RotateCcw className="w-3.5 h-3.5" /> Reset
                </button>
                <button
                  onClick={() => {
                    removeCustomCase(problem.id, activeCustom.id);
                    setActive(visible.length > 0 ? { kind: 'visible', index: 0 } : { kind: 'custom', id: '' });
                  }}
                  className="flex items-center gap-1.5 text-sm text-rose-400/80 hover:text-rose-400 px-2 py-1.5 rounded-lg hover:bg-rose-500/5 transition-colors ml-auto"
                >
                  <Trash2 className="w-3.5 h-3.5" /> Delete
                </button>
              </div>
            </div>
          );
        })()}

        {activeCustom && !isFunctionMode && (
          <div className="space-y-3">
            <div>
              <div className="text-sm text-zinc-600 mb-1">Input</div>
              <textarea
                value={activeCustom.input_data}
                onChange={(e) => updateCustomCase(problem.id, activeCustom.id, { input_data: e.target.value })}
                rows={4}
                placeholder="stdin for your program"
                className="w-full text-sm text-zinc-200 bg-white/3 rounded-lg px-3 py-2 font-mono resize-y border border-charcoal/10 focus:border-violet-500/40 focus:outline-none"
              />
            </div>
            <div>
              <div className="text-sm text-zinc-600 mb-1 flex items-center justify-between">
                <span>Expected Output (optional)</span>
                {activeCustom.expected_output !== null && (
                  <button
                    onClick={() => updateCustomCase(problem.id, activeCustom.id, { expected_output: null })}
                    className="text-zinc-600 hover:text-zinc-400"
                  >
                    clear
                  </button>
                )}
              </div>
              <textarea
                value={activeCustom.expected_output ?? ''}
                onChange={(e) => updateCustomCase(problem.id, activeCustom.id, { expected_output: e.target.value })}
                rows={3}
                placeholder="Leave blank to just see program output, no pass/fail"
                className="w-full text-sm text-zinc-200 bg-white/3 rounded-lg px-3 py-2 font-mono resize-y border border-charcoal/10 focus:border-violet-500/40 focus:outline-none"
              />
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() =>
                  onRun({
                    mode: 'custom',
                    cases: [{ input_data: activeCustom.input_data, expected_output: activeCustom.expected_output }],
                  })
                }
                disabled={isRunning}
                className="flex items-center gap-1.5 text-sm bg-white/8 hover:bg-white/12 border border-charcoal/10 text-white px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5" />
                Run This Case
              </button>
              <button
                onClick={() => duplicateCustomCase(problem.id, activeCustom.id)}
                className="flex items-center gap-1.5 text-sm text-zinc-500 hover:text-white px-2 py-1.5 rounded-lg hover:bg-white/5 transition-colors"
              >
                <Copy className="w-3.5 h-3.5" /> Duplicate
              </button>
              <button
                onClick={() => updateCustomCase(problem.id, activeCustom.id, { input_data: '', expected_output: null })}
                className="flex items-center gap-1.5 text-sm text-zinc-500 hover:text-white px-2 py-1.5 rounded-lg hover:bg-white/5 transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" /> Reset
              </button>
              <button
                onClick={() => {
                  removeCustomCase(problem.id, activeCustom.id);
                  setActive(visible.length > 0 ? { kind: 'visible', index: 0 } : { kind: 'custom', id: '' });
                }}
                className="flex items-center gap-1.5 text-sm text-rose-400/80 hover:text-rose-400 px-2 py-1.5 rounded-lg hover:bg-rose-500/5 transition-colors ml-auto"
              >
                <Trash2 className="w-3.5 h-3.5" /> Delete
              </button>
            </div>
          </div>
        )}

        {!activeVisible && !activeCustom && (
          <div className="text-center text-sm text-zinc-600 py-8">
            No test cases yet. Add a custom case with the + button above.
          </div>
        )}
      </div>
    </div>
  );
}
