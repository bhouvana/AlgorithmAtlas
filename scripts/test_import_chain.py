"""Test import chain to find the hang."""
import time, sys, loguru
loguru.logger.remove()
sys.path.insert(0, 'apps/backend')
import logging; logging.disable(logging.CRITICAL + 10)

t0 = time.time()
print("Importing independent_oracles...", flush=True)
from algorithm_atlas.atlascode import independent_oracles as oracles
t1 = time.time()
print(f"  independent_oracles: {t1-t0:.2f}s", flush=True)

print("Importing testgen...", flush=True)
from algorithm_atlas.atlascode import testgen as tg
t2 = time.time()
print(f"  testgen: {t2-t1:.2f}s", flush=True)

print("Importing binary_search_variants...", flush=True)
from algorithm_atlas.atlascode.families.binary_search_variants import _SPECS
t3 = time.time()
print(f"  binary_search_variants: {t3-t2:.2f}s ({len(_SPECS)} specs)", flush=True)

print("Importing testdata...", flush=True)
from algorithm_atlas.atlascode.families.binary_search_variants_testdata import BINARY_SEARCH_VARIANT_TEST_PLANS
t4 = time.time()
print(f"  testdata: {t4-t3:.2f}s ({len(BINARY_SEARCH_VARIANT_TEST_PLANS)} plans)", flush=True)
