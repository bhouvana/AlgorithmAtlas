import { useState, useEffect } from 'react';
import { CheckCircle2, XCircle, AlertTriangle, Clock, Cpu } from 'lucide-react';
import { cn } from '../../../lib/utils';
import type { ExecutionMode } from '../../api/problems';
import type { NormalizedResult, NormalizedCase } from './resultNormalize';
import { formatCompactJson } from './formatJson';

const STATUS_STYLE: Record<string, { icon: 'pass' | 'fail' | 'warn'; color: string }> = {
  passed: { icon: 'pass', color: 'text-emerald-400' },
  executed: { icon: 'warn', color: 'text-zinc-400' },
  failed: { icon: 'fail', color: 'text-rose-400' },
  'Runtime Error': { icon: 'fail', color: 'text-orange-400' },
  'Time Limit Exceeded': { icon: 'warn', color: 'text-amber-400' },
  'Compilation Error': { icon: 'fail', color: 'text-red-400' },
  // Function Mode only -- a missing/renamed function or wrong signature is a
  // structural problem with the submission, not a wrong VALUE, so it gets
  // its own color rather than being folded into "failed" (Phase 18).
  'Function Contract Error': { icon: 'fail', color: 'text-fuchsia-400' },
};

function StatusIcon({ status }: { status: string }) {
  const style = STATUS_STYLE[status] ?? { icon: 'fail', color: 'text-rose-400' };
  if (style.icon === 'pass') return <CheckCircle2 className={cn('w-3.5 h-3.5 flex-shrink-0', style.color)} />;
  if (style.icon === 'warn') return <AlertTriangle className={cn('w-3.5 h-3.5 flex-shrink-0', style.color)} />;
  return <XCircle className={cn('w-3.5 h-3.5 flex-shrink-0', style.color)} />;
}

function HeaderBanner({ result }: { result: NormalizedResult }) {
  const comparable = result.cases.filter((c) => c.hasExpected);
  const allPassed = comparable.length > 0 && comparable.every((c) => c.status === 'passed');
  const nonePassed = result.passed === 0;

  if (result.verdictHeadline === 'Compilation Error') {
    return (
      <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4">
        <div className="text-lg font-bold text-red-400 mb-1.5">Compilation Error</div>
        {result.compileOutput && (
          <pre className="text-sm text-red-300/90 font-mono whitespace-pre-wrap overflow-x-auto max-h-40 overflow-y-auto">
            {result.compileOutput}
          </pre>
        )}
      </div>
    );
  }

  return (
    <div
      className={cn(
        'rounded-xl border p-4',
        allPassed ? 'border-emerald-500/20 bg-emerald-500/5'
          : nonePassed ? 'border-rose-500/20 bg-rose-500/5'
            : 'border-amber-500/20 bg-amber-500/5'
      )}
    >
      <div className="flex items-center justify-between">
        <span className={cn('text-lg font-bold flex items-center gap-2', allPassed ? 'text-emerald-400' : nonePassed ? 'text-rose-400' : 'text-amber-400')}>
          {allPassed ? <CheckCircle2 className="w-5 h-5" /> : nonePassed ? <XCircle className="w-5 h-5" /> : <AlertTriangle className="w-5 h-5" />}
          {allPassed ? 'All Passed' : nonePassed ? 'None Passed' : 'Partial Pass'}
        </span>
        <span className="text-sm text-zinc-400">
          {result.passed} / {result.total} passed
        </span>
      </div>
      <div className="flex items-center gap-4 mt-2 text-sm text-zinc-500">
        <span className="flex items-center gap-1.5"><Clock className="w-4 h-4" />{result.runtimeMs.toFixed(1)} ms</span>
        {result.memoryKb != null && (
          <span className="flex items-center gap-1.5"><Cpu className="w-4 h-4" />{(result.memoryKb / 1024).toFixed(1)} MB</span>
        )}
      </div>
    </div>
  );
}

function Diff({ expected, actual }: { expected: string; actual: string }) {
  const expLines = expected.split('\n');
  const actLines = actual.split('\n');
  const firstDiff = expLines.findIndex((l, i) => l !== actLines[i]);
  return (
    <div className="grid grid-cols-2 gap-2">
      <div>
        <div className="text-sm text-zinc-600 mb-1">Expected</div>
        <pre className="text-sm text-emerald-300/90 bg-white/3 rounded-lg px-3 py-2 font-mono overflow-x-auto whitespace-pre-wrap">
          {expLines.map((l, i) => (
            <div key={i} className={i === firstDiff ? 'bg-rose-500/10 -mx-1 px-1 rounded' : ''}>{l || ' '}</div>
          ))}
        </pre>
      </div>
      <div>
        <div className="text-sm text-zinc-600 mb-1">Your Output</div>
        <pre className="text-sm text-rose-300/90 bg-white/3 rounded-lg px-3 py-2 font-mono overflow-x-auto whitespace-pre-wrap">
          {actLines.map((l, i) => (
            <div key={i} className={i === firstDiff ? 'bg-rose-500/10 -mx-1 px-1 rounded' : ''}>{l || ' '}</div>
          ))}
        </pre>
      </div>
    </div>
  );
}

