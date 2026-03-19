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
    ErrorResponse,
    PluginResponse,
)
from plugindb.queries import build_plugin_response, build_plugin_responses

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
        404: {"model": ErrorResponse, "description": "No plugin matching this alias"},
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

    Accepts up to 200 names and returns match results for each.
    Uses bulk queries for efficient alias resolution.
    """
    conn = get_db()

    # 1. Collect all lowercased names
    lower_names = [name.lower() for name in body.names]

    # 2. Single query: resolve all aliases at once
    placeholders = ",".join("?" for _ in lower_names)
    alias_rows = conn.execute(
        f"SELECT name_lower, plugin_id FROM aliases WHERE name_lower IN ({placeholders})",
        lower_names,
    ).fetchall()

    # Build mapping: name_lower -> plugin_id (first match wins)
    alias_to_plugin_id: dict[str, int] = {}
    for row in alias_rows:
        if row["name_lower"] not in alias_to_plugin_id:
            alias_to_plugin_id[row["name_lower"]] = row["plugin_id"]

    # 3. Get unique plugin_ids from matches
    unique_plugin_ids = list(set(alias_to_plugin_id.values()))

    # 4. Single query: fetch all matched plugins at once
    plugin_map: dict[int, PluginResponse] = {}
    if unique_plugin_ids:
        pid_placeholders = ",".join("?" for _ in unique_plugin_ids)
        plugin_rows = conn.execute(
            f"SELECT * FROM plugins WHERE id IN ({pid_placeholders})",
            unique_plugin_ids,
        ).fetchall()

        # 5. Batch-build all matched plugin responses
        plugin_responses = build_plugin_responses(list(plugin_rows), conn)
        plugin_map = {p.id: p for p in plugin_responses}

    # 6. Map results back to original query names
    results: list[BatchLookupMatch] = []
    matched = 0
    unmatched = 0

    for name in body.names:
        plugin_id = alias_to_plugin_id.get(name.lower())
        plugin = plugin_map.get(plugin_id) if plugin_id is not None else None
        if plugin is not None:
            results.append(BatchLookupMatch(query=name, matched=True, plugin=plugin))
            matched += 1
        else:
            results.append(BatchLookupMatch(query=name, matched=False, plugin=None))
            unmatched += 1

    # Detect duplicates: queries that resolved to the same plugin
    seen_ids: dict[int, list[str]] = {}
    for r in results:
        if r.matched and r.plugin is not None:
            seen_ids.setdefault(r.plugin.id, []).append(r.query)
    duplicates = [q for names in seen_ids.values() if len(names) > 1 for q in names]

    return BatchLookupResponse(results=results, matched=matched, unmatched=unmatched, duplicates=duplicates)
