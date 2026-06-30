import { useState } from 'react';
import { motion } from 'framer-motion';
import { Plus, Pin, Trash2, MessageSquare, Search } from 'lucide-react';
import { useAtlasStore } from '../store';

function timeAgo(ts: number): string {
  const diff = Date.now() - ts;
  const m = Math.floor(diff / 60000);
  if (m < 1) return 'just now';
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

export function LeftSidebar() {
  const {
    conversations, activeConversationId,
    newConversation, selectConversation, deleteConversation, pinConversation,
  } = useAtlasStore();

  const [query, setQuery] = useState('');

  const pinned = conversations.filter((c) => c.pinned);
  const recent = conversations.filter((c) => !c.pinned && c.messages.length > 0);
  const filtered = query
    ? conversations.filter((c) => c.title.toLowerCase().includes(query.toLowerCase()))
    : null;

  const renderConv = (id: string, title: string, updatedAt: number, pinned?: boolean) => {
    const active = id === activeConversationId;
    return (
      <motion.div
        key={id}
        initial={{ opacity: 0, x: -6 }}
        animate={{ opacity: 1, x: 0 }}
        className="group relative flex items-center gap-2 px-2 py-2 rounded-xl cursor-pointer transition-all"
        style={{
          background: active ? 'rgba(99,102,241,0.12)' : 'transparent',
          border: active ? '1px solid rgba(99,102,241,0.2)' : '1px solid transparent',
        }}
        onClick={() => selectConversation(id)}
        onMouseEnter={(e) => {
          if (!active) (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.04)';
        }}
        onMouseLeave={(e) => {
          if (!active) (e.currentTarget as HTMLElement).style.background = 'transparent';
        }}
      >
        <MessageSquare className="w-3.5 h-3.5 flex-shrink-0 text-zinc-600" />
        <div className="flex-1 min-w-0">
          <p className={`text-[12px] truncate leading-tight ${active ? 'text-zinc-200 font-medium' : 'text-zinc-400'}`}>
            {title}
          </p>
          <p className="text-[10px] text-zinc-700">{timeAgo(updatedAt)}</p>
        </div>
        <div className="hidden group-hover:flex items-center gap-0.5">
          <button
            onClick={(e) => { e.stopPropagation(); pinConversation(id); }}
            className="p-1 rounded text-zinc-700 hover:text-zinc-400 transition-colors"
          >
            <Pin className={`w-3 h-3 ${pinned ? 'fill-indigo-500 text-indigo-500' : ''}`} />
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); deleteConversation(id); }}
            className="p-1 rounded text-zinc-700 hover:text-red-400 transition-colors"
          >
            <Trash2 className="w-3 h-3" />
          </button>
        </div>
      </motion.div>
    );
  };

  return (
    <div className="flex flex-col h-full overflow-hidden" style={{ borderRight: '1px solid rgba(255,255,255,0.05)' }}>
      {/* Header */}
      <div className="px-3 pt-3 pb-2 flex-shrink-0">
        <div className="flex items-center justify-between mb-2.5">
          <span className="text-[10px] font-semibold uppercase tracking-widest text-zinc-600">History</span>
          <button
            onClick={newConversation}
            className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] text-zinc-400 hover:text-white transition-colors"
            style={{ background: 'rgba(255,255,255,0.05)' }}
          >
            <Plus className="w-3 h-3" /> New
          </button>
        </div>
        {/* Search */}
        <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-xl" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }}>
          <Search className="w-3 h-3 text-zinc-600 flex-shrink-0" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search…"
            className="flex-1 bg-transparent text-[11px] text-zinc-300 placeholder-zinc-700 outline-none"
          />
        </div>
      </div>

      {/* Conversations */}
      <div className="flex-1 overflow-y-auto px-2 pb-2" style={{ scrollbarWidth: 'thin', scrollbarColor: '#27272a transparent' }}>
        {filtered ? (
          <div className="space-y-0.5">
            {filtered.map((c) => renderConv(c.id, c.title, c.updatedAt, c.pinned))}
            {filtered.length === 0 && (
              <p className="text-center text-[11px] text-zinc-700 py-6">No results</p>
            )}
          </div>
        ) : (
          <>
            {pinned.length > 0 && (
              <div className="mb-2">
                <p className="text-[9px] uppercase tracking-widest text-zinc-700 px-2 mb-1">Pinned</p>
                <div className="space-y-0.5">
                  {pinned.map((c) => renderConv(c.id, c.title, c.updatedAt, true))}
                </div>
              </div>
            )}
            {recent.length > 0 && (
              <div>
                <p className="text-[9px] uppercase tracking-widest text-zinc-700 px-2 mb-1">Recent</p>
                <div className="space-y-0.5">
                  {recent.map((c) => renderConv(c.id, c.title, c.updatedAt))}
                </div>
              </div>
            )}
            {conversations.length === 0 && (
              <div className="flex flex-col items-center justify-center h-32 gap-2 text-center">
                <MessageSquare className="w-6 h-6 text-zinc-800" />
                <p className="text-[11px] text-zinc-700">No conversations yet</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
