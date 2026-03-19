"""FastAPI application factory for PluginDB."""

from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from plugindb.database import DEFAULT_DB_PATH, create_schema, get_connection

# ---------------------------------------------------------------------------
# Module-level state (set during lifespan or injected for tests)
# ---------------------------------------------------------------------------

_db_connection: sqlite3.Connection | None = None

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


def get_db() -> sqlite3.Connection:
    """Return the active database connection.

    Raises RuntimeError if the app has not been started yet.
    """
    if _db_connection is None:
        raise RuntimeError("Database connection not initialised")
    return _db_connection


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app(db_connection: sqlite3.Connection | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Parameters
    ----------
    db_connection:
        Optional pre-configured database connection (used by tests to inject
        an in-memory SQLite instance).  When *None*, the lifespan handler
        opens the default on-disk database.
    """
    global _db_connection

    # When a connection is injected (tests / scripts), make it available
    # immediately so routes work even before the ASGI lifespan runs.
    if db_connection is not None:
        _db_connection = db_connection

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        global _db_connection
        if db_connection is not None:
            # Test mode — use the injected connection directly
            _db_connection = db_connection
        else:
            _db_connection = get_connection(DEFAULT_DB_PATH)
            create_schema(_db_connection)
        yield
        # Cleanup: only close if we opened it ourselves
        if db_connection is None and _db_connection is not None:
            _db_connection.close()
        _db_connection = None

    app = FastAPI(
        title="PluginDB",
        description="Open database of audio production plugins",
        version="1.0.0",
        lifespan=lifespan,
    )

    # -- CORS --
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -- Rate limiting --
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # -- Routers --
    from plugindb.routes.lookup import router as lookup_router
    from plugindb.routes.plugins import router as plugins_router
    from plugindb.routes.manufacturers import router as manufacturers_router
    from plugindb.routes.search import router as search_router
    from plugindb.routes.meta import router as meta_router

    app.include_router(lookup_router, prefix="/api/v1")
    app.include_router(plugins_router, prefix="/api/v1")
    app.include_router(manufacturers_router, prefix="/api/v1")
    app.include_router(search_router, prefix="/api/v1")
    app.include_router(meta_router, prefix="/api/v1")

    # Health check also at root for convenience (load balancers, etc.)
    @app.get("/health")
    def root_health():
        from plugindb.routes.meta import health_check
        return health_check()

    return app
