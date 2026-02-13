from typing import Any, Awaitable, Callable, Optional, Protocol, runtime_checkable


@runtime_checkable
class ICache(Protocol):
    """
    Интерфейс кэша для pymoex.

    Любая реализация (Redis, Memcached, FileSystem) должна поддерживать эти методы.
    """

    async def get(self, key: str) -> Optional[Any]:
        """
        Получить значение по ключу.
        Вернуть None, если ключа нет или он истек.
        """
        ...

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Сохранить значение.
        :param ttl: Время жизни в секундах. Если None, используется дефолтное.
        """
        ...

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Awaitable[Any]],
        ttl: Optional[int] = None,
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
