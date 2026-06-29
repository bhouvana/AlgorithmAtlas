/**
 * SimulationController — abstract interface for all simulation backends.
 *
 * Two implementations will exist:
 *   WebSocketController  — streams frames from the server (all algorithms in Phase 0)
 *   WasmController       — runs WASM-compiled algorithms in a Web Worker (Phase 1+)
 *
 * All simulation UI components depend ONLY on this interface.
 * Switching a plugin from server-side to WASM requires zero UI changes.
 */

export interface SimulationFrame {
  frame_index: number;
  state: Record<string, unknown>;
  timestamp_ms: number;
  event_label: string | null;
}

export type SimulationStatus =
  | 'created'
  | 'paused'
  | 'running'
  | 'completed'
  | 'error';

export interface SimulationController {
  readonly sessionId: string;
  readonly status: SimulationStatus;
  readonly currentFrameIndex: number;
  readonly totalFrames: number | null;
  readonly playbackSpeed: number;

  /** Connect and return the initial frame. Must be called before all else. */
  connect(): Promise<SimulationFrame>;

  play(speed?: number): void;
  pause(): void;
  stepForward(): Promise<SimulationFrame>;
  stepBackward(): Promise<SimulationFrame>;
  seek(frameIndex: number): Promise<SimulationFrame>;
  reset(): Promise<SimulationFrame>;
  setSpeed(speed: number): void;

  /** Tear down resources (WebSocket, Web Worker, etc.) */
  destroy(): void;

  /** Event handlers — set before calling connect() */
  onFrame: ((frame: SimulationFrame) => void) | null;
  onStatus: ((status: SimulationStatus, meta?: Record<string, unknown>) => void) | null;
  onError: ((code: string, message: string) => void) | null;
}
