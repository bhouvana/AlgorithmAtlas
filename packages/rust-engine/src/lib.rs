/// Algorithm Atlas — Rust Engine (PyO3)
///
/// Build:
///   maturin develop                   # editable install for dev
///   maturin build --release           # wheel for distribution
///
/// Python import:
///   import algorithm_atlas_rs as rust_engine
///
/// Functions fall into two groups:
///   1. Raw sort (no frames, max throughput)  — quicksort_parallel_rs, etc.
///   2. Simulation sort (full frames, JSON)   — run_sort_rs, benchmark_sort_rs, benchmark_parallel_rs

use pyo3::prelude::*;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::time::Instant;

mod sort;

// ── Simulation API (uses shared SDK) ─────────────────────────────────────────

/// Run a sort algorithm and return all simulation frames as a JSON string.
///
/// Returns `"[]"` for unknown slugs. Compatible with WasmController's frame format.
#[pyfunction]
pub fn run_sort_rs(
    py: Python<'_>,
    slug: &str,
    seed: u32,
    array_size: usize,
    input_order: &str,
) -> PyResult<String> {
    let slug = slug.to_string();
    let input_order = input_order.to_string();
    let frames = py.allow_threads(|| {
        algorithm_atlas_sdk::sorting::run_sort(&slug, seed, array_size, &input_order)
    });
    Ok(serde_json::to_string(&frames).unwrap_or_else(|_| "[]".to_string()))
}

/// Benchmark a sort algorithm: run it `trials` times and return median milliseconds.
///
/// Uses `std::time::Instant` for high-resolution native timing (unlike WASM's
/// `performance.now()`, this is not subject to browser timer clamping).
#[pyfunction]
pub fn benchmark_sort_rs(
    py: Python<'_>,
    slug: &str,
    seed: u32,
    array_size: usize,
    input_order: &str,
    trials: u32,
) -> PyResult<f64> {
    let trials = trials.max(1) as usize;
    let slug = slug.to_string();
    let input_order = input_order.to_string();

    let median_ms = py.allow_threads(|| {
        let mut times: Vec<f64> = (0..trials)
            .map(|i| {
                let t = Instant::now();
                let _ = algorithm_atlas_sdk::sorting::run_sort(
                    &slug,
                    seed + i as u32,
                    array_size,
                    &input_order,
                );
                t.elapsed().as_secs_f64() * 1000.0
            })
            .collect();
        times.sort_by(|a, b| a.partial_cmp(b).unwrap());
        times[times.len() / 2]
    });

    Ok(median_ms)
}

/// Parallel benchmark: run multiple (slug, size) requests concurrently via Rayon.
///
/// Input JSON:  `[{"slug": str, "seed": int, "array_size": int, "input_order": str, "trials": int}, ...]`
/// Output JSON: `[{"slug": str, "array_size": int, "ms": float}, ...]`
///
/// All requests are dispatched to the Rayon thread pool simultaneously.
/// On an 8-core machine this gives ~8× throughput over sequential Python benchmarks.
#[pyfunction]
pub fn benchmark_parallel_rs(py: Python<'_>, requests_json: &str) -> PyResult<String> {
    #[derive(Deserialize)]
    struct Request {
        slug: String,
        seed: u32,
        array_size: usize,
        input_order: String,
        trials: u32,
    }
    #[derive(Serialize)]
    struct Result {
        slug: String,
        array_size: usize,
        ms: f64,
    }

    let requests: Vec<Request> =
        serde_json::from_str(requests_json).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;

    let results: Vec<Result> = py.allow_threads(|| {
        requests
            .par_iter()
            .map(|req| {
                let trials = req.trials.max(1) as usize;
                let mut times: Vec<f64> = (0..trials)
                    .map(|i| {
                        let t = Instant::now();
                        let _ = algorithm_atlas_sdk::sorting::run_sort(
                            &req.slug,
                            req.seed + i as u32,
                            req.array_size,
                            &req.input_order,
                        );
                        t.elapsed().as_secs_f64() * 1000.0
                    })
                    .collect();
                times.sort_by(|a, b| a.partial_cmp(b).unwrap());
                Result {
                    slug: req.slug.clone(),
                    array_size: req.array_size,
                    ms: times[times.len() / 2],
                }
            })
            .collect()
    });

    Ok(serde_json::to_string(&results).unwrap_or_else(|_| "[]".to_string()))
}

// ── Module definition ─────────────────────────────────────────────────────────

#[pymodule]
fn algorithm_atlas_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Raw high-throughput sort (no visualization frames)
    m.add_function(wrap_pyfunction!(sort::quicksort_parallel_rs, m)?)?;
    m.add_function(wrap_pyfunction!(sort::mergesort_parallel_rs, m)?)?;
    m.add_function(wrap_pyfunction!(sort::radixsort_rs, m)?)?;

    // Simulation sort (full visualization frames + benchmarking)
    m.add_function(wrap_pyfunction!(run_sort_rs, m)?)?;
    m.add_function(wrap_pyfunction!(benchmark_sort_rs, m)?)?;
    m.add_function(wrap_pyfunction!(benchmark_parallel_rs, m)?)?;

    Ok(())
}
