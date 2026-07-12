"""Time each BSV plan individually."""
import time, sys, loguru, random
loguru.logger.remove()
sys.path.insert(0, 'apps/backend')
import logging; logging.disable(logging.CRITICAL + 10)

from algorithm_atlas.atlascode.families.binary_search_variants_testdata import BINARY_SEARCH_VARIANT_TEST_PLANS
from algorithm_atlas.atlascode import testgen as tg

for slug in sorted(BINARY_SEARCH_VARIANT_TEST_PLANS):
    t0 = time.time()
    to_input, fmt, plan_fn = BINARY_SEARCH_VARIANT_TEST_PLANS[slug]
    rng = tg.problem_rng(slug)
    try:
        plan = plan_fn(rng)
        t1 = time.time()
        counts = {b: len(plan.get(b, [])) for b in ["visible","basic","boundary","adversarial","mutation","stress"]}
        total = sum(counts.values())
        print(f"  {slug}: {t1-t0:.2f}s total={total} {counts}", flush=True)
    except Exception as e:
        t1 = time.time()
        print(f"  {slug}: ERROR after {t1-t0:.2f}s: {e}", flush=True)
