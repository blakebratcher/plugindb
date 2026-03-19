"""Tests for plugin browse endpoints."""

from __future__ import annotations

import pytest


class TestListPlugins:
    def test_list_all(self, client):
        """GET /plugins returns all 3 seeded plugins."""
        resp = client.get("/api/v1/plugins")
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 3
        assert len(body["data"]) == 3

    def test_filter_by_category(self, client):
        """Filter by category=instrument returns 2 plugins (Serum, Diva)."""
        resp = client.get("/api/v1/plugins", params={"category": "instrument"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 2
        names = {p["name"] for p in body["data"]}
        assert names == {"Serum", "Diva"}

    def test_filter_by_category_effect(self, client):
        """Filter by category=effect returns 1 plugin (VintageVerb)."""
        resp = client.get("/api/v1/plugins", params={"category": "effect"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["name"] == "Valhalla VintageVerb"

    def test_filter_by_manufacturer(self, client):
        """Filter by manufacturer slug returns matching plugins."""
        resp = client.get("/api/v1/plugins", params={"manufacturer": "xfer-records"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["name"] == "Serum"

    def test_filter_by_format(self, client):
        """Filter by format does a LIKE match on the JSON formats column."""
        resp = client.get("/api/v1/plugins", params={"format": "VST2"})
        assert resp.status_code == 200
        body = resp.json()
        # Only Diva has VST2 in its formats
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["name"] == "Diva"

    def test_filter_by_price_type_free(self, client):
        """No seeded plugins are free, so price_type=free returns empty."""
        resp = client.get("/api/v1/plugins", params={"price_type": "free"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 0

    def test_pagination(self, client):
        """Pagination with per_page=1, page=2 returns the second plugin."""
        resp = client.get("/api/v1/plugins", params={"per_page": 1, "page": 2})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 3
        assert body["pagination"]["page"] == 2
        assert body["pagination"]["per_page"] == 1
        assert body["pagination"]["pages"] == 3
        assert len(body["data"]) == 1

    def test_per_page_clamped_to_max(self, client):
        """per_page > 200 is clamped to 200."""
        resp = client.get("/api/v1/plugins", params={"per_page": 999})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["per_page"] == 200

    def test_per_page_clamped_to_min(self, client):
        """per_page < 1 is clamped to 1."""
        resp = client.get("/api/v1/plugins", params={"per_page": 0})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["per_page"] == 1

    def test_invalid_page(self, client):
        """Page < 1 returns 400."""
        resp = client.get("/api/v1/plugins", params={"page": 0})
        assert resp.status_code == 400

    def test_page_beyond_total(self, client):
        """Page beyond total returns empty results but 200 OK."""
        resp = client.get("/api/v1/plugins", params={"page": 100})
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"] == []
        assert body["pagination"]["total"] == 3


class TestDawFilter:
    """DAW filter tests — the daw parameter should search the daws column."""

    def test_filter_by_daw_bitwig(self, client):
        """Filter ?daw=Bitwig returns plugins with Bitwig in their daws list."""
        resp = client.get("/api/v1/plugins", params={"daw": "Bitwig"})
        assert resp.status_code == 200
        body = resp.json()
        # Serum and Diva have Bitwig in daws; VintageVerb does not
        assert body["pagination"]["total"] == 2
        names = {p["name"] for p in body["data"]}
        assert names == {"Serum", "Diva"}

    def test_filter_by_daw_fl_studio(self, client):
        """Filter ?daw=FL Studio returns plugins with FL Studio in daws."""
        resp = client.get("/api/v1/plugins", params={"daw": "FL Studio"})
        assert resp.status_code == 200
        body = resp.json()
        # Serum and VintageVerb have FL Studio
        assert body["pagination"]["total"] == 2
        names = {p["name"] for p in body["data"]}
        assert names == {"Serum", "Valhalla VintageVerb"}

    def test_filter_by_daw_no_match(self, client):
        """Filter by a DAW that no plugin supports returns empty."""
        resp = client.get("/api/v1/plugins", params={"daw": "Pro Tools"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 0


class TestCombinedFilters:
    """Combined filter tests — multiple query parameters applied together."""

    def test_category_and_manufacturer(self, client):
        """category=instrument & manufacturer=xfer-records returns only Serum."""
        resp = client.get(
            "/api/v1/plugins",
            params={"category": "instrument", "manufacturer": "xfer-records"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["name"] == "Serum"

    def test_category_and_format(self, client):
        """category=instrument & format=VST2 returns only Diva."""
        resp = client.get(
            "/api/v1/plugins",
            params={"category": "instrument", "format": "VST2"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["name"] == "Diva"

    def test_category_and_daw(self, client):
        """category=effect & daw=FL Studio returns only VintageVerb."""
        resp = client.get(
            "/api/v1/plugins",
            params={"category": "effect", "daw": "FL Studio"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["name"] == "Valhalla VintageVerb"

    def test_no_match_combined(self, client):
        """Contradictory combined filters return empty results."""
        resp = client.get(
            "/api/v1/plugins",
            params={"category": "effect", "manufacturer": "xfer-records"},
        )
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 0


class TestGetPlugin:
    def test_get_by_id(self, client):
        """GET /plugins/{id} returns full plugin detail."""
        # First, list to get a valid ID
        list_resp = client.get("/api/v1/plugins")
        plugin_id = list_resp.json()["data"][0]["id"]

        resp = client.get(f"/api/v1/plugins/{plugin_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == plugin_id
        assert "manufacturer" in body
        assert "formats" in body
        assert "aliases" in body

    def test_not_found(self, client):
        """GET /plugins/99999 returns 404."""
        resp = client.get("/api/v1/plugins/99999")
        assert resp.status_code == 404
