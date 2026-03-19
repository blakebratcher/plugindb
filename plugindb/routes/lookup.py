"""Lookup routes — the killer feature of PluginDB.

Provides instant case-insensitive alias resolution for plugin names.
"""

from __future__ import annotations

import json
import sqlite3

from fastapi import APIRouter, HTTPException, Query

from plugindb.main import get_db
from plugindb.models import (
    BatchLookupMatch,
    BatchLookupRequest,
    BatchLookupResponse,
    ManufacturerResponse,
    PluginResponse,
)

router = APIRouter(tags=["lookup"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_plugin_response(row: sqlite3.Row, conn: sqlite3.Connection) -> PluginResponse:
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

    # Formats (stored as JSON array)
    formats = json.loads(row["formats"]) if row["formats"] else []

    return PluginResponse(
        id=row["id"],
        slug=row["slug"],
        name=row["name"],
        manufacturer=manufacturer,
        category=row["category"],
        subcategory=row["subcategory"],
        formats=formats,
        aliases=aliases,
        description=row["description"],
        website=row["website"],
        is_free=bool(row["is_free"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _lookup_alias(alias: str, conn: sqlite3.Connection) -> PluginResponse | None:
    """Look up a single alias (case-insensitive). Returns None if not found."""
    alias_row = conn.execute(
        "SELECT plugin_id FROM aliases WHERE name_lower = ? LIMIT 1",
        (alias.lower(),),
    ).fetchone()
    if alias_row is None:
        return None

    plugin_row = conn.execute(
        "SELECT * FROM plugins WHERE id = ?",
        (alias_row["plugin_id"],),
    ).fetchone()
    if plugin_row is None:
        return None

    return _build_plugin_response(plugin_row, conn)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/lookup", response_model=PluginResponse)
def lookup_plugin(
    alias: str = Query(..., description="Plugin name or alias to look up"),
) -> PluginResponse:
    """Look up a plugin by name or alias (case-insensitive).

    Returns the full plugin record if a match is found, or 404 otherwise.
    """
    conn = get_db()
    result = _lookup_alias(alias, conn)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No plugin found for alias '{alias}'")
    return result


@router.post("/lookup", response_model=BatchLookupResponse)
def batch_lookup(body: BatchLookupRequest) -> BatchLookupResponse:
    """Look up multiple plugins by name/alias in a single request.

    Accepts up to 100 names and returns match results for each.
    """
    conn = get_db()
    results: list[BatchLookupMatch] = []
    matched = 0
    unmatched = 0

    for name in body.names:
        plugin = _lookup_alias(name, conn)
        if plugin is not None:
            results.append(BatchLookupMatch(query=name, matched=True, plugin=plugin))
            matched += 1
        else:
            results.append(BatchLookupMatch(query=name, matched=False, plugin=None))
            unmatched += 1

    return BatchLookupResponse(results=results, matched=matched, unmatched=unmatched)
