---
type: spec
status: active
date-created: 2026-03-18
sub-project: 1 of 4 (Core API)
---

# PluginDB Core API — Design Spec

## Overview

PluginDB is an open, community-driven database of audio production plugins — the canonical source of truth for "what is this plugin?" Developers query the API to normalize plugin filenames into structured metadata. Think MusicBrainz for VSTs.

**Domain:** plugindb.org
**API base:** api.plugindb.org/v1
**License:** MIT (code), CC0 (data — public domain, like MusicBrainz)
**First consumer:** Bitwig OS vault (replaces local `plugin-registry.json` with API lookups)
**Seed data:** 272 entries from the Bitwig OS registry

## Problem

There is no canonical, open, community-driven database for audio production plugins. Every producer and every DAW tool faces the same problem:

- Plugin filenames are cryptic (`FabfilterProQ3.vst3`, `ValhallaVintageVerb_x64.dll`)
- No standardized metadata — category, manufacturer, format, description
- KVR Audio has data but no open API
- Plugin Boutique and Splice are stores, not databases
- Every tool that needs plugin metadata builds its own incomplete mapping

PluginDB solves this by providing a single API that answers: "Given this filename, what plugin is it, who makes it, what does it do, and what category is it?"

## Tech Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.12+ | Existing expertise (Bitwig OS pipeline), fast development |
| Framework | FastAPI | Auto-generated OpenAPI docs, async support, modern Python |
| Database | SQLite | Zero ops, single file, FTS5 for search, upgrade to Postgres later |
| ORM | None (raw `sqlite3`) | Stdlib only, no extra dependencies, full control |
| Server | Uvicorn | ASGI server for FastAPI, production-grade |
| Deploy | Railway or Render (free tier) | Zero-config deploy from GitHub, auto-deploy on push |
| Repo | github.com/[user]/plugindb | Public repo, contributions via PRs |

**Dependencies (minimal):**
- `fastapi` — web framework
- `uvicorn` — ASGI server
- No other runtime dependencies (sqlite3 is stdlib)

## Data Model

### `manufacturers` table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | TEXT | PRIMARY KEY | Kebab-case slug (`fabfilter`) |
| `name` | TEXT | NOT NULL | Display name (`FabFilter`) |
| `url` | TEXT | | Company website |
| `created_at` | TEXT | NOT NULL | ISO 8601 timestamp |
| `updated_at` | TEXT | NOT NULL | ISO 8601 timestamp |

### `plugins` table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | TEXT | PRIMARY KEY | Kebab-case unique ID (`fabfilter-pro-q-3`) |
| `name` | TEXT | NOT NULL | Canonical display name (`Pro-Q 3`) |
| `manufacturer_id` | TEXT | NOT NULL, FK → manufacturers.id | Manufacturer reference |
| `category` | TEXT | NOT NULL | Top-level category (see taxonomy) |
| `subcategory` | TEXT | DEFAULT 'general' | Specific type within category |
| `description` | TEXT | | 1-2 sentence summary |
| `formats` | TEXT | | JSON array: `["VST3", "CLAP", "AU", "AAX"]` |
| `daws` | TEXT | | JSON array: `["Bitwig", "Ableton", "Logic", ...]` |
| `os` | TEXT | | JSON array: `["windows", "macos", "linux"]` |
| `price_type` | TEXT | | `free`, `paid`, `subscription`, `freemium` |
| `tags` | TEXT | | JSON array: `["equalizer", "dynamic-eq", ...]` |
| `year` | INTEGER | | Initial release year |
| `url` | TEXT | | Official product page |
| `created_at` | TEXT | NOT NULL | ISO 8601 timestamp |
| `updated_at` | TEXT | NOT NULL | ISO 8601 timestamp |

### `aliases` table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `lookup_key` | TEXT | PRIMARY KEY | Lowercased filename variant for matching (`fabfilterproq3`) |
| `display` | TEXT | NOT NULL | Original-case alias for API responses (`FabfilterProQ3`) |
| `plugin_id` | TEXT | NOT NULL, FK → plugins.id ON DELETE CASCADE | Plugin this alias resolves to |

Separate table for O(1) lookup performance. Index on `lookup_key`. The `display` column preserves original casing for API responses while `lookup_key` enables case-insensitive matching.

### `plugins_fts` virtual table (FTS5)

