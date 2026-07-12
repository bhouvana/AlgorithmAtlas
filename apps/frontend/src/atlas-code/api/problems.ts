const BASE = '/api/v1';

// ── Dual-mode Run architecture ────────────────────────────────────────────────
// Function Mode: user writes only the requested function; AtlasCode generates
// the driver, invokes it with typed arguments, and compares the typed return.
// Program Mode: user writes a complete stdin -> stdout program (unchanged).
export type ExecutionMode = 'function' | 'program';

export type TypeSpec =
  | { kind: 'integer' | 'float' | 'boolean' | 'string' }
  | { kind: 'array' | 'optional'; items: TypeSpec };

export interface FunctionParameter {
  name: string;
  type: TypeSpec;
}

export interface FunctionContract {
  function_name: string;
  parameters: FunctionParameter[];
  return_type: TypeSpec;
}

export interface TestCaseOut {
  id: string;
  input_data: string;
  expected_output: string;
  explanation: string | null;
  order: number;
  // Function Mode -- null for problems/cases without a function_contract.
  function_args: Record<string, unknown> | null;
  function_expected: unknown;
}

export interface ProblemSummary {
  id: string;
  title: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  category: string;
  acceptance_rate: number;
  estimated_minutes: number;
  companies: string[];
  total_submissions: number;
  total_accepted: number;
  // Problem-level completion + Language Coverage (2026-07-12 redefinition --
  // see docs/atlascode-complete-matrix.md). is_complete is true once the
  // problem has >=1 verified language in EITHER mode; the language arrays
  // below are Language Coverage, a separate, non-blocking metric.
  is_complete: boolean;
  leetcode_languages: string[];   // verified languages in Function ("LeetCode") Mode
  codeforces_languages: string[]; // verified languages in Program ("Codeforces") Mode
}

export interface ProblemDetail extends ProblemSummary {
  problem_statement: string;
  examples: Array<{ input: string; output: string; explanation?: string }>;
  constraints: string[];
  algorithm_slug: string | null;
  starter_code: Record<string, string>;
  // Function Mode support -- function_contract is null when this problem
  // hasn't been migrated yet (Program Mode above is unaffected either way).
  function_contract: FunctionContract | null;
  starter_code_function: Record<string, string>;
  visible_test_cases: TestCaseOut[];
}

export function supportsFunctionMode(problem: ProblemDetail, language: string): boolean {
  return (problem.function_contract ?? null) !== null
    && !!problem.starter_code_function
    && language in problem.starter_code_function;
}

export interface HintOut {
  level: number;
  text: string;
}

export interface TestResultOut {
  test_case_id: string;
  passed: boolean;
  verdict: string;
  input_data: string;
  actual_output: string;
  expected_output: string;
  stdout: string;
  stderr: string;
  runtime_ms: number;
  memory_kb: number | null;
  exit_code: number | null;
  timed_out: boolean;
  is_hidden: boolean;
  output_truncated: boolean;
}

export interface SubmissionOut {
  id: string;
  problem_id: string;
  user_id: string;
  language: string;
  verdict: string;
  runtime_ms: number | null;
  memory_kb: number | null;
  test_cases_passed: number;
  test_cases_total: number;
  compile_output: string | null;
  judge_version: string | null;
  test_suite_version: string | null;
  test_results: TestResultOut[];
  ai_review: Record<string, unknown> | null;
  created_at: string;
}

// ── Run (fast iteration -- never persisted, never touches hidden cases) ───────

export interface CustomCaseIn {
  // Program Mode
  input_data?: string;
  expected_output?: string | null;
  // Function Mode -- typed arguments, validated server-side against the
  // problem's function_contract BEFORE execution (malformed cases are
  // rejected with a 400, never silently run).
  arguments?: Record<string, unknown>;
  expected_return?: unknown;
  has_expected_return?: boolean;
}

export interface RunRequest {
  language: string;
  code: string;
  mode: 'visible' | 'selected' | 'custom';
  execution_mode?: ExecutionMode; // defaults to 'program' server-side
  case_indices?: number[];
  custom_cases?: CustomCaseIn[];
}

export interface RunCaseResult {
  case_index: number;
  label: string;
  is_hidden: boolean;
  has_expected: boolean;
  // 'passed' | 'failed' | 'executed' | 'Runtime Error' | 'Time Limit Exceeded'
  // | 'Compilation Error' | 'Function Contract Error' (function mode only)
  status: string;
  input_data: string;
  expected_output: string | null;
  actual_output: string;
  stdout: string;
  stderr: string;
  runtime_ms: number;
  memory_kb: number | null;
  exit_code: number | null;
  timed_out: boolean;
  // Function Mode only -- present (non-null) only when execution_mode was
  // 'function'. Use these instead of input_data/expected_output/actual_output
  // when rendering a function-mode result (see resultNormalize.ts).
  arguments?: Record<string, unknown> | null;
  expected_return?: unknown;
  actual_return?: unknown;
  contract_error?: { reason: string; message: string } | null;
}

export interface RunSummary {
  passed: number;
  failed: number;
  total: number;
  runtime_ms: number;
}

