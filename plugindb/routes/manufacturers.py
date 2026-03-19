"""Manufacturer browse routes — list and detail with full plugin catalogs."""

from __future__ import annotations

import math

from fastapi import APIRouter, HTTPException, Query

from plugindb.main import get_db
from plugindb.models import (
    ManufacturerDetailResponse,
    ManufacturerListResponse,
    ManufacturerResponse,
    PaginatedResponse,
    PluginResponse,
)
from plugindb.routes.lookup import _build_plugin_response

router = APIRouter(tags=["manufacturers"])


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/manufacturers", response_model=ManufacturerListResponse)
def list_manufacturers(
    page: int = Query(1, description="Page number (starting at 1)"),
    per_page: int = Query(50, description="Results per page (1-200)"),
) -> ManufacturerListResponse:
    """List all manufacturers, paginated."""
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")

    per_page = max(1, min(200, per_page))

    conn = get_db()

    total = conn.execute("SELECT COUNT(*) FROM manufacturers").fetchone()[0]
    pages = math.ceil(total / per_page) if total > 0 else 0

    offset = (page - 1) * per_page
    rows = conn.execute(
        "SELECT * FROM manufacturers ORDER BY name ASC LIMIT ? OFFSET ?",
        (per_page, offset),
    ).fetchall()

    data = [
        ManufacturerResponse(
            id=row["id"],
            slug=row["slug"],
            name=row["name"],
            website=row["website"],
            created_at=row["created_at"],
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


@router.get("/manufacturers/{slug}", response_model=ManufacturerDetailResponse)
def get_manufacturer(slug: str) -> ManufacturerDetailResponse:
    """Get a manufacturer by slug, including its full plugin catalog."""
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

    plugin_rows = conn.execute(
        "SELECT * FROM plugins WHERE manufacturer_id = ? ORDER BY name ASC",
        (mfr_row["id"],),
    ).fetchall()

    plugins: list[PluginResponse] = [
        _build_plugin_response(row, conn) for row in plugin_rows
    ]

    return ManufacturerDetailResponse(
        manufacturer=manufacturer,
        plugins=plugins,
        plugin_count=len(plugins),
    )
