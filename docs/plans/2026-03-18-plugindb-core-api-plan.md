# PluginDB Core API — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a public REST API that serves as the canonical database for audio production plugins — lookup by filename, browse by category, search by text.

**Architecture:** FastAPI app with SQLite backend (raw sql, no ORM). Seed data imported from a JSON file. FTS5 for search. Rate limiting via slowapi. Deploy-ready with Dockerfile.

**Tech Stack:** Python 3.12+, FastAPI, Uvicorn, SQLite (FTS5), slowapi, pytest, httpx (test client)

**Spec:** `docs/specs/2026-03-18-plugindb-core-api-design.md`

---

## File Structure

| Action | File | Responsibility |
|--------|------|----------------|
| Create | `pyproject.toml` | Project metadata, dependencies |
| Create | `plugindb/__init__.py` | Package init with version |
| Create | `plugindb/database.py` | SQLite connection, schema DDL, WAL mode, FTS5 |
| Create | `plugindb/models.py` | Pydantic response models |
| Create | `plugindb/main.py` | FastAPI app, CORS, rate limiter, lifespan, router mounts |
| Create | `plugindb/routes/__init__.py` | Empty |
| Create | `plugindb/routes/lookup.py` | GET /lookup, POST /lookup (batch) |
| Create | `plugindb/routes/plugins.py` | GET /plugins, GET /plugins/{id} |
| Create | `plugindb/routes/manufacturers.py` | GET /manufacturers, GET /manufacturers/{slug} |
| Create | `plugindb/routes/search.py` | GET /search |
| Create | `plugindb/routes/meta.py` | GET /stats, GET /categories, GET /health |
| Create | `plugindb/seed.py` | Transform + import seed.json → SQLite |
| Create | `data/seed.json` | Seed data (transformed from Bitwig OS registry) |
| Create | `tests/conftest.py` | Test fixtures: in-memory DB, seeded test client |
| Create | `tests/test_lookup.py` | Lookup endpoint tests |
| Create | `tests/test_plugins.py` | Plugins endpoint tests |
| Create | `tests/test_manufacturers.py` | Manufacturers endpoint tests |
| Create | `tests/test_search.py` | Search endpoint tests |
| Create | `tests/test_meta.py` | Stats, categories, health tests |
| Create | `tests/test_seed.py` | Seed script tests |
| Create | `.gitignore` | Python + SQLite ignores |
| Create | `LICENSE` | MIT |
| Create | `README.md` | Project overview + API quickstart |
| Create | `Dockerfile` | Production container |
| Create | `.github/workflows/test.yml` | CI: run tests on every PR |
| Create | `.github/workflows/validate-seed.yml` | CI: validate seed.json schema |

---

### Task 1: Project scaffolding and database layer

**Files:**
- Create: `pyproject.toml`
- Create: `plugindb/__init__.py`
- Create: `plugindb/database.py`
- Create: `tests/conftest.py`
- Create: `tests/test_seed.py`
- Create: `.gitignore`
- Create: `LICENSE`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "plugindb"
version = "1.0.0"
description = "Open database of audio production plugins — the MusicBrainz for VSTs"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "slowapi>=0.1.9",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "httpx>=0.27",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create .gitignore**

```
__pycache__/
*.pyc
.pytest_cache/
data/plugindb.sqlite
*.egg-info/
dist/
.venv/
```

- [ ] **Step 3: Create LICENSE (MIT)**

- [ ] **Step 4: Create plugindb/__init__.py**

```python
"""PluginDB — Open database of audio production plugins."""
__version__ = "1.0.0"
```

- [ ] **Step 5: Write failing test for database schema**

```python
# tests/test_seed.py
"""Tests for database schema and seed import."""
import sqlite3
import pytest


def test_schema_creates_tables(tmp_path):
    """Schema DDL creates all required tables."""
    from plugindb.database import create_schema

    db_path = tmp_path / "test.sqlite"
    conn = sqlite3.connect(str(db_path))
    create_schema(conn)

    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    assert "manufacturers" in tables
    assert "plugins" in tables
    assert "aliases" in tables


def test_schema_enables_wal_mode(tmp_path):
    """Database uses WAL mode for concurrent reads."""
    from plugindb.database import get_connection

    db_path = tmp_path / "test.sqlite"
    conn = get_connection(str(db_path))

    mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
    conn.close()
    assert mode == "wal"


def test_schema_enables_foreign_keys(tmp_path):
    """Foreign keys are enforced."""
    from plugindb.database import get_connection

    db_path = tmp_path / "test.sqlite"
    conn = get_connection(str(db_path))

    fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
    conn.close()
    assert fk == 1
```

- [ ] **Step 6: Run tests to verify they fail**

Run: `cd "C:\Users\Blake\Documents\GitHub\plugindb" && pip install -e ".[dev]" && python -m pytest tests/test_seed.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'plugindb.database'`

- [ ] **Step 7: Implement database.py**

