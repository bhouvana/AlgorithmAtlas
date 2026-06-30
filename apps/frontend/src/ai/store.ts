import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  AtlasMode, ChatMessage, Conversation, EditorWrite,
  InterviewProblem, InterviewState, SimulationCommand,
} from './types';

// ── helpers ───────────────────────────────────────────────────────────────────

function uid() { return crypto.randomUUID(); }

function newConv(title = 'New conversation'): Conversation {
  const now = Date.now();
  return { id: uid(), title, messages: [], createdAt: now, updatedAt: now };
}

function deriveTitle(msg: string): string {
  const t = msg.trim().slice(0, 58);
  return t.length < msg.trim().length ? t + '…' : t;
}

interface Pos { x: number; y: number }
interface Sz  { width: number; height: number }

const DEFAULT_SIZE: Sz = { width: 460, height: 640 };

function defaultPos(): Pos {
  if (typeof window === 'undefined') return { x: 60, y: 60 };
  return { x: Math.max(20, window.innerWidth - 500), y: Math.max(20, window.innerHeight - 700) };
}

// ── state shape ───────────────────────────────────────────────────────────────

interface AtlasState {
  isOpen: boolean;
  mode: AtlasMode;
  leftOpen: boolean;
  rightOpen: boolean;

  conversations: Conversation[];
  activeConversationId: string | null;
  isStreaming: boolean;

  position: Pos;
  size: Sz;

  pendingCommands: SimulationCommand[];
  pendingEditorWrite: EditorWrite | null;
  pendingNavigation: string | null;
  proactiveHint: string | null;
  hasNewSuggestion: boolean;
  interview: InterviewState;

  // ── actions ──
  open: (mode?: AtlasMode) => void;
  close: () => void;
  toggle: (mode?: AtlasMode) => void;
  setMode: (mode: AtlasMode) => void;
  toggleLeft: () => void;
  toggleRight: () => void;

  newConversation: () => string;
  selectConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
  pinConversation: (id: string) => void;
  clearConversation: () => void;

  addMessage: (msg: ChatMessage) => void;
  appendToLastAssistant: (token: string) => void;
  markLastAssistantDone: () => void;
  setStreaming: (v: boolean) => void;

  setPosition: (pos: Pos) => void;
  setSize: (size: Sz) => void;

  addPendingCommands: (cmds: SimulationCommand[]) => void;
  clearPendingCommands: () => void;
  setPendingEditorWrite: (w: EditorWrite | null) => void;
  setPendingNavigation: (path: string | null) => void;
  setProactiveHint: (hint: string | null) => void;
  setHasNewSuggestion: (v: boolean) => void;

  startInterview: (problem: InterviewProblem) => void;
  revealNextHint: () => void;
  endInterview: () => void;
}

// ── store ─────────────────────────────────────────────────────────────────────

