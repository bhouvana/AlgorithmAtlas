import { useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAtlasStore } from '../store';
import type { AtlasContext, AtlasMode } from '../types';
import { WorkspaceHeader } from '../workspace/WorkspaceHeader';
import { LeftSidebar } from '../workspace/LeftSidebar';
import { RightSidebar } from '../workspace/RightSidebar';
import { ConversationView } from '../workspace/ConversationView';

interface Props { context: AtlasContext }

const SPRING = { type: 'spring' as const, damping: 30, stiffness: 300, mass: 0.85 };

const SIDEBAR_SPRING = { type: 'spring' as const, damping: 28, stiffness: 280 };

function getModeRect(
  mode: AtlasMode,
  pos: { x: number; y: number },
  size: { width: number; height: number },
): React.CSSProperties {
  switch (mode) {
    case 'panel':
      return { right: 0, top: 0, bottom: 0, width: 420, borderRadius: '20px 0 0 20px' };
    case 'floating':
      return {
        left: pos.x, top: pos.y,
        width: size.width, height: size.height,
        borderRadius: 20,
      };
    case 'workspace':
    case 'immersive':
      return { inset: 0, borderRadius: 0 };
    default:
      return { right: 0, top: 0, bottom: 0, width: 420, borderRadius: '20px 0 0 20px' };
  }
}

export function AtlasWorkspace({ context }: Props) {
  const { mode, isOpen, position, size, setPosition, setSize, leftOpen, rightOpen } = useAtlasStore();

  const dragRef = useRef<{ sx: number; sy: number; spx: number; spy: number } | null>(null);
  const resizeRef = useRef<{ sx: number; sy: number; sw: number; sh: number } | null>(null);

  if (!isOpen) return null;

  const isWide = mode === 'workspace' || mode === 'immersive';
  const forceLeft = mode === 'immersive';
  const forceRight = mode === 'immersive';
  const showLeft = forceLeft || leftOpen;
  const showRight = forceRight || rightOpen;

  const modeRect = getModeRect(mode, position, size);

  const handleDragPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    if (mode !== 'floating') return;
    if ((e.target as HTMLElement).closest('button')) return;
    dragRef.current = { sx: e.clientX, sy: e.clientY, spx: position.x, spy: position.y };
    e.currentTarget.setPointerCapture(e.pointerId);
  };

  const handleDragPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!dragRef.current) return;
    setPosition({
      x: dragRef.current.spx + e.clientX - dragRef.current.sx,
      y: dragRef.current.spy + e.clientY - dragRef.current.sy,
    });
  };

  const handleDragPointerUp = () => { dragRef.current = null; };

  const handleResizePointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    if (mode !== 'floating') return;
    resizeRef.current = { sx: e.clientX, sy: e.clientY, sw: size.width, sh: size.height };
    e.currentTarget.setPointerCapture(e.pointerId);
    e.stopPropagation();
  };

  const handleResizePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!resizeRef.current) return;
    setSize({
      width:  Math.max(320, resizeRef.current.sw + e.clientX - resizeRef.current.sx),
      height: Math.max(400, resizeRef.current.sh + e.clientY - resizeRef.current.sy),
    });
  };

  const handleResizePointerUp = () => { resizeRef.current = null; };

  return (
    <motion.div
      layoutId="atlas-shell"
      layout
      transition={SPRING}
      style={{
        position: 'fixed',
        ...modeRect,
        zIndex: mode === 'immersive' ? 9999 : mode === 'floating' ? 200 : 100,
        background: 'linear-gradient(160deg, rgba(11,11,22,0.97) 0%, rgba(7,7,16,0.98) 100%)',
        backdropFilter: 'blur(28px) saturate(1.5)',
        border: '1px solid rgba(255,255,255,0.065)',
        boxShadow: mode === 'panel'
          ? '-24px 0 80px rgba(0,0,0,0.6)'
          : '0 40px 100px rgba(0,0,0,0.75), 0 0 0 0.5px rgba(255,255,255,0.04) inset',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {/* Drag handle wrapper — only header area is draggable in floating mode */}
      <div
        onPointerDown={handleDragPointerDown}
        onPointerMove={handleDragPointerMove}
        onPointerUp={handleDragPointerUp}
        style={{ cursor: mode === 'floating' ? 'grab' : 'default', flexShrink: 0 }}
      >
        <WorkspaceHeader mode={mode} />
      </div>

      {/* Body */}
      {isWide ? (
        <div className="flex flex-1 min-h-0">
          <AnimatePresence initial={false}>
            {showLeft && (
              <motion.div
                key="left"
                initial={{ width: 0, opacity: 0 }}
                animate={{ width: 220, opacity: 1 }}
                exit={{ width: 0, opacity: 0 }}
                transition={SIDEBAR_SPRING}
                style={{ overflow: 'hidden', flexShrink: 0 }}
              >
                <div style={{ width: 220, height: '100%' }}>
                  <LeftSidebar />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="flex-1 min-w-0 min-h-0">
            <ConversationView context={context} showContextInline={false} />
          </div>

          <AnimatePresence initial={false}>
            {showRight && (
              <motion.div
                key="right"
                initial={{ width: 0, opacity: 0 }}
                animate={{ width: 260, opacity: 1 }}
                exit={{ width: 0, opacity: 0 }}
                transition={SIDEBAR_SPRING}
                style={{ overflow: 'hidden', flexShrink: 0 }}
              >
                <div style={{ width: 260, height: '100%' }}>
                  <RightSidebar context={context} />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      ) : (
        <div className="flex-1 min-h-0">
          <ConversationView context={context} showContextInline />
        </div>
      )}

      {/* Resize handle (floating mode only) */}
      {mode === 'floating' && (
        <div
          onPointerDown={handleResizePointerDown}
          onPointerMove={handleResizePointerMove}
          onPointerUp={handleResizePointerUp}
          style={{
            position: 'absolute', bottom: 0, right: 0,
            width: 20, height: 20, cursor: 'se-resize',
            zIndex: 10,
          }}
        >
          <svg width="12" height="12" viewBox="0 0 12 12"
            style={{ position: 'absolute', bottom: 4, right: 4 }}
          >
            <path d="M2 10L10 2M6 10L10 6M10 10L10 10" stroke="rgba(255,255,255,0.2)" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </div>
      )}
    </motion.div>
  );
}
