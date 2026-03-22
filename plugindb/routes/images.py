"""Image proxy — serves plugin images with Internet Archive fallback."""

from __future__ import annotations

import ipaddress
import json
import logging
import socket
import urllib.request
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, Response

logger = logging.getLogger("plugindb")

router = APIRouter(tags=["images"])

_MAX_IMAGE_BYTES = 10_000_000

# Load Internet Archive URL mapping (slug -> IA URL)
_archive_map: dict[str, str] = {}
_archive_path = Path(__file__).resolve().parent.parent.parent / "data" / "image_archive.json"
if _archive_path.exists():
    try:
        _archive_map = json.loads(_archive_path.read_text(encoding="utf-8"))
        logger.info("Loaded %d Internet Archive image URLs", len(_archive_map))
    except Exception:
        pass


def get_archive_url(slug: str) -> str | None:
    """Get the Internet Archive URL for a plugin image, if available."""
    return _archive_map.get(slug)


def _is_safe_url(url: str) -> bool:
    """Block SSRF: reject private IPs, loopback, link-local, cloud metadata."""
    parsed = urlparse(url)
    if not parsed.hostname:
        return False
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(parsed.hostname))
        return ip.is_global
    except (socket.gaierror, ValueError):
        return True


@lru_cache(maxsize=100)
def _fetch_image(url: str) -> tuple[bytes, str]:
    """Fetch an image and return (bytes, content_type)."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "PluginDB/2.0 (https://github.com/blakebratcher/plugindb)",
        "Accept": "image/*",
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        content_type = resp.headers.get("Content-Type", "image/jpeg")
        if "image" not in content_type and "octet-stream" not in content_type:
            raise ValueError(f"Not an image: {content_type}")
        data = resp.read(_MAX_IMAGE_BYTES)
    return data, content_type


@router.get("/image/{slug}")
def get_plugin_image(slug: str):
    """Get a plugin image by slug — redirects to Internet Archive if available, otherwise proxies."""
    ia_url = get_archive_url(slug)
    if ia_url:
        return RedirectResponse(url=ia_url, status_code=302)

    # Fall back to proxy via the plugin's image_url
    from plugindb.main import get_db
    conn = get_db()
    row = conn.execute("SELECT image_url FROM plugins WHERE slug = ?", (slug,)).fetchone()
    if not row or not row["image_url"]:
        raise HTTPException(status_code=404, detail="No image for this plugin")

    return _proxy_url(row["image_url"])


@router.get("/image-proxy")
def proxy_image(
    url: str = Query(..., description="Image URL to proxy"),
):
    """Proxy an external image to avoid CORS and hotlinking issues."""
    return _proxy_url(url)


def _proxy_url(url: str) -> Response:
    """Fetch and serve an image from a URL."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="URL must use http or https")

    # If this URL is an archive.org URL, redirect instead of proxying
    if "archive.org" in (parsed.hostname or ""):
        return RedirectResponse(url=url, status_code=302)

    if not _is_safe_url(url):
        raise HTTPException(status_code=403, detail="URL not allowed")

    try:
        data, content_type = _fetch_image(url)
    except Exception as e:
        logger.debug("Image proxy failed for %s: %s", url, e)
        raise HTTPException(status_code=502, detail="Failed to fetch image")

    return Response(
        content=data,
        media_type=content_type,
        headers={
            "Cache-Control": "public, max-age=86400",
            "Access-Control-Allow-Origin": "*",
        },
    )
