#!/usr/bin/env python3
"""Upload plugin images to the Internet Archive for permanent hosting.

Usage:
    python scripts/archive_images.py --access-key YOUR_KEY --secret-key YOUR_SECRET
    python scripts/archive_images.py --access-key YOUR_KEY --secret-key YOUR_SECRET --limit 10 --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

COLLECTION = "plugindb-images"
IA_S3_URL = "https://s3.us.archive.org"


def download_image(url: str, timeout: int = 10) -> bytes | None:
    """Download an image from a URL, return bytes or None on failure."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "PluginDB/2.0 (https://github.com/blakebratcher/plugindb)",
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read(10_000_000)  # 10MB max
            content_type = resp.headers.get("Content-Type", "")
            if "image" not in content_type and "octet" not in content_type:
                return None
            return data
    except Exception as e:
        print(f"    Download failed: {e}")
        return None


def upload_to_ia(
    item_id: str,
    filename: str,
    data: bytes,
    access_key: str,
    secret_key: str,
    metadata: dict | None = None,
) -> bool:
    """Upload a file to the Internet Archive using their S3-like API."""
    url = f"{IA_S3_URL}/{item_id}/{filename}"

    headers = {
        "Authorization": f"LOW {access_key}:{secret_key}",
        "Content-Type": "image/jpeg",
        "x-amz-auto-make-bucket": "1",
        "x-archive-meta-mediatype": "image",
    }

    if metadata:
        for key, value in metadata.items():
            headers[f"x-archive-meta-{key}"] = str(value)

    try:
        req = urllib.request.Request(url, data=data, method="PUT", headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status in (200, 201)
    except urllib.error.HTTPError as e:
        print(f"    Upload failed: HTTP {e.code} - {e.read().decode('utf-8', errors='replace')[:200]}")
        return False
    except Exception as e:
        print(f"    Upload failed: {e}")
        return False


def check_ia_exists(item_id: str, filename: str) -> bool:
    """Check if a file already exists on Internet Archive."""
    url = f"https://archive.org/download/{item_id}/{filename}"
    try:
        req = urllib.request.Request(url, method="HEAD", headers={
            "User-Agent": "PluginDB/2.0",
        })
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Upload plugin images to Internet Archive")
    parser.add_argument("--access-key", required=True, help="IA S3 access key")
    parser.add_argument("--secret-key", required=True, help="IA S3 secret key")
    parser.add_argument("--limit", type=int, default=0, help="Max plugins to process (0=all)")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between uploads")
    parser.add_argument("--dry-run", action="store_true", help="Download but don't upload")
    parser.add_argument("--skip-existing", action="store_true", default=True, help="Skip already uploaded")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    seed_path = base / "data" / "seed.json"

    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    plugins = data["plugins"]
    to_process = [p for p in plugins if p.get("image_url") and not p["image_url"].startswith("https://archive.org/")]

    if args.limit > 0:
        to_process = to_process[:args.limit]

    print(f"Processing {len(to_process)} plugins with external images...")

    uploaded = 0
    skipped = 0
    failed = 0
    already = 0

    for i, plugin in enumerate(to_process):
        slug = plugin["slug"]
        original_url = plugin["image_url"]
        item_id = f"plugindb-{slug}"

        # Determine file extension from URL
        ext = "jpg"
        lower_url = original_url.lower()
        if ".png" in lower_url:
            ext = "png"
        elif ".gif" in lower_url:
            ext = "gif"
        elif ".webp" in lower_url:
            ext = "webp"
        filename = f"{slug}.{ext}"

        print(f"  [{i+1}/{len(to_process)}] {plugin['name']}...", end=" ", flush=True)

        # Check if already on IA
        if args.skip_existing and check_ia_exists(item_id, filename):
            # Update URL to IA
            ia_url = f"https://archive.org/download/{item_id}/{filename}"
            plugin["image_url"] = ia_url
            already += 1
            print("already on IA")
            continue

        # Download from current source
        img_data = download_image(original_url)
        if img_data is None:
            failed += 1
            print("download failed")
            continue

        if args.dry_run:
            skipped += 1
            print(f"downloaded ({len(img_data)//1024}KB) [dry run]")
            continue

        # Upload to IA
        metadata = {
            "title": f"{plugin['name']} - PluginDB",
            "description": f"Product image for {plugin['name']} by {plugin.get('manufacturer_slug', 'unknown')}",
            "subject": "audio;plugin;vst;music-production",
            "creator": "PluginDB",
            "source": original_url,
        }

        success = upload_to_ia(item_id, filename, img_data, args.access_key, args.secret_key, metadata)

        if success:
            ia_url = f"https://archive.org/download/{item_id}/{filename}"
            plugin["image_url"] = ia_url
            uploaded += 1
            print(f"uploaded ({len(img_data)//1024}KB)")
        else:
            failed += 1
            print("upload failed")

        time.sleep(args.delay)

    # Save updated seed.json
    if uploaded > 0 or already > 0:
        with open(seed_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n=== Results ===")
    print(f"  Uploaded: {uploaded}")
    print(f"  Already on IA: {already}")
    print(f"  Failed: {failed}")
    print(f"  Skipped (dry run): {skipped}")
    print(f"  Total: {uploaded + already + failed + skipped}")

    if uploaded > 0:
        print(f"\n  Updated seed.json with {uploaded} new IA URLs")


if __name__ == "__main__":
    main()