Full-text search index across `name`, `description`, `tags`, and manufacturer name. Rebuilt on seed/update.

### Taxonomy

| Category | Subcategories |
|----------|--------------|
| `instrument` | `synth`, `sampler`, `drum-machine`, `rompler`, `organ`, `piano`, `guitar`, `general` |
| `effect` | `eq`, `compressor`, `limiter`, `gate`, `reverb`, `delay`, `distortion`, `saturation`, `filter`, `modulation`, `chorus`, `phaser`, `flanger`, `pitch`, `vocoder`, `de-esser`, `multiband`, `general` |
| `container` | `layer`, `selector`, `splitter`, `chain`, `general` |
| `note-effect` | `arpeggiator`, `quantize`, `transpose`, `harmonize`, `strum`, `general` |
| `utility` | `analyzer`, `meter`, `test-tone`, `routing`, `sidechain`, `tuner`, `general` |
| `midi` | `sequencer`, `generator`, `filter`, `general` |

## API Endpoints

### Lookup (the killer feature)

```
GET /api/v1/lookup?alias=FabfilterProQ3

200: { "id": "fabfilter-pro-q-3", "name": "Pro-Q 3", ... }
404: { "error": "not_found", "alias": "FabfilterProQ3" }
```

Case-insensitive exact match against the `aliases` table. Sub-10ms target. This is the endpoint that replaces local registry files in DAW tools.

### Browse

```
GET /api/v1/plugins?category=effect&format=VST3&manufacturer=fabfilter&daw=Bitwig&price_type=paid&page=1&per_page=50
GET /api/v1/plugins/{id}
GET /api/v1/manufacturers?page=1&per_page=50
GET /api/v1/manufacturers/{slug}
```

All list endpoints are paginated (default 50, max 200). All filter params are optional and combinable. Plugin detail embeds the full manufacturer object and aliases list. Manufacturer detail includes full plugin catalog.

### Search

```
GET /api/v1/search?q=reverb&category=effect&page=1&per_page=50

200: { "results": [...], "total": 47, "page": 1, "per_page": 50 }
```

SQLite FTS5 full-text search across name, manufacturer name, description, and tags. Supports natural language queries. Filter params narrow results.

### Meta

```
GET /api/v1/stats
→ { "plugins": 272, "manufacturers": 74, "aliases": 891, "last_updated": "2026-03-18T..." }

GET /api/v1/categories
→ { "instrument": ["synth", "sampler", ...], "effect": ["eq", "compressor", ...], ... }
```

### Response Format

Every plugin response uses this structure:

```json
{
  "id": "fabfilter-pro-q-3",
  "name": "Pro-Q 3",
  "manufacturer": {
    "id": "fabfilter",
    "name": "FabFilter",
    "url": "https://www.fabfilter.com"
  },
  "category": "effect",
  "subcategory": "eq",
  "description": "Parametric EQ with dynamic bands, linear phase mode, and mid/side processing.",
  "formats": ["VST3", "CLAP", "AU", "AAX"],
  "daws": ["Bitwig", "Ableton", "Logic", "FL Studio", "Reaper", "Cubase", "Studio One"],
  "os": ["windows", "macos"],
  "price_type": "paid",
  "tags": ["equalizer", "dynamic-eq", "linear-phase", "mid-side"],
  "year": 2018,
  "url": "https://www.fabfilter.com/products/pro-q-3-equalizer-plug-in",
  "aliases": ["FabfilterProQ3", "FabFilter Pro-Q 3", "Pro-Q3", "ProQ3"]
}
```

List responses wrap results in pagination:

```json
{
  "results": [...],
  "total": 272,
  "page": 1,
  "per_page": 50,
  "pages": 6
}
```

### Error Responses

```json
{
  "error": "not_found",
  "message": "No plugin found matching alias 'UnknownPlugin'",
  "alias": "UnknownPlugin"
}
```

Standard HTTP status codes: 200 (success), 404 (not found), 400 (bad request), 422 (validation error), 500 (server error).

## Project Structure

