"""Time each plan in binary_search_variants_testdata to find the slow one."""
import time
import loguru; loguru.logger.remove()
import sys; sys.path.insert(0, 'apps/backend')
import logging; logging.disable(logging.CRITICAL + 10)

from algorithm_atlas.atlascode.families.binary_search_variants_testdata import BINARY_SEARCH_VARIANT_TEST_PLANS
from algorithm_atlas.atlascode import testgen as tg

for slug in sorted(BINARY_SEARCH_VARIANT_TEST_PLANS):
    t0 = time.time()
    to_input, fmt, plan_fn = BINARY_SEARCH_VARIANT_TEST_PLANS[slug]
    rng = tg.problem_rng(slug)
    plan = plan_fn(rng)
    t1 = time.time()
    print(f"  {slug}: {t1-t0:.2f}s, visible={len(plan.get('visible',[]))}, basic={len(plan.get('basic',[]))}")
    sys.stdout.flush()
