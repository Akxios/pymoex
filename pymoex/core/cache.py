import time
import asyncio
from typing import Any, Optional
from collections import OrderedDict

# Используем монотонное время (не зависит от перевода часов)
_now = time.monotonic


class TTLCache:
    """
    Асинхронный in-memory TTL-кэш с поддержкой LRU-эвикшена.

    Особенности:
    - Потокобезопасен (через asyncio.Lock)
    - Поддерживает TTL на элемент
    - Опциональное ограничение размера (LRU: вытесняется самый старый)
    - Поддержка атомарного get_or_set

    :param ttl: время жизни элемента по умолчанию (сек)
    :param maxsize: максимум элементов в кэше (None = без лимита)
    """

    def __init__(self, ttl: int = 30, maxsize: Optional[int] = None):
        self.ttl = int(ttl)
        self.maxsize = None if maxsize is None else int(maxsize)

        # Основное хранилище: key -> (value, expires_at)
        self._data: dict[str, tuple[Any, float]] = {}

        # LRU-порядок: самый старый в начале, самый свежий в конце
        self._order = OrderedDict()

        # Асинхронная блокировка для конкурентного доступа
        self._lock = asyncio.Lock()

    def _now(self) -> float:
        """Текущее монотонное время."""
        return _now()

    async def _evict_if_needed(self) -> None:
        """
        Удаляет элементы, если превышен лимит размера.
        Удаляется самый давно неиспользуемый (LRU).
        """
        if self.maxsize is None:
            return

        while len(self._data) > self.maxsize:
            oldest_key, _ = self._order.popitem(last=False)
            self._data.pop(oldest_key, None)

    async def get(self, key: str) -> Optional[Any]:
        """
        Получить значение по ключу.

        - Возвращает None, если ключ отсутствует или протух
        - Обновляет LRU-позицию при успешном доступе
        """
        async with self._lock:
            item = self._data.get(key)
            if not item:
                return None

            value, expires_at = item

            # Проверка TTL
            if self._now() > expires_at:
                self._data.pop(key, None)
                self._order.pop(key, None)
                return None

            # Помечаем как недавно использованный
            try:
                self._order.move_to_end(key, last=True)
            except KeyError:
                self._order[key] = True

            return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Сохранить значение в кэш.

        :param key: ключ
        :param value: данные
        :param ttl: индивидуальный TTL (сек), иначе используется self.ttl
        """
        expires_at = self._now() + (int(ttl) if ttl is not None else self.ttl)

        async with self._lock:
            self._data[key] = (value, expires_at)

            # Обновляем LRU-очередь
            self._order.pop(key, None)
            self._order[key] = True

            await self._evict_if_needed()

    async def delete(self, key: str) -> None:
        """Удалить элемент из кэша."""
        async with self._lock:
            self._data.pop(key, None)
            self._order.pop(key, None)

    async def clear(self) -> None:
        """Полная очистка кэша."""
        async with self._lock:
            self._data.clear()
            self._order.clear()

    async def keys(self) -> list[str]:
        """Список всех ключей (без проверки TTL)."""
        async with self._lock:
            return list(self._data.keys())

    async def get_or_set(self, key: str, factory, ttl: Optional[int] = None):
        """
        Атомарная операция:
        - если значение есть и живое → вернуть
        - иначе вычислить через factory, сохранить и вернуть

        factory может быть:
        - обычной функцией
        - корутиной
        """

        # Быстрый путь без блокировки
        val = await self.get(key)
        if val is not None:
            return val

        async with self._lock:
            # Повторная проверка внутри lock (double-checked locking)
            item = self._data.get(key)
            if item:
                value, expires_at = item
                if self._now() <= expires_at:
                    try:
                        self._order.move_to_end(key, last=True)
                    except KeyError:
                        self._order[key] = True
                    return value

                # Если протух — удаляем
                self._data.pop(key, None)
                self._order.pop(key, None)

            # Вычисление значения
            result = factory()
            if asyncio.iscoroutine(result):
                result = await result  # поддержка async factory

            expires_at = self._now() + (int(ttl) if ttl is not None else self.ttl)
            self._data[key] = (result, expires_at)
            self._order[key] = True

            await self._evict_if_needed()
            return result
