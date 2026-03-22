#!/usr/bin/env python3
"""Upload plugin images to the Internet Archive for permanent hosting.

Reads source URLs from seed.json, uploads to IA, and saves the mapping
to data/image_archive.json. NEVER modifies seed.json.

Usage:
    python scripts/archive_images.py --access-key KEY --secret-key SECRET
    python scripts/archive_images.py --access-key KEY --secret-key SECRET --limit 10 --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

IA_S3_URL = "https://s3.us.archive.org"


def download_image(url: str, timeout: int = 10) -> bytes | None:
    """Download an image, return bytes or None on failure."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "PluginDB/2.0 (https://github.com/blakebratcher/plugindb)",
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read(10_000_000)
            content_type = resp.headers.get("Content-Type", "")
            if "image" not in content_type and "octet" not in content_type:
                return None
            return data
    except Exception:
        return None


def upload_to_ia(item_id: str, filename: str, data: bytes,
                 access_key: str, secret_key: str, metadata: dict) -> bool:
    """Upload a file to Internet Archive."""
    url = f"{IA_S3_URL}/{item_id}/{filename}"
    headers = {
        "Authorization": f"LOW {access_key}:{secret_key}",
        "Content-Type": "image/jpeg",
        "x-amz-auto-make-bucket": "1",
        "x-archive-meta-mediatype": "image",
    }
    for key, value in metadata.items():
        headers[f"x-archive-meta-{key}"] = str(value)

    try:
        req = urllib.request.Request(url, data=data, method="PUT", headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status in (200, 201)
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Upload plugin images to Internet Archive")
    parser.add_argument("--access-key", required=True)
    parser.add_argument("--secret-key", required=True)
    parser.add_argument("--limit", type=int, default=0, help="Max to process (0=all)")
    parser.add_argument("--delay", type=float, default=1.5, help="Delay between uploads")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    seed_path = base / "data" / "seed.json"
    archive_path = base / "data" / "image_archive.json"

    # Load seed (read-only)
    seed = json.loads(seed_path.read_text(encoding="utf-8"))

    # Load existing archive mapping
    if archive_path.exists():
        archive_map = json.loads(archive_path.read_text(encoding="utf-8"))
    else:
        archive_map = {}

    # Find plugins with images not yet in the archive
    to_process = []
    for p in seed["plugins"]:
        slug = p["slug"]
        img = p.get("image_url")
        if not img or slug in archive_map:
            continue
        to_process.append((slug, p["name"], img, p.get("manufacturer_slug", "")))

    if args.limit > 0:
        to_process = to_process[:args.limit]

    print(f"Processing {len(to_process)} plugins (already archived: {len(archive_map)})...")

    uploaded = 0
    failed = 0

    for i, (slug, name, source_url, mfr) in enumerate(to_process):
        ext = "jpg"
        lower = source_url.lower()
        if ".png" in lower: ext = "png"
        elif ".gif" in lower: ext = "gif"
        elif ".webp" in lower: ext = "webp"

        item_id = f"plugindb-{slug}"
        filename = f"{slug}.{ext}"

        print(f"  [{i+1}/{len(to_process)}] {name}...", end=" ", flush=True)

        img_data = download_image(source_url)
        if img_data is None:
            failed += 1
            print("download failed")
            continue

        if args.dry_run:
            print(f"downloaded ({len(img_data)//1024}KB) [dry run]")
            continue

        metadata = {
            "title": f"{name} - PluginDB",
            "description": f"Product image for {name} by {mfr}",
            "subject": "audio;plugin;vst;music-production",
            "creator": "PluginDB",
            "source": source_url,
        }

        if upload_to_ia(item_id, filename, img_data, args.access_key, args.secret_key, metadata):
            ia_url = f"https://archive.org/download/{item_id}/{filename}"
            archive_map[slug] = ia_url
            uploaded += 1
            print(f"uploaded ({len(img_data)//1024}KB)")
        else:
            failed += 1
            print("upload failed")

        time.sleep(args.delay)

    # Save archive mapping (NEVER modifies seed.json)
    archive_path.write_text(json.dumps(archive_map, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n=== Results ===")
    print(f"  Uploaded: {uploaded}")
    print(f"  Failed: {failed}")
    print(f"  Total archived: {len(archive_map)}")
    print(f"\n  Saved to {archive_path}")


if __name__ == "__main__":
    main()
