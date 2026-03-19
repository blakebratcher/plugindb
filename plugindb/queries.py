"""Shared database query helpers."""

from __future__ import annotations

import json
import sqlite3

from plugindb.models import ManufacturerResponse, PluginResponse


def build_plugin_response(row: sqlite3.Row, conn: sqlite3.Connection) -> PluginResponse:
    """Construct a full PluginResponse from a plugins DB row.

    Joins the manufacturer record and loads all aliases for the plugin.
    Parses the JSON-encoded ``formats`` column.
    """
    plugin_id: int = row["id"]

    # Manufacturer
    mfr_row = conn.execute(
        "SELECT id, slug, name, website, created_at FROM manufacturers WHERE id = ?",
        (row["manufacturer_id"],),
    ).fetchone()
    manufacturer = ManufacturerResponse(
        id=mfr_row["id"],
        slug=mfr_row["slug"],
        name=mfr_row["name"],
        website=mfr_row["website"],
        created_at=mfr_row["created_at"],
    )

    # Aliases
    alias_rows = conn.execute(
        "SELECT name FROM aliases WHERE plugin_id = ? ORDER BY name",
        (plugin_id,),
    ).fetchall()
    aliases = [a["name"] for a in alias_rows]

    # JSON array columns
    formats = json.loads(row["formats"]) if row["formats"] else []
    daws = json.loads(row["daws"]) if row["daws"] else []
    os_list = json.loads(row["os"]) if row["os"] else []

    return PluginResponse(
        id=row["id"],
        slug=row["slug"],
        name=row["name"],
        manufacturer=manufacturer,
        category=row["category"],
        subcategory=row["subcategory"],
        formats=formats,
        daws=daws,
        os=os_list,
        aliases=aliases,
        description=row["description"],
        website=row["website"],
        is_free=bool(row["is_free"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
