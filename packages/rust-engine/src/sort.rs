/// High-performance sorting implementations.
///
/// These are NOT instrumented — they produce no frames.
/// They are used by the Benchmark Engine for raw throughput measurement.
/// The visualization path always uses the Python instrumented implementations.

use pyo3::prelude::*;
use rayon::prelude::*;

/// Parallel quicksort. Uses rayon for data-parallel divide-and-conquer.
/// Falls back to std::sort_unstable for sub-arrays ≤ 1024 elements.
#[pyfunction]
pub fn quicksort_parallel_rs(py: Python<'_>, data: Vec<i64>) -> PyResult<Vec<i64>> {
    let mut arr = data;
    py.allow_threads(|| parallel_quicksort(&mut arr));
    Ok(arr)
}

/// Parallel merge sort. Always O(n log n), stable, allocates O(n) extra space.
#[pyfunction]
pub fn mergesort_parallel_rs(py: Python<'_>, data: Vec<i64>) -> PyResult<Vec<i64>> {
    let result = py.allow_threads(|| parallel_mergesort(data));
    Ok(result)
}

/// LSD Radix sort. O(d * n) where d = number of digits. Non-comparative.
#[pyfunction]
pub fn radixsort_rs(py: Python<'_>, data: Vec<i64>) -> PyResult<Vec<i64>> {
    let mut arr = data;
    py.allow_threads(|| radix_sort(&mut arr));
    Ok(arr)
}

// ──────────────────────────────────────────────────────────────────────────────
// Internal implementations
// ──────────────────────────────────────────────────────────────────────────────

const PARALLEL_THRESHOLD: usize = 1024;

fn parallel_quicksort(arr: &mut [i64]) {
    if arr.len() <= PARALLEL_THRESHOLD {
        arr.sort_unstable();
        return;
    }
    let pivot_idx = partition(arr);
    let (left, right) = arr.split_at_mut(pivot_idx);
    let right = &mut right[1..];
    rayon::join(
        || parallel_quicksort(left),
        || parallel_quicksort(right),
    );
}

fn partition(arr: &mut [i64]) -> usize {
    let n = arr.len();
    // Median-of-three pivot selection
    let mid = n / 2;
    if arr[0] > arr[mid] { arr.swap(0, mid); }
    if arr[0] > arr[n - 1] { arr.swap(0, n - 1); }
    if arr[mid] > arr[n - 1] { arr.swap(mid, n - 1); }
    let pivot = arr[mid];
    arr.swap(mid, n - 1);
    let mut store = 0;
    for i in 0..n - 1 {
        if arr[i] <= pivot {
            arr.swap(i, store);
            store += 1;
        }
    }
    arr.swap(store, n - 1);
    store
}

fn parallel_mergesort(arr: Vec<i64>) -> Vec<i64> {
    if arr.len() <= PARALLEL_THRESHOLD {
        let mut v = arr;
        v.sort_unstable();
        return v;
    }
    let mid = arr.len() / 2;
    let (left, right) = arr.split_at(mid);
    let (sorted_left, sorted_right) = rayon::join(
        || parallel_mergesort(left.to_vec()),
        || parallel_mergesort(right.to_vec()),
    );
    merge(sorted_left, sorted_right)
}

fn merge(left: Vec<i64>, right: Vec<i64>) -> Vec<i64> {
    let mut result = Vec::with_capacity(left.len() + right.len());
    let (mut i, mut j) = (0, 0);
    while i < left.len() && j < right.len() {
        if left[i] <= right[j] {
            result.push(left[i]);
            i += 1;
        } else {
            result.push(right[j]);
            j += 1;
        }
    }
    result.extend_from_slice(&left[i..]);
    result.extend_from_slice(&right[j..]);
    result
}

fn radix_sort(arr: &mut Vec<i64>) {
    if arr.is_empty() { return; }
    let max_val = *arr.iter().max().unwrap_or(&0);
    let mut exp = 1i64;
    while max_val / exp > 0 {
        counting_sort_by_digit(arr, exp);
        exp *= 10;
    }
}

fn counting_sort_by_digit(arr: &mut Vec<i64>, exp: i64) {
    let n = arr.len();
    let mut output = vec![0i64; n];
    let mut count = vec![0usize; 10];
    for &val in arr.iter() {
        let digit = ((val / exp) % 10) as usize;
        count[digit] += 1;
    }
    for i in 1..10 {
        count[i] += count[i - 1];
    }
    for &val in arr.iter().rev() {
        let digit = ((val / exp) % 10) as usize;
        count[digit] -= 1;
        output[count[digit]] = val;
    }
    arr.copy_from_slice(&output);
}

// ──────────────────────────────────────────────────────────────────────────────
// Tests
// ──────────────────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    fn assert_sorted(arr: &[i64]) {
        for i in 1..arr.len() {
            assert!(arr[i - 1] <= arr[i], "Not sorted at index {i}: {:?}", arr);
        }
    }

    #[test]
    fn test_quicksort_random() {
        let mut arr = vec![5, 2, 8, 1, 9, 3, 7, 4, 6];
        parallel_quicksort(&mut arr);
        assert_sorted(&arr);
    }

    #[test]
    fn test_quicksort_already_sorted() {
        let mut arr: Vec<i64> = (1..=100).collect();
        parallel_quicksort(&mut arr);
        assert_sorted(&arr);
    }

    #[test]
    fn test_quicksort_reverse_sorted() {
        let mut arr: Vec<i64> = (1..=100).rev().collect();
        parallel_quicksort(&mut arr);
        assert_sorted(&arr);
    }

    #[test]
    fn test_quicksort_single_element() {
        let mut arr = vec![42i64];
        parallel_quicksort(&mut arr);
        assert_eq!(arr, vec![42]);
    }

    #[test]
    fn test_quicksort_empty() {
        let mut arr: Vec<i64> = vec![];
        parallel_quicksort(&mut arr);
        assert!(arr.is_empty());
    }

    #[test]
    fn test_mergesort_random() {
        let arr = vec![5i64, 2, 8, 1, 9, 3];
        let result = parallel_mergesort(arr.clone());
        let mut expected = arr;
        expected.sort();
        assert_eq!(result, expected);
    }

    #[test]
    fn test_radixsort_random() {
        let mut arr = vec![170i64, 45, 75, 90, 802, 24, 2, 66];
        radix_sort(&mut arr);
        assert_sorted(&arr);
    }

    #[test]
    fn test_parallel_quicksort_large() {
        let n = 100_000;
        let mut arr: Vec<i64> = (0..n).rev().collect();
        parallel_quicksort(&mut arr);
        assert_sorted(&arr);
        assert_eq!(arr.len(), n as usize);
    }
}
