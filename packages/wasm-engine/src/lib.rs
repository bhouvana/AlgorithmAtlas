/// Algorithm Atlas WASM Engine
///
/// Exposed JS API:
///   run_sort(slug, seed, array_size, input_order) → JSON string of SimulationFrame[]
///
/// Build:
///   wasm-pack build --target web --out-dir ../../apps/frontend/src/wasm-engine
///
/// The returned JSON matches the frontend SimulationFrame interface exactly,
/// so WasmController can parse it and feed frames directly to the store.

use wasm_bindgen::prelude::*;
use algorithm_atlas_sdk::sorting::run_sort as sdk_run_sort;

mod sorting; // thin shim; actual impls live in algorithm_atlas_sdk::sorting

/// Run a sort algorithm and return all simulation frames as a JSON string.
///
/// # Arguments
/// - `slug`:         algorithm identifier, e.g. "bubble-sort"
/// - `seed`:         PRNG seed for deterministic array generation
/// - `array_size`:   number of elements (2–200)
/// - `input_order`:  "random" | "sorted" | "reverse" | "nearly_sorted"
///
/// # Returns
/// JSON string of `SimulationFrame[]`. Returns `"[]"` for unknown slugs.
#[wasm_bindgen]
pub fn run_sort(slug: &str, seed: u32, array_size: u32, input_order: &str) -> String {
    let frames = sdk_run_sort(slug, seed, array_size as usize, input_order);
    serde_json::to_string(&frames).unwrap_or_else(|_| "[]".to_string())
}

/// Benchmark a sort algorithm: run it `trials` times and return median ms.
/// Uses `performance.now()` via a JS import, so it only works in a browser/worker.
#[wasm_bindgen]
pub fn benchmark_sort(slug: &str, seed: u32, array_size: u32, input_order: &str, trials: u32) -> f64 {
    let trials = trials.max(1);
    let mut times = Vec::with_capacity(trials as usize);
    for i in 0..trials {
        let t_start = js_sys::Date::now();
        let _ = sdk_run_sort(slug, seed + i, array_size as usize, input_order);
        times.push(js_sys::Date::now() - t_start);
    }
    times.sort_by(|a, b| a.partial_cmp(b).unwrap());
    times[times.len() / 2]
}
