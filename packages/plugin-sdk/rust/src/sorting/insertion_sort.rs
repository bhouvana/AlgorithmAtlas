use crate::SimulationFrame;
use super::utils::{generate_array, FrameBuilder};

pub fn run(seed: u32, n: usize, input_order: &str) -> Vec<SimulationFrame> {
    let mut fb = FrameBuilder::new(generate_array(seed, n, input_order));
    let mut frames = Vec::new();

    fb.sorted_indices.push(0);

    for i in 1..n {
        let key = fb.arr[i];
        let mut j = i;

        fb.push(&mut frames, None, None, vec![i],
            format!("Inserting element {} from index {}", key, i));

        while j > 0 {
            fb.comparisons += 1;
            if fb.arr[j - 1] > key {
                fb.push(&mut frames, Some([j - 1, j]), None, vec![],
                    format!("Comparing {} > {} — shift right", fb.arr[j - 1], key));
                fb.arr[j] = fb.arr[j - 1];
                fb.swaps += 1;
                fb.push(&mut frames, Some([j - 1, j]), Some([j - 1, j]), vec![],
                    format!("Shifted {} right to index {}", fb.arr[j], j));
                j -= 1;
            } else {
                fb.push(&mut frames, Some([j - 1, j]), None, vec![],
                    format!("Comparing {} ≤ {} — found insertion point at {}", fb.arr[j - 1], key, j));
                break;
            }
        }

        fb.arr[j] = key;
        fb.mark_sorted_range(0, i);
        fb.push(&mut frames, None, Some([j, j]), vec![],
            format!("Placed {} at index {} — indices 0..{} sorted", key, j, i));
    }

    fb.mark_all_sorted();
    fb.push(&mut frames, None, None, vec![],
        format!("Sorted — {} comparisons, {} shifts", fb.comparisons, fb.swaps));
    frames
}
