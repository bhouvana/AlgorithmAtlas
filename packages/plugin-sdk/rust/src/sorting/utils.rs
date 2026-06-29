fn xorshift32(state: &mut u32) -> u32 {
    let mut s = *state;
    s ^= s << 13;
    s ^= s >> 17;
    s ^= s << 5;
    *state = s;
    s
}

pub fn generate_array(seed: u32, n: usize, input_order: &str) -> Vec<i32> {
    let mut arr: Vec<i32> = (1..=n as i32).collect();
    let mut rng = seed | 1;

    match input_order {
        "sorted"  => arr,
        "reverse" => { arr.reverse(); arr }
        "nearly_sorted" => {
            let num_swaps = (n / 10).max(1);
            for _ in 0..num_swaps {
                let i = (xorshift32(&mut rng) as usize) % n;
                let j = (xorshift32(&mut rng) as usize) % n;
                arr.swap(i, j);
            }
            arr
        }
        _ => {
            for i in (1..n).rev() {
                let j = (xorshift32(&mut rng) as usize) % (i + 1);
                arr.swap(i, j);
            }
            arr
        }
    }
}

use crate::{SimulationFrame, SortState};

pub struct FrameBuilder {
    pub arr: Vec<i32>,
    pub comparisons: usize,
    pub swaps: usize,
    pub sorted_indices: Vec<usize>,
    pub frame_index: usize,
}

impl FrameBuilder {
    pub fn new(arr: Vec<i32>) -> Self {
        Self { arr, comparisons: 0, swaps: 0, sorted_indices: vec![], frame_index: 0 }
    }

    pub fn push(
        &mut self,
        frames: &mut Vec<SimulationFrame>,
        comparing: Option<[usize; 2]>,
        last_swap: Option<[usize; 2]>,
        auxiliary_indices: Vec<usize>,
        description: String,
    ) {
        frames.push(SimulationFrame {
            frame_index: self.frame_index,
            state: SortState {
                array: self.arr.clone(),
                comparing,
                last_swap,
                sorted_indices: self.sorted_indices.clone(),
                auxiliary_indices,
                comparisons: self.comparisons,
                swaps: self.swaps,
                description,
            },
            timestamp_ms: 0.0,
            event_label: None,
        });
        self.frame_index += 1;
    }

    pub fn mark_sorted_range(&mut self, start: usize, end: usize) {
        for i in start..=end {
            if !self.sorted_indices.contains(&i) {
                self.sorted_indices.push(i);
            }
        }
        self.sorted_indices.sort_unstable();
    }

    pub fn mark_all_sorted(&mut self) {
        self.sorted_indices = (0..self.arr.len()).collect();
    }
}
