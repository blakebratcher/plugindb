#!/usr/bin/env python3
"""Scrape plugin images from Splice.com — the best source for product screenshots."""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


def search_splice(plugin_name: str, manufacturer: str) -> str | None:
    """Search Splice for a plugin and extract the og:image from the result page."""
    query = urllib.parse.quote(f"{manufacturer} {plugin_name}")
    search_url = f"https://splice.com/plugins/search?q={query}"

    try:
        req = urllib.request.Request(search_url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; PluginDB/1.4)",
            "Accept": "text/html",
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read(500_000).decode("utf-8", errors="replace")

        # Extract og:image
        match = re.search(r'<meta\s+(?:[^>]*?)property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if not match:
            match = re.search(r'<meta\s+content=["\']([^"\']+)["\']\s+(?:[^>]*?)property=["\']og:image["\']', html, re.IGNORECASE)
        if match:
            img = match.group(1)
            if "splice" in img.lower() or "cloudinary" in img.lower():
                return img

        # Try to find plugin page links and follow them
        page_match = re.search(rf'href=["\'](/plugins/[^"\']*?{re.escape(plugin_name.lower().split()[0])}[^"\']*)["\']', html, re.IGNORECASE)
        if page_match:
            plugin_url = f"https://splice.com{page_match.group(1)}"
            req2 = urllib.request.Request(plugin_url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; PluginDB/1.4)",
                "Accept": "text/html",
            })
            with urllib.request.urlopen(req2, timeout=10) as resp2:
                html2 = resp2.read(500_000).decode("utf-8", errors="replace")

            for pat in [
                r'<meta\s+(?:[^>]*?)property=["\']og:image["\']\s+content=["\']([^"\']+)["\']',
                r'<meta\s+content=["\']([^"\']+)["\']\s+(?:[^>]*?)property=["\']og:image["\']',
            ]:
                m = re.search(pat, html2, re.IGNORECASE)
                if m and ("splice" in m.group(1).lower() or "cloudinary" in m.group(1).lower()):
                    return m.group(1)

    except Exception:
        pass
    return None


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Scrape Splice for plugin images")
    parser.add_argument("--limit", type=int, default=0, help="Max plugins (0=all)")
    parser.add_argument("--delay", type=float, default=1.5, help="Delay between requests")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    seed_path = base / "data" / "seed.json"
    data = json.load(open(seed_path))

    # Get manufacturer names
    mfr_map = {m["slug"]: m["name"] for m in data["manufacturers"]}

    missing = [p for p in data["plugins"] if not p.get("image_url")]
    to_process = missing[:args.limit] if args.limit > 0 else missing

    print(f"Searching Splice for {len(to_process)} plugins missing images...")
    found = 0
    failed = 0

    for i, plugin in enumerate(to_process):
        mfr_name = mfr_map.get(plugin["manufacturer_slug"], "")
        print(f"  [{i+1}/{len(to_process)}] {plugin['name']} ({mfr_name})...", end=" ", flush=True)

        time.sleep(args.delay)
        img = search_splice(plugin["name"], mfr_name)

        if img:
            plugin["image_url"] = img
            found += 1
            print(f"FOUND")
        else:
            failed += 1
            print(f"not on Splice")

    print(f"\n=== Results ===")
    print(f"  Found: {found}")
    print(f"  Not found: {failed}")

    if not args.dry_run and found > 0:
        json.dump(data, open(seed_path, "w"), indent=2, ensure_ascii=False)
        total = sum(1 for p in data["plugins"] if p.get("image_url"))
        print(f"  Written. Total images: {total}/294")


if __name__ == "__main__":
    main()
