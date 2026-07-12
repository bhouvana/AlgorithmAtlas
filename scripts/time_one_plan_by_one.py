"""Time each plan one at a time to find the slow one."""
import time, sys, loguru
loguru.logger.remove()
sys.path.insert(0, 'apps/backend')
import logging; logging.disable(logging.CRITICAL + 10)

from algorithm_atlas.atlascode.families.binary_search_variants_testdata import (
    _plan_rotated_search, _plan_bitonic, _plan_first_occurrence,
    _plan_last_occurrence, _plan_count_occurrences, _plan_search_insert,
    _plan_koko, _plan_ship, _plan_integer_sqrt, _plan_search_2d_matrix,
    _plan_find_min_rotated
)
from algorithm_atlas.atlascode import testgen as tg

plans = [
    ("rotated-search", _plan_rotated_search),
    ("bitonic", _plan_bitonic),
    ("first-occurrence", _plan_first_occurrence),
    ("last-occurrence", _plan_last_occurrence),
    ("count-occurrences", _plan_count_occurrences),
    ("search-insert", _plan_search_insert),
    ("koko", _plan_koko),
    ("ship", _plan_ship),
    ("integer-sqrt", _plan_integer_sqrt),
    ("search-2d-matrix", _plan_search_2d_matrix),
    ("find-min-rotated", _plan_find_min_rotated),
]

for name, fn in plans:
    sys.stdout.flush()
    t0 = time.time()
    rng = tg.problem_rng(name)
    try:
        plan = fn(rng)
        t1 = time.time()
        total = sum(len(plan.get(b, [])) for b in ["visible","basic","boundary","adversarial","mutation","stress"])
        print(f"OK {name}: {t1-t0:.3f}s total={total}", flush=True)
    except Exception as e:
        t1 = time.time()
        print(f"FAIL {name}: after {t1-t0:.1f}s: {e}", flush=True)
