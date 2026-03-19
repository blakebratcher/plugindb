"""Meta routes — stats, categories, and health check."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from plugindb import __version__
from plugindb.main import get_db
from plugindb.models import CategoriesResponse, HealthResponse, StatsResponse

router = APIRouter(tags=["meta"])


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

    # Format breakdown (formats stored as JSON arrays — need to unpack)
    all_plugins = conn.execute("SELECT formats FROM plugins").fetchall()
    format_counts: dict[str, int] = {}
    import json
    for row in all_plugins:
        if row["formats"]:
            for fmt in json.loads(row["formats"]):
                format_counts[fmt] = format_counts.get(fmt, 0) + 1

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
        top_manufacturers=top_manufacturers,
    )


@router.get("/categories", response_model=CategoriesResponse)
def get_categories() -> CategoriesResponse:
    """Return the canonical category/subcategory taxonomy.

    This is a static hierarchy — it does not depend on database contents.
    Use it to populate filter dropdowns or validate user input.
    """
    return CategoriesResponse(
        categories=list(TAXONOMY.keys()),
        subcategories=TAXONOMY,
    )


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Basic health check — confirms the API is running and the database
    is reachable.
    """
    conn = get_db()
    try:
        count = conn.execute("SELECT COUNT(*) FROM plugins").fetchone()[0]
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
    )
