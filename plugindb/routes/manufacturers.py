"""Manufacturer browse routes — list and detail with full plugin catalogs."""

from __future__ import annotations

import math

from fastapi import APIRouter, HTTPException, Query

from plugindb.main import get_db
from plugindb.models import (
    ErrorResponse,
    ManufacturerDetailResponse,
    ManufacturerListResponse,
    ManufacturerResponse,
    ManufacturerWithCountResponse,
    PaginatedResponse,
    PluginResponse,
)
from plugindb.queries import build_plugin_responses

router = APIRouter(tags=["manufacturers"])


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/manufacturers", response_model=ManufacturerListResponse)
def list_manufacturers(
    page: int = Query(1, description="Page number (starting at 1)"),
    per_page: int = Query(50, description="Results per page (1-200)"),
    search: str | None = Query(None, description="Search by name (case-insensitive)"),
    sort: str | None = Query(None, description="Sort field: name, plugin_count"),
    order: str | None = Query(None, description="Sort direction: asc, desc"),
) -> ManufacturerListResponse:
    """List all manufacturers with plugin counts, paginated."""
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")

    per_page = max(1, min(200, per_page))
    conn = get_db()

    where_clause = ""
    params: list[object] = []
    if search:
        where_clause = "WHERE m.name LIKE ?"
        params.append(f"%{search}%")

    # Sorting
    sort_fields = {"name": "m.name", "plugin_count": "plugin_count"}
    sort_col = sort_fields.get(sort, "m.name")
    sort_dir = "DESC" if order and order.lower() == "desc" else "ASC"

    total = conn.execute(
        f"SELECT COUNT(*) FROM manufacturers m {where_clause}", params
    ).fetchone()[0]
    pages = math.ceil(total / per_page) if total > 0 else 0

    offset = (page - 1) * per_page
    rows = conn.execute(
        f"""SELECT m.*, COUNT(p.id) as plugin_count
            FROM manufacturers m
            LEFT JOIN plugins p ON p.manufacturer_id = m.id
            {where_clause}
            GROUP BY m.id
            ORDER BY {sort_col} {sort_dir}
            LIMIT ? OFFSET ?""",
        [*params, per_page, offset],
    ).fetchall()

    data = [
        ManufacturerWithCountResponse(
            id=row["id"],
            slug=row["slug"],
            name=row["name"],
            website=row["website"],
            created_at=row["created_at"],
            plugin_count=row["plugin_count"],
        )
        for row in rows
    ]

    return ManufacturerListResponse(
        data=data,
        pagination=PaginatedResponse(
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
        ),
    )


@router.get("/manufacturers/{slug}", response_model=ManufacturerDetailResponse, responses={404: {"model": ErrorResponse}})
def get_manufacturer(
    slug: str,
    page: int = Query(1, description="Page number for plugins"),
    per_page: int = Query(50, description="Plugins per page (1-200)"),
) -> ManufacturerDetailResponse:
    """Get a manufacturer by slug with paginated plugin catalog."""
    conn = get_db()

    mfr_row = conn.execute(
        "SELECT * FROM manufacturers WHERE slug = ?", (slug,)
    ).fetchone()
    if mfr_row is None:
        raise HTTPException(
            status_code=404, detail=f"Manufacturer '{slug}' not found"
        )

    manufacturer = ManufacturerResponse(
        id=mfr_row["id"],
        slug=mfr_row["slug"],
        name=mfr_row["name"],
        website=mfr_row["website"],
        created_at=mfr_row["created_at"],
    )

    per_page = max(1, min(200, per_page))
    total = conn.execute(
        "SELECT COUNT(*) FROM plugins WHERE manufacturer_id = ?",
        (mfr_row["id"],),
    ).fetchone()[0]
    pages = math.ceil(total / per_page) if total > 0 else 0

    offset = (page - 1) * per_page
    plugin_rows = conn.execute(
        "SELECT * FROM plugins WHERE manufacturer_id = ? ORDER BY name ASC LIMIT ? OFFSET ?",
        (mfr_row["id"], per_page, offset),
    ).fetchall()

    plugins: list[PluginResponse] = build_plugin_responses(plugin_rows, conn)

    # Category breakdown for this manufacturer
    cat_rows = conn.execute(
        "SELECT category, COUNT(*) as cnt FROM plugins WHERE manufacturer_id = ? GROUP BY category",
        (mfr_row["id"],),
    ).fetchall()
    categories = {row["category"]: row["cnt"] for row in cat_rows}

    return ManufacturerDetailResponse(
        manufacturer=manufacturer,
        plugins=plugins,
        plugin_count=total,
        categories=categories,
        pagination=PaginatedResponse(
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
        ),
    )
