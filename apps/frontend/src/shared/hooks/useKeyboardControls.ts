/**
 * useKeyboardControls — wires keyboard shortcuts to the active simulation.
 *
 * Shortcuts (ignored when focus is inside an input / textarea / select):
 *   Space      → play / pause
 *   ArrowRight → step forward
 *   ArrowLeft  → step backward
 *   r / R      → reset to frame 0
 *   = / +      → speed up (cycle through SPEED_OPTIONS)
 *   -          → slow down
 */

import { useEffect } from 'react';
import { useSimulationStore } from '../../core/store/simulationStore';

const SPEED_OPTIONS = [0.25, 0.5, 1, 2, 4, 8];

function nearestSpeedIndex(speed: number): number {
  let best = 0;
  let bestDiff = Math.abs(SPEED_OPTIONS[0] - speed);
  for (let i = 1; i < SPEED_OPTIONS.length; i++) {
    const diff = Math.abs(SPEED_OPTIONS[i] - speed);
    if (diff < bestDiff) { bestDiff = diff; best = i; }
  }
  return best;
}

function isEditingInput(event: KeyboardEvent): boolean {
  const target = event.target as HTMLElement | null;
  return !!target?.closest('input, textarea, select, [contenteditable="true"]');
}

export function useKeyboardControls(): void {
  const {
    controller,
    status,
    playbackSpeed,
    setFrame,
    setStatus,
    setTotalFrames,
    setPlaybackSpeed,
  } = useSimulationStore();

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent): void {
      if (isEditingInput(e) || !controller) return;

      switch (e.key) {
        case ' ':
          e.preventDefault();
          if (status === 'running') {
            controller.pause();
            setStatus('paused');
          } else if (status !== 'completed') {
            controller.play(playbackSpeed);
            setStatus('running');
          }
          break;

        case 'ArrowRight':
          e.preventDefault();
          controller.stepForward()
            .then((frame) => setFrame(frame))
            .catch(() => { /* at last frame */ });
          break;

        case 'ArrowLeft':
          e.preventDefault();
          controller.stepBackward()
            .then((frame) => setFrame(frame))
            .catch(() => { /* at first frame */ });
          break;

        case 'r':
        case 'R':
          e.preventDefault();
          controller.reset().then((frame) => {
            setFrame(frame);
            setStatus('paused');
            setTotalFrames(null);
          });
          break;

        case '=':
        case '+': {
          e.preventDefault();
          const idx = nearestSpeedIndex(playbackSpeed);
          if (idx < SPEED_OPTIONS.length - 1) {
            const next = SPEED_OPTIONS[idx + 1];
            setPlaybackSpeed(next);
            controller.setSpeed(next);
          }
          break;
        }

        case '-': {
          e.preventDefault();
          const idx = nearestSpeedIndex(playbackSpeed);
          if (idx > 0) {
            const next = SPEED_OPTIONS[idx - 1];
            setPlaybackSpeed(next);
            controller.setSpeed(next);
          }
          break;
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [controller, status, playbackSpeed, setFrame, setStatus, setTotalFrames, setPlaybackSpeed]);
}
