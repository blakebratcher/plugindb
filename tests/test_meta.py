"""Tests for meta endpoints — stats, categories, and health."""

from __future__ import annotations


class TestStats:
    """GET /api/v1/stats"""

    def test_stats_returns_correct_counts(self, client):
        """Stats endpoint returns correct totals for seeded data."""
        resp = client.get("/api/v1/stats")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_plugins"] == 3
        assert body["total_manufacturers"] == 3
        # Serum: 3 + Diva: 2 + VintageVerb: 3 = 8
        assert body["total_aliases"] == 8

    def test_stats_includes_categories(self, client):
        """Stats include a category breakdown."""
        resp = client.get("/api/v1/stats")
        body = resp.json()
        assert "instrument" in body["categories"]
        assert body["categories"]["instrument"] == 2
        assert body["categories"]["effect"] == 1

    def test_stats_includes_formats(self, client):
        """Stats include a format breakdown."""
        resp = client.get("/api/v1/stats")
        body = resp.json()
        assert "VST3" in body["formats"]
        # All 3 plugins have VST3
        assert body["formats"]["VST3"] == 3

    def test_stats_includes_top_manufacturers(self, client):
        """Stats include top manufacturers with plugin counts."""
        resp = client.get("/api/v1/stats")
        body = resp.json()
        assert len(body["top_manufacturers"]) == 3
        # Each manufacturer has 1 plugin in test data
        for mfr in body["top_manufacturers"]:
            assert "name" in mfr
            assert "plugin_count" in mfr


class TestCategories:
    """GET /api/v1/categories"""

    def test_categories_returns_taxonomy(self, client):
        """Categories endpoint returns the full taxonomy."""
        resp = client.get("/api/v1/categories")
        assert resp.status_code == 200
        body = resp.json()
        assert "instrument" in body["categories"]
        assert "effect" in body["categories"]
        assert "container" in body["categories"]
        assert "note-effect" in body["categories"]
        assert "utility" in body["categories"]
        assert "midi" in body["categories"]

    def test_categories_includes_subcategories(self, client):
        """Taxonomy includes subcategory lists for each category."""
        resp = client.get("/api/v1/categories")
        body = resp.json()
        assert "synth" in body["subcategories"]["instrument"]
        assert "reverb" in body["subcategories"]["effect"]
        assert "eq" in body["subcategories"]["effect"]
        assert "arpeggiator" in body["subcategories"]["note-effect"]


class TestHealth:
    """GET /health and GET /api/v1/health"""

    def test_health_returns_ok(self, client):
        """Root health check returns ok status."""
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["version"] == "1.0.0"
        assert body["database"] == "connected"

    def test_health_at_api_prefix(self, client):
        """Health check is also available under /api/v1."""
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
