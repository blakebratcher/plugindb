"""Tests for manufacturer browse endpoints."""

from __future__ import annotations

import pytest


class TestListManufacturers:
    def test_list_all(self, client):
        """GET /manufacturers returns all 3 seeded manufacturers."""
        resp = client.get("/api/v1/manufacturers")
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 3
        assert len(body["data"]) == 3

    def test_pagination(self, client):
        """Pagination works for manufacturers."""
        resp = client.get("/api/v1/manufacturers", params={"per_page": 1, "page": 1})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 3
        assert body["pagination"]["pages"] == 3
        assert len(body["data"]) == 1


class TestManufacturerSearch:
    def test_search_by_name(self, client):
        """search=xfer returns Xfer Records."""
        resp = client.get("/api/v1/manufacturers", params={"search": "xfer"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] >= 1
        names = [m["name"] for m in body["data"]]
        assert "Xfer Records" in names

    def test_search_case_insensitive(self, client):
        """search=VALHALLA returns Valhalla DSP."""
        resp = client.get("/api/v1/manufacturers", params={"search": "VALHALLA"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] >= 1
        names = [m["name"] for m in body["data"]]
        assert "Valhalla DSP" in names

    def test_search_no_match(self, client):
        """search=zzzzz returns total=0."""
        resp = client.get("/api/v1/manufacturers", params={"search": "zzzzz"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 0


class TestGetManufacturer:
    def test_get_by_slug(self, client):
        """GET /manufacturers/{slug} returns manufacturer with plugins."""
        resp = client.get("/api/v1/manufacturers/xfer-records")
        assert resp.status_code == 200
        body = resp.json()
        assert body["manufacturer"]["slug"] == "xfer-records"
        assert body["manufacturer"]["name"] == "Xfer Records"
        assert body["plugin_count"] == 1
        assert len(body["plugins"]) == 1
        assert body["plugins"][0]["name"] == "Serum"

    def test_manufacturer_has_full_plugin_detail(self, client):
        """Plugin objects in manufacturer detail include all fields."""
        resp = client.get("/api/v1/manufacturers/u-he")
        assert resp.status_code == 200
        plugin = resp.json()["plugins"][0]
        assert plugin["name"] == "Diva"
        assert "manufacturer" in plugin
        assert "formats" in plugin
        assert "aliases" in plugin

    def test_not_found(self, client):
        """GET /manufacturers/nonexistent returns 404."""
        resp = client.get("/api/v1/manufacturers/nonexistent")
        assert resp.status_code == 404

    def test_detail_has_pagination(self, client):
        """Detail response includes pagination metadata."""
        resp = client.get("/api/v1/manufacturers/xfer-records")
        body = resp.json()
        assert "pagination" in body
        assert body["pagination"]["total"] == 1
        assert body["pagination"]["page"] == 1

    def test_detail_pagination_per_page(self, client):
        """Pagination with per_page=1 limits plugins returned."""
        resp = client.get("/api/v1/manufacturers/xfer-records", params={"per_page": 1})
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["plugins"]) <= 1


class TestManufacturerPluginCount:
    """Tests for plugin_count on manufacturer list."""

    def test_list_includes_plugin_count(self, client):
        """Each manufacturer in the list has a plugin_count field."""
        resp = client.get("/api/v1/manufacturers")
        assert resp.status_code == 200
        for mfr in resp.json()["data"]:
            assert "plugin_count" in mfr
            assert isinstance(mfr["plugin_count"], int)
            assert mfr["plugin_count"] == 1  # each has 1 plugin in test data

    def test_plugin_count_values(self, client):
        """Plugin counts are accurate."""
        resp = client.get("/api/v1/manufacturers")
        counts = {m["name"]: m["plugin_count"] for m in resp.json()["data"]}
        assert counts["Xfer Records"] == 1
        assert counts["u-he"] == 1
        assert counts["Valhalla DSP"] == 1


class TestManufacturerSorting:
    """Tests for sort and order on /manufacturers."""

    def test_sort_by_name_desc(self, client):
        resp = client.get("/api/v1/manufacturers", params={"sort": "name", "order": "desc"})
        assert resp.status_code == 200
        names = [m["name"] for m in resp.json()["data"]]
        assert names == sorted(names, reverse=True)

    def test_sort_by_plugin_count_desc(self, client):
        """sort=plugin_count works (all equal in test data, so just verify no error)."""
        resp = client.get("/api/v1/manufacturers", params={"sort": "plugin_count", "order": "desc"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 3

    def test_sort_invalid_falls_back(self, client):
        resp = client.get("/api/v1/manufacturers", params={"sort": "invalid"})
        assert resp.status_code == 200
        names = [m["name"] for m in resp.json()["data"]]
        assert names == sorted(names)


class TestManufacturerSearchWithPagination:
    """Combined search and pagination on manufacturers."""

    def test_search_with_pagination(self, client):
        """Search + pagination works together."""
        resp = client.get("/api/v1/manufacturers", params={"search": "xfer", "per_page": 1})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] >= 1
        assert len(body["data"]) <= 1


class TestManufacturerCategories:
    """Category breakdown in manufacturer detail."""

    def test_detail_includes_categories(self, client):
        resp = client.get("/api/v1/manufacturers/xfer-records")
        assert resp.status_code == 200
        body = resp.json()
        assert "categories" in body
        assert body["categories"]["instrument"] == 1

    def test_categories_reflects_actual_data(self, client):
        resp = client.get("/api/v1/manufacturers/valhalla-dsp")
        body = resp.json()
        assert body["categories"]["effect"] == 1
