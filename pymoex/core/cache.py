import asyncio
import logging
import time
from collections import OrderedDict
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Монотонное время
_now = time.monotonic


class TTLCache:
    """
    Продвинутый асинхронный TTL-кэш.

    Особенности:
    - Thread-safe (asyncio).
    - LRU вытеснение.
    - Request Coalescing: защита от одновременных одинаковых запросов (через Future).
    """

    def __init__(self, ttl: int = 30, maxsize: Optional[int] = None):
        self.ttl = int(ttl)
        self.maxsize = int(maxsize) if maxsize is not None else None

        # Хранение: key -> (value, expires_at)
        self._data: dict[str, tuple[Any, float]] = {}
        # Порядок LRU
        self._order = OrderedDict()

        # Очередь ожидающих запросов: key -> asyncio.Future
        self._pending: dict[str, asyncio.Future] = {}

        self._lock = asyncio.Lock()

    def _now(self) -> float:
        return _now()

    async def get(self, key: str) -> Optional[Any]:
        """
        Получить значение. Если оно сейчас грузится другим запросом — подождать его.
        """
        async with self._lock:
            # Пробуем найти готовое
            val = self._get_from_data_locked(key)
            if val is not None:
                return val

            # Если не нашли, проверяем, не грузится ли оно прямо сейчас
            future = self._pending.get(key)

        # Ждем снаружи лока
        if future:
            try:
                return await future
            except Exception:
                return None

        return None

    async def get_or_set(self, key: str, factory, ttl: Optional[int] = None):
        """
        Получить или создать. Гарантирует, что factory вызовется 1 раз для ключа.
        """
        async with self._lock:
            # Быстрая проверка наличия
            val = self._get_from_data_locked(key)
            if val is not None:
                logger.debug(f"Cache HIT: {key}")
                return val

            # Проверка: не грузит ли кто-то уже?
            if key in self._pending:
                logger.debug(f"Cache WAIT: {key} (coalescing)")
                future = self._pending[key]
                # Мы не инициаторы, поэтому просто запомнили future и пойдем ждать
                im_initiator = False
            else:
                # Мы первые. Создаем Future
                logger.debug(f"Cache MISS: {key} -> loading...")
                future = asyncio.Future()
                self._pending[key] = future
                im_initiator = True

        # --- БЛОК ОЖИДАНИЯ ---
        if not im_initiator:
            return await future

        # --- БЛОК ЗАГРУЗКИ ---
        try:
            # Выполняем factory без блокировки кэша
            result = factory()
            if asyncio.iscoroutine(result):
                result = await result

            # Сохраняем результат
            expires_at = self._now() + (int(ttl) if ttl is not None else self.ttl)

            async with self._lock:
                # Проверяем, не удалили ли pending, пока мы работали
                if key in self._pending:
                    self._data[key] = (result, expires_at)
                    self._order[key] = True
                    self._move_to_end_locked(key)

                    # Убираем из pending
                    self._pending.pop(key, None)

                    # Чистим место, если надо
                    self._evict_if_needed_locked()

            # Сообщаем всем ждущим
            future.set_result(result)
            return result

        except Exception as e:
            # Если factory упала, нужно сообщить ошибку всем, кто ждет
            async with self._lock:
                self._pending.pop(key, None)
            future.set_exception(e)

            # Убираем предупреждение asyncio
            try:
                future.result()
            except Exception:
                pass

            raise e

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expires_at = self._now() + (int(ttl) if ttl is not None else self.ttl)
        async with self._lock:
            self._data[key] = (value, expires_at)
            self._move_to_end_locked(key)
            self._evict_if_needed_locked()

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._delete_locked(key)

    async def clear(self) -> None:
        """Полная очистка."""
        async with self._lock:
            self._data.clear()
            self._order.clear()

    # --- Приватные хелперы ---

    def _get_from_data_locked(self, key: str) -> Optional[Any]:
        """Возвращает значение или None, удаляет протухшее."""
        item = self._data.get(key)
        if not item:
            return None

        val, expires_at = item
        if self._now() > expires_at:
            self._delete_locked(key)
            return None

        self._move_to_end_locked(key)
        return val

    def _move_to_end_locked(self, key: str):
        try:
            self._order.move_to_end(key, last=True)
        except KeyError:
            self._order[key] = True

    def _delete_locked(self, key: str):
        self._data.pop(key, None)
        self._order.pop(key, None)

    def _evict_if_needed_locked(self):
        if self.maxsize is None:
            return
        while len(self._data) > self.maxsize:
            oldest_key, _ = self._order.popitem(last=False)
            self._data.pop(oldest_key, None)
