"""Tests for static frontend serving."""

from __future__ import annotations


class TestFrontendServing:
    """Verify that the frontend static files are served correctly."""

    def test_root_serves_html_for_browsers(self, client):
        """Root path returns HTML when Accept: text/html."""
        resp = client.get("/", headers={"Accept": "text/html"})
        assert resp.status_code == 200
        assert "PluginDB" in resp.text

    def test_root_serves_json_for_api_clients(self, client):
        """Root path returns JSON when Accept: application/json."""
        resp = client.get("/", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "PluginDB"

    def test_static_css(self, client):
        """style.css is served with correct content type."""
        resp = client.get("/style.css")
        assert resp.status_code == 200
        assert "text/css" in resp.headers.get("content-type", "")

    def test_static_js(self, client):
        """app.js is served with correct content type."""
        resp = client.get("/app.js")
        assert resp.status_code == 200
        assert "javascript" in resp.headers.get("content-type", "")

    def test_favicon(self, client):
        """favicon.svg is served."""
        resp = client.get("/favicon.svg")
        assert resp.status_code == 200

    def test_api_routes_unaffected(self, client):
        """API routes still work after static mounting."""
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_swagger_docs_accessible(self, client):
        """Swagger docs still accessible."""
        resp = client.get("/docs")
        assert resp.status_code == 200
