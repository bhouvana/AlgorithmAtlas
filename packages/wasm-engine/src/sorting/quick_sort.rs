/// Quick Sort — instrumented for Algorithm Atlas WASM visualization.
///
/// Lomuto partition scheme with the last element as pivot.
/// Uses auxiliary_indices to highlight the current pivot.
/// Iterative (stack-based) to avoid recursion depth issues with large arrays.

use algorithm_atlas_sdk::SimulationFrame;
use super::utils::{generate_array, FrameBuilder};

pub fn run(seed: u32, array_size: u32, input_order: &str) -> Vec<SimulationFrame> {
    let n = (array_size as usize).max(2);
    let mut fb = FrameBuilder::new(generate_array(seed, n, input_order));
    let mut frames = Vec::new();

    // Explicit stack: (low, high)
    let mut stack: Vec<(usize, usize)> = vec![(0, n - 1)];

    while let Some((low, high)) = stack.pop() {
        if low >= high {
            fb.sorted_indices.push(low);
            fb.sorted_indices.sort_unstable();
            continue;
        }

        let pivot_idx = partition(&mut fb, &mut frames, low, high);

        // Mark pivot as sorted
        if !fb.sorted_indices.contains(&pivot_idx) {
            fb.sorted_indices.push(pivot_idx);
            fb.sorted_indices.sort_unstable();
        }

        // Push sub-ranges (push larger first so smaller is processed first)
        if pivot_idx > low {
            if pivot_idx > 0 && pivot_idx - 1 > low {
                stack.push((low, pivot_idx - 1));
            } else if pivot_idx > 0 {
                fb.sorted_indices.push(low);
                fb.sorted_indices.sort_unstable();
            }
        } else {
            fb.sorted_indices.push(low);
            fb.sorted_indices.sort_unstable();
        }

        if pivot_idx + 1 < high {
            stack.push((pivot_idx + 1, high));
        } else if pivot_idx + 1 == high {
            fb.sorted_indices.push(high);
            fb.sorted_indices.sort_unstable();
        }
    }

    fb.mark_all_sorted();
    fb.push(
        &mut frames,
        None,
        None,
        vec![],
        format!("Sorted — {} comparisons, {} swaps", fb.comparisons, fb.swaps),
    );

    frames
}

fn partition(
    fb: &mut FrameBuilder,
    frames: &mut Vec<SimulationFrame>,
    low: usize,
    high: usize,
) -> usize {
    let pivot = fb.arr[high];

    fb.push(
        frames,
        None,
        None,
        vec![high],
        format!("Partition [{}, {}]: pivot = {} at index {}", low, high, pivot, high),
    );

    let mut store = low;

    for j in low..high {
        fb.comparisons += 1;

        if fb.arr[j] <= pivot {
            fb.push(
                frames,
                Some([j, high]),
                None,
                vec![high],
                format!(
                    "Compare arr[{}]={} ≤ pivot {} — will swap with store index {}",
                    j, fb.arr[j], pivot, store
                ),
            );

            if store != j {
                fb.arr.swap(store, j);
                fb.swaps += 1;
                fb.push(
                    frames,
                    None,
                    Some([store, j]),
                    vec![high],
                    format!("Swapped index {} and {} — swap #{}", store, j, fb.swaps),
                );
            }
            store += 1;
        } else {
            fb.push(
                frames,
                Some([j, high]),
                None,
                vec![high],
                format!(
                    "Compare arr[{}]={} > pivot {} — no swap",
                    j, fb.arr[j], pivot
                ),
            );
        }
    }

    // Place pivot in final position
    if store != high {
        fb.arr.swap(store, high);
        fb.swaps += 1;
    }

    fb.push(
        frames,
        None,
        Some([store, high]),
        vec![store],
        format!("Pivot {} placed at final index {}", pivot, store),
    );

    store
}
