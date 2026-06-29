/**
 * Thin wrapper over Tauri 2.x's injected runtime globals.
 *
 * `window.__TAURI_INTERNALS__` is injected automatically when the page
 * runs inside a Tauri desktop window. Using it directly avoids adding
 * `@tauri-apps/api` as a frontend dependency.
 */

declare global {
  interface Window {
    __TAURI_INTERNALS__?: {
      invoke: <T>(command: string, args?: Record<string, unknown>) => Promise<T>;
    };
  }
}

/** True when running inside a Tauri desktop window. */
export function isTauriApp(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;
}

/**
 * Call a Tauri command by name.
 * Throws if called outside a Tauri context — always guard with `isTauriApp()`.
 */
export async function tauriInvoke<T>(
  command: string,
  args?: Record<string, unknown>,
): Promise<T> {
  const internals = window.__TAURI_INTERNALS__;
  if (!internals) throw new Error('Not running in Tauri desktop app');
  return internals.invoke<T>(command, args);
}
