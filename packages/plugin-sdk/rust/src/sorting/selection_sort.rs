use crate::SimulationFrame;
use super::utils::{generate_array, FrameBuilder};

pub fn run(seed: u32, n: usize, input_order: &str) -> Vec<SimulationFrame> {
    let mut fb = FrameBuilder::new(generate_array(seed, n, input_order));
    let mut frames = Vec::new();

    for i in 0..n - 1 {
        let mut min_idx = i;
        fb.push(&mut frames, None, None, vec![min_idx],
            format!("Pass {}: searching for minimum in [{}, {}]", i + 1, i, n - 1));

        for j in (i + 1)..n {
            fb.comparisons += 1;
            if fb.arr[j] < fb.arr[min_idx] {
                fb.push(&mut frames, Some([j, min_idx]), None, vec![min_idx],
                    format!("New minimum: {} at index {} (beats {} at index {})", fb.arr[j], j, fb.arr[min_idx], min_idx));
                min_idx = j;
            } else {
                fb.push(&mut frames, Some([j, min_idx]), None, vec![min_idx],
                    format!("Comparing {} at {} with current min {} at {} — no change", fb.arr[j], j, fb.arr[min_idx], min_idx));
            }
        }

        if min_idx != i {
            fb.arr.swap(i, min_idx);
            fb.swaps += 1;
            fb.push(&mut frames, None, Some([i, min_idx]), vec![],
                format!("Swap: placed {} at index {} — swap #{}", fb.arr[i], i, fb.swaps));
        } else {
            fb.push(&mut frames, None, None, vec![],
                format!("No swap needed: {} already at index {}", fb.arr[i], i));
        }

        fb.sorted_indices.push(i);
        fb.sorted_indices.sort_unstable();
    }

    fb.mark_all_sorted();
    fb.push(&mut frames, None, None, vec![],
        format!("Sorted — {} comparisons, {} swaps", fb.comparisons, fb.swaps));
    frames
}
