/**
 * Typed API client — wraps all REST calls to the backend.
 *
 * All functions throw on non-2xx responses with a descriptive error.
 * WebSocket URLs are constructed here so the base URL is configured once.
 */

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
const WS_BASE = import.meta.env.VITE_WS_URL ?? BASE_URL.replace(/^https/, 'wss').replace(/^http/, 'ws');

// ──────────────────────────────────────────────────────────────────────────────
// Types (mirrors backend Pydantic models)
// ──────────────────────────────────────────────────────────────────────────────

export interface ComplexitySpec {
  time_best: string;
  time_average: string;
  time_worst: string;
  space: string;
}

export interface Reference {
  title: string;
  type: 'paper' | 'book' | 'video' | 'article';
  url?: string;
}

export interface AlgorithmSummary {
  slug: string;
  name: string;
  category: string;
  visualization_type: string;
  execution_target: 'server' | 'wasm' | 'both';
  complexity: ComplexitySpec;
  tags: string[];
  description: string;
}

export interface AlgorithmDetail extends AlgorithmSummary {
  intuition: string;
  references: Reference[];
  default_params: Record<string, unknown>;
  version: string;
  benchmark_enabled: boolean;
}

export interface CategoryInfo {
  slug: string;
  name: string;
  algorithm_count: number;
}

export interface CreateSimulationRequest {
  algorithm_slug: string;
  params?: Record<string, unknown>;
  seed?: number;
}

export interface CreateSimulationResponse {
  session_id: string;
  algorithm_slug: string;
  status: string;
  seed: number;
}

export interface BenchmarkSizeResult {
  input_size: number;
  frame_count: number;
  init_ms: number;
  steps_ms: number;
  total_ms: number;
}

export interface BenchmarkRequest {
  algorithm_slug: string;
  sizes?: number[];
  size_param?: string;
  param_overrides?: Record<string, unknown>;
  trials?: number;
  seed?: number;
}

export interface AlgorithmSource {
  slug: string;
  filename: string;
  source: string;
  language: string;
  line_count: number;
}

export interface BenchmarkResponse {
  slug: string;
  size_param: string;
  results: BenchmarkSizeResult[];
  engine: 'python' | 'rust';
}

export interface BenchmarkConfigResponse {
  slug: string;
  category: string;
  size_param: string;
  default_sizes: number[];
  label: string;
}

// ──────────────────────────────────────────────────────────────────────────────
// HTTP helpers
// ──────────────────────────────────────────────────────────────────────────────

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`GET ${path} failed (${res.status}): ${body}`);
  }
  return res.json() as Promise<T>;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`POST ${path} failed (${res.status}): ${text}`);
  }
  return res.json() as Promise<T>;
}

async function del(path: string): Promise<void> {
  const res = await fetch(`${BASE_URL}${path}`, { method: 'DELETE' });
  if (!res.ok && res.status !== 204) {
    throw new Error(`DELETE ${path} failed (${res.status})`);
  }
}

// ──────────────────────────────────────────────────────────────────────────────
// Algorithm endpoints
// ──────────────────────────────────────────────────────────────────────────────

export const api = {
  algorithms: {
    list: (params?: {
      category?: string;
      search?: string;
      execution_target?: string;
    }) => {
      const qs = new URLSearchParams();
      if (params?.category) qs.set('category', params.category);
      if (params?.search) qs.set('search', params.search);
      if (params?.execution_target) qs.set('execution_target', params.execution_target);
      const query = qs.toString() ? `?${qs}` : '';
      return get<AlgorithmSummary[]>(`/api/v1/algorithms${query}`);
    },

    get: (slug: string) =>
      get<AlgorithmDetail>(`/api/v1/algorithms/${slug}`),

    getSource: (slug: string) =>
      get<AlgorithmSource>(`/api/v1/algorithms/${slug}/source`),

    categories: () =>
      get<CategoryInfo[]>('/api/v1/algorithms/categories'),
  },

  simulations: {
    create: (req: CreateSimulationRequest) =>
      post<CreateSimulationResponse>('/api/v1/simulations', req),

    delete: (sessionId: string) =>
      del(`/api/v1/simulations/${sessionId}`),
  },

  benchmarks: {
    run: (req: BenchmarkRequest) =>
      post<BenchmarkResponse>('/api/v1/benchmarks', req),

    config: (slug: string) =>
      get<BenchmarkConfigResponse>(`/api/v1/benchmarks/config/${slug}`),
  },

  notebook: {
    run: (body: { source: string; language?: string; timeout?: number }) =>
      post<{ output: string; error: string; duration_ms: number; language: string }>('/api/v1/notebook/run', body),
  },

  ws: {
    simulationUrl: (sessionId: string) =>
      `${WS_BASE}/ws/v1/simulations/${sessionId}`,
  },
};
