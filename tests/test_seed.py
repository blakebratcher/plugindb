"""Tests for PluginDB schema creation, seeding, and alias lookup."""

from __future__ import annotations

import copy
import json
import sqlite3
from pathlib import Path

import pytest

from plugindb.database import create_schema, get_connection
from plugindb.seed import load_seed, seed_database, slugify, validate_seed


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_SEED = {
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
            "aliases": ["Serum", "Xfer Serum", "SerumFX"],
            "description": "Advanced wavetable synthesizer with visual feedback",
            "tags": ["synthesizer", "wavetable", "electronic"],
            "year": 2014,
            "price_type": "paid",
        },
        {
            "slug": "diva",
            "name": "Diva",
            "manufacturer_slug": "u-he",
            "category": "instrument",
            "subcategory": "synth",
            "formats": ["VST3", "VST2", "AU"],
            "aliases": ["Diva", "u-he Diva"],
            "description": "Analogue modelling synthesizer with zero-delay feedback filters",
            "tags": ["synthesizer", "analog-modeling", "vintage"],
            "year": 2011,
            "price_type": "paid",
        },
        {
            "slug": "valhalla-vintage-verb",
            "name": "Valhalla VintageVerb",
            "manufacturer_slug": "valhalla-dsp",
            "category": "effect",
            "subcategory": "reverb",
            "formats": ["VST3", "AU", "AAX"],
            "aliases": ["VintageVerb", "Valhalla VintageVerb", "ValhallaVintageVerb"],
            "description": "Lush algorithmic reverb inspired by classic hardware",
            "tags": ["reverb", "vintage", "lush"],
            "year": 2012,
            "price_type": "free",
        },
    ],
}


@pytest.fixture
def db():
    """In-memory SQLite database with schema created."""
    conn = get_connection(":memory:")
    create_schema(conn)
    yield conn
    conn.close()


@pytest.fixture
def seeded_db(db):
    """In-memory database seeded with sample data."""
    seed_database(db, SAMPLE_SEED)
    return db


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------

