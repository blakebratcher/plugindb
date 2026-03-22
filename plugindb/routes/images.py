"""Image proxy — serves external plugin images to avoid CORS/hotlinking issues."""

from __future__ import annotations

import ipaddress
import logging
import socket
import urllib.request
from functools import lru_cache
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

logger = logging.getLogger("plugindb")

router = APIRouter(tags=["images"])

# Max 2MB per cached image, 100 images max (~200MB ceiling)
_MAX_IMAGE_BYTES = 2_000_000


def _is_safe_url(url: str) -> bool:
    """Block SSRF: reject private IPs, loopback, link-local, cloud metadata."""
    parsed = urlparse(url)
    if not parsed.hostname:
        return False
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(parsed.hostname))
        return ip.is_global
    except (socket.gaierror, ValueError):
        # Can't resolve — allow (might be a CDN hostname)
        return True


@lru_cache(maxsize=100)
def _fetch_image(url: str) -> tuple[bytes, str]:
    """Fetch an image and return (bytes, content_type)."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "PluginDB/1.4 (https://github.com/blakebratcher/plugindb)",
        "Accept": "image/*",
    })
    with urllib.request.urlopen(req, timeout=8) as resp:
        content_type = resp.headers.get("Content-Type", "image/jpeg")
        if "image" not in content_type and "octet-stream" not in content_type:
            raise ValueError(f"Not an image: {content_type}")
        data = resp.read(_MAX_IMAGE_BYTES)
    return data, content_type


@router.get("/image-proxy")
def proxy_image(
    url: str = Query(..., description="Image URL to proxy"),
):
    """Proxy an external image to avoid CORS and hotlinking issues."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="URL must use http or https")

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
