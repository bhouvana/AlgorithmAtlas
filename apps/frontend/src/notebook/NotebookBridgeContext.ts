/**
 * NotebookBridgeContext — exposes current notebook state to Atlas AI.
 *
 * NotebookPage provides the value; useAtlasContext reads from it.
 * Components outside the notebook tree get null (handled gracefully).
 */
import { createContext } from 'react';

export interface NotebookBridge {
  language: string;
  source: string;
  lastOutput: string;
  lastError: string;
}

export const NotebookBridgeContext = createContext<NotebookBridge | null>(null);
