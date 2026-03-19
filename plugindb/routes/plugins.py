"""Browse routes — paginated plugin listing, detail, and similar plugins."""

from __future__ import annotations

import json
import math

from fastapi import APIRouter, HTTPException, Query

from plugindb.main import get_db
from plugindb.models import (
    ComparisonResponse,
    ErrorResponse,
    PaginatedResponse,
    PluginListResponse,
    PluginResponse,
)
from plugindb.queries import build_plugin_response, build_plugin_responses

router = APIRouter(tags=["plugins"])


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/plugins", response_model=PluginListResponse)
def list_plugins(
    page: int = Query(1, description="Page number (starting at 1)"),
    per_page: int = Query(50, description="Results per page (1-200)"),
    category: str | None = Query(None, description="Filter by category (exact match)"),
    subcategory: str | None = Query(None, description="Filter by subcategory (exact match)"),
    manufacturer: str | None = Query(None, description="Filter by manufacturer slug"),
    format: str | None = Query(None, description="Filter by format (LIKE match on JSON)"),
    daw: str | None = Query(None, description="Filter by DAW compatibility (LIKE match)"),
    os: str | None = Query(None, description="Filter by OS (LIKE match on JSON)"),
    price_type: str | None = Query(None, description="Filter by price type (free, paid, freemium, etc.)"),
    tag: str | None = Query(None, description="Filter by tag (LIKE match on JSON)"),
    tags: str | None = Query(None, description="Filter by multiple tags (comma-separated, AND logic)"),
    year: int | None = Query(None, description="Filter by release year (exact match)"),
    year_min: int | None = Query(None, description="Minimum release year (inclusive)"),
    year_max: int | None = Query(None, description="Maximum release year (inclusive)"),
    sort: str | None = Query(None, description="Sort field: name, year, created_at"),
    order: str | None = Query(None, description="Sort direction: asc, desc"),
) -> PluginListResponse:
    """List all plugins with optional filters, paginated."""
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")

    # Clamp per_page to 1-200
    per_page = max(1, min(200, per_page))

    # Validate known-set filters
    from plugindb.seed import VALID_CATEGORIES, VALID_FORMATS, VALID_PRICE_TYPES
    if category is not None and category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category '{category}'. Valid: {sorted(VALID_CATEGORIES)}")
    if price_type is not None and price_type not in VALID_PRICE_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid price_type '{price_type}'. Valid: {sorted(VALID_PRICE_TYPES)}")

    conn = get_db()

    # Build query dynamically
    where_clauses: list[str] = []
    params: list[object] = []

    if category is not None:
        where_clauses.append("p.category = ?")
        params.append(category)

    if subcategory is not None:
        where_clauses.append("p.subcategory = ?")
        params.append(subcategory)

    if manufacturer is not None:
        where_clauses.append("m.slug = ?")
        params.append(manufacturer)

    if format is not None:
        where_clauses.append("p.formats LIKE ?")
        params.append(f'%"{format}"%')

    if daw is not None:
        where_clauses.append("p.daws LIKE ?")
        params.append(f'%"{daw}"%')

    if os is not None:
        where_clauses.append("p.os LIKE ?")
        params.append(f'%"{os}"%')

    if price_type is not None:
        where_clauses.append("p.price_type = ?")
        params.append(price_type)

    if tag is not None:
        where_clauses.append("p.tags LIKE ?")
        params.append(f'%"{tag}"%')

    if year is not None:
        where_clauses.append("p.year = ?")
        params.append(year)

    if year_min is not None:
        where_clauses.append("p.year >= ?")
        params.append(year_min)

    if year_max is not None:
        where_clauses.append("p.year <= ?")
        params.append(year_max)

    if tags is not None:
        for t in tags.split(","):
            t = t.strip()
            if t:
                where_clauses.append("p.tags LIKE ?")
                params.append(f'%"{t}"%')

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    # Sorting
    sort_fields = {"name": "p.name", "year": "p.year", "created_at": "p.created_at"}
    sort_col = sort_fields.get(sort, "p.name")
    sort_dir = "DESC" if order and order.lower() == "desc" else "ASC"
    order_sql = f"ORDER BY {sort_col} {sort_dir}"

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
        {order_sql}
        LIMIT ? OFFSET ?
    """
    rows = conn.execute(query_sql, [*params, per_page, offset]).fetchall()

    data = build_plugin_responses(rows, conn)

    # Compute related tags when any filter is active
    related_tags = None
    has_filters = any(v is not None for v in [category, subcategory, manufacturer, format, daw, os, price_type, tag, tags, year, year_min, year_max])
    if has_filters and total > 0:
        # Get tags from ALL filtered results (not just current page)
        all_tag_rows = conn.execute(
            f"SELECT p.tags FROM plugins p JOIN manufacturers m ON p.manufacturer_id = m.id {where_sql}",
            params,
        ).fetchall()
        tag_freq: dict[str, int] = {}
        for r in all_tag_rows:
            if r["tags"]:
                for t in json.loads(r["tags"]):
                    tag_freq[t] = tag_freq.get(t, 0) + 1
        # Exclude the tag being filtered on
        if tag:
            tag_freq.pop(tag, None)
        if tags:
            for t_val in tags.split(","):
                tag_freq.pop(t_val.strip(), None)
        related_tags = dict(sorted(tag_freq.items(), key=lambda x: -x[1])[:10])

    return PluginListResponse(
        data=data,
        total=total,
        pagination=PaginatedResponse(
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
        ),
        related_tags=related_tags,
    )


@router.get("/plugins/compare", response_model=ComparisonResponse, responses={400: {"model": ErrorResponse}})
def compare_plugins(
    ids: str = Query(..., description="Comma-separated plugin IDs (2-5)"),
) -> ComparisonResponse:
    """Compare 2-5 plugins side by side with a diff summary."""
    id_list = [s.strip() for s in ids.split(",") if s.strip()]
    if len(id_list) < 2:
        raise HTTPException(status_code=400, detail="Must provide at least 2 plugin IDs")
    if len(id_list) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 plugin IDs allowed")

    try:
        int_ids = [int(i) for i in id_list]
    except ValueError:
        raise HTTPException(status_code=400, detail="Plugin IDs must be integers")

    conn = get_db()
    placeholders = ",".join("?" for _ in int_ids)
    rows = conn.execute(
        f"SELECT * FROM plugins WHERE id IN ({placeholders})", int_ids
    ).fetchall()

    if len(rows) != len(int_ids):
        found = {row["id"] for row in rows}
        missing = [i for i in int_ids if i not in found]
        raise HTTPException(status_code=404, detail=f"Plugin IDs not found: {missing}")

    plugins = build_plugin_responses(list(rows), conn)

    # Build comparison summary
    all_tags = [set(p.tags) for p in plugins]
    all_formats = [set(p.formats) for p in plugins]
    comparison = {
        "shared_tags": sorted(set.intersection(*all_tags)) if all_tags else [],
        "shared_formats": sorted(set.intersection(*all_formats)) if all_formats else [],
        "all_tags": sorted(set.union(*all_tags)) if all_tags else [],
        "all_formats": sorted(set.union(*all_formats)) if all_formats else [],
        "categories": list({p.category for p in plugins}),
        "subcategories": list({p.subcategory for p in plugins if p.subcategory}),
        "manufacturers": list({p.manufacturer.name for p in plugins}),
        "price_types": list({p.price_type for p in plugins}),
        "year_range": [min(p.year for p in plugins if p.year), max(p.year for p in plugins if p.year)] if any(p.year for p in plugins) else None,
    }

    return ComparisonResponse(plugins=plugins, comparison=comparison)


@router.get("/plugins/random", response_model=PluginResponse)
def get_random_plugin() -> PluginResponse:
    """Get a random plugin for discovery."""
    conn = get_db()
    row = conn.execute("SELECT * FROM plugins ORDER BY RANDOM() LIMIT 1").fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="No plugins in database")
    return build_plugin_response(row, conn)


def _attach_includes(plugin: PluginResponse, conn, include: str | None) -> dict:
    """Optionally attach extra data based on include parameter."""
    data = plugin.model_dump()
    if include and "manufacturer_plugins" in include:
        mfr_id = plugin.manufacturer.id
        other_rows = conn.execute(
            "SELECT * FROM plugins WHERE manufacturer_id = ? AND id != ? ORDER BY name ASC LIMIT 10",
            (mfr_id, plugin.id),
        ).fetchall()
        others = build_plugin_responses(list(other_rows), conn) if other_rows else []
        data["manufacturer_plugins"] = [p.model_dump() for p in others]
    return data


@router.get("/plugins/by-slug/{slug}", responses={404: {"model": ErrorResponse}})
def get_plugin_by_slug(
    slug: str,
    include: str | None = Query(None, description="Include extra data: manufacturer_plugins"),
):
    """Get a single plugin by its URL-safe slug."""
    conn = get_db()
    row = conn.execute("SELECT * FROM plugins WHERE slug = ?", (slug,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Plugin with slug '{slug}' not found")
    plugin = build_plugin_response(row, conn)
    return _attach_includes(plugin, conn, include)


@router.get("/plugins/{plugin_id}", responses={404: {"model": ErrorResponse}})
def get_plugin(
    plugin_id: int,
    include: str | None = Query(None, description="Include extra data: manufacturer_plugins"),
):
    """Get a single plugin by its database ID."""
    conn = get_db()
    row = conn.execute("SELECT * FROM plugins WHERE id = ?", (plugin_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Plugin with id {plugin_id} not found")
    plugin = build_plugin_response(row, conn)
    return _attach_includes(plugin, conn, include)


@router.get("/plugins/{plugin_id}/similar", response_model=PluginListResponse, responses={404: {"model": ErrorResponse}})
def get_similar_plugins(
    plugin_id: int,
    limit: int = Query(10, ge=1, le=50, description="Max similar plugins to return"),
) -> PluginListResponse:
    """Find plugins similar to the given plugin based on category, subcategory, and tag overlap."""
    conn = get_db()
    source = conn.execute("SELECT * FROM plugins WHERE id = ?", (plugin_id,)).fetchone()
    if source is None:
        raise HTTPException(status_code=404, detail=f"Plugin with id {plugin_id} not found")

    source_tags = set(json.loads(source["tags"]) if source["tags"] else [])

    # Find candidates in same category or subcategory
    candidates = conn.execute(
        "SELECT * FROM plugins WHERE id != ? AND (category = ? OR subcategory = ?)",
        (plugin_id, source["category"], source["subcategory"]),
    ).fetchall()

    # Score by tag overlap
    scored = []
    for c in candidates:
        c_tags = set(json.loads(c["tags"]) if c["tags"] else [])
        overlap = len(source_tags & c_tags)
        if overlap > 0 or c["subcategory"] == source["subcategory"]:
            scored.append((c, overlap))
    scored.sort(key=lambda x: -x[1])
    top_rows = [row for row, _ in scored[:limit]]

    plugins = build_plugin_responses(top_rows, conn) if top_rows else []

    return PluginListResponse(
        data=plugins,
        total=len(plugins),
        pagination=PaginatedResponse(
            total=len(plugins), page=1, per_page=limit, pages=1 if plugins else 0,
        ),
    )
