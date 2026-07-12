"""Time build_forty for each BSV problem to find the slow one."""
import time, sys, loguru
loguru.logger.remove()
sys.path.insert(0, 'apps/backend')
import logging; logging.disable(logging.CRITICAL + 10)

from algorithm_atlas.atlascode.families.binary_search_variants import _SPECS
from algorithm_atlas.atlascode.families.binary_search_variants_testdata import BINARY_SEARCH_VARIANT_TEST_PLANS
from algorithm_atlas.atlascode import testgen as tg

for slug in sorted(BINARY_SEARCH_VARIANT_TEST_PLANS):
    spec = _SPECS.get(slug)
    if spec is None:
        print(f"SKIP {slug}: no _SPECS entry")
        continue
    t0 = time.time()
    to_input, fmt, plan_fn = BINARY_SEARCH_VARIANT_TEST_PLANS[slug]
    rng = tg.problem_rng(slug)
    case_plan = plan_fn(rng)
    t1 = time.time()
    print(f"  {slug} plan: {t1-t0:.3f}s", flush=True)
    try:
        test_spec = tg.TestSpec(oracle=spec.oracle, to_input=to_input, format_output=fmt)
        test_cases = tg.build_forty(slug, test_spec, case_plan)
        t2 = time.time()
        print(f"  {slug} build_forty: {t2-t1:.3f}s ({len(test_cases)} cases)", flush=True)
    except Exception as e:
        t2 = time.time()
        print(f"  {slug} ERROR after {t2-t1:.1f}s: {e}", flush=True)
