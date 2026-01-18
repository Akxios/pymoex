import time
import asyncio
from typing import Any, Optional


class TTLCache:
    """
    Простейший асинхронный in-memory кэш с TTL (time-to-live).

    Хранит значения в памяти и автоматически инвалидирует их
    после истечения времени жизни.
    """

    def __init__(self, ttl: int = 30):
        """
        :param ttl: время жизни записи в секундах
        """
        self.ttl = ttl
        self._data: dict[str, tuple[Any, float]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """
        Получить значение из кэша, если оно ещё не протухло.
        """
        async with self._lock:
            item = self._data.get(key)
            if not item:
                return None

            value, ts = item

            if time.time() - ts > self.ttl:
                del self._data[key]
                return None

            return value

    async def set(self, key: str, value: Any) -> None:
        """
        Сохранить значение в кэш с текущим timestamp.
        """
        async with self._lock:
            self._data[key] = (value, time.time())
