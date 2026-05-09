from collections.abc import Awaitable, Callable
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ICache(Protocol):
    """
    Интерфейс кэша для pymoex.

    Любая реализация (Redis, Memcached, FileSystem) должна поддерживать эти методы.
    """

    async def get(self, key: str) -> Any | None:
        """
        Получить значение по ключу.
        Вернуть None, если ключа нет или он истек.
        """
        ...

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Сохранить значение.
        :param ttl: Время жизни в секундах. Если None, используется дефолтное.
        """
        ...

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Awaitable[Any]],
        ttl: int | None = None,
    ) -> Any:
        """
        Получить значение, если оно есть.
        Если нет — выполнить асинхронную функцию factory(), сохранить результат и вернуть его.
        Желательно реализовать защиту от 'Cache Stampede' (склейку запросов).
        """
        ...

    async def clear(self) -> None:
        """
        Полная очистка кэша.
        """
        ...