```python
"""SQLite database connection, schema, and FTS5 setup."""
from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS manufacturers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plugins (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    manufacturer_id TEXT NOT NULL REFERENCES manufacturers(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    subcategory TEXT DEFAULT 'general',
    description TEXT,
    formats TEXT,
    daws TEXT,
    os TEXT,
    price_type TEXT,
    tags TEXT,
    year INTEGER,
    url TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS aliases (
    lookup_key TEXT PRIMARY KEY,
    display TEXT NOT NULL,
    plugin_id TEXT NOT NULL REFERENCES plugins(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_plugins_category ON plugins(category);
CREATE INDEX IF NOT EXISTS idx_plugins_manufacturer ON plugins(manufacturer_id);
"""

FTS_SQL = """
CREATE VIRTUAL TABLE IF NOT EXISTS plugins_fts USING fts5(
    plugin_id,
    name,
    manufacturer_name,
    description,
    tags,
    content='',
    tokenize='unicode61'
);
"""


def get_connection(db_path: str) -> sqlite3.Connection:
    """Create a connection with WAL mode and foreign keys enabled."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """Create all tables and indexes."""
    conn.executescript(SCHEMA_SQL)
    conn.executescript(FTS_SQL)
    conn.commit()
```

- [ ] **Step 8: Run tests**

Run: `python -m pytest tests/test_seed.py -v`
Expected: 3 passed

- [ ] **Step 9: Commit**

```bash
cd "C:\Users\Blake\Documents\GitHub\plugindb"
git init
git add -A
git commit -m "feat: project scaffolding + database schema with WAL, FTS5"
```

---

### Task 2: Seed data pipeline

**Files:**
- Create: `plugindb/seed.py`
- Create: `data/seed.json`
- Modify: `tests/test_seed.py`

- [ ] **Step 1: Create the seed transformation script**

This reads the Bitwig OS `plugin-registry.json`, strips Bitwig-specific fields, extracts manufacturers, and writes `data/seed.json`.

```python
# plugindb/seed.py
"""Seed data import: JSON → SQLite."""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .database import create_schema, get_connection

VALID_FORMATS = {"VST2", "VST3", "CLAP", "AU", "AAX"}


def slugify(name: str) -> str:
    """Convert a name to a kebab-case slug."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load_seed(seed_path: Path) -> dict:
    """Load and validate seed.json."""
    with open(seed_path, "r", encoding="utf-8") as f:
        return json.load(f)


def seed_database(conn: sqlite3.Connection, data: dict) -> dict:
    """Import seed data into the database. Returns stats."""
    now = datetime.now(timezone.utc).isoformat()
    create_schema(conn)

    # Clear existing data for idempotent re-seed
    conn.execute("DELETE FROM aliases")
    conn.execute("DELETE FROM plugins")
    conn.execute("DELETE FROM manufacturers")
    conn.execute("DELETE FROM plugins_fts")

    manufacturers = data.get("manufacturers", [])
    plugins = data.get("plugins", [])

    # Insert manufacturers
    for mfr in manufacturers:
        conn.execute(
            "INSERT INTO manufacturers (id, name, url, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (mfr["id"], mfr["name"], mfr.get("url", ""), now, now),
        )

    # Insert plugins
    for p in plugins:
        formats_json = json.dumps(p.get("formats", []))
        daws_json = json.dumps(p.get("daws", []))
        os_json = json.dumps(p.get("os", []))
        tags_json = json.dumps(p.get("tags", []))

        conn.execute(
            """INSERT INTO plugins
            (id, name, manufacturer_id, category, subcategory, description,
             formats, daws, os, price_type, tags, year, url, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                p["id"], p["name"], p["manufacturer_id"],
                p["category"], p.get("subcategory", "general"),
                p.get("description"), formats_json, daws_json, os_json,
                p.get("price_type"), tags_json, p.get("year"),
                p.get("url"), now, now,
            ),
        )

        # Insert aliases
        for alias in p.get("aliases", []):
            conn.execute(
                "INSERT OR IGNORE INTO aliases (lookup_key, display, plugin_id) VALUES (?, ?, ?)",
                (alias.lower(), alias, p["id"]),
            )

    # Rebuild FTS index
    for p in plugins:
        mfr_name = next((m["name"] for m in manufacturers if m["id"] == p["manufacturer_id"]), "")
        tags_str = " ".join(p.get("tags", []))
        conn.execute(
            "INSERT INTO plugins_fts (plugin_id, name, manufacturer_name, description, tags) VALUES (?, ?, ?, ?, ?)",
            (p["id"], p["name"], mfr_name, p.get("description", ""), tags_str),
        )

    conn.commit()

    return {
        "manufacturers": len(manufacturers),
        "plugins": len(plugins),
        "aliases": conn.execute("SELECT COUNT(*) FROM aliases").fetchone()[0],
    }


def transform_registry(registry_path: Path, output_path: Path) -> None:
    """Transform Bitwig OS plugin-registry.json into PluginDB seed.json."""
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    # Extract unique manufacturers
    mfr_map: dict[str, dict] = {}
    for entry in registry["entries"]:
        mfr_name = entry["manufacturer"]
        mfr_id = slugify(mfr_name)
        if mfr_id not in mfr_map:
            mfr_map[mfr_id] = {"id": mfr_id, "name": mfr_name, "url": ""}

    # Transform plugins
    plugins = []
    for entry in registry["entries"]:
        mfr_id = slugify(entry["manufacturer"])
        # Filter formats to valid set
        formats = [f for f in entry.get("formats", []) if f in VALID_FORMATS]

        plugins.append({
            "id": entry["id"],
            "name": entry["name"],
            "manufacturer_id": mfr_id,
            "category": entry["category"],
            "subcategory": entry.get("subcategory", "general"),
            "description": entry.get("description"),
            "formats": formats,
            "daws": entry.get("daws", []),
            "os": entry.get("os", []),
            "price_type": entry.get("price_type"),
            "tags": entry.get("tags", []),
            "year": entry.get("year"),
            "url": entry.get("url", ""),
            "aliases": entry.get("aliases", []),
        })

    seed = {
        "schema_version": "1.0",
        "generated": datetime.now(timezone.utc).isoformat(),
        "manufacturers": sorted(mfr_map.values(), key=lambda m: m["name"].lower()),
        "plugins": sorted(plugins, key=lambda p: (p["manufacturer_id"], p["name"].lower())),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(seed, f, indent=2, ensure_ascii=False)


def main() -> None:
    """CLI entry point: seed the database from data/seed.json."""
    import sys

    base = Path(__file__).resolve().parent.parent
    seed_path = base / "data" / "seed.json"
    db_path = base / "data" / "plugindb.sqlite"

    if not seed_path.exists():
        print(f"Seed file not found: {seed_path}")
        sys.exit(1)

    data = load_seed(seed_path)
    conn = get_connection(str(db_path))
    stats = seed_database(conn, data)
    conn.close()

    print(f"Seeded: {stats['manufacturers']} manufacturers, "
          f"{stats['plugins']} plugins, {stats['aliases']} aliases")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Add seed tests**

Add to `tests/test_seed.py`:

```python
def _make_seed_data():
    """Minimal seed data for testing."""
    return {
        "schema_version": "1.0",
        "manufacturers": [
            {"id": "fabfilter", "name": "FabFilter", "url": "https://fabfilter.com"},
            {"id": "xfer", "name": "Xfer Records", "url": ""},
        ],
        "plugins": [
            {
                "id": "fabfilter-pro-q-3", "name": "Pro-Q 3",
                "manufacturer_id": "fabfilter", "category": "effect",
                "subcategory": "eq", "description": "Parametric EQ",
                "formats": ["VST3", "CLAP"], "daws": [], "os": [],
                "price_type": "paid", "tags": ["equalizer"],
                "year": 2018, "url": "", "aliases": ["FabfilterProQ3", "ProQ3"],
            },
            {
                "id": "xfer-serum", "name": "Serum",
                "manufacturer_id": "xfer", "category": "instrument",
                "subcategory": "synth", "description": "Wavetable synth",
                "formats": ["VST3"], "daws": [], "os": [],
                "price_type": "paid", "tags": ["synth", "wavetable"],
                "year": 2014, "url": "", "aliases": ["Serum", "XferSerum"],
            },
        ],
    }