```
plugindb/
├── README.md
├── LICENSE                      # MIT
├── pyproject.toml               # fastapi, uvicorn
├── plugindb/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app, CORS, lifespan
│   ├── database.py              # SQLite connection, schema, FTS5
│   ├── models.py                # Pydantic response models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── lookup.py            # GET /lookup
│   │   ├── plugins.py           # GET /plugins, /plugins/{id}
│   │   ├── manufacturers.py     # GET /manufacturers, /manufacturers/{slug}
│   │   ├── search.py            # GET /search
│   │   └── meta.py              # GET /stats, /categories
│   └── seed.py                  # Import from seed.json → SQLite
├── data/
│   ├── plugindb.sqlite          # Database file (gitignored)
│   └── seed.json                # Seed data (272 entries, checked in)
├── tests/
│   ├── conftest.py              # Test client + in-memory SQLite
│   ├── test_lookup.py
│   ├── test_plugins.py
│   ├── test_manufacturers.py
│   ├── test_search.py
│   └── test_meta.py
├── .github/
│   └── workflows/
│       ├── test.yml             # Run tests on every PR
│       └── validate-seed.yml    # Validate seed.json schema on PR
├── .gitignore
├── Dockerfile                   # For Railway/Render deploy
└── render.yaml                  # Or railway.toml — deploy config
```

## Seed Data Pipeline

One-time import that converts the Bitwig OS `plugin-registry.json` into PluginDB's format:

1. Read `plugin-registry.json` (272 entries from Bitwig OS vault)
2. Extract unique manufacturers → `manufacturers` table
3. Insert plugins with FK references → `plugins` table
4. Populate aliases (lowercased) → `aliases` table
5. Build FTS5 index → `plugins_fts` virtual table

The seed script (`plugindb/seed.py`) is idempotent — running it twice produces the same database. It can also incrementally update when `seed.json` grows.

After seeding, `data/seed.json` remains the human-editable source of truth. All contributions happen in this file via GitHub PRs. The database is derived from it.

## Community Contributions (v1)

**Mechanism:** GitHub pull requests against `data/seed.json`.

**Workflow:**
1. Contributor forks the repo
2. Adds/edits entries in `data/seed.json`
3. Opens a PR
4. GitHub Actions runs validation (schema check, duplicate ID detection, alias conflict detection, required fields)
5. Maintainer reviews and merges
6. Deploy hook re-seeds the database and restarts the API

**Validation rules (enforced by CI):**
- Every entry must have: `id`, `name`, `manufacturer`, `category`, `aliases`
- `id` must be unique and kebab-case
- `aliases` must be unique across all entries (case-insensitive)
- `category` must be from the valid taxonomy
- No empty `name`, `manufacturer`, or `aliases` arrays

**Why GitHub PRs:**
- Zero auth infrastructure needed
- Built-in review/discussion workflow
- Full edit history via git
- Developers (the v1 audience) already know how to submit PRs
- Web submission form comes in a later sub-project when non-developer users arrive

## Deployment

**Initial:** Railway or Render free tier
- Auto-deploy on push to `main`
- SQLite file persists on disk (Railway volumes, Render persistent disk)
- Custom domain: `api.plugindb.org`
- HTTPS via platform (automatic)

**Scaling path (when needed):**
1. Free tier → $5/mo VPS (handles thousands of req/sec with SQLite)
2. SQLite → PostgreSQL (when concurrent writes matter — i.e., when the web submission form exists)
3. Add Redis cache for `/lookup` if latency matters at scale
4. CDN for the API if global latency matters

**For launch, SQLite + free tier handles everything.** SQLite can serve ~50,000 reads/sec on a single core. PluginDB won't see that kind of traffic for a long time.

## Data Completeness at Launch

The seed data (272 entries from Bitwig OS registry) has **complete coverage** for: `id`, `name`, `manufacturer`, `category`, `subcategory`, `aliases`, `formats`.

These fields will be **empty/null at launch** for most entries: `description`, `daws`, `os`, `price_type`, `year`, `url`.

**Null handling in API responses:** Null fields are included in the response as `null` (not omitted). Empty arrays render as `[]`. This makes the schema predictable for consumers — every field is always present.

**Enrichment strategy (post-launch):**
1. Maintainer manually enriches the top ~50 most-used plugins (descriptions, DAW compatibility, pricing)
2. Community PRs gradually fill in the rest
3. The `/stats` endpoint tracks completion percentage so progress is visible

## Seed Transformation

The Bitwig OS `plugin-registry.json` must be transformed before becoming `seed.json`:

