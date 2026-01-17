import time
import asyncio


class TTLCache:
    def __init__(self, ttl: int = 30):
        self.ttl = ttl
        self._data = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str):
        async with self._lock:
            item = self._data.get(key)

            if not item:
                return None

            value, ts = item

            if time.time() - ts > self.ttl:
                del self._data[key]
                return None

            return value

    async def set(self, key: str, value):
        async with self._lock:
            self._data[key] = (value, time.time())
