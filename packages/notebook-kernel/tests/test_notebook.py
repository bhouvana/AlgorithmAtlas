"""
Tests for the notebook kernel package.

Runs without Jupyter — only tests frame generation and HTML output.
"""
import json
import pathlib
import sys

# Ensure SDK, backend, and notebook-kernel package are findable from the test location
_ROOT = pathlib.Path(__file__).parents[3]
sys.path.insert(0, str(_ROOT / "packages" / "plugin-sdk" / "python"))
sys.path.insert(0, str(_ROOT / "apps" / "backend"))
sys.path.insert(0, str(_ROOT / "packages" / "notebook-kernel"))

from algorithm_atlas_notebook import run, AtlasDisplay


def test_run_returns_atlas_display():
    result = run("bubble-sort", seed=42, array_size=10)
    assert isinstance(result, AtlasDisplay)


def test_frames_are_non_empty():
    result = run("bubble-sort", seed=42, array_size=10)
    assert result.total_frames > 0


def test_frames_have_correct_structure():
    result = run("insertion-sort", seed=1, array_size=8)
    frame = result.frames[0]
    assert "frame_index" in frame
    assert "state" in frame
    assert "array" in frame["state"]
    assert len(frame["state"]["array"]) == 8


def test_repr_html_contains_canvas():
    result = run("selection-sort", seed=42, array_size=12)
    html = result._repr_html_()
    assert "<canvas" in html
    assert "FRAMES" in html  # embedded JSON


def test_repr_html_contains_frame_data():
    result = run("merge-sort", seed=10, array_size=8)
    html = result._repr_html_()
    data = json.loads(html.split("const FRAMES = ")[1].split(";\n")[0])
    assert len(data) == result.total_frames


def test_comparisons_and_swaps():
    result = run("bubble-sort", seed=42, array_size=10)
    assert result.comparisons >= 0
    assert result.swaps >= 0


def test_save_html(tmp_path):
    result = run("quick-sort", seed=42, array_size=15)
    out = result.save_html(tmp_path / "test.html")
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "<canvas" in content


def test_repr_json():
    result = run("bubble-sort", seed=42, array_size=6)
    data = result._repr_json_()
    assert data["slug"] == "bubble-sort"
    assert data["seed"] == 42
    assert len(data["frames"]) == result.total_frames


def test_multiple_algorithms():
    for slug in ["bubble-sort", "insertion-sort", "selection-sort", "merge-sort", "quick-sort"]:
        result = run(slug, seed=42, array_size=10)
        assert result.total_frames > 1, f"{slug} produced only {result.total_frames} frames"