export const useAtlasStore = create<AtlasState>()(
  persist(
    (set, get) => {
      const patchActiveConv = (fn: (c: Conversation) => Conversation) =>
        set((s) => {
          const id = s.activeConversationId;
          if (!id) return {};
          return { conversations: s.conversations.map((c) => (c.id === id ? fn(c) : c)) };
        });

      const ensureActive = (s: AtlasState): Pick<AtlasState, 'conversations' | 'activeConversationId'> => {
        if (s.activeConversationId && s.conversations.find(c => c.id === s.activeConversationId)) {
          return { conversations: s.conversations, activeConversationId: s.activeConversationId };
        }
        const conv = newConv();
        return { conversations: [conv, ...s.conversations], activeConversationId: conv.id };
      };

      return {
        isOpen: false,
        mode: 'panel',
        leftOpen: false,
        rightOpen: true,
        conversations: [],
        activeConversationId: null,
        isStreaming: false,
        position: defaultPos(),
        size: DEFAULT_SIZE,
        pendingCommands: [],
        pendingEditorWrite: null,
        pendingNavigation: null,
        proactiveHint: null,
        hasNewSuggestion: false,
        interview: { active: false, problem: null, startedAt: null, hintsRevealed: 0 },

        open: (mode) =>
          set((s) => ({
            isOpen: true,
            hasNewSuggestion: false,
            mode: mode ?? s.mode,
            ...ensureActive(s),
          })),

        close: () => set({ isOpen: false }),

        toggle: (mode) => {
          const { isOpen } = get();
          if (isOpen) set({ isOpen: false });
          else get().open(mode);
        },

        setMode: (mode) => set({ mode }),
        toggleLeft:  () => set((s) => ({ leftOpen:  !s.leftOpen  })),
        toggleRight: () => set((s) => ({ rightOpen: !s.rightOpen })),

        newConversation: () => {
          const conv = newConv();
          set((s) => ({ conversations: [conv, ...s.conversations], activeConversationId: conv.id }));
          return conv.id;
        },

        selectConversation: (id) => set({ activeConversationId: id }),

        deleteConversation: (id) =>
          set((s) => {
            const convs = s.conversations.filter((c) => c.id !== id);
            const activeId = s.activeConversationId === id ? (convs[0]?.id ?? null) : s.activeConversationId;
            return { conversations: convs, activeConversationId: activeId };
          }),

        pinConversation: (id) =>
          set((s) => ({
            conversations: s.conversations.map((c) => (c.id === id ? { ...c, pinned: !c.pinned } : c)),
          })),

        clearConversation: () =>
          patchActiveConv((c) => ({ ...c, messages: [], title: 'New conversation', updatedAt: Date.now() })),

        addMessage: (msg) =>
          patchActiveConv((c) => {
            const isFirstUser = msg.role === 'user' && c.messages.filter((m) => m.role === 'user').length === 0;
            return {
              ...c,
              messages: [...c.messages, msg],
              title: isFirstUser && c.title === 'New conversation' ? deriveTitle(msg.content) : c.title,
              updatedAt: Date.now(),
            };
          }),

        appendToLastAssistant: (token) =>
          patchActiveConv((c) => {
            const msgs = [...c.messages];
            const last = msgs[msgs.length - 1];
            if (last?.role === 'assistant') msgs[msgs.length - 1] = { ...last, content: last.content + token };
            return { ...c, messages: msgs };
          }),

        markLastAssistantDone: () => {
          patchActiveConv((c) => {
            const msgs = [...c.messages];
            const last = msgs[msgs.length - 1];
            if (last?.role === 'assistant') msgs[msgs.length - 1] = { ...last, streaming: false };
            return { ...c, messages: msgs };
          });
          set({ isStreaming: false });
        },

        setStreaming: (v) => set({ isStreaming: v }),
        setPosition:  (pos)  => set({ position: pos }),
        setSize:      (size) => set({ size }),

        addPendingCommands: (cmds) => set((s) => ({ pendingCommands: [...s.pendingCommands, ...cmds] })),
        clearPendingCommands: () => set({ pendingCommands: [] }),
        setPendingEditorWrite: (w) => set({ pendingEditorWrite: w }),
        setPendingNavigation:  (path) => set({ pendingNavigation: path }),
        setProactiveHint:    (hint) => set({ proactiveHint: hint }),
        setHasNewSuggestion: (v)    => set({ hasNewSuggestion: v }),

        startInterview: (problem) =>
          set({ interview: { active: true, problem, startedAt: Date.now(), hintsRevealed: 0 } }),

        revealNextHint: () =>
          set((s) => ({
            interview: {
              ...s.interview,
              hintsRevealed: Math.min(s.interview.hintsRevealed + 1, s.interview.problem?.hints.length ?? 0),
            },
          })),

        endInterview: () =>
          set({ interview: { active: false, problem: null, startedAt: null, hintsRevealed: 0 } }),
      };
    },
    {
      name: 'atlas-ai-v2',
      partialize: (s) => ({
        mode: s.mode,
        conversations: s.conversations,
        activeConversationId: s.activeConversationId,
        position: s.position,
        size: s.size,
        leftOpen: s.leftOpen,
        rightOpen: s.rightOpen,
      }),
      // On rehydration, clear any stale streaming state left over from a crash/reload
      onRehydrateStorage: () => (state) => {
        if (!state) return;
        state.isStreaming = false;
        state.pendingEditorWrite = null;
        state.pendingNavigation = null;
        state.conversations = state.conversations.map((c) => ({
          ...c,
          messages: c.messages.map((m) =>
            m.streaming ? { ...m, streaming: false, content: m.content || '⚡ Response interrupted.' } : m,
          ),
        }));
      },
    },
  ),
);
