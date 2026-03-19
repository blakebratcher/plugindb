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

    def test_stats_includes_tags_breakdown(self, client):
        """Stats include a tags dict with correct counts."""
        resp = client.get("/api/v1/stats")
        body = resp.json()
        assert "tags" in body
        assert isinstance(body["tags"], dict)
        # "synthesizer" appears in Serum and Diva tags
        assert body["tags"]["synthesizer"] == 2

    def test_stats_includes_price_types(self, client):
        """Stats include a price_types dict with correct counts."""
        resp = client.get("/api/v1/stats")
        body = resp.json()
        assert "price_types" in body
        assert isinstance(body["price_types"], dict)
        assert body["price_types"]["paid"] == 2
        assert body["price_types"]["free"] == 1


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


class TestTags:
    """GET /api/v1/tags"""

    def test_tags_returns_all_tags(self, client):
        """Tags endpoint returns all distinct tags with counts."""
        resp = client.get("/api/v1/tags")
        assert resp.status_code == 200
        body = resp.json()
        assert "tags" in body
        assert "total" in body
        assert body["tags"]["synthesizer"] == 2
        assert body["tags"]["vintage"] == 2
        assert body["tags"]["wavetable"] == 1
        assert body["total"] == 7  # 7 distinct tags across 3 plugins

    def test_tags_sorted_by_frequency(self, client):
        """Tags are sorted by frequency descending."""
        resp = client.get("/api/v1/tags")
        body = resp.json()
        counts = list(body["tags"].values())
        assert counts == sorted(counts, reverse=True)


class TestFormats:
    """GET /api/v1/formats"""

    def test_formats_returns_all(self, client):
        resp = client.get("/api/v1/formats")
        assert resp.status_code == 200
        body = resp.json()
        assert "VST3" in body["formats"]
        assert body["formats"]["VST3"] == 3

    def test_formats_total(self, client):
        resp = client.get("/api/v1/formats")
        body = resp.json()
        assert body["total"] == len(body["formats"])

    def test_formats_sorted_by_frequency(self, client):
        resp = client.get("/api/v1/formats")
        counts = list(resp.json()["formats"].values())
        assert counts == sorted(counts, reverse=True)


class TestHealth:
    """GET /health and GET /api/v1/health"""

    def test_health_returns_ok(self, client):
        """Root health check returns ok status."""
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        from plugindb import __version__
        assert body["version"] == __version__
        assert body["database"] == "connected"

    def test_health_at_api_prefix(self, client):
        """Health check is also available under /api/v1."""
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"