def test_seed_inserts_manufacturers(tmp_path):
    from plugindb.database import get_connection
    from plugindb.seed import seed_database

    conn = get_connection(str(tmp_path / "test.sqlite"))
    stats = seed_database(conn, _make_seed_data())
    assert stats["manufacturers"] == 2
    conn.close()


def test_seed_inserts_plugins(tmp_path):
    from plugindb.database import get_connection
    from plugindb.seed import seed_database

    conn = get_connection(str(tmp_path / "test.sqlite"))
    stats = seed_database(conn, _make_seed_data())
    assert stats["plugins"] == 2
    conn.close()


def test_seed_inserts_aliases(tmp_path):
    from plugindb.database import get_connection
    from plugindb.seed import seed_database

    conn = get_connection(str(tmp_path / "test.sqlite"))
    stats = seed_database(conn, _make_seed_data())
    assert stats["aliases"] == 4  # 2 aliases per plugin
    conn.close()


def test_seed_is_idempotent(tmp_path):
    from plugindb.database import get_connection
    from plugindb.seed import seed_database

    conn = get_connection(str(tmp_path / "test.sqlite"))
    data = _make_seed_data()
    seed_database(conn, data)
    stats = seed_database(conn, data)  # Run again
    assert stats["plugins"] == 2  # Same count, not doubled
    conn.close()


def test_alias_lookup_case_insensitive(tmp_path):
    from plugindb.database import get_connection
    from plugindb.seed import seed_database

    conn = get_connection(str(tmp_path / "test.sqlite"))
    seed_database(conn, _make_seed_data())

    row = conn.execute(
        "SELECT plugin_id FROM aliases WHERE lookup_key = ?",
        ("fabfilterproq3",),
    ).fetchone()
    assert row is not None
    assert row["plugin_id"] == "fabfilter-pro-q-3"
    conn.close()
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest tests/test_seed.py -v`
Expected: 8 passed

- [ ] **Step 4: Generate seed.json from Bitwig OS registry**

Run: `python -c "from plugindb.seed import transform_registry; from pathlib import Path; transform_registry(Path(r'B:\My files\Obsidian Vaults\Bitwig OS\_Meta\Data\plugin-registry.json'), Path(r'C:\Users\Blake\Documents\GitHub\plugindb\data\seed.json'))"`

Verify: `python -c "import json; d=json.load(open('data/seed.json')); print(f'{len(d[\"plugins\"])} plugins, {len(d[\"manufacturers\"])} manufacturers')"`

- [ ] **Step 5: Seed the database**

Run: `python -m plugindb.seed`
Expected: "Seeded: X manufacturers, 272 plugins, Y aliases"

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: seed pipeline — transform registry JSON, import to SQLite"
```

---

