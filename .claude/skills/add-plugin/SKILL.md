---
name: add-plugin
description: Add a new audio plugin to the PluginDB database with full validation, image discovery, and testing
---

## Add Plugin Workflow

When the user wants to add one or more plugins to the database, follow this workflow:

### 1. Gather Information

Required fields:
- **name** — plugin name
- **manufacturer** — must match an existing manufacturer in seed.json, or create a new one
- **category** — one of: container, effect, instrument, midi, note-effect, utility

Optional but recommended:
- **formats** — list from: AAX, AU, CLAP, LV2, Standalone, VST2, VST3
- **price_type** — one of: free, freemium, included, paid, subscription
- **description** — short description of the plugin
- **year** — release year (1990–current year)
- **url** — official website
- **tags** — lowercase, hyphenated descriptors (e.g., "reverb", "delay", "analog-modeling")
- **aliases** — alternate names users might search for
- **image_url** — cover art URL (https)

### 2. Generate Slug

Create slug from plugin name: lowercase, replace spaces/special chars with hyphens, remove consecutive hyphens. Verify the slug is unique in seed.json.

### 3. Check for Duplicates

Search seed.json for existing entries with the same name and manufacturer_slug. Warn the user if a potential duplicate is found.

### 4. Add to seed.json

Insert the new plugin entry into the appropriate position in the plugins array (alphabetical by name within manufacturer, or at the end). Use the standard structure:

```json
{
  "name": "Plugin Name",
  "slug": "plugin-name",
  "manufacturer_slug": "manufacturer-slug",
  "category": "effect",
  "description": "...",
  "url": "https://...",
  "image_url": "https://...",
  "formats": ["VST3", "AU", "AAX"],
  "price_type": "paid",
  "year": 2024,
  "tags": ["tag1", "tag2"],
  "aliases": []
}
```

### 5. If New Manufacturer Needed

Add manufacturer to the manufacturers array:

```json
{
  "name": "Manufacturer Name",
  "slug": "manufacturer-slug",
  "url": "https://..."
}
```

### 6. Validate

Run: `python -m plugindb.seed --validate`

Fix any reported errors before proceeding.

### 7. Image Discovery

If no image_url was provided, attempt to find one:
- Check the manufacturer's website for product images
- Run: `python scripts/scrape_images.py --delay 0.2` if the script supports the new plugin

### 8. Rebuild Database

Run: `python -m plugindb.seed`

### 9. Test

Run: `python -m pytest tests/ -x -q --tb=short`

Confirm all tests pass. If any fail, diagnose and fix before finishing.

### 10. Summary

Report what was added: plugin name, manufacturer, category, and whether an image was found.
