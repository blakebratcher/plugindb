# PluginDB

An open database and REST API for audio production plugins. Think MusicBrainz, but for VSTs, Audio Units, and CLAP plugins. PluginDB provides instant alias-based lookup, full-text search, and a structured taxonomy of instruments, effects, containers, and utilities used in modern music production.

## Quickstart

```bash
# Install
pip install -e ".[dev]"

# Seed the database from data/seed.json
python -m plugindb.seed

# Run the server
uvicorn plugindb.main:create_app --factory --host 0.0.0.0 --port 8000
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/lookup?alias=X` | Resolve a plugin by name or alias |
| `POST` | `/api/v1/lookup` | Batch resolve up to 200 names |
| `GET` | `/api/v1/search?q=X` | Full-text search (min 2 chars) |
| `GET` | `/api/v1/suggest?q=X` | Autocomplete suggestions (up to 10 names) |
| `GET` | `/api/v1/plugins` | List all plugins (paginated, filterable, sortable) |
| `GET` | `/api/v1/plugins/random` | Get a random plugin |
| `GET` | `/api/v1/plugins/by-slug/{slug}` | Get a plugin by slug |
| `GET` | `/api/v1/plugins/{id}` | Get a single plugin by ID |
| `GET` | `/api/v1/plugins/{id}/similar` | Find similar plugins by tag overlap |
| `GET` | `/api/v1/manufacturers` | List manufacturers (paginated, searchable, sortable) |
| `GET` | `/api/v1/manufacturers/{slug}` | Get a manufacturer + paginated plugins |
| `GET` | `/api/v1/stats` | Database statistics |
| `GET` | `/api/v1/categories` | Plugin category taxonomy |
| `GET` | `/api/v1/subcategories` | Subcategories with actual plugin counts |
| `GET` | `/api/v1/tags` | All tags with usage counts |
| `GET` | `/api/v1/formats` | All formats with usage counts |
| `GET` | `/api/v1/os` | All operating systems with usage counts |
| `GET` | `/api/v1/years` | Plugin counts by release year |
| `GET` | `/api/v1/version` | Data and API version info |
| `GET` | `/api/v1/export` | Bulk export (JSON or CSV) |
| `GET` | `/api/v1/plugins/compare?ids=1,2` | Compare 2-5 plugins side by side |

### Examples

```bash
# Look up a plugin by alias
curl "http://localhost:8000/api/v1/lookup?alias=OTT"

# Full-text search with category filter
curl "http://localhost:8000/api/v1/search?q=reverb&category=effect"

# Batch lookup
curl -X POST "http://localhost:8000/api/v1/lookup" \
  -H "Content-Type: application/json" \
  -d '{"names": ["Serum", "Diva", "OTT"]}'

# List plugins filtered by format
curl "http://localhost:8000/api/v1/plugins?format=VST3&per_page=10"

# Filter by tag and year
curl "http://localhost:8000/api/v1/plugins?tag=synthesizer&year=2014"

# Filter by price type
curl "http://localhost:8000/api/v1/plugins?price_type=free"

# Sort by year, descending
curl "http://localhost:8000/api/v1/plugins?sort=year&order=desc"

# Year range filter
curl "http://localhost:8000/api/v1/plugins?year_min=2020&year_max=2025"

# Multi-tag filter (AND logic)
curl "http://localhost:8000/api/v1/plugins?tags=synthesizer,analog-modeling"

# Get a random plugin
curl "http://localhost:8000/api/v1/plugins/random"

# Autocomplete suggestions
curl "http://localhost:8000/api/v1/suggest?q=Ser"

# Filter by subcategory and OS
curl "http://localhost:8000/api/v1/plugins?subcategory=synth&os=linux"

# Find similar plugins
curl "http://localhost:8000/api/v1/plugins/1/similar"

# Search manufacturers (with sorting by plugin count)
curl "http://localhost:8000/api/v1/manufacturers?search=fab&sort=plugin_count&order=desc"

# Database stats
curl "http://localhost:8000/api/v1/stats"

# Health check
curl "http://localhost:8000/health"
```

## Running Tests

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

## Contributing

Plugin data lives in `data/seed.json`. To add or correct entries:

1. Fork the repository
2. Edit `data/seed.json` following the existing schema
3. Run `python -m pytest tests/ -v` to verify
4. Open a pull request

PRs that touch `data/seed.json` are automatically validated against the schema.

## License

- **Code:** MIT (see [LICENSE](LICENSE))
- **Data** (`data/seed.json`): CC0 1.0 Universal (public domain)
