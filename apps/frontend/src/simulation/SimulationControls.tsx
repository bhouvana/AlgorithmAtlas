/**
 * SimulationControls — playback UI: play, pause, step, rewind, speed, scrubber.
 *
 * This component is pure UI. It reads from the simulation store and dispatches
 * to the active controller. It knows nothing about algorithms or frame content.
 */

import React, { useCallback } from 'react';
import { useSimulationStore } from '../core/store/simulationStore';

const SPEED_OPTIONS = [0.25, 0.5, 1, 2, 4, 8] as const;

interface IconButtonProps {
  onClick: () => void;
  disabled?: boolean;
  title: string;
  children: React.ReactNode;
}

function IconButton({ onClick, disabled, title, children }: IconButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={[
        'flex items-center justify-center w-9 h-9 rounded-lg transition-colors',
        'text-neutral-300 hover:text-white hover:bg-white/10',
        'disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent',
        'focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500',
      ].join(' ')}
    >
      {children}
    </button>
  );
}

export function SimulationControls() {
  const {
    controller,
    status,
    currentFrameIndex,
    totalFrames,
    playbackSpeed,
    setFrame,
    setStatus,
    setPlaybackSpeed,
    setTotalFrames,
  } = useSimulationStore();

  const isRunning = status === 'running';
  const isCompleted = status === 'completed';
  const isAtStart = currentFrameIndex === 0;
  const isAtEnd = totalFrames !== null && currentFrameIndex >= totalFrames - 1;

  const handlePlay = useCallback(() => {
    controller?.play(playbackSpeed);
    setStatus('running');
  }, [controller, playbackSpeed, setStatus]);

  const handlePause = useCallback(() => {
    controller?.pause();
    setStatus('paused');
  }, [controller, setStatus]);

  const handleStepForward = useCallback(async () => {
    if (!controller) return;
    try {
      const frame = await controller.stepForward();
      setFrame(frame);
    } catch {
      // At last frame — ignore
    }
  }, [controller, setFrame]);

  const handleStepBackward = useCallback(async () => {
    if (!controller) return;
    try {
      const frame = await controller.stepBackward();
      setFrame(frame);
    } catch {
      // At first frame — ignore
    }
  }, [controller, setFrame]);

  const handleReset = useCallback(async () => {
    if (!controller) return;
    const frame = await controller.reset();
    setFrame(frame);
    setStatus('paused');
    setTotalFrames(null);
  }, [controller, setFrame, setStatus, setTotalFrames]);

  const handleSeek = useCallback(async (value: string) => {
    const idx = parseInt(value, 10);
    if (!controller || isNaN(idx)) return;
    try {
      const frame = await controller.seek(idx);
      setFrame(frame);
    } catch {
      // Out of bounds
    }
  }, [controller, setFrame]);

  const handleSpeedChange = useCallback((speed: number) => {
    setPlaybackSpeed(speed);
    controller?.setSpeed(speed);
    if (isRunning) {
      controller?.play(speed);
    }
  }, [controller, isRunning, setPlaybackSpeed]);

  const hasController = controller !== null;

  return (
    <div className="flex flex-col gap-3 p-4 bg-neutral-900 rounded-xl border border-charcoal/10">
      {/* Primary controls row */}
      <div className="flex items-center justify-center gap-1">
        {/* Reset to start */}
        <IconButton
          onClick={handleReset}
          disabled={!hasController || isAtStart}
          title="Reset (R)"
        >
          <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
            <path d="M7.707 10L13 4.707A1 1 0 0011.586 3.293l-6 6a1 1 0 000 1.414l6 6A1 1 0 0013 15.293L7.707 10z" />
            <path d="M3 3h1.5v14H3V3z" />
          </svg>
        </IconButton>

        {/* Step backward */}
        <IconButton
          onClick={handleStepBackward}
          disabled={!hasController || isAtStart}
          title="Step backward (←)"
        >
          <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
            <path d="M8.707 10L14 4.707A1 1 0 0012.586 3.293l-6 6a1 1 0 000 1.414l6 6A1 1 0 0014 15.293L8.707 10z" />
          </svg>
        </IconButton>

        {/* Play / Pause */}
        {isRunning ? (
          <IconButton onClick={handlePause} disabled={!hasController} title="Pause (Space)">
            <svg viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
              <path d="M5.75 3a.75.75 0 00-.75.75v12.5c0 .414.336.75.75.75h1.5a.75.75 0 00.75-.75V3.75A.75.75 0 007.25 3h-1.5zM12.75 3a.75.75 0 00-.75.75v12.5c0 .414.336.75.75.75h1.5a.75.75 0 00.75-.75V3.75a.75.75 0 00-.75-.75h-1.5z" />
            </svg>
          </IconButton>
        ) : (
          <button
            onClick={handlePlay}
            disabled={!hasController || isCompleted}
            title="Play (Space)"
            className={[
              'flex items-center justify-center w-11 h-11 rounded-full transition-colors',
              'bg-indigo-600 hover:bg-indigo-500 text-white',
              'disabled:opacity-30 disabled:cursor-not-allowed',
              'focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400',
            ].join(' ')}
          >
            <svg viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5 ml-0.5">
              <path d="M6.3 2.841A1.5 1.5 0 004 4.11v11.78a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
            </svg>
          </button>
        )}

        {/* Step forward */}
        <IconButton
          onClick={handleStepForward}
          disabled={!hasController || isAtEnd}
          title="Step forward (→)"
        >
          <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
            <path d="M11.293 10L6 4.707A1 1 0 017.414 3.293l6 6a1 1 0 010 1.414l-6 6A1 1 0 016 15.293L11.293 10z" />
          </svg>
        </IconButton>

        {/* Skip to end */}
        <IconButton
          onClick={() => totalFrames !== null && handleSeek(String(totalFrames - 1))}
          disabled={!hasController || isAtEnd || totalFrames === null}
          title="Jump to end"
        >
          <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
            <path d="M12.293 10L7 4.707A1 1 0 018.414 3.293l6 6a1 1 0 010 1.414l-6 6A1 1 0 017 15.293L12.293 10z" />
            <path d="M16.5 3H15v14h1.5V3z" />
          </svg>
        </IconButton>
      </div>

      {/* Scrubber */}
      {totalFrames !== null && totalFrames > 1 && (
        <div className="flex items-center gap-3 px-1">
          <span className="text-xs text-neutral-500 font-mono w-8 text-right">
            {currentFrameIndex}
          </span>
          <input
            type="range"
            min={0}
            max={totalFrames - 1}
            value={currentFrameIndex}
            onChange={(e) => handleSeek(e.target.value)}
            className="flex-1 h-1 accent-indigo-500"
            aria-label="Simulation timeline"
          />
          <span className="text-xs text-neutral-500 font-mono w-8">
            {totalFrames - 1}
          </span>
        </div>
      )}

      {/* Speed selector */}
      <div className="flex items-center justify-center gap-1">
        <span className="text-xs text-neutral-500 mr-1">Speed</span>
        {SPEED_OPTIONS.map((speed) => (
          <button
            key={speed}
            onClick={() => handleSpeedChange(speed)}
            className={[
              'px-2 py-0.5 rounded text-xs font-mono transition-colors',
              playbackSpeed === speed
                ? 'bg-indigo-600 text-white'
                : 'text-neutral-400 hover:text-white hover:bg-white/10',
            ].join(' ')}
          >
            {speed}×
          </button>
        ))}
      </div>

      {/* Frame counter */}
      <div className="text-center text-xs text-neutral-600">
        {hasController ? (
          <>
            Frame <span className="text-neutral-400 font-mono">{currentFrameIndex}</span>
            {totalFrames !== null && (
              <> of <span className="text-neutral-400 font-mono">{totalFrames - 1}</span></>
            )}
          </>
        ) : (
          'No active simulation'
        )}
      </div>
    </div>
  );
}
