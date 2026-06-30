import { useRef, useEffect, useState, useCallback } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Send, Square, Trash2, Sparkles } from 'lucide-react';
import { useAtlasStore } from '../store';
import { streamChat } from '../api';
import type { AtlasContext } from '../types';
import { MessageBubble } from '../components/MessageBubble';
import { ActionCards } from './ActionCards';
import { ContextCards } from './ContextCards';
import { InterviewOverlay } from '../components/InterviewOverlay';

interface Props {
  context: AtlasContext;
  showContextInline?: boolean;
}

export function ConversationView({ context, showContextInline }: Props) {
  const {
    conversations, activeConversationId, isStreaming, interview,
    addMessage, appendToLastAssistant, markLastAssistantDone,
    setStreaming, addPendingCommands, startInterview, clearConversation,
    setPendingEditorWrite, setPendingNavigation,
  } = useAtlasStore();

  const activeConv = conversations.find((c) => c.id === activeConversationId);
  const messages = activeConv?.messages ?? [];

  const [input, setInput] = useState('');
  const scrollRef    = useRef<HTMLDivElement>(null);
  const inputRef     = useRef<HTMLTextAreaElement>(null);
  const abortRef     = useRef<AbortController | null>(null);
  const timeoutRef   = useRef<ReturnType<typeof setTimeout> | null>(null);
  const prevCount    = useRef(0);

  const resetStreamTimeout = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
      abortRef.current?.abort();
      markLastAssistantDone();
      appendToLastAssistant('\n\n*Atlas timed out — try again.*');
    }, 60_000);
  };

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const isNearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 120;
    if (isNearBottom || messages.length !== prevCount.current) {
      el.scrollTop = el.scrollHeight;
    }
    prevCount.current = messages.length;
  }, [messages]);

  useEffect(() => {
    setTimeout(() => inputRef.current?.focus(), 100);
  }, [activeConversationId]);

  const send = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isStreaming) return;
    setInput('');

    const userId = crypto.randomUUID();
    addMessage({ id: userId, role: 'user', content: trimmed });
    addMessage({ id: crypto.randomUUID(), role: 'assistant', content: '', streaming: true });
    setStreaming(true);

    abortRef.current = new AbortController();
    resetStreamTimeout();
    try {
      for await (const ev of streamChat(trimmed, context, messages, abortRef.current.signal)) {
        switch (ev.type) {
          case 'token':
            appendToLastAssistant(ev.content);
            resetStreamTimeout();
            break;
          case 'commands':        addPendingCommands(ev.commands); break;
          case 'interview_start': startInterview(ev.problem); break;
          case 'editor_write':    setPendingEditorWrite({ code: ev.code, language: ev.language }); break;
          case 'navigate':        setPendingNavigation(ev.path); break;
          case 'error':
            appendToLastAssistant(`\n\n**Error:** ${ev.message}`);
            break;
          default: break;
        }
      }
    } finally {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      markLastAssistantDone();
    }
  }, [isStreaming, context, messages, addMessage, appendToLastAssistant, markLastAssistantDone, setStreaming, addPendingCommands, startInterview]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); send(input); }
  };

  const autoResize = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 140)}px`;
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Interview overlay */}
      <AnimatePresence>
        {interview.active && <InterviewOverlay />}
      </AnimatePresence>

      {/* Messages / empty state */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto min-h-0"
        style={{ scrollbarWidth: 'thin', scrollbarColor: '#1f1f2e transparent' }}
      >
        {isEmpty ? (
          <EmptyState context={context} onAction={send} showContextInline={showContextInline} />
        ) : (
          <div className="px-4 py-4 space-y-4">
            {showContextInline && <ContextCards context={context} />}
            {messages.map((msg, i) => (
              <MessageBubble
                key={msg.id}
                message={msg}
                isNew={i === messages.length - 1 && msg.role === 'assistant'}
              />
            ))}
          </div>
        )}
      </div>

      {/* Compact action chips when conversation is active */}
      {!isEmpty && (
        <div className="flex-shrink-0 border-t" style={{ borderColor: 'rgba(255,255,255,0.05)' }}>
          <div className="pt-2">
            <ActionCards context={context} onAction={send} disabled={isStreaming} compact />
          </div>
        </div>
      )}

      {/* Input */}
      <div className="flex-shrink-0 px-3 pb-3 pt-1">
        <div
          className="flex items-end gap-2 rounded-2xl transition-all"
          style={{
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(255,255,255,0.08)',
          }}
          onFocus={() => {}}
        >
          <textarea
            ref={inputRef}
            value={input}
            onChange={autoResize}
            onKeyDown={handleKeyDown}
            placeholder="Ask Atlas anything…"
            disabled={isStreaming}
            rows={1}
            className="flex-1 bg-transparent resize-none outline-none px-3.5 py-3 text-[13.5px] text-zinc-200 placeholder-zinc-600 leading-relaxed disabled:opacity-40"
            style={{ scrollbarWidth: 'none', minHeight: 44, maxHeight: 140 }}
          />
          <div className="flex items-center gap-1 pr-2 pb-2 flex-shrink-0">
            {!isEmpty && (
              <button
                onClick={clearConversation}
                className="p-1.5 rounded-xl text-zinc-700 hover:text-zinc-400 transition-colors"
                title="Clear conversation"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            )}
            {isStreaming ? (
              <button
                onClick={() => { abortRef.current?.abort(); markLastAssistantDone(); }}
                className="p-2 rounded-xl transition-all"
                style={{ background: 'rgba(239,68,68,0.15)', color: '#ef4444' }}
              >
                <Square className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={() => send(input)}
                disabled={!input.trim()}
                className="p-2 rounded-xl transition-all disabled:opacity-30"
                style={{ background: 'rgba(99,102,241,0.9)', color: 'white' }}
              >
                <Send className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
        <div className="flex items-center justify-between px-1 mt-1.5">
          <span className="text-[10px] text-zinc-700">
            <kbd className="px-1 py-0.5 rounded bg-white/5 font-mono text-[9px]">⌘↵</kbd> send
          </span>
          <span className="text-[10px] text-zinc-700 flex items-center gap-1">
            <Sparkles className="w-2.5 h-2.5 text-indigo-600" />
            Atlas AI
          </span>
        </div>
      </div>
    </div>
  );
}

// ── Empty state ───────────────────────────────────────────────────────────────

function EmptyState({
  context, onAction, showContextInline,
}: { context: AtlasContext; onAction: (m: string) => void; showContextInline?: boolean }) {
  return (
    <div className="flex flex-col px-4 pt-6 pb-2 gap-6">
      {/* Greeting */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="text-center"
      >
        <div
          className="w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-3"
          style={{
            background: 'linear-gradient(145deg, rgba(99,102,241,0.25), rgba(139,92,246,0.15))',
            border: '1px solid rgba(99,102,241,0.2)',
          }}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M12 2.5L13.09 9.26L19.5 12L13.09 14.74L12 21.5L10.91 14.74L4.5 12L10.91 9.26L12 2.5Z"
              fill="url(#g)" />
            <defs>
              <linearGradient id="g" x1="4.5" y1="2.5" x2="19.5" y2="21.5" gradientUnits="userSpaceOnUse">
                <stop stopColor="#818cf8" />
                <stop offset="1" stopColor="#a78bfa" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <h2 className="text-[15px] font-semibold text-zinc-200">Atlas AI</h2>
        <p className="text-[12px] text-zinc-600 mt-0.5 leading-snug">
          I already know what you're working on.<br />Ask me anything.
        </p>
      </motion.div>

      {/* Context cards */}
      {showContextInline && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.15 }}
        >
          <ContextCards context={context} />
        </motion.div>
      )}

      {/* Suggested actions */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <ActionCards context={context} onAction={onAction} />
      </motion.div>
    </div>
  );
}
