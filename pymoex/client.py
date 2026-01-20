import asyncio

from pymoex.core.session import MoexSession
from pymoex.core.cache import TTLCache
from pymoex.services.shares import SharesService
from pymoex.services.search import SearchService
from pymoex.services.bonds import BondsService
from pymoex.models.share import Share
from pymoex.models.bond import Bond


class MoexClient:
    """
    Асинхронный клиент для работы с ISS API Московской биржи.

    Предоставляет удобный интерфейс для:
    - получения котировок акций,
    - получения информации по облигациям,
    - поиска инструментов.

    Использует in-memory TTL-кэш для снижения количества запросов к API.
    """

    def __init__(self, price_ttl: int = 60, search_ttl: int = 300):
        """
        :param price_ttl: время жизни кэша цен (в секундах)
        :param search_ttl: время жизни кэша поиска (в секундах)
        """
        self.session = MoexSession()

        # Кэши
        self.cache = TTLCache(ttl=price_ttl, maxsize=1000)
        self.search_cache = TTLCache(ttl=search_ttl, maxsize=2000)

        # Сервисы
        self.shares = SharesService(self.session, self.cache)
        self.bonds = BondsService(self.session, self.cache)
        self.search = SearchService(self.session, self.search_cache)

    async def __aenter__(self) -> "MoexClient":
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self) -> None:
        """
        Закрыть HTTP-сессию и аккуратно очистить локальные кэши.
        Вызывать только когда нет активных запросов к клиенту.
        """
        # 1) Остановить background cleanup (если реализовано)
        for c in (getattr(self, "cache", None), getattr(self, "search_cache", None)):
            if c is None:
                continue
            stop = getattr(c, "stop_cleanup", None)
            if callable(stop):
                try:
                    res = stop()
                    # stop_cleanup может быть sync или async
                    if asyncio.iscoroutine(res):
                        await res
                except Exception:
                    # не критично — просто логировать по желанию
                    pass

        # 2) Очистить локальные in-memory кэши (если есть)
        for c in (getattr(self, "cache", None), getattr(self, "search_cache", None)):
            if c is None:
                continue
            clear = getattr(c, "clear", None)
            if callable(clear):
                try:
                    maybe = clear()
                    if asyncio.iscoroutine(maybe):
                        await maybe
                except Exception:
                    # не критично — можно логировать
                    pass

        # 3) Закрыть HTTP-сессию
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

    async def find(self, query: str, instrument_type: str | None = None):
        """
        Поиск инструментов по строке.

        :param query: строка поиска (тикер, имя, ISIN)
        :param instrument_type: 'share', 'bond' или None (всё)
        :return: список найденных инструментов
        """
        return await self.search.find(query, instrument_type)
