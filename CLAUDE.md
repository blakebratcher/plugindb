# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

PluginDB is an open database and REST API for audio production plugins (VSTs, Audio Units, CLAP) with a web frontend. Python/FastAPI backend with SQLite (in-process, no external DB server). Vanilla HTML/CSS/JS frontend served by FastAPI. The canonical data source is `data/seed.json` — the SQLite DB is derived from it at startup. Read-only API; all data changes go through GitHub PRs to seed.json.

## Commands

```bash
# Install (editable, with test deps)
pip install -e ".[dev]"

# Seed the SQLite database (auto-detects schema changes)
python -m plugindb.seed

# Validate seed.json only (no DB write)
python -m plugindb.seed --validate

# Run the API server (also: python -m plugindb)
uvicorn plugindb.main:create_app --factory --host 0.0.0.0 --port 8000

# Run all tests
python -m pytest tests/ -v

# Run a single test
python -m pytest tests/test_plugins.py::TestSorting -v
```

After modifying `data/seed.json`, re-run `python -m plugindb.seed`. Schema changes are auto-detected and the DB is rebuilt automatically.

## Architecture

**Data flow:** `data/seed.json` → `plugindb/seed.py` (validate + import) → SQLite → FastAPI routes

- **`main.py`** — App factory. DB injection for tests. Rate limiting (100/min), CORS, GZip (>1KB), ETag/conditional caching (304), timing headers (X-Processing-Time-Ms), global exception handler, structured logging, API root at `/`.
- **`database.py`** — Schema (5 tables: manufacturers, plugins, aliases, plugins_fts, metadata). WAL, FK, `check_schema()` for auto-migration.
- **`seed.py`** — Load, validate, import. Validates categories, formats, price_types, year range, tags. Stores seed hash + timestamp in metadata table. Auto-migration on schema changes.
- **`queries.py`** — `build_plugin_response()` (single), `build_plugin_responses()` (batch, 3 queries total).
- **`models.py`** — Pydantic models. `ManufacturerWithCountResponse`, `ComparisonResponse`, `SuggestItemResponse`, `YearsResponse`, `ErrorResponse` in OpenAPI.
- **`routes/`** — `lookup.py` (bulk-optimized batch with duplicate detection), `search.py` (FTS5 + sorting + suggest with rich results), `plugins.py` (filters/sort/compare/similar/include), `manufacturers.py` (search/sort/plugin_count/categories/pagination), `meta.py` (stats/categories/subcategories/tags/formats/os/years/version/export/health).

**Key design decisions:**
- JSON array columns (formats, daws, os, tags) — LIKE substring filtering. Filter validation on category/price_type (400 on invalid).
- FTS5 contentless — indexes name, manufacturer_name, category, subcategory, description, aliases, tags. Rebuilt on seed.
- ETag caching — seed fingerprint used for conditional 304 responses. Cache-Control: public, max-age=3600.
- Related tags — computed on filtered /plugins results, excludes filtered tags, top 10 by frequency.
- Similar plugins — scored by tag overlap within same category/subcategory.
- Include parameter — `?include=manufacturer_plugins` on detail endpoints.

## API Surface

**Root:** `GET /` (name, version, data_version, API versions)
**Health:** `GET /health`, `GET /api/v1/health` (enriched: plugin_count, manufacturer_count, data_version, uptime)
**Lookup:** `GET /lookup?alias=X`, `POST /lookup` (batch 200, duplicate detection)
**Search:** `GET /search?q=X` (all filters + sort + order), `GET /suggest?q=X` (rich results with name/slug/category/manufacturer)
**Plugins:** `GET /plugins` (all filters + sort + related_tags), `GET /plugins/compare?ids=1,2`, `GET /plugins/random`, `GET /plugins/by-slug/{slug}`, `GET /plugins/{id}` (with `?include=manufacturer_plugins`), `GET /plugins/{id}/similar`
**Manufacturers:** `GET /manufacturers` (search, sort: name/plugin_count, with counts), `GET /manufacturers/{slug}` (paginated, with categories)
**Meta:** `GET /stats`, `GET /categories`, `GET /subcategories`, `GET /tags`, `GET /formats`, `GET /os`, `GET /years`, `GET /version`, `GET /export` (JSON/CSV)

Swagger at `/docs`, ReDoc at `/redoc`.

## Frontend

Vanilla SPA in `frontend/` (index.html, style.css, app.js, favicon.svg). No build tools, no npm.

- Hash-based router (`#/path`) — no server-side routing needed
- Content negotiation on `/` — HTML for browsers (`Accept: text/html`), JSON for API clients
- `StaticFiles` mounted last in FastAPI (catch-all, `html=True`)
- Debounced typeahead using `/suggest` endpoint
- Filter state encoded in URL hash for bookmarkability
- Dark theme via CSS custom properties (audio production aesthetic)
- Responsive (mobile-friendly at 768px and 480px breakpoints)
- All user data escaped via `escapeHtml()` to prevent XSS

## Community

- GitHub Issue templates: plugin submission (structured form), data correction
- PR template with validation checklist
- CONTRIBUTING.md with data format docs and valid field values
- CI runs full test suite + seed stats summary on data PRs

## Testing

In-memory SQLite via `create_app(db_connection=...)`. Fixtures: `seed_data` (3 mfrs, 3 plugins with tags/year/price_type/os), `seeded_db`, `client`.

## Database Schema

5 tables + FTS5. WAL, FK ON. Indexes: manufacturer_id, category, slug, year, price_type, aliases.name_lower, aliases.plugin_id.

- **manufacturers** — id, slug (UNIQUE), name, website, created_at
- **plugins** — id, slug (UNIQUE), name, manufacturer_id (FK), category, subcategory, formats/daws/os/tags (JSON), description, website, is_free, price_type, year, created_at, updated_at
- **aliases** — id, plugin_id (FK CASCADE), name, name_lower
- **plugins_fts** — FTS5 contentless, rowid = plugins.id
- **metadata** — key (PK), value (seed_hash, seed_timestamp)

## seed.json → DB

- `manufacturer_slug` → `manufacturer_id` (FK); `price_type` → stored + derived `is_free`; `url` → `website`; `aliases` → table; `formats/daws/os/tags` → JSON; `year` → nullable int

## Docker

Multi-stage (builder → seeder → runtime) from `python:3.12-slim`. Frontend files copied in runtime stage. `.dockerignore` excludes tests/docs. Healthcheck every 30s.

## CI

- **`test.yml`** — Push/PR to main. Python 3.12 + 3.13.
- **`validate-seed.yml`** — PRs touching `data/`. Schema + import validation.

## Package

- Version: `1.4.0`
- License: MIT (Blake Bratcher)
- Python: `>=3.12`
- Runtime: `fastapi`, `uvicorn[standard]`, `slowapi`
- Dev: `pytest`, `httpx`
