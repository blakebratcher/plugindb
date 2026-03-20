"""Plugin data enrichment — validate and update seed data from external sources."""
from __future__ import annotations

import json
import re
import time
import urllib.request
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path


from plugindb.seed import VALID_CATEGORIES, VALID_FORMATS, VALID_PRICE_TYPES

KVR_SEARCH_URL = "https://www.kvraudio.com/plugins/the-newest-plugins"


@dataclass
class EnrichmentResult:
    """Result of enriching a single plugin."""
    plugin_id: str
    fields_updated: list[str] = field(default_factory=list)
    source: str = ""
    error: str = ""


def search_kvr(plugin_name: str, manufacturer: str) -> dict | None:
    """Search KVR Audio for a plugin and extract metadata.

    Returns a dict of enriched fields, or None if not found.
    Uses KVR's search page to find the plugin.
    """
    query = urllib.parse.quote(f"{manufacturer} {plugin_name}")
    url = f"https://www.kvraudio.com/plugins/newest-plugins?q={query}"

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "PluginDB/1.0 (https://github.com/plugindb; contact@plugindb.org)"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # Extract basic info from search results
        # This is a best-effort approach — KVR's HTML structure may change
        result = {}

        # Look for price info
        if "Free" in html and plugin_name.lower() in html.lower():
            result["price_type"] = "free"

        return result if result else None

    except Exception:
        return None


def search_web(plugin_name: str, manufacturer: str) -> dict | None:
    """Search the web for plugin info using a simple HTTP request.

    Returns enrichment data dict or None.
    """
    # Use DuckDuckGo instant answers (doesn't require API key)
    query = urllib.parse.quote(f"{manufacturer} {plugin_name} VST plugin")
    url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "PluginDB/1.0"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        result = {}

        # Extract abstract/description if available
        abstract = data.get("Abstract", "")
        if abstract and len(abstract) > 20:
            # Clean up the description
            desc = abstract.split(".")[0] + "." if "." in abstract else abstract
            if len(desc) < 200:
                result["description"] = desc

        # Extract official URL
        official_url = data.get("AbstractURL", "")
        if official_url:
            result["url"] = official_url

        return result if result else None

    except Exception:
        return None


def enrich_plugin(plugin: dict, manufacturers: list[dict], delay: float = 1.0) -> EnrichmentResult:
    """Enrich a single plugin with external data.

    Respects rate limits with configurable delay between requests.
    """
    result = EnrichmentResult(plugin_id=plugin["slug"])

    # Find manufacturer name
    mfr_name = ""
    for m in manufacturers:
        if m["slug"] == plugin.get("manufacturer_slug", ""):
            mfr_name = m["name"]
            break

    # Try web search first
    time.sleep(delay)
    web_data = search_web(plugin["name"], mfr_name)

    if web_data:
        result.source = "web_search"
        for key, value in web_data.items():
            if value and (not plugin.get(key) or plugin.get(key) == ""):
                plugin[key] = value
                result.fields_updated.append(key)

    return result


def validate_enrichment(plugin: dict) -> list[str]:
    """Validate that enriched data meets our schema requirements."""
    errors = []

    if plugin.get("price_type") and plugin["price_type"] not in VALID_PRICE_TYPES:
        errors.append(f"Invalid price_type: {plugin['price_type']}")

    if plugin.get("category") and plugin["category"] not in VALID_CATEGORIES:
        errors.append(f"Invalid category: {plugin['category']}")

    formats = plugin.get("formats", [])
    for fmt in formats:
        if fmt not in VALID_FORMATS:
            errors.append(f"Invalid format: {fmt}")

    return errors


def enrich_seed(seed_path: Path, output_path: Path | None = None,
                limit: int = 0, delay: float = 1.0, dry_run: bool = False) -> dict:
    """Enrich all plugins in seed.json.

    Args:
        seed_path: Path to seed.json
        output_path: Where to write enriched data (default: overwrite seed_path)
        limit: Max plugins to enrich (0 = all)
        delay: Seconds between API requests
        dry_run: If True, don't write output

    Returns:
        Stats dict with counts of enriched/skipped/errors
    """
    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    plugins = data["plugins"]
    manufacturers = data["manufacturers"]

    if limit > 0:
        plugins_to_enrich = plugins[:limit]
    else:
        plugins_to_enrich = plugins

    stats = {"total": len(plugins_to_enrich), "enriched": 0, "skipped": 0, "errors": 0}

    for i, plugin in enumerate(plugins_to_enrich):
        print(f"  [{i+1}/{stats['total']}] {plugin['name']}...", end=" ", flush=True)

        result = enrich_plugin(plugin, manufacturers, delay=delay)

        if result.error:
            print(f"ERROR: {result.error}")
            stats["errors"] += 1
        elif result.fields_updated:
            print(f"updated: {', '.join(result.fields_updated)}")
            stats["enriched"] += 1
        else:
            print("no new data")
            stats["skipped"] += 1

    if not dry_run:
        out = output_path or seed_path
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nWritten to {out}")

    return stats
