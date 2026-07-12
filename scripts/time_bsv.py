"""Time just binary_search_variants import and build."""
import time, sys, loguru
loguru.logger.remove()
sys.path.insert(0, 'scripts')
sys.path.insert(0, 'apps/backend')
import logging; logging.disable(logging.CRITICAL + 10)

import seed_atlas_code as seed_mod
from algorithm_atlas.atlascode.discovery import discover_registered_algorithms
registered = discover_registered_algorithms()
curated_algorithm_slugs = {p[0]['algorithm_slug'] for p in seed_mod.PROBLEMS if p[0].get('algorithm_slug')}

# Time just the import
t0 = time.time()
from algorithm_atlas.atlascode.families.binary_search_variants import build_binary_search_variant_problems
t1 = time.time()
print(f"Import binary_search_variants: {t1-t0:.2f}s", flush=True)

# Now build with existing = curated only
existing = {p[0]['id'] for p in seed_mod.PROBLEMS}
print(f"Existing: {len(existing)}", flush=True)
t2 = time.time()
probs, skips = build_binary_search_variant_problems(registered, existing)
t3 = time.time()
print(f"Build BSV: {t3-t2:.2f}s, {len(probs)}p, {len(skips)} skipped", flush=True)
