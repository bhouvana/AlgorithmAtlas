/**
 * Checks whether the Algorithm Atlas API server is reachable.
 *
 * Returns:
 *   null    — initial check in progress
 *   true    — server responded
 *   false   — server unreachable (offline mode)
 *
 * Rechecks every 30 seconds so the UI recovers automatically
 * when the user starts the server after opening the app.
 */

import { useEffect, useState } from 'react';
export { isTauriApp } from '../tauri';

const PROBE_URL =
  (import.meta.env.VITE_API_URL ?? 'http://localhost:8000') +
  '/api/v1/algorithms/categories';

async function probe(): Promise<boolean> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 2500);
  try {
    const res = await fetch(PROBE_URL, { signal: ctrl.signal });
    return res.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timer);
  }
}

export function useServerAvailable(): boolean | null {
  const [available, setAvailable] = useState<boolean | null>(null);

  useEffect(() => {
    probe().then(setAvailable);
    const id = setInterval(() => probe().then(setAvailable), 30_000);
    return () => clearInterval(id);
  }, []);

  return available;
}

