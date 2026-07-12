"""Time each family build to find what's slow."""
import time, sys, loguru
loguru.logger.remove()
sys.path.insert(0, 'scripts')
sys.path.insert(0, 'apps/backend')
import logging; logging.disable(logging.CRITICAL + 10)

import seed_atlas_code as seed_mod
from algorithm_atlas.atlascode.discovery import discover_registered_algorithms

registered = discover_registered_algorithms()
t0 = time.time()
print(f"discovery: 0.0s ({len(registered)} algs)")

curated_algorithm_slugs = {p[0]['algorithm_slug'] for p in seed_mod.PROBLEMS if p[0].get('algorithm_slug')}

families = [
    ("sorting", "sorting", "build_sorting_problems"),
    ("searching", "searching", "build_searching_problems"),
    ("number-theory", "number_theory", "build_number_theory_problems"),
    ("dynamic-programming", "dynamic_programming", "build_dynamic_programming_problems"),
    ("greedy", "greedy", "build_greedy_problems"),
    ("divide-and-conquer", "divide_and_conquer", "build_divide_and_conquer_problems"),
    ("string", "string_family", "build_string_problems"),
]

existing = {p[0]['id'] for p in seed_mod.PROBLEMS}
prev = time.time()

for tag, mod_name, func_name in families:
    mod = __import__(f"algorithm_atlas.atlascode.families.{mod_name}", fromlist=[func_name])
    func = getattr(mod, func_name)
    t1 = time.time()
    probs, skips = func(registered, curated_algorithm_slugs)
    t2 = time.time()
    existing |= {p[0]['id'] for p in probs}
    total = t2 - t1
    cum = t2 - t0
    print(f"{tag}: {total:.1f}s ({len(probs)}p, {len(skips)} skipped) [cum={cum:.1f}s]")
    sys.stdout.flush()

# Now variant families
variant_families = [
    ("binary-search-variants", "binary_search_variants", "build_binary_search_variant_problems"),
    ("sliding-window-variants", "sliding_window_variants", "build_sliding_window_variant_problems"),
    ("bfs-graph-variants", "bfs_graph_variants", "build_bfs_graph_variant_problems"),
    ("array-hashing-variants", "array_hashing_variants", "build_array_hashing_variant_problems"),
    ("stack-variants", "stack_variants", "build_stack_variant_problems"),
    ("bit-manipulation-variants", "bit_manipulation_variants", "build_bit_manipulation_variant_problems"),
    ("tree-variants", "tree_variants", "build_tree_variant_problems"),
    ("dp-variants", "dp_variants", "build_dp_variant_problems"),
    ("linked-list-variants", "linked_list_variants", "build_linked_list_variant_problems"),
    ("backtracking-count-variants", "backtracking_count_variants", "build_backtracking_count_variant_problems"),
]

for tag, mod_name, func_name in variant_families:
    mod = __import__(f"algorithm_atlas.atlascode.families.{mod_name}", fromlist=[func_name])
    func = getattr(mod, func_name)
    t1 = time.time()
    probs, skips = func(registered, existing)
    t2 = time.time()
    existing |= {p[0]['id'] for p in probs}
    total = t2 - t1
    cum = t2 - t0
    print(f"{tag}: {total:.1f}s ({len(probs)}p, {len(skips)} skipped) [cum={cum:.1f}s]")
    sys.stdout.flush()

# Famous concepts families
famous_families = [
    ("famous-easy", "famous_easy", "build_famous_easy_problems"),
    ("famous-arrays-matrix", "famous_arrays_matrix", "build_famous_arrays_matrix_problems"),
    ("famous-graphs-trees-lists", "famous_graphs_trees_lists", "build_famous_graphs_trees_lists_problems"),
    ("famous-hard", "famous_hard", "build_famous_hard_problems"),
]

for tag, mod_name, func_name in famous_families:
    mod = __import__(f"algorithm_atlas.atlascode.families.{mod_name}", fromlist=[func_name])
    func = getattr(mod, func_name)
    t1 = time.time()
    probs, skips = func(registered, existing)
    t2 = time.time()
    existing |= {p[0]['id'] for p in probs}
    total = t2 - t1
    cum = t2 - t0
    print(f"{tag}: {total:.1f}s ({len(probs)}p, {len(skips)} skipped) [cum={cum:.1f}s]")
    sys.stdout.flush()

print(f"\nTotal: {time.time()-t0:.1f}s, all problems: {len(existing)}")
