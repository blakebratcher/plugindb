"""Browse routes — paginated plugin listing and detail."""

from __future__ import annotations

import math

from fastapi import APIRouter, HTTPException, Query

from plugindb.main import get_db
from plugindb.models import (
    PaginatedResponse,
    PluginListResponse,
    PluginResponse,
)
from plugindb.queries import build_plugin_response

router = APIRouter(tags=["plugins"])


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/plugins", response_model=PluginListResponse)
def list_plugins(
    page: int = Query(1, description="Page number (starting at 1)"),
    per_page: int = Query(50, description="Results per page (1-200)"),
    category: str | None = Query(None, description="Filter by category (exact match)"),
    manufacturer: str | None = Query(None, description="Filter by manufacturer slug"),
    format: str | None = Query(None, description="Filter by format (LIKE match on JSON)"),
    daw: str | None = Query(None, description="Filter by DAW compatibility (LIKE match)"),
    price_type: str | None = Query(None, description="Filter by price type: free or paid"),
) -> PluginListResponse:
    """List all plugins with optional filters, paginated."""
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")

    # Clamp per_page to 1-200
    per_page = max(1, min(200, per_page))

    conn = get_db()

    # Build query dynamically
    where_clauses: list[str] = []
    params: list[object] = []

    if category is not None:
        where_clauses.append("p.category = ?")
        params.append(category)

    if manufacturer is not None:
        where_clauses.append("m.slug = ?")
        params.append(manufacturer)

    if format is not None:
        where_clauses.append("p.formats LIKE ?")
        params.append(f"%{format}%")

    if daw is not None:
        # DAW compatibility stored in formats or description — LIKE match
        where_clauses.append("p.formats LIKE ?")
        params.append(f"%{daw}%")

    if price_type is not None:
        if price_type == "free":
            where_clauses.append("p.is_free = 1")
        elif price_type == "paid":
            where_clauses.append("p.is_free = 0")

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    # Count total matching rows
    count_sql = f"""
        SELECT COUNT(*) FROM plugins p
        JOIN manufacturers m ON p.manufacturer_id = m.id
        {where_sql}
    """
    total = conn.execute(count_sql, params).fetchone()[0]
    pages = math.ceil(total / per_page) if total > 0 else 0

    # Fetch page
    offset = (page - 1) * per_page
    query_sql = f"""
        SELECT p.* FROM plugins p
        JOIN manufacturers m ON p.manufacturer_id = m.id
        {where_sql}
        ORDER BY p.name ASC
        LIMIT ? OFFSET ?
    """
    rows = conn.execute(query_sql, [*params, per_page, offset]).fetchall()

    data = [build_plugin_response(row, conn) for row in rows]

    return PluginListResponse(
        data=data,
        total=total,
        pagination=PaginatedResponse(
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
        ),
    )


@router.get("/plugins/{plugin_id}", response_model=PluginResponse)
def get_plugin(plugin_id: int) -> PluginResponse:
    """Get a single plugin by its database ID."""
    conn = get_db()
    row = conn.execute("SELECT * FROM plugins WHERE id = ?", (plugin_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Plugin with id {plugin_id} not found")
    return build_plugin_response(row, conn)
