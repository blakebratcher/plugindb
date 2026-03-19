"""Meta routes — stats, categories, tags, and health check."""

from __future__ import annotations

import functools
import json
from typing import Any

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from plugindb import __version__
from plugindb.main import get_db
from plugindb.models import (
    CategoriesResponse,
    FormatsResponse,
    HealthResponse,
    OSResponse,
    StatsResponse,
    SubcategoriesResponse,
    TagsResponse,
    YearsResponse,
)

router = APIRouter(tags=["meta"])

_cache: dict[str, Any] = {}


def cached(key):
    """Simple process-lifetime cache decorator for read-only endpoints."""
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if key not in _cache:
                _cache[key] = fn(*args, **kwargs)
            return _cache[key]
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Taxonomy — canonical category/subcategory hierarchy
# ---------------------------------------------------------------------------

TAXONOMY: dict[str, list[str]] = {
    "instrument": [
        "synth", "sampler", "drum-machine", "rompler", "organ",
        "piano", "guitar", "general",
    ],
    "effect": [
        "eq", "compressor", "limiter", "gate", "reverb", "delay",
        "distortion", "saturation", "filter", "modulation", "chorus",
        "phaser", "flanger", "pitch", "vocoder", "de-esser",
        "multiband", "general",
    ],
    "container": [
        "layer", "selector", "splitter", "chain", "general",
    ],
    "note-effect": [
        "arpeggiator", "quantize", "transpose", "harmonize", "strum",
        "general",
    ],
    "utility": [
        "analyzer", "meter", "test-tone", "routing", "sidechain",
        "tuner", "general",
    ],
    "midi": [
        "sequencer", "generator", "filter", "general",
    ],
}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/stats", response_model=StatsResponse)
@cached("stats")
def get_stats() -> StatsResponse:
    """Return database-wide statistics.

    Includes total counts for plugins, manufacturers, and aliases,
    plus breakdowns by category and format, and a list of top
    manufacturers by plugin count.
    """
    conn = get_db()

    total_plugins = conn.execute("SELECT COUNT(*) FROM plugins").fetchone()[0]
    total_manufacturers = conn.execute("SELECT COUNT(*) FROM manufacturers").fetchone()[0]
    total_aliases = conn.execute("SELECT COUNT(*) FROM aliases").fetchone()[0]

    # Category breakdown
    cat_rows = conn.execute(
        "SELECT category, COUNT(*) as cnt FROM plugins GROUP BY category ORDER BY cnt DESC"
    ).fetchall()
    categories = {row["category"]: row["cnt"] for row in cat_rows}

    # Format, tag, and OS breakdown (stored as JSON arrays — need to unpack)
    all_plugins = conn.execute("SELECT formats, tags, os FROM plugins").fetchall()
    format_counts: dict[str, int] = {}
    tag_counts: dict[str, int] = {}
    os_counts: dict[str, int] = {}
    for row in all_plugins:
        if row["formats"]:
            for fmt in json.loads(row["formats"]):
                format_counts[fmt] = format_counts.get(fmt, 0) + 1
        if row["tags"]:
            for t in json.loads(row["tags"]):
                tag_counts[t] = tag_counts.get(t, 0) + 1
        if row["os"]:
            for o in json.loads(row["os"]):
                os_counts[o] = os_counts.get(o, 0) + 1

    # Price type breakdown
    price_rows = conn.execute(
        "SELECT price_type, COUNT(*) as cnt FROM plugins GROUP BY price_type ORDER BY cnt DESC"
    ).fetchall()
    price_types = {row["price_type"]: row["cnt"] for row in price_rows}

    # Top manufacturers
    top_rows = conn.execute(
        """SELECT m.name, m.slug, COUNT(p.id) as plugin_count
           FROM manufacturers m
           JOIN plugins p ON p.manufacturer_id = m.id
           GROUP BY m.id
           ORDER BY plugin_count DESC
           LIMIT 10"""
    ).fetchall()
    top_manufacturers = [
        {"name": r["name"], "slug": r["slug"], "plugin_count": r["plugin_count"]}
        for r in top_rows
    ]

    return StatsResponse(
        total_plugins=total_plugins,
        total_manufacturers=total_manufacturers,
        total_aliases=total_aliases,
        categories=categories,
        formats=format_counts,
        os=os_counts,
        tags=tag_counts,
        price_types=price_types,
        top_manufacturers=top_manufacturers,
    )


@router.get("/categories", response_model=CategoriesResponse)
@cached("categories")
def get_categories() -> CategoriesResponse:
    """Return the canonical category/subcategory taxonomy.

    This is a static hierarchy — it does not depend on database contents.
    Use it to populate filter dropdowns or validate user input.
    """
    return CategoriesResponse(
        categories=list(TAXONOMY.keys()),
        subcategories=TAXONOMY,
    )


@router.get("/formats", response_model=FormatsResponse)
@cached("formats")
def get_formats() -> FormatsResponse:
    """Return all plugin formats with usage counts, sorted by frequency."""
    conn = get_db()
    rows = conn.execute("SELECT formats FROM plugins").fetchall()
    format_counts: dict[str, int] = {}
    for row in rows:
        if row["formats"]:
            for fmt in json.loads(row["formats"]):
                format_counts[fmt] = format_counts.get(fmt, 0) + 1
    sorted_formats = dict(sorted(format_counts.items(), key=lambda x: (-x[1], x[0])))
    return FormatsResponse(formats=sorted_formats, total=len(sorted_formats))


