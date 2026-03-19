"""Image proxy — serves external plugin images to avoid CORS/hotlinking issues."""

from __future__ import annotations

import logging
import urllib.request
from functools import lru_cache
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

logger = logging.getLogger("plugindb")

router = APIRouter(tags=["images"])

# Bounded cache: 200 images max (~40MB assuming ~200KB avg)
@lru_cache(maxsize=200)
def _fetch_image(url: str) -> tuple[bytes, str]:
    """Fetch an image and return (bytes, content_type)."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "PluginDB/1.4 (https://github.com/blakebratcher/plugindb)",
        "Accept": "image/*",
    })
    with urllib.request.urlopen(req, timeout=8) as resp:
        content_type = resp.headers.get("Content-Type", "image/jpeg")
        data = resp.read(2 * 1024 * 1024)  # Max 2MB
    return data, content_type


@router.get("/image-proxy")
def proxy_image(
    url: str = Query(..., description="Image URL to proxy"),
):
    """Proxy an external image to avoid CORS and hotlinking issues."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="URL must use http or https")

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
