"""Backend REST API integration tests.

Uses a real plugin registry loaded from the filesystem.
All 40+ algorithm plugins must be discoverable for these tests to pass.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


# ─────────────────────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────────────────────

class TestHealth:
    def test_health_ok(self, client: TestClient):
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_status_field(self, client: TestClient):
        r = client.get("/health")
        assert r.json()["status"] == "ok"

    def test_health_has_version(self, client: TestClient):
        r = client.get("/health")
        assert "version" in r.json()

    def test_health_algorithms_loaded(self, client: TestClient):
        r = client.get("/health")
        assert r.json()["algorithms_loaded"] >= 40


# ─────────────────────────────────────────────────────────────────────────────
# Algorithm catalog
# ─────────────────────────────────────────────────────────────────────────────

class TestAlgorithmList:
    def test_list_returns_200(self, client: TestClient):
        r = client.get("/api/v1/algorithms")
        assert r.status_code == 200

    def test_list_returns_all_plugins(self, client: TestClient):
        r = client.get("/api/v1/algorithms")
        assert len(r.json()) >= 40

    def test_list_item_has_required_fields(self, client: TestClient):
        r = client.get("/api/v1/algorithms")
        item = r.json()[0]
        for field in ("slug", "name", "category", "visualization_type", "complexity", "tags", "description"):
            assert field in item, f"Missing field: {field}"

    def test_list_complexity_subfields(self, client: TestClient):
        r = client.get("/api/v1/algorithms")
        c = r.json()[0]["complexity"]
        for field in ("time_best", "time_average", "time_worst", "space"):
            assert field in c

    def test_filter_by_category_sorting(self, client: TestClient):
        r = client.get("/api/v1/algorithms", params={"category": "sorting"})
        assert r.status_code == 200
        items = r.json()
        assert len(items) >= 11
        assert all(a["category"] == "sorting" for a in items)

    def test_filter_by_category_searching(self, client: TestClient):
        r = client.get("/api/v1/algorithms", params={"category": "searching"})
        items = r.json()
        assert len(items) >= 7
        assert all(a["category"] == "searching" for a in items)

    def test_filter_by_category_graph(self, client: TestClient):
        r = client.get("/api/v1/algorithms", params={"category": "graph"})
        items = r.json()
        assert len(items) >= 8
        assert all(a["category"] == "graph" for a in items)

    def test_filter_by_category_empty(self, client: TestClient):
        r = client.get("/api/v1/algorithms", params={"category": "nonexistent"})
        assert r.status_code == 200
        assert r.json() == []

    def test_search_by_name(self, client: TestClient):
        r = client.get("/api/v1/algorithms", params={"search": "bubble"})
        slugs = [a["slug"] for a in r.json()]
        assert "bubble-sort" in slugs

    def test_search_by_tag(self, client: TestClient):
        r = client.get("/api/v1/algorithms", params={"search": "dijkstra"})
        assert r.status_code == 200
        # Should find Dijkstra by name
        slugs = [a["slug"] for a in r.json()]
        assert any("dijkstra" in s for s in slugs)

    def test_search_case_insensitive(self, client: TestClient):
        r = client.get("/api/v1/algorithms", params={"search": "QUICK"})
        slugs = [a["slug"] for a in r.json()]
        assert "quick-sort" in slugs

    def test_combined_category_and_search(self, client: TestClient):
        r = client.get("/api/v1/algorithms", params={"category": "sorting", "search": "merge"})
        items = r.json()
        assert len(items) >= 1
        assert all(a["category"] == "sorting" for a in items)

    @pytest.mark.parametrize("slug", [
        "bubble-sort", "quick-sort", "merge-sort", "heap-sort",
        "binary-search", "linear-search",
        "bfs", "dfs", "dijkstra", "bellman-ford",
        "longest-common-subsequence", "coin-change",
        "kmp", "a-star",
    ])
    def test_known_slugs_present(self, client: TestClient, slug: str):
        r = client.get("/api/v1/algorithms")
        slugs = [a["slug"] for a in r.json()]
        assert slug in slugs, f"Expected slug '{slug}' in algorithm list"


class TestCategories:
    def test_categories_returns_200(self, client: TestClient):
        r = client.get("/api/v1/algorithms/categories")
        assert r.status_code == 200

    def test_categories_has_expected(self, client: TestClient):
        r = client.get("/api/v1/algorithms/categories")
        slugs = {c["slug"] for c in r.json()}
        for cat in ("sorting", "searching", "graph", "dynamic-programming", "string"):
            assert cat in slugs, f"Expected category '{cat}'"

    def test_categories_have_counts(self, client: TestClient):
        r = client.get("/api/v1/algorithms/categories")
        for cat in r.json():
            assert cat["algorithm_count"] >= 1

    def test_sorting_count(self, client: TestClient):
        r = client.get("/api/v1/algorithms/categories")
        cat = next(c for c in r.json() if c["slug"] == "sorting")
        assert cat["algorithm_count"] >= 11

    def test_categories_sorted(self, client: TestClient):
        r = client.get("/api/v1/algorithms/categories")
        slugs = [c["slug"] for c in r.json()]
        assert slugs == sorted(slugs)


class TestAlgorithmDetail:
    def test_detail_returns_200(self, client: TestClient):
        r = client.get("/api/v1/algorithms/bubble-sort")
        assert r.status_code == 200

    def test_detail_has_all_fields(self, client: TestClient):
        r = client.get("/api/v1/algorithms/bubble-sort")
        data = r.json()
        for field in ("slug", "name", "category", "visualization_type",
                      "complexity", "tags", "description", "intuition",
                      "references", "default_params", "version", "benchmark_enabled"):
            assert field in data, f"Missing field: {field}"

    def test_detail_slug_matches(self, client: TestClient):
        r = client.get("/api/v1/algorithms/quick-sort")
        assert r.json()["slug"] == "quick-sort"

    def test_detail_has_intuition(self, client: TestClient):
        r = client.get("/api/v1/algorithms/dijkstra")
        assert len(r.json()["intuition"]) > 0

    def test_detail_not_found(self, client: TestClient):
        r = client.get("/api/v1/algorithms/does-not-exist")
        assert r.status_code == 404

    def test_detail_404_message(self, client: TestClient):
        r = client.get("/api/v1/algorithms/ghost-algo")
        assert "ghost-algo" in r.json()["detail"]

    @pytest.mark.parametrize("slug", [
        "bubble-sort", "merge-sort", "binary-search",
        "bfs", "dijkstra", "coin-change", "kmp",
    ])
    def test_detail_each_slug(self, client: TestClient, slug: str):
        r = client.get(f"/api/v1/algorithms/{slug}")
        assert r.status_code == 200
        assert r.json()["slug"] == slug


# ─────────────────────────────────────────────────────────────────────────────
# Simulations
# ─────────────────────────────────────────────────────────────────────────────

class TestSimulations:
    def test_create_returns_201(self, client: TestClient):
        r = client.post("/api/v1/simulations", json={"algorithm_slug": "bubble-sort"})
        assert r.status_code == 201

    def test_create_has_session_id(self, client: TestClient):
        r = client.post("/api/v1/simulations", json={"algorithm_slug": "bubble-sort"})
        assert "session_id" in r.json()
        assert len(r.json()["session_id"]) > 0

    def test_create_returns_slug(self, client: TestClient):
        r = client.post("/api/v1/simulations", json={"algorithm_slug": "merge-sort"})
        assert r.json()["algorithm_slug"] == "merge-sort"

    def test_create_has_status(self, client: TestClient):
        r = client.post("/api/v1/simulations", json={"algorithm_slug": "quick-sort"})
        assert r.json()["status"] == "paused"

    def test_create_with_seed(self, client: TestClient):
        r = client.post("/api/v1/simulations", json={"algorithm_slug": "bubble-sort", "seed": 99})
        assert r.status_code == 201
        assert r.json()["seed"] == 99

    def test_create_with_params(self, client: TestClient):
        r = client.post("/api/v1/simulations", json={
            "algorithm_slug": "bubble-sort",
            "params": {"array_size": 15},
        })
        assert r.status_code == 201

    def test_create_not_found(self, client: TestClient):
        r = client.post("/api/v1/simulations", json={"algorithm_slug": "nonexistent-algo"})
        assert r.status_code == 404

    def test_get_returns_200(self, client: TestClient):
        create = client.post("/api/v1/simulations", json={"algorithm_slug": "bubble-sort"})
        sid = create.json()["session_id"]
        r = client.get(f"/api/v1/simulations/{sid}")
        assert r.status_code == 200

    def test_get_returns_status(self, client: TestClient):
        create = client.post("/api/v1/simulations", json={"algorithm_slug": "bubble-sort"})
        sid = create.json()["session_id"]
        r = client.get(f"/api/v1/simulations/{sid}")
        data = r.json()
        assert data["status"] == "paused"
        assert data["current_frame"] == 0

    def test_get_not_found(self, client: TestClient):
        r = client.get("/api/v1/simulations/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404

    def test_delete_returns_204(self, client: TestClient):
        create = client.post("/api/v1/simulations", json={"algorithm_slug": "bubble-sort"})
        sid = create.json()["session_id"]
        r = client.delete(f"/api/v1/simulations/{sid}")
        assert r.status_code == 204

    def test_delete_makes_gone(self, client: TestClient):
        create = client.post("/api/v1/simulations", json={"algorithm_slug": "bubble-sort"})
        sid = create.json()["session_id"]
        client.delete(f"/api/v1/simulations/{sid}")
        r = client.get(f"/api/v1/simulations/{sid}")
        assert r.status_code == 404

    def test_delete_not_found(self, client: TestClient):
        r = client.delete("/api/v1/simulations/00000000-0000-0000-0000-000000000001")
        assert r.status_code == 404

    @pytest.mark.parametrize("slug", [
        "bfs", "dijkstra", "kmp", "coin-change", "a-star",
        "inorder-traversal", "sieve-of-eratosthenes",
    ])
    def test_create_various_algorithms(self, client: TestClient, slug: str):
        r = client.post("/api/v1/simulations", json={"algorithm_slug": slug})
        assert r.status_code == 201, f"Failed to create simulation for {slug}: {r.text}"


# ─────────────────────────────────────────────────────────────────────────────
# Benchmarks
# ─────────────────────────────────────────────────────────────────────────────

class TestBenchmarks:
    def test_benchmark_returns_200(self, client: TestClient):
        r = client.post("/api/v1/benchmarks", json={
            "algorithm_slug": "bubble-sort",
            "sizes": [10, 20],
            "trials": 1,
        })
        assert r.status_code == 200

    def test_benchmark_has_slug(self, client: TestClient):
        r = client.post("/api/v1/benchmarks", json={
            "algorithm_slug": "merge-sort",
            "sizes": [10],
            "trials": 1,
        })
        assert r.json()["slug"] == "merge-sort"

    def test_benchmark_has_size_param(self, client: TestClient):
        r = client.post("/api/v1/benchmarks", json={
            "algorithm_slug": "bubble-sort",
            "sizes": [10],
            "trials": 1,
        })
        assert "size_param" in r.json()

    def test_benchmark_results_count(self, client: TestClient):
        r = client.post("/api/v1/benchmarks", json={
            "algorithm_slug": "insertion-sort",
            "sizes": [10, 20, 30],
            "trials": 1,
        })
        assert len(r.json()["results"]) == 3

    def test_benchmark_result_fields(self, client: TestClient):
        r = client.post("/api/v1/benchmarks", json={
            "algorithm_slug": "quick-sort",
            "sizes": [10],
            "trials": 1,
        })
        result = r.json()["results"][0]
        for field in ("input_size", "frame_count", "init_ms", "steps_ms", "total_ms"):
            assert field in result, f"Missing result field: {field}"

    def test_benchmark_sizes_match(self, client: TestClient):
        sizes = [5, 15, 50]
        r = client.post("/api/v1/benchmarks", json={
            "algorithm_slug": "selection-sort",
            "sizes": sizes,
            "trials": 1,
        })
        returned = [res["input_size"] for res in r.json()["results"]]
        assert returned == sizes

    def test_benchmark_frame_count_positive(self, client: TestClient):
        r = client.post("/api/v1/benchmarks", json={
            "algorithm_slug": "bubble-sort",
            "sizes": [10],
            "trials": 1,
        })
        assert r.json()["results"][0]["frame_count"] > 0

    def test_benchmark_timings_non_negative(self, client: TestClient):
        r = client.post("/api/v1/benchmarks", json={
            "algorithm_slug": "bubble-sort",
            "sizes": [10],
            "trials": 2,
        })
        res = r.json()["results"][0]
        assert res["init_ms"] >= 0
        assert res["steps_ms"] >= 0
        assert res["total_ms"] >= 0

    def test_benchmark_not_found(self, client: TestClient):
        r = client.post("/api/v1/benchmarks", json={
            "algorithm_slug": "does-not-exist",
            "sizes": [10],
        })
        assert r.status_code == 404

    def test_benchmark_custom_size_param(self, client: TestClient):
        r = client.post("/api/v1/benchmarks", json={
            "algorithm_slug": "bfs",
            "sizes": [5, 10],
            "size_param": "node_count",
            "trials": 1,
        })
        assert r.status_code == 200
        assert r.json()["size_param"] == "node_count"

    def test_benchmark_default_sizes(self, client: TestClient):
        r = client.post("/api/v1/benchmarks", json={
            "algorithm_slug": "binary-search",
        })
        assert r.status_code == 200
        # Default sizes are [10, 25, 50, 100, 200]
        assert len(r.json()["results"]) == 5
