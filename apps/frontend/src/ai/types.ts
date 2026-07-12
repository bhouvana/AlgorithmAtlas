// ── Platform context sent with every request ──────────────────────────────────

export interface ComplexityInfo {
  time_best: string;
  time_average: string;
  time_worst: string;
  space: string;
}

export interface AlgorithmContext {
  slug: string;
  name: string;
  category: string;
  visualization_type: string;
  complexity?: ComplexityInfo;
  description?: string;
}

export interface SimulationContext {
  status: 'created' | 'paused' | 'running' | 'completed' | 'error';
  currentFrameIndex: number;
  totalFrames: number | null;
  playbackSpeed: number;
  currentFrame: Record<string, unknown> | null;
  eventLabel: string | null;
}

export interface NotebookContext {
  language: string;
  source: string;
  lastOutput: string;
  lastError: string;
}

export interface ProblemContext {
  slug: string;
  title: string;
  difficulty: string;
  language: string;
  // Which Run contract is active -- Atlas AI must not give Program Mode
  // advice ("read input using sys.stdin") while the user is in Function
  // Mode, or vice versa (Phase 21).
  executionMode: 'function' | 'program';
  // Only populated in Function Mode -- e.g. "top_k_frequent(nums, k)".
  functionSignature: string | null;
  source: string;
  // Only ever derived from Run (visible/selected/custom cases) -- this
  // workspace has no Submit/hidden-test path, so there is no hidden data to
  // ever accidentally include here.
  lastRunSummary: { passed: number; failed: number; total: number } | null;
  lastRunVerdict: string | null;
  firstFailingCase: {
    label: string; input: string; expected: string | null; actual: string;
  } | null;
}

export interface LessonContext {
  id: string;
  title: string;
  track: string;
  difficulty: string;
  activeSection: string;
}

export interface LearningProgressContext {
  xp: number;
  level: number;
  completedLessons: string[];
  currentStreak: number;
}

export interface ComparisonContext {
  algorithmA: string | null;
  algorithmB: string | null;
}

export interface AtlasContext {
  page: string;
  userId: string;
  algorithm?: AlgorithmContext;
  simulation?: SimulationContext;
  notebook?: NotebookContext;
  lesson?: LessonContext;
  learningProgress?: LearningProgressContext;
  comparison?: ComparisonContext;
  problem?: ProblemContext;
}

// ── Conversation ──────────────────────────────────────────────────────────────

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  streaming?: boolean;
  hasMermaid?: boolean;       // assistant message contains a mermaid block
  commands?: SimulationCommand[];
}

// ── SSE events from the backend ───────────────────────────────────────────────

export type SSEEvent =
  | { type: 'token';           content: string }
  | { type: 'commands';        commands: SimulationCommand[] }
  | { type: 'interview_start'; problem: InterviewProblem }
  | { type: 'editor_write';    code: string; language: string }
  | { type: 'navigate';        path: string }
  | { type: 'done' }
  | { type: 'error';           message: string };

export interface EditorWrite {
  code: string;
  language: string;
}

// ── Simulation commands ───────────────────────────────────────────────────────

export type SimulationCommand =
  | { action: 'play' }
  | { action: 'pause' }
  | { action: 'reset' }
  | { action: 'step_forward' }
  | { action: 'step_backward' }
  | { action: 'seek';      frame: number }
  | { action: 'set_speed'; value: number };

// ── Interview mode ────────────────────────────────────────────────────────────

export interface InterviewProblem {
  title: string;
  difficulty: 'easy' | 'medium' | 'hard';
  time_limit_minutes: number;
  description: string;
  examples: Array<{ input: string; output: string; explanation: string }>;
  hints: string[];
  evaluation_criteria: string[];
}

export interface InterviewState {
  active: boolean;
  problem: InterviewProblem | null;
  startedAt: number | null;    // Date.now() when interview started
  hintsRevealed: number;       // how many hints have been shown
}

// ── Quick actions ─────────────────────────────────────────────────────────────

export interface QuickAction {
  label: string;
  icon: string;
  message: string;
}

// ── Workspace ─────────────────────────────────────────────────────────────────

export type AtlasMode = 'panel' | 'floating' | 'workspace' | 'immersive';

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: number;
  updatedAt: number;
  pinned?: boolean;
  algorithmContext?: string;
}
