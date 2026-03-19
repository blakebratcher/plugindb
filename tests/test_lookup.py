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

    def test_batch_max_200_accepted(self, client):
        """Batch with exactly 200 names is accepted."""
        names = ["Serum"] + [f"Unknown{i}" for i in range(199)]
        resp = client.post("/api/v1/lookup", json={"names": names})
        assert resp.status_code == 200
        data = resp.json()
        assert data["matched"] == 1
        assert data["unmatched"] == 199

    def test_batch_over_200_rejected(self, client):
        """Batch with 201 names is rejected (422)."""
        names = [f"Plugin{i}" for i in range(201)]
        resp = client.post("/api/v1/lookup", json={"names": names})
        assert resp.status_code == 422

    def test_batch_response_includes_new_fields(self, client):
        """Batch results include tags, year, and price_type."""
        resp = client.post("/api/v1/lookup", json={"names": ["Serum"]})
        assert resp.status_code == 200
        plugin = resp.json()["results"][0]["plugin"]
        assert "tags" in plugin
        assert "year" in plugin
        assert "price_type" in plugin

    def test_batch_detects_duplicates(self, client):
        """Multiple queries resolving to same plugin are reported as duplicates."""
        resp = client.post("/api/v1/lookup", json={"names": ["Serum", "Xfer Serum"]})
        assert resp.status_code == 200
        body = resp.json()
        assert body["matched"] == 2
        assert "Serum" in body["duplicates"]
        assert "Xfer Serum" in body["duplicates"]

    def test_batch_no_duplicates(self, client):
        """Distinct plugins have empty duplicates list."""
        resp = client.post("/api/v1/lookup", json={"names": ["Serum", "Diva"]})
        assert resp.status_code == 200
        assert resp.json()["duplicates"] == []


class TestBatchEdgeCases:
    """Edge cases for batch lookup."""

    def test_batch_single_name(self, client):
        """Batch with single name works."""
        resp = client.post("/api/v1/lookup", json={"names": ["Serum"]})
        assert resp.status_code == 200
        assert resp.json()["matched"] == 1

    def test_batch_all_unknown(self, client):
        """Batch with all unknown names returns 200 with 0 matched."""
        resp = client.post("/api/v1/lookup", json={"names": ["x", "y", "z"]})
        assert resp.status_code == 200
        assert resp.json()["matched"] == 0
        assert resp.json()["unmatched"] == 3


class TestBatchUnicode:
    """Unicode names in batch lookup."""

    def test_batch_unicode_names(self, client):
        resp = client.post("/api/v1/lookup", json={"names": ["Sérum", "Díva"]})
        assert resp.status_code == 200
        assert resp.json()["unmatched"] == 2
