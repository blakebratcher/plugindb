#!/usr/bin/env python3
"""Scrape og:image/twitter:image from plugin product pages to populate image_url."""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from pathlib import Path


def extract_og_image(html: str) -> str | None:
    """Extract og:image or twitter:image from HTML using regex."""
    # Try og:image first (both attribute orders)
    for pattern in [
        r'<meta\s+(?:[^>]*?)property=["\']og:image(?::secure_url)?["\']\s+content=["\']([^"\']+)["\']',
        r'<meta\s+content=["\']([^"\']+)["\']\s+(?:[^>]*?)property=["\']og:image(?::secure_url)?["\']',
    ]:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1)

    # Fallback to twitter:image
    for pattern in [
        r'<meta\s+(?:[^>]*?)(?:name|property)=["\']twitter:image(?::src)?["\']\s+content=["\']([^"\']+)["\']',
        r'<meta\s+content=["\']([^"\']+)["\']\s+(?:[^>]*?)(?:name|property)=["\']twitter:image(?::src)?["\']',
    ]:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def extract_product_image(html: str, url: str) -> str | None:
    """Deeper image extraction — look for hero/product images in HTML."""
    # Look for large images with product-related classes or attributes
    patterns = [
        r'<img[^>]+(?:class|id)=["\'][^"\']*(?:hero|product|plugin|main-image|featured)[^"\']*["\'][^>]+src=["\']([^"\']+)["\']',
        r'<img[^>]+src=["\']([^"\']+)["\'][^>]+(?:class|id)=["\'][^"\']*(?:hero|product|plugin|main-image|featured)[^"\']*["\']',
        # srcset first value (often highest quality)
        r'<img[^>]+srcset=["\']([^\s"\']+)',
        # JSON-LD product image
        r'"image"\s*:\s*["\']([^"\']+\.(?:jpg|jpeg|png|webp))["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            img = match.group(1)
            # Make relative URLs absolute
            if img.startswith("//"):
                img = "https:" + img
            elif img.startswith("/"):
                from urllib.parse import urlparse
                parsed = urlparse(url)
                img = f"{parsed.scheme}://{parsed.netloc}{img}"
            return img
    return None


def is_valid_image_url(url: str) -> bool:
    """Check if URL looks like a valid image."""
    if not url or not url.startswith(("http://", "https://")):
        return False
    lower = url.lower()
    if any(skip in lower for skip in ["1x1", "pixel", "spacer", "favicon", "logo-small", "blank.", "empty."]):
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Scrape og:image from plugin URLs")
    parser.add_argument("--limit", type=int, default=0, help="Max plugins to process (0=all)")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests")
    parser.add_argument("--dry-run", action="store_true", help="Don't write output")
    parser.add_argument("--force", action="store_true", help="Re-scrape even if image_url exists")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    seed_path = base / "data" / "seed.json"

    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    plugins = data["plugins"]
    found = 0
    failed = 0
    skipped = 0
    already = 0

    to_process = plugins[:args.limit] if args.limit > 0 else plugins

    for i, plugin in enumerate(to_process):
        name = plugin["name"]
        url = plugin.get("url")

        if not url:
            skipped += 1
            continue

        if plugin.get("image_url") and not args.force:
            already += 1
            continue

        print(f"  [{i+1}/{len(to_process)}] {name}...", end=" ", flush=True)

        try:
            time.sleep(args.delay)
            req = urllib.request.Request(url, headers={
                "User-Agent": "PluginDB/1.4 (https://github.com/blakebratcher/plugindb)",
                "Accept": "text/html",
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read(500_000).decode("utf-8", errors="replace")

            img_url = extract_og_image(html)

            # Fallback: deeper extraction from page content
            if not img_url or not is_valid_image_url(img_url):
                img_url = extract_product_image(html, url)

            if img_url and is_valid_image_url(img_url):
                plugin["image_url"] = img_url
                found += 1
                print(f"FOUND ({img_url[:60]})")
            else:
                failed += 1
                print(f"no image found")

        except Exception as e:
            failed += 1
            print(f"ERROR: {str(e)[:60]}")

    print(f"\n=== Results ===")
    print(f"  Found: {found}")
    print(f"  Failed: {failed}")
    print(f"  Skipped (no URL): {skipped}")
    print(f"  Already had image: {already}")
    print(f"  Total: {len(to_process)}")

    if not args.dry_run and found > 0:
        with open(seed_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n  Written to {seed_path}")
    elif args.dry_run:
        print(f"\n  (dry run — not written)")


if __name__ == "__main__":
    main()
