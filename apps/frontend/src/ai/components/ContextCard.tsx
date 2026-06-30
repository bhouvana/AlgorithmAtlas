import type { AtlasContext } from '../types';

interface Props {
  context: AtlasContext;
}

export function ContextCard({ context }: Props) {
  const parts: string[] = [];

  if (context.algorithm?.name) {
    parts.push(`⬡ ${context.algorithm.name}`);
  }

  if (context.simulation) {
    const { status, currentFrameIndex, totalFrames } = context.simulation;
    const total = totalFrames ? `/${totalFrames}` : '';
    parts.push(`Frame ${currentFrameIndex}${total} · ${status}`);
  }

  if (context.notebook) {
    parts.push(`🖊 ${context.notebook.language}`);
    if (context.notebook.lastError) {
      const errLine = context.notebook.lastError.split('\n')[0].slice(0, 40);
      parts.push(`⚠ ${errLine}`);
    }
  }

  if (context.lesson) {
    parts.push(`📖 ${context.lesson.title}`);
    parts.push(context.lesson.activeSection);
  }

  if (context.comparison) {
    const a = context.comparison.algorithmA ?? '—';
    const b = context.comparison.algorithmB ?? '—';
    parts.push(`⇄ ${a} vs ${b}`);
  }

  if (parts.length === 0) return null;

  return (
    <div className="px-4 py-2 border-b border-white/6 bg-white/[0.02]">
      <p className="text-[10px] text-zinc-500 font-mono leading-relaxed truncate">
        {parts.join('  ·  ')}
      </p>
    </div>
  );
}