### Task 3: Pydantic response models

**Files:**
- Create: `plugindb/models.py`

- [ ] **Step 1: Create all response models**

```python
"""Pydantic response models for the API."""
from __future__ import annotations

from pydantic import BaseModel


class ManufacturerResponse(BaseModel):
    id: str
    name: str
    url: str | None = None


class PluginResponse(BaseModel):
    id: str
    name: str
    manufacturer: ManufacturerResponse
    category: str
    subcategory: str
    description: str | None = None
    formats: list[str] = []
    daws: list[str] = []
    os: list[str] = []
    price_type: str | None = None
    tags: list[str] = []
    year: int | None = None
    url: str | None = None
    aliases: list[str] = []


class PaginatedResponse(BaseModel):
    results: list
    total: int
    page: int
    per_page: int
    pages: int


class PluginListResponse(PaginatedResponse):
    results: list[PluginResponse]


class ManufacturerListResponse(PaginatedResponse):
    results: list[ManufacturerResponse]


class ManufacturerDetailResponse(ManufacturerResponse):
    plugins: list[PluginResponse] = []


class BatchLookupRequest(BaseModel):
    aliases: list[str]


class BatchLookupResponse(BaseModel):
    results: dict[str, PluginResponse | None]
    matched: int
    unmatched: int


class StatsResponse(BaseModel):
    plugins: int
    manufacturers: int
    aliases: int
    last_updated: str | None = None
    version: str


class HealthResponse(BaseModel):
    status: str
    plugins: int
    version: str


class ErrorResponse(BaseModel):
    error: str
    message: str


class CategoriesResponse(BaseModel):
    categories: dict[str, list[str]]
```

- [ ] **Step 2: Commit**

```bash
git add plugindb/models.py
git commit -m "feat: Pydantic response models for all endpoints"
```

---

### Task 4: FastAPI app + lookup endpoint (the killer feature)

**Files:**
- Create: `plugindb/main.py`
- Create: `plugindb/routes/__init__.py`
- Create: `plugindb/routes/lookup.py`
- Create: `tests/conftest.py`
- Create: `tests/test_lookup.py`

- [ ] **Step 1: Create conftest.py with test fixtures**

```python
# tests/conftest.py
"""Shared test fixtures."""
import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from plugindb.database import get_connection
from plugindb.seed import seed_database


@pytest.fixture
def seed_data():
    """Minimal seed data for testing."""
    return {
        "schema_version": "1.0",
        "manufacturers": [
            {"id": "fabfilter", "name": "FabFilter", "url": "https://fabfilter.com"},
            {"id": "xfer", "name": "Xfer Records", "url": ""},
            {"id": "valhalla", "name": "Valhalla DSP", "url": ""},
        ],
        "plugins": [
            {
                "id": "fabfilter-pro-q-3", "name": "Pro-Q 3",
                "manufacturer_id": "fabfilter", "category": "effect",
                "subcategory": "eq", "description": "Parametric EQ",
                "formats": ["VST3", "CLAP"], "daws": ["Bitwig", "Ableton"],
                "os": ["windows", "macos"], "price_type": "paid",
                "tags": ["equalizer", "dynamic-eq"], "year": 2018,
                "url": "https://fabfilter.com/pro-q-3",
                "aliases": ["FabfilterProQ3", "ProQ3", "FabFilter Pro-Q 3"],
            },
            {
                "id": "xfer-serum", "name": "Serum",
                "manufacturer_id": "xfer", "category": "instrument",
                "subcategory": "synth", "description": "Wavetable synthesizer",
                "formats": ["VST3"], "daws": [], "os": ["windows", "macos"],
                "price_type": "paid", "tags": ["synth", "wavetable"],
                "year": 2014, "url": "",
                "aliases": ["Serum", "XferSerum", "Xfer Serum"],
            },
            {
                "id": "valhalla-vintage-verb", "name": "VintageVerb",
                "manufacturer_id": "valhalla", "category": "effect",
                "subcategory": "reverb", "description": "Vintage reverb",
                "formats": ["VST3", "AU"], "daws": [], "os": [],
                "price_type": "paid", "tags": ["reverb", "vintage"],
                "year": 2012, "url": "",
                "aliases": ["ValhallaVintageVerb", "Valhalla VintageVerb"],
            },
        ],
    }


@pytest.fixture
def seeded_db(tmp_path, seed_data):
    """Return a seeded SQLite connection."""
    db_path = str(tmp_path / "test.sqlite")
    conn = get_connection(db_path)
    seed_database(conn, seed_data)
    return conn


@pytest.fixture
def client(tmp_path, seed_data):
    """Return a FastAPI test client with seeded database."""
    db_path = str(tmp_path / "test.sqlite")
    conn = get_connection(db_path)
    seed_database(conn, seed_data)

    from plugindb.main import create_app

    app = create_app(db_connection=conn)
    return TestClient(app)
```

- [ ] **Step 2: Write failing lookup tests**

