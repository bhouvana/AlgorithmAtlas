import { useCallback, useRef } from 'react';

/**
 * Drag-to-resize for a single divider. `onDelta` receives the pixel delta
 * along `axis` since the previous pointer-move event (not since drag start)
 * so callers can just add it to their current size each tick.
 */
export function useResizeDrag(onDelta: (deltaPx: number) => void, axis: 'x' | 'y' = 'x') {
  const lastRef = useRef(0);

  const onPointerDown = useCallback(
    (e: React.PointerEvent<HTMLElement>) => {
      e.preventDefault();
      lastRef.current = axis === 'x' ? e.clientX : e.clientY;

      const handleMove = (ev: PointerEvent) => {
        const current = axis === 'x' ? ev.clientX : ev.clientY;
        const delta = current - lastRef.current;
        lastRef.current = current;
        if (delta !== 0) onDelta(delta);
      };
      const handleUp = () => {
        window.removeEventListener('pointermove', handleMove);
        window.removeEventListener('pointerup', handleUp);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      };
      window.addEventListener('pointermove', handleMove);
      window.addEventListener('pointerup', handleUp);
      document.body.style.cursor = axis === 'x' ? 'col-resize' : 'row-resize';
      document.body.style.userSelect = 'none';
    },
    [onDelta, axis]
  );

  return onPointerDown;
}