class TestSchema:
    def test_tables_exist(self, db):
        """All expected tables are created."""
        tables = {
            row[0]
            for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert "manufacturers" in tables
        assert "plugins" in tables
        assert "aliases" in tables

    def test_fts_table_exists(self, db):
        """FTS5 virtual table is created."""
        tables = {
            row[0]
            for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert "plugins_fts" in tables

    def test_wal_mode(self, tmp_path):
        """WAL journal mode is activated for on-disk databases."""
        db_path = tmp_path / "test.sqlite"
        conn = get_connection(db_path)
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        conn.close()
        assert mode == "wal"

    def test_foreign_keys_enabled(self, db):
        """Foreign key enforcement is on."""
        fk = db.execute("PRAGMA foreign_keys").fetchone()[0]
        assert fk == 1

    def test_schema_idempotent(self, db):
        """Calling create_schema twice doesn't error."""
        create_schema(db)  # second call
        tables = {
            row[0]
            for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert "plugins" in tables


# ---------------------------------------------------------------------------
# Seed tests
# ---------------------------------------------------------------------------

class TestSeed:
    def test_manufacturer_count(self, seeded_db):
        count = seeded_db.execute("SELECT COUNT(*) FROM manufacturers").fetchone()[0]
        assert count == 3

    def test_plugin_count(self, seeded_db):
        count = seeded_db.execute("SELECT COUNT(*) FROM plugins").fetchone()[0]
        assert count == 3

    def test_alias_count(self, seeded_db):
        count = seeded_db.execute("SELECT COUNT(*) FROM aliases").fetchone()[0]
        # Serum: 3 + Diva: 2 + VintageVerb: 3 = 8
        assert count == 8

    def test_plugin_has_correct_manufacturer(self, seeded_db):
        row = seeded_db.execute(
            """SELECT p.name, m.name as mfr_name
               FROM plugins p JOIN manufacturers m ON p.manufacturer_id = m.id
               WHERE p.slug = 'serum'"""
        ).fetchone()
        assert row is not None
        assert row["mfr_name"] == "Xfer Records"

    def test_formats_stored_as_json(self, seeded_db):
        row = seeded_db.execute(
            "SELECT formats FROM plugins WHERE slug = 'serum'"
        ).fetchone()
        formats = json.loads(row["formats"])
        assert "VST3" in formats
        assert "AU" in formats

    def test_idempotent_reseed(self, seeded_db):
        """Seeding twice produces the same counts (no duplicates)."""
        seed_database(seeded_db, SAMPLE_SEED)
        count = seeded_db.execute("SELECT COUNT(*) FROM plugins").fetchone()[0]
        assert count == 3

    def test_fts_populated(self, seeded_db):
        rows = seeded_db.execute(
            "SELECT * FROM plugins_fts WHERE plugins_fts MATCH 'Serum'"
        ).fetchall()
        assert len(rows) >= 1

    def test_tags_stored_as_json(self, seeded_db):
        """Tags column stores a valid JSON array that parses correctly."""
        row = seeded_db.execute(
            "SELECT tags FROM plugins WHERE slug = 'serum'"
        ).fetchone()
        tags = json.loads(row["tags"])
        assert isinstance(tags, list)
        assert "synthesizer" in tags
        assert "wavetable" in tags
        assert "electronic" in tags

    def test_year_stored(self, seeded_db):
        """Year column holds the correct integer value."""
        row = seeded_db.execute(
            "SELECT year FROM plugins WHERE slug = 'serum'"
        ).fetchone()
        assert row["year"] == 2014

    def test_price_type_stored(self, seeded_db):
        """Price type column has the correct value."""
        row = seeded_db.execute(
            "SELECT price_type FROM plugins WHERE slug = 'valhalla-vintage-verb'"
        ).fetchone()
        assert row["price_type"] == "free"

    def test_tags_in_fts(self, seeded_db):
        """FTS index includes tag text — MATCH on 'wavetable' returns results."""
        rows = seeded_db.execute(
            "SELECT * FROM plugins_fts WHERE plugins_fts MATCH 'wavetable'"
        ).fetchall()
        assert len(rows) >= 1


# ---------------------------------------------------------------------------
# Alias lookup tests
# ---------------------------------------------------------------------------

class TestAliasLookup:
    def test_case_insensitive_lookup(self, seeded_db):
        """Alias lookup is case-insensitive via name_lower column."""
        row = seeded_db.execute(
            "SELECT plugin_id FROM aliases WHERE name_lower = ?",
            ("serumfx",),
        ).fetchone()
        assert row is not None

    def test_exact_alias_match(self, seeded_db):
        row = seeded_db.execute(
            "SELECT plugin_id FROM aliases WHERE name_lower = ?",
            ("valhalla vintageverb",),
        ).fetchone()
        assert row is not None

    def test_unknown_alias_returns_nothing(self, seeded_db):
        row = seeded_db.execute(
            "SELECT plugin_id FROM aliases WHERE name_lower = ?",
            ("nonexistent-plugin",),
        ).fetchone()
        assert row is None


# ---------------------------------------------------------------------------
# Slugify tests
# ---------------------------------------------------------------------------

class TestSlugify:
    def test_basic(self):
        assert slugify("Xfer Records") == "xfer-records"

    def test_preserves_hyphens(self):
        assert slugify("u-he") == "u-he"

    def test_strips_parens(self):
        assert slugify("OTT (Xfer)") == "ott-xfer"

    def test_collapses_spaces(self):
        assert slugify("  My   Plugin  ") == "my-plugin"

    def test_empty_string(self):
        assert slugify("") == ""


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def _make_seed_data() -> dict:
    """Return a deep copy of the sample seed data for mutation in tests."""
    return copy.deepcopy(SAMPLE_SEED)


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------

class TestValidation:
    def test_validate_valid_data(self):
        errors = validate_seed(_make_seed_data())
        assert errors == []

    def test_validate_missing_required_field(self):
        data = _make_seed_data()
        del data["plugins"][0]["name"]
        errors = validate_seed(data)
        assert any("name" in e for e in errors)

    def test_validate_duplicate_id(self):
        data = _make_seed_data()
        data["plugins"].append(data["plugins"][0].copy())
        errors = validate_seed(data)
        assert any("duplicate" in e.lower() for e in errors)

    def test_validate_invalid_category(self):
        data = _make_seed_data()
        data["plugins"][0]["category"] = "invalid"
        errors = validate_seed(data)
        assert any("category" in e for e in errors)

    def test_validate_alias_conflict(self):
        data = _make_seed_data()
        data["plugins"][1]["aliases"].append(data["plugins"][0]["aliases"][0])
        errors = validate_seed(data)
        assert any("alias" in e.lower() for e in errors)

    def test_validate_bad_schema_version(self):
        data = _make_seed_data()
        data["schema_version"] = "2.0"
        errors = validate_seed(data)
        assert any("schema_version" in e for e in errors)

    def test_validate_non_kebab_slug(self):
        data = _make_seed_data()
        data["plugins"][0]["slug"] = "Not_Kebab Case!"
        errors = validate_seed(data)
        assert any("kebab" in e.lower() for e in errors)

    def test_validate_unknown_manufacturer(self):
        data = _make_seed_data()
        data["plugins"][0]["manufacturer_slug"] = "nonexistent-mfr"
        errors = validate_seed(data)
        assert any("manufacturer" in e.lower() for e in errors)

    def test_validate_empty_name(self):
        data = _make_seed_data()
        data["plugins"][0]["name"] = ""
        errors = validate_seed(data)
        assert any("empty" in e.lower() for e in errors)

    def test_validate_empty_aliases(self):
        data = _make_seed_data()
        data["plugins"][0]["aliases"] = []
        errors = validate_seed(data)
        assert any("aliases" in e.lower() for e in errors)

    def test_validate_invalid_tags_not_list(self):
        data = _make_seed_data()
        data["plugins"][0]["tags"] = "not-a-list"
        errors = validate_seed(data)
        assert any("tags" in e.lower() for e in errors)

    def test_validate_invalid_tag_item(self):
        data = _make_seed_data()
        data["plugins"][0]["tags"] = ["valid", 123]
        errors = validate_seed(data)
        assert any("tag" in e.lower() and "string" in e.lower() for e in errors)

    def test_validate_invalid_year_out_of_range(self):
        data = _make_seed_data()
        data["plugins"][0]["year"] = 1800
        errors = validate_seed(data)
        assert any("year" in e.lower() for e in errors)

    def test_validate_invalid_price_type(self):
        data = _make_seed_data()
        data["plugins"][0]["price_type"] = "premium"
        errors = validate_seed(data)
        assert any("price_type" in e.lower() for e in errors)

    def test_validate_invalid_format(self):
        data = _make_seed_data()
        data["plugins"][0]["formats"] = ["VST3", "BadFormat"]
        errors = validate_seed(data)
        assert any("format" in e.lower() for e in errors)


class TestAutoMigration:
    """Schema change auto-detection."""

    def test_check_schema_detects_stale(self):
        """check_schema returns False when columns are missing."""
        from plugindb.database import check_schema, get_connection
        conn = get_connection(":memory:")
        # Create an old-style table missing tags, year, price_type
        conn.execute("""
            CREATE TABLE plugins (
                id INTEGER PRIMARY KEY,
                slug TEXT NOT NULL,
                name TEXT NOT NULL,
                manufacturer_id INTEGER NOT NULL,
                category TEXT NOT NULL DEFAULT 'effect',
                subcategory TEXT,
                formats TEXT NOT NULL DEFAULT '[]',
                daws TEXT NOT NULL DEFAULT '[]',
                os TEXT NOT NULL DEFAULT '[]',
                description TEXT,
                website TEXT,
                is_free INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
        assert check_schema(conn) is False
        conn.close()

    def test_check_schema_passes_current(self, seeded_db):
        """check_schema returns True for the current schema."""
        from plugindb.database import check_schema
        assert check_schema(seeded_db) is True