export interface RunResult {
  run_id: string;
  status: string;
  language: string;
  execution_mode: ExecutionMode;
  judge_version: string;
  summary: RunSummary;
  compile_output: string | null;
  cases: RunCaseResult[];
}

export interface QualityRuntime {
  median_ms: number | null;
  p95_ms: number | null;
  slowest_ms: number | null;
  measured_cases: number;
}

export interface QualityPercentile {
  available: boolean;
  percentile: number | null;
  comparable_count: number;
  reason: string | null;
}

export interface SubmissionQualityOut {
  submission_id: string;
  correctness_pct: number;
  tests_passed: number;
  tests_total: number;
  runtime: QualityRuntime;
  memory_kb: number | null;
  memory_available: boolean;
  runtime_percentile: QualityPercentile;
  complexity_estimate: string | null;
  complexity_confidence: string | null;
}

export interface DailyChallengeOut {
  date: string;
  problem_id: string;
  bonus_xp: number;
  problem_title: string;
  problem_difficulty: string;
  problem_category: string;
}

export interface ProgressOut {
  user_id: string;
  solved_problems: string[];
  attempted_problems: string[];
  current_streak: number;
  longest_streak: number;
  xp: number;
  language_stats: Record<string, number>;
  achievements: string[];
}

export async function listProblems(params?: {
  category?: string;
  difficulty?: string;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<ProblemSummary[]> {
  const q = new URLSearchParams();
  if (params?.category) q.set('category', params.category);
  if (params?.difficulty) q.set('difficulty', params.difficulty);
  if (params?.search) q.set('search', params.search);
  if (params?.limit) q.set('limit', String(params.limit));
  if (params?.offset) q.set('offset', String(params.offset));
  const res = await fetch(`${BASE}/problems?${q}`);
  if (!res.ok) throw new Error('Failed to load problems');
  return res.json();
}

export interface ProblemsPage {
  items: ProblemSummary[];
  total: number;
}

// Paginated variant for the catalog: filtering happens server-side (so 216+
// problems are never all fetched at once) and `total` (from the
// X-Total-Count response header) drives page controls.
export async function listProblemsPage(params: {
  category?: string;
  difficulty?: string;
  search?: string;
  limit: number;
  offset: number;
}): Promise<ProblemsPage> {
  const q = new URLSearchParams();
  if (params.category) q.set('category', params.category);
  if (params.difficulty) q.set('difficulty', params.difficulty);
  if (params.search) q.set('search', params.search);
  q.set('limit', String(params.limit));
  q.set('offset', String(params.offset));
  const res = await fetch(`${BASE}/problems?${q}`);
  if (!res.ok) throw new Error('Failed to load problems');
  const items = await res.json();
  const total = Number(res.headers.get('X-Total-Count') ?? items.length);
  return { items, total };
}

export async function getProblem(slug: string): Promise<ProblemDetail> {
  const res = await fetch(`${BASE}/problems/${slug}`);
  if (!res.ok) throw new Error(`Problem '${slug}' not found`);
  return res.json();
}

export async function getHints(slug: string, maxLevel: number): Promise<HintOut[]> {
  const res = await fetch(`${BASE}/problems/${slug}/hints?max_level=${maxLevel}`);
  if (!res.ok) throw new Error('Failed to load hints');
  return res.json();
}

export async function runProblem(slug: string, body: RunRequest): Promise<RunResult> {
  const res = await fetch(`${BASE}/problems/${slug}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? 'Run failed');
  }
  return res.json();
}

export async function submitSolution(body: {
  problem_id: string;
  language: string;
  code: string;
  user_id?: string;
}): Promise<SubmissionOut> {
  const res = await fetch(`${BASE}/submissions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: 'anonymous', ...body }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? 'Submission failed');
  }
  return res.json();
}

export async function listSubmissions(params: {
  problem_id?: string;
  user_id?: string;
}): Promise<SubmissionOut[]> {
  const q = new URLSearchParams({ user_id: params.user_id ?? 'anonymous' });
  if (params.problem_id) q.set('problem_id', params.problem_id);
  const res = await fetch(`${BASE}/submissions?${q}`);
  if (!res.ok) throw new Error('Failed to load submissions');
  return res.json();
}

export async function getSubmission(id: string): Promise<SubmissionOut> {
  const res = await fetch(`${BASE}/submissions/${id}`);
  if (!res.ok) throw new Error('Failed to load submission');
  return res.json();
}

export async function getSubmissionQuality(id: string): Promise<SubmissionQualityOut> {
  const res = await fetch(`${BASE}/submissions/${id}/quality`);
  if (!res.ok) throw new Error('Failed to load submission quality');
  return res.json();
}

export async function getProgress(userId = 'anonymous'): Promise<ProgressOut> {
  const res = await fetch(`${BASE}/progress/${userId}`);
  if (!res.ok) throw new Error('Failed to load progress');
  return res.json();
}

export async function getDailyChallenge(): Promise<DailyChallengeOut> {
  const res = await fetch(`${BASE}/challenges/today`);
  if (!res.ok) throw new Error('No daily challenge today');
  return res.json();
}
