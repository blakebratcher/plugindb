#!/usr/bin/env python3
"""Validate all URLs in seed.json are reachable."""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path


def main():
    seed_path = Path(__file__).resolve().parent.parent / "data" / "seed.json"
    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    plugins_with_urls = [(p["slug"], p["url"]) for p in data["plugins"] if p.get("url")]
    mfr_with_urls = [(m["slug"], m["url"]) for m in data["manufacturers"] if m.get("url")]

    all_urls = [(f"plugin:{id}", url) for id, url in plugins_with_urls] + \
               [(f"mfr:{id}", url) for id, url in mfr_with_urls]

    print(f"Checking {len(all_urls)} URLs...")
    broken = []

    for i, (label, url) in enumerate(all_urls):
        try:
            req = urllib.request.Request(url, method="HEAD", headers={
                "User-Agent": "PluginDB/1.0 (URL validation)"
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status >= 400:
                    broken.append((label, url, f"HTTP {resp.status}"))
        except Exception as e:
            broken.append((label, url, str(e)[:80]))

        if (i + 1) % 10 == 0:
            print(f"  checked {i+1}/{len(all_urls)}...")

    if broken:
        print(f"\n{len(broken)} broken URLs:")
        for label, url, err in broken:
            print(f"  {label}: {url} — {err}")
    else:
        print("\nAll URLs valid!")

    return len(broken)


if __name__ == "__main__":
    sys.exit(main())
