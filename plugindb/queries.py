"""Shared database query helpers."""

from __future__ import annotations

import json
import sqlite3

from plugindb.models import ManufacturerCompactResponse, ManufacturerResponse, PluginCompactResponse, PluginResponse

# Load IA archive map once — maps slug to archive.org URL
_archive_map: dict[str, str] = {}
try:
    from pathlib import Path as _Path
    _archive_path = _Path(__file__).resolve().parent.parent / "data" / "image_archive.json"
    if _archive_path.exists():
        _archive_map = json.loads(_archive_path.read_text(encoding="utf-8"))
except Exception:
    pass


def _resolve_image_url(slug: str, source_url: str | None) -> str | None:
    """Return the best image URL — IA if available, otherwise source."""
    return _archive_map.get(slug) or source_url


def _row_to_plugin(
    row: sqlite3.Row,
    manufacturer: ManufacturerResponse,
    aliases: list[str],
) -> PluginResponse:
    """Assemble a PluginResponse from pre-fetched components."""
    formats = json.loads(row["formats"]) if row["formats"] else []
    daws = json.loads(row["daws"]) if row["daws"] else []
    os_list = json.loads(row["os"]) if row["os"] else []
    tags = json.loads(row["tags"]) if row["tags"] else []

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
        tags=tags,
        description=row["description"],
        website=row["website"],
        image_url=_resolve_image_url(row["slug"], row["image_url"]),
        manual_url=row["manual_url"],
        video_url=row["video_url"],
        is_free=bool(row["is_free"]),
        price_type=row["price_type"],
        year=row["year"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def build_plugin_response(row: sqlite3.Row, conn: sqlite3.Connection) -> PluginResponse:
    """Construct a full PluginResponse from a single plugins DB row.

    Runs 2 extra queries (manufacturer + aliases). Use ``build_plugin_responses``
    for batch operations to avoid N+1.
    """
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

    alias_rows = conn.execute(
        "SELECT name FROM aliases WHERE plugin_id = ? ORDER BY name",
        (row["id"],),
    ).fetchall()
    aliases = [a["name"] for a in alias_rows]

    return _row_to_plugin(row, manufacturer, aliases)


def build_plugin_responses(rows: list[sqlite3.Row], conn: sqlite3.Connection) -> list[PluginResponse]:
    """Batch-construct PluginResponses — 3 queries total regardless of page size.

    Prefetches all referenced manufacturers and aliases in bulk, then assembles.
    """
    if not rows:
        return []

    # Collect unique manufacturer IDs and all plugin IDs
    mfr_ids = list({row["manufacturer_id"] for row in rows})
    plugin_ids = [row["id"] for row in rows]

    # Batch-load manufacturers (1 query)
    placeholders = ",".join("?" for _ in mfr_ids)
    mfr_rows = conn.execute(
        f"SELECT id, slug, name, website, created_at FROM manufacturers WHERE id IN ({placeholders})",
        mfr_ids,
    ).fetchall()
    mfr_map: dict[int, ManufacturerResponse] = {
        r["id"]: ManufacturerResponse(
            id=r["id"], slug=r["slug"], name=r["name"],
            website=r["website"], created_at=r["created_at"],
        )
        for r in mfr_rows
    }

    # Batch-load aliases (1 query)
    placeholders = ",".join("?" for _ in plugin_ids)
    alias_rows = conn.execute(
        f"SELECT plugin_id, name FROM aliases WHERE plugin_id IN ({placeholders}) ORDER BY plugin_id, name",
        plugin_ids,
    ).fetchall()
    alias_map: dict[int, list[str]] = {}
    for a in alias_rows:
        alias_map.setdefault(a["plugin_id"], []).append(a["name"])

    # Assemble responses
    return [
        _row_to_plugin(row, mfr_map[row["manufacturer_id"]], alias_map.get(row["id"], []))
        for row in rows
    ]


def build_compact_responses(rows: list[sqlite3.Row], conn: sqlite3.Connection) -> list[PluginCompactResponse]:
    """Build compact plugin responses for list views — 1 query (manufacturers only, no aliases)."""
    if not rows:
        return []

    mfr_ids = list({row["manufacturer_id"] for row in rows})
    placeholders = ",".join("?" for _ in mfr_ids)
    mfr_rows = conn.execute(
        f"SELECT id, slug, name, website, created_at FROM manufacturers WHERE id IN ({placeholders})",
        mfr_ids,
    ).fetchall()
    mfr_map = {
        r["id"]: ManufacturerResponse(
            id=r["id"], slug=r["slug"], name=r["name"],
            website=r["website"], created_at=r["created_at"],
        )
        for r in mfr_rows
    }

    return [
        PluginCompactResponse(
            slug=row["slug"],
            name=row["name"],
            manufacturer=ManufacturerCompactResponse(
                slug=mfr_map[row["manufacturer_id"]].slug,
                name=mfr_map[row["manufacturer_id"]].name,
            ),
            category=row["category"],
            subcategory=row["subcategory"],
            image_url=_resolve_image_url(row["slug"], row["image_url"]),
            year=row["year"],
        )
        for row in rows
    ]