```python
# tests/test_lookup.py
"""Tests for the lookup endpoint."""


def test_lookup_exact_match(client):
    r = client.get("/api/v1/lookup", params={"alias": "FabfilterProQ3"})
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == "fabfilter-pro-q-3"
    assert data["name"] == "Pro-Q 3"
    assert data["manufacturer"]["name"] == "FabFilter"


def test_lookup_case_insensitive(client):
    r = client.get("/api/v1/lookup", params={"alias": "fabfilterproq3"})
    assert r.status_code == 200
    assert r.json()["id"] == "fabfilter-pro-q-3"


def test_lookup_not_found(client):
    r = client.get("/api/v1/lookup", params={"alias": "NonexistentPlugin"})
    assert r.status_code == 404
    assert r.json()["error"] == "not_found"


def test_lookup_missing_param(client):
    r = client.get("/api/v1/lookup")
    assert r.status_code == 422


def test_lookup_returns_aliases(client):
    r = client.get("/api/v1/lookup", params={"alias": "ProQ3"})
    assert r.status_code == 200
    assert "FabfilterProQ3" in r.json()["aliases"]


def test_batch_lookup(client):
    r = client.post("/api/v1/lookup", json={
        "aliases": ["FabfilterProQ3", "Serum", "UnknownPlugin"]
    })
    assert r.status_code == 200
    data = r.json()
    assert data["matched"] == 2
    assert data["unmatched"] == 1
    assert data["results"]["FabfilterProQ3"]["name"] == "Pro-Q 3"
    assert data["results"]["Serum"]["name"] == "Serum"
    assert data["results"]["UnknownPlugin"] is None


def test_batch_lookup_empty(client):
    r = client.post("/api/v1/lookup", json={"aliases": []})
    assert r.status_code == 200
    assert r.json()["matched"] == 0
```

- [ ] **Step 3: Implement main.py**

```python
"""FastAPI application factory."""
from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from . import __version__

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Module-level DB connection (set by create_app or lifespan)
_db: sqlite3.Connection | None = None


def get_db() -> sqlite3.Connection:
    """Get the active database connection."""
    assert _db is not None, "Database not initialized"
    return _db


def create_app(db_connection: sqlite3.Connection | None = None) -> FastAPI:
    """Create the FastAPI app. Optionally inject a DB connection (for tests)."""
    global _db

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        global _db
        if _db is None:
            from .database import get_connection, create_schema
            db_path = Path(__file__).resolve().parent.parent / "data" / "plugindb.sqlite"
            _db = get_connection(str(db_path))
            create_schema(_db)
        yield
        if _db is not None:
            _db.close()
            _db = None

    if db_connection is not None:
        _db = db_connection

    app = FastAPI(
        title="PluginDB",
        description="Open database of audio production plugins",
        version=__version__,
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"error": "rate_limited", "message": "Too many requests"},
        )

    from .routes import lookup, plugins, manufacturers, search, meta
    app.include_router(lookup.router, prefix="/api/v1")
    app.include_router(plugins.router, prefix="/api/v1")
    app.include_router(manufacturers.router, prefix="/api/v1")
    app.include_router(search.router, prefix="/api/v1")
    app.include_router(meta.router)

    return app
```

- [ ] **Step 4: Create routes/__init__.py** (empty file)

- [ ] **Step 5: Implement lookup route**

```python
# plugindb/routes/lookup.py
"""Lookup endpoint — the killer feature."""
from __future__ import annotations

import json

from fastapi import APIRouter, Query, HTTPException

from ..main import get_db
from ..models import PluginResponse, ManufacturerResponse, BatchLookupRequest, BatchLookupResponse

router = APIRouter()


def _build_plugin_response(row, conn) -> PluginResponse:
    """Build a full PluginResponse from a plugins row."""
    mfr = conn.execute(
        "SELECT id, name, url FROM manufacturers WHERE id = ?",
        (row["manufacturer_id"],),
    ).fetchone()

    aliases = [
        r["display"] for r in conn.execute(
            "SELECT display FROM aliases WHERE plugin_id = ?", (row["id"],)
        ).fetchall()
    ]

    return PluginResponse(
        id=row["id"],
        name=row["name"],
        manufacturer=ManufacturerResponse(
            id=mfr["id"], name=mfr["name"], url=mfr["url"],
        ),
        category=row["category"],
        subcategory=row["subcategory"] or "general",
        description=row["description"],
        formats=json.loads(row["formats"]) if row["formats"] else [],
        daws=json.loads(row["daws"]) if row["daws"] else [],
        os=json.loads(row["os"]) if row["os"] else [],
        price_type=row["price_type"],
        tags=json.loads(row["tags"]) if row["tags"] else [],
        year=row["year"],
        url=row["url"],
        aliases=aliases,
    )


@router.get("/lookup")
def lookup(alias: str = Query(..., min_length=1)) -> PluginResponse:
    """Look up a plugin by filename/alias. Case-insensitive."""
    conn = get_db()
    alias_row = conn.execute(
        "SELECT plugin_id FROM aliases WHERE lookup_key = ?",
        (alias.lower(),),
    ).fetchone()

    if alias_row is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "message": f"No plugin found matching alias '{alias}'", "alias": alias},
        )

    plugin = conn.execute("SELECT * FROM plugins WHERE id = ?", (alias_row["plugin_id"],)).fetchone()
    return _build_plugin_response(plugin, conn)


@router.post("/lookup")
def batch_lookup(body: BatchLookupRequest) -> BatchLookupResponse:
    """Look up multiple plugins by alias. Max 200 per request."""
    conn = get_db()
    aliases = body.aliases[:200]

    results = {}
    matched = 0
    for alias in aliases:
        alias_row = conn.execute(
            "SELECT plugin_id FROM aliases WHERE lookup_key = ?",
            (alias.lower(),),
        ).fetchone()

        if alias_row:
            plugin = conn.execute("SELECT * FROM plugins WHERE id = ?", (alias_row["plugin_id"],)).fetchone()
            results[alias] = _build_plugin_response(plugin, conn)
            matched += 1
        else:
            results[alias] = None

    return BatchLookupResponse(
        results=results, matched=matched, unmatched=len(aliases) - matched,
    )
```

