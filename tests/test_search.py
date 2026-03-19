"""Tests for the /api/v1/search endpoint (FTS5 full-text search)."""

from __future__ import annotations


class TestSearch:
    """GET /api/v1/search?q=..."""

    def test_search_by_name(self, client):
        """Searching by plugin name returns matching results."""
        resp = client.get("/api/v1/search", params={"q": "Serum"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] >= 1
        names = [p["name"] for p in body["data"]]
        assert "Serum" in names

    def test_search_by_description(self, client):
        """Searching by a term in the description returns matching results."""
        resp = client.get("/api/v1/search", params={"q": "wavetable"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] >= 1
        names = [p["name"] for p in body["data"]]
        assert "Serum" in names

    def test_search_by_tag(self, client):
        """Searching by an alias (tag) returns matching results."""
        resp = client.get("/api/v1/search", params={"q": "SerumFX"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] >= 1
        names = [p["name"] for p in body["data"]]
        assert "Serum" in names

    def test_search_with_category_filter(self, client):
        """Filtering by category limits results to that category only."""
        # "Valhalla" matches VintageVerb (effect), not instruments
        resp = client.get("/api/v1/search", params={"q": "Valhalla", "category": "instrument"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 0
        assert body["data"] == []

    def test_search_category_filter_with_results(self, client):
        """Category filter returns results when category matches."""
        resp = client.get("/api/v1/search", params={"q": "Valhalla", "category": "effect"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] >= 1
        names = [p["name"] for p in body["data"]]
        assert "Valhalla VintageVerb" in names

    def test_query_too_short(self, client):
        """Query shorter than 2 characters returns 400."""
        resp = client.get("/api/v1/search", params={"q": "S"})
        assert resp.status_code == 400
        assert "at least 2 characters" in resp.json()["detail"]

    def test_missing_query(self, client):
        """Omitting the required q parameter returns 422."""
        resp = client.get("/api/v1/search")
        assert resp.status_code == 422

    def test_search_prefix_matching(self, client):
        """Prefix matching works — 'Ser' matches 'Serum'."""
        resp = client.get("/api/v1/search", params={"q": "Ser"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] >= 1
        names = [p["name"] for p in body["data"]]
        assert "Serum" in names

    def test_search_pagination(self, client):
        """Search results include pagination metadata."""
        resp = client.get("/api/v1/search", params={"q": "synth", "per_page": 1})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["per_page"] == 1
        assert body["pagination"]["page"] == 1
        assert len(body["data"]) <= 1

    def test_search_returns_full_plugin_detail(self, client):
        """Search results include full plugin objects with manufacturer and aliases."""
        resp = client.get("/api/v1/search", params={"q": "Serum"})
        assert resp.status_code == 200
        plugin = resp.json()["data"][0]
        assert "manufacturer" in plugin
        assert "aliases" in plugin
        assert "formats" in plugin
        assert plugin["manufacturer"]["name"] == "Xfer Records"