function jsonPreview(value: unknown): string {
  if (value === undefined) return '(none)';
  return formatCompactJson(value);
}

// Function Mode case detail -- deliberately labeled "Arguments"/"Expected
// Return"/"Actual Return", never "stdin"/"stdout" (Phase 16: the UI language
// must reflect the contract actually being judged).
function FunctionCaseDetail({ c }: { c: NormalizedCase }) {
  if (c.isHidden) {
    return (
      <div className="rounded-lg border border-charcoal/10 bg-white/3 p-3 text-sm text-zinc-500 space-y-1">
        <div><span className="text-zinc-600">Arguments: </span>Hidden</div>
        <div><span className="text-zinc-600">Expected Return: </span>Hidden</div>
        <div><span className="text-zinc-600">Actual Return: </span>Hidden</div>
      </div>
    );
  }
  return (
    <>
      <div>
        <div className="text-sm text-zinc-600 mb-1">Arguments</div>
        <pre className="text-sm text-zinc-300 bg-white/3 rounded-lg px-3 py-2 font-mono overflow-x-auto whitespace-pre-wrap">
          {jsonPreview(c.arguments)}
        </pre>
      </div>

      {c.status === 'Function Contract Error' && c.contractError && (
        <div>
          <div className="text-sm text-zinc-600 mb-1">Contract Error</div>
          <pre className="text-sm text-fuchsia-300/90 bg-white/3 rounded-lg px-3 py-2 font-mono overflow-x-auto whitespace-pre-wrap">
            {c.contractError.message}
          </pre>
        </div>
      )}

      {c.hasExpected && (c.status === 'passed' || c.status === 'failed') && (
        <div className="grid grid-cols-2 gap-2">
          <div>
            <div className="text-sm text-zinc-600 mb-1">Expected Return</div>
            <pre className="text-sm text-emerald-300/90 bg-white/3 rounded-lg px-3 py-2 font-mono overflow-x-auto whitespace-pre-wrap">
              {jsonPreview(c.expectedReturn)}
            </pre>
          </div>
          <div>
            <div className="text-sm text-zinc-600 mb-1">Actual Return</div>
            <pre className="text-sm text-rose-300/90 bg-white/3 rounded-lg px-3 py-2 font-mono overflow-x-auto whitespace-pre-wrap">
              {jsonPreview(c.actualReturn)}
            </pre>
          </div>
        </div>
      )}

      {(!c.hasExpected || (c.status !== 'passed' && c.status !== 'failed' && c.status !== 'Function Contract Error')) && (
        <div>
          <div className="text-sm text-zinc-600 mb-1">Actual Return</div>
          <pre className="text-sm text-zinc-300 bg-white/3 rounded-lg px-3 py-2 font-mono overflow-x-auto whitespace-pre-wrap">
            {jsonPreview(c.actualReturn)}
          </pre>
        </div>
      )}

      {c.stderr && c.status !== 'passed' && (
        <div>
          <div className="text-sm text-zinc-600 mb-1">stderr</div>
          <pre className="text-sm text-orange-300/80 bg-white/3 rounded-lg px-3 py-2 font-mono overflow-x-auto whitespace-pre-wrap max-h-32 overflow-y-auto">
            {c.stderr}
          </pre>
        </div>
      )}
    </>
  );
}

