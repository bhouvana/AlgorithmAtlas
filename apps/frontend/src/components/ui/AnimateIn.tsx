import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';
import type { ReactNode } from 'react';
import { cn } from '../../lib/utils';

interface AnimateInProps {
  children: ReactNode;
  delay?: number;
  direction?: 'up' | 'down' | 'left' | 'right' | 'fade';
  className?: string;
  once?: boolean;
}

const directionMap = {
  up:    { y: 14, x: 0 },
  down:  { y: -14, x: 0 },
  left:  { y: 0, x: 14 },
  right: { y: 0, x: -14 },
  fade:  { y: 0, x: 0 },
};

// Snappy spring easing — fast out, no bounce
const EASE = [0.22, 1, 0.36, 1] as const;

export function AnimateIn({
  children,
  delay = 0,
  direction = 'up',
  className,
  once = true,
}: AnimateInProps) {
  const ref = useRef(null);
  const inView = useInView(ref, { once, margin: '-20px' });
  const { x, y } = directionMap[direction];

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, x, y }}
      animate={inView ? { opacity: 1, x: 0, y: 0 } : { opacity: 0, x, y }}
      transition={{ duration: 0.32, delay, ease: EASE }}
      className={cn(className)}
    >
      {children}
    </motion.div>
  );
}
