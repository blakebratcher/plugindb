#!/usr/bin/env python3
"""CLI tool for adding a new plugin to seed.json with validation."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from plugindb.seed import VALID_CATEGORIES, VALID_FORMATS, VALID_PRICE_TYPES, slugify, validate_seed


def main():
    parser = argparse.ArgumentParser(description="Add a new plugin to data/seed.json")
    parser.add_argument("--name", required=True, help="Plugin name")
    parser.add_argument("--manufacturer", required=True, help="Manufacturer name")
    parser.add_argument("--category", required=True, choices=sorted(VALID_CATEGORIES))
    parser.add_argument("--subcategory", help="Subcategory (e.g., synth, reverb, compressor)")
    parser.add_argument("--formats", required=True, help="Comma-separated formats (e.g., VST3,AU,CLAP)")
    parser.add_argument("--price-type", required=True, choices=sorted(VALID_PRICE_TYPES))
    parser.add_argument("--description", help="Brief description (1-2 sentences)")
    parser.add_argument("--url", help="Official product URL")
    parser.add_argument("--year", type=int, help="Release year")
    parser.add_argument("--tags", help="Comma-separated tags (lowercase, hyphenated)")
    parser.add_argument("--aliases", help="Comma-separated aliases (include official name)")
    parser.add_argument("--os", help="Comma-separated OS (windows,macos,linux)", default="windows,macos")
    parser.add_argument("--daws", help="Comma-separated DAWs", default="Bitwig,Ableton,Cubase,Studio One,Reaper,FL Studio")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    seed_path = base / "data" / "seed.json"

    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Build plugin entry
    plugin_slug = slugify(args.name)
    mfr_slug = slugify(args.manufacturer)

    # Ensure manufacturer exists
    mfr_slugs = {m["slug"] for m in data["manufacturers"]}
    if mfr_slug not in mfr_slugs:
        new_mfr = {"slug": mfr_slug, "name": args.manufacturer}
        if args.url:
            # Extract domain as manufacturer website
            from urllib.parse import urlparse
            parsed = urlparse(args.url)
            new_mfr["website"] = f"{parsed.scheme}://{parsed.netloc}"
        data["manufacturers"].append(new_mfr)
        data["manufacturers"].sort(key=lambda m: m["slug"])
        print(f"  Added new manufacturer: {args.manufacturer} ({mfr_slug})")

    # Check for duplicate slug
    existing_slugs = {p["slug"] for p in data["plugins"]}
    if plugin_slug in existing_slugs:
        print(f"Error: plugin slug '{plugin_slug}' already exists!")
        sys.exit(1)

    formats = [f.strip() for f in args.formats.split(",")]
    for fmt in formats:
        if fmt not in VALID_FORMATS:
            print(f"Warning: format '{fmt}' is not in VALID_FORMATS")

    aliases = [a.strip() for a in (args.aliases or args.name).split(",")]
    if args.name not in aliases:
        aliases.insert(0, args.name)

    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
    os_list = [o.strip() for o in args.os.split(",")]
    daws = [d.strip() for d in args.daws.split(",")]

    plugin = {
        "slug": plugin_slug,
        "name": args.name,
        "manufacturer_slug": mfr_slug,
        "category": args.category,
        "subcategory": args.subcategory,
        "formats": formats,
        "aliases": aliases,
        "daws": daws,
        "os": os_list,
        "description": args.description,
        "price_type": args.price_type,
        "url": args.url,
        "year": args.year,
        "tags": tags,
    }

    data["plugins"].append(plugin)

    # Validate
    errors = validate_seed(data)
    if errors:
        print(f"Validation FAILED ({len(errors)} errors):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"  Plugin: {args.name} ({plugin_slug})")
    print(f"  Manufacturer: {args.manufacturer} ({mfr_slug})")
    print(f"  Category: {args.category}/{args.subcategory or 'general'}")
    print(f"  Formats: {', '.join(formats)}")
    print(f"  Tags: {', '.join(tags) if tags else 'none'}")
    print(f"  Validation: PASSED")

    if args.dry_run:
        print("\n  (dry run — not written)")
        return

    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n  Written to {seed_path}")
    print(f"  Total: {len(data['plugins'])} plugins, {len(data['manufacturers'])} manufacturers")


if __name__ == "__main__":
    main()
