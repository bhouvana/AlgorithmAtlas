"""Tests for Polynomial Multiplication (FFT) algorithm."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "polynomial_multiplication", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

PolynomialMultiplicationSimulation = _mod.PolynomialMultiplicationSimulation
_POLY_PAIRS = _mod._POLY_PAIRS
_poly_mul = _mod._poly_mul
_naive_mul = _mod._naive_mul
_fft = _mod._fft


def _make_plugin(seed=0):
    plugin = PolynomialMultiplicationSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def test_metadata_slug():
    plugin, _ = _make_plugin()
    assert plugin.metadata().slug == "polynomial-multiplication"


def test_metadata_category():
    plugin, _ = _make_plugin()
    assert plugin.metadata().category == "divide-and-conquer"


def test_metadata_visualization():
    plugin, _ = _make_plugin()
    assert plugin.metadata().visualization_type == "ARRAY_BARS"


def test_fft_correctness():
    # FFT of [1, 0, 0, 0] should be [1, 1, 1, 1]
    result = _fft([1, 0, 0, 0])
    for v in result:
        assert abs(v - 1) < 1e-9


def test_poly_mul_matches_naive():
    for a, b in _POLY_PAIRS:
        fft_result = _poly_mul(a, b)
        naive_result = _naive_mul(a, b)
        assert fft_result == naive_result, f"FFT {fft_result} != naive {naive_result} for {a}*{b}"


def test_poly_mul_simple():
    # (1+x)(1+x) = 1+2x+x^2
    result = _poly_mul([1, 1], [1, 1])
    assert result == [1, 2, 1]


def test_poly_mul_degree():
    a = [1, 2, 3]
    b = [4, 5]
    result = _poly_mul(a, b)
    assert len(result) == len(a) + len(b) - 1


def test_initialize_returns_sort_state():
    from algorithm_atlas_sdk import SortState
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert isinstance(state, SortState)


def test_initialize_description_contains_polys():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert "A=[" in state.description
    assert "B=[" in state.description


def test_steps_yields_four_steps():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    all_steps = list(plugin.steps(state))
    assert len(all_steps) == 4


def test_steps_final_array_positive():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    all_steps = list(plugin.steps(state))
    last = all_steps[-1]
    for v in last.array:
        assert 1 <= v <= 99


def test_steps_all_seeds():
    plugin, _ = _make_plugin()
    for seed in range(len(_POLY_PAIRS)):
        class P:
            pass
        P.seed = seed
        P.inputs = {}
        state = plugin.initialize(P())
        steps = list(plugin.steps(state))
        assert len(steps) == 4
        # Check description of last step mentions verification
        assert "verified" in steps[-1].description.lower() or "coefficients" in steps[-1].description.lower()
