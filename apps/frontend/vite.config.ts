import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

// vite-plugin-wasm is only needed when building the WASM engine (npm run build:wasm).
// For regular dev/build it is optional.
let wasmPlugin: any[] = [];
try {
  const { default: wasm } = await import('vite-plugin-wasm');
  wasmPlugin = [wasm()];
} catch {
  // vite-plugin-wasm not installed — WASM algorithms will fall back to server execution
}

export default defineConfig({
  plugins: [react(), ...wasmPlugin],
  resolve: {
    alias: {
      // Points to the wasm-pack output directory.
      // Run: cd packages/wasm-engine && wasm-pack build --target web --out-dir ../../apps/frontend/src/wasm-engine
      '@wasm-engine': resolve(__dirname, 'src/wasm-engine'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        changeOrigin: true,
      },
    },
  },
  build: {
    target: 'esnext',
    sourcemap: true,
  },
});