1. **Strip Bitwig-specific fields:** Remove `source`, `vault_note` from all entries
2. **Extract manufacturers:** Generate `manufacturers` array from unique manufacturer strings
3. **Generate manufacturer slugs:** Lowercase, replace spaces/special chars with hyphens, strip non-alphanumeric. `"Air Music Technology"` → `air-music-technology`. `"iZotope"` → `izotope`.
4. **Deduplicate manufacturers:** Normalize casing before dedup (`"iZotope"` and `"Izotope"` merge)
5. **Validate format values:** Only allow: `VST2`, `VST3`, `CLAP`, `AU`, `AAX`. Strip non-standard values like `"Ableton Live instrument"`.
6. **Add `schema_version: "1.0"`** to seed.json root

**Plugin ID convention:** `{manufacturer-slug}-{plugin-name-slug}`. Examples: `fabfilter-pro-q-3`, `xfer-serum`, `valhalla-vintage-verb`. Existing IDs that don't follow this convention are grandfathered.

## Rate Limiting

Basic rate limiting from day one via `slowapi` middleware:
- **100 requests/minute per IP** for all endpoints
- **429 Too Many Requests** response with `Retry-After` header
- Sufficient to prevent abuse without impacting legitimate use
- No API keys required — IP-based throttling only

## SQLite Configuration

- **WAL mode** enabled for concurrent reads during writes
- **Re-seed strategy:** Seed to a new `.sqlite` file, then atomically rename to replace the active database. Zero downtime during re-seed.
- **FK cascades:** `ON DELETE CASCADE` on all foreign keys. The seed script drops and recreates all data in a single transaction.

## Additional Endpoints

**Health check (for deploy platforms):**
```
GET /health
→ { "status": "ok", "plugins": 272, "version": "1.0.0" }
```

**Batch lookup (for bulk consumers like Bitwig OS):**
```
POST /api/v1/lookup
Body: { "aliases": ["FabfilterProQ3", "ValhallaVintageVerb", "UnknownPlugin"] }

→ 200: {
    "results": {
      "FabfilterProQ3": { "id": "fabfilter-pro-q-3", "name": "Pro-Q 3", ... },
      "ValhallaVintageVerb": { "id": "valhalla-vintage-verb", "name": "VintageVerb", ... },
      "UnknownPlugin": null
    },
    "matched": 2,
    "unmatched": 1
  }
```

Max 200 aliases per batch request. Returns a map of alias → plugin (or null for misses).

## Search Constraints

- Minimum query length: **2 characters**. Queries shorter than 2 chars return 400 with `"error": "query_too_short"`.
- FTS5 natural language mode (no special syntax required)
- Results ranked by relevance (FTS5 rank function)

## CORS Policy

`allow_origins=["*"]` — fully open. This is a public, read-only API with no auth. Any website or tool can call it directly from the browser.

## Pagination Rules

- `page` minimum: 1. Values < 1 return 400.
- `per_page` range: 1-200. Values outside this range are clamped (not errored).
- `page` beyond total pages returns empty `results: []` (not 404).
- Default: `page=1, per_page=50`.

## What's NOT in v1

- No frontend website (FastAPI auto-docs at `/docs` is the browsing interface)
- No user auth / API keys
- No write API endpoints beyond batch lookup (all data changes via GitHub PRs to seed.json)
- No image uploads or screenshots
- No user ratings or reviews
- No caching layer (SQLite is fast enough)
- No webhooks or real-time updates

## Future Sub-projects

| # | Sub-project | Depends On | Description |
|---|-------------|-----------|-------------|
| 2 | Community contribution system | Core API | Web submission form, moderation queue, user accounts |
| 3 | Frontend website | Core API | Browse, search, plugin pages — the plugindb.org experience |
| 4 | Integrations | Core API | Bitwig OS network lookup, DAW scanner tool, other consumers |

## Success Criteria

- [ ] API serves `/lookup` responses in <10ms
- [ ] All 272 seed entries queryable via the API
- [ ] All 8 endpoints return correct responses with proper pagination
- [ ] FTS5 search returns relevant results for natural language queries
- [ ] GitHub Actions validates seed.json on every PR
- [ ] API auto-deploys on push to main
- [ ] FastAPI auto-docs page at `/docs` is functional and browsable
- [ ] Bitwig OS vault can be configured to use the API instead of local registry
- [ ] Zero external dependencies beyond fastapi + uvicorn
