#!/usr/bin/env python3
"""Upload plugin manuals/PDFs to the Internet Archive for permanent hosting.

Only uploads manuals that are direct PDF links (not generic support pages).

Usage:
    python scripts/archive_manuals.py --access-key YOUR_KEY --secret-key YOUR_SECRET
    python scripts/archive_manuals.py --access-key YOUR_KEY --secret-key YOUR_SECRET --limit 10 --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

IA_S3_URL = "https://s3.us.archive.org"
COLLECTION = "plugindb-manuals"


def is_direct_pdf(url: str) -> bool:
    """Check if URL is a direct link to a PDF (not a generic support page)."""
    lower = url.lower()
    return lower.endswith(".pdf") or "/manual" in lower and ".pdf" in lower


def download_file(url: str, timeout: int = 15) -> tuple[bytes, str] | None:
    """Download a file, return (bytes, content_type) or None."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "PluginDB/2.0 (https://github.com/blakebratcher/plugindb)",
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "")
            data = resp.read(50_000_000)  # 50MB max for PDFs
            return data, content_type
    except Exception as e:
        return None


def upload_to_ia(item_id: str, filename: str, data: bytes, content_type: str,
                 access_key: str, secret_key: str, metadata: dict) -> bool:
    """Upload to Internet Archive."""
    url = f"{IA_S3_URL}/{item_id}/{filename}"
    headers = {
        "Authorization": f"LOW {access_key}:{secret_key}",
        "Content-Type": content_type or "application/pdf",
        "x-amz-auto-make-bucket": "1",
        "x-archive-meta-mediatype": "texts",
    }
    for key, value in metadata.items():
        headers[f"x-archive-meta-{key}"] = str(value)

    try:
        req = urllib.request.Request(url, data=data, method="PUT", headers=headers)
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status in (200, 201)
    except Exception as e:
        print(f"    Upload failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Upload plugin manuals to Internet Archive")
    parser.add_argument("--access-key", required=True, help="IA S3 access key")
    parser.add_argument("--secret-key", required=True, help="IA S3 secret key")
    parser.add_argument("--limit", type=int, default=0, help="Max to process (0=all)")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between uploads")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    seed_path = base / "data" / "seed.json"
    data = json.load(open(seed_path, encoding="utf-8"))

    # Only process manuals that are direct PDF links
    to_process = [p for p in data["plugins"]
                  if p.get("manual_url") and is_direct_pdf(p["manual_url"])
                  and not p["manual_url"].startswith("https://archive.org/")]

    if args.limit > 0:
        to_process = to_process[:args.limit]

    print(f"Found {len(to_process)} direct PDF manual links to archive...")

    uploaded = 0
    failed = 0

    for i, plugin in enumerate(to_process):
        slug = plugin["slug"]
        url = plugin["manual_url"]
        item_id = f"plugindb-manual-{slug}"
        filename = f"{slug}-manual.pdf"

        print(f"  [{i+1}/{len(to_process)}] {plugin['name']}...", end=" ", flush=True)

        result = download_file(url)
        if result is None:
            failed += 1
            print("download failed")
            continue

        file_data, ct = result
        print(f"downloaded ({len(file_data)//1024}KB)", end=" ", flush=True)

        if args.dry_run:
            print("[dry run]")
            continue

        metadata = {
            "title": f"{plugin['name']} Manual - PluginDB",
            "description": f"User manual for {plugin['name']}",
            "subject": "audio;plugin;manual;documentation",
            "creator": "PluginDB",
            "source": url,
        }

        if upload_to_ia(item_id, filename, file_data, ct, args.access_key, args.secret_key, metadata):
            ia_url = f"https://archive.org/download/{item_id}/{filename}"
            plugin["manual_url"] = ia_url
            uploaded += 1
            print("uploaded")
        else:
            failed += 1
            print("upload failed")

        time.sleep(args.delay)

    if uploaded > 0:
        with open(seed_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n=== Results ===")
    print(f"  Uploaded: {uploaded}")
    print(f"  Failed: {failed}")


if __name__ == "__main__":
    main()
