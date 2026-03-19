"""Lookup routes — the killer feature of PluginDB.

Provides instant case-insensitive alias resolution for plugin names.
"""

from __future__ import annotations

import sqlite3

from fastapi import APIRouter, HTTPException, Query

from plugindb.main import get_db
from plugindb.models import (
    BatchLookupMatch,
    BatchLookupRequest,
    BatchLookupResponse,
    PluginResponse,
)
from plugindb.queries import build_plugin_response

router = APIRouter(tags=["lookup"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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

    return build_plugin_response(plugin_row, conn)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get(
    "/lookup",
    response_model=PluginResponse,
    responses={
        200: {"description": "Plugin found"},
        404: {"description": "No plugin matching this alias"},
    },
)
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
