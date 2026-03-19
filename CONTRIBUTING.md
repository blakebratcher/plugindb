# Contributing to PluginDB

PluginDB is an open database of audio production plugins. Contributions of any kind are welcome.

## Ways to Contribute

- **Submit new plugins** via [GitHub Issue](https://github.com/blakebratcher/plugindb/issues/new?template=plugin-submission.yml) or direct PR
- **Fix incorrect data** via [Data Correction issue](https://github.com/blakebratcher/plugindb/issues/new?template=data-correction.yml)
- **Improve the frontend** (vanilla HTML/CSS/JS in `frontend/`)
- **Report bugs** or suggest features

## Adding a Plugin via PR

1. Fork the repository
2. Edit `data/seed.json`
3. Add a manufacturer if it doesn't exist yet:
   ```json
   { "slug": "manufacturer-slug", "name": "Manufacturer Name", "website": "https://..." }
   ```
4. Add the plugin entry:
   ```json
   {
     "slug": "plugin-name",
     "name": "Plugin Name",
     "manufacturer_slug": "manufacturer-slug",
     "category": "instrument",
     "subcategory": "synth",
     "formats": ["VST3", "AU"],
     "aliases": ["Plugin Name", "Alternative Name"],
     "daws": ["Bitwig", "Ableton", "Cubase", "Studio One", "Reaper", "FL Studio"],
     "os": ["windows", "macos"],
     "description": "Brief description of the plugin.",
     "price_type": "paid",
     "url": "https://...",
     "image_url": "https://example.com/plugin-screenshot.png",
     "year": 2024,
     "tags": ["synthesizer", "wavetable"]
   }
   ```
5. Validate: `python -m plugindb.seed --validate`
6. Test: `python -m pytest tests/ -v`
7. Open a pull request

## Valid Field Values

| Field | Values |
|-------|--------|
| **category** | instrument, effect, midi, utility, container, note-effect |
| **formats** | VST2, VST3, AU, CLAP, AAX, LV2, Standalone |
| **price_type** | free, paid, freemium, subscription, included |
| **os** | windows, macos, linux |
| **slug** | Lowercase, hyphenated (kebab-case). Must be unique. |
| **aliases** | Must include the official plugin name. Globally unique (case-insensitive). |
| **tags** | Lowercase, hyphenated. See existing tags at `/api/v1/tags`. |
| **year** | Integer between 1970 and 2030. |

## Validation Rules

The CI automatically validates `data/seed.json` on every PR. Validation checks:

- Slugs are unique and kebab-case
- Aliases are globally unique (case-insensitive)
- manufacturer_slug references an existing manufacturer
- Category, format, and price_type values are from the valid sets
- Year is within range if provided
- Tags is a list of strings if provided

## Code Contributions

- Python 3.12+
- Install: `pip install -e ".[dev]"`
- Test: `python -m pytest tests/ -v`
- Frontend: edit files directly in `frontend/` (no build tools)
