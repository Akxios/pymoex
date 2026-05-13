import logging

from pydantic import BaseModel

from pymoex.core import endpoints
from pymoex.core.constants import CacheTTL
from pymoex.core.interfaces import ICache
from pymoex.core.session import MoexSession
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.dividend import Dividend
from pymoex.models.share import Share
from pymoex.utils.boards import select_best_board
from pymoex.utils.response import (
    find_row_by_board,
    get_table,
    normalize_ticker,
)
from pymoex.utils.table import parse_table

logger = logging.getLogger(__name__)


class SharesService:
    """
    Сервис для получения данных по акциям.
    """

    def __init__(self, session: MoexSession, cache: ICache) -> None:
        self.session: MoexSession = session
        self.cache: ICache = cache

    async def get_share(self, ticker: str) -> Share:
        ticker = normalize_ticker(ticker)
        cache_key = f"share:{ticker}"

        async def _fetch() -> Share:
            data = await self.session.get(endpoints.share(ticker))
            return self._build_share(ticker, data)

        return await self.cache.get_or_set(
            cache_key, _fetch, ttl=CacheTTL.SHARE_TTL_SECONDS
        )

    def _build_share(self, ticker: str, data: dict[str, object]) -> Share:
        securities = get_table(data, "securities")

        if not securities.get("data"):
            logger.warning("Share %s not found in MOEX response", ticker)
            raise InstrumentNotFoundError(f"Share {ticker} not found")

        sec_rows = parse_table(securities)
        md_rows = parse_table(get_table(data, "marketdata"))
        yield_rows = parse_table(get_table(data, "marketdata_yields"))

        if not sec_rows:
            logger.warning("Share %s has empty securities table", ticker)
            raise InstrumentNotFoundError(f"Share {ticker} not found")

        target_board = select_best_board(
            sec_rows=sec_rows,
            md_rows=md_rows,
            priority_boards=self.session.settings.preferred_share_boards,
        )

        logger.debug("Selected board %r for share %s", target_board, ticker)

        security = find_row_by_board(sec_rows, target_board) or sec_rows[0]
        market_data = find_row_by_board(md_rows, target_board) or {}
        yield_data = find_row_by_board(yield_rows, target_board) or {}

        combined_data = {**security, **yield_data, **market_data}

        return Share.model_validate(combined_data)

    async def get_dividends(self, ticker: str) -> list[Dividend]:
        """
        Получить историю дивидендов и будущие утвержденные выплаты по акции.
        """
        ticker = normalize_ticker(ticker)
        return await self._get_share_event_rows(
            ticker=ticker,
            table_name="dividends",
            model=Dividend,
        )

    async def _get_share_events(self, ticker: str) -> dict[str, object]:
        cache_key = f"share_events:{ticker}"

        async def _fetch() -> dict[str, object]:
            return await self.session.get(endpoints.dividends(ticker))

        return await self.cache.get_or_set(
            cache_key,
            _fetch,
            ttl=CacheTTL.SHARE_EVENT_TTL_SECONDS,
        )

    async def _get_share_event_rows[TModel: BaseModel](
        self,
        ticker: str,
        table_name: str,
        model: type[TModel],
    ) -> list[TModel]:
        data = await self._get_share_events(ticker)
        table = get_table(data, table_name)

        if not table.get("data"):
            logger.info("No %s found for %s", table_name, ticker)
            return []

        rows = parse_table(table)
        return [model.model_validate(row) for row in rows]
