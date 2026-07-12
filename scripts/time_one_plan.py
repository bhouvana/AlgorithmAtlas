"""Time just the rotated_search plan."""
import time, sys, loguru
loguru.logger.remove()
sys.path.insert(0, 'apps/backend')
import logging; logging.disable(logging.CRITICAL + 10)

from algorithm_atlas.atlascode.families.binary_search_variants_testdata import _plan_rotated_search
from algorithm_atlas.atlascode import testgen as tg

print("starting", flush=True)
t0 = time.time()
rng = tg.problem_rng("rotated-binary-search")
t1 = time.time()
print(f"rng: {t1-t0:.2f}s", flush=True)
plan = _plan_rotated_search(rng)
t2 = time.time()
print(f"plan: {t2-t1:.2f}s", flush=True)
counts = {b: len(plan.get(b, [])) for b in ["visible","basic","boundary","adversarial","mutation","stress"]}
print(f"  {counts}", flush=True)
