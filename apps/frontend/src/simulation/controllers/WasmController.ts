/**
 * WasmController — SimulationController backed by the WASM engine.
 *
 * Computes ALL frames upfront in connect() by calling the WASM run_sort function.
 * Frame navigation is then pure array indexing — no network round-trips.
 *
 * The WASM module is loaded lazily on first connect() call and cached for the
 * lifetime of the page.
 *
 * Build the WASM module before using this controller:
 *   cd packages/wasm-engine
 *   wasm-pack build --target web --out-dir ../../apps/frontend/src/wasm-engine
 */

import type { SimulationController, SimulationFrame, SimulationStatus } from './SimulationController';

// ── WASM module types ─────────────────────────────────────────────────────────

interface WasmEngine {
  run_sort(slug: string, seed: number, arraySize: number, inputOrder: string): string;
  benchmark_sort(slug: string, seed: number, arraySize: number, inputOrder: string, trials: number): number;
}

// Module-level cache — loaded once, shared across all WasmController instances.
let wasmCache: WasmEngine | null = null;
let wasmLoadPromise: Promise<WasmEngine> | null = null;

async function loadWasm(): Promise<WasmEngine> {
  if (wasmCache) return wasmCache;
  if (wasmLoadPromise) return wasmLoadPromise;

  wasmLoadPromise = (async () => {
    // Dynamic import resolves to the wasm-pack output.
    // The path alias @wasm-engine is configured in vite.config.ts.
    const mod = await import(/* @vite-ignore */ '@wasm-engine/wasm_engine.js') as {
      default: () => Promise<void>;
      run_sort: WasmEngine['run_sort'];
      benchmark_sort: WasmEngine['benchmark_sort'];
    };
    // init() fetches and compiles the .wasm binary (no-op on repeat calls)
    await mod.default();
    wasmCache = { run_sort: mod.run_sort, benchmark_sort: mod.benchmark_sort };
    return wasmCache;
  })();

  return wasmLoadPromise;
}

// ── WasmController ────────────────────────────────────────────────────────────

export class WasmController implements SimulationController {
  readonly sessionId: string;

  status: SimulationStatus = 'created';
  currentFrameIndex = 0;
  totalFrames: number | null = null;
  playbackSpeed = 1.0;

  onFrame: ((frame: SimulationFrame) => void) | null = null;
  onStatus: ((status: SimulationStatus, meta?: Record<string, unknown>) => void) | null = null;
  onError: ((code: string, message: string) => void) | null = null;

  private frames: SimulationFrame[] = [];
  private playTimer: ReturnType<typeof setInterval> | null = null;

  private readonly slug: string;
  private readonly seed: number;
  private readonly arraySize: number;
  private readonly inputOrder: string;

  constructor(
    slug: string,
    params: Record<string, unknown>,
    seed = 42,
  ) {
    this.slug = slug;
    this.seed = seed;
    this.arraySize = typeof params['array_size'] === 'number' ? params['array_size'] : 20;
    this.inputOrder = typeof params['input_order'] === 'string' ? params['input_order'] : 'random';
    // Stable session ID based on slug + seed (no server involved)
    this.sessionId = `wasm:${slug}:${seed}`;
  }

  // ── Lifecycle ──────────────────────────────────────────────────────────────

  async connect(): Promise<SimulationFrame> {
    try {
      const wasm = await loadWasm();
      const json = wasm.run_sort(this.slug, this.seed, this.arraySize, this.inputOrder);
      this.frames = JSON.parse(json) as SimulationFrame[];

      if (this.frames.length === 0) {
        throw new Error(`WASM returned no frames for "${this.slug}"`);
      }

      this.totalFrames = this.frames.length;
      this.currentFrameIndex = 0;
      this.status = 'paused';

      this.onStatus?.('paused', { total_frames: this.totalFrames, current_frame: 0 });

      return this.frames[0];
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      this.onError?.('WASM_ERROR', msg);
      throw err;
    }
  }

  destroy(): void {
    this._stopTimer();
  }

  // ── Playback ───────────────────────────────────────────────────────────────

  play(speed = this.playbackSpeed): void {
    this._stopTimer();
    this.playbackSpeed = speed;
    this.status = 'running';

    // Base speed 1× = 500ms/frame; higher speed = shorter interval
    const msPerFrame = Math.max(16, 500 / speed);

    this.playTimer = setInterval(() => {
      if (this.currentFrameIndex >= this.frames.length - 1) {
        this._stopTimer();
        this.status = 'completed';
        this.onStatus?.('completed', { total_frames: this.frames.length });
        return;
      }
      this.currentFrameIndex++;
      this.onFrame?.(this.frames[this.currentFrameIndex]);
    }, msPerFrame);
  }

  pause(): void {
    this._stopTimer();
    this.status = 'paused';
  }

  setSpeed(speed: number): void {
    this.playbackSpeed = speed;
    if (this.status === 'running') {
      this.play(speed);
    }
  }

  // ── Frame navigation ───────────────────────────────────────────────────────

  async stepForward(): Promise<SimulationFrame> {
    if (this.currentFrameIndex >= this.frames.length - 1) {
      throw new Error('Already at last frame');
    }
    this.currentFrameIndex++;
    return this.frames[this.currentFrameIndex];
  }

  async stepBackward(): Promise<SimulationFrame> {
    if (this.currentFrameIndex <= 0) {
      throw new Error('Already at first frame');
    }
    this.currentFrameIndex--;
    return this.frames[this.currentFrameIndex];
  }

  async seek(frameIndex: number): Promise<SimulationFrame> {
    const clamped = Math.max(0, Math.min(frameIndex, this.frames.length - 1));
    this.currentFrameIndex = clamped;
    return this.frames[clamped];
  }

  async reset(): Promise<SimulationFrame> {
    this._stopTimer();
    this.currentFrameIndex = 0;
    this.status = 'paused';
    return this.frames[0];
  }

  // ── WASM benchmark ─────────────────────────────────────────────────────────

  /** Run a client-side benchmark across multiple input sizes. */
  async benchmarkSizes(sizes: number[], trials = 3): Promise<{ input_size: number; wasm_ms: number }[]> {
    const wasm = await loadWasm();
    return sizes.map((size) => ({
      input_size: size,
      wasm_ms: wasm.benchmark_sort(this.slug, this.seed, size, this.inputOrder, trials),
    }));
  }

  // ── Private ────────────────────────────────────────────────────────────────

  private _stopTimer(): void {
    if (this.playTimer !== null) {
      clearInterval(this.playTimer);
      this.playTimer = null;
    }
  }
}
