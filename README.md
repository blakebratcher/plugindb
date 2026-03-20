# PluginDB

[![Tests](https://github.com/blakebratcher/plugindb/actions/workflows/test.yml/badge.svg)](https://github.com/blakebratcher/plugindb/actions/workflows/test.yml)
[![Docker](https://github.com/blakebratcher/plugindb/actions/workflows/deploy.yml/badge.svg)](https://github.com/blakebratcher/plugindb/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Data: CC0](https://img.shields.io/badge/data-CC0-green.svg)](https://creativecommons.org/publicdomain/zero/1.0/)

The open database for audio production plugins. Search, browse, and discover VSTs, Audio Units, and CLAP plugins through a clean web interface or a powerful REST API.

> Think MusicBrainz, but for audio plugins. 1,000+ plugins from 220+ manufacturers — and growing.

### Deploy Your Own

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/blakebratcher/plugindb) [![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/template/blakebratcher/plugindb)

Or pull the Docker image: `docker pull ghcr.io/blakebratcher/plugindb:latest`

## Quickstart

```bash
pip install -e ".[dev]"
python -m plugindb.seed
uvicorn plugindb.main:create_app --factory --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 for the web UI, or http://localhost:8000/docs for the API explorer.

## Features

- **Instant lookup** — resolve any plugin name or alias in milliseconds
- **Full-text search** — FTS5-powered search across names, descriptions, tags, and aliases
- **Rich filtering** — category, subcategory, format, OS, DAW, tags, price type, year ranges
- **Similar plugins** — discover alternatives based on tag overlap
- **Autocomplete** — typeahead suggestions with manufacturer context
- **Batch lookup** — resolve up to 200 plugin names in a single request
- **Bulk export** — download the entire catalog as JSON or CSV
- **Plugin comparison** — compare 2-5 plugins side by side
- **HTTP caching** — ETag + Cache-Control for efficient client caching
- **Zero dependencies frontend** — vanilla HTML/CSS/JS, no build tools

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check (enriched with counts and uptime) |
| `GET` | `/api/v1/lookup?alias=X` | Resolve a plugin by name or alias |
| `POST` | `/api/v1/lookup` | Batch resolve up to 200 names |
| `GET` | `/api/v1/search?q=X` | Full-text search with filters and sorting |
| `GET` | `/api/v1/suggest?q=X` | Autocomplete suggestions |
| `GET` | `/api/v1/plugins` | Browse plugins (filterable, sortable, paginated) |
| `GET` | `/api/v1/plugins/compare?ids=1,2` | Compare 2-5 plugins side by side |
| `GET` | `/api/v1/plugins/random` | Get a random plugin |
| `GET` | `/api/v1/plugins/by-slug/{slug}` | Get a plugin by slug |
| `GET` | `/api/v1/plugins/{id}` | Get a plugin by ID |
| `GET` | `/api/v1/plugins/{id}/similar` | Find similar plugins |
| `GET` | `/api/v1/manufacturers` | Browse manufacturers (with plugin counts) |
| `GET` | `/api/v1/manufacturers/{slug}` | Manufacturer detail with plugins |
| `GET` | `/api/v1/stats` | Database statistics |
| `GET` | `/api/v1/categories` | Category taxonomy |
| `GET` | `/api/v1/subcategories` | Subcategories with plugin counts |
| `GET` | `/api/v1/tags` | All tags with counts |
| `GET` | `/api/v1/formats` | All formats with counts |
| `GET` | `/api/v1/os` | OS platforms with counts |
| `GET` | `/api/v1/years` | Plugin counts by year |
| `GET` | `/api/v1/version` | Data and API version info |
| `GET` | `/api/v1/export` | Bulk export (JSON or CSV) |

### Examples

```bash
# Look up a plugin by alias
curl "http://localhost:8000/api/v1/lookup?alias=OTT"

# Full-text search
curl "http://localhost:8000/api/v1/search?q=reverb&category=effect&sort=year&order=desc"

# Batch lookup
curl -X POST "http://localhost:8000/api/v1/lookup" \
  -H "Content-Type: application/json" \
  -d '{"names": ["Serum", "Diva", "OTT"]}'

# Filter by tag, year range, and OS
curl "http://localhost:8000/api/v1/plugins?tag=synthesizer&year_min=2020&os=linux"

# Multi-tag filter (AND logic)
curl "http://localhost:8000/api/v1/plugins?tags=synthesizer,analog-modeling"

# Compare plugins
curl "http://localhost:8000/api/v1/plugins/compare?ids=1,2,3"

# Similar plugins
curl "http://localhost:8000/api/v1/plugins/1/similar"

# Autocomplete
curl "http://localhost:8000/api/v1/suggest?q=Ser"

# Bulk export as CSV
curl "http://localhost:8000/api/v1/export?format=csv" -o plugins.csv
```

## Frontend

The web frontend is a lightweight single-page application using vanilla HTML, CSS, and JavaScript — no frameworks, no build steps. It lives in `frontend/` and is served directly by FastAPI.

## Running Tests

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

## Contributing

Plugin data lives in `data/seed.json`. See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions on:
- Submitting new plugins (via GitHub Issue form or PR)
- Reporting data corrections
- Contributing code

PRs that touch `data/seed.json` are automatically validated by CI.

## Docker

```bash
docker build -t plugindb .
docker run -p 8000:8000 plugindb
```

## License

- **Code:** MIT (see [LICENSE](LICENSE))
- **Data** (`data/seed.json`): CC0 1.0 Universal (public domain)
