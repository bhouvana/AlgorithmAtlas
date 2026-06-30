/**
 * InlineCompletionProvider — VS Code-style predictive typing for Monaco Editor.
 *
 * Registers an inline completions provider for the given Monaco language.
 * After a 350ms debounce the code prefix is sent to /api/v1/ai/complete.
 * The returned completion appears as ghost text; Tab to accept, Escape to dismiss.
 *
 * The `enabled` ref lets the toggle be hot-switched without re-registering.
 * Call the returned dispose() to unregister when the component unmounts.
 */
import type { AtlasContext } from '../types';
import { fetchCompletion } from '../api';

type Monaco = typeof import('monaco-editor');
type IDisposable = { dispose(): void };

export function registerAtlasCompletionProvider(
  monaco: Monaco,
  language: string,
  context: { current: AtlasContext | null },
  enabled: { current: boolean },
): IDisposable {
  let debounceTimer: ReturnType<typeof setTimeout> | null = null;

  const disposable = monaco.languages.registerInlineCompletionsProvider(language, {
    provideInlineCompletions: async (model, position, _ctx, token) => {
      if (!enabled.current) return null;

      const prefix = model.getValueInRange({
        startLineNumber: 1,
        startColumn: 1,
        endLineNumber: position.lineNumber,
        endColumn: position.column,
      });

      // Require at least a meaningful prefix before calling the API
      if (prefix.trim().length < 8) return null;

      // Debounce — wait 350ms after user stops typing
      await new Promise<void>((resolve, reject) => {
        if (debounceTimer !== null) clearTimeout(debounceTimer);
        debounceTimer = setTimeout(resolve, 350);
        token.onCancellationRequested(() => {
          if (debounceTimer !== null) clearTimeout(debounceTimer);
          reject(new Error('cancelled'));
        });
      }).catch(() => null);

      if (token.isCancellationRequested) return null;

      const completion = await fetchCompletion(
        prefix,
        language,
        context.current,
      ).catch(() => '');

      if (!completion || token.isCancellationRequested) return null;

      // Insert after the current cursor position
      return {
        items: [
          {
            insertText: completion,
            range: {
              startLineNumber: position.lineNumber,
              startColumn: position.column,
              endLineNumber: position.lineNumber,
              endColumn: position.column,
            },
          },
        ],
        enableForwardStability: true,
      };
    },
    disposeInlineCompletions: () => {},
  });

  return disposable;
}
