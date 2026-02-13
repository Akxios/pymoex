import asyncio
import logging
import time
from collections import OrderedDict
from typing import Any, Awaitable, Callable, Optional

from pymoex.core.interfaces import ICache

logger = logging.getLogger(__name__)

# Монотонное время для корректного подсчета TTL (защита от перевода часов)
_now = time.monotonic


class NullCache(ICache):
    """
    Заглушка (Dummy Cache).
    Используется, если кэширование нужно полностью отключить.
    Ничего не сохраняет, factory() вызывает напрямую.
    """

    async def get(self, key: str) -> Optional[Any]:
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        pass

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Awaitable[Any]],
        ttl: Optional[int] = None,
    ) -> Any:
        # Кэша нет, поэтому просто выполняем запрос к API
        return await factory()

    async def clear(self) -> None:
        pass


class MemoryCache(ICache):
    """
    In-memory кэш с защитой от Cache Stampede (Request Coalescing).

    Особенности:
    - LRU вытеснение (удаляет старые ключи при достижении maxsize).
    - Асинхронная thread-safe реализация (asyncio.Lock).
    - Request Coalescing: Если 100 запросов придут за одним ключом одновременно,
      выполнится только один реальный HTTP-запрос, остальные подождут результат.
    """

    def __init__(self, ttl: int = 60, maxsize: int = 1000):
        self.ttl = int(ttl)
        self.maxsize = int(maxsize)

        # Хранилище: key -> (value, expire_at)
        self._data: dict[str, tuple[Any, float]] = {}

        # Очередь использования для LRU (Least Recently Used)
        self._order = OrderedDict()

        # Очередь ожидающих запросов: key -> asyncio.Future
        self._pending: dict[str, asyncio.Future] = {}

        # Лок для защиты внутренних структур данных
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            return self._get_locked(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expire = _now() + (ttl if ttl is not None else self.ttl)
        async with self._lock:
            self._set_locked(key, value, expire)

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Awaitable[Any]],
        ttl: Optional[int] = None,
    ) -> Any:
        async with self._lock:
            # 1. Быстрая проверка: может значение уже есть и оно свежее?
            val = self._get_locked(key)
            if val is not None:
                logger.debug(f"Cache HIT: {key}")
                return val

            # 2. Проверка Request Coalescing (Склейка запросов)
            # Если кто-то уже загружает этот ключ прямо сейчас, мы просто подпишемся на результат
            if key in self._pending:
                logger.debug(f"Cache WAIT: {key} (coalescing)")
                future = self._pending[key]
                im_initiator = False
            else:
                # Мы первые -> создаем Future, становимся инициатором загрузки
                logger.debug(f"Cache MISS: {key} -> loading...")
                future = asyncio.Future()
                self._pending[key] = future
                im_initiator = True

        # --- БЛОК ОЖИДАНИЯ (для тех, кто пришел вторым и далее) ---
        if not im_initiator:
            try:
                return await future
            except Exception:
                # Если инициатор упал с ошибкой, нам тоже придется вернуть None (или упасть).
                # Вернем None, чтобы вызывающий код мог попробовать перезапросить.
                return None

        # --- БЛОК ЗАГРУЗКИ (для инициатора) ---
        try:
            # Выполняем factory() БЕЗ блокировки кэша, чтобы не тормозить другие запросы к другим ключам
            result = await factory()

            # Сохраняем результат
            expire = _now() + (ttl if ttl is not None else self.ttl)

            async with self._lock:
                # Проверяем, что ключ все еще в pending (не был очищен через clear())
                if key in self._pending:
                    self._set_locked(key, result, expire)
                    # Убираем из очереди ожидания, так как загрузка завершена
                    self._pending.pop(key, None)

            # Сообщаем всем ждущим успех
            if not future.done():
                future.set_result(result)

            return result

        except Exception as e:
            # Если загрузка упала (сетевая ошибка и т.д.), нужно сообщить ошибку всем ждущим
            async with self._lock:
                # Удаляем из pending, чтобы следующий запрос попробовал загрузить снова
                self._pending.pop(key, None)

            if not future.done():
                future.set_exception(e)
            raise e

    async def clear(self) -> None:
        """Полная очистка кэша."""
        async with self._lock:
            self._data.clear()
            self._order.clear()
            # Важно: мы не трогаем _pending, чтобы текущие летящие запросы могли корректно завершиться

    # --- Приватные методы (вызывать только под self._lock) ---

    def _get_locked(self, key: str) -> Optional[Any]:
        """Безопасное получение значения без блокировки (блокировка должна быть снаружи)."""
        if key not in self._data:
            return None

        val, expire = self._data[key]
        if _now() > expire:
            self._delete_locked(key)
            return None

        # LRU: перемещаем в конец списка (как недавно использованный)
        self._order.move_to_end(key)
        return val

    def _set_locked(self, key: str, value: Any, expire: float):
        """Безопасное сохранение значения."""
        # Если ключа нет и место кончилось -> удаляем самый старый (LRU Eviction)
        if key not in self._data and len(self._data) >= self.maxsize:
            # popitem(last=False) удаляет первый (самый старый) элемент
            oldest, _ = self._order.popitem(last=False)
            self._data.pop(oldest, None)

        self._data[key] = (value, expire)
        # Обновляем порядок LRU
        self._order[key] = True
        self._order.move_to_end(key)

    def _delete_locked(self, key: str):
        self._data.pop(key, None)
        self._order.pop(key, None)
