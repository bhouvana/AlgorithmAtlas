/**
 * Simulation store — global state for the active simulation session.
 *
 * The store holds the current frame, playback status, and a reference
 * to the active controller. Components read from the store; the controller
 * writes to it via event handlers.
 */

import { create } from 'zustand';
import type { SimulationFrame, SimulationStatus } from '../../simulation/controllers/SimulationController';
import type { SimulationController } from '../../simulation/controllers/SimulationController';

interface SimulationState {
  // Active controller (null when no simulation is running)
  controller: SimulationController | null;

  // Current frame data
  currentFrame: SimulationFrame | null;
  currentFrameIndex: number;
  totalFrames: number | null;

  // Playback
  status: SimulationStatus;
  playbackSpeed: number;

  // Algorithm context
  algorithmSlug: string | null;
  sessionId: string | null;

  // Actions
  setController: (controller: SimulationController | null) => void;
  setFrame: (frame: SimulationFrame) => void;
  setStatus: (status: SimulationStatus) => void;
  setTotalFrames: (total: number | null) => void;
  setPlaybackSpeed: (speed: number) => void;
  setAlgorithmSlug: (slug: string | null) => void;
  setSessionId: (id: string | null) => void;
  reset: () => void;
}

export const useSimulationStore = create<SimulationState>((set) => ({
  controller: null,
  currentFrame: null,
  currentFrameIndex: 0,
  totalFrames: null,
  status: 'created',
  playbackSpeed: 1.0,
  algorithmSlug: null,
  sessionId: null,

  setController: (controller) => set({ controller }),
  setFrame: (frame) => set({
    currentFrame: frame,
    currentFrameIndex: frame.frame_index,
  }),
  setStatus: (status) => set({ status }),
  setTotalFrames: (totalFrames) => set({ totalFrames }),
  setPlaybackSpeed: (playbackSpeed) => set({ playbackSpeed }),
  setAlgorithmSlug: (algorithmSlug) => set({ algorithmSlug }),
  setSessionId: (sessionId) => set({ sessionId }),
  reset: () => set({
    controller: null,
    currentFrame: null,
    currentFrameIndex: 0,
    totalFrames: null,
    status: 'created',
    algorithmSlug: null,
    sessionId: null,
  }),
}));
