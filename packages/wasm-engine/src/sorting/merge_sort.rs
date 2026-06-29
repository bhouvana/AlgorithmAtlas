/// Merge Sort — instrumented for Algorithm Atlas WASM visualization.
///
/// Bottom-up iterative merge sort — no recursion, straightforward frame generation.
/// Each pass doubles the subarray width. During each merge, shows comparisons
/// between the two halves and element placements.

use algorithm_atlas_sdk::SimulationFrame;
use super::utils::{generate_array, FrameBuilder};

pub fn run(seed: u32, array_size: u32, input_order: &str) -> Vec<SimulationFrame> {
    let n = (array_size as usize).max(2);
    let mut fb = FrameBuilder::new(generate_array(seed, n, input_order));
    let mut frames = Vec::new();
    let mut pass_num = 0;

    let mut width = 1usize;
    while width < n {
        pass_num += 1;
        fb.push(
            &mut frames,
            None,
            None,
            vec![],
            format!("Pass {}: merging subarrays of width {}", pass_num, width),
        );

        let mut left = 0;
        while left < n {
            let mid = (left + width).min(n);
            let right = (left + 2 * width).min(n);

            if mid < right {
                merge_step(&mut fb, &mut frames, left, mid, right);
            }

            left += 2 * width;
        }

        width *= 2;
    }

    fb.mark_all_sorted();
    fb.push(
        &mut frames,
        None,
        None,
        vec![],
        format!("Sorted — {} comparisons, {} moves", fb.comparisons, fb.swaps),
    );

    frames
}

fn merge_step(
    fb: &mut FrameBuilder,
    frames: &mut Vec<SimulationFrame>,
    left: usize,
    mid: usize,
    right: usize,
) {
    let left_half = fb.arr[left..mid].to_vec();
    let right_half = fb.arr[mid..right].to_vec();

    let auxiliary: Vec<usize> = (left..right).collect();
    fb.push(
        frames,
        None,
        None,
        auxiliary.clone(),
        format!("Merging [{}, {}] and [{}, {}]", left, mid - 1, mid, right - 1),
    );

    let mut i = 0;
    let mut j = 0;
    let mut k = left;

    while i < left_half.len() && j < right_half.len() {
        fb.comparisons += 1;
        let li = left + i;
        let rj = mid + j;

        if left_half[i] <= right_half[j] {
            fb.push(
                frames,
                Some([li, rj]),
                None,
                auxiliary.clone(),
                format!(
                    "Take {} from left (index {}) — {} ≤ {}",
                    left_half[i], li, left_half[i], right_half[j]
                ),
            );
            fb.arr[k] = left_half[i];
            fb.swaps += 1;
            i += 1;
        } else {
            fb.push(
                frames,
                Some([li, rj]),
                None,
                auxiliary.clone(),
                format!(
                    "Take {} from right (index {}) — {} > {}",
                    right_half[j], rj, left_half[i], right_half[j]
                ),
            );
            fb.arr[k] = right_half[j];
            fb.swaps += 1;
            j += 1;
        }

        fb.push(
            frames,
            None,
            Some([k, k]),
            auxiliary.clone(),
            format!("Placed at index {}", k),
        );
        k += 1;
    }

    while i < left_half.len() {
        fb.arr[k] = left_half[i];
        fb.swaps += 1;
        fb.push(
            frames,
            None,
            Some([k, k]),
            auxiliary.clone(),
            format!("Copied remaining left element {} to index {}", left_half[i], k),
        );
        i += 1;
        k += 1;
    }

    while j < right_half.len() {
        fb.arr[k] = right_half[j];
        fb.swaps += 1;
        fb.push(
            frames,
            None,
            Some([k, k]),
            auxiliary.clone(),
            format!("Copied remaining right element {} to index {}", right_half[j], k),
        );
        j += 1;
        k += 1;
    }
}
