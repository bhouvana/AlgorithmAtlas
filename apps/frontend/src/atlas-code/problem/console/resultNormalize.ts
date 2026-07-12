import type { ExecutionMode, RunResult } from '../../api/problems';

export interface NormalizedCase {
  key: string;
  label: string;
  isHidden: boolean;
  // 'passed' | 'failed' | 'executed' | 'Runtime Error' | 'Time Limit Exceeded'
  // | 'Compilation Error' | 'Function Contract Error'
  status: string;
  hasExpected: boolean;
  input: string | null;
  expected: string | null;
  actual: string;
  stdout: string;
  stderr: string;
  runtimeMs: number;
  memoryKb: number | null;
  exitCode: number | null;
  timedOut: boolean;
  outputTruncated: boolean;
  // Function Mode only -- the UI must render these as "Arguments"/"Expected
  // Return"/"Actual Return", never "stdin"/"stdout" (Phase 16).
  arguments: Record<string, unknown> | null;
  expectedReturn: unknown;
  actualReturn: unknown;
  contractError: { reason: string; message: string } | null;
}

export interface NormalizedResult {
  executionMode: ExecutionMode;
  language: string;
  verdictHeadline: string; // e.g. "Accepted" | "Wrong Answer" | "Compilation Error" ...
  passed: number;
  total: number;
  runtimeMs: number;
  memoryKb: number | null;
  compileOutput: string | null;
  cases: NormalizedCase[];
}

export function normalizeRun(r: RunResult): NormalizedResult {
  const cases: NormalizedCase[] = r.cases.map((c) => ({
    key: `run-${c.case_index}`,
    label: c.label,
    isHidden: c.is_hidden,
    status: c.status,
    hasExpected: c.has_expected,
    input: c.input_data,
    expected: c.expected_output,
    actual: c.actual_output,
    stdout: c.stdout,
    stderr: c.stderr,
    runtimeMs: c.runtime_ms,
    memoryKb: c.memory_kb,
    exitCode: c.exit_code,
    timedOut: c.timed_out,
    outputTruncated: false,
    arguments: c.arguments ?? null,
    expectedReturn: c.expected_return,
    actualReturn: c.actual_return,
    contractError: c.contract_error ?? null,
  }));
  const comparable = cases.filter((c) => c.hasExpected);
  const headline =
    r.compile_output && comparable.length === 0
      ? 'Compilation Error'
      : comparable.every((c) => c.status === 'passed') && comparable.length > 0
        ? 'All Passed'
        : comparable.some((c) => c.status === 'failed' || !['passed'].includes(c.status))
          ? firstNonPassedVerdict(comparable)
          : 'Executed';
  const memSamples = cases.map((c) => c.memoryKb).filter((m): m is number => m != null);
  return {
    executionMode: r.execution_mode,
    language: r.language,
    verdictHeadline: headline,
    passed: r.summary.passed,
    total: r.summary.total,
    runtimeMs: r.summary.runtime_ms,
    memoryKb: memSamples.length > 0 ? Math.max(...memSamples) : null,
    compileOutput: r.compile_output,
    cases,
  };
}

function firstNonPassedVerdict(cases: NormalizedCase[]): string {
  const priority = ['Compilation Error', 'Function Contract Error', 'Time Limit Exceeded', 'Runtime Error', 'failed'];
  for (const p of priority) {
    const hit = cases.find((c) => c.status === p);
    if (hit) return p === 'failed' ? 'Wrong Answer' : p;
  }
  return 'Wrong Answer';
}