class TestCORS:
    """CORS middleware tests."""

    def test_cors_allows_any_origin(self, client):
        """Responses include Access-Control-Allow-Origin: *."""
        resp = client.get("/health", headers={"Origin": "https://example.com"})
        assert resp.status_code == 200
        assert resp.headers.get("access-control-allow-origin") == "*"

    def test_cors_preflight(self, client):
        """OPTIONS preflight returns correct CORS headers."""
        resp = client.options(
            "/api/v1/plugins",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.status_code == 200
        assert resp.headers.get("access-control-allow-origin") == "*"


class TestOpenAPI:
    """OpenAPI schema tests."""

    def test_openapi_schema_accessible(self, client):
        """GET /openapi.json returns valid schema with tag descriptions."""
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert "openapi" in schema
        assert "paths" in schema
        tag_names = [t["name"] for t in schema.get("tags", [])]
        assert "lookup" in tag_names
        assert "search" in tag_names
        assert "plugins" in tag_names


class TestOSEndpoint:
    """GET /api/v1/os"""

    def test_os_returns_all(self, client):
        resp = client.get("/api/v1/os")
        assert resp.status_code == 200
        body = resp.json()
        assert "windows" in body["os"]
        assert body["os"]["windows"] == 3
        assert body["os"]["macos"] == 3
        assert body["os"]["linux"] == 1

    def test_os_total(self, client):
        resp = client.get("/api/v1/os")
        assert resp.json()["total"] == 3  # windows, macos, linux

    def test_os_sorted_by_frequency(self, client):
        resp = client.get("/api/v1/os")
        counts = list(resp.json()["os"].values())
        assert counts == sorted(counts, reverse=True)


class TestSubcategoriesEndpoint:
    """GET /api/v1/subcategories"""

    def test_subcategories_returns_structure(self, client):
        resp = client.get("/api/v1/subcategories")
        assert resp.status_code == 200
        body = resp.json()
        assert "instrument" in body["subcategories"]
        assert "effect" in body["subcategories"]

    def test_subcategories_counts(self, client):
        resp = client.get("/api/v1/subcategories")
        body = resp.json()
        assert body["subcategories"]["instrument"]["synth"] == 2
        assert body["subcategories"]["effect"]["reverb"] == 1


class TestStatsOS:
    """Verify OS breakdown in /stats."""

    def test_stats_includes_os(self, client):
        resp = client.get("/api/v1/stats")
        body = resp.json()
        assert "os" in body
        assert body["os"]["windows"] == 3
        assert body["os"]["linux"] == 1


class TestRootEndpoint:
    """GET / returns API info."""

    def test_root_returns_info(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "PluginDB"
        assert "version" in body
        assert "data_version" in body
        assert body["api_versions"][0]["version"] == "v1"
        assert body["docs"] == "/docs"


class TestCaching:
    """ETag and caching headers."""

    def test_response_has_etag(self, client):
        resp = client.get("/api/v1/plugins")
        assert "etag" in resp.headers

    def test_response_has_cache_control(self, client):
        resp = client.get("/api/v1/plugins")
        assert "cache-control" in resp.headers
        assert "public" in resp.headers["cache-control"]

    def test_conditional_304(self, client):
        """If-None-Match with matching ETag returns 304."""
        resp1 = client.get("/api/v1/plugins")
        etag = resp1.headers["etag"]
        resp2 = client.get("/api/v1/plugins", headers={"If-None-Match": etag})
        assert resp2.status_code == 304

    def test_mismatched_etag_returns_200(self, client):
        """If-None-Match with wrong ETag returns 200."""
        resp = client.get("/api/v1/plugins", headers={"If-None-Match": '"wrong"'})
        assert resp.status_code == 200


class TestTimingHeaders:
    """X-Processing-Time-Ms header."""

    def test_timing_header_present(self, client):
        resp = client.get("/api/v1/plugins")
        assert "x-processing-time-ms" in resp.headers
        assert float(resp.headers["x-processing-time-ms"]) >= 0


class TestExport:
    """GET /api/v1/export"""

    def test_export_json(self, client):
        resp = client.get("/api/v1/export")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_export_csv(self, client):
        resp = client.get("/api/v1/export", params={"format": "csv"})
        assert resp.status_code == 200
        assert "text/csv" in resp.headers.get("content-type", "")
        lines = resp.text.strip().split("\n")
        assert len(lines) == 4  # header + 3 plugins

    def test_export_content_disposition(self, client):
        resp = client.get("/api/v1/export")
        assert "content-disposition" in resp.headers


class TestYearsEndpoint:
    """GET /api/v1/years"""

    def test_years_returns_counts(self, client):
        resp = client.get("/api/v1/years")
        assert resp.status_code == 200
        body = resp.json()
        assert 2014 in body["years"] or "2014" in body["years"]
        assert body["total"] == 3  # 3 distinct years

    def test_years_sorted_chronologically(self, client):
        resp = client.get("/api/v1/years")
        years = list(resp.json()["years"].keys())
        assert years == sorted(years)


class TestEnrichedHealth:
    """Enriched health endpoint fields."""

    def test_health_includes_counts(self, client):
        resp = client.get("/health")
        body = resp.json()
        assert "plugin_count" in body
        assert body["plugin_count"] == 3
        assert body["manufacturer_count"] == 3

    def test_health_includes_data_version(self, client):
        resp = client.get("/health")
        body = resp.json()
        assert "data_version" in body
        assert isinstance(body["data_version"], str)

    def test_health_includes_uptime(self, client):
        resp = client.get("/health")
        body = resp.json()
        assert "uptime_seconds" in body
        assert body["uptime_seconds"] >= 0


class TestSearchAnalytics:
    """GET /api/v1/search-analytics"""

    def test_analytics_returns_structure(self, client):
        # Trigger a search first to generate log data
        client.get("/api/v1/search", params={"q": "reverb"})
        resp = client.get("/api/v1/search-analytics")
        assert resp.status_code == 200
        body = resp.json()
        assert "total_searches" in body
        assert "top_queries" in body
        assert "zero_result_queries" in body
        assert body["total_searches"] >= 1

    def test_analytics_logs_search(self, client):
        """Search queries are logged and appear in analytics."""
        client.get("/api/v1/search", params={"q": "test_unique_query_xyz"})
        resp = client.get("/api/v1/search-analytics")
        queries = [q["query"] for q in resp.json()["top_queries"]]
        assert "test_unique_query_xyz" in queries

    def test_analytics_tracks_zero_results(self, client):
        """Zero-result searches are tracked separately."""
        client.get("/api/v1/search", params={"q": "zznonexistent"})
        resp = client.get("/api/v1/search-analytics")
        zero_queries = [q["query"] for q in resp.json()["zero_result_queries"]]
        assert "zznonexistent" in zero_queries


class TestSecurityHeaders:
    """Security headers on all responses."""

    def test_nosniff(self, client):
        resp = client.get("/api/v1/plugins")
        assert resp.headers.get("x-content-type-options") == "nosniff"

    def test_frame_deny(self, client):
        resp = client.get("/api/v1/plugins")
        assert resp.headers.get("x-frame-options") == "DENY"

    def test_referrer_policy(self, client):
        resp = client.get("/api/v1/plugins")
        assert "strict-origin" in resp.headers.get("referrer-policy", "")


class TestResponseCaching:
    """Meta endpoint caching."""

    def test_cached_stats_same_result(self, client):
        """Two calls to /stats return identical results."""
        r1 = client.get("/api/v1/stats").json()
        r2 = client.get("/api/v1/stats").json()
        assert r1 == r2

    def test_cached_formats_same_result(self, client):
        r1 = client.get("/api/v1/formats").json()
        r2 = client.get("/api/v1/formats").json()
        assert r1 == r2


class TestVersionEndpoint:
    """GET /api/v1/version"""

    def test_version_returns_info(self, client):
        resp = client.get("/api/v1/version")
        assert resp.status_code == 200
        body = resp.json()
        assert "api_version" in body
        assert "data_version" in body
        assert "data_updated_at" in body

    def test_version_data_version_is_string(self, client):
        resp = client.get("/api/v1/version")
        body = resp.json()
        assert isinstance(body["data_version"], str)
        assert len(body["data_version"]) == 12  # truncated SHA256


class TestExportEdgeCases:
    """Edge cases for export."""

    def test_export_invalid_format_defaults_json(self, client):
        """Invalid format parameter still returns JSON."""
        resp = client.get("/api/v1/export", params={"format": "xml"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
