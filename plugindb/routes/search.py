"""Search routes — FTS5 full-text search across the plugin database."""

from __future__ import annotations

import json as _json
import logging
import math
import re
import sqlite3

_logger = logging.getLogger("plugindb")

from fastapi import APIRouter, HTTPException, Query

from plugindb.main import get_db
from plugindb.models import (
    ErrorResponse,
    PaginatedResponse,
    PluginListResponse,
    SuggestItemResponse,
    SuggestResponse,
)
from plugindb.queries import build_plugin_responses

router = APIRouter(tags=["search"])


# ---------------------------------------------------------------------------
# FTS5 query sanitisation
# ---------------------------------------------------------------------------

def _sanitize_fts_query(q: str) -> str:
    """Escape user input for safe FTS5 MATCH queries.

    Removes FTS5 special operators and characters, then wraps the remaining
    text in double-quotes so it is treated as a literal phrase.  A trailing
    ``*`` is appended for prefix matching.
    """
    # Remove FTS5 special operators and characters
    cleaned = re.sub(r'[*"{}()\[\]]', '', q.strip())
    # Quote the entire string to prevent operator interpretation
    if cleaned:
        return f'"{cleaned}"' + '*'  # prefix match on quoted string
    return '""'


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/search", response_model=PluginListResponse, responses={400: {"model": ErrorResponse}})
def search_plugins(
    q: str = Query(..., description="Search query (minimum 2 characters)"),
    category: str | None = Query(None, description="Filter by category"),
    subcategory: str | None = Query(None, description="Filter by subcategory"),
    manufacturer: str | None = Query(None, description="Filter by manufacturer slug"),
    tag: str | None = Query(None, description="Filter by tag"),
    os: str | None = Query(None, description="Filter by OS (LIKE match on JSON)"),
    year: int | None = Query(None, description="Filter by release year"),
    year_min: int | None = Query(None, description="Minimum release year (inclusive)"),
    year_max: int | None = Query(None, description="Maximum release year (inclusive)"),
    price_type: str | None = Query(None, description="Filter by price type"),
    format: str | None = Query(None, description="Filter by format (LIKE match on JSON)"),
    daw: str | None = Query(None, description="Filter by DAW compatibility (LIKE match)"),
    sort: str | None = Query(None, description="Sort: relevance (default), name, year, created_at"),
    order: str | None = Query(None, description="Sort direction: asc, desc"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
) -> PluginListResponse:
    """Full-text search across plugins using FTS5.

    Searches plugin names, manufacturer names, categories, subcategories,
    descriptions, aliases, and tags. Supports prefix matching. Results are
    ordered by relevance (FTS5 rank).
    """
    if len(q.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Search query must be at least 2 characters",
        )

    conn = get_db()

    # Sanitise user input for FTS5
    fts_query = _sanitize_fts_query(q)

    # Build dynamic WHERE clause
    where_parts = ["plugins_fts MATCH ?"]
    params: list[object] = [fts_query]

    if category:
        where_parts.append("plugins.category = ?")
        params.append(category)
    if subcategory:
        where_parts.append("plugins.subcategory = ?")
        params.append(subcategory)
    if manufacturer:
        where_parts.append("plugins.manufacturer_id = (SELECT id FROM manufacturers WHERE slug = ?)")
        params.append(manufacturer)
    if tag:
        where_parts.append("plugins.tags LIKE ?")
        params.append(f'%"{tag}"%')
    if year is not None:
        where_parts.append("plugins.year = ?")
        params.append(year)
    if year_min is not None:
        where_parts.append("plugins.year >= ?")
        params.append(year_min)
    if year_max is not None:
        where_parts.append("plugins.year <= ?")
        params.append(year_max)
    if price_type:
        where_parts.append("plugins.price_type = ?")
        params.append(price_type)
    if format:
        where_parts.append("plugins.formats LIKE ?")
        params.append(f'%"{format}"%')
    if daw:
        where_parts.append("plugins.daws LIKE ?")
        params.append(f'%"{daw}"%')
    if os:
        where_parts.append("plugins.os LIKE ?")
        params.append(f'%"{os}"%')

    where_sql = " AND ".join(where_parts)

    # Sorting
    sort_fields = {"name": "plugins.name", "year": "plugins.year", "created_at": "plugins.created_at"}
    if sort and sort in sort_fields:
        sort_col = sort_fields[sort]
        sort_dir = "DESC" if order and order.lower() == "desc" else "ASC"
        order_sql = f"ORDER BY {sort_col} {sort_dir}"
    else:
        order_sql = "ORDER BY plugins_fts.rank"

    try:
        count_row = conn.execute(
            f"""SELECT COUNT(*) FROM plugins_fts
                JOIN plugins ON plugins.rowid = plugins_fts.rowid
                WHERE {where_sql}""",
            params,
        ).fetchone()
        total = count_row[0]

        offset = (page - 1) * per_page
        rows = conn.execute(
            f"""SELECT plugins.* FROM plugins_fts
                JOIN plugins ON plugins.rowid = plugins_fts.rowid
                WHERE {where_sql}
                {order_sql}
                LIMIT ? OFFSET ?""",
            [*params, per_page, offset],
        ).fetchall()
    except sqlite3.OperationalError as fts_err:
        _logger.warning("FTS query failed, falling back to LIKE search: %s", fts_err)
        try:
            like_pattern = f"%{q.strip()}%"
            like_where = ["(plugins.name LIKE ? OR plugins.description LIKE ?)"]
            like_params: list[object] = [like_pattern, like_pattern]

            if category:
                like_where.append("plugins.category = ?")
                like_params.append(category)
            if subcategory:
                like_where.append("plugins.subcategory = ?")
                like_params.append(subcategory)
            if manufacturer:
                like_where.append("plugins.manufacturer_id = (SELECT id FROM manufacturers WHERE slug = ?)")
                like_params.append(manufacturer)
            if tag:
                like_where.append("plugins.tags LIKE ?")
                like_params.append(f'%"{tag}"%')
            if year is not None:
                like_where.append("plugins.year = ?")
                like_params.append(year)
            if year_min is not None:
                like_where.append("plugins.year >= ?")
                like_params.append(year_min)
            if year_max is not None:
                like_where.append("plugins.year <= ?")
                like_params.append(year_max)
            if price_type:
                like_where.append("plugins.price_type = ?")
                like_params.append(price_type)
            if format:
                like_where.append("plugins.formats LIKE ?")
                like_params.append(f'%"{format}"%')
            if daw:
                like_where.append("plugins.daws LIKE ?")
                like_params.append(f'%"{daw}"%')
            if os:
                like_where.append("plugins.os LIKE ?")
                like_params.append(f'%"{os}"%')

            like_where_sql = " AND ".join(like_where)
            offset = (page - 1) * per_page

            count_row = conn.execute(
                f"SELECT COUNT(*) FROM plugins WHERE {like_where_sql}",
                like_params,
            ).fetchone()
            total = count_row[0]

            rows = conn.execute(
                f"SELECT * FROM plugins WHERE {like_where_sql} ORDER BY name ASC LIMIT ? OFFSET ?",
                [*like_params, per_page, offset],
            ).fetchall()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_query",
                    "message": f"Search query '{q}' could not be processed",
                },
            )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_query",
                "message": f"Search query '{q}' could not be processed",
            },
        )

    plugins = build_plugin_responses(rows, conn)
    pages = math.ceil(total / per_page) if total > 0 else 0

    # Log search query for analytics (non-blocking)
    try:
        filters = {k: v for k, v in {
            "category": category, "subcategory": subcategory, "manufacturer": manufacturer,
            "tag": tag, "os": os, "format": format, "daw": daw,
            "price_type": price_type, "year": year, "sort": sort,
        }.items() if v}
        conn.execute(
            "INSERT INTO search_log (query, results_count, filters) VALUES (?, ?, ?)",
            (q, total, _json.dumps(filters) if filters else None),
        )
        conn.commit()
    except Exception:
        pass  # Never let analytics break search

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


@router.get("/suggest", response_model=SuggestResponse)
def suggest_plugins(
    q: str = Query(..., min_length=1, description="Autocomplete query (min 1 char)"),
) -> SuggestResponse:
    """Lightweight autocomplete — returns up to 10 plugin names matching the query."""
    conn = get_db()
    fts_query = _sanitize_fts_query(q)

    try:
        rows = conn.execute(
            """SELECT DISTINCT plugins.name, plugins.slug, plugins.category, plugins.image_url, m.name as manufacturer_name
               FROM plugins_fts
               JOIN plugins ON plugins.rowid = plugins_fts.rowid
               JOIN manufacturers m ON plugins.manufacturer_id = m.id
               WHERE plugins_fts MATCH ?
               ORDER BY plugins_fts.rank
               LIMIT 10""",
            (fts_query,),
        ).fetchall()
    except Exception:
        rows = []

    results = [
        SuggestItemResponse(
            name=row["name"],
            slug=row["slug"],
            category=row["category"],
            manufacturer_name=row["manufacturer_name"],
            image_url=row["image_url"],
        )
        for row in rows
    ]

    return SuggestResponse(
        suggestions=[r.name for r in results],
        results=results,
        query=q,
    )