- [ ] **Step 6: Run lookup tests**

Run: `python -m pytest tests/test_lookup.py -v`
Expected: 7 passed

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat: FastAPI app + lookup endpoint (GET + batch POST)"
```

---

### Task 5: Browse endpoints (plugins + manufacturers)

**Files:**
- Create: `plugindb/routes/plugins.py`
- Create: `plugindb/routes/manufacturers.py`
- Create: `tests/test_plugins.py`
- Create: `tests/test_manufacturers.py`

- [ ] **Step 1: Write plugin endpoint tests**

```python
# tests/test_plugins.py
"""Tests for plugin browse endpoints."""


def test_list_plugins(client):
    r = client.get("/api/v1/plugins")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3
    assert len(data["results"]) == 3
    assert data["page"] == 1


def test_list_plugins_filter_category(client):
    r = client.get("/api/v1/plugins", params={"category": "effect"})
    assert r.status_code == 200
    assert r.json()["total"] == 2  # Pro-Q 3 + VintageVerb


def test_list_plugins_filter_manufacturer(client):
    r = client.get("/api/v1/plugins", params={"manufacturer": "fabfilter"})
    assert r.status_code == 200
    assert r.json()["total"] == 1


def test_list_plugins_pagination(client):
    r = client.get("/api/v1/plugins", params={"per_page": 1, "page": 2})
    assert r.status_code == 200
    data = r.json()
    assert len(data["results"]) == 1
    assert data["page"] == 2
    assert data["pages"] == 3


def test_get_plugin_by_id(client):
    r = client.get("/api/v1/plugins/fabfilter-pro-q-3")
    assert r.status_code == 200
    assert r.json()["name"] == "Pro-Q 3"


def test_get_plugin_not_found(client):
    r = client.get("/api/v1/plugins/nonexistent")
    assert r.status_code == 404


def test_pagination_invalid_page(client):
    r = client.get("/api/v1/plugins", params={"page": 0})
    assert r.status_code == 400


def test_pagination_beyond_total(client):
    r = client.get("/api/v1/plugins", params={"page": 999})
    assert r.status_code == 200
    assert r.json()["results"] == []
```

- [ ] **Step 2: Write manufacturer endpoint tests**

```python
# tests/test_manufacturers.py
"""Tests for manufacturer browse endpoints."""


def test_list_manufacturers(client):
    r = client.get("/api/v1/manufacturers")
    assert r.status_code == 200
    assert r.json()["total"] == 3


def test_get_manufacturer_detail(client):
    r = client.get("/api/v1/manufacturers/fabfilter")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "FabFilter"
    assert len(data["plugins"]) == 1


def test_manufacturer_not_found(client):
    r = client.get("/api/v1/manufacturers/nonexistent")
    assert r.status_code == 404
```

- [ ] **Step 3: Implement plugins route**

```python
# plugindb/routes/plugins.py
"""Plugin browse endpoints."""
from __future__ import annotations

import math
from fastapi import APIRouter, Query, HTTPException

from ..main import get_db
from ..models import PluginResponse, PluginListResponse
from .lookup import _build_plugin_response

router = APIRouter()


@router.get("/plugins", response_model=PluginListResponse)
def list_plugins(
    category: str | None = None,
    manufacturer: str | None = None,
    format: str | None = None,
    daw: str | None = None,
    price_type: str | None = None,
    page: int = Query(1),
    per_page: int = Query(50),
):
    if page < 1:
        raise HTTPException(status_code=400, detail={"error": "invalid_page", "message": "page must be >= 1"})
    per_page = max(1, min(200, per_page))

    conn = get_db()
    where = []
    params = []

    if category:
        where.append("p.category = ?")
        params.append(category)
    if manufacturer:
        where.append("p.manufacturer_id = ?")
        params.append(manufacturer)
    if price_type:
        where.append("p.price_type = ?")
        params.append(price_type)
    if format:
        where.append("p.formats LIKE ?")
        params.append(f'%"{format}"%')
    if daw:
        where.append("p.daws LIKE ?")
        params.append(f'%"{daw}"%')

    where_sql = " AND ".join(where) if where else "1=1"

    total = conn.execute(f"SELECT COUNT(*) FROM plugins p WHERE {where_sql}", params).fetchone()[0]
    offset = (page - 1) * per_page
    rows = conn.execute(
        f"SELECT * FROM plugins p WHERE {where_sql} ORDER BY p.name LIMIT ? OFFSET ?",
        params + [per_page, offset],
    ).fetchall()

    results = [_build_plugin_response(row, conn) for row in rows]
    return PluginListResponse(
        results=results, total=total, page=page, per_page=per_page,
        pages=math.ceil(total / per_page) if total > 0 else 0,
    )


@router.get("/plugins/{plugin_id}", response_model=PluginResponse)
def get_plugin(plugin_id: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM plugins WHERE id = ?", (plugin_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": f"Plugin '{plugin_id}' not found"})
    return _build_plugin_response(row, conn)
