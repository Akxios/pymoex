import logging
from typing import ClassVar, override

from pydantic import BaseModel

from pymoex.core import endpoints
from pymoex.core.constants import CacheTTL
from pymoex.models.bond import Bond
from pymoex.models.bondization import Amortization, Coupon
from pymoex.services.base import InstrumentService
from pymoex.utils.response import (
    get_table,
    normalize_ticker,
)
from pymoex.utils.table import parse_table

logger = logging.getLogger(__name__)


class BondsService(InstrumentService[Bond]):
    """
    Сервис для получения данных по облигациям.
    """

    instrument_name: ClassVar[str] = "Bond"
    cache_prefix: ClassVar[str] = "bond"
    ttl: ClassVar[int] = CacheTTL.BOND_EVENTS_TTL_SECONDS
    priority_boards_attr: ClassVar[str] = "preferred_share_boards"

    @override
    def get_model(self) -> type[Bond]:
        return Bond

    @override
    def get_endpoint(self, ticker: str) -> str:
        return endpoints.bond(ticker)

    async def coupons(self, ticker: str) -> list[Coupon]:
        """
        Получить историю и график будущих купонов по облигации.
        """
        ticker = normalize_ticker(ticker)
        return await self._get_bond_event_rows(
            ticker=ticker,
            table_name="coupons",
            model=Coupon,
        )

    async def amortizations(self, ticker: str) -> list[Amortization]:
        """
        Получить график амортизации (выплаты номинала) по облигации.
        """
        ticker = normalize_ticker(ticker)
        return await self._get_bond_event_rows(
            ticker=ticker,
            table_name="amortizations",
            model=Amortization,
        )

    async def _get_bond_events(self, ticker: str) -> dict[str, object]:
        cache_key = f"bond_events:{ticker}"

        async def _fetch() -> dict[str, object]:
            return await self.session.get(endpoints.bond_events(ticker))

        return await self.cache.get_or_set(
            cache_key,
            _fetch,
            ttl=CacheTTL.BOND_EVENTS_TTL_SECONDS,
        )

    async def _get_bond_event_rows[TModel: BaseModel](
        self,
        ticker: str,
        table_name: str,
        model: type[TModel],
    ) -> list[TModel]:
        data = await self._get_bond_events(ticker)
        table = get_table(data, table_name)

        if not table.get("data"):
            logger.info("No %s found for %s", table_name, ticker)
            return []

        rows = parse_table(table)
        return [model.model_validate(row) for row in rows]
