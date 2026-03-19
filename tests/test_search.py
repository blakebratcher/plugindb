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


class TestSearchFTS5SafetyNet:
    """Queries containing FTS5 special operators must not crash the server."""

    def test_fts5_operator_OR(self, client):
        """FTS5 operator 'OR' as raw input returns 200 or 400, never 500."""
        resp = client.get("/api/v1/search", params={"q": "OR"})
        assert resp.status_code in (200, 400)

    def test_fts5_operator_AND_NOT(self, client):
        """FTS5 operator 'AND NOT' as raw input returns 200 or 400, never 500."""
        resp = client.get("/api/v1/search", params={"q": "AND NOT"})
        assert resp.status_code in (200, 400)

    def test_fts5_operator_NEAR(self, client):
        """FTS5 NEAR operator as raw input does not crash."""
        resp = client.get("/api/v1/search", params={"q": "NEAR(a b)"})
        assert resp.status_code in (200, 400)

    def test_fts5_special_characters(self, client):
        """FTS5 special characters like quotes and brackets are handled."""
        resp = client.get("/api/v1/search", params={"q": '"test" {foo} [bar]'})
        assert resp.status_code in (200, 400)

    def test_fts5_asterisk_only(self, client):
        """A query of just '*' does not crash."""
        resp = client.get("/api/v1/search", params={"q": "**"})
        assert resp.status_code in (200, 400)

    def test_fts5_parentheses(self, client):
        """Unbalanced parentheses do not crash the search."""
        resp = client.get("/api/v1/search", params={"q": "synth(("})
        assert resp.status_code in (200, 400)


class TestSearchEmptyDatabase:
    """Search against a database with no plugins should return empty, not crash."""

    def test_search_empty_db(self):
        """Searching an empty DB returns zero results, not an error."""
        from fastapi.testclient import TestClient
        from plugindb.database import create_schema, get_connection
        from plugindb.main import create_app

        conn = get_connection(":memory:")
        create_schema(conn)
        # No seed data — database is empty
        app = create_app(db_connection=conn)
        with TestClient(app) as tc:
            resp = tc.get("/api/v1/search", params={"q": "anything"})
            assert resp.status_code == 200
            body = resp.json()
            assert body["pagination"]["total"] == 0
            assert body["data"] == []
        conn.close()
