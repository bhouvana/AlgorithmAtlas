import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { supportsFunctionMode } from '../api/problems';
import type { ExecutionMode, ProblemDetail, ProgressOut, RunResult } from '../api/problems';

// Program Mode fallback invariant: a requested/persisted mode of "function"
// must never be honored for a problem/language combination that doesn't
// genuinely support it (missing contract, missing starter, stale
// localStorage from before a problem lost its contract, etc). Program Mode
// must always be reachable regardless of Function Mode's state.
function resolveMode(problem: ProblemDetail, language: string, requested: ExecutionMode): ExecutionMode {
  return requested === 'function' && !supportsFunctionMode(problem, language) ? 'program' : requested;
}

type Difficulty = 'All' | 'Easy' | 'Medium' | 'Hard';
export type ConsoleTab = 'testcase' | 'result' | 'console';

export interface CustomCase {
  id: string;
  // Program Mode
  input_data: string;
  expected_output: string | null;
  // Function Mode -- raw JSON text the user edits directly (e.g. '{"nums":
  // [1,2,3], "k": 2}'); parsed + validated against the contract server-side
  // before execution, never trusted client-side.
  arguments_json: string;
  expected_return_json: string | null;
}

function newCustomCase(): CustomCase {
  return {
    id: `custom-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    input_data: '', expected_output: null,
    arguments_json: '', expected_return_json: null,
  };
}

// Draft identity: a problem's code is kept independently per (language,
// execution mode) pair so switching either NEVER discards the other's code
// (Phase 2/Language Switching -- e.g. python:function, python:program,
// javascript:function are all independently preservable).
function draftKey(problemId: string, language: string, mode: ExecutionMode): string {
  return `${problemId}:${language}:${mode}`;
}

function starterFor(problem: ProblemDetail, language: string, mode: ExecutionMode): string {
  return (mode === 'function' ? problem.starter_code_function?.[language] : problem.starter_code?.[language]) ?? '';
}

interface AtlasCodeState {
  // Catalog filters
  selectedDifficulty: Difficulty;
  selectedCategory: string;
  searchQuery: string;

  // Current problem being solved
  currentProblem: ProblemDetail | null;
  currentLanguage: string;
  executionMode: ExecutionMode;
  editorCode: string;
  // Every (problemId:language:mode) draft the user has typed, so switching
  // mode or language never discards the other's code (Phase 2/Language
  // Switching). Persisted locally like customCasesByProblem below.
  draftsByKey: Record<string, string>;
  // Per-problem "last mode used" -- Default Mode resolution order #2, and
  // what makes a page refresh preserve the current mode (Phase 20).
  lastModeByProblem: Record<string, ExecutionMode>;

  // Run state (fast iteration -- the only judging path this workspace exposes)
  isRunning: boolean;
  lastRunResult: RunResult | null;

  // Bottom execution console
  consoleTab: ConsoleTab;
  consoleCollapsed: boolean;
  consoleHeightPct: number;     // % of the editor-workspace height given to the console
  problemPaneWidthPx: number;   // problem pane <-> editor divider position
  activeCaseKey: string | null; // which case is expanded in the Test Result tab

  // Testcase tab: selection + per-problem custom scratch cases (persisted locally)
  selectedCaseIndices: number[];
  customCasesByProblem: Record<string, CustomCase[]>;

  // Hints revealed
  revealedHintLevel: number;

  // User progress (lazy loaded)
  progress: ProgressOut | null;

  // Actions
  setDifficulty: (d: Difficulty) => void;
  setCategory: (c: string) => void;
  setSearch: (q: string) => void;
  setProblem: (p: ProblemDetail) => void;
  setLanguage: (lang: string) => void;
  setExecutionMode: (mode: ExecutionMode) => void;
  setCode: (code: string) => void;
  setRunning: (v: boolean) => void;
  setLastRunResult: (r: RunResult | null) => void;
  revealNextHint: () => void;
  resetHints: () => void;
  setProgress: (p: ProgressOut) => void;
  resetEditor: () => void;

  setConsoleTab: (t: ConsoleTab) => void;
  toggleConsoleCollapsed: () => void;
  setConsoleHeightPct: (n: number) => void;
  setProblemPaneWidthPx: (n: number) => void;
  // Delta (not absolute) variants for drag-resize: each pointermove event
  // during a single drag gesture must accumulate against the LATEST store
  // state, not a value closed over when the drag started -- see useResizeDrag
  // usage in ProblemPage.tsx.
  adjustConsoleHeightPct: (deltaPct: number) => void;
  adjustProblemPaneWidthPx: (deltaPx: number) => void;
  setActiveCaseKey: (k: string | null) => void;

  toggleSelectedCase: (i: number) => void;
  clearSelectedCases: () => void;

  addCustomCase: (problemId: string) => void;
  updateCustomCase: (problemId: string, id: string, patch: Partial<CustomCase>) => void;
  removeCustomCase: (problemId: string, id: string) => void;
  duplicateCustomCase: (problemId: string, id: string) => void;
}

export const useAtlasCodeStore = create<AtlasCodeState>()(
  persist(
    (set, get) => ({
      selectedDifficulty: 'All',
      selectedCategory: 'all',
      searchQuery: '',

      currentProblem: null,
      currentLanguage: 'python',
      executionMode: 'program',
      editorCode: '',
      draftsByKey: {},
      lastModeByProblem: {},

      isRunning: false,
      lastRunResult: null,

      consoleTab: 'testcase',
      consoleCollapsed: false,
      consoleHeightPct: 40,
      problemPaneWidthPx: 380,
      activeCaseKey: null,

      selectedCaseIndices: [],
      customCasesByProblem: {},

      revealedHintLevel: 0,
      progress: null,

      setDifficulty: (d) => set({ selectedDifficulty: d }),
      setCategory: (c) => set({ selectedCategory: c }),
      setSearch: (q) => set({ searchQuery: q }),

      setProblem: (p) => {
        const prevId = get().currentProblem?.id;
        const isNewProblem = prevId !== p.id;

        // Keep language selected if the new problem supports it (in either
        // mode), otherwise fall back to the first language it has ANY
        // template for.
        let language = get().currentLanguage;
        if (isNewProblem) {
          const langs = Object.keys(p.starter_code || {});
          if (langs.length > 0 && !langs.includes(language)) {
            language = langs.includes('python') ? 'python' : langs[0];
          }
        }

        // Default Mode resolution (Phase 2): last mode used for THIS problem,
        // else Program Mode -- never destroys existing Program-mode users by
        // defaulting a never-visited problem into Function Mode. Always run
        // through resolveMode so a stale "function" preference (or a
        // problem/language combination that never supported it) can't crash
        // the workspace -- Program Mode is the guaranteed fallback.
        const requestedMode: ExecutionMode = isNewProblem
          ? (get().lastModeByProblem[p.id] ?? 'program')
          : get().executionMode;
        const mode = resolveMode(p, language, requestedMode);

        const key = draftKey(p.id, language, mode);
        const editorCode = get().draftsByKey[key] ?? starterFor(p, language, mode);

        set({
          currentProblem: p,
          currentLanguage: language,
          executionMode: mode,
          editorCode,
          lastRunResult: null,
          revealedHintLevel: 0,
          selectedCaseIndices: [],
          activeCaseKey: null,
          consoleTab: 'testcase',
        });
      },

      setLanguage: (lang) => {
        const p = get().currentProblem;
        if (!p) return;
        // Switching language can invalidate Function Mode support (Phase 32:
        // language switch must never blank the page) -- fall back to Program
        // Mode if the new language doesn't support it for this problem.
        const mode = resolveMode(p, lang, get().executionMode);
        const key = draftKey(p.id, lang, mode);
        set({
          currentLanguage: lang,
          executionMode: mode,
          editorCode: get().draftsByKey[key] ?? starterFor(p, lang, mode),
          lastRunResult: null,
        });
      },

      setExecutionMode: (requestedMode) => {
        const p = get().currentProblem;
        if (!p) return;
        const lang = get().currentLanguage;
        const mode = resolveMode(p, lang, requestedMode);
        const key = draftKey(p.id, lang, mode);
        set((s) => ({
          executionMode: mode,
          editorCode: s.draftsByKey[key] ?? starterFor(p, lang, mode),
          lastRunResult: null,
          consoleTab: 'testcase',
          lastModeByProblem: { ...s.lastModeByProblem, [p.id]: mode },
        }));
      },

      setCode: (code) => {
        const { currentProblem, currentLanguage, executionMode } = get();
        set((s) => ({
          editorCode: code,
          // Mirror every keystroke into the draft map immediately -- draftsByKey
          // is the single source of truth for "what's saved", not something
          // written only at switch-time (which would resurrect stale code
          // after a Reset, since Reset only touches editorCode otherwise).
          draftsByKey: currentProblem
            ? { ...s.draftsByKey, [draftKey(currentProblem.id, currentLanguage, executionMode)]: code }
            : s.draftsByKey,
        }));
      },
      setRunning: (v) => set({ isRunning: v }),
      setLastRunResult: (r) => set({ lastRunResult: r }),

      revealNextHint: () => set((s) => ({ revealedHintLevel: s.revealedHintLevel + 1 })),
      resetHints: () => set({ revealedHintLevel: 0 }),

      setProgress: (p) => set({ progress: p }),

      resetEditor: () => {
        const { currentProblem, currentLanguage, executionMode } = get();
        if (!currentProblem) return;
        const starter = starterFor(currentProblem, currentLanguage, executionMode);
        set((s) => ({
          editorCode: starter,
          lastRunResult: null,
          // Reset must stick -- also overwrite the draft, otherwise switching
          // mode away and back would resurrect the pre-reset code.
          draftsByKey: {
            ...s.draftsByKey,
            [draftKey(currentProblem.id, currentLanguage, executionMode)]: starter,
          },
        }));
      },

      setConsoleTab: (t) => set({ consoleTab: t }),
      toggleConsoleCollapsed: () => set((s) => ({ consoleCollapsed: !s.consoleCollapsed })),
      setConsoleHeightPct: (n) => set({ consoleHeightPct: Math.min(80, Math.max(15, n)) }),
      setProblemPaneWidthPx: (n) => set({ problemPaneWidthPx: Math.min(720, Math.max(260, n)) }),
      adjustConsoleHeightPct: (deltaPct) =>
        set((s) => ({ consoleHeightPct: Math.min(80, Math.max(15, s.consoleHeightPct + deltaPct)) })),
      adjustProblemPaneWidthPx: (deltaPx) =>
        set((s) => ({ problemPaneWidthPx: Math.min(720, Math.max(260, s.problemPaneWidthPx + deltaPx)) })),
      setActiveCaseKey: (k) => set({ activeCaseKey: k }),

      toggleSelectedCase: (i) =>
        set((s) => ({
          selectedCaseIndices: s.selectedCaseIndices.includes(i)
            ? s.selectedCaseIndices.filter((x) => x !== i)
            : [...s.selectedCaseIndices, i].sort((a, b) => a - b),
        })),
      clearSelectedCases: () => set({ selectedCaseIndices: [] }),

      addCustomCase: (problemId) =>
        set((s) => ({
          customCasesByProblem: {
            ...s.customCasesByProblem,
            [problemId]: [...(s.customCasesByProblem[problemId] ?? []), newCustomCase()],
          },
        })),
      updateCustomCase: (problemId, id, patch) =>
        set((s) => ({
          customCasesByProblem: {
            ...s.customCasesByProblem,
            [problemId]: (s.customCasesByProblem[problemId] ?? []).map((c) =>
              c.id === id ? { ...c, ...patch } : c
            ),
          },
        })),
      removeCustomCase: (problemId, id) =>
        set((s) => ({
          customCasesByProblem: {
            ...s.customCasesByProblem,
            [problemId]: (s.customCasesByProblem[problemId] ?? []).filter((c) => c.id !== id),
          },
        })),
      duplicateCustomCase: (problemId, id) =>
        set((s) => {
          const list = s.customCasesByProblem[problemId] ?? [];
          const found = list.find((c) => c.id === id);
          if (!found) return {};
          return {
            customCasesByProblem: {
              ...s.customCasesByProblem,
              [problemId]: [...list, { ...found, id: newCustomCase().id }],
            },
          };
        }),
    }),
    {
      name: 'atlascode-workspace',
      // Only layout preferences and user-authored scratch cases persist
      // across sessions -- never problem/submission/run state, which is
      // always re-fetched or re-derived fresh.
      partialize: (s) => ({
        consoleHeightPct: s.consoleHeightPct,
        consoleCollapsed: s.consoleCollapsed,
        problemPaneWidthPx: s.problemPaneWidthPx,
        customCasesByProblem: s.customCasesByProblem,
        // Function/Program drafts + per-problem mode memory -- what makes a
        // refresh preserve both the current mode and unsaved code (Phase 20).
        draftsByKey: s.draftsByKey,
        lastModeByProblem: s.lastModeByProblem,
      }),
    }
  )
);
