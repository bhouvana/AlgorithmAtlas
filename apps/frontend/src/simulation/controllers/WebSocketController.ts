/**
 * WebSocketController — SimulationController backed by the FastAPI WebSocket endpoint.
 *
 * Message flow:
 *   connect()      → opens WS, receives initial frame + status
 *   play()         → sends {type: "play", speed}; server streams frames
 *   pause()        → sends {type: "pause"}; server stops streaming
 *   stepForward()  → sends {type: "step_forward"}; awaits one frame response
 *   stepBackward() → sends {type: "step_backward"}; awaits one frame response
 *   seek()         → sends {type: "seek", frame_index}; awaits one frame response
 *   reset()        → sends {type: "reset"}; awaits frame + status
 *   destroy()      → closes the WebSocket
 */

import type { SimulationController, SimulationFrame, SimulationStatus } from './SimulationController';

type InflightResolver = {
  resolve: (frame: SimulationFrame) => void;
  reject: (reason: Error) => void;
};

export class WebSocketController implements SimulationController {
  readonly sessionId: string;

  status: SimulationStatus = 'created';
  currentFrameIndex = 0;
  totalFrames: number | null = null;
  playbackSpeed = 1.0;

  onFrame: ((frame: SimulationFrame) => void) | null = null;
  onStatus: ((status: SimulationStatus, meta?: Record<string, unknown>) => void) | null = null;
  onError: ((code: string, message: string) => void) | null = null;

  private ws: WebSocket | null = null;
  private readonly wsUrl: string;

  /** True once the initial connection frame has been delivered via connect(). */
  private _initialFrameDelivered = false;

  /** Pending promise resolver for command-response round trips (step, seek, reset). */
  private inflight: InflightResolver | null = null;

  constructor(sessionId: string, wsUrl: string) {
    this.sessionId = sessionId;
    this.wsUrl = wsUrl;
  }

  // ── Lifecycle ─────────────────────────────────────────────────────────────

  connect(): Promise<SimulationFrame> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl);

      this.ws.onopen = () => {
        // Server sends the initial frame immediately on connection.
        // We'll resolve once we receive it.
      };

      this.ws.onmessage = (event: MessageEvent) => {
        try {
          const msg = JSON.parse(event.data as string) as Record<string, unknown>;
          this._handleMessage(msg, resolve, reject);
        } catch (e) {
          reject(new Error(`Failed to parse WebSocket message: ${e}`));
        }
      };

      this.ws.onerror = () => {
        reject(new Error(`WebSocket connection to ${this.wsUrl} failed`));
      };

      this.ws.onclose = (event) => {
        // If we haven't received the initial frame yet, the connection failed.
        if (!this._initialFrameDelivered) {
          reject(new Error(`WebSocket closed before initial frame (code=${event.code})`));
          return;
        }
        if (this.status === 'running' || this.status === 'paused') {
          this.onError?.('WS_CLOSED', `Connection closed: code=${event.code}`);
        }
      };
    });
  }

  destroy(): void {
    this.ws?.close(1000, 'Client destroyed');
    this.ws = null;
    this.inflight = null;
  }

  // ── Playback control ──────────────────────────────────────────────────────

  play(speed = this.playbackSpeed): void {
    this.playbackSpeed = speed;
    this._send({ type: 'play', speed });
    this._setStatus('running');
  }

  pause(): void {
    this._send({ type: 'pause' });
    this._setStatus('paused');
  }

  setSpeed(speed: number): void {
    this.playbackSpeed = speed;
    this._send({ type: 'set_speed', speed });
  }

  // ── Frame navigation ──────────────────────────────────────────────────────

  stepForward(): Promise<SimulationFrame> {
    return this._commandWithFrameResponse({ type: 'step_forward' });
  }

  stepBackward(): Promise<SimulationFrame> {
    return this._commandWithFrameResponse({ type: 'step_backward' });
  }

  seek(frameIndex: number): Promise<SimulationFrame> {
    return this._commandWithFrameResponse({ type: 'seek', frame_index: frameIndex });
  }

  reset(): Promise<SimulationFrame> {
    return this._commandWithFrameResponse({ type: 'reset' });
  }

  // ── Internal ──────────────────────────────────────────────────────────────

  private _handleMessage(
    msg: Record<string, unknown>,
    initialResolve?: (frame: SimulationFrame) => void,
    initialReject?: (reason: Error) => void,
  ): void {
    const type = msg['type'] as string;

    switch (type) {
      case 'frame': {
        const frame = msg['data'] as SimulationFrame;
        this.currentFrameIndex = frame.frame_index;

        // First frame ever: resolve the connect() promise and mark as delivered.
        if (initialResolve && !this._initialFrameDelivered) {
          this._initialFrameDelivered = true;
          initialResolve(frame);
          return;
        }

        // Frame responding to a step/seek/reset command.
        if (this.inflight) {
          this.inflight.resolve(frame);
          this.inflight = null;
          return;
        }

        // Streaming frame during play — push to React.
        this.onFrame?.(frame);
        break;
      }

      case 'status': {
        const newStatus = msg['status'] as SimulationStatus;
        const totalFrames = msg['total_frames'] as number | undefined;
        const currentFrame = msg['current_frame'] as number | undefined;

        this._setStatus(newStatus);
        if (totalFrames !== undefined) this.totalFrames = totalFrames;
        if (currentFrame !== undefined) this.currentFrameIndex = currentFrame;

        this.onStatus?.(newStatus, {
          total_frames: totalFrames,
          current_frame: currentFrame,
        });
        break;
      }

      case 'error': {
        const code = msg['code'] as string;
        const message = msg['message'] as string;

        if (this.inflight) {
          this.inflight.reject(new Error(`[${code}] ${message}`));
          this.inflight = null;
          return;
        }

        if (initialReject) {
          initialReject(new Error(`[${code}] ${message}`));
          return;
        }

        this.onError?.(code, message);
        break;
      }

      case 'pong':
        break;

      default:
        console.warn(`[WebSocketController] Unknown message type: ${type}`, msg);
    }
  }

  private _commandWithFrameResponse(
    msg: Record<string, unknown>,
  ): Promise<SimulationFrame> {
    return new Promise((resolve, reject) => {
      if (this.inflight) {
        reject(new Error('Another command is already in flight'));
        return;
      }
      this.inflight = { resolve, reject };
      this._send(msg);
    });
  }

  private _send(msg: Record<string, unknown>): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(msg));
    } else {
      console.error('[WebSocketController] Cannot send — WebSocket not open', msg);
    }
  }

  private _setStatus(status: SimulationStatus): void {
    this.status = status;
  }
}
