"""Tests for the enrichment pipeline."""
from plugindb.enricher import validate_enrichment, EnrichmentResult


def test_validate_valid_plugin():
    plugin = {"price_type": "paid", "category": "effect", "formats": ["VST3", "AU"]}
    assert validate_enrichment(plugin) == []


def test_validate_invalid_price_type():
    plugin = {"price_type": "premium"}
    errors = validate_enrichment(plugin)
    assert any("price_type" in e for e in errors)


def test_validate_invalid_format():
    plugin = {"formats": ["VST3", "BadFormat"]}
    errors = validate_enrichment(plugin)
    assert any("format" in e.lower() for e in errors)


def test_enrichment_result_default():
    r = EnrichmentResult(plugin_id="test")
    assert r.fields_updated == []
    assert r.source == ""
    assert r.error == ""
