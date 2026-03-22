"""Shared test fixtures for PluginDB API tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from plugindb.database import create_schema, get_connection
from plugindb.seed import seed_database


# ---------------------------------------------------------------------------
# Seed data — minimal but covers instruments, effects, multiple manufacturers
# ---------------------------------------------------------------------------

SEED_DATA = {
    "schema_version": "1.0",
    "manufacturers": [
        {"slug": "xfer-records", "name": "Xfer Records"},
        {"slug": "u-he", "name": "u-he"},
        {"slug": "valhalla-dsp", "name": "Valhalla DSP"},
    ],
    "plugins": [
        {
            "slug": "serum",
            "name": "Serum",
            "manufacturer_slug": "xfer-records",
            "category": "instrument",
            "subcategory": "synth",
            "formats": ["VST3", "AU", "AAX"],
            "daws": ["Ableton Live", "Bitwig", "FL Studio"],
            "aliases": ["Serum", "Xfer Serum", "SerumFX"],
            "description": "Advanced wavetable synthesizer with visual feedback",
            "price_type": "paid",
            "tags": ["synthesizer", "wavetable", "electronic"],
            "year": 2014,
            "os": ["windows", "macos"],
            "image_url": "https://xferrecords.com/images/serum.png",
            "manual_url": "https://example.com/manual.pdf",
        },
        {
            "slug": "diva",
            "name": "Diva",
            "manufacturer_slug": "u-he",
            "category": "instrument",
            "subcategory": "synth",
            "formats": ["VST3", "VST2", "AU"],
            "daws": ["Ableton Live", "Bitwig", "Reaper"],
            "aliases": ["Diva", "u-he Diva"],
            "description": "Analogue modelling synthesizer with zero-delay feedback filters",
            "price_type": "paid",
            "tags": ["synthesizer", "analog-modeling", "vintage"],
            "year": 2011,
            "os": ["windows", "macos", "linux"],
        },
        {
            "slug": "valhalla-vintage-verb",
            "name": "Valhalla VintageVerb",
            "manufacturer_slug": "valhalla-dsp",
            "category": "effect",
            "subcategory": "reverb",
            "formats": ["VST3", "AU", "AAX"],
            "daws": ["Ableton Live", "FL Studio"],
            "aliases": ["VintageVerb", "Valhalla VintageVerb", "ValhallaVintageVerb"],
            "description": "Lush algorithmic reverb inspired by classic hardware",
            "price_type": "free",
            "tags": ["reverb", "vintage", "lush"],
            "year": 2012,
            "os": ["windows", "macos"],
        },
    ],
}


@pytest.fixture()
def seed_data() -> dict:
    """Return the minimal seed data dict for use in tests."""
    return SEED_DATA


@pytest.fixture()
def seeded_db():
    """In-memory SQLite database with schema + seed data loaded."""
    conn = get_connection(":memory:")
    create_schema(conn)
    seed_database(conn, SEED_DATA)
    yield conn
    conn.close()


@pytest.fixture()
def client(seeded_db):
    """FastAPI TestClient backed by the seeded in-memory database."""
    from plugindb.main import create_app

    app = create_app(db_connection=seeded_db)
    with TestClient(app) as tc:
        yield tc