```

- [ ] **Step 4: Implement manufacturers route**

```python
# plugindb/routes/manufacturers.py
"""Manufacturer browse endpoints."""
from __future__ import annotations

import math
from fastapi import APIRouter, Query, HTTPException

from ..main import get_db
from ..models import ManufacturerResponse, ManufacturerListResponse, ManufacturerDetailResponse, PluginResponse
from .lookup import _build_plugin_response

router = APIRouter()


@router.get("/manufacturers", response_model=ManufacturerListResponse)
def list_manufacturers(page: int = Query(1), per_page: int = Query(50)):
    if page < 1:
        raise HTTPException(status_code=400, detail={"error": "invalid_page", "message": "page must be >= 1"})
    per_page = max(1, min(200, per_page))

    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM manufacturers").fetchone()[0]
    offset = (page - 1) * per_page
    rows = conn.execute("SELECT * FROM manufacturers ORDER BY name LIMIT ? OFFSET ?", (per_page, offset)).fetchall()

    results = [ManufacturerResponse(id=r["id"], name=r["name"], url=r["url"]) for r in rows]
    return ManufacturerListResponse(
        results=results, total=total, page=page, per_page=per_page,
        pages=math.ceil(total / per_page) if total > 0 else 0,
    )


@router.get("/manufacturers/{slug}", response_model=ManufacturerDetailResponse)
def get_manufacturer(slug: str):
    conn = get_db()
    mfr = conn.execute("SELECT * FROM manufacturers WHERE id = ?", (slug,)).fetchone()
    if mfr is None:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": f"Manufacturer '{slug}' not found"})

    plugin_rows = conn.execute("SELECT * FROM plugins WHERE manufacturer_id = ? ORDER BY name", (slug,)).fetchall()
    plugins = [_build_plugin_response(r, conn) for r in plugin_rows]

    return ManufacturerDetailResponse(id=mfr["id"], name=mfr["name"], url=mfr["url"], plugins=plugins)
```

- [ ] **Step 5: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: All passing (8 seed + 7 lookup + 8 plugins + 3 manufacturers = 26)

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: browse endpoints — plugins list/detail, manufacturers list/detail"
```

---

### Task 6: Search + meta endpoints

**Files:**
- Create: `plugindb/routes/search.py`
- Create: `plugindb/routes/meta.py`
- Create: `tests/test_search.py`
- Create: `tests/test_meta.py`

- [ ] **Step 1: Write search + meta tests**

```python
# tests/test_search.py
"""Tests for full-text search."""


def test_search_by_name(client):
    r = client.get("/api/v1/search", params={"q": "Pro-Q"})
    assert r.status_code == 200
    assert r.json()["total"] >= 1


def test_search_by_description(client):
    r = client.get("/api/v1/search", params={"q": "wavetable"})
    assert r.status_code == 200
    names = [p["name"] for p in r.json()["results"]]
    assert "Serum" in names


def test_search_by_tag(client):
    r = client.get("/api/v1/search", params={"q": "reverb"})
    assert r.status_code == 200
    assert r.json()["total"] >= 1


def test_search_with_category_filter(client):
    r = client.get("/api/v1/search", params={"q": "reverb", "category": "instrument"})
    assert r.status_code == 200
    assert r.json()["total"] == 0  # VintageVerb is effect, not instrument


def test_search_too_short(client):
    r = client.get("/api/v1/search", params={"q": "a"})
    assert r.status_code == 400


def test_search_missing_query(client):
    r = client.get("/api/v1/search")
    assert r.status_code == 422
```

```python
# tests/test_meta.py
"""Tests for stats, categories, and health endpoints."""


def test_stats(client):
    r = client.get("/api/v1/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["plugins"] == 3
    assert data["manufacturers"] == 3


def test_categories(client):
    r = client.get("/api/v1/categories")
    assert r.status_code == 200
    cats = r.json()["categories"]
    assert "instrument" in cats
    assert "effect" in cats


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
```

- [ ] **Step 2: Implement search route**

```python
# plugindb/routes/search.py
"""Full-text search endpoint."""
from __future__ import annotations

import math
from fastapi import APIRouter, Query, HTTPException

from ..main import get_db
from ..models import PluginListResponse
from .lookup import _build_plugin_response

router = APIRouter()


@router.get("/search", response_model=PluginListResponse)
def search(
    q: str = Query(..., min_length=1),
    category: str | None = None,
    page: int = Query(1),
    per_page: int = Query(50),
):
    if len(q) < 2:
        raise HTTPException(status_code=400, detail={"error": "query_too_short", "message": "Query must be at least 2 characters"})
    if page < 1:
        raise HTTPException(status_code=400, detail={"error": "invalid_page", "message": "page must be >= 1"})
    per_page = max(1, min(200, per_page))

    conn = get_db()

    # FTS5 search
    fts_query = q + "*"  # prefix matching
    where_extra = ""
    params_extra: list = []
    if category:
        where_extra = "AND p.category = ?"
        params_extra = [category]

    count_sql = f"""
        SELECT COUNT(*) FROM plugins_fts f
        JOIN plugins p ON f.plugin_id = p.id
        WHERE plugins_fts MATCH ? {where_extra}
    """
    total = conn.execute(count_sql, [fts_query] + params_extra).fetchone()[0]

    offset = (page - 1) * per_page
    rows_sql = f"""
        SELECT p.* FROM plugins_fts f
        JOIN plugins p ON f.plugin_id = p.id
        WHERE plugins_fts MATCH ? {where_extra}
        ORDER BY rank
        LIMIT ? OFFSET ?
    """
    rows = conn.execute(rows_sql, [fts_query] + params_extra + [per_page, offset]).fetchall()

    results = [_build_plugin_response(row, conn) for row in rows]
    return PluginListResponse(
        results=results, total=total, page=page, per_page=per_page,
        pages=math.ceil(total / per_page) if total > 0 else 0,
    )
```

