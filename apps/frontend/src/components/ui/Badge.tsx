import type { ReactNode } from 'react';
import { cn } from '../../lib/utils';

type Variant = 'indigo' | 'blue' | 'purple' | 'cyan' | 'green' | 'amber' | 'red' | 'zinc';

interface BadgeProps {
  children: ReactNode;
  variant?: Variant;
  className?: string;
}

const variants: Record<Variant, string> = {
  indigo: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30',
  blue: 'bg-blue-500/15 text-blue-300 border-blue-500/30',
  purple: 'bg-purple-500/15 text-purple-300 border-purple-500/30',
  cyan: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
  green: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  amber: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  red: 'bg-red-500/15 text-red-300 border-red-500/30',
  zinc: 'bg-zinc-500/15 text-zinc-300 border-zinc-500/30',
};

export function Badge({ children, variant = 'zinc', className }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border',
        variants[variant],
        className,
      )}
    >
      {children}
    </span>
  );
}
