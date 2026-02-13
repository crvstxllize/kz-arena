from datetime import datetime, timedelta, timezone
from typing import Any

_CACHE: dict[str, tuple[datetime, Any]] = {}


def get_cached(key: str, ttl_minutes: int):
    item = _CACHE.get(key)
    if not item:
        return None
    cached_at, value = item
    if datetime.now(timezone.utc) - cached_at > timedelta(minutes=ttl_minutes):
        return None
    return value


def set_cached(key: str, value: Any):
    _CACHE[key] = (datetime.now(timezone.utc), value)