- [ ] **Step 3: Implement meta route**

```python
# plugindb/routes/meta.py
"""Stats, categories, and health endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from ..main import get_db
from .. import __version__
from ..models import StatsResponse, CategoriesResponse, HealthResponse

router = APIRouter()

TAXONOMY = {
    "instrument": ["synth", "sampler", "drum-machine", "rompler", "organ", "piano", "guitar", "general"],
    "effect": ["eq", "compressor", "limiter", "gate", "reverb", "delay", "distortion", "saturation", "filter", "modulation", "chorus", "phaser", "flanger", "pitch", "vocoder", "de-esser", "multiband", "general"],
    "container": ["layer", "selector", "splitter", "chain", "general"],
    "note-effect": ["arpeggiator", "quantize", "transpose", "harmonize", "strum", "general"],
    "utility": ["analyzer", "meter", "test-tone", "routing", "sidechain", "tuner", "general"],
    "midi": ["sequencer", "generator", "filter", "general"],
}


@router.get("/api/v1/stats", response_model=StatsResponse)
def stats():
    conn = get_db()
    plugins = conn.execute("SELECT COUNT(*) FROM plugins").fetchone()[0]
    manufacturers = conn.execute("SELECT COUNT(*) FROM manufacturers").fetchone()[0]
    aliases = conn.execute("SELECT COUNT(*) FROM aliases").fetchone()[0]
    last = conn.execute("SELECT MAX(updated_at) FROM plugins").fetchone()[0]

    return StatsResponse(
        plugins=plugins, manufacturers=manufacturers, aliases=aliases,
        last_updated=last, version=__version__,
    )


@router.get("/api/v1/categories", response_model=CategoriesResponse)
def categories():
    return CategoriesResponse(categories=TAXONOMY)


@router.get("/health", response_model=HealthResponse)
def health():
    conn = get_db()
    plugins = conn.execute("SELECT COUNT(*) FROM plugins").fetchone()[0]
    return HealthResponse(status="ok", plugins=plugins, version=__version__)
```

- [ ] **Step 4: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: All passing (~35 tests)

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: search (FTS5) + stats + categories + health endpoints"
```

---

### Task 7: README + Dockerfile + CI

**Files:**
- Create: `README.md`
- Create: `Dockerfile`
- Create: `.github/workflows/test.yml`
- Create: `.github/workflows/validate-seed.yml`

- [ ] **Step 1: Create README.md**

A proper README with: what it is, quickstart (run locally), API overview with curl examples, how to contribute (PR to seed.json), license.

- [ ] **Step 2: Create Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY . .
RUN python -m plugindb.seed

EXPOSE 8000
CMD ["uvicorn", "plugindb.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: Create CI workflows**

`test.yml` — runs pytest on every push/PR.
`validate-seed.yml` — validates `data/seed.json` schema on PRs that touch it.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: README, Dockerfile, GitHub Actions CI"
```

---

### Task 8: Final validation

- [ ] **Step 1: Run full test suite**

Run: `python -m pytest tests/ -v`
Expected: All 35+ tests pass

- [ ] **Step 2: Start the server locally and test**

Run: `python -m plugindb.seed && uvicorn plugindb.main:create_app --factory --reload`
Then test: `curl http://localhost:8000/api/v1/lookup?alias=FabfilterProQ3`
Expected: Full plugin JSON response

- [ ] **Step 3: Test the docs page**

Open: `http://localhost:8000/docs`
Expected: Interactive Swagger UI with all endpoints

- [ ] **Step 4: Test batch lookup**

Run: `curl -X POST http://localhost:8000/api/v1/lookup -H "Content-Type: application/json" -d '{"aliases":["Serum","OTT","Unknown"]}'`
Expected: Results map with Serum matched, OTT matched, Unknown null

- [ ] **Step 5: Verify health endpoint**

Run: `curl http://localhost:8000/health`
Expected: `{"status":"ok","plugins":272,"version":"1.0.0"}`

- [ ] **Step 6: Final commit**

```bash
git add -A
git commit -m "feat: PluginDB Core API v1.0.0 — complete"
```

---

## Summary

| Task | What | Tests |
|------|------|-------|
| 1 | Project scaffold + database schema | 3 |
| 2 | Seed pipeline + data import | 5 |
| 3 | Pydantic response models | 0 (type-checked by FastAPI) |
| 4 | FastAPI app + lookup endpoint | 7 |
| 5 | Browse endpoints (plugins + manufacturers) | 11 |
| 6 | Search + meta endpoints | 9 |
| 7 | README + Docker + CI | 0 (infra) |
| 8 | Final validation | Manual |
| **Total** | | **~35 tests** |
