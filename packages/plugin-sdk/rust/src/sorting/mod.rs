pub mod utils;
mod bubble_sort;
mod insertion_sort;
mod selection_sort;
mod merge_sort;
mod quick_sort;

use crate::SimulationFrame;

/// Dispatch: run a named sort algorithm and return all simulation frames.
///
/// # Arguments
/// - `slug`: algorithm identifier — "bubble-sort", "insertion-sort", etc.
/// - `seed`: Xorshift32 PRNG seed (same seed → same array)
/// - `n`: array size (clamped to ≥ 2)
/// - `input_order`: "random" | "sorted" | "reverse" | "nearly_sorted"
pub fn run_sort(slug: &str, seed: u32, n: usize, input_order: &str) -> Vec<SimulationFrame> {
    let n = n.max(2);
    match slug {
        "bubble-sort"    | "bubble_sort"    => bubble_sort::run(seed, n, input_order),
        "insertion-sort" | "insertion_sort" => insertion_sort::run(seed, n, input_order),
        "selection-sort" | "selection_sort" => selection_sort::run(seed, n, input_order),
        "merge-sort"     | "merge_sort"     => merge_sort::run(seed, n, input_order),
        "quick-sort"     | "quick_sort"     => quick_sort::run(seed, n, input_order),
        _                                   => vec![],
    }
}
