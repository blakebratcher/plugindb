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
        """VintageVerb is free, so price_type=free returns 1 result."""
        resp = client.get("/api/v1/plugins", params={"price_type": "free"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 1
        assert resp.json()["data"][0]["name"] == "Valhalla VintageVerb"

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


class TestTagFilter:
    """Tests for the tag query parameter on /plugins."""

    def test_filter_by_tag(self, client):
        """tag=synthesizer returns 2 plugins (Serum and Diva both have it)."""
        resp = client.get("/api/v1/plugins", params={"tag": "synthesizer"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 2
        names = {p["name"] for p in body["data"]}
        assert names == {"Serum", "Diva"}

    def test_filter_by_tag_no_match(self, client):
        """tag=nonexistent returns 0 results."""
        resp = client.get("/api/v1/plugins", params={"tag": "nonexistent"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 0

    def test_filter_by_tag_and_category(self, client):
        """tag=vintage & category=effect returns only VintageVerb."""
        resp = client.get(
            "/api/v1/plugins",
            params={"tag": "vintage", "category": "effect"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["name"] == "Valhalla VintageVerb"


class TestYearFilter:
    """Tests for the year query parameter on /plugins."""

    def test_filter_by_year(self, client):
        """year=2014 returns only Serum."""
        resp = client.get("/api/v1/plugins", params={"year": 2014})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["name"] == "Serum"

    def test_filter_by_year_no_match(self, client):
        """year=1999 returns 0 results."""
        resp = client.get("/api/v1/plugins", params={"year": 1999})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 0


class TestPriceTypeFilter:
    """Tests for the price_type query parameter on /plugins."""

    def test_filter_by_price_type_paid(self, client):
        """price_type=paid returns 2 plugins (Serum and Diva)."""
        resp = client.get("/api/v1/plugins", params={"price_type": "paid"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 2

    def test_filter_by_price_type_free_returns_plugin(self, client):
        """price_type=free returns VintageVerb."""
        resp = client.get("/api/v1/plugins", params={"price_type": "free"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["name"] == "Valhalla VintageVerb"

    def test_filter_by_price_type_freemium(self, client):
        """price_type=freemium returns 0 (no freemium plugins in seed data)."""
        resp = client.get("/api/v1/plugins", params={"price_type": "freemium"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 0


class TestResponseFields:
    """Tests verifying that new fields appear correctly in plugin responses."""

    def test_plugin_response_includes_tags(self, client):
        """Plugin list response includes tags as a list."""
        resp = client.get("/api/v1/plugins")
        assert resp.status_code == 200
        plugin = resp.json()["data"][0]
        assert "tags" in plugin
        assert isinstance(plugin["tags"], list)

    def test_plugin_response_includes_year(self, client):
        """Plugin response includes year as an int."""
        resp = client.get("/api/v1/plugins")
        assert resp.status_code == 200
        plugin = resp.json()["data"][0]
        assert "year" in plugin
        assert isinstance(plugin["year"], int)

    def test_plugin_response_includes_price_type(self, client):
        """Plugin response includes price_type as a string."""
        resp = client.get("/api/v1/plugins")
        assert resp.status_code == 200
        plugin = resp.json()["data"][0]
        assert "price_type" in plugin
        assert isinstance(plugin["price_type"], str)

    def test_plugin_response_all_fields_present(self, client):
        """GET /plugins/{id} includes ALL expected keys."""
        list_resp = client.get("/api/v1/plugins")
        plugin_id = list_resp.json()["data"][0]["id"]

        resp = client.get(f"/api/v1/plugins/{plugin_id}")
        assert resp.status_code == 200
        body = resp.json()

        expected_keys = {
            "id", "slug", "name", "manufacturer", "category", "subcategory",
            "formats", "daws", "os", "aliases", "tags", "description",
            "website", "image_url", "manual_url", "is_free", "price_type", "year",
            "created_at", "updated_at",
        }
        assert expected_keys.issubset(set(body.keys()))


class TestGetPluginBySlug:
    """GET /plugins/by-slug/{slug}"""

    def test_get_by_slug(self, client):
        resp = client.get("/api/v1/plugins/by-slug/serum")
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "Serum"
        assert body["slug"] == "serum"
        assert body["manufacturer"]["name"] == "Xfer Records"

    def test_slug_not_found(self, client):
        resp = client.get("/api/v1/plugins/by-slug/nonexistent")
        assert resp.status_code == 404

    def test_slug_returns_all_fields(self, client):
        resp = client.get("/api/v1/plugins/by-slug/serum")
        body = resp.json()
        assert "tags" in body
        assert "year" in body
        assert "price_type" in body
        assert "aliases" in body


class TestYearRangeFilter:
    """Tests for year_min / year_max on /plugins."""

    def test_year_min(self, client):
        resp = client.get("/api/v1/plugins", params={"year_min": 2013})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 1
        assert resp.json()["data"][0]["name"] == "Serum"

    def test_year_max(self, client):
        resp = client.get("/api/v1/plugins", params={"year_max": 2012})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 2

    def test_year_range(self, client):
        resp = client.get("/api/v1/plugins", params={"year_min": 2012, "year_max": 2014})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 2

    def test_year_range_no_match(self, client):
        resp = client.get("/api/v1/plugins", params={"year_min": 2020, "year_max": 2025})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 0


class TestMultiTagFilter:
    """Tests for comma-separated tags parameter."""

    def test_multi_tag_and_logic(self, client):
        """tags=synthesizer,vintage returns only Diva (has both)."""
        resp = client.get("/api/v1/plugins", params={"tags": "synthesizer,vintage"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["name"] == "Diva"

    def test_multi_tag_no_match(self, client):
        """tags=synthesizer,reverb returns 0 (no plugin has both)."""
        resp = client.get("/api/v1/plugins", params={"tags": "synthesizer,reverb"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 0


class TestSorting:
    """Tests for sort and order parameters on /plugins."""

    def test_sort_by_name_desc(self, client):
        resp = client.get("/api/v1/plugins", params={"sort": "name", "order": "desc"})
        assert resp.status_code == 200
        names = [p["name"] for p in resp.json()["data"]]
        assert names == sorted(names, reverse=True)

    def test_sort_by_year_asc(self, client):
        resp = client.get("/api/v1/plugins", params={"sort": "year", "order": "asc"})
        assert resp.status_code == 200
        years = [p["year"] for p in resp.json()["data"]]
        assert years == [2011, 2012, 2014]

    def test_sort_by_year_desc(self, client):
        resp = client.get("/api/v1/plugins", params={"sort": "year", "order": "desc"})
        assert resp.status_code == 200
        years = [p["year"] for p in resp.json()["data"]]
        assert years == [2014, 2012, 2011]

    def test_sort_invalid_falls_back(self, client):
        resp = client.get("/api/v1/plugins", params={"sort": "invalid"})
        assert resp.status_code == 200
        names = [p["name"] for p in resp.json()["data"]]
        assert names == sorted(names)


class TestRandomPlugin:
    """GET /plugins/random"""

    def test_random_returns_valid_plugin(self, client):
        resp = client.get("/api/v1/plugins/random")
        assert resp.status_code == 200
        body = resp.json()
        assert "name" in body
        assert "tags" in body
        assert "manufacturer" in body


class TestTripleFilters:
    """Tests for combining 3+ filters simultaneously."""

    def test_tag_year_price_type(self, client):
        """tag=synthesizer&year=2014&price_type=paid returns only Serum."""
        resp = client.get("/api/v1/plugins", params={
            "tag": "synthesizer", "year": 2014, "price_type": "paid",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["name"] == "Serum"

    def test_tag_year_combined(self, client):
        """tag=vintage&year=2012 returns VintageVerb."""
        resp = client.get("/api/v1/plugins", params={"tag": "vintage", "year": 2012})
        assert resp.status_code == 200
        assert resp.json()["data"][0]["name"] == "Valhalla VintageVerb"

    def test_tag_price_type_combined(self, client):
        """tag=vintage&price_type=free returns VintageVerb."""
        resp = client.get("/api/v1/plugins", params={"tag": "vintage", "price_type": "free"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["name"] == "Valhalla VintageVerb"

    def test_all_filters_no_match(self, client):
        """Impossible combination returns 0."""
        resp = client.get("/api/v1/plugins", params={
            "category": "effect", "tag": "synthesizer", "price_type": "paid",
        })
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 0

    def test_sorting_with_filters(self, client):
        """Filters and sorting work together."""
        resp = client.get("/api/v1/plugins", params={
            "category": "instrument", "sort": "year", "order": "desc",
        })
        assert resp.status_code == 200
        years = [p["year"] for p in resp.json()["data"]]
        assert years == [2014, 2011]


class TestSubcategoryFilter:
    """Tests for subcategory filter on /plugins."""

    def test_filter_by_subcategory(self, client):
        """subcategory=synth returns Serum and Diva."""
        resp = client.get("/api/v1/plugins", params={"subcategory": "synth"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 2

    def test_filter_by_subcategory_reverb(self, client):
        """subcategory=reverb returns VintageVerb only."""
        resp = client.get("/api/v1/plugins", params={"subcategory": "reverb"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["name"] == "Valhalla VintageVerb"

    def test_subcategory_and_category_combined(self, client):
        """category=effect&subcategory=reverb returns VintageVerb."""
        resp = client.get("/api/v1/plugins", params={"category": "effect", "subcategory": "reverb"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 1

    def test_subcategory_no_match(self, client):
        resp = client.get("/api/v1/plugins", params={"subcategory": "drum-machine"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 0


class TestOSFilter:
    """Tests for OS filter on /plugins."""

    def test_filter_by_os_linux(self, client):
        """os=linux returns only Diva."""
        resp = client.get("/api/v1/plugins", params={"os": "linux"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["name"] == "Diva"

    def test_filter_by_os_windows(self, client):
        """os=windows returns all 3 plugins."""
        resp = client.get("/api/v1/plugins", params={"os": "windows"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 3

    def test_filter_os_and_category(self, client):
        """os=macos&category=instrument returns Serum and Diva."""
        resp = client.get("/api/v1/plugins", params={"os": "macos", "category": "instrument"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 2


class TestSimilarPlugins:
    """GET /plugins/{id}/similar"""

    def test_similar_returns_related(self, client):
        """Serum's similar includes Diva (both instrument/synth, share 'synthesizer' tag)."""
        # First get Serum's ID
        resp = client.get("/api/v1/lookup", params={"alias": "Serum"})
        serum_id = resp.json()["id"]

        resp = client.get(f"/api/v1/plugins/{serum_id}/similar")
        assert resp.status_code == 200
        body = resp.json()
        names = [p["name"] for p in body["data"]]
        assert "Diva" in names

    def test_similar_excludes_self(self, client):
        """Source plugin is never in its own similar list."""
        resp = client.get("/api/v1/lookup", params={"alias": "Serum"})
        serum_id = resp.json()["id"]

        resp = client.get(f"/api/v1/plugins/{serum_id}/similar")
        ids = [p["id"] for p in resp.json()["data"]]
        assert serum_id not in ids

    def test_similar_404(self, client):
        """Similar for nonexistent plugin returns 404."""
        resp = client.get("/api/v1/plugins/99999/similar")
        assert resp.status_code == 404

    def test_similar_has_pagination(self, client):
        """Response includes pagination metadata."""
        resp = client.get("/api/v1/lookup", params={"alias": "Serum"})
        serum_id = resp.json()["id"]

        resp = client.get(f"/api/v1/plugins/{serum_id}/similar")
        assert "pagination" in resp.json()


class TestRandomPluginVariety:
    """Verify /plugins/random returns varied results."""

    def test_random_returns_different_results(self, client):
        """Call random 20 times, expect at least 2 distinct plugins (with 3 total)."""
        names = set()
        for _ in range(20):
            resp = client.get("/api/v1/plugins/random")
            assert resp.status_code == 200
            names.add(resp.json()["name"])
        assert len(names) >= 2


class TestComparePlugins:
    """GET /plugins/compare"""

    def test_compare_two_plugins(self, client):
        resp = client.get("/api/v1/plugins")
        ids = [p["id"] for p in resp.json()["data"][:2]]
        compare_resp = client.get("/api/v1/plugins/compare", params={"ids": f"{ids[0]},{ids[1]}"})
        assert compare_resp.status_code == 200
        body = compare_resp.json()
        assert len(body["plugins"]) == 2
        assert "shared_tags" in body["comparison"]
        assert "shared_formats" in body["comparison"]

    def test_compare_too_few(self, client):
        resp = client.get("/api/v1/plugins/compare", params={"ids": "1"})
        assert resp.status_code == 400

    def test_compare_too_many(self, client):
        resp = client.get("/api/v1/plugins/compare", params={"ids": "1,2,3,4,5,6"})
        assert resp.status_code == 400

    def test_compare_not_found(self, client):
        resp = client.get("/api/v1/plugins/compare", params={"ids": "99998,99999"})
        assert resp.status_code == 404

    def test_compare_shared_tags(self, client):
        """Serum and Diva share 'synthesizer' tag."""
        resp = client.get("/api/v1/plugins")
        plugins = resp.json()["data"]
        serum = next(p for p in plugins if p["name"] == "Serum")
        diva = next(p for p in plugins if p["name"] == "Diva")
        compare = client.get("/api/v1/plugins/compare", params={"ids": f"{serum['id']},{diva['id']}"})
        assert "synthesizer" in compare.json()["comparison"]["shared_tags"]


class TestIncludeParameter:
    """Tests for ?include=manufacturer_plugins."""

    def test_include_manufacturer_plugins(self, client):
        """include=manufacturer_plugins returns the field."""
        resp = client.get("/api/v1/plugins")
        plugin_id = resp.json()["data"][0]["id"]
        resp2 = client.get(f"/api/v1/plugins/{plugin_id}", params={"include": "manufacturer_plugins"})
        assert resp2.status_code == 200
        assert "manufacturer_plugins" in resp2.json()

    def test_without_include_no_extra_field(self, client):
        """Without include, manufacturer_plugins is absent."""
        resp = client.get("/api/v1/plugins")
        plugin_id = resp.json()["data"][0]["id"]
        resp2 = client.get(f"/api/v1/plugins/{plugin_id}")
        assert resp2.status_code == 200
        assert "manufacturer_plugins" not in resp2.json()

    def test_include_on_by_slug(self, client):
        """include works on /plugins/by-slug/ too."""
        resp = client.get("/api/v1/plugins/by-slug/serum", params={"include": "manufacturer_plugins"})
        assert resp.status_code == 200
        assert "manufacturer_plugins" in resp.json()


class TestRelatedTags:
    """Related tags on filtered /plugins results."""

    def test_filtered_has_related_tags(self, client):
        """Filtering by tag returns related_tags."""
        resp = client.get("/api/v1/plugins", params={"tag": "synthesizer"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["related_tags"] is not None
        assert "wavetable" in body["related_tags"]

    def test_related_tags_excludes_filtered_tag(self, client):
        """related_tags does not include the tag being filtered on."""
        resp = client.get("/api/v1/plugins", params={"tag": "synthesizer"})
        assert "synthesizer" not in resp.json()["related_tags"]

    def test_unfiltered_no_related_tags(self, client):
        """Unfiltered list has null related_tags."""
        resp = client.get("/api/v1/plugins")
        assert resp.json()["related_tags"] is None


class TestFilterValidation:
    """Validation of filter parameter values."""

    def test_invalid_category_returns_400(self, client):
        resp = client.get("/api/v1/plugins", params={"category": "bogus"})
        assert resp.status_code == 400
        assert "category" in resp.json()["detail"].lower()

    def test_invalid_price_type_returns_400(self, client):
        resp = client.get("/api/v1/plugins", params={"price_type": "premium"})
        assert resp.status_code == 400
        assert "price_type" in resp.json()["detail"].lower()

    def test_valid_category_still_works(self, client):
        resp = client.get("/api/v1/plugins", params={"category": "instrument"})
        assert resp.status_code == 200


class TestEdgeCases:
    """Miscellaneous edge cases."""

    def test_all_filters_combined(self, client):
        """Applying many filters at once works."""
        resp = client.get("/api/v1/plugins", params={
            "category": "instrument",
            "subcategory": "synth",
            "tag": "synthesizer",
            "year": 2014,
            "price_type": "paid",
            "os": "windows",
            "sort": "name",
        })
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 1
        assert resp.json()["data"][0]["name"] == "Serum"

    def test_tag_filter_no_substring_false_positive(self, client):
        """tag=verb should NOT match 'reverb' — only exact tag values."""
        resp = client.get("/api/v1/plugins", params={"tag": "verb"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 0

    def test_format_filter_no_substring_false_positive(self, client):
        """format=VST should NOT match VST2 or VST3."""
        resp = client.get("/api/v1/plugins", params={"format": "VST"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 0

    def test_os_filter_no_substring_false_positive(self, client):
        """os=win should NOT match 'windows'."""
        resp = client.get("/api/v1/plugins", params={"os": "win"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 0

    def test_compare_with_non_integer_ids(self, client):
        """Non-integer IDs return 400."""
        resp = client.get("/api/v1/plugins/compare", params={"ids": "abc,def"})
        assert resp.status_code == 400


class TestManualUrl:
    """Tests for manual_url field."""

    def test_plugin_with_manual_url(self, client):
        """Serum has manual_url in test data."""
        resp = client.get("/api/v1/plugins/by-slug/serum")
        assert resp.status_code == 200
        assert resp.json()["manual_url"] == "https://example.com/manual.pdf"

    def test_plugin_without_manual_url(self, client):
        """Diva has no manual_url in test data."""
        resp = client.get("/api/v1/plugins/by-slug/diva")
        assert resp.status_code == 200
        assert resp.json()["manual_url"] is None

    def test_manual_url_in_list(self, client):
        """Plugin list includes manual_url field."""
        resp = client.get("/api/v1/plugins")
        assert resp.status_code == 200
        plugin = resp.json()["data"][0]
        assert "manual_url" in plugin


class TestImageUrl:
    """Tests for image_url field."""

    def test_plugin_with_image_url(self, client):
        """Serum has image_url in test data."""
        resp = client.get("/api/v1/plugins/by-slug/serum")
        assert resp.status_code == 200
        assert resp.json()["image_url"] == "https://xferrecords.com/images/serum.png"

    def test_plugin_without_image_url(self, client):
        """Diva has no image_url in test data."""
        resp = client.get("/api/v1/plugins/by-slug/diva")
        assert resp.status_code == 200
        assert resp.json()["image_url"] is None

    def test_image_url_in_list(self, client):
        """Plugin list includes image_url field."""
        resp = client.get("/api/v1/plugins")
        assert resp.status_code == 200
        plugin = resp.json()["data"][0]
        assert "image_url" in plugin

    def test_image_url_in_suggest(self, client):
        """Suggest results include image_url."""
        resp = client.get("/api/v1/suggest", params={"q": "Ser"})
        assert resp.status_code == 200
        if resp.json()["results"]:
            assert "image_url" in resp.json()["results"][0]

    def test_image_proxy_bad_url(self, client):
        """Image proxy rejects non-HTTP URLs."""
        resp = client.get("/api/v1/image-proxy", params={"url": "ftp://bad.com/img.png"})
        assert resp.status_code == 400
