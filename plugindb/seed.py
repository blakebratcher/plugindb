"""Seed pipeline — load, transform, and import plugin data into PluginDB."""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

from plugindb.database import DEFAULT_DB_PATH, check_schema, create_schema, get_connection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(name: str) -> str:
    """Convert a name to a URL-safe kebab-case slug.

    Examples:
        >>> slugify("Xfer Records")
        'xfer-records'
        >>> slugify("u-he Diva")
        'u-he-diva'
        >>> slugify("OTT (Xfer)")
        'ott-xfer'
    """
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", " ", s)   # keep letters, digits, hyphens
    s = re.sub(r"[\s]+", "-", s)            # whitespace -> single hyphen
    s = re.sub(r"-{2,}", "-", s)            # collapse multiple hyphens
    s = s.strip("-")
    return s


# ---------------------------------------------------------------------------
# Load / Transform
# ---------------------------------------------------------------------------

def load_seed(path: Path | str) -> dict:
    """Load a seed JSON file and return its parsed contents."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Seed file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


VALID_CATEGORIES = {"instrument", "effect", "midi", "utility", "container", "note-effect"}
VALID_FORMATS = {"VST2", "VST3", "AU", "CLAP", "AAX", "LV2", "Standalone"}
VALID_PRICE_TYPES = {"free", "paid", "subscription", "freemium", "included"}


def transform_registry(registry_path: Path | str, output_path: Path | str) -> None:
    """Convert a Bitwig OS plugin-registry.json into PluginDB seed.json format.

    Transformations applied:
        - Strips ``source`` and ``vault_note`` fields from each entry
        - Extracts a deduplicated manufacturers list
        - Validates category against known set
        - Filters formats to known standard formats (drops DAW-specific like
          "Ableton Live instrument")
        - Preserves id, name, manufacturer, category, subcategory, aliases, formats
    """
    registry_path = Path(registry_path)
    output_path = Path(output_path)

    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    entries = registry.get("entries", [])
    manufacturers: dict[str, dict] = {}
    plugins: list[dict] = []

    for entry in entries:
        mfr_name = entry.get("manufacturer", "Unknown")
        mfr_slug = slugify(mfr_name)
        if mfr_slug not in manufacturers:
            manufacturers[mfr_slug] = {
                "slug": mfr_slug,
                "name": mfr_name,
            }

        # Filter formats to known standards
        raw_formats = entry.get("formats", [])
        formats = [f for f in raw_formats if f in VALID_FORMATS]
        if not formats:
            # Keep original formats if none match (better than empty)
            formats = raw_formats

        category = entry.get("category", "effect")
        if category not in VALID_CATEGORIES:
            category = "effect"

        plugin = {
            "slug": entry.get("id", slugify(entry.get("name", ""))),
            "name": entry.get("name", ""),
            "manufacturer_slug": mfr_slug,
            "category": category,
            "subcategory": entry.get("subcategory"),
            "formats": formats,
            "aliases": entry.get("aliases", []),
        }
        plugins.append(plugin)

    seed_data = {
        "schema_version": "1.0",
        "manufacturers": sorted(manufacturers.values(), key=lambda m: m["slug"]),
        "plugins": plugins,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(seed_data, f, indent=2, ensure_ascii=False)

    print(f"Transformed {len(plugins)} plugins, {len(manufacturers)} manufacturers -> {output_path}")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

_KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_seed(data: dict) -> list[str]:
    """Validate seed data and return a list of error strings (empty = valid).

    Checks performed:
        - schema_version is "1.0"
        - Every plugin has required fields: slug, name, manufacturer_slug,
          category, aliases
        - Every plugin slug is unique
        - Every plugin slug is kebab-case (lowercase letters, digits, hyphens)
        - Every alias is unique across all plugins (case-insensitive)
        - Every manufacturer_slug references an existing manufacturer
        - Every category is valid
        - No empty name, manufacturer_slug, or aliases arrays
    """
    errors: list[str] = []

    # Schema version
    if data.get("schema_version") != "1.0":
        errors.append(
            f"schema_version must be \"1.0\", got \"{data.get('schema_version')}\""
        )

    # Build manufacturer slug set
    mfr_slugs = {m["slug"] for m in data.get("manufacturers", []) if "slug" in m}

    # Plugin-level checks
    seen_slugs: set[str] = set()
    seen_aliases: dict[str, str] = {}  # alias_lower -> plugin slug that owns it
    required_fields = ("slug", "name", "manufacturer_slug", "category", "aliases")

    for i, plugin in enumerate(data.get("plugins", [])):
        label = plugin.get("name") or plugin.get("slug") or f"[{i}]"

        # Required fields
        for field in required_fields:
            if field not in plugin:
                errors.append(f"Plugin {label}: missing required field '{field}'")

        # Empty-value checks
        name = plugin.get("name")
        if name is not None and not name.strip():
            errors.append(f"Plugin [{i}]: name is empty")

        mfr_slug = plugin.get("manufacturer_slug")
        if mfr_slug is not None and not mfr_slug.strip():
            errors.append(f"Plugin {label}: manufacturer_slug is empty")

        aliases = plugin.get("aliases")
        if aliases is not None and not isinstance(aliases, list):
            errors.append(f"Plugin {label}: aliases must be a list")
        elif aliases is not None and len(aliases) == 0:
            errors.append(f"Plugin {label}: aliases array is empty")

        # Slug uniqueness
        slug = plugin.get("slug")
        if slug is not None:
            if slug in seen_slugs:
                errors.append(f"Duplicate plugin slug: '{slug}'")
            seen_slugs.add(slug)

            # Kebab-case check
            if slug and not _KEBAB_RE.match(slug):
                errors.append(
                    f"Plugin {label}: slug '{slug}' is not kebab-case "
                    "(must be lowercase letters, digits, and hyphens only)"
                )

        # Manufacturer reference
        if mfr_slug and mfr_slug.strip() and mfr_slug not in mfr_slugs:
            errors.append(
                f"Plugin {label}: manufacturer_slug '{mfr_slug}' "
                "does not reference an existing manufacturer"
            )

        # Category validity
        category = plugin.get("category")
        if category is not None and category not in VALID_CATEGORIES:
            errors.append(
                f"Plugin {label}: invalid category '{category}' "
                f"(expected one of {sorted(VALID_CATEGORIES)})"
            )

        # Alias uniqueness (case-insensitive, across all plugins)
        if isinstance(aliases, list):
            for alias in aliases:
                alias_lower = alias.lower()
                if alias_lower in seen_aliases:
                    owner = seen_aliases[alias_lower]
                    errors.append(
                        f"Duplicate alias '{alias}' in plugin '{slug}' "
                        f"(already defined in '{owner}')"
                    )
                else:
                    seen_aliases[alias_lower] = slug or label

        # Tags validation (optional field)
        tags = plugin.get("tags")
        if tags is not None:
            if not isinstance(tags, list):
                errors.append(f"Plugin {label}: tags must be a list")
            else:
                for t in tags:
                    if not isinstance(t, str):
                        errors.append(f"Plugin {label}: tag items must be strings, got {type(t).__name__}")

        # Year validation (optional field)
        year = plugin.get("year")
        if year is not None:
            if not isinstance(year, int):
                errors.append(f"Plugin {label}: year must be an integer")
            elif year < 1970 or year > 2030:
                errors.append(f"Plugin {label}: year {year} is out of range (1970-2030)")

        # Price type validation (optional field)
        price_type = plugin.get("price_type")
        if price_type is not None and price_type not in VALID_PRICE_TYPES:
            errors.append(
                f"Plugin {label}: invalid price_type '{price_type}' "
                f"(expected one of {sorted(VALID_PRICE_TYPES)})"
            )

        # Format validation (optional field)
        formats = plugin.get("formats")
        if isinstance(formats, list):
            for fmt in formats:
                if fmt not in VALID_FORMATS:
                    errors.append(f"Plugin {label}: invalid format '{fmt}'")

    return errors


# ---------------------------------------------------------------------------
# Seed database
# ---------------------------------------------------------------------------

def seed_database(conn: sqlite3.Connection, data: dict) -> dict[str, int]:
    """Import seed data into the database. Idempotent — clears and re-inserts.

    Returns a dict of counts: manufacturers, plugins, aliases.
    """
    cur = conn.cursor()

    # Clear existing data (order matters for foreign keys)
    # Contentless FTS5 tables don't support DELETE — drop and recreate
    cur.execute("DROP TABLE IF EXISTS plugins_fts")
    cur.execute("DELETE FROM aliases")
    cur.execute("DELETE FROM plugins")
    cur.execute("DELETE FROM manufacturers")
    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS plugins_fts USING fts5(
            name,
            manufacturer_name,
            category,
            subcategory,
            description,
            aliases,
            tags,
            content=''
        )
    """)

    # Insert manufacturers
    mfr_id_map: dict[str, int] = {}
    for mfr in data.get("manufacturers", []):
        cur.execute(
            "INSERT INTO manufacturers (slug, name, website) VALUES (?, ?, ?)",
            (mfr["slug"], mfr["name"], mfr.get("website")),
        )
        mfr_id_map[mfr["slug"]] = cur.lastrowid  # type: ignore[assignment]

    # Insert plugins + aliases + FTS
    plugin_count = 0
    alias_count = 0
    for plugin in data.get("plugins", []):
        mfr_slug = plugin.get("manufacturer_slug", "")
        mfr_id = mfr_id_map.get(mfr_slug)
        if mfr_id is None:
            print(f"  Warning: unknown manufacturer slug '{mfr_slug}' for plugin '{plugin['name']}', skipping")
            continue

        formats_json = json.dumps(plugin.get("formats", []))
        daws_json = json.dumps(plugin.get("daws", []))
        os_json = json.dumps(plugin.get("os", []))
        tags_json = json.dumps(plugin.get("tags", []))
        is_free = 1 if plugin.get("price_type") == "free" else 0
        price_type = plugin.get("price_type", "paid")
        year = plugin.get("year")
        website = plugin.get("url")
        image_url = plugin.get("image_url")
        cur.execute(
            """INSERT INTO plugins
               (slug, name, manufacturer_id, category, subcategory, formats, daws, os,
                description, website, image_url, is_free, price_type, tags, year)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                plugin["slug"],
                plugin["name"],
                mfr_id,
                plugin.get("category", "effect"),
                plugin.get("subcategory"),
                formats_json,
                daws_json,
                os_json,
                plugin.get("description"),
                website,
                image_url,
                is_free,
                price_type,
                tags_json,
                year,
            ),
        )
        plugin_id = cur.lastrowid

        # Aliases
        for alias in plugin.get("aliases", []):
            cur.execute(
                "INSERT INTO aliases (plugin_id, name, name_lower) VALUES (?, ?, ?)",
                (plugin_id, alias, alias.lower()),
            )
            alias_count += 1

        # FTS entry
        aliases_text = " | ".join(plugin.get("aliases", []))
        tags_text = " ".join(plugin.get("tags", []))
        mfr_name = next(
            (m["name"] for m in data.get("manufacturers", []) if m["slug"] == mfr_slug),
            "",
        )
        cur.execute(
            "INSERT INTO plugins_fts (rowid, name, manufacturer_name, category, subcategory, description, aliases, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                plugin_id,
                plugin["name"],
                mfr_name,
                plugin.get("category", ""),
                plugin.get("subcategory", ""),
                plugin.get("description", ""),
                aliases_text,
                tags_text,
            ),
        )
        plugin_count += 1

    # Store seed metadata
    import hashlib
    import datetime
    seed_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:12]
    cur.execute("DELETE FROM metadata")
    cur.execute("INSERT INTO metadata (key, value) VALUES (?, ?)", ("seed_hash", seed_hash))
    cur.execute("INSERT INTO metadata (key, value) VALUES (?, ?)", ("seed_timestamp", datetime.datetime.now(datetime.UTC).isoformat()))

    conn.commit()
    return {
        "manufacturers": len(mfr_id_map),
        "plugins": plugin_count,
        "aliases": alias_count,
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI: seed the database from data/seed.json.

    Usage:
        python -m plugindb.seed              # Seed the database
        python -m plugindb.seed --validate   # Validate only (no seeding)
    """
    validate_only = "--validate" in sys.argv

    seed_path = Path(__file__).resolve().parent.parent / "data" / "seed.json"
    if not seed_path.exists():
        print(f"Error: seed file not found at {seed_path}")
        print("Run transform_registry() first to generate it.")
        sys.exit(1)

    data = load_seed(seed_path)

    if validate_only:
        errors = validate_seed(data)
        if errors:
            print(f"VALIDATION FAILED ({len(errors)} errors):")
            for e in errors:
                print(f"  - {e}")
            sys.exit(1)
        else:
            mfr_count = len(data.get("manufacturers", []))
            plugin_count = len(data.get("plugins", []))
            print(f"seed.json is valid: {mfr_count} manufacturers, {plugin_count} plugins")
            sys.exit(0)

    conn = get_connection(DEFAULT_DB_PATH)

    # Auto-migrate: detect stale schema and drop/recreate
    if not check_schema(conn):
        print("Schema change detected — rebuilding database...")
        conn.execute("DROP TABLE IF EXISTS plugins_fts")
        conn.execute("DROP TABLE IF EXISTS aliases")
        conn.execute("DROP TABLE IF EXISTS plugins")
        conn.execute("DROP TABLE IF EXISTS manufacturers")
        conn.commit()

    create_schema(conn)
    counts = seed_database(conn, data)
    conn.close()

    print(f"Seeded database at {DEFAULT_DB_PATH}:")
    print(f"  {counts['manufacturers']} manufacturers")
    print(f"  {counts['plugins']} plugins")
    print(f"  {counts['aliases']} aliases")


if __name__ == "__main__":
    main()
