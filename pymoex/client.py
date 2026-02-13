import asyncio
from typing import List

from pymoex.core.cache import TTLCache
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

    def __init__(self, price_ttl: int = 60, search_ttl: int = 300):
        """
        :param price_ttl: время жизни кэша цен (акции и облигации) в секундах
        :param search_ttl: время жизни кэша поиска в секундах
        """

        self.session = MoexSession()

        # Кэши
        self.cache_shares = TTLCache(ttl=price_ttl, maxsize=1000)
        self.cache_bonds = TTLCache(ttl=price_ttl, maxsize=1000)
        self.cache_search = TTLCache(ttl=search_ttl, maxsize=2000)

        # Сервисы
        self.shares = SharesService(self.session, self.cache_shares)
        self.bonds = BondsService(self.session, self.cache_bonds)
        self.search = SearchService(self.session, self.cache_search)

    async def close(self) -> None:
        """
        Закрыть HTTP-сессию и очистить кэши.
        """

        caches = [self.cache_shares, self.cache_bonds, self.cache_search]

        for c in caches:
            try:
                res = c.clear()

                if asyncio.iscoroutine(res):
                    await res
            except Exception:
                pass

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

    async def find_bonds(self, query: str):
        """
        Поиск облигаций по строке.

        :param query: строка поиска (тикер, имя, ISIN)
        :param instrument_type:с'bond'
        :return: список найденных облигаций
        """
        return await self.search.find(query, InstrumentType.BOND)

    async def find_shares(self, query: str):
        """
        Поиск акций по строке.

        :param query: строка поиска (тикер, имя, ISIN)
        :param instrument_type: 'share'
        :return: список найденных акций
        """
        return await self.search.find(query, InstrumentType.SHARE)

    async def __aenter__(self) -> "MoexClient":
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
