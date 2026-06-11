import logging

from pymoex.core import endpoints
from pymoex.core.constants import CacheTTL
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.currency import Currency
from pymoex.services.base import BaseService
from pymoex.utils.boards import select_best_board
from pymoex.utils.response import find_row_by_board, get_table, normalize_ticker
from pymoex.utils.table import parse_table

logger = logging.getLogger(__name__)

CURRENCY_MARKETS_TO_TRY: tuple[str, ...] = ("selt", "otcindices", "index")


class CurrenciesService(BaseService):
    async def get(self, secid: str) -> Currency:
        """
        Получить валютный инструмент по реальному SECID MOEX.
        """
        secid = normalize_ticker(secid)
        cache_key = f"currency:{secid}"

        async def _fetch() -> Currency:
            data = await self._load_currency_data(secid)
            return self._build_currency(secid, data)

        return await self.cache.get_or_set(
            cache_key,
            _fetch,
            ttl=CacheTTL.CURRENCY_TTL_SECONDS,
        )

    async def _load_currency_data(self, secid: str) -> dict[str, object]:
        for market in CURRENCY_MARKETS_TO_TRY:
            try:
                data = await self.session.get(endpoints.currency(secid, market=market))
                securities = get_table(data, "securities")

                if securities.get("data"):
                    return data
            except Exception as e:
                logger.debug("Market '%s' failed for %s: %s", market, secid, e)
                continue

        logger.warning("Currency %s not found in MOEX response", secid)
        raise InstrumentNotFoundError(f"Currency {secid} not found")

    def _build_currency(self, secid: str, data: dict[str, object]) -> Currency:
        securities = get_table(data, "securities")

        if not securities.get("data"):
            logger.warning("Currency %s not found in MOEX response", secid)
            raise InstrumentNotFoundError(f"Currency {secid} not found")

        sec_rows = parse_table(securities)
        md_rows = parse_table(get_table(data, "marketdata"))

        if not sec_rows:
            logger.warning("Currency %s has empty securities table", secid)
            raise InstrumentNotFoundError(f"Currency {secid} not found")

        target_board = select_best_board(
            sec_rows=sec_rows,
            md_rows=md_rows,
            priority_boards=self.session.settings.preferred_currency_boards,
        )

        logger.debug("Selected board %r for currency %s", target_board, secid)

        security = find_row_by_board(sec_rows, target_board) or sec_rows[0]
        market_data = find_row_by_board(md_rows, target_board) or {}

        combined_data = {**security, **market_data}
        return Currency.model_validate(combined_data)
