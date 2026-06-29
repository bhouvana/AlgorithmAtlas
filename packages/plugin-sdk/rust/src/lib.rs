/// Algorithm Atlas — Rust Plugin SDK
///
/// Mirrors the Python SDK types for WASM-compiled algorithm plugins.
/// All types implement Serialize/Deserialize so they can be sent as JSON
/// through the wasm-bindgen boundary.

pub mod sorting;

use serde::{Deserialize, Serialize};

// ── Metadata ──────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AlgorithmMetadata {
    pub slug: String,
    pub name: String,
    pub category: String,
    pub visualization_type: String,
    pub execution_target: String,
    pub complexity_time_best: String,
    pub complexity_time_average: String,
    pub complexity_time_worst: String,
    pub complexity_space: String,
}

// ── Simulation params ─────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SortParams {
    pub seed: u32,
    pub array_size: u32,
    pub input_order: String,
}

// ── Sort state (mirrors Python SortState) ─────────────────────────────────────

/// Matches the frontend ArrayBarRenderer's SortState interface exactly.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SortState {
    pub array: Vec<i32>,
    /// Pair of indices being compared this frame.
    pub comparing: Option<[usize; 2]>,
    /// Pair of indices that were just swapped/moved.
    pub last_swap: Option<[usize; 2]>,
    /// Indices known to be in their final sorted position.
    pub sorted_indices: Vec<usize>,
    /// Indices highlighted as auxiliary (pivot, current-min, etc.).
    pub auxiliary_indices: Vec<usize>,
    pub comparisons: usize,
    pub swaps: usize,
    pub description: String,
}

// ── Simulation frame (mirrors frontend SimulationFrame) ───────────────────────

/// Matches the frontend SimulationFrame interface.
/// The `state` field contains SortState nested as a JSON object.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SimulationFrame {
    pub frame_index: usize,
    pub state: SortState,
    /// Always 0.0 for WASM (computation is synchronous, no real timestamps).
    pub timestamp_ms: f64,
    pub event_label: Option<String>,
}

// ── Plugin trait ──────────────────────────────────────────────────────────────

pub trait SortPlugin {
    fn metadata(&self) -> AlgorithmMetadata;
    fn run(&self, params: SortParams) -> Vec<SimulationFrame>;
}
