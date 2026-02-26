import logging
from typing import List

from pymoex.core import endpoints
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.dividend import Dividend
from pymoex.models.share import Share
from pymoex.utils.boards import select_best_board
from pymoex.utils.table import parse_table

logger = logging.getLogger(__name__)


class SharesService:
    """
    Сервис для получения данных по акциям.
    """

    def __init__(self, session, cache):
        self.session = session
        self.cache = cache

    async def get_share(self, ticker: str) -> Share:
        ticker = ticker.upper()
        cache_key = f"share:{ticker}"

        async def _fetch():
            return await self._load_share(ticker)

        return await self.cache.get_or_set(cache_key, _fetch, ttl=60)

    async def _load_share(self, ticker: str) -> Share:
        data = await self.session.get(endpoints.share(ticker))

        if not data.get("securities", {}).get("data"):
            logger.warning(f"Share {ticker} not found in MOEX response")
            raise InstrumentNotFoundError(f"Share {ticker} not found")

        sec_rows = parse_table(data["securities"])
        md_rows = parse_table(data.get("marketdata", {}))

        # Список приоритетных режимов для акций и фондов
        priority_boards = self.session.settings.preferred_share_boards

        target_board = select_best_board(
            sec_rows=sec_rows, md_rows=md_rows, priority_boards=priority_boards
        )

        logger.debug(f"Selected board '{target_board}' for share {ticker}")

        # Берем данные именно для выбранного борда
        security = next(
            (r for r in sec_rows if r["BOARDID"] == target_board), sec_rows[0]
        )
        market_data = next((r for r in md_rows if r["BOARDID"] == target_board), {})

        combined_data = {**security, **market_data}

        return Share.model_validate(combined_data)

    async def get_dividends(self, ticker: str) -> List[Dividend]:
        """
        Получить историю дивидендов и будущие утвержденные выплаты по акции.
        """
        ticker = ticker.upper()
        cache_key = f"dividends:{ticker}"

        async def _fetch():
            data = await self.session.get(endpoints.dividends(ticker))

            # Если блок dividends пустой или отсутствует
            if not data.get("dividends", {}).get("data"):
                logger.info(f"No dividends found for {ticker}")
                return []

            div_rows = parse_table(data["dividends"])

            # Преобразуем каждую строку ответа биржи в Pydantic-модель
            return [Dividend.model_validate(row) for row in div_rows]

        # Дивиденды можно кэшировать надолго (например, на час = 3600 сек)
        return await self.cache.get_or_set(cache_key, _fetch, ttl=3600)
