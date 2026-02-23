"""
Art Institute of Chicago API client (with optional response caching).
"""
from typing import Optional

import httpx
from fastapi import HTTPException, status

from config import ARTIC_BASE_URL, ARTIC_CACHE_TTL
from services.cache import TTLCache

_artwork_cache: Optional[TTLCache] = None


def _get_cache() -> Optional[TTLCache]:
    global _artwork_cache
    if _artwork_cache is None and ARTIC_CACHE_TTL > 0:
        _artwork_cache = TTLCache(ttl_seconds=ARTIC_CACHE_TTL)
    return _artwork_cache


async def fetch_artwork_title(external_id: str) -> Optional[str]:
    """
    Fetch artwork from Art Institute of Chicago API.
    Returns the title if found; raises HTTPException(400) if not found.
    Uses in-memory cache when ARTIC_CACHE_TTL > 0.
    """
    cache = _get_cache()
    if cache:
        cached = cache.get(f"artwork:{external_id}")
        if cached is not None:
            return cached
    url = f"{ARTIC_BASE_URL}/artworks/{external_id}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to contact Art Institute API: {exc}",
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Artwork with id {external_id} does not exist in Art Institute API",
        )
    try:
        data = resp.json()
        title = (data.get("data") or {}).get("title")
        if cache and title is not None:
            cache.set(f"artwork:{external_id}", title)
        return title
    except Exception:
        return None