@router.get("/os", response_model=OSResponse)
@cached("os")
def get_os() -> OSResponse:
    """Return all operating systems with usage counts, sorted by frequency."""
    conn = get_db()
    rows = conn.execute("SELECT os FROM plugins").fetchall()
    os_counts: dict[str, int] = {}
    for row in rows:
        if row["os"]:
            for o in json.loads(row["os"]):
                os_counts[o] = os_counts.get(o, 0) + 1
    sorted_os = dict(sorted(os_counts.items(), key=lambda x: (-x[1], x[0])))
    return OSResponse(os=sorted_os, total=len(sorted_os))


@router.get("/subcategories", response_model=SubcategoriesResponse)
@cached("subcategories")
def get_subcategories() -> SubcategoriesResponse:
    """Return subcategories with actual plugin counts from the database."""
    conn = get_db()
    rows = conn.execute(
        "SELECT category, subcategory, COUNT(*) as cnt FROM plugins "
        "GROUP BY category, subcategory ORDER BY category, cnt DESC"
    ).fetchall()
    result: dict[str, dict[str, int]] = {}
    for row in rows:
        cat = row["category"]
        subcat = row["subcategory"] or "general"
        if cat not in result:
            result[cat] = {}
        result[cat][subcat] = row["cnt"]
    return SubcategoriesResponse(subcategories=result)


@router.get("/tags", response_model=TagsResponse)
@cached("tags")
def get_tags() -> TagsResponse:
    """Return all distinct tags with usage counts, sorted by frequency."""
    conn = get_db()
    rows = conn.execute("SELECT tags FROM plugins").fetchall()
    tag_counts: dict[str, int] = {}
    for row in rows:
        if row["tags"]:
            for t in json.loads(row["tags"]):
                tag_counts[t] = tag_counts.get(t, 0) + 1
    sorted_tags = dict(sorted(tag_counts.items(), key=lambda x: (-x[1], x[0])))
    return TagsResponse(tags=sorted_tags, total=len(sorted_tags))


@router.get("/years", response_model=YearsResponse)
@cached("years")
def get_years() -> YearsResponse:
    """Return plugin counts by release year, sorted chronologically."""
    conn = get_db()
    rows = conn.execute(
        "SELECT year, COUNT(*) as cnt FROM plugins WHERE year IS NOT NULL "
        "GROUP BY year ORDER BY year ASC"
    ).fetchall()
    years = {row["year"]: row["cnt"] for row in rows}
    return YearsResponse(years=years, total=len(years))


@router.get("/export")
def export_data(
    format: str = Query("json", description="Export format: json or csv"),
):
    """Export the entire plugin catalog as JSON or CSV."""
    from plugindb.queries import build_plugin_responses
    conn = get_db()
    rows = conn.execute("SELECT * FROM plugins ORDER BY name ASC").fetchall()
    plugins = build_plugin_responses(list(rows), conn)

    if format == "csv":
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "slug", "name", "manufacturer", "category", "subcategory",
                         "formats", "daws", "os", "tags", "description", "website",
                         "is_free", "price_type", "year"])
        for p in plugins:
            writer.writerow([
                p.id, p.slug, p.name, p.manufacturer.name, p.category, p.subcategory,
                "|".join(p.formats), "|".join(p.daws), "|".join(p.os), "|".join(p.tags),
                p.description, p.website, p.is_free, p.price_type, p.year,
            ])
        from starlette.responses import Response
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=plugindb-export.csv"},
        )

    # Default: JSON
    return JSONResponse(
        content=[p.model_dump() for p in plugins],
        headers={"Content-Disposition": "attachment; filename=plugindb-export.json"},
    )


@router.get("/search-analytics")
def get_search_analytics():
    """Return search analytics: top queries, zero-result queries, volume."""
    conn = get_db()
    try:
        top = conn.execute(
            "SELECT query, COUNT(*) as count, AVG(results_count) as avg_results "
            "FROM search_log GROUP BY query ORDER BY count DESC LIMIT 50"
        ).fetchall()
        zero = conn.execute(
            "SELECT query, COUNT(*) as count FROM search_log "
            "WHERE results_count = 0 GROUP BY query ORDER BY count DESC LIMIT 50"
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM search_log").fetchone()[0]
        return {
            "total_searches": total,
            "top_queries": [{"query": r["query"], "count": r["count"], "avg_results": round(r["avg_results"], 1)} for r in top],
            "zero_result_queries": [{"query": r["query"], "count": r["count"]} for r in zero],
        }
    except Exception:
        return {"total_searches": 0, "top_queries": [], "zero_result_queries": []}


@router.get("/version")
def get_version():
    """Return API and data version info for lightweight polling."""
    conn = get_db()
    seed_hash = None
    seed_timestamp = None
    try:
        for row in conn.execute("SELECT key, value FROM metadata").fetchall():
            if row["key"] == "seed_hash":
                seed_hash = row["value"]
            elif row["key"] == "seed_timestamp":
                seed_timestamp = row["value"]
    except Exception:
        pass
    return {
        "api_version": __version__,
        "data_version": seed_hash,
        "data_updated_at": seed_timestamp,
    }


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Basic health check — confirms the API is running and the database
    is reachable.
    """
    from plugindb.main import get_seed_etag, get_uptime
    conn = get_db()
    try:
        plugin_count = conn.execute("SELECT COUNT(*) FROM plugins").fetchone()[0]
        mfr_count = conn.execute("SELECT COUNT(*) FROM manufacturers").fetchone()[0]
        db_status = "connected"
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "version": __version__, "database": "error"},
        )

    return HealthResponse(
        status="ok",
        version=__version__,
        database=db_status,
        plugin_count=plugin_count,
        manufacturer_count=mfr_count,
        data_version=get_seed_etag(),
        uptime_seconds=round(get_uptime(), 1),
    )
