from collections.abc import Awaitable, Callable
from typing import Protocol


class ICache(Protocol):
    """
    Интерфейс кэша для pymoex.
    """

    async def get(self, key: str) -> object | None:
        """
        Получить значение по ключу.
        """
        ...

    async def set(self, key: str, value: object, ttl: int | None = None) -> None:
        """
        Сохранить значение.
        :param ttl: Время жизни в секундах. Если None, используется дефолтное.
        """
        ...

    async def get_or_set[T](
        self,
        key: str,
        factory: Callable[[], Awaitable[T]],
        ttl: int | None = None,
    ) -> T:
        """
        Получить значение, если оно есть.
        """
        ...

    async def clear(self) -> None:
        """
        Полная очистка кэша.
        """
        ...
