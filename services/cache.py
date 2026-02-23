"""
Simple in-memory TTL cache for third-party API responses.
"""
import threading
import time
from typing import Any, Optional


class TTLCache:
    """Thread-safe cache with TTL (time-to-live)."""

    def __init__(self, ttl_seconds: int, max_size: int = 10_000):
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._data: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._data:
                return None
            value, expires = self._data[key]
            if time.monotonic() > expires:
                del self._data[key]
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        if self._ttl <= 0:
            return
        with self._lock:
            if len(self._data) >= self._max_size:
                self._evict_expired()
            if len(self._data) >= self._max_size:
                return
            self._data[key] = (value, time.monotonic() + self._ttl)

    def _evict_expired(self) -> None:
        now = time.monotonic()
        expired = [k for k, (_, e) in self._data.items() if e <= now]
        for k in expired:
            del self._data[k]
