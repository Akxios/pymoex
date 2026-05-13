import logging

from pydantic import BaseModel

from pymoex.core import endpoints
from pymoex.core.constants import CacheTTL
from pymoex.core.interfaces import ICache
from pymoex.core.session import MoexSession
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.bond import Bond
from pymoex.models.bondization import Amortization, Coupon
from pymoex.utils.boards import select_best_board
from pymoex.utils.response import (
    find_row_by_board,
    get_table,
    normalize_ticker,
)
from pymoex.utils.table import parse_table

logger = logging.getLogger(__name__)


class BondsService:
    """
    Сервис для получения данных по облигациям.
    """

    def __init__(self, session: MoexSession, cache: ICache) -> None:
        self.session: MoexSession = session
        self.cache: ICache = cache

    async def get_bond(self, ticker: str) -> Bond:
        ticker = normalize_ticker(ticker)
        cache_key = f"bond:{ticker}"

        async def _fetch() -> Bond:
            data = await self.session.get(endpoints.bond(ticker))
            return self._build_bond(ticker, data)

        return await self.cache.get_or_set(
            cache_key, _fetch, ttl=CacheTTL.BOND_TTL_SECONDS
        )

    async def get_coupons(self, ticker: str) -> list[Coupon]:
        """
        Получить историю и график будущих купонов по облигации.
        """
        ticker = normalize_ticker(ticker)
        return await self._get_bond_event_rows(
            ticker=ticker,
            table_name="coupons",
            model=Coupon,
        )

    async def get_amortizations(self, ticker: str) -> list[Amortization]:
        """
        Получить график амортизации (выплаты номинала) по облигации.
        """
        ticker = normalize_ticker(ticker)
        return await self._get_bond_event_rows(
            ticker=ticker,
            table_name="amortizations",
            model=Amortization,
        )

    def _build_bond(self, ticker: str, data: dict[str, object]) -> Bond:
        securities = get_table(data, "securities")

        if not securities.get("data"):
            logger.warning("Bond %s not found in MOEX response", ticker)
            raise InstrumentNotFoundError(f"Bond {ticker} not found")

        sec_rows = parse_table(securities)
        md_rows = parse_table(get_table(data, "marketdata"))
        yield_rows = parse_table(get_table(data, "marketdata_yields"))

        if not sec_rows:
            logger.warning("Bond %s has empty securities table", ticker)
            raise InstrumentNotFoundError(f"Bond {ticker} not found")

        target_board = select_best_board(
            sec_rows=sec_rows,
            md_rows=md_rows,
            priority_boards=self.session.settings.preferred_bond_boards,
        )

        logger.debug("Selected board %r for bond %s", target_board, ticker)

        security = find_row_by_board(sec_rows, target_board) or sec_rows[0]
        market_data = find_row_by_board(md_rows, target_board) or {}
        yield_data = find_row_by_board(yield_rows, target_board) or {}

        combined_data = {**security, **yield_data, **market_data}

        return Bond.model_validate(combined_data)

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
