import logging
from typing import ClassVar, override

from pydantic import BaseModel

from pymoex.core import endpoints
from pymoex.core.constants import CacheTTL
from pymoex.exceptions import MoexResponseParseError
from pymoex.models.dividend import Dividend
from pymoex.models.share import Share
from pymoex.services.base import InstrumentService
from pymoex.utils.response import get_table, normalize_ticker
from pymoex.utils.table import parse_table

logger = logging.getLogger(__name__)


class SharesService(InstrumentService[Share]):
    instrument_name: ClassVar[str] = "Share"
    cache_prefix: ClassVar[str] = "share"
    ttl: ClassVar[int] = CacheTTL.SHARE_TTL_SECONDS
    priority_boards_attr: ClassVar[str] = "preferred_share_boards"

    @override
    def get_model(self) -> type[Share]:
        return Share

    @override
    def get_endpoint(self, ticker: str) -> str:
        return endpoints.share(ticker)

    async def dividends(self, ticker: str) -> list[Dividend]:
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

        if table_name not in data:
            logger.warning(
                "Table %r is unavailable in MOEX response for %s",
                table_name,
                ticker,
            )
            return []

        table = get_table(data, table_name)
        table_data = table.get("data")

        if not isinstance(table_data, list):
            raise MoexResponseParseError(f"Invalid {table_name!r} table")

        if not table_data:
            logger.info("No %s found for %s", table_name, ticker)
            return []

        rows = parse_table(table)
        return [model.model_validate(row) for row in rows]
