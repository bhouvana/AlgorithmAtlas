/**
 * InterviewOverlay — shows inside the Atlas panel when interview mode is active.
 * Displays: problem, countdown timer, progressive hints, end button.
 */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Clock, ChevronDown, ChevronUp, XCircle, Lightbulb } from 'lucide-react';
import { useAtlasStore } from '../store';

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export function InterviewOverlay() {
  const { interview, revealNextHint, endInterview } = useAtlasStore();
  const { problem, startedAt, hintsRevealed } = interview;

  const [elapsed, setElapsed] = useState(0);
  const [showProblem, setShowProblem] = useState(true);

  const totalSeconds = (problem?.time_limit_minutes ?? 35) * 60;

  useEffect(() => {
    if (!startedAt) return;
    const tick = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startedAt) / 1000));
    }, 1000);
    return () => clearInterval(tick);
  }, [startedAt]);

  if (!problem) return null;

  const remaining = Math.max(0, totalSeconds - elapsed);
  const pct = (remaining / totalSeconds) * 100;
  const isUrgent = remaining < 300; // last 5 min

  const diffColors: Record<string, string> = {
    easy:   'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
    medium: 'text-amber-400 border-amber-500/30 bg-amber-500/10',
    hard:   'text-rose-400 border-rose-500/30 bg-rose-500/10',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      className="mx-3 mb-2 rounded-xl border border-white/10 bg-[#0c0c18] overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-white/8">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-white">Interview</span>
          <span className={`text-[10px] px-1.5 py-0.5 rounded border font-medium ${diffColors[problem.difficulty] ?? ''}`}>
            {problem.difficulty}
          </span>
        </div>
        <div className="flex items-center gap-2">
          {/* Timer */}
          <div className={`flex items-center gap-1 font-mono text-xs ${isUrgent ? 'text-rose-400' : 'text-zinc-400'}`}>
            <Clock className="w-3 h-3" />
            {formatTime(remaining)}
          </div>
          <button
            onClick={endInterview}
            className="text-zinc-600 hover:text-zinc-400 transition-colors"
            title="End interview"
          >
            <XCircle className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Timer bar */}
      <div className="h-0.5 bg-zinc-800">
        <motion.div
          className={`h-full ${isUrgent ? 'bg-rose-500' : 'bg-indigo-500'}`}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 1, ease: 'linear' }}
        />
      </div>

      {/* Problem */}
      <div className="px-3 py-2">
        <button
          onClick={() => setShowProblem((v) => !v)}
          className="flex items-center gap-1.5 text-xs font-medium text-zinc-300 hover:text-white transition-colors w-full text-left"
        >
          {showProblem ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          {problem.title}
        </button>

        {showProblem && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-2 space-y-2"
          >
            <p className="text-xs text-zinc-400 leading-relaxed">{problem.description}</p>

            {problem.examples.slice(0, 1).map((ex, i) => (
              <div key={i} className="rounded-lg bg-black/30 border border-white/6 p-2 text-xs font-mono">
                <div className="text-zinc-500 mb-0.5">Example:</div>
                <div className="text-zinc-300">In: {ex.input}</div>
                <div className="text-emerald-400">Out: {ex.output}</div>
              </div>
            ))}
          </motion.div>
        )}
      </div>

      {/* Hints */}
      <div className="px-3 pb-2 space-y-1.5">
        {problem.hints.slice(0, hintsRevealed).map((hint, i) => (
          <div key={i} className="flex items-start gap-2 text-xs text-zinc-400">
            <Lightbulb className="w-3 h-3 text-amber-400 mt-0.5 flex-shrink-0" />
            <span>{hint}</span>
          </div>
        ))}
        {hintsRevealed < problem.hints.length && (
          <button
            onClick={revealNextHint}
            className="flex items-center gap-1.5 text-[11px] text-amber-500 hover:text-amber-300 transition-colors mt-1"
          >
            <Lightbulb className="w-3 h-3" />
            Reveal hint {hintsRevealed + 1}/{problem.hints.length}
          </button>
        )}
      </div>
    </motion.div>
  );
}