function CaseInspector({ c, executionMode }: { c: NormalizedCase; executionMode: ExecutionMode }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <StatusIcon status={c.status} />
        <span className={cn('text-base font-semibold', (STATUS_STYLE[c.status] ?? STATUS_STYLE.failed).color)}>
          {c.status === 'passed' ? 'Accepted' : c.status === 'failed' ? 'Wrong Answer' : c.status === 'executed' ? 'Executed' : c.status}
        </span>
        <span className="text-sm text-zinc-500 ml-auto flex items-center gap-3">
          <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" />{c.runtimeMs.toFixed(1)} ms</span>
          {c.memoryKb != null && <span className="flex items-center gap-1"><Cpu className="w-3.5 h-3.5" />{(c.memoryKb / 1024).toFixed(1)} MB</span>}
        </span>
      </div>

      {executionMode === 'function' ? (
        <FunctionCaseDetail c={c} />
      ) : c.isHidden ? (
        <div className="rounded-lg border border-charcoal/10 bg-white/3 p-3 text-sm text-zinc-500 space-y-1">
          <div><span className="text-zinc-600">Input: </span>Hidden</div>
          <div><span className="text-zinc-600">Expected: </span>Hidden</div>
          <div><span className="text-zinc-600">Actual: </span>Hidden</div>
        </div>
      ) : (
        <>
          <div>
            <div className="text-sm text-zinc-600 mb-1">Input</div>
            <pre className="text-sm text-zinc-300 bg-white/3 rounded-lg px-3 py-2 font-mono overflow-x-auto whitespace-pre-wrap">
              {c.input || '(empty)'}
            </pre>
          </div>

          {c.hasExpected && (c.status === 'passed' || c.status === 'failed') && (
            <Diff expected={c.expected ?? ''} actual={c.actual} />
          )}

          {(!c.hasExpected || (c.status !== 'passed' && c.status !== 'failed')) && (
            <div>
              <div className="text-sm text-zinc-600 mb-1">Output</div>
              <pre className="text-sm text-zinc-300 bg-white/3 rounded-lg px-3 py-2 font-mono overflow-x-auto whitespace-pre-wrap">
                {c.actual || '(no output)'}
              </pre>
            </div>
          )}

          {c.stderr && c.status !== 'passed' && (
            <div>
              <div className="text-sm text-zinc-600 mb-1">stderr</div>
              <pre className="text-sm text-orange-300/80 bg-white/3 rounded-lg px-3 py-2 font-mono overflow-x-auto whitespace-pre-wrap max-h-32 overflow-y-auto">
                {c.stderr}
              </pre>
            </div>
          )}
          {c.outputTruncated && (
            <div className="text-sm text-zinc-600">Output truncated for display.</div>
          )}
        </>
      )}
    </div>
  );
}

interface Props {
  result: NormalizedResult | null;
}

export function ResultTab({ result }: Props) {
  const [activeKey, setActiveKey] = useState<string | null>(null);

  // Only individually-inspectable cases get a tab: every visible case (there
  // are only ever a handful), plus any hidden case that DIDN'T pass (real
  // diagnostic value). Passing hidden cases collapse into one summary line --
  // scrolling through 35 identical "Hidden Case N: Accepted" tabs is noise,
  // not signal (see product feedback: "for hidden no need to scroll at all,
  // 40/40 passed is good enough").
  const tabCases = result
    ? result.cases.filter((c) => !c.isHidden || c.status !== 'passed')
    : [];
  const passedHiddenCount = result
    ? result.cases.filter((c) => c.isHidden && c.status === 'passed').length
    : 0;

  useEffect(() => {
    if (!result) { setActiveKey(null); return; }
    const firstFailing = tabCases.find((c) => c.status !== 'passed' && c.status !== 'executed');
    setActiveKey((firstFailing ?? tabCases[0])?.key ?? null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [result]);

  if (!result) {
    return (
      <div className="flex items-center justify-center h-full text-sm text-zinc-600">
        Run your code to see results here.
      </div>
    );
  }

  const active = tabCases.find((c) => c.key === activeKey) ?? null;

  return (
    <div className="flex flex-col h-full">
      <div className="flex-shrink-0 p-3">
        <HeaderBanner result={result} />
      </div>

      {(tabCases.length > 0 || passedHiddenCount > 0) && (
        <div className="flex-shrink-0 flex items-center gap-1.5 px-3 pb-2 flex-wrap">
          {tabCases.map((c) => (
            <button
              key={c.key}
              onClick={() => setActiveKey(c.key)}
              className={cn(
                'flex-shrink-0 flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg border transition-colors',
                activeKey === c.key ? 'border-indigo-500/40 bg-indigo-500/10 text-white' : 'border-charcoal/10 text-zinc-500 hover:text-zinc-300'
              )}
            >
              <StatusIcon status={c.status} />
              {c.label}
            </button>
          ))}
          {passedHiddenCount > 0 && (
            <span className="flex-shrink-0 flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg border border-emerald-500/15 bg-emerald-500/5 text-emerald-400/90">
              <CheckCircle2 className="w-3.5 h-3.5" />
              {passedHiddenCount} hidden case{passedHiddenCount === 1 ? '' : 's'} passed
            </span>
          )}
        </div>
      )}

      <div className="flex-1 overflow-y-auto px-3 pb-3">
        {active && <CaseInspector c={active} executionMode={result.executionMode} />}
        {!active && tabCases.length === 0 && (
          <div className="text-sm text-zinc-500 text-center py-6">
            All {passedHiddenCount} hidden cases passed — nothing further to inspect.
          </div>
        )}
      </div>
    </div>
  );
}
