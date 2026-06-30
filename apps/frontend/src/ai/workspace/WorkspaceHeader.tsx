import { motion } from 'framer-motion';
import {
  X, Plus, PanelRight, Maximize2, LayoutDashboard,
  Expand, ChevronLeft, ChevronRight,
} from 'lucide-react';
import { useAtlasStore } from '../store';
import type { AtlasMode } from '../types';

interface ModeBtn { id: AtlasMode; icon: React.ReactNode; title: string }

const MODES: ModeBtn[] = [
  { id: 'panel',     icon: <PanelRight className="w-3.5 h-3.5" />,     title: 'Side panel'       },
  { id: 'floating',  icon: <Maximize2  className="w-3.5 h-3.5" />,     title: 'Floating window'  },
  { id: 'workspace', icon: <LayoutDashboard className="w-3.5 h-3.5" />, title: 'Workspace'        },
  { id: 'immersive', icon: <Expand className="w-3.5 h-3.5" />,         title: 'Immersive'        },
];

interface Props {
  mode: AtlasMode;
  draggable?: boolean;
}

export function WorkspaceHeader({ mode, draggable }: Props) {
  const { close, setMode, newConversation, leftOpen, rightOpen, toggleLeft, toggleRight, isStreaming } = useAtlasStore();

  return (
    <div
      className="flex items-center gap-2 px-3 flex-shrink-0 select-none"
      style={{
        height: 48,
        borderBottom: '1px solid rgba(255,255,255,0.05)',
        cursor: draggable ? 'grab' : 'default',
        background: 'rgba(10,10,20,0.6)',
        backdropFilter: 'blur(12px)',
      }}
    >
      {/* Logo */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <div
          className="w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
            <path d="M12 2.5L13.09 9.26L19.5 12L13.09 14.74L12 21.5L10.91 14.74L4.5 12L10.91 9.26L12 2.5Z"
              fill="white" fillOpacity="0.95" />
          </svg>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-[13px] font-semibold text-zinc-200">Atlas</span>
          {isStreaming && (
            <motion.span
              animate={{ opacity: [1, 0.4, 1] }}
              transition={{ duration: 1.1, repeat: Infinity }}
              className="text-[10px] text-indigo-400 font-mono"
            >
              thinking…
            </motion.span>
          )}
        </div>
      </div>

      <div className="flex-1" />

      {/* Mode switcher */}
      <div
        className="flex items-center gap-0.5 rounded-lg p-0.5"
        style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)' }}
      >
        {MODES.map(({ id, icon, title }) => (
          <button
            key={id}
            onClick={() => setMode(id)}
            title={title}
            className="p-1.5 rounded-md transition-all"
            style={{
              background: mode === id ? 'rgba(99,102,241,0.25)' : 'transparent',
              color: mode === id ? '#818cf8' : '#52525b',
            }}
          >
            {icon}
          </button>
        ))}
      </div>

      {/* Sidebar toggles (visible in workspace/immersive) */}
      {(mode === 'workspace' || mode === 'immersive') && (
        <>
          <button
            onClick={toggleLeft}
            title="Toggle history"
            className="p-1.5 rounded-lg transition-colors"
            style={{ color: leftOpen ? '#818cf8' : '#3f3f46' }}
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            onClick={toggleRight}
            title="Toggle context"
            className="p-1.5 rounded-lg transition-colors"
            style={{ color: rightOpen ? '#818cf8' : '#3f3f46' }}
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </>
      )}

      {/* New conversation */}
      <button
        onClick={newConversation}
        title="New conversation"
        className="p-1.5 rounded-lg text-zinc-600 hover:text-zinc-300 transition-colors"
      >
        <Plus className="w-4 h-4" />
      </button>

      {/* Close */}
      <button
        onClick={close}
        className="p-1.5 rounded-lg text-zinc-700 hover:text-zinc-300 transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
