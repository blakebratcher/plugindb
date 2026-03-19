"""Search routes — FTS5 full-text search across the plugin database."""

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

router = APIRouter(tags=["search"])


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/search", response_model=PluginListResponse)
def search_plugins(
    q: str = Query(..., description="Search query (minimum 2 characters)"),
    category: str | None = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
) -> PluginListResponse:
    """Full-text search across plugins using FTS5.

    Searches plugin names, manufacturer names, categories, subcategories,
    descriptions, and aliases. Supports prefix matching. Results are ordered
    by relevance (FTS5 rank).
    """
    if len(q.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Search query must be at least 2 characters",
        )

    conn = get_db()

    # FTS5 prefix match: append * for prefix matching
    fts_query = q.strip() + "*"

    # Build the query — join FTS results back to the plugins table
    if category:
        # Count total matches with category filter
        count_row = conn.execute(
            """SELECT COUNT(*) FROM plugins_fts
               JOIN plugins ON plugins.rowid = plugins_fts.rowid
               WHERE plugins_fts MATCH ? AND plugins.category = ?""",
            (fts_query, category),
        ).fetchone()
        total = count_row[0]

        # Fetch paginated results
        offset = (page - 1) * per_page
        rows = conn.execute(
            """SELECT plugins.* FROM plugins_fts
               JOIN plugins ON plugins.rowid = plugins_fts.rowid
               WHERE plugins_fts MATCH ? AND plugins.category = ?
               ORDER BY plugins_fts.rank
               LIMIT ? OFFSET ?""",
            (fts_query, category, per_page, offset),
        ).fetchall()
    else:
        # Count total matches without category filter
        count_row = conn.execute(
            """SELECT COUNT(*) FROM plugins_fts
               JOIN plugins ON plugins.rowid = plugins_fts.rowid
               WHERE plugins_fts MATCH ?""",
            (fts_query,),
        ).fetchone()
        total = count_row[0]

        # Fetch paginated results
        offset = (page - 1) * per_page
        rows = conn.execute(
            """SELECT plugins.* FROM plugins_fts
               JOIN plugins ON plugins.rowid = plugins_fts.rowid
               WHERE plugins_fts MATCH ?
               ORDER BY plugins_fts.rank
               LIMIT ? OFFSET ?""",
            (fts_query, per_page, offset),
        ).fetchall()

    plugins = [build_plugin_response(row, conn) for row in rows]
    pages = math.ceil(total / per_page) if total > 0 else 0

    return PluginListResponse(
        data=plugins,
        total=total,
        pagination=PaginatedResponse(
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
        ),
    )
