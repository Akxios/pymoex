from types import TracebackType
from typing import Self

from pymoex.core.cache import MemoryCache, NullCache
from pymoex.core.interfaces import ICache
from pymoex.core.session import MoexSession
from pymoex.models.bond import Bond
from pymoex.models.bondization import Amortization, Coupon
from pymoex.models.currency import Currency
from pymoex.models.dividend import Dividend
from pymoex.models.enums import InstrumentType
from pymoex.models.search import Search
from pymoex.models.share import Share
from pymoex.services.bonds import BondsService
from pymoex.services.currencies import CurrenciesService
from pymoex.services.search import SearchService
from pymoex.services.shares import SharesService


class MoexClient:
    """
    Асинхронный клиент для работы с ISS API Московской биржи.
    """

    def __init__(
        self,
        session: MoexSession | None = None,
        cache: ICache | None = None,
        use_cache: bool = True,
    ) -> None:
        self.session: MoexSession = session or MoexSession()

        if not use_cache:
            self._cache: ICache = NullCache()
        elif cache is not None:
            self._cache = cache
        else:
            self._cache = MemoryCache(ttl=60, maxsize=1000)

        self.shares: SharesService = SharesService(self.session, self._cache)
        self.bonds: BondsService = BondsService(self.session, self._cache)
        self.currencies: CurrenciesService = CurrenciesService(
            self.session, self._cache
        )
        self.search: SearchService = SearchService(self.session, self._cache)

    async def close(self) -> None:
        """Закрыть HTTP-сессию и очистить ресурсы кэша."""

        await self._cache.clear()
        await self.session.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def share(self, ticker: str) -> Share:
        """Получить данные по акции."""
        return await self.shares.get(ticker)

    async def bond(self, ticker: str) -> Bond:
        """Получить данные по облигации."""
        return await self.bonds.get(ticker)

    async def fund(self, ticker: str) -> Share:
        """
        Получить данные по биржевому фонду.
        """

        return await self.shares.get(ticker)

    async def currency(self, ticker: str) -> Currency:
        """Получить данные по валютной паре."""
        return await self.currencies.get(ticker)

    async def find(
        self, query: str, instrument_type: InstrumentType | str | None = None
    ) -> list[Search]:
        """Поиск инструментов по строке."""
        return await self.search.find(query, instrument_type)

    async def find_bonds(self, query: str) -> list[Search]:
        """Поиск облигаций по строке."""
        return await self.search.find(query, InstrumentType.BOND)

    async def find_shares(self, query: str) -> list[Search]:
        """Поиск акций по строке."""
        return await self.search.find(query, InstrumentType.SHARE)

    async def find_funds(self, query: str) -> list[Search]:
        return await self.search.find(query, InstrumentType.FUND)

    async def find_currencies(self, query: str) -> list[Search]:
        return await self.search.find(query, InstrumentType.CURRENCY)

    async def dividends(self, ticker: str) -> list[Dividend]:
        """Получить данные по дивидендам."""
        return await self.shares.dividends(ticker)

    async def coupons(self, ticker: str) -> list[Coupon]:
        """Асинхронно получить историю и график купонов по облигации."""
        return await self.bonds.coupons(ticker)

    async def amortizations(self, ticker: str) -> list[Amortization]:
        """Асинхронно получить график амортизации по облигации."""
        return await self.bonds.amortizations(ticker)
