"""SQLite database schema and connection management for PluginDB."""

from __future__ import annotations

import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "plugindb.sqlite"


def get_connection(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open a SQLite connection with WAL mode and foreign keys enabled.

    Returns a connection with row_factory set to sqlite3.Row for
    dict-like access to query results.
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """Create all tables and indexes if they don't already exist.

    Tables:
        manufacturers — plugin makers (e.g. "u-he", "Xfer Records")
        plugins       — individual plugin entries with category/format metadata
        aliases       — alternative names for fuzzy/case-insensitive lookup
        plugins_fts   — FTS5 virtual table for full-text search across plugins
    """
    conn.executescript("""
        -- Manufacturers
        CREATE TABLE IF NOT EXISTS manufacturers (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            slug        TEXT    NOT NULL UNIQUE,
            name        TEXT    NOT NULL,
            website     TEXT,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        -- Plugins
        CREATE TABLE IF NOT EXISTS plugins (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            slug            TEXT    NOT NULL UNIQUE,
            name            TEXT    NOT NULL,
            manufacturer_id INTEGER NOT NULL REFERENCES manufacturers(id),
            category        TEXT    NOT NULL DEFAULT 'effect',
            subcategory     TEXT,
            formats         TEXT    NOT NULL DEFAULT '[]',
            description     TEXT,
            website         TEXT,
            is_free         INTEGER NOT NULL DEFAULT 0,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_plugins_manufacturer
            ON plugins(manufacturer_id);
        CREATE INDEX IF NOT EXISTS idx_plugins_category
            ON plugins(category);
        CREATE INDEX IF NOT EXISTS idx_plugins_slug
            ON plugins(slug);

        -- Aliases (alternative names for lookup)
        CREATE TABLE IF NOT EXISTS aliases (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            plugin_id INTEGER NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
            name      TEXT    NOT NULL,
            name_lower TEXT   NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_aliases_name_lower
            ON aliases(name_lower);
        CREATE INDEX IF NOT EXISTS idx_aliases_plugin_id
            ON aliases(plugin_id);

        -- Full-text search
        CREATE VIRTUAL TABLE IF NOT EXISTS plugins_fts USING fts5(
            name,
            manufacturer_name,
            category,
            subcategory,
            description,
            aliases,
            content=''
        );
    """)
    conn.commit()
