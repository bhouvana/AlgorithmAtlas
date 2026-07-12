import { ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '../../../lib/utils';
import { useAtlasCodeStore, type ConsoleTab } from '../../store/atlasCodeStore';
import type { ProblemDetail } from '../../api/problems';
import { normalizeRun } from './resultNormalize';
import { TestcaseTab } from './TestcaseTab';
import { ResultTab } from './ResultTab';
import { ConsoleTab as ExecConsoleTab } from './ConsoleTab';
import type { RunSpec } from './types';
import { useResizeDrag } from '../useResizeDrag';

const TABS: { key: ConsoleTab; label: string }[] = [
  { key: 'testcase', label: 'Testcase' },
  { key: 'result', label: 'Test Result' },
  { key: 'console', label: 'Console' },
];

interface Props {
  problem: ProblemDetail;
  isRunning: boolean;
  onRun: (spec: RunSpec) => void;
  onResizeDeltaY: (deltaY: number) => void;
}

export function BottomConsole({ problem, isRunning, onRun, onResizeDeltaY }: Props) {
  const {
    consoleTab, setConsoleTab, consoleCollapsed, toggleConsoleCollapsed,
    lastRunResult,
  } = useAtlasCodeStore();

  const normalizedResult = lastRunResult ? normalizeRun(lastRunResult) : null;

  const onDividerPointerDown = useResizeDrag(onResizeDeltaY, 'y');

  const hasFailure = normalizedResult
    ? normalizedResult.cases.some((c) => c.hasExpected && c.status !== 'passed')
    : false;

  return (
    <div className="flex flex-col h-full bg-[#0c0c0f]">
      {/* Resize handle */}
      <div
        onPointerDown={consoleCollapsed ? undefined : onDividerPointerDown}
        className={cn(
          'flex-shrink-0 h-1.5 -mt-1.5 relative z-10 group',
          !consoleCollapsed && 'cursor-row-resize'
        )}
      >
        <div className="absolute inset-x-0 top-0.5 h-0.5 bg-transparent group-hover:bg-indigo-500/40 transition-colors" />
      </div>

      {/* Tab bar */}
      <div className="flex-shrink-0 flex items-center border-b border-white/8 bg-[#09090B]">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setConsoleTab(t.key)}
            className={cn(
              'relative px-4 py-2.5 text-sm font-medium transition-colors',
              consoleTab === t.key && !consoleCollapsed ? 'text-white' : 'text-zinc-500 hover:text-zinc-300'
            )}
          >
            {t.label}
            {t.key === 'result' && hasFailure && (
              <span className="absolute top-1.5 right-1 w-1.5 h-1.5 rounded-full bg-amber-400" />
            )}
            {consoleTab === t.key && !consoleCollapsed && (
              <span className="absolute bottom-0 left-2 right-2 h-0.5 bg-indigo-500 rounded-full" />
            )}
          </button>
        ))}
        <div className="flex-1" />
        <button
          onClick={toggleConsoleCollapsed}
          className="flex items-center gap-1 text-sm text-zinc-500 hover:text-white px-3 py-2 transition-colors"
          title={consoleCollapsed ? 'Expand console' : 'Collapse console'}
        >
          {consoleCollapsed ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Panel content */}
      {!consoleCollapsed && (
        <div className="flex-1 min-h-0 overflow-hidden">
          {consoleTab === 'testcase' && <TestcaseTab problem={problem} isRunning={isRunning} onRun={onRun} />}
          {consoleTab === 'result' && <ResultTab result={normalizedResult} />}
          {consoleTab === 'console' && <ExecConsoleTab result={normalizedResult} />}
        </div>
      )}
    </div>
  );
}
