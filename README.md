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
| `POST` | `/api/v1/lookup` | Batch resolve up to 100 names |
| `GET` | `/api/v1/search?q=X` | Full-text search (min 2 chars) |
| `GET` | `/api/v1/plugins` | List all plugins (paginated, filterable) |
| `GET` | `/api/v1/plugins/{id}` | Get a single plugin by ID |
| `GET` | `/api/v1/manufacturers` | List all manufacturers (paginated) |
| `GET` | `/api/v1/manufacturers/{slug}` | Get a manufacturer + its plugins |
| `GET` | `/api/v1/stats` | Database statistics |
| `GET` | `/api/v1/categories` | Plugin category taxonomy |

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
