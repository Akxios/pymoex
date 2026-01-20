import time
import asyncio
from typing import Any, Optional
from collections import OrderedDict

_now = time.monotonic


class TTLCache:
    """
    Асинхронный in-memory TTL-кэш с опциональным ограничением размера (LRU eviction).
    - ttl: время жизни по умолчанию в секундах
    - maxsize: максимальное число элементов в кэше (None = без ограничения)
    """

    def __init__(self, ttl: int = 30, maxsize: Optional[int] = None):
        self.ttl = int(ttl)
        self.maxsize = None if maxsize is None else int(maxsize)
        # _data: key -> (value, expires_at)
        self._data: dict[str, tuple[Any, float]] = {}
        # _order stores keys in LRU order: oldest first, newest last
        self._order = OrderedDict()
        self._lock = asyncio.Lock()

    def _now(self) -> float:
        return _now()

    async def _evict_if_needed(self) -> None:
        """Evict oldest entries if cache exceeded maxsize."""
        if self.maxsize is None:
            return
        while len(self._data) > self.maxsize:
            oldest_key, _ = self._order.popitem(last=False)
            self._data.pop(oldest_key, None)

    async def get(self, key: str) -> Optional[Any]:
        """Return value or None if missing/expired."""
        async with self._lock:
            item = self._data.get(key)
            if not item:
                return None
            value, expires_at = item
            if self._now() > expires_at:
                # expired -> remove
                self._data.pop(key, None)
                self._order.pop(key, None)
                return None
            # touch LRU (mark as recently used)
            try:
                self._order.move_to_end(key, last=True)
            except KeyError:
                self._order[key] = True
            return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value with optional per-key ttl (in seconds)."""
        expires_at = self._now() + (int(ttl) if ttl is not None else self.ttl)
        async with self._lock:
            # insert / update
            self._data[key] = (value, expires_at)
            # update order: newest at the end
            self._order.pop(key, None)
            self._order[key] = True
            await self._evict_if_needed()

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._data.pop(key, None)
            self._order.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._data.clear()
            self._order.clear()

    async def keys(self) -> list[str]:
        async with self._lock:
            return list(self._data.keys())

    async def get_or_set(self, key: str, factory, ttl: Optional[int] = None):
        """
        Atomically get or compute+set.
        factory may be a coroutine function or sync function.
        """
        val = await self.get(key)
        if val is not None:
            return val

        async with self._lock:
            # double-check inside lock
            item = self._data.get(key)
            if item:
                value, expires_at = item
                if self._now() <= expires_at:
                    try:
                        self._order.move_to_end(key, last=True)
                    except KeyError:
                        self._order[key] = True
                    return value
                # expired -> remove
                self._data.pop(key, None)
                self._order.pop(key, None)

            result = factory()
            if asyncio.iscoroutine(result):
                result = await result  # type: ignore
            expires_at = self._now() + (int(ttl) if ttl is not None else self.ttl)
            self._data[key] = (result, expires_at)
            self._order[key] = True
            await self._evict_if_needed()
            return result
