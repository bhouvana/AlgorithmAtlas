import type { AtlasContext, ChatMessage, SSEEvent } from './types';

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

// ── Streaming chat ─────────────────────────────────────────────────────────────

export async function* streamChat(
  message: string,
  context: AtlasContext,
  history: ChatMessage[],
  signal: AbortSignal,
): AsyncGenerator<SSEEvent> {
  const body = {
    message,
    context,
    history: history.map((m) => ({ role: m.role, content: m.content })),
  };

  let response: Response;
  try {
    response = await fetch(`${BASE}/api/v1/ai/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal,
    });
  } catch (err) {
    yield { type: 'error', message: `Network error: ${err}` };
    return;
  }

  if (!response.ok) {
    yield { type: 'error', message: `Server error ${response.status}` };
    return;
  }

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() ?? '';

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const raw = line.slice(6).trim();
        if (!raw) continue;
        try {
          yield JSON.parse(raw) as SSEEvent;
        } catch {
          // malformed line — skip
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

// ── Inline code completion ─────────────────────────────────────────────────────

export async function fetchCompletion(
  prefix: string,
  language: string,
  context: AtlasContext | null,
  signal?: AbortSignal,
): Promise<string> {
  try {
    const res = await fetch(`${BASE}/api/v1/ai/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prefix, language, context }),
      signal,
    });
    if (!res.ok) return '';
    const data = await res.json();
    return (data as { completion: string }).completion ?? '';
  } catch {
    return '';
  }
}

// ── User memory ────────────────────────────────────────────────────────────────

export async function fetchMemory(userId: string): Promise<Record<string, string>> {
  try {
    const res = await fetch(`${BASE}/api/v1/ai/memory?user_id=${encodeURIComponent(userId)}`);
    if (!res.ok) return {};
    const data = await res.json();
    return (data as { memories: Record<string, string> }).memories ?? {};
  } catch {
    return {};
  }
}

export async function saveMemory(userId: string, key: string, value: string): Promise<void> {
  try {
    await fetch(`${BASE}/api/v1/ai/memory`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, key, value }),
    });
  } catch {
    // best-effort
  }
}

// ── Anonymous user identity (persisted in localStorage) ───────────────────────

const USER_ID_KEY = 'atlas_ai_user_id';

export function getOrCreateUserId(): string {
  let id = localStorage.getItem(USER_ID_KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(USER_ID_KEY, id);
  }
  return id;
}
