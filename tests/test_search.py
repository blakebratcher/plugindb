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

    def test_search_by_tag_fts(self, client):
        """Searching by a tag term via FTS matches the correct plugin."""
        resp = client.get("/api/v1/search", params={"q": "wavetable"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] >= 1
        names = [p["name"] for p in body["data"]]
        assert "Serum" in names

    def test_search_with_tag_filter(self, client):
        """q=synth with tag=vintage returns only Diva (not Serum)."""
        resp = client.get("/api/v1/search", params={"q": "synth", "tag": "vintage"})
        assert resp.status_code == 200
        body = resp.json()
        names = [p["name"] for p in body["data"]]
        assert "Diva" in names
        assert "Serum" not in names

    def test_search_with_year_filter(self, client):
        """q=synth with year=2014 returns only Serum."""
        resp = client.get("/api/v1/search", params={"q": "synth", "year": 2014})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] >= 1
        names = [p["name"] for p in body["data"]]
        assert "Serum" in names
        assert "Diva" not in names


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


class TestSearchAdvancedFilters:
    """Tests for manufacturer, price_type, year_min/max, format, daw on /search."""

    def test_search_with_manufacturer_filter(self, client):
        """q=synth&manufacturer=xfer-records returns only Serum."""
        resp = client.get("/api/v1/search", params={"q": "synth", "manufacturer": "xfer-records"})
        assert resp.status_code == 200
        names = [p["name"] for p in resp.json()["data"]]
        assert "Serum" in names
        assert "Diva" not in names

    def test_search_with_price_type(self, client):
        """q=vintage&price_type=free returns VintageVerb."""
        resp = client.get("/api/v1/search", params={"q": "vintage", "price_type": "free"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] >= 1
        assert any(p["name"] == "Valhalla VintageVerb" for p in body["data"])

    def test_search_year_min(self, client):
        """q=synth&year_min=2013 returns only Serum."""
        resp = client.get("/api/v1/search", params={"q": "synth", "year_min": 2013})
        assert resp.status_code == 200
        names = [p["name"] for p in resp.json()["data"]]
        assert "Serum" in names
        assert "Diva" not in names

    def test_search_year_range(self, client):
        """q=synth&year_min=2011&year_max=2014 returns both synths."""
        resp = client.get("/api/v1/search", params={"q": "synth", "year_min": 2011, "year_max": 2014})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 2

    def test_search_with_format_filter(self, client):
        """q=synth&format=VST2 returns only Diva."""
        resp = client.get("/api/v1/search", params={"q": "synth", "format": "VST2"})
        assert resp.status_code == 200
        names = [p["name"] for p in resp.json()["data"]]
        assert names == ["Diva"]

    def test_search_with_daw_filter(self, client):
        """q=synth&daw=Reaper returns only Diva."""
        resp = client.get("/api/v1/search", params={"q": "synth", "daw": "Reaper"})
        assert resp.status_code == 200
        names = [p["name"] for p in resp.json()["data"]]
        assert names == ["Diva"]

    def test_search_with_subcategory_filter(self, client):
        """q=synth&subcategory=synth returns results, q=synth&subcategory=reverb returns 0."""
        resp = client.get("/api/v1/search", params={"q": "synth", "subcategory": "synth"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 2

        resp2 = client.get("/api/v1/search", params={"q": "synth", "subcategory": "reverb"})
        assert resp2.status_code == 200
        assert resp2.json()["pagination"]["total"] == 0

    def test_search_with_os_filter(self, client):
        """q=synth&os=linux returns only Diva."""
        resp = client.get("/api/v1/search", params={"q": "synth", "os": "linux"})
        assert resp.status_code == 200
        names = [p["name"] for p in resp.json()["data"]]
        assert names == ["Diva"]


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


class TestSuggest:
    """GET /api/v1/suggest"""

    def test_suggest_returns_names(self, client):
        resp = client.get("/api/v1/suggest", params={"q": "Ser"})
        assert resp.status_code == 200
        body = resp.json()
        assert "Serum" in body["suggestions"]
        assert body["query"] == "Ser"

    def test_suggest_single_char_accepted(self, client):
        """Unlike search, suggest accepts 1 character."""
        resp = client.get("/api/v1/suggest", params={"q": "D"})
        assert resp.status_code == 200

    def test_suggest_no_match(self, client):
        resp = client.get("/api/v1/suggest", params={"q": "zzzzz"})
        assert resp.status_code == 200
        assert resp.json()["suggestions"] == []


class TestSuggestEdgeCases:
    """Edge cases for /suggest endpoint."""

    def test_suggest_with_fts_special_chars(self, client):
        """Special characters don't crash suggest."""
        resp = client.get("/api/v1/suggest", params={"q": "Serum*"})
        assert resp.status_code == 200

    def test_suggest_with_long_query(self, client):
        """Very long query doesn't crash."""
        resp = client.get("/api/v1/suggest", params={"q": "a" * 200})
        assert resp.status_code == 200

    def test_suggest_returns_max_10(self, client):
        """Suggest never returns more than 10 results."""
        resp = client.get("/api/v1/suggest", params={"q": "a"})
        assert resp.status_code == 200
        assert len(resp.json()["suggestions"]) <= 10


class TestSearchSorting:
    """Sort and order params on /search."""

    def test_search_sort_by_name(self, client):
        resp = client.get("/api/v1/search", params={"q": "synth", "sort": "name", "order": "asc"})
        assert resp.status_code == 200
        names = [p["name"] for p in resp.json()["data"]]
        assert names == sorted(names)

    def test_search_sort_by_year_desc(self, client):
        resp = client.get("/api/v1/search", params={"q": "synth", "sort": "year", "order": "desc"})
        assert resp.status_code == 200
        years = [p["year"] for p in resp.json()["data"]]
        assert years == sorted(years, reverse=True)

    def test_search_default_sort_is_relevance(self, client):
        """Without sort param, results are ordered by relevance (no crash)."""
        resp = client.get("/api/v1/search", params={"q": "synth"})
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1


class TestEnhancedSuggest:
    """Enhanced suggest with rich results."""

    def test_suggest_results_field(self, client):
        resp = client.get("/api/v1/suggest", params={"q": "Ser"})
        assert resp.status_code == 200
        body = resp.json()
        assert "results" in body
        assert len(body["results"]) >= 1
        item = body["results"][0]
        assert "name" in item
        assert "slug" in item
        assert "category" in item
        assert "manufacturer_name" in item

    def test_suggest_manufacturer_name_correct(self, client):
        resp = client.get("/api/v1/suggest", params={"q": "Ser"})
        body = resp.json()
        serum = next((r for r in body["results"] if r["name"] == "Serum"), None)
        assert serum is not None
        assert serum["manufacturer_name"] == "Xfer Records"

    def test_suggest_backward_compatible(self, client):
        """suggestions list still present alongside results."""
        resp = client.get("/api/v1/suggest", params={"q": "Ser"})
        body = resp.json()
        assert "suggestions" in body
        assert "Serum" in body["suggestions"]


class TestSearchEdgeCases:
    """Edge cases for search endpoint."""

    def test_search_all_filters_combined(self, client):
        resp = client.get("/api/v1/search", params={
            "q": "synth",
            "category": "instrument",
            "subcategory": "synth",
            "manufacturer": "xfer-records",
            "year": 2014,
            "price_type": "paid",
            "sort": "name",
        })
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 1

    def test_search_unicode_query(self, client):
        """Unicode search query doesn't crash."""
        resp = client.get("/api/v1/search", params={"q": "réverb"})
        assert resp.status_code in (200, 400)
