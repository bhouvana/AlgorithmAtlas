// Sorting implementations now live in the shared plugin-sdk crate.
// The individual .rs files in this directory are kept as reference but
// are no longer compiled; all logic routes through the SDK dispatch.
pub use algorithm_atlas_sdk::sorting::run_sort;
