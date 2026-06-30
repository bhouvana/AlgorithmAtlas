import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAtlasStore } from '../store';

export function AtlasOrb() {
  const { toggle, hasNewSuggestion, proactiveHint, isOpen } = useAtlasStore();
  const btnRef    = useRef<HTMLButtonElement>(null);
  const magnetRef = useRef({ x: 0, y: 0 });
  const [magnet, setMagnet] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (!btnRef.current) return;
      const r  = btnRef.current.getBoundingClientRect();
      const cx = r.left + r.width / 2;
      const cy = r.top  + r.height / 2;
      const dx = e.clientX - cx;
      const dy = e.clientY - cy;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const radius = 110;
      if (dist < radius) {
        const t = (1 - dist / radius) * 0.13;
        const nx = dx * t;
        const ny = dy * t;
        if (Math.abs(nx - magnetRef.current.x) > 0.3 || Math.abs(ny - magnetRef.current.y) > 0.3) {
          magnetRef.current = { x: nx, y: ny };
          setMagnet({ x: nx, y: ny });
        }
      } else if (magnetRef.current.x !== 0 || magnetRef.current.y !== 0) {
        magnetRef.current = { x: 0, y: 0 };
        setMagnet({ x: 0, y: 0 });
      }
    };
    window.addEventListener('mousemove', onMove, { passive: true });
    return () => window.removeEventListener('mousemove', onMove);
  }, []);

  if (isOpen) return null;

  return (
    <div className="fixed bottom-6 right-6 z-[200] flex flex-col items-end gap-2.5">
      {/* Proactive hint */}
      <AnimatePresence>
        {proactiveHint && (
          <motion.div
            initial={{ opacity: 0, x: 10, scale: 0.95 }}
            animate={{ opacity: 1, x: 0,  scale: 1    }}
            exit={{   opacity: 0, x: 10,  scale: 0.95 }}
            transition={{ type: 'spring', stiffness: 400, damping: 32 }}
            className="max-w-[200px] px-3 py-2 rounded-2xl text-xs text-zinc-300 leading-snug pointer-events-none"
            style={{
              background: 'rgba(15,15,26,0.9)',
              border: '1px solid rgba(255,255,255,0.08)',
              backdropFilter: 'blur(16px)',
              boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
            }}
          >
            {proactiveHint}
          </motion.div>
        )}
      </AnimatePresence>

      {/* The orb */}
      <motion.button
        ref={btnRef}
        layoutId="atlas-shell"
        onClick={() => toggle()}
        animate={{ x: magnet.x, y: magnet.y }}
        transition={{ type: 'spring', stiffness: 280, damping: 28 }}
        whileTap={{ scale: 0.9 }}
        className="relative w-[52px] h-[52px] rounded-full focus:outline-none select-none"
        aria-label="Open Atlas AI"
        style={{ borderRadius: '50%' }}
      >
        {/* Outer breathing glow */}
        <motion.div
          className="absolute inset-0 rounded-full pointer-events-none"
          animate={{
            opacity: hasNewSuggestion ? [0.45, 0.85, 0.45] : [0.18, 0.38, 0.18],
            scale:   hasNewSuggestion ? [1, 1.5, 1] : [1, 1.25, 1],
          }}
          transition={{
            duration: hasNewSuggestion ? 1.8 : 3.6,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          style={{
            background: 'radial-gradient(circle, rgba(99,102,241,1), transparent 70%)',
            filter: 'blur(12px)',
          }}
        />

        {/* Glass surface */}
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background: 'linear-gradient(145deg, rgba(118,120,255,0.95) 0%, rgba(79,70,229,0.92) 55%, rgba(109,40,217,0.88) 100%)',
            boxShadow: hasNewSuggestion
              ? '0 0 0 1.5px rgba(139,92,246,0.6), 0 12px 40px rgba(99,102,241,0.55), inset 0 1px 0 rgba(255,255,255,0.25)'
              : '0 0 0 1px rgba(99,102,241,0.35), 0 8px 28px rgba(99,102,241,0.32), inset 0 1px 0 rgba(255,255,255,0.18)',
          }}
        />

        {/* Glass specular highlight */}
        <div
          className="absolute inset-0 rounded-full pointer-events-none"
          style={{
            background: 'radial-gradient(ellipse at 38% 32%, rgba(255,255,255,0.38), transparent 62%)',
          }}
        />

        {/* Sparkle icon */}
        <div className="absolute inset-0 flex items-center justify-center">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path d="M12 2.5L13.09 9.26L19.5 12L13.09 14.74L12 21.5L10.91 14.74L4.5 12L10.91 9.26L12 2.5Z"
              fill="white" fillOpacity="0.96" />
            <circle cx="19" cy="5" r="1.5" fill="white" fillOpacity="0.6" />
            <circle cx="5"  cy="19" r="1"   fill="white" fillOpacity="0.4" />
          </svg>
        </div>

        {/* Suggestion dot */}
        <AnimatePresence>
          {hasNewSuggestion && (
            <motion.div
              key="dot"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 500, damping: 22 }}
              className="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 rounded-full border-2 border-[#09090B]"
              style={{
                background: 'radial-gradient(circle, #c084fc, #7c3aed)',
                boxShadow: '0 0 8px rgba(167,139,250,0.9)',
              }}
            />
          )}
        </AnimatePresence>
      </motion.button>
    </div>
  );
}
