"""FastAPI application factory for PluginDB."""

from __future__ import annotations

import hashlib
import logging
import sqlite3
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.gzip import GZipMiddleware

from plugindb import __version__
from plugindb.database import DEFAULT_DB_PATH, create_schema, get_connection

logger = logging.getLogger("plugindb")

# ---------------------------------------------------------------------------
# Module-level state (set during lifespan or injected for tests)
# ---------------------------------------------------------------------------

_db_connection: sqlite3.Connection | None = None
_seed_etag: str = ""
_startup_time: float = 0.0

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


def get_db() -> sqlite3.Connection:
    """Return the active database connection.

    Raises RuntimeError if the app has not been started yet.
    """
    if _db_connection is None:
        raise RuntimeError("Database connection not initialised")
    return _db_connection


def get_seed_etag() -> str:
    """Return the current seed ETag."""
    return _seed_etag


def get_uptime() -> float:
    """Return seconds since app startup."""
    return time.time() - _startup_time if _startup_time else 0.0


def _compute_seed_etag(conn: sqlite3.Connection) -> str:
    """Compute an ETag from the current database state."""
    try:
        row = conn.execute(
            "SELECT COUNT(*) as cnt, MAX(updated_at) as max_updated FROM plugins"
        ).fetchone()
        raw = f"{row['cnt']}:{row['max_updated']}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app(db_connection: sqlite3.Connection | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    global _db_connection, _seed_etag, _startup_time

    if db_connection is not None:
        _db_connection = db_connection
        _seed_etag = _compute_seed_etag(db_connection)
        _startup_time = time.time()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        global _db_connection, _seed_etag, _startup_time
        _startup_time = time.time()
        if db_connection is not None:
            _db_connection = db_connection
        else:
            _db_connection = get_connection(DEFAULT_DB_PATH)
            create_schema(_db_connection)
        _seed_etag = _compute_seed_etag(_db_connection)
        # Warm up caches — reduces cold-start latency
        try:
            _db_connection.execute("SELECT COUNT(*) FROM plugins").fetchone()
            _db_connection.execute("SELECT rowid FROM plugins_fts LIMIT 1").fetchone()
            logger.info("Database warm-up complete: %s plugins", _db_connection.execute("SELECT COUNT(*) FROM plugins").fetchone()[0])
        except Exception as e:
            logger.warning("Database warm-up failed: %s", e)
        yield
        if db_connection is None and _db_connection is not None:
            _db_connection.close()
        _db_connection = None

    openapi_tags = [
        {"name": "lookup", "description": "Instant case-insensitive plugin name resolution"},
        {"name": "search", "description": "Full-text search and autocomplete across all plugin data"},
        {"name": "plugins", "description": "Browse, filter, and sort the plugin catalog"},
        {"name": "manufacturers", "description": "Browse plugin manufacturers"},
        {"name": "meta", "description": "Statistics, categories, tags, formats, and health checks"},
    ]

    app = FastAPI(
        title="PluginDB",
        description="Open database of audio production plugins — the MusicBrainz for VSTs, Audio Units, and CLAP plugins.",
        version=__version__,
        lifespan=lifespan,
        openapi_tags=openapi_tags,
    )

    # -- CORS --
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -- GZip compression --
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # -- Rate limiting --
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # -- Timing + ETag middleware --
    @app.middleware("http")
    async def add_headers(request: Request, call_next):
        start = time.perf_counter()

        # ETag conditional check BEFORE running the handler
        if _seed_etag and request.method == "GET":
            etag = f'"{_seed_etag}"'
            if_none_match = request.headers.get("if-none-match")
            if if_none_match and if_none_match == etag:
                elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
                return JSONResponse(
                    status_code=304, content=None,
                    headers={"ETag": etag, "X-Processing-Time-Ms": str(elapsed_ms)},
                )

        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Processing-Time-Ms"] = str(elapsed_ms)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Add ETag + Cache-Control to successful GET responses
        if _seed_etag and request.method == "GET":
            etag = f'"{_seed_etag}"'
            response.headers["ETag"] = etag
            response.headers["Cache-Control"] = "public, max-age=3600"

        return response

    # -- Routers --
    from plugindb.routes.lookup import router as lookup_router
    from plugindb.routes.plugins import router as plugins_router
    from plugindb.routes.manufacturers import router as manufacturers_router
    from plugindb.routes.search import router as search_router
    from plugindb.routes.meta import router as meta_router
    from plugindb.routes.images import router as images_router

    app.include_router(lookup_router, prefix="/api/v1")
    app.include_router(plugins_router, prefix="/api/v1")
    app.include_router(manufacturers_router, prefix="/api/v1")
    app.include_router(images_router, prefix="/api/v1")
    app.include_router(search_router, prefix="/api/v1")
    app.include_router(meta_router, prefix="/api/v1")

    # Health check also at root for convenience (load balancers, etc.)
    @app.get("/health")
    def root_health():
        from plugindb.routes.meta import health_check
        return health_check()

    # API root — content-negotiated: HTML for browsers, JSON for API clients
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"

    @app.get("/")
    def root(request: Request):
        accept = request.headers.get("accept", "")
        if "text/html" in accept and frontend_dir.is_dir():
            return FileResponse(frontend_dir / "index.html")
        return {
            "name": "PluginDB",
            "version": __version__,
            "data_version": _seed_etag,
            "api_versions": [{"version": "v1", "base_url": "/api/v1", "status": "current"}],
            "docs": "/docs",
        }

    # Global exception handler — prevents leaking stack traces
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"error": "internal_server_error", "detail": "An unexpected error occurred"},
        )

    # Mount static frontend files (must be last — catch-all)
    if frontend_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

    return app
