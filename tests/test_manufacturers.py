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
