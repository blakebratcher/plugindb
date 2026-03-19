"""Tests for the /lookup endpoint (GET single + POST batch)."""

from __future__ import annotations


class TestGetLookup:
    """GET /lookup?alias=..."""

    def test_exact_match(self, client):
        """Exact alias resolves to the correct plugin."""
        resp = client.get("/api/v1/lookup", params={"alias": "Serum"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Serum"
        assert data["slug"] == "serum"
        assert data["manufacturer"]["name"] == "Xfer Records"

    def test_case_insensitive(self, client):
        """Alias matching is case-insensitive."""
        resp = client.get("/api/v1/lookup", params={"alias": "serumfx"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Serum"

    def test_not_found(self, client):
        """Unknown alias returns 404."""
        resp = client.get("/api/v1/lookup", params={"alias": "NonExistentPlugin9999"})
        assert resp.status_code == 404

    def test_missing_param(self, client):
        """Omitting the required alias parameter returns 422."""
        resp = client.get("/api/v1/lookup")
        assert resp.status_code == 422

    def test_response_includes_aliases(self, client):
        """Response contains the full list of aliases for the matched plugin."""
        resp = client.get("/api/v1/lookup", params={"alias": "Xfer Serum"})
        assert resp.status_code == 200
        aliases = resp.json()["aliases"]
        assert "Serum" in aliases
        assert "Xfer Serum" in aliases
        assert "SerumFX" in aliases


class TestPostBatchLookup:
    """POST /lookup (batch)."""

    def test_batch_mixed(self, client):
        """Batch with 2 known + 1 unknown returns correct matched/unmatched counts."""
        resp = client.post("/api/v1/lookup", json={"names": ["Serum", "Diva", "FakePlugin"]})
        assert resp.status_code == 200
        data = resp.json()
        assert data["matched"] == 2
        assert data["unmatched"] == 1
        # Verify the matched entries
        matched_names = [r["plugin"]["name"] for r in data["results"] if r["matched"]]
        assert "Serum" in matched_names
        assert "Diva" in matched_names
        # Verify the unmatched entry
        unmatched = [r for r in data["results"] if not r["matched"]]
        assert len(unmatched) == 1
        assert unmatched[0]["query"] == "FakePlugin"
        assert unmatched[0]["plugin"] is None

    def test_batch_empty_names_rejected(self, client):
        """Batch with empty names list is rejected (422)."""
        resp = client.post("/api/v1/lookup", json={"names": []})
        assert resp.status_code == 422
