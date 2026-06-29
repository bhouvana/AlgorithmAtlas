/**
 * Type declarations for the wasm-pack generated WASM engine.
 *
 * This file is a stub used during TypeScript compilation before the real
 * wasm-pack output exists. It is overwritten by wasm-pack when you run:
 *
 *   npm run build:wasm
 *
 * If the generated wasm_engine.d.ts from wasm-pack conflicts with this file,
 * the wasm-pack version takes precedence (it's more specific).
 */

/** Initialize the WASM binary. Must be awaited before calling any other export. */
declare function init(): Promise<void>;
export default init;

/**
 * Run a sort algorithm and return all simulation frames as a JSON string.
 *
 * @param slug        - Algorithm slug e.g. "bubble-sort"
 * @param seed        - PRNG seed for deterministic array generation
 * @param array_size  - Number of elements (2–200)
 * @param input_order - "random" | "sorted" | "reverse" | "nearly_sorted"
 * @returns           - JSON string of SimulationFrame[]
 */
export function run_sort(
  slug: string,
  seed: number,
  array_size: number,
  input_order: string,
): string;

/**
 * Benchmark a sort algorithm.
 *
 * @param slug        - Algorithm slug
 * @param seed        - PRNG seed
 * @param array_size  - Input size
 * @param input_order - Input distribution
 * @param trials      - Number of repetitions (median is returned)
 * @returns           - Median execution time in milliseconds
 */
export function benchmark_sort(
  slug: string,
  seed: number,
  array_size: number,
  input_order: string,
  trials: number,
): number;
