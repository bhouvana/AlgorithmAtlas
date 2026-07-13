import { motion } from 'framer-motion';
import { Cpu, BookOpen, Terminal, GitCompare, Layers, GraduationCap } from 'lucide-react';
import type { AtlasContext } from '../types';

interface Props { context: AtlasContext }

interface Card {
  icon: React.ReactNode;
  label: string;
  value: string;
  sub?: string;
  accent: string;
}

function buildCards(ctx: AtlasContext): Card[] {
  const cards: Card[] = [];

  if (ctx.algorithm) {
    cards.push({
      icon: <Cpu className="w-3 h-3" />,
      label: 'Algorithm',
      value: ctx.algorithm.name,
      sub: ctx.algorithm.category || undefined,
      accent: '#6366f1',
    });
  }

  if (ctx.simulation) {
    const { currentFrameIndex, totalFrames, status } = ctx.simulation;
    cards.push({
      icon: <Layers className="w-3 h-3" />,
      label: 'Visualization',
      value: status === 'running' ? 'Running' : status === 'paused' ? 'Paused' : 'Ready',
      sub: totalFrames ? `Frame ${currentFrameIndex + 1} / ${totalFrames}` : undefined,
      accent: status === 'running' ? '#10b981' : '#f59e0b',
    });
  }

  if (ctx.notebook) {
    cards.push({
      icon: <Terminal className="w-3 h-3" />,
      label: 'Compiler',
      value: ctx.notebook.language.charAt(0).toUpperCase() + ctx.notebook.language.slice(1),
      sub: ctx.notebook.lastError ? 'Has errors' : ctx.notebook.lastOutput ? 'Last run: OK' : undefined,
      accent: ctx.notebook.lastError ? '#ef4444' : '#6366f1',
    });
  }

  if (ctx.lesson) {
    cards.push({
      icon: <BookOpen className="w-3 h-3" />,
      label: 'Lesson',
      value: ctx.lesson.title,
      sub: ctx.lesson.difficulty,
      accent: '#8b5cf6',
    });
  }

  if (ctx.comparison) {
    cards.push({
      icon: <GitCompare className="w-3 h-3" />,
      label: 'Comparing',
      value: [ctx.comparison.algorithmA, ctx.comparison.algorithmB].filter(Boolean).join(' vs ') || 'Two algorithms',
      accent: '#0ea5e9',
    });
  }

  if (ctx.learningProgress) {
    cards.push({
      icon: <GraduationCap className="w-3 h-3" />,
      label: 'Progress',
      value: `Level ${ctx.learningProgress.level}`,
      sub: `${ctx.learningProgress.xp} XP · ${ctx.learningProgress.completedLessons.length} lessons done`,
      accent: '#f59e0b',
    });
  }

  return cards;
}

export function ContextCards({ context }: Props) {
  const cards = buildCards(context);
  if (cards.length === 0) return null;

  return (
    <div className="px-3 pb-2">
      <p className="text-[9px] font-semibold uppercase tracking-widest text-zinc-600 mb-2 px-1">
        Current context
      </p>
      <div className="flex flex-col gap-1.5">
        {cards.map((card, i) => (
          <motion.div
            key={card.label}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="flex items-center gap-2.5 px-3 py-2 rounded-xl"
            style={{
              background: 'rgba(255,255,255,0.025)',
              border: '1px solid rgba(255,255,255,0.055)',
            }}
          >
            <div
              className="w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ background: `${card.accent}18`, color: card.accent }}
            >
              {card.icon}
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-zinc-600 uppercase tracking-wider">{card.label}</span>
              </div>
              <p className="text-[12px] font-medium text-zinc-200 truncate leading-tight">{card.value}</p>
              {card.sub && (
                <p className="text-[10px] text-zinc-600 truncate">{card.sub}</p>
              )}
            </div>
            <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: card.accent, opacity: 0.7 }} />
          </motion.div>
        ))}
      </div>
    </div>
  );
}
