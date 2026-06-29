/// Bubble Sort — instrumented for Algorithm Atlas WASM visualization.
///
/// Optimized variant with early-termination: if no swap occurs in a pass,
/// the array is already sorted. Matches the Python plugin's frame semantics.

use algorithm_atlas_sdk::SimulationFrame;
use super::utils::{generate_array, FrameBuilder};

pub fn run(seed: u32, array_size: u32, input_order: &str) -> Vec<SimulationFrame> {
    let n = (array_size as usize).max(2);
    let mut fb = FrameBuilder::new(generate_array(seed, n, input_order));
    let mut frames = Vec::new();

    for pass in 0..n {
        let boundary = n - pass - 1;
        let mut swapped_this_pass = false;

        for j in 0..boundary {
            fb.comparisons += 1;

            if fb.arr[j] > fb.arr[j + 1] {
                fb.push(
                    &mut frames,
                    Some([j, j + 1]),
                    None,
                    vec![],
                    format!(
                        "Comparing index {} ({}) and {} ({}) — will swap",
                        j, fb.arr[j], j + 1, fb.arr[j + 1]
                    ),
                );

                fb.arr.swap(j, j + 1);
                fb.swaps += 1;
                swapped_this_pass = true;

                fb.push(
                    &mut frames,
                    Some([j, j + 1]),
                    Some([j, j + 1]),
                    vec![],
                    format!("Swapped index {} and {} — swap #{}", j, j + 1, fb.swaps),
                );
            } else {
                fb.push(
                    &mut frames,
                    Some([j, j + 1]),
                    None,
                    vec![],
                    format!(
                        "Comparing index {} ({}) and {} ({}) — no swap needed",
                        j, fb.arr[j], j + 1, fb.arr[j + 1]
                    ),
                );
            }
        }

        fb.sorted_indices.push(boundary);
        fb.sorted_indices.sort_unstable();

        if !swapped_this_pass {
            fb.mark_sorted_range(0, boundary.saturating_sub(1));
            break;
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
