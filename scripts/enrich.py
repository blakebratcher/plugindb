#!/usr/bin/env python3
"""CLI tool for enriching PluginDB seed data from external sources."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from plugindb.enricher import enrich_seed


def main():
    parser = argparse.ArgumentParser(description="Enrich PluginDB seed data from external sources")
    parser.add_argument("--limit", type=int, default=0, help="Max plugins to enrich (0 = all)")
    parser.add_argument("--delay", type=float, default=1.5, help="Delay between API requests (seconds)")
    parser.add_argument("--dry-run", action="store_true", help="Don't write output")
    parser.add_argument("--output", type=str, help="Output path (default: overwrite seed.json)")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    seed_path = base / "data" / "seed.json"
    output_path = Path(args.output) if args.output else None

    print("=== PluginDB Enrichment Pipeline ===")
    print(f"Source: {seed_path}")
    print(f"Limit: {'all' if args.limit == 0 else args.limit}")
    print(f"Delay: {args.delay}s between requests")
    print()

    stats = enrich_seed(seed_path, output_path, limit=args.limit, delay=args.delay, dry_run=args.dry_run)

    print(f"\n=== Results ===")
    print(f"  Total: {stats['total']}")
    print(f"  Enriched: {stats['enriched']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Errors: {stats['errors']}")


if __name__ == "__main__":
    main()
