from typing import List, Optional

from pymoex.core.cache import MemoryCache, NullCache
from pymoex.core.interfaces import ICache
from pymoex.core.session import MoexSession
from pymoex.models.bond import Bond
from pymoex.models.enums import InstrumentType
from pymoex.models.search import Search
from pymoex.models.share import Share
from pymoex.services.bonds import BondsService
from pymoex.services.search import SearchService
from pymoex.services.shares import SharesService


class MoexClient:
    """
    Асинхронный клиент для работы с ISS API Московской биржи.
    """

    def __init__(
        self,
        cache: Optional[ICache] = None,
        use_cache: bool = True,
    ):
        """
        Инициализация клиента.

        :param cache: Объект кэша, реализующий интерфейс ICache (например, Redis).
                      Если None, будет создан встроенный MemoryCache.
        :param use_cache: Если False, кэширование будет полностью отключено (используется NullCache).
        """

        self.session = MoexSession()

        # Логика выбора стратегии кэширования
        if not use_cache:
            self._cache = NullCache()
        elif cache is not None:
            self._cache = cache
        else:
            # Дефолтный кэш: храним в памяти, 1000 элементов, TTL 60 сек
            self._cache = MemoryCache(ttl=60, maxsize=1000)

        # Передаем единый инстанс кэша во все сервисы.
        # Сервисы сами формируют уникальные ключи (например 'share:SBER', 'bond:OFZ...').
        self.shares = SharesService(self.session, self._cache)
        self.bonds = BondsService(self.session, self._cache)
        self.search = SearchService(self.session, self._cache)

    async def close(self) -> None:
        """
        Закрыть HTTP-сессию и очистить ресурсы кэша.
        """
        if self._cache:
            await self._cache.clear()

        if self.session:
            await self.session.close()

    async def share(self, ticker: str) -> Share:
        """
        Получить данные по акции.

        :param ticker: тикер (например, 'SBER')
        :return: модель Share
        """
        return await self.shares.get_share(ticker)

    async def bond(self, ticker: str) -> Bond:
        """
        Получить данные по облигации.

        :param ticker: ISIN или торговый код
        :return: модель Bond
        """
        return await self.bonds.get_bond(ticker)

    async def find(
        self, query: str, instrument_type: InstrumentType | str | None = None
    ) -> List[Search]:
        """
        Поиск инструментов по строке.

        :param query: строка поиска (тикер, имя, ISIN)
        :param instrument_type: 'share', 'bond' или None (всё)
        :return: список найденных инструментов
        """
        return await self.search.find(query, instrument_type)

    async def find_bonds(self, query: str) -> List[Search]:
        """
        Поиск облигаций по строке.
        """
        return await self.search.find(query, InstrumentType.BOND)

    async def find_shares(self, query: str) -> List[Search]:
        """
        Поиск акций по строке.
        """
        return await self.search.find(query, InstrumentType.SHARE)

    async def __aenter__(self) -> "MoexClient":
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
