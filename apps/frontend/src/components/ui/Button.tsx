import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';
import type { ReactNode } from 'react';

type Variant = 'primary' | 'secondary' | 'ghost';
type Size = 'sm' | 'md' | 'lg';

interface ButtonProps {
  children: ReactNode;
  variant?: Variant;
  size?: Size;
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
  icon?: ReactNode;
  as?: 'button' | 'a';
  href?: string;
}

const variants: Record<Variant, string> = {
  primary:
    'bg-indigo-600 hover:bg-indigo-500 text-white shadow-glow-sm hover:shadow-glow border border-indigo-500/50',
  secondary:
    'bg-white/5 hover:bg-white/10 text-white border border-white/10 hover:border-white/20',
  ghost:
    'bg-transparent hover:bg-white/5 text-zinc-400 hover:text-white border border-transparent',
};

const sizes: Record<Size, string> = {
  sm: 'h-8 px-3 text-xs gap-1.5',
  md: 'h-9 px-4 text-sm gap-2',
  lg: 'h-11 px-6 text-base gap-2.5',
};

export function Button({
  children,
  variant = 'secondary',
  size = 'md',
  onClick,
  className,
  disabled,
  icon,
}: ButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.97 }}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'inline-flex items-center justify-center rounded-xl font-medium transition-all duration-200 cursor-pointer select-none',
        'focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 focus-visible:ring-offset-[#09090B]',
        'disabled:opacity-40 disabled:cursor-not-allowed disabled:pointer-events-none',
        variants[variant],
        sizes[size],
        className,
      )}
    >
      {icon && <span className="flex-shrink-0">{icon}</span>}
      {children}
    </motion.button>
  );
}
