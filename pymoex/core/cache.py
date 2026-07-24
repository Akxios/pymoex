import asyncio
import logging
import time
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from typing import cast, override

from pymoex.core.interfaces import ICache

logger = logging.getLogger(__name__)

_now = time.monotonic


class NullCache(ICache):
    """
    Заглушка (Dummy Cache).
    Используется, если кэширование нужно полностью отключить.
    """

    @override
    async def get(self, key: str) -> object | None:
        return None

    @override
    async def set(self, key: str, value: object, ttl: int | None = None) -> None:
        pass

    @override
    async def get_or_set[T](
        self,
        key: str,
        factory: Callable[[], Awaitable[T]],
        ttl: int | None = None,
    ) -> T:

        return await factory()

    @override
    async def clear(self) -> None:
        pass


class MemoryCache(ICache):
    """
    In-memory кэш с защитой от Cache Stampede.
    """

    def __init__(self, ttl: int = 60, maxsize: int = 1000) -> None:
        if maxsize <= 0:
            raise ValueError("maxsize must be greater than zero")

        self.ttl: int = ttl
        self.maxsize: int = maxsize

        # Хранилище: key -> (value, expire_at)
        self._data: dict[str, tuple[object, float]] = {}

        # Очередь использования для LRU (Least Recently Used)
        self._order: OrderedDict[str, bool] = OrderedDict()

        # Очередь ожидающих запросов: key -> asyncio.Future
        self._pending: dict[str, asyncio.Future[object]] = {}

        # Лок для защиты внутренних структур данных
        self._lock: asyncio.Lock = asyncio.Lock()

    @override
    async def get(self, key: str) -> object | None:
        async with self._lock:
            return self._get_locked(key)

    @override
    async def set(self, key: str, value: object, ttl: int | None = None) -> None:
        expire = _now() + (ttl if ttl is not None else self.ttl)
        async with self._lock:
            self._set_locked(key, value, expire)

    @override
    async def get_or_set[T](
        self,
        key: str,
        factory: Callable[[], Awaitable[T]],
        ttl: int | None = None,
    ) -> T:
        async with self._lock:
            val = self._get_locked(key)
            if val is not None:
                logger.debug("Cache HIT: %s", key)
                return cast(T, val)

            if key in self._pending:
                logger.debug("Cache WAIT: %s (coalescing)", key)
                future = self._pending[key]
                im_initiator = False
            else:
                logger.debug("Cache MISS: %s -> loading...", key)
                future = asyncio.get_running_loop().create_future()
                self._pending[key] = future
                im_initiator = True

        # --- БЛОК ОЖИДАНИЯ ---
        if not im_initiator:
            return cast(T, await future)

        # --- БЛОК ЗАГРУЗКИ ---
        try:
            result = await factory()

            expire = _now() + (ttl if ttl is not None else self.ttl)

            async with self._lock:
                if key in self._pending:
                    self._set_locked(key, result, expire)
                    _ = self._pending.pop(key, None)

            if not future.done():
                future.set_result(result)

            return result

        except BaseException as e:
            logger.exception("Cache load failed", extra={"key": key})

            async with self._lock:
                _ = self._pending.pop(key, None)

            if not future.done():
                if isinstance(e, asyncio.CancelledError):
                    _ = future.cancel()
                else:
                    future.set_exception(e)
                    future.add_done_callback(lambda f: f.exception())

            raise

    @override
    async def clear(self) -> None:
        """Полная очистка кэша."""
        async with self._lock:
            self._data.clear()
            self._order.clear()
            pending = list(self._pending.values())
            self._pending.clear()

        for future in pending:
            if not future.done():
                _ = future.cancel()

    def _get_locked(self, key: str) -> object | None:
        """Безопасное получение значения без блокировки"""
        if key not in self._data:
            return None

        val, expire = self._data[key]
        if _now() > expire:
            self._delete_locked(key)
            return None

        self._order.move_to_end(key)
        return val

    def _set_locked(self, key: str, value: object, expire: float) -> None:
        """Безопасное сохранение значения."""
        if key not in self._data and len(self._data) >= self.maxsize:
            oldest, _ = self._order.popitem(last=False)
            _ = self._data.pop(oldest, None)

        self._data[key] = (value, expire)

        self._order[key] = True
        self._order.move_to_end(key)

    def _delete_locked(self, key: str) -> None:
        _ = self._data.pop(key, None)
        _ = self._order.pop(key, None)
